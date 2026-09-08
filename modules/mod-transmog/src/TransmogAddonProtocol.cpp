#include "Transmog.h"
#include "TransmogAddonProtocol.h"
#include "ScriptMgr.h"
#include "Chat.h"
#include "Player.h"
#include "WorldSession.h"
#include "Util.h"
#include "Tokenize.h"
#include <sstream>
#include <vector>
#include <string>
#include <string_view>
#include <cstdlib>
#include <algorithm>

// ==========================================
// TRANSMOG ADDON PROTOCOL
// ==========================================
//
// This file replaces the CMaNGOS gossip-menu-free command channel with
// its AzerothCore equivalent. It does NOT reimplement any transmogrification
// logic -- every handler below is a thin translation shim that calls into
// the existing mod-transmog-plus backend (Transmog.h / TransmogRules*.cpp)
// and formats the reply using the exact same message vocabulary the
// original CMaNGOS "Transmog" client addon already understands
// (TransmogStatus, AvailableTransmogs, ApplyTransmogResult, Open).
//
// Transport differences from CMaNGOS:
//   - CMaNGOS: client -> server via a fake ".transmog <cmd>" chat command
//              intercepted by a bespoke Module chat-command dispatcher;
//              server -> client via a CHAT_MSG_WHISPER packet tagged
//              LANG_ADDON (a disguise, because the framework had no real
//              addon-message channel).
//   - AzerothCore (this file): both directions use the real WoW addon
//     message channel (LANG_ADDON), sent as a self-targeted WHISPER, which
//     is the standard, supported way to run a private client<->server
//     channel on this core (the exact same BuildChatPacket(..., CHAT_MSG_WHISPER,
//     LANG_ADDON, player, player, msg) idiom AzerothCore itself uses
//     elsewhere for addon echo, and the same raw-packet approach documented
//     for server-initiated addon pushes).
//
// Wire format (both directions): "transmog\t<payload>" where <payload> is
// identical to the strings the CMaNGOS addon already parses/emits.

namespace TransmogAddon
{
    constexpr size_t MAX_IDS_PER_CHUNK = 20; // keeps each packet well under the ~255 byte addon-message limit

    // ==========================================
    // LOW-LEVEL SEND
    // ==========================================

    void SendToClient(Player* player, std::string const& payload)
    {
        if (!player || !player->GetSession())
            return;

        std::string full = std::string(PREFIX) + "\t" + payload;

        WorldPacket data;
        ChatHandler::BuildChatPacket(data, CHAT_MSG_WHISPER, LANG_ADDON, player, player, full);
        player->GetSession()->SendPacket(&data);
    }

    // ==========================================
    // OUTBOUND MESSAGE BUILDERS
    // ==========================================

    // "Open" -- tells the addon this gossip interaction belongs to the
    // transmog NPC and it should take over the frame instead of the
    // hardcoded NPC-name check the original addon used.
    void SendOpen(Player* player)
    {
        SendToClient(player, "Open");
    }

    // "TransmogStatus:<amount>:<slot>,<itemEntry>:..."  /  "TransmogStatus:0"
    void SendStatus(Player* player)
    {
        std::ostringstream out;
        uint32 count = 0;
        for (uint8 slot = EQUIPMENT_SLOT_START; slot < EQUIPMENT_SLOT_END; ++slot)
        {
            uint32 fakeEntry = sTransmog->GetSlotAppearance(player->GetGUID(), slot);
            if (fakeEntry == 0)
                continue;

            out << ":" << uint32(slot) << "," << fakeEntry;
            ++count;
        }

        if (count == 0)
        {
            SendToClient(player, "TransmogStatus:0");
            return;
        }

        SendToClient(player, "TransmogStatus:" + std::to_string(count) + out.str());
    }

    // "AvailableTransmogs:<slot>:<bucket>:<amount>:<total>:start"
    // "AvailableTransmogs:<slot>:<bucket>:<amount>:<total>:<id1>:<id2>:..."   (chunked)
    // "AvailableTransmogs:<slot>:<bucket>:<amount>:<total>:end"
    //
    // The bucket MUST equal what the addon independently computes for the
    // currently equipped item in that slot: Transmog.currentTransmogItemClass
    // = ItemClassStrToNum(itemClass) + ItemSubclassStrToNum(itemSubclass) in
    // Transmog.lua's selectTransmogSlot(). Those Str-to-Num tables map
    // directly onto WoW's real ITEM_CLASS_*/ITEM_SUBCLASS_* values, which are
    // exactly ItemTemplate::Class/SubClass here -- so bucket must be their sum,
    // not an arbitrary constant, or the client's table lookup finds nothing.
    //
    // <amount> is how many collected appearances follow (i.e. how many items
    // the player has actually unlocked for this bucket) -- it is NOT a
    // "total possible" figure, it's just the size of the id list that
    // follows, used by the client to validate it received every chunk.
    // <total> is the new field: how many items exist in the whole item store
    // that could ever be a valid transmog source here, collected or not.
    // It's computed with the exact same matching rules as <amount>'s list
    // (see Transmog::GetTotalPossibleAppearances), just scanning the full
    // item store instead of the player's collection, so the two numbers are
    // always comparable as a genuine "collected/total" pair.
    void SendAvailableForSlot(Player* player, uint8 slot)
    {
        Item* targetItem = player->GetItemByPos(INVENTORY_SLOT_BAG_0, slot);
        ItemTemplate const* targetTemplate = targetItem ? targetItem->GetTemplate() : nullptr;
        uint32 bucket = targetTemplate ? uint32(targetTemplate->Class) + uint32(targetTemplate->SubClass) : 0;

        std::vector<ItemTemplate const*> appearances = Transmog::GetValidAppearances(player, targetTemplate, slot);
        uint32 amount = static_cast<uint32>(appearances.size());
        uint32 total = Transmog::GetTotalPossibleAppearances(player, targetTemplate, slot);

        std::string header = "AvailableTransmogs:" + std::to_string(uint32(slot)) + ":" + std::to_string(bucket) + ":" + std::to_string(amount) + ":" + std::to_string(total) + ":";

        SendToClient(player, header + "start");

        size_t i = 0;
        while (i < appearances.size())
        {
            std::ostringstream chunk;
            size_t end = std::min(i + MAX_IDS_PER_CHUNK, appearances.size());
            for (size_t j = i; j < end; ++j)
            {
                if (j != i)
                    chunk << ":";
                chunk << appearances[j]->ItemId;
            }
            SendToClient(player, header + chunk.str());
            i = end;
        }

        SendToClient(player, header + "end");
    }

    void SendAvailableAll(Player* player)
    {
        for (uint8 slot = EQUIPMENT_SLOT_START; slot < EQUIPMENT_SLOT_END; ++slot)
        {
            if (Transmog::GetSlotName(slot).empty())
                continue;

            SendAvailableForSlot(player, slot);
        }
    }

    // "ApplyTransmogResult:1:<slot>,<itemEntry>"  /  "ApplyTransmogResult:0"
    void SendApplyResult(Player* player, bool success, uint8 slot, uint32 itemEntry)
    {
        if (!success)
        {
            SendToClient(player, "ApplyTransmogResult:0");
            return;
        }

        SendToClient(player, "ApplyTransmogResult:1:" + std::to_string(uint32(slot)) + "," + std::to_string(itemEntry));
    }

    // "TransmogCost:<cost>:<tokenID>:<canPurchase>"
    // mod-transmog-plus has no token-currency system, so tokenID is always
    // 0 (interpreted by the addon as "money") and affordability is checked
    // against copper only.
    void SendCost(Player* player, uint32 cost)
    {
        uint32 canPurchase = player->GetMoney() >= cost ? 1 : 0;
        SendToClient(player, "TransmogCost:" + std::to_string(cost) + ":0:" + std::to_string(canPurchase));
    }

    // ==========================================
    // INBOUND COMMAND HANDLERS
    // ==========================================
    // These call the exact same backend entry points TransmogGossip.cpp
    // uses (sTransmog->SetSlotAppearance / ApplySlot / RefreshSlot / etc,
    // TransmogRules_*), so applying an appearance via the addon overlay
    // behaves identically to applying it via the gossip menu.

    uint32 GetApplyCost(bool hidden)
    {
        if (hidden && sTransmog->HiddenTransmogIsFree)
            return 0;
        return sTransmog->PriceCopper;
    }

    void HandleGetTransmogStatus(Player* player, std::string const&)
    {
        SendStatus(player);
    }

    void HandleGetAvailableTransmogs(Player* player, std::string const&)
    {
        SendAvailableAll(player);
    }

    // "Apply:<slot>:<itemEntry>"  (itemEntry may be the HIDDEN_ITEM_ID sentinel)
    void HandleApply(Player* player, std::string const& args)
    {
        std::vector<std::string_view> parts = Acore::Tokenize(args, ':', false);
        if (parts.size() != 2)
        {
            SendApplyResult(player, false, 0, 0);
            return;
        }

        uint8 slot = static_cast<uint8>(std::strtoul(std::string(parts[0]).c_str(), nullptr, 10));
        uint32 itemEntry = static_cast<uint32>(std::strtoul(std::string(parts[1]).c_str(), nullptr, 10));

        if (slot >= EQUIPMENT_SLOT_END)
        {
            SendApplyResult(player, false, slot, itemEntry);
            return;
        }

        Item* targetItem = player->GetItemByPos(INVENTORY_SLOT_BAG_0, slot);
        bool hidden = (itemEntry == HIDDEN_ITEM_ID);

        if (hidden && !TransmogRules_IsArmorSlot(slot))
        {
            SendApplyResult(player, false, slot, itemEntry);
            return;
        }

        ItemTemplate const* sourceTemplate = hidden ? nullptr : sObjectMgr->GetItemTemplate(itemEntry);
        if (!hidden && !sourceTemplate)
        {
            SendApplyResult(player, false, slot, itemEntry);
            return;
        }

        if (!hidden && targetItem)
        {
            ItemTemplate const* targetTemplate = targetItem->GetTemplate();
            if (!TransmogRules_CanTransmogrifyItemWithItem(player, targetTemplate, sourceTemplate))
            {
                SendApplyResult(player, false, slot, itemEntry);
                return;
            }
        }

        uint32 cost = GetApplyCost(hidden);
        if (cost > 0 && !player->HasEnoughMoney(cost))
        {
            SendApplyResult(player, false, slot, itemEntry);
            return;
        }

        if (cost > 0)
            player->ModifyMoney(-static_cast<int32>(cost), false);

        sTransmog->SetSlotAppearance(player, slot, itemEntry);
        sTransmog->ApplySlot(player, slot, targetItem);

        SendApplyResult(player, true, slot, itemEntry);
    }

    // "Remove:<slot>"
    void HandleRemove(Player* player, std::string const& args)
    {
        uint8 slot = static_cast<uint8>(std::strtoul(args.c_str(), nullptr, 10));
        if (slot >= EQUIPMENT_SLOT_END)
        {
            SendApplyResult(player, false, slot, 0);
            return;
        }

        sTransmog->SetSlotAppearance(player, slot, 0);
        sTransmog->RefreshSlot(player, slot);
        SendApplyResult(player, true, slot, 0);
    }

    // "RemoveAll"
    void HandleRemoveAll(Player* player, std::string const&)
    {
        sTransmog->ClearAllSlots(player);
        sTransmog->RefreshAllSlots(player);
        SendStatus(player);
    }

    // "CalculateCost:<slot0>:<item0>,<slot1>:<item1>,..."
    // Only ever called by the addon for slots where a new appearance is
    // being applied (removals are free and handled client-side without a
    // round trip -- see Transmog:calculateCost in the addon).
    void HandleCalculateCost(Player* player, std::string const& args)
    {
        uint32 totalCost = 0;

        for (std::string_view pairStr : Acore::Tokenize(args, ',', false))
        {
            if (pairStr.empty())
                continue;

            size_t colon = pairStr.find(':');
            if (colon == std::string_view::npos)
                continue;

            uint32 itemEntry = static_cast<uint32>(std::strtoul(std::string(pairStr.substr(colon + 1)).c_str(), nullptr, 10));
            totalCost += GetApplyCost(itemEntry == HIDDEN_ITEM_ID);
        }

        SendCost(player, totalCost);
    }

    // ==========================================
    // DISPATCH
    // ==========================================

    void Dispatch(Player* player, std::string const& message)
    {
        size_t colon = message.find(':');
        std::string command = colon == std::string::npos ? message : message.substr(0, colon);
        std::string args = colon == std::string::npos ? std::string() : message.substr(colon + 1);

        if (command == "GetTransmogStatus")
            HandleGetTransmogStatus(player, args);
        else if (command == "GetAvailableTransmogs")
            HandleGetAvailableTransmogs(player, args);
        else if (command == "Apply")
            HandleApply(player, args);
        else if (command == "Remove")
            HandleRemove(player, args);
        else if (command == "RemoveAll")
            HandleRemoveAll(player, args);
        else if (command == "CalculateCost")
            HandleCalculateCost(player, args);
    }
}

// ==========================================
// INBOUND CHANNEL: PlayerScript hook
// ==========================================
//
// The client addon talks to us over the standard WoW addon-message
// channel by whispering itself: SendAddonMessage("transmog", payload,
// "WHISPER", UnitName("player")). That arrives here as an ordinary
// whisper with lang == LANG_ADDON and receiver == the sender, which
// OnPlayerCanUseChat(..., Player* receiver) already surfaces for every
// private chat message before it's delivered. We consume "transmog\t..."
// messages here and swallow them (return false) so the client never sees
// its own request echoed back as a real whisper; every other whisper
// (including other addons' prefixes) passes through untouched.

class TransmogAddonProtocolScript : public PlayerScript
{
public:
    TransmogAddonProtocolScript() : PlayerScript("TransmogAddonProtocolScript",
        {
            PLAYERHOOK_CAN_PLAYER_USE_PRIVATE_CHAT
        }) { }

    bool OnPlayerCanUseChat(Player* player, uint32 /*type*/, uint32 lang, std::string& msg, Player* receiver) override
    {
        if (!sTransmog->Enable)
            return true;

        if (lang != LANG_ADDON || !receiver || receiver != player)
            return true;

        std::string const prefixTab = std::string(TransmogAddon::PREFIX) + "\t";
        if (msg.compare(0, prefixTab.size(), prefixTab) != 0)
            return true;

        TransmogAddon::Dispatch(player, msg.substr(prefixTab.size()));
        return false; // consumed: don't deliver the raw request back to the client as a whisper
    }
};

// ==========================================
// LOADER
// ==========================================

void AddSC_TransmogAddonProtocol()
{
    new TransmogAddonProtocolScript();
}
