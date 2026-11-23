/* House bankroll rules, kept free of game types so they can be unit tested.
 *
 * The house never creates gold: its bankroll is gold a GM moved in or players lost. Every open round reserves the
 * most the house could lose on it, and a new bet is only taken while the unreserved bankroll covers that worst case.
 */
#ifndef ESTERIA_CASINO_HOUSE_H
#define ESTERIA_CASINO_HOUSE_H

#include <algorithm>
#include <cstdint>

namespace EsteriaCasino
{
    struct House
    {
        int64_t bankroll = 0;  // copper the house owns, as stored in casino_house
        uint64_t reserved = 0; // worst-case loss of every open round, memory only

        uint64_t Available() const
        {
            return bankroll > int64_t(reserved) ? uint64_t(bankroll) - reserved : 0;
        }

        // Largest opening stake the house can cover, capped by the table limit.
        uint64_t MaxBet(uint32_t lossMultiplier, uint64_t tableMax) const
        {
            return std::min(tableMax, Available() / lossMultiplier);
        }

        bool Reserve(uint64_t worstLoss)
        {
            if (worstLoss > Available())
                return false;
            reserved += worstLoss;
            return true;
        }

        // Closes a round: drops its reservation and books the house's net result (wagered minus paid back).
        int64_t Settle(uint64_t worstLoss, uint64_t wagered, uint64_t paid)
        {
            reserved -= std::min(reserved, worstLoss);
            int64_t const delta = int64_t(wagered) - int64_t(paid);
            bankroll += delta;
            return delta;
        }
    };
}

#endif
