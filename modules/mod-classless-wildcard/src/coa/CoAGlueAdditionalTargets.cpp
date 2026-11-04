/* Copyright (C) 2016+ AzerothCore, GNU AGPL v3. */

// CoA's additional-target contracts (ApplyAdditionalTargetContracts in AscensionClassMechanics.cpp): eight kit
// spells carry their extra targets as a flat spell modifier on an op this engine does not read, and become the
// stock "max affected targets" aura at load.

#include "CoAPort.h"
#include "Log.h"
#include "SpellInfo.h"
#include <array>

namespace
{
enum AdditionalTargetSpells : uint32
{
    AdvantageQuills = 801429,
    AerialAssault = 705068,
    PulsarExplosionRankOne = 704794,
    PulsarExplosionRankTwo = 707894,
    GoodVenom = 680797,
    Lifemender = 706477,
    PropheticSpeaker = 706956,
    Earthsplitter = 806081
};

constexpr int32 ADDITIONAL_TARGETS_OP = 34;

struct Contract
{
    uint32 SpellId;
    uint32 Family;
    SpellEffIndex EffectIndex;
    int32 BasePoints;
    std::array<uint32, 3> Mask;
};

constexpr std::array<Contract, 8> CONTRACTS =
{{
    { AdvantageQuills, 27, EFFECT_1, 0, {{ 0, 4, 0 }} },
    { AerialAssault, 27, EFFECT_2, 1, {{ 512, 0, 0 }} },
    { PulsarExplosionRankOne, 32, EFFECT_0, 0, {{ 0, 128, 0 }} },
    { PulsarExplosionRankTwo, 32, EFFECT_0, 1, {{ 0, 128, 0 }} },
    { GoodVenom, 35, EFFECT_0, 0, {{ 0, 0, 524288 }} },
    { Lifemender, 35, EFFECT_0, 4, {{ 4194304, 0, 0 }} },
    { PropheticSpeaker, 35, EFFECT_1, 4, {{ 0, 0, 8 }} },
    { Earthsplitter, 24, EFFECT_2, 0, {{ 16, 0, 0 }} }
}};
}

void ApplyCoAAdditionalTargetContracts(SpellInfo* spellInfo)
{
    if (!spellInfo)
        return;

    for (Contract const& contract : CONTRACTS)
    {
        if (spellInfo->Id != contract.SpellId)
            continue;

        SpellEffectInfo& effect = spellInfo->Effects[contract.EffectIndex];
        if (spellInfo->SpellFamilyName == contract.Family && spellInfo->ProcCharges == 0 &&
            effect.Effect == SPELL_EFFECT_APPLY_AURA &&
            (effect.ApplyAuraName == SPELL_AURA_ADD_FLAT_MODIFIER ||
                effect.ApplyAuraName == SPELL_AURA_MOD_MAX_AFFECTED_TARGETS) &&
            effect.MiscValue == ADDITIONAL_TARGETS_OP && effect.BasePoints == contract.BasePoints &&
            effect.DieSides == 1 && effect.TargetA.GetTarget() == TARGET_UNIT_CASTER &&
            effect.TargetB.GetTarget() == 0 &&
            effect.SpellClassMask == flag96(contract.Mask[0], contract.Mask[1], contract.Mask[2]))
            effect.ApplyAuraName = SPELL_AURA_MOD_MAX_AFFECTED_TARGETS;
        else
            LOG_ERROR("module.classless", "CoA: skipped unexpected additional-target record {}", spellInfo->Id);
        return;
    }
}
