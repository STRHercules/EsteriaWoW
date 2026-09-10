# Battlemon installation and runtime status

Date: 2026-09-08

Scope: implementation of the Battlemon server modules, WXL server continuation support, sanitized client assets, addon, and runtime verification in Esteria.

## Verdict

Battlemon is installed and enabled in the Esteria server runtime. The overworld path now loads its display/model data through WarcraftXL-style server continuation files, and the worldserver reaches its ready marker without the previous crash.

The supplied contaminated continuation files were not copied wholesale. Clean Battlemon-only continuations were selected from the staged client overlays and used on both sides. Esteria's existing base DBCs and other patch layers remain untouched.

Completed:

- `mod-battlemon`, `mod-battlemon-overworld`, and the upstream-compatible `mod-wxl-dbc` server modules are present and enabled.
- The overworld form-entry collision was moved to `1000001..1001581`; live entry `70100` remains unchanged.
- The live database contains the Battlemon catalog and form templates.
- The persistent Docker client-data volume contains only the two Battlemon server continuation files.
- The rebuilt worldserver is running with `RestartCount=0` and reports 6,324 continuation rows applied and the Battlemon catalog loaded.

Remaining verification is client launch/extension-load, addon UI, and actual Battlemon gameplay smoke; those cannot be established from server startup alone.

## What was inspected

The downloaded documentation/readmes were read, including:

- `Server\modules\mod-battlemon\README.md` — title only; no installation instructions.
- `Server\modules\mod-battlemon-overworld\README.md` — module dependency, SQL, DBC, loose-file, spawn, and configuration instructions.
- `Client\addon\Battlemon\README.md` — title only.
- `Server\server-sidecar-optional\Battlemon-web\README.md`.
- `Server\server-sidecar-optional\Battlemon-web\deploy\README-deploy.md`.
- `Server\server-sidecar-optional\Battlemon-web\web\README.md`.
- `zExternal-sidecar-clients\pokeshell\README.md`.
- `zExternal-sidecar-clients\pokeshell\LIMITATIONS.md`.
- `zExternal-sidecar-clients\pokeshell - 3d-model-test\README.md`.
- `zExternal-sidecar-clients\pokeshell - 3d-model-test\3D-TEST.md`.
- `zExternal-sidecar-clients\pokeshell - 3d-model-test\LIMITATIONS.md`.

The PokeShell README and LIMITATIONS copies are byte-for-byte duplicates. The sidecar/web/PokeShell projects are optional and are not required for the in-game addon.

## Package contents

### Server modules

`Server\modules` contains:

- `mod-battlemon` — core Battlemon catalog, collection, party, battle, catch, shop, bag, move, shiny, faint/revive, chat-addon protocol, and optional TCP sidecar.
- `mod-battlemon-overworld` — depends on `mod-battlemon`; morphs critters, supports right-click wild encounters, and provides `.bmo` commands.

The primary catalog is substantial but internally aligned:

- 1,025 species.
- 1,581 forms.
- 740 moves.
- 693 items.
- 14,201 and 15,546 species-move seed rows from successive catalog revisions.
- 59,295 tutor-move rows.
- 4,428 per-form move rows.

`mod-battlemon` stores its own state in `acore_characters` and catalog in `acore_world`, using `battlemon_*` tables. The SQL is idempotent-oriented (`CREATE TABLE IF NOT EXISTS`, `REPLACE`, and guarded migrations), though several older/newer seed files coexist and later filenames replace earlier rows.

### Client patch

`Client\patch-Z.mpq` is a **folder patch**, not an MPQ archive. It contains:

- `CreatureDisplayInfo.dbc` — 24,262 base records.
- `CreatureModelData.dbc` — 1,331 base records.
- `CreatureDisplayInfo.dbc1-battlemon` — 10,611 records.
- `CreatureModelData.dbc1-battlemon` — 3,173 records.
- 3,162 `.m2`, 3,162 `.skin`, and 3,162 `.blp` files under `Creature\Battlemon`.

The Battlemon form catalog has IDs `1..1581`, so the expected client additions are 3,162 display rows and 3,162 model rows:

- Displays: `50001..51581` normal and `70001..71581` shiny. Broken retains `60002/60003`.
- Models: `2252001..2253581` normal and `2272001..2273581` shiny.

All expected Battlemon rows are present. However, the display continuation has **7,449 additional out-of-range rows**, and the model continuation has **11 additional out-of-range rows**. These files are therefore not isolated Battlemon deltas; they appear to carry other client changes as well.

The patch also includes full base `.dbc` files. The Extended DBC project explicitly exists to layer `*.dbc1-*` files without replacing the original tables. Do not blindly replace the current client's base DBCs or import the entire contaminated continuation into Esteria.

The downloaded patch has no `wxl-dbc.manifest`, which is acceptable for a folder patch because the extension auto-discovers continuation files. A real MPQ archive would require a manifest.

### Addon

`Client\addon\Battlemon\Battlemon.toc` targets interface `30300`, appropriate for WotLK 3.3.5a. It contains embedded CSV data, core networking/UI code, and all listed UI frames; it does not use a WXL-specific Lua API.

The addon sends `BM` commands through `SendAddonMessage` and receives the server response through the existing `LANG_ADDON` self-whisper path. This matches the current Esteria core pattern used by AzerothCore and existing local addons.

Asset checks found:

- All 1,581 front sprites are present.
- 18 back-sprite names are absent; the addon falls back to front art.
- One shiny front sprite (`0323_Camerupt_01_female`) is absent; the addon falls back to normal art.
- `BattleMusic.lua` references `Music\01 - GBA - Battle Vs. Wild Pokemon.mp3`, but that file is not present in the downloaded addon. Battlemon can still function; only that optional music path is incomplete.

## Esteria compatibility

### CMake and server API

The current Esteria module system auto-discovers every `modules\<module>\src` directory and separately copies every `modules\<module>\conf\*.conf.dist` file. The Battlemon modules use the same current hooks and APIs already present in this checkout:

- `WorldScript` startup/config/shutdown/update hooks.
- `PlayerScript` login/logout and addon-chat hooks.
- `AllCreatureScript`, `CreatureScript`, and `DatabaseScript` hooks.
- Current `Creature::UpdateEntry`, display, scale, summon, and gossip APIs.
- Current `ChatHandler::BuildChatPacket` `LANG_ADDON` path.
- Current Boost.Asio/thread and AzerothCore crypto dependencies.

`mod-battlemon` has duplicated deprecated `AC_ADD_SCRIPT`/`AC_ADD_CONFIG_FILE` lines, but the current module collector handles the `src` tree and current config glob independently. This is untidy, not an install blocker.

The overworld module's `creature_model_info` rows reference Battlemon display IDs, so server-side WXL continuation support is required as well as the client DLL. The upstream `mod-wxl-dbc` module was added, and its six-file core patch was applied so continuations load after normal DBC files and `*_dbc` database overlays, before world startup validation. The server then reads the injected `CreatureDisplayInfo`/`CreatureModelData` rows while loading creature model information.

### SQL discovery

The primary module uses the current-style paths:

- `data\sql\db-world\...`
- `data\sql\db-characters\...`

The overworld module uses `data\sql\world\base`. In this checkout, `UpdateFetcher.cpp` accepts module SQL directories whose name contains the active database token (`world`, `characters`, etc.), so `world` is discovered for the world database. The current `dbimport.conf` has `Updates.AllowedModules = "all"`.

### Current checkout/runtime state

The current checkout is on `main` at `760fbfad8eb52ece65dfcc79b9fca1d6a3408948`. It already has unrelated dirty logs, `mod-learn-spells` work, and `mod-starting-pet` work; those were preserved.

Battlemon is installed/staged in Esteria:

- `modules\mod-battlemon`, `modules\mod-battlemon-overworld`, and `modules\mod-wxl-dbc` are present.
- Active configs are present under `env\dist\etc\modules`; Battlemon, overworld, and WXL continuation loading are enabled, while the Battlemon sidecar remains disabled.
- The live `acore_world` database contains 1,025 species, 1,581 forms, 740 moves, 693 items, and 1,581 overworld creature templates in `1000001..1001581`.
- The live database still contains creature entry `70100`, named `Conversing With the Depths Trigger`, with script `npc_conversing_with_the_depths_trigger`.
- The client staging contains the sanitized patch folder, Battlemon addon, Battlemon model assets, and clean continuation overlays.
- The persistent Docker client-data volume contains `data\dbc-continuations\CreatureDisplayInfo.dbc1-battlemon` and `CreatureModelData.dbc1-battlemon`.

## Completed server-entry reconciliation

The old mapping used `FormEntryBase = 70000`, producing creature entries `70001..71581`. Form ID `100` therefore collided with the existing live entry `70100`.

I selected `FormEntryBase = 1000000` after checking the live `acore_world` database. The new form-template range is `1000001..1001581`, and the live checks found zero occupants or references in that range across:

- `creature_template`.
- creature spawns.
- SmartAI entry references.
- condition `SourceEntry` references.

The coordinated package changes were:

- `src\BattlemonOverworld.h`: `FormEntryBase = 1000000`.
- `tools\export_form_npcs_sql.py`: matching `FORM_ENTRY_BASE = 1000000` and documentation.
- Regenerated `data\sql\world\base\2026_08_21_02_battlemon_overworld_form_npcs.sql`.

The regenerated SQL contains exactly 1,581 form templates in `1000001..1001581`; the old `70100` database row was left untouched. This corrected SQL is present in Esteria's Battlemon module and is imported in the live database.

The generic creature entry remains `60000`. Client display/model IDs remain unchanged because they are separate namespaces.

Validation performed:

- RED collision assertion: the old creature-entry range `70001..71581` failed because one live entry was occupied.
- GREEN mapping/SQL invariant: passed with 1,581 unique template entries in `1000001..1001581` and 3,162 expected display-info references.
- Live database check: passed with zero current occupants in `1000001..1001581`; the existing `70100` template remains present and unchanged.
- Docker build completed successfully for the rebuilt worldserver image after removing two unavailable upstream registry names (`sCharacterFacialHairStylesStore` and `sCharHairGeosetsStore`) from the WXL registry.
- The Battlemon database import completed successfully before the WXL-only server integration; the live catalog and form-template counts are verified above.
- The rebuilt worldserver was recreated and remains running with `RestartCount=0`.

## Implemented Esteria client DBC policy

For Esteria, we leave the existing base DBCs untouched and use WarcraftXL additive continuation files, such as `CreatureDisplayInfo.dbc1-battlemon`, to add Battlemon rows only. This policy is implemented for both the client patch and the server data volume.

Each continuation was verified to contain only the expected Battlemon IDs:

- `CreatureDisplayInfo.dbc1-battlemon`: `50001..51581` and `70001..71581`.
- `CreatureModelData.dbc1-battlemon`: `2252001..2253581` and `2272001..2273581`.

Existing Esteria patch layers remain in place; the downloaded full base DBCs and unrelated continuation rows are not part of the Esteria Battlemon install.

The original downloaded continuation payload remains unsuitable: its display file had 7,449 extra rows and its model file had 11 extra rows. Those rows were excluded. The clean client files contain 3,162 display rows and 3,162 model rows, and the server continuation copies have matching SHA-256 content.

The full base DBC files were not copied or replaced. Existing patch layers remain the authority for all non-Battlemon rows.

## WarcraftXL Extended DBC status

Upstream documentation: [wxl-extended-dbc](https://github.com/notacoder-dev/wxl-extended-dbc).

The upstream README says the client DLL belongs at `<WoW>\Extensions\wxl-extended-dbc\`. The installed DLL is at the correct path:

`R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Extensions\wxl-extended-dbc\wxl-extended-dbc.dll`

Observed SHA-256:

`89779553920782a544857e717f52bee3ad0e4a32020a83b1e3fab521d376e41c`

The DLL has no embedded Windows file/product version metadata, so its exact source commit cannot be confirmed from the file alone. The referenced upstream manifest currently identifies version `1.0.0` and ABI `1.1`; matching the local DLL to that release still needs a client launch/load check.

The specified `3.3.5a - Dev` client already has `WarcraftXL.dll` and an `Extensions` directory. The sanitized Battlemon folder patch and addon are now staged at:

- `3.3.5a - Dev\Data\patch-z.mpq\DBFilesClient\` plus `Creature\Battlemon\` assets.
- `3.3.5a - Dev\Interface\AddOns\Battlemon\`.

## Server-side WXL continuation integration

The upstream `server-files\module\mod-wxl-dbc` module is installed as `modules\mod-wxl-dbc`. Its required core integration is present in:

- `src\server\game\Scripting\ScriptDefines\WorldScript.h` and `.cpp`.
- `src\server\game\Scripting\ScriptMgr.h`.
- `src\server\game\World\World.cpp`.
- `src\server\shared\DataStores\DBCStore.h`.
- `src\server\game\DataStores\DBCStores.cpp` and `.h`.

The added hook runs immediately after `LoadDBCStores()`. The WXL loader then scans `data\dbc-continuations`, injects continuation rows after base DBC/SQL-overlay loading, and rebuilds the affected derived indexes. Esteria's two unavailable upstream store names (`sCharacterFacialHairStylesStore` and `sCharHairGeosetsStore`) were omitted from the registry; the Battlemon-required CreatureDisplayInfo and CreatureModelData stores are registered.

The active server config is `env\dist\etc\modules\mod_wxl_dbc.conf` with `WxlDbc.Enable = 1` and `WxlDbc.ContinuationPath = dbc-continuations`. The persistent Docker data volume contains only the clean Battlemon continuation files under `/azerothcore/env/dist/data/dbc-continuations`.

## Optional sidecar/web/PokeShell

These are not needed for the WoW addon:

- `Battlemon.Sidecar.Enable` defaults to `0`.
- PokeShell is a standalone PowerShell client with offline mode and an optional online sidecar mode.
- Battlemon-web is a separate Node/Vite/Fastify/SQLite LAN web client.

If the sidecar is later enabled, use a deliberate bind/firewall policy. The supplied docs recommend `127.0.0.1:8787` when the web client is on the same host and warn that the sidecar has token authentication but no TLS. The current Esteria Compose override does not publish port `8787` or define the optional Battlemon web service.

The PokeShell limitations document reports 740 catalog moves: 407 fully supported, 31 partial, 157 damage-only, and 145 unsupported. That is a gameplay coverage limitation, not an installation dependency.

## Safe follow-up sequence

1. **Completed:** move the overworld form-template range to the verified `1000001..1001581` block; do not import the current `70100` row unchanged.
2. **Completed:** select and validate clean Battlemon-only continuations for the actual Esteria client. Preserve the current base DBCs and other patch layers.
3. **Completed:** copy `mod-battlemon`, the dependent `mod-battlemon-overworld`, and server-side `mod-wxl-dbc` into Esteria `modules`.
4. **Completed:** enable the Battlemon/WXL active configs. The sidecar remains disabled unless the web/PokeShell path is intentionally wanted.
5. **Completed:** build the worldserver image, retain the successful Battlemon database import, and recreate the worldserver without deleting persistent Docker volumes.
6. **Completed:** stage the sanitized folder patch at `3.3.5a - Dev\Data\patch-z.mpq` and the addon directory at `3.3.5a - Dev\Interface\AddOns\Battlemon`.
7. **Pending:** fully exit/relaunch the WXL client, then verify the DLL load and client DBC rows in the live client.
8. **Pending:** verify server commands/UI/gameplay: `.battlemon status`, `/bm`, `.battlemon wild`, and—only if enabled—`.bmo status`/`.bmo spawn`.

## Verification boundary

Completed and verified:

- Docker CMake/build: the rebuilt `acore/ac-wotlk-worldserver:master` image links successfully with both Battlemon modules, WXL server support, and the six-file core integration.
- Database state: Battlemon catalog/form-template counts and the untouched `70100` row are verified live.
- Server continuation load: 2 files and 6,324 rows applied from `/azerothcore/env/dist/data/dbc-continuations`.
- Server startup: `WORLD: World Initialized`, the worldserver ready marker, Battlemon catalog startup, `Status=running`, and `RestartCount=0`.
- Client asset contract: both client continuation files contain exactly their expected 3,162 Battlemon rows; no base DBC replacement occurred.
- C++ style check: the repository-wide script still exits `1` on its pre-existing multiple-blank-line warning at `src\server\game\DataStores\DBCStores.h:37`; it reported no Battlemon/WXL-specific style finding in the filtered output.

Still outstanding:

- Client launch and confirmation that the installed WarcraftXL DLL loads the continuation rows.
- Addon Lua/UI runtime smoke test.
- Battlemon battle, catch, overworld interaction, and multiplayer gameplay test.
