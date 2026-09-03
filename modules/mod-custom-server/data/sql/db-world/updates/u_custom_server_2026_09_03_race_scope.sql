-- Keep the active custom-race scope limited to Worgoblin and High Elf.
UPDATE `chrraces_dbc`
SET `Flags` = `Flags` | 1
WHERE `ID` BETWEEN 14 AND 28;
