/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef ESTERIA_HOUSING_HOOKS_H
#define ESTERIA_HOUSING_HOOKS_H

#include "Define.h"
#include <atomic>

class Player;
class Unit;
class WorldPacket;
class WorldSession;

// The only core surface of mod-esteria-housing; the core behaves exactly as stock while a hook is null. Instance is
// set only while EsteriaHousing.Enable = 1. Packet is set whenever the module is compiled in, so a disabled realm can
// answer HELLO with enabled = 0 (without the module the packets are dropped and the client times out).
namespace EsteriaHousingHooks
{
    // CMSG_ESTERIA_HOUSING_* (0x537-0x53D). Null: the packet is dropped, so the client times out and hides housing.
    using PacketHandler = void (*)(WorldSession* session, WorldPacket& packet);
    // MapInstanced::CreateInstanceForPlayer: return the instance ID this player must enter on mapId, or 0 for the
    // stock choice (binds, group). A returned ID that has no live map is created with no save.
    using InstancePicker = uint32 (*)(Player* player, uint32 mapId);

    AC_GAME_API extern std::atomic<PacketHandler> Packet;
    AC_GAME_API extern std::atomic<InstancePicker> Instance;
    // CMSG_GET_MIRRORIMAGE_DATA for a unit that is not a clone: true when the module answered (a housing merchant).
    using MirrorImageData = bool (*)(Player* player, Unit* unit);
    AC_GAME_API extern std::atomic<MirrorImageData> MirrorImage;
}

#endif
