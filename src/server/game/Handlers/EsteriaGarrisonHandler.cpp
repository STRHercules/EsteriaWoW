#include "EsteriaGarrisonHooks.h"
#include "WorldPacket.h"
#include "WorldSession.h"

namespace EsteriaGarrisonHooks
{
    std::atomic<PacketHandler> Packet{ nullptr };
    std::atomic<InstancePicker> Instance{ nullptr };
}

void WorldSession::HandleEsteriaGarrisonOpcode(WorldPacket& recvData)
{
    if (auto handler = EsteriaGarrisonHooks::Packet.load())
        handler(this, recvData);
    else
        recvData.rfinish();
}
