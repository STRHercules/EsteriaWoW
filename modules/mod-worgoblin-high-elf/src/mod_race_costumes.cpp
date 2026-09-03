#include "ScriptMgr.h"
#include "Player.h"
#include "SpellAuras.h"
#include "SpellAuraEffects.h"
#include "SpellScript.h"

#include <cstdint>
#include <map>

namespace
{
    struct GenderedDisplay
    {
        uint32 maleDisplayId;
        uint32 femaleDisplayId;
    };

    // To add a new costume: add a line below, recompile, and make sure
    // the trigger spell's effect is a SPELL_AURA_DUMMY (not Transform) -
    // see the note at the bottom of this file about spell_script_names
    // and the spell's own effect setup.
    std::map<uint32, GenderedDisplay> const CostumeSpells =
    {
        // spellId, { maleDisplayId, femaleDisplayId }
        { 68994,    { 94135,          94136          } }, // Gilnean disguise
        { 110020,   { 20585,          20584          } }, // Tauren disguise
    };

    uint32 GetCostumeDisplayId(uint32 spellId, uint8 gender)
    {
        auto itr = CostumeSpells.find(spellId);
        if (itr == CostumeSpells.end())
            return 0;

        return (gender == GENDER_FEMALE) ? itr->second.femaleDisplayId : itr->second.maleDisplayId;
    }
}

// ============================================================
// Aura script - this aura is a plain SPELL_AURA_DUMMY with no other
// built-in behavior, so there's no competing native handler fighting
// us for control of the model. We own the whole apply/remove cycle:
// snapshot the player's current display ID when the aura lands,
// switch to the gendered costume model, and put the snapshot back
// when the aura is removed. This mirrors how AzerothCore's own
// spell_gen_model_visible script (src/server/scripts/Spells/
// spell_generic.cpp) handles the same kind of "disguise while this
// aura is up" pattern.
// ============================================================

class spell_costume_override : public AuraScript
{
    PrepareAuraScript(spell_costume_override);

    uint32 _previousDisplayId = 0;

    void HandleEffectApply(AuraEffect const* /*aurEff*/, AuraEffectHandleModes /*mode*/)
    {
        Player* player = GetUnitOwner()->ToPlayer();
        if (!player)
            return;

        uint32 displayId = GetCostumeDisplayId(GetId(), player->getGender());
        if (!displayId)
            return;

        _previousDisplayId = player->GetDisplayId();
        player->SetDisplayId(displayId);

        LOG_DEBUG(
            "scripts",
            "Custom costume applied: spell={}, gender={}, display={}",
            GetId(),
            (uint32)player->getGender(),
            displayId
        );
    }

    void HandleEffectRemove(AuraEffect const* /*aurEff*/, AuraEffectHandleModes /*mode*/)
    {
        Player* player = GetUnitOwner()->ToPlayer();
        if (!player)
            return;

        if (_previousDisplayId)
            player->SetDisplayId(_previousDisplayId);

        LOG_DEBUG("scripts", "Custom costume removed: spell={}", GetId());
    }

    void Register() override
    {
        OnEffectApply += AuraEffectApplyFn(
            spell_costume_override::HandleEffectApply,
            EFFECT_0, SPELL_AURA_DUMMY, AURA_EFFECT_HANDLE_REAL
        );
        OnEffectRemove += AuraEffectRemoveFn(
            spell_costume_override::HandleEffectRemove,
            EFFECT_0, SPELL_AURA_DUMMY, AURA_EFFECT_HANDLE_REAL
        );
    }
};

// ============================================================
// Script registration
//
// This binds to whichever spells have a `custom_race_costumes`-style
// spell_script_names row pointing at "spell_costume_override" (same
// requirement as before - see prior messages for the INSERT).
//
// IMPORTANT: each trigger spell's own effect must be changed from
// SPELL_AURA_TRANSFORM to SPELL_AURA_DUMMY (still on EFFECT_0) in
// whatever tool you used to create these custom spells, and the
// client-side DBC re-patched/re-extracted. Otherwise this script
// never fires, since it's listening for a dummy effect that isn't
// there.
// ============================================================

void AddSC_mod_race_costumes()
{
    RegisterSpellScript(spell_costume_override);
}