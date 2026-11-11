#include "Incarnations.h"

#include "Chat.h"
#include "DatabaseEnv.h"
#include "Log.h"
#include "Player.h"
#include "StringConvert.h"
#include "Tokenize.h"

#include <set>
#include <unordered_map>

namespace
{
    struct Category
    {
        uint8 kind = 0;
        uint32 key = 0;
        uint32 classMask = 0;
    };

    std::unordered_map<uint32, Category> s_categories;
    std::unordered_map<uint32, uint32> s_formCategory;
    std::unordered_map<uint32, uint32> s_creatureCategory;
    std::set<std::pair<uint32, uint32>> s_looks;

    void Reply(Player* player, std::string const& body)
    {
        // CHAT_MSG_WHISPER, never CHAT_MSG_ADDON: see FreebornClaim.h (the client rejects type 0xFF).
        WorldPacket data;
        ChatHandler::BuildChatPacket(data, CHAT_MSG_WHISPER, LANG_ADDON, player, player,
            std::string(Incarnations::AddonPrefix) + "\t" + body);
        player->GetSession()->SendPacket(&data);
    }
}

void Incarnations::LoadFromDB()
{
    s_categories.clear();
    s_formCategory.clear();
    s_creatureCategory.clear();
    s_looks.clear();

    if (QueryResult result = WorldDatabase.Query("SELECT `id`, `kind`, `key`, `class_mask` FROM `esteria_incarnation_category`"))
    {
        do
        {
            Field* fields = result->Fetch();
            Category category{fields[1].Get<uint8>(), fields[2].Get<uint32>(), fields[3].Get<uint32>()};
            uint32 id = fields[0].Get<uint32>();
            if (category.kind == KIND_FORM)
                s_formCategory[category.key] = id;
            else if (category.kind == KIND_SUMMON)
                s_creatureCategory[category.key] = id;
            else
                continue;
            s_categories[id] = category;
        } while (result->NextRow());
    }

    if (QueryResult result = WorldDatabase.Query("SELECT `form`, `category` FROM `esteria_incarnation_form`"))
    {
        do
        {
            Field* fields = result->Fetch();
            auto category = s_categories.find(fields[1].Get<uint32>());
            if (category != s_categories.end() && category->second.kind == KIND_FORM)
                s_formCategory[fields[0].Get<uint32>()] = category->first;
        } while (result->NextRow());
    }

    if (QueryResult result = WorldDatabase.Query("SELECT `category`, `display` FROM `esteria_incarnation`"))
    {
        do
        {
            Field* fields = result->Fetch();
            if (s_categories.count(fields[0].Get<uint32>()))
                s_looks.emplace(fields[0].Get<uint32>(), fields[1].Get<uint32>());
        } while (result->NextRow());
    }

    LOG_INFO("server.loading", ">> Loaded {} incarnation categories and {} looks", s_categories.size(), s_looks.size());
}

uint32 Incarnations::CategoryForForm(uint32 form)
{
    auto found = s_formCategory.find(form);
    return found == s_formCategory.end() ? 0 : found->second;
}

uint32 Incarnations::CategoryForCreature(uint32 entry)
{
    auto found = s_creatureCategory.find(entry);
    return found == s_creatureCategory.end() ? 0 : found->second;
}

bool Incarnations::IsLook(uint32 category, uint32 display, uint8 playerClass)
{
    auto found = s_categories.find(category);
    if (found == s_categories.end() || !playerClass || !(found->second.classMask & (1u << (playerClass - 1))))
        return false;
    return !display || s_looks.count({category, display});
}

bool Incarnations::HandleAddonMessage(Player* player, std::string const& msg)
{
    std::string const prefix = std::string(AddonPrefix) + "\t";
    if (!player || msg.compare(0, prefix.size(), prefix) != 0)
        return false;

    std::vector<std::string_view> args = Acore::Tokenize(std::string_view(msg).substr(prefix.size()), '\t', false);
    if (args.empty())
        return true;

    if (args[0] == "list")
    {
        std::string body = "list\t";
        for (auto const& [category, display] : player->GetIncarnations())
            body += std::to_string(category) + ":" + std::to_string(display) + ",";
        Reply(player, body);
        return true;
    }

    if (args[0] == "set" && args.size() == 3)
    {
        Optional<uint32> category = Acore::StringTo<uint32>(args[1]);
        Optional<uint32> display = Acore::StringTo<uint32>(args[2]);
        if (category && display && IsLook(*category, *display, player->getClass()) && player->SetIncarnation(*category, *display))
            Reply(player, "ok\t" + std::to_string(*category) + "\t" + std::to_string(*display));
        else
            Reply(player, "err\t" + std::string(args[1]));
        return true;
    }

    return true;
}
