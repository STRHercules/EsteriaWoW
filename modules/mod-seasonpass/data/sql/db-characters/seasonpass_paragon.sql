-- mod-seasonpass: Traumschmiede (Paragon-System, Diablo-Stil).
-- Jedes Prestige gibt 1 frei verteilbaren Punkt (stat 1-8).
-- Idempotent: der AzerothCore-Auto-Updater wendet diese Datei automatisch an.
CREATE TABLE IF NOT EXISTS `character_seasonpass_paragon` (
  `guid` INT UNSIGNED NOT NULL,
  `stat` TINYINT UNSIGNED NOT NULL COMMENT '1=Macht 2=Zauberkunst 3=Flaeche 4=Toxine 5=Vitalitaet 6=Seelenkraft 7=Heilkunst 8=Weisheit',
  `points` INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`guid`,`stat`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
