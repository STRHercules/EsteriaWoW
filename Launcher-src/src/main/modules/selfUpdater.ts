import { app } from 'electron';
import { autoUpdater } from 'electron-updater';
import Logger from 'electron-log/main';
import { is } from '@electron-toolkit/utils';

import Observable from './observable';

export type SelfUpdaterStatus =
	| { state: 'idle'; currentVersion: string }
	| { state: 'checking'; currentVersion: string }
	| { state: 'unavailable'; currentVersion: string }
	| { state: 'available'; currentVersion: string; nextVersion: string }
	| {
			state: 'downloading';
			currentVersion: string;
			nextVersion: string;
			progress: number;
	  }
	| { state: 'ready'; currentVersion: string; nextVersion: string }
	| { state: 'error'; currentVersion: string; message: string };

class SelfUpdaterClass extends Observable<SelfUpdaterStatus> {
	protected _value: SelfUpdaterStatus = {
		state: 'idle',
		currentVersion: app.getVersion()
	};

	#initialized = false;
	#nextVersion: string | undefined;

	get status(): SelfUpdaterStatus {
		return this._value;
	}

	private set status(v: SelfUpdaterStatus) {
		this._value = v;
		this._notifyObservers();
	}

	init() {
		if (this.#initialized) return;
		this.#initialized = true;

		if (is.dev) {
			Logger.info('[selfUpdater] dev mode, skipping');
			return;
		}

		const currentVersion = app.getVersion();

		autoUpdater.logger = Logger;
		autoUpdater.autoDownload = true;
		autoUpdater.autoInstallOnAppQuit = false;

		autoUpdater.on('checking-for-update', () => {
			Logger.info('[selfUpdater] checking');
			this.status = { state: 'checking', currentVersion };
		});
		autoUpdater.on('update-available', info => {
			Logger.info(`[selfUpdater] update available: ${info.version}`);
			this.#nextVersion = info.version;
			this.status = {
				state: 'available',
				currentVersion,
				nextVersion: info.version
			};
		});
		autoUpdater.on('update-not-available', info => {
			Logger.info(`[selfUpdater] up to date (current: ${info.version})`);
			this.status = { state: 'unavailable', currentVersion };
		});
		autoUpdater.on('error', err => {
			Logger.error('[selfUpdater] error', err);
			this.status = {
				state: 'error',
				currentVersion,
				message: err?.message ?? String(err)
			};
		});
		autoUpdater.on('download-progress', p => {
			Logger.info(`[selfUpdater] downloading ${Math.round(p.percent)}%`);
			this.status = {
				state: 'downloading',
				currentVersion,
				nextVersion: this.#nextVersion ?? '',
				progress: Math.max(0, Math.min(1, p.percent / 100))
			};
		});
		autoUpdater.on('update-downloaded', info => {
			Logger.info(
				`[selfUpdater] downloaded ${info.version}, awaiting user click`
			);
			this.status = {
				state: 'ready',
				currentVersion,
				nextVersion: info.version
			};
		});

		autoUpdater.checkForUpdates().catch(err => {
			Logger.error('[selfUpdater] checkForUpdates failed', err);
		});
	}

	triggerInstall() {
		if (this._value.state !== 'ready') {
			Logger.warn(
				`[selfUpdater] triggerInstall called in state ${this._value.state}, ignoring`
			);
			return;
		}
		Logger.info(
			'[selfUpdater] user clicked install, quitting + running installer'
		);
		autoUpdater.quitAndInstall(false, true);
	}
}

const SelfUpdater = new SelfUpdaterClass();
export default SelfUpdater;

export const initSelfUpdater = () => SelfUpdater.init();
