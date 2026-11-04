/*
 * mod-classless-wildcard
 * Copyright (C) 2026 Dustin Hendrickson
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * General Public License for more details.
 */

// Where the ported CoA class packages meet the engine. In CoA this wiring is
// AscensionCompat.cpp and AscensionClassMechanics.cpp, which reach every class
// at once; here each package is added as it is ported, in CoA's own order.

#include "AscensionBarbarian.h"
#include "AscensionConditionalCombat.h"
#include "AscensionBarbarianScaling.h"
#include "AscensionClassMechanics12To17.h"
#include "AscensionClassMechanics19To25.h"
#include "AscensionClassMechanics26To32.h"
#include "AscensionNecromancer.h"
#include "AscensionPyromancer.h"
#include "AscensionStarcaller.h"
#include "AscensionStormbringer.h"
#include "AscensionSunCleric.h"
#include "AscensionTemplar.h"
#include "AscensionFelsworn.h"
#include "AscensionReaperDeathwind.h"
#include "AscensionReaperPainmail.h"
#include "AscensionReaperScytheRush.h"
#include "AscensionReaperSoulStrike.h"
#include "AscensionReaperTalents.h"
#include "AscensionRunemasterBrand.h"
#include "AscensionRunemasterDamageModifiers.h"
#include "AscensionRunemasterEchoes.h"
#include "AscensionRunemasterGlyphs.h"
#include "AscensionRunemasterScaling.h"
#include "AscensionRunemasterTalents.h"
#include "AscensionRunemasterZenith.h"
#include "AscensionTinker.h"
#include "AscensionVenomancer.h"
#include "AscensionWitchDoctorCompletion.h"
#include "AscensionXoroth.h"
#include "AscensionBloodmageHemoglobe.h"
#include "AscensionSunClericRadiance.h"
#include "AscensionHealingStatSelectors.h"
#include "AscensionPrimalistEarthshaping.h"
#include "AscensionTemplarLibrams.h"
#include "AscensionTinkerCombustion.h"
#include "AscensionTinkerOverload.h"
#include "AscensionVenomancerCatalyst.h"
#include "ClasslessMgr.h"
#include "CoAPort.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "Spell.h"
#include "SpellAuras.h"
#include "SpellAuraEffects.h"
#include "SpellInfo.h"
#include "SpellMgr.h"

void AddAscensionTinkerOverloadScripts();
void AddAscensionBarbarianCompletionScripts();
void AddAscensionBarbarianEventScripts();
void AddAscensionBarbarianAbilityScripts();
void AddAscensionWitchDoctorCompletionScripts();
void AddAscensionNecromancerScripts();
void AddAscensionNecromancerSummonScripts();
void AddAscensionNecromancerEventScripts();
void AddAscensionNecromancerAbilityScripts();
void AddAscensionNecromancerAuraScripts();
void AddSC_AscensionXoroth();
void AddSC_AscensionStarcaller();
void AddSC_AscensionPyromancer();
void AddSC_AscensionPyromancerEvents();
void AddSC_AscensionPyromancerAbilities();
void AddSC_AscensionPyromancerAuras();
void AddSC_AscensionPyromancerSummons();
void AddSC_AscensionVenomancer();
void AddSC_AscensionVenomancerEvents();
void AddSC_AscensionVenomancerAbilities();
void AddSC_AscensionVenomancerAuras();
void AddSC_AscensionVenomancerSummons();
void AddSC_AscensionTinker();
void AddSC_AscensionTinkerEvents();
void AddSC_AscensionTinkerAbilities();
void AddSC_AscensionTinkerAuras();
void AddSC_AscensionTinkerSummons();
void AddSC_AscensionSunCleric();
void AddSC_AscensionSunClericEvents();
void AddSC_AscensionSunClericAbilities();
void AddSC_AscensionSunClericAuras();
void AddSC_AscensionSunClericSummons();
void AddSC_AscensionStarcallerEvents();
void AddSC_AscensionStarcallerAbilities();
void AddSC_AscensionStarcallerAuras();
void AddSC_AscensionStarcallerMechanics();
void AddSC_AscensionXorothEvents();
void AddSC_AscensionXorothAbilities();
void AddSC_AscensionXorothAuras();
void AddSC_AscensionXorothSummons();
void AddSC_AscensionTemplar();
void AddSC_AscensionFelsworn();
void AddSC_AscensionFelswornAbilities();
void AddSC_AscensionFelswornAuras();
void AddSC_AscensionFelswornContracts();
void AddSC_AscensionFelswornEvents();
void AddSC_AscensionFelswornSummons();
void AddSC_AscensionChronomancerMovement();
void AddSC_AscensionChronomancerRenewal();
void AddSC_AscensionChronomancerRipple();
void AddSC_AscensionChronomancerSecondary();
void AddSC_AscensionChronomancerTalents();
void AddSC_AscensionChronomancerTime();
void AddSC_AscensionReaperAnimaAmbusher();
void AddSC_AscensionReaperBloodBinding();
void AddSC_AscensionReaperDirge();
void AddSC_AscensionReaperGhostClaw();
void AddSC_AscensionReaperMindScreech();
void AddSC_AscensionReaperRedshade();
void AddSC_AscensionReaperReflexes();
void AddSC_AscensionReaperReliquary();
void AddSC_AscensionReaperRuin();
void AddSC_AscensionReaperSecondary();
void AddSC_AscensionReaperSpellContracts();
void AddSC_AscensionReaperTalentProcs();
void AddSC_AscensionReaperTormentedSouls();
void AddSC_AscensionRunemasterBurnedEtching();
void AddSC_AscensionRunemasterDisappearance();
void AddSC_AscensionRunemasterElementalTalents();
void AddSC_AscensionRunemasterHurricane();
void AddSC_AscensionRunemasterRiftClones();
void AddSC_AscensionRunemasterRunicTalents();
void AddSC_AscensionRunemasterSecondary();
void AddSC_AscensionRunemasterTalentEffects();
void AddSC_AscensionRunemasterTalentMechanics();
void AddSC_AscensionRunemasterTalentProcs();
void AddSC_AscensionRunemasterTravel();
void ApplyAscensionChronomancerTalentContracts(SpellInfo* info);
void AddSC_AscensionTemplarAuras();
void AddSC_AscensionTemplarEvents();
void AddSC_AscensionTemplarAbilities();
void AddSC_AscensionTemplarSummons();
void AddSC_AscensionTemplarTemporaryLibramProcs();
void AddAscensionTinkerAugmentationScripts();
void AddAscensionTinkerAugmentationTalentScripts();
void AddSC_AscensionPrimalistEarthshaping();
void AddSC_AscensionBloodmageBloodShards();
void AddSC_AscensionVenomancerCatalyst();
void AddAscensionTinkerRockadierScripts();
void AddSC_AscensionStormbringerLightning();
void AddSC_AscensionStormbringerMysticThunder();
void AddSC_AscensionStormbringerWindGate();
void AddSC_AscensionStormbringerDrown();
void AddSC_AscensionStormbringerPet();
void AddSC_AscensionStormbringerIonicAura();
void AddSC_AscensionBloodmageSecondary();
void AddSC_AscensionBloodmageHemostasis();
void AddSC_AscensionBloodmageTalents();
void AddSC_AscensionBloodmageVitality();
void AddSC_AscensionBloodmageProcs();
void AddAscensionNecromancerContractScripts();
void AddSC_AscensionStarcallerContracts();
void AddSC_AscensionPyromancerContracts();
void AddSC_AscensionVenomancerContracts();
void AddSC_AscensionTinkerContracts();
void AddSC_AscensionSunClericContracts();
void AddSC_AscensionXorothContracts();
void AddSC_AscensionTemplarContracts();
void AddAscensionVenomancerVenomScripts();
void AddAscensionVenomancerVenomProcScripts();
void AddAscensionVenomancerVenomTalentScripts();
void AddAscensionVenomancerVenomPayloadScripts();
void AddAscensionWitchDoctorEventScripts();
void AddAscensionWitchDoctorAbilityScripts();
void AddAscensionWitchDoctorBrewingScripts();
void AddAscensionWitchDoctorAuraScripts();
void AddAscensionWitchDoctorSummonScripts();
void AddSC_AscensionSunClericValkyrie();
void AddSC_AscensionSunClericDevotion();
void AddSC_AscensionSunClericRadiance();
void AddSC_AscensionTemplarTithe();
void AddAscensionTinkerHackingScripts();
void AddSC_AscensionStormbringerTalents();
void AddSC_AscensionResourceTalents();
void AddSC_AscensionThreatRedirect();
void AddSC_AscensionStormbringerThunderOrb();
void AddSC_AscensionStormbringerZephyr();
void AddSC_AscensionStormbringerSphere();
void AddSC_AscensionStormbringerStormflow();
void AddSC_AscensionStormbringerFog();
void AddSC_AscensionStormbringerSurge();
void AddSC_AscensionBloodmageDarkwing();
void AddSC_AscensionVenomancerSerpentFang();
void AddSC_AscensionVenomancerWasp();
void AddSC_AscensionSunClericBattleCleric();
void AddAscensionTinkerCombatSymbiosisScripts();
void AddCoAGuardianPackage();
void ApplyCoAGuardianContracts(SpellInfo* spellInfo);
void ApplyCoATinkerScrapContracts(SpellInfo* spellInfo);
void ApplyCoAAdditionalTargetContracts(SpellInfo* spellInfo);
void AddCoARangerPackage();
void ApplyCoARangerContracts(SpellInfo* spellInfo);
void AddCoACultistPackage();
void ApplyCoACultistContracts(SpellInfo* spellInfo);
void AddCoAPrimalistPackage();
void ApplyCoAPrimalistContracts(SpellInfo* spellInfo);
void AddCoASpellAffectScripts();
void AddCoASpellAffectClientScripts();
void AddCoAEmpowermentScripts();
void AddCoAReplacementScripts();
void AddCoAResourceScripts();
void AddCoAAuraAmountScripts();
void AddSC_AscensionRaidDamageAuras();
void AddSC_AscensionSummonAvoidance();
void AddCoARunicPowerScripts();
void ApplyCoASpellChargeMetadata(SpellInfo* spellInfo);
void AddCoASpellChargeScripts();
void AddCoAWitchHunterPackage();
void ApplyCoAWitchHunterContracts(SpellInfo* spellInfo);

bool HasCoAKit(Player const* player, uint8 coaClass)
{
    return player && coaClass < 32
        && (sClasslessMgr->OwnedCoAClassMask(const_cast<Player*>(player)) & (1u << coaClass));
}

bool HasCoAKit(Unit const* unit, uint8 coaClass)
{
    return unit && unit->IsPlayer() && HasCoAKit(unit->ToPlayer(), coaClass);
}

namespace
{
    // A Hero owns talents rather than a specialisation, so the Runemaster's Runic specialisation (the one
    // that has Echoes) is taken to be active; the sync itself checks the kit and the spells owned.
    constexpr uint32 RUNEMASTER_RUNIC_SPECIALIZATION = 61;
    bool IsRunemasterEchoesSpell(uint32 spellId) { return spellId == 712325 || spellId == 712389 || spellId == 521211; }

    // the imported spells are loaded only when the catalog is switched on
    bool Enabled() { return sClasslessMgr->cfg.coaEnable; }
}

class cw_coa_spell_data : public GlobalScript
{
public:
    cw_coa_spell_data() : GlobalScript("cw_coa_spell_data", { GLOBALHOOK_ON_LOAD_SPELL_CUSTOM_ATTR }) { }

    // CoA's load-time corrections (ApplyAscensionClassMechanics); each one
    // names its own spell ids, so it changes nothing else
    void OnLoadSpellCustomAttr(SpellInfo* spellInfo) override
    {
        // ApplyAscensionClassMechanics, then AscensionCompat's own, in CoA's order
        ApplyCoAGuardianContracts(spellInfo);
        ApplyCoATinkerScrapContracts(spellInfo);
        ApplyCoAAdditionalTargetContracts(spellInfo);
        ApplyAscensionClassMechanics19To25(spellInfo);
        ApplyCoARangerContracts(spellInfo);
        ApplyAscensionBarbarianSpellChanges(spellInfo);
        ApplyCoAWitchHunterContracts(spellInfo);
        AscensionWitchDoctor::ApplyContracts(spellInfo);
        AscensionNecromancer::ApplyContracts(spellInfo);
        AscensionTemplar::ApplyContracts(spellInfo);
        AscensionFelsworn::ApplyContracts(spellInfo);
        ApplyAscensionChronomancerTalentContracts(spellInfo);
        ApplyAscensionRunemasterGlyphContracts(spellInfo);
        ApplyAscensionRunemasterBrandContracts(spellInfo);
        ApplyAscensionRunemasterScalingContracts(spellInfo);
        ApplyAscensionRunemasterDamageModifierContracts(spellInfo);
        ApplyAscensionRunemasterZenithContracts(spellInfo);
        ApplyAscensionRunemasterTalentContracts(spellInfo);
        ApplyAscensionManuscriptionContracts(spellInfo);
        ApplyAscensionRunemasterTravelContracts(spellInfo);
        ApplyAscensionReaperDeathwindContracts(spellInfo);
        ApplyAscensionReaperScytheRushContracts(spellInfo);
        AscensionXoroth::ApplyContracts(spellInfo);
        AscensionStarcaller::ApplyContracts(spellInfo);
        AscensionPyromancer::ApplyContracts(spellInfo);
        ApplyCoACultistContracts(spellInfo);
        AscensionVenomancer::ApplyContracts(spellInfo);
        AscensionTinker::ApplyContracts(spellInfo);
        AscensionSunCleric::ApplyContracts(spellInfo);
        AscensionStormbringer::ApplyContracts(spellInfo);
        ApplyAscensionTinkerCombustionContracts(spellInfo);
        ApplyAscensionTinkerOverloadMetadata(spellInfo);
        ApplyAscensionTemplarLibramContracts(spellInfo);
        ApplyAscensionHealingStatSelectorContracts(spellInfo);
        ApplyAscensionSunClericRadianceContracts(spellInfo);
        ApplyAscensionPrimalistEarthshapingContracts(spellInfo);
        ApplyAscensionVenomancerCatalystContract(spellInfo);
        ApplyCoAPrimalistContracts(spellInfo);
        ApplyAscensionConditionalCombatContracts(spellInfo);
        ApplyCoASpellChargeMetadata(spellInfo);
        AscensionTinker::ApplyBeaconChargePool(spellInfo);
        AscensionTinker::ApplyReplenishmentFieldAura(spellInfo);
        ApplyAscensionBloodmageHemoglobeContract(spellInfo);
    }
};

class cw_coa_spells : public AllSpellScript
{
public:
    cw_coa_spells() : AllSpellScript("cw_coa_spells", {
        ALLSPELLHOOK_ON_CAST,
        ALLSPELLHOOK_ON_BEFORE_EFFECTS,
        ALLSPELLHOOK_ON_CALCULATED_TARGET,
        ALLSPELLHOOK_ON_HIT_RESULT,
        ALLSPELLHOOK_ON_SUCCESSFUL_INTERRUPT,
        ALLSPELLHOOK_CAN_PREPARE
    }) { }

    [[nodiscard]] bool CanPrepare(Spell* spell, SpellCastTargets const* /*targets*/,
                                  AuraEffect const* /*triggeredByAura*/) override
    {
        return !Enabled() || CanPrepareAscensionClassMechanics19To25(spell);
    }

    void OnSpellSuccessfulInterrupt(Spell* spell, Unit* /*target*/) override
    {
        if (Enabled() && spell)
            if (Player* player = spell->GetCaster()->ToPlayer())
                HandleAscensionClassMechanics26To32SuccessfulInterrupt(spell, player);
    }

    void OnSpellCast(Spell* spell, Unit* /*caster*/, SpellInfo const* /*spellInfo*/, bool /*skipCheck*/) override
    {
        if (Enabled())
            HandleAscensionBarbarianCast(spell);
    }

    void OnSpellBeforeEffects(Spell* spell, Unit* /*caster*/, SpellInfo const* /*spellInfo*/) override
    {
        if (Enabled())
            PrepareAscensionBarbarianScaling(spell);
    }

    void OnSpellCalculatedTarget(Spell* spell, Unit* target, TargetInfo& targetInfo) override
    {
        if (!Enabled() || !spell || !target)
            return;
        if (Player* player = spell->GetCaster()->ToPlayer())
            HandleAscensionClassMechanics12To17CalculatedTarget(spell, player, target, targetInfo);
    }

    void OnSpellHitResult(Spell* spell, Unit* target, uint8 missInfo, uint32 damage, uint32 /*healing*/,
                          bool critical) override
    {
        if (!Enabled() || !spell || !target || missInfo != SPELL_MISS_NONE)
            return;
        if (Player* player = spell->GetCaster()->ToPlayer())
        {
            HandleAscensionClassMechanics12To17Hit(spell, player, target, missInfo, damage, critical);
            HandleAscensionClassMechanics19To25Hit(spell, player, target, missInfo, damage);
            HandleAscensionClassMechanics26To32Hit(spell, player, target, missInfo, damage, critical);
            HandleAscensionReaperSoulStrikeHit(spell, player, target, missInfo);
            HandleAscensionReaperPainmailHit(spell, player, target, missInfo, damage);
        }
    }
};

class cw_coa_auras : public UnitScript
{
public:
    cw_coa_auras() : UnitScript("cw_coa_auras", true, { UNITHOOK_ON_AURA_APPLY, UNITHOOK_ON_AURA_REMOVE }) { }

    void OnAuraApply(Unit* unit, Aura* aura) override
    {
        if (Enabled() && unit && aura)
            if (Player* player = unit->ToPlayer())
                HandleAscensionBarbarianAura(player, aura->GetId(), true);
    }

    void OnAuraRemove(Unit* unit, AuraApplication* aurApp, AuraRemoveMode /*mode*/) override
    {
        if (Enabled() && unit && aurApp && aurApp->GetBase())
            if (Player* player = unit->ToPlayer())
                HandleAscensionBarbarianAura(player, aurApp->GetBase()->GetId(), false);
    }
};

class cw_coa_player : public PlayerScript
{
public:
    cw_coa_player() : PlayerScript("cw_coa_player", {
        PLAYERHOOK_ON_AFTER_UPDATE_ATTACK_POWER_AND_DAMAGE,
        PLAYERHOOK_ON_LEARN_SPELL,
        PLAYERHOOK_ON_FORGOT_SPELL
    }) { }

    // CoA's taught abilities (AscensionTaughtAbilityData.h): a spell that
    // comes with another and goes with it. CoA re-synchronised them from its
    // class tables; here they simply follow the parent spell.
    void OnPlayerLearnSpell(Player* player, uint32 spellId) override
    {
        if (Enabled() && IsRunemasterEchoesSpell(spellId))
            SynchronizeAscensionRunemasterEchoes(player, RUNEMASTER_RUNIC_SPECIALIZATION);
        if (Enabled())
            if (std::vector<uint32> const* taught = sClasslessMgr->CoATaught(spellId))
                for (uint32 child : *taught)
                    if (!player->HasSpell(child))
                        player->learnSpell(child);
    }

    void OnPlayerForgotSpell(Player* player, uint32 spellId) override
    {
        if (Enabled() && IsRunemasterEchoesSpell(spellId))
            SynchronizeAscensionRunemasterEchoes(player, RUNEMASTER_RUNIC_SPECIALIZATION);
        if (Enabled())
            if (std::vector<uint32> const* taught = sClasslessMgr->CoATaught(spellId))
                for (uint32 child : *taught)
                    if (player->HasSpell(child))
                        player->removeSpell(child, SPEC_MASK_ALL, false);
    }

    void OnPlayerAfterUpdateAttackPowerAndDamage(Player* player, float& /*level*/, float& /*baseAttPower*/,
                                                 float& attPowerMod, float& /*attPowerMultiplier*/,
                                                 bool ranged) override
    {
        if (Enabled())
            HandleAscensionBarbarianAttackPower(player, attPowerMod, ranged);
    }
};

class cw_coa_casting : public UnitScript
{
public:
    cw_coa_casting() : UnitScript("cw_coa_casting", true, {
        UNITHOOK_CAN_CAST_SPELL_WHILE_MOVING,
        UNITHOOK_CAN_CAST_DURING_CHANNEL,
        UNITHOOK_CAN_USE_SCRIPTED_PET_AI,
        UNITHOOK_MODIFY_RUN_SPEED,
        UNITHOOK_MODIFY_RUN_SPEED_RATE
    }) { }

    // CoA's Unit::CanCastSpellWhileMoving, for the kits ported so far; "is this kit's class" is
    // "owns the kit" here
    [[nodiscard]] bool CanCastSpellWhileMoving(Unit const* unit, SpellInfo const* info) override
    {
        if (!Enabled() || !unit || !info)
            return false;

        if (HasCoAKit(unit, CLASS_STARCALLER) &&
            (info->Id == 801990 || info->Id == 802682 || (unit->HasAura(704772) && !info->IsPositive())))
            return true;

        if (HasCoAKit(unit, CLASS_WITCH_DOCTOR) && info->SpellFamilyName == 19 &&
            ((info->SpellFamilyFlags[1] & 4) || (info->SpellFamilyFlags[0] & 33554432)))
            return true;

        if (HasCoAKit(unit, CLASS_TINKER) && info->SpellFamilyName == 34)
        {
            uint32 const first = sSpellMgr->GetFirstSpellInChain(info->Id);
            return info->Id == 500213 || info->Id == 504594 || first == 504527 || first == 801387;
        }

        return false;
    }

    // CoA's Unit::CanCastDuringChannel, for the kits ported so far
    [[nodiscard]] bool CanCastDuringChannel(Unit const* unit, SpellInfo const* info) override
    {
        if (!Enabled() || !unit || !info)
            return false;

        if (HasCoAKit(unit, CLASS_TINKER) && info->SpellFamilyName == 34 && info->Id == 801798)
            return true;
        if (HasCoAKit(unit, CLASS_STARCALLER) && info->Id == 800386)
            return true;
        if (HasCoAKit(unit, CLASS_NECROMANCER) && info->Id == 500991)
            return true;

        Spell const* channel = unit->GetCurrentSpell(CURRENT_CHANNELED_SPELL);
        if (!channel || channel->getState() == SPELL_STATE_FINISHED || !channel->IsChannelActive())
            return false;
        SpellInfo const* channeled = channel->GetSpellInfo();

        if (HasCoAKit(unit, CLASS_STORMBRINGER) && info->SpellFamilyName == 22 &&
            channeled->SpellFamilyName == 22 && (channeled->SpellFamilyFlags[1] & 65536) &&
            ((info->SpellFamilyFlags[0] & 2048) || (info->SpellFamilyFlags[1] & 128) ||
             ((info->SpellFamilyFlags[0] & 33554432) && (info->SpellFamilyFlags[2] & 32) && unit->HasAura(578300))))
            return true;

        return HasCoAKit(unit, CLASS_WITCH_DOCTOR) && info->SpellFamilyName == 19 &&
            ((info->SpellFamilyFlags[1] & 2048) || (info->SpellFamilyFlags[2] & 536870913)) &&
            channeled->SpellFamilyName == 19 && (channeled->SpellFamilyFlags[1] & 4194304);
    }

    void ModifyRunSpeed(Unit const* unit, int32& modifier) override
    {
        if (!Enabled() || !unit)
            return;
        if (HasCoAKit(unit, CLASS_WITCH_HUNTER) && unit->HasAura(504790))
            modifier = std::max(modifier, 20);
    }

    void ModifyRunSpeedRate(Unit const* unit, float& speed) override
    {
        if (Enabled() && HasCoAKit(unit, CLASS_GUARDIAN) && unit->HasAura(803130))
            if (AuraEffect const* floor = unit->GetAuraEffect(300542, EFFECT_0))
                speed = std::max(speed, float(floor->GetAmount()) / 100.0f);
    }

    // CoA's CreatureAISelector::SelectAI: a permanent companion of a kit runs its scripted AI (which extends
    // PetAI): the Witch Hunter's Shadowhound, the Tinker's pets
    [[nodiscard]] bool CanUseScriptedPetAI(Creature const* pet) override
    {
        if (!Enabled() || !pet)
            return false;

        Unit* owner = pet->GetOwner();
        if (!owner)
            return false;

        uint32 const entry = pet->GetEntry();
        if (entry == 50124)
            return HasCoAKit(owner, CLASS_WITCH_HUNTER);
        if (entry == 50048 || entry == 500481 || entry == 60671 || entry == 60070 || entry == 60672)
            return HasCoAKit(owner, CLASS_TINKER);
        return false;
    }
};

void AddClasslessCoAClassScripts()
{
    AddCoASpellAffectScripts();
    AddCoASpellAffectClientScripts();
    AddCoASpellChargeScripts();
    AddCoAEmpowermentScripts();
    AddCoAReplacementScripts();
    AddCoAResourceScripts();
    AddCoAAuraAmountScripts();
    AddSC_AscensionRaidDamageAuras();
    AddSC_AscensionSummonAvoidance();
    AddCoARunicPowerScripts();
    new cw_coa_spell_data();
    new cw_coa_spells();
    new cw_coa_auras();
    new cw_coa_casting();
    new cw_coa_player();

    // the packages, in CoAScriptLoader.cpp's order
    AddAscensionTinkerOverloadScripts();
    AddAscensionBarbarianCompletionScripts();
    AddAscensionBarbarianEventScripts();
    AddAscensionBarbarianAbilityScripts();
    AddCoAGuardianPackage();
    AddCoARangerPackage();
    AddCoAWitchHunterPackage();
    AddAscensionWitchDoctorCompletionScripts();
    AddAscensionNecromancerScripts();
    AddAscensionNecromancerSummonScripts();
    AddAscensionNecromancerEventScripts();
    AddAscensionNecromancerAbilityScripts();
    AddAscensionNecromancerAuraScripts();
    AddSC_AscensionXoroth();
    AddSC_AscensionStarcaller();
    AddSC_AscensionPyromancer();
    AddSC_AscensionPyromancerEvents();
    AddSC_AscensionPyromancerAbilities();
    AddSC_AscensionPyromancerAuras();
    AddSC_AscensionPyromancerSummons();
    AddSC_AscensionVenomancer();
    AddSC_AscensionVenomancerEvents();
    AddSC_AscensionVenomancerAbilities();
    AddSC_AscensionVenomancerAuras();
    AddSC_AscensionVenomancerSummons();
    AddSC_AscensionTinker();
    AddSC_AscensionTinkerEvents();
    AddSC_AscensionTinkerAbilities();
    AddSC_AscensionTinkerAuras();
    AddSC_AscensionTinkerSummons();
    AddSC_AscensionSunCleric();
    AddSC_AscensionSunClericEvents();
    AddSC_AscensionSunClericAbilities();
    AddSC_AscensionSunClericAuras();
    AddSC_AscensionSunClericSummons();
    AddSC_AscensionStarcallerEvents();
    AddSC_AscensionStarcallerAbilities();
    AddSC_AscensionStarcallerAuras();
    AddSC_AscensionStarcallerMechanics();
    AddSC_AscensionXorothEvents();
    AddSC_AscensionXorothAbilities();
    AddSC_AscensionXorothAuras();
    AddSC_AscensionXorothSummons();
    AddSC_AscensionTemplar();
    AddSC_AscensionFelsworn();
    AddSC_AscensionFelswornAbilities();
    AddSC_AscensionFelswornAuras();
    AddSC_AscensionFelswornContracts();
    AddSC_AscensionFelswornEvents();
    AddSC_AscensionFelswornSummons();
    AddSC_AscensionChronomancerMovement();
    AddSC_AscensionChronomancerRenewal();
    AddSC_AscensionChronomancerRipple();
    AddSC_AscensionChronomancerSecondary();
    AddSC_AscensionChronomancerTalents();
    AddSC_AscensionChronomancerTime();
    AddSC_AscensionReaperAnimaAmbusher();
    AddSC_AscensionReaperBloodBinding();
    AddSC_AscensionReaperDirge();
    AddSC_AscensionReaperGhostClaw();
    AddSC_AscensionReaperMindScreech();
    AddSC_AscensionReaperRedshade();
    AddSC_AscensionReaperReflexes();
    AddSC_AscensionReaperReliquary();
    AddSC_AscensionReaperRuin();
    AddSC_AscensionReaperSecondary();
    AddSC_AscensionReaperSpellContracts();
    AddSC_AscensionReaperTalentProcs();
    AddSC_AscensionReaperTalents();
    AddSC_AscensionReaperTormentedSouls();
    AddSC_AscensionRunemasterBurnedEtching();
    AddSC_AscensionRunemasterDisappearance();
    AddSC_AscensionRunemasterElementalTalents();
    AddSC_AscensionRunemasterHurricane();
    AddSC_AscensionRunemasterManuscription();
    AddSC_AscensionRunemasterRiftClones();
    AddSC_AscensionRunemasterRunicTalents();
    AddSC_AscensionRunemasterSecondary();
    AddSC_AscensionRunemasterTalentEffects();
    AddSC_AscensionRunemasterTalentMechanics();
    AddSC_AscensionRunemasterTalentProcs();
    AddSC_AscensionRunemasterTalents();
    AddSC_AscensionRunemasterTravel();
    AddAscensionRunemasterBrandScripts();
    AddAscensionRunemasterEchoesScripts();
    AddAscensionRunemasterGlyphScripts();
    AddAscensionRunemasterScalingScripts();
    AddAscensionRunemasterZenithScripts();
    AddSC_AscensionTemplarAuras();
    AddSC_AscensionTemplarEvents();
    AddSC_AscensionTemplarAbilities();
    AddSC_AscensionTemplarSummons();
    AddSC_AscensionTemplarTemporaryLibramProcs();
    AddAscensionNecromancerContractScripts();
    AddSC_AscensionStarcallerContracts();
    AddSC_AscensionPyromancerContracts();
    AddCoACultistPackage();
    AddSC_AscensionVenomancerContracts();
    AddSC_AscensionTinkerContracts();
    AddSC_AscensionSunClericContracts();
    AddSC_AscensionXorothContracts();
    AddSC_AscensionTemplarContracts();
    AddAscensionTinkerAugmentationScripts();
    AddAscensionTinkerAugmentationTalentScripts();
    AddCoAPrimalistPackage();
    AddSC_AscensionPrimalistEarthshaping();
    AddSC_AscensionBloodmageBloodShards();
    AddSC_AscensionVenomancerCatalyst();
    AddAscensionTinkerRockadierScripts();
    AddSC_AscensionStormbringerLightning();
    AddSC_AscensionStormbringerMysticThunder();
    AddSC_AscensionStormbringerWindGate();
    AddSC_AscensionStormbringerDrown();
    AddSC_AscensionStormbringerPet();
    AddSC_AscensionStormbringerIonicAura();
    AddSC_AscensionBloodmageSecondary();
    AddSC_AscensionBloodmageHemostasis();
    AddSC_AscensionBloodmageTalents();
    AddSC_AscensionBloodmageVitality();
    AddSC_AscensionBloodmageProcs();
    AddAscensionVenomancerVenomScripts();
    AddAscensionVenomancerVenomProcScripts();
    AddAscensionVenomancerVenomTalentScripts();
    AddAscensionVenomancerVenomPayloadScripts();
    AddAscensionWitchDoctorEventScripts();
    AddAscensionWitchDoctorAbilityScripts();
    AddAscensionWitchDoctorBrewingScripts();
    AddAscensionWitchDoctorAuraScripts();
    AddAscensionWitchDoctorSummonScripts();
    AddSC_AscensionSunClericValkyrie();
    AddSC_AscensionSunClericDevotion();
    AddSC_AscensionSunClericRadiance();
    AddSC_AscensionTemplarTithe();
    AddAscensionTinkerHackingScripts();
    AddSC_AscensionStormbringerTalents();
    AddSC_AscensionResourceTalents();
    AddSC_AscensionThreatRedirect();
    AddSC_AscensionStormbringerThunderOrb();
    AddSC_AscensionStormbringerZephyr();
    AddSC_AscensionStormbringerSphere();
    AddSC_AscensionStormbringerStormflow();
    AddSC_AscensionStormbringerFog();
    AddSC_AscensionStormbringerSurge();
    AddSC_AscensionBloodmageDarkwing();
    AddSC_AscensionVenomancerSerpentFang();
    AddSC_AscensionVenomancerWasp();
    AddSC_AscensionSunClericBattleCleric();
    AddAscensionTinkerCombatSymbiosisScripts();
}
