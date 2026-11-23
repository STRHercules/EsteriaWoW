/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information.
 * Distributed under the GNU General Public License, version 2 or later.
 */

#include "WorldPvpWilderness.h"
#include "AreaDefines.h"
#include "Common.h"
#include "CryptoHash.h"
#include "DBCStores.h"
#include "Log.h"
#include "Map.h"
#include "Object.h"
#include "SharedDefines.h"
#include "StringFormat.h"
#include "World.h"
#include "WorldPvpRules.h"
#include "WorldSessionMgr.h"
#include <algorithm>
#include <array>
#include <atomic>
#include <mutex>
#include <unordered_set>
#include <utility>

namespace
{
constexpr std::array<uint32, 4> WildernessZones = { AREA_ZUL_DRAK, AREA_THE_STORM_PEAKS, AREA_ICECROWN,
    AREA_SHOLAZAR_BASIN };
std::atomic<uint32> ActiveWildernessMask{0};
}

bool Acore::WorldPvp::ClaimWildernessArenaReward(uint32 killerAccount, uint32 victimAccount, uint64 day)
{
    if (killerAccount == victimAccount)
        return false;

    static std::mutex mutex;
    static uint64 rewardDay = 0;
    // shortcut: the daily limit resets on restart, persist it before public rollout
    static std::unordered_set<uint64> rewardedPairs;
    std::lock_guard lock(mutex);
    if (day < rewardDay)
        return false;

    if (day > rewardDay)
    {
        rewardedPairs.clear();
        rewardDay = day;
    }

    auto const [first, second] = std::minmax(killerAccount, victimAccount);
    return rewardedPairs.insert((uint64(first) << 32) | second).second;
}

uint64 Acore::WorldPvp::WildernessWindow(uint64 seconds, uint32 hours)
{
    return seconds / (uint64(std::max(hours, 1u)) * HOUR);
}

uint32 Acore::WorldPvp::WildernessRotationMask(uint32 realmId, uint64 window, uint32 zoneCount)
{
    if (!zoneCount)
        return 0;

    using RankedZone = std::pair<Acore::Crypto::SHA256::Digest, std::size_t>;
    std::array<RankedZone, WildernessZones.size()> ranked{};
    for (std::size_t index = 0; index < ranked.size(); ++index)
        ranked[index] = { Acore::Crypto::SHA256::GetDigestOf(
            Acore::StringFormat("{}:{}:{}", realmId, window, WildernessZones[index])), index };

    std::sort(ranked.begin(), ranked.end());
    uint32 mask = 0;
    for (std::size_t index = 0; index < std::min<std::size_t>(zoneCount, ranked.size()); ++index)
        mask |= 1u << ranked[index].second;

    return mask;
}

bool Acore::WorldPvp::IsWildernessLocation(WorldObject const& object)
{
    uint32 const mask = ActiveWildernessMask.load(std::memory_order_relaxed);
    Map const* map = object.FindMap();
    if (!mask || !map || !map->IsWorldMap())
        return false;

    uint32 const zone = object.GetZoneId();
    for (std::size_t index = 0; index < WildernessZones.size(); ++index)
        if ((mask & (1u << index)) && zone == WildernessZones[index])
        {
            AreaTableEntry const* area = sAreaTableStore.LookupEntry(object.GetAreaId());
            return area && !area->IsSanctuary() && !IsCapital(area);
        }

    return false;
}

std::vector<uint32> Acore::WorldPvp::ActiveWildernessZones()
{
    uint32 const mask = ActiveWildernessMask.load(std::memory_order_relaxed);
    std::vector<uint32> zones;
    for (std::size_t index = 0; index < WildernessZones.size(); ++index)
        if (mask & (1u << index))
            zones.push_back(WildernessZones[index]);
    return zones;
}

uint64 Acore::WorldPvp::SecondsUntilWildernessRotation(uint64 seconds)
{
    uint64 const length = uint64(std::max(sWorld->getIntConfig(CONFIG_ESTERIA_WILDERNESS_HOURS), 1u)) * HOUR;
    return length - seconds % length;
}

void Acore::WorldPvp::UpdateWildernessRotation(uint64 seconds, uint32 realmId)
{
    static uint64 previousWindow = 0;
    static uint32 previousHours = 0;
    static uint32 previousCount = 0;
    uint32 const hours = std::max(sWorld->getIntConfig(CONFIG_ESTERIA_WILDERNESS_HOURS), 1u);
    uint32 const count = sWorld->getBoolConfig(CONFIG_ESTERIA_WORLD_PVP) ?
        sWorld->getIntConfig(CONFIG_ESTERIA_WILDERNESS_ZONE_COUNT) : 0;
    uint64 const window = WildernessWindow(seconds, hours);
    if (window == previousWindow && hours == previousHours && count == previousCount)
        return;

    previousWindow = window;
    previousHours = hours;
    previousCount = count;
    uint32 const mask = WildernessRotationMask(realmId, window, count);
    if (mask == ActiveWildernessMask.exchange(mask, std::memory_order_relaxed))
        return;

    std::string zones;
    for (std::size_t index = 0; index < WildernessZones.size(); ++index)
    {
        if (!(mask & (1u << index)))
            continue;

        AreaTableEntry const* area = sAreaTableStore.LookupEntry(WildernessZones[index]);
        char const* name = area ? area->area_name[LOCALE_enUS] : nullptr;
        if (!zones.empty())
            zones += ", ";
        zones += name && *name ? std::string(name) : std::to_string(WildernessZones[index]);
    }

    std::string const message = mask ?
        Acore::StringFormat("Active Wilderness zones: {}", zones) : "The Wilderness rotation has ended.";
    LOG_INFO("server.loading", "{}", message);
    sWorldSessionMgr->SendServerMessage(SERVER_MSG_STRING, message);
}
