# Procedural Items Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver persistent procedural AzerothCore items that remain client-safe and visually accurate while supporting runtime generation.

**Architecture:** A deterministic pure-C++ generator feeds a permanent prepared-ID allocator and verified appearance catalog. A transactional persistence service writes canonical templates/provenance, then a narrow runtime registry adapter exposes them to the running worldserver.

**Tech Stack:** AzerothCore WotLK current master conventions, C++20, MySQL/MariaDB world database, Python 3 client-manifest tooling, WotLK 3.3.5a DBC client patch.

**Spec:** `docs/superpowers/specs/2026-08-28-procedural-items-design.md`

## Global Constraints

- Generated entries are never recycled.
- Every generated entry must exist in the prepared client `Item.dbc` pool.
- Display IDs are allow-listed and verified; unknown assets fail generation.
- Generator behavior is deterministic by generation version + seed + request.
- Delivery happens only after canonical persistence and successful runtime registration.
- Runtime registry code must not mutate `ObjectMgr` through `const_cast` and must not reload all item templates per drop.

---

### Task 1: Pure generator and safety model

**Files:**
- `src/core/Types.h`
- `src/core/DeterministicRng.h`
- `src/core/IdPool.{h,cpp}`
- `src/core/AppearanceCatalog.{h,cpp}`
- `src/core/ItemGenerator.{h,cpp}`
- `tests/test_core.cpp`

**Interfaces:** `IdPool::allocate`, `AppearanceCatalog::choose`, `ItemGenerator::generate`.

- [x] Write tests proving deterministic RNG, first-unused allocation, pool exhaustion, incompatible-display rejection, and deterministic generated drafts.
- [x] Run the test compile and confirm it fails before implementation because generator headers do not exist.
- [x] Implement the minimum pure-C++ core needed for those behaviors.
- [x] Compile with C++20 warnings enabled and run all core tests.

### Task 2: Client pool tooling

**Files:**
- `client/item_pool_ranges.csv`
- `client/README.md`
- `tools/validate_client_pool.py`
- `tools/generate_client_pool_manifest.py`

**Interfaces:** range CSV expands to `{entry,pool_key,item_class,subclass,inventory_type}` rows for the client DBC pipeline.

- [x] Define starter non-overlapping development ranges.
- [x] Reject duplicate pool names, reversed ranges, overlaps, and entries above unsigned MEDIUMINT.
- [x] Expand validated ranges into one immutable reservation row per entry.
- [x] Document how server static identity must mirror the patched client's `Item.dbc` rows.

### Task 3: Database contract and AzerothCore loader

**Files:**
- `data/sql/db-world/base/mod_procedural_items.sql`
- `conf/mod_procedural_items.conf.dist`
- `src/acore/ProceduralItemsWorldScript.cpp`
- `src/mod_procedural_items_loader.cpp`

**Interfaces:** world DB tables `mod_procedural_id_range`, `mod_procedural_display_pool`, `mod_procedural_item`; loader `Addmod_procedural_itemsScripts()`.

- [x] Add append-only ID range and provenance schema.
- [x] Leave display catalog empty so no DBC-backed ID is guessed.
- [x] Add module startup/config hooks using current AzerothCore module conventions.
- [x] Log clearly that live runtime template registration remains disabled in scaffold v0.1.

### Task 4: Safe runtime ItemTemplate registry

**Files:**
- AzerothCore core: narrowly scoped `ObjectMgr` API and tests.
- Module: new `src/acore/AcoreRuntimeItemRegistry.{h,cpp}` implementing `IRuntimeItemRegistry`.

**Interfaces:** `RuntimeRegisterStatus registerTemplate(uint32 entry, GeneratedItemDraft const&, std::string& error)` after the full-template mapper exists.

- [ ] Write core tests that register one template, retrieve it by entry, reject conflicting duplicate entry, and retain valid lookups for existing items.
- [ ] Implement a world-thread-only one-template registration API that updates every required item-template lookup structure atomically.
- [ ] Run core tests plus a server startup smoke test with PCH disabled.
- [ ] Implement the module adapter with no direct access to private/const-cast core stores.

### Task 5: Transactional full-template persistence

**Files:**
- New `src/acore/AcoreGeneratedItemPersistence.{h,cpp}`.
- New `src/acore/ItemTemplateMapper.{h,cpp}`.
- New persistence/integration tests.

**Interfaces:** map a validated draft + pool identity to every required `item_template` column; persist canonical row + provenance before runtime registration.

- [ ] Add tests for class/subclass/inventory identity, stat slots, quality/levels, display ID, defaults, and SQL rollback on failure.
- [ ] Implement complete current-schema `item_template` mapping with explicit values rather than relying on accidental DB defaults.
- [ ] Implement permanent-used detection against both `item_template` and `mod_procedural_item`.
- [ ] Execute persistence + runtime registration as one delivery gate; never create an item instance if either fails.

### Task 6: GM command and loot integration

**Files:**
- New command script and loot source service under `src/acore/`.
- New config keys and integration tests.

**Interfaces:** `.pitem generate <role> <level> <quality> <poolKey>` and one shared generation service usable by future creature, quest, chest, vendor, and crafting sources.

- [ ] Select a collision-safe RBAC permission strategy and test unauthorized/authorized invocation.
- [ ] Implement command parsing and structured validation errors.
- [ ] Route command generation through the same transactional service used by loot.
- [ ] Add a configurable creature/world drop hook only after command-path persistence is proven stable.
