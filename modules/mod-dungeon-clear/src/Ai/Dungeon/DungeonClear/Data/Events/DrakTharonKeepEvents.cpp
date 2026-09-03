/*
 * Copyright (C) 2016+ AzerothCore <www.azerothcore.org>, released under GNU AGPL v3 license, you may redistribute it
 * and/or modify it under version 3 of the License, or (at your option), any later version.
 */

#include "Ai/Dungeon/DungeonClear/Data/Events/DungeonEventTables.h"
#include "Ai/Dungeon/DungeonClear/Data/Events/DungeonRosterBuilders.h"

#include "Creature.h"
#include "Player.h"
#include "Playerbots.h"
#include "SharedDefines.h"
#include "UnitDefines.h"

// --- Drak'Tharon Keep (map 600) -------------------------------------------
//
// One navmesh component, no break, no drop, no teleport leg, and the DBC's
// encounter order (0 Trollgore, 1 Novos, 2 King Dred, 3 The Prophet Tharon'ja)
// is already the shortest travel order — 422 + 206 + 354 + 643 = 1625yd by
// Dijkstra over the 23 map-600 mmtiles' poly graph. So nothing here is about
// routing. Three things are authored, in descending order of value:
//
//   1. THE FOURTH BOSS IS INVISIBLE TO THE CLEAR, and that is a data defect,
//      not a tuning one. See below — it ends every run at 3/4.
//   2. NOVOS THE SUMMONER is a camp-and-hold set-piece with a hard kill gate and
//      a 1665-damage-per-second pool on the boss for the whole of phase 1. It is
//      the only encounter on the map the stock engage pipeline cannot do
//      unaided.
//   3. KING DRED'S RAPTOR POOL (heroic only) is one free level-74 elite every
//      ~30s for the whole fight unless it is emptied first.
//
// --- 1. Tharon'ja is missing from the derived roster — ROOT CAUSE ----------
//
// instance_encounters, map 600 (both difficulties, verified live):
//
//     369/370  bit 0  Trollgore              creditType 0  creditEntry 26630
//     371/372  bit 1  Novos the Summoner     creditType 0  creditEntry 26631
//     373/374  bit 2  King Dred              creditType 0  creditEntry 27483
//     375/376  bit 3  The Prophet Tharon'ja  creditType 1  creditEntry 61863  <-- SPELL
//
// BossSpawnIndex::Build skips every encounter that is not
// ENCOUNTER_CREDIT_KILL_CREATURE, because a cast-spell credit's `creditEntry` is
// a SPELL id and there is no creature to look a spawn position up by. That
// filter is right and stays. The consequence is that Tharon'ja never enters
// `_store`, NextDungeonBossValue empties after King Dred, AllClearedTrigger
// fires and the run declares itself finished at 3/4.
//
// The fix is the roster patch below plus one new builder
// (DcRoster::MakeBossWithBit) that lets an added boss carry an EXPLICIT
// encounterIndex. `completionFrom` cannot express this: it resolves a kill-bit
// by looking the source entry up in the DERIVED list, and the whole problem is
// that Tharon'ja is not in it.
//
// Completion then works exactly as it does for the other three. His
// boss_tharon_jaAI::JustDied casts 61863; ObjectMgr stamps
// SPELL_ATTR0_CU_ENCOUNTER_REWARD on every cast-spell credit spell, Spell::finish
// calls Map::UpdateEncounterState(ENCOUNTER_CREDIT_CAST_SPELL, 61863, ...), and
// that sets bit 3 on the instance's completed-encounter mask — the same mask
// NextDungeonBossValue already reads for Trollgore, Novos and Dred.
//
// NOT USED HERE, deliberately: doneBossStateIndex. The instance script's index
// space is SHIFTED relative to the DBC on this map — DATA_TROLLGORE 0,
// DATA_NOVOS 1, DATA_NOVOS_CRYSTALS 2 (a door pseudo-encounter, not a boss),
// DATA_DRED 3, DATA_THARON_JA 4 — so Dred's DBC bit is 2 while his SetBossState
// slot is 3. Reading the DBC mask keeps all four bosses on ONE completion
// source; mixing the two is how a divergence hides (the Nexus Frozen Commander
// note makes the same argument from the other direction).
//
// THIS DEFECT IS NOT DTK-SPECIFIC. Every creditType-1 encounter is invisible the
// same way: CoT Stratholme (595, Mal'ganis, spell 58630), Halls of Stone (599,
// Tribunal of Ages, 59046) and Trial of the Champion (650, the Grand Champions /
// Argent Champion / Black Knight) are all in the clear's gear-tier list and all
// short a boss today. MakeBossWithBit is written to be reused for them; each is
// one patch of its own and is deliberately NOT bundled into this change.
//
// --- 2. Novos: the gate, the pool, and the decoy pile ----------------------
//
// boss_novos.cpp, verified against the live script:
//
//   * RESTING. Reset() sets UNIT_FLAG_DISABLE_MOVE (he is rooted for the whole
//     encounter) and CLEARS NON_ATTACKABLE / NOT_SELECTABLE. MoveInLineOfSight is
//     overridden to do nothing, so HE NEVER AGGROS ON PROXIMITY — somebody has to
//     hit him. The ordinary at-boss engage does that; nothing here is needed for
//     the pull itself.
//   * PHASE 1 (JustEngagedWith). He re-sets NON_ATTACKABLE | NOT_SELECTABLE — so
//     for the whole of phase 1 no bot can target him at all — and casts
//     SPELL_ARCANE_FIELD 47346 on himself. From Spell.dbc that is
//     SPELL_EFFECT_PERSISTENT_AREA_AURA at TARGET_DEST_CASTER, EffectRadiusIndex
//     42 = 11.0yd, amplitude 1000ms, BasePoints+DieSides = 1665 damage per
//     second, plus a −50% movement-speed leg. A DynamicObject lands on his feet
//     and is the phase-1 keep-out; see the DcHazardRegistry row.
//   * THE GATE. A task scheduled at 70s tests `me->HasAura(SPELL_BEAM_CHANNEL)`
//     and REPEATS EVERY 2s FOREVER while it holds. Four Crystal Channel Targets
//     (26712, one under each Ritual Crystal) channel 52106 on him, and the only
//     thing that silences one is a CRYSTAL HANDLER (26627) DYING. Four handlers
//     spawn on me->m_Events at 16s / 32s / 48s / 64s, alternating right-room and
//     left-room, each SetInCombatWithZone() on summon — THEY COME TO YOU. So:
//     kill all four handlers; Novos becomes attackable ~70s after the pull or 2s
//     after the fourth handler dies, whichever is later. There is no timeout
//     escape and no other way through.
//   * THE ADD STREAM, all from the ROOM_STAIRS trigger 45yd up the staircase
//     south of the chamber at (-378.40, -813.13, 59.74):
//       Fetid Troll Corpse 27598 — first at 3s then EVERY 3s, REACT_DEFENSIVE,
//         MovePoint(1, -373.56, -770.86, 28.59) down to the stairs' foot, and
//         SummonMovementInform then DoZoneInCombat()s it. ~23 over phase 1, and
//         the only summon that actually engages.
//       Risen Shadowcaster 27600 (9s then 10s) and Hulking Corpse 27597 (30s then
//         30s) — REACT_DEFENSIVE and LEFT STANDING AT THE SPAWN POINT. They never
//         walk down and never aggro unless attacked: a pile of passive-but-
//         hostile mobs 45 yards up a staircase, which is the Mechanar bridge
//         gauntlet's failure mode with different scenery. A clear that goes
//         LOOKING for them walks the party out of the fight and off the leash.
//   * THE LEASH. CheckEvadeIfOutOfCombatArea() is
//     `!SelectTargetFromPlayerList(80.0f)`, so at least one player must stay
//     within 80yd of Novos or the encounter resets.
//
// WHY A CONDITIONAL EVENT WITH DrivesInCombat, NOT AN ANCHORED ONE. The party is
// in continuous combat from the pull — a Fetid Troll Corpse every three seconds —
// so there is no out-of-combat tick between the pull and the gate opening.
// Anchored events drive on the non-combat engine only, and the conditional rung
// stands down on bot->IsInCombat(); either would run in gaps that do not exist.
// This is the Black Morass wave-driver shape and it is the same lesson, from the
// Mechanar bridge onward: hold the camp, let them come.
//
// WHY THE CAMP IS WHERE IT IS — (-379.0, -757.0), column-probed against the live
// 600 mmtiles as one walkable surface at z 28.39:
//
//     19.3yd from Novos — outside the 11yd Arcane Field with 8yd of margin, and
//                         far inside the 80yd leash.
//     14.9yd from (-373.56, -770.86), the Fetid Troll Corpses' arrival point, so
//                         the stream walks straight into the camp.
//     56yd  from the stairs spawn trigger — far enough that a garrisoned party
//                         has no reason to climb to the decoy pile.
//
// --- 3. King Dred's raptor pool (heroic only) ------------------------------
//
// boss_dred.cpp schedules SPELL_RAPTOR_CALL 59416 `if (IsHeroic())` — first at
// 16s, then every 30s. Its spell script does
// GetCreatureListWithEntryInGrid({26628 Drakkari Scytheclaw, 26641 Drakkari
// Gutripper}, 100.0f) and AttackStart()s a random one that is alive and NOT
// already in combat, on Dred's current victim. Nine spawns qualify, seven of them
// inside the pen. Left unpulled that is a free level-74 elite every ~30s for the
// entire fight. On normal difficulty the spell is never cast, so there is no row.
//
// --- also authored elsewhere for this map ---------------------------------
//   * DcNeverTargetRegistry — Novos Summon Target (27583). THE softlock: it is a
//     fully selectable, attackable, faction-14 elite, and a dead one cannot cast
//     SPELL_SUMMON_CRYSTAL_HANDLER, so killing one permanently stops a Crystal
//     Handler spawning, which leaves a Beam Channel that is never silenced, which
//     means Novos never becomes attackable for the life of the instance.
//   * FightInPlaceRegistry — Trollgore's arena. boss_trollgore's CheckInRoom() is
//     `Y >= -700 && Y <= -628` and failing it calls EnterEvadeMode(BOUNDARY)
//     every tick, so any pull that drags him south toward the Novos corridor
//     evades the boss outright.
//   * DcEventDoorRegistry::IsNavigationIgnored — the four Ritual Crystals
//     (189299-189302), a 27x26yd square of DOOR_TYPE_ROOM gameobjects the party
//     walks through to reach Novos, on lock 1669 (a key item no bot has).
//   * DcHazardRegistry — Arcane Field 47346 (phase 1), Blizzard 49034 (phase 2)
//     and Tharon'ja's Poison Cloud 49548.
//
// --- deliberately NOT authored --------------------------------------------
//   * NO RoomAggroRegistry / ClearRadius row at Novos. The adds come to the
//     party; a pre-clear sweep would walk it up the staircase into the decoy
//     pile, which is the exact failure the camp exists to prevent.
//   * NO SealedEncounterRegistry row anywhere. Nothing closes behind the party.
//   * NO Trollgore event. The invader stream comes to him and the arena is small,
//     so the engage pipeline should handle it once the fight-in-place box stops
//     the pull dragging him out of his Y band. Revisit only if run data shows the
//     party chasing invaders toward the east balcony.
//   * NO route anchors. Unlike Azjol-Nerub the mesh here defeats nothing.
//   * NO handling for Tharon'ja's Gift (52509) — 26 seconds of MOD_CHARM +
//     OVERRIDE_ACTIONBAR_SPELLS on every player at 55% HP. Playerbots rotations
//     are not written against an overridden action bar, so expect ~26s per fight
//     of bots doing nothing useful. That is a rotation question, not a clear
//     question; it is a known cost, recorded here so it is not re-derived as a
//     dungeon-clear bug.

namespace
{
    constexpr uint32 DTK_MAP = 600;

    constexpr uint32 DTK_TROLLGORE = 26630;
    constexpr uint32 DTK_NOVOS     = DcDrakTharonKeep::NOVOS;
    constexpr uint32 DTK_DRED      = 27483;
    constexpr uint32 DTK_THARON_JA = 26632;

    // Tharon'ja's own DB spawn — the coordinates BossSpawnIndex WOULD have
    // derived had his encounter not been credit-type 1. Column-probed at
    // (-236.8, -675.4): one walkable surface at z 131.72 against a spawn z of
    // 131.95, a 0.23yd delta NavmeshSnap absorbs. This is emphatically not an
    // Ahn'kahet-style mid-air anchor.
    constexpr float DTK_THARON_JA_X = -236.83f;
    constexpr float DTK_THARON_JA_Y = -675.41f;
    constexpr float DTK_THARON_JA_Z = 131.95f;

    // --- Novos' camp ------------------------------------------------------
    //
    // The camp coordinates, the scan radius and the two leashes live in
    // DcDrakTharonKeep (DungeonEventTables.h) because hook 14 needs the same
    // numbers, and a camp that drifts apart from the Arcane Field keep-out it is
    // placed against is a silent bug in both directions.

    // The driver's step budget. The gate is >=70s by construction and the four
    // handlers only start arriving at 16s, so a normal phase 1 runs 70-120s; a
    // party that loses a handler kill to a wipe can run several minutes longer.
    // The step is Running only while the tank is OUT of position (it hands the
    // tick back the moment it is camped), so this budget is only ever spent on a
    // tank that cannot reach the camp at all — which is a bug report, not a
    // control-flow mechanism. Optional besides, so a timeout skips.
    constexpr uint32 DTK_NOVOS_HOLD_TIMEOUT = 600000;

    constexpr uint32 DTK_HOOK_HOLD_NOVOS_CAMP = 14;  // ObjectiveHookRegistry id

    // --- King Dred's raptor pen (heroic) ----------------------------------

    // Column-probed at (-533.0, -692.0): ONE surface, z 30.63, and nothing else
    // in the column — the pen is a single-floor room. 12.5yd north-east of Dred's
    // own spawn (-544.87, -696.97, 30.30), i.e. inside the pen but not on top of
    // him.
    constexpr float DTK_PEN_X = -533.0f;
    constexpr float DTK_PEN_Y = -692.0f;
    constexpr float DTK_PEN_Z = 30.63f;

    // Sweep radius. Measured from the anchor, the nine Raptor Call candidates sit
    // at 5.7 / 14.6 / 19.5 / 26.2 / 30.5 / 32.7 / 33.7 / 62.0 / 65.9 yards (only
    // the one at 14.6 wanders, and only 5yd). 38 takes the SEVEN inside the pen
    // with 4yd to spare and deliberately leaves the last two — they stand at
    // (-483.3, -655.0) and (-483.0, -649.0), which is ON the Novos -> Dred route
    // through the handler hall (the route passes (-480.0, -651.6)), so the
    // corridor sweep has already met them by the time the party turns south into
    // the pen. Widening to 66 would instead march the party back east out of the
    // pen to re-clear ground it just walked.
    constexpr float DTK_PEN_RADIUS = 38.0f;

    // Arrival radius, and it MUST EXCEED the sweep radius — the Dire Maul crystal
    // lesson, restated by Ahn'kahet's initiate sweep. While a sweep runs the tank
    // has to stay inside arriveRadius or DcObjectiveArriveAction stops owning the
    // tick and engage-trash / Advance start competing for it. `.Persistent()`
    // does NOT rescue this: DungeonEventExecutor::IsPersistentAnchoredEventActive
    // only goes sticky at `stepIndex >= 1`, and this event's sweep IS step 0, so
    // the distance check governs the whole thing.
    //
    // 42 is comfortably inside the pen either way (it runs x -567 .. -488,
    // y -748 .. -638) and reaches nothing that should not be reached: Elder
    // Kilias, the faction-35 quest NPC, is 48.3yd from the anchor.
    constexpr float DTK_PEN_ARRIVE = 42.0f;
    // The pen floor is flat at z 30.1-32.1; 8 keeps the sweep on it.
    constexpr float DTK_PEN_ZBAND = 8.0f;
    constexpr uint32 DTK_PEN_TIMEOUT = 300000;

    constexpr uint32 DTK_DRAKKARI_SCYTHECLAW = 26628;
    constexpr uint32 DTK_DRAKKARI_GUTRIPPER  = 26641;

    // --- clear-order keys (heroic patch only) ------------------------------
    // Real kill-bits (0/1/2/3) are untouched; this is only the travel sequence,
    // and it exists solely so the raptor-pen objective has a slot to sit in
    // between Novos and Dred. The normal-difficulty patch needs no reorder at
    // all — the DBC order already matches the path.
    constexpr int32 DTK_ORDER_TROLLGORE = 1;
    constexpr int32 DTK_ORDER_NOVOS     = 2;
    constexpr int32 DTK_ORDER_PEN       = 3;
    constexpr int32 DTK_ORDER_DRED      = 4;
    constexpr int32 DTK_ORDER_THARON_JA = 5;

    bool DtkNovosPhaseOne(Player* bot, AiObjectContext* context);
}

// --- the Novos phase-1 gate (event 1, repeatable) -------------------------
//
// DUE for exactly the window the camp is needed and no longer: a live Novos
// within 120yd of the bot that is carrying UNIT_FLAG_NOT_SELECTABLE.
//
// That flag is the encounter's own phase bit and it is unambiguous. Reset()
// REMOVES it (so the predicate is false for a resting boss the party has not
// pulled yet, and false again after a wipe), JustEngagedWith SETS it (true for
// the whole of phase 1), and the 70s gate task REMOVES it in the same statement
// that starts phase 2 — `me->RemoveUnitFlag(UNIT_FLAG_NON_ATTACKABLE |
// UNIT_FLAG_NOT_SELECTABLE)` — so the predicate goes false on the very tick the
// boss becomes attackable. It is also what the boss's own JustSummoned uses to
// tell its two phases apart, so this reads the same bit the script does.
//
// The proximity term is what keeps this near-gated. The event's lone step is a
// Custom hook with no arrival step, so without a distance term it could read
// true — and the step could report Done — with the tank anywhere on the map.
// FindNearestCreature is a grid scan FROM THE BOT, so 120yd means "the leader is
// in or beside Novos' chamber". Repeatable besides: a momentary completion
// latches nothing and the next tick re-fires it.
namespace
{
    bool DtkNovosPhaseOne(Player* bot, AiObjectContext* /*context*/)
    {
        Creature* novos = bot->FindNearestCreature(DTK_NOVOS, DcDrakTharonKeep::NOVOS_SCAN, /*alive*/ true);
        if (!novos)
            return false;
        return novos->HasUnitFlag(UNIT_FLAG_NOT_SELECTABLE);
    }
}

void RegisterDrakTharonKeepEvents(std::vector<DungeonEvent>& out)
{
    // (1) NOVOS: HOLD THE CAMP THROUGH PHASE 1.
    //
    // ONE Custom step (hook 14), for the same reason the Black Morass wave event
    // is one: what this encounter needs is not a sequence but a standing
    // preference re-evaluated every tick — "be at the camp unless you are
    // usefully in melee somewhere close to it" — while adds arrive every three
    // seconds and four handlers walk in on a 16s cadence.
    //
    // What a step list could not express here:
    //   * The gate is a KILL COUNT the party never chooses targets for. The
    //     handlers SetInCombatWithZone() themselves and the corpses walk into the
    //     camp; a KillCreature(26627, 4) gate would be correct and completely
    //     inert, because nothing has to be sought.
    //   * The failure modes are all POSITIONAL and all reversible mid-fight: the
    //     tank drifting north into the Arcane Field as it chases a corpse, or
    //     south/up the staircase toward the passive Shadowcaster pile. A step
    //     list can hold ONE position; it cannot decide, per tick, whether the
    //     tank is somewhere it is allowed to be.
    //   * MoveToHoldUntilSpawn / ...InstanceData / ...PersistentData all miss:
    //     instance_drak_tharon_keep overrides neither GetData nor
    //     SetPersistentData, and GetBossState(DATA_NOVOS_CRYSTALS) only flips to
    //     DONE on Novos' DEATH — long after the hold should have ended.
    //
    // DRIVES IN COMBAT — the load-bearing flag, and the Black Morass lesson
    // verbatim. A Fetid Troll Corpse spawns every 3s and DoZoneInCombat()s
    // itself, so the party is in combat continuously from the pull to the gate.
    // The conditional rung stands down on bot->IsInCombat(), so without this the
    // driver would never run once and the tank would simply fight wherever the
    // pull left it — inside an 1665-per-second pool.
    //
    // STEPS OWN MOVEMENT — the hook issues the garrison itself, so the per-tick
    // hold in DcRunEventAction must not cancel it before the hook has looked at
    // it (the Old Hillsbrad barrel trap). It also makes the driver YIELD the tick
    // whenever the hook reports Done, which is the only reason the tank still has
    // a rotation: this rung sits above the stock combat movers and an action that
    // returned true every tick would starve them outright.
    //
    // REPEATABLE — the hook reports Done every tick the tank is correctly camped
    // (that IS the yield), so a one-shot latch would end the hold on the first
    // in-position tick, ~1 second into a 70-second phase. The condition going
    // false is the real end.
    //
    // OPTIONAL — a timed-out step skips and the repeat re-fires fresh, so a wipe
    // or a corpse run never hard-stalls the run for the human.
    out.push_back(EventBuilder(DTK_MAP, 1, "Novos: hold the camp (Crystal Handlers)")
                      .Conditional(&DtkNovosPhaseOne)
                      .Repeatable()
                      .Optional()
                      .DrivesInCombat()
                      .StepsOwnMovement()
                      .PanelBeforeBoss(DTK_NOVOS)
                      .Custom(DTK_HOOK_HOLD_NOVOS_CAMP)
                          .Timeout(DTK_NOVOS_HOLD_TIMEOUT)
                      .Build());

    // (2) KING DRED: EMPTY THE RAPTOR POOL FIRST (heroic only).
    //
    // A single entry-filtered sweep of the pen, anchored one order key ahead of
    // Dred so boss navigation walks the tank in before the pull rather than
    // leaving the pool to whatever the corridor pull happened to aggro.
    //
    // ENTRY-FILTERED, not a plain volume clear: Dred himself stands 12.5yd from
    // the anchor and Elder Kilias (30534, faction 35, npcflag 3) stands 26yd away
    // in the same pen. The filter names the two entries Raptor Call actually
    // draws from and nothing else, so the sweep can neither pull the boss early
    // nor go looking at a friendly quest NPC. (It cannot stop the party WALKING
    // near Dred while it clears — the pen is his room. That is accepted: a
    // premature Dred pull costs the pre-clear, which is what Optional is for.)
    //
    // PERSISTENT by convention rather than by necessity, and it is worth being
    // exact about which: with only ONE step there is no progress to lose, so the
    // rewind this normally guards against cannot bite. What it actually changes
    // is that the step's timeout clock keeps running across the fight's combat
    // gaps instead of being re-based by each one — which is why the budget below
    // is set at five minutes rather than the 30s default. Every ClearRadius event
    // in this folder carries the flag; keeping it means a later author who adds a
    // by-entry backstop step (the Ahn'kahet shape) does not have to remember to.
    //
    // NO BY-ENTRY BACKSTOP, unlike Ahn'kahet's initiate sweep, and for a reason
    // that does not generalise: a ClearRadius resolves candidates through
    // NearestHostileNearPoint, so anything IsPossibleTarget / IsEngageReachable
    // rejects is invisible to it and the step can answer "clear" with a raptor
    // alive. There it mattered (Jedoga never descends over a live initiate, so
    // the run walks to a permanently immune boss); here the entire consequence is
    // that Raptor Call has one more thing to call, which is the ordinary
    // unauthored behaviour. A second step to buy that is not worth its cost.
    //
    // OPTIONAL because this is a tuning pre-clear, not a gate. Nothing about Dred
    // is unreachable with raptors alive — the fight is merely worse — so a
    // wedged sweep must degrade into "fight him with the pool full" rather than
    // stall the run.
    //
    // HEROIC ONLY, matching the script: boss_dred schedules Raptor Call inside
    // `if (IsHeroic())`, so on normal there is nothing to empty and this would be
    // a pure detour. The gate is carried by BOTH the roster patch that wires the
    // anchor and the event itself, per DungeonEvent::gate.
    out.push_back(EventBuilder(DTK_MAP, 2, "King Dred: clear the raptor pen")
                      .Anchored(/*orderIndex (doc)*/ DTK_ORDER_PEN)
                      .HeroicOnly()
                      .Persistent()
                      .Optional()
                      .ClearRadius(DTK_PEN_X, DTK_PEN_Y, DTK_PEN_Z,
                                   DTK_PEN_RADIUS, DTK_PEN_ZBAND)
                          .OnlyEntries({ DTK_DRAKKARI_SCYTHECLAW, DTK_DRAKKARI_GUTRIPPER })
                          .Timeout(DTK_PEN_TIMEOUT)
                      .Build());
}

// --- roster patches -------------------------------------------------------
void RegisterDrakTharonKeepRoster(std::vector<BossRosterPatch>& t)
{
    using namespace DcRoster;

    // --- both difficulties: the missing fourth boss ------------------------
    //
    // ADD ONLY — no remove, because there is nothing to remove: Tharon'ja was
    // never in the derived list (see the header). No reorder either: the DBC bits
    // 0/1/2 already sort Trollgore -> Novos -> Dred along the travel path, and
    // bit 3 puts Tharon'ja last, which is where he belongs.
    //
    // MakeBossWithBit rather than MakeBoss(completionFrom): completionFrom
    // resolves a kill-bit out of the BASE list, and the base list is exactly
    // what is missing him.
    BossRosterPatch p;
    p.mapId = DTK_MAP;
    p.add = {
        MakeBossWithBit(DTK_THARON_JA, DTK_MAP, "The Prophet Tharon'ja",
                        DTK_THARON_JA_X, DTK_THARON_JA_Y, DTK_THARON_JA_Z,
                        /*encounterIndex*/ 3),
    };
    t.push_back(std::move(p));

    // --- heroic only: the raptor pen --------------------------------------
    //
    // Applied AFTER the patch above (Apply runs every matching patch in
    // registration order over the same list), so Tharon'ja is present here and
    // the reorder row for him lands.
    //
    // The whole 1..5 key scale exists only to give the pen objective somewhere to
    // sit between Novos and Dred. Every kill-bit is untouched — orderOverride
    // moves the clear sequence and nothing else — and the four bosses' relative
    // order is exactly what their DBC bits already gave them.
    BossRosterPatch heroic;
    heroic.mapId = DTK_MAP;
    heroic.gate = DcDifficultyGate::HeroicOnly;
    heroic.add = {
        MakeObjective(OBJ(1), /*encounterIndex*/ 0, DTK_MAP, "King Dred: clear the raptor pen",
                      DTK_PEN_X, DTK_PEN_Y, DTK_PEN_Z, DTK_PEN_ARRIVE,
                      /*gateEntry*/ 0, /*hook*/ 0, /*eventId*/ 2,
                      /*orderOverride*/ DTK_ORDER_PEN),
    };
    heroic.reorder = {
        { DTK_TROLLGORE, DTK_ORDER_TROLLGORE },
        { DTK_NOVOS,     DTK_ORDER_NOVOS     },
        { DTK_DRED,      DTK_ORDER_DRED      },
        { DTK_THARON_JA, DTK_ORDER_THARON_JA },
    };
    t.push_back(std::move(heroic));
}
