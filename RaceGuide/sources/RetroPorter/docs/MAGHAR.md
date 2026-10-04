# Mag'har Orc Retroport Status

## Current status

The initial Mag'har Orc Retail discovery and asset conversion are complete.

This is **not yet a playable 3.3.5a race**. The converted art exists and is structurally loadable by build 12340. The remaining major work is the character DBC and customization flattening phase.

## Verified Retail identity

Verified against Retail `12.1.0.69933` on 2026-09-28.

```text
Race name:          Mag'har Orc
ClientFileString:   MagharOrc
Retail RaceID:      36
Base fallback race: Orc, RaceID 2
```

Retail explicitly uses Orc fallback model and texture races for Mag'har. This confirms that Mag'har is primarily an Orc body plus Mag'har-specific materials, geosets, conditional model behavior, and customization data.

## Player models

### Male

```text
ChrModelID:         71
DisplayID:          84558
Model FileDataID:   917116
Model path:         character\orc\male\orcmale_hd.m2
Skeleton FDID:      4690417
```

### Female

```text
ChrModelID:         72
DisplayID:          84560
Model FileDataID:   949470
Model path:         character\orc\female\orcfemale_hd.m2
Skeleton FDID:      4690416
```

### Upright male

```text
Model FileDataID:   1968587
Model path:         character\orc\male\orcmaleupright.m2
```

The upright option is not represented as a normal old-style Wrath appearance field. Retail choice `3427` references a `ChrCustomizationCondModel` record. This needs special handling during 3.3.5a integration.

## Retail customization options found

Male model `71` currently exposes:

```text
347   Skin Color
350   Hair Style
351   Hair Color
352   Beard
353   Hunched
412   Face
880   Eye Color
882   Sideburns
883   Tusks
884   Earrings
885   Piercings
6378  Eyesight
8564  Eye Style
```

Female model `72` currently exposes:

```text
354   Skin Color
357   Hair Style
358   Hair Color
413   Face
414   Earrings
881   Eye Color
886   Nose Ring
887   Necklace
6379  Eyesight
8565  Eye Style
```

The current graph contains:

```text
23 customization options
201 customization choices
548 customization elements
74 referenced customization geoset records
376 referenced customization material records
```

## Notable choices

Male hair choices include:

```text
Bald
Majestic
Unbound
Veteran
Dreadnaught
Foehawk
Savage
Crude
```

Female hair includes:

```text
Savage
Boar Tails
Majestic
Unbridled
Strong
Gronn Breaker
Sleek
Dreadnaught
Bald
```

Male beard choices include:

```text
None
Full
Iron Band
Iron Spikes
Braid
Goatee
```

Male tusk choices include:

```text
Natural
Gold Root
Broken
Iron Band
```

There are also earrings, piercings, sideburns, nose rings, necklaces, multiple eye colors, eyesight choices, and newer eye-style choices.

## Retail requirement filtering

Modern Retail reuses customization choices through requirements. A naive walk of every choice attached to the Mag'har model can therefore pull unrelated shared art.

Current requirement records observed include:

```text
10   ReqType 4
12   ReqType 2
141  ReqType 3, ClassMask -1
142  ReqType 3, ClassMask 32
144  ReqType 3, ClassMask 30687
146  ReqType 3, ClassMask 32735
```

Some newer eye choices with requirement `12` resolve to shared Dracthyr or Human textures. The initial asset planner avoids obvious unrelated assets by limiting customization textures to `character\orc\`.

A future refinement should build a choice-level dependency graph and evaluate requirements before selecting assets. This will matter more for races such as Haranir and Mechagnome.

## Discovered Mag'har texture families

The Retail customization graph resolves large groups of Orc-clan textures such as:

```text
character\orc\orcclanhair00_*.blp
character\orc\female\orcfemaleclanfaceupper*_*.blp
character\orc\female\orcfemaleclannakedpelvisskin00_*.blp
character\orc\female\orcfemaleclannakedtorsoskin00_*.blp
character\orc\female\orcfemaleclanskin00_*.blp
character\orc\male\orcmaleclanfaceupper*_*.blp
character\orc\male\orcmaleclannakedpelvisskin00_*.blp
character\orc\male\orcmaleclannakedtorsoskin00_*.blp
character\orc\male\orcmaleclanskin00_*.blp
character\orc\claneyes*.blp
```

The exact FileDataID-to-path map is preserved in:

```text
G:\RetroPorterWork\maghar\reports\discovery.json
```

## Current conversion results

Canonical patch staging root:

```text
G:\RetroPorterWork\maghar\output\patch-root\
```

The race files live below:

```text
custom\maghar\character\orc\...
```

Current totals:

```text
276 selected Retail source files
439 written 3.3.5a-side files
0 failed conversions
```

Output extensions:

```text
3   .m2
3   .skin
160 .anim
273 .blp
```

Converter status totals:

```text
160 ok
6 lossy
273 passthrough
9 skipped
0 failed
```

The September 29 integration QA exposed nine BLPs referenced directly by the player M2 TXID data that were not part of the original customization-graph asset slice. RetroPorter now reads direct texture FileDataIDs from every core M2 and adds them to the asset plan. The regenerated Mag'har patch root contains all nine hard dependencies, including the male/female eye-reflection and model-specific textures. A converted player M2 is no longer considered complete unless every hard BLP reference resolves in the generated patch root.

## Model verification

`wotlkconv inspect` reports:

### Male HD

```text
version:          264
chunked:          False
vertices:         46799
bones:            220
sequences:        372
textures:         12
materials:        11
skin_profiles:    1
wotlk_compatible: True
```

### Female HD

```text
version:          264
chunked:          False
vertices:         44003
bones:            223
sequences:        361
textures:         13
materials:        12
skin_profiles:    1
wotlk_compatible: True
```

### Upright male

```text
version:          264
chunked:          False
vertices:         46781
bones:            220
sequences:        118
textures:         12
materials:        11
skin_profiles:    1
wotlk_compatible: True
```

## Expected lossy conversion areas

The six lossy results are:

```text
character/orc/female/orcfemale_hd.m2
orcfemale_hd00.skin
character/orc/male/orcmale_hd.m2
orcmale_hd00.skin
character/orc/male/orcmaleupright.m2
orcmaleupright00.skin
```

Important conversion notes include:

- external skeletons merged into Wrath-compatible M2s
- modern split animation payloads flattened into Wrath ANIM files
- unused geometry compacted below the 65,535 vertex ceiling
- post-Wrath flags cleared
- modern LOD data dropped
- modern shadow batches dropped
- a small number of newer shader and blend behaviors mapped to Wrath-compatible behavior
- modern replaceable texture types that Wrath does not understand cannot be represented 1:1

These are expected technical losses. Visual QA in the actual 3.3.5a client is still mandatory.

## Known skipped eye textures

Nine eye textures currently fail before BLP conversion because the CASC reader receives bytes that are not a valid BLTE stream:

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

Retrying one with Converter's `--casc-cdn` produced the same result, so this does not appear to be a simple locally-missing streamed file.

Do not block the whole race on these nine textures. Continue with the main skin/face/hair work and revisit eye appearance during client QA.

## Unsupported `.bone` overrides

The discovery currently identifies 27 Retail `.bone` assets tied into modern customization. 3.3.5a has no direct equivalent and Converter intentionally does not carry them over.

Do not assume this means 27 visible customizations are lost. First determine which choices actually rely on those overrides after requirement filtering. If a required look depends on one, it will need to be baked into a model, converted into a geoset/model variant, or approximated in Wrath.

## Current encrypted-table limitation

`CreatureDisplayInfo.db2` in this Retail build uses encryption key:

```text
583C5B29BF208655
```

That key is not in the current public TACT keyring. All other tables needed for the current pass were readable.

This does not block the initial Mag'har conversion because Retail itself identifies Mag'har as an Orc-fallback race, and the relevant Orc player model FileDataIDs are resolved directly through the customization/model data and listfile.

If the key becomes public later, rerun:

```powershell
python -m retroporter extract-db2 --race maghar
python -m retroporter discover --race maghar
```

Then compare the display chain with the current manifest.

## Build-12340 geometry QA finding

The directly converted Retail Orc player M2s are structurally readable by 3.3.5a, but September 30 Character Creation QA showed that they are not yet a safe production player-geometry target. Retail carries many modern submesh/geoset groups that build 12340 does not select as part of the legacy character geoset state. The result is a model that loads and animates, but with most of the male and female body/head geometry invisible.

This matches Retail's own Mag'har race data: Mag'har uses the Orc fallback model and differentiates the race primarily through Mag'har-specific materials and customization geosets. For the first playable 3.3.5a integration, use the known-good Wrath-HD Orc/Orc2 player geometry and apply the retroported Retail Mag'har skin, face, hair, underwear, and related material assets through the legacy customization DBCs. Keep the converted Retail M2s as an experimental source for future explicit geoset flattening/remapping rather than making them the active player model by default.

## Next milestone

The next milestone is not "convert more art." It is:

**Create an Esteria Mag'har race definition and flatten the useful Retail Mag'har appearance choices into build-12340 DBCs that use a validated Wrath-HD Orc geometry contract while referencing `custom\maghar\...` appearance art.**

See `DBC_STRATEGY.md` for that work.
