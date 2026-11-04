/* Copyright (C) 2016+ AzerothCore, GNU AGPL v3. */

// CoA's custom-resource service (AscensionCompat.cpp, AscensionResourceService): the gain, cost and threshold
// rules in AscensionCustomResourceData.h that give a class its resource aura (Heat, Static, Scrap, Thirst...).
// Esteria's Cultist, Primalist and Ranger packages run their own slices of these rules, and the
// other kits' rules run here.
// A Hero owns kits rather than being a class: a rule applies while the Hero owns that kit.

#include "AscensionCustomResourceData.h"
#include "AscensionFelsworn.h"
#include "AscensionPyromancer.h"
#include "AscensionReaperTalents.h"
#include "AscensionSunCleric.h"
#include "AscensionTinker.h"
#include "AscensionVenomancer.h"
#include "ClasslessMgr.h"
#include "CoAPort.h"
#include "Creature.h"
#include "Log.h"
#include "Player.h"
#include "Random.h"
#include "ScriptMgr.h"
#include "Spell.h"
#include "SpellAuraEffects.h"
#include "SpellAuras.h"
#include "SpellInfo.h"
#include "SpellMgr.h"
#include <algorithm>
#include <array>
#include <mutex>
#include <unordered_map>

using namespace AscensionCompatData;

namespace
{
constexpr uint32 SPELL_PYROMANCER_HEAT = 807389;
constexpr uint32 SPELL_PYROMANCER_EMBER = 807533;
constexpr uint8 PYROMANCER_HEAT_PER_EMBER = 100;
constexpr uint32 SPELL_STORMBRINGER_STATIC = 803102;
constexpr uint32 SPELL_STORMBRINGER_CHARGED_CONDUIT = 803790;
constexpr uint32 SPELL_STORMBRINGER_WRATH_OF_ALAKIR = 300834;
constexpr uint32 SPELL_STORMBRINGER_UNSHACKLE_EXTENSION = 300835;
constexpr uint32 SPELL_BLOODMAGE_THIRST_PASSIVE = 92112;
constexpr uint32 SPELL_BLOODMAGE_THIRST = 706613;

// The kits whose rules this runs.
constexpr uint32 SPELL_FELSWORN_FURY = 800058;
constexpr uint32 SPELL_REAPER_REAPED_SOUL = 500363;
constexpr uint32 SPELL_REAPER_SOUL_INFUSION = 803031;
constexpr uint32 SPELL_REAPER_SOUL_INFUSION_REMOVER = 561290;
constexpr uint32 SPELL_REAPER_SOUL_FRAGMENT = 805077;
constexpr uint32 SPELL_REAPER_GENERATE_SOUL = 805078;
constexpr uint32 SPELL_REAPER_SCYTHE_RUSH = 500359;
constexpr uint32 SPELL_REAPER_SCYTHE_RUSH_MARKER = 500377;
constexpr uint32 SPELL_REAPER_HARVEST_TIME = 803995;
constexpr uint8 REAPER_SOUL_FRAGMENT_COST = 3;
constexpr std::array<uint32, 12> REAPER_ALL_SOUL_CONSUMERS = {
    500483, 500484, 500576, 500631, 572341, 572342, 573316, 573317, 573318, 573319, 573321, 573322
};
constexpr std::array<std::pair<uint32, uint32>, 1> REAPER_ONE_SOUL_CONSUMERS = { { { 500361, 500361 } } };

constexpr std::array<uint8, 15> SERVED_CLASSES = {
    CLASS_BARBARIAN, CLASS_DEMON_HUNTER, CLASS_CHRONOMANCER, CLASS_STORMBRINGER, CLASS_FLESHWARDEN,
    CLASS_MONK, CLASS_SON_OF_ARUGAL, CLASS_NECROMANCER, CLASS_PYROMANCER, CLASS_STARCALLER,
    CLASS_SUN_CLERIC, CLASS_TINKER, CLASS_PROPHET, CLASS_REAPER, CLASS_SPIRIT_MAGE
};

bool Serves(uint8 classId)
{
    return std::find(SERVED_CLASSES.begin(), SERVED_CLASSES.end(), classId) != SERVED_CLASSES.end();
}

// the player, when the realm runs CoA and the Hero owns a served kit
Player* ServedPlayer(Unit const* unit)
{
    if (!sClasslessMgr->cfg.coaEnable || !sClasslessMgr->cfg.coaResources || !unit || !unit->IsPlayer())
        return nullptr;
    Player* player = const_cast<Unit*>(unit)->ToPlayer();
    for (uint8 classId : SERVED_CLASSES)
        if (HasCoAKit(player, classId))
            return player;
    return nullptr;
}

bool Owns(Player const* player, uint8 classId)
{
    return Serves(classId) && HasCoAKit(player, classId);
}

bool InRange(uint32 spellId, uint32 first, uint32 last)
{
    return (!first && !last) || (spellId >= first && spellId <= last);
}

bool AuraGatesPass(Player const* player, uint32 required, uint32 forbidden)
{
    return (!required || player->HasAura(required)) && (!forbidden || !player->HasAura(forbidden));
}

uint8 AuraStacks(Unit const* unit, uint32 spellId)
{
    if (Aura const* aura = unit->GetAura(spellId))
        return aura->GetStackAmount();
    return 0;
}

void ModifyAuraStacks(Player* player, uint32 spellId, int32 amount)
{
    if (!amount)
        return;

    if (HandleAscensionReaperResource(player, spellId, amount) ||
        AscensionPyromancer::Resource(player, spellId, amount) ||
        AscensionVenomancer::Resource(player, spellId, amount) ||
        AscensionTinker::Resource(player, spellId, amount) ||
        AscensionSunCleric::Resource(player, spellId, amount))
        return;

    if (spellId == SPELL_FELSWORN_FURY && amount > 0)
        AscensionFelsworn::Generated(player, uint32(amount));

    if (Aura* aura = player->GetAura(spellId))
    {
        aura->ModStackAmount(amount);
        return;
    }

    if (amount < 0)
        return;

    if (Aura* aura = player->AddAura(spellId, player))
        if (amount > 1)
            aura->ModStackAmount(amount - 1);
}

bool ApplyGainRule(Player* player, ResourceGainRule const& rule)
{
    if (!rule.ChancePercent || (rule.ChancePercent < 100 && !roll_chance_i(rule.ChancePercent)))
        return false;

    if (rule.Mutation == ResourceMutation::AuraStacks)
    {
        ModifyAuraStacks(player, rule.ResourceSpellId, rule.Amount);
        return true;
    }

    for (int16 count = 0; count < rule.Amount; ++count)
        player->CastSpell(player, rule.ResourceSpellId, true);
    return true;
}

bool MatchesGainRule(Player const* player, uint32 spellId, ResourceGainRule const& rule)
{
    return Owns(player, rule.ClassId) && InRange(spellId, rule.FirstSpellId, rule.LastSpellId);
}

bool MatchesNativePowerRule(Player const* player, uint32 spellId, NativePowerGainRule const& rule)
{
    return Owns(player, rule.ClassId) && InRange(spellId, rule.FirstSpellId, rule.LastSpellId);
}

bool MatchesCostRule(Player const* player, uint32 spellId, ResourceCostRule const& rule)
{
    return Owns(player, rule.ClassId) && spellId >= rule.FirstSpellId && spellId <= rule.LastSpellId;
}

bool SpellDealsDamage(SpellInfo const* spellInfo)
{
    return spellInfo &&
        (spellInfo->HasEffect(SPELL_EFFECT_SCHOOL_DAMAGE) || spellInfo->HasEffect(SPELL_EFFECT_WEAPON_DAMAGE) ||
            spellInfo->HasEffect(SPELL_EFFECT_WEAPON_DAMAGE_NOSCHOOL) ||
            spellInfo->HasEffect(SPELL_EFFECT_WEAPON_PERCENT_DAMAGE) ||
            spellInfo->HasEffect(SPELL_EFFECT_NORMALIZED_WEAPON_DMG));
}

// A resource that reaches its threshold casts the threshold aura, and one that falls below it drops it;
// Pyromancer Heat turns into Ember every hundred.
void SynchronizeThresholdResources(Player* player)
{
    for (ResourceThresholdRule const& rule : ResourceThresholdRules)
    {
        if (!Owns(player, rule.ClassId))
            continue;

        bool const meetsThreshold = AuraStacks(player, rule.ResourceSpellId) >= rule.Amount;
        if (meetsThreshold && !player->HasAura(rule.ThresholdSpellId))
            player->CastSpell(player, rule.ThresholdSpellId, true);
        else if (!meetsThreshold && player->HasAura(rule.ThresholdSpellId))
            player->RemoveAurasDueToSpell(rule.ThresholdSpellId);
    }

    if (Owns(player, CLASS_PYROMANCER))
        while (AuraStacks(player, SPELL_PYROMANCER_HEAT) >= PYROMANCER_HEAT_PER_EMBER)
        {
            ModifyAuraStacks(player, SPELL_PYROMANCER_HEAT, -PYROMANCER_HEAT_PER_EMBER);
            ModifyAuraStacks(player, SPELL_PYROMANCER_EMBER, 1);
        }

    if (Owns(player, CLASS_REAPER))
    {
        while (AuraStacks(player, SPELL_REAPER_SOUL_FRAGMENT) >= REAPER_SOUL_FRAGMENT_COST)
        {
            ModifyAuraStacks(player, SPELL_REAPER_SOUL_FRAGMENT, -REAPER_SOUL_FRAGMENT_COST);
            ModifyAuraStacks(player, SPELL_REAPER_REAPED_SOUL, 1);
        }

        if (AuraStacks(player, SPELL_REAPER_REAPED_SOUL) >= 3 && !player->HasAura(SPELL_REAPER_SOUL_INFUSION))
        {
            player->CastSpell(player, SPELL_REAPER_SOUL_INFUSION, true);
            ApplyAscensionReaperSoulInfusionGained(player);
        }
    }
}

bool HarvestTimePreserves(Player const* player, SpellInfo const* spellInfo)
{
    if (spellInfo->CasterAuraSpell != SPELL_REAPER_SOUL_INFUSION || !player->HasAura(SPELL_REAPER_HARVEST_TIME))
        return false;

    SpellInfo const* harvestTime = sSpellMgr->GetSpellInfo(SPELL_REAPER_HARVEST_TIME);
    if (!harvestTime)
        return false;

    return roll_chance_f(std::abs(harvestTime->Effects[EFFECT_1].CalcValue()));
}

bool WasAvoidedByEveryTarget(Player const* player, Spell* spell)
{
    bool external = false;
    for (TargetInfo const& hit : *spell->GetUniqueTargetInfo())
    {
        if (hit.targetGUID == player->GetGUID())
            continue;

        if (hit.missCondition != SPELL_MISS_MISS && hit.missCondition != SPELL_MISS_DODGE &&
            hit.missCondition != SPELL_MISS_PARRY)
            return false;

        external = true;
    }
    return external;
}

// Reaper spells spend Reaped Souls: some all of them, some one; Soul Infusion changes what is left.
void ConsumeReaperSouls(Player* player, Spell* spell)
{
    if (!Owns(player, CLASS_REAPER))
        return;

    SpellInfo const* spellInfo = spell->GetSpellInfo();
    if (HarvestTimePreserves(player, spellInfo))
        return;

    bool const requiresSoulInfusion = spellInfo->CasterAuraSpell == SPELL_REAPER_SOUL_INFUSION &&
        player->HasAura(SPELL_REAPER_SOUL_INFUSION);

    uint32 const spellId = spellInfo->Id;
    if (std::find(REAPER_ALL_SOUL_CONSUMERS.begin(), REAPER_ALL_SOUL_CONSUMERS.end(), spellId) !=
        REAPER_ALL_SOUL_CONSUMERS.end())
    {
        if (WasAvoidedByEveryTarget(player, spell))
            return;

        player->RemoveAurasDueToSpell(SPELL_REAPER_REAPED_SOUL);
        player->RemoveAurasDueToSpell(SPELL_REAPER_SOUL_INFUSION);
        if (requiresSoulInfusion)
            ApplyAscensionReaperSoulInfusionSpent(player);
        return;
    }

    if (requiresSoulInfusion && !WasAvoidedByEveryTarget(player, spell))
    {
        player->CastSpell(player, SPELL_REAPER_SOUL_INFUSION_REMOVER, true);
        ApplyAscensionReaperSoulInfusionSpent(player);
        return;
    }

    for (std::pair<uint32, uint32> const& range : REAPER_ONE_SOUL_CONSUMERS)
        if (spellId >= range.first && spellId <= range.second)
        {
            ModifyAuraStacks(player, SPELL_REAPER_REAPED_SOUL, -1);
            return;
        }
}

// Stormbringer Static fades five seconds after combat ends, a stack a second.
std::mutex staticDecayLock;
std::unordered_map<ObjectGuid, uint32> staticDecayTimers;

void ForgetStaticDecay(ObjectGuid guid)
{
    std::lock_guard<std::mutex> lock(staticDecayLock);
    staticDecayTimers.erase(guid);
}

uint32 AdvanceStaticDecay(ObjectGuid guid, uint8 stacks, uint32 diff)
{
    constexpr uint32 graceMs = 5000;
    constexpr uint32 intervalMs = 1000;
    std::lock_guard<std::mutex> lock(staticDecayLock);
    uint32& timer = staticDecayTimers[guid];
    uint64 const elapsed = uint64(timer) + diff;
    if (elapsed < graceMs + intervalMs)
    {
        timer = uint32(elapsed);
        return 0;
    }

    uint32 const loss = uint32(std::min<uint64>(stacks, (elapsed - graceMs) / intervalMs));
    if (loss == stacks)
        staticDecayTimers.erase(guid);
    else
        timer = graceMs + uint32((elapsed - graceMs) % intervalMs);
    return loss;
}

void DecayStatic(Player* player, uint32 diff)
{
    ObjectGuid const guid = player->GetGUID();
    uint8 const stacks = AuraStacks(player, SPELL_STORMBRINGER_STATIC);
    if (!Owns(player, CLASS_STORMBRINGER) || !player->IsAlive() || !stacks || player->IsInCombat())
    {
        ForgetStaticDecay(guid);
        return;
    }

    if (uint32 const loss = AdvanceStaticDecay(guid, stacks, diff))
        ModifyAuraStacks(player, SPELL_STORMBRINGER_STATIC, -int32(loss));
}

void ExtendUnshackleOnStaticDepleted(Player* player, ResourceCostRule const& rule)
{
    if (rule.ClassId != CLASS_STORMBRINGER || rule.ResourceSpellId != SPELL_STORMBRINGER_STATIC ||
        !player->HasSpell(SPELL_STORMBRINGER_WRATH_OF_ALAKIR))
        return;

    player->CastSpell(player, SPELL_STORMBRINGER_UNSHACKLE_EXTENSION, true);
}

// whether a hit event applies, and whether it fires once per cast
struct HitEvent
{
    bool qualifies = false;
    bool firstOnly = false;
};

HitEvent EvaluateHitEvent(ResourceGainEvent event, bool successful, bool hostile, bool damaging, bool critical)
{
    HitEvent result;
    switch (event)
    {
        case ResourceGainEvent::FirstSuccessfulHostileTarget:
            result = { successful && hostile, true };
            break;
        case ResourceGainEvent::EachSuccessfulHostileTarget:
            result = { successful && hostile, false };
            break;
        case ResourceGainEvent::FirstSuccessfulDamagingHit:
            result = { successful && hostile && damaging, true };
            break;
        case ResourceGainEvent::EachSuccessfulDamagingHit:
            result = { successful && hostile && damaging, false };
            break;
        case ResourceGainEvent::FirstCriticalDamagingHit:
            result = { successful && hostile && damaging && critical, true };
            break;
        case ResourceGainEvent::EachCriticalDamagingHit:
            result = { successful && hostile && damaging && critical, false };
            break;
        default:
            break;
    }
    return result;
}

bool IsHitEvent(ResourceGainEvent event)
{
    return event != ResourceGainEvent::Cast && event != ResourceGainEvent::PeriodicDamageTick &&
        event != ResourceGainEvent::Block;
}

class cw_coa_resource_spells : public AllSpellScript
{
public:
    cw_coa_resource_spells() : AllSpellScript("cw_coa_resource_spells", {
        ALLSPELLHOOK_ON_SPELL_CHECK_CAST,
        ALLSPELLHOOK_CAN_PREPARE,
        ALLSPELLHOOK_ON_CAST,
        ALLSPELLHOOK_ON_HIT_RESULT
    }) { }

    // Generate Soul needs a full fragment set
    [[nodiscard]] bool CanPrepare(Spell* spell, SpellCastTargets const* /*targets*/,
                                  AuraEffect const* /*triggeredByAura*/) override
    {
        if (!spell || spell->GetSpellInfo()->Id != SPELL_REAPER_GENERATE_SOUL)
            return true;

        Player* player = ServedPlayer(spell->GetCaster());
        return !player || !Owns(player, CLASS_REAPER) ||
            AuraStacks(player, SPELL_REAPER_SOUL_FRAGMENT) >= REAPER_SOUL_FRAGMENT_COST;
    }

    // a spell that spends a resource cannot be cast without it
    void OnSpellCheckCast(Spell* spell, bool /*strict*/, SpellCastResult& result) override
    {
        if (!spell || spell->IsTriggered() || result != SPELL_CAST_OK)
            return;

        Player* player = ServedPlayer(spell->GetCaster());
        if (!player)
            return;

        uint32 const spellId = spell->GetSpellInfo()->Id;
        if (Owns(player, CLASS_REAPER) && spellId == SPELL_REAPER_SCYTHE_RUSH)
            if (Unit* target = spell->m_targets.GetUnitTarget())
                if (target->HasAura(SPELL_REAPER_SCYTHE_RUSH_MARKER, player->GetGUID()))
                {
                    result = SPELL_FAILED_TARGET_AURASTATE;
                    return;
                }

        for (ResourceCostRule const& rule : ResourceCostRules)
        {
            if (!MatchesCostRule(player, spellId, rule))
                continue;

            if (AuraStacks(player, rule.ResourceSpellId) < rule.Amount)
                result = SPELL_FAILED_NO_POWER;
            return;
        }
    }

    void OnSpellCast(Spell* spell, Unit* /*caster*/, SpellInfo const* spellInfo, bool /*skipCheck*/) override
    {
        if (!spell || spell->IsTriggered())
            return;

        Player* player = ServedPlayer(spell->GetCaster());
        if (!player)
            return;

        uint32 const spellId = spellInfo->Id;

        if (Owns(player, CLASS_SON_OF_ARUGAL) && spellInfo->SpellFamilyName == 26 &&
            spellInfo->PowerType == POWER_HEALTH && spell->GetPowerCost() > 0 &&
            player->HasAura(SPELL_BLOODMAGE_THIRST_PASSIVE))
            ModifyAuraStacks(player, SPELL_BLOODMAGE_THIRST, 1);

        for (ResourceGainRule const& rule : ResourceGainRules)
            if (rule.Event == ResourceGainEvent::Cast && MatchesGainRule(player, spellId, rule) &&
                AuraGatesPass(player, rule.RequiredAuraSpellId, rule.ForbiddenAuraSpellId))
                ApplyGainRule(player, rule);

        for (NativePowerGainRule const& rule : NativePowerGainRules)
            if (rule.Event == ResourceGainEvent::Cast && MatchesNativePowerRule(player, spellId, rule) &&
                AuraGatesPass(player, rule.RequiredAuraSpellId, rule.ForbiddenAuraSpellId))
                player->ModifyPower(static_cast<Powers>(rule.PowerType), rule.InternalAmount);

        for (ResourceCostRule const& rule : ResourceCostRules)
        {
            if (!MatchesCostRule(player, spellId, rule))
                continue;

            if (rule.ClassId == CLASS_STORMBRINGER && rule.ResourceSpellId == SPELL_STORMBRINGER_STATIC &&
                player->HasAura(SPELL_STORMBRINGER_CHARGED_CONDUIT))
                break;

            if (rule.PreserveCostAuraSpellId && player->HasAura(rule.PreserveCostAuraSpellId) &&
                rule.PreserveCostChancePercent && roll_chance_i(rule.PreserveCostChancePercent))
                break;

            if (rule.Consumption == ResourceConsumption::Fixed)
            {
                ModifyAuraStacks(player, rule.ResourceSpellId, -rule.Amount);
                ExtendUnshackleOnStaticDepleted(player, rule);
            }
            else if (rule.Consumption == ResourceConsumption::All)
            {
                player->RemoveAurasDueToSpell(rule.ResourceSpellId);
                ExtendUnshackleOnStaticDepleted(player, rule);
            }
            break;
        }

        ConsumeReaperSouls(player, spell);
        SynchronizeThresholdResources(player);
    }

    void OnSpellHitResult(Spell* spell, Unit* target, uint8 missInfo, uint32 damage, uint32 /*healing*/,
                          bool critical) override
    {
        if (!spell || spell->IsTriggered() || !target)
            return;

        Player* player = ServedPlayer(spell->GetCaster());
        if (!player)
            return;

        bool const successful = missInfo == SPELL_MISS_NONE;
        bool const hostile = target != player && !player->IsFriendlyTo(target);
        bool const damaging = damage > 0 || SpellDealsDamage(spell->GetSpellInfo());
        uint32 const spellId = spell->GetSpellInfo()->Id;
        std::array<int8, 9> firstEventState = {};
        bool changed = false;

        // a "first" event fires once per cast, however many targets it hits
        auto firstHandled = [&](ResourceGainEvent event)
        {
            uint8 const index = static_cast<uint8>(event);
            if (!firstEventState[index])
                firstEventState[index] = spell->TryMarkScriptEventHandled(index) ? 1 : -1;
            return firstEventState[index] > 0;
        };

        for (ResourceGainRule const& rule : ResourceGainRules)
        {
            if (!IsHitEvent(rule.Event) || !MatchesGainRule(player, spellId, rule) ||
                !AuraGatesPass(player, rule.RequiredAuraSpellId, rule.ForbiddenAuraSpellId))
                continue;

            HitEvent const event = EvaluateHitEvent(rule.Event, successful, hostile, damaging, critical);
            if (!event.qualifies || (event.firstOnly && !firstHandled(rule.Event)))
                continue;

            changed = ApplyGainRule(player, rule) || changed;
        }

        for (NativePowerGainRule const& rule : NativePowerGainRules)
        {
            if (!IsHitEvent(rule.Event) || !MatchesNativePowerRule(player, spellId, rule) ||
                !AuraGatesPass(player, rule.RequiredAuraSpellId, rule.ForbiddenAuraSpellId))
                continue;

            HitEvent const event = EvaluateHitEvent(rule.Event, successful, hostile, damaging, critical);
            if (!event.qualifies || (event.firstOnly && !firstHandled(rule.Event)))
                continue;

            int32 amount = rule.InternalAmount;
            if (rule.AmountSpellId)
                if (SpellInfo const* amountSpell = sSpellMgr->GetSpellInfo(rule.AmountSpellId))
                    if (amountSpell->Effects[EFFECT_0].Effect == SPELL_EFFECT_ENERGIZE &&
                        amountSpell->Effects[EFFECT_0].MiscValue == rule.PowerType)
                        amount = amountSpell->Effects[EFFECT_0].CalcValue(player);

            player->ModifyPower(static_cast<Powers>(rule.PowerType), amount);
            changed = true;
        }

        if (changed)
            SynchronizeThresholdResources(player);
    }
};

class cw_coa_resource_units : public UnitScript
{
public:
    cw_coa_resource_units() : UnitScript("cw_coa_resource_units", true, {
        UNITHOOK_ON_BLOCK,
        UNITHOOK_ON_PERIODIC_DAMAGE_RESULT
    }) { }

    void OnBlock(Unit* victim, Unit* /*attacker*/) override
    {
        Player* player = ServedPlayer(victim);
        if (!player)
            return;

        bool changed = false;
        for (ResourceGainRule const& rule : ResourceGainRules)
            if (rule.Event == ResourceGainEvent::Block && Owns(player, rule.ClassId) &&
                AuraGatesPass(player, rule.RequiredAuraSpellId, rule.ForbiddenAuraSpellId))
                changed = ApplyGainRule(player, rule) || changed;

        if (changed)
            SynchronizeThresholdResources(player);
    }

    void OnPeriodicDamageResult(Unit* target, Unit* attacker, uint32 damage, SpellInfo const* spellInfo) override
    {
        if (!target || !attacker || !spellInfo)
            return;

        Creature const* creature = target->ToCreature();
        if (!damage && !(creature && creature->GetScriptName() == "npc_training_dummy"))
            return;

        Player* player = ServedPlayer(attacker);
        if (!player || target == player || player->IsFriendlyTo(target))
            return;

        bool changed = false;
        for (ResourceGainRule const& rule : ResourceGainRules)
            if (rule.Event == ResourceGainEvent::PeriodicDamageTick && MatchesGainRule(player, spellInfo->Id, rule) &&
                AuraGatesPass(player, rule.RequiredAuraSpellId, rule.ForbiddenAuraSpellId))
                changed = ApplyGainRule(player, rule) || changed;

        for (NativePowerGainRule const& rule : NativePowerGainRules)
            if (rule.Event == ResourceGainEvent::PeriodicDamageTick &&
                MatchesNativePowerRule(player, spellInfo->Id, rule) &&
                AuraGatesPass(player, rule.RequiredAuraSpellId, rule.ForbiddenAuraSpellId))
            {
                player->ModifyPower(static_cast<Powers>(rule.PowerType), rule.InternalAmount);
                changed = true;
            }

        if (changed)
            SynchronizeThresholdResources(player);
    }
};

class cw_coa_resource_players : public PlayerScript
{
public:
    cw_coa_resource_players() : PlayerScript("cw_coa_resource_players", {
        PLAYERHOOK_ON_LOGIN,
        PLAYERHOOK_ON_LOGOUT,
        PLAYERHOOK_ON_UPDATE
    }) { }

    void OnPlayerLogin(Player* player) override
    {
        ForgetStaticDecay(player->GetGUID());
        if (ServedPlayer(player))
            SynchronizeThresholdResources(player);
    }

    void OnPlayerLogout(Player* player) override
    {
        if (player)
            ForgetStaticDecay(player->GetGUID());
    }

    void OnPlayerUpdate(Player* player, uint32 diff) override
    {
        if (!ServedPlayer(player))
            return;

        DecayStatic(player, diff);
        SynchronizeThresholdResources(player);
    }
};
}

void AddCoAResourceScripts()
{
    new cw_coa_resource_spells();
    new cw_coa_resource_units();
    new cw_coa_resource_players();
}
