# RetroPorter Handoff

## Resume target

This document is the authoritative resume point for the RetroPorter project.

Repository:

```text
R:\Users\Zach\Documents\GitHub\RetroPorter\
```

DevSpace workspace used for this session:

```text
ws_6e9b89c7bb
```

If that workspace is still valid, reuse it. If a future session must reopen the project, open the same repository path in checkout mode.

## What has been completed

The repository foundation is in place and the Mag'har Orc, Highmountain Tauren, Mechagnome, Earthen, Haranir, and Skyborne art retroports have all been run successfully. The first five were sourced from Retail; Skyborne was sourced from the installed World of Warcraft: Forever beta.

Completed work:

- installed and validated Bar3b0n3s/Converter (`wotlkconv`)
- found the correct Retail CASC root
- fetched community listfile, WoWDBDefs, and TACT keys
- created reusable Python package/CLI for future races
- extracted modern customization DB2s
- discovered Mag'har's Retail race/model/customization graph
- resolved Mag'har material resources through `TextureFileData`
- resolved FileDataIDs to paths through the community listfile
- created a conservative Mag'har asset plan
- dry-ran the conversion
- ran the real conversion
- verified converted player models as Wrath-compatible M2 v264
- corrected physical output namespacing to match Converter's internal path prefix
- created a canonical patch staging root
- recorded current Retail IDs in `manifests/maghar.toml`
- generalized the asset planner so race-specific roots/core model IDs come from `RaceSpec` instead of Mag'har-specific constants
- extracted/discovered Highmountain Tauren Retail RaceID 28 and ChrModel IDs 55/56
- converted and verified the dedicated Highmountain male/female player models
- recorded Highmountain findings in `docs/HIGHMOUNTAIN.md` and `manifests/highmountain.toml`
- extended `RaceSpec` with explicit required dependency FileDataIDs for assets outside the DB2 material graph
- discovered Mechagnome Retail RaceID 37 and ChrModel IDs 73/74
- identified the male/female Mechagnome collection M2s used by `ChrCustomizationSkinnedModel`
- expanded the safe asset slice to include directly referenced shared Gnome textures while excluding Dracthyr/Human requirement noise
- converted and verified both Mechagnome base bodies and both collection models as Wrath-compatible M2 v264
- recorded Mechagnome findings in `docs/MECHAGNOME.md` and `manifests/mechagnome.toml`
- generalized discovery so one visual target can intentionally match multiple Retail `ChrRaces` rows
- discovered Earthen Retail RaceIDs 84/85 sharing ChrModel IDs 195/196
- identified the male/female `earthenextras` collection M2s used by 126 `ChrCustomizationSkinnedModel` rows
- converted and verified both Earthen base bodies and both collection models as Wrath-compatible M2 v264
- recorded Earthen findings in `docs/EARTHEN.md` and `manifests/earthen.toml`
- verified Haranir's internal `ClientFileString` is `Harronir`
- discovered Haranir Retail RaceIDs 86/91 sharing ChrModel IDs 200/201
- identified Haranir base models plus two dominant external customization collection models (6255031/6255032)
- converted and verified both Haranir base bodies and both Haranir collection models as Wrath-compatible M2 v264
- recorded Haranir findings in `docs/HARANIR.md` and `manifests/haranir.toml`
- generalized extraction/conversion so an alternate CASC source root/product can be supplied per run
- verified the installed Forever beta at `D:\Blizzard\World of Warcraft`, product `wow_classic_beta`, build `1.60.1.70009`
- discovered paired Skyborne RaceIDs 95/96 sharing ChrModel IDs 218/219
- identified Skyborne male/female body M2s, dedicated customization collections, and reused Blood Elf Demon Hunter collection models
- converted and verified all six Skyborne M2s as Wrath-compatible v264 with zero skipped/failed files
- recorded completed Skyborne findings in `docs/SKYBORNE.md` and `manifests/skyborne.toml`

## Current verified environment

```text
Retail CASC root: G:\Blizzard\World of Warcraft
Retail product:   wow
Retail version:   12.1.0.69933
Retail build:     WOW-69933patch12.1.0_Retail
Forever CASC root: D:\Blizzard\World of Warcraft
Forever product:   wow_classic_beta
Forever version:   1.60.1.70009
Forever build:     WOW-70009patch1.60.1_ForeverBeta
Locale:            enUS
Wrath client:      G:\3.3.5a - Dev
Work root:         G:\RetroPorterWork
```

Converter support files:

```text
C:\Users\Zach\.cache\wotlkconv\community-listfile.csv
C:\Users\Zach\.cache\wotlkconv\definitions\
C:\Users\Zach\.cache\wotlkconv\WoW.txt
```

Python is currently 3.14.4. The project requires Python 3.10+.

## Important path detail

Use this as `--casc`:

```text
G:\Blizzard\World of Warcraft
```

Do **not** use:

```text
G:\Blizzard\World of Warcraft\_retail_
```

Converter expects `.build.info` and `Data`, which are in the parent directory.

## Current CLI

Run commands from the repo or any environment where the editable package is installed:

```powershell
python -m retroporter doctor
python -m retroporter extract-db2 --race maghar
python -m retroporter discover --race maghar
python -m retroporter plan-assets --race maghar
python -m retroporter convert-assets --race maghar --dry-run
python -m retroporter convert-assets --race maghar
python -m retroporter extract-db2 --race highmountain
python -m retroporter discover --race highmountain
python -m retroporter plan-assets --race highmountain
python -m retroporter convert-assets --race highmountain --dry-run
python -m retroporter convert-assets --race highmountain
python -m retroporter extract-db2 --race mechagnome
python -m retroporter discover --race mechagnome
python -m retroporter plan-assets --race mechagnome
python -m retroporter convert-assets --race mechagnome --dry-run
python -m retroporter convert-assets --race mechagnome
```

Use `python -m retroporter` rather than assuming `retroporter.exe` is on PATH. The current Python user Scripts directory is not on PATH.

## Mag'har IDs verified from live Retail

```text
Retail RaceID: 36
ClientFileString: MagharOrc
Fallback race: Orc, RaceID 2
```

Male:

```text
ChrModelID: 71
DisplayID: 84558
Core model FDID: 917116
Path: character\orc\male\orcmale_hd.m2
Skeleton FDID: 4690417
```

Female:

```text
ChrModelID: 72
DisplayID: 84560
Core model FDID: 949470
Path: character\orc\female\orcfemale_hd.m2
Skeleton FDID: 4690416
```

Upright male:

```text
Core model FDID: 1968587
Path: character\orc\male\orcmaleupright.m2
```

These are also stored in:

```text
manifests/maghar.toml
```

## Mag'har customization discovery

Current live graph totals:

```text
23 options
201 choices
548 elements
74 linked geoset records
376 linked material records
358 discovered FileDataIDs before safe-slice filtering
```

Important male options:

```text
347 Skin Color
350 Hair Style
351 Hair Color
352 Beard
353 Hunched
412 Face
880 Eye Color
882 Sideburns
883 Tusks
884 Earrings
885 Piercings
6378 Eyesight
8564 Eye Style
```

Important female options:

```text
354 Skin Color
357 Hair Style
358 Hair Color
413 Face
414 Earrings
881 Eye Color
886 Nose Ring
887 Necklace
6379 Eyesight
8565 Eye Style
```

Retail uses requirements to inject shared choices. Some requirement-gated eye choices lead to Dracthyr/Human assets. Do not assume every choice attached to the Mag'har `ChrModel` is baseline Mag'har content.

## Current generated reports

```text
G:\RetroPorterWork\maghar\reports\discovery.json
G:\RetroPorterWork\maghar\reports\asset-plan.json
G:\RetroPorterWork\maghar\reports\core-model-dryrun.json
G:\RetroPorterWork\maghar\reports\asset-convert-dryrun.json
G:\RetroPorterWork\maghar\reports\asset-convert.json
```

These are intentionally outside Git because they may contain detailed references derived from Blizzard client data and are generated artifacts.

## Canonical converted output

Use only this staging root for future packaging:

```text
G:\RetroPorterWork\maghar\output\patch-root\
```

Current race tree:

```text
G:\RetroPorterWork\maghar\output\patch-root\custom\maghar\character\orc\...
```

Current actual output:

```text
439 files total
3 M2
3 SKIN
160 ANIM
273 BLP
```

Converter report:

```text
160 ok
6 lossy
273 passthrough
9 skipped
0 failed
```

September 29 integration QA found nine textures referenced directly by the Mag'har core M2 TXID chunks that were not selected by the original customization-material graph. `build_asset_plan()` now opens each core M2 from CASC, collects nonzero `texture_file_ids`, and marks them as required hard model dependencies. The regenerated patch root contains all nine. Future races must pass the same direct-M2 texture closure check before their art conversion is considered complete.

The older tree below is exploratory and must not be packaged:

```text
G:\RetroPorterWork\maghar\output\assets\
```

It was generated before the physical `custom\maghar` namespace fix.

## Verified converted model properties

Male HD:

```text
M2 version 264
flat, not chunked
46,799 vertices
220 bones
372 sequences
wotlk_compatible: True
```

Female HD:

```text
M2 version 264
flat, not chunked
44,003 vertices
223 bones
361 sequences
wotlk_compatible: True
```

Upright male:

```text
M2 version 264
flat, not chunked
46,781 vertices
220 bones
118 sequences
wotlk_compatible: True
```

## Expected lossy results

Only these six conversion results are lossy:

```text
character/orc/female/orcfemale_hd.m2
orcfemale_hd00.skin
character/orc/male/orcmale_hd.m2
orcmale_hd00.skin
character/orc/male/orcmaleupright.m2
orcmaleupright00.skin
```

Expected losses include newer shaders, newer blend behavior, modern shadow batches, modern LOD chunks, and replaceable texture types Wrath does not support.

Do not treat `lossy` as failure. Test the results visually in 3.3.5a.

## Nine skipped eye textures

These currently fail CASC decode before BLP conversion:

```text
character\orc\claneyes00_00_3492843.blp
character\orc\claneyes00_01_3492844.blp
character\orc\claneyes00_02_3492845.blp
character\orc\claneyes00_03_3492846.blp
character\orc\claneyes00_04_3492847.blp
character\orc\claneyes00_05_3492848.blp
character\orc\claneyes00_06_3492849.blp
character\orc\claneyes00_07_3492850.blp
character\orc\eyes00_08_3492836.blp
```

A retry using `--casc-cdn` produced the same invalid-BLTE result. This is not currently a simple CDN/local-cache problem.

Do not let these block the first playable Mag'har build.

## Retail `.bone` limitation

The current discovery includes 27 `character\orc\... .bone` files. Converter does not convert `.bone` overrides because Wrath has no equivalent system.

The asset planner marks them unsupported rather than copying them.

Before spending time recreating them, add choice-level requirement/dependency filtering so we know exactly which visible Mag'har options need them.

## Current encrypted DB2 limitation

`CreatureDisplayInfo.db2` is encrypted with TACT key:

```text
583C5B29BF208655
```

That key is absent from the current public keyring. Every other currently needed DB2 extracted successfully.

This does not block the current art conversion. The race/model relationship and core model FileDataIDs were independently established through `ChrRaces`, `ChrRaceXChrModel`, `ChrModel`, the listfile, and Retail's explicit Orc fallback.

If the key becomes available, fetch current keys and rerun DB2 extraction/discovery.

## Highmountain Tauren completion

Verified Retail identity:

```text
Retail RaceID: 28
ClientFileString: HighmountainTauren
Fallback race: Tauren, RaceID 6
Male ChrModelID: 55, DisplayID: 75080, model FDID: 1630218
Female ChrModelID: 56, DisplayID: 75081, model FDID: 1630402
```

Customization discovery:

```text
44 options
251 choices
487 elements
104 linked geosets
274 linked materials
9 linked bone sets
245 discovered FileDataIDs before safe filtering
```

Canonical output:

```text
G:\RetroPorterWork\highmountain\output\patch-root\custom\highmountain\
279 files: 2 M2, 2 SKIN, 103 ANIM, 172 BLP
103 ok, 4 lossy, 172 passthrough, 7 skipped, 0 failed
```

Both converted player M2s are version 264, flat/non-chunked, and report `wotlk_compatible: True`. Seven Highmountain eye BLPs currently have the same invalid/non-BLTE CASC issue seen with Mag'har eye assets. Nine Retail `.bone` overrides are intentionally unsupported.

See `docs/HIGHMOUNTAIN.md` and `manifests/highmountain.toml`.

## Mechagnome completion

Verified Retail identity:

```text
Retail RaceID: 37
ClientFileString: Mechagnome
Fallback race: Gnome, RaceID 7
Male ChrModelID: 73, DisplayID: 90786, model FDID: 2622502
Female ChrModelID: 74, DisplayID: 90787, model FDID: 2564806
```

Mechagnome is the first completed target that depends heavily on Retail's external skinned-model customization system:

```text
23 options
236 choices
694 elements
46 linked geosets
78 linked ChrCustomizationSkinnedModel rows
402 linked materials
28 linked bone sets
393 discovered FileDataIDs before safe filtering
```

The cybernetic geometry comes from these collection models:

```text
2628212 item\objectcomponents\collections\collections_mechagnome_mg_m.m2
2628213 item\objectcomponents\collections\collections_mechagnome_mg_f.m2
```

Required collection textures explicitly injected into the plan:

```text
2628215 item\objectcomponents\collections\collections_mechagnome_2_2628215.blp
2628216 item\objectcomponents\collections\collections_mechagnome_3_2628216.blp
```

The safe material slice intentionally includes directly referenced `character\gnome\...` textures because Mechagnome reuses the Gnome face/skin material system. Dracthyr/Human requirement-driven eye assets remain excluded.

Canonical output:

```text
G:\RetroPorterWork\mechagnome\output\patch-root\custom\mechagnome\
360 files: 4 M2, 4 SKIN, 46 ANIM, 306 BLP
46 ok, 8 lossy, 306 passthrough, 2 skipped, 0 failed
```

All four M2s are version 264, flat/non-chunked, and report `wotlk_compatible: True`:

```text
Male base:         17,763 vertices, 202 bones
Female base:       18,455 vertices, 214 bones
Male collection:   26,473 vertices, 67 bones
Female collection: 26,079 vertices, 60 bones
```

Two male BLPs currently have the known invalid/non-BLTE CASC payload issue:

```text
3060787 character\mechagnome\male\mechagnomemale_paint_3060787.blp
3060788 character\mechagnome\male\mechagnomemale_hair_color_3060788.blp
```

The 28 Retail `.bone` overrides remain unsupported by Wrath/Converter.

Most importantly, stock Wrath has no `ChrCustomizationSkinnedModel` equivalent. A fully featured Mechagnome will eventually require baking the collection-model geometry into custom player M2/geoset variants, extending the client, or shipping a reduced fixed mechanical configuration first.

See `docs/MECHAGNOME.md` and `manifests/mechagnome.toml`.

## Earthen completion

Verified Retail identity:

```text
Retail RaceIDs: 84 and 85
ClientFileString: EarthenDwarf
RaceID 84: Horde-facing row
RaceID 85: Alliance-facing row
Shared male ChrModelID: 195, DisplayID: 115279, model FDID: 5548261
Shared female ChrModelID: 196, DisplayID: 115281, model FDID: 5548259
```

Earthen required a discovery change because two playable `ChrRaces` rows intentionally share one visual race. `RaceSpec.retail_race_ids` now supports this without guessing from duplicate display names.

Customization discovery:

```text
36 options
308 choices
675 elements
22 linked geosets
126 linked ChrCustomizationSkinnedModel rows
466 linked materials
22 linked bone sets
448 discovered FileDataIDs before safe filtering
```

External collection geometry:

```text
5792407 item\objectcomponents\collections\earthenextras_ed_f.m2
5792408 item\objectcomponents\collections\earthenextras_ed_m.m2
5688294 item\objectcomponents\collections\earthenextras_ed_m_5688294.blp
```

Canonical output:

```text
G:\RetroPorterWork\earthen\output\patch-root\custom\earthen\
517 files: 4 M2, 4 SKIN, 109 ANIM, 400 BLP
109 ok, 40 lossy, 368 passthrough, 9 skipped, 0 failed
```

All four M2s are version 264, flat/non-chunked, and report `wotlk_compatible: True`:

```text
Male base:         18,561 vertices, 229 bones
Female base:       15,840 vertices, 245 bones
Male collection:   56,684 vertices, 110 bones
Female collection: 60,596 vertices, 111 bones
```

The 40 lossy results are expected. Eight are the four M2/SKIN pairs. The other 32 are 2048x1024 skin-color textures downscaled to 1024x512 for Wrath compatibility. Nine Earthen BLPs have the known invalid/non-BLTE CASC payload issue. The 22 Retail `.bone` overrides remain unsupported by Wrath/Converter.

The female collection model is relatively close to Wrath's 65,535 vertex ceiling. Any future geometry-baking strategy must validate compacted vertex counts before shipping.

See `docs/EARTHEN.md` and `manifests/earthen.toml`.

## Haranir completion

Verified Retail identity:

```text
Retail RaceIDs: 86 and 91
ClientFileString: Harronir
Shared male ChrModelID: 200, DisplayID: 116539, model FDID: 5422149
Shared female ChrModelID: 201, DisplayID: 116687, model FDID: 5422147
```

Customization discovery:

```text
57 options
568 choices
1,444 elements
51 linked geosets
250 linked ChrCustomizationSkinnedModel rows
1,017 linked materials
3 linked item-geo modification rows
950 discovered FileDataIDs before safe filtering
```

Primary external customization geometry:

```text
6255032 models\item\unk_exp11_6255032_hr_m\6255032_hr_m.m2
6255031 models\item\unk_exp11_6255031_hr_f\6255031_hr_f.m2
```

Canonical output:

```text
G:\RetroPorterWork\haranir\output\patch-root\custom\haranir\
1,028 files: 4 M2, 4 SKIN, 108 ANIM, 912 BLP
108 ok, 189 lossy, 731 passthrough, 25 skipped, 0 failed
```

All four converted models report `wotlk_compatible: True`:

```text
Male base:         24,087 vertices, 231 bones
Female base:       24,042 vertices, 247 bones
Male collection:   59,563 vertices, 79 bones
Female collection: 55,233 vertices, 65 bones
```

181 of the 189 lossy outputs are BLP texture downscales. The remaining eight are the four M2/SKIN pairs. Twenty-five Haranir BLPs have the known malformed/non-BLTE CASC payload issue. The male collection model is close enough to Wrath's 65,535-vertex ceiling that later geometry baking must be conservative.

See `docs/HARANIR.md` and `manifests/haranir.toml`.

## Skyborne completion

Skyborne was sourced from the installed **World of Warcraft: Forever beta**:

```text
CASC root: D:\Blizzard\World of Warcraft
Product: wow_classic_beta
Version: 1.60.1.70009
Build: WOW-70009patch1.60.1_ForeverBeta
```

Verified identity:

```text
RaceID 95: High Order Skyborne
RaceID 96: Windshaper Skyborne
ClientFileString: Skyborne
Shared male ChrModelID: 218, DisplayID: 139407, model FDID: 7478487
Shared female ChrModelID: 219, DisplayID: 139408, model FDID: 7478494
```

Customization discovery:

```text
37 options
497 choices
1,556 elements
97 linked geosets
96 linked ChrCustomizationSkinnedModel rows
1,261 linked materials
40 linked bone sets
1,201 discovered FileDataIDs before safe filtering
```

Dedicated Skyborne customization collections:

```text
7845093 models\unknown\unk_exp00_7845093\7845093.m2  (male)
7845092 models\unknown\unk_exp00_7845092\7845092.m2  (female)
```

Skyborne also reuses the Blood Elf Demon Hunter collections:

```text
2763973 item\objectcomponents\collections\demonhuntergeosets_be_m.m2
2763972 item\objectcomponents\collections\demonhuntergeosets_be_f.m2
```

Canonical output:

```text
G:\RetroPorterWork\skyborne\output\patch-root\custom\skyborne\
1,219 files: 6 M2, 6 SKIN, 106 ANIM, 1,101 BLP
12 lossy, 1,207 passthrough, 0 skipped, 0 failed
```

All six converted M2s report `wotlk_compatible: True`:

```text
Male base:                    42,031 vertices, 250 bones
Female base:                  35,974 vertices, 245 bones
Male Skyborne collection:      2,299 vertices, 52 bones
Female Skyborne collection:    2,556 vertices, 42 bones
Male BE DH collection:         3,506 vertices, 40 bones
Female BE DH collection:       3,165 vertices, 37 bones
```

The 12 lossy files are exactly the six M2/SKIN pairs. No Skyborne texture was skipped. Forty `.bone` overrides remain unsupported by stock Wrath/Converter.

`CreatureDisplayInfo.db2` in this beta is encrypted with missing public key `057DC814574BD5B6`; this did not block model/customization discovery.

See `docs/SKYBORNE.md` and `manifests/skyborne.toml`. `docs/SKYBORNE_PREP.md` is retained only as historical preparation notes.

## The next task

The next substantial phase for all six completed art-port targets is **Wrath DBC integration**. Skyborne no longer has a source-client blocker; its Forever asset conversion is complete.

Do not convert random additional assets without first running discovery and building a conservative race-specific asset plan.

Next actions:

1. Identify/extract Esteria's current highest-priority copies of the character DBCs from `G:\3.3.5a - Dev` and its active custom patch stack.
2. Copy those templates to a safe external working directory such as `G:\RetroPorterWork\wrath-templates\DBFilesClient\`.
3. Determine an unused Esteria race ID for Mag'har. Do not reuse Retail RaceID 36 blindly.
4. Inspect RaceID 36 rows in Retail `ChrCustomizationConversion` and incorporate them into the flattening plan.
5. Add an ID-allocation manifest for new `CreatureModelData`, `CreatureDisplayInfo`, `CharSections`, `CharHairGeosets`, `CharacterFacialHairStyles`, and `BarberShopStyle` records.
6. Implement a DBC generator that merges new rows onto Esteria's actual templates and refuses ID collisions.
7. First make a minimally selectable Mag'har with default male/female appearance.
8. Then add skin, face, hair, and beard in that order.
9. Treat upright posture, eyes, tusks, jewelry, and modern extras as later layers.
10. Only after DBC output exists should `patch-root` be packed into the test MPQ and installed in the client.

Read `docs/DBC_STRATEGY.md` before writing any DBC code.

## Important decisions still open

These are not bugs. They are design decisions that need to be made deliberately:

- Esteria's custom RaceID for Mag'har
- default male posture: hunched or upright
- whether both male postures need to be selectable in the first release
- how many modern accessory categories to expose through Wrath's limited appearance fields
- whether to initially simplify modern eye customization
- whether modern `.bone`-driven choices are important enough to bake into custom model variants

## Repository state

The target directory was empty at the start of this session and was **not a Git repository**. Source files and docs have been laid down, but `git init` was not performed by DevSpace because the available file-writing workflow does not include a dedicated repository-initialization action and shell commands were kept to inspection/build/test work.

Before first commit, initialize Git manually or through an appropriate Git-aware workflow:

```powershell
cd R:\Users\Zach\Documents\GitHub\RetroPorter
git init
git add .
git commit -m "Bootstrap Retail race retroporter and Mag'har discovery pipeline"
```

Review `.gitignore` before committing. Blizzard asset binaries are intentionally excluded.

## Quick resume commands

```powershell
cd R:\Users\Zach\Documents\GitHub\RetroPorter
python -m retroporter doctor
python -m retroporter discover --race skyborne
python -m retroporter plan-assets --race skyborne
python -m retroporter convert-assets --race skyborne --dry-run --source-root "D:\Blizzard\World of Warcraft" --source-product wow_classic_beta
```

The existing converted patch root does not need to be regenerated unless Retail changed, Converter changed, source selection changed, or the work directory was removed.

## Read these first when resuming

```text
README.md
docs/PIPELINE.md
docs/MAGHAR.md
docs/HIGHMOUNTAIN.md
docs/MECHAGNOME.md
docs/EARTHEN.md
docs/HARANIR.md
docs/SKYBORNE.md
docs/SKYBORNE_PREP.md
docs/DBC_STRATEGY.md
docs/HANDOFF.md
manifests/maghar.toml
manifests/highmountain.toml
manifests/mechagnome.toml
manifests/earthen.toml
manifests/haranir.toml
manifests/skyborne.toml
manifests/skyborne-prep.toml
```
