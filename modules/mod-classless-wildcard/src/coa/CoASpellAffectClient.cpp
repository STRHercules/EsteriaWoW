/* Copyright (C) 2016+ AzerothCore, GNU AGPL v3. */

#include "ClasslessMgr.h"
#include "AscensionPooledVitality.h"
#include "CoAPort.h"
#include "CoASpellAffectData.h"
#include "Opcodes.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "SpellAuras.h"
#include "SpellInfo.h"
#include "SpellMgr.h"
#include "WorldPacket.h"
#include <algorithm>
#include <map>
#include <tuple>

namespace
{
enum DirectModifierType : uint8
{
    DIRECT_FLAT = 3,
    DIRECT_PERCENT = 4,
    DIRECT_RESET = 5,
    DIRECT_COST = 6
};
using Totals = std::map<std::tuple<uint32, uint8, uint8>, int32>;
struct DirectModifiers : DataMap::Base
{
    Totals totals;
};
constexpr char STATE[] = "cw_coa_direct_modifiers";

void Send(Player* player, uint8 type, uint32 modifier = 0, uint8 op = 0, int32 value = 0)
{
    WorldPacket packet(SMSG_ESTERIA_SPELL_MOD, 11);
    packet << type << uint8(0) << op << value << modifier;
    player->SendDirectMessage(&packet);
}

void Synchronize(Player* player)
{
    if (!player)
        return;
    Totals totals;
    if (sClasslessMgr->cfg.coaEnable)
        for (uint8 op = 0; op < MAX_CLIENT_SPELLMOD; ++op)
            for (SpellModifier const* mod : player->GetSpellModList(op))
            {
                if (mod->mask || (mod->ownerAura && mod->ownerAura->IsRemoved()))
                    continue;
                auto const end = CoASpellAffect::Targets.end();
                auto entry = std::lower_bound(CoASpellAffect::Targets.begin(), end, mod->spellId,
                    [](CoASpellAffect::Entry const& row, uint32 id) { return row.modifier < id; });
                if (entry != end && entry->modifier == mod->spellId)
                    totals[{mod->spellId, op, uint8(mod->type == SPELLMOD_PCT ? DIRECT_PERCENT : DIRECT_FLAT)}]
                        += mod->value;
            }
    // Script costs and load-time contracts are authoritative on the server. Send
    // complete prices for owned CoA spells instead of approximating them twice.
    if (sClasslessMgr->cfg.coaEnable && sClasslessMgr->OwnedCoAClassMask(player))
        for (auto const& [id, known] : player->GetSpellMap())
        {
            if (!known || known->State == PLAYERSPELL_REMOVED || !known->IsInSpec(player->GetActiveSpec()))
                continue;
            SpellInfo const* info = sSpellMgr->GetSpellInfo(id);
            if (!info || info->IsPassive() || info->SpellFamilyName < 18 || info->SpellFamilyName > 38)
                continue;
            int32 cost = info->CalcPowerCost(player, info->GetSchoolMask());
            using namespace AscensionBloodmage;
            if (info->SpellFamilyName == BloodmageSpellFamily && info->PowerType == POWER_RAGE &&
                player->IsAlive() && player->IsInWorld() &&
                HasCoAKit(player, CLASS_SON_OF_ARUGAL) && player->HasAura(PooledVitalityTalent) &&
                !player->HasAura(CursedForm))
                if (Aura const* pool = player->GetAura(PooledVitality, player->GetGUID());
                    pool && pool->GetStackAmount() >= 10)
                {
                    Empowerment const kind = GetEmpowerment(id);
                    if (kind == CrimsonTide || kind == Fleshcraft || kind == Apotheosis)
                        cost = 0;
                }
            totals[{id, SPELLMOD_COST, DIRECT_COST}] = std::max(cost, 0);
        }
    DirectModifiers* previous = player->CustomData.Get<DirectModifiers>(STATE);
    if ((!previous && totals.empty()) || (previous && previous->totals == totals))
        return;
    previous = player->CustomData.GetDefault<DirectModifiers>(STATE);
    previous->totals = totals;
    Send(player, DIRECT_RESET);
    for (auto const& [key, value] : totals)
    {
        auto const& [modifier, op, type] = key;
        Send(player, type, modifier, op, value);
    }
}

class cw_coa_direct_modifiers : public PlayerScript
{
public:
    cw_coa_direct_modifiers() : PlayerScript("cw_coa_direct_modifiers",
        { PLAYERHOOK_ON_LOGIN, PLAYERHOOK_ON_UPDATE }) { }

    void OnPlayerLogin(Player* player) override
    {
        // CharacterHandler resends its reset after OnPlayerLogin; send this snapshot on the first world tick.
        player->CustomData.Erase(STATE);
    }
    void OnPlayerUpdate(Player* player, uint32 /*diff*/) override
    {
        Synchronize(player);
    }
};
}

void AddCoASpellAffectClientScripts()
{
    new cw_coa_direct_modifiers();
}
