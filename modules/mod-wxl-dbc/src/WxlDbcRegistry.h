/*
 * mod-wxl-dbc — registry of server DBC stores.
 */

#ifndef MOD_WXL_DBC_REGISTRY_H
#define MOD_WXL_DBC_REGISTRY_H

#include "Common.h"

#include <functional>
#include <string>
#include <unordered_map>

namespace ModWxlDbc
{
    using ContinuationInjector = std::function<uint32(char const*)>;

    void InitDbcRegistry();
    uint32 InjectContinuationByTable(char const* baseDbcFile, char const* path);
}

#endif
