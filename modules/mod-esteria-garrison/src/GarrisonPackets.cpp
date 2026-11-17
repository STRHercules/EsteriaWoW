#include "GarrisonPackets.h"
#include "Opcodes.h"

namespace WorldPackets::Garrison
{
    namespace
    {
        void WritePos(ByteBuffer& data, Position const& pos, bool orientation)
        {
            data << float(pos.GetPositionX()) << float(pos.GetPositionY()) << float(pos.GetPositionZ());
            if (orientation)
                data << float(pos.GetOrientation());
        }

        void WriteGuid(ByteBuffer& data, ObjectGuid const& guid) { data << uint64(guid.GetRawValue()); }

        ObjectGuid ReadGuid(ByteBuffer& data)
        {
            uint64 raw = 0;
            data >> raw;
            return ObjectGuid(raw);
        }
    }

    ByteBuffer& operator<<(ByteBuffer& data, GarrisonPlotInfo const& plotInfo)
    {
        data << uint32(plotInfo.GarrPlotInstanceID);
        WritePos(data, plotInfo.PlotPos, true);
        data << uint32(plotInfo.PlotType);
        return data;
    }

    ByteBuffer& operator<<(ByteBuffer& data, GarrisonBuildingInfo const& buildingInfo)
    {
        data << uint32(buildingInfo.GarrPlotInstanceID);
        data << uint32(buildingInfo.GarrBuildingID);
        data << uint32(buildingInfo.TimeBuilt);
        data << uint32(buildingInfo.CurrentGarSpecID);
        data << uint32(buildingInfo.TimeSpecCooldown);
        data << uint8(buildingInfo.Active);
        return data;
    }

    ByteBuffer& operator<<(ByteBuffer& data, GarrisonFollower const& follower)
    {
        data << uint64(follower.DbID);
        data << uint32(follower.GarrFollowerID);
        data << uint32(follower.Quality);
        data << uint32(follower.FollowerLevel);
        data << uint32(follower.ItemLevelWeapon);
        data << uint32(follower.ItemLevelArmor);
        data << uint32(follower.Xp);
        data << uint32(follower.CurrentBuildingID);
        data << uint32(follower.CurrentMissionID);
        data << uint32(follower.AbilityID.size());
        data << uint32(follower.FollowerStatus);
        for (GarrAbilityEntry const* ability : follower.AbilityID)
            data << uint32(ability->ID);
        return data;
    }

    ByteBuffer& operator<<(ByteBuffer& data, GarrisonMission const& mission)
    {
        data << uint64(mission.DbID);
        data << uint32(mission.MissionRecID);
        data << uint32(mission.OfferTime);
        data << uint32(mission.OfferDuration);
        data << uint32(mission.StartTime);
        data << uint32(mission.TravelDuration);
        data << uint32(mission.MissionDuration);
        data << uint32(mission.MissionState);
        return data;
    }

    ByteBuffer& operator<<(ByteBuffer& data, Shipment const& shipment)
    {
        data << uint32(shipment.ShipmentRecID);
        data << uint64(shipment.ShipmentID);
        data << uint32(shipment.CreationTime);
        data << int32(shipment.ShipmentDuration);
        data << uint32(shipment.BuildingTypeID);
        return data;
    }

    ServerPacket::ServerPacket(GarrisonServerOpcode opcode, size_t size) : _worldPacket(SMSG_ESTERIA_GARRISON_STATE, size + 2)
    {
        _worldPacket << uint16(opcode);
    }

    WorldPacket const* ServerPacket::Write()
    {
        WritePayload();
        return &_worldPacket;
    }

    void GarrisonCreateResult::WritePayload()
    {
        _worldPacket << uint32(Result);
        _worldPacket << uint32(GarrSiteLevelID);
    }

    void GarrisonDeleteResult::WritePayload()
    {
        _worldPacket << uint32(Result);
        _worldPacket << uint32(GarrSiteID);
    }

    void GetGarrisonInfoResult::WritePayload()
    {
        _worldPacket << int32(GarrSiteID);
        _worldPacket << int32(GarrSiteLevelID);
        _worldPacket << int32(FactionIndex);
        _worldPacket << uint32(Buildings.size());
        _worldPacket << uint32(Plots.size());
        _worldPacket << uint32(Followers.size());
        _worldPacket << uint32(Missions.size());
        _worldPacket << uint32(ArchivedMissions.size());
        _worldPacket << int32(NumFollowerActivationsRemaining);

        for (GarrisonBuildingInfo const* building : Buildings)
            _worldPacket << *building;

        for (GarrisonPlotInfo const* plot : Plots)
            _worldPacket << *plot;

        for (GarrisonFollower const* follower : Followers)
            _worldPacket << *follower;

        for (GarrisonMission const* mission : Missions)
            _worldPacket << *mission;

        for (int32 archived : ArchivedMissions)
            _worldPacket << int32(archived);
    }

    void GarrisonRemoteInfo::WritePayload()
    {
        _worldPacket << uint32(Sites.size());
        for (GarrisonRemoteSiteInfo const& site : Sites)
        {
            _worldPacket << uint32(site.GarrSiteLevelID);
            _worldPacket << uint32(site.Buildings.size());
            for (GarrisonRemoteBuildingInfo const& building : site.Buildings)
                _worldPacket << uint32(building.GarrPlotInstanceID) << uint32(building.GarrBuildingID);
        }
    }

    void GarrisonPurchaseBuilding::Read()
    {
        NpcGUID = ReadGuid(_worldPacket);
        _worldPacket >> PlotInstanceID;
        _worldPacket >> BuildingID;
    }

    void GarrisonPlaceBuildingResult::WritePayload()
    {
        _worldPacket << uint32(Result);
        _worldPacket << BuildingInfo;
        _worldPacket << uint8(PlayActivationCinematic);
    }

    void GarrisonCancelConstruction::Read()
    {
        NpcGUID = ReadGuid(_worldPacket);
        _worldPacket >> PlotInstanceID;
    }

    void GarrisonBuildingRemoved::WritePayload()
    {
        _worldPacket << uint32(Result);
        _worldPacket << uint32(GarrPlotInstanceID);
        _worldPacket << uint32(GarrBuildingID);
    }

    void GarrisonLearnBlueprintResult::WritePayload()
    {
        _worldPacket << uint32(Result);
        _worldPacket << uint32(BuildingID);
    }

    void GarrisonUnlearnBlueprintResult::WritePayload()
    {
        _worldPacket << uint32(Result);
        _worldPacket << uint32(BuildingID);
    }

    void GarrisonRequestBlueprintAndSpecializationDataResult::WritePayload()
    {
        _worldPacket << uint32(BlueprintsKnown ? BlueprintsKnown->size() : 0);
        _worldPacket << uint32(SpecializationsKnown ? SpecializationsKnown->size() : 0);
        if (BlueprintsKnown)
            for (uint32 blueprint : *BlueprintsKnown)
                _worldPacket << uint32(blueprint);

        if (SpecializationsKnown)
            for (uint32 specialization : *SpecializationsKnown)
                _worldPacket << uint32(specialization);
    }

    void GarrisonBuildingLandmarks::WritePayload()
    {
        _worldPacket << uint32(Landmarks.size());
        for (GarrisonBuildingLandmark const& landmark : Landmarks)
        {
            _worldPacket << uint32(landmark.GarrBuildingPlotInstID);
            WritePos(_worldPacket, landmark.Pos, false);
        }
    }

    void GarrisonPlotPlaced::WritePayload()
    {
        _worldPacket << *PlotInfo;
    }

    void GarrisonPlotRemoved::WritePayload()
    {
        _worldPacket << uint32(GarrPlotInstanceID);
    }

    void GarrisonAddFollowerResult::WritePayload()
    {
        _worldPacket << uint32(Result);
        _worldPacket << Follower;
    }

    void GarrisonFollowerChangedItemLevel::WritePayload()
    {
        _worldPacket << Follower;
    }

    void GarrisonBuildingActivated::WritePayload()
    {
        _worldPacket << uint32(GarrPlotInstanceID);
    }

    void GarrisonMissionBonusRoll::Read()
    {
        NpcGUID = ReadGuid(_worldPacket);
        _worldPacket >> MissionRecID;
    }

    void GarrisonMissionBonusRollResult::WritePayload()
    {
        _worldPacket << MissionData;
        _worldPacket << uint32(MissionRecID);
        _worldPacket << uint32(Result);
    }

    void GarrisonStartMission::Read()
    {
        NpcGUID = ReadGuid(_worldPacket);
        uint32 followerCount = 0;
        _worldPacket >> followerCount;
        _worldPacket >> MissionRecID;
        FollowerDBIDs.clear();
        for (uint32 i = 0; i < followerCount && i < 32; ++i)
        {
            uint64 followerDbId = 0;
            _worldPacket >> followerDbId;
            FollowerDBIDs.push_back(followerDbId);
        }
    }

    void GarrisonCompleteMission::Read()
    {
        NpcGUID = ReadGuid(_worldPacket);
        _worldPacket >> MissionRecID;
    }

    void GarrisonAssignFollowerToBuildingResult::WritePayload()
    {
        _worldPacket << uint64(FollowerDBID);
        _worldPacket << int32(Result);
        _worldPacket << int32(PlotInstanceID);
    }

    void GarrisonLandingPage::WritePayload()
    {
        _worldPacket << uint32(MsgData.size());
        for (Shipment const& shipment : MsgData)
            _worldPacket << shipment;
    }

    void GarrisonAddMissionResult::WritePayload()
    {
        _worldPacket << uint32(Result);
        _worldPacket << uint8(unk);
        _worldPacket << MissionData;
    }

    void GarrisonUpgradeResult::WritePayload()
    {
        _worldPacket << uint32(Result);
        _worldPacket << uint32(GarrSiteLevelID);
    }

    void GarrisonStartMissionResult::WritePayload()
    {
        _worldPacket << uint32(Result);
        _worldPacket << MissionData;
        _worldPacket << uint32(FollowerDBIDs.size());
        for (uint64 dbId : FollowerDBIDs)
            _worldPacket << uint64(dbId);
    }

    void GarrisonCompleteMissionResult::WritePayload()
    {
        _worldPacket << uint32(Result);
        _worldPacket << MissionData;
        _worldPacket << uint32(MissionRecID);
        _worldPacket << uint8(Succeeded);
    }

    void GarrisonIsUpgradeableResult::WritePayload()
    {
        _worldPacket << uint32(Result);
    }

    void CreateShipment::Read()
    {
        NpcGUID = ReadGuid(_worldPacket);
        _worldPacket >> Count;
    }

    void GarrisonRequestShipmentInfo::Read()
    {
        NpcGUID = ReadGuid(_worldPacket);
    }

    void GarrisonOpenMissionNpc::Read()
    {
        NpcGUID = ReadGuid(_worldPacket);
    }

    void CompleteAllReadyShipments::Read()
    {
        GUID = ReadGuid(_worldPacket);
    }

    void GetShipmentInfoResponse::WritePayload()
    {
        _worldPacket << uint8(Success);
        _worldPacket << uint32(ShipmentID);
        _worldPacket << uint32(MaxShipments);
        _worldPacket << uint32(Shipments.size());
        _worldPacket << uint32(PlotInstanceID);
        for (Shipment const& shipment : Shipments)
            _worldPacket << shipment;
    }

    void CreateShipmentResponse::WritePayload()
    {
        _worldPacket << uint64(ShipmentID);
        _worldPacket << uint32(ShipmentRecID);
        _worldPacket << uint32(Result);
    }

    void OpenShipmentNPCFromGossip::WritePayload()
    {
        WriteGuid(_worldPacket, NpcGUID);
        _worldPacket << uint32(CharShipmentContainerID);
    }

    void UpgradeGarrison::Read()
    {
        NpcGUID = ReadGuid(_worldPacket);
    }

    void GarrisonSetFollowerInactive::Read()
    {
        _worldPacket >> FollowerDBID;
        uint8 inactive = 0;
        _worldPacket >> inactive;
        Inactive = inactive != 0;
    }

    void GarrisonRemoveFollowerFromBuilding::Read()
    {
        NpcGUID = ReadGuid(_worldPacket);
        _worldPacket >> FollowerDBID;
    }

    void GarrisonAssignFollowerToBuilding::Read()
    {
        NpcGUID = ReadGuid(_worldPacket);
        _worldPacket >> PlotInstanceID;
        _worldPacket >> FollowerDBID;
    }

    void GarrisonOpenArchitect::WritePayload()
    {
        WriteGuid(_worldPacket, NpcGUID);
    }

    void GarrisonOpenMissionNpcResponse::WritePayload()
    {
        WriteGuid(_worldPacket, NpcGUID);
    }

    void GarrisonRemoveFollowerResult::WritePayload()
    {
        _worldPacket << uint64(FollowerDBID);
        _worldPacket << int32(Result);
        _worldPacket << int32(Destroyed);
    }

    void GarrisonFollowerChangedXP::WritePayload()
    {
        _worldPacket << uint32(TotalXp);
        _worldPacket << int32(Result);
        _worldPacket << Follower;
        _worldPacket << Follower2;
    }

    void GarrisonNumFollowerActivationsRemaining::WritePayload()
    {
        _worldPacket << int32(Amount);
    }

    void GarrisonRemoveFollowerFromBuildingResult::WritePayload()
    {
        _worldPacket << uint64(FollowerDBID);
        _worldPacket << int32(Result);
    }

    void GarrisonMissionListUpdate::WritePayload()
    {
        _worldPacket << uint32(Result);
        _worldPacket << uint32(updatedMissionRecIDs.size());
        for (uint32 id : updatedMissionRecIDs)
            _worldPacket << uint32(id);
        _worldPacket << uint8(openMissionNpc);
    }

    void SetCurrency::WritePayload()
    {
        _worldPacket << uint32(Type);
        _worldPacket << int32(Quantity);
        _worldPacket << uint8(SuppressChatLog);
    }

    void StreamingMovie::WritePayload()
    {
        _worldPacket << uint32(MovieIDs.size());
        for (uint32 id : MovieIDs)
            _worldPacket << uint32(id);
    }
}
