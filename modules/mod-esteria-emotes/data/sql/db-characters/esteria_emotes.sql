-- Esteria emote collection: account-wide known emotes and the emote wheel layout (4 pages x 8 slots).
CREATE TABLE IF NOT EXISTS `esteria_emote_known` (
  `account` INT UNSIGNED NOT NULL,
  `emote` INT UNSIGNED NOT NULL,
  `learned` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'unix time',
  PRIMARY KEY (`account`, `emote`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `esteria_emote_wheel` (
  `account` INT UNSIGNED NOT NULL,
  `slot` TINYINT UNSIGNED NOT NULL COMMENT '0-31: page * 8 + position',
  `emote` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`account`, `slot`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
