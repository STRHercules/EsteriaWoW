-- Creation-time language skills for every custom race.
--
-- `playercreateinfo_skills` only carried Common (98) for 18/19/21/23/24/25 and
-- Orcish (109) for 15/16/17/20/22/26/27/28, so a freshly created Kul Tiran (29)
-- or Illidari (30) learned no language at all - `Player::LearnDefaultSkills()` walks
-- these rows through `GetSkillRaceClassInfo()`, which rev_1787850000010 widened.
-- Rank 0 is what the stock rows use; the language branch in `LearnDefaultSkill()`
-- sets 0/300/300 itself (SKILL_RANGE_LANGUAGE).

INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES
  (131072,    0, 98,  0, 'Pandaren - Common'),
  (262144,    0, 98,  0, 'Void Elf - Common'),
  (1048576,   0, 98,  0, 'Lightforged Draenei - Common'),
  (4194304,   0, 98,  0, 'Dark Iron Dwarf - Common'),
  (268435456, 0, 98,  0, 'Kul Tiran - Common'),
  (32768,     0, 109, 0, 'Eredar - Orcish'),
  (65536,     0, 109, 0, 'Nightborne - Orcish'),
  (524288,    0, 109, 0, 'Vulpera - Orcish'),
  (2097152,   0, 109, 0, 'Zandalari Troll - Orcish'),
  (134217728, 0, 109, 0, 'Dracthyr - Orcish'),
  (536870912, 0, 109, 0, 'Illidari - Orcish');
