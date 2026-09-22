import os from 'node:os';
import { spawn } from 'node:child_process';

import Logger from 'electron-log/main';

const SCRIPT = [
	'$ErrorActionPreference = "Stop"',
	"Add-Type -TypeDefinition @'",
	'using System;',
	'using System.Runtime.InteropServices;',
	'public static class VmmfDisplays {',
	'  [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Ansi)]',
	'  public struct DISPLAY_DEVICE {',
	'    public int cb;',
	'    [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string DeviceName;',
	'    [MarshalAs(UnmanagedType.ByValTStr, SizeConst=128)] public string DeviceString;',
	'    public int StateFlags;',
	'    [MarshalAs(UnmanagedType.ByValTStr, SizeConst=128)] public string DeviceID;',
	'    [MarshalAs(UnmanagedType.ByValTStr, SizeConst=128)] public string DeviceKey;',
	'  }',
	'  [DllImport("user32.dll", EntryPoint="EnumDisplayDevicesA", CharSet=CharSet.Ansi)]',
	'  public static extern bool EnumDisplayDevices(string lpDevice, uint iDevNum, ref DISPLAY_DEVICE lpDisplayDevice, uint dwFlags);',
	'}',
	"'@",
	'$dd = New-Object VmmfDisplays+DISPLAY_DEVICE',
	'$dd.cb = [System.Runtime.InteropServices.Marshal]::SizeOf($dd)',
	'for ($i = 0; [VmmfDisplays]::EnumDisplayDevices([NullString]::Value, $i, [ref]$dd, 0); $i++) {',
	'  if ($dd.StateFlags -band 4) { Write-Output $i; exit 0 }',
	'}',
	'exit 1'
].join('\n');

export const detectPrimaryDisplayIndex = (): Promise<number> => {
	if (os.platform() !== 'win32') return Promise.resolve(0);

	const encoded = Buffer.from(SCRIPT, 'utf16le').toString('base64');

	return new Promise(resolve => {
		let settled = false;
		const finish = (index: number) => {
			if (settled) return;
			settled = true;
			clearTimeout(timer);
			resolve(index);
		};

		const child = spawn(
			'powershell.exe',
			['-NoProfile', '-NonInteractive', '-EncodedCommand', encoded],
			{ windowsHide: true }
		);

		const timer = setTimeout(() => {
			child.kill();
			Logger.warn('Primary display detection timed out');
			finish(0);
		}, 8000);

		let stdout = '';
		child.stdout.on('data', d => (stdout += String(d)));
		child.on('error', e => {
			Logger.warn('Primary display detection failed to launch PowerShell', e);
			finish(0);
		});
		child.on('exit', code => {
			const index = Number(stdout.trim());
			if (code === 0 && Number.isInteger(index) && index >= 0) {
				Logger.info(`Detected primary display at device index ${index}`);
				finish(index);
			} else {
				Logger.warn('Primary display detection failed, defaulting to 0');
				finish(0);
			}
		});
	});
};
