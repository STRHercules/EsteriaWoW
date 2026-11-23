/* Three-reel slot machine rules, kept free of game types so they can be unit tested.
 *
 * Every reel draws one symbol by weight; only the centre line pays. Three of a kind pays TriplePay times the stake
 * (stake included), and any other line made only of coins (copper, silver, gold) returns the stake. The exact return
 * to player follows from the weights and is published to the client.
 */
#ifndef ESTERIA_CASINO_SLOTS_H
#define ESTERIA_CASINO_SLOTS_H

#include <array>
#include <cstdint>

namespace EsteriaCasino::Slots
{
    // Copper, silver, gold, ruby, crown, red dragon. The client maps the same order to icons.
    constexpr size_t SymbolCount = 6;
    constexpr std::array<uint32_t, SymbolCount> Weights = { 10, 8, 6, 4, 3, 1 };
    constexpr std::array<uint32_t, SymbolCount> TriplePay = { 4, 10, 20, 50, 100, 500 };
    constexpr uint32_t CoinSymbols = 3;  // symbols 0..2 are coins
    constexpr uint32_t MixedCoinPay = 1; // stake back
    constexpr uint32_t MaxPay = 500;

    constexpr uint32_t TotalWeight()
    {
        uint32_t total = 0;
        for (uint32_t w : Weights)
            total += w;
        return total;
    }

    // roll is uniform in [0, TotalWeight).
    constexpr uint8_t Symbol(uint32_t roll)
    {
        for (size_t i = 0; i < SymbolCount; ++i)
        {
            if (roll < Weights[i])
                return uint8_t(i);
            roll -= Weights[i];
        }
        return SymbolCount - 1;
    }

    // Multiple of the stake handed back for a centre line.
    constexpr uint32_t Pay(uint8_t a, uint8_t b, uint8_t c)
    {
        if (a == b && b == c)
            return TriplePay[a];
        if (a < CoinSymbols && b < CoinSymbols && c < CoinSymbols)
            return MixedCoinPay;
        return 0;
    }

    // Exact return to player in basis points (10000 = everything back), from every weighted line.
    constexpr uint32_t ReturnBasisPoints()
    {
        uint64_t returned = 0;
        for (uint8_t a = 0; a < SymbolCount; ++a)
            for (uint8_t b = 0; b < SymbolCount; ++b)
                for (uint8_t c = 0; c < SymbolCount; ++c)
                    returned += uint64_t(Weights[a]) * Weights[b] * Weights[c] * Pay(a, b, c);
        uint64_t const total = uint64_t(TotalWeight()) * TotalWeight() * TotalWeight();
        return uint32_t(returned * 10000 / total);
    }
}

#endif
