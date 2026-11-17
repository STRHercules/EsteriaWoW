/*
 * UWoW GarrisonPackets.h carried over the client extension opcodes: every server packet is
 * SMSG_ESTERIA_GARRISON_STATE = [uint16 GarrisonServerOpcode][payload], every client packet is
 * CMSG_ESTERIA_GARRISON_ACTION = [uint16 GarrisonClientOpcode][payload]; CMSG_ESTERIA_GARRISON_HELLO is
 * CMSG_GET_GARRISON_INFO. Payload fields keep UWoW's order; guids are uint64, times are uint32 unix seconds,
 * positions are four floats (x, y, z, o), lists are a uint32 count followed by the elements.
 */

#ifndef GarrisonPackets_h__
#define GarrisonPackets_h__

#include "GarrisonDB2.h"
#include "ObjectGuid.h"
#include "Position.h"
#include "WorldPacket.h"
#include <list>
#include <optional>
#include <unordered_set>
#include <vector>

enum GarrisonServerOpcode : uint16
{
    SMSG_GARRISON_CREATE_RESULT                                     = 1,
    SMSG_GARRISON_DELETE_RESULT                                     = 2,
    SMSG_GET_GARRISON_INFO_RESULT                                   = 3,
    SMSG_GARRISON_REMOTE_INFO                                       = 4,
    SMSG_GARRISON_PLACE_BUILDING_RESULT                             = 5,
    SMSG_GARRISON_BUILDING_REMOVED                                  = 6,
    SMSG_GARRISON_LEARN_BLUEPRINT_RESULT                            = 7,
    SMSG_GARRISON_UNLEARN_BLUEPRINT_RESULT                          = 8,
    SMSG_GARRISON_REQUEST_BLUEPRINT_AND_SPECIALIZATION_DATA_RESULT  = 9,
    SMSG_GARRISON_BUILDING_LANDMARKS                                = 10,
    SMSG_GARRISON_PLOT_PLACED                                       = 11,
    SMSG_GARRISON_PLOT_REMOVED                                      = 12,
    SMSG_GARRISON_ADD_FOLLOWER_RESULT                               = 13,
    SMSG_GARRISON_FOLLOWER_CHANGED_ITEM_LEVEL                       = 14,
    SMSG_GARRISON_BUILDING_ACTIVATED                                = 15,
    SMSG_GARRISON_MISSION_BONUS_ROLL_RESULT                         = 16,
    SMSG_GARRISON_LANDING_PAGE_SHIPMENT_INFO                        = 17,
    SMSG_GARRISON_ADD_MISSION_RESULT                                = 18,
    SMSG_GARRISON_UPGRADE_RESULT                                    = 19,
    SMSG_GARRISON_START_MISSION_RESULT                              = 20,
    SMSG_GARRISON_COMPLETE_MISSION_RESULT                           = 21,
    SMSG_GARRISON_IS_UPGRADEABLE_RESULT                             = 22,
    SMSG_GET_SHIPMENT_INFO_RESPONSE                                 = 23,
    SMSG_CREATE_SHIPMENT_RESPONSE                                   = 24,
    SMSG_OPEN_SHIPMENT_NPC_FROM_GOSSIP                              = 25,
    SMSG_GARRISON_OPEN_ARCHITECT                                    = 26,
    SMSG_GARRISON_OPEN_MISSION_NPC                                  = 27,
    SMSG_GARRISON_FOLLOWER_CHANGED_XP                               = 28,
    SMSG_GARRISON_MISSION_LIST_UPDATE                               = 29,
    SMSG_GARRISON_ASSIGN_FOLLOWER_TO_BUILDING_RESULT                = 30,
    SMSG_GARRISON_REMOVE_FOLLOWER_FROM_BUILDING_RESULT              = 31,
    SMSG_GARRISON_REMOVE_FOLLOWER_RESULT                            = 32,
    SMSG_GARRISON_NUM_FOLLOWER_ACTIVATIONS_REMAINING                = 33,
    SMSG_SET_CURRENCY                                               = 34,
    SMSG_STREAMING_MOVIE                                            = 35,
};

enum GarrisonClientOpcode : uint16
{
    CMSG_GET_GARRISON_INFO                                          = 1,
    CMSG_GARRISON_PURCHASE_BUILDING                                 = 2,
    CMSG_GARRISON_CANCEL_CONSTRUCTION                               = 3,
    CMSG_GARRISON_REQUEST_BLUEPRINT_AND_SPECIALIZATION_DATA         = 4,
    CMSG_GARRISON_GET_BUILDING_LANDMARKS                            = 5,
    CMSG_GARRISON_MISSION_BONUS_ROLL                                = 6,
    CMSG_GARRISON_REQUEST_LANDING_PAGE_SHIPMENT_INFO                = 7,
    CMSG_GARRISON_CHECK_UPGRADEABLE                                 = 8,
    CMSG_GARRISON_START_MISSION                                     = 9,
    CMSG_GARRISON_COMPLETE_MISSION                                  = 10,
    CMSG_CREATE_SHIPMENT                                            = 11,
    CMSG_GARRISON_REQUEST_SHIPMENT_INFO                             = 12,
    CMSG_OPEN_MISSION_NPC                                           = 13,
    CMSG_COMPLETE_ALL_READY_SHIPMENTS                               = 14,
    CMSG_UPGRADE_GARRISON                                           = 15,
    CMSG_GARRISON_SET_FOLLOWER_INACTIVE                             = 16,
    CMSG_GARRISON_REMOVE_FOLLOWER_FROM_BUILDING                     = 17,
    CMSG_GARRISON_ASSIGN_FOLLOWER_TO_BUILDING                       = 18,
};

namespace WorldPackets::Garrison
{
    class ServerPacket
    {
    public:
        explicit ServerPacket(GarrisonServerOpcode opcode, size_t size = 32);
        virtual ~ServerPacket() = default;

        WorldPacket const* Write();

    protected:
        virtual void WritePayload() = 0;
        WorldPacket _worldPacket;
    };

    class ClientPacket
    {
    public:
        explicit ClientPacket(WorldPacket& packet) : _worldPacket(packet) { }
        virtual ~ClientPacket() = default;
        virtual void Read() { }

    protected:
        WorldPacket& _worldPacket;
    };

    struct GarrisonPlotInfo
    {
        Position PlotPos;
        uint32 GarrPlotInstanceID = 0;
        uint32 PlotType = 0;
    };

    struct GarrisonBuildingInfo
    {
        uint32 GarrPlotInstanceID = 0;
        uint32 GarrBuildingID = 0;
        time_t TimeBuilt = time_t(0);
        uint32 CurrentGarSpecID = 0;
        time_t TimeSpecCooldown = time_t(2288912640);
        bool Active = false;
    };

    struct GarrisonFollower
    {
        uint64 DbID = 0;
        uint32 GarrFollowerID = 0;
        uint32 Quality = 0;
        uint32 FollowerLevel = 0;
        uint32 ItemLevelWeapon = 0;
        uint32 ItemLevelArmor = 0;
        uint32 Xp = 0;
        uint32 CurrentBuildingID = 0;
        uint32 CurrentMissionID = 0;
        std::list<GarrAbilityEntry const*> AbilityID;
        uint32 FollowerStatus = 0;
    };

    struct GarrisonMission
    {
        uint64 DbID = 0;
        uint32 MissionRecID = 0;
        time_t OfferTime = time_t(0);
        uint32 OfferDuration = 0;
        time_t StartTime = time_t(2288912640);
        uint32 TravelDuration = 0;
        uint32 MissionDuration = 0;
        uint32 MissionState = 0;
    };

    struct Shipment
    {
        uint64 ShipmentID = 0;
        uint32 ShipmentRecID = 0;
        uint32 BuildingTypeID = 0;
        time_t CreationTime = time(nullptr);
        int32 ShipmentDuration = 0;
    };

    class GarrisonCreateResult final : public ServerPacket
    {
    public:
        GarrisonCreateResult() : ServerPacket(SMSG_GARRISON_CREATE_RESULT, 8) { }
        uint32 GarrSiteLevelID = 0;
        uint32 Result = 0;
    private:
        void WritePayload() override;
    };

    class GarrisonDeleteResult final : public ServerPacket
    {
    public:
        GarrisonDeleteResult() : ServerPacket(SMSG_GARRISON_DELETE_RESULT, 8) { }
        uint32 Result = 0;
        uint32 GarrSiteID = 0;
    private:
        void WritePayload() override;
    };

    class GetGarrisonInfoResult final : public ServerPacket
    {
    public:
        GetGarrisonInfoResult() : ServerPacket(SMSG_GET_GARRISON_INFO_RESULT, 512) { }
        uint32 GarrSiteID = 0;
        uint32 GarrSiteLevelID = 0;
        uint32 FactionIndex = 0;
        uint32 NumFollowerActivationsRemaining = 0;
        std::vector<GarrisonPlotInfo*> Plots;
        std::vector<GarrisonBuildingInfo const*> Buildings;
        std::vector<GarrisonFollower const*> Followers;
        std::vector<GarrisonMission const*> Missions;
        std::vector<int32> ArchivedMissions;
    private:
        void WritePayload() override;
    };

    struct GarrisonRemoteBuildingInfo
    {
        GarrisonRemoteBuildingInfo(uint32 plotInstanceId, uint32 buildingId) : GarrPlotInstanceID(plotInstanceId), GarrBuildingID(buildingId) { }
        uint32 GarrPlotInstanceID;
        uint32 GarrBuildingID;
    };

    struct GarrisonRemoteSiteInfo
    {
        uint32 GarrSiteLevelID = 0;
        std::vector<GarrisonRemoteBuildingInfo> Buildings;
    };

    class GarrisonRemoteInfo final : public ServerPacket
    {
    public:
        GarrisonRemoteInfo() : ServerPacket(SMSG_GARRISON_REMOTE_INFO, 64) { }
        std::vector<GarrisonRemoteSiteInfo> Sites;
    private:
        void WritePayload() override;
    };

    class GarrisonPurchaseBuilding final : public ClientPacket
    {
    public:
        using ClientPacket::ClientPacket;
        void Read() override;
        ObjectGuid NpcGUID;
        uint32 BuildingID = 0;
        uint32 PlotInstanceID = 0;
    };

    class GarrisonPlaceBuildingResult final : public ServerPacket
    {
    public:
        GarrisonPlaceBuildingResult() : ServerPacket(SMSG_GARRISON_PLACE_BUILDING_RESULT, 32) { }
        GarrisonBuildingInfo BuildingInfo;
        uint32 Result = 0;
        bool PlayActivationCinematic = false;
    private:
        void WritePayload() override;
    };

    class GarrisonCancelConstruction final : public ClientPacket
    {
    public:
        using ClientPacket::ClientPacket;
        void Read() override;
        ObjectGuid NpcGUID;
        uint32 PlotInstanceID = 0;
    };

    class GarrisonBuildingRemoved final : public ServerPacket
    {
    public:
        GarrisonBuildingRemoved() : ServerPacket(SMSG_GARRISON_BUILDING_REMOVED, 12) { }
        uint32 Result = 0;
        uint32 GarrPlotInstanceID = 0;
        uint32 GarrBuildingID = 0;
    private:
        void WritePayload() override;
    };

    class GarrisonLearnBlueprintResult final : public ServerPacket
    {
    public:
        GarrisonLearnBlueprintResult() : ServerPacket(SMSG_GARRISON_LEARN_BLUEPRINT_RESULT, 8) { }
        uint32 BuildingID = 0;
        uint32 Result = 0;
    private:
        void WritePayload() override;
    };

    class GarrisonUnlearnBlueprintResult final : public ServerPacket
    {
    public:
        GarrisonUnlearnBlueprintResult() : ServerPacket(SMSG_GARRISON_UNLEARN_BLUEPRINT_RESULT, 8) { }
        uint32 BuildingID = 0;
        uint32 Result = 0;
    private:
        void WritePayload() override;
    };

    class GarrisonRequestBlueprintAndSpecializationDataResult final : public ServerPacket
    {
    public:
        GarrisonRequestBlueprintAndSpecializationDataResult() : ServerPacket(SMSG_GARRISON_REQUEST_BLUEPRINT_AND_SPECIALIZATION_DATA_RESULT, 400) { }
        std::unordered_set<uint32> const* SpecializationsKnown = nullptr;
        std::unordered_set<uint32> const* BlueprintsKnown = nullptr;
    private:
        void WritePayload() override;
    };

    struct GarrisonBuildingLandmark
    {
        GarrisonBuildingLandmark(uint32 buildingPlotInstId, Position const& pos) : Pos(pos), GarrBuildingPlotInstID(buildingPlotInstId) { }
        Position Pos;
        uint32 GarrBuildingPlotInstID;
    };

    class GarrisonBuildingLandmarks final : public ServerPacket
    {
    public:
        GarrisonBuildingLandmarks() : ServerPacket(SMSG_GARRISON_BUILDING_LANDMARKS, 64) { }
        std::vector<GarrisonBuildingLandmark> Landmarks;
    private:
        void WritePayload() override;
    };

    class GarrisonPlotPlaced final : public ServerPacket
    {
    public:
        GarrisonPlotPlaced() : ServerPacket(SMSG_GARRISON_PLOT_PLACED, 24) { }
        GarrisonPlotInfo* PlotInfo = nullptr;
    private:
        void WritePayload() override;
    };

    class GarrisonPlotRemoved final : public ServerPacket
    {
    public:
        GarrisonPlotRemoved() : ServerPacket(SMSG_GARRISON_PLOT_REMOVED, 4) { }
        uint32 GarrPlotInstanceID = 0;
    private:
        void WritePayload() override;
    };

    class GarrisonAddFollowerResult final : public ServerPacket
    {
    public:
        GarrisonAddFollowerResult() : ServerPacket(SMSG_GARRISON_ADD_FOLLOWER_RESULT, 64) { }
        GarrisonFollower Follower;
        uint32 Result = 0;
    private:
        void WritePayload() override;
    };

    class GarrisonFollowerChangedItemLevel final : public ServerPacket
    {
    public:
        GarrisonFollowerChangedItemLevel() : ServerPacket(SMSG_GARRISON_FOLLOWER_CHANGED_ITEM_LEVEL, 64) { }
        GarrisonFollower Follower;
    private:
        void WritePayload() override;
    };

    class GarrisonBuildingActivated final : public ServerPacket
    {
    public:
        GarrisonBuildingActivated() : ServerPacket(SMSG_GARRISON_BUILDING_ACTIVATED, 4) { }
        uint32 GarrPlotInstanceID = 0;
    private:
        void WritePayload() override;
    };

    class GarrisonMissionBonusRoll final : public ClientPacket
    {
    public:
        using ClientPacket::ClientPacket;
        void Read() override;
        ObjectGuid NpcGUID;
        uint32 MissionRecID = 0;
    };

    class GarrisonMissionBonusRollResult final : public ServerPacket
    {
    public:
        GarrisonMissionBonusRollResult() : ServerPacket(SMSG_GARRISON_MISSION_BONUS_ROLL_RESULT, 48) { }
        GarrisonMission MissionData;
        uint32 MissionRecID = 0;
        uint32 Result = 0;
    private:
        void WritePayload() override;
    };

    class GarrisonStartMission final : public ClientPacket
    {
    public:
        using ClientPacket::ClientPacket;
        void Read() override;
        ObjectGuid NpcGUID;
        std::vector<uint64> FollowerDBIDs;
        uint32 MissionRecID = 0;
    };

    class GarrisonCompleteMission final : public ClientPacket
    {
    public:
        using ClientPacket::ClientPacket;
        void Read() override;
        ObjectGuid NpcGUID;
        uint32 MissionRecID = 0;
    };

    class GarrisonAssignFollowerToBuildingResult final : public ServerPacket
    {
    public:
        GarrisonAssignFollowerToBuildingResult() : ServerPacket(SMSG_GARRISON_ASSIGN_FOLLOWER_TO_BUILDING_RESULT, 16) { }
        uint64 FollowerDBID = 0;
        int32 Result = 0;
        int32 PlotInstanceID = 0;
    private:
        void WritePayload() override;
    };

    class GarrisonLandingPage final : public ServerPacket
    {
    public:
        GarrisonLandingPage() : ServerPacket(SMSG_GARRISON_LANDING_PAGE_SHIPMENT_INFO, 64) { }
        std::vector<Shipment> MsgData;
    private:
        void WritePayload() override;
    };

    class GarrisonAddMissionResult final : public ServerPacket
    {
    public:
        GarrisonAddMissionResult() : ServerPacket(SMSG_GARRISON_ADD_MISSION_RESULT, 48) { }
        GarrisonMission MissionData;
        uint32 Result = 0;
        uint8 unk = 0;
    private:
        void WritePayload() override;
    };

    class GarrisonUpgradeResult final : public ServerPacket
    {
    public:
        GarrisonUpgradeResult() : ServerPacket(SMSG_GARRISON_UPGRADE_RESULT, 8) { }
        uint32 GarrSiteLevelID = 0;
        uint32 Result = 0;
    private:
        void WritePayload() override;
    };

    class GarrisonStartMissionResult final : public ServerPacket
    {
    public:
        GarrisonStartMissionResult() : ServerPacket(SMSG_GARRISON_START_MISSION_RESULT, 64) { }
        GarrisonMission MissionData;
        std::vector<uint64> FollowerDBIDs;
        uint32 Result = 0;
    private:
        void WritePayload() override;
    };

    class GarrisonCompleteMissionResult final : public ServerPacket
    {
    public:
        GarrisonCompleteMissionResult() : ServerPacket(SMSG_GARRISON_COMPLETE_MISSION_RESULT, 48) { }
        GarrisonMission MissionData;
        uint32 Result = 0;
        uint32 MissionRecID = 0;
        bool Succeeded = false;
    private:
        void WritePayload() override;
    };

    class GarrisonIsUpgradeableResult final : public ServerPacket
    {
    public:
        GarrisonIsUpgradeableResult() : ServerPacket(SMSG_GARRISON_IS_UPGRADEABLE_RESULT, 4) { }
        uint32 Result = 0;
    private:
        void WritePayload() override;
    };

    class CreateShipment final : public ClientPacket
    {
    public:
        using ClientPacket::ClientPacket;
        void Read() override;
        ObjectGuid NpcGUID;
        uint32 Count = 0;
    };

    class GarrisonRequestShipmentInfo final : public ClientPacket
    {
    public:
        using ClientPacket::ClientPacket;
        void Read() override;
        ObjectGuid NpcGUID;
    };

    class GarrisonOpenMissionNpc final : public ClientPacket
    {
    public:
        using ClientPacket::ClientPacket;
        void Read() override;
        ObjectGuid NpcGUID;
    };

    class CompleteAllReadyShipments final : public ClientPacket
    {
    public:
        using ClientPacket::ClientPacket;
        void Read() override;
        ObjectGuid GUID;
    };

    class GetShipmentInfoResponse final : public ServerPacket
    {
    public:
        GetShipmentInfoResponse() : ServerPacket(SMSG_GET_SHIPMENT_INFO_RESPONSE, 64) { }
        std::vector<Shipment> Shipments;
        uint32 ShipmentID = 0;
        uint32 MaxShipments = 0;
        uint32 PlotInstanceID = 0;
        bool Success = false;
    private:
        void WritePayload() override;
    };

    class CreateShipmentResponse final : public ServerPacket
    {
    public:
        CreateShipmentResponse() : ServerPacket(SMSG_CREATE_SHIPMENT_RESPONSE, 16) { }
        uint64 ShipmentID = 0;
        uint32 ShipmentRecID = 0;
        uint32 Result = 0;
    private:
        void WritePayload() override;
    };

    class OpenShipmentNPCFromGossip final : public ServerPacket
    {
    public:
        OpenShipmentNPCFromGossip() : ServerPacket(SMSG_OPEN_SHIPMENT_NPC_FROM_GOSSIP, 12) { }
        ObjectGuid NpcGUID;
        uint32 CharShipmentContainerID = 0;
    private:
        void WritePayload() override;
    };

    class UpgradeGarrison final : public ClientPacket
    {
    public:
        using ClientPacket::ClientPacket;
        void Read() override;
        ObjectGuid NpcGUID;
    };

    class GarrisonSetFollowerInactive final : public ClientPacket
    {
    public:
        using ClientPacket::ClientPacket;
        void Read() override;
        uint64 FollowerDBID = 0;
        bool Inactive = false;
    };

    class GarrisonRemoveFollowerFromBuilding final : public ClientPacket
    {
    public:
        using ClientPacket::ClientPacket;
        void Read() override;
        ObjectGuid NpcGUID;
        uint64 FollowerDBID = 0;
    };

    class GarrisonAssignFollowerToBuilding final : public ClientPacket
    {
    public:
        using ClientPacket::ClientPacket;
        void Read() override;
        ObjectGuid NpcGUID;
        uint64 FollowerDBID = 0;
        uint32 PlotInstanceID = 0;
    };

    class GarrisonOpenArchitect final : public ServerPacket
    {
    public:
        GarrisonOpenArchitect() : ServerPacket(SMSG_GARRISON_OPEN_ARCHITECT, 8) { }
        ObjectGuid NpcGUID;
    private:
        void WritePayload() override;
    };

    class GarrisonOpenMissionNpcResponse final : public ServerPacket
    {
    public:
        GarrisonOpenMissionNpcResponse() : ServerPacket(SMSG_GARRISON_OPEN_MISSION_NPC, 8) { }
        ObjectGuid NpcGUID;
    private:
        void WritePayload() override;
    };

    class GarrisonRemoveFollowerResult final : public ServerPacket
    {
    public:
        GarrisonRemoveFollowerResult() : ServerPacket(SMSG_GARRISON_REMOVE_FOLLOWER_RESULT, 16) { }
        uint64 FollowerDBID = 0;
        int32 Result = 0;
        int32 Destroyed = 0;
    private:
        void WritePayload() override;
    };

    class GarrisonFollowerChangedXP final : public ServerPacket
    {
    public:
        GarrisonFollowerChangedXP() : ServerPacket(SMSG_GARRISON_FOLLOWER_CHANGED_XP, 128) { }
        GarrisonFollower Follower;
        GarrisonFollower Follower2;
        int32 Result = 0;
        uint32 TotalXp = 0;
    private:
        void WritePayload() override;
    };

    class GarrisonNumFollowerActivationsRemaining final : public ServerPacket
    {
    public:
        GarrisonNumFollowerActivationsRemaining() : ServerPacket(SMSG_GARRISON_NUM_FOLLOWER_ACTIVATIONS_REMAINING, 4) { }
        int32 Amount = 0;
    private:
        void WritePayload() override;
    };

    class GarrisonRemoveFollowerFromBuildingResult final : public ServerPacket
    {
    public:
        GarrisonRemoveFollowerFromBuildingResult() : ServerPacket(SMSG_GARRISON_REMOVE_FOLLOWER_FROM_BUILDING_RESULT, 12) { }
        uint64 FollowerDBID = 0;
        int32 Result = 0;
    private:
        void WritePayload() override;
    };

    class GarrisonMissionListUpdate final : public ServerPacket
    {
    public:
        GarrisonMissionListUpdate() : ServerPacket(SMSG_GARRISON_MISSION_LIST_UPDATE, 16) { }
        uint32 Result = 0;
        std::vector<uint32> updatedMissionRecIDs;
        bool openMissionNpc = false;
    private:
        void WritePayload() override;
    };

    // SMSG_SET_CURRENCY: a 3.3.5 client has no currency 824, the garrison UI reads it from here.
    class SetCurrency final : public ServerPacket
    {
    public:
        SetCurrency() : ServerPacket(SMSG_SET_CURRENCY, 12) { }
        uint32 Type = 0;
        int32 Quantity = 0;
        bool SuppressChatLog = false;
    private:
        void WritePayload() override;
    };

    class StreamingMovie final : public ServerPacket
    {
    public:
        StreamingMovie() : ServerPacket(SMSG_STREAMING_MOVIE, 8) { }
        std::vector<uint32> MovieIDs;
    private:
        void WritePayload() override;
    };
}

#endif
