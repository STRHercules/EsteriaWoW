-- Mount customization (CMSG_ESTERIA_MOUNT_LOOK): the choices a character's customizable mount display is drawn with,
-- as comma-separated ChrCustomizationChoice (or client-defined) IDs.
CREATE TABLE IF NOT EXISTS `character_mount_look` (
  `guid` INT UNSIGNED NOT NULL,
  `display` INT UNSIGNED NOT NULL,
  `choices` VARCHAR(768) NOT NULL DEFAULT '',
  PRIMARY KEY (`guid`, `display`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
