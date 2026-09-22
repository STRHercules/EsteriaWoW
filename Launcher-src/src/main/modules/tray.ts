import { Tray, Menu, nativeImage, app } from 'electron';
import Logger from 'electron-log/main';

import icon from '~build/icon.png?asset';

import { mainWindow } from '~main/index';

let tray: Tray | null = null;
let isMinimizedToTray = false;

const restoreWindow = () => {
	if (!mainWindow) return;
	mainWindow.show();
	if (mainWindow.isMinimized()) mainWindow.restore();
	mainWindow.focus();
	isMinimizedToTray = false;
};

const ensureTray = () => {
	if (tray) return tray;
	const trayIcon = nativeImage.createFromPath(icon).resize({ width: 16, height: 16 });
	tray = new Tray(trayIcon);
	tray.setToolTip('Esteria Launcher');
	tray.setContextMenu(
		Menu.buildFromTemplate([
			{ label: 'Show launcher', click: restoreWindow },
			{ type: 'separator' },
			{ label: 'Quit', click: () => app.quit() }
		])
	);
	tray.on('click', restoreWindow);
	return tray;
};

export const minimizeToTray = () => {
	if (!mainWindow) return;
	ensureTray();
	mainWindow.hide();
	isMinimizedToTray = true;
	Logger.info('Minimized to tray');
};

export const restoreFromTray = () => {
	if (!isMinimizedToTray) return;
	restoreWindow();
};

export const isInTray = () => isMinimizedToTray;

export const destroyTray = () => {
	tray?.destroy();
	tray = null;
};
