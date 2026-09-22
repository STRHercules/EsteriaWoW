/*
 * Darkfallen racial behaviour that DBC data alone cannot express.
 *
 * "Children of the Night" (spell 110042) carries the passive stealth-detection and
 * stealth-level effects. Its two movement effects need scripts because stock 3.3.5 has
 * no stealth-only speed aura, and run-speed auras take the highest amount instead of
 * stacking:
 *
 *   - While stealthed: spell 110043 (+10% run speed) is applied when any stealth aura
 *     lands on the player and removed once the last one is gone. Without the gate the
 *     aura would be a permanent movement buff.
 *   - While dead: spell 110044 is cast on ghost release and removed on resurrection,
 *     mirroring how the core handles the Night Elf "Wisp Spirit" (spell 20584). Living
 *     ghosts already run at +50% (spell 8326), and the speed aura is a max(), so the
 *     Darkfallen spell carries +90%: the stock +50% plus the racial +40%.
 */

#include "Player.h"
#include "ScriptMgr.h"
#include "SharedDefines.h"
#include "SpellAuras.h"
#include "SpellInfo.h"

namespace
{
    enum DarkfallenSpells : uint32
    {
        SPELL_CHILDREN_STEALTH_SPEED = 110043,
        SPELL_CHILDREN_GHOST_SPEED   = 110044,
    };

    bool IsDarkfallen(Unit const* unit)
    {
        if (!unit || !unit->IsPlayer())
            return false;

        uint32 race = unit->ToPlayer()->getRace(true);
        return race == RACE_DARKFALLEN_ALLIANCE || race == RACE_DARKFALLEN_HORDE;
    }

    bool IsStealthAura(Aura const* aura)
    {
        return aura && aura->GetSpellInfo() && aura->GetSpellInfo()->HasAura(SPELL_AURA_MOD_STEALTH);
    }
}

class darkfallen_children_of_the_night : public UnitScript
{
public:
    darkfallen_children_of_the_night() : UnitScript("darkfallen_children_of_the_night", true,
        { UNITHOOK_ON_AURA_APPLY, UNITHOOK_ON_AURA_REMOVE }) { }

    void OnAuraApply(Unit* unit, Aura* aura) override
    {
        if (!IsStealthAura(aura) || !IsDarkfallen(unit))
            return;

        unit->CastSpell(unit, SPELL_CHILDREN_STEALTH_SPEED, true);
    }

    void OnAuraRemove(Unit* unit, AuraApplication* aurApp, AuraRemoveMode /*mode*/) override
    {
        if (!aurApp || !IsStealthAura(aurApp->GetBase()) || !IsDarkfallen(unit))
            return;

        // Remaining stealth auras (Vanish, Camouflage, ...) keep the speed bonus alive.
        if (!unit->HasAuraType(SPELL_AURA_MOD_STEALTH))
            unit->RemoveAurasDueToSpell(SPELL_CHILDREN_STEALTH_SPEED);
    }
};

class darkfallen_ghost_speed : public PlayerScript
{
public:
    darkfallen_ghost_speed() : PlayerScript("darkfallen_ghost_speed") { }

    void OnPlayerReleasedGhost(Player* player) override
    {
        if (IsDarkfallen(player))
            player->CastSpell(player, SPELL_CHILDREN_GHOST_SPEED, true);
    }

    void OnPlayerResurrect(Player* player, float /*restore_percent*/, bool& /*applySickness*/) override
    {
        if (IsDarkfallen(player))
            player->RemoveAurasDueToSpell(SPELL_CHILDREN_GHOST_SPEED);
    }
};

void AddSC_darkfallen_racials()
{
    new darkfallen_children_of_the_night();
    new darkfallen_ghost_speed();
}
