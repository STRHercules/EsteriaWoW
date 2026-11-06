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

    struct HouseRoom
    {
        uint32 id = 0; // housing_room.room_id
        Rooms::Room layout;
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
        uint32 stewardEntry = 9500100;
        uint16 starterQuantity = 5;
        uint32 editsPerSecond = 8;
        uint32 firstRoomKind = 1; // HouseRoom 1, Square Room (Small)
        uint32 maxRooms = 8;
    };

    std::recursive_mutex s_lock;
    Config s_config;
    bool s_loaded = false;
    std::map<uint32, CatalogEntry> s_catalog;
    std::unordered_map<uint32, RoomTemplate> s_rooms;
    Rooms::Kinds s_kinds; // retail room kinds and their kit pieces
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
            "go_door, go_wide, width FROM housing_room_kit ORDER BY kind, piece_id"))
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
                if (!mapObject(p.door)) p.door = 0;
                if (!mapObject(p.wide)) p.wide = 0;
                kind->second.pieces.push_back(p);
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
        min[2] = t.Origin(2) + kind->second.min[2] - 0.5f;
        max[2] = t.Origin(2) + kind->second.max[2] + 0.5f;
        return true;
    }

    int RoomAt(House const& house, RoomTemplate const& t, float x, float y)
    {
        for (size_t i = 0; i < house.rooms.size(); ++i)
        {
            float min[3], max[3];
            if (RoomBox(house, t, i, min, max) && x >= min[0] && x <= max[0] && y >= min[1] && y <= max[1])
                return int(i);
        }
        return -1;
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
        auto const variants = Rooms::Variants(s_kinds, layouts);
        for (size_t r = 0; r < layouts.size(); ++r)
        {
            auto kind = s_kinds.find(layouts[r].kind);
            if (kind == s_kinds.end())
                continue;
            for (size_t i = 0; i < kind->second.pieces.size(); ++i)
            {
                Rooms::KitPiece const& piece = kind->second.pieces[i];
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
        if (RoomTemplate const* room = Room(house))
            map->SummonCreature(s_config.stewardEntry, Position(room->entry[0] + 2, room->entry[1], room->entry[2],
                room->entry[3] + float(M_PI)));
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
    }

    void BroadcastState(Map* map)
    {
        for (auto const& ref : map->GetPlayers())
            if (Player* player = ref.GetSource())
                SendState(player);
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
                 << e.surface << e.name;
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
            int const at = RoomAt(*house, *room, e.pos[0], e.pos[1]);
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
        // The slice grants starter decor on claim; acquisition comes in Phase 3.
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
            if (t && RoomAt(house, *t, p->GetPositionX(), p->GetPositionY()) < 0)
                p->NearTeleportTo(t->entry[0], t->entry[1], t->entry[2], t->entry[3]);
            SendState(p);
        });
    }

    std::string AddRoom(Player* player, House& house, size_t room, size_t piece, uint32 kind)
    {
        if (house.rooms.size() >= s_config.maxRooms)
            return "Your house already has the most rooms it can hold.";
        auto placed = Rooms::Attach(s_kinds, Layouts(house), room, piece, kind);
        if (!placed)
            return "That room no longer fits there.";
        HouseRoom r{ s_nextRoomId++, *placed };
        uint8 const slot = uint8(house.rooms.size());
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        trans->Append("INSERT INTO housing_room (room_id, house_id, room_template_id, slot) VALUES ({}, {}, {}, {})", r.id,
            house.id, house.roomTemplate, slot);
        trans->Append("INSERT INTO housing_room_layout (room_id, kind, offset_x, offset_y, yaw_quarter) VALUES ({}, {}, {}, {}, {})",
            r.id, kind, r.layout.x, r.layout.y, r.layout.quarter);
        CharacterDatabase.CommitTransaction(trans);
        house.rooms.push_back(r);
        LOG_INFO("module", "housing: house {} added room {} (kind {}) at {:.2f}, {:.2f} turn {}", house.id, r.id, kind,
            r.layout.x, r.layout.y, r.layout.quarter);
        RoomsChanged(player->GetMap(), house);
        return "";
    }

    std::string RemoveLastRoom(Player* player, House& house)
    {
        RoomTemplate const* t = Room(house);
        if (!t || house.rooms.size() < 2)
            return "The first room cannot be removed.";
        size_t const last = house.rooms.size() - 1;
        for (auto const& [id, p] : house.placed)
            if (RoomAt(house, *t, p.pos[0], p.pos[1]) == int(last))
                return "Remove the decor in that room first.";
        CharacterDatabase.Execute("DELETE FROM housing_room WHERE room_id = {}", house.rooms[last].id); // layout cascades
        LOG_INFO("module", "housing: house {} removed room {}", house.id, house.rooms[last].id);
        house.rooms.pop_back();
        RoomsChanged(player->GetMap(), house);
        return "";
    }

    enum GossipAction : uint32
    {
        ActionLeave = 1,
        ActionEnter = 2,
        ActionClaim = 3,
        ActionVisit = 4,      // sender = owner account
        ActionAddRoom = 5,    // lists room kinds
        ActionPickKind = 6,   // sender = kind; lists walls it fits through
        ActionRemoveRoom = 7,
        ActionVisitNeighborhood = 8,
        ActionLeaveNeighborhood = 9,
        ActionPlaceRoom = 1000, // + room * 256 + piece; sender = kind
    };

    constexpr size_t MaxGossipItems = 30; // the client shows 32

    class npc_esteria_housing_steward : public CreatureScript
    {
    public:
        npc_esteria_housing_steward() : CreatureScript("npc_esteria_housing_steward") { }

        bool OnGossipHello(Player* player, Creature* creature) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            ClearGossipMenuFor(player);
            if (!s_config.enabled || !s_loaded || !DefaultRoom())
                AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Housing is not available on this realm.", 0, 0);
            else if (House* house = HouseOfInstance(player->GetMap()))
            {
                if (house->account == player->GetSession()->GetAccountId())
                {
                    if (house->rooms.size() < s_config.maxRooms)
                        AddGossipItemFor(player, GOSSIP_ICON_INTERACT_1, "Add a room...", 0, ActionAddRoom);
                    if (house->rooms.size() > 1)
                        AddGossipItemFor(player, GOSSIP_ICON_INTERACT_1, "Remove the newest room.", 0, ActionRemoveRoom);
                }
                AddGossipItemFor(player, GOSSIP_ICON_TAXI, "Leave the house.", 0, ActionLeave);
            }
            else
            {
                uint32 const account = player->GetSession()->GetAccountId();
                if (player->GetMapId() == NeighborhoodMap)
                    AddGossipItemFor(player, GOSSIP_ICON_TAXI, "Leave Founder's Point.", 0, ActionLeaveNeighborhood);
                else
                    AddGossipItemFor(player, GOSSIP_ICON_TAXI, "Visit Founder's Point.", 0, ActionVisitNeighborhood);
                if (HouseOfAccount(account))
                    AddGossipItemFor(player, GOSSIP_ICON_TAXI, "Take me to my house.", 0, ActionEnter);
                else
                    AddGossipItemFor(player, GOSSIP_ICON_INTERACT_1, "Claim a house.", 0, ActionClaim);
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

        bool OnGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 action) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            CloseGossipMenuFor(player);
            if (!s_config.enabled || !s_loaded)
                return true;
            uint32 const account = player->GetSession()->GetAccountId();

            // Room editing: owner only, re-checked on every step since the menu could be stale.
            House* own = HouseOfInstance(player->GetMap());
            if (own && own->account != account)
                own = nullptr;
            if (action == ActionAddRoom || action == ActionPickKind || action == ActionRemoveRoom || action >= ActionPlaceRoom)
            {
                if (!own)
                    return true;
                std::vector<Rooms::Room> const layouts = Layouts(*own);
                if (action == ActionAddRoom)
                {
                    ClearGossipMenuFor(player);
                    for (auto const& [id, kind] : s_kinds)
                        AddGossipItemFor(player, GOSSIP_ICON_INTERACT_1, kind.name, id, ActionPickKind);
                    SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature);
                }
                else if (action == ActionPickKind)
                {
                    ClearGossipMenuFor(player);
                    size_t offered = 0;
                    for (size_t r = 0; r < layouts.size() && offered < MaxGossipItems; ++r)
                    {
                        auto found = s_kinds.find(layouts[r].kind);
                        if (found == s_kinds.end())
                            continue;
                        Rooms::Kind const& kind = found->second;
                        for (size_t i = 0; i < kind.pieces.size() && i < 256 && offered < MaxGossipItems; ++i)
                            if (Rooms::Attach(s_kinds, layouts, r, i, sender))
                            {
                                char const* facing = Rooms::Facing(Rooms::PieceWorld(layouts[r], kind.pieces[i]));
                                AddGossipItemFor(player, GOSSIP_ICON_INTERACT_1, "Room " + std::to_string(r + 1) + " (" + kind.name
                                    + "), " + facing + " wall", sender, ActionPlaceRoom + uint32(r) * 256 + uint32(i));
                                ++offered;
                            }
                    }
                    if (!offered)
                        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "That room does not fit against any free wall.", 0, 0);
                    SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature);
                }
                else
                {
                    std::string const error = action == ActionRemoveRoom ? RemoveLastRoom(player, *own)
                        : AddRoom(player, *own, (action - ActionPlaceRoom) / 256, (action - ActionPlaceRoom) % 256, sender);
                    if (!error.empty())
                        ChatHandler(player->GetSession()).SendSysMessage(error);
                }
                return true;
            }

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
                case ActionClaim:
                    if (House* house = Claim(player))
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

    class EsteriaHousingWorld : public WorldScript
    {
    public:
        EsteriaHousingWorld() : WorldScript("EsteriaHousingWorld", { WORLDHOOK_ON_AFTER_CONFIG_LOAD, WORLDHOOK_ON_STARTUP }) { }

        void OnAfterConfigLoad(bool /*reload*/) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            s_config.enabled = sConfigMgr->GetOption<bool>("EsteriaHousing.Enable", false);
            s_config.roomTemplate = sConfigMgr->GetOption<uint32>("EsteriaHousing.RoomTemplate", 1);
            s_config.stewardEntry = sConfigMgr->GetOption<uint32>("EsteriaHousing.StewardEntry", 9500100);
            s_config.starterQuantity = uint16(std::min<uint32>(1000, sConfigMgr->GetOption<uint32>("EsteriaHousing.StarterQuantity", 5)));
            s_config.editsPerSecond = std::max<uint32>(1, sConfigMgr->GetOption<uint32>("EsteriaHousing.EditsPerSecond", 8));
            s_config.firstRoomKind = sConfigMgr->GetOption<uint32>("EsteriaHousing.FirstRoomKind", 1);
            s_config.maxRooms = std::clamp<uint32>(sConfigMgr->GetOption<uint32>("EsteriaHousing.MaxRooms", 8), 1, 32);
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
    new EsteriaHousingWorld();
    new EsteriaHousingMaps();
}
