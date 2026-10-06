#include "BrokenRacialEffects.h"

#include "Player.h"
#include "ScriptMgr.h"
#include "SpellAuraEffects.h"
#include "SpellAuras.h"
#include "SpellScript.h"

enum BrokenRacials : uint32
{
    SPELL_BROKEN_SALVAGER       = 110001,
    SPELL_BROKEN_KROKUL_CUNNING = 110002,
    SPELL_BROKEN_FEL_SCARRED    = 110003,
    SPELL_BROKEN_ECHO_NAARU     = 110004,
};

// Race id this install targets. Change this (and the race mask 8192 in the SQL)
// if your Broken race is not race 14.
uint32 const BROKEN_RACE_ID = 14;

class broken_racials : public PlayerScript
{
public:
    broken_racials() : PlayerScript("broken_racials") { }

    void OnPlayerLogin(Player* player) override
    {
        if (player->getRace() != BROKEN_RACE_ID)
            return;

        uint32 const staleRacials[] = { 20549, 20550, 20551, 20552 };
        for (uint32 spell : staleRacials)
            if (player->HasSpell(spell))
                player->removeSpell(spell, SPEC_MASK_ALL, false);

        uint32 const brokenRacials[] =
        {
            SPELL_BROKEN_SALVAGER,
            SPELL_BROKEN_KROKUL_CUNNING,
            SPELL_BROKEN_FEL_SCARRED,
            SPELL_BROKEN_ECHO_NAARU,
        };
        for (uint32 spell : brokenRacials)
            if (!player->HasSpell(spell))
                player->learnSpell(spell);
    }

    void OnPlayerBeforeDurabilityRepair(Player* player, ObjectGuid /*npcGUID*/, ObjectGuid /*itemGUID*/,
        float& discountMod, uint8 /*guildBank*/) override
    {
        if (player->getRace() == BROKEN_RACE_ID)
            discountMod = Acore::BrokenRacialEffects::ApplySalvagerRepairDiscount(discountMod);
    }
};

class spell_broken_echo_of_the_naaru : public AuraScript
{
    PrepareAuraScript(spell_broken_echo_of_the_naaru);

    void HandleApply(AuraEffect const* aurEff, AuraEffectHandleModes /*mode*/)
    {
        Player* player = GetTarget()->ToPlayer();
        if (!player || player->getRace() != BROKEN_RACE_ID)
            return;

        const_cast<AuraEffect*>(aurEff)->SetAmount(Acore::BrokenRacialEffects::EchoHealPerTick(player->GetMaxHealth()));
    }

    void Register() override
    {
        OnEffectApply += AuraEffectApplyFn(spell_broken_echo_of_the_naaru::HandleApply,
            EFFECT_0, SPELL_AURA_PERIODIC_HEAL, AURA_EFFECT_HANDLE_REAL);
    }
};

void AddBrokenRacialsScripts()
{
    new broken_racials();
    RegisterSpellScript(spell_broken_echo_of_the_naaru);
}
