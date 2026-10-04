# Working outputs, deployment and rollback

[Back to the guide](README.md)

## What G:\RetroPorterWork contains

The work root separates source/discovery, generic conversion and playable integration. Use the latest
report plus hashes to identify a valid stage; a directory named `latest` is not automatically current.

| Path inside a race directory | Meaning / how to use |
| --- | --- |
| `retail-db2/` | Extracted source DB2 tables for the pinned build; discovery inputs |
| `reports/discovery.json` | Race/model/options/choices/material/dependency graph |
| `reports/asset-plan.json` | Exact assets scheduled for conversion |
| `reports/asset-convert.json` | Conversion results, paths, failures/losses and completeness |
| `reports/source-pin.json` / `source-inventory.json` | Build keys, source hashes and dependency closure |
| `reports/texture-layouts.json` | Source atlas/layer dimensions and mapping evidence |
| `output/patch-root/` | Generic converted assets; input to the playable integration |
| `integration/patch-root/` | Corrected playable geometry/material/art payload |
| `integration/codec.json` | Stable option ordering, choices, radices, capacities and prerequisites |
| `integration/customization-audit.json` | Included/excluded choices and source reasoning |
| `integration/rendering.json` / `preparation.json` | Model/material preparation details |
| `integration/source-acquisition.json` | Supplemental reachable FileDataID recovery |
| `integration/portraits.json` | Art input/output identities and hashes |
| `integration/acceptance.json` | Recorded stage/install/runtime acceptance; may contain stale intermediate status |
| `integration/latest/` / `expanded/` | Early Mag'har/Skyborne merged stages and native expansion data |
| `C:\Users\Zach\.codex\tmp\<race>/` | Native binaries, staged archives/DBCs, build reports and install receipts |

This handoff copies top-level report/integration JSON to `evidence/workspaces`. Large asset payloads
stay in the external work/client trees.

Current work families are `maghar`, `skyborne`, `mechagnome`, `highmountain`, `earthen`, `haranir`,
`vulpera`, `naga`, `tuskarr`, `vrykul` and `thinhuman`. `MagharDiscovery` is earlier investigation
material. `dreadlord` is a separate NPC override with PORT/source/build/geoset/display reports.

`RetroPorterWork.zip` is an approximately 4.9 GB backup of the work area. It is not a ready-to-install
race package and may predate later fixes. Inspect extracted reports/hashes against the active state.

## Workspace-specific outputs

- **Mag'har:** converted source, Orc2-based playable texture bake, legacy appearance/full DBC stage.
- **Skyborne:** initial curated stage plus native `expanded` descriptors, geometry/material data and
  corrected external animations. Native mode supersedes curated mode.
- **Mechagnome:** merged body/mechanical collections and complete parent/child animations, shared
  descriptor/material catalogs.
- **Highmountain:** codec/audit, full texture closure, BONE face reports, selections and final track/
  teardown stages.
- **Earthen:** source acquisition, sixteen-control codec, merged collection geometry, dedicated
  selection catalog and preview/persistence/feet touchups.
- **Haranir:** uint64 codec, layer audit/texture bank, reduced collection geometry and corrected
  client-buffer loader stage.
- **Vulpera:** source recovery scripts, source pins/inventory, atlas layouts, primary models, equipment
  coverage, helmet visibility/catalog, v2 codec and glow follow-up.
- **Creature ports:** narrower five-field codecs, source pins, texture banks, native selections,
  combined stage and later equipment/name/chat corrections.
- **Dreadlord:** Patch-Dr payload, restored UV lookup, source/build reports and rollback material.

## What belongs in the client

| Location | Content |
| --- | --- |
| Client root | Matched Wow.exe, EsteriaAppearance.dll and all required Esteria catalogs |
| `Extensions\races-64-esteria` | WXL race-capacity DLL and manifest |
| `Extensions\z-darkfallen-character-select` | Reviewed select/runtime DLL and manifest |
| `Data\Patch-R.MPQ` | Namespaced retroported assets |
| `Data\patch-Z.MPQ` | Winning root client DBC/Glue/custom content |
| `Data\enUS\patch-enUS-Z.MPQ` | Winning locale DBC/Glue/custom content |
| `Data\PATCH-X.MPQ` / `Patch-W.MPQ` | Earlier/later custom mount content |
| `Data\Patch-Dr.MPQ` | Dreadlord NPC override |
| `Interface\AddOns\EsteriaAppearanceCache` | Disposable helper-generated texture cache |

Other baseline archives remain part of the asset closure. The directory contains historical client
backup/staging folders too. Keep backups out of mountable `Data`; the Mag'har repair proved that renamed
backup MPQs can still win the archive scan.

The bin files are consumed from the client root, not copied into MPQs or the server DBC directory.
The same family can require its selection bank, texture bank, merged geometry catalog and physical
model/SKIN files simultaneously.

## Current client/server comparison

The audit reads the **effective** client files through the repository's archive resolver and compares
the mounted server source files. These are current findings:

| Table | Client records | Comparison |
| --- | ---: | --- |
| ChrRaces | 47 | Only semantic row differences are 58/59's Forgotten display-name change |
| CharStartOutfit | 1,043 | Byte-identical |
| CharSections | 547,108 | Same complete row multiset/string pool; different row ordering |
| BarberShopStyle | 8,083 | Byte-identical |
| CreatureDisplayInfo | 26,152 | Byte-identical |
| CreatureModelData | 1,639 | Byte-identical |
| Spell | 51,358 | Byte-identical |
| SkillRaceClassInfo | 328 | Server has 364 expanded eligibility rows; different policy layer |

Client CharSections is sorted for its native cache. The server file has the same content in its earlier
order. Do not describe all seven as byte-identical today just because an original install report did.

Server SQL race overlays retain legacy/NPC rows absent or different in client data. See the live SQL
readback and [the gaps](09-EVIDENCE-AND-GAPS.md) before reusing those IDs.

The inspected worldserver was running image
`sha256:1af4a401fee6d1f77b1bc477dde7c6594b4498370fa46ce2cf8c53e69df5dc70`.
Its bind mounts and migration/schema readbacks are captured. This does not establish that every
uncommitted source change is in that image or that live gameplay was tested during this guide task.

## Staging rules

1. Record current client source hashes, server DBCs, migration receipts and character appearances.
2. Build from the current winning root/locale archives; preserve unrelated entries.
3. Generate all matching native catalogs and headers.
4. Use compressed temporary archives and validate actual entries, not only staged loose files.
5. Validate model/texture dependency closure and compatibility with the current executable/helper.
6. Reject stale source hashes, unfamiliar executable signatures and foreign ID collisions.
7. Review the exact output set and named rollback directory before replacement.

The packers use StormLib, not 7z. Do not stream the same MPQ concurrently through several writers.
Keep classic archive offsets within the tested boundary; earlier uncompressed >2 GiB copies produced
real client read failures. Recompression must preserve every unrelated entry.

## Build and database scope

For a new race whose server C++/headers changed, build the matching worldserver. A Lua/art/catalog-only
repair may not require a server rebuild. Repo instructions require explicit authorization for builds;
the commands below document the established deployment pattern.

~~~powershell
docker compose build ac-worldserver
~~~

A clean `--no-cache` build was specifically used for the approved Darkfallen deployment; it is not
required for every texture repair.

Back up the reviewed stage and affected character/database rows. Stop only worldserver when the
installer requires database/appearance consistency:

~~~powershell
docker compose stop ac-worldserver
~~~

Run the specific packer's `backup`/`install` or reviewed migration path. Do not substitute a bulk SQL
import or delete updater receipts. Read back the affected starts, spells, languages, schema and
migration hashes.

Recreate only the matched server:

~~~powershell
docker compose up -d --no-deps --no-build --pull never --force-recreate ac-worldserver
~~~

This keeps the existing auth/database services and persistent volumes. Never use `down -v` for a race
deployment. Observe readiness and errors, then start the client fresh.

## Client replacement and runtime restart

WoW and Eclipse must be closed before replacing mounted archives or loaded DLLs. Build to scratch
while they are open; do not attempt a partial overwrite. Hash-verify backups, stage readbacks and copied
files, and retain the report as the output identity.

A full client restart reloads cached catalogs and native components. `/reload` does not reload root
DLLs or Glue at the same stage. Texture-cache removal, when necessary, is scoped to the disposable
generated cache, not character state.

## Rollback is a matched set

A rollback restores the previous executable/helper pair, catalogs, root/locale/assets archives,
mounted server DBCs and affected character appearance tuples where they changed. Use the receipt's
actual file set; later helper-only repairs have a narrower rollback than initial ports.

Keep the prior worldserver image tag and migration/appearance rollback SQL. With worldserver stopped,
restore the affected files and execute only the scoped rollback, then recreate only worldserver.

For Haranir rollback, retaining the widened BIGINT column avoids truncating saved high bits. Existing
characters need an explicit policy before removing a race. Do not delete new characters merely to
satisfy an old first-port installer guard.

## Moving this handoff to another machine

1. Copy `RaceGuide` with `sources`, `reference`, `evidence` and `tools` intact.
2. Verify the captured hashes.
3. Use a complete matching Esteria/WarcraftXL checkout for upstream/vendor/build dependencies.
4. Overlay the relevant current source; do not run source snapshots as if they were a live installation.
5. Configure literal paths and the exposed arguments/environment variables.
6. Supply the verified customized executable baseline, source assets, StormLib and Converter metadata.
7. Rebuild outputs from reports/codecs; do not copy GUID-specific migration assumptions unchanged.
8. Capture a new target-machine inventory and complete live acceptance.

The original foundation-image injector was not recovered here. The fingerprinted baseline is therefore
an explicit required input. Every recovered script and the missing historical diagnostic are cataloged,
so remaining gaps are visible rather than replaced by invented commands.

## Handoff utilities

From a full Esteria checkout:

~~~powershell
rtk proxy python -X utf8 RaceGuide/tools/capture_snapshot.py
rtk proxy python -X utf8 RaceGuide/tools/audit_current_state.py --database
rtk proxy python -X utf8 RaceGuide/tools/write_references.py
rtk proxy python -X utf8 RaceGuide/tools/capture_snapshot.py --verify
rtk proxy python -X utf8 RaceGuide/tools/verify_guide.py
~~~

`capture_snapshot` reads sources and writes only its own RaceGuide snapshots/manifests.
`audit_current_state` reads MPQs/DBCs and writes the effective Glue source/current-state report.
`--database` adds SELECT/SHOW queries and a limited container state/mount read; it does not mutate DBs.
`write_references` uses saved evidence to regenerate the indexes. Verification does not need the client
to render or a server rebuild. Refreshing evidence does not automatically rewrite the authored narrative.
