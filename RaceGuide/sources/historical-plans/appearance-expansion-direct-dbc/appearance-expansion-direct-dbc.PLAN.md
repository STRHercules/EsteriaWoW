# Esteria Appearance Expansion Direct DBC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge the extracted Classic appearance expansion into Esteria's live client and server DBCs additively, including Blood Elf-derived High Elf options and Playerbot availability, without overwriting existing rows or assets.

**Architecture:** Read the winning root and enUS client MPQs and the live `ac-worldserver` DBC volume as immutable bases. Parse all four appearance WDBC tables, clone donor Blood Elf rows to High Elf, allocate collision-free row IDs, preserve existing semantic selections, and rebase string pools. Build replacement archives from the original entries plus donor assets, install the same merged tables in both client archives and the server's stock DBC directory, then verify hashes, row preservation, references, and server startup.

**Tech Stack:** Python 3 standard library, repository StormLib wrapper, WDBC binary format, StormLib MPQ read/write, Docker volume copy, PowerShell/certutil verification.

**Spec:** `NewModels/_Other/WoW-Appearance-Expansion-0.3.0-beta(1)/WoW-Appearance-Expansion/ESTERIA_INSTALL.md` (updated by Task 5 with the executed merge report and rollback instructions).

## Global Constraints

- Use direct stock DBC files; do not create, install, or depend on DBC continuations.
- Preserve every current client MPQ entry and every current server DBC row.
- A same-path asset collision with different bytes aborts the build; identical bytes are retained once.
- Blood Elf race ID 10 rows are cloned to High Elf race ID 13; existing High Elf rows remain untouched.
- Keep the current root and locale client DBC entries synchronized because both archives currently contain the winning tables.
- Do not run `Setup.cmd`, `Setup.ps1`, or donor `Install.ps1`; do not configure or build; do not edit immutable SQL.
- Do not alter Playerbot C++ or databases unless verification proves the existing data path is insufficient.
- Back up every external file before changing it and record SHA-256 hashes.
- Preserve all unrelated dirty worktree changes and do not reset, checkout, or clean the repository.

## Review Focus

- Existing row IDs that collide with donor IDs must be remapped, never replaced.
- Existing semantic appearance keys with different donor bytes must retain the Esteria row and be reported as conflicts.
- Blood Elf-to-High Elf cloning must change only the race field and preserve all other appearance relationships.
- WDBC string offsets must point into the rebuilt pool after merge.
- Root and locale archives must contain byte-identical merged DBC entries and all referenced donor assets.

---

### Task 1: Build and test the table-aware merge tool

**Files:**
- Create: `NewModels/_Other/WoW-Appearance-Expansion-0.3.0-beta(1)/WoW-Appearance-Expansion/tools/merge_esteria_appearance.py`
- Create: `NewModels/_Other/WoW-Appearance-Expansion-0.3.0-beta(1)/WoW-Appearance-Expansion/tools/test_merge_esteria_appearance.py`

**Interfaces:**
- Consumes: four base WDBC byte strings, four donor WDBC byte strings, and a donor/client asset map.
- Produces: merged WDBC bytes, a JSON report, and collision-checked merged MPQ entries.

- [ ] Add tests for WDBC parsing, string-pool rebasing, collision-free row allocation, semantic-key preservation, and race-10-to-race-13 cloning.
- [ ] Run the tests once and confirm the intended missing/incorrect implementation failure.
- [ ] Implement the minimum table-aware merger using the existing `RawWdbc` and `Storm` helpers where they fit; keep CharSections selection keys and non-ID facial-style semantics explicit.
- [ ] Run the focused tests and then the repository appearance-tool tests.

### Task 2: Snapshot all external bases

**Files:**
- Create: `NewModels/_Other/WoW-Appearance-Expansion-0.3.0-beta(1)/WoW-Appearance-Expansion/backups/<timestamp>/`
- Create: a backup manifest containing source paths, sizes, and SHA-256 values.

- [ ] Confirm no WoW or worldserver process is using the target files.
- [ ] Copy `G:\3.3.5a - Dev\Data\patch-Z.MPQ` and `G:\3.3.5a - Dev\Data\enUS\patch-enUS-Z.MPQ` into the backup directory and hash them.
- [ ] Copy the four live files from `/azerothcore/env/dist/data/dbc` in `ac-worldserver` into the backup directory with `docker cp`, and hash them.
- [ ] Record that world and character databases are unchanged because no bot-refresh operation is being applied.

### Task 3: Inventory and generate merged artifacts

**Files:**
- Create: `NewModels/_Other/WoW-Appearance-Expansion-0.3.0-beta(1)/WoW-Appearance-Expansion/build/esteria-appearance/`
- Create: `merge-report.json` and merged four-table DBCs.

- [ ] Read both current archives and the extracted donor archive through StormLib; fail on unreadable or non-ASCII paths.
- [ ] Merge all four donor tables into each current client table, clone Blood Elf rows to High Elf, preserve current rows, and validate referenced paths against the donor/current asset set.
- [ ] Add donor assets to a complete copy of the current root archive and mirror the merged DBC entries into both root and enUS archives; abort on different-byte path collisions.
- [ ] Emit counts for kept, added, cloned, deduplicated, conflicted, omitted, and missing-reference rows/assets before installation.

### Task 4: Install directly and verify server/client state

- [ ] Stop only the relevant `ac-worldserver` service if it is running, install the merged four DBCs into its stock `/azerothcore/env/dist/data/dbc`, and preserve the backups.
- [ ] Replace the two client archive files only after the generated artifacts pass all static checks; use a temporary file and atomic move per archive.
- [ ] Verify current-row preservation, unique IDs, High Elf coverage, synchronized client/server table hashes, asset references, and MPQ entry counts.
- [ ] Restart only `ac-worldserver` if it was running and inspect the fresh startup log for DBC load errors. Do not rebuild or configure.
- [ ] Verify Playerbot code/data paths statically and record that newly created High Elf bots can select the merged options; do not rewrite existing characters or bot databases.

### Task 5: Update the installation/report document

- [ ] Rewrite `ESTERIA_INSTALL.md` so it documents the executed direct-DBC merge, backups, exact artifacts, row/asset counts, High Elf and Playerbot behavior, live-test gaps, and rollback commands.
- [ ] Remove all continuation-based installation instructions from the document.
- [ ] Run a final path/hash/report/document consistency check and preserve the ledger.

## Rollback

Restore the two client MPQs from the timestamped backup, copy the four server DBC backups back into `/azerothcore/env/dist/data/dbc`, and restart only `ac-worldserver`. No database rollback is required because this plan does not mutate world or character databases.
