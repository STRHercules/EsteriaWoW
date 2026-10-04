# RetroPorter Pipeline

## Goal

RetroPorter is a repeatable pipeline for taking modern Retail player-race assets and preparing them for Esteria's WoW 3.3.5a client.

The pipeline separates three jobs that should not be mixed together:

1. **Retail discovery** - determine which Retail race, model, customization, material, geoset, and FileDataID records are actually used.
2. **Asset conversion** - use `wotlkconv` to downgrade M2, SKIN, ANIM, SKEL, and BLP assets into formats build 12340 can load.
3. **Wrath integration** - flatten Retail customization data into 3.3.5a DBC records and point Esteria's race definition at the converted assets.

The Mag'har pass has completed jobs 1 and 2 for the initial safe asset slice. Job 3 is the next major phase.

## Local layout

The repository contains code, manifests, and documentation only:

```text
R:\Users\Zach\Documents\GitHub\RetroPorter\
```

Blizzard data and generated binaries stay outside Git:

```text
G:\RetroPorterWork\
└── maghar\
    ├── retail-db2\
    ├── reports\
    └── output\
        └── patch-root\
            └── custom\
                └── maghar\
```

The current inputs are:

```text
Retail CASC root: G:\Blizzard\World of Warcraft
Retail product:   wow
Wrath dev client: G:\3.3.5a - Dev
```

Verified Retail build at the time of this pass:

```text
12.1.0.69933
WOW-69933patch12.1.0_Retail
```

## Why the CASC root is not `_retail_`

`wotlkconv` expects the directory containing `.build.info` and `Data`. On this machine those are here:

```text
G:\Blizzard\World of Warcraft\.build.info
G:\Blizzard\World of Warcraft\Data\
```

The executable is one level lower in `_retail_`, but `_retail_` is not the CASC root accepted by the converter.

## Prerequisites

Install Converter:

```powershell
python -m pip install --user "git+https://github.com/Bar3b0n3s/Converter.git"
```

Install this repository in editable mode:

```powershell
python -m pip install -e "R:\Users\Zach\Documents\GitHub\RetroPorter"
```

Fetch support data used by Converter:

```powershell
python -c "from wotlkconv.fetch import fetch_listfile, fetch_definitions, fetch_keys; print(fetch_listfile()); print(fetch_definitions()); print(fetch_keys())"
```

Expected cache locations on this machine:

```text
C:\Users\Zach\.cache\wotlkconv\community-listfile.csv
C:\Users\Zach\.cache\wotlkconv\definitions\
C:\Users\Zach\.cache\wotlkconv\WoW.txt
```

Run the environment check:

```powershell
python -m retroporter doctor
```

## Race discovery

Each race starts with DB2 extraction:

```powershell
python -m retroporter extract-db2 --race maghar
```

This pulls the current Retail tables needed to walk the customization graph. They include:

```text
ChrRaces
ChrModel
ChrRaceXChrModel
ChrCustomizationOption
ChrCustomizationChoice
ChrCustomizationReq
ChrCustomizationReqChoice
ChrCustomizationVisReq
ChrCustomizationElement
ChrCustomizationGeoset
ChrCustomizationMaterial
ChrCustomizationSkinnedModel
ChrCustomizationDisplayInfo
ChrCustomizationBoneSet
ChrCustomizationCondModel
ChrCustItemGeoModify
ChrCustGeoComponentLink
ChrCustomizationConversion
ChrModelMaterial
ChrModelTextureLayer
ModelFileData
TextureFileData
CreatureDisplayInfo
CreatureModelData
```

Then run discovery:

```powershell
python -m retroporter discover --race maghar
```

The discovery walk is:

```text
ChrRaces
  -> ChrRaceXChrModel
      -> ChrModel
          -> ChrCustomizationOption
              -> ChrCustomizationChoice
                  -> ChrCustomizationElement
                      -> ChrCustomizationGeoset
                      -> ChrCustomizationMaterial
                      -> ChrCustomizationSkinnedModel
                      -> ChrCustomizationBoneSet
                      -> ChrCustomizationCondModel
                      -> ChrCustomizationDisplayInfo
```

Material resources are additionally resolved through `TextureFileData`. Every discovered FileDataID is resolved through the community listfile where possible.

The machine-readable result is:

```text
G:\RetroPorterWork\maghar\reports\discovery.json
```

## Asset planning

Generate an explicit asset plan before conversion:

```powershell
python -m retroporter plan-assets --race maghar
```

The current Mag'har planner intentionally selects a conservative first slice:

- the Retail HD male Orc body
- the Retail HD female Orc body
- the Retail upright male Orc body
- Mag'har/Orc customization BLPs under `character\orc\`

Retail `.bone` overrides are recorded as unsupported instead of silently copied.

The plan is written to:

```text
G:\RetroPorterWork\maghar\reports\asset-plan.json
```

## Conversion

Dry run first:

```powershell
python -m retroporter convert-assets --race maghar --dry-run
```

Real conversion:

```powershell
python -m retroporter convert-assets --race maghar
```

The canonical patch staging root is:

```text
G:\RetroPorterWork\maghar\output\patch-root\
```

The race is namespaced below:

```text
custom\maghar\character\orc\...
```

This matters because Converter's `--path-prefix custom\maghar` rewrites references inside converted assets, but it does not relocate each top-level output by itself. RetroPorter deliberately sets Converter's output directory beneath the same physical prefix so the MPQ path and internal references agree.

Do not package the older exploratory tree at:

```text
G:\RetroPorterWork\maghar\output\assets\
```

That tree predates the physical namespace fix.

## Conversion verification

For Mag'har the canonical conversion currently produces:

```text
430 written files
  3 M2
  3 SKIN
160 ANIM
264 BLP
```

Converter report totals:

```text
160 ok
  6 lossy
264 passthrough
  9 skipped
  0 failed
```

The six lossy results are the three player M2s and their three SKIN files. The losses are expected modern-to-Wrath reductions such as modern shader behavior, shadow batches, LOD data, newer replaceable texture slots, and newer blend behavior.

The converted body models verify as Wrath-compatible M2 version 264:

```text
orcmale_hd.m2       46,799 vertices, 220 bones, 372 sequences
orcfemale_hd.m2     44,003 vertices, 223 bones, 361 sequences
orcmaleupright.m2   46,781 vertices, 220 bones, 118 sequences
```

All three are below the 65,535 vertex index ceiling after Converter compacts unused geometry.

## Packaging rule

The patch staging root is designed to be copied into an MPQ as-is later:

```text
patch-root\
└── custom\
    └── maghar\
        └── character\
            └── orc\
                ├── male\
                └── female\
```

Do not build the final MPQ until the DBC phase points the new race at this namespace. Otherwise the converted files exist but no 3.3.5a race will reference them.

## Adding another race

The intended future workflow is:

```powershell
python -m retroporter extract-db2 --race <slug>
python -m retroporter discover --race <slug>
python -m retroporter plan-assets --race <slug>
python -m retroporter convert-assets --race <slug> --dry-run
python -m retroporter convert-assets --race <slug>
```

Before relying on a future race entry in `races.py`, verify its live Retail `ClientFileString`. Only Mag'har has been verified against the current 12.1.0 build so far.
