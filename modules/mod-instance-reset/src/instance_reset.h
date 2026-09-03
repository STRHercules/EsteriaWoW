#include "Chat.h"
#include "Configuration/Config.h"
#include "GossipDef.h"
#include "Language.h"
#include "Opcodes.h"
#include "Player.h"
#include "ScriptedGossip.h"
#include "ScriptMgr.h"
#include "WorldPacket.h"
#include "WorldSession.h"

void GossipSetText(Player* player, std::string message, uint32 textID);

bool enable = true;
uint8 transactionType = 0;
uint16 count = 26;
uint32 token = 49426;
uint32 money = 10000000;

class InstanceResetAnnouncer : public PlayerScript
{
public:
    InstanceResetAnnouncer() : PlayerScript("InstanceResetAnnouncer", {
        PLAYERHOOK_ON_LOGIN
    }) {}

    void OnPlayerLogin(Player* player) override;
};

class InstanceReset : public CreatureScript
{
public:
    InstanceReset() : CreatureScript("instance_reset") {}

    bool OnGossipHello(Player* player, Creature* creature) override;
    bool OnGossipSelect(Player* player, Creature* creature, uint32 /*sender*/, uint32 action) override;
};

class InstanceResetWorldConfig : public WorldScript
{
public:
    InstanceResetWorldConfig() : WorldScript("InstanceResetWorldConfig", {
        WORLDHOOK_ON_BEFORE_CONFIG_LOAD
    }) { }

    void OnBeforeConfigLoad(bool /*reload*/) override;
};

void AddInstanceResetScripts()
{
    new InstanceReset();
    new InstanceResetAnnouncer();
    new InstanceResetWorldConfig();
}
