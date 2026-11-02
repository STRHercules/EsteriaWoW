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

#include "GameTime.h"
#include "Map.h"
#include "PerkFx.h"
#include "PerkTraitWire.h"
#include "Player.h"
#include "QuestDef.h"
#include "SpellInfo.h"

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
        }
        return state;
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
                if (player->GetEsteriaTrait() == CharacterPerkTrait::Wanderer)
                    bonus += 0.05f;
            }
            auto const it = states.find(player->GetGUID());
            if (it != states.end() && NowMs() < it->second.hearthSpeedUntil)
                bonus += 0.10f;
        }
        return bonus;
    }

    float BuyMod(Player const* player) { return 1.0f - Val(player, Id::ThriftyBuyer, 0.01f, 0.02f); }
    float SellMod(Player const* player) { return 1.0f + Val(player, Id::FairDealer, 0.01f, 0.02f); }
    float TrainMod(Player const* player) { return 1.0f - Val(player, Id::SilverTongue, 0.10f, 0.10f); }
    float TaxiMod(Player const* player) { return 1.0f - Val(player, Id::Surveyor, 0.10f, 0.20f); }
    float RestMod(Player const* player) { return 1.0f + Val(player, Id::RestfulMind, 0.10f, 0.20f); }
    float DeathDurabilityMod(Player const* player) { return 1.0f - Val(player, Id::PatchworkRepairs, 0.10f, 0.20f); }
    float EnvironmentMod(Player const* player) { return 1.0f - Val(player, Id::Weathered, 0.08f, 0.16f); }

    float CastTimeMod(Unit const* caster, SpellInfo const* spell)
    {
        Player const* player = caster ? caster->ToPlayer() : nullptr;
        if (!player || !spell)
            return 1.0f;
        if (player->GetEsteriaPerkRank(Id::EfficientHands) && IsGathering(spell))
            return 1.0f - Val(player, Id::EfficientHands, 0.05f, 0.10f);
        if (player->GetEsteriaPerkRank(Id::Trailblazer) && !IsPvpMap(player) && player->IsOutdoors() && IsMounting(spell))
            return 1.0f - Val(player, Id::Trailblazer, 0.05f, 0.10f);
        return 1.0f;
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

    int32 SkillChance(Player const* player, int32 chance)
    {
        float bonus = Val(player, Id::ApprenticeLuck, 0.05f, 0.10f);
        if (player->GetEsteriaTrait() == CharacterPerkTrait::ArtisanSoul) bonus += 0.10f;
        if (player->GetEsteriaTrait() == CharacterPerkTrait::CuriousMind) bonus -= 0.10f;
        return bonus == 0.0f ? chance : int32(float(chance) * std::max(0.0f, 1.0f + bonus));
    }

    int32 QuestMoney(Player const* player, Quest const* quest, int32 money)
    {
        if (money <= 0 || !quest->IsDaily())
            return money;
        float bonus = Val(player, Id::CivicContributor, 0.05f, 0.10f);
        int32 const sort = quest->GetZoneOrSort();
        if (sort == -QUEST_SORT_COOKING || sort == -QUEST_SORT_FISHING || sort == -QUEST_SORT_JEWELCRAFTING)
            bonus += Val(player, Id::ContractKeeper, 0.10f, 0.10f);
        return int32(float(money) * (1.0f + bonus));
    }

    uint32 AuctionDeposit(Player const* player, uint32 deposit)
    {
        float const cut = Val(player, Id::TradeBroker, 0.05f, 0.05f);
        if (cut <= 0.0f)
            return deposit;
        CoreState& state = Daily(player);
        uint32 const saved = std::min(uint32(float(deposit) * cut), 10 * GOLD - std::min(state.auctionSaved, uint32(10 * GOLD)));
        state.auctionSaved += saved;
        return deposit - saved;
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
