# Battlemon

One AzerothCore module containing the Pokemon collection and battle engine, overworld encounters,
classic battle UI support, world pet battles, human duels, Playerbot duels and the optional sidecar API.
The active 3D catalog includes all 980 converted Extras. Both client addons live under `addon/`.

## Installation and upgrades

Keep only `modules/mod-battlemon` for Battlemon server code. The former `mod-battlemon-overworld`
and `mod-battlemon-battles` directories have been merged into this module and must not remain enabled
from an older checkout. Commit the moved/new files **and** old-path deletions together. Retain
`mod-playerbots` for bot integration. Build remotely using your normal process; CMake must regenerate
its module/source list after the directory changes. No local configure/build was performed.

See [3D deployment](3D-DEPLOYMENT.md) for the catalog SQL and paired eDBC installer. Module SQL keeps
its original filenames and contents, so previously applied module migrations are still recognized.
Do not reimport base SQL just because the files moved. No consolidation-specific SQL is needed.

## Configuration

All **56 existing options**, their names and defaults remain available. The single module registers
all three original config filenames, so existing server settings require no rename or merge:

| File in the server's modules config directory | Options |
| --- | --- |
| `mod_battlemon.conf` | `Battlemon.*`: enable, starters, captures, encounters, rewards, revival, sidecar |
| `mod_battlemon_overworld.conf` | `BattlemonOverworld.*`: enable, critter morphing, rerolls, scale, hover, nudges |
| `mod_battlemon_battles.conf` | `BattlemonBattles.*`: enable, classic mode, duels, bot teams, timers, distance, actors, effects |

The matching `.conf.dist` templates are in `conf/`. Keep your existing `.conf` files; templates are
references for missing settings, not replacements for customized values. Disable features through
`BattlemonOverworld.Enable`, `BattlemonBattles.Enable`, `BattlemonBattles.EnableDuels` and
`BattlemonBattles.EnableBotDuels` instead of the retired per-module CMake switches. Disabling the
single `mod-battlemon` module disables the entire server integration.

## Client and tools

- `addon/Battlemon`: collection, moves, bag, classic UI and 3D previews.
- `addon/BattlemonBattles`: world battle HUD, switching/capture menus and duels.
- `tools/install_addon.py`: existing companion installer and packet hook, with backups.
- `tools/install_3d_dbcs.py`: guarded paired eDBC deployment.
- `tools/pixelmon/`: model/texture conversion and validation tools.
- `assets/battle-effects/`: preserved effect assets and delivery evidence.
- [Battle presentation and duel guide](docs/BATTLES.md).
- [Overworld guide](docs/OVERWORLD.md).

## Individual Pokemon

Each `battlemon_owned` row carries IVs, EVs, nature, ability slot and original trainer
(`2026_11_05_00_battlemon_individual.sql`; existing rows keep their exact stats). Stat maths is in
`src/BattlemonStats.h`; check it with `tests/test_stats.cpp`. Wins add the foe species' EV yield (`battlemon_species_ev`, covering all 1025 dex species; custom species such as
MissingNo fall back to 1 EV in their best base stat). Reference data comes from pokeemerald-expansion, Pokemon
Showdown and PKHeX via the importers in `tools/`: `import_ev_yields.py`, `import_learnsets.py` (egg moves; level-up
differences are reported, not applied) and `import_showdown.py` (Gen 9 moves the engine can already express).
Wild, caught and starter Pokemon roll random IVs and nature; trainer/duel teams keep IV 31.

## Poke Ball items

Talk to a Center attendant and pick "Seal a stored Pokemon in a Poke Ball" to turn a Pokemon that is not in your
party into a real item. Balls can be traded, mailed and auctioned (search the species name); right-clicking one
releases the Pokemon into the user's collection. Item templates are generated per species and shiny state by
`tools/export_ball_items.py` (entries 960000+). The Pokemon stays in `battlemon_owned` with `guid = 0`, linked by
`battlemon_ball_item`; the item and the Pokemon change in one transaction. Orphan-recovery SQL is in
`data/sql/db-characters/base/2026_11_05_01_battlemon_ball_item.sql`. Custom species (id above 1025) have no ball yet.
The icon (Hearthstone's display id) and the "Use:" tooltip (a placeholder spell) are set at the top of the tool.

## Items, berries and the menu shop

The Center attendant also has a gossip shop ("Buy supplies with Battlemon Points (menu)"), so buying works
without the addon: pick a category, pick an item, type a quantity. It sells whatever `battlemon_shop` lists
(balls, medicine, drinks, berries). Oran (10 HP) and Sitrus (a quarter of max HP) berries are now usable.
The server also supports X items (+2 stage in battle), but they are not sold yet: the addon's battle bag only
lists `OnPokemon` items, so `addon/Battlemon/UI/BattleFrame.lua` and `BagFrame.lua` need to accept `OnBattler`
for them first. Check shop data with `python tests/test_shop_sql.py`.

## Following Pokemon

`.battlemon follow` makes your lead Pokemon walk behind you (`.battlemon follow 3` picks party slot 3, `... off`
stops it). It is a cosmetic creature using the Pokemon's overworld template, so it needs the overworld SQL; the
choice persists in `battlemon_follower`. It hides while you ride, fly, are in a battleground or in a Battlemon
battle and returns on its own, including after zoning. Config: `Battlemon.Follower.Enable` / `.Distance`.
It is separate from the Pokemon Trainer profession's Ditto companion, so both can be out at once.

## Verification

Run `python tests/test_module_layout.py`, `python tools/test_3d_catalog.py` and
`python tests/test_addon.py addon/Battlemon`. Installer regression tests are under `tests/`. The real-MySQL migration regression is
`tests/test_3d_migration_mysql.py`; it requires a MySQL client/connection file and creates only
disposable test databases. It covers full migration, partial-failure retry, collision/schema guards,
precise ownership cleanup and rollback.
No model reconversion or asset changes are needed for the consolidation. The frozen 2D distribution
remains unchanged. Historical generated conversion evidence was moved byte-for-byte into `generated/`;
its original absolute paths can be translated using `generated/module-consolidation/receipt.json`.
Do not rewrite old proof hashes or rerun historical install scripts merely to change their path strings.
