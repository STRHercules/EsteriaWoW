#ifndef BATTLEMON_BREEDING_RULES_H
#define BATTLEMON_BREEDING_RULES_H

// The rules of Pokemon breeding, apart from the database and the networking. Header-only and free of core types
// so tests/test_breedingrules.cpp can compile it on its own. They follow the mainline games (Gen 6/7).

#include <algorithm>
#include <cstdint>
#include <string>
#include <vector>

namespace BattlemonBreedingRules
{
struct Parent
{
    std::string groups; // egg groups, comma separated ("Monster,Grass")
    char gender = 'N';  // M, F or N (genderless)
    uint32_t species = 0;
    uint32_t ot = 0;    // original trainer
};

enum class Match : uint8_t
{
    Ok,
    Undiscovered,  // a baby or a legendary: cannot breed
    DittoPair,     // two Ditto cannot make an egg
    Genderless,    // a genderless Pokemon only breeds with Ditto
    SameGender,
    NoSharedGroup
};

inline bool HasGroup(std::string const& groups, std::string const& name)
{
    size_t pos = 0;
    while (pos <= groups.size())
    {
        size_t const end = std::min(groups.find(',', pos), groups.size());
        if (end - pos == name.size() && groups.compare(pos, end - pos, name) == 0)
            return true;
        pos = end + 1;
    }
    return false;
}

inline bool SharesGroup(std::string const& a, std::string const& b)
{
    size_t pos = 0;
    while (pos <= a.size())
    {
        size_t const end = std::min(a.find(',', pos), a.size());
        std::string const group = a.substr(pos, end - pos);
        if (!group.empty() && HasGroup(b, group))
            return true;
        pos = end + 1;
    }
    return false;
}

inline Match Check(Parent const& a, Parent const& b)
{
    if (HasGroup(a.groups, "Undiscovered") || HasGroup(b.groups, "Undiscovered"))
        return Match::Undiscovered;
    bool const dittoA = HasGroup(a.groups, "Ditto");
    bool const dittoB = HasGroup(b.groups, "Ditto");
    if (dittoA && dittoB)
        return Match::DittoPair;
    if (dittoA || dittoB)
        return Match::Ok; // Ditto breeds with anything that can breed at all
    if (a.gender == 'N' || b.gender == 'N')
        return Match::Genderless;
    if (a.gender == b.gender)
        return Match::SameGender;
    return SharesGroup(a.groups, b.groups) ? Match::Ok : Match::NoSharedGroup;
}

// Chance (percent) that a compatible pair produces an egg at each check.
inline uint32_t EggChancePercent(bool sameSpecies, bool sameOt)
{
    if (sameSpecies)
        return sameOt ? 50 : 70;
    return sameOt ? 20 : 50;
}

// Which parent's species the egg is: the female's; with a Ditto, the other one. Returns 0 or 1.
inline int MotherIndex(Parent const& a, Parent const& b)
{
    if (HasGroup(a.groups, "Ditto"))
        return 1;
    if (HasGroup(b.groups, "Ditto"))
        return 0;
    return a.gender == 'F' ? 0 : 1;
}

// `count` stats (3 normally, 5 with a Destiny Knot) come from a random parent each, the rest are random.
// `rng(lo, hi)` is inclusive.
template <class Rng>
inline void InheritIvs(uint8_t const (&a)[6], uint8_t const (&b)[6], Rng&& rng, uint8_t (&out)[6], int count = 3)
{
    bool taken[6] = {};
    for (int n = 0; n < count;)
    {
        uint32_t const stat = rng(0, 5);
        if (taken[stat])
            continue;
        taken[stat] = true;
        out[stat] = rng(0, 1) ? a[stat] : b[stat];
        ++n;
    }
    for (int i = 0; i < 6; ++i)
        if (!taken[i])
            out[i] = static_cast<uint8_t>(rng(0, 31));
}

// The nature an egg gets: a parent holding an Everstone passes its own on (a coin flip if both do), otherwise
// the egg's nature is random. `holder[i]` says parent i holds one; returns the parent index, or -1 for random.
template <class Rng>
inline int NatureParent(bool const (&holder)[2], Rng&& rng)
{
    if (holder[0] && holder[1])
        return static_cast<int>(rng(0, 1));
    return holder[0] ? 0 : holder[1] ? 1 : -1;
}

// Seconds until an egg hatches: one 256-step cycle takes `secondsPer256`, scaled by `percent`.
inline uint32_t HatchSeconds(uint32_t hatchSteps, uint32_t secondsPer256, uint32_t percent)
{
    uint64_t const cycles = std::max<uint32_t>(1, hatchSteps / 256);
    return static_cast<uint32_t>(std::max<uint64_t>(1, cycles * secondsPer256 * percent / 100));
}

// The baby starts with its own level-1 moves, then inherited moves are added on top. A move already there is moved
// to the end (so it is kept); more than four drops the oldest.
inline std::vector<std::string> MergeMoves(std::vector<std::string> moves, std::vector<std::string> const& inherited)
{
    for (std::string const& move : inherited)
    {
        if (move.empty())
            continue;
        moves.erase(std::remove(moves.begin(), moves.end(), move), moves.end());
        moves.push_back(move);
    }
    while (moves.size() > 4)
        moves.erase(moves.begin());
    return moves;
}
} // namespace BattlemonBreedingRules

#endif
