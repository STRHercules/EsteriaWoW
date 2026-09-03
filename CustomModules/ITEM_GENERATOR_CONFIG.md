# ITEM_GENERATOR_CONFIG.md

# AzerothCore Custom Item Generator
## Default Generation Configuration

This file defines the default behavior, ranges, weights, balance philosophy, ID allocation rules, naming behavior, and validation limits used by the AzerothCore Custom Item Generator Agent.

These settings apply whenever the user asks for generated items without explicitly overriding them.

User-provided values always take priority over this file.

---

# 1. CONFIGURATION PRIORITY

Resolve configuration in this order:

```text
1. Explicit values in the current user request
2. Explicit batch-generation configuration supplied by the user
3. Project/server-specific configuration
4. ITEM_GENERATOR_CONFIG.md defaults
5. Reference-item-derived values
6. Conservative AzerothCore/WotLK defaults
```

Example:

If this file says:

```yaml
default_quality: epic
```

but the user requests:

```text
Generate 10 rare swords.
```

then use:

```yaml
quality: rare
```

The user's request wins.

---

# 2. GLOBAL GENERATOR MODE

```yaml
generator:
  mode: reference_based

  randomness: custom

  deterministic_when_seeded: true

  default_seed: null

  validate_before_output: true

  emit_invalid_items: false

  auto_correct_minor_conflicts: true

  warn_on_major_conflicts: true

  preserve_intentional_overpowered_values: true
```

Supported modes:

```text
reference_based
range_based
explicit
wild
```

Default:

```yaml
mode: reference_based
```

The generator should prefer comparable Blizzard WotLK items when determining normal item power.

---

# 3. TARGET GAME

```yaml
target:
  core: AzerothCore
  expansion: Wrath of the Lich King
  client_version: "3.3.5a"
  database: acore_world
  primary_table: item_template
```

Do not silently generate Cataclysm, Retail, Classic Era, or post-WotLK item mechanics.

---

# 4. CUSTOM ENTRY ID RANGE

Default custom item namespace:

```yaml
entry_ids:
  min: 900000
  max: 999999

  allocation: sequential

  verify_free_ids_when_database_available: true

  overwrite_existing_custom_item: false

  overwrite_blizzard_item: false
```

Preferred allocation:

```text
900000
900001
900002
900003
...
```

If the requested count exceeds the available entry range:

```text
STOP GENERATION
```

and report the shortage.

Never silently reuse IDs.

---

# 5. SQL OUTPUT SETTINGS

```yaml
sql:
  schema: acore_world

  table: item_template

  explicit_column_lists: true

  delete_before_insert: true

  use_transactions_for_batches: true

  batch_transaction_threshold: 2

  escape_strings: true

  include_comments: true

  include_spawn_commands: true

  qualify_database_name: false
```

Preferred single-item SQL:

```sql
DELETE FROM `item_template`
WHERE `entry` = 900000;

INSERT INTO `item_template`
(
    ...
)
VALUES
(
    ...
);
```

Preferred batch SQL:

```sql
START TRANSACTION;

DELETE FROM `item_template`
WHERE `entry` IN (...);

INSERT INTO `item_template`
(
    ...
)
VALUES
(...),
(...),
(...);

COMMIT;
```

---

# 6. DEFAULT ITEM QUALITY

When quality is unspecified:

```yaml
quality:
  default: epic
```

For fully randomized generation:

```yaml
quality_weights:
  poor: 0
  common: 0
  uncommon: 15
  rare: 30
  epic: 50
  legendary: 5
  artifact: 0
  heirloom: 0
```

Equivalent:

```text
Uncommon     15%
Rare         30%
Epic         50%
Legendary     5%
```

Do not generate Artifact or Heirloom quality randomly unless explicitly enabled.

---

# 7. QUALITY IDS

```yaml
quality_ids:
  poor: 0
  common: 1
  uncommon: 2
  rare: 3
  epic: 4
  legendary: 5
  artifact: 6
  heirloom: 7
```

---

# 8. DEFAULT LEVEL PROFILE

For unspecified endgame custom equipment:

```yaml
levels:
  required_level:
    default: 80

  item_level:
    default: 245
```

For random level-80 equipment:

```yaml
level_80_item_level_range:
  min: 200
  max: 277
```

Allow explicit generation through:

```text
284
```

when requested for high-end Icecrown-tier equipment.

Do not infer:

```text
RequiredLevel = ItemLevel
```

These fields are independent.

---

# 9. WOTLK ITEM LEVEL TIERS

Use these labels when translating natural-language power requests.

```yaml
item_level_tiers:

  early_heroic:
    min: 187
    max: 200

  entry_raid:
    min: 200
    max: 213

  naxx:
    min: 200
    max: 226

  ulduar:
    min: 219
    max: 239

  toc:
    min: 232
    max: 258

  early_icc:
    min: 251
    max: 258

  icc_normal:
    min: 251
    max: 264

  icc_heroic:
    min: 264
    max: 277

  heroic_lich_king:
    min: 277
    max: 284
```

These are generator selection bands.

When precise Blizzard authenticity matters, reference actual items rather than relying only on the tier label.

---

# 10. DEFAULT EQUIPMENT SLOT WEIGHTS

For random armor/accessory generation:

```yaml
slot_weights:
  head: 8
  neck: 6
  shoulders: 8
  back: 6
  chest: 10
  wrists: 6
  hands: 8
  waist: 8
  legs: 10
  feet: 8
  finger: 7
  trinket: 5
  weapon: 10
```

Weights are relative.

They do not need to total 100.

---

# 11. DEFAULT ITEM CATEGORY WEIGHTS

For unrestricted random equipment generation:

```yaml
category_weights:
  armor: 45
  weapon: 25
  jewelry: 15
  trinket: 10
  relic: 5
```

---

# 12. ARMOR TYPE WEIGHTS

```yaml
armor_type_weights:
  cloth: 20
  leather: 20
  mail: 20
  plate: 30
  shield: 10
```

When the selected slot cannot use an armor material, choose a compatible category instead.

Example:

```text
finger -> miscellaneous armor/ring
neck   -> miscellaneous armor
back   -> miscellaneous armor
```

---

# 13. ROLE WEIGHTS

For unrestricted level-80 generated equipment:

```yaml
role_weights:
  strength_dps: 18
  agility_dps: 15
  hunter: 10
  caster_dps: 18
  healer: 14
  tank: 15
  pvp: 5
  hybrid: 5
```

---

# 14. CLASS-SPECIFIC ROLE RESOLUTION

When the user names a class but not a role, use compatible possibilities.

```yaml
class_roles:

  warrior:
    - strength_dps
    - tank

  paladin:
    - strength_dps
    - tank
    - healer

  hunter:
    - hunter

  rogue:
    - agility_dps

  priest:
    - caster_dps
    - healer

  death_knight:
    - strength_dps
    - tank

  shaman:
    - agility_dps
    - caster_dps
    - healer

  mage:
    - caster_dps

  warlock:
    - caster_dps

  druid:
    - agility_dps
    - caster_dps
    - healer
    - tank
```

If the named specialization clearly establishes a role, use it.

Examples:

```text
Protection Warrior -> tank
Holy Paladin       -> healer
Frost DK           -> strength_dps
Balance Druid      -> caster_dps
Feral Cat          -> agility_dps
Feral Bear         -> tank
Restoration Shaman -> healer
```

---

# 15. ARMOR TYPE COMPATIBILITY

```yaml
role_armor_preferences:

  strength_dps:
    preferred:
      - plate

  agility_dps:
    preferred:
      - leather
    allowed:
      - mail

  hunter:
    preferred:
      - mail

  caster_dps:
    preferred:
      - cloth
    allowed:
      - leather
      - mail

  healer:
    preferred:
      - cloth
      - leather
      - mail
      - plate

  tank:
    preferred:
      - plate
    allowed:
      - leather
      - shield
```

Do not use this table to override a specifically requested class or armor type.

---

# 16. STATIC STAT LIMITS

```yaml
stats:
  min_per_item: 2
  max_per_item: 5

  absolute_max: 10

  duplicate_stats: false

  contiguous_slots_required: true
```

Default random distribution:

```yaml
stat_count_weights:
  2: 10
  3: 30
  4: 40
  5: 20
```

---

# 17. STAT TYPE IDS

```yaml
stat_types:
  health: 1

  agility: 3
  strength: 4
  intellect: 5
  spirit: 6
  stamina: 7

  defense_rating: 12
  dodge_rating: 13
  parry_rating: 14
  block_rating: 15

  melee_hit_rating: 16
  ranged_hit_rating: 17
  spell_hit_rating: 18

  melee_crit_rating: 19
  ranged_crit_rating: 20
  spell_crit_rating: 21

  melee_haste_rating: 28
  ranged_haste_rating: 29
  spell_haste_rating: 30

  hit_rating: 31
  crit_rating: 32

  resilience_rating: 35
  haste_rating: 36
  expertise_rating: 37

  attack_power: 38
  ranged_attack_power: 39

  mp5: 43
  armor_penetration: 44
  spell_power: 45
  health_regen: 46
  spell_penetration: 47
  block_value: 48
```

Prefer combined:

```text
31 Hit Rating
32 Crit Rating
36 Haste Rating
```

for ordinary WotLK equipment.

---

# 18. ROLE STAT POOLS

## Strength DPS

```yaml
strength_dps:
  mandatory:
    - strength
    - stamina

  preferred:
    - crit_rating
    - hit_rating
    - haste_rating
    - expertise_rating
    - armor_penetration

  optional:
    - attack_power
```

---

## Agility DPS

```yaml
agility_dps:
  mandatory:
    - agility
    - stamina

  preferred:
    - crit_rating
    - hit_rating
    - haste_rating
    - expertise_rating
    - armor_penetration

  optional:
    - attack_power
```

---

## Hunter

```yaml
hunter:
  mandatory:
    - agility
    - stamina

  preferred:
    - crit_rating
    - hit_rating
    - haste_rating
    - armor_penetration

  optional:
    - attack_power
    - ranged_attack_power
```

---

## Caster DPS

```yaml
caster_dps:
  mandatory:
    - intellect
    - stamina

  preferred:
    - spell_power
    - hit_rating
    - crit_rating
    - haste_rating

  optional:
    - spirit
    - spell_penetration
```

---

## Healer

```yaml
healer:
  mandatory:
    - intellect
    - stamina

  preferred:
    - spell_power
    - haste_rating
    - crit_rating
    - spirit
    - mp5

  forbidden_by_default:
    - hit_rating
```

---

## Tank

```yaml
tank:
  mandatory:
    - stamina

  preferred:
    - strength
    - defense_rating
    - dodge_rating
    - parry_rating
    - expertise_rating
    - hit_rating

  shield_preferred:
    - block_rating
    - block_value
```

---

## PvP

```yaml
pvp:
  mandatory:
    - stamina
    - resilience_rating

  preferred:
    - strength
    - agility
    - intellect
    - spell_power
    - attack_power
    - crit_rating
    - haste_rating
    - hit_rating
    - spell_penetration
```

Primary stats must still match the intended role.

---

# 19. DEFAULT RAW STAT RANGES

These values are intended for custom-server range-based generation.

They are not replacements for reference-based balancing.

For level-80 epic items approximately within item level 200-264:

```yaml
raw_stat_ranges:

  strength:
    min: 40
    max: 160

  agility:
    min: 40
    max: 160

  intellect:
    min: 40
    max: 160

  spirit:
    min: 30
    max: 120

  stamina:
    min: 50
    max: 200

  defense_rating:
    min: 25
    max: 100

  dodge_rating:
    min: 25
    max: 100

  parry_rating:
    min: 25
    max: 100

  block_rating:
    min: 20
    max: 90

  block_value:
    min: 30
    max: 160

  hit_rating:
    min: 25
    max: 100

  crit_rating:
    min: 25
    max: 110

  haste_rating:
    min: 25
    max: 110

  expertise_rating:
    min: 20
    max: 90

  armor_penetration:
    min: 25
    max: 120

  attack_power:
    min: 80
    max: 320

  ranged_attack_power:
    min: 80
    max: 320

  spell_power:
    min: 50
    max: 180

  mp5:
    min: 10
    max: 50

  resilience_rating:
    min: 25
    max: 120

  spell_penetration:
    min: 10
    max: 50
```

---

# 20. ITEM LEVEL SCALING

When using raw ranges, scale them according to item level.

Use:

```yaml
item_level_scaling:
  baseline_item_level: 232
```

Suggested multiplier:

```text
multiplier = ItemLevel / 232
```

Example:

```text
ItemLevel 200:

200 / 232 = 0.862
```

A baseline value of:

```text
100 Strength
```

becomes approximately:

```text
86 Strength
```

before slot, quality, and randomness modifiers.

This is a generator approximation only.

Reference-based generation remains preferred for authentic itemization.

---

# 21. QUALITY POWER MULTIPLIERS

For range-based generation:

```yaml
quality_power_multiplier:
  poor: 0.55
  common: 0.70
  uncommon: 0.82
  rare: 0.92
  epic: 1.00
  legendary: 1.12
  artifact: 1.18
  heirloom: 1.00
```

Do not apply these multipliers when values are explicitly provided by the user.

---

# 22. SLOT STAT-BUDGET MULTIPLIERS

Use these only for approximate procedural balancing.

```yaml
slot_budget_multiplier:

  head: 1.00

  neck: 0.70

  shoulders: 0.80

  back: 0.65

  chest: 1.15

  wrists: 0.60

  hands: 0.80

  waist: 0.80

  legs: 1.10

  feet: 0.80

  finger: 0.70

  trinket: 0.85

  one_hand_weapon: 0.75

  two_hand_weapon: 1.10

  ranged_weapon: 0.90

  shield: 0.90

  held_offhand: 0.65

  relic: 0.50
```

These are relative generator weights.

Do not treat them as canonical Blizzard item-budget formulas.

---

# 23. STAT RANDOMIZATION VARIANCE

```yaml
variance:
  conservative:
    min_percent: -5
    max_percent: 5

  custom:
    min_percent: -10
    max_percent: 10

  wild:
    min_percent: -35
    max_percent: 50
```

Default:

```yaml
randomness: custom
```

---

# 24. REFERENCE ITEM SEARCH

For balanced items:

```yaml
reference_matching:
  enabled: true

  prioritize:
    - inventory_type
    - subclass
    - item_level
    - quality
    - role

  item_level_search_radius:
    initial: 3
    expanded: 10
    maximum: 25

  allow_cross_quality_reference: false

  allow_cross_slot_reference: false

  allow_cross_weapon_handedness: false
```

If no exact reference exists, broaden item level before broadening item type.

---

# 25. REFERENCE TRANSFORMATION

When using an existing item as a baseline:

```yaml
reference_transform:
  preserve:
    - approximate_total_power
    - slot_budget
    - armor_or_weapon_dps
    - durability_scale

  may_change:
    - stats
    - name
    - class_restrictions
    - sockets
    - binding
    - flavor_text

  do_not_copy_automatically:
    - spell_ids
    - random_properties
    - random_suffixes
    - disenchant_loot
    - set_membership
```

Effects and special IDs must be explicitly validated.

---

# 26. SOCKET GENERATION

```yaml
sockets:
  enabled: true

  max: 3

  count_weights:
    0: 45
    1: 35
    2: 17
    3: 3
```

Socket color weights:

```yaml
socket_color_weights:
  red: 40
  yellow: 35
  blue: 25
```

Meta:

```yaml
meta_socket:
  random_generation_enabled: true

  allowed_slots:
    - head

  chance_percent: 12
```

If a meta socket is selected:

```text
socketColor_1 = Meta
```

unless matching a verified reference item with another ordering.

---

# 27. SOCKET COLOR IDS

```yaml
socket_colors:
  none: 0
  meta: 1
  red: 2
  yellow: 4
  blue: 8
```

Socket fields must be contiguous.

---

# 28. SOCKET BONUS

```yaml
socket_bonus:
  generate_automatically: false
```

Do not invent socket bonus IDs.

Only assign a socket bonus when:

- Supplied by the user
- Copied from a verified item
- Explicitly found in compatible data

Otherwise:

```yaml
socketBonus: 0
```

---

# 29. WEAPON TYPE WEIGHTS

```yaml
weapon_type_weights:

  one_hand_sword: 12
  two_hand_sword: 12

  one_hand_axe: 10
  two_hand_axe: 10

  one_hand_mace: 10
  two_hand_mace: 8

  dagger: 10

  staff: 9

  polearm: 5

  fist_weapon: 4

  bow: 3
  gun: 2
  crossbow: 3

  wand: 2
```

---

# 30. WEAPON SPEED RANGES

Values are milliseconds.

```yaml
weapon_speed:

  dagger:
    min: 1400
    max: 2000

  fist_weapon:
    min: 1600
    max: 2700

  one_hand_sword:
    min: 1800
    max: 2800

  one_hand_axe:
    min: 1800
    max: 2800

  one_hand_mace:
    min: 1800
    max: 2800

  two_hand_sword:
    min: 3200
    max: 3800

  two_hand_axe:
    min: 3200
    max: 3800

  two_hand_mace:
    min: 3200
    max: 3800

  polearm:
    min: 3200
    max: 3800

  staff:
    min: 2800
    max: 3600

  bow:
    min: 2400
    max: 3200

  gun:
    min: 2400
    max: 3200

  crossbow:
    min: 2600
    max: 3400

  wand:
    min: 1400
    max: 2000
```

Reference-item speed should take priority when generating Blizzard-like equipment.

---

# 31. WEAPON DAMAGE SPREAD

When generating damage around a target average:

```yaml
weapon_damage:
  default_spread_percent: 10
```

Example:

```text
Average Damage = 700

10% spread = 70

Minimum = 630
Maximum = 770
```

Validate:

```text
minimum <= maximum
```

---

# 32. WEAPON DPS GENERATION

Default:

```yaml
weapon_dps:
  mode: reference_based
```

Fallback approximate level-80 epic DPS ranges:

```yaml
fallback_weapon_dps:

  item_level_200:
    one_hand:
      min: 125
      max: 150
    two_hand:
      min: 160
      max: 190

  item_level_232:
    one_hand:
      min: 150
      max: 180
    two_hand:
      min: 190
      max: 225

  item_level_245:
    one_hand:
      min: 165
      max: 195
    two_hand:
      min: 210
      max: 245

  item_level_264:
    one_hand:
      min: 180
      max: 215
    two_hand:
      min: 230
      max: 270

  item_level_277:
    one_hand:
      min: 195
      max: 230
    two_hand:
      min: 250
      max: 290
```

These are fallback procedural ranges only.

Always prefer actual comparable WotLK weapons when authenticity matters.

---

# 33. WEAPON DAMAGE SCHOOL

```yaml
damage_school:
  default: physical
```

IDs:

```yaml
damage_school_ids:
  physical: 0
  holy: 1
  fire: 2
  nature: 3
  frost: 4
  shadow: 5
  arcane: 6
```

Elemental damage generation:

```yaml
random_elemental_weapon_damage:
  enabled: false
```

---

# 34. ARMOR GENERATION

```yaml
armor:
  mode: reference_based
```

Reference selection must match:

```text
slot
armor subclass
approximate item level
quality
```

Fallback procedural armor should only be used when no suitable reference exists.

Do not assign armor based only on item quality.

---

# 35. SHIELD GENERATION

```yaml
shield:
  enabled: true

  roles:
    - tank
    - healer
    - caster_dps

  armor_mode: reference_based
  block_mode: reference_based
```

Tank shield stat priority:

```yaml
tank_shield_priority:
  - stamina
  - defense_rating
  - dodge_rating
  - parry_rating
  - block_rating
  - block_value
  - strength
```

Caster/healer shields should not inherit physical tank stats unless intentionally hybridized.

---

# 36. SPELL EFFECT GENERATION

```yaml
item_spells:
  enabled: true

  random_generation_enabled: false

  max_spell_slots: 5

  allow_unverified_spell_ids: false
```

Effects may only be attached when a valid spell ID is known.

Accepted sources:

```text
user-provided spell ID
verified WotLK spell
known existing item
known custom spell
```

Do not create a fake spell ID to satisfy a theme.

---

# 37. RANDOM PROC SETTINGS

Random procs are disabled by default because spell IDs require validation.

```yaml
random_procs:
  enabled: false

  chance_per_item_percent: 10

  trigger_weights:
    on_equip: 35
    chance_on_hit: 35
    use: 30
```

Enabling this setting does not permit hallucinated spell IDs.

It permits choosing from a validated spell pool.

---

# 38. VALIDATED SPELL POOLS

Optional server-specific pools may be defined here:

```yaml
validated_spell_pools:

  melee_proc: []

  caster_proc: []

  healer_proc: []

  tank_proc: []

  on_use_melee: []

  on_use_caster: []

  on_use_healer: []

  on_use_tank: []
```

Until IDs are populated:

```text
DO NOT RANDOMLY GENERATE ITEM SPELLS
```

---

# 39. DISPLAY ID GENERATION

```yaml
appearance:
  mode: verified_reference

  random_unverified_display_ids: false

  reuse_reference_item_display: true

  allow_user_supplied_display_id: true
```

Appearance priority:

```text
1. Explicit user item/model reference
2. Existing comparable WotLK item
3. Curated display-ID pool
4. Mark unresolved
```

Never choose arbitrary numbers.

---

# 40. CURATED APPEARANCE POOLS

Optional server-specific pools:

```yaml
appearance_pools:

  plate_head: []
  plate_shoulders: []
  plate_chest: []
  plate_hands: []
  plate_legs: []
  plate_feet: []

  mail: []
  leather: []
  cloth: []

  one_hand_sword: []
  two_hand_sword: []
  one_hand_axe: []
  two_hand_axe: []
  one_hand_mace: []
  two_hand_mace: []
  dagger: []
  staff: []
  polearm: []
  bow: []
  gun: []
  crossbow: []

  shield: []
  cloak: []
```

Pool values should contain either:

```text
known item entries
```

or:

```text
validated display IDs
```

The generator must know which type is stored.

---

# 41. DEFAULT BINDING

```yaml
binding:

  default_equipment: bind_on_equip

  raid_quality_epic: bind_on_pickup

  legendary: bind_on_pickup

  leveling_green: bind_on_equip

  leveling_blue: bind_on_equip
```

IDs:

```yaml
bonding_ids:
  none: 0
  bind_on_pickup: 1
  bind_on_equip: 2
  bind_on_use: 3
  quest: 4
```

---

# 42. CLASS RESTRICTIONS

Default:

```yaml
restrictions:
  allowable_class: -1
  allowable_race: -1
```

Only restrict by class when:

- The user asks
- The generated item is class-specific
- The theme explicitly calls for it
- A relic requires it
- A set is intentionally class-specific

---

# 43. CLASS MASKS

```yaml
class_masks:
  warrior: 1
  paladin: 2
  hunter: 4
  rogue: 8
  priest: 16
  death_knight: 32
  shaman: 64
  mage: 128
  warlock: 256
  druid: 1024
```

Combine by bitwise OR or equivalent additive mask construction.

---

# 44. ACCOUNT BINDING

```yaml
account_bound:
  enabled_by_default: false

  item_flag: 134217728
```

When adding this flag, combine it with existing `Flags`.

Do not overwrite other bits.

---

# 45. PRICE GENERATION

```yaml
prices:
  mode: reference_based

  buy_count: 1

  sell_price_enabled: true
  buy_price_enabled: true

  buy_to_sell_ratio:
    min: 3
    max: 5
```

All stored values are copper.

Fallback random level-80 epic sell price:

```yaml
fallback_sell_price:
  min_gold: 5
  max_gold: 25
```

Convert to copper before writing SQL.

---

# 46. DURABILITY

```yaml
durability:
  mode: reference_based
```

Do not use one universal durability value.

Determine from:

```text
slot
weapon type
armor type
reference item
```

Accessories without durability should remain consistent with known WotLK examples.

---

# 47. DISENCHANTING

```yaml
disenchanting:
  automatic_generation: false

  copy_from_reference: false

  require_verified_disenchant_id: true
```

Do not invent:

```text
DisenchantID
```

or disenchant loot data.

---

# 48. RANDOMPROPERTY

```yaml
random_property:
  enabled: false
```

Use:

```yaml
RandomProperty: 0
RandomSuffix: 0
```

for procedurally generated static-stat equipment unless requested otherwise.

---

# 49. NAMING SETTINGS

```yaml
names:
  generate: true

  avoid_duplicates: true

  prefer_unique_names_for_legendary: true

  allow_apostrophes: true

  maximum_attempts_to_avoid_duplicate: 20
```

---

# 50. NAMING STRUCTURES

Weights:

```yaml
name_patterns:

  adjective_noun: 20

  noun_of_suffix: 20

  adjective_noun_of_suffix: 10

  possessive_noun: 15

  unique_proper_name: 20

  title_style: 15
```

Examples:

```text
Runebound Greatsword

Crown of the Frozen Watch

Ashen Defender's Greaves

The Hollow Oath

Dreadfang

Winter's Rebuke

Bulwark of Silent Snow
```

---

# 51. DEFAULT THEMES

For unrestricted WotLK generation:

```yaml
theme_weights:

  scourge: 15
  frost: 15
  titan: 10
  dragon: 10
  shadow: 10
  holy: 8
  arcane: 8
  nature: 6
  dwarven: 5
  vrykul: 5
  nerubian: 4
  blood: 4
```

Themes affect:

```text
name
flavor text
appearance selection when possible
spell pool selection when enabled
```

Themes must not automatically add elemental damage.

---

# 52. FLAVOR TEXT

```yaml
flavor_text:
  enabled: true

  chance_percent: 35

  max_words: 14

  comedy_enabled: false
```

Example:

```text
"It still carries the chill of Icecrown."
```

Avoid long lore paragraphs in `description`.

---

# 53. LEGENDARY GENERATION

```yaml
legendary:
  random_generation_enabled: true

  default_weight: 5

  require_unique_name: true

  special_effect_required: false

  appearance_should_be_distinct: true

  default_binding: bind_on_pickup
```

A Legendary does not require a fabricated proc.

A powerful stat-only Legendary is preferable to one with a fake spell.

---

# 54. TRINKETS

Random trinket generation requires additional caution because many WotLK trinkets derive most of their identity from spell effects.

```yaml
trinkets:
  enabled: true

  allow_stat_only: true

  random_spell_effects: false

  prefer_verified_reference_effects: true
```

If no valid effect exists, generate:

```text
stat-only trinket
```

or clearly state:

```text
Effect requires a verified spell ID.
```

---

# 55. RELICS

```yaml
relics:
  enabled: true

  require_class_compatibility: true

  random_generation_weight: 5
```

Mappings:

```yaml
relic_types:
  libram:
    class: paladin

  idol:
    class: druid

  totem:
    class: shaman

  sigil:
    class: death_knight
```

Do not generate a Death Knight Libram or Paladin Sigil unless intentionally requested.

---

# 56. SET GENERATION

```yaml
sets:
  maintain_theme: true
  maintain_quality: true
  maintain_role: true
  maintain_armor_type: true
  maintain_required_level: true

  item_level_variance:
    min: -0
    max: 0

  preserve_name_family: true

  identical_stats_across_slots: false
```

Recommended standard armor set slots:

```yaml
default_set_slots:
  - head
  - shoulders
  - chest
  - hands
  - legs
```

Extended set:

```yaml
extended_set_slots:
  - head
  - shoulders
  - chest
  - wrists
  - hands
  - waist
  - legs
  - feet
```

---

# 57. SET SLOT POWER

Use slot budget multipliers.

Example:

```text
Chest > Wrists

Legs > Waist

Head > Hands
```

Do not copy:

```text
+100 Strength
+120 Stamina
+80 Crit
```

onto every piece.

---

# 58. BATCH GENERATION

```yaml
batch:
  default_count: 1

  maximum_recommended_count: 500

  allow_larger_batches: true

  use_single_insert_statement: true

  use_transaction: true

  include_summary_table: true
```

For very large outputs, SQL may be divided into logical sections.

Example:

```text
Weapons
Plate
Mail
Leather
Cloth
Accessories
```

while remaining transaction-safe.

---

# 59. RANDOM GENERATOR DEFAULT PROFILE

When the user says only:

> Generate random level 80 gear.

Use approximately:

```yaml
default_random_level_80:

  required_level:
    min: 80
    max: 80

  item_level:
    min: 200
    max: 264

  quality_weights:
    uncommon: 5
    rare: 30
    epic: 60
    legendary: 5

  stat_count:
    min: 3
    max: 5

  sockets:
    min: 0
    max: 2

  binding:
    bind_on_equip: 60
    bind_on_pickup: 40
```

---

# 60. LEVELING GEAR PROFILE

When generating general leveling equipment:

```yaml
leveling:

  quality_weights:
    uncommon: 60
    rare: 35
    epic: 5

  legendary_enabled: false

  required_level_variance: 0

  stats:
    min: 1
    max: 4

  sockets:
    enabled_below_level_60: false

  binding:
    default: bind_on_equip
```

---

# 61. ENDGAME RAID PROFILE

```yaml
endgame_raid:

  required_level: 80

  item_level:
    min: 232
    max: 284

  quality_weights:
    rare: 5
    epic: 90
    legendary: 5

  stats:
    min: 3
    max: 5

  sockets:
    enabled: true

  binding:
    default: bind_on_pickup
```

---

# 62. ICC PROFILE

When the user says:

```text
ICC gear
Icecrown gear
ICC-level
```

use:

```yaml
icc:

  required_level: 80

  item_level_weights:
    251: 10
    258: 25
    264: 30
    271: 20
    277: 12
    284: 3

  quality:
    epic: 98
    legendary: 2

  balance_mode: reference_based
```

Do not treat item level 284 as ordinary random ICC gear.

---

# 63. OVERPOWERED PROFILE

Activated only when the user explicitly asks for:

```text
overpowered
OP
ridiculous
god item
GM gear
broken item
```

Configuration:

```yaml
overpowered:

  reference_budget_enforced: false

  stat_multiplier:
    min: 1.5
    max: 5.0

  maximum_static_stats: 10

  socket_limit: 3

  allow_cross_role_stats: true

  legendary_weight: 30

  preserve_user_values_exactly: true
```

Still enforce technical AzerothCore limits.

---

# 64. WILD PROFILE

Activated only when explicitly requested.

```yaml
wild:

  coherent_roles_required: false

  stat_multiplier:
    min: 0.5
    max: 8.0

  random_elemental_damage: true

  cross_role_stats: true

  unusual_weapon_speed: true

  unusual_socket_distribution: true

  legendary_weight: 25
```

Do not automatically activate Wild mode for normal random generation.

---

# 65. CONSERVATIVE PROFILE

```yaml
conservative:

  reference_variance_percent: 5

  coherent_roles_required: true

  random_spells: false

  random_elemental_damage: false

  quality_maximum: epic

  legendary_random_generation: false
```

Use when the user asks for:

```text
Blizzlike
vanilla-like
balanced
retail WotLK style
normal progression
```

---

# 66. DEFAULT CUSTOM PROFILE

This is the normal generator mode.

```yaml
custom:

  reference_variance_percent: 10

  coherent_roles_required: true

  random_spells: false

  random_elemental_damage: false

  legendary_random_generation: true

  legendary_weight: 5

  socket_generation: true

  flavor_text: true
```

---

# 67. ITEM SPELL TRIGGER IDS

```yaml
spell_triggers:
  use: 0
  on_equip: 1
  chance_on_hit: 2
  soulstone: 4
  use_no_delay: 5
  learn_spell: 6
```

Cooldowns are milliseconds.

---

# 68. PROC RATE

```yaml
proc:
  default_ppm: 1.0

  minimum_ppm: 0.2
  maximum_ppm: 5.0
```

Only use PPM when the spell/effect is designed for chance-on-hit behavior.

---

# 69. ITEM DISPLAY REQUIREMENTS

For automatically generated items:

```yaml
display_requirements:
  displayid_required_for_final_sql: true

  unresolved_display_behavior: use_reference_item

  allow_zero_displayid: false
```

Prefer cloning the appearance of a compatible item rather than emitting a visually broken item.

---

# 70. MATERIAL MAPPING

```yaml
materials:
  undefined: 0
  metal: 1
  wood: 2
  liquid: 3
  jewelry: 4
  chain: 5
  plate: 6
  cloth: 7
  leather: 8
```

Preferred equipment mapping:

```yaml
material_by_type:

  plate: 6
  mail: 5
  cloth: 7
  leather: 8

  ring: 4
  neck: 4
```

For weapons and unusual objects, prefer reference-item material values.

---

# 71. SHEATH VALUES

```yaml
sheath:
  two_handed: 1
  staff: 2
  one_handed: 3
  shield: 4
  enchanter_rod: 5
  offhand: 7
```

Reference known working items when uncertain.

---

# 72. ARMOR SUBCLASS IDS

```yaml
armor_subclasses:
  miscellaneous: 0
  cloth: 1
  leather: 2
  mail: 3
  plate: 4
  shield: 6
  libram: 7
  idol: 8
  totem: 9
  sigil: 10
```

---

# 73. WEAPON SUBCLASS IDS

```yaml
weapon_subclasses:
  one_hand_axe: 0
  two_hand_axe: 1
  bow: 2
  gun: 3
  one_hand_mace: 4
  two_hand_mace: 5
  polearm: 6
  one_hand_sword: 7
  two_hand_sword: 8
  staff: 10
  fist_weapon: 13
  miscellaneous: 14
  dagger: 15
  thrown: 16
  crossbow: 18
  wand: 19
  fishing_pole: 20
```

---

# 74. INVENTORY TYPE IDS

```yaml
inventory_types:

  none: 0
  head: 1
  neck: 2
  shoulder: 3
  shirt: 4
  chest: 5
  waist: 6
  legs: 7
  feet: 8
  wrists: 9
  hands: 10
  finger: 11
  trinket: 12
  one_hand: 13
  shield: 14
  ranged: 15
  back: 16
  two_hand: 17
  bag: 18
  tabard: 19
  robe: 20
  main_hand: 21
  off_hand_weapon: 22
  held_offhand: 23
  ammo: 24
  thrown: 25
  ranged_right: 26
  quiver: 27
  relic: 28
```

---

# 75. ITEM CLASS IDS

```yaml
item_classes:
  consumable: 0
  container: 1
  weapon: 2
  gem: 3
  armor: 4
  reagent: 5
  projectile: 6
  trade_goods: 7
  recipe: 9
  quest: 12
  key: 13
  miscellaneous: 15
  glyph: 16
```

---

# 76. GENERATED ITEM VALIDATION

Every item must pass all enabled checks:

```yaml
validation:

  unique_entry: true

  unique_name_within_batch: true

  valid_class: true

  valid_subclass: true

  valid_inventory_type: true

  class_subclass_compatible: true

  subclass_inventory_compatible: true

  quality_valid: true

  required_level_valid: true

  item_level_valid: true

  max_10_stats: true

  contiguous_stats: true

  duplicate_stats_forbidden: true

  role_stats_coherent: true

  weapon_damage_valid: true

  weapon_speed_valid: true

  weapon_dps_checked: true

  socket_count_max_3: true

  contiguous_sockets: true

  spell_slots_max_5: true

  spell_ids_verified: true

  class_mask_valid: true

  race_mask_valid: true

  displayid_verified: true

  sql_strings_escaped: true

  column_value_counts_match: true
```

---

# 77. INVALID ITEM BEHAVIOR

```yaml
invalid_item_behavior:

  attempt_minor_repair: true

  maximum_repair_attempts: 3

  emit_after_failed_validation: false

  report_failure_reason: true
```

Examples of repairable problems:

```text
duplicate secondary stat
socket gap
damage minimum greater than maximum
incompatible random armor role
duplicate generated name
```

Examples that should normally stop generation:

```text
no available entry ID
unknown required spell ID
unresolvable appearance when one is mandatory
invalid user-provided subclass
requested item exceeds technical limits
```

---

# 78. USER-REQUEST CONFLICT HANDLING

If the user intentionally requests unusual behavior:

```text
"Make a cloth DK chest."
```

Do not automatically reject it.

Instead:

```text
1. Determine whether AzerothCore can technically represent it.
2. Preserve the explicit request.
3. Mention that the combination is non-standard.
4. Generate it if technically valid.
```

Technical restrictions are hard limits.

Blizzard itemization conventions are soft limits.

---

# 79. USER VALUE PRESERVATION

```yaml
user_overrides:

  preserve_explicit_stats: true

  preserve_explicit_quality: true

  preserve_explicit_item_level: true

  preserve_explicit_required_level: true

  preserve_explicit_weapon_speed: true

  preserve_explicit_damage: true

  preserve_explicit_sockets: true

  preserve_explicit_binding: true

  preserve_explicit_class_restrictions: true
```

Do not silently rebalance an intentional custom item.

---

# 80. RANDOM SEED

```yaml
random:
  seed: null
```

When the user supplies:

```text
seed = 12345
```

the generator must use deterministic selection for:

```text
quality
slot
role
stats
values
weapon type
weapon speed
sockets
names
themes
```

The same configuration and seed should reproduce the same batch.

---

# 81. DEFAULT RANDOM BATCH EXAMPLE

Request:

```text
Generate 25 random level 80 epics.
```

Resolve approximately to:

```yaml
count: 25

entry:
  allocate_from: 900000

required_level: 80

item_level:
  min: 213
  max: 264

quality:
  epic: 100

role:
  use_default_weights: true

slots:
  use_default_weights: true

stats:
  min: 3
  max: 5

sockets:
  use_default_weights: true

appearance:
  verified_reference: true

balance:
  reference_based: true
```

---

# 82. DEFAULT GENERATED ITEM OUTPUT

For every item provide:

```text
Name
Entry
Quality
Slot
Armor/Weapon Type
Role
Required Level
Item Level
Stats
Sockets
Weapon Damage/DPS if applicable
Appearance reference
Binding
```

Then provide SQL.

Then provide:

```text
.additem ENTRY
```

---

# 83. BATCH OUTPUT FORMAT

Example:

```text
ENTRY   NAME                         SLOT       ILVL   ROLE
900000  Runebound Greatsword         Two-Hand   264    Strength DPS
900001  Crown of Silent Winter       Head       251    Healer
900002  Band of the Fallen Watch     Finger     245    Tank
900003  Dreadfang                    Dagger      258    Agility DPS
```

Then provide a single executable SQL batch.

---

# 84. SERVER INTEGRATION DEFAULTS

Creating equipment does not automatically add it to gameplay systems.

```yaml
integration:

  add_to_vendor: false

  add_to_creature_loot: false

  add_to_gameobject_loot: false

  add_to_quest: false

  add_to_mail: false

  add_to_item_set: false
```

Only generate those SQL changes when requested.

---

# 85. LOOT GENERATION

When the user requests generated loot for a creature:

```yaml
loot:

  default_drop_chance: 5.0

  group_id: 0

  min_count: 1

  max_count: 1

  reference: 0
```

Do not modify loot tables unless requested.

For rare boss items, prefer user-defined or context-derived drop rates.

---

# 86. VENDOR GENERATION

```yaml
vendor:

  maxcount: 0

  incrtime: 0

  extendedcost: 0
```

Use unlimited stock by default unless otherwise requested.

---

# 87. CACHE AND RESTART NOTES

Default testing notes:

```yaml
testing_notes:

  mention_worldserver_restart: true

  mention_itemcache_for_changed_items: true
```

After changing item-template definitions:

```text
Restart worldserver.
```

If the client still displays old item data:

```text
Close WoW.
Delete the relevant itemcache.wdb.
Restart WoW.
```

---

# 88. CLIENT-ASSET POLICY

```yaml
client_assets:

  generate_new_models_via_sql: false

  generate_new_icons_via_sql: false

  generate_new_textures_via_sql: false

  allow_existing_asset_reuse: true
```

If custom client assets are requested, explicitly separate:

```text
SERVER SQL
```

from:

```text
CLIENT PATCH
```

---

# 89. SQL SCHEMA SAFETY

```yaml
schema_safety:

  use_statscount_column: false

  assume_legacy_trinity_schema: false

  explicit_stat_slots: true

  maximum_stat_slots: 10

  maximum_damage_slots: 2

  maximum_spell_slots: 5

  maximum_socket_slots: 3
```

Never insert obsolete schema fields simply because they appear in old guides.

---

# 90. STAT SLOT PACKING

Example three-stat item:

```text
stat_type1  = Strength
stat_value1 = 100

stat_type2  = Stamina
stat_value2 = 120

stat_type3  = Crit
stat_value3 = 70

stat_type4  = 0
stat_value4 = 0

...

stat_type10  = 0
stat_value10 = 0
```

Never generate:

```text
stat_type1 = Strength
stat_type2 = 0
stat_type3 = Crit
```

---

# 91. SOCKET PACKING

Example:

```text
socketColor_1 = Red
socketColor_2 = Yellow
socketColor_3 = 0
```

Never generate:

```text
socketColor_1 = Red
socketColor_2 = 0
socketColor_3 = Blue
```

unless reproducing a specifically verified item requiring that arrangement.

---

# 92. GENERATOR SAFETY PHILOSOPHY

When choosing between:

```text
A. A technically valid conservative item using known IDs
```

and:

```text
B. A more exciting item requiring guessed database/DBC values
```

always choose:

```text
A
```

Unknown IDs should be explicitly identified rather than fabricated.

---

# 93. DEFAULT PHILOSOPHY

The normal generator should produce items that feel like they plausibly belong in WotLK while still allowing the server to have its own identity.

Default priorities:

```text
1. Technical validity
2. User intent
3. Role coherence
4. WotLK-style itemization
5. Interesting variety
6. Reproducibility
7. Maintainable SQL
```

---

# 94. DEFAULT CONFIG SUMMARY

The normal server configuration is:

```yaml
defaults:

  core: AzerothCore
  expansion: WotLK
  client: 3.3.5a

  entry_range: 900000-999999

  generator_mode: reference_based
  randomness: custom

  default_required_level: 80
  default_item_level: 245
  default_quality: epic

  random_item_level:
    min: 200
    max: 264

  stats:
    min: 2
    max: 5

  sockets:
    min: 0
    max: 3

  random_spells: false
  elemental_weapon_damage: false

  default_binding: bind_on_equip

  appearance_mode: verified_reference

  sql_delete_before_insert: true
  sql_explicit_columns: true

  validation_required: true

  preserve_user_overrides: true
```

---

# 95. FINAL GENERATOR RULE

This configuration provides defaults.

It does not override explicit user intent.

The generator must always interpret requests using:

```text
USER REQUEST
      ↓
CONFIG DEFAULTS
      ↓
REFERENCE ITEM DATA
      ↓
VALIDATION
      ↓
FINAL ITEM
      ↓
SQL
```

The goal is to make requests as simple as:

```text
Generate me 20 random ICC weapons.
```

or:

```text
Make a level 80 epic Blood DK tank sword.
```

or:

```text
Generate 100 random items between ilvl 200 and 264 using entries 910000-910099.
```

without requiring the user to manually specify every AzerothCore database field.

When the user does specify exact values, those values become authoritative unless they exceed a hard technical limitation of AzerothCore or the WotLK client.