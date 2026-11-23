/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information.
 * Distributed under the GNU General Public License, version 2 or later.
 */

#ifndef AC_WORLD_PVP_EAR_H
#define AC_WORLD_PVP_EAR_H

#include "Define.h"
#include <array>

class Player;
class ObjectGuid;

namespace Acore::WorldPvp
{
constexpr uint32 EarTrophyItem = 9510710;
constexpr uint32 FenceEarPrice = 10000;
constexpr uint32 UnderbellyFenceEntry = 9510704;

struct EarReward
{
    uint32 entry;
    uint8 cost;
};

inline constexpr std::array<EarReward, 4> EarRewards = {{
    {9510711, 5}, {9510712, 10}, {901211, 40}, {1001933, 40}
}};
inline constexpr EarReward FencePickpocketTool = {9510713, 3};
inline constexpr EarReward FenceStunPowder = {951076, 1};
inline constexpr uint32 FenceStunSpell = 951070;

void AwardEarTrophy(Player& killer, Player const& victim);
[[nodiscard]] AC_GAME_API bool CanBuyEarRewards(Player const& player);
AC_GAME_API void BuyEarReward(Player& buyer, uint32 entry);
[[nodiscard]] AC_GAME_API bool CanUseEarFence(Player const& player);
[[nodiscard]] AC_GAME_API bool CanBuyFenceTool(Player const& player);
void SellEarToFence(Player& seller, ObjectGuid itemGuid);
}

#endif
