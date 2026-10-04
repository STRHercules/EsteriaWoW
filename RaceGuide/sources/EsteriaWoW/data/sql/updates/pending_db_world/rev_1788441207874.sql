-- Enable the existing Sethrak race (ID 15) without changing other race flags.
UPDATE `chrraces_dbc` SET `Flags` = `Flags` - (`Flags` & 1)
WHERE `ID` = 15 AND (`Flags` & 1) = 1;
