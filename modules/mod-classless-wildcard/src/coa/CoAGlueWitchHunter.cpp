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

// The Witch Hunter package (CoA CLASS_WITCH_HUNTER, spell family 21): what
// CoA's AscensionClassMechanics, AscensionCompat, CoAScriptLoader and core
// asked of it, kept out of CoAGlue.cpp.

#include "AscensionWitchHunterCompletion.h"
#include "AscensionWitchHunterFlames.h"
#include "AscensionWitchHunterScaling.h"
#include "AscensionWitchHunterStake.h"
#include "AscensionWitchHunterTargeting.h"
#include "AscensionWitchHunterTonics.h"
#include "ClasslessMgr.h"
#include "CoAPort.h"
#include "ScriptMgr.h"
#include "SpellInfo.h"
#include "Unit.h"

void AddAscensionWitchHunterTonicScripts();
void AddAscensionWitchHunterTonicTalentScripts();
void AddAscensionWitchHunterTorchScripts();
void AddAscensionWitchHunterFlameScripts();
void AddAscensionWitchHunterTorchlightScripts();
void AddAscensionWitchHunterStakeScripts();
void AddAscensionWitchHunterCompletionScripts();
void AddAscensionWitchHunterEventScripts();
void AddAscensionWitchHunterAbilityScripts();
void AddAscensionWitchHunterDefenseScripts();
void AddAscensionWitchHunterSummonScripts();

// CoA's AscensionCompat answers from its appearance collection, which Esteria
// does not have: the Shadowhound keeps its creature display.
uint32 AscensionWitchHunter::GetShadowhoundDisplay(Player* /*player*/)
{
    return 0;
}

// ApplyAscensionClassMechanics' Witch Hunter lines, in CoA's order (before the
// Witch Doctor contracts)
void ApplyCoAWitchHunterContracts(SpellInfo* spellInfo)
{
    ApplyAscensionWitchHunterTonicContracts(spellInfo);
    ApplyAscensionWitchHunterFlameContracts(spellInfo);
    ApplyAscensionWitchHunterScalingContracts(spellInfo);
    ApplyAscensionWitchHunterTargetingContracts(spellInfo);
    ApplyAscensionWitchHunterStakeContracts(spellInfo);
    AscensionWitchHunter::ApplyContracts(spellInfo);
}

class cw_coa_witch_hunter_casting : public UnitScript
{
public:
    cw_coa_witch_hunter_casting() : UnitScript("cw_coa_witch_hunter_casting", true,
        { UNITHOOK_CAN_CAST_SPELL_WHILE_MOVING }) { }

    // CoA's Unit::CanCastSpellWhileMoving: Witch Hunter channels (family 21)
    [[nodiscard]] bool CanCastSpellWhileMoving(Unit const* unit, SpellInfo const* info) override
    {
        return sClasslessMgr->cfg.coaEnable && info && info->SpellFamilyName == 21 && info->IsChanneled() &&
            ((info->SpellFamilyFlags[0] & 2) || info->Id == 807364) && HasCoAKit(unit, CLASS_WITCH_HUNTER);
    }
};

// CoAScriptLoader.cpp's Witch Hunter block, in its order
void AddCoAWitchHunterPackage()
{
    new cw_coa_witch_hunter_casting();

    AddAscensionWitchHunterTonicScripts();
    AddAscensionWitchHunterTonicTalentScripts();
    AddAscensionWitchHunterTorchScripts();
    AddAscensionWitchHunterFlameScripts();
    AddAscensionWitchHunterTorchlightScripts();
    AddAscensionWitchHunterStakeScripts();
    AddAscensionWitchHunterCompletionScripts();
    AddAscensionWitchHunterEventScripts();
    AddAscensionWitchHunterAbilityScripts();
    AddAscensionWitchHunterDefenseScripts();
    AddAscensionWitchHunterSummonScripts();
}
