/*
 * Copyright (C) 2016+ AzerothCore <www.azerothcore.org>, released under GNU AGPL v3 license.
 */

#include "DigitalInventory.h"
#include "Bag.h"
#include "Chat.h"
#include "Config.h"
#include "DBCStores.h"
#include "GameObject.h"
#include "Guild.h"
#include "Item.h"
#include "ItemPackets.h"
#include "Log.h"
#include "ObjectAccessor.h"
#include "ObjectMgr.h"
#include "Opcodes.h"
#include "Player.h"
#include "Spell.h"
#include "WorldPacket.h"
#include "WorldSession.h"
#include <algorithm>
#include <cctype>
#include <cmath>
#include <limits>
#include <sstream>
#include <set>
#include <tuple>

namespace
{
    constexpr uint8 ProtocolVersion = 3;
    // Stored stacks merge up to this size regardless of the template stack limit.
    constexpr uint32 VirtualStackMax = 1000;
    constexpr size_t MaxTagLength = 24;
    constexpr uint32 DefaultPageSize = 20;
    constexpr uint32 MaximumPageSize = 255;
    bool Enabled = false;
    uint32 InitialCapacity = 256;
    uint32 MaximumCapacity = 10000;
    uint32 UpgradeSize = 256;
    uint32 UpgradeCost = 1000000;
    // Account bank: unlock fee, starting size, and an escalating price per size increase.
    uint32 BankUnlockCost = 10000000;
    uint32 BankInitialSlots = 512;
    uint32 BankMaximumSlots = 100000;
    uint32 BankUpgradeSlots = 256;
    uint32 BankUpgradeCost = 1000000;
    double BankUpgradeGrowth = 1.25;

    std::string Lower(std::string text)
    {
        std::transform(text.begin(), text.end(), text.begin(), [](unsigned char c) { return std::tolower(c); });
        return text;
    }

    uint8 Category(Item const* item)
    {
        switch (item->GetTemplate()->Class)
        {
            case ITEM_CLASS_WEAPON:
            case ITEM_CLASS_ARMOR:
                return 1;
            case ITEM_CLASS_CONSUMABLE:
                return 2;
            case ITEM_CLASS_TRADE_GOODS:
            case ITEM_CLASS_REAGENT:
            case ITEM_CLASS_GEM:
                return 3;
            default:
                return 4;
        }
    }

    bool SameStack(Item const* a, Item const* b)
    {
        if (a->GetEntry() != b->GetEntry() || a->GetMaxStackCount() <= 1
            || a->GetUInt32Value(ITEM_FIELD_FLAGS) != b->GetUInt32Value(ITEM_FIELD_FLAGS)
            || a->GetItemRandomPropertyId() != b->GetItemRandomPropertyId()
            || a->GetItemSuffixFactor() != b->GetItemSuffixFactor()
            || a->GetGuidValue(ITEM_FIELD_CREATOR) != b->GetGuidValue(ITEM_FIELD_CREATOR)
            || a->GetGuidValue(ITEM_FIELD_GIFTCREATOR) != b->GetGuidValue(ITEM_FIELD_GIFTCREATOR)
            || a->GetUInt32Value(ITEM_FIELD_DURABILITY) != b->GetUInt32Value(ITEM_FIELD_DURABILITY)
            || a->GetText() != b->GetText())
            return false;

        for (uint8 i = 0; i < MAX_ITEM_PROTO_SPELLS; ++i)
            if (a->GetSpellCharges(i) != b->GetSpellCharges(i))
                return false;

        for (uint8 i = 0; i < MAX_ENCHANTMENT_SLOT; ++i)
        {
            auto slot = EnchantmentSlot(i);
            if (a->GetEnchantmentId(slot) != b->GetEnchantmentId(slot)
                || a->GetEnchantmentDuration(slot) != b->GetEnchantmentDuration(slot)
                || a->GetEnchantmentCharges(slot) != b->GetEnchantmentCharges(slot))
                return false;
        }
        return true;
    }

    std::string StackKey(Item const* item)
    {
        std::ostringstream key;
        key << item->GetEntry() << ':' << item->GetUInt32Value(ITEM_FIELD_FLAGS) << ':'
            << item->GetItemRandomPropertyId() << ':' << item->GetItemSuffixFactor() << ':'
            << item->GetGuidValue(ITEM_FIELD_CREATOR).GetRawValue() << ':'
            << item->GetGuidValue(ITEM_FIELD_GIFTCREATOR).GetRawValue() << ':'
            << item->GetUInt32Value(ITEM_FIELD_DURABILITY) << ':';
        for (uint8 i = 0; i < MAX_ITEM_PROTO_SPELLS; ++i)
            key << item->GetSpellCharges(i) << ':';
        for (uint8 i = 0; i < MAX_ENCHANTMENT_SLOT; ++i)
        {
            auto slot = EnchantmentSlot(i);
            key << item->GetEnchantmentId(slot) << ':' << item->GetEnchantmentDuration(slot) << ':'
                << item->GetEnchantmentCharges(slot) << ':';
        }
        key << item->GetText();
        return key.str();
    }

    std::string Link(Item const* item, uint8 level)
    {
        return Acore::StringFormat("item:{}:{}:{}:{}:{}:0:{}:{}:{}", item->GetEntry(),
            item->GetEnchantmentId(PERM_ENCHANTMENT_SLOT), item->GetEnchantmentId(SOCK_ENCHANTMENT_SLOT),
            item->GetEnchantmentId(EnchantmentSlot(SOCK_ENCHANTMENT_SLOT + 1)),
            item->GetEnchantmentId(EnchantmentSlot(SOCK_ENCHANTMENT_SLOT + 2)),
            item->GetItemRandomPropertyId(), item->GetItemSuffixFactor(), level);
    }
}

void DigitalInventory::LoadConfig()
{
    Enabled = sConfigMgr->GetOption<bool>("DigitalInventory.Enable", false);
    // Ownership changes share the existing FIFO writer with every legacy inventory/gold save.
    // A separate synchronous connection could commit ahead of an older queued snapshot.
    if (Enabled && CharacterDatabase.GetAsyncWorkerCount() != 1)
    {
        Enabled = false;
        LOG_ERROR("server.loading", "Digital inventory requires CharacterDatabase.WorkerThreads = 1");
    }
    MaximumCapacity = std::clamp(sConfigMgr->GetOption<uint32>("DigitalInventory.MaximumSlots", 10000),
        256u, 10000u);
    InitialCapacity = std::clamp(sConfigMgr->GetOption<uint32>("DigitalInventory.InitialSlots", 256),
        1u, MaximumCapacity);
    UpgradeSize = std::clamp(sConfigMgr->GetOption<uint32>("DigitalInventory.UpgradeSlots", 256), 1u, MaximumCapacity);
    UpgradeCost = std::min(sConfigMgr->GetOption<uint32>("DigitalInventory.UpgradeCost", 1000000),
        uint32(MAX_MONEY_AMOUNT));
    BankUnlockCost = std::min(sConfigMgr->GetOption<uint32>("DigitalInventory.BankUnlockCost", 10000000),
        uint32(MAX_MONEY_AMOUNT));
    BankMaximumSlots = std::clamp(sConfigMgr->GetOption<uint32>("DigitalInventory.BankMaximumSlots", 100000), 256u, 1000000u);
    BankInitialSlots = std::clamp(sConfigMgr->GetOption<uint32>("DigitalInventory.BankInitialSlots", 512), 1u, BankMaximumSlots);
    BankUpgradeSlots = std::clamp(sConfigMgr->GetOption<uint32>("DigitalInventory.BankUpgradeSlots", 256), 1u, BankMaximumSlots);
    BankUpgradeCost = std::min(sConfigMgr->GetOption<uint32>("DigitalInventory.BankUpgradeCost", 1000000),
        uint32(MAX_MONEY_AMOUNT));
    BankUpgradeGrowth = std::clamp(sConfigMgr->GetOption<float>("DigitalInventory.BankUpgradeGrowth", 1.25f), 1.0f, 3.0f);
}

DigitalInventory::~DigitalInventory()
{
    for (auto const& [guid, stored] : _items)
        delete stored.item;
    for (Item* item : _deleted)
        delete item;
}

void DigitalInventory::Load(PreparedQueryResult metadata, PreparedQueryResult items)
{
    bool bank = _scope == Bank;
    uint32 maximumStored = bank ? BankMaximumSlots : 10000;
    _capacity = bank ? BankInitialSlots : InitialCapacity;
    if (metadata)
    {
        _capacity = metadata->Fetch()[0].Get<uint32>();
        _revision = std::max(metadata->Fetch()[1].Get<uint32>(), 1u);
        if (bank)
            _unlocked = metadata->Fetch()[2].Get<bool>();
        if (!_capacity || _capacity > maximumStored)
            _failed = true;
    }
    if (items)
    {
        do
        {
            Field* fields = items->Fetch();
            uint32 guid = fields[11].Get<uint32>();
            uint32 entry = fields[12].Get<uint32>();
            if (_items.size() >= maximumStored)
            {
                _failed = true;
                break;
            }
            // Any conflicting location or owner is quarantined, never cloned or silently deleted.
            // Bank items belong to no character (owner 0), like guild bank items.
            uint32 expectedOwner = bank ? 0 : _owner.GetGUID().GetCounter();
            if (fields[14].Get<uint32>() != expectedOwner || fields[15].Get<uint8>())
            {
                _failed = true;
                LOG_ERROR("entities.player", "Digital inventory conflict for player {} item {}",
                    _owner.GetGUID().ToString(), ObjectGuid::Create<HighGuid::Item>(guid).ToString());
                continue;
            }
            Item* item = new Item();
            if (!item->LoadFromDB(guid, bank ? ObjectGuid::Empty : _owner.GetGUID(), fields, entry))
            {
                delete item;
                _failed = true;
                continue;
            }
            item->SetSlot(NULL_SLOT);
            item->SetContainer(nullptr);
            item->FSetState(ITEM_UNCHANGED);
            auto stored = _items.emplace(guid, StoredItem{item, fields[13].Get<bool>(), false}).first;
            stored->second.tag = fields[16].Get<std::string>();
            stored->second.split = fields[17].Get<bool>();
        } while (items->NextRow());
    }
    _loaded = true;
}

void DigitalInventory::LoadBank()
{
    if (_scope != Bank || _loaded || _bankLoadAttempted || !Enabled)
        return;
    _bankLoadAttempted = true;
    uint32 account = _owner.GetSession()->GetAccountId();
    auto* metaStmt = CharacterDatabase.GetPreparedStatement(CHAR_SEL_ACCOUNT_BANK);
    metaStmt->SetData(0, account);
    PreparedQueryResult metadata = CharacterDatabase.Query(metaStmt);
    auto* itemStmt = CharacterDatabase.GetPreparedStatement(CHAR_SEL_ACCOUNT_BANK_ITEMS);
    itemStmt->SetData(0, account);
    PreparedQueryResult items = CharacterDatabase.Query(itemStmt);
    Load(metadata, items);
}

// Stock bank slots are retired: anything still sitting there moves into the account bank.
bool DigitalInventory::MigrateLegacyBank()
{
    if (_scope != Bank || !Enabled || !_loaded || _failed)
        return false;
    std::vector<Item*> pending;
    for (uint8 slot = BANK_SLOT_ITEM_START; slot < BANK_SLOT_ITEM_END; ++slot)
        if (Item* item = _owner.GetItemByPos(INVENTORY_SLOT_BAG_0, slot))
            pending.push_back(item);
    for (uint8 bag = BANK_SLOT_BAG_START; bag < BANK_SLOT_BAG_END; ++bag)
        if (Bag* container = _owner.GetBagByPos(bag))
            for (uint32 slot = 0; slot < container->GetBagSize(); ++slot)
                if (Item* item = container->GetItemByPos(slot))
                    pending.push_back(item);
    bool moved = false;
    for (Item* item : pending)
        moved = DepositItem(item) || moved;
    if (moved)
        MergeStacks(false);
    return moved;
}

// Bank deposit: a stack from carried digital storage, or a physical carried item.
bool DigitalInventory::DepositFrom(uint32 guid)
{
    if (_items.size() >= _capacity)
        return false;
    DigitalInventory& carried = _owner.GetDigitalInventory();
    auto src = carried._items.find(guid);
    if (src == carried._items.end())
        return DepositItem(_owner.GetItemByGuid(ObjectGuid::Create<HighGuid::Item>(guid)));
    StoredItem moved = src->second;
    carried._items.erase(src);
    carried._removedStorage.push_back(guid);
    carried.Changed();
    moved.item->SetOwnerGUID(ObjectGuid::Empty);
    if (moved.item->GetState() != ITEM_NEW)
        moved.item->FSetState(ITEM_CHANGED);
    moved.dirty = true;
    _items.emplace(guid, moved);
    Changed();
    return true;
}

// Bank withdrawal lands in carried digital storage, never in a physical slot.
bool DigitalInventory::WithdrawTo(uint32 guid)
{
    DigitalInventory& carried = _owner.GetDigitalInventory();
    auto src = _items.find(guid);
    if (src == _items.end() || !carried._loaded || carried._failed || !carried._active
        || carried._items.size() >= carried._capacity)
        return false;
    StoredItem moved = src->second;
    _items.erase(src);
    _removedStorage.push_back(guid);
    Changed();
    moved.item->SetOwnerGUID(_owner.GetGUID());
    if (moved.item->GetState() != ITEM_NEW)
        moved.item->FSetState(ITEM_CHANGED);
    moved.dirty = true;
    carried._items.emplace(guid, moved);
    carried.Changed();
    carried.MergeStacks(false);
    return true;
}

uint32 DigitalInventory::UpgradePrice() const
{
    if (_scope == Carried)
        return UpgradeCost;
    uint32 steps = _capacity > BankInitialSlots ? (_capacity - BankInitialSlots) / BankUpgradeSlots : 0;
    double price = double(BankUpgradeCost) * std::pow(BankUpgradeGrowth, double(steps));
    return uint32(std::min(price, double(MAX_MONEY_AMOUNT)));
}

uint32 DigitalInventory::UpgradeSlots() const
{
    uint32 maximum = _scope == Bank ? BankMaximumSlots : MaximumCapacity;
    return std::min(_scope == Bank ? BankUpgradeSlots : UpgradeSize, maximum > _capacity ? maximum - _capacity : 0);
}

uint32 DigitalInventory::Count(uint32 entry, Item const* skip) const
{
    uint64 count = 0;
    for (auto const& [guid, stored] : _items)
    {
        if (stored.item != skip && stored.item->GetEntry() == entry)
            count += stored.item->GetCount();
        if (skip && skip->GetTemplate()->GemProperties && stored.item != skip && stored.item->HasSocket())
            count += stored.item->GetGemCountWithID(entry);
    }
    return uint32(std::min(count, uint64(std::numeric_limits<uint32>::max())));
}

uint32 DigitalInventory::CountLimit(uint32 category, Item const* skip) const
{
    uint32 count = 0;
    for (auto const& [guid, stored] : _items)
        if (stored.item != skip && stored.item->GetTemplate()->ItemLimitCategory == category)
            count += stored.item->GetCount();
    return count;
}

bool DigitalInventory::HasTool(uint32 category) const
{
    for (auto const& [guid, stored] : _items)
        if (_owner.IsTotemCategoryCompatiableWith(stored.item->GetTemplate(), category))
            return true;
    return false;
}

bool DigitalInventory::CanAct() const
{
    return _loaded && !_failed && _owner.IsInWorld() && _owner.IsAlive()
        && !_owner.GetTradeData() && !_owner.IsBeingTeleported() && !_owner.IsNonMeleeSpellCast(false);
}

bool DigitalInventory::CanDeposit(Item const* item) const
{
    if (!item || item->GetOwnerGUID() != _owner.GetGUID() || item->IsBag() || item->IsInTrade()
        || item->IsRefundable() || item->IsBOPTradable() || item->IsWrapped() || item->m_lootGenerated
        || item->IsCurrencyToken() || item->GetTemplate()->Duration || item->IsConjuredConsumable()
        || item->GetTemplate()->Map || item->GetTemplate()->Area || item->GetTemplate()->HolidayId
        || item->GetGUID() == _owner.GetLootGUID())
        return false;
    for (uint8 i = 0; i < MAX_ENCHANTMENT_SLOT; ++i)
        if (item->GetEnchantmentDuration(EnchantmentSlot(i)))
            return false;
    for (auto const& spell : item->GetTemplate()->Spells)
        if (spell.SpellId > 0 && spell.SpellTrigger == ITEM_SPELLTRIGGER_ON_NO_DELAY_USE)
            return false;
    // Equipment, bank, keyring and currency slots never enter bulk deposits.
    uint8 bag = item->GetBagSlot();
    uint8 slot = item->GetSlot();
    bool carriedSlot = (bag == INVENTORY_SLOT_BAG_0 && slot >= INVENTORY_SLOT_ITEM_START && slot < INVENTORY_SLOT_ITEM_END)
        || (bag >= INVENTORY_SLOT_BAG_START && bag < INVENTORY_SLOT_BAG_END);
    bool bankSlot = (bag == INVENTORY_SLOT_BAG_0 && slot >= BANK_SLOT_ITEM_START && slot < BANK_SLOT_ITEM_END)
        || (bag >= BANK_SLOT_BAG_START && bag < BANK_SLOT_BAG_END);
    return carriedSlot || (_scope == Bank && bankSlot);
}

void DigitalInventory::Changed()
{
    _dirty = true;
    if (++_revision == 0)
        ++_revision;
}

bool DigitalInventory::DepositItem(Item* item)
{
    if (!CanDeposit(item) || _items.size() >= _capacity)
        return false;
    uint32 guid = item->GetGUID().GetCounter();
    _owner.RemoveItem(item->GetBagSlot(), item->GetSlot(), true);
    item->RemoveFromUpdateQueueOf(&_owner);
    if (item->IsInWorld())
    {
        item->RemoveFromWorld();
        item->DestroyForPlayer(&_owner);
    }
    item->SetSlot(NULL_SLOT);
    item->SetContainer(nullptr);
    item->SetGuidValue(ITEM_FIELD_CONTAINED, ObjectGuid::Empty);
    if (_scope == Bank)
        item->SetOwnerGUID(ObjectGuid::Empty);
    if (item->GetState() != ITEM_NEW)
        item->FSetState(ITEM_CHANGED);
    _removedInventory.push_back(guid);
    _items.emplace(guid, StoredItem{item});
    Changed();
    return true;
}

Item* DigitalInventory::WithdrawItem(uint32 guid)
{
    auto itr = _items.find(guid);
    if (itr == _items.end())
        return nullptr;
    Item* source = itr->second.item;
    Item* item = source;
    bool partial = source->GetCount() > source->GetMaxStackCount();
    if (partial)
    {
        // Virtual stacks may exceed the template limit; a carried slot never can.
        item = CloneStack(source, source->GetMaxStackCount());
        if (!item)
            return nullptr;
    }
    ItemPosCountVec dest;
    // Materialize into an empty slot: never merge a selected instance into another stack before an action.
    auto trySlot = [&](uint8 bag, uint8 slot)
    {
        if (_owner.GetItemByPos(bag, slot))
            return false;
        dest.clear();
        return _owner.CanStoreItem(bag, slot, dest, item, false) == EQUIP_ERR_OK;
    };
    bool found = false;
    for (uint8 slot = INVENTORY_SLOT_ITEM_START; slot < INVENTORY_SLOT_ITEM_END && !found; ++slot)
        found = trySlot(INVENTORY_SLOT_BAG_0, slot);
    for (uint8 bag = INVENTORY_SLOT_BAG_START; bag < INVENTORY_SLOT_BAG_END && !found; ++bag)
        if (Bag* container = _owner.GetBagByPos(bag))
            for (uint32 slot = 0; slot < container->GetBagSize() && !found; ++slot)
                found = trySlot(bag, uint8(slot));
    if (!found)
    {
        _owner.SendEquipError(EQUIP_ERR_INVENTORY_FULL, item);
        if (partial)
            delete item;
        return nullptr;
    }
    if (partial)
    {
        source->SetCount(source->GetCount() - item->GetCount());
        if (source->GetState() != ITEM_NEW)
            source->FSetState(ITEM_CHANGED);
        itr->second.dirty = true;
    }
    else
    {
        _items.erase(itr);
        _removedStorage.push_back(guid);
    }
    // StoreItem applies ordinary binding, update fields and stack rules. No quest acquire/loss occurs.
    Item* stored = _owner.StoreItem(dest, item, true);
    if (stored)
        _pinned[stored->GetGUID().GetCounter()] = 30000;
    Changed();
    return stored;
}

std::vector<Item*> DigitalInventory::Items() const
{
    std::vector<Item*> out;
    for (auto const& [guid, stored] : _items)
        out.push_back(stored.item);
    return out;
}

Item* DigitalInventory::TakeForShop(uint32 guid)
{
    auto itr = _items.find(guid);
    if (itr == _items.end())
        return nullptr;
    Item* item = itr->second.item;
    _items.erase(itr);
    _removedStorage.push_back(guid);
    Changed();
    Send(0, 0, "");
    return item;
}

uint32 DigitalInventory::Consume(uint32 entry, uint32 count)
{
    uint32 consumed = 0;
    for (auto itr = _items.begin(); itr != _items.end() && consumed < count;)
    {
        Item* item = itr->second.item;
        if (item->GetEntry() != entry)
        {
            ++itr;
            continue;
        }
        uint32 take = std::min(count - consumed, item->GetCount());
        _owner.ItemRemovedQuestCheck(entry, take);
        consumed += take;
        if (take == item->GetCount())
        {
            _removedStorage.push_back(itr->first);
            _deleted.push_back(item);
            itr = _items.erase(itr);
        }
        else
        {
            item->SetCount(item->GetCount() - take);
            if (item->GetState() != ITEM_NEW)
                item->FSetState(ITEM_CHANGED);
            ++itr;
        }
        Changed();
    }
    return consumed;
}

Item* DigitalInventory::CloneStack(Item* source, uint32 count)
{
    Item* clone = source->CloneItem(count, &_owner);
    if (!clone)
        return nullptr;
    clone->SetSlot(NULL_SLOT);
    clone->SetText(source->GetText());
    clone->SetUInt32Value(ITEM_FIELD_DURABILITY, source->GetUInt32Value(ITEM_FIELD_DURABILITY));
    clone->SetUInt32Value(ITEM_FIELD_PROPERTY_SEED, source->GetItemSuffixFactor());
    for (uint8 i = 0; i < MAX_ITEM_PROTO_SPELLS; ++i)
        clone->SetSpellCharges(i, source->GetSpellCharges(i));
    for (uint8 i = 0; i < MAX_ENCHANTMENT_SLOT; ++i)
    {
        auto slot = EnchantmentSlot(i);
        clone->SetEnchantment(slot, source->GetEnchantmentId(slot), source->GetEnchantmentDuration(slot),
            source->GetEnchantmentCharges(slot));
    }
    clone->RemoveFromUpdateQueueOf(&_owner);
    return clone;
}

// Automatic passes leave deliberately split stacks alone; the Stack button (manual) merges everything
// and clears the split marks.
void DigitalInventory::MergeStacks(bool manual)
{
    std::map<std::string, std::vector<uint32>> groups;
    for (auto const& [guid, stored] : _items)
        if (stored.item->GetMaxStackCount() > 1 && (manual || !stored.split))
            groups[StackKey(stored.item) + '|' + stored.tag].push_back(guid);
    for (auto const& [key, guids] : groups)
    {
        if (manual)
            for (uint32 guid : guids)
            {
                auto& member = _items.at(guid);
                if (member.split)
                {
                    member.split = false;
                    member.dirty = true;
                    Changed();
                }
            }
        Item* target = nullptr;
        uint32 targetGuid = 0;
        for (uint32 guid : guids)
        {
            auto src = _items.find(guid);
            Item* source = src->second.item;
            if (!target || target->GetCount() >= VirtualStackMax || !SameStack(source, target))
            {
                target = source;
                targetGuid = guid;
                continue;
            }
            uint32 moved = std::min(source->GetCount(), VirtualStackMax - target->GetCount());
            target->SetCount(target->GetCount() + moved);
            if (target->GetState() != ITEM_NEW)
                target->FSetState(ITEM_CHANGED);
            auto& destination = _items.at(targetGuid);
            destination.favorite = destination.favorite || src->second.favorite;
            destination.split = false;
            destination.dirty = true;
            if (moved == source->GetCount())
            {
                _removedStorage.push_back(src->first);
                _deleted.push_back(source);
                _items.erase(src);
            }
            else
            {
                source->SetCount(source->GetCount() - moved);
                if (source->GetState() != ITEM_NEW)
                    source->FSetState(ITEM_CHANGED);
                src->second.split = false;
                src->second.dirty = true;
                target = source;
                targetGuid = guid;
            }
            Changed();
        }
    }
}

void DigitalInventory::Save(CharacterDatabaseTransaction trans)
{
    if (!_loaded || !_dirty || _failed)
        return;
    for (uint32 guid : _removedInventory)
        Item::DeleteFromInventoryDB(trans, guid);
    bool bank = _scope == Bank;
    uint32 key = bank ? _owner.GetSession()->GetAccountId() : _owner.GetGUID().GetCounter();
    for (uint32 guid : _removedStorage)
    {
        auto* stmt = CharacterDatabase.GetPreparedStatement(bank ? CHAR_DEL_ACCOUNT_BANK_ITEM : CHAR_DEL_DIGITAL_ITEM);
        stmt->SetData(0, key);
        stmt->SetData(1, guid);
        trans->Append(stmt);
    }
    for (Item* item : _deleted)
    {
        item->FSetState(ITEM_REMOVED);
        item->SaveToDB(trans);
    }
    _deleted.clear();
    for (auto& [guid, stored] : _items)
    {
        if (!stored.dirty && stored.item->GetState() == ITEM_UNCHANGED)
            continue;
        stored.item->SaveToDB(trans);
        auto* stmt = CharacterDatabase.GetPreparedStatement(bank ? CHAR_REP_ACCOUNT_BANK_ITEM : CHAR_REP_DIGITAL_ITEM);
        stmt->SetData(0, key);
        stmt->SetData(1, guid);
        stmt->SetData(2, stored.favorite);
        stmt->SetData(3, stored.tag);
        stmt->SetData(4, stored.split);
        trans->Append(stmt);
        stored.dirty = false;
    }
    auto* stmt = CharacterDatabase.GetPreparedStatement(bank ? CHAR_REP_ACCOUNT_BANK : CHAR_REP_DIGITAL_STORAGE);
    stmt->SetData(0, key);
    stmt->SetData(1, _capacity);
    stmt->SetData(2, _revision);
    if (bank)
        stmt->SetData(3, _unlocked);
    trans->Append(stmt);
    _removedInventory.clear();
    _removedStorage.clear();
    _dirty = false;
}

bool DigitalInventory::Persist()
{
    auto trans = CharacterDatabase.BeginTransaction();
    _owner.SaveInventoryAndGoldToDB(trans);
    if (CharacterDatabase.AsyncCommitTransaction(trans).m_future.get())
        return true;
    // No success reply, autosave or logout save may overwrite the last durable inventory on failure.
    _failed = true;
    LOG_ERROR("entities.player", "Digital inventory transaction failed for {}; disconnecting for recovery",
        _owner.GetGUID().ToString());
    _owner.GetSession()->KickPlayer("Digital inventory persistence failure; reconnect to recover");
    return false;
}

void DigitalInventory::PerformItemAction(uint8 action, Item* item, uint64 target)
{
    if (!item)
        return;
    WorldSession* session = _owner.GetSession();
    if (action == Equip)
    {
        WorldPackets::Item::AutoEquipItem packet{WorldPacket(CMSG_AUTOEQUIP_ITEM)};
        packet.SourceBag = item->GetBagSlot();
        packet.SourceSlot = item->GetSlot();
        session->HandleAutoEquipItemOpcode(packet);
    }
    else if (action == Sell)
    {
        WorldPackets::Item::SellItem packet{WorldPacket(CMSG_SELL_ITEM)};
        packet.ItemGuid = item->GetGUID();
        packet.VendorGuid = ObjectGuid(target);
        packet.Count = item->GetCount();
        session->HandleSellItemOpcode(packet);
    }
    else if (action == Use)
    {
        for (auto const& spell : item->GetTemplate()->Spells)
        {
            if (spell.SpellId <= 0 || spell.SpellTrigger != ITEM_SPELLTRIGGER_ON_USE)
                continue;
            WorldPacket packet(CMSG_USE_ITEM);
            packet << item->GetBagSlot() << item->GetSlot() << uint8(0) << uint32(spell.SpellId)
                << item->GetGUID() << uint32(0) << uint8(0);
            SpellCastTargets targets;
            if (Unit* unit = ObjectAccessor::GetUnit(_owner, _owner.GetTarget()))
                targets.SetUnitTarget(unit);
            targets.Write(packet);
            session->HandleUseItemOpcode(packet);
            return;
        }
    }
}

void DigitalInventory::Handle(WorldPacket& packet)
{
    auto now = std::chrono::steady_clock::now();
    if (now - _requestWindow >= std::chrono::seconds(1))
    {
        _requestWindow = now;
        _requestsInWindow = 0;
    }
    if (++_requestsInWindow > 8)
        return;
    if (packet.size() < 34 || packet.size() > 114)
        return;
    uint8 version, action, scope, category, sort;
    uint32 request, revision, guid, count, argument;
    uint64 target;
    std::string search;
    packet >> version >> action >> scope >> request >> revision >> guid >> count >> argument >> target
        >> category >> sort >> search;
    if (version != ProtocolVersion || scope != _scope || action > Unlock || search.size() > 80 || category > 5 || sort > 4
        || packet.rpos() != packet.size() || !request || request <= _lastRequest)
        return;
    _lastRequest = request;
    _category = category;
    _sort = sort;
    // SetTag reuses the string field for the tag text, so it must not replace the active search.
    if (action != SetTag)
        _search = Lower(search);
    _offset = argument;
    // Browse carries the client's tile count in "count"; older clients send 0 and keep the default page.
    if (action == Browse)
        _pageSize = count >= 1 && count <= MaximumPageSize ? count : DefaultPageSize;
    if (_scope == Bank)
        LoadBank();
    if (!Enabled || !_loaded || _failed)
    {
        Send(request, 1, "Digital inventory is unavailable. Your normal bags remain accessible.");
        return;
    }
    bool access = _scope == Carried || _unlocked || _owner.GetSession()->IsAtBanker();
    char const* locked = "Remote bank access is locked. Unlock it, or visit a banker.";
    if (action == Activate)
    {
        _active = true;
        if (_scope == Carried)
        {
            _scan = true;
            // The account bank loads with the character; stock bank slots are retired into it.
            DigitalInventory& bank = _owner.GetDigitalBank();
            bank.LoadBank();
            if (bank.MigrateLegacyBank() && !Persist())
                return;
        }
        Send(request, access ? 0 : 4, access ? "Digital inventory ready." : locked);
        return;
    }
    if (action == Browse)
    {
        Send(request, access ? 0 : 4, access ? "" : locked);
        return;
    }
    if (!_active || !CanAct() || revision != _revision)
    {
        Send(request, 2, "Inventory changed or an item action is in progress. Try again.");
        return;
    }
    if (!access && action != Unlock)
    {
        Send(request, 4, locked);
        return;
    }
    bool changed = false;
    uint32 carriedRevision = _owner.GetDigitalInventory()._revision;
    auto itr = _items.find(guid);
    Item* ordinary = _owner.GetItemByGuid(ObjectGuid::Create<HighGuid::Item>(guid));
    if (action == Unlock)
    {
        if (_scope == Bank && !_unlocked && _owner.HasEnoughMoney(BankUnlockCost))
        {
            _owner.ModifyMoney(-int32(BankUnlockCost));
            _unlocked = true;
            Changed();
            changed = true;
        }
    }
    else if (action == Deposit)
    {
        changed = _scope == Bank ? DepositFrom(guid) : DepositItem(ordinary);
        if (changed)
            MergeStacks(false);
    }
    else if (action == DepositAll && _scope == Carried)
    {
        std::vector<Item*> carried;
        for (uint8 slot = INVENTORY_SLOT_ITEM_START; slot < INVENTORY_SLOT_ITEM_END; ++slot)
            if (Item* item = _owner.GetItemByPos(INVENTORY_SLOT_BAG_0, slot))
                carried.push_back(item);
        for (uint8 bag = INVENTORY_SLOT_BAG_START; bag < INVENTORY_SLOT_BAG_END; ++bag)
            if (Bag* container = _owner.GetBagByPos(bag))
                for (uint32 slot = 0; slot < container->GetBagSize(); ++slot)
                    if (Item* item = container->GetItemByPos(slot))
                        carried.push_back(item);
        for (Item* item : carried)
            changed = DepositItem(item) || changed;
        MergeStacks(false);
        changed = changed || _dirty;
    }
    else if (action == Withdraw)
        changed = _scope == Bank ? WithdrawTo(guid) : WithdrawItem(guid) != nullptr;
    else if (action == Split && itr != _items.end() && count && count < itr->second.item->GetCount()
        && _items.size() < _capacity)
    {
        Item* source = itr->second.item;
        if (Item* clone = CloneStack(source, count))
        {
            source->SetCount(source->GetCount() - count);
            if (source->GetState() != ITEM_NEW)
                source->FSetState(ITEM_CHANGED);
            // Both halves stay split until the user presses Stack.
            itr->second.split = true;
            itr->second.dirty = true;
            _items.emplace(clone->GetGUID().GetCounter(),
                StoredItem{clone, itr->second.favorite, true, itr->second.tag, true});
            Changed();
            changed = true;
        }
    }
    else if (action == Merge)
    {
        MergeStacks(true);
        changed = _dirty;
    }
    else if (action == Expand && UpgradeSlots() && count == UpgradePrice() && _owner.HasEnoughMoney(count))
    {
        _owner.ModifyMoney(-int32(count));
        _capacity += UpgradeSlots();
        Changed();
        changed = true;
    }
    else if (action == SetTag && itr != _items.end())
    {
        std::string tag;
        for (char c : search)
            if (uint8(c) >= 0x20 && uint8(c) != 0x7F && c != '|' && tag.size() < MaxTagLength)
                tag += c;
        tag.erase(0, tag.find_first_not_of(' '));
        tag.erase(tag.find_last_not_of(' ') + 1);
        if (tag != itr->second.tag)
        {
            itr->second.tag = tag;
            itr->second.dirty = true;
            Changed();
            changed = true;
        }
    }
    else if (action == Favorite && itr != _items.end())
    {
        itr->second.favorite = !itr->second.favorite;
        itr->second.dirty = true;
        Changed();
        changed = true;
    }
    else if (_scope == Carried && (action == Use || action == Equip || action == Sell))
    {
        // Reuse stock validators only after materializing an ordinary carried item.
        Item* item = itr != _items.end() ? WithdrawItem(guid) : ordinary;
        if (item && _owner.IsInventoryPos(item->GetBagSlot(), item->GetSlot()))
        {
            PerformItemAction(action, item, target);
            Changed();
            changed = true;
        }
    }
    if ((changed || _dirty) && !Persist())
        return;
    Send(request, changed ? 0 : 3,
        changed ? "" : "Action unavailable. Check capacity, gold, item restrictions or bag space.");
    // A bank transfer also changes what the carried window shows.
    if (_scope == Bank && _owner.GetDigitalInventory()._revision != carriedRevision)
        _owner.GetDigitalInventory().Send(0, 0, "");
}

void DigitalInventory::Update(uint32 diff)
{
    if (_scope == Bank || !Enabled || !_active || _failed)
        return;
    _elapsed += diff;
    for (auto itr = _pinned.begin(); itr != _pinned.end();)
    {
        if (itr->second <= diff)
            itr = _pinned.erase(itr);
        else
        {
            itr->second -= diff;
            ++itr;
        }
    }
    if (_elapsed < 1000 || !CanAct())
        return;
    _elapsed = 0;
    std::set<uint32> actionItems;
    for (uint8 button = 0; button < MAX_ACTION_BUTTONS; ++button)
        if (ActionButton const* action = _owner.GetActionButton(button))
            if (action->GetType() == ACTION_BUTTON_ITEM)
                actionItems.insert(action->GetAction());
    // Stock action bars need a real item object. Retain/refill one action stack for bound items.
    for (uint32 entry : actionItems)
    {
        if (_owner.GetItemByEntry(entry))
            continue;
        if (!_owner.GetFreeInventorySpace())
            break;
        for (auto const& [guid, stored] : _items)
            if (stored.item->GetEntry() == entry)
            {
                WithdrawItem(guid);
                break;
            }
    }
    if (_scan && !_owner.IsInCombat())
    {
        _scan = false;
        std::set<uint32> retained;
        auto tryDeposit = [&](Item* item)
        {
            if (!item)
                return;
            if (actionItems.count(item->GetEntry()) && retained.insert(item->GetEntry()).second)
                return;
            if (!_pinned.count(item->GetGUID().GetCounter()))
                DepositItem(item);
        };
        for (uint8 slot = INVENTORY_SLOT_ITEM_START; slot < INVENTORY_SLOT_ITEM_END; ++slot)
            tryDeposit(_owner.GetItemByPos(INVENTORY_SLOT_BAG_0, slot));
        for (uint8 bag = INVENTORY_SLOT_BAG_START; bag < INVENTORY_SLOT_BAG_END; ++bag)
            if (Bag* container = _owner.GetBagByPos(bag))
                for (uint32 slot = 0; slot < container->GetBagSize(); ++slot)
                    tryDeposit(container->GetItemByPos(slot));
        MergeStacks(false);
    }
    if (_dirty && Persist())
        Send(0, 0, "");
}

void DigitalInventory::Send(uint32 request, uint8 status, std::string const& message)
{
    struct Row
    {
        Item* item;
        bool digital;
        bool favorite;
        std::string tag;
        bool split;
    };
    std::vector<Row> rows;
    auto append = [&](Item* item, bool digital, bool favorite, std::string const& tag = "", bool split = false)
    {
        if (!item || (_category && _category < 5 && Category(item) != _category) || (_category == 5 && !favorite))
            return;
        if (!_search.empty() && Lower(item->GetTemplate()->Name1).find(_search) == std::string::npos
            && std::to_string(item->GetEntry()).find(_search) == std::string::npos
            && Lower(tag).find(_search) == std::string::npos)
            return;
        rows.push_back({item, digital, favorite, tag, split});
    };
    bool access = _scope == Carried || _unlocked || _owner.GetSession()->IsAtBanker();
    if (access)
        for (auto const& [guid, stored] : _items)
            append(stored.item, true, stored.favorite, stored.tag, stored.split);
    if (_scope == Carried)
        for (uint8 slot = INVENTORY_SLOT_ITEM_START; slot < INVENTORY_SLOT_ITEM_END; ++slot)
            append(_owner.GetItemByPos(INVENTORY_SLOT_BAG_0, slot), false, false);
    if (_scope == Carried)
        for (uint8 bag = INVENTORY_SLOT_BAG_START; bag < INVENTORY_SLOT_BAG_END; ++bag)
            if (Bag* container = _owner.GetBagByPos(bag))
                for (uint32 slot = 0; slot < container->GetBagSize(); ++slot)
                    append(container->GetItemByPos(slot), false, false);
    std::sort(rows.begin(), rows.end(), [&](Row const& a, Row const& b)
    {
        if (a.favorite != b.favorite)
            return a.favorite > b.favorite;
        if (_sort == 1 && a.item->GetTemplate()->Quality != b.item->GetTemplate()->Quality)
            return a.item->GetTemplate()->Quality > b.item->GetTemplate()->Quality;
        if (_sort == 2 && a.item->GetCount() != b.item->GetCount())
            return a.item->GetCount() > b.item->GetCount();
        if (_sort == 3 && Category(a.item) != Category(b.item))
            return Category(a.item) < Category(b.item);
        if (_sort == 4 && a.tag != b.tag)
        {
            if (a.tag.empty() || b.tag.empty())
                return b.tag.empty();
            return Lower(a.tag) < Lower(b.tag);
        }
        return std::make_pair(a.item->GetTemplate()->Name1, a.item->GetGUID())
            < std::make_pair(b.item->GetTemplate()->Name1, b.item->GetGUID());
    });
    uint32 total = uint32(rows.size());
    uint32 offset = total ? std::min(_offset / _pageSize, (total - 1) / _pageSize) * _pageSize : 0;
    uint8 size = uint8(std::min(_pageSize, total - offset));
    WorldPacket packet(SMSG_ESTERIA_INVENTORY);
    DigitalInventory& bank = _scope == Bank ? *this : _owner.GetDigitalBank();
    // flags: bit 0 remote bank unlocked, bit 1 standing at a banker
    uint8 flags = uint8(bank._unlocked) | (uint8(_owner.GetSession()->IsAtBanker()) << 1);
    packet << ProtocolVersion << uint8(_scope) << request << _revision << _capacity << uint32(_items.size()) << total << offset
        << UpgradePrice() << UpgradeSlots() << BankUnlockCost
        << uint8(_active && Enabled && !_failed) << status << flags << message << size;
    for (uint32 i = offset; i < offset + size; ++i)
    {
        Row const& row = rows[i];
        Item const* item = row.item;
        std::string icon = "INV_Misc_QuestionMark";
        if (auto const* display = sItemDisplayInfoStore.LookupEntry(item->GetTemplate()->DisplayInfoID))
            icon = display->inventoryIcon;
        packet << uint32(item->GetGUID().GetCounter()) << item->GetEntry() << item->GetCount()
            << uint8(row.digital) << item->GetBagSlot() << item->GetSlot() << uint8(item->GetTemplate()->Quality)
            << uint8(row.favorite) << uint8(Category(item)) << uint8(item->GetTemplate()->InventoryType)
            << uint8(item->IsSoulBound())
            << item->GetUInt32Value(ITEM_FIELD_DURABILITY) << item->GetUInt32Value(ITEM_FIELD_MAXDURABILITY)
            << Link(item, _owner.GetLevel()) << item->GetTemplate()->Name1 << icon << uint8(row.split) << row.tag;
    }
    // A compact count index makes crafting and quest counts independent of the visible page.
    std::map<uint32, std::pair<uint32, uint32>> totals;
    if (_scope == Carried)
    for (auto const& [guid, stored] : _items)
    {
        auto& total = totals[stored.item->GetEntry()];
        total.first += stored.item->GetCount();
        total.second = stored.item->GetTemplate()->TotemCategory;
    }
    packet << uint16(totals.size());
    for (auto const& [entry, total] : totals)
        packet << entry << total.first << total.second;
    _owner.GetSession()->SendPacket(&packet);
}

// Guild bank tab descriptors: one pseudo-row per tab (guid tab, entry slots, count expand price,
// durability expansion step, maxDurability slot ceiling, name). Header price is the next tab's price.
void DigitalInventory::HandleGuild(Player& owner, WorldPacket& packet)
{
    if (!Enabled || packet.size() < 34 || packet.size() > 114)
        return;
    uint8 version, action, scope, category, sort;
    uint32 request, revision, guid, count, argument;
    uint64 target;
    std::string search;
    packet >> version >> action >> scope >> request >> revision >> guid >> count >> argument >> target
        >> category >> sort >> search;
    if (version != ProtocolVersion || scope != 2 || action > Unlock || search.size() > 80
        || packet.rpos() != packet.size() || !request)
        return;
    Guild* guild = owner.GetGuild();
    bool access = guild && owner.IsAlive()
        && owner.FindNearestGameObjectOfType(GAMEOBJECT_TYPE_GUILD_BANK, INTERACTION_DISTANCE * 2.0f);
    uint8 status = access ? 0 : 4;
    std::string message = access ? "" : "Stand next to your guild vault.";
    if (access && action == Expand)
    {
        if (!guild->HandleExpandBankTab(owner.GetSession(), uint8(argument), count))
        {
            status = 3;
            message = "Only the guild master can expand a tab, and only with enough gold.";
        }
    }
    uint32 step = std::max(1u, sConfigMgr->GetOption<uint32>("Guild.BankTabExpandSlots", 16));
    uint32 ceiling = std::min<uint32>(sConfigMgr->GetOption<uint32>("Guild.BankTabMaxSlots", GUILD_BANK_MAX_SLOTS),
        GUILD_BANK_MAX_SLOTS);
    uint8 tabs = access ? guild->GetPurchasedBankTabs() : 0;
    WorldPacket reply(SMSG_ESTERIA_INVENTORY);
    reply << ProtocolVersion << uint8(2) << request << uint32(1) << ceiling << uint32(0) << uint32(tabs) << uint32(0)
        << (access ? guild->GetNextBankTabPrice() : 0u) << uint32(tabs) << uint32(0)
        << uint8(1) << status << uint8(0) << message << tabs;
    for (uint8 tab = 0; tab < tabs; ++tab)
    {
        reply << uint32(tab) << uint32(guild->GetBankTabSlots(tab)) << guild->GetBankTabExpandPrice(tab)
            << uint8(1) << uint8(0) << uint8(0) << uint8(0) << uint8(0) << uint8(0) << uint8(0) << uint8(0)
            << step << ceiling << std::string() << guild->GetBankTabName(tab) << std::string()
            << uint8(0) << std::string();
    }
    reply << uint16(0);
    owner.GetSession()->SendPacket(&reply);
}

void WorldSession::HandleEsteriaInventoryOpcode(WorldPacket& packet)
{
    if (packet.size() > 2 && packet.contents()[2] == 2)
    {
        DigitalInventory::HandleGuild(*GetPlayer(), packet);
        return;
    }
    // Byte 2 of a v3 request selects carried (0) or account bank (1).
    bool bank = packet.size() > 2 && packet.contents()[2] == DigitalInventory::Bank;
    (bank ? GetPlayer()->GetDigitalBank() : GetPlayer()->GetDigitalInventory()).Handle(packet);
}
