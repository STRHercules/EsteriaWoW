# Final review fix report

Status: **PASS for the scoped fix wave**

The final-review findings were addressed in one scoped change. No plan or ledger
file was modified, and no subagent/reviewer was spawned.

## Changes

- `tools/playable_race_pack.py`
  - Resolves `dbc_root`, `model_root`, and `patch_b_root` before any donor read
    or staging operation.
  - Rejects `output_root` equality, ancestor, or descendant overlap with each
    of those three source roots.
  - Fails closed when a `SkillRaceClassInfo` donor row contains only one of
    source race bits 19/20; rows with both bits retain the existing replacement
    of both target bits 20/18 and all unrelated bits.
- `tools/test_playable_race_pack.py`
  - Adds production-path overlap coverage for both DBC and model donor roots in
    both ancestor/descendant directions.
  - Adds a single-source-bit `SkillRaceClassInfo` regression test and updates
    the shared fixture to match the reviewed donor invariant.
- `modules/mod-custom-server/data/sql/db-world/updates/u_custom_server_2026_09_10_01_race_scope_corrective.sql`
  - Adds `BaseLanguage` to the existing race-row preflight.
  - Adds read-only mismatch reporting for Alliance ID18
    (`FactionID=1`, `Alliance=0`, `BaseLanguage=7`) and Horde ID20
    (`FactionID=2`, `Alliance=1`, `BaseLanguage=1`), based on the project-owned
    `chrraces_dbc` registry/schema evidence.
- `tools/test_playable_race_contract.py`
  - Requires the `BaseLanguage` preflight field and both target metadata
    mismatch checks.

## Verification

- `rtk python tools/test_playable_race_contract.py -v` — **PASS**, 11 tests.
- `rtk python tools/test_playable_race_pack.py -v` — **PASS**, 25 tests.
- `rtk python -m py_compile` on the four playable-race Python files — **PASS**.
- `rtk git diff --check` — **PASS**.
- `rtk python apps/codestyle/codestyle-sql.py` — **BLOCKED before analysis** because
  this checkout has no `origin/master` ref (`fatal: couldn't find remote ref
  master`), consistent with prior reports.

No SQL import, configure/build, deployment, live runtime test, original Patch-B
write, or staged client asset change was performed. Pre-existing untracked
`DBCs/`, `NewMounts/`, and `Vehicles/` directories were preserved.
