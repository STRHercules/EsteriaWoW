// SPDX-License-Identifier: GPL-2.0-or-later
#include "Player.h"
#include "Item.h"
#include "ObjectAccessor.h"
#include "Spell.h"
#include "SpellInfo.h"
#include "SpellMgr.h"
#include "Log.h"
#include "Config.h"
#include <mutex>
#include <unordered_map>

namespace
{
bool enabled = true;
enum class Mode { Melee, Ranged };
struct AttackState
{
    ObjectGuid target;
    Mode mode = Mode::Melee;
    uint32 elapsed = 250;
    uint32 settling = 0;
};
std::mutex stateLock;
std::unordered_map<uint32, AttackState> states;
uint32 WeaponSpell(Player* player)
{
    Item* weapon = player->GetWeaponForAttack(RANGED_ATTACK, true);
    if (!weapon) return 0;
    switch (weapon->GetTemplate()->SubClass)
    {
        case ITEM_SUBCLASS_WEAPON_BOW:
        case ITEM_SUBCLASS_WEAPON_GUN:
        // The universal control authorizes dispatch; native Auto Shot preserves
        // spell-family procs and core shot handling without teaching spell 75.
        case ITEM_SUBCLASS_WEAPON_CROSSBOW: return player->HasSpell(970100) ? 75 : 0;
        case ITEM_SUBCLASS_WEAPON_THROWN: return player->HasSpell(970101) ? 970101 : 0;
        case ITEM_SUBCLASS_WEAPON_WAND: return player->HasSpell(970102) ? 970102 : 0;
        default: return 0;
    }
}
bool IsOurs(Spell* spell)
{
    return spell && (spell->GetSpellInfo()->Id == 75 ||
        (spell->GetSpellInfo()->Id >= 970100 && spell->GetSpellInfo()->Id <= 970102));
}
void SetMode(Player* player, Unit* target, Mode mode)
{
    // Arm the response handling before sending any stop packet. No ranged
    // spell starts until the client replies or the transition window ends.
    {
        std::lock_guard<std::mutex> lock(stateLock);
        auto it = states.find(player->GetGUID().GetCounter());
        if (it == states.end()) return;
        it->second.mode = mode;
        it->second.settling = 100;
    }
    if (IsOurs(player->GetCurrentSpell(CURRENT_AUTOREPEAT_SPELL)))
        player->InterruptSpell(CURRENT_AUTOREPEAT_SPELL);
    if (mode == Mode::Ranged)
    {
        // Do not activate melee at range. Keep the server target relationship,
        // but explicitly turn off the client's melee loop exactly once.
        player->ClearUnitState(UNIT_STATE_MELEE_ATTACKING);
        player->Attack(target, false);
        player->SendMeleeAttackStop(target);
        player->SetSheath(SHEATH_STATE_RANGED);
    }
    else
    {
        player->Attack(target, true);
        player->SetSheath(SHEATH_STATE_MELEE);
    }
    LOG_DEBUG("module.adaptive_autoattack", "Adaptive Auto Attack: mode={} player={}", mode == Mode::Melee ? "melee" : "ranged", player->GetGUID().GetCounter());
}
}

bool AdaptiveAutoAttackEnabled()
{
    return enabled;
}

void InitializeUnifiedAttack()
{
    enabled = sConfigMgr->GetOption<bool>("AdaptiveAutoAttack.Enable", true);
    LOG_INFO("server.loading", "Adaptive Auto Attack: module loaded (no-core prototype 1; stock wand timing).");
}
void RangedAutoStop(Player* player)
{
    bool managed;
    { std::lock_guard<std::mutex> lock(stateLock); managed = states.erase(player->GetGUID().GetCounter()) != 0; }
    Spell* current = player->GetCurrentSpell(CURRENT_AUTOREPEAT_SPELL);
    // Native Auto Shot outside our controller must still work, including when disabled.
    if (IsOurs(current) && (managed || current->GetSpellInfo()->Id != 75))
        player->InterruptSpell(CURRENT_AUTOREPEAT_SPELL);
}
// Called only for a ranged-cancel packet. A melee-stop command always follows
// the core AttackStop path and clears the entire mode, including during setup.
void RangedAutoClientCancel(Player* player)
{
    {
        std::lock_guard<std::mutex> lock(stateLock);
        if (states.find(player->GetGUID().GetCounter()) == states.end()) return;
    }
    if (!player->GetCurrentSpell(CURRENT_AUTOREPEAT_SPELL))
    {
        std::lock_guard<std::mutex> lock(stateLock);
        auto it = states.find(player->GetGUID().GetCounter());
        if (it != states.end() && it->second.settling)
        {
            it->second.settling = 0;
            LOG_DEBUG("module.adaptive_autoattack", "Adaptive Auto Attack: transition acknowledged player={}", player->GetGUID().GetCounter());
            return;
        }
    }
    // Never swallow a cancellation while a ranged repeat is actually active.
    player->AttackStop();
    RangedAutoStop(player);
}
void RangedAutoStart(Player* player, Unit* target)
{
    RangedAutoStop(player);
    if (!AdaptiveAutoAttackEnabled())
    { if (target) player->Attack(target, true); return; }
    if (!target || !player->IsAlive() || player->IsMounted() || !player->IsValidAttackTarget(target)) return;
    Mode mode = player->IsWithinMeleeRange(target) || !WeaponSpell(player) ? Mode::Melee : Mode::Ranged;
    {
        std::lock_guard<std::mutex> lock(stateLock);
        states[player->GetGUID().GetCounter()] = {target->GetGUID(), mode, 250, 0};
    }
    SetMode(player, target, mode);
    if (player->GetVictim() != target) RangedAutoStop(player);
}
void RangedAutoUpdate(Player* player, uint32 diff)
{
    if (!AdaptiveAutoAttackEnabled())
    { RangedAutoStop(player); return; }
    AttackState state;
    bool due = false;
    {
        std::lock_guard<std::mutex> lock(stateLock);
        auto it = states.find(player->GetGUID().GetCounter());
        if (it == states.end()) return;
        it->second.settling = diff >= it->second.settling ? 0 : it->second.settling - diff;
        it->second.elapsed += diff;
        due = it->second.elapsed >= 100;
        if (due) it->second.elapsed = 0;
        state = it->second;
    }
    Unit* target = ObjectAccessor::GetUnit(*player, state.target);
    if (!target || player->GetVictim() != target || !player->IsAlive() || !target->IsAlive()
        || player->IsMounted() || !player->IsValidAttackTarget(target))
    { RangedAutoStop(player); return; }
    // Native AttackStop no longer calls into this module. Check the victim on
    // every update before the core processes another autorepeat shot.
    if (!due) return;
    uint32 id = WeaponSpell(player);
    Mode desired = player->IsWithinMeleeRange(target) || !id ? Mode::Melee : Mode::Ranged;
    if (desired != state.mode) { SetMode(player, target, desired); return; }
    if (desired == Mode::Melee) return;
    if (state.settling) return;
    Spell* current = player->GetCurrentSpell(CURRENT_AUTOREPEAT_SPELL);
    if (current)
    {
        if (!IsOurs(current)) { RangedAutoStop(player); return; }
        if (current->GetSpellInfo()->Id == id && current->m_targets.GetUnitTargetGUID() == state.target) return;
        SetMode(player, target, Mode::Ranged);
        return;
    }
    if (player->isMoving() || player->IsNonMeleeSpellCast(false, false, true)) return;
    SpellInfo const* info = sSpellMgr->GetSpellInfo(id);
    if (!info) return;
    SpellCastTargets targets;
    targets.SetUnitTarget(target);
    Spell* spell = new Spell(player, info, TRIGGERED_NONE);
    spell->InitExplicitTargets(targets);
    if (spell->CheckCast(true) != SPELL_CAST_OK) { delete spell; return; }
    LOG_DEBUG("module.adaptive_autoattack", "Adaptive Auto Attack: begin repeating spell={} player={}", id, player->GetGUID().GetCounter());
    spell->prepare(&targets);
}
