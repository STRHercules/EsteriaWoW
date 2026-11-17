# Remaining model and feature-data requirements

Audited 2026-11-17 against the isolated installer startup logs, module SQL/catalogues,
the working reference world database and local development/client staging. These
findings distinguish missing server records from missing physical client files.

## Creature display warnings: Battlemon

The baseline logged **85 unique creature/display references** with a missing
CreatureDisplayInfo ID. All 85 templates use `npc_battlemon_overworld`; these are
Pokemon forms/palettes, not core race, Classless summon, Housing or Garrison models.
The [complete CSV inventory](server-install-missing-creature-displays.csv) lists
each creature entry, name, old display ID and current 3D catalogue status.

Cross-checking `modules/mod-battlemon/data/3d/catalog.json` gives:

- **77 unsupported legacy variants** have no appearance in the current supported
  3D catalogue. Examples include Pikachu variants 08-16 and Ogerpon variants 04-11.
  They do not need new models to support the current catalogue. Recovering those
  particular legacy appearances would be a separate asset task.
- **Eight rescued forms** already have replacement normal/shiny displays in the
  repo's one-time 3D transition. These need the paired deployment, not invented
  placeholder models.

| Creature | Entry | Old missing display | Existing 3D normal / shiny |
| --- | ---: | ---: | --- |
| Rainy Form Castform | 1000544 | 50544 | 400454 / 400455 |
| Spiritomb | 1000675 | 50675 | 400532 / 400533 |
| Fan Rotom | 1000738 | 50738 | 400552 / 400553 |
| Basculin | 1000840 | 50840 | 400567 / 400568 |
| Blue-Striped Basculin | 1000841 | 50841 | 400565 / 400566 |
| Joltik | 1000904 | 50904 | 400597 / 400598 |
| Lampent | 1000918 | 50918 | 400599 / 400600 |
| Araquanid | 1001160 | 51160 | 400639 / 400640 |

Spiritomb, Joltik, Lampent and Araquanid also produced runtime "no model defined"
spawn errors. The inspected reference database has no static `creature` spawn rows
for these 85 templates, but that does not make them unused: Battlemon dynamically
spawns/morphs creatures, and its overworld feature defaults to enabled.

The repo already contains six hashed server eDBC layers under
`modules/mod-battlemon/data/3d/dbc-continuations`. None is in the captured baseline
server-data archive. Before qualifying the 3D feature, align those layers, the 3D
catalogue/transition state and the matching client model package. Follow
[Battlemon deployment](../modules/mod-battlemon/3D-DEPLOYMENT.md), including its
collision guards. Do not blindly replay the manual 2D-to-3D character migration
on an already migrated realm; it changes ownership state and requires backups.
For the read-only Docker data volume, prepare a new staged/versioned bundle rather
than editing the running container's mounted data.

These warnings establish missing server display records, not 85 missing `.m2`
files. Full client mesh/skin/animation/texture closure was not re-audited here.
They are not required for core server startup or Manastorm. For Battlemon, deploy
the paired supported catalogue or disable `BattlemonOverworld.Enable` (and, if
necessary, the battle feature) until its client/data acceptance is complete.

## Housing

The installer includes the Housing world/character schema, catalogue and map/area
definitions. The module is disabled by default. Its current maps are:

| Map | Purpose |
| ---: | --- |
| 2783 | Home Interior |
| 2735 | Founder's Point |
| 2736 | Razorwind Shores |

The matching client needs the retail WDT/ADT terrain, room/exterior/decor WMOs and
M2s, skins/textures, the Housing DBC patch, WDT/asset aliases, native extensions and
Housing addon. The SQL display/catalogue rows alone do not deliver those visuals.
The WDT aliases are based on retail file IDs 5890928, 5660542 and 5660543.

No `maps`, `vmaps` or `mmaps` files for these three map IDs were present in the
inspected active server data. They are also not provided by the pinned stock v20
terrain package. Missing terrain is tolerated by the loader; the fixed-Z,
client-authoritative prototype can operate without those files. They are **not a
hard server-startup requirement**, but normal server height, collision/line-of-
sight and navigation behavior would require suitable server geometry/export work.
Runtime-built rooms also need an approach that accounts for their dynamic layout.
Stock WotLK extractors do not directly understand these retail terrain layouts.

## Garrison

The six tier maps are Alliance **1158, 1331, 1159** and Horde **1152, 1330, 1153**.
No matching server `maps`, `vmaps` or `mmaps` files were present for them in the
inspected active data. The Garrison module currently uses fixed spawn heights;
missing server geometry limits terrain queries, NPC navigation and line-of-sight.
It does not make these files necessary for the baseline with Garrison disabled.

The matching client needs the six retail terrain maps, building/doodad/NPC models,
skins/textures, Garrison DBC/world-map patch, WDT aliases, native Garrison extension,
EsteriaGarrison addon and Blizzard_GarrisonUI art. See
[the module's installation instructions](../modules/mod-esteria-garrison/README.md).

The required Garrison SQL and DBC-overlay SQL are already in the repo but are not
auto-imported by this baseline. `GarrisonDB2.cpp` reads DB2-derived **SQL tables**;
there is no separate raw DB2-file runtime download required by that loader. Apply
the module's world/character SQL and overlays before enabling it. This publication
does not claim to validate the separate in-progress Garrison changes.

## What already exists locally

Both inspected Dev and Live clients already contain these packs:

| Pack | Observed bytes |
| --- | ---: |
| `patch-RetailGarrison-001.MPQ` | 2,193,338,600 |
| Garrison DBC/world-map patch (28 Zs) | 105,716,088 |
| Housing development patch | 131,539,701 |
| `Patch-ZzzzBattlemon.MPQ` | 1,829,481,876 |

Garrison retail staging contains 12,713 files totaling 2,182,296,475 bytes. These
presence/size checks are not an exhaustive verification of every referenced
asset or the later Pixelmon extras in the client's winning archive chain.

The client-side packs are therefore not simply "lost"; they need to be included
and qualified in the matching client distribution. They are intentionally absent
from the server-only Git package. Server geometry for the nine Housing/Garrison
maps remains separate work if authoritative height/collision/pathing is required.
Neither optional feature's assets are required to reproduce the validated core
server startup. No client files or live databases were changed for this audit.
