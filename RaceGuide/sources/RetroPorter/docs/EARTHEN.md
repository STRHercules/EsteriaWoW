# Earthen Retail discovery and art retroport

## Status

Earthen has completed the same discovery and art-conversion milestone as Mag'har Orc, Highmountain Tauren, and Mechagnome.

Verified against live Retail build:

```text
12.1.0.69933
WOW-69933patch12.1.0_Retail
```

Canonical converted staging root:

```text
G:\RetroPorterWork\earthen\output\patch-root\custom\earthen\
```

Do not copy the converted files over the base Dwarf or any existing Esteria race. The converter rewrites internal references into the `custom\earthen` namespace so the eventual MPQ can remain isolated.

## Retail race identity

Earthen is unusual because Retail represents the playable race with two `ChrRaces` rows that share the same appearance graph.

```text
RaceID 84
ClientFileString: EarthenDwarf
FactionID: 2
LoreDescription: Horde-facing Earthen row
Race_related: 85

RaceID 85
ClientFileString: EarthenDwarf
FactionID: 3
LoreDescription: Alliance-facing Earthen row
Race_related: 84
```

Both rows map to the same player models:

```text
Male ChrModelID: 195
DisplayID: 115279
Model FDID: 5548261
Path: character\earthendwarf\earthendwarfmale.m2

Female ChrModelID: 196
DisplayID: 115281
Model FDID: 5548259
Path: character\earthendwarf\earthendwarffemale.m2
```

Both models reference skeleton FDID `5752243`.

The main Retail Earthen row falls back to Dwarf RaceID 3 for model/texture fallback and helmet animation scaling. The Alliance-facing RaceID 85 points its visual fallback at RaceID 84.

The RetroPorter discovery layer was generalized during this pass so a `RaceSpec` can identify multiple Retail race rows that share one visual race. The discovery report now stores both `race_ids` and `races`, while keeping `race_id`/`race` as the canonical first row for compatibility with earlier tooling.

## Customization graph

Current live discovery totals:

```text
36 customization options
308 customization choices
675 customization elements
22 linked ChrCustomizationGeoset rows
126 linked ChrCustomizationSkinnedModel rows
466 linked ChrCustomizationMaterial rows
22 linked ChrCustomizationBoneSet rows
448 discovered FileDataIDs before safe filtering
```

Major customization categories include:

```text
Skin Color
Face
Hair Style
Hair Color
Beard Style
Eyebrows
Eye Color
Eyesight
Gem Color
Belt
Horn Style
Hand FX
Right Shoulder
Left Shoulder
Torso
Arms
Legs
Hands
```

This is substantially richer than Wrath's fixed character customization schema.

## External collection geometry

Earthen uses Retail's `ChrCustomizationSkinnedModel` system heavily. The 126 linked skinned-model records resolve to two collection M2s:

```text
Female collection
FDID: 5792407
item\objectcomponents\collections\earthenextras_ed_f.m2

Male collection
FDID: 5792408
item\objectcomponents\collections\earthenextras_ed_m.m2
```

These collections carry a large portion of the selectable Earthen extras used for body and crystal/stone appearance choices.

The collection family also has a directly named texture that is injected into the asset plan because it is not guaranteed to appear as a direct `ChrCustomizationMaterial` FileDataID:

```text
FDID: 5688294
item\objectcomponents\collections\earthenextras_ed_m_5688294.blp
```

The two collection models are treated as core models, not optional metadata.

## Asset filtering

The safe Earthen asset roots are currently:

```text
character\earthendwarf\
item\objectcomponents\collections\earthenextras_
```

The initial scaffold incorrectly guessed `character\earthen\` and a Dwarf shared root. Live discovery showed that the player art actually resides under `character\earthendwarf\`.

The discovery graph also contains shared Human eye assets introduced through modern requirement/customization relationships. Those are deliberately excluded from the conservative first-pass asset slice, matching the strategy used for Mag'har and Highmountain.

## Retail `.bone` overrides

Earthen discovery contains 22 bone-set overrides, split between the male and female base player models.

The `.bone` files are not converted because Wrath has no direct equivalent to Retail's `ChrCustomizationBoneSet` behavior.

They are recorded as unsupported instead of silently copied.

A future full-fidelity Earthen implementation may need to bake choices that depend on those bone overrides into alternate model/geoset variants or add custom client support.

## Conversion result

Asset plan:

```text
413 selected FileDataIDs
22 unsupported Retail-only `.bone` assets
```

Converter result:

```text
526 reported outputs
109 ok
40 lossy
368 passthrough
9 skipped
0 failed
```

Canonical files actually written to patch-root:

```text
517 files total
4 M2
4 SKIN
109 ANIM
400 BLP
```

The difference between reported outputs and files physically written is the 9 skipped CASC inputs.

## Why 40 files are marked lossy

The high lossy count is expected and does not indicate 40 broken models.

Eight are the four M2/SKIN pairs:

```text
character/earthendwarf/earthendwarfmale.m2
earthendwarfmale00.skin
character/earthendwarf/earthendwarffemale.m2
earthendwarffemale00.skin
item/objectcomponents/collections/earthenextras_ed_m.m2
earthenextras_ed_m00.skin
item/objectcomponents/collections/earthenextras_ed_f.m2
earthenextras_ed_f00.skin
```

Expected M2/SKIN losses include:

- modern replaceable texture types that 3.3.5a does not understand
- post-Wrath material blend modes
- modern shader batches being reset to Wrath-compatible combiners
- Retail shadow batches being dropped in favor of Wrath's blob shadows
- Legion+ LOD data being removed
- modern chunks such as `LDV1` and `TXAC` being removed
- modern split animation blend times being flattened
- post-Wrath flags being cleared

The other 32 lossy outputs are skin-color BLPs that are 2048x1024 on Retail. Converter downsizes them to 1024x512 because its Wrath-compatible maximum texture dimension is 1024.

That is an intentional compatibility conversion, not missing data.

## Skipped CASC assets

Nine Earthen BLPs currently fail before conversion because CASC returns payloads that are not valid BLTE streams:

```text
5662344 character\earthendwarf\earthendwarffemale_skin_color_5662344.blp
5662345 character\earthendwarf\earthendwarffemale_skin_color_5662345.blp
5565688 character\earthendwarf\earthendwarfmale_face_5565688.blp
5742569 character\earthendwarf\earthendwarfmale_face_5742569.blp
5742570 character\earthendwarf\earthendwarfmale_face_5742570.blp
5742571 character\earthendwarf\earthendwarfmale_face_5742571.blp
5742572 character\earthendwarf\earthendwarfmale_face_5742572.blp
5742573 character\earthendwarf\earthendwarfmale_face_5742573.blp
5742574 character\earthendwarf\earthendwarfmale_face_5742574.blp
```

This is the same class of source-side CASC issue already seen with Mag'har, Highmountain, and Mechagnome.

Do not block the first playable Earthen integration on these nine files.

## Converted model verification

All four M2s inspect as version 264, flat/non-chunked, and `wotlk_compatible: True`.

### Male base

```text
18,561 vertices
229 bones
361 sequences
13 textures
14 materials
2 cameras
1 skin profile
```

### Female base

```text
15,840 vertices
245 bones
355 sequences
13 textures
14 materials
2 cameras
1 skin profile
```

### Male collection

```text
56,684 vertices
110 bones
1 sequence
5 textures
10 materials
1 skin profile
```

### Female collection

```text
60,596 vertices
111 bones
1 sequence
5 textures
10 materials
1 skin profile
```

The female collection is important to watch during future geometry baking because 60,596 vertices is already relatively close to Wrath's 65,535 vertex ceiling. Any attempt to merge additional geometry into that exact M2 should validate the compacted vertex count before packaging.

## Wrath integration implications

A basic Earthen can be made from the dedicated male/female base bodies and a reduced set of stable appearance choices.

A full Retail-like Earthen cannot be expressed purely through stock Wrath DBCs because Retail uses 126 `ChrCustomizationSkinnedModel` records and 22 bone-set overrides.

Likely strategies are:

1. Start with fixed/default collection geometry and map skin/face/hair/beard into Wrath fields.
2. Bake important collection-model choices into alternate player-model/geoset variants.
3. Extend the client so it can reproduce a subset of Retail's external skinned-model behavior.
4. Avoid exposing choices whose visible result depends on unsupported `.bone` data until they are deliberately recreated.

The shoulder, torso, arm, leg, hand, belt, horn, gem, and hand-FX categories should be treated as second-stage work after a stable selectable Earthen exists.

## Generated reports

```text
G:\RetroPorterWork\earthen\reports\discovery.json
G:\RetroPorterWork\earthen\reports\asset-plan.json
G:\RetroPorterWork\earthen\reports\asset-convert-dryrun.json
G:\RetroPorterWork\earthen\reports\asset-convert.json
```

## Re-run commands

```powershell
python -m retroporter extract-db2 --race earthen
python -m retroporter discover --race earthen
python -m retroporter plan-assets --race earthen
python -m retroporter convert-assets --race earthen --dry-run
python -m retroporter convert-assets --race earthen
```

## Next target

If continuing the art-port coverage before DBC integration, the remaining planned race is Haranir.

Do not assume the current Haranir scaffold identifiers are correct. Verify its live `ChrRaces`, models, asset roots, and customization graph first, exactly as was done for the prior races.
