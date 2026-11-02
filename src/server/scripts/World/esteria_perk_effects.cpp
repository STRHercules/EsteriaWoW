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

// Paths of Fate: background traits and the perks that are script hooks (numbers: Esteria_Paths_of_Fate_Design_v1.md
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
#include "PerkTraitWire.h"
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
        uint32 hearthPending = 0;     // ms until which a fresh Hearthstone cooldown may still be shortened
    };

    // shortcut: keyed by guid in memory; daily caps and cooldowns reset on a restart, move into the characters db if abused.
    std::unordered_map<ObjectGuid, State> states;

    uint32 NowMs() { return uint32(GameTime::GetGameTimeMS().count()); }
    uint32 Today() { return uint32(GameTime::GetGameTime().count() / DAY); }

    uint8 Trait(Player const* player) { return player->GetEsteriaTrait(); }

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
        value = uint32(std::max(0.0f, float(value) * (1.0f + bonus)));
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

    // Damage the player deals to a creature: First Strike, Opportunist, Finisher's Resolve and the trait.
    void OnPlayerDeals(Player* player, Unit* victim, uint32& damage)
    {
        Creature* creature = victim ? victim->ToCreature() : nullptr;
        if (!creature || !damage)
            return;

        float bonus = 0.0f;
        uint8 const trait = Trait(player);
        if (!IsPvpMap(player))
        {
            if (trait == CharacterPerkTrait::GlassCannon) bonus += 0.02f;
            if (trait == CharacterPerkTrait::Ironbound) bonus -= 0.02f;
        }

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

    // Damage a creature deals to the player: Guarded Reflex and Hold the Line.
    void OnPlayerTakes(Player* player, Unit* attacker, uint32& damage)
    {
        if (!attacker || !attacker->ToCreature() || !damage || IsPvpMap(player))
            return;
        uint32 const now = NowMs();

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
              UNITHOOK_ON_DAMAGE, UNITHOOK_ON_AURA_APPLY }) { }

        void ModifyMeleeDamage(Unit* target, Unit* attacker, uint32& damage) override
        {
            if (Player* player = attacker ? attacker->ToPlayer() : nullptr)
                OnPlayerDeals(player, target, damage);
            if (Player* player = target ? target->ToPlayer() : nullptr)
                OnPlayerTakes(player, attacker, damage);
        }

        void ModifySpellDamageTaken(Unit* target, Unit* attacker, int32& damage, SpellInfo const* /*spellInfo*/) override
        {
            if (damage <= 0)
                return;
            uint32 value = uint32(damage);
            if (Player* player = attacker ? attacker->ToPlayer() : nullptr)
                OnPlayerDeals(player, target, value);
            if (Player* player = target ? target->ToPlayer() : nullptr)
            {
                OnPlayerTakes(player, attacker, value);
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
            Player* player = target ? target->ToPlayer() : nullptr;
            if (!player || healer != target || !spellInfo)
                return;
            if (std::find(std::begin(BANDAGES), std::end(BANDAGES), spellInfo->Id) != std::end(BANDAGES))
                Scale(heal, ByRank(player, Perk::FieldMedic, 0.15f, 0.30f));
            else if (spellInfo->SpellFamilyName == SPELLFAMILY_POTION)
            {
                // Frugal Survivor: -10% healing from your own potions.
                if (Trait(player) == CharacterPerkTrait::FrugalSurvivor)
                    Scale(heal, -0.10f);
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
            SpellInfo const* spell = aura->GetSpellInfo();
            bool const food = (spell->AttributesEx2 & SPELL_ATTR2_FOOD) != 0;
            bool const flask = spell->SpellFamilyName == SPELLFAMILY_POTION && aura->GetMaxDuration() >= 10 * MINUTE * IN_MILLISECONDS;
            if (!food && !flask)
                return;
            float bonus = 0.0f;
            if (food)
                bonus += ByRank(player, Perk::RationKeeper, 0.10f, 0.20f);
            if (Trait(player) == CharacterPerkTrait::FrugalSurvivor)
                bonus += 0.15f;
            if (bonus <= 0.0f)
                return;
            int32 const duration = int32(float(aura->GetMaxDuration()) * (1.0f + bonus));
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
            PLAYERHOOK_ON_BEFORE_DURABILITY_REPAIR, PLAYERHOOK_ON_QUEST_COMPUTE_EXP }) { }

        void OnPlayerLogin(Player* player) override
        {
            states[player->GetGUID()];
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

            // Speed bonuses depend on position and combat, so they are re-checked here and pushed into UpdateSpeed on change.
            EsteriaPerkFx::CoreState& core = EsteriaPerkFx::StateOf(player->GetGUID());
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
                    player->ModifySpellCooldown(SPELL_HEARTHSTONE, -15 * MINUTE * int32(IN_MILLISECONDS));
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
            if (!enemy || !enemy->ToCreature() || !player->GetEsteriaPerkRank(Perk::FirstStrike))
                return;
            State& state = states[player->GetGUID()];
            if (NowMs() >= state.firstStrikeReady)
                state.firstStrikeArmed = true;
        }

        void OnPlayerLeaveCombat(Player* player) override
        {
            State& state = states[player->GetGUID()];
            state.firstStrikeArmed = false;
            uint32 const now = NowMs();
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
            // Victory's Reward: a creature that still gives experience restores health.
            float const heal = ByRank(killer, Perk::VictoryReward, 0.015f, 0.03f, true);
            if (heal <= 0.0f || !killer->IsAlive() || killed->GetLevel() <= Acore::XP::GetGrayLevel(killer->GetLevel()))
                return;
            State& state = states[killer->GetGUID()];
            uint32 const now = NowMs();
            if (now < state.victoryReady)
                return;
            state.victoryReady = now + 20 * IN_MILLISECONDS;
            killer->SetHealth(std::min(killer->GetMaxHealth(), killer->GetHealth() + uint32(float(killer->GetMaxHealth()) * heal)));
        }

        void OnPlayerGiveXP(Player* player, uint32& amount, Unit* /*victim*/, uint8 xpSource) override
        {
            float bonus = 0.0f;
            if (xpSource == PlayerXPSource::XPSOURCE_EXPLORE)
            {
                bonus += ByRank(player, Perk::Cartographer, 0.10f, 0.20f);
                if (Trait(player) == CharacterPerkTrait::CuriousMind) bonus += 0.10f;
                if (Trait(player) == CharacterPerkTrait::ArtisanSoul) bonus -= 0.10f;
            }
            else if (xpSource == PlayerXPSource::XPSOURCE_KILL)
            {
                // Tutor: the owner's grouped, nearby players earn more from shared kills.
                static float const values[] = { 0.0f, 0.02f, 0.04f };
                bonus += values[std::min<uint8>(BestNearbyRank(player, Perk::Tutor), 2)];
            }
            Scale(amount, bonus);
        }

        // Lorekeeper: quests in a fully explored zone.
        void OnPlayerQuestComputeXP(Player* player, Quest const* quest, uint32& xpValue) override
        {
            if (!xpValue || !player->GetEsteriaPerkRank(Perk::Lorekeeper) || quest->GetZoneOrSort() <= 0)
                return;
            if (ZoneExplored(player, uint32(quest->GetZoneOrSort())))
                Scale(xpValue, 0.05f);
        }

        void OnPlayerGiveReputation(Player* player, int32 factionID, float& amount, ReputationSource source) override
        {
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
                switch (Trait(player))
                {
                    case CharacterPerkTrait::Wanderer: case CharacterPerkTrait::OutlawHeart: bonus -= 0.10f; break;
                    case CharacterPerkTrait::FolkHero: bonus += 0.10f; break;
                    default: break;
                }
            }
            if (rank < REP_EXALTED)
                bonus += ByRank(player, Perk::PowerBroker, 0.10f);
            amount *= std::max(0.0f, 1.0f + bonus);
        }

        void OnPlayerBeforeLootMoney(Player* player, Loot* loot) override
        {
            if (!loot || !loot->gold)
                return;
            Creature* creature = ObjectAccessor::GetCreature(*player, loot->sourceWorldObjectGUID);
            if (!creature || creature->GetCreatureTemplate()->type != CREATURE_TYPE_HUMANOID)
                return;

            float bonus = 0.0f;
            if (Trait(player) == CharacterPerkTrait::FolkHero) bonus -= 0.10f;
            if (Trait(player) == CharacterPerkTrait::OutlawHeart) bonus += 0.10f;
            Scale(loot->gold, bonus);

            // Underworld Contact: +10%, up to 10 gold a day.
            float const extra = ByRank(player, Perk::UnderworldContact, 0.10f);
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

        // Glass Cannon -4% and Ironbound +4% maximum health, outside rated PvP.
        void OnPlayerAfterUpdateMaxHealth(Player* player, float& value) override
        {
            if (IsPvpMap(player))
                return;
            if (Trait(player) == CharacterPerkTrait::GlassCannon) value *= 0.96f;
            else if (Trait(player) == CharacterPerkTrait::Ironbound) value *= 1.04f;
        }

        // Favored Patron: vendor repairs.
        void OnPlayerBeforeDurabilityRepair(Player* player, ObjectGuid /*npc*/, ObjectGuid /*item*/, float& discountMod, uint8 /*guildBank*/) override
        {
            discountMod *= 1.0f - ByRank(player, Perk::FavoredPatron, 0.10f);
        }

        // Relic Seeker (treasure chests) and Scavenger (herb and ore nodes): one more of a common trade material.
        void OnPlayerLootItem(Player* player, Item* item, uint32 /*count*/, ObjectGuid lootGuid) override
        {
            if (!lootGuid.IsGameObject() || !item || !IsCommon(item->GetTemplate(), false))
                return;
            GameObject* go = ObjectAccessor::GetGameObject(*player, lootGuid);
            if (!go || !go->GetGOInfo() || go->GetGOInfo()->type != GAMEOBJECT_TYPE_CHEST)
                return;

            bool gathering = false;
            if (LockEntry const* lock = sLockStore.LookupEntry(go->GetGOInfo()->GetLockId()))
                for (uint8 i = 0; i < MAX_LOCK_CASE; ++i)
                    if (lock->Type[i] == LOCK_KEY_SKILL && (lock->Index[i] == LOCKTYPE_HERBALISM || lock->Index[i] == LOCKTYPE_MINING))
                        gathering = true;

            if (gathering)
            {
                float const chance = ByRank(player, Perk::Scavenger, 0.04f, 0.08f);
                if (chance > 0.0f && roll_chance_f(chance * 100.0f))
                    GiveExtra(player, item->GetEntry(), EsteriaPerkFx::Daily(player).scavenged, 20);
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
            if (info->Id == SPELL_HEARTHSTONE && player->GetEsteriaPerkRank(Perk::Hearthwalker))
            {
                uint32 const now = NowMs();
                EsteriaPerkFx::StateOf(player->GetGUID()).hearthSpeedUntil = now + 2 * MINUTE * IN_MILLISECONDS;
                states[player->GetGUID()].hearthPending = now + 30 * IN_MILLISECONDS;
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
