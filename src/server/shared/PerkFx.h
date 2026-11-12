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

// Paths of Fate effects that live at a core call site (prices, speed, cast time, pushback...). The core files call these
// one-liners; the rules are in game/Handlers/PerkEffects.cpp. Script-only effects stay in scripts/World/esteria_perk_effects.cpp.

#ifndef ESTERIA_PERK_FX_H
#define ESTERIA_PERK_FX_H

#include "Define.h"
#include "ObjectGuid.h"
#include <unordered_set>

class Creature;
class Player;
class Quest;
class SpellInfo;
class Unit;

namespace EsteriaPerkFx
{
    // Card ids (path * 10 + slot, as in PerkRules.h).
    namespace Id
    {
        constexpr uint8 FirstStrike = 1, GuardedReflex = 2, Countermeasure = 3, Opportunist = 4, SteadyFocus = 5,
            VictoryReward = 6, FinisherResolve = 7, HoldLine = 8, Unbroken = 9;
        constexpr uint8 FieldMedic = 11, RationKeeper = 12, Weathered = 14, PatchworkRepairs = 15, RestfulMind = 16,
            SecondWind = 17, Lifeline = 18, Diehard = 19;
        constexpr uint8 Wayfarer = 21, KeenEye = 22, Cartographer = 23, Trailblazer = 24, Surveyor = 25, RelicSeeker = 26,
            GhostTrail = 27, Lorekeeper = 28, Hearthwalker = 29;
        constexpr uint8 Scavenger = 31, ThriftyBuyer = 32, ApprenticeLuck = 33, ResourceRecovery = 34, EfficientHands = 35,
            ContractKeeper = 36, ArtisanSignature = 37, TradeBroker = 38;
        constexpr uint8 FamiliarFace = 41, FairDealer = 42, Diplomat = 43, SilverTongue = 44, CivicContributor = 45,
            UnderworldContact = 46, Mediator = 47, FavoredPatron = 48, PowerBroker = 49;
        constexpr uint8 SharedRations = 51, Tutor = 52, SharedVictory = 56;
    }

    // Timers shared between the core call sites and the script; milliseconds of game time.
    struct CoreState
    {
        uint32 guardReady = 0, guardFrom = 0, guardUntil = 0;   // Guarded Reflex
        uint32 steadyReady = 0, steadyUntil = 0;                // Steady Focus
        uint32 countermeasureReady = 0;
        uint32 hearthSpeedUntil = 0;                            // Hearthwalker
        float moveBonus = 0.0f;                                 // last bonus pushed into UpdateSpeed
        uint32 capDay = 0;                                      // day the counters below belong to
        uint32 scavenged = 0, relics = 0, recovered = 0, signed_ = 0;
        uint32 auctionSaved = 0;                                // Trade Broker, copper saved today
        uint32 traitGathered = 0, scrounged = 0;                // Green Thumb / Ore Whisperer, Lucky Scrounger
        // Starting traits: what the once-a-second tick knows about how the player moves.
        uint32 stillSince = 0;                                  // 0 while moving
        uint32 lastMoved = 0;
        uint32 travelSince = 0;                                 // moving out of combat since; 0 otherwise
        uint32 rabbitReady = 0, rabbitUntil = 0;                // Run Rabbit Run
        uint32 traitLoot = 0;                                   // extra cloth, gray, leather and salvage handed out today
        uint32 frenzyUntil = 0;                                 // Frenzied: the bonus lasts until then
        float frenzyApplied = 0.0f;                             // attack speed percent currently applied
        std::unordered_set<uint32> diedQuests;                  // High Roller: quests in the log when the player died
        bool diedLoaded = false;
        ObjectGuid grayCorpse;                                  // Junk Magnet: the corpse already rolled for
        uint32 rewardQuest = 0;                                 // the quest being handed in (its reputation comes first)
    };

    // The housing module registers these so traits can ask where the player is (the core cannot call the module).
    inline bool (*OwnHomeProbe)(Player const*) = nullptr;       // inside a house the player's account owns
    inline bool (*HousingMapProbe)(uint32 mapId) = nullptr;     // a housing neighborhood map

    CoreState& StateOf(ObjectGuid guid);
    void Forget(ObjectGuid guid);
    // Resets the daily counters when the day changed.
    CoreState& Daily(Player const* player);

    // Starting traits never touch a fight between players: off in battlegrounds, arenas, duels and PvP combat.
    bool TraitsActive(Player const* player);
    bool IsNight();                                             // server clock, 18:00 to 06:00
    bool IsDamaging(SpellInfo const* spell);

    float MoveBonus(Player const* player);                      // fraction added to run speed
    float SwimBonus(Player const* player);                      // fraction added to swim speed
    float BuyMod(Player const* player);                         // multipliers on a price
    float SellMod(Player const* player, bool gray = false);
    float TrainMod(Player const* player);
    float TaxiMod(Player const* player);
    float CastTimeMod(Unit const* caster, SpellInfo const* spell);
    float PushbackReduction(Player const* player);              // fraction of pushback removed
    float RestMod(Player const* player);
    float DeathDurabilityMod(Player const* player);
    float EnvironmentMod(Player const* player);                 // lava, slime, drowning, fatigue
    float FallMod(Player const* player);
    float HealthRegenMod(Player const* player);                 // natural regeneration out of combat
    float PowerCostMod(Unit const* caster, SpellInfo const* spell);
    int32 SkillChance(Player const* player, uint16 skill, int32 chance);
    int32 QuestMoney(Player const* player, Quest const* quest, int32 money);
    uint32 AuctionDeposit(Player const* player, uint32 deposit);
    // What the seller is mailed for a sale: the traits move the commission, even for a seller who is offline.
    uint32 AuctionProfit(ObjectGuid seller, uint32 profit, uint32 cut);

    // Stats, in the rule that follows the core's own formulas. Chances are percentage points, mods are multipliers.
    float CritDelta(Unit const* attacker, Unit const* victim, bool spell);
    float CritDamageDelta(Unit const* attacker, Unit const* victim);   // percent added to the crit bonus
    float ArmorGearMod(Player const* player);
    float ManaRegenCombatMod(Player const* player);
    float DodgeDelta(Unit const* victim, Unit const* attacker);
    float HitDelta(Unit const* attacker, Unit const* victim);
    float AggroMod(Unit const* target, Creature const* creature);
    float PetHealthMod(Unit const* pet);
    float PetSpeedBonus(Unit const* pet);                              // fraction added to the pet's speed
    float FoodMod(Unit const* target, Unit const* caster);
    float DrinkMod(Unit const* target);
    bool InCapital(Player const* player);
    bool IsWetWeather(Player const* player);                           // rain or snow where the player stands
    bool QuestIsKill(Quest const* quest);
    bool QuestIsDungeon(Player const* player, Quest const* quest);

    void OnCritTaken(Unit const* victim);
    void OnInterrupt(Unit* caster, Unit* target);
}

#endif
