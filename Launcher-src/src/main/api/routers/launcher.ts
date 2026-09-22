import path from 'path';
import { spawn } from 'child_process';

import fs from 'fs-extra';
import Logger from 'electron-log/main';

import Preferences from '~main/modules/preferences';
import { mainWindow } from '~main/index';
import { isGameRunning } from '~main/modules/updater';
import { patchConfig } from '~main/modules/patcher';
import { applyLocalePatch } from '~main/modules/localePatch';
import { minimizeToTray, restoreFromTray } from '~main/modules/tray';

import { createTRPCRouter, publicProcedure } from '../trpc';

type StartResult = { ok: boolean; error?: string };

export const launcherRouter = createTRPCRouter({
	start: publicProcedure.mutation(async (): Promise<StartResult> => {
		const { cleanWdb, minimizeToTrayOnPlay, clientDir } = Preferences.data;
		if (!clientDir) return { ok: false, error: 'No game folder is set.' };

		const exePath = path.join(clientDir, 'WoW.exe');
		if (!(await fs.pathExists(exePath)))
			return { ok: false, error: 'WoW.exe was not found in the game folder.' };
		if (await isGameRunning(exePath))
			return { ok: false, error: 'WoW is already running.' };

		if (cleanWdb) {
			Logger.log('Cleaning up WDB...');
			await fs.remove(path.join(clientDir, 'WDB'));
		}

		Logger.log('Checking Config.wtf...');
		await patchConfig();

		Logger.log('Applying UI language...');
		await applyLocalePatch(clientDir, Preferences.data.locale);

		Logger.log(`Launching ${exePath}...`);
		const child = spawn(exePath, {
			cwd: clientDir,
			detached: !minimizeToTrayOnPlay
		});

		try {
			await new Promise<void>((resolve, reject) => {
				child.once('spawn', resolve);
				child.once('error', reject);
			});
		} catch (e) {
			Logger.error('Failed to launch the game', e);
			const message = e instanceof Error ? e.message : String(e);
			return { ok: false, error: `Failed to launch the game: ${message}` };
		}

		child.on('error', e => Logger.error('Game process error', e));

		if (!minimizeToTrayOnPlay) {
			mainWindow?.close();
			return { ok: true };
		}

		minimizeToTray();
		child.on('exit', () => {
			Logger.log('WoW stopped');
			restoreFromTray();
		});
		return { ok: true };
	})
});
