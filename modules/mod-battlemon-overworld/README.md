# Battlemon overworld

AzerothCore module that sits **next to** `mod-battlemon`. It does not change that repo.

Right-click a world Battlemon to start a wild through `BattlemonMgr::HandleAddon`. Display id encodes the form (`50000 + formId`, shiny `70000 + formId`). That fight uses the sprite you clicked and does not start the addon Fight cooldown.

## What you do

1. Symlink or copy this folder into `azerothcore/modules/mod-battlemon-overworld` (alongside `mod-battlemon`).
2. World SQL lives at `data/sql/world/base/2026_08_21_00_battlemon_overworld.sql`. Worldserver applies it on start.
3. Import the patched CSVs into DBCs yourself (WDBX or whatever you use). **Do not pack MPQs.** Drop the two `.dbc` files as loose files:

   `Data\patch-z.mpq\DBFilesClient\CreatureDisplayInfo.dbc`  
   `Data\patch-z.mpq\DBFilesClient\CreatureModelData.dbc`

   `patch-z.mpq` is already a folder on this Chromie client.
4. Cardboard plane (WotLK M2 v264, texture type 11) plus every Front / Front shiny BLP:

   `python tools/build_plane.py`

   That writes loose files into `patch-z.mpq` (no packing) and a copy under `client/Creature/Battlemon/`. Fully quit Wow.exe after replacing M2/BLP.

5. Restart worldserver and the client. `.bmo spawn` (default Pikachu, form 37). `.bmo spawn 37 1` is shiny. `.bmo spawn <formId>` for any catalog form.

Outdoor critters morph on by default (`BattlemonOverworld.MorphCritters = 1`). Rolls use `BattlemonMgr::PickWildForm()` (same weights as the addon Fight button). Shinies are 1-in-N from `Battlemon.ShinyEvery`.

## CSV patch

Already applied to the Chromie export under `patch-z.mpq\DBFilesClient\CSV`. To rebuild after a fresh DBC export:

```
python tools/patch_dbc_csv.py
```

Reserved IDs: model `2252000`; displays `50001–51581` and `70001–71581`. Broken retains display IDs `60002/60003`.
