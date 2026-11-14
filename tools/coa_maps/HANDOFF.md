# CoA custom maps -> Esteria (Live)

Decisions (user, 2026-11-12/13): port all CoA custom maps (the 192 "ours" teleports, 61 maps) with everything;
work in Live only; keep CoA ids where Esteria has them free, remap collisions, never replace an Esteria row or file;
CoA's map-0 zones (Druk'Thar, Pale Reach, Shadewell) become standalone **map 1820 `DrukThar`**; ~10 GB of new client
archives is acceptable.

Sources: CoA client `G:\CoAClient\Client`, CoA core `R:\Users\Zach\Documents\GitHub\azerothcore-wotlk-coa`, CoA live
world dump `G:\Downloads\HDWoWModels\acore_world_2026-11-13.sql.gz` loaded as schema `coa_live_world` (the git
package and `coa_b7_world` / `ms_coa_world` have no spawns on these maps).

## Phase 1: terrain, DBCs, teleports (tool: `coa_stage.py`)

`python -I coa_stage.py` reads the CoA client + Dev client (baseline) + Live server DBCs and writes
`G:\CoAMapsPort\stage`:
- `client/`: `Patch-ZZZ..(27 Z)CoAMapsDbc.MPQ` (merged DBCs, built on the current winners) and
  `Patch-ZzzzzzzzzzCoAMaps-001..007.MPQ` (15.8k files new to Esteria). Installed 2026-11-13 into both
  `G:\3.3.5a - Dev\Data` and `G:\3.3.5a - Live\Data` (new files only).
- `server/dbc/` (Map, AreaTable, AreaTrigger, WorldSafeLocs, LiquidType), `server/sql/coa_maps_world.sql`
  (199 game_tele at 2300+, graveyards, areatrigger_teleport).
- `extract/patch-4..7.MPQ`: full file set for the server extractors (terrain in 4/5, models 6+; MPQ v1 stops at 4 GB),
  with a Map.dbc of only these 62 maps.
- `reports/`: `idmap.json` (CoA -> Esteria ids), `kept-existing-CoA.txt` (27k CoA files that differ from Esteria's;
  Esteria's kept), `unresolved.txt` (702 models in neither client: invisible), `stage-report.txt`.

Gotchas: CoA's Map.dbc stores "Azeroth" at string offset 0 (reads as empty); CoA has 0-byte M2s; CoA streams many
retail-era models from outside its MPQs, so the closure falls back to Esteria's client; the tool streams files (holding
them all ran the PC out of memory).

Server extraction: `G:\CoAMapsPort\extract.sh` in a throwaway `housing-build:base` container (binaries copied from
housing-build to `G:\CoAMapsPort\bin`), input `G:\CoAMapsPort\extract-in\Data` = hard links to CoA base MPQs +
`stage/extract/patch-4..7`, output `G:\CoAMapsPort\extract-out\{maps,vmaps,mmaps}`.

mmaps_generator crashed on every map once any 4-digit map id (1171, 1758+, 1820) sat in the data dir: two fixed char
buffers in `src/tools/mmaps_generator/MapBuilder.cpp` (`filter[12]`, `tileString[20]`) overflow. Fixed in EsteriaWoW
and rebuilt in housing-build (`ninja mmaps_generator`, copied to `G:\CoAMapsPort\bin`). Pathing ran per map in a
throwaway container (`G:\CoAMapsPort\mmaps-run.log`).

Install on Live (server): back up acore_world + the five DBCs; copy DBCs into the ac-worldserver data volume
(AreaTable is bind-mounted from `modules/mod-fly-anywhere/data/patch/server/AreaTable.dbc`); copy maps/vmaps/mmaps
files; apply `coa_maps_world.sql`; restart ac-worldserver.

### In-game fixes after the first test (2026-11-13)

- **Green terrain**: Esteria's client draws a terrain layer solid green when its texture has no `_s.blp` specular
  companion. The stage only followed base names. `Patch-ZzzzzzzzzzCoAMaps-008.MPQ` = 74 companions copied from CoA
  (`G:\CoAMapsPort\companions.py`); `-009.MPQ` = 14 generated ones (base colour, zero specular) for textures with no
  `_s` anywhere (`G:\CoAMapsPort\make_spec.py`). `coa_stage.py` now walks `_s`/`_h` itself; a re-stage still needs
  make_spec for the rest. Darkcove confirmed fixed. Still broken: textures whose base exists in neither client
  (`10cav_sulfur01_512`, `11UDM_PEBBLES01_512`; CoA streams them) and bogus MTEX names in CoA's ADTs.
- **Crash on map 907 (FadingIsland, anywhere on the map)**: its lights used LightSkybox 14909
  (`environments\stars\8dru_westerndrustsky01.m2`), a model in neither client. LightParams 10024/10025 now have no
  skybox (`G:\CoAMapsPort\fixsky.py` rewrote the DBC archive); `coa_stage.py` drops such skyboxes. Not yet confirmed.
- **Crashes on maps 800/900/909 (and suspected 907)**: symbolized with the linker map (`G:\CoAMapsPort\symbolize.py`):
  `CMapObjGroup::CreateOptionalDataPointers` -> SMemAlloc fatal. Esteria's `common-3.MPQ` copies of 7 Zuldazar WMOs
  (8SWA_PYRAMID, _TREEWMO_B01, _UNDERROTCAVE01, _DEATHLOATEMPLE01/_CRYPT01, ...) still carry retail chunks
  (MOBS/MOLP/MDAL) the 3.3.5 parser walks into. `Patch-ZzzzzzzzzzCoAMaps-010.MPQ` overrides them with CoA's valid
  copies (`G:\CoAMapsPort\wmofix.py`; validator `wmocheck.py`). This replaces Esteria files on purpose: Esteria's
  copies crash any map that loads them. 47 WMOs with empty groups are byte-identical to CoA's and left alone.
  The stage's kept-existing rule should run wmocheck on WMO groups and prefer CoA's copy when Esteria's misparses.
- **More crashes on 907**, each named by `Errors\*.txt` or the symbolized crash log:
  - Vulkan `ITexUpload`/`CopyRows` read past a BLP's end: Esteria textures (mostly `patch-D.mpq`) whose last mips are
    declared with size 0. `Patch-ZzzzzzzzzzCoAMaps-011.MPQ` = 232 completed BLPs (`blpcheck.py` per map ->
    `blpcheck-all.txt` -> `blpfix.py`; missing mips repeat the previous level's block), 2 Zuldazar jungle-tree BLPs that
    weren't BLPs at all (CoA's copies), and VEB_WATERLILY04.m2 (Esteria's is M2 v256 with a broken texture table).
  - `CMap::SafeOpen() failed ..._005.wmo`: Esteria roots in raw retail format (MODI/GFID, no MOTX/MODN). `check_root`
    in `wmocheck.py`; `Patch-ZzzzzzzzzzCoAMaps-012.MPQ` = 10 such WMOs from CoA. Build new override archives with a
    new number: the scripts read the Dev client, so WMOs/BLPs already fixed by an installed archive drop out.
- Characters stuck on a crashing map: move them in `acore_characters.characters` while offline (done for Zach, Foxbow).

## Phase 2: content (not started)

From `coa_live_world`: 3,436 creatures + 65 gameobjects on the custom maps, ~1,646 creatures in the map-0 zones (move
to 1820 when their chunk area is a Druk'Thar/Pale Reach/Shadewell area). 2,671 creature templates (2,612 ids free in
Esteria, 59 identical, 0 clashing), 265 SmartAI, 128 quests, 18 vendors. Display ids need look-matching (Ascension
renumbered stock displays, see wowdecomp Tools/ManastormPort). C++ (~7k lines): `mod-coa-raid-difficulty`
boss_world_coa.cpp / boss_world_custom_coa.cpp (+ CoaBossAI.cpp), `src/server/coa/CoAVaults.cpp`,
`CoAOtherSide*.cpp`, `AscensionAreaQuestOffers.cpp`; `npc_coa_other_side_venom_trap`, `go_setis_leave_coa`,
`go_snowgrave_leave_coa` have no source in the CoA repo.
