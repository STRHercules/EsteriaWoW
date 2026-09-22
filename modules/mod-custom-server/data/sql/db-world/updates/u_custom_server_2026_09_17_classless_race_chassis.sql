-- Esteria Classless Wildcard: Paladin chassis rows for custom playable races.
-- The upstream module adds the stock races only; Esteria's race registry extends
-- the client/server contract through race 28.

-- Preserve the existing custom-race start profiles. Add only a missing
-- Paladin chassis row; the custom race module owns the action bars.
INSERT IGNORE INTO `playercreateinfo`
    (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`)
VALUES
    (15, 2, 1, 14, -618.518, -4251.67, 38.718, 0.0),
    (16, 2, 1, 14, -618.518, -4251.67, 38.718, 0.0),
    (17, 2, 530, 3431, 10349.6, -6357.29, 33.4026, 5.31605),
    (18, 2, 0, 12, -8949.95, -132.493, 83.5312, 0.0),
    (19, 2, 0, 12, -8949.95, -132.493, 83.5312, 0.0),
    (20, 2, 1, 14, -618.518, -4251.67, 38.718, 0.0),
    (21, 2, 530, 3526, -3961.64, -13931.2, 100.615, 2.08364),
    (22, 2, 1, 14, -618.518, -4251.67, 38.718, 0.0),
    (23, 2, 0, 1, -6240.32, 331.033, 382.758, 6.17716),
    (24, 2, 530, 3526, -3961.64, -13931.2, 100.615, 2.08364),
    (25, 2, 0, 12, -8949.95, -132.493, 83.5312, 0.0),
    (26, 2, 1, 14, -618.518, -4251.67, 38.718, 0.0),
    (27, 2, 1, 14, -618.518, -4251.67, 38.718, 0.0),
    (28, 2, 1, 14, -618.518, -4251.67, 38.718, 0.0);
