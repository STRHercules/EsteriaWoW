/* Copyright (C) 2016+ AzerothCore, GNU AGPL v3. */

#include "AscensionTalentReplacementData.h"
#include "ClasslessMgr.h"
#include "CoAPort.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "SpellAuras.h"
#include "SpellMgr.h"
#include <algorithm>
#include <map>
#include <set>
#include <vector>

namespace
{
struct ReplacementState : DataMap::Base
{
    bool syncing = false;
    bool started = false;
    size_t spells = 0;
    uint32 level = 0;
    uint64 auras = 0;
};
constexpr char STATE[] = "cw_coa_talent_replacements";

// A replacement is wanted while the Hero owns the parent talent (or holds its aura, for the trap launcher
// kind) and owns the kit of the class the row belongs to. CoA also tied a row to the active specialisation;
// a Hero owns talents, not a specialisation, so owning the parent is the whole test here.
bool ParentOwned(Player* player, AscensionCompatData::TalentReplacement const& entry)
{
    if (!HasCoAKit(player, entry.ClassId))
        return false;
    if (!entry.RequiresAura)
        return player->HasSpell(entry.ParentSpellId);
    Aura const* aura = player->GetAura(entry.ParentSpellId, player->GetGUID());
    return aura && !aura->IsRemoved();
}

uint64 AuraSignature(Player* player)
{
    uint64 signature = 0;
    for (size_t i = 0; i < AscensionCompatData::TalentReplacements.size(); ++i)
        if (AscensionCompatData::TalentReplacements[i].RequiresAura && ParentOwned(player,
            AscensionCompatData::TalentReplacements[i]))
            signature |= uint64(1) << i;
    return signature;
}

class cw_coa_talent_replacements : public PlayerScript
{
public:
    cw_coa_talent_replacements() : PlayerScript("cw_coa_talent_replacements",
        { PLAYERHOOK_ON_LOGIN, PLAYERHOOK_ON_UPDATE }) { }

    void OnPlayerLogin(Player* player) override
    {
        SynchronizeAscensionTalentReplacements(player);
    }

    void OnPlayerUpdate(Player* player, uint32 /*diff*/) override
    {
        SynchronizeAscensionTalentReplacements(player);
    }
};
}

// CoA's AscensionClassService::SynchronizeTalentReplacements: while a Hero owns a replacing talent, the
// spell it replaces is swapped for the rank spell its level allows, and those rank spells are learned and
// forgotten with it.
uint32 SynchronizeAscensionTalentReplacements(Player* player)
{
    if (!player || !sClasslessMgr->cfg.coaEnable || !sClasslessMgr->cfg.coaReplacements)
        return 0;
    // a Hero with no CoA kit that never had a replacement has nothing to do or undo
    if (!sClasslessMgr->OwnedCoAClassMask(player) && !player->CustomData.Get<ReplacementState>(STATE))
        return 0;
    ReplacementState* state = player->CustomData.GetDefault<ReplacementState>(STATE);
    uint64 const auras = AuraSignature(player);
    if (state->syncing || (state->started && state->spells == player->GetSpellMap().size() &&
        state->level == player->GetLevel() && state->auras == auras))
        return 0;
    state->syncing = true;

    std::set<uint32> candidates;
    std::map<uint32, uint32> replacements;
    for (auto const& entry : AscensionCompatData::TalentReplacements)
    {
        uint32 replacement = 0;
        bool const allowed = ParentOwned(player, entry);
        for (auto const& rank : entry.Ranks)
        {
            if (!rank.SpellId)
                continue;
            candidates.insert(rank.SpellId);
            if (allowed && rank.RequiredLevel <= player->GetLevel() && sSpellMgr->GetSpellInfo(rank.SpellId))
                replacement = rank.SpellId;
        }
        for (auto const& [id, data] : player->GetSpellMap())
        {
            if (sSpellMgr->GetFirstSpellInChain(id) != entry.OriginalSpellId)
                continue;
            replacements.try_emplace(id, 0);
            if (replacement && player->HasActiveSpell(id))
                replacements[id] = replacement;
        }
    }

    std::set<uint32> desired;
    for (auto const& [id, replacement] : replacements)
    {
        if (replacement)
            desired.insert(replacement);
        if (player->GetTemporarySpellReplacement(id) != replacement)
            player->SetTemporarySpellReplacement(id, 0);
    }

    for (uint32 id : candidates)
    {
        if (desired.count(id) || !player->HasSpell(id))
            continue;
        bool const neededByHigherRank = std::any_of(desired.begin(), desired.end(), [id](uint32 rank)
        {
            return sSpellMgr->GetFirstSpellInChain(id) == sSpellMgr->GetFirstSpellInChain(rank) &&
                sSpellMgr->GetSpellRank(id) < sSpellMgr->GetSpellRank(rank);
        });
        if (!neededByHigherRank)
            player->removeSpell(id, SPEC_MASK_ALL, true);
    }

    uint32 learned = 0;
    for (uint32 id : desired)
        if (player->GetSpellMap().find(id) == player->GetSpellMap().end())
        {
            player->learnSpellWithoutAnnouncement(id);
            if (player->HasSpell(id))
                ++learned;
        }

    bool barChanged = false;
    for (auto const& [id, replacement] : replacements)
    {
        player->SetTemporarySpellReplacement(id, replacement);
        if (!replacement)
            continue;
        for (uint8 button = 0; button < MAX_ACTION_BUTTONS; ++button)
        {
            ActionButton const* action = player->GetActionButton(button);
            if (action && action->GetType() == ACTION_BUTTON_SPELL && action->GetAction() == id)
            {
                player->addActionButton(button, replacement, ACTION_BUTTON_SPELL);
                barChanged = true;
            }
        }
    }
    if (barChanged)
        player->SendInitialActionButtons();

    state->syncing = false;
    state->started = true;
    state->spells = player->GetSpellMap().size();
    state->level = player->GetLevel();
    state->auras = auras;
    return learned;
}

void AddCoAReplacementScripts()
{
    new cw_coa_talent_replacements();
}
