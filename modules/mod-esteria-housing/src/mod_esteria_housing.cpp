// Esteria housing (wowdecomp docs/housing/). Houses in a per-house instance of a reused interior map; neighborhoods
// (an account's own, or a guild's) each an instance of a neighborhood map, with every house's exterior and outdoor
// decor spawned into it; decor as temporary GameObjects, edits over the HousingWire.h opcodes. Everything is off unless
// EsteriaHousing.Enable = 1; with it off both core hooks stay null and the module does nothing.
//
// All state lives on the world thread (PROCESS_THREADUNSAFE packets, gossip, teleports, map enter), so the maps below
// are only guarded against the occasional map-thread caller by one mutex.

#include "CharacterCache.h"
#include "Chat.h"
#include "Config.h"
#include "DatabaseEnv.h"
#include "EsteriaHousingHooks.h"
#include "GameObject.h"
#include "GameTime.h"
#include "AchievementMgr.h"
#include "Bag.h"
#include "Group.h"
#include "Guild.h"
#include "GuildMgr.h"
#include "HousingRooms.h"
#include "HousingRules.h"
#include "InstanceSaveMgr.h"
#include "Item.h"
#include "Log.h"
#include "Mail.h"
#include "Map.h"
#include "MapMgr.h"
#include "ObjectMgr.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "BodyShapeWire.h"
#include "RetailLookWire.h"
#include "ScriptedCreature.h"
#include "ScriptedGossip.h"
#include "SpellScript.h"
#include "Spell.h"
#include "World.h"
#include "SpellInfo.h"
#include "SpellMgr.h"
#include "DBCStores.h"
#include "WorldPacket.h"
#include "WorldSession.h"
#include <cmath>
#include <sstream>
#include <tuple>
#include <deque>
#include <map>
#include <memory>
#include <set>
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
    // A basement, then floors above the ground: 4 to start, up to 15 bought with gold (ActionUpgrade).
    constexpr int8 MinLevel = -1;
    constexpr uint8 BaseFloors = 4, FloorCap = 15;
    constexpr uint16 DecorBase = 200, DecorCap = 5000, DecorStep = 100;
    constexpr uint8 RoomCap = 64, RoomStep = 4;

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
        float yaw = 0;                    // the heading of rot
        float rot[4] = { 0, 0, 0, 1 };    // xyzw
        float scale = 1;
    };

    struct House
    {
        uint32 id = 0, account = 0, roomTemplate = 0, roomId = 0, revision = 0;
        uint16 maxDecor = 0;
        uint8 floors = BaseFloors;    // floors above the ground it may build (housing_house_limits)
        uint8 roomLimit = 0;          // rooms it may hold; 0: the realm's EsteriaHousing.MaxRooms
        uint8 access = AccessParty;   // who else may go in (housing_permission)
        std::string owner;            // the owner's most played character, for visitors' lists
        int8 MaxLevel() const { return int8(floors - 1); }
        std::map<uint64, Placed> placed;
        // decor on its plots (housing_placed_decor.room_id NULL), by neighborhood: a house has one plot in each
        std::map<uint32, std::map<uint64, Placed>> outdoor;
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
        uint32 maxAnimated = 12;   // moving displays (stable mounts, sanctuary pets) per house or neighborhood instance
        uint32 guildHoodPrice = 50000000; // copper from the guild bank for a guild neighborhood (5000 g)
        uint32 repairDiscount = 10;       // percent off at a house's repair station, at most MaxRepairDiscount
        uint32 hearthCooldown = 30;       // minutes between House Hearthstone uses
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
        uint32 style = 0; // HouseExteriorWmoData.ID * 10 + size; 0 for the front door, which every style uses
        std::string role; // base roof window chimney door_hook front_door
        uint32 entry = 0;
        float pos[3] = { 0, 0, 0 };
        float rotDeg = 0;
        float matX = 0, matZ = 0; // door hooks: where the Front Door mat lies on the porch, in the door's own coordinates
    };
    // How an owner set their plot's house: its style, and where it stands from the plot's spot (housing_plot_style).
    struct PlotLook
    {
        uint32 style = 92; // Human House (Small), the house every plot started with
        float dx = 0, dy = 0, turn = 0; // yd east/north of the plot's spot; degrees
        float dz = 0, scale = 1;        // yd up from the spot; size
    };
    constexpr float PlotReachYd = 15.0f;   // how far the house may move from the plot's spot
    constexpr float PlotHeightYd = 15.0f;  // and up or down
    constexpr float HouseMinScale = 0.5f, HouseMaxScale = 1.5f;
    // A swappable part (housing_exterior_fixture) and the hooks on it (housing_exterior_fixture_hook).
    struct Fixture
    {
        uint32 id = 0, theme = 0, parent = 0, entry = 0;
        uint8 type = 0, size = 0;
        bool isDefault = false;
        std::string name;
        float matX = 0, matZ = 0;
    };
    constexpr uint8 FixtureTypes[] = { FixtureBase, FixtureRoof, FixtureDoor, FixtureWindow, FixtureChimney, FixtureTower,
        FixtureDormer };
    // A wall or roof spot: the dormer, tower and chimney hooks of one base or roof shape at one place.
    struct Spot
    {
        uint32 shape = 0;
        uint8 local = 0;   // its number on the shape, in hook order
        uint8 accepts = 0; // SpotAccepts
        std::map<uint8, Rooms::Hook> hooks; // type -> the hook it stands on
    };
    // A plot in one neighborhood: (neighborhood_id, plot index). The plot's place on its map is a Plot.
    using Lot = std::pair<uint32, uint8>;
    std::map<std::tuple<uint32, uint8, uint32, uint8>, uint8> s_plotSpot; // neighborhood, plot, shape, spot -> type (0 empty)
    uint8 SpotBit(uint8 type) { return type == FixtureDormer ? SpotDormer : type == FixtureTower ? SpotTower
        : type == FixtureChimney ? SpotChimney : 0; }
    struct Placement { uint32 entry; float x, y, z, yaw; float rot[4] = { 0, 0, 0, 0 }; float scale = 1; }; // rot all 0: turn by yaw
    constexpr uint16 OutdoorBudget = 100;           // decor on a plot
    float s_plotRadius = 20;                        // half the distance between the closest two plots, at most 30 yd
    std::unordered_map<ObjectGuid, uint32> s_onPlot;   // player -> house whose plot they stand on (0: none)
    std::unordered_map<ObjectGuid, uint32> s_plotWatch; // player -> ms before the next plot check
    std::vector<Plot> s_plots;
    std::vector<ExteriorPiece> s_exterior;
    std::map<uint32, std::string> s_exteriorStyles;                    // style -> name
    std::map<uint32, Fixture> s_fixtures;                              // component -> part
    std::unordered_map<uint32, std::vector<std::pair<uint8, Rooms::Hook>>> s_fixtureHooks; // shape -> (type, hook)
    std::map<std::tuple<uint32, uint8, uint32, uint8>, uint32> s_plotFixture; // neighborhood, plot, theme, type -> component
    std::map<Lot, PlotLook> s_plotLook;
    std::map<Lot, uint32> s_plotHouse;                                 // plot -> house
    std::unordered_map<uint32, std::set<Lot>> s_houseLots;             // house -> its plots, one per neighborhood at most
    std::unordered_map<uint32, House> s_houses;
    std::unordered_map<uint32, std::vector<uint32>> s_accountHouses;   // account -> its houses, oldest first
    std::unordered_map<uint32, std::unordered_map<uint32, Owned>> s_owned; // account -> decor -> counts
    uint32 s_nextHouseId = 1, s_nextRoomId = 1;
    uint64 s_nextPlacedId = 1;

    // The neighborhood maps (retail NeighborhoodMap 1 and 2): map, name, entry and facing (make_slice.py spawns a
    // steward there). Every neighborhood is an instance of one of them.
    struct HoodMap { uint16 map; char const* name; float entry[4]; };
    constexpr HoodMap HoodMaps[] = {
        { 2735, "Founder's Point", { 3807.76f, -160.427f, 194.111f, 2.852f } },
        { 2736, "Razorwind Shores", { 2053.6f, 175.468f, 175.12f, 3.4558f } },
    };
    constexpr uint8 HoodMapCount = 2;
    // An account's own neighborhood, or one of a guild's (housing_neighborhood).
    enum HoodKind : uint8 { HoodAccount = 0, HoodGuild = 1 };
    struct Hood
    {
        uint32 id = 0, owner = 0; // account, or guild
        uint8 kind = HoodAccount, mapIndex = 0;
        bool chosen = true;       // an account's: its owner picked the map (the Neighborhood window asks until then)
        std::set<uint32> members; // accounts the owner invited: they may come in and buy plots
        uint16 Map() const { return HoodMaps[mapIndex].map; }
    };
    std::map<uint32, Hood> s_hoods;
    std::unordered_map<uint32, uint32> s_accountHood;      // account -> its own neighborhood
    uint32 s_nextHoodId = 1;
    // Guild rank rights (Right bits) in a guild's neighborhoods (housing_guild_right); the Guild Master has them all.
    constexpr uint8 DefaultRankRights = RightBuy;
    std::map<std::pair<uint32, uint8>, uint8> s_guildRights; // (guild, rank) -> GuildRight bits
    std::unordered_map<uint32, std::vector<std::pair<uint32, uint32>>> s_favorites; // account -> (house, neighborhood)
    std::unordered_map<uint32, std::deque<std::pair<uint32, uint32>>> s_recent;     // character -> visits, newest first
    constexpr size_t RecentVisits = 10;
    std::unordered_map<uint32, std::string> s_accountName;  // account -> its most played character
    std::unordered_map<uint32, uint32> s_guildCheckAt;      // guild -> ms left before its plots are checked (members left)

    // Live instances. A house or neighborhood keeps its instance only while that map exists.
    std::unordered_map<uint32, uint32> s_houseInstance;    // house -> instance
    std::unordered_map<uint32, uint32> s_instanceHouse;    // instance -> house
    std::unordered_map<uint32, uint32> s_hoodInstance;     // neighborhood -> instance
    std::unordered_map<uint32, uint32> s_instanceHood;     // instance -> neighborhood
    std::unordered_map<uint32, std::unordered_map<uint64, ObjectGuid>> s_spawned; // instance -> placed -> GO
    std::unordered_set<uint32> s_populated;
    std::unordered_map<uint32, std::vector<ObjectGuid>> s_roomSpawned; // instance -> room-kit GOs
    std::unordered_map<uint32, std::map<uint8, std::vector<ObjectGuid>>> s_lotSpawned; // instance -> plot -> exterior GOs

    std::unordered_map<ObjectGuid, uint32> s_pending;      // player -> house they are teleporting into
    std::unordered_map<ObjectGuid, uint32> s_lastHouse;    // player -> last house entered (relog inside)
    std::unordered_map<ObjectGuid, uint32> s_pendingHood;  // player -> neighborhood they are teleporting into
    std::unordered_map<ObjectGuid, uint32> s_lastHood;     // player -> last neighborhood entered (relog inside)
    std::unordered_map<ObjectGuid, WorldLocation> s_returnTo;
    std::unordered_map<ObjectGuid, uint32> s_returnHood;   // player -> neighborhood s_returnTo leads into (0: none)
    std::unordered_map<ObjectGuid, WorldLocation> s_neighborhoodReturn;

    std::unordered_map<uint32, EditSession> s_editSessions; // account -> seq/rate state
    std::unordered_set<uint32> s_hasUi;                     // accounts whose client said HELLO with this Proto
    std::unordered_map<ObjectGuid, Lot> s_plotView;         // player -> plot whose cornerstone they clicked

    // Shop decor: catalog rows ServiceDecorBase + kind (housing_commerce_world.sql).
    enum ServiceKind : uint8 { ServiceMerchant = 1, ServiceBoard = 2 };
    constexpr uint32 ServiceDecorBase = 40000;
    constexpr uint8 ServiceKindOf(uint32 decorId) { return decorId > ServiceDecorBase && decorId <= ServiceDecorBase + 7 ? uint8(decorId - ServiceDecorBase) : 0; }
    void LoadCommerce();
    void SpawnMerchant(Map* map, Placed const& p);
    void ShopPlaced(House const& house, Placed const& p, Player* player, CharacterDatabaseTransaction trans);
    void ShopRemoved(uint64 placedId, CharacterDatabaseTransaction trans);
    void MerchantJustPlaced(Player* player, Placed const& p);
    bool MerchantMirrorImage(Player* player, Unit* unit);
    void PushMerchantNames(Player* player, Map* map);
    bool HasStockForSale(uint64 placedId);
    void SpawnShopLabel(Map* map, Placed const& p);
    void DespawnShopLabel(Map* map, uint64 placedId);
    void SweepOrders();
    // Training dummies, portals and meeting stones: catalog rows AdventureDecorBase + kind (HousingAdventure.inc).
    enum AdventureKind : uint8 { AdvDummy = 1, AdvTank = 2, AdvHeal = 3, AdvBoss = 4, AdvPortal = 5, AdvStone = 6 };
    uint8 AdventureKindOf(uint32 decorId);
    void SpawnDummy(Map* map, Placed const& p);
    uint32 PortalLookEntry(uint64 placed);
    uint32 StoneLookEntry(uint64 placed);
    void AdventureRemoved(uint64 placed, CharacterDatabaseTransaction trans);
    void LoadAdventure();
    void TrainingTick(uint32 diff);
    void SyncHomeSpells(Player* player);
    // Trophies, mounts, mannequins, the library and pets: catalog rows CollectionDecorBase + kind (HousingCollections.inc).
    enum CollectionKind : uint8
    {
        ColTrophyMount = 1, ColTrophyPedestal, ColTrophyPlaque, ColTrophyCase, ColStall, ColPaddock, ColMountPedestal,
        ColMannequin, ColBookshelf, ColLectern, ColDisplayTable, ColReadingNook, ColHabitat, ColPetBed, ColPetToy, ColFeeder,
        // household services (HousingHousehold.inc): several decor pieces share a kind, see CollectionKindOf
        ColInnkeeper, ColBanker, ColBankVault, ColGuildVault, ColMailbox, ColRepairNpc, ColRepairBench, ColAuctioneer, ColStorage,
        ColStation, ColTrainer,
        ColMountMat,              // a mat a mount stands on, unseen while it does
        ColTrophyRug,             // a rug a statue or banner stands on, unseen while it does
        ColLast = ColTrophyRug
    };
    constexpr uint32 CollectionDecorBase = 40200;
    // Catalog rows 40201-40216 are one kind each; the services' (housing_household_world.sql) map onto theirs.
    constexpr uint8 CollectionKindOf(uint32 decorId)
    {
        if (decorId > CollectionDecorBase && decorId <= CollectionDecorBase + ColFeeder) return uint8(decorId - CollectionDecorBase);
        switch (decorId)
        {
            case 40217: return ColInnkeeper;
            case 40218: return ColBanker;
            case 40219: case 40220: return ColBankVault;
            case 40221: return ColGuildVault;
            case 40222: case 40223: return ColMailbox;
            case 40224: return ColRepairNpc;
            case 40225: return ColRepairBench;
            case 40226: return ColAuctioneer;
            case 40227: case 40228: case 40229: return ColStorage;
            default: break;
        }
        if (decorId >= 40230 && decorId <= 40239) return ColStation;
        if (decorId >= 40251 && decorId <= 40264) return ColTrainer;
        switch (decorId)
        {
            case 40265: return ColMountMat;
            case 40272: return ColTrophyRug;
            case 40266: case 40267: case 40268: return ColHabitat;   // small habitats: rugs and a cushion
            case 40273: return ColHabitat;                           // the Grand Pet Rug: ten pets
            case 40269: case 40270: case 40271: return ColPetToy;    // plushies
            default: return 0;
        }
    }
    // a character drawn with a customizable look: the mannequin and the service NPCs
    constexpr bool IsFigureKind(uint8 k) { return k == ColMannequin || k == ColInnkeeper || k == ColBanker || k == ColRepairNpc
        || k == ColAuctioneer || k == ColTrainer; }
    constexpr bool IsHouseholdKind(uint8 k) { return k >= ColInnkeeper && k <= ColTrainer; }
    // A piece drawn at a fixed share of its placed size: gameobject_template.size (1 for most; the mount stall's model
    // is large, the mount mat's is shrunk out of sight).
    float BaseScale(uint32 decorId);
    bool MatHidden(uint64 placed); // a mount mat with a mount on it: only the mount shows
    void HouseholdPlaced(Placed const& p, uint32 account, CharacterDatabaseTransaction trans);
    void LoadCollections();
    void SpawnMannequin(Map* map, Placed const& p);
    void SpawnDisplayExtras(Map* map, Placed const& p);
    void DespawnDisplayExtras(Map* map, uint64 placed);
    void CollectionRemoved(uint64 placed, CharacterDatabaseTransaction trans);
    void PushDisplayNames(Player* player, Map* map);
    bool DisplayMirrorImage(Player* player, Unit* unit);
    void ForgetDisplayUnit(ObjectGuid guid);

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

    // The account's first house (the steward's "take me to my house"), or null.
    House* HouseOfAccount(uint32 account)
    {
        auto it = s_accountHouses.find(account);
        return it == s_accountHouses.end() || it->second.empty() ? nullptr : &s_houses[it->second.front()];
    }

    bool IsNeighborhoodMap(uint32 mapId)
    {
        for (HoodMap const& m : HoodMaps)
            if (m.map == mapId)
                return true;
        return false;
    }

    Hood* FindHood(uint32 id)
    {
        auto it = s_hoods.find(id);
        return it == s_hoods.end() ? nullptr : &it->second;
    }

    // The neighborhood a neighborhood-map instance is, or null.
    Hood* HoodOfMap(Map const* map)
    {
        if (!map || !IsNeighborhoodMap(map->GetId()))
            return nullptr;
        auto it = s_instanceHood.find(map->GetInstanceId());
        Hood* hood = it == s_instanceHood.end() ? nullptr : FindHood(it->second);
        return hood && hood->Map() == map->GetId() ? hood : nullptr;
    }

    // The live instance of a neighborhood, or null.
    Map* LiveMap(Hood const& hood)
    {
        auto it = s_hoodInstance.find(hood.id);
        return it == s_hoodInstance.end() ? nullptr : sMapMgr->FindMap(hood.Map(), it->second);
    }

    Plot const* FindPlot(uint16 map, uint8 index)
    {
        for (Plot const& p : s_plots)
            if (p.map == map && p.index == index)
                return &p;
        return nullptr;
    }

    Plot const* PlotOfLot(Lot const& lot)
    {
        Hood const* hood = FindHood(lot.first);
        return hood ? FindPlot(hood->Map(), lot.second) : nullptr;
    }

    // The account's most played character's name (houses and neighborhoods are named for it).
    std::string const& AccountName(uint32 account)
    {
        auto it = s_accountName.find(account);
        if (it != s_accountName.end())
            return it->second;
        std::string name = "Someone";
        if (QueryResult r = CharacterDatabase.Query("SELECT name FROM characters WHERE account = {} ORDER BY totaltime DESC "
            "LIMIT 1", account))
            name = r->Fetch()[0].Get<std::string>();
        return s_accountName[account] = name;
    }

    std::string HoodName(Hood const& hood)
    {
        if (hood.kind == HoodGuild)
        {
            Guild const* guild = sGuildMgr->GetGuildById(hood.owner);
            uint32 n = 0, mine = 0;
            for (auto const& [id, h] : s_hoods)
                if (h.kind == HoodGuild && h.owner == hood.owner && ++n && id == hood.id)
                    mine = n;
            std::string name = (guild ? guild->GetName() : std::string("A guild")) + "'s Neighborhood";
            return mine > 1 ? name + " " + std::to_string(mine) : name;
        }
        return AccountName(hood.owner) + "'s Neighborhood";
    }

    uint16 PlotCount(Hood const& hood)
    {
        uint16 n = 0;
        for (Plot const& p : s_plots)
            n += p.map == hood.Map();
        return n;
    }

    uint16 FreePlots(Hood const& hood)
    {
        uint16 taken = 0;
        for (auto const& [lot, house] : s_plotHouse)
            taken += lot.first == hood.id;
        return uint16(PlotCount(hood) - std::min<uint16>(taken, PlotCount(hood)));
    }

    // The account's own neighborhood, made on first use (Founder's Point).
    Hood& AccountHood(uint32 account)
    {
        if (auto it = s_accountHood.find(account); it != s_accountHood.end())
            return s_hoods[it->second];
        Hood h;
        h.id = s_nextHoodId++;
        h.owner = account;
        h.chosen = false;
        CharacterDatabase.Execute("INSERT INTO housing_neighborhood (neighborhood_id, kind, owner, map_id, created_at, chosen) "
            "VALUES ({}, 0, {}, {}, {}, 0)", h.id, account, h.Map(), uint32(GameTime::GetGameTime().count()));
        s_accountHood[account] = h.id;
        LOG_INFO("module", "housing: account {} gets neighborhood {}", account, h.id);
        return s_hoods[h.id] = h;
    }

    void Load()
    {
        s_catalog.clear();
        s_rooms.clear();
        s_houses.clear();
        s_accountHouses.clear();
        s_owned.clear();
        s_hoods.clear();
        s_accountHood.clear();
        s_houseLots.clear();
        s_guildRights.clear();
        s_favorites.clear();
        s_recent.clear();
        s_accountName.clear();

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
            "GROUP BY h.house_id ORDER BY h.house_id"))
            do
            {
                Field* f = result->Fetch();
                House h;
                h.id = f[0].Get<uint32>(); h.account = f[1].Get<uint32>(); h.roomTemplate = f[2].Get<uint32>();
                h.revision = f[3].Get<uint32>(); h.maxDecor = f[4].Get<uint16>(); h.roomId = f[5].Get<uint32>();
                s_accountHouses[h.account].push_back(h.id);
                s_nextHouseId = std::max(s_nextHouseId, h.id + 1);
                s_houses[h.id] = std::move(h);
            } while (result->NextRow());
        if (QueryResult result = CharacterDatabase.Query("SELECT house_id, scope, can_visit FROM housing_permission "
            "WHERE scope IN (0, 1, 2, 4) AND grantee = 0"))
            do
                if (auto house = s_houses.find(result->Fetch()[0].Get<uint32>()); house != s_houses.end())
                {
                    uint8 const bit = uint8(1 << result->Fetch()[1].Get<uint8>());
                    house->second.access = result->Fetch()[2].Get<uint8>() ? house->second.access | bit : house->second.access & ~bit;
                }
            while (result->NextRow());
        // most played last, so it wins
        if (QueryResult result = CharacterDatabase.Query("SELECT h.house_id, c.name FROM characters c JOIN housing_house h "
            "ON h.account_id = c.account ORDER BY c.totaltime"))
            do
                if (auto house = s_houses.find(result->Fetch()[0].Get<uint32>()); house != s_houses.end())
                    house->second.owner = result->Fetch()[1].Get<std::string>();
            while (result->NextRow());
        if (QueryResult result = CharacterDatabase.Query("SELECT house_id, floors, rooms FROM housing_house_limits"))
            do
                if (auto house = s_houses.find(result->Fetch()[0].Get<uint32>()); house != s_houses.end())
                {
                    house->second.floors = uint8(std::clamp<int>(result->Fetch()[1].Get<uint8>(), BaseFloors, FloorCap));
                    house->second.roomLimit = uint8(std::min<int>(result->Fetch()[2].Get<uint8>(), RoomCap));
                }
            while (result->NextRow());

        // Before neighborhoods were instances, exteriors and outdoor decor were saved world spawns, which an instanced map
        // would load into every neighborhood: delete them (they are spawned per instance now).
        std::vector<uint32> legacy;
        if (QueryResult result = CharacterDatabase.Query("SELECT spawn_id FROM housing_outdoor_spawn"))
            do legacy.push_back(result->Fetch()[0].Get<uint32>()); while (result->NextRow());
        if (QueryResult result = CharacterDatabase.Query("SELECT spawns FROM housing_plot_claim WHERE spawns <> ''"))
            do
            {
                std::istringstream spawns(result->Fetch()[0].Get<std::string>());
                for (uint32 id; spawns >> id;)
                    legacy.push_back(id);
            } while (result->NextRow());
        for (uint32 id : legacy)
        {
            sObjectMgr->DeleteGOData(id);
            WorldDatabase.Execute("DELETE FROM gameobject WHERE guid = {}", id);
        }
        if (!legacy.empty())
        {
            CharacterDatabase.Execute("DELETE FROM housing_outdoor_spawn");
            CharacterDatabase.Execute("UPDATE housing_plot_claim SET spawns = ''");
            LOG_INFO("module", "housing: deleted {} saved exterior and outdoor decor spawns (now spawned per neighborhood)",
                legacy.size());
        }

        if (QueryResult result = CharacterDatabase.Query("SELECT neighborhood_id, kind, owner, map_id, chosen FROM housing_neighborhood"))
            do
            {
                Field* f = result->Fetch();
                Hood h;
                h.id = f[0].Get<uint32>(); h.kind = f[1].Get<uint8>(); h.owner = f[2].Get<uint32>();
                h.chosen = h.kind != HoodAccount || f[4].Get<uint8>();
                for (uint8 i = 0; i < HoodMapCount; ++i)
                    if (HoodMaps[i].map == f[3].Get<uint16>())
                        h.mapIndex = i;
                if (h.kind == HoodAccount)
                    s_accountHood[h.owner] = h.id;
                s_nextHoodId = std::max(s_nextHoodId, h.id + 1);
                s_hoods[h.id] = h;
            } while (result->NextRow());
        if (QueryResult result = CharacterDatabase.Query("SELECT neighborhood_id, account_id FROM housing_neighborhood_member"))
            do
                if (Hood* hood = FindHood(result->Fetch()[0].Get<uint32>()))
                    hood->members.insert(result->Fetch()[1].Get<uint32>());
            while (result->NextRow());
        if (QueryResult result = CharacterDatabase.Query("SELECT guild_id, rank_id, rights FROM housing_guild_right"))
            do
                s_guildRights[{ result->Fetch()[0].Get<uint32>(), result->Fetch()[1].Get<uint8>() }] = result->Fetch()[2].Get<uint8>();
            while (result->NextRow());
        if (QueryResult result = CharacterDatabase.Query("SELECT account_id, house_id, neighborhood_id FROM housing_favorite "
            "ORDER BY added_at"))
            do
                s_favorites[result->Fetch()[0].Get<uint32>()].push_back({ result->Fetch()[1].Get<uint32>(),
                    result->Fetch()[2].Get<uint32>() });
            while (result->NextRow());
        if (QueryResult result = CharacterDatabase.Query("SELECT guid, house_id, neighborhood_id FROM housing_recent_visit "
            "ORDER BY visited_at DESC"))
            do
                if (auto& list = s_recent[result->Fetch()[0].Get<uint32>()]; list.size() < RecentVisits)
                    list.push_back({ result->Fetch()[1].Get<uint32>(), result->Fetch()[2].Get<uint32>() });
            while (result->NextRow());

        s_plots.clear();
        s_exterior.clear();
        s_exteriorStyles.clear();
        s_plotLook.clear();
        s_plotHouse.clear();
        s_fixtures.clear();
        s_fixtureHooks.clear();
        s_plotFixture.clear();
        if (QueryResult result = WorldDatabase.Query("SELECT component, theme, type, size, parent, is_default, gameobject_entry, "
            "name, mat_x, mat_z FROM housing_exterior_fixture"))
            do
            {
                Field* f = result->Fetch();
                Fixture x;
                x.id = f[0].Get<uint32>(); x.theme = f[1].Get<uint32>(); x.type = f[2].Get<uint8>(); x.size = f[3].Get<uint8>();
                x.parent = f[4].Get<uint32>(); x.isDefault = f[5].Get<uint8>() != 0; x.entry = f[6].Get<uint32>();
                x.name = f[7].Get<std::string>(); x.matX = f[8].Get<float>(); x.matZ = f[9].Get<float>();
                GameObjectTemplate const* go = sObjectMgr->GetGameObjectTemplate(x.entry);
                if (go && go->type == GAMEOBJECT_TYPE_MAP_OBJECT)
                    s_fixtures[x.id] = std::move(x);
            } while (result->NextRow());
        if (QueryResult result = WorldDatabase.Query("SELECT component, type, pos_x, pos_y, pos_z, rot_deg "
            "FROM housing_exterior_fixture_hook ORDER BY id"))
            do
            {
                Field* f = result->Fetch();
                s_fixtureHooks[f[0].Get<uint32>()].push_back({ f[1].Get<uint8>(),
                    Rooms::Hook{ f[2].Get<float>(), f[3].Get<float>(), f[4].Get<float>(), f[5].Get<float>() } });
            } while (result->NextRow());
        s_plotSpot.clear();
        if (QueryResult result = CharacterDatabase.Query("SELECT neighborhood_id, plot, shape, spot, type FROM housing_plot_spot"))
            do
            {
                Field* f = result->Fetch();
                s_plotSpot[{ f[0].Get<uint32>(), f[1].Get<uint8>(), f[2].Get<uint32>(), f[3].Get<uint8>() }] = f[4].Get<uint8>();
            } while (result->NextRow());
        if (QueryResult result = CharacterDatabase.Query("SELECT neighborhood_id, plot, theme, type, component FROM housing_plot_fixture"))
            do
            {
                Field* f = result->Fetch();
                s_plotFixture[{ f[0].Get<uint32>(), f[1].Get<uint8>(), f[2].Get<uint32>(), f[3].Get<uint8>() }] = f[4].Get<uint32>();
            } while (result->NextRow());
        if (QueryResult result = WorldDatabase.Query("SELECT style, name FROM housing_exterior_style"))
            do
                s_exteriorStyles[result->Fetch()[0].Get<uint32>()] = result->Fetch()[1].Get<std::string>();
            while (result->NextRow());
        if (QueryResult result = CharacterDatabase.Query("SELECT neighborhood_id, plot, style, offset_x, offset_y, turn, offset_z, scale "
            "FROM housing_plot_style"))
            do
            {
                Field* f = result->Fetch();
                s_plotLook[{ f[0].Get<uint32>(), f[1].Get<uint8>() }] = { f[2].Get<uint32>(), f[3].Get<float>(), f[4].Get<float>(),
                    f[5].Get<float>(), f[6].Get<float>(), std::clamp(f[7].Get<float>(), HouseMinScale, HouseMaxScale) };
            } while (result->NextRow());

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
        s_plotRadius = 30;
        for (Plot const& a : s_plots)
            for (Plot const& b : s_plots)
                if (&a != &b && a.map == b.map)
                    s_plotRadius = std::min(s_plotRadius, 0.5f * std::hypot(a.house[0] - b.house[0], a.house[1] - b.house[1]));
        if (QueryResult result = WorldDatabase.Query("SELECT role, gameobject_entry, pos_x, pos_y, pos_z, rot_deg, style, mat_x, mat_z "
            "FROM housing_exterior_piece ORDER BY id"))
            do
            {
                Field* f = result->Fetch();
                ExteriorPiece e;
                e.role = f[0].Get<std::string>(); e.entry = f[1].Get<uint32>();
                for (int i = 0; i < 3; ++i) e.pos[i] = f[2 + i].Get<float>();
                e.rotDeg = f[5].Get<float>();
                e.style = f[6].Get<uint32>(); e.matX = f[7].Get<float>(); e.matZ = f[8].Get<float>();
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
                        r.layout.level = int8(std::clamp<int>(f[2].Get<int8>(), MinLevel, FloorCap - 1));
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

        if (QueryResult result = CharacterDatabase.Query("SELECT neighborhood_id, plot, house_id FROM housing_plot_claim"))
            do
            {
                Field* f = result->Fetch();
                Lot const lot{ f[0].Get<uint32>(), f[1].Get<uint8>() };
                if (!PlotOfLot(lot) || !s_houses.count(f[2].Get<uint32>()))
                    continue;
                s_plotHouse[lot] = f[2].Get<uint32>();
                s_houseLots[f[2].Get<uint32>()].insert(lot);
            } while (result->NextRow());

        if (QueryResult result = CharacterDatabase.Query("SELECT MAX(room_id) FROM housing_room"))
            s_nextRoomId = std::max<uint32>(1, result->Fetch()[0].Get<uint32>() + 1);
        if (QueryResult result = CharacterDatabase.Query("SELECT MAX(placed_id) FROM housing_placed_decor"))
            s_nextPlacedId = std::max<uint64>(1, result->Fetch()[0].Get<uint64>() + 1);

        if (QueryResult result = CharacterDatabase.Query("SELECT placed_id, house_id, decor_id, pos_x, pos_y, pos_z, rot_x, "
            "rot_y, rot_z, rot_w, scale, COALESCE(room_id, 0), neighborhood_id FROM housing_placed_decor"))
            do
            {
                Field* f = result->Fetch();
                auto house = s_houses.find(f[1].Get<uint32>());
                if (house == s_houses.end())
                    continue;
                Placed p;
                p.id = f[0].Get<uint64>(); p.decorId = f[2].Get<uint32>();
                for (int i = 0; i < 3; ++i) p.pos[i] = f[3 + i].Get<float>();
                for (int i = 0; i < 4; ++i) p.rot[i] = f[6 + i].Get<float>();
                p.scale = f[10].Get<float>();
                p.yaw = EsteriaHousing::SnapYaw(p.rot, 0);
                (f[11].Get<uint32>() ? house->second.placed : house->second.outdoor[f[12].Get<uint32>()])[p.id] = p;
            } while (result->NextRow());

        if (QueryResult result = CharacterDatabase.Query("SELECT account_id, decor_id, quantity_owned, quantity_placed "
            "FROM housing_account_decor"))
            do
            {
                Field* f = result->Fetch();
                s_owned[f[0].Get<uint32>()][f[1].Get<uint32>()] = { f[2].Get<uint16>(), f[3].Get<uint16>() };
            } while (result->NextRow());


        LoadCommerce();
        LoadAdventure();
        LoadCollections();
        s_loaded = true;
        LOG_INFO("module", "housing: loaded {} catalog entries, {} room templates, {} room kinds, {} houses, {} neighborhoods",
            s_catalog.size(), s_rooms.size(), s_kinds.size(), s_houses.size(), s_hoods.size());
        if (!DefaultRoom())
            LOG_ERROR("module", "housing: room template {} (EsteriaHousing.RoomTemplate) is missing", s_config.roomTemplate);
    }

    // ---------------------------------------------------------------- world objects

    float BaseScale(uint32 decorId)
    {
        auto entry = s_catalog.find(decorId);
        GameObjectTemplate const* t = entry == s_catalog.end() ? nullptr : sObjectMgr->GetGameObjectTemplate(entry->second.goEntry);
        return t && t->size > 0.0f ? t->size : 1.0f;
    }

    void Spawn(Map* map, Placed const& p)
    {
        if (ServiceKindOf(p.decorId) == ServiceMerchant)
            return SpawnMerchant(map, p);
        uint8 const adventure = AdventureKindOf(p.decorId);
        if (adventure >= AdvDummy && adventure <= AdvBoss)
            return SpawnDummy(map, p);
        uint8 const collection = CollectionKindOf(p.decorId);
        if (IsFigureKind(collection))
            return SpawnMannequin(map, p);
        auto entry = s_catalog.find(p.decorId);
        if (entry == s_catalog.end())
            return;
        uint32 const goEntry = adventure == AdvPortal ? PortalLookEntry(p.id) : adventure == AdvStone ? StoneLookEntry(p.id)
            : entry->second.goEntry;
        // Map::SummonGameObject, with the scale set before the object enters the map: the client builds a gameobject's
        // transform (CGGameObject_C::UpdateWorldObject) from OBJECT_FIELD_SCALE_X when it is created, and a later scale
        // update does not rebuild it.
        GameObject* go = new GameObject();
        if (go->Create(map->GenerateLowGuid<HighGuid::GameObject>(), goEntry, map, PHASEMASK_NORMAL, p.pos[0],
            p.pos[1], p.pos[2], p.yaw, G3D::Quat(p.rot[0], p.rot[1], p.rot[2], p.rot[3]), 100, GO_STATE_READY))
        {
            go->SetObjectScale(p.scale * (MatHidden(p.id) ? 0.01f : BaseScale(p.decorId)));
            go->SetRespawnTime(0);
            go->SetSpawnedByDefault(false);
            map->AddToMap(go, false);
            s_spawned[map->GetInstanceId()][p.id] = go->GetGUID();
            if (ServiceKindOf(p.decorId)) // a shop's name floats above it
                SpawnShopLabel(map, p);
            if (collection) // a trophy, mount or habitat's pets beside it
                SpawnDisplayExtras(map, p);
        }
        else
        {
            delete go;
            LOG_ERROR("module", "housing: could not spawn decor {} (placed {}) in instance {}", p.decorId, p.id,
                map->GetInstanceId());
        }
    }

    void Despawn(Map* map, uint64 placedId)
    {
        DespawnShopLabel(map, placedId);
        DespawnDisplayExtras(map, placedId);
        auto& spawned = s_spawned[map->GetInstanceId()];
        auto it = spawned.find(placedId);
        if (it == spawned.end())
            return;
        ForgetDisplayUnit(it->second);
        if (GameObject* go = it->second.IsGameObject() ? map->GetGameObject(it->second) : nullptr)
        {
            go->SetRespawnTime(0);
            go->Delete();
        }
        else if (Creature* c = it->second.IsGameObject() ? nullptr : map->GetCreature(it->second))
            c->DespawnOrUnsummon();
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

    // The next floor: 100 g for the 5th, 200 g for the 6th ... 1100 g for the 15th. 0 at the cap.
    uint32 FloorPrice(House const& house)
    {
        return house.floors >= FloorCap ? 0 : uint32(house.floors - BaseFloors + 1) * 100 * 10000;
    }

    // The next +100 decor: 10 g, then a gold more for each step bought. 0 at the cap.
    uint32 DecorPrice(House const& house)
    {
        return house.maxDecor >= DecorCap ? 0 : (10 + uint32(std::max<int>(0, house.maxDecor - DecorBase)) / DecorStep) * 10000;
    }

    uint32 MaxRooms(House const& house) { return std::max<uint32>(s_config.maxRooms, house.roomLimit); }

    // The next +4 rooms: 50 g, then 25 g more for each step bought. 0 at the cap.
    uint32 RoomLimitPrice(House const& house)
    {
        uint32 const now = MaxRooms(house);
        return now >= RoomCap ? 0 : (50 + (now > s_config.maxRooms ? (now - s_config.maxRooms) / RoomStep : 0) * 25) * 10000;
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

    constexpr float DecorMinScale = 0.5f, DecorMaxScale = 2.0f; // the catalog's range (make_slice.py writes it per decor)

    void SendHello(WorldSession* session)
    {
        WorldPacket data(SMSG_ESTERIA_HOUSING_HELLO, 32);
        RoomTemplate const* room = DefaultRoom();
        data << uint16(Proto) << uint8(s_config.enabled && s_loaded && room) << uint32(0) << uint32(s_catalog.size())
             << uint16(room ? room->maxDecor : 0) << DecorMinScale << DecorMaxScale << float(15);
        session->SendPacket(&data);
    }

    // Whether `kind` can be built through socket (room, piece): it fits there, and a stairwell also needs the floor above
    // free for its top (and a floor left to climb to).
    bool Fits(std::vector<Rooms::Room> const& layouts, size_t room, size_t piece, uint32 kind, int8 maxLevel)
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
        return placed->level < maxLevel && Rooms::Fits(s_kinds, layouts, top);
    }

    // The owner's blueprint: room kinds, the rooms placed, and every free wall with the kinds that fit through it.
    void SendLayout(Player* player, House const& house, RoomTemplate const& room)
    {
        std::vector<Rooms::Room> const layouts = Layouts(house);
        WorldPacket data(SMSG_ESTERIA_HOUSING_LAYOUT, 512);
        data << uint8(MaxRooms(house)) << room.Origin(0) << room.Origin(1);
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
        bool const full = layouts.size() >= MaxRooms(house);
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
                    if (id != StairwellTop && Fits(layouts, r, i, id, house.MaxLevel()))
                        fits.push_back(id);
                    if (IsStairwell(id) && Fits(layouts, r, i, StairsDownBase + id, house.MaxLevel()))
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
        data << house.floors << FloorPrice(house) << DecorPrice(house) << DecorStep << DecorCap << RoomLimitPrice(house)
             << RoomStep << RoomCap;
        player->SendDirectMessage(&data);
    }

    // The owner standing on one of their own plots in the neighborhood they are in: its house, plot and neighborhood.
    struct OwnPlot { House* house = nullptr; Plot const* plot = nullptr; uint32 hood = 0; };
    OwnPlot OnOwnPlot(Player* player)
    {
        Hood const* hood = player ? HoodOfMap(player->GetMap()) : nullptr;
        if (!hood)
            return {};
        auto mine = s_accountHouses.find(player->GetSession()->GetAccountId());
        if (mine == s_accountHouses.end())
            return {};
        for (auto const& [lot, houseId] : s_plotHouse)
        {
            if (lot.first != hood->id || std::find(mine->second.begin(), mine->second.end(), houseId) == mine->second.end())
                continue;
            Plot const* plot = FindPlot(hood->Map(), lot.second);
            if (plot && std::fabs(player->GetPositionX() - plot->house[0]) <= s_plotRadius
                && std::fabs(player->GetPositionY() - plot->house[1]) <= s_plotRadius)
                return { &s_houses[houseId], plot, hood->id };
        }
        return {};
    }

    void SendState(Player* player)
    {
        House const* house = HouseOfInstance(player->GetMap());
        RoomTemplate const* room = house ? Room(*house) : nullptr;
        OwnPlot const own = house ? OwnPlot{} : OnOwnPlot(player);
        if (own.house)
        {
            // outside: the plot's decor, in a box around the house's spot
            House* plotHouse = own.house;
            Plot const* plot = own.plot;
            std::map<uint64, Placed> const& outdoor = plotHouse->outdoor[own.hood];
            WorldPacket data(SMSG_ESTERIA_HOUSING_STATE, 64 + outdoor.size() * 44);
            data << uint8(1) << uint8(1) << uint8(1) << plotHouse->id << plotHouse->revision << uint16(outdoor.size())
                 << OutdoorBudget;
            data << (plot->house[0] - s_plotRadius) << (plot->house[1] - s_plotRadius) << (plot->house[2] - 10)
                 << (plot->house[0] + s_plotRadius) << (plot->house[1] + s_plotRadius) << (plot->house[2] + 30);
            data << uint16(outdoor.size());
            for (auto const& [id, p] : outdoor)
                data << uint64(id) << uint32(p.decorId) << p.pos[0] << p.pos[1] << p.pos[2] << p.rot[0] << p.rot[1] << p.rot[2]
                     << p.rot[3] << p.scale;
            auto const look = s_plotLook.find({ own.hood, plot->index });
            PlotLook const l = look == s_plotLook.end() ? PlotLook{} : look->second;
            data << plot->house[0] << plot->house[1] << plot->house[2] << plot->house[3] << l.dx << l.dy << l.dz << l.turn << l.scale
                 << PlotReachYd;
            player->SendDirectMessage(&data);
            return;
        }
        WorldPacket data(SMSG_ESTERIA_HOUSING_STATE, 64 + (house ? house->placed.size() * 44 : 0));
        data << uint8(house && room) << uint8(house && house->account == player->GetSession()->GetAccountId()) << uint8(0)
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
                data << uint64(id) << uint32(p.decorId) << p.pos[0] << p.pos[1] << p.pos[2] << p.rot[0] << p.rot[1]
                     << p.rot[2] << p.rot[3] << p.scale;
            }
        }
        for (int i = 0; i < 10; ++i) // no plot house indoors
            data << 0.0f;
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
        if (e.category == 9) // services: a trainer or auctioneer is an investment
        {
            uint8 const k = CollectionKindOf(e.decorId);
            return (k == ColTrainer || k == ColAuctioneer ? 100 : k == ColStation || k == ColMailbox ? 10 : 50) * 10000;
        }
        return (e.category < 6 ? gold[e.category] : 1) * 10000;
    }

    // Purchases answer with one catalog refresh once the buying stops: a cart buys many decor in a burst, and a refresh per
    // purchase started as many page-by-page passes on the client, which spliced its list together (player id -> ms left).
    std::unordered_map<ObjectGuid, uint32> s_catalogDue;
    constexpr uint32 CatalogSettleMs = 400;

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
            uint16 const used = o == owned.end() ? 0 : o->second.placed;
            uint16 const have = ServiceKindOf(e.decorId) ? uint16(used + 99) : o == owned.end() ? 0 : o->second.owned; // shops cost only decor budget
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
        return Acore::StringFormat("{{\"decor\":{},\"x\":{},\"y\":{},\"z\":{},\"rot\":[{},{},{},{}],\"scale\":{}}}",
            p.decorId, p.pos[0], p.pos[1], p.pos[2], p.rot[0], p.rot[1], p.rot[2], p.rot[3], p.scale);
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
        Plot const* plot = nullptr;
        uint32 hood = 0;
        if (!house && player)
        {
            OwnPlot const own = OnOwnPlot(player);
            house = own.house; plot = own.plot; hood = own.hood;
        }
        bool const outdoors = plot != nullptr;
        std::map<uint64, Placed>* decor = house ? (outdoors ? &house->outdoor[hood] : &house->placed) : nullptr;
        EditSession& state = s_editSessions[account];
        uint64 const now = GameTime::GetGameTimeMS().count();
        while (!state.recent.empty() && now - state.recent.front() >= 1000)
            state.recent.pop_front();

        EsteriaHousing::Facts f;
        f.enabled = s_config.enabled && s_loaded;
        f.inHouse = house && (room || outdoors);
        f.isOwner = house && house->account == account;
        f.lastSeq = state.lastSeq;
        f.revision = house ? house->revision : 0;
        f.decorKnown = s_catalog.count(e.decorId) != 0;
        auto& owned = s_owned[account];
        if (auto o = owned.find(e.decorId); o != owned.end())
            f.available = o->second.owned > o->second.placed ? o->second.owned - o->second.placed : 0;
        if (ServiceKindOf(e.decorId))
            f.available = 99;
        f.placementKnown = decor && decor->count(e.placedId);
        f.placed = decor ? uint32(decor->size()) : 0;
        f.maxDecor = house ? (outdoors ? OutdoorBudget : house->maxDecor) : 0;
        if (outdoors) // the plot's box: as SendState gives it
        {
            f.boundsMin[0] = plot->house[0] - s_plotRadius; f.boundsMax[0] = plot->house[0] + s_plotRadius;
            f.boundsMin[1] = plot->house[1] - s_plotRadius; f.boundsMax[1] = plot->house[1] + s_plotRadius;
            f.boundsMin[2] = plot->house[2] - 10; f.boundsMax[2] = plot->house[2] + 30;
        }
        // Bounds are those of the room the decor lands in; outside every room, an empty box refuses it.
        if (room && house && !outdoors)
        {
            int const at = RoomAt(*house, *room, e.pos[0], e.pos[1], e.pos[2]);
            if (at < 0 || !RoomBox(*house, *room, size_t(at), f.boundsMin, f.boundsMax))
                for (int i = 0; i < 3; ++i) { f.boundsMin[i] = 1; f.boundsMax[i] = 0; }
        }
        // a move carries no decorId; its scale range is that of the decor already placed
        uint32 const decorId = e.op == OpPlace || !decor || !decor->count(e.placedId) ? e.decorId : decor->at(e.placedId).decorId;
        if (auto c = s_catalog.find(decorId); c != s_catalog.end())
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
        // a shop with goods still for sale stays until its owner empties it (the items would otherwise be mailed off unasked)
        if (e.op == OpRemove && HasStockForSale(e.placedId))
            return SendAck(session, e.seq, ShopHasStock, house->revision, e.placedId, nullptr);

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
            Placed p{ placedId, e.decorId, { out.pos[0], out.pos[1], out.pos[2] }, out.yaw,
                { out.rot[0], out.rot[1], out.rot[2], out.rot[3] }, out.scale };
            (*decor)[placedId] = p;
            ++owned[e.decorId].placed;
            trans->Append("INSERT INTO housing_placed_decor (placed_id, house_id, room_id, neighborhood_id, decor_id, pos_x, pos_y, "
                "pos_z, rot_x, rot_y, rot_z, rot_w, scale, placed_by, placed_at) VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, "
                "{}, {}, {})", placedId, house->id, outdoors ? std::string("NULL") : std::to_string(house->roomId), hood, e.decorId,
                out.pos[0], out.pos[1], out.pos[2], out.rot[0], out.rot[1], out.rot[2], out.rot[3], out.scale, character, now32);
            trans->Append("UPDATE housing_account_decor SET quantity_placed = quantity_placed + 1 WHERE account_id = {} AND decor_id = {}",
                account, e.decorId);
            after = "'" + Json(p) + "'";
            ShopPlaced(*house, p, player, trans);
            HouseholdPlaced(p, house->account, trans);
            Spawn(map, p);
            MerchantJustPlaced(player, p);
        }
        else if (e.op == OpMove)
        {
            Placed& p = (*decor)[placedId];
            before = "'" + Json(p) + "'";
            for (int i = 0; i < 3; ++i) p.pos[i] = out.pos[i];
            p.yaw = out.yaw;
            for (int i = 0; i < 4; ++i) p.rot[i] = out.rot[i];
            p.scale = out.scale;
            trans->Append("UPDATE housing_placed_decor SET pos_x = {}, pos_y = {}, pos_z = {}, rot_x = {}, rot_y = {}, rot_z = {}, "
                "rot_w = {}, scale = {} WHERE placed_id = {} AND house_id = {}", out.pos[0], out.pos[1], out.pos[2], out.rot[0],
                out.rot[1], out.rot[2], out.rot[3], out.scale, placedId, house->id);
            after = "'" + Json(p) + "'";
            Despawn(map, placedId);
            Spawn(map, p);
        }
        else
        {
            Placed const p = (*decor)[placedId];
            before = "'" + Json(p) + "'";
            decor->erase(placedId);
            if (Owned& o = owned[p.decorId]; o.placed)
                --o.placed;
            trans->Append("DELETE FROM housing_placed_decor WHERE placed_id = {} AND house_id = {}", placedId, house->id);
            trans->Append("UPDATE housing_account_decor SET quantity_placed = quantity_placed - 1 WHERE account_id = {} "
                "AND decor_id = {} AND quantity_placed > 0", account, p.decorId);
            ShopRemoved(placedId, trans);
            AdventureRemoved(placedId, trans);
            CollectionRemoved(placedId, trans);
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
        if (outdoors)
            SendState(player); // others in the neighborhood see the decor itself; only the editor needs the list
        else
            BroadcastState(map);
    }

    void Leave(Player* player)
    {
        auto it = s_returnTo.find(player->GetGUID());
        if (it != s_returnTo.end())
        {
            WorldLocation const to = it->second;
            s_returnTo.erase(it);
            // back into the neighborhood the house was entered from
            if (auto hood = s_returnHood.find(player->GetGUID()); hood != s_returnHood.end())
            {
                if (IsNeighborhoodMap(to.GetMapId()))
                    s_pendingHood[player->GetGUID()] = hood->second;
                s_returnHood.erase(hood);
            }
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

    // A neighborhood map's instance for whoever is entering it: the neighborhood they are traveling to, the one they
    // were last in (a relog), else their own.
    uint32 PickHoodInstance(Player* player, uint32 mapId)
    {
        uint32 hoodId = 0;
        if (auto it = s_pendingHood.find(player->GetGUID()); it != s_pendingHood.end())
            hoodId = it->second;
        else if (auto last = s_lastHood.find(player->GetGUID()); last != s_lastHood.end())
            hoodId = last->second;
        Hood* hood = FindHood(hoodId);
        if (!hood || hood->Map() != mapId)
            hood = &AccountHood(player->GetSession()->GetAccountId());
        if (hood->Map() != mapId)
            return 0; // the stock instance, which sends them home (EsteriaHousingMaps)
        uint32& instanceId = s_hoodInstance[hood->id];
        if (!instanceId || !sMapMgr->FindMap(mapId, instanceId))
        {
            if (instanceId)
                s_instanceHood.erase(instanceId);
            instanceId = sMapMgr->GenerateInstanceId();
            s_instanceHood[instanceId] = hood->id;
        }
        if (InstancePlayerBind* bind = sInstanceSaveMgr->PlayerGetBoundInstance(player->GetGUID(), mapId, DUNGEON_DIFFICULTY_NORMAL))
            if (!bind->perm && bind->save && bind->save->GetInstanceId() != instanceId)
                sInstanceSaveMgr->PlayerUnbindInstance(player->GetGUID(), mapId, DUNGEON_DIFFICULTY_NORMAL, true, player);
        return instanceId;
    }

    // MapInstanced hook: the owner's instance for whoever is entering a house, the neighborhood's for a neighborhood.
    uint32 PickInstance(Player* player, uint32 mapId)
    {
        std::lock_guard<std::recursive_mutex> guard(s_lock);
        if (s_config.enabled && s_loaded && IsNeighborhoodMap(mapId))
            return PickHoodInstance(player, mapId);
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
        EsteriaHousingHooks::MirrorImage.store(s_config.enabled ? &MerchantMirrorImage : nullptr);
    }

    bool EnterHouse(Player* player, House const& house, Position const* at = nullptr)
    {
        RoomTemplate const* room = Room(house);
        if (!room)
            return false;
        if (!IsHousingMap(player->GetMapId()))
        {
            s_returnTo[player->GetGUID()] = WorldLocation(player->GetMapId(), player->GetPositionX(), player->GetPositionY(),
                player->GetPositionZ(), player->GetOrientation());
            if (Hood const* hood = HoodOfMap(player->GetMap()))
                s_returnHood[player->GetGUID()] = hood->id;
            else
                s_returnHood.erase(player->GetGUID());
        }
        House const* inside = HouseOfInstance(player->GetMap());
        s_pending[player->GetGUID()] = house.id;
        LOG_INFO("module", "housing: {} enters house {} (owner account {})", player->GetName(), house.id, house.account);
        // from another house: the same map, but that house's instance
        Position const door(room->entry[0], room->entry[1], room->entry[2], room->entry[3]);
        Position const& to = at ? *at : door;
        return player->TeleportTo(room->mapId, to.GetPositionX(), to.GetPositionY(), to.GetPositionZ(), to.GetOrientation(), 0, nullptr,
            inside && inside->id != house.id);
    }

    // Starter decor: StarterQuantity of every catalog entry. shortcut: grants stand in for acquisition (vendors, drops).
    void GrantStarter(uint32 account, CharacterDatabaseTransaction trans)
    {
        auto& owned = s_owned[account];
        for (auto const& [decorId, entry] : s_catalog)
        {
            if (entry.category == 9) // services are bought
                continue;
            Owned& o = owned[decorId];
            if (o.owned >= s_config.starterQuantity)
                continue;
            o.owned = s_config.starterQuantity;
            trans->Append("INSERT INTO housing_account_decor (account_id, decor_id, quantity_owned, quantity_placed) "
                "VALUES ({}, {}, {}, 0) ON DUPLICATE KEY UPDATE quantity_owned = GREATEST(quantity_owned, VALUES(quantity_owned))",
                account, decorId, o.owned);
        }
    }

    // A new house for the player's account (an account may own any number).
    House* Claim(Player* player)
    {
        uint32 const account = player->GetSession()->GetAccountId();
        RoomTemplate const* room = DefaultRoom();
        if (!room)
            return nullptr;
        House h;
        h.id = s_nextHouseId++;
        h.roomId = s_nextRoomId++;
        h.account = account;
        h.roomTemplate = room->id;
        h.maxDecor = room->maxDecor;
        h.owner = player->GetName();
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
        s_accountHouses[account].push_back(h.id);
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
        if (house.rooms.size() + needed > MaxRooms(house))
            return "Your house already has the most rooms it can hold.";
        std::vector<Rooms::Room> const layouts = Layouts(house);
        if (kind > StairsDownBase)
        {
            uint32 const stairwell = kind - StairsDownBase;
            if (!Fits(layouts, room, piece, kind, house.MaxLevel()))
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
        if (kind == StairwellTop || !s_kinds.count(kind) || !Fits(layouts, room, piece, kind, house.MaxLevel()))
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
        if (!below || layouts[room].level >= house.MaxLevel() || !Rooms::Fits(s_kinds, layouts, top))
            return "There is no space for stairs above that.";
        if (house.rooms.size() + 1 > MaxRooms(house))
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

    PlotLook LookOf(Lot const& lot)
    {
        auto it = s_plotLook.find(lot);
        return it == s_plotLook.end() ? PlotLook{} : it->second;
    }

    // Whether a part fits a style: its theme, and for walls and roofs its size too.
    bool Fits(Fixture const& x, uint32 style, uint8 type)
    {
        return x.type == type && x.theme == style / 10 && ((type != FixtureBase && type != FixtureRoof) || x.size == style % 10);
    }

    // The part of this type the plot's house has: the owner's choice where it still fits, else the style's default.
    Fixture const* PartOf(Lot const& lot, uint32 style, uint8 type)
    {
        if (auto c = s_plotFixture.find({ lot.first, lot.second, style / 10, type }); c != s_plotFixture.end())
            if (auto x = s_fixtures.find(c->second); x != s_fixtures.end() && Fits(x->second, style, type))
                return &x->second;
        for (auto const& [id, x] : s_fixtures)
            if (x.isDefault && Fits(x, style, type))
                return &x;
        return nullptr;
    }

    // The hooks of one type on a part; a colour variant has its shape's.
    std::vector<Rooms::Hook> HooksOn(Fixture const& x, uint8 type)
    {
        auto it = s_fixtureHooks.find(x.id);
        if (it == s_fixtureHooks.end())
            it = s_fixtureHooks.find(x.parent);
        std::vector<Rooms::Hook> out;
        if (it != s_fixtureHooks.end())
            for (auto const& [t, h] : it->second)
                if (t == type)
                    out.push_back(h);
        return out;
    }

    // The spots of a base or roof (its shape's hooks), grouped by place: a tower and a chimney share a spot though their
    // hooks may differ a yard in height.
    std::vector<Spot> SpotsOn(Fixture const& x)
    {
        uint32 const shape = s_fixtureHooks.count(x.id) ? x.id : x.parent;
        std::vector<Spot> out;
        auto it = s_fixtureHooks.find(shape);
        if (it == s_fixtureHooks.end())
            return out;
        for (auto const& [type, h] : it->second)
        {
            if (!SpotBit(type))
                continue;
            Spot* spot = nullptr;
            for (Spot& o : out)
            {
                Rooms::Hook const& f = o.hooks.begin()->second;
                if (std::fabs(f.x - h.x) < 0.3f && std::fabs(f.y - h.y) < 0.3f && std::fabs(f.z - h.z) < 1.5f)
                    spot = &o;
            }
            if (!spot)
            {
                out.push_back({ shape, uint8(out.size()), 0, {} });
                spot = &out.back();
            }
            spot->accepts |= SpotBit(type);
            spot->hooks.emplace(type, h); // the first hook of a type there
        }
        return out;
    }

    std::vector<Spot> HouseSpots(Fixture const& base, Fixture const& roof)
    {
        std::vector<Spot> spots = SpotsOn(base);
        for (Spot& s : SpotsOn(roof))
            spots.push_back(std::move(s));
        return spots;
    }

    // What stands on a spot: the owner's choice, else a chimney on the roof's first chimney spot (the house every plot
    // had before spots), else nothing.
    uint8 SpotType(Lot const& lot, std::vector<Spot> const& spots, size_t i, uint32 roofShape)
    {
        Spot const& s = spots[i];
        if (auto c = s_plotSpot.find({ lot.first, lot.second, s.shape, s.local }); c != s_plotSpot.end())
            return (s.accepts & SpotBit(c->second)) ? c->second : 0;
        if (s.shape != roofShape || !(s.accepts & SpotChimney))
            return 0;
        for (size_t k = 0; k < i; ++k)
            if (spots[k].shape == roofShape && (spots[k].accepts & SpotChimney))
                return 0;
        return FixtureChimney;
    }

    // The exterior on a plot: the owner's parts on their hooks, plus the door on the hook facing the cornerstone.
    // door receives the spot just outside that door, where walking in enters the house.
    std::vector<Placement> Exterior(Lot const& lot, Plot const& plot, Rooms::Pose* door = nullptr)
    {
        std::vector<Placement> out;
        std::vector<Rooms::Hook> doors;
        std::vector<uint32> doorEntries;
        std::vector<std::pair<float, float>> doorMats; // x out of the door, z up
        uint32 frontDoor = 0;
        PlotLook const l = LookOf(lot);
        // where the house stands: the plot's spot, moved and turned as its owner set it
        float const hx = plot.house[0] + l.dx, hy = plot.house[1] + l.dy, hz = plot.house[2] + l.dz;
        float const s = l.scale;
        float const yaw = plot.house[3] + l.turn * float(M_PI) / 180;
        // The parts the owner picked, on their hooks (housing_exterior_fixture); the fixed recipe below when the world
        // data has no parts for this style.
        Fixture const* base = PartOf(lot, l.style, FixtureBase);
        Fixture const* roof = PartOf(lot, l.style, FixtureRoof);
        Fixture const* doorPart = PartOf(lot, l.style, FixtureDoor);
        bool const parts = base && roof && doorPart && !HooksOn(*base, FixtureDoor).empty();
        if (parts)
        {
            auto const put = [&](uint32 entry, Rooms::Hook const& h) {
                Rooms::Pose const p = Rooms::OnPlot(hx, hy, hz, yaw, { h.x * s, h.y * s, h.z * s, h.rotDeg });
                Placement placement{ entry, p.x, p.y, p.z, p.yaw };
                placement.scale = s;
                out.push_back(placement);
            };
            put(base->entry, {});
            put(roof->entry, {});
            if (Fixture const* window = PartOf(lot, l.style, FixtureWindow))
                for (Rooms::Hook const& h : HooksOn(*base, FixtureWindow))
                    put(window->entry, h);
            std::vector<Spot> const spots = HouseSpots(*base, *roof);
            uint32 const roofShape = s_fixtureHooks.count(roof->id) ? roof->id : roof->parent;
            for (size_t i = 0; i < spots.size(); ++i)
                if (uint8 const type = SpotType(lot, spots, i, roofShape))
                    if (Fixture const* part = PartOf(lot, l.style, type))
                        put(part->entry, spots[i].hooks.at(type));
            for (Rooms::Hook const& h : HooksOn(*base, FixtureDoor))
            {
                doors.push_back({ h.x * s, h.y * s, h.z * s, h.rotDeg });
                doorEntries.push_back(doorPart->entry);
                doorMats.push_back({ doorPart->matX, doorPart->matZ });
            }
        }
        for (ExteriorPiece const& e : s_exterior)
        {
            Rooms::Hook const h{ e.pos[0], e.pos[1], e.pos[2], e.rotDeg };
            if (e.role == "front_door")
            {
                frontDoor = e.entry;
                continue;
            }
            if (e.style != l.style || parts)
                continue;
            if (e.role == "door_hook")
            {
                doors.push_back(h);
                doorEntries.push_back(e.entry);
                doorMats.push_back({ e.matX, e.matZ });
                continue;
            }
            Rooms::Pose const p = Rooms::OnPlot(hx, hy, hz, yaw, h);
            out.push_back({ e.entry, p.x, p.y, p.z, p.yaw });
        }
        if (!doors.empty())
        {
            size_t const i = Rooms::FrontDoor(hx, hy, hz, yaw, doors, plot.corner[0], plot.corner[1]);
            Rooms::Pose const p = Rooms::OnPlot(hx, hy, hz, yaw, doors[i]);
            Placement piece{ doorEntries[i], p.x, p.y, p.z, p.yaw };
            piece.scale = s;
            out.push_back(piece);
            if (frontDoor)
                out.push_back({ frontDoor, p.x + p.nx * doorMats[i].first * s, p.y + p.ny * doorMats[i].first * s,
                    p.z + doorMats[i].second * s, p.yaw });
            if (door)
            {
                *door = p;
                door->x += p.nx * 1.5f;
                door->y += p.ny * 1.5f;
            }
        }
        return out;
    }

    // One exterior piece, a temporary GameObject in a neighborhood's instance (sized before it enters the map, as Spawn).
    ObjectGuid SpawnPiece(Map* map, Placement const& p)
    {
        GameObjectTemplate const* info = sObjectMgr->GetGameObjectTemplate(p.entry);
        if (!info)
            return ObjectGuid::Empty;
        bool const turnOnly = !p.rot[0] && !p.rot[1] && !p.rot[2] && !p.rot[3];
        G3D::Quat const rotation = turnOnly ? G3D::Quat::fromAxisAngleRotation(G3D::Vector3::unitZ(), p.yaw)
            : G3D::Quat(p.rot[0], p.rot[1], p.rot[2], p.rot[3]);
        GameObject* go = new GameObject();
        if (!go->Create(map->GenerateLowGuid<HighGuid::GameObject>(), info->entry, map, PHASEMASK_NORMAL, p.x, p.y, p.z, p.yaw,
            rotation, 0, GO_STATE_READY))
        {
            delete go;
            return ObjectGuid::Empty;
        }
        go->SetObjectScale(p.scale);
        go->SetRespawnTime(0);
        go->SetSpawnedByDefault(false);
        map->AddToMap(go, false);
        return go->GetGUID();
    }

    void ClearExterior(Map* map, uint8 index)
    {
        auto& lots = s_lotSpawned[map->GetInstanceId()];
        auto it = lots.find(index);
        if (it == lots.end())
            return;
        for (ObjectGuid const& guid : it->second)
            if (GameObject* go = map->GetGameObject(guid))
            {
                go->SetRespawnTime(0);
                go->Delete();
            }
        lots.erase(it);
    }

    // The house on a plot, rebuilt in its neighborhood's live instance (map, else the live one, if any) after anything
    // about it changed; nothing stands on a free plot.
    void RefreshExterior(Lot const& lot, Map* map = nullptr)
    {
        Hood const* hood = FindHood(lot.first);
        if (!map && hood)
            map = LiveMap(*hood);
        Plot const* plot = PlotOfLot(lot);
        if (!map || !plot)
            return;
        ClearExterior(map, lot.second);
        if (!s_plotHouse.count(lot))
            return;
        auto& spawned = s_lotSpawned[map->GetInstanceId()][lot.second];
        for (Placement const& p : Exterior(lot, *plot))
            if (ObjectGuid const guid = SpawnPiece(map, p); !guid.IsEmpty())
                spawned.push_back(guid);
    }

    // A neighborhood instance's houses and outdoor decor, once, as the first player arrives.
    void PopulateHood(Map* map, Hood const& hood)
    {
        if (!s_populated.insert(map->GetInstanceId()).second)
            return;
        size_t houses = 0, decor = 0;
        for (auto const& [lot, houseId] : s_plotHouse)
        {
            if (lot.first != hood.id)
                continue;
            RefreshExterior(lot, map);
            for (auto const& [id, p] : s_houses[houseId].outdoor[hood.id])
            {
                Spawn(map, p);
                ++decor;
            }
            ++houses;
        }
        LOG_INFO("module", "housing: neighborhood {} populated instance {} with {} houses and {} outdoor decor", hood.id,
            map->GetInstanceId(), houses, decor);
    }

    // A house's outdoor decor on its plot in one neighborhood goes back to the account's storage.
    void ReturnOutdoor(House& house, uint32 hoodId, CharacterDatabaseTransaction trans)
    {
        Hood const* hood = FindHood(hoodId);
        Map* map = hood ? LiveMap(*hood) : nullptr;
        auto& owned = s_owned[house.account];
        for (auto const& [id, p] : house.outdoor[hoodId])
        {
            if (map)
                Despawn(map, id);
            ShopRemoved(id, trans);
            AdventureRemoved(id, trans);
            CollectionRemoved(id, trans);
            if (Owned& o = owned[p.decorId]; o.placed)
                --o.placed;
            trans->Append("UPDATE housing_account_decor SET quantity_placed = quantity_placed - 1 WHERE account_id = {} "
                "AND decor_id = {} AND quantity_placed > 0", house.account, p.decorId);
        }
        trans->Append("DELETE FROM housing_placed_decor WHERE house_id = {} AND room_id IS NULL AND neighborhood_id = {}", house.id,
            hoodId);
        house.outdoor.erase(hoodId);
    }

    // Takes a house off a plot. The house, its rooms and indoor decor stay (saved, to stand on another plot); its outdoor
    // decor there goes back to storage.
    void ReleaseLot(Lot const& lot)
    {
        auto claim = s_plotHouse.find(lot);
        if (claim == s_plotHouse.end())
            return;
        uint32 const houseId = claim->second;
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        ReturnOutdoor(s_houses[houseId], lot.first, trans);
        trans->Append("DELETE FROM housing_plot_claim WHERE neighborhood_id = {} AND plot = {}", lot.first, lot.second);
        for (char const* table : { "housing_plot_style", "housing_plot_fixture", "housing_plot_spot" })
            trans->Append("DELETE FROM {} WHERE neighborhood_id = {} AND plot = {}", table, lot.first, lot.second);
        CharacterDatabase.CommitTransaction(trans);
        s_plotLook.erase(lot);
        for (auto it = s_plotFixture.begin(); it != s_plotFixture.end();)
            it = std::get<0>(it->first) == lot.first && std::get<1>(it->first) == lot.second ? s_plotFixture.erase(it) : std::next(it);
        for (auto it = s_plotSpot.begin(); it != s_plotSpot.end();)
            it = std::get<0>(it->first) == lot.first && std::get<1>(it->first) == lot.second ? s_plotSpot.erase(it) : std::next(it);
        s_plotHouse.erase(claim);
        s_houseLots[houseId].erase(lot);
        RefreshExterior(lot); // clears it
        LOG_INFO("module", "housing: house {} left plot {} of neighborhood {}", houseId, lot.second, lot.first);
    }

    // Puts a house on a plot: houseId 0 builds a new one; an existing house is mirrored there (the same rooms and decor
    // as wherever else it stands).
    std::string ClaimPlot(Player* player, Hood const& hood, Plot const& plot, uint32 houseId)
    {
        Lot const lot{ hood.id, plot.index };
        if (s_plotHouse.count(lot))
            return "Someone has already claimed this plot.";
        House* house = nullptr;
        if (houseId)
        {
            auto it = s_houses.find(houseId);
            if (it == s_houses.end() || it->second.account != player->GetSession()->GetAccountId())
                return "That is not your house.";
            house = &it->second;
            for (Lot const& l : s_houseLots[houseId])
                if (l.first == hood.id)
                    return "That house already stands in this neighborhood.";
        }
        else if (!(house = Claim(player)))
            return "Housing could not create your house.";
        CharacterDatabase.Execute("INSERT INTO housing_plot_claim (neighborhood_id, plot, house_id, spawns, claimed_at) "
            "VALUES ({}, {}, {}, '', {})", hood.id, plot.index, house->id, uint32(GameTime::GetGameTime().count()));
        s_plotHouse[lot] = house->id;
        s_houseLots[house->id].insert(lot);
        RefreshExterior(lot);
        SyncHomeSpells(player); // a first house teaches Teleport: Home and Portal: Home
        LOG_INFO("module", "housing: {} put house {} on plot {} of neighborhood {}", player->GetName(), house->id, plot.index,
            hood.id);
        return "";
    }

    // The accounts a player is tied to, for house access: grouped with, befriended by, and sharing a guild with.
    struct Ties
    {
        std::unordered_set<uint32> party, friends, guild;
    };

    Ties TiesOf(Player* player)
    {
        Ties t;
        if (Group* group = player->GetGroup())
            for (GroupReference* ref = group->GetFirstMember(); ref; ref = ref->next())
                if (ref->GetSource())
                    t.party.insert(ref->GetSource()->GetSession()->GetAccountId());
        // accounts with a character that has this one on its friends list (character_social flag 1: friend)
        if (QueryResult r = CharacterDatabase.Query("SELECT DISTINCT c.account FROM character_social s JOIN characters c "
            "ON c.guid = s.guid WHERE s.friend = {} AND (s.flags & 1)", player->GetGUID().GetCounter()))
            do t.friends.insert(r->Fetch()[0].Get<uint32>()); while (r->NextRow());
        if (uint32 const guild = player->GetGuildId())
            if (QueryResult r = CharacterDatabase.Query("SELECT DISTINCT c.account FROM guild_member m JOIN characters c "
                "ON c.guid = m.guid WHERE m.guildid = {}", guild))
                do t.guild.insert(r->Fetch()[0].Get<uint32>()); while (r->NextRow());
        return t;
    }

    bool MayEnter(uint32 account, Ties const& t, House const& house)
    {
        return house.account == account || (house.access & AccessEveryone)
            || ((house.access & AccessParty) && t.party.count(house.account))
            || ((house.access & AccessFriends) && t.friends.count(house.account))
            || ((house.access & AccessGuild) && t.guild.count(house.account));
    }

    // The owner, or whoever the house's access lets in.
    bool MayEnter(Player* player, House const& house)
    {
        uint32 const account = player->GetSession()->GetAccountId();
        return house.account == account || (house.access & AccessEveryone) || MayEnter(account, TiesOf(player), house);
    }

    // A guild member's rights in their guild's neighborhoods: the Guild Master has every one, other ranks what the
    // Guild Master gave them.
    uint8 GuildRights(Player* player, uint32 guildId)
    {
        if (!guildId || player->GetGuildId() != guildId)
            return 0;
        Guild const* guild = sGuildMgr->GetGuildById(guildId);
        if (guild && guild->GetLeaderGUID() == player->GetGUID())
            return RightBuy | RightInvite | RightManage;
        auto it = s_guildRights.find({ guildId, player->GetRank() });
        return it == s_guildRights.end() ? DefaultRankRights : it->second;
    }

    // What a player may do in a neighborhood (Right bits): its owner everything, someone it invited buy plots.
    uint8 RightsIn(Player* player, Hood const& hood)
    {
        uint32 const account = player->GetSession()->GetAccountId();
        if (hood.kind == HoodGuild)
            return GuildRights(player, hood.owner);
        return hood.owner == account ? RightBuy | RightInvite | RightManage : hood.members.count(account) ? RightBuy : 0;
    }

    // Who may come into a neighborhood: its owner, its guild, those it invited, and anyone a house there lets in.
    bool MayEnterHood(Player* player, Hood const& hood, Ties const& ties)
    {
        uint32 const account = player->GetSession()->GetAccountId();
        if (RightsIn(player, hood) || hood.members.count(account) || (hood.kind == HoodGuild && player->GetGuildId() == hood.owner))
            return true;
        for (auto const& [lot, houseId] : s_plotHouse)
            if (lot.first == hood.id && MayEnter(account, ties, s_houses[houseId]))
                return true;
        return false;
    }

    bool MayEnterHood(Player* player, Hood const& hood) { return MayEnterHood(player, hood, TiesOf(player)); }

    // Saves who may visit, and sends out whoever is inside and no longer may.
    void SetAccess(House& house, uint8 access)
    {
        house.access = access & (AccessEveryone | AccessFriends | AccessGuild | AccessParty);
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        for (uint8 scope : { 0, 1, 2, 4 })
            trans->Append("REPLACE INTO housing_permission (house_id, scope, grantee, can_visit, can_edit) VALUES ({}, {}, 0, {}, 0)",
                house.id, scope, (house.access >> scope) & 1);
        CharacterDatabase.CommitTransaction(trans);
        LOG_INFO("module", "housing: house {} access now {}", house.id, house.access);
        RoomTemplate const* room = Room(house);
        auto instance = s_houseInstance.find(house.id);
        if (!room || instance == s_houseInstance.end())
            return;
        if (Map* map = sMapMgr->FindMap(room->mapId, instance->second))
            map->DoForAllPlayers([&](Player* p) {
                if (!MayEnter(p, house))
                {
                    ChatHandler(p->GetSession()).SendNotification("The owner has closed their house to you.");
                    Leave(p);
                }
            });
    }

    constexpr float PlotReach = 15.0f; // how far from the cornerstone the plot window keeps working

    uint8 StatusOfPlot(uint32 account, Ties const& ties, Lot const& lot)
    {
        auto owner = s_plotHouse.find(lot);
        if (owner == s_plotHouse.end())
            return PlotForSale;
        auto house = s_houses.find(owner->second);
        return house == s_houses.end() ? PlotPrivate : house->second.account == account ? PlotYours
            : MayEnter(account, ties, house->second) ? PlotVisitable : PlotPrivate;
    }

    // A house's plot in a neighborhood, 1-based; 0 when it stands on none there.
    uint16 PlotNumber(uint32 houseId, uint32 hoodId)
    {
        for (Lot const& l : s_houseLots[houseId])
            if (l.first == hoodId)
                return uint16(l.second + 1);
        return 0;
    }

    bool IsFavorite(uint32 account, uint32 houseId, uint32 hoodId)
    {
        for (auto const& f : s_favorites[account])
            if (f.first == houseId && f.second == hoodId)
                return true;
        return false;
    }

    void SendPlot(Player* player, Lot const& lot, Plot const& plot, std::string const& message = "")
    {
        uint32 const account = player->GetSession()->GetAccountId();
        Hood const* hood = FindHood(lot.first);
        if (!hood)
            return;
        Ties const ties = TiesOf(player);
        uint8 const status = StatusOfPlot(account, ties, lot);
        auto const claim = s_plotHouse.find(lot);
        uint32 const houseId = claim != s_plotHouse.end() ? claim->second : 0;
        std::string const owner = houseId && s_houses.count(houseId) ? s_houses[houseId].owner : "";
        WorldPacket data(SMSG_ESTERIA_HOUSING_PLOT, 128);
        data << uint16(plot.index + 1) << status << s_config.plotPrice << uint8(0) << HoodName(*hood) << owner << message;
        PlotLook const l = LookOf(lot);
        data << l.style << l.dx << l.dy << l.dz << l.turn << l.scale << PlotReachYd;
        uint8 const styles = status == PlotYours ? uint8(std::min<size_t>(s_exteriorStyles.size(), 255)) : 0;
        data << styles;
        size_t n = 0;
        for (auto const& [id, name] : s_exteriorStyles)
            if (n++ < styles)
                data << id << name;
        ByteBuffer parts;
        uint8 types = 0;
        if (status == PlotYours)
            for (uint8 type : FixtureTypes)
            {
                Fixture const* now = PartOf(lot, l.style, type);
                std::vector<Fixture const*> options;
                for (auto const& [id, x] : s_fixtures)
                    if (Fits(x, l.style, type))
                        options.push_back(&x);
                if (!now || options.size() < 2)
                    continue; // nothing to choose
                parts << type << now->id << uint16(options.size());
                for (Fixture const* x : options)
                    parts << x->id << x->parent << x->name;
                ++types;
            }
        data << types;
        data.append(parts);
        // the wall and roof spots, where they are in the world, so the window can point at them
        Fixture const* base = status == PlotYours ? PartOf(lot, l.style, FixtureBase) : nullptr;
        Fixture const* roof = status == PlotYours ? PartOf(lot, l.style, FixtureRoof) : nullptr;
        std::vector<Spot> const spots = base && roof ? HouseSpots(*base, *roof) : std::vector<Spot>{};
        uint32 const roofShape = roof ? (s_fixtureHooks.count(roof->id) ? roof->id : roof->parent) : 0;
        float const s = l.scale, yaw = plot.house[3] + l.turn * float(M_PI) / 180;
        uint8 const spotCount = uint8(std::min<size_t>(spots.size(), 255));
        data << spotCount;
        for (size_t i = 0; i < spotCount; ++i)
        {
            Rooms::Hook const& h = spots[i].hooks.begin()->second;
            Rooms::Pose const p = Rooms::OnPlot(plot.house[0] + l.dx, plot.house[1] + l.dy, plot.house[2] + l.dz, yaw,
                { h.x * s, h.y * s, h.z * s, h.rotDeg });
            data << p.x << p.y << p.z << spots[i].accepts << SpotType(lot, spots, i, roofShape);
        }
        // proto 15: the neighborhood, whether this house is a favorite, and what a buyer may put here: a new house, or
        // one of theirs that does not stand in this neighborhood yet (mirrored)
        data << hood->id << uint8(houseId && IsFavorite(account, houseId, hood->id)) << houseId
             << uint8(status == PlotForSale && (RightsIn(player, *hood) & RightBuy));
        ByteBuffer choices;
        uint8 count = 0;
        if (status == PlotForSale)
            for (uint32 id : s_accountHouses[account])
            {
                if (PlotNumber(id, hood->id) || count == 255)
                    continue;
                House const& h = s_houses[id];
                std::string label;
                if (!s_houseLots[id].empty())
                {
                    Lot const& at = *s_houseLots[id].begin();
                    Hood const* there = FindHood(at.first);
                    label = "Mirror your house on plot " + std::to_string(at.second + 1) + ", " + (there ? HoodName(*there) : "");
                }
                else
                    label = "Your saved house (" + std::to_string(h.rooms.size()) + " rooms)";
                choices << id << label;
                ++count;
            }
        data << count;
        data.append(choices);
        player->SendDirectMessage(&data);
    }

    // A favorite or recent visit: the house, where it stands (in that neighborhood, else wherever else it does), and
    // whether this player may go in.
    void WriteVisit(ByteBuffer& b, uint32 account, Ties const& ties, uint32 houseId, uint32 hoodId)
    {
        auto house = s_houses.find(houseId);
        uint16 plot = house != s_houses.end() ? PlotNumber(houseId, hoodId) : 0;
        if (!plot && house != s_houses.end() && !s_houseLots[houseId].empty())
        {
            hoodId = s_houseLots[houseId].begin()->first;
            plot = PlotNumber(houseId, hoodId);
        }
        Hood const* hood = FindHood(hoodId);
        bool const ok = house != s_houses.end() && plot && hood && MayEnter(account, ties, house->second);
        b << houseId << uint32(hood ? hood->id : 0) << plot << (house != s_houses.end() ? house->second.owner : std::string())
          << (hood ? HoodName(*hood) : std::string()) << uint8(ok);
    }

    // The neighborhoods a player can go to, with how they belong there: 0 their own, 1 invited, 2 their guild's,
    // 3 visiting (a house there lets them in).
    std::vector<std::pair<Hood const*, uint8>> HoodsOf(Player* player, Ties const& ties)
    {
        uint32 const account = player->GetSession()->GetAccountId();
        std::vector<std::pair<Hood const*, uint8>> out;
        out.push_back({ &AccountHood(account), 0 });
        for (auto const& [id, h] : s_hoods)
        {
            if (h.kind == HoodAccount && h.owner == account)
                continue;
            uint8 const role = h.members.count(account) ? 1 : h.kind == HoodGuild && h.owner == player->GetGuildId() ? 2 : 3;
            if (role < 3 || MayEnterHood(player, h, ties))
                out.push_back({ &h, role });
        }
        std::stable_sort(out.begin(), out.end(), [](auto const& a, auto const& b) { return a.second < b.second; });
        return out;
    }

    uint8 WhereOf(Player* player)
    {
        return IsHousingMap(player->GetMapId()) ? WhereHouse : HoodOfMap(player->GetMap()) ? WhereNeighborhood : WhereAway;
    }

    uint8 GuildRankCount(uint32 guildId)
    {
        if (QueryResult r = CharacterDatabase.Query("SELECT COUNT(*) FROM guild_rank WHERE guildid = {}", guildId))
            return uint8(std::min<uint64>(r->Fetch()[0].Get<uint64>(), 10));
        return 0;
    }

    // The Neighborhood window: the neighborhood being looked at (browse; 0 the one the player is in, else their own),
    // their homes, the neighborhoods they can go to, favorites, recent visits, invitees and guild neighborhoods.
    void SendNeighborhood(Player* player, uint32 browse = 0, std::string const& message = "")
    {
        uint32 const account = player->GetSession()->GetAccountId();
        Ties const ties = TiesOf(player);
        Hood const* here = HoodOfMap(player->GetMap());
        Hood const* hood = FindHood(browse);
        if (!hood || !MayEnterHood(player, *hood, ties))
            hood = here ? here : &AccountHood(account);
        uint8 const rights = RightsIn(player, *hood);
        WorldPacket data(SMSG_ESTERIA_HOUSING_NEIGHBORHOOD, 512);
        data << hood->id << hood->kind << hood->mapIndex << HoodName(*hood) << HoodMaps[hood->mapIndex].name << s_config.plotPrice
             << WhereOf(player) << message << rights << uint8(here == hood) << uint8(!AccountHood(account).chosen);
        ByteBuffer plots;
        uint16 plotCount = 0;
        for (Plot const& plot : s_plots)
        {
            if (plot.map != hood->Map())
                continue;
            Lot const lot{ hood->id, plot.index };
            uint8 const status = StatusOfPlot(account, ties, lot);
            std::string const name = status == PlotVisitable || status == PlotYours ? s_houses[s_plotHouse[lot]].owner : "";
            plots << uint16(plot.index + 1) << status << name;
            ++plotCount;
        }
        data << plotCount;
        data.append(plots);

        ByteBuffer homes;
        uint8 homeCount = 0;
        for (uint32 id : s_accountHouses[account])
        {
            House const& h = s_houses[id];
            std::vector<Lot> lots(s_houseLots[id].begin(), s_houseLots[id].end());
            if (lots.empty())
                lots.push_back({ 0, 0 }); // saved: on no plot
            for (Lot const& lot : lots)
                if (homeCount < 255)
                {
                    Hood const* at = FindHood(lot.first);
                    homes << id << lot.first << uint16(at ? lot.second + 1 : 0) << (at ? HoodName(*at) : std::string())
                          << uint8(h.rooms.size()) << uint16(h.placed.size()) << h.maxDecor << h.access;
                    ++homeCount;
                }
        }
        data << homeCount;
        data.append(homes);

        auto const hoods = HoodsOf(player, ties);
        data << uint8(std::min<size_t>(hoods.size(), 255));
        for (size_t i = 0; i < hoods.size() && i < 255; ++i)
            data << hoods[i].first->id << hoods[i].first->kind << hoods[i].second << hoods[i].first->mapIndex
                 << FreePlots(*hoods[i].first) << HoodName(*hoods[i].first);

        auto const& favorites = s_favorites[account];
        data << uint8(std::min<size_t>(favorites.size(), 255));
        for (size_t i = 0; i < favorites.size() && i < 255; ++i)
            WriteVisit(data, account, ties, favorites[i].first, favorites[i].second);
        auto const& recent = s_recent[player->GetGUID().GetCounter()];
        data << uint8(recent.size());
        for (auto const& [houseId, hoodId] : recent)
            WriteVisit(data, account, ties, houseId, hoodId);

        uint8 const members = rights & RightInvite ? uint8(std::min<size_t>(hood->members.size(), 255)) : 0;
        data << members;
        size_t written = 0;
        for (uint32 member : hood->members)
            if (written++ < members)
                data << member << AccountName(member);

        // the player's guild: whether they lead it, what a neighborhood costs, the bank, and each rank's rights
        Guild* guild = sGuildMgr->GetGuildById(player->GetGuildId());
        bool const leader = guild && guild->GetLeaderGUID() == player->GetGUID();
        bool full = true; // a guild buys another neighborhood only when every one it has is full
        for (auto const& [id, h] : s_hoods)
            if (guild && h.kind == HoodGuild && h.owner == guild->GetId() && FreePlots(h))
                full = false;
        data << uint32(guild ? guild->GetId() : 0) << uint8(leader) << s_config.guildHoodPrice
             << uint32(guild ? std::min<uint64>(guild->GetTotalBankMoney(), 0xFFFFFFFFu) : 0) << uint8(leader && full);
        uint8 const ranks = leader ? GuildRankCount(guild->GetId()) : 0;
        data << uint8(ranks > 1 ? ranks - 1 : 0);
        for (uint8 rank = 1; rank < ranks; ++rank)
        {
            auto it = s_guildRights.find({ guild->GetId(), rank });
            data << uint8(it == s_guildRights.end() ? DefaultRankRights : it->second);
        }
        player->SendDirectMessage(&data);
    }

    // Why this character can't travel by the Neighborhood window right now; empty when it can. The window greys its
    // buttons by the same rules, but only this check counts.
    std::string TravelBlock(Player* player)
    {
        if (player->IsBeingTeleported())
            return "You are already traveling.";
        if (player->IsInCombat())
            return "You cannot travel while in combat.";
        if (!player->IsAlive())
            return "You cannot travel while dead.";
        if (player->IsInFlight())
            return "You cannot travel while on a flight path.";
        Map const* map = player->GetMap();
        if (map->IsBattlegroundOrArena())
            return "You cannot travel from a battleground or arena.";
        if (map->Instanceable() && !IsHousingMap(map->GetId()) && !IsNeighborhoodMap(map->GetId()))
            return "You cannot travel from inside a dungeon or raid.";
        return "";
    }

    // Keeps where "leave the neighborhood" goes back to: this spot, or from a house, wherever its door leads outside
    // the neighborhoods.
    void RememberNeighborhoodReturn(Player* player)
    {
        if (IsHousingMap(player->GetMapId()))
        {
            auto it = s_returnTo.find(player->GetGUID());
            if (it != s_returnTo.end() && !IsNeighborhoodMap(it->second.GetMapId()))
                s_neighborhoodReturn[player->GetGUID()] = it->second;
        }
        else if (!IsNeighborhoodMap(player->GetMapId()))
            s_neighborhoodReturn[player->GetGUID()] = WorldLocation(player->GetMapId(), player->GetPositionX(),
                player->GetPositionY(), player->GetPositionZ(), player->GetOrientation());
    }

    // Into a neighborhood's instance: a new instance when the player stands in another neighborhood on the same map.
    void TravelInto(Player* player, Hood const& hood, float x, float y, float z, float o)
    {
        RememberNeighborhoodReturn(player);
        Hood const* here = HoodOfMap(player->GetMap());
        s_pendingHood[player->GetGUID()] = hood.id;
        player->TeleportTo(hood.Map(), x, y, z, o, 0, nullptr, player->GetMapId() == hood.Map() && here != &hood);
    }

    void VisitNeighborhood(Player* player, Hood const& hood)
    {
        float const* e = HoodMaps[hood.mapIndex].entry;
        TravelInto(player, hood, e[0], e[1], e[2], e[3]);
    }

    void LeaveNeighborhood(Player* player)
    {
        auto it = s_neighborhoodReturn.find(player->GetGUID());
        if (it != s_neighborhoodReturn.end())
        {
            WorldLocation const to = it->second;
            s_neighborhoodReturn.erase(it);
            player->TeleportTo(to.GetMapId(), to.GetPositionX(), to.GetPositionY(), to.GetPositionZ(), to.GetOrientation());
        }
        else
            player->TeleportTo(player->m_homebindMapId, player->m_homebindX, player->m_homebindY, player->m_homebindZ,
                player->GetOrientation());
    }

    // A visit to someone else's house goes on this character's recent list.
    void RecordVisit(Player* player, House const& house, uint32 hoodId)
    {
        if (house.account == player->GetSession()->GetAccountId())
            return;
        uint32 const guid = player->GetGUID().GetCounter();
        auto& list = s_recent[guid];
        std::pair<uint32, uint32> const visit{ house.id, hoodId };
        list.erase(std::remove(list.begin(), list.end(), visit), list.end());
        list.push_front(visit);
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        trans->Append("REPLACE INTO housing_recent_visit (guid, house_id, neighborhood_id, visited_at) VALUES ({}, {}, {}, {})",
            guid, house.id, hoodId, uint32(GameTime::GetGameTime().count()));
        while (list.size() > RecentVisits)
        {
            trans->Append("DELETE FROM housing_recent_visit WHERE guid = {} AND house_id = {} AND neighborhood_id = {}", guid,
                list.back().first, list.back().second);
            list.pop_back();
        }
        CharacterDatabase.CommitTransaction(trans);
    }

    // Entering from a plot: leaving the house puts you at the plot's arrival point, not back on the door.
    void EnterFromPlot(Player* player, House const& house, Lot const& lot, Plot const& plot)
    {
        EnterHouse(player, house);
        s_returnTo[player->GetGUID()] = WorldLocation(plot.map, plot.exit[0], plot.exit[1], plot.exit[2], plot.corner[3]);
        s_returnHood[player->GetGUID()] = lot.first;
        RecordVisit(player, house, lot.first);
    }

    // The plot the player's open window is about, while they are still beside its cornerstone in that neighborhood.
    Plot const* ViewedPlot(Player* player, Lot* lot = nullptr)
    {
        auto it = s_plotView.find(player->GetGUID());
        Hood const* here = HoodOfMap(player->GetMap());
        if (it == s_plotView.end() || !here || here->id != it->second.first)
            return nullptr;
        Plot const* p = FindPlot(here->Map(), it->second.second);
        if (!p || player->GetExactDist2d(p->corner[0], p->corner[1]) > PlotReach)
            return nullptr;
        if (lot)
            *lot = it->second;
        return p;
    }

    std::string BuyPlot(Player* player, Lot const& lot, Plot const& plot, uint32 houseId)
    {
        Hood const* hood = FindHood(lot.first);
        if (!hood)
            return "This neighborhood is gone.";
        if (s_plotHouse.count(lot))
            return "Someone has already bought this plot.";
        if (!(RightsIn(player, *hood) & RightBuy))
            return hood->kind == HoodGuild ? "Your guild rank may not buy plots here."
                : "Only the owner and those they invite may buy plots here.";
        if (!player->HasEnoughMoney(s_config.plotPrice))
            return "You cannot afford this plot.";
        std::string const error = ClaimPlot(player, *hood, plot, houseId);
        if (error.empty())
            player->ModifyMoney(-int32(s_config.plotPrice));
        return error;
    }

    // Moves a neighborhood to the other map: each house keeps its plot number (both maps have 55), its outdoor decor goes
    // back to storage and it stands on the new plot's spot. Everyone inside is sent back where they came from.
    void MoveHood(Hood& hood, uint8 mapIndex)
    {
        if (Map* map = LiveMap(hood))
            map->DoForAllPlayers([&](Player* p) {
                ChatHandler(p->GetSession()).SendNotification("This neighborhood is moving to {}.", HoodMaps[mapIndex].name);
                LeaveNeighborhood(p);
            });
        if (auto it = s_hoodInstance.find(hood.id); it != s_hoodInstance.end())
        {
            s_instanceHood.erase(it->second);
            s_hoodInstance.erase(it);
        }
        std::vector<Lot> lots;
        for (auto const& [lot, houseId] : s_plotHouse)
            if (lot.first == hood.id)
                lots.push_back(lot);
        uint16 const to = HoodMaps[mapIndex].map;
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        for (Lot const& lot : lots)
        {
            if (!FindPlot(to, lot.second))
                continue;
            ReturnOutdoor(s_houses[s_plotHouse[lot]], hood.id, trans);
            PlotLook& look = s_plotLook[lot];
            look.dx = look.dy = look.dz = look.turn = 0;
            trans->Append("UPDATE housing_plot_style SET offset_x = 0, offset_y = 0, offset_z = 0, turn = 0 WHERE neighborhood_id = {} "
                "AND plot = {}", hood.id, lot.second);
        }
        hood.mapIndex = mapIndex;
        trans->Append("UPDATE housing_neighborhood SET map_id = {} WHERE neighborhood_id = {}", to, hood.id);
        CharacterDatabase.CommitTransaction(trans);
        for (Lot const& lot : lots)
            if (!FindPlot(to, lot.second))
                ReleaseLot(lot);
        LOG_INFO("module", "housing: neighborhood {} moved to map {}", hood.id, to);
    }

    std::string BuyGuildHood(Player* player, uint8 mapIndex)
    {
        Guild* guild = sGuildMgr->GetGuildById(player->GetGuildId());
        if (!guild)
            return "You are not in a guild.";
        if (guild->GetLeaderGUID() != player->GetGUID())
            return "Only the Guild Master can buy a guild neighborhood.";
        if (mapIndex >= HoodMapCount)
            return "That neighborhood is not available.";
        for (auto const& [id, h] : s_hoods)
            if (h.kind == HoodGuild && h.owner == guild->GetId() && FreePlots(h))
                return "Your guild's neighborhood still has free plots.";
        if (guild->GetTotalBankMoney() < s_config.guildHoodPrice)
            return "The guild bank cannot afford a neighborhood.";
        Hood h;
        h.id = s_nextHoodId++;
        h.kind = HoodGuild;
        h.owner = guild->GetId();
        h.mapIndex = mapIndex;
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        if (!guild->ModifyBankMoney(trans, s_config.guildHoodPrice, false))
            return "The guild bank cannot afford a neighborhood.";
        trans->Append("INSERT INTO housing_neighborhood (neighborhood_id, kind, owner, map_id, created_at) VALUES ({}, 1, {}, {}, {})",
            h.id, h.owner, h.Map(), uint32(GameTime::GetGameTime().count()));
        CharacterDatabase.CommitTransaction(trans);
        s_hoods[h.id] = h;
        LOG_INFO("module", "housing: guild {} bought neighborhood {} on map {} for {} copper", h.owner, h.id, h.Map(),
            s_config.guildHoodPrice);
        return "";
    }

    // A house in a guild's neighborhood whose account has no character left in the guild is taken off its plot (saved,
    // to move into its next guild's neighborhood).
    void CheckGuildPlots(uint32 guildId)
    {
        std::unordered_set<uint32> accounts;
        if (QueryResult r = CharacterDatabase.Query("SELECT DISTINCT c.account FROM guild_member m JOIN characters c "
            "ON c.guid = m.guid WHERE m.guildid = {}", guildId))
            do accounts.insert(r->Fetch()[0].Get<uint32>()); while (r->NextRow());
        std::vector<Lot> gone;
        for (auto const& [lot, houseId] : s_plotHouse)
            if (Hood const* h = FindHood(lot.first); h && h->kind == HoodGuild && h->owner == guildId
                && !accounts.count(s_houses[houseId].account))
                gone.push_back(lot);
        for (Lot const& lot : gone)
            ReleaseLot(lot);
    }

    // A disbanded guild's neighborhoods close; every house in them is saved.
    void CloseGuildHoods(uint32 guildId)
    {
        std::vector<uint32> hoods;
        for (auto const& [id, h] : s_hoods)
            if (h.kind == HoodGuild && h.owner == guildId)
                hoods.push_back(id);
        for (uint32 id : hoods)
        {
            Hood& hood = s_hoods[id];
            if (Map* map = LiveMap(hood))
                map->DoForAllPlayers([](Player* p) { LeaveNeighborhood(p); });
            std::vector<Lot> lots;
            for (auto const& [lot, houseId] : s_plotHouse)
                if (lot.first == id)
                    lots.push_back(lot);
            for (Lot const& lot : lots)
                ReleaseLot(lot);
            CharacterDatabase.Execute("DELETE FROM housing_neighborhood WHERE neighborhood_id = {}", id);
            CharacterDatabase.Execute("DELETE FROM housing_neighborhood_member WHERE neighborhood_id = {}", id);
            if (auto it = s_hoodInstance.find(id); it != s_hoodInstance.end())
            {
                s_instanceHood.erase(it->second);
                s_hoodInstance.erase(it);
            }
            s_hoods.erase(id);
            LOG_INFO("module", "housing: guild {} disbanded; its neighborhood {} closed", guildId, id);
        }
        CharacterDatabase.Execute("DELETE FROM housing_guild_right WHERE guild_id = {}", guildId);
        for (auto it = s_guildRights.begin(); it != s_guildRights.end();)
            it = it->first.first == guildId ? s_guildRights.erase(it) : std::next(it);
    }

#include "HousingCommerce.inc"
#include "HousingAdventure.inc"
#include "HousingCollections.inc"
#include "HousingHousehold.inc"

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
        uint32 const account = session->GetAccountId();
        if (action == ActionCommerce)
        {
            std::string text;
            packet >> text;
            if (text.rfind("adv\t", 0) == 0) // section 3 shares the commerce channel
                HandleAdventure(player, Split(text));
            else if (text.rfind("col\t", 0) == 0) // and section 4
                HandleCollection(player, Split(text));
            else
                HandleCommerce(player, text);
            return;
        }
        if (action == ActionNeighborhood)
        {
            uint32 browse;
            packet >> browse;
            SendNeighborhood(player, browse);
            return;
        }
        if (action == ActionHouseAccess)
        {
            uint32 houseId;
            uint8 access;
            packet >> houseId >> access;
            if (auto house = s_houses.find(houseId); house != s_houses.end() && house->second.account == account)
                SetAccess(house->second, access);
            SendNeighborhood(player);
            return;
        }
        if (action == ActionFavorite)
        {
            uint32 houseId, hoodId;
            uint8 on;
            packet >> houseId >> hoodId >> on;
            auto& list = s_favorites[account];
            std::pair<uint32, uint32> const fav{ houseId, hoodId };
            list.erase(std::remove(list.begin(), list.end(), fav), list.end());
            CharacterDatabase.Execute("DELETE FROM housing_favorite WHERE account_id = {} AND house_id = {} AND neighborhood_id = {}",
                account, houseId, hoodId);
            if (on && s_houses.count(houseId) && list.size() < 50)
            {
                list.push_back(fav);
                CharacterDatabase.Execute("INSERT INTO housing_favorite (account_id, house_id, neighborhood_id, added_at) VALUES "
                    "({}, {}, {}, {})", account, houseId, hoodId, uint32(GameTime::GetGameTime().count()));
            }
            Lot lot;
            if (Plot const* plot = ViewedPlot(player, &lot))
                SendPlot(player, lot, *plot);
            SendNeighborhood(player);
            return;
        }
        if (action == ActionInvite || action == ActionUninvite || action == ActionHoodMap)
        {
            uint32 hoodId;
            packet >> hoodId;
            Hood* hood = FindHood(hoodId);
            std::string message;
            uint8 const rights = hood ? RightsIn(player, *hood) : 0;
            if (action == ActionInvite)
            {
                std::string name;
                packet >> name;
                ObjectGuid const guid = sCharacterCache->GetCharacterGuidByName(name);
                uint32 const invitee = guid ? sCharacterCache->GetCharacterAccountIdByGuid(guid) : 0;
                if (!hood || !(rights & RightInvite))
                    message = "You may not invite anyone here.";
                else if (!invitee)
                    message = "There is no character named " + name + ".";
                else if (invitee == account)
                    message = "You live here already.";
                else if (hood->members.insert(invitee).second)
                {
                    CharacterDatabase.Execute("REPLACE INTO housing_neighborhood_member (neighborhood_id, account_id) VALUES ({}, {})",
                        hood->id, invitee);
                    message = name + " is invited.";
                    if (Player* p = ObjectAccessor::FindPlayerByName(name, false))
                        ChatHandler(p->GetSession()).PSendSysMessage("{} invited you to {}. Open the Neighborhood window to go "
                            "there.", player->GetName(), HoodName(*hood));
                }
                else
                    message = name + " is already invited.";
            }
            else if (action == ActionUninvite)
            {
                uint32 member;
                packet >> member;
                if (hood && (rights & RightInvite) && hood->members.erase(member))
                {
                    CharacterDatabase.Execute("DELETE FROM housing_neighborhood_member WHERE neighborhood_id = {} AND account_id = {}",
                        hood->id, member);
                    if (Map* map = LiveMap(*hood))
                        map->DoForAllPlayers([&](Player* p) {
                            if (p->GetSession()->GetAccountId() == member && !MayEnterHood(p, *hood))
                            {
                                ChatHandler(p->GetSession()).SendNotification("You are no longer invited here.");
                                LeaveNeighborhood(p);
                            }
                        });
                }
            }
            else
            {
                uint8 mapIndex;
                packet >> mapIndex;
                if (!hood || !(rights & RightManage))
                    message = "You may not move this neighborhood.";
                else if (mapIndex < HoodMapCount)
                {
                    if (mapIndex != hood->mapIndex)
                        MoveHood(*hood, mapIndex);
                    if (!hood->chosen) // the first pick, the map it already had included
                    {
                        hood->chosen = true;
                        CharacterDatabase.Execute("UPDATE housing_neighborhood SET chosen = 1 WHERE neighborhood_id = {}", hood->id);
                    }
                    message = "Your neighborhood is at " + std::string(HoodMaps[mapIndex].name) + ".";
                }
            }
            SendNeighborhood(player, hoodId, message);
            return;
        }
        if (action == ActionBuyGuildHood || action == ActionGuildRights)
        {
            std::string message;
            if (action == ActionBuyGuildHood)
            {
                uint8 mapIndex;
                packet >> mapIndex;
                message = BuyGuildHood(player, mapIndex);
                if (message.empty())
                    message = "Your guild has a new neighborhood.";
            }
            else
            {
                uint8 rank, rights;
                packet >> rank >> rights;
                Guild const* guild = sGuildMgr->GetGuildById(player->GetGuildId());
                if (guild && guild->GetLeaderGUID() == player->GetGUID() && rank >= 1 && rank < 10)
                {
                    rights &= RightBuy | RightInvite | RightManage;
                    s_guildRights[{ guild->GetId(), rank }] = rights;
                    CharacterDatabase.Execute("REPLACE INTO housing_guild_right (guild_id, rank_id, rights) VALUES ({}, {}, {})",
                        guild->GetId(), rank, rights);
                }
            }
            SendNeighborhood(player, 0, message);
            return;
        }
        if (action == ActionTravelNeighborhood || action == ActionTravelBack || action == ActionTravelPlot
            || action == ActionEnterHouse)
        {
            uint32 hoodId = 0, houseId = 0;
            uint16 number = 0;
            if (action == ActionTravelNeighborhood)
                packet >> hoodId;
            else if (action == ActionTravelPlot)
                packet >> hoodId >> number;
            else if (action == ActionEnterHouse)
                packet >> houseId;
            std::string refused = TravelBlock(player);
            Hood const* hood = hoodId ? FindHood(hoodId) : &AccountHood(account);
            if (refused.empty() && action != ActionTravelBack && action != ActionEnterHouse && (!hood || !MayEnterHood(player, *hood)))
                refused = "You may not go there.";
            if (refused.empty())
            {
                if (action == ActionTravelNeighborhood)
                    VisitNeighborhood(player, *hood);
                else if (action == ActionTravelBack)
                {
                    if (HoodOfMap(player->GetMap()))
                        LeaveNeighborhood(player);
                }
                else if (action == ActionEnterHouse)
                {
                    if (auto house = s_houses.find(houseId); house != s_houses.end() && house->second.account == account)
                        EnterHouse(player, house->second);
                }
                else if (Plot const* plot = FindPlot(hood->Map(), uint8(number - 1)); plot && number)
                    // the spot leaving its house puts you: in front of the door, by the cornerstone
                    TravelInto(player, *hood, plot->exit[0], plot->exit[1], plot->exit[2], plot->corner[3]);
            }
            SendNeighborhood(player, hood ? hood->id : 0, refused);
            return;
        }
        if (action == ActionPlotStyle || action == ActionPlotPlace || action == ActionPlotFixture || action == ActionPlotSpot
            || action == ActionMoveOut)
        {
            Lot lot;
            Plot const* plot = ViewedPlot(player, &lot);
            bool const fromEditor = !plot && action == ActionPlotPlace; // the outdoor editor's house handles
            if (fromEditor)
            {
                OwnPlot const own = OnOwnPlot(player);
                plot = own.plot;
                lot = { own.hood, plot ? plot->index : uint8(0) };
            }
            auto owner = plot ? s_plotHouse.find(lot) : s_plotHouse.end();
            if (owner == s_plotHouse.end() || !s_houses.count(owner->second) || s_houses[owner->second].account != account)
            {
                packet.rfinish();
                return;
            }
            if (action == ActionMoveOut)
            {
                ReleaseLot(lot);
                SendPlot(player, lot, *plot, "Your house is saved. Buy a plot anywhere to move it there.");
                return;
            }
            PlotLook look = LookOf(lot);
            std::string message;
            if (action == ActionPlotSpot)
            {
                uint8 index, type;
                packet >> index >> type;
                Fixture const* base = PartOf(lot, look.style, FixtureBase);
                Fixture const* roof = PartOf(lot, look.style, FixtureRoof);
                std::vector<Spot> const spots = base && roof ? HouseSpots(*base, *roof) : std::vector<Spot>{};
                if (index >= spots.size() || (type && !(spots[index].accepts & SpotBit(type))))
                    message = "That does not fit there.";
                else
                {
                    Spot const& spot = spots[index];
                    s_plotSpot[{ lot.first, lot.second, spot.shape, spot.local }] = type;
                    CharacterDatabase.Execute("REPLACE INTO housing_plot_spot (neighborhood_id, plot, shape, spot, type) VALUES "
                        "({}, {}, {}, {}, {})", lot.first, lot.second, spot.shape, spot.local, type);
                    RefreshExterior(lot);
                }
                SendPlot(player, lot, *plot, message);
                return;
            }
            if (action == ActionPlotFixture)
            {
                uint8 type;
                uint32 component;
                packet >> type >> component;
                auto x = s_fixtures.find(component);
                if (component && (x == s_fixtures.end() || !Fits(x->second, look.style, type)))
                    message = "That part does not fit this house.";
                else
                {
                    auto const key = std::make_tuple(lot.first, lot.second, look.style / 10, type);
                    if (component)
                    {
                        s_plotFixture[key] = component;
                        CharacterDatabase.Execute("REPLACE INTO housing_plot_fixture (neighborhood_id, plot, theme, type, component) "
                            "VALUES ({}, {}, {}, {}, {})", lot.first, lot.second, look.style / 10, type, component);
                    }
                    else
                    {
                        s_plotFixture.erase(key);
                        CharacterDatabase.Execute("DELETE FROM housing_plot_fixture WHERE neighborhood_id = {} AND plot = {} "
                            "AND theme = {} AND type = {}", lot.first, lot.second, look.style / 10, type);
                    }
                    RefreshExterior(lot);
                    LOG_INFO("module", "housing: neighborhood {} plot {} part {} now {}", lot.first, lot.second, type, component);
                }
                SendPlot(player, lot, *plot, message);
                return;
            }
            if (action == ActionPlotStyle)
            {
                uint32 style;
                packet >> style;
                if (s_exteriorStyles.count(style))
                    look.style = style;
                else
                    message = "That house style is not available.";
            }
            else
            {
                float dx, dy, dz, turn, scale;
                packet >> dx >> dy >> dz >> turn >> scale;
                if (!std::isfinite(dx) || !std::isfinite(dy) || !std::isfinite(dz) || !std::isfinite(turn) || !std::isfinite(scale)
                    || dx * dx + dy * dy > PlotReachYd * PlotReachYd + 0.01f || std::fabs(dz) > PlotHeightYd + 0.01f)
                    message = "The house cannot move that far from its spot.";
                else if (scale < HouseMinScale - 0.001f || scale > HouseMaxScale + 0.001f)
                    message = "The house cannot be that size.";
                else
                {
                    look.dx = dx; look.dy = dy; look.dz = dz;
                    look.turn = std::fmod(std::round(turn) + 360, 360.0f); // whole degrees
                    look.scale = std::round(scale * 100) / 100;
                }
            }
            if (message.empty())
            {
                s_plotLook[lot] = look;
                CharacterDatabase.Execute("REPLACE INTO housing_plot_style (neighborhood_id, plot, style, offset_x, offset_y, turn, "
                    "offset_z, scale) VALUES ({}, {}, {}, {}, {}, {}, {}, {})", lot.first, lot.second, look.style, look.dx, look.dy,
                    look.turn, look.dz, look.scale);
                RefreshExterior(lot);
                LOG_INFO("module", "housing: neighborhood {} plot {} now style {} at {:.2f}, {:.2f}, {:.2f} turned {} size {:.2f}",
                    lot.first, lot.second, look.style, look.dx, look.dy, look.dz, look.turn, look.scale);
            }
            if (fromEditor) // the editor reads the house from SMSG_STATE; the plot window is not open
            {
                if (!message.empty())
                    ChatHandler(session).SendNotification(message);
                SendState(player);
            }
            else
                SendPlot(player, lot, *plot, message);
            return;
        }
        if (action == ActionBuyPlot || action == ActionEnterPlot)
        {
            uint32 houseId = 0;
            if (action == ActionBuyPlot)
                packet >> houseId;
            Lot lot;
            Plot const* plot = ViewedPlot(player, &lot);
            if (!plot)
                return;
            if (action == ActionBuyPlot)
            {
                std::string const error = BuyPlot(player, lot, *plot, houseId);
                SendPlot(player, lot, *plot, error.empty() ? "Welcome home! Walk in through your front door." : error);
            }
            else if (auto owner = s_plotHouse.find(lot); owner != s_plotHouse.end() && s_houses.count(owner->second)
                && MayEnter(player, s_houses[owner->second]))
                EnterFromPlot(player, s_houses[owner->second], lot, *plot);
            return;
        }
        // Buying decor fills the account's storage: it works anywhere, not only inside a house (the yard's chest too).
        if (action == ActionBuyDecor)
        {
            std::string error;
            uint32 decorId;
            uint16 count;
            packet >> decorId >> count;
            auto entry = s_catalog.find(decorId);
            uint32 const price = entry == s_catalog.end() ? 0 : DecorPrice(entry->second) * count; // at most 100 x 5 g
            Owned& o = s_owned[account][decorId];
            if (entry == s_catalog.end() || count < 1 || count > 100 || o.owned + count > 1000)
                error = "That decor cannot be bought.";
            else if (!player->HasEnoughMoney(price))
                error = "You cannot afford that.";
            else
            {
                player->ModifyMoney(-int32(price));
                o.owned = uint16(o.owned + count);
                CharacterDatabase.Execute("INSERT INTO housing_account_decor (account_id, decor_id, quantity_owned, quantity_placed) "
                    "VALUES ({}, {}, {}, 0) ON DUPLICATE KEY UPDATE quantity_owned = {}", account, decorId, o.owned, o.owned);
                LOG_INFO("module", "housing: account {} bought {} x decor {} for {} copper", account, count, decorId, price);
                s_catalogDue[player->GetGUID()] = CatalogSettleMs;
            }
            if (!error.empty())
                ChatHandler(session).SendNotification(error);
            return;
        }
        // Room editing: the owner, inside their own house.
        House* own = HouseOfInstance(player->GetMap());
        if (!own || own->account != account)
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
        else if (action == ActionUpgrade)
        {
            uint8 what;
            packet >> what;
            uint32 const price = what == UpgradeFloors ? FloorPrice(*own) : what == UpgradeDecor ? DecorPrice(*own)
                : what == UpgradeRooms ? RoomLimitPrice(*own) : 0;
            if (!price)
                error = "That is already as large as it gets.";
            else if (!player->HasEnoughMoney(price))
                error = "You cannot afford that upgrade.";
            else
            {
                player->ModifyMoney(-int32(price));
                if (what == UpgradeFloors || what == UpgradeRooms)
                {
                    if (what == UpgradeFloors)
                        ++own->floors;
                    else
                        own->roomLimit = uint8(std::min<uint32>(RoomCap, MaxRooms(*own) + RoomStep));
                    CharacterDatabase.Execute("REPLACE INTO housing_house_limits (house_id, floors, rooms) VALUES ({}, {}, {})",
                        own->id, own->floors, own->roomLimit);
                }
                else
                {
                    own->maxDecor = uint16(std::min<int>(DecorCap, own->maxDecor + DecorStep));
                    CharacterDatabase.Execute("UPDATE housing_house SET max_decor = {} WHERE house_id = {}", own->maxDecor, own->id);
                }
                LOG_INFO("module", "housing: house {} bought upgrade {} for {} copper (floors {}, decor {})", own->id, what, price,
                    own->floors, own->maxDecor);
                BroadcastState(player->GetMap());
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

    // The steward at each neighborhood's entry: travel only. Houses are bought at plot cornerstones and edited in the
    // client UI.
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
                if (Hood const* here = HoodOfMap(player->GetMap()))
                    AddGossipItemFor(player, GOSSIP_ICON_TAXI, "Leave " + HoodName(*here) + ".", 0, ActionLeaveNeighborhood);
                else
                    AddGossipItemFor(player, GOSSIP_ICON_TAXI, "Go to my neighborhood.", 0, ActionVisitNeighborhood);
                if (HouseOfAccount(account))
                    AddGossipItemFor(player, GOSSIP_ICON_TAXI, "Take me to my house.", 0, ActionEnter);
                if (Group* group = player->GetGroup())
                    for (GroupReference* ref = group->GetFirstMember(); ref; ref = ref->next())
                        if (Player* member = ref->GetSource())
                        {
                            uint32 const owner = member->GetSession()->GetAccountId();
                            if (owner != account && HouseOfAccount(owner) && MayEnter(player, *HouseOfAccount(owner)))
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
                    if (!HoodOfMap(player->GetMap()) && !IsHousingMap(player->GetMapId()))
                        VisitNeighborhood(player, AccountHood(account));
                    break;
                case ActionLeaveNeighborhood:
                    if (HoodOfMap(player->GetMap()))
                        LeaveNeighborhood(player);
                    break;
                case ActionEnter:
                    if (House* house = HouseOfAccount(account))
                        EnterHouse(player, *house);
                    break;
                case ActionVisit:
                {
                    // Re-check: the owner must still own a house that lets this player in.
                    if (House* house = HouseOfAccount(sender); house && MayEnter(player, *house))
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

    // The plot a cornerstone stands on, in the neighborhood it stands in.
    Plot const* PlotOfCornerstone(GameObject* go, Lot& lot)
    {
        Hood const* hood = s_config.enabled && s_loaded ? HoodOfMap(go->GetMap()) : nullptr;
        Plot const* plot = hood ? PlotAt(go->GetMapId(), go->GetPositionX(), go->GetPositionY(), 3) : nullptr;
        if (plot)
            lot = { hood->id, plot->index };
        return plot;
    }

    // The sign on every plot (make_slice.py spawns one per housing_plot row). Free: claim it. Claimed: go in, if allowed.
    class go_esteria_housing_cornerstone : public GameObjectScript
    {
    public:
        go_esteria_housing_cornerstone() : GameObjectScript("go_esteria_housing_cornerstone") { }

        bool OnGossipHello(Player* player, GameObject* go) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            ClearGossipMenuFor(player);
            Lot lot;
            Plot const* plot = PlotOfCornerstone(go, lot);
            if (plot && s_hasUi.count(player->GetSession()->GetAccountId()))
            {
                s_plotView[player->GetGUID()] = lot;
                SendPlot(player, lot, *plot);
                return true; // the client opens its plot window instead of a gossip menu
            }
            if (!plot)
                AddGossipItemFor(player, GOSSIP_ICON_CHAT, "This plot is not available.", 0, 0);
            else if (auto owner = s_plotHouse.find(lot); owner == s_plotHouse.end())
                AddGossipItemFor(player, GOSSIP_ICON_CHAT, "This plot is for sale. Buying it needs the Esteria housing client.", 0, 0);
            else if (House* house = s_houses.count(owner->second) ? &s_houses[owner->second] : nullptr; house && MayEnter(player, *house))
                AddGossipItemFor(player, GOSSIP_ICON_TAXI, house->account == player->GetSession()->GetAccountId()
                    ? "Enter your house." : "Visit this house.", 0, ActionEnterPlot);
            else
                AddGossipItemFor(player, GOSSIP_ICON_CHAT, "This plot is someone's home. The owner has not opened it to you.", 0, 0);
            SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, go->GetGUID());
            return true;
        }

        bool OnGossipSelect(Player* player, GameObject* go, uint32 /*sender*/, uint32 action) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            CloseGossipMenuFor(player);
            Lot lot;
            Plot const* plot = PlotOfCornerstone(go, lot);
            if (!plot)
                return true;
            if (action == ActionEnterPlot)
                if (auto owner = s_plotHouse.find(lot); owner != s_plotHouse.end() && s_houses.count(owner->second)
                    && MayEnter(player, s_houses[owner->second]))
                    EnterFromPlot(player, s_houses[owner->second], lot, *plot);
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
            Hood const* hood = s_config.enabled && s_loaded ? HoodOfMap(go->GetMap()) : nullptr;
            if (!hood)
                return true;
            for (auto const& [lot, houseId] : s_plotHouse)
            {
                Plot const* plot = lot.first == hood->id ? PlotOfLot(lot) : nullptr;
                auto house = s_houses.find(houseId);
                if (!plot || house == s_houses.end())
                    continue;
                // this plot's house has its front door mat right where this one lies
                bool mine = false;
                for (Placement const& p : Exterior(lot, *plot))
                    mine = mine || (p.entry == go->GetEntry() && go->GetExactDist2d(p.x, p.y) < 1.0f);
                if (!mine)
                    continue;
                if (MayEnter(player, house->second))
                    EnterFromPlot(player, house->second, lot, *plot);
                else
                    ChatHandler(player->GetSession()).SendNotification("This is someone's home. The owner has not opened it to you.");
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

    // Stepping onto or off your own plot in a neighborhood switches the editor to its outdoor decor (SMSG_STATE).
    class EsteriaHousingPlotWatch : public PlayerScript
    {
    public:
        EsteriaHousingPlotWatch() : PlayerScript("EsteriaHousingPlotWatch", { PLAYERHOOK_ON_UPDATE }) { }

        void OnPlayerUpdate(Player* player, uint32 diff) override
        {
            if (!IsNeighborhoodMap(player->GetMapId()) || player->IsBeingTeleported())
                return;
            std::lock_guard<std::recursive_mutex> guard(s_lock); // map threads call this
            if (!s_config.enabled || !s_loaded || !s_hasUi.count(player->GetSession()->GetAccountId()))
                return;
            uint32& wait = s_plotWatch[player->GetGUID()];
            if (wait > diff) { wait -= diff; return; }
            wait = 1000;
            House const* house = OnOwnPlot(player).house;
            uint32& was = s_onPlot[player->GetGUID()];
            uint32 const now = house ? house->id : 0;
            if (was != now)
            {
                was = now;
                SendState(player);
            }
        }
    };

    // Members leaving a guild take their houses off its neighborhoods' plots (checked a moment later, once the core has
    // removed them); a disbanded guild's neighborhoods close.
    class EsteriaHousingGuilds : public GuildScript
    {
    public:
        EsteriaHousingGuilds() : GuildScript("EsteriaHousingGuilds", { GUILDHOOK_ON_REMOVE_MEMBER, GUILDHOOK_ON_DISBAND }) { }

        void OnRemoveMember(Guild* guild, Player* /*player*/, bool isDisbanding, bool /*isKicked*/) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            if (s_config.enabled && s_loaded && !isDisbanding)
                s_guildCheckAt[guild->GetId()] = 2000;
        }

        void OnDisband(Guild* guild) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            if (s_config.enabled && s_loaded)
                CloseGuildHoods(guild->GetId());
        }
    };

    class EsteriaHousingWorld : public WorldScript
    {
    public:
        EsteriaHousingWorld() : WorldScript("EsteriaHousingWorld", { WORLDHOOK_ON_AFTER_CONFIG_LOAD, WORLDHOOK_ON_STARTUP,
            WORLDHOOK_ON_UPDATE }) { }

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
            s_config.guildHoodPrice = sConfigMgr->GetOption<uint32>("EsteriaHousing.GuildNeighborhoodPrice", 50000000);
            s_config.maxAnimated = sConfigMgr->GetOption<uint32>("EsteriaHousing.MaxAnimatedDisplays", 12);
            s_config.repairDiscount = std::min<uint32>(25, sConfigMgr->GetOption<uint32>("EsteriaHousing.RepairDiscount", 10));
            s_config.hearthCooldown = std::clamp<uint32>(sConfigMgr->GetOption<uint32>("EsteriaHousing.HearthCooldownMinutes", 30), 1, 1440);
            if (s_config.enabled && !s_loaded && sObjectMgr->GetGameObjectTemplates()->size())
                Load(); // a .reload config that turns housing on after startup
            ApplyHooks();
        }

        void OnStartup() override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            if (s_config.enabled)
            {
                Load();
                // guilds that changed while the realm was down
                std::set<uint32> guilds;
                for (auto const& [id, h] : s_hoods)
                    if (h.kind == HoodGuild)
                        guilds.insert(h.owner);
                for (uint32 guild : guilds)
                    if (sGuildMgr->GetGuildById(guild))
                        CheckGuildPlots(guild);
                    else
                        CloseGuildHoods(guild);
            }
            ApplyHooks();
        }

        void OnUpdate(uint32 diff) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            if (s_loaded && (s_orderSweep += diff) >= 60000)
            {
                s_orderSweep = 0;
                SweepOrders();
            }
            if (s_loaded)
                TrainingTick(diff);
            for (auto it = s_catalogDue.begin(); it != s_catalogDue.end();)
            {
                if (it->second > diff)
                {
                    it->second -= diff;
                    ++it;
                    continue;
                }
                if (Player* player = ObjectAccessor::FindConnectedPlayer(it->first))
                    SendCatalog(player->GetSession(), 0);
                it = s_catalogDue.erase(it);
            }
            for (auto it = s_guildCheckAt.begin(); it != s_guildCheckAt.end();)
            {
                if (it->second > diff)
                {
                    it->second -= diff;
                    ++it;
                    continue;
                }
                CheckGuildPlots(it->first);
                it = s_guildCheckAt.erase(it);
            }
        }
    };

    class EsteriaHousingMaps : public AllMapScript
    {
    public:
        EsteriaHousingMaps() : AllMapScript("EsteriaHousingMaps", { ALLMAPHOOK_ON_PLAYER_ENTER_ALL, ALLMAPHOOK_ON_DESTROY_INSTANCE }) { }

        // Someone who may not be somewhere (a stale bind, a GM teleport, a closed neighborhood) is sent away a moment later.
        static void SendAway(Player* player, bool toReturn)
        {
            ObjectGuid const guid = player->GetGUID();
            player->m_Events.AddEventAtOffset([guid, toReturn]() {
                std::lock_guard<std::recursive_mutex> guard(s_lock);
                if (Player* p = ObjectAccessor::FindPlayer(guid); p && p->IsInWorld())
                {
                    if (toReturn)
                        Leave(p);
                    else
                        p->TeleportTo(p->m_homebindMapId, p->m_homebindX, p->m_homebindY, p->m_homebindZ, p->GetOrientation());
                }
            }, 1s);
        }

        void OnPlayerEnterAll(Map* map, Player* player) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            if (!s_config.enabled || !s_loaded)
                return;
            if (IsNeighborhoodMap(map->GetId()))
            {
                s_pendingHood.erase(player->GetGUID());
                Hood* hood = HoodOfMap(map);
                if (!hood || !MayEnterHood(player, *hood))
                    return SendAway(player, false);
                s_lastHood[player->GetGUID()] = hood->id;
                PopulateHood(map, *hood);
                PushMerchantNames(player, map);
                PushDisplayNames(player, map);
                return;
            }
            if (!IsHousingMap(map->GetId()))
                return;
            s_pending.erase(player->GetGUID());
            House* house = HouseOfInstance(map);
            if (!house) // The interior map is reserved for houses
                return SendAway(player, false);
            if (!MayEnter(player, *house)) // relogged into a house its owner has since closed to them
                return SendAway(player, true);
            s_lastHouse[player->GetGUID()] = house->id;
            if (house->account == player->GetSession()->GetAccountId())
            {
                CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
                GrantStarter(house->account, trans);
                if (trans->GetSize())
                    CharacterDatabase.CommitTransaction(trans);
            }
            Populate(map, *house);
            PushMerchantNames(player, map);
            PushDisplayNames(player, map);
            SendState(player);
        }

        void OnDestroyInstance(MapInstanced* /*mapInstanced*/, Map* map) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            uint32 const instance = map->GetInstanceId();
            s_spawned.erase(instance);
            s_roomSpawned.erase(instance);
            s_lotSpawned.erase(instance);
            s_populated.erase(instance);
            for (auto it = s_extras.begin(); it != s_extras.end();)
            {
                if (it->second.instance != instance) { ++it; continue; }
                for (ObjectGuid const& g : it->second.units)
                    s_extraPlaced.erase(g);
                it = s_extras.erase(it);
            }
            if (auto it = s_instanceHood.find(instance); it != s_instanceHood.end())
            {
                if (auto hood = s_hoodInstance.find(it->second); hood != s_hoodInstance.end() && hood->second == instance)
                    s_hoodInstance.erase(hood);
                s_instanceHood.erase(it);
            }
            auto it = s_instanceHouse.find(instance);
            if (it == s_instanceHouse.end())
                return;
            if (auto house = s_houseInstance.find(it->second); house != s_houseInstance.end() && house->second == it->first)
                s_houseInstance.erase(house);
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
    new npc_esteria_housing_merchant();
    new go_esteria_housing_service();
    new go_esteria_housing_adventure();
    new npc_esteria_housing_dummy();
    new npc_esteria_housing_display();
    new go_esteria_housing_collection();
    new EsteriaHousingBooks();
    new EsteriaHousingHousehold();
    new EsteriaHousingHouseholdSpells();
    RegisterSpellScript(spell_esteria_housing_hearth);
    new EsteriaHousingHomeSpells();
    RegisterSpellScript(spell_esteria_housing_home);
    new EsteriaHousingPlotWatch();
    new EsteriaHousingGuilds();
    new EsteriaHousingWorld();
    new EsteriaHousingMaps();
}
