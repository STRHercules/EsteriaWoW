/* Goblin Dice rules: two six-sided dice against the house, kept free of game types so they can be unit tested.
 *
 * The player picks a call before the roll: under 7, exactly 7, over 7, or any double. A winning call returns
 * ReturnBasisPoints of the stake (stake included, rounded down to the copper); a losing call returns nothing.
 */
#ifndef ESTERIA_CASINO_DICE_H
#define ESTERIA_CASINO_DICE_H

#include <array>
#include <cstdint>

namespace EsteriaCasino::Dice
{
    enum class Call : uint8_t
    {
        Under,
        Seven,
        Over,
        Doubles,
    };

    constexpr size_t CallCount = 4;
    // Under/over win 15 of 36 rolls, seven and doubles 6 of 36; these returns keep each call near 97%.
    constexpr std::array<uint32_t, CallCount> ReturnBasisPoints = { 23300, 58000, 23300, 58000 };
    // Largest net house loss per call, rounded up to whole stakes (5.8x return = 4.8x net loss).
    constexpr uint32_t MaxHouseLossMultiplier = 5;

    constexpr bool Wins(Call call, uint8_t d1, uint8_t d2)
    {
        uint32_t const sum = d1 + d2;
        switch (call)
        {
            case Call::Under: return sum < 7;
            case Call::Seven: return sum == 7;
            case Call::Over: return sum > 7;
            case Call::Doubles: return d1 == d2;
        }
        return false;
    }

    constexpr uint64_t Paid(uint64_t stake, Call call, uint8_t d1, uint8_t d2)
    {
        return Wins(call, d1, d2) ? stake * ReturnBasisPoints[size_t(call)] / 10000 : 0;
    }

    // Exact return to player of one call in basis points, over all 36 rolls.
    constexpr uint32_t CallReturnBasisPoints(Call call)
    {
        uint32_t wins = 0;
        for (uint8_t d1 = 1; d1 <= 6; ++d1)
            for (uint8_t d2 = 1; d2 <= 6; ++d2)
                wins += Wins(call, d1, d2) ? 1 : 0;
        return wins * ReturnBasisPoints[size_t(call)] / 36;
    }
}

#endif
