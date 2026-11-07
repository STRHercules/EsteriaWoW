// Server side of the GM Tool Chest (Addons/EsteriaToolChest in wowdecomp). Requests arrive as self-whispered addon
// messages, "ESTC\t<op>\t<args>", and every one is checked against the account's security here: the client hiding the
// panel is only cosmetic. Placement and moving go through the ordinary chat commands, which keep their own checks.
#include "Chat.h"
#include "Config.h"
#include "Creature.h"
#include "DBCStores.h"
#include "DatabaseEnv.h"
#include "GameObject.h"
#include "Log.h"
#include "Map.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "SpellInfo.h"
#include "SpellMgr.h"
#include "StringConvert.h"
#include "Tokenize.h"
#include "Util.h"
#include "WorldPacket.h"
#include "WorldSession.h"

#include <algorithm>
#include <cmath>
#include <map>
#include <vector>

namespace
{
    constexpr char PREFIX[] = "ESTC\t";
    constexpr size_t SEARCH_LIMIT = 60;
    constexpr size_t NEAR_LIMIT = 40;
    constexpr size_t MAX_HELP = 180; // keeps a row inside the client's 255 byte addon message

    struct Column { std::string name; std::string type; };

    void Send(Player* player, std::string const& body)
    {
        WorldPacket data;
        ChatHandler::BuildChatPacket(data, CHAT_MSG_WHISPER, LANG_ADDON, player, player, PREFIX + body);
        player->GetSession()->SendPacket(&data);
    }

    std::string Clean(std::string s)
    {
        for (char& c : s)
            if (c == '\t' || c == '\n' || c == '\r' || c == '|')
                c = ' ';
        return s;
    }

    std::string Lower(std::string s)
    {
        std::transform(s.begin(), s.end(), s.begin(), [](unsigned char c) { return char(std::tolower(c)); });
        return s;
    }

    // The editable fields are whatever the table has, so a schema change can't leave a field out. These names are
    // also the whitelist for writes: a client column is only ever used after an exact match here.
    std::vector<Column> const& Columns(std::string const& table)
    {
        static std::map<std::string, std::vector<Column>> cache;
        std::vector<Column>& columns = cache[table];
        if (columns.empty())
            if (QueryResult result = WorldDatabase.Query("SHOW COLUMNS FROM `{}`", table))
                do
                {
                    Field* f = result->Fetch();
                    std::string name = f[0].Get<std::string>();
                    if (name != "entry" && name != "VerifiedBuild")
                        columns.push_back({ name, f[1].Get<std::string>() });
                } while (result->NextRow());
        return columns;
    }

    // A stored value as text; "" when the row does not exist. Undo sends this back, and "" removes the row again.
    std::string ReadValue(std::string_view table, std::string_view owner, uint32 ownerId, std::string_view key, uint32 keyId, std::string const& column)
    {
        std::string where = Acore::StringFormat("`{}` = {}", owner, ownerId);
        if (!key.empty())
            where += Acore::StringFormat(" AND `{}` = {}", key, keyId);
        QueryResult result = WorldDatabase.Query("SELECT CAST(`{}` AS CHAR) FROM `{}` WHERE {}", column, table, where);
        return result ? Clean(result->Fetch()[0].Get<std::string>()) : "";
    }

    // Empty string when the value suits the column's type, otherwise why not. The SQL literal comes back in `sql`.
    std::string Validate(std::string const& type, std::string const& value, std::string& sql)
    {
        if (type.find("char") != std::string::npos)
        {
            size_t open = type.find('(');
            size_t max = open == std::string::npos ? 64 : Acore::StringTo<size_t>(std::string_view(type).substr(open + 1, type.find(')') - open - 1)).value_or(64);
            if (value.size() > max)
                return "too long";
            std::string escaped = value;
            WorldDatabase.EscapeString(escaped);
            sql = "'" + escaped + "'";
            return "";
        }
        if (type.find("float") != std::string::npos || type.find("double") != std::string::npos)
        {
            Optional<float> parsed = Acore::StringTo<float>(value);
            if (!parsed || !std::isfinite(*parsed))
                return "not a number";
            sql = Acore::StringFormat("{}", *parsed);
            return "";
        }

        bool isUnsigned = type.find("unsigned") != std::string::npos;
        int bits = type.find("tinyint") == 0 ? 8 : type.find("smallint") == 0 ? 16 : type.find("mediumint") == 0 ? 24 : 32;
        int64 lo = isUnsigned ? 0 : -(int64(1) << (bits - 1));
        int64 hi = isUnsigned ? (int64(1) << bits) - 1 : (int64(1) << (bits - 1)) - 1;
        Optional<int64> parsed = Acore::StringTo<int64>(value);
        if (!parsed || *parsed < lo || *parsed > hi)
            return Acore::StringFormat("must be a whole number from {} to {}", lo, hi);
        sql = std::to_string(*parsed);
        return "";
    }

    void SendCommands(Player* player)
    {
        uint32 security = player->GetSession()->GetSecurity();
        // shortcut: lists what the `command` table knows at the account's security; the server still decides on run.
        if (QueryResult result = WorldDatabase.Query("SELECT name, security, help FROM command WHERE security <= {} ORDER BY name", security))
            do
            {
                Field* f = result->Fetch();
                std::string help = Clean(f[2].Get<std::string>());
                if (help.size() > MAX_HELP)
                    help = help.substr(0, MAX_HELP) + "...";
                Send(player, "c\t" + Clean(f[0].Get<std::string>()) + "\t" + help);
            } while (result->NextRow());
        Send(player, "c.");
    }

    void SearchNpcs(Player* player, std::string const& term)
    {
        Optional<uint32> entry = Acore::StringTo<uint32>(term);
        std::string lower = Lower(term);
        std::vector<CreatureTemplate const*> found;
        for (auto const& [id, cinfo] : *sObjectMgr->GetCreatureTemplates())
            if (entry ? id == *entry : Lower(cinfo.Name).find(lower) != std::string::npos)
                found.push_back(&cinfo);
        std::sort(found.begin(), found.end(), [](auto* a, auto* b) { return a->Entry < b->Entry; });
        if (found.size() > SEARCH_LIMIT)
            found.resize(SEARCH_LIMIT);
        for (CreatureTemplate const* c : found)
            Send(player, Acore::StringFormat("n\t{}\t{}\t{}\t{}\t{}", c->Entry, uint32(c->minlevel), uint32(c->maxlevel), Clean(c->Name), Clean(c->SubName)));
        Send(player, "n.");
    }

    void SearchObjects(Player* player, std::string const& term)
    {
        Optional<uint32> entry = Acore::StringTo<uint32>(term);
        std::string lower = Lower(term);
        std::vector<GameObjectTemplate const*> found;
        for (auto const& [id, got] : *sObjectMgr->GetGameObjectTemplates())
            if (entry ? id == *entry : Lower(got.name).find(lower) != std::string::npos)
                found.push_back(&got);
        std::sort(found.begin(), found.end(), [](auto* a, auto* b) { return a->entry < b->entry; });
        if (found.size() > SEARCH_LIMIT)
            found.resize(SEARCH_LIMIT);
        for (GameObjectTemplate const* g : found)
            Send(player, Acore::StringFormat("o\t{}\t{}\t{}\t{}", g->entry, g->type, g->displayId, Clean(g->name)));
        Send(player, "o.");
    }

    template <class T>
    void SendNear(Player* player, char const* tag, T const& store)
    {
        struct Row { float dist; std::string text; };
        std::vector<Row> rows;
        for (auto const& [spawnId, object] : store)
        {
            float dist = player->GetDistance(object);
            if (dist <= 200.0f)
                rows.push_back({ dist, Acore::StringFormat("{}\t{}\t{}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.1f}\t{}", tag, spawnId, object->GetEntry(),
                    object->GetPositionX(), object->GetPositionY(), object->GetPositionZ(), object->GetOrientation(), dist, Clean(object->GetName())) });
        }
        std::sort(rows.begin(), rows.end(), [](Row const& a, Row const& b) { return a.dist < b.dist; });
        if (rows.size() > NEAR_LIMIT)
            rows.resize(NEAR_LIMIT);
        for (Row const& row : rows)
            Send(player, row.text);
        Send(player, std::string(tag) + ".");
    }

    void SendFields(Player* player, std::string const& table, uint32 entry, char const* tag)
    {
        std::string select;
        std::vector<Column> const& columns = Columns(table);
        for (Column const& c : columns)
            select += (select.empty() ? "CAST(`" : ", CAST(`") + c.name + "` AS CHAR)";
        QueryResult result = WorldDatabase.Query("SELECT {} FROM `{}` WHERE entry = {}", select, table, entry);
        if (!result)
        {
            Send(player, std::string(tag) + "!\tNo such entry: " + std::to_string(entry));
            return;
        }
        Field* f = result->Fetch();
        for (size_t i = 0; i < columns.size(); ++i)
            Send(player, std::string(tag) + "\t" + columns[i].name + "\t" + Clean(f[i].Get<std::string>()));
        Send(player, std::string(tag) + ".\t" + std::to_string(entry));
    }

    void WriteField(Player* player, std::string const& table, uint32 entry, std::string const& column, std::string const& value)
    {
        std::vector<Column> const& columns = Columns(table);
        auto it = std::find_if(columns.begin(), columns.end(), [&](Column const& c) { return c.name == column; });
        std::string sql;
        std::string problem = it == columns.end() ? "unknown field" : Validate(it->type, value, sql);
        bool isNpc = table == "creature_template";
        bool exists = isNpc ? sObjectMgr->GetCreatureTemplate(entry) != nullptr : sObjectMgr->GetGameObjectTemplate(entry) != nullptr;
        if (problem.empty() && !exists)
            problem = "no such entry";
        if (!problem.empty())
        {
            Send(player, "w!\t" + Clean(column) + "\t" + problem);
            return;
        }

        std::string old = ReadValue(table, "entry", entry, "", 0, column);
        LOG_INFO("module", "ToolChest: account {} ({}) set {}.{} of entry {} to {}", player->GetSession()->GetAccountId(), player->GetName(), table, column, entry, sql);
        // Direct: the reload just below has to read this value back.
        WorldDatabase.DirectExecute("UPDATE `{}` SET `{}` = {} WHERE entry = {}", table, column, sql, entry);
        if (isNpc)
        {
            WorldDatabasePreparedStatement* stmt = WorldDatabase.GetPreparedStatement(WORLD_SEL_CREATURE_TEMPLATE);
            stmt->SetData(0, entry);
            if (PreparedQueryResult row = WorldDatabase.Query(stmt))
            {
                sObjectMgr->LoadCreatureTemplate(row->Fetch(), true);
                sObjectMgr->CheckCreatureTemplate(const_cast<CreatureTemplate*>(sObjectMgr->GetCreatureTemplate(entry)));
            }
        }
        else
            // shortcut: there is no single-entry loader for objects, so this rereads the table; add one if saves hitch.
            sObjectMgr->LoadGameObjectTemplate();
        Send(player, "w\t" + column + "\t" + Clean(value) + "\t" + old);
    }

    // Rows hanging off a template or spawn, shown in the editor as "table.key.column". `key` is empty for one-row tables.
    struct Related
    {
        char const* table;
        char const* owner;
        char const* key;
        uint32 lo, hi;
        std::vector<std::string> columns;
    };

    std::vector<Related> const& AllRelated()
    {
        static std::vector<Related> const related =
        {
            { "creature_template_model", "CreatureID", "Idx", 0, 3, { "CreatureDisplayID", "DisplayScale", "Probability" } },
            { "creature_equip_template", "CreatureID", "ID", 1, 3, { "ItemID1", "ItemID2", "ItemID3" } },
            { "creature_template_spell", "CreatureID", "Index", 0, 7, { "Spell" } },
            { "creature_template_resistance", "CreatureID", "School", 1, 6, { "Resistance" } },
            { "gameobject_template_addon", "entry", "", 0, 0, { "faction", "flags", "mingold", "maxgold", "artkit0", "artkit1", "artkit2", "artkit3" } },
            { "creature", "guid", "", 0, 0, { "phaseMask", "spawntimesecs", "wander_distance", "MovementType", "equipment_id", "npcflag", "unit_flags", "dynamicflags", "Comment" } },
            { "gameobject", "guid", "", 0, 0, { "phaseMask", "spawntimesecs", "animprogress", "state", "Comment" } },
        };
        return related;
    }

    Related const* FindRelated(std::string_view table)
    {
        for (Related const& r : AllRelated())
            if (table == r.table)
                return &r;
        return nullptr;
    }

    void SendRelated(Player* player, char const* tableName, uint32 owner, char const* tag)
    {
        Related const* r = FindRelated(tableName);
        for (uint32 key = r->lo; key <= r->hi; ++key)
            for (std::string const& column : r->columns)
                Send(player, Acore::StringFormat("{}\t{}.{}.{}\t{}", tag, r->table, key, column, ReadValue(r->table, r->owner, owner, r->key, key, column)));
    }

    void ReloadNpcSlots(uint32 entry)
    {
        CreatureTemplate* cinfo = const_cast<CreatureTemplate*>(sObjectMgr->GetCreatureTemplate(entry));
        if (!cinfo)
            return;
        cinfo->Models.clear();
        if (QueryResult result = WorldDatabase.Query("SELECT CreatureDisplayID, DisplayScale, Probability FROM creature_template_model WHERE CreatureID = {} ORDER BY Idx", entry))
            do
            {
                Field* f = result->Fetch();
                if (sCreatureDisplayInfoStore.LookupEntry(f[0].Get<uint32>()))
                    cinfo->Models.emplace_back(f[0].Get<uint32>(), f[1].Get<float>() > 0.0f ? f[1].Get<float>() : 1.0f, f[2].Get<float>());
            } while (result->NextRow());

        for (auto& spell : cinfo->spells)
            spell = 0;
        if (QueryResult result = WorldDatabase.Query("SELECT `Index`, Spell FROM creature_template_spell WHERE CreatureID = {}", entry))
            do
            {
                uint8 index = result->Fetch()[0].Get<uint8>();
                if (index < MAX_CREATURE_SPELLS)
                    cinfo->spells[index] = result->Fetch()[1].Get<uint32>();
            } while (result->NextRow());

        for (auto& resistance : cinfo->resistance)
            resistance = 0;
        if (QueryResult result = WorldDatabase.Query("SELECT School, Resistance FROM creature_template_resistance WHERE CreatureID = {}", entry))
            do
            {
                uint8 school = result->Fetch()[0].Get<uint8>();
                if (school < MAX_SPELL_SCHOOL)
                    cinfo->resistance[school] = result->Fetch()[1].Get<int16>();
            } while (result->NextRow());
    }

    template <class T>
    void SetSpawnPhase(T const& range, uint32 phaseMask)
    {
        for (auto it = range.first; it != range.second; ++it)
            it->second->SetPhaseMask(phaseMask, true);
    }

    // Puts a saved row into the running server. Fields the live spawn does not reread apply when it next respawns.
    void ApplyRelated(Player* player, Related const& r, uint32 owner, std::string const& column, std::string const& value)
    {
        std::string_view table = r.table;
        if (table == "creature_template_model" || table == "creature_template_spell" || table == "creature_template_resistance")
            ReloadNpcSlots(owner);
        else if (table == "creature_equip_template")
            // shortcut: no single-entry loader, and a cleared set stays in memory until restart.
            sObjectMgr->LoadEquipmentTemplates();
        else if (table == "gameobject_template_addon")
            sObjectMgr->LoadGameObjectTemplateAddons();
        else if (table == "creature")
        {
            CreatureData& data = sObjectMgr->NewOrExistCreatureData(owner);
            if (column == "phaseMask") data.phaseMask = Acore::StringTo<uint32>(value).value_or(data.phaseMask);
            else if (column == "spawntimesecs") data.spawntimesecs = Acore::StringTo<uint32>(value).value_or(data.spawntimesecs);
            else if (column == "wander_distance") data.wander_distance = Acore::StringTo<float>(value).value_or(data.wander_distance);
            else if (column == "MovementType") data.movementType = Acore::StringTo<uint8>(value).value_or(data.movementType);
            else if (column == "equipment_id") data.equipmentId = Acore::StringTo<int8>(value).value_or(data.equipmentId);
            else if (column == "npcflag") data.npcflag = Acore::StringTo<uint32>(value).value_or(data.npcflag);
            else if (column == "unit_flags") data.unit_flags = Acore::StringTo<uint32>(value).value_or(data.unit_flags);
            else if (column == "dynamicflags") data.dynamicflags = Acore::StringTo<uint32>(value).value_or(data.dynamicflags);
            if (column == "phaseMask")
                SetSpawnPhase(player->GetMap()->GetCreatureBySpawnIdStore().equal_range(owner), data.phaseMask);
        }
        else if (table == "gameobject")
        {
            GameObjectData const* cached = sObjectMgr->GetGameObjectData(owner);
            if (!cached)
                return;
            GameObjectData& data = const_cast<GameObjectData&>(*cached);
            if (column == "phaseMask") data.phaseMask = Acore::StringTo<uint32>(value).value_or(data.phaseMask);
            else if (column == "spawntimesecs") data.spawntimesecs = Acore::StringTo<int32>(value).value_or(data.spawntimesecs);
            else if (column == "animprogress") data.animprogress = Acore::StringTo<uint32>(value).value_or(data.animprogress);
            else if (column == "state") data.go_state = GOState(Acore::StringTo<uint32>(value).value_or(uint32(data.go_state)));
            if (column == "phaseMask")
                SetSpawnPhase(player->GetMap()->GetGameObjectBySpawnIdStore().equal_range(owner), data.phaseMask);
        }
    }

    // A bad id in these tables can crash clients or the server, so they are checked against the real stores.
    std::string CheckReference(std::string_view table, std::string const& column, std::string const& value)
    {
        uint32 id = Acore::StringTo<uint32>(value).value_or(0);
        if (column == "CreatureDisplayID" && !sCreatureDisplayInfoStore.LookupEntry(id))
            return "no such display id";
        if (table == "creature_template_spell" && id && !sSpellMgr->GetSpellInfo(id))
            return "no such spell";
        if (table == "creature_equip_template" && id && !sObjectMgr->GetItemTemplate(id))
            return "no such item";
        return "";
    }

    // `field` is "table.key.column".
    void WriteRow(Player* player, uint32 owner, std::string const& field, std::string const& value)
    {
        std::vector<std::string_view> parts = Acore::Tokenize(field, '.', true);
        Related const* r = parts.size() == 3 ? FindRelated(parts[0]) : nullptr;
        uint32 key = r ? Acore::StringTo<uint32>(parts[1]).value_or(UINT32_MAX) : 0;
        std::string column = r ? std::string(parts[2]) : "";
        if (!r || key < r->lo || key > r->hi || std::find(r->columns.begin(), r->columns.end(), column) == r->columns.end())
        {
            Send(player, "w!\t" + Clean(field) + "\tunknown field");
            return;
        }

        std::string_view table = r->table;
        bool hasKey = r->key[0] != 0;
        bool remove = hasKey && value.empty();
        bool isSpawn = table == "creature" || table == "gameobject";
        std::string where = Acore::StringFormat("`{}` = {}", r->owner, owner);
        if (hasKey)
            where += Acore::StringFormat(" AND `{}` = {}", r->key, key);
        bool exists = bool(WorldDatabase.Query("SELECT 1 FROM `{}` WHERE {}", r->table, where));

        std::string sql, problem;
        if (std::string_view(r->owner) == "CreatureID" && !sObjectMgr->GetCreatureTemplate(owner))
            problem = "no such entry";
        else if (table == "gameobject_template_addon" && !sObjectMgr->GetGameObjectTemplate(owner))
            problem = "no such entry";
        else if (isSpawn && !exists)
            problem = "no such spawn";
        else if (!remove)
        {
            std::string type;
            if (QueryResult result = WorldDatabase.Query("SHOW COLUMNS FROM `{}` LIKE '{}'", r->table, column))
                type = result->Fetch()[1].Get<std::string>();
            problem = type.empty() ? "unknown field" : (type == "text" ? "" : Validate(type, value, sql));
            if (type == "text")
            {
                std::string escaped = value;
                WorldDatabase.EscapeString(escaped);
                sql = "'" + escaped + "'";
            }
            if (problem.empty())
                problem = CheckReference(table, column, value);
            if (problem.empty() && !exists && table == "creature_template_model" && column != "CreatureDisplayID")
                problem = "set CreatureDisplayID first";
        }
        if (!problem.empty())
        {
            Send(player, "w!\t" + Clean(field) + "\t" + problem);
            return;
        }

        std::string old = ReadValue(r->table, r->owner, owner, r->key, key, column);
        LOG_INFO("module", "ToolChest: account {} ({}) set {} of {} to {}", player->GetSession()->GetAccountId(), player->GetName(), field, owner, remove ? "(removed)" : sql);
        if (remove)
            WorldDatabase.DirectExecute("DELETE FROM `{}` WHERE {}", r->table, where);
        else if (exists)
            WorldDatabase.DirectExecute("UPDATE `{}` SET `{}` = {} WHERE {}", r->table, column, sql, where);
        else if (hasKey)
        {
            // A new model row needs a usable scale and weight; zero defaults would keep it from ever being picked.
            bool model = table == "creature_template_model";
            WorldDatabase.DirectExecute("INSERT INTO `{}` (`{}`, `{}`, `{}`{}) VALUES ({}, {}, {}{})", r->table, r->owner, r->key, column,
                model ? ", DisplayScale, Probability" : "", owner, key, sql, model ? ", 1, 1" : "");
        }
        else
            WorldDatabase.DirectExecute("INSERT INTO `{}` (`{}`, `{}`) VALUES ({}, {})", r->table, r->owner, column, owner, sql);
        ApplyRelated(player, *r, owner, column, value);
        Send(player, "w\t" + field + "\t" + Clean(value) + "\t" + old);
    }

    void CopyRows(std::string const& table, char const* owner, char const* columns, uint32 from, uint32 to)
    {
        WorldDatabase.DirectExecute("INSERT INTO `{0}` (`{1}`, {2}) SELECT {3}, {2} FROM `{0}` WHERE `{1}` = {4}", table, owner, columns, to, from);
    }

    void Clone(Player* player, std::string const& table, uint32 from)
    {
        bool isNpc = table == "creature_template";
        if (isNpc ? !sObjectMgr->GetCreatureTemplate(from) : !sObjectMgr->GetGameObjectTemplate(from))
        {
            Send(player, "f!\tNo such entry to clone.");
            return;
        }
        QueryResult top = WorldDatabase.Query("SELECT MAX(entry) + 1 FROM `{}`", table);
        uint32 to = top->Fetch()[0].Get<uint32>();
        std::string columns;
        for (Column const& c : Columns(table))
            columns += (columns.empty() ? "`" : ", `") + c.name + "`";
        WorldDatabase.DirectExecute("INSERT INTO `{0}` (entry, {1}) SELECT {2}, {1} FROM `{0}` WHERE entry = {3}", table, columns, to, from);
        LOG_INFO("module", "ToolChest: account {} ({}) cloned {} {} to {}", player->GetSession()->GetAccountId(), player->GetName(), table, from, to);
        if (isNpc)
        {
            CopyRows("creature_template_model", "CreatureID", "Idx, CreatureDisplayID, DisplayScale, Probability", from, to);
            CopyRows("creature_template_spell", "CreatureID", "`Index`, Spell", from, to);
            CopyRows("creature_template_resistance", "CreatureID", "School, Resistance", from, to);
            CopyRows("creature_equip_template", "CreatureID", "ID, ItemID1, ItemID2, ItemID3", from, to);
            WorldDatabasePreparedStatement* stmt = WorldDatabase.GetPreparedStatement(WORLD_SEL_CREATURE_TEMPLATE);
            stmt->SetData(0, to);
            if (PreparedQueryResult row = WorldDatabase.Query(stmt))
                sObjectMgr->LoadCreatureTemplate(row->Fetch(), true);
            ReloadNpcSlots(to);
            sObjectMgr->CheckCreatureTemplate(sObjectMgr->GetCreatureTemplate(to));
            sObjectMgr->LoadEquipmentTemplates();
        }
        else
        {
            CopyRows("gameobject_template_addon", "entry", "faction, flags, mingold, maxgold, artkit0, artkit1, artkit2, artkit3", from, to);
            sObjectMgr->LoadGameObjectTemplate();
            sObjectMgr->LoadGameObjectTemplateAddons();
        }
        Send(player, "cl\t" + std::to_string(to));
    }

    // Name lookups behind the editor's search buttons.
    void Pick(Player* player, std::string_view kind, std::string const& term)
    {
        Optional<uint32> id = Acore::StringTo<uint32>(term);
        std::string lower = Lower(term);
        size_t sent = 0;
        auto offer = [&](uint32 rowId, char const* name)
        {
            if (sent >= SEARCH_LIMIT || !name || (id ? rowId != *id : Lower(name).find(lower) == std::string::npos))
                return;
            ++sent;
            Send(player, "p\t" + std::to_string(rowId) + "\t" + Clean(name));
        };
        if (kind == "spell")
        {
            for (uint32 i = 1; i < sSpellMgr->GetSpellInfoStoreSize(); ++i)
                if (SpellInfo const* spell = sSpellMgr->GetSpellInfo(i))
                    offer(i, spell->SpellName[0]);
        }
        else if (kind == "item")
        {
            for (auto const& [itemId, item] : *sObjectMgr->GetItemTemplateStore())
                offer(itemId, item.Name1.c_str());
        }
        else if (kind == "faction")
        {
            for (uint32 i = 1; i < sFactionTemplateStore.GetNumRows(); ++i)
                if (FactionTemplateEntry const* row = sFactionTemplateStore.LookupEntry(i))
                    if (FactionEntry const* faction = sFactionStore.LookupEntry(row->faction))
                        offer(i, faction->name[0]);
        }
        Send(player, "p.");
    }

    void HandleRequest(Player* player, std::string_view body, uint32 minSecurity)
    {
        if (player->GetSession()->GetSecurity() < minSecurity)
            return; // no reply at all: to a player account the tool chest does not exist

        std::vector<std::string_view> args = Acore::Tokenize(body, '\t', true);
        if (args.empty())
            return;
        std::string_view op = args[0];
        std::string first = args.size() > 1 ? std::string(args[1]) : "";
        uint32 entry = Acore::StringTo<uint32>(first).value_or(0);

        if (op == "hello")
            Send(player, "hello\t" + std::to_string(uint32(player->GetSession()->GetSecurity())));
        else if (op == "commands")
            SendCommands(player);
        else if (op == "npcs" && !first.empty())
            SearchNpcs(player, first);
        else if (op == "objects" && !first.empty())
            SearchObjects(player, first);
        else if (op == "nearnpcs")
            SendNear(player, "N", player->GetMap()->GetCreatureBySpawnIdStore());
        else if (op == "nearobjects")
            SendNear(player, "O", player->GetMap()->GetGameObjectBySpawnIdStore());
        else if (op == "npc" && entry)
        {
            uint32 spawn = args.size() > 2 ? Acore::StringTo<uint32>(args[2]).value_or(0) : 0;
            if (spawn)
                SendRelated(player, "creature", spawn, "f");
            SendRelated(player, "creature_template_model", entry, "f");
            SendRelated(player, "creature_equip_template", entry, "f");
            SendRelated(player, "creature_template_spell", entry, "f");
            SendRelated(player, "creature_template_resistance", entry, "f");
            SendFields(player, "creature_template", entry, "f");
        }
        else if (op == "object" && entry)
        {
            uint32 spawn = args.size() > 2 ? Acore::StringTo<uint32>(args[2]).value_or(0) : 0;
            if (GameObjectTemplate const* got = sObjectMgr->GetGameObjectTemplate(entry))
                if (GameObjectDisplayInfoEntry const* display = sGameObjectDisplayInfoStore.LookupEntry(got->displayId))
                    Send(player, std::string("pv\t") + display->filename);
            if (spawn)
                SendRelated(player, "gameobject", spawn, "f");
            SendRelated(player, "gameobject_template_addon", entry, "f");
            SendFields(player, "gameobject_template", entry, "f");
        }
        else if (op == "setrow" && entry && args.size() >= 3)
            WriteRow(player, entry, std::string(args[2]), args.size() > 3 ? std::string(args[3]) : "");
        else if (op == "clonenpc" && entry)
            Clone(player, "creature_template", entry);
        else if (op == "cloneobject" && entry)
            Clone(player, "gameobject_template", entry);
        else if (op == "pick" && args.size() >= 3)
            Pick(player, first, std::string(args[2]));
        else if ((op == "setnpc" || op == "setobject") && entry && args.size() >= 3)
            WriteField(player, op == "setnpc" ? "creature_template" : "gameobject_template", entry, std::string(args[2]), args.size() > 3 ? std::string(args[3]) : "");
    }

    class ToolChestScript : public PlayerScript
    {
    public:
        ToolChestScript() : PlayerScript("EsteriaToolChest", { PLAYERHOOK_CAN_PLAYER_USE_PRIVATE_CHAT }) { }

        bool OnPlayerCanUseChat(Player* player, uint32 type, uint32 language, std::string& msg, Player* receiver) override
        {
            if (language != LANG_ADDON || type != CHAT_MSG_WHISPER || receiver != player)
                return true;
            std::string_view view = msg;
            if (view.substr(0, sizeof(PREFIX) - 1) != PREFIX)
                return true;
            HandleRequest(player, view.substr(sizeof(PREFIX) - 1), sConfigMgr->GetOption<uint32>("EsteriaToolChest.MinSecurity", SEC_GAMEMASTER));
            return false;
        }
    };
}

void AddSC_esteria_toolchest()
{
    new ToolChestScript();
}
