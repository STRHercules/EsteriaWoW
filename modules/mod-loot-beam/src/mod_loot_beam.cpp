/*
 * mod-loot-beam
 *
 * Server half of the wxl-loot-beam client extension: the beacon the client draws over a lootable
 * corpse is tinted by the *server's* view of that corpse's loot, so it is already the right colour
 * before the loot window is ever opened.
 *
 * The stock 3.3.5a client only learns a corpse's loot when loot is requested for it, which is why
 * the extension could originally only colour a body after it had been opened. This module closes
 * that gap without a custom opcode, an addon message or a client patch: at the moment a creature
 * dies its loot has just been rolled, so the best item quality in that loot is written into the
 * corpse's own UNIT_FIELD_PADDING update field. The field is one this core never writes for
 * non-player objects, it lies inside UNIT_END so the client keeps it, and it is UF_FLAG_PUBLIC so
 * it is sent to every nearby player. The extension reads it straight out of the descriptor block.
 *
 * Encoding: the best item quality (0..7) is stored as quality + 1, so the untouched default of 0
 * means "no server hint" and the client falls back to the loot it learns when the window opens.
 *
 * This program is free software: you can redistribute it and/or modify it under the terms of the
 * GNU General Public License as published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

#include "Config.h"
#include "Creature.h"
#include "ItemTemplate.h"
#include "Log.h"
#include "LootMgr.h"
#include "ObjectMgr.h"
#include "ScriptMgr.h"
#include "Unit.h"

#include <algorithm>

namespace
{
    // The slot the client extension reads. UNIT_FIELD_PADDING is the one unit field this core
    // leaves to non-player objects; players use it for the extended-appearance byte, creatures do
    // not use it at all. It is within UNIT_END (so the client keeps it in the descriptor block) and
    // UF_FLAG_PUBLIC (so it reaches nearby players). uint16 to match Object::SetUInt32Value.
    constexpr uint16 kHintField = UNIT_FIELD_PADDING;

    // The highest item quality the client's colour table knows (ITEM_QUALITY_HEIRLOOM == 7). A
    // drop table that somehow reports more is clamped to the top colour rather than sent raw.
    constexpr int kMaxQuality = 7;

    // The hint for a corpse whose loot held money but no gear: it has no quality to describe it, so
    // the client shows its own "currency" tier. It sits one past the quality range (value 9).
    constexpr uint32 kCurrencyHint = kMaxQuality + 2;

    bool g_enabled = true;

    // The highest item quality in the corpse's rolled loot, or -1 when it holds no gear at all.
    // The loot is generated in Unit::Kill before this hook runs, so this reads the real drop table
    // (chance rolls and references already applied), not the template.
    int BestLootQuality(Creature const* creature)
    {
        int best = -1;
        for (LootItem const& item : creature->loot.items)
        {
            if (!item.itemid)
                continue;

            if (ItemTemplate const* proto = sObjectMgr->GetItemTemplate(item.itemid))
                best = std::max(best, int(proto->Quality));
        }
        return best;
    }
}

class LootBeamUnitScript : public UnitScript
{
public:
    LootBeamUnitScript() : UnitScript("LootBeamUnitScript", true, { UNITHOOK_ON_UNIT_DEATH }) { }

    void OnUnitDeath(Unit* unit, Unit* /*killer*/) override
    {
        if (!g_enabled || !unit || !unit->IsCreature())
            return;

        Creature* creature = unit->ToCreature();
        int const  best     = BestLootQuality(creature);

        // quality + 1 keeps 0 free for "no hint"; a corpse with no gear (or an item the world does
        // not know) falls back to the currency hint when it still holds money, so the client can tint
        // it as a money drop, and to 0 otherwise.
        uint32 hint = 0;
        if (best >= 0)
            hint = uint32(std::min(best, kMaxQuality)) + 1;
        else if (creature->loot.gold > 0)
            hint = kCurrencyHint;

        creature->SetUInt32Value(kHintField, hint);
    }
};

class LootBeamWorldScript : public WorldScript
{
public:
    LootBeamWorldScript() : WorldScript("LootBeamWorldScript", { WORLDHOOK_ON_AFTER_CONFIG_LOAD }) { }

    void OnAfterConfigLoad(bool /*reload*/) override
    {
        g_enabled = sConfigMgr->GetOption<bool>("LootBeam.Enable", true);
        LOG_INFO("module", "mod-loot-beam: server-driven loot beam colour is {}.", g_enabled ? "enabled" : "disabled");
    }
};

void AddSC_mod_loot_beam()
{
    new LootBeamUnitScript();
    new LootBeamWorldScript();
}
