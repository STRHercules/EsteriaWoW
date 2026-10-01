# Esteria CDN setup on Windows 10

This procedure runs the launcher manifest/file service on a Windows 10
machine. It uses Node.js 22 LTS and stages the complete Esteria WotLK 3.3.5a
build 12340 client outside the Git checkout.

The service is an HTTP origin for development or a private LAN. Remote public
players need a reachable DNS name or public IP, HTTPS, and a reverse proxy
such as Caddy or IIS. Replace every example hostname with an operator-owned
Esteria hostname; this guide does not invent one.

## 1. Install Node.js 22 LTS

Install the x64 Node.js 22 LTS installer from nodejs.org, or use WinGet in an
elevated PowerShell window:

~~~powershell
winget install OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
~~~

Open a new PowerShell window and confirm both tools:

~~~powershell
node --version
npm --version
~~~

The first command should report a Node.js 22.x LTS version. If Windows still
reports an older version, close and reopen PowerShell so PATH is refreshed.

## 2. Create an external staging layout

Keep the client payload and generated manifests outside Git. A simple layout
is:

~~~powershell
New-Item -ItemType Directory -Force -Path C:\Esteria\CDN\client\live, C:\Esteria\CDN\launcher-updates, C:\Esteria\CDN\backups | Out-Null
~~~

The important source directory is:

    C:\Esteria\CDN\client\live

It must be a sanitized, validated release tree containing the complete client:
WoW.exe, Data, Interface, Extensions, addons, and all other managed root
files. Do not use a player's live profile as the release source.

## 3. Copy the complete client

Export or validate the client in a separate directory, then copy it into the
external live staging directory. This example intentionally omits generated
and player-owned state:

~~~powershell
$source = 'D:\Validated\Esteria-WotLK-3.3.5a-12340'
$client = 'C:\Esteria\CDN\client\live'
robocopy $source $client /E /COPY:DAT /DCOPY:DAT /R:2 /W:2 /XF manifest.json manifest.json.tmp /XD "$source\Errors" "$source\Logs" "$source\Screenshots" "$source\WDB" "$source\WTF\Account"
if ($LASTEXITCODE -gt 7) { throw "robocopy failed with exit code $LASTEXITCODE" }
~~~

Do not use /MIR against a directory that contains player data. Confirm that
the staged root contains WoW.exe and the expected Data and Interface trees:

~~~powershell
Test-Path C:\Esteria\CDN\client\live\WoW.exe
Get-ChildItem C:\Esteria\CDN\client\live\Data
Get-ChildItem C:\Esteria\CDN\client\live\Interface
~~~

The source tree, credentials, account WTF data, logs, WDB files, screenshots,
and other player data must stay outside Git and outside any public repository.

### Bundle-delivered patch directories

Two large extracted patch directories are delivered as single ZIP archives to
avoid thousands of individual HTTP requests:

```text
Data\Patch-Housing.MPQ\
Data\Patch-Housing.MPQ.zip
Data\patch-K.mpq\
Data\patch-K.mpq.zip
```

Keep both the expanded directory and its matching ZIP in the staged client.
The expanded directory is the authoritative installed layout and is used to
build the file manifest. The ZIP is only the transport artifact. It is omitted
from the normal installed-file tree and recorded as delivery metadata on the
directory entry. Older launchers can ignore that metadata and still fall back
to per-file delivery, while current launchers use the ZIP bundle.

The ZIP may contain either the directory contents directly or one top-level
directory with the matching name. Archives larger than 4 GiB must use ZIP64.
The launcher downloads the ZIP with normal `.part` resume support, verifies
the archive hash, extracts to a temporary folder, verifies the extracted files
against the manifest, swaps the completed directory into place, and removes
the downloaded ZIP. Players therefore end up with only the normal extracted
folders under `Data`.

Whenever either expanded directory changes, rebuild its matching ZIP before
regenerating `manifest.json`. A stale or mismatched ZIP will be rejected by
the launcher instead of replacing the player's working directory.

## 4. Install and start the CDN service

The server has no dotenv dependency, so set SOURCE_DIR in the PowerShell
session that starts it. From the Esteria launcher checkout:

~~~powershell
Set-Location R:\Users\Zach\Documents\GitHub\EsteriaWoW\Launcher-src\server
npm install
$env:SOURCE_DIR = 'C:\Esteria\CDN\client\live'
$env:LAUNCHER_UPDATES_DIR = 'C:\Esteria\CDN\launcher-updates'
npm run dev
~~~

Leave this terminal running. The service listens on TCP port 7384 and serves
both the client CDN and `/launcher-updates/`. It pre-builds
client\manifest.json. A complete client can take time to hash.
The generated manifest is beside the source tree and is not committed to
Launcher-src.

## 5. Check the endpoints

Use a second PowerShell window:

~~~powershell
$base = 'http://127.0.0.1:7384'
Invoke-RestMethod "$base/health"
Invoke-RestMethod "$base/api/build-status" | ConvertTo-Json
~~~

Health should return:

    { "ok": true }

The manifest endpoint is:

~~~powershell
Invoke-WebRequest "$base/api/file/live/manifest.json" -UseBasicParsing
~~~

During the first build it can return HTTP 503 with
manifest_building. Poll build progress, then retry:

~~~powershell
do {
  $status = Invoke-RestMethod "$base/api/build-status"
  $status | ConvertTo-Json -Compress
  if ($status.state -eq 'building') { Start-Sleep -Seconds 5 }
} while ($status.state -eq 'building')
Invoke-WebRequest "$base/api/file/live/manifest.json" -UseBasicParsing
~~~

Check a small managed file through the versioned file route. Replace the
example path if the validated client uses a different small file:

~~~powershell
Invoke-WebRequest "$base/client/live/Interface/FrameXML/UIParent.lua" -Method Head -UseBasicParsing
~~~

Check the launcher update metadata from the same listener:

~~~powershell
Invoke-WebRequest "$base/launcher-updates/latest.yml" -UseBasicParsing
~~~

The launcher consumes these routes:

- /api/file/live/manifest.json
- /client/live/<relative-file-path>
- /launcher-updates/<release-file>

The route rejects paths that escape the staged source directory.

## 6. Allow LAN access in Windows Defender Firewall only when needed

For a private LAN test, run PowerShell as Administrator and open TCP 7384 on
the Private profile only:

~~~powershell
New-NetFirewallRule -DisplayName 'Esteria CDN TCP 7384' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 7384 -Profile Private
~~~

Do not create this rule for a local-only launcher. If it is no longer needed,
remove the exact rule:

~~~powershell
Remove-NetFirewallRule -DisplayName 'Esteria CDN TCP 7384'
~~~

## 7. Public player access

Players outside the LAN need all of the following:

1. a DNS name or public IP that resolves to the server;
2. router/NAT forwarding for the reverse-proxy HTTPS port;
3. a valid TLS certificate; and
4. a reverse proxy forwarding HTTPS to 127.0.0.1:7384.

Caddy and IIS are both suitable. For example, a Caddy site block can reverse
proxy an operator-owned name:

~~~text
cdn.example.invalid {
    reverse_proxy 127.0.0.1:7384
}
~~~

Build the launcher with that public HTTPS origin in
MAIN_VITE_SERVER_URL. Do not expose the raw Node port as the long-term public
API, and do not put credentials or account files under the source directory.

## 8. Host launcher self-update artifacts on the same CDN service

Launcher self-update files are not client files. Keep them in the separate
launcher-updates directory served by the same port 7384 listener:

    C:\Esteria\CDN\launcher-updates

Before packaging a local launcher release, set the update URL to the same
listener:

~~~powershell
Set-Location R:\Users\Zach\Documents\GitHub\EsteriaWoW\Launcher-src
$env:ESTERIA_LAUNCHER_UPDATE_URL = 'http://127.0.0.1:7384/launcher-updates/'
npm run dist
~~~

Upload the generated portable/NSIS artifacts and electron-builder metadata
such as latest.yml to `C:\Esteria\CDN\launcher-updates`. For public HTTPS,
replace the local URL with the public CDN origin and keep the
`/launcher-updates/` path.

## 9. Release and rollback procedure

For every client release:

1. prepare a clean validated source export;
2. back up the current manifest;
3. copy the new client into client\live without player-owned state;
4. remove the old manifest so the service creates a new one;
5. start or restart the service and wait for build-status to report ready;
6. check health, manifest, and a representative file endpoint; and
7. verify a clean destination with the launcher before announcing the release.

Back up and regenerate the manifest from PowerShell:

~~~powershell
$manifest = 'C:\Esteria\CDN\client\live\manifest.json'
$stamp = Get-Date -Format yyyyMMdd-HHmmss
Copy-Item $manifest "C:\Esteria\CDN\backups\manifest-live-$stamp.json"
Remove-Item $manifest
~~~

Restarting the service is the simplest deterministic regeneration path. Keep
the backup until the new client has passed a clean-install and update test;
restoring the backup and restarting provides a quick rollback.

## Data boundary

The client source, generated MPQs, manifest backups, logs, WDB files,
screenshots, account WTF data, credentials, and player addon state stay
outside Git. Only launcher source, configuration examples, and this operating
guide belong in Launcher-src.
