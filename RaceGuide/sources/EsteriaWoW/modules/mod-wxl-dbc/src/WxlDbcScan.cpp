/*
 * mod-wxl-dbc — discover WXL continuation files on disk.
 */

#include "WxlDbcScan.h"

#include <algorithm>
#include <cctype>
#include <fstream>
#include <unordered_map>

namespace ModWxlDbc
{
    bool ParseContinuationFileName(std::string const& fileName, ContinuationEntry& out);

    namespace
    {
        std::string ToLower(std::string value)
        {
            for (char& c : value)
                c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
            return value;
        }

        std::string FileNameOnly(std::filesystem::path const& path)
        {
            return path.filename().string();
        }

        void TrimLine(std::string& line)
        {
            while (!line.empty() && (line.back() == '\r' || line.back() == ' ' || line.back() == '\t'))
                line.pop_back();

            size_t pos = 0;
            while (pos < line.size() && (line[pos] == ' ' || line[pos] == '\t'))
                ++pos;

            line = line.substr(pos);
        }

        bool EndsWithIgnoreCase(std::string const& value, std::string const& suffix)
        {
            if (value.size() < suffix.size())
                return false;

            return ToLower(value.substr(value.size() - suffix.size())) == ToLower(suffix);
        }

        bool IsBackupOrEditorArtifact(std::string const& fileName)
        {
            static char const* const kIgnoredSuffixes[] = {
                ".bak",
                ".backup",
                ".old",
                ".orig",
                ".tmp",
            };

            for (char const* suffix : kIgnoredSuffixes)
            {
                if (EndsWithIgnoreCase(fileName, suffix))
                    return true;
            }

            return false;
        }

        bool IsValidProjectSlug(std::string const& project)
        {
            if (project.empty())
                return false;

            for (char c : project)
            {
                if (std::isalnum(static_cast<unsigned char>(c)) || c == '-' || c == '_')
                    continue;
                return false;
            }

            return true;
        }

        bool IsContinuationCandidate(std::string const& fileName)
        {
            ContinuationEntry probe{};
            return ParseContinuationFileName(fileName, probe);
        }
    }

    std::string BaseDbcFileFromStem(std::string const& tableStem)
    {
        return tableStem + ".dbc";
    }

    bool ParseContinuationFileName(std::string const& fileName, ContinuationEntry& out)
    {
        if (IsBackupOrEditorArtifact(fileName))
            return false;

        size_t const dbcPos = fileName.find(".dbc");
        if (dbcPos == std::string::npos || dbcPos + 4 >= fileName.size())
            return false;

        char const tierChar = fileName[dbcPos + 4];
        if (tierChar < '1' || tierChar > '9')
            return false;

        if (dbcPos + 5 >= fileName.size() || fileName[dbcPos + 5] != '-')
            return false;

        std::string const project = fileName.substr(dbcPos + 6);
        if (!IsValidProjectSlug(project))
            return false;

        out.tier = static_cast<uint8_t>(tierChar - '0');
        out.project = project;
        out.baseDbcFile = BaseDbcFileFromStem(fileName.substr(0, dbcPos));
        return true;
    }

    std::vector<ContinuationEntry> DiscoverContinuations(std::filesystem::path const& root)
    {
        std::unordered_map<std::string, ContinuationEntry> entries;

        auto tryAdd = [&](std::filesystem::path const& filePath, int manifestOrder)
        {
            if (!std::filesystem::is_regular_file(filePath))
                return;

            ContinuationEntry entry{};
            if (!ParseContinuationFileName(FileNameOnly(filePath), entry))
                return;

            entry.path = filePath;
            entry.manifestOrder = manifestOrder;

            std::string const key = ToLower(entry.path.lexically_normal().string());
            auto found = entries.find(key);
            if (found == entries.end())
            {
                entries.emplace(key, std::move(entry));
                return;
            }

            if (manifestOrder >= 0 && found->second.manifestOrder < 0)
                found->second.manifestOrder = manifestOrder;
        };

        std::filesystem::path const manifestPath = root / "wxl-dbc.manifest";
        if (std::filesystem::exists(manifestPath))
        {
            std::ifstream manifest(manifestPath);
            std::string line;
            int lineOrder = 0;
            while (std::getline(manifest, line))
            {
                TrimLine(line);
                if (line.empty() || line[0] == '#')
                    continue;

                std::filesystem::path relative = line;
                tryAdd(root / relative, lineOrder);
                ++lineOrder;
            }
        }

        if (!std::filesystem::exists(root))
            return {};

        for (auto const& dirEntry : std::filesystem::recursive_directory_iterator(
                 root, std::filesystem::directory_options::skip_permission_denied))
        {
            if (!dirEntry.is_regular_file())
                continue;

            std::string const fileName = dirEntry.path().filename().string();
            if (!IsContinuationCandidate(fileName))
                continue;

            tryAdd(dirEntry.path(), -1);
        }

        std::vector<ContinuationEntry> result;
        result.reserve(entries.size());
        for (auto& [_, entry] : entries)
            result.push_back(std::move(entry));

        std::sort(result.begin(), result.end(),
            [](ContinuationEntry const& a, ContinuationEntry const& b)
            {
                if (a.tier != b.tier)
                    return a.tier < b.tier;

                int const aOrder = a.manifestOrder < 0 ? 0x7FFFFFFF : a.manifestOrder;
                int const bOrder = b.manifestOrder < 0 ? 0x7FFFFFFF : b.manifestOrder;
                if (aOrder != bOrder)
                    return aOrder < bOrder;

                if (ToLower(a.project) != ToLower(b.project))
                    return ToLower(a.project) < ToLower(b.project);

                return ToLower(a.baseDbcFile) < ToLower(b.baseDbcFile);
            });

        return result;
    }
}
