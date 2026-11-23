/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information.
 * Distributed under the GNU General Public License, version 2 or later.
 */

#ifndef AZEROTHCORE_WORLD_PVP_PICKPOCKET_H
#define AZEROTHCORE_WORLD_PVP_PICKPOCKET_H

#include "Define.h"

class ChatHandler;
class ObjectGuid;
class Player;

namespace Acore::WorldPvp
{
[[nodiscard]] bool CanUsePlayerPickpocket(Player const& player);
AC_GAME_API bool TryPlayerPickpocket(ChatHandler& handler, ObjectGuid victimGuid);
}

#endif
