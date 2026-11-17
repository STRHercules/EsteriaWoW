/*
 * The only core surface of mod-esteria-garrison. Hooks stay null until the module enables itself, so a realm
 * without the module behaves as stock.
 */

#ifndef ESTERIA_GARRISON_HOOKS_H
#define ESTERIA_GARRISON_HOOKS_H

#include "Define.h"
#include <atomic>

class WorldPacket;
class WorldSession;
class Player;

namespace EsteriaGarrisonHooks
{
    // CMSG_ESTERIA_GARRISON_* (0x54A, 0x54C). Null: the packet is dropped.
    using PacketHandler = void (*)(WorldSession* session, WorldPacket& packet);
    // MapInstanced::CreateInstanceForPlayer: the owner's garrison instance for this map, or 0 for the stock choice.
    using InstancePicker = uint32 (*)(Player* player, uint32 mapId);

    AC_GAME_API extern std::atomic<PacketHandler> Packet;
    AC_GAME_API extern std::atomic<InstancePicker> Instance;
}

#endif
