import crypto from 'crypto';
import path from 'path';

import fs from 'fs-extra';

const allowedExtra = [
	'.launcher',
	'Data',
	'Errors',
	'Interface\\AddOns',
	'Logs',
	'Screenshots',
	'WDB',
	'WTF\\Account'
];

const skipFiles = new Set([
	'manifest.json',
	'manifest.json.tmp',
	'wow-client.zip',
	'.gitkeep',
	'.manifest-overrides.json'
]);

const skipPatterns: RegExp[] = [
	/\.bak([.\-]|$)/,
	/\.crashing(\.|$)/,
	/\.torrent$/,
	/^manifest\.json\./
];
const isSkipPattern = (file: string) => skipPatterns.some(p => p.test(file));

const skipDirsPosix = new Set([
	'Errors',
	'Logs',
	'Screenshots',
	'WDB',
	'WTF/Account'
]);
const isSkipDir = (...filePath: string[]) =>
	skipDirsPosix.has(filePath.join('/'));
const isPatchDirectory = (file: string) =>
	/patch-./.test(file) && !file.toLowerCase().endsWith('.mpq');

type FolderTags = 'allowExtra';

type FileManifest = { name: string } & (
	| { type: 'dir'; files: FileManifest[]; tags?: FolderTags[] }
	| { type: 'mpq'; files: FileManifest[]; hash: string; size: number }
	| {
			type: 'file';
			hash: string;
			version?: number;
			size: number;
		}
	| { type: 'del' }
);

export type BuildProgress = {
	state: 'idle' | 'building' | 'ready' | 'failed';
	done: number;
	total: number;
	currentFile: string;
	startedAt: number | null;
	finishedAt: number | null;
	error: string | null;
};

export type ProgressCallback = (
	p: Pick<BuildProgress, 'done' | 'total' | 'currentFile'>
) => void;

const getHash = (...filePath: string[]): Promise<string> =>
	new Promise((resolve, reject) => {
		const hash = crypto.createHash('sha1');
		const stream = fs.createReadStream(path.join(...filePath));
		stream.on('error', reject);
		stream.on('data', (chunk: Buffer) => hash.update(chunk));
		stream.on('end', () => resolve(hash.digest('hex').toLocaleUpperCase()));
	});

const countFiles = async (
	clientPath: string,
	...filePath: string[]
): Promise<number> => {
	let total = 0;
	const dir = path.join(clientPath, ...filePath);
	const files = await fs.readdir(dir);
	for (const file of files.sort()) {
		if (skipFiles.has(file)) continue;
		if (isSkipPattern(file)) continue;
		const stats = await fs.stat(path.join(dir, file));
		if (stats.isDirectory()) {
			if (isSkipDir(...filePath, file)) continue;
			if (isPatchDirectory(file)) {
				const mpqPath = path.join(dir, `${file}.mpq`);
				if (await fs.pathExists(mpqPath)) total += 1;
			}
			total += await countFiles(clientPath, ...filePath, file);
		} else {
			total += 1;
		}
	}
	return total;
};

export const buildCache = async (
	clientPath: string,
	onProgress?: ProgressCallback
) => {
	console.log('Building cache...');

	const prevManifestPath = path.join(clientPath, 'manifest.json');
	let prevManifestMtimeMs = 0;
	const prevHashByPath = new Map<string, string>();
	const prevVersionByPath = new Map<string, number | undefined>();
	const prevSizeByPath = new Map<string, number>();
	try {
		const prevStat = await fs.stat(prevManifestPath);
		prevManifestMtimeMs = prevStat.mtimeMs;
		const prev = await fs.readJSON(prevManifestPath);
		const walk = (node: FileManifest, prefix: string[]) => {
			if (node.type === 'dir' || node.type === 'mpq') {
				const newPrefix = node.name ? [...prefix, node.name] : prefix;
				if (node.type === 'mpq') {
					const mpqKey = [...newPrefix.slice(0, -1), node.name + '.mpq'].join(
						'/'
					);
					prevHashByPath.set(mpqKey, node.hash);
					prevSizeByPath.set(mpqKey, node.size);
				}
				for (const child of node.files) walk(child, newPrefix);
			} else {
				const key = [...prefix, node.name].join('/');
				prevHashByPath.set(key, node.hash);
				prevVersionByPath.set(key, node.version);
				prevSizeByPath.set(key, node.size);
			}
		};
		walk(prev.root, []);
		console.log(
			`mtime-skip: loaded ${prevHashByPath.size} cached hashes from ` +
				`prior manifest (mtime=${new Date(prevManifestMtimeMs).toISOString()})`
		);
	} catch (e) {
		console.log(
			'mtime-skip: no usable prior manifest, full rebuild ' +
				`(${(e as Error).message})`
		);
	}

	const total = await countFiles(clientPath);
	let done = 0;
	let reused = 0;
	const tick = (currentFile: string) => {
		done += 1;
		onProgress?.({ done, total, currentFile });
	};
	console.log(`Building cache: ${total} files to hash...`);

	const getHashCached = async (
		relPath: string,
		mtimeMs: number,
		...filePath: string[]
	): Promise<string> => {
		if (prevManifestMtimeMs > 0 && mtimeMs <= prevManifestMtimeMs) {
			const cached = prevHashByPath.get(relPath);
			if (cached) {
				reused++;
				return cached;
			}
		}
		return getHash(clientPath, ...filePath);
	};

	const buildTree = async (...filePath: string[]): Promise<FileManifest[]> => {
		const files = await fs.readdir(path.join(clientPath, ...filePath));

		const patches: string[] = [];
		const tree: FileManifest[] = [];
		for (const file of files.sort()) {
			if (skipFiles.has(file)) continue;
			if (isSkipPattern(file)) continue;

			const stats = await fs.stat(path.join(clientPath, ...filePath, file));

			if (stats.isDirectory()) {
				if (isSkipDir(...filePath, file)) continue;
				if (isPatchDirectory(file)) {
					patches.push(file);
					const mpqRelPath = path
						.join(...filePath, `${file}.mpq`)
						.split(path.sep)
						.join('/');
					const mpqStat = await fs.stat(
						path.join(clientPath, ...filePath, `${file}.mpq`)
					);
					tree.push({
						type: 'mpq',
						name: file,
						files: await buildTree(...filePath, file),
						size: mpqStat.size,
						hash: await getHashCached(
							mpqRelPath,
							mpqStat.mtimeMs,
							...filePath,
							`${file}.mpq`
						)
					});
					tick(mpqRelPath);
				} else {
					const tags: FolderTags[] = [];
					allowedExtra.includes(path.join(...filePath, file)) &&
						tags.push('allowExtra');
					tree.push({
						type: 'dir',
						name: file,
						files: await buildTree(...filePath, file),
						tags: tags.length ? tags : undefined
					});
				}
				continue;
			}

			if (patches.find(v => file.match(v))) continue;

			const allowModifiedPaths = new Set([
				'WTF/Config.wtf',
				'Data/fonts.MPQ',
				'Data/sound.MPQ',
				'Data/speech.MPQ'
			]);
			const fullPath = path
				.join(...filePath, file)
				.split(path.sep)
				.join('/');
			const allowModified =
				file === 'WoW.exe' || allowModifiedPaths.has(fullPath);

			tree.push({
				type: 'file',
				name: file,
				hash: await getHashCached(fullPath, stats.mtimeMs, ...filePath, file),
				version: allowModified ? stats.mtimeMs : undefined,
				size: stats.size
			});
			tick(fullPath);
		}
		return tree;
	};

	const rootFiles = await buildTree();

	const overridesPath = path.join(clientPath, '.manifest-overrides.json');
	try {
		if (await fs.pathExists(overridesPath)) {
			const ov = await fs.readJSON(overridesPath);
			const dels: string[] = Array.isArray(ov.del) ? ov.del : [];
			for (const relPath of dels) {
				const parts = relPath.split('/').filter(Boolean);
				if (parts.length === 0) continue;
				const fileName = parts.pop()!;
				let dirNode: FileManifest = {
					type: 'dir',
					name: '',
					files: rootFiles
				} as FileManifest;
				let ok = true;
				for (const seg of parts) {
					if (dirNode.type !== 'dir' && dirNode.type !== 'mpq') {
						ok = false;
						break;
					}
					let child = dirNode.files.find(f => f.name === seg);
					if (!child) {
						child = {
							type: 'dir',
							name: seg,
							files: [],
							tags: ['allowExtra']
						};
						dirNode.files.push(child);
					}
					dirNode = child;
				}
				if (!ok || (dirNode.type !== 'dir' && dirNode.type !== 'mpq')) {
					console.warn(
						`manifest-overrides: del path "${relPath}" hit a non-dir ` +
							`node, skipping`
					);
					continue;
				}
				const exists = dirNode.files.some(
					f => f.name === fileName && f.type === 'del'
				);
				if (!exists) {
					dirNode.files.push({ type: 'del', name: fileName } as FileManifest);
					console.log(
						`manifest-overrides: inserted {type:'del', name:'${fileName}'} ` +
							`under ${parts.join('/') || '<root>'}`
					);
				}
			}
		}
	} catch (e) {
		console.warn(
			`manifest-overrides: failed to apply ${overridesPath}, continuing` +
				`without overrides (${(e as Error).message})`
		);
	}

	const finalPath = path.join(clientPath, 'manifest.json');
	const tmpPath = path.join(clientPath, 'manifest.json.tmp');
	await fs.writeJSON(tmpPath, {
		build: 3,
		buildName: '3',
		root: {
			type: 'dir',
			name: '',
			files: rootFiles
		}
	});
	await fs.rename(tmpPath, finalPath);
	if (prevManifestMtimeMs > 0) {
		console.log(
			`mtime-skip: reused ${reused}/${total} cached hashes ` +
				`(re-hashed ${total - reused})`
		);
	}
};
