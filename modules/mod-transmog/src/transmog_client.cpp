/*
 * Transmog window companion: the server half of the in-game "Manastorm_Transmog" addon.
 *
 * The addon talks to this module over the addon channel, the same way the other Manastorm client/server
 * pairs do: an addon whisper to oneself, which reaches OnPlayerBeforeSendChatMessage as LANG_ADDON.
 *
 *   client -> server   "TMOGC\t<body>"      server -> client   "TMOGS\t<body>"
 *
 * Fields are separated by ':', lists by ',' and ';'. Messages are capped at 255 bytes by the core, so
 * anything that can grow (the item list, the outfits) is paged or split over several messages.
 *
 * client -> server
 *   HI                         the addon is loaded; answers with I: and an E: dump
 *   ST                         resend the E: dump
 *   L:<slot>:<page>:<search>   one page of the appearances the account owns that fit the slot
 *   SL:<nonce>:<first>:<count>:<search>   a range of the item sets this class can wear, most complete first
 *   A:<slot>:<entry>           transmogrify a slot; entry 0 removes it, 1 (HIDDEN_ITEM_ID) hides it
 *   XA                         remove every transmogrification
 *   OL                         list the saved outfits
 *   OS:<id>:<slot=entry,...>:<name>   save an outfit (charged like the gossip "save set")
 *   OU:<id>                    apply a saved outfit (free, it was paid for when saved)
 *   OD:<id>                    delete a saved outfit
 *   OR:<id>:<name>             rename a saved outfit (free)
 *   OP                         buy one more outfit slot
 *
 * server -> client
 *   OPEN                                  the player talked to a transmogrifier: show the window
 *   I:<hidden>,<sets>,<maxSets>,<setMod%>,<setCopper>,<token>,<tokenEntry>,<tokenAmount>,<hiddenFree>
 *   E:<slot>,<equipped>,<fake>,<cost>;...  one entry per slot (equipped 0 = empty slot)
 *   L:<slot>:<page>:<total>:<id>,<id>,...
 *   SB:<nonce>:<total>                    how many sets match the SL: search
 *   T:<nonce>:<index>:<id>|<owned>|<total>|<name>|<slot=entry,slot/entry,...>   one set; '=' marks a piece the
 *                                         account owns, '/' one it does not
 *   R:<slot>:<code>                       result; code is a TransmogStrings id or one of the OUTFIT_* codes
 *   OB:<maxSets>:<slots>:<slotCost>       start of an outfit list (the client clears its copy); <slots> is how
 *                                         many outfit slots the player owns, <slotCost> the price of the next
 *   O:<id>:<slot=entry,...>:<name>        one saved outfit
 *
 * Fields are only ever appended, never reordered, so an older addon keeps working against a newer server.
 */

#include "Transmogrification.h"
#include "CosmeticsPolicy.h"
#include "Chat.h"
#include "ObjectMgr.h"
#include "ItemTemplate.h"
#include "DBCStores.h"
#include "DatabaseEnv.h"
#include "WorldPacket.h"
#include "ScriptMgr.h"

#include <algorithm>
#include <cctype>
#include <mutex>
#include <set>
#include <sstream>
#include <unordered_map>

#define sT sTransmogrification

namespace
{
    constexpr char const* PREFIX_IN  = "TMOGC\t";
    constexpr char const* PREFIX_OUT = "TMOGS\t";
    constexpr size_t PREFIX_LEN = 6;
    constexpr uint32 ITEMS_PER_PAGE = 20;
    constexpr size_t MAX_BODY = 240;
    constexpr size_t MAX_OUTFIT_NAME = 24;

    // Codes the client shows that are not TransmogStrings ids (those occupy 1..88).
    enum ClientCodes : uint32
    {
        CODE_NO_TRANSMOGRIFIER  = 101,
        CODE_OUTFIT_SAVED       = 102,
        CODE_OUTFIT_FULL        = 103,
        CODE_OUTFIT_BAD_NAME    = 104,
        CODE_OUTFIT_EMPTY       = 105,
        CODE_OUTFIT_DISABLED    = 106,
        CODE_OUTFIT_APPLIED     = 107,
        CODE_OUTFIT_DELETED     = 108,
        CODE_OUTFIT_SLOT_BOUGHT = 109,
        CODE_OUTFIT_SLOTS_MAXED = 110,
        CODE_OUTFIT_RENAMED     = 111,
    };

    std::mutex g_lock;
    std::set<ObjectGuid> g_windowPlayers;

    std::vector<std::string> Split(std::string const& s, char sep, size_t maxParts = 0)
    {
        std::vector<std::string> out;
        size_t start = 0;
        while (true)
        {
            if (maxParts && out.size() + 1 == maxParts)
            {
                out.push_back(s.substr(start));
                break;
            }
            size_t pos = s.find(sep, start);
            if (pos == std::string::npos)
            {
                out.push_back(s.substr(start));
                break;
            }
            out.push_back(s.substr(start, pos - start));
            start = pos + 1;
        }
        return out;
    }

    bool ParseUInt(std::string const& s, uint32& out)
    {
        if (s.empty() || s.size() > 10)
            return false;
        uint64 v = 0;
        for (char c : s)
        {
            if (c < '0' || c > '9')
                return false;
            v = v * 10 + uint32(c - '0');
        }
        if (v > 0xFFFFFFFFull)
            return false;
        out = uint32(v);
        return true;
    }

    bool IsWindowSlot(uint32 slot)
    {
        switch (slot)
        {
            case EQUIPMENT_SLOT_HEAD:
            case EQUIPMENT_SLOT_SHOULDERS:
            case EQUIPMENT_SLOT_BODY:
            case EQUIPMENT_SLOT_CHEST:
            case EQUIPMENT_SLOT_WAIST:
            case EQUIPMENT_SLOT_LEGS:
            case EQUIPMENT_SLOT_FEET:
            case EQUIPMENT_SLOT_WRISTS:
            case EQUIPMENT_SLOT_HANDS:
            case EQUIPMENT_SLOT_BACK:
            case EQUIPMENT_SLOT_MAINHAND:
            case EQUIPMENT_SLOT_OFFHAND:
            case EQUIPMENT_SLOT_RANGED:
            case EQUIPMENT_SLOT_TABARD:
                return true;
            default:
                return false;
        }
    }

    void Send(Player* player, std::string const& body)
    {
        WorldPacket data;
        std::string message = std::string(PREFIX_OUT) + body;
        ChatHandler::BuildChatPacket(data, CHAT_MSG_WHISPER, LANG_ADDON, player, player, message);
        player->SendDirectMessage(&data);
    }

    bool NearTransmogrifier(Player* player)
    {
        if (!sConfigMgr->GetOption<bool>("Transmogrification.Window.RequireNpc", true))
            return true;

        if (player->FindNearestCreature(TMOG_VENDOR_CREATURE_ID, 15.0f))
            return true;
        return sT->PetEntry && player->FindNearestCreature(sT->PetEntry, 15.0f);
    }

    uint32 PriceFor(ItemTemplate const* target)
    {
        uint32 price = sT->GetSpecialPrice(target);
        price *= sT->GetScaledCostModifier();
        price += sT->GetCopperCost();
        return price;
    }

    void SendInfo(Player* player)
    {
        std::ostringstream ss;
        ss << "I:" << (sT->GetAllowHiddenTransmog() ? 1 : 0)
           << ',' << ((sT->GetEnableSets()) ? 1 : 0)
           << ',' << uint32(sT->GetMaxSets())
           << ',' << uint32(sT->GetSetCostModifier() * 100.0f)
           << ',' << uint32(std::max<int32>(sT->GetSetCopperCost(), 0))
           << ',' << (sT->GetRequireToken() ? 1 : 0)
           << ',' << sT->GetTokenEntry()
           << ',' << sT->GetTokenAmount()
           << ',' << (sT->GetHiddenTransmogIsFree() ? 1 : 0);
        Send(player, ss.str());
    }

    // One E: message carries several slots; a slot entry is at most ~24 bytes.
    void SendState(Player* player)
    {
        std::string line;
        auto flush = [&]()
        {
            if (!line.empty())
                Send(player, "E:" + line);
            line.clear();
        };

        for (uint8 slot = EQUIPMENT_SLOT_START; slot < EQUIPMENT_SLOT_END; ++slot)
        {
            if (!IsWindowSlot(slot))
                continue;

            Item* item = player->GetItemByPos(INVENTORY_SLOT_BAG_0, slot);
            uint32 equip = item ? item->GetEntry() : 0;
            uint32 fake = item ? sT->GetFakeEntry(item->GetGUID()) : 0;
            uint32 cost = item ? PriceFor(item->GetTemplate()) : 0;

            std::ostringstream ss;
            ss << uint32(slot) << ',' << equip << ',' << fake << ',' << cost;
            if (!line.empty() && line.size() + ss.str().size() + 1 > MAX_BODY)
                flush();
            if (!line.empty())
                line += ';';
            line += ss.str();
        }
        flush();
    }

    void SendSlot(Player* player, uint8 slot)
    {
        Item* item = player->GetItemByPos(INVENTORY_SLOT_BAG_0, slot);
        std::ostringstream ss;
        ss << "E:" << uint32(slot) << ','
           << (item ? item->GetEntry() : 0) << ','
           << (item ? sT->GetFakeEntry(item->GetGUID()) : 0) << ','
           << (item ? PriceFor(item->GetTemplate()) : 0);
        Send(player, ss.str());
    }

    void SendResult(Player* player, uint32 slot, uint32 code)
    {
        Send(player, "R:" + std::to_string(slot) + ":" + std::to_string(code));
    }

    // Whether the account is allowed to use the appearance of this entry. With the collection system on it
    // is the account's unlocked list; otherwise the item has to be in the player's possession.
    bool OwnsAppearance(Player* player, uint32 entry)
    {
        if (sT->GetUseCollectionSystem())
        {
            auto it = sT->collectionCache.find(player->GetSession()->GetAccountId());
            return it != sT->collectionCache.end() && it->second.count(entry);
        }
        return player->HasItemCount(entry, 1, false);
    }

    void GatherOwnedEntries(Player* player, std::vector<uint32>& out)
    {
        if (sT->GetUseCollectionSystem())
        {
            auto it = sT->collectionCache.find(player->GetSession()->GetAccountId());
            if (it != sT->collectionCache.end())
                out.assign(it->second.begin(), it->second.end());
            return;
        }

        auto add = [&](Item* item)
        {
            if (item)
                out.push_back(item->GetEntry());
        };
        for (uint8 i = INVENTORY_SLOT_ITEM_START; i < INVENTORY_SLOT_ITEM_END; ++i)
            add(player->GetItemByPos(INVENTORY_SLOT_BAG_0, i));
        for (uint8 i = INVENTORY_SLOT_BAG_START; i < INVENTORY_SLOT_BAG_END; ++i)
        {
            Bag* bag = player->GetBagByPos(i);
            if (!bag)
                continue;
            for (uint32 j = 0; j < bag->GetBagSize(); ++j)
                add(player->GetItemByPos(i, j));
        }
        std::sort(out.begin(), out.end());
        out.erase(std::unique(out.begin(), out.end()), out.end());
    }

    std::string LowerCopy(std::string s)
    {
        std::transform(s.begin(), s.end(), s.begin(), [](unsigned char c) { return std::tolower(c); });
        return s;
    }

    // Everything the account owns that can be put on the item in `slot`, best quality first, one entry per
    // visible appearance.
    void BuildCandidates(Player* player, Item* target, std::string const& search, std::vector<ItemTemplate const*>& out)
    {
        std::vector<uint32> owned;
        GatherOwnedEntries(player, owned);

        std::string needle = LowerCopy(search);
        int locIndex = player->GetSession()->GetSessionDbLocaleIndex();

        ItemTemplate const* targetProto = target->GetTemplate();
        for (uint32 id : owned)
        {
            ItemTemplate const* proto = sObjectMgr->GetItemTemplate(id);
            if (!proto || !sT->CanTransmogrifyItemWithItem(player, targetProto, proto))
                continue;

            if (!needle.empty())
            {
                std::string name = proto->Name1;
                if (ItemLocale const* il = sObjectMgr->GetItemLocale(id))
                    ObjectMgr::GetLocaleString(il->Name, locIndex, name);
                if (LowerCopy(name).find(needle) == std::string::npos)
                    continue;
            }
            out.push_back(proto);
        }

        std::sort(out.begin(), out.end(), [](ItemTemplate const* a, ItemTemplate const* b)
        {
            if (a->Quality != b->Quality)
                return a->Quality > b->Quality;
            if (a->Name1 != b->Name1)
                return a->Name1 < b->Name1;
            return a->ItemId < b->ItemId;
        });

        std::set<uint32> seenDisplay;
        std::vector<ItemTemplate const*> unique;
        unique.reserve(out.size());
        for (ItemTemplate const* proto : out)
            if (seenDisplay.insert(proto->DisplayInfoID).second)
                unique.push_back(proto);
        out.swap(unique);
    }

    void HandleList(Player* player, std::vector<std::string> const& args)
    {
        uint32 slot = 0, page = 0;
        if (args.size() < 3 || !ParseUInt(args[1], slot) || !ParseUInt(args[2], page) || !IsWindowSlot(slot))
            return;

        std::string search = args.size() > 3 ? args[3] : "";
        if (search.size() > MAX_SEARCH_STRING_LENGTH)
            search.resize(MAX_SEARCH_STRING_LENGTH);

        std::vector<ItemTemplate const*> list;
        if (Item* target = player->GetItemByPos(INVENTORY_SLOT_BAG_0, slot))
            BuildCandidates(player, target, search, list);

        std::ostringstream ss;
        ss << "L:" << slot << ':' << page << ':' << list.size() << ':';
        size_t first = size_t(page) * ITEMS_PER_PAGE;
        for (size_t i = first; i < list.size() && i < first + ITEMS_PER_PAGE; ++i)
        {
            if (i != first)
                ss << ',';
            ss << list[i]->ItemId;
        }
        Send(player, ss.str());
    }

    // Debug: tells the player in chat why an owned appearance is missing from the list for `slot`.
    void HandleWhy(Player* player, std::vector<std::string> const& args)
    {
        uint32 slot = 0, entry = 0;
        if (args.size() < 3 || !ParseUInt(args[1], slot) || !ParseUInt(args[2], entry) || !IsWindowSlot(slot))
            return;

        ChatHandler chat(player->GetSession());
        ItemTemplate const* proto = sObjectMgr->GetItemTemplate(entry);
        Item* target = player->GetItemByPos(INVENTORY_SLOT_BAG_0, slot);
        if (!proto)
            return chat.PSendSysMessage("why {}: no such item", entry);
        if (!target)
            return chat.PSendSysMessage("why {}: nothing is equipped in slot {}", entry, slot);

        ItemTemplate const* t = target->GetTemplate();
        chat.PSendSysMessage("why {}: owned={} suitable={} (class mask {}, race mask {}, level {}, quality {}) same item={} same display={} "
            "class {}/{} subclass {}/{} invtype {}/{} -> allowed={}",
            entry, OwnsAppearance(player, entry), sT->SuitableForTransmogrification(player, proto),
            proto->AllowableClass, proto->AllowableRace, proto->RequiredLevel, proto->Quality,
            entry == t->ItemId, proto->DisplayInfoID == t->DisplayInfoID,
            proto->Class, t->Class, proto->SubClass, t->SubClass, proto->InventoryType, t->InventoryType,
            sT->CanTransmogrifyItemWithItem(player, t, proto));
    }

    // The equipment slot a set piece goes in, or -1 for what cannot be transmogrified (rings, trinkets, neck).
    int32 PieceSlot(ItemTemplate const* proto)
    {
        switch (proto->InventoryType)
        {
            case INVTYPE_HEAD:            return EQUIPMENT_SLOT_HEAD;
            case INVTYPE_SHOULDERS:       return EQUIPMENT_SLOT_SHOULDERS;
            case INVTYPE_BODY:            return EQUIPMENT_SLOT_BODY;
            case INVTYPE_CHEST:
            case INVTYPE_ROBE:            return EQUIPMENT_SLOT_CHEST;
            case INVTYPE_WAIST:           return EQUIPMENT_SLOT_WAIST;
            case INVTYPE_LEGS:            return EQUIPMENT_SLOT_LEGS;
            case INVTYPE_FEET:            return EQUIPMENT_SLOT_FEET;
            case INVTYPE_WRISTS:          return EQUIPMENT_SLOT_WRISTS;
            case INVTYPE_HANDS:           return EQUIPMENT_SLOT_HANDS;
            case INVTYPE_CLOAK:           return EQUIPMENT_SLOT_BACK;
            case INVTYPE_WEAPON:
            case INVTYPE_2HWEAPON:
            case INVTYPE_WEAPONMAINHAND:  return EQUIPMENT_SLOT_MAINHAND;
            case INVTYPE_SHIELD:
            case INVTYPE_HOLDABLE:
            case INVTYPE_WEAPONOFFHAND:   return EQUIPMENT_SLOT_OFFHAND;
            case INVTYPE_RANGED:
            case INVTYPE_THROWN:
            case INVTYPE_RANGEDRIGHT:     return EQUIPMENT_SLOT_RANGED;
            default:                      return -1;
        }
    }

    // The armor type the class wears (cloth 1, leather 2, mail 3, plate 4): transmog only swaps like for like.
    uint32 ArmorTypeOf(Player* player)
    {
        switch (player->getClass())
        {
            case CLASS_WARRIOR:
            case CLASS_PALADIN:
            case CLASS_DEATH_KNIGHT: return ITEM_SUBCLASS_ARMOR_PLATE;
            case CLASS_HUNTER:
            case CLASS_SHAMAN:       return ITEM_SUBCLASS_ARMOR_MAIL;
            case CLASS_ROGUE:
            case CLASS_DRUID:        return ITEM_SUBCLASS_ARMOR_LEATHER;
            default:                 return ITEM_SUBCLASS_ARMOR_CLOTH;
        }
    }

    struct SetRow
    {
        uint32 id = 0;
        uint32 owned = 0;
        uint32 total = 0;
        std::string name;
        std::string pieces; // slot=entry for a piece the account owns, slot/entry for one it does not
    };

    std::string CleanText(char const* text, size_t cap)
    {
        std::string out;
        for (; text && *text && out.size() < cap; ++text)
            out.push_back((*text == ':' || *text == ',' || *text == '|' || *text == ';' || *text == '=' || *text == '/') ? ' ' : *text);
        return out;
    }

    // Every item set that holds something this class can wear, with how many of its pieces the account owns,
    // most complete first.
    void BuildSets(Player* player, std::string const& search, std::vector<SetRow>& out)
    {
        std::string needle = LowerCopy(search);
        uint32 armorType = ArmorTypeOf(player);
        uint32 classMask = player->getClassMask();
        LocaleConstant loc = player->GetSession()->GetSessionDbcLocale();

        for (uint32 i = 0; i < sItemSetStore.GetNumRows(); ++i)
        {
            ItemSetEntry const* set = sItemSetStore.LookupEntry(i);
            if (!set)
                continue;

            SetRow row;
            row.id = i; // the DBC keys a set by its row
            char const* name = set->name[loc];
            if (!name || !*name)
                name = set->name[LOCALE_enUS];
            row.name = CleanText(name, 40);

            bool wearable = false;
            for (uint32 n = 0; n < MAX_ITEM_SET_ITEMS; ++n)
            {
                uint32 entry = set->itemId[n];
                if (!entry)
                    continue;
                ItemTemplate const* proto = sObjectMgr->GetItemTemplate(entry);
                int32 slot = proto ? PieceSlot(proto) : -1;
                if (slot < 0)
                    continue;

                // AllowableClass is signed: 0 and -1 both mean every class
                bool classOk = proto->AllowableClass <= 0 || (uint32(proto->AllowableClass) & classMask) != 0;
                if (classOk && proto->Class == ITEM_CLASS_ARMOR && proto->InventoryType != INVTYPE_CLOAK && proto->SubClass == armorType)
                    wearable = true;

                bool owned = OwnsAppearance(player, entry);
                ++row.total;
                if (owned)
                    ++row.owned;
                if (!row.pieces.empty())
                    row.pieces += ',';
                row.pieces += std::to_string(slot) + (owned ? '=' : '/') + std::to_string(entry);
            }

            if (!wearable || row.name.empty() || (!needle.empty() && LowerCopy(row.name).find(needle) == std::string::npos))
                continue;
            out.push_back(std::move(row));
        }

        std::sort(out.begin(), out.end(), [](SetRow const& a, SetRow const& b)
        {
            if (a.owned != b.owned)
                return a.owned > b.owned;
            if (a.name != b.name)
                return a.name < b.name;
            return a.id < b.id;
        });
    }

    // SL:<nonce>:<first>:<count>:<search>  ->  SB:<nonce>:<total>, then one T: per set in the range
    void HandleSetList(Player* player, std::string const& body)
    {
        std::vector<std::string> args = Split(body, ':', 5);
        uint32 nonce = 0, first = 0, count = 0;
        if (args.size() < 4 || !ParseUInt(args[1], nonce) || !ParseUInt(args[2], first) || !ParseUInt(args[3], count))
            return;
        count = std::min<uint32>(count, 24);

        std::string search = args.size() > 4 ? args[4] : "";
        if (search.size() > MAX_SEARCH_STRING_LENGTH)
            search.resize(MAX_SEARCH_STRING_LENGTH);

        std::vector<SetRow> sets;
        BuildSets(player, search, sets);

        Send(player, "SB:" + std::to_string(nonce) + ":" + std::to_string(sets.size()));
        for (size_t i = first; i < sets.size() && i < size_t(first) + count; ++i)
        {
            SetRow const& s = sets[i];
            std::ostringstream ss;
            ss << "T:" << nonce << ':' << i << ':' << s.id << '|' << s.owned << '|' << s.total << '|' << s.name << '|' << s.pieces;
            Send(player, ss.str());
        }
    }

    void HandleApply(Player* player, std::vector<std::string> const& args, bool cosmetics = false)
    {
        uint32 slot = 0, entry = 0;
        if (args.size() < 3 || !ParseUInt(args[1], slot) || !ParseUInt(args[2], entry) || !IsWindowSlot(slot))
            return;

        Item* target = player->GetItemByPos(INVENTORY_SLOT_BAG_0, slot);
        bool const backpack = slot == EQUIPMENT_SLOT_BACK &&
            IsEsteriaBackpackAppearance(entry ? entry : target ? sT->GetFakeEntry(target->GetGUID()) : 0);
        if (cosmetics && !EsteriaCosmetics::CanApplyBackpack(backpack, !entry || OwnsAppearance(player, entry),
            target && target->GetTemplate()->InventoryType == INVTYPE_CLOAK, player->IsAlive(), player->IsInCombat()))
        {
            SendResult(player, slot, LANG_TRANSMOG_INVALID_ITEMS);
            return;
        }

        if (!NearTransmogrifier(player) && !(cosmetics && backpack))
        {
            SendResult(player, slot, CODE_NO_TRANSMOGRIFIER);
            return;
        }

        if (!target)
        {
            SendResult(player, slot, LANG_TRANSMOG_MISSING_DEST_ITEM);
            return;
        }

        TransmogStrings res = LANG_TRANSMOG_OK;
        if (entry == 0)
        {
            if (sT->GetFakeEntry(target->GetGUID()))
            {
                sT->DeleteFakeEntry(player, slot, target);
                res = LANG_TRANSMOG_UNTRANSMOG_OK;
            }
            else
                res = LANG_TRANSMOG_UNTRANSMOG_NO_TRANSMOGS;
        }
        else if (entry == HIDDEN_ITEM_ID)
        {
            res = sT->GetAllowHiddenTransmog() ? sT->Transmogrify(player, uint32(UINT_MAX), uint8(slot)) : LANG_TRANSMOG_INVALID_ITEMS;
        }
        else if (!OwnsAppearance(player, entry) || !sObjectMgr->GetItemTemplate(entry))
        {
            res = LANG_TRANSMOG_MISSING_SRC_ITEM;
        }
        else if (Item* source = Item::CreateItem(entry, 1, 0))
        {
            res = sT->Transmogrify(player, source, uint8(slot), false, false);
            delete source;
        }
        else
            res = LANG_TRANSMOG_MISSING_SRC_ITEM;

        SendResult(player, slot, res);
        SendSlot(player, uint8(slot));
    }

    void HandleRemoveAll(Player* player)
    {
        if (!NearTransmogrifier(player))
        {
            SendResult(player, 255, CODE_NO_TRANSMOGRIFIER);
            return;
        }

        bool removed = false;
        auto trans = CharacterDatabase.BeginTransaction();
        for (uint8 slot = EQUIPMENT_SLOT_START; slot < EQUIPMENT_SLOT_END; ++slot)
        {
            Item* item = player->GetItemByPos(INVENTORY_SLOT_BAG_0, slot);
            if (!item || !sT->GetFakeEntry(item->GetGUID()))
                continue;
            sT->DeleteFakeEntry(player, slot, item, &trans);
            removed = true;
        }
        if (removed)
            CharacterDatabase.CommitTransaction(trans);

        SendResult(player, 255, removed ? LANG_TRANSMOG_UNTRANSMOG_OK : LANG_TRANSMOG_UNTRANSMOG_NO_TRANSMOGS);
        SendState(player);
    }

#ifdef PRESETS
    void SendOutfit(Player* player, uint8 id)
    {
        auto const& slots = sT->presetById[player->GetGUID()][id];
        std::ostringstream ss;
        ss << "O:" << uint32(id) << ':';
        bool first = true;
        for (auto const& kv : slots)
        {
            if (!first)
                ss << ',';
            first = false;
            ss << uint32(kv.first) << '=' << kv.second;
        }
        ss << ':' << sT->presetByName[player->GetGUID()][id];
        Send(player, ss.str());
    }

    // Outfit slots: a few come free, the rest are bought one at a time, up to MaxSets.
    // The slots a character has bought live in their own table, not in the core's player settings: those are
    // only saved when EnablePlayerSettings is on, and it is off by default.
    std::unordered_map<ObjectGuid::LowType, uint32>& OutfitSlotsCache()
    {
        static std::unordered_map<ObjectGuid::LowType, uint32> cache;
        return cache;
    }

    uint32 OutfitSlotsBought(Player* player)
    {
        ObjectGuid::LowType guid = player->GetGUID().GetCounter();
        auto& cache = OutfitSlotsCache();
        auto it = cache.find(guid);
        if (it != cache.end())
            return it->second;

        uint32 bought = 0;
        if (QueryResult result = CharacterDatabase.Query("SELECT `Bought` FROM `custom_transmogrification_outfit_slots` WHERE `Owner` = {}", guid))
            bought = (*result)[0].Get<uint32>();
        cache[guid] = bought;
        return bought;
    }

    void SetOutfitSlotsBought(Player* player, uint32 bought)
    {
        ObjectGuid::LowType guid = player->GetGUID().GetCounter();
        CharacterDatabase.Execute("REPLACE INTO `custom_transmogrification_outfit_slots` (`Owner`, `Bought`) VALUES ({}, {})", guid, bought);
        OutfitSlotsCache()[guid] = bought;
    }

    uint32 OutfitSlotCount(Player* player)
    {
        uint32 free = sConfigMgr->GetOption<uint32>("Transmogrification.Window.FreeOutfitSlots", 2);
        return std::min<uint32>(sT->GetMaxSets(), free + OutfitSlotsBought(player));
    }

    uint32 OutfitSlotCost()
    {
        return sConfigMgr->GetOption<uint32>("Transmogrification.Window.OutfitSlotCost", 2500000); // 250 gold
    }

    void SendOutfits(Player* player)
    {
        Send(player, "OB:" + std::to_string(uint32(sT->GetMaxSets())) + ":" + std::to_string(OutfitSlotCount(player)) + ":" + std::to_string(OutfitSlotCost()));
        if (!sT->GetEnableSets())
            return;
        std::vector<uint8> ids;
        for (auto const& kv : sT->presetByName[player->GetGUID()])
            ids.push_back(kv.first);
        for (uint8 id : ids)
            SendOutfit(player, id);
    }

    bool CleanOutfitName(std::string& name)
    {
        std::string clean;
        for (unsigned char c : name)
        {
            if (c < 0x20 || c == '"' || c == '\\' || c == ':' || c == 0x7F)
                return false;
            clean.push_back(char(c));
        }
        // trim
        size_t b = clean.find_first_not_of(' ');
        if (b == std::string::npos)
            return false;
        clean = clean.substr(b, clean.find_last_not_of(' ') - b + 1);
        if (clean.size() > MAX_OUTFIT_NAME)
            clean.resize(MAX_OUTFIT_NAME);
        name = clean;
        return !name.empty();
    }

    void HandleOutfitSave(Player* player, std::string const& body)
    {
        // OS:<id>:<slot=entry,...>:<name>
        std::vector<std::string> args = Split(body, ':', 4);
        uint32 id = 0;
        if (args.size() < 4 || !ParseUInt(args[1], id))
            return;

        if (!sT->GetEnableSets())
        {
            SendResult(player, 255, CODE_OUTFIT_DISABLED);
            return;
        }
        if (!NearTransmogrifier(player))
        {
            SendResult(player, 255, CODE_NO_TRANSMOGRIFIER);
            return;
        }
        if (id >= OutfitSlotCount(player))
        {
            SendResult(player, 255, CODE_OUTFIT_FULL);
            return;
        }

        std::string name = args[3];
        if (!CleanOutfitName(name))
        {
            SendResult(player, 255, CODE_OUTFIT_BAD_NAME);
            return;
        }

        std::map<uint8, uint32> items;
        uint32 cost = 0;
        for (std::string const& pair : Split(args[2], ','))
        {
            std::vector<std::string> kv = Split(pair, '=');
            uint32 slot = 0, entry = 0;
            if (kv.size() != 2 || !ParseUInt(kv[0], slot) || !ParseUInt(kv[1], entry) || !IsWindowSlot(slot))
                continue;

            Item* target = player->GetItemByPos(INVENTORY_SLOT_BAG_0, slot);
            if (!target)
                continue;

            if (entry == HIDDEN_ITEM_ID)
            {
                if (!sT->GetAllowHiddenTransmog())
                    continue;
            }
            else
            {
                ItemTemplate const* proto = sObjectMgr->GetItemTemplate(entry);
                if (!proto || !OwnsAppearance(player, entry) || !sT->CanTransmogrifyItemWithItem(player, target->GetTemplate(), proto))
                    continue;
                cost += sT->GetSpecialPrice(proto);
            }
            items[uint8(slot)] = entry;
        }

        if (items.empty())
        {
            SendResult(player, 255, CODE_OUTFIT_EMPTY);
            return;
        }

        cost = uint32(cost * sT->GetSetCostModifier()) + uint32(std::max<int32>(sT->GetSetCopperCost(), 0));
        if (!player->HasEnoughMoney(cost))
        {
            SendResult(player, 255, LANG_TRANSMOG_NOT_ENOUGH_MONEY);
            return;
        }

        std::ostringstream data;
        auto& slots = sT->presetById[player->GetGUID()][uint8(id)];
        slots.clear();
        for (auto const& kv : items)
        {
            data << uint32(kv.first) << ' ' << kv.second << ' ';
            slots[kv.first] = kv.second;
        }
        sT->presetByName[player->GetGUID()][uint8(id)] = name;
        CharacterDatabase.Execute("REPLACE INTO `custom_transmogrification_sets` (`Owner`, `PresetID`, `SetName`, `SetData`) VALUES ({}, {}, \"{}\", \"{}\")",
            player->GetGUID().GetCounter(), id, name, data.str());
        if (cost)
            player->ModifyMoney(-int32(cost));

        SendResult(player, 255, CODE_OUTFIT_SAVED);
        SendOutfits(player);
    }

    void HandleOutfitUse(Player* player, uint32 id)
    {
        if (!sT->GetEnableSets())
            return;
        if (!NearTransmogrifier(player))
        {
            SendResult(player, 255, CODE_NO_TRANSMOGRIFIER);
            return;
        }
        auto const& all = sT->presetById[player->GetGUID()];
        auto it = all.find(uint8(id));
        if (it == all.end())
            return;

        for (auto const& kv : it->second)
            if (Item* item = player->GetItemByPos(INVENTORY_SLOT_BAG_0, kv.first))
                sT->PresetTransmog(player, item, kv.second, kv.first);

        SendResult(player, 255, CODE_OUTFIT_APPLIED);
        SendState(player);
    }

    void HandleOutfitSlotPurchase(Player* player)
    {
        if (!sT->GetEnableSets())
        {
            SendResult(player, 255, CODE_OUTFIT_DISABLED);
            return;
        }
        if (!NearTransmogrifier(player))
        {
            SendResult(player, 255, CODE_NO_TRANSMOGRIFIER);
            return;
        }
        if (OutfitSlotCount(player) >= sT->GetMaxSets())
        {
            SendResult(player, 255, CODE_OUTFIT_SLOTS_MAXED);
            return;
        }

        uint32 cost = OutfitSlotCost();
        if (!player->HasEnoughMoney(cost))
        {
            SendResult(player, 255, LANG_TRANSMOG_NOT_ENOUGH_MONEY);
            return;
        }

        player->ModifyMoney(-int32(cost));
        SetOutfitSlotsBought(player, OutfitSlotsBought(player) + 1);
        SendResult(player, 255, CODE_OUTFIT_SLOT_BOUGHT);
        SendOutfits(player);
    }

    void HandleOutfitRename(Player* player, std::string const& body)
    {
        // OR:<id>:<name>
        std::vector<std::string> args = Split(body, ':', 3);
        uint32 id = 0;
        if (args.size() < 3 || !ParseUInt(args[1], id) || id >= 255 || !sT->GetEnableSets())
            return;

        auto& names = sT->presetByName[player->GetGUID()];
        auto it = names.find(uint8(id));
        if (it == names.end())
            return;

        std::string name = args[2];
        if (!CleanOutfitName(name))
        {
            SendResult(player, 255, CODE_OUTFIT_BAD_NAME);
            return;
        }

        it->second = name;
        CharacterDatabase.Execute("UPDATE `custom_transmogrification_sets` SET `SetName` = \"{}\" WHERE `Owner` = {} AND `PresetID` = {}",
            name, player->GetGUID().GetCounter(), id);
        SendResult(player, 255, CODE_OUTFIT_RENAMED);
        SendOutfits(player);
    }

    void HandleOutfitDelete(Player* player, uint32 id)
    {
        if (!sT->GetEnableSets() || id >= 255)
            return;
        CharacterDatabase.Execute("DELETE FROM `custom_transmogrification_sets` WHERE Owner = {} AND PresetID = {}", player->GetGUID().GetCounter(), id);
        sT->presetById[player->GetGUID()].erase(uint8(id));
        sT->presetByName[player->GetGUID()].erase(uint8(id));
        SendResult(player, 255, CODE_OUTFIT_DELETED);
        SendOutfits(player);
    }
#endif

    void HandleMessage(Player* player, std::string const& body)
    {
        if (!sT->IsEnabled())
            return;

        std::vector<std::string> args = Split(body, ':', 4);
        std::string const& cmd = args[0];

        if (cmd == "HI")
        {
            {
                std::lock_guard<std::mutex> guard(g_lock);
                g_windowPlayers.insert(player->GetGUID());
            }
            SendInfo(player);
            SendState(player);
#ifdef PRESETS
            SendOutfits(player);
#endif
        }
        else if (cmd == "ST")
            SendState(player);
        else if (cmd == "L")
            HandleList(player, args);
        else if (cmd == "SL")
            HandleSetList(player, body);
        else if (cmd == "Y")
            HandleWhy(player, args);
        else if (cmd == "A")
            HandleApply(player, args);
        else if (cmd == "XA")
            HandleRemoveAll(player);
#ifdef PRESETS
        else if (cmd == "OL")
            SendOutfits(player);
        else if (cmd == "OS")
            HandleOutfitSave(player, body);
        else if (cmd == "OP")
            HandleOutfitSlotPurchase(player);
        else if (cmd == "OR")
            HandleOutfitRename(player, body);
        else if (cmd == "OU" || cmd == "OD")
        {
            uint32 id = 0;
            if (args.size() < 2 || !ParseUInt(args[1], id))
                return;
            if (cmd == "OU")
                HandleOutfitUse(player, id);
            else
                HandleOutfitDelete(player, id);
        }
#endif
    }

    class TransmogClientPlayerScript : public PlayerScript
    {
    public:
        TransmogClientPlayerScript() : PlayerScript("TransmogClientPlayerScript", {
            PLAYERHOOK_ON_BEFORE_SEND_CHAT_MESSAGE,
            PLAYERHOOK_ON_LOGOUT
        }) { }

        void OnPlayerBeforeSendChatMessage(Player* player, uint32& /*type*/, uint32& lang, std::string& msg) override
        {
            if (!player || lang != LANG_ADDON || msg.size() <= PREFIX_LEN || msg.compare(0, PREFIX_LEN, PREFIX_IN) != 0)
                return;
            HandleMessage(player, msg.substr(PREFIX_LEN));
        }

        void OnPlayerLogout(Player* player) override
        {
            std::lock_guard<std::mutex> guard(g_lock);
            g_windowPlayers.erase(player->GetGUID());
        }
    };
}

// Called from the transmogrifier's gossip hello. When the player's client has the window, it is opened in
// place of the gossip menu and the caller must not send one.
bool TransmogClient_TryOpenWindow(Player* player)
{
    if (!sConfigMgr->GetOption<bool>("Transmogrification.Window.OpenOnNpc", true))
        return false;

    {
        std::lock_guard<std::mutex> guard(g_lock);
        if (!g_windowPlayers.count(player->GetGUID()))
            return false;
    }

    Send(player, "OPEN");
    SendState(player);
    return true;
}

void AddSC_transmog_client()
{
    new TransmogClientPlayerScript();
}

void TransmogClient_ApplyAppearance(Player* player, uint8 slot, uint32 entry)
{
    if (player && sT->IsEnabled())
        HandleApply(player, {"A", std::to_string(slot), std::to_string(entry)}, true);
}
