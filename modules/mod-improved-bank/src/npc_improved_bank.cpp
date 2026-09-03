/*
 * Credits: silviu20092
 */

#include "ScriptMgr.h"
#include "ScriptedGossip.h"
#include "Player.h"
#include "Chat.h"
#include "improved_bank.h"

class npc_improved_bank : public CreatureScript
{
public:
    npc_improved_bank() : CreatureScript("npc_improved_bank")
    {
    }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        AddGossipItemFor(player, GOSSIP_ICON_VENDOR, "Deposit...", GOSSIP_SENDER_MAIN, GOSSIP_ACTION_INFO_DEF + 1);
        if (sImprovedBank->GetShowDepositReagents())
            AddGossipItemFor(player, GOSSIP_ICON_VENDOR, "Deposit all reagents...", GOSSIP_SENDER_MAIN, GOSSIP_ACTION_INFO_DEF + 4);
        AddGossipItemFor(player, GOSSIP_ICON_MONEY_BAG, "Withdraw...", GOSSIP_SENDER_MAIN, GOSSIP_ACTION_INFO_DEF + 2);
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Nevermind", GOSSIP_SENDER_MAIN, GOSSIP_ACTION_INFO_DEF + 3);
        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 action) override
    {
        ImprovedBank::PagedData& pagedData = sImprovedBank->GetPagedData(player);
        if (sender == GOSSIP_SENDER_MAIN)
        {
            if (action == GOSSIP_ACTION_INFO_DEF)
            {
                ClearGossipMenuFor(player);
                return OnGossipHello(player, creature);
            }
            else if (action == GOSSIP_ACTION_INFO_DEF + 1)
            {
                sImprovedBank->BuildDepositItemCatalogue(player);
                return sImprovedBank->AddPagedData(player, creature, 0);
            }
            else if (action == GOSSIP_ACTION_INFO_DEF + 2)
            {
                sImprovedBank->BuildWithdrawItemCatalogue(player);
                return sImprovedBank->AddPagedData(player, creature, 0);
            }
            else if (action == GOSSIP_ACTION_INFO_DEF + 3)
            {
                CloseGossipMenuFor(player);
                return true;
            }
            else if (action == GOSSIP_ACTION_INFO_DEF + 4)
            {
                uint32 count = 0;
                sImprovedBank->DepositAllReagents(player, &count);
                if (count == 0)
                    ChatHandler(player->GetSession()).SendSysMessage("No reagents found to deposit.");
                else
                    ChatHandler(player->GetSession()).PSendSysMessage("Deposited a total of {} reagents.", count);
                CloseGossipMenuFor(player);
                return true;
            }
        }
        else if (sender == GOSSIP_SENDER_MAIN + 1)
        {
            uint32 id = action - GOSSIP_ACTION_INFO_DEF;
            return sImprovedBank->TakePagedDataAction(player, creature, id);
        }
        else if (sender == GOSSIP_SENDER_MAIN + 2)
        {
            uint32 page = action - GOSSIP_ACTION_INFO_DEF;
            return sImprovedBank->AddPagedData(player, creature, page);
        }
        else if (sender == GOSSIP_SENDER_MAIN + 20)
        {
            sImprovedBank->BuildDepositItemCatalogue(player);
            return sImprovedBank->AddPagedData(player, creature, 0);
        }
        else if (sender == GOSSIP_SENDER_MAIN + 21)
        {
            sImprovedBank->BuildItemSubClassesCatalogue(player, pagedData, ImprovedBank::PAGED_DATA_TYPE_DEPOSIT_SUBCLASS, pagedData.itemClass);
            return sImprovedBank->AddPagedData(player, creature, 0);
        }
        else if (sender == GOSSIP_SENDER_MAIN + 22)
        {
            sImprovedBank->BuildWithdrawItemCatalogue(player);
            return sImprovedBank->AddPagedData(player, creature, 0);
        }
        else if (sender == GOSSIP_SENDER_MAIN + 23)
        {
            sImprovedBank->BuildItemSubClassesCatalogue(player, pagedData, ImprovedBank::PAGED_DATA_TYPE_WITHDRAW_SUBCLASS, pagedData.itemClass);
            return sImprovedBank->AddPagedData(player, creature, 0);
        }

        CloseGossipMenuFor(player);
        return false;
    }
};

void AddSC_npc_improved_bank()
{
    new npc_improved_bank();
}
