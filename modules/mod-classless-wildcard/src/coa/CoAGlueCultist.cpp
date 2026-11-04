/* Copyright (C) 2016+ AzerothCore, GNU AGPL v3. */

// The Cultist slice of AscensionCompat's resource service and ClassMechanics.
#include "AscensionCultist.h"
#include "AscensionCustomResourceData.h"
#include "ClasslessMgr.h"
#include "CoAPort.h"
#include "Player.h"
#include "Random.h"
#include "ScriptMgr.h"
#include "Spell.h"
#include "SpellAuraEffects.h"
#include "SpellAuras.h"
#include <algorithm>
#include <array>

void AddSC_AscensionCultist();
void AddSC_AscensionCultistContracts();
void AddSC_AscensionCultistEvents();
void AddSC_AscensionCultistAbilities();
void AddSC_AscensionCultistAuras();
void AddSC_AscensionCultistSummons();

namespace
{
using AscensionCompatData::ResourceGainEvent;
using AscensionCompatData::ResourceGainRule;

constexpr uint32 CULTIST_SPELL_FAMILY = 31;
constexpr uint32 SPELL_TWILIGHT_SHIELDTOSS_SLOW = 524880;
constexpr uint32 SPELL_HERALDS_REPRIEVE = 560977;
constexpr uint32 SPELL_DEVOUR_MAGIC = 520151;
constexpr uint32 SPELL_DEVOUR_MAGIC_HEAL = 520152;
constexpr uint32 SPELL_CULTIST_INSANITY_FREE_CAST = 801153;
constexpr uint32 SPELL_CULTIST_INSTANT_COST_TALENT = 582307;
constexpr std::array<uint32, 7> TWILIGHT_SHIELDTOSS = {503487, 503488, 524876, 572140, 572141, 572715, 804208};

// Fail when upstream adds a Cultist resource event this slice does not dispatch.
static_assert([]
{
    for (ResourceGainRule const& rule : AscensionCompatData::ResourceGainRules)
        if (rule.ClassId == CLASS_CULTIST &&
            (rule.ResourceSpellId != AscensionCultist::Insanity ||
             rule.Mutation != AscensionCompatData::ResourceMutation::AuraStacks ||
             (rule.Event != ResourceGainEvent::Cast && rule.Event != ResourceGainEvent::EachSuccessfulDamagingHit &&
              rule.Event != ResourceGainEvent::EachCriticalDamagingHit && rule.Event != ResourceGainEvent::Block)))
            return false;
    return true;
}());

Player* Cultist(Unit const* unit)
{
    if (!sClasslessMgr->cfg.coaEnable || !unit || !unit->IsPlayer())
        return nullptr;
    Player* player = const_cast<Player*>(unit->ToPlayer());
    return HasCoAKit(player, CLASS_CULTIST) ? player : nullptr;
}

bool MatchesGain(Player const* player, uint32 spellId, ResourceGainRule const& rule)
{
    return rule.ClassId == CLASS_CULTIST &&
        ((!rule.FirstSpellId && !rule.LastSpellId) ||
         (spellId >= rule.FirstSpellId && spellId <= rule.LastSpellId)) &&
        (!rule.RequiredAuraSpellId || player->HasAura(rule.RequiredAuraSpellId)) &&
        (!rule.ForbiddenAuraSpellId || !player->HasAura(rule.ForbiddenAuraSpellId));
}

void Gain(Player* player, ResourceGainRule const& rule)
{
    if (rule.ChancePercent && (rule.ChancePercent == 100 || roll_chance_i(rule.ChancePercent)))
        AscensionCultist::Resource(player, rule.ResourceSpellId, rule.Amount);
}

void SynchronizeThresholds(Player* player)
{
    for (auto const& rule : AscensionCompatData::ResourceThresholdRules)
        if (rule.ClassId == CLASS_CULTIST)
            AscensionCultist::SetHelper(player, rule.ThresholdSpellId,
                AscensionCultist::Count(player, rule.ResourceSpellId) >= rule.Amount);
}

void RemoveThresholds(Player* player)
{
    for (auto const& rule : AscensionCompatData::ResourceThresholdRules)
        if (rule.ClassId == CLASS_CULTIST)
            player->RemoveAurasDueToSpell(rule.ThresholdSpellId, player->GetGUID());
}

class cw_coa_cultist_resources : public AllSpellScript
{
public:
    cw_coa_cultist_resources() : AllSpellScript("cw_coa_cultist_resources",
        { ALLSPELLHOOK_ON_CAST, ALLSPELLHOOK_ON_HIT_RESULT, ALLSPELLHOOK_ON_SUCCESSFUL_DISPEL }) { }

    void OnSpellCast(Spell* spell, Unit* caster, SpellInfo const* info, bool /*skipCheck*/) override
    {
        Player* player = Cultist(caster);
        if (!player || !spell || spell->IsTriggered() || !info || info->SpellFamilyName != CULTIST_SPELL_FAMILY)
            return;

        for (ResourceGainRule const& rule : AscensionCompatData::ResourceGainRules)
            if (rule.Event == ResourceGainEvent::Cast && MatchesGain(player, info->Id, rule))
                Gain(player, rule);
        SynchronizeThresholds(player);
    }

    void OnSpellHitResult(Spell* spell, Unit* target, uint8 missInfo, uint32 damage, uint32 /*healing*/,
        bool critical) override
    {
        Player* player = spell ? Cultist(spell->GetCaster()) : nullptr;
        SpellInfo const* info = spell ? spell->GetSpellInfo() : nullptr;
        if (!player || !target || missInfo != SPELL_MISS_NONE || !info ||
            info->SpellFamilyName != CULTIST_SPELL_FAMILY)
            return;

        if (std::find(TWILIGHT_SHIELDTOSS.begin(), TWILIGHT_SHIELDTOSS.end(), info->Id) != TWILIGHT_SHIELDTOSS.end())
            player->CastSpell(target, SPELL_TWILIGHT_SHIELDTOSS_SLOW, true);

        if (spell->IsTriggered() || target == player || player->IsFriendlyTo(target))
            return;

        bool const damaging = damage || info->HasEffect(SPELL_EFFECT_SCHOOL_DAMAGE) ||
            info->HasEffect(SPELL_EFFECT_WEAPON_DAMAGE) || info->HasEffect(SPELL_EFFECT_WEAPON_DAMAGE_NOSCHOOL) ||
            info->HasEffect(SPELL_EFFECT_WEAPON_PERCENT_DAMAGE) || info->HasEffect(SPELL_EFFECT_NORMALIZED_WEAPON_DMG);
        if (!damaging)
            return;

        for (ResourceGainRule const& rule : AscensionCompatData::ResourceGainRules)
            if ((rule.Event == ResourceGainEvent::EachSuccessfulDamagingHit ||
                (critical && rule.Event == ResourceGainEvent::EachCriticalDamagingHit)) &&
                MatchesGain(player, info->Id, rule))
                Gain(player, rule);
        SynchronizeThresholds(player);
    }

    void OnSpellSuccessfulDispel(Spell* spell, Unit* /*target*/, SpellEffIndex /*effect*/, uint32 count) override
    {
        Player* player = spell ? Cultist(spell->GetCaster()) : nullptr;
        if (player && count && spell->GetSpellInfo()->SpellFamilyName == CULTIST_SPELL_FAMILY &&
            spell->GetSpellInfo()->Id == SPELL_DEVOUR_MAGIC)
            player->CastSpell(player, SPELL_DEVOUR_MAGIC_HEAL, true);
    }
};

class cw_coa_cultist_player : public PlayerScript
{
public:
    cw_coa_cultist_player() : PlayerScript("cw_coa_cultist_player",
        { PLAYERHOOK_ON_LOGIN, PLAYERHOOK_ON_UPDATE }) { }

    void OnPlayerLogin(Player* player) override
    {
        if (Cultist(player))
            SynchronizeThresholds(player);
    }

    void OnPlayerUpdate(Player* player, uint32 /*diff*/) override
    {
        if (Cultist(player))
            SynchronizeThresholds(player);
        else
            RemoveThresholds(player);
    }
};

class cw_coa_cultist_casting : public UnitScript
{
public:
    cw_coa_cultist_casting() : UnitScript("cw_coa_cultist_casting", true,
        { UNITHOOK_CAN_CAST_DURING_CHANNEL }) { }

    [[nodiscard]] bool CanCastDuringChannel(Unit const* unit, SpellInfo const* info) override
    {
        return Cultist(unit) && info && info->SpellFamilyName == CULTIST_SPELL_FAMILY &&
            (info->Id == 802575 || (unit->HasAura(SPELL_HERALDS_REPRIEVE) &&
             (info->Id == 808036 || info->Id == 808037 || info->Id == 808038)));
    }
};

#ifdef ESTERIA_COA_POWER_COST_HOOK
class cw_coa_cultist_power_cost : public UnitScript
{
public:
    cw_coa_cultist_power_cost() : UnitScript("cw_coa_cultist_power_cost", true,
        { UNITHOOK_MODIFY_SPELL_POWER_COST }) { }

    void ModifySpellPowerCost(Unit const* caster, SpellInfo const* info, int32& cost, float& multiplier) override
    {
        Player* player = Cultist(caster);
        if (!player || !info || info->SpellFamilyName != CULTIST_SPELL_FAMILY || info->PowerType != POWER_MANA)
            return;

        uint32 const insanity = AscensionCultist::Count(player, AscensionCultist::Insanity);
        if (info->Id == SPELL_CULTIST_INSANITY_FREE_CAST && insanity >= 60)
        {
            cost = 0;
            return;
        }
        if (!info->IsChanneled() && (!info->CastTimeEntry || info->CastTimeEntry->CastTime == 0))
            if (AuraEffect const* talent = player->GetAuraEffect(SPELL_CULTIST_INSTANT_COST_TALENT, EFFECT_0))
                multiplier -= insanity * talent->GetAmount() / 100.0f;
    }
};
#endif

#ifdef ESTERIA_COA_BLOCK_HOOK
class cw_coa_cultist_block : public UnitScript
{
public:
    cw_coa_cultist_block() : UnitScript("cw_coa_cultist_block", true, { UNITHOOK_ON_BLOCK }) { }

    void OnBlock(Unit* victim, Unit* /*attacker*/) override
    {
        if (Player* player = Cultist(victim))
            for (ResourceGainRule const& rule : AscensionCompatData::ResourceGainRules)
                if (rule.Event == ResourceGainEvent::Block && MatchesGain(player, 0, rule))
                    Gain(player, rule);
    }
};
#endif
}

void ApplyCoACultistContracts(SpellInfo* info)
{
    AscensionCultist::ApplyContracts(info);
}

void AddCoACultistPackage()
{
    new cw_coa_cultist_resources();
    new cw_coa_cultist_player();
    new cw_coa_cultist_casting();
#ifdef ESTERIA_COA_BLOCK_HOOK
    new cw_coa_cultist_block();
#endif
#ifdef ESTERIA_COA_POWER_COST_HOOK
    new cw_coa_cultist_power_cost();
#endif

    AddSC_AscensionCultist();
    AddSC_AscensionCultistContracts();
    AddSC_AscensionCultistEvents();
    AddSC_AscensionCultistAbilities();
    AddSC_AscensionCultistAuras();
    AddSC_AscensionCultistSummons();
}
