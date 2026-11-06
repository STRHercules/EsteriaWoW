// Esteria housing, Phase 1 slice (wowdecomp docs/housing/). One house per account in a per-house instance of a reused
// interior map, decor as temporary GameObjects, edits over the HousingWire.h opcodes. Everything is off unless
// EsteriaHousing.Enable = 1; with it off both core hooks stay null and the module does nothing.
//
// All state lives on the world thread (PROCESS_THREADUNSAFE packets, gossip, teleports, map enter), so the maps below
// are only guarded against the occasional map-thread caller by one mutex.

#include "Chat.h"
#include "Config.h"
#include "DatabaseEnv.h"
#include "EsteriaHousingHooks.h"
#include "GameObject.h"
#include "GameTime.h"
#include "Group.h"
#include "HousingRooms.h"
#include "HousingRules.h"
#include "InstanceSaveMgr.h"
#include "Log.h"
#include "Map.h"
#include "MapMgr.h"
#include "ObjectMgr.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "ScriptedGossip.h"
#include "WorldPacket.h"
#include "WorldSession.h"
#include <cmath>
#include <sstream>
#include <tuple>
#include <deque>
#include <map>
#include <mutex>
#include <unordered_map>
#include <unordered_set>

namespace
{
    using namespace EsteriaHousingWire;
    namespace Rooms = EsteriaHousing::Rooms;

    struct CatalogEntry
    {
        uint32 decorId = 0, fdid = 0, displayId = 0, goEntry = 0;
        std::string name;
        uint8 category = 0, surface = 0;
        float minScale = 1, maxScale = 1;
    };

    struct RoomTemplate
    {
        uint32 id = 0, mapId = 0;
        float entry[4] = { 0, 0, 0, 0 };
        float min[3] = { 0, 0, 0 }, max[3] = { 0, 0, 0 };
        uint16 maxDecor = 0;
        // Rooms are laid out from here: the entry's x/y on the floor at min_z (make_slice.py writes both from it).
        float Origin(int axis) const { return axis == 2 ? min[2] : entry[axis]; }
    };

    // Retail HouseTheme: the room kit's mesh themes (Generic is the kit itself).
    constexpr uint32 GenericTheme = 3;
    constexpr uint32 StairwellTop = 48; // Stairwell Room (Empty): the floor above a stairwell, built with it
    inline bool IsStairwell(uint32 kind) { return kind == 10 || kind == 50; } // Stairwell (Left) / (Right)
    constexpr int8 MinLevel = -1, MaxLevel = 3; // a basement and four floors

    struct HouseRoom
    {
        uint32 id = 0; // housing_room.room_id
        Rooms::Room layout;
        uint32 theme[3] = { GenericTheme, GenericTheme, GenericTheme }; // walls, floor, ceiling (KitPiece::type - 1)
        bool ceilingHidden = false;
    };

    struct Placed
    {
        uint64 id = 0;
        uint32 decorId = 0;
        float pos[3] = { 0, 0, 0 };
        float yaw = 0;
    };

    struct House
    {
        uint32 id = 0, account = 0, roomTemplate = 0, roomId = 0, revision = 0;
        uint16 maxDecor = 0;
        std::map<uint64, Placed> placed;
        std::vector<HouseRoom> rooms; // slot order; rooms[0] is the room decor rows reference (roomId)
    };

    struct Owned
    {
        uint16 owned = 0, placed = 0;
    };

    struct EditSession
    {
        uint32 lastSeq = 0;
        std::deque<uint64> recent; // ms timestamps of edits in the last second
    };

    struct Config
    {
        bool enabled = false;
        uint32 roomTemplate = 1;
        uint32 plotPrice = 1000000; // copper
        uint16 starterQuantity = 5;
        uint32 editsPerSecond = 8;
        uint32 firstRoomKind = 1; // HouseRoom 1, Square Room (Small)
        uint32 maxRooms = 16;
        uint32 roomPrice = 250000; // copper for a 23 x 23 yd room; others scale by floor area
    };

    std::recursive_mutex s_lock;
    Config s_config;
    bool s_loaded = false;
    std::map<uint32, CatalogEntry> s_catalog;
    std::unordered_map<uint32, RoomTemplate> s_rooms;
    Rooms::Kinds s_kinds; // retail room kinds and their kit pieces
    struct ThemedModels { uint32 solid = 0, door = 0, wide = 0, doorFrame = 0, wideFrame = 0; };
    std::map<std::tuple<uint32, uint32, uint32>, ThemedModels> s_themed; // (kind, piece id, theme) -> models
    std::map<uint32, std::string> s_themes;                             // theme -> name, Generic included
    std::map<std::tuple<uint32, uint32, uint32, uint8>, uint32> s_stairs; // (kind, piece id, theme, variant) -> staircase

    // Neighborhood plots (housing_plot) and the exterior a claimed plot is built from (housing_exterior_piece).
    struct Plot
    {
        uint16 map = 0;
        uint8 index = 0;
        float house[4] = { 0, 0, 0, 0 };   // x y z yaw
        float corner[4] = { 0, 0, 0, 0 };  // x y z orientation
        float exit[3] = { 0, 0, 0 };       // where leaving the house puts you
    };
    struct ExteriorPiece
    {
        std::string role; // base roof window chimney door_hook front_door
        uint32 entry = 0;
        float pos[3] = { 0, 0, 0 };
        float rotDeg = 0;
    };
    struct Placement { uint32 entry; float x, y, z, yaw; };
    std::vector<Plot> s_plots;
    std::vector<ExteriorPiece> s_exterior;
    std::map<std::pair<uint16, uint8>, uint32> s_plotHouse;           // plot -> house
    std::map<std::pair<uint16, uint8>, std::vector<uint32>> s_plotSpawns; // plot -> its saved exterior spawns
    std::unordered_map<uint32, std::pair<uint16, uint8>> s_housePlot; // house -> plot
    std::unordered_map<uint32, House> s_houses;
    std::unordered_map<uint32, uint32> s_houseByAccount;
    std::unordered_map<uint32, std::unordered_map<uint32, Owned>> s_owned; // account -> decor -> counts
    uint32 s_nextHouseId = 1, s_nextRoomId = 1;
    uint64 s_nextPlacedId = 1;

    // Live instances. A house keeps its instance only while that map exists.
    std::unordered_map<uint32, uint32> s_houseInstance;    // house -> instance
    std::unordered_map<uint32, uint32> s_instanceHouse;    // instance -> house
    std::unordered_map<uint32, std::unordered_map<uint64, ObjectGuid>> s_spawned; // instance -> placed -> GO
    std::unordered_set<uint32> s_populated;
    std::unordered_map<uint32, std::vector<ObjectGuid>> s_roomSpawned; // instance -> room-kit GOs

    std::unordered_map<ObjectGuid, uint32> s_pending;      // player -> house they are teleporting into
    std::unordered_map<ObjectGuid, uint32> s_lastHouse;    // player -> last house entered (relog inside)
    std::unordered_map<ObjectGuid, WorldLocation> s_returnTo;
    std::unordered_map<ObjectGuid, WorldLocation> s_neighborhoodReturn;

    // NeighborhoodMap.db2 row 1, Founder's Point: map, entry position and facing (make_slice.py spawns its steward there).
    constexpr uint32 NeighborhoodMap = 2735;
    constexpr float NeighborhoodEntry[4] = { 3807.76f, -160.427f, 194.111f, 2.852f };
    std::unordered_map<uint32, EditSession> s_editSessions; // account -> seq/rate state
    std::unordered_set<uint32> s_hasUi;                     // accounts whose client said HELLO with this Proto
    std::unordered_map<ObjectGuid, std::pair<uint16, uint8>> s_plotView; // player -> plot whose cornerstone they clicked

    RoomTemplate const* Room(House const& house)
    {
        auto it = s_rooms.find(house.roomTemplate);
        return it == s_rooms.end() ? nullptr : &it->second;
    }

    RoomTemplate const* DefaultRoom()
    {
        auto it = s_rooms.find(s_config.roomTemplate);
        return it == s_rooms.end() ? nullptr : &it->second;
    }

    bool IsHousingMap(uint32 mapId)
    {
        RoomTemplate const* room = DefaultRoom();
        return room && room->mapId == mapId;
    }

    House* HouseOfInstance(Map const* map)
    {
        if (!map || !IsHousingMap(map->GetId()))
            return nullptr;
        auto it = s_instanceHouse.find(map->GetInstanceId());
        if (it == s_instanceHouse.end())
            return nullptr;
        auto house = s_houses.find(it->second);
        return house == s_houses.end() ? nullptr : &house->second;
    }

    House* HouseOfAccount(uint32 account)
    {
        auto it = s_houseByAccount.find(account);
        return it == s_houseByAccount.end() ? nullptr : &s_houses[it->second];
    }

    void Load()
    {
        s_catalog.clear();
        s_rooms.clear();
        s_houses.clear();
        s_houseByAccount.clear();
        s_owned.clear();

        if (QueryResult result = WorldDatabase.Query("SELECT decor_id, model_fdid, display_id, gameobject_entry, name, "
            "category, surface, min_scale, max_scale FROM housing_decor_catalog WHERE enabled = 1"))
            do
            {
                Field* f = result->Fetch();
                CatalogEntry e;
                e.decorId = f[0].Get<uint32>(); e.fdid = f[1].Get<uint32>(); e.displayId = f[2].Get<uint32>();
                e.goEntry = f[3].Get<uint32>(); e.name = f[4].Get<std::string>(); e.category = f[5].Get<uint8>();
                e.surface = f[6].Get<uint8>(); e.minScale = f[7].Get<float>(); e.maxScale = f[8].Get<float>();
                if (!sObjectMgr->GetGameObjectTemplate(e.goEntry))
                {
                    LOG_ERROR("module", "housing: decor {} names missing gameobject_template {}; skipped", e.decorId, e.goEntry);
                    continue;
                }
                s_catalog[e.decorId] = e;
            } while (result->NextRow());

        if (QueryResult result = WorldDatabase.Query("SELECT room_template_id, map_id, entry_x, entry_y, entry_z, entry_o, "
            "min_x, min_y, min_z, max_x, max_y, max_z, max_decor FROM housing_room_template"))
            do
            {
                Field* f = result->Fetch();
                RoomTemplate r;
                r.id = f[0].Get<uint32>(); r.mapId = f[1].Get<uint16>();
                for (int i = 0; i < 4; ++i) r.entry[i] = f[2 + i].Get<float>();
                for (int i = 0; i < 3; ++i) { r.min[i] = f[6 + i].Get<float>(); r.max[i] = f[9 + i].Get<float>(); }
                r.maxDecor = f[12].Get<uint16>();
                s_rooms[r.id] = r;
            } while (result->NextRow());

        s_kinds.clear();
        if (QueryResult result = WorldDatabase.Query("SELECT kind, name, min_x, min_y, min_z, max_x, max_y, max_z "
            "FROM housing_room_kind"))
            do
            {
                Field* f = result->Fetch();
                Rooms::Kind k;
                k.id = f[0].Get<uint32>(); k.name = f[1].Get<std::string>();
                for (int i = 0; i < 3; ++i) { k.min[i] = f[2 + i].Get<float>(); k.max[i] = f[5 + i].Get<float>(); }
                s_kinds[k.id] = k;
            } while (result->NextRow());

        auto const mapObject = [](uint32 entry) {
            GameObjectTemplate const* go = entry ? sObjectMgr->GetGameObjectTemplate(entry) : nullptr;
            return go && go->type == GAMEOBJECT_TYPE_MAP_OBJECT;
        };
        if (QueryResult result = WorldDatabase.Query("SELECT kind, piece_id, type, pos_x, pos_y, pos_z, rot_deg, go_solid, "
            "go_door, go_wide, width, go_door_frame, go_wide_frame FROM housing_room_kit ORDER BY kind, piece_id"))
            do
            {
                Field* f = result->Fetch();
                auto kind = s_kinds.find(f[0].Get<uint32>());
                Rooms::KitPiece p;
                p.id = f[1].Get<uint32>(); p.type = f[2].Get<uint8>();
                p.x = f[3].Get<float>(); p.y = f[4].Get<float>(); p.z = f[5].Get<float>(); p.rotDeg = f[6].Get<float>();
                p.solid = f[7].Get<uint32>(); p.door = f[8].Get<uint32>(); p.wide = f[9].Get<uint32>(); p.width = f[10].Get<float>();
                if (kind == s_kinds.end() || !mapObject(p.solid))
                {
                    LOG_ERROR("module", "housing: room kit piece {} of kind {} names a missing kind or a non map-object "
                        "gameobject_template {}; skipped", p.id, f[0].Get<uint32>(), p.solid);
                    continue;
                }
                p.doorFrame = f[11].Get<uint32>(); p.wideFrame = f[12].Get<uint32>();
                if (!mapObject(p.door)) p.door = 0;
                if (!mapObject(p.wide)) p.wide = 0;
                if (!mapObject(p.doorFrame)) p.doorFrame = 0;
                if (!mapObject(p.wideFrame)) p.wideFrame = 0;
                kind->second.pieces.push_back(p);
            } while (result->NextRow());
        s_themed.clear();
        s_themes.clear();
        s_themes[GenericTheme] = "Generic";
        if (QueryResult result = WorldDatabase.Query("SELECT theme, name FROM housing_room_theme"))
            do
                s_themes[result->Fetch()[0].Get<uint32>()] = result->Fetch()[1].Get<std::string>();
            while (result->NextRow());
        if (QueryResult result = WorldDatabase.Query("SELECT kind, piece_id, theme, go_solid, go_door, go_wide, go_door_frame, "
            "go_wide_frame FROM housing_room_kit_theme"))
            do
            {
                Field* f = result->Fetch();
                ThemedModels m{ f[3].Get<uint32>(), f[4].Get<uint32>(), f[5].Get<uint32>(), f[6].Get<uint32>(), f[7].Get<uint32>() };
                for (uint32* e : { &m.solid, &m.door, &m.wide, &m.doorFrame, &m.wideFrame })
                    if (!mapObject(*e)) *e = 0;
                s_themed[{ f[0].Get<uint32>(), f[1].Get<uint32>(), f[2].Get<uint32>() }] = m;
            } while (result->NextRow());
        s_stairs.clear();
        if (QueryResult result = WorldDatabase.Query("SELECT kind, piece_id, theme, variant, go FROM housing_room_stairs"))
            do
            {
                Field* f = result->Fetch();
                if (mapObject(f[4].Get<uint32>()))
                    s_stairs[{ f[0].Get<uint32>(), f[1].Get<uint32>(), f[2].Get<uint32>(), f[3].Get<uint8>() }] = f[4].Get<uint32>();
            } while (result->NextRow());
        if (!s_kinds.count(s_config.firstRoomKind))
            LOG_ERROR("module", "housing: room kind {} (EsteriaHousing.FirstRoomKind) is missing", s_config.firstRoomKind);

        // shortcut: every house and placement is held in memory from startup; load per account on login when the
        // house count outgrows a dev realm.
        if (QueryResult result = CharacterDatabase.Query("SELECT h.house_id, h.account_id, h.room_template_id, h.revision, "
            "h.max_decor, COALESCE(MIN(r.room_id), 0) FROM housing_house h LEFT JOIN housing_room r ON r.house_id = h.house_id "
            "GROUP BY h.house_id"))
            do
            {
                Field* f = result->Fetch();
                House h;
                h.id = f[0].Get<uint32>(); h.account = f[1].Get<uint32>(); h.roomTemplate = f[2].Get<uint32>();
                h.revision = f[3].Get<uint32>(); h.maxDecor = f[4].Get<uint16>(); h.roomId = f[5].Get<uint32>();
                s_houseByAccount[h.account] = h.id;
                s_nextHouseId = std::max(s_nextHouseId, h.id + 1);
                s_houses[h.id] = std::move(h);
            } while (result->NextRow());

        s_plots.clear();
        s_exterior.clear();
        s_plotHouse.clear();
        s_housePlot.clear();
        if (QueryResult result = WorldDatabase.Query("SELECT map_id, plot, house_x, house_y, house_z, house_yaw, corner_x, "
            "corner_y, corner_z, corner_o, exit_x, exit_y, exit_z FROM housing_plot ORDER BY map_id, plot"))
            do
            {
                Field* f = result->Fetch();
                Plot p;
                p.map = f[0].Get<uint16>(); p.index = f[1].Get<uint8>();
                for (int i = 0; i < 4; ++i) { p.house[i] = f[2 + i].Get<float>(); p.corner[i] = f[6 + i].Get<float>(); }
                for (int i = 0; i < 3; ++i) p.exit[i] = f[10 + i].Get<float>();
                s_plots.push_back(p);
            } while (result->NextRow());
        if (QueryResult result = WorldDatabase.Query("SELECT role, gameobject_entry, pos_x, pos_y, pos_z, rot_deg "
            "FROM housing_exterior_piece ORDER BY id"))
            do
            {
                Field* f = result->Fetch();
                ExteriorPiece e;
                e.role = f[0].Get<std::string>(); e.entry = f[1].Get<uint32>();
                for (int i = 0; i < 3; ++i) e.pos[i] = f[2 + i].Get<float>();
                e.rotDeg = f[5].Get<float>();
                GameObjectTemplate const* go = sObjectMgr->GetGameObjectTemplate(e.entry);
                if (!go || (go->type != GAMEOBJECT_TYPE_MAP_OBJECT && e.role != "front_door"))
                {
                    LOG_ERROR("module", "housing: exterior piece names a non map-object gameobject_template {}; skipped", e.entry);
                    continue;
                }
                s_exterior.push_back(e);
            } while (result->NextRow());

        // Rooms claimed before layouts existed have no housing_room_layout row: they are the first kind at the origin.
        if (QueryResult result = CharacterDatabase.Query("SELECT r.room_id, r.house_id, COALESCE(l.kind, {}), "
            "COALESCE(l.offset_x, 0), COALESCE(l.offset_y, 0), COALESCE(l.yaw_quarter, 0) FROM housing_room r "
            "LEFT JOIN housing_room_layout l ON l.room_id = r.room_id ORDER BY r.house_id, r.slot", s_config.firstRoomKind))
            do
            {
                Field* f = result->Fetch();
                auto house = s_houses.find(f[1].Get<uint32>());
                if (house == s_houses.end())
                    continue;
                HouseRoom r;
                r.id = f[0].Get<uint32>();
                r.layout = { f[2].Get<uint32>(), f[3].Get<float>(), f[4].Get<float>(), uint8(f[5].Get<uint8>() % 4) };
                house->second.rooms.push_back(r);
            } while (result->NextRow());
        if (QueryResult result = CharacterDatabase.Query("SELECT l.room_id, r.house_id, l.level FROM housing_room_level l "
            "JOIN housing_room r ON r.room_id = l.room_id"))
            do
            {
                Field* f = result->Fetch();
                auto house = s_houses.find(f[1].Get<uint32>());
                if (house == s_houses.end())
                    continue;
                for (HouseRoom& r : house->second.rooms)
                    if (r.id == f[0].Get<uint32>())
                        r.layout.level = int8(std::clamp<int>(f[2].Get<int8>(), MinLevel, MaxLevel));
            } while (result->NextRow());
        if (QueryResult result = CharacterDatabase.Query("SELECT s.room_id, r.house_id, s.wall_theme, s.floor_theme, "
            "s.ceiling_theme, s.ceiling_hidden FROM housing_room_style s JOIN housing_room r ON r.room_id = s.room_id"))
            do
            {
                Field* f = result->Fetch();
                auto house = s_houses.find(f[1].Get<uint32>());
                if (house == s_houses.end())
                    continue;
                for (HouseRoom& r : house->second.rooms)
                    if (r.id == f[0].Get<uint32>())
                    {
                        for (int i = 0; i < 3; ++i) r.theme[i] = f[2 + i].Get<uint32>();
                        r.ceilingHidden = f[5].Get<uint8>() != 0;
                    }
            } while (result->NextRow());

        if (QueryResult result = CharacterDatabase.Query("SELECT map_id, plot, house_id, spawns FROM housing_plot_claim"))
            do
            {
                Field* f = result->Fetch();
                auto const key = std::make_pair(f[0].Get<uint16>(), f[1].Get<uint8>());
                s_plotHouse[key] = f[2].Get<uint32>();
                std::istringstream spawns(f[3].Get<std::string>());
                for (uint32 id; spawns >> id;)
                    s_plotSpawns[key].push_back(id);
                s_housePlot[f[2].Get<uint32>()] = key;
            } while (result->NextRow());

        if (QueryResult result = CharacterDatabase.Query("SELECT MAX(room_id) FROM housing_room"))
            s_nextRoomId = std::max<uint32>(1, result->Fetch()[0].Get<uint32>() + 1);
        if (QueryResult result = CharacterDatabase.Query("SELECT MAX(placed_id) FROM housing_placed_decor"))
            s_nextPlacedId = std::max<uint64>(1, result->Fetch()[0].Get<uint64>() + 1);

        if (QueryResult result = CharacterDatabase.Query("SELECT placed_id, house_id, decor_id, pos_x, pos_y, pos_z, rot_z, rot_w "
            "FROM housing_placed_decor"))
            do
            {
                Field* f = result->Fetch();
                auto house = s_houses.find(f[1].Get<uint32>());
                if (house == s_houses.end())
                    continue;
                Placed p;
                p.id = f[0].Get<uint64>(); p.decorId = f[2].Get<uint32>();
                for (int i = 0; i < 3; ++i) p.pos[i] = f[3 + i].Get<float>();
                p.yaw = 2 * std::atan2(f[6].Get<float>(), f[7].Get<float>());
                if (p.yaw < 0) p.yaw += 2 * float(M_PI);
                house->second.placed[p.id] = p;
            } while (result->NextRow());

        if (QueryResult result = CharacterDatabase.Query("SELECT account_id, decor_id, quantity_owned, quantity_placed "
            "FROM housing_account_decor"))
            do
            {
                Field* f = result->Fetch();
                s_owned[f[0].Get<uint32>()][f[1].Get<uint32>()] = { f[2].Get<uint16>(), f[3].Get<uint16>() };
            } while (result->NextRow());

        s_loaded = true;
        LOG_INFO("module", "housing: loaded {} catalog entries, {} room templates, {} room kinds, {} houses", s_catalog.size(),
            s_rooms.size(), s_kinds.size(), s_houses.size());
        if (!DefaultRoom())
            LOG_ERROR("module", "housing: room template {} (EsteriaHousing.RoomTemplate) is missing", s_config.roomTemplate);
    }

    // ---------------------------------------------------------------- world objects

    void Spawn(Map* map, Placed const& p)
    {
        auto entry = s_catalog.find(p.decorId);
        if (entry == s_catalog.end())
            return;
        if (GameObject* go = map->SummonGameObject(entry->second.goEntry, p.pos[0], p.pos[1], p.pos[2], p.yaw, 0, 0,
            std::sin(p.yaw / 2), std::cos(p.yaw / 2), 0, false))
            s_spawned[map->GetInstanceId()][p.id] = go->GetGUID();
        else
            LOG_ERROR("module", "housing: could not spawn decor {} (placed {}) in instance {}", p.decorId, p.id,
                map->GetInstanceId());
    }

    void Despawn(Map* map, uint64 placedId)
    {
        auto& spawned = s_spawned[map->GetInstanceId()];
        auto it = spawned.find(placedId);
        if (it == spawned.end())
            return;
        if (GameObject* go = map->GetGameObject(it->second))
        {
            go->SetRespawnTime(0);
            go->Delete();
        }
        spawned.erase(it);
    }

    std::vector<Rooms::Room> Layouts(House const& house)
    {
        std::vector<Rooms::Room> out;
        for (HouseRoom const& r : house.rooms)
            out.push_back(r.layout);
        return out;
    }

    // Decor and players are bounded by the room they stand in; z spans that room's height from the floor.
    bool RoomBox(House const& house, RoomTemplate const& t, size_t index, float min[3], float max[3])
    {
        auto kind = s_kinds.find(house.rooms[index].layout.kind);
        if (kind == s_kinds.end())
            return false;
        Rooms::Box const b = Rooms::Footprint(kind->second, house.rooms[index].layout);
        for (int i = 0; i < 2; ++i) { min[i] = t.Origin(i) + b.min[i]; max[i] = t.Origin(i) + b.max[i]; }
        float const floor = t.Origin(2) + float(house.rooms[index].layout.level) * Rooms::LevelHeight;
        min[2] = floor + std::max(0.0f, kind->second.min[2]) - 0.5f;
        max[2] = floor + std::min(Rooms::LevelHeight, kind->second.max[2]) + 0.5f; // a stairwell's top half is the floor above
        return true;
    }

    int RoomAt(House const& house, RoomTemplate const& t, float x, float y, float z)
    {
        for (size_t i = 0; i < house.rooms.size(); ++i)
        {
            float min[3], max[3];
            if (RoomBox(house, t, i, min, max) && x >= min[0] && x <= max[0] && y >= min[1] && y <= max[1]
                && z >= min[2] - 1.0f && z <= max[2] + 1.0f)
                return int(i);
        }
        return -1;
    }

    // A kit piece in a room's chosen theme for its part (walls, floor, ceiling); Generic, or a theme the piece lacks,
    // keeps the kit's own models.
    Rooms::KitPiece Themed(HouseRoom const& room, Rooms::KitPiece piece)
    {
        uint32 const theme = piece.type >= 1 && piece.type <= 3 ? room.theme[piece.type - 1] : GenericTheme;
        auto it = s_themed.find({ room.layout.kind, piece.id, theme });
        if (theme == GenericTheme || it == s_themed.end() || !it->second.solid)
            return piece;
        ThemedModels const& m = it->second;
        piece.solid = m.solid;
        if (m.door) piece.door = m.door;
        if (m.wide) piece.wide = m.wide;
        if (m.doorFrame) piece.doorFrame = m.doorFrame;
        if (m.wideFrame) piece.wideFrame = m.wideFrame;
        return piece;
    }

    // The stairwell directly above (up) or below a room, if any: same spot, one floor over.
    Rooms::Room const* StairwellNext(std::vector<Rooms::Room> const& layouts, Rooms::Room const& r, int step)
    {
        for (Rooms::Room const& o : layouts)
            if (IsStairwell(o.kind) && o.level == r.level + step && std::fabs(o.x - r.x) < 0.1f && std::fabs(o.y - r.y) < 0.1f)
                return &o;
        return nullptr;
    }

    uint32 RoomPrice(Rooms::Kind const& kind)
    {
        float const area = (kind.max[0] - kind.min[0]) * (kind.max[1] - kind.min[1]);
        uint32 const price = uint32(double(s_config.roomPrice) * area / (23.0 * 23.0));
        return std::max<uint32>(10000, price / 10000 * 10000); // whole gold, at least 1
    }

    // The room shell is rebuilt whole whenever the layout changes: a new neighbour turns walls into doorways.
    void SpawnRooms(Map* map, House const& house)
    {
        RoomTemplate const* t = Room(house);
        if (!t)
            return;
        auto& spawned = s_roomSpawned[map->GetInstanceId()];
        for (ObjectGuid const& guid : spawned)
            if (GameObject* go = map->GetGameObject(guid))
            {
                go->SetRespawnTime(0);
                go->Delete();
            }
        spawned.clear();
        std::vector<Rooms::Room> const layouts = Layouts(house);
        std::vector<Rooms::Joint> joints;
        auto const variants = Rooms::Variants(s_kinds, layouts, &joints);
        for (Rooms::Joint j : joints)
        {
            // the frame takes the first room's wall theme
            auto kind = s_kinds.find(layouts[j.room].kind);
            if (kind != s_kinds.end() && j.piece < kind->second.pieces.size())
            {
                Rooms::KitPiece const& base = kind->second.pieces[j.piece];
                Rooms::KitPiece const themed = Themed(house.rooms[j.room], base);
                j.frame = j.frame == base.wideFrame ? themed.wideFrame : themed.doorFrame;
            }
            if (GameObject* go = map->SummonGameObject(j.frame, t->Origin(0) + j.pose.x, t->Origin(1) + j.pose.y,
                t->Origin(2) + j.pose.z, j.pose.yaw, 0, 0, std::sin(j.pose.yaw / 2), std::cos(j.pose.yaw / 2), 0, false))
                spawned.push_back(go->GetGUID());
        }
        for (size_t r = 0; r < layouts.size(); ++r)
        {
            auto kind = s_kinds.find(layouts[r].kind);
            if (kind == s_kinds.end())
                continue;
            for (size_t i = 0; i < kind->second.pieces.size(); ++i)
            {
                uint8 const type = kind->second.pieces[i].type;
                bool const below = StairwellNext(layouts, layouts[r], -1) != nullptr;
                if (type == 3 && (house.rooms[r].ceilingHidden || IsStairwell(layouts[r].kind)))
                    continue;
                // the floor of a stairwell top, or of a stairwell on another, is the landing of the stairwell below
                if (type == 2 && (layouts[r].kind == StairwellTop || (IsStairwell(layouts[r].kind) && below)))
                    continue;
                Rooms::KitPiece piece = Themed(house.rooms[r], kind->second.pieces[i]);
                if (type == 4) // the staircase: its variant by what is above and below, its theme the walls'
                {
                    bool const above = StairwellNext(layouts, layouts[r], 1) != nullptr;
                    // 2/3 leave the floor over the bottom flight open for the stairs above to continue; 1/4 close it
                    uint8 const variant = above ? (below ? 3 : 2) : (below ? 4 : 1);
                    for (uint32 theme : { house.rooms[r].theme[0], GenericTheme })
                        if (auto s = s_stairs.find({ layouts[r].kind, piece.id, theme, variant }); s != s_stairs.end())
                        {
                            piece.solid = s->second;
                            break;
                        }
                }
                Rooms::Pose const p = Rooms::PieceWorld(layouts[r], piece);
                uint32 const entry = Rooms::Model(piece, variants[r][i]);
                if (GameObject* go = map->SummonGameObject(entry, t->Origin(0) + p.x, t->Origin(1) + p.y, t->Origin(2) + p.z,
                    p.yaw, 0, 0, std::sin(p.yaw / 2), std::cos(p.yaw / 2), 0, false))
                    spawned.push_back(go->GetGUID());
                else
                    LOG_ERROR("module", "housing: could not spawn room piece {} in instance {}", entry, map->GetInstanceId());
            }
        }
    }

    void Populate(Map* map, House const& house)
    {
        if (!s_populated.insert(map->GetInstanceId()).second)
            return;
        SpawnRooms(map, house);
        for (auto const& [id, p] : house.placed)
            Spawn(map, p);
        LOG_INFO("module", "housing: house {} populated instance {} with {} decor and {} rooms", house.id,
            map->GetInstanceId(), house.placed.size(), house.rooms.size());
    }

    // ---------------------------------------------------------------- packets

    void SendHello(WorldSession* session)
    {
        WorldPacket data(SMSG_ESTERIA_HOUSING_HELLO, 32);
        RoomTemplate const* room = DefaultRoom();
        data << uint16(Proto) << uint8(s_config.enabled && s_loaded && room) << uint32(0) << uint32(s_catalog.size())
             << uint16(room ? room->maxDecor : 0) << float(1) << float(1) << float(15);
        session->SendPacket(&data);
    }

    // Whether `kind` can be built through socket (room, piece): it fits there, and a stairwell also needs the floor above
    // free for its top (and a floor left to climb to).
    bool Fits(std::vector<Rooms::Room> const& layouts, size_t room, size_t piece, uint32 kind)
    {
        if (kind > StairsDownBase) // a stairwell down: its top on this floor through the socket, the stairwell below it
        {
            auto top = Rooms::Attach(s_kinds, layouts, room, piece, StairwellTop);
            if (!top || !IsStairwell(kind - StairsDownBase) || top->level <= MinLevel)
                return false;
            return Rooms::Fits(s_kinds, layouts, { kind - StairsDownBase, top->x, top->y, top->quarter, int8(top->level - 1) });
        }
        auto placed = Rooms::Attach(s_kinds, layouts, room, piece, kind);
        if (!placed)
            return false;
        if (!IsStairwell(kind))
            return true;
        Rooms::Room top{ StairwellTop, placed->x, placed->y, placed->quarter, int8(placed->level + 1) };
        return placed->level < MaxLevel && Rooms::Fits(s_kinds, layouts, top);
    }

    // The owner's blueprint: room kinds, the rooms placed, and every free wall with the kinds that fit through it.
    void SendLayout(Player* player, House const& house, RoomTemplate const& room)
    {
        std::vector<Rooms::Room> const layouts = Layouts(house);
        WorldPacket data(SMSG_ESTERIA_HOUSING_LAYOUT, 512);
        data << uint8(s_config.maxRooms) << room.Origin(0) << room.Origin(1);
        // the kinds, then a "Stairs Down" entry per stairwell (StairsDownBase + its kind)
        std::vector<std::pair<uint32, Rooms::Kind const*>> listed;
        for (auto const& [id, kind] : s_kinds)
            listed.push_back({ id, &kind });
        for (auto const& [id, kind] : s_kinds)
            if (IsStairwell(id))
                listed.push_back({ StairsDownBase + id, &kind });
        data << uint8(std::min<size_t>(listed.size(), 255));
        for (size_t i = 0; i < listed.size() && i < 255; ++i)
        {
            Rooms::Kind const& kind = *listed[i].second;
            std::string name = kind.name;
            if (listed[i].first > StairsDownBase)
                name.replace(0, std::string("Stairwell").size(), "Stairs Down");
            data << listed[i].first << (kind.max[0] - kind.min[0]) << (kind.max[1] - kind.min[1]) << RoomPrice(kind) << name;
        }
        data << uint8(house.rooms.size());
        for (HouseRoom const& r : house.rooms)
            data << r.layout.kind << r.layout.x << r.layout.y << r.layout.quarter << r.theme[0] << r.theme[1] << r.theme[2]
                 << uint8(r.ceilingHidden) << int8(r.layout.level);
        bool const full = layouts.size() >= s_config.maxRooms;
        uint16 sockets = 0;
        WorldPacket list(SMSG_ESTERIA_HOUSING_LAYOUT, 512);
        for (size_t r = 0; r < layouts.size() && r < 256 && !full; ++r)
        {
            auto kind = s_kinds.find(layouts[r].kind);
            if (kind == s_kinds.end())
                continue;
            for (size_t i = 0; i < kind->second.pieces.size() && i < 256; ++i)
            {
                if (!Rooms::FreeSocket(s_kinds, layouts, r, i))
                    continue;
                std::vector<uint32> fits;
                for (auto const& [id, k] : s_kinds)
                {
                    if (id != StairwellTop && Fits(layouts, r, i, id))
                        fits.push_back(id);
                    if (IsStairwell(id) && Fits(layouts, r, i, StairsDownBase + id))
                        fits.push_back(StairsDownBase + id);
                }
                if (fits.empty())
                    continue;
                Rooms::Pose const p = Rooms::PieceWorld(layouts[r], kind->second.pieces[i]);
                list << uint8(r) << uint8(i) << int8(layouts[r].level) << p.x << p.y << p.nx << p.ny
                     << uint8(std::min<size_t>(fits.size(), 255));
                for (size_t f = 0; f < fits.size() && f < 255; ++f)
                    list << fits[f];
                ++sockets;
            }
        }
        data << sockets;
        if (list.size())
            data.append(list.contents(), list.size());
        data << uint8(std::min<size_t>(s_themes.size(), 255));
        for (auto const& [id, name] : s_themes)
            data << id << name;
        player->SendDirectMessage(&data);
    }

    void SendState(Player* player)
    {
        House const* house = HouseOfInstance(player->GetMap());
        RoomTemplate const* room = house ? Room(*house) : nullptr;
        WorldPacket data(SMSG_ESTERIA_HOUSING_STATE, 64 + (house ? house->placed.size() * 28 : 0));
        data << uint8(house && room) << uint8(house && house->account == player->GetSession()->GetAccountId())
             << uint32(house ? house->id : 0) << uint32(house ? house->revision : 0)
             << uint16(house ? house->placed.size() : 0) << uint16(house ? house->maxDecor : 0);
        // The client only gets one box: the union of the rooms (the server still checks per room).
        float lo[3] = { 0, 0, 0 }, hi[3] = { 0, 0, 0 };
        if (house && room)
            for (size_t r = 0; r < house->rooms.size(); ++r)
            {
                float min[3], max[3];
                if (!RoomBox(*house, *room, r, min, max))
                    continue;
                for (int i = 0; i < 3; ++i)
                {
                    lo[i] = r ? std::min(lo[i], min[i]) : min[i];
                    hi[i] = r ? std::max(hi[i], max[i]) : max[i];
                }
            }
        for (int i = 0; i < 3; ++i) data << lo[i];
        for (int i = 0; i < 3; ++i) data << hi[i];
        uint16 const n = house && room ? uint16(std::min<size_t>(house->placed.size(), MaxStateEntries)) : 0;
        data << n;
        if (n)
        {
            uint16 written = 0;
            for (auto const& [id, p] : house->placed)
            {
                if (written++ == n) break;
                data << uint64(id) << uint32(p.decorId) << p.pos[0] << p.pos[1] << p.pos[2] << p.yaw;
            }
        }
        player->SendDirectMessage(&data);
        if (house && room && house->account == player->GetSession()->GetAccountId())
            SendLayout(player, *house, *room);
    }

    void BroadcastState(Map* map)
    {
        for (auto const& ref : map->GetPlayers())
            if (Player* player = ref.GetSource())
                SendState(player);
    }

    // What a decor costs at the house catalog, by category. shortcut: a price per category until decor has its own.
    uint32 DecorPrice(CatalogEntry const& e)
    {
        static uint32 const gold[] = { 1, 5, 2, 3, 2, 4 }; // Misc Furniture Accents Lighting Nature Structural
        return (e.category < 6 ? gold[e.category] : 1) * 10000;
    }

    void SendCatalog(WorldSession* session, uint32 page)
    {
        uint32 const account = session->GetAccountId();
        uint32 const pageCount = std::max<uint32>(1, (uint32(s_catalog.size()) + CatalogPageSize - 1) / CatalogPageSize);
        page = std::min(page, pageCount - 1);
        auto begin = s_catalog.begin();
        std::advance(begin, std::min<size_t>(size_t(page) * CatalogPageSize, s_catalog.size()));
        WorldPacket data(SMSG_ESTERIA_HOUSING_CATALOG, 16 + CatalogPageSize * 48);
        uint16 n = 0;
        for (auto it = begin; it != s_catalog.end() && n < CatalogPageSize; ++it) ++n;
        data << page << pageCount << n;
        auto const& owned = s_owned[account];
        for (auto it = begin; n--; ++it)
        {
            CatalogEntry const& e = it->second;
            auto o = owned.find(e.decorId);
            uint16 const have = o == owned.end() ? 0 : o->second.owned, used = o == owned.end() ? 0 : o->second.placed;
            data << e.decorId << e.goEntry << e.fdid << uint16(have > used ? have - used : 0) << used << e.category
                 << e.surface << DecorPrice(e) << e.name;
        }
        session->SendPacket(&data);
    }

    void SendAck(WorldSession* session, uint32 seq, uint8 result, uint32 revision, uint64 placedId,
        EsteriaHousing::Final const* final)
    {
        EsteriaHousing::Final const zero{ { 0, 0, 0 }, 0, { 0, 0, 0, 0 }, 0 };
        EsteriaHousing::Final const& f = final ? *final : zero;
        WorldPacket data(SMSG_ESTERIA_HOUSING_EDIT_ACK, 48);
        data << seq << result << revision << placedId << f.pos[0] << f.pos[1] << f.pos[2] << f.rot[0] << f.rot[1]
             << f.rot[2] << f.rot[3] << f.scale;
        session->SendPacket(&data);
    }

    std::string Json(Placed const& p)
    {
        return Acore::StringFormat("{{\"decor\":{},\"x\":{},\"y\":{},\"z\":{},\"yaw\":{}}}", p.decorId, p.pos[0], p.pos[1],
            p.pos[2], p.yaw);
    }

    void HandleEdit(WorldSession* session, WorldPacket& packet)
    {
        EsteriaHousing::Edit e;
        packet >> e.seq >> e.baseRevision >> e.op >> e.placedId >> e.decorId;
        for (float& v : e.pos) packet >> v;
        for (float& v : e.rot) packet >> v;
        packet >> e.scale;

        Player* player = session->GetPlayer();
        uint32 const account = session->GetAccountId();
        House* house = player ? HouseOfInstance(player->GetMap()) : nullptr;
        RoomTemplate const* room = house ? Room(*house) : nullptr;
        EditSession& state = s_editSessions[account];
        uint64 const now = GameTime::GetGameTimeMS().count();
        while (!state.recent.empty() && now - state.recent.front() >= 1000)
            state.recent.pop_front();

        EsteriaHousing::Facts f;
        f.enabled = s_config.enabled && s_loaded;
        f.inHouse = house && room;
        f.isOwner = house && house->account == account;
        f.lastSeq = state.lastSeq;
        f.revision = house ? house->revision : 0;
        f.decorKnown = s_catalog.count(e.decorId) != 0;
        auto& owned = s_owned[account];
        if (auto o = owned.find(e.decorId); o != owned.end())
            f.available = o->second.owned > o->second.placed ? o->second.owned - o->second.placed : 0;
        f.placementKnown = house && house->placed.count(e.placedId);
        f.placed = house ? uint32(house->placed.size()) : 0;
        f.maxDecor = house ? house->maxDecor : 0;
        // Bounds are those of the room the decor lands in; outside every room, an empty box refuses it.
        if (room && house)
        {
            int const at = RoomAt(*house, *room, e.pos[0], e.pos[1], e.pos[2]);
            if (at < 0 || !RoomBox(*house, *room, size_t(at), f.boundsMin, f.boundsMax))
                for (int i = 0; i < 3; ++i) { f.boundsMin[i] = 1; f.boundsMax[i] = 0; }
        }
        if (auto c = s_catalog.find(e.decorId); c != s_catalog.end())
        {
            f.minScale = c->second.minScale;
            f.maxScale = c->second.maxScale;
        }
        f.rateOk = state.recent.size() < s_config.editsPerSecond;

        EsteriaHousing::Final out;
        Result result = EsteriaHousing::Check(e, f, out);
        if (result != DuplicateSeq && result != Disabled && result != NotInHouse && result != NoPermission)
        {
            state.lastSeq = e.seq;
            state.recent.push_back(now);
        }
        if (result != Ok)
        {
            LOG_DEBUG("module", "housing: account {} edit seq {} op {} refused: {}", account, e.seq, e.op, uint32(result));
            return SendAck(session, e.seq, result, house ? house->revision : 0, e.placedId, nullptr);
        }

        // Apply in memory, persist in one transaction, then update the world for everyone inside.
        Map* map = player->GetMap();
        uint32 const revision = house->revision + 1;
        uint32 const now32 = uint32(GameTime::GetGameTime().count());
        uint32 const character = player->GetGUID().GetCounter();
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        uint64 placedId = e.placedId;
        std::string before = "NULL", after = "NULL";
        if (e.op == OpPlace)
        {
            placedId = s_nextPlacedId++;
            Placed p{ placedId, e.decorId, { out.pos[0], out.pos[1], out.pos[2] }, out.yaw };
            house->placed[placedId] = p;
            ++owned[e.decorId].placed;
            trans->Append("INSERT INTO housing_placed_decor (placed_id, house_id, room_id, decor_id, pos_x, pos_y, pos_z, "
                "rot_x, rot_y, rot_z, rot_w, scale, placed_by, placed_at) VALUES ({}, {}, {}, {}, {}, {}, {}, 0, 0, {}, {}, 1, {}, {})",
                placedId, house->id, house->roomId, e.decorId, out.pos[0], out.pos[1], out.pos[2], out.rot[2], out.rot[3],
                character, now32);
            trans->Append("UPDATE housing_account_decor SET quantity_placed = quantity_placed + 1 WHERE account_id = {} AND decor_id = {}",
                account, e.decorId);
            after = "'" + Json(p) + "'";
            Spawn(map, p);
        }
        else if (e.op == OpMove)
        {
            Placed& p = house->placed[placedId];
            before = "'" + Json(p) + "'";
            for (int i = 0; i < 3; ++i) p.pos[i] = out.pos[i];
            p.yaw = out.yaw;
            trans->Append("UPDATE housing_placed_decor SET pos_x = {}, pos_y = {}, pos_z = {}, rot_x = 0, rot_y = 0, rot_z = {}, "
                "rot_w = {} WHERE placed_id = {} AND house_id = {}", out.pos[0], out.pos[1], out.pos[2], out.rot[2], out.rot[3],
                placedId, house->id);
            after = "'" + Json(p) + "'";
            Despawn(map, placedId);
            Spawn(map, p);
        }
        else
        {
            Placed const p = house->placed[placedId];
            before = "'" + Json(p) + "'";
            house->placed.erase(placedId);
            if (Owned& o = owned[p.decorId]; o.placed)
                --o.placed;
            trans->Append("DELETE FROM housing_placed_decor WHERE placed_id = {} AND house_id = {}", placedId, house->id);
            trans->Append("UPDATE housing_account_decor SET quantity_placed = quantity_placed - 1 WHERE account_id = {} "
                "AND decor_id = {} AND quantity_placed > 0", account, p.decorId);
            Despawn(map, placedId);
            out = EsteriaHousing::Final{};
        }
        house->revision = revision;
        trans->Append("INSERT INTO housing_revision (house_id, revision, op, placed_id, before_json, after_json, character_guid, at) "
            "VALUES ({}, {}, {}, {}, {}, {}, {}, {})", house->id, revision, e.op, placedId, before, after, character, now32);
        trans->Append("UPDATE housing_house SET revision = {} WHERE house_id = {}", revision, house->id);
        CharacterDatabase.CommitTransaction(trans);

        LOG_INFO("module", "housing: account {} house {} rev {} op {} placed {} decor {}", account, house->id, revision,
            e.op, placedId, e.decorId);
        SendAck(session, e.seq, Ok, revision, placedId, &out);
        BroadcastState(map);
    }

    void Leave(Player* player)
    {
        auto it = s_returnTo.find(player->GetGUID());
        if (it != s_returnTo.end())
        {
            WorldLocation const to = it->second;
            s_returnTo.erase(it);
            player->TeleportTo(to.GetMapId(), to.GetPositionX(), to.GetPositionY(), to.GetPositionZ(), to.GetOrientation());
        }
        else
            player->TeleportTo(player->m_homebindMapId, player->m_homebindX, player->m_homebindY, player->m_homebindZ,
                player->GetOrientation());
    }

    void HandleAction(WorldSession* session, WorldPacket& packet);

    void OnPacket(WorldSession* session, WorldPacket& packet)
    {
        std::lock_guard<std::recursive_mutex> guard(s_lock);
        switch (packet.GetOpcode())
        {
            case CMSG_ESTERIA_HOUSING_HELLO:
            {
                uint16 proto;
                uint32 features;
                packet >> proto >> features;
                s_editSessions[session->GetAccountId()] = EditSession{}; // a new client session restarts seq at 1
                if (proto == Proto)
                    s_hasUi.insert(session->GetAccountId());
                else
                    s_hasUi.erase(session->GetAccountId());
                SendHello(session);
                if (s_config.enabled && proto == Proto && session->GetPlayer())
                    SendState(session->GetPlayer());
                break;
            }
            case CMSG_ESTERIA_HOUSING_CATALOG:
            {
                uint32 page;
                packet >> page;
                if (s_config.enabled && s_loaded)
                    SendCatalog(session, page);
                break;
            }
            case CMSG_ESTERIA_HOUSING_EDIT:
                HandleEdit(session, packet);
                break;
            case CMSG_ESTERIA_HOUSING_ACTION:
                HandleAction(session, packet);
                break;
            case CMSG_ESTERIA_HOUSING_ENTER:
            {
                uint8 action;
                packet >> action;
                Player* player = session->GetPlayer();
                if (!player || !s_config.enabled)
                    break;
                if (action == EnterSync)
                    SendState(player);
                else if (action == EnterLeave && HouseOfInstance(player->GetMap()))
                    Leave(player);
                break;
            }
            default:
                packet.rfinish();
                break;
        }
    }

    // MapInstanced hook: the owner's instance for whoever is entering a house.
    uint32 PickInstance(Player* player, uint32 mapId)
    {
        std::lock_guard<std::recursive_mutex> guard(s_lock);
        if (!s_config.enabled || !s_loaded || !IsHousingMap(mapId))
            return 0;
        uint32 houseId = 0;
        if (auto it = s_pending.find(player->GetGUID()); it != s_pending.end())
            houseId = it->second;
        else if (auto last = s_lastHouse.find(player->GetGUID()); last != s_lastHouse.end())
            houseId = last->second;
        else if (House* own = HouseOfAccount(player->GetSession()->GetAccountId()))
            houseId = own->id;
        if (!houseId || !s_houses.count(houseId))
            return 0;

        uint32& instanceId = s_houseInstance[houseId];
        if (!instanceId || !sMapMgr->FindMap(mapId, instanceId))
        {
            if (instanceId)
                s_instanceHouse.erase(instanceId);
            instanceId = sMapMgr->GenerateInstanceId();
            s_instanceHouse[instanceId] = houseId;
        }
        // A stale non-permanent bind to another house's instance would make InstanceMap::AddPlayerToMap refuse a
        // relogging player; housing instances never hold permanent binds.
        if (InstancePlayerBind* bind = sInstanceSaveMgr->PlayerGetBoundInstance(player->GetGUID(), mapId, DUNGEON_DIFFICULTY_NORMAL))
            if (!bind->perm && bind->save && bind->save->GetInstanceId() != instanceId)
                sInstanceSaveMgr->PlayerUnbindInstance(player->GetGUID(), mapId, DUNGEON_DIFFICULTY_NORMAL, true, player);
        return instanceId;
    }

    void ApplyHooks()
    {
        EsteriaHousingHooks::Packet.store(&OnPacket);
        EsteriaHousingHooks::Instance.store(s_config.enabled ? &PickInstance : nullptr);
    }

    bool EnterHouse(Player* player, House const& house)
    {
        RoomTemplate const* room = Room(house);
        if (!room)
            return false;
        if (!IsHousingMap(player->GetMapId()))
            s_returnTo[player->GetGUID()] = WorldLocation(player->GetMapId(), player->GetPositionX(), player->GetPositionY(),
                player->GetPositionZ(), player->GetOrientation());
        s_pending[player->GetGUID()] = house.id;
        LOG_INFO("module", "housing: {} enters house {} (owner account {})", player->GetName(), house.id, house.account);
        return player->TeleportTo(room->mapId, room->entry[0], room->entry[1], room->entry[2], room->entry[3]);
    }

    // Starter decor: StarterQuantity of every catalog entry. shortcut: grants stand in for acquisition (vendors, drops).
    void GrantStarter(uint32 account, CharacterDatabaseTransaction trans)
    {
        auto& owned = s_owned[account];
        for (auto const& [decorId, entry] : s_catalog)
        {
            Owned& o = owned[decorId];
            if (o.owned >= s_config.starterQuantity)
                continue;
            o.owned = s_config.starterQuantity;
            trans->Append("INSERT INTO housing_account_decor (account_id, decor_id, quantity_owned, quantity_placed) "
                "VALUES ({}, {}, {}, 0) ON DUPLICATE KEY UPDATE quantity_owned = GREATEST(quantity_owned, VALUES(quantity_owned))",
                account, decorId, o.owned);
        }
    }

    House* Claim(Player* player)
    {
        uint32 const account = player->GetSession()->GetAccountId();
        RoomTemplate const* room = DefaultRoom();
        if (!room || HouseOfAccount(account))
            return HouseOfAccount(account);
        House h;
        h.id = s_nextHouseId++;
        h.roomId = s_nextRoomId++;
        h.account = account;
        h.roomTemplate = room->id;
        h.maxDecor = room->maxDecor;
        uint32 const now = uint32(GameTime::GetGameTime().count());
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        trans->Append("INSERT INTO housing_house (house_id, account_id, room_template_id, revision, max_decor, created_at) "
            "VALUES ({}, {}, {}, 0, {}, {})", h.id, account, room->id, h.maxDecor, now);
        trans->Append("INSERT INTO housing_room (room_id, house_id, room_template_id, slot) VALUES ({}, {}, {}, 0)", h.roomId,
            h.id, room->id);
        trans->Append("INSERT INTO housing_room_layout (room_id, kind, offset_x, offset_y, yaw_quarter) VALUES ({}, {}, 0, 0, 0)",
            h.roomId, s_config.firstRoomKind);
        h.rooms.push_back({ h.roomId, { s_config.firstRoomKind, 0, 0, 0 } });
        GrantStarter(account, trans);
        CharacterDatabase.CommitTransaction(trans);
        s_houseByAccount[account] = h.id;
        LOG_INFO("module", "housing: {} (account {}) claimed house {}", player->GetName(), account, h.id);
        return &(s_houses[h.id] = std::move(h));
    }

    // Everyone in the house sees the new shell; anyone left standing where a room was removed goes back to the entry.
    void RoomsChanged(Map* map, House const& house)
    {
        SpawnRooms(map, house);
        RoomTemplate const* t = Room(house);
        map->DoForAllPlayers([&](Player* p) {
            if (t && RoomAt(house, *t, p->GetPositionX(), p->GetPositionY(), p->GetPositionZ()) < 0)
                p->NearTeleportTo(t->entry[0], t->entry[1], t->entry[2], t->entry[3]);
            SendState(p);
        });
    }

    void SaveRoom(House& house, Rooms::Room const& layout)
    {
        HouseRoom r{ s_nextRoomId++, layout };
        uint8 const slot = uint8(house.rooms.size());
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        trans->Append("INSERT INTO housing_room (room_id, house_id, room_template_id, slot) VALUES ({}, {}, {}, {})", r.id,
            house.id, house.roomTemplate, slot);
        trans->Append("INSERT INTO housing_room_layout (room_id, kind, offset_x, offset_y, yaw_quarter) VALUES ({}, {}, {}, {}, {})",
            r.id, layout.kind, layout.x, layout.y, layout.quarter);
        if (layout.level)
            trans->Append("INSERT INTO housing_room_level (room_id, level) VALUES ({}, {})", r.id, layout.level);
        CharacterDatabase.CommitTransaction(trans);
        house.rooms.push_back(r);
        LOG_INFO("module", "housing: house {} added room {} (kind {}) at {:.2f}, {:.2f} floor {} turn {}", house.id, r.id,
            layout.kind, layout.x, layout.y, layout.level + 1, layout.quarter);
    }

    std::string AddRoom(Player* player, House& house, size_t room, size_t piece, uint32 kind)
    {
        size_t const needed = IsStairwell(kind) || kind > StairsDownBase ? 2 : 1;
        if (house.rooms.size() + needed > s_config.maxRooms)
            return "Your house already has the most rooms it can hold.";
        std::vector<Rooms::Room> const layouts = Layouts(house);
        if (kind > StairsDownBase)
        {
            uint32 const stairwell = kind - StairsDownBase;
            if (!Fits(layouts, room, piece, kind))
                return "Those stairs no longer fit there, or the floor below is taken.";
            auto const top = Rooms::Attach(s_kinds, layouts, room, piece, StairwellTop);
            uint32 const price = RoomPrice(s_kinds.at(stairwell));
            if (!player->HasEnoughMoney(price))
                return "You cannot afford that room.";
            player->ModifyMoney(-int32(price));
            SaveRoom(house, { stairwell, top->x, top->y, top->quarter, int8(top->level - 1) });
            SaveRoom(house, *top);
            RoomsChanged(player->GetMap(), house);
            return "";
        }
        if (kind == StairwellTop || !s_kinds.count(kind) || !Fits(layouts, room, piece, kind))
            return IsStairwell(kind) ? "That stairwell no longer fits there, or the floor above is taken."
                : "That room no longer fits there.";
        auto const placed = Rooms::Attach(s_kinds, layouts, room, piece, kind);
        uint32 const price = RoomPrice(s_kinds.at(kind));
        if (!player->HasEnoughMoney(price))
            return "You cannot afford that room.";
        player->ModifyMoney(-int32(price));
        SaveRoom(house, *placed);
        if (IsStairwell(kind))
            SaveRoom(house, { StairwellTop, placed->x, placed->y, placed->quarter, int8(placed->level + 1) });
        RoomsChanged(player->GetMap(), house);
        return "";
    }

    // A stairwell's top becomes a stairwell of the same hand as the one below it, with a new top on the floor above.
    std::string StairsUp(Player* player, House& house, uint8 room)
    {
        std::vector<Rooms::Room> const layouts = Layouts(house);
        if (room >= layouts.size() || layouts[room].kind != StairwellTop)
            return "Only the top of a stairwell can lead further up.";
        Rooms::Room const* below = StairwellNext(layouts, layouts[room], -1);
        Rooms::Room top = layouts[room];
        top.level = int8(top.level + 1);
        if (!below || layouts[room].level >= MaxLevel || !Rooms::Fits(s_kinds, layouts, top))
            return "There is no space for stairs above that.";
        if (house.rooms.size() + 1 > s_config.maxRooms)
            return "Your house already has the most rooms it can hold.";
        uint32 const price = RoomPrice(s_kinds.at(below->kind));
        if (!player->HasEnoughMoney(price))
            return "You cannot afford that room.";
        player->ModifyMoney(-int32(price));
        HouseRoom& r = house.rooms[room];
        r.layout.kind = below->kind;
        CharacterDatabase.Execute("UPDATE housing_room_layout SET kind = {} WHERE room_id = {}", r.layout.kind, r.id);
        SaveRoom(house, top);
        RoomsChanged(player->GetMap(), house);
        return "";
    }

    std::string StyleRoom(Player* player, House& house, uint8 room, uint8 part, uint32 theme)
    {
        if (room >= house.rooms.size() || part < 1 || part > 3 || !s_themes.count(theme))
            return "That style is not available.";
        HouseRoom& r = house.rooms[room];
        r.theme[part - 1] = theme;
        CharacterDatabase.Execute("REPLACE INTO housing_room_style (room_id, wall_theme, floor_theme, ceiling_theme, ceiling_hidden) "
            "VALUES ({}, {}, {}, {}, {})", r.id, r.theme[0], r.theme[1], r.theme[2], uint8(r.ceilingHidden));
        RoomsChanged(player->GetMap(), house);
        return "";
    }

    std::string ShowCeiling(Player* player, House& house, uint8 room, bool hidden)
    {
        if (room >= house.rooms.size())
            return "That room is gone.";
        HouseRoom& r = house.rooms[room];
        r.ceilingHidden = hidden;
        CharacterDatabase.Execute("REPLACE INTO housing_room_style (room_id, wall_theme, floor_theme, ceiling_theme, ceiling_hidden) "
            "VALUES ({}, {}, {}, {}, {})", r.id, r.theme[0], r.theme[1], r.theme[2], uint8(r.ceilingHidden));
        RoomsChanged(player->GetMap(), house);
        return "";
    }

    std::string RemoveLastRoom(Player* player, House& house)
    {
        RoomTemplate const* t = Room(house);
        if (!t || house.rooms.size() < 2)
            return "The first room cannot be removed.";
        size_t const last = house.rooms.size() - 1;
        std::vector<Rooms::Room> const layouts = Layouts(house);
        // The newest room may be a stairwell's top. A stairwell that was a top itself (Extend Stairs Up: a stairwell below
        // it) turns back into one; otherwise the stairwell was built with the top (the room before it) and goes too.
        size_t count = 1;
        int revert = -1;
        if (layouts[last].kind == StairwellTop)
            if (Rooms::Room const* stairwell = StairwellNext(layouts, layouts[last], -1))
            {
                // only Extend Stairs Up puts a stairwell over another (a top always holds the spot above one)
                size_t const at = size_t(stairwell - layouts.data());
                if (StairwellNext(layouts, *stairwell, -1))
                    revert = int(at);
                else if (at == last - 1 && last >= 2)
                    count = 2;
            }
        for (auto const& [id, p] : house.placed)
            if (int const at = RoomAt(house, *t, p.pos[0], p.pos[1], p.pos[2]); at >= int(house.rooms.size() - count))
                return "Remove the decor in that room first.";
        if (revert >= 0)
        {
            HouseRoom& r = house.rooms[size_t(revert)];
            r.layout.kind = StairwellTop;
            CharacterDatabase.Execute("UPDATE housing_room_layout SET kind = {} WHERE room_id = {}", StairwellTop, r.id);
        }
        for (size_t i = 0; i < count; ++i)
        {
            CharacterDatabase.Execute("DELETE FROM housing_room WHERE room_id = {}", house.rooms.back().id); // the rest cascades
            LOG_INFO("module", "housing: house {} removed room {}", house.id, house.rooms.back().id);
            house.rooms.pop_back();
        }
        RoomsChanged(player->GetMap(), house);
        return "";
    }

    // ---------------------------------------------------------------- neighborhood plots

    Plot const* PlotAt(uint16 map, float x, float y, float maxDistance)
    {
        Plot const* best = nullptr;
        float bestDistance = maxDistance * maxDistance;
        for (Plot const& p : s_plots)
        {
            float const dx = p.corner[0] - x, dy = p.corner[1] - y, d = dx * dx + dy * dy;
            if (p.map == map && d <= bestDistance) { best = &p; bestDistance = d; }
        }
        return best;
    }

    Plot const* PlotOf(uint32 houseId)
    {
        auto it = s_housePlot.find(houseId);
        if (it == s_housePlot.end())
            return nullptr;
        for (Plot const& p : s_plots)
            if (p.map == it->second.first && p.index == it->second.second)
                return &p;
        return nullptr;
    }

    // The default exterior on a plot: every piece but the door hooks, plus the door on the hook facing the cornerstone.
    // door receives the spot just outside that door, where walking in enters the house.
    std::vector<Placement> Exterior(Plot const& plot, Rooms::Pose* door = nullptr)
    {
        std::vector<Placement> out;
        std::vector<Rooms::Hook> doors;
        std::vector<uint32> doorEntries;
        uint32 frontDoor = 0;
        for (ExteriorPiece const& e : s_exterior)
        {
            Rooms::Hook const h{ e.pos[0], e.pos[1], e.pos[2], e.rotDeg };
            if (e.role == "front_door")
            {
                frontDoor = e.entry;
                continue;
            }
            if (e.role == "door_hook")
            {
                doors.push_back(h);
                doorEntries.push_back(e.entry);
                continue;
            }
            Rooms::Pose const p = Rooms::OnPlot(plot.house[0], plot.house[1], plot.house[2], plot.house[3], h);
            out.push_back({ e.entry, p.x, p.y, p.z, p.yaw });
        }
        if (!doors.empty())
        {
            size_t const i = Rooms::FrontDoor(plot.house[0], plot.house[1], plot.house[2], plot.house[3], doors, plot.corner[0],
                plot.corner[1]);
            Rooms::Pose const p = Rooms::OnPlot(plot.house[0], plot.house[1], plot.house[2], plot.house[3], doors[i]);
            out.push_back({ doorEntries[i], p.x, p.y, p.z, p.yaw });
            if (frontDoor)
                out.push_back({ frontDoor, p.x - p.nx * 1.5f, p.y - p.ny * 1.5f, p.z + 2.02f, p.yaw });
            if (door)
            {
                *door = p;
                door->x += p.nx * 1.5f;
                door->y += p.ny * 1.5f;
            }
        }
        return out;
    }

    // Saves a permanent world spawn the way .gobject add does, so the grid owns it across unloads and restarts.
    uint32 SaveSpawn(Map* map, Placement const& p)
    {
        GameObjectTemplate const* info = sObjectMgr->GetGameObjectTemplate(p.entry);
        if (!info)
            return 0;
        GameObject* object = new GameObject();
        G3D::Quat const rotation = G3D::Quat::fromAxisAngleRotation(G3D::Vector3::unitZ(), p.yaw);
        if (!object->Create(map->GenerateLowGuid<HighGuid::GameObject>(), info->entry, map, PHASEMASK_NORMAL, p.x, p.y, p.z,
            p.yaw, rotation, 0, GO_STATE_READY))
        {
            delete object;
            return 0;
        }
        object->SaveToDB(map->GetId(), 1 << map->GetSpawnMode(), PHASEMASK_NORMAL);
        uint32 const spawnId = object->GetSpawnId();
        delete object;
        object = new GameObject();
        if (!object->LoadGameObjectFromDB(spawnId, map, true))
        {
            delete object;
            return 0;
        }
        sObjectMgr->AddGameobjectToGrid(spawnId, sObjectMgr->GetGameObjectData(spawnId));
        return spawnId;
    }

    void DeleteSpawn(Map* map, uint32 spawnId)
    {
        std::vector<GameObject*> loaded;
        auto range = map->GetGameObjectBySpawnIdStore().equal_range(spawnId);
        for (auto it = range.first; it != range.second; ++it)
            loaded.push_back(it->second);
        for (GameObject* go : loaded)
        {
            go->SetRespawnTime(0);
            go->Delete();
        }
        sObjectMgr->DeleteGOData(spawnId);
        WorldDatabase.Execute("DELETE FROM gameobject WHERE guid = {}", spawnId);
    }

    // A plot bought before the exterior recipe changed (the clickable front door) gets the current one.
    void RefreshExterior(Map* map, Plot const& plot)
    {
        auto const key = std::make_pair(plot.map, plot.index);
        std::vector<Placement> const want = Exterior(plot);
        std::vector<uint32>& have = s_plotSpawns[key];
        if (map->GetId() != plot.map)
            return;
        bool same = have.size() == want.size();
        for (size_t i = 0; same && i < have.size(); ++i)
        {
            GameObjectData const* d = sObjectMgr->GetGameObjectData(have[i]);
            same = d && d->id == want[i].entry && std::fabs(d->posX - want[i].x) < 0.05f && std::fabs(d->posY - want[i].y) < 0.05f
                && std::fabs(d->posZ - want[i].z) < 0.05f;
        }
        if (same)
            return;
        for (uint32 id : have)
            DeleteSpawn(map, id);
        have.clear();
        std::string spawns;
        for (Placement const& p : want)
            if (uint32 const spawnId = SaveSpawn(map, p))
            {
                have.push_back(spawnId);
                spawns += (spawns.empty() ? "" : " ") + std::to_string(spawnId);
            }
        CharacterDatabase.Execute("UPDATE housing_plot_claim SET spawns = '{}' WHERE map_id = {} AND plot = {}", spawns, plot.map,
            plot.index);
        LOG_INFO("module", "housing: rebuilt the exterior on plot {} (spawns {})", plot.index, spawns);
    }

    std::string ClaimPlot(Player* player, Plot const& plot)
    {
        uint32 const account = player->GetSession()->GetAccountId();
        if (s_plotHouse.count({ plot.map, plot.index }))
            return "Someone has already claimed this plot.";
        House* house = HouseOfAccount(account);
        if (house && s_housePlot.count(house->id))
            return "Your house already stands on another plot.";
        if (!house && !(house = Claim(player)))
            return "Housing could not create your house.";
        std::string spawns;
        for (Placement const& p : Exterior(plot))
            if (uint32 const spawnId = SaveSpawn(player->GetMap(), p))
                spawns += (spawns.empty() ? "" : " ") + std::to_string(spawnId);
        CharacterDatabase.Execute("INSERT INTO housing_plot_claim (map_id, plot, house_id, spawns, claimed_at) VALUES ({}, {}, {}, '{}', {})",
            plot.map, plot.index, house->id, spawns, uint32(GameTime::GetGameTime().count()));
        std::istringstream ids(spawns);
        for (uint32 id; ids >> id;)
            s_plotSpawns[{ plot.map, plot.index }].push_back(id);
        s_plotHouse[{ plot.map, plot.index }] = house->id;
        s_housePlot[house->id] = { plot.map, plot.index };
        LOG_INFO("module", "housing: {} claimed plot {} on map {} for house {} (spawns {})", player->GetName(), plot.index,
            plot.map, house->id, spawns);
        return "";
    }

    // Entering from a plot: leaving the house puts you at the plot's arrival point, not back on the door.
    void EnterFromPlot(Player* player, House const& house, Plot const& plot)
    {
        EnterHouse(player, house);
        s_returnTo[player->GetGUID()] = WorldLocation(plot.map, plot.exit[0], plot.exit[1], plot.exit[2], plot.corner[3]);
    }

    // Owner, or anyone grouped with the owner, may go in.
    bool MayEnter(Player* player, House const& house)
    {
        if (house.account == player->GetSession()->GetAccountId())
            return true;
        if (Group* group = player->GetGroup())
            for (GroupReference* ref = group->GetFirstMember(); ref; ref = ref->next())
                if (ref->GetSource() && ref->GetSource()->GetSession()->GetAccountId() == house.account)
                    return true;
        return false;
    }

    char const* const NeighborhoodName = "Founder's Point";
    constexpr float PlotReach = 15.0f; // how far from the cornerstone the plot window keeps working

    void SendPlot(Player* player, Plot const& plot, std::string const& message = "")
    {
        uint32 const account = player->GetSession()->GetAccountId();
        House const* own = HouseOfAccount(account);
        uint8 status = PlotForSale;
        if (auto owner = s_plotHouse.find({ plot.map, plot.index }); owner != s_plotHouse.end())
        {
            auto house = s_houses.find(owner->second);
            status = house == s_houses.end() ? PlotPrivate : house->second.account == account ? PlotYours
                : MayEnter(player, house->second) ? PlotVisitable : PlotPrivate;
        }
        // shortcut: no owner name; housing_house only knows the account. Add a character name column when visitors need it.
        WorldPacket data(SMSG_ESTERIA_HOUSING_PLOT, 64);
        data << uint16(plot.index + 1) << status << s_config.plotPrice
             << uint8(own && s_housePlot.count(own->id) && status != PlotYours) << NeighborhoodName << "" << message;
        player->SendDirectMessage(&data);
    }

    // The plot the player's open window is about, while they are still beside its cornerstone.
    Plot const* ViewedPlot(Player* player)
    {
        auto it = s_plotView.find(player->GetGUID());
        if (it == s_plotView.end() || player->GetMapId() != it->second.first)
            return nullptr;
        for (Plot const& p : s_plots)
            if (p.map == it->second.first && p.index == it->second.second)
                return player->GetExactDist2d(p.corner[0], p.corner[1]) <= PlotReach ? &p : nullptr;
        return nullptr;
    }

    std::string BuyPlot(Player* player, Plot const& plot)
    {
        if (s_plotHouse.count({ plot.map, plot.index }))
            return "Someone has already bought this plot.";
        if (House const* own = HouseOfAccount(player->GetSession()->GetAccountId()); own && s_housePlot.count(own->id))
            return "Your house already stands on another plot.";
        if (!player->HasEnoughMoney(s_config.plotPrice))
            return "You cannot afford this plot.";
        std::string const error = ClaimPlot(player, plot);
        if (error.empty())
            player->ModifyMoney(-int32(s_config.plotPrice));
        return error;
    }

    void HandleAction(WorldSession* session, WorldPacket& packet)
    {
        uint8 action;
        packet >> action;
        Player* player = session->GetPlayer();
        if (!player || !s_config.enabled || !s_loaded)
        {
            packet.rfinish();
            return;
        }
        if (action == ActionBuyPlot || action == ActionEnterPlot)
        {
            Plot const* plot = ViewedPlot(player);
            if (!plot)
                return;
            if (action == ActionBuyPlot)
            {
                std::string const error = BuyPlot(player, *plot);
                SendPlot(player, *plot, error.empty() ? "Welcome home! Walk in through your front door." : error);
            }
            else if (auto owner = s_plotHouse.find({ plot->map, plot->index }); owner != s_plotHouse.end()
                && s_houses.count(owner->second) && MayEnter(player, s_houses[owner->second]))
                EnterFromPlot(player, s_houses[owner->second], *plot);
            return;
        }
        // Room editing: the owner, inside their own house.
        House* own = HouseOfInstance(player->GetMap());
        if (!own || own->account != session->GetAccountId())
        {
            packet.rfinish();
            return;
        }
        std::string error;
        if (action == ActionAddRoom)
        {
            uint8 room, piece;
            uint32 kind;
            packet >> room >> piece >> kind;
            error = AddRoom(player, *own, room, piece, kind);
        }
        else if (action == ActionRemoveRoom)
            error = RemoveLastRoom(player, *own);
        else if (action == ActionRoomStyle)
        {
            uint8 room, part;
            uint32 theme;
            packet >> room >> part >> theme;
            error = StyleRoom(player, *own, room, part, theme);
        }
        else if (action == ActionBuyDecor)
        {
            uint32 decorId;
            uint16 count;
            packet >> decorId >> count;
            auto entry = s_catalog.find(decorId);
            uint32 const price = entry == s_catalog.end() ? 0 : DecorPrice(entry->second) * count; // at most 100 x 5 g
            Owned& o = s_owned[session->GetAccountId()][decorId];
            if (entry == s_catalog.end() || count < 1 || count > 100 || o.owned + count > 1000)
                error = "That decor cannot be bought.";
            else if (!player->HasEnoughMoney(price))
                error = "You cannot afford that.";
            else
            {
                player->ModifyMoney(-int32(price));
                o.owned = uint16(o.owned + count);
                CharacterDatabase.Execute("INSERT INTO housing_account_decor (account_id, decor_id, quantity_owned, quantity_placed) "
                    "VALUES ({}, {}, {}, 0) ON DUPLICATE KEY UPDATE quantity_owned = {}", session->GetAccountId(), decorId, o.owned, o.owned);
                LOG_INFO("module", "housing: account {} bought {} x decor {} for {} copper", session->GetAccountId(), count, decorId,
                    price);
                SendCatalog(session, 0);
            }
        }
        else if (action == ActionStairsUp)
        {
            uint8 room;
            packet >> room;
            error = StairsUp(player, *own, room);
        }
        else if (action == ActionRoomCeiling)
        {
            uint8 room, hidden;
            packet >> room >> hidden;
            error = ShowCeiling(player, *own, room, hidden != 0);
        }
        if (!error.empty())
            ChatHandler(session).SendNotification(error);
    }

    enum GossipAction : uint32
    {
        ActionLeave = 1,
        ActionEnter = 2,
        ActionVisit = 4,      // sender = owner account
        ActionVisitNeighborhood = 8,
        ActionLeaveNeighborhood = 9,
    };

    // The steward at Founder's Point: travel only. Houses are bought at plot cornerstones and edited in the client UI.
    class npc_esteria_housing_steward : public CreatureScript
    {
    public:
        npc_esteria_housing_steward() : CreatureScript("npc_esteria_housing_steward") { }

        bool OnGossipHello(Player* player, Creature* creature) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            ClearGossipMenuFor(player);
            uint32 const account = player->GetSession()->GetAccountId();
            if (!s_config.enabled || !s_loaded || !DefaultRoom())
                AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Housing is not available on this realm.", 0, 0);
            else if (HouseOfInstance(player->GetMap()))
                AddGossipItemFor(player, GOSSIP_ICON_TAXI, "Leave the house.", 0, ActionLeave);
            else
            {
                if (player->GetMapId() == NeighborhoodMap)
                    AddGossipItemFor(player, GOSSIP_ICON_TAXI, "Leave Founder's Point.", 0, ActionLeaveNeighborhood);
                else
                    AddGossipItemFor(player, GOSSIP_ICON_TAXI, "Visit Founder's Point.", 0, ActionVisitNeighborhood);
                if (HouseOfAccount(account))
                    AddGossipItemFor(player, GOSSIP_ICON_TAXI, "Take me to my house.", 0, ActionEnter);
                if (Group* group = player->GetGroup())
                    for (GroupReference* ref = group->GetFirstMember(); ref; ref = ref->next())
                        if (Player* member = ref->GetSource())
                        {
                            uint32 const owner = member->GetSession()->GetAccountId();
                            if (owner != account && HouseOfAccount(owner))
                                AddGossipItemFor(player, GOSSIP_ICON_TAXI, "Visit " + member->GetName() + "'s house.", owner,
                                    ActionVisit);
                        }
            }
            SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature);
            return true;
        }

        bool OnGossipSelect(Player* player, Creature* /*creature*/, uint32 sender, uint32 action) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            CloseGossipMenuFor(player);
            if (!s_config.enabled || !s_loaded)
                return true;
            uint32 const account = player->GetSession()->GetAccountId();
            switch (action)
            {
                case ActionLeave:
                    if (HouseOfInstance(player->GetMap()))
                        Leave(player);
                    break;
                case ActionVisitNeighborhood:
                    if (player->GetMapId() != NeighborhoodMap && !IsHousingMap(player->GetMapId()))
                    {
                        s_neighborhoodReturn[player->GetGUID()] = WorldLocation(player->GetMapId(), player->GetPositionX(),
                            player->GetPositionY(), player->GetPositionZ(), player->GetOrientation());
                        player->TeleportTo(NeighborhoodMap, NeighborhoodEntry[0], NeighborhoodEntry[1], NeighborhoodEntry[2],
                            NeighborhoodEntry[3]);
                    }
                    break;
                case ActionLeaveNeighborhood:
                    if (player->GetMapId() == NeighborhoodMap)
                    {
                        auto it = s_neighborhoodReturn.find(player->GetGUID());
                        if (it != s_neighborhoodReturn.end())
                        {
                            WorldLocation const to = it->second;
                            s_neighborhoodReturn.erase(it);
                            player->TeleportTo(to.GetMapId(), to.GetPositionX(), to.GetPositionY(), to.GetPositionZ(),
                                to.GetOrientation());
                        }
                        else
                            player->TeleportTo(player->m_homebindMapId, player->m_homebindX, player->m_homebindY,
                                player->m_homebindZ, player->GetOrientation());
                    }
                    break;
                case ActionEnter:
                    if (House* house = HouseOfAccount(account))
                        EnterHouse(player, *house);
                    break;
                case ActionVisit:
                {
                    // Re-check: the owner must still be in the visitor's group and own a house.
                    House* house = HouseOfAccount(sender);
                    bool grouped = false;
                    if (Group* group = player->GetGroup())
                        for (GroupReference* ref = group->GetFirstMember(); ref && !grouped; ref = ref->next())
                            grouped = ref->GetSource() && ref->GetSource()->GetSession()->GetAccountId() == sender;
                    if (house && grouped)
                        EnterHouse(player, *house);
                    break;
                }
            }
            return true;
        }
    };

    enum CornerstoneAction : uint32
    {
        ActionEnterPlot = 21,
    };

    // The sign on every plot (make_slice.py spawns one per housing_plot row). Free: claim it. Claimed: go in, if allowed.
    class go_esteria_housing_cornerstone : public GameObjectScript
    {
    public:
        go_esteria_housing_cornerstone() : GameObjectScript("go_esteria_housing_cornerstone") { }

        bool OnGossipHello(Player* player, GameObject* go) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            ClearGossipMenuFor(player);
            Plot const* plot = s_config.enabled && s_loaded ? PlotAt(go->GetMapId(), go->GetPositionX(), go->GetPositionY(), 3) : nullptr;
            if (plot)
                if (auto owner = s_plotHouse.find({ plot->map, plot->index }); owner != s_plotHouse.end()
                    && s_houses.count(owner->second) && s_houses[owner->second].account == player->GetSession()->GetAccountId())
                    RefreshExterior(go->GetMap(), *plot);
            if (plot && s_hasUi.count(player->GetSession()->GetAccountId()))
            {
                s_plotView[player->GetGUID()] = { plot->map, plot->index };
                SendPlot(player, *plot);
                return true; // the client opens its plot window instead of a gossip menu
            }
            if (!plot)
                AddGossipItemFor(player, GOSSIP_ICON_CHAT, "This plot is not available.", 0, 0);
            else if (auto owner = s_plotHouse.find({ plot->map, plot->index }); owner == s_plotHouse.end())
                AddGossipItemFor(player, GOSSIP_ICON_CHAT, "This plot is for sale. Buying it needs the Esteria housing client.", 0, 0);
            else if (House* house = s_houses.count(owner->second) ? &s_houses[owner->second] : nullptr; house && MayEnter(player, *house))
                AddGossipItemFor(player, GOSSIP_ICON_TAXI, house->account == player->GetSession()->GetAccountId()
                    ? "Enter your house." : "Visit this house.", 0, ActionEnterPlot);
            else
                AddGossipItemFor(player, GOSSIP_ICON_CHAT, "This plot is someone's home. Group with them to visit.", 0, 0);
            SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, go->GetGUID());
            return true;
        }

        bool OnGossipSelect(Player* player, GameObject* go, uint32 /*sender*/, uint32 action) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            CloseGossipMenuFor(player);
            Plot const* plot = s_config.enabled && s_loaded ? PlotAt(go->GetMapId(), go->GetPositionX(), go->GetPositionY(), 3) : nullptr;
            if (!plot)
                return true;
            if (action == ActionEnterPlot)
                if (auto owner = s_plotHouse.find({ plot->map, plot->index }); owner != s_plotHouse.end() && s_houses.count(owner->second)
                    && MayEnter(player, s_houses[owner->second]))
                    EnterFromPlot(player, s_houses[owner->second], *plot);
            return true;
        }
    };

    // The front door on a bought plot: clicking it goes in, for whoever may (MayEnter).
    class go_esteria_housing_front_door : public GameObjectScript
    {
    public:
        go_esteria_housing_front_door() : GameObjectScript("go_esteria_housing_front_door") { }

        bool OnGossipHello(Player* player, GameObject* go) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            if (!s_config.enabled || !s_loaded)
                return true;
            for (auto const& [key, houseId] : s_plotHouse)
            {
                Plot const* plot = PlotOf(houseId);
                auto house = s_houses.find(houseId);
                if (!plot || plot->map != go->GetMapId() || house == s_houses.end())
                    continue;
                Rooms::Pose door;
                Exterior(*plot, &door);
                if (go->GetExactDist2d(door.x, door.y) > 4.0f) // the mat lies 3 yd behind the door point, on the porch
                    continue;
                if (MayEnter(player, house->second))
                    EnterFromPlot(player, house->second, *plot);
                else
                    ChatHandler(player->GetSession()).SendNotification("This is someone's home. Group with them to visit.");
                break;
            }
            return true;
        }
    };

    // Door decor inside a house: clicking it leaves, like the Leave House button.
    class go_esteria_housing_exit : public GameObjectScript
    {
    public:
        go_esteria_housing_exit() : GameObjectScript("go_esteria_housing_exit") { }

        bool OnGossipHello(Player* player, GameObject* /*go*/) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            if (s_config.enabled && s_loaded && HouseOfInstance(player->GetMap()))
                Leave(player);
            return true;
        }
    };

    class EsteriaHousingWorld : public WorldScript
    {
    public:
        EsteriaHousingWorld() : WorldScript("EsteriaHousingWorld", { WORLDHOOK_ON_AFTER_CONFIG_LOAD, WORLDHOOK_ON_STARTUP }) { }

        void OnAfterConfigLoad(bool /*reload*/) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            s_config.enabled = sConfigMgr->GetOption<bool>("EsteriaHousing.Enable", false);
            s_config.roomTemplate = sConfigMgr->GetOption<uint32>("EsteriaHousing.RoomTemplate", 1);
            s_config.plotPrice = sConfigMgr->GetOption<uint32>("EsteriaHousing.PlotPrice", 1000000);
            s_config.starterQuantity = uint16(std::min<uint32>(1000, sConfigMgr->GetOption<uint32>("EsteriaHousing.StarterQuantity", 5)));
            s_config.editsPerSecond = std::max<uint32>(1, sConfigMgr->GetOption<uint32>("EsteriaHousing.EditsPerSecond", 8));
            s_config.firstRoomKind = sConfigMgr->GetOption<uint32>("EsteriaHousing.FirstRoomKind", 1);
            s_config.maxRooms = std::clamp<uint32>(sConfigMgr->GetOption<uint32>("EsteriaHousing.MaxRooms", 16), 1, 32);
            s_config.roomPrice = sConfigMgr->GetOption<uint32>("EsteriaHousing.RoomPrice", 250000);
            if (s_config.enabled && !s_loaded && sObjectMgr->GetGameObjectTemplates()->size())
                Load(); // a .reload config that turns housing on after startup
            ApplyHooks();
        }

        void OnStartup() override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            if (s_config.enabled)
                Load();
            ApplyHooks();
        }
    };

    class EsteriaHousingMaps : public AllMapScript
    {
    public:
        EsteriaHousingMaps() : AllMapScript("EsteriaHousingMaps", { ALLMAPHOOK_ON_PLAYER_ENTER_ALL, ALLMAPHOOK_ON_DESTROY_INSTANCE }) { }

        void OnPlayerEnterAll(Map* map, Player* player) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            if (!s_config.enabled || !s_loaded || !IsHousingMap(map->GetId()))
                return;
            s_pending.erase(player->GetGUID());
            House* house = HouseOfInstance(map);
            if (!house)
            {
                // The interior map is reserved for houses: anyone else (stale bind, GM teleport) goes home.
                ObjectGuid const guid = player->GetGUID();
                player->m_Events.AddEventAtOffset([guid]() {
                    if (Player* p = ObjectAccessor::FindPlayer(guid); p && p->IsInWorld())
                        p->TeleportTo(p->m_homebindMapId, p->m_homebindX, p->m_homebindY, p->m_homebindZ, p->GetOrientation());
                }, 1s);
                return;
            }
            s_lastHouse[player->GetGUID()] = house->id;
            if (house->account == player->GetSession()->GetAccountId())
            {
                CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
                GrantStarter(house->account, trans);
                if (trans->GetSize())
                    CharacterDatabase.CommitTransaction(trans);
            }
            Populate(map, *house);
            SendState(player);
        }

        void OnDestroyInstance(MapInstanced* /*mapInstanced*/, Map* map) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            auto it = s_instanceHouse.find(map->GetInstanceId());
            if (it == s_instanceHouse.end())
                return;
            if (auto house = s_houseInstance.find(it->second); house != s_houseInstance.end() && house->second == it->first)
                s_houseInstance.erase(house);
            s_spawned.erase(it->first);
            s_roomSpawned.erase(it->first);
            s_populated.erase(it->first);
            s_instanceHouse.erase(it);
        }
    };
}

void AddSC_mod_esteria_housing()
{
    new npc_esteria_housing_steward();
    new go_esteria_housing_cornerstone();
    new go_esteria_housing_front_door();
    new go_esteria_housing_exit();
    new EsteriaHousingWorld();
    new EsteriaHousingMaps();
}
