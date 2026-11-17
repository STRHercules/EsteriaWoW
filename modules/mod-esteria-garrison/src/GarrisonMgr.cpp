#include "GarrisonMgr.h"
#include "Containers.h"
#include "Creature.h"
#include "DatabaseEnv.h"
#include "Field.h"
#include "QueryResult.h"
#include "GameObject.h"
#include "Garrison.h"
#include "Log.h"
#include "ObjectMgr.h"
#include "Random.h"
#include "Timer.h"
#include "World.h"
#include <algorithm>
#include <iterator>
#include <limits>

uint32 GarrisonMgr::getFirstMap(uint32 map)
{
    switch (map)
    {
        case 1152:
        case 1330:
        case 1153:
            return 1152;
        case 1158:
        case 1331:
        case 1159:
            return 1158;
    }
    return 0;
}

void GarrisonMgr::Initialize()
{
    GarrisonDB2::Load();

    _garrisonPlotInstBySiteLevel.clear();
    _garrisonPlots.clear();
    _garrisonBuildingsByPlot.clear();
    _garrisonBuildingPlotInstances.clear();
    _garrisonBuildingsByType.clear();
    _garrisonFollowerAbilities[0].clear();
    _garrisonFollowerAbilities[1].clear();
    _garrisonFollowerRandomTraits.clear();

    for (GarrSiteLevelPlotInstEntry const* plotInstance : sGarrSiteLevelPlotInstStore)
        _garrisonPlotInstBySiteLevel[plotInstance->GarrSiteLevelID].push_back(plotInstance);

    for (GameObjectsEntry const* gameObject : sGameObjectsStore)
        if (gameObject->Type == GAMEOBJECT_TYPE_GARRISON_PLOT)
            _garrisonPlots[gameObject->MapID][gameObject->Data[0]] = gameObject;

    for (GarrPlotBuildingEntry const* plotBuilding : sGarrPlotBuildingStore)
        _garrisonBuildingsByPlot[plotBuilding->GarrPlotID].insert(plotBuilding->GarrBuildingID);

    for (GarrBuildingPlotInstEntry const* buildingPlotInst : sGarrBuildingPlotInstStore)
        _garrisonBuildingPlotInstances[uint64(buildingPlotInst->GarrBuildingID) | (uint64(buildingPlotInst->GarrSiteLevelPlotInstID) << 32)] = buildingPlotInst->ID;

    for (GarrBuildingEntry const* building : sGarrBuildingStore)
        _garrisonBuildingsByType[building->Type].push_back(building);

    for (GarrFollowerXAbilityEntry const* followerAbility : sGarrFollowerXAbilityStore)
    {
        if (!sGarrFollowerStore.LookupEntry(followerAbility->GarrFollowerID))
            continue;

        if (GarrAbilityEntry const* ability = sGarrAbilityStore.LookupEntry(followerAbility->GarrAbilityID))
        {
            if (!(ability->Flags & GARRISON_ABILITY_CANNOT_ROLL) && ability->Flags & GARRISON_ABILITY_FLAG_TRAIT)
                _garrisonFollowerRandomTraits.insert(ability);

            if (followerAbility->FactionIndex < 2)
            {
                if (ability->Flags & GARRISON_ABILITY_FLAG_TRAIT)
                    _garrisonFollowerAbilities[followerAbility->FactionIndex][followerAbility->GarrFollowerID].Traits.insert(ability);
                else
                    _garrisonFollowerAbilities[followerAbility->FactionIndex][followerAbility->GarrFollowerID].Counters.insert(ability);
            }
        }
    }

    InitializeDbIdSequences();
    LoadPlotFinalizeGOInfo();
    LoadFollowerClassSpecAbilities();
    LoadBuildingSpawnNPC();
    LoadBuildingSpawnGo();
    LoadMissionLine();
    LoadNpcFlags2();
    LoadWoDGameObjects();
    LoadShipment();
    LoadSpellEffects();
}

GarrSiteLevelEntry const* GarrisonMgr::GetGarrSiteLevelEntry(uint32 garrSiteId, uint32 level) const
{
    for (GarrSiteLevelEntry const* garrSiteLevel : sGarrSiteLevelStore)
        if (garrSiteLevel->SiteID == garrSiteId && garrSiteLevel->Level == level)
            return garrSiteLevel;

    return nullptr;
}

std::vector<GarrSiteLevelPlotInstEntry const*> const* GarrisonMgr::GetGarrPlotInstForSiteLevel(uint32 garrSiteLevelId) const
{
    auto itr = _garrisonPlotInstBySiteLevel.find(garrSiteLevelId);
    if (itr != _garrisonPlotInstBySiteLevel.end())
        return &itr->second;

    return nullptr;
}

GameObjectsEntry const* GarrisonMgr::GetPlotGameObject(uint32 mapId, uint32 garrPlotInstanceId) const
{
    auto mapItr = _garrisonPlots.find(mapId);
    if (mapItr != _garrisonPlots.end())
    {
        auto plotItr = mapItr->second.find(garrPlotInstanceId);
        if (plotItr != mapItr->second.end())
            return plotItr->second;
    }

    return nullptr;
}

bool GarrisonMgr::IsPlotMatchingBuilding(uint32 garrPlotId, uint32 garrBuildingId) const
{
    auto plotItr = _garrisonBuildingsByPlot.find(garrPlotId);
    if (plotItr != _garrisonBuildingsByPlot.end())
        return plotItr->second.count(garrBuildingId) > 0;

    return false;
}

uint32 GarrisonMgr::GetGarrBuildingPlotInst(uint32 garrBuildingId, uint32 garrSiteLevelPlotInstId) const
{
    auto itr = _garrisonBuildingPlotInstances.find(uint64(garrBuildingId) | (uint64(garrSiteLevelPlotInstId) << 32));
    if (itr != _garrisonBuildingPlotInstances.end())
        return itr->second;

    return 0;
}

GarrBuildingEntry const* GarrisonMgr::GetPreviousLevelBuilding(uint32 buildingType, uint32 currentLevel) const
{
    auto itr = _garrisonBuildingsByType.find(buildingType);
    if (itr != _garrisonBuildingsByType.end())
        for (GarrBuildingEntry const* building : itr->second)
            if (building->Level == currentLevel - 1)
                return building;

    return nullptr;
}

FinalizeGarrisonPlotGOInfo const* GarrisonMgr::GetPlotFinalizeGOInfo(uint32 garrPlotInstanceID) const
{
    auto itr = _finalizePlotGOInfo.find(garrPlotInstanceID);
    if (itr != _finalizePlotGOInfo.end())
        return &itr->second;

    return nullptr;
}

uint64 GarrisonMgr::GenerateFollowerDbId()
{
    if (_followerDbIdGenerator >= std::numeric_limits<uint64>::max())
    {
        LOG_ERROR("module", "Garrison follower db id overflow! Can't continue, shutting down server. ");
        World::StopNow(ERROR_EXIT_CODE);
    }

    return _followerDbIdGenerator++;
}

uint64 GarrisonMgr::GenerateMissionDbId()
{
    if (_missionDbIdGenerator >= std::numeric_limits<uint64>::max())
    {
        LOG_ERROR("module", "Garrison mission db id overflow! Can't continue, shutting down server. ");
        World::StopNow(ERROR_EXIT_CODE);
    }

    return _missionDbIdGenerator++;
}

uint64 GarrisonMgr::GenerateShipmentDbId()
{
    if (_shipmentDbIdGenerator >= std::numeric_limits<uint64>::max())
    {
        LOG_ERROR("module", "Garrison shipment db id overflow! Can't continue, shutting down server. ");
        World::StopNow(ERROR_EXIT_CODE);
    }

    return _shipmentDbIdGenerator++;
}

uint32 const AbilitiesForQuality[][2] =
{
    // Counters, Traits
    {0, 0},
    {1, 0},
    {1, 1},   // Uncommon
    {1, 2},   // Rare
    {2, 3},   // Epic
    {2, 3}    // Legendary
};

std::list<GarrAbilityEntry const*> GarrisonMgr::RollFollowerAbilities(GarrFollowerEntry const* follower, uint32 quality, uint32 faction, bool initial) const
{
    ASSERT(faction < 2);

    bool hasForcedExclusiveTrait = false;
    std::list<GarrAbilityEntry const*> result;
    int32 slots[2] = { int32(AbilitiesForQuality[quality][0]), int32(AbilitiesForQuality[quality][1]) };

    GarrAbilities const* abilities = nullptr;
    auto itr = _garrisonFollowerAbilities[faction].find(follower->ID);
    if (itr != _garrisonFollowerAbilities[faction].end())
        abilities = &itr->second;

    std::list<GarrAbilityEntry const*> abilityList, forcedAbilities, traitList, forcedTraits;
    if (abilities)
    {
        for (GarrAbilityEntry const* ability : abilities->Counters)
        {
            if (ability->Flags & GARRISON_ABILITY_HORDE_ONLY && faction != GARRISON_FACTION_INDEX_HORDE)
                continue;
            else if (ability->Flags & GARRISON_ABILITY_ALLIANCE_ONLY && faction != GARRISON_FACTION_INDEX_ALLIANCE)
                continue;

            if (ability->Flags & GARRISON_ABILITY_FLAG_CANNOT_REMOVE)
                forcedAbilities.push_back(ability);
            else
                abilityList.push_back(ability);
        }

        for (GarrAbilityEntry const* ability : abilities->Traits)
        {
            if (ability->Flags & GARRISON_ABILITY_HORDE_ONLY && faction != GARRISON_FACTION_INDEX_HORDE)
                continue;
            else if (ability->Flags & GARRISON_ABILITY_ALLIANCE_ONLY && faction != GARRISON_FACTION_INDEX_ALLIANCE)
                continue;

            if (ability->Flags & GARRISON_ABILITY_FLAG_CANNOT_REMOVE)
                forcedTraits.push_back(ability);
            else
                traitList.push_back(ability);
        }
    }

    Acore::Containers::RandomResize(abilityList, std::max<int32>(0, slots[0] - int32(forcedAbilities.size())));
    Acore::Containers::RandomResize(traitList, std::max<int32>(0, slots[1] - int32(forcedTraits.size())));

    // Add abilities specified in GarrFollowerXAbility.db2 before generic classspec ones on follower creation
    if (initial)
    {
        forcedAbilities.splice(forcedAbilities.end(), abilityList);
        forcedTraits.splice(forcedTraits.end(), traitList);
    }

    forcedAbilities.sort();
    abilityList.sort();
    forcedTraits.sort();
    traitList.sort();

    // check if we have a trait from exclusive category
    for (GarrAbilityEntry const* ability : forcedTraits)
    {
        if (ability->Flags & GARRISON_ABILITY_FLAG_EXCLUSIVE)
        {
            hasForcedExclusiveTrait = true;
            break;
        }
    }

    if (size_t(slots[0]) > forcedAbilities.size() + abilityList.size())
    {
        std::list<GarrAbilityEntry const*> classSpecAbilities = GetClassSpecAbilities(follower, faction);
        std::list<GarrAbilityEntry const*> classSpecAbilitiesTemp, classSpecAbilitiesTemp2;
        classSpecAbilitiesTemp2.swap(abilityList);
        std::set_difference(classSpecAbilities.begin(), classSpecAbilities.end(), forcedAbilities.begin(), forcedAbilities.end(), std::back_inserter(classSpecAbilitiesTemp));
        std::set_union(classSpecAbilitiesTemp.begin(), classSpecAbilitiesTemp.end(), classSpecAbilitiesTemp2.begin(), classSpecAbilitiesTemp2.end(), std::back_inserter(abilityList));

        Acore::Containers::RandomResize(abilityList, std::max<int32>(0, slots[0] - int32(forcedAbilities.size())));
    }

    if (size_t(slots[1]) > forcedTraits.size() + traitList.size())
    {
        std::list<GarrAbilityEntry const*> genericTraits, genericTraitsTemp;
        for (GarrAbilityEntry const* ability : _garrisonFollowerRandomTraits)
        {
            if (ability->Flags & GARRISON_ABILITY_HORDE_ONLY && faction != GARRISON_FACTION_INDEX_HORDE)
                continue;
            else if (ability->Flags & GARRISON_ABILITY_ALLIANCE_ONLY && faction != GARRISON_FACTION_INDEX_ALLIANCE)
                continue;

            // forced exclusive trait exists, skip other ones entirely
            if (hasForcedExclusiveTrait && ability->Flags & GARRISON_ABILITY_FLAG_EXCLUSIVE)
                continue;

            genericTraitsTemp.push_back(ability);
        }

        std::set_difference(genericTraitsTemp.begin(), genericTraitsTemp.end(), forcedTraits.begin(), forcedTraits.end(), std::back_inserter(genericTraits));
        genericTraits.splice(genericTraits.begin(), traitList);
        // "split" the list into two parts [nonexclusive, exclusive] to make selection later easier
        genericTraits.sort([](GarrAbilityEntry const* a1, GarrAbilityEntry const* a2)
        {
            uint32 e1 = a1->Flags & GARRISON_ABILITY_FLAG_EXCLUSIVE;
            uint32 e2 = a2->Flags & GARRISON_ABILITY_FLAG_EXCLUSIVE;
            if (e1 != e2)
                return e1 < e2;

            return a1->ID < a2->ID;
        });
        genericTraits.unique();

        size_t firstExclusive = 0, total = genericTraits.size();
        for (auto gitr = genericTraits.begin(); gitr != genericTraits.end(); ++gitr, ++firstExclusive)
            if ((*gitr)->Flags & GARRISON_ABILITY_FLAG_EXCLUSIVE)
                break;

        while (int32(traitList.size()) < std::max<int32>(0, slots[1] - int32(forcedTraits.size())) && total)
        {
            auto gitr = genericTraits.begin();
            std::advance(gitr, urand(0, uint32(total-- - 1)));
            if ((*gitr)->Flags & GARRISON_ABILITY_FLAG_EXCLUSIVE)
                total = firstExclusive; // selected exclusive trait - no other can be selected now
            else
                --firstExclusive;

            traitList.push_back(*gitr);
            genericTraits.erase(gitr);
        }
    }

    result.splice(result.end(), forcedAbilities);
    result.splice(result.end(), abilityList);
    result.splice(result.end(), forcedTraits);
    result.splice(result.end(), traitList);

    return result;
}

std::list<GarrAbilityEntry const*> GarrisonMgr::GetClassSpecAbilities(GarrFollowerEntry const* follower, uint32 faction) const
{
    std::list<GarrAbilityEntry const*> abilities;
    uint32 classSpecId;
    switch (faction)
    {
        case GARRISON_FACTION_INDEX_HORDE:
            classSpecId = follower->HordeGarrClassSpecID;
            break;
        case GARRISON_FACTION_INDEX_ALLIANCE:
            classSpecId = follower->AllianceGarrClassSpecID;
            break;
        default:
            return abilities;
    }

    if (!sGarrClassSpecStore.LookupEntry(classSpecId))
        return abilities;

    auto itr = _garrisonFollowerClassSpecAbilities.find(classSpecId);
    if (itr != _garrisonFollowerClassSpecAbilities.end())
        abilities = itr->second;

    return abilities;
}

void GarrisonMgr::InitializeDbIdSequences()
{
    if (QueryResult result = CharacterDatabase.Query("SELECT MAX(dbId) FROM character_garrison_followers"))
        _followerDbIdGenerator = (*result)[0].Get<uint64>() + 1;

    if (QueryResult result = CharacterDatabase.Query("SELECT MAX(dbId) FROM character_garrison_missions"))
        _missionDbIdGenerator = (*result)[0].Get<uint64>() + 1;

    if (QueryResult result = CharacterDatabase.Query("SELECT MAX(dbId) FROM character_garrison_shipment"))
        _shipmentDbIdGenerator = (*result)[0].Get<uint64>() + 1;
}

void GarrisonMgr::LoadPlotFinalizeGOInfo()
{
    _finalizePlotGOInfo.clear();
    //                                                0                   1                  2       3       4       5
    QueryResult result = WorldDatabase.Query("SELECT garrPlotInstanceId, hordeGameObjectId, hordeX, hordeY, hordeZ, hordeO, "
    //                      6                     7          8          9          10
        "allianceGameObjectId, allianceX, allianceY, allianceZ, allianceO FROM garrison_plot_finalize_info");
    if (!result)
    {
        LOG_INFO("server.loading", ">> Loaded 0 garrison plot finalize entries. DB table `garrison_plot_finalize_info` is empty.");
        return;
    }

    uint32 msTime = getMSTime();
    do
    {
        Field* fields = result->Fetch();
        uint32 garrPlotInstanceId = fields[0].Get<uint32>();
        uint32 hordeGameObjectId = fields[1].Get<uint32>();
        uint32 allianceGameObjectId = fields[6].Get<uint32>();

        if (!sGarrPlotInstanceStore.LookupEntry(garrPlotInstanceId))
        {
            LOG_ERROR("sql.sql", "Non-existing GarrPlotInstance.db2 entry {} was referenced in `garrison_plot_finalize_info`.", garrPlotInstanceId);
            continue;
        }

        GameObjectTemplate const* goTemplate = sObjectMgr->GetGameObjectTemplate(hordeGameObjectId);
        if (!goTemplate)
        {
            LOG_ERROR("sql.sql", "Non-existing gameobject_template entry {} was referenced in `garrison_plot_finalize_info`.`hordeGameObjectId` for garrPlotInstanceId {}.",
                hordeGameObjectId, garrPlotInstanceId);
            continue;
        }

        if (goTemplate->type != GAMEOBJECT_TYPE_GOOBER)
        {
            LOG_ERROR("sql.sql", "Invalid gameobject type {} (entry {}) was referenced in `garrison_plot_finalize_info`.`hordeGameObjectId` for garrPlotInstanceId {}.",
                goTemplate->type, hordeGameObjectId, garrPlotInstanceId);
            continue;
        }

        goTemplate = sObjectMgr->GetGameObjectTemplate(allianceGameObjectId);
        if (!goTemplate)
        {
            LOG_ERROR("sql.sql", "Non-existing gameobject_template entry {} was referenced in `garrison_plot_finalize_info`.`allianceGameObjectId` for garrPlotInstanceId {}.",
                allianceGameObjectId, garrPlotInstanceId);
            continue;
        }

        if (goTemplate->type != GAMEOBJECT_TYPE_GOOBER)
        {
            LOG_ERROR("sql.sql", "Invalid gameobject type {} (entry {}) was referenced in `garrison_plot_finalize_info`.`allianceGameObjectId` for garrPlotInstanceId {}.",
                goTemplate->type, allianceGameObjectId, garrPlotInstanceId);
            continue;
        }

        FinalizeGarrisonPlotGOInfo& info = _finalizePlotGOInfo[garrPlotInstanceId];
        info.FactionInfo[GARRISON_FACTION_INDEX_HORDE].GameObjectId = hordeGameObjectId;
        info.FactionInfo[GARRISON_FACTION_INDEX_HORDE].Pos.Relocate(fields[2].Get<float>(), fields[3].Get<float>(), fields[4].Get<float>(), fields[5].Get<float>());

        info.FactionInfo[GARRISON_FACTION_INDEX_ALLIANCE].GameObjectId = allianceGameObjectId;
        info.FactionInfo[GARRISON_FACTION_INDEX_ALLIANCE].Pos.Relocate(fields[7].Get<float>(), fields[8].Get<float>(), fields[9].Get<float>(), fields[10].Get<float>());
    }
    while (result->NextRow());

    LOG_INFO("server.loading", ">> Loaded {} garrison plot finalize entries in {} ms.", uint32(_finalizePlotGOInfo.size()), GetMSTimeDiffToNow(msTime));
}

void GarrisonMgr::LoadFollowerClassSpecAbilities()
{
    _garrisonFollowerClassSpecAbilities.clear();
    QueryResult result = WorldDatabase.Query("SELECT classSpecId, abilityId FROM garrison_follower_class_spec_abilities");
    if (!result)
    {
        LOG_INFO("server.loading", ">> Loaded 0 garrison follower class spec abilities. DB table `garrison_follower_class_spec_abilities` is empty.");
        return;
    }

    uint32 msTime = getMSTime();
    uint32 count = 0;
    do
    {
        Field* fields = result->Fetch();
        uint32 classSpecId = fields[0].Get<uint32>();
        uint32 abilityId = fields[1].Get<uint32>();

        if (!sGarrClassSpecStore.LookupEntry(classSpecId))
        {
            LOG_ERROR("sql.sql", "Non-existing GarrClassSpec.db2 entry {} was referenced in `garrison_follower_class_spec_abilities` by row ({}, {}).", classSpecId, classSpecId, abilityId);
            continue;
        }

        GarrAbilityEntry const* ability = sGarrAbilityStore.LookupEntry(abilityId);
        if (!ability)
        {
            LOG_ERROR("sql.sql", "Non-existing GarrAbility.db2 entry {} was referenced in `garrison_follower_class_spec_abilities` by row ({}, {}).", abilityId, classSpecId, abilityId);
            continue;
        }

        _garrisonFollowerClassSpecAbilities[classSpecId].push_back(ability);
        ++count;
    }
    while (result->NextRow());

    for (auto& pair : _garrisonFollowerClassSpecAbilities)
        pair.second.sort();

    LOG_INFO("server.loading", ">> Loaded {} garrison follower class spec abilities in {} ms.", count, GetMSTimeDiffToNow(msTime));
}

void GarrisonMgr::LoadBuildingSpawnNPC()
{
    _buildSpawnNpc.clear();
    //                                                0       1        2   3    4           5           6           7            8
    QueryResult result = WorldDatabase.Query("SELECT plotID, BuildID, id, map, position_x, position_y, position_z, orientation, building FROM garrison_building_creature");

    if (!result)
    {
        LOG_INFO("server.loading", ">> Loaded 0 garrison building creatures. DB table `garrison_building_creature` is empty.");
        return;
    }

    uint32 msTime = getMSTime();
    uint32 count = 0;
    do
    {
        uint8 index = 0;
        Field* fields = result->Fetch();

        uint32 garrPlotInstanceId = fields[index++].Get<uint32>();
        uint32 BuildID = fields[index++].Get<uint32>();
        uint32 entry = fields[index++].Get<uint32>();

        if (!sObjectMgr->GetCreatureTemplate(entry))
        {
            LOG_ERROR("sql.sql", "Table `garrison_building_creature` has creature with non existing creature entry {}, skipped.", entry);
            continue;
        }

        if (!sGarrPlotInstanceStore.LookupEntry(garrPlotInstanceId))
        {
            LOG_ERROR("sql.sql", "Non-existing GarrPlotInstance.db2 entry {} was referenced in `garrison_building_creature`.", garrPlotInstanceId);
            continue;
        }

        //! BuildID = 0 - empty build spawn.
        if (BuildID && !sGarrBuildingStore.LookupEntry(BuildID))
        {
            LOG_ERROR("sql.sql", "Non-existing GarrBuilding.db2 entry {} was referenced in `garrison_building_creature`.", BuildID);
            continue;
        }

        GarrisonBuildingSpawn data;
        data.id = entry;
        uint32 map = fields[index++].Get<uint32>();
        data.mapid = getFirstMap(map);
        data.posX = fields[index++].Get<float>();
        data.posY = fields[index++].Get<float>();
        data.posZ = fields[index++].Get<float>();
        data.orientation = fields[index++].Get<float>();
        data.building = fields[index++].Get<bool>();
        _buildSpawnNpc[BuildID][garrPlotInstanceId].push_back(data);

        if (!data.mapid)
            LOG_ERROR("sql.sql", "Not supported map {} in `garrison_building_creature`.", map);

        ++count;
    } while (result->NextRow());

    LOG_INFO("server.loading", ">> Loaded {} garrison building creatures in {} ms.", count, GetMSTimeDiffToNow(msTime));
}

void GarrisonMgr::LoadBuildingSpawnGo()
{
    _buildSpawnGo.clear();
    //                                                0       1        2   3    4           5           6           7            8          9          10         11         12
    QueryResult result = WorldDatabase.Query("SELECT plotID, BuildID, id, map, position_x, position_y, position_z, orientation, rotation0, rotation1, rotation2, rotation3, building FROM garrison_building_gameobject");

    if (!result)
    {
        LOG_INFO("server.loading", ">> Loaded 0 garrison building go. DB table `garrison_building_gameobject` is empty.");
        return;
    }

    uint32 msTime = getMSTime();
    uint32 count = 0;
    do
    {
        uint8 index = 0;
        Field* fields = result->Fetch();

        uint32 garrPlotInstanceId = fields[index++].Get<uint32>();
        uint32 BuildID = fields[index++].Get<uint32>();
        uint32 entry = fields[index++].Get<uint32>();
        if (!sObjectMgr->GetGameObjectTemplate(entry))
        {
            LOG_ERROR("sql.sql", "Table `garrison_building_gameobject` has go with non existing go entry {}, skipped.", entry);
            continue;
        }

        uint32 wodType = GetWoDGameObjectType(entry);
        if (wodType == GAMEOBJECT_TYPE_GARRISON_BUILDING || wodType == GAMEOBJECT_TYPE_GARRISON_PLOT)
        {
            if (entry != 239085)
            {
                LOG_ERROR("sql.sql", "Table `garrison_building_gameobject` has go ({}) with no allowed type {}, skipped.", entry, wodType);
                continue;
            }
        }

        if (!sGarrPlotInstanceStore.LookupEntry(garrPlotInstanceId))
        {
            LOG_ERROR("sql.sql", "Non-existing GarrPlotInstance.db2 entry {} was referenced in `garrison_building_gameobject`.", garrPlotInstanceId);
            continue;
        }

        //! BuildID = 0 - empty build spawn.
        if (BuildID && !sGarrBuildingStore.LookupEntry(BuildID))
        {
            LOG_ERROR("sql.sql", "Non-existing GarrBuilding.db2 entry {} was referenced in `garrison_building_gameobject`.", BuildID);
            continue;
        }

        GarrisonBuildingSpawn data;
        data.id = entry;
        uint32 map = fields[index++].Get<uint32>();
        data.mapid = getFirstMap(map);
        data.posX = fields[index++].Get<float>();
        data.posY = fields[index++].Get<float>();
        data.posZ = fields[index++].Get<float>();
        data.orientation = fields[index++].Get<float>();
        data.rotation0 = fields[index++].Get<float>();
        data.rotation1 = fields[index++].Get<float>();
        data.rotation2 = fields[index++].Get<float>();
        data.rotation3 = fields[index++].Get<float>();
        data.building = fields[index++].Get<bool>();
        _buildSpawnGo[BuildID][garrPlotInstanceId].push_back(data);

        if (!data.mapid)
            LOG_ERROR("sql.sql", "Not supported map {} in `garrison_building_gameobject`.", map);

        ++count;
    } while (result->NextRow());

    LOG_INFO("server.loading", ">> Loaded {} garrison building go in {} ms.", count, GetMSTimeDiffToNow(msTime));
}

void GarrisonMgr::LoadMissionLine()
{
    _MissionLineStore.clear();
    _nextMission.clear();
    _nextMissionByFollower.clear();
    //                                                0   1            2                  3
    QueryResult result = WorldDatabase.Query("SELECT ID, NextMission, ReqGarrFollowerID, IsRandom FROM garrison_mission_line");

    if (!result)
    {
        LOG_INFO("server.loading", ">> Loaded 0 garrison mission lines. DB table `garrison_mission_line` is empty.");
        return;
    }

    uint32 msTime = getMSTime();
    uint32 count = 0;
    do
    {
        uint8 index = 0;
        Field* fields = result->Fetch();

        uint32 missionID = fields[index++].Get<uint32>();
        uint32 NextMission = fields[index++].Get<uint32>();
        uint32 ReqGarrFollowerID = fields[index++].Get<uint32>();
        bool IsRandom = fields[index++].Get<bool>();

        GarrMissionEntry const* missionEntry = sGarrMissionStore.LookupEntry(missionID);
        if (!missionEntry)
        {
            LOG_ERROR("sql.sql", "Non-existing sGarrMissionStore missionID {} was referenced in `garrison_mission_line`.", missionID);
            continue;
        }

        GarrMissionEntry const* NextMissionEntry = sGarrMissionStore.LookupEntry(NextMission);

        if (NextMission && !NextMissionEntry)
        {
            LOG_ERROR("sql.sql", "Non-existing sGarrMissionStore missionID {} was referenced in `garrison_mission_line`.", NextMission);
            continue;
        }

        GarrFollowerEntry const* followerEntry = sGarrFollowerStore.LookupEntry(ReqGarrFollowerID);
        if (ReqGarrFollowerID && !followerEntry)
        {
            LOG_ERROR("sql.sql", "Non-existing sGarrFollowerStore ReqGarrFollowerID {} was referenced in `garrison_mission_line`.", ReqGarrFollowerID);
            continue;
        }

        GarrMissionLine& data = _MissionLineStore[missionID];
        data.MissionID = missionEntry;
        data.NextMission = NextMissionEntry;
        data.Reqfollower = followerEntry;
        data.isRandom = IsRandom;

        if (NextMissionEntry)
            _nextMission[missionID] = NextMissionEntry;

        if (followerEntry)
            _nextMissionByFollower[ReqGarrFollowerID] = missionEntry;

        ++count;
    } while (result->NextRow());

    LOG_INFO("server.loading", ">> Loaded {} garrison mission lines in {} ms.", count, GetMSTimeDiffToNow(msTime));
}

void GarrisonMgr::LoadShipment()
{
    shipment.clear();
    //                                                0       1            2         3
    QueryResult result = WorldDatabase.Query("SELECT SiteID, ContainerID, NpcEntry, ShipmentID FROM garrison_shipment");

    if (!result)
    {
        LOG_INFO("server.loading", ">> Loaded 0 garrison shipment. DB table `garrison_shipment` is empty.");
        return;
    }

    uint32 msTime = getMSTime();
    uint32 count = 0;
    do
    {
        uint8 index = 0;
        Field* fields = result->Fetch();

        GarrShipment data;
        data.SiteID = fields[index++].Get<uint32>();
        data.ContainerID = fields[index++].Get<uint32>();
        data.NpcEntry = fields[index++].Get<uint32>();
        data.ShipmentID = fields[index++].Get<uint32>();

        if (data.SiteID && data.SiteID != SITE_ID_GARRISON_ALLIANCE && data.SiteID != SITE_ID_GARRISON_HORDE)
        {
            LOG_ERROR("sql.sql", "Table `garrison_shipment` has non-existen SiteID {}, skipped.", data.SiteID);
            continue;
        }

        CreatureTemplate const* cInfo = sObjectMgr->GetCreatureTemplate(data.NpcEntry);
        if (!cInfo)
        {
            LOG_ERROR("sql.sql", "Table `garrison_shipment` has creature with non existing creature entry {}, skipped.", data.NpcEntry);
            continue;
        }

        CharShipmentEntry const* shipmentEntry = sCharShipmentStore.LookupEntry(data.ShipmentID);
        if (!shipmentEntry)
        {
            LOG_ERROR("sql.sql", "Non-existing CharShipment.db2 entry {} was referenced in `garrison_shipment`.", data.ShipmentID);
            continue;
        }

        CharShipmentConteiner const* shipmentConteinerEntry = sCharShipmentContainerStore.LookupEntry(data.ContainerID);
        if (!shipmentConteinerEntry)
        {
            LOG_ERROR("sql.sql", "Non-existing CharShipmentContainer.db2 entry {} was referenced in `garrison_shipment`.", data.ContainerID);
            continue;
        }
        data.cEntry = shipmentConteinerEntry;
        data.data = shipmentEntry;

        _npcFlags2[data.NpcEntry] |= UNIT_NPC_FLAG2_SHIPMENT_ORDER;
        const_cast<CreatureTemplate*>(cInfo)->npcflag |= UNIT_NPC_FLAG_GOSSIP;
        const_cast<CreatureTemplate*>(cInfo)->IconName = "workorders";

        shipment[SHIPMENT_GET_BY_NPC].insert(shipmentStoreMap::value_type(data.NpcEntry, data));
        shipment[SHIPMENT_GET_BY_CONTEINER_ID].insert(shipmentStoreMap::value_type(data.ContainerID, data));

        ++count;
    } while (result->NextRow());

    LOG_INFO("server.loading", ">> Loaded {} garrison_shipment in {} ms.", count, GetMSTimeDiffToNow(msTime));
}

void GarrisonMgr::LoadNpcFlags2()
{
    _npcFlags2.clear();
    if (QueryResult result = WorldDatabase.Query("SELECT entry, npcflag2 FROM garrison_creature_npcflag2"))
    {
        do
        {
            Field* fields = result->Fetch();
            uint32 entry = fields[0].Get<uint32>();
            _npcFlags2[entry] = fields[1].Get<uint32>();
            // 6.x opened the architect / mission table / work order windows from npcflag2 alone; here the hello goes through gossip
            if (CreatureTemplate const* cInfo = sObjectMgr->GetCreatureTemplate(entry))
                const_cast<CreatureTemplate*>(cInfo)->npcflag |= UNIT_NPC_FLAG_GOSSIP;
        } while (result->NextRow());
    }
    LOG_INFO("server.loading", ">> Loaded {} garrison creature npcflag2 rows.", uint32(_npcFlags2.size()));
}

void GarrisonMgr::LoadWoDGameObjects()
{
    _wodGameObjects.clear();
    if (QueryResult result = WorldDatabase.Query("SELECT entry, type, Data0, Data1, Data2, Data3 FROM garrison_gameobject_wod_type"))
    {
        do
        {
            Field* fields = result->Fetch();
            GarrisonWoDGameObject& go = _wodGameObjects[fields[0].Get<uint32>()];
            go.type = fields[1].Get<uint32>();
            for (uint8 i = 0; i < 4; ++i)
                go.data[i] = fields[2 + i].Get<uint32>();
        } while (result->NextRow());
    }
    LOG_INFO("server.loading", ">> Loaded {} garrison WoD gameobject types.", uint32(_wodGameObjects.size()));
}

void GarrisonMgr::LoadSpellEffects()
{
    _spellEffects.clear();
    _itemSpells.clear();
    if (QueryResult result = WorldDatabase.Query("SELECT spell_id, effect_index, effect, effect_base_points_f, effect_misc_value_0, effect_misc_value_1 FROM db2_spell_effect"))
    {
        do
        {
            Field* fields = result->Fetch();
            GarrisonSpellEffect effect;
            effect.SpellID = fields[0].Get<uint32>();
            effect.EffectIndex = fields[1].Get<uint32>();
            effect.Effect = fields[2].Get<uint32>();
            effect.BasePoints = int32(fields[3].Get<float>());
            effect.MiscValue = fields[4].Get<int32>();
            effect.MiscValueB = fields[5].Get<int32>();
            _spellEffects[effect.SpellID].push_back(effect);
        } while (result->NextRow());
    }

    if (QueryResult result = WorldDatabase.Query("SELECT DISTINCT parent_item_id, spell_id FROM db2_item_effect"))
    {
        do
        {
            Field* fields = result->Fetch();
            _itemSpells[fields[0].Get<uint32>()].push_back(fields[1].Get<uint32>());
        } while (result->NextRow());
    }

    LOG_INFO("server.loading", ">> Loaded {} garrison spells, {} garrison items.", uint32(_spellEffects.size()), uint32(_itemSpells.size()));
}

GarrShipment const* GarrisonMgr::GetGarrShipment(uint32 entry, ShipmentGetType type) const
{
    auto i = shipment.find(type);
    if (i == shipment.end())
        return nullptr;

    auto itr = i->second.find(entry);
    if (itr == i->second.end())
        return nullptr;

    return &itr->second;
}

GarrMissionEntry const* GarrisonMgr::GetNextMissionInQuestLine(uint32 missionID)
{
    auto data = _nextMission.find(missionID);
    if (data != _nextMission.end())
        return data->second;
    return nullptr;
}

GarrMissionEntry const* GarrisonMgr::GetMissionAtFollowerTaking(uint32 followerID)
{
    auto data = _nextMissionByFollower.find(followerID);
    if (data != _nextMissionByFollower.end())
        return data->second;
    return nullptr;
}

std::vector<uint32> GarrisonMgr::GetRandomMissionIDs() const
{
    std::vector<uint32> ids;
    for (auto const& line : _MissionLineStore)
        if (line.second.isRandom && line.second.MissionID && line.second.MissionID->OfferDuration > 0
            && line.second.MissionID->GarrFollowerTypeID == 1)
            ids.push_back(line.second.MissionID->ID);
    return ids;
}

std::list<GarrisonBuildingSpawn> const* GarrisonMgr::GetGoSpawnBuilding(uint32 plotID, uint32 build) const
{
    auto b = _buildSpawnGo.find(build);
    if (b != _buildSpawnGo.end())
    {
        auto p = b->second.find(plotID);
        if (p != b->second.end())
            return &p->second;
    }
    return nullptr;
}

std::list<GarrisonBuildingSpawn> const* GarrisonMgr::GetNpcSpawnBuilding(uint32 plotID, uint32 build) const
{
    auto b = _buildSpawnNpc.find(build);
    if (b != _buildSpawnNpc.end())
    {
        auto p = b->second.find(plotID);
        if (p != b->second.end())
            return &p->second;
    }
    return nullptr;
}

uint32 GarrisonMgr::GetNpcFlags2(uint32 creatureEntry) const
{
    auto itr = _npcFlags2.find(creatureEntry);
    return itr != _npcFlags2.end() ? itr->second : 0;
}

GarrisonWoDGameObject const* GarrisonMgr::GetWoDGameObject(uint32 goEntry) const
{
    auto itr = _wodGameObjects.find(goEntry);
    return itr != _wodGameObjects.end() ? &itr->second : nullptr;
}

uint32 GarrisonMgr::GetWoDGameObjectType(uint32 goEntry) const
{
    if (GarrisonWoDGameObject const* go = GetWoDGameObject(goEntry))
        return go->type;
    if (GameObjectTemplate const* goInfo = sObjectMgr->GetGameObjectTemplate(goEntry))
        return goInfo->type;
    return 0;
}

std::vector<GarrisonSpellEffect> const* GarrisonMgr::GetSpellEffects(uint32 spellId) const
{
    auto itr = _spellEffects.find(spellId);
    return itr != _spellEffects.end() ? &itr->second : nullptr;
}

GarrisonSpellEffect const* GarrisonMgr::GetSpellEffect(uint32 spellId, uint32 effect) const
{
    if (std::vector<GarrisonSpellEffect> const* effects = GetSpellEffects(spellId))
        for (GarrisonSpellEffect const& e : *effects)
            if (e.Effect == effect)
                return &e;
    return nullptr;
}

std::vector<uint32> const* GarrisonMgr::GetItemSpells(uint32 itemId) const
{
    auto itr = _itemSpells.find(itemId);
    return itr != _itemSpells.end() ? &itr->second : nullptr;
}
