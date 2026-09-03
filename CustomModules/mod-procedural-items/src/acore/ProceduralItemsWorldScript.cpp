#include "Config.h"
#include "Log.h"
#include "ScriptMgr.h"

namespace
{
bool g_enabled = true;
bool g_requireClientPool = true;
}

class ProceduralItemsWorldScript final : public WorldScript
{
public:
    ProceduralItemsWorldScript() : WorldScript("ProceduralItemsWorldScript", {
        WORLDHOOK_ON_BEFORE_CONFIG_LOAD,
        WORLDHOOK_ON_STARTUP
    }) { }

    void OnBeforeConfigLoad(bool /*reload*/) override
    {
        g_enabled = sConfigMgr->GetOption<bool>("ProceduralItems.Enable", true);
        g_requireClientPool = sConfigMgr->GetOption<bool>("ProceduralItems.RequireClientPreparedPool", true);
    }

    void OnStartup() override
    {
        if (!g_enabled)
        {
            LOG_INFO("module", "mod-procedural-items is disabled.");
            return;
        }

        LOG_INFO("module", "mod-procedural-items scaffold enabled.");
        LOG_INFO("module", "Client-prepared item pool enforcement: {}", g_requireClientPool ? "ON" : "OFF");
        LOG_WARN("module", "Live runtime ItemTemplate registration is intentionally not enabled in scaffold v0.1; see docs/RUNTIME_REGISTRY.md.");
    }
};

void AddProceduralItemsWorldScript()
{
    new ProceduralItemsWorldScript();
}
