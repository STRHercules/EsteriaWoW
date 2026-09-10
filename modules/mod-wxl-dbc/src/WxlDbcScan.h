/*
 * mod-wxl-dbc — discover WXL continuation files on disk.
 */

#ifndef MOD_WXL_DBC_SCAN_H
#define MOD_WXL_DBC_SCAN_H

#include <cstdint>
#include <filesystem>
#include <string>
#include <vector>

namespace ModWxlDbc
{
    struct ContinuationEntry
    {
        std::filesystem::path path;
        std::string baseDbcFile; // e.g. "Spell.dbc"
        uint8_t tier = 0;
        std::string project;
        int manifestOrder = -1;
    };

    std::vector<ContinuationEntry> DiscoverContinuations(std::filesystem::path const& root);
    bool ParseContinuationFileName(std::string const& fileName, ContinuationEntry& out);
    std::string BaseDbcFileFromStem(std::string const& tableStem);
}

#endif
