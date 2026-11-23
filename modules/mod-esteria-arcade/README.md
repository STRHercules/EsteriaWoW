# mod-esteria-arcade

Playable arcade cabinets. The client half is wowdecomp `Extensions/Arcade` (a libretro frontend) and
`Addons/EsteriaArcade` (the screen window); content comes from wowdecomp `Tools/Arcade/pack.py`.

- A cabinet is a type-2 gameobject with `ScriptName = 'go_esteria_arcade'` and a row in `esteria_arcade_cabinet`
  (game + price in copper, 0 = free). Gossip offers "Insert a coin (…) and play …"; paying starts a session.
- The server sends the game (core, ROM path inside the client's `Patch-ZzzzzzzzzzzEsteriaArcadeRoms.MPQ`, title) and
  the character's battery RAM + resume state from `character_arcade_save`. The client uploads battery RAM every
  30 s while it changes, and both on quit.
- Walking more than 8 yards away, changing map or logging out stops the game: the client is told, uploads and quits.
  A stopped session accepts its final uploads for 60 s.
- Opcodes (core `Opcodes.h/.cpp`): `CMSG_ESTERIA_ARCADE` 0x54D, `SMSG_ESTERIA_ARCADE` 0x54E. The client opcode is
  `Handle_NULL` in the core; this module consumes it in `CanPacketReceive`.

## Apply

1. `data/sql/db-world/esteria_arcade.sql` (world) and `data/sql/db-characters/esteria_arcade.sql` (characters).
2. Content: `python Tools/Arcade/pack.py --cores <dir> --out <new dir> [--install]` (wowdecomp) writes
   `arcade_content.sql` (games, cabinet gameobjects 9610011+, prices, showcase spawns) and the client archive;
   `--install` does both for the Dev client and `housing_dev_*`.
3. Rebuild worldserver (the opcode change touches the core).

Not yet: housing cabinets (free for the owner, guest price, collectable earnings).
