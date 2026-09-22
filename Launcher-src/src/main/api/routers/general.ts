import { app, dialog, shell } from 'electron';
import Logger from 'electron-log/main';
import { z } from 'zod';

import { mainWindow } from '~main/index';
import Preferences from '~main/modules/preferences';
import { detectHardware, recommendFarClip } from '~main/modules/hardware';

import { createTRPCRouter, publicProcedure } from '../trpc';

export const generalRouter = createTRPCRouter({
	appVersion: publicProcedure.query(() => app.getVersion()),
	hardware: publicProcedure.query(() => {
		const hardware = Preferences.data.hardware ?? null;
		return { hardware, recommendedFarClip: recommendFarClip(hardware) };
	}),
	redetectHardware: publicProcedure.mutation(async () => {
		const hardware = await detectHardware();
		Preferences.data = { hardware };
		return { hardware, recommendedFarClip: recommendFarClip(hardware) };
	}),
	quit: publicProcedure.mutation(() => app.quit()),
	minimize: publicProcedure.mutation(() => mainWindow?.minimize()),
	openLink: publicProcedure
		.input(z.string().url())
		.mutation(({ input }) => shell.openExternal(input)),
	openInstallFolder: publicProcedure.mutation(() => {
		const dir = Preferences.data.clientDir;
		if (dir) shell.openPath(dir);
	}),
	openLogFile: publicProcedure.mutation(() => {
		const file = Logger.transports.file.getFile().path;
		shell.openPath(file);
	}),
	filePicker: publicProcedure
		.input(
			z.object({
				title: z.string().optional(),
				message: z.string().optional(),
				filters: z
					.array(
						z.object({
							name: z.string(),
							extensions: z.array(z.string())
						})
					)
					.optional(),
				properties: z
					.array(
						z.enum([
							'openDirectory',
							'openFile',
							'multiSelections',
							'showHiddenFiles',
							'createDirectory',
							'promptToCreate',
							'noResolveAliases',
							'treatPackageAsDirectory',
							'dontAddToRecent'
						])
					)
					.optional()
			})
		)
		.mutation(async ({ input }) => {
			if (!mainWindow) return { canceled: true } as const;
			const { canceled, filePaths } = await dialog.showOpenDialog(
				mainWindow,
				input
			);

			return canceled
				? ({ canceled: true } as const)
				: ({
						canceled: false,
						path: filePaths as [string, ...string[]]
				  } as const);
		})
});
