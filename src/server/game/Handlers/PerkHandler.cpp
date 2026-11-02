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

// Paths of Fate, phase 0: points, purchases, respecs and the ledger (rules in PerkRules.h, wire in PerkWire.h).
// The server holds the only real state; the client asks for a snapshot and redraws from the reply.

#include "Config.h"
#include "DatabaseEnv.h"
#include "GameTime.h"
#include "Log.h"
#include "PerkRules.h"
#include "Player.h"
#include "WorldPacket.h"
#include "WorldSession.h"

namespace
{
    using namespace EsteriaPerkWire;

    enum AuditAction : uint8
    {
        AUDIT_PURCHASE = 1,
        AUDIT_RESPEC = 2,
        AUDIT_REPAIR = 3,
    };

    bool PerksEnabled()
    {
        return sConfigMgr->GetOption<bool>("Esteria.Perks.Enable", false);
    }

    EsteriaPerks::Options PerkOptions()
    {
        return { sConfigMgr->GetOption<bool>("Esteria.Perks.SellPlanned", false) };
    }

    void Audit(CharacterDatabaseTransaction trans, Player const* player, uint8 action, uint8 perk, uint8 rank,
        uint32 gold)
    {
        CharacterDatabasePreparedStatement* stmt = CharacterDatabase.GetPreparedStatement(CHAR_INS_PERK_AUDIT);
        stmt->SetData(0, player->GetGUID().GetCounter());
        stmt->SetData(1, uint32(GameTime::GetGameTime().count()));
        stmt->SetData(2, action);
        stmt->SetData(3, perk);
        stmt->SetData(4, rank);
        stmt->SetData(5, player->GetLevel());
        stmt->SetData(6, EsteriaPerks::Spent(player->GetEsteriaPerkRanks()));
        stmt->SetData(7, gold);
        trans->Append(stmt);
    }

    Result RespecLock(Player const* player)
    {
        if (!EsteriaPerks::Spent(player->GetEsteriaPerkRanks()))
            return Nothing;
        if (player->IsInCombat()
            || !(player->HasRestFlag(REST_FLAG_IN_TAVERN) || player->HasRestFlag(REST_FLAG_IN_CITY)))
            return Place;
        return Ok;
    }

    void SendResult(WorldSession* session, uint8 action, uint8 perk, uint8 rank, uint8 result)
    {
        WorldPacket data(SMSG_ESTERIA_PERK_RESULT, 4);
        data << action << perk << rank << result;
        session->SendPacket(&data);
    }
}

void Player::LoadEsteriaPerks(PreparedQueryResult profile, PreparedQueryResult perks)
{
    _esteriaPerks = {};
    _esteriaTrait = 0;
    _esteriaRespecs = 0;
    if (profile)
    {
        _esteriaTrait = (*profile)[0].Get<uint8>();
        _esteriaRespecs = (*profile)[1].Get<uint8>();
    }
    if (perks)
    {
        do
        {
            Field* fields = perks->Fetch();
            int const index = EsteriaPerks::IndexOf(fields[0].Get<uint8>());
            if (index >= 0)
                _esteriaPerks[index] = std::min(fields[1].Get<uint8>(), EsteriaPerks::Cards[index].maxRank);
        } while (perks->NextRow());
    }

    // A level drop (GM command, custom level transitions) can leave more spent than earned: refund everything.
    if (EsteriaPerks::Spent(_esteriaPerks) > EsteriaPerks::Earned(GetLevel()))
    {
        LOG_INFO("entities.player", "Perks: {} spent {} above level {}'s budget, refunded", GetGUID().ToString(),
            EsteriaPerks::Spent(_esteriaPerks), GetLevel());
        ResetEsteriaPerks(AUDIT_REPAIR, false, 0);
    }
}

uint8 Player::GetEsteriaPerkRank(uint8 perk) const
{
    int const index = EsteriaPerks::IndexOf(perk);
    return index >= 0 && PerksEnabled() ? _esteriaPerks[index] : 0;
}

void Player::ResetEsteriaPerks(uint8 auditAction, bool countRespec, uint32 gold)
{
    _esteriaPerks = {};
    CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
    Audit(trans, this, auditAction, 0, 0, gold);

    CharacterDatabasePreparedStatement* stmt = CharacterDatabase.GetPreparedStatement(CHAR_DEL_PERKS);
    stmt->SetData(0, GetGUID().GetCounter());
    trans->Append(stmt);

    if (countRespec && _esteriaRespecs < 255)
    {
        ++_esteriaRespecs;
        stmt = CharacterDatabase.GetPreparedStatement(CHAR_UPD_PERK_RESPECS);
        stmt->SetData(0, GetGUID().GetCounter());
        stmt->SetData(1, _esteriaRespecs);
        trans->Append(stmt);
    }
    CharacterDatabase.CommitTransaction(trans);
}

void Player::SendEsteriaPerkSnapshot()
{
    EsteriaPerks::Options const options = PerkOptions();
    uint8 const level = GetLevel();
    uint8 const classId = getClass();

    WorldPacket data(SMSG_ESTERIA_PERK_SNAPSHOT, 16 + EsteriaPerks::CardCount * 8);
    data << Proto << EsteriaPerks::Earned(level) << EsteriaPerks::Spent(_esteriaPerks) << _esteriaTrait
        << _esteriaRespecs << EsteriaPerks::RespecCost(_esteriaRespecs, level);
    Result respec = RespecLock(this);
    if (respec == Ok && !HasEnoughMoney(EsteriaPerks::RespecCost(_esteriaRespecs, level)))
        respec = Gold;
    data << uint8(respec);

    size_t const countPos = data.wpos();
    data << uint8(0);
    uint8 count = 0;
    for (size_t i = 0; i < EsteriaPerks::CardCount; ++i)
    {
        EsteriaPerks::Card const& card = EsteriaPerks::Cards[i];
        if (!EsteriaPerks::ClassCanUse(card, classId))
            continue;
        uint8 const rank = _esteriaPerks[i];
        uint8 const lock = EsteriaPerks::Check(_esteriaPerks, int(i), rank + 1, level, classId, options);
        data << card.id << card.path << card.tier << rank << card.maxRank << EsteriaPerks::Cost(card) << lock
            << uint8(card.implemented ? 0 : CardPlanned);
        ++count;
    }
    data.put<uint8>(countPos, count);
    GetSession()->SendPacket(&data);
}

void WorldSession::HandleEsteriaPerkSnapshotRequestOpcode(WorldPacket& recvData)
{
    uint8 proto;
    recvData >> proto;

    Player* player = GetPlayer();
    if (!player)
        return;
    if (proto != Proto)
        return SendResult(this, ActionSnapshot, 0, 0, Version);
    if (!PerksEnabled())
        return SendResult(this, ActionSnapshot, 0, 0, Disabled);
    player->SendEsteriaPerkSnapshot();
}

void WorldSession::HandleEsteriaPerkPurchaseOpcode(WorldPacket& recvData)
{
    uint8 perk, rank;
    recvData >> perk >> rank;

    Player* player = GetPlayer();
    if (!player)
        return;
    if (!PerksEnabled())
        return SendResult(this, ActionPurchase, perk, rank, Disabled);

    int const index = EsteriaPerks::IndexOf(perk);
    Result const result = EsteriaPerks::Check(player->GetEsteriaPerkRanks(), index, rank, player->GetLevel(),
        player->getClass(), PerkOptions());
    LOG_INFO("entities.player", "Perks: {} buys perk {} rank {}: result {}", player->GetGUID().ToString(), perk,
        rank, uint32(result));

    if (result == Ok)
    {
        // The rank changes here, on the world thread, before the next request can be read: a double click is
        // refused by Check as the wrong rank.
        player->SetEsteriaPerkRank(size_t(index), rank);

        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        CharacterDatabasePreparedStatement* stmt = CharacterDatabase.GetPreparedStatement(CHAR_REP_PERK);
        stmt->SetData(0, player->GetGUID().GetCounter());
        stmt->SetData(1, perk);
        stmt->SetData(2, rank);
        trans->Append(stmt);
        Audit(trans, player, AUDIT_PURCHASE, perk, rank, 0);
        CharacterDatabase.CommitTransaction(trans);
    }

    SendResult(this, ActionPurchase, perk, rank, result);
    player->SendEsteriaPerkSnapshot();
}

void WorldSession::HandleEsteriaPerkRespecOpcode(WorldPacket& /*recvData*/)
{
    Player* player = GetPlayer();
    if (!player)
        return;
    if (!PerksEnabled())
        return SendResult(this, ActionRespec, 0, 0, Disabled);

    uint32 const cost = EsteriaPerks::RespecCost(player->GetEsteriaPerkRespecs(), player->GetLevel());
    Result result = RespecLock(player);
    if (result == Ok && !player->HasEnoughMoney(cost))
        result = Gold;
    LOG_INFO("entities.player", "Perks: {} respec for {} copper: result {}", player->GetGUID().ToString(), cost,
        uint32(result));

    if (result == Ok)
    {
        player->ModifyMoney(-int32(cost));
        player->ResetEsteriaPerks(AUDIT_RESPEC, true, cost);
    }

    SendResult(this, ActionRespec, 0, 0, result);
    player->SendEsteriaPerkSnapshot();
}
