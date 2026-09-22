import path from 'node:path';
import crypto from 'node:crypto';
import { exec } from 'node:child_process';
import os from 'node:os';

import fetch from 'node-fetch';
import fs from 'fs-extra';
import {
	SFileOpenArchive,
	type HANDLE,
	SFileHasFile,
	SFileCloseArchive,
	SFileOpenFileEx,
	SFileReadFile,
	SFileGetFileSize,
	SFileCloseFile,
	SFileCreateFile,
	SFileWriteFile,
	SFileFinishFile,
	SFileFlushArchive,
	SFileRemoveFile,
	SFileCompactArchive
} from 'stormlib-node';
import {
	MPQ_COMPRESSION,
	MPQ_FILE,
	STREAM_FLAG
} from 'stormlib-node/dist/enums';
import Logger from 'electron-log/main';

import {
	asyncMap,
	formatFileSize,
	isNotUndef,
	nestedGet,
	nestedSet
} from '~common/utils';
import { EsteriaConfig } from '~common/config';
import { mainWindow } from '~main/index';

import Preferences from './preferences';
import Observable from './observable';

const getAvailableDiskSpace = async (probePath?: string): Promise<number> => {
	const target =
		probePath ||
		Preferences.data?.clientDir ||
		os.homedir() ||
		(os.platform() === 'win32' ? 'C:\\' : '/');
	try {
		// @ts-expect-error statfs exists at runtime (Node 18) but not @types/node 16
		const s = await fs.promises.statfs(target);
		return Number(s.bsize) * Number(s.bavail);
	} catch (e) {
		Logger.warn(
			`fs.statfs("${target}") failed; treating disk-space check as ` +
				`unavailable. Error: ${e instanceof Error ? e.message : String(e)}`
		);
		return Number.POSITIVE_INFINITY;
	}
};

const isReadOnly = async (filePath: string) => {
	try {
		const { mode } = await fs.stat(filePath);
		return !(mode & fs.constants.S_IWUSR);
	} catch {
		return false;
	}
};

const friendlyError = (e: unknown): string => {
	const msg = e instanceof Error ? e.message : String(e);
	if (/EPERM|EACCES|EROFS|read-only/i.test(msg))
		return (
			'Cannot write to the game folder. Move your Esteria install out of ' +
			'Program Files (or any protected folder), or run the launcher as ' +
			'administrator, then try again.'
		);
	if (/ENOSPC/i.test(msg)) return 'Not enough disk space to finish the update.';
	return msg;
};

type FolderTags = 'allowExtra';
type FileManifest = { name: string } & (
	| { type: 'del' }
	| { type: 'dir'; files: FileManifest[]; tags?: FolderTags[] }
	| { type: 'mpq'; files: FileManifest[]; hash: string; size: number }
	| {
			type: 'file';
			hash: string;
			version?: number;
			size: number;
		}
);

type CacheEntry = [hash: string, mtime: number];
type CacheTree = { [key: string]: CacheTree & CacheEntry };

const getManifestSize = (m?: FileManifest): number =>
	(m?.type === 'del'
		? 0
		: m?.type === 'file'
		? m?.size
		: m?.files?.reduce((acc, v) => acc + getManifestSize(v), 0)) ?? 0;

const getManifestFiles = (m?: FileManifest, p = ''): string[] =>
	(m?.type === 'del'
		? [`-- ${path.join(p, m?.name)}`]
		: m?.type === 'file'
		? [`++ ${path.join(p, m?.name)}`]
		: m?.files?.flatMap(v => getManifestFiles(v, path.join(p, m?.name)))) ?? [];

const getManifestItem = (
	m?: FileManifest,
	p?: string[]
): FileManifest | undefined => {
	if (!p?.length) return m;

	if (m?.type === 'file' || m?.type === 'del')
		throw Error(`Can't access ${p.join('.')} from file ${m.name}`);

	const [next, ...rest] = p;
	return getManifestItem(
		m?.files.find(f => f.name === next),
		rest
	);
};

export const isGameRunning = (executablePath: string) =>
	os.platform() === 'win32'
		? new Promise<boolean>(resolve => {
				const exeName = path.basename(executablePath);
				exec(
					`tasklist /FI "IMAGENAME eq ${exeName}" /FO CSV /NH`,
					(error, stdout) => {
						if (error) {
							Logger.warn(
								`tasklist probe for "${exeName}" failed; assuming game ` +
									`is not running. Error: ${error.message}`
							);
							resolve(false);
							return;
						}
						resolve(
							stdout.toLowerCase().includes(`"${exeName.toLowerCase()}"`)
						);
					}
				);
		  })
		: false;

const toUrlPath = (p: string) =>
	p.split(path.sep).map(encodeURIComponent).join('/');

const CDN_VERSION = EsteriaConfig.clientVersion;

const CONNECT_TIMEOUT_MS = 30_000;
const STALL_TIMEOUT_MS = 60_000;

const isUnsafeName = (name: string) =>
	!name ||
	name === '.' ||
	name === '..' ||
	/[/\\]/.test(name) ||
	path.isAbsolute(name);

const manifestPathsSafe = (m: FileManifest, isRoot = false): boolean => {
	if (!isRoot && isUnsafeName(m.name)) return false;
	if (m.type === 'dir' || m.type === 'mpq')
		return m.files.every(f => manifestPathsSafe(f));
	return true;
};

const fetchManifest = async () => {
	try {
		const r = await fetch(
			`${
				EsteriaConfig.serverUrl
			}/api/file/${CDN_VERSION}/manifest.json`,
			{ timeout: CONNECT_TIMEOUT_MS }
		);
		if (!r.ok) {
			Logger.error(`Update server returned HTTP ${r.status}`);
			return null;
		}
		const j = await r.json();
		if (!j || typeof j !== 'object' || !('root' in j) || !j.root) {
			Logger.error('Update server returned a malformed manifest');
			return null;
		}
		const root = j.root as FileManifest;
		if (!manifestPathsSafe(root, true)) {
			Logger.error(
				'Update server manifest has unsafe path names; refusing it.'
			);
			return null;
		}
		await fs.writeJSON(path.join(Preferences.userDataDir, 'manifest.json'), j);
		return root;
	} catch (e) {
		Logger.error('Failed to reach update server', e);
		return null;
	}
};

const buildClientUrl = (filePath: string) =>
	`${
		EsteriaConfig.serverUrl
	}/client/${CDN_VERSION}/${toUrlPath(path.normalize(filePath))}`;

export const fetchFile = async (
	filePath: string,
	onChunk?: (deltaBytes: number) => void
) => {
	try {
		const response = await fetch(buildClientUrl(filePath), {
			timeout: CONNECT_TIMEOUT_MS
		});
		if (!response.ok) throw Error(`HTTP ${response.status}`);
		if (!onChunk || !response.body) return await response.arrayBuffer();

		const chunks: Buffer[] = [];
		for await (const chunk of response.body as NodeJS.ReadableStream) {
			const buf = Buffer.isBuffer(chunk)
				? chunk
				: Buffer.from(chunk);
			chunks.push(buf);
			onChunk(buf.byteLength);
		}
		const total = chunks.reduce((acc, c) => acc + c.byteLength, 0);
		const out = Buffer.concat(chunks, total);
		return out.buffer.slice(out.byteOffset, out.byteOffset + out.byteLength);
	} catch (e) {
		Logger.error(`Failed to download ${path.normalize(filePath)}`, e);
		throw Error(`Failed to download ${path.normalize(filePath)}`);
	}
};

export const downloadFileToDisk = async (
	filePath: string,
	fullPath: string,
	expectedSize: number,
	onChunk: (deltaBytes: number) => void
) => {
	const partPath = `${fullPath}.part`;
	await fs.ensureFile(partPath);
	let resumeFrom = 0;
	try {
		const stats = await fs.stat(partPath);
		if (stats.size > 0 && stats.size < expectedSize) resumeFrom = stats.size;
		else if (stats.size >= expectedSize) {
			await fs.truncate(partPath, 0);
		}
	} catch (e) {
		Logger.warn(`Failed to resume from "${partPath}".`, e);
	}

	if (resumeFrom > 0) onChunk(resumeFrom);

	const url = buildClientUrl(filePath);
	const headers: Record<string, string> = {};
	if (resumeFrom > 0) headers.Range = `bytes=${resumeFrom}-`;

	const controller = new AbortController();
	let response;
	try {
		response = await fetch(url, {
			headers,
			signal: controller.signal,
			timeout: CONNECT_TIMEOUT_MS
		});
	} catch (e) {
		Logger.error(`Network error downloading ${filePath}`, e);
		throw Error(`Failed to download ${path.normalize(filePath)}`);
	}

	if (!response.ok && response.status !== 206) {
		throw Error(
			`Failed to download ${path.normalize(filePath)}: HTTP ${response.status}`
		);
	}

	if (resumeFrom > 0 && response.status === 200) {
		onChunk(-resumeFrom);
		await fs.truncate(partPath, 0);
		resumeFrom = 0;
	}

	const writeStream = fs.createWriteStream(partPath, {
		flags: resumeFrom > 0 ? 'a' : 'w'
	});

	let stalled = false;
	try {
		await new Promise<void>((resolve, reject) => {
			if (!response.body) {
				reject(Error('No response body'));
				return;
			}
			const body = response.body as NodeJS.ReadableStream;
			let stallTimer: NodeJS.Timeout;
			const armStall = () => {
				clearTimeout(stallTimer);
				stallTimer = setTimeout(() => {
					stalled = true;
					controller.abort();
				}, STALL_TIMEOUT_MS);
			};
			armStall();
			body.on('data', (chunk: Buffer | Uint8Array) => {
				armStall();
				const buf = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
				if (!writeStream.write(buf)) body.pause();
				onChunk(buf.byteLength);
			});
			writeStream.on('drain', () => body.resume());
			body.on('end', () => {
				clearTimeout(stallTimer);
				writeStream.end(resolve);
			});
			body.on('error', err => {
				clearTimeout(stallTimer);
				reject(err);
			});
			writeStream.on('error', err => {
				clearTimeout(stallTimer);
				reject(err);
			});
		});
	} catch (e) {
		writeStream.destroy();
		Logger.error(`Download interrupted for ${filePath}`, e);
		throw Error(
			stalled
				? `Download stalled for ${path.normalize(
						filePath
				  )}; no data received in ${STALL_TIMEOUT_MS / 1000}s.`
				: `Failed to download ${path.normalize(filePath)}`
		);
	}

	const finalStats = await fs.stat(partPath);
	if (finalStats.size !== expectedSize) {
		throw Error(
			`Size mismatch for ${path.normalize(filePath)}: got ${
				finalStats.size
			}, expected ${expectedSize}. Will retry on next run.`
		);
	}

	await fs.move(partPath, fullPath, { overwrite: true });
};

type UpdaterState =
	| 'verifying'
	| 'serverUnreachable'
	| 'noClient'
	| 'updateAvailable'
	| 'updating'
	| 'upToDate'
	| 'failed';

export type UpdaterStatus = {
	state: UpdaterState;
	progress?: number;
	message?: string;
	bytesDone?: number;
	bytesTotal?: number;
	bytesPerSecond?: number;
	etaSeconds?: number;
};

const RATE_WINDOW_MS = 5_000;
const ETA_WARMUP_MS = 10_000;
const ETA_PADDING = 1.15;

class ProgressTracker {
	#startedAt = Date.now();
	#samples: { t: number; bytesDone: number }[] = [];
	bytesDone: number;
	#baseline: number;

	constructor(baseline = 0) {
		this.bytesDone = baseline;
		this.#baseline = baseline;
	}

	add(delta: number) {
		this.bytesDone = Math.max(this.#baseline, this.bytesDone + delta);
		const now = Date.now();
		this.#samples.push({ t: now, bytesDone: this.bytesDone });
		const cutoff = now - RATE_WINDOW_MS;
		while (this.#samples.length > 2 && this.#samples[0].t < cutoff)
			this.#samples.shift();
	}

	bytesPerSecond() {
		if (this.#samples.length < 2) return 0;
		const first = this.#samples[0];
		const last = this.#samples[this.#samples.length - 1];
		const dt = (last.t - first.t) / 1000;
		if (dt <= 0) return 0;
		return Math.max(0, (last.bytesDone - first.bytesDone) / dt);
	}

	etaSeconds(bytesTotal: number) {
		if (Date.now() - this.#startedAt < ETA_WARMUP_MS) return undefined;
		const rate = this.bytesPerSecond();
		if (rate <= 0) return undefined;
		const remaining = bytesTotal - this.bytesDone;
		if (remaining <= 0) return 0;
		return (remaining / rate) * ETA_PADDING;
	}
}

class UpdaterClass extends Observable<UpdaterStatus> {
	#manifest?: FileManifest;
	#clientTotalBytes = 0;
	#bytesAlreadyOnDisk = 0;
	#cachePath = path.join(Preferences.userDataDir, 'cache.json');
	#cache: CacheTree = this.#readCache();

	#readCache(): CacheTree {
		try {
			return fs.existsSync(this.#cachePath) ? fs.readJSONSync(this.#cachePath) : {};
		} catch {
			return {};
		}
	}

	async #saveCache() {
		await fs.writeJSON(this.#cachePath, this.#cache);
	}

	async #getHash(
		{
			clientPath,
			...m
		}: { clientPath: string } & (
			| { hMpq: HANDLE; mpqPath: string[] }
			| { hMpq?: never }
		),
		...filePath: string[]
	) {
		if (m.hMpq) {
			if (!SFileHasFile(m.hMpq, path.join(...filePath))) {
				nestedSet(this.#cache, filePath, undefined);
				return undefined;
			}
			const c = nestedGet<CacheEntry>(this.#cache, [...m.mpqPath, ...filePath]);

			if (c?.[0]) return c[0];

			const hFile = SFileOpenFileEx(m.hMpq, path.join(...filePath), 0);

			try {
				const fileSize = Number(SFileGetFileSize(hFile).toString());

				const buffer = new ArrayBuffer(fileSize);
				if (fileSize > 0) SFileReadFile(hFile, buffer);

				const newHash = crypto
					.createHash('sha1')
					.update(new Uint8Array(buffer))
					.digest('hex')
					.toLocaleUpperCase();

				nestedSet(this.#cache, [...m.mpqPath, ...filePath], { [0]: newHash });
				return newHash;
			} finally {
				SFileCloseFile(hFile);
			}
		}

		if (!(await fs.exists(path.join(clientPath, ...filePath)))) {
			nestedSet(this.#cache, filePath, undefined);
			return undefined;
		}

		const stats = await fs.stat(path.join(clientPath, ...filePath));
		if (stats.isDirectory())
			throw Error(`Tried to get hash of directory ${path.join(...filePath)}`);

		const c = nestedGet<CacheEntry>(this.#cache, filePath);

		if (c?.[0] && c[1] === stats.mtimeMs) return c[0];

		const newHash = crypto
			.createHash('sha1')
			.update(await fs.readFile(path.join(clientPath, ...filePath)))
			.digest('hex')
			.toLocaleUpperCase();
		nestedSet(this.#cache, filePath, {
			...c,
			[0]: newHash,
			[1]: stats.mtimeMs
		});
		return newHash;
	}

	protected _value: UpdaterStatus = { state: 'failed' };

	get status() {
		return this._value;
	}
	private set status(v: UpdaterStatus) {
		this._value = v;
		this._notifyObservers(v);
		if (this.status.state === 'failed') {
			mainWindow?.setProgressBar(1, { mode: 'error' });
		} else if (this.status.progress === 1) {
			mainWindow?.setProgressBar(0);
		} else {
			mainWindow?.setProgressBar(this.status.progress ?? 0, {
				mode: this.status.progress === -1 ? 'indeterminate' : 'normal'
			});
		}
	}

	async verify() {
		if (this.status?.state === 'verifying' || this.status?.state === 'updating')
			return;

		const clientPath = Preferences.data.clientDir;
		if (!clientPath) {
			this.status = { state: 'noClient' };
			return;
		}

		if (os.platform() === 'win32' && clientPath.length > 220) {
			this.status = {
				state: 'failed',
				message:
					'Path to current install location is too long and may cause issues.'
			};
			return;
		}

		if (await isGameRunning(path.join(clientPath, 'WoW.exe'))) {
			this.status = {
				state: 'failed',
				message: 'Please close WoW first, before updating.'
			};
			return;
		}

		Logger.log(`Verifying client files at ${path.join(clientPath)}...`);
		this.status = {
			state: 'verifying',
			progress: -1,
			message: 'Looking for updates...'
		};

		try {
			const hashTree = await fetchManifest();
			if (!hashTree) {
				this.status = { state: 'serverUnreachable' };
				return;
			}
			this.#manifest = { type: 'dir', name: 'root', files: [] };

			const totalSize = getManifestSize(hashTree);
			let i = 0;

			const buildMpqTree = async (
				hMpq: HANDLE,
				mpqPath: string[],
				...filePath: string[]
			): Promise<FileManifest | undefined> => {
				const item = getManifestItem(hashTree, [...mpqPath, ...filePath]);
				if (!item) return undefined;

				if (item.type === 'del') return item;

				if (item.type === 'dir') {
					const files = (
						await asyncMap(item.files, f =>
							buildMpqTree(hMpq, mpqPath, ...filePath, f.name)
						)
					).filter(isNotUndef);
					return !files.length ? undefined : { ...item, files };
				}

				if (item.type === 'mpq')
					throw Error(
						`There can't be an mpq archive inside mpq at path ${path.join(
							...mpqPath,
							...filePath
						)}`
					);

				this.status = {
					state: 'verifying',
					progress: i / totalSize,
					message: `Verifying: [${mpqPath.at(-1)}] "${path.join(
						...filePath
					)}"...`
				};

				i += item.size;

				if (
					(await this.#getHash({ clientPath, hMpq, mpqPath }, ...filePath)) ===
					item.hash
				)
					return undefined;
				return item;
			};

			const buildTree = async (
				...filePath: string[]
			): Promise<FileManifest | undefined> => {
				const item = getManifestItem(hashTree, filePath);
				if (!item) return undefined;

				if (item.type === 'del') {
					if (await fs.exists(path.join(clientPath, ...filePath)))
						return item;
					return undefined;
				}

				if (item.type === 'dir') {
					const files = (
						await asyncMap(item.files, f => buildTree(...filePath, f.name))
					).filter(isNotUndef);

					return !files.length ? undefined : { ...item, files };
				}

				if (item.type === 'mpq') {
					const patchPath = [
						...filePath.slice(0, -1),
						`${filePath.at(-1)}.mpq`
					];
					this.status = {
						state: 'verifying',
						progress: i / totalSize,
						message: `Verifying: "${path.join(...patchPath)}"...`
					};

					if (!(await fs.exists(path.join(clientPath, ...patchPath)))) {
						i += item.size;
						return {
							type: 'file',
							name: `${item.name}.mpq`,
							hash: item.hash,
							size: item.size
						};
					}

					if (
						(await this.#getHash({ clientPath }, ...patchPath)) === item.hash
					) {
						i += item.size;
						return undefined;
					}

					try {
						const hMpq = SFileOpenArchive(
							path.join(clientPath, ...patchPath),
							STREAM_FLAG.READ_ONLY
						);

						try {
							const files = (
								await asyncMap(item.files, f =>
									buildMpqTree(hMpq, filePath, f.name)
								)
							).filter(isNotUndef);
							return !files.length ? undefined : { ...item, files };
						} finally {
							SFileCloseArchive(hMpq);
						}
					} catch (e) {
						Logger.warn(
							`Failed to verify ${path.join(
								...patchPath
							)}, will be downloaded fresh`,
							e
						);
						return {
							type: 'file',
							name: `${item.name}.mpq`,
							hash: item.hash,
							size: item.size
						};
					}
				}

				this.status = {
					state: 'verifying',
					progress: i / totalSize,
					message: `Verifying: "${path.join(...filePath)}"...`
				};

				i += item.size;

				const hash = await this.#getHash({ clientPath }, ...filePath);

				if (hash === item.hash) return undefined;

				if (hash && item.version) {
					const stats = await fs.stat(path.join(clientPath, ...filePath));
					if (item.version <= stats.mtimeMs) return undefined;
				}

				return item;
			};

			this.#manifest = await buildTree();

			await this.#saveCache();

			const toDownload = getManifestSize(this.#manifest);
			this.#clientTotalBytes = getManifestSize(hashTree);
			this.#bytesAlreadyOnDisk = Math.max(
				0,
				this.#clientTotalBytes - toDownload
			);
			const availableSpace = await getAvailableDiskSpace();

			if (toDownload > availableSpace) {
				this.status = {
					state: 'failed',
					message: `Not enough disk space. Required: ${formatFileSize(
						toDownload
					)}, Available: ${formatFileSize(availableSpace)}`
				};
				return;
			}

			this.status = this.#manifest
				? {
						state: 'updateAvailable',
						message: formatFileSize(toDownload),
						progress: this.#bytesAlreadyOnDisk / this.#clientTotalBytes,
						bytesDone: this.#bytesAlreadyOnDisk,
						bytesTotal: this.#clientTotalBytes
				  }
				: { state: 'upToDate', progress: 1 };
			this.#manifest &&
				Logger.log(
					`Detected changes:\n\t${getManifestFiles(this.#manifest).join(
						',\n\t'
					)}`
				);

		} catch (e) {
			const message = friendlyError(e);
			Logger.error(`Verification failed: ${message}`, e);
			this.status = { state: 'failed', message };
		}
	}

	async update(clean?: boolean) {
		if (this.status?.state === 'verifying' || this.status?.state === 'updating')
			return;

		const clientPath = Preferences.data.clientDir;
		if (!clientPath) {
			this.status = { state: 'noClient' };
			return;
		}

		if (await isGameRunning(path.join(clientPath, 'WoW.exe'))) {
			this.status = {
				state: 'failed',
				message: 'Please close WoW first, before updating.'
			};
			return;
		}

		Logger.log(`Updating client files at ${path.join(clientPath)}...`);
		this.status = {
			state: 'updating',
			progress: -1,
			message: 'Preparing files...'
		};

		try {
			if (clean) {
				const resolvedClientPath = path.resolve(clientPath);
				const isFilesystemRoot =
					path.parse(resolvedClientPath).root === resolvedClientPath;
				if (
					isFilesystemRoot ||
					!fs.existsSync(path.join(resolvedClientPath, 'WoW.exe'))
				) {
					this.status = {
						state: 'failed',
						message:
							'Refusing to clean: the client folder does not look like a valid WoW install.'
					};
					return;
				}

				this.status = {
					state: 'updating',
					progress: -1,
					message: 'Cleaning up old files...'
				};

				const preserve = new Set([
					'esteria launcher.exe',
					'.launcher',
					'wtf',
					'interface',
					'screenshots'
				]);
				const files = await fs.readdir(clientPath);
				for (const file of files) {
					if (preserve.has(file.toLowerCase())) continue;
					await fs.rm(path.join(clientPath, file), {
						recursive: true,
						force: true
					});
				}

				this.#bytesAlreadyOnDisk = 0;
			}
			const hashTree =
				(clean ? undefined : this.#manifest) ?? (await fetchManifest());

			if (!hashTree) {
				this.status = { state: 'serverUnreachable' };
				return;
			}

			const fullClientTotal =
				this.#clientTotalBytes > 0
					? this.#clientTotalBytes
					: getManifestSize(hashTree);
			this.#clientTotalBytes = fullClientTotal;
			const baseline = this.#bytesAlreadyOnDisk;
			const tracker = new ProgressTracker(baseline);
			let lastEmit = 0;
			const STATUS_EMIT_INTERVAL_MS = 250;

			const emitProgress = (message: string, force = false) => {
				const now = Date.now();
				if (!force && now - lastEmit < STATUS_EMIT_INTERVAL_MS) return;
				lastEmit = now;
				this.status = {
					state: 'updating',
					progress: tracker.bytesDone / fullClientTotal,
					message,
					bytesDone: tracker.bytesDone,
					bytesTotal: fullClientTotal,
					bytesPerSecond: tracker.bytesPerSecond(),
					etaSeconds: tracker.etaSeconds(fullClientTotal)
				};
			};

			const iterateMpqTree = async (
				hMpq: HANDLE,
				mpqPath: string[],
				...filePath: string[]
			) => {
				const item = getManifestItem(hashTree, [...mpqPath, ...filePath]);
				if (!item) return undefined;

				if (item.type === 'del') {
					if (SFileHasFile(hMpq, path.join(...filePath)))
						SFileRemoveFile(hMpq, path.join(...filePath));
					nestedSet(this.#cache, [...mpqPath, ...filePath], undefined);
					return;
				}

				if (item.type === 'dir') {
					for (const f of item.files)
						await iterateMpqTree(hMpq, mpqPath, ...filePath, f.name);
					return;
				}

				if (item.type === 'mpq')
					throw Error(
						`There can't be an mpq archive inside mpq at path ${path.join(
							...mpqPath,
							...filePath
						)}`
					);

				const label = `Patching: [${mpqPath.at(-1)}] "${path.join(
					...filePath
				)}"`;
				emitProgress(label, true);

				const data = await fetchFile(
					path.join(...mpqPath, ...filePath),
					delta => {
						tracker.add(delta);
						emitProgress(label);
					}
				);

				if (SFileHasFile(hMpq, path.join(...filePath)))
					SFileRemoveFile(hMpq, path.join(...filePath));

				const hFile = SFileCreateFile(
					hMpq,
					path.join(...filePath),
					0,
					data.byteLength,
					0,
					MPQ_FILE.COMPRESS
				);
				try {
					SFileWriteFile(hFile, data, MPQ_COMPRESSION.ZLIB);
				} finally {
					SFileFinishFile(hFile);
				}
				nestedSet(this.#cache, [...mpqPath, ...filePath], undefined);
			};

			const iterateTree = async (...filePath: string[]) => {
				const item = getManifestItem(hashTree, filePath);
				if (!item) return undefined;

				if (item.type === 'del') {
					const fullPath = path.join(clientPath, ...filePath);
					if (await isReadOnly(fullPath))
						throw Error(
							`Failed to delete "${fullPath}" because it's read-only.`
						);

					await fs.remove(fullPath);

					await this.#getHash({ clientPath }, ...filePath);
					return;
				}

				if (item.type === 'dir') {
					for (const i of item.files) await iterateTree(...filePath, i.name);
					return;
				}

				if (item.type === 'mpq') {
					const patchPath = [
						...filePath.slice(0, -1),
						`${filePath.at(-1)}.mpq`
					];
					const patchFile = path.join(clientPath, ...patchPath);
					const label = `Downloading: "${path.join(...patchPath)}"`;
					emitProgress(label, true);

					if (!(await fs.exists(patchFile))) {
						await downloadFileToDisk(
							path.join(...patchPath),
							patchFile,
							item.size,
							delta => {
								tracker.add(delta);
								emitProgress(label);
							}
						);
						return;
					}

					if (await isReadOnly(patchFile))
						throw Error(
							`Failed to update "${patchFile}" because it's read-only.`
						);

					const hMpq = SFileOpenArchive(path.join(clientPath, ...patchPath), 0);
					try {
						for (const f of item.files)
							await iterateMpqTree(hMpq, filePath, f.name);
						SFileFlushArchive(hMpq);
						SFileCompactArchive(hMpq);
					} finally {
						SFileCloseArchive(hMpq);
					}
					return;
				}

				const label = `Downloading: "${path.join(...filePath)}"`;
				emitProgress(label, true);

				const fullPath = path.join(clientPath, ...filePath);
				if ((await fs.exists(fullPath)) && (await isReadOnly(fullPath)))
					throw Error(`Failed to update "${fullPath}" because it's read-only.`);

				await downloadFileToDisk(
					path.join(...filePath),
					fullPath,
					item.size,
					delta => {
						tracker.add(delta);
						emitProgress(label);
					}
				);

				await this.#getHash({ clientPath }, ...filePath);
			};

			await iterateTree();
			await this.#saveCache();

			Preferences.data = { version: EsteriaConfig.clientVersion };

			this.#bytesAlreadyOnDisk = fullClientTotal;
			this.status = { state: 'upToDate', progress: 1 };
		} catch (e) {
			Logger.error('Update failed', e);
			this.status = { state: 'failed', message: friendlyError(e) };
		}
	}

}

const Updater = new UpdaterClass();
export default Updater;
