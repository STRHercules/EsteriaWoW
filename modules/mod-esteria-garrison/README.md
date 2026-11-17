# mod-esteria-garrison

UWoW's Draenor garrison on Esteria: Alliance tiers 1158/1331/1159 (Lunarfall), Horde 1152/1330/1153 (Frostwall).
Every character gets a garrison at login (no teleport); players open it from the Housing UI's Neighborhood window
(**Garrison** button) or `/garr`. Ported from the risServer handoff (`wowdecomp/GarrisonHandoff`, 2026-11-16).

Nothing here may overwrite Esteria data: the tools below check every row against Live before writing.

## Pieces

| Where | What |
|---|---|
| `src/` | Garrison, GarrisonMgr, DB2 loader, packets, scripts, `.garrison` command (create/enter/leave/status for players; GM: `resources <±n>`, `upgrade`, `downgrade` (drops plots the lower tier lacks), `reset` (wipe to a fresh tier 1 with 0 resources), `delete`, `blueprint`, `place`, `follower`, `mission`, `spell`) |
| EsteriaWoW `src/server/game/Handlers/EsteriaGarrison*` | Null-by-default hooks (packet handler, owner instance picker) |
| EsteriaWoW core | Opcodes 0x54A HELLO / 0x54B STATE / 0x54C ACTION, `WorldSession::HandleEsteriaGarrisonOpcode`, MapInstanced owner-instance branch after housing's |
| `conf/esteria_garrison.conf.dist` | `EsteriaGarrison.Enable` (default 0) |
| wowdecomp `Extensions/Garrison` | Client side of the three opcodes, `garrisonEnabled` CVar (default 1), Lua `EsteriaGarrison_*` |
| wowdecomp `Addons/EsteriaGarrison` | Landing page, architect, missions; art as `retail/<FDID>.blp` and `Interface\AddOns\Blizzard_GarrisonUI\Art` |
| `Interface\AddOns\Blizzard_GarrisonUI` (client only, 66 MB, from the handoff) | Pre-converted window art. Keep `Blizzard_GarrisonUI.toc.bak`; renaming it loads the old architect window |

## Building the data

All tools run on the host with the `ac-database` container and the Dev client.

1. **World SQL** — `python tools/build_world_sql.py` → `sql/world/garrison_world.sql`.
   Loads `sql/source/*` (the UWoW port) into an empty clone of `acore_world`, moves the 17 creature and 13 gameobject
   templates whose entries Esteria already uses (Black Rat, Winter Revelers, Winter Veil objects, ...) to 9603000+ /
   9604000+ with every reference, and fails if any row still shares a primary key with `acore_world`. Ledger:
   `garrison_entry_remap`. `garrison_uwow_templates.sql` is not used: it is an older placeholder import of the same
   objects that, in the handoff's order, replaced the real templates with fake displays.
2. **Client DBCs** — `python tools/build_client_dbc.py --client "G:/3.3.5a - Dev"` (needs a database holding
   garrison_world.sql, default `garrison_verify`) → `Data/Patch-ZZZZZZZZZZZZZZZZZZZZZZZZZZZZGarrison.MPQ` (28 Zs: sorts above
   CoAMapsDbc) and `sql/world/garrison_dbc_world.sql` (the same new rows for the server's `*_dbc` tables).
   Each DBC is the client's current winner plus only the rows garrison content references; existing rows are checked
   unchanged. Run it per client folder (Dev and Live load different winners).
3. **Retail assets** — `python tools/retail_assets.py collect G:/garrison-build/retail-originals --seeds
   data/client_dbc_seeds.txt data/ui_seeds.txt`, then `pack ... patch-RetailGarrison-001.MPQ`.
   Reads the installed retail client (`T:\World of Warcraft`, local CASC) first and the CDN second, following the six
   WDTs (ADTs, textures, WMOs, doodads, minimaps, WDL) and every model/texture the DBC rows and addon name.
   2026-11-16: 12,075 files, 2.0 GB, none missing. Needs RetailAssetProbe with `--extract-batch` (wowdecomp
   `Tools/RetailAssets/probe.cpp`).
3b. **Body textures** — `python tools/garrison_skins.py --client "G:/3.3.5a - Dev"`: type-1 bake textures and
   geosets for retail humanoid displays (otherwise they draw white), written as a marked block in the client's
   `Data/HotS/MountSkins.csv`; other rows in that file are kept. Feed its texture IDs to `collect --seeds` too.
3c. **Zones and world map** — `python tools/build_world_map.py --client ...` after step 2 (it rewrites the same
   archive): AreaTable rows for the terrain's area IDs (zone text), one orphan WorldMapArea per tier map, and the
   retail UiMapArt tiles as `Interface\WorldMap\Garrison<Lunarfall|Frostwall><tier>\...`. Writes
   `sql/world/garrison_worldmap_world.sql`.
3d. **UI mipmaps** — `python tools/ui_mips.py retail` (before `pack`, which prefers `G:/garrison-build/retail-mipped`)
   and `python tools/ui_mips.py addon <handoff Blizzard_GarrisonUI\Art> G:/garrison-build/Blizzard_GarrisonUI/Art`
   (install that Art folder). Retail UI textures ship with one mip level and alias into jagged edges when drawn small.
4. **WDT aliases** — the client's active registry `aliases.csv` (see `Data/Retail/RetailCasc.ini aliases=`) needs:
   `876612;World\Maps\1152\1152.wdt`, `876623;...1153`, `879512;...1158`, `879360;...1159`, `1001652;...1330`, `1001653;...1331`.

## Applying

- acore_characters: `sql/characters/garrison_characters.sql` (create-if-missing only; safe to re-run).
- acore_world: `sql/world/garrison_world.sql`, `sql/world/garrison_dbc_world.sql`, `sql/world/garrison_worldmap_world.sql` (all safe to re-run).
- `etc/modules/esteria_garrison.conf` with `EsteriaGarrison.Enable = 1`.
- Client: Wow.exe with `Extensions/Garrison`, the DBC patch, `patch-RetailGarrison-001.MPQ`, the aliases, both addons.

## Not done

- Server terrain (maps/vmaps/mmaps) for the six maps: spawns use fixed Z; pathing and LoS need them.
- ID ranges to keep clear: creatures 9601100–9601999, 9603000+; gameobjects 9510016–9510337, 9525024–9525085,
  9602000–9602999, 9604000+; spawn guids 5100000+; waypoints 51000000+; displays 66524–68610, 7xxxxx.
