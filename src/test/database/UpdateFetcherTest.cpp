#include "UpdateFetcher.h"

#include <gtest/gtest.h>

#include <chrono>
#include <filesystem>
#include <fstream>

TEST(UpdateFetcherTest, ModuleFoundationsPrecedeDatedUpdates)
{
    namespace fs = std::filesystem;
    fs::path root = fs::temp_directory_path() /
        ("esteria-update-test-" + std::to_string(std::chrono::steady_clock::now().time_since_epoch().count()));
    ASSERT_TRUE(fs::create_directory(root));
    struct Cleanup
    {
        fs::path path;
        ~Cleanup()
        {
            fs::remove_all(path);
        }
    } cleanup{root};

    fs::path source = root / "updates/repo";
    fs::path module = source / "modules/example/data/sql/db-characters";
    fs::create_directories(module / "base");
    fs::create_directories(module / "updates");
    std::ofstream(module / "base/nemesis_system.sql") << "SELECT 1;\n";
    std::ofstream(module / "updates/2026_03_22_nemesis_last_seen.sql") << "SELECT 2;\n";

    std::vector<std::string> directories{"/modules/example/data/sql/db-characters"};
    std::vector<std::string> applied;
    UpdateFetcher fetcher(source, [](std::string const&) { },
        [&](fs::path const& file) { applied.push_back(file.filename().string()); },
        [](std::string const&) { return QueryResult{}; }, "characters", &directories);
    fetcher.Update(false, true, false, 0);
    EXPECT_EQ(applied, (std::vector<std::string>{"nemesis_system.sql", "2026_03_22_nemesis_last_seen.sql"}));
}
