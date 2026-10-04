# Darkfallen Playable Race Implementation Plan

> **For agentic workers:** Execute inline in the existing checkout. Preserve unrelated dirty work and verify every checkpoint before moving on.

**Goal:** Add Darkfallen as unique Alliance race 43 and Horde race 44 with custom models, creation UI data, Common/Orcish language behavior, start data, and temporary racial abilities.

**Architecture:** Use a small Python packer that reads the active Z archives as merge bases, clones compatible Blood Elf rows, rewrites only Darkfallen-owned IDs/paths, and rejects case-insensitive archive collisions. Use one idempotent pending world SQL migration for server-side race/start/language/spell data. Keep faction identity in race IDs/ChrRaces TeamID; the shared `0x80000000` mask is not used for faction decisions.

**Tech Stack:** Python 3 stdlib, repository StormLib wrapper/WDBC helpers, WotLK 3.3.5a WDBC/GlueXML, AzerothCore pending world SQL.

**Spec:** `NewModels/_Other/PlayableDarkfallen/Darkfallen/DARKFALLEN.md` and the approved contract in the task handoff.

## Global Constraints

- Alliance race ID `43`; Horde race ID `44`.
- Shared WXL race mask `0x80000000`; never calculate `1 << (race - 1)` for these IDs.
- Unique client filestring `Darkfallen`; Blood Elf helmet prefix `Be`; model data IDs `3658/3659`; display IDs `60028/60029`.
- Allowed classes: `1,2,3,4,5,6,7,8,9,11`; Alliance starts Elwynn/Common; Horde starts Durotar/Orcish.
- Active archives are `G:\3.3.5a - Dev\Data\patch-Z.MPQ` and `G:\3.3.5a - Dev\Data\enUS\patch-enUS-Z.MPQ`.
- Do not build, restart services, import SQL, or claim live playability without explicit evidence.
- Do not overwrite unrelated dirty files or replace complete client archives without SHA-256 backups.

## Checkpoints

1. Add packer and migration; run `py_compile`, contract test, and SQL linter.
2. Run packer against temporary/output copies and verify WDBC rows, asset paths, Glue, and collision rejection.
3. SHA-256-back up both active Z archives, apply the packer, and verify the resulting archives.
4. Update `DARKFALLEN.md` with actual implementation state and evidence; leave live creation/relog/equipment testing explicitly pending.

## Review Focus

- Shared mask must not make Alliance race 43 use Orcish or Horde race 44 use Common; test source and SQL faction routing.
- Existing archive entries must survive the merge; test path collision rejection and required-entry presence.
- WDBC strings and row IDs must remain valid after cloning; test headers, record sizes, offsets, and references.
- Missing supplied textures must fall back to Blood Elf paths without creating broken Darkfallen references.
- Character creator button ordinals are faction enumeration positions, not race IDs; verify both faction buttons and `MAX_RACES`.

### Task 1: Packer and contract test

**Files:** Create `tools/darkfallen_race_pack.py`; use existing `tools/test_darkfallen_contract.py` as the red/green contract. Reuse Storm/Wdbc/archive helpers from `tools/cars_mount_pack.py` where practical.

- [x] Baseline test run recorded red because packer/migration are absent.
- [ ] Implement `--print-contract`, archive merge, WDBC cloning, supplied asset packaging, Glue/locale patching, and collision checks.
- [ ] Run `python -m py_compile tools/darkfallen_race_pack.py` and `python tools/test_darkfallen_contract.py`.

### Task 2: Server migration

**File:** Create `modules/mod-custom-server/data/sql/updates/pending_db_world/rev_1787850000020_darkfallen.sql`.

- [ ] Add idempotent DBC overlays for race/model/display/start outfit/customization/skill-mask rows.
- [ ] Add player-create, action, item, skill, stats, language, and temporary racial spell data for both faction IDs.
- [ ] Run the repository SQL codestyle check and inspect all affected tables/IDs.

### Task 3: Archive staging and documentation

**Files:** Active Z archives outside the repository; update `NewModels/_Other/PlayableDarkfallen/Darkfallen/DARKFALLEN.md`.

- [ ] Back up and hash both active archives.
- [ ] Apply the packer to root and locale archives, then re-open and verify required entries and references.
- [ ] Document exact applied artifacts, hashes, static checks, and the remaining live-game matrix.
