/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program. If not, see <http://www.gnu.org/licenses/>.
 */

// Character hot-swap, phase 1 (wowdecomp docs/character-hot-swap-plan.md): a validated, cooldown-stamped instant
// logout. The client then logs the target in through the normal CMSG_PLAYER_LOGIN, which is marked as a swap login.
//   CMSG_ESTERIA_SWAP_REQUEST: guid(8)
//   SMSG_ESTERIA_SWAP_RESULT:  guid(8) result(u8) detail(u8) cooldownMs(u32)
//   CMSG_ESTERIA_SWAP_ROSTER_REQUEST: empty
//   SMSG_ESTERIA_SWAP_ROSTER:  unsafe(u8) cooldownMs(u32) count(u8), then per character:
//                              guid(8) name(cstring) race(u8) class(u8) gender(u8) level(u8) map(u32) zone(u32) zoneName(cstring) flags(u8)

#include "CharacterPackets.h"
#include "Config.h"
#include "GameTime.h"
#include "Group.h"
#include "DBCStores.h"
#include "DatabaseEnv.h"
#include "LFGMgr.h"
#include "Log.h"
#include "Player.h"
#include "StringFormat.h"
#include "TC9Sidecar.h"
#include "WorldPacket.h"
#include "WorldSession.h"
#include "WorldSessionMgr.h"

namespace
{
    enum SwapResult : uint8
    {
        SWAP_OK = 0,
        SWAP_NOT_YOURS = 1,
        SWAP_COOLDOWN = 2,
        SWAP_UNSAFE = 3,
        SWAP_TARGET_ONLINE = 4,
        SWAP_DISABLED = 5,
        SWAP_INTERNAL = 6,
    };

    // Detail byte of SWAP_UNSAFE, and the roster's "unsafe" byte.
    enum SwapUnsafe : uint8
    {
        UNSAFE_NONE = 0,
        UNSAFE_COMBAT = 1,
        UNSAFE_CASTING = 2,
        UNSAFE_DEAD = 3,
        UNSAFE_INSTANCE = 4,
        UNSAFE_QUEUED = 5,
        UNSAFE_MOVING = 6,   // teleport, taxi, vehicle, falling
        UNSAFE_BUSY = 7,     // duel, trade, loot
        UNSAFE_BIND = 8,
        UNSAFE_RAID = 9,
    };

    enum RosterFlags : uint8
    {
        ROSTER_ACTIVE = 0x01,
        ROSTER_DEAD = 0x02,
    };

    bool SwapEnabled()
    {
        // shortcut: refuses swapping with several character DB workers, since the logout save and the target's
        // login holder are then not ordered (plan §6.3). Add the save-pending lock if WorkerThreads ever goes above 1.
        return sConfigMgr->GetOption<bool>("Esteria.Swap.Enable", false)
            && !sToCloud9Sidecar->ClusterModeEnabled()
            && sConfigMgr->GetOption<int32>("CharacterDatabase.WorkerThreads", 1) <= 1;
    }

    uint8 UnsafeReason(Player* player)
    {
        if (player->IsGameMaster())
            return UNSAFE_NONE;
        if (player->IsInCombat())
            return UNSAFE_COMBAT;
        if (player->IsNonMeleeSpellCast(false))
            return UNSAFE_CASTING;
        if (!player->IsAlive() || player->HasPlayerFlag(PLAYER_FLAGS_GHOST) || player->HasSpiritOfRedemptionAura())
            return UNSAFE_DEAD;
        if (player->GetMap()->Instanceable() || player->InBattleground())
            return UNSAFE_INSTANCE;
        if (player->InBattlegroundQueue() || sLFGMgr->GetState(player->GetGUID()) != lfg::LFG_STATE_NONE)
            return UNSAFE_QUEUED;
        if (player->IsBeingTeleported() || player->IsInFlight() || player->GetVehicle()
            || player->m_movementInfo.HasMovementFlag(MOVEMENTFLAG_FALLING | MOVEMENTFLAG_FALLING_FAR))
            return UNSAFE_MOVING;
        if (player->duel || player->GetTradeData() || player->GetLootGUID())
            return UNSAFE_BUSY;
        if (player->HasPendingBind())
            return UNSAFE_BIND;
        if (player->GetGroup() && player->GetGroup()->isRaidGroup())
            return UNSAFE_RAID;
        return UNSAFE_NONE;
    }
}

uint32 WorldSession::GetSwapCooldownMs() const
{
    Milliseconds const cooldown = Seconds(sConfigMgr->GetOption<uint32>("Esteria.Swap.CooldownSeconds", 30));
    Milliseconds const elapsed = GameTime::GetGameTimeMS() - _swapTime;
    return _swapTime == 0ms || elapsed >= cooldown ? 0 : uint32((cooldown - elapsed).count());
}

void WorldSession::HandleEsteriaSwapRequestOpcode(WorldPacket& recvData)
{
    uint64 rawGuid;
    recvData >> rawGuid;

    ObjectGuid const target(rawGuid);
    Player* player = GetPlayer();

    auto reply = [&](uint8 result, uint8 detail = 0)
    {
        LOG_INFO("entities.player", "Swap: account {} from {} to {} result {} detail {}", GetAccountId(),
            player ? player->GetGUID().ToString() : "none", target.ToString(), result, detail);
        WorldPacket data(SMSG_ESTERIA_SWAP_RESULT, 8 + 1 + 1 + 4);
        data << rawGuid << result << detail << GetSwapCooldownMs();
        SendPacket(&data);
    };

    if (!player || !player->IsInWorld() || PlayerLogout())
        return;

    if (!SwapEnabled())
        return reply(SWAP_DISABLED);

    if (!target.IsPlayer() || target == player->GetGUID() || !IsLegitCharacterForAccount(target))
        return reply(SWAP_NOT_YOURS);

    if (GetSwapCooldownMs())
        return reply(SWAP_COOLDOWN);

    if (uint8 unsafe = UnsafeReason(player))
        return reply(SWAP_UNSAFE, unsafe);

    // Another account's offline session holding it would refuse the login with DuplicateCharacter.
    if (WorldSession* sess = sWorldSessionMgr->FindOfflineSessionForCharacterGUID(target.GetCounter()))
        if (sess->GetAccountId() != GetAccountId())
            return reply(SWAP_TARGET_ONLINE);

    _swapTime = GameTime::GetGameTimeMS();
    _swapTarget = target;
    reply(SWAP_OK);

    // Same order as the instant logout in HandleLogoutRequestOpcode; the client re-enters from SMSG_LOGOUT_COMPLETE.
    WorldPackets::Character::LogoutResponse logoutResponse;
    logoutResponse.LogoutResult = 0;
    logoutResponse.Instant = true;
    SendPacket(logoutResponse.Write());
    LogoutPlayer(true);
}

void WorldSession::HandleEsteriaSwapRosterRequestOpcode(WorldPacket& /*recvData*/)
{
    Player* player = GetPlayer();
    if (!player)
        return;

    uint8 const unsafe = SwapEnabled() ? UnsafeReason(player) : UNSAFE_NONE;
    ObjectGuid const active = player->GetGUID();
    uint32 const activeMap = player->GetMapId(), activeZone = player->GetZoneId();
    bool const activeDead = !player->IsAlive() || player->HasPlayerFlag(PLAYER_FLAGS_GHOST);

    std::string const sql = Acore::StringFormat("SELECT guid, name, race, class, gender, level, map, zone, "
        "(health = 0 OR (playerFlags & {}) <> 0) FROM characters WHERE account = {} AND deleteInfos_Account IS NULL "
        "ORDER BY guid LIMIT 255", uint32(PLAYER_FLAGS_GHOST), GetAccountId());

    _queryProcessor.AddCallback(CharacterDatabase.AsyncQuery(sql).WithCallback(
        [this, unsafe, active, activeMap, activeZone, activeDead](QueryResult result)
        {
            WorldPacket data(SMSG_ESTERIA_SWAP_ROSTER, 64);
            data << unsafe << GetSwapCooldownMs();
            size_t const countPos = data.wpos();
            data << uint8(0);
            uint8 count = 0;
            if (result)
            {
                do
                {
                    Field* fields = result->Fetch();
                    ObjectGuid const guid = ObjectGuid::Create<HighGuid::Player>(fields[0].Get<uint32>());
                    bool const isActive = guid == active;
                    uint8 flags = (isActive ? ROSTER_ACTIVE : 0)
                        | ((isActive ? activeDead : fields[8].Get<uint32>() != 0) ? ROSTER_DEAD : 0);
                    data << guid.GetRawValue() << fields[1].Get<std::string>() << fields[2].Get<uint8>()
                        << fields[3].Get<uint8>() << fields[4].Get<uint8>() << fields[5].Get<uint8>();
                    uint32 const zone = isActive ? activeZone : fields[7].Get<uint16>();
                    AreaTableEntry const* area = sAreaTableStore.LookupEntry(zone);
                    data << (isActive ? activeMap : uint32(fields[6].Get<uint16>())) << zone
                        << (area ? area->area_name[GetSessionDbcLocale()] : "") << flags;
                    ++count;
                } while (result->NextRow());
            }
            data.put<uint8>(countPos, count);
            SendPacket(&data);
        }));
}
