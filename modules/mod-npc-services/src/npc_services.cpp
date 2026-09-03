/*
**  Written by MtgCore
**  Rewritten by Poszer & Talamortis https://github.com/poszer/ & https://github.com/talamortis/
**  AzerothCore +2019 http://www.azerothcore.org/
**  Cleaned and made into a module by Micrah https://github.com/milestorme/
*/

#include "npc_services.h"
#include "Chat.h"

bool NpcServices::OnGossipHello(Player* player, Creature* creature)
{
    // Repair Items
    AddGossipItemFor(player, 10, "|TInterface\\icons\\INV_Hammer_24:40:40:-18|t Repair Items", GOSSIP_SENDER_MAIN, 6);
    // Open Bank
    AddGossipItemFor(player, 10, "|TInterface/Icons/INV_Misc_Bag_07:40:40:-18|t Bank", GOSSIP_SENDER_MAIN, 8);
    // Open Mailbox
    AddGossipItemFor(player, 10, "|TInterface/Icons/INV_Letter_11:40:40:-18|t Mail", GOSSIP_SENDER_MAIN, 9);

    SendGossipMenuFor(player, 1, creature->GetGUID());
    return true;
}

bool NpcServices::OnGossipSelect(Player* player, Creature* /*creature*/, uint32 /*sender*/, uint32 action)
{
    player->PlayerTalkClass->ClearMenus();

    switch (action)
    {
        case 6: // Repair Items
            CloseGossipMenuFor(player);
            player->DurabilityRepairAll(false, 0, false);
            ChatHandler(player->GetSession()).SendNotification("|cffFFFF00NPC SERVICES \n |cffFFFFFFItems repaired succesfully!");
            player->CastSpell(player, 31726);
            break;

        case 8: // BANK
            CloseGossipMenuFor(player);
            player->GetSession()->SendShowBank(player->GetGUID());
            break;

        case 9: // MAIL
            CloseGossipMenuFor(player);
            player->GetSession()->SendShowMailBox(player->GetGUID());
            break;

        default:
            return false;

    }
    return true;
}
