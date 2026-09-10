#include "BattlemonMgr.h"
#include "BattlemonSidecarServer.h"

#include "Chat.h"
#include "ChatCommand.h"
#include "Group.h"
#include "Player.h"
#include "PlayerScript.h"
#include "ScriptMgr.h"
#include "StringFormat.h"
#include "WorldSession.h"

using namespace Acore::ChatCommands;

namespace
{
    bool IsBattlemonAddon(uint32 lang, std::string const& msg)
    {
        return lang == LANG_ADDON && msg.size() >= 3 && msg.compare(0, 3, "BM\t") == 0;
    }
}

class BattlemonWorldScript : public WorldScript
{
public:
    BattlemonWorldScript() : WorldScript("BattlemonWorldScript", {
        WORLDHOOK_ON_BEFORE_CONFIG_LOAD,
        WORLDHOOK_ON_STARTUP
    }) { }

    void OnBeforeConfigLoad(bool /*reload*/) override
    {
        sBattlemonMgr->LoadConfig();
    }

    void OnStartup() override
    {
        sBattlemonMgr->LoadCatalog();
    }
};

class BattlemonPlayerScript : public PlayerScript
{
public:
    BattlemonPlayerScript() : PlayerScript("BattlemonPlayerScript", {
        PLAYERHOOK_ON_LOGIN,
        PLAYERHOOK_ON_LOGOUT,
        PLAYERHOOK_ON_BEFORE_SEND_CHAT_MESSAGE,
        PLAYERHOOK_CAN_PLAYER_USE_PRIVATE_CHAT,
        PLAYERHOOK_CAN_PLAYER_USE_GROUP_CHAT
    }) { }

    void OnPlayerLogin(Player* player) override
    {
        if (!sBattlemonMgr->ShouldHandle(player))
            return;

        BattlemonAccount const acc = sBattlemonMgr->EnsureAccount(player);
        if (!sBattlemonMgr->Announce())
            return;

        uint32 leadId = sBattlemonMgr->PartyOwnedId(acc.guid, 1);
        BattlemonOwned lead = sBattlemonMgr->LoadOwnedById(leadId);
        BattlemonForm const* form = sBattlemonMgr->GetForm(lead.formId);
        uint32 wait = sBattlemonMgr->SecondsUntilReady(acc);
        std::string ready = wait == 0 ? "Fight is ready" : Acore::StringFormat("Fight in {}s", wait);
        ChatHandler(player->GetSession()).SendSysMessage(Acore::StringFormat(
            "|cff00ff00Battlemon:|r {} Lv.{} — {}. Open the Battlemon addon (/bm).",
            form ? form->name : "???", lead.level ? lead.level : 1, ready));
    }

    void OnPlayerLogout(Player* player) override
    {
        if (player)
            sBattlemonMgr->ClearEncounter(player->GetGUID());
    }

    void OnPlayerBeforeSendChatMessage(Player* player, uint32& /*type*/, uint32& lang, std::string& msg) override
    {
        if (!IsBattlemonAddon(lang, msg))
            return;
        sBattlemonMgr->HandleAddon(player, msg);
    }

    bool OnPlayerCanUseChat(Player* /*player*/, uint32 /*type*/, uint32 lang, std::string& msg, Player* /*receiver*/) override
    {
        return !IsBattlemonAddon(lang, msg);
    }

    bool OnPlayerCanUseChat(Player* /*player*/, uint32 /*type*/, uint32 lang, std::string& msg, Group* /*group*/) override
    {
        return !IsBattlemonAddon(lang, msg);
    }
};

class BattlemonCommandScript : public CommandScript
{
public:
    BattlemonCommandScript() : CommandScript("BattlemonCommandScript") { }

    ChatCommandTable GetCommands() const override
    {
        static ChatCommandTable battlemonTable =
        {
            { "status", HandleStatus, SEC_PLAYER, Console::No },
            { "reset",  HandleReset,  SEC_PLAYER, Console::No },
            { "wild",   HandleWild,   SEC_PLAYER, Console::No },
            { "link",   HandleLink,   SEC_PLAYER, Console::No },
            { "revoke", HandleRevoke, SEC_PLAYER, Console::No },
            { "reload", HandleReload, SEC_ADMINISTRATOR, Console::Yes },
        };
        static ChatCommandTable root = { { "battlemon", battlemonTable } };
        return root;
    }

    static bool HandleStatus(ChatHandler* handler)
    {
        Player* player = handler->GetSession() ? handler->GetSession()->GetPlayer() : nullptr;
        if (!player)
        {
            handler->SendSysMessage("This command must be used in-game.");
            return true;
        }
        if (!sBattlemonMgr->IsEnabled())
        {
            handler->SendSysMessage("Battlemon is disabled.");
            return true;
        }

        BattlemonAccount const acc = sBattlemonMgr->EnsureAccount(player);
        uint32 leadId = sBattlemonMgr->PartyOwnedId(acc.guid, 1);
        BattlemonOwned lead = sBattlemonMgr->LoadOwnedById(leadId);
        BattlemonForm const* form = sBattlemonMgr->GetForm(lead.formId);
        uint32 wait = sBattlemonMgr->SecondsUntilReady(acc);
        handler->SendSysMessage(Acore::StringFormat(
            "Battlemon: lead {} Lv.{}  party {}/6  balls {}  points {}  fight {}",
            form ? form->name : "none", lead.level, sBattlemonMgr->PartyCount(acc.guid),
            sBattlemonMgr->BagCount(acc.guid, "POKEBALL"), acc.points,
            wait == 0 ? "READY" : Acore::StringFormat("in {}s", wait)));
        return true;
    }

    static bool HandleReset(ChatHandler* handler)
    {
        Player* player = handler->GetSession() ? handler->GetSession()->GetPlayer() : nullptr;
        if (!player)
        {
            handler->SendSysMessage("This command must be used in-game.");
            return true;
        }
        if (!sBattlemonMgr->IsEnabled())
        {
            handler->SendSysMessage("Battlemon is disabled.");
            return true;
        }

        sBattlemonMgr->ResetPlayer(player);
        handler->SendSysMessage("Battlemon reset to the level 1 starter.");
        return true;
    }

    static bool HandleWild(ChatHandler* handler)
    {
        Player* player = handler->GetSession() ? handler->GetSession()->GetPlayer() : nullptr;
        if (!player)
        {
            handler->SendSysMessage("This command must be used in-game.");
            return true;
        }
        if (!sBattlemonMgr->ShouldHandle(player))
        {
            handler->SendSysMessage("Battlemon is disabled.");
            return true;
        }

        sBattlemonMgr->StartWild(player);
        return true;
    }

    static bool HandleLink(ChatHandler* handler)
    {
        Player* player = handler->GetSession() ? handler->GetSession()->GetPlayer() : nullptr;
        if (!player)
        {
            handler->SendSysMessage("This command must be used in-game.");
            return true;
        }
        if (!sBattlemonSidecar->IsEnabled())
        {
            handler->SendSysMessage("Battlemon sidecar is disabled on this realm.");
            return true;
        }
        std::string code = sBattlemonSidecar->CreatePairCode(player->GetGUID().GetCounter());
        if (code.empty())
        {
            handler->SendSysMessage("Could not create a pair code.");
            return true;
        }
        handler->SendSysMessage(Acore::StringFormat(
            "|cff00ff00Battlemon:|r Pocketmon pair code |cffFFFF00{}|r (valid five minutes).",
            code));
        return true;
    }

    static bool HandleRevoke(ChatHandler* handler)
    {
        Player* player = handler->GetSession() ? handler->GetSession()->GetPlayer() : nullptr;
        if (!player)
        {
            handler->SendSysMessage("This command must be used in-game.");
            return true;
        }
        sBattlemonSidecar->RevokeTokensForGuid(player->GetGUID().GetCounter());
        sBattlemonSidecar->RevokeLease(player->GetGUID().GetCounter());
        handler->SendSysMessage("Battlemon Pocketmon tokens revoked for this character.");
        return true;
    }

    static bool HandleReload(ChatHandler* handler)
    {
        sBattlemonMgr->LoadConfig();
        sBattlemonMgr->LoadCatalog();
        handler->SendSysMessage("Battlemon config and world catalog reloaded.");
        return true;
    }
};

void AddSC_battlemon()
{
    new BattlemonWorldScript();
    new BattlemonPlayerScript();
    new BattlemonCommandScript();
}
