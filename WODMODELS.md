# WoD Character Models and `Patch-Zz.mpq` Forensic Analysis

## Scope

This was a read-only investigation of:

- Donor client: `F:\Wrath of the Lich King 3.3.5a (wod models)`
- Esteria developer client: `G:\3.3.5a - Dev`
- Large donor archive: `G:\Patch-Zz.mpq`
- Esteria repository and its existing MPQ/DBC tooling

No client files, MPQs, executables, server code, SQL, or DBCs were modified during this investigation. The only new file created is this report.

## Executive summary

### WoD player models

The donor client is using a real 3.3.5a backport of the later player character models. The important piece is `Data\patch-x.mpq` plus locale DBC overrides in `Data\enUS\patch-enUS-x.mpq` and one companion table from `patch-enUS-w.mpq`.

The model conversion is not being performed by a special renderer DLL. The donor places converted WotLK-format M2/SKIN/ANIM/BLP assets at the original WotLK character paths such as:

```text
Character\Human\Male\HumanMale.m2
Character\Orc\Female\OrcFemale.m2
Character\NightElf\Male\NightElfMale.m2
```

The converted Human male model is an `MD20` M2 with version `0x108`, which is the 3.3.5-era M2 format expected by this client family.

`patch-x.mpq` contains replacements for all ten WotLK playable races, both sexes, including player and NPC model variants.

Replication in Esteria is highly feasible. However, copying the donor `patch-x.mpq` and locale patch as-is is not safe and would not reliably win load priority. Esteria already has higher-priority `patch-Z.MPQ` and `patch-enUS-Z.MPQ` archives that contain overlapping character assets and much larger customized DBCs. The correct approach is to merge the donor assets and only the required donor DBC rows into Esteria's existing highest-priority patch stack.

### `G:\Patch-Zz.mpq`

`Patch-Zz.mpq` is a separate modern-asset library. It is not the source of the donor client's WoD vanilla-race player models.

It contains 364,155 files and is dominated by modern item, world, creature, interface, dungeon, tileset, and environment assets. It contains Legion, Battle for Azeroth, and Shadowlands-era content, including Argus, Azerite assets, the Arbiter, Ardenweald, Oribos, and Torghast assets.

It has no `Character` top-level tree and no `DBFilesClient` tree.

Many of its assets have already been converted to WotLK-compatible formats. Verified examples include:

- Arbiter M2: `MD20`, version `0x108`
- Ardenweald arrow M2: `MD20`, version `0x108`
- Arathi WMO: WMO `MVER` 17

That makes it a very valuable donor library for Esteria. It should not be treated as a plug-and-play 22 GB client patch. Most new assets have no WotLK DBC row or map reference that would make the client use them automatically. Some paths also overlap existing WotLK/Esteria assets, so loading the whole archive at high priority could silently replace existing art.

The safest use is selective extraction/import of chosen models, textures, skins, animations, and WMOs into Esteria-owned paths and DBC IDs.

---

# 1. Donor client inventory

The donor client contains the normal 3.3.5a archive set plus two obvious custom root patches:

| Archive | Size | Role found during inspection |
|---|---:|---|
| `Data\patch-w.mpq` | 1,409,036,963 bytes | Large supporting HD/content archive. Missing a useful listfile, so many names cannot be reconstructed directly. |
| `Data\patch-x.mpq` | 895,581,412 bytes | Dedicated playable-character HD/WoD model package. |
| `Data\enUS\patch-enUS-w.mpq` | 1,025,484 bytes | Companion DBC package, including `CreatureDisplayInfoExtra.dbc`. |
| `Data\enUS\patch-enUS-x.mpq` | 546,120 bytes | Higher-priority character DBC package. |

The important distinction is that `patch-x.mpq` is extremely focused.

Its top-level contents are:

- `Character`: 12,675 entries
- `Textures`: 26 entries
- MPQ metadata entries

File counts observed in `patch-x.mpq`:

- 40 M2 files
- 161 SKIN files
- 1,926 ANIM files
- 10,467 BLP files
- 10,302 BLP files matching the `_HD.blp` naming pattern

There is no `Character\Human2` style indirection in this package. The models replace the old paths directly.

## 1.1 Playable M2 coverage

The package includes the following player/NPC M2 families:

- Human male/female
- Orc male/female
- Dwarf male/female
- Night Elf male/female
- Scourge male/female
- Tauren male/female
- Gnome male/female
- Troll male/female
- Blood Elf male/female
- Draenei male/female

For most races there are both normal and `NPC` M2 variants.

Example paths:

```text
Character\Human\Male\HumanMale.m2
Character\Human\Male\HumanMaleNPC.M2
Character\Human\Female\HumanFemale.m2
Character\Orc\Male\OrcMale.m2
Character\Dwarf\Female\DwarfFemale.m2
Character\Bloodelf\MALE\BloodElfMale.m2
Character\Draenei\Female\DraeneiFemale.m2
```

The Human male donor model is:

- Size: 10,294,888 bytes
- M2 magic: `MD20`
- M2 version: `0x108`
- SHA-256: `2d47d15897b2922816011630797bc80ef348cc020b7b64e454825b84b73e8cbe`

This is a converted/backported model, not a raw modern-retail model being interpreted by a modern renderer.

---

# 2. How the donor client actually makes the WoD models work

The donor uses four cooperating mechanisms.

## 2.1 It replaces the original character model paths

The converted M2 files use the same logical paths that WotLK already expects.

For example, the donor `CreatureModelData.dbc` still resolves Human male model ID 49 to:

```text
Character\Human\Male\HumanMale.mdx
```

The MPQ supplies the converted model at the corresponding `.m2` path.

This is why the donor does not need new playable race IDs or a rewritten `ChrRaces.dbc` just to make Human/Orc/etc. use the new geometry.

## 2.2 It supplies matching SKIN files

The package includes the model skin partitions expected beside each model, such as:

```text
Character\Human\Male\HumanMale00.skin
Character\Human\Male\HumanMale01.skin
Character\Human\Male\HumanMale02.skin
Character\Human\Male\HumanMale03.skin
```

The exact number varies by race/model.

These files are essential. Copying only the `.m2` is not sufficient.

## 2.3 It supplies converted animation and texture dependencies

The archive contains 1,926 `.anim` files and over ten thousand character BLPs.

A large portion of the textures use `_HD.blp` names. These are part of the later-model character texture/customization pipeline.

The character model package therefore needs to be treated as a dependency set, not as forty isolated M2 files.

## 2.4 It overlays character/display DBCs

`patch-enUS-x.mpq` contains exactly:

```text
DBFilesClient\CharSections.dbc
DBFilesClient\CreatureDisplayInfo.dbc
DBFilesClient\CreatureModelData.dbc
DBFilesClient\EmotesTextSound.dbc
```

`patch-enUS-w.mpq` contains:

```text
DBFilesClient\CharSections.dbc
DBFilesClient\CreatureDisplayInfo.dbc
DBFilesClient\CreatureDisplayInfoExtra.dbc
DBFilesClient\CreatureModelData.dbc
```

Because X is later than W in the normal patch suffix chain, the effective donor stack uses the X copies for the tables X contains, while `CreatureDisplayInfoExtra.dbc` remains supplied by W.

The donor does not override `ChrRaces.dbc` in either W or X.

That is another strong indication that this is an in-place model/customization replacement for the existing WotLK races.

---

# 3. DBC changes found in the donor

The donor DBCs are not just stock WotLK tables repackaged under a new archive name.

## 3.1 Base versus donor table shapes

Base `locale-enUS.MPQ`:

| Table | Rows | Fields | Record bytes |
|---|---:|---:|---:|
| `CharSections` | 8,915 | 10 | 40 |
| `CreatureDisplayInfo` | 21,171 | 16 | 64 |
| `CreatureModelData` | 1,046 | 26 | 104 |
| `CreatureDisplayInfoExtra` | 13,599 | 21 | 84 |
| `ChrRaces` | 21 | 69 | 276 |

Donor W locale patch:

| Table | Rows | Fields | Record bytes |
|---|---:|---:|---:|
| `CharSections` | 9,271 | 10 | 40 |
| `CreatureDisplayInfo` | 24,262 | 16 | 64 |
| `CreatureModelData` | 1,349 | 28 | 112 |
| `CreatureDisplayInfoExtra` | 15,475 | 21 | 84 |

Donor X locale patch:

| Table | Rows | Fields | Record bytes |
|---|---:|---:|---:|
| `CharSections` | 8,958 | 10 | 40 |
| `CreatureDisplayInfo` | 24,262 | 16 | 64 |
| `CreatureModelData` | 1,351 | 28 | 112 |

The donor's `CreatureModelData` is already using the 28-field, 112-byte extended layout that Esteria currently uses.

## 3.2 Existing playable display IDs remain the stock IDs

The base WotLK `ChrRaces.dbc` points the ten playable races at these male/female display IDs:

| Race ID | Race | Male display | Female display |
|---:|---|---:|---:|
| 1 | Human | 49 | 50 |
| 2 | Orc | 51 | 52 |
| 3 | Dwarf | 53 | 54 |
| 4 | Night Elf | 55 | 56 |
| 5 | Scourge | 57 | 58 |
| 6 | Tauren | 59 | 60 |
| 7 | Gnome | 1563 | 1564 |
| 8 | Troll | 1478 | 1479 |
| 10 | Blood Elf | 15476 | 15475 |
| 11 | Draenei | 16125 | 16126 |

The donor keeps this overall contract rather than inventing replacement race IDs.

For Human and Orc, the donor display rows still use model IDs 49 through 52. Human male model ID 49 still points at the normal Human path.

---

# 4. Does the donor require a special `Wow.exe` to render these models?

There is no evidence that it does.

I compared:

```text
F:\Wrath of the Lich King 3.3.5a (wod models)\Wow.exe
```

against the repository's known original executable:

```text
BinaryWork\Original Executable\Wow.exe
```

Both files are exactly 7,704,216 bytes.

Their SHA-256 hashes differ, but a byte comparison found only **two changed byte positions in the entire executable**.

## 4.1 Change 1: Large Address Aware

At PE file-header offset `0x126`, the byte changes from `0x03` to `0x23`.

This adds the PE `IMAGE_FILE_LARGE_ADDRESS_AWARE` characteristic (`0x20`).

That allows the 32-bit process to use a larger user-mode address space where the OS permits it. This is useful for a large HD-asset client, but it is not a new model renderer.

## 4.2 Change 2: branch in `ClientServices.cpp`

At file offset `0x2B1F48`, the donor changes:

```text
74 21    JE  ...
```

to:

```text
EB 21    JMP ...
```

The mapped code address is approximately `0x006B2B48` in the original image.

The nearby embedded source filename is:

```text
.\ClientServices.cpp
```

This branch selects between two ClientServices object construction paths. It is not located in the M2/skin/graphics rendering code identified during this analysis.

### Conclusion on the executable

The donor executable is effectively the normal 3.3.5a engine with LAA plus a one-byte ClientServices branch patch.

The actual WoD-model support is coming from converted 3.3.5-compatible assets plus DBC data, not from a modern renderer transplanted into `Wow.exe`.

Esteria does not need to replace its executable with the donor executable to reproduce this character-model behavior.

---

# 5. Esteria's current client state

Esteria is not a clean WotLK client. It already has a large custom patch stack and WarcraftXL-related extensions.

Relevant current archives include:

```text
Data\PATCH-A.MPQ
Data\Patch-C.MPQ
Data\Patch-D.MPQ
Data\Patch-E.MPQ
Data\Patch-F.MPQ
Data\Patch-G.MPQ
Data\Patch-O.mpq
Data\Patch-W.MPQ
Data\PATCH-X.MPQ
Data\Patch-Y.MPQ
Data\patch-Z.MPQ
Data\enUS\patch-enUS-Z.MPQ
```

It also has `common-3.MPQ` and DBC-continuation support.

## 5.1 Esteria's winning race/display DBCs already come from Z

Using the repository's own archive-priority logic, the current winning copies of the relevant DBCs come from:

```text
G:\3.3.5a - Dev\Data\enUS\patch-enUS-Z.MPQ
```

Observed current table shapes include:

| Table | Rows | Fields | Record bytes |
|---|---:|---:|---:|
| `ChrRaces` | 32 | 69 | 276 |
| `CharSections` | 417,188 | 10 | 40 |
| `CharHairGeosets` | 1,166 | 6 | 24 |
| `CharHairTextures` | 119 | 8 | 32 |
| `CharacterFacialHairStyles` | 3,539 | 8 | 32 |
| `BarberShopStyle` | 1,131 | 40 | 160 |
| `CreatureDisplayInfo` | 26,135 | 16 | 64 |
| `CreatureDisplayInfoExtra` | 22,477 | 21 | 84 |
| `CreatureModelData` | 1,602 | 28 | 112 |

This is why the donor locale DBC files must not be copied wholesale over Esteria.

They would throw away substantial existing custom race/display/appearance data.

## 5.2 Esteria already uses the donor-compatible `CreatureModelData` layout

Current Esteria `CreatureModelData` is already 28 fields / 112 bytes per record, matching the donor X/W layout.

More specifically, current Esteria model row 49 for Human male is field-equivalent to donor X row 49 and points at:

```text
Character\Human\Male\HumanMale.mdx
```

This is very good news. It means the low-level DBC layout needed by the donor pack is already present.

## 5.3 Esteria already overrides the same character model paths

Current `Data\patch-Z.MPQ` contains paths such as:

```text
Character\Human\Male\HumanMale.m2
Character\Orc\Male\OrcMale.m2
Character\Dwarf\Male\DwarfMale.m2
Character\Nightelf\Male\NightElfMale.m2
```

The current Esteria Human male model is not the same model as the donor WoD Human male.

Current Esteria Human male:

- Size: 1,934,354 bytes
- Version: `0x108`
- SHA-256: `386b43dc9278588e181e02c1d423d7d4f9fbbc714189348b0386b4129435033f`

Donor WoD Human male:

- Size: 10,294,888 bytes
- Version: `0x108`
- SHA-256: `2d47d15897b2922816011630797bc80ef348cc020b7b64e454825b84b73e8cbe`

Stock patch-3 Human male, for comparison:

- Size: 1,585,376 bytes
- SHA-256: `b22478c1ab8d1e9bb7542f686e60e4e665a510d11b5360109a3e9e46d5bf91d2`

So Esteria is already using a non-stock converted/custom Human model, but it is not the donor WoD model.

## 5.4 Exact path collision with the donor character package

`patch-x.mpq` contains 12,703 named entries.

Comparing its paths against Esteria's current `patch-Z.MPQ` found:

- 74 path overlaps including `(listfile)`
- 73 actual asset overlaps
- **0 of those 73 overlapping assets are byte-identical**

The collisions are overwhelmingly the playable character M2 and SKIN files.

Examples include:

```text
Character\Human\Male\HumanMale.m2
Character\Human\Male\HumanMale00.skin
Character\Human\Female\HumanFemale.m2
Character\Orc\Male\OrcMale.m2
Character\Dwarf\Male\DwarfMale.m2
Character\Nightelf\Female\NightElfFemale.m2
Character\Scourge\Male\SCOURGEMale.m2
Character\Tauren\Male\TaurenMale.m2
Character\Troll\Female\TrollFemale.m2
Character\Bloodelf\MALE\BloodElfMale.m2
```

This is a hard conflict, not a theoretical one.

### Consequence

Simply dropping the donor `patch-x.mpq` into Esteria as `patch-X.MPQ` will not reproduce the donor client.

Esteria's later `patch-Z.MPQ` already owns many of the same paths and will win the normal custom patch chain.

The donor assets need to be deliberately merged into the winning Esteria archive or the archive strategy needs to be changed in a controlled way.

---

# 6. Recommended WoD model replication strategy

This is the safest implementation path for a future implementation task. Nothing in this section was executed during this analysis.

## Phase A: make a precise dependency manifest

Build an inventory from donor `patch-x.mpq` containing:

- all 40 character M2 files
- all matching SKIN files
- all ANIM files referenced by those models
- all BLP dependencies
- all `_HD.blp` character customization textures
- the 26 `Textures` entries

Use the MPQ listfile as the authoritative source for names.

Do not pull anonymous `File000...` entries from `patch-w.mpq` unless a dependency proves they are needed.

## Phase B: merge root character assets into Esteria's winning patch

Use Esteria's existing StormLib tooling to create a staging copy of the current winning root archive.

Merge the complete donor `patch-x.mpq` character dependency set into that staging archive.

Expected behavior:

- about 12.6k donor paths will be new to current `patch-Z`
- 73 known current character M2/SKIN assets will be intentionally replaced

This should be done transactionally with hashes and a full backup because those 73 paths are currently custom Esteria assets.

Do not replace `patch-Z.MPQ` until the staged archive can be fully enumerated and every imported entry can be read back.

## Phase C: merge locale DBC data at row level

Use current `patch-enUS-Z.MPQ` as the base.

Do **not** replace the whole DBC tables with the donor W/X tables.

### `CharSections.dbc`

This is the most important appearance table to reconcile because it supplies texture/customization sections for the converted models.

Recommended rule:

- preserve all Esteria non-stock race rows
- replace/merge only rows whose race field is one of `1,2,3,4,5,6,7,8,10,11`
- use donor X as the preferred source because X is the winning donor table
- rebase every string offset into Esteria's resulting string block
- preserve all unrelated Esteria rows

### `CreatureDisplayInfo.dbc`

Compare the twenty stock playable display rows listed earlier and any NPC display rows that depend on the converted character models.

Current Esteria already matches the donor for at least the verified Human base row/model contract.

Only replace rows where a semantic field comparison proves the donor differs in a way required by the WoD model.

Do not import all 24,262 donor rows over Esteria's 26,135-row table.

### `CreatureModelData.dbc`

The layout already matches.

For the stock playable model IDs, compare row-by-row and keep Esteria rows that are already equivalent.

Current Human male model row 49 already matches donor X.

Again, do not replace the entire table.

### `CreatureDisplayInfoExtra.dbc`

X does not contain this table, so the donor's effective copy comes from W.

This table is relevant to NPCs that use player-style models and appearance data.

Merge only donor rows proven necessary for NPCs that should use the converted race appearance set. Do not replace Esteria's entire 22,477-row table with W's 15,475-row table.

### `EmotesTextSound.dbc`

X supplies this table, but it should be treated as optional until a row-level comparison proves which changes are actually tied to the character backport.

It is not a reason to overwrite Esteria's full table blindly.

## Phase D: server DBC parity

Because the playable race IDs and base display IDs are not changing, the server-side impact can be much smaller than the client-side asset change.

Still verify server DBC parity for any `CreatureDisplayInfo` / `CreatureModelData` rows that are actually changed or added.

If future work uses new display/model IDs from `Patch-Zz.mpq`, those IDs must also exist in the server's DBC/continuation data where AzerothCore requires them.

## Phase E: regression test the custom-race ecosystem

The donor intentionally replaces common base paths. Esteria custom races may inherit or reuse those base race assets.

At minimum test:

- all ten WotLK races, both sexes
- character creation
- character select
- login and world appearance
- face, skin, hair, facial hair, and hair color combinations
- barber shop
- helmets
- shoulder armor
- chest/robe/pants/boots/gloves
- capes
- weapons and shields
- sheathe/unsheathe
- mounted animations
- swim
- death/corpse
- emotes
- sitting/kneeling
- NPCs that use player-race models
- existing custom races that borrow Human/Elf/etc. geometry or textures
- Darkfallen and other custom appearance systems
- current custom race portraits/UI

Do not consider the migration complete based only on the login screen or one naked Human character.

---

# 7. `G:\Patch-Zz.mpq` detailed analysis

## 7.1 Physical/archive facts

Path:

```text
G:\Patch-Zz.mpq
```

Size:

```text
23,704,065,998 bytes
```

That is about 23.7 GB decimal, or about 22.1 GiB.

The archive begins with a valid MPQ header and uses an extended MPQ format capable of addressing a very large archive.

It is currently outside the Esteria client `Data` directory, so it is not part of the running client's normal archive stack.

Esteria's repository archive-chain tooling currently enumerates single-character custom suffixes from `A` through `Z`. It does not include a `ZZ` suffix. Therefore, even if this file were moved later, its loading behavior should be explicitly proven rather than assumed.

## 7.2 Total inventory

StormLib enumerated **364,155 entries**.

Top-level path counts:

| Root | Entries |
|---|---:|
| `ITEM` | 149,599 |
| `WORLD` | 135,961 |
| `CREATURE` | 40,014 |
| `interface` | 23,901 |
| `DUNGEONS` | 7,727 |
| `tileset` | 5,081 |
| `environments` | 1,784 |
| `spells` | 48 |
| `Novritsch` | 24 |
| `unknown` | 9 |

Other tiny roots include `xtextures`, `particles`, and `textures`.

Important absences:

- no `Character` top-level root
- no `DBFilesClient` root

Therefore this archive does not contain the WoD vanilla-race character package analyzed above and does not carry DBCs that would automatically register most of its new models.

## 7.3 File-type inventory

Observed extension counts:

| Extension | Files |
|---|---:|
| `.blp` | 170,921 |
| `.skin` | 89,372 |
| `.m2` | 60,500 |
| `.wmo` | 24,869 |
| `.anim` | 17,066 |
| `.phys` | 824 |
| `.bone` | 546 |
| `.skel` | 52 |

There are also a handful of miscellaneous files including a JSON manifest, a command file, and PNG data.

## 7.4 Expansion/content era

The archive is not simply a Warlords of Draenor texture pack.

Examples found directly in its listfile include:

### Legion-era examples

```text
WORLD\WMO\argus\...
ITEM\OBJECTCOMPONENTS\AMMO\arrow_bow_1h_artifactlegion_d_06.m2
ITEM\OBJECTCOMPONENTS\AMMO\arrow_bow_1h_artifactwindrunner_d.m2
```

### Battle for Azeroth-era examples

```text
CREATURE\azeriteelemental\azeriteelemental.m2
CREATURE\azeritewarmachinealliance\azeritewarmachinealliance.m2
CREATURE\azeritewarmachinehorde\azeritewarmachinehorde.m2
```

### Shadowlands-era examples

```text
CREATURE\arbiter\arbiter.m2
CREATURE\ardenwealddryadfemale\ardenwealddryadfemale.m2
CREATURE\ardenwealdstag\ardenwealdstag.m2
CREATURE\attendantoribos\attendantoribos.m2
WORLD\WMO\DUNGEON\torghastraid\...
```

No Dracthyr/Dragonriding path matches were found in the targeted search used for this investigation.

A safe description is: **a very large later-expansion asset backport library with content reaching at least Shadowlands-era assets**.

## 7.5 The models are genuinely backported

Two sampled modern M2s were inspected in memory.

### Arbiter

```text
CREATURE\arbiter\arbiter.m2
```

- Size: 1,306,864 bytes
- Magic: `MD20`
- Version: `0x108`

### Ardenweald arrow

```text
ITEM\OBJECTCOMPONENTS\AMMO\arrow_bow_1h_ardenweald_d_01.m2
```

- Size: 25,965 bytes
- Magic: `MD20`
- Version: `0x108`

A sampled BfA-era Arathi WMO:

```text
WORLD\WMO\arathi\8ara_arathirockwmo_01.wmo
```

reported:

- WMO version: 17

These are strong indicators that this is a WotLK-format conversion/backport collection rather than an untouched retail CASC dump stuffed into an MPQ.

The archive still contains later-format sidecar extensions such as `.phys`, `.bone`, and `.skel`. Their presence does not prove the 3.3.5 client uses those files. Treat them as possible source/conversion leftovers or per-model dependencies until each target asset is validated.

## 7.6 It contains real override collisions

This archive is not entirely namespaced new content.

Comparison against stock `patch-3.MPQ` found 289 overlapping paths.

Examples include existing WotLK creature/item textures such as:

```text
CREATURE\alglontheobserver\algalontheobserver_03.blp
ITEM\OBJECTCOMPONENTS\head\helm_cloth_pvpmage_b_04.blp
ITEM\OBJECTCOMPONENTS\head\helm_plate_pvpwarrior_b_04.blp
ITEM\OBJECTCOMPONENTS\SHOULDER\cloth_pvpmage_b_04.blp
```

Comparison against Esteria's current `patch-Z.MPQ` found 877 overlapping paths.

Therefore loading the entire archive at a higher priority would not be a no-op. It would silently replace some existing stock/custom content while leaving most new content unused because nothing references it.

---

# 8. Best ways to use `Patch-Zz.mpq`

## 8.1 Creature and mount donor library

This is probably the highest-value use.

For a selected model:

1. Find the target M2.
2. Verify version `0x108`.
3. Collect every required SKIN, BLP, and ANIM dependency.
4. Re-home the assets under an Esteria-owned path where practical, for example `Creature\Esteria\...`.
5. Create new `CreatureModelData` and `CreatureDisplayInfo` rows with Esteria-owned IDs.
6. Add corresponding server DBC continuation rows if required.
7. Add the creature/mount/item game data that points to the new display ID.
8. Test all animations and texture variations.

This is already close to the workflow used by the repository's mount tooling.

## 8.2 Modern item appearance donor library

The archive has 149,599 `ITEM` entries, including many later-expansion weapon/armor assets.

Potential uses include:

- custom weapons
- shields
- helmets
- shoulders
- ammunition/projectiles
- custom armor appearances

The asset alone does not make an item selectable in WotLK.

A usable custom item appearance normally requires a compatible `ItemDisplayInfo` row and all referenced component textures/models.

This is especially useful for Esteria's custom/heirloom item work.

## 8.3 World/WMO/doodad donor library

The archive has over 135k `WORLD` entries and nearly 25k WMOs.

These can be useful for:

- custom areas
- housing
- custom interiors
- dungeon dressing
- city decoration
- environmental props

A WMO must be tested with all group files and referenced textures/doodads. Copying only the root `.wmo` is not enough.

World content can also have server-side collision/vmap implications depending on how it is used.

## 8.4 Interface art donor library

There are about 23.9k `interface` entries.

These can be mined for icons, frames, textures, and other artwork when format/licensing/project requirements are acceptable.

## 8.5 What not to do

Do not simply move the 22 GB archive into `Data`, rename it to a high-priority patch, and assume it is a global HD upgrade.

Reasons:

- it has no DBC registrations for most new assets
- it contains hundreds of stock/Esteria path collisions
- it contains content from multiple later expansions
- not every dependency has been validated for 3.3.5
- its 22 GB size makes rollback, distribution, and troubleshooting expensive
- Esteria's normal archive tooling does not currently include a `ZZ` suffix
- the current client already has an extensive custom patch hierarchy

Use it as a curated source archive.

---

# 9. Existing Esteria tooling that can support implementation

The repository already contains useful infrastructure for this work.

Relevant tools found during the investigation include:

```text
tools\inspect_client_archive.py
tools\cars_mount_pack.py
tools\mount_pack_batch2.py
tools\ascension_hd_migration.py
tools\playable_race_pack.py
tools\race_portrait_pack.py
```

The existing `ascension_hd_migration.py` is particularly relevant conceptually. It already demonstrates how to:

- merge stock-race appearance rows selectively
- preserve non-stock Esteria race rows
- rebase WDBC strings
- merge `ChrRaces`, `CharSections`, `CreatureDisplayInfo`, `CreatureDisplayInfoExtra`, and `CreatureModelData`
- collect character asset trees
- validate resulting MPQs

Its current donor assumptions are Ascension-specific, so it should not simply be run against this F: donor unchanged. But it provides most of the architectural pattern needed for a dedicated WoD-donor migration tool.

The current mount tooling also already knows how to:

- inspect active archive priority
- identify the winning DBC copy
- merge WDBC rows by ID
- package WotLK M2/SKIN/BLP assets
- validate M2 version `0x108`
- stage and verify MPQ output

This means the proposed migration does not need a new MPQ/DBC framework from scratch.

---

# 10. Feasibility assessment

## WoD vanilla/WotLK race models from the F: donor

**Feasibility: High.**

The models are already converted to WotLK M2 format. The package contains the full dependency family. The donor uses the same base character paths and display IDs that Esteria already understands. Esteria's active `CreatureModelData` layout is already donor-compatible.

The hard part is not model conversion. The hard part is safely reconciling the donor package with Esteria's existing `patch-Z` character models and its heavily customized `patch-enUS-Z` appearance tables.

This should be implemented as a merge, not a file copy.

## Using `Patch-Zz.mpq` for individual modern models/assets

**Feasibility: High, asset-by-asset.**

Verified samples are already WotLK-format M2/WMO files. Esteria already has tooling for custom model/display integration.

Each selected asset still needs dependency collection, ID assignment, DBC integration, and in-game validation.

## Loading the entire `Patch-Zz.mpq` as a global client upgrade

**Feasibility: Technically uncertain and operationally poor.**

The archive itself is valid and full of backported assets, but most new assets are unreferenced and hundreds of paths collide with existing content. Esteria also has no current proven `ZZ` patch slot in its archive tooling.

A selective donor workflow is much safer and more useful.

---

# 11. Recommended next implementation task

If this work is approved later, the next task should be a staged **WoD Player Model Migration** with these explicit rules:

1. Keep Esteria's current `Wow.exe`.
2. Use donor `patch-x.mpq` as the authoritative character-asset source.
3. Treat donor locale X as the authoritative `CharSections`/display/model source for the character pack.
4. Use donor locale W only for companion data not present in X, especially `CreatureDisplayInfoExtra` where proven necessary.
5. Use Esteria `patch-Z.MPQ` and `patch-enUS-Z.MPQ` as the merge bases.
6. Never replace an entire Esteria DBC with the smaller donor DBC.
7. Preserve every custom/non-stock race row.
8. Back up the current Z archives before any write.
9. Stage output first and verify every MPQ entry can be read back.
10. Run a full player-race/custom-race appearance regression matrix before deployment.

A separate later task should build a **Patch-Zz Asset Catalog/Importer** that can search the 364k-entry donor by category, validate M2/WMO versions, collect dependencies, assign safe Esteria IDs, and package only selected assets.

That would turn the 22 GB archive into a practical reusable content library instead of a risky monolithic patch.

---

# 13. Ascension HD live mapping correction (2026-09-28)

The first Ascension-HD deployment exposed two migration bugs that were not asset failures.

## 13.1 In-world player display IDs are effectively 16-bit

Ascension's HD `ChrRaces` rows use display IDs in the `141xxx` range. Those IDs work in Glue/character creation, but Esteria's in-world player display path truncates them to 16 bits. This exactly reproduced an older Pandaren/Vulpera issue already documented in the repository.

Example:

```text
Ascension Human male display 141284
141284 & 0xFFFF = 10212
Esteria CreatureDisplayInfo 10212 -> model 186 -> Character\\Troll\\Female\\TrollFemale.mdx
```

That is why a male Human logged into the world as a female Troll. Night Elf female `141674 & 0xFFFF = 10602`; no such display row existed, which explains the fatal client failure on login.

The corrected split is:

- client `ChrRaces`: keep full Ascension `141xxx` display IDs for Glue;
- client `CreatureDisplayInfo`: retain the full IDs and add 16-bit-safe clones `49000-49019`;
- server `ChrRaces` continuation: use `49000-49019` for the ten stock male/female pairs;
- server `CreatureDisplayInfo` continuation: inject only those 20 low-ID clones;
- both high and low display rows point at the same Ascension `CreatureModelData` IDs.

The `49000-49019` range was verified unused in Esteria's live client display table, server base display DBC, Battlemon continuation, and world SQL `creaturedisplayinfo_dbc` overlay before use.

## 13.2 CreatureDisplayInfo string offsets must be rebased

`tools/ascension_hd_migration.py` originally did not declare fields 6-9 of `CreatureDisplayInfo` as string offsets. Ascension's HD player rows store `51` in those fields, where offset 51 is an empty string in Ascension's string block. The same numeric offset in Esteria resolved to `nLow`.

The migration now rebases `CreatureDisplayInfo` fields 6-9 and canonicalizes donor empty strings to offset zero instead of carrying donor-local numeric offsets into Esteria.

Validated live examples after repair:

```text
49000 -> 112887 -> Character\\Human2\\Male\\HumanMale2.m2
49001 -> 112888 -> Character\\Human2\\Female\\HumanFemale2.m2
49006 -> 112915 -> Character\\NightElf2\\Male\\NightElfMale2.m2
49007 -> 112916 -> Character\\NightElf2\\Female\\NightElfFemale2.m2
```

All four `CreatureDisplayInfo` texture-string fields for those rows now resolve to the same empty strings as the Ascension source.

## 13.3 Esteria DBC preservation audit

The correction does not replace Esteria's DBCs with Ascension's files. The merger starts with Esteria's live tables and changes only the stock-race slices required by the HD models. The live preservation audit confirmed byte-for-byte retention of:

- 403,232 non-stock `CharSections` rows;
- 654 non-stock `CharHairGeosets` rows;
- 46 non-stock `CharHairTextures` rows;
- 3,333 non-stock `CharacterFacialHairStyles` rows;
- 386 non-stock `BarberShopStyle` rows;
- 22 custom `ChrRaces` rows;
- 26,135 pre-existing non-Ascension `CreatureDisplayInfo` rows;
- all pre-existing unrelated `CreatureModelData` and `CreatureDisplayInfoExtra` rows.

Stock appearance rows are intentionally replaced by the matching Ascension HD stock-race contract because the `Race2` models use `Human2`, `Orc2`, etc. UV/texture namespaces. Appending the old stock appearance rows beside them would recreate incompatible duplicate customization mappings.

Regression coverage in `tools/test_ascension_hd_migration.py` now explicitly tests the 16-bit world-display split and the `CreatureDisplayInfo` string-rebase behavior.

---

# 12. Implementation outcome: Ascension HD replacement (2026-09-28)

The original F: WoD player-model splice was retired after repeated in-game face/hair/skin corruption despite exhaustive byte validation of its M2/SKIN/ANIM/BLP payload and appearance DBCs.

Esteria now uses Ascension's isolated HD stock-race implementation instead.

## Active client contract

The ten stock races keep their normal Esteria race IDs, but their `ChrRaces` male/female display IDs now point at Ascension's dedicated HD display rows:

- Human: `141284 / 141285`
- Orc: `141286 / 141287`
- Dwarf: `141671 / 141672`
- Night Elf: `141673 / 141674`
- Scourge: `141675 / 141676`
- Tauren: `141677 / 141678`
- Gnome: `141679 / 141680`
- Troll: `141669 / 141670`
- Blood Elf: `141681 / 141682`
- Draenei: `141683 / 141684`

Those displays resolve through Ascension model IDs `112887..112926` to isolated asset namespaces such as `Character\\Human2\\...`, `Character\\Orc2\\...`, etc. The normal `Character\\Human`, `Character\\Orc`, and other stock namespaces are no longer used as the HD player implementation.

The live stock appearance counts after migration are:

- `CharSections`: 8,520 rows
- `CharHairGeosets`: 295 rows
- `CharHairTextures`: 73 rows
- `CharacterFacialHairStyles`: 172 rows
- `BarberShopStyle`: 563 rows

All custom/non-stock race rows were preserved.

## Asset replacement

The migration removed or restored 12,784 F-donor stock-race entries from `patch-Z.MPQ`:

- 12,701 visible donor-X assets
- 83 hidden donor-W texture dependencies
- 73 paths that predated the WoD experiment were restored byte-for-byte from the pre-WoD backup instead of being deleted

Ascension contributed 14,709 `Race2` files totaling about 1.0 GiB of source data. Every imported asset was validated byte-for-byte after staging and again after live installation.

Final `patch-Z.MPQ` size: 1,799,088,232 bytes (~1.68 GiB).

The temporary full donor-W archive `patch-T.MPQ` was removed.

## DBC rollback + replacement

The migration restored the F-donor changes to the original stock display/model metadata before adding Ascension's dedicated HD player rows:

- 56 `CreatureDisplayInfo` rows restored from the pre-WoD backup
- 20 `CreatureModelData` rows restored
- 29 `CreatureDisplayInfoExtra` rows restored
- 20 Ascension HD `CreatureDisplayInfo` rows added
- 20 Ascension HD `CreatureModelData` rows added
- Ascension's player displays require no additional `CreatureDisplayInfoExtra` rows

Only the ten stock `ChrRaces` male/female display fields were changed. Custom race rows and unrelated DBC content were retained.

Final `patch-enUS-Z.MPQ` size: 185,267,532 bytes (~176.7 MiB).

## Executable cleanup

The donor-only test patch at `Wow.exe` file offset `0x2B1F48` was reverted from `0xEB` back to Esteria's original `0x74`. No other executable bytes were changed by this replacement.

## Server DBC continuity

The running AzerothCore server now loads matching WXL continuations:

- `ChrRaces.dbc1-ascension-hd` — 10 rows
- `CreatureDisplayInfo.dbc1-ascension-hd` — 20 rows
- `CreatureModelData.dbc1-ascension-hd` — 20 rows

They coexist without ID collisions with the existing Battlemon and Freeborn continuation files. After restart, `mod-wxl-dbc` reported 6 continuation files and 6,389 total injected rows with no load errors.

## Saved-character audit

All 310 existing stock-race characters were checked against the new live Ascension appearance contract. Zero characters require skin/face/hair/facial-style remapping.

## Known donor-stale texture rows

The live Ascension stock `CharSections` references 10,037 unique non-empty texture paths. Exactly seven paths do not exist in `patch-Z`; the same seven are absent from Ascension's source client and are treated as stale/unreachable donor rows rather than missing migration payloads:

- `Character\\Dwarf2\\Male\\DwarfMaleFaceLower00_104.blp`
- `Character\\Dwarf2\\Male\\DwarfMaleFaceUpper00_104.blp`
- `Character\\Dwarf2\\Male\\DwarfMaleNakedPelvisSkin00_104.blp`
- `Character\\Dwarf2\\Male\\DwarfMaleNakedTorsoSkin00_06.blp`
- `Character\\Gnome2\\Female\\GnomeFemaleSkin00_100_Extra.blp`
- `Character\\Gnome2\\Female\\GnomeFemaleSkin00_101_Extra.blp`
- `Character\\NightElf2\\Female\\nightelffemaleskin00_12.blp`

## Rollback point

The complete pre-replacement state is backed up under:

`G:\\3.3.5a - Dev\\Backups\\ascension-hd-replacement-20260928-020737`

That backup includes the previous Z/enUS-Z archives, `Wow.exe`, the temporary `patch-T.MPQ`, a migration manifest, the generated Ascension server continuations, and copies of the pre-existing server continuation files.

The reusable replacement tool is `tools/replace_wod_with_ascension_hd.py`.

---

# 14. Final Ascension correction: native stock display/model IDs (2026-09-28)

The `141xxx`/`49000-49019` player-display design described above was retired after live testing. It reproduced a split between Glue and in-world rendering and did not match Esteria's actual authoritative DBC layering.

## 14.1 Why Ascension itself works

Ascension does more than ship MPQ assets. Its `Extensions.dll` explicitly loads a parallel HD data system including:

- `HDCharHairGeosets.dbc`
- `HDCharSections.dbc`
- `HDCharacterFacialHairStyles.dbc`
- `HDCreatureDisplayInfo.dbc`
- `HDCreatureDisplayInfoExtra.dbc`
- `HDCreatureModelData.dbc`

`MemoryBridge.log` also shows Ascension creating separate runtime tables. Therefore Ascension's high display/model ID scheme cannot be assumed to behave identically in an unmodified 3.3.5 client simply because the M2 files themselves are WotLK-compatible.

Esteria does not need to reproduce Ascension's complete binary HD subsystem for the `Race2` player models. The models are already `MD20`/WotLK-format assets. The safer solution is to flatten the Race2 model metadata into Esteria's native stock player chain.

## 14.2 Authoritative Esteria DBC layering

The earlier migration updated `patch-enUS-Z.MPQ`, but the active global `Data\\patch-Z.MPQ` still carried stock player model rows. That is why character select continued to show non-HD models.

The same character DBCs also exist in lower global patches (`PATCH-A`, `Patch-C`, `Patch-Y`), but `patch-Z` is the winning global layer. Both active Z archives are now kept coherent for the stock player contract.

## 14.3 Final native player chain

The ten stock races now retain their original 3.3.5 display IDs everywhere. No special high player displays or 16-bit clone displays remain.

Examples:

```text
Human male
race 1 -> display 49 -> model 49 -> Character\\Human2\\Male\\HumanMale2.m2

Human female
race 1 -> display 50 -> model 50 -> Character\\Human2\\Female\\HumanFemale2.m2

Night Elf male
race 4 -> display 55 -> model 55 -> Character\\NightElf2\\Male\\NightElfMale2.m2

Night Elf female
race 4 -> display 56 -> model 56 -> Character\\NightElf2\\Female\\NightElfFemale2.m2
```

The complete stock model mapping copies Ascension model metadata onto the existing stock IDs:

| Stock model ID | Ascension source ID | Race2 model |
|---:|---:|---|
| 49 | 112887 | Human male |
| 50 | 112888 | Human female |
| 51 | 112889 | Orc male |
| 52 | 112890 | Orc female |
| 53 | 112913 | Dwarf male |
| 54 | 112914 | Dwarf female |
| 55 | 112915 | Night Elf male |
| 56 | 112916 | Night Elf female |
| 57 | 112917 | Scourge male |
| 58 | 112918 | Scourge female |
| 59 | 112919 | Tauren male |
| 60 | 112920 | Tauren female |
| 182 | 112921 | Gnome male |
| 183 | 112922 | Gnome female |
| 185 | 112911 | Troll male |
| 186 | 112912 | Troll female |
| 2208 | 112923 | Blood Elf male |
| 2209 | 112924 | Blood Elf female |
| 2248 | 112925 | Draenei male |
| 2250 | 112926 | Draenei female |

The temporary Ascension high player displays (`141xxx`), temporary world clones (`49000-49019`), and temporary high source model rows (`112887-112926`) were removed from the final player DBC contract after their metadata was copied to the stock model IDs.

## 14.4 Preservation and validation

Both `Data\\patch-Z.MPQ` and `Data\\enUS\\patch-enUS-Z.MPQ` now resolve the same stock `ChrRaces` display pairs and the same Race2 stock model aliases. The repair preserves:

- 403,232 non-stock `CharSections` rows;
- 654 non-stock `CharHairGeosets` rows;
- 46 non-stock `CharHairTextures` rows;
- 3,333 non-stock `CharacterFacialHairStyles` rows;
- 386 non-stock `BarberShopStyle` rows;
- 22 custom/non-stock `ChrRaces` rows;
- 26,135 unrelated `CreatureDisplayInfo` rows;
- 1,582 unrelated `CreatureModelData` rows.

All 20 live Race2 M2 files were independently verified byte-for-byte against the Ascension extracted source.

The server no longer injects Ascension `ChrRaces` or `CreatureDisplayInfo` continuations. It loads only a 20-row `CreatureModelData.dbc1-ascension-hd` continuation using the same stock model IDs. The latest startup reports four continuation files total and 6,359 injected rows, with Battlemon and Freeborn unchanged.

The final migration/repair helper is `tools/finalize_ascension_hd_stock_ids.py`. Regression coverage in `tools/test_ascension_hd_migration.py` is 9/9 passing.

The latest rollback point is:

`G:\\3.3.5a - Dev\\Backups\\ascension-hd-native-stock-20260928-041942`

---

# 15. HD follow-up corrections: direct textures, High Elves, and NPC appearances

Live testing after the native stock-ID conversion exposed three smaller follow-up problems. They were corrected without changing the working stock player display/model chain.

## 15.1 Missing direct M2 textures

The Race2 M2 files contain named type-0 texture references in addition to the composited skin textures supplied by `CharSections`. The first Race2 import copied the Race2 folders but did not copy those dependencies because many of them live under the original stock race namespaces such as `Character\\Human`, `Character\\Tauren`, and `Character\\BloodElf`.

An audit of all 20 Race2 player models found 54 unique named type-0 BLP dependencies. All 54 were absent from the live `patch-Z.MPQ`, while all 54 exist in Ascension's extracted `patch-CHA.mpq`. These include eye textures, eye-reflection textures, Death Knight eye effects, Tauren jewelry/hair-detail textures, and several model-specific detail textures.

All 54 were imported byte-for-byte. This specifically addresses the flat green eyeballs and neon-green Tauren braid/jewelry pieces seen in live testing.

## 15.2 High Elf inherits the HD Blood Elf standard contract

High Elf is race 13 and already shares Blood Elf's male/female display IDs (`15476 / 15475`), so its body model chain resolves through the HD BloodElf2 model aliases. Its appearance rows, however, were still largely based on the old `Character\\BloodElf\\...` texture set.

The follow-up repair keeps all High-Elf-only customization rows but makes every standard Blood Elf customization key inherit the live HD Blood Elf values. The final `CharSections` audit reports zero mismatches across all 1,067 standard Blood Elf keys while retaining 2,521 total High Elf rows. In addition, 493 High-Elf-only texture fields were upgraded from `Character\\BloodElf` to an existing `Character\\BloodElf2` equivalent where one was available.

Matching standard rows in `CharHairTextures`, `CharacterFacialHairStyles`, and `BarberShopStyle` were also synchronized. High-Elf-only extra options remain present.

## 15.3 NPC appearance rows

Once the stock `CreatureModelData` aliases pointed at Race2 models, NPC displays that already referenced those stock model IDs also began using the HD body meshes. Most existing NPC appearance records remained valid, but 75 `CreatureDisplayInfoExtra` rows used face/facial-style indices that are outside the live HD appearance contract.

The repair changes only those invalid values to the nearest supported HD option while retaining all other NPC appearance/equipment data. The affected rows break down as:

- 64 Tauren;
- 7 Night Elf;
- 3 Troll;
- 1 Draenei.

The changes consist of 42 face-index corrections and 33 facial-style corrections. A matching `CreatureDisplayInfoExtra.dbc1-ascension-hd-npc` continuation with exactly 75 rows is installed on the server. Worldserver reports five continuation files and 6,434 injected rows with no base DBC files modified.

The reusable follow-up repair tool is `tools/fix_ascension_hd_followups.py`.

The rollback point for this pass is:

`G:\\3.3.5a - Dev\\Backups\\ascension-hd-followups-20260928-053727`
