CREATE TABLE IF NOT EXISTS `housing_decor_catalog` (
  `decor_id`          INT UNSIGNED      NOT NULL COMMENT 'HouseDecor.ID (retail)',
  `model_fdid`        INT UNSIGNED      NOT NULL COMMENT 'HouseDecor.ModelFileDataID, client loads retail\\<fdid>.m2',
  `display_id`        INT UNSIGNED      NOT NULL COMMENT 'GameObjectDisplayInfo ID, range 60000-69999',
  `gameobject_entry`  INT UNSIGNED      NOT NULL COMMENT 'gameobject_template.entry, range 9500000-9599999',
  `name`              VARCHAR(100)      NOT NULL DEFAULT '',
  `category`          TINYINT UNSIGNED  NOT NULL DEFAULT 0 COMMENT '0 misc 1 furniture 2 accents 3 lighting 4 nature 5 structural',
  `surface`           TINYINT UNSIGNED  NOT NULL DEFAULT 0 COMMENT '0 floor 1 wall 2 ceiling 3 on-decor',
  `budget_cost`       SMALLINT UNSIGNED NOT NULL DEFAULT 1,
  `min_scale`         FLOAT             NOT NULL DEFAULT 1,
  `max_scale`         FLOAT             NOT NULL DEFAULT 1,
  `origin`            ENUM('retail','custom','stock') NOT NULL DEFAULT 'retail' COMMENT 'retail = dev-only until distribution is decided',
  `enabled`           TINYINT UNSIGNED  NOT NULL DEFAULT 0,
  PRIMARY KEY (`decor_id`),
  UNIQUE KEY `uk_gameobject_entry` (`gameobject_entry`),
  KEY `idx_display` (`display_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Interior templates a house can use (MVP: one).
CREATE TABLE IF NOT EXISTS `housing_room_template` (
  `room_template_id`  INT UNSIGNED NOT NULL,
  `map_id`            SMALLINT UNSIGNED NOT NULL,
  `entry_x` FLOAT NOT NULL, `entry_y` FLOAT NOT NULL, `entry_z` FLOAT NOT NULL, `entry_o` FLOAT NOT NULL,
  `min_x` FLOAT NOT NULL, `min_y` FLOAT NOT NULL, `min_z` FLOAT NOT NULL,
  `max_x` FLOAT NOT NULL, `max_y` FLOAT NOT NULL, `max_z` FLOAT NOT NULL,
  `max_decor`         SMALLINT UNSIGNED NOT NULL DEFAULT 100,
  `name`              VARCHAR(100) NOT NULL DEFAULT '',
  PRIMARY KEY (`room_template_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Retail room-kit WMOs (RoomComponent rows) spawned as type-14 GameObjects when a house instance is populated.
CREATE TABLE IF NOT EXISTS `housing_room_piece` (
  `room_template_id`  INT UNSIGNED NOT NULL,
  `piece_id`          INT UNSIGNED NOT NULL COMMENT 'RoomComponent.ID (retail)',
  `gameobject_entry`  INT UNSIGNED NOT NULL COMMENT 'type 14, display retail\<fdid>.wmo',
  `pos_x` FLOAT NOT NULL, `pos_y` FLOAT NOT NULL, `pos_z` FLOAT NOT NULL,
  `yaw`               FLOAT NOT NULL COMMENT 'radians',
  PRIMARY KEY (`room_template_id`, `piece_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
