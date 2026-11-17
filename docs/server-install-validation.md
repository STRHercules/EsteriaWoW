# Server installation validation — 2026-11-17

The standalone installer was built and exercised on Linux AMD64 containers using
Ubuntu 24.04, Clang 18.1.3 and MySQL 8.4.11. This is server-side integration evidence;
it is not client or gameplay acceptance.

## Baseline

The build context contained repository files and the installer changes, with
submodules initialized. Machine-local `conf/config.cmake`, ignored custom scripts,
developer bind mounts and the unrelated working-tree Garrison edits were excluded.
The persistent development builder and running realm were not changed.

| Check | Result |
| --- | --- |
| Source build: AuthServer, WorldServer, dbimport | Passed |
| New MySQL volume: compiled dbimport creates/imports auth, characters and world | Exit 0 |
| Server data: official v20 terrain download, SHA-256, custom DBCs and continuations | Exit 0 |
| AuthServer listener and online realm record | Passed |
| WorldServer explicit ready message | Passed |
| Playerbots database and initialization | 30 tables; world-thread processor initialized |
| Configuration after image recreation | Existing marker preserved; module configs loaded |
| Explicit auth/world restart | Both listeners returned; another world-ready message |
| Installed catalogues | 244 Incarnations looks; 2,866 Housing decor entries |
| Offline installer tests | Eight passed |

The test used a separate Compose project, database, volumes and ports. The default
baseline excludes Manastorm and the superseded standalone Attunement Plus module.
Classless Wildcard and Playerbots were included. Initial Playerbots pool creation
takes time even with random bot autologin disabled.

## Manastorm

A separate image included Manastorm and used disposable databases. The complete
SQL sequence passed from empty databases with the recovered item package. The
compiled importer also passed statement preparation. Native Mode 2 reached
world-ready and logged **Shared Manastorm backend initialized**, both initially
and after restart, with no invalid-datastore message in the final run.

The verified datastore loaded 296 segments, 2,000 endgame depth points, five
endgame group ranges, 27 affixes and 36 progression unlocks. Its private actor
table contains 35 records: the original 14 and 21 restored route dependencies.
The final reward pool contains 126,457 enabled entries and zero missing or
quality-mismatched enabled items. The compatibility migration excluded 173
incompatible entries without changing shared item stats or authored weights.

The tests exposed and fixed missing persistence schemas, missing endgame curves,
missing private route actors, the native DBC path, first-run module configuration,
two DevMenu API incompatibilities and empty custom-script loader discovery.

## Remaining boundaries

- A matching client, character creation/rendering, combat, actual Manastorm runs,
  rewards, relog and clean client exit were not tested.
- Housing and Garrison remain off. Their extra retail terrain/assets are not part
  of the pinned stock terrain package.
- Existing content warnings remain, including 85 missing display references for
  Battlemon/Pokemon variants and separate orphaned creature spell definitions. A ready
  server is not proof that every creature is safe to render in a client.
- The [asset audit](server-install-asset-gaps.md) identifies those display references,
  existing 3D replacements and the precise Housing/Garrison data requirements.
- Local ignored custom scripts are not part of the published source build. In
  particular, local Kyrian hover/racial implementations were excluded from this
  clean-context test; their gameplay was not qualified.
- The full C++ unit suite was not built. Repository-wide linters were attempted:
  the C++ checker encounters an existing Eluna PNG, and the SQL checker expects a
  nonexistent remote `master` and flags generated SQL formatting. These are not
  clean global lint gates. Compilation, integration checks and `git diff --check`
  passed.

Issue #4 should retain these distinctions when reporting installation support.
Publication of the changes and a retry by the reporter are separate from this
local validation.
