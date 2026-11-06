#include "BattlemonHeldItems.h"
#include "BattlemonMgr.h"
#include "BattlemonSql.h"

#include "DatabaseEnv.h"
#include "Player.h"

// Giving an item takes one from the bag, and whatever the Pokemon held goes back into it, so nothing is created or
// lost. Nothing changes during a battle: the battle works on a copy and writes the held item back at the end.

bool BattlemonMgr::GiveHeldItem(Player* player, uint32 ownedId, std::string const& item)
{
    if (!CanBoxAction(player))
        return false;
    if (!BattlemonHeldItems::IsHoldable(item))
    {
        Msg(player, "A Pokémon cannot hold that.");
        return false;
    }
    uint32 const guid = SessionLowGuid(player);
    BattlemonOwned const row = LoadOwnedById(ownedId);
    // Ownership comes from the database row, never from the id the client sent.
    if (!row.id || row.guid != guid)
    {
        Msg(player, "That Pokémon is not yours.");
        return false;
    }
    if (row.heldItem == item)
    {
        Msg(player, "It is already holding that.");
        return false;
    }
    if (!BagTake(guid, item, 1))
    {
        Msg(player, "You have none of those left.");
        return false;
    }
    if (!row.heldItem.empty())
        BagAdd(guid, row.heldItem, 1);
    CharacterDatabase.DirectExecute("UPDATE battlemon_owned SET held_item = {} WHERE id = {} AND guid = {}",
                                    SqlQuote(item), ownedId, guid);
    BattlemonItemDef const* def = GetItem(item);
    BattlemonForm const* form = GetBattlemonForm(row.formId);
    Msg(player, (form ? form->name : std::string("Your Pokémon")) + " is now holding " + (def ? def->name : item) + ".");
    SendBag(player, guid);
    SendOwnedList(player, guid);
    return true;
}

bool BattlemonMgr::TakeHeldItem(Player* player, uint32 ownedId)
{
    if (!CanBoxAction(player))
        return false;
    uint32 const guid = SessionLowGuid(player);
    BattlemonOwned const row = LoadOwnedById(ownedId);
    if (!row.id || row.guid != guid)
    {
        Msg(player, "That Pokémon is not yours.");
        return false;
    }
    if (row.heldItem.empty())
    {
        Msg(player, "It is not holding anything.");
        return false;
    }
    BagAdd(guid, row.heldItem, 1);
    CharacterDatabase.DirectExecute("UPDATE battlemon_owned SET held_item = '' WHERE id = {} AND guid = {}", ownedId,
                                    guid);
    BattlemonItemDef const* def = GetItem(row.heldItem);
    Msg(player, "You took " + (def ? def->name : row.heldItem) + " back.");
    SendBag(player, guid);
    SendOwnedList(player, guid);
    return true;
}
