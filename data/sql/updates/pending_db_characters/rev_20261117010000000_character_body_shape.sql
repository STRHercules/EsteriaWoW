-- Per-character body sliders (see src/server/shared/BodyShapeWire.h): one version byte + 48 signed slot bytes.
-- Re-applicable. Apply before starting a worldserver that includes the body-slider code: it prepares statements
-- against this table at startup.
CREATE TABLE IF NOT EXISTS `character_body_shape` (
  `guid` int unsigned NOT NULL,
  `data` binary(49) NOT NULL,
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
