-- Restore the custom-race Paladin action bars from the pre-migration world dump.
-- The chassis overlay must not replace these race-specific actions.

DELETE FROM `playercreateinfo_action`
 WHERE `race` IN (16, 17, 20, 21, 22, 23, 24, 25, 26, 27, 28)
   AND `class` = 2
   AND `button` = 9
   AND `action` = 59752;

INSERT IGNORE INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
VALUES
    (16, 2, 3, 33697, 0),
    (17, 2, 3, 28730, 0),
    (20, 2, 3, 33697, 0),
    (21, 2, 3, 59542, 0),
    (22, 2, 3, 33697, 0),
    (23, 2, 3, 20594, 0),
    (23, 2, 4, 2481, 0),
    (28, 2, 3, 33697, 0);
