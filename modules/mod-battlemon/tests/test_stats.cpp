// Standalone check for src/BattlemonStats.h. Build and run:
// Run via tests/test_stats.py, which compiles and runs it.
#include "BattlemonStats.h"

#include <cstdio>
#include <cstdlib>

using namespace BattlemonStats;

#define CHECK(x)                                                    \
    do                                                              \
    {                                                               \
        if (!(x))                                                   \
        {                                                           \
            std::printf("FAIL line %d: %s\n", __LINE__, #x);        \
            return 1;                                               \
        }                                                           \
    } while (0)

int main()
{
    // Default Individual must equal the old fixed formula, so existing rows keep their stats.
    Individual legacy;
    // Old code: (2*80+31)*50/100 = 95, then +50+10 for HP and +5 for other stats.
    CHECK(Calc(80, 50, legacy, Stat::HP) == 155);
    CHECK(Calc(80, 50, legacy, Stat::ATK) == 100);

    // Bulbasaur-style reference (Gen 3+ formula): base 45 HP, L50, IV 31, EV 0 -> 120.
    CHECK(Calc(45, 50, legacy, Stat::HP) == 120);

    // base 130 Atk, L78, Adamant, IV 31, EV 252: core (260+31+63)*78/100 = 276, (276+5)*1.1 = 309.
    Individual g;
    g.nature = 3; // Adamant: +Atk -SpA
    g.ev[Stat::ATK] = 252;
    CHECK(Calc(130, 78, g, Stat::ATK) == 309);
    CHECK(NatureMod(3, Stat::ATK) == 110);
    CHECK(NatureMod(3, Stat::SPA) == 90);
    CHECK(NatureMod(3, Stat::SPE) == 100);
    CHECK(NatureMod(3, Stat::HP) == 100);
    for (int n : {0, 6, 12, 18, 24}) // the five neutral natures
        for (uint8_t s = 0; s < Stat::COUNT; ++s)
            CHECK(NatureMod(static_cast<uint8_t>(n), s) == 100);

    // EV caps: 252 per stat, 510 total.
    Individual e;
    CHECK(AddEv(e, Stat::ATK, 300) == 252);
    CHECK(AddEv(e, Stat::ATK, 1) == 0);
    CHECK(AddEv(e, Stat::DEF, 252) == 252);
    CHECK(AddEv(e, Stat::SPE, 252) == 6); // 510 - 504
    CHECK(AddEv(e, Stat::HP, 1) == 0);
    std::puts("ok");
    return 0;
}
