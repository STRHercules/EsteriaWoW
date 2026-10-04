-- Preserve the initial curated Skyborne appearance when enabling the native byte codec.
CREATE TABLE IF NOT EXISTS `esteria_appearance_schema` (
  `race` TINYINT UNSIGNED NOT NULL,
  `version` SMALLINT UNSIGNED NOT NULL,
  PRIMARY KEY (`race`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

START TRANSACTION;

UPDATE `characters` AS `c` SET `c`.`hairStyle` = CASE `c`.`hairStyle`
      WHEN 0 THEN IF(`c`.`gender` = 0, 16, 20) WHEN 1 THEN 0 WHEN 2 THEN 1 WHEN 3 THEN 2 END,
    `c`.`hairColor` = CASE `c`.`hairColor`
      WHEN 0 THEN 0 WHEN 1 THEN 4 WHEN 2 THEN 9 WHEN 3 THEN 13
      WHEN 4 THEN 18 WHEN 5 THEN 22 WHEN 6 THEN 27 WHEN 7 THEN 31 END,
    `c`.`facialStyle` = CASE `c`.`facialStyle` WHEN 0 THEN 0 WHEN 1 THEN 4 WHEN 2 THEN 1 WHEN 3 THEN 5 END
WHERE `c`.`race` IN (52, 53)
  AND NOT EXISTS (SELECT 1 FROM `esteria_appearance_schema` AS `s` WHERE `s`.`race` = `c`.`race`);

DELETE FROM `esteria_appearance_schema` WHERE `race` IN (52, 53) AND `version` = 0;
INSERT IGNORE INTO `esteria_appearance_schema` (`race`, `version`) VALUES (52, 1), (53, 1);

COMMIT;
