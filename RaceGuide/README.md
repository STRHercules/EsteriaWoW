# EsteriaWoW race and custom-content developer guide

Developer handoff audited October 3, 2026. This guide explains how Esteria's playable races, expanded
appearance system, custom interface, mounts and supporting AzerothCore changes were assembled, and how
to reproduce the work. It combines all pages of the six requested chats with later repair chats, current
source, installed client files, effective MPQ entries, mounted server DBCs and read-only database queries.

## Read in this order

1. [Races and customization](01-RACES.md): identities, factions, controls and accepted behavior.
2. [Retroporting pipeline](02-PIPELINE.md): acquisition, conversion, integration and verification.
3. [Race-by-race recipes](03-RECIPES.md): maintained commands and the repairs each port needs.
4. [DLLs and binary catalogs](04-RUNTIME.md): source, ABI, loaders, encoding and every listed Esteria binary.
5. [AzerothCore changes](05-SERVER.md): compatibility, persistence, SQL, Freeborn, Eluna and modules.
6. [Interface and portraits](06-INTERFACE.md): login, creator, ECS, names, dropdowns and art.
7. [Mounts, geosets and equipment](07-MOUNTS-AND-GEOMETRY.md): additional content and geometry contracts.
8. [Outputs, deployment and rollback](08-OUTPUTS-AND-DEPLOYMENT.md): what to use from each working directory.
9. [Conversation reconciliation and gaps](09-EVIDENCE-AND-GAPS.md): superseded claims and current state.
10. [Developer verification checklist](10-VALIDATION.md): data, runtime and live acceptance gates.

## Included source and evidence

| Directory | Contents |
| --- | --- |
| `sources/EsteriaWoW/` | Tools, DLL source, race manifests, modules, SQL copies and changed core files |
| `sources/RetroPorter/` | Working acquisition/discovery/conversion orchestrator, manifests and tests |
| `sources/wow-race-retroporter/` | Requested scaffold, schemas, source/build policy and adapters |
| `sources/Converter/wotlkconv/` | Installed Converter Python source used by the working pipeline |
| `sources/WarcraftXL/` | 64-race extension, SDK headers, available extension/core source and build files |
| `sources/client-active/Interface/GlueXML/` | Effective Lua/XML/TOC extracted from the active archive stack |
| `sources/Portraits/` | Supplied portrait PNGs and faction artwork |
| `sources/RetroPorterWork/vulpera/` | Acquisition, inventory and BLTE-recovery helpers outside the repositories |
| `sources/historical-plans/` | Previously ignored UI, race, mount and repair tools, tests and plans |
| `sources/historical-diagnostics/` | Recovered temporary investigation scripts from the linked chats |
| `evidence/` | Hash manifests, conversation excerpts, workspace reports, current-state audit and core diff |
| `reference/` | Generated complete tool, option, race, artifact, module and core-file indexes |
| `tools/` | Utilities to capture, audit and verify this handoff |

Original-source and snapshot hashes are recorded in
[snapshot-manifest.json](evidence/snapshot-manifest.json). The shareable Compose copy substitutes an
environment variable for its SOAP credential. Historical snapshots retain their original machine
defaults; they are evidence and reusable source, not a batch of scripts to execute in order.

The package does not duplicate full Blizzard clients, raw CASC caches, the 4.9 GB workspace ZIP, MPQs or
large runtime texture banks. Their installed locations and captured hashes are in
[CLIENT_ARTIFACTS.md](reference/CLIENT_ARTIFACTS.md). Obtain matching inputs and rebuild derived outputs
through the documented stages. Use this source handoff alongside a complete Esteria checkout.

## The architecture that shipped

~~~mermaid
flowchart TD
    A[Retail and Forever CASC] --> B[RetroPorter plus Converter]
    P[wow-race-retroporter policy and schemas] --> B
    B --> C[RetroPorterWork reports and converted patch-root]
    C --> D[Esteria race integration tools]
    D --> E[Client assets and full DBCs in MPQs]
    D --> F[Native appearance catalogs]
    D --> G[Server DBC mounts and scoped SQL]
    H[EsteriaAppearance.dll imported by Wow.exe] --> F
    H --> E
    I[WarcraftXL 64-race extension] --> E
    J[GlueXML creator and ECS] --> H
    J --> E
    G --> K[Customized AzerothCore worldserver]
~~~

Three repositories have different jobs:

- **`wow-race-retroporter`** supplies policy, schemas and a resumable scaffold. Its generic stages still
  have implementation checkpoints; its `build` is not the production converter.
- **`RetroPorter`** is the working race-aware DB2 discovery and art-conversion frontend.
- **`EsteriaWoW/tools`** turns converted art into playable data, codecs, portraits and guarded stages.

Expanded customization uses **`EsteriaAppearance.dll` directly imported by `Wow.exe`**, independently
of WXL's appearance APIs. WarcraftXL still supplies the current 64-race runtime and other features.
Installing the helper does not replace the race-capacity extension.

## Original machine layout

| Purpose | Original path |
| --- | --- |
| Server/integration source | `R:\Users\Zach\Documents\GitHub\EsteriaWoW` |
| Requested scaffold | `R:\Users\Zach\Documents\GitHub\wow-race-retroporter` |
| Working art orchestrator | `R:\Users\Zach\Documents\GitHub\RetroPorter` |
| WarcraftXL source | `R:\Users\Zach\Documents\GitHub\AzerothPlex\build\wxl-core` |
| Derived working area | `G:\RetroPorterWork` |
| Active client | `G:\3.3.5a - Dev` |
| Portrait inputs | `R:\Users\Zach\Pictures\Portraits` |
| Native/install stages | `C:\Users\Zach\.codex\tmp\<race>` |
| Backups | Per-install receipts identify C: or G: directories |

Configure paths before using another computer. Some tools expose arguments, some use `RETROPORTER_*`
environment variables, and older integration scripts have literal paths. The recipes cover portability.

## First steps for another developer

1. Obtain the matching server checkout and a separate customized build-12340 client baseline.
2. Verify the snapshot and inspect [the known gaps](09-EVIDENCE-AND-GAPS.md).
3. Install pinned tooling and configure source/work/client paths.
4. Acquire one race's dependency closure and inspect its inventory.
5. Convert into a work directory; apply its animation/material/runtime repairs.
6. Generate matching DBCs, SQL, server codecs, UI entries and portraits.
7. Stage copies of the current winning archives and review validation.
8. Build required native/server components, then perform a backed-up, scoped install.
9. Complete the live checklist for both genders/factions and an unrelated race.

Retail IDs and Esteria IDs are separate. Database rows, conversions, loaded DLLs and running containers
do not prove playable rendering.

Commands here are reproduction instructions. Creating this guide did not convert assets, compile a
DLL/server, import SQL, patch a client or restart a service.

## Complete reference catalogs

- [Every captured Python tool/library](reference/ALL_TOOLS.md)
- [Exact customization labels and counts](reference/CUSTOMIZATION_OPTIONS.md)
- [Current client race rows](reference/RACE_ROWS.md)
- [Installed DLL/catalog locations and hashes](reference/CLIENT_ARTIFACTS.md)
- [Every core file changed since the AC import](reference/CORE_FILES.md)
- [Source-installed modules](reference/MODULES.md)
- [Provenance and missing historical files](reference/SOURCE_PROVENANCE.md)

Relative links keep the guide portable with its source snapshots.
