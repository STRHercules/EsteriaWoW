/*
 * mod-wxl-dbc — apply continuation files after LoadDBCStores().
 */

#include "WxlDbcLoader.h"

#include "WxlDbcRegistry.h"
#include "WxlDbcScan.h"

#include "Config.h"
#include "DBCStores.h"
#include "Log.h"
#include "World.h"

#include <filesystem>

namespace ModWxlDbc
{
    void ApplyContinuations()
    {
        if (!sConfigMgr->GetOption<bool>("WxlDbc.Enable", true))
        {
            LOG_INFO("module.wxl-dbc", "Disabled via WxlDbc.Enable.");
            return;
        }

        InitDbcRegistry();

        std::string const continuationSubPath =
            sConfigMgr->GetOption<std::string>("WxlDbc.ContinuationPath", "dbc-continuations");

        std::filesystem::path const root =
            std::filesystem::path(sWorld->GetDataPath()) / continuationSubPath;

        if (!std::filesystem::exists(root))
        {
            LOG_INFO("module.wxl-dbc", "No continuation folder at {} (nothing to apply).", root.string());
            return;
        }

        std::vector<ContinuationEntry> const entries = DiscoverContinuations(root);
        if (entries.empty())
        {
            LOG_INFO("module.wxl-dbc", "No continuation files found under {}.", root.string());
            return;
        }

        LOG_INFO("module.wxl-dbc", "Applying {} continuation file(s) from {}...", entries.size(), root.string());

        uint32 filesApplied = 0;
        uint32 rowsInjected = 0;

        for (ContinuationEntry const& entry : entries)
        {
            uint32 const injected = InjectContinuationByTable(entry.baseDbcFile.c_str(), entry.path.string().c_str());
            if (injected == 0)
            {
                LOG_WARN("module.wxl-dbc", "No rows injected from {} (unknown table or load error).", entry.path.string());
                continue;
            }

            ++filesApplied;
            rowsInjected += injected;
            LOG_INFO("module.wxl-dbc", "  {} -> {} row(s) into {}", entry.path.filename().string(), injected, entry.baseDbcFile);
        }

        RebuildDbcDerivedIndexes();

        LOG_INFO("module.wxl-dbc", "Done. {} file(s), {} row(s) injected. Base data/dbc/ files were not modified.",
            filesApplied, rowsInjected);
    }
}
