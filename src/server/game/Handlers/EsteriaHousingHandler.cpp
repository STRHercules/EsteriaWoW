/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#include "EsteriaHousingHooks.h"
#include "WorldPacket.h"
#include "WorldSession.h"

namespace EsteriaHousingHooks
{
    std::atomic<PacketHandler> Packet{ nullptr };
    std::atomic<InstancePicker> Instance{ nullptr };
std::atomic<MirrorImageData> MirrorImage{ nullptr };
}

void WorldSession::HandleEsteriaHousingOpcode(WorldPacket& recvData)
{
    if (auto handler = EsteriaHousingHooks::Packet.load())
        handler(this, recvData);
    else
        recvData.rfinish();
}
