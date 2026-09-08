/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify it under
 * the terms of the GNU General Public License as published by the Free Software
 * Foundation; either version 2 of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along with
 * this program. If not, see <http://www.gnu.org/licenses/>.
 */

#include "IntegrationTestFixture.h"
#include "ObjectDefines.h"

TEST_F(IntegrationTestFixture, CollisionHeight_MissingNativeDisplayUsesDefault)
{
    TestCreature* creature = CreateTestCreature(1, 12345, TEST_FACTION_HOSTILE_TO_ALL);
    creature->SetNativeDisplayId(0xFFFFFFFF);

    EXPECT_FLOAT_EQ(creature->GetCollisionHeight(), DEFAULT_COLLISION_HEIGHT);
}

TEST_F(IntegrationTestFixture, CollisionWidth_MissingNativeDisplayUsesObjectSize)
{
    TestCreature* creature = CreateTestCreature(1, 12345, TEST_FACTION_HOSTILE_TO_ALL);
    float objectSize = creature->GetObjectSize();
    creature->SetNativeDisplayId(0xFFFFFFFF);

    EXPECT_FLOAT_EQ(creature->GetCollisionWidth(), objectSize);
}
