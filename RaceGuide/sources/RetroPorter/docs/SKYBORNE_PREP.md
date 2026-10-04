# Skyborne Retroport Preparation

## Status: superseded

This preparation document is retained only as historical context.

Skyborne discovery and conversion were completed on 2026-09-28 from the installed **World of Warcraft: Forever beta** client:

```text
CASC root: D:\Blizzard\World of Warcraft
Product: wow_classic_beta
Version: 1.60.1.70009
Build: WOW-70009patch1.60.1_ForeverBeta
```

The live source verified:

```text
RaceID 95: High Order Skyborne
RaceID 96: Windshaper Skyborne
ClientFileString: Skyborne
Male ChrModelID: 218
Female ChrModelID: 219
```

The race is now `ready_for_assets = True` and its full safe asset conversion completed with zero skipped and zero failed files.

Use these instead of this preparation document:

```text
docs/SKYBORNE.md
manifests/skyborne.toml
```

Current commands:

```powershell
python -m retroporter extract-db2 --race skyborne --source-root "D:\Blizzard\World of Warcraft" --source-product wow_classic_beta
python -m retroporter discover --race skyborne
python -m retroporter plan-assets --race skyborne
python -m retroporter convert-assets --race skyborne --dry-run --source-root "D:\Blizzard\World of Warcraft" --source-product wow_classic_beta
python -m retroporter convert-assets --race skyborne --source-root "D:\Blizzard\World of Warcraft" --source-product wow_classic_beta
```

Retail `skyborne` housing, armor, and mount filenames remain unrelated false positives. The verified player-race evidence comes from the Forever beta DB2s and CASC source above.
