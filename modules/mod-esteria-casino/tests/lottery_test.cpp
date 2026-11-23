#include "Lottery.h"

#include "gtest/gtest.h"

#include <random>
#include <set>

using namespace EsteriaCasino::Lottery;

TEST(EsteriaCasinoLottery, ParsesOnlyValidPicks)
{
    auto pick = Parse("19,3,12,7");
    ASSERT_TRUE(pick.has_value());
    EXPECT_EQ(Text(*pick), "3,7,12,19") << "sorted";
    EXPECT_FALSE(Parse("1,2,3").has_value());
    EXPECT_FALSE(Parse("1,2,3,4,5").has_value());
    EXPECT_FALSE(Parse("1,2,3,3").has_value()) << "numbers must differ";
    EXPECT_FALSE(Parse("0,2,3,4").has_value());
    EXPECT_FALSE(Parse("1,2,3,21").has_value());
    EXPECT_FALSE(Parse("1,2,,4").has_value());
    EXPECT_FALSE(Parse("1,2,3,x").has_value());
    EXPECT_FALSE(Parse("").has_value());
}

TEST(EsteriaCasinoLottery, DrawsFourDifferentNumbersEvenly)
{
    std::mt19937 rng(42);
    auto random = [&rng](uint32_t n) { return uint32_t(rng() % n); };
    std::array<int, HIGHEST + 1> seen {};
    for (int i = 0; i < 20000; ++i)
    {
        Numbers const n = Draw(random);
        std::set<int> distinct(n.begin(), n.end());
        ASSERT_EQ(distinct.size(), size_t(PICK));
        for (uint8_t v : n)
        {
            ASSERT_GE(v, 1);
            ASSERT_LE(v, HIGHEST);
            ++seen[v];
        }
    }
    // Each number should appear about 20000 * 4 / 20 = 4000 times.
    for (int v = 1; v <= HIGHEST; ++v)
        EXPECT_TRUE(seen[v] > 3600 && seen[v] < 4400) << v;
}

TEST(EsteriaCasinoLottery, PrizesComeOnlyFromThePool)
{
    Numbers const drawn = *Parse("2,5,9,14");
    std::vector<Numbers> const tickets = { *Parse("2,5,9,14"), *Parse("2,5,9,14"), *Parse("2,5,9,20"),
                                           *Parse("1,3,4,6") };
    Payout p = Settle(tickets, drawn, 1000001, 10000);
    EXPECT_EQ(p.smallWinners, 1);
    EXPECT_EQ(p.jackpotWinners, 2);
    EXPECT_EQ(p.smallEach, 10000u);
    EXPECT_EQ(p.jackpotEach, (1000001u - 10000u) / 2) << "two winners split the jackpot";
    EXPECT_EQ(p.prizes[0], p.jackpotEach);
    EXPECT_EQ(p.prizes[2], 10000u);
    EXPECT_EQ(p.prizes[3], 0u);
    EXPECT_EQ(p.paid + p.rollover, 1000001u);
    EXPECT_EQ(p.rollover, 1u) << "the odd copper stays in the pool";

    // No jackpot winner: everything after the small prizes rolls over.
    p = Settle({ *Parse("2,5,9,20") }, drawn, 50000, 10000);
    EXPECT_EQ(p.paid, 10000u);
    EXPECT_EQ(p.rollover, 40000u);

    // A thin pool shrinks the small prizes evenly instead of overpaying.
    p = Settle({ *Parse("2,5,9,20"), *Parse("2,5,14,20"), *Parse("5,9,14,1") }, drawn, 9000, 10000);
    EXPECT_EQ(p.smallEach, 3000u);
    EXPECT_EQ(p.paid, 9000u);
    EXPECT_EQ(p.rollover, 0u);

    EXPECT_EQ(Settle({}, drawn, 777, 10).rollover, 777u);
}
