// SPDX-License-Identifier: GPL-2.0-or-later
#include "ScriptMgr.h"
#include "Player.h"
#include "SharedDefines.h"
#include "Config.h"

void InitializeUnifiedAttack();
void RangedAutoStop(Player*);
void RegisterAdaptiveAttackHooks();
bool AdaptiveAutoAttackEnabled();

class adaptive_autoattack_player : public PlayerScript
{
public:
    adaptive_autoattack_player() : PlayerScript("adaptive_autoattack_player", {
        PLAYERHOOK_ON_LOGIN, PLAYERHOOK_ON_LOGOUT, PLAYERHOOK_ON_UPDATE_SKILL }) { }
    static void Sync(Player* player)
    {
        if (!AdaptiveAutoAttackEnabled()) return;
        // Everyone receives the controls. Equipment/proficiency restrictions
        // remain enforced by the core; these grants never teach weapon skills.
        if (!player->HasSpell(970100)) player->learnSpell(970100);
        if (!player->HasSpell(970101)) player->learnSpell(970101);
        if (!player->HasSpell(970102)) player->learnSpell(970102);
    }
    void OnPlayerLogin(Player* player) override { Sync(player); }
    void OnPlayerLogout(Player* player) override { RangedAutoStop(player); }
    void OnPlayerUpdateSkill(Player* player, uint32, uint32, uint32, uint32, uint32) override { Sync(player); }
};
void Addmod_adaptive_autoattackScripts()
{
    InitializeUnifiedAttack();
    new adaptive_autoattack_player();
    RegisterAdaptiveAttackHooks();
}
