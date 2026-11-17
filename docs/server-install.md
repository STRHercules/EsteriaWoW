# Installing the Esteria server

Use the standalone `compose.server.yml`, not the upstream Compose defaults or a
developer's local override. It builds AuthServer, WorldServer and dbimport from
the same checkout and installs the custom SQL and server DBC snapshot. A client
is not needed to initialize the databases or start the server.

See [the validation report](server-install-validation.md) for executed checks and remaining limits.

## Requirements

- Docker Desktop with Linux AMD64 containers and Compose v2 on Windows, or Docker
  Engine and Compose v2 on Linux.
- Git with submodules initialized, an internet connection and enough Docker disk
space for the C++ build, caches, MySQL and extracted server data (allow at least 60 GB).
- A matching Esteria client for actual login and gameplay. A stock 3.3.5a client
  does not implement Esteria's additional races and packet formats.

## First installation

From the repository root in PowerShell:

```powershell
git submodule update --init --recursive
Set-Content -Encoding ascii .env.server ('ESTERIA_DB_PASSWORD=' + [guid]::NewGuid().ToString('N'))
docker compose --env-file .env.server -f compose.server.yml build db-import data-init
docker compose --env-file .env.server -f compose.server.yml up -d --no-build
docker compose --env-file .env.server -f compose.server.yml ps -a
```

On Linux, create `.env.server` with `ESTERIA_DB_PASSWORD=` followed by a private,
random password, then run the same Git and Docker commands. Keep this file; it is
ignored by Git. Replacing the password does not change an existing MySQL volume's
password. Do not run the `Set-Content` command again on an existing installation.

The initial source build is slow. Data initialization downloads the pinned 1.2 GB
upstream v20 terrain archive, verifies its SHA-256, extracts it and overlays the
repository's Esteria DBCs. MySQL is private to the Compose network. Only auth and
world ports are published. No existing `ac-database` or `ac-worldserver` container
is reused, and no developer bind mounts are required.

If ports are already occupied, add `ESTERIA_AUTH_PORT=3725` and
`ESTERIA_WORLD_PORT=8086` to `.env.server`. Set `realmlist.port` to the chosen world
port as described below. Use `-p another-name` consistently with every Compose
command if you want more than one independent installation.

## Check installation

```powershell
docker compose --env-file .env.server -f compose.server.yml logs --tail 100 data-init db-import
docker compose --env-file .env.server -f compose.server.yml logs --tail 100 worldserver authserver
```

`data-init` and `db-import` must exit successfully. WorldServer must reach its
`(worldserver-daemon) ready...` message. An importer exit code alone does not prove
that WorldServer initialized. Do not bypass an import failure or create empty
placeholder tables. Include the first failing migration and its error in a bug
report.

The importer applies stock updates, module foundations, then module updates and
core pending migrations. This includes Nemesis, exact-race startup tables,
Retail Look/Body Shape, the Incarnations catalogue and ordered Housing SQL.
Playerbots' separate database bootstraps in WorldServer, whose image includes
the module SQL. Random bot autologin is off in this installation profile; enable
it later after checking your machine's capacity.
The first world startup also creates Playerbots' account/character pool, which
can take several minutes even while random bot autologin is off.

## Realm address and administrator

The initial realm address is loopback. To edit it without placing the database
password on the command line, open a shell in the database container:

```powershell
docker compose --env-file .env.server -f compose.server.yml exec database sh
```

Inside that shell:

```sh
MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot acore_auth
```

At the MySQL prompt, set your reachable address and published world port:

```sql
UPDATE realmlist SET name = 'Esteria', address = '127.0.0.1', port = 8085 WHERE id = 1;
```

Use `quit`, then `exit`. Remote players need the reachable server address,
forwarded auth/world ports, and matching client realm settings. MySQL needs no
public port. A module's legacy public-address migration runs only through the
tracked updater; it is not a source of installation-specific configuration.

Attach to WorldServer's console (use `ps` to find its container name):

```powershell
docker attach esteria-worldserver-1
```

Create your account at the server console:

```text
account create <username> <password>
account set gmlevel <username> 3 -1
```

Detach using Ctrl+P, Ctrl+Q. Ctrl+C stops the server.

## Features and optional data

The baseline compiles the repository modules except **Manastorm Endless** and
the superseded **Attunement Plus** module (its implementation is in `mod-custom-server`).
Classless Wildcard, Playerbots and custom race support remain available. Their
client-facing features still require the matching client.

The recovered CoA/Ascension item prerequisites are supplied in
[`data/server/manastorm`](../data/server/manastorm/README.md), with checksums and
an unpacking tool. The complete SQL installation and compiled native-mode backend
startup have passed in isolation. Manastorm remains opt-in while client/gameplay
acceptance is pending. For a separate fresh installation, add
`ESTERIA_DISABLED_MODULES=mod-attunement-plus` to its `.env.server` before building.
Use a different Compose project name and a new database; the dataset updates
selected shared item definitions. The image verifies and installs its item SQL
and native Manastorm DBC automatically. Character persistence, endgame scaling
and private route spawn dependencies are included in the module migrations.

Housing's schema and catalogue install automatically, but
`EsteriaHousing.Enable` defaults to 0. Housing and Garrison need the matching
client maps/models/UI; Garrison also needs its existing module SQL applied.
Their presence in the source tree is not a claim that the pinned stock terrain
package contains their maps or server geometry.
The [asset audit](server-install-asset-gaps.md) distinguishes required client
resources, existing repo SQL and missing server geometry. Fixed-Z prototypes can
tolerate absent server terrain, with height, collision and pathfinding limits;
this is not full geometry/gameplay acceptance.

Never substitute a random DBC collection. The server uses the published binary
DBCs, WXL continuations and SQL overrides. The installer checks every published DBC hash and all
navigation tile versions. To check an installed volume again:

```powershell
docker compose --env-file .env.server -f compose.server.yml run --rm data-init
```

For an offline terrain download, `prepare_data.py` also accepts `--base-archive`
pointing to the exact official v20.0 `Data.zip`; the same checksum is required.

## Updating and stopping

Back up the database volume before updating. Do not point this fresh-install
profile at another realm's database or data volume.

```powershell
docker compose --env-file .env.server -f compose.server.yml stop worldserver authserver
docker compose --env-file .env.server -f compose.server.yml build db-import data-init
docker compose --env-file .env.server -f compose.server.yml run --rm db-import
docker compose --env-file .env.server -f compose.server.yml up -d --no-build
```

Stop here if the importer fails. `docker compose ... down` preserves named
volumes. Adding `-v` destroys them, including accounts and characters.
Server-data volumes are versioned by snapshot in Compose. A release that updates
the data snapshot uses a new data volume while retaining your database volume.

The Housing migrations are generated from their owning module SQL. After editing
that source, run `python tools/server_install/sync_housing_sql.py` and review the
result. Offline installer checks run with
`python tools/server_install/test_install.py`.
