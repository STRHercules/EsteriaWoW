# Darkfallen Reboot Handoff

**Prepared:** 2026-09-20 (America/Chicago)

## Current state

The source and client package are prepared, but the server deployment is **not complete**.

- Active client package is already installed and verified in:
  - `G:\3.3.5a - Dev\Data\patch-Z.MPQ`
  - `G:\3.3.5a - Dev\Data\enUS\patch-enUS-Z.MPQ`
- The current archive SHA-256 values match the staged backup pair under `env/dist/data-backups/20260920-darkfallen-stage-v2/`:
  - Root: `d695417e2de5a8e56f30f257af5059e6f45f0041b5252f9dd2942644e94fc109`
  - Locale: `6ab9f68a9dac4b197ee0c818e48d10b87b3a74f9c27c3a2ab24311c4f13042ea`
- StormLib readback confirmed root WDBC rows `43`/`44`, model IDs `3658`/`3659`, display IDs `60028`/`60029`, Darkfallen models/portraits/root Glue, and locale `GlueStrings.lua`.
- `acore_world` had no Darkfallen rows before deployment: no `chrraces_dbc` 43/44, model/display rows, player-create rows, cast-spell rows, or update receipt.

## Completed source work

The shared dirty checkout contains the prior Darkfallen work plus these verified corrections:

- `tools/darkfallen_race_pack.py` stages the additive root/locale package without changing source archives.
- `modules/mod-custom-server/data/sql/updates/pending_db_world/rev_1787850000020_darkfallen.sql` now:
  - clones creation-time cast spells from the High Elf/Blood Elf donors under the shared Darkfallen mask;
  - avoids converting zero language masks to the signed high bit.
- `src/server/game/Entities/Unit/Unit.h` now routes `Unit::getRaceMask()` through `GetRaceMaskForRace(getRace(true))`, which is required for race IDs 43/44.
- `src/server/shared/SharedDefines.h` contains the Darkfallen helper and has the trivial single-line brace style correction.
- `tools/test_darkfallen_contract.py` contains the packer/SQL/Unit contract checks.

Freshly observed before the final brace-only formatting correction:

```text
python tools/test_darkfallen_contract.py
Ran 11 tests
OK
```

Run it again after reboot before declaring the source gate green. The global SQL/C++ linters cannot currently complete because of unrelated dirty-tree issues (`origin/master` is absent for the SQL linter; the C++ linter reports unrelated LuaEngine formatting and an undecodable Eluna PNG). Scoped checks for the changed SQL/C++ files passed.

## Build and Docker interruption

Deployment was intentionally ordered as build -> SQL import -> recreate only `ac-worldserver`.

1. An initial cached `docker compose build ac-worldserver` continued after its terminal returned.
2. A second `docker compose build --no-cache ac-worldserver` was started to ensure the header changes compiled. It was actively compiling when Docker Desktop's engine stopped.
3. **Do not assume either build succeeded.** No resulting image was verified, no SQL was imported, and no service was recreated.
4. Docker Desktop then failed to restore its Linux engine. At handoff:
   - `com.docker.service` was stopped;
   - `\\.\pipe\dockerDesktopLinuxEngine` was absent;
   - Docker's backend log reported an inaccessible stale runtime endpoint at `C:\Users\Zach\AppData\Local\Docker\run\dockerInference`.

No attempt was made to delete that endpoint. A whole-system reboot is the preferred recovery.

## Resume after reboot

1. Confirm Docker Desktop is healthy before any deployment action:

   ```powershell
   docker version
   docker ps --format "table {{.Names}}\t{{.Status}}"
   docker buildx history ls
   ```

   Confirm `ac-database` is healthy. If stale build records remain, inspect them; do not start a third concurrent build.

2. Run exactly one clean worldserver build and wait for a successful completion:

   ```powershell
   docker compose build --no-cache ac-worldserver
   ```

3. Re-run the focused source contract:

   ```powershell
   rtk python tools/test_darkfallen_contract.py
   ```

4. Import only the dedicated Darkfallen migration into `acore_world`, then query the expected rows. Use the database container's own `MYSQL_ROOT_PASSWORD`; do not print it. The migration path is:

   ```text
   modules/mod-custom-server/data/sql/updates/pending_db_world/rev_1787850000020_darkfallen.sql
   ```

5. Recreate only the worldserver, preserving database/auth services and volumes:

   ```powershell
   docker compose up -d --no-deps --force-recreate ac-worldserver
   docker compose ps
   docker compose logs --tail 200 ac-worldserver
   ```

   Do not use `docker compose down -v`.

6. Verify the imported rows and the update receipt with SELECT-only queries. Then perform the manual client smoke in the active dev client: create both Darkfallen factions, relog, check language/starting skills/equipment/model visibility. Do not call it playable without this live smoke.

## Known non-core limitation

`src/server/game/Handlers/MiscHandler.cpp` uses a 32-bit WHO packet race filter with `1 << race`. It cannot uniquely represent IDs 43/44. This affects WHO filtering only, not character creation, login, faction, language, models, or equipment. Leave it unchanged unless a separately scoped packet-protocol solution is approved.

## Safety notes

- The checkout is heavily dirty. Preserve every unrelated change; never reset or clean it.
- Client archive backups already exist. Do not overwrite the active Z archives unless a future readback proves them wrong.
- The execution ledger is `.superpowers/sdd/darkfallen-playable-race.PLAN/progress.md`.
