# DBC Integration Strategy

## Purpose

Retail art conversion alone does not create a playable 3.3.5a race. Retail's character-customization system is substantially newer than Wrath's fixed character fields.

The next phase must translate Retail customization intent into the smaller set of DBC structures understood by build 12340.

## The source and target systems are different

Modern Retail uses a graph centered on tables such as:

```text
ChrModel
ChrCustomizationOption
ChrCustomizationChoice
ChrCustomizationElement
ChrCustomizationGeoset
ChrCustomizationMaterial
ChrCustomizationSkinnedModel
ChrCustomizationBoneSet
ChrCustomizationCondModel
ChrCustomizationDisplayInfo
```

Wrath 3.3.5a expects fixed appearance values and older DBCs such as:

```text
ChrRaces.dbc
CreatureModelData.dbc
CreatureDisplayInfo.dbc
CharSections.dbc
CharHairGeosets.dbc
CharacterFacialHairStyles.dbc
BarberShopStyle.dbc
CharHairTextures.dbc
```

There is no one-to-one conversion for many modern choices.

## Required Esteria template DBCs

Before generating race DBC output, extract the **highest-priority copies currently used by the Esteria client**, not clean Blizzard 3.3.5a copies.

At minimum preserve and work from:

```text
DBFilesClient\ChrRaces.dbc
DBFilesClient\CreatureModelData.dbc
DBFilesClient\CreatureDisplayInfo.dbc
DBFilesClient\CharSections.dbc
DBFilesClient\CharHairGeosets.dbc
DBFilesClient\CharacterFacialHairStyles.dbc
DBFilesClient\BarberShopStyle.dbc
DBFilesClient\CharHairTextures.dbc
```

Place working copies outside source control, for example:

```text
G:\RetroPorterWork\wrath-templates\DBFilesClient\
```

Do not overwrite the live client while developing the generator.

## Race ID is intentionally not assigned yet

Retail Mag'har is RaceID `36`. That is **not** automatically the RaceID Esteria should use.

The eventual Esteria race ID must be chosen to avoid collisions with existing custom races and any client-side RaceMask assumptions.

Do not write Mag'har rows into Esteria DBCs until the target race ID is explicitly chosen.

Every generated row must translate:

```text
Retail race 36 -> Esteria custom Mag'har race ID
```

## Asset namespace

All generated DBC references must point to the canonical converted namespace:

```text
custom\maghar\character\orc\...
```

Do not point the Mag'har race at normal `character\orc\...` paths. Doing so would make the race depend on or replace base Orc assets.

## Model and display rows

The current converted player bodies are:

```text
custom\maghar\character\orc\male\orcmale_hd.m2
custom\maghar\character\orc\female\orcfemale_hd.m2
custom\maghar\character\orc\male\orcmaleupright.m2
```

The DBC phase needs new `CreatureModelData` and `CreatureDisplayInfo` records that reference these custom paths and do not collide with existing Esteria IDs.

The normal male and female models should be established first. Upright male should be treated separately because Retail implements it as a conditional model rather than a simple material/geoset choice.

## `ChrRaces.dbc`

Create one custom Mag'har race row based on the closest working Esteria Orc/custom-race pattern.

Important areas to preserve or deliberately choose include:

- client prefix and file string
- male and female display/model linkage
- faction/team behavior required by Esteria
- starting location behavior
- cinematic and login glue behavior
- base language
- facial customization support flags
- helmet scaling/fallback behavior

Do not copy Retail `ChrRaces.db2` fields blindly. Wrath's `ChrRaces.dbc` layout and semantics are different.

## `CharSections.dbc`

Wrath uses `CharSections` to connect race, sex, section type, variation index, and color index to texture paths.

For Mag'har, the first useful mapping is:

```text
Retail Skin Color -> Wrath skin section/color variation
Retail Face       -> Wrath face section/variation
Retail Hair Color -> Wrath hair texture/color where applicable
```

Modern Retail often composes multiple material layers that Wrath cannot reproduce dynamically. Therefore some Retail combinations may need to be flattened into precomposed BLPs rather than represented as separate runtime layers.

The initial converted source textures already include families such as:

```text
orcmaleclanskin00_XX.blp
orcfemaleclanskin00_XX.blp
orc*clanfaceupperXX_YY.blp
orc*clannakedtorsoskin00_XX.blp
orc*clannakedpelvisskin00_XX.blp
```

A generator should group these by sex, face index, and skin color, then create deterministic Wrath `CharSections` rows.

## `CharHairGeosets.dbc`

Retail hair choices are represented through `ChrCustomizationChoice` plus linked `ChrCustomizationGeoset` records.

Wrath expects a much simpler relationship:

```text
RaceID
SexID
VariationID
GeosetID
ShowsScalp
```

For each normal Mag'har hair choice:

1. Resolve the choice's customization element.
2. Resolve its `ChrCustomizationGeoset` record.
3. Determine which Retail geoset number corresponds to the actual player-model hair submesh.
4. Write a new `CharHairGeosets` row for the Esteria race ID.
5. Test scalp visibility in client.

Do not assume Retail `GeosetType` values map directly to Wrath `CharHairGeosets.GeosetID`. Validate against the converted model's submesh/geoset IDs.

## `CharacterFacialHairStyles.dbc`

Wrath provides five geoset slots per race/sex/variation entry. Mag'har's modern options are richer than this.

Candidates that may need to share this limited system include:

```text
Beard
Sideburns
Tusks
Earrings
Piercings
Nose Ring
Necklace
```

Not all of these should necessarily be exposed independently in the first version.

A practical first pass is:

- fully support beard/sideburn appearance that maps cleanly to model geosets
- preserve the default tusks expected by the model
- add accessory combinations only where they fit into the available five slots without breaking normal equipment rendering

Later, Esteria's custom character-creation UI/client code can expose more independent appearance dimensions if desired.

## Posture: Hunched vs Upright

Retail male Mag'har option `353` provides Hunched/Upright choices.

The upright choice points to `ChrCustomizationCondModelID=2`. This is a model swap, not merely a texture or hair geoset.

Stock Wrath character data has no dedicated posture field.

Initial implementation options are:

1. Make one posture the default for the playable Mag'har race.
2. Use a custom client field or custom race variant later to expose both.
3. Repurpose a less-important appearance field only if both server and client are deliberately modified to interpret it as posture.

Do not attempt to encode upright posture as a normal `CharHairGeosets` entry.

## Eye color, eyesight, and eye style

Retail now supports more independent eye customization than Wrath.

The current Mag'har graph includes:

```text
Eye Color
Eyesight
Eye Style
```

Some choices are class/requirement gated or shared with unrelated races. Nine clan-eye BLPs also currently fail CASC decoding through Converter.

For the first playable build, choose a stable default eye presentation or a small validated subset. Do not block the entire race on perfect modern eye parity.

## `BarberShopStyle.dbc`

Once character creation works, expose the subset of appearance choices that map safely into Wrath's barber system.

Wrath barber types include legacy categories such as hair style, hair color, facial hair, skin, and face.

Modern accessories such as tusks, jewelry, eyesight, and posture do not automatically gain barber support just because Retail exposes them in its modern barber UI.

## `ChrCustomizationConversion` as reference data

Retail's `ChrCustomizationConversion` table exists specifically to relate modern choices to older-style appearance dimensions in builds that still need compatibility behavior.

Before implementing the generator, inspect all rows relevant to RaceID 36 and use them as Blizzard's own hint for:

```text
Skin Color
Face
Hair Style
Hair Color
Features
Custom display slots
```

This table should guide the flattening logic, but the result still must target Esteria's build-12340 DBC layouts.

## ID management

Do not use arbitrary IDs scattered through code.

Create a future allocation manifest that records reserved ranges for:

```text
CreatureModelData IDs
CreatureDisplayInfo IDs
CharSections IDs
CharHairGeosets IDs
CharacterFacialHairStyles IDs
BarberShopStyle IDs
```

The generator should reject collisions with the loaded Esteria template DBCs.

## Recommended implementation order

1. Extract Esteria's current template DBCs.
2. Choose the Esteria Mag'har RaceID.
3. Generate male/female model and display rows pointing at `custom\maghar`.
4. Create the `ChrRaces` row and verify a minimally selectable race with default appearance.
5. Generate skin rows in `CharSections`.
6. Generate face rows.
7. Generate hair styles and hair colors.
8. Generate beard/sideburn mappings.
9. Add accessory combinations only after the base race is stable.
10. Decide posture behavior.
11. Decide eye behavior.
12. Add barber rows.
13. Package DBCs plus canonical patch root into the test MPQ.
14. Test character creation, login, equipment, helmets, animations, emotes, death, mounts, barber, and relog persistence.

## Success criteria for the first playable Mag'har

The first milestone does not need perfect Retail feature parity. It should meet these requirements:

- separate Esteria race entry
- correct male/female Mag'har skin colors
- correct basic faces
- correct basic hair styles/colors
- stable beard/facial appearance
- no base-Orc asset replacement
- normal armor and helmet rendering
- normal movement and combat animations
- appearance persists across relog
- no client crash in character creation or barber

Once that is stable, the more modern extras can be layered on deliberately.
