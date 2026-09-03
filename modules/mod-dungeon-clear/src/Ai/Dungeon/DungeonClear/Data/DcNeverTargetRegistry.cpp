/*
 * Copyright (C) 2016+ AzerothCore <www.azerothcore.org>, released under GNU AGPL v3 license, you may redistribute it
 * and/or modify it under version 3 of the License, or (at your option), any later version.
 */

#include "DcNeverTargetRegistry.h"

namespace
{
    // ---- the table ------------------------------------------------------
    //
    // The Nexus (576) — Crystalline Frayer (26793), 44 spawns filling the
    // south-west garden the party crosses to reach Ormorok the Tree-Shaper.
    // `npc_crystalline_frayer` (instance_nexus.cpp) makes it unkillable until
    // Ormorok is dead, and then kills every one of them itself:
    //
    //     void JustEngagedWith(Unit*) override
    //     {
    //         _allowDeath = instance->GetBossState(DATA_ORMOROK_EVENT) == DONE;
    //     }
    //     void DamageTaken(Unit*, uint32& damage, ...) override
    //     {
    //         if (damage >= me->GetHealth() && !_allowDeath)
    //         {
    //             damage = 0;            // <-- the killing blow is discarded
    //             EnterSeedPod();
    //         }
    //     }
    //
    // EnterSeedPod parks it for NINETY SECONDS — REACT_PASSIVE, threat cleared,
    // NOT_SELECTABLE | IMMUNE_TO_PC | IMMUNE_TO_NPC, scale 0.6, and an Aura of
    // Regeneration (57056) ticking it back up — and LeaveSeedPod then returns it
    // to full health, REACT_AGGRESSIVE and roaming. Ormorok's death runs
    // `instance_nexus::KillAllFrayers()`, which strips those flags off every
    // frayer and `Unit::Kill`s it outright.
    //
    // So the clear's view of a frayer is binary and needs no instance-data read:
    // while one is ALIVE it cannot be killed, and the moment it can be killed it
    // is already dead. There is no window in which fighting one is progress.
    //
    // The dormant half of that cycle is already invisible to the clear —
    // IsPossibleTarget rejects NOT_SELECTABLE and IMMUNE_TO_PC — which is exactly
    // why filtering only the seed pod would not have fixed anything: the bots
    // wedge on the AWAKE frayer, whose only observable difference from ordinary
    // trash is that its health bar refills every 90 seconds. Hence a flat row
    // rather than an aura test.
    // ---------------------------------------------------------------------
    //
    // Ahn'kahet (619) — Jedoga Shadowseeker's ritual STAGING. Two entries, one
    // failure: the party walks off the ritual floor mid-encounter and the
    // encounter resets behind it.
    //
    // WHAT BREAKS. At 55% HP boss_jedoga_shadowseeker enters PHASE_RITUAL:
    //
    //     me->SetCombatMovement(false);
    //     me->InterruptNonMeleeSpells(false);
    //     me->AttackStop();
    //     me->SetReactState(REACT_PASSIVE);
    //     me->SetUnitFlag(UNIT_FLAG_NOT_SELECTABLE | UNIT_FLAG_NON_ATTACKABLE);
    //
    // and `damage = 0` for the rest of the phase. She takes off, hovers 13.7yd
    // above the floor and sacrifices a volunteer. For those seconds the party has
    // no boss to hit and no boss hitting it, so the CLEAR'S NON-COMBAT LADDER
    // TAKES OVER — and the corridor scan finds the ring of staging mobs the
    // encounter has just placed around the arena. Live (tr-20260825-224456-8,
    // tank Wieron, 23:02:48-23:03:33):
    //
    //     pull target vetoed — Jedoga Shadowseeker (untargetable)
    //     blocking-trash: 3 candidate(s) in band -> Entry: 30111 at 52.6yd   x25
    //
    // The tank walked 52yd off the ritual floor. Jedoga is REACT_PASSIVE with
    // combat movement off, so `CreatureAI::UpdateVictim` takes the passive
    // branch, her threat list empties behind the departing party, and she
    // EnterEvadeMode(NO_HOSTILES)s — `BossAI::_EnterEvadeMode` then
    // `summons.DespawnAll()`s the whole staging set and `Reset()` re-summons the
    // fifteen Twilight Initiates at full strength. The clear cannot recover from
    // that: the initiate objective (map 619 event 3) latched Done minutes ago and
    // is not Repeatable, so nothing clears them a second time and the party is
    // left standing at a boss that will never come down.
    //
    // 30111 TWILIGHT WORSHIPPER. Ten of them are summoned by
    // `JustEngagedWith` -> SummonCreatureGroup(SUMMON_GROUP_IC_WORSHIPPERS), set
    // kneeling, at z -17.95 and up to 65yd from the ritual floor. They are
    // scenery — kneeling congregation watching the sacrifice — but nothing marks
    // them as such: they are plain hostile SmartAI casters, so the corridor scan
    // reads them as a pack standing on the route out.
    //
    // The row also covers the SIX DB spawns in the lower chamber (z -31.6) the
    // party crosses on the way in, and that is accepted rather than worked
    // around: they aggro on their own (every 30111 first-contact in the live logs
    // is one of them opening the fight from 0.0yd off its spawn), and this table
    // only removes the clear's decision to go LOOKING — a worshipper that pulls
    // the party is still fought normally. There is no position in a
    // (mapId, entry) row to separate the two sets, and letting the clear seek the
    // approach six is not worth an unrecoverable reset at the boss.
    //
    // 30385 TWILIGHT VOLUNTEER. Twenty-five are summoned when the last initiate
    // dies, at z -31.6, and walk to a ring around the arena up to 36yd out.
    // Twenty-four of them are NOT_SELECTABLE | NON_ATTACKABLE, `SetImmuneToAll`
    // and `UNIT_STATE_STUNNED` for the whole encounter — they fit this table's
    // original criterion exactly, in that they cannot be killed at all. Only the
    // one Jedoga picks as `sacrificeTargetGUID` has those flags removed
    // (`npc_twilight_volunteer::DoAction(ACTION_RITUAL_BEGIN)`), and it then
    // walks to (373.5, -706.0, -16.2) — INTO the party — so nobody ever needs to
    // travel to reach it.
    //
    // Chasing it is what the clear was doing instead: `DcTargeting::
    // LeaderFightAnchor` resolves the regroup anchor off the leader's victim, so
    // the moment the tank picked the volunteer at its ring position the whole
    // party's standoff anchor moved with it — "regroup: moving to standoff
    // (36.3yd, anchor=Entry: 30385)", three members at once, in the same window.
    //
    // KILLING IT IS STILL THE RIGHT PLAY and this row does not stop it. Denying
    // Jedoga `SPELL_GIFT_OF_THE_HERALD` (56219) means killing the volunteer
    // before she does, and mod-playerbots' own `wotlk-ok` strategy does exactly
    // that (JedogaVolunteerTrigger / AttackJedogaVolunteerAction, which scan
    // `possible targets no los` by entry). That is the COMBAT engine, which this
    // table leaves untouched. All that is removed is the CLEAR's decision to walk
    // the tank out to the arena's edge for it.
    // Drak'Tharon Keep (600) — Novos Summon Target (27583). THE softlock on the
    // map, and the one row here whose failure mode is unrecoverable.
    //
    // WHAT IT IS. boss_novos' JustEngagedWith summons two of them into the Novos
    // chamber's opposite corners, at (-341.31, -724.40, 28.57) and
    // (-408.87, -730.21, 28.58). Its template reads `unit_flags 0`,
    // `flags_extra 128` (TRIGGER), faction 14, rank 1 (elite), level 74 — i.e.
    // it is a "trigger" only by convention. It carries NONE of the flags that
    // hide a trigger from the clear: not NOT_SELECTABLE, not NON_ATTACKABLE, not
    // IMMUNE_TO_PC. AttackersValue::IsPossibleTarget accepts it, and there is no
    // IsTrigger() test anywhere in mod-playerbots or mod-dungeon-clear. So to the
    // corridor scan it is simply a fresh elite standing 30-40yd away, in the room
    // the party is already fighting in.
    //
    // WHY KILLING IT ENDS THE RUN. The four Crystal Handlers are spawned by
    // `target->CastSpell(target, SPELL_SUMMON_CRYSTAL_HANDLER, ...)` on me->
    // m_Events at 16s / 32s / 48s / 64s, alternating between these two targets.
    // A dead unit cannot cast. Killing one therefore permanently prevents one or
    // both of its two handlers from ever spawning — and a handler's death is the
    // ONLY thing that removes a Beam Channel (52106) from Novos. The 70s gate
    // task tests `me->HasAura(SPELL_BEAM_CHANNEL)` and repeats every 2s FOREVER
    // while it holds, with no timeout escape, so Novos never becomes attackable.
    // The encounter is unwinnable until the instance resets: not a wipe, not a
    // stall the human can unstick at the keyboard, a dead run.
    //
    // This is class 2 of the two above (killing it is NEGATIVE progress) in its
    // purest form: it is encounter staging, placed by the script, and the party
    // has no reason to travel to it and every reason not to.
    //
    // NOT LISTED, on purpose: Darkweb Victim (27909), the six cocooned civilians
    // in the corridor between Trollgore and Novos. Killing one rolls 49958/49959
    // and hands the party a free level-76 elite at the corpse, so it is genuine
    // negative progress — but only one of the six ((-287.1, -701.2)) is within
    // ~10yd of the route and the rest are 20yd+ east of it, off-path. This table
    // is meant to stay small and justified; add the row if run data shows the
    // clear actually detouring to them.
    DcNeverTargetRow const kRows[] =
    {
        { 576, 26793 },  // The Nexus — Crystalline Frayer (seed pod; unkillable until Ormorok dies)
        { 619, 30111 },  // Ahn'kahet — Twilight Worshipper (Jedoga's kneeling congregation, 65yd out)
        { 619, 30385 },  // Ahn'kahet — Twilight Volunteer (24/25 permanently unattackable; the 25th walks in)
        { 600, 27583 },  // Drak'Tharon Keep — Novos Summon Target (killing one softlocks the Novos gate)
    };
}

bool DcNeverTargetRegistry::IsNeverTarget(uint32 mapId, uint32 entry)
{
    for (DcNeverTargetRow const& r : kRows)
        if (r.mapId == mapId && r.entry == entry)
            return true;
    return false;
}
