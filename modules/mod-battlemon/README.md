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
X items (+2 stage for the Pokemon that is out, one battle) are sold in the Battle items category; the addon's battle
bag lists them (`UI/BattleFrame.lua` `X_ITEMS`, kept in step with the server by `tests/test_xitems_addon.py`) and now
scrolls with the mouse wheel when it holds more than six kinds of item. Check shop data with `python tests/test_shop_sql.py`.

## Following Pokemon

`.battlemon follow` makes your lead Pokemon walk behind you (`.battlemon follow 3` picks party slot 3, `... off`
stops it). It is a cosmetic creature using the Pokemon's overworld template, so it needs the overworld SQL; the
choice persists in `battlemon_follower`. It hides while you ride, fly, are in a battleground or in a Battlemon
battle and returns on its own, including after zoning. Config: `Battlemon.Follower.Enable` / `.Distance`.
It is separate from the Pokemon Trainer profession's Ditto companion, so both can be out at once.
In the addon, open the Party screen, select any Pokemon you own (it does not need a party slot) and press FOLLOW
(STOP FOLLOW when it is already the follower); the server confirms with `BM	FOLLOW	<id>`. The addon source is not in
this repository: verify the button with `python tests/test_follow_addon.py "<Battlemon addon dir>"`.

## Zone-aware spawns and the admin panel

Wild Pokemon now depend on where you are. Each WoW zone can list the Pokemon types that live there and a level
range (`battlemon_spawn_zone`, seeded for the standard Azeroth, Outland and Northrend zones; add your custom
zones). On top of the zone, every species is weighted by rarity (catch rate) and held back until its natural
level: the real evolution levels, plus a few levels for evolutions by stone, trade or friendship. A species is
picked before a form, so a species with many forms is no more common than one with a single form. Overworld
critters pick by their own zone when they morph. A zone with no row still gets the rarity and level rules.

The knobs live in `battlemon_spawn_setting` and apply immediately: `enable`, `level_mode` (0 follow your lead as
before, 1 roll inside the zone's range, 2 keep your level inside it), `rarity_exponent`, `stage_step`, `leak`
(how likely a type the zone does not list is) and the legendary/starter/normal class weights. Per-species
multipliers (0 bans) go in `battlemon_spawn_species`. Defaults leave levels exactly as they were.

Administrators edit all of it in the addon with `/bm admin`: change a knob and press Enter or APPLY ALL, edit the
levels and types of the zone you are standing in and SAVE ZONE, and PREVIEW to see the likeliest spawns there at
the resulting level. The server answers only accounts at administrator level. Check the maths with
`python tests/test_spawns.py` and the seed with `python tests/test_spawn_sql.py`; the panel with
`python tests/test_admin_addon.py "<Battlemon addon dir>"`.

## Move learning

Level-ups follow mainline. With fewer than four moves a Pokemon simply learns the new move; with four it queues an
offer (`battlemon_learn_offer`) and, once the battle screen closes (or at login, or when the Party screen opens),
the addon asks "Bulbasaur wants to learn Vine Whip! Forget which move?" with the four moves, their stats, and a
"Don't learn" button. The server answers only for offers it queued, only outside a battle, and only for your own
Pokemon. Closing the window leaves the offer waiting; a declined move can still be relearned for free from the move
manager, as before. Regional forms use their own level-up list. Slot logic: `python tests/test_moveslots.py`; the
prompt: `python tests/test_learn_addon.py "<Battlemon addon dir>"`.

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
