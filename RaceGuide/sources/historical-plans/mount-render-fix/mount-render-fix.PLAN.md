# Additive Mount Render Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make all 89 imported WotLK mounts resolve through AzerothCore's normal creature-entry mount path, use sane icons, and package the model dependencies required by the client.

**Architecture:** Extend the existing generator rather than patching callers or hand-editing generated output. Each mount gets a unique creature entry plus `creature_template_model` mapping to its unique `CreatureDisplayInfo`; its spell's `EffectMiscValue_1` points to that creature entry. Explicit source icons are used when available, otherwise a stock riding-mount icon is copied; arbitrary model-texture fallback is removed.

**Tech Stack:** Python 3 standard library, StormLib, WDBC, AzerothCore SQL, unittest.

**Spec:** Current-task diagnosis and user approval to proceed with the proposed mount-link, icon, and asset fixes.

## Global Constraints

- Target WoW client/server: 3.3.5a / AzerothCore WotLK.
- Import only MD20 model version 264 and preserve the four working car mounts.
- Keep all client paths and generated IDs additive; fail on conflicting archive bytes.
- Use unique mount creature entries `3460608..3460696`, verified unused in the active world database before regeneration.
- Do not configure or build the server; run focused Python, archive, SQL, and database read-only verification.
- Preserve unrelated dirty files and persistent Docker volumes.

### Task 1: Add regression tests first

**Files:**
- Modify: `tools/test_cars_mount_pack.py`
- Test: `tools/test_cars_mount_pack.py`

- [x] Assert a generated mount spell stores a unique creature entry in `EffectMiscValue_1`, not its `CreatureDisplayInfo` ID.
- [x] Assert generated SQL includes matching `creature_template_model` and `creature_template` rows.
- [x] Assert a source-root texture referenced as `Creature\\Example\\body.blp` is remapped into the mount namespace.
- [x] Assert an absent source icon uses the explicit default icon bytes and never the first model texture.
- [x] Run the new focused tests and observe the expected failures before implementation.

### Task 2: Implement the minimum generator changes

**Files:**
- Modify: `tools/cars_mount_pack.py`

- [x] Add deterministic creature-entry allocation beginning at `3460608` and carry `creature_id` through `MountRecord` and the report.
- [x] Set both client and server spell `EffectMiscValue_1` to `creature_id`.
- [x] Render idempotent `creature_template_model` and `creature_template` rows using the generated display ID and a stock-derived non-vehicle creature template.
- [x] Match source-root texture basenames, require/alias the model's canonical `00.skin`, and keep all existing sibling animation/physics assets.
- [x] Remove arbitrary first-texture icon fallback; use matching source icons or the stock `Ability_Mount_RidingHorse.blp` bytes passed by `main()`.

### Task 3: Regenerate and verify artifacts

**Files:**
- Regenerate: `modules/mod-custom-server/data/sql/db-world/updates/u_custom_server_2026_09_09_01_mounts.sql`
- Regenerate: `3.3.5a - Dev/Data/PATCH-X.MPQ`
- Generate ignored report/backup files under `var/mount-build/`

- [x] Run focused Python tests and the SQL style checker.
- [x] Run `tools/cars_mount_pack.py` against the existing baseline, source folders, and `PATCH-X.MPQ`.
- [x] Reopen the archive and verify 89 creature-entry joins, 89 model paths, 89 icon paths, no v272 models, and no missing required canonical skins or source-root texture references.
- [x] Query the active world database to verify all 89 mount spells join to their creature templates and model mappings while car joins remain intact.
- [x] Report the remaining live WoW client smoke-test boundary if no in-game cast is performed.
