/*
 * mod-wxl-dbc — WorldScript hook (requires OnAfterLoadDBCStores core patch).
 */

#include "ScriptMgr.h"
#include "WxlDbcLoader.h"

class mod_wxl_dbc_worldscript : public WorldScript
{
public:
    mod_wxl_dbc_worldscript() : WorldScript("mod_wxl_dbc", { WORLDHOOK_ON_AFTER_LOAD_DBC_STORES })
    {
    }

    void OnAfterLoadDBCStores() override
    {
        ModWxlDbc::ApplyContinuations();
    }
};

void AddSC_mod_wxl_dbc()
{
    new mod_wxl_dbc_worldscript();
}
