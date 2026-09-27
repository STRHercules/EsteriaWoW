-- RBAC permission for the `.playerteam` command (RBAC_PERM_COMMAND_PLAYERTEAM = 1000, the custom
-- range declared at the end of src/server/game/Accounts/RBAC.h).
--
-- Linked to group 197, the same group that already grants the other character-admin commands
-- (274 customize, 283 level, 286 titles, 945 account info), so anyone who can inspect a character
-- today can also read and set its persistent team. Granting it elsewhere is a one-row insert.

DELETE FROM `rbac_permissions` WHERE `id` = 1000;
INSERT INTO `rbac_permissions` (`id`, `name`) VALUES
(1000, 'Command: playerteam');

DELETE FROM `rbac_linked_permissions` WHERE `linkedId` = 1000;
INSERT INTO `rbac_linked_permissions` (`id`, `linkedId`) VALUES
(197, 1000);
