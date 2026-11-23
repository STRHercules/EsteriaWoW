/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information.
 * Distributed under the GNU General Public License, version 2 or later.
 */

#include "WorldPvpEar.h"
#include "Bag.h"
#include "Chat.h"
#include "DatabaseEnv.h"
#include "GameTime.h"
#include "Item.h"
#include "Mail.h"
#include "Map.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "RBAC.h"
#include "StringFormat.h"
#include "WildernessPouch.h"
#include "World.h"
#include "WorldPvpPickpocket.h"
#include "WorldPvpRules.h"
#include "WorldSession.h"
#include <algorithm>
#include <ctime>
#include <memory>
#include <utility>
#include <vector>

namespace
{
using namespace Acore::WorldPvp;

bool CanTradeEars(Player const& player)
{
    return sWorld->getBoolConfig(CONFIG_ESTERIA_WORLD_PVP) &&
        sWorld->getBoolConfig(CONFIG_ESTERIA_WORLD_PVP_EAR_TROPHIES) && CanUseBountyEscrow() &&
        player.IsInWorld() && player.IsAlive() && !player.IsBeingTeleported() && !player.IsSpectator() &&
        !player.GetDigitalInventory().Failed() && player.GetMap()->IsWorldMap();
}

std::vector<std::pair<ObjectGuid, uint16>> FindSpendableEars(Player const& player, std::size_t limit,
    ObjectGuid selected = ObjectGuid::Empty)
{
    auto* query = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_UNSPENT_EARS);
    query->SetData(0, player.GetGUID().GetCounter());
    std::vector<std::pair<ObjectGuid, uint16>> ears;
    if (PreparedQueryResult result = CharacterDatabase.Query(query))
    {
        do
        {
            ObjectGuid const guid = ObjectGuid::Create<HighGuid::Item>(result->Fetch()[0].Get<uint32>());
            if (selected && guid != selected)
                continue;

            Item const* ear = player.GetItemByGuid(guid);
            if (ear && Player::IsInventoryPos(ear->GetPos()) && ear->GetEntry() == EarTrophyItem &&
                ear->GetOwnerGUID() == player.GetGUID() && ear->GetCount() == 1 && !ear->IsInTrade() &&
                !ear->m_lootGenerated)
                ears.emplace_back(guid, ear->GetPos());
        } while (ears.size() < limit && result->NextRow());
    }

    return ears;
}

void RemoveSettledEar(Player& player, uint16 pos)
{
    Item* ear = player.GetItemByPos(pos);
    player.MoveItemFromInventory(pos >> 8, pos & 255, true);
    delete ear;
}
}

void Acore::WorldPvp::AwardEarTrophy(Player& killer, Player const& victim)
{
    if (!sObjectMgr->GetItemTemplate(EarTrophyItem) || killer.GetDigitalInventory().Failed())
        return;

    ChatHandler handler(killer.GetSession());
    ItemPosCountVec dest;
    if (killer.CanStoreNewItem(NULL_BAG, NULL_SLOT, dest, EarTrophyItem, 1) != EQUIP_ERR_OK || dest.size() != 1)
    {
        handler.SendSysMessage("Your bags are full. Make room to collect Ear Trophies from future kills.");
        return;
    }

    std::unique_ptr<Item> ear(Item::CreateItem(EarTrophyItem, 1, &killer));
    if (!ear)
        return;

    time_t const killedAt = GameTime::GetGameTime().count();
    ear->SetBinding(true);
    ear->SetFlag(ITEM_FIELD_FLAGS, ITEM_FIELD_FLAG_READABLE);
    ear->SetText(Acore::StringFormat("Taken from {}.\nKilling blow by {}.\n{:%Y-%m-%d %H:%M:%S} UTC.",
        victim.GetName(), killer.GetName(), fmt::gmtime(killedAt)));
    uint32 const itemGuid = ear->GetGUID().GetCounter();
    uint32 const owner = killer.GetGUID().GetCounter();
    uint16 const pos = dest.front().pos;
    Bag const* bag = killer.GetBagByPos(pos >> 8);
    uint32 const bagGuid = bag ? bag->GetGUID().GetCounter() : 0;
    uint8 const slot = pos & 255;

    CharacterDatabaseTransaction transaction = CharacterDatabase.BeginTransaction();
    killer.SaveInventoryAndGoldToDB(transaction);
    auto* reserve = CharacterDatabase.GetPreparedStatement(CHAR_INS_WORLD_PVP_EAR_RECEIPT);
    reserve->SetData(0, itemGuid);
    reserve->SetData(1, victim.GetGUID().GetCounter());
    reserve->SetData(2, victim.GetSession()->GetAccountId());
    reserve->SetData(3, owner);
    reserve->SetData(4, killer.GetSession()->GetAccountId());
    transaction->Append(reserve);

    // Keep stock item serialization while discarding a provisional instance if the pairing is on cooldown.
    ear->SaveToDB(transaction);
    auto* discard = CharacterDatabase.GetPreparedStatement(CHAR_DEL_UNAWARDED_WORLD_PVP_EAR);
    discard->SetData(0, itemGuid);
    discard->SetData(1, EarTrophyItem);
    discard->SetData(2, owner);
    transaction->Append(discard);

    auto* store = CharacterDatabase.GetPreparedStatement(CHAR_INS_WORLD_PVP_EAR_INVENTORY);
    store->SetData(0, bagGuid);
    store->SetData(1, slot);
    store->SetData(2, itemGuid);
    store->SetData(3, owner);
    transaction->Append(store);

    bool const committed = CharacterDatabase.AsyncCommitTransaction(transaction).m_future.get();
    auto* check = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_EAR_RECEIPT);
    check->SetData(0, EarTrophyItem);
    check->SetData(1, bagGuid);
    check->SetData(2, slot);
    check->SetData(3, itemGuid);
    check->SetData(4, owner);
    PreparedQueryResult result = CharacterDatabase.Query(check);
    if (committed && result && result->Fetch()[0].Get<uint64>() == 0)
        return;

    if (!result || result->Fetch()[0].Get<uint64>() != 1 || killer.GetItemByPos(pos))
    {
        killer.GetDigitalInventory().DisconnectOnPersistenceFailure("Ear Trophy award could not be verified.");
        return;
    }

    Item* const awarded = ear.release();
    killer.MoveItemToInventory(dest, awarded, true, true);
    killer.SendNewItem(awarded, 1, true, false);
}

bool Acore::WorldPvp::CanBuyEarRewards(Player const& player)
{
    return CanTradeEars(player) && player.GetSession()->HasPermission(rbac::RBAC_PERM_COMMAND_DEV) &&
        IsCapital(sAreaTableStore.LookupEntry(player.GetAreaId()));
}

void Acore::WorldPvp::BuyEarReward(Player& buyer, uint32 entry)
{
    bool const fenceTool = entry == FencePickpocketTool.entry;
    bool const fencePowder = entry == FenceStunPowder.entry;
    if (!(fenceTool ? CanBuyFenceTool(buyer) : fencePowder ? CanUseEarFence(buyer) : CanBuyEarRewards(buyer)))
        return;

    auto const offer = std::find_if(EarRewards.begin(), EarRewards.end(),
        [entry](EarReward const& reward) { return reward.entry == entry; });
    ItemTemplate const* itemTemplate = sObjectMgr->GetItemTemplate(entry);
    if ((!fenceTool && !fencePowder && offer == EarRewards.end()) || !itemTemplate)
        return;

    ChatHandler handler(buyer.GetSession());
    bool const mount = itemTemplate->Class == ITEM_CLASS_MISC && itemTemplate->SubClass == ITEM_SUBCLASS_JUNK_MOUNT;
    if (mount && buyer.HasSpell(itemTemplate->Spells[1].SpellId))
    {
        handler.SendSysMessage("You already know this mount.");
        return;
    }
    if ((fenceTool || mount) && (buyer.HasItemCount(entry, 1, true) ||
        std::any_of(buyer.mMitems.begin(), buyer.mMitems.end(),
        [entry](auto const& attachment) { return attachment.second->GetEntry() == entry; })))
    {
        handler.SendSysMessage("You already have this reward.");
        return;
    }

    uint8 const price = fenceTool ? FencePickpocketTool.cost : fencePowder ? FenceStunPowder.cost : offer->cost;
    auto const cost = FindSpendableEars(buyer, price);
    if (cost.size() != price)
    {
        handler.PSendSysMessage("You need {} earned Ear Trophies in your bags.", uint32(price));
        return;
    }

    std::unique_ptr<Item> reward(Item::CreateItem(entry, 1, &buyer));
    if (!reward)
        return;

    reward->SetBinding(true);
    bool const direct = fenceTool || fencePowder;
    auto mail = direct ? nullptr : MakeWorldPvpItemMail(buyer, *reward, "Wilderness trophy reward");
    uint32 const mailId = mail ? mail->messageID : 0;
    uint32 const buyerGuid = buyer.GetGUID().GetCounter();
    // A Fence purchase can use the bag slot vacated by the first Ear Trophy it spends.
    uint16 const pos = direct ? cost.front().second : 0;
    Bag const* bag = direct ? buyer.GetBagByPos(pos >> 8) : nullptr;
    uint32 const bagGuid = bag ? bag->GetGUID().GetCounter() : 0;
    uint8 const slot = pos & 255;
    uint32 const rewardGuid = reward->GetGUID().GetCounter();
    CharacterDatabaseTransaction transaction = CharacterDatabase.BeginTransaction();
    buyer.SaveInventoryAndGoldToDB(transaction);

    auto* purchase = CharacterDatabase.GetPreparedStatement(CHAR_INS_WORLD_PVP_EAR_PURCHASE);
    purchase->SetData(0, rewardGuid);
    purchase->SetData(1, mailId);
    purchase->SetData(2, entry);
    purchase->SetData(3, price);
    purchase->SetData(4, buyerGuid);
    purchase->SetData(5, buyer.GetSession()->GetAccountId());
    transaction->Append(purchase);

    for (auto const& trophy : cost)
    {
        auto* reserve = CharacterDatabase.GetPreparedStatement(CHAR_RESERVE_WORLD_PVP_EAR_PURCHASE_COST);
        reserve->SetData(0, rewardGuid);
        reserve->SetData(1, trophy.first.GetCounter());
        reserve->SetData(2, EarTrophyItem);
        transaction->Append(reserve);
    }

    auto* fund = CharacterDatabase.GetPreparedStatement(CHAR_FUND_WORLD_PVP_EAR_PURCHASE);
    fund->SetData(0, rewardGuid);
    transaction->Append(fund);

    auto* release = CharacterDatabase.GetPreparedStatement(CHAR_RELEASE_WORLD_PVP_EAR_PURCHASE_COST);
    release->SetData(0, rewardGuid);
    transaction->Append(release);

    auto* consume = CharacterDatabase.GetPreparedStatement(CHAR_DELETE_WORLD_PVP_EAR_PURCHASE_COST);
    consume->SetData(0, rewardGuid);
    consume->SetData(1, EarTrophyItem);
    transaction->Append(consume);

    reward->SaveToDB(transaction);
    auto* discard = CharacterDatabase.GetPreparedStatement(CHAR_DEL_UNFUNDED_WORLD_PVP_EAR_REWARD);
    discard->SetData(0, rewardGuid);
    discard->SetData(1, entry);
    discard->SetData(2, buyerGuid);
    transaction->Append(discard);

    if (direct)
    {
        auto* store = CharacterDatabase.GetPreparedStatement(CHAR_INS_WORLD_PVP_EAR_REWARD_INVENTORY);
        store->SetData(0, bagGuid);
        store->SetData(1, slot);
        store->SetData(2, rewardGuid);
        transaction->Append(store);
    }
    else
    {
        auto* send = CharacterDatabase.GetPreparedStatement(CHAR_INS_WORLD_PVP_EAR_REWARD_MAIL);
        BindWorldPvpItemMail(*send, *mail);
        send->SetData(8, rewardGuid);
        send->SetData(9, mailId);
        transaction->Append(send);

        auto* attach = CharacterDatabase.GetPreparedStatement(CHAR_INS_WORLD_PVP_EAR_REWARD_MAIL_ITEM);
        attach->SetData(0, rewardGuid);
        attach->SetData(1, mailId);
        transaction->Append(attach);
    }

    bool const committed = CharacterDatabase.AsyncCommitTransaction(transaction).m_future.get();
    auto* check = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_EAR_PURCHASE);
    check->SetData(0, bagGuid);
    check->SetData(1, slot);
    check->SetData(2, rewardGuid);
    check->SetData(3, mailId);
    check->SetData(4, buyerGuid);
    PreparedQueryResult result = CharacterDatabase.Query(check);
    if (committed && result && result->Fetch()[0].Get<uint64>() == 0)
    {
        handler.SendSysMessage("The collector could not verify your Ear Trophies.");
        return;
    }

    // The inventory save has already cleared dirty flags, so an uncertain result requires a reload.
    if (!result || result->Fetch()[0].Get<uint64>() != 1 || !std::all_of(cost.begin(), cost.end(),
        [&buyer](auto const& trophy)
        {
            Item const* ear = buyer.GetItemByPos(trophy.second);
            return ear && ear->GetGUID() == trophy.first;
        }))
    {
        buyer.GetDigitalInventory().DisconnectOnPersistenceFailure("Ear reward purchase could not be verified.");
        return;
    }

    for (auto const& trophy : cost)
        RemoveSettledEar(buyer, trophy.second);

    if (direct)
    {
        Item* purchased = reward.release();
        buyer.MoveItemToInventory({{pos, 1}}, purchased, true, true);
        buyer.SendNewItem(purchased, 1, true, false);
    }
    else
    {
        PublishWorldPvpItemMail(buyer, std::move(mail), std::move(reward));
        handler.SendSysMessage("Your Wilderness reward is in your mailbox.");
    }
}

bool Acore::WorldPvp::CanUseEarFence(Player const& player)
{
    return CanTradeEars(player) && player.IsWorldPvpWanted();
}

bool Acore::WorldPvp::CanBuyFenceTool(Player const& player)
{
    return CanUseEarFence(player) && CanUsePlayerPickpocket(player);
}

void Acore::WorldPvp::SellEarToFence(Player& seller, ObjectGuid itemGuid)
{
    if (!CanUseEarFence(seller))
        return;

    ChatHandler handler(seller.GetSession());
    if (WalletRoom(seller) < FenceEarPrice)
    {
        handler.SendSysMessage("Make room in your wallet before selling an Ear Trophy.");
        return;
    }

    auto const ears = FindSpendableEars(seller, 1, itemGuid);
    if (ears.empty())
    {
        handler.SendSysMessage("You need an earned Ear Trophy in your bags.");
        return;
    }

    auto const [guid, pos] = ears.front();
    uint32 const sellerGuid = seller.GetGUID().GetCounter();
    uint32 const account = seller.GetSession()->GetAccountId();
    uint32 const balance = seller.GetMoney();
    uint32 const newBalance = balance + FenceEarPrice;
    CharacterDatabaseTransaction transaction = CharacterDatabase.BeginTransaction();
    seller.SaveInventoryAndGoldToDB(transaction);

    auto* sell = CharacterDatabase.GetPreparedStatement(CHAR_SELL_WORLD_PVP_EAR_TO_FENCE);
    sell->SetData(0, FenceEarPrice);
    sell->SetData(1, newBalance);
    sell->SetData(2, guid.GetCounter());
    sell->SetData(3, sellerGuid);
    sell->SetData(4, account);
    sell->SetData(5, balance);
    sell->SetData(6, EarTrophyItem);
    transaction->Append(sell);

    auto* consume = CharacterDatabase.GetPreparedStatement(CHAR_DEL_WORLD_PVP_FENCE_EAR);
    consume->SetData(0, guid.GetCounter());
    consume->SetData(1, sellerGuid);
    consume->SetData(2, FenceEarPrice);
    consume->SetData(3, EarTrophyItem);
    transaction->Append(consume);

    bool const committed = CharacterDatabase.AsyncCommitTransaction(transaction).m_future.get();
    auto* check = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_FENCE_SALE);
    check->SetData(0, FenceEarPrice);
    check->SetData(1, newBalance);
    check->SetData(2, guid.GetCounter());
    check->SetData(3, sellerGuid);
    check->SetData(4, account);
    PreparedQueryResult result = CharacterDatabase.Query(check);
    if (committed && result && result->Fetch()[0].Get<uint64>() == 0)
    {
        handler.SendSysMessage("The Fence could not verify your Ear Trophy.");
        return;
    }

    Item const* ear = seller.GetItemByPos(pos);
    if (!result || result->Fetch()[0].Get<uint64>() != 1 || !ear || ear->GetGUID() != guid)
    {
        seller.GetDigitalInventory().DisconnectOnPersistenceFailure("Fence sale could not be verified.");
        return;
    }

    RemoveSettledEar(seller, pos);
    seller.SetMoney(newBalance);
    handler.PSendSysMessage("The Fence paid you {} gold for an Ear Trophy.", FenceEarPrice / GOLD);
}
