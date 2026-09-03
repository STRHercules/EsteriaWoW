/*
 * Copyright (C) 2016+ AzerothCore <www.azerothcore.org>, released under GNU AGPL v3 license, you may redistribute it
 * and/or modify it under version 3 of the License, or (at your option), any later version.
 */

#include "gtest/gtest.h"

#include "Ai/Dungeon/DungeonClear/Data/FightInPlaceRegistry.h"

// Selin Fireheart's room (Magisters' Terrace, map 585). The registry must veto the
// advanced pull for anything inside the room (X>216, the boss's own CanAIAttack
// plane) while leaving the antechamber and the instance's other encounters pullable.

TEST(FightInPlaceTest, SelinRoomGuardsAreInTheZone)
{
    // The three room-guard spawn extremes (24688/24689/24690): X 222.3-231.7,
    // Y -23.0..+23.8. Every one must read as no-pull.
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(585, 222.3f, -18.0f));
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(585, 231.7f, 2.6f));
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(585, 227.3f, -23.0f));
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(585, 228.0f, 23.8f));
    // Selin himself and the deep end of his room.
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(585, 242.1f, 0.3f));
}

TEST(FightInPlaceTest, AntechamberStaysPullable)
{
    // Sunblade trash top out at X=182.3 — below Selin's X=216 gate, so a normal
    // pull must still fire there. The camp the stuck runs landed on (X~197) is also
    // outside the room and must not be swallowed.
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(585, 182.3f, 0.0f));
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(585, 197.0f, 7.0f));
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(585, 216.0f - 0.01f, 0.0f));
}

TEST(FightInPlaceTest, OtherMgtEncountersAreNotVetoed)
{
    // Priestess Delrissa (X=126.9) — far west, below the gate.
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(585, 126.9f, 19.2f));
    // Vexallus (X=231.4 but Y=-214.3) — inside the X band but far outside the Y band.
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(585, 231.4f, -214.3f));
}

TEST(FightInPlaceTest, OtherMapsAreNeverVetoed)
{
    // The same coordinates on any other map carry no zone.
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(0, 242.0f, 0.0f));
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(560, 230.0f, 0.0f));
}

TEST(FightInPlaceTest, ZoneBoundsAreInclusive)
{
    // The gate plane (X=216) and the Y edges are inside the room (closed interval).
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(585, 216.0f, 0.0f));
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(585, 260.0f, 45.0f));
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(585, 240.0f, -45.0f));
    // Just past the far/side walls: out.
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(585, 260.01f, 0.0f));
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(585, 240.0f, 45.01f));
}

// Azjol-Nerub's Hadronox shaft (map 601). The crusher packs are TempSummons of
// the boss, and boss_hadronox::SummonedCreatureEvade resets the WHOLE encounter
// the moment one of them evades — so an advanced pull that drags a pack member
// off its home is a run-ender, not a tuning question.

TEST(FightInPlaceTest, HadronoxShaftIsNoPull)
{
    // The z~733 platform the packs walk down to and the fight ends on.
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(601, 530.4f, 560.0f));
    // The two upper ledges packs 2 and 3 spawn on.
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(601, 493.5f, 603.3f));
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(601, 567.0f, 602.6f));
    // Hadronox's own spawn ledge and the pit floor below it.
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(601, 522.5f, 544.9f));
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(601, 522.0f, 548.0f));
}

TEST(FightInPlaceTest, AzjolNerubKeepsItsOtherEncountersPullable)
{
    // Krik'thir (529.6, 646.2) and his watcher trash out to y~706 sit above the
    // y=625 ceiling and must keep the ordinary pull.
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(601, 529.6f, 646.2f));
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(601, 529.0f, 706.9f));
    // Anub'arak (551, 248) and his Prime Guards (y 341) are below the y=480 floor.
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(601, 551.0f, 248.3f));
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(601, 542.0f, 341.4f));
    // The zone-in.
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(601, 413.3f, 796.0f));
}


// Trollgore's arena (Drak'Tharon Keep, map 600). A third reason for the same
// rule: this boss polices his own room COORDINATES. boss_trollgore's
// CheckInRoom() is `Y >= -700 && Y <= -628`, and UpdateAI calls
// EnterEvadeMode(EVADE_REASON_BOUNDARY) every tick it fails — so a pull-to-camp
// that drags him or his pack a few yards south toward the Novos corridor
// (which leaves the band at y ~ -705) evades the boss outright.

TEST(FightInPlaceTest, TrollgoreArenaIsNoPull)
{
    // The boss's own spawn.
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(600, -266.2f, -660.1f));
    // The three Drakkari Invader landing spots 12-16yd east of him — the whole
    // point is that this fight happens where it stands.
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(600, -250.0f, -672.92f));
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(600, -254.0f, -665.92f));
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(600, -250.0f, -658.92f));
    // The band mirrors his own CheckInRoom exactly, inclusive at both edges.
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(600, -266.0f, -700.0f));
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(600, -266.0f, -628.0f));
}

TEST(FightInPlaceTest, TrollgoreBoxStopsShortOfTheGhoulPit)
{
    // Column probes along y = -660 (his latitude): the arena floor is z 24-26.6
    // over x -277..-245, the ramp drops through z 20.4 / 15.3 at x -278 / -280,
    // and the ghoul pit proper is z 11.3 at x -300 — 13yd below the arena. A
    // FightInPlaceZone is XY-only, so the box has to stop before the pit or the
    // clear would be forbidden from pulling on the way UP to Trollgore.
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(600, -276.0f, -660.0f));   // arena floor
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(600, -282.0f, -660.0f));   // ramp lip (edge)
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(600, -290.0f, -660.0f));  // ramp, pullable
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(600, -300.0f, -660.0f));  // ghoul pit
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(600, -336.3f, -633.4f));  // pit, on route
}

TEST(FightInPlaceTest, DrakTharonKeepsItsOtherEncountersPullable)
{
    // The Darkweb corridor to Novos leaves the Y band at y ~ -705.
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(600, -259.8f, -705.4f));
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(600, -290.0f, -717.5f));
    // Novos' chamber, King Dred's pen and Tharon'ja's platform.
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(600, -379.3f, -737.7f));
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(600, -544.9f, -697.0f));
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(600, -236.8f, -675.4f));
    // The zone-in and the lower hall the route crosses on the way in.
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(600, -517.3f, -488.0f));
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(600, -441.9f, -603.7f));
}

TEST(FightInPlaceTest, TrollgoreBoxOverlapsTharonJaPlatformAndThatIsHarmless)
{
    // A FightInPlaceZone is XY-only and Tharon'ja's platform sits 107yd directly
    // ABOVE Trollgore's arena, so its western half is inside the box. The box
    // cannot be narrowed out of it: the three Drakkari Invader landing spots are
    // at x -250 / -254, so maxX cannot go west of -250, and the platform starts
    // at x -261.8. Pinned here so the overlap is a recorded decision rather than
    // something a later reader "fixes" by shrinking the box off the invaders.
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(600, -250.0f, -672.92f))
        << "the invader landing spot is the constraint on maxX";
    EXPECT_TRUE(FightInPlaceRegistry::IsNoPullZone(600, -250.0f, -670.0f))
        << "so the platform's western half is inside the box too";

    // Harmless because nothing up there is pullable: Tharon'ja himself, and four
    // Drakuru Event Invisman triggers (28492) that are faction 35 and
    // NOT_SELECTABLE. His own spawn is east of the box in any case.
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(600, -236.83f, -675.41f))
        << "Tharon'ja's own anchor is outside the box (x > -240)";
    // And the approach to him leaves the box at every waypoint, in x or in y.
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(600, -288.0f, -693.3f));  // DK ledge
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(600, -274.6f, -734.7f));  // final climb
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(600, -251.9f, -733.1f));
    EXPECT_FALSE(FightInPlaceRegistry::IsNoPullZone(600, -238.1f, -697.8f));
}
