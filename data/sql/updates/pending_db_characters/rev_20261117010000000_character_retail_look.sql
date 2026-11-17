-- Per-character full Retail customization (see src/server/shared/RetailLookWire.h): an opaque 132-byte blob the
-- native client reads: version, race, sex, option count, then 64 little-endian u16 choice indices.
-- Re-applicable. Apply before starting a worldserver that includes this code: it prepares statements against the
-- table at startup.
CREATE TABLE IF NOT EXISTS `character_retail_look` (
  `guid` int unsigned NOT NULL,
  `data` binary(132) NOT NULL,
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
