import os from 'node:os';
import { spawn } from 'node:child_process';

import { app } from 'electron';
import Logger from 'electron-log/main';

import type { HardwareInfo } from '~common/schemas';

export const HARDWARE_SCHEMA_VERSION = 1;

export const FARCLIP_FLOOR = 777;
export const FARCLIP_CEILING = 3000;

const VIDEO_CLASS_GUID = '{4d36e968-e325-11ce-bfc1-08002be10318}';

const getVramMb = (): Promise<{
	mb: number | null;
	source: HardwareInfo['vramSource'];
}> => {
	if (os.platform() !== 'win32')
		return Promise.resolve({ mb: null, source: 'none' });

	const script = [
		'$ErrorActionPreference = "Stop"',
		`$base = 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Class\\${VIDEO_CLASS_GUID}'`,
		'$max = [int64]0',
		'Get-ChildItem $base -ErrorAction SilentlyContinue | ForEach-Object {',
		'  $p = Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue',
		'  $v = [int64]0',
		"  if ($p.'HardwareInformation.qwMemorySize') { $v = [int64]$p.'HardwareInformation.qwMemorySize' }",
		"  elseif ($p.'HardwareInformation.MemorySize') {",
		"    $m = $p.'HardwareInformation.MemorySize'",
		'    if ($m -is [byte[]]) { $v = [int64][System.BitConverter]::ToUInt32($m, 0) } else { $v = [int64]$m }',
		'  }',
		'  if ($v -gt $max) { $max = $v }',
		'}',
		'Write-Output $max'
	].join('\n');
	const encoded = Buffer.from(script, 'utf16le').toString('base64');

	return new Promise(resolve => {
		let settled = false;
		const finish = (mb: number | null, source: HardwareInfo['vramSource']) => {
			if (settled) return;
			settled = true;
			clearTimeout(timer);
			resolve({ mb, source });
		};

		const child = spawn(
			'powershell.exe',
			['-NoProfile', '-NonInteractive', '-EncodedCommand', encoded],
			{ windowsHide: true }
		);

		const timer = setTimeout(() => {
			child.kill();
			Logger.warn('VRAM detection timed out');
			finish(null, 'none');
		}, 8000);

		let stdout = '';
		child.stdout.on('data', d => (stdout += String(d)));
		child.on('error', e => {
			Logger.warn('VRAM detection failed to launch PowerShell', e);
			finish(null, 'none');
		});
		child.on('exit', code => {
			const bytes = Number(stdout.trim());
			if (code === 0 && Number.isFinite(bytes) && bytes > 0)
				finish(Math.round(bytes / 1024 / 1024), 'registry');
			else finish(null, 'none');
		});
	});
};

const getGpuModel = async (): Promise<string> => {
	try {
		const info = (await app.getGPUInfo('complete')) as {
			auxAttributes?: { glRenderer?: string };
			gpuDevice?: { active?: boolean; vendorId?: number; deviceId?: number }[];
		};
		const renderer = info?.auxAttributes?.glRenderer?.trim();
		if (renderer) return renderer;
		const active = info?.gpuDevice?.find(d => d.active) ?? info?.gpuDevice?.[0];
		if (active) return `vendor ${active.vendorId} device ${active.deviceId}`;
	} catch (e) {
		Logger.warn('GPU info detection failed', e);
	}
	return 'unknown';
};

export const detectHardware = async (): Promise<HardwareInfo> => {
	const cpus = os.cpus();
	const [vram, gpuModel] = await Promise.all([getVramMb(), getGpuModel()]);

	const info: HardwareInfo = {
		totalRamMb: Math.round(os.totalmem() / 1024 / 1024),
		cpuCores: cpus.length,
		cpuModel: cpus[0]?.model?.trim() || 'unknown',
		gpuModel,
		vramMb: vram.mb,
		vramSource: vram.source,
		detectedAt: new Date().toISOString(),
		schemaVersion: HARDWARE_SCHEMA_VERSION
	};
	Logger.info('Detected hardware', info);
	return info;
};

const clampFarClip = (n: number) =>
	Math.min(FARCLIP_CEILING, Math.max(FARCLIP_FLOOR, Math.round(n)));

export const recommendFarClip = (hw: HardwareInfo | null): number => {
	if (!hw) return clampFarClip(1000);

	const ramGb = hw.totalRamMb / 1024;
	const cores = hw.cpuCores;
	const vramTrusted = hw.vramSource !== 'none' && hw.vramMb != null;
	const vramGb = vramTrusted ? (hw.vramMb as number) / 1024 : null;

	if (ramGb < 6 || cores <= 2) return clampFarClip(FARCLIP_FLOOR);

	if (vramGb === null)
		return clampFarClip(ramGb >= 8 && cores >= 4 ? 1500 : 1000);

	if (ramGb < 8 || vramGb < 2) return clampFarClip(1000);
	if (ramGb >= 32 && vramGb >= 8 && cores >= 8) return clampFarClip(3000);
	if (ramGb >= 16 && vramGb >= 4 && cores >= 6) return clampFarClip(2200);
	if (ramGb >= 8 && vramGb >= 2 && cores >= 4) return clampFarClip(1500);
	return clampFarClip(1000);
};
