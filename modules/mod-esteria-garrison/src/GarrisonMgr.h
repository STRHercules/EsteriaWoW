/*
 * UWoW GarrisonMgr. AzerothCore has no npcflag2, no WoD gameobject types and no WoD spells, so the manager also
 * keeps garrison_creature_npcflag2, garrison_gameobject_wod_type and the retail SpellEffect rows (db2_spell_effect)
 * that the 6.x core read from its own templates and Spell.dbc.
 */

#ifndef GarrisonMgr_h__
#define GarrisonMgr_h__

#include "GarrisonDB2.h"
#include "Position.h"
#include <list>
#include <map>
#include <set>
#include <unordered_map>
#include <unordered_set>
#include <vector>

struct FinalizeGarrisonPlotGOInfo
{
    struct
    {
        uint32 GameObjectId;
        Position Pos;
    } FactionInfo[2];
};

struct GarrMissionLine
{
    GarrMissionEntry const* MissionID;
    GarrMissionEntry const* NextMission;
    GarrFollowerEntry const* Reqfollower;
    bool isRandom = false;
};

struct GarrAbilities
{
    std::unordered_set<GarrAbilityEntry const*> Counters;
    std::unordered_set<GarrAbilityEntry const*> Traits;
};

struct GarrShipment
{
    uint32 SiteID = 0;
    uint32 ContainerID = 0;
    uint32 NpcEntry = 0;
    uint32 ShipmentID = 0;

    CharShipmentEntry const* data = nullptr;
    CharShipmentConteiner const* cEntry = nullptr;
};

// CreatureData / GameObjectData rows of garrison_building_creature / garrison_building_gameobject
struct GarrisonBuildingSpawn
{
    uint32 id = 0;
    uint32 mapid = 0;
    float posX = 0.f, posY = 0.f, posZ = 0.f, orientation = 0.f;
    float rotation0 = 0.f, rotation1 = 0.f, rotation2 = 0.f, rotation3 = 0.f;
    bool building = false;
};

// Original 6.x gameobject type of a template that was exported to 3.3.5 as GENERIC / GOOBER
struct GarrisonWoDGameObject
{
    uint32 type = 0;
    uint32 data[4] = { };
};

struct GarrisonSpellEffect
{
    uint32 SpellID = 0;
    uint32 EffectIndex = 0;
    uint32 Effect = 0;
    int32 BasePoints = 0;
    int32 MiscValue = 0;
    int32 MiscValueB = 0;
};

enum ShipmentGetType : uint8
{
    SHIPMENT_GET_BY_NPC           = 0,
    SHIPMENT_GET_BY_CONTEINER_ID  = 1,
};

enum GarrBuildingType
{
    GARR_BTYPE_NONE         = 0,
    GARR_BTYPE_MINE         = 1,
    GARR_BTYPE_HERB_GARDEN  = 2,
    GARR_BTYPE_BARN         = 3,
    GARR_BTYPE_LUMBER_MILL  = 4,
    GARR_BTYPE_TAVERN       = 5,
    GARR_BTYPE_TRADING_POST = 6,
    GARR_BTYPE_MENAGERIE    = 7,
    GARR_BTYPE_BARRACKS     = 8,
    GARR_BTYPE_WARMILL      = 10,
    GARR_BTYPE_STABLES      = 11,
    GARR_BTYPE_MAGETOWER    = 13,
    GARR_BTYPE_SALVAGE_YARD = 14,
    GARR_BTYPE_STOREHOUSE   = 15,
    GARR_BTYPE_ALCHEMY_LAB  = 16,
    GARR_BTYPE_FORGE        = 17,
    GARR_BTYPE_ENCHANTERS   = 18,
    GARR_BTYPE_ENGINEERING  = 19,
    GARR_BTYPE_SCRIBE       = 20,
    GARR_BTYPE_GEM          = 21,
    GARR_BTYPE_TANNERY      = 22,
    GARR_BTYPE_TAILORING    = 23,
    GARR_BTYPE_FISHING      = 24,
    GARR_BTYPE_GLADIATORS   = 25,
    GARR_BTYPE_WORKSHOP     = 26,
    GARR_BTYPE_MAX
};

enum GarrisonGameObjectTypes
{
    GAMEOBJECT_TYPE_GARRISON_BUILDING = 38,
    GAMEOBJECT_TYPE_GARRISON_PLOT     = 39,
    GAMEOBJECT_TYPE_GARRISON_SHIPMENT = 45,
};

enum GarrisonNpcFlags2
{
    UNIT_NPC_FLAG2_UPGRADE_MASTER       = 0x01,
    UNIT_NPC_FLAG2_GARRISON_ARCHITECT   = 0x02,
    UNIT_NPC_FLAG2_SHIPMENT_ORDER       = 0x04,
    UNIT_NPC_FLAG2_SHIPMENT_CRAFTER     = 0x20,
    UNIT_NPC_FLAG2_GARRISON_MISSION_NPC = 0x40,
    UNIT_NPC_FLAG2_TRADESKILL_NPC       = 0x80,
};

enum GarrisonSpellEffects
{
    SPELL_EFFECT_LEARN_GARRISON_BUILDING      = 210,
    SPELL_EFFECT_CREATE_GARRISON              = 214,
    SPELL_EFFECT_CREATE_SHIPMENT              = 216,
    SPELL_EFFECT_UPGRADE_GARRISON             = 217,
    SPELL_EFFECT_ADD_GARRISON_FOLLOWER        = 220,
    SPELL_EFFECT_ADD_GARRISON_MISSION         = 221,
    SPELL_EFFECT_ACTIVATE_GARRISON_BUILDING   = 224,
    SPELL_EFFECT_INCREASE_FOLLOWER_ITEM_LEVEL = 230,
    SPELL_EFFECT_RETRAIN_FOLLOWER             = 233,
};

class GarrisonMgr
{
public:
    static GarrisonMgr& Instance()
    {
        static GarrisonMgr instance;
        return instance;
    }

    static uint32 getFirstMap(uint32 map);
    static bool IsGarrisonMap(uint32 map) { return getFirstMap(map) != 0; }

    void Initialize();

    GarrSiteLevelEntry const* GetGarrSiteLevelEntry(uint32 garrSiteId, uint32 level) const;
    std::vector<GarrSiteLevelPlotInstEntry const*> const* GetGarrPlotInstForSiteLevel(uint32 garrSiteLevelId) const;
    GameObjectsEntry const* GetPlotGameObject(uint32 mapId, uint32 garrPlotInstanceId) const;
    bool IsPlotMatchingBuilding(uint32 garrPlotId, uint32 garrBuildingId) const;
    uint32 GetGarrBuildingPlotInst(uint32 garrBuildingId, uint32 garrSiteLevelPlotInstId) const;
    GarrBuildingEntry const* GetPreviousLevelBuilding(uint32 buildingType, uint32 currentLevel) const;
    FinalizeGarrisonPlotGOInfo const* GetPlotFinalizeGOInfo(uint32 garrPlotInstanceID) const;
    uint64 GenerateFollowerDbId();
    std::list<GarrAbilityEntry const*> RollFollowerAbilities(GarrFollowerEntry const* follower, uint32 quality, uint32 faction, bool initial) const;
    std::list<GarrAbilityEntry const*> GetClassSpecAbilities(GarrFollowerEntry const* follower, uint32 faction) const;
    uint64 GenerateMissionDbId();
    uint64 GenerateShipmentDbId();
    std::list<GarrisonBuildingSpawn> const* GetGoSpawnBuilding(uint32 plotID, uint32 build) const;
    std::list<GarrisonBuildingSpawn> const* GetNpcSpawnBuilding(uint32 plotID, uint32 build) const;

    GarrMissionEntry const* GetNextMissionInQuestLine(uint32 missionID);
    GarrMissionEntry const* GetMissionAtFollowerTaking(uint32 followerID);
    // Random command-table offers from garrison_mission_line. OfferDuration 0 never survives a save.
    std::vector<uint32> GetRandomMissionIDs() const;

    GarrShipment const* GetGarrShipment(uint32 entry, ShipmentGetType type) const;

    uint32 GetNpcFlags2(uint32 creatureEntry) const;
    GarrisonWoDGameObject const* GetWoDGameObject(uint32 goEntry) const;
    uint32 GetWoDGameObjectType(uint32 goEntry) const;
    std::vector<GarrisonSpellEffect> const* GetSpellEffects(uint32 spellId) const;
    GarrisonSpellEffect const* GetSpellEffect(uint32 spellId, uint32 effect) const;
    std::vector<uint32> const* GetItemSpells(uint32 itemId) const;

private:
    void InitializeDbIdSequences();
    void LoadPlotFinalizeGOInfo();
    void LoadFollowerClassSpecAbilities();
    void LoadBuildingSpawnNPC();
    void LoadBuildingSpawnGo();
    void LoadMissionLine();
    void LoadShipment();
    void LoadNpcFlags2();
    void LoadWoDGameObjects();
    void LoadSpellEffects();

    std::unordered_map<uint32 /*garrSiteId*/, std::vector<GarrSiteLevelPlotInstEntry const*>> _garrisonPlotInstBySiteLevel;
    std::unordered_map<uint32 /*mapId*/, std::unordered_map<uint32 /*garrPlotId*/, GameObjectsEntry const*>> _garrisonPlots;
    std::unordered_map<uint32 /*garrPlotId*/, std::unordered_set<uint32/*garrBuildingId*/>> _garrisonBuildingsByPlot;
    std::unordered_map<uint64 /*garrBuildingId | garrSiteLevelPlotInstId << 32*/, uint32 /*garrBuildingPlotInstId*/> _garrisonBuildingPlotInstances;
    std::unordered_map<uint32 /*buildingType*/, std::vector<GarrBuildingEntry const*>> _garrisonBuildingsByType;
    std::unordered_map<uint32 /*garrPlotInstanceId*/, FinalizeGarrisonPlotGOInfo> _finalizePlotGOInfo;
    std::unordered_map<uint32 /*garrFollowerId*/, GarrAbilities> _garrisonFollowerAbilities[2];
    std::unordered_map<uint32 /*classSpecId*/, std::list<GarrAbilityEntry const*>> _garrisonFollowerClassSpecAbilities;

    std::unordered_map<uint32 /*BuildID*/, std::unordered_map<uint32 /*garrPlotId*/, std::list<GarrisonBuildingSpawn>>> _buildSpawnGo;
    std::unordered_map<uint32 /*BuildID*/, std::unordered_map<uint32 /*garrPlotId*/, std::list<GarrisonBuildingSpawn>>> _buildSpawnNpc;

    std::unordered_map<uint32 /*MissionID*/, GarrMissionLine /*nextMission*/> _MissionLineStore;
    std::unordered_map<uint32 /*MissionID*/, GarrMissionEntry const* /*nextMission*/> _nextMission;
    std::unordered_map<uint32 /*FollowerID*/, GarrMissionEntry const* /*nextMission*/> _nextMissionByFollower;

    typedef std::unordered_map<uint32/*entry*/, GarrShipment> shipmentStoreMap;
    std::map<uint8 /*ShipmentGetType*/, shipmentStoreMap> shipment;

    std::set<GarrAbilityEntry const*> _garrisonFollowerRandomTraits;

    std::unordered_map<uint32, uint32> _npcFlags2;
    std::unordered_map<uint32, GarrisonWoDGameObject> _wodGameObjects;
    std::unordered_map<uint32, std::vector<GarrisonSpellEffect>> _spellEffects;
    std::unordered_map<uint32, std::vector<uint32>> _itemSpells;

    uint64 _followerDbIdGenerator = UI64LIT(1);
    uint64 _missionDbIdGenerator = UI64LIT(1);
    uint64 _shipmentDbIdGenerator = UI64LIT(1);
};

#define sGarrisonMgr GarrisonMgr::Instance()

#endif // GarrisonMgr_h__
