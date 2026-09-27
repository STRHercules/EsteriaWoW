# AzerothCore Random WotLK Item Pack

Deterministic seed: `3874151851`<br>
Output directory: `generated-3874151851`<br>
Generated items: `10000`<br>
Automatic name repairs: `0`<br>
Expansion: `All` (`1-80`)<br>
Classes: `Warrior, Paladin, Hunter, Rogue, Priest, Death Knight, Shaman, Mage, Warlock, Druid`<br>
Magic effects: `All`<br>
Sockets: `yes`<br>
Legendaries: `yes`<br>
Generated entry ranges: `Warrior: 200000-200999; Paladin: 220000-220999; Hunter: 240000-240999; Rogue: 260000-260999; Priest: 280000-280999; Death Knight: 300000-300999; Shaman: 320000-320999; Mage: 340000-340999; Warlock: 360000-360999; Druid: 380000-380999`<br>
Generated loot pools: `6` (`10000` item rows)<br>
World-loot attachments: `310` at `2.0%`<br>
Loot destinations: `world, dungeon, raid`<br>
Dungeon/raid LootMode: `1 << MapDifficulty difficulty_id`<br>
Placement reports: `world_item_placements.csv`, `dungeon_raid_item_placements.csv`, `encounter_profile_coverage.csv`, `encounter_profiles.csv`, `difficulty_band_comparison.csv`, `encounter_band_rejections.csv`, `encounter_distribution_audit.csv`, `encounter_reference_provenance.csv`, `gameobject_reward_targets.csv`, `set_manifest.csv`<br>
World-loot source: `creature_loot_template.sql`<br>
Reference-loot source: `reference_loot_template.sql`<br>
Dungeon/raid source files: `Map.dbc, MapDifficulty.dbc, DungeonMap.dbc, creature.sql, creature_template.sql, instance_encounters.sql`<br>
Optional gameobject source files: `gameobject.sql, gameobject_template.sql, gameobject_loot_template.sql`<br>
Gameobject source discovery: the complete optional `gameobject.sql`, `gameobject_template.sql`, and `gameobject_loot_template.sql` trio is used when present; `gameobject_template.Data1` supplies the loot relationship.<br>
Gameobject association methods: `explicit_instance_mapping`, `script_summon`, and diagnostic `static_spawn` rows; static map-only rows are never guessed as boss rewards. Rejected static spawns are aggregated per map/reward object by default; add `--verbose-audit` for the full per-spawn audit.<br>
Script reward mapping: `EXERCISED` (files scanned: `325`, candidate reward calls: `36`, validated mappings: `13`, rejected mappings: `89`)<br>
Item-template source: `item_template.sql`<br>
Client Item.dbc sources: `Item.dbc, Item.custom.dbc`<br>
ItemSet.dbc source: `ItemSet.dbc`<br>
Spell.dbc source: `Spell.dbc`<br>
SpellItemEnchantment.dbc source: `SpellItemEnchantment.dbc`<br>
Disenchant source: `disenchant_loot_template.sql`<br>
Spell proc source: `spell_proc.sql`<br>
Spell script source: `spell_script_names.sql`<br>
Disabled new features: `none`<br>
Feature counts: `{"chance-on-hit": 9, "disenchant": 9891, "on-use": 33, "sets": 20, "socket-bonuses": 697, "spell-effects": 92}`<br>
Harvested stock appearance references: `16521`<br>
Harvested unique stock display IDs: `16429`<br>
Appearance fallback categories: `0`<br>
Appearance provenance: `reference_catalog_used.csv` (`16521` rows; strict scope: `no`)<br>
Target: AzerothCore / WotLK 3.3.5a

## Generator CLI

- `py generate_pack.py` - default 100,000-item pack (10,000 per class).
- `py generate_pack.py` - also reads the dungeon/raid DBC and SQL sources and writes world plus dungeon/raid loot integrations by default.
- `py generate_pack.py --number 10` - exactly 10 items total, distributed across classes.
- `py generate_pack.py --class warrior` - default 10,000-item Warrior block.
- `py generate_pack.py --seed 12311523 --number 20 --class warlock` - exactly 20 deterministic Warlock items.
- `py generate_pack.py --number 200000` - maximum pack: 200,000 items total, 20,000 per class.
- `py generate_pack.py --class warrior --number 20000` - maximum single-class pack: 20,000 Warrior items.
- `py generate_pack.py --loot-chance 5` - override the default 2% independent roll on each shared world-loot reference.
- `py generate_pack.py --world-loot-source PATH --reference-loot-source PATH` - use alternate base loot SQL sources.
- `py generate_pack.py --item-template-source PATH` - use an alternate stock item-template source for appearance harvesting.
- `py generate_pack.py` - always uses the vanilla `Item.dbc`; `Item.custom.dbc` beside the generator is merged automatically only when it exists, then the merged copy is written under `client/`.
- `py generate_pack.py --item-dbc-source PATH --item-dbc-source PATH` - merge every complete or additive WotLK `Item.dbc` source supplied; repeat the option for each client baseline.
- Add `--item-dbc-overwrite` only when intentionally replacing conflicting generated-ID rows in that source DBC.
- `py generate_pack.py --disable sets chance-on-hit` - disable selected new features; `effects` disables all three item spell triggers and `all-new` disables every new feature.
- Encounter integration is source-backed and fail-closed. If validation is invalid, diagnostic reports remain available but encounter SQL is omitted from `sql/IMPORT_ORDER.txt`; item and world-loot output still completes.
- `--set-rate`, `--set-min-level`, `--set-size` - tune complete class/role set generation; five pieces is the default.
- `--spell-effect-rate-multiplier`, `--proc-rate-multiplier`, `--on-use-rate-multiplier`, `--effect-ilvl-window`, `--max-special-effects` - tune stock effect-package selection; low-level effects still obey the stricter 5/10/15 progression windows.
- `--socket-bonus-rate`, `--disenchant-rate` - tune validated stock socket and disenchant assignment.
- `--no-sockets` - skip socket colors, including the guaranteed sockets used by Legendary items.
- `--ui auto|fancy|plain` - choose the terminal presentation; `auto` uses the Rich live dashboard on an interactive terminal when Rich is installed and falls back to plain output otherwise.
- `--no-animations` - keep the styled dashboard but disable animated spinners.
- `--show-items` - expand the live discovery feed beyond the default Legendary, set, proc, and special-effect callouts.
- `--quiet` - suppress progress output and print only errors plus the final completion line.
- `--verbose-audit` - keep every rejected static gameobject spawn row in `gameobject_reward_targets.csv`; the default aggregates them per map, reward object, and loot entry.
- Rich is optional. If installed, interactive `--ui auto` runs use the live dashboard; otherwise the generator automatically falls back to the standard-library plain UI.

Flags can be combined in any order. The default remains 100,000 total and world-loot attachment chance defaults to 2%. Explicit `--number` is capped at 200,000 total and 20,000 per selected class.

## Safety / generation policy

- Final values are generated and validated before SQL is emitted.
- Stock appearances are auto-harvested from the complete supplied `item_template.sql`, including current-schema weapon damage/delay fields, deduplicated by display ID per compatible equipment category, and weighted by reference item level/quality.
- The old curated appearance rows are used only as expansion-scoped safety fallbacks for categories missing from the supplied stock table.
- Generated names reject repeated meaningful words anywhere in the name plus compound-root repetitions such as `Earthshard Shard`.
- Legendary flavor text is equipment-aware for weapons, armor, shields, relics, and accessories.
- Death Knight items are generated only for required levels 55-80.
- Uncommon quality is capped at item level 213; Rare quality is capped at item level 226.
- Ordinary gear uses role/equipment-compatible multi-class masks; class-specific relics remain class-specific.
- Legendaries use dedicated names, guaranteed flavor text, five stats, at least two sockets, and distinct source classes when possible.
- Static stats are packed contiguously from stat slot 1.
- `RandomProperty` and `RandomSuffix` are zero.
- Item spell effects are copied as complete stock packages and validated against `Spell.dbc`, `spell_proc.sql`, and `spell_script_names.sql`.
- Generated sets use complete class/role groups (five pieces by default), stock visual families where available, and exactly one stock 2-piece plus one stock 4-piece bonus when the configured size supports it in merged `client/ItemSet.dbc`.
- The same generated `ItemSet.dbc` is staged under `server/dbc/ItemSet.dbc` because AzerothCore worldserver must load the generated set definitions too.
- Socket bonuses are resolved through `SpellItemEnchantment.dbc`; no enchantment ID is invented.
- Disenchant pairs are copied from stock item rows only when their `DisenchantID` exists in `disenchant_loot_template.sql`.
- Set pieces do not receive independent random special effects by default.
- Every catalog `displayid`, class, subclass, and inventory type is checked against the selected `item_template.sql` before generation.
- SQL uses explicit column lists and transactions.
- Generated items are placed into up to six centralized `reference_loot_template` pools by required-level bracket.
- Pool rows use `Chance = 0`, `GroupId = 1` to select one generated item; attachments use `GroupId = 0` and the configured independent roll.
- Existing creature loot rows are not rewritten. World-loot levels 81–82 use the level-80 pool, and the generated pool is shared across classes.
- Encounter placement requires both ItemLevel and RequiredLevel evidence, respects each MapDifficulty LootMode, rejects unsafe shared references/outliers, and keeps generated sets in one map+difficulty.
- Generated reference pool IDs are reserved at `3000000`–`3000005`; attachment keys use the reserved `2000000000 + parent_reference` range.
- Item entries use the `200000-399999` namespace, split into 20,000-ID blocks per class.
- The default 100,000-item pack uses the first 10,000 IDs of each class block; larger runs fill those blocks up to 200,000 items.

## Import

1. Run `00_SCHEMA_CHECK.sql` and confirm the columns match your AzerothCore schema.
2. Run `00_PREIMPORT_COLLISION_CHECK.sql`. Do not import unless every reported collision count is 0.
3. Import files in `sql/IMPORT_ORDER.txt`. Encounter SQL appears there only when encounter integration validation succeeds.
4. When sets are enabled, copy `server/dbc/ItemSet.dbc` into the AzerothCore worldserver DBC directory.
5. Restart worldserver after the SQL import and server DBC copy.
6. With the client closed, clear `Cache/WDB/<locale>/itemcache.wdb` if item names/icons are stale, then retest.
7. `client/item_dbc_rows.csv` contains only this run's generated rows; `client/item_dbc_merged_rows.csv` contains the complete final client table.
8. When sets are enabled, package `client/ItemSet.dbc` as `DBFilesClient\ItemSet.dbc` alongside `client/Item.dbc`.
9. All configured DBC sources are merged additively. Identical duplicate rows are accepted; conflicting rows stop generation instead of silently overwriting client data.
10. Package only the final `client/Item.dbc` and `client/ItemSet.dbc` externally and keep other custom client assets/DBC rows in the effective source set.

`00_PREIMPORT_COLLISION_CHECK.sql` checks item IDs, reserved pool IDs, pool references, and attachment keys. `99_REMOVE_GENERATED_ITEMS.sql` removes this run's generated items, pools, and pool attachments.


## Collision-safe encounter attachment patch

Dungeon/raid attachment rows use reserved synthetic `Item` keys `2010000001` through `2010000622` so they do not collide with existing `(Entry, Item)` primary keys that happen to use `Item = 1`. Run `00_PREIMPORT_COLLISION_CHECK.sql` before importing. See `FIX_NOTES.md` and `encounter_attachment_keys.csv`.
