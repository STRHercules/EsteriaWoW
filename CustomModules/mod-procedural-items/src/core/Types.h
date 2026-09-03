#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace ProceduralItems
{
enum class ItemQuality : std::uint8_t
{
    Uncommon = 2,
    Rare = 3,
    Epic = 4
};

enum class ItemRole : std::uint8_t
{
    Hunter,
    Melee,
    Caster,
    Healer,
    Tank
};

enum class StatType : std::uint32_t
{
    Agility = 3,
    Strength = 4,
    Intellect = 5,
    Spirit = 6,
    Stamina = 7,
    DefenseRating = 12,
    DodgeRating = 13,
    ParryRating = 14,
    BlockRating = 15,
    HitRating = 31,
    CritRating = 32,
    HasteRating = 36,
    ExpertiseRating = 37,
    AttackPower = 38,
    RangedAttackPower = 39,
    ManaRegen = 43,
    ArmorPenetration = 44,
    SpellPower = 45,
    BlockValue = 48
};

struct ItemStat
{
    StatType type{};
    std::int32_t value{};

    bool operator==(ItemStat const&) const = default;
};

struct PoolRange
{
    std::string poolKey;
    std::uint32_t startEntry{};
    std::uint32_t endEntry{};
    std::uint32_t itemClass{};
    std::uint32_t subClass{};
    std::uint32_t inventoryType{};
};

struct AppearanceCandidate
{
    std::string poolKey;
    std::uint32_t displayId{};
    std::uint32_t minLevel{};
    std::uint32_t maxLevel{};
    std::uint32_t weight{1};
};

struct GenerationRequest
{
    std::uint64_t seed{};
    std::uint32_t level{1};
    std::uint32_t itemLevel{1};
    ItemQuality quality{ItemQuality::Uncommon};
    ItemRole role{ItemRole::Melee};
    std::string poolKey;
};

struct GeneratedItemDraft
{
    std::uint64_t seed{};
    std::string poolKey;
    std::string name;
    std::uint32_t requiredLevel{};
    std::uint32_t itemLevel{};
    ItemQuality quality{ItemQuality::Uncommon};
    ItemRole role{ItemRole::Melee};
    std::uint32_t displayId{};
    std::vector<ItemStat> stats;
};
}
