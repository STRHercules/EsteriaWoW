# Haranir Retail Discovery and Art Retroport

## Status

Haranir art conversion is complete against live Retail build `12.1.0.69933` with zero failed conversions.

Canonical output:

```text
G:\RetroPorterWork\haranir\output\patch-root\custom\haranir\
```

## Retail identity

Retail's internal spelling is `Harronir`, even though the player-facing race name is `Haranir`.

Haranir uses two faction-facing `ChrRaces` rows that share one visual model pair:

```text
RaceID 86
RaceID 91
ClientFileString: Harronir
```

Male:

```text
ChrModelID: 200
DisplayID: 116539
Model FDID: 5422149
Path: character\harronir\harronirmale.m2
Skeleton FDID: 4690415
```

Female:

```text
ChrModelID: 201
DisplayID: 116687
Model FDID: 5422147
Path: character\harronir\harronirfemale.m2
Skeleton FDID: 4993122
```

## Customization graph

Live discovery found:

```text
57 customization options
568 choices
1,444 elements
51 linked geosets
250 linked ChrCustomizationSkinnedModel rows
1,017 linked materials
3 linked ChrCustItemGeoModify rows
950 discovered FileDataIDs before safe filtering
```

Notable options include:

- skin color
- face
- hair style/color/highlight
- eyebrows
- tusks
- ears
- nose
- eye color / eyesight
- face and body fur patterns
- fur color
- shoulder spines and spine color
- feet
- loincloth / underclothes colors
- hair spines
- beard, sideburns, moustache
- jewelry, necklaces, earrings
- face and body paint
- paint color

## External customization geometry

249 of the 250 `ChrCustomizationSkinnedModel` rows use two Haranir-specific collection models:

```text
6255032 models\item\unk_exp11_6255032_hr_m\6255032_hr_m.m2
6255031 models\item\unk_exp11_6255031_hr_f\6255031_hr_f.m2
```

The remaining linked collection record points at a shared Dracthyr collection model and is treated as requirement/shared-data noise for the initial safe slice.

Stock Wrath has no direct `ChrCustomizationSkinnedModel` equivalent. Full customization will eventually require either baking selected collection geometry into player-model variants or client changes.

## Asset slice

The initial safe slice includes:

- the two base Haranir player M2s
- the two Haranir customization collection M2s
- customization BLPs under `character\harronir\...`
- Converter-resolved M2 dependencies such as SKIN/ANIM files

Human/shared requirement assets and the unrelated Dracthyr collection model are not part of the initial Haranir slice.

## Conversion result

Converter report:

```text
1,053 accounted outputs
108 ok
189 lossy
731 passthrough
25 skipped
0 failed
```

Physical patch-root files:

```text
1,028 files
4 M2
4 SKIN
108 ANIM
912 BLP
```

The high lossy count is expected:

```text
181 BLP texture downscales
4 M2 conversions
4 SKIN conversions
```

The BLPs exceed Wrath's configured 1024-pixel texture cap and are resized during conversion.

## Verified converted models

Male base:

```text
M2 v264
24,087 vertices
231 bones
401 sequences
wotlk_compatible: True
```

Female base:

```text
M2 v264
24,042 vertices
247 bones
397 sequences
wotlk_compatible: True
```

Male collection:

```text
M2 v264
59,563 vertices
79 bones
1 sequence
wotlk_compatible: True
```

Female collection:

```text
M2 v264
55,233 vertices
65 bones
1 sequence
wotlk_compatible: True
```

The male collection model is relatively close to the 65,535-vertex Wrath limit. Any later baked-geometry workflow must budget vertices carefully.

## Skipped BLPs

25 Haranir BLPs currently return malformed/non-BLTE payloads from CASC. They include several male/female face, fur, hair-color, jewelry, quill-color, and skin-color textures.

This is the same CASC behavior seen on smaller subsets of Mag'har, Highmountain, Mechagnome, and Earthen. The skips did not prevent any of the four core/customization M2s from converting.

See the exact list in:

```text
G:\RetroPorterWork\haranir\reports\asset-convert.json
```

## Reports

```text
G:\RetroPorterWork\haranir\reports\discovery.json
G:\RetroPorterWork\haranir\reports\asset-plan.json
G:\RetroPorterWork\haranir\reports\asset-convert-dryrun.json
G:\RetroPorterWork\haranir\reports\asset-convert.json
```

## DBC integration note

Haranir's Retail race IDs must not be reused blindly as Esteria race IDs. The eventual Wrath integration still needs Esteria-specific allocation, DBC flattening, and an explicit decision about how much external collection geometry to expose in 3.3.5a.
