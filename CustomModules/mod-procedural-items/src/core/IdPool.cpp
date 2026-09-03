#include "core/IdPool.h"

#include <algorithm>

namespace ProceduralItems
{
void IdPool::addRange(PoolRange range)
{
    _ranges.push_back(std::move(range));
}

std::optional<std::uint32_t> IdPool::allocate(std::string const& poolKey, std::set<std::uint32_t> const& permanentlyUsed) const
{
    auto range = findRange(poolKey);
    if (!range || range->startEntry > range->endEntry)
        return std::nullopt;

    for (std::uint32_t entry = range->startEntry; entry <= range->endEntry; ++entry)
    {
        if (!permanentlyUsed.contains(entry))
            return entry;
        if (entry == UINT32_MAX)
            break;
    }
    return std::nullopt;
}

std::optional<PoolRange> IdPool::findRange(std::string const& poolKey) const
{
    auto it = std::find_if(_ranges.begin(), _ranges.end(), [&](PoolRange const& range)
    {
        return range.poolKey == poolKey;
    });
    return it == _ranges.end() ? std::nullopt : std::optional<PoolRange>(*it);
}

bool IdPool::hasOverlaps() const
{
    for (std::size_t i = 0; i < _ranges.size(); ++i)
    {
        for (std::size_t j = i + 1; j < _ranges.size(); ++j)
        {
            if (_ranges[i].startEntry <= _ranges[j].endEntry && _ranges[j].startEntry <= _ranges[i].endEntry)
                return true;
        }
    }
    return false;
}
}
