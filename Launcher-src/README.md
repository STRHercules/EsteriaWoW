# Esteria Launcher

Desktop launcher for the Esteria World of Warcraft: Wrath of the Lich King
3.3.5a client (build 12340). It is built with Electron, React, and tRPC.

The launcher:

- downloads a complete staged client through a versioned manifest CDN;
- verifies and updates changed files in the `live` client channel;
- writes `WTF/Config.wtf` with the configured Esteria realm values;
- starts the supplied `WoW.exe` directly; it never rewrites executable bytes;
- optionally manages addons from explicitly configured Git sources; and
- self-updates from the `/launcher-updates/` path on the configured CDN origin.

## Player quick start

1. Download `Esteria Launcher.exe` or `Esteria Launcher_Installer.exe` from
   the release page.
2. Run it and select the directory where the client should live.
3. Click **Verify** or **Update**. A clean directory receives `WoW.exe`,
   `Data`, `Interface`, extensions, addons, and the other managed client files.
4. Click **Play**.

The launcher does not require a separately downloaded base client when the
configured CDN has a complete `live` tree. Player-generated state such as
logs, WDB files, screenshots, account WTF data, and credentials is not part of
the managed source tree.

## Build-time configuration

Copy `.env.example` to `.env` for local development. The values are embedded
at build time:

| Variable | Purpose |
|---|---|
| `MAIN_VITE_SERVER_URL` | Esteria CDN/API origin |
| `MAIN_VITE_CLIENT_VERSION` | Client channel, normally `live` |
| `MAIN_VITE_REALM_LIST` | Realm-list address written to `Config.wtf` |
| `MAIN_VITE_PATCH_LIST` | Patch-list address written to `Config.wtf` |
| `MAIN_VITE_REALM_NAME` | Realm display name |
| `MAIN_VITE_NEWS_URL` | Optional news JSON endpoint; blank disables news feed requests |
| `MAIN_VITE_FORUM_URL` | Optional forum announcement endpoint; blank disables forum requests |

The committed examples use loopback for local testing. Set the actual
reachable Esteria HTTPS origin before producing a player build; no public
hostname or IP is assumed by this repository.

## Build the launcher

For Windows prerequisites and the native dependency notes, see
[`BUILD.md`](BUILD.md). The operator-facing CDN procedure is in
[`CDN-SETUP-WINDOWS10.md`](CDN-SETUP-WINDOWS10.md).

```powershell
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
npm install
npm run dist
```

Artifacts are written to `distprod` by the current electron-builder config:

- `Esteria Launcher.exe` - portable build;
- `Esteria Launcher_Installer.exe` - NSIS installer.

Set `ESTERIA_LAUNCHER_UPDATE_URL` to
`http://127.0.0.1:7384/launcher-updates/` for a local release that should
self-update. The client files and launcher updates use separate directories on
the same CDN listener.

## Run the local CDN service

The standalone Express service in `server/` is not bundled into the Electron
application. It serves the staged client, its manifest, and launcher updates:

```powershell
Set-Location server
npm install
$env:SOURCE_DIR = 'C:\Esteria\CDN\client\live'
$env:LAUNCHER_UPDATES_DIR = 'C:\Esteria\CDN\launcher-updates'
npm run dev
```

Endpoints:

- `GET /health`
- `GET /api/build-status`
- `GET /api/file/live/manifest.json`
- `GET /client/live/<relative-file-path>`
- `GET /launcher-updates/<release-file>`
- `GET /api/addons.json`

The first manifest build can take time for a complete client. Poll
`/api/build-status` while it is building. See
[`CDN-SETUP-WINDOWS10.md`](CDN-SETUP-WINDOWS10.md) for firewall, HTTPS, public
access, release, and rollback instructions.

## Repository boundary

Keep the validated client, generated MPQs, manifest backups, logs, WDB files,
screenshots, account WTF data, credentials, and other player data outside
this Git checkout. Only the launcher source and operator documentation belong
here.

## License

MIT. The upstream license attribution is preserved in [`LICENSE`](LICENSE).
