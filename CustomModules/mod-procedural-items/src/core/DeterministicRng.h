#pragma once

#include <cstddef>
#include <cstdint>

namespace ProceduralItems
{
class DeterministicRng
{
public:
    explicit DeterministicRng(std::uint64_t seed) : _state(seed) { }

    std::uint64_t nextU64()
    {
        std::uint64_t z = (_state += 0x9E3779B97F4A7C15ULL);
        z = (z ^ (z >> 30U)) * 0xBF58476D1CE4E5B9ULL;
        z = (z ^ (z >> 27U)) * 0x94D049BB133111EBULL;
        return z ^ (z >> 31U);
    }

    std::uint64_t bounded(std::uint64_t upperExclusive)
    {
        return upperExclusive == 0 ? 0 : nextU64() % upperExclusive;
    }

    std::size_t index(std::size_t count)
    {
        return static_cast<std::size_t>(bounded(static_cast<std::uint64_t>(count)));
    }

private:
    std::uint64_t _state;
};
}
