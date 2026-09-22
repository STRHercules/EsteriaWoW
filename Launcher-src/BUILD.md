# Esteria Launcher build guide (Windows)

This guide builds the Esteria launcher for the WotLK 3.3.5a client (build
12340). It covers the Electron application only. For the local client CDN,
follow [`CDN-SETUP-WINDOWS10.md`](CDN-SETUP-WINDOWS10.md).

## Prerequisites

- Windows 10 x64;
- Node.js 20 LTS for the current Electron/native dependency graph;
- Visual Studio 2022 Build Tools with the C++ workload and Windows SDK; and
- Python 3 for `node-gyp`.

The server-only CDN setup uses Node.js 22 LTS and does not require the native
Electron dependencies.

Install Node.js 20 with `fnm`, or use the repository helper:

```powershell
winget install Schniz.fnm --accept-source-agreements --accept-package-agreements
fnm install 20
fnm default 20
node --version
npm --version
```

Install the C++ toolchain if it is not already present:

```powershell
winget install Microsoft.VisualStudio.2022.BuildTools `
  --accept-source-agreements --accept-package-agreements `
  --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.Windows11SDK.22621 --includeRecommended"
```

## Install dependencies

From `Launcher-src`:

```powershell
npm install
```

The postinstall step prepares the Electron native dependencies. If the
environment is controlled by an IDE and contains `ELECTRON_RUN_AS_NODE`,
remove it before launching Electron:

```powershell
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
```

The helper performs the same setup with a portable Node.js runtime:

```powershell
.\Tools\launcher\install.ps1
```

## Development

For the local CDN in another terminal, see the Windows CDN guide. Then from
`Launcher-src`:

```powershell
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
npm run dev
```

The default development configuration targets `http://127.0.0.1:7384` and
the `live` channel. Use a `.env` file to point at a different operator-owned
CDN/API origin.

## Distribution build

Before a player release, set the real CDN values in the build environment and
point the launcher update URL at the `/launcher-updates/` path on that same
CDN origin:

```powershell
$env:MAIN_VITE_SERVER_URL = 'https://cdn.example.invalid'
$env:MAIN_VITE_CLIENT_VERSION = 'live'
$env:MAIN_VITE_REALM_LIST = 'realmlist.example.invalid'
$env:MAIN_VITE_PATCH_LIST = 'patch.example.invalid'
$env:MAIN_VITE_REALM_NAME = 'Esteria'
$env:ESTERIA_LAUNCHER_UPDATE_URL = 'https://cdn.example.invalid/launcher-updates/'
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
npm run dist
```

The example hostnames above are placeholders. Replace them with reachable
Esteria origins before packaging. The output directory is `distprod`:

- `Esteria Launcher.exe` - portable build;
- `Esteria Launcher_Installer.exe` - NSIS installer.

Upload the launcher artifacts and generated `latest.yml` metadata to the
configured `LAUNCHER_UPDATES_DIR`. Keep that directory separate from the client
tree even though both are served by the same CDN listener.

## Release checks

Before distributing a build, verify that:

- the CDN manifest contains `WoW.exe`, `Data`, `Interface`, extensions, and
  the intended addons;
- `/health`, `/api/build-status`, the manifest endpoint, and a representative
  file endpoint respond from the player network;
- the launcher update URL serves the matching electron-builder metadata; and
- no client source, credentials, account data, logs, WDB files, or screenshots
  have been added to Git.

The launcher delivers the supplied executable as a normal manifest file and
launches it directly. It does not binary-patch `WoW.exe`.
