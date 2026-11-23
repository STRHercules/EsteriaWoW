/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information.
 * Distributed under the GNU General Public License, version 2 or later.
 */

#include "WorldPvpBountyTargets.h"
#include "DatabaseEnv.h"
#include "GameTime.h"
#include "Mail.h"
#include "MailMgr.h"
#include "ObjectAccessor.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "WorldPvpRules.h"
#include <algorithm>
#include <mutex>
#include <shared_mutex>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

namespace
{
using SponsorAccounts = std::unordered_map<uint32, uint64>;
struct TargetBounties
{
    SponsorAccounts sponsors;
    std::vector<std::pair<uint64, uint64>> contributions;
};
using BountyTargets = std::unordered_map<uint32, TargetBounties>;

std::shared_mutex BountyMutex;
BountyTargets ActiveBountyTargets;
std::unordered_set<uint32> PendingBountyTargets;
uint64 BountyRevision = 1;
uint64 LoadedBountyRevision = 0;
bool BountyRefreshInFlight = false;
Milliseconds NextBountyRefresh{};

constexpr char RefundSubject[] = "Player bounty refund";

void SettleBountyRefund(uint32 sponsor, uint64 id, uint32 copper, uint32 account)
{
    using namespace Acore::WorldPvp;
    Player* player = ObjectAccessor::FindConnectedPlayer(ObjectGuid::Create<HighGuid::Player>(sponsor));
    CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
    if (player && !player->GetDigitalInventory().Failed() && copper <= WalletRoom(*player))
    {
        uint32 const balance = player->GetMoney() + copper;
        auto* credit = CharacterDatabase.GetPreparedStatement(CHAR_CREDIT_WORLD_PVP_REFUND_WALLET);
        credit->SetData(0, balance);
        credit->SetData(1, sponsor);
        credit->SetData(2, id);
        credit->SetData(3, account);
        trans->Append(credit);
        if (!CharacterDatabase.AsyncCommitTransaction(trans).m_future.get())
            return;

        auto* check = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_BOUNTY_STATE);
        check->SetData(0, sponsor);
        check->SetData(1, id);
        check->SetData(2, account);
        PreparedQueryResult result = CharacterDatabase.Query(check);
        if (!result)
            player->GetDigitalInventory().DisconnectOnPersistenceFailure("Bounty refund could not be verified.");
        else if (result->Fetch()[0].Get<int64>() == static_cast<int8>(BountyEscrowState::Refunded))
            player->SetMoney(balance);
        return;
    }

    uint32 const mailId = sObjectMgr->GenerateMailID();
    uint32 const now = GameTime::GetGameTime().count();
    uint32 const expires = now + 30 * DAY;
    auto* reserve = CharacterDatabase.GetPreparedStatement(CHAR_RESERVE_WORLD_PVP_REFUND_MAIL);
    reserve->SetData(0, mailId);
    reserve->SetData(1, sponsor);
    reserve->SetData(2, id);
    trans->Append(reserve);

    auto* send = CharacterDatabase.GetPreparedStatement(CHAR_INS_WORLD_PVP_REFUND_MAIL);
    send->SetData(0, uint8(MAIL_CREATURE));
    send->SetData(1, uint8(MAIL_STATIONERY_DEFAULT));
    send->SetData(2, BountyCollectorEntry);
    send->SetData(3, std::string(RefundSubject));
    send->SetData(4, expires);
    send->SetData(5, now);
    send->SetData(6, uint8(MAIL_CHECK_MASK_COPIED));
    send->SetData(7, sponsor);
    send->SetData(8, id);
    send->SetData(9, mailId);
    trans->Append(send);
    if (!CharacterDatabase.AsyncCommitTransaction(trans).m_future.get())
        return;

    auto* check = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_REFUND_MAIL);
    check->SetData(0, mailId);
    check->SetData(1, sponsor);
    if (!CharacterDatabase.Query(check))
        return;

    sMailMgr->OnMailSent(sponsor);
    if (player)
    {
        auto* mail = new Mail();
        mail->messageID = mailId;
        mail->messageType = MAIL_CREATURE;
        mail->stationery = MAIL_STATIONERY_DEFAULT;
        mail->sender = BountyCollectorEntry;
        mail->receiver = sponsor;
        mail->subject = RefundSubject;
        mail->deliver_time = now;
        mail->expire_time = expires;
        mail->money = copper;
        mail->checked = MAIL_CHECK_MASK_COPIED;
        mail->state = MAIL_STATE_UNCHANGED;
        player->AddMail(mail);
        player->AddNewMailDeliverTime(now);
    }
}
}

bool Acore::WorldPvp::CanHuntBountyTarget(uint32 targetGuid, uint32 hunterAccount)
{
    std::shared_lock lock(BountyMutex);
    auto const target = ActiveBountyTargets.find(targetGuid);
    if (target == ActiveBountyTargets.end())
        return false;

    uint64 const now = GameTime::GetGameTime().count();
    auto const& sponsors = target->second.sponsors;
    auto const own = sponsors.find(hunterAccount);
    return (own == sponsors.end() || own->second <= now) &&
        std::any_of(sponsors.begin(), sponsors.end(),
            [now](auto const& sponsor) { return sponsor.second > now; });
}

bool Acore::WorldPvp::HasActiveOrPendingBounty(uint32 targetGuid)
{
    std::shared_lock lock(BountyMutex);
    if (LoadedBountyRevision == 0 || PendingBountyTargets.contains(targetGuid))
        return true;

    auto const target = ActiveBountyTargets.find(targetGuid);
    uint64 const now = GameTime::GetGameTime().count();
    return target != ActiveBountyTargets.end() &&
        std::any_of(target->second.sponsors.begin(), target->second.sponsors.end(),
        [now](auto const& sponsor) { return sponsor.second > now; });
}

std::optional<uint64> Acore::WorldPvp::ActiveBountyCopper(uint32 targetGuid)
{
    std::shared_lock lock(BountyMutex);
    if (LoadedBountyRevision == 0 || PendingBountyTargets.contains(targetGuid))
        return std::nullopt;

    auto const target = ActiveBountyTargets.find(targetGuid);
    uint64 total = 0;
    uint64 const now = GameTime::GetGameTime().count();
    if (target != ActiveBountyTargets.end())
        for (auto const& [expires, copper] : target->second.contributions)
            if (expires == 0 || expires > now)
                total += copper;
    return total;
}

void Acore::WorldPvp::InvalidateBountyTarget(uint32 targetGuid)
{
    std::unique_lock lock(BountyMutex);
    ActiveBountyTargets.erase(targetGuid);
    PendingBountyTargets.insert(targetGuid);
    ++BountyRevision;
}

void Acore::WorldPvp::RefreshBountyTargets(QueryCallbackProcessor& processor)
{
    if (!CanUseBountyEscrow() || BountyRefreshInFlight || GameTime::GetGameTimeMS() < NextBountyRefresh)
        return;

    uint64 revision;
    {
        std::shared_lock lock(BountyMutex);
        if (LoadedBountyRevision == BountyRevision)
            return;

        revision = BountyRevision;
    }

    BountyRefreshInFlight = true;
    auto* query = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_BOUNTY_TARGETS);
    processor.AddCallback(CharacterDatabase.AsyncQuery(query).WithPreparedCallback(
        [revision](PreparedQueryResult result)
        {
            BountyRefreshInFlight = false;
            if (!result)
            {
                NextBountyRefresh = GameTime::GetGameTimeMS() + Seconds(5);
                return;
            }

            BountyTargets targets;
            do
            {
                Field* row = result->Fetch();
                uint32 const guid = static_cast<uint32>(row[0].Get<uint64>());
                if (!guid)
                    continue;

                uint32 const account = static_cast<uint32>(row[1].Get<uint64>());
                uint64 const expires = row[2].Get<uint64>();
                TargetBounties& target = targets[guid];
                target.contributions.emplace_back(expires, row[3].Get<uint64>());
                if (account && expires)
                {
                    uint64& lastExpiry = target.sponsors[account];
                    lastExpiry = std::max(lastExpiry, expires);
                }
            } while (result->NextRow());

            std::unique_lock lock(BountyMutex);
            if (revision != BountyRevision)
                return;

            ActiveBountyTargets.swap(targets);
            PendingBountyTargets.clear();
            LoadedBountyRevision = revision;
        }));
}

void Acore::WorldPvp::ProcessBountyRefunds(QueryCallbackProcessor& processor)
{
    static Milliseconds nextRefundPoll{};
    static bool refundPollInFlight = false;
    Milliseconds const now = GameTime::GetGameTimeMS();
    if (!CanUseBountyEscrow() || refundPollInFlight || now < nextRefundPoll)
        return;

    nextRefundPoll = now + Seconds(5);
    refundPollInFlight = true;
    auto* query = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_REFUND_QUEUE);
    processor.AddCallback(CharacterDatabase.AsyncQuery(query).WithPreparedCallback([](PreparedQueryResult result)
    {
        refundPollInFlight = false;
        if (!result || !CanUseBountyEscrow())
            return;

        do
        {
            Field* row = result->Fetch();
            SettleBountyRefund(row[0].Get<uint32>(), row[1].Get<uint64>(), row[2].Get<uint32>(), row[3].Get<uint32>());
        } while (result->NextRow());
    }));
}
