# Skyborne Retroport Findings

## Source client

Skyborne was verified from the installed **World of Warcraft: Forever beta** client, not Retail.

```text
CASC root: D:\Blizzard\World of Warcraft
Product:   wow_classic_beta
Version:   1.60.1.70009
Build:     WOW-70009patch1.60.1_ForeverBeta
Locale:    enUS
```

`CreatureDisplayInfo.db2` is currently encrypted with TACT key `057DC814574BD5B6`, which is not in the public keyring used by Converter. This did not block race/model/customization discovery because the required relationships were available through `ChrRaces`, `ChrRaceXChrModel`, `ChrModel`, customization DB2s, the listfile, and direct CASC model discovery.

## Verified race identity

Forever contains two paired playable Skyborne rows:

```text
RaceID 95  High Order Skyborne
RaceID 96  Windshaper Skyborne
ClientFileString: Skyborne
ClientPrefix: Sb
```

They reference each other through `Race_related` and share the same visual `ChrModel` records.

Male:

```text
ChrModelID: 218
DisplayID: 139407
Model FDID: 7478487
Path: models\creature\unk_exp00_7478487\7478487.m2
Skeleton FDID: 4690403
```

Female:

```text
ChrModelID: 219
DisplayID: 139408
Model FDID: 7478494
Path: models\creature\unk_exp00_7478494\7478494.m2
Skeleton FDID: 4690402
```

Unlike the earlier races, Skyborne's base bodies are stored under generic `models\creature\unk_exp00_*` paths rather than a named `character\skyborne` directory.

## Customization graph

Live Forever beta discovery found:

```text
37 customization options
497 choices
1,556 customization elements
97 linked ChrCustomizationGeoset rows
96 linked ChrCustomizationSkinnedModel rows
1,261 linked ChrCustomizationMaterial rows
40 linked ChrCustomizationBoneSet rows
1,201 discovered FileDataIDs before safe filtering
```

Representative options include:

```text
Face
Skin Color
Hair Style
Hair Color
Facial Hair
Ears
Horns
Blindfold
Body Tattoo
Body Tattoo Color
Eye Color
Eyesight
Eye Style
Feathers
Feather Color
Eyebrow Style
Face Tattoo
Face Tattoo Color
Earrings
Jewelry Color
```

## Body and collection geometry

All 40 Skyborne bone-set overrides target the two base body models:

```text
7478487 -> male ChrModel 218
7478494 -> female ChrModel 219
```

Dedicated Skyborne customization collections:

```text
7845093 -> male, 29 linked skinned-model uses
7845092 -> female, 33 linked skinned-model uses
```

Skyborne also intentionally reuses the Blood Elf Demon Hunter collections:

```text
2763973 item\objectcomponents\collections\demonhuntergeosets_be_m.m2
2763972 item\objectcomponents\collections\demonhuntergeosets_be_f.m2
```

Each is referenced by 17 Skyborne skinned-model rows.

The bulk of Skyborne customization textures are stored under `character\bloodelf\...`. The asset planner therefore includes only Blood Elf textures that are actually present in the Skyborne customization graph. Requirement-driven Human and Dracthyr assets remain outside the safe slice.

## Asset plan

The race-specific safe roots are:

```text
character\bloodelf\
models\creature\unk_exp00_7478487\
models\creature\unk_exp00_7478494\
models\unknown\unk_exp00_7845092\
models\unknown\unk_exp00_7845093\
item\objectcomponents\collections\demonhuntergeosets_be_
```

Core M2 FileDataIDs:

```text
7478487
7478494
7845092
7845093
2763972
2763973
```

The planner selected 1,107 FileDataIDs and marked 40 `.bone` overrides unsupported because stock Wrath has no direct equivalent.

## Conversion result

Canonical output:

```text
G:\RetroPorterWork\skyborne\output\patch-root\custom\skyborne\
```

Physical output:

```text
1,219 files
6 M2
6 SKIN
106 ANIM
1,101 BLP
```

Converter report:

```text
12 lossy
1,207 passthrough
0 skipped
0 failed
```

The 12 lossy files are exactly the six M2/SKIN pairs. No Skyborne textures were skipped.

## Verified converted models

Male base:

```text
M2 v264
42,031 vertices
250 bones
395 sequences
wotlk_compatible: True
```

Female base:

```text
M2 v264
35,974 vertices
245 bones
389 sequences
wotlk_compatible: True
```

Male Skyborne collection:

```text
M2 v264
2,299 vertices
52 bones
1 sequence
wotlk_compatible: True
```

Female Skyborne collection:

```text
M2 v264
2,556 vertices
42 bones
1 sequence
wotlk_compatible: True
```

Male Blood Elf Demon Hunter collection:

```text
M2 v264
3,506 vertices
40 bones
1 sequence
wotlk_compatible: True
```

Female Blood Elf Demon Hunter collection:

```text
M2 v264
3,165 vertices
37 bones
1 sequence
wotlk_compatible: True
```

Skyborne therefore has much more vertex headroom for future geometry baking than Earthen or Haranir.

## Wrath integration implications

Skyborne still uses systems Wrath does not natively expose:

- `ChrCustomizationSkinnedModel`
- `.bone` overrides
- modern independent tattoo/feather/horn/accessory dimensions
- modern material layering

The likely first playable implementation should use the dedicated male/female bodies plus a deliberately selected default set of collection geosets. Full parity will require either baking selected collection geometry into player M2 variants or extending the client customization system.

Because Skyborne reuses Blood Elf textures and Demon Hunter collections, do not overwrite stock Blood Elf paths in Esteria. Keep the converted race under the current `custom\skyborne\...` namespace and point generated DBC/client records there.

## Re-run commands

```powershell
python -m retroporter extract-db2 --race skyborne --source-root "D:\Blizzard\World of Warcraft" --source-product wow_classic_beta
python -m retroporter discover --race skyborne
python -m retroporter plan-assets --race skyborne
python -m retroporter convert-assets --race skyborne --dry-run --source-root "D:\Blizzard\World of Warcraft" --source-product wow_classic_beta
python -m retroporter convert-assets --race skyborne --source-root "D:\Blizzard\World of Warcraft" --source-product wow_classic_beta
```
