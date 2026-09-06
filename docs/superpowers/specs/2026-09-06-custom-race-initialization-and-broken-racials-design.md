# Custom race initialization and Broken racials

## Scope

Make Goblin (race 9), Worgen (race 12), High Elf (race 13), and Broken
(race 14) start with the language, weapon, and armor skills required by their
class and access the quests in their faction/class starting quest chains.
Worgen use the Night Elf/Teldrassil starting profile and Night Elf starting
quests, while retaining Common as their player language. Replace the copied
Broken racial set with the four requested abilities.

The existing dirty worktree remains untouched except for files directly
needed by this change. Existing custom spell IDs 110001 through 110004 are
reused so the race data does not gain another ID family.

## Existing flow and root cause

`ObjectMgr::LoadPlayerInfo()` loads `playercreateinfo_skills`, expands race
and class masks, and rejects a skill when `GetSkillRaceClassInfo()` cannot
validate the same race/class pair. `Player::LearnDefaultSkills()` then creates
the character's actual skills. Initial outfits are equipped through this
skill-backed path, so adding only a race row or only a client race entry is
insufficient.

Quest acceptance reaches `Player::SatisfyQuestRace()` and checks the player's
race bit against `quest_template.AllowableRaces`. The current Worgen spawn
profile already matches Night Elf/Teldrassil, but its quest masks only cover
some class equivalents rather than the Night Elf starting chain. The current
Broken replacement does not add Broken to the Orc quest masks. The shared
starting skill updates also leave the 2H-mace row without High Elf and Broken.

Broken's pending replacement currently removes old 110001-110004 rows but the
older race/action data still identifies those IDs as the copied Mag'har set.

## Design

### World data

Add one idempotent update under `data/sql/updates/pending_db_world/`.

- Ensure Common, Orcish, and Thalassian language rows contain the four race
  masks where appropriate: Common for Worgen/High Elf, Orcish for Goblin/
  Broken, and Thalassian for High Elf.
- Ensure the shared class-based weapon and armor skill rows validate for all
  four races. Extend the existing 2H-mace starting row to High Elf and Broken;
  preserve the existing one-ranged-weapon-per-Hunter choice.
- Add Goblin and Broken to Orc-restricted quests, High Elf to Human/Alliance
  starting quests, and Worgen to the Night Elf/Teldrassil starting quest
  chain, including its class-specific entries. Keep Worgen on Common only;
  do not grant Darnassian as a side effect of copying the Night Elf path. Do
  not bypass quest checks in C++.
- Replace Broken's old custom spell grants and action buttons with 110001
  Salvager, 110002 Krokul Cunning, 110003 Fel-Scarred, and 110004 Echo of the
  Naaru.
- Set the racial spell DBC fields needed for passive/aura behavior, including
  a 17-point stealth-level bonus (the core converts each point to 0.3 yards),
  a 10-point Shadow resistance bonus, and a 180000 ms Echo cooldown with a
  10000 ms periodic duration.

### Server behavior

Extend the existing race module's player hook for Salvager's 0.9 repair-cost
multiplier. Add a small aura script for Echo of the Naaru that applies five
2-second heals totaling 15% of the caster's maximum health, using the normal
spell aura lifecycle and no scheduler.

Apply Broken's 10% mana-drain reduction in the shared `Spell::EffectPowerDrain`
and `Spell::EffectPowerBurn` path after normal spell/resilience calculations.
This covers all callers of those effects instead of patching individual drain
spells. Keep the condition race-specific and limited to `POWER_MANA`.

### Compatibility and safety

- Use existing IDs and tables; add no dependency or new subsystem.
- Keep SQL idempotent and confined to `pending_db_world`.
- Do not alter quest C++ gating or grant unrestricted quest access.
- Do not configure or build unless separately requested.
- Do not claim client MPQ/DBC or live character creation verification from
  static checks alone.

## Validation

Before production edits, add a focused regression check for the Broken racial
math and spell definitions, run it red, then implement the minimum code to
make it green. Run the repository C++ and SQL linters plus `git diff --check`.
The final report will distinguish lint/SQL/source evidence from live server,
client, and gameplay smoke testing.
