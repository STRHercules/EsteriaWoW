/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 */

#ifndef AZEROTHCORE_WORLD_PVP_RULES_H
#define AZEROTHCORE_WORLD_PVP_RULES_H

#include "DBCStores.h"
#include "SharedDefines.h"
#include <algorithm>
#include <optional>
#include <string>

class Player;

namespace Acore::WorldPvp
{
inline std::string const CrimeSettingsSource = "core.world_pvp_crime";
inline constexpr uint32 MinimumPlayerBounty = 100 * GOLD;
inline constexpr uint32 BountyCollectorEntry = 9510700;

[[nodiscard]] AC_GAME_API bool CanUseBountyEscrow();
[[nodiscard]] AC_GAME_API uint32 WalletRoom(Player const& player);

constexpr uint32 PickpocketGoldAmount(uint32 victimBalance, uint32 walletRoom)
{
    return std::min({ 5u * GOLD, victimBalance / 100, walletRoom });
}

enum class BountyEscrowState : int8
{
    Missing = -1,
    Pending,
    Funded,
    Refunded,
    Claimed,
    Redeemed,
    Expired,
    RefundQueued
};

constexpr bool IsBountyWalletChangeCommitted(BountyEscrowState expected, BountyEscrowState stored)
{
    // Settlement can advance the receipt between funding and the wallet readback.
    return stored == expected || (expected == BountyEscrowState::Funded &&
        (stored == BountyEscrowState::Claimed || stored == BountyEscrowState::Redeemed ||
         stored == BountyEscrowState::RefundQueued || stored == BountyEscrowState::Refunded));
}

constexpr bool MeetsPlayerBountyMinimum(uint32 copper)
{
    return copper >= MinimumPlayerBounty;
}

enum CrimeSetting : uint8
{
    Notoriety,
    WantedUntil
};

inline bool IsCapital(AreaTableEntry const* area)
{
    if (!area)
        return false;

    if ((area->flags & AREA_FLAG_CAPITAL) || area->ID == AREA_DALARAN)
        return true;

    AreaTableEntry const* zone = area->zone ? sAreaTableStore.LookupEntry(area->zone) : nullptr;
    return zone && ((zone->flags & AREA_FLAG_CAPITAL) || zone->ID == AREA_DALARAN);
}

constexpr bool AreHostile(
    bool firstFlagged, bool secondFlagged, bool freebornPair, bool protectedPair, bool bothInWilderness = false)
{
    return !protectedPair && (bothInWilderness || freebornPair || (firstFlagged && secondFlagged));
}

constexpr std::optional<bool> BountyAttackOverride(
    bool ordinaryHostility, bool attackerAuthorized, bool targetAuthorized, bool areaEffect)
{
    if (attackerAuthorized && !areaEffect)
        return true;

    if (!ordinaryHostility && (attackerAuthorized || targetAuthorized))
        return false;

    return std::nullopt;
}

constexpr bool IsMurder(bool selfDefense, bool victimWanted, bool bothInWilderness = false)
{
    return !selfDefense && !victimWanted && !bothInWilderness;
}
}

#endif
