#pragma once

#include "core/AppearanceCatalog.h"
#include "core/Types.h"

#include <optional>
#include <string>
#include <vector>

namespace ProceduralItems
{
class ItemGenerator
{
public:
    explicit ItemGenerator(AppearanceCatalog const& appearances) : _appearances(appearances) { }

    std::optional<GeneratedItemDraft> generate(GenerationRequest const& request) const;

private:
    static std::vector<StatType> statPool(ItemRole role);
    static std::string makeName(ItemRole role, std::string const& poolKey, DeterministicRng& rng);
    static std::uint32_t statBudget(GenerationRequest const& request);

    AppearanceCatalog const& _appearances;
};
}
