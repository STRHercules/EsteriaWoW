# Custom Race Initialization and Broken Racials Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Goblin, Worgen, High Elf, and Broken characters receive valid starting skills and starting-zone quest access, while replacing Broken's copied racials with the requested abilities.

**Architecture:** Keep race eligibility in world SQL and keep the existing Worgen/Teldrassil spawn profile. Put reusable racial calculations in a small game-layer helper, use the existing Worgoblin script registration for repair and Echo, and apply Broken's mana-drain reduction once in the shared spell-effect implementations.

**Tech Stack:** AzerothCore C++, GoogleTest, MySQL world SQL, DBC-backed spell data.

**Spec:** `docs/superpowers/specs/2026-09-06-custom-race-initialization-and-broken-racials-design.md`

## Global Constraints

- Preserve the existing dirty worktree and stage only files belonging to this feature.
- Do not configure or build unless explicitly requested.
- Never edit SQL outside `data/sql/updates/pending_db_*/`.
- Use existing spell IDs 110001 through 110004; add no dependency or new subsystem.
- Keep Worgen at the Night Elf/Teldrassil starting profile, grant Night Elf starting quests, and retain Common without Darnassian.
- Keep SQL idempotent; every new `INSERT` is preceded by a matching `DELETE`.
- Run C++ and SQL linters plus `git diff --check` before completion.

## File Map

- Create `src/server/game/Entities/Player/BrokenRacialEffects.h` and `.cpp` for the three tested numeric racial calculations.
- Modify `modules/mod-worgoblin-high-elf/src/Worgoblin.cpp` for Salvager's repair hook and Echo's periodic heal script registration.
- Modify `src/server/game/Spells/SpellEffects.cpp` for the shared Broken mana-drain calculation entry point.
- Create `src/test/server/game/Modules/BrokenRacialsTest.cpp` for the red/green numeric regression tests.
- Create `data/sql/updates/pending_db_world/rev_1788720000000000000.sql` for race masks, quest masks, spell definitions, spell bindings, and Broken action-bar grants.

### Task 1: Add the failing racial calculation tests

**Files:**
- Create: `src/test/server/game/Modules/BrokenRacialsTest.cpp`
- Test target: existing `unit_tests` target; `src/test/CMakeLists.txt` already collects sources recursively.

**Interfaces:**
- Consumes the intended functions in `Acore::BrokenRacialEffects`:
  `ApplySalvagerRepairDiscount(float)`,
  `ReduceManaDrain(int32)`, and
  `EchoHealPerTick(uint32)`.
- Produces the exact numeric contract used by Tasks 2 and 3.

- [ ] **Step 1: Write the failing test**

```cpp
#include "SharedDefines.h"
#include "gtest/gtest.h"

namespace Acore::BrokenRacialEffects
{
float ApplySalvagerRepairDiscount(float discount);
int32 ReduceManaDrain(int32 amount);
int32 EchoHealPerTick(uint32 maxHealth);
}

TEST(BrokenRacialEffects, AppliesSalvagerRepairDiscount)
{
    EXPECT_FLOAT_EQ(Acore::BrokenRacialEffects::ApplySalvagerRepairDiscount(1.0f), 0.9f);
}

TEST(BrokenRacialEffects, ReducesManaDrainByTenPercent)
{
    EXPECT_EQ(Acore::BrokenRacialEffects::ReduceManaDrain(1000), 900);
    EXPECT_EQ(Acore::BrokenRacialEffects::ReduceManaDrain(9), 8);
}

TEST(BrokenRacialEffects, SplitsEchoIntoFiveThreePercentTicks)
{
    EXPECT_EQ(Acore::BrokenRacialEffects::EchoHealPerTick(100000), 3000);
}
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run from a configured test build directory only if one already exists:

```powershell
rtk test --build-config Debug --target unit_tests --gtest_filter=BrokenRacialEffects.*
```

Expected: the test cannot link because the three production functions do not exist yet. Do not configure a new build directory.

- [ ] **Step 3: Commit the failing test**

```powershell
rtk git add -- src/test/server/game/Modules/BrokenRacialsTest.cpp
rtk git commit -m "test: define Broken racial contracts"
```

### Task 2: Implement reusable racial calculations and shared mana reduction

**Files:**
- Create: `src/server/game/Entities/Player/BrokenRacialEffects.h`
- Create: `src/server/game/Entities/Player/BrokenRacialEffects.cpp`
- Modify: `src/server/game/Spells/SpellEffects.cpp` at `Spell::EffectPowerDrain` and `Spell::EffectPowerBurn`.
- Test: `src/test/server/game/Modules/BrokenRacialsTest.cpp`

**Interfaces:**
- `ApplySalvagerRepairDiscount(float discount)` returns `discount * 0.9f`.
- `ReduceManaDrain(int32 amount)` returns `CalculatePct(amount, 90)`.
- `EchoHealPerTick(uint32 maxHealth)` returns `CalculatePct(maxHealth, 3)`.

- [ ] **Step 1: Add the minimal production helper**

```cpp
#pragma once

#include "Define.h"

namespace Acore::BrokenRacialEffects
{
float ApplySalvagerRepairDiscount(float discount);
int32 ReduceManaDrain(int32 amount);
int32 EchoHealPerTick(uint32 maxHealth);
}
```

Implement the three functions in the `.cpp` with the existing `CalculatePct` helper from `Utilities/Util.h`; do not add rounding policy beyond the core's established integer conversion.

- [ ] **Step 2: Apply the helper in both shared mana-effect paths**

After the existing mana resilience reduction and before `ModifyPower`, add the same guard to both methods:

```cpp
if (PowerType == POWER_MANA && unitTarget->IsPlayer()
    && unitTarget->ToPlayer()->getRace() == RACE_BROKEN_PLAYER)
    power = Acore::BrokenRacialEffects::ReduceManaDrain(power);
```

Include `BrokenRacialEffects.h` and preserve the existing effect ordering.

- [ ] **Step 3: Run the focused test to verify it passes**

```powershell
rtk test --build-config Debug --target unit_tests --gtest_filter=BrokenRacialEffects.*
```

Expected: PASS for all three tests. If no configured build exists, record the test as unavailable and continue with static lint; do not configure/build.

- [ ] **Step 4: Commit the implementation**

```powershell
rtk git add -- src/server/game/Entities/Player/BrokenRacialEffects.h src/server/game/Entities/Player/BrokenRacialEffects.cpp src/server/game/Spells/SpellEffects.cpp src/test/server/game/Modules/BrokenRacialsTest.cpp
rtk git commit -m "feat: implement Broken racial calculations"
```

### Task 3: Register Salvager and Echo behavior in the existing race module

**Files:**
- Modify: `modules/mod-worgoblin-high-elf/src/Worgoblin.cpp`
- Consume: `src/server/game/Entities/Player/BrokenRacialEffects.h`
- SQL binding is completed in Task 4.

**Interfaces:**
- Existing `worgoblin` `PlayerScript` receives `OnPlayerBeforeDurabilityRepair` and multiplies only Broken discounts.
- New `spell_broken_echo_of_the_naaru` `AuraScript` sets the periodic-heal amount to `EchoHealPerTick(player->GetMaxHealth())` on aura application.

- [ ] **Step 1: Add Salvager's repair hook**

Inside the existing `worgoblin` script class, add:

```cpp
void OnPlayerBeforeDurabilityRepair(Player* player, ObjectGuid /*npcGUID*/, ObjectGuid /*itemGUID*/, float& discountMod, uint8 /*guildBank*/) override
{
    if (player->getRace() == RACE_BROKEN_PLAYER)
        discountMod = Acore::BrokenRacialEffects::ApplySalvagerRepairDiscount(discountMod);
}
```

- [ ] **Step 2: Add Echo's aura script**

Use the established `PrepareAuraScript` pattern and apply the snapshot amount on `SPELL_AURA_PERIODIC_HEAL`:

```cpp
class spell_broken_echo_of_the_naaru : public AuraScript
{
    PrepareAuraScript(spell_broken_echo_of_the_naaru);

    void HandleApply(AuraEffect const* aurEff, AuraEffectHandleModes /*mode*/)
    {
        Player* player = GetTarget()->ToPlayer();
        if (!player || player->getRace() != RACE_BROKEN_PLAYER)
            return;

        const_cast<AuraEffect*>(aurEff)->SetAmount(Acore::BrokenRacialEffects::EchoHealPerTick(player->GetMaxHealth()));
    }

    void Register() override
    {
        OnEffectApply += AuraEffectApplyFn(spell_broken_echo_of_the_naaru::HandleApply,
            EFFECT_0, SPELL_AURA_PERIODIC_HEAL, AURA_EFFECT_HANDLE_REAL);
    }
};
```

Register it in the existing `Add_Worgoblin()` function with `RegisterSpellScript(spell_broken_echo_of_the_naaru);`.

- [ ] **Step 3: Run the focused calculation test and C++ linter**

```powershell
rtk test --build-config Debug --target unit_tests --gtest_filter=BrokenRacialEffects.*
python apps/codestyle/codestyle-cpp.py
```

Expected: the focused test remains green and the C++ linter reports no new violations.

- [ ] **Step 4: Commit the module behavior**

```powershell
rtk git add -- modules/mod-worgoblin-high-elf/src/Worgoblin.cpp
rtk git commit -m "feat: add Broken racial runtime effects"
```

### Task 4: Add the pending world-data contract

**Files:**
- Create: `data/sql/updates/pending_db_world/rev_1788720000000000000.sql`

**Interfaces:**
- Consumes the existing race IDs and spell IDs 110001–110004.
- Produces valid `playercreateinfo_skills`, `skillraceclassinfo_dbc`, `quest_template`, `spell_dbc`, `skilllineability_dbc`, `spell_script_names`, `playercreateinfo_spell_custom`, and `playercreateinfo_action` rows.

- [ ] **Step 1: Write the language and equipment-skill updates**

Use these masks: Orc `2`, Human `1`, Night Elf `8`, Goblin `256`, Worgen `2048`, High Elf `4096`, Broken `8192`.

```sql
SET @GoblinMask = 256;
SET @WorgenMask = 2048;
SET @HighElfMask = 4096;
SET @BrokenMask = 8192;

UPDATE `playercreateinfo_skills`
SET `raceMask` = `raceMask` | @GoblinMask | @BrokenMask
WHERE `skill` = 109 AND (`raceMask` & 2) != 0;

UPDATE `playercreateinfo_skills`
SET `raceMask` = `raceMask` | @WorgenMask | @HighElfMask
WHERE `skill` = 98 AND (`raceMask` & 1) != 0;

UPDATE `playercreateinfo_skills`
SET `raceMask` = `raceMask` | @HighElfMask
WHERE `skill` = 137 AND (`raceMask` & 512) != 0;

UPDATE `playercreateinfo_skills`
SET `raceMask` = `raceMask` | @GoblinMask | @WorgenMask | @HighElfMask | @BrokenMask
WHERE `skill` = 160 AND `classMask` IN (1, 3) AND `raceMask` != 0;

UPDATE `skillraceclassinfo_dbc`
SET `RaceMask` = `RaceMask` | @GoblinMask | @WorgenMask | @HighElfMask | @BrokenMask
WHERE `SkillID` IN (43, 44, 46, 54, 136, 160, 172, 173, 228, 229, 293, 413, 414, 415, 433);

UPDATE `skillraceclassinfo_dbc`
SET `RaceMask` = `RaceMask` | @GoblinMask | @BrokenMask
WHERE `SkillID` = 109;

UPDATE `skillraceclassinfo_dbc`
SET `RaceMask` = `RaceMask` | @WorgenMask | @HighElfMask
WHERE `SkillID` = 98;

UPDATE `skillraceclassinfo_dbc`
SET `RaceMask` = `RaceMask` | @HighElfMask
WHERE `SkillID` = 137;
```

Keep the current Hunter ranged choice: Goblin/Worgen receive the existing gun row and High Elf/Broken receive the existing bow row.

- [ ] **Step 2: Write starting-quest eligibility updates**

Add Goblin and Broken to Orc-restricted quests and High Elf to Alliance/Human-restricted quests using the existing full-mask exclusions. Add Worgen to the Night Elf/Teldrassil starting-chain IDs, including the existing Worgen class-equivalent list and Night Elf-only starting entries `5842`, `6341`, `6342`, `6343`, and `6344`. Do not add Worgen to the Darnassian skill row.

```sql
UPDATE `quest_template`
SET `AllowableRaces` = `AllowableRaces` | @GoblinMask | @BrokenMask
WHERE (`AllowableRaces` & 2) != 0
  AND `AllowableRaces` NOT IN (-1, 2147483647, 2047, 4095, 8191, 16383, 32767, 65535, 131071, 262143, 524287, 1048575, 2097151);

UPDATE `quest_template`
SET `AllowableRaces` = `AllowableRaces` | @HighElfMask
WHERE (`AllowableRaces` & 1) != 0
  AND `AllowableRaces` NOT IN (-1, 2147483647, 2047, 4095, 8191, 16383, 32767, 65535, 131071, 262143, 524287, 1048575, 2097151);

UPDATE `quest_template`
SET `AllowableRaces` = `AllowableRaces` | @WorgenMask
WHERE `ID` IN (26, 29, 272, 1703, 3116, 3117, 3118, 3119, 3120, 5061,
    5621, 5622, 5627, 5628, 5629, 5630, 5631, 5632, 5633, 5672, 5673,
    5674, 5675, 5842, 5921, 5923, 5924, 5925, 5929, 5931, 6001, 6063,
    6071, 6072, 6073, 6101, 6102, 6103, 6121, 6122, 6123, 6124, 6125,
    6341, 6342, 6343, 6344, 6721, 6722, 9591, 9592, 9593, 9675);
```

- [ ] **Step 3: Replace Broken's old spell grants and action buttons**

```sql
DELETE FROM `playercreateinfo_spell_custom`
WHERE `racemask` = 8192 AND `Spell` IN (20549, 20550, 20551, 20552);

DELETE FROM `playercreateinfo_spell_custom`
WHERE `racemask` = 8192 AND `Spell` IN (110001, 110002, 110003, 110004);

INSERT INTO `playercreateinfo_spell_custom` (`racemask`, `classmask`, `Spell`, `Note`) VALUES
(8192, 0, 110001, 'Broken - Salvager'),
(8192, 0, 110002, 'Broken - Krokul Cunning'),
(8192, 0, 110003, 'Broken - Fel-Scarred'),
(8192, 0, 110004, 'Broken - Echo of the Naaru');

UPDATE `playercreateinfo_action`
SET `action` = 110004
WHERE `race` = 14 AND `action` = 20549 AND `type` = 0;

DELETE FROM `skilllineability_dbc`
WHERE `ID` IN (31459, 31460, 31461, 31462);

INSERT INTO `skilllineability_dbc`
    (`ID`, `SkillLine`, `Spell`, `RaceMask`, `ClassMask`, `ExcludeRace`, `ExcludeClass`,
     `MinSkillLineRank`, `SupercededBySpell`, `AcquireMethod`, `TrivialSkillLineRankHigh`,
     `TrivialSkillLineRankLow`, `CharacterPoints_1`, `CharacterPoints_2`) VALUES
(31459, 792, 110001, 8192, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0),
(31460, 792, 110002, 8192, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0),
(31461, 792, 110003, 8192, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0),
(31462, 792, 110004, 8192, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0);

DELETE FROM `spell_script_names` WHERE `spell_id` = 110004;
INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`)
VALUES (110004, 'spell_broken_echo_of_the_naaru');
```

- [ ] **Step 4: Update the four spell definitions**

Update `spell_dbc` rows 110001–110004 by named columns:

- 110001: passive, two `SPELL_AURA_MOD_SKILL` effects with `EffectMiscValue_1=202`, `EffectMiscValue_2=186`, and `EffectBasePoints_1=9`, `EffectBasePoints_2=9`; name Salvager.
- 110002: passive `SPELL_AURA_MOD_STEALTH_LEVEL`, `EffectBasePoints_1=16`, `EffectMiscValue_1=0`; name Krokul Cunning.
- 110003: passive `SPELL_AURA_MOD_RESISTANCE`, `EffectBasePoints_1=9`, `EffectMiscValue_1=32`; name Fel-Scarred. The core handles the separate mana-drain reduction.
- 110004: active `SPELL_AURA_PERIODIC_HEAL`, `RecoveryTime=180000`, `DurationIndex=28`, and `EffectAuraPeriod_1=2000`; name Echo of the Naaru. The aura script supplies each 3% max-health tick.

Use named-column updates equivalent to the following, clearing every unused effect slot on each row and preserving the existing DBC table schema:

```sql
UPDATE `spell_dbc`
SET `Attributes` = 80, `AttributesEx` = 0, `AttributesEx2` = 0, `AttributesEx3` = 0,
    `CastingTimeIndex` = 0, `RecoveryTime` = 0, `DurationIndex` = 0,
    `Effect_1` = 6, `Effect_2` = 6, `Effect_3` = 0,
    `EffectBasePoints_1` = 9, `EffectBasePoints_2` = 9, `EffectBasePoints_3` = 0,
    `EffectAura_1` = 30, `EffectAura_2` = 30, `EffectAura_3` = 0,
    `EffectAuraPeriod_1` = 0, `EffectAuraPeriod_2` = 0, `EffectAuraPeriod_3` = 0,
    `EffectMiscValue_1` = 202, `EffectMiscValue_2` = 186, `EffectMiscValue_3` = 0,
    `EffectMiscValueB_1` = 0, `EffectMiscValueB_2` = 0, `EffectMiscValueB_3` = 0,
    `Name_Lang_enUS` = 'Salvager', `NameSubtext_Lang_enUS` = 'Racial Passive',
    `Description_Lang_enUS` = 'Engineering and Mining skill increased by 10, and repair costs reduced by 10%.',
    `AuraDescription_Lang_enUS` = 'Engineering and Mining skill increased by 10.',
    `SchoolMask` = 1
WHERE `ID` = 110001;

UPDATE `spell_dbc`
SET `Attributes` = 80, `AttributesEx` = 0, `AttributesEx2` = 0, `AttributesEx3` = 0,
    `CastingTimeIndex` = 0, `RecoveryTime` = 0, `DurationIndex` = 0,
    `Effect_1` = 6, `Effect_2` = 0, `Effect_3` = 0,
    `EffectBasePoints_1` = 16, `EffectBasePoints_2` = 0, `EffectBasePoints_3` = 0,
    `EffectAura_1` = 154, `EffectAura_2` = 0, `EffectAura_3` = 0,
    `EffectAuraPeriod_1` = 0, `EffectAuraPeriod_2` = 0, `EffectAuraPeriod_3` = 0,
    `EffectMiscValue_1` = 0, `EffectMiscValue_2` = 0, `EffectMiscValue_3` = 0,
    `EffectMiscValueB_1` = 0, `EffectMiscValueB_2` = 0, `EffectMiscValueB_3` = 0,
    `Name_Lang_enUS` = 'Krokul Cunning', `NameSubtext_Lang_enUS` = 'Racial Passive',
    `Description_Lang_enUS` = 'Reduces the radius at which enemies detect you by 5 yards.',
    `AuraDescription_Lang_enUS` = 'Enemy detection radius reduced by 5 yards.',
    `SchoolMask` = 1
WHERE `ID` = 110002;

UPDATE `spell_dbc`
SET `Attributes` = 80, `AttributesEx` = 0, `AttributesEx2` = 0, `AttributesEx3` = 0,
    `CastingTimeIndex` = 0, `RecoveryTime` = 0, `DurationIndex` = 0,
    `Effect_1` = 6, `Effect_2` = 0, `Effect_3` = 0,
    `EffectBasePoints_1` = 9, `EffectBasePoints_2` = 0, `EffectBasePoints_3` = 0,
    `EffectAura_1` = 22, `EffectAura_2` = 0, `EffectAura_3` = 0,
    `EffectAuraPeriod_1` = 0, `EffectAuraPeriod_2` = 0, `EffectAuraPeriod_3` = 0,
    `EffectMiscValue_1` = 32, `EffectMiscValue_2` = 0, `EffectMiscValue_3` = 0,
    `EffectMiscValueB_1` = 0, `EffectMiscValueB_2` = 0, `EffectMiscValueB_3` = 0,
    `Name_Lang_enUS` = 'Fel-Scarred', `NameSubtext_Lang_enUS` = 'Racial Passive',
    `Description_Lang_enUS` = 'Mana-draining magic is 10% less effective, and Shadow resistance is increased by 10.',
    `AuraDescription_Lang_enUS` = 'Shadow resistance increased by 10.',
    `SchoolMask` = 1
WHERE `ID` = 110003;

UPDATE `spell_dbc`
SET `Attributes` = 16, `AttributesEx` = 0, `AttributesEx2` = 0, `AttributesEx3` = 0,
    `CastingTimeIndex` = 1, `RecoveryTime` = 180000, `DurationIndex` = 28,
    `Effect_1` = 6, `Effect_2` = 0, `Effect_3` = 0,
    `EffectBasePoints_1` = 0, `EffectBasePoints_2` = 0, `EffectBasePoints_3` = 0,
    `EffectAura_1` = 8, `EffectAura_2` = 0, `EffectAura_3` = 0,
    `EffectAuraPeriod_1` = 2000, `EffectAuraPeriod_2` = 0, `EffectAuraPeriod_3` = 0,
    `EffectMiscValue_1` = 0, `EffectMiscValue_2` = 0, `EffectMiscValue_3` = 0,
    `EffectMiscValueB_1` = 0, `EffectMiscValueB_2` = 0, `EffectMiscValueB_3` = 0,
    `Name_Lang_enUS` = 'Echo of the Naaru', `NameSubtext_Lang_enUS` = 'Racial',
    `Description_Lang_enUS` = 'Restore 15% maximum health over 10 seconds.',
    `AuraDescription_Lang_enUS` = 'Restoring health over 10 seconds.',
    `SchoolMask` = 1
WHERE `ID` = 110004;
```

Do not replace full rows positionally.

- [ ] **Step 5: Validate the SQL update without importing it**

```powershell
python apps/codestyle/codestyle-sql.py
rtk git diff --check
```

Expected: SQL style passes or reports only pre-existing repository issues; the new pending file has no whitespace errors. Do not run the importer in this task.

- [ ] **Step 6: Commit the SQL update**

```powershell
rtk git add -- data/sql/updates/pending_db_world/rev_1788720000000000000.sql
rtk git commit -m "feat: repair custom race starting data"
```

### Task 5: Final verification and evidence report

**Files:**
- Inspect only the feature files and staged commits; do not modify unrelated dirty paths.

- [ ] **Step 1: Run the focused test again**

```powershell
rtk test --build-config Debug --target unit_tests --gtest_filter=BrokenRacialEffects.*
```

- [ ] **Step 2: Run both repository linters**

```powershell
python apps/codestyle/codestyle-cpp.py
python apps/codestyle/codestyle-sql.py
```

- [ ] **Step 3: Inspect only the feature diff**

```powershell
rtk git diff HEAD~4..HEAD --stat
rtk git diff HEAD~4..HEAD --check
rtk git status --short
```

Confirm no unrelated file was staged and separately report any pre-existing dirty files. Report build/test/import/live-client status exactly; no build, SQL import, client DBC smoke, or live character creation claim is valid unless it was actually run.
