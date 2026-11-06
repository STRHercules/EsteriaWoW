-- mod-esteria-housing player state. Dev characters DB only (housing_dev_characters). Rollback: housing_characters_rollback.sql.

CREATE TABLE IF NOT EXISTS `housing_house` (
  `house_id`          INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `account_id`        INT UNSIGNED NOT NULL,
  `room_template_id`  INT UNSIGNED NOT NULL,
  `revision`          INT UNSIGNED NOT NULL DEFAULT 0,
  `max_decor`         SMALLINT UNSIGNED NOT NULL DEFAULT 100,
  `created_at`        INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'unix time',
  PRIMARY KEY (`house_id`),
  UNIQUE KEY `uk_account` (`account_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Rooms instanced from templates (one per house in MVP; the room graph comes later).
CREATE TABLE IF NOT EXISTS `housing_room` (
  `room_id`           INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `house_id`          INT UNSIGNED NOT NULL,
  `room_template_id`  INT UNSIGNED NOT NULL,
  `slot`              TINYINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`room_id`),
  UNIQUE KEY `uk_house_slot` (`house_id`, `slot`),
  CONSTRAINT `fk_room_house` FOREIGN KEY (`house_id`) REFERENCES `housing_house` (`house_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Placed decor. The transform is stored exactly as the server finalized it.
-- Where each room sits: a retail HouseRoom kind at an offset from the room template's origin, turned by quarter
-- turns. A room with no row is EsteriaHousing.FirstRoomKind at the origin (houses claimed before Phase 3a).
CREATE TABLE IF NOT EXISTS `housing_room_layout` (
  `room_id`     INT UNSIGNED NOT NULL,
  `kind`        INT UNSIGNED NOT NULL COMMENT 'housing_room_kind.kind (HouseRoom.ID)',
  `offset_x`    FLOAT NOT NULL DEFAULT 0,
  `offset_y`    FLOAT NOT NULL DEFAULT 0,
  `yaw_quarter` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`room_id`),
  CONSTRAINT `fk_layout_room` FOREIGN KEY (`room_id`) REFERENCES `housing_room` (`room_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- A room's look: wall, floor and ceiling theme (HouseTheme.ID, 3 Generic) and whether its ceiling is shown.
CREATE TABLE IF NOT EXISTS `housing_room_style` (
  `room_id`        INT UNSIGNED NOT NULL,
  `wall_theme`     INT UNSIGNED NOT NULL DEFAULT 3,
  `floor_theme`    INT UNSIGNED NOT NULL DEFAULT 3,
  `ceiling_theme`  INT UNSIGNED NOT NULL DEFAULT 3,
  `ceiling_hidden` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`room_id`),
  CONSTRAINT `fk_style_room` FOREIGN KEY (`room_id`) REFERENCES `housing_room` (`room_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Which neighborhood plot a house stands on, and the world gameobject guids of its exterior (saved spawns).
CREATE TABLE IF NOT EXISTS `housing_plot_claim` (
  `map_id`     SMALLINT UNSIGNED NOT NULL,
  `plot`       TINYINT UNSIGNED NOT NULL,
  `house_id`   INT UNSIGNED NOT NULL,
  `spawns`     VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'space-separated acore_world gameobject guids',
  `claimed_at` INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`map_id`, `plot`),
  UNIQUE KEY `uk_claim_house` (`house_id`),
  CONSTRAINT `fk_claim_house` FOREIGN KEY (`house_id`) REFERENCES `housing_house` (`house_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `housing_placed_decor` (
  `placed_id`         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `house_id`          INT UNSIGNED NOT NULL,
  `room_id`           INT UNSIGNED NOT NULL,
  `decor_id`          INT UNSIGNED NOT NULL,
  `pos_x` FLOAT NOT NULL, `pos_y` FLOAT NOT NULL, `pos_z` FLOAT NOT NULL,
  `rot_x` FLOAT NOT NULL DEFAULT 0, `rot_y` FLOAT NOT NULL DEFAULT 0,
  `rot_z` FLOAT NOT NULL DEFAULT 0, `rot_w` FLOAT NOT NULL DEFAULT 1,
  `scale`             FLOAT NOT NULL DEFAULT 1,
  `parent_placed_id`  BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'later: ride-along on larger decor',
  `placed_by`         INT UNSIGNED NOT NULL COMMENT 'character guid',
  `placed_at`         INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`placed_id`),
  KEY `idx_house` (`house_id`),
  CONSTRAINT `fk_placed_house` FOREIGN KEY (`house_id`) REFERENCES `housing_house` (`house_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_placed_room` FOREIGN KEY (`room_id`) REFERENCES `housing_room` (`room_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Decor owned by an account (shared across characters, warband-style).
CREATE TABLE IF NOT EXISTS `housing_account_decor` (
  `account_id`        INT UNSIGNED NOT NULL,
  `decor_id`          INT UNSIGNED NOT NULL,
  `quantity_owned`    SMALLINT UNSIGNED NOT NULL DEFAULT 0,
  `quantity_placed`   SMALLINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`account_id`, `decor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Who may visit or edit. MVP: only the owner edits; this is for the permission phase.
CREATE TABLE IF NOT EXISTS `housing_permission` (
  `house_id`          INT UNSIGNED NOT NULL,
  `scope`             TINYINT UNSIGNED NOT NULL COMMENT '0 everyone 1 friends 2 guild 3 account',
  `grantee`           INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'account id for scope 3, else 0',
  `can_visit`         TINYINT UNSIGNED NOT NULL DEFAULT 1,
  `can_edit`          TINYINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`house_id`, `scope`, `grantee`),
  CONSTRAINT `fk_perm_house` FOREIGN KEY (`house_id`) REFERENCES `housing_house` (`house_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Edit log: one row per accepted edit. Gives undo and audit later.
CREATE TABLE IF NOT EXISTS `housing_revision` (
  `house_id`          INT UNSIGNED NOT NULL,
  `revision`          INT UNSIGNED NOT NULL,
  `op`                TINYINT UNSIGNED NOT NULL COMMENT '1 place 2 move 3 remove',
  `placed_id`         BIGINT UNSIGNED NOT NULL,
  `before_json`       TEXT NULL,
  `after_json`        TEXT NULL,
  `character_guid`    INT UNSIGNED NOT NULL,
  `at`                INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`house_id`, `revision`),
  CONSTRAINT `fk_rev_house` FOREIGN KEY (`house_id`) REFERENCES `housing_house` (`house_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
