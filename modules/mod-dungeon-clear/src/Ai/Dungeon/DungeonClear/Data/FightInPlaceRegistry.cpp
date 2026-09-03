/*
 * Copyright (C) 2016+ AzerothCore <www.azerothcore.org>, released under GNU AGPL v3 license, you may redistribute it
 * and/or modify it under version 3 of the License, or (at your option), any later version.
 */

#include "FightInPlaceRegistry.h"

namespace
{
    // The rooms, sized off live spawn data (acore_world.creature on map 585):
    //   * Selin Fireheart spawns at X=242.1, Y=0.3; his CanAIAttack plane is X>216.
    //   * His 14 room-guard spawns (24688/24689/24690) sit at X 222.3-231.7,
    //     Y -23.0..+23.8 — the whole occupied room.
    //   * The antechamber Sunblade trash top out at X=182.3 (all X<216), so they
    //     stay normally pullable — the box floor at X=216 (Selin's own gate) keeps
    //     them out.
    //   * The instance's other encounters are far outside: Priestess Delrissa at
    //     X=126.9, and Vexallus at X=231.4 but Y=-214.3 — the Y band [-45,45]
    //     excludes him cleanly.
    // So [216,260] x [-45,45] is exactly Selin's room and nothing else.
    // Azjol-Nerub (601) — Hadronox's shaft. A different reason for the same rule:
    // here the boss does not gate on the party's position, her ADDS gate on their
    // own. The crusher packs are TempSummons of boss_hadronox, and
    // boss_hadronox::SummonedCreatureEvade calls EnterEvadeMode on HER the moment
    // any Anub'ar Crusher / Champion / Crypt Fiend / Necromancer summon evades.
    // Since a pack evading is a full encounter reset — Reset() re-summons pack 1
    // and the three swarm triggers and the whole crusher count starts over — an
    // advanced pull that drags a pack member off its MovePoint home is not a
    // tuning question, it is the run.
    //
    // The box is the whole shaft: the two upper ledges the packs spawn on
    // (493,603) and (567,603), the z~733 platform they walk down to, Hadronox's
    // z~675 ledge and the z~648 pit floor below it. Krik'thir sits at
    // (529.6, 646.2) with his watchers and trash out to y 706, so the y ceiling
    // at 625 keeps his whole encounter normally pullable.
    //
    // KNOWN AND ACCEPTED OVERLAP: a FightInPlaceZone is XY-only, and the lower
    // kingdom lies DIRECTLY BENEATH this shaft, so the box also covers the lake
    // and the bank beside it. Nothing of consequence lives there — the only
    // spawns in that XY footprint below are Anub'ar Brood Keepers (29340, rank 5
    // trivial), the decorative spiders the party walks past. Anub'arak (551,
    // 248), his Prime Guards (y 341) and the exit are all at y < 480 and stay
    // normally pullable, and the drop landing (544.18, 481.26, 288.98) sits 1yd
    // inside the southern edge — the party is out of the box within a step.
    //
    // Drak'Tharon Keep (600) — Trollgore's arena. The THIRD reason for the same
    // rule, and the bluntest: this boss policices his own room coordinates.
    // boss_trollgore's CheckInRoom() override is
    //
    //     return (me->GetPositionY() >= -700.0f && me->GetPositionY() <= -628.0f);
    //
    // and UpdateAI calls EnterEvadeMode(EVADE_REASON_BOUNDARY) EVERY TICK it
    // fails. His arena is 72 yards of Y, and the corridor to Novos leaves it at
    // y ~ -705 — so a pull-to-camp that drags him or his pack even a few yards
    // south of -700 does not merely reposition the fight, it evades the boss and
    // resets the encounter.
    //
    // The Y band mirrors his own gate exactly. The X band is the part that needs
    // care, because a FightInPlaceZone is XY-only and the ghoul pit runs directly
    // WEST of the arena at 9-13yd lower. Column-probing the live 600 mmtiles
    // along y = -660 (his latitude):
    //
    //     x -244   131.55                      <- only Tharon'ja's platform above
    //     x -246   131.55 / 26.59              <- arena floor starts
    //     x -276    24.05                      <- arena floor
    //     x -278    20.39                      <- the ramp down begins
    //     x -280    15.32                      <- ramp
    //     x -300    86.69 / 11.28              <- the ghoul pit, 13yd below the arena
    //
    // So the arena floor at his latitude is x -277 .. -245, and [-282, -240] is
    // that floor plus ~5yd of the ramp at either end. The pit proper (x <= -299)
    // is outside the box and stays normally pullable, which matters: the party
    // fights its way UP through the pit to reach him and nothing there gates on
    // position. The five yards of ramp inside the box are deliberate — a pack
    // held at the arena lip is one the tank should engage where it stands rather
    // than drag back down the ramp toward the boss's own boundary.
    //
    // KNOWN AND ACCEPTED OVERLAP, the Azjol-Nerub caveat again: a zone is XY-only
    // and THE PROPHET THARON'JA'S PLATFORM SITS DIRECTLY ABOVE THIS ARENA, 107yd
    // up (x -261.8 .. -210.6, y -706.1 .. -651.1, z 128.3 .. 131.7). Its western
    // half therefore falls inside this footprint. That is unavoidable rather than
    // sloppy: the three Drakkari Invader landing spots are at x -250 and -254, so
    // the box cannot end west of -250, and the platform starts at -261.8. It is
    // also harmless — the only things standing up there are Tharon'ja himself and
    // four Drakuru Event Invisman triggers (28492, faction 35, NOT_SELECTABLE,
    // SmartAI with zero rows), so there is nothing on the platform for an
    // advanced pull to have dragged anywhere. The whole approach to him — the
    // z~102 death-knight ledge at (-288,-693) and the final climb from
    // (-274.6,-734.7) to (-245.3,-672.0) — lies outside the box in x or y at
    // every waypoint.
    FightInPlaceZone const kZones[] =
    {
        { 585, 216.0f, 260.0f, -45.0f, 45.0f },  // Magisters' Terrace — Selin Fireheart's room
        { 601, 470.0f, 640.0f, 480.0f, 625.0f }, // Azjol-Nerub — Hadronox's shaft
        { 600, -282.0f, -240.0f, -700.0f, -628.0f }, // Drak'Tharon Keep — Trollgore's arena
    };
}

bool FightInPlaceRegistry::IsNoPullZone(uint32 mapId, float x, float y)
{
    for (FightInPlaceZone const& z : kZones)
    {
        if (z.mapId != mapId)
            continue;
        if (x >= z.minX && x <= z.maxX && y >= z.minY && y <= z.maxY)
            return true;
    }
    return false;
}
