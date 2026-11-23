/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 */

#include "WildernessPouch.h"
#include "WorldPvpRules.h"
#include "WorldPvpWilderness.h"
#include "gtest/gtest.h"
#include <bit>

TEST(WorldPvpRulesTest, VoluntaryHostilityRequiresBothOrdinaryPlayersToBeFlagged)
{
    EXPECT_FALSE(Acore::WorldPvp::AreHostile(false, false, false, false));
    EXPECT_FALSE(Acore::WorldPvp::AreHostile(false, true, false, false));
    EXPECT_FALSE(Acore::WorldPvp::AreHostile(true, false, false, false));
    EXPECT_TRUE(Acore::WorldPvp::AreHostile(true, true, false, false));
}

TEST(WorldPvpRulesTest, FreebornHostilityRespectsProtectedPairs)
{
    EXPECT_TRUE(Acore::WorldPvp::AreHostile(false, false, true, false));
    EXPECT_FALSE(Acore::WorldPvp::AreHostile(true, true, true, true));
}

TEST(WorldPvpRulesTest, OrdinaryFlaggedVictimsAreProtectedByMurderLaw)
{
    EXPECT_TRUE(Acore::WorldPvp::IsMurder(false, false));
    EXPECT_FALSE(Acore::WorldPvp::IsMurder(true, false));
    EXPECT_FALSE(Acore::WorldPvp::IsMurder(false, true));
}

TEST(WorldPvpRulesTest, WildernessFightsAreLawfulAndRetainFreebornProtection)
{
    EXPECT_TRUE(Acore::WorldPvp::AreHostile(false, false, false, false, true));
    EXPECT_FALSE(Acore::WorldPvp::AreHostile(true, true, true, true, true));
    EXPECT_FALSE(Acore::WorldPvp::IsMurder(false, false, true));
}

TEST(WorldPvpRulesTest, WildernessWindowsUseUtcBoundariesAndClampZeroHours)
{
    EXPECT_EQ(Acore::WorldPvp::WildernessWindow(14399, 4), 0u);
    EXPECT_EQ(Acore::WorldPvp::WildernessWindow(14400, 4), 1u);
    EXPECT_EQ(Acore::WorldPvp::WildernessWindow(3600, 0), 1u);
}

TEST(WorldPvpRulesTest, WildernessSelectionIsRepeatableAndCappedByTheZonePool)
{
    EXPECT_EQ(Acore::WorldPvp::WildernessRotationMask(1, 42, 0), 0u);
    EXPECT_EQ(Acore::WorldPvp::WildernessRotationMask(1, 42, 5), 0xFu);

    uint32 const mask = Acore::WorldPvp::WildernessRotationMask(1, 42, 2);
    EXPECT_EQ(std::popcount(mask), 2);
    EXPECT_EQ(Acore::WorldPvp::WildernessRotationMask(1, 42, 2), mask);
}

TEST(WorldPvpRulesTest, WildernessRewardBonusPreservesZeroAndSaturatesMoney)
{
    using Acore::WorldPvp::AddWildernessBonus;
    constexpr uint32 maxAmount = std::numeric_limits<uint32>::max();
    EXPECT_EQ(AddWildernessBonus(0, 25), 0u);
    EXPECT_EQ(AddWildernessBonus(100, 25), 125u);
    EXPECT_EQ(AddWildernessBonus(maxAmount - 1, 25), maxAmount);
}

TEST(WorldPvpRulesTest, WildernessArenaRewardLimitsAccountPairsInEitherDirection)
{
    using Acore::WorldPvp::ClaimWildernessArenaReward;
    EXPECT_FALSE(ClaimWildernessArenaReward(11, 11, 10));
    EXPECT_TRUE(ClaimWildernessArenaReward(11, 22, 10));
    EXPECT_FALSE(ClaimWildernessArenaReward(22, 11, 10));
    EXPECT_TRUE(ClaimWildernessArenaReward(11, 33, 10));
    EXPECT_TRUE(ClaimWildernessArenaReward(22, 11, 11));
    EXPECT_FALSE(ClaimWildernessArenaReward(11, 22, 10));
}

TEST(WorldPvpRulesTest, WildernessGoldPouchRoundsDownAndCapsTheDrop)
{
    using Acore::WorldPvp::WildernessPouchCopper;
    EXPECT_EQ(WildernessPouchCopper(99), 0u);
    EXPECT_EQ(WildernessPouchCopper(100), 1u);
    EXPECT_EQ(WildernessPouchCopper(4999999), 49999u);
    EXPECT_EQ(WildernessPouchCopper(5000000), 50000u);
    EXPECT_EQ(WildernessPouchCopper(std::numeric_limits<uint32>::max()), 50000u);
    EXPECT_EQ(WildernessPouchCopper(49, true), 0u);
    EXPECT_EQ(WildernessPouchCopper(50, true), 1u);
    EXPECT_EQ(WildernessPouchCopper(10000, true), 200u);
    EXPECT_EQ(WildernessPouchCopper(std::numeric_limits<uint32>::max(), true), 100000u);
}

TEST(WorldPvpRulesTest, WildernessDeathXpLossUsesEarnedProgress)
{
    using Acore::WorldPvp::WildernessDeathXpLoss;
    EXPECT_EQ(WildernessDeathXpLoss(0), 0u);
    EXPECT_EQ(WildernessDeathXpLoss(19), 0u);
    EXPECT_EQ(WildernessDeathXpLoss(20), 1u);
    EXPECT_EQ(WildernessDeathXpLoss(12345), 617u);
}

TEST(WorldPvpRulesTest, BloodyAuctionHouseBuybackHasALowerFee)
{
    using Acore::WorldPvp::WildernessAuctionFee;
    EXPECT_EQ(WildernessAuctionFee(1, true), 0u);
    EXPECT_EQ(WildernessAuctionFee(1000, true), 100u);
    EXPECT_EQ(WildernessAuctionFee(1000, false), 250u);
}

TEST(WorldPvpRulesTest, BloodyAuctionHousePublicGoodsCostTheirListedValue)
{
    using Acore::WorldPvp::WildernessItemAuctionFee;
    using Acore::WorldPvp::WildernessItemAuctionValue;
    EXPECT_EQ(WildernessItemAuctionValue(2, 20), 100u);
    EXPECT_EQ(WildernessItemAuctionValue(45, 20), 900u);
    EXPECT_EQ(WildernessItemAuctionValue(std::numeric_limits<uint32>::max(), 2), 8589934590ull);
    EXPECT_EQ(WildernessItemAuctionFee(100, true), 25u);
    EXPECT_EQ(WildernessItemAuctionFee(900, true), 225u);
    EXPECT_EQ(WildernessItemAuctionFee(900, false), 900u);
}

TEST(WorldPvpRulesTest, EachPlayerContributionMustReachOneHundredGold)
{
    EXPECT_FALSE(Acore::WorldPvp::MeetsPlayerBountyMinimum(0));
    EXPECT_FALSE(Acore::WorldPvp::MeetsPlayerBountyMinimum(999999));
    EXPECT_TRUE(Acore::WorldPvp::MeetsPlayerBountyMinimum(1000000));
    EXPECT_TRUE(Acore::WorldPvp::MeetsPlayerBountyMinimum(1000001));
}

TEST(WorldPvpRulesTest, AClaimCanAdvanceAFundedReceiptBeforeReadback)
{
    using Acore::WorldPvp::BountyEscrowState;
    using Acore::WorldPvp::IsBountyWalletChangeCommitted;

    EXPECT_TRUE(IsBountyWalletChangeCommitted(BountyEscrowState::Funded, BountyEscrowState::Claimed));
    EXPECT_TRUE(IsBountyWalletChangeCommitted(BountyEscrowState::Funded, BountyEscrowState::Redeemed));
    EXPECT_TRUE(IsBountyWalletChangeCommitted(BountyEscrowState::Funded, BountyEscrowState::RefundQueued));
    EXPECT_TRUE(IsBountyWalletChangeCommitted(BountyEscrowState::Funded, BountyEscrowState::Refunded));
    EXPECT_FALSE(IsBountyWalletChangeCommitted(BountyEscrowState::Funded, BountyEscrowState::Pending));
    EXPECT_FALSE(IsBountyWalletChangeCommitted(BountyEscrowState::Refunded, BountyEscrowState::Claimed));
    EXPECT_FALSE(IsBountyWalletChangeCommitted(BountyEscrowState::Redeemed, BountyEscrowState::Claimed));
}

TEST(WorldPvpRulesTest, ContractPermissionIsDirectionalAndLimitedToDirectAttacks)
{
    using Acore::WorldPvp::BountyAttackOverride;

    EXPECT_EQ(BountyAttackOverride(false, true, false, false), true);
    EXPECT_EQ(BountyAttackOverride(false, false, true, false), false);
    EXPECT_EQ(BountyAttackOverride(false, true, true, false), true);
    EXPECT_EQ(BountyAttackOverride(false, true, false, true), false);
    EXPECT_EQ(BountyAttackOverride(true, false, true, false), std::nullopt);
    EXPECT_EQ(BountyAttackOverride(false, false, false, false), std::nullopt);
}

TEST(WorldPvpRulesTest, PickpocketRespectsVictimPercentageAndWalletCaps)
{
    using Acore::WorldPvp::PickpocketGoldAmount;

    EXPECT_EQ(PickpocketGoldAmount(99, 50000), 0u);
    EXPECT_EQ(PickpocketGoldAmount(123456, 50000), 1234u);
    EXPECT_EQ(PickpocketGoldAmount(50000000, 50000), 50000u);
    EXPECT_EQ(PickpocketGoldAmount(50000000, 1200), 1200u);
    EXPECT_EQ(PickpocketGoldAmount(50000000, 0), 0u);
}
