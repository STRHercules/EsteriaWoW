/*
 * Fixed-limit Texas Hold'em between players at the Poker Croupier NPC: one table per croupier, six seats.
 *
 * A buy-in leaves the character into an escrowed round, and that round's `wagered` is rewritten to the player's
 * stack after every hand, together with the hand's rake, in one commit. A server restart therefore refunds every
 * seat its stack as of the last finished hand (the startup sweep in EsteriaCasino.cpp), and the chips of the hand in
 * progress go back with it. Leaving pays the stack out. The table deals itself: a new hand starts a few seconds after
 * the last when two or more seats have chips, and a player who runs out of time checks if free, else folds.
 *
 * House players (Holdem.h Bot) fill seats up to EsteriaCasino.Poker.HouseSeats while at least one real player is
 * seated, so nobody needs company to play. Their chips are house gold: a buy-in reserves it from the bankroll, every
 * finished hand books their win or loss to the house in the same commit as the players' stacks, and leaving releases
 * the reservation. They never sit at an empty table.
 *
 * client -> server
 *   PJ:<seat>:<buyIn>    sit down with a buy-in
 *   PA:<f|k|c|b|r>       fold, check, call, bet, raise
 *   PL                   stand up (at once between hands; after the hand otherwise, folding when it is your turn)
 *   PQ                   close the window (the seat stays)
 *
 * server -> client
 *   O:poker:<small>:<big>:<minBuy>:<maxBuy>:<rakeBp>:<rakeCap>:<actionSeconds>
 *   PS:<seat>:<name>:<stack>:<bet>:<flags>     flags: i in hand, f folded, a all in, d button, t to act, s you,
 *                                              w leaving; an empty seat has no name
 *   PT:<hand>:<street>:<pot>:<board>:<toAct>:<currentBet>:<legal>:<seconds>:<toCall>:<betSize>
 *       street 0 between hands, 1 preflop .. 4 river; board card codes joined by ','; legal = your actions
 *   PH:<card>,<card>                           your hole cards this hand
 *   PW:<hand>:<seat>:<won>:<cards>:<handName>  a winner, or a hand shown at showdown
 *   PR:<hand>:<pot>:<rake>                     the hand is over
 */
#include "Blackjack.h"
#include "CasinoCommon.h"
#include "Holdem.h"

#include "Config.h"
#include "Creature.h"
#include "CreatureScript.h"
#include "DatabaseEnv.h"
#include "Log.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "ScriptedGossip.h"
#include "StringConvert.h"
#include "StringFormat.h"
#include "Tokenize.h"
#include "WorldSession.h"

#include <array>
#include <limits>
#include <random>
#include <map>
#include <set>
#include <unordered_map>

using namespace EsteriaCasino;
using namespace EsteriaCasino::Server;
namespace HE = EsteriaCasino::Holdem;

namespace
{
    enum GossipAction : uint32
    {
        GOSSIP_ACTION_TABLE = 1,
    };

    struct PokerConfig
    {
        uint64 smallBlind = 5000;  // 50 silver
        uint64 bigBlind = 10000;   // 1 gold
        uint32 minBuyIn = 20;      // big blinds
        uint32 maxBuyIn = 100;
        uint32 rakeBp = 500;
        uint64 rakeCap = 20000;    // 2 gold
        uint32 actionSeconds = 30;
        uint32 nextHandSeconds = 4;
        uint32 houseSeats = 3;      // players the table is filled to with house players; 0 turns them off
        uint32 houseBuyIn = 50;     // big blinds
    } pokerConfig;

    constexpr uint64 BOT_ID = 0x100000000ull; // engine ids above any character guid
    char const* const BOT_NAMES[HE::SEATS] = { "Gizmo", "Sprocket", "Fizzlebang", "Nix", "Boltwrench", "Zapp" };

    struct PokerTable
    {
        explicit PokerTable(ObjectGuid npc_, uint32 entry)
            : npc(npc_), npcEntry(entry),
              game(pokerConfig.smallBlind, pokerConfig.bigBlind, pokerConfig.rakeBp, pokerConfig.rakeCap) { }

        ObjectGuid npc;
        uint32 npcEntry;
        HE::Table game;
        std::array<ObjectGuid, HE::SEATS> guids;
        std::array<std::string, HE::SEATS> names;
        std::array<uint64, HE::SEATS> rounds {};
        std::array<bool, HE::SEATS> leaving {};
        std::array<bool, HE::SEATS> bot {};
        std::array<uint64, HE::SEATS> botBooked {}; // a house player's stack as last booked to the bankroll
        std::set<ObjectGuid> viewers;
        int64 actionMs = 0;
        int64 nextHandMs = 0;
        uint64 settledHand = 0;
    };

    std::map<ObjectGuid, PokerTable> tables; // by croupier
    std::unordered_map<ObjectGuid, ObjectGuid> seatedAt;
    std::unordered_map<ObjectGuid, ObjectGuid> viewingAt;

    uint64 MinBuy() { return pokerConfig.bigBlind * pokerConfig.minBuyIn; }
    uint64 MaxBuy() { return pokerConfig.bigBlind * pokerConfig.maxBuyIn; }

    int SeatOf(PokerTable const& t, ObjectGuid guid)
    {
        for (int i = 0; i < HE::SEATS; ++i)
            if (t.guids[i] == guid && !guid.IsEmpty())
                return i;
        return -1;
    }

    std::string Code(HE::Card card) { return Blackjack::Code(card); }

    void SendOpen(Player* player)
    {
        Send(player, Acore::StringFormat("O:poker:{}:{}:{}:{}:{}:{}:{}", pokerConfig.smallBlind, pokerConfig.bigBlind,
            MinBuy(), MaxBuy(), pokerConfig.rakeBp, pokerConfig.rakeCap, pokerConfig.actionSeconds));
    }

    void SendTable(Player* to, PokerTable const& t)
    {
        HE::Table const& g = t.game;
        int const you = SeatOf(t, to->GetGUID());
        for (int i = 0; i < HE::SEATS; ++i)
        {
            HE::Seat const& s = g.seats[i];
            if (!s.id)
            {
                Send(to, Acore::StringFormat("PS:{}::0:0:", i));
                continue;
            }
            std::string flags;
            if (g.InHand() && s.inHand) flags += 'i';
            if (g.InHand() && s.folded) flags += 'f';
            if (s.allIn && g.InHand()) flags += 'a';
            if (g.button == i) flags += 'd';
            if (g.InHand() && g.toAct == i) flags += 't';
            if (you == i) flags += 's';
            if (t.leaving[i]) flags += 'w';
            if (t.bot[i]) flags += 'h';
            Send(to, Acore::StringFormat("PS:{}:{}:{}:{}:{}", i, t.names[i], s.stack, g.InHand() ? s.bet : 0, flags));
        }
        std::string board;
        for (HE::Card c : g.board)
            board += (board.empty() ? "" : ",") + Code(c);
        std::string const legal = you >= 0 ? g.Legal(you) : "";
        Send(to, Acore::StringFormat("PT:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}", g.handNumber, int(g.street),
            g.InHand() ? g.Pot() : 0, board, g.toAct, g.currentBet, legal, std::max<int64>(0, t.actionMs / 1000),
            you >= 0 ? g.CallAmount(you) : 0, g.BetSize()));
        if (you >= 0 && g.InHand() && g.seats[you].inHand)
            Send(to, Acore::StringFormat("PH:{},{}", Code(g.seats[you].hole[0]), Code(g.seats[you].hole[1])));
    }

    void Broadcast(PokerTable const& t)
    {
        for (ObjectGuid const& viewer : t.viewers)
            if (Player* player = ObjectAccessor::FindConnectedPlayer(viewer))
                SendTable(player, t);
    }

    void CashOut(PokerTable& t, int seat, char const* why)
    {
        HE::Seat& s = t.game.seats[seat];
        ObjectGuid const guid = t.guids[seat];
        uint64 const paid = s.stack;
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        bool const mailed = Pay(guid, trans, paid, "Your chips from the Esteria Casino poker table.");
        CloseRound(trans, t.rounds[seat], paid,
            Acore::StringFormat("holdem table {} seat {}: {}", t.npcEntry, seat, why));
        AppendLedger(trans, t.rounds[seat], guid.GetCounter(), mailed ? 0 : int64(paid), 0,
            mailed ? "mailed" : "cashout");
        CharacterDatabase.CommitTransaction(trans);
        LOG_INFO("module.casino", "{} leaves poker table {} with {} ({})", t.names[seat], t.npcEntry, paid, why);
        seatedAt.erase(guid);
        s = HE::Seat();
        t.guids[seat].Clear();
        t.names[seat].clear();
        t.rounds[seat] = 0;
        t.leaving[seat] = false;
    }

    uint32 Humans(PokerTable const& t)
    {
        uint32 n = 0;
        for (int i = 0; i < HE::SEATS; ++i)
            n += (t.game.seats[i].id && !t.bot[i]) ? 1 : 0;
        return n;
    }

    // A house player leaves: its chips go back to the house's free bankroll (its result is already booked).
    void RemoveBot(PokerTable& t, int seat)
    {
        house.reserved -= std::min(house.reserved, t.game.seats[seat].stack);
        t.game.seats[seat] = HE::Seat();
        t.names[seat].clear();
        t.bot[seat] = false;
        t.botBooked[seat] = 0;
        t.leaving[seat] = false;
    }

    // Between hands: house players come and go so the table holds HouseSeats players while anyone real is seated;
    // short-stacked ones are replaced with a fresh buy-in.
    void ManageBots(PokerTable& t)
    {
        uint64 const buyIn = pokerConfig.bigBlind * pokerConfig.houseBuyIn;
        uint32 const humans = Humans(t);
        uint32 const wanted = humans && pokerConfig.houseSeats > humans ? pokerConfig.houseSeats - humans : 0;
        uint32 bots = 0;
        for (int i = 0; i < HE::SEATS; ++i)
        {
            if (!t.bot[i])
                continue;
            if (bots >= wanted || t.game.seats[i].stack < pokerConfig.bigBlind * 10)
                RemoveBot(t, i);
            else
                ++bots;
        }
        for (int i = 0; i < HE::SEATS && bots < wanted; ++i)
        {
            if (t.game.seats[i].id)
                continue;
            if (!Open() || !house.Reserve(buyIn))
                break; // the house can't cover another stack right now
            t.game.seats[i] = { BOT_ID + uint64(i), buyIn };
            t.names[i] = Acore::StringFormat("{} (House)", BOT_NAMES[i]);
            t.bot[i] = true;
            t.botBooked[i] = buyIn;
            ++bots;
        }
    }

    // A finished hand: stacks and rake are saved together, results go out, broke and leaving players stand up.
    void SettleHand(PokerTable& t)
    {
        HE::Table const& g = t.game;
        HE::Result const& r = g.Last();
        t.settledHand = g.handNumber;
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        for (int i = 0; i < HE::SEATS; ++i)
        {
            if (!g.seats[i].id)
                continue;
            if (t.bot[i])
            {
                // A house player's win or loss is the house's, booked now so a restart can't undo it.
                int64 const delta = int64(g.seats[i].stack) - int64(t.botBooked[i]);
                if (delta)
                {
                    house.bankroll += delta;
                    house.reserved = uint64(std::max<int64>(0, int64(house.reserved) + delta));
                    AppendLedger(trans, 0, 0, 0, delta, "housebot");
                    BookHouse(trans, delta, 0);
                }
                t.botBooked[i] = g.seats[i].stack;
                continue;
            }
            trans->Append(Acore::StringFormat(
                "UPDATE `casino_round` SET `wagered` = {} WHERE `id` = {} AND `state` = {}", g.seats[i].stack,
                t.rounds[i], uint32(ROUND_OPEN)));
        }
        if (r.rake)
        {
            int64 const delta = house.Settle(0, r.rake, 0);
            AppendLedger(trans, 0, 0, 0, delta, "rake");
            BookHouse(trans, delta, 0);
        }
        CharacterDatabase.CommitTransaction(trans);

        for (int i = 0; i < HE::SEATS; ++i)
        {
            HE::Seat const& s = g.seats[i];
            if (!s.id || !s.inHand || (!r.won[i] && !r.value[i]))
                continue;
            std::string const cards = r.value[i] ? Code(s.hole[0]) + "," + Code(s.hole[1]) : "";
            std::string const line = Acore::StringFormat("PW:{}:{}:{}:{}:{}", g.handNumber, i, r.won[i], cards,
                r.value[i] ? HE::CategoryName(r.value[i]) : "");
            for (ObjectGuid const& viewer : t.viewers)
                SendTo(viewer, line);
        }
        for (ObjectGuid const& viewer : t.viewers)
            SendTo(viewer, Acore::StringFormat("PR:{}:{}:{}", g.handNumber, r.pot, r.rake));

        for (int i = 0; i < HE::SEATS; ++i)
            if (g.seats[i].id && !t.bot[i] && (t.leaving[i] || !g.seats[i].stack))
                CashOut(t, i, g.seats[i].stack ? "left" : "busted");
        t.nextHandMs = int64(pokerConfig.nextHandSeconds) * 1000;
    }

    // After every action: settle a finished hand, fold players who left, restart the turn clock, tell the table.
    void AfterAction(PokerTable& t)
    {
        HE::Table& g = t.game;
        while (g.InHand() && g.toAct >= 0 && t.leaving[g.toAct])
            g.Act(g.toAct, HE::Action::Fold);
        if (!g.InHand() && g.handNumber != t.settledHand)
            SettleHand(t);
        // House players take a moment, so their action reads like a decision.
        bool const botTurn = g.InHand() && g.toAct >= 0 && t.bot[g.toAct];
        t.actionMs = botTurn ? 1200 + int64(SecureBelow(1500)) : int64(pokerConfig.actionSeconds) * 1000;
        Broadcast(t);
    }

    void Sit(Player* player, std::string_view args)
    {
        auto view = viewingAt.find(player->GetGUID());
        if (view == viewingAt.end())
            return Refuse(player, "noseat");
        PokerTable& t = tables.at(view->second);
        std::vector<std::string_view> parts = Acore::Tokenize(args, ':', true);
        std::optional<uint32> seat = parts.size() == 2 ? Acore::StringTo<uint32>(parts[0]) : std::nullopt;
        std::optional<uint64> buyIn = parts.size() == 2 ? Acore::StringTo<uint64>(parts[1]) : std::nullopt;
        if (!seat || !buyIn || *seat >= HE::SEATS)
            return Refuse(player, "amount");
        if (!Near(player, t.npc))
            return Refuse(player, "range");
        if (seatedAt.contains(player->GetGUID()))
            return Refuse(player, "playing");
        if (t.game.seats[*seat].id)
            return Refuse(player, "taken");
        if (*buyIn < MinBuy())
            return Refuse(player, "min");
        if (*buyIn > MaxBuy())
            return Refuse(player, "max");
        if (char const* refusal = StakeRefusal(player, *buyIn))
            return Refuse(player, refusal);

        uint64 const round = NextRoundId();
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        TakeStake(player, trans, round, "holdem", t.npcEntry, *buyIn,
            Acore::StringFormat("holdem table {} seat {}", t.npcEntry, *seat));
        CharacterDatabase.CommitTransaction(trans);

        t.game.seats[*seat] = { player->GetGUID().GetCounter(), *buyIn };
        t.guids[*seat] = player->GetGUID();
        t.names[*seat] = player->GetName();
        t.rounds[*seat] = round;
        t.leaving[*seat] = false;
        seatedAt[player->GetGUID()] = t.npc;
        LOG_INFO("module.casino", "{} sits at poker table {} seat {} with {}", player->GetName(), t.npcEntry, *seat,
            *buyIn);
        if (!t.game.InHand())
        {
            ManageBots(t);
            if (t.nextHandMs <= 0)
                t.nextHandMs = int64(pokerConfig.nextHandSeconds) * 1000;
        }
        Broadcast(t);
    }

    void Leave(PokerTable& t, int seat)
    {
        HE::Table& g = t.game;
        if (!g.InHand() || !g.seats[seat].inHand || g.seats[seat].folded)
        {
            CashOut(t, seat, "left");
            return Broadcast(t);
        }
        t.leaving[seat] = true;
        AfterAction(t); // folds now if it is their turn
    }

    void ActAt(Player* player, std::string_view args)
    {
        auto at = seatedAt.find(player->GetGUID());
        if (at == seatedAt.end() || args.size() != 1)
            return Refuse(player, "noseat");
        PokerTable& t = tables.at(at->second);
        int const seat = SeatOf(t, player->GetGUID());
        size_t const kind = std::string_view("fkcbr").find(args[0]);
        if (kind == std::string_view::npos || !t.game.Act(seat, HE::Action(kind)))
            return Refuse(player, "action");
        AfterAction(t);
    }
}

namespace EsteriaCasino::Server
{
    void LoadPokerConfig()
    {
        pokerConfig.bigBlind = std::clamp<uint64>(sConfigMgr->GetOption<uint64>("EsteriaCasino.Poker.BigBlind", 10000),
            2, 10000000);
        pokerConfig.smallBlind = std::clamp<uint64>(sConfigMgr->GetOption<uint64>("EsteriaCasino.Poker.SmallBlind",
            pokerConfig.bigBlind / 2), 1, pokerConfig.bigBlind);
        pokerConfig.minBuyIn = std::max(2u, sConfigMgr->GetOption<uint32>("EsteriaCasino.Poker.MinBuyIn", 20));
        pokerConfig.maxBuyIn = std::max(pokerConfig.minBuyIn,
            sConfigMgr->GetOption<uint32>("EsteriaCasino.Poker.MaxBuyIn", 100));
        // A stack must stay payable in one ModifyMoney: cap the buy-in so six of them fit.
        uint64 const ceiling = uint64(std::numeric_limits<int32>::max()) / HE::SEATS / pokerConfig.bigBlind;
        pokerConfig.maxBuyIn = uint32(std::min<uint64>(pokerConfig.maxBuyIn, ceiling));
        pokerConfig.minBuyIn = std::min(pokerConfig.minBuyIn, pokerConfig.maxBuyIn);
        pokerConfig.rakeBp = std::min(1000u, sConfigMgr->GetOption<uint32>("EsteriaCasino.Poker.Rake", 500));
        pokerConfig.rakeCap = sConfigMgr->GetOption<uint64>("EsteriaCasino.Poker.RakeCap", 20000);
        pokerConfig.actionSeconds = std::clamp(sConfigMgr->GetOption<uint32>("EsteriaCasino.Poker.ActionSeconds", 30),
            5u, 120u);
        pokerConfig.houseSeats = std::min<uint32>(HE::SEATS,
            sConfigMgr->GetOption<uint32>("EsteriaCasino.Poker.HouseSeats", 3));
        pokerConfig.houseBuyIn = std::clamp(sConfigMgr->GetOption<uint32>("EsteriaCasino.Poker.HouseBuyIn", 50),
            pokerConfig.minBuyIn, pokerConfig.maxBuyIn);
    }

    void OpenPoker(Player* player, Creature* npc)
    {
        auto [it, created] = tables.try_emplace(npc->GetGUID(), npc->GetGUID(), npc->GetEntry());
        PokerTable& t = it->second;
        if (auto old = viewingAt.find(player->GetGUID()); old != viewingAt.end() && old->second != npc->GetGUID())
            if (auto other = tables.find(old->second); other != tables.end())
                other->second.viewers.erase(player->GetGUID());
        viewingAt[player->GetGUID()] = npc->GetGUID();
        t.viewers.insert(player->GetGUID());
        SendOpen(player);
        SendTable(player, t);
    }

    bool HandlePokerMessage(Player* player, std::string_view command, std::string_view args)
    {
        if (command.size() != 2 || command[0] != 'P')
            return false;
        ObjectGuid const guid = player->GetGUID();
        switch (command[1])
        {
            case 'J': Sit(player, args); break;
            case 'A': ActAt(player, args); break;
            case 'L':
                if (auto at = seatedAt.find(guid); at != seatedAt.end())
                {
                    PokerTable& t = tables.at(at->second);
                    Leave(t, SeatOf(t, guid));
                }
                break;
            case 'Q':
                if (auto view = viewingAt.find(guid); view != viewingAt.end())
                {
                    if (auto t = tables.find(view->second); t != tables.end())
                        t->second.viewers.erase(guid);
                    viewingAt.erase(view);
                }
                break;
            default:
                return false;
        }
        return true;
    }

    void PokerLogout(Player* player)
    {
        ObjectGuid const guid = player->GetGUID();
        if (auto view = viewingAt.find(guid); view != viewingAt.end())
        {
            if (auto t = tables.find(view->second); t != tables.end())
                t->second.viewers.erase(guid);
            viewingAt.erase(view);
        }
        if (auto at = seatedAt.find(guid); at != seatedAt.end())
        {
            PokerTable& t = tables.at(at->second);
            Leave(t, SeatOf(t, guid));
        }
    }

    bool PokerSeated(ObjectGuid guid)
    {
        return seatedAt.contains(guid);
    }

    void PokerUpdate(uint32 diff)
    {
        for (auto& [npc, t] : tables)
        {
            HE::Table& g = t.game;
            if (g.InHand())
            {
                t.actionMs -= diff;
                if (t.actionMs <= 0 && g.toAct >= 0)
                {
                    HE::Action action = g.Default(g.toAct);
                    if (t.bot[g.toAct])
                    {
                        std::mt19937 rng(SecureBelow(std::numeric_limits<uint32>::max()));
                        action = HE::Bot::Decide(g, g.toAct, [&rng](uint32_t n) { return uint32_t(rng() % n); });
                    }
                    g.Act(g.toAct, action);
                    AfterAction(t);
                }
                continue;
            }
            ManageBots(t);
            if (g.Ready() < 2 || !Humans(t))
                continue;
            t.nextHandMs -= diff;
            if (t.nextHandMs > 0)
                continue;
            if (g.Start(HE::Shuffled(SecureBelow)))
            {
                t.actionMs = int64(pokerConfig.actionSeconds) * 1000;
                AfterAction(t);
            }
        }
    }
}

class npc_esteria_casino_poker : public CreatureScript
{
public:
    npc_esteria_casino_poker() : CreatureScript("npc_esteria_casino_poker") { }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        ClearGossipMenuFor(player);
        if (Open())
            AddGossipItemFor(player, GOSSIP_ICON_MONEY_BAG, "Join the Hold'em table.", GOSSIP_SENDER_MAIN,
                GOSSIP_ACTION_TABLE);
        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature);
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* creature, uint32 /*sender*/, uint32 action) override
    {
        CloseGossipMenuFor(player);
        if (action == GOSSIP_ACTION_TABLE && Open())
            OpenPoker(player, creature);
        return true;
    }
};

void AddCasinoPokerScripts()
{
    new npc_esteria_casino_poker();
}
