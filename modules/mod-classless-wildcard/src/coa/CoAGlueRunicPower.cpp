/* Copyright (C) 2016+ AzerothCore, GNU AGPL v3. */

// The Necromancer and the Reaper spend Runic Power. CoA gave those classes the native bar through their class
// table; a Hero is the Paladin chassis, so owning either kit makes Runic Power an active power type with CoA's
// maximum of 100 (stored as 1000), the way the Ranger's Focus is done in CoAGlueRanger.cpp.

#include "ClasslessMgr.h"
#include "CoAPort.h"
#include "Player.h"
#include "ScriptMgr.h"

namespace
{
constexpr float RUNIC_POWER_MAXIMUM = 1000.0f;

bool OwnsRunicKit(Player const* player)
{
    return sClasslessMgr->cfg.coaEnable && player &&
        (HasCoAKit(player, CLASS_NECROMANCER) || HasCoAKit(player, CLASS_REAPER));
}

class cw_coa_runic_power : public PlayerScript
{
public:
    cw_coa_runic_power() : PlayerScript("cw_coa_runic_power", {
        PLAYERHOOK_ON_LOGIN,
        PLAYERHOOK_ON_AFTER_UPDATE_MAX_POWER,
        PLAYERHOOK_ON_PLAYER_HAS_ACTIVE_POWER_TYPE
    }) { }

    bool OnPlayerHasActivePowerType(Player const* player, Powers power) override
    {
        return power == POWER_RUNIC_POWER && OwnsRunicKit(player);
    }

    void OnPlayerAfterUpdateMaxPower(Player* player, Powers& power, float& value) override
    {
        if (power == POWER_RUNIC_POWER && OwnsRunicKit(player))
            value += RUNIC_POWER_MAXIMUM;
    }

    void OnPlayerLogin(Player* player) override
    {
        if (!OwnsRunicKit(player))
            return;

        player->UpdateMaxPower(POWER_RUNIC_POWER);
        player->SetPower(POWER_RUNIC_POWER, 0);
    }
};
}

void AddCoARunicPowerScripts()
{
    new cw_coa_runic_power();
}
