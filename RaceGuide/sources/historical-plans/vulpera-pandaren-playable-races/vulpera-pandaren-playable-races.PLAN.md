# Vulpera Horde and Pandaren Alliance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task.
> Steps use checkbox syntax for tracking.

**Goal:** Add playable Vulpera Horde ID 20 and Pandaren Alliance ID 18 while
preserving Sethrak ID 15, disabling Horde Pandaren ID 26, and keeping
Patch-B/client/server behavior additive.

**Architecture:** Reconcile the complete custom-race enum with the authored
registry, replace PlayerBots' numeric cutoff with an explicit allowlist, add
one idempotent world migration, generate remapped WDBC continuations and
staged MPQ additions with existing StormLib/WXL helpers, then merge only
required Patch-B Glue entries.

**Tech Stack:** C++20, AzerothCore CMake/GoogleTest, MySQL SQL updates,
Python unittest, WDBC binary rows, tools/cars_mount_pack.py helpers, WXL
continuations, Lua/XML Glue.

**Spec:** .agents/plans/vulpera-pandaren-playable-races/vulpera-pandaren-playable-races.REQUIREMENTS.md

## Global Constraints

- Preserve authored IDs: Sethrak 15, Pandaren Alliance 18, Vulpera 20, Horde Pandaren 26.
- Preserve existing character rows; never remap or delete characters.
- Do not edit applied race migrations.
- Do not add Horde Pandaren, Ogre, Forsaken, Kul Tiran, Monk class 10, or new racial abilities.
- Patch-B remains authoritative; never copy donor Glue/interface directories wholesale.
- Original MPQs and baseline DBCs remain unchanged; stage output separately.
- Reuse RaceMgr, ObjectMgr, Player::Create(), existing WXL loader, and existing pack helpers.
- No configure/build/deploy/live-client claim without explicit user authorization.

## File map

- Create tools/test_playable_race_contract.py: source, registry, SQL, and Glue contract checks.
- Modify src/server/shared/SharedDefines.h: complete authoritative custom-race enum.
- Modify modules/mod-playerbots/src/Bot/Factory/RandomPlayerbotFactory.cpp: explicit bot policy and name mapping.
- Create: modules/mod-custom-server/data/sql/db-world/updates/
  u_custom_server_2026_09_10_01_race_vulpera_pandaren.sql: scope correction.
- Create tools/playable_race_pack.py: WDBC remapping, manifests, staged archive merge.
- Create tools/test_playable_race_pack.py: WDBC, manifest, archive, asset, and Glue tests.
- Stage external client output under G:\Ascension\Ascension\resources\ascension-live\Data\Staging\.

No changes to RaceMgr.cpp, ObjectMgr.cpp, CharacterHandler.cpp, or the dirty
mod-wxl-dbc implementation unless a focused test proves the existing seam
cannot support the target rows.

## Fixed interfaces

~~~cpp
namespace
{
bool IsSupportedRandomBotRace(uint8 race);
}
~~~

~~~python
def remap_race_rows(table_name: str, rows: list[list[int]], source_race: int, target_race: int) -> list[list[int]]: ...
def remap_race_masks(value: int, source_mask: int, target_mask: int) -> int: ...
def build_race_pack(dbc_root: Path, model_root: Path, patch_b_root: Path, output_root: Path) -> PackReport: ...
~~~

PackReport contains continuations, asset_paths, manifest_entries, collisions, and missing_requirements.

## Task 1: Write failing race-contract tests

**Files:** Create tools/test_playable_race_contract.py. Read the registry,
SharedDefines.h, and RandomPlayerbotFactory.cpp.

- [ ] Parse enum assignments and assert this exact custom map:

~~~python
{
    "RACE_SETHRAK": 15,
    "RACE_EREDAR": 16,
    "RACE_NIGHTBORNE": 17,
    "RACE_PANDAREN_ALLIANCE": 18,
    "RACE_VOIDELF": 19,
    "RACE_VULPERA": 20,
    "RACE_LIGHTFORGEDDRAENEI": 21,
    "RACE_ZANDALARITROLL": 22,
    "RACE_DARKIRONDWARF": 23,
    "RACE_BROKEN_ALLIANCE": 24,
    "RACE_FORSAKEN": 25,
    "RACE_PANDAREN_HORDE": 26,
    "RACE_BROKEN_HORDE": 27,
    "RACE_DRACTHYR": 28,
}
~~~

- [ ] Load race_registry.json and assert target entries 18/alliance and
  20/horde, deferred entry 26/horde, and classes 1,2,3,4,5,6,7,8,9,11.
- [ ] Assert the current numeric PlayerBots cutoff is absent after the helper exists.
- [ ] Run red: python tools/test_playable_race_contract.py -v. It must fail on current enum and PlayerBots source.
- [ ] Commit only the new test with message test: define playable race contract.

## Task 2: Reconcile enum and PlayerBots policy

**Files:** Modify SharedDefines.h and RandomPlayerbotFactory.cpp. Test the contract file.

- [ ] Extend the red test to require explicit cases for supported IDs 1-14,
  18, and 20, and reject ID 15, ID 26, and all deferred IDs.
- [ ] Replace custom enum values 15-28 with the Task 1 map. Remove stale
  RACE_OGRE; no authoritative race uses that value.
- [ ] Add this anonymous-namespace helper:

~~~cpp
bool IsSupportedRandomBotRace(uint8 race)
{
    switch (race)
    {
        case RACE_HUMAN:
        case RACE_ORC:
        case RACE_DWARF:
        case RACE_NIGHTELF:
        case RACE_UNDEAD_PLAYER:
        case RACE_TAUREN:
        case RACE_GNOME:
        case RACE_TROLL:
        case RACE_GOBLIN:
        case RACE_BLOODELF:
        case RACE_DRAENEI:
        case RACE_WORGEN:
        case RACE_HIGHELF:
        case RACE_BROKEN_PLAYER:
        case RACE_PANDAREN_ALLIANCE:
        case RACE_VULPERA:
            return true;
        default:
            return false;
    }
}
~~~

- [ ] Replace the numeric cutoff in IsValidRaceClassCombination with the
  helper; keep expansion, disabled-mask, faction, appearance, and PlayerInfo
  checks.
- [ ] Remove the Ogre name case. Add Sethrak, Dracthyr, and all reconciled
  custom enum names to the generic-name group; retain target generic names.
- [ ] Run python tools/test_playable_race_contract.py -v and python
  apps/codestyle/codestyle-cpp.py. Expected: contract passes; no new C++ lint
  errors.
- [ ] Commit the two source files with message feat: align playable race IDs and bot policy.

## Task 3: Add corrective world migration

**Files:** Create the named module SQL update. Modify the contract test.

- [ ] Add red assertions that migration exists, reports counts for IDs
  15/18/20/26, uses idempotent flags for IDs 18/20/26, and contains no
  character-table mutation.
- [ ] Run red: python tools/test_playable_race_contract.py SqlMigrationContractTest -v.
- [ ] Create the migration with this operation order:

~~~sql
SELECT race, COUNT(*) AS character_count
FROM acore_characters.characters
WHERE race IN (15, 18, 20, 26)
GROUP BY race
ORDER BY race;

SELECT ID, Flags, FactionID, Alliance, MaleDisplayId, FemaleDisplayId
FROM chrraces_dbc
WHERE ID IN (15, 18, 20, 26)
ORDER BY ID;

UPDATE chrraces_dbc
SET Flags = Flags - (Flags & 1)
WHERE ID IN (18, 20) AND (Flags & 1) = 1;

UPDATE chrraces_dbc
SET Flags = Flags | 1
WHERE ID = 26 AND (Flags & 1) = 0;
~~~

- [ ] Append validation reports for playercreateinfo, playercreateinfo_item,
  playercreateinfo_action, player_race_stats, charstartoutfit_dbc using
  RaceID/ClassID/SexID, playercreateinfo_spell_custom, and
  skillraceclassinfo_dbc. Report missing rows; do not mutate them.
- [ ] Run the SQL contract and python apps/codestyle/codestyle-sql.py.
- [ ] Commit migration and contract test with message feat: scope Vulpera and Alliance Pandaren.
- [ ] Do not import/deploy this migration without separate authorization.

## Task 4: Build tested additive DBC/model packer

**Files:** Create tools/playable_race_pack.py and
tools/test_playable_race_pack.py. Reuse tools/cars_mount_pack.py Storm,
Wdbc, build_wdbc, merge_archive_entries, merge_wxl_manifest, and safe_relative.

- [ ] Write red tests for target-row remapping, race-field-only changes,
  target-mask replacement that preserves unrelated bits, duplicate-ID
  rejection, .mdx rejection, and .m2 acceptance.
- [ ] Run red: python tools/test_playable_race_pack.py -v.
- [ ] Implement remap_race_rows, remap_race_masks, and build_race_pack without duplicating StormLib/WDBC framing.
- [ ] Use field maps:
  - RACE_ID_FIELDS: ChrRaces 0, CharBaseInfo 0, CharStartOutfit 1,
    CharSections 0, CharHairGeosets 1, CharHairTextures 1,
    BarberShopStyle 37, CharacterFacialHairStyles 0, NameGen 2,
    CreatureDisplayInfoExtra 1.
  - RACE_MASK_FIELDS: SkillLineAbility 3, SkillRaceClassInfo 2.
- [ ] Preserve dependent model/display/item/faction rows by reference; preserve unrelated rows and existing faction IDs.
- [ ] Require male/female model, skin, and animation sets under
  Character\vulpera and Character\Pandaren. Record SHA-256 and file counts.
  Read donor DBCs from
  G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\DBFilesClient.
- [ ] Emit deterministic DBFilesClient/<Table>.dbc1-vulpera-pandaren files
  and wxl-dbc.manifest. Keep ID 26 absent from playable UI rows.
- [ ] Merge only into a staged Patch-B copy. Accept identical
  case-insensitive bytes; reject different bytes. Never write original
  archives.
- [ ] Run python tools/test_playable_race_pack.py -v; expected PASS.
- [ ] Commit packer and tests with message feat: add additive playable race packer.

## Task 5: Merge Patch-B Glue and icon contract

**External files:** Patch-B CharacterCreate.lua, CharacterCreate.xml,
GlueLocalization.lua, GlueParent.lua, SharedConstants.lua; staged
CharacterCreate icons; tools/test_playable_race_pack.py.

- [ ] Add red Glue tests requiring MAX_RACES = 13, ordinal buttons 12 and
  13, both hard-coded loops changed to MAX_RACES, target race strings, and no
  Horde Pandaren Glue path.
- [ ] Run red: python tools/test_playable_race_pack.py GlueContractTest -v.
- [ ] Add two XML buttons with the existing template and 30-pixel vertical
  anchor pattern. Ordinals 12/13 remain separate from actual IDs 18/20.
- [ ] Set MAX_RACES = 13 and update the two loops at the race highlight/stop functions from 10 to MAX_RACES.
- [ ] Add RACE_INFO_PANDAREN, RACE_INFO_PANDAREN_FEMALE,
  RACE_INFO_VULPERA, and RACE_INFO_VULPERA_FEMALE in GlueLocalization.lua.
  Add only target icon-coordinate keys and faction lighting/ambience aliases;
  add no abilities.
- [ ] Require explicit target icon assets. If none are supplied, stop with
  missing_requirements rather than substitute another race portrait.
- [ ] Run GlueContractTest against the staged tree; expected PASS only with
  both target icons, both genders, 13 buttons, and no Horde Pandaren path.
- [ ] Preserve original Patch-B and record only staged output path/hash; do
  not add external binaries to the repository unless explicitly requested.

## Task 6: Static validation and review

**Files:** Both Python tests and all files from Tasks 2-5.

- [ ] Run python tools/test_playable_race_contract.py -v and python tools/test_playable_race_pack.py -v.
- [ ] Verify no stale numeric PlayerBots cutoff, no RACE_OGRE, no Horde
  Pandaren Glue entry, no duplicate authoritative Glue file, and no .mdx
  target model path.
- [ ] Run python apps/codestyle/codestyle-cpp.py and python
  apps/codestyle/codestyle-sql.py; report unrelated pre-existing failures
  separately.
- [ ] Run git diff --check and inspect status. Preserve all pre-existing dirty files.
- [ ] Review every spec requirement and keep static/runtime boundaries explicit.
- [ ] Commit only scoped repository changes if execution mode authorizes commits.

## Task 7: Optional build, deploy, and live gate

Not performed by default: repository rules prohibit configure/build without
explicit authorization and deployment changes shared runtime state.

When explicitly authorized:

- Configure an out-of-source build with -DBUILD_TESTING=ON, build worldserver/modules, and run focused GoogleTests.
- Run ac-db-import for the module migration, recreate only ac-worldserver with
  --no-deps --force-recreate, and inspect readiness, active config, update
  history, and logs without deleting volumes.
- Verify live flags, target class/start/outfit counts, and zero changes to ID15 characters.
- Install staged client additions separately and smoke-test both races, both
  genders, every class 1-9,11, creation, login, relog, restart, equipment,
  jump, mount, barber, character select, and random PlayerBot creation.

## Handoff

Execute Tasks 1-6 in order. Task 7 requires separate explicit authorization
because it changes build/runtime/client state.
