import path from 'path';

import express from 'express';
import fs from 'fs-extra';
import { buildCache, type BuildProgress } from './cache.js';
import { getAddons, warmUp as warmUpAddons } from './addons-resolver.js';

const SourceDir = process.env.SOURCE_DIR || './client';
const LauncherUpdatesDir = process.env.LAUNCHER_UPDATES_DIR || './launcher-updates';

const app = express();
const port = 7384;

app.use('/launcher-updates', express.static(LauncherUpdatesDir));

const buildProgress: BuildProgress = {
	state: 'idle',
	done: 0,
	total: 0,
	currentFile: '',
	startedAt: null,
	finishedAt: null,
	error: null
};

let buildInFlight: Promise<void> | null = null;
const ensureManifestBuilt = (): Promise<void> => {
	if (buildInFlight) return buildInFlight;
	buildProgress.state = 'building';
	buildProgress.done = 0;
	buildProgress.total = 0;
	buildProgress.currentFile = '';
	buildProgress.startedAt = Date.now();
	buildProgress.finishedAt = null;
	buildProgress.error = null;
	buildInFlight = buildCache(SourceDir, p => {
		buildProgress.done = p.done;
		buildProgress.total = p.total;
		buildProgress.currentFile = p.currentFile;
	})
		.then(() => {
			buildProgress.state = 'ready';
			buildProgress.finishedAt = Date.now();
		})
		.catch(e => {
			buildProgress.state = 'failed';
			buildProgress.error = e instanceof Error ? e.message : String(e);
			buildProgress.finishedAt = Date.now();
			buildInFlight = null;
			throw e;
		});
	return buildInFlight;
};

app.get('/api/build-status', (_req, res) => {
	res.json(buildProgress);
});

app.get('/api/file/:version/manifest.json', async (_req, res) => {
	console.log(`Fetching manifest`);
	const filePath = path.join(SourceDir, 'manifest.json');

	if (await fs.pathExists(filePath)) {
		res.json(await fs.readJSON(filePath));
		return;
	}

	void ensureManifestBuilt().catch(() => {});
	res.setHeader('Retry-After', '5');
	res.status(503).json({
		error: 'manifest_building',
		message:
			'Manifest is being built for the first time on this server. ' +
			'Poll /api/build-status for progress; retry this endpoint when ready.',
		buildProgress
	});
});

app.get(
	'/client/:version/*',
	async (req: express.Request<{ 0: string }>, res) => {
		const filePath = req.params[0];
		console.log(`Fetching file: ${filePath}`);

		const root = path.resolve(SourceDir);
		const target = path.resolve(SourceDir, filePath);
		if (target !== root && !target.startsWith(root + path.sep)) {
			res.status(403).end();
			return;
		}

		res.sendFile(target);
	}
);

app.get('/api/addons.json', async (req, res) => {
	try {
		const force = req.query.refresh === '1';
		const addons = await getAddons(force);
		res.json(addons);
	} catch (e) {
		console.error('Failed to resolve addons:', e);
		res.status(500).json({ error: 'Failed to resolve addons' });
	}
});

app.get('/health', (_req, res) => {
	res.json({ ok: true });
});

const newestSourceMtime = async (dir: string): Promise<number> => {
	let newest = 0;
	const entries = await fs.readdir(dir);
	for (const name of entries) {
		if (name === 'manifest.json' || name === 'manifest.json.tmp') continue;
		const full = path.join(dir, name);
		const stat = await fs.stat(full);
		if (stat.isDirectory()) {
			const inner = await newestSourceMtime(full);
			if (inner > newest) newest = inner;
		} else if (stat.mtimeMs > newest) {
			newest = stat.mtimeMs;
		}
	}
	return newest;
};

app.listen(port, () => {
	console.log(`Server listening on port ${port}`);
	warmUpAddons();

	void (async () => {
		const manifestPath = path.join(SourceDir, 'manifest.json');
		if (!fs.existsSync(manifestPath)) {
			console.log(`Pre-warming manifest cache for ${SourceDir}...`);
			try {
				await ensureManifestBuilt();
				console.log(`Manifest cache pre-warm complete.`);
			} catch (e) {
				console.error(
					'Manifest pre-warm failed (will fall back to lazy build on first request):',
					e
				);
			}
			return;
		}

		buildProgress.state = 'ready';
		buildProgress.finishedAt = Date.now();

		try {
			const manifestStat = await fs.stat(manifestPath);
			const newest = await newestSourceMtime(SourceDir);
			if (newest > manifestStat.mtimeMs) {
				console.log(
					`Manifest is stale (newest source mtime ${new Date(
						newest
					).toISOString()} > manifest ${new Date(
						manifestStat.mtimeMs
					).toISOString()}); rebuilding in background.`
				);
				ensureManifestBuilt()
					.then(() => console.log('Background manifest rebuild complete.'))
					.catch(e => console.error('Background manifest rebuild failed:', e));
			} else {
				console.log(
					`Manifest cache already on disk at ${manifestPath} and up to date; no rebuild needed.`
				);
			}
		} catch (e) {
			console.error('Manifest staleness check failed:', e);
		}
	})();
});
