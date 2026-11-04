/* Copyright (C) 2016+ AzerothCore, GNU AGPL v3. */

// CoA's two Tinker Scrap load-time contracts (AscensionClassMechanics.cpp): Scrap stops being a damage modifier
// and becomes a plain resource aura, and Scrapper ticks generate ten Scrap instead of twenty.

#include "CoAPort.h"
#include "Log.h"
#include "Player.h"
#include "SpellInfo.h"
#include <array>

namespace
{
constexpr uint32 SPELL_TINKER_SCRAP = 801816;
constexpr uint32 SPELL_TINKER_SCRAPPER = 525039;
constexpr uint32 SPELL_TINKER_GENERATE_TEN_SCRAP = 704594;
constexpr uint32 SPELL_TINKER_GENERATE_TWENTY_SCRAP = 707596;

void ApplyScrapperContract(SpellInfo* spellInfo)
{
    if (spellInfo->Id != SPELL_TINKER_SCRAPPER || spellInfo->SpellFamilyName != uint32(CLASS_TINKER) + 6)
        return;

    SpellEffectInfo& tick = spellInfo->Effects[EFFECT_0];
    if (tick.Effect == SPELL_EFFECT_APPLY_AURA && tick.ApplyAuraName == SPELL_AURA_PERIODIC_TRIGGER_SPELL &&
        (tick.TriggerSpell == SPELL_TINKER_GENERATE_TWENTY_SCRAP || tick.TriggerSpell == SPELL_TINKER_GENERATE_TEN_SCRAP))
        tick.TriggerSpell = SPELL_TINKER_GENERATE_TEN_SCRAP;
    else
        LOG_ERROR("module.classless", "CoA: skipped unexpected Scrapper resource record {}", spellInfo->Id);
}

void ApplyScrapResourceContract(SpellInfo* spellInfo)
{
    if (spellInfo->Id != SPELL_TINKER_SCRAP || spellInfo->SpellFamilyName != uint32(CLASS_TINKER) + 6)
        return;

    std::array<uint32, MAX_SPELL_EFFECTS> const originalAuras =
        { SPELL_AURA_ADD_FLAT_MODIFIER, SPELL_AURA_ADD_PCT_MODIFIER, SPELL_AURA_ADD_FLAT_MODIFIER };
    std::array<int32, MAX_SPELL_EFFECTS> const originalBasePoints = { 999, 9, 1 };
    for (uint8 index = 0; index < MAX_SPELL_EFFECTS; ++index)
    {
        SpellEffectInfo const& effect = spellInfo->Effects[index];
        if (effect.Effect != SPELL_EFFECT_APPLY_AURA ||
            (effect.ApplyAuraName != originalAuras[index] && effect.ApplyAuraName != SPELL_AURA_DUMMY) ||
            effect.MiscValue != SPELLMOD_DAMAGE || effect.SpellClassMask ||
            effect.BasePoints != originalBasePoints[index] || effect.DieSides != 1)
        {
            LOG_ERROR("module.classless", "CoA: skipped unexpected Scrap resource record {}", spellInfo->Id);
            return;
        }
    }

    for (SpellEffectInfo& effect : spellInfo->Effects)
        effect.ApplyAuraName = SPELL_AURA_DUMMY;
}
}

void ApplyCoATinkerScrapContracts(SpellInfo* spellInfo)
{
    if (!spellInfo)
        return;
    ApplyScrapResourceContract(spellInfo);
    ApplyScrapperContract(spellInfo);
}
