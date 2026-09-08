/*
 * Copyright (C) 2016+ AzerothCore <www.azerothcore.org>, released under GNU AGPL v3 license: https://github.com/azerothcore/azerothcore-wotlk/blob/master/LICENSE-AGPL3
 */

#include "ConfigValueCache.h"
#include "GameGraveyard.h"
#include "Opcodes.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "WorldPacket.h"

enum CorpseRespawnConfig
{
    ENABLE,
    SEND_GRAVEYARD_MARKER,
    NUM_CONFIGS
};

class CorpseRespawnConfigData : public ConfigValueCache<CorpseRespawnConfig>
{
public:
    CorpseRespawnConfigData() : ConfigValueCache(CorpseRespawnConfig::NUM_CONFIGS) { }

    void BuildConfigCache() override
    {
        SetConfigValue<bool>(CorpseRespawnConfig::ENABLE, "CorpseRespawn.Enable", true);
        SetConfigValue<bool>(CorpseRespawnConfig::SEND_GRAVEYARD_MARKER, "CorpseRespawn.SendGraveyardMarker", true);
    }
};

static CorpseRespawnConfigData corpseRespawnConfigData;

class CorpseRespawnPlayerScript : public PlayerScript
{
public:
    CorpseRespawnPlayerScript() : PlayerScript("CorpseRespawnPlayerScript", { PLAYERHOOK_CAN_REPOP_AT_GRAVEYARD }) { }

    bool OnPlayerCanRepopAtGraveyard(Player* player) override
    {
        if (!corpseRespawnConfigData.GetConfigValue<bool>(CorpseRespawnConfig::ENABLE))
            return true;

        if (player->InBattleground() || player->InArena())
            return true;

        if (corpseRespawnConfigData.GetConfigValue<bool>(CorpseRespawnConfig::SEND_GRAVEYARD_MARKER))
        {
            if (GraveyardStruct const* gy = sGraveyard->GetClosestGraveyard(player, player->GetTeamId()))
            {
                WorldPacket data(SMSG_DEATH_RELEASE_LOC, 4 * 4);
                data << gy->Map;
                data << gy->x;
                data << gy->y;
                data << gy->z;
                player->SendDirectMessage(&data);
            }
        }

        return false;
    }
};

class CorpseRespawnWorldScript : public WorldScript
{
public:
    CorpseRespawnWorldScript() : WorldScript("CorpseRespawnWorldScript", { WORLDHOOK_ON_BEFORE_CONFIG_LOAD }) { }

    void OnBeforeConfigLoad(bool reload) override
    {
        corpseRespawnConfigData.Initialize(reload);
    }
};

void AddCorpseRespawnScripts()
{
    new CorpseRespawnPlayerScript();
    new CorpseRespawnWorldScript();
}
