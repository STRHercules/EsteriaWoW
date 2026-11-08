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

-- A room's floor when it is not the ground floor (stairwells lead up; floors are 12 yd apart).
CREATE TABLE IF NOT EXISTS `housing_room_level` (
  `room_id` INT UNSIGNED NOT NULL,
  `level`   TINYINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`room_id`),
  CONSTRAINT `fk_level_room` FOREIGN KEY (`room_id`) REFERENCES `housing_room` (`room_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
ALTER TABLE `housing_room_level` MODIFY `level` TINYINT NOT NULL DEFAULT 0 COMMENT '-1 basement, 0 ground';

-- Upgrades bought with gold beyond a new house's limits (the decor budget is housing_house.max_decor).
CREATE TABLE IF NOT EXISTS `housing_house_limits` (
  `house_id` INT UNSIGNED NOT NULL,
  `floors`   TINYINT UNSIGNED NOT NULL DEFAULT 4 COMMENT 'floors above the ground it may build, 4 to 15',
  PRIMARY KEY (`house_id`),
  CONSTRAINT `fk_limits_house` FOREIGN KEY (`house_id`) REFERENCES `housing_house` (`house_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
-- rooms arrived after floors; MySQL has no ADD COLUMN IF NOT EXISTS, so it is added only when missing
SET @has_rooms = (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE()
  AND table_name = 'housing_house_limits' AND column_name = 'rooms');
SET @add_rooms = IF(@has_rooms = 0,
  'ALTER TABLE `housing_house_limits` ADD COLUMN `rooms` TINYINT UNSIGNED NOT NULL DEFAULT 0', 'DO 0');
PREPARE add_rooms FROM @add_rooms;
EXECUTE add_rooms;
DEALLOCATE PREPARE add_rooms;

-- How an owner set their plot's house: its exterior style, and its offset (yd) and turn (degrees) from the plot's spot.
CREATE TABLE IF NOT EXISTS `housing_plot_style` (
  `map_id`   SMALLINT UNSIGNED NOT NULL,
  `plot`     TINYINT UNSIGNED NOT NULL,
  `style`    INT UNSIGNED NOT NULL DEFAULT 92,
  `offset_x` FLOAT NOT NULL DEFAULT 0,
  `offset_y` FLOAT NOT NULL DEFAULT 0,
  `turn`     FLOAT NOT NULL DEFAULT 0,
  PRIMARY KEY (`map_id`, `plot`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- height and size arrived after offset and turn; added only when missing
SET @has_oz = (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE()
  AND table_name = 'housing_plot_style' AND column_name = 'offset_z');
SET @add_oz = IF(@has_oz = 0, 'ALTER TABLE `housing_plot_style` ADD COLUMN `offset_z` FLOAT NOT NULL DEFAULT 0, '
  'ADD COLUMN `scale` FLOAT NOT NULL DEFAULT 1', 'DO 0');
PREPARE add_oz FROM @add_oz;
EXECUTE add_oz;
DEALLOCATE PREPARE add_oz;

-- The parts an owner swapped on their plot's house (housing_exterior_fixture.component); a missing type is the
-- style's default. Choices for another style are kept for when the owner goes back to it.
CREATE TABLE IF NOT EXISTS `housing_plot_fixture` (
  `map_id`    SMALLINT UNSIGNED NOT NULL,
  `plot`      TINYINT UNSIGNED NOT NULL,
  `theme`     INT UNSIGNED NOT NULL COMMENT 'HouseExteriorWmoData.ID',
  `type`      TINYINT UNSIGNED NOT NULL COMMENT '9 base 10 roof 11 door 12 window 16 chimney',
  `component` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`map_id`, `plot`, `theme`, `type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- What stands on each wall or roof spot of a plot's house (a spot: the dormer, tower and chimney hooks of one base or
-- roof shape at one place, numbered in hook order). No row: the roof's first chimney spot has a chimney, the rest
-- are empty.
CREATE TABLE IF NOT EXISTS `housing_plot_spot` (
  `map_id` SMALLINT UNSIGNED NOT NULL,
  `plot`   TINYINT UNSIGNED NOT NULL,
  `shape`  INT UNSIGNED NOT NULL COMMENT 'housing_exterior_fixture.component of the base or roof shape',
  `spot`   TINYINT UNSIGNED NOT NULL,
  `type`   TINYINT UNSIGNED NOT NULL COMMENT '0 empty, 14 dormer, 15 tower, 16 chimney',
  PRIMARY KEY (`map_id`, `plot`, `shape`, `spot`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Outdoor decor (housing_placed_decor rows with room_id NULL) and the saved world spawn each one is.
CREATE TABLE IF NOT EXISTS `housing_outdoor_spawn` (
  `placed_id` BIGINT UNSIGNED NOT NULL,
  `spawn_id`  INT UNSIGNED NOT NULL COMMENT 'acore_world gameobject guid',
  PRIMARY KEY (`placed_id`)
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
  `room_id`           INT UNSIGNED NULL COMMENT 'NULL: outdoor decor on the plot',
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
-- Outdoor decor has no room: room_id 0 broke fk_placed_room and rolled back the whole save.
ALTER TABLE `housing_placed_decor` MODIFY `room_id` INT UNSIGNED NULL COMMENT 'NULL: outdoor decor on the plot';

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
  `scope`             TINYINT UNSIGNED NOT NULL COMMENT '0 everyone 1 friends 2 guild 3 account 4 party (no row: party may visit)',
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

-- ---------------------------------------------------------------- neighborhoods (proto 15)
-- Every account has a neighborhood of its own (an instance of Founder's Point or Razorwind Shores); a guild may buy
-- more. Plots, their looks and outdoor decor are kept per neighborhood, and a house may stand in several (mirrored).
CREATE TABLE IF NOT EXISTS `housing_neighborhood` (
  `neighborhood_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `kind`            TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '0 an account''s own, 1 a guild''s',
  `owner`           INT UNSIGNED NOT NULL COMMENT 'account id, or guild id',
  `map_id`          SMALLINT UNSIGNED NOT NULL DEFAULT 2735 COMMENT '2735 Founder''s Point, 2736 Razorwind Shores',
  `created_at`      INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`neighborhood_id`),
  KEY `idx_owner` (`kind`, `owner`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Accounts a neighborhood's owner invited: they may come in and buy plots.
CREATE TABLE IF NOT EXISTS `housing_neighborhood_member` (
  `neighborhood_id` INT UNSIGNED NOT NULL,
  `account_id`      INT UNSIGNED NOT NULL,
  PRIMARY KEY (`neighborhood_id`, `account_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- What each guild rank may do in its guild's neighborhoods (1 buy plots, 2 invite, 4 manage); no row: buy plots.
CREATE TABLE IF NOT EXISTS `housing_guild_right` (
  `guild_id` INT UNSIGNED NOT NULL,
  `rank_id`  TINYINT UNSIGNED NOT NULL,
  `rights`   TINYINT UNSIGNED NOT NULL DEFAULT 1,
  PRIMARY KEY (`guild_id`, `rank_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Houses an account marked as favorites (shared by its characters), and each character's last 10 visits.
CREATE TABLE IF NOT EXISTS `housing_favorite` (
  `account_id`      INT UNSIGNED NOT NULL,
  `house_id`        INT UNSIGNED NOT NULL,
  `neighborhood_id` INT UNSIGNED NOT NULL,
  `added_at`        INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`account_id`, `house_id`, `neighborhood_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS `housing_recent_visit` (
  `guid`            INT UNSIGNED NOT NULL COMMENT 'character guid',
  `house_id`        INT UNSIGNED NOT NULL,
  `neighborhood_id` INT UNSIGNED NOT NULL,
  `visited_at`      INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`guid`, `house_id`, `neighborhood_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- An account may own any number of houses.
SET @has_uk = (SELECT COUNT(*) FROM information_schema.statistics WHERE table_schema = DATABASE()
  AND table_name = 'housing_house' AND index_name = 'uk_account');
SET @q = IF(@has_uk > 0, 'ALTER TABLE `housing_house` DROP INDEX `uk_account`, ADD KEY `idx_account` (`account_id`)', 'DO 0');
PREPARE s FROM @q; EXECUTE s; DEALLOCATE PREPARE s;

-- Outdoor decor belongs to the house's plot in one neighborhood.
SET @has_pdn = (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE()
  AND table_name = 'housing_placed_decor' AND column_name = 'neighborhood_id');
SET @q = IF(@has_pdn = 0, 'ALTER TABLE `housing_placed_decor` ADD COLUMN `neighborhood_id` INT UNSIGNED NOT NULL DEFAULT 0 '
  'COMMENT ''outdoor decor: the neighborhood whose plot it is on''', 'DO 0');
PREPARE s FROM @q; EXECUTE s; DEALLOCATE PREPARE s;

-- Every account with a house gets its neighborhood, and every house already on Founder's Point moves into its
-- owner's, onto the same plot.
INSERT INTO `housing_neighborhood` (`kind`, `owner`, `map_id`, `created_at`)
  SELECT 0, h.`account_id`, 2735, UNIX_TIMESTAMP() FROM `housing_house` h
  WHERE h.`account_id` NOT IN (SELECT `owner` FROM `housing_neighborhood` WHERE `kind` = 0) GROUP BY h.`account_id`;

-- The plot tables were keyed by map (2735); they become keyed by neighborhood. Looks first, while the claims still
-- say whose plot is whose; an unclaimed plot's leftovers go.
SET @old = (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE()
  AND table_name = 'housing_plot_claim' AND column_name = 'map_id');
SET @q = IF(@old > 0, 'UPDATE `housing_plot_style` t JOIN `housing_plot_claim` c ON c.map_id = t.map_id AND c.plot = t.plot '
  'JOIN `housing_house` h ON h.house_id = c.house_id JOIN `housing_neighborhood` n ON n.kind = 0 AND n.owner = h.account_id '
  'SET t.map_id = n.neighborhood_id WHERE t.map_id = 2735', 'DO 0');
PREPARE s FROM @q; EXECUTE s; DEALLOCATE PREPARE s;
SET @q = IF(@old > 0, 'UPDATE `housing_plot_fixture` t JOIN `housing_plot_claim` c ON c.map_id = t.map_id AND c.plot = t.plot '
  'JOIN `housing_house` h ON h.house_id = c.house_id JOIN `housing_neighborhood` n ON n.kind = 0 AND n.owner = h.account_id '
  'SET t.map_id = n.neighborhood_id WHERE t.map_id = 2735', 'DO 0');
PREPARE s FROM @q; EXECUTE s; DEALLOCATE PREPARE s;
SET @q = IF(@old > 0, 'UPDATE `housing_plot_spot` t JOIN `housing_plot_claim` c ON c.map_id = t.map_id AND c.plot = t.plot '
  'JOIN `housing_house` h ON h.house_id = c.house_id JOIN `housing_neighborhood` n ON n.kind = 0 AND n.owner = h.account_id '
  'SET t.map_id = n.neighborhood_id WHERE t.map_id = 2735', 'DO 0');
PREPARE s FROM @q; EXECUTE s; DEALLOCATE PREPARE s;
SET @q = IF(@old > 0, 'UPDATE `housing_plot_claim` c JOIN `housing_house` h ON h.house_id = c.house_id '
  'JOIN `housing_neighborhood` n ON n.kind = 0 AND n.owner = h.account_id SET c.map_id = n.neighborhood_id WHERE c.map_id = 2735',
  'DO 0');
PREPARE s FROM @q; EXECUTE s; DEALLOCATE PREPARE s;
SET @q = IF(@old > 0, 'DELETE FROM `housing_plot_style` WHERE map_id = 2735', 'DO 0');
PREPARE s FROM @q; EXECUTE s; DEALLOCATE PREPARE s;
SET @q = IF(@old > 0, 'DELETE FROM `housing_plot_fixture` WHERE map_id = 2735', 'DO 0');
PREPARE s FROM @q; EXECUTE s; DEALLOCATE PREPARE s;
SET @q = IF(@old > 0, 'DELETE FROM `housing_plot_spot` WHERE map_id = 2735', 'DO 0');
PREPARE s FROM @q; EXECUTE s; DEALLOCATE PREPARE s;
SET @q = IF(@old > 0, 'ALTER TABLE `housing_plot_style` CHANGE `map_id` `neighborhood_id` INT UNSIGNED NOT NULL', 'DO 0');
PREPARE s FROM @q; EXECUTE s; DEALLOCATE PREPARE s;
SET @q = IF(@old > 0, 'ALTER TABLE `housing_plot_fixture` CHANGE `map_id` `neighborhood_id` INT UNSIGNED NOT NULL', 'DO 0');
PREPARE s FROM @q; EXECUTE s; DEALLOCATE PREPARE s;
SET @q = IF(@old > 0, 'ALTER TABLE `housing_plot_spot` CHANGE `map_id` `neighborhood_id` INT UNSIGNED NOT NULL', 'DO 0');
PREPARE s FROM @q; EXECUTE s; DEALLOCATE PREPARE s;
-- a house stands on one plot per neighborhood (its foreign key keeps an index on house_id throughout)
SET @q = IF(@old > 0, 'ALTER TABLE `housing_plot_claim` CHANGE `map_id` `neighborhood_id` INT UNSIGNED NOT NULL, '
  'ADD UNIQUE KEY `uk_claim_house_hood` (`house_id`, `neighborhood_id`), DROP INDEX `uk_claim_house`', 'DO 0');
PREPARE s FROM @q; EXECUTE s; DEALLOCATE PREPARE s;

-- outdoor decor placed before neighborhoods is on its owner's plot in their own neighborhood
UPDATE `housing_placed_decor` p JOIN `housing_house` h ON h.`house_id` = p.`house_id`
  JOIN `housing_neighborhood` n ON n.`kind` = 0 AND n.`owner` = h.`account_id`
  SET p.`neighborhood_id` = n.`neighborhood_id` WHERE p.`room_id` IS NULL AND p.`neighborhood_id` = 0;
