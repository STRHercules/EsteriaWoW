THE RISEN DEPTHS / SIRUS2 EXTRACTION
===================================

Output root:
D:/Sirus/_client/World of Warcraft Sirus/Risen_Depths_Extract_2026-10-04

IDENTITY
--------
AreaTable ID: 10050
Map ID: 10001
Terrain/internal map directory: Sirus2
WorldMapArea UI directory: RisingDepths
WorldMapArea ID: 899
World-map parent area: 966
Terrain footprint: X 28-36, Y 28-36 (81 active ADT tiles)

FINAL INVENTORY
---------------
Physical files in extraction root: 2807
Physical bytes: 556164269 (530.40 MiB)
Manifested extracted copies: 2772
Distinct internal MPQ paths identified across manifests: 2427

Terrain/map files: 186 copies / 83 unique paths
ADT direct dependency paths: 386
Recursive visual dependency closure: 1739 unique paths (1947 patch copies)
World-map art: 54 BLPs
Zone extras: 105 files
Liquid renderer assets present: 34 files
Relevant DBC copies: 52

DIRECT TERRAIN CONTENT
----------------------
Doodad model paths: 320
WMO root paths: 41
Terrain texture paths: 25
Doodad placements across extracted ADT patch versions: 26902
WMO placements across extracted ADT patch versions: 502

CLIENT UI / MAP ART
-------------------
Recovered all 12 RisingDepths base world-map BLP tiles plus RisingDepthsHighlight and custom fog-of-war overlay pieces.
Recovered all 81 minimap tiles through the Sirus2 md5translate.trs mapping.
Recovered custom loading screen: Interface\Glues\LoadingScreens\loadingscreen_naga_start.blp

AUDIO
-----
Recovered all 21 Vashj'ir-family MP3 files actually present in the Sirus locale patch.
AreaTable links the zone/subzones to ZoneMusic IDs 703, 705, 706, 707, 708 and intro ID 637.
Resolved sets include Abyssal Depths, Vashjir Naga, Vashjir Cave, Shimmering Expanse, and Nightmare Depths intro music.
SoundAmbience ID 567 references coastal day/night ambience names, but those exact WAV files are not present by filename hash in this Sirus client.

LIGHTING / SKY
--------------
Map 10001 has 20 Light rows and 10 referenced LightParams rows.
Recovered DeathSkybox and Hyjal smoke sky assets and their discovered M2 companions.
LightSkybox also references Environments\Stars\JadeForestSky01.m2, which does not exist in any Sirus MPQ by exact filename hash.

LIQUIDS
-------
MH2O liquid types actually used: 1, 2, 5
  1 = Water
  2 = Ocean (dominant; present across all 81 active tiles)
  5 = Slow Water
Recovered 34 concrete XTextures/ocean rendering assets present in the Sirus client.

ZONE/SUBZONE AREA TABLE
-----------------------
  10004: Укрытие
  10050: Поднявшиеся глубины (10 terrain tile(s))
  10051: Затопленные руины (2 terrain tile(s))
  10052: Нерестилище (2 terrain tile(s))
  10053: Логово Карибдис (1 terrain tile(s))
  10054: Земли Жемчужного Плавника (2 terrain tile(s))
  10055: Ржавое ущелье (4 terrain tile(s))
  10056: Аммонитовый риф (2 terrain tile(s))
  10058: Молниевая Лагуна (4 terrain tile(s))
  10059: Туманная отмель (2 terrain tile(s))
  10060: Остров Проклятых (3 terrain tile(s))
  10061: Остров Кровавого Прилива (4 terrain tile(s))
  10062: Сердце Мглы (3 terrain tile(s))
  10064: Гряда Аквариона (4 terrain tile(s))
  10065: Бездна (12 terrain tile(s))
  10066: Остров Кораллового Когтя (3 terrain tile(s))
  10067: Стоянка Элементалей (1 terrain tile(s))
  10068: Ведьмин остров (1 terrain tile(s))
  10069: Проклятый Корабль (4 terrain tile(s))
  10070: Хищный Риф (2 terrain tile(s))
  10071: Мемориал Кало'теры (2 terrain tile(s))
  10072: Храм Тел'серай  (2 terrain tile(s))
  10073: Ставка Наместницы (1 terrain tile(s))
  10074: Усыпальница Кракена (4 terrain tile(s))
  10075: Руины Хажири (4 terrain tile(s))
  10433: Бескрайние глубины (78 terrain tile(s))
  10465: Логово сектантов

CLIENT-SIDE ZONE RECORD COUNTS
------------------------------
  Map: 1
  AreaTable: 27
  WorldMapArea: 2
  WorldMapOverlay: 18
  AreaPOI: 28
  AreaGroup: 0
  AreaTrigger: 1
  WorldSafeLocs: 4
  TaxiNodes: 0
  TaxiPathNode: 0
  TaxiPath: 0
  Light: 20
  LightParams: 10
  LightSkybox: 4
  WorldStateZoneSounds: 0
  WorldStateUI: 0
  WorldMapTransforms: 0
  ZoneIntroMusicTable: 0
  ZoneMusic: 0
  SoundAmbience: 0

KNOWN NON-EXTRACTION REFERENCES
-------------------------------
The recursive closure has six raw printable-string candidates that do not hash-match. Five are confirmed false/stale path strings caused by embedded historical names or shortened strings; the real active dependencies were recovered. The remaining active texture-table reference is world\expansion06\doodads\legion\8fx_explosionsmoke_a.blp, which the Sirus M2 references but no Sirus MPQ contains. This is a client-side stale/broken reference, not an extraction failure.

JadeForestSky01.m2 is also referenced by LightParams/LightSkybox but absent from every Sirus MPQ.

All extraction failure CSVs are empty (header only).

SCOPE LIMITATION
----------------
This package covers client/MPQ-side zone data discoverable through map/area DBC relationships, WDT/ADT structure, exact filename hashes, M2/WMO dependency recursion, world-map/minimap mappings, loading-screen records, lighting, liquids, and audio tables. Creature/NPC spawn placement, quest chains, scripts, vendors, and most gameplay logic are normally server-database/server-script data and are not encoded in the client terrain MPQs.
