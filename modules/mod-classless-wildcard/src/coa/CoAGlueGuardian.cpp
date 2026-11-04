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

// The Guardian package (CoA CLASS_GUARDIAN, spell family 24): the Guardian
// lines of CoA's AscensionClassMechanics.cpp (formations, Centurion Strike's
// weapon effects, the cast/hit/block talent triggers, the load-time record
// fixes) and its CoAScriptLoader block, kept out of CoAGlue.cpp. Every hook
// returns early unless the player owns the Guardian kit.

#include "AscensionGuardianCompletion.h"
#include "AscensionGuardianResources.h"
#include "CellImpl.h"
#include "ClasslessMgr.h"
#include "CoAPort.h"
#include "GridNotifiers.h"
#include "GridNotifiersImpl.h"
#include "Item.h"
#include "Log.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "Spell.h"
#include "SpellAuras.h"
#include "SpellInfo.h"
#include "SpellMgr.h"
#include <algorithm>
#include <array>
#include <cmath>

void AddAscensionGuardianStandardScripts();
void AddAscensionGuardianFavorScripts();
void AddAscensionGuardianEventScripts();
void AddAscensionGuardianCompletionScripts();
void AddAscensionGuardianAbilityScripts();
void AddAscensionGuardianTalentScripts();
void AddAscensionGuardianDrumScripts();

namespace
{
constexpr uint32 SPELL_GUARDIAN_TOWER_FORMATION = 800317;
constexpr uint32 SPELL_GUARDIAN_TOWER_FORMATION_EFFECTS = 803431;
constexpr uint32 SPELL_GUARDIAN_TOWER_FORMATION_STANCE = 803907;
constexpr uint32 SPELL_GUARDIAN_LINE_FORMATION = 803130;
constexpr uint32 SPELL_GUARDIAN_LINE_FORMATION_EFFECTS = 803151;
constexpr uint32 SPELL_GUARDIAN_ASSAULT_FORMATION = 803417;
constexpr uint32 SPELL_GUARDIAN_ASSAULT_FORMATION_EFFECTS = 803709;
constexpr uint32 SPELL_GUARDIAN_ASSAULT_FORMATION_VISUAL = 803419;
constexpr uint32 SPELL_GUARDIAN_TOWER_FORMATION_VISUAL = 803941;
constexpr uint32 SPELL_GUARDIAN_FOOTMANS_CALLING = 92105;
constexpr uint32 SPELL_GUARDIAN_FOOTMANS_CALLING_EFFECTS = 807728;
constexpr uint32 SPELL_GUARDIAN_REPRISAL_READY = 504885;
constexpr uint32 SPELL_GUARDIAN_CENTURION_SWORD_ATTACKS = 807967;
constexpr uint8 GUARDIAN_CENTURION_SWORD_EVENT = 16;
constexpr uint8 GUARDIAN_CENTURION_POLEARM_EVENT = 22;
constexpr uint32 SPELL_GUARDIAN_CENTURION_AXE_EFFECTS = 542238;
constexpr uint32 SPELL_GUARDIAN_CENTURION_MACE_EFFECTS = 542265;
constexpr uint32 SPELL_GUARDIAN_RAISE_SHIELD = 500168;
constexpr uint32 SPELL_GUARDIAN_RAISE_SHIELD_ENERGIZE = 500493;
constexpr uint32 SPELL_GUARDIAN_GUARDBREAKER = 504385;
constexpr uint32 SPELL_GUARDIAN_GUARDBREAKER_RESET = 802895;
constexpr uint32 SPELL_GUARDIAN_REFUSE = 804892;
constexpr uint32 SPELL_GUARDIAN_REFUSE_RESET = 807191;
constexpr uint32 SPELL_GUARDIAN_NO_ESCAPE = 802300;
constexpr uint32 SPELL_GUARDIAN_NO_ESCAPE_RESET = 806544;
constexpr uint32 SPELL_GUARDIAN_BULWARK_RUSH = 300536;
constexpr uint32 SPELL_GUARDIAN_BULWARK_RUSH_EFFECTS = 300537;
constexpr uint32 SPELL_GUARDIAN_ORDER_IN_THE_COURT = 707716;
constexpr uint32 SPELL_GUARDIAN_ORDER_IN_THE_COURT_DEBUFF = 704417;
constexpr uint32 SPELL_GUARDIAN_FORCEFUL_IMPACT = 705346;
constexpr uint32 SPELL_GUARDIAN_BRACE = 800313;
constexpr uint32 SPELL_GUARDIAN_KINGS_GUARD = 803134;
constexpr uint32 SPELL_GUARDIAN_KINGS_GUARD_RESET = 520284;
constexpr uint32 SPELL_GUARDIAN_WRECK_FORMATION = 803126;
constexpr uint32 SPELL_GUARDIAN_WRECK_FORMATION_AP = 803416;
constexpr uint32 SPELL_GUARDIAN_HIGH_GUARD = 707621;
constexpr uint32 SPELL_GUARDIAN_HIGH_GUARD_EFFECTS = 504586;
constexpr uint32 SPELL_GUARDIAN_PLATE_BUSTER = 705333;
constexpr uint32 SPELL_GUARDIAN_PLATE_BUSTER_RESET = 705334;
constexpr uint32 SPELL_GUARDIAN_VANGUARDS_MIGHT = 705345;
constexpr uint32 SPELL_GUARDIAN_VANGUARDS_MIGHT_EFFECTS = 802894;
constexpr uint32 SPELL_GUARDIAN_PINNED_DOWN = 301252;
constexpr uint32 SPELL_GUARDIAN_PINNED_DOWN_REFRESH = 600325;
constexpr uint32 SPELL_GUARDIAN_SHOW_OF_FORCE = 573047;
constexpr uint32 SPELL_GUARDIAN_SHOW_OF_FORCE_DISPEL = 520861;
constexpr uint32 SPELL_GUARDIAN_KNIGHTS_SONG = 505228;
constexpr uint32 SPELL_GUARDIAN_KNIGHTS_SONG_EFFECTS = 807460;
constexpr uint32 SPELL_GUARDIAN_MINSTREL = 704533;
constexpr uint32 SPELL_GUARDIAN_MINSTREL_EFFECTS = 704534;
#ifdef ESTERIA_COA_BLOCK_HOOK
constexpr uint32 SPELL_GUARDIAN_REPRISAL = 800316;
constexpr uint32 SPELL_GUARDIAN_VETERAN = 300540;
constexpr uint32 SPELL_GUARDIAN_VETERAN_HEAL = 705382;
constexpr uint32 SPELL_GUARDIAN_HONORABLE = 705377;
constexpr uint32 SPELL_GUARDIAN_HONORABLE_EFFECTS = 524931;
#endif
constexpr int32 GUARDIAN_RAISE_SHIELD_ENERGY_BASE_POINTS = 19;
constexpr uint32 GUARDIAN_FORCEFUL_IMPACT_EXTENSION_MS = 1000;
constexpr uint32 GUARDIAN_KINGS_GUARD_ICD_MS = 1000;
constexpr uint8 GUARDIAN_GUARDBREAKER_CHANCE = 20;
constexpr uint8 GUARDIAN_KINGS_GUARD_CHANCE = 10;
constexpr float GUARDIAN_CENTURION_POLEARM_DEPTH = 5.0f;
constexpr float GUARDIAN_CENTURION_POLEARM_HALF_WIDTH = 2.5f;
constexpr uint32 GUARDIAN_CENTURION_DAMAGE_EFFECT_MASK = (1u << EFFECT_0) | (1u << EFFECT_2);

constexpr std::array<uint32, 3> GUARDIAN_FORMATIONS =
{{
    SPELL_GUARDIAN_TOWER_FORMATION, SPELL_GUARDIAN_LINE_FORMATION, SPELL_GUARDIAN_ASSAULT_FORMATION
}};

constexpr std::array<uint32, 7> GUARDIAN_FORMATION_HELPERS =
{{
    SPELL_GUARDIAN_TOWER_FORMATION_EFFECTS, SPELL_GUARDIAN_TOWER_FORMATION_STANCE,
    SPELL_GUARDIAN_LINE_FORMATION_EFFECTS, SPELL_GUARDIAN_ASSAULT_FORMATION_EFFECTS,
    SPELL_GUARDIAN_FOOTMANS_CALLING_EFFECTS, SPELL_GUARDIAN_ASSAULT_FORMATION_VISUAL,
    SPELL_GUARDIAN_TOWER_FORMATION_VISUAL
}};

bool Enabled() { return sClasslessMgr->cfg.coaEnable; }

Player* GuardianOf(Unit* unit)
{
    Player* player = unit ? unit->ToPlayer() : nullptr;
    return player && HasCoAKit(player, CLASS_GUARDIAN) ? player : nullptr;
}

bool InRange(uint32 id, uint32 first, uint32 last) { return id >= first && id <= last; }
bool IsHammerOfJustice(uint32 id) { return id == 704418 || InRange(id, 707710, 707715); }
bool IsSpearThrow(uint32 id) { return id == 500463 || InRange(id, 572142, 572147); }
bool IsBattleRush(uint32 id) { return id == 802197 || InRange(id, 501546, 501548); }
bool IsBalladOfTheConqueror(uint32 id) { return id == 801776 || InRange(id, 501068, 501074) || id == 574340; }
bool IsStandardOfValiance(uint32 id)
{
    return id == 800315 || id == 800319 || InRange(id, 501538, 501545) || InRange(id, 803931, 803938);
}

void RemoveFormationHelpers(Player* player)
{
    for (uint32 id : GUARDIAN_FORMATION_HELPERS)
        player->RemoveAurasDueToSpell(id);
}

void ApplyFormation(Player* player, uint32 spellId)
{
    for (uint32 formation : GUARDIAN_FORMATIONS)
        if (formation != spellId)
            player->RemoveAurasDueToSpell(formation);

    RemoveFormationHelpers(player);
    switch (spellId)
    {
        case SPELL_GUARDIAN_TOWER_FORMATION:
            player->CastSpell(player, SPELL_GUARDIAN_TOWER_FORMATION_EFFECTS, true);
            player->CastSpell(player, SPELL_GUARDIAN_TOWER_FORMATION_STANCE, true);
            break;
        case SPELL_GUARDIAN_LINE_FORMATION:
            player->CastSpell(player, SPELL_GUARDIAN_LINE_FORMATION_EFFECTS, true);
            break;
        case SPELL_GUARDIAN_ASSAULT_FORMATION:
            player->CastSpell(player, SPELL_GUARDIAN_ASSAULT_FORMATION_EFFECTS, true);
            break;
        default:
            break;
    }

    if ((spellId == SPELL_GUARDIAN_TOWER_FORMATION || spellId == SPELL_GUARDIAN_LINE_FORMATION) &&
        player->HasAura(SPELL_GUARDIAN_FOOTMANS_CALLING))
        player->CastSpell(player, SPELL_GUARDIAN_FOOTMANS_CALLING_EFFECTS, true);
}

void ExtendBrace(Player* player)
{
    if (Aura* brace = player->GetAura(SPELL_GUARDIAN_BRACE))
        brace->SetDuration(std::min(brace->GetMaxDuration(),
            brace->GetDuration() + int32(GUARDIAN_FORCEFUL_IMPACT_EXTENSION_MS)));
}

void TryKingsGuardReset(Player* player)
{
    if (!player->HasAura(SPELL_GUARDIAN_KINGS_GUARD) || player->HasSpellCooldown(SPELL_GUARDIAN_KINGS_GUARD) ||
        !roll_chance_i(GUARDIAN_KINGS_GUARD_CHANCE))
        return;

    player->CastSpell(player, SPELL_GUARDIAN_KINGS_GUARD_RESET, true);
    player->AddSpellCooldown(SPELL_GUARDIAN_KINGS_GUARD, 0, GUARDIAN_KINGS_GUARD_ICD_MS);
}

uint32 MainHandSubclass(Player const* player)
{
    Item const* weapon = player->GetWeaponForAttack(BASE_ATTACK, true);
    ItemTemplate const* proto = weapon ? weapon->GetTemplate() : nullptr;
    return proto && proto->Class == ITEM_CLASS_WEAPON ? proto->SubClass : MAX_ITEM_SUBCLASS_WEAPON;
}

bool IsSword(uint32 subclass) { return subclass == ITEM_SUBCLASS_WEAPON_SWORD || subclass == ITEM_SUBCLASS_WEAPON_SWORD2; }
bool IsAxe(uint32 subclass) { return subclass == ITEM_SUBCLASS_WEAPON_AXE || subclass == ITEM_SUBCLASS_WEAPON_AXE2; }
bool IsMace(uint32 subclass) { return subclass == ITEM_SUBCLASS_WEAPON_MACE || subclass == ITEM_SUBCLASS_WEAPON_MACE2; }

void RemoveCenturionWeaponEffects(Player* player)
{
    player->RemoveAurasDueToSpell(SPELL_GUARDIAN_CENTURION_AXE_EFFECTS);
    player->RemoveAurasDueToSpell(SPELL_GUARDIAN_CENTURION_MACE_EFFECTS);
}

// a polearm's Centurion Strike also hits whoever stands right behind the target
void AddCenturionPolearmTargets(Spell* spell, Player* player)
{
    Unit* primary = spell->GetOriginalTarget();
    if (!primary || primary == player)
        return;

    float dirX = primary->GetPositionX() - player->GetPositionX();
    float dirY = primary->GetPositionY() - player->GetPositionY();
    float length = std::hypot(dirX, dirY);
    if (length <= 0.001f)
        return;
    dirX /= length;
    dirY /= length;

    float range = length + GUARDIAN_CENTURION_POLEARM_DEPTH;
    std::list<Unit*> candidates;
    Acore::AnyUnfriendlyUnitInObjectRangeCheck check(player, player, range);
    Acore::UnitListSearcher<Acore::AnyUnfriendlyUnitInObjectRangeCheck> searcher(player, candidates, check);
    Cell::VisitObjects(player, searcher, range);

    for (Unit* candidate : candidates)
    {
        if (!candidate || candidate == primary || !candidate->IsAlive() ||
            !player->IsValidAttackTarget(candidate, spell->GetSpellInfo()) || !player->IsWithinLOSInMap(candidate))
            continue;

        float relX = candidate->GetPositionX() - primary->GetPositionX();
        float relY = candidate->GetPositionY() - primary->GetPositionY();
        float depth = relX * dirX + relY * dirY;
        float lateral = std::abs(relX * dirY - relY * dirX);
        if (depth <= 0.0f || depth > GUARDIAN_CENTURION_POLEARM_DEPTH ||
            lateral > GUARDIAN_CENTURION_POLEARM_HALF_WIDTH + candidate->GetCombatReach() ||
            std::abs(candidate->GetPositionZ() - primary->GetPositionZ()) > GUARDIAN_CENTURION_POLEARM_DEPTH)
            continue;

        spell->AddUnitTargetForScript(candidate, GUARDIAN_CENTURION_DAMAGE_EFFECT_MASK, true, true);
    }
}
}

// ApplyAscensionClassMechanics' Guardian lines, in CoA's order: the resource
// contracts (which run AscensionGuardian::ApplyContracts) come first, the
// Bannerman and Raise Shield record fixes later in the same function
void ApplyCoAGuardianContracts(SpellInfo* spellInfo)
{
    if (!spellInfo || spellInfo->SpellFamilyName != uint32(CLASS_GUARDIAN) + 6)
        return;

    ApplyAscensionGuardianResourceContracts(spellInfo);

    if (spellInfo->Id == 504144)
    {
        SpellEffectInfo& effect = spellInfo->Effects[EFFECT_0];
        if (effect.Effect == SPELL_EFFECT_APPLY_AURA && effect.ApplyAuraName == SPELL_AURA_ADD_FLAT_MODIFIER &&
            effect.MiscValue == SPELLMOD_EFFECT3 && effect.SpellClassMask == flag96(0, 0, 0x00100000))
            effect.ApplyAuraName = SPELL_AURA_DUMMY;
        else
            LOG_ERROR("module", "CoA: skipped unexpected Bannerman record {}", spellInfo->Id);
    }

    if (spellInfo->Id == SPELL_GUARDIAN_RAISE_SHIELD_ENERGIZE)
    {
        SpellEffectInfo& effect = spellInfo->Effects[EFFECT_0];
        if (effect.Effect == SPELL_EFFECT_ENERGIZE && effect.MiscValue == POWER_ENERGY && effect.DieSides == 1 &&
            (effect.BasePoints == 29 || effect.BasePoints == GUARDIAN_RAISE_SHIELD_ENERGY_BASE_POINTS))
            effect.BasePoints = GUARDIAN_RAISE_SHIELD_ENERGY_BASE_POINTS;
        else
            LOG_ERROR("module", "CoA: skipped unexpected Raise Shield energize record {}", spellInfo->Id);
    }
}

class cw_coa_guardian_spells : public AllSpellScript
{
public:
    cw_coa_guardian_spells() : AllSpellScript("cw_coa_guardian_spells", {
        ALLSPELLHOOK_ON_CAST,
        ALLSPELLHOOK_ON_BEFORE_EFFECTS,
        ALLSPELLHOOK_ON_HIT_RESULT
    }) { }

    // PrepareAscensionClassMechanicsCast: Centurion Strike reads the main-hand weapon
    void OnSpellBeforeEffects(Spell* spell, Unit* /*caster*/, SpellInfo const* /*spellInfo*/) override
    {
        if (!Enabled() || !spell || spell->IsTriggered() || !AscensionGuardian::Centurion(spell->GetSpellInfo()->Id))
            return;
        Player* player = GuardianOf(spell->GetCaster());
        if (!player)
            return;

        RemoveCenturionWeaponEffects(player);
        uint32 const subclass = MainHandSubclass(player);
        if (IsAxe(subclass))
            player->CastSpell(player, SPELL_GUARDIAN_CENTURION_AXE_EFFECTS, true);
        else if (IsMace(subclass))
            player->CastSpell(player, SPELL_GUARDIAN_CENTURION_MACE_EFFECTS, true);
        else if (subclass == ITEM_SUBCLASS_WEAPON_POLEARM)
            AddCenturionPolearmTargets(spell, player);
    }

    // HandleAscensionClassMechanicsCast: the resource service first, then the Guardian block
    void OnSpellCast(Spell* spell, Unit* /*caster*/, SpellInfo const* /*spellInfo*/, bool /*skipCheck*/) override
    {
        if (!Enabled() || !spell)
            return;
        HandleAscensionGuardianResourceCast(spell);
        if (spell->IsTriggered())
            return;
        Player* player = GuardianOf(spell->GetCaster());
        if (!player)
            return;

        SpellInfo const* info = spell->GetSpellInfo();
        uint32 const spellId = info->Id;
        if (sSpellMgr->GetFirstSpellInChain(spellId) == 800316)
        {
            player->CastSpell(player, 500175, true);
            player->RemoveAurasDueToSpell(SPELL_GUARDIAN_REPRISAL_READY);
        }
        else if (AscensionGuardian::Centurion(spellId) && player->HasAura(504140))
            player->CastSpell(player, 504143, true);

        bool const guardbreaker = AscensionGuardian::Pulverize(spellId) || AscensionGuardian::Ram(spellId) ||
            (player->HasAura(505344) && IsBalladOfTheConqueror(spellId));
        if (guardbreaker && player->HasAura(SPELL_GUARDIAN_GUARDBREAKER) && roll_chance_i(GUARDIAN_GUARDBREAKER_CHANCE))
            player->CastSpell(player, SPELL_GUARDIAN_GUARDBREAKER_RESET, true);

        if (AscensionGuardian::Advance(spellId) && player->HasAura(SPELL_GUARDIAN_REFUSE))
            player->CastSpell(player, SPELL_GUARDIAN_REFUSE_RESET, true);

        if (IsBattleRush(spellId) && player->HasAura(SPELL_GUARDIAN_BULWARK_RUSH))
            player->CastSpell(player, SPELL_GUARDIAN_BULWARK_RUSH_EFFECTS, true);

        if ((spellId == SPELL_GUARDIAN_RAISE_SHIELD || AscensionGuardian::HeavyBlow(spellId)) &&
            player->HasAura(SPELL_GUARDIAN_FORCEFUL_IMPACT))
            ExtendBrace(player);

        if (AscensionGuardian::HeavyBlow(spellId))
        {
            if (player->HasAura(SPELL_GUARDIAN_VANGUARDS_MIGHT))
                player->CastSpell(player, SPELL_GUARDIAN_VANGUARDS_MIGHT_EFFECTS, true);
            if (player->HasAura(SPELL_GUARDIAN_HIGH_GUARD_EFFECTS))
            {
                player->RemoveAurasDueToSpell(SPELL_GUARDIAN_HIGH_GUARD_EFFECTS);
                player->CastSpell(player, SPELL_GUARDIAN_REPRISAL_READY, true);
            }
        }

        if ((spellId == SPELL_GUARDIAN_RAISE_SHIELD || AscensionGuardian::Advance(spellId) || IsBattleRush(spellId)) &&
            player->HasAura(SPELL_GUARDIAN_HIGH_GUARD))
            player->CastSpell(player, SPELL_GUARDIAN_HIGH_GUARD_EFFECTS, true);

        if ((IsStandardOfValiance(spellId) || spellId == 803420) && player->HasAura(SPELL_GUARDIAN_WRECK_FORMATION))
            player->CastSpell(player, SPELL_GUARDIAN_WRECK_FORMATION_AP, true);

        if (AscensionGuardian::Ballad(spellId))
        {
            if (player->HasAura(SPELL_GUARDIAN_KNIGHTS_SONG))
                player->CastSpell(player, SPELL_GUARDIAN_KNIGHTS_SONG_EFFECTS, true);
            if (player->HasAura(SPELL_GUARDIAN_MINSTREL))
                player->CastSpell(player, SPELL_GUARDIAN_MINSTREL_EFFECTS, true);
        }

        if (AscensionGuardian::Centurion(spellId))
            RemoveCenturionWeaponEffects(player);
    }

    // HandleAscensionClassMechanicsHit's Guardian block
    void OnSpellHitResult(Spell* spell, Unit* target, uint8 missInfo, uint32 damage, uint32 /*healing*/,
                          bool critical) override
    {
        if (!Enabled() || !spell || !target || missInfo != SPELL_MISS_NONE || spell->IsTriggered())
            return;
        Player* player = GuardianOf(spell->GetCaster());
        if (!player || target == player || player->IsFriendlyTo(target))
            return;

        uint32 const spellId = spell->GetSpellInfo()->Id;
        bool const centurion = AscensionGuardian::Centurion(spellId) && target == spell->GetOriginalTarget();
        if (centurion && IsSword(MainHandSubclass(player)) &&
            spell->TryMarkScriptEventHandled(GUARDIAN_CENTURION_SWORD_EVENT))
            player->CastSpell(player, SPELL_GUARDIAN_CENTURION_SWORD_ATTACKS, true);

        if (centurion && damage && MainHandSubclass(player) == ITEM_SUBCLASS_WEAPON_POLEARM &&
            spell->TryMarkScriptEventHandled(GUARDIAN_CENTURION_POLEARM_EVENT))
        {
            SpellInfo const* info = spell->GetSpellInfo();
            uint32 const struck = Unit::DealDamage(player, target, damage, nullptr, SPELL_DIRECT_DAMAGE,
                info->GetSchoolMask(), info, false);
            player->SendSpellNonMeleeDamageLog(target, info, struck, info->GetSchoolMask(), 0, 0, true, 0, critical);
        }

        if (!damage)
            return;

        if (AscensionGuardian::Ram(spellId))
        {
            if (player->HasAura(SPELL_GUARDIAN_NO_ESCAPE) && target->HasRootAura())
                player->CastSpell(player, SPELL_GUARDIAN_NO_ESCAPE_RESET, true);
            if (critical && player->HasAura(SPELL_GUARDIAN_PLATE_BUSTER))
                player->CastSpell(player, SPELL_GUARDIAN_PLATE_BUSTER_RESET, true);
            if (player->HasAura(SPELL_GUARDIAN_SHOW_OF_FORCE))
                player->CastSpell(target, SPELL_GUARDIAN_SHOW_OF_FORCE_DISPEL, true);
            TryKingsGuardReset(player);
        }
        else if (AscensionGuardian::Pulverize(spellId))
            TryKingsGuardReset(player);
        else if (IsHammerOfJustice(spellId) && player->HasAura(SPELL_GUARDIAN_ORDER_IN_THE_COURT))
            player->CastSpell(target, SPELL_GUARDIAN_ORDER_IN_THE_COURT_DEBUFF, true);
        else if (IsSpearThrow(spellId) && player->HasAura(SPELL_GUARDIAN_PINNED_DOWN))
            player->CastSpell(target, SPELL_GUARDIAN_PINNED_DOWN_REFRESH, true);
    }
};

class cw_coa_guardian_auras : public UnitScript
{
public:
    cw_coa_guardian_auras() : UnitScript("cw_coa_guardian_auras", true,
        { UNITHOOK_ON_AURA_APPLY, UNITHOOK_ON_AURA_REMOVE }) { }

    // HandleAscensionClassMechanicsAuraApply's Guardian lines
    void OnAuraApply(Unit* unit, Aura* aura) override
    {
        if (!Enabled() || !aura)
            return;
        uint32 const spellId = aura->GetId();
        bool const formation =
            std::find(GUARDIAN_FORMATIONS.begin(), GUARDIAN_FORMATIONS.end(), spellId) != GUARDIAN_FORMATIONS.end();
        if (!formation && spellId != SPELL_GUARDIAN_FOOTMANS_CALLING)
            return;
        Player* player = GuardianOf(unit);
        if (!player)
            return;

        if (formation)
        {
            ApplyFormation(player, spellId);
            if (spellId == SPELL_GUARDIAN_TOWER_FORMATION)
                player->CastSpell(player, SPELL_GUARDIAN_TOWER_FORMATION_VISUAL, true);
        }
        else if (player->HasAura(SPELL_GUARDIAN_TOWER_FORMATION))
            ApplyFormation(player, SPELL_GUARDIAN_TOWER_FORMATION);
        else if (player->HasAura(SPELL_GUARDIAN_LINE_FORMATION))
            ApplyFormation(player, SPELL_GUARDIAN_LINE_FORMATION);
    }

    // HandleAscensionClassMechanicsAuraRemove's Guardian lines
    void OnAuraRemove(Unit* unit, AuraApplication* aurApp, AuraRemoveMode /*mode*/) override
    {
        if (!Enabled() || !aurApp || !aurApp->GetBase())
            return;
        Player* player = GuardianOf(unit);
        if (!player)
            return;

        uint32 const spellId = aurApp->GetBase()->GetId();
        RemoveAscensionGuardianResourceTalent(player, spellId);
        if (std::find(GUARDIAN_FORMATIONS.begin(), GUARDIAN_FORMATIONS.end(), spellId) != GUARDIAN_FORMATIONS.end())
            RemoveFormationHelpers(player);
        else if (spellId == SPELL_GUARDIAN_FOOTMANS_CALLING)
            player->RemoveAurasDueToSpell(SPELL_GUARDIAN_FOOTMANS_CALLING_EFFECTS);
    }
};

class cw_coa_guardian_player : public PlayerScript
{
public:
    cw_coa_guardian_player() : PlayerScript("cw_coa_guardian_player", { PLAYERHOOK_ON_LOGIN }) { }

    // SynchronizeAscensionClassMechanics' Guardian block: re-derive the formation helpers
    void OnPlayerLogin(Player* player) override
    {
        if (!Enabled() || !GuardianOf(player))
            return;
        if (player->HasAura(SPELL_GUARDIAN_TOWER_FORMATION))
            ApplyFormation(player, SPELL_GUARDIAN_TOWER_FORMATION);
        else if (player->HasAura(SPELL_GUARDIAN_LINE_FORMATION))
            ApplyFormation(player, SPELL_GUARDIAN_LINE_FORMATION);
        else if (player->HasAura(SPELL_GUARDIAN_ASSAULT_FORMATION))
            ApplyFormation(player, SPELL_GUARDIAN_ASSAULT_FORMATION);
        else
            RemoveFormationHelpers(player);
    }
};

#ifdef ESTERIA_COA_BLOCK_HOOK   // Esteria: needs CoA's UnitScript::OnBlock; entries using it stay off
class cw_coa_guardian_block : public UnitScript
{
public:
    cw_coa_guardian_block() : UnitScript("cw_coa_guardian_block", true, { UNITHOOK_ON_BLOCK }) { }

    // HandleAscensionClassMechanicsBlock
    void OnBlock(Unit* victim, Unit* /*attacker*/) override
    {
        Player* player = Enabled() ? GuardianOf(victim) : nullptr;
        if (!player)
            return;
        if (player->HasAura(SPELL_GUARDIAN_RAISE_SHIELD))
            player->CastSpell(player, SPELL_GUARDIAN_RAISE_SHIELD_ENERGIZE, true);
        if (player->HasSpell(SPELL_GUARDIAN_REPRISAL))
            player->CastSpell(player, SPELL_GUARDIAN_REPRISAL_READY, true);
        if (player->HasAura(SPELL_GUARDIAN_VETERAN))
            player->CastSpell(player, SPELL_GUARDIAN_VETERAN_HEAL, true);
        if (player->HasAura(SPELL_GUARDIAN_HONORABLE))
            player->CastSpell(player, SPELL_GUARDIAN_HONORABLE_EFFECTS, true);
    }
};
#endif

// CoAScriptLoader.cpp's Guardian block, in its order
void AddCoAGuardianPackage()
{
    new cw_coa_guardian_spells();
    new cw_coa_guardian_auras();
    new cw_coa_guardian_player();
#ifdef ESTERIA_COA_BLOCK_HOOK
    new cw_coa_guardian_block();
#endif

    AddAscensionGuardianStandardScripts();
    AddAscensionGuardianFavorScripts();
    AddAscensionGuardianEventScripts();
    AddAscensionGuardianCompletionScripts();
    AddAscensionGuardianAbilityScripts();
    AddAscensionGuardianTalentScripts();
    AddAscensionGuardianDrumScripts();
}
