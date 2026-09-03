#include "core/AppearanceCatalog.h"

#include <cstdint>

namespace ProceduralItems
{
void AppearanceCatalog::add(AppearanceCandidate candidate)
{
    _candidates.push_back(std::move(candidate));
}

std::optional<AppearanceCandidate> AppearanceCatalog::choose(std::string const& poolKey, std::uint32_t level, DeterministicRng& rng) const
{
    std::uint64_t totalWeight = 0;
    for (auto const& candidate : _candidates)
    {
        if (candidate.poolKey == poolKey && level >= candidate.minLevel && level <= candidate.maxLevel && candidate.weight > 0)
            totalWeight += candidate.weight;
    }

    if (totalWeight == 0)
        return std::nullopt;

    std::uint64_t roll = rng.bounded(totalWeight);
    for (auto const& candidate : _candidates)
    {
        if (candidate.poolKey != poolKey || level < candidate.minLevel || level > candidate.maxLevel || candidate.weight == 0)
            continue;
        if (roll < candidate.weight)
            return candidate;
        roll -= candidate.weight;
    }

    return std::nullopt;
}
}
