/*
 * Credits: silviu20092
 */

#include "ObjectMgr.h"
#include "Chat.h"
#include "ScriptMgr.h"
#include "Config.h"
#include "Player.h"
#include "ScriptedGossip.h"
#include "DatabaseEnv.h"
#include "Tokenize.h"
#include "GameTime.h"
#include "improved_bank.h"

ImprovedBank::ImprovedBank()
{
    accountWide = true;
    searchBank = false;
    showDepositReagents = true;
    depositReagentsSearchBank = false;
    categorizedItemMenuDeposit = true;
    categorizedItemMenuWithdraw = true;

    itemClasses = {
        {0, "Consumable",
            {
                {0, "Consumable" },
                {1, "Potion" },
                {2, "Elixir" },
                {3, "Flask" },
                {4, "Scroll" },
                {5, "Food & Drink" },
                {6, "Item Enhancement" },
                {7, "Bandage" },
                {8, "Other" }
            }
        },

        {1, "Container",
            {
                {0, "Bag"},
                {1, "Soul Bag"},
                {2, "Herb Bag"},
                {3, "Enchanting Bag"},
                {4, "Engineering Bag"},
                {5, "Gem Bag"},
                {6, "Mining Bag"},
                {7, "Leatherworking Bag"},
                {8, "Inscription Bag"}
            }
        },

        {2, "Weapon",
            {
                {0, "One-Handed Axe"},
                {1, "Two-Handed Axe"},
                {2, "Bow"},
                {3, "Gun"},
                {4, "One-Handed Mace"},
                {5, "Two-Handed Mace"},
                {6, "Polearm"},
                {7, "One-Handed Sword"},
                {8, "Two-Handed Sword"},
                {10, "Staff"},
                {13, "Fist Weapon"},
                {14, "Miscellaneous (ex. Mining Pick)"},
                {15, "Dagger"},
                {16, "Thrown"},
                {17, "Spear"},
                {18, "Crossbow"},
                {19, "Wand"},
                {20, "Fishing Pole"}
            }
        },

        {3, "Gem",
            {
                {0, "Red"},
                {1, "Blue"},
                {2, "Yellow"},
                {3, "Purple"},
                {4, "Green"},
                {5, "Orange"},
                {6, "Meta"},
                {7, "Simple"},
                {8, "Prismatic"}
            }
        },

        {4, "Armor",
            {
                {0, "Miscellaneous"},
                {1, "Cloth"},
                {2, "Leather"},
                {3, "Mail"},
                {4, "Plate"},
                {6, "Shield"},
                {7, "Libram"},
                {8, "Idol"},
                {9, "Totem"},
                {10, "Sigil"}
            }
        },

        {5, "Reagent",
            {
                {0, "Reagent"}
            }
        },

        {6, "Projectile",
            {
                {2, "Arrow"},
                {3, "Bullet"}
            }
        },

        {7, "Trade Goods",
            {
                {0, "Trade Goods"},
                {1, "Parts"},
                {2, "Explosives"},
                {3, "Devices"},
                {4, "Jewelcrafting"},
                {5, "Cloth"},
                {6, "Leather"},
                {7, "Metal & Stone"},
                {8, "Meat"},
                {9, "Herb"},
                {10, "Elemental"},
                {11, "Other"},
                {12, "Enchanting"},
                {13, "Materials"},
                {14, "Armor Enchantment"},
                {15, "Weapon Enchantment"}
            }
        },

        {9, "Recipe",
            {
                {0, "Book"},
                {1, "Leatherworking"},
                {2, "Tailoring"},
                {3, "Engineering"},
                {4, "Blacksmithing"},
                {5, "Cooking"},
                {6, "Alchemy"},
                {7, "First Aid"},
                {8, "Enchanting"},
                {9, "Fishing"},
                {10, "Jewelcrafting"},
            }
        },

        {11, "Quiver",
            {
                {2, "Quiver"},
                {3, "Ammo Pouch"}
            }
        },

        {12, "Quest",
            {
                {0, "Quest"}
            }
        },

        {13, "Key",
            {
                {0, "Key"},
                {1, "Lockpick"}
            }
        },

        {15, "Miscellaneous",
            {
                {0, "Junk"},
                {1, "Reagent"},
                {2, "Pet"},
                {3, "Holiday"},
                {4, "Other"},
                {5, "Mount"}
            }
        },

        {16, "Glyph",
            {
                {1, "Warrior"},
                {2, "Paladin"},
                {3, "Hunter"},
                {4, "Rogue"},
                {5, "Priest"},
                {6, "Death Knight"},
                {7, "Shaman"},
                {8, "Mage"},
                {9, "Warlock"},
                {11, "Druid"}
            }
        }
    };
}

ImprovedBank::~ImprovedBank()
{
    for (auto& pageData : playerPagedData)
        pageData.second.Reset();
}

ImprovedBank* ImprovedBank::instance()
{
    static ImprovedBank instance;
    return &instance;
}

void ImprovedBank::SetBlacklistedSubclasses(const std::string& subclasses)
{
    blacklistedSubclasses.clear();
    std::vector<std::string_view> tokenized = Acore::Tokenize(subclasses, ',', false);
    for (auto it = tokenized.begin(); it != tokenized.end(); ++it)
        blacklistedSubclasses.insert(*Acore::StringTo<int32>(*it));
}

bool ImprovedBank::IsBlacklistedSubclass(int32 subclass) const
{
    return blacklistedSubclasses.find(subclass) != blacklistedSubclasses.end();
}

/*static*/ bool ImprovedBank::CompareIdentifier(const BaseIdentifier* a, const BaseIdentifier* b)
{
    if (a->GetType() == ITEM_IDENTIFIER && b->GetType() == ITEM_IDENTIFIER)
        return a->name < b->name;

    return a->id < b->id;
}

std::string ImprovedBank::ItemIcon(uint32 entry, uint32 width, uint32 height, int x, int y) const
{
    std::ostringstream ss;
    ss << "|TInterface";
    const ItemTemplate* temp = sObjectMgr->GetItemTemplate(entry);
    const ItemDisplayInfoEntry* dispInfo = NULL;
    if (temp)
    {
        dispInfo = sItemDisplayInfoStore.LookupEntry(temp->DisplayInfoID);
        if (dispInfo)
            ss << "/ICONS/" << dispInfo->inventoryIcon;
    }
    if (!dispInfo)
        ss << "/InventoryItems/WoWUnknownItem01";
    ss << ":" << width << ":" << height << ":" << x << ":" << y << "|t";
    return ss.str();
}

std::string ImprovedBank::ItemIcon(uint32 entry) const
{
    return ItemIcon(entry, 30, 30, 0, 0);
}

std::string ImprovedBank::ItemNameWithLocale(const Player* player, const ItemTemplate* itemTemplate, int32 randomPropertyId) const
{
    LocaleConstant loc_idx = player->GetSession()->GetSessionDbLocaleIndex();
    std::string name = itemTemplate->Name1;
    if (ItemLocale const* il = sObjectMgr->GetItemLocale(itemTemplate->ItemId))
        ObjectMgr::GetLocaleString(il->Name, loc_idx, name);

    std::array<char const*, 16> const* suffix = nullptr;
    if (randomPropertyId < 0)
    {
        if (const ItemRandomSuffixEntry* itemRandEntry = sItemRandomSuffixStore.LookupEntry(-randomPropertyId))
            suffix = &itemRandEntry->Name;
    }
    else
    {
        if (const ItemRandomPropertiesEntry* itemRandEntry = sItemRandomPropertiesStore.LookupEntry(randomPropertyId))
            suffix = &itemRandEntry->Name;
    }
    if (suffix)
    {
        std::string_view test((*suffix)[(name != itemTemplate->Name1) ? loc_idx : DEFAULT_LOCALE]);
        if (!test.empty())
        {
            name += ' ';
            name += test;
        }
    }

    return name;
}

std::string ImprovedBank::ItemLink(const Player* player, const ItemTemplate* itemTemplate, int32 randomPropertyId) const
{
    std::stringstream oss;
    oss << "|c";
    oss << std::hex << ItemQualityColors[itemTemplate->Quality] << std::dec;
    oss << "|Hitem:";
    oss << itemTemplate->ItemId;
    oss << ":0:0:0:0:0:0:0:0:0|h[";
    oss << ItemNameWithLocale(player, itemTemplate, randomPropertyId);
    oss << "]|h|r";

    return oss.str();
}

void ImprovedBank::AddDepositItem(const Player* player, const Item* item, PagedData& pagedData, const std::string& from) const
{
    ItemTemplate const* itemTemplate = sObjectMgr->GetItemTemplate(item->GetEntry());
    if (!itemTemplate)
        return;

    if (pagedData.type == PAGED_DATA_TYPE_DEPOSIT_CATEGORIZED)
    {
        uint32 itemClass = pagedData.itemClass;
        uint32 itemSubClass = pagedData.itemSubClass;
        if (itemTemplate->Class != itemClass || itemTemplate->SubClass != itemSubClass)
            return;
    }

    if (item->IsNotEmptyBag())
        return;

    ItemIdentifier* itemIdentifier = new ItemIdentifier();
    itemIdentifier->id = pagedData.data.size();
    itemIdentifier->guid = item->GetGUID();
    itemIdentifier->name = ItemNameWithLocale(player, itemTemplate, item->GetItemRandomPropertyId());

    std::ostringstream oss;
    oss << ItemIcon(item->GetEntry());
    oss << ItemLink(player, itemTemplate, item->GetItemRandomPropertyId());
    if (item->GetCount() > 1)
        oss << " - " << item->GetCount() << "x";
    oss << " - IN " << from;

    itemIdentifier->duration = item->GetUInt32Value(ITEM_FIELD_DURATION);
    itemIdentifier->tradeable = item->HasFlag(ITEM_FIELD_FLAGS, ITEM_FIELD_FLAG_BOP_TRADEABLE);

    if (itemIdentifier->duration > 0)
        oss << " - |cffb50505DURATION|r";
    if (itemIdentifier->tradeable)
        oss << " - |cffb50505TRADEABLE|r";

    itemIdentifier->uiName = oss.str();

    pagedData.data.push_back(itemIdentifier);
}

void ImprovedBank::BuildDepositItemCatalogue(const Player* player)
{
    PagedData& pagedData = GetPagedData(player);
    pagedData.Reset();
    bool categorized = GetCategorizedItemMenuDeposit();
    pagedData.type = categorized ? PAGED_DATA_TYPE_DEPOSIT_CLASS : PAGED_DATA_TYPE_DEPOSIT_ALL;

    if (!categorized)
        BuildItemCatalogueFromInventory(player, pagedData);
    else
        BuildItemClassesCatalogue(player, pagedData, itemClasses);

    pagedData.SortAndCalculateTotals();
}

void ImprovedBank::BuildItemClassesCatalogue(const Player* player, PagedData& pagedData, const std::vector<ClassifiedItem>& classifiedItems)
{
    for (const ClassifiedItem& item : classifiedItems)
    {
        BaseIdentifier* identifier = new BaseIdentifier();
        identifier->id = item.id;
        identifier->name = item.name;
        identifier->uiName = item.name;
        pagedData.data.push_back(identifier);
    }
}

void ImprovedBank::BuildItemSubClassesCatalogue(const Player* player, PagedData& pagedData, PagedDataType type, uint32 id)
{
    pagedData.Reset();
    pagedData.type = type;
    pagedData.itemClass = id;

    const ClassifiedItem* classifiedItem = FindItemClass(id);
    ASSERT(classifiedItem != nullptr);

    BuildItemClassesCatalogue(player, pagedData, classifiedItem->subclasses);

    pagedData.SortAndCalculateTotals();
}

void ImprovedBank::BuildItemCatalogueForDeposit(const Player* player, PagedData& pagedData, uint32 id)
{
    pagedData.Reset();
    pagedData.itemSubClass = id;
    pagedData.type = PAGED_DATA_TYPE_DEPOSIT_CATEGORIZED;

    BuildItemCatalogueFromInventory(player, pagedData);

    pagedData.SortAndCalculateTotals();
}

void ImprovedBank::BuildItemCatalogueForWithdraw(const Player* player, PagedData& pagedData, uint32 id)
{
    pagedData.Reset();
    pagedData.itemSubClass = id;
    pagedData.type = PAGED_DATA_TYPE_WITHDRAW_CATEGORIZED;

    BuildWithdrawItemCatalogue(player, pagedData);

    pagedData.SortAndCalculateTotals();
}

void ImprovedBank::BuildItemCatalogueFromInventory(const Player* player, PagedData& pagedData)
{
    for (uint8 i = INVENTORY_SLOT_ITEM_START; i < INVENTORY_SLOT_ITEM_END; i++)
        if (Item* item = player->GetItemByPos(INVENTORY_SLOT_BAG_0, i))
            AddDepositItem(player, item, pagedData, "BACKPACK");

    for (uint8 i = INVENTORY_SLOT_BAG_START; i < INVENTORY_SLOT_BAG_END; i++)
        if (Bag* bag = player->GetBagByPos(i))
            for (uint32 j = 0; j < bag->GetBagSize(); j++)
                if (Item* item = player->GetItemByPos(i, j))
                    AddDepositItem(player, item, pagedData, "BAGS");

    for (uint8 i = KEYRING_SLOT_START; i < KEYRING_SLOT_END; ++i)
        if (Item* item = player->GetItemByPos(INVENTORY_SLOT_BAG_0, i))
            AddDepositItem(player, item, pagedData, "KEYRING");

    for (uint8 i = EQUIPMENT_SLOT_START; i < EQUIPMENT_SLOT_END; i++)
        if (Item* item = player->GetItemByPos(INVENTORY_SLOT_BAG_0, i))
            AddDepositItem(player, item, pagedData, "EQUIPPED");

    if (GetSearchBank())
    {
        for (uint8 i = BANK_SLOT_ITEM_START; i < BANK_SLOT_ITEM_END; i++)
            if (Item* item = player->GetItemByPos(INVENTORY_SLOT_BAG_0, i))
                AddDepositItem(player, item, pagedData, "BANK");

        for (uint8 i = BANK_SLOT_BAG_START; i < BANK_SLOT_BAG_END; i++)
            if (Bag* bag = player->GetBagByPos(i))
                for (uint32 j = 0; j < bag->GetBagSize(); j++)
                    if (Item* item = player->GetItemByPos(i, j))
                        AddDepositItem(player, item, pagedData, "BANK BAGS");
    }
}

void ImprovedBank::PagedData::Reset()
{
    totalPages = 0;
    for (BaseIdentifier* identifier : data)
        delete identifier;
    data.clear();
}

void ImprovedBank::PagedData::CalculateTotals()
{
    totalPages = data.size() / PAGE_SIZE;
    if (data.size() % PAGE_SIZE != 0)
        totalPages++;
}

void ImprovedBank::PagedData::SortAndCalculateTotals()
{
    if (data.size() > 0)
    {
        std::sort(data.begin(), data.end(), CompareIdentifier);
        CalculateTotals();
    }
}

bool ImprovedBank::PagedData::IsEmpty() const
{
    return data.empty();
}

const ImprovedBank::BaseIdentifier* ImprovedBank::PagedData::FindIdentifierById(uint32 id) const
{
    std::vector<BaseIdentifier*>::const_iterator citer = std::find_if(data.begin(), data.end(), [&](const BaseIdentifier* idnt) { return idnt->id == id; });
    if (citer != data.end())
        return *citer;
    return nullptr;
}

void ImprovedBank::NoPagedData(Player* player, const PagedData& pagedData) const
{
    AddGossipItemFor(player, GOSSIP_ICON_CHAT, "|cffb50505NOTHING ON THIS PAGE, GO BACK|r", GOSSIP_SENDER_MAIN, GOSSIP_ACTION_INFO_DEF);
    AddGossipItemFor(player, GOSSIP_ICON_CHAT, "<- [Back]", GOSSIP_SENDER_MAIN, GOSSIP_ACTION_INFO_DEF);
}

std::string ImprovedBank::GetItemCharges(const Item* item) const
{
    std::ostringstream oss;
    for (uint8 i = 0; i < MAX_ITEM_PROTO_SPELLS; ++i)
        oss << item->GetSpellCharges(i) << ' ';
    return oss.str();
}

std::string ImprovedBank::GetItemEnchantments(const Item* item) const
{
    std::ostringstream oss;
    for (uint8 i = 0; i < MAX_ENCHANTMENT_SLOT; ++i)
    {
        oss << item->GetEnchantmentId(EnchantmentSlot(i)) << ' ';
        oss << item->GetEnchantmentDuration(EnchantmentSlot(i)) << ' ';
        oss << item->GetEnchantmentCharges(EnchantmentSlot(i)) << ' ';
    }
    return oss.str();
}

void ImprovedBank::AddDepositItemToDatabase(const Player* player, const Item* item) const
{
    CharacterDatabase.Execute("INSERT INTO mod_improved_bank(owner_guid, owner_account, item_entry, item_count, "
            "duration, charges, flags, enchantments, randomPropertyId, durability, deposit_time, creatorGuid, giftCreatorGuid) VALUES ({}, {}, {}, {}, {}, \"{}\", {}, \"{}\", {}, {}, {}, {}, {})",
        player->GetGUID().GetCounter(), player->GetSession()->GetAccountId(), item->GetEntry(), item->GetCount(),
        item->GetUInt32Value(ITEM_FIELD_DURATION), GetItemCharges(item), item->GetUInt32Value(ITEM_FIELD_FLAGS), GetItemEnchantments(item),
        item->GetItemRandomPropertyId(), item->GetUInt32Value(ITEM_FIELD_DURABILITY), (uint32)GameTime::GetGameTime().count(),
        item->GetGuidValue(ITEM_FIELD_CREATOR).GetCounter(), item->GetGuidValue(ITEM_FIELD_GIFTCREATOR).GetCounter());
}

bool ImprovedBank::DepositItem(ObjectGuid itemGuid, Player* player, uint32* count)
{
    Item* item = player->GetItemByGuid(itemGuid);
    if (item == nullptr)
        return false;

    if (item->IsNotEmptyBag())
        return false;

    if (item->HasFlag(ITEM_FIELD_FLAGS, ITEM_FIELD_FLAG_BOP_TRADEABLE))
        item->RemoveFlag(ITEM_FIELD_FLAGS, ITEM_FIELD_FLAG_BOP_TRADEABLE);

    AddDepositItemToDatabase(player, item);

    if (count != nullptr)
        *count += item->GetCount();

    player->DestroyItem(item->GetBagSlot(), item->GetSlot(), true);

    return true;
}

bool ImprovedBank::DepositItem(uint32 id, Player* player, const PagedData& pagedData)
{
    const ItemIdentifier* itemIdentifier = (ItemIdentifier*)pagedData.FindIdentifierById(id);
    if (itemIdentifier == nullptr)
        return false;

    return DepositItem(itemIdentifier->guid, player);
}

void ImprovedBank::BuildWithdrawItemCatalogue(const Player* player)
{
    PagedData& pagedData = GetPagedData(player);
    pagedData.Reset();
    bool categorized = GetCategorizedItemMenuWithdraw();
    pagedData.type = categorized ? PAGED_DATA_TYPE_WITHDRAW_CLASS : PAGED_DATA_TYPE_WITHDRAW_ALL;

    if (!categorized)
        BuildWithdrawItemCatalogue(player, pagedData);
    else
        BuildItemClassesCatalogue(player, pagedData, itemClasses);

    pagedData.SortAndCalculateTotals();
}

void ImprovedBank::BuildWithdrawItemCatalogue(const Player* player, PagedData& pagedData)
{
    pagedData.Reset();

    std::string baseQuery = "select mib.id, mib.owner_guid, mib.item_entry, mib.item_count, ifnull(ch.name, \"CHAR DELETED\") ch_name, duration, charges, flags, "
        "enchantments, randomPropertyId, durability, deposit_time, creatorGuid, giftCreatorGuid from mod_improved_bank mib "
        "left outer join characters ch on mib.owner_guid = ch.guid where owner_account = {}";
    QueryResult result;

    if (GetAccountWide())
        result = CharacterDatabase.Query(baseQuery, player->GetSession()->GetAccountId());
    else
        result = CharacterDatabase.Query(baseQuery + " and owner_guid = {}", player->GetSession()->GetAccountId(), player->GetGUID().GetCounter());

    if (!result)
        return;

    do
    {
        Field* fields = result->Fetch();

        ItemIdentifier* itemIdentifier = new ItemIdentifier();
        itemIdentifier->id = fields[0].Get<uint32>();
        itemIdentifier->entry = fields[2].Get<uint32>();
        const ItemTemplate* itemTemplate = sObjectMgr->GetItemTemplate(itemIdentifier->entry);
        if (!itemTemplate)
            continue;
        if (pagedData.type == PAGED_DATA_TYPE_WITHDRAW_CATEGORIZED)
            if (itemTemplate->Class != pagedData.itemClass || itemTemplate->SubClass != pagedData.itemSubClass)
                continue;
        int32 randomPropertyId = fields[9].Get<int32>();
        itemIdentifier->randomPropertyId = randomPropertyId;
        itemIdentifier->name = ItemNameWithLocale(player, itemTemplate, randomPropertyId);
        itemIdentifier->count = fields[3].Get<uint32>();

        std::ostringstream oss;
        oss << ItemIcon(itemIdentifier->entry);
        oss << ItemLink(player, itemTemplate, randomPropertyId);
        if (itemIdentifier->count > 1)
            oss << " - " << itemIdentifier->count << "x";
        if (GetAccountWide() && player->GetGUID().GetCounter() != fields[1].Get<uint32>())
            oss << " - FROM " << fields[4].Get<std::string>();

        itemIdentifier->depositTime = fields[11].Get<uint32>();

        int32 duration = (int32)fields[5].Get<uint32>();
        if (duration == 0)
            itemIdentifier->duration = 0;
        else
        {
            uint32 diff = GameTime::GetGameTime().count() - itemIdentifier->depositTime;
            itemIdentifier->duration = duration - diff;
            if (itemIdentifier->duration <= 0)
            {
                itemIdentifier->duration = -1;
                oss << " - |cffb50505EXPIRED|r";
            }
        }

        itemIdentifier->uiName = oss.str();

        itemIdentifier->charges = fields[6].Get<std::string>();
        itemIdentifier->flags = fields[7].Get<uint32>();
        itemIdentifier->enchants = fields[8].Get<std::string>();
        itemIdentifier->durability = fields[10].Get<uint32>();
        itemIdentifier->creatorGuid = fields[12].Get<uint32>();
        itemIdentifier->giftCreatorGuid = fields[13].Get<uint32>();

        pagedData.data.push_back(itemIdentifier);
    } while (result->NextRow());

    pagedData.SortAndCalculateTotals();
}

bool ImprovedBank::LoadDataIntoItemFields(Item* item, std::string const& data, uint32 startOffset, uint32 count)
{
    if (data.empty())
        return false;

    std::vector<std::string_view> tokens = Acore::Tokenize(data, ' ', false);

    if (tokens.size() != count)
        return false;

    for (uint32 index = 0; index < count; ++index)
    {
        Optional<uint32> val = Acore::StringTo<uint32>(tokens[index]);
        if (!val)
        {
            return false;
        }

        item->UpdateUInt32Value(startOffset + index, *val);
    }

    return true;
}

Item* ImprovedBank::CreateItem(Player* player, ItemPosCountVec const& dest, uint32 itemEntry, bool update, int32 randomPropertyId,
    uint32 duration, const std::string& charges, uint32 flags, const std::string& enchants, uint32 durability, uint32 creatorGuid, uint32 giftCreatorGuid)
{
    uint32 count = 0;
    for (ItemPosCountVec::const_iterator itr = dest.begin(); itr != dest.end(); ++itr)
        count += itr->count;

    Item* newItem = Item::CreateItem(itemEntry, count, player, false, randomPropertyId);
    if (newItem != nullptr)
    {
        ItemTemplate const* itemTemplate = newItem->GetTemplate();

        newItem->SetGuidValue(ITEM_FIELD_CREATOR, ObjectGuid::Create<HighGuid::Player>(creatorGuid));
        newItem->SetGuidValue(ITEM_FIELD_GIFTCREATOR, ObjectGuid::Create<HighGuid::Player>(giftCreatorGuid));

        newItem->SetUInt32Value(ITEM_FIELD_DURATION, duration);

        std::vector<std::string_view> tokens = Acore::Tokenize(charges, ' ', false);
        if (tokens.size() == MAX_ITEM_PROTO_SPELLS)
        {
            for (uint8 i = 0; i < MAX_ITEM_PROTO_SPELLS; ++i)
            {
                if (Optional<int32> charges = Acore::StringTo<int32>(tokens[i]))
                    newItem->SetSpellCharges(i, *charges);
            }
        }

        newItem->SetUInt32Value(ITEM_FIELD_FLAGS, flags);
        if (newItem->IsSoulBound() && itemTemplate->Bonding == NO_BIND && sScriptMgr->CanApplySoulboundFlag(newItem, itemTemplate))
            newItem->ApplyModFlag(ITEM_FIELD_FLAGS, ITEM_FIELD_FLAG_SOULBOUND, false);

        LoadDataIntoItemFields(newItem, enchants, ITEM_FIELD_ENCHANTMENT_1_1, MAX_ENCHANTMENT_SLOT * MAX_ENCHANTMENT_OFFSET);

        newItem->SetUInt32Value(ITEM_FIELD_DURABILITY, durability);
        if (durability > itemTemplate->MaxDurability && !newItem->HasFlag(ITEM_FIELD_FLAGS, ITEM_FIELD_FLAG_WRAPPED))
            newItem->SetUInt32Value(ITEM_FIELD_DURABILITY, itemTemplate->MaxDurability);

        if (itemTemplate->Quality >= ITEM_QUALITY_RARE)
            player->AdditionalSavingAddMask(ADDITIONAL_SAVING_INVENTORY_AND_GOLD);

        player->ItemAddedQuestCheck(itemEntry, count);
        player->UpdateAchievementCriteria(ACHIEVEMENT_CRITERIA_TYPE_RECEIVE_EPIC_ITEM, itemEntry, count);
        player->UpdateAchievementCriteria(ACHIEVEMENT_CRITERIA_TYPE_OWN_ITEM, itemEntry, count);
        newItem = player->StoreItem(dest, newItem, update);

        sScriptMgr->OnPlayerStoreNewItem(player, newItem, count);
    }
    return newItem;
}

bool ImprovedBank::WithdrawItem(uint32 id, Player* player, PagedData& pagedData)
{
    ItemIdentifier* itemIdentifier = (ItemIdentifier*)pagedData.FindIdentifierById(id);
    if (itemIdentifier == nullptr)
        return false;

    // item expired, just remove it
    if (itemIdentifier->duration == -1)
    {
        RemoveItemFromDatabase(itemIdentifier->id);
        return false;
    }

    // re-check with deposit time if item expired, maybe player did not refresh in the meantime
    if (itemIdentifier->duration > 0)
    {
        uint32 diff = GameTime::GetGameTime().count() - itemIdentifier->depositTime;
        itemIdentifier->duration = itemIdentifier->duration - diff;
        if (itemIdentifier->duration <= 0)
        {
            RemoveItemFromDatabase(itemIdentifier->id);
            return false;
        }
    }

    ItemPosCountVec dest;
    InventoryResult msg = player->CanStoreNewItem(NULL_BAG, NULL_SLOT, dest, itemIdentifier->entry, itemIdentifier->count);
    if (msg == EQUIP_ERR_OK)
    {
        Item* item = CreateItem(player, dest, itemIdentifier->entry, true, itemIdentifier->randomPropertyId, (uint32)itemIdentifier->duration, itemIdentifier->charges,
            itemIdentifier->flags, itemIdentifier->enchants, itemIdentifier->durability, itemIdentifier->creatorGuid, itemIdentifier->giftCreatorGuid);
        player->SendNewItem(item, itemIdentifier->count, true, false);

        RemoveItemFromDatabase(itemIdentifier->id);
        RemoveFromPagedData(itemIdentifier->id, pagedData);
        
        return true;
    }

    return false;
}

void ImprovedBank::RemoveFromPagedData(uint32 id, PagedData& pagedData)
{
    IdentifierContainer::const_iterator citr = std::remove_if(pagedData.data.begin(), pagedData.data.end(), [&](const BaseIdentifier* identifier) { return identifier->id == id; });
    pagedData.data.erase(citr, pagedData.data.end());

    pagedData.CalculateTotals();
}

void ImprovedBank::RemoveItemFromDatabase(uint32 id)
{
    CharacterDatabase.Execute("DELETE FROM mod_improved_bank WHERE id = {}", id);
}

bool ImprovedBank::IsReagent(const Item* item) const
{
    const ItemTemplate* itemTemplate = item->GetTemplate();
    return ((itemTemplate->Class == ITEM_CLASS_TRADE_GOODS && !IsBlacklistedSubclass(itemTemplate->SubClass)) || itemTemplate->Class == ITEM_CLASS_GEM) && itemTemplate->GetMaxStackSize() > 1;
}

void ImprovedBank::DepositAllReagents(Player* player, uint32* totalCount)
{
    *totalCount = 0;

    for (uint8 i = INVENTORY_SLOT_ITEM_START; i < INVENTORY_SLOT_ITEM_END; i++)
        if (Item* item = player->GetItemByPos(INVENTORY_SLOT_BAG_0, i))
            if (IsReagent(item))
                DepositItem(item->GetGUID(), player, totalCount);

    for (uint8 i = INVENTORY_SLOT_BAG_START; i < INVENTORY_SLOT_BAG_END; i++)
        if (Bag* bag = player->GetBagByPos(i))
            for (uint32 j = 0; j < bag->GetBagSize(); j++)
                if (Item* item = player->GetItemByPos(i, j))
                    if (IsReagent(item))
                        DepositItem(item->GetGUID(), player, totalCount);

    if (GetDepositReagentsSearchBank())
    {
        for (uint8 i = BANK_SLOT_ITEM_START; i < BANK_SLOT_ITEM_END; i++)
            if (Item* item = player->GetItemByPos(INVENTORY_SLOT_BAG_0, i))
                if (IsReagent(item))
                    DepositItem(item->GetGUID(), player, totalCount);

        for (uint8 i = BANK_SLOT_BAG_START; i < BANK_SLOT_BAG_END; i++)
            if (Bag* bag = player->GetBagByPos(i))
                for (uint32 j = 0; j < bag->GetBagSize(); j++)
                    if (Item* item = player->GetItemByPos(i, j))
                        if (IsReagent(item))
                            DepositItem(item->GetGUID(), player, totalCount);
    }
}

ImprovedBank::PagedData& ImprovedBank::GetPagedData(const Player* player)
{
    return playerPagedData[player->GetGUID().GetCounter()];
}

bool ImprovedBank::_AddPagedData(Player* player, const PagedData& pagedData, uint32 page) const
{
    const IdentifierContainer& data = pagedData.data;
    if (data.size() == 0 || (page + 1) > pagedData.totalPages)
        return false;

    uint32 lowIndex = page * PagedData::PAGE_SIZE;
    if (data.size() <= lowIndex)
        return false;

    uint32 highIndex = lowIndex + PagedData::PAGE_SIZE - 1;
    if (highIndex >= data.size())
        highIndex = data.size() - 1;

    for (uint32 i = lowIndex; i <= highIndex; i++)
    {
        const BaseIdentifier* identifier = data[i];
        if (pagedData.type == PAGED_DATA_TYPE_DEPOSIT_ALL || pagedData.type == PAGED_DATA_TYPE_WITHDRAW_ALL
            || pagedData.type == PAGED_DATA_TYPE_DEPOSIT_CATEGORIZED || pagedData.type == PAGED_DATA_TYPE_WITHDRAW_CATEGORIZED)
        {
            const ItemIdentifier* itemIdentifier = (ItemIdentifier*)identifier;
            if (itemIdentifier->tradeable)
                AddGossipItemFor(player, GOSSIP_ICON_MONEY_BAG, itemIdentifier->uiName, GOSSIP_SENDER_MAIN + 1, GOSSIP_ACTION_INFO_DEF + itemIdentifier->id, "Item is eligible for BOP trade. Depositing it will invalidate this!", 0, false);
            else if (itemIdentifier->duration > 0)
                AddGossipItemFor(player, GOSSIP_ICON_MONEY_BAG, itemIdentifier->uiName, GOSSIP_SENDER_MAIN + 1, GOSSIP_ACTION_INFO_DEF + itemIdentifier->id, "Item has an expiration time. Timer will still advance while the item is deposited!", 0, false);
            else
                AddGossipItemFor(player, GOSSIP_ICON_MONEY_BAG, itemIdentifier->uiName, GOSSIP_SENDER_MAIN + 1, GOSSIP_ACTION_INFO_DEF + itemIdentifier->id);
        }
        else
            AddGossipItemFor(player, GOSSIP_ICON_VENDOR, identifier->uiName, GOSSIP_SENDER_MAIN + 1, GOSSIP_ACTION_INFO_DEF + identifier->id);
    }

    if (page + 1 < pagedData.totalPages)
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "[Next] ->", GOSSIP_SENDER_MAIN + 2, GOSSIP_ACTION_INFO_DEF + page + 1);

    uint32 pageZeroSender = GOSSIP_SENDER_MAIN;
    if (pagedData.type == PAGED_DATA_TYPE_DEPOSIT_SUBCLASS)
        pageZeroSender += 20;
    else if (pagedData.type == PAGED_DATA_TYPE_DEPOSIT_CATEGORIZED)
        pageZeroSender += 21;
    else if (pagedData.type == PAGED_DATA_TYPE_WITHDRAW_SUBCLASS)
        pageZeroSender += 22;
    else if (pagedData.type == PAGED_DATA_TYPE_WITHDRAW_CATEGORIZED)
        pageZeroSender += 23;

    AddGossipItemFor(player, GOSSIP_ICON_CHAT, "<- [Back]", page == 0 ? pageZeroSender : GOSSIP_SENDER_MAIN + 2, page == 0 ? GOSSIP_ACTION_INFO_DEF : GOSSIP_ACTION_INFO_DEF + page - 1);

    return true;
}

bool ImprovedBank::AddPagedData(Player* player, Creature* creature, uint32 page)
{
    ClearGossipMenuFor(player);
    PagedData& pagedData = GetPagedData(player);
    while (!_AddPagedData(player, pagedData, page))
    {
        if (page == 0)
        {
            NoPagedData(player, pagedData);
            break;
        }
        else
            page--;
    }

    pagedData.currentPage = page;

    SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
    return true;
}

bool ImprovedBank::TakePagedDataAction(Player* player, Creature* creature, uint32 action)
{
    PagedData& pagedData = GetPagedData(player);
    if (pagedData.type == PAGED_DATA_TYPE_DEPOSIT_CLASS || pagedData.type == PAGED_DATA_TYPE_WITHDRAW_CLASS)
    {
        PagedDataType type = pagedData.type == PAGED_DATA_TYPE_DEPOSIT_CLASS ? PAGED_DATA_TYPE_DEPOSIT_SUBCLASS : PAGED_DATA_TYPE_WITHDRAW_SUBCLASS;
        BuildItemSubClassesCatalogue(player, pagedData, type, action);
        return AddPagedData(player, creature, 0);
    }
    else if (pagedData.type == PAGED_DATA_TYPE_DEPOSIT_SUBCLASS)
    {
        BuildItemCatalogueForDeposit(player, pagedData, action);
        return AddPagedData(player, creature, 0);
    }
    else if (pagedData.type == PAGED_DATA_TYPE_DEPOSIT_ALL || pagedData.type == PAGED_DATA_TYPE_DEPOSIT_CATEGORIZED)
    {
        if (!DepositItem(action, player, pagedData))
            ChatHandler(player->GetSession()).SendSysMessage("Could not deposit item. Item might not longer be in inventory.");
        else
        {
            if (pagedData.type == PAGED_DATA_TYPE_DEPOSIT_CATEGORIZED)
                BuildItemCatalogueForDeposit(player, pagedData, pagedData.itemSubClass);
            else
                BuildDepositItemCatalogue(player);
            return AddPagedData(player, creature, pagedData.currentPage);
        }
    }
    else if (pagedData.type == PAGED_DATA_TYPE_WITHDRAW_SUBCLASS)
    {
        BuildItemCatalogueForWithdraw(player, pagedData, action);
        return AddPagedData(player, creature, 0);
    }
    else if (pagedData.type == PAGED_DATA_TYPE_WITHDRAW_ALL || pagedData.type == PAGED_DATA_TYPE_WITHDRAW_CATEGORIZED)
    {
        if (!WithdrawItem(action, player, pagedData))
            ChatHandler(player->GetSession()).SendSysMessage("Could not withdraw item. Possible reasons: item already withdrawn, no space in inventory, unique item already in inventory, item expired.");
        else
            return AddPagedData(player, creature, pagedData.currentPage);
    }

    CloseGossipMenuFor(player);
    return false;
}

const ImprovedBank::ClassifiedItem* ImprovedBank::FindItemClass(uint32 id) const
{
    std::vector<ClassifiedItem>::const_iterator citer = std::find_if(itemClasses.begin(), itemClasses.end(), [&](const ClassifiedItem& item) { return item.id == id; });
    if (citer != itemClasses.end())
        return &*citer;
    return nullptr;
}
