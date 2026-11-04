/* Copyright (C) 2016+ AzerothCore, GNU AGPL v3. */

#include "AscensionPooledVitality.h"
#include "ClasslessMgr.h"
#include "CoAPort.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "Spell.h"
#include "SpellInfo.h"
#include <algorithm>

namespace
{
using namespace AscensionBloodmage;

// These offsets precede ordinary spellmods; readiness belongs to this cast's snapshot.
constexpr bool ApplyEmpowerment(Empowerment kind, uint8 op, double& basevalue, int32& totalflat)
{
    if ((op == SPELLMOD_CASTING_TIME && kind == Mend) ||
        (op == SPELLMOD_COST && (kind == CrimsonTide || kind == Fleshcraft || kind == Apotheosis)))
    {
        basevalue = 0;
        return true;
    }

    if (op == SPELLMOD_RADIUS && kind == CrimsonTide)
        totalflat += 5;
    if (kind == AnimatedBlood)
    {
        if (op == SPELLMOD_EFFECT1)
            totalflat += 1;
        if (op == SPELLMOD_DURATION)
            totalflat += 5000;
    }
    if (op == SPELLMOD_COOLDOWN && kind == Transfusion)
        basevalue = std::max(0.0, basevalue - 60000.0);
    return false;
}

static_assert([]
{
    double value = 1500;
    int32 flat = 300;
    return ApplyEmpowerment(Mend, SPELLMOD_CASTING_TIME, value, flat) && value == 0 && flat == 300;
}());
static_assert([]
{
    double value = 1500;
    int32 flat = 300;
    return !ApplyEmpowerment(None, SPELLMOD_CASTING_TIME, value, flat) && value == 1500 && flat == 300;
}());
static_assert([]
{
    double value = 45000;
    int32 flat = 0;
    return !ApplyEmpowerment(Transfusion, SPELLMOD_COOLDOWN, value, flat) && value == 0 && flat == 0;
}());
static_assert([]
{
    double value = 10000;
    int32 flat = 2000;
    return !ApplyEmpowerment(AnimatedBlood, SPELLMOD_DURATION, value, flat) && value == 10000 && flat == 7000;
}());

class cw_coa_empowerment : public PlayerScript
{
public:
    cw_coa_empowerment() : PlayerScript("cw_coa_empowerment", { PLAYERHOOK_ON_APPLY_SPELL_MOD }) { }

    void OnPlayerApplySpellMod(Player* player, SpellInfo const* info, uint8 op, Spell* spell,
        bool temporaryPet, double& basevalue, int32& totalflat, float& /*totalmul*/, bool& handled) override
    {
        if (handled || !sClasslessMgr->cfg.coaEnable || !player || !info || !spell || temporaryPet ||
            !HasCoAKit(player, CLASS_SON_OF_ARUGAL) || info->SpellFamilyName != BloodmageSpellFamily ||
            spell->GetCaster() != player || spell->IsTriggered() || spell->GetSpellInfo()->Id != info->Id)
            return;

        Empowerment const kind = GetEmpowerment(info->Id);
        if (kind != None && spell->GetScriptValue(PooledVitalityTalent) == kind)
            handled = ApplyEmpowerment(kind, op, basevalue, totalflat);
    }
};
}

void AddCoAEmpowermentScripts()
{
    new cw_coa_empowerment();
}
