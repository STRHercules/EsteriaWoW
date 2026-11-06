#ifndef BATTLEMON_HELD_ITEMS_H
#define BATTLEMON_HELD_ITEMS_H

// What a held item does, apart from the battle engine and the database. Header-only and free of core types so
// tests/test_helditems.cpp can compile it on its own. Items are named by battlemon_items.internal_name.
// Status numbers match BmStatus (0 none, 1 BRN, 2 PAR, 3 SLP, 4 PSN, 5 TOX, 6 FRZ); BattlemonBattle.cpp
// static_asserts that.

#include <cstdint>
#include <cstring>
#include <string>

namespace BattlemonHeldItems
{
enum class Kind : uint8_t
{
    TypeBoost,    // +20% to moves of one type
    ChoiceBand,   // physical x1.5, locks the first move used
    ChoiceSpecs,  // special x1.5, locks the first move used
    ChoiceScarf,  // speed x1.5, locks the first move used
    MuscleBand,   // physical x1.1
    WiseGlasses,  // special x1.1
    LifeOrb,      // damage x1.3, 10% of max HP lost per attack
    ExpertBelt,   // super effective hits x1.2
    FocusSash,    // survives one hit from full HP at 1 HP, then is used up
    Leftovers,    // heals 1/16 of max HP every round
    BlackSludge,  // like Leftovers for a Poison type, hurts anything else by 1/8
    HealBerry,    // eaten at half HP or less
    StatusBerry,  // eaten when the matching status lands
    LuckyEgg,     // +50% experience
    Everstone,    // breeding: passes its holder's nature on
    DestinyKnot   // breeding: five IVs are inherited instead of three
};

struct Entry
{
    char const* name;
    Kind kind;
    char const* type; // TypeBoost: the move type
    int32_t arg;      // HealBerry: HP healed (negative = that percent of max HP); StatusBerry: the status, 255 = any
};

constexpr Entry TABLE[] = {
    {"CHARCOAL", Kind::TypeBoost, "FIRE", 0},       {"MYSTICWATER", Kind::TypeBoost, "WATER", 0},
    {"MIRACLESEED", Kind::TypeBoost, "GRASS", 0},   {"MAGNET", Kind::TypeBoost, "ELECTRIC", 0},
    {"NEVERMELTICE", Kind::TypeBoost, "ICE", 0},    {"BLACKBELT", Kind::TypeBoost, "FIGHTING", 0},
    {"POISONBARB", Kind::TypeBoost, "POISON", 0},   {"SOFTSAND", Kind::TypeBoost, "GROUND", 0},
    {"SHARPBEAK", Kind::TypeBoost, "FLYING", 0},    {"TWISTEDSPOON", Kind::TypeBoost, "PSYCHIC", 0},
    {"SILVERPOWDER", Kind::TypeBoost, "BUG", 0},    {"HARDSTONE", Kind::TypeBoost, "ROCK", 0},
    {"SPELLTAG", Kind::TypeBoost, "GHOST", 0},      {"DRAGONFANG", Kind::TypeBoost, "DRAGON", 0},
    {"BLACKGLASSES", Kind::TypeBoost, "DARK", 0},   {"METALCOAT", Kind::TypeBoost, "STEEL", 0},
    {"SILKSCARF", Kind::TypeBoost, "NORMAL", 0},
    {"CHOICEBAND", Kind::ChoiceBand, "", 0},        {"CHOICESPECS", Kind::ChoiceSpecs, "", 0},
    {"CHOICESCARF", Kind::ChoiceScarf, "", 0},      {"MUSCLEBAND", Kind::MuscleBand, "", 0},
    {"WISEGLASSES", Kind::WiseGlasses, "", 0},      {"LIFEORB", Kind::LifeOrb, "", 0},
    {"EXPERTBELT", Kind::ExpertBelt, "", 0},        {"FOCUSSASH", Kind::FocusSash, "", 0},
    {"LEFTOVERS", Kind::Leftovers, "", 0},          {"BLACKSLUDGE", Kind::BlackSludge, "", 0},
    {"ORANBERRY", Kind::HealBerry, "", 10},         {"SITRUSBERRY", Kind::HealBerry, "", -25},
    {"CHERIBERRY", Kind::StatusBerry, "", 2},       {"CHESTOBERRY", Kind::StatusBerry, "", 3},
    {"PECHABERRY", Kind::StatusBerry, "", 4},       {"RAWSTBERRY", Kind::StatusBerry, "", 1},
    {"ASPEARBERRY", Kind::StatusBerry, "", 6},      {"LUMBERRY", Kind::StatusBerry, "", 255},
    {"LUCKYEGG", Kind::LuckyEgg, "", 0},            {"EVERSTONE", Kind::Everstone, "", 0},
    {"DESTINYKNOT", Kind::DestinyKnot, "", 0},
};

inline Entry const* Find(std::string const& item)
{
    for (Entry const& e : TABLE)
        if (item == e.name)
            return &e;
    return nullptr;
}

inline bool IsHoldable(std::string const& item)
{
    return Find(item) != nullptr;
}

inline bool Is(std::string const& item, Kind kind)
{
    Entry const* e = Find(item);
    return e && e->kind == kind;
}

inline bool IsChoice(std::string const& item)
{
    Entry const* e = Find(item);
    return e && (e->kind == Kind::ChoiceBand || e->kind == Kind::ChoiceSpecs || e->kind == Kind::ChoiceScarf);
}

// Multiplier on the attacker's offence for one move.
inline float AttackMul(std::string const& item, std::string const& category, std::string const& moveType)
{
    Entry const* e = Find(item);
    if (!e)
        return 1.0f;
    switch (e->kind)
    {
        case Kind::TypeBoost: return moveType == e->type ? 1.2f : 1.0f;
        case Kind::ChoiceBand: return category == "Physical" ? 1.5f : 1.0f;
        case Kind::ChoiceSpecs: return category == "Special" ? 1.5f : 1.0f;
        case Kind::MuscleBand: return category == "Physical" ? 1.1f : 1.0f;
        case Kind::WiseGlasses: return category == "Special" ? 1.1f : 1.0f;
        case Kind::LifeOrb: return 1.3f;
        default: return 1.0f;
    }
}

inline float SpeedMul(std::string const& item)
{
    return Is(item, Kind::ChoiceScarf) ? 1.5f : 1.0f;
}

// Applied after type effectiveness is known.
inline float AfterEffMul(std::string const& item, float effectiveness)
{
    return Is(item, Kind::ExpertBelt) && effectiveness > 1.0f ? 1.2f : 1.0f;
}

inline float ExpMul(std::string const& item)
{
    return Is(item, Kind::LuckyEgg) ? 1.5f : 1.0f;
}

// HP lost by a Life Orb holder after dealing damage.
inline int32_t LifeOrbRecoil(std::string const& item, int32_t maxHp)
{
    return Is(item, Kind::LifeOrb) ? (maxHp / 10 > 1 ? maxHp / 10 : 1) : 0;
}

// End-of-round HP change: positive heals, negative hurts.
inline int32_t EndOfRoundHp(std::string const& item, int32_t maxHp, bool isPoisonType)
{
    int32_t const sixteenth = maxHp / 16 > 1 ? maxHp / 16 : 1;
    if (Is(item, Kind::Leftovers))
        return sixteenth;
    if (Is(item, Kind::BlackSludge))
        return isPoisonType ? sixteenth : -(maxHp / 8 > 1 ? maxHp / 8 : 1);
    return 0;
}

// A Focus Sash holder at full HP that would be knocked out is left at 1 HP.
inline bool SashSaves(std::string const& item, int32_t hp, int32_t maxHp, int32_t damage)
{
    return Is(item, Kind::FocusSash) && hp == maxHp && damage >= hp;
}

struct BerryUse
{
    bool eat = false;
    int32_t heal = 0;     // HP restored
    bool cure = false;    // status removed
};

// Whether a berry is eaten now, given the holder's HP and status (BmStatus numbering).
inline BerryUse Berry(std::string const& item, int32_t hp, int32_t maxHp, uint8_t status)
{
    BerryUse use;
    Entry const* e = Find(item);
    if (!e || hp <= 0)
        return use;
    if (e->kind == Kind::HealBerry && hp * 2 <= maxHp && hp < maxHp)
    {
        use.eat = true;
        use.heal = e->arg >= 0 ? e->arg : maxHp * -e->arg / 100;
    }
    else if (e->kind == Kind::StatusBerry && status != 0)
    {
        bool const poison = e->arg == 4 && (status == 4 || status == 5); // Pecha cures bad poison too
        if (e->arg == 255 || e->arg == status || poison)
        {
            use.eat = true;
            use.cure = true;
        }
    }
    return use;
}
} // namespace BattlemonHeldItems

#endif
