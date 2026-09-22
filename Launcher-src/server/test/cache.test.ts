import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';

import { buildCache } from '../src/cache.js';

test('builds a manifest for a directory whose name already ends in .mpq', async () => {
	const clientPath = await mkdtemp(path.join(os.tmpdir(), 'esteria-cache-'));
	try {
		const stagedPath = path.join(clientPath, 'Data', 'patch-K.mpq');
		await mkdir(stagedPath, { recursive: true });
		await writeFile(path.join(stagedPath, 'entry.txt'), 'payload');

		await assert.doesNotReject(() => buildCache(clientPath));

		const manifest = JSON.parse(
			await readFile(path.join(clientPath, 'manifest.json'), 'utf8')
		);
		const data = manifest.root.files.find(
			(file: { name: string }) => file.name === 'Data'
		);
		const staged = data.files.find(
			(file: { name: string }) => file.name === 'patch-K.mpq'
		);

		assert.equal(staged.type, 'dir');
		assert.equal(staged.files[0].name, 'entry.txt');
	} finally {
		await rm(clientPath, { recursive: true, force: true });
	}
});
