#ifndef BATTLEMON_TRADE_RULES_H
#define BATTLEMON_TRADE_RULES_H

// The rules of a Pokemon-for-Pokemon trade, apart from the networking and the database. Header-only and free of
// core types so tests/test_traderules.cpp can compile it on its own.

#include <cstdint>

namespace BattlemonTradeRules
{
enum class Check : uint8_t
{
    Ok,
    NothingOffered,  // neither side put a Pokemon up
    WouldBeEmpty     // a side would be left with no Pokemon at all
};

// `owned` is how many Pokemon each side has now; `gives`/`gets` are 1 when that side puts one up / receives one.
// Both sides must keep at least one Pokemon (a trainer with none cannot fight or even open the party screen).
inline Check Validate(uint32_t ownedA, bool givesA, uint32_t ownedB, bool givesB)
{
    if (!givesA && !givesB)
        return Check::NothingOffered;
    // A gives 1 and gets 1 if B gives, and vice versa.
    // Signed: a side that "gives" a Pokemon it does not have must not wrap around to a huge number.
    int64_t const afterA = int64_t(ownedA) - (givesA ? 1 : 0) + (givesB ? 1 : 0);
    int64_t const afterB = int64_t(ownedB) - (givesB ? 1 : 0) + (givesA ? 1 : 0);
    if (afterA < 1 || afterB < 1)
        return Check::WouldBeEmpty;
    return Check::Ok;
}

// The party after `gave` leaves and `received` arrives (0 = nothing arrives). The newcomer takes the traded
// Pokemon's slot, as in the mainline games; if nothing arrives the party closes up so slot 1 (the lead) is never
// empty. A Pokemon that was in the box stays out of the party.
inline void NewParty(uint32_t (&party)[6], uint32_t gave, uint32_t received)
{
    int slot = -1;
    for (int i = 0; i < 6; ++i)
        if (gave && party[i] == gave)
            slot = i;
    if (slot < 0)
        return;
    party[slot] = received;
    // Close gaps, keeping order.
    uint32_t packed[6] = {};
    int n = 0;
    for (int i = 0; i < 6; ++i)
        if (party[i])
            packed[n++] = party[i];
    for (int i = 0; i < 6; ++i)
        party[i] = packed[i];
}
} // namespace BattlemonTradeRules

#endif
