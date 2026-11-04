/*
 * Live aura amounts for CoA tooltips: CoA's client shows an aura's real numbers ($w1..$w3 in its text: Tankard fill,
 * Drunken Frenzy damage, absorb left). The ported AscensionAuraAmounts sends them on SMSG_ESTERIA_AURA_AMOUNT;
 * this sends them only for the imported spells whose tooltip names one, so stock auras cost nothing extra.
 */

#include "AscensionAuraAmounts.h"
#include "ClasslessMgr.h"
#include "CoAAuraAmountSpells.h"
#include "CoAPort.h"
#include "ScriptMgr.h"
#include "SpellAuras.h"
#include "SpellInfo.h"
#include "Unit.h"
#include <algorithm>

namespace
{
bool ShowsAmount(AuraApplication const* application)
{
    uint32 const spell = application->GetBase()->GetId();
    return std::binary_search(CoAAuraAmountSpells.begin(), CoAAuraAmountSpells.end(), spell);
}

class cw_coa_aura_amounts : public UnitScript
{
public:
    cw_coa_aura_amounts() : UnitScript("cw_coa_aura_amounts", true, { UNITHOOK_ON_SEND_AURA_UPDATE }) { }

    void OnSendAuraUpdate(Unit* target, Player* receiver, AuraApplication const* application, bool remove) override
    {
        if (!target || !sClasslessMgr->cfg.coaEnable)
            return;
        if (application)
        {
            if (ShowsAmount(application))
                SendAscensionAuraAmounts(target, receiver, application, remove);
            return;
        }
        for (auto const& [slot, visible] : *target->GetVisibleAuras())
            if (ShowsAmount(visible))
                SendAscensionAuraAmounts(target, receiver, visible, false);
    }
};
}

void AddCoAAuraAmountScripts()
{
    new cw_coa_aura_amounts();
}
