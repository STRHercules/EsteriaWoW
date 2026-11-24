/*
 * Esteria casino: server half of the EsteriaCasino addon (wowdecomp/Addons/EsteriaCasino). Blackjack, slots and
 * Goblin Dice against the house; see .agents/plans/esteria-casino for the rest.
 *
 * The addon talks over the addon channel like the other Esteria windows: an addon whisper to oneself, which reaches
 * OnPlayerBeforeSendChatMessage as LANG_ADDON. The client sends intentions only. Cards, totals and payouts are
 * decided here, and the dealer's hole card is never sent before the round ends.
 *
 *   client -> server  "ECAS\t<body>"      server -> client  "ECAR\t<body>"
 *
 * client -> server
 *   HI                 addon loaded; resends the table when a round is still open (after /reload)
 *   B:<copper>         place the opening stake and deal
 *   H | S | D | P      hit, stand, double, split
 *   L                  leave the table (refused mid-round)
 *   SP:<copper>        spin the slot machine
 *   DR:<copper>:<call> roll Goblin Dice; call 0 under 7, 1 seven, 2 over 7, 3 doubles
 *
 * server -> client
 *   O:bj:<min>:<max>:<hitSoft17>
 *   O:slots:<min>:<max>:<weights>:<triplePays>:<mixedCoinPay>:<returnBp>     lists joined by ','
 *   O:dice:<min>:<max>:<returnsBp>:<callReturnsBp>                          lists joined by ','
 *   SR:<round>:<a>:<b>:<c>:<stake>:<paid>:<mailed>         slot result, symbols 0..5 on the centre line
 *   DR:<round>:<d1>:<d2>:<call>:<stake>:<paid>:<mailed>    dice result
 *   T:0                                                    no round
 *   T:<round>:<phase>:<active>:<dealer>:<dealerTotal>:<hands>:<actions>
 *       phase 1 playing, 2 finished; dealer = card codes joined by ',' ("??" while the hole card is hidden);
 *       hands = per hand "<cards>|<total>|<soft>|<stake>|<status>" joined by ';', status P playing, D done,
 *       B bust, or once finished W win, J blackjack, U push, L lose; actions = letters from "HSDP".
 *   R:<round>:<wagered>:<paid>:<mailed>                   the committed result
 *   M:<max>                                               new table limit after the bankroll moved
 *   E:<code>                                              refused, nothing changed
 *   W                                                     a blackjack hand is still open at the dealer
 *   C                                                     table closed
 *
 * Gold: every move is one character DB transaction that also saves the player's money, so a crash keeps both or
 * neither. Slots and dice settle in the same commit that takes the stake. A blackjack round's stake sits in
 * casino_round (state 0) until settlement books the house's net result. Rounds still
 * open at startup are refunded by mail. Packets and logout both run on the world thread, so the state here needs no
 * lock. The casino opens only with one character DB async worker (as bounty escrow requires), so the bet, double and
 * settlement commits of a round, and the money each one saves, reach the DB in order.
 */
#include "Blackjack.h"
#include "CasinoCommon.h"
#include "CasinoHouse.h"
#include "Dice.h"
#include "Slots.h"

#include "Chat.h"
#include "CommandScript.h"
#include "Config.h"
#include "Creature.h"
#include "CreatureScript.h"
#include "CryptoRandom.h"
#include "DatabaseEnv.h"
#include "GameObject.h"
#include "GameObjectScript.h"
#include "GameTime.h"
#include "Log.h"
#include "Mail.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "PlayerScript.h"
#include "ScriptedGossip.h"
#include "StringConvert.h"
#include "StringFormat.h"
#include "Tokenize.h"
#include "WorldPacket.h"
#include "WorldPvpRules.h"
#include "WorldScript.h"
#include "WorldSession.h"

#include <limits>
#include <optional>
#include <unordered_map>

using namespace Acore::ChatCommands;
namespace BJ = EsteriaCasino::Blackjack;

namespace EsteriaCasino::Server
{
    Settings settings;
    House house;
    bool houseLoaded = false;
    uint64 nextRoundId = 1;

    namespace
    {
        constexpr char PREFIX_OUT[] = "ECAR\t";
        constexpr uint32 SECONDS_PER_DAY = 86400;

        // One character per account is online, so the account row is only ever written from here.
        std::unordered_map<uint32, Allowance> allowances;
    }

    bool Open()
    {
        return settings.enabled && houseLoaded;
    }

    uint64 NextRoundId()
    {
        return nextRoundId++;
    }

    uint32 Now()
    {
        return uint32(GameTime::GetGameTime().count());
    }

    uint32 SecureBelow(uint32 n)
    {
        // Rejection sampling keeps every value equally likely.
        uint32 const limit = std::numeric_limits<uint32>::max() - std::numeric_limits<uint32>::max() % n;
        for (;;)
        {
            uint32 value;
            Acore::Crypto::GetRandomBytes(reinterpret_cast<uint8*>(&value), sizeof(value));
            if (value < limit)
                return value % n;
        }
    }

    std::string GoldText(uint64 copper)
    {
        return Acore::StringFormat("{}g {}s {}c", copper / GOLD, copper % GOLD / SILVER, copper % SILVER);
    }

    Allowance& AllowanceFor(uint32 account)
    {
        auto [it, inserted] = allowances.try_emplace(account);
        if (inserted)
            if (QueryResult result = CharacterDatabase.Query(
                "SELECT `day`, `wagered`, `excluded_until` FROM `casino_player` WHERE `account` = {}", account))
            {
                Field* fields = result->Fetch();
                it->second = { fields[0].Get<uint32>(), fields[1].Get<uint64>(), fields[2].Get<uint32>() };
            }

        uint32 const today = Now() / SECONDS_PER_DAY;
        if (it->second.day != today)
        {
            it->second.day = today;
            it->second.wagered = 0;
        }
        return it->second;
    }

    void ForgetAllowance(uint32 account)
    {
        allowances.erase(account);
    }

    void SaveAllowance(CharacterDatabaseTransaction trans, uint32 account, Allowance const& allowance)
    {
        trans->Append(Acore::StringFormat(
            "INSERT INTO `casino_player` (`account`, `day`, `wagered`, `excluded_until`) VALUES ({}, {}, {}, {}) "
            "ON DUPLICATE KEY UPDATE `day` = VALUES(`day`), `wagered` = VALUES(`wagered`), "
            "`excluded_until` = VALUES(`excluded_until`)",
            account, allowance.day, allowance.wagered, allowance.excludedUntil));
    }

    void AppendLedger(CharacterDatabaseTransaction trans, uint64 round, ObjectGuid::LowType guid, int64 playerDelta,
        int64 houseDelta, char const* reason)
    {
        trans->Append(Acore::StringFormat(
            "INSERT INTO `casino_ledger` (`round`, `guid`, `player_delta`, `house_delta`, `reason`) "
            "VALUES ({}, {}, {}, {}, '{}')", round, guid, playerDelta, houseDelta, reason));
    }

    void Send(Player* player, std::string const& body)
    {
        WorldPacket data;
        ChatHandler::BuildChatPacket(data, CHAT_MSG_WHISPER, LANG_ADDON, player, player, PREFIX_OUT + body);
        player->SendDirectMessage(&data);
    }

    void SendTo(ObjectGuid guid, std::string const& body)
    {
        if (Player* player = ObjectAccessor::FindConnectedPlayer(guid))
            Send(player, body);
    }

    void Refuse(Player* player, char const* code)
    {
        Send(player, Acore::StringFormat("E:{}", code));
    }

    bool Near(Player* player, ObjectGuid npc)
    {
        // the dealer NPC, or a casino table gameobject standing in for one
        WorldObject* dealer = ObjectAccessor::GetWorldObject(*player, npc);
        Creature* creature = dealer ? dealer->ToCreature() : nullptr;
        return dealer && (!creature || creature->IsAlive()) && player->IsWithinDistInMap(dealer, settings.maxDistance);
    }

    char const* StakeRefusal(Player* player, uint64 stake)
    {
        if (!Open())
            return "closed";
        if (player->GetDigitalInventory().Failed())
            return "state";
        Allowance const& allowance = AllowanceFor(player->GetSession()->GetAccountId());
        if (allowance.excludedUntil > Now())
            return "excluded";
        if (settings.dailyCap && allowance.wagered + stake > settings.dailyCap)
            return "daily";
        if (stake > uint64(std::numeric_limits<int32>::max()) || !player->HasEnoughMoney(uint32(stake)))
            return "money";
        return nullptr;
    }

    void TakeStake(Player* player, CharacterDatabaseTransaction trans, uint64 round, char const* game,
        uint32 dealerEntry, uint64 stake, std::string const& note)
    {
        uint32 const account = player->GetSession()->GetAccountId();
        ObjectGuid::LowType const guid = player->GetGUID().GetCounter();
        Allowance& allowance = AllowanceFor(account);
        allowance.wagered += stake;
        player->ModifyMoney(-int32(stake));
        trans->Append(Acore::StringFormat(
            "INSERT INTO `casino_round` (`id`, `game`, `guid`, `account`, `dealer`, `wagered`, `state`, `result`) "
            "VALUES ({}, '{}', {}, {}, {}, {}, {}, '{}')",
            round, game, guid, account, dealerEntry, stake, uint32(ROUND_OPEN), note.substr(0, 128)));
        AppendLedger(trans, round, guid, -int64(stake), 0, "bet");
        SaveAllowance(trans, account, allowance);
        player->SaveGoldToDB(trans);
    }

    bool Pay(ObjectGuid guid, CharacterDatabaseTransaction trans, uint64 copper, std::string const& body)
    {
        if (!copper)
            return false;
        Player* player = ObjectAccessor::FindConnectedPlayer(guid);
        if (player && copper <= uint64(std::numeric_limits<int32>::max()) && player->ModifyMoney(int32(copper), false))
        {
            player->SaveGoldToDB(trans);
            return false;
        }
        // Offline, or above the gold cap (or a trial cap): the mail holds it instead of losing it. A sum larger than
        // one mail can carry goes in several.
        constexpr uint64 MAIL_LIMIT = 2000000000;
        while (copper)
        {
            uint64 const part = std::min(copper, MAIL_LIMIT);
            MailDraft("Esteria Casino", body)
                .AddMoney(uint32(part))
                .SendMailTo(trans, MailReceiver(player, guid.GetCounter()),
                    MailSender(MAIL_NORMAL, 0, MAIL_STATIONERY_GM));
            copper -= part;
        }
        return true;
    }

    void CloseRound(CharacterDatabaseTransaction trans, uint64 round, uint64 paid, std::string const& result)
    {
        trans->Append(Acore::StringFormat(
            "UPDATE `casino_round` SET `paid` = {}, `state` = {}, `result` = '{}', `settled` = NOW() "
            "WHERE `id` = {} AND `state` = {}", paid, uint32(ROUND_SETTLED), result.substr(0, 128), round,
            uint32(ROUND_OPEN)));
    }

    void BookHouse(CharacterDatabaseTransaction trans, int64 delta, uint64 round)
    {
        // Without the lottery tables the share stays with the house: a failing UPDATE would sink the whole commit.
        int64 const share = delta > 0 && LotteryLoaded() ? delta * int64(settings.lotteryShareBp) / 10000 : 0;
        house.bankroll -= share;
        trans->Append(Acore::StringFormat(
            "UPDATE `casino_house` SET `bankroll` = `bankroll` + {}, `earned` = `earned` + {} WHERE `id` = 1",
            delta - share, delta));
        if (share > 0)
        {
            AddToLottery(trans, uint64(share));
            AppendLedger(trans, round, 0, 0, -share, "lottery");
        }
    }
}

namespace EsteriaCasino::Server
{
    void ForgetAllowance(uint32 account);
}

namespace
{
    using namespace EsteriaCasino::Server;

    constexpr char PREFIX_IN[] = "ECAS\t";
    constexpr size_t PREFIX_LEN = sizeof(PREFIX_IN) - 1;
    // The largest payout of each game must fit ModifyMoney's int32: a split, doubled, won blackjack round pays back
    // 8x the opening stake, a dragon line 500x, a dice call 5.8x.
    constexpr uint64 INT32_COPPER = uint64(std::numeric_limits<int32>::max());
    constexpr uint64 BLACKJACK_STAKE_LIMIT = INT32_COPPER / 8;
    constexpr uint64 SLOTS_STAKE_LIMIT = INT32_COPPER / EsteriaCasino::Slots::MaxPay;
    constexpr uint64 DICE_STAKE_LIMIT = INT32_COPPER / 6;
    constexpr uint32 SLOTS_LOSS_MULTIPLIER = EsteriaCasino::Slots::MaxPay - 1;

    enum class Game : uint8
    {
        Blackjack,
        Slots,
        Dice,
    };

    char const* GameName(Game game)
    {
        switch (game)
        {
            case Game::Slots: return "slots";
            case Game::Dice: return "dice";
            default: return "blackjack";
        }
    }

    enum GossipAction : uint32
    {
        GOSSIP_ACTION_SIT = 1,
    };

    struct Limits
    {
        uint64 minBet;
        uint64 maxBet;
    };

    struct Config
    {
        Limits blackjack { 1000, 10000000 };
        Limits slots { 1000, 1000000 };
        Limits dice { 1000, 5000000 };
        bool hitSoft17 = false;
    } config;

    struct Seat
    {
        Game game = Game::Blackjack;
        ObjectGuid dealer;
        uint32 dealerEntry = 0;
        BJ::Shoe shoe { 6 };
        std::optional<BJ::Round> round;
        uint64 roundId = 0; // 0 once the round is settled
        uint64 reserve = 0;
    };

    std::unordered_map<ObjectGuid, Seat> seats;

    // The stake a table takes right now from this account: its limit, what the house can cover, the daily cap.
    uint64 TableMax(uint32 account, uint32 lossMultiplier, Limits const& limits)
    {
        uint64 max = house.MaxBet(lossMultiplier, limits.maxBet);
        if (settings.dailyCap)
        {
            Allowance const& allowance = AllowanceFor(account);
            max = std::min(max, settings.dailyCap > allowance.wagered ? settings.dailyCap - allowance.wagered : 0);
        }
        return max;
    }

    struct TableRules
    {
        uint32 lossMultiplier;
        Limits const& limits;
    };

    TableRules RulesOf(Game game)
    {
        switch (game)
        {
            case Game::Slots: return { SLOTS_LOSS_MULTIPLIER, config.slots };
            case Game::Dice: return { EsteriaCasino::Dice::MaxHouseLossMultiplier, config.dice };
            default: return { BJ::MaxHouseLossMultiplier, config.blackjack };
        }
    }

    uint64 TableMax(Player* player, Game game)
    {
        TableRules const rules = RulesOf(game);
        return TableMax(player->GetSession()->GetAccountId(), rules.lossMultiplier, rules.limits);
    }

    template<typename Container>
    std::string Joined(Container const& values)
    {
        std::string out;
        for (auto const& value : values)
            out += (out.empty() ? "" : ",") + std::to_string(value);
        return out;
    }

    // Opens the window; slots and dice publish their whole pay table and exact return with it.
    void SendOpen(Player* player, Game game)
    {
        namespace S = EsteriaCasino::Slots;
        namespace D = EsteriaCasino::Dice;
        uint64 const max = TableMax(player, game);
        switch (game)
        {
            case Game::Slots:
                return Send(player, Acore::StringFormat("O:slots:{}:{}:{}:{}:{}:{}", config.slots.minBet, max,
                    Joined(S::Weights), Joined(S::TriplePay), S::MixedCoinPay, S::ReturnBasisPoints()));
            case Game::Dice:
            {
                std::array<uint32, D::CallCount> returns {};
                for (size_t i = 0; i < D::CallCount; ++i)
                    returns[i] = D::CallReturnBasisPoints(D::Call(i));
                return Send(player, Acore::StringFormat("O:dice:{}:{}:{}:{}", config.dice.minBet, max,
                    Joined(D::ReturnBasisPoints), Joined(returns)));
            }
            default:
                return Send(player, Acore::StringFormat("O:bj:{}:{}:{}", config.blackjack.minBet, max,
                    config.hitSoft17 ? 1 : 0));
        }
    }

    std::string Cards(std::vector<BJ::Card> const& cards)
    {
        std::string out;
        for (BJ::Card card : cards)
        {
            if (!out.empty())
                out += ',';
            out += BJ::Code(card);
        }
        return out;
    }

    char Status(BJ::Round const& round, BJ::Hand const& hand)
    {
        if (round.Finished())
            switch (round.OutcomeOf(hand))
            {
                case BJ::Outcome::Blackjack: return 'J';
                case BJ::Outcome::Win: return 'W';
                case BJ::Outcome::Push: return 'U';
                default: return 'L';
            }
        if (hand.IsBust())
            return 'B';
        return hand.done ? 'D' : 'P';
    }

    // `id` names the round; Settle passes it explicitly because it has already cleared seat.roundId.
    void SendTable(Player* player, Seat const& seat, uint64 id = 0)
    {
        if (!seat.round)
            return Send(player, "T:0");

        BJ::Round const& round = *seat.round;
        bool const finished = round.Finished();
        std::vector<BJ::Card> const& dealer = round.Dealer();
        std::string dealerCards = finished ? Cards(dealer) : BJ::Code(dealer[0]) + ",??";
        uint32 const dealerTotal = finished ? BJ::Evaluate(dealer).value : BJ::Evaluate({ dealer[0] }).value;

        std::string hands;
        for (BJ::Hand const& hand : round.Hands())
        {
            if (!hands.empty())
                hands += ';';
            BJ::Total const total = BJ::Evaluate(hand.cards);
            hands += Acore::StringFormat("{}|{}|{}|{}|{}", Cards(hand.cards), total.value, total.soft ? 1 : 0,
                hand.stake, Status(round, hand));
        }

        std::string actions;
        if (round.CanHit())
            actions += 'H';
        if (round.CanStand())
            actions += 'S';
        if (round.CanDouble())
            actions += 'D';
        if (round.CanSplit())
            actions += 'P';

        Send(player, Acore::StringFormat("T:{}:{}:{}:{}:{}:{}:{}", id ? id : seat.roundId, finished ? 2 : 1,
            round.Active(), dealerCards, dealerTotal, hands, actions));
    }

    std::string Summary(BJ::Round const& round)
    {
        std::string out = "D " + Cards(round.Dealer());
        for (BJ::Hand const& hand : round.Hands())
            out += " P " + Cards(hand.cards);
        return out.substr(0, 128);
    }

    // Pays the round out, books the house's result and closes it. Runs exactly once per round: roundId is cleared.
    void Settle(Player* player, Seat& seat)
    {
        BJ::Round const& round = *seat.round;
        uint64 const id = seat.roundId;
        uint64 const wagered = round.Wagered();
        uint64 const paid = round.Paid();
        int64 const delta = house.Settle(seat.reserve, wagered, paid);
        seat.roundId = 0;
        seat.reserve = 0;

        ObjectGuid::LowType const guid = player->GetGUID().GetCounter();
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        bool const mailed = Pay(player->GetGUID(), trans, paid,
            Acore::StringFormat("Your blackjack winnings from round {}.", id));
        CloseRound(trans, id, paid, Summary(round));
        BookHouse(trans, delta, id);
        AppendLedger(trans, id, guid, mailed ? 0 : int64(paid), delta, mailed ? "mailed" : "settle");
        player->SaveGoldToDB(trans);
        CharacterDatabase.CommitTransaction(trans);

        LOG_INFO("module.casino", "{} blackjack round {}: wagered {} paid {} (house {:+}){}", player->GetName(), id,
            wagered, paid, delta, mailed ? " by mail" : "");
        SendTable(player, seat, id);
        Send(player, Acore::StringFormat("R:{}:{}:{}:{}", id, wagered, paid, mailed ? 1 : 0));
        Send(player, Acore::StringFormat("M:{}", TableMax(player, Game::Blackjack)));
    }

    void AfterAction(Player* player, Seat& seat)
    {
        if (seat.round->Finished())
            Settle(player, seat);
        else
            SendTable(player, seat);
    }

    bool Playing(Seat const& seat)
    {
        return seat.roundId != 0;
    }

    // Checks shared by every opening stake; returns the refusal code, or nullptr when the bet may be taken.
    char const* BetRefusal(Player* player, Seat const& seat, uint64 stake)
    {
        if (!settings.enabled || !houseLoaded)
            return "closed";
        if (seat.game == Game::Blackjack && Playing(seat))
            return "playing";
        if (!Near(player, seat.dealer))
            return "range";
        if (player->GetDigitalInventory().Failed())
            return "state";
        if (AllowanceFor(player->GetSession()->GetAccountId()).excludedUntil > Now())
            return "excluded";
        if (stake < RulesOf(seat.game).limits.minBet)
            return "min";
        if (stake > TableMax(player, seat.game))
            return "max";
        if (!player->HasEnoughMoney(uint32(stake)))
            return "money";
        return nullptr;
    }

    // Slots and dice: the stake, the payout, the house's result and the receipt commit together.
    // `outcome` is the reply's game-specific fields ("<a>:<b>:<c>" or "<d1>:<d2>:<call>").
    void PlayInstant(Player* player, Seat& seat, uint64 stake, uint64 paid, std::string const& result,
        char const* reply, std::string const& outcome)
    {
        uint64 const id = NextRoundId();
        uint32 const account = player->GetSession()->GetAccountId();
        ObjectGuid::LowType const guid = player->GetGUID().GetCounter();
        Allowance& allowance = AllowanceFor(account);
        allowance.wagered += stake;
        int64 const delta = house.Settle(0, stake, paid);

        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        player->ModifyMoney(-int32(stake));
        bool const mailed = Pay(player->GetGUID(), trans, paid,
            Acore::StringFormat("Your {} winnings from round {}.", GameName(seat.game), id));
        trans->Append(Acore::StringFormat(
            "INSERT INTO `casino_round` (`id`, `game`, `guid`, `account`, `dealer`, `wagered`, `paid`, `state`, "
            "`result`, `settled`) VALUES ({}, '{}', {}, {}, {}, {}, {}, {}, '{}', NOW())",
            id, GameName(seat.game), guid, account, seat.dealerEntry, stake, paid, uint32(ROUND_SETTLED), result));
        BookHouse(trans, delta, id);
        AppendLedger(trans, id, guid, -int64(stake), 0, "bet");
        AppendLedger(trans, id, guid, mailed ? 0 : int64(paid), delta, mailed ? "mailed" : "settle");
        SaveAllowance(trans, account, allowance);
        player->SaveGoldToDB(trans);
        CharacterDatabase.CommitTransaction(trans);

        LOG_INFO("module.casino", "{} {} round {}: {}, wagered {} paid {} (house {:+}){}", player->GetName(),
            GameName(seat.game), id, result, stake, paid, delta, mailed ? " by mail" : "");
        Send(player, Acore::StringFormat("{}:{}:{}:{}:{}:{}", reply, id, outcome, stake, paid, mailed ? 1 : 0));
        Send(player, Acore::StringFormat("M:{}", TableMax(player, seat.game)));
    }

    void Spin(Player* player, Seat& seat, uint64 stake)
    {
        namespace S = EsteriaCasino::Slots;
        if (char const* refusal = BetRefusal(player, seat, stake))
            return Refuse(player, refusal);
        uint8 const a = S::Symbol(SecureBelow(S::TotalWeight()));
        uint8 const b = S::Symbol(SecureBelow(S::TotalWeight()));
        uint8 const c = S::Symbol(SecureBelow(S::TotalWeight()));
        PlayInstant(player, seat, stake, stake * S::Pay(a, b, c), Acore::StringFormat("line {} {} {}", a, b, c),
            "SR", Acore::StringFormat("{}:{}:{}", a, b, c));
    }

    void Roll(Player* player, Seat& seat, uint64 stake, uint32 call)
    {
        namespace D = EsteriaCasino::Dice;
        if (call >= D::CallCount)
            return Refuse(player, "action");
        if (char const* refusal = BetRefusal(player, seat, stake))
            return Refuse(player, refusal);
        uint8 const d1 = uint8(1 + SecureBelow(6));
        uint8 const d2 = uint8(1 + SecureBelow(6));
        PlayInstant(player, seat, stake, D::Paid(stake, D::Call(call), d1, d2),
            Acore::StringFormat("call {} rolled {}+{}", call, d1, d2), "DR",
            Acore::StringFormat("{}:{}:{}", d1, d2, call));
    }

    void PlaceBet(Player* player, Seat& seat, uint64 stake)
    {
        if (char const* refusal = BetRefusal(player, seat, stake))
            return Refuse(player, refusal);
        uint32 const account = player->GetSession()->GetAccountId();
        Allowance& allowance = AllowanceFor(account);
        uint64 const worst = stake * BJ::MaxHouseLossMultiplier;
        if (!house.Reserve(worst))
            return Refuse(player, "house");

        if (seat.shoe.NeedsShuffle())
            seat.shoe.Shuffle(SecureBelow);

        uint64 const id = NextRoundId();
        ObjectGuid::LowType const guid = player->GetGUID().GetCounter();
        allowance.wagered += stake;

        // The stake leaves the character and enters escrow in one commit; the deal happens only after it.
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        player->ModifyMoney(-int32(stake));
        trans->Append(Acore::StringFormat(
            "INSERT INTO `casino_round` (`id`, `game`, `guid`, `account`, `dealer`, `wagered`, `state`) "
            "VALUES ({}, '{}', {}, {}, {}, {}, {})",
            id, GameName(Game::Blackjack), guid, account, seat.dealerEntry, stake, uint32(ROUND_OPEN)));
        AppendLedger(trans, id, guid, -int64(stake), 0, "bet");
        SaveAllowance(trans, account, allowance);
        player->SaveGoldToDB(trans);
        CharacterDatabase.CommitTransaction(trans);

        seat.roundId = id;
        seat.reserve = worst;
        seat.round.emplace(config.hitSoft17);
        seat.round->Start(seat.shoe, stake);
        AfterAction(player, seat);
    }

    // Double and split put up one more copy of the active hand's stake. The opening reservation already covers it.
    bool TakeExtraStake(Player* player, Seat& seat, char const* reason)
    {
        uint64 const extra = seat.round->ExtraStake();
        uint32 const account = player->GetSession()->GetAccountId();
        Allowance& allowance = AllowanceFor(account);
        if (settings.dailyCap && allowance.wagered + extra > settings.dailyCap)
        {
            Refuse(player, "daily");
            return false;
        }
        if (!player->HasEnoughMoney(uint32(extra)))
        {
            Refuse(player, "money");
            return false;
        }

        allowance.wagered += extra;
        ObjectGuid::LowType const guid = player->GetGUID().GetCounter();
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        player->ModifyMoney(-int32(extra));
        trans->Append(Acore::StringFormat(
            "UPDATE `casino_round` SET `wagered` = `wagered` + {} WHERE `id` = {} AND `state` = {}",
            extra, seat.roundId, uint32(ROUND_OPEN)));
        AppendLedger(trans, seat.roundId, guid, -int64(extra), 0, reason);
        SaveAllowance(trans, account, allowance);
        player->SaveGoldToDB(trans);
        CharacterDatabase.CommitTransaction(trans);
        return true;
    }

    void Act(Player* player, Seat& seat, char action)
    {
        if (!Playing(seat))
            return Refuse(player, "noround");
        BJ::Round& round = *seat.round;
        switch (action)
        {
            case 'H':
                round.Hit(seat.shoe);
                break;
            case 'S':
                round.Stand(seat.shoe);
                break;
            case 'D':
                if (!round.CanDouble())
                    return Refuse(player, "action");
                if (!TakeExtraStake(player, seat, "double"))
                    return;
                round.Double(seat.shoe);
                break;
            case 'P':
                if (!round.CanSplit())
                    return Refuse(player, "action");
                if (!TakeExtraStake(player, seat, "split"))
                    return;
                round.Split(seat.shoe);
                break;
            default:
                return Refuse(player, "action");
        }
        AfterAction(player, seat);
    }

    void HandleMessage(Player* player, std::string_view body)
    {
        // Chess, checkers, poker and the lottery own their commands; HI reaches every game.
        size_t const colon = body.find(':');
        std::string_view const command = body.substr(0, colon);
        std::string_view const args = colon == std::string_view::npos ? std::string_view() : body.substr(colon + 1);
        if (HandleBoardMessage(player, command, args) || HandlePokerMessage(player, command, args) ||
            HandleLotteryMessage(player, command, args))
            return;

        auto it = seats.find(player->GetGUID());
        if (body == "HI")
        {
            if (it != seats.end() && Playing(it->second))
            {
                SendOpen(player, Game::Blackjack);
                SendTable(player, it->second);
            }
            return;
        }
        if (it == seats.end())
            return Refuse(player, "noseat");
        Seat& seat = it->second;

        if (body == "L")
        {
            // An open blackjack hand keeps the seat: it waits at the dealer while the window is closed.
            if (Playing(seat))
                return;
            seats.erase(it);
            return Send(player, "C");
        }
        if (seat.game == Game::Slots && body.starts_with("SP:"))
        {
            std::optional<uint64> stake = Acore::StringTo<uint64>(body.substr(3));
            if (!stake)
                return Refuse(player, "amount");
            return Spin(player, seat, *stake);
        }
        if (seat.game == Game::Dice && body.starts_with("DR:"))
        {
            std::vector<std::string_view> parts = Acore::Tokenize(body.substr(3), ':', true);
            std::optional<uint64> stake = parts.size() == 2 ? Acore::StringTo<uint64>(parts[0]) : std::nullopt;
            std::optional<uint32> call = parts.size() == 2 ? Acore::StringTo<uint32>(parts[1]) : std::nullopt;
            if (!stake || !call)
                return Refuse(player, "amount");
            return Roll(player, seat, *stake, *call);
        }
        if (seat.game != Game::Blackjack)
            return Refuse(player, "unknown");
        if (body.starts_with("B:"))
        {
            std::optional<uint64> stake = Acore::StringTo<uint64>(body.substr(2));
            if (!stake)
                return Refuse(player, "amount");
            return PlaceBet(player, seat, *stake);
        }
        if (body.size() == 1)
            return Act(player, seat, body[0]);
        Refuse(player, "unknown");
    }

    // Startup: create the house row, load the bankroll and refund every round a crash left open.
    void LoadHouse()
    {
        if (!Acore::WorldPvp::CanUseBountyEscrow())
        {
            LOG_ERROR("module.casino", "The casino needs CharacterDatabase.WorkerThreads = 1 and a non-clustered "
                "realm, so gold commits stay in order. Casino closed.");
            return;
        }
        CharacterDatabase.DirectExecute("INSERT IGNORE INTO `casino_house` (`id`) VALUES (1)");
        QueryResult result = CharacterDatabase.Query("SELECT `bankroll` FROM `casino_house` WHERE `id` = 1");
        if (!result)
        {
            LOG_ERROR("module.casino", "casino_house is missing; apply mod-esteria-casino's characters SQL. "
                "Casino closed.");
            return;
        }
        house.bankroll = result->Fetch()[0].Get<int64>();

        if (QueryResult max = CharacterDatabase.Query("SELECT MAX(`id`) FROM `casino_round`"))
            if (!max->Fetch()[0].IsNull())
                nextRoundId = max->Fetch()[0].Get<uint64>() + 1;

        if (QueryResult open = CharacterDatabase.Query(Acore::StringFormat(
            "SELECT `id`, `guid`, `wagered` FROM `casino_round` WHERE `state` = {}", uint32(ROUND_OPEN))))
        {
            CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
            uint32 count = 0;
            do
            {
                Field* fields = open->Fetch();
                uint64 const id = fields[0].Get<uint64>();
                ObjectGuid::LowType const guid = fields[1].Get<uint32>();
                uint64 const wagered = fields[2].Get<uint64>();
                if (wagered)
                    MailDraft("Esteria Casino refund", Acore::StringFormat(
                        "Round {} was interrupted by a server restart. Your full stake is returned.", id))
                        .AddMoney(uint32(wagered))
                        .SendMailTo(trans, MailReceiver(guid), MailSender(MAIL_NORMAL, 0, MAIL_STATIONERY_GM));
                trans->Append(Acore::StringFormat(
                    "UPDATE `casino_round` SET `paid` = {}, `state` = {}, `settled` = NOW() "
                    "WHERE `id` = {} AND `state` = {}",
                    wagered, uint32(ROUND_REFUNDED), id, uint32(ROUND_OPEN)));
                AppendLedger(trans, id, guid, 0, 0, "refund");
                ++count;
            } while (open->NextRow());
            CharacterDatabase.DirectCommitTransaction(trans);
            LOG_WARN("module.casino", "Refunded {} casino round(s) left open by the last shutdown.", count);
        }

        houseLoaded = true;
        LOG_INFO("module.casino", "Casino house loaded: bankroll {}.",
            GoldText(uint64(std::max<int64>(house.bankroll, 0))));
    }
}

namespace
{
    // Sit at a house game (blackjack, slots, dice) run by `dealer`: an NPC or a table gameobject.
    void OpenTable(Player* player, WorldObject* dealer, Game game)
    {
        Seat& seat = seats[player->GetGUID()];
        // An open blackjack hand waits at its table: slots and dice still open, and any blackjack dealer resumes it.
        seat.game = game;
        seat.dealer = dealer->GetGUID();
        seat.dealerEntry = dealer->GetEntry();
        SendOpen(player, seat.game);
        if (seat.game == Game::Blackjack)
            SendTable(player, seat);
        else if (Playing(seat))
            Send(player, "W");
    }
}

// One script per game. The dealer only opens the window; every bet checks the distance to it again.
class npc_esteria_casino_table : public CreatureScript
{
public:
    npc_esteria_casino_table(char const* name, Game game, char const* option)
        : CreatureScript(name), _game(game), _option(option) { }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        ClearGossipMenuFor(player);
        if (settings.enabled && houseLoaded)
            AddGossipItemFor(player, GOSSIP_ICON_MONEY_BAG, _option, GOSSIP_SENDER_MAIN, GOSSIP_ACTION_SIT);
        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature);
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* creature, uint32 /*sender*/, uint32 action) override
    {
        CloseGossipMenuFor(player);
        if (action == GOSSIP_ACTION_SIT && settings.enabled && houseLoaded)
            OpenTable(player, creature, _game);
        return true;
    }

private:
    Game _game;
    char const* _option;
};

// Casino furniture (housing decor or world spawns): a table gameobject opens its game the way its dealer NPC does.
class go_esteria_casino_table : public GameObjectScript
{
public:
    enum Kind { House, Board, Poker };

    go_esteria_casino_table(char const* name, Kind kind, Game game, char const* option)
        : GameObjectScript(name), _kind(kind), _game(game), _option(option) { }

    bool OnGossipHello(Player* player, GameObject* go) override
    {
        ClearGossipMenuFor(player);
        if (_kind == House ? settings.enabled && houseLoaded : Open())
            AddGossipItemFor(player, GOSSIP_ICON_MONEY_BAG, _option, GOSSIP_SENDER_MAIN, GOSSIP_ACTION_SIT);
        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, go->GetGUID());
        return true;
    }

    bool OnGossipSelect(Player* player, GameObject* go, uint32 /*sender*/, uint32 action) override
    {
        CloseGossipMenuFor(player);
        if (action != GOSSIP_ACTION_SIT)
            return true;
        if (_kind == House && settings.enabled && houseLoaded)
            OpenTable(player, go, _game);
        else if (_kind == Board && Open())
            OpenBoardLobby(player, go);
        else if (_kind == Poker && Open())
            OpenPoker(player, go);
        return true;
    }

private:
    Kind _kind;
    Game _game;
    char const* _option;
};

class esteria_casino_player : public PlayerScript
{
public:
    esteria_casino_player() : PlayerScript("esteria_casino_player",
        { PLAYERHOOK_ON_BEFORE_SEND_CHAT_MESSAGE, PLAYERHOOK_CAN_PLAYER_USE_PRIVATE_CHAT, PLAYERHOOK_ON_LOGIN,
          PLAYERHOOK_ON_LOGOUT }) { }

    // A player back within the disconnect grace rejoins their chess or checkers match.
    void OnPlayerLogin(Player* player) override
    {
        BoardLogin(player);
    }

    void OnPlayerBeforeSendChatMessage(Player* player, uint32& /*type*/, uint32& lang, std::string& msg) override
    {
        if (lang != LANG_ADDON || !msg.starts_with(PREFIX_IN))
            return;
        HandleMessage(player, std::string_view(msg).substr(PREFIX_LEN));
    }

    bool OnPlayerCanUseChat(Player* /*player*/, uint32 /*type*/, uint32 lang, std::string& msg, Player* /*receiver*/)
        override
    {
        return !(lang == LANG_ADDON && msg.starts_with(PREFIX_IN));
    }

    // Leaving mid-round stands on every open blackjack hand and settles it before the save; a poker seat cashes
    // out; a chess or checkers match starts its disconnect grace.
    void OnPlayerLogout(Player* player) override
    {
        BoardLogout(player);
        PokerLogout(player);
        auto it = seats.find(player->GetGUID());
        if (it != seats.end())
        {
            if (Playing(it->second))
            {
                it->second.round->StandAll(it->second.shoe);
                Settle(player, it->second);
            }
            seats.erase(it);
        }
        ForgetAllowance(player->GetSession()->GetAccountId());
    }
};

class esteria_casino_world : public WorldScript
{
public:
    esteria_casino_world() : WorldScript("esteria_casino_world",
        { WORLDHOOK_ON_AFTER_CONFIG_LOAD, WORLDHOOK_ON_STARTUP, WORLDHOOK_ON_UPDATE }) { }

    void OnAfterConfigLoad(bool reload) override
    {
        settings.enabled = sConfigMgr->GetOption<bool>("EsteriaCasino.Enable", false);
        auto limits = [](char const* game, uint64 min, uint64 max, uint64 cap)
        {
            std::string const prefix = Acore::StringFormat("EsteriaCasino.{}.", game);
            uint64 const minBet = sConfigMgr->GetOption<uint64>(prefix + "MinBet", min);
            uint64 const maxBet = sConfigMgr->GetOption<uint64>(prefix + "MaxBet", max);
            return Limits { std::max<uint64>(1, minBet), std::min(cap, maxBet) };
        };
        config.blackjack = limits("Blackjack", 1000, 10000000, BLACKJACK_STAKE_LIMIT);
        config.slots = limits("Slots", 1000, 1000000, SLOTS_STAKE_LIMIT);
        config.dice = limits("Dice", 1000, 5000000, DICE_STAKE_LIMIT);
        config.hitSoft17 = sConfigMgr->GetOption<bool>("EsteriaCasino.Blackjack.HitSoft17", false);
        settings.dailyCap = sConfigMgr->GetOption<uint64>("EsteriaCasino.DailyWagerCap", 100000000);
        settings.maxDistance = sConfigMgr->GetOption<float>("EsteriaCasino.MaxDistance", 12.0f);
        settings.lotteryShareBp =
            std::min(10000u, sConfigMgr->GetOption<uint32>("EsteriaCasino.Lottery.HouseShare", 1000));
        LoadBoardConfig();
        LoadPokerConfig();
        LoadLotteryConfig();
        if (reload && settings.enabled && !houseLoaded)
            LOG_WARN("module.casino", "EsteriaCasino.Enable takes effect at the next restart.");
    }

    void OnStartup() override
    {
        if (settings.enabled)
            LoadHouse();
        if (houseLoaded)
            LoadLottery();
    }

    void OnUpdate(uint32 diff) override
    {
        if (!houseLoaded)
            return;
        BoardUpdate(diff);
        PokerUpdate(diff);
        LotteryUpdate();
    }
};

class esteria_casino_commands : public CommandScript
{
public:
    esteria_casino_commands() : CommandScript("esteria_casino_commands") { }

    ChatCommandTable GetCommands() const override
    {
        static ChatCommandTable casino =
        {
            { "status", HandleStatus, SEC_PLAYER, Console::No },
            { "optout", HandleOptOut, SEC_PLAYER, Console::No },
            { "house", HandleHouse, SEC_ADMINISTRATOR, Console::No },
            { "fund", HandleFund, SEC_ADMINISTRATOR, Console::No },
            { "withdraw", HandleWithdraw, SEC_ADMINISTRATOR, Console::No },
            { "round", HandleRound, SEC_GAMEMASTER, Console::No },
        };
        return { { "casino", casino } };
    }

    static bool Ready(ChatHandler* handler)
    {
        if (houseLoaded)
            return true;
        handler->SendErrorMessage("The casino is not running (EsteriaCasino.Enable, then restart).");
        return false;
    }

    static bool HandleStatus(ChatHandler* handler)
    {
        if (!Ready(handler))
            return false;
        Allowance const& allowance = AllowanceFor(handler->GetSession()->GetAccountId());
        if (settings.dailyCap)
            handler->PSendSysMessage("Staked today: {} of {}.", GoldText(allowance.wagered),
                GoldText(settings.dailyCap));
        else
            handler->PSendSysMessage("Staked today: {}.", GoldText(allowance.wagered));
        if (allowance.excludedUntil > Now())
            handler->PSendSysMessage("You are excluded from the casino for another {} hour(s).",
                (allowance.excludedUntil - Now()) / 3600 + 1);
        return true;
    }

    // Self-exclusion: only ever extended, never shortened.
    static bool HandleOptOut(ChatHandler* handler, uint32 days)
    {
        if (!Ready(handler))
            return false;
        if (!days || days > 3650)
        {
            handler->SendErrorMessage("Choose between 1 and 3650 days.");
            return false;
        }
        uint32 const account = handler->GetSession()->GetAccountId();
        Allowance& allowance = AllowanceFor(account);
        allowance.excludedUntil = std::max(allowance.excludedUntil, Now() + days * SECONDS_PER_DAY);
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        SaveAllowance(trans, account, allowance);
        CharacterDatabase.CommitTransaction(trans);
        handler->PSendSysMessage("You will not be able to place casino bets for {} day(s). This cannot be shortened.",
            (allowance.excludedUntil - Now() + SECONDS_PER_DAY - 1) / SECONDS_PER_DAY);
        return true;
    }

    static bool HandleHouse(ChatHandler* handler)
    {
        if (!Ready(handler))
            return false;
        uint32 open = 0;
        for (auto const& [guid, seat] : seats)
            open += Playing(seat) ? 1 : 0;
        handler->PSendSysMessage("Casino bankroll {} copper ({} reserved for {} open round(s), {} available).",
            house.bankroll, house.reserved, open, house.Available());
        handler->PSendSysMessage("Lottery pool {}.", GoldText(LotteryPool()));
        handler->PSendSysMessage("Table limits now: blackjack {}, slots {}, dice {}.",
            GoldText(house.MaxBet(BJ::MaxHouseLossMultiplier, config.blackjack.maxBet)),
            GoldText(house.MaxBet(SLOTS_LOSS_MULTIPLIER, config.slots.maxBet)),
            GoldText(house.MaxBet(EsteriaCasino::Dice::MaxHouseLossMultiplier, config.dice.maxBet)));
        return true;
    }

    // Moves the GM character's own gold into the house: the bankroll is never minted.
    static bool HandleFund(ChatHandler* handler, uint32 gold)
    {
        if (!Ready(handler))
            return false;
        Player* player = handler->GetSession()->GetPlayer();
        uint64 const copper = uint64(gold) * GOLD;
        if (!gold || copper > uint64(std::numeric_limits<int32>::max()) || !player->HasEnoughMoney(uint32(copper)))
        {
            handler->SendErrorMessage("You don't carry that much gold.");
            return false;
        }
        if (!MoveHouseGold(player, -int64(copper), "fund"))
            return false;
        handler->PSendSysMessage("Moved {} into the casino bankroll.", GoldText(copper));
        return true;
    }

    static bool HandleWithdraw(ChatHandler* handler, uint32 gold)
    {
        if (!Ready(handler))
            return false;
        Player* player = handler->GetSession()->GetPlayer();
        uint64 const copper = uint64(gold) * GOLD;
        if (!gold || copper > house.Available() || copper > uint64(MAX_MONEY_AMOUNT - player->GetMoney()))
        {
            handler->SendErrorMessage("Withdraw at most the unreserved bankroll, and no more than you can carry.");
            return false;
        }
        if (!MoveHouseGold(player, int64(copper), "withdraw"))
        {
            handler->SendErrorMessage("Your character can't hold that much gold.");
            return false;
        }
        handler->PSendSysMessage("Withdrew {} from the casino bankroll.", GoldText(copper));
        return true;
    }

    static bool MoveHouseGold(Player* player, int64 playerDelta, char const* reason)
    {
        if (!player->ModifyMoney(int32(playerDelta)))
            return false;
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        trans->Append(Acore::StringFormat("UPDATE `casino_house` SET `bankroll` = `bankroll` + {} WHERE `id` = 1",
            -playerDelta));
        AppendLedger(trans, 0, player->GetGUID().GetCounter(), playerDelta, -playerDelta, reason);
        player->SaveGoldToDB(trans);
        CharacterDatabase.CommitTransaction(trans);
        house.bankroll -= playerDelta;
        LOG_INFO("module.casino", "{} {} {} copper; bankroll now {}.", player->GetName(), reason,
            playerDelta < 0 ? -playerDelta : playerDelta, house.bankroll);
        return true;
    }

    static bool HandleRound(ChatHandler* handler, uint64 id)
    {
        QueryResult result = CharacterDatabase.Query(Acore::StringFormat(
            "SELECT `game`, `guid`, `wagered`, `paid`, `state`, `result`, `created` FROM `casino_round` "
            "WHERE `id` = {}",
            id));
        if (!result)
        {
            handler->SendErrorMessage("No casino round {}.", id);
            return false;
        }
        Field* f = result->Fetch();
        handler->PSendSysMessage("Round {} ({}) character {}: wagered {} paid {} state {} [{}] {}", id,
            f[0].Get<std::string>(), f[1].Get<uint32>(), f[2].Get<uint64>(), f[3].Get<uint64>(),
            uint32(f[4].Get<uint8>()),
            f[5].Get<std::string>(), f[6].Get<std::string>());
        return true;
    }
};

void AddCasinoBoardScripts();
void AddCasinoPokerScripts();
void AddCasinoLotteryScripts();

void AddSC_esteria_casino()
{
    AddCasinoBoardScripts();
    AddCasinoPokerScripts();
    AddCasinoLotteryScripts();
    new npc_esteria_casino_table("npc_esteria_casino_blackjack", Game::Blackjack,
        "Take a seat at the blackjack table.");
    new npc_esteria_casino_table("npc_esteria_casino_slots", Game::Slots, "Play the slot machine.");
    new npc_esteria_casino_table("npc_esteria_casino_dice", Game::Dice, "Roll Goblin Dice.");
    using Table = go_esteria_casino_table;
    new Table("go_esteria_casino_blackjack", Table::House, Game::Blackjack, "Take a seat at the blackjack table.");
    new Table("go_esteria_casino_slots", Table::House, Game::Slots, "Play the slot machine.");
    new Table("go_esteria_casino_dice", Table::House, Game::Dice, "Roll Goblin Dice.");
    new Table("go_esteria_casino_board", Table::Board, Game::Blackjack, "Play chess or checkers.");
    new Table("go_esteria_casino_poker", Table::Poker, Game::Blackjack, "Join the Hold'em table.");
    new esteria_casino_player();
    new esteria_casino_world();
    new esteria_casino_commands();
}
