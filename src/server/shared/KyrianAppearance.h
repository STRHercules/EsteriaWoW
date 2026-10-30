#ifndef ESTERIA_KYRIAN_APPEARANCE_H
#define ESTERIA_KYRIAN_APPEARANCE_H

#include <array>
#include <cstdint>

namespace CreatureAppearance
{
    // Legacy wire values retain their meaning; logical controls split hair from wings.
    template <std::size_t N>
    constexpr std::array<std::uint8_t, N> DecodeKyrian(unsigned sex, std::array<std::uint8_t, N> fields)
    {
        unsigned const armorCount = sex ? 5 : 10;
        if (fields[4] >= 80)
        {
            // New wire layout: armor/hair in byte 2, wings in byte 3.
            fields[4] -= 80;
            return fields;
        }
        unsigned const packed = fields[3];
        unsigned const oldCount = sex ? 8 : 12;
        unsigned const legacyHairCount = sex ? 2 : 7;
        unsigned const legacyPackedCount = sex ? 16 : 56;
        unsigned wing, hair;
        if (packed >= legacyPackedCount)
        {
            unsigned const extra = packed - legacyPackedCount;
            if (extra < 3 * legacyHairCount)
            {
                wing = 8 + extra % 3;
                hair = extra / 3;
            }
            else
            {
                wing = (extra - 3 * legacyHairCount) % 11;
                hair = legacyHairCount + (extra - 3 * legacyHairCount) / 11;
            }
        }
        else if (packed < oldCount)
        {
            wing = packed % 4;
            hair = packed / 4;
        }
        else if (sex || packed < 24)
        {
            wing = 4 + (packed - oldCount) % 4;
            hair = (packed - oldCount) / 4;
        }
        else
        {
            wing = (packed - 24) % 8;
            hair = 3 + (packed - 24) / 8;
        }
        unsigned const theme = fields[4] / 16;
        if (theme > 0 && theme < 5)
        {
            wing = 3 + theme;
            if (!sex)
            {
                fields[0] = fields[2] = 2 + theme;
                hair = 2 + theme;
            }
        }
        fields[2] += armorCount * hair;
        fields[3] = wing;
        fields[4] %= 16;
        return fields;
    }

    template <std::size_t N>
    constexpr std::array<std::uint8_t, N> EncodeKyrian(unsigned sex, std::array<std::uint8_t, N> fields)
    {
        unsigned const armorCount = sex ? 5 : 10;
        unsigned const wing = fields[3];
        unsigned const hair = fields[2] / armorCount;
        if (wing >= 11 || hair >= (sex ? 5u : 10u))
        {
            fields[4] = 80 + fields[4] % 16;
            return fields;
        }
        fields[2] %= armorCount;
        unsigned const legacyHairCount = sex ? 2 : 7;
        if (wing >= 8 || hair >= legacyHairCount)
        {
            unsigned const extra = hair < legacyHairCount ? hair * 3 + wing - 8
                : 3 * legacyHairCount + (hair - legacyHairCount) * 11 + wing;
            fields[3] = (sex ? 16 : 56) + extra;
        }
        else if (wing < 4 && hair < (sex ? 2u : 3u))
            fields[3] = wing + 4 * hair;
        else if (sex || hair < 3)
            fields[3] = (sex ? 8 : 12) + 4 * hair + wing - 4;
        else
            fields[3] = 24 + 8 * (hair - 3) + wing;
        fields[4] %= 16;
        return fields;
    }

    static_assert(DecodeKyrian(0, std::array<std::uint8_t, 5>{2, 14, 2, 11, 15})[2] == 22);
    static_assert(EncodeKyrian(0, std::array<std::uint8_t, 5>{2, 14, 22, 3, 15})[3] == 11);
    static_assert(DecodeKyrian(1, std::array<std::uint8_t, 5>{22, 19, 94, 24, 95})[4] == 15);
    static_assert(EncodeKyrian(1, std::array<std::uint8_t, 5>{22, 19, 94, 24, 15})[4] == 95);

}

#endif
