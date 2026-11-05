#ifndef BATTLEMON_STATS_H
#define BATTLEMON_STATS_H

// Mainline (Gen 3+) stat maths. Header-only and free of core types so tests/test_stats.cpp
// can compile it on its own.

#include <algorithm>
#include <cstdint>

namespace BattlemonStats
{
// Index order used by every array below.
namespace Stat
{
enum : uint8_t { HP = 0, ATK, DEF, SPA, SPD, SPE, COUNT };
}

constexpr uint16_t MAX_EV_STAT = 252;
constexpr uint16_t MAX_EV_TOTAL = 510;
constexpr uint8_t MAX_IV = 31;
constexpr uint8_t NATURE_COUNT = 25;

// What makes one Pokemon different from another of the same species.
// Defaults reproduce the old fixed maths (IV 31, no EVs, neutral nature), so rows
// and trainer teams that never rolled one keep their exact stats.
struct Individual
{
    uint8_t iv[Stat::COUNT] = {MAX_IV, MAX_IV, MAX_IV, MAX_IV, MAX_IV, MAX_IV};
    uint16_t ev[Stat::COUNT] = {};
    uint8_t nature = 0;      // 0..24; Hardy (0) is neutral
    uint8_t abilitySlot = 0; // 0 = ability1, 1 = ability2, 2 = hidden
    uint32_t otGuid = 0;     // original trainer's character guid; 0 = unknown
};

// Natures run in the mainline order: +stat = nature / 5, -stat = nature % 5, over
// Atk, Def, Spe, SpA, SpD. Equal means neutral (Hardy, Docile, Serious, Bashful, Quirky).
constexpr uint8_t NATURE_AXIS[5] = {Stat::ATK, Stat::DEF, Stat::SPE, Stat::SPA, Stat::SPD};

// Percent multiplier: 110, 100 or 90.
constexpr uint32_t NatureMod(uint8_t nature, uint8_t stat)
{
    if (nature >= NATURE_COUNT || stat == Stat::HP)
        return 100;
    uint8_t const up = NATURE_AXIS[nature / 5];
    uint8_t const down = NATURE_AXIS[nature % 5];
    if (up == down)
        return 100;
    return stat == up ? 110 : stat == down ? 90 : 100;
}

inline uint32_t Calc(uint32_t base, uint32_t level, Individual const& ind, uint8_t stat)
{
    uint32_t const core = (2 * base + ind.iv[stat] + ind.ev[stat] / 4) * level / 100;
    if (stat == Stat::HP)
        return core + level + 10;
    return (core + 5) * NatureMod(ind.nature, stat) / 100;
}

// Adds EVs honouring both caps; returns how many were actually added.
inline uint16_t AddEv(Individual& ind, uint8_t stat, uint16_t amount)
{
    uint32_t total = 0;
    for (uint8_t i = 0; i < Stat::COUNT; ++i)
        total += ind.ev[i];
    uint32_t const totalRoom = total >= MAX_EV_TOTAL ? 0 : MAX_EV_TOTAL - total;
    uint32_t const room = std::min<uint32_t>(MAX_EV_STAT - ind.ev[stat], totalRoom);
    uint16_t const added = static_cast<uint16_t>(std::min<uint32_t>(amount, room));
    ind.ev[stat] = static_cast<uint16_t>(ind.ev[stat] + added);
    return added;
}
} // namespace BattlemonStats

#endif
