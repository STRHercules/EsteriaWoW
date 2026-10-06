-- Cosmetics: make the wing spells stick, and give the tab and the wings their icons.
--
-- Skill line 779 is a class-category line, so mod-classless-wildcard sweeps it on login for a
-- Hero with nothing earned on it, and Player::SetSkill(line, 0, 0, 0) unlearns every spell whose
-- SkillLineAbility maps to that line -- which took all 123 wings away from every classless
-- character on every relog.  The client needs its own SkillLineAbility.dbc rows (shipped in the
-- MPQ) to file the spells under the tab; the server does not, so the server rows go.  Without
-- them 779 never enters _classSkillLines and nothing unlearns the wings.
DELETE FROM `skilllineability_dbc` WHERE `Spell` IN (970100, 970101, 970102, 970200, 970300, 970301, 970302, 970303, 970304, 970305, 970306, 970307, 970308, 970309, 970310, 970311, 970312, 970313, 970314, 970315, 970316, 970317, 970318, 970319, 970320, 970321, 970322, 970323, 970324, 970325, 970326, 970327, 970328, 970329, 970330, 970331, 970332, 970333, 970334, 970335, 970336, 970337, 970338, 970339, 970340, 970341, 970342, 970343, 970344, 970345, 970346, 970347, 970348, 970349, 970350, 970351, 970352, 970353, 970354, 970355, 970356, 970357, 970358, 970359, 970360, 970361, 970362, 970363, 970364, 970365, 970366, 970367, 970368, 970369, 970370, 970371, 970372, 970373, 970374, 970375, 970376, 970377, 970378, 970379, 970380, 970381, 970382, 970383, 970384, 970385, 970386, 970387, 970388, 970389, 970390, 970391, 970392, 970393, 970394, 970395, 970396, 970397, 970398, 970399, 970400, 970401, 970402, 970403, 970404, 970405, 970406, 970407, 970408, 970409, 970410, 970411, 970412, 970413, 970414, 970415, 970416, 970417, 970418, 970419, 970420, 970421, 970422, 970423, 970424, 970425, 970426);

-- 0/0 means "any race, any class" (SkillRaceClassInfo only tests a non-zero mask), so the
-- retro-ported races do not have the line deleted as invalid for their race/class.
UPDATE `skillraceclassinfo_dbc` SET `RaceMask` = 0, `ClassMask` = 0 WHERE `ID` = 1147;

-- Cosmetics tab icon.
UPDATE `skillline_dbc` SET `SpellIconID` = 515100 WHERE `ID` = 779;

-- Per-wing icons, taken from the icon Sirus itself gives the donor spell for each wing.
UPDATE `spell_dbc` SET `SpellIconID` = 515200 WHERE `ID` = 970301;
UPDATE `spell_dbc` SET `SpellIconID` = 515201 WHERE `ID` = 970302;
UPDATE `spell_dbc` SET `SpellIconID` = 515202 WHERE `ID` = 970303;
UPDATE `spell_dbc` SET `SpellIconID` = 515203 WHERE `ID` = 970304;
UPDATE `spell_dbc` SET `SpellIconID` = 515204 WHERE `ID` = 970305;
UPDATE `spell_dbc` SET `SpellIconID` = 515205 WHERE `ID` = 970306;
UPDATE `spell_dbc` SET `SpellIconID` = 515206 WHERE `ID` = 970307;
UPDATE `spell_dbc` SET `SpellIconID` = 515207 WHERE `ID` = 970308;
UPDATE `spell_dbc` SET `SpellIconID` = 515204 WHERE `ID` = 970309;
UPDATE `spell_dbc` SET `SpellIconID` = 515208 WHERE `ID` = 970310;
UPDATE `spell_dbc` SET `SpellIconID` = 515209 WHERE `ID` = 970311;
UPDATE `spell_dbc` SET `SpellIconID` = 515210 WHERE `ID` = 970312;
UPDATE `spell_dbc` SET `SpellIconID` = 515211 WHERE `ID` = 970313;
UPDATE `spell_dbc` SET `SpellIconID` = 515212 WHERE `ID` = 970314;
UPDATE `spell_dbc` SET `SpellIconID` = 515213 WHERE `ID` = 970315;
UPDATE `spell_dbc` SET `SpellIconID` = 515214 WHERE `ID` = 970318;
UPDATE `spell_dbc` SET `SpellIconID` = 515215 WHERE `ID` = 970319;
