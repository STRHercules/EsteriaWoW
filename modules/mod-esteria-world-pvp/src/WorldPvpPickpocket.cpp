/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information.
 * Distributed under the GNU General Public License, version 2 or later.
 */

#include "Chat.h"
#include "CommandScript.h"
#include "Player.h"
#include "RBAC.h"
#include "WorldPvpPickpocket.h"
#include "WorldSession.h"

using namespace Acore::ChatCommands;

namespace
{
class world_pvp_pickpocket_commandscript final : public CommandScript
{
public:
    world_pvp_pickpocket_commandscript() : CommandScript("world_pvp_pickpocket_commandscript") { }

    ChatCommandTable GetCommands() const override
    {
        return { { "pickpocket", HandlePickpocket, rbac::RBAC_PERM_COMMAND_DEV, Console::No } };
    }

private:
    static bool HandlePickpocket(ChatHandler* handler)
    {
        Player const* selected = handler->GetSession()->GetPlayer()->GetSelectedPlayer();
        return Acore::WorldPvp::TryPlayerPickpocket(*handler, selected ? selected->GetGUID() : ObjectGuid::Empty);
    }
};
}

void AddWorldPvpPickpocketCommands()
{
    new world_pvp_pickpocket_commandscript();
}
