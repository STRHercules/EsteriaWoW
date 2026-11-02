#ifndef ESTERIA_PERK_RULES_H
#define ESTERIA_PERK_RULES_H

#include "PerkWire.h"
#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>

// Paths of Fate rules (design: Esteria_Paths_of_Fate_Design_v1.md §2-3). Pure, so they can be tested without a
// server. Card ids are the contract with the database and the client: never reorder or reuse one, only append.
namespace EsteriaPerks
{
    enum Path : uint8_t { Combat, Survival, Exploration, Industry, Influence, Companions, PathCount };
    enum Tier : uint8_t { Initiate, Specialist, Veteran, Legendary };

    struct Card
    {
        uint8_t id;
        uint8_t path;
        uint8_t tier;
        uint8_t maxRank;
        uint32_t classMask; // 0: every class; else bit (class - 1) per class that can use it
        bool implemented;   // has an effect; the rest are previews (EsteriaPerkWire::CardPlanned)
    };

    // Mage, Warlock, Priest, Shaman, Druid: the classes spell pushback matters to.
    inline constexpr uint32_t Casters = 1u << 7 | 1u << 8 | 1u << 4 | 1u << 6 | 1u << 10;

    // Id = path * 10 + slot. Names (in order): see the design doc §3 and the EsteriaPerks addon.
    inline constexpr Card Cards[] = {
        { 1, Combat, Initiate, 2, 0, true }, { 2, Combat, Initiate, 2, 0, true }, { 3, Combat, Initiate, 2, 0, true },
        { 4, Combat, Specialist, 2, 0, true }, { 5, Combat, Specialist, 2, Casters, true },
        { 6, Combat, Specialist, 2, 0, true }, { 7, Combat, Veteran, 1, 0, true }, { 8, Combat, Veteran, 1, 0, false },
        { 9, Combat, Legendary, 1, 0, true },
        { 11, Survival, Initiate, 2, 0, true }, { 12, Survival, Initiate, 2, 0, true },
        { 13, Survival, Initiate, 2, 0, true }, // Surefooted
        { 14, Survival, Specialist, 2, 0, true }, { 15, Survival, Specialist, 2, 0, true },
        { 16, Survival, Specialist, 2, 0, true }, { 17, Survival, Veteran, 1, 0, true },
        { 18, Survival, Veteran, 1, 0, true }, { 19, Survival, Legendary, 1, 0, true },
        { 21, Exploration, Initiate, 2, 0, true }, { 22, Exploration, Initiate, 2, 0, true },
        { 23, Exploration, Initiate, 2, 0, true }, { 24, Exploration, Specialist, 2, 0, true },
        { 25, Exploration, Specialist, 2, 0, true }, { 26, Exploration, Specialist, 2, 0, true },
        { 27, Exploration, Veteran, 1, 0, true }, { 28, Exploration, Veteran, 1, 0, true },
        { 29, Exploration, Legendary, 1, 0, true },
        { 31, Industry, Initiate, 2, 0, true }, { 32, Industry, Initiate, 2, 0, true },
        { 33, Industry, Initiate, 2, 0, true }, { 34, Industry, Specialist, 2, 0, true },
        { 35, Industry, Specialist, 2, 0, true }, { 36, Industry, Specialist, 1, 0, true },
        { 37, Industry, Veteran, 1, 0, true }, { 38, Industry, Veteran, 1, 0, true },
        { 39, Industry, Legendary, 1, 0, false },
        { 41, Influence, Initiate, 2, 0, true }, { 42, Influence, Initiate, 2, 0, true },
        { 43, Influence, Initiate, 2, 0, true }, { 44, Influence, Specialist, 1, 0, true },
        { 45, Influence, Specialist, 2, 0, true }, { 46, Influence, Specialist, 1, 0, true },
        { 47, Influence, Veteran, 1, 0, true }, { 48, Influence, Veteran, 1, 0, true },
        { 49, Influence, Legendary, 1, 0, true },
        { 51, Companions, Initiate, 2, 0, true }, { 52, Companions, Initiate, 2, 0, true },
        { 53, Companions, Initiate, 1, 0, false }, { 54, Companions, Specialist, 2, 0, false },
        { 55, Companions, Specialist, 1, 0, false }, { 56, Companions, Specialist, 2, 0, true },
        { 57, Companions, Veteran, 1, 0, false }, { 58, Companions, Veteran, 2, 0, false },
        { 59, Companions, Legendary, 1, 0, false },
    };
    inline constexpr size_t CardCount = sizeof(Cards) / sizeof(Cards[0]);
    inline constexpr uint8_t Surefooted = 13;

    // Purchased rank per card, in Cards order.
    using Ranks = std::array<uint8_t, CardCount>;

    struct TierGate { uint8_t level; uint8_t pathPoints; };
    inline constexpr TierGate Gates[] = { { 10, 0 }, { 30, 2 }, { 50, 4 }, { 70, 6 } };

    // Options a realm sets: SellPlanned lets previews (and feat-gated legendaries) be bought, for testing.
    struct Options { bool sellPlanned = false; };

    inline int IndexOf(uint8_t id)
    {
        for (size_t i = 0; i < CardCount; ++i)
            if (Cards[i].id == id)
                return int(i);
        return -1;
    }

    constexpr uint8_t Cost(Card const& card) { return card.tier == Legendary ? 2 : 1; }

    // One point at 10, then one every five levels: 15 at 80.
    constexpr uint8_t Earned(uint32_t level)
    {
        return level < 10 ? 0 : uint8_t(std::min<uint32_t>((level - 10) / 5 + 1, 15));
    }

    inline uint8_t Spent(Ranks const& ranks, int path = -1)
    {
        unsigned total = 0;
        for (size_t i = 0; i < CardCount; ++i)
            if (path < 0 || Cards[i].path == path)
                total += ranks[i] * Cost(Cards[i]);
        return uint8_t(total);
    }

    constexpr bool ClassCanUse(Card const& card, uint8_t classId)
    {
        return !card.classMask || (classId >= 1 && classId <= 32 && (card.classMask & 1u << (classId - 1)));
    }

    // What buying `rank` of the card at `index` gets now. Checked in the order a player fixes them.
    inline EsteriaPerkWire::Result Check(Ranks const& ranks, int index, uint8_t rank, uint32_t level, uint8_t classId,
        Options const& options)
    {
        using namespace EsteriaPerkWire;
        if (index < 0 || size_t(index) >= CardCount)
            return Unknown;
        Card const& card = Cards[index];
        if (!ClassCanUse(card, classId))
            return Class;
        if (rank != ranks[index] + 1 || rank > card.maxRank)
            return Rank;
        if (!card.implemented && !options.sellPlanned)
            return Planned;
        if (level < Gates[card.tier].level)
            return Level;
        if (Spent(ranks, card.path) < Gates[card.tier].pathPoints)
            return PathPoints;
        if (card.tier == Legendary)
            for (size_t i = 0; i < CardCount; ++i)
                if (Cards[i].tier == Legendary && ranks[i])
                    return LegendaryOwned;
        if (Spent(ranks) + Cost(card) > Earned(level))
            return Points;
        // shortcut: no feats exist yet, so legendaries stay locked unless the realm sells previews; add the feat
        // check here with the legendary questlines (design phase 5).
        if (card.tier == Legendary && !options.sellPlanned)
            return Feat;
        return Ok;
    }

    // Gold for the next respec: the first is free, then 50 silver per level up to 50 gold.
    constexpr uint32_t RespecCost(uint8_t respecsDone, uint32_t level)
    {
        return respecsDone == 0 ? 0 : std::min<uint32_t>(level * 5000, 500000);
    }
}

#endif
