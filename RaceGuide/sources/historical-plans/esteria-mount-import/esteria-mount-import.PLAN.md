# Esteria Additive Mount Import Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the 89 WotLK-format mount models from the supplied folders to the existing `PATCH-X.MPQ` as additive, collision-safe client assets with synchronized WotLK DBC continuations and server SQL.

**Architecture:** Extend the existing `tools/cars_mount_pack.py` generator with directory-based mount discovery, WotLK v264 filtering, deterministic ID allocation, model-asset packaging, DBC continuation generation, and archive merge support. Preserve the existing four car entries and their DBC continuations; add regular mounts without vehicle/seat records, using cloned native ground/flying spell templates and one stock mount icon.

**Tech Stack:** Python 3 standard library, StormLib, WDBC continuation files, AzerothCore module SQL, unittest.

**Spec:** User-approved chat design: omit the three v272 models; import every distinct v264 model from all 12 supplied folders, add them alongside the existing `PATCH-X.MPQ`, and create synchronized client/server records without overwrites.

## Global Constraints

- Target client/server: WoW 3.3.5a / AzerothCore WotLK.
- Import only MD20 model version 264; reject the three v272 models.
- Preserve the existing four car records and all existing Patch-X entries.
- Use unique IDs and asset paths; fail closed on byte-conflicting archive collisions.
- Do not replace baseline DBC files; add WXL continuation files and matching `*_dbc` SQL overlays.
- Use the existing StormLib and WDBC helpers; add no dependencies.
- SQL updates belong under `modules/mod-custom-server/data/sql/db-world/updates/` and must be idempotent.
- Do not configure or build the server unless separately requested; perform generator and static validation only.

## Files and Responsibilities

- Modify `tools/cars_mount_pack.py`: shared archive/DBC helpers, mount discovery, package merge, continuation generation, SQL rendering, CLI.
- Modify `tools/test_cars_mount_pack.py`: failing-first tests for discovery, v272 rejection, deterministic IDs, and archive collision behavior.
- Create `modules/mod-custom-server/data/sql/db-world/updates/u_custom_server_2026_09_09_01_mounts.sql`: generated idempotent item and DBC-overlay records for the 89 mounts.
- Generate ignored artifacts under `var/mount-build/`: source manifest, archive summary, and Patch-X backup.
- Replace ignored `3.3.5a - Dev/Data/PATCH-X.MPQ` only after the merged archive passes entry and collision checks.

### Task 1: Add failing tests for the mount contract

**Files:**
- Modify: `tools/test_cars_mount_pack.py`
- Test: `tools/test_cars_mount_pack.py`

**Interfaces:**
- `discover_mounts(roots) -> tuple[Mount, ...]`
- `rejected_models(roots) -> tuple[RejectedModel, ...]`
- `merge_archive_entries(existing, additions) -> dict[str, bytes]`
- `mount_ids(mounts) -> dict[str, tuple[int, ...]]`

- [ ] Add a test that a temporary source tree containing one v264 MD20 and one v272 MD20 returns only the v264 model and reports the v272 model through `rejected_models()`.
- [ ] Add a test that repeated discovery over the same roots produces the same ordered slugs and IDs.
- [ ] Add a test that archive merge retains an existing entry byte-for-byte and raises on a same-path byte conflict.
- [ ] Run `py -m unittest tools/test_cars_mount_pack.py -v` and confirm the new tests fail because the mount interfaces do not exist yet.

### Task 2: Implement deterministic source discovery and asset packaging

**Files:**
- Modify: `tools/cars_mount_pack.py`

**Interfaces:**
- `Mount` stores `slug`, `display_name`, `source_root`, `source_model`, `model_version`, and allocated IDs.
- `discover_mounts()` scans the twelve supplied source roots, sorts case-insensitively by package and relative model path, and returns only v264 models.
- `collect_mount_entries(mount)` copies the model, sibling `.skin`/`.anim`/`.phys` files, and `.blp` files into a deterministic client-relative path while preserving internal relative paths required by the model.
- `merge_archive_entries()` returns the union and raises for differing bytes at a case-insensitive path.

- [ ] Implement the MD20 header/version reader using `struct.unpack_from`, with explicit short-file and bad-magic errors.
- [ ] Implement source-root normalization for nested `[MK8]...`, `WotLK`, and `Creature` directories without mutating source files.
- [ ] Implement stable slug/name derivation from relative model paths and fail on duplicate slugs or duplicate display names.
- [ ] Implement archive-entry collision checks before any output file is replaced.
- [ ] Run the focused tests and confirm they pass.

### Task 3: Generate WotLK DBC continuations and SQL

**Files:**
- Modify: `tools/cars_mount_pack.py`
- Create: `modules/mod-custom-server/data/sql/db-world/updates/u_custom_server_2026_09_09_01_mounts.sql`

**Interfaces:**
- `build_mount_records(mounts, baseline) -> tuple[MountRecord, ...]`
- `build_mount_dbc_entries(records) -> dict[str, bytes]`
- `render_mount_sql(records) -> str`

- [ ] Allocate collision-scanned ranges: spells `201000+`, items `901000+`, item displays `135000+`, creature displays `94300+`, and model data `5000+`; use exactly one row per imported model.
- [ ] Clone valid native ground/flying mount spell/item templates from the existing WotLK baseline, replace only IDs, display IDs, names, descriptions, and the mount icon reference, and keep all other spell behavior stock-derived.
- [ ] Create `CreatureModelData` rows pointing to the packaged v264 model paths and conservative bounds; create `CreatureDisplayInfo` rows using each model ID and empty texture variations when the M2 provides its own textures.
- [ ] Create additive `Spell.dbc1-mounts`, `Item.dbc1-mounts`, `ItemDisplayInfo.dbc1-mounts`, `CreatureDisplayInfo.dbc1-mounts`, and `CreatureModelData.dbc1-mounts` entries, preserving the existing car continuation files and extending `wxl-dbc.manifest`.
- [ ] Render idempotent SQL with matching `DELETE` statements for the five DBC overlay tables and `REPLACE INTO` for `item_template`, which AzerothCore's SQL checker explicitly protects from delete-before-insert updates.
- [ ] Run SQL formatting/lint checks required by `.agents/docs/sql-guidelines.md` without modifying immutable SQL trees.

### Task 4: Merge and write Patch-X plus audit artifacts

**Files:**
- Modify: `tools/cars_mount_pack.py`
- Generate ignored: `3.3.5a - Dev/Data/PATCH-X.MPQ`, `var/mount-build/`

- [ ] Add CLI options for source roots, baseline DBC directory, existing Patch-X path, StormLib path, SQL output, and report output while preserving existing car defaults.
- [ ] Read and preserve every existing Patch-X entry, merge new model assets and DBC continuations, and keep `(listfile)` updated without dropping existing paths.
- [ ] Write the previous Patch-X to `var/mount-build/PATCH-X-before-mounts.MPQ` before replacing it.
- [ ] Reopen the resulting archive with StormLib and verify every generated entry, all 89 model paths, no v272 model, no stock-path overwrite, and manifest coverage.
- [ ] Emit a JSON manifest with source provenance, rejected models, allocated IDs, asset paths, and archive hash.

### Task 5: Verify the completed artifact

- [ ] Run `py -m unittest tools/test_cars_mount_pack.py -v`.
- [ ] Run the generator against the eleven supplied roots and existing Patch-X.
- [ ] Run `python apps/codestyle/codestyle-sql.py` and record its result.
- [ ] Re-scan the generated archive, continuation headers/row counts, SQL IDs, and source hashes.
- [ ] Report that server build, database import, and live WoW learn/mount/riding smoke were not performed unless explicitly requested.
