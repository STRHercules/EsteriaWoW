-- Sethrak display IDs must fit the server PlayerInfo uint16 fields.
UPDATE `chrraces`
SET `male_display_id` = 60000,
    `female_display_id` = 60001
WHERE `id` = @Sethrak;
