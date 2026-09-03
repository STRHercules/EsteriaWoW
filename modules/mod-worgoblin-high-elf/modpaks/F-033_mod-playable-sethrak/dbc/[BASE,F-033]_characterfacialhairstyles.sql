-- characterfacialhairstyles: 2 inserts, 0 updates, all prior race-15 rows removed

-- Insertions
DELETE FROM `characterfacialhairstyles` WHERE `race` = @Sethrak;
INSERT INTO `characterfacialhairstyles` (`race`, `gender`, `variation_id`, `geoset_1`, `geoset_2`, `geoset_3`, `geoset_4`, `geoset_5`) VALUES
    (@Sethrak, @Male, 0, 0, 0, 0, 0, 0),
    (@Sethrak, @Female, 0, 0, 0, 0, 0, 0);
