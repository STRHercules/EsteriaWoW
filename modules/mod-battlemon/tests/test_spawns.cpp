// Standalone check for src/BattlemonSpawnRules.h; tests/test_spawns.py compiles and runs it.
#include "BattlemonSpawnRules.h"

#include <cstdio>

using namespace BattlemonSpawnRules;

#define CHECK(x)                                             \
    do                                                       \
    {                                                        \
        if (!(x))                                            \
        {                                                    \
            std::printf("FAIL line %d: %s\n", __LINE__, #x); \
            return 1;                                        \
        }                                                    \
    } while (0)

int main()
{
    std::vector<std::pair<std::string, float>> zone;
    CHECK(ParseTypes("grass:3, BUG:2,Fire:0.5", zone));
    CHECK(zone.size() == 3 && zone[0].first == "GRASS" && zone[0].second == 3.0f && zone[2].second == 0.5f);
    CHECK(ParseTypes("", zone) && zone.empty());
    CHECK(!ParseTypes("GRASS", zone));       // no weight
    CHECK(!ParseTypes("GRASS:x", zone));     // not a number
    CHECK(!ParseTypes("GRASS:-1", zone));    // negative
    CHECK(!ParseTypes(":3", zone));          // no type
    CHECK(!ParseTypes("GRASS:3,,BUG", zone)); // second token malformed

    ParseTypes("GRASS:3,BUG:2", zone);
    CHECK(TypeWeight(zone, "GRASS", "POISON", 0.1f) == 3.0f);   // best of the two types
    CHECK(TypeWeight(zone, "POISON", "BUG", 0.1f) == 2.0f);
    CHECK(TypeWeight(zone, "FIRE", "", 0.1f) == 0.1f);          // stranger gets the leak weight
    CHECK(TypeWeight(zone, "FIRE", "", 0.0f) == 0.0f);          // leak 0 excludes it
    ParseTypes("GRASS:0", zone);
    CHECK(TypeWeight(zone, "GRASS", "", 0.5f) == 0.0f);         // an explicit 0 bans, not leaks

    CHECK(RarityWeight(255, 1.0f) == 1.0f);
    CHECK(std::fabs(RarityWeight(45, 1.0f) - 45.0f / 255.0f) < 1e-6f);
    CHECK(RarityWeight(3, 0.0f) == 1.0f);                       // exponent 0 ignores rarity
    CHECK(RarityWeight(0, 1.0f) > 0.0f);                        // never zero, so nothing vanishes
    CHECK(RarityWeight(3, 1.0f) < RarityWeight(255, 1.0f));

    CHECK(EnemyLevel(0, 33, 10, 20, 15) == 33);                 // mode 0 untouched
    CHECK(EnemyLevel(1, 33, 10, 20, 15) == 15);                 // mode 1 uses the roll
    CHECK(EnemyLevel(2, 33, 10, 20, 15) == 20);                 // mode 2 clamps down...
    CHECK(EnemyLevel(2, 4, 10, 20, 15) == 10);                  // ...and up
    CHECK(EnemyLevel(2, 15, 10, 20, 12) == 15);
    CHECK(EnemyLevel(2, 33, 0, 0, 5) == 33);                    // no zone range -> scaled level

    // Natural minimum level from real evolution data. Ids: 1 Bulbasaur 2 Ivysaur 3 Venusaur,
    // 10 Pichu 11 Pikachu 12 Raichu, 20/21 a two-species loop in bad data.
    std::unordered_map<uint32_t, EvoLink> links = {
        {2, {1, 16}}, {3, {2, 32}},   // by level
        {11, {10, 0}}, {12, {11, 0}}, // baby -> happiness, then a stone
        {20, {21, 0}}, {21, {20, 0}}};
    CHECK(MinLevel(1, links, 8) == 1);                          // a base form appears at any level
    CHECK(MinLevel(2, links, 8) == 16 && MinLevel(3, links, 8) == 32);
    CHECK(MinLevel(10, links, 8) == 1);
    CHECK(MinLevel(11, links, 8) == 9);                         // Pikachu: one non-level hop
    CHECK(MinLevel(12, links, 8) == 17);                        // Raichu: two hops
    CHECK(MinLevel(11, links, 0) == 1 && MinLevel(3, links, 0) == 1); // step 0 = gate off
    CHECK(MinLevel(99, links, 8) == 1);                         // unknown species
    CHECK(MinLevel(20, links, 8) <= 100);                       // a cycle terminates
    CHECK(MinLevel(12, links, 200) == 100);                     // never above the level cap
    std::puts("ok");
    return 0;
}
