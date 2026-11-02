/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program. If not, see <http://www.gnu.org/licenses/>.
 */

#include "PerkRules.h"
#include "gtest/gtest.h"

using namespace EsteriaPerks;
using namespace EsteriaPerkWire;

namespace
{
    constexpr uint8_t Warrior = 1, Mage = 8;
    Options const Live{};
    Options const Dev{ true };

    int At(uint8_t id) { return IndexOf(id); }
}

TEST(PerkRulesTest, PointsByLevel)
{
    EXPECT_EQ(Earned(1), 0);
    EXPECT_EQ(Earned(9), 0);
    EXPECT_EQ(Earned(10), 1);
    EXPECT_EQ(Earned(14), 1);
    EXPECT_EQ(Earned(15), 2);
    EXPECT_EQ(Earned(79), 14);
    EXPECT_EQ(Earned(80), 15);
    EXPECT_EQ(Earned(81), 15);
    EXPECT_EQ(Earned(255), 15);
}

TEST(PerkRulesTest, CatalogueHasFiftyFourUniqueCards)
{
    EXPECT_EQ(CardCount, 54u);
    for (size_t i = 0; i < CardCount; ++i)
    {
        EXPECT_EQ(IndexOf(Cards[i].id), int(i));
        EXPECT_EQ(Cards[i].path, Cards[i].id / 10);
    }
}

TEST(PerkRulesTest, BuyInOrder)
{
    Ranks ranks{};
    EXPECT_EQ(Check(ranks, At(Surefooted), 1, 9, Warrior, Live), Level);
    EXPECT_EQ(Check(ranks, At(Surefooted), 2, 10, Warrior, Live), Rank);
    EXPECT_EQ(Check(ranks, At(Surefooted), 1, 10, Warrior, Live), Ok);
    ranks[At(Surefooted)] = 1;
    EXPECT_EQ(Check(ranks, At(Surefooted), 1, 10, Warrior, Live), Rank); // a double click
    EXPECT_EQ(Check(ranks, At(Surefooted), 2, 14, Warrior, Live), Points);
    EXPECT_EQ(Check(ranks, At(Surefooted), 2, 15, Warrior, Live), Ok);
    ranks[At(Surefooted)] = 2;
    EXPECT_EQ(Check(ranks, At(Surefooted), 3, 80, Warrior, Live), Rank);
    EXPECT_EQ(Check(ranks, -1, 1, 80, Warrior, Live), Unknown);
}

TEST(PerkRulesTest, PreviewsOnlyWithSellPlanned)
{
    Ranks ranks{};
    EXPECT_EQ(Check(ranks, At(53), 1, 80, Warrior, Live), Planned);
    EXPECT_EQ(Check(ranks, At(53), 1, 80, Warrior, Dev), Ok);
}

TEST(PerkRulesTest, TierGates)
{
    Ranks ranks{};
    // Specialist: level 30 and two points in the path.
    EXPECT_EQ(Check(ranks, At(14), 1, 29, Warrior, Dev), Level);
    EXPECT_EQ(Check(ranks, At(14), 1, 30, Warrior, Dev), PathPoints);
    ranks[At(11)] = 1;
    ranks[At(21)] = 1; // another path's points do not count
    EXPECT_EQ(Check(ranks, At(14), 1, 30, Warrior, Dev), PathPoints);
    ranks[At(12)] = 1;
    EXPECT_EQ(Check(ranks, At(14), 1, 30, Warrior, Dev), Ok);
}

TEST(PerkRulesTest, Legendary)
{
    Ranks ranks{};
    ranks[At(11)] = 2;
    ranks[At(12)] = 2;
    ranks[At(13)] = 2;
    EXPECT_EQ(Check(ranks, At(19), 1, 70, Warrior, Dev), Ok);
    EXPECT_EQ(Check(ranks, At(19), 1, 70, Warrior, Live), Feat);
    EXPECT_EQ(Cost(Cards[At(19)]), 2);
    ranks[At(19)] = 1;
    ranks[At(1)] = 2;
    ranks[At(2)] = 2;
    ranks[At(3)] = 2;
    EXPECT_EQ(Check(ranks, At(9), 1, 80, Warrior, Dev), LegendaryOwned);
    // Six path points plus the two-point legendary need eight of the points earned.
    Ranks one{};
    one[At(11)] = 2;
    one[At(12)] = 2;
    one[At(13)] = 2;
    EXPECT_EQ(Spent(one), 6);
    EXPECT_EQ(Check(one, At(19), 1, 70, Warrior, Dev), Ok); // 13 earned at 70
}

TEST(PerkRulesTest, ClassFilter)
{
    Ranks ranks{};
    ranks[At(1)] = 2;
    EXPECT_EQ(Check(ranks, At(5), 1, 30, Warrior, Dev), Class);
    EXPECT_EQ(Check(ranks, At(5), 1, 30, Mage, Dev), Ok);
}

TEST(PerkRulesTest, RespecCost)
{
    EXPECT_EQ(RespecCost(0, 80), 0u);
    EXPECT_EQ(RespecCost(1, 20), 100000u);
    EXPECT_EQ(RespecCost(5, 80), 400000u);
    EXPECT_EQ(RespecCost(1, 255), 500000u);
}
