/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Affero General Public License as published by the
 * Free Software Foundation; either version 3 of the License, or (at your
 * option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program. If not, see <http://www.gnu.org/licenses/>.
 */

// Paths of Fate: starting traits (PerkTraitRules.h) and the perks that are script hooks (numbers: Esteria_Paths_of_Fate_Design_v1.md
// §3, as reworded in the EsteriaPerks addon's Data.lua). Effects that need a core call site are in game/Handlers/PerkEffects.cpp.
// Not wired: Mobile Workshop (summons) and the bot perks (Quick Orders, Rally Point, Watchful Guard, Formation Discipline,
// Companion Bond, Warband Marshal).

#include "DBCStores.h"
#include "Formulas.h"
#include "GameObject.h"
#include "GameTime.h"
#include "Group.h"
#include "GroupReference.h"
#include "LootMgr.h"
#include "Map.h"
#include "ObjectAccessor.h"
#include "ObjectMgr.h"
#include "PerkFx.h"
#include "PerkRules.h"
#include "CombatManager.h"
#include "Creature.h"
#include "PerkTraitRules.h"
#include "Pet.h"
#include "Player.h"
#include "ReputationMgr.h"
#include "ScriptMgr.h"
#include "Spell.h"
#include "SpellAuras.h"
#include "SpellInfo.h"

namespace
{
    namespace Perk = EsteriaPerkFx::Id;

    constexpr uint32 SPELL_FIND_TREASURE = 2481; // the dwarf racial's chest tracking, used for Keen Eye
    constexpr uint32 SPELL_HEARTHSTONE = 8690;
constexpr uint32 SPELL_HOUSE_HEARTH = 9500102, HOUSE_HEARTH_ITEM = 9500200; // mod-esteria-housing
    constexpr uint32 SPELL_ATTR2_FOOD = 0x20000000; // SPELL_ATTR2_FOOD_BUFF, not named in this fork
    constexpr float NEARBY = 60.0f;                 // "nearby" for group perks, yards
    constexpr uint32 UNDERWORLD_DAILY_CAP = 10 * GOLD;

    // First Aid ranks; bandages are periodic heals from these spells.
    constexpr uint32 BANDAGES[] = { 746, 1159, 3267, 3268, 7926, 7927, 10838, 10839, 18608, 18610, 27030, 27031, 45543, 45544 };

    struct State
    {
        uint32 firstStrikeReady = 0;  // ms game time the next first strike may arm
        bool firstStrikeArmed = false;
        uint32 opportunistReady = 0;
        uint32 finisherReady = 0;
        uint32 finisherUntil = 0;
        ObjectGuid finisherTarget;
        uint32 holdReady = 0;
        uint32 victoryReady = 0;
        uint32 holdUntil = 0;
        uint32 secondWindReady = 0;
        uint8 secondWindTicks = 0;
        uint32 secondWindNext = 0;
        uint32 underworldDay = 0;
        uint32 underworldCopper = 0;
        uint32 nextTick = 0;          // 1 sec housekeeping
        uint8 rationTicks = 0;
        uint32 shieldLeft = 0;        // Unbroken, Diehard and Lifeline feed one shield
        uint32 shieldUntil = 0;
        uint32 unbrokenReady = 0;
        uint32 diehardReady = 0;
        uint32 lifelineReady = 0;
        uint32 houseHearthPending = 0; // ms until which a fresh House Hearthstone cooldown may be scaled
uint32 hearthPending = 0;     // ms until which a fresh Hearthstone cooldown may still be shortened
        // Starting traits
        ObjectGuid fightTarget;       // Relentless: the creature being fought, and since when
        uint32 fightSince = 0;
        uint32 lastCombatEnd = 0;     // Ambusher
        bool ambushArmed = false;
        uint32 ambushAfterUntil = 0;
        uint32 wildReady = 0;         // Wild Card
        uint32 wildUntil = 0;
        bool wildUp = false;
        uint32 graveReady = 0;        // Grave Feeder
    };

    // shortcut: keyed by guid in memory; daily caps and cooldowns reset on a restart, move into the characters db if abused.
    std::unordered_map<ObjectGuid, State> states;

    uint32 NowMs() { return uint32(GameTime::GetGameTimeMS().count()); }
    uint32 Today() { return uint32(GameTime::GetGameTime().count() / DAY); }

    EsteriaTraits::Mods const& Mods(Player const* player) { return player->GetEsteriaTraitMods(); }

    bool IsPvpMap(Player const* player)
    {
        Map const* map = player->GetMap();
        return map && map->IsBattlegroundOrArena();
    }

    // Value of rank 1 / rank 2 of a card, or 0 when the player does not own it (or is in rated PvP for `pve`).
    float ByRank(Player const* player, uint8 perk, float r1, float r2 = 0.0f, bool pve = false)
    {
        uint8 const rank = player->GetEsteriaPerkRank(perk);
        if (!rank || (pve && IsPvpMap(player)))
            return 0.0f;
        return rank >= 2 ? r2 : r1;
    }

    // The best rank of `perk` among the player's group members near them, not counting the player.
    uint8 BestNearbyRank(Player const* player, uint8 perk)
    {
        uint8 best = 0;
        Group const* group = player->GetGroup();
        if (!group)
            return 0;
        for (GroupReference const* ref = group->GetFirstMember(); ref; ref = ref->next())
        {
            Player const* member = ref->GetSource();
            if (member && member != player && member->IsInMap(player) && member->IsWithinDist(player, NEARBY, false))
                best = std::max(best, member->GetEsteriaPerkRank(perk));
        }
        return best;
    }

    bool NearbyMemberBelow(Player const* player, uint8 pct)
    {
        Group const* group = player->GetGroup();
        if (!group)
            return false;
        for (GroupReference const* ref = group->GetFirstMember(); ref; ref = ref->next())
        {
            Player const* member = ref->GetSource();
            if (member && member != player && member->IsAlive() && member->IsInMap(player) &&
                member->IsWithinDist(player, 40.0f, false) && member->HealthBelowPct(pct))
                return true;
        }
        return false;
    }

    void Scale(uint32& value, float bonus)
    {
        if (bonus != 0.0f)
            value = uint32(std::max(0.0f, float(value) * (1.0f + bonus)));
    }

    // A creature no player owns. Starting traits only ever apply against these: a player's pet, totem or guardian
    // is that player, so nothing here can leak into a fight between players.
    bool IsWild(Unit const* unit)
    {
        return unit && unit->IsCreature() && !unit->GetCharmerOrOwnerPlayerOrPlayerItself();
    }

    bool IsBoss(Creature const* creature)
    {
        return creature->isWorldBoss() || creature->IsDungeonBoss();
    }

    bool GuildMateNearby(Player const* player)
    {
        Group const* group = player->GetGroup();
        if (!group || !player->GetGuildId())
            return false;
        for (GroupReference const* ref = group->GetFirstMember(); ref; ref = ref->next())
        {
            Player const* member = ref->GetSource();
            if (member && member != player && member->GetGuildId() == player->GetGuildId() && member->IsInMap(player)
                && member->IsWithinDist(player, NEARBY, false))
                return true;
        }
        return false;
    }

    // Starting traits on damage the player deals to a wild creature. `spell` is null for a white hit. The gains
    // stop at +6% however many traits line up; the losses always apply.
    float TraitDealt(Player* player, Unit* victim, SpellInfo const* spell, bool periodic)
    {
        using namespace EsteriaTraits;
        EsteriaTraits::Mods const& mods = Mods(player);
        if (!mods.any || !IsWild(victim) || IsPvpMap(player))
            return 0.0f;
        Creature* creature = victim->ToCreature();
        State& state = states[player->GetGUID()];
        EsteriaPerkFx::CoreState const& core = EsteriaPerkFx::StateOf(player->GetGUID());
        uint32 const now = NowMs();

        Sum sum;
        sum.add(mods, DmgAll);
        if (player->GetPet())
            sum.add(mods, OwnerDmgPet);
        float const health = creature->GetHealthPct();
        if (health > 90.0f) sum.add(mods, DmgTargetAbove90);
        if (health > 75.0f) sum.add(mods, DmgTargetAbove75);
        if (health < 30.0f) sum.add(mods, DmgTargetBelow30);
        if (health < 25.0f) sum.add(mods, DmgTargetBelow25);
        switch (creature->GetCreatureType())
        {
            case CREATURE_TYPE_BEAST: sum.add(mods, DmgBeast); break;
            case CREATURE_TYPE_HUMANOID: sum.add(mods, DmgHumanoid); break;
            case CREATURE_TYPE_UNDEAD: sum.add(mods, DmgUndead); break;
            case CREATURE_TYPE_ELEMENTAL: sum.add(mods, DmgElemental); break;
            default: break;
        }
        if (creature->isElite())
            sum.add(mods, DmgElite);
        // Enemies are the creatures in combat with the player, not whatever stands nearby.
        size_t const foes = player->GetCombatManager().GetPvECombatRefs().size();
        if (foes <= 1) sum.add(mods, DmgSingle);
        else if (foes >= 3) sum.add(mods, DmgCrowd);
        sum.add(mods, player->GetGroup() ? DmgGrouped : DmgSolo);
        sum.add(mods, EsteriaPerkFx::IsNight() ? DmgNight : DmgDay);
        if (player->HealthBelowPct(35))
            sum.add(mods, DmgLowHealth);

        // Relentless: how long this creature has been the one being hit.
        if (state.fightTarget != creature->GetGUID())
        {
            state.fightTarget = creature->GetGUID();
            state.fightSince = now;
        }
        if (now - state.fightSince >= 8 * IN_MILLISECONDS) sum.add(mods, DmgFightLong);
        else if (now - state.fightSince < 5 * IN_MILLISECONDS) sum.add(mods, DmgFightEarly);

        // Ambusher: the opening hit, then the lull after it.
        if (state.ambushArmed)
        {
            state.ambushArmed = false;
            state.ambushAfterUntil = now + 6 * IN_MILLISECONDS;
            sum.add(mods, Ambush);
        }
        else if (now < state.ambushAfterUntil)
            sum.add(mods, AmbushAfter);

        if (now < state.wildUntil)
            sum.add(mods, state.wildUp ? WildUp : WildDown);

        if (!spell || spell->IsAutoRepeatRangedSpell())
            sum.add(mods, DmgAuto);
        else if (spell->DmgClass == SPELL_DAMAGE_CLASS_MELEE || spell->DmgClass == SPELL_DAMAGE_CLASS_RANGED)
            sum.add(mods, DmgSpecial);
        else
        {
            sum.add(mods, DmgSpell).add(mods, periodic ? DmgSpellPeriodic : DmgSpellDirect);
            if (core.stillSince && now - core.stillSince >= 3 * IN_MILLISECONDS) sum.add(mods, DmgSpellStill);
            if (player->isMoving()) sum.add(mods, DmgSpellMoving);
            int32 const cast = spell->CastTimeEntry ? spell->CastTimeEntry->CastTime : 0;
            if (cast > 1500) sum.add(mods, DmgSpellSlow);
            if (cast > 0) sum.add(mods, DmgSpellCast);
            else if (core.lastMoved && now - core.lastMoved <= 3 * IN_MILLISECONDS) sum.add(mods, DmgSpellInstantMoved);
        }
        return sum.total(0.06f);
    }

    // Starting traits on damage a wild creature deals to the player. Reductions stop at 8%.
    float TraitTaken(Player* player, Unit* attacker, SpellInfo const* spell)
    {
        using namespace EsteriaTraits;
        EsteriaTraits::Mods const& mods = Mods(player);
        if (!mods.any || !IsWild(attacker) || IsPvpMap(player))
            return 0.0f;
        Creature const* creature = attacker->ToCreature();
        EsteriaPerkFx::CoreState const& core = EsteriaPerkFx::StateOf(player->GetGUID());

        Sum sum;
        sum.add(mods, !spell || (spell->GetSchoolMask() & SPELL_SCHOOL_MASK_NORMAL) ? TakenPhysical : TakenMagic);
        if (player->HealthBelowPct(30)) sum.add(mods, TakenLowHealth);
        else if (player->HealthAbovePct(70)) sum.add(mods, TakenHighHealth);
        if (player->isMoving()) sum.add(mods, TakenMoving);
        else if (core.stillSince && NowMs() - core.stillSince >= 3 * IN_MILLISECONDS) sum.add(mods, TakenStill);
        if (!spell) sum.add(mods, TakenMelee);
        else if (spell->IsAffectingArea() && !IsBoss(creature)) sum.add(mods, TakenArea);
        sum.add(mods, player->GetGroup() ? TakenGrouped : TakenSolo);
        if (creature->isElite())
            sum.add(mods, TakenElite);
        switch (creature->GetCreatureType())
        {
            case CREATURE_TYPE_UNDEAD: sum.add(mods, TakenUndead); break;
            case CREATURE_TYPE_BEAST: case CREATURE_TYPE_DRAGONKIN: case CREATURE_TYPE_GIANT:
            case CREATURE_TYPE_HUMANOID: case CREATURE_TYPE_CRITTER: sum.add(mods, TakenLiving); break;
            default: break;
        }
        return sum.total(10.0f, 0.08f);
    }

    // A player's combat pet against wild creatures: Pet Trainer, Protective Handler.
    void PetTraits(Unit* target, Unit* attacker, uint32& damage)
    {
        using namespace EsteriaTraits;
        if (attacker && attacker->IsPet() && IsWild(target))
        {
            Player const* owner = attacker->GetCharmerOrOwnerPlayerOrPlayerItself();
            if (owner && !IsPvpMap(owner))
                Scale(damage, Sum().add(Mods(owner), PetDmg).total(0.06f));
        }
        else if (target && target->IsPet() && IsWild(attacker))
        {
            Player const* owner = target->GetCharmerOrOwnerPlayerOrPlayerItself();
            if (owner && !IsPvpMap(owner))
                Scale(damage, Sum().add(Mods(owner), PetTaken).total(10.0f, 0.08f));
        }
    }

    // A zone counts as fully explored when every explorable area inside it is known.
    bool ZoneExplored(Player const* player, uint32 zoneId)
    {
        static std::unordered_map<uint32, std::vector<uint32>> flags;
        auto it = flags.find(zoneId);
        if (it == flags.end())
        {
            std::vector<uint32> list;
            for (uint32 i = 0; i < sAreaTableStore.GetNumRows(); ++i)
                if (AreaTableEntry const* area = sAreaTableStore.LookupEntry(i))
                    if ((area->ID == zoneId || area->zone == zoneId) && area->exploreFlag && area->exploreFlag < PLAYER_EXPLORED_ZONES_SIZE * 32)
                        list.push_back(area->exploreFlag);
            it = flags.emplace(zoneId, std::move(list)).first;
        }
        if (it->second.empty())
            return false;
        for (uint32 flag : it->second)
            if (!(player->GetUInt32Value(PLAYER_EXPLORED_ZONES_1 + flag / 32) & (1u << (flag % 32))))
                return false;
        return true;
    }

    // Capital city factions; a character's home city follows its race. shortcut: a race that is not one of the ten
    // stock ones counts the capital of its team (Stormwind or Orgrimmar); give it its own entry when it has a city.
    bool IsCapitalFaction(uint32 faction)
    {
        static std::set<uint32> const capitals = { 72, 47, 69, 54, 930, 76, 81, 68, 530, 911 };
        return capitals.count(faction) != 0;
    }

    uint32 HomeFaction(Player const* player)
    {
        switch (player->getRace())
        {
            case RACE_HUMAN: return 72;
            case RACE_ORC: return 76;
            case RACE_DWARF: return 47;
            case RACE_NIGHTELF: return 69;
            case RACE_UNDEAD_PLAYER: return 68;
            case RACE_TAUREN: return 81;
            case RACE_GNOME: return 54;
            case RACE_TROLL: return 530;
            case RACE_BLOODELF: return 911;
            case RACE_DRAENEI: return 930;
            default: return player->GetTeamId() == TEAM_ALLIANCE ? 72 : 76;
        }
    }

    bool IsCommon(ItemTemplate const* proto, bool consumables)
    {
        return proto && proto->Quality <= ITEM_QUALITY_NORMAL &&
            (proto->Class == ITEM_CLASS_TRADE_GOODS || (consumables && proto->Class == ITEM_CLASS_CONSUMABLE));
    }

    // Adds one extra of an item under a daily cap.
    void GiveExtra(Player* player, uint32 itemId, uint32& counter, uint32 cap)
    {
        if (counter >= cap)
            return;
        if (player->AddItem(itemId, 1))
            ++counter;
    }

    // Damage the player deals to a creature: First Strike, Opportunist, Finisher's Resolve and the starting traits.
    void OnPlayerDeals(Player* player, Unit* victim, uint32& damage, SpellInfo const* spell = nullptr)
    {
        Creature* creature = victim ? victim->ToCreature() : nullptr;
        if (!creature || !damage)
            return;

        float bonus = TraitDealt(player, victim, spell, false);

        if (player->GetEsteriaPerkRank(Perk::FirstStrike) || player->GetEsteriaPerkRank(Perk::Opportunist) ||
            player->GetEsteriaPerkRank(Perk::FinisherResolve))
        {
            State& state = states[player->GetGUID()];
            uint32 const now = NowMs();

            if (state.firstStrikeArmed)
            {
                state.firstStrikeArmed = false;
                state.firstStrikeReady = now + 30 * IN_MILLISECONDS;
                bonus += ByRank(player, Perk::FirstStrike, 0.02f, 0.04f, true);
            }
            if (now >= state.opportunistReady && creature->HasUnitState(UNIT_STATE_STUNNED | UNIT_STATE_ROOT | UNIT_STATE_CONFUSED))
            {
                float const opportunist = ByRank(player, Perk::Opportunist, 0.03f, 0.06f, true);
                if (opportunist > 0.0f)
                {
                    state.opportunistReady = now + 45 * IN_MILLISECONDS;
                    bonus += opportunist;
                }
            }
            if (player->GetEsteriaPerkRank(Perk::FinisherResolve) && !IsPvpMap(player))
            {
                if (now >= state.finisherReady && creature->HealthBelowPct(20))
                {
                    state.finisherReady = now + 2 * MINUTE * IN_MILLISECONDS;
                    state.finisherUntil = now + 6 * IN_MILLISECONDS;
                    state.finisherTarget = creature->GetGUID();
                }
                if (now < state.finisherUntil && state.finisherTarget == creature->GetGUID())
                    bonus += 0.03f;
            }
        }
        Scale(damage, bonus);
    }

    // Damage a creature deals to the player: Guarded Reflex, Hold the Line and the starting traits.
    void OnPlayerTakes(Player* player, Unit* attacker, uint32& damage, SpellInfo const* spell = nullptr)
    {
        if (!attacker || !attacker->ToCreature() || !damage || IsPvpMap(player))
            return;
        uint32 const now = NowMs();
        Scale(damage, TraitTaken(player, attacker, spell));

        // Guarded Reflex: the first hit after the window opened is softened, the window closes either way.
        if (player->GetEsteriaPerkRank(Perk::GuardedReflex))
        {
            EsteriaPerkFx::CoreState& core = EsteriaPerkFx::StateOf(player->GetGUID());
            if (core.guardUntil && now >= core.guardFrom)
            {
                if (now < core.guardUntil)
                    Scale(damage, -ByRank(player, Perk::GuardedReflex, 0.03f, 0.06f));
                core.guardUntil = 0;
            }
        }

        if (!player->GetEsteriaPerkRank(Perk::HoldLine))
            return;
        State& state = states[player->GetGUID()];
        if (now >= state.holdReady && NearbyMemberBelow(player, 35))
        {
            state.holdReady = now + 2 * MINUTE * IN_MILLISECONDS;
            state.holdUntil = now + 6 * IN_MILLISECONDS;
        }
        if (now < state.holdUntil)
            Scale(damage, -0.04f);
    }

    void Absorb(State& state, uint32& damage, uint32 now)
    {
        if (!state.shieldLeft)
            return;
        if (now >= state.shieldUntil)
        {
            state.shieldLeft = 0;
            return;
        }
        uint32 const absorbed = std::min(damage, state.shieldLeft);
        damage -= absorbed;
        state.shieldLeft -= absorbed;
    }

    void Shield(State& state, Player const* player, float pct, uint32 ms)
    {
        state.shieldLeft = std::max(state.shieldLeft, uint32(float(player->GetMaxHealth()) * pct));
        state.shieldUntil = NowMs() + ms;
    }

    class esteria_perk_units : public UnitScript
    {
    public:
        esteria_perk_units() : UnitScript("esteria_perk_units", true,
            { UNITHOOK_MODIFY_MELEE_DAMAGE, UNITHOOK_MODIFY_SPELL_DAMAGE_TAKEN, UNITHOOK_MODIFY_HEAL_RECEIVED,
              UNITHOOK_ON_DAMAGE, UNITHOOK_ON_AURA_APPLY, UNITHOOK_MODIFY_PERIODIC_DAMAGE_AURAS_TICK }) { }

        void ModifyMeleeDamage(Unit* target, Unit* attacker, uint32& damage) override
        {
            if (Player* player = attacker ? attacker->ToPlayer() : nullptr)
                OnPlayerDeals(player, target, damage);
            if (Player* player = target ? target->ToPlayer() : nullptr)
                OnPlayerTakes(player, attacker, damage);
            PetTraits(target, attacker, damage);
        }

        // Damage over time: only the starting traits, the perks above are about single hits.
        void ModifyPeriodicDamageAurasTick(Unit* target, Unit* attacker, uint32& damage, SpellInfo const* spellInfo) override
        {
            if (!damage || !spellInfo)
                return;
            if (Player* player = attacker ? attacker->ToPlayer() : nullptr)
                Scale(damage, TraitDealt(player, target, spellInfo, true));
            if (Player* player = target ? target->ToPlayer() : nullptr)
                Scale(damage, TraitTaken(player, attacker, spellInfo));
            PetTraits(target, attacker, damage);
        }

        void ModifySpellDamageTaken(Unit* target, Unit* attacker, int32& damage, SpellInfo const* spellInfo) override
        {
            if (damage <= 0)
                return;
            uint32 value = uint32(damage);
            PetTraits(target, attacker, value);
            if (Player* player = attacker ? attacker->ToPlayer() : nullptr)
                OnPlayerDeals(player, target, value, spellInfo);
            if (Player* player = target ? target->ToPlayer() : nullptr)
            {
                OnPlayerTakes(player, attacker, value, spellInfo);
                // Steady Focus: a creature's spell opens a window of reduced pushback (spent in Spell::Delayed).
                if (attacker && attacker->IsCreature() && player->GetEsteriaPerkRank(Perk::SteadyFocus))
                {
                    EsteriaPerkFx::CoreState& core = EsteriaPerkFx::StateOf(player->GetGUID());
                    uint32 const now = NowMs();
                    if (now >= core.steadyReady)
                    {
                        core.steadyReady = now + 30 * IN_MILLISECONDS;
                        core.steadyUntil = now + 5 * IN_MILLISECONDS;
                    }
                }
            }
            damage = int32(value);
        }

        void ModifyHealReceived(Unit* target, Unit* healer, uint32& heal, SpellInfo const* spellInfo) override
        {
            using namespace EsteriaTraits;
            Player* player = target ? target->ToPlayer() : nullptr;
            if (!spellInfo)
                return;
            bool const bandage = std::find(std::begin(BANDAGES), std::end(BANDAGES), spellInfo->Id) != std::end(BANDAGES);
            bool const potion = spellInfo->SpellFamilyName == SPELLFAMILY_POTION;

            // A healing spell: the healer's traits. Not in battlegrounds, nor while either side fights a player.
            Player* caster = healer ? healer->ToPlayer() : nullptr;
            if (caster && !bandage && !potion && Mods(caster).any && !IsPvpMap(caster)
                && !caster->GetCombatManager().HasPvPCombat() && !(player && player->GetCombatManager().HasPvPCombat()))
            {
                Sum sum;
                if (caster == player)
                    sum.add(Mods(caster), HealSelf);
                else if (player)
                {
                    sum.add(Mods(caster), HealOthers);
                    if (player->HealthBelowPct(40) && caster->IsInSameRaidWith(player))
                        sum.add(Mods(caster), HealLowParty);
                }
                Scale(heal, sum.total(0.10f));
            }
            // Bloodscent: any healing lands weaker on a badly hurt holder.
            if (player && player->HealthBelowPct(35) && !IsPvpMap(player) && !player->GetCombatManager().HasPvPCombat())
                Scale(heal, Mods(player).total(HealTakenLow));

            if (!player || healer != target)
                return;
            if (bandage)
                Scale(heal, ByRank(player, Perk::FieldMedic, 0.15f, 0.30f) + Sum().add(Mods(player), BandageHeal).total(0.25f));
            else if (potion)
            {
                Scale(heal, Sum().add(Mods(player), PotionHeal).total(0.25f));
                // Lifeline: a healing potion below 35% health also shields.
                if (player->GetEsteriaPerkRank(Perk::Lifeline) && player->HealthBelowPct(35))
                {
                    State& state = states[player->GetGUID()];
                    uint32 const now = NowMs();
                    if (now >= state.lifelineReady)
                    {
                        state.lifelineReady = now + 5 * MINUTE * IN_MILLISECONDS;
                        Shield(state, player, 0.03f, 5 * IN_MILLISECONDS);
                    }
                }
            }
        }

        // The shield (Unbroken, Diehard, Lifeline) takes damage first; Unbroken and Diehard trigger here.
        void OnDamage(Unit* /*attacker*/, Unit* victim, uint32& damage) override
        {
            Player* player = victim ? victim->ToPlayer() : nullptr;
            if (!player || !damage || !player->IsAlive())
                return;
            auto const it = states.find(player->GetGUID());
            if (it == states.end())
                return;
            State& state = it->second;
            uint32 const now = NowMs();
            Absorb(state, damage, now);

            if (!damage || IsPvpMap(player))
                return;
            uint32 const health = player->GetHealth();
            uint32 const threshold = player->GetMaxHealth() / 5;
            // shortcut: Unbroken uses its 10 min cooldown, not "once per boss attempt"; tighten when encounters are tracked.
            if (now >= state.unbrokenReady && player->GetEsteriaPerkRank(Perk::Unbroken) && health >= threshold &&
                health - std::min(damage, health) < threshold)
            {
                state.unbrokenReady = now + 10 * MINUTE * IN_MILLISECONDS;
                Shield(state, player, 0.12f, 6 * IN_MILLISECONDS);
                Absorb(state, damage, now);
            }
            Map const* map = player->GetMap();
            if (damage >= health && now >= state.diehardReady && player->GetEsteriaPerkRank(Perk::Diehard) && map && !map->Instanceable())
            {
                state.diehardReady = now + 20 * MINUTE * IN_MILLISECONDS;
                damage = health > 1 ? health - 1 : 0;
                Shield(state, player, 0.10f, 6 * IN_MILLISECONDS);
            }
        }

        // Food buffs: Ration Keeper, and Frugal Survivor's non-combat buffs (food, flasks and elixirs).
        void OnAuraApply(Unit* unit, Aura* aura) override
        {
            Player* player = unit ? unit->ToPlayer() : nullptr;
            if (!player || !aura || aura->GetMaxDuration() <= 0)
                return;
            using namespace EsteriaTraits;
            SpellInfo const* spell = aura->GetSpellInfo();
            EsteriaTraits::Mods const& mods = Mods(player);
            bool const food = (spell->AttributesEx2 & SPELL_ATTR2_FOOD) != 0;
            bool const flask = spell->SpellFamilyName == SPELLFAMILY_POTION && aura->GetMaxDuration() >= 10 * MINUTE * IN_MILLISECONDS;
            float bonus = 0.0f;
            if (food || flask)
            {
                if (food)
                    bonus += ByRank(player, Perk::RationKeeper, 0.10f, 0.20f);
                bonus += Sum().add(mods, food ? FoodDuration : ElixirDuration).total(0.25f);
            }
            else if (mods.any && !spell->IsPositive() && !IsPvpMap(player))
            {
                // Poisons, diseases, slows, roots, fears and stuns from ordinary creatures; never a boss's.
                Unit const* caster = aura->GetCaster();
                if (!IsWild(caster) || IsBoss(caster->ToCreature()))
                    return;
                uint64 const mechanics = spell->GetAllEffectsMechanicMask();
                Sum sum;
                if (spell->Dispel == DISPEL_POISON) sum.add(mods, PoisonDuration);
                if (spell->Dispel == DISPEL_DISEASE) sum.add(mods, DiseaseDuration);
                if (mechanics & (1ULL << MECHANIC_SNARE)) sum.add(mods, SlowDuration);
                if (mechanics & (1ULL << MECHANIC_ROOT)) sum.add(mods, RootDuration);
                if (mechanics & (1ULL << MECHANIC_FEAR)) sum.add(mods, FearDuration);
                if (mechanics & (1ULL << MECHANIC_STUN)) sum.add(mods, StunDuration);
                bonus = sum.total();
            }
            if (bonus == 0.0f)
                return;
            int32 const duration = std::max(1, int32(float(aura->GetMaxDuration()) * (1.0f + bonus)));
            aura->SetMaxDuration(duration);
            aura->SetDuration(duration);
        }
    };

    class esteria_perk_players : public PlayerScript
    {
    public:
        esteria_perk_players() : PlayerScript("esteria_perk_players", {
            PLAYERHOOK_ON_LOGIN, PLAYERHOOK_ON_LOGOUT, PLAYERHOOK_ON_UPDATE, PLAYERHOOK_ON_GIVE_EXP,
            PLAYERHOOK_ON_GIVE_REPUTATION, PLAYERHOOK_ON_BEFORE_LOOT_MONEY, PLAYERHOOK_ON_AFTER_UPDATE_MAX_HEALTH,
            PLAYERHOOK_ON_CREATURE_KILL, PLAYERHOOK_ON_PLAYER_ENTER_COMBAT, PLAYERHOOK_ON_PLAYER_LEAVE_COMBAT,
            PLAYERHOOK_ON_SPELL_CAST, PLAYERHOOK_ON_LOOT_ITEM, PLAYERHOOK_ON_CREATE_ITEM,
            PLAYERHOOK_ON_BEFORE_DURABILITY_REPAIR, PLAYERHOOK_ON_QUEST_COMPUTE_EXP,
            PLAYERHOOK_ON_AFTER_UPDATE_MAX_POWER, PLAYERHOOK_ON_PLAYER_JUST_DIED, PLAYERHOOK_ON_QUEST_ABANDON,
            PLAYERHOOK_ON_PLAYER_COMPLETE_QUEST }) { }

        static bool WatchesDeaths(Player const* player)
        {
            EsteriaTraits::Mods const& mods = Mods(player);
            return mods.pos[EsteriaTraits::QuestGoldClean] != 0.0f || mods.neg[EsteriaTraits::QuestGoldDied] != 0.0f;
        }

        void OnPlayerLogin(Player* player) override
        {
            states[player->GetGUID()];
            // High Roller: which quests in the log were running when the character died.
            if (WatchesDeaths(player))
                if (QueryResult result = CharacterDatabase.Query("SELECT quest FROM character_esteria_trait_questdeath WHERE guid = {}", player->GetGUID().GetCounter()))
                    do
                        EsteriaPerkFx::StateOf(player->GetGUID()).diedQuests.insert((*result)[0].Get<uint32>());
                    while (result->NextRow());
        }

        void OnPlayerJustDied(Player* player) override
        {
            if (!WatchesDeaths(player))
                return;
            for (auto const& [quest, status] : player->getQuestStatusMap())
                if ((status.Status == QUEST_STATUS_INCOMPLETE || status.Status == QUEST_STATUS_COMPLETE)
                    && EsteriaPerkFx::StateOf(player->GetGUID()).diedQuests.insert(quest).second)
                    CharacterDatabase.Execute("REPLACE INTO character_esteria_trait_questdeath (guid, quest) VALUES ({}, {})", player->GetGUID().GetCounter(), quest);
        }

        // A quest that was abandoned or handed in starts fresh the next time.
        void ForgetDeath(Player* player, uint32 quest)
        {
            if (EsteriaPerkFx::StateOf(player->GetGUID()).diedQuests.erase(quest))
                CharacterDatabase.Execute("DELETE FROM character_esteria_trait_questdeath WHERE guid = {} AND quest = {}", player->GetGUID().GetCounter(), quest);
        }

        void OnPlayerQuestAbandon(Player* player, uint32 questId) override { ForgetDeath(player, questId); }

        void OnPlayerCompleteQuest(Player* player, Quest const* quest) override
        {
            EsteriaPerkFx::StateOf(player->GetGUID()).rewardQuest = 0;
            ForgetDeath(player, quest->GetQuestId());
        }

        void OnPlayerLogout(Player* player) override
        {
            states.erase(player->GetGUID());
            EsteriaPerkFx::Forget(player->GetGUID());
        }

        // Once a second: Keen Eye's tracking, Second Wind's ticks, movement speed, Shared Rations, Hearthwalker.
        void OnPlayerUpdate(Player* player, uint32 /*diff*/) override
        {
            uint32 const now = NowMs();
            auto const it = states.find(player->GetGUID());
            if (it == states.end() || now < it->second.nextTick)
                return;
            State& state = it->second;
            state.nextTick = now + IN_MILLISECONDS;

            bool const eye = player->GetEsteriaPerkRank(Perk::KeenEye) > 0;
            if (eye && !player->HasAura(SPELL_FIND_TREASURE))
                player->AddAura(SPELL_FIND_TREASURE, player);
            else if (!eye && player->HasAura(SPELL_FIND_TREASURE))
                player->RemoveAurasDueToSpell(SPELL_FIND_TREASURE);

            if (state.secondWindTicks && now >= state.secondWindNext)
            {
                --state.secondWindTicks;
                state.secondWindNext = now + IN_MILLISECONDS;
                if (player->IsAlive() && !player->IsInCombat())
                    player->SetHealth(std::min(player->GetMaxHealth(), player->GetHealth() + player->GetMaxHealth() / 200));
                else
                    state.secondWindTicks = 0;
            }

            // What the starting traits need to know about movement: standing still, just moved, travelling.
            EsteriaPerkFx::CoreState& core = EsteriaPerkFx::StateOf(player->GetGUID());
            if (player->isMoving())
            {
                core.stillSince = 0;
                core.lastMoved = now;
                if (player->IsInCombat())
                    core.travelSince = 0;
                else if (!core.travelSince)
                    core.travelSince = now;
            }
            else
            {
                if (!core.stillSince)
                    core.stillSince = now;
                core.travelSince = 0;
            }
            // Run Rabbit Run: a burst of speed when badly hurt.
            if (Mods(player).pos[EsteriaTraits::MoveLowHealthProc] > 0.0f && player->IsAlive() && player->HealthBelowPct(25)
                && now >= core.rabbitReady && !IsPvpMap(player) && !player->GetCombatManager().HasPvPCombat())
            {
                core.rabbitReady = now + MINUTE * IN_MILLISECONDS;
                core.rabbitUntil = now + 5 * IN_MILLISECONDS;
            }

            // Frenzied: attack speed is +4% for a while after a kill and -3% the rest of the time. The old modifier comes
            // off before the new one goes on, so repeated changes never leave a remainder.
            {
                EsteriaTraits::Mods const& traitMods = Mods(player);
                float want = 0.0f;
                if (player->IsAlive() && !IsPvpMap(player) && !player->GetCombatManager().HasPvPCombat())
                    want = 100.0f * (now < core.frenzyUntil ? traitMods.pos[EsteriaTraits::AttackSpeedFrenzy] : traitMods.neg[EsteriaTraits::AttackSpeedIdle]);
                if (want != core.frenzyApplied)
                {
                    for (WeaponAttackType type : { BASE_ATTACK, OFF_ATTACK, RANGED_ATTACK })
                    {
                        if (core.frenzyApplied != 0.0f)
                            player->ApplyAttackTimePercentMod(type, core.frenzyApplied, false);
                        if (want != 0.0f)
                            player->ApplyAttackTimePercentMod(type, want, true);
                    }
                    core.frenzyApplied = want;
                }
            }

            // Speed bonuses depend on position and combat, so they are re-checked here and pushed into UpdateSpeed on change.
            float const move = EsteriaPerkFx::MoveBonus(player);
            if (move != core.moveBonus)
            {
                core.moveBonus = move;
                player->UpdateSpeed(MOVE_RUN, true);
            }

            // Hearthwalker: shorten the Hearthstone cooldown once, as soon as the cast has started it.
            if (state.hearthPending)
            {
                if (now >= state.hearthPending)
                    state.hearthPending = 0;
                else if (player->HasSpellCooldown(SPELL_HEARTHSTONE))
                {
                    state.hearthPending = 0;
                    // Hearthwalker takes 15 minutes off; the traits scale the 30 minute cooldown.
                    int32 change = int32(30.0f * MINUTE * IN_MILLISECONDS * Mods(player).total(EsteriaTraits::Hearth));
                    if (player->GetEsteriaPerkRank(Perk::Hearthwalker))
                        change -= 15 * MINUTE * int32(IN_MILLISECONDS);
                    if (change)
                        player->ModifySpellCooldown(SPELL_HEARTHSTONE, change);
                }
            }

            // Wandering Tenant: the House Hearthstone's cooldown (set by the housing module) scales once it has started.
            if (state.houseHearthPending)
            {
                if (now >= state.houseHearthPending)
                    state.houseHearthPending = 0;
                else if (player->HasSpellCooldown(SPELL_HOUSE_HEARTH))
                {
                    state.houseHearthPending = 0;
                    ItemTemplate const* stone = sObjectMgr->GetItemTemplate(HOUSE_HEARTH_ITEM);
                    int32 const change = stone ? int32(float(stone->Spells[0].SpellCooldown) * Mods(player).total(EsteriaTraits::HouseHearth)) : 0;
                    if (change)
                        player->ModifySpellCooldown(SPELL_HOUSE_HEARTH, change);
                }
            }

            // Shared Rations: every 5 sec, party members near a rank holder regain a little extra health out of combat.
            // shortcut: base regeneration is approximated as 2% of maximum health per 5 sec, not read from the regen tables.
            if (++state.rationTicks >= 5)
            {
                state.rationTicks = 0;
                if (player->IsAlive() && !player->IsInCombat() && player->GetHealth() < player->GetMaxHealth())
                {
                    static float const values[] = { 0.0f, 0.03f, 0.06f };
                    float const pct = values[std::min<uint8>(BestNearbyRank(player, Perk::SharedRations), 2)];
                    if (pct > 0.0f)
                        player->SetHealth(std::min(player->GetMaxHealth(), player->GetHealth() + std::max<uint32>(1, uint32(float(player->GetMaxHealth()) * 0.02f * pct))));
                }
            }
        }

        void OnPlayerEnterCombat(Player* player, Unit* enemy) override
        {
            if (!enemy || !enemy->ToCreature())
                return;
            State& state = states[player->GetGUID()];
            uint32 const now = NowMs();
            if (player->GetEsteriaPerkRank(Perk::FirstStrike) && now >= state.firstStrikeReady)
                state.firstStrikeArmed = true;

            EsteriaTraits::Mods const& mods = Mods(player);
            if (!mods.any || !IsWild(enemy) || IsPvpMap(player))
                return;
            // Ambusher: armed by a fight that starts after 10 seconds of peace.
            if (mods.pos[EsteriaTraits::Ambush] > 0.0f && now - state.lastCombatEnd >= 10 * IN_MILLISECONDS)
                state.ambushArmed = true;
            // Wild Card: every two minutes the next fight opens with a coin toss, the server's.
            if (mods.pos[EsteriaTraits::WildUp] > 0.0f && now >= state.wildReady)
            {
                state.wildReady = now + 2 * MINUTE * IN_MILLISECONDS;
                state.wildUntil = now + 10 * IN_MILLISECONDS;
                state.wildUp = roll_chance_i(50);
            }
        }

        void OnPlayerLeaveCombat(Player* player) override
        {
            State& state = states[player->GetGUID()];
            state.firstStrikeArmed = false;
            state.ambushArmed = false;
            uint32 const now = NowMs();
            state.lastCombatEnd = now;
            if (player->GetEsteriaPerkRank(Perk::SecondWind) && player->IsAlive() && player->HealthBelowPct(30) &&
                now >= state.secondWindReady && !IsPvpMap(player))
            {
                state.secondWindReady = now + 3 * MINUTE * IN_MILLISECONDS;
                state.secondWindTicks = 10; // 10 ticks of 0.5% = 5% of maximum health over 10 sec
                state.secondWindNext = now + IN_MILLISECONDS;
            }
        }

        void OnPlayerCreatureKill(Player* killer, Creature* killed) override
        {
            if (!killer->IsAlive() || killed->GetLevel() <= Acore::XP::GetGrayLevel(killer->GetLevel()))
                return;
            State& state = states[killer->GetGUID()];
            uint32 const now = NowMs();

            // Frenzied: a kill that still gives experience speeds the next eight seconds of attacks.
            if (Mods(killer).pos[EsteriaTraits::AttackSpeedFrenzy] > 0.0f && IsWild(killed) && !IsPvpMap(killer))
                EsteriaPerkFx::StateOf(killer->GetGUID()).frenzyUntil = now + 8 * IN_MILLISECONDS;

            // Grave Feeder: the same kind of kill, its own 10 second cooldown.
            float const feed = Mods(killer).pos[EsteriaTraits::KillHeal];
            if (feed > 0.0f && now >= state.graveReady && IsWild(killed) && !IsPvpMap(killer))
            {
                state.graveReady = now + 10 * IN_MILLISECONDS;
                killer->SetHealth(std::min(killer->GetMaxHealth(), killer->GetHealth() + uint32(float(killer->GetMaxHealth()) * feed)));
            }

            // Victory's Reward: a creature that still gives experience restores health.
            float const heal = ByRank(killer, Perk::VictoryReward, 0.015f, 0.03f, true);
            if (heal <= 0.0f)
                return;
            if (now < state.victoryReady)
                return;
            state.victoryReady = now + 20 * IN_MILLISECONDS;
            killer->SetHealth(std::min(killer->GetMaxHealth(), killer->GetHealth() + uint32(float(killer->GetMaxHealth()) * heal)));
        }

        // Kill and exploration experience. Quest experience is only ever changed in OnPlayerQuestComputeXP.
        void OnPlayerGiveXP(Player* player, uint32& amount, Unit* /*victim*/, uint8 xpSource) override
        {
            using namespace EsteriaTraits;
            EsteriaTraits::Mods const& mods = Mods(player);
            float bonus = 0.0f;
            if (xpSource == PlayerXPSource::XPSOURCE_EXPLORE)
            {
                bonus += ByRank(player, Perk::Cartographer, 0.10f, 0.20f);
                bonus += mods.total(ExploreXp);
            }
            else if (xpSource == PlayerXPSource::XPSOURCE_KILL)
            {
                // Tutor: the owner's grouped, nearby players earn more from shared kills.
                static float const values[] = { 0.0f, 0.02f, 0.04f };
                bonus += values[std::min<uint8>(BestNearbyRank(player, Perk::Tutor), 2)];
                if (mods.any)
                {
                    Sum sum;
                    sum.add(mods, KillXp).add(mods, GuildMateNearby(player) ? KillXpGuild : KillXpNoGuild);
                    if (player->GetRestBonus() <= 0.0f)
                        sum.add(mods, KillXpUnrested);
                    bonus += sum.total(0.15f);
                }
            }
            Scale(amount, bonus);
        }

        // Quest experience: the starting traits (gains stop at +15%), and Lorekeeper in a fully explored zone.
        void OnPlayerQuestComputeXP(Player* player, Quest const* quest, uint32& xpValue) override
        {
            if (!xpValue)
                return;
            using namespace EsteriaTraits;
            EsteriaTraits::Mods const& mods = Mods(player);
            Sum sum;
            sum.add(mods, QuestXp).add(mods, EsteriaPerkFx::QuestIsKill(quest) ? QuestXpKill : QuestXpDelivery);
            if (EsteriaPerkFx::QuestIsDungeon(player, quest))
                sum.add(mods, DungeonQuestXp);
            Scale(xpValue, sum.total(0.15f));
            if (!player->GetEsteriaPerkRank(Perk::Lorekeeper) || quest->GetZoneOrSort() <= 0)
                return;
            if (ZoneExplored(player, uint32(quest->GetZoneOrSort())))
                Scale(xpValue, 0.05f);
        }

        void OnPlayerGiveReputation(Player* player, int32 factionID, float& amount, ReputationSource source) override
        {
            using namespace EsteriaTraits;
            if (amount <= 0.0f)
                return;
            bool const quest = source == REPUTATION_SOURCE_QUEST || source == REPUTATION_SOURCE_DAILY_QUEST ||
                source == REPUTATION_SOURCE_WEEKLY_QUEST || source == REPUTATION_SOURCE_MONTHLY_QUEST ||
                source == REPUTATION_SOURCE_REPEATABLE_QUEST;
            FactionEntry const* faction = sFactionStore.LookupEntry(factionID);
            ReputationRank const rank = faction ? player->GetReputationMgr().GetRank(faction) : REP_NEUTRAL;

            float bonus = 0.0f;
            if (source == REPUTATION_SOURCE_KILL)
            {
                bonus += ByRank(player, Perk::FamiliarFace, 0.05f, 0.10f);
                if (player->GetMap() && player->GetMap()->IsDungeon())
                {
                    static float const values[] = { 0.0f, 0.03f, 0.06f };
                    bonus += values[std::min<uint8>(BestNearbyRank(player, Perk::SharedVictory), 2)];
                }
            }
            if (quest)
            {
                bonus += ByRank(player, Perk::Diplomat, 0.03f, 0.06f);
                if (rank == REP_NEUTRAL || rank == REP_FRIENDLY)
                    bonus += ByRank(player, Perk::Mediator, 0.10f);
                bonus += EsteriaTraits::Sum().add(Mods(player), EsteriaTraits::QuestRep).total(0.20f);
                if (Quest const* handedIn = sObjectMgr->GetQuestTemplate(EsteriaPerkFx::StateOf(player->GetGUID()).rewardQuest))
                    bonus += Sum().add(Mods(player), EsteriaPerkFx::QuestIsDungeon(player, handedIn) ? RepDungeon : RepOutdoor).total(0.20f);
            }
            // Home city and the other capitals' factions.
            if (uint32 const home = HomeFaction(player))
            {
                if (uint32(factionID) == home)
                    bonus += Mods(player).total(RepHome);
                else if (IsCapitalFaction(uint32(factionID)))
                    bonus += Mods(player).total(RepCapital);
            }
            // Sour Reputation: factions that belong to neither the Alliance nor the Horde.
            if (faction && faction->team != 469 && faction->team != 67 && faction->team != 891 && faction->team != 892)
                bonus += Mods(player).total(EsteriaTraits::NeutralRep);
            if (rank < REP_EXALTED)
                bonus += ByRank(player, Perk::PowerBroker, 0.10f);
            amount *= std::max(0.0f, 1.0f + bonus);
        }

        void OnPlayerBeforeLootMoney(Player* player, Loot* loot) override
        {
            using namespace EsteriaTraits;
            if (!loot || !loot->gold)
                return;
            EsteriaTraits::Mods const& mods = Mods(player);
            // Chest Rat: coin inside chests and other containers in the world.
            if (loot->sourceWorldObjectGUID.IsGameObject())
            {
                Scale(loot->gold, mods.total(GoldChest));
                return;
            }
            Creature* creature = ObjectAccessor::GetCreature(*player, loot->sourceWorldObjectGUID);
            if (!creature || creature->GetCreatureTemplate()->type != CREATURE_TYPE_HUMANOID)
                return;

            Scale(loot->gold, Sum().add(mods, GoldHumanoid).total(0.20f));

            // Underworld Contact (+10%) and Gold Nose (+5%) share one purse: up to 10 gold a day between them.
            float const extra = ByRank(player, Perk::UnderworldContact, 0.10f) + mods.pos[GoldHumanoidCapped];
            if (extra > 0.0f)
            {
                State& state = states[player->GetGUID()];
                if (state.underworldDay != Today())
                {
                    state.underworldDay = Today();
                    state.underworldCopper = 0;
                }
                uint32 const room = UNDERWORLD_DAILY_CAP - std::min(state.underworldCopper, UNDERWORLD_DAILY_CAP);
                uint32 const add = std::min(uint32(float(loot->gold) * extra), room);
                state.underworldCopper += add;
                loot->gold += add;
            }
        }

        // Maximum health from the starting traits, outside rated PvP; gains stop at +8%. Set from the full value
        // each time the stat is recomputed, so it never compounds, and SetMaxHealth clamps current health.
        void OnPlayerAfterUpdateMaxHealth(Player* player, float& value) override
        {
            if (!IsPvpMap(player))
                value *= 1.0f + EsteriaTraits::Sum().add(Mods(player), EsteriaTraits::MaxHealth).total(0.08f);
        }

        void OnPlayerAfterUpdateMaxPower(Player* player, Powers& power, float& value) override
        {
            if (power == POWER_MANA && !IsPvpMap(player))
                value *= 1.0f + Mods(player).total(EsteriaTraits::MaxMana);
        }

        // Favored Patron and the repair traits: vendor repairs.
        void OnPlayerBeforeDurabilityRepair(Player* player, ObjectGuid /*npc*/, ObjectGuid /*item*/, float& discountMod, uint8 /*guildBank*/) override
        {
            discountMod *= (1.0f - ByRank(player, Perk::FavoredPatron, 0.10f))
                * std::max(0.0f, 1.0f + Mods(player).total(EsteriaTraits::Repair));
        }

        // Relic Seeker (treasure chests) and Scavenger (herb and ore nodes): one more of a common trade material.
        // Extra loot from the starting traits: leather from skinning, cloth and gray items from humanoids, materials
        // from prospecting, milling and disenchanting. One shared daily cap keeps it from running away.
        void ExtraLoot(Player* player, Item* item, ObjectGuid lootGuid)
        {
            using namespace EsteriaTraits;
            EsteriaTraits::Mods const& mods = Mods(player);
            if (!mods.any || IsPvpMap(player))
                return;
            ItemTemplate const* proto = item->GetTemplate();
            EsteriaPerkFx::CoreState& core = EsteriaPerkFx::Daily(player);
            auto const roll = [&](uint8 family)
            {
                float const chance = mods.pos[family];
                if (chance > 0.0f && roll_chance_f(chance * 100.0f))
                    GiveExtra(player, item->GetEntry(), core.traitLoot, 30);
            };

            if (lootGuid.IsCreature())
            {
                Creature* creature = ObjectAccessor::GetCreature(*player, lootGuid);
                if (!creature)
                    return;
                bool const trade = proto->Class == ITEM_CLASS_TRADE_GOODS;
                // Leather only drops from skinning, bar a rare corpse drop.
                if (trade && proto->SubClass == ITEM_SUBCLASS_LEATHER)
                    roll(BonusSkin);
                if (creature->GetCreatureTemplate()->type != CREATURE_TYPE_HUMANOID)
                    return;
                if (trade && proto->SubClass == ITEM_SUBCLASS_CLOTH)
                    roll(ClothDrop);
                // One roll for the corpse: the first gray item that it gave up.
                if (proto->Quality == ITEM_QUALITY_POOR && core.grayCorpse != lootGuid)
                {
                    core.grayCorpse = lootGuid;
                    roll(GrayExtra);
                }
            }
            else if (lootGuid.IsItem())
            {
                // What is being opened is an ore, an herb or a piece of gear, not a bag or a chest.
                Item* source = player->GetItemByGuid(lootGuid);
                ItemTemplate const* from = source ? source->GetTemplate() : nullptr;
                if (from && !(from->Flags & ITEM_FLAG_HAS_LOOT) && ((from->Flags & (ITEM_FLAG_IS_PROSPECTABLE | ITEM_FLAG_IS_MILLABLE))
                    || from->DisenchantID) && IsCommon(proto, false))
                    roll(Salvage);
            }
        }

        // Relic Seeker (treasure chests) and Scavenger (herb and ore nodes): one more of a common trade material.
        void OnPlayerLootItem(Player* player, Item* item, uint32 /*count*/, ObjectGuid lootGuid) override
        {
            if (item && !lootGuid.IsGameObject())
            {
                ExtraLoot(player, item, lootGuid);
                return;
            }
            if (!lootGuid.IsGameObject() || !item || !IsCommon(item->GetTemplate(), false))
                return;
            GameObject* go = ObjectAccessor::GetGameObject(*player, lootGuid);
            if (!go || !go->GetGOInfo() || go->GetGOInfo()->type != GAMEOBJECT_TYPE_CHEST)
                return;

            bool gathering = false, herb = false;
            if (LockEntry const* lock = sLockStore.LookupEntry(go->GetGOInfo()->GetLockId()))
                for (uint8 i = 0; i < MAX_LOCK_CASE; ++i)
                    if (lock->Type[i] == LOCK_KEY_SKILL && (lock->Index[i] == LOCKTYPE_HERBALISM || lock->Index[i] == LOCKTYPE_MINING))
                    {
                        gathering = true;
                        herb = lock->Index[i] == LOCKTYPE_HERBALISM;
                    }

            if (gathering)
            {
                float const chance = ByRank(player, Perk::Scavenger, 0.04f, 0.08f);
                if (chance > 0.0f && roll_chance_f(chance * 100.0f))
                    GiveExtra(player, item->GetEntry(), EsteriaPerkFx::Daily(player).scavenged, 20);
                // Green Thumb / Ore Whisperer (20 a day) and Lucky Scrounger (4 a day): the cap only counts an
                // item that was really handed over.
                float const bonus = Mods(player).pos[herb ? EsteriaTraits::BonusHerb : EsteriaTraits::BonusOre];
                if (bonus > 0.0f && roll_chance_f(bonus * 100.0f))
                    GiveExtra(player, item->GetEntry(), EsteriaPerkFx::Daily(player).traitGathered, 20);
                float const lucky = Mods(player).pos[EsteriaTraits::BonusGather];
                if (lucky > 0.0f && roll_chance_f(lucky * 100.0f))
                    GiveExtra(player, item->GetEntry(), EsteriaPerkFx::Daily(player).scrounged, 4);
            }
            else
            {
                float const chance = ByRank(player, Perk::RelicSeeker, 0.05f, 0.10f);
                if (chance > 0.0f && roll_chance_f(chance * 100.0f))
                    GiveExtra(player, item->GetEntry(), EsteriaPerkFx::Daily(player).relics, 10);
            }
        }

        // Artisan's Signature: one more of the crafted trade good or consumable.
        void OnPlayerCreateItem(Player* player, Item* item, uint32 /*count*/) override
        {
            float const chance = ByRank(player, Perk::ArtisanSignature, 0.05f);
            if (chance > 0.0f && item && IsCommon(item->GetTemplate(), true) && roll_chance_f(chance * 100.0f))
                GiveExtra(player, item->GetEntry(), EsteriaPerkFx::Daily(player).signed_, 5);
        }

        void OnPlayerSpellCast(Player* player, Spell* spell, bool /*skipCheck*/) override
        {
            SpellInfo const* info = spell ? spell->GetSpellInfo() : nullptr;
            if (!info)
                return;

            // Hearthwalker: a speed boost from the cast, and the cooldown is shortened once it has started.
            if (info->Id == SPELL_HEARTHSTONE && (player->GetEsteriaPerkRank(Perk::Hearthwalker)
                || Mods(player).total(EsteriaTraits::Hearth) != 0.0f))
            {
                uint32 const now = NowMs();
                if (player->GetEsteriaPerkRank(Perk::Hearthwalker))
                    EsteriaPerkFx::StateOf(player->GetGUID()).hearthSpeedUntil = now + 2 * MINUTE * IN_MILLISECONDS;
                states[player->GetGUID()].hearthPending = now + 30 * IN_MILLISECONDS;
                return;
            }

            if (info->Id == SPELL_HOUSE_HEARTH && Mods(player).total(EsteriaTraits::HouseHearth) != 0.0f)
            {
                states[player->GetGUID()].houseHearthPending = NowMs() + 30 * IN_MILLISECONDS;
                return;
            }

            // Resource Recovery: crafting may hand one common reagent back.
            float const chance = ByRank(player, Perk::ResourceRecovery, 0.03f, 0.06f);
            if (chance <= 0.0f)
                return;
            bool crafts = false;
            for (auto const& effect : info->Effects)
                crafts |= effect.Effect == SPELL_EFFECT_CREATE_ITEM;
            if (!crafts || !roll_chance_f(chance * 100.0f))
                return;

            std::vector<uint32> reagents;
            for (uint8 i = 0; i < MAX_SPELL_REAGENTS; ++i)
                if (info->Reagent[i] > 0 && info->ReagentCount[i] > 0 && IsCommon(sObjectMgr->GetItemTemplate(info->Reagent[i]), false))
                    reagents.push_back(uint32(info->Reagent[i]));
            if (!reagents.empty())
                GiveExtra(player, reagents[urand(0, reagents.size() - 1)], EsteriaPerkFx::Daily(player).recovered, 10);
        }
    };
}

void AddSC_esteria_perk_effects()
{
    new esteria_perk_units();
    new esteria_perk_players();
}
