/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify it under
 * the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along with
 * this program. If not, see <http://www.gnu.org/licenses/>.
 */

#include "SharedDefines.h"
#include "gtest/gtest.h"

TEST(FreebornTeamTest, HostilityIsSymmetricAndLimitedToFreeborn)
{
    EXPECT_FALSE(IsFreebornHostilePlayerTeamPair(TEAM_ALLIANCE, TEAM_ALLIANCE));
    EXPECT_FALSE(IsFreebornHostilePlayerTeamPair(TEAM_ALLIANCE, TEAM_HORDE));
    EXPECT_FALSE(IsFreebornHostilePlayerTeamPair(TEAM_HORDE, TEAM_ALLIANCE));
    EXPECT_FALSE(IsFreebornHostilePlayerTeamPair(TEAM_HORDE, TEAM_HORDE));

    EXPECT_TRUE(IsFreebornHostilePlayerTeamPair(TEAM_FREEBORN, TEAM_ALLIANCE));
    EXPECT_TRUE(IsFreebornHostilePlayerTeamPair(TEAM_ALLIANCE, TEAM_FREEBORN));
    EXPECT_TRUE(IsFreebornHostilePlayerTeamPair(TEAM_FREEBORN, TEAM_HORDE));
    EXPECT_TRUE(IsFreebornHostilePlayerTeamPair(TEAM_HORDE, TEAM_FREEBORN));
    EXPECT_TRUE(IsFreebornHostilePlayerTeamPair(TEAM_FREEBORN, TEAM_FREEBORN));

    EXPECT_FALSE(IsFreebornHostilePlayerTeamPair(TEAM_FREEBORN, TEAM_NEUTRAL));
}

// Groups, guilds and guild charters are shared with the same kind of team only: a Freeborn never
// shares them with a native team, and natives keep sharing them with each other as before.
TEST(FreebornTeamTest, CooperationIsLimitedToMatchingFreebornState)
{
    EXPECT_TRUE(IsFreebornCooperativeTeamPair(TEAM_ALLIANCE, TEAM_ALLIANCE));
    EXPECT_TRUE(IsFreebornCooperativeTeamPair(TEAM_ALLIANCE, TEAM_HORDE));
    EXPECT_TRUE(IsFreebornCooperativeTeamPair(TEAM_HORDE, TEAM_ALLIANCE));
    EXPECT_TRUE(IsFreebornCooperativeTeamPair(TEAM_HORDE, TEAM_HORDE));

    EXPECT_TRUE(IsFreebornCooperativeTeamPair(TEAM_FREEBORN, TEAM_FREEBORN));

    EXPECT_FALSE(IsFreebornCooperativeTeamPair(TEAM_FREEBORN, TEAM_ALLIANCE));
    EXPECT_FALSE(IsFreebornCooperativeTeamPair(TEAM_ALLIANCE, TEAM_FREEBORN));
    EXPECT_FALSE(IsFreebornCooperativeTeamPair(TEAM_FREEBORN, TEAM_HORDE));
    EXPECT_FALSE(IsFreebornCooperativeTeamPair(TEAM_HORDE, TEAM_FREEBORN));

    // TEAM_NEUTRAL never reaches a player structure, but it must not look Freeborn either.
    EXPECT_TRUE(IsFreebornCooperativeTeamPair(TEAM_NEUTRAL, TEAM_ALLIANCE));
    EXPECT_FALSE(IsFreebornCooperativeTeamPair(TEAM_NEUTRAL, TEAM_FREEBORN));
}

// Quest availability: `AllowableRaces` masks team-side content (Alliance mask 1101, Horde 690), so
// a Freeborn must not be blocked by them, while natives keep matching with their own race.
TEST(FreebornTeamTest, QuestRaceMaskDoesNotBlockFreeborn)
{
    constexpr uint32 ALLIANCE_RACES = 1101;
    constexpr uint32 HORDE_RACES = 690;
    constexpr uint32 NIGHT_ELF = 8;
    constexpr uint32 TAUREN = 32;

    EXPECT_TRUE(SatisfiesQuestRaceMask(TEAM_FREEBORN, HORDE_RACES, NIGHT_ELF));
    EXPECT_TRUE(SatisfiesQuestRaceMask(TEAM_FREEBORN, TAUREN, NIGHT_ELF));
    EXPECT_TRUE(SatisfiesQuestRaceMask(TEAM_FREEBORN, ALLIANCE_RACES, NIGHT_ELF));

    EXPECT_TRUE(SatisfiesQuestRaceMask(TEAM_ALLIANCE, ALLIANCE_RACES, NIGHT_ELF));
    EXPECT_FALSE(SatisfiesQuestRaceMask(TEAM_ALLIANCE, HORDE_RACES, NIGHT_ELF));
    EXPECT_TRUE(SatisfiesQuestRaceMask(TEAM_HORDE, TAUREN, TAUREN));
    EXPECT_FALSE(SatisfiesQuestRaceMask(TEAM_HORDE, NIGHT_ELF, TAUREN));

    // An unrestricted quest stays unrestricted for everyone.
    EXPECT_TRUE(SatisfiesQuestRaceMask(TEAM_HORDE, 0, TAUREN));
}

// Faction-availability conditions: a Freeborn satisfies either side, and is never treated as Horde
// just because its persistent team is not Alliance.
TEST(FreebornTeamTest, TeamConditionsAreSatisfiedByBothSidesForFreeborn)
{
    EXPECT_TRUE(SatisfiesTeamCondition(TEAM_FREEBORN, ALLIANCE));
    EXPECT_TRUE(SatisfiesTeamCondition(TEAM_FREEBORN, HORDE));

    EXPECT_TRUE(SatisfiesTeamCondition(TEAM_ALLIANCE, ALLIANCE));
    EXPECT_FALSE(SatisfiesTeamCondition(TEAM_ALLIANCE, HORDE));
    EXPECT_TRUE(SatisfiesTeamCondition(TEAM_HORDE, HORDE));
    EXPECT_FALSE(SatisfiesTeamCondition(TEAM_HORDE, ALLIANCE));

    // A value that is not a team is not satisfied by the Freeborn both-sides rule.
    EXPECT_FALSE(SatisfiesTeamCondition(TEAM_FREEBORN, 0));
}
