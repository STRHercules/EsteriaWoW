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

// Paths of Fate: the effects that the core calls into (see PerkFx.h). Numbers match the EsteriaPerks addon's Data.lua.

#include "Bag.h"
#include "Creature.h"
#include "DBCStores.h"
#include "GameTime.h"
#include "Map.h"
#include "Pet.h"
#include "Spell.h"
#include "Weather.h"
#include "ObjectAccessor.h"
#include "PerkFx.h"
#include "CombatManager.h"
#include "PerkTraitRules.h"
#include "Player.h"
#include "QuestDef.h"
#include "SpellInfo.h"
#include "Timer.h"

namespace EsteriaPerkFx
{
    namespace
    {
        // shortcut: in-memory per-player timers and daily counters; they reset on a restart, move into the characters db if abused.
        std::unordered_map<ObjectGuid, CoreState> states;

        uint32 NowMs() { return uint32(GameTime::GetGameTimeMS().count()); }

        bool IsPvpMap(Player const* player)
        {
            Map const* map = player->GetMap();
            return map && map->IsBattlegroundOrArena();
        }

        // Value for the player's rank of a card; 0 when not owned.
        float Val(Player const* player, uint8 perk, float r1, float r2)
        {
            uint8 const rank = player->GetEsteriaPerkRank(perk);
            return !rank ? 0.0f : (rank >= 2 ? r2 : r1);
        }

        bool IsGathering(SpellInfo const* spell)
        {
            for (auto const& effect : spell->Effects)
            {
                if (effect.Effect == SPELL_EFFECT_SKINNING)
                    return true;
                if (effect.Effect == SPELL_EFFECT_OPEN_LOCK && (effect.MiscValue == LOCKTYPE_HERBALISM || effect.MiscValue == LOCKTYPE_MINING))
                    return true;
            }
            return false;
        }

        bool IsMounting(SpellInfo const* spell)
        {
            for (auto const& effect : spell->Effects)
                if (effect.ApplyAuraName == SPELL_AURA_MOUNTED)
                    return true;
            return false;
        }

        // Herbalism, mining or skinning: the trait family that slows or speeds that one gather, FamilyCount if none.
        uint8 GatherFamily(SpellInfo const* spell)
        {
            for (auto const& effect : spell->Effects)
            {
                if (effect.Effect == SPELL_EFFECT_SKINNING)
                    return EsteriaTraits::SkinTime;
                if (effect.Effect == SPELL_EFFECT_OPEN_LOCK && effect.MiscValue == LOCKTYPE_HERBALISM)
                    return EsteriaTraits::HerbTime;
                if (effect.Effect == SPELL_EFFECT_OPEN_LOCK && effect.MiscValue == LOCKTYPE_MINING)
                    return EsteriaTraits::MineTime;
            }
            return EsteriaTraits::FamilyCount;
        }

        // A profession recipe: makes an item from reagents and has no cooldown of its own (those stay as they are).
        bool IsPlainCraft(SpellInfo const* spell)
        {
            if (spell->Reagent[0] <= 0 || spell->RecoveryTime || spell->CategoryRecoveryTime)
                return false;
            for (auto const& effect : spell->Effects)
                if (effect.Effect == SPELL_EFFECT_CREATE_ITEM)
                    return true;
            return false;
        }

        EsteriaTraits::Mods const& Mods(Player const* player) { return player->GetEsteriaTraitMods(); }
    }

    bool TraitsActive(Player const* player)
    {
        if (!player || !Mods(player).any || IsPvpMap(player) || player->duel)
            return false;
        if (player->GetCombatManager().HasPvPCombat())
            return false;
        // A hostile player selected as the target counts too: an opener would otherwise slip through before combat.
        ObjectGuid const target = player->GetTarget();
        if (!target.IsPlayer() || target == player->GetGUID())
            return true;
        Player const* other = ObjectAccessor::FindPlayer(target);
        return !other || !player->IsHostileTo(other);
    }

    bool IsNight()
    {
        int const hour = Acore::Time::TimeBreakdown(GameTime::GetGameTime().count()).tm_hour;
        return hour >= 18 || hour < 6;
    }

    bool IsDamaging(SpellInfo const* spell)
    {
        for (auto const& effect : spell->Effects)
            if (effect.Effect == SPELL_EFFECT_SCHOOL_DAMAGE || effect.ApplyAuraName == SPELL_AURA_PERIODIC_DAMAGE)
                return true;
        return false;
    }

    CoreState& StateOf(ObjectGuid guid) { return states[guid]; }
    void Forget(ObjectGuid guid) { states.erase(guid); }

    CoreState& Daily(Player const* player)
    {
        CoreState& state = states[player->GetGUID()];
        uint32 const today = uint32(GameTime::GetGameTime().count() / DAY);
        if (state.capDay != today)
        {
            state.capDay = today;
            state.scavenged = state.relics = state.recovered = state.signed_ = state.auctionSaved = 0;
            state.traitGathered = state.scrounged = 0;
        }
        return state;
    }

    bool InCapital(Player const* player)
    {
        AreaTableEntry const* area = sAreaTableStore.LookupEntry(player->GetAreaId());
        return area && (area->flags & (AREA_FLAG_CAPITAL | AREA_FLAG_SLAVE_CAPITAL));
    }

    bool IsWetWeather(Player const* player)
    {
        Map const* map = player->GetMap();
        if (!map)
            return false;
        switch (map->GetZoneWeatherState(player->GetZoneId()))
        {
            case WEATHER_STATE_LIGHT_RAIN: case WEATHER_STATE_MEDIUM_RAIN: case WEATHER_STATE_HEAVY_RAIN:
            case WEATHER_STATE_LIGHT_SNOW: case WEATHER_STATE_MEDIUM_SNOW: case WEATHER_STATE_HEAVY_SNOW:
            case WEATHER_STATE_THUNDERS: case WEATHER_STATE_BLACKRAIN: case WEATHER_STATE_BLACKSNOW:
                return true;
            default:
                return false;
        }
    }

    namespace
    {
        bool InHousingMap(Player const* player) { return HousingMapProbe && HousingMapProbe(player->GetMapId()); }

        // Bags at least 80% full (backpack and equipped bags).
        bool BagsNearlyFull(Player const* player)
        {
            uint32 capacity = INVENTORY_SLOT_ITEM_END - INVENTORY_SLOT_ITEM_START;
            for (uint8 i = INVENTORY_SLOT_BAG_START; i < INVENTORY_SLOT_BAG_END; ++i)
                if (Bag* bag = player->GetBagByPos(i))
                    capacity += bag->GetBagSize();
            return capacity && (capacity - std::min(capacity, player->GetFreeInventorySpace())) * 5 >= capacity * 4;
        }

        // A creature that is a plain target for starting traits: a wild one, never a player's or a pet.
        bool IsWildTarget(Unit const* unit) { return unit && unit->IsCreature() && !unit->IsControlledByPlayer(); }

        Player const* OwnerPlayer(Unit const* pet)
        {
            if (!pet || !pet->IsPet() || !pet->IsControlledByPlayer())
                return nullptr;
            Unit const* owner = pet->GetOwner();
            return owner ? owner->ToPlayer() : nullptr;
        }
    }

    float MoveBonus(Player const* player)
    {
        float bonus = 0.0f;
        if (player->HasPlayerFlag(PLAYER_FLAGS_GHOST))
            bonus += Val(player, Id::GhostTrail, 0.20f, 0.20f);

        bool const onFoot = !player->IsMounted() && !player->IsInFlight();
        if (onFoot && !IsPvpMap(player) && player->IsOutdoors())
        {
            if (!player->IsInCombat())
            {
                bonus += Val(player, Id::Wayfarer, 0.05f, 0.10f);
            }
            auto const it = states.find(player->GetGUID());
            if (it != states.end() && NowMs() < it->second.hearthSpeedUntil)
                bonus += 0.10f;
        }

        // Starting traits: the gains are capped (+15% out of combat, +5% in it), the losses always apply.
        EsteriaTraits::Mods const& mods = Mods(player);
        if (mods.any && onFoot && !IsPvpMap(player))
        {
            using namespace EsteriaTraits;
            auto const it = states.find(player->GetGUID());
            uint32 const now = NowMs();
            if (!player->IsInCombat())
            {
                Sum sum;
                sum.add(mods, MoveOoc).add(mods, IsNight() ? MoveNight : MoveDay);
                if (player->IsOutdoors())
                    sum.add(mods, MoveOutdoorOoc);
                // Where the player stands: caves and wilderness (world maps only), rain or clear skies, housing
                // neighborhoods and capital cities. A cave is shelter that is neither a city nor a house.
                Map const* map = player->GetMap();
                bool const world = map && !map->Instanceable() && !InHousingMap(player);
                bool const capital = InCapital(player);
                if (world && !capital)
                {
                    if (!player->IsOutdoors())
                        sum.add(mods, MoveCave);
                    else
                    {
                        sum.add(mods, MoveWild);
                        sum.add(mods, IsWetWeather(player) ? MoveRain : MoveClear);
                    }
                }
                if (InHousingMap(player))
                    sum.add(mods, MoveHousing);
                else if (capital)
                    sum.add(mods, MoveCapital);
                if (it != states.end() && it->second.travelSince)
                    sum.add(mods, now - it->second.travelSince >= 15 * IN_MILLISECONDS ? MoveTravelLong : MoveTravelEarly);
                bonus += sum.total(0.15f);
            }
            else if (!player->GetCombatManager().HasPvPCombat())
                bonus += Sum().add(mods, MoveCombat).total(0.05f);
            if (it != states.end() && now < it->second.rabbitUntil)
                bonus += mods.pos[MoveLowHealthProc];
            // Losses that hold in a fight too: a pet out, bags nearly full.
            if (mods.neg[OwnerMovePet] != 0.0f)
                if (Pet const* pet = player->GetPet(); pet && pet->IsAlive())
                    bonus += mods.neg[OwnerMovePet];
            if (mods.neg[MoveFullBags] != 0.0f && BagsNearlyFull(player))
                bonus += mods.neg[MoveFullBags];
        }
        return bonus;
    }

    float SwimBonus(Player const* player)
    {
        return IsPvpMap(player) ? 0.0f : Mods(player).total(EsteriaTraits::Swim);
    }

    // Trait price changes: a discount is capped at 10%, a sale bonus at 15%, so buying never beats selling.
    float BuyMod(Player const* player)
    {
        return (1.0f - Val(player, Id::ThriftyBuyer, 0.01f, 0.02f))
            * (1.0f + EsteriaTraits::Sum().add(Mods(player), EsteriaTraits::Buy).total(10.0f, 0.10f));
    }

    float SellMod(Player const* player, bool gray)
    {
        EsteriaTraits::Sum sum;
        sum.add(Mods(player), EsteriaTraits::Sell);
        if (gray)
            sum.add(Mods(player), EsteriaTraits::SellGray);
        return (1.0f + Val(player, Id::FairDealer, 0.01f, 0.02f)) * (1.0f + sum.total(0.15f));
    }

    float TrainMod(Player const* player) { return 1.0f - Val(player, Id::SilverTongue, 0.10f, 0.10f); }

    float TaxiMod(Player const* player)
    {
        return (1.0f - Val(player, Id::Surveyor, 0.10f, 0.20f)) * (1.0f + Mods(player).total(EsteriaTraits::Taxi));
    }

    // Only how fast rest builds up; the cap on stored rest is untouched. Trait gains stop at +30%.
    float RestMod(Player const* player)
    {
        EsteriaTraits::Sum sum;
        sum.add(Mods(player), EsteriaTraits::Rest);
        // Homebody: more rest in your own house, less in an ordinary inn.
        if (OwnHomeProbe && OwnHomeProbe(player))
            sum.add(Mods(player), EsteriaTraits::RestHome);
        else if (player->HasRestFlag(REST_FLAG_IN_TAVERN))
            sum.add(Mods(player), EsteriaTraits::RestInn);
        return (1.0f + Val(player, Id::RestfulMind, 0.10f, 0.20f)) * (1.0f + sum.total(0.30f));
    }

    float DeathDurabilityMod(Player const* player)
    {
        return (1.0f - Val(player, Id::PatchworkRepairs, 0.10f, 0.20f))
            * (1.0f + Mods(player).total(EsteriaTraits::DeathDurability));
    }

    float EnvironmentMod(Player const* player)
    {
        return (1.0f - Val(player, Id::Weathered, 0.08f, 0.16f)) * (1.0f + Mods(player).total(EsteriaTraits::EnvOther));
    }

    // Fall damage: traits take off at most 60%.
    float FallMod(Player const* player)
    {
        return 1.0f + EsteriaTraits::Sum().add(Mods(player), EsteriaTraits::Fall).total(10.0f, 0.60f);
    }

    float HealthRegenMod(Player const* player)
    {
        return std::max(0.0f, 1.0f + Mods(player).total(EsteriaTraits::HealthRegen));
    }

    // Mana cost of damaging spells.
    float PowerCostMod(Unit const* caster, SpellInfo const* spell)
    {
        Player const* player = caster ? caster->ToPlayer() : nullptr;
        if (!player || !spell || spell->PowerType != POWER_MANA || !TraitsActive(player) || !IsDamaging(spell))
            return 1.0f;
        return std::max(0.0f, 1.0f + Mods(player).total(EsteriaTraits::SpellCost));
    }

    float CastTimeMod(Unit const* caster, SpellInfo const* spell)
    {
        Player const* player = caster ? caster->ToPlayer() : nullptr;
        if (!player || !spell)
            return 1.0f;

        // Starting traits: gathering and plain crafting anywhere, damaging spells only against creatures.
        using namespace EsteriaTraits;
        EsteriaTraits::Mods const& mods = Mods(player);
        float trait = 0.0f;
        if (mods.any)
        {
            if (IsGathering(spell))
            {
                uint8 const family = GatherFamily(spell);
                trait = mods.total(GatherTime) + (family < FamilyCount ? mods.total(family) : 0.0f);
            }
            else if (IsPlainCraft(spell))
                trait = mods.total(CraftTime);
            else if (spell->CastTimeEntry && spell->CastTimeEntry->CastTime > 0 && IsDamaging(spell) && TraitsActive(player))
                trait = mods.total(CastTimeDamaging) + (spell->CastTimeEntry->CastTime > 1500 ? mods.total(CastTimeSlow) : 0.0f);
        }
        float const traitMod = std::max(0.0f, 1.0f + trait);

        if (player->GetEsteriaPerkRank(Id::EfficientHands) && IsGathering(spell))
            return traitMod * (1.0f - Val(player, Id::EfficientHands, 0.05f, 0.10f));
        if (player->GetEsteriaPerkRank(Id::Trailblazer) && !IsPvpMap(player) && player->IsOutdoors() && IsMounting(spell))
            return traitMod * (1.0f - Val(player, Id::Trailblazer, 0.05f, 0.10f));
        return traitMod;
    }

    float PushbackReduction(Player const* player)
    {
        if (!player)
            return 0.0f;
        auto const it = states.find(player->GetGUID());
        if (it == states.end() || NowMs() >= it->second.steadyUntil)
            return 0.0f;
        return Val(player, Id::SteadyFocus, 0.10f, 0.20f);
    }

    // Profession skill-up chance. Trait gains stop at +25%; a chance that was certain stays certain.
    int32 SkillChance(Player const* player, uint16 skill, int32 chance)
    {
        using namespace EsteriaTraits;
        EsteriaTraits::Mods const& mods = Mods(player);
        Sum sum;
        sum.add(mods, Skill).add(mods, player->GetPureSkillValue(skill) < 150 ? SkillLow : SkillHigh);
        if (skill == SKILL_ENGINEERING)
            sum.add(mods, SkillEngineering);
        // Crafting skill-ups: the spell being cast is a recipe (a profession spell that makes an item).
        if (Spell const* cast = player->GetCurrentSpell(CURRENT_GENERIC_SPELL); cast && IsPlainCraft(cast->GetSpellInfo()))
            sum.add(mods, SkillCraft);
        float const bonus = Val(player, Id::ApprenticeLuck, 0.05f, 0.10f) + sum.total(0.25f);
        return bonus == 0.0f ? chance : int32(float(chance) * std::max(0.0f, 1.0f + bonus));
    }

    // A kill quest asks for creatures; every other kind is counted as a delivery or errand.
    bool QuestIsKill(Quest const* quest)
    {
        for (uint8 i = 0; i < QUEST_OBJECTIVES_COUNT; ++i)
            if (quest->RequiredNpcOrGo[i] > 0 && quest->RequiredNpcOrGoCount[i] > 0)
                return true;
        return false;
    }

    bool QuestIsDungeon(Player const* player, Quest const* quest)
    {
        switch (quest->GetType())
        {
            case QUEST_TYPE_DUNGEON: case QUEST_TYPE_HEROIC: case QUEST_TYPE_RAID: case QUEST_TYPE_RAID_10: case QUEST_TYPE_RAID_25:
                return true;
            default:
                return player->GetMap() && player->GetMap()->IsDungeon();
        }
    }

    int32 QuestMoney(Player const* player, Quest const* quest, int32 money)
    {
        if (money <= 0)
            return money;
        float bonus = Mods(player).total(EsteriaTraits::QuestGold);
        {
            using namespace EsteriaTraits;
            EsteriaTraits::Mods const& mods = Mods(player);
            if (mods.any)
            {
                Sum sum;
                sum.add(mods, QuestIsKill(quest) ? QuestGoldKill : QuestGoldDelivery);
                CoreState const& state = StateOf(player->GetGUID());
                sum.add(mods, state.diedQuests.count(quest->GetQuestId()) ? QuestGoldDied : QuestGoldClean);
                bonus += sum.total(0.20f);
            }
        }
        if (quest->IsDaily())
        {
            bonus += Val(player, Id::CivicContributor, 0.05f, 0.10f);
            int32 const sort = quest->GetZoneOrSort();
            if (sort == -QUEST_SORT_COOKING || sort == -QUEST_SORT_FISHING || sort == -QUEST_SORT_JEWELCRAFTING)
                bonus += Val(player, Id::ContractKeeper, 0.10f, 0.10f);
        }
        return bonus == 0.0f ? money : int32(float(money) * std::max(0.0f, 1.0f + bonus));
    }

    uint32 AuctionDeposit(Player const* player, uint32 deposit)
    {
        float const own = Mods(player).total(EsteriaTraits::AhDeposit);
        if (own != 0.0f)
            deposit = uint32(float(deposit) * std::max(0.0f, 1.0f + own));
        float const cut = Val(player, Id::TradeBroker, 0.05f, 0.05f);
        if (cut <= 0.0f)
            return deposit;
        CoreState& state = Daily(player);
        uint32 const saved = std::min(uint32(float(deposit) * cut), 10 * GOLD - std::min(state.auctionSaved, uint32(10 * GOLD)));
        state.auctionSaved += saved;
        return deposit - saved;
    }

    // A seller's mail for a finished sale. The seller may be offline, so the build is read from the database then.
    uint32 AuctionProfit(ObjectGuid seller, uint32 profit, uint32 cut)
    {
        EsteriaTraits::Mods mods;
        if (Player const* online = ObjectAccessor::FindConnectedPlayer(seller))
            mods = Mods(online);
        else if (QueryResult result = CharacterDatabase.Query("SELECT trait_id FROM character_esteria_trait_selection WHERE guid = {}", seller.GetCounter()))
        {
            EsteriaTraits::Selection selection;
            do
            {
                if (selection.count < CharacterPerkTrait::MaxTraits)
                    selection.ids[selection.count++] = (*result)[0].Get<uint16>();
            } while (result->NextRow());
            mods = EsteriaTraits::Compose(selection);
        }
        float const change = mods.total(EsteriaTraits::AhCut);
        if (change == 0.0f)
            return profit;
        // The cut grows or shrinks; what was held back moves into or out of the seller's pocket.
        int64 const adjusted = int64(profit) - int64(float(cut) * change);
        return uint32(std::max<int64>(0, adjusted));
    }

    // ---- stats. Starting traits never touch a fight between players: wild creatures only.

    float CritDelta(Unit const* attacker, Unit const* victim, bool spell)
    {
        Player const* player = attacker ? attacker->ToPlayer() : nullptr;
        if (!player || !IsWildTarget(victim) || !TraitsActive(player))
            return 0.0f;
        EsteriaTraits::Sum sum;
        sum.add(Mods(player), EsteriaTraits::CritChanceNpc);
        if (spell)
            sum.add(Mods(player), EsteriaTraits::CritSpellNpc);
        return 100.0f * sum.total(0.05f, 0.05f);
    }

    float CritDamageDelta(Unit const* attacker, Unit const* victim)
    {
        Player const* player = attacker ? attacker->ToPlayer() : nullptr;
        if (!player || !IsWildTarget(victim) || !TraitsActive(player))
            return 0.0f;
        return 100.0f * EsteriaTraits::Sum().add(Mods(player), EsteriaTraits::CritDamage).total(0.25f, 0.25f);
    }

    float ArmorGearMod(Player const* player)
    {
        return IsPvpMap(player) ? 1.0f : std::max(0.0f, 1.0f + Mods(player).total(EsteriaTraits::ArmorGear));
    }

    float ManaRegenCombatMod(Player const* player)
    {
        return IsPvpMap(player) ? 1.0f : std::max(0.0f, 1.0f + Mods(player).total(EsteriaTraits::ManaRegenCombat));
    }

    // Tipsy Brawler: while drunk, a creature's blow is dodged more often and the player's own blows miss more often.
    float DodgeDelta(Unit const* victim, Unit const* attacker)
    {
        Player const* player = victim ? victim->ToPlayer() : nullptr;
        if (!player || !player->GetDrunkValue() || !IsWildTarget(attacker) || !TraitsActive(player))
            return 0.0f;
        return 100.0f * Mods(player).pos[EsteriaTraits::DodgeDrunk];
    }

    float HitDelta(Unit const* attacker, Unit const* victim)
    {
        Player const* player = attacker ? attacker->ToPlayer() : nullptr;
        if (!player || !player->GetDrunkValue() || !IsWildTarget(victim) || !TraitsActive(player))
            return 0.0f;
        return 100.0f * Mods(player).neg[EsteriaTraits::HitDrunk];
    }

    // Underbrush: ordinary creatures notice a player on foot in the open from a little closer.
    float AggroMod(Unit const* target, Creature const* creature)
    {
        Player const* player = target ? target->ToPlayer() : nullptr;
        if (!player || !creature || creature->isElite() || creature->IsDungeonBoss() || creature->IsControlledByPlayer())
            return 1.0f;
        float const change = Mods(player).neg[EsteriaTraits::Aggro];
        if (change == 0.0f || player->IsMounted() || player->IsInFlight() || !player->IsOutdoors() || IsPvpMap(player))
            return 1.0f;
        return std::max(0.0f, 1.0f + std::max(change, -0.25f));
    }

    float PetHealthMod(Unit const* pet)
    {
        Player const* owner = OwnerPlayer(pet);
        if (!owner || IsPvpMap(owner))
            return 1.0f;
        return std::max(0.0f, 1.0f + EsteriaTraits::Sum().add(Mods(owner), EsteriaTraits::PetMaxHealth).total(0.15f, 0.15f));
    }

    float PetSpeedBonus(Unit const* pet)
    {
        Player const* owner = OwnerPlayer(pet);
        return owner && !IsPvpMap(owner) ? std::min(Mods(owner).pos[EsteriaTraits::PetSpeed], 0.15f) : 0.0f;
    }

    // Food heals the one who eats it; a drink restores mana. Each trait moves one and slows the other.
    float FoodMod(Unit const* target, Unit const* caster)
    {
        Player const* player = target ? target->ToPlayer() : nullptr;
        if (!player || target != caster || IsPvpMap(player))
            return 1.0f;
        return std::max(0.0f, 1.0f + Mods(player).total(EsteriaTraits::FoodHeal));
    }

    float DrinkMod(Unit const* target)
    {
        Player const* player = target ? target->ToPlayer() : nullptr;
        if (!player || IsPvpMap(player))
            return 1.0f;
        return std::max(0.0f, 1.0f + Mods(player).total(EsteriaTraits::DrinkMana));
    }

    // A crit on the player: Guarded Reflex arms a window that the script spends on the next hit.
    void OnCritTaken(Unit const* victim)
    {
        Player const* player = victim ? victim->ToPlayer() : nullptr;
        if (!player || !player->GetEsteriaPerkRank(Id::GuardedReflex) || IsPvpMap(player))
            return;
        CoreState& state = states[player->GetGUID()];
        uint32 const now = NowMs();
        if (now < state.guardReady)
            return;
        state.guardReady = now + 45 * IN_MILLISECONDS;
        state.guardFrom = now + 1; // the crit itself is not "the next hit"
        state.guardUntil = now + 8 * IN_MILLISECONDS;
    }

    void OnInterrupt(Unit* caster, Unit* target)
    {
        Player* player = caster ? caster->ToPlayer() : nullptr;
        float const heal = player ? Val(player, Id::Countermeasure, 0.01f, 0.02f) : 0.0f;
        if (heal <= 0.0f || !target || !target->IsCreature() || !player->IsAlive())
            return;
        CoreState& state = states[player->GetGUID()];
        uint32 const now = NowMs();
        if (now < state.countermeasureReady)
            return;
        state.countermeasureReady = now + 30 * IN_MILLISECONDS;
        player->SetHealth(std::min(player->GetMaxHealth(), player->GetHealth() + uint32(float(player->GetMaxHealth()) * heal)));
    }
}
