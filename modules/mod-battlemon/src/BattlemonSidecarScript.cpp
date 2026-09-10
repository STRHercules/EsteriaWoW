#include "BattlemonSidecarServer.h"

#include "ScriptMgr.h"
#include "World.h"

class BattlemonSidecarWorldScript : public WorldScript
{
public:
    BattlemonSidecarWorldScript() : WorldScript("BattlemonSidecarWorldScript", {
        WORLDHOOK_ON_STARTUP,
        WORLDHOOK_ON_SHUTDOWN,
        WORLDHOOK_ON_UPDATE
    }) { }

    void OnStartup() override
    {
        sBattlemonSidecar->LoadConfig();
        sBattlemonSidecar->Start();
    }

    void OnShutdown() override
    {
        sBattlemonSidecar->Stop();
    }

    void OnUpdate(uint32 /*diff*/) override
    {
        sBattlemonSidecar->Update();
    }
};

void AddSC_battlemon_sidecar()
{
    new BattlemonSidecarWorldScript();
}
