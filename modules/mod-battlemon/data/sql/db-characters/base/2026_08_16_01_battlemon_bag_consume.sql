-- Consume the migration source from 2026_08_16_00_battlemon_bag.sql.
--
-- That file folds battlemon_account.pokeballs into the bag, and its ON DUPLICATE
-- no-op protects a stack the player has spent down. It does NOT protect a stack
-- spent all the way to zero: BagTake deletes the bag row at 0, so a re-run would
-- see no row to collide with and hand the old balls back. Zeroing the source
-- column makes the fold one-way, so every later pass selects nothing.
--
-- The server pins this column at 0 on save; the bag is the only inventory now.

UPDATE `battlemon_account` SET `pokeballs` = 0 WHERE `pokeballs` > 0;
