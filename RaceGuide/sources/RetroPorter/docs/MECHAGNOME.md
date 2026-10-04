# Mechagnome Retroport Notes

## Status

The first-pass Mechagnome art retroport is complete against live Retail build `12.1.0.69933`.

Canonical converted output:

```text
G:\RetroPorterWork\mechagnome\output\patch-root\custom\mechagnome\
```

Do not treat this as a fully playable race yet. The converted art is ready for the later Wrath DBC/client integration phase.

## Verified Retail identity

```text
Retail RaceID: 37
ClientFileString: Mechagnome
Fallback race: Gnome, RaceID 7
```

Male:

```text
ChrModelID: 73
DisplayID: 90786
Model FDID: 2622502
Path: character\mechagnome\male\mechagnomemale.m2
Skeleton FDID: 4690408
```

Female:

```text
ChrModelID: 74
DisplayID: 90787
Model FDID: 2564806
Path: character\mechagnome\female\mechagnomefemale.m2
Skeleton FDID: 4690408
```

## The important Mechagnome difference

Mechagnome is the first target in this project where the Retail customization system cannot be represented as only textures plus geosets.

Discovery found:

```text
23 customization options
236 choices
694 customization elements
46 linked ChrCustomizationGeoset rows
78 linked ChrCustomizationSkinnedModel rows
402 linked ChrCustomizationMaterial rows
28 linked ChrCustomizationBoneSet rows
393 FileDataIDs before safe-slice filtering
```

The cybernetic geometry is primarily supplied through two collection models:

```text
Male collection model
FDID: 2628212
item\objectcomponents\collections\collections_mechagnome_mg_m.m2

Female collection model
FDID: 2628213
item\objectcomponents\collections\collections_mechagnome_mg_f.m2
```

Their required collection textures are:

```text
2628215 item\objectcomponents\collections\collections_mechagnome_2_2628215.blp
2628216 item\objectcomponents\collections\collections_mechagnome_3_2628216.blp
```

Retail's `ChrCustomizationSkinnedModel` rows select geosets from those collection models. Arm, leg, head modification, ear, antenna, visor, receiver, and similar choices do not simply toggle a geoset on the base player M2.

That distinction matters when we later make the race playable in Wrath.

## Customization options

Male `ChrModelID 73` includes:

```text
360 Skin Color
361 Face
362 Hair Style
363 Hair Color
364 Facial Hair
366 Arm Upgrade
367 Leg Upgrade
415 Modification
794 Eye Color
797 Paint
6380 Eyesight
8566 Eye Style
```

Female `ChrModelID 74` includes:

```text
368 Skin Color
369 Face
370 Hair Style
371 Hair Color
374 Arm Upgrade
375 Leg Upgrade
416 Modification
795 Eye Color
799 Paint
6381 Eyesight
8567 Eye Style
```

## Arm and leg upgrades

The mechanical body choices are represented by collection-model geosets.

Male arm upgrade uses collection model `2628212` with four choices:

```text
Standard
Steel Plating
Iron Grips
Thorium Grips
```

Female arm upgrade uses collection model `2628213` with the same four choices.

Male and female leg upgrades likewise select collection-model geosets, with extra collection geosets participating in the final appearance.

This is not natively expressible through 3.3.5a `CharHairGeosets.dbc` or `CharacterFacialHairStyles.dbc` alone.

## Modification choices

The Modification category is also heavily dependent on `ChrCustomizationSkinnedModel`.

Examples include:

```text
Ears
Antennas
Transducers
Infra-Sight
Plated Ears
Receivers
Conductors
Optics
Cyber Ears
Wires
Earphones
Tactical Visor
Mech Ears
Sensors
Transceivers
Bifocals
Bionic Ears
Feelers
Sonic Amplifiers
```

Many of these choices combine a normal customization geoset on the base body with one or more geosets from the male/female collection model.

## Shared Gnome material dependency

Mechagnome's material graph heavily reuses Gnome character textures.

The discovery graph contained:

```text
281 character\gnome\... BLPs
25 character\mechagnome\... BLPs
42 character\dracthyr\... BLPs
8 character\human\... BLPs
1 item/objectcomponents BLP discovered directly
```

The Gnome textures are legitimate Mechagnome dependencies and are included in the safe asset slice.

The Dracthyr and Human eye assets are shared requirement-driven Retail customization noise, as seen with previous races, and are intentionally excluded from the initial safe slice.

The two collection textures listed above are explicitly injected into the plan because they are referenced by the collection M2s rather than by `ChrCustomizationMaterial`.

## Asset planner changes made for Mechagnome

`RaceSpec` now supports `required_file_ids` in addition to `core_model_file_ids`.

This lets a race declare dependencies that are not reached directly from the DB2 customization material graph.

For Mechagnome the current source roots are:

```text
character\mechagnome\
character\gnome\
item\objectcomponents\collections\collections_mechagnome_
```

Core/customization models:

```text
2564806 female base body
2622502 male base body
2628212 male collection model
2628213 female collection model
```

Required extra files:

```text
2628215 collection texture
2628216 collection texture
```

## Conversion result

The real conversion completed with zero failed inputs:

```text
362 conversion report entries
360 files written

46 ok
8 lossy
306 passthrough
2 skipped
0 failed
```

Written output by extension:

```text
4 M2
4 SKIN
46 ANIM
306 BLP
```

The eight lossy outputs are exactly the four M2/SKIN pairs:

```text
character/mechagnome/male/mechagnomemale.m2
mechagnomemale00.skin

character/mechagnome/female/mechagnomefemale.m2
mechagnomefemale00.skin

item/objectcomponents/collections/collections_mechagnome_mg_m.m2
collections_mechagnome_mg_m00.skin

item/objectcomponents/collections/collections_mechagnome_mg_f.m2
collections_mechagnome_mg_f00.skin
```

Losses are the expected modern-to-Wrath shader, blend, LOD, and skin-batch downgrade behavior.

## Verified converted model properties

Male base body:

```text
M2 version: 264
chunked: False
vertices: 17,763
bones: 202
sequences: 61
wotlk_compatible: True
```

Female base body:

```text
M2 version: 264
chunked: False
vertices: 18,455
bones: 214
sequences: 63
wotlk_compatible: True
```

Male collection model:

```text
M2 version: 264
chunked: False
vertices: 26,473
bones: 67
sequences: 1
wotlk_compatible: True
```

Female collection model:

```text
M2 version: 264
chunked: False
vertices: 26,079
bones: 60
sequences: 1
wotlk_compatible: True
```

All four are below Wrath's practical 65,535 vertex ceiling after conversion.

## Two skipped textures

These two male Mechagnome textures currently fail during CASC read before BLP conversion:

```text
3060787 character\mechagnome\male\mechagnomemale_paint_3060787.blp
3060788 character\mechagnome\male\mechagnomemale_hair_color_3060788.blp
```

They produce the same invalid/non-BLTE payload pattern seen with some eye textures on Mag'har and Highmountain.

They do not block the converted player models or collection geometry.

## Bone-set limitation

Retail defines 28 `ChrCustomizationBoneSet` records for Mechagnome.

They point at `.bone` files associated with the male/female base M2s. Converter does not have a 3.3.5a equivalent for these files, so they are marked unsupported and are not copied into the canonical patch root.

This means some Retail appearance deformations may not be reproduced by the converted models alone.

The later integration phase must determine whether each visible choice can be approximated without those bone overrides or whether specific variants need to be baked into custom M2s.

## Wrath integration consequence

Stock Wrath character customization has no `ChrCustomizationSkinnedModel` system.

Therefore, simply adding Mechagnome rows to `CharSections`, `CharHairGeosets`, and `CharacterFacialHairStyles` will not reproduce its mechanical upgrades.

The likely paths are:

1. Bake the relevant collection-model geosets into one or more custom player M2 variants and expose them through Wrath-visible geoset IDs.
2. Extend the 3.3.5a client to load and toggle the external collection model in a Retail-like way.
3. Start with a reduced Mechagnome feature set using a fixed/default mechanical configuration, then add the more complex variants later.

For the first playable implementation, option 1 or option 3 is substantially simpler than recreating Retail's full runtime skinned-model system.

## Generated reports

```text
G:\RetroPorterWork\mechagnome\reports\discovery.json
G:\RetroPorterWork\mechagnome\reports\asset-plan.json
G:\RetroPorterWork\mechagnome\reports\asset-convert-dryrun.json
G:\RetroPorterWork\mechagnome\reports\asset-convert.json
```

## Re-run commands

```powershell
cd R:\Users\Zach\Documents\GitHub\RetroPorter

python -m retroporter extract-db2 --race mechagnome
python -m retroporter discover --race mechagnome
python -m retroporter plan-assets --race mechagnome
python -m retroporter convert-assets --race mechagnome --dry-run
python -m retroporter convert-assets --race mechagnome
```

Regeneration is only necessary if Retail changes, Converter changes, the safe asset slice changes, or `G:\RetroPorterWork\mechagnome` is removed.
