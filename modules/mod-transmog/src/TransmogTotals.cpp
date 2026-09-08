#include "Transmog.h"

// ==========================================
// PER-SLOT ITEM CACHE
// ==========================================
//
// GetTotalPossibleAppearances needs to know, for a given equipment slot,
// how many items in the ENTIRE item store could ever be a valid transmog
// source for it -- not just the items a specific player has collected.
// A naive implementation would scan the full item_template store (tens of
// thousands of rows) on every addon UI open, which is wasteful.
//
// The item store never changes at runtime, so the player-independent part
// of that filter (does this item's InventoryType fit the slot, is it armor
// or a weapon, is it one of the item types transmog can never touch) is
// safe to compute once per slot and reuse forever. Only the remaining,
// genuinely player-specific checks (class/race/faction, known spells,
// skill values, armor-tier proficiency) still run per request, but by then
// they're running over a pre-filtered list of hundreds of items instead of
// tens of thousands.
//
// References into an unordered_map's values stay valid across future
// inserts of OTHER keys (erasure is the only thing that invalidates them,
// per the standard), and we never erase from this cache, so it's safe to
// hand back a reference after releasing the read lock.

namespace
{
    std::shared_mutex slotItemCacheMutex;
    std::unordered_map<uint8, std::vector<ItemTemplate const*>> slotItemCache;

    std::vector<ItemTemplate const*> const& GetItemsFittingSlot(uint8 slot)
    {
        {
            std::shared_lock<std::shared_mutex> readLock(slotItemCacheMutex);
            auto it = slotItemCache.find(slot);
            if (it != slotItemCache.end())
                return it->second;
        }

        std::vector<ItemTemplate const*> items;
        for (auto const& pair : *sObjectMgr->GetItemTemplateStore())
        {
            ItemTemplate const* proto = &pair.second;

            if (proto->Class != ITEM_CLASS_ARMOR && proto->Class != ITEM_CLASS_WEAPON)
                continue;

            if (!TransmogRules_ItemFitsInSlot(proto, slot))
                continue;

            if (TransmogRules_CanNeverTransmog(proto))
                continue;

            items.push_back(proto);
        }

        std::unique_lock<std::shared_mutex> writeLock(slotItemCacheMutex);
        // Another thread may have built and inserted this same slot's list
        // between the read-unlock above and this write-lock; emplace() is a
        // no-op in that case and we just use whichever copy won -- both are
        // built from the same immutable item store, so either is correct.
        auto result = slotItemCache.emplace(slot, std::move(items));
        return result.first->second;
    }
}

// ==========================================
// GET TOTAL POSSIBLE APPEARANCES
// ==========================================

uint32 Transmog::GetTotalPossibleAppearances(Player* player, ItemTemplate const* targetTemplate, uint8 slot)
{
    if (!player)
        return 0;

    uint32 count = 0;

    for (ItemTemplate const* proto : GetItemsFittingSlot(slot))
    {
        if (targetTemplate)
        {
            if (TransmogRules_CanTransmogrifyItemWithItem(player, targetTemplate, proto))
                ++count;
        }
        else if (TransmogRules_SuitableForTransmogrification(player, proto))
        {
            ++count;
        }
    }

    return count;
}
