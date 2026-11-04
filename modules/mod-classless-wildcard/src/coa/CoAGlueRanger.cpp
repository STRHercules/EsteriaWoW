/* Copyright (C) 2016+ AzerothCore, GNU AGPL v3. */

// Ranger's shared CoA contracts and resources, scoped to owners of the Ranger kit.

#include "AscensionCustomResourceData.h"
#include "AscensionRangerDamage.h"
#include "AscensionRangerTalents.h"
#include "ClasslessMgr.h"
#include "CoAPort.h"
#include "DataMap.h"
#include "Log.h"
#include "Player.h"
#include "Random.h"
#include "ScriptMgr.h"
#include "Spell.h"
#include "SpellAuraEffects.h"
#include "SpellAuras.h"
#include "SpellInfo.h"
#include "World.h"
#include "WorldSession.h"
#include <algorithm>
#include <array>
#include <cmath>

void AddAscensionRangerDamageScripts();
void AddAscensionRangerScalingScripts();
void AddAscensionRangerAssaultScripts();
void AddSC_AscensionRangerSecondary();
void AddSC_AscensionRangerDirtyFighter();
void AddSC_AscensionRangerDeadeye();
void AddSC_AscensionRangerHookshot();
void AddSC_AscensionRangerOutmaneuver();
void AddSC_AscensionRangerToTheSkies();
void AddSC_AscensionRangerFlowers();
void AddSC_AscensionRangerPetalkeeper();
void AddSC_AscensionRangerFalconstrike();
void AddSC_AscensionRangerArchery();

namespace
{
bool RangerOf(Player const* player)
{
    return sClasslessMgr->cfg.coaEnable && player && player->IsInWorld() &&
        HasCoAKit(player, CLASS_RANGER);
}

constexpr uint32 RANGER_FAMILY = uint32(CLASS_RANGER) + 6;
constexpr float RANGER_FOCUS_PER_SECOND = 12.0f;
constexpr float RANGER_FOCUS_MAXIMUM = 100.0f;
constexpr char RANGER_RESOURCE_STATE[] = "cw.coa.ranger.resources";

struct RangerResourceState : DataMap::Base
{
    float FocusFraction = 0.0f;
};

constexpr uint32 SPELL_RANGER_ADVANTAGE = 804329;
constexpr uint32 SPELL_RANGER_ADVANTAGE_DECREMENT = 520618;
constexpr uint32 SPELL_RANGER_ADVANTAGE_DECREMENT_PASSIVE = 582770;
constexpr uint32 SPELL_RANGER_ADVANTAGE_INCREMENT = 524659;
constexpr uint32 SPELL_RANGER_ELUDE = 801345;
constexpr uint32 SPELL_RANGER_ELUDE_EFFECTS = 524862;
constexpr uint32 SPELL_RANGER_ELUDE_SPEED_PENALTY = 524886;
constexpr uint32 SPELL_RANGER_ELUSIVE_CHARACTER = 560340;
constexpr uint32 SPELL_RANGER_ELUSIVE_CHARACTER_EFFECTS = 705046;
constexpr uint32 SPELL_RANGER_FOREST_DWELLER = 524864;
constexpr uint32 SPELL_RANGER_FOREST_DWELLER_HEAL = 524863;
constexpr uint32 SPELL_RANGER_RAVAGER = 92116;
constexpr uint32 SPELL_RANGER_RAVAGER_LEGACY = 500024;
#ifdef ESTERIA_COA_CONDITIONAL_COMBAT
constexpr uint32 SPELL_RANGER_HUNTING_TACTICS = 300897;
#endif
constexpr uint32 SPELL_RANGER_ARCHERY_MASTER = 706281;
constexpr uint32 SPELL_RANGER_RUB_IT_IN = 705085;
constexpr uint32 SPELL_RANGER_SNIPERS_FOCUS = 680470;
constexpr uint32 SPELL_RANGER_SNIPERS_FOCUS_ENERGIZE = 807318;
constexpr uint32 SPELL_RANGER_MAXIMUM_POWER = 560688;
constexpr uint32 SPELL_RANGER_MAXIMUM_POWER_EXTENSION = 560689;
constexpr uint32 SPELL_RANGER_LETHAL_CUNNING = 704320;
constexpr uint32 SPELL_RANGER_LETHAL_CUNNING_EFFECTS = 704321;
constexpr uint32 SPELL_RANGER_SKIRMISH = 802039;
constexpr uint32 SPELL_RANGER_SEARING_QUIVER = 500103;
constexpr uint32 SPELL_RANGER_POISON_QUIVER = 800260;
constexpr uint32 SPELL_RANGER_LIGHT_QUIVER = 800261;
constexpr uint32 SPELL_RANGER_HUNTING_QUIVER = 800262;
constexpr uint32 SPELL_RANGER_SKIRMISHERS_QUIVER = 801069;
constexpr uint32 SPELL_RANGER_SEARING_QUIVER_DAMAGE = 681109;
constexpr uint32 SPELL_RANGER_POISON_QUIVER_DAMAGE = 500104;
constexpr uint32 SPELL_RANGER_BOUNTY_HUNTER = 803114;
constexpr uint32 SPELL_RANGER_BOUNTY_HUNTER_DEBUFF = 560722;
constexpr uint32 SPELL_RANGER_RUSTY_SHIV_DAMAGE = 681459;
constexpr uint8 RANGER_ADVANTAGE_REFUND_CHANCE = 20;
constexpr uint8 RANGER_ADVANTAGE_CAST_EVENT = 30;
constexpr uint8 RANGER_ARCHERY_MASTER_EVENT = 31;

constexpr std::array<uint32, 5> RANGER_QUIVERS =
{{
    SPELL_RANGER_SEARING_QUIVER,
    SPELL_RANGER_POISON_QUIVER,
    SPELL_RANGER_LIGHT_QUIVER,
    SPELL_RANGER_HUNTING_QUIVER,
    SPELL_RANGER_SKIRMISHERS_QUIVER
}};

bool IsSpellInRange(uint32 spellId, uint32 first, uint32 last)
{
    return spellId >= first && spellId <= last;
}

bool IsRangerWildStrike(uint32 spellId)
{
    return spellId == 800083 || IsSpellInRange(spellId, 501724, 501734);
}

bool IsRangerFlank(uint32 spellId)
{
    return spellId == 804940 || IsSpellInRange(spellId, 805082, 805088) ||
        IsSpellInRange(spellId, 582530, 582531);
}

bool IsRangerQuickShot(uint32 spellId)
{
    return spellId == 500074 || IsSpellInRange(spellId, 572727, 572732);
}

bool IsRangerHuntingShot(uint32 spellId)
{
    return spellId == 801191 || IsSpellInRange(spellId, 547202, 547208);
}

bool IsRangerToxicDart(uint32 spellId)
{
    return spellId == 807237 || IsSpellInRange(spellId, 807324, 807330);
}

bool IsRangerBountyHunterTrigger(uint32 spellId)
{
    return IsRangerFlank(spellId) ||
        spellId == SPELL_RANGER_RUSTY_SHIV_DAMAGE;
}

void ApplyRangerEludeExitEffects(Player* player, bool removedByDeath)
{
    if (!player || !RangerOf(player) || removedByDeath || !player->IsAlive() ||
        !player->IsInWorld() || !player->GetSession() || player->GetSession()->PlayerLogout() ||
        player->HasAura(SPELL_RANGER_ELUDE) || !player->HasAura(SPELL_RANGER_ELUSIVE_CHARACTER))
        return;

    player->CastSpell(player, SPELL_RANGER_ELUSIVE_CHARACTER_EFFECTS, true);
}

void RefreshRangerEludePenalty(Player* player)
{
    if (!player || !RangerOf(player))
        return;

    AuraEffect* penalty = player->GetAuraEffect(SPELL_RANGER_ELUDE_SPEED_PENALTY, EFFECT_2);
    if (!penalty || penalty->GetAuraType() != SPELL_AURA_MOD_DECREASE_SPEED)
        return;

    if (player->HasAura(SPELL_RANGER_FOREST_DWELLER))
        penalty->ChangeAmount(0);
    else
    {
        penalty->SetCanBeRecalculated(true);
        penalty->ChangeAmount(penalty->CalculateAmount(player), false);
    }
}

void ApplyRangerFixedDurationContract(SpellInfo* spellInfo)
{
    if (!spellInfo || spellInfo->Id != SPELL_RANGER_ADVANTAGE ||
        spellInfo->SpellFamilyName != uint32(CLASS_RANGER) + 6)
        return;

    SpellEffectInfo& duration = spellInfo->Effects[EFFECT_1];
    if (duration.Effect == SPELL_EFFECT_APPLY_AURA &&
        duration.ApplyAuraName == SPELL_AURA_ADD_FLAT_MODIFIER &&
        duration.MiscValue == SPELLMOD_DURATION &&
        (duration.SpellClassMask == flag96(16777280, 0, 1048704) ||
            duration.SpellClassMask == flag96(16777216, 0, 1048704)))
    {
        duration.SpellClassMask = flag96(16777216, 0, 1048704);
    }
    else
    {
        LOG_ERROR("coa", "Skipped unexpected Advantage duration record {}", spellInfo->Id);
    }
}

#ifdef ESTERIA_COA_CONDITIONAL_COMBAT
void ApplyRangerConditionalDamageContracts(SpellInfo* spellInfo)
{
    if (!spellInfo || spellInfo->SpellFamilyName != uint32(CLASS_RANGER) + 6)
        return;

    SpellEffIndex index;
    int32 amount;
    uint32 state;
    flag96 mask;
    if (spellInfo->Id == SPELL_RANGER_RAVAGER)
    {
        index = EFFECT_2;
        amount = 49;
        state = AURA_STATE_BLEEDING;
        mask = flag96(0, 32768, 0);
    }
    else if (spellInfo->Id == SPELL_RANGER_HUNTING_TACTICS)
    {
        index = EFFECT_0;
        amount = 29;
        state = ASCENSION_TARGET_POISONED;
        mask = flag96(0, 134217728, 0);
    }
    else
        return;

    SpellEffectInfo& effect = spellInfo->Effects[index];
    bool const copied = effect.ApplyAuraName == SPELL_AURA_OVERRIDE_CLASS_SCRIPTS &&
        effect.MiscValue == ASCENSION_CLASSMASK_AURASTATE_DAMAGE && effect.MiscValueB == int32(state);
    bool const converted = effect.ApplyAuraName == SPELL_AURA_MOD_DAMAGE_DONE_VERSUS_AURASTATE &&
        effect.MiscValue == int32(state) && effect.MiscValueB == ASCENSION_CLASSMASK_AURASTATE_DAMAGE;
    if (effect.Effect == SPELL_EFFECT_APPLY_AURA && (copied || converted) && effect.BasePoints == amount &&
        effect.DieSides == 1 && effect.SpellClassMask == mask &&
        effect.TargetA.GetTarget() == TARGET_UNIT_CASTER && effect.TargetB.GetTarget() == 0)
    {
        effect.ApplyAuraName = SPELL_AURA_MOD_DAMAGE_DONE_VERSUS_AURASTATE;
        effect.MiscValue = int32(state);
        effect.MiscValueB = ASCENSION_CLASSMASK_AURASTATE_DAMAGE;
    }
    else
        LOG_ERROR("coa", "Skipped unexpected Ranger conditional damage record {}", spellInfo->Id);
}

void ApplyRangerSerrationsContract(SpellInfo* spellInfo)
{
    if (spellInfo->Id != 705050 && spellInfo->Id != 707850)
        return;

    int32 amount = spellInfo->Id == 705050 ? 4 : 9;
    for (SpellEffectInfo& effect : spellInfo->Effects)
    {
        if (effect.Effect != SPELL_EFFECT_APPLY_AURA ||
            effect.ApplyAuraName != SPELL_AURA_OVERRIDE_CLASS_SCRIPTS ||
            effect.MiscValue != ASCENSION_CLASSMASK_AURASTATE_DAMAGE)
            continue;

        if (effect.BasePoints == amount && effect.DieSides == 1)
        {
            effect.ApplyAuraName = SPELL_AURA_MOD_DAMAGE_DONE_VERSUS_AURASTATE;
            effect.MiscValue = effect.MiscValueB;
            effect.MiscValueB = ASCENSION_CLASSMASK_AURASTATE_DAMAGE;
        }
        else
            LOG_ERROR("coa", "Skipped unexpected Ranger Serrations record {}", spellInfo->Id);
        return;
    }

    LOG_ERROR("coa", "Skipped unexpected Ranger Serrations record {}", spellInfo->Id);
}

#endif

void ApplyRangerUnderhandedContracts(SpellInfo* spellInfo)
{
    if (!spellInfo || spellInfo->SpellFamilyName != uint32(CLASS_RANGER) + 6 ||
        (spellInfo->Id != 705061 && spellInfo->Id != 707884))
        return;

    int32 const basePoints = spellInfo->Id == 705061 ? 14 : 29;
    std::array<flag96, 2> const masks = {{flag96(0, 134217728, 0), flag96(0, 0, 128)}};
    for (SpellEffIndex index : {EFFECT_0, EFFECT_1})
    {
        SpellEffectInfo const& effect = spellInfo->Effects[index];
        int32 const copiedIndex = index == EFFECT_0 ? 42 : 45;
        int32 const script = index == EFFECT_0 ?
            ASCENSION_DIRECT_AP_COEFFICIENT_PCT : ASCENSION_PERIODIC_AP_COEFFICIENT_PCT;
        bool const copied = effect.ApplyAuraName == SPELL_AURA_ADD_PCT_MODIFIER && effect.MiscValue == copiedIndex;
        bool const converted = effect.ApplyAuraName == SPELL_AURA_OVERRIDE_CLASS_SCRIPTS && effect.MiscValue == script;
        if (effect.Effect != SPELL_EFFECT_APPLY_AURA || (!copied && !converted) || effect.MiscValueB != 0 ||
            effect.BasePoints != basePoints || effect.DieSides != 1 || effect.SpellClassMask != masks[index] ||
            effect.TargetA.GetTarget() != TARGET_UNIT_CASTER || effect.TargetB.GetTarget() != 0)
        {
            LOG_ERROR("coa", "Skipped unexpected Underhanded coefficient record {}", spellInfo->Id);
            return;
        }
    }

    for (SpellEffIndex index : {EFFECT_0, EFFECT_1})
    {
        spellInfo->Effects[index].ApplyAuraName = SPELL_AURA_OVERRIDE_CLASS_SCRIPTS;
        spellInfo->Effects[index].MiscValue = index == EFFECT_0 ?
            ASCENSION_DIRECT_AP_COEFFICIENT_PCT : ASCENSION_PERIODIC_AP_COEFFICIENT_PCT;
    }
}

void ApplyRangerInstinctualCombatantContract(SpellInfo* spellInfo)
{
    if (!spellInfo || (spellInfo->Id != 520572 && spellInfo->Id != 707319) ||
        spellInfo->SpellFamilyName != uint32(CLASS_RANGER) + 6)
        return;

    if (spellInfo->Id == 707319)
    {
        SpellEffectInfo& attackPower = spellInfo->Effects[EFFECT_1];
        if (attackPower.Effect == SPELL_EFFECT_APPLY_AURA &&
            attackPower.ApplyAuraName == SPELL_AURA_ADD_FLAT_MODIFIER &&
            attackPower.MiscValue == SPELLMOD_EFFECT2 && attackPower.MiscValueB == 0 &&
            attackPower.BasePoints == 9 && attackPower.DieSides == 1 &&
            attackPower.TargetA.GetTarget() == TARGET_UNIT_CASTER && attackPower.TargetB.GetTarget() == 0 &&
            (attackPower.SpellClassMask == flag96(16, 0, 8) || attackPower.SpellClassMask == flag96(16, 0, 0)))
            attackPower.SpellClassMask = flag96(16, 0, 0);
        else
            LOG_ERROR("coa", "Skipped unexpected Instinctual Combatant talent record {}", spellInfo->Id);
        return;
    }

    SpellEffectInfo& criticalChance = spellInfo->Effects[EFFECT_1];
    if (spellInfo->ProcFlags == 0 && (spellInfo->ProcCharges == 0 || spellInfo->ProcCharges == 3) &&
        spellInfo->GetDuration() == 20000 &&
        criticalChance.Effect == SPELL_EFFECT_APPLY_AURA &&
        criticalChance.ApplyAuraName == SPELL_AURA_ADD_FLAT_MODIFIER &&
        criticalChance.MiscValue == SPELLMOD_CRITICAL_CHANCE && criticalChance.MiscValueB == 0 &&
        criticalChance.BasePoints == 99 && criticalChance.DieSides == 1 &&
        criticalChance.TargetA.GetTarget() == TARGET_UNIT_CASTER && criticalChance.TargetB.GetTarget() == 0 &&
        (criticalChance.SpellClassMask == flag96(0, 134250498, 0) ||
            criticalChance.SpellClassMask == flag96(0, 134250496, 0)))
    {
        spellInfo->ProcCharges = 3;
        criticalChance.SpellClassMask = flag96(0, 134250496, 0);
    }
    else
        LOG_ERROR("coa", "Skipped unexpected Instinctual Combatant record {}", spellInfo->Id);
}

void ApplyAdditionalTargetContracts(SpellInfo* spellInfo)
{
    if (!spellInfo)
        return;

    enum AdditionalTargetSpells : uint32
    {
        AdvantageQuills = 801429,
        AerialAssault = 705068
    };

    struct Contract
    {
        uint32 SpellId;
        uint32 Family;
        SpellEffIndex EffectIndex;
        int32 BasePoints;
        std::array<uint32, 3> Mask;
    };
    static constexpr std::array<Contract, 2> contracts =
    {{
        {AdvantageQuills, 27, EFFECT_1, 0, {{0, 4, 0}}},
        {AerialAssault, 27, EFFECT_2, 1, {{512, 0, 0}}}
    }};

    for (Contract const& contract : contracts)
    {
        if (spellInfo->Id != contract.SpellId)
            continue;

        SpellEffectInfo& effect = spellInfo->Effects[contract.EffectIndex];
        if (spellInfo->SpellFamilyName == contract.Family &&
            spellInfo->ProcCharges == 0 &&
            effect.Effect == SPELL_EFFECT_APPLY_AURA &&
            (effect.ApplyAuraName == SPELL_AURA_ADD_FLAT_MODIFIER ||
                effect.ApplyAuraName == SPELL_AURA_MOD_MAX_AFFECTED_TARGETS) &&
            effect.MiscValue == 34 && effect.BasePoints == contract.BasePoints &&
            effect.DieSides == 1 && effect.TargetA.GetTarget() == TARGET_UNIT_CASTER &&
            effect.TargetB.GetTarget() == 0 &&
            effect.SpellClassMask == flag96(contract.Mask[0], contract.Mask[1], contract.Mask[2]))
        {
            effect.ApplyAuraName = SPELL_AURA_MOD_MAX_AFFECTED_TARGETS;
        }
        else
        {
            LOG_ERROR("coa",
                "Skipped unexpected additional-target record {}", spellInfo->Id);
        }
        return;
    }
}

void ApplyRangerForestDwellerContract(SpellInfo* spellInfo)
{
    if (!spellInfo || spellInfo->Id != SPELL_RANGER_FOREST_DWELLER ||
        spellInfo->SpellFamilyName != uint32(CLASS_RANGER) + 6)
        return;

    // The CoA client tables this was imported from carry the obsolete speed modifier on the third effect
    // slot; the contract below looks for it on the second. Read it as the contract expects.
    if (spellInfo->Effects[EFFECT_1].Effect == SPELL_EFFECT_APPLY_AURA &&
        spellInfo->Effects[EFFECT_1].ApplyAuraName == SPELL_AURA_ADD_FLAT_MODIFIER &&
        spellInfo->Effects[EFFECT_1].MiscValue == SPELLMOD_EFFECT3)
        spellInfo->Effects[EFFECT_1].MiscValue = SPELLMOD_EFFECT1;

    SpellEffectInfo const& heal = spellInfo->Effects[EFFECT_0];
    SpellEffectInfo& obsoleteSpeed = spellInfo->Effects[EFFECT_1];
    if (heal.Effect != SPELL_EFFECT_APPLY_AURA || heal.ApplyAuraName != SPELL_AURA_PERIODIC_TRIGGER_SPELL ||
        heal.TriggerSpell != SPELL_RANGER_FOREST_DWELLER_HEAL || heal.Amplitude != 3000 ||
        !((obsoleteSpeed.Effect == SPELL_EFFECT_APPLY_AURA &&
            obsoleteSpeed.ApplyAuraName == SPELL_AURA_ADD_FLAT_MODIFIER &&
            obsoleteSpeed.MiscValue == SPELLMOD_EFFECT1) || obsoleteSpeed.Effect == 0))
    {
        LOG_ERROR("coa", "Skipped unexpected Forest Dweller record {}", spellInfo->Id);
        return;
    }

    obsoleteSpeed.Effect = 0;
    obsoleteSpeed.ApplyAuraName = SPELL_AURA_NONE;
}

void ApplyRangerOffensiveSpellContracts(SpellInfo* spellInfo)
{
    if (!spellInfo || spellInfo->SpellFamilyName != uint32(CLASS_RANGER) + 6)
        return;

    bool const toxicDart = IsRangerToxicDart(spellInfo->Id);
    bool const precisionShot = spellInfo->Id == 500075 || IsSpellInRange(spellInfo->Id, 572108, 572113);
    if (toxicDart || precisionShot)
    {
        SpellEffectInfo const& damage = spellInfo->Effects[EFFECT_0];
        bool const expectedDamage = toxicDart
            ? damage.Effect == SPELL_EFFECT_APPLY_AURA && damage.ApplyAuraName == SPELL_AURA_PERIODIC_DAMAGE
            : damage.Effect == SPELL_EFFECT_SCHOOL_DAMAGE;
        SpellEffectInfo& helper = spellInfo->Effects[EFFECT_1];
        if (!expectedDamage || spellInfo->DmgClass != SPELL_DAMAGE_CLASS_RANGED ||
            (toxicDart && (helper.Effect != SPELL_EFFECT_TRIGGER_SPELL ||
                (helper.TriggerSpell != 681293 && helper.TriggerSpell != 807821))))
        {
            LOG_ERROR("coa", "Skipped unexpected Ranger offensive spell {}", spellInfo->Id);
            return;
        }

        spellInfo->AttributesEx &= ~SPELL_ATTR1_ALLOW_WHILE_STEALTHED;
        if (toxicDart)
        {
            helper.TriggerSpell = 807821;
        }
    }

    if (spellInfo->Id == 570017)
    {
        SpellEffectInfo const& stealth = spellInfo->Effects[EFFECT_1];
        if (stealth.Effect == SPELL_EFFECT_APPLY_AURA && stealth.ApplyAuraName == SPELL_AURA_MOD_STEALTH)
        {
            spellInfo->AuraInterruptFlags |= AURA_INTERRUPT_FLAG_CAST |
                AURA_INTERRUPT_FLAG_MELEE_ATTACK | AURA_INTERRUPT_FLAG_SPELL_ATTACK;
        }
        else
            LOG_ERROR("coa", "Skipped unexpected Woodland Adept stealth {}", spellInfo->Id);
    }
}

void AddRangerAdvantage(Player* player, uint8 amount)
{
    for (uint8 index = 0; index < amount; ++index)
        player->CastSpell(player, SPELL_RANGER_ADVANTAGE_INCREMENT, true);
}

void HandleRangerAdvantageCast(Spell* spell, Player* player)
{
    uint32 spellId = spell->GetSpellInfo()->Id;
    uint8 amount = 0;
    if (IsRangerWildStrike(spellId))
        amount = player->HasAura(SPELL_RANGER_RAVAGER) || player->HasAura(SPELL_RANGER_RAVAGER_LEGACY) ? 2 : 1;
    else if (IsRangerFlank(spellId))
        amount = 2;
    else if (IsRangerQuickShot(spellId) || IsRangerToxicDart(spellId))
        amount = 1;
    else if (IsRangerHuntingShot(spellId))
    {
        for (TargetInfo const& target : *spell->GetUniqueTargetInfo())
            if (target.targetGUID != player->GetGUID())
                ++amount;
    }

    if (amount && spell->TryMarkScriptEventHandled(RANGER_ADVANTAGE_CAST_EVENT))
        AddRangerAdvantage(player, amount);
}

void ApplyRangerQuiver(Player* player, uint32 spellId)
{
    for (uint32 quiverId : RANGER_QUIVERS)
        if (quiverId != spellId)
            player->RemoveAurasDueToSpell(quiverId);
}

void SynchronizeRangerQuiver(Player* player)
{
    Aura const* newest = nullptr;
    uint32 newestId = 0;
    for (uint32 spellId : RANGER_QUIVERS)
    {
        Aura const* aura = player->GetAura(spellId);
        if (aura && (!newest || aura->GetApplyTime() > newest->GetApplyTime()))
        {
            newest = aura;
            newestId = spellId;
        }
    }

    if (newest)
        ApplyRangerQuiver(player, newestId);
}

bool DidRangerAdvantageConsumerSucceed(Spell* spell, Player const* player)
{
    bool hasExternalTarget = false;
    for (TargetInfo const& targetInfo : *spell->GetUniqueTargetInfo())
    {
        if (targetInfo.targetGUID == player->GetGUID())
            continue;

        hasExternalTarget = true;
        if (targetInfo.missCondition == SPELL_MISS_NONE)
            return true;
    }

    return !hasExternalTarget;
}

void HandleRangerQuiverHit(Player* player, Unit* target,
    SpellInfo const* spellInfo, uint32 damage)
{
    if (spellInfo->DmgClass != SPELL_DAMAGE_CLASS_RANGED)
        return;

    if (AuraEffect const* searing = player->GetAuraEffect(
            SPELL_RANGER_SEARING_QUIVER, EFFECT_0); searing && damage)
    {
        int32 fireDamage = CalculatePct(damage, searing->GetAmount());
        player->CastCustomSpell(target, SPELL_RANGER_SEARING_QUIVER_DAMAGE,
            &fireDamage, nullptr, nullptr, true, nullptr, searing);
    }

    if (AuraEffect const* poison = player->GetAuraEffect(
            SPELL_RANGER_POISON_QUIVER, EFFECT_1))
    {
        player->CastSpell(target, SPELL_RANGER_POISON_QUIVER_DAMAGE, true,
            nullptr, poison);
    }
}

void HandleRangerBountyHunterHit(Player* player, Unit* target,
    uint32 spellId, uint32 damage)
{
    if (damage && player->HasAura(SPELL_RANGER_BOUNTY_HUNTER) &&
        IsRangerBountyHunterTrigger(spellId))
    {
        player->CastSpell(target, SPELL_RANGER_BOUNTY_HUNTER_DEBUFF, true);
    }
}

void HandleRangerAdvantageSpent(Player* player, uint8 amount)
{
    if (player->HasAura(SPELL_RANGER_RUB_IT_IN))
    {
        for (uint8 index = 0; index < amount; ++index)
            if (roll_chance_i(RANGER_ADVANTAGE_REFUND_CHANCE))
                AddRangerAdvantage(player, 1);
    }

    if (player->HasAura(SPELL_RANGER_SNIPERS_FOCUS))
    {
        for (uint8 index = 0; index < amount; ++index)
            if (roll_chance_i(RANGER_ADVANTAGE_REFUND_CHANCE))
                player->CastSpell(player,
                    SPELL_RANGER_SNIPERS_FOCUS_ENERGIZE, true);
    }

}

void HandleRangerMaximumPower(Player* player, uint8 amount)
{
    if (amount == 5 && player->HasAura(SPELL_RANGER_MAXIMUM_POWER) &&
        player->HasAura(SPELL_RANGER_SKIRMISH))
    {
        player->CastSpell(player, SPELL_RANGER_MAXIMUM_POWER_EXTENSION, true);
    }
}

static_assert([]
{
    for (auto const& rule : AscensionCompatData::ResourceGainRules)
        if (rule.ClassId == CLASS_RANGER &&
            (rule.Event != AscensionCompatData::ResourceGainEvent::Cast ||
                rule.Mutation != AscensionCompatData::ResourceMutation::AuraStacks ||
                rule.ResourceSpellId != SPELL_RANGER_ADVANTAGE || !rule.FirstSpellId))
            return false;
    return true;
}(), "Ranger resource rules need matching event and mutation handlers");

void ApplyRangerResourceGainRules(Player* player, uint32 spellId)
{
    for (AscensionCompatData::ResourceGainRule const& rule : AscensionCompatData::ResourceGainRules)
    {
        if (rule.ClassId != CLASS_RANGER || rule.Event != AscensionCompatData::ResourceGainEvent::Cast ||
            spellId < rule.FirstSpellId || spellId > rule.LastSpellId ||
            (rule.RequiredAuraSpellId && !player->HasAura(rule.RequiredAuraSpellId)) ||
            (rule.ForbiddenAuraSpellId && player->HasAura(rule.ForbiddenAuraSpellId)) ||
            !roll_chance_i(rule.ChancePercent))
            continue;

        if (Aura* resource = player->GetAura(rule.ResourceSpellId))
            resource->ModStackAmount(rule.Amount);
        else if (rule.Amount > 0)
            if (Aura* resource = player->AddAura(rule.ResourceSpellId, player))
                if (rule.Amount > 1)
                    resource->ModStackAmount(rule.Amount - 1);
    }
}

void SynchronizeRanger(Player* player)
{
    SynchronizeRangerQuiver(player);
    if (player->HasAura(SPELL_RANGER_ELUDE))
    {
        if (!player->HasAura(SPELL_RANGER_ELUDE_EFFECTS))
            player->CastSpell(player, SPELL_RANGER_ELUDE_EFFECTS, true);
        if (!player->HasAura(SPELL_RANGER_ELUDE_SPEED_PENALTY))
            player->CastSpell(player, SPELL_RANGER_ELUDE_SPEED_PENALTY, true);
        RefreshRangerEludePenalty(player);
    }
    else
    {
        player->RemoveAurasDueToSpell(SPELL_RANGER_ELUDE_EFFECTS);
        player->RemoveAurasDueToSpell(SPELL_RANGER_ELUDE_SPEED_PENALTY);
    }
}

class cw_coa_ranger_spells : public AllSpellScript
{
public:
    cw_coa_ranger_spells() : AllSpellScript("cw_coa_ranger_spells",
        { ALLSPELLHOOK_ON_CAST, ALLSPELLHOOK_ON_HIT_RESULT, ALLSPELLHOOK_ON_SPELL_CHECK_CAST }) { }

    void OnSpellCheckCast(Spell* spell, bool /*strict*/, SpellCastResult& result) override
    {
        Player* player = spell && spell->GetCaster() ? spell->GetCaster()->ToPlayer() : nullptr;
        if (!RangerOf(player) || spell->IsTriggered() || result != SPELL_CAST_OK)
            return;

        SpellInfo const* info = spell->GetSpellInfo();
        if (info->SpellFamilyName == RANGER_FAMILY && info->CasterAuraSpell == SPELL_RANGER_ADVANTAGE &&
            !player->HasAura(SPELL_RANGER_ADVANTAGE))
            result = SPELL_FAILED_CASTER_AURASTATE;
    }

    void OnSpellCast(Spell* spell, Unit* /*caster*/, SpellInfo const* info, bool /*skipCheck*/) override
    {
        Player* player = spell && spell->GetCaster() ? spell->GetCaster()->ToPlayer() : nullptr;
        if (!RangerOf(player) || spell->IsTriggered() || info->SpellFamilyName != RANGER_FAMILY)
            return;

        HandleRangerAdvantageCast(spell, player);
        if (info->CasterAuraSpell == SPELL_RANGER_ADVANTAGE)
        {
            if (!DidRangerAdvantageConsumerSucceed(spell, player))
                return;
            HandleAscensionRangerStonemason(spell, player);
            HandleAscensionRangerPhoenixPlumes(spell, player);
            uint8 spent = 0;
            if (Aura const* advantage = player->GetAura(SPELL_RANGER_ADVANTAGE))
                spent = advantage->GetStackAmount();
            HandleRangerMaximumPower(player, spent);

            float chance = 100.0f;
            player->ApplySpellMod(SPELL_RANGER_ADVANTAGE_DECREMENT_PASSIVE,
                SPELLMOD_CHANCE_OF_SUCCESS, chance, spell);
            if (roll_chance_f(chance))
            {
                player->CastSpell(player, SPELL_RANGER_ADVANTAGE_DECREMENT, true);
                HandleRangerAdvantageSpent(player, spent);
            }
        }
        ApplyRangerResourceGainRules(player, info->Id);
    }

    void OnSpellHitResult(Spell* spell, Unit* target, uint8 missInfo, uint32 damage,
        uint32 /*healing*/, bool critical) override
    {
        Player* player = spell && spell->GetCaster() ? spell->GetCaster()->ToPlayer() : nullptr;
        if (!RangerOf(player) || !target || target == player || player->IsFriendlyTo(target) ||
            missInfo != SPELL_MISS_NONE || spell->GetSpellInfo()->SpellFamilyName != RANGER_FAMILY)
            return;

        uint32 spellId = spell->GetSpellInfo()->Id;
        HandleRangerBountyHunterHit(player, target, spellId, damage);
        if (spell->IsTriggered())
            return;

        HandleRangerQuiverHit(player, target, spell->GetSpellInfo(), damage);
        if (IsRangerQuickShot(spellId) && critical && player->HasAura(SPELL_RANGER_ARCHERY_MASTER) &&
            spell->TryMarkScriptEventHandled(RANGER_ARCHERY_MASTER_EVENT))
            AddRangerAdvantage(player, 1);
    }
};

class cw_coa_ranger_auras : public UnitScript
{
public:
    cw_coa_ranger_auras() : UnitScript("cw_coa_ranger_auras", true,
        { UNITHOOK_ON_AURA_APPLY, UNITHOOK_ON_AURA_REMOVE }) { }

    void OnAuraApply(Unit* unit, Aura* aura) override
    {
        Player* player = unit ? unit->ToPlayer() : nullptr;
        if (!RangerOf(player) || !aura)
            return;

        uint32 spellId = aura->GetId();
        if (spellId == SPELL_RANGER_FOREST_DWELLER || spellId == SPELL_RANGER_ELUDE_SPEED_PENALTY)
            RefreshRangerEludePenalty(player);
        if (spellId == SPELL_RANGER_ELUDE)
        {
            player->CastSpell(player, SPELL_RANGER_ELUDE_EFFECTS, true);
            player->CastSpell(player, SPELL_RANGER_ELUDE_SPEED_PENALTY, true);
            if (player->HasAura(SPELL_RANGER_LETHAL_CUNNING))
                player->CastSpell(player, SPELL_RANGER_LETHAL_CUNNING_EFFECTS, true);
        }
        else if (std::find(RANGER_QUIVERS.begin(), RANGER_QUIVERS.end(), spellId) != RANGER_QUIVERS.end())
            ApplyRangerQuiver(player, spellId);
    }

    void OnAuraRemove(Unit* unit, AuraApplication* application, AuraRemoveMode mode) override
    {
        Player* player = unit ? unit->ToPlayer() : nullptr;
        if (!RangerOf(player) || !application || !application->GetBase())
            return;

        uint32 spellId = application->GetBase()->GetId();
        if (spellId == SPELL_RANGER_ELUDE)
        {
            player->RemoveAurasDueToSpell(SPELL_RANGER_ELUDE_EFFECTS);
            player->RemoveAurasDueToSpell(SPELL_RANGER_ELUDE_SPEED_PENALTY);
            ApplyRangerEludeExitEffects(player, mode == AURA_REMOVE_BY_DEATH);
        }
        if (spellId == SPELL_RANGER_ELUSIVE_CHARACTER)
            player->RemoveAurasDueToSpell(SPELL_RANGER_ELUSIVE_CHARACTER_EFFECTS);
        if (spellId == SPELL_RANGER_FOREST_DWELLER)
            RefreshRangerEludePenalty(player);
    }
};

class cw_coa_ranger_player : public PlayerScript
{
public:
    cw_coa_ranger_player() : PlayerScript("cw_coa_ranger_player",
        { PLAYERHOOK_ON_LOGIN, PLAYERHOOK_ON_LOGOUT, PLAYERHOOK_ON_UPDATE, PLAYERHOOK_ON_LEVEL_CHANGED,
          PLAYERHOOK_ON_AFTER_UPDATE_MAX_POWER, PLAYERHOOK_ON_PLAYER_HAS_ACTIVE_POWER_TYPE }) { }

    bool OnPlayerHasActivePowerType(Player const* player, Powers power) override
    {
        return power == POWER_FOCUS && RangerOf(player);
    }

    void OnPlayerAfterUpdateMaxPower(Player* player, Powers& power, float& value) override
    {
        if (power == POWER_FOCUS && RangerOf(player))
            value += RANGER_FOCUS_MAXIMUM * player->GetPctModifierValue(UNIT_MOD_FOCUS, BASE_PCT) *
                player->GetPctModifierValue(UNIT_MOD_FOCUS, TOTAL_PCT);
    }

    void OnPlayerLogin(Player* player) override
    {
        if (!RangerOf(player))
            return;
        SynchronizeRanger(player);
        player->UpdateMaxPower(POWER_FOCUS);
        player->SetPower(POWER_FOCUS, player->GetMaxPower(POWER_FOCUS));
        player->CustomData.GetDefault<RangerResourceState>(RANGER_RESOURCE_STATE);
    }

    void OnPlayerLevelChanged(Player* player, uint8 /*oldLevel*/) override
    {
        if (RangerOf(player))
            player->SetPower(POWER_FOCUS, player->GetMaxPower(POWER_FOCUS));
    }

    void OnPlayerLogout(Player* player) override
    {
        player->CustomData.Erase(RANGER_RESOURCE_STATE);
    }

    void OnPlayerUpdate(Player* player, uint32 diff) override
    {
        if (!RangerOf(player))
        {
            if (player->CustomData.Erase(RANGER_RESOURCE_STATE))
                player->UpdateMaxPower(POWER_FOCUS);
            return;
        }

        RangerResourceState* state = player->CustomData.Get<RangerResourceState>(RANGER_RESOURCE_STATE);
        if (!state)
        {
            state = player->CustomData.GetDefault<RangerResourceState>(RANGER_RESOURCE_STATE);
            player->UpdateMaxPower(POWER_FOCUS);
            player->SetPower(POWER_FOCUS, player->GetMaxPower(POWER_FOCUS));
        }
        if (!player->IsAlive() ||
            player->HasAuraTypeWithMiscvalue(SPELL_AURA_PREVENT_REGENERATE_POWER, POWER_FOCUS + 1))
            return;
        if (player->GetCommandStatus(CHEAT_POWER))
        {
            player->SetPower(POWER_FOCUS, player->GetMaxPower(POWER_FOCUS));
            state->FocusFraction = 0;
            return;
        }

        if (player->GetPower(POWER_FOCUS) >= player->GetMaxPower(POWER_FOCUS))
        {
            state->FocusFraction = 0;
            return;
        }

        // CoA's measured Focus rate and the same aura modifiers as Player::Regenerate.
        float gain = RANGER_FOCUS_PER_SECOND * sWorld->getRate(RATE_POWER_FOCUS);
        gain *= player->GetTotalAuraMultiplierByMiscValue(SPELL_AURA_MOD_POWER_REGEN_PERCENT, POWER_FOCUS);
        gain += float(player->GetTotalAuraModifierByMiscValue(SPELL_AURA_MOD_POWER_REGEN, POWER_FOCUS)) / 5.0f;
        gain = gain * diff / IN_MILLISECONDS + state->FocusFraction;
        int32 whole = int32(gain);
        state->FocusFraction = gain - whole;
        if (whole)
            player->ModifyPower(POWER_FOCUS, whole);
    }
};
}

void ApplyCoARangerContracts(SpellInfo* info)
{
    if (!sClasslessMgr->cfg.coaEnable || !info || info->SpellFamilyName != RANGER_FAMILY)
        return;

    ApplyRangerFixedDurationContract(info);
#ifdef ESTERIA_COA_CONDITIONAL_COMBAT
    ApplyRangerConditionalDamageContracts(info);
    ApplyRangerSerrationsContract(info);
#endif
    ApplyRangerUnderhandedContracts(info);
    ApplyRangerInstinctualCombatantContract(info);
    // Rusty Shiv: the CoA client tables this was imported from already carry the final MiscValueB (20) that
    // CoA's contract writes, while the contract expects the earlier 10 and the stacking rule its script needs.
    // Put the row back to what the contract expects so it runs as CoA wrote it.
    if (info->Id == 561315 && info->Effects[EFFECT_1].IsAura(SPELL_AURA_SCHOOL_ABSORB) &&
        info->Effects[EFFECT_1].MiscValueB == 20)
    {
        info->Effects[EFFECT_1].MiscValueB = 10;
        info->AttributesEx3 |= SPELL_ATTR3_DOT_STACKING_RULE;
    }
    ApplyAscensionRangerDamageContracts(info);
    ApplyAdditionalTargetContracts(info);
    ApplyRangerOffensiveSpellContracts(info);
    ApplyRangerForestDwellerContract(info);
    ApplyAscensionRangerTalentContracts(info);
}

void AddCoARangerPackage()
{
    new cw_coa_ranger_spells();
    new cw_coa_ranger_auras();
    new cw_coa_ranger_player();
    AddAscensionRangerDamageScripts();
    AddAscensionRangerScalingScripts();
    AddAscensionRangerAssaultScripts();
    AddSC_AscensionRangerSecondary();
    AddSC_AscensionRangerDirtyFighter();
    AddSC_AscensionRangerDeadeye();
    AddSC_AscensionRangerHookshot();
    AddSC_AscensionRangerOutmaneuver();
    AddSC_AscensionRangerToTheSkies();
    AddSC_AscensionRangerTalents();
    AddSC_AscensionRangerFlowers();
    AddSC_AscensionRangerPetalkeeper();
    AddSC_AscensionRangerFalconstrike();
    AddSC_AscensionRangerArchery();
}
