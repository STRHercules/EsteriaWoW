#include "BattlemonBattles.h"
#include "BattlemonNpcTrainers.h"
#include "BattlemonBall.h"
#include "BattlemonCenter.h"
#include "BattlemonMgr.h"
#include "Chat.h"
#include "Creature.h"
#include "CreatureScript.h"
#include "Player.h"
#include "ScriptedGossip.h"
#include "StringFormat.h"

#include <algorithm>
#include <cstdlib>
#include <vector>

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
        AddGossipItemFor(player, GOSSIP_ICON_VENDOR, "Buy supplies with Battlemon Points (menu).",
            GOSSIP_SENDER_MAIN, BattlemonCenter::Supplies);
        if (sBattlemonMgr->BreedingEnabled())
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Visit the Pokemon Day Care.", GOSSIP_SENDER_MAIN,
                BattlemonCenter::DayCare);
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

    static std::string PokemonLabel(BattlemonOwned const& row)
    {
        BattlemonForm const* form = sBattlemonMgr->GetBattlemonForm(row.formId);
        return Acore::StringFormat("Lv.{} {}{}", row.level, row.shiny ? "Shiny " : "", form ? form->name : "Pokemon");
    }

    // The Day Care: take back what is staying, leave something, or check on the pair and the eggs.
    void ShowDaycare(Player* player, Creature* creature)
    {
        ClearGossipMenuFor(player);
        std::vector<BattlemonOwned> const parents = sBattlemonMgr->DaycareParents(player);
        for (BattlemonOwned const& row : parents)
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Take back " + PokemonLabel(row),
                BattlemonCenter::SENDER_DAYCARE_TAKE, row.id);
        if (parents.size() < 2)
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Leave a Pokemon here.", BattlemonCenter::SENDER_DAYCARE_PUTLIST, 0);
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Check on my Pokemon and eggs.", BattlemonCenter::SENDER_DAYCARE_CHECK, 0);
        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
    }

    void ShowDaycarePutList(Player* player, Creature* creature, uint32 page)
    {
        ClearGossipMenuFor(player);
        std::vector<BattlemonOwned> const boxed = sBattlemonMgr->LoadBoxed(player->GetGUID().GetCounter());
        uint32 const first = page * BattlemonBall::PAGE_SIZE;
        if (boxed.empty() || first >= boxed.size())
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "You have no stored Pokemon to leave.", GOSSIP_SENDER_MAIN,
                BattlemonCenter::DayCare);
        for (uint32 i = first; i < boxed.size() && i < first + BattlemonBall::PAGE_SIZE; ++i)
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, PokemonLabel(boxed[i]), BattlemonCenter::SENDER_DAYCARE_PUT,
                boxed[i].id, "Leave " + PokemonLabel(boxed[i]) + " at the Day Care?", 0, false);
        if (first + BattlemonBall::PAGE_SIZE < boxed.size())
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Next page", BattlemonCenter::SENDER_DAYCARE_PUTLIST, page + 1);
        if (page > 0)
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Previous page", BattlemonCenter::SENDER_DAYCARE_PUTLIST, page - 1);
        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
    }

    static char const* PocketName(uint32 pocket)
    {
        switch (pocket)
        {
            case 3: return "Poke Balls";
            case 2: return "Medicine";
            case 5: return "Berries";
            case 7: return "Battle items";
            case 1: return "Held items";
            default: return nullptr;
        }
    }

    // The pockets that actually have something for sale, in shop order.
    void ShowShopCategories(Player* player, Creature* creature)
    {
        ClearGossipMenuFor(player);
        std::vector<uint32> seen;
        for (BattlemonShopEntry const& e : sBattlemonMgr->ShopEntries())
        {
            BattlemonItemDef const* def = sBattlemonMgr->GetItem(e.itemInternal);
            if (!def || !PocketName(def->pocket) || std::find(seen.begin(), seen.end(), def->pocket) != seen.end())
                continue;
            seen.push_back(def->pocket);
            AddGossipItemFor(player, GOSSIP_ICON_VENDOR, PocketName(def->pocket), BattlemonCenter::SENDER_SHOP_CATEGORY,
                def->pocket);
        }
        if (seen.empty())
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Nothing is for sale right now.", GOSSIP_SENDER_MAIN,
                BattlemonCenter::Supplies);
        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
    }

    void ShowShopPage(Player* player, Creature* creature, uint32 pocket, uint32 page)
    {
        constexpr uint32 perPage = 8;
        ClearGossipMenuFor(player);
        std::vector<BattlemonShopEntry> const& shop = sBattlemonMgr->ShopEntries();
        std::vector<uint32> indexes; // positions in the shop list, which is what the buy action carries
        for (uint32 i = 0; i < shop.size(); ++i)
        {
            BattlemonItemDef const* def = sBattlemonMgr->GetItem(shop[i].itemInternal);
            if (def && def->pocket == pocket)
                indexes.push_back(i);
        }
        uint32 const first = page * perPage;
        for (uint32 n = first; n < indexes.size() && n < first + perPage; ++n)
        {
            BattlemonShopEntry const& e = shop[indexes[n]];
            std::string const label = Acore::StringFormat("{} - {} points",
                sBattlemonMgr->GetItem(e.itemInternal)->name, e.cost);
            AddGossipItemFor(player, GOSSIP_ICON_VENDOR, label, BattlemonCenter::SENDER_SHOP_ITEM, indexes[n],
                "How many?", 0, true);
        }
        if (first + perPage < indexes.size())
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Next page", BattlemonCenter::SENDER_SHOP_PAGE,
                pocket * 1000 + page + 1);
        if (page > 0)
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Previous page", BattlemonCenter::SENDER_SHOP_PAGE,
                pocket * 1000 + page - 1);
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Back", BattlemonCenter::SENDER_SHOP_CATEGORY, 0);
        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
    }

    bool OnGossipSelectCode(Player* player, Creature* creature, uint32 sender, uint32 action, char const* code) override
    {
        CloseGossipMenuFor(player);
        if (sender != BattlemonCenter::SENDER_SHOP_ITEM || !code || !sBattlemonMgr->ShouldHandle(player)
            || !creature->IsWithinDistInMap(player, INTERACTION_DISTANCE) || !sBattlemonMgr->CanBoxAction(player))
            return false;
        std::vector<BattlemonShopEntry> const& shop = sBattlemonMgr->ShopEntries();
        if (action >= shop.size())
            return false;
        // The player typed this: anything that is not a plain number buys one.
        char* end = nullptr;
        unsigned long const qty = std::strtoul(code, &end, 10);
        std::string message;
        sBattlemonMgr->TryBuy(player, shop[action].itemInternal, end == code ? 1 : static_cast<uint32>(
            std::min<unsigned long>(qty, 99)), message);
        if (!message.empty())
            ChatHandler(player->GetSession()).SendSysMessage(message);
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 action) override
    {
        bool const dayCare = sender == BattlemonCenter::SENDER_DAYCARE_PUTLIST || sender == BattlemonCenter::SENDER_DAYCARE_PUT
            || sender == BattlemonCenter::SENDER_DAYCARE_TAKE || sender == BattlemonCenter::SENDER_DAYCARE_CHECK
            || (sender == GOSSIP_SENDER_MAIN && action == BattlemonCenter::DayCare);
        if (dayCare)
        {
            if (!sBattlemonMgr->ShouldHandle(player) || !creature->IsWithinDistInMap(player, INTERACTION_DISTANCE))
            {
                CloseGossipMenuFor(player);
                return false;
            }
            if (sender == BattlemonCenter::SENDER_DAYCARE_PUTLIST)
            {
                ShowDaycarePutList(player, creature, action);
                return true;
            }
            if (sender == BattlemonCenter::SENDER_DAYCARE_PUT)
                sBattlemonMgr->DaycareDeposit(player, action);
            else if (sender == BattlemonCenter::SENDER_DAYCARE_TAKE)
                sBattlemonMgr->DaycareTake(player, action);
            else if (sender == BattlemonCenter::SENDER_DAYCARE_CHECK)
            {
                sBattlemonMgr->DaycareCheck(player);
                sBattlemonMgr->DaycareHatch(player);
            }
            ShowDaycare(player, creature);
            return true;
        }

        bool const shopMenu = sender == BattlemonCenter::SENDER_SHOP_CATEGORY
            || sender == BattlemonCenter::SENDER_SHOP_PAGE
            || (sender == GOSSIP_SENDER_MAIN && action == BattlemonCenter::Supplies);
        if (shopMenu)
        {
            if (!sBattlemonMgr->ShouldHandle(player) || !creature->IsWithinDistInMap(player, INTERACTION_DISTANCE))
            {
                CloseGossipMenuFor(player);
                return false;
            }
            if (sender == BattlemonCenter::SENDER_SHOP_PAGE)
                ShowShopPage(player, creature, action / 1000, action % 1000);
            else if (sender == BattlemonCenter::SENDER_SHOP_CATEGORY && action)
                ShowShopPage(player, creature, action, 0);
            else
                ShowShopCategories(player, creature);
            return true;
        }

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
