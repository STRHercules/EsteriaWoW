PROJECT REFORGED CUSTOM STARTING ZONE EXTRACTION
Generated: 2026-10-04T07:00:15.193Z

SOURCE
G:\Downloads\HDWoWModels\Project Reforged\Data

OUTPUT
G:\Downloads\HDWoWModels\Project Reforged\Custom_Starting_Zones_Isolated_2026-10-04

CONFIRMED / HIGH-CONFIDENCE PACKAGES

Tuskarr_Iskirr_Village
  Internal map: custom_tuskarr
  Race/category: Tuskarr
  Status: confirmed custom race zone
  Area: 11435 - Iskirr Village
  Map files: 14
  Direct ADT dependencies: 69
  Unique extracted paths: 430
  Extracted copies: 446
  Size: 51.63 MiB
  Doodad placements: 457
  WMO placements: 38
  Minimap tiles: 12
  Unresolved candidates: 0

Troll_Custom_Start
  Internal map: custom_troll
  Race/category: Troll
  Status: strong starting-zone candidate
  Area: 50506 - custom runtime area 50506
  Map files: 21
  Direct ADT dependencies: 215
  Unique extracted paths: 698
  Extracted copies: 747
  Size: 60.01 MiB
  Doodad placements: 15330
  WMO placements: 15
  Minimap tiles: 0
  Unresolved candidates: 3

Worgen_Gilneas
  Internal map: Giln
  Race/category: Worgen
  Status: confirmed custom Gilneas race zone
  Area: 5179 - Gilneas
  Map files: 17
  Direct ADT dependencies: 349
  Unique extracted paths: 1710
  Extracted copies: 1819
  Size: 69.50 MiB
  Doodad placements: 4936
  WMO placements: 307
  Minimap tiles: 16
  Unresolved candidates: 0

Shared_Obelisk_of_the_Stars
  Internal map: obeliskofthestarts
  Race/category: Shared
  Status: shared starter/tutorial hub candidate
  Area: 8463 - Obelisk of the Stars
  Map files: 20
  Direct ADT dependencies: 562
  Unique extracted paths: 2076
  Extracted copies: 2163
  Size: 164.93 MiB
  Doodad placements: 11923
  WMO placements: 155
  Minimap tiles: 18
  Unresolved candidates: 0

GOBLIN FINDING
Goblin is playable as race ID 9 in the final Project Reforged ChrRaces.dbc. No World\Maps directory containing Goblin, Kezan, Lost Isles, or Bilgewater exists anywhere in the Project Reforged MPQ stack. No dedicated Goblin terrain map was identified. Client-side evidence is therefore consistent with Goblin using an existing starting map such as the Orc Valley of Trials start. Exact spawn coordinates are server-side and cannot be proven from the client MPQs alone.

OBELISK OF THE STARS
Area ID 8463 on Map ID 1402. The map mixes Human, Orc, Tauren, Goblin, Tuskarr and other starter-flavored assets. It has Kezan/Lost Isles Goblin props, but is not Goblin-specific. It is isolated as a shared starter/tutorial hub candidate.

EXCLUDED FROM START-ZONE SET
Naga Ascent: Area ID 10099, Map ID 960. Direct ADT scan found it only in World\Maps\MiniGames\minigames_39_22.adt, occupying 49 MCNK chunks. This is a minigame area, not a standalone Naga start map.
Vrykul: custom_vrykul1 and custom_vrykul2 are strongly Vrykul-themed, but Vrykul race ID 38 has the NOT_PLAYABLE flag in the final client. They were not classified as active starting zones. custom_vrykul1 contains Isle of the Forgotten God, Area ID 11428.
The Grim Marsh: custom_marsh, Area ID 11429 / Map ID 1771. Strong Blood Troll/Zandalari environment, but no evidence tying it to a playable race start.
Eonar's Cradle: custom_tropical, Area ID 11439 / Map ID 1774. Tropical environment with no strong playable-race ownership.
cu_LD_draenei: custom Draenei-themed level-design map, but it belongs to a broader cu_LD_* family and could not be established as a player start.

TROLL NOTE
custom_troll is an extremely strong Troll-start candidate: 20 ADTs, 15,330 doodad placements, 215 direct dependencies and heavy Zul'Aman/Zul'Drak/Zul'Gurub/Troll asset use. Unlike Tuskarr/Gilneas/Obelisk, no minimap section was found in md5translate.trs. Three AdaalosIsland paths referenced by its ADTs do not exist in Project Reforged or the public Blizzard listfiles and appear to be stale/missing references.

FILES
manifest.csv - every extracted copy with source archive, internal path, size and SHA1
failures.csv - extraction/index/parser failures
summary.json - machine-readable zone inventory
Shared_Client_Metadata - relevant client DBC copies used for map/area identification
