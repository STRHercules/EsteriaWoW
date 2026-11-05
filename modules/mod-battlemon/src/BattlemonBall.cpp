#include "BattlemonBall.h"
#include "BattlemonFollower.h"
#include "BattlemonMgr.h"

#include "Chat.h"
#include "DatabaseEnv.h"
#include "Item.h"
#include "ItemScript.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "ScriptMgr.h"

#include <algorithm>
#include <unordered_set>

namespace
{
void Tell(Player* player, char const* text)
{
    ChatHandler(player->GetSession()).SendSysMessage(text);
}
}

// Same refusals as the Center: nothing happens mid-battle, mid-duel or mid-combat.
bool BattlemonMgr::CanBoxAction(Player* player)
{
    if (!player || !ShouldHandle(player) || player->IsInCombat() || HasRemoteSession(player)
        || IsExternallyReserved(player->GetGUID()) || HasActiveEncounter(player))
    {
        if (player)
            Tell(player, "Finish your battle first.");
        return false;
    }
    return true;
}

std::vector<BattlemonOwned> BattlemonMgr::LoadBoxed(uint32 guid) const
{
    std::unordered_set<uint32> inParty;
    for (uint8 slot = 1; slot <= 6; ++slot)
        inParty.insert(PartyOwnedId(guid, slot));
    std::vector<BattlemonOwned> rows = LoadOwned(guid);
    rows.erase(std::remove_if(rows.begin(), rows.end(),
        [&](BattlemonOwned const& r) { return inParty.count(r.id) != 0; }), rows.end());
    return rows;
}

bool BattlemonMgr::SealPokemon(Player* player, uint32 ownedId)
{
    if (!CanBoxAction(player))
        return false;

    uint32 const guid = SessionLowGuid(player);
    BattlemonOwned const row = LoadOwnedById(ownedId);
    // Ownership comes from the database row, never from the client's idea of who owns what.
    if (!row.id || row.guid != guid)
    {
        Tell(player, "That Pokemon is not yours.");
        return false;
    }
    for (uint8 slot = 1; slot <= 6; ++slot)
    {
        if (PartyOwnedId(guid, slot) == ownedId)
        {
            Tell(player, "Take it out of your party first.");
            return false;
        }
    }

    uint32 const entry = BattlemonBall::ItemEntry(row.speciesId, row.shiny);
    if (!sObjectMgr->GetItemTemplate(entry))
    {
        Tell(player, "Poke Ball items for this Pokemon are not installed on this server.");
        return false;
    }
    ItemPosCountVec dest;
    if (player->CanStoreNewItem(NULL_BAG, NULL_SLOT, dest, entry, 1) != EQUIP_ERR_OK)
    {
        Tell(player, "Your bags are full.");
        return false;
    }
    Item* item = player->StoreNewItem(dest, entry, true);
    if (!item)
        return false;
    if (sBattlemonFollower->Chosen(player) == ownedId)
        sBattlemonFollower->Choose(player, 0);

    // The item and the Pokemon move in one transaction: a crash can never leave a Pokemon
    // that belongs to nobody, or a ball with nothing in it.
    CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
    player->SaveInventoryAndGoldToDB(trans);
    trans->Append("UPDATE battlemon_owned SET guid = 0 WHERE id = {} AND guid = {}", ownedId, guid);
    trans->Append("REPLACE INTO battlemon_ball_item (item_guid, owned_id) VALUES ({}, {})",
        item->GetGUID().GetCounter(), ownedId);
    CharacterDatabase.CommitTransaction(trans);

    SendOwnedList(player, guid);
    ChatHandler(player->GetSession()).PSendSysMessage("You sealed {} in a Poke Ball.",
        GetBattlemonForm(row.formId) ? GetBattlemonForm(row.formId)->name : "your Pokemon");
    return true;
}

bool BattlemonMgr::UnsealPokemon(Player* player, Item* item)
{
    if (!CanBoxAction(player))
        return false;

    uint32 const itemGuid = item->GetGUID().GetCounter();
    QueryResult result = CharacterDatabase.Query(
        "SELECT owned_id FROM battlemon_ball_item WHERE item_guid = {}", itemGuid);
    if (!result)
    {
        Tell(player, "This Poke Ball is empty.");
        return false;
    }
    uint32 const ownedId = result->Fetch()[0].Get<uint32>();
    BattlemonOwned const row = LoadOwnedById(ownedId);
    // guid 0 is the only state a sealed Pokemon may be in; anything else means this ball is stale.
    if (!row.id || row.guid != 0)
    {
        Tell(player, "This Poke Ball is empty.");
        return false;
    }

    uint32 const guid = SessionLowGuid(player);
    EnsureAccount(guid);

    CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
    trans->Append("UPDATE battlemon_owned SET guid = {} WHERE id = {} AND guid = 0", guid, ownedId);
    trans->Append("DELETE FROM battlemon_ball_item WHERE item_guid = {}", itemGuid);
    std::string const name = GetBattlemonForm(row.formId) ? GetBattlemonForm(row.formId)->name : "A Pokemon";
    player->DestroyItem(item->GetBagSlot(), item->GetSlot(), true); // item is gone after this line
    player->SaveInventoryAndGoldToDB(trans);
    CharacterDatabase.CommitTransaction(trans);

    SendOwnedList(player, guid);
    ChatHandler(player->GetSession()).PSendSysMessage("{} was released into your collection.", name);
    return true;
}

// Right-click on a ball. Always claims the use so the placeholder spell on the template never casts.
class item_battlemon_ball : public ItemScript
{
public:
    item_battlemon_ball() : ItemScript("item_battlemon_ball") { }

    bool OnUse(Player* player, Item* item, SpellCastTargets const& /*targets*/) override
    {
        if (!sBattlemonMgr->UnsealPokemon(player, item))
            player->SendEquipError(EQUIP_ERR_CANT_DO_RIGHT_NOW, item, nullptr);
        return true;
    }
};

void AddSC_battlemon_ball()
{
    new item_battlemon_ball();
}
