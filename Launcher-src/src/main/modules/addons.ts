import path from 'node:path';

import git, { type ProgressCallback } from 'isomorphic-git';
import http from 'isomorphic-git/http/node';
import fs from 'fs-extra';
import fetch from 'node-fetch';
import Logger from 'electron-log/main';

import { EsteriaConfig } from '~common/config';
import { isNotUndef } from '~common/utils';
import { type AddonData, type TocData } from '~common/schemas';

import Preferences from './preferences';
import Observable from './observable';

export type AddonsStatus = {
	state: 'verifying' | 'done';
	addons: { [name: string]: AddonData };
	available: AddonData[];
};

type AddonsList = {
	name: string;
	owner: string;
	branch?: string;
	ref?: string;
	git: string;
	toc?: TocData;
	description?: string;
	lastUpdated?: string;
	stars?: number;
	dependencies?: string[];
}[];

const readTocData = (content: string) =>
	(content.charCodeAt(0) === 0xfeff ? content.slice(1) : content)
		.split('\n')
		.filter(l => l.startsWith('## '))
		.map(l => l.slice(3))
		.map(l => {
			const idx = l.indexOf(':');
			if (idx === -1) return null;
			return [l.slice(0, idx).trim(), l.slice(idx + 1).trim()] as const;
		})
		.filter((e): e is readonly [string, string] => !!e)
		.reduce((acc, [key, value]) => {
			acc[key] = value;
			return acc;
		}, {} as TocData);

const isUnsafeFolder = (name?: string) =>
	!name || name === '.' || name === '..' || /[/\\]/.test(name);

const ALLOWED_GIT_HOSTS = [
	'github.com',
	'gitlab.com',
	'gitea.com',
	'codeberg.org'
];

const isAllowedGitUrl = (url: string) => {
	try {
		const parsed = new URL(url);
		if (parsed.protocol !== 'https:') return false;
		const host = parsed.hostname.toLowerCase();
		return ALLOWED_GIT_HOSTS.some(h => host === h || host.endsWith('.' + h));
	} catch {
		return false;
	}
};

const cloneAddon = async (
	dir: string,
	url: string,
	ref: string | undefined,
	onProgress: ProgressCallback
) => {
	const tmpDir = `${dir}.tmp`;
	await fs.remove(tmpDir);
	await git.clone({
		dir: tmpDir,
		fs,
		http,
		url,
		ref,
		singleBranch: !ref || ref === 'master' || ref === 'main',
		onProgress
	});
	await fs.remove(dir);
	await fs.move(tmpDir, dir);
};

const pullAddon = async (
	dir: string,
	remote: string,
	branch: string,
	ref: string | undefined,
	onProgress: ProgressCallback
) => {
	if (ref) {
		await git.fetch({
			fs,
			http,
			dir,
			tags: true,
			singleBranch: false,
			onProgress
		});
		await git.checkout({ fs, dir, force: true, ref, onProgress });
		return;
	}

	await git.checkout({
		fs,
		dir,
		force: true,
		ref: `${remote}/${branch}`,
		onProgress
	});
	await git.pull({
		fs,
		http,
		dir,
		ref: branch,
		singleBranch: true,
		author: { name: 'Esteria Launcher' },
		onProgress
	});
};

const fetchAddons = async () => {
	try {
		const response = await fetch(
			`${
				EsteriaConfig.serverUrl
			}/api/addons.json`
		);
		return (await response.json()) as AddonsList;
	} catch (e) {
		Logger.error('Failed to reach update server', e);
		return [];
	}
};

class AddonsClass extends Observable<AddonsStatus> {
	protected _value: AddonsStatus = {
		state: 'done',
		addons: {},
		available: []
	};

	get status() {
		return this._value;
	}
	private set status(v: AddonsStatus) {
		this._value = v;
		this._notifyObservers(v);
	}

	#onProgress =
		(folder: string, data: AddonData): ProgressCallback =>
		progress => {
			const getPhase = (step: string) => {
				switch (step) {
					case 'Counting objects':
						return 1;
					case 'Compressing objects':
						return 2;
					case 'Receiving objects':
						return 3;
					case 'Resolving deltas':
						return 4;
					case 'Analyzing workdir':
						return 5;
					case 'Updating workdir':
						return 6;
					default:
						return 0;
				}
			};
			this.#setAddon(folder, {
				...data,
				progress: `${Math.round(
					(progress.loaded / (progress.total ?? progress.loaded)) * 100
				)}% (${getPhase(progress.phase)}/6)`
			});
		};

	async checkGitUrl(url: string) {
		const clean = url.trim().replace(/\/+$/, '');
		const gitUrl = clean.endsWith('.git') ? clean : `${clean}.git`;
		if (!isAllowedGitUrl(gitUrl)) return undefined;
		try {
			await git.getRemoteInfo({
				http,
				url: gitUrl
			});

			let preview: string | undefined;
			try {
				if (isAllowedGitUrl(url)) {
					const response = await fetch(url).then(r => r.text());
					preview = response.match(
						/property="og:image" content="([^"]*)"/
					)?.[1];
				}
			} catch {
			}

			const folder = gitUrl.slice(0, -4).split('/').at(-1);
			if (isUnsafeFolder(folder)) return undefined;
			return {
				status: 'available',
				folder,
				git: gitUrl,
				preview
			} as AddonData;
		} catch {
			return undefined;
		}
	}

	async verify() {
		if (this.status.state !== 'done') return;

		this.status = {
			...this.status,
			state: 'verifying'
		};

		const remoteAddons = await fetchAddons();
		const available: AddonData[] = remoteAddons.map(a => ({
			status: 'available',
			git: a.git,
			toc: a.toc,
			description: a.description,
			folder: a.name,
			branch: a.branch,
			ref: a.ref
		}));

		const clientPath = Preferences.data.clientDir;
		if (!clientPath) {
			this.status = { state: 'done', addons: {}, available };
			return;
		}

		const addonsPath = path.join(clientPath, 'Interface', 'Addons');
		const dirs = (await fs.pathExists(addonsPath))
			? await fs.readdir(addonsPath)
			: [];
		const addons: AddonsStatus['addons'] = Object.fromEntries(
			dirs
				.filter(d => !d.startsWith('Blizzard_'))
				.map(name => [name, { status: 'fetching' as const, folder: name }])
		);

		this.status = { state: 'verifying', addons, available };

		const verifyOne = async (folder: string) => {
			const dir = path.join(addonsPath, folder);

			if (!fs.existsSync(path.join(dir, `${folder}.toc`))) {
				this.#setAddon(folder, {
					status: 'invalid',
					error: 'Missing .toc file',
					folder
				});
				return;
			}

			const toc = await readTocData(
				await fs.readFile(path.join(dir, `${folder}.toc`), 'utf-8')
			);

			const remote = await git
				.listRemotes({ fs, dir })
				.then(r => r[0])
				.catch(() => null);

			const avail = remoteAddons.find(a => a.name === folder);
			if (!remote) {
				Logger.log(`Addon "${folder}" is not a git repository`);
				this.#setAddon(
					folder,
					avail
						? {
								status: 'outOfDate',
								git: avail.git,
								toc,
								description: avail.description,
								folder
						  }
						: { status: 'unknown', toc, folder }
				);
				return;
			}

			try {
				await git.fetch({ fs, dir, http, tags: true });

				const branch = await git.currentBranch({ fs, dir });

				const localCommit = await git
					.log({ fs, dir, ref: 'HEAD', depth: 1 })
					.then(r => r[0].oid)
					.catch(() => null);

				const remoteCommit = avail?.ref
					? await git.resolveRef({ fs, dir, ref: avail.ref }).catch(() => null)
					: await git
							.log({ fs, dir, ref: `${remote.remote}/${branch}`, depth: 1 })
							.then(r => r[0].oid)
							.catch(() => null);

				const status = await git.statusMatrix({ fs, dir });
				const hasChanges = status.some(
					([_, HEAD, index, workdir]) => HEAD !== index || index !== workdir
				);

				const isUpToDate =
					!hasChanges && remoteCommit && localCommit === remoteCommit;
				this.#setAddon(folder, {
					git: remote.url,
					status: isUpToDate ? 'upToDate' : 'outOfDate',
					toc,
					description: avail?.description,
					ref: avail?.ref,
					folder
				});

				Logger.log(
					isUpToDate
						? `Addon "${folder}" is up to date${
								avail?.ref ? ` (pinned ${avail.ref})` : ''
						  }`
						: `Addon "${folder}" has an update available`
				);
			} catch (e) {
				this.#setAddon(folder, {
					git: remote.url,
					status: 'invalid',
					error: 'Failed to verify',
					toc,
					folder
				});
				Logger.error(`Addon "${folder}" failed to verify`, e);
			}
		};

		const folders = Object.keys(addons);
		const VERIFY_CONCURRENCY = 6;
		let idx = 0;
		await Promise.all(
			Array.from(
				{ length: Math.min(VERIFY_CONCURRENCY, folders.length) },
				async () => {
					while (true) {
						const i = idx++;
						if (i >= folders.length) return;
						await verifyOne(folders[i]);
					}
				}
			)
		);

		this.status = { ...this.status, state: 'done' };
	}

	async update(
		toUpdate = Object.values(this.status.addons)
			.filter(e => e.status === 'outOfDate')
			.map(e => e.folder)
			.filter(isNotUndef)
	) {
		const clientPath = Preferences.data.clientDir;
		if (!clientPath) return;
		if (this.status.state !== 'done') return;

		const addonsPath = path.join(clientPath, 'Interface', 'Addons');

		for (const folder of toUpdate) {
			if (this.status.addons[folder]?.status === 'downloading') continue;
			const dir = path.join(addonsPath, folder);

			const avail = this.status.available.find(a => a.folder === folder);
			const data: AddonData = {
				...avail,
				...this.status.addons[folder],
				status: 'downloading'
			};
			this.#setAddon(folder, data);

			const remote = await git
				.listRemotes({ fs, dir })
				.then(r => r?.[0])
				.catch(() => null);

			try {
				if (!remote) {
					if (!data.git) throw new Error('Addon repository is unavailable.');
					await cloneAddon(
						dir,
						data.git,
						data.ref ?? data.branch,
						this.#onProgress(folder, data)
					);
				} else {
					const branch =
						(await git.currentBranch({ fs, dir })) ?? avail?.branch ?? 'master';
					await pullAddon(
						dir,
						remote.remote,
						branch,
						avail?.ref,
						this.#onProgress(folder, data)
					);
				}
				const toc = readTocData(
					await fs.readFile(path.join(dir, `${folder}.toc`), 'utf-8')
				);

				this.#setAddon(folder, { ...data, toc, status: 'upToDate' });
				Logger.log(`Updated addon "${folder}"`);
			} catch (e) {
				this.#setAddon(folder, {
					...data,
					status: 'invalid',
					error: 'Failed to update'
				});
				Logger.error(`Addon "${folder}" failed to update`, e);
			}
		}
	}

	async remove(toRemove: string[]) {
		const clientPath = Preferences.data.clientDir;
		if (!clientPath) return;
		if (this.status.state !== 'done') return;

		for (const folder of toRemove) {
			const dir = path.join(clientPath, 'Interface', 'Addons', folder);
			if (fs.existsSync(dir)) await fs.remove(dir);
			this.#setAddon(folder);
			Logger.log(`Removed addon "${folder}"`);
		}
	}

	async install(data: AddonData) {
		const clientPath = Preferences.data.clientDir;
		if (!clientPath) return;
		if (isUnsafeFolder(data.folder)) {
			Logger.error(`Refusing addon with unsafe folder name: "${data.folder}"`);
			this.#setAddon(data.folder, {
				...data,
				status: 'invalid',
				error: 'Invalid addon name'
			});
			return;
		}

		if (!data.git || !isAllowedGitUrl(data.git)) {
			Logger.error(`Refusing addon from disallowed git host: "${data.git}"`);
			this.#setAddon(data.folder, {
				...data,
				status: 'invalid',
				error: 'Addon URL is not from an allowed git host'
			});
			return;
		}

		const addonsPath = path.join(clientPath, 'Interface', 'Addons');
		const dir = path.join(addonsPath, data.folder);
		try {
			if (!data.git) throw new Error('Addon repository is unavailable.');
			await cloneAddon(
				dir,
				data.git,
				data.ref ?? data.branch,
				this.#onProgress(data.folder, data)
			);
			const toc = await readTocData(
				await fs.readFile(path.join(dir, `${data.folder}.toc`), 'utf-8')
			);
			this.#setAddon(data.folder, { ...data, toc, status: 'upToDate' });
			Logger.log(`Installed addon "${data.folder}"`);
		} catch (e) {
			this.#setAddon(data.folder, {
				...data,
				status: 'invalid',
				error: 'Failed to install'
			});
			Logger.error(`Addon "${data.folder}" failed to install`, e);
		}
	}

	#setAddon(folder: string, data?: AddonData) {
		const { [folder]: _, ...addons } = this.status.addons;
		this.status = {
			...this.status,
			addons: data ? { ...addons, [folder]: data } : addons
		};
	}
}

const Addons = new AddonsClass();
export default Addons;
