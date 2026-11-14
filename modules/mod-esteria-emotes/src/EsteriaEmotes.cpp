/*
 * Esteria emote collection. Emotes are looping animations appended to the retail character skeletons
 * (animation ids from 3000) with matching client Emotes.dbc rows. The emote state is a public unit field,
 * so nearby players see it; MovementHandler clears it when the player moves.
 *
 * Known emotes and the wheel layout (4 pages x 8 slots) are account-wide (characters DB, see
 * data/sql/db-characters/esteria_emotes.sql). The EsteriaEmotes addon talks over addon whispers to self:
 *   ESTEMO\tsync                 -> reset, known\t<id,...> (chunked), wheel\t<32 ids>, done
 *   ESTEMO\tplay\t<id>           -> playing\t<id> | err\t<reason>
 *   ESTEMO\tstop
 *   ESTEMO\tslot\t<0-31>\t<id|0> -> slot\t<n>\t<id> | err\t<reason>
 */

#include "Chat.h"
#include "CommandScript.h"
#include "DatabaseEnv.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "StringConvert.h"
#include "Tokenize.h"
#include "WorldPacket.h"
#include "WorldSession.h"

#include <algorithm>
#include <array>
#include <ctime>
#include <mutex>
#include <set>
#include <unordered_map>

using namespace Acore::ChatCommands;

namespace
{
    constexpr char PREFIX[] = "ESTEMO\t";
    constexpr size_t WHEEL_SLOTS = 32;
    constexpr size_t CHUNK = 180; // keeps each reply inside the client's 255 byte addon message

    // The client dereferences its Emotes.dbc row without a null check, so only ids it ships may be sent.
    // shortcut: hardcoded shipped set, move to a world table when emotes stop arriving with client packs.
    constexpr std::array<uint32, 15> SHIPPED_EMOTES =
    {
        3000, 3001, 3002, 3003, 3004, 3005, 3006, 3007,
        3008, 3009, 3010, 3011, 3012, 3013, 3014
    };

    bool IsShipped(uint32 emoteId)
    {
        return std::find(SHIPPED_EMOTES.begin(), SHIPPED_EMOTES.end(), emoteId) != SHIPPED_EMOTES.end();
    }

    struct Collection
    {
        std::set<uint32> known;
        std::array<uint32, WHEEL_SLOTS> wheel{};
    };

    std::mutex lock;
    std::unordered_map<uint32, Collection> collections; // account id -> collection, loaded at login

    void Load(uint32 account)
    {
        Collection collection;
        if (QueryResult result = CharacterDatabase.Query("SELECT emote FROM esteria_emote_known WHERE account = {}", account))
            do
                collection.known.insert((*result)[0].Get<uint32>());
            while (result->NextRow());
        if (QueryResult result = CharacterDatabase.Query("SELECT slot, emote FROM esteria_emote_wheel WHERE account = {}", account))
            do
            {
                uint8 slot = (*result)[0].Get<uint8>();
                if (slot < WHEEL_SLOTS)
                    collection.wheel[slot] = (*result)[1].Get<uint32>();
            }
            while (result->NextRow());
        std::lock_guard<std::mutex> guard(lock);
        collections[account] = std::move(collection);
    }

    void Send(Player* player, std::string const& body)
    {
        WorldPacket data;
        ChatHandler::BuildChatPacket(data, CHAT_MSG_WHISPER, LANG_ADDON, player, player, PREFIX + body);
        player->GetSession()->SendPacket(&data);
    }

    void SendCollection(Player* player)
    {
        Collection copy;
        {
            std::lock_guard<std::mutex> guard(lock);
            copy = collections[player->GetSession()->GetAccountId()];
        }
        Send(player, "reset");
        std::string line;
        for (uint32 emote : copy.known)
        {
            if (!IsShipped(emote))
                continue;
            if (line.size() > CHUNK)
            {
                Send(player, "known\t" + line);
                line.clear();
            }
            line += (line.empty() ? "" : ",") + std::to_string(emote);
        }
        if (!line.empty())
            Send(player, "known\t" + line);
        std::string wheel;
        for (size_t i = 0; i < WHEEL_SLOTS; ++i)
            wheel += (i ? "," : "") + std::to_string(copy.wheel[i]);
        Send(player, "wheel\t" + wheel);
        Send(player, "done");
    }

    bool Knows(Player* player, uint32 emote)
    {
        if (player->GetSession()->GetSecurity() >= SEC_GAMEMASTER)
            return true; // GMs test every shipped emote without collecting it
        std::lock_guard<std::mutex> guard(lock);
        auto found = collections.find(player->GetSession()->GetAccountId());
        return found != collections.end() && found->second.known.count(emote);
    }

    void Play(Player* player, uint32 emote)
    {
        if (!IsShipped(emote) || !Knows(player, emote))
            return Send(player, "err\tYou have not collected that emote.");
        if (!player->IsAlive())
            return Send(player, "err\tYou can't dance while dead.");
        player->SetUInt32Value(UNIT_NPC_EMOTESTATE, emote);
        Send(player, "playing\t" + std::to_string(emote));
    }

    void SetSlot(Player* player, uint32 slot, uint32 emote)
    {
        if (slot >= WHEEL_SLOTS || (emote && (!IsShipped(emote) || !Knows(player, emote))))
            return Send(player, "err\tThat emote can't go on your wheel.");
        uint32 account = player->GetSession()->GetAccountId();
        {
            std::lock_guard<std::mutex> guard(lock);
            collections[account].wheel[slot] = emote;
        }
        if (emote)
            CharacterDatabase.Execute("REPLACE INTO esteria_emote_wheel (account, slot, emote) VALUES ({}, {}, {})", account, slot, emote);
        else
            CharacterDatabase.Execute("DELETE FROM esteria_emote_wheel WHERE account = {} AND slot = {}", account, slot);
        Send(player, "slot\t" + std::to_string(slot) + "\t" + std::to_string(emote));
    }

    void HandleRequest(Player* player, std::string_view body)
    {
        std::vector<std::string_view> args = Acore::Tokenize(body, '\t', true);
        if (args.empty())
            return;
        auto number = [&](size_t i) { return i < args.size() ? Acore::StringTo<uint32>(args[i]).value_or(0) : 0; };
        if (args[0] == "sync")
            SendCollection(player);
        else if (args[0] == "play")
            Play(player, number(1));
        else if (args[0] == "stop")
            player->SetUInt32Value(UNIT_NPC_EMOTESTATE, EMOTE_ONESHOT_NONE);
        else if (args[0] == "slot" && args.size() >= 3)
            SetSlot(player, number(1), number(2));
    }

    // Learn or forget for an account; returns how many rows changed. The player is told when online.
    uint32 Change(Player* target, std::string_view which, bool learn)
    {
        std::vector<uint32> emotes;
        if (which == "all")
            emotes.assign(SHIPPED_EMOTES.begin(), SHIPPED_EMOTES.end());
        else if (Optional<uint32> id = Acore::StringTo<uint32>(which); id && IsShipped(*id))
            emotes.push_back(*id);
        uint32 account = target->GetSession()->GetAccountId(), changed = 0;
        {
            std::lock_guard<std::mutex> guard(lock);
            Collection& collection = collections[account];
            for (uint32 emote : emotes)
                if (learn ? collection.known.insert(emote).second : collection.known.erase(emote) > 0)
                    ++changed;
            if (!learn)
                for (uint32& slot : collection.wheel)
                    if (std::find(emotes.begin(), emotes.end(), slot) != emotes.end())
                        slot = 0;
        }
        for (uint32 emote : emotes)
        {
            if (learn)
                CharacterDatabase.Execute("INSERT IGNORE INTO esteria_emote_known (account, emote, learned) VALUES ({}, {}, {})",
                    account, emote, uint32(std::time(nullptr)));
            else
            {
                CharacterDatabase.Execute("DELETE FROM esteria_emote_known WHERE account = {} AND emote = {}", account, emote);
                CharacterDatabase.Execute("DELETE FROM esteria_emote_wheel WHERE account = {} AND emote = {}", account, emote);
            }
        }
        if (changed)
            SendCollection(target);
        return changed;
    }
}

class esteria_emotes_playerscript : public PlayerScript
{
public:
    esteria_emotes_playerscript() : PlayerScript("esteria_emotes_playerscript", { PLAYERHOOK_ON_LOGIN, PLAYERHOOK_CAN_PLAYER_USE_PRIVATE_CHAT }) { }

    void OnPlayerLogin(Player* player) override
    {
        Load(player->GetSession()->GetAccountId());
    }

    bool OnPlayerCanUseChat(Player* player, uint32 type, uint32 language, std::string& msg, Player* receiver) override
    {
        if (language != LANG_ADDON || type != CHAT_MSG_WHISPER || receiver != player)
            return true;
        std::string_view view = msg;
        if (view.substr(0, sizeof(PREFIX) - 1) != PREFIX)
            return true;
        HandleRequest(player, view.substr(sizeof(PREFIX) - 1));
        return false;
    }
};

class esteria_emotes_commandscript : public CommandScript
{
public:
    esteria_emotes_commandscript() : CommandScript("esteria_emotes_commandscript") { }

    ChatCommandTable GetCommands() const override
    {
        static ChatCommandTable emoteTable =
        {
            { "play",    HandlePlay,    SEC_GAMEMASTER, Console::No },
            { "stop",    HandleStop,    SEC_GAMEMASTER, Console::No },
            { "learn",   HandleLearn,   SEC_GAMEMASTER, Console::No },
            { "unlearn", HandleUnlearn, SEC_GAMEMASTER, Console::No },
        };
        static ChatCommandTable root =
        {
            { "emote", emoteTable },
        };
        return root;
    }

    static bool HandlePlay(ChatHandler* handler, uint32 emoteId)
    {
        if (!IsShipped(emoteId))
        {
            handler->PSendSysMessage("Emote {} is not in the shipped emote set.", emoteId);
            return false;
        }

        Player* player = handler->GetSession()->GetPlayer();
        player->SetUInt32Value(UNIT_NPC_EMOTESTATE, emoteId);
        handler->PSendSysMessage("Playing emote {}. Move to stop.", emoteId);
        return true;
    }

    static bool HandleStop(ChatHandler* handler)
    {
        handler->GetSession()->GetPlayer()->SetUInt32Value(UNIT_NPC_EMOTESTATE, EMOTE_ONESHOT_NONE);
        return true;
    }

    // .emote learn <id|all>: on the selected player (or yourself); account-wide.
    static bool HandleLearn(ChatHandler* handler, std::string which)
    {
        Player* target = handler->getSelectedPlayerOrSelf();
        uint32 changed = Change(target, which, true);
        handler->PSendSysMessage("{} emote(s) learned for {}'s account.", changed, target->GetName());
        return true;
    }

    static bool HandleUnlearn(ChatHandler* handler, std::string which)
    {
        Player* target = handler->getSelectedPlayerOrSelf();
        uint32 changed = Change(target, which, false);
        handler->PSendSysMessage("{} emote(s) removed from {}'s account.", changed, target->GetName());
        return true;
    }
};

void AddSC_esteria_emotes()
{
    new esteria_emotes_playerscript();
    new esteria_emotes_commandscript();
}
