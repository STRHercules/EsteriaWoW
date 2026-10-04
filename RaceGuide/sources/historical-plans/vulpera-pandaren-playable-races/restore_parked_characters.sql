-- Restore the four legacy custom-race characters parked on 2026-09-11 13:38.
-- Values come from zachgm-custom-char-backup-20260911-133854.csv.
UPDATE acore_characters.characters SET race=15, skin=3, face=0, hairstyle=0, haircolor=0 WHERE guid=299;
UPDATE acore_characters.characters SET race=15, skin=5, face=0, hairstyle=0, haircolor=0 WHERE guid=300;
UPDATE acore_characters.characters SET race=14, skin=6, face=0, hairstyle=2, haircolor=4 WHERE guid=305;
UPDATE acore_characters.characters SET race=14, skin=7, face=1, hairstyle=5, haircolor=0 WHERE guid=421;

-- Restore the bot characters moved off custom races (values in custom-race-bot-backup-*.csv).
-- They are disposable PlayerBot characters; the bot factory recreates them as needed.
