import path from 'path';

import fs from 'fs-extra';
import { type z } from 'zod';
import { app } from 'electron';
import Logger from 'electron-log/main';

import { PreferencesSchema } from '~common/schemas';
import { omit } from '~common/utils';

const portableDir = process.env.PORTABLE_EXECUTABLE_DIR;

abstract class Preferences {
	static #data: z.infer<typeof PreferencesSchema>;
	static #writeChain: Promise<void> = Promise.resolve();

	static readonly userDataDir = process.env.PORTABLE_EXECUTABLE_DIR
		? path.join(process.env.PORTABLE_EXECUTABLE_DIR, '.launcher')
		: app.getPath('userData');

	static async load() {
		await fs.ensureDir(this.userDataDir);
		const settingsPath = path.join(this.userDataDir, 'settings.json');

		let json: Record<string, unknown>;
		try {
			json = await fs.readJSON(settingsPath);
		} catch {
			return PreferencesSchema.parse({
				isPortable: !!portableDir,
				clientDir: portableDir
			});
		}

		const merged = {
			...json,
			isPortable: !!portableDir,
			clientDir: portableDir ?? json.clientDir
		};

		const parsed = PreferencesSchema.safeParse(merged);
		if (parsed.success) return parsed.data;

		Logger.warn(
			'settings.json failed validation; salvaging valid fields',
			parsed.error
		);
		await fs.copy(settingsPath, `${settingsPath}.corrupt`).catch(() => {});

		const salvaged: Record<string, unknown> = {
			isPortable: !!portableDir,
			clientDir: portableDir ?? json.clientDir
		};
		const shape = PreferencesSchema.shape;
		for (const key of Object.keys(shape) as (keyof typeof shape)[]) {
			if (!(key in merged)) continue;
			const value = (merged as Record<string, unknown>)[key];
			if (shape[key].safeParse(value).success) salvaged[key] = value;
		}
		return PreferencesSchema.parse(salvaged);
	}

	static get data(): PreferencesSchema {
		return this.#data;
	}

	static set data(newData: Partial<Omit<PreferencesSchema, 'portableDir'>>) {
		this.#data = { ...this.#data, ...newData };

		const settingsPath = path.join(this.userDataDir, 'settings.json');
		const delta = omit(
			newData,
			portableDir ? ['isPortable', 'clientDir'] : ['isPortable']
		);
		const snapshot = omit(
			this.#data,
			portableDir ? ['isPortable', 'clientDir'] : ['isPortable']
		);
		this.#writeChain = this.#writeChain
			.then(async () => {
				let onDisk: unknown = null;
				try {
					onDisk = await fs.readJSON(settingsPath);
				} catch {
					onDisk = null;
				}
				const base =
					!!onDisk && typeof onDisk === 'object' && !Array.isArray(onDisk)
						? (onDisk as Record<string, unknown>)
						: null;
				const merged = base ? { ...base, ...delta } : snapshot;
				const tmp = `${settingsPath}.tmp`;
				await fs.writeJSON(tmp, merged, { spaces: 2 });
				await fs.move(tmp, settingsPath, { overwrite: true });
			})
			.catch(e => Logger.error('Failed to persist settings.json', e));
	}

	static save() {
		return this.#writeChain;
	}

	static async isValidClientDir(clientDir?: string) {
		return !!clientDir && (await fs.exists(path.join(clientDir, 'WoW.exe')));
	}
}

export default Preferences;
