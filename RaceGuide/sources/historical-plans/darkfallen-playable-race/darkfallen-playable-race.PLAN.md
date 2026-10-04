# Darkfallen Playable Race Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the approved Darkfallen Alliance/Horde client and server-data package without overwriting unrelated custom-race work.

**Architecture:** The existing `darkfallen_race_pack.py` stages additive root and locale MPQ updates from the supplied assets and active Z-archive contents. The dedicated pending SQL migration supplies matching server creation data. The active archives are changed only after the contract test stages successfully and two hash-verified backups exist.

**Tech Stack:** Python 3, unittest, StormLib, WDBC, MySQL migration SQL, WoW 3.3.5a MPQ/Glue assets.

**Spec:** `.agents/plans/darkfallen-playable-race/darkfallen-playable-race.REQUIREMENTS.md`

## Global Constraints

- Race IDs are exactly `43` Alliance and `44` Horde; both map to `0x80000000`.
- Model data/display IDs are exactly `3658`/`3659` and `60028`/`60029`; filestring is `Darkfallen`.
- Faction-specific creation remains Common for 43 and Orcish for 44.
- Reuse existing helpers; no dependencies, wholesale donor files, resets, or unrelated edits.
- Back up both live Z archives with SHA-256 before a collision-checked staged install.
- Do not configure/build/restart the server in this task.

## Review Focus

- Existing target IDs or MPQ paths: installation must abort before replacing an unexpected entry.
- WDBC strings: cloned string offsets must point into the rebuilt table pool.
- Creator enumeration: buttons stay faction-grouped positions rather than race IDs.
- Shared mask: creation-language rows must retain faction behavior despite one mask.
- Archive safety: staging must not change the source archive hashes.

---

### Task 1: Validate and repair the Darkfallen packer

**Files:**
- Modify only if the focused contract test proves it necessary: `tools/darkfallen_race_pack.py`
- Modify only if it needs a missing behavior assertion: `tools/test_darkfallen_contract.py`

**Interfaces:**
- Consumes: supplied Darkfallen assets and source root/locale Z archive copies.
- Produces: `build_darkfallen_pack(root, locale, output)` with staged root/locale MPQs and exact update maps.

- [ ] **Step 1: Run the focused contract test before any production edit**

Run: `python tools/test_darkfallen_contract.py`

Expected before a repair: a behavioral failure identifying the missing merge or safety guard; otherwise record the existing green baseline.

- [ ] **Step 2: Implement only the failing packer behavior**

Preserve `build_darkfallen_pack` and add the smallest table-aware/collision-safe correction needed for the failing assertion. Keep root Glue/WDBC entries in root and `GlueStrings.lua` in locale.

- [ ] **Step 3: Re-run the focused contract test**

Run: `python tools/test_darkfallen_contract.py`

Expected: all non-skipped assertions pass and the test confirms source archive hashes remain unchanged.

### Task 2: Validate and repair the dedicated server migration

**Files:**
- Modify only if audit/test evidence requires it: `modules/mod-custom-server/data/sql/updates/pending_db_world/rev_1787850000020_darkfallen.sql`
- Modify only if it needs a missing contract assertion: `tools/test_darkfallen_contract.py`

**Interfaces:**
- Consumes: existing custom-race schema and server-side shared-mask plumbing.
- Produces: idempotent Darkfallen DBC/player-creation rows matching the staged client data.

- [ ] **Step 1: Add or use a focused assertion for a missing migration contract**

The assertion must cover the exact missing `43`/`44` faction data, mask, or ID collision safeguard and fail before the SQL correction.

- [ ] **Step 2: Apply the minimal idempotent SQL correction**

Use matching delete/insert blocks or guarded temporary-table statements; do not modify immutable SQL locations.

- [ ] **Step 3: Run the focused contract and SQL style checks**

Run: `python tools/test_darkfallen_contract.py` and `python apps/codestyle/codestyle-sql.py`.

Expected: contract passes; report any unrelated baseline linter failures by name.

### Task 3: Back up and install the verified client package

**Files:**
- Modify: `G:\3.3.5a - Dev\Data\patch-Z.MPQ`
- Modify: `G:\3.3.5a - Dev\Data\enUS\patch-enUS-Z.MPQ`
- Create: a timestamped backup pair adjacent to the active archives.

**Interfaces:**
- Consumes: the passing packer stage and exact archive update maps.
- Produces: both active archives containing the verified Darkfallen client package, with restorable backups.

- [ ] **Step 1: Hash and copy both active archives before mutation**

Record SHA-256 for each active archive and its backup. Abort if either backup hash differs.

- [ ] **Step 2: Stage and collision-check the complete package**

Run the packer against copies/staging and require a zero-unexpected-collision report before replacing either active archive.

- [ ] **Step 3: Install atomically per archive and post-verify entries**

Replace only after the stage and backup checks pass. Re-open both active archives through StormLib and verify required WDBC, asset, root Glue, and locale GlueStrings entries.

- [ ] **Step 4: Record live-test handoff**

Do not claim server/gameplay completion without a separately authorized DB import/server restart and manual creation, relog, and equipment smoke.

### Task 4: Remove the remaining direct player-race bit shift

**Files:**
- Modify: `src/server/game/Entities/Unit/Unit.h`
- Modify: `tools/test_darkfallen_contract.py`
- Inspect only: `src/server/game/Handlers/MiscHandler.cpp`

**Interfaces:**
- Consumes: `GetRaceMaskForRace(uint32)` from `SharedDefines.h`.
- Produces: `Unit::getRaceMask()` that represents either Darkfallen race as the shared high bit.

- [ ] **Step 1: Add a focused failing contract assertion**

Assert that `Unit::getRaceMask()` calls `GetRaceMaskForRace(getRace(true))`, then run the focused Darkfallen contract to observe that assertion fail before modifying C++.

- [ ] **Step 2: Replace only the direct Unit race shift**

Implement `return GetRaceMaskForRace(getRace(true));` in `Unit::getRaceMask()`. Inspect the WHO packet filter separately and change it only if the packet mask contract proves the helper is compatible.

- [ ] **Step 3: Verify the C++ source contract**

Run: `python tools/test_darkfallen_contract.py` and the C++ style checker for the changed file. Do not configure/build/restart the server.
