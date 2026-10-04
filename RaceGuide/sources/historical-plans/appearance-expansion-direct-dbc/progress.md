# SDD ledger — plan: .agents/plans/appearance-expansion-direct-dbc/appearance-expansion-direct-dbc.PLAN.md

Pre-flight: current branch is `main` with extensive unrelated dirty changes; user explicitly authorized the live client/server edits, so no reset, cleanup, or worktree migration will be performed.

Ruling: no Git commit for generated client/server artifacts — the requested deliverables are external MPQ/Docker-volume files and a package-local report; committing the dirty repository or binary copies would capture unrelated user work.

Task 1: complete — the table-aware direct-DBC merger, MPQ collision checks, High Elf cloning, and regression tests were implemented; focused merger tests finished 4/4.

Ruling: client backups were placed on C: while server backups remain under the package — R: had only 121 MB free and could not hold the two 142 MB client archives; cost if wrong: rollback requires the documented C: path.

Task 2: complete — client root/locale MPQs and all four live server DBCs were SHA-256 verified before installation; no world, character, or Playerbot database mutation was performed.

Task 3: complete — staged artifacts/report generated at C:\Users\Zach\Documents\EsteriaWoW-Builds\appearance-expansion-20260920-064051; archive/DBC/static preservation checks passed.

Task 4: complete — only ac-worldserver was stopped, four stock server DBCs and both client Z archives were installed, live hashes matched, and the fresh worldserver log reached ready without appearance-DBC load errors.

Task 5: complete — ESTERIA_INSTALL.md records the executed direct-DBC install, counts, hashes, backups, Playerbot behavior, manual gaps, and rollback.

Ruling: no Playerbot source/database change — existing RACE_HIGHELF and sCharSectionsStore paths already consume the merged data; cost if wrong: a new High Elf bot still needs manual gameplay verification.

Ruling: test_playable_race_contract.py retains one pre-existing failure — current dirty checkout lacks allowlist IDs 14, 18, and 20; this task did not alter that unrelated contract, and the cost if wrong is limited to the existing unrelated Playerbot race-allowlist gap.
