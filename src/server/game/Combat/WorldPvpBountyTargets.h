/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information.
 * Distributed under the GNU General Public License, version 2 or later.
 */

#ifndef AZEROTHCORE_WORLD_PVP_BOUNTY_TARGETS_H
#define AZEROTHCORE_WORLD_PVP_BOUNTY_TARGETS_H

#include "DatabaseEnvFwd.h"
#include "Define.h"
#include <optional>

namespace Acore::WorldPvp
{
[[nodiscard]] AC_GAME_API bool CanHuntBountyTarget(uint32 targetGuid, uint32 hunterAccount);
[[nodiscard]] bool HasActiveOrPendingBounty(uint32 targetGuid);
[[nodiscard]] std::optional<uint64> ActiveBountyCopper(uint32 targetGuid);
AC_GAME_API void InvalidateBountyTarget(uint32 targetGuid);
void RefreshBountyTargets(QueryCallbackProcessor& processor);
void ProcessBountyRefunds(QueryCallbackProcessor& processor);
}

#endif
