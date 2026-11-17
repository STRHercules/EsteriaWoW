#include "Garrison.h"
#include "Creature.h"
#include "CreatureTextMgr.h"
#include "DatabaseEnv.h"
#include "Field.h"
#include "QueryResult.h"
#include "GameObject.h"
#include "GarrisonMgr.h"
#include "Item.h"
#include "Log.h"
#include "LootMgr.h"
#include "Map.h"
#include "MapMgr.h"
#include "ObjectAccessor.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "Random.h"
#include "SharedDefines.h"
#include "Opcodes.h"
#include "WorldSession.h"
#include <G3D/Quat.h>
#include <cmath>
#include <mutex>
#include <shared_mutex>
#include <cstdio>
#include <map>
#include <sstream>
#include <unordered_set>

#define RESP_GO_LOOT 12 * HOUR * MINUTE

namespace
{
    uint32 getSiteLevelIdById(uint32 team, uint8 lvl)
    {
        switch (lvl)
        {
            case 1:
                return team == ALLIANCE ? 5 : 258;
            case 2:
                return team == ALLIANCE ? 444 : 445;
            case 3:
                return team == ALLIANCE ? 6 : 259;
        }

        ASSERT(false);
        return 0;
    }

    uint32 getQuestIdReqForShipment(uint32 siteID, uint32 buildingType)
    {
        switch (buildingType)
        {
            case GARR_BTYPE_ALCHEMY_LAB:
                return siteID == SITE_ID_GARRISON_ALLIANCE ? 36641 : 37568;
            case GARR_BTYPE_TAILORING:
                return siteID == SITE_ID_GARRISON_ALLIANCE ? 36643 : 37575;
            case GARR_BTYPE_FORGE:
                return siteID == SITE_ID_GARRISON_ALLIANCE ? 35168 : 37569;
            case GARR_BTYPE_TANNERY:
                return siteID == SITE_ID_GARRISON_ALLIANCE ? 36642 : 37574;
            case GARR_BTYPE_GEM:
                return siteID == SITE_ID_GARRISON_ALLIANCE ? 36644 : 37573;
            case GARR_BTYPE_ENCHANTERS:
                return siteID == SITE_ID_GARRISON_ALLIANCE ? 36645 : 37570;
            case GARR_BTYPE_ENGINEERING:
                return siteID == SITE_ID_GARRISON_ALLIANCE ? 36646 : 37571;
            case GARR_BTYPE_SCRIBE:
                return siteID == SITE_ID_GARRISON_ALLIANCE ? 36647 : 37572;
            default:
                return 0;
        }
    }

    //! Shipment for requarement.
    uint32 getProgressShipment(uint32 questID)
    {
        switch (questID)
        {
            //GARR_BTYPE_ALCHEMY_LAB
            case 36641: return 114;
            case 37568: return 122;
            //GARR_BTYPE_TAILORING
            case 36643: return 120;
            case 37575: return 136;
            //GARR_BTYPE_FORGE
            case 35168: return 113;
            case 37569: return 123;
            //GARR_BTYPE_TANNERY
            case 36642: return 119;
            case 37574: return 134;
            //GARR_BTYPE_GEM
            case 36644: return 118;
            case 37573: return 131;
            //GARR_BTYPE_ENCHANTERS
            case 36645: return 115;
            case 37570: return 126;
            //GARR_BTYPE_ENGINEERING
            case 36646: return 116;
            case 37571: return 128;
            //GARR_BTYPE_SCRIBE
            case 36647: return 117;
            case 37572: return 130;
        }
        return 0;
    }

    // UWoW garrison_general.cpp spell_garrison_hearthstone (171253) landing spots, by garrison level
    Position const hearhstoneHorde[3] =
    {
        {5560.4f, 4507.7f, 132.67f, 206.1f},         // Horde lvl1 map 1152
        {5565.86f, 4593.5f, 140.893f, 2.332632f},    // Horde lvl2 spell 171325 map 1330
        {5563.7f, 4599.9f, 141.71f, 131.75f},        // Horde lvl3 spell 171325 map 1153
    };
    Position const hearhstoneAlliance[3] =
    {
        {1850.71f, 254.43f, 78.083f, 1.886526f},     // ALLiance lvl1 spell 158825
        {1936.9f, 341.35f, 90.28f, 123.479f},        // Alliance lvl2
        {1947.0f, 324.88f, 90.28f, 118.664f},        // Alliance lvl3
    };

    Position const& HearthstonePosition(Player* player, uint8 level)
    {
        uint8 idx = level ? std::min<uint8>(level, 3) - 1 : 0;
        return player->GetTeamId() == TEAM_ALLIANCE ? hearhstoneAlliance[idx] : hearhstoneHorde[idx];
    }

    // UWoW instance_garr.cpp wod_garrisone_horde_lvl1 / wod_garrisone_alliance_lvl1 ::OnPlaceBuilding
    void OnPlaceBuilding(Player* player, uint32 garrBuildingId, time_t& time)
    {
        enum
        {
            Q_BUILD_BARRACKS_H = 34461,
            Q_BUILD_BARRACKS_A = 34587,
            GAR_BARRACK_BUILD  = 26,
            NPC_GAZLO          = 78466,
            NPC_BAROS          = 77209,
        };

        if (garrBuildingId != GAR_BARRACK_BUILD)
            return;

        if (player->GetMapId() == 1152)
        {
            if (player->GetQuestStatus(Q_BUILD_BARRACKS_H) != QUEST_STATUS_INCOMPLETE)
                return;

            if (Creature* gazlo = player->FindNearestCreature(NPC_GAZLO, 100.0f))
            {
                for (uint8 text = 0; text < 3; ++text)
                    sCreatureTextMgr->SendChat(gazlo, text, player);
                player->KilledMonsterCredit(gazlo->GetEntry());
                time -= 3540;
            }
        }
        else if (player->GetMapId() == 1158)
        {
            if (player->GetQuestStatus(Q_BUILD_BARRACKS_A) != QUEST_STATUS_INCOMPLETE)
                return;

            if (Creature* baros = player->FindNearestCreature(NPC_BAROS, 100.0f))
            {
                for (uint8 text = 4; text < 8; ++text)
                    sCreatureTextMgr->SendChat(baros, text, player);
                time -= 3540;
            }
        }
    }

    struct ReturnPoint
    {
        uint32 map = 0;
        float x = 0.f, y = 0.f, z = 0.f, o = 0.f;
    };

    std::shared_mutex s_registryLock;
    std::unordered_map<ObjectGuid::LowType, std::unique_ptr<Garrison>> s_garrisons;
    std::unordered_map<ObjectGuid::LowType, ReturnPoint> s_returnPoints;

    std::mutex s_currencyLock;
    std::unordered_map<ObjectGuid::LowType, std::unordered_map<uint32, uint32>> s_currencies;

    void AddOrReplaceItem(Loot* loot, uint32 itemId, uint32 count)
    {
        for (LootItem& item : loot->items)
        {
            if (item.itemid == itemId && !item.is_looted)
            {
                item.count += count;
                return;
            }
        }

        LootStoreItem storeItem(itemId, 0, 100.0f, false, LOOT_MODE_DEFAULT, 0, uint8(std::min<uint32>(count, 255)), uint8(std::min<uint32>(count, 255)));
        loot->AddItem(storeItem);
    }
}

Garrison::Garrison(Player* owner) : _owner(owner), _siteLevel(nullptr), _followerActivationsRemainingToday(1), _lastResTaken(0)
{
    updateTimer.SetInterval(5 * IN_MILLISECONDS);
    updateTimer.Reset();
}

bool Garrison::LoadFromDB()
{
    ObjectGuid::LowType guid = _owner->GetGUID().GetCounter();

    QueryResult garrison = CharacterDatabase.Query("SELECT siteLevelId, followerActivationsRemainingToday, lastResTaken FROM character_garrison WHERE guid = {}", guid);
    if (!garrison)
        return false;

    Field* fields = garrison->Fetch();
    _siteLevel = sGarrSiteLevelStore.LookupEntry(fields[0].Get<uint32>());
    _followerActivationsRemainingToday = fields[1].Get<uint32>();
    _lastResTaken = fields[2].Get<uint32>();

    if (!_siteLevel)
        return false;

    if ((_siteLevel->SiteID == SITE_ID_GARRISON_ALLIANCE && _owner->GetTeamId() == TEAM_HORDE) ||
        (_siteLevel->SiteID == SITE_ID_GARRISON_HORDE && _owner->GetTeamId() == TEAM_ALLIANCE))
    {
        _siteLevel = sGarrSiteLevelStore.LookupEntry(getSiteLevelIdById(_owner->GetTeamId() == TEAM_ALLIANCE ? ALLIANCE : HORDE, uint8(_siteLevel->Level)));

        if (!_siteLevel)
            return false;
    }

    InitializePlots();

    if (QueryResult blueprints = CharacterDatabase.Query("SELECT buildingId FROM character_garrison_blueprints WHERE guid = {}", guid))
    {
        do
        {
            fields = blueprints->Fetch();
            if (GarrBuildingEntry const* building = sGarrBuildingStore.LookupEntry(fields[0].Get<uint32>()))
                _knownBuildings.insert(building->ID);
        }
        while (blueprints->NextRow());
    }

    if (QueryResult buildings = CharacterDatabase.Query("SELECT plotInstanceId, buildingId, timeBuilt, active FROM character_garrison_buildings WHERE guid = {}", guid))
    {
        do
        {
            fields = buildings->Fetch();
            uint32 plotInstanceId = fields[0].Get<uint32>();
            uint32 buildingId = fields[1].Get<uint32>();
            time_t timeBuilt = time_t(fields[2].Get<uint64>());
            bool active = fields[3].Get<bool>();

            Plot* plot = GetPlot(plotInstanceId);
            if (!plot)
                continue;

            if (!sGarrBuildingStore.LookupEntry(buildingId))
                continue;

            plot->BuildingInfo.PacketInfo.emplace();
            plot->BuildingInfo.PacketInfo->GarrPlotInstanceID = plotInstanceId;
            plot->BuildingInfo.PacketInfo->GarrBuildingID = buildingId;
            plot->BuildingInfo.PacketInfo->TimeBuilt = timeBuilt;
            plot->BuildingInfo.PacketInfo->Active = active;

            if (!plot->BuildingInfo.PacketInfo->Active)
                plot->buildingActivationWaiting = true;
        }
        while (buildings->NextRow());
    }

    //            0     1             2          3              4          5               6                7
    if (QueryResult missions = CharacterDatabase.Query("SELECT dbId, missionRecID, offerTime, offerDuration, startTime, travelDuration, missionDuration, missionState "
        "FROM character_garrison_missions WHERE guid = {}", guid))
    {
        do
        {
            fields = missions->Fetch();

            uint64 dbId = fields[0].Get<uint64>();
            uint32 missionRecID = fields[1].Get<uint32>();
            uint32 offerTime = fields[2].Get<uint32>();
            uint32 offerDuration = fields[3].Get<uint32>();

            if (!sGarrMissionStore.LookupEntry(missionRecID))
                continue;

            if (offerTime + offerDuration <= time(nullptr))
                continue;

            _missionIds.insert(missionRecID);
            Mission& mission = _missions[dbId];
            mission.PacketInfo.DbID = dbId;
            mission.PacketInfo.MissionRecID = missionRecID;
            mission.PacketInfo.OfferTime = offerTime;
            mission.PacketInfo.OfferDuration = offerDuration;
            mission.PacketInfo.StartTime = fields[4].Get<uint32>();
            mission.PacketInfo.TravelDuration = fields[5].Get<uint32>();
            mission.PacketInfo.MissionDuration = fields[6].Get<uint32>();
            mission.PacketInfo.MissionState = fields[7].Get<uint32>();
        } while (missions->NextRow());
    }

    //            0     1           2        3      4                5               6   7                8               9
    if (QueryResult followers = CharacterDatabase.Query("SELECT dbId, followerId, quality, level, itemLevelWeapon, itemLevelArmor, xp, currentBuilding, currentMission, status "
        "FROM character_garrison_followers WHERE guid = {}", guid))
    {
        do
        {
            fields = followers->Fetch();

            uint64 dbId = fields[0].Get<uint64>();
            uint32 followerId = fields[1].Get<uint32>();
            if (!sGarrFollowerStore.LookupEntry(followerId))
                continue;

            _followerIds.insert(followerId);
            Follower& follower = _followers[dbId];
            follower.PacketInfo.DbID = dbId;
            follower.PacketInfo.GarrFollowerID = followerId;
            follower.PacketInfo.Quality = fields[2].Get<uint32>();
            follower.PacketInfo.FollowerLevel = fields[3].Get<uint32>();
            follower.PacketInfo.ItemLevelWeapon = fields[4].Get<uint32>();
            follower.PacketInfo.ItemLevelArmor = fields[5].Get<uint32>();
            follower.PacketInfo.Xp = fields[6].Get<uint32>();
            follower.PacketInfo.CurrentBuildingID = fields[7].Get<uint32>();
            follower.PacketInfo.CurrentMissionID = fields[8].Get<uint32>();
            follower.PacketInfo.FollowerStatus = fields[9].Get<uint32>();
            if (!sGarrBuildingStore.LookupEntry(follower.PacketInfo.CurrentBuildingID))
                follower.PacketInfo.CurrentBuildingID = 0;

            if (follower.PacketInfo.CurrentMissionID)
            {
                if (Garrison::Mission* mission = GetMissionByRecID(follower.PacketInfo.CurrentMissionID))
                    mission->CurrentFollowerDBIDs.push_back(follower.PacketInfo.DbID);
                else
                    follower.PacketInfo.CurrentMissionID = 0;
            }
        }
        while (followers->NextRow());

        if (QueryResult abilities = CharacterDatabase.Query("SELECT a.dbId, a.abilityId FROM character_garrison_follower_abilities a "
            "JOIN character_garrison_followers f ON f.dbId = a.dbId WHERE f.guid = {} ORDER BY a.slot", guid))
        {
            do
            {
                fields = abilities->Fetch();
                uint64 dbId = fields[0].Get<uint64>();
                GarrAbilityEntry const* ability = sGarrAbilityStore.LookupEntry(fields[1].Get<uint32>());

                if (!ability)
                    continue;

                auto itr = _followers.find(dbId);
                if (itr == _followers.end())
                    continue;

                itr->second.PacketInfo.AbilityID.push_back(ability);
            }
            while (abilities->NextRow());
        }
    }

    if (QueryResult shipments = CharacterDatabase.Query("SELECT dbId, shipmentID, orderTime FROM character_garrison_shipment WHERE guid = {} ORDER BY orderTime ASC", guid))
    {
        do
        {
            fields = shipments->Fetch();

            uint64 dbId = fields[0].Get<uint64>();
            uint32 shipmentID = fields[1].Get<uint32>();
            uint32 orderTime = fields[2].Get<uint32>();
            PlaceShipment(shipmentID, orderTime, dbId);

        } while (shipments->NextRow());
    }
    return true;
}

void Garrison::SaveToDB(CharacterDatabaseTransaction trans)
{
    ObjectGuid::LowType guid = _owner->GetGUID().GetCounter();
    DeleteFromDB(guid, trans);

    trans->Append("INSERT INTO character_garrison (guid, siteLevelId, followerActivationsRemainingToday, lastResTaken) VALUES ({}, {}, {}, {})",
        guid, _siteLevel->ID, _followerActivationsRemainingToday, _lastResTaken);

    for (uint32 building : _knownBuildings)
        trans->Append("INSERT INTO character_garrison_blueprints (guid, buildingId) VALUES ({}, {})", guid, building);

    for (auto const& p : _plots)
    {
        Plot const& plot = p.second;
        if (plot.BuildingInfo.PacketInfo)
            trans->Append("INSERT INTO character_garrison_buildings (guid, plotInstanceId, buildingId, timeBuilt, active) VALUES ({}, {}, {}, {}, {})",
                guid, plot.BuildingInfo.PacketInfo->GarrPlotInstanceID, plot.BuildingInfo.PacketInfo->GarrBuildingID,
                uint64(plot.BuildingInfo.PacketInfo->TimeBuilt), uint32(plot.BuildingInfo.PacketInfo->Active));
    }

    for (auto const& p : _followers)
    {
        Follower const& follower = p.second;
        trans->Append("INSERT INTO character_garrison_followers (dbId, guid, followerId, quality, level, itemLevelWeapon, itemLevelArmor, xp, currentBuilding, currentMission, status) "
            "VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})",
            follower.PacketInfo.DbID, guid, follower.PacketInfo.GarrFollowerID, follower.PacketInfo.Quality, follower.PacketInfo.FollowerLevel,
            follower.PacketInfo.ItemLevelWeapon, follower.PacketInfo.ItemLevelArmor, follower.PacketInfo.Xp, follower.PacketInfo.CurrentBuildingID,
            follower.PacketInfo.CurrentMissionID, follower.PacketInfo.FollowerStatus);

        uint8 slot = 0;
        for (GarrAbilityEntry const* ability : follower.PacketInfo.AbilityID)
            trans->Append("INSERT INTO character_garrison_follower_abilities (dbId, abilityId, slot) VALUES ({}, {}, {})", follower.PacketInfo.DbID, ability->ID, slot++);
    }

    for (auto const& m : _missions)
    {
        Mission const& mission = m.second;

        if (mission.PacketInfo.MissionState == MISSION_STATE_COMPLETED)
            continue;

        if (mission.PacketInfo.OfferTime + mission.PacketInfo.OfferDuration <= time(nullptr))
            continue;

        trans->Append("INSERT INTO character_garrison_missions (dbId, guid, missionRecID, offerTime, offerDuration, startTime, travelDuration, missionDuration, missionState) "
            "VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {})",
            mission.PacketInfo.DbID, guid, mission.PacketInfo.MissionRecID, uint32(mission.PacketInfo.OfferTime), mission.PacketInfo.OfferDuration,
            uint32(mission.PacketInfo.StartTime), mission.PacketInfo.TravelDuration, mission.PacketInfo.MissionDuration, mission.PacketInfo.MissionState);
    }

    for (auto const& x : _shipments)
        for (auto const& shipment : x.second)
            trans->Append("INSERT INTO character_garrison_shipment (dbId, guid, shipmentID, orderTime) VALUES ({}, {}, {}, {})",
                shipment.ShipmentID, guid, shipment.ShipmentRecID, uint32(shipment.CreationTime));
}

void Garrison::DeleteFromDB(ObjectGuid::LowType ownerGuid, CharacterDatabaseTransaction trans)
{
    trans->Append("DELETE FROM character_garrison WHERE guid = {}", ownerGuid);
    trans->Append("DELETE FROM character_garrison_blueprints WHERE guid = {}", ownerGuid);
    trans->Append("DELETE FROM character_garrison_buildings WHERE guid = {}", ownerGuid);
    trans->Append("DELETE a FROM character_garrison_follower_abilities a JOIN character_garrison_followers f ON f.dbId = a.dbId WHERE f.guid = {}", ownerGuid);
    trans->Append("DELETE FROM character_garrison_followers WHERE guid = {}", ownerGuid);
    trans->Append("DELETE FROM character_garrison_missions WHERE guid = {}", ownerGuid);
    trans->Append("DELETE FROM character_garrison_shipment WHERE guid = {}", ownerGuid);
}

bool Garrison::Create(uint32 garrSiteId, bool enter)
{
    _siteLevel = sGarrisonMgr.GetGarrSiteLevelEntry(garrSiteId, 1);
    if (!_siteLevel)
        return false;

    InitializePlots();

    WorldPackets::Garrison::GarrisonCreateResult garrisonCreateResult;
    garrisonCreateResult.GarrSiteLevelID = _siteLevel->ID;
    _owner->SendDirectMessage(garrisonCreateResult.Write());

    if (enter)
        Enter();
    SendRemoteInfo();
    return true;
}

void Garrison::Delete()
{
    CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
    DeleteFromDB(_owner->GetGUID().GetCounter(), trans);
    CharacterDatabase.CommitTransaction(trans);

    WorldPackets::Garrison::GarrisonDeleteResult garrisonDelete;
    garrisonDelete.Result = GARRISON_SUCCESS;
    garrisonDelete.GarrSiteID = _siteLevel->SiteID;
    _owner->SendDirectMessage(garrisonDelete.Write());
}

void Garrison::InitializePlots()
{
    if (std::vector<GarrSiteLevelPlotInstEntry const*> const* plots = sGarrisonMgr.GetGarrPlotInstForSiteLevel(_siteLevel->ID))
    {
        for (size_t i = 0; i < plots->size(); ++i)
        {
            uint32 garrPlotInstanceId = plots->at(i)->GarrPlotInstanceID;
            GarrPlotInstanceEntry const* plotInstance = sGarrPlotInstanceStore.LookupEntry(garrPlotInstanceId);
            GameObjectsEntry const* gameObject = sGarrisonMgr.GetPlotGameObject(_siteLevel->MapID, garrPlotInstanceId);
            if (!plotInstance || !gameObject)
                continue;

            GarrPlotEntry const* plot = sGarrPlotStore.LookupEntry(plotInstance->GarrPlotID);
            if (!plot)
                continue;

            Plot& plotInfo = _plots[garrPlotInstanceId];
            plotInfo.PacketInfo.GarrPlotInstanceID = garrPlotInstanceId;

            float orientation = 2 * std::acos(gameObject->RotationW);

            if (_siteLevel->SiteID == SITE_ID_GARRISON_ALLIANCE)
            {
                if (garrPlotInstanceId == 18)
                    orientation = 4.991641f;
                if (garrPlotInstanceId == 22)
                    orientation = 4.799657f;
                if (garrPlotInstanceId == 24)
                    orientation = 5.628688f;
            }
            else if (_siteLevel->SiteID == SITE_ID_GARRISON_HORDE)
            {
                if (garrPlotInstanceId == 18)
                    orientation = 2.042035f;
                if (garrPlotInstanceId == 19)
                    orientation = 3.534301f;
                if (garrPlotInstanceId == 20)
                    orientation = 0.802851f;
            }

            plotInfo.PacketInfo.PlotPos.Relocate(gameObject->Position.X, gameObject->Position.Y, gameObject->Position.Z, orientation);
            plotInfo.RotationX = gameObject->RotationX;
            plotInfo.RotationY = gameObject->RotationY;
            plotInfo.RotationZ = gameObject->RotationZ;
            plotInfo.RotationW = gameObject->RotationW;

            plotInfo.PacketInfo.PlotType = plot->PlotType;
            plotInfo.EmptyGameObjectId = gameObject->ID;
            plotInfo.GarrSiteLevelPlotInstId = plots->at(i)->ID;
        }
    }
}

void Garrison::Upgrade()
{
    WorldPackets::Garrison::GarrisonUpgradeResult result;

    uint32 garrLvl = _siteLevel->Level;

    // check for cheting / modification in client
    if (garrLvl == 3)
    {
        result.Result = GARRISON_ERROR_MAX_LEVEL;
        _owner->SendDirectMessage(result.Write());
        return;
    }

    GarrSiteLevelEntry const* newSiteLevel = nullptr;
    for (GarrSiteLevelEntry const* v : sGarrSiteLevelStore)
        if (v->SiteID == _siteLevel->SiteID && v->Level == garrLvl + 1)
            newSiteLevel = v;

    if (!newSiteLevel || newSiteLevel->Level == garrLvl)
    {
        result.Result = GARRISON_ERROR_NO_BUILDING;
        _owner->SendDirectMessage(result.Write());
        return;
    }

    // cost taken from old site, not from new
    if (!GarrisonCurrency::Has(_owner, CURRENCY_TYPE_GARRISON_RESOURCES, _siteLevel->UpgradeResourceCost))
    {
        result.Result = GARRISON_ERROR_NOT_ENOUGH_CURRENCY;
        _owner->SendDirectMessage(result.Write());
        return;
    }

    // cost taken from old site, not from new
    if (!_owner->HasEnoughMoney(uint32(_siteLevel->UpgradeMoneyCost) * GOLD))
    {
        result.Result = GARRISON_ERROR_NOT_ENOUGH_GOLD;
        _owner->SendDirectMessage(result.Write());
        return;
    }

    int32 resourceCost = _siteLevel->UpgradeResourceCost;
    int32 moneyCost = _siteLevel->UpgradeMoneyCost;

    //Set new site level.
    _siteLevel = newSiteLevel;
    InitializePlots();
    OnMapUnloaded();

    switch (_siteLevel->ID)
    {
        //< alliance
        case 444:   // 2 lvl
            _owner->TeleportTo(_siteLevel->MapID, 1779.97f, 199.439f, 70.8068f, 0.3276943f);
            break;
        case 6:     // 3 lvl
            _owner->TeleportTo(_siteLevel->MapID, 1733.25f, 156.995f, 75.40f, 0.79f);
            break;
            //< horde
        case 445:   // 2 lvl
        case 259:   // 3 lvl
            _owner->TeleportTo(_siteLevel->MapID, 5756.79f, 4493.11f, 132.311f, 2.862183f);
            break;
        default:
            _owner->TeleportTo(_siteLevel->MapID, _owner->GetPositionX(), _owner->GetPositionY(), _owner->GetPositionZ(), _owner->GetOrientation());
            break;
    }

    WorldPackets::Garrison::StreamingMovie movie;
    movie.MovieIDs.push_back(_siteLevel->MovieID);
    _owner->SendDirectMessage(movie.Write());

    result.Result = GARRISON_SUCCESS;
    result.GarrSiteLevelID = _siteLevel->ID;
    _owner->SendDirectMessage(result.Write());

    GarrisonCurrency::Modify(_owner, CURRENCY_TYPE_GARRISON_RESOURCES, -resourceCost, false);
    _owner->ModifyMoney(-moneyCost * int32(GOLD), false);

    // Save us
    CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
    SaveToDB(trans);
    CharacterDatabase.CommitTransaction(trans);
}

bool Garrison::Downgrade()
{
    GarrSiteLevelEntry const* lower = nullptr;
    for (GarrSiteLevelEntry const* v : sGarrSiteLevelStore)
        if (v->SiteID == _siteLevel->SiteID && v->Level + 1 == _siteLevel->Level)
            lower = v;
    if (!lower)
        return false;

    // Plots the lower tier does not have go away with their buildings; the rest keep theirs.
    std::unordered_set<uint32> kept;
    if (std::vector<GarrSiteLevelPlotInstEntry const*> const* plots = sGarrisonMgr.GetGarrPlotInstForSiteLevel(lower->ID))
        for (GarrSiteLevelPlotInstEntry const* plot : *plots)
            kept.insert(plot->GarrPlotInstanceID);
    for (auto itr = _plots.begin(); itr != _plots.end();)
        itr = kept.count(itr->first) ? std::next(itr) : _plots.erase(itr);

    _siteLevel = lower;
    InitializePlots();
    OnMapUnloaded();

    CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
    SaveToDB(trans);
    CharacterDatabase.CommitTransaction(trans);

    if (GarrisonMgr::IsGarrisonMap(_owner->GetMapId()))
        Enter();
    SendWindow(0, 0);
    return true;
}

void Garrison::Enter()
{
    if (!GarrisonMgr::IsGarrisonMap(_owner->GetMapId()))
    {
        std::unique_lock<std::shared_mutex> lock(s_registryLock);
        ReturnPoint& point = s_returnPoints[_owner->GetGUID().GetCounter()];
        point.map = _owner->GetMapId();
        point.x = _owner->GetPositionX();
        point.y = _owner->GetPositionY();
        point.z = _owner->GetPositionZ();
        point.o = _owner->GetOrientation();
    }

    Position const& pos = HearthstonePosition(_owner, GetGarrisonLevel());
    _owner->TeleportTo(_siteLevel->MapID, pos.GetPositionX(), pos.GetPositionY(), pos.GetPositionZ(), pos.GetOrientation());
}

void Garrison::Leave() const
{
    ReturnPoint point;
    {
        std::shared_lock<std::shared_mutex> lock(s_registryLock);
        auto itr = s_returnPoints.find(_owner->GetGUID().GetCounter());
        if (itr != s_returnPoints.end())
            point = itr->second;
    }

    if (point.map && !GarrisonMgr::IsGarrisonMap(point.map))
        _owner->TeleportTo(point.map, point.x, point.y, point.z, point.o);
    else
        _owner->TeleportTo(_owner->m_homebindMapId, _owner->m_homebindX, _owner->m_homebindY, _owner->m_homebindZ, _owner->GetOrientation());
}

void Garrison::OnMapLoaded(Map* map)
{
    if (_plotsSpawned)
        return;

    _plotsSpawned = true;
    for (Plot* plot : GetPlots())
    {
        if (GameObject* go = plot->CreateGameObject(map, GetFaction(), this))
            map->AddToMap(go);
        UpdatePlotPad(*plot, map);
        EnsureFinalizer(*plot, map);
    }
}

void Garrison::OnMapUnloaded()
{
    _plotsSpawned = false;
    ShipmentConteiners.clear();
    for (auto& p : _plots)
    {
        p.second.BuildingInfo.Guid.Clear();
        p.second.BuildingInfo.Spawns.clear();
        p.second.FinalizerGuid.Clear();
        if (p.second.BuildingInfo.PacketInfo && !p.second.BuildingInfo.PacketInfo->Active)
            p.second.buildingActivationWaiting = true;
    }
}

void Garrison::EnsureFinalizer(Plot& plot, Map* map)
{
    if (!map || !plot.BuildingInfo.CanActivate() || !plot.BuildingInfo.PacketInfo || plot.BuildingInfo.PacketInfo->Active)
        return;

    if (!plot.FinalizerGuid.IsEmpty())
        if (map->GetGameObject(plot.FinalizerGuid))
            return;

    FinalizeGarrisonPlotGOInfo const* finalizeInfo = sGarrisonMgr.GetPlotFinalizeGOInfo(plot.PacketInfo.GarrPlotInstanceID);
    if (!finalizeInfo)
        return;

    Position const& pos = finalizeInfo->FactionInfo[GetFaction()].Pos;
    uint32 entry = finalizeInfo->FactionInfo[GetFaction()].GameObjectId;
    GameObject* finalizer = new GameObject();
    if (!finalizer->Create(map->GenerateLowGuid<HighGuid::GameObject>(), entry, map, PHASEMASK_NORMAL,
        pos.GetPositionX(), pos.GetPositionY(), pos.GetPositionZ(), pos.GetOrientation(), G3D::Quat(), 255, GO_STATE_READY))
    {
        delete finalizer;
        LOG_ERROR("module", "Garrison failed to create finalize scroll {} for plot {}", entry, plot.PacketInfo.GarrPlotInstanceID);
        return;
    }

    finalizer->SetRespawnTime(0);
    finalizer->setActive(true);
    finalizer->SetVisibilityDistanceOverride(VisibilityDistanceType::Large);
    if (!map->AddToMap(finalizer))
    {
        delete finalizer;
        return;
    }

    plot.FinalizerGuid = finalizer->GetGUID();
    plot.buildingActivationWaiting = false;
    UpdatePlotPad(plot, map);
    LOG_INFO("module", "Garrison finalize scroll {} on plot {} at {:.2f} {:.2f} {:.2f}", entry, plot.PacketInfo.GarrPlotInstanceID,
        pos.GetPositionX(), pos.GetPositionY(), pos.GetPositionZ());
}

void Garrison::UpdatePlotPad(Plot& plot, Map* map)
{
    if (!map || !_owner || !plot.EmptyGameObjectId)
        return;

    float x = plot.PacketInfo.PlotPos.GetPositionX();
    float y = plot.PacketInfo.PlotPos.GetPositionY();
    map->LoadGrid(x, y);

    WorldObject* center = nullptr;
    if (!plot.BuildingInfo.Guid.IsEmpty())
        center = map->GetGameObject(plot.BuildingInfo.Guid);
    if (!center)
        center = _owner;

    float range = center->GetExactDist2d(x, y) + 10.f;
    if (range < 15.f)
        range = 15.f;
    std::list<GameObject*> pads;
    center->GetGameObjectListWithEntryInGrid(pads, plot.EmptyGameObjectId, range);

    bool occupied = plot.BuildingInfo.PacketInfo.has_value();
    for (GameObject* pad : pads)
    {
        if (pad->GetGUID() == plot.BuildingInfo.Guid)
            continue;
        if (pad->GetExactDist2d(x, y) > 8.f)
            continue;

        if (occupied)
        {
            if (pad->isSpawned())
                pad->DespawnOrUnsummon(0s, Seconds(365 * DAY));
        }
        else if (!pad->isSpawned())
            pad->Respawn();
    }
}

void Garrison::Update(uint32 diff)
{
    updateTimer.Update(diff);
    if (!updateTimer.Passed())
        return;

    updateTimer.Reset();

    Map* map = _owner->GetMap();
    if (!map || !_plotsSpawned || map->GetId() != uint32(GetGarrisonMapID()))
        return;

    for (auto& p : _plots)
    {
        UpdatePlotPad(p.second, map);
        EnsureFinalizer(p.second, map);
    }

    //! Shipment orders update.
    for (auto const& data : ShipmentConteiners)
    {
        GameObject* object = map->GetGameObject(data.second);
        if (!object)
            continue;

        bool ready = false;
        for (auto& ship_data : _shipments[data.first])
        {
            if (ship_data.ShipmentDuration > 0)
                ship_data.ShipmentDuration -= int32(updateTimer.GetInterval() / IN_MILLISECONDS);
            else
            {
                ready = true;
                ship_data.ShipmentDuration = 0;
            }
        }

        // go horde non actine = 20508, active 19959
        // go alliance non active 15585, active = 16091
        if (ready)
        {
            uint32 displayID = _owner->GetTeamId() == TEAM_HORDE ? 19959 : 16091;
            if (object->GetDisplayId() != displayID)
                object->SetDisplayId(displayID);

            if (object->GetGoState() == GO_STATE_ACTIVE_ALTERNATIVE)
                object->SetGoState(GO_STATE_READY);
        }
        else
        {
            ready = true;
            for (LootItem const& loot : object->loot.items)
                if (!loot.is_looted)
                    ready = false;

            if (ready)
            {
                uint32 displayID = _owner->GetTeamId() == TEAM_HORDE ? 20508 : 15585;
                if (object->GetDisplayId() != displayID)
                    object->SetDisplayId(displayID);
                GOState state = _shipments[data.first].size() ? GO_STATE_ACTIVE_ALTERNATIVE : GO_STATE_READY;
                if (object->GetGoState() != state)
                    object->SetGoState(state);
            }
        }
    }
}

GarrisonFactionIndex Garrison::GetFaction() const
{
    return _owner->GetTeamId() == TEAM_HORDE ? GARRISON_FACTION_INDEX_HORDE : GARRISON_FACTION_INDEX_ALLIANCE;
}

std::vector<Garrison::Plot*> Garrison::GetPlots()
{
    std::vector<Plot*> plots;
    plots.reserve(_plots.size());
    for (auto& p : _plots)
        plots.push_back(&p.second);

    return plots;
}

Garrison::Plot* Garrison::GetPlot(uint32 garrPlotInstanceId)
{
    auto itr = _plots.find(garrPlotInstanceId);
    if (itr != _plots.end())
        return &itr->second;

    return nullptr;
}

Garrison::Plot const* Garrison::GetPlot(uint32 garrPlotInstanceId) const
{
    auto itr = _plots.find(garrPlotInstanceId);
    if (itr != _plots.end())
        return &itr->second;

    return nullptr;
}

Garrison::Plot* Garrison::GetPlotWithBuildingType(uint32 BuildingTypeID)
{
    for (auto& p : _plots)
    {
        if (p.second.BuildingInfo.PacketInfo)
        {
            GarrBuildingEntry const* existingBuilding = sGarrBuildingStore.AssertEntry(p.second.BuildingInfo.PacketInfo->GarrBuildingID);
            if (existingBuilding->Type == BuildingTypeID)
                return &p.second;
        }
    }
    return nullptr;
}

Garrison::Plot* Garrison::GetPlotByFinalizer(ObjectGuid const& guid)
{
    for (auto& p : _plots)
        if (p.second.FinalizerGuid == guid)
            return &p.second;
    return nullptr;
}

bool Garrison::LearnBlueprint(uint32 garrBuildingId)
{
    WorldPackets::Garrison::GarrisonLearnBlueprintResult learnBlueprintResult;
    learnBlueprintResult.BuildingID = garrBuildingId;
    learnBlueprintResult.Result = GARRISON_SUCCESS;

    if (!sGarrBuildingStore.LookupEntry(garrBuildingId))
        learnBlueprintResult.Result = GARRISON_ERROR_INVALID_BUILDINGID;
    else if (_knownBuildings.count(garrBuildingId))
        learnBlueprintResult.Result = GARRISON_ERROR_BLUEPRINT_KNOWN;
    else
        _knownBuildings.insert(garrBuildingId);

    _owner->SendDirectMessage(learnBlueprintResult.Write());

    return learnBlueprintResult.Result == GARRISON_SUCCESS;
}

void Garrison::UnlearnBlueprint(uint32 garrBuildingId)
{
    WorldPackets::Garrison::GarrisonUnlearnBlueprintResult unlearnBlueprintResult;
    unlearnBlueprintResult.BuildingID = garrBuildingId;
    unlearnBlueprintResult.Result = GARRISON_SUCCESS;

    if (!sGarrBuildingStore.LookupEntry(garrBuildingId))
        unlearnBlueprintResult.Result = GARRISON_ERROR_INVALID_BUILDINGID;
    else if (!_knownBuildings.count(garrBuildingId))
        unlearnBlueprintResult.Result = GARRISON_ERROR_BLUEPRINT_NOT_KNOWN;
    else
        _knownBuildings.erase(garrBuildingId);

    _owner->SendDirectMessage(unlearnBlueprintResult.Write());
}

namespace
{
    std::string CleanField(std::string text)
    {
        for (char& c : text)
            if (c == '\t' || c == '\n' || c == '\r')
                c = ' ';
        return text;
    }

    uint32 UiError(GarrisonError error)
    {
        switch (error)
        {
            case GARRISON_SUCCESS: return 0;
            case GARRISON_ERROR_INVALID_PLOT: return 3;
            case GARRISON_ERROR_INVALID_PLOT_BUILDING: return 4;
            case GARRISON_ERROR_BLUEPRINT_NOT_KNOWN: return 5;
            case GARRISON_ERROR_BUILDING_EXISTS: return 6;
            case GARRISON_ERROR_INVALID_BUILDINGID: return 7;
            case GARRISON_ERROR_NOT_ENOUGH_CURRENCY: return 8;
            case GARRISON_ERROR_NOT_ENOUGH_GOLD: return 9;
            case GARRISON_ERROR_NO_BUILDING: return 10;
            case GARRISON_ERROR_MAX_LEVEL: return 11;
            default: return 2;
        }
    }

    struct MechanicTypeInfo
    {
        std::string Name;
        uint32 Icon = 0;
    };

    MechanicTypeInfo const* MechanicType(uint32 id)
    {
        static std::map<uint32, MechanicTypeInfo> types;
        static bool loaded = false;
        if (!loaded)
        {
            loaded = true;
            if (QueryResult result = WorldDatabase.Query("SELECT id, name, icon_file_data_id FROM db2_garr_mechanic_type"))
            {
                do
                {
                    Field* fields = result->Fetch();
                    MechanicTypeInfo& row = types[fields[0].Get<uint32>()];
                    row.Name = fields[1].IsNull() ? std::string() : fields[1].Get<std::string>();
                    row.Icon = fields[2].Get<uint32>();
                } while (result->NextRow());
            }
        }
        auto itr = types.find(id);
        return itr == types.end() ? nullptr : &itr->second;
    }
}

void Garrison::SendWindow(uint32 uiResult, uint8 openPage)
{
    if (!_siteLevel || !_owner)
        return;

    bool horde = GetFaction() == GARRISON_FACTION_INDEX_HORDE;
    bool anyBuilding = false;
    for (auto const& plot : _plots)
        if (plot.second.BuildingInfo.PacketInfo)
            anyBuilding = true;

    // The intro quest that pays for the first building is not on this client yet.
    if (openPage == 1 && !anyBuilding && GarrisonCurrency::Get(_owner, CURRENCY_TYPE_GARRISON_RESOURCES) < 150)
        GarrisonCurrency::Modify(_owner, CURRENCY_TYPE_GARRISON_RESOURCES, 500, false);

    std::ostringstream out;
    if (openPage == 1)
        out << "OPEN\tbuildings\n";
    else if (openPage == 2)
        out << "OPEN\tmissions\n";

    out << "R\t" << uiResult << "\n";
    out << "G\t1\t" << (horde ? 1 : 0) << "\t" << uint32(_siteLevel->Level) << "\t"
        << GarrisonCurrency::Get(_owner, CURRENCY_TYPE_GARRISON_RESOURCES) << "\t" << GetResNumber() << "\t"
        << _siteLevel->SiteID << "\t" << _siteLevel->MapID << "\t"
        << _siteLevel->UpgradeResourceCost << "\t" << _siteLevel->UpgradeMoneyCost << "\t";
    char townPos[64];
    snprintf(townPos, sizeof(townPos), "%.6f\t%.6f", _siteLevel->TownHall.X, _siteLevel->TownHall.Y);
    out << townPos << "\n";

    std::unordered_set<uint32> plotTypes;
    for (auto const& plot : _plots)
        if (GarrPlotInstanceEntry const* instance = sGarrPlotInstanceStore.LookupEntry(plot.first))
            plotTypes.insert(instance->GarrPlotID);

    for (auto const& plot : _plots)
    {
        GarrPlotInstanceEntry const* instance = sGarrPlotInstanceStore.LookupEntry(plot.first);
        uint32 garrPlot = instance ? instance->GarrPlotID : 0;
        uint32 buildingId = 0;
        uint32 active = 1;
        uint32 left = 0;
        if (plot.second.BuildingInfo.PacketInfo)
        {
            buildingId = plot.second.BuildingInfo.PacketInfo->GarrBuildingID;
            active = plot.second.BuildingInfo.PacketInfo->Active ? 1 : 0;
            if (!active)
            {
                GarrBuildingEntry const* building = sGarrBuildingStore.LookupEntry(buildingId);
                time_t ready = plot.second.BuildingInfo.PacketInfo->TimeBuilt + (building ? building->BuildDuration : 0);
                time_t now = time(nullptr);
                left = ready > now ? uint32(ready - now) : 0;
            }
        }
        std::string name = instance ? instance->Name : "";
        float uiX = 0.f;
        float uiY = 0.f;
        uint32 uiSize = 0;
        if (GarrSiteLevelPlotInstEntry const* marker = sGarrSiteLevelPlotInstStore.LookupEntry(plot.second.GarrSiteLevelPlotInstId))
        {
            uiX = marker->Landmark.X;
            uiY = marker->Landmark.Y;
            uiSize = marker->Unknown;
        }
        char uiPos[64];
        snprintf(uiPos, sizeof(uiPos), "%.6f\t%.6f", uiX, uiY);
        out << "P\t" << plot.first << "\t" << garrPlot << "\t" << buildingId << "\t" << active << "\t" << left << "\t"
            << CleanField(name) << "\t" << uiPos << "\t" << uiSize << "\n";
    }

    std::unordered_set<uint32> listed;
    for (GarrPlotBuildingEntry const* link : sGarrPlotBuildingStore)
    {
        if (!plotTypes.count(link->GarrPlotID) || !listed.insert(link->GarrBuildingID).second)
            continue;

        GarrBuildingEntry const* building = sGarrBuildingStore.LookupEntry(link->GarrBuildingID);
        if (!building)
            continue;
        // Mine, farm and fishing shack have no blueprint. Retail still draws the
        // level-1 building on the plot with a lock until the quest chain grants it.
        // Higher ranks are included even above the garrison tier so the hover
        // tooltip can list every level.
        bool questPlot = link->GarrPlotID == 28 || link->GarrPlotID == 29 || link->GarrPlotID == 31;
        if (!(building->Flags & GARRISON_BUILDING_FLAG_NEEDS_PLAN) && !(questPlot && building->Level == 1))
            continue;

        bool known = _knownBuildings.count(building->ID) || building->Level == 1;
        std::string name = horde ? building->NameHorde : building->NameAlliance;
        if (name.empty())
            name = horde ? building->NameAlliance : building->NameHorde;
        out << "B\t" << building->ID << "\t" << building->Type << "\t" << building->Level << "\t" << link->GarrPlotID << "\t"
            << building->CostCurrencyAmount << "\t" << building->CostMoney << "\t" << building->BuildDuration << "\t"
            << (known ? 1 : 0) << "\t" << CleanField(name) << "\t" << CleanField(building->Tooltip) << "\n";
    }

    for (auto const& follower : _followers)
    {
        GarrFollowerEntry const* entry = sGarrFollowerStore.LookupEntry(follower.second.PacketInfo.GarrFollowerID);
        std::string name;
        std::string specName;
        uint32 portrait = 0;
        if (entry)
        {
            uint32 creatureId = horde ? entry->HordeCreatureID : entry->AllianceCreatureID;
            if (CreatureTemplate const* creature = sObjectMgr->GetCreatureTemplate(creatureId))
                name = creature->Name;
            if (name.empty())
                name = horde ? entry->HordeSourceText : entry->AllianceSourceText;
            portrait = horde ? entry->HordePortraitIconID : entry->AlliancePortraitIconID;
            uint32 specId = horde ? entry->HordeGarrClassSpecID : entry->AllianceGarrClassSpecID;
            if (GarrClassSpecEntry const* spec = sGarrClassSpecStore.LookupEntry(specId))
                specName = !spec->NameGenderless.empty() ? spec->NameGenderless : spec->NameMale;
        }
        if (name.empty())
            name = "Follower";
        uint32 level = follower.second.PacketInfo.FollowerLevel;
        uint32 nextXp = level >= 100
            ? GarrisonDB2::GetXPForNextFollowerQuality(follower.second.PacketInfo.Quality)
            : GarrisonDB2::GetXPForNextFollowerLevel(level);
        out << "F\t" << follower.first << "\t" << follower.second.PacketInfo.GarrFollowerID << "\t"
            << level << "\t" << follower.second.PacketInfo.Quality << "\t"
            << follower.second.PacketInfo.CurrentMissionID << "\t" << CleanField(name) << "\t"
            << portrait << "\t" << CleanField(specName) << "\t" << follower.second.PacketInfo.CurrentBuildingID << "\t"
            << follower.second.GetItemLevel() << "\t" << follower.second.PacketInfo.ItemLevelWeapon << "\t"
            << follower.second.PacketInfo.ItemLevelArmor << "\t" << follower.second.PacketInfo.Xp << "\t" << nextXp << "\n";
        for (GarrAbilityEntry const* ability : follower.second.PacketInfo.AbilityID)
            if (ability)
                out << "A\t" << follower.first << "\t" << ability->ID << "\t" << ability->IconFileDataID << "\t"
                    << CleanField(ability->Name) << "\t" << ((ability->Flags & 1) ? 1 : 0) << "\t"
                    << CleanField(ability->Description) << "\n";
    }

    std::string missionIds;
    for (auto const& mission : _missions)
    {
        GarrMissionEntry const* entry = sGarrMissionStore.LookupEntry(mission.second.PacketInfo.MissionRecID);
        uint32 left = 0;
        if (mission.second.PacketInfo.MissionState != 0 && mission.second.PacketInfo.StartTime)
        {
            time_t ready = time_t(mission.second.PacketInfo.StartTime) + mission.second.PacketInfo.MissionDuration;
            time_t now = time(nullptr);
            left = ready > now ? uint32(ready - now) : 0;
        }
        MechanicTypeInfo const* env = MechanicType(entry ? entry->GarrMechanicTypeID : 0);
        out << "M\t" << mission.first << "\t" << mission.second.PacketInfo.MissionRecID << "\t"
            << mission.second.PacketInfo.MissionState << "\t" << left << "\t0\t" << CleanField(entry ? entry->Name : "") << "\t"
            << CleanField(entry ? entry->Location : "") << "\t" << CleanField(entry ? entry->Description : "") << "\t"
            << (entry ? entry->MissionDuration : 0) << "\t" << (entry ? entry->ReqFollowersCount : 0) << "\t"
            << (entry ? entry->ReqResourcesCount : 0) << "\t" << (entry ? entry->BaseXP : 0) << "\t"
            << (entry ? entry->ReqLevel : 0) << "\t" << CleanField(env ? env->Name : "") << "\t"
            << (env ? env->Icon : 0) << "\t" << (entry ? entry->BaseChance : 0) << "\n";
        for (uint64 followerId : mission.second.CurrentFollowerDBIDs)
            out << "Y\t" << mission.first << "\t" << followerId << "\n";
        if (!missionIds.empty())
            missionIds += ",";
        missionIds += std::to_string(mission.second.PacketInfo.MissionRecID);
    }

    if (!missionIds.empty())
    {
        std::string sql = "SELECT x.garr_mission_id, e.name, e.portrait_file_data_id, IFNULL(mt.name, ''), "
            "IFNULL(mt.icon_file_data_id, 0), IFNULL(m.garr_ability_id, 0) "
            "FROM db2_garr_mission_x_encounter x "
            "JOIN db2_garr_encounter e ON e.id = x.garr_encounter_id "
            "LEFT JOIN db2_garr_encounter_x_mechanic xm ON xm.garr_encounter_id = e.id "
            "LEFT JOIN db2_garr_mechanic m ON m.id = xm.garr_mechanic_id "
            "LEFT JOIN db2_garr_mechanic_type mt ON mt.id = m.garr_mechanic_type_id "
            "WHERE x.garr_mission_id IN (" + missionIds + ") ORDER BY x.garr_mission_id, x.order_index, xm.id";
        if (QueryResult encounters = WorldDatabase.Query(sql.c_str()))
        {
            do
            {
                Field* fields = encounters->Fetch();
                std::string enemy = fields[1].IsNull() ? std::string() : fields[1].Get<std::string>();
                std::string mechanic = fields[3].IsNull() ? std::string() : fields[3].Get<std::string>();
                out << "E\t" << fields[0].Get<uint32>() << "\t" << CleanField(enemy) << "\t" << fields[2].Get<uint32>() << "\t"
                    << CleanField(mechanic) << "\t" << fields[4].Get<uint32>() << "\t" << fields[5].Get<uint32>() << "\n";
            } while (encounters->NextRow());
        }
    }

    std::string text = out.str();
    WorldPacket data(SMSG_ESTERIA_GARRISON_STATE, text.size() + 1);
    data.append(text.c_str(), text.size() + 1);
    _owner->SendDirectMessage(&data);
}

void Garrison::HandleUiAction(uint8 op, uint32 a, uint32 b)
{
    uint32 result = 0;
    bool save = false;
    uint8 openPage = 0;

    switch (op)
    {
        case 1:
            Enter();
            break;
        case 2:
            Leave();
            break;
        case 3:
        {
            if (GarrBuildingEntry const* building = sGarrBuildingStore.LookupEntry(b))
                if (building->Level == 1 && (building->Flags & GARRISON_BUILDING_FLAG_NEEDS_PLAN) && !_knownBuildings.count(b))
                    _knownBuildings.insert(b);

            result = UiError(CheckBuildingPlacement(a, b));
            if (result == 0)
            {
                PlaceBuilding(a, b);
                save = true;
            }
            break;
        }
        case 4:
            result = UiError(CheckBuildingRemoval(a));
            if (result == 0)
            {
                CancelBuildingConstruction(a);
                save = true;
            }
            break;
        case 5:
            if (_siteLevel->Level >= 3)
                result = 11;
            else if (!GarrisonCurrency::Has(_owner, CURRENCY_TYPE_GARRISON_RESOURCES, _siteLevel->UpgradeResourceCost))
                result = 8;
            else if (!_owner->HasEnoughMoney(uint32(_siteLevel->UpgradeMoneyCost) * GOLD))
                result = 9;
            else
            {
                Upgrade();
                save = true;
            }
            break;
        case 11:
            ActivateBuilding(a);
            save = true;
            break;
        case 7:
        {
            Mission* mission = GetMission(a);
            if (!mission)
                result = 12;
            else if (!mission->CanStart(_owner))
            {
                GarrMissionEntry const* entry = sGarrMissionStore.LookupEntry(mission->PacketInfo.MissionRecID);
                if (entry && !GarrisonCurrency::Has(_owner, CURRENCY_TYPE_GARRISON_RESOURCES, entry->ReqResourcesCount))
                    result = 8;
                else
                    result = 13;
            }
            else
            {
                mission->Start(_owner);
                save = true;
            }
            break;
        }
        case 8:
        {
            Mission* mission = GetMission(a);
            if (!mission)
                result = 12;
            else if (mission->PacketInfo.MissionState == MISSION_STATE_IN_PROGRESS
                && mission->PacketInfo.StartTime + mission->PacketInfo.MissionDuration <= time(nullptr))
            {
                mission->Complete(_owner);
                save = true;
            }
            else if (mission->CanBonusRoll())
            {
                mission->BonusRoll(_owner);
                save = true;
            }
            else
                result = 12;
            break;
        }
        case 12:
        {
            Mission* mission = GetMission(a);
            GarrMissionEntry const* entry = mission ? sGarrMissionStore.LookupEntry(mission->PacketInfo.MissionRecID) : nullptr;
            if (!mission || !entry || mission->PacketInfo.MissionState != MISSION_STATE_AVAILABLE)
            {
                result = 12;
                break;
            }
            if (b == 0)
            {
                mission->CurrentFollowerDBIDs.clear();
                break;
            }
            Follower* follower = GetFollower(b);
            if (!follower || follower->PacketInfo.CurrentMissionID != 0 || follower->PacketInfo.CurrentBuildingID != 0)
            {
                result = 13;
                break;
            }
            bool already = false;
            for (uint64 id : mission->CurrentFollowerDBIDs)
                if (id == b)
                    already = true;
            if (already)
                break;
            if (mission->CurrentFollowerDBIDs.size() >= entry->ReqFollowersCount)
            {
                result = 13;
                break;
            }
            mission->CurrentFollowerDBIDs.push_back(b);
            break;
        }
        case 13:
        {
            Mission* mission = GetMission(a);
            if (!mission || mission->PacketInfo.MissionState != MISSION_STATE_AVAILABLE)
                result = 12;
            else
                mission->CurrentFollowerDBIDs.remove(uint64(b));
            break;
        }
        case 14:
            OfferTableMissions();
            openPage = 2;
            break;
        default:
            break;
    }

    if (save)
    {
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        SaveToDB(trans);
        GarrisonCurrency::Save(_owner, trans);
        CharacterDatabase.CommitTransaction(trans);
    }

    SendWindow(result, openPage);
}

void Garrison::PlaceBuilding(uint32 garrPlotInstanceId, uint32 garrBuildingId, bool quest/* = false*/)
{
    WorldPackets::Garrison::GarrisonPlaceBuildingResult placeBuildingResult;
    placeBuildingResult.Result = CheckBuildingPlacement(garrPlotInstanceId, garrBuildingId, quest);
    if (placeBuildingResult.Result == GARRISON_SUCCESS)
    {
        placeBuildingResult.BuildingInfo.GarrPlotInstanceID = garrPlotInstanceId;
        placeBuildingResult.BuildingInfo.GarrBuildingID = garrBuildingId;
        placeBuildingResult.BuildingInfo.TimeBuilt = time(nullptr);

        Plot* plot = GetPlot(garrPlotInstanceId);
        plot->buildingActivationWaiting = true;

        uint32 oldBuildingId = 0;
        Map* map = _plotsSpawned ? FindMap() : nullptr;
        GarrBuildingEntry const* building = sGarrBuildingStore.AssertEntry(garrBuildingId);
        if (map)
        {
            OnPlaceBuilding(_owner, garrBuildingId, placeBuildingResult.BuildingInfo.TimeBuilt);
            plot->DeleteGameObject(map);
        }

        if (plot->BuildingInfo.PacketInfo)
        {
            oldBuildingId = plot->BuildingInfo.PacketInfo->GarrBuildingID;
            if (sGarrBuildingStore.AssertEntry(oldBuildingId)->Type != building->Type)
                plot->ClearBuildingInfo(_owner);
        }

        // If build by quest - skip building state and spawn building.
        if (quest)
        {
            placeBuildingResult.PlayActivationCinematic = true;
            placeBuildingResult.BuildingInfo.Active = true;
        }
        else
        {
            GarrisonCurrency::Modify(_owner, building->CostCurrencyID, -building->CostCurrencyAmount, false);
            _owner->ModifyMoney(-building->CostMoney * int32(GOLD), false);
        }

        plot->SetBuildingInfo(placeBuildingResult.BuildingInfo, _owner);
        if (map)
        {
            if (GameObject* go = plot->CreateGameObject(map, GetFaction(), this))
                map->AddToMap(go);
            UpdatePlotPad(*plot, map);
        }

        if (oldBuildingId)
        {
            WorldPackets::Garrison::GarrisonBuildingRemoved buildingRemoved;
            buildingRemoved.Result = GARRISON_SUCCESS;
            buildingRemoved.GarrPlotInstanceID = garrPlotInstanceId;
            buildingRemoved.GarrBuildingID = oldBuildingId;
            _owner->SendDirectMessage(buildingRemoved.Write());
        }
    }

    _owner->SendDirectMessage(placeBuildingResult.Write());
}

void Garrison::CancelBuildingConstruction(uint32 garrPlotInstanceId)
{
    WorldPackets::Garrison::GarrisonBuildingRemoved buildingRemoved;
    buildingRemoved.Result = CheckBuildingRemoval(garrPlotInstanceId);
    if (buildingRemoved.Result == GARRISON_SUCCESS)
    {
        Plot* plot = GetPlot(garrPlotInstanceId);

        buildingRemoved.GarrPlotInstanceID = garrPlotInstanceId;
        buildingRemoved.GarrBuildingID = plot->BuildingInfo.PacketInfo->GarrBuildingID;

        Map* map = _plotsSpawned ? FindMap() : nullptr;
        if (map)
            plot->DeleteGameObject(map);

        plot->ClearBuildingInfo(_owner);
        _owner->SendDirectMessage(buildingRemoved.Write());

        GarrBuildingEntry const* constructing = sGarrBuildingStore.AssertEntry(buildingRemoved.GarrBuildingID);
        // Refund construction/upgrade cost
        GarrisonCurrency::Modify(_owner, constructing->CostCurrencyID, constructing->CostCurrencyAmount, false);
        _owner->ModifyMoney(constructing->CostMoney * int32(GOLD), false);

        if (constructing->Level > 1)
        {
            // Restore previous level building
            GarrBuildingEntry const* restored = sGarrisonMgr.GetPreviousLevelBuilding(constructing->Type, constructing->Level);
            ASSERT(restored);

            WorldPackets::Garrison::GarrisonPlaceBuildingResult placeBuildingResult;
            placeBuildingResult.Result = GARRISON_SUCCESS;
            placeBuildingResult.BuildingInfo.GarrPlotInstanceID = garrPlotInstanceId;
            placeBuildingResult.BuildingInfo.GarrBuildingID = restored->ID;
            placeBuildingResult.BuildingInfo.TimeBuilt = time(nullptr);
            placeBuildingResult.BuildingInfo.Active = true;

            plot->SetBuildingInfo(placeBuildingResult.BuildingInfo, _owner);
            _owner->SendDirectMessage(placeBuildingResult.Write());
        }

        if (map)
        {
            if (GameObject* go = plot->CreateGameObject(map, GetFaction(), this))
                map->AddToMap(go);
            UpdatePlotPad(*plot, map);
        }
    }
    else
        _owner->SendDirectMessage(buildingRemoved.Write());
}

void Garrison::ActivateBuilding(uint32 garrPlotInstanceId)
{
    if (Plot* plot = GetPlot(garrPlotInstanceId))
    {
        if (plot->BuildingInfo.CanActivate() && plot->BuildingInfo.PacketInfo && !plot->BuildingInfo.PacketInfo->Active)
        {
            plot->BuildingInfo.PacketInfo->Active = true;

            if (Map* map = _plotsSpawned ? FindMap() : nullptr)
            {
                if (GameObject* finalizer = map->GetGameObject(plot->FinalizerGuid))
                    finalizer->Delete();
                plot->FinalizerGuid.Clear();

                plot->DeleteGameObject(map);
                if (GameObject* go = plot->CreateGameObject(map, GetFaction(), this))
                    map->AddToMap(go);
                UpdatePlotPad(*plot, map);
            }

            WorldPackets::Garrison::GarrisonBuildingActivated buildingActivated;
            buildingActivated.GarrPlotInstanceID = garrPlotInstanceId;
            _owner->SendDirectMessage(buildingActivated.Write());
        }
    }
}

void Garrison::AddFollower(uint32 garrFollowerId)
{
    WorldPackets::Garrison::GarrisonAddFollowerResult addFollowerResult;
    GarrFollowerEntry const* followerEntry = sGarrFollowerStore.LookupEntry(garrFollowerId);
    if (_followerIds.count(garrFollowerId) || !followerEntry)
    {
        addFollowerResult.Result = GARRISON_GENERIC_UNKNOWN_ERROR;
        _owner->SendDirectMessage(addFollowerResult.Write());
        return;
    }

    _followerIds.insert(garrFollowerId);
    uint64 dbId = sGarrisonMgr.GenerateFollowerDbId();
    Follower& follower = _followers[dbId];
    follower.PacketInfo.DbID = dbId;
    follower.PacketInfo.GarrFollowerID = garrFollowerId;
    follower.PacketInfo.Quality = follower.RollQuality(followerEntry->Quality);
    follower.PacketInfo.FollowerLevel = followerEntry->Level;
    follower.PacketInfo.ItemLevelWeapon = followerEntry->ItemLevelWeapon;
    follower.PacketInfo.ItemLevelArmor = followerEntry->ItemLevelArmor;
    follower.PacketInfo.AbilityID = sGarrisonMgr.RollFollowerAbilities(followerEntry, follower.PacketInfo.Quality, GetFaction(), true);
    follower.PacketInfo.FollowerStatus = FOLLOWER_STATUS_BASE;

    addFollowerResult.Follower = follower.PacketInfo;
    _owner->SendDirectMessage(addFollowerResult.Write());

    if (GarrMissionEntry const* mission = sGarrisonMgr.GetMissionAtFollowerTaking(garrFollowerId))
        AddMission(mission->ID);
}

void Garrison::AddMission(uint32 missionRecID)
{
    WorldPackets::Garrison::GarrisonAddMissionResult addMissionResult;
    GarrMissionEntry const* missionEntry = sGarrMissionStore.LookupEntry(missionRecID);
    if (_missionIds.count(missionRecID) || !missionEntry)
    {
        addMissionResult.Result = GARRISON_GENERIC_UNKNOWN_ERROR;
        _owner->SendDirectMessage(addMissionResult.Write());
        return;
    }

    _missionIds.insert(missionRecID);
    uint64 dbId = sGarrisonMgr.GenerateMissionDbId();
    Mission& mission = _missions[dbId];
    mission.PacketInfo.DbID = dbId;
    mission.PacketInfo.MissionRecID = missionRecID;
    mission.PacketInfo.OfferTime = time(nullptr);
    mission.PacketInfo.OfferDuration = missionEntry->OfferDuration;
    mission.PacketInfo.StartTime = 0;
    mission.PacketInfo.TravelDuration = 0;
    mission.PacketInfo.MissionDuration = missionEntry->MissionDuration;
    mission.PacketInfo.MissionState = MISSION_STATE_AVAILABLE;

    addMissionResult.unk = 1;
    addMissionResult.MissionData = mission.PacketInfo;
    _owner->SendDirectMessage(addMissionResult.Write());
}

bool Garrison::OfferTableMissions()
{
    uint32 available = 0;
    for (auto const& mission : _missions)
        if (mission.second.PacketInfo.MissionState == MISSION_STATE_AVAILABLE)
            ++available;

    bool added = false;
    for (uint32 id : sGarrisonMgr.GetRandomMissionIDs())
    {
        if (available >= 6)
            break;
        if (_missionIds.count(id))
            continue;
        size_t before = _missions.size();
        AddMission(id);
        if (_missions.size() != before)
        {
            ++available;
            added = true;
        }
    }

    if (!added)
        return false;

    CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
    SaveToDB(trans);
    CharacterDatabase.CommitTransaction(trans);
    return true;
}

Garrison::Follower const* Garrison::GetFollower(uint64 dbId) const
{
    auto itr = _followers.find(dbId);
    if (itr != _followers.end())
        return &itr->second;

    return nullptr;
}

Garrison::Follower* Garrison::GetFollower(uint64 dbId)
{
    auto itr = _followers.find(dbId);
    if (itr != _followers.end())
        return &itr->second;

    return nullptr;
}

Garrison::Follower* Garrison::GetFollowerByID(uint32 entry)
{
    for (auto& v : _followers)
        if (v.second.PacketInfo.GarrFollowerID == entry)
            return &v.second;

    return nullptr;
}

void Garrison::ReTrainFollower(int32 miscValue, uint32 followerID)
{
    auto follower = GetFollowerByID(followerID);
    if (!follower)
        return;

    auto followerEntry = sGarrFollowerStore.LookupEntry(follower->PacketInfo.GarrFollowerID);
    if (!followerEntry)
        return;

    follower->PacketInfo.AbilityID = sGarrisonMgr.RollFollowerAbilities(followerEntry, follower->PacketInfo.Quality, GetFaction(), miscValue == 1 ? false : true);
}

Garrison::Mission const* Garrison::GetMission(uint64 dbId) const
{
    auto itr = _missions.find(dbId);
    if (itr != _missions.end())
        return &itr->second;

    return nullptr;
}

Garrison::Mission* Garrison::GetMission(uint64 dbId)
{
    auto itr = _missions.find(dbId);
    if (itr != _missions.end())
        return &itr->second;

    return nullptr;
}

Garrison::Mission* Garrison::GetMissionByRecID(uint32 missionRecID)
{
    for (auto& m : _missions)
        if (m.second.PacketInfo.MissionRecID == missionRecID)
            return &m.second;

    return nullptr;
}

void Garrison::SendInfo()
{
    WorldPackets::Garrison::GetGarrisonInfoResult garrisonInfo;
    garrisonInfo.GarrSiteID = _siteLevel->SiteID;
    garrisonInfo.GarrSiteLevelID = _siteLevel->ID;
    garrisonInfo.FactionIndex = GetFaction();
    garrisonInfo.NumFollowerActivationsRemaining = _followerActivationsRemainingToday;
    for (auto& p : _plots)
    {
        Plot& plot = p.second;
        garrisonInfo.Plots.push_back(&plot.PacketInfo);
        if (plot.BuildingInfo.PacketInfo)
            garrisonInfo.Buildings.push_back(&*plot.BuildingInfo.PacketInfo);
    }

    for (auto const& p : _followers)
        garrisonInfo.Followers.push_back(&p.second.PacketInfo);

    for (auto const& i : _missions)
        garrisonInfo.Missions.push_back(&i.second.PacketInfo);

    _owner->SendDirectMessage(garrisonInfo.Write());
}

void Garrison::SendRemoteInfo() const
{
    if (GarrisonMgr::IsGarrisonMap(_owner->GetMapId()))
        return;

    WorldPackets::Garrison::GarrisonRemoteInfo remoteInfo;
    remoteInfo.Sites.resize(1);

    WorldPackets::Garrison::GarrisonRemoteSiteInfo& remoteSiteInfo = remoteInfo.Sites[0];
    remoteSiteInfo.GarrSiteLevelID = _siteLevel->ID;
    for (auto const& p : _plots)
        if (p.second.BuildingInfo.PacketInfo)
            remoteSiteInfo.Buildings.emplace_back(p.first, p.second.BuildingInfo.PacketInfo->GarrBuildingID);

    _owner->SendDirectMessage(remoteInfo.Write());
}

void Garrison::SendBlueprintAndSpecializationData()
{
    WorldPackets::Garrison::GarrisonRequestBlueprintAndSpecializationDataResult data;
    data.BlueprintsKnown = &_knownBuildings;
    _owner->SendDirectMessage(data.Write());
}

void Garrison::SendBuildingLandmarks(Player* receiver) const
{
    WorldPackets::Garrison::GarrisonBuildingLandmarks buildingLandmarks;
    buildingLandmarks.Landmarks.reserve(_plots.size());

    for (auto const& p : _plots)
    {
        Plot const& plot = p.second;
        if (plot.BuildingInfo.PacketInfo)
            if (uint32 garrBuildingPlotInstId = sGarrisonMgr.GetGarrBuildingPlotInst(plot.BuildingInfo.PacketInfo->GarrBuildingID, plot.GarrSiteLevelPlotInstId))
                buildingLandmarks.Landmarks.emplace_back(garrBuildingPlotInstId, plot.PacketInfo.PlotPos);
    }

    receiver->SendDirectMessage(buildingLandmarks.Write());
}

void Garrison::SendGarrisonUpgradebleResult(Player* receiver) const
{
    WorldPackets::Garrison::GarrisonIsUpgradeableResult result;
    switch (_siteLevel->Level)
    {
        case 1:
        case 2: //Requare Alliance Q: 36592, Horde Q: 36567
            result.Result = _plots.size() < 2 ? GARRISON_ERROR_NOT_ALLOW_GARRISON_UPGRADE : GARRISON_SUCCESS;
            break;
        default:
            result.Result = GARRISON_ERROR_MAX_LEVEL;
            break;
    }

    receiver->SendDirectMessage(result.Write());
}

Map* Garrison::FindMap() const
{
    if (!_instanceId)
        return nullptr;
    return sMapMgr->FindMap(_siteLevel->MapID, _instanceId);
}

GarrisonError Garrison::CheckBuildingPlacement(uint32 garrPlotInstanceId, uint32 garrBuildingId, bool byQuest/*=false*/) const
{
    GarrPlotInstanceEntry const* plotInstance = sGarrPlotInstanceStore.LookupEntry(garrPlotInstanceId);
    Plot const* plot = GetPlot(garrPlotInstanceId);
    if (!plotInstance || !plot)
        return GARRISON_ERROR_INVALID_PLOT;

    GarrBuildingEntry const* building = sGarrBuildingStore.LookupEntry(garrBuildingId);
    if (!building)
        return GARRISON_ERROR_INVALID_BUILDINGID;

    if (!sGarrisonMgr.IsPlotMatchingBuilding(plotInstance->GarrPlotID, garrBuildingId))
        return GARRISON_ERROR_INVALID_PLOT_BUILDING;

    // Cannot place buldings of higher level than garrison level
    if (building->Level > _siteLevel->Level)
        return GARRISON_ERROR_INVALID_BUILDINGID;

    if (building->Flags & GARRISON_BUILDING_FLAG_NEEDS_PLAN)
    {
        if (!_knownBuildings.count(garrBuildingId))
            return GARRISON_ERROR_BLUEPRINT_NOT_KNOWN;
    }
    else if (!byQuest) // Building is built as a quest reward
        return GARRISON_ERROR_INVALID_BUILDINGID;

    // Check all plots to find if we already have this building
    for (auto const& p : _plots)
    {
        if (p.second.BuildingInfo.PacketInfo)
        {
            GarrBuildingEntry const* existingBuilding = sGarrBuildingStore.AssertEntry(p.second.BuildingInfo.PacketInfo->GarrBuildingID);
            if (existingBuilding->Type == building->Type)
                if (p.first != garrPlotInstanceId || existingBuilding->Level + 1 != building->Level)    // check if its an upgrade in same plot
                    return GARRISON_ERROR_BUILDING_EXISTS;
        }
    }

    if (!byQuest && building->CostCurrencyAmount && !GarrisonCurrency::Has(_owner, building->CostCurrencyID, building->CostCurrencyAmount))
        return GARRISON_ERROR_NOT_ENOUGH_CURRENCY;

    if (building->CostMoney && !_owner->HasEnoughMoney(uint32(building->CostMoney) * GOLD))
        return GARRISON_ERROR_NOT_ENOUGH_GOLD;

    // New building cannot replace another building currently under construction
    if (plot->BuildingInfo.PacketInfo)
        if (!plot->BuildingInfo.PacketInfo->Active)
            return GARRISON_ERROR_NO_BUILDING;

    return GARRISON_SUCCESS;
}

GarrisonError Garrison::CheckBuildingRemoval(uint32 garrPlotInstanceId) const
{
    Plot const* plot = GetPlot(garrPlotInstanceId);
    if (!plot)
        return GARRISON_ERROR_INVALID_PLOT;

    if (!plot->BuildingInfo.PacketInfo)
        return GARRISON_ERROR_NO_BUILDING;

    if (plot->BuildingInfo.CanActivate())
        return GARRISON_ERROR_BUILDING_EXISTS;

    return GARRISON_SUCCESS;
}

GameObject* Garrison::Plot::CreateGameObject(Map* map, GarrisonFactionIndex faction, Garrison* garrison)
{
    uint32 entry = EmptyGameObjectId;
    GarrBuildingEntry const* buildingEtry = nullptr;
    if (BuildingInfo.PacketInfo)
    {
        GarrPlotInstanceEntry const* plotInstance = sGarrPlotInstanceStore.AssertEntry(PacketInfo.GarrPlotInstanceID);
        GarrPlotEntry const* plot = sGarrPlotStore.AssertEntry(plotInstance->GarrPlotID);
        buildingEtry = sGarrBuildingStore.AssertEntry(BuildingInfo.PacketInfo->GarrBuildingID);
        entry = faction == GARRISON_FACTION_INDEX_HORDE ? plot->HordeConstructionGameObjectID : plot->AllianceConstructionGameObjectID;
        if (BuildingInfo.PacketInfo->Active || !entry)
            entry = faction == GARRISON_FACTION_INDEX_HORDE ? buildingEtry->HordeGameObjectID : buildingEtry->AllianceGameObjectID;
    }

    if (!sObjectMgr->GetGameObjectTemplate(entry))
    {
        LOG_ERROR("module", "Garrison attempted to spawn gameobject whose template doesn't exist ({})", entry);
        return nullptr;
    }

    Position const& pos = PacketInfo.PlotPos;
    GameObject* building = new GameObject();
    if (!building->Create(map->GenerateLowGuid<HighGuid::GameObject>(), entry, map, PHASEMASK_NORMAL, pos.GetPositionX(), pos.GetPositionY(), pos.GetPositionZ(), pos.GetOrientation(),
        G3D::Quat(RotationX, RotationY, RotationZ, RotationW), 255, GO_STATE_READY))
    {
        delete building;
        return nullptr;
    }

    uint32 wodType = sGarrisonMgr.GetWoDGameObjectType(entry);
    if (wodType == GAMEOBJECT_TYPE_GARRISON_BUILDING || wodType == GAMEOBJECT_TYPE_GARRISON_PLOT)
    {
        uint32 build = BuildingInfo.PacketInfo && BuildingInfo.PacketInfo->Active ? BuildingInfo.PacketInfo->GarrBuildingID : 0;
        if (std::list<GarrisonBuildingSpawn> const* goList = sGarrisonMgr.GetGoSpawnBuilding(PacketInfo.GarrPlotInstanceID, build))
        for (GarrisonBuildingSpawn const& data : *goList)
        {
            if (GarrisonMgr::getFirstMap(map->GetId()) != data.mapid)
                continue;

            // ignore building state object for already build object.
            if ((data.building && !BuildingInfo.PacketInfo) ||
                (BuildingInfo.PacketInfo && BuildingInfo.PacketInfo->Active == data.building))
                continue;

            GameObject* linkGO = new GameObject();
            if (!linkGO->Create(map->GenerateLowGuid<HighGuid::GameObject>(), data.id, map, PHASEMASK_NORMAL, data.posX, data.posY, data.posZ, data.orientation,
                G3D::Quat(data.rotation0, data.rotation1, data.rotation2, data.rotation3), 255, GO_STATE_READY) ||
                !linkGO->IsPositionValid() || !map->AddToMap(linkGO))
            {
                delete linkGO;
                continue;
            }
            linkGO->SetRespawnDelay(RESP_GO_LOOT);

            if (buildingEtry && sGarrisonMgr.GetWoDGameObjectType(data.id) == GAMEOBJECT_TYPE_GARRISON_SHIPMENT)
                garrison->ShipmentConteiners[buildingEtry->Type] = linkGO->GetGUID();
            BuildingInfo.Spawns.insert(linkGO->GetGUID());
        }

        if (std::list<GarrisonBuildingSpawn> const* npcList = sGarrisonMgr.GetNpcSpawnBuilding(PacketInfo.GarrPlotInstanceID, build))
        for (GarrisonBuildingSpawn const& data : *npcList)
        {
            if (GarrisonMgr::getFirstMap(map->GetId()) != data.mapid)
                continue;
            // ignore building state object for already build object.
            if ((data.building && !BuildingInfo.PacketInfo) ||
                (BuildingInfo.PacketInfo && BuildingInfo.PacketInfo->Active == data.building))
                continue;
            Creature* linkNPC = new Creature();
            if (!linkNPC->Create(map->GenerateLowGuid<HighGuid::Unit>(), map, PHASEMASK_NORMAL, data.id, 0, data.posX, data.posY, data.posZ, data.orientation) ||
                !linkNPC->IsPositionValid() || !map->AddToMap(linkNPC))
            {
                delete linkNPC;
                continue;
            }
            if (data.building)
                linkNPC->SetUInt32Value(UNIT_NPC_EMOTESTATE, urand(0, 1) ? 173 : 69);

            BuildingInfo.Spawns.insert(linkNPC->GetGUID());
        }
    }

    BuildingInfo.Guid = building->GetGUID();
    return building;
}

void Garrison::Plot::DeleteGameObject(Map* map)
{
    if (BuildingInfo.Guid.IsEmpty())
        return;

    for (ObjectGuid const& guid : BuildingInfo.Spawns)
    {
        if (guid.IsCreature())
        {
            if (Creature* creature = map->GetCreature(guid))
                creature->AddObjectToRemoveList();
        }
        else if (guid.IsGameObject())
        {
            if (GameObject* go = map->GetGameObject(guid))
                go->Delete();
        }
    }

    BuildingInfo.Spawns.clear();

    if (GameObject* oldBuilding = map->GetGameObject(BuildingInfo.Guid))
        oldBuilding->Delete();

    BuildingInfo.Guid.Clear();
}

void Garrison::Plot::ClearBuildingInfo(Player* owner)
{
    WorldPackets::Garrison::GarrisonPlotPlaced plotPlaced;
    plotPlaced.PlotInfo = &PacketInfo;
    owner->SendDirectMessage(plotPlaced.Write());

    BuildingInfo.PacketInfo.reset();
}

void Garrison::Plot::SetBuildingInfo(WorldPackets::Garrison::GarrisonBuildingInfo const& buildingInfo, Player* owner)
{
    if (!BuildingInfo.PacketInfo)
    {
        WorldPackets::Garrison::GarrisonPlotRemoved plotRemoved;
        plotRemoved.GarrPlotInstanceID = PacketInfo.GarrPlotInstanceID;
        owner->SendDirectMessage(plotRemoved.Write());
    }

    BuildingInfo.PacketInfo = buildingInfo;
}

bool Garrison::Building::CanActivate() const
{
    if (PacketInfo)
    {
        GarrBuildingEntry const* building = sGarrBuildingStore.AssertEntry(PacketInfo->GarrBuildingID);
        if (PacketInfo->TimeBuilt + building->BuildDuration <= time(nullptr))
            return true;
    }

    return false;
}

uint32 Garrison::Follower::GetItemLevel() const
{
    return (PacketInfo.ItemLevelWeapon + PacketInfo.ItemLevelArmor) / 2;
}

void Garrison::Follower::IncreaseFollowerItemLevel(uint32 spellId, int32 basePoints, int32 miscValueB, Player* caster)
{
    bool updateInfo = false;

    uint32 bp = uint32(basePoints);
    uint32 mvb = uint32(miscValueB);

    switch (spellId)
    {
        // Description: Equip a follower with an item level $s2 weapon.
        case 168143:
        case 168150:
        case 168389:
            if (PacketInfo.ItemLevelWeapon < mvb)
            {
                PacketInfo.ItemLevelWeapon = mvb;
                updateInfo = true;
            }
            break;
            // Description: Upgrade a follower's weapon by $s1 item levels.
        case 168154:
        case 168155:
        case 168156:
        case 168157:
        case 168158:
        case 168159:
        case 168161:
        case 168395:
            if (PacketInfo.ItemLevelWeapon < mvb)
            {
                PacketInfo.ItemLevelWeapon += bp;
                updateInfo = true;
            }
            break;
            // Description: Upgrade a follower's weapon by 15 item levels, up to a total item level of 655.
        case 168162:
        case 168246:
        case 168151:
            if (PacketInfo.ItemLevelWeapon < 655)
            {
                PacketInfo.ItemLevelWeapon += bp;
                updateInfo = true;
            }
            break;
            // Description: Upgrade a follower's armor by $s1 item levels.
        case 168235:
        case 168236:
        case 168237:
        case 168238:
        case 168239:
        case 168240:
        case 168241:
            if (PacketInfo.ItemLevelArmor < mvb)
            {
                PacketInfo.ItemLevelArmor += bp;
                updateInfo = true;
            }
            break;
            // Description: Equip a follower with a full set of item level $s2 armor.
        case 168242:
        case 168243:
        case 168244:
        case 168245:
            if (PacketInfo.ItemLevelArmor < mvb)
            {
                PacketInfo.ItemLevelArmor = mvb;
                updateInfo = true;
            }
            break;
        case 174914: // wrong spell for effect
            break;
        default:
            break;
    }

    if (updateInfo)
    {
        if (PacketInfo.ItemLevelWeapon > 675)
            PacketInfo.ItemLevelWeapon = 675;

        if (PacketInfo.ItemLevelArmor > 675)
            PacketInfo.ItemLevelArmor = 675;

        WorldPackets::Garrison::GarrisonFollowerChangedItemLevel update;
        update.Follower = PacketInfo;
        caster->SendDirectMessage(update.Write());
    }
}

uint8 Garrison::Follower::RollQuality(uint32 baseQuality)
{
    // 35% - rare, 7% - epic
    uint32 r = urand(0, 100);
    uint8 quality = FOLLOWER_QUALITY_UNCOMMON;
    if (r >= 65 && r < 90)
        quality = FOLLOWER_QUALITY_RARE;
    else if (r >= 93 && r <= 100)
        quality = FOLLOWER_QUALITY_EPIC;

    return quality > baseQuality ? quality : uint8(baseQuality);
}

uint32 Garrison::GetAreaIdForTeam(uint32 team)
{
    switch (team)
    {
        case ALLIANCE:
            return 7078;
        case HORDE:
            return 7004;
    }
    return 0;
}

void Garrison::Mission::Start(Player* owner)
{
    if (Garrison* garrison = GarrisonRegistry::Get(owner))
    {
        // check followers
        for (auto f : CurrentFollowerDBIDs)
        {
            if (Garrison::Follower* follower = garrison->GetFollower(f))
                follower->PacketInfo.CurrentMissionID = PacketInfo.MissionRecID;
        }

        PacketInfo.MissionState = MISSION_STATE_IN_PROGRESS;
        PacketInfo.StartTime = time(nullptr);

        WorldPackets::Garrison::GarrisonStartMissionResult missionRes;
        missionRes.MissionData = PacketInfo;
        missionRes.FollowerDBIDs.insert(missionRes.FollowerDBIDs.begin(), CurrentFollowerDBIDs.begin(), CurrentFollowerDBIDs.end());
        owner->SendDirectMessage(missionRes.Write());

        if (GarrMissionEntry const* entry = sGarrMissionStore.LookupEntry(PacketInfo.MissionRecID))
            GarrisonCurrency::Modify(owner, CURRENCY_TYPE_GARRISON_RESOURCES, -int32(entry->ReqResourcesCount));

        garrison->SendMissionListUpdate(false);
    }
}

void Garrison::Mission::Complete(Player* owner)
{
    if (Garrison* garrison = GarrisonRegistry::Get(owner))
    {
        // succeeded or failed
        bool bonus = HasBonusRoll();

        if (bonus)
            PacketInfo.MissionState = MISSION_STATE_WAITING_BONUS;
        else
            PacketInfo.MissionState = MISSION_STATE_COMPLETED;

        WorldPackets::Garrison::GarrisonCompleteMissionResult res;
        res.MissionData = PacketInfo;
        res.MissionRecID = PacketInfo.MissionRecID;
        res.Succeeded = bonus;
        owner->SendDirectMessage(res.Write());

        for (auto f : CurrentFollowerDBIDs)
        {
            if (Garrison::Follower* follower = garrison->GetFollower(f))
            {
                if (!bonus)
                    follower->PacketInfo.CurrentMissionID = 0;

                if (GarrMissionEntry const* entry = sGarrMissionStore.LookupEntry(PacketInfo.MissionRecID))
                {
                    WorldPackets::Garrison::GarrisonFollowerChangedXP data;
                    data.TotalXp = entry->BaseXP;
                    data.Follower = follower->PacketInfo;

                    follower->GiveXP(entry->BaseXP);

                    data.Follower2 = follower->PacketInfo;
                    owner->SendDirectMessage(data.Write());
                }
            }
        }

        if (!bonus)
        {
            CurrentFollowerDBIDs.clear();
            garrison->SendMissionListUpdate(true);
        }
    }
}

void Garrison::SendMissionListUpdate(bool openMissionNpc) const
{
    WorldPackets::Garrison::GarrisonMissionListUpdate data;
    data.openMissionNpc = openMissionNpc;
    _owner->SendDirectMessage(data.Write());
}

void Garrison::Mission::BonusRoll(Player* owner)
{
    if (Garrison* garrison = GarrisonRegistry::Get(owner))
    {
        PacketInfo.MissionState = MISSION_STATE_COMPLETED;

        WorldPackets::Garrison::GarrisonMissionBonusRollResult res;
        res.MissionData = PacketInfo;
        res.MissionRecID = PacketInfo.MissionRecID;
        owner->SendDirectMessage(res.Write());

        // GarrMissionReward.db2 (follower XP / money / currency / item per mission) was dropped after 6.x and is not
        // in the retail files this port reads, so the bonus roll frees the followers and continues the mission line.
        for (auto f : CurrentFollowerDBIDs)
            if (Garrison::Follower* follower = garrison->GetFollower(f))
                follower->PacketInfo.CurrentMissionID = 0;

        CurrentFollowerDBIDs.clear();

        garrison->RewardMission(PacketInfo.MissionRecID);
        garrison->SendMissionListUpdate(true);
    }
}

bool Garrison::Mission::HasBonusRoll()
{
    float chance = ComputeSuccessChance();
    return roll_chance_f(chance);
}

void Garrison::Follower::GiveXP(uint32 xp)
{
    uint32 curXp = PacketInfo.Xp;
    uint32 nextLvlXP = GetXPForNextUpgrade();
    uint32 newXP = curXp + xp;

    if (PacketInfo.FollowerLevel == 100 && PacketInfo.Quality == FOLLOWER_QUALITY_EPIC)
        newXP = 0;

    // calc level xp
    while (nextLvlXP && newXP >= nextLvlXP && PacketInfo.FollowerLevel < 100)
    {
        newXP -= nextLvlXP;

        if (PacketInfo.FollowerLevel < 100)
            GiveLevel(PacketInfo.FollowerLevel + 1);

        nextLvlXP = GetXPForNextUpgrade();
    }

    // calc level quality
    while (nextLvlXP && newXP >= nextLvlXP && PacketInfo.FollowerLevel == 100 && PacketInfo.Quality < FOLLOWER_QUALITY_EPIC)
    {
        newXP -= nextLvlXP;

        if (PacketInfo.Quality < FOLLOWER_QUALITY_EPIC)
            GiveQuality(PacketInfo.Quality + 1);

        nextLvlXP = GetXPForNextUpgrade();
    }

    PacketInfo.Xp = newXP;
}

uint32 Garrison::Follower::GetXPForNextUpgrade()
{
    if (PacketInfo.FollowerLevel < 100)
        return GarrisonDB2::GetXPForNextFollowerLevel(PacketInfo.FollowerLevel);
    else if (PacketInfo.FollowerLevel == 100)
        return GarrisonDB2::GetXPForNextFollowerQuality(PacketInfo.Quality);

    return 0;
}

bool Garrison::Mission::CanStart(Player* owner)
{
    Garrison* garrison = GarrisonRegistry::Get(owner);

    if (!garrison)
        return false;

    if (!sGarrMissionStore.LookupEntry(PacketInfo.MissionRecID))
        return false;

    if (PacketInfo.MissionState != MISSION_STATE_AVAILABLE)
        return false;

    if (PacketInfo.StartTime != time_t(0))
        return false;

    GarrMissionEntry const* entry = sGarrMissionStore.LookupEntry(PacketInfo.MissionRecID);

    if (!GarrisonCurrency::Has(owner, CURRENCY_TYPE_GARRISON_RESOURCES, entry->ReqResourcesCount))
        return false;

    if (CurrentFollowerDBIDs.empty() || CurrentFollowerDBIDs.size() != entry->ReqFollowersCount)
        return false;

    for (auto f : CurrentFollowerDBIDs)
    {
        Garrison::Follower* follower = garrison->GetFollower(f);

        if (!follower)
            return false;

        if (follower->PacketInfo.CurrentMissionID != 0 || follower->PacketInfo.CurrentBuildingID != 0)
            return false;
    }

    return true;
}

bool Garrison::Mission::CanBonusRoll()
{
    if (!sGarrMissionStore.LookupEntry(PacketInfo.MissionRecID))
        return false;

    if (PacketInfo.MissionState != MISSION_STATE_WAITING_BONUS)
        return false;

    if (PacketInfo.StartTime + PacketInfo.MissionDuration > time(nullptr))
        return false;

    return true;
}

float Garrison::Mission::ComputeSuccessChance()
{
    return 100.0f;
}

float Garrison::Mission::CalcChance(float a, float b, float c)
{
    float d = 0.0f;
    if (c >= 0)
        d = ((b - a) * c) + a;
    else
        d = (c + 1) * a;

    return d;
}

uint32 Garrison::Mission::GetDuration(Player* /*owner*/)
{
    return PacketInfo.MissionDuration;
}

void Garrison::RewardMission(uint32 missionRecID)
{
    if (GarrMissionEntry const* mission = sGarrisonMgr.GetNextMissionInQuestLine(missionRecID))
        AddMission(mission->ID);
}

/*
The Garrison Cache next to your Town Hall accumulates Garrison Resources (GR)
at a rate of 1 GR every 10 minutes of real time (6 per hour),
which works out to 144 GR every full day (6 x 24hrs = 144 GR).
*/
uint32 Garrison::GetResNumber() const
{
    constexpr uint32 default_resource_num = 50;
    constexpr uint32 limit_cap = 500;
    constexpr uint32 min_counter = 10;

    if (!_lastResTaken)
        return default_resource_num;

    uint32 res = uint32(time(nullptr) - _lastResTaken) / (min_counter * MINUTE);
    return res > limit_cap ? limit_cap : res;
}

void Garrison::UpdateResTakenTime()
{
    _lastResTaken = uint32(time(nullptr));

    CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
    SaveToDB(trans);
    CharacterDatabase.CommitTransaction(trans);
}

//! Activate some buildings at finishing quests as complete spells not exist on dbc. For example: spellID 165077
void Garrison::OnQuestReward(uint32 questID)
{
    switch (questID)
    {
        // Open Herb Garden PlotID = 63 & BuildID = 29
        case 36404:
        case 34193:
            PlaceBuilding(63, 29, true);
            break;
        // Open Mines PlotID = 59 & BuildID = 61
        case 35154:
        case 34192:
            PlaceBuilding(59, 61, true);
            break;
        // Open Fishing PlotID = 67 & BuildID = 64
        case 36870:
        case 36612:
            PlaceBuilding(67, 64, true);
            break;
        // Open Pet Menagerie PlotID = 81 & BuildID = 42
        case 36483:
        case 36662:
            PlaceBuilding(81, 42, true);
            break;
        default:
            break;
    }
}

bool Garrison::canAddShipmentOrder(Creature* source)
{
    if (!(sGarrisonMgr.GetNpcFlags2(source->GetEntry()) & UNIT_NPC_FLAG2_SHIPMENT_ORDER))
        return false;

    GarrShipment const* data = sGarrisonMgr.GetGarrShipment(source->GetEntry(), SHIPMENT_GET_BY_NPC);
    if (!data)
        return false;

    if (uint32 questID = getQuestIdReqForShipment(_siteLevel->SiteID, data->cEntry->BuildingType))
    {
        QuestStatus status = _owner->GetQuestStatus(questID);
        if (status == QUEST_STATUS_NONE)
            return false;
    }

    // check if we have aready build building.
    for (auto const& p : _plots)
    {
        if (p.second.BuildingInfo.PacketInfo && p.second.BuildingInfo.PacketInfo->Active)
        {
            GarrBuildingEntry const* existingBuilding = sGarrBuildingStore.AssertEntry(p.second.BuildingInfo.PacketInfo->GarrBuildingID);
            if (existingBuilding->Type == data->cEntry->BuildingType)
                return true;
        }
    }

    return false;
}

uint32 Garrison::GetPlotInstanceForBuildingType(uint32 type) const
{
    for (auto const& p : _plots)
    {
        if (p.second.BuildingInfo.PacketInfo)
        {
            GarrBuildingEntry const* existingBuilding = sGarrBuildingStore.AssertEntry(p.second.BuildingInfo.PacketInfo->GarrBuildingID);
            if (existingBuilding->Type == type)
                return p.second.BuildingInfo.PacketInfo->GarrPlotInstanceID;
        }
    }
    return 0;
}

void Garrison::OnGossipSelect(WorldObject* source)
{
    if (!(sGarrisonMgr.GetNpcFlags2(source->GetEntry()) & UNIT_NPC_FLAG2_SHIPMENT_ORDER))
        return;

    GarrShipment const* data = sGarrisonMgr.GetGarrShipment(source->GetEntry(), SHIPMENT_GET_BY_NPC);
    if (!data)
        return;

    if (uint32 questID = getQuestIdReqForShipment(_siteLevel->SiteID, data->cEntry->BuildingType))
    {
        QuestStatus status = _owner->GetQuestStatus(questID);
        if (status == QUEST_STATUS_NONE)
            return;
    }

    //SMSG_OPEN_SHIPMENT_NPC_FROM_GOSSIP
    WorldPackets::Garrison::OpenShipmentNPCFromGossip openShipment;
    openShipment.NpcGUID = source->GetGUID();
    openShipment.CharShipmentContainerID = data->data->ShipmentConteinerID;
    _owner->SendDirectMessage(openShipment.Write());
}

void Garrison::SendShipmentInfo(ObjectGuid const& guid)
{
    GarrShipment const* shipment = sGarrisonMgr.GetGarrShipment(guid.GetEntry(), SHIPMENT_GET_BY_NPC);
    Garrison::Plot const* plot = shipment ? GetPlotWithBuildingType(shipment->cEntry->BuildingType) : nullptr;

    uint32 questID = shipment ? getQuestIdReqForShipment(_siteLevel->SiteID, shipment->cEntry->BuildingType) : 0;

    //SMSG_GET_SHIPMENT_INFO_RESPONSE
    WorldPackets::Garrison::GetShipmentInfoResponse shipmentResponse;
    shipmentResponse.Success = shipment && plot && (!questID || _owner->GetQuestStatus(questID) != QUEST_STATUS_NONE);
    if (shipmentResponse.Success)
    {
        GarrBuildingEntry const* existingBuilding = sGarrBuildingStore.AssertEntry(plot->BuildingInfo.PacketInfo->GarrBuildingID);

        // check if has finish quest for activate. if rewardet - use usual state. if in progress - send
        shipmentResponse.ShipmentID = (!questID || _owner->GetQuestStatus(questID) == QUEST_STATUS_REWARDED) ? shipment->ShipmentID : getProgressShipment(questID);
        shipmentResponse.MaxShipments = existingBuilding->MaxShipments;
        shipmentResponse.PlotInstanceID = plot->BuildingInfo.PacketInfo->GarrPlotInstanceID;

        shipmentResponse.Shipments.assign(_shipments[shipment->cEntry->BuildingType].begin(), _shipments[shipment->cEntry->BuildingType].end());
    }

    _owner->SendDirectMessage(shipmentResponse.Write());
}

void Garrison::CreateShipment(ObjectGuid const& guid, uint32 count)
{
    GarrShipment const* shipment = sGarrisonMgr.GetGarrShipment(guid.GetEntry(), SHIPMENT_GET_BY_NPC);
    if (!shipment)
        return;

    Garrison::Plot const* plot = GetPlotWithBuildingType(shipment->cEntry->BuildingType);
    if (!plot)
        return;

    uint32 sh = shipment->ShipmentID;
    if (uint32 questID = getQuestIdReqForShipment(_siteLevel->SiteID, shipment->cEntry->BuildingType))
        if (_owner->GetQuestStatus(questID) != QUEST_STATUS_REWARDED)
            sh = getProgressShipment(questID);

    CharShipmentEntry const* shipmentEntry = sCharShipmentStore.LookupEntry(sh);
    if (!shipmentEntry)
        return;

    uint32 spellCast = 0;
    for (uint32 i = 0; i < count; ++i)
    {
        spellCast = shipmentEntry->SpellCreation;
        switch (sh)
        {
            case 60:  spellCast = 172840; break;
            case 103: spellCast = 171959; break;
            case 106: spellCast = 172841; break;
            case 107: spellCast = 172842; break;
            case 108: spellCast = 172843; break;
            case 105: spellCast = 172844; break;
            case 104: spellCast = 172845; break;
            case 72:  spellCast = 172846; break;
            case 125: spellCast = 173065; break;
            case 123: spellCast = 173066; break;
            case 121: spellCast = 173067; break;
            case 135: spellCast = 173068; break;
            case 133: spellCast = 173069; break;
            case 131: spellCast = 173070; break;
            case 129: spellCast = 173071; break;
            case 127: spellCast = 173072; break;
        }
        HandleSpell(spellCast);
    }
}

void Garrison::CreateGarrisonShipment(uint32 shipmentID)
{
    uint64 dbID = PlaceShipment(shipmentID, uint32(time(nullptr)));

    //SMSG_CREATE_SHIPMENT_RESPONSE
    WorldPackets::Garrison::CreateShipmentResponse shipmentResponse;
    shipmentResponse.ShipmentRecID = shipmentID;
    shipmentResponse.ShipmentID = dbID;
    shipmentResponse.Result = dbID ? 0 : 1;    //0 - OK

    _owner->SendDirectMessage(shipmentResponse.Write());
}

uint64 Garrison::PlaceShipment(uint32 shipmentID, uint32 placeTime, uint64 dbID/* = 0*/)
{
    CharShipmentEntry const* shipmentEntry = sCharShipmentStore.LookupEntry(shipmentID);
    if (!shipmentEntry)
        return 0;

    CharShipmentConteiner const* shipmentConteinerEntry = sCharShipmentContainerStore.LookupEntry(shipmentEntry->ShipmentConteinerID);
    if (!shipmentConteinerEntry)
        return 0;

    Garrison::Plot* plot = GetPlotWithBuildingType(shipmentConteinerEntry->BuildingType);
    if (!plot)
        return 0;

    GarrBuildingEntry const* existingBuilding = sGarrBuildingStore.AssertEntry(plot->BuildingInfo.PacketInfo->GarrBuildingID);
    if (!existingBuilding)
        return 0;

    if (_shipments[shipmentConteinerEntry->BuildingType].size() >= existingBuilding->MaxShipments)
        return 0;

    uint32 EndShipment = shipmentEntry->TimeForShipment + placeTime;
    uint32 lastFinishTime = 0;

    // find last finishing time.
    for (auto const& x : _shipments[shipmentConteinerEntry->BuildingType])
    {
        uint32 end = uint32(x.CreationTime) + x.ShipmentDuration;
        if (!lastFinishTime || end > lastFinishTime)
            lastFinishTime = end;
    }

    // last in progress. so out complition is incrased.
    if (lastFinishTime > placeTime)
        EndShipment = lastFinishTime + shipmentEntry->TimeForShipment;

    WorldPackets::Garrison::Shipment _s;
    _s.ShipmentID = dbID ? dbID : sGarrisonMgr.GenerateShipmentDbId();
    _s.ShipmentRecID = shipmentID;
    _s.BuildingTypeID = shipmentConteinerEntry->BuildingType;
    _s.CreationTime = time_t(placeTime);
    _s.ShipmentDuration = int32(EndShipment) - int32(::time(nullptr));
    if (_s.ShipmentDuration < 0)
        _s.ShipmentDuration = 0;

    _shipments[shipmentConteinerEntry->BuildingType].push_back(_s);
    return _s.ShipmentID;
}

void Garrison::SendGarrisonShipmentLandingPage()
{
    WorldPackets::Garrison::GarrisonLandingPage packet;

    for (auto const& x : _shipments)
        for (auto const& shipment : x.second)
            packet.MsgData.push_back(shipment);

    _owner->SendDirectMessage(packet.Write());
}

void Garrison::CompleteShipments(GameObject* go)
{
    GarrisonWoDGameObject const* wod = sGarrisonMgr.GetWoDGameObject(go->GetEntry());
    CharShipmentConteiner const* shipmentConteinerEntry = wod ? sCharShipmentContainerStore.LookupEntry(wod->data[0]) : nullptr;
    if (!shipmentConteinerEntry)
        return;

    std::map<uint32, uint32> loot_items;
    for (auto const& sh : _shipments[shipmentConteinerEntry->BuildingType])
        if (!sh.ShipmentDuration)
        {
            if (CharShipmentEntry const* shipmentEntry = sCharShipmentStore.LookupEntry(sh.ShipmentRecID))
                ++loot_items[shipmentEntry->ShipmentResultItemID];
        }

    // This is hardcode of Player::SendLoot
    Loot* loot = &go->loot;

    // fill loot only once... after we should add only continue.
    if (loot->items.empty())
    {
        loot->clear();
        loot->AddLooter(_owner->GetGUID());
    }

    uint32 resources = 0;
    for (auto const& data : loot_items)
    {
        //HARDCORE.
        switch (data.first)
        {
            //Mine Shipment
            case 116055:
                AddOrReplaceItem(loot, 109119, data.second);
                AddOrReplaceItem(loot, 109118, data.second);
                break;
            //Garden Shipment
            case 116054:
                AddOrReplaceItem(loot, 109125, data.second);
                AddOrReplaceItem(loot, 109124, data.second);
                break;
            case 114677:
            case 118111:
                resources += data.second * 30;
                break;
            default:
                AddOrReplaceItem(loot, data.first, data.second);
                break;
        }
    }

    if (resources)
    {
        GarrisonCurrency::Modify(_owner, CURRENCY_TYPE_GARRISON_RESOURCES, int32(resources));
        if (loot->items.empty())
            FreeShipmentChest(shipmentConteinerEntry->BuildingType);
    }

    go->SetLootGenerationTime();
    go->SetLootState(GO_ACTIVATED, _owner);
    _owner->SendLoot(go->GetGUID(), LOOT_CORPSE);
}

void Garrison::FreeShipmentChest(uint32 shipmentConteinerBuildingType)
{
    ShipmentSet& set = _shipments[shipmentConteinerBuildingType];
    for (ShipmentSet::iterator itr = set.begin(); itr != set.end();)
    {
        if (!itr->ShipmentDuration)
            set.erase(itr++);
        else
            ++itr;
    }
}

uint32 Garrison::GetShipmentChestBuildingType(ObjectGuid const& guid) const
{
    for (auto const& data : ShipmentConteiners)
        if (data.second == guid)
            return data.first;
    return 0;
}

bool Garrison::HandleSpell(uint32 spellId, uint32 followerID)
{
    std::vector<GarrisonSpellEffect> const* effects = sGarrisonMgr.GetSpellEffects(spellId);
    if (!effects)
        return false;

    for (GarrisonSpellEffect const& effect : *effects)
    {
        switch (effect.Effect)
        {
            case SPELL_EFFECT_LEARN_GARRISON_BUILDING:
                LearnBlueprint(uint32(effect.MiscValue));
                break;
            case SPELL_EFFECT_CREATE_SHIPMENT:
                CreateGarrisonShipment(uint32(effect.MiscValue));
                break;
            case SPELL_EFFECT_UPGRADE_GARRISON:
                Upgrade();
                break;
            case SPELL_EFFECT_ADD_GARRISON_FOLLOWER:
                AddFollower(uint32(effect.MiscValue));
                break;
            case SPELL_EFFECT_ADD_GARRISON_MISSION:
                AddMission(uint32(effect.MiscValue));
                break;
            case SPELL_EFFECT_ACTIVATE_GARRISON_BUILDING:
                ActivateBuilding(uint32(effect.MiscValue));
                break;
            case SPELL_EFFECT_INCREASE_FOLLOWER_ITEM_LEVEL:
                if (Follower* follower = GetFollowerByID(followerID))
                    follower->IncreaseFollowerItemLevel(spellId, effect.BasePoints, effect.MiscValueB, _owner);
                break;
            case SPELL_EFFECT_RETRAIN_FOLLOWER:
                ReTrainFollower(effect.MiscValue, followerID);
                break;
            default:
                break;
        }
    }
    return true;
}

Garrison* GarrisonRegistry::Get(Player* player)
{
    return player ? Get(player->GetGUID().GetCounter()) : nullptr;
}

Garrison* GarrisonRegistry::Get(ObjectGuid::LowType guid)
{
    std::shared_lock<std::shared_mutex> lock(s_registryLock);
    auto itr = s_garrisons.find(guid);
    return itr != s_garrisons.end() ? itr->second.get() : nullptr;
}

void GarrisonRegistry::Load(Player* player)
{
    std::unique_ptr<Garrison> garrison = std::make_unique<Garrison>(player);
    if (!garrison->LoadFromDB())
        return;

    std::unique_lock<std::shared_mutex> lock(s_registryLock);
    s_garrisons[player->GetGUID().GetCounter()] = std::move(garrison);
}

void GarrisonRegistry::Unload(Player* player)
{
    std::unique_lock<std::shared_mutex> lock(s_registryLock);
    s_garrisons.erase(player->GetGUID().GetCounter());
    s_returnPoints.erase(player->GetGUID().GetCounter());
}

void GarrisonRegistry::Create(Player* player, uint32 garrSiteId, bool enter)
{
    std::unique_ptr<Garrison> garrison = std::make_unique<Garrison>(player);
    Garrison* raw = garrison.get();
    {
        std::unique_lock<std::shared_mutex> lock(s_registryLock);
        s_garrisons[player->GetGUID().GetCounter()] = std::move(garrison);
    }

    if (!raw->Create(garrSiteId, enter))
    {
        std::unique_lock<std::shared_mutex> lock(s_registryLock);
        s_garrisons.erase(player->GetGUID().GetCounter());
        return;
    }

    CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
    raw->SaveToDB(trans);
    CharacterDatabase.CommitTransaction(trans);
}

void GarrisonRegistry::Delete(Player* player)
{
    if (Garrison* garrison = Get(player))
    {
        garrison->Delete();
        std::unique_lock<std::shared_mutex> lock(s_registryLock);
        s_garrisons.erase(player->GetGUID().GetCounter());
    }
}

void GarrisonRegistry::ForEach(std::function<void(Garrison&)> const& fn)
{
    std::shared_lock<std::shared_mutex> lock(s_registryLock);
    for (auto& p : s_garrisons)
        fn(*p.second);
}

void GarrisonCurrency::Load(Player* player)
{
    std::unordered_map<uint32, uint32> counts;
    if (QueryResult result = CharacterDatabase.Query("SELECT currency, count FROM character_garrison_currency WHERE guid = {}", player->GetGUID().GetCounter()))
    {
        do
        {
            Field* fields = result->Fetch();
            counts[fields[0].Get<uint32>()] = fields[1].Get<uint32>();
        } while (result->NextRow());
    }

    std::lock_guard<std::mutex> lock(s_currencyLock);
    s_currencies[player->GetGUID().GetCounter()] = std::move(counts);
}

void GarrisonCurrency::Save(Player* player, CharacterDatabaseTransaction trans)
{
    std::lock_guard<std::mutex> lock(s_currencyLock);
    auto itr = s_currencies.find(player->GetGUID().GetCounter());
    if (itr == s_currencies.end())
        return;

    for (auto const& [currency, count] : itr->second)
        trans->Append("REPLACE INTO character_garrison_currency (guid, currency, count) VALUES ({}, {}, {})", player->GetGUID().GetCounter(), currency, count);
}

void GarrisonCurrency::Unload(Player* player)
{
    std::lock_guard<std::mutex> lock(s_currencyLock);
    s_currencies.erase(player->GetGUID().GetCounter());
}

uint32 GarrisonCurrency::Get(Player* player, uint32 currency)
{
    std::lock_guard<std::mutex> lock(s_currencyLock);
    auto itr = s_currencies.find(player->GetGUID().GetCounter());
    if (itr == s_currencies.end())
        return 0;
    auto c = itr->second.find(currency);
    return c != itr->second.end() ? c->second : 0;
}

bool GarrisonCurrency::Has(Player* player, uint32 currency, uint32 count)
{
    return Get(player, currency) >= count;
}

void GarrisonCurrency::Modify(Player* player, uint32 currency, int32 amount, bool printLog)
{
    if (!currency || !amount)
        return;

    uint32 newCount;
    {
        std::lock_guard<std::mutex> lock(s_currencyLock);
        uint32& count = s_currencies[player->GetGUID().GetCounter()][currency];
        int64 value = int64(count) + amount;
        count = uint32(std::max<int64>(0, value));
        newCount = count;
    }

    WorldPackets::Garrison::SetCurrency packet;
    packet.Type = currency;
    packet.Quantity = int32(newCount);
    packet.SuppressChatLog = !printLog;
    player->SendDirectMessage(packet.Write());
}

void GarrisonCurrency::Send(Player* player, uint32 currency)
{
    WorldPackets::Garrison::SetCurrency packet;
    packet.Type = currency;
    packet.Quantity = int32(Get(player, currency));
    packet.SuppressChatLog = true;
    player->SendDirectMessage(packet.Write());
}
