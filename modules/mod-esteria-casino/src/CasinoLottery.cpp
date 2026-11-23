/*
 * The Esteria Lottery: tickets for gold at the Lottery Vendor, a draw on a fixed schedule, prizes paid from the pool.
 *
 * The pool is real gold: every ticket's price, plus a share of the house's winnings (BookHouse in
 * EsteriaCasino.cpp). Rules in Lottery.h. A draw happens once per number: its row, the ticket results, the prizes
 * (mailed when the winner is offline) and the new pool commit together; with no jackpot winner the pool rolls over.
 *
 * client -> server
 *   LS                    state again
 *   LB:<n,n,n,n> | LB:Q   buy a ticket with these numbers, or a quick pick
 *   LQ                    close the window
 *
 * server -> client
 *   O:lottery:<ticketCost>:<threeMatchPrize>:<maxTickets>:<pick>:<highest>
 *   LS:<draw>:<pool>:<secondsToDraw>:<yourTickets>
 *   LT:<numbers>                                   one of your tickets for the coming draw
 *   LR:<draw>:<numbers>:<jackpotWinners>:<jackpotEach>:<threeWinners>:<threeEach>:<rollover>   the last draw
 *   LP:<numbers>:<matched>:<prize>                 your ticket in the last draw
 *   LK:<numbers>                                   ticket bought
 */
#include "CasinoCommon.h"
#include "Lottery.h"

#include "Chat.h"
#include "Config.h"
#include "Creature.h"
#include "CreatureScript.h"
#include "DatabaseEnv.h"
#include "Log.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "ScriptedGossip.h"
#include "StringFormat.h"
#include "WorldSession.h"

#include <limits>
#include <unordered_map>

using namespace EsteriaCasino;
using namespace EsteriaCasino::Server;
namespace LO = EsteriaCasino::Lottery;

namespace
{
    enum GossipAction : uint32
    {
        GOSSIP_ACTION_LOTTERY = 1,
    };

    struct LotteryConfig
    {
        uint64 ticketCost = 100000;   // 10 gold
        uint64 threePrize = 1500000;  // 150 gold
        uint32 maxTickets = 10;       // per character per draw
        uint32 intervalMinutes = 60;
    } lotteryConfig;

    bool loaded = false;
    uint64 pool = 0;
    uint32 drawNumber = 1;
    uint32 nextDraw = 0;

    struct LastDraw
    {
        uint32 draw = 0;
        std::string numbers;
        uint32 jackpotWinners = 0;
        uint64 jackpotEach = 0;
        uint32 threeWinners = 0;
        uint64 threeEach = 0;
        uint64 rollover = 0;
    } lastDraw;

    std::unordered_map<ObjectGuid, ObjectGuid> viewers; // player -> vendor

    void SendOpen(Player* player)
    {
        Send(player, Acore::StringFormat("O:lottery:{}:{}:{}:{}:{}", lotteryConfig.ticketCost, lotteryConfig.threePrize,
            lotteryConfig.maxTickets, LO::PICK, LO::HIGHEST));
    }

    uint32 TicketsFor(ObjectGuid guid, uint32 draw)
    {
        QueryResult result = CharacterDatabase.Query(Acore::StringFormat(
            "SELECT COUNT(*) FROM `casino_lottery_ticket` WHERE `draw` = {} AND `guid` = {}", draw, guid.GetCounter()));
        return result ? uint32(result->Fetch()[0].Get<uint64>()) : 0;
    }

    void SendState(Player* player)
    {
        ObjectGuid const guid = player->GetGUID();
        QueryResult mine = CharacterDatabase.Query(Acore::StringFormat(
            "SELECT `numbers` FROM `casino_lottery_ticket` WHERE `draw` = {} AND `guid` = {} ORDER BY `id`",
            drawNumber, guid.GetCounter()));
        uint32 const count = mine ? uint32(mine->GetRowCount()) : 0;
        uint32 const now = Now();
        Send(player, Acore::StringFormat("LS:{}:{}:{}:{}", drawNumber, pool, nextDraw > now ? nextDraw - now : 0,
            count));
        if (mine)
            do
                Send(player, "LT:" + mine->Fetch()[0].Get<std::string>());
            while (mine->NextRow());
        if (!lastDraw.draw)
            return;
        Send(player, Acore::StringFormat("LR:{}:{}:{}:{}:{}:{}:{}", lastDraw.draw, lastDraw.numbers,
            lastDraw.jackpotWinners, lastDraw.jackpotEach, lastDraw.threeWinners, lastDraw.threeEach,
            lastDraw.rollover));
        if (QueryResult past = CharacterDatabase.Query(Acore::StringFormat(
            "SELECT `numbers`, `matched`, `prize` FROM `casino_lottery_ticket` WHERE `draw` = {} AND `guid` = {} "
            "ORDER BY `id`", lastDraw.draw, guid.GetCounter())))
            do
            {
                Field* f = past->Fetch();
                Send(player, Acore::StringFormat("LP:{}:{}:{}", f[0].Get<std::string>(), uint32(f[1].Get<uint8>()),
                    f[2].Get<uint64>()));
            } while (past->NextRow());
    }

    void Buy(Player* player, std::string_view args)
    {
        auto view = viewers.find(player->GetGUID());
        if (!loaded || view == viewers.end())
            return Refuse(player, "closed");
        if (!Near(player, view->second))
            return Refuse(player, "range");
        if (char const* refusal = StakeRefusal(player, lotteryConfig.ticketCost))
            return Refuse(player, refusal);
        if (TicketsFor(player->GetGUID(), drawNumber) >= lotteryConfig.maxTickets)
            return Refuse(player, "tickets");
        std::optional<LO::Numbers> numbers = args == "Q" ? std::optional<LO::Numbers>(LO::Draw(SecureBelow))
                                                         : LO::Parse(std::string(args));
        if (!numbers)
            return Refuse(player, "numbers");

        uint32 const account = player->GetSession()->GetAccountId();
        ObjectGuid::LowType const guid = player->GetGUID().GetCounter();
        Allowance& allowance = AllowanceFor(account);
        allowance.wagered += lotteryConfig.ticketCost;
        std::string const text = LO::Text(*numbers);
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        player->ModifyMoney(-int32(lotteryConfig.ticketCost));
        trans->Append(Acore::StringFormat(
            "INSERT INTO `casino_lottery_ticket` (`draw`, `guid`, `account`, `numbers`, `cost`) "
            "VALUES ({}, {}, {}, '{}', {})",
            drawNumber, guid, account, text, lotteryConfig.ticketCost));
        AddToLottery(trans, lotteryConfig.ticketCost);
        AppendLedger(trans, 0, guid, -int64(lotteryConfig.ticketCost), 0, "ticket");
        SaveAllowance(trans, account, allowance);
        player->SaveGoldToDB(trans);
        CharacterDatabase.CommitTransaction(trans);
        LOG_INFO("module.casino", "{} bought lottery ticket {} for draw {}", player->GetName(), text, drawNumber);
        Send(player, "LK:" + text);
        SendState(player);
    }

    void RunDraw()
    {
        LO::Numbers const drawn = LO::Draw(SecureBelow);
        std::vector<uint32> ids;
        std::vector<ObjectGuid::LowType> owners;
        std::vector<LO::Numbers> tickets;
        if (QueryResult result = CharacterDatabase.Query(Acore::StringFormat(
            "SELECT `id`, `guid`, `numbers` FROM `casino_lottery_ticket` WHERE `draw` = {}", drawNumber)))
            do
            {
                Field* f = result->Fetch();
                std::optional<LO::Numbers> numbers = LO::Parse(f[2].Get<std::string>());
                if (!numbers)
                    continue;
                ids.push_back(f[0].Get<uint32>());
                owners.push_back(f[1].Get<uint32>());
                tickets.push_back(*numbers);
            } while (result->NextRow());

        LO::Payout const payout = LO::Settle(tickets, drawn, pool, lotteryConfig.threePrize);
        uint32 const now = Now();
        uint32 const following = now + lotteryConfig.intervalMinutes * 60;
        std::string const numbers = LO::Text(drawn);
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        for (size_t i = 0; i < tickets.size(); ++i)
        {
            int const matched = LO::Matches(tickets[i], drawn);
            trans->Append(Acore::StringFormat("UPDATE `casino_lottery_ticket` SET `matched` = {}, `prize` = {} "
                "WHERE `id` = {}", matched, payout.prizes[i], ids[i]));
            if (!payout.prizes[i])
                continue;
            ObjectGuid const owner = ObjectGuid::Create<HighGuid::Player>(owners[i]);
            bool const mailed = Pay(owner, trans, payout.prizes[i], Acore::StringFormat(
                "Your ticket {} matched {} numbers in Esteria Lottery draw #{} ({}).", LO::Text(tickets[i]), matched,
                drawNumber, numbers));
            AppendLedger(trans, 0, owners[i], mailed ? 0 : int64(payout.prizes[i]), 0, mailed ? "mailed" : "prize");
        }
        trans->Append(Acore::StringFormat(
            "INSERT INTO `casino_lottery_draw` (`draw`, `numbers`, `tickets`, `pool`, `paid`, `rollover`, "
            "`jackpot_winners`, `three_winners`) VALUES ({}, '{}', {}, {}, {}, {}, {}, {})",
            drawNumber, numbers, tickets.size(), pool, payout.paid, payout.rollover, payout.jackpotWinners,
            payout.smallWinners));
        trans->Append(Acore::StringFormat(
            "UPDATE `casino_lottery` SET `pool` = `pool` - {}, `draw` = {}, `next_draw` = {} WHERE `id` = 1",
            payout.paid, drawNumber + 1, following));
        CharacterDatabase.CommitTransaction(trans);

        LOG_INFO("module.casino", "Lottery draw {}: {} from {} tickets, pool {}, paid {}, rolls over {}", drawNumber,
            numbers, tickets.size(), pool, payout.paid, payout.rollover);
        std::string announce = Acore::StringFormat("|cffe8c46aEsteria Lottery|r draw #{}: {}.", drawNumber, numbers);
        if (payout.jackpotWinners)
            announce += Acore::StringFormat(" {} jackpot winner(s) take {} each!", payout.jackpotWinners,
                GoldText(payout.jackpotEach));
        else
            announce += Acore::StringFormat(" No jackpot: {} rolls over.", GoldText(payout.rollover));
        // SendWorldText needs a session (it dereferences m_session); the draw runs with none, which crashed the server.
        ChatHandler(nullptr).SendGlobalSysMessage(announce.c_str());

        lastDraw = { drawNumber, numbers, uint32(payout.jackpotWinners), payout.jackpotEach,
                     uint32(payout.smallWinners), payout.smallEach, payout.rollover };
        pool -= payout.paid;
        ++drawNumber;
        nextDraw = following;
        for (auto const& [guid, vendor] : viewers)
            if (Player* player = ObjectAccessor::FindConnectedPlayer(guid))
                SendState(player);
    }
}

namespace EsteriaCasino::Server
{
    void LoadLotteryConfig()
    {
        lotteryConfig.ticketCost = std::max<uint64>(1, std::min<uint64>(uint64(std::numeric_limits<int32>::max()),
            sConfigMgr->GetOption<uint64>("EsteriaCasino.Lottery.TicketCost", 100000)));
        lotteryConfig.threePrize = sConfigMgr->GetOption<uint64>("EsteriaCasino.Lottery.ThreeMatchPrize", 1500000);
        lotteryConfig.maxTickets = std::max(1u, sConfigMgr->GetOption<uint32>("EsteriaCasino.Lottery.MaxTickets", 10));
        lotteryConfig.intervalMinutes = std::max(1u,
            sConfigMgr->GetOption<uint32>("EsteriaCasino.Lottery.DrawMinutes", 60));
    }

    void LoadLottery()
    {
        CharacterDatabase.DirectExecute(Acore::StringFormat(
            "INSERT IGNORE INTO `casino_lottery` (`id`, `pool`, `draw`, `next_draw`) VALUES (1, 0, 1, {})",
            Now() + lotteryConfig.intervalMinutes * 60));
        QueryResult state =
            CharacterDatabase.Query("SELECT `pool`, `draw`, `next_draw` FROM `casino_lottery` WHERE `id` = 1");
        if (!state)
        {
            LOG_ERROR("module.casino", "casino_lottery is missing; apply mod-esteria-casino's characters SQL. "
                "The lottery stays closed.");
            return;
        }
        Field* f = state->Fetch();
        pool = f[0].Get<uint64>();
        drawNumber = f[1].Get<uint32>();
        nextDraw = f[2].Get<uint32>();
        if (QueryResult last = CharacterDatabase.Query(
            "SELECT `draw`, `numbers`, `jackpot_winners`, `three_winners`, `paid`, `rollover`, `pool` "
            "FROM `casino_lottery_draw` ORDER BY `draw` DESC LIMIT 1"))
        {
            Field* d = last->Fetch();
            lastDraw.draw = d[0].Get<uint32>();
            lastDraw.numbers = d[1].Get<std::string>();
            lastDraw.jackpotWinners = d[2].Get<uint32>();
            lastDraw.threeWinners = d[3].Get<uint32>();
            lastDraw.rollover = d[5].Get<uint64>();
            // Each prize, from the stored totals (the draw stored what it paid, not the split).
            if (QueryResult prizes = CharacterDatabase.Query(Acore::StringFormat(
                "SELECT MAX(CASE WHEN `matched` = 4 THEN `prize` END), MAX(CASE WHEN `matched` = 3 THEN `prize` END) "
                "FROM `casino_lottery_ticket` WHERE `draw` = {}", lastDraw.draw)))
            {
                Field* p = prizes->Fetch();
                lastDraw.jackpotEach = p[0].IsNull() ? 0 : p[0].Get<uint64>();
                lastDraw.threeEach = p[1].IsNull() ? 0 : p[1].Get<uint64>();
            }
        }
        loaded = true;
        LOG_INFO("module.casino", "Lottery loaded: draw {} in {} minute(s), pool {}.", drawNumber,
            nextDraw > Now() ? (nextDraw - Now()) / 60 : 0, GoldText(pool));
    }

    void OpenLottery(Player* player, Creature* npc)
    {
        viewers[player->GetGUID()] = npc->GetGUID();
        SendOpen(player);
        SendState(player);
    }

    bool HandleLotteryMessage(Player* player, std::string_view command, std::string_view args)
    {
        if (command == "LS")
        {
            if (loaded && viewers.contains(player->GetGUID()))
                SendState(player);
        }
        else if (command == "LB")
            Buy(player, args);
        else if (command == "LQ")
            viewers.erase(player->GetGUID());
        else
            return false;
        return true;
    }

    void LotteryUpdate()
    {
        if (loaded && Now() >= nextDraw)
            RunDraw();
    }

    bool LotteryLoaded()
    {
        return loaded;
    }

    void AddToLottery(CharacterDatabaseTransaction trans, uint64 copper)
    {
        pool += copper;
        trans->Append(Acore::StringFormat("UPDATE `casino_lottery` SET `pool` = `pool` + {} WHERE `id` = 1", copper));
    }

    uint64 LotteryPool()
    {
        return pool;
    }
}

class npc_esteria_casino_lottery : public CreatureScript
{
public:
    npc_esteria_casino_lottery() : CreatureScript("npc_esteria_casino_lottery") { }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        ClearGossipMenuFor(player);
        if (Open() && LotteryLoaded())
            AddGossipItemFor(player, GOSSIP_ICON_MONEY_BAG, "Buy lottery tickets.", GOSSIP_SENDER_MAIN,
                GOSSIP_ACTION_LOTTERY);
        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature);
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* creature, uint32 /*sender*/, uint32 action) override
    {
        CloseGossipMenuFor(player);
        if (action == GOSSIP_ACTION_LOTTERY && Open() && LotteryLoaded())
            OpenLottery(player, creature);
        return true;
    }
};

void AddCasinoLotteryScripts()
{
    new npc_esteria_casino_lottery();
}
