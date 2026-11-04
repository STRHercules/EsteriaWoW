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

#include "ClasslessMgr.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "SpellInfo.h"

namespace
{
    // Conquest of Azeroth authored some spells' numbers for level 1 and grows
    // them along one curve (AscensionScalingBase.cpp); cw_coa_spell_scaling
    // names the effects that do. Without it those spells hit for their
    // level 1 value at every level.
    double CoALevelCurve(uint8 level)
    {
        return 0.0267291844060354 + 0.0048541098014737 * level + 0.0001859597762293 * level * level;
    }

    // a pet's spells scale with its owner
    Player const* LevelOwner(Unit const* caster)
    {
        if (Player const* player = caster->ToPlayer())
            return player;
        if (Unit const* owner = caster->GetOwner())
            return owner->ToPlayer();
        return nullptr;
    }
}

class cw_coa_scaling : public UnitScript
{
public:
    cw_coa_scaling() : UnitScript("cw_coa_scaling", true, { UNITHOOK_MODIFY_SPELL_EFFECT_BASE_VALUE }) { }

    void ModifySpellEffectBaseValue(Unit const* caster, SpellInfo const* spellInfo, uint8 effectIndex,
                                    float& value) override
    {
        if (!spellInfo || value == 0.0f || effectIndex >= MAX_SPELL_EFFECTS)
            return;
        if (!(sClasslessMgr->CoAScalingMask(spellInfo->Id) & (1 << effectIndex)))
            return;
        if (Player const* player = LevelOwner(caster))
            value = float(double(value) * CoALevelCurve(player->GetLevel()));
    }
};

void AddClasslessCoAScripts()
{
    new cw_coa_scaling();
}
