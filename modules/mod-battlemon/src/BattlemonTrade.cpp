#include "BattlemonTrade.h"
#include "BattlemonFollower.h"
#include "BattlemonMgr.h"
#include "BattlemonTradeRules.h"

#include "Chat.h"
#include "Config.h"
#include "DatabaseEnv.h"
#include "GameTime.h"
#include "Log.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "StringFormat.h"

#include <algorithm>
#include <cstdlib>
#include <vector>

namespace Rules = BattlemonTradeRules;

namespace
{
constexpr uint32 INVITE_SECONDS = 60;  // an unanswered invitation
constexpr uint32 IDLE_SECONDS = 300;   // an accepted trade nobody touches

uint32 Now()
{
    return static_cast<uint32>(GameTime::GetGameTime().count());
}

void Chat(Player* player, std::string const& text)
{
    if (player && player->GetSession())
        ChatHandler(player->GetSession()).SendSysMessage(text);
}

std::string FormName(BattlemonOwned const& row)
{
    BattlemonForm const* form = sBattlemonMgr->GetBattlemonForm(row.formId);
    return form ? form->name : "a Pokémon";
}
}

BattlemonTrade* BattlemonTrade::instance()
{
    static BattlemonTrade inst;
    return &inst;
}

void BattlemonTrade::LoadConfig()
{
    _enabled = sConfigMgr->GetOption<bool>("Battlemon.Trade.Enable", true);
    _remote = sConfigMgr->GetOption<bool>("Battlemon.Trade.Remote", true);
    _distance = std::clamp(sConfigMgr->GetOption<float>("Battlemon.Trade.Distance", 40.0f), 1.0f, 500.0f);
}

std::shared_ptr<BattlemonTrade::Session> BattlemonTrade::Find(ObjectGuid guid)
{
    std::lock_guard<std::mutex> guard(_lock);
    auto it = _sessions.find(guid);
    return it == _sessions.end() ? nullptr : it->second;
}

bool BattlemonTrade::InRange(Player* a, Player* b) const
{
    return _remote || (a->GetMapId() == b->GetMapId() && a->IsWithinDist(b, _distance));
}

// Both sides get their own view: whose Pokemon is "mine" and who has confirmed.
void BattlemonTrade::Send(Session const& live)
{
    Session s;
    {
        std::lock_guard<std::mutex> guard(_lock);
        s = live;
    }
    for (int i = 0; i < 2; ++i)
    {
        Player* me = ObjectAccessor::FindPlayer(s.side[i]);
        Player* them = ObjectAccessor::FindPlayer(s.side[1 - i]);
        if (!me || !them)
            continue;
        sBattlemonMgr->SendAddonDirect(me, Acore::StringFormat("BM\tTRADE\t{}\t{}\t{}", them->GetName(),
                                                                s.confirmed[i] ? 1 : 0, s.confirmed[1 - i] ? 1 : 0));
        for (int mine = 1; mine >= 0; --mine)
        {
            uint32 const id = s.offer[mine ? i : 1 - i];
            BattlemonOwned const row = id ? sBattlemonMgr->LoadOwnedById(id) : BattlemonOwned();
            std::string line = Acore::StringFormat("BM\tTRADEMON\t{}", mine ? "M" : "T");
            if (row.id)
                line += Acore::StringFormat("\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}", row.formId, row.level,
                                            row.shiny ? 1 : 0, row.gender, row.move[0], row.move[1], row.move[2],
                                            row.move[3], FormName(row));
            sBattlemonMgr->SendAddonDirect(me, line);
        }
    }
}

void BattlemonTrade::Close(std::shared_ptr<Session> const& s, std::string const& why)
{
    {
        std::lock_guard<std::mutex> guard(_lock);
        for (ObjectGuid const& guid : s->side)
        {
            auto it = _sessions.find(guid);
            if (it != _sessions.end() && it->second == s)
                _sessions.erase(it);
        }
    }
    for (ObjectGuid const& guid : s->side)
        if (Player* player = ObjectAccessor::FindPlayer(guid))
        {
            sBattlemonMgr->SendAddonDirect(player, "BM\tTRADEEND\t" + why);
            Chat(player, "Pokémon trade: " + why);
        }
}

void BattlemonTrade::OnLogout(Player* player)
{
    if (auto s = Find(player->GetGUID()))
        Close(s, player->GetName() + " left.");
}

void BattlemonTrade::Expire()
{
    std::vector<std::shared_ptr<Session>> stale;
    {
        std::lock_guard<std::mutex> guard(_lock);
        uint32 const now = Now();
        for (auto const& entry : _sessions)
        {
            Session const& s = *entry.second;
            bool const gone = !ObjectAccessor::FindPlayer(s.side[0]) || !ObjectAccessor::FindPlayer(s.side[1]);
            if ((gone || now - s.touched > (s.accepted ? IDLE_SECONDS : INVITE_SECONDS))
                && std::find(stale.begin(), stale.end(), entry.second) == stale.end())
                stale.push_back(entry.second);
        }
    }
    for (auto const& s : stale)
        Close(s, "The trade timed out.");
}

void BattlemonTrade::Handle(Player* player, std::string const& arg)
{
    if (!player)
        return;
    if (!_enabled)
    {
        sBattlemonMgr->Msg(player, "Trading is turned off on this server.");
        return;
    }
    if (!sBattlemonMgr->ShouldHandle(player))
        return;

    size_t const tab = arg.find('\t');
    std::string const verb = arg.substr(0, tab);
    std::string const rest = tab == std::string::npos ? std::string() : arg.substr(tab + 1);
    std::shared_ptr<Session> s = Find(player->GetGUID());

    if (verb == "INVITE")
    {
        if (!sBattlemonMgr->CanBoxAction(player))
            return;
        if (s)
        {
            sBattlemonMgr->Msg(player, "You are already in a trade.");
            return;
        }
        Player* target = ObjectAccessor::FindPlayerByName(rest);
        if (!target || target == player || !sBattlemonMgr->ShouldHandle(target))
        {
            sBattlemonMgr->Msg(player, "No trainer called " + rest + " is online.");
            return;
        }
        if (Find(target->GetGUID()))
        {
            sBattlemonMgr->Msg(player, target->GetName() + " is busy.");
            return;
        }
        if (!InRange(player, target))
        {
            sBattlemonMgr->Msg(player, "Stand within " + std::to_string(static_cast<uint32>(_distance))
                                           + " yards of " + target->GetName() + " to trade.");
            return;
        }
        auto fresh = std::make_shared<Session>();
        fresh->side[0] = player->GetGUID();
        fresh->side[1] = target->GetGUID();
        fresh->touched = Now();
        {
            std::lock_guard<std::mutex> guard(_lock);
            _sessions[fresh->side[0]] = fresh;
            _sessions[fresh->side[1]] = fresh;
        }
        sBattlemonMgr->Msg(player, "Trade request sent to " + target->GetName() + ".");
        sBattlemonMgr->SendAddonDirect(target, "BM\tTRADEINVITE\t" + player->GetName());
        Chat(target, player->GetName() + " wants to trade Pokémon. Open the Battlemon addon (/bm trade) to answer.");
        return;
    }

    if (!s)
    {
        if (verb != "CANCEL" && verb != "DECLINE")
            sBattlemonMgr->Msg(player, "You are not in a trade.");
        return;
    }
    int const me = s->side[0] == player->GetGUID() ? 0 : 1;
    Player* other = ObjectAccessor::FindPlayer(s->side[1 - me]);

    if (verb == "DECLINE" || verb == "CANCEL")
    {
        Close(s, verb == "DECLINE" ? player->GetName() + " declined." : "Trade cancelled.");
        return;
    }
    if (!other)
    {
        Close(s, "The other trainer is gone.");
        return;
    }
    if (verb == "STATE")
    {
        if (s->accepted)
            Send(*s);
        return;
    }
    if (verb == "ACCEPT")
    {
        if (me != 1 || s->accepted || !sBattlemonMgr->CanBoxAction(player))
            return;
        if (!InRange(player, other))
        {
            sBattlemonMgr->Msg(player, "You are too far from " + other->GetName() + " to trade.");
            return;
        }
        {
            std::lock_guard<std::mutex> guard(_lock);
            s->accepted = true;
            s->touched = Now();
        }
        Send(*s);
        return;
    }
    if (!s->accepted)
        return;

    if (verb == "OFFER")
    {
        uint32 const ownedId = static_cast<uint32>(std::strtoul(rest.c_str(), nullptr, 10));
        if (ownedId)
        {
            // The database decides whose Pokemon this is, not the number the client sent.
            BattlemonOwned const row = sBattlemonMgr->LoadOwnedById(ownedId);
            if (!row.id || row.guid != player->GetGUID().GetCounter())
            {
                sBattlemonMgr->Msg(player, "That Pokemon is not yours to trade.");
                return;
            }
        }
        {
            std::lock_guard<std::mutex> guard(_lock);
            if (s->committing)
                return;
            s->offer[me] = ownedId;
            s->confirmed[0] = s->confirmed[1] = false; // any change voids both confirmations
            s->touched = Now();
        }
        Send(*s);
        return;
    }
    if (verb == "CONFIRM")
    {
        bool both = false;
        {
            std::lock_guard<std::mutex> guard(_lock);
            if ((!s->offer[0] && !s->offer[1]) || s->committing)
                return;
            s->confirmed[me] = true;
            s->touched = Now();
            both = s->confirmed[0] && s->confirmed[1];
            s->committing = both;
        }
        if (!both)
        {
            Send(*s);
            return;
        }
        Commit(s, ObjectAccessor::FindPlayer(s->side[0]), ObjectAccessor::FindPlayer(s->side[1]));
    }
}

void BattlemonTrade::Commit(std::shared_ptr<Session> const& s, Player* a, Player* b)
{
    auto reopen = [&](std::string const& why)
    {
        {
            std::lock_guard<std::mutex> guard(_lock);
            s->confirmed[0] = s->confirmed[1] = false;
            s->committing = false;
        }
        for (Player* p : { a, b })
            if (p)
                sBattlemonMgr->Msg(p, why);
        Send(*s);
    };

    if (!a || !b)
    {
        Close(s, "The other trainer is gone.");
        return;
    }
    // Everything is checked again now: a lot can change between agreeing and the last click.
    if (!sBattlemonMgr->CanBoxAction(a) || !sBattlemonMgr->CanBoxAction(b))
    {
        reopen("Both trainers must be out of battle to finish the trade.");
        return;
    }
    if (!InRange(a, b))
    {
        reopen("The trainers are too far apart.");
        return;
    }

    Player* const who[2] = { a, b };
    uint32 guid[2] = { a->GetGUID().GetCounter(), b->GetGUID().GetCounter() };
    uint32 id[2] = { s->offer[0], s->offer[1] };
    BattlemonOwned row[2];
    for (int i = 0; i < 2; ++i)
    {
        if (!id[i])
            continue;
        row[i] = sBattlemonMgr->LoadOwnedById(id[i]);
        if (!row[i].id || row[i].guid != guid[i])
        {
            Close(s, "A Pokémon in the trade is no longer available.");
            return;
        }
    }
    uint32 const owned[2] = { static_cast<uint32>(sBattlemonMgr->LoadOwned(guid[0]).size()),
                              static_cast<uint32>(sBattlemonMgr->LoadOwned(guid[1]).size()) };
    Rules::Check const check = Rules::Validate(owned[0], id[0] != 0, owned[1], id[1] != 0);
    if (check != Rules::Check::Ok)
    {
        reopen(check == Rules::Check::NothingOffered ? "Put a Pokémon up first."
                                                     : "A trainer cannot give away their last Pokémon.");
        return;
    }

    uint32 party[2][6];
    for (int i = 0; i < 2; ++i)
        for (uint8 slot = 1; slot <= 6; ++slot)
            party[i][slot - 1] = sBattlemonMgr->PartyOwnedId(guid[i], slot);

    // One statement changes both owners or neither: it only runs while every offered Pokemon still belongs to
    // the side offering it.
    std::string cases, conds, ids;
    uint32 expected = 0;
    for (int i = 0; i < 2; ++i)
    {
        if (!id[i])
            continue;
        cases += Acore::StringFormat(" WHEN {} THEN {}", id[i], guid[1 - i]);
        conds += Acore::StringFormat("{}(id = {} AND guid = {})", expected ? " OR " : "", id[i], guid[i]);
        ids += Acore::StringFormat("{}{}", expected ? "," : "", id[i]);
        ++expected;
    }
    CharacterDatabase.DirectExecute(
        "UPDATE battlemon_owned SET guid = CASE id{} END WHERE id IN ({}) AND "
        "(SELECT c FROM (SELECT COUNT(*) AS c FROM battlemon_owned WHERE {}) AS t) = {}",
        cases, ids, conds, expected);

    bool done = true;
    if (QueryResult result = CharacterDatabase.Query("SELECT id, guid FROM battlemon_owned WHERE id IN ({})", ids))
    {
        do
        {
            Field* f = result->Fetch();
            for (int i = 0; i < 2; ++i)
                if (id[i] && f[0].Get<uint32>() == id[i] && f[1].Get<uint32>() != guid[1 - i])
                    done = false;
        } while (result->NextRow());
    }
    else
        done = false;
    if (!done)
    {
        Close(s, "The trade could not be completed. Nothing changed.");
        return;
    }

    // The newcomer takes the traded Pokemon's party slot; a Pokemon from the box, or one received as a gift,
    // goes to the box.
    CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
    for (int i = 0; i < 2; ++i)
    {
        uint32 before[6];
        std::copy(party[i], party[i] + 6, before);
        Rules::NewParty(party[i], id[i], id[1 - i]);
        if (std::equal(before, before + 6, party[i]))
            continue;
        trans->Append("DELETE FROM battlemon_party WHERE guid = {}", guid[i]);
        for (uint8 slot = 0; slot < 6; ++slot)
            if (party[i][slot])
                trans->Append("INSERT INTO battlemon_party (guid, slot, owned_id) VALUES ({}, {}, {})", guid[i],
                              slot + 1, party[i][slot]);
    }
    trans->Append("INSERT INTO battlemon_trade_log (guid_a, owned_a, guid_b, owned_b) VALUES ({}, {}, {}, {})",
                  guid[0], id[0], guid[1], id[1]);
    CharacterDatabase.CommitTransaction(trans);

    for (int i = 0; i < 2; ++i)
    {
        if (id[i] && sBattlemonFollower->Chosen(who[i]) == id[i])
            sBattlemonFollower->Choose(who[i], 0); // it is no longer theirs to walk behind them
        if (id[1 - i])
            Chat(who[i], "You received " + FormName(row[1 - i]) + " from " + who[1 - i]->GetName() + "!");
        sBattlemonMgr->SyncCollection(who[i]);
    }
    Close(s, "Trade complete!");
}
