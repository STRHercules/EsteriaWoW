# Consolidated findings

This is the consolidated read-only result of the repository, server, SQL, client-package, and asset audit. No files were modified, and no build, database import/query, client launch, or live gameplay test was performed.

I distinguish:

- **Verified repository fact** — directly supported by source, SQL, CSV, static package contents, or documented files.
- **General 3.3.5a conclusion** — technical conclusion based on the normal WotLK client/server model contract.
- **Unresolved** — requires parsing the actual client binary/archive or live testing.

---

# 1. Overall verdict

## Half-Elf

A Half-Elf is feasible, but the exact requirement matters.

### Exact requirement: Human body and rig plus pointed ears

This is a **medium/high-effort custom model project**.

The correct approach is:

1. Duplicate the Human male and female player M2s.
2. Preserve the Human skeleton, animations, equipment attachments, and body proportions.
3. Integrate pointed ear geometry into the duplicated M2.
4. Bind the ear vertices to compatible Human head bones.
5. Rebuild every required SKIN LOD and verify geosets, attachments, UVs, and animation references.
6. Give the result a new client path, display IDs, race ID, customization rows, portraits, and UI identity.

A separate arbitrary ear M2 attached to a normal Human player model is **not** a proven standard 3.3.5 player-race mechanism. It would require a custom client/model attachment pipeline that has not been found in this project.

### Practical alternative: Blood Elf donor

A complete Blood Elf-derived Half-Elf is the safest practical implementation. Existing High Elf work proves the identity/model-reuse pattern.

However, it would not strictly satisfy:

- Human body proportions;
- Human UV layout;
- Human head topology;
- necessarily the full Human skeleton/attachment contract.

## Halfling

A Halfling is feasible, but the safest implementation depends on whether Human anatomy is mandatory.

### Exact requirement: Human anatomy uniformly scaled smaller

The best final design is a **duplicated, baked-scaled Human M2**:

- Human model and proportions;
- Human skeleton and animations;
- Human equipment relationship;
- new model path and IDs;
- geometry, bone pivots, and attachment points uniformly scaled.

This is more reliable than relying on runtime scale.

### Runtime scaling

Runtime/player scale is useful for a prototype, but is not sufficient as currently implemented:

- `Player::Create()` resets scale to `1.0f`;
- `Player::InitStatsForLevel()` resets it again;
- login in `PlayerStorage::LoadFromDB()` resets it again;
- player collision width uses player object size rather than only `CreatureModelData`.

Relevant code:

- `src/server/game/Entities/Player/Player.cpp:521`
- `src/server/game/Entities/Player/Player.cpp:2636-2661`
- `src/server/game/Entities/Player/PlayerStorage.cpp:5081-5121`
- `src/server/game/Entities/Player/Player.h:1100-1105`
- `src/server/game/Entities/Unit/Unit.cpp:13178-13195, 17145-17238`

A Gnome or Dwarf donor would be technically more robust, but would not preserve Human anatomy.

---

# 2. Current evidence and project state

## Client state is not verified

The documented working client is external:

```text
R:\Users\Zach\Downloads\World.of.Warcraft.3.3.5a.Truewow\
```

The repository says the client is not a clean unified distribution and that patch ordering, Worgoblin/ARAC data, and merged DBC/MPQ state remain unresolved (`README.md:239-280`).

The audit could not parse or directly read the external client binaries. The delegated audit had only static `glob`, `grep`, and `read` access. No binary parser was successfully executed.

Therefore:

- archive precedence is unresolved;
- active client DBC contents are unresolved;
- static package contents are not proof of active runtime behavior.

## Checked-in baseline DBC

`DBCs\ChrRaces.dbc` exists, but it was not directly parsed as binary.

Static documentation, CSV exports, and snapshot cross-checks suggest it is a 26-row Worgoblin-era baseline containing:

- IDs 1–26;
- legacy NPC identities around IDs 16–25;
- blank/unused ID 26.

That interpretation is **probable staged evidence**, not a verified binary read.

Do not attribute project SQL rows 27–28, pending rows 29–31, or Darkfallen 43/44 to that baseline binary.

## Static asset inventory

The corrected case-insensitive audit found:

### Patch-A loose tree

- 10,402 paths
- 2,718 M2 files
- 2,777 SKIN files
- 3,246 BLP files
- 639 animation files
- 38 other DBC/UI/Glue paths

Breakdown:

- Goblin: 2 M2, 8 SKIN, 1,007 BLP, 97 animations
- Worgen: 2 M2, 8 SKIN, 899 BLP, 102 animations
- WorgenWild: 2 M2, 8 SKIN, 899 BLP, 102 animations

WorgenWild is an alternate NPC/wild-body package, not a separate registry race.

### PlayableOgre

- 1,246 paths total
- 1,245 payload files plus receipt
- 561 M2
- 564 SKIN
- 66 BLP
- 22 animations

Most are item components and creature/NPC assets. Only a small `Character\Ogre` player subset exists. The package is donor/staging content, not an integrated playable race.

### PlayableTaunka

- 863 paths
- 1 M2
- 32 SKIN
- 709 BLP
- 103 animations
- only three relevant DBC files

The assets are Tauren-based:

```text
Non-HD model\Character\Tauren\Male
```

The package contains no decoded race-row values. Taunka flags, displays, faction, language, and playability remain unresolved.

### VulperaDBC

- 1,309 paths
- 6 M2
- 16 SKIN
- 975 BLP
- 288 animations

The package contains:

- PATCH-Y donor files;
- PATCH-C non-HD Vulpera;
- PATCH-C Vulpera HD;
- helmet DBCs.

This is donor/candidate evidence, not proof of active integration.

### High Elf

No dedicated body tree was found at:

```text
Character\HighElf
Character\Highelf
Character\BloodElf
```

The `_HeF/_HeM` files are item/head components, not a High Elf body.

Existing High Elf implementation is therefore Blood Elf model/customization reuse.

---

# 3. Race IDs and current race-contract conflicts

## SharedDefines and masks

`src/server/shared/SharedDefines.h:66-114` defines:

- IDs 1–28;
- Darkfallen Alliance 43;
- Darkfallen Horde 44.

`GetRaceMaskForRace()` maps:

```text
1..32 -> 1 << (race - 1)
43/44 -> 0x80000000
other -> 0
```

Consequences:

- IDs 1–31 are ordinary mask candidates in principle.
- ID 32 uses `0x80000000`, colliding with the Darkfallen high-bit convention.
- IDs above 32 are not normally representable.
- 43/44 are a special shared-mask implementation, not ordinary independent race IDs.

## IDs 29–31

IDs 29–31 appear only in pending SQL:

- `rev_1787850000003_races_29_30.sql`
  - 29 Kul Tiran
  - 30 Illidari
- `rev_1787850000015_alliance_illidari.sql`
  - 31 Alliance Illidari

They are not in the current registry’s ordinary playable list, which stops at 28 and then uses 43/44.

Therefore IDs 29–31 should be classified as:

> pending/reserved candidates requiring reconciliation, not current playable races and not automatically free.

## ID 14 conflict

ID 14 has multiple incompatible contracts:

1. Patch-A-era CSV:
   - Mag’har
   - displays 51/52
   - prefix `Mo`
   - client string `Maghar`

2. Project SQL mirror:
   - also Mag’har in `chrraces_dbc.sql`

3. Current Broken migration:
   - Broken
   - displays 60002/60003
   - prefix `Bk`
   - client string `Broken`

Relevant files:

- `modules/mod-worgoblin-high-elf/data/DBC/CSV from DBC/ChrRaces.csv`
- `modules/mod-custom-server/data/sql/db-world/updates/dbc/chrraces_dbc.sql`
- `modules/mod-custom-server/data/sql/db-world/updates/u_custom_server_2026_09_17_broken_race14_alignment.sql`
- `.agents/plans/broken-replacement/check.py`

This must be resolved before any new race is tested.

## Project registry versus proven runtime

`race_registry.json` describes IDs 1–28 and 43/44, but registry ownership is not proof of:

- active client files;
- active SQL import;
- current client selection;
- current server playability;
- correct display rows.

Several registry paths refer to absent or ignored external/staged asset roots.

---

# 4. Existing race implementations

## High Elf

Verified pattern:

- race identity is separate;
- player display IDs are Blood Elf displays 15476/15475;
- `CharSections` paths point to Blood Elf textures;
- hair/facial-hair rows are donor/remapped rows;
- no standalone High Elf player body was found.

Relevant evidence:

- `modules/mod-custom-server/data/sql/db-world/updates/dbc/chrraces_dbc.sql:86-90`
- `modules/mod-worgoblin-high-elf/data/DBC/CSV from DBC/ChrRaces.csv`
- `modules/mod-worgoblin-high-elf/modpaks/F-031_mod-azerothcore-high-elf/dbc/[BASE,F-031]_charsections.sql`
- `modules/mod-worgoblin-high-elf/merge-notes.md`
- `modules/mod-worgoblin-high-elf/README.md`

This is the best existing example for a donor-model custom race.

## Worgen, Goblin, Sethrak

These have dedicated player model assets:

- `Character\Worgen\`
- `Character\Goblin\`
- `Character\Sethrak\`

They demonstrate the higher-cost but cleaner approach:

- dedicated M2;
- SKIN;
- animation;
- texture;
- race-specific DBC;
- model/display IDs.

## Darkfallen

Darkfallen has dedicated assets under:

```text
NewModels\_Other\PlayableDarkfallen\Darkfallen\
```

The SQL migration creates:

- model IDs 3658/3659;
- display IDs 60028/60029;
- race IDs 43/44.

However, there is a client-string conflict:

- `darkfallen_race_pack.py` expects Alliance `Darkfallen` and Horde `DarkfallenHorde`;
- `u_custom_server_2026_09_21_00_darkfallen.sql` sets both `ClientFilestring` values to `Darkfallen`.

Darkfallen is therefore useful as an additive packaging example, but not a clean proof of current live integration.

---

# 5. How the 3.3.5 player model contract works

## Server-side flow

The relevant flow is:

```text
ChrRaces.dbc model_m/model_f
  -> ObjectMgr::LoadPlayerInfo()
  -> PlayerInfo::displayId_m/displayId_f
  -> Player::InitDisplayIds()
  -> Unit::SetDisplayId()
  -> UNIT_FIELD_DISPLAYID
```

Relevant locations:

- `src/server/game/Globals/ObjectMgr.cpp:4385-4432`
- `src/server/game/Entities/Player/Player.cpp:485-541`
- `src/server/game/Entities/Player/Player.cpp:10878-10902`

## Creature model path limitation

The server does not resolve the actual M2 path from the SQL `ModelName` column.

`CreatureDisplayInfoEntry` stores:

- display ID;
- model ID;
- extended display ID;
- scale.

`CreatureModelDataEntry` stores:

- model ID;
- flags;
- scale;
- collision width;
- collision height;
- mount height.

The model path fields are commented out in:

- `src/server/shared/DataStores/DBCStructure.h:747-763`
- `src/server/shared/DataStores/DBCStructure.h:801-829`

The DBC formats are:

- `CreatureDisplayInfofmt` at `DBCfmt.h:39`
- `CreatureModelDatafmt` at `DBCfmt.h:42`

Thus the client must contain a coherent:

```text
CreatureDisplayInfo.dbc
 -> ModelID
CreatureModelData.dbc
 -> client model path
Character\...\*.m2
```

A SQL `ModelName` value alone does not make the model available.

## M2/SKIN coupling

`tools/playable_race_pack.py:642-681` confirms the expected package relationship:

- male/female M2;
- all required SKIN files;
- animation files;
- WotLK model validation;
- M2 version checking.

SKIN files are coupled to the exact M2 vertex/index/batch structure. Copying a donor SKIN without matching the edited M2 is unsafe.

---

# 6. Half-Elf model findings

## Human reuse alone cannot create ears

A Human race row can reuse:

- Human display IDs;
- Human `CharSections`;
- Human hair;
- Human facial-hair rows;
- Human equipment.

But DBC labels and geoset rows do not manufacture new head geometry.

A pointed-ear Half-Elf therefore requires one of:

### Option A — integrate ears into Human M2

Recommended for the strict requirement.

Required work:

- duplicate Human M2;
- add ear vertices/triangles;
- bind them to Human head bones;
- rebuild SKIN LODs;
- preserve Human animations;
- verify geoset IDs and visibility;
- add or rebase texture slots;
- preserve hand/head/weapon/cape attachments.

The ear donor’s original bone indices cannot simply be copied into the Human model. The geometry must be rebound to the Human rig.

### Option B — use Blood Elf wholesale

Recommended practical solution if exact Human anatomy is negotiable.

Advantages:

- native pointed ears;
- complete animation/skeleton package;
- existing hair/facial/helmet ecosystem;
- proven High Elf reuse pattern;
- lower M2 risk.

Disadvantages:

- Blood Elf proportions differ from Human;
- Blood Elf UV layout differs;
- Human BLPs cannot be assumed compatible;
- Human equipment fit must still be tested if the model is changed.

### Option C — external ear attachment

Not recommended without a proven custom pipeline.

Risks:

- no standard generic player-ear attachment hook found;
- head positioning;
- geoset visibility;
- helmet hiding;
- LOD behavior;
- death/alternate animations;
- character-create versus world behavior;
- separate texture and alpha handling.

## Blood Elf versus Night Elf

### Blood Elf

Best donor/reference for a human-like Half-Elf.

It has:

- smaller pointed ears;
- closer human-like silhouette;
- coherent Blood Elf head/face/hair UVs;
- existing helmet and animation support.

### Night Elf

Better only if the desired result is:

- very long ears;
- more visibly Night Elf proportions;
- more exaggerated fantasy silhouette.

Using the entire Night Elf model is safer than copying only Night Elf ear geometry into Human, but it fails the requested Human-like result more substantially.

## Half-Elf non-model assets

A complete new race would need new or cloned rows/assets for:

- `ChrRaces`
- `CharBaseInfo`
- `CharSections`
- `CharStartOutfit`
- `NameGen`
- `BarberShopStyle`
- `CharHairGeosets`
- `CharacterFacialHairStyles`
- `CreatureDisplayInfo`
- `CreatureDisplayInfoExtra`
- `CreatureModelData`
- `HelmetGeosetVisData`
- `SkillRaceClassInfo`
- `SkillLineAbility`
- race-mask SQL
- Glue strings/icons/portraits/backgrounds

Existing Human assets should be reused through copied rows or new references, not overwritten.

---

# 7. Halfling model and scaling findings

## Three distinct scale systems

Do not treat these as interchangeable:

1. `CreatureDisplayInfo.scale`
2. `CreatureModelData.Scale`
3. player object scale via `UNIT_FIELD_SCALE_X`/`SetObjectScale()`

For non-player units, model-data and display scale contribute to collision calculations (`Unit.cpp:17145-17238`).

For players:

- scale is reset in creation/stat/login paths;
- bounding radius and combat reach are separately updated;
- player collision width returns `GetObjectSize()` directly.

## Baked Human scaling

Best fit for the requested anatomy.

A baked model requires scaling:

- mesh vertices;
- bone pivots where appropriate;
- attachment points;
- head/hand/weapon/cape locations;
- possibly mount-related anchors.

Uniform vertex scaling preserves UV coordinates, but it does not automatically make:

- helmets fit;
- shoulder armor fit;
- capes fit;
- vehicle seats fit;
- mounts sit correctly;
- collision and combat reach correct.

## Runtime scale

Suitable for a prototype only unless persistent native-scale support is implemented.

It must be reapplied after:

- character creation;
- database login;
- `InitStatsForLevel`;
- level changes;
- display changes;
- transformations;
- mount/dismount;
- shapeshift/form changes.

## Target height

“Approximately Dwarf height” must become a numeric design requirement.

The project needs to define:

- target male/female height;
- ratio to Human;
- ratio to Dwarf;
- whether eye height or feet-to-head height is authoritative;
- desired collision height;
- desired combat reach.

---

# 8. Customization and geoset findings

## `CharSections`

The server does not retain texture paths. It indexes only race/gender/generation/type/color:

- `src/server/shared/DataStores/DBCStructure.h:646-656`
- `src/server/game/DataStores/DBCStores.cpp:297-300, 889-898`

The client must receive the complete patched `CharSections.dbc` and BLP paths.

`Player::Create()` explicitly contains a TODO that skin, face, hair, and facial-hair values should be validated, but they are currently stored as raw packet values (`Player.cpp:485-490, 554-560`).

## Hair and facial hair

`CharHairGeosets.dbc` and `CharacterFacialHairStyles.dbc` are client appearance tables in this project. The server has no standard stores/loader for them.

Therefore:

- client customization rows are mandatory;
- server does not guarantee that every geoset exists;
- testing must cover every hairstyle, facial-hair style, face, and color.

## UVs and BLPs

A donor model’s UV atlas cannot be assumed to match another race’s BLPs.

For a Human-based Half-Elf:

- Human-compatible body/face BLPs are preferable;
- integrated ears need compatible UVs;
- new ear textures may require new BLPs;
- face/hair/facial-hair sections must be tested on all customization combinations.

For a Blood Elf-based Half-Elf:

- use Blood Elf-compatible UVs and texture sections;
- do not blindly substitute Human textures.

---

# 9. Helmets, equipment, mounts, and vehicles

## Helmets

The staged client disassembly notes in `.agents/plans/races-9-port/races-9-port.PLAN.md:527-583` identify race-prefix head component lookup using forms such as:

```text
Item\ObjectComponents\Head\<stem>_<ClientPrefix><M/F>.mdx
```

Attachment ID 11 is the important head anchor (`:596-600, 703-728`).

A new race therefore requires:

- a new or deliberately reused `ClientPrefix`;
- compatible male/female head components;
- helmet geoset visibility;
- correct attachment 11;
- ear visibility tests;
- no clipping/floating under helmets.

The current `_HeF/_HeM` files are High Elf-style item components, not a High Elf body model.

## General equipment

Test:

- cloth, leather, mail, plate;
- shoulders;
- cloaks;
- capes;
- shields;
- two-handed weapons;
- bows/guns;
- sheathed weapons;
- transmogrified items;
- all genders.

A Human-based Half-Elf should have the lowest equipment risk if the Human body and attachment contract are preserved.

## Mounts and vehicles

A smaller or edited model requires validation of:

- mount attachment height;
- mount seat position;
- mounted collision;
- flying mount position;
- vehicle seat position;
- vehicle camera;
- spell/projectile attachments;
- corpse/death position.

`CreatureModelData.MountHeight` affects collision calculations, but it does not automatically fix player visual seating or vehicle attachment positions.

---

# 10. AzerothCore creation and persistence findings

## Character creation

`WorldSession::HandleCharCreateOpcode()` reads:

- name;
- race;
- class;
- gender;
- skin;
- face;
- hairstyle;
- hair color;
- facial hair;
- outfit ID.

See `src/server/game/Handlers/CharacterHandler.cpp:265-279`.

It validates:

- class existence;
- race existence;
- expansion;
- disabled race mask;
- disabled class mask;
- name;
- Death Knight restrictions.

It does not fully validate customization against DBC appearance rows.

`Player::Create()` then requires a valid race/class `PlayerInfo` (`Player.cpp:485-502`).

## Character enumeration

`Player::BuildEnumData()` rejects a saved character with no valid race/class `PlayerInfo` (`Player.cpp:1157-1207`).

## Login

`PlayerStorage::LoadFromDB()` restores:

- race;
- class;
- gender;
- persistent team;
- customization fields;
- scale state.

It resets object scale at login (`PlayerStorage.cpp:5081-5121`).

## Class combinations

Class availability is controlled across:

- `playercreateinfo`
- `playercreateinfo_item`
- `playercreateinfo_skills`
- `playercreateinfo_spell_custom`
- `playercreateinfo_cast_spell`
- `playercreateinfo_action`
- `player_race_stats`
- `CharBaseInfo.dbc`
- `CharStartOutfit.dbc`

`ObjectMgr::LoadPlayerInfo()` dynamically creates race/class entries and populates stats, skills, spells, actions, and start data (`ObjectMgr.cpp:4350-4909`).

Every intended class needs:

- valid start location;
- valid stats;
- valid class/race `PlayerInfo`;
- starter outfit;
- skills;
- spells;
- actions;
- client class-selection support.

## Packets

The ordinary 3.3.5 character-create and character-enumeration packets already carry race and customization fields. A normal new race ID does not require a new opcode protocol.

The limitation is consistency:

- the client must enumerate and send the race ID;
- the server must have `ChrRaces` and `PlayerInfo`;
- the client must resolve the display/model;
- the saved race must load later.

---

# 11. Items, spells, skills, languages, factions, and reputation

## Items

Item `AllowableRace` masks are validated and used by:

- `src/server/game/Globals/ObjectMgr.cpp:3541-3591`
- `src/server/game/Entities/Player/PlayerStorage.cpp:2397-2467`
- `src/server/game/AuctionHouse/AuctionHouseSearcher.cpp:672`

A new race requires review of:

- starter item masks;
- armor restrictions;
- faction flags;
- weapon/shield use;
- auction filtering;
- transmog filtering;
- head-component assets.

## Spells and skills

Race/class masks are used by:

- `SkillRaceClassInfo`
- `SkillLineAbility`
- `playercreateinfo_skills`
- `playercreateinfo_spell_custom`
- `playercreateinfo_cast_spell`

Relevant code:

- `ObjectMgr.cpp:4513-4707`
- `Player.cpp:12321-12357`
- `Player.cpp:12710-12736`

The existing custom-language migrations show that granting a spell without matching skill/race rows causes language learning or chat failure.

A new race needs explicit language policy and matching rows in every relevant table.

## Languages and race changes

`CharacterHandler.cpp:2200-2273` has stock-race-specific language cases for:

- Dwarf;
- Draenei;
- Gnome;
- Night Elf;
- Undead;
- Tauren;
- Troll;
- Blood Elf.

A new race will not automatically receive a race-specific language during race/faction change.

## Faction and team

`Player::TeamIdForRace()` uses `ChrRaces.TeamID` (`Player.cpp:6030-6047`).

`Player::SetFactionForRace()` uses `ChrRaces.FactionID` (`Player.cpp:6082-6107`).

The new race needs correct:

- `TeamID`;
- `FactionID`;
- Alliance/Horde field;
- item faction masks;
- quest masks;
- reputation masks.

## Reputation

Base reputation uses `Faction.dbc.BaseRepRaceMask`:

- `ObjectMgr.cpp:9699-9717`
- `ReputationMgr.cpp`

A new race may work with generic faction masks, but race-specific or faction-specific reputation rows need explicit widening.

## Taxi

`PlayerTaxi::InitTaxiNodesForLevel()` has race-specific cases only for stock races 1–11 (`PlayerTaxi.cpp:23-87`).

A new race receives team-wide taxi defaults but not a race-specific capital node unless the code is extended.

## Cinematics and starting zones

Starting positions come from `playercreateinfo` and are validated in `ObjectMgr.cpp:4380-4432`.

Race cinematics use `ChrRaces.CinematicSequence`, with first-login handling in `CharacterHandler.cpp:907-917`.

A new race can safely use cinematic sequence 0 initially, avoiding the need for a new cinematic camera contract.

---

# 12. Glue/UI findings

The current Glue implementation is not dynamically synchronized with the server registry.

`modules/mod-worgoblin-high-elf/data/patch-A.MPQ/Interface/GlueXML/CharacterCreate.lua` contains:

- `MAX_RACES = 15`;
- fixed race icon coordinates;
- fixed faction lists;
- ordinal/button-based race selection;
- race-specific model/background logic.

Additional hard-coded data exists in:

- `CharacterCreate.xml`
- `CharacterInfo.lua`
- `GlueParent.lua`
- `CharacterSelect.lua`

A new race requires:

- a race slot and layout;
- faction lists;
- race token;
- localized names;
- descriptions;
- racial ability text;
- creation icons;
- portraits;
- background models;
- ambience/fog/glow/light;
- character-select faction logic;
- possibly executable changes.

Portrait naming is handled by `tools/race_portrait_pack.py`, using:

```text
Interface\CharacterFrame\TemporaryPortrait-<Male|Female>-<ClientFileString>.blp
```

The current server/registry race count cannot be treated as proof that the client can display the same number of choices.

---

# 13. Current tooling findings

Available useful tooling includes:

- `tools/playable_race_pack.py`
- `tools/darkfallen_race_pack.py`
- `tools/race_portrait_pack.py`
- `tools/derive_playable_race_portraits.py`
- `tools/ascension_hd_migration.py`
- `tools/inspect_client_archive.py`
- `modules/mod-adaptive-autoattack/tools/lib/clientfs.py`
- StormLib/StormTools under `BinaryWork`

These tools can:

- merge/add DBC rows;
- rebase WDBC strings;
- package MPQ content;
- validate WotLK M2 versions;
- generate portraits;
- resolve archive priority.

They do **not** provide:

- Blender model authoring;
- generic M2 merging;
- automatic ear topology integration;
- automatic Human model scaling;
- automatic equipment/helmet fitting.

No verified `.blend`, Blender addon, dedicated M2 converter, or M2 authoring pipeline was found.

---

# 14. Major risks

| Risk | Severity | Finding |
|---|---:|---|
| Race-ID conflicts | Critical | Registry, baseline CSV, SQL overlays, pending SQL, and snapshots disagree. |
| ID 14 conflict | Critical | Mag’har and Broken contracts coexist. |
| Display-ID truncation | Critical | `PlayerInfo` stores display IDs as `uint16`; existing 3m IDs are invalid if applied. |
| Client archive precedence | Critical | Patch-C/Patch-X and other packages may shadow one another. |
| Half-Elf ear modeling | High | Requires real M2/SKIN geometry and bone work. |
| Human/Blood Elf UV mismatch | High | Textures cannot be assumed interchangeable. |
| Helmet compatibility | High | Prefix, geoset visibility, attachment 11, and item models must agree. |
| Halfling scale persistence | High | Player scale resets during lifecycle operations. |
| Player collision | High | Player width uses object size, not just CreatureModelData. |
| Language/race-change support | Medium/high | Existing code is stock-race-specific. |
| UI race count | High | Current Glue has 15 slots despite broader server data. |
| SQL/DBC startup integrity | High | Missing display/model rows can cause invalid models or startup failure. |
| Active-client proof | Critical | Actual archive stack and binaries were not available for validation. |

---

# 15. Recommended implementation order

No implementation should begin until the following sequence is completed.

## First: reconcile the contract

1. Extract/read the actual client archive stack.
2. Determine the winning copies of all race-related DBCs.
3. Resolve ID 14 Mag’har/Broken.
4. Determine whether IDs 27–28 are actually applied.
5. Reconcile pending 29–31 ownership.
6. Verify Darkfallen 43/44 separately.
7. Choose a genuinely unused race ID.
8. Reserve display/model IDs below 65,536.

## Second: prove a donor race

Create no new model yet. First prove a complete donor identity through:

- character creation;
- character select;
- world login;
- relog;
- both genders;
- multiple faces/hair styles;
- starter outfit;
- at least one class;
- model path resolution.

## Third: build the actual race model

### Half-Elf

- duplicate Human M2;
- integrate ears;
- rebuild SKIN;
- preserve Human rig/animations;
- test Human equipment;
- add new BLP/customization rows;
- add helmets and portraits.

Or, if exact Human anatomy is relaxed, use a complete Blood Elf donor.

### Halfling

- define exact scale;
- prototype runtime scale;
- decide on baked M2 scale;
- validate attachments, armor, camera, collision, combat reach, mounts, and vehicles.

## Fourth: integrate server/client data

Add and verify:

- `ChrRaces`
- `CreatureDisplayInfo`
- `CreatureDisplayInfoExtra`
- `CreatureModelData`
- `CharSections`
- `CharBaseInfo`
- `CharStartOutfit`
- `NameGen`
- `BarberShopStyle`
- hair/facial geosets
- `HelmetGeosetVisData`
- skills/spells/languages
- player creation data
- stats
- item masks
- faction/reputation masks
- taxi/race-change behavior

## Fifth: update Glue/UI

Add:

- race buttons;
- ordinal/faction lists;
- strings;
- icons;
- portraits;
- background models;
- lighting/fog/ambience;
- character-select handling;
- executable compatibility if required.

---

# Final findings

1. **A strict Human-based Half-Elf with pointed ears is feasible, but it requires genuine M2/SKIN authoring.**
2. **A separate external ear mesh is not a proven standard client solution.**
3. **Blood Elf is the best practical Half-Elf donor; Night Elf is better only for a longer-ear/Night-Elf-like result.**
4. **A Human-based Halfling should use a baked-scaled duplicate for a finished implementation.**
5. **Runtime scale alone is only a prototype because player scale resets and collision behavior are separate.**
6. **The project’s race data is fragmented and currently contradictory, especially ID 14.**
7. **IDs 29–31 are pending/unregistered, not current playable races, but must still be treated as reserved candidates until reconciled.**
8. **IDs 43/44 are already a special Darkfallen implementation and should not be reused.**
9. **The checked-in baseline client evidence appears to be a 26-row legacy/Worgoblin-era contract, but the binary was not directly parsed.**
10. **The existing High Elf implementation is Blood Elf reuse, not proof of a standalone High Elf body.**
11. **Existing asset counts are static/staged evidence, not proof of active client precedence.**
12. **No implementation should begin until the live client archive stack, race-ID ownership, display-ID ranges, and ID 14 conflict are resolved.**