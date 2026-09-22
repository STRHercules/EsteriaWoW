import type path from 'path';

import { type ElectronAPI } from '@electron-toolkit/preload';

declare global {
	interface Window {
		electron: ElectronAPI;
		path: typeof path;
	}
}
