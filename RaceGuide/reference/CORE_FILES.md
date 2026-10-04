# Core files changed since the initial AC import

Baseline a29b5dc is this repository's AC import, not a verified current upstream commit.
This includes inherited playerbot changes, Eluna integration and Esteria changes.
Current dirty source is included; it is not proof that the running image contains every change.

Exact diff: [server-since-core-import.patch](../evidence/server-since-core-import.patch).

- [CMakeLists.txt](../sources/EsteriaWoW/CMakeLists.txt)
  Added 1 lines; removed 0.
- [apps/docker/Dockerfile](../sources/EsteriaWoW/apps/docker/Dockerfile)
  Added 3 lines; removed 8.
- [modules/CMakeLists.txt](../sources/EsteriaWoW/modules/CMakeLists.txt)
  Added 18 lines; removed 0.
- [src/cmake/macros/ConfigureEluna.cmake](../sources/EsteriaWoW/src/cmake/macros/ConfigureEluna.cmake)
  Added 1 lines; removed 0.
- [src/cmake/showoptions.cmake](../sources/EsteriaWoW/src/cmake/showoptions.cmake)
  Added 9 lines; removed 10.
- [src/common/CMakeLists.txt](../sources/EsteriaWoW/src/common/CMakeLists.txt)
  Added 6 lines; removed 0.
- [src/common/Collision/Maps/MapDefines.h](../sources/EsteriaWoW/src/common/Collision/Maps/MapDefines.h)
  Added 9 lines; removed 9.
- [src/server/apps/CMakeLists.txt](../sources/EsteriaWoW/src/server/apps/CMakeLists.txt)
  Added 0 lines; removed 39.
- [src/server/apps/worldserver/Main.cpp](../sources/EsteriaWoW/src/server/apps/worldserver/Main.cpp)
  Added 11 lines; removed 5.
- [src/server/apps/worldserver/worldserver.conf.dist](../sources/EsteriaWoW/src/server/apps/worldserver/worldserver.conf.dist)
  Added 18 lines; removed 14.
- [src/server/database/Database/DatabaseEnv.cpp](../sources/EsteriaWoW/src/server/database/Database/DatabaseEnv.cpp)
  Added 4 lines; removed 0.
- [src/server/database/Database/DatabaseEnv.h](../sources/EsteriaWoW/src/server/database/Database/DatabaseEnv.h)
  Added 9 lines; removed 0.
- [src/server/database/Database/DatabaseEnvFwd.h](../sources/EsteriaWoW/src/server/database/Database/DatabaseEnvFwd.h)
  Added 16 lines; removed 0.
- [src/server/database/Database/DatabaseLoader.cpp](../sources/EsteriaWoW/src/server/database/Database/DatabaseLoader.cpp)
  Added 5 lines; removed 0.
- [src/server/database/Database/DatabaseLoader.h](../sources/EsteriaWoW/src/server/database/Database/DatabaseLoader.h)
  Added 11 lines; removed 2.
- [src/server/database/Database/DatabaseWorkerPool.cpp](../sources/EsteriaWoW/src/server/database/Database/DatabaseWorkerPool.cpp)
  Added 8 lines; removed 0.
- [src/server/database/Database/Implementation/CharacterDatabase.cpp](../sources/EsteriaWoW/src/server/database/Database/Implementation/CharacterDatabase.cpp)
  Added 28 lines; removed 11.
- [src/server/database/Database/Implementation/CharacterDatabase.h](../sources/EsteriaWoW/src/server/database/Database/Implementation/CharacterDatabase.h)
  Added 4 lines; removed 0.
- [src/server/database/Database/Implementation/LoginDatabase.cpp](../sources/EsteriaWoW/src/server/database/Database/Implementation/LoginDatabase.cpp)
  Added 2 lines; removed 1.
- [src/server/database/Database/Implementation/LoginDatabase.h](../sources/EsteriaWoW/src/server/database/Database/Implementation/LoginDatabase.h)
  Added 1 lines; removed 0.
- [src/server/database/Database/Implementation/PlayerbotsDatabase.cpp](../sources/EsteriaWoW/src/server/database/Database/Implementation/PlayerbotsDatabase.cpp)
  Added 129 lines; removed 0.
- [src/server/database/Database/Implementation/PlayerbotsDatabase.h](../sources/EsteriaWoW/src/server/database/Database/Implementation/PlayerbotsDatabase.h)
  Added 120 lines; removed 0.
- [src/server/database/Database/Implementation/WorldDatabase.cpp](../sources/EsteriaWoW/src/server/database/Database/Implementation/WorldDatabase.cpp)
  Added 4 lines; removed 0.
- [src/server/database/Database/Implementation/WorldDatabase.h](../sources/EsteriaWoW/src/server/database/Database/Implementation/WorldDatabase.h)
  Added 4 lines; removed 0.
- [src/server/database/Updater/DBUpdater.cpp](../sources/EsteriaWoW/src/server/database/Updater/DBUpdater.cpp)
  Added 67 lines; removed 5.
- [src/server/database/Updater/DBUpdater.h](../sources/EsteriaWoW/src/server/database/Updater/DBUpdater.h)
  Added 1 lines; removed 0.
- [src/server/game/AI/CoreAI/UnitAI.h](../sources/EsteriaWoW/src/server/game/AI/CoreAI/UnitAI.h)
  Added 0 lines; removed 5.
- [src/server/game/AI/SmartScripts/SmartAI.cpp](../sources/EsteriaWoW/src/server/game/AI/SmartScripts/SmartAI.cpp)
  Added 0 lines; removed 2.
- [src/server/game/AI/SmartScripts/SmartScript.cpp](../sources/EsteriaWoW/src/server/game/AI/SmartScripts/SmartScript.cpp)
  Added 2 lines; removed 2.
- [src/server/game/Accounts/RBAC.h](../sources/EsteriaWoW/src/server/game/Accounts/RBAC.h)
  Added 1 lines; removed 0.
- [src/server/game/Achievements/AchievementMgr.cpp](../sources/EsteriaWoW/src/server/game/Achievements/AchievementMgr.cpp)
  Added 4 lines; removed 3.
- [src/server/game/Battlefield/Battlefield.cpp](../sources/EsteriaWoW/src/server/game/Battlefield/Battlefield.cpp)
  Added 31 lines; removed 30.
- [src/server/game/Battlefield/Battlefield.h](../sources/EsteriaWoW/src/server/game/Battlefield/Battlefield.h)
  Added 2 lines; removed 1.
- [src/server/game/Battlefield/Zones/BattlefieldWG.cpp](../sources/EsteriaWoW/src/server/game/Battlefield/Zones/BattlefieldWG.cpp)
  Added 11 lines; removed 10.
- [src/server/game/Battlegrounds/Arena.cpp](../sources/EsteriaWoW/src/server/game/Battlegrounds/Arena.cpp)
  Added 3 lines; removed 2.
- [src/server/game/Battlegrounds/ArenaTeam.cpp](../sources/EsteriaWoW/src/server/game/Battlegrounds/ArenaTeam.cpp)
  Added 19 lines; removed 0.
- [src/server/game/Battlegrounds/ArenaTeam.h](../sources/EsteriaWoW/src/server/game/Battlegrounds/ArenaTeam.h)
  Added 4 lines; removed 0.
- [src/server/game/Battlegrounds/Battleground.h](../sources/EsteriaWoW/src/server/game/Battlegrounds/Battleground.h)
  Added 1 lines; removed 0.
- [src/server/game/Battlegrounds/BattlegroundQueue.cpp](../sources/EsteriaWoW/src/server/game/Battlegrounds/BattlegroundQueue.cpp)
  Added 2 lines; removed 1.
- [src/server/game/Battlegrounds/Zones/BattlegroundAB.cpp](../sources/EsteriaWoW/src/server/game/Battlegrounds/Zones/BattlegroundAB.cpp)
  Added 16 lines; removed 15.
- [src/server/game/Battlegrounds/Zones/BattlegroundAB.h](../sources/EsteriaWoW/src/server/game/Battlegrounds/Zones/BattlegroundAB.h)
  Added 16 lines; removed 15.
- [src/server/game/Battlegrounds/Zones/BattlegroundAV.cpp](../sources/EsteriaWoW/src/server/game/Battlegrounds/Zones/BattlegroundAV.cpp)
  Added 13 lines; removed 12.
- [src/server/game/Battlegrounds/Zones/BattlegroundAV.h](../sources/EsteriaWoW/src/server/game/Battlegrounds/Zones/BattlegroundAV.h)
  Added 4 lines; removed 0.
- [src/server/game/Battlegrounds/Zones/BattlegroundEY.cpp](../sources/EsteriaWoW/src/server/game/Battlegrounds/Zones/BattlegroundEY.cpp)
  Added 14 lines; removed 13.
- [src/server/game/Battlegrounds/Zones/BattlegroundEY.h](../sources/EsteriaWoW/src/server/game/Battlegrounds/Zones/BattlegroundEY.h)
  Added 22 lines; removed 20.
- [src/server/game/Battlegrounds/Zones/BattlegroundIC.cpp](../sources/EsteriaWoW/src/server/game/Battlegrounds/Zones/BattlegroundIC.cpp)
  Added 20 lines; removed 19.
- [src/server/game/Battlegrounds/Zones/BattlegroundIC.h](../sources/EsteriaWoW/src/server/game/Battlegrounds/Zones/BattlegroundIC.h)
  Added 3 lines; removed 0.
- [src/server/game/Battlegrounds/Zones/BattlegroundSA.cpp](../sources/EsteriaWoW/src/server/game/Battlegrounds/Zones/BattlegroundSA.cpp)
  Added 19 lines; removed 18.
- [src/server/game/Battlegrounds/Zones/BattlegroundWS.cpp](../sources/EsteriaWoW/src/server/game/Battlegrounds/Zones/BattlegroundWS.cpp)
  Added 16 lines; removed 15.
- [src/server/game/CMakeLists.txt](../sources/EsteriaWoW/src/server/game/CMakeLists.txt)
  Added 37 lines; removed 2.
- [src/server/game/Cache/CharacterCache.cpp](../sources/EsteriaWoW/src/server/game/Cache/CharacterCache.cpp)
  Added 71 lines; removed 12.
- [src/server/game/Cache/CharacterCache.h](../sources/EsteriaWoW/src/server/game/Cache/CharacterCache.h)
  Added 7 lines; removed 2.
- [src/server/game/Chat/Channels/ChannelMgr.h](../sources/EsteriaWoW/src/server/game/Chat/Channels/ChannelMgr.h)
  Added 1 lines; removed 0.
- [src/server/game/Chat/Chat.cpp](../sources/EsteriaWoW/src/server/game/Chat/Chat.cpp)
  Added 72 lines; removed 0.
- [src/server/game/Chat/Chat.h](../sources/EsteriaWoW/src/server/game/Chat/Chat.h)
  Added 7 lines; removed 0.
- [src/server/game/Combat/ThreatManager.cpp](../sources/EsteriaWoW/src/server/game/Combat/ThreatManager.cpp)
  Added 0 lines; removed 9.
- [src/server/game/Conditions/ConditionMgr.cpp](../sources/EsteriaWoW/src/server/game/Conditions/ConditionMgr.cpp)
  Added 1 lines; removed 3.
- [src/server/game/DataStores/DBCStores.cpp](../sources/EsteriaWoW/src/server/game/DataStores/DBCStores.cpp)
  Added 198 lines; removed 105.
- [src/server/game/DataStores/DBCStores.h](../sources/EsteriaWoW/src/server/game/DataStores/DBCStores.h)
  Added 13 lines; removed 0.
- [src/server/game/DungeonFinding/LFGMgr.cpp](../sources/EsteriaWoW/src/server/game/DungeonFinding/LFGMgr.cpp)
  Added 7 lines; removed 6.
- [src/server/game/DungeonFinding/LFGMgr.h](../sources/EsteriaWoW/src/server/game/DungeonFinding/LFGMgr.h)
  Added 1 lines; removed 1.
- [src/server/game/DungeonFinding/LFGQueue.cpp](../sources/EsteriaWoW/src/server/game/DungeonFinding/LFGQueue.cpp)
  Added 6 lines; removed 0.
- [src/server/game/Entities/Creature/Creature.cpp](../sources/EsteriaWoW/src/server/game/Entities/Creature/Creature.cpp)
  Added 1 lines; removed 1.
- [src/server/game/Entities/Creature/CreatureData.h](../sources/EsteriaWoW/src/server/game/Entities/Creature/CreatureData.h)
  Added 1 lines; removed 1.
- [src/server/game/Entities/Item/Item.cpp](../sources/EsteriaWoW/src/server/game/Entities/Item/Item.cpp)
  Added 13 lines; removed 5.
- [src/server/game/Entities/Item/Item.h](../sources/EsteriaWoW/src/server/game/Entities/Item/Item.h)
  Added 1 lines; removed 1.
- [src/server/game/Entities/Item/ItemTemplate.h](../sources/EsteriaWoW/src/server/game/Entities/Item/ItemTemplate.h)
  Added 3 lines; removed 1.
- [src/server/game/Entities/Object/Object.cpp](../sources/EsteriaWoW/src/server/game/Entities/Object/Object.cpp)
  Added 31 lines; removed 0.
- [src/server/game/Entities/Object/Object.h](../sources/EsteriaWoW/src/server/game/Entities/Object/Object.h)
  Added 20 lines; removed 0.
- [src/server/game/Entities/Object/Updates/UpdateFieldFlags.cpp](../sources/EsteriaWoW/src/server/game/Entities/Object/Updates/UpdateFieldFlags.cpp)
  Added 2 lines; removed 2.
- [src/server/game/Entities/Object/Updates/UpdateFields.h](../sources/EsteriaWoW/src/server/game/Entities/Object/Updates/UpdateFields.h)
  Added 1 lines; removed 1.
- [src/server/game/Entities/Player/BrokenRacialEffects.cpp](../sources/EsteriaWoW/src/server/game/Entities/Player/BrokenRacialEffects.cpp)
  Added 21 lines; removed 0.
- [src/server/game/Entities/Player/BrokenRacialEffects.h](../sources/EsteriaWoW/src/server/game/Entities/Player/BrokenRacialEffects.h)
  Added 13 lines; removed 0.
- [src/server/game/Entities/Player/Player.cpp](../sources/EsteriaWoW/src/server/game/Entities/Player/Player.cpp)
  Added 163 lines; removed 11.
- [src/server/game/Entities/Player/Player.h](../sources/EsteriaWoW/src/server/game/Entities/Player/Player.h)
  Added 12 lines; removed 2.
- [src/server/game/Entities/Player/PlayerQuest.cpp](../sources/EsteriaWoW/src/server/game/Entities/Player/PlayerQuest.cpp)
  Added 1 lines; removed 4.
- [src/server/game/Entities/Player/PlayerStorage.cpp](../sources/EsteriaWoW/src/server/game/Entities/Player/PlayerStorage.cpp)
  Added 103 lines; removed 4.
- [src/server/game/Entities/Player/PlayerUpdates.cpp](../sources/EsteriaWoW/src/server/game/Entities/Player/PlayerUpdates.cpp)
  Added 27 lines; removed 14.
- [src/server/game/Entities/Player/PlayerUpdates.cpp.bkup](../sources/EsteriaWoW/src/server/game/Entities/Player/PlayerUpdates.cpp.bkup)
  Added 2455 lines; removed 0.
- [src/server/game/Entities/Player/RaceMgr.cpp](../sources/EsteriaWoW/src/server/game/Entities/Player/RaceMgr.cpp)
  Added 3 lines; removed 1.
- [src/server/game/Entities/Unit/Unit.cpp](../sources/EsteriaWoW/src/server/game/Entities/Unit/Unit.cpp)
  Added 71 lines; removed 8.
- [src/server/game/Entities/Unit/Unit.h](../sources/EsteriaWoW/src/server/game/Entities/Unit/Unit.h)
  Added 3 lines; removed 1.
- [src/server/game/Entities/Vehicle/Vehicle.cpp](../sources/EsteriaWoW/src/server/game/Entities/Vehicle/Vehicle.cpp)
  Added 1 lines; removed 15.
- [src/server/game/Entities/Vehicle/VehicleDefines.h](../sources/EsteriaWoW/src/server/game/Entities/Vehicle/VehicleDefines.h)
  Added 1 lines; removed 0.
- [src/server/game/Globals/ObjectMgr.cpp](../sources/EsteriaWoW/src/server/game/Globals/ObjectMgr.cpp)
  Added 171 lines; removed 8.
- [src/server/game/Globals/ObjectMgr.h](../sources/EsteriaWoW/src/server/game/Globals/ObjectMgr.h)
  Added 1 lines; removed 0.
- [src/server/game/Groups/Group.cpp](../sources/EsteriaWoW/src/server/game/Groups/Group.cpp)
  Added 13 lines; removed 6.
- [src/server/game/Groups/Group.h](../sources/EsteriaWoW/src/server/game/Groups/Group.h)
  Added 5 lines; removed 0.
- [src/server/game/Guilds/Guild.cpp](../sources/EsteriaWoW/src/server/game/Guilds/Guild.cpp)
  Added 308 lines; removed 232.
- [src/server/game/Guilds/Guild.h](../sources/EsteriaWoW/src/server/game/Guilds/Guild.h)
  Added 171 lines; removed 164.
- [src/server/game/Handlers/ArenaTeamHandler.cpp](../sources/EsteriaWoW/src/server/game/Handlers/ArenaTeamHandler.cpp)
  Added 3 lines; removed 1.
- [src/server/game/Handlers/ChannelHandler.cpp](../sources/EsteriaWoW/src/server/game/Handlers/ChannelHandler.cpp)
  Added 20 lines; removed 19.
- [src/server/game/Handlers/CharacterHandler.cpp](../sources/EsteriaWoW/src/server/game/Handlers/CharacterHandler.cpp)
  Added 426 lines; removed 266.
- [src/server/game/Handlers/ChatHandler.cpp](../sources/EsteriaWoW/src/server/game/Handlers/ChatHandler.cpp)
  Added 15 lines; removed 4.
- [src/server/game/Handlers/GroupHandler.cpp](../sources/EsteriaWoW/src/server/game/Handlers/GroupHandler.cpp)
  Added 51 lines; removed 0.
- [src/server/game/Handlers/PetitionsHandler.cpp](../sources/EsteriaWoW/src/server/game/Handlers/PetitionsHandler.cpp)
  Added 22 lines; removed 2.
- `src/server/game/LuaEngine` (deleted)
  Added 1 lines; removed 0.
- [src/server/game/Maps/Map.cpp](../sources/EsteriaWoW/src/server/game/Maps/Map.cpp)
  Added 27 lines; removed 0.
- [src/server/game/Maps/Map.h](../sources/EsteriaWoW/src/server/game/Maps/Map.h)
  Added 17 lines; removed 0.
- [src/server/game/Misc/GameGraveyard.cpp](../sources/EsteriaWoW/src/server/game/Misc/GameGraveyard.cpp)
  Added 6 lines; removed 1.
- [src/server/game/Misc/GameGraveyard.h](../sources/EsteriaWoW/src/server/game/Misc/GameGraveyard.h)
  Added 1 lines; removed 0.
- [src/server/game/Movement/MotionMaster.cpp](../sources/EsteriaWoW/src/server/game/Movement/MotionMaster.cpp)
  Added 42 lines; removed 0.
- [src/server/game/Movement/MotionMaster.h](../sources/EsteriaWoW/src/server/game/Movement/MotionMaster.h)
  Added 4 lines; removed 2.
- [src/server/game/Movement/MovementGenerators/EscortMovementGenerator.cpp](../sources/EsteriaWoW/src/server/game/Movement/MovementGenerators/EscortMovementGenerator.cpp)
  Added 0 lines; removed 4.
- [src/server/game/Movement/MovementGenerators/PathGenerator.cpp](../sources/EsteriaWoW/src/server/game/Movement/MovementGenerators/PathGenerator.cpp)
  Added 33 lines; removed 3.
- [src/server/game/Movement/MovementGenerators/PathGenerator.h](../sources/EsteriaWoW/src/server/game/Movement/MovementGenerators/PathGenerator.h)
  Added 18 lines; removed 0.
- [src/server/game/Movement/MovementGenerators/PointMovementGenerator.cpp](../sources/EsteriaWoW/src/server/game/Movement/MovementGenerators/PointMovementGenerator.cpp)
  Added 5 lines; removed 0.
- [src/server/game/Movement/MovementGenerators/WaypointMovementGenerator.cpp](../sources/EsteriaWoW/src/server/game/Movement/MovementGenerators/WaypointMovementGenerator.cpp)
  Added 3 lines; removed 1.
- [src/server/game/OutdoorPvP/OutdoorPvP.cpp](../sources/EsteriaWoW/src/server/game/OutdoorPvP/OutdoorPvP.cpp)
  Added 8 lines; removed 7.
- [src/server/game/Scripting/ScriptDefines/DatabaseScript.cpp](../sources/EsteriaWoW/src/server/game/Scripting/ScriptDefines/DatabaseScript.cpp)
  Added 55 lines; removed 0.
- [src/server/game/Scripting/ScriptDefines/DatabaseScript.h](../sources/EsteriaWoW/src/server/game/Scripting/ScriptDefines/DatabaseScript.h)
  Added 7 lines; removed 0.
- [src/server/game/Scripting/ScriptDefines/MiscScript.cpp](../sources/EsteriaWoW/src/server/game/Scripting/ScriptDefines/MiscScript.cpp)
  Added 12 lines; removed 0.
- [src/server/game/Scripting/ScriptDefines/MiscScript.h](../sources/EsteriaWoW/src/server/game/Scripting/ScriptDefines/MiscScript.h)
  Added 8 lines; removed 0.
- [src/server/game/Scripting/ScriptDefines/PlayerScript.cpp](../sources/EsteriaWoW/src/server/game/Scripting/ScriptDefines/PlayerScript.cpp)
  Added 25 lines; removed 0.
- [src/server/game/Scripting/ScriptDefines/PlayerScript.h](../sources/EsteriaWoW/src/server/game/Scripting/ScriptDefines/PlayerScript.h)
  Added 12 lines; removed 1.
- [src/server/game/Scripting/ScriptDefines/PlayerbotsScript.cpp](../sources/EsteriaWoW/src/server/game/Scripting/ScriptDefines/PlayerbotsScript.cpp)
  Added 105 lines; removed 0.
- [src/server/game/Scripting/ScriptDefines/ServerScript.cpp](../sources/EsteriaWoW/src/server/game/Scripting/ScriptDefines/ServerScript.cpp)
  Added 9 lines; removed 0.
- [src/server/game/Scripting/ScriptDefines/ServerScript.h](../sources/EsteriaWoW/src/server/game/Scripting/ScriptDefines/ServerScript.h)
  Added 3 lines; removed 0.
- [src/server/game/Scripting/ScriptDefines/WorldScript.cpp](../sources/EsteriaWoW/src/server/game/Scripting/ScriptDefines/WorldScript.cpp)
  Added 5 lines; removed 0.
- [src/server/game/Scripting/ScriptDefines/WorldScript.h](../sources/EsteriaWoW/src/server/game/Scripting/ScriptDefines/WorldScript.h)
  Added 3 lines; removed 0.
- [src/server/game/Scripting/ScriptMgr.cpp](../sources/EsteriaWoW/src/server/game/Scripting/ScriptMgr.cpp)
  Added 8 lines; removed 2.
- [src/server/game/Scripting/ScriptMgr.h](../sources/EsteriaWoW/src/server/game/Scripting/ScriptMgr.h)
  Added 44 lines; removed 1.
- [src/server/game/Server/FreebornClaim.h](../sources/EsteriaWoW/src/server/game/Server/FreebornClaim.h)
  Added 114 lines; removed 0.
- [src/server/game/Server/PlayerTeamSide.h](../sources/EsteriaWoW/src/server/game/Server/PlayerTeamSide.h)
  Added 36 lines; removed 0.
- [src/server/game/Server/WorldSession.cpp](../sources/EsteriaWoW/src/server/game/Server/WorldSession.cpp)
  Added 42 lines; removed 4.
- [src/server/game/Server/WorldSession.h](../sources/EsteriaWoW/src/server/game/Server/WorldSession.h)
  Added 33 lines; removed 2.
- [src/server/game/Server/WorldSessionMgr.cpp](../sources/EsteriaWoW/src/server/game/Server/WorldSessionMgr.cpp)
  Added 5 lines; removed 0.
- [src/server/game/Spells/Spell.cpp](../sources/EsteriaWoW/src/server/game/Spells/Spell.cpp)
  Added 7 lines; removed 40.
- [src/server/game/Spells/SpellEffects.cpp](../sources/EsteriaWoW/src/server/game/Spells/SpellEffects.cpp)
  Added 9 lines; removed 0.
- [src/server/game/Spells/SpellInfoCorrections.cpp](../sources/EsteriaWoW/src/server/game/Spells/SpellInfoCorrections.cpp)
  Added 6 lines; removed 7.
- [src/server/game/TC9Sidecar/TC9Sidecar.cpp](../sources/EsteriaWoW/src/server/game/TC9Sidecar/TC9Sidecar.cpp)
  Added 0 lines; removed 65.
- [src/server/game/TC9Sidecar/TC9Sidecar.h](../sources/EsteriaWoW/src/server/game/TC9Sidecar/TC9Sidecar.h)
  Added 0 lines; removed 5.
- [src/server/game/Tools/PlayerDump.cpp](../sources/EsteriaWoW/src/server/game/Tools/PlayerDump.cpp)
  Added 75 lines; removed 2.
- [src/server/game/World/IWorld.h](../sources/EsteriaWoW/src/server/game/World/IWorld.h)
  Added 13 lines; removed 0.
- [src/server/game/World/World.cpp](../sources/EsteriaWoW/src/server/game/World/World.cpp)
  Added 27 lines; removed 0.
- [src/server/game/World/World.h](../sources/EsteriaWoW/src/server/game/World/World.h)
  Added 25 lines; removed 0.
- [src/server/game/World/WorldConfig.cpp](../sources/EsteriaWoW/src/server/game/World/WorldConfig.cpp)
  Added 4 lines; removed 5.
- [src/server/game/World/WorldConfig.h](../sources/EsteriaWoW/src/server/game/World/WorldConfig.h)
  Added 1 lines; removed 1.
- [src/server/scripts/Commands/cs_cache.cpp](../sources/EsteriaWoW/src/server/scripts/Commands/cs_cache.cpp)
  Added 5 lines; removed 2.
- [src/server/scripts/Commands/cs_character.cpp](../sources/EsteriaWoW/src/server/scripts/Commands/cs_character.cpp)
  Added 144 lines; removed 10.
- [src/server/scripts/Commands/cs_debug.cpp](../sources/EsteriaWoW/src/server/scripts/Commands/cs_debug.cpp)
  Added 1 lines; removed 1.
- [src/server/scripts/Commands/cs_server.cpp](../sources/EsteriaWoW/src/server/scripts/Commands/cs_server.cpp)
  Added 8 lines; removed 0.
- [src/server/scripts/EasternKingdoms/ScarletMonastery/instance_scarlet_monastery.cpp](../sources/EsteriaWoW/src/server/scripts/EasternKingdoms/ScarletMonastery/instance_scarlet_monastery.cpp)
  Added 14 lines; removed 38.
- [src/server/scripts/EasternKingdoms/ZulGurub/boss_jeklik.cpp](../sources/EsteriaWoW/src/server/scripts/EasternKingdoms/ZulGurub/boss_jeklik.cpp)
  Added 1 lines; removed 1.
- [src/server/scripts/Events/love_in_air.cpp](../sources/EsteriaWoW/src/server/scripts/Events/love_in_air.cpp)
  Added 3 lines; removed 2.
- [src/server/scripts/Northrend/IcecrownCitadel/boss_professor_putricide.cpp](../sources/EsteriaWoW/src/server/scripts/Northrend/IcecrownCitadel/boss_professor_putricide.cpp)
  Added 0 lines; removed 37.
- [src/server/scripts/Northrend/Ulduar/Ulduar/boss_flame_leviathan.cpp](../sources/EsteriaWoW/src/server/scripts/Northrend/Ulduar/Ulduar/boss_flame_leviathan.cpp)
  Added 4 lines; removed 90.
- [src/server/scripts/Northrend/Ulduar/Ulduar/boss_freya.cpp](../sources/EsteriaWoW/src/server/scripts/Northrend/Ulduar/Ulduar/boss_freya.cpp)
  Added 0 lines; removed 13.
- [src/server/scripts/Northrend/Ulduar/Ulduar/boss_mimiron.cpp](../sources/EsteriaWoW/src/server/scripts/Northrend/Ulduar/Ulduar/boss_mimiron.cpp)
  Added 1 lines; removed 15.
- [src/server/scripts/Northrend/Ulduar/Ulduar/boss_razorscale.cpp](../sources/EsteriaWoW/src/server/scripts/Northrend/Ulduar/Ulduar/boss_razorscale.cpp)
  Added 3 lines; removed 6.
- [src/server/scripts/Northrend/Ulduar/Ulduar/boss_thorim.cpp](../sources/EsteriaWoW/src/server/scripts/Northrend/Ulduar/Ulduar/boss_thorim.cpp)
  Added 7 lines; removed 10.
- [src/server/scripts/Northrend/Ulduar/Ulduar/boss_yoggsaron.cpp](../sources/EsteriaWoW/src/server/scripts/Northrend/Ulduar/Ulduar/boss_yoggsaron.cpp)
  Added 5 lines; removed 44.
- [src/server/scripts/Northrend/Ulduar/Ulduar/instance_ulduar.cpp](../sources/EsteriaWoW/src/server/scripts/Northrend/Ulduar/Ulduar/instance_ulduar.cpp)
  Added 34 lines; removed 368.
- [src/server/scripts/Northrend/Ulduar/Ulduar/ulduar.cpp](../sources/EsteriaWoW/src/server/scripts/Northrend/Ulduar/Ulduar/ulduar.cpp)
  Added 14 lines; removed 25.
- [src/server/scripts/Northrend/Ulduar/Ulduar/ulduar.h](../sources/EsteriaWoW/src/server/scripts/Northrend/Ulduar/Ulduar/ulduar.h)
  Added 1 lines; removed 48.
- [src/server/scripts/Northrend/VaultOfArchavon/boss_emalon.cpp](../sources/EsteriaWoW/src/server/scripts/Northrend/VaultOfArchavon/boss_emalon.cpp)
  Added 0 lines; removed 7.
- [src/server/scripts/Northrend/zone_dragonblight.cpp](../sources/EsteriaWoW/src/server/scripts/Northrend/zone_dragonblight.cpp)
  Added 0 lines; removed 3.
- [src/server/scripts/Northrend/zone_storm_peaks.cpp](../sources/EsteriaWoW/src/server/scripts/Northrend/zone_storm_peaks.cpp)
  Added 10 lines; removed 27.
- [src/server/scripts/Northrend/zone_wintergrasp.cpp](../sources/EsteriaWoW/src/server/scripts/Northrend/zone_wintergrasp.cpp)
  Added 3 lines; removed 2.
- [src/server/scripts/OutdoorPvP/OutdoorPvPEP.cpp](../sources/EsteriaWoW/src/server/scripts/OutdoorPvP/OutdoorPvPEP.cpp)
  Added 3 lines; removed 2.
- [src/server/scripts/OutdoorPvP/OutdoorPvPGH.cpp](../sources/EsteriaWoW/src/server/scripts/OutdoorPvP/OutdoorPvPGH.cpp)
  Added 3 lines; removed 2.
- [src/server/scripts/OutdoorPvP/OutdoorPvPHP.cpp](../sources/EsteriaWoW/src/server/scripts/OutdoorPvP/OutdoorPvPHP.cpp)
  Added 5 lines; removed 4.
- [src/server/scripts/OutdoorPvP/OutdoorPvPNA.cpp](../sources/EsteriaWoW/src/server/scripts/OutdoorPvP/OutdoorPvPNA.cpp)
  Added 5 lines; removed 4.
- [src/server/scripts/OutdoorPvP/OutdoorPvPSI.cpp](../sources/EsteriaWoW/src/server/scripts/OutdoorPvP/OutdoorPvPSI.cpp)
  Added 5 lines; removed 4.
- [src/server/scripts/OutdoorPvP/OutdoorPvPTF.cpp](../sources/EsteriaWoW/src/server/scripts/OutdoorPvP/OutdoorPvPTF.cpp)
  Added 2 lines; removed 1.
- [src/server/scripts/OutdoorPvP/OutdoorPvPZM.cpp](../sources/EsteriaWoW/src/server/scripts/OutdoorPvP/OutdoorPvPZM.cpp)
  Added 6 lines; removed 5.
- [src/server/scripts/Pet/pet_generic.cpp](../sources/EsteriaWoW/src/server/scripts/Pet/pet_generic.cpp)
  Added 1 lines; removed 1.
- [src/server/scripts/Spells/spell_generic.cpp](../sources/EsteriaWoW/src/server/scripts/Spells/spell_generic.cpp)
  Added 13 lines; removed 23.
- [src/server/scripts/Spells/spell_quest.cpp](../sources/EsteriaWoW/src/server/scripts/Spells/spell_quest.cpp)
  Added 2 lines; removed 1.
- [src/server/shared/CreatureAppearance.h](../sources/EsteriaWoW/src/server/shared/CreatureAppearance.h)
  Added 98 lines; removed 0.
- [src/server/shared/DataStores/DBCDatabaseLoader.cpp](../sources/EsteriaWoW/src/server/shared/DataStores/DBCDatabaseLoader.cpp)
  Added 11 lines; removed 3.
- [src/server/shared/DataStores/DBCStore.h](../sources/EsteriaWoW/src/server/shared/DataStores/DBCStore.h)
  Added 35 lines; removed 0.
- [src/server/shared/DataStores/DBCStructure.h](../sources/EsteriaWoW/src/server/shared/DataStores/DBCStructure.h)
  Added 36 lines; removed 0.
- [src/server/shared/DataStores/DBCfmt.h](../sources/EsteriaWoW/src/server/shared/DataStores/DBCfmt.h)
  Added 2 lines; removed 0.
- [src/server/shared/EarthenAppearance.h](../sources/EsteriaWoW/src/server/shared/EarthenAppearance.h)
  Added 140 lines; removed 0.
- [src/server/shared/HaranirAppearance.h](../sources/EsteriaWoW/src/server/shared/HaranirAppearance.h)
  Added 209 lines; removed 0.
- [src/server/shared/HighmountainAppearance.h](../sources/EsteriaWoW/src/server/shared/HighmountainAppearance.h)
  Added 180 lines; removed 0.
- [src/server/shared/SharedDefines.h](../sources/EsteriaWoW/src/server/shared/SharedDefines.h)
  Added 189 lines; removed 15.
- [src/server/shared/VulperaAppearance.h](../sources/EsteriaWoW/src/server/shared/VulperaAppearance.h)
  Added 346 lines; removed 0.
- [src/server/shared/enuminfo_SharedDefines.cpp](../sources/EsteriaWoW/src/server/shared/enuminfo_SharedDefines.cpp)
  Added 50 lines; removed 29.
- [src/test/server/game/Combat/FreebornTeamTest.cpp](../sources/EsteriaWoW/src/test/server/game/Combat/FreebornTeamTest.cpp)
  Added 94 lines; removed 0.
- [src/test/server/game/Entities/CollisionDimensionsTest.cpp](../sources/EsteriaWoW/src/test/server/game/Entities/CollisionDimensionsTest.cpp)
  Added 34 lines; removed 0.
- [src/test/server/game/Modules/BrokenRacialsTest.cpp](../sources/EsteriaWoW/src/test/server/game/Modules/BrokenRacialsTest.cpp)
  Added 25 lines; removed 0.
- [src/test/server/game/Spells/VehicleScalingUlduarTest.cpp](../sources/EsteriaWoW/src/test/server/game/Spells/VehicleScalingUlduarTest.cpp)
  Added 60 lines; removed 72.
- [src/tools/mmaps_generator/Config.cpp](../sources/EsteriaWoW/src/tools/mmaps_generator/Config.cpp)
  Added 9 lines; removed 1.
- [src/tools/mmaps_generator/Config.h](../sources/EsteriaWoW/src/tools/mmaps_generator/Config.h)
  Added 2 lines; removed 0.
- [src/tools/mmaps_generator/MapBuilder.cpp](../sources/EsteriaWoW/src/tools/mmaps_generator/MapBuilder.cpp)
  Added 30 lines; removed 0.
- [src/tools/mmaps_generator/mmaps-config.yaml](../sources/EsteriaWoW/src/tools/mmaps_generator/mmaps-config.yaml)
  Added 3 lines; removed 3.
