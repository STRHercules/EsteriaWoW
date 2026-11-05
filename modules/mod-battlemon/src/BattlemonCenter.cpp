#include "BattlemonBattles.h"
#include "BattlemonNpcTrainers.h"
#include "BattlemonBall.h"
#include "BattlemonCenter.h"
#include "BattlemonMgr.h"
#include "Creature.h"
#include "CreatureScript.h"
#include "Player.h"
#include "ScriptedGossip.h"
#include "StringFormat.h"

class npc_battlemon_center : public CreatureScript
{
public:
    npc_battlemon_center() : CreatureScript("npc_battlemon_center") { }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        if (!sBattlemonMgr->ShouldHandle(player))
            return false;
        ClearGossipMenuFor(player);
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Heal my Pokemon party.", GOSSIP_SENDER_MAIN,
            BattlemonCenter::Heal);
        AddGossipItemFor(player, GOSSIP_ICON_VENDOR, "Browse the Battlemon shop.", GOSSIP_SENDER_MAIN,
            BattlemonCenter::Shop);
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Manage my Pokemon and moves.", GOSSIP_SENDER_MAIN,
            BattlemonCenter::Party);
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Seal a stored Pokemon in a Poke Ball.", GOSSIP_SENDER_MAIN,
            BattlemonCenter::Storage);
        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
        return true;
    }

    // One page of the player's stored (non-party) Pokemon; picking one seals it.
    void ShowStorage(Player* player, Creature* creature, uint32 page)
    {
        ClearGossipMenuFor(player);
        std::vector<BattlemonOwned> const boxed = sBattlemonMgr->LoadBoxed(player->GetGUID().GetCounter());
        uint32 const first = page * BattlemonBall::PAGE_SIZE;
        if (boxed.empty() || first >= boxed.size())
        {
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "You have no stored Pokemon to seal.", GOSSIP_SENDER_MAIN,
                BattlemonCenter::Storage);
        }
        for (uint32 i = first; i < boxed.size() && i < first + BattlemonBall::PAGE_SIZE; ++i)
        {
            BattlemonOwned const& row = boxed[i];
            BattlemonForm const* form = sBattlemonMgr->GetBattlemonForm(row.formId);
            std::string const label = Acore::StringFormat("Lv.{} {}{}", row.level, row.shiny ? "Shiny " : "",
                form ? form->name : "Pokemon");
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, label, BattlemonBall::SENDER_SEAL, row.id,
                "Seal " + label + " in a Poke Ball?", 0, false);
        }
        if (first + BattlemonBall::PAGE_SIZE < boxed.size())
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Next page", BattlemonBall::SENDER_PAGE, page + 1);
        if (page > 0)
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Previous page", BattlemonBall::SENDER_PAGE, page - 1);
        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
    }

    bool OnGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 action) override
    {
        bool const storage = sender == BattlemonBall::SENDER_SEAL || sender == BattlemonBall::SENDER_PAGE
            || (sender == GOSSIP_SENDER_MAIN && action == BattlemonCenter::Storage);
        if (storage)
        {
            if (!sBattlemonMgr->ShouldHandle(player) || !creature->IsWithinDistInMap(player, INTERACTION_DISTANCE))
            {
                CloseGossipMenuFor(player);
                return false;
            }
            if (sender == BattlemonBall::SENDER_SEAL)
            {
                CloseGossipMenuFor(player);
                sBattlemonMgr->SealPokemon(player, action);
            }
            else
                ShowStorage(player, creature, sender == BattlemonBall::SENDER_PAGE ? action : 0);
            return true;
        }

        ClearGossipMenuFor(player);
        CloseGossipMenuFor(player);
        if (sender != GOSSIP_SENDER_MAIN || !creature->IsWithinDistInMap(player, INTERACTION_DISTANCE)
            || action < BattlemonCenter::Heal || action > BattlemonCenter::Party)
            return false;
        sBattlemonMgr->UseCenterService(player, action);
        return true;
    }
};

class npc_battlemon_trainer : public CreatureScript
{
public:
    npc_battlemon_trainer() : CreatureScript("npc_battlemon_trainer") { }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        if (!sBattlemonMgr->ShouldHandle(player) || !BattlemonNpcTrainers::Find(creature->GetEntry()))
            return false;
        ClearGossipMenuFor(player);
        AddGossipItemFor(player, GOSSIP_ICON_BATTLE, "Challenge this Pokemon Trainer.", GOSSIP_SENDER_MAIN, 1);
        AddGossipItemFor(player, GOSSIP_ICON_VENDOR, "Browse Pokemon supplies.", GOSSIP_SENDER_MAIN, 2);
        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 action) override
    {
        ClearGossipMenuFor(player);
        CloseGossipMenuFor(player);
        if (sender != GOSSIP_SENDER_MAIN || !creature->IsWithinDistInMap(player, INTERACTION_DISTANCE)
            || !BattlemonNpcTrainers::Find(creature->GetEntry()))
            return false;
        if (action == 1)
            BattlemonBattles::Instance().ChallengeTrainer(player, creature);
        else if (action == 2)
            sBattlemonMgr->UseCenterService(player, BattlemonCenter::Shop);
        return true;
    }
};

void AddSC_battlemon_center()
{
    new npc_battlemon_center();
    new npc_battlemon_trainer();
}
