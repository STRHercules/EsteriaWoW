#include "CratePool.h"

#include "gtest/gtest.h"

using namespace EsteriaCrates;

TEST(EsteriaCratePool, EveryRollMapsToExactlyItsWeight)
{
    // The Starfall Cache test pool: 7x12%, 1x10%, 3x2% in basis points.
    std::vector<uint32_t> const weights = { 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1000, 200, 200, 200 };
    uint32_t const total = TotalWeight(weights);
    ASSERT_EQ(total, 10000u);

    std::vector<uint32_t> hits(weights.size(), 0);
    for (uint32_t roll = 1; roll <= total; ++roll)
        ++hits[Pick(weights, roll)];
    EXPECT_EQ(hits, weights);
}

TEST(EsteriaCratePool, RejectsBrokenPools)
{
    EXPECT_EQ(TotalWeight({}), 0u);
    EXPECT_EQ(TotalWeight({ 5, 0, 5 }), 0u);
    EXPECT_EQ(TotalWeight({ 0xFFFFFFFFu, 1 }), 0u);
    EXPECT_EQ(TotalWeight({ 1 }), 1u);
}
