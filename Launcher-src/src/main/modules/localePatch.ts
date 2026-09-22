import path from 'node:path';

import fs from 'fs-extra';
import {
	SFileOpenArchive,
	SFileCloseArchive,
	SFileHasFile
} from 'stormlib-node';
import { STREAM_FLAG } from 'stormlib-node/dist/enums';
import Logger from 'electron-log/main';

import Preferences from './preferences';

const PREFERRED = 'L';
const LETTERS = 'BCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
const MARKER = 'esteria-locale.marker';

const patchFile = (dataDir: string, letter: string) =>
	path.join(dataDir, `patch-${letter}.mpq`);

const prebuiltFor = (dataDir: string, locale: string) =>
	path.join(dataDir, locale, 'patch-L.mpq');

const isOurPatch = (mpqPath: string): boolean => {
	if (!fs.existsSync(mpqPath)) return false;
	try {
		const h = SFileOpenArchive(mpqPath, STREAM_FLAG.READ_ONLY);
		try {
			return SFileHasFile(h, MARKER);
		} finally {
			SFileCloseArchive(h);
		}
	} catch {
		return false;
	}
};

const usableSlot = (dataDir: string, letter: string): boolean => {
	if (fs.existsSync(path.join(dataDir, `patch-${letter}.MPQ`))) return false;
	const f = patchFile(dataDir, letter);
	return !fs.existsSync(f) || isOurPatch(f);
};

const removeOurPatch = async (dataDir: string) => {
	for (const l of LETTERS) {
		const f = patchFile(dataDir, l);
		if (isOurPatch(f)) await fs.remove(f).catch(() => {});
	}
	if (Preferences.data.localePatchLetter || Preferences.data.localePatchLocale)
		Preferences.data = {
			localePatchLetter: undefined,
			localePatchLocale: undefined
		};
};

export const applyLocalePatch = async (
	clientDir: string | undefined,
	locale: string | undefined
): Promise<void> => {
	if (!clientDir) return;
	const dataDir = path.join(clientDir, 'Data');

	const nextLocale = !locale || locale === 'enUS' ? undefined : locale;
	if (Preferences.data.localePatchLocale !== nextLocale)
		await fs.remove(path.join(clientDir, 'WDB')).catch(() => {});

	if (!locale || locale === 'enUS') {
		await removeOurPatch(dataDir);
		return;
	}

	const source = prebuiltFor(dataDir, locale);
	if (!(await fs.pathExists(source))) {
		Logger.warn(
			`Locale patch: no prebuilt patch-L for ${locale}; leaving UI as-is`
		);
		return;
	}

	const tracked = Preferences.data.localePatchLetter;
	const letter =
		(tracked && usableSlot(dataDir, tracked) ? tracked : undefined) ??
		(usableSlot(dataDir, PREFERRED)
			? PREFERRED
			: LETTERS.find(l => usableSlot(dataDir, l)));
	if (!letter) {
		Logger.warn('Locale patch: no usable patch slot');
		return;
	}
	const target = patchFile(dataDir, letter);

	try {
		if (
			Preferences.data.localePatchLocale === locale &&
			isOurPatch(target) &&
			fs.statSync(target).mtimeMs >= fs.statSync(source).mtimeMs
		)
			return;
	} catch {
	}

	try {
		for (const l of LETTERS) {
			if (l === letter) continue;
			const f = patchFile(dataDir, l);
			if (isOurPatch(f)) await fs.remove(f).catch(() => {});
		}
		await fs.copy(source, target, { overwrite: true });
		Preferences.data = { localePatchLetter: letter, localePatchLocale: locale };
		Logger.log(
			`Locale patch: swapped prebuilt ${locale} -> patch-${letter}.mpq`
		);
	} catch (e) {
		Logger.error('Locale patch: failed to swap in prebuilt patch', e);
	}
};
