/* Pure crate-pool rules, kept free of game types so they can be unit tested. */
#ifndef ESTERIA_CRATE_POOL_H
#define ESTERIA_CRATE_POOL_H

#include <cstdint>
#include <limits>
#include <vector>

namespace EsteriaCrates
{
    // Sum of the weights, or 0 when the pool is empty, has a zero weight, or would overflow.
    inline uint32_t TotalWeight(std::vector<uint32_t> const& weights)
    {
        uint64_t total = 0;
        for (uint32_t weight : weights)
        {
            if (!weight)
                return 0;
            total += weight;
        }
        return total > std::numeric_limits<uint32_t>::max() ? 0 : uint32_t(total);
    }

    // roll is uniform in [1, TotalWeight]; each index is hit by exactly `weight` roll values.
    inline size_t Pick(std::vector<uint32_t> const& weights, uint32_t roll)
    {
        for (size_t i = 0; i < weights.size(); ++i)
        {
            if (roll <= weights[i])
                return i;
            roll -= weights[i];
        }
        return weights.size() - 1;
    }
}

#endif
