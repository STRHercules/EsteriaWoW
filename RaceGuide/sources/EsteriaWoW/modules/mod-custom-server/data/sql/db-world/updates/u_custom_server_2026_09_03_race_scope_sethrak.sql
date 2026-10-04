-- Re-enable the explicitly playable Sethrak after the custom race scope update.
UPDATE `chrraces_dbc`
SET `Flags` = `Flags` - (`Flags` & 1)
WHERE `ID` = 15 AND (`Flags` & 1) = 1;
