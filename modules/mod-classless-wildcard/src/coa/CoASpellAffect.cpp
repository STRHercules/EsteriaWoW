/* Copyright (C) 2016+ AzerothCore, GNU AGPL v3. */

#include "ClasslessMgr.h"
#include "CoASpellAffectData.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "SpellInfo.h"
#include "SpellMgr.h"
#include <algorithm>

namespace
{
constexpr bool MatchesSpellAffect(int32 target, uint32 spell, uint32 firstRank)
{
    return target < 0 ? uint32(-int64(target)) == firstRank : uint32(target) == spell;
}

static_assert(MatchesSpellAffect(100, 100, 0));
static_assert(!MatchesSpellAffect(100, 101, 100));
static_assert(MatchesSpellAffect(-100, 101, 100));
static_assert(!MatchesSpellAffect(-100, 100, 0));

class cw_coa_spell_affect : public GlobalScript
{
public:
    cw_coa_spell_affect()
        : GlobalScript("cw_coa_spell_affect", { GLOBALHOOK_ON_SPELL_MOD_FAMILY_MASK }) { }

    void OnSpellModFamilyMask(SpellInfo const* affectSpell, SpellInfo const* checkSpell,
        SpellModifier const* mod, bool& affected) override
    {
        if (!sClasslessMgr->cfg.coaEnable || !affectSpell || !checkSpell || !mod || mod->mask ||
            affectSpell->SpellFamilyName < 18 || affectSpell->SpellFamilyName > 38)
            return;

        auto const end = CoASpellAffect::Targets.end();
        auto entry = std::lower_bound(CoASpellAffect::Targets.begin(), end, mod->spellId,
            [](CoASpellAffect::Entry const& value, uint32 modifier) { return value.modifier < modifier; });
        if (entry == end || entry->modifier != mod->spellId)
            return;

        affected = false;
        uint32 const firstRank = sSpellMgr->GetFirstSpellInChain(checkSpell->Id);
        for (; entry != end && entry->modifier == mod->spellId; ++entry)
            if (MatchesSpellAffect(entry->target, checkSpell->Id, firstRank))
            {
                affected = true;
                return;
            }
    }
};
}

void AddCoASpellAffectScripts()
{
    new cw_coa_spell_affect();
}
