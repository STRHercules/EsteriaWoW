/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information.
 * Distributed under the GNU General Public License, version 2 or later.
 */

#include "WildernessPouch.h"
#include "Bag.h"
#include "CellImpl.h"
#include "Chat.h"
#include "Common.h"
#include "CryptoRandom.h"
#include "DatabaseEnv.h"
#include "GameObject.h"
#include "GameTime.h"
#include "Item.h"
#include "Mail.h"
#include "MailMgr.h"
#include "Map.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "RBAC.h"
#include "Random.h"
#include "ScriptMgr.h"
#include "World.h"
#include "WorldPvpRules.h"
#include "WorldSession.h"
#include <G3D/Quat.h>
#include <limits>
#include <list>
#include <memory>
#include <optional>
#include <utility>
#include <vector>

namespace
{
constexpr float PouchReach = 5.0f;
constexpr uint32 PouchEntry = 701950;

bool IsWildernessSupply(ItemTemplate const& proto)
{
    switch (proto.Class)
    {
        case ITEM_CLASS_CONSUMABLE:
        case ITEM_CLASS_GEM:
        case ITEM_CLASS_REAGENT:
        case ITEM_CLASS_PROJECTILE:
        case ITEM_CLASS_TRADE_GOODS:
        case ITEM_CLASS_GLYPH:
            return true;
        default:
            return false;
    }
}

Item* SelectWildernessPouchItem(Player const& player, bool allowGear, bool allowSupplies, uint32 maxCount)
{
    std::vector<Item*> candidates;
    auto const add = [&](Item* item)
    {
        if (!item || item->GetState() == ITEM_REMOVED || item->IsInTrade() || item->m_lootGenerated ||
            item->IsWrapped() || item->IsBoundAccountWide() || item->IsRefundable() ||
            item->IsBOPTradable() || item->IsBoundByTempEnchant() || item->GetEnchantmentId(TEMP_ENCHANTMENT_SLOT) ||
            item->GetUInt32Value(ITEM_FIELD_DURATION) || item->GetGUID() == player.GetLootGUID())
            return;

        ItemTemplate const* proto = item->GetTemplate();
        bool const gear = proto->Class == ITEM_CLASS_WEAPON || proto->Class == ITEM_CLASS_ARMOR;
        uint32 const count = item->GetCount();
        bool const eligibleGear = gear && allowGear && count == 1 && item->GetMaxStackCount() == 1;
        bool const eligibleSupply = allowSupplies && IsWildernessSupply(*proto) && proto->Bonding == NO_BIND &&
            !item->IsSoulBound() && !item->IsBoundByEnchant();
        if (!eligibleGear && !eligibleSupply)
            return;

        if (!count || count > maxCount || count > item->GetMaxStackCount() ||
            proto->Quality >= ITEM_QUALITY_LEGENDARY || proto->Bonding >= BIND_QUEST_ITEM ||
            proto->Duration || proto->StartQuest ||
            proto->HasFlag(ITEM_FLAG_HAS_LOOT) || proto->HasFlag(ITEM_FLAG_CONJURED) ||
            proto->HasFlag(ITEM_FLAG_NO_USER_DESTROY) || proto->HasFlag(ITEM_FLAG_HAS_QUEST_GLOW) ||
            Acore::WorldPvp::WildernessItemAuctionValue(proto->SellPrice, count) > MAX_MONEY_AMOUNT ||
            player.CanUnequipItem(item->GetPos(), false) != EQUIP_ERR_OK ||
            !sScriptMgr->OnPlayerCanDropWildernessGear(&player, item))
            return;

        candidates.push_back(item);
    };

    if (allowGear)
        for (uint8 slot = EQUIPMENT_SLOT_START; slot < EQUIPMENT_SLOT_END; ++slot)
            add(player.GetItemByPos(INVENTORY_SLOT_BAG_0, slot));
    for (uint8 slot = INVENTORY_SLOT_ITEM_START; slot < INVENTORY_SLOT_ITEM_END; ++slot)
        add(player.GetItemByPos(INVENTORY_SLOT_BAG_0, slot));
    for (uint8 slot = INVENTORY_SLOT_BAG_START; slot < INVENTORY_SLOT_BAG_END; ++slot)
        if (Bag const* bag = player.GetBagByPos(slot))
            for (uint8 inside = 0; inside < bag->GetBagSize(); ++inside)
                add(bag->GetItemByPos(inside));

    return candidates.empty() ? nullptr : candidates[urand(0, uint32(candidates.size() - 1))];
}

void SpawnPouch(Map& map, uint64 id, uint32 phase, float x, float y, float z, int32 lifetime)
{
    if (!id || lifetime <= 0 || !Acore::IsValidMapCoord(x, y, z) || !sObjectMgr->GetGameObjectTemplate(PouchEntry))
        return;

    std::unique_ptr<GameObject> pouch = std::make_unique<GameObject>();
    if (!pouch->Create(map.GenerateLowGuid<HighGuid::GameObject>(), PouchEntry, &map, phase,
        x, y, z, 0.0f, G3D::Quat(0, 0, 0, 1), 100, GO_STATE_READY))
        return;

    pouch->SetWildernessPouchId(id);
    // The stock summoned-gameobject lifecycle uses a spell marker to delete expired goobers.
    pouch->SetSpellId(1);
    pouch->SetRespawnTime(lifetime);
    pouch->SetSpawnedByDefault(false);
    if (map.AddToMap(pouch.get(), false))
        pouch.release();
}

void RemovePouch(Player const& player, uint64 id)
{
    std::list<GameObject*> nearby;
    player.GetGameObjectListWithEntryInGrid(nearby, PouchEntry, PouchReach);
    for (GameObject* pouch : nearby)
        if (pouch->GetWildernessPouchId() == id)
            pouch->Delete();
}

uint64 NewPouchNonce()
{
    uint64 nonce;
    Acore::Crypto::GetRandomBytes(reinterpret_cast<uint8*>(&nonce), sizeof(nonce));
    return nonce;
}

PreparedQueryResult VerifyPouchWrite(Player& player, CharacterDatabaseTransaction const& transaction,
    CharacterDatabasePreparedStatement* receipt)
{
    // Use the same database worker as character saves and read back the unique receipt before changing the wallet.
    CharacterDatabase.AsyncCommitTransaction(transaction).m_future.get();
    PreparedQueryResult result = CharacterDatabase.Query(receipt);
    if (!result)
        player.GetDigitalInventory().DisconnectOnPersistenceFailure(
            "Wilderness pouch outcome unavailable; reconnect to recover your saved balance");

    return result;
}

std::optional<bool> ReadPouchClaim(Player& player, CharacterDatabaseTransaction const& transaction,
    uint64 id, uint64 nonce)
{
    auto* receipt = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WILDERNESS_POUCH_CLAIM);
    receipt->SetData(0, id);
    receipt->SetData(1, player.GetGUID().GetCounter());
    receipt->SetData(2, nonce);
    if (PreparedQueryResult result = VerifyPouchWrite(player, transaction, receipt))
    {
        uint64 const status = result->Fetch()[0].Get<uint64>();
        if (status <= 1)
            return status == 1;

        player.GetDigitalInventory().DisconnectOnPersistenceFailure(
            "Wilderness item delivery could not be verified; reconnect to refresh your inventory");
    }

    return std::nullopt;
}

struct PendingItemDelivery
{
    std::unique_ptr<Item> item;
    std::unique_ptr<Mail> mail;

    bool Stage(ChatHandler& handler, CharacterDatabaseTransaction const& transaction,
        uint64 id, uint64 nonce, uint32 itemGuid, uint32 entry)
    {
        if (!itemGuid)
            return true;

        auto* load = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WILDERNESS_GEAR);
        load->SetData(0, itemGuid);
        load->SetData(1, entry);
        load->SetData(2, 0u);
        PreparedQueryResult result = CharacterDatabase.Query(load);
        item = std::make_unique<Item>();
        if (!result || !item->LoadFromDB(itemGuid, ObjectGuid::Empty, result->Fetch(), entry))
        {
            handler.SendErrorMessage("This pouch's item is unavailable.");
            return false;
        }

        Player const& player = *handler.GetSession()->GetPlayer();
        mail = Acore::WorldPvp::MakeWorldPvpItemMail(player, *item, "Recovered Wilderness items");

        auto* send = CharacterDatabase.GetPreparedStatement(CHAR_INS_WILDERNESS_GEAR_MAIL);
        Acore::WorldPvp::BindWorldPvpItemMail(*send, *mail);
        send->SetData(8, id);
        send->SetData(9, mail->receiver);
        send->SetData(10, nonce);
        transaction->Append(send);

        auto* attach = CharacterDatabase.GetPreparedStatement(CHAR_INS_WILDERNESS_GEAR_MAIL_ITEM);
        attach->SetData(0, mail->messageID);
        attach->SetData(1, id);
        attach->SetData(2, mail->receiver);
        attach->SetData(3, nonce);
        transaction->Append(attach);

        auto* transfer = CharacterDatabase.GetPreparedStatement(CHAR_TRANSFER_WILDERNESS_GEAR);
        transfer->SetData(0, id);
        transfer->SetData(1, mail->receiver);
        transfer->SetData(2, nonce);
        transaction->Append(transfer);
        return true;
    }

    void Publish(Player& player)
    {
        if (mail)
            Acore::WorldPvp::PublishWorldPvpItemMail(player, std::move(mail), std::move(item));
    }
};

PreparedQueryResult FindNearbyPouches(Player const& player, uint64 id)
{
    auto* query = CharacterDatabase.GetPreparedStatement(CHAR_SEL_NEARBY_WILDERNESS_POUCHES);
    query->SetData(0, player.GetMapId());
    query->SetData(1, player.GetPositionX() - PouchReach);
    query->SetData(2, player.GetPositionX() + PouchReach);
    query->SetData(3, player.GetPositionY() - PouchReach);
    query->SetData(4, player.GetPositionY() + PouchReach);
    query->SetData(5, player.GetPositionZ() - PouchReach);
    query->SetData(6, player.GetPositionZ() + PouchReach);
    query->SetData(7, player.GetGUID().GetCounter());
    query->SetData(8, player.GetSession()->GetAccountId());
    query->SetData(9, uint8(player.IsAlive()));
    query->SetData(10, id);
    query->SetData(11, id);
    return CharacterDatabase.Query(query);
}
}

Item* Acore::WorldPvp::SelectWildernessSupplyToSteal(Player const& player)
{
    return SelectWildernessPouchItem(player, false, true, 5);
}

std::unique_ptr<Mail> Acore::WorldPvp::MakeWorldPvpItemMail(Player const& receiver, Item const& item,
    char const* subject)
{
    auto mail = std::make_unique<Mail>();
    mail->messageID = sObjectMgr->GenerateMailID();
    mail->messageType = MAIL_CREATURE;
    mail->stationery = MAIL_STATIONERY_DEFAULT;
    mail->sender = BountyCollectorEntry;
    mail->receiver = receiver.GetGUID().GetCounter();
    mail->subject = subject;
    mail->deliver_time = GameTime::GetGameTime().count();
    mail->expire_time = mail->deliver_time + 30 * DAY;
    mail->checked = MAIL_CHECK_MASK_COPIED;
    mail->state = MAIL_STATE_UNCHANGED;
    mail->AddItem(item.GetGUID().GetCounter(), item.GetEntry());
    return mail;
}

void Acore::WorldPvp::BindWorldPvpItemMail(CharacterDatabasePreparedStatement& statement, Mail const& mail)
{
    statement.SetData(0, mail.messageID);
    statement.SetData(1, mail.messageType);
    statement.SetData(2, mail.stationery);
    statement.SetData(3, mail.sender);
    statement.SetData(4, mail.subject);
    statement.SetData(5, uint32(mail.expire_time));
    statement.SetData(6, uint32(mail.deliver_time));
    statement.SetData(7, uint8(mail.checked));
}

void Acore::WorldPvp::PublishWorldPvpItemMail(Player& receiver, std::unique_ptr<Mail> mail,
    std::unique_ptr<Item> item)
{
    item->SetOwnerGUID(receiver.GetGUID());
    receiver.AddMItem(item.release());
    sMailMgr->OnMailSent(mail->receiver);
    receiver.AddNewMailDeliverTime(mail->deliver_time);
    receiver.AddMail(mail.release());
}

void Acore::WorldPvp::LoadWildernessPouches(Map& map, uint32 gridX, uint32 gridY)
{
    if (map.GetId() != MAP_NORTHREND || !sWorld->getBoolConfig(CONFIG_ESTERIA_WILDERNESS_GOLD_POUCHES) ||
        !CanUseBountyEscrow() || !sObjectMgr->GetGameObjectTemplate(PouchEntry))
        return;

    float const upperX = (float(CENTER_GRID_ID) - float(gridX)) * SIZE_OF_GRIDS;
    float const upperY = (float(CENTER_GRID_ID) - float(gridY)) * SIZE_OF_GRIDS;
    auto* query = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WILDERNESS_POUCHES_IN_GRID);
    query->SetData(0, map.GetId());
    // Pad the SQL bounds for float rounding. The same cell check used by AddToMap decides ownership.
    query->SetData(1, upperX - SIZE_OF_GRIDS - 1.0f);
    query->SetData(2, upperX + 1.0f);
    query->SetData(3, upperY - SIZE_OF_GRIDS - 1.0f);
    query->SetData(4, upperY + 1.0f);
    // shortcut: load receipts with the preview grid, prefetch before public rollout
    PreparedQueryResult rows = CharacterDatabase.Query(query);
    if (!rows)
        return;

    do
    {
        Field* row = rows->Fetch();
        float const x = row[2].Get<float>();
        float const y = row[3].Get<float>();
        float const z = row[4].Get<float>();
        if (!Acore::IsValidMapCoord(x, y, z))
            continue;

        Cell const cell(x, y);
        if (cell.GridX() == gridX && cell.GridY() == gridY)
            SpawnPouch(map, row[0].Get<uint64>(), row[1].Get<uint32>(), x, y, z, int32(row[5].Get<int64>()));
    } while (rows->NextRow());
}

void Player::ApplyWildernessDeathPenalty()
{
    bool const freebornKillingBlow = std::exchange(_wildernessFreebornKillingBlow, false);
    if (!sWorld->getBoolConfig(CONFIG_ESTERIA_WILDERNESS_GOLD_POUCHES) || !Acore::WorldPvp::CanUseBountyEscrow() ||
        !IsInWorld() || !IsInActiveWilderness() || IsBeingTeleported() ||
        IsFlying() || IsInFlight() || GetTransport() || duel ||
        GetDigitalInventory().Failed())
        return;

    bool const allowGear = sWorld->getBoolConfig(CONFIG_ESTERIA_WILDERNESS_GEAR_POUCHES);
    bool const allowSupplies = sWorld->getBoolConfig(CONFIG_ESTERIA_WILDERNESS_INVENTORY_POUCHES);
    if ((allowGear || allowSupplies) && !GetTradeData() && roll_chance_i(10))
        if (Item* item = SelectWildernessPouchItem(*this, allowGear, allowSupplies, std::numeric_limits<uint32>::max()))
            DropWildernessItem(*item);

    if (GetDigitalInventory().Failed())
        return;

    uint32 const copper = Acore::WorldPvp::WildernessPouchCopper(GetMoney(), freebornKillingBlow);
    uint32 const xp = GetUInt32Value(PLAYER_XP);
    uint32 const xpLoss = sWorld->getBoolConfig(CONFIG_ESTERIA_WILDERNESS_DEATH_XP_LOSS) && !IsMaxLevel() ?
        Acore::WorldPvp::WildernessDeathXpLoss(xp) : 0;
    if (!copper && !xpLoss)
        return;

    uint64 const id = NewPouchNonce();
    if (!id)
        return;

    uint32 const guid = GetGUID().GetCounter();
    uint32 const account = GetSession()->GetAccountId();
    uint32 const remaining = GetMoney() - copper;
    Map& map = *GetMap();
    uint32 const phase = GetPhaseMask();
    float const x = GetPositionX();
    float const y = GetPositionY();
    float const z = GetPositionZ();
    CharacterDatabaseTransaction transaction = CharacterDatabase.BeginTransaction();
    // Save the current level with XP so a recent level-up cannot leave reduced XP on the previous level.
    if (xpLoss)
        _SaveCharacter(false, transaction);

    auto* create = CharacterDatabase.GetPreparedStatement(CHAR_INS_WILDERNESS_POUCH);
    create->SetData(0, id);
    create->SetData(1, map.GetId());
    create->SetData(2, phase);
    create->SetData(3, x);
    create->SetData(4, y);
    create->SetData(5, z);
    create->SetData(6, copper);
    create->SetData(7, xpLoss);
    create->SetData(8, guid);
    create->SetData(9, account);
    transaction->Append(create);

    auto* fund = CharacterDatabase.GetPreparedStatement(CHAR_FUND_WILDERNESS_POUCH);
    fund->SetData(0, remaining);
    fund->SetData(1, xp - xpLoss);
    fund->SetData(2, id);
    transaction->Append(fund);

    auto* receipt = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WILDERNESS_POUCH_FUNDING);
    receipt->SetData(0, id);
    receipt->SetData(1, guid);
    receipt->SetData(2, account);
    PreparedQueryResult funding = VerifyPouchWrite(*this, transaction, receipt);
    if (!funding || funding->Fetch()[0].Get<uint64>() != 1)
        return;

    ChatHandler handler(GetSession());
    if (xpLoss)
    {
        SetUInt32Value(PLAYER_XP, xp - xpLoss);
        handler.PSendSysMessage("You lost {} XP on death in the Wilderness.", xpLoss);
    }

    if (!copper)
        return;

    SetMoney(remaining);
    Cell const cell(x, y);
    if (map.IsGridLoaded(GridCoord(cell.GridX(), cell.GridY())))
        SpawnPouch(map, id, phase, x, y, z, int32(funding->Fetch()[1].Get<int64>()));

    handler.PSendSysMessage(
        "You dropped {} copper in pouch {}. Only you can loot for two minutes. Auction opens after 15 minutes.",
        copper, id);
}

void Player::DropWildernessItem(Item& item)
{
    uint64 const id = NewPouchNonce();
    if (!id)
        return;

    uint32 const guid = GetGUID().GetCounter();
    uint32 const account = GetSession()->GetAccountId();
    uint8 const bag = item.GetBagSlot();
    uint8 const slot = item.GetSlot();
    ItemTemplate const* proto = item.GetTemplate();
    uint32 const count = item.GetCount();
    uint32 const value = uint32(Acore::WorldPvp::WildernessItemAuctionValue(proto->SellPrice, count));
    bool const ownerOnly = item.IsSoulBound() || item.IsBoundByEnchant() || proto->Bonding == BIND_WHEN_PICKED_UP;
    Map& map = *GetMap();
    uint32 const phase = GetPhaseMask();
    float const x = GetPositionX();
    float const y = GetPositionY();
    float const z = GetPositionZ();

    CharacterDatabaseTransaction transaction = CharacterDatabase.BeginTransaction();
    // Flush the selected instance and its current slot before relocating its database ownership.
    _SaveInventory(transaction);
    auto* create = CharacterDatabase.GetPreparedStatement(CHAR_INS_WILDERNESS_GEAR_POUCH);
    create->SetData(0, id);
    create->SetData(1, map.GetId());
    create->SetData(2, phase);
    create->SetData(3, x);
    create->SetData(4, y);
    create->SetData(5, z);
    create->SetData(6, value);
    create->SetData(7, uint8(ownerOnly));
    create->SetData(8, guid);
    create->SetData(9, account);
    create->SetData(10, item.GetGUID().GetCounter());
    create->SetData(11, item.GetEntry());
    create->SetData(12, count);
    transaction->Append(create);

    auto* fund = CharacterDatabase.GetPreparedStatement(CHAR_FUND_WILDERNESS_GEAR_POUCH);
    fund->SetData(0, id);
    transaction->Append(fund);
    auto* detach = CharacterDatabase.GetPreparedStatement(CHAR_DETACH_WILDERNESS_GEAR);
    detach->SetData(0, id);
    transaction->Append(detach);

    auto* receipt = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WILDERNESS_POUCH_FUNDING);
    receipt->SetData(0, id);
    receipt->SetData(1, guid);
    receipt->SetData(2, account);
    PreparedQueryResult funding = VerifyPouchWrite(*this, transaction, receipt);
    if (!funding)
        return;

    if (funding->Fetch()[0].Get<uint64>() != 1 || GetItemByPos(bag, slot) != &item)
    {
        GetDigitalInventory().DisconnectOnPersistenceFailure(
            "Wilderness item custody could not be verified; reconnect to refresh your inventory");
        return;
    }

    MoveItemFromInventory(bag, slot, true);
    delete &item;
    Cell const cell(x, y);
    if (map.IsGridLoaded(GridCoord(cell.GridX(), cell.GridY())))
        SpawnPouch(map, id, phase, x, y, z, int32(funding->Fetch()[1].Get<int64>()));

    ChatHandler(GetSession()).PSendSysMessage("You dropped {} x {} in Wilderness pouch {}.", count, proto->Name1, id);
}

bool Acore::WorldPvp::InteractWithWildernessPouch(ChatHandler& handler, uint64 id)
{
    Player& player = *handler.GetSession()->GetPlayer();
    if (!CanUseBountyEscrow() || !player.IsInWorld() || !player.GetMap()->IsWorldMap() ||
        player.IsBeingTeleported() || player.IsInFlight() || player.IsFlying() || player.GetTransport() ||
        player.IsInSanctuary() || player.IsSpectator() || player.GetDigitalInventory().Failed() ||
        (!player.IsAlive() && !player.HasPlayerFlag(PLAYER_FLAGS_GHOST)))
    {
        handler.SendErrorMessage("You cannot recover a Wilderness pouch right now.");
        return false;
    }

    PreparedQueryResult nearby = FindNearbyPouches(player, id);
    bool found = false;
    uint32 copper = 0;
    uint32 itemGuid = 0;
    uint32 entry = 0;
    if (nearby)
    {
        do
        {
            Field* row = nearby->Fetch();
            float const x = row[3].Get<float>();
            float const y = row[4].Get<float>();
            float const z = row[5].Get<float>();
            if (!player.InSamePhase(row[2].Get<uint32>()) || !player.IsInDist(x, y, z, PouchReach) ||
                !player.IsWithinLOS(x, y, z))
                continue;

            if (id)
            {
                found = true;
                copper = row[1].Get<uint32>();
                itemGuid = uint32(row[6].Get<uint64>());
                entry = row[7].Get<uint32>();
                break;
            }

            if (uint32 itemEntry = row[7].Get<uint32>())
            {
                ItemTemplate const* proto = sObjectMgr->GetItemTemplate(itemEntry);
                handler.PSendSysMessage("Wilderness pouch {} contains {} x {}.", row[0].Get<uint64>(),
                    row[8].Get<uint64>(), proto ? proto->Name1 : "unavailable item");
            }
            else
                handler.PSendSysMessage("Wilderness pouch {} contains {} copper.",
                    row[0].Get<uint64>(), row[1].Get<uint32>());
            found = true;
        } while (nearby->NextRow());
    }

    if (!found)
    {
        handler.SendErrorMessage("No claimable Wilderness pouch is within five yards.");
        return false;
    }

    if (!id)
        return true;

    uint32 const guid = player.GetGUID().GetCounter();
    uint32 const balance = player.GetMoney();
    uint64 const nonce = NewPouchNonce();
    CharacterDatabaseTransaction transaction = CharacterDatabase.BeginTransaction();
    auto* claim = CharacterDatabase.GetPreparedStatement(CHAR_CLAIM_WILDERNESS_POUCH);
    claim->SetData(0, guid);
    claim->SetData(1, player.GetSession()->GetAccountId());
    claim->SetData(2, balance);
    claim->SetData(3, nonce);
    claim->SetData(4, id);
    claim->SetData(5, WalletRoom(player));
    claim->SetData(6, itemGuid);
    claim->SetData(7, uint8(player.IsAlive()));
    transaction->Append(claim);
    PendingItemDelivery delivery;
    if (!delivery.Stage(handler, transaction, id, nonce, itemGuid, entry))
        return false;

    auto const claimed = ReadPouchClaim(player, transaction, id, nonce);
    if (!claimed)
        return false;

    if (!*claimed)
    {
        handler.SendErrorMessage("The pouch is no longer available or your wallet has insufficient room.");
        return false;
    }

    if (copper)
        player.SetMoney(balance + copper);

    delivery.Publish(player);
    RemovePouch(player, id);
    if (itemGuid)
        handler.SendSysMessage("Your recovered item is in your mailbox.");
    else
        handler.PSendSysMessage("You recovered {} copper from the Wilderness pouch.", copper);
    return true;
}

bool Acore::WorldPvp::InteractWithBloodyAuctionHouse(ChatHandler& handler, uint64 id, bool requireCapital)
{
    Player& player = *handler.GetSession()->GetPlayer();
    if (!CanUseBountyEscrow() || !player.IsInWorld() || !player.IsAlive() || player.IsBeingTeleported() ||
        player.IsSpectator() || player.GetDigitalInventory().Failed() || player.IsInCombat())
    {
        handler.SendErrorMessage("You can't use the Bloody Auction House right now.");
        return false;
    }

    if (requireCapital && (!player.GetMap()->IsWorldMap() ||
        !IsCapital(sAreaTableStore.LookupEntry(player.GetAreaId()))))
    {
        handler.SendErrorMessage("The Bloody Auction House is available in capital cities.");
        return false;
    }

    uint32 const guid = player.GetGUID().GetCounter();
    uint32 const account = player.GetSession()->GetAccountId();
    auto* query = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WILDERNESS_AUCTION_POUCHES);
    query->SetData(0, guid);
    query->SetData(1, account);
    query->SetData(2, id);
    query->SetData(3, id);
    PreparedQueryResult listings = CharacterDatabase.Query(query);
    if (!listings)
    {
        handler.SendErrorMessage(id ? "That Bloody Auction House pouch is unavailable." :
            "The Bloody Auction House has no pouches available to you.");
        return false;
    }

    if (!id)
    {
        do
        {
            Field* row = listings->Fetch();
            uint32 const copper = row[1].Get<uint32>();
            bool const owner = row[2].Get<uint64>() != 0;
            if (uint32 entry = row[4].Get<uint32>())
            {
                ItemTemplate const* proto = sObjectMgr->GetItemTemplate(entry);
                handler.PSendSysMessage("Pouch {} contains {} x {}. {} price: {} copper.",
                    row[0].Get<uint64>(), row[6].Get<uint64>(), proto ? proto->Name1 : "unavailable item",
                    owner ? "Buyback" : "Public purchase", WildernessItemAuctionFee(row[5].Get<uint32>(), owner));
            }
            else
                handler.PSendSysMessage("Pouch {} contains {} copper. {} fee: {} copper.",
                    row[0].Get<uint64>(), copper, owner ? "Buyback" : "Public purchase",
                    WildernessAuctionFee(copper, owner));
        } while (listings->NextRow());
        handler.SendSysMessage("Use .bloodyauction buy <pouch ID> to purchase.");
        return true;
    }

    Field* row = listings->Fetch();
    uint32 const copper = row[1].Get<uint32>();
    bool const owner = row[2].Get<uint64>() != 0;
    uint32 const itemGuid = uint32(row[3].Get<uint64>());
    uint32 const fee = itemGuid ? WildernessItemAuctionFee(row[5].Get<uint32>(), owner) :
        WildernessAuctionFee(copper, owner);
    uint32 const balance = player.GetMoney();
    if (balance < fee || (copper > fee && copper - fee > WalletRoom(player)))
    {
        handler.SendErrorMessage("You need enough copper for the fee and enough wallet room for the payout.");
        return false;
    }

    uint32 const updatedBalance = balance - fee + copper;
    uint64 const nonce = NewPouchNonce();
    CharacterDatabaseTransaction transaction = CharacterDatabase.BeginTransaction();
    auto* buy = CharacterDatabase.GetPreparedStatement(CHAR_BUY_WILDERNESS_AUCTION_POUCH);
    buy->SetData(0, guid);
    buy->SetData(1, account);
    buy->SetData(2, updatedBalance);
    buy->SetData(3, nonce);
    buy->SetData(4, fee);
    buy->SetData(5, id);
    buy->SetData(6, copper);
    buy->SetData(7, itemGuid);
    transaction->Append(buy);
    PendingItemDelivery delivery;
    if (!delivery.Stage(handler, transaction, id, nonce, itemGuid, row[4].Get<uint32>()))
        return false;

    auto const claimed = ReadPouchClaim(player, transaction, id, nonce);
    if (!claimed)
        return false;

    if (!*claimed)
    {
        handler.SendErrorMessage("That Bloody Auction House pouch is no longer available.");
        return false;
    }

    player.SetMoney(updatedBalance);
    delivery.Publish(player);
    if (itemGuid)
        handler.PSendSysMessage("Your Bloody Auction House item is in your mailbox. You paid {} copper.", fee);
    else
        handler.PSendSysMessage("You recovered {} copper from the Bloody Auction House for a {} copper fee.",
            copper, fee);
    return true;
}
