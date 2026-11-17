#include "GarrisonDB2.h"
#include "DatabaseEnv.h"
#include "Field.h"
#include "QueryResult.h"
#include "Log.h"
#include "Timer.h"

GarrDB2Storage<CharShipmentEntry>          sCharShipmentStore;
GarrDB2Storage<CharShipmentConteiner>      sCharShipmentContainerStore;
GarrDB2Storage<GarrAbilityEntry>           sGarrAbilityStore;
GarrDB2Storage<GarrBuildingEntry>          sGarrBuildingStore;
GarrDB2Storage<GarrBuildingPlotInstEntry>  sGarrBuildingPlotInstStore;
GarrDB2Storage<GarrClassSpecEntry>         sGarrClassSpecStore;
GarrDB2Storage<GarrFollowerEntry>          sGarrFollowerStore;
GarrDB2Storage<GarrFollowerLevelXPEntry>   sGarrFollowerLevelXPStore;
GarrDB2Storage<GarrFollowerQualityEntry>   sGarrFollowerQualityStore;
GarrDB2Storage<GarrFollowerXAbilityEntry>  sGarrFollowerXAbilityStore;
GarrDB2Storage<GarrMissionEntry>           sGarrMissionStore;
GarrDB2Storage<GarrPlotEntry>              sGarrPlotStore;
GarrDB2Storage<GarrPlotBuildingEntry>      sGarrPlotBuildingStore;
GarrDB2Storage<GarrPlotInstanceEntry>      sGarrPlotInstanceStore;
GarrDB2Storage<GarrSiteLevelEntry>         sGarrSiteLevelStore;
GarrDB2Storage<GarrSiteLevelPlotInstEntry> sGarrSiteLevelPlotInstStore;
GarrDB2Storage<GameObjectsEntry>           sGameObjectsStore;

namespace
{
    template<class T, class F>
    void LoadTable(GarrDB2Storage<T>& store, char const* query, F&& fill)
    {
        store.Clear();
        if (QueryResult result = WorldDatabase.Query(query))
        {
            do
            {
                Field* f = result->Fetch();
                T& entry = store.Add(f[0].Get<uint32>());
                fill(entry, f);
            } while (result->NextRow());
        }
    }

    std::string Str(Field const& f) { return f.IsNull() ? std::string() : f.Get<std::string>(); }
}

void GarrisonDB2::Load()
{
    uint32 oldMSTime = getMSTime();

    LoadTable(sCharShipmentStore,
        "SELECT id, container_id, flags, duration, spell_id, dummy_item_id, max_shipments, garr_follower_id FROM db2_char_shipment",
        [](CharShipmentEntry& e, Field* f)
        {
            e.ID = f[0].Get<uint32>(); e.ShipmentConteinerID = f[1].Get<uint32>(); e.Flags = f[2].Get<uint32>();
            e.TimeForShipment = f[3].Get<uint32>(); e.SpellCreation = f[4].Get<uint32>(); e.ShipmentResultItemID = f[5].Get<uint32>();
            e.MaxShipments = f[6].Get<uint32>(); e.GarrFollowerID = f[7].Get<uint32>();
        });

    LoadTable(sCharShipmentContainerStore,
        "SELECT id, description, pending_text, ui_texture_kit_id, garr_type_id, garr_building_type, base_capacity, faction FROM db2_char_shipment_container",
        [](CharShipmentConteiner& e, Field* f)
        {
            e.ID = f[0].Get<uint32>(); e.Description = Str(f[1]); e.PendingText = Str(f[2]); e.UiTextureKitID = f[3].Get<uint32>();
            e.GarrTypeID = f[4].Get<uint32>(); e.BuildingType = f[5].Get<uint32>(); e.BaseCapacity = f[6].Get<uint32>();
            e.Faction = f[7].Get<uint32>();
        });

    LoadTable(sGarrAbilityStore,
        "SELECT id, flags, name, description, icon_file_data_id, faction_change_garr_ability_id, garr_ability_category_id, garr_follower_type_id FROM db2_garr_ability",
        [](GarrAbilityEntry& e, Field* f)
        {
            e.ID = f[0].Get<uint32>(); e.Flags = f[1].Get<uint32>(); e.Name = Str(f[2]); e.Description = Str(f[3]);
            e.IconFileDataID = f[4].Get<uint32>(); e.OtherFactionGarrAbilityID = f[5].Get<uint32>();
            e.GarrAbilityCategoryID = f[6].Get<uint32>(); e.GarrFollowerTypeID = f[7].Get<uint32>();
        });

    LoadTable(sGarrBuildingStore,
        "SELECT id, horde_game_object_id, alliance_game_object_id, garr_type_id, building_type, upgrade_level, alliance_name, horde_name, "
        "description, tooltip, build_seconds, currency_type_id, currency_qty, horde_ui_texture_kit_id, alliance_ui_texture_kit_id, "
        "icon_file_data_id, flags, alliance_scene_script_package_id, horde_scene_script_package_id, max_assignments, shipment_capacity, "
        "garr_ability_id, bonus_garr_ability_id, gold_cost FROM db2_garr_building WHERE garr_type_id = 2",
        [](GarrBuildingEntry& e, Field* f)
        {
            e.ID = f[0].Get<uint32>(); e.HordeGameObjectID = f[1].Get<uint32>(); e.AllianceGameObjectID = f[2].Get<uint32>();
            e.GarrTypeID = f[3].Get<uint32>(); e.Type = f[4].Get<uint32>(); e.Level = f[5].Get<uint32>();
            e.NameAlliance = Str(f[6]); e.NameHorde = Str(f[7]); e.Description = Str(f[8]); e.Tooltip = Str(f[9]);
            e.BuildDuration = f[10].Get<uint32>(); e.CostCurrencyID = f[11].Get<uint32>(); e.CostCurrencyAmount = f[12].Get<int32>();
            e.HordeTexPrefixKitID = f[13].Get<uint32>(); e.AllianceTexPrefixKitID = f[14].Get<uint32>();
            e.IconFileDataID = f[15].Get<uint32>(); e.Flags = f[16].Get<uint32>();
            e.AllianceActivationScenePackageID = f[17].Get<uint32>(); e.HordeActivationScenePackageID = f[18].Get<uint32>();
            e.MaxAssignments = f[19].Get<uint32>(); e.MaxShipments = f[20].Get<uint32>();
            e.FollowerRequiredGarrAbilityID = f[21].Get<uint32>(); e.FollowerGarrAbilityEffectID = f[22].Get<uint32>();
            e.CostMoney = f[23].Get<int32>();
        });

    LoadTable(sGarrBuildingPlotInstStore,
        "SELECT id, garr_building_id, ui_texture_atlas_member_id, garr_site_level_plot_inst_id, map_offset_0, map_offset_1 FROM db2_garr_building_plot_inst",
        [](GarrBuildingPlotInstEntry& e, Field* f)
        {
            e.ID = f[0].Get<uint32>(); e.GarrBuildingID = f[1].Get<uint32>(); e.UiTextureAtlasMemberID = f[2].Get<uint32>();
            e.GarrSiteLevelPlotInstID = f[3].Get<uint32>(); e.LandmarkOffset.X = f[4].Get<float>(); e.LandmarkOffset.Y = f[5].Get<float>();
        });

    LoadTable(sGarrClassSpecStore,
        "SELECT id, class_spec_male, class_spec_female, class_spec, ui_texture_atlas_member_id, garr_foll_item_set_id FROM db2_garr_class_spec",
        [](GarrClassSpecEntry& e, Field* f)
        {
            e.ID = f[0].Get<uint32>(); e.NameMale = Str(f[1]); e.NameFemale = Str(f[2]); e.NameGenderless = Str(f[3]);
            e.ClassAtlasID = f[4].Get<uint32>(); e.GarrFollItemSetID = f[5].Get<uint32>();
        });

    LoadTable(sGarrFollowerStore,
        "SELECT id, garr_type_id, garr_follower_type_id, horde_creature_id, alliance_creature_id, horde_garr_foll_race_id, "
        "alliance_garr_foll_race_id, quality, horde_garr_class_spec_id, alliance_garr_class_spec_id, horde_garr_foll_item_set_id, "
        "alliance_garr_foll_item_set_id, follower_level, item_level_weapon, item_level_armor, flags, horde_source_text, "
        "alliance_source_text, horde_icon_file_data_id, alliance_icon_file_data_id FROM db2_garr_follower WHERE garr_follower_type_id = 1",
        [](GarrFollowerEntry& e, Field* f)
        {
            e.ID = f[0].Get<uint32>(); e.GarrTypeID = f[1].Get<uint32>(); e.GarrFollowerTypeID = f[2].Get<uint32>();
            e.HordeCreatureID = f[3].Get<uint32>(); e.AllianceCreatureID = f[4].Get<uint32>();
            e.HordeUiAnimRaceInfoID = f[5].Get<uint32>(); e.AllianceUiAnimRaceInfoID = f[6].Get<uint32>();
            e.Quality = f[7].Get<uint32>(); e.HordeGarrClassSpecID = f[8].Get<uint32>(); e.AllianceGarrClassSpecID = f[9].Get<uint32>();
            e.HordeGarrFollItemSetID = f[10].Get<uint32>(); e.AllianceGarrFollItemSetID = f[11].Get<uint32>();
            e.Level = f[12].Get<uint32>(); e.ItemLevelWeapon = f[13].Get<uint32>(); e.ItemLevelArmor = f[14].Get<uint32>();
            e.Flags = f[15].Get<uint32>(); e.HordeSourceText = Str(f[16]); e.AllianceSourceText = Str(f[17]);
            e.HordePortraitIconID = f[18].Get<uint32>(); e.AlliancePortraitIconID = f[19].Get<uint32>();
        });

    LoadTable(sGarrFollowerLevelXPStore,
        "SELECT id, follower_level, xp_to_next_level, garr_follower_type_id FROM db2_garr_follower_level_xp WHERE garr_follower_type_id = 1",
        [](GarrFollowerLevelXPEntry& e, Field* f)
        {
            e.ID = f[0].Get<uint32>(); e.Level = f[1].Get<uint32>(); e.NextLevelXP = f[2].Get<uint32>(); e.GarrFollowerTypeID = f[3].Get<uint32>();
        });

    LoadTable(sGarrFollowerQualityStore,
        "SELECT id, quality, xp_to_next_quality, garr_follower_type_id FROM db2_garr_follower_quality WHERE garr_follower_type_id = 1",
        [](GarrFollowerQualityEntry& e, Field* f)
        {
            e.ID = f[0].Get<uint32>(); e.Quality = f[1].Get<uint32>(); e.NextQualityXP = f[2].Get<uint32>(); e.GarrFollowerTypeID = f[3].Get<uint32>();
        });

    LoadTable(sGarrFollowerXAbilityStore,
        "SELECT id, garr_follower_id, garr_ability_id, faction_index FROM db2_garr_follower_x_ability",
        [](GarrFollowerXAbilityEntry& e, Field* f)
        {
            e.ID = f[0].Get<uint32>(); e.GarrFollowerID = f[1].Get<uint32>(); e.GarrAbilityID = f[2].Get<uint32>(); e.FactionIndex = f[3].Get<uint32>();
        });

    LoadTable(sGarrMissionStore,
        "SELECT id, target_level, target_item_level, env_garr_mechanic_type_id, max_followers, mission_duration, offer_duration, "
        "garr_mission_type_id, garr_type_id, garr_follower_type_id, name, description, location, mission_cost, "
        "mission_cost_currency_types_id, base_follower_xp, base_completion_chance, travel_duration, flags "
        "FROM db2_garr_mission WHERE garr_follower_type_id = 1",
        [](GarrMissionEntry& e, Field* f)
        {
            e.ID = f[0].Get<uint32>(); e.ReqLevel = f[1].Get<uint32>(); e.ReqFollowersItemLevel = f[2].Get<uint32>();
            e.GarrMechanicTypeID = f[3].Get<uint32>(); e.ReqFollowersCount = f[4].Get<uint32>(); e.MissionDuration = f[5].Get<uint32>();
            e.OfferDuration = f[6].Get<uint32>(); e.GarrMissionTypeID = f[7].Get<uint32>(); e.GarrTypeID = f[8].Get<uint32>();
            e.GarrFollowerTypeID = f[9].Get<uint32>(); e.Name = Str(f[10]); e.Description = Str(f[11]); e.Location = Str(f[12]);
            e.ReqResourcesCount = f[13].Get<uint32>(); e.ReqResourcesCurrencyID = f[14].Get<uint32>();
            e.BaseXP = f[15].Get<uint32>(); e.BaseChance = f[16].Get<uint32>(); e.TravelDuration = f[17].Get<uint32>();
            e.Flags = f[18].Get<uint32>();
        });

    LoadTable(sGarrPlotStore,
        "SELECT id, plot_type, flags, name, alliance_construct_obj_id, horde_construct_obj_id FROM db2_garr_plot",
        [](GarrPlotEntry& e, Field* f)
        {
            e.ID = f[0].Get<uint32>(); e.PlotType = f[1].Get<uint32>(); e.Flags = f[2].Get<uint32>(); e.Name = Str(f[3]);
            e.AllianceConstructionGameObjectID = f[4].Get<uint32>(); e.HordeConstructionGameObjectID = f[5].Get<uint32>();
        });

    LoadTable(sGarrPlotBuildingStore,
        "SELECT id, garr_plot_id, garr_building_id FROM db2_garr_plot_building",
        [](GarrPlotBuildingEntry& e, Field* f)
        {
            e.ID = f[0].Get<uint32>(); e.GarrPlotID = f[1].Get<uint32>(); e.GarrBuildingID = f[2].Get<uint32>();
        });

    LoadTable(sGarrPlotInstanceStore,
        "SELECT id, garr_plot_id, name FROM db2_garr_plot_instance",
        [](GarrPlotInstanceEntry& e, Field* f)
        {
            e.ID = f[0].Get<uint32>(); e.GarrPlotID = f[1].Get<uint32>(); e.Name = Str(f[2]);
        });

    LoadTable(sGarrSiteLevelStore,
        "SELECT id, garr_level, map_id, garr_site_id, ui_texture_kit_id, town_hall_ui_pos_0, town_hall_ui_pos_1, upgrade_movie_id, "
        "max_building_level, upgrade_cost, upgrade_gold_cost FROM db2_garr_site_level",
        [](GarrSiteLevelEntry& e, Field* f)
        {
            e.ID = f[0].Get<uint32>(); e.Level = f[1].Get<uint32>(); e.MapID = f[2].Get<uint32>(); e.SiteID = f[3].Get<uint32>();
            e.UITextureKitID = f[4].Get<uint32>(); e.TownHall.X = f[5].Get<float>(); e.TownHall.Y = f[6].Get<float>();
            e.MovieID = f[7].Get<uint32>(); e.Level2 = f[8].Get<uint32>(); e.UpgradeResourceCost = f[9].Get<int32>();
            e.UpgradeMoneyCost = f[10].Get<int32>();
        });

    LoadTable(sGarrSiteLevelPlotInstStore,
        "SELECT id, garr_site_level_id, garr_plot_instance_id, ui_marker_pos_0, ui_marker_pos_1, ui_marker_size FROM db2_garr_site_level_plot_inst",
        [](GarrSiteLevelPlotInstEntry& e, Field* f)
        {
            e.ID = f[0].Get<uint32>(); e.GarrSiteLevelID = f[1].Get<uint32>(); e.GarrPlotInstanceID = f[2].Get<uint32>();
            e.Landmark.X = f[3].Get<float>(); e.Landmark.Y = f[4].Get<float>(); e.Unknown = f[5].Get<uint32>();
        });

    LoadTable(sGameObjectsStore,
        "SELECT id, owner_id, display_id, pos_0, pos_1, pos_2, rot_0, rot_1, rot_2, rot_3, scale, type_id, "
        "prop_value_0, prop_value_1, prop_value_2, prop_value_3, prop_value_4, prop_value_5, prop_value_6, prop_value_7, name "
        "FROM db2_game_objects",
        [](GameObjectsEntry& e, Field* f)
        {
            e.ID = f[0].Get<uint32>(); e.MapID = f[1].Get<uint32>(); e.DisplayID = f[2].Get<uint32>();
            e.Position.X = f[3].Get<float>(); e.Position.Y = f[4].Get<float>(); e.Position.Z = f[5].Get<float>();
            e.RotationX = f[6].Get<float>(); e.RotationY = f[7].Get<float>(); e.RotationZ = f[8].Get<float>(); e.RotationW = f[9].Get<float>();
            e.Size = f[10].Get<float>(); e.Type = f[11].Get<uint32>();
            for (uint8 i = 0; i < 8; ++i)
                e.Data[i] = f[12 + i].Get<uint32>();
            e.Name = Str(f[20]);
        });

    LOG_INFO("server.loading", ">> Loaded garrison DB2: {} buildings, {} plots, {} site levels, {} followers, {} missions, {} shipments, {} gameobjects in {} ms",
        sGarrBuildingStore.GetNumRows(), sGarrPlotInstanceStore.GetNumRows(), sGarrSiteLevelStore.GetNumRows(),
        sGarrFollowerStore.GetNumRows(), sGarrMissionStore.GetNumRows(), sCharShipmentStore.GetNumRows(),
        sGameObjectsStore.GetNumRows(), GetMSTimeDiffToNow(oldMSTime));
}

uint32 GarrisonDB2::GetXPForNextFollowerLevel(uint32 level)
{
    for (GarrFollowerLevelXPEntry const* entry : sGarrFollowerLevelXPStore)
        if (entry->Level == level)
            return entry->NextLevelXP;
    return 0;
}

uint32 GarrisonDB2::GetXPForNextFollowerQuality(uint32 quality)
{
    for (GarrFollowerQualityEntry const* entry : sGarrFollowerQualityStore)
        if (entry->Quality == quality)
            return entry->NextQualityXP;
    return 0;
}
