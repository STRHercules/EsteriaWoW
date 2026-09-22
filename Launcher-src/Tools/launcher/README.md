# Esteria launcher build helper

`install.ps1` downloads a portable Node.js 20 runtime and runs the Electron
launcher build without changing the repository's global Node installation.

```powershell
Set-Location Launcher-src\Tools\launcher
.\install.ps1
```

The helper writes the packaged artifacts to the launcher root's `dist` or
`distprod` directory, depending on the active electron-builder configuration:

- `Esteria Launcher.exe` (portable); and
- `Esteria Launcher_Installer.exe` (NSIS).

The downloaded `node` directory is ignored by Git. Keep the client CDN source
and launcher-update artifacts outside this repository; see
`CDN-SETUP-WINDOWS10.md` for the Windows 10 CDN procedure.
