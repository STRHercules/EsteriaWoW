# Unique car mounts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract the four supplied car MPQs, create four independent WotLK car mounts, package them as `PATCH-X.MPQ`, deploy matching world records, and restart the realm safely.

**Architecture:** Use one small Python asset tool with StormLib ctypes for extraction, DBC continuation generation, M2 path isolation, MPQ creation, and assert-based archive checks. Keep existing server IDs for the four car definitions, add independent Vehicle/VehicleSeat IDs, and ship client-only DBC deltas through the installed WXL extension. Build a car-only `PATCH-X.MPQ` so the existing Battlemon `patch-z.mpq` folder remains untouched. Add one corrective module SQL migration, then rebuild/import/recreate the existing Docker services.

**Tech Stack:** PowerShell, Python standard library, StormLib, WDBC, MPQ, MySQL 8.4, Docker Compose, AzerothCore module SQL.

**Spec:** `.agents/plans/car-mounts/car-mounts.REQUIREMENTS.md`

## Global Constraints

- Source MPQ files remain unchanged.
- `3.3.5a - Dev\Data\patch-z.mpq` is preserved; the requested archive is `PATCH-X.MPQ`.
- Existing dirty repository files remain untouched except the new car migration and the temporary/ignored plan artifacts.
- `data/sql/base/`, `data/sql/archive/`, and merged `data/sql/updates/db_*` remain immutable.
- Never delete persistent Docker volumes; never use `docker compose down -v`.
- Use only collision-scanned IDs and WotLK-compatible source assets.

---

### Task 1: Build the extraction and packaging tool

**Files:**
- Create: `tools/cars_mount_pack.py`

**Interfaces:**
- Consumes: four source MPQs, the existing Battlemon folder patch, runtime baseline DBCs copied from `ac-worldserver`, and the existing car SQL rows.
- Produces: extracted source directories, per-car WXL continuation files, isolated car assets, `PATCH-X.MPQ`, and a machine-readable verification summary.

- [ ] **Step 1: Implement StormLib archive enumeration/read/write using the installed x64 DLL.** Use Unicode for `SFileOpenArchive`, ANSI archive keys for `SFileOpenFileEx`, and assert every read size equals `SFileGetFileSize`.
- [ ] **Step 2: Extract every listed entry from each source archive into its matching `Extracted\Patch-*` directory, preserving archive-relative paths and source filenames.
- [ ] **Step 3: Parse the source M2 texture arrays and rewrite only the model name and GoblinHotrod texture paths to the car-specific directory, padding replacements in place so offsets remain valid. Preserve all other animation, skin, and effect bytes.
- [ ] **Step 4: Generate WDBC continuation files for Spell, Item, ItemDisplayInfo, SpellIcon, CreatureDisplayInfo, CreatureModelData, Vehicle, and VehicleSeat with the approved IDs and exact source/server-compatible layouts. Add an icon row per car and unique icon BLP paths.
- [ ] **Step 5: Build a car-only real MPQ containing the car assets, all continuation files under `DBFilesClient/`, and a root `wxl-dbc.manifest` listing every continuation path; leave the existing Battlemon folder patch untouched.
- [ ] **Step 6: Add assert-based checks for source extraction counts, WDBC headers/row IDs, unique asset paths, MPQ signature, manifest coverage, representative file reads, and absence of the original chopper/icon claim paths.
- [ ] **Step 7: Run the tool once and inspect its summary before changing server SQL.

### Task 2: Add the corrective server migration

**Files:**
- Create: `modules/mod-custom-server/data/sql/db-world/updates/u_custom_server_2026_09_09_00_cars_unique.sql`

**Interfaces:**
- Consumes: IDs and full Vehicle/VehicleSeat row values emitted by Task 1.
- Produces: idempotent world SQL that moves each car to its independent vehicle/seat rows and corrects its model path.

- [ ] **Step 1: Write `DELETE` plus `INSERT` blocks for `vehicle_dbc` IDs `900301..900304` and `vehicleseat_dbc` IDs `900401..900404`, cloning only the validated stock chopper movement/seat behavior while changing the primary keys.
- [ ] **Step 2: Write one exact `UPDATE creature_template` block for entries `3460604..3460607` assigning Vehicle IDs `900301..900304`.
- [ ] **Step 3: Write one exact `DELETE` plus `INSERT` block for `creaturemodeldata_dbc` IDs `4892..4895` with `.m2` model paths matching the package.
- [ ] **Step 4: Run the repository SQL linter and a live collision query before importing.

### Task 3: Deploy and verify

**Files:**
- Modify: no existing source files beyond the new SQL migration; ignored runtime/image state only.

**Interfaces:**
- Consumes: `PATCH-X.MPQ`, the Task 1 verification summary, and the Task 2 migration.
- Produces: imported live rows, a recreated ready worldserver, and verification evidence.

- [ ] **Step 1: Build `ac-db-import` and `ac-worldserver` from the current checkout.
- [ ] **Step 2: Recreate/run `ac-db-import` and require exit code 0.
- [ ] **Step 3: Recreate only `ac-worldserver` without volume deletion.
- [ ] **Step 4: Query migration state, creature Vehicle IDs, Vehicle/VehicleSeat rows, model paths, and existing spell/item mappings.
- [ ] **Step 5: Check `docker compose ps -a`, worldserver readiness, health, and restart count.
- [ ] **Step 6: Report static verification and explicitly leave live WoW learning/riding/relog smoke as the remaining test boundary.

## Self-review

- Requirements coverage: extraction, additive IDs, unique assets, WXL manifest, Battlemon preservation, SQL correction, importer, restart, and verification are covered by Tasks 1–3.
- Placeholder scan: no TBD/TODO steps are required.
- Type/ID consistency: Task 1 emits `200101..200104`, `900137..900140`, `3460604..3460607`, `94229..94232`, `4892..4895`, `134239..134242`, `900301..900304`, and `900401..900404`; Tasks 2–3 consume those exact ranges.
