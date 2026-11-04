/* Copyright (C) 2016+ AzerothCore, GNU AGPL v3. */

#include "AscensionCustomResourceData.h"
#include "AscensionPrimalistEarthquake.h"
#include "AscensionPrimalistEarthshaping.h"
#include "AscensionPrimalistSpiritBeast.h"
#include "AscensionPrimalistWeapons.h"
#include "ClasslessMgr.h"
#include "CoAPort.h"
#include "Creature.h"
#include "Pet.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "Spell.h"
#include "SpellAuras.h"
#include "SpellInfo.h"

void AddSC_AscensionPrimalistHeavyEarth();
void AddSC_AscensionPrimalistEarthshaker();
void AddSC_AscensionPrimalistRunningInstinct();
void AddSC_AscensionPrimalistRideWave();
void AddSC_AscensionPrimalistPowerHammer();
void AddSC_AscensionPrimalistEmeraldWill();
void AddSC_AscensionPrimalistTotemicEchoes();
void AddSC_AscensionPrimalistWildCarnage();
void AddSC_AscensionPrimalistPendant();
void AddSC_AscensionPrimalistThorns();
void AddSC_AscensionPrimalistBloodyClaws();
void AddSC_AscensionPrimalistJudgement();
void AddSC_AscensionPrimalistShattering();
void AddSC_AscensionPrimalistPrecision();
void AddSC_AscensionPrimalistVerdantChase();
void AddSC_AscensionPrimalistJourney();
void AddSC_AscensionPrimalistQuakingThane();
void AddSC_AscensionPrimalistTremors();
void AddSC_AscensionPrimalistCataclysm();
void AddSC_AscensionPrimalistFaePresence();
void AddSC_AscensionPrimalistEarthsGuidance();
void AddSC_AscensionPrimalistGroveTender();
void AddSC_AscensionPrimalistBramblepatch();
void AddSC_AscensionPrimalistPrimalStrikes();
void AddSC_AscensionPrimalistLithicLance();
void AddSC_AscensionPrimalistEmpoweredBoons();
void AddSC_AscensionPrimalistEarthmotherWarden();
void AddSC_AscensionPrimalistDruidTraining();
void AddSC_AscensionPrimalistSpiritualFrenzy();
void AddSC_AscensionPrimalistPhysicalCrit();
void AddSC_AscensionPrimalistRipsAndTears();
void AddSC_AscensionPrimalistMountainAvatar();
void AddSC_AscensionPrimalistRylaksBite();
void AddSC_AscensionPrimalistRylaksBlessing();
void AddSC_AscensionPrimalistWildheart();
void AddSC_AscensionPrimalistDreamslip();
void AddSC_AscensionPrimalistDouse();
void AddSC_AscensionPrimalistNeptulonWrath();
void AddSC_AscensionPrimalistSacredGrove();
void AddSC_AscensionPrimalistAncientWar();
void AddSC_AscensionPrimalistEarthmotherRoar();
void AddSC_AscensionPrimalistRushHunt();
void AddSC_AscensionPrimalistCrushingEarth();
void AddSC_AscensionPrimalistSpiritBeast();
void AddSC_AscensionPrimalistWeapons();
void AddSC_AscensionPrimalistTalents();
void AddSC_AscensionPrimalistBones();
void AddSC_AscensionPrimalistBoons();
void AddSC_AscensionPrimalistSeismicResources();
void AddSC_AscensionPrimalistGuidance();
void AddSC_AscensionPrimalistBarrier();
void AddSC_AscensionPrimalistGrove();
void AddSC_AscensionPrimalistMountainFury();
void AddSC_AscensionPrimalistBoulder();
void AddSC_AscensionPrimalistUrsoc();
void AddSC_AscensionPrimalistTorn();
void AddSC_AscensionPrimalistRexxarMight();
void AddSC_AscensionPrimalistMineralization();
void AddSC_AscensionPrimalistLifeSpirit();
void AddSC_AscensionPrimalistTotem();
void AddSC_AscensionPrimalistHeavyHanded();
void AddSC_AscensionPrimalistTremor();
void AddSC_AscensionPrimalistPulverize();
void AddSC_AscensionPrimalistStoneTosser();
void AddSC_AscensionPrimalistVitality();
void AddSC_AscensionPrimalistMagmatism();
void AddSC_AscensionPrimalistGeomancy();
void AddSC_AscensionPrimalistMountain();
void AddSC_AscensionPrimalistSecondary();

namespace
{
enum PrimalistSpells : uint32
{
    SPELL_PRIMALIST_PET_TRAINING = 92148,
    SPELL_EARTHSHAPING = 680441,
    SPELL_STONESHARD_MODIFIER = 680846,
    SPELL_EARTHQUAKE_MODIFIER = 532562,
    SPELL_ERUPTION_MODIFIER = 680450,
    SPELL_PRIMAL_WEAPONS = 537218,
    SPELL_BESTIAL_MIGHT = 801242,
    SPELL_PRIMAL_MIGHT = 704098,
    SPELL_WILDCLAW_BONUS = 563262,
    SPELL_TALONFURY = 806070,
    SPELL_PET_TALONFURY = 806071
};

static_assert([]
{
    for (auto const& rule : AscensionCompatData::ResourceGainRules)
        if (rule.ClassId == CLASS_WILDWALKER &&
            (rule.Event != AscensionCompatData::ResourceGainEvent::Cast ||
             rule.ResourceSpellId != SPELL_EARTHSHAPING ||
             rule.Mutation != AscensionCompatData::ResourceMutation::AuraStacks || rule.Amount <= 0 ||
             rule.ForbiddenAuraSpellId || rule.ChancePercent != 100))
            return false;
    for (auto const& rule : AscensionCompatData::NativePowerGainRules)
        if (rule.ClassId == CLASS_WILDWALKER &&
            ((rule.Event != AscensionCompatData::ResourceGainEvent::EachSuccessfulDamagingHit &&
              rule.Event != AscensionCompatData::ResourceGainEvent::PeriodicDamageTick) ||
             rule.RequiredAuraSpellId || rule.ForbiddenAuraSpellId || rule.AmountSpellId))
            return false;
    return true;
}(), "Primalist resource rules need matching gain handlers");

bool PrimalistEnabled(Player const* player)
{
    return sClasslessMgr->cfg.coaEnable && HasCoAKit(player, CLASS_WILDWALKER);
}

void RemovePrimalistHelpers(Player* player)
{
    if (!player)
        return;
    for (uint32 id : {SPELL_BESTIAL_MIGHT, SPELL_PRIMAL_MIGHT, SPELL_WILDCLAW_BONUS, SPELL_TALONFURY,
        SPELL_EARTHSHAPING, SPELL_STONESHARD_MODIFIER, SPELL_EARTHQUAKE_MODIFIER, SPELL_ERUPTION_MODIFIER})
        player->RemoveAurasDueToSpell(id, player->GetGUID());
    if (Pet* pet = player->GetPet())
        pet->RemoveAurasDueToSpell(SPELL_PET_TALONFURY, player->GetGUID());
}

void ReconcilePrimalistWeapon(Player* player)
{
    if (!player)
        return;
    if (!PrimalistEnabled(player) || !player->IsAlive())
    {
        RemovePrimalistHelpers(player);
        return;
    }
    if (IsAscensionPrimalistWeaponsEligible(player, true))
    {
        ReconcileAscensionPrimalistWeapon(player);
        return;
    }

    // The copied helper requires kit ownership, but the last kit spell can already be gone here.
    for (uint32 id : {SPELL_BESTIAL_MIGHT, SPELL_PRIMAL_MIGHT, SPELL_WILDCLAW_BONUS, SPELL_TALONFURY})
        player->RemoveAurasDueToSpell(id, player->GetGUID());
    if (Pet* pet = player->GetPet())
        pet->RemoveAurasDueToSpell(SPELL_PET_TALONFURY, player->GetGUID());
}

bool IsHostilePrimalistTarget(Player const* player, Unit const* target)
{
    return player && target && PrimalistEnabled(player) && player != target && !player->IsFriendlyTo(target);
}

void GainPrimalistNativePower(Player* player, SpellInfo const* info, AscensionCompatData::ResourceGainEvent event)
{
    for (AscensionCompatData::NativePowerGainRule const& rule : AscensionCompatData::NativePowerGainRules)
        if (rule.ClassId == CLASS_WILDWALKER && rule.Event == event &&
            info->Id >= rule.FirstSpellId && info->Id <= rule.LastSpellId)
            player->ModifyPower(static_cast<Powers>(rule.PowerType), rule.InternalAmount);
}

class cw_coa_primalist_resources : public AllSpellScript
{
public:
    cw_coa_primalist_resources() : AllSpellScript("cw_coa_primalist_resources", {
        ALLSPELLHOOK_ON_CAST,
        ALLSPELLHOOK_ON_HIT_RESULT
    }) { }

    void OnSpellCast(Spell* spell, Unit* /*caster*/, SpellInfo const* info, bool /*skipCheck*/) override
    {
        if (!spell || spell->IsTriggered() || !info)
            return;
        Player* player = spell->GetCaster()->ToPlayer();
        if (!PrimalistEnabled(player))
            return;
        for (AscensionCompatData::ResourceGainRule const& rule : AscensionCompatData::ResourceGainRules)
        {
            if (rule.ClassId != CLASS_WILDWALKER || rule.Event != AscensionCompatData::ResourceGainEvent::Cast ||
                info->Id < rule.FirstSpellId || info->Id > rule.LastSpellId ||
                (rule.RequiredAuraSpellId && !player->HasAura(rule.RequiredAuraSpellId)))
                continue;
            if (HandleAscensionPrimalistEarthshapingGain(player))
                continue;
            if (Aura* aura = player->GetAura(rule.ResourceSpellId))
            {
                int32 const remaining = aura->GetDuration();
                aura->ModStackAmount(rule.Amount);
                aura->SetDuration(remaining);
            }
            else if (Aura* aura = player->AddAura(rule.ResourceSpellId, player); aura && rule.Amount > 1)
                aura->ModStackAmount(rule.Amount - 1);
        }
    }

    void OnSpellHitResult(Spell* spell, Unit* target, uint8 miss, uint32 damage, uint32 /*healing*/,
        bool /*critical*/) override
    {
        if (!spell || spell->IsTriggered() || miss != SPELL_MISS_NONE)
            return;
        Player* player = spell->GetCaster()->ToPlayer();
        SpellInfo const* info = spell->GetSpellInfo();
        if (!IsHostilePrimalistTarget(player, target) ||
            (!damage && !info->HasEffect(SPELL_EFFECT_SCHOOL_DAMAGE)))
            return;
        GainPrimalistNativePower(player, info, AscensionCompatData::ResourceGainEvent::EachSuccessfulDamagingHit);
    }
};

class cw_coa_primalist_periodic_resources : public UnitScript
{
public:
    cw_coa_primalist_periodic_resources() : UnitScript("cw_coa_primalist_periodic_resources", true,
        { UNITHOOK_ON_PERIODIC_DAMAGE_RESULT }) { }

    void OnPeriodicDamageResult(Unit* target, Unit* attacker, uint32 damage, SpellInfo const* info) override
    {
        if (!attacker || !info)
            return;
        Player* player = attacker->ToPlayer();
        if (!IsHostilePrimalistTarget(player, target))
            return;
        Creature const* creature = target->ToCreature();
        if (!damage && !(creature && creature->GetScriptName() == "npc_training_dummy"))
            return;
        GainPrimalistNativePower(player, info, AscensionCompatData::ResourceGainEvent::PeriodicDamageTick);
    }
};

class cw_coa_primalist_player : public PlayerScript
{
public:
    cw_coa_primalist_player() : PlayerScript("cw_coa_primalist_player", {
        PLAYERHOOK_ON_LOGIN,
        PLAYERHOOK_ON_LOGOUT,
        PLAYERHOOK_ON_PLAYER_JUST_DIED,
        PLAYERHOOK_ON_LEARN_SPELL,
        PLAYERHOOK_ON_FORGOT_SPELL,
        PLAYERHOOK_ON_LEVEL_CHANGED,
        PLAYERHOOK_ON_AFTER_SPEC_SLOT_CHANGED,
        PLAYERHOOK_ON_EQUIP,
        PLAYERHOOK_ON_UPDATE
    }) { }

    void OnPlayerLogin(Player* player) override
    {
        ReconcilePrimalistWeapon(player);
    }

    void OnPlayerLogout(Player* player) override
    {
        RemovePrimalistHelpers(player);
    }

    void OnPlayerJustDied(Player* player) override
    {
        RemovePrimalistHelpers(player);
    }

    void OnPlayerLearnSpell(Player* player, uint32 spellId) override
    {
        if (spellId == SPELL_PRIMAL_WEAPONS)
            ReconcilePrimalistWeapon(player);
    }

    void OnPlayerForgotSpell(Player* player, uint32 /*spellId*/) override
    {
        ReconcilePrimalistWeapon(player);
    }

    void OnPlayerLevelChanged(Player* player, uint8 /*oldLevel*/) override
    {
        ReconcilePrimalistWeapon(player);
    }

    void OnPlayerAfterSpecSlotChanged(Player* player, uint8 /*newSlot*/) override
    {
        ReconcilePrimalistWeapon(player);
    }

    void OnPlayerEquip(Player* player, Item* /*item*/, uint8 /*bag*/, uint8 /*slot*/, bool /*update*/) override
    {
        ReconcilePrimalistWeapon(player);
    }

    void OnPlayerUpdate(Player* player, uint32 /*diff*/) override
    {
        if (!player)
            return;
        // Ownership can be updated after the learn/forget hooks; also catch unequipping a weapon.
        if (player->HasAura(SPELL_BESTIAL_MIGHT) || player->HasAura(SPELL_PRIMAL_MIGHT) ||
            player->HasAura(SPELL_WILDCLAW_BONUS) || player->HasAura(SPELL_TALONFURY) ||
            player->HasAura(SPELL_EARTHSHAPING) || player->HasAura(SPELL_STONESHARD_MODIFIER) ||
            player->HasAura(SPELL_EARTHQUAKE_MODIFIER) || player->HasAura(SPELL_ERUPTION_MODIFIER))
            ReconcilePrimalistWeapon(player);

        if (PrimalistEnabled(player))
            if (Pet* pet = player->GetPet(); pet && pet->getPetType() == HUNTER_PET &&
                pet->GetPower(POWER_HAPPINESS) != pet->GetMaxPower(POWER_HAPPINESS))
                pet->SetPower(POWER_HAPPINESS, pet->GetMaxPower(POWER_HAPPINESS));
    }
};
}

// Esteria has simultaneous kits; owning the baseline ability replaces CoA specialization 59.
bool IsAscensionPrimalistTameEligible(Player const* player)
{
    return PrimalistEnabled(player) && player->GetLevel() >= 10 && player->HasSpell(SPELL_PRIMALIST_PET_TRAINING);
}

bool IsAscensionPrimalistWeaponsEligible(Player const* player, bool /*allowUnconfirmed*/)
{
    return PrimalistEnabled(player) && player->GetLevel() >= 20 && player->HasSpell(SPELL_PRIMAL_WEAPONS);
}

void ApplyCoAPrimalistContracts(SpellInfo* spellInfo)
{
    if (!sClasslessMgr->cfg.coaEnable || !spellInfo)
        return;
    // Earthshaping is already applied by CoAGlue.cpp.
    ApplyAscensionPrimalistEarthquakeContract(spellInfo);
    ApplyAscensionPrimalistSpiritBeastContract(spellInfo);
    ApplyAscensionPrimalistWeaponsContract(spellInfo);
}

void AddCoAPrimalistPackage()
{
    new cw_coa_primalist_player();
    new cw_coa_primalist_resources();
    new cw_coa_primalist_periodic_resources();

    // CoAScriptLoader order, excluding Earthshaping which CoAGlue.cpp already registers.
    AddSC_AscensionPrimalistHeavyEarth();
    AddSC_AscensionPrimalistEarthshaker();
    AddSC_AscensionPrimalistRunningInstinct();
    AddSC_AscensionPrimalistRideWave();
    AddSC_AscensionPrimalistPowerHammer();
    AddSC_AscensionPrimalistEmeraldWill();
    AddSC_AscensionPrimalistTotemicEchoes();
    AddSC_AscensionPrimalistWildCarnage();
    AddSC_AscensionPrimalistPendant();
    AddSC_AscensionPrimalistThorns();
    AddSC_AscensionPrimalistBloodyClaws();
    AddSC_AscensionPrimalistJudgement();
    AddSC_AscensionPrimalistShattering();
    AddSC_AscensionPrimalistPrecision();
    AddSC_AscensionPrimalistVerdantChase();
    AddSC_AscensionPrimalistJourney();
    AddSC_AscensionPrimalistQuakingThane();
    AddSC_AscensionPrimalistTremors();
    AddSC_AscensionPrimalistCataclysm();
    AddSC_AscensionPrimalistFaePresence();
    AddSC_AscensionPrimalistEarthsGuidance();
    AddSC_AscensionPrimalistGroveTender();
    AddSC_AscensionPrimalistBramblepatch();
    AddSC_AscensionPrimalistPrimalStrikes();
    AddSC_AscensionPrimalistLithicLance();
    AddSC_AscensionPrimalistEmpoweredBoons();
    AddSC_AscensionPrimalistEarthmotherWarden();
    AddSC_AscensionPrimalistDruidTraining();
    AddSC_AscensionPrimalistSpiritualFrenzy();
    AddSC_AscensionPrimalistPhysicalCrit();
    AddSC_AscensionPrimalistRipsAndTears();
    AddSC_AscensionPrimalistMountainAvatar();
    AddSC_AscensionPrimalistRylaksBite();
    AddSC_AscensionPrimalistRylaksBlessing();
    AddSC_AscensionPrimalistWildheart();
    AddSC_AscensionPrimalistDreamslip();
    AddSC_AscensionPrimalistDouse();
    AddSC_AscensionPrimalistNeptulonWrath();
    AddSC_AscensionPrimalistSacredGrove();
    AddSC_AscensionPrimalistAncientWar();
    AddSC_AscensionPrimalistEarthmotherRoar();
    AddSC_AscensionPrimalistRushHunt();
    AddSC_AscensionPrimalistCrushingEarth();
    AddSC_AscensionPrimalistSpiritBeast();
    AddSC_AscensionPrimalistWeapons();
    AddSC_AscensionPrimalistTalents();
    AddSC_AscensionPrimalistBones();
    AddSC_AscensionPrimalistBoons();
    AddSC_AscensionPrimalistSeismicResources();
    AddSC_AscensionPrimalistGuidance();
    AddSC_AscensionPrimalistBarrier();
    AddSC_AscensionPrimalistGrove();
    AddSC_AscensionPrimalistMountainFury();
    AddSC_AscensionPrimalistBoulder();
    AddSC_AscensionPrimalistUrsoc();
    AddSC_AscensionPrimalistTorn();
    AddSC_AscensionPrimalistRexxarMight();
    AddSC_AscensionPrimalistMineralization();
    AddSC_AscensionPrimalistLifeSpirit();
    AddSC_AscensionPrimalistTotem();
    AddSC_AscensionPrimalistHeavyHanded();
    AddSC_AscensionPrimalistTremor();
    AddSC_AscensionPrimalistPulverize();
    AddSC_AscensionPrimalistStoneTosser();
    AddSC_AscensionPrimalistVitality();
    AddSC_AscensionPrimalistMagmatism();
    AddSC_AscensionPrimalistGeomancy();
    AddSC_AscensionPrimalistMountain();
    AddSC_AscensionPrimalistSecondary();
}
