/*
 * UWoW (fluxurion/UWoW_WoD) DB2Structure.h garrison entries, filled from the retail Garr* / CharShipment* /
 * GameObjects tables imported into acore_world as db2_<name>. Field names stay UWoW's so Garrison.cpp and
 * GarrisonMgr.cpp read as they did there.
 */

#ifndef GarrisonDB2_h__
#define GarrisonDB2_h__

#include "DBCEnums.h"
#include "Define.h"
#include "Errors.h"
#include <map>
#include <string>

struct DBCPosition2D { float X = 0.f, Y = 0.f; };

struct CharShipmentEntry
{
    uint32 ID;
    uint32 ShipmentConteinerID;
    uint32 Flags;
    uint32 TimeForShipment;
    uint32 SpellCreation;
    uint32 ShipmentResultItemID;
    uint32 MaxShipments;
    uint32 GarrFollowerID;
};

struct CharShipmentConteiner
{
    uint32 ID;
    std::string Description;
    std::string PendingText;
    uint32 UiTextureKitID;
    uint32 GarrTypeID;
    uint32 BuildingType;
    uint32 BaseCapacity;
    uint32 Faction;
};

struct GarrAbilityEntry
{
    uint32 ID;
    uint32 Flags;
    std::string Name;
    std::string Description;
    uint32 IconFileDataID;
    uint32 OtherFactionGarrAbilityID;
    uint32 GarrAbilityCategoryID;
    uint32 GarrFollowerTypeID;
};

struct GarrBuildingEntry
{
    uint32 ID;
    uint32 HordeGameObjectID;
    uint32 AllianceGameObjectID;
    uint32 GarrTypeID;
    uint32 Type;
    uint32 Level;
    std::string NameAlliance;
    std::string NameHorde;
    std::string Description;
    std::string Tooltip;
    uint32 BuildDuration;
    uint32 CostCurrencyID;
    int32 CostCurrencyAmount;
    uint32 HordeTexPrefixKitID;
    uint32 AllianceTexPrefixKitID;
    uint32 IconFileDataID;
    uint32 Flags;
    uint32 AllianceActivationScenePackageID;
    uint32 HordeActivationScenePackageID;
    uint32 MaxAssignments;
    uint32 MaxShipments;
    uint32 FollowerRequiredGarrAbilityID;
    uint32 FollowerGarrAbilityEffectID;
    int32 CostMoney;
};

struct GarrBuildingPlotInstEntry
{
    uint32 ID;
    uint32 GarrBuildingID;
    uint32 UiTextureAtlasMemberID;
    uint32 GarrSiteLevelPlotInstID;
    DBCPosition2D LandmarkOffset;
};

struct GarrClassSpecEntry
{
    uint32 ID;
    std::string NameMale;
    std::string NameFemale;
    std::string NameGenderless;
    uint32 ClassAtlasID;
    uint32 GarrFollItemSetID;
};

struct GarrFollowerEntry
{
    uint32 ID;
    uint32 GarrTypeID;
    uint32 GarrFollowerTypeID;
    uint32 HordeCreatureID;
    uint32 AllianceCreatureID;
    uint32 HordeUiAnimRaceInfoID;
    uint32 AllianceUiAnimRaceInfoID;
    uint32 Quality;
    uint32 HordeGarrClassSpecID;
    uint32 AllianceGarrClassSpecID;
    uint32 HordeGarrFollItemSetID;
    uint32 AllianceGarrFollItemSetID;
    uint32 Level;
    uint32 ItemLevelWeapon;
    uint32 ItemLevelArmor;
    uint32 Flags;
    std::string HordeSourceText;
    std::string AllianceSourceText;
    uint32 HordePortraitIconID;
    uint32 AlliancePortraitIconID;
};

struct GarrFollowerLevelXPEntry
{
    uint32 ID;
    uint32 Level;
    uint32 NextLevelXP;
    uint32 GarrFollowerTypeID;
};

struct GarrFollowerQualityEntry
{
    uint32 ID;
    uint32 Quality;
    uint32 NextQualityXP;
    uint32 GarrFollowerTypeID;
};

struct GarrFollowerXAbilityEntry
{
    uint32 ID;
    uint32 GarrFollowerID;
    uint32 GarrAbilityID;
    uint32 FactionIndex;
};

struct GarrMissionEntry
{
    uint32 ID;
    uint32 ReqLevel;
    uint32 ReqFollowersItemLevel;
    uint32 GarrMechanicTypeID;
    uint32 ReqFollowersCount;
    uint32 MissionDuration;
    uint32 OfferDuration;
    uint32 GarrMissionTypeID;
    uint32 GarrTypeID;
    uint32 GarrFollowerTypeID;
    std::string Name;
    std::string Description;
    std::string Location;
    uint32 ReqResourcesCount;
    uint32 ReqResourcesCurrencyID;
    uint32 BaseXP;
    uint32 BaseChance;
    uint32 TravelDuration;
    uint32 Flags;
};

struct GarrPlotEntry
{
    uint32 ID;
    uint32 PlotType;
    uint32 Flags;
    std::string Name;
    uint32 AllianceConstructionGameObjectID;
    uint32 HordeConstructionGameObjectID;
};

struct GarrPlotBuildingEntry
{
    uint32 ID;
    uint32 GarrPlotID;
    uint32 GarrBuildingID;
};

struct GarrPlotInstanceEntry
{
    uint32 ID;
    uint32 GarrPlotID;
    std::string Name;
};

struct GarrSiteLevelEntry
{
    uint32 ID;
    uint32 Level;
    uint32 MapID;
    uint32 SiteID;
    uint32 UITextureKitID;
    DBCPosition2D TownHall;
    uint32 MovieID;
    uint32 Level2;
    int32 UpgradeResourceCost;
    int32 UpgradeMoneyCost;
};

struct GarrSiteLevelPlotInstEntry
{
    uint32 ID;
    uint32 GarrSiteLevelID;
    uint32 GarrPlotInstanceID;
    DBCPosition2D Landmark;
    uint32 Unknown;
};

struct GameObjectsEntry
{
    uint32 ID;
    uint32 MapID;
    uint32 DisplayID;
    DBCPosition3D Position;
    float RotationX, RotationY, RotationZ, RotationW;
    float Size;
    uint32 Type;
    uint32 Data[8];
    std::string Name;
};

template<class T>
class GarrDB2Storage
{
public:
    using Map = std::map<uint32, T>;

    T const* LookupEntry(uint32 id) const
    {
        auto itr = _rows.find(id);
        return itr != _rows.end() ? &itr->second : nullptr;
    }

    T const* AssertEntry(uint32 id) const
    {
        T const* entry = LookupEntry(id);
        ASSERT(entry, "garrison DB2 entry %u missing", id);
        return entry;
    }

    T& Add(uint32 id) { return _rows[id]; }
    void Clear() { _rows.clear(); }
    size_t GetNumRows() const { return _rows.size(); }

    class const_iterator
    {
    public:
        explicit const_iterator(typename Map::const_iterator itr) : _itr(itr) { }
        T const* operator*() const { return &_itr->second; }
        const_iterator& operator++() { ++_itr; return *this; }
        bool operator!=(const_iterator const& other) const { return _itr != other._itr; }
    private:
        typename Map::const_iterator _itr;
    };

    const_iterator begin() const { return const_iterator(_rows.begin()); }
    const_iterator end() const { return const_iterator(_rows.end()); }

private:
    Map _rows;
};

extern GarrDB2Storage<CharShipmentEntry>          sCharShipmentStore;
extern GarrDB2Storage<CharShipmentConteiner>      sCharShipmentContainerStore;
extern GarrDB2Storage<GarrAbilityEntry>           sGarrAbilityStore;
extern GarrDB2Storage<GarrBuildingEntry>          sGarrBuildingStore;
extern GarrDB2Storage<GarrBuildingPlotInstEntry>  sGarrBuildingPlotInstStore;
extern GarrDB2Storage<GarrClassSpecEntry>         sGarrClassSpecStore;
extern GarrDB2Storage<GarrFollowerEntry>          sGarrFollowerStore;
extern GarrDB2Storage<GarrFollowerLevelXPEntry>   sGarrFollowerLevelXPStore;
extern GarrDB2Storage<GarrFollowerQualityEntry>   sGarrFollowerQualityStore;
extern GarrDB2Storage<GarrFollowerXAbilityEntry>  sGarrFollowerXAbilityStore;
extern GarrDB2Storage<GarrMissionEntry>           sGarrMissionStore;
extern GarrDB2Storage<GarrPlotEntry>              sGarrPlotStore;
extern GarrDB2Storage<GarrPlotBuildingEntry>      sGarrPlotBuildingStore;
extern GarrDB2Storage<GarrPlotInstanceEntry>      sGarrPlotInstanceStore;
extern GarrDB2Storage<GarrSiteLevelEntry>         sGarrSiteLevelStore;
extern GarrDB2Storage<GarrSiteLevelPlotInstEntry> sGarrSiteLevelPlotInstStore;
extern GarrDB2Storage<GameObjectsEntry>           sGameObjectsStore;

namespace GarrisonDB2
{
    void Load();

    // UWoW DB2Manager helpers
    uint32 GetXPForNextFollowerLevel(uint32 level);
    uint32 GetXPForNextFollowerQuality(uint32 quality);
}

#endif
