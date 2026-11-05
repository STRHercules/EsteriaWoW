#ifndef BATTLEMON_SPAWN_RULES_H
#define BATTLEMON_SPAWN_RULES_H

// Scoring rules for zone-aware wild spawns. Header-only and free of core types so
// tests/test_spawns.cpp can compile it on its own.

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

namespace BattlemonSpawnRules
{
// "GRASS:3,BUG:2" -> [("GRASS", 3), ("BUG", 2)]. Returns false on any malformed token so a typo in the
// admin panel is rejected instead of silently dropping a type.
inline bool ParseTypes(std::string const& text, std::vector<std::pair<std::string, float>>& out)
{
    out.clear();
    size_t pos = 0;
    while (pos <= text.size())
    {
        size_t const end = std::min(text.find(',', pos), text.size());
        std::string token = text.substr(pos, end - pos);
        pos = end + 1;
        token.erase(std::remove(token.begin(), token.end(), ' '), token.end());
        if (token.empty())
        {
            if (end >= text.size() && pos > text.size())
                break;
            continue;
        }
        size_t const colon = token.find(':');
        if (colon == std::string::npos || colon == 0 || colon + 1 >= token.size())
            return false;
        std::string type = token.substr(0, colon);
        for (char& c : type)
            c = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
        char* stop = nullptr;
        float const weight = std::strtof(token.c_str() + colon + 1, &stop);
        if (*stop != '\0' || !(weight >= 0.0f) || weight > 100.0f)
            return false;
        out.emplace_back(type, weight);
    }
    return true;
}

// A species counts as its best-matching type; a type the zone does not list gets the leak weight
// (0 keeps strangers out entirely).
inline float TypeWeight(std::vector<std::pair<std::string, float>> const& zone, std::string const& type1,
                        std::string const& type2, float leak)
{
    float best = -1.0f;
    for (auto const& entry : zone)
        if (entry.first == type1 || (!type2.empty() && entry.first == type2))
            best = std::max(best, entry.second);
    return best < 0.0f ? leak : best;
}

// Catch rate 255 is the most common Pokemon, 3 a legendary. exponent 0 ignores rarity; 1 is proportional.
inline float RarityWeight(uint32_t catchRate, float exponent)
{
    if (exponent <= 0.0f)
        return 1.0f;
    float const common = std::max(1u, std::min(catchRate, 255u)) / 255.0f;
    return std::max(0.0005f, std::pow(common, exponent));
}

// How a species evolves from the one before it: `level` is the level it evolves at, 0 when it evolves by
// anything else (stone, trade, happiness, ...).
struct EvoLink
{
    uint32_t prevo = 0;
    uint32_t level = 0;
};

// The lowest level a species naturally appears at: the chain's real evolution levels, with `step` extra levels
// for each evolution that is not level-based. Ivysaur 16, Venusaur 32; with step 8, Pikachu 9 (a happiness
// evolution of a baby) and Raichu 17. step 0 turns the whole gate off.
inline uint32_t MinLevel(uint32_t species, std::unordered_map<uint32_t, EvoLink> const& links, uint32_t step)
{
    if (step == 0)
        return 1;
    EvoLink chain[8];
    uint32_t depth = 0;
    for (uint32_t cur = species; depth < 8;)
    {
        auto it = links.find(cur);
        if (it == links.end() || !it->second.prevo)
            break;
        chain[depth++] = it->second;
        cur = it->second.prevo;
    }
    uint32_t level = 1;
    for (uint32_t i = depth; i-- > 0;) // base form first
        level = chain[i].level ? std::max(level, chain[i].level) : level + step;
    return std::min(level, 100u);
}

// mode 0 keeps the player-scaled level, 1 rolls inside the zone's range, 2 clamps the scaled level into it.
// `roll` is a uniform number in [min, max] supplied by the caller.
inline uint32_t EnemyLevel(uint32_t mode, uint32_t scaled, uint32_t zoneMin, uint32_t zoneMax, uint32_t roll)
{
    if (mode == 0 || zoneMin == 0 || zoneMax < zoneMin)
        return scaled;
    uint32_t level = mode == 1 ? roll : std::min(std::max(scaled, zoneMin), zoneMax);
    return std::min(std::max(level, 1u), 100u);
}

} // namespace BattlemonSpawnRules

#endif
