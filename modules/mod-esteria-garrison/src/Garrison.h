/*
 * UWoW Garrison (fluxurion/UWoW_WoD src/server/game/Garrison/Garrison.h) on AzerothCore. The player owns the
 * garrison through GarrisonRegistry instead of Player::_garrison, the garrison map is an InstanceMap whose id is
 * picked by EsteriaGarrisonHooks::Instance, and currency 824 lives in GarrisonCurrency.
 */

#ifndef Garrison_h__
#define Garrison_h__

#include "DatabaseEnvFwd.h"
#include "GarrisonPackets.h"
#include "ObjectGuid.h"
#include "Timer.h"
#include <functional>
#include <list>
#include <map>
#include <memory>
#include <optional>
#include <unordered_map>
#include <unordered_set>

class Creature;
class GameObject;
class Map;
class Player;
class WorldObject;

enum GarrisonSiteiD
{
    SITE_ID_GARRISON_ALLIANCE = 2,
    SITE_ID_GARRISON_HORDE = 71,
};

enum GarrisonFactionIndex
{
    GARRISON_FACTION_INDEX_HORDE    = 0,
    GARRISON_FACTION_INDEX_ALLIANCE = 1
};

enum GarrisonBuildingFlags
{
    GARRISON_BUILDING_FLAG_NEEDS_PLAN   = 0x1
};

enum GarrisonFollowerFlags
{
    GARRISON_FOLLOWER_FLAG_UNIQUE   = 0x1
};

enum GarrisonAbilityFlags
{
    GARRISON_ABILITY_FLAG_TRAIT         = 0x01,
    GARRISON_ABILITY_CANNOT_ROLL        = 0x02,
    GARRISON_ABILITY_HORDE_ONLY         = 0x04,
    GARRISON_ABILITY_ALLIANCE_ONLY      = 0x08,
    GARRISON_ABILITY_FLAG_CANNOT_REMOVE = 0x10,
    GARRISON_ABILITY_FLAG_EXCLUSIVE     = 0x20
};

enum GarrisonError
{
    GARRISON_SUCCESS                        = 0,
    GARRISON_ERROR_INVALID_PLOT             = 1,
    GARRISON_ERROR_INVALID_BUILDINGID       = 2,
    GARRISON_ERROR_INVALID_PLOT_BUILDING    = 7,
    GARRISON_ERROR_NO_BUILDING              = 8,
    GARRISON_ERROR_MAX_LEVEL                = 12,
    GARRISON_ERROR_SPECIALIZATION_KNOWN     = 19,
    GARRISON_ERROR_BLUEPRINT_KNOWN          = 21,
    GARRISON_ERROR_BLUEPRINT_NOT_KNOWN      = 22,
    GARRISON_ERROR_BUILDING_EXISTS          = 24,
    GARRISON_ERROR_NOT_ENOUGH_CURRENCY      = 46,
    GARRISON_ERROR_NOT_ENOUGH_GOLD          = 47,
    GARRISON_ERROR_NOT_ALLOW_GARRISON_UPGRADE = 68,
    GARRISON_GENERIC_UNKNOWN_ERROR          = 255   // custom value for packets whose handlers only check if error != 0
};

enum GarrisonFollowerStatus
{
    FOLLOWER_STATUS_BASE        = 0x00,
    FOLLOWER_STATUS_FAVORITE    = 0x01,
    FOLLOWER_STATUS_EXHAUSTED   = 0x02,
    FOLLOWER_STATUS_INACTIVE    = 0x04
};

enum MissionState
{
    MISSION_STATE_AVAILABLE     = 0,
    MISSION_STATE_IN_PROGRESS   = 1,
    MISSION_STATE_WAITING_BONUS = 2,
    MISSION_STATE_COMPLETED     = 5
};

enum FollowerQuality
{
    FOLLOWER_QUALITY_UNCOMMON  = 2,
    FOLLOWER_QUALITY_RARE      = 3,
    FOLLOWER_QUALITY_EPIC      = 4,
    FOLLOWER_QUALITY_LEGENDARY = 5
};

enum GarrisonCurrencies
{
    CURRENCY_TYPE_GARRISON_RESOURCES = 824,
};

typedef std::list<WorldPackets::Garrison::Shipment> ShipmentSet;
typedef std::unordered_map<uint32/*buildingType*/, ObjectGuid /*guid*/> ShipmentConteinerSpawn;

class Garrison
{
public:
    struct Building
    {
        bool CanActivate() const;

        ObjectGuid Guid;
        GuidUnorderedSet Spawns;
        std::optional<WorldPackets::Garrison::GarrisonBuildingInfo> PacketInfo;
    };

    struct Plot
    {
        GameObject* CreateGameObject(Map* map, GarrisonFactionIndex faction, Garrison* g);
        void DeleteGameObject(Map* map);
        void ClearBuildingInfo(Player* owner);
        void SetBuildingInfo(WorldPackets::Garrison::GarrisonBuildingInfo const& buildingInfo, Player* owner);

        WorldPackets::Garrison::GarrisonPlotInfo PacketInfo;
        float RotationX = 0.f;
        float RotationY = 0.f;
        float RotationZ = 0.f;
        float RotationW = 0.f;
        uint32 EmptyGameObjectId = 0;
        uint32 GarrSiteLevelPlotInstId = 0;
        Building BuildingInfo;

        bool buildingActivationWaiting = false;
        ObjectGuid FinalizerGuid;
    };

    struct Follower
    {
        WorldPackets::Garrison::GarrisonFollower PacketInfo;

        uint32 GetItemLevel() const;
        void IncreaseFollowerItemLevel(uint32 spellId, int32 basePoints, int32 miscValueB, Player* caster);
        uint8 RollQuality(uint32 baseQuality);
        void GiveLevel(uint32 level) { PacketInfo.FollowerLevel = level; }
        void GiveQuality(uint32 quality) { PacketInfo.Quality = quality; }
        void GiveXP(uint32 xp);
        uint32 GetXPForNextUpgrade();
    };

    struct Mission
    {
        WorldPackets::Garrison::GarrisonMission PacketInfo;
        std::list<uint64> CurrentFollowerDBIDs;

        void Start(Player* owner);
        bool CanStart(Player* owner);
        void BonusRoll(Player* onwer);
        bool CanBonusRoll();
        void Complete(Player* owner);
        bool HasBonusRoll();
        float ComputeSuccessChance();
        float CalcChance(float a, float b, float c);
        uint32 GetDuration(Player* owner);
    };

    explicit Garrison(Player* owner);

    bool LoadFromDB();
    void SaveToDB(CharacterDatabaseTransaction trans);
    static void DeleteFromDB(ObjectGuid::LowType ownerGuid, CharacterDatabaseTransaction trans);

    bool Create(uint32 garrSiteId, bool enter = true);
    void Delete();
    void Upgrade();
    bool Downgrade(); // GM: one tier down, false at tier 1

    void Enter();
    void Leave() const;

    void Update(uint32 diff);

    GarrisonFactionIndex GetFaction() const;
    Player* GetOwner() const { return _owner; }

    // Plots
    std::vector<Plot*> GetPlots();
    Plot* GetPlot(uint32 garrPlotInstanceId);
    Plot const* GetPlot(uint32 garrPlotInstanceId) const;
    Garrison::Plot* GetPlotWithBuildingType(uint32 BuildingTypeID);
    Plot* GetPlotByFinalizer(ObjectGuid const& guid);

    // Buildings
    bool LearnBlueprint(uint32 garrBuildingId);
    void UnlearnBlueprint(uint32 garrBuildingId);
    void PlaceBuilding(uint32 garrPlotInstanceId, uint32 garrBuildingId, bool byQuest = false);
    void CancelBuildingConstruction(uint32 garrPlotInstanceId);
    void ActivateBuilding(uint32 garrPlotInstanceId);
    // Text window the 3.3.5 addon draws. openPage: 0 leave it, 1 buildings, 2 missions.
    void SendWindow(uint32 uiResult, uint8 openPage);
    void HandleUiAction(uint8 op, uint32 a, uint32 b);
    uint32 GetCountOfBluePrints() const { return uint32(_knownBuildings.size()); }
    uint32 GetCountOFollowers() const { return uint32(_followers.size()); }

    // Followers
    void AddFollower(uint32 garrFollowerId);
    Follower const* GetFollower(uint64 dbId) const;
    Follower* GetFollower(uint64 dbId);
    Follower* GetFollowerByID(uint32 entry);
    void ReTrainFollower(int32 miscValue, uint32 followerID);

    // Missions
    void AddMission(uint32 missionRecID);
    // Fills the command table from the real random mission line, up to six open offers.
    bool OfferTableMissions();
    Mission const* GetMission(uint64 dbId) const;
    Mission* GetMission(uint64 dbId);
    Mission* GetMissionByRecID(uint32 missionRecID);
    void RewardMission(uint32 missionRecID);

    void SendInfo();
    void SendRemoteInfo() const;
    void SendBlueprintAndSpecializationData();
    void SendBuildingLandmarks(Player* receiver) const;
    void SendGarrisonUpgradebleResult(Player* receiver) const;
    void SendMissionListUpdate(bool openMissionNpc) const;

    void ResetFollowerActivationLimit() { _followerActivationsRemainingToday = 1; }
    uint32 GetPlotInstanceForBuildingType(uint32 type) const;

    // Map
    int32 GetGarrisonMapID() const { return _siteLevel ? int32(_siteLevel->MapID) : -1; }
    uint8 GetGarrisonLevel() const { return _siteLevel ? uint8(_siteLevel->Level) : 0; }
    GarrSiteLevelEntry const* GetSiteLevel() const { return _siteLevel; }
    uint32 GetInstanceId() const { return _instanceId; }
    void SetInstanceId(uint32 instanceId) { _instanceId = instanceId; }
    static uint32 GetAreaIdForTeam(uint32 team);
    void OnMapLoaded(Map* map);
    void OnMapUnloaded();

    //  Ressource
    uint32 GetResNumber() const;
    void UpdateResTakenTime();

    // Enother
    void OnQuestReward(uint32 questID);

    // Shipment
    void CreateShipment(ObjectGuid const& guid, uint32 count);
    void CreateGarrisonShipment(uint32 shipmentID);
    bool canAddShipmentOrder(Creature* source);
    void OnGossipSelect(WorldObject* source);
    void SendShipmentInfo(ObjectGuid const& guid);
    uint64 PlaceShipment(uint32 shipmentID, uint32 placeTime, uint64 dbID = 0);
    void SendGarrisonShipmentLandingPage();
    void CompleteShipments(GameObject* go);
    void FreeShipmentChest(uint32 shipment);
    uint32 GetShipmentChestBuildingType(ObjectGuid const& guid) const;

    // Spells the 3.3.5 client cannot cast: the retail SpellEffect rows UWoW's Spell::Effect* handlers read
    bool HandleSpell(uint32 spellId, uint32 followerID = 0);

protected:
    Map* FindMap() const;
    void InitializePlots();
    void EnsureFinalizer(Plot& plot, Map* map);
    void UpdatePlotPad(Plot& plot, Map* map);
    GarrisonError CheckBuildingPlacement(uint32 garrPlotInstanceId, uint32 garrBuildingId, bool byQuest = false) const;
    GarrisonError CheckBuildingRemoval(uint32 garrPlotInstanceId) const;
    Player* _owner;
    GarrSiteLevelEntry const* _siteLevel;
    uint32 _followerActivationsRemainingToday;
    uint32 _lastResTaken;
    uint32 _instanceId = 0;
    bool _plotsSpawned = false;

    std::unordered_map<uint32 /*garrPlotInstanceId*/, Plot> _plots;
    std::unordered_set<uint32 /*garrBuildingId*/> _knownBuildings;
    std::unordered_map<uint64 /*dbId*/, Follower> _followers;
    std::unordered_set<uint32> _followerIds;
    std::unordered_map<uint64 /*dbId*/, Mission> _missions;
    std::unordered_set<uint32> _missionIds;

    std::map<uint32/*shipmentID*/, ShipmentSet> _shipments;
    ShipmentConteinerSpawn ShipmentConteiners;

    IntervalTimer updateTimer;
};

// Player::GetGarrison / CreateGarrison / DeleteGarrison
namespace GarrisonRegistry
{
    Garrison* Get(Player* player);
    Garrison* Get(ObjectGuid::LowType guid);
    void Load(Player* player);
    void Unload(Player* player);
    // enter = false: the login grant, which must not move the player
    void Create(Player* player, uint32 garrSiteId, bool enter = true);
    void Delete(Player* player);
    void ForEach(std::function<void(Garrison&)> const& fn);
}

// Player::HasCurrency / ModifyCurrency for the garrison currencies a 3.3.5 character has no field for
namespace GarrisonCurrency
{
    void Load(Player* player);
    void Save(Player* player, CharacterDatabaseTransaction trans);
    void Unload(Player* player);
    uint32 Get(Player* player, uint32 currency);
    bool Has(Player* player, uint32 currency, uint32 count);
    void Modify(Player* player, uint32 currency, int32 amount, bool printLog = true);
    void Send(Player* player, uint32 currency);
}

#endif // Garrison_h__
