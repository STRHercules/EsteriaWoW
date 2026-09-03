#include "core/ItemGenerator.h"

#include <algorithm>
#include <array>
#include <string_view>

namespace ProceduralItems
{
namespace
{
std::string_view baseName(std::string const& poolKey)
{
    if (poolKey.find("chest") != std::string::npos) return "Jerkin";
    if (poolKey.find("legs") != std::string::npos) return "Legguards";
    if (poolKey.find("bow") != std::string::npos) return "Longbow";
    if (poolKey.find("gun") != std::string::npos) return "Rifle";
    if (poolKey.find("sword") != std::string::npos) return "Blade";
    if (poolKey.find("axe") != std::string::npos) return "Axe";
    if (poolKey.find("mace") != std::string::npos) return "Mace";
    return "Relic";
}
}

std::vector<StatType> ItemGenerator::statPool(ItemRole role)
{
    switch (role)
    {
        case ItemRole::Hunter: return {StatType::Agility, StatType::Stamina, StatType::CritRating, StatType::HitRating, StatType::RangedAttackPower};
        case ItemRole::Melee:  return {StatType::Strength, StatType::Agility, StatType::Stamina, StatType::CritRating, StatType::HitRating, StatType::AttackPower};
        case ItemRole::Caster: return {StatType::Intellect, StatType::Stamina, StatType::SpellPower, StatType::CritRating, StatType::HasteRating};
        case ItemRole::Healer: return {StatType::Intellect, StatType::Spirit, StatType::SpellPower, StatType::HasteRating, StatType::ManaRegen};
        case ItemRole::Tank:   return {StatType::Stamina, StatType::Strength, StatType::DefenseRating, StatType::DodgeRating, StatType::ParryRating};
    }
    return {StatType::Stamina};
}

std::uint32_t ItemGenerator::statBudget(GenerationRequest const& request)
{
    std::uint32_t qualityFactor = request.quality == ItemQuality::Epic ? 145 : request.quality == ItemQuality::Rare ? 120 : 100;
    return std::max<std::uint32_t>(3, (request.itemLevel * qualityFactor) / 100);
}

std::string ItemGenerator::makeName(ItemRole role, std::string const& poolKey, DeterministicRng& rng)
{
    static constexpr std::array<std::string_view, 8> prefixes = {
        "Ashen", "Stormhide", "Thornbound", "Duskwoven", "Ironbark", "Embermarked", "Frostward", "Wildrunner"
    };
    static constexpr std::array<std::string_view, 5> hunter = {"Ranger's", "Tracker's", "Falconer's", "Pathfinder's", "Stalker's"};
    static constexpr std::array<std::string_view, 5> melee  = {"Vanguard's", "Slayer's", "Raider's", "Champion's", "Reaver's"};
    static constexpr std::array<std::string_view, 5> caster = {"Arcanist's", "Seer's", "Invoker's", "Sage's", "Mystic's"};
    static constexpr std::array<std::string_view, 5> healer = {"Mender's", "Oracle's", "Keeper's", "Lifebinder's", "Caretaker's"};
    static constexpr std::array<std::string_view, 5> tank   = {"Defender's", "Bulwark", "Warden's", "Guardian's", "Sentinel's"};

    auto chooseRole = [&](auto const& values) { return values[rng.index(values.size())]; };
    std::string_view roleWord;
    switch (role)
    {
        case ItemRole::Hunter: roleWord = chooseRole(hunter); break;
        case ItemRole::Melee: roleWord = chooseRole(melee); break;
        case ItemRole::Caster: roleWord = chooseRole(caster); break;
        case ItemRole::Healer: roleWord = chooseRole(healer); break;
        case ItemRole::Tank: roleWord = chooseRole(tank); break;
    }

    return std::string(prefixes[rng.index(prefixes.size())]) + " " + std::string(roleWord) + " " + std::string(baseName(poolKey));
}

std::optional<GeneratedItemDraft> ItemGenerator::generate(GenerationRequest const& request) const
{
    if (request.poolKey.empty() || request.level == 0 || request.itemLevel == 0)
        return std::nullopt;

    DeterministicRng rng(request.seed);
    auto appearance = _appearances.choose(request.poolKey, request.level, rng);
    if (!appearance)
        return std::nullopt;

    GeneratedItemDraft result;
    result.seed = request.seed;
    result.poolKey = request.poolKey;
    result.name = makeName(request.role, request.poolKey, rng);
    result.requiredLevel = request.level;
    result.itemLevel = request.itemLevel;
    result.quality = request.quality;
    result.role = request.role;
    result.displayId = appearance->displayId;

    auto candidates = statPool(request.role);
    std::uint32_t budget = statBudget(request);
    std::uint32_t statCount = request.quality == ItemQuality::Epic ? 4 : request.quality == ItemQuality::Rare ? 3 : 2;
    statCount = std::min<std::uint32_t>(statCount, static_cast<std::uint32_t>(candidates.size()));

    for (std::uint32_t i = 0; i < statCount; ++i)
    {
        std::size_t index = rng.index(candidates.size());
        StatType type = candidates[index];
        candidates.erase(candidates.begin() + static_cast<std::ptrdiff_t>(index));

        std::uint32_t remainingSlots = statCount - i;
        std::uint32_t share = std::max<std::uint32_t>(1, budget / remainingSlots);
        std::uint32_t jitter = std::max<std::uint32_t>(1, share / 5);
        std::uint32_t value = share - std::min(share - 1, jitter) + static_cast<std::uint32_t>(rng.bounded(jitter * 2 + 1));
        value = std::max<std::uint32_t>(1, value);
        result.stats.push_back({type, static_cast<std::int32_t>(value)});
        budget = budget > value ? budget - value : 0;
    }

    return result;
}
}
