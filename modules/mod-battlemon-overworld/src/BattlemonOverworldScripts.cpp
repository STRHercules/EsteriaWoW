#include "BattlemonOverworld.h"
#include "BattlemonMgr.h"

#include "AllCreatureScript.h"
#include "Chat.h"
#include "ChatCommand.h"
#include "CommandScript.h"
#include "Creature.h"
#include "CreatureScript.h"
#include "DatabaseScript.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "ScriptedGossip.h"
#include "ScriptMgr.h"
#include "StringFormat.h"
#include "WorldScript.h"

using namespace Acore::ChatCommands;

class BattlemonOverworldWorldScript : public WorldScript
{
public:
    BattlemonOverworldWorldScript() : WorldScript("BattlemonOverworldWorldScript", {
        WORLDHOOK_ON_BEFORE_CONFIG_LOAD
    }) { }

    void OnBeforeConfigLoad(bool /*reload*/) override
    {
        sBattlemonOverworld->LoadConfig();
    }
};

class BattlemonOverworldDatabaseScript : public DatabaseScript
{
public:
    BattlemonOverworldDatabaseScript() : DatabaseScript("BattlemonOverworldDatabaseScript", {
        DATABASEHOOK_ON_AFTER_DATABASES_LOADED
    }) { }

    void OnAfterDatabasesLoaded(uint32 /*updateFlags*/) override
    {
        sBattlemonOverworld->LoadSpeciesMetrics();
    }
};

class BattlemonOverworldAllCreatureScript : public AllCreatureScript
{
public:
    BattlemonOverworldAllCreatureScript() : AllCreatureScript("BattlemonOverworldAllCreatureScript") { }

    void OnCreatureAddWorld(Creature* creature) override
    {
        sBattlemonOverworld->TryMorphCritter(creature);
    }

    void OnCreatureRemoveWorld(Creature* creature) override
    {
        sBattlemonOverworld->ForgetCreature(creature);
    }

    void OnAllCreatureUpdate(Creature* creature, uint32 diff) override
    {
        sBattlemonOverworld->TickCreature(creature, diff);
    }

    bool CanCreatureGossipHello(Player* player, Creature* creature) override
    {
        if (!sBattlemonOverworld->IsEnabled())
            return false;
        uint32 formId = 0;
        bool shiny = false;
        if (!BattlemonOverworld::ParseDisplay(creature->GetDisplayId(), formId, shiny))
            return false;

        CloseGossipMenuFor(player);
        sBattlemonOverworld->TryStartFromCreature(player, creature);
        return true;
    }
};

class npc_battlemon_overworld : public CreatureScript
{
public:
    npc_battlemon_overworld() : CreatureScript("npc_battlemon_overworld") { }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        CloseGossipMenuFor(player);
        sBattlemonOverworld->TryStartFromCreature(player, creature);
        return true;
    }
};

class BattlemonOverworldCommandScript : public CommandScript
{
public:
    BattlemonOverworldCommandScript() : CommandScript("BattlemonOverworldCommandScript") { }

    ChatCommandTable GetCommands() const override
    {
        static ChatCommandTable bmoTable =
        {
            { "spawn", HandleSpawn, SEC_GAMEMASTER, Console::No },
            { "status", HandleStatus, SEC_PLAYER, Console::No },
            { "inspect", HandleInspect, SEC_GAMEMASTER, Console::No },
            { "remorph", HandleRemorph, SEC_GAMEMASTER, Console::No },
        };
        static ChatCommandTable root = { { "bmo", bmoTable } };
        return root;
    }

    static bool HandleStatus(ChatHandler* handler)
    {
        float scale = 1.0f;
        float hover = 0.0f;
        sBattlemonOverworld->ComputeNudge(BattlemonOverworldIds::PikachuFormId, scale, hover);
        handler->SendSysMessage(Acore::StringFormat(
            "Battlemon overworld: {}  morph-critters {}  refresh {}-{}s  form-pool {}  entry {}  pikachu display {}  "
            "nudge-overrides {}  pikachu scale {:.2f} hover {:.2f}",
            sBattlemonOverworld->IsEnabled() ? "ON" : "OFF",
            sBattlemonOverworld->MorphCritters() ? "ON" : "OFF",
            sBattlemonOverworld->RefreshMinSeconds(),
            sBattlemonOverworld->RefreshMaxSeconds(),
            sBattlemonOverworld->FormPool(),
            BattlemonOverworldIds::CreatureEntry,
            BattlemonOverworld::DisplayId(BattlemonOverworldIds::PikachuFormId, false),
            sBattlemonOverworld->NudgeOverrideCount(),
            scale, hover));
        return true;
    }

    static bool HandleSpawn(ChatHandler* handler, Optional<uint32> formIdArg, Optional<uint32> shinyArg)
    {
        Player* player = handler->GetSession() ? handler->GetSession()->GetPlayer() : nullptr;
        if (!player)
        {
            handler->SendSysMessage("This command must be used in-game.");
            return true;
        }
        if (!sBattlemonOverworld->IsEnabled())
        {
            handler->SendSysMessage("Battlemon overworld is disabled.");
            return true;
        }

        uint32 formId = formIdArg.value_or(BattlemonOverworldIds::PikachuFormId);
        bool shiny = shinyArg.value_or(0) != 0;
        if (!sBattlemonMgr->GetForm(formId))
        {
            handler->SendSysMessage(Acore::StringFormat("Unknown Battlemon form {}.", formId));
            return true;
        }

        float x, y, z;
        player->GetNearPoint(player, x, y, z, 0.0f, 3.0f, player->GetOrientation());
        player->UpdateAllowedPositionZ(x, y, z);
        z += 0.05f;
        uint32 spawnEntry = BattlemonOverworldIds::FormEntry(formId);
        if (!spawnEntry || !sObjectMgr->GetCreatureTemplate(spawnEntry))
            spawnEntry = BattlemonOverworldIds::CreatureEntry;
        Creature* creature = player->SummonCreature(
            spawnEntry, x, y, z, player->GetOrientation(),
            TEMPSUMMON_TIMED_DESPAWN, 300000);
        if (!creature)
        {
            handler->SendSysMessage(Acore::StringFormat("Could not summon creature {}.", spawnEntry));
            return true;
        }
        sBattlemonOverworld->ApplyLook(creature, formId, shiny);
        BattlemonForm const* form = sBattlemonMgr->GetForm(formId);
        float scale = 1.0f;
        float hover = 0.0f;
        sBattlemonOverworld->ComputeNudge(formId, scale, hover);
        handler->SendSysMessage(Acore::StringFormat(
            "Spawned {} (form {}{}) display {} scale {:.2f} hover {:.2f}. Override: {}:{:.2f}:{:.2f}",
            form ? form->name : "?", formId, shiny ? ", shiny" : "",
            creature->GetDisplayId(), scale, hover, formId, scale, hover));
        return true;
    }

    static bool HandleInspect(ChatHandler* handler)
    {
        Creature* target = handler->getSelectedCreature();
        if (!target)
        {
            handler->SendSysMessage("Select a creature first.");
            return true;
        }

        uint32 formId = 0;
        bool shiny = false;
        bool battlemon = BattlemonOverworld::ParseDisplay(target->GetDisplayId(), formId, shiny);
        handler->SendSysMessage(Acore::StringFormat(
            "{} — entry {}  display {}  native {}  scale {:.2f}  battlemon {}  form {}{}",
            target->GetName(),
            target->GetEntry(),
            target->GetDisplayId(),
            target->GetNativeDisplayId(),
            target->GetObjectScale(),
            battlemon ? "yes" : "no",
            formId,
            shiny ? " (shiny)" : ""));
        return true;
    }

    static bool HandleRemorph(ChatHandler* handler)
    {
        if (!sBattlemonOverworld->IsEnabled())
        {
            handler->SendSysMessage("Battlemon overworld is disabled.");
            return true;
        }

        Creature* target = handler->getSelectedCreature();
        if (!target)
        {
            handler->SendSysMessage("Select a creature first.");
            return true;
        }

        uint32 beforeEntry = target->GetEntry();
        uint32 beforeDisplay = target->GetDisplayId();
        sBattlemonOverworld->RefreshLook(target);
        handler->SendSysMessage(Acore::StringFormat(
            "Refreshed {} — entry {} -> {}  display {} -> {}.",
            target->GetName(),
            beforeEntry,
            target->GetEntry(),
            beforeDisplay,
            target->GetDisplayId()));
        return true;
    }
};

void AddSC_battlemon_overworld()
{
    new BattlemonOverworldWorldScript();
    new BattlemonOverworldDatabaseScript();
    new BattlemonOverworldAllCreatureScript();
    new npc_battlemon_overworld();
    new BattlemonOverworldCommandScript();
}
