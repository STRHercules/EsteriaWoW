/*
 * Copyright (C) 2016+ AzerothCore <www.azerothcore.org>, released under GNU AGPL v3 license, you may redistribute it
 * and/or modify it under version 3 of the License, or (at your option), any later version.
 */

#include "gtest/gtest.h"

#include "Ai/Dungeon/DungeonClear/Data/DcNeverTargetRegistry.h"

// The Nexus's Crystalline Frayer is the row this registry exists for. It cannot
// be killed while Ormorok lives (npc_crystalline_frayer::DamageTaken discards the
// lethal hit and parks the mob in a 90s seed pod, from which it returns at full
// health), and instance_nexus::KillAllFrayers kills every one of them the moment
// Ormorok dies — so no live frayer is ever worth the clear's attention, and one
// that IS killable is already a corpse.
TEST(DcNeverTargetRegistryTest, NexusCrystallineFrayerIsNeverAClearTarget)
{
    EXPECT_TRUE(DcNeverTargetRegistry::IsNeverTarget(576, 26793));
}

TEST(DcNeverTargetRegistryTest, TheRowIsScopedToItsOwnMapAndEntry)
{
    // Same entry on another map, and another entry on the same map, must both
    // pass — this table is a scalpel, not a species ban.
    EXPECT_FALSE(DcNeverTargetRegistry::IsNeverTarget(575, 26793));
    EXPECT_FALSE(DcNeverTargetRegistry::IsNeverTarget(576, 26794));  // Ormorok himself
    EXPECT_FALSE(DcNeverTargetRegistry::IsNeverTarget(576, 26723));  // Keristrasza
    EXPECT_FALSE(DcNeverTargetRegistry::IsNeverTarget(0, 0));
}

// The heroic twin (30528) must NOT be listed: Creature::InitEntry resolves
// difficulty_entry_1 into m_creatureInfo but calls SetEntry with the NORMAL
// entry, so a heroic frayer still answers to 26793. A row for 30528 would be
// dead data that reads as coverage.
TEST(DcNeverTargetRegistryTest, HeroicTwinIsNotListedBecauseGetEntryStaysNormal)
{
    EXPECT_FALSE(DcNeverTargetRegistry::IsNeverTarget(576, 30528));
}

// --- Ahn'kahet (619) — Jedoga Shadowseeker's ritual staging ----------------
//
// At 55% HP she goes REACT_PASSIVE + NOT_SELECTABLE | NON_ATTACKABLE with
// `damage = 0` and takes off to sacrifice a volunteer. With no boss to hit the
// clear's non-combat ladder takes over, and the corridor scan finds the ring of
// staging mobs the encounter has just placed around the arena. Live
// (tr-20260825-224456-8, tank Wieron): "pull target vetoed — Jedoga
// Shadowseeker" followed by 25 consecutive
// "blocking-trash: 3 candidate(s) in band -> Entry: 30111 at 52.6yd".
//
// Jedoga has combat movement off and is passive, so her threat list empties
// behind the departing party and she EnterEvadeMode(NO_HOSTILES)s —
// DespawnAll + Reset, which re-summons the fifteen Twilight Initiates. The
// clear cannot recover: map-619 event 3 latched Done and is not Repeatable, so
// nothing clears them again and the boss never comes down.
TEST(DcNeverTargetRegistryTest, AhnkahetRitualStagingIsNeverAClearTarget)
{
    EXPECT_TRUE(DcNeverTargetRegistry::IsNeverTarget(619, 30111))
        << "Twilight Worshipper — the kneeling congregation summoned around the "
           "arena on engage, up to 65yd out";
    EXPECT_TRUE(DcNeverTargetRegistry::IsNeverTarget(619, 30385))
        << "Twilight Volunteer — 24 of 25 are permanently NOT_SELECTABLE and "
           "immune; the 25th walks INTO the party on its own";
}

// The rows must not blunt the encounter the party actually has to fight, and
// must not leak onto the neighbouring map.
TEST(DcNeverTargetRegistryTest, AhnkahetRowsAreScopedToTheStagingMobs)
{
    // The FIFTEEN Twilight Initiates are the gate on Jedoga descending — map-619
    // event 3 sweeps them by entry. Listing 30114 here would make that sweep
    // permanently blind and wedge the run at an immune boss, which is the exact
    // failure the 30111/30385 rows exist to prevent.
    EXPECT_FALSE(DcNeverTargetRegistry::IsNeverTarget(619, 30114))
        << "the initiates ARE the objective — they must stay targetable";

    // The bosses themselves, and the approach trash that shares the chamber.
    EXPECT_FALSE(DcNeverTargetRegistry::IsNeverTarget(619, 29310));  // Jedoga
    EXPECT_FALSE(DcNeverTargetRegistry::IsNeverTarget(619, 30179));  // Twilight Apostle
    EXPECT_FALSE(DcNeverTargetRegistry::IsNeverTarget(619, 30319));  // Twilight Darkcaster

    // Azjol-Nerub is the other half of this instance pair and shares nothing.
    EXPECT_FALSE(DcNeverTargetRegistry::IsNeverTarget(601, 30111));
    EXPECT_FALSE(DcNeverTargetRegistry::IsNeverTarget(601, 30385));
}

// --- Drak'Tharon Keep (600) — the Novos gate's softlock -------------------
//
// Novos Summon Target (27583) is a "trigger" by convention only: unit_flags 0,
// flags_extra 128, faction 14, rank 1 elite, level 74 — fully selectable and
// fully attackable, and nothing in mod-playerbots or mod-dungeon-clear tests
// IsTrigger(). Two are summoned into the chamber's opposite corners at the pull.
//
// The four Crystal Handlers are spawned by `target->CastSpell(target,
// SPELL_SUMMON_CRYSTAL_HANDLER, ...)` on these two, alternating, at 16s / 32s /
// 48s / 64s. A dead unit cannot cast, and a Crystal Handler's death is the ONLY
// thing that removes a Beam Channel (52106) from Novos — whose 70s gate task
// tests `me->HasAura(SPELL_BEAM_CHANNEL)` and repeats every 2s FOREVER while it
// holds. So killing one of these permanently prevents Novos ever becoming
// attackable: the encounter is unwinnable until the instance resets.
TEST(DcNeverTargetRegistryTest, DrakTharonNovosSummonTargetIsNeverAClearTarget)
{
    EXPECT_TRUE(DcNeverTargetRegistry::IsNeverTarget(600, 27583))
        << "killing a Novos Summon Target stops a Crystal Handler spawning, which "
           "leaves a Beam Channel that is never silenced, which softlocks the gate";
}

TEST(DcNeverTargetRegistryTest, DrakTharonRowDoesNotBanTheRestOfTheMap)
{
    // The things the clear MUST still fight on map 600.
    EXPECT_FALSE(DcNeverTargetRegistry::IsNeverTarget(600, 26627))
        << "Crystal Handler — killing all four IS the gate";
    EXPECT_FALSE(DcNeverTargetRegistry::IsNeverTarget(600, 27598))
        << "Fetid Troll Corpse — the phase-1 add stream that walks into the camp";
    EXPECT_FALSE(DcNeverTargetRegistry::IsNeverTarget(600, 26631))  // Novos
        << "the boss";
    // Deliberately unlisted: Darkweb Victim (27909). Killing one hands the party a
    // free level-76 elite (49960 rolls 49958/49959 at the corpse), but five of the
    // six are 20yd+ off the Trollgore -> Novos route. Add the row only if run data
    // shows the clear detouring to them; see the note in the registry.
    EXPECT_FALSE(DcNeverTargetRegistry::IsNeverTarget(600, 27909));
    // Scoping, same as the Nexus row above.
    EXPECT_FALSE(DcNeverTargetRegistry::IsNeverTarget(601, 27583));
}
