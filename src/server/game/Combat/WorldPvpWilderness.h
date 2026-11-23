/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information.
 * Distributed under the GNU General Public License, version 2 or later.
 */

#ifndef AZEROTHCORE_WORLD_PVP_WILDERNESS_H
#define AZEROTHCORE_WORLD_PVP_WILDERNESS_H

#include "Define.h"
#include <limits>
#include <vector>

class WorldObject;

namespace Acore::WorldPvp
{
[[nodiscard]] AC_GAME_API uint64 WildernessWindow(uint64 seconds, uint32 hours);
[[nodiscard]] AC_GAME_API uint32 WildernessRotationMask(uint32 realmId, uint64 window, uint32 zoneCount);
[[nodiscard]] bool IsWildernessLocation(WorldObject const& object);
[[nodiscard]] AC_GAME_API std::vector<uint32> ActiveWildernessZones();
[[nodiscard]] AC_GAME_API uint64 SecondsUntilWildernessRotation(uint64 seconds);
void UpdateWildernessRotation(uint64 seconds, uint32 realmId);

constexpr uint32 WildernessPveBonusPct = 25;
constexpr uint32 WildernessWeaponDamageBonusPct = 15;

[[nodiscard]] constexpr uint32 AddWildernessBonus(uint32 amount, uint32 bonusPct)
{
    uint64 const increased = uint64(amount) + uint64(amount) * bonusPct / 100;
    constexpr uint32 limit = std::numeric_limits<uint32>::max();
    return increased > limit ? limit : uint32(increased);
}

[[nodiscard]] AC_GAME_API bool ClaimWildernessArenaReward(uint32 killerAccount, uint32 victimAccount, uint64 day);
}

#endif
