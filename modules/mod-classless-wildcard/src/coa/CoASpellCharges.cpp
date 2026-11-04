/* Copyright (C) 2016+ AzerothCore, GNU AGPL v3. */

#include "ClasslessMgr.h"
#include "CoASpellChargesData.h"
#include "SpellInfo.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "SpellMgr.h"
#include <algorithm>

void ApplyCoASpellChargeMetadata(SpellInfo* info)
{
    if (!sClasslessMgr->cfg.coaEnable || !info || info->SpellFamilyName < 18 || info->SpellFamilyName > 38)
        return;

    auto const end = CoASpellCharges::Entries.end();
    auto entry = std::lower_bound(CoASpellCharges::Entries.begin(), end, info->Id,
        [](CoASpellCharges::Entry const& row, uint32 spell) { return row.spell < spell; });
    if (entry == end || entry->spell != info->Id)
        return;

    info->MaxCharges = entry->maximum;
    info->ChargeRecoveryTime = entry->recovery;
    info->ChargeRecoveryKey = entry->root;
    info->ChargeCategoryId = entry->category;
}

namespace
{
class cw_coa_charge_learning : public PlayerScript
{
public:
    cw_coa_charge_learning() : PlayerScript("cw_coa_charge_learning", { PLAYERHOOK_ON_LEARN_SPELL }) { }

    void OnPlayerLearnSpell(Player* player, uint32 id) override
    {
        if (SpellInfo const* info = sSpellMgr->GetSpellInfo(id); info && info->MaxCharges)
            player->SendSpellChargeState(id);
    }
};
}

void AddCoASpellChargeScripts()
{
    new cw_coa_charge_learning();
}
