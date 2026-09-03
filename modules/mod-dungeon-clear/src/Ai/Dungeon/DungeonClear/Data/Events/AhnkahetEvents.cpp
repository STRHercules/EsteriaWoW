/*
 * Copyright (C) 2016+ AzerothCore <www.azerothcore.org>, released under GNU AGPL v3 license, you may redistribute it
 * and/or modify it under version 3 of the License, or (at your option), any later version.
 */

#include "Ai/Dungeon/DungeonClear/Data/Events/DungeonEventTables.h"
#include "Ai/Dungeon/DungeonClear/Data/Events/DungeonRosterBuilders.h"

// --- Ahn'kahet: The Old Kingdom (map 619) ---------------------------------
//
// Two of the five encounters are GATED — the boss stands there, visible and
// targetable-looking, and cannot be fought until the party does something else
// first. Neither gate is anything the engage pipeline can discover on its own,
// so both are authored here. A third correction rides along because it is the
// same two bosses: their DB spawn rows are their PRE-FIGHT positions, suspended
// in the air, and the roster snap cannot reach the floor under either.
//
//   1. PRINCE TALDARAM is imprisoned until BOTH Ancient Nerubian Devices are
//      clicked. Two objectives, one per device.
//   2. JEDOGA SHADOWSEEKER will not descend until all fifteen Twilight Initiates
//      kneeling in her ritual chamber are dead. One objective, an entry-filtered
//      sweep.
//
// The rest of the dungeon (Elder Nadox's guardian aura, Amanitar's mushrooms,
// Herald Volazj's Insanity phasing, and the NAVMESH BREAK between the party's
// component and Volazj's chamber) is not addressed here — see
// deployment-files/docs/mod-dungeon-clear_ahnkahet_plan.md. The Volazj break in
// particular means a run authored only this far still cannot finish; that is a
// separate piece of work and deliberately not bundled in.
//
// NO CLIENT PACKET IS INVOLVED ANYWHERE ON THIS MAP. AreaTrigger.dbc has three
// rows on 619 — 5213 and 5235 are plain areatrigger_teleport exits, 5322 has no
// row in any script table — and there is no areatrigger_scripts,
// areatrigger_involvedrelation or smart_scripts source_type 2 entry for any of
// them. DcTestAreaTriggers has nothing to relay here (same finding as
// Azjol-Nerub; contrast the Underbog and the Shattered Halls, which really are
// missing-packet bugs).
//
// --- 1. Prince Taldaram: the two Ancient Nerubian Devices ------------------
//
// boss_prince_taldaram.cpp::InitializeAI, while either sphere is unset:
//
//     me->SetImmuneToAll(true);
//     me->SetDisableGravity(true);
//     me->SetHover(true);
//     DoCastSelf(SPELL_BEAM_VISUAL, true);
//     me->SummonCreatureGroup(SUMMON_GROUP_TRIGGERS);
//     return;
//
// He hangs at z 42.04 over his platform, immune, wearing the beam, with seven
// Jedoga Controllers (30181) holding it on him. Nothing the party can do to him
// matters until the prison drops.
//
// WHAT DROPS IT. Not a C++ gameobject script — SmartAI on the two devices:
//
//     smart_scripts source_type=1
//       193093  event 64 (SMART_EVENT_GOSSIP_HELLO) -> action 34 SET_INST_DATA 0
//       193094  event 64 (SMART_EVENT_GOSSIP_HELLO) -> action 34 SET_INST_DATA 1
//
// `GameObject::Use(player)` reaches that through `AI()->GossipHello(player,
// false)`, and `SmartGameObjectAI::GossipHello` RETURNS FALSE — so Use does not
// early-out on the gossip branch and also falls through to `UseDoorOrButton`,
// flipping the device out of GO_STATE_READY. Both halves matter here: the first
// is what sets the data, the second is what makes the step idempotent (the
// executor reads a non-READY GO as already used).
//
// `instance_ahnkahet::SetData` then StorePersistentData(index, DONE) +
// SaveToDB(), and on the SECOND device HandleGameObject(platform, true) +
// `taldaram->AI()->DoAction(ACTION_REMOVE_PRISON)`. He casts Hover Fall,
// MoveLands onto `GetMapWaterOrGroundLevel` (z 11.43), and only on
// MovementInform(EFFECT_MOTION_TYPE, POINT_LAND) clears
// UNIT_FLAG_NON_ATTACKABLE | NOT_SELECTABLE and SetImmuneToAll(false).
//
// TWO OBJECTIVES, NOT ONE TWO-CLICK EVENT — the Nexus Containment Sphere idiom.
// The devices are 74.5yd apart and an event step's own movement is a plain
// `HopTo` MovePoint, documented as a SHORT intra-room hop; a haul that long
// belongs to a travel anchor so boss navigation and the pull machinery drive it.
// It also puts two legible rows in the `dc bosses` panel instead of one opaque
// one.
//
// VISIT ORDER. Dijkstra over the live 619 navmesh poly graph, entering from
// Nadox (the boss immediately before these on the DBC scale):
//
//     nadox -> 193094 -> 193093 -> taldaram   307 + 160 + 225 = 692
//     nadox -> 193093 -> 193094 -> taldaram   332 + 160 + 228 = 720
//
// so 193094 (the EASTERN device, y -783.9) is first and 193093 (the WESTERN one,
// y -719.0) second. Poly-centre distances overstate a string-pulled route, but
// the 28yd margin is a comparison between two routes measured the same way.
//
// EACH OBJECTIVE VERIFIES ITSELF. UseGameObject reports Done the moment it calls
// `go->Use(bot)` — it does not check that anything happened. A click that was
// swallowed would latch the objective complete and send the party on to a boss
// that is still immune, which reads as an unexplained stall at Taldaram rather
// than a failure at the device. So each event follows its click with a
// persistent-data hold on the index that click is supposed to set. SetData runs
// synchronously inside Use, so on the happy path the hold clears on the same
// tick and costs nothing; on the unhappy path it stalls AT THE DEVICE, where the
// human can see what actually went wrong.
//
// SAFE ON A SAVED INSTANCE. If the lockout already has a sphere stored,
// `instance_ahnkahet::OnGameObjectCreate` spawns that device GO_STATE_ACTIVE
// with GO_FLAG_NOT_SELECTABLE, the UseGameObject step reads the non-READY state
// as already used and returns Done without clicking, and the hold behind it is
// already satisfied. The whole event no-ops.
//
// --- 2. Jedoga Shadowseeker: the fifteen Twilight Initiates ----------------
//
// boss_jedoga_shadowseeker.cpp::Reset() summons creature_summon_groups group 0 —
// fifteen Twilight Initiates (30114) at z -16.10 — and parks HER at
// (372.33, -705.28, -2.46): REACT_PASSIVE, UNIT_FLAG_NOT_SELECTABLE |
// NON_ATTACKABLE, SetImmuneToAll(true), gravity off, hovering, with a sphere
// visual and the lightning-bolt channel running.
//
// The ONLY thing that brings her down is SummonedCreatureDies emptying
// `oocSummons`:
//
//     oocSummons.erase(itr);
//     if (!oocSummons.empty()) break;
//     DespawnOOCSummons();
//     DoCastSelf(SPELL_HOVER_FALL);
//     me->GetMotionMaster()->MovePoint(POINT_DOWN, JedogaPosition[1], ...);
//
// and POINT_DOWN's MovementInform is what clears her flags and immunity. So the
// fifteen are a hard gate, exactly like the Nexus spheres, and they are the last
// thing between the party and the encounter.
//
// (JedogaPosition's comments have indices 0 and 1 labelled the wrong way round:
// the code MovePoints POINT_DOWN to JedogaPosition[1] (z -16.18) and MoveTakeoffs
// POINT_UP to JedogaPosition[0] (z -2.46). She FIGHTS at -16.18.)
//
// AN ENTRY-FILTERED ClearRadius, NOT A BARE ROOM SWEEP. Three other things stand
// inside any radius wide enough to cover the initiates and none of them may be
// swept: Jedoga herself (13.5yd overhead), the two Jedoga Controllers (30181)
// group 1 puts on the ledges 45yd up, and the ten Twilight Worshippers (30111)
// group 2 summons the instant she is ENGAGED — i.e. after this objective is
// already done, but a rewind must not pick them up. `.OnlyEntries({30114})`
// makes the sweep exactly the fifteen. (Jedoga is additionally excluded by
// NearestHostileNearPoint's own IsDungeonBossEntry and IsPossibleTarget filters,
// and by the z-band; the entry filter is the one that is obviously correct at a
// glance.)
//
// THE STEP TAKES THEM ONE AT A TIME. ClearRadius is a pure GATE in the executor
// — Running while any in-filter hostile is reachable in the volume, Done when
// none is — and it issues no movement of its own except the single HopTo that
// re-centres the tank before certifying an EMPTY room. The fighting is done by
// the step's driving half in DcEngageActions, which EngageDirects the NEAREST
// in-filter hostile and re-picks after each kill. So the pack is worked from
// whichever edge the tank is standing on, one initiate at a time.
//
// That is why there is NO leading MoveTo here, unlike the Arcatraz Eredar sweep.
// Three mobs is a room to walk into the middle of; fifteen is not. A MoveTo would
// march the tank to the centroid through all of them before a single one was
// engaged, and the re-centring HopTo cannot do the same by accident — it only
// fires when the sweep has already found nothing left to fight.
//
// THE ANCHOR SITS AT THE CENTROID WITH A WIDE ARRIVE RADIUS for the reason the
// Dire Maul crystals document: while the sweep runs, the tank must stay inside
// arriveRadius or the at-objective action stops owning the tick and
// engage-trash/Advance start competing for it — the live back-and-forth
// deadlock. 30 > the 26yd sweep, so the whole kill zone is inside "arrived", and
// because nothing walks the tank in, boss-nav parks it at the volume's edge and
// the pack is worked from outside.
//
// A BY-ENTRY BACKSTOP FOLLOWS THE SWEEP — the Shattered Halls / Arcatraz lesson.
// ClearRadius resolves candidates through NearestHostileNearPoint, which filters
// on AttackersValue::IsPossibleTarget (hard-gated on CanSeeOrDetect) and a STRICT
// IsEngageReachable; anything those reject is invisible to the sweep, which then
// answers "clear" over a live initiate and latches the objective done. The
// consequence here is specific and bad: Jedoga never descends, so the party walks
// to a permanently immune boss. KillCreatureEngage resolves by entry through
// FindNearestCreature — a plain grid scan with no visibility filter and the
// looser requireDirect=false probe — and is an instant no-op when the chamber
// really is empty.
//
// --- 3. Both bosses' anchors are in mid-air, and the snap cannot save them --
//
// BossSpawnIndex takes its coordinates from the `creature` spawn row, and for
// these two that row is the PRE-FIGHT pose:
//
//     29308 Prince Taldaram      (528.734, -845.998,  42.035)  <- in his prison
//     29310 Jedoga Shadowseeker  (372.331, -705.278,  -0.624)  <- hovering
//
// Column-probing the live mmaps gives ONE walkable surface under each — z 11.43
// and z -15.98 — so the anchors are 30.6yd and 15.4yd off the floor.
//
// DungeonBossesValue::SnapAll would normally fix that, and it is worth being
// explicit about why it does not: BOSS_SNAP_RADIUS is 40, but NavmeshSnap uses a
// fixed `SNAP_VERT_EXTENT = 10.0f` for the query box's vertical half-extent
// regardless of the radius. findNearestPoly only considers polys overlapping
// that box, and neither floor does. Both snaps fail, Snap leaves the raw coords,
// and the at-boss trigger then never matches. So both are remove + re-add with
// hand-probed coordinates, `completionFrom` = their own entry to keep their real
// DBC kill-bit (resolved off the base list before the removal takes effect,
// ApplyOne step 1), and the order key on the MakeBoss call because p.reorder only
// touches entries that survived the removal.
//
// --- clear order ----------------------------------------------------------
//
// The DBC bit order already matches the travel path on both difficulties
// (normal: Nadox 0, Taldaram 1, Jedoga 2, Volazj 3; heroic inserts Amanitar at 3
// and pushes Volazj to 4), so nothing is reordered for ordering's sake — the
// bosses are only restated on a 1..8 scale so the three objectives have integer
// slots to sit in.

namespace
{
    constexpr uint32 AK_MAP = 619;

    // --- the two devices --------------------------------------------------

    // gameobject_template 193093/193094, both named "Ancient Nerubian Device",
    // both GAMEOBJECT_TYPE_DOOR with startOpen 0, lock 0 and autoCloseTime 0,
    // both spawned GO_STATE_READY. Distinguished here by side: 193094 sits at
    // y -783.9 (east) and 193093 at y -719.0 (west).
    constexpr uint32 AK_DEVICE_EAST = 193094;
    constexpr uint32 AK_DEVICE_WEST = 193093;

    // GO spawn XY with the navmesh floor under it for Z. Column probes against
    // the live 619 mmtiles return exactly ONE walkable surface at each — 18.19
    // and 18.37 — so there is no ambiguity about which deck the anchor is on.
    constexpr float AK_DEVICE_EAST_X = 692.47f;
    constexpr float AK_DEVICE_EAST_Y = -783.91f;
    constexpr float AK_DEVICE_EAST_Z = 18.19f;

    constexpr float AK_DEVICE_WEST_X = 655.73f;
    constexpr float AK_DEVICE_WEST_Y = -719.05f;
    constexpr float AK_DEVICE_WEST_Z = 18.37f;

    // The persistent-data index each device's SmartAI row sets.
    // AhnKahetPersistentData: DATA_TELDRAM_SPHERE1 = 0, DATA_TELDRAM_SPHERE2 = 1;
    // 193093 carries SET_INST_DATA 0 and 193094 SET_INST_DATA 1, and
    // instance_ahnkahet::SetData maps type -> index one-for-one.
    constexpr uint32 AK_SPHERE_INDEX_WEST = 0;
    constexpr uint32 AK_SPHERE_INDEX_EAST = 1;

    // EncounterState::DONE. Restated rather than including InstanceScript.h for
    // one integer, the same way MechanarEvents.cpp restates its wave threshold.
    constexpr uint32 AK_SPHERE_DONE = 3;

    // Comfortably covers the objective's 8yd arrive radius, and the two devices
    // are 74.5yd apart carrying DISTINCT entries, so the bot-centred
    // FindNearestGameObject the step uses cannot resolve the wrong one.
    constexpr float AK_DEVICE_SEARCH = 12.0f;
    constexpr float AK_DEVICE_ARRIVE = 8.0f;

    // Radius for the verification hold. Only has to cover the few yards
    // UseGameObject's own walk-in leaves the tank at (it closes to within 5yd of
    // the GO before clicking), so this never issues a move of its own.
    constexpr float AK_DEVICE_HOLD = 8.0f;

    // Walk-in plus one click plus a same-tick data read. The 30s EventStepTimeout
    // default would do, but the Eye of Taldaram / Frostbringer packs share this
    // deck and an arrival that lands mid-fight should not read as a stall. 60s
    // matches the Nexus spheres.
    constexpr uint32 AK_DEVICE_TIMEOUT = 60000;

    // --- Jedoga's ritual chamber -----------------------------------------

    constexpr uint32 AK_TWILIGHT_INITIATE = 30114;

    // Centroid of the fifteen group-0 summon positions, with the navmesh floor
    // under it. The column here holds TWO surfaces — -15.98 and -97.37 — because
    // Amanitar's cave system runs 81yd below this chamber, which is what the
    // z-band below is guarding against.
    constexpr float AK_INITIATE_X = 377.31f;
    constexpr float AK_INITIATE_Y = -709.06f;
    constexpr float AK_INITIATE_Z = -15.98f;

    // The furthest initiate is 19.9yd from the centroid, so 26 covers all fifteen
    // with ~6yd of margin for one that has been pulled off its spot.
    constexpr float AK_INITIATE_RADIUS = 26.0f;

    // Half-band. The initiates sit at z -16.10, one tenth of a yard off the
    // centre, so 12 is enormously generous for them while still excluding both
    // things stacked in this column: Jedoga hovering at -2.46 (13.5yd up) and the
    // -97.37 cave floor. The lower chamber the party approaches through is at
    // z -31.6, also outside the band.
    constexpr float AK_INITIATE_ZBAND = 12.0f;

    // > AK_INITIATE_RADIUS on purpose (Dire Maul crystal lesson): the tank must
    // stay "arrived" for the whole sweep or the at-objective action loses the tick.
    constexpr float AK_INITIATE_ARRIVE = 30.0f;

    // Backstop scan. The initiates are summons pinned to a 30x25yd patch of one
    // platform, so 60 reaches every one of them from anywhere in the chamber and
    // cannot walk the tank into another room.
    constexpr float AK_INITIATE_SCAN = 60.0f;

    // Set far past any real fight rather than close to it — a timeout that fires
    // while the party is still winning turns a slow clear into a Failed step, and
    // this step is `required`. Fifteen level-74 mobs taken in pull-governed
    // groups, plus a wipe and a corpse run (the event is Persistent, so the party
    // resumes the sweep rather than restarting it), fits inside 7 minutes.
    constexpr uint32 AK_INITIATE_TIMEOUT = 420000;

    // --- bosses ----------------------------------------------------------

    constexpr uint32 AK_NADOX    = 29309;
    constexpr uint32 AK_TALDARAM = 29308;
    constexpr uint32 AK_JEDOGA   = 29310;
    constexpr uint32 AK_AMANITAR = 30258;
    constexpr uint32 AK_VOLAZJ   = 29311;

    // Hand-probed floors, replacing the mid-air spawn rows. One walkable surface
    // in each column.
    constexpr float AK_TALDARAM_X = 528.73f;
    constexpr float AK_TALDARAM_Y = -846.00f;
    constexpr float AK_TALDARAM_Z = 11.43f;

    // boss_jedoga_shadowseeker.cpp JedogaPosition[1] — her own POINT_DOWN
    // destination — with the probed floor for Z (the script's -16.18 and the
    // mesh's -15.98 agree to within 0.2yd).
    constexpr float AK_JEDOGA_X = 372.33f;
    constexpr float AK_JEDOGA_Y = -705.28f;
    constexpr float AK_JEDOGA_Z = -15.98f;

    // --- clear-order keys -------------------------------------------------
    // Real kill-bits are untouched; this is only the travel sequence.
    constexpr int32 AK_ORDER_NADOX       = 1;
    constexpr int32 AK_ORDER_DEVICE_EAST = 2;
    constexpr int32 AK_ORDER_DEVICE_WEST = 3;
    constexpr int32 AK_ORDER_TALDARAM    = 4;
    constexpr int32 AK_ORDER_INITIATES   = 5;
    constexpr int32 AK_ORDER_JEDOGA      = 6;
    constexpr int32 AK_ORDER_AMANITAR    = 7;
    constexpr int32 AK_ORDER_VOLAZJ      = 8;
}

void RegisterAhnkahetEvents(std::vector<DungeonEvent>& out)
{
    // Device 1 of 2 — the eastern one, nearest the walk down from Elder Nadox.
    //
    // PERSISTENT because the verification hold is a data-gated MoveTo, which the
    // F1 persistence lint (rightly) classes as a rewind hazard: a combat gap on
    // this deck would otherwise rewind to step 0. Both steps are idempotent — a
    // used device is left non-READY, which UseGameObject reads as already done,
    // and the hold behind it re-reads a value that only ever moves one way — so
    // the rewind would in fact be survivable; persistence just stops it happening.
    //
    // REQUIRED (the default), like the Nexus spheres and unlike the Sunken Temple
    // statues: a device that will not click leaves Taldaram permanently immune,
    // and the run genuinely cannot finish from there. That has to surface as a
    // stall the human can act on, not be skipped past.
    out.push_back(EventBuilder(AK_MAP, 1, "Ancient Nerubian Device (east)")
                      .Anchored(/*orderIndex (doc)*/ AK_ORDER_DEVICE_EAST)
                      .Persistent()
                      .UseGO(AK_DEVICE_EAST, AK_DEVICE_SEARCH)
                          .Timeout(AK_DEVICE_TIMEOUT)
                      .MoveToHoldUntilPersistentData(AK_DEVICE_EAST_X, AK_DEVICE_EAST_Y,
                                                     AK_DEVICE_EAST_Z, AK_DEVICE_HOLD,
                                                     AK_SPHERE_INDEX_EAST, AK_SPHERE_DONE)
                          .Timeout(AK_DEVICE_TIMEOUT)
                      .Build());

    // Device 2 of 2 — the western one, on the way down to Taldaram's platform.
    // Clicking this one is what fires ACTION_REMOVE_PRISON, so the ~4s MoveLand
    // starts here. Nothing waits for it: the walk from this device to Taldaram's
    // anchor is ~225yd of navmesh, and he is attackable long before the party
    // arrives.
    out.push_back(EventBuilder(AK_MAP, 2, "Ancient Nerubian Device (west)")
                      .Anchored(/*orderIndex (doc)*/ AK_ORDER_DEVICE_WEST)
                      .Persistent()
                      .UseGO(AK_DEVICE_WEST, AK_DEVICE_SEARCH)
                          .Timeout(AK_DEVICE_TIMEOUT)
                      .MoveToHoldUntilPersistentData(AK_DEVICE_WEST_X, AK_DEVICE_WEST_Y,
                                                     AK_DEVICE_WEST_Z, AK_DEVICE_HOLD,
                                                     AK_SPHERE_INDEX_WEST, AK_SPHERE_DONE)
                          .Timeout(AK_DEVICE_TIMEOUT)
                      .Build());

    // Jedoga's ritual chamber. Kill all fifteen kneeling initiates; she comes
    // down on the last one.
    //
    // PERSISTENT because a ClearRadius is a fight and a mid-fight Drive gap would
    // rewind the step list — a wipe resumes the sweep rather than restarting it,
    // which matters here because Jedoga's Reset() re-summons the whole group and
    // the party is walking back into fifteen fresh mobs either way.
    //
    // REQUIRED: the same argument as the devices. A half-cleared chamber leaves
    // her hovering and immune forever.
    out.push_back(EventBuilder(AK_MAP, 3, "Clear the Twilight Initiates")
                      .Anchored(/*orderIndex (doc)*/ AK_ORDER_INITIATES)
                      .Persistent()
                      // 1. The gate, and the thing that picks each target.
                      //    Entry-filtered to the fifteen; see the header note for
                      //    the three things inside this volume that must NOT be
                      //    swept, and for why nothing walks the tank in.
                      .ClearRadius(AK_INITIATE_X, AK_INITIATE_Y, AK_INITIATE_Z,
                                   AK_INITIATE_RADIUS, AK_INITIATE_ZBAND)
                          .OnlyEntries({ AK_TWILIGHT_INITIATE })
                          .Timeout(AK_INITIATE_TIMEOUT)
                      // 2. By-entry backstop for whatever IsPossibleTarget /
                      //    IsEngageReachable hid from the position sweep. An
                      //    instant no-op when the chamber really is empty.
                      .KillCreatureEngage(AK_TWILIGHT_INITIATE,
                                          /*count (doc; "any alive")*/ 15,
                                          AK_INITIATE_SCAN)
                          .Timeout(AK_INITIATE_TIMEOUT)
                      .Build());
}

// --- roster patch ---------------------------------------------------------
void RegisterAhnkahetRoster(std::vector<BossRosterPatch>& t)
{
    using namespace DcRoster;

    BossRosterPatch p;
    p.mapId = AK_MAP;

    // Taldaram and Jedoga are both re-anchored onto the floor they actually
    // fight on — see the header for why SnapAll cannot do it (fixed 10yd vertical
    // query extent against 30.6yd and 15.4yd drops). remove + re-add rather than
    // `reorder` because only remove+add can carry hand-authored coordinates;
    // completionFrom = each boss's own entry keeps its real DungeonEncounter
    // kill-bit, which differs by difficulty for neither of them (Taldaram bit 1,
    // Jedoga bit 2, on both).
    p.remove = { AK_TALDARAM, AK_JEDOGA };

    p.add = {
        MakeBoss(AK_TALDARAM, AK_MAP, "Prince Taldaram",
                 AK_TALDARAM_X, AK_TALDARAM_Y, AK_TALDARAM_Z,
                 /*completionFrom*/ AK_TALDARAM,
                 /*orderOverride*/ AK_ORDER_TALDARAM),

        MakeBoss(AK_JEDOGA, AK_MAP, "Jedoga Shadowseeker",
                 AK_JEDOGA_X, AK_JEDOGA_Y, AK_JEDOGA_Z,
                 /*completionFrom*/ AK_JEDOGA,
                 /*orderOverride*/ AK_ORDER_JEDOGA),

        // The two devices, between Nadox and Taldaram. An objective's
        // encounterIndex is an ordering hint only — it carries no kill-bit and
        // NextDungeonBossValue never tests the completion mask for one — so it
        // stays 0 and the clear orders entirely by orderOverride.
        MakeObjective(OBJ(1), /*encounterIndex*/ 0, AK_MAP, "Ancient Nerubian Device (east)",
                      AK_DEVICE_EAST_X, AK_DEVICE_EAST_Y, AK_DEVICE_EAST_Z,
                      AK_DEVICE_ARRIVE, /*gateEntry*/ 0, /*hook*/ 0,
                      /*eventId*/ 1, /*orderOverride*/ AK_ORDER_DEVICE_EAST),

        MakeObjective(OBJ(2), /*encounterIndex*/ 0, AK_MAP, "Ancient Nerubian Device (west)",
                      AK_DEVICE_WEST_X, AK_DEVICE_WEST_Y, AK_DEVICE_WEST_Z,
                      AK_DEVICE_ARRIVE, /*gateEntry*/ 0, /*hook*/ 0,
                      /*eventId*/ 2, /*orderOverride*/ AK_ORDER_DEVICE_WEST),

        // The initiate sweep, one key ahead of Jedoga and 6.2yd from her anchor,
        // so boss navigation walks the tank into the chamber once and the event
        // holds the objective open until she can be fought.
        MakeObjective(OBJ(3), /*encounterIndex*/ 0, AK_MAP, "Clear the Twilight Initiates",
                      AK_INITIATE_X, AK_INITIATE_Y, AK_INITIATE_Z,
                      AK_INITIATE_ARRIVE, /*gateEntry*/ 0, /*hook*/ 0,
                      /*eventId*/ 3, /*orderOverride*/ AK_ORDER_INITIATES),
    };

    // Put the three untouched bosses on the same 1..8 key scale so the objectives
    // have somewhere to sit. Their DBC kill-bits are unchanged and their relative
    // order already matched the travel path on both difficulties.
    //
    // Amanitar is heroic-only (spawnMask 2, and he only has a DungeonEncounter
    // row on difficulty 1), so on normal this row matches nothing and is a silent
    // no-op — which is the correct behaviour, and why he does not need a separate
    // HeroicOnly patch the way the Nexus' Frozen Commander does: that one had to
    // change completion, and only remove+re-add can do that.
    p.reorder = {
        { AK_NADOX,    AK_ORDER_NADOX    },
        { AK_AMANITAR, AK_ORDER_AMANITAR },
        { AK_VOLAZJ,   AK_ORDER_VOLAZJ   },
    };

    t.push_back(std::move(p));
}
