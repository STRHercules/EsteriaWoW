#pragma once

#include "core/DeterministicRng.h"
#include "core/Types.h"

#include <optional>
#include <string>
#include <vector>

namespace ProceduralItems
{
class AppearanceCatalog
{
public:
    void add(AppearanceCandidate candidate);
    std::optional<AppearanceCandidate> choose(std::string const& poolKey, std::uint32_t level, DeterministicRng& rng) const;
    bool empty() const { return _candidates.empty(); }

private:
    std::vector<AppearanceCandidate> _candidates;
};
}
