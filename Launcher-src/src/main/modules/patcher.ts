import path from 'path';

import { screen } from 'electron';
import fs from 'fs-extra';
import Logger from 'electron-log/main';

import { EsteriaConfig } from '~common/config';
import { isNotUndef } from '~common/utils';
import Preferences from '~main/modules/preferences';

export const patchConfig = async () => {
	const { clientDir, locale } = Preferences.data;
	if (!clientDir) return;

	const configPath = path.join(clientDir, 'WTF', 'Config.wtf');
	await fs.ensureDir(path.dirname(configPath));
	const raw = (await fs.pathExists(configPath))
		? await fs.readFile(configPath, { encoding: 'utf-8' })
		: '';

	const configWtf = Object.fromEntries(
		raw
			.split(/\r?\n/)
			.map(l => {
				const [, k, v] = l.match(/SET (\w+) "(.*)"/) ?? [];
				return !k || v === undefined ? undefined : [k, v];
			})
			.filter(isNotUndef)
	);

	const primaryDisplay = screen.getPrimaryDisplay();
	const scale = primaryDisplay.scaleFactor || 1;
	const width = Math.round(primaryDisplay.bounds.width * scale);
	const height = Math.round(primaryDisplay.bounds.height * scale);

	const parsed = {
		...configWtf,
		scriptMemory: 512000,
		gxResolution: `${width}x${height}`,
		gxColorBits: primaryDisplay.colorDepth,
		gxDepthBits: primaryDisplay.colorDepth,
		gxRefresh: 60,
		gxMultisample: 8,
		gxMultisampleQuality: 0,
		gxTripleBuffer: 1,
		anisotropic: 16,
		frillDensity: 48,
		fullAlpha: 1,
		SmallCull: 0.01,
		DistCull: 888.8,
		shadowLevel: 0,
		trilinear: 1,
		specular: 1,
		pixelShaders: 1,
		M2UsePixelShaders: 1,
		particleDensity: 1,
		unitDrawDist: 300,
		weatherDensity: 3,
		movieSubtitle: 1,
		minimapZoom: 0,
		minimapInsideZoom: 0,
		SoundZoneMusicNoDelay: 1,
		patchList: EsteriaConfig.patchList,
		realmName: EsteriaConfig.realmName,
		gxWindow: configWtf['gxWindow'] ?? 1,
		gxMaximize: configWtf['gxMaximize'] ?? 1,
		gxCursor: configWtf['gxCursor'] ?? 1,
		checkAddonVersion: configWtf['checkAddonVersion'] ?? 0,
		farClip: configWtf['farClip'] ?? 777,
		CameraDistanceMax: configWtf['CameraDistanceMax'] ?? 50,
		locale,
		realmList: EsteriaConfig.realmList,
		hwDetect: 0,
		M2UseShaders: 1
	};

	const body = Object.entries(parsed)
		.filter(v => v[1] !== undefined && v[1] !== null)
		.map(l => `SET ${l[0]} "${l[1]}"`)
		.join('\n');
	const tmpPath = `${configPath}.tmp`;
	await fs.writeFile(tmpPath, body);
	await fs.move(tmpPath, configPath, { overwrite: true });
	Logger.log('Config.wtf successfully patched');
};
