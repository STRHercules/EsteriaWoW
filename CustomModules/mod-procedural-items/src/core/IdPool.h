#pragma once

#include "core/Types.h"

#include <cstdint>
#include <optional>
#include <set>
#include <string>
#include <vector>

namespace ProceduralItems
{
class IdPool
{
public:
    void addRange(PoolRange range);
    std::optional<std::uint32_t> allocate(std::string const& poolKey, std::set<std::uint32_t> const& permanentlyUsed) const;
    std::optional<PoolRange> findRange(std::string const& poolKey) const;
    bool hasOverlaps() const;

private:
    std::vector<PoolRange> _ranges;
};
}
