// Standalone check for src/BattlemonTradeRules.h; tests/test_traderules.py compiles and runs it.
#include "BattlemonTradeRules.h"

#include <cstdio>

using namespace BattlemonTradeRules;

#define CHECK(x)                                             \
    do                                                       \
    {                                                        \
        if (!(x))                                            \
        {                                                    \
            std::printf("FAIL line %d: %s\n", __LINE__, #x); \
            return 1;                                        \
        }                                                    \
    } while (0)

static bool same(uint32_t const (&a)[6], uint32_t const (&b)[6])
{
    for (int i = 0; i < 6; ++i)
        if (a[i] != b[i])
            return false;
    return true;
}

int main()
{
    // Swaps are always fine while both keep a Pokemon, however few they own.
    CHECK(Validate(1, true, 1, true) == Check::Ok);
    CHECK(Validate(5, true, 2, true) == Check::Ok);
    CHECK(Validate(3, false, 3, false) == Check::NothingOffered);
    // A gift must not strip the giver's last Pokemon, but is fine from someone with spares.
    CHECK(Validate(1, true, 4, false) == Check::WouldBeEmpty);
    CHECK(Validate(2, true, 4, false) == Check::Ok);
    CHECK(Validate(4, false, 1, true) == Check::WouldBeEmpty); // B would give away their only Pokemon
    CHECK(Validate(4, false, 2, true) == Check::Ok);
    CHECK(Validate(0, false, 3, true) == Check::Ok);          // an empty-handed receiver of a gift ends with one
    CHECK(Validate(0, true, 3, true) == Check::WouldBeEmpty); // cannot give what is not there
    CHECK(Validate(0, true, 3, false) == Check::WouldBeEmpty); // ...and must not wrap around to "plenty left"

    // The newcomer takes the traded Pokemon's slot.
    uint32_t p1[6] = {10, 11, 12, 0, 0, 0};
    NewParty(p1, 11, 99);
    { uint32_t want[6] = {10, 99, 12, 0, 0, 0}; CHECK(same(p1, want)); }
    uint32_t lead[6] = {10, 11, 0, 0, 0, 0};
    NewParty(lead, 10, 99);                                   // trading the lead hands the lead to the newcomer
    { uint32_t want[6] = {99, 11, 0, 0, 0, 0}; CHECK(same(lead, want)); }

    // A gift out of the party closes the gap and keeps a lead.
    uint32_t gift[6] = {10, 11, 12, 0, 0, 0};
    NewParty(gift, 10, 0);
    { uint32_t want[6] = {11, 12, 0, 0, 0, 0}; CHECK(same(gift, want)); }

    // A Pokemon from the box changes nothing about the party, whether or not something arrives.
    uint32_t box[6] = {10, 11, 0, 0, 0, 0};
    NewParty(box, 77, 99);
    { uint32_t want[6] = {10, 11, 0, 0, 0, 0}; CHECK(same(box, want)); }
    NewParty(box, 0, 99);                                     // a gift received goes to the box
    { uint32_t want[6] = {10, 11, 0, 0, 0, 0}; CHECK(same(box, want)); }
    std::puts("ok");
    return 0;
}
