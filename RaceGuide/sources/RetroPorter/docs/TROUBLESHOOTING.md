# Troubleshooting

## `wotlkconv` says the Retail install is invalid

Use:

```text
G:\Blizzard\World of Warcraft
```

Do not use `_retail_` as the CASC root. Converter needs `.build.info` and `Data` from the parent directory.

## `CreatureDisplayInfo.db2` will not extract

Current Retail build `12.1.0.69933` encrypts that table with key:

```text
583C5B29BF208655
```

The key is not present in the current public TACT keyring. This is a known limitation of the current Mag'har discovery pass.

The rest of the Mag'har graph is still usable. If a future TACT key update provides the key, refetch keys and rerun extraction/discovery.

## Some eye BLPs say `not a BLTE stream`

Nine current Orc eye textures fail this way. A retry with `--casc-cdn` gives the same result.

Treat them as a known source/CASC-reader issue for now. They are listed in `docs/MAGHAR.md` and the conversion report.

## Why are there `.bone` files in discovery but not output?

Modern Retail uses `.bone` overrides in customization. 3.3.5a does not have the same mechanism and Converter intentionally does not convert them.

RetroPorter records them as unsupported. If a required appearance depends on one, the visual change will need to be baked into an M2/geoset variant or approximated another way.

## Why is the conversion report `lossy` for the player models?

Modern M2/SKIN features do not all exist in Wrath. Expected losses include newer shaders, shadow batches, LOD data, blend behavior, and replaceable texture types.

`lossy` does not mean the file is invalid. The converted Mag'har bodies currently inspect as `wotlk_compatible: True`.

## Which output tree should be packaged?

Use only:

```text
G:\RetroPorterWork\maghar\output\patch-root\
```

Do not package:

```text
G:\RetroPorterWork\maghar\output\assets\
```

The latter is an exploratory conversion made before physical path namespacing was corrected.

## Why do the output paths start with `custom\maghar`?

This prevents the new race from overwriting the base Orc assets.

Converter's `--path-prefix` rewrites references inside converted assets. RetroPorter also places the converted files physically beneath the matching namespace so those references resolve when packed into an MPQ.

## The `retroporter` command is not found

Use the module form:

```powershell
python -m retroporter doctor
```

The current Python user Scripts directory is not on PATH.

## Retail updated and the old discovery may be stale

Rerun:

```powershell
python -m retroporter extract-db2 --race maghar
python -m retroporter discover --race maghar
python -m retroporter plan-assets --race maghar
python -m retroporter convert-assets --race maghar --dry-run
```

Compare the new discovery/asset reports with `manifests/maghar.toml`. If core model IDs or customization structure changed, update the manifest and code deliberately before doing a real conversion.

## A future race returns no match

Only Mag'har's `ClientFileString` has been verified live in the current build. Entries for Highmountain, Mechagnome, Earthen, and Haranir are scaffolding for future work.

Inspect `ChrRaces` in the current Retail build and update `src/retroporter/races.py` if Blizzard's current `ClientFileString` differs.
