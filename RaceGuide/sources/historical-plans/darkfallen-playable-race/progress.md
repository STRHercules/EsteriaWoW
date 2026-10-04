# Darkfallen checkpoint ledger

- Baseline: `tools/test_darkfallen_contract.py` ran 7 tests; 5 passed and 2 failed because `tools/darkfallen_race_pack.py` and `rev_1787850000020_darkfallen.sql` were absent.
- Workspace: existing `main` checkout is intentionally retained because it contains the user's dirty race-extension state and the active client is outside the repository.
- In progress: map reusable WDBC/MPQ/Glue helpers and exact SQL schemas before adding the first implementation files.
