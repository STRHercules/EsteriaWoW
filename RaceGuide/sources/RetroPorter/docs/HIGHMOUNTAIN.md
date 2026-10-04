# Highmountain Tauren Retroport

## Status

The first Highmountain Tauren art retroport is complete against Retail `12.1.0.69933`.

Canonical output:

```text
G:\RetroPorterWork\highmountain\output\patch-root\custom\highmountain\
```

Do not copy Blizzard source data into this Git repository.

## Verified Retail identity

```text
Retail RaceID: 28
ClientFileString: HighmountainTauren
Name: Highmountain Tauren
Fallback race: Tauren, RaceID 6
```

### Male

```text
ChrModelID: 55
DisplayID: 75080
Core model FDID: 1630218
Model: character\highmountaintauren\male\highmountaintaurenmale.m2
Skeleton FDID: 4690423
```

### Female

```text
ChrModelID: 56
DisplayID: 75081
Core model FDID: 1630402
Model: character\highmountaintauren\female\highmountaintaurenfemale.m2
Skeleton FDID: 4690422
```

Unlike Mag'har Orc, Highmountain uses dedicated player M2s rather than only a parent-race body plus alternate materials.

## Customization graph

Discovery totals:

```text
44 options
251 choices
487 elements
104 linked ChrCustomizationGeoset rows
274 linked ChrCustomizationMaterial rows
9 linked ChrCustomizationBoneSet rows
245 discovered FileDataIDs before safe-slice filtering
```

Important male options include:

```text
Face
Skin Color
Horn Style
Horn Markings
Beard
Hair
Eye Color
Body Paint
Body Paint Color
Foremane
Nose Piercing
Headdress
Horn Wraps
Horn Decoration
Tail Decoration
Tail
Jewelry Color
Feather
Horn Color
Eyesight
Eye Style
```

Important female options include:

```text
Face
Skin Color
Hair
Eye Color
Horn Style
Horn Markings
Foremane
Earrings
Body Paint
Body Paint Color
Feather
Hair Decoration
Jewelry Color
Nose Piercing
Headdress
Horn Wraps
Horn Decoration
Horn Color
Tail
Tail Decoration
Necklace
Eyesight
Eye Style
```

This confirms that a full fidelity port cannot be represented by Wrath's stock five appearance fields without flattening/combining categories.

## Asset planning

The reusable planner now uses race-specific asset roots and core-model IDs from `RaceSpec`. It is no longer Mag'har-hardcoded.

Highmountain initial safe slice:

```text
181 selected assets
9 unsupported Retail .bone assets
```

The selected slice consists of the two player M2s and BLPs under:

```text
character\highmountaintauren\
```

The `.bone` overrides are intentionally recorded as unsupported because stock Wrath has no equivalent mechanism.

## Conversion result

Real conversion report:

```text
286 result records
103 ok
4 lossy
172 passthrough
7 skipped
0 failed
```

Physical patch output:

```text
279 files
2 M2
2 SKIN
103 ANIM
172 BLP
```

The four lossy records are the two player M2s and their SKIN files. Losses are expected modern-to-Wrath reductions involving shaders, LOD data, shadow batches, replaceable texture behavior, and similar post-Wrath features.

## Verified converted models

### Male

```text
M2 version: 264
Chunked: False
Vertices: 40,166
Bones: 227
Sequences: 15
Textures: 13
Materials: 12
Skin profiles: 1
wotlk_compatible: True
```

### Female

```text
M2 version: 264
Chunked: False
Vertices: 36,188
Bones: 228
Sequences: 13
Textures: 14
Materials: 13
Skin profiles: 1
wotlk_compatible: True
```

The relatively small sequence counts are inherited from the dedicated Highmountain model/skeleton arrangement and should be visually tested in the Wrath client once DBC integration exists.

## Seven skipped eye textures

These CASC entries currently fail before BLP conversion with invalid/non-BLTE payloads:

```text
character\highmountaintauren\eyes00_00_3649403.blp
character\highmountaintauren\eyes00_01_3649404.blp
character\highmountaintauren\eyes00_02_3649405.blp
character\highmountaintauren\eyes00_03_3649406.blp
character\highmountaintauren\eyes00_04_3649407.blp
character\highmountaintauren\eyes00_05_3649408.blp
character\highmountaintauren\eyes00_06_3649409.blp
```

This is the same general CASC issue encountered with a subset of Mag'har eye textures. It does not block the body, skin, horn, tattoo, or main customization texture port.

## Modern eye contamination

Retail injects some shared/requirement-gated eye choices into the customization graph. Discovery therefore sees Dracthyr and Human eye assets in addition to Highmountain assets.

The safe-slice planner deliberately excludes anything outside `character\highmountaintauren\` unless it is an explicitly listed core model. Do not broaden that rule casually.

## DBC implications

Highmountain should eventually receive its own Esteria race ID and its own Wrath character DBC rows.

Minimum first playable pass should expose:

1. default male/female body
2. skin color
3. face
4. hair
5. horn style

After that, prioritize:

6. beard/foremane
7. horn color/markings
8. body paint
9. tail variants
10. accessories and jewelry

Many Highmountain choices map to modern geoset types. Those geoset relationships should be preserved in the DBC-flattening metadata even when the first Wrath UI exposes only a subset.

## Reproduction commands

```powershell
python -m retroporter extract-db2 --race highmountain
python -m retroporter discover --race highmountain
python -m retroporter plan-assets --race highmountain
python -m retroporter convert-assets --race highmountain --dry-run
python -m retroporter convert-assets --race highmountain
```

Generated reports live under:

```text
G:\RetroPorterWork\highmountain\reports\
```
