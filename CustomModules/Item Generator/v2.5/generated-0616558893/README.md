# AzerothCore Random WotLK Item Pack

Deterministic seed: `0616558893`  
Output directory: `generated-0616558893`  
Generated items: `100000`  
Classes: `Warrior, Paladin, Hunter, Rogue, Priest, Death Knight, Shaman, Mage, Warlock, Druid`  
Generated entry ranges: `Warrior: 200000-209999; Paladin: 220000-229999; Hunter: 240000-249999; Rogue: 260000-269999; Priest: 280000-289999; Death Knight: 300000-309999; Shaman: 320000-329999; Mage: 340000-349999; Warlock: 360000-369999; Druid: 380000-389999`  
Generated loot pools: `6` (`100000` item rows)  
World-loot attachments: `310` at `10.0%`  
World-loot source: `R:\Users\Zach\Documents\GitHub\Azeroth\data\sql\base\db_world\creature_loot_template.sql`  
Reference-loot source: `R:\Users\Zach\Documents\GitHub\Azeroth\data\sql\base\db_world\reference_loot_template.sql`  
Target: AzerothCore / WotLK 3.3.5a

## Generator CLI

- `py generate_pack.py` - default 100,000-item pack (10,000 per class).
- `py generate_pack.py --number 10` - exactly 10 items total, distributed across classes.
- `py generate_pack.py --class warrior` - default 10,000-item Warrior block.
- `py generate_pack.py --seed 12311523 --number 20 --class warlock` - exactly 20 deterministic Warlock items.
- `py generate_pack.py --number 200000` - maximum pack: 200,000 items total, 20,000 per class.
- `py generate_pack.py --class warrior --number 20000` - maximum single-class pack: 20,000 Warrior items.
- `py generate_pack.py --loot-chance 5` - use a 5% independent roll on each shared world-loot reference.
- `py generate_pack.py --world-loot-source PATH --reference-loot-source PATH` - use alternate base loot SQL sources.

Flags can be combined in any order. The default remains 100,000 total. Explicit `--number` is capped at 200,000 total and 20,000 per selected class.

## Safety / generation policy

- Final values are generated and validated before SQL is emitted.
- Static stats are packed contiguously from stat slot 1.
- `RandomProperty` and `RandomSuffix` are zero.
- No random item spells/procs are generated.
- No socket bonus ID is generated (`socketBonus = 0`).
- No disenchant ID is invented (`DisenchantID = 0`, `RequiredDisenchantSkill = -1`).
- Every `displayid` comes from a verified existing WotLK item reference captured from AzerothCore's official base `item_template.sql`.
- SQL uses explicit column lists and transactions.
- Generated items are placed into up to six centralized `reference_loot_template` pools by required-level bracket.
- Pool rows use `Chance = 0`, `GroupId = 1` to select one generated item; attachments use `GroupId = 0` and the configured independent roll.
- Existing creature loot rows are not rewritten. World-loot levels 81–82 use the level-80 pool, and the generated pool is shared across classes.
- Generated reference pool IDs are reserved at `3000000`–`3000005`; attachment keys use the reserved `2000000000 + parent_reference` range.
- Item entries use the `200000-399999` namespace, split into 20,000-ID blocks per class.
- The default 100,000-item pack uses the first 10,000 IDs of each class block; larger runs fill those blocks up to 200,000 items.

## Import

1. Run `00_SCHEMA_CHECK.sql` and confirm the columns match your AzerothCore schema.
2. Run `00_PREIMPORT_COLLISION_CHECK.sql`. Do not import unless every reported collision count is 0.
3. Import files in `sql/IMPORT_ORDER.txt`.
4. Restart worldserver after import.
5. Clear the relevant client `itemcache.wdb` if cached item data is stale.

`00_PREIMPORT_COLLISION_CHECK.sql` checks item IDs, reserved pool IDs, pool references, and attachment keys. `99_REMOVE_GENERATED_ITEMS.sql` removes this run's generated items, pools, and pool attachments.
