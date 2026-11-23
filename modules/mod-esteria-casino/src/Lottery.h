/* Lottery rules, kept free of game types so they can be unit tested.
 *
 * A ticket is four different numbers from 1 to 20. A draw picks four. Matching three wins a fixed prize; matching
 * all four shares the jackpot. Prizes come only from the pool: three-number prizes are paid first (shrunk evenly
 * if the pool can't cover them all), the jackpot winners split what is left, and with no jackpot winner the pool
 * rolls over to the next draw.
 */
#ifndef ESTERIA_CASINO_LOTTERY_H
#define ESTERIA_CASINO_LOTTERY_H

#include <algorithm>
#include <array>
#include <cstdint>
#include <functional>
#include <optional>
#include <string>
#include <vector>

namespace EsteriaCasino::Lottery
{
    constexpr int PICK = 4;
    constexpr int HIGHEST = 20;
    // C(20, 4) = 4845 tickets: one wins the jackpot, 4 * 16 = 64 match exactly three.
    constexpr uint32_t COMBINATIONS = 4845;

    using Numbers = std::array<uint8_t, PICK>; // ascending

    // "3,7,12,19" in any order; nullopt unless it is four different numbers in range.
    inline std::optional<Numbers> Parse(std::string const& text)
    {
        Numbers out {};
        size_t count = 0, start = 0;
        while (start <= text.size())
        {
            size_t const comma = text.find(',', start);
            std::string const part = text.substr(start, comma == std::string::npos ? std::string::npos : comma - start);
            if (part.empty() || part.size() > 2 || count >= PICK ||
                part.find_first_not_of("0123456789") != std::string::npos)
                return std::nullopt;
            int const n = std::stoi(part);
            if (n < 1 || n > HIGHEST)
                return std::nullopt;
            out[count++] = uint8_t(n);
            if (comma == std::string::npos)
                break;
            start = comma + 1;
        }
        if (count != PICK)
            return std::nullopt;
        std::sort(out.begin(), out.end());
        if (std::adjacent_find(out.begin(), out.end()) != out.end())
            return std::nullopt;
        return out;
    }

    inline std::string Text(Numbers const& n)
    {
        std::string out;
        for (uint8_t v : n)
            out += (out.empty() ? "" : ",") + std::to_string(v);
        return out;
    }

    using RandomBelow = std::function<uint32_t(uint32_t)>;

    // Four different numbers, each set equally likely.
    inline Numbers Draw(RandomBelow const& random)
    {
        std::array<uint8_t, HIGHEST> pool {};
        for (int i = 0; i < HIGHEST; ++i)
            pool[i] = uint8_t(i + 1);
        for (int i = 0; i < PICK; ++i)
            std::swap(pool[i], pool[i + random(uint32_t(HIGHEST - i))]);
        Numbers out {};
        std::copy(pool.begin(), pool.begin() + PICK, out.begin());
        std::sort(out.begin(), out.end());
        return out;
    }

    inline int Matches(Numbers const& ticket, Numbers const& drawn)
    {
        int n = 0;
        for (uint8_t v : ticket)
            n += std::binary_search(drawn.begin(), drawn.end(), v) ? 1 : 0;
        return n;
    }

    struct Payout
    {
        std::vector<uint64_t> prizes; // per ticket, same order as the input
        uint64_t smallEach = 0;
        uint64_t jackpotEach = 0;
        int smallWinners = 0;
        int jackpotWinners = 0;
        uint64_t paid = 0;
        uint64_t rollover = 0; // what stays in the pool
    };

    inline Payout Settle(std::vector<Numbers> const& tickets, Numbers const& drawn, uint64_t pool, uint64_t smallPrize)
    {
        Payout p;
        p.prizes.assign(tickets.size(), 0);
        for (Numbers const& t : tickets)
        {
            int const m = Matches(t, drawn);
            p.smallWinners += m == 3 ? 1 : 0;
            p.jackpotWinners += m == 4 ? 1 : 0;
        }
        uint64_t left = pool;
        if (p.smallWinners)
            p.smallEach = std::min<uint64_t>(smallPrize, left / p.smallWinners);
        left -= p.smallEach * p.smallWinners;
        if (p.jackpotWinners)
            p.jackpotEach = left / p.jackpotWinners;
        left -= p.jackpotEach * p.jackpotWinners;
        for (size_t i = 0; i < tickets.size(); ++i)
        {
            int const m = Matches(tickets[i], drawn);
            p.prizes[i] = m == 4 ? p.jackpotEach : m == 3 ? p.smallEach : 0;
        }
        p.paid = pool - left;
        p.rollover = left;
        return p;
    }
}

#endif
