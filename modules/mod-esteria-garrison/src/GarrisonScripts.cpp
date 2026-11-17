/*
 * AzerothCore glue for the UWoW garrison: WorldSession::HandleGarrison* (UWoW GarrisonHandler.cpp) behind the
 * CMSG_ESTERIA_GARRISON_* opcodes, the Player::GetGarrison lifetime, GarrisonMap's per-owner instance, the npcflag2
 * interactions the 6.x client started on its own, and the garrison_general.cpp spell scripts.
 */

#include "Chat.h"
#include "ChatCommand.h"
#include "Config.h"
#include "Creature.h"
#include "CreatureTextMgr.h"
#include "DatabaseEnv.h"
#include "Field.h"
#include "QueryResult.h"
#include "EsteriaGarrisonHooks.h"
#include "GameObject.h"
#include "Garrison.h"
#include "GarrisonMgr.h"
#include "GossipDef.h"
#include "InstanceSaveMgr.h"
#include "Item.h"
#include "Log.h"
#include "MapMgr.h"
#include "ObjectMgr.h"
#include "Opcodes.h"
#include "Player.h"
#include "RBAC.h"
#include "ScriptMgr.h"
#include "ScriptedGossip.h"
#include "Spell.h"
#include "SpellMgr.h"
#include "WorldPacket.h"
#include "WorldSession.h"

namespace
{
    bool s_enabled = false;
    bool s_initialized = false;

    // gossip_menu_option rows of OptionType 22 (GOSSIP_OPTION_GARRISON_SHIPMENT), which 3.3.5 has no case for
    constexpr uint32 GOSSIP_SENDER_GARRISON_SHIPMENT = 0x4752;

    enum GarrisonSpells
    {
        SPELL_GARRISON_HEARTHSTONE = 171253,
        SPELL_GARRISON_CACHE_LOOT  = 173847,
    };

    enum GarrisonCacheData
    {
        NPC_CACHE_QUEST_TALKER = 80223,
        QUEST_CACHE_ALLIANCE   = 35176,
        QUEST_CACHE_HORDE      = 34824,
    };

    struct ShipmentGossipOption
    {
        uint32 OptionID = 0;
        uint8 OptionIcon = 0;
        std::string OptionText;
        uint32 OptionBroadcastTextID = 0;
    };

    std::unordered_map<uint32 /*menuId*/, std::vector<ShipmentGossipOption>> s_shipmentGossip;

    void LoadShipmentGossip()
    {
        s_shipmentGossip.clear();
        if (QueryResult result = WorldDatabase.Query("SELECT MenuID, OptionID, OptionIcon, OptionText, OptionBroadcastTextID FROM garrison_gossip_shipment_option"))
        {
            do
            {
                Field* fields = result->Fetch();
                ShipmentGossipOption& option = s_shipmentGossip[fields[0].Get<uint32>()].emplace_back();
                option.OptionID = fields[1].Get<uint32>();
                option.OptionIcon = fields[2].Get<uint8>();
                option.OptionText = fields[3].Get<std::string>();
                option.OptionBroadcastTextID = fields[4].Get<uint32>();
            } while (result->NextRow());
        }
    }

    // Player::GetNPCIfCanInteractWith(guid, UNIT_NPC_FLAG_NONE, npcFlag2)
    Creature* GetNPCIfCanInteractWith(Player* player, ObjectGuid const& guid, uint32 npcFlag2)
    {
        Creature* creature = player->GetNPCIfCanInteractWith(guid, UNIT_NPC_FLAG_NONE);
        if (!creature || !(sGarrisonMgr.GetNpcFlags2(creature->GetEntry()) & npcFlag2))
            return nullptr;
        return creature;
    }

    void HandleAction(Player* player, WorldPacket& packet)
    {
        using namespace WorldPackets::Garrison;

        // The addon sends one byte and two ints. The retail-shaped packets below are longer.
        if (packet.size() - packet.rpos() == 9)
        {
            uint8 op = 0;
            uint32 a = 0;
            uint32 b = 0;
            packet >> op >> a >> b;

            Garrison* garrison = GarrisonRegistry::Get(player);
            if (!garrison && op == 1)
            {
                GarrisonRegistry::Create(player, player->GetTeamId() == TEAM_ALLIANCE ? SITE_ID_GARRISON_ALLIANCE : SITE_ID_GARRISON_HORDE);
                garrison = GarrisonRegistry::Get(player);
            }
            if (garrison)
                garrison->HandleUiAction(op, a, b);
            return;
        }

        uint16 opcode = 0;
        packet >> opcode;
        Garrison* garrison = GarrisonRegistry::Get(player);

        switch (GarrisonClientOpcode(opcode))
        {
            case CMSG_GET_GARRISON_INFO:
                if (garrison)
                    garrison->SendInfo();
                break;
            case CMSG_GARRISON_PURCHASE_BUILDING:
            {
                GarrisonPurchaseBuilding data(packet);
                data.Read();
                if (!GetNPCIfCanInteractWith(player, data.NpcGUID, UNIT_NPC_FLAG2_GARRISON_ARCHITECT))
                    return;
                if (garrison)
                    garrison->PlaceBuilding(data.PlotInstanceID, data.BuildingID);
                break;
            }
            case CMSG_GARRISON_CANCEL_CONSTRUCTION:
            {
                GarrisonCancelConstruction data(packet);
                data.Read();
                if (!GetNPCIfCanInteractWith(player, data.NpcGUID, UNIT_NPC_FLAG2_GARRISON_ARCHITECT))
                    return;
                if (garrison)
                    garrison->CancelBuildingConstruction(data.PlotInstanceID);
                break;
            }
            case CMSG_GARRISON_REQUEST_BLUEPRINT_AND_SPECIALIZATION_DATA:
                if (garrison)
                    garrison->SendBlueprintAndSpecializationData();
                break;
            case CMSG_GARRISON_GET_BUILDING_LANDMARKS:
                if (garrison)
                    garrison->SendBuildingLandmarks(player);
                break;
            case CMSG_GARRISON_MISSION_BONUS_ROLL:
            {
                GarrisonMissionBonusRoll data(packet);
                data.Read();
                if (!GetNPCIfCanInteractWith(player, data.NpcGUID, UNIT_NPC_FLAG2_GARRISON_MISSION_NPC))
                    return;
                if (!sGarrMissionStore.LookupEntry(data.MissionRecID))
                    return;
                if (garrison)
                    if (Garrison::Mission* mission = garrison->GetMissionByRecID(data.MissionRecID))
                        if (mission->CanBonusRoll())
                            mission->BonusRoll(player);
                break;
            }
            case CMSG_GARRISON_REQUEST_LANDING_PAGE_SHIPMENT_INFO:
                if (garrison)
                    garrison->SendGarrisonShipmentLandingPage();
                break;
            case CMSG_GARRISON_CHECK_UPGRADEABLE:
                if (garrison)
                    garrison->SendGarrisonUpgradebleResult(player);
                break;
            case CMSG_GARRISON_START_MISSION:
            {
                GarrisonStartMission data(packet);
                data.Read();
                if (!GetNPCIfCanInteractWith(player, data.NpcGUID, UNIT_NPC_FLAG2_GARRISON_MISSION_NPC))
                    return;
                if (!sGarrMissionStore.LookupEntry(data.MissionRecID))
                    return;
                if (garrison)
                {
                    if (Garrison::Mission* mission = garrison->GetMissionByRecID(data.MissionRecID))
                    {
                        mission->CurrentFollowerDBIDs.insert(mission->CurrentFollowerDBIDs.begin(), data.FollowerDBIDs.begin(), data.FollowerDBIDs.end());
                        if (mission->CanStart(player))
                            mission->Start(player);
                    }
                }
                break;
            }
            case CMSG_GARRISON_COMPLETE_MISSION:
            {
                GarrisonCompleteMission data(packet);
                data.Read();
                if (!GetNPCIfCanInteractWith(player, data.NpcGUID, UNIT_NPC_FLAG2_GARRISON_MISSION_NPC))
                    return;
                if (!sGarrMissionStore.LookupEntry(data.MissionRecID))
                    return;
                if (garrison)
                {
                    if (Garrison::Mission* mission = garrison->GetMissionByRecID(data.MissionRecID))
                    {
                        if (mission->PacketInfo.MissionState != MISSION_STATE_IN_PROGRESS)
                            return;
                        if (mission->PacketInfo.StartTime + mission->PacketInfo.MissionDuration <= time(nullptr))
                            mission->Complete(player);
                    }
                }
                break;
            }
            case CMSG_CREATE_SHIPMENT:
            {
                CreateShipment data(packet);
                data.Read();
                if (!GetNPCIfCanInteractWith(player, data.NpcGUID, UNIT_NPC_FLAG2_SHIPMENT_ORDER))
                    return;
                if (garrison)
                    garrison->CreateShipment(data.NpcGUID, data.Count);
                break;
            }
            case CMSG_GARRISON_REQUEST_SHIPMENT_INFO:
            {
                GarrisonRequestShipmentInfo data(packet);
                data.Read();
                if (!GetNPCIfCanInteractWith(player, data.NpcGUID, UNIT_NPC_FLAG2_SHIPMENT_ORDER))
                    return;
                if (garrison)
                    garrison->SendShipmentInfo(data.NpcGUID);
                break;
            }
            case CMSG_OPEN_MISSION_NPC:
            {
                GarrisonOpenMissionNpc data(packet);
                data.Read();
                if (!GetNPCIfCanInteractWith(player, data.NpcGUID, UNIT_NPC_FLAG2_GARRISON_MISSION_NPC))
                    return;
                if (garrison)
                    garrison->SendMissionListUpdate(true);
                break;
            }
            case CMSG_COMPLETE_ALL_READY_SHIPMENTS:
            {
                CompleteAllReadyShipments data(packet);
                data.Read();
                Map* map = player->FindMap();
                if (!map)
                    return;
                GameObject* go = map->GetGameObject(data.GUID);
                if (!go)
                    return;
                if (garrison)
                    garrison->CompleteShipments(go);
                break;
            }
            case CMSG_UPGRADE_GARRISON:
            {
                UpgradeGarrison data(packet);
                data.Read();
                if (!GetNPCIfCanInteractWith(player, data.NpcGUID, UNIT_NPC_FLAG2_GARRISON_ARCHITECT))
                    return;
                if (garrison)
                    garrison->Upgrade();
                break;
            }
            // UWoW leaves these three empty
            case CMSG_GARRISON_SET_FOLLOWER_INACTIVE:
            case CMSG_GARRISON_REMOVE_FOLLOWER_FROM_BUILDING:
            case CMSG_GARRISON_ASSIGN_FOLLOWER_TO_BUILDING:
            default:
                break;
        }
    }

    void HandlePacket(WorldSession* session, WorldPacket& packet)
    {
        Player* player = session->GetPlayer();
        if (!s_enabled || !s_initialized || !player || !player->IsInWorld())
        {
            packet.rfinish();
            return;
        }

        try
        {
            if (packet.GetOpcode() == CMSG_ESTERIA_GARRISON_HELLO)
            {
                if (Garrison* garrison = GarrisonRegistry::Get(player))
                    garrison->SendWindow(0, 0);
            }
            else
                HandleAction(player, packet);
        }
        catch (ByteBufferException const&)
        {
            LOG_DEBUG("module", "garrison: malformed packet from {}", player->GetName());
        }
        packet.rfinish();
    }

    // GarrisonMap: one instance of the tier map per owner
    uint32 PickInstance(Player* player, uint32 mapId)
    {
        if (!s_enabled || !s_initialized || !GarrisonMgr::IsGarrisonMap(mapId))
            return 0;

        Garrison* garrison = GarrisonRegistry::Get(player);
        if (!garrison || garrison->GetGarrisonMapID() != int32(mapId))
            return 0;

        if (!garrison->GetInstanceId() || !sMapMgr->FindMap(mapId, garrison->GetInstanceId()))
            garrison->SetInstanceId(sMapMgr->GenerateInstanceId());

        if (InstancePlayerBind* bind = sInstanceSaveMgr->PlayerGetBoundInstance(player->GetGUID(), mapId, DUNGEON_DIFFICULTY_NORMAL))
            if (!bind->perm && bind->save && bind->save->GetInstanceId() != garrison->GetInstanceId())
                sInstanceSaveMgr->PlayerUnbindInstance(player->GetGUID(), mapId, DUNGEON_DIFFICULTY_NORMAL, true, player);

        return garrison->GetInstanceId();
    }

    void SetHooks()
    {
        EsteriaGarrisonHooks::Packet = s_enabled && s_initialized ? &HandlePacket : nullptr;
        EsteriaGarrisonHooks::Instance = s_enabled && s_initialized ? &PickInstance : nullptr;
    }

    // UWoW spell_garrison_cache_loot
    bool LootGarrisonCache(Player* player, Garrison* garrison)
    {
        if (!garrison->GetResNumber())
            return true;

        GarrisonCurrency::Modify(player, CURRENCY_TYPE_GARRISON_RESOURCES, garrison->GetResNumber(), false);
        garrison->UpdateResTakenTime();

        if (player->GetQuestStatus(QUEST_CACHE_ALLIANCE) == QUEST_STATUS_INCOMPLETE ||
            player->GetQuestStatus(QUEST_CACHE_HORDE) == QUEST_STATUS_INCOMPLETE)
            if (Creature* talker = player->FindNearestCreature(NPC_CACHE_QUEST_TALKER, 100.0f))
                sCreatureTextMgr->SendChat(talker, 0, player);
        return true;
    }

    // Spell::Effect* for a spell the 3.3.5 client has no record of; true when the garrison handled it
    bool CastGarrisonSpell(Player* player, Garrison* garrison, uint32 spellId)
    {
        switch (spellId)
        {
            case SPELL_GARRISON_HEARTHSTONE:
                if (garrison->GetGarrisonMapID() == -1)
                    return true;
                garrison->Enter();
                return true;
            case SPELL_GARRISON_CACHE_LOOT:
                return LootGarrisonCache(player, garrison);
            default:
                return garrison->HandleSpell(spellId);
        }
    }
}

class garrison_world : public WorldScript
{
public:
    garrison_world() : WorldScript("garrison_world", { WORLDHOOK_ON_AFTER_CONFIG_LOAD, WORLDHOOK_ON_STARTUP, WORLDHOOK_ON_SHUTDOWN }) { }

    void OnAfterConfigLoad(bool /*reload*/) override
    {
        s_enabled = sConfigMgr->GetOption<bool>("EsteriaGarrison.Enable", false);
        SetHooks();
    }

    void OnStartup() override
    {
        if (!s_enabled)
            return;

        sGarrisonMgr.Initialize();
        LoadShipmentGossip();

        // The client loads the saved map before OnPlayerLogin can move the player, and a garrison map without its
        // owner's garrison crashes it (CMap::LoadWdt) when the tier WDT is missing.
        CharacterDatabase.DirectExecute("UPDATE characters c JOIN character_homebind h ON h.guid = c.guid "
            "LEFT JOIN character_garrison g ON g.guid = c.guid "
            "SET c.map = h.mapId, c.zone = h.zoneId, c.position_x = h.posX, c.position_y = h.posY, c.position_z = h.posZ, c.instance_id = 0 "
            "WHERE c.online = 0 AND c.map IN (1152, 1153, 1158, 1159, 1330, 1331) AND (g.guid IS NULL OR c.map <> CASE g.siteLevelId "
            "WHEN 5 THEN 1158 WHEN 444 THEN 1331 WHEN 6 THEN 1159 WHEN 258 THEN 1152 WHEN 445 THEN 1330 WHEN 259 THEN 1153 ELSE 0 END)");
        s_initialized = true;
        SetHooks();
    }

    void OnShutdown() override
    {
        EsteriaGarrisonHooks::Packet = nullptr;
        EsteriaGarrisonHooks::Instance = nullptr;
    }
};

class garrison_player : public PlayerScript
{
public:
    garrison_player() : PlayerScript("garrison_player", { PLAYERHOOK_ON_LOGIN, PLAYERHOOK_ON_LOGOUT, PLAYERHOOK_ON_SAVE, PLAYERHOOK_ON_UPDATE,
        PLAYERHOOK_ON_DELETE_FROM_DB, PLAYERHOOK_ON_LOOT_ITEM, PLAYERHOOK_ON_MAP_CHANGED }) { }

    void OnPlayerLogin(Player* player) override
    {
        if (!s_initialized)
            return;

        GarrisonCurrency::Load(player);
        GarrisonRegistry::Load(player);
        GarrisonCurrency::Send(player, CURRENCY_TYPE_GARRISON_RESOURCES);

        // Esteria: every character owns a garrison from creation; the Housing UI opens it
        if (!GarrisonRegistry::Get(player))
            GarrisonRegistry::Create(player, player->GetTeamId() == TEAM_ALLIANCE ? SITE_ID_GARRISON_ALLIANCE : SITE_ID_GARRISON_HORDE, false);

        if (!GarrisonMgr::IsGarrisonMap(player->GetMapId()))
            return;

        Garrison* garrison = GarrisonRegistry::Get(player);
        if (garrison && garrison->GetGarrisonMapID() == int32(player->GetMapId()))
            return;

        player->TeleportTo(player->m_homebindMapId, player->m_homebindX, player->m_homebindY, player->m_homebindZ, player->GetOrientation());
    }

    void OnPlayerLogout(Player* player) override
    {
        if (!s_initialized)
            return;

        GarrisonRegistry::Unload(player);
        GarrisonCurrency::Unload(player);
    }

    void OnPlayerSave(Player* player) override
    {
        if (!s_initialized)
            return;

        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        if (Garrison* garrison = GarrisonRegistry::Get(player))
            garrison->SaveToDB(trans);
        GarrisonCurrency::Save(player, trans);
        CharacterDatabase.CommitTransaction(trans);
    }

    void OnPlayerDeleteFromDB(CharacterDatabaseTransaction trans, uint32 guid) override
    {
        Garrison::DeleteFromDB(guid, trans);
        trans->Append("DELETE FROM character_garrison_currency WHERE guid = {}", guid);
    }

    void OnPlayerUpdate(Player* player, uint32 diff) override
    {
        if (!s_initialized)
            return;

        if (Garrison* garrison = GarrisonRegistry::Get(player))
            garrison->Update(diff);
    }

    // Player::StoreLootItem -> Garrison::FreeShipmentChest(loot->shipmentBuildingType)
    void OnPlayerLootItem(Player* player, Item* /*item*/, uint32 /*count*/, ObjectGuid lootguid) override
    {
        if (!s_initialized || !lootguid.IsGameObject())
            return;

        if (Garrison* garrison = GarrisonRegistry::Get(player))
            if (uint32 buildingType = garrison->GetShipmentChestBuildingType(lootguid))
                garrison->FreeShipmentChest(buildingType);
    }

    void OnPlayerMapChanged(Player* player) override
    {
        if (!s_initialized)
            return;

        if (Garrison* garrison = GarrisonRegistry::Get(player))
            garrison->SendRemoteInfo();
    }
};

class garrison_map : public AllMapScript
{
public:
    garrison_map() : AllMapScript("garrison_map", { ALLMAPHOOK_ON_PLAYER_ENTER_ALL, ALLMAPHOOK_ON_DESTROY_INSTANCE }) { }

    void OnPlayerEnterAll(Map* map, Player* player) override
    {
        if (!s_initialized || !GarrisonMgr::IsGarrisonMap(map->GetId()))
            return;

        Garrison* garrison = GarrisonRegistry::Get(player);
        if (!garrison || garrison->GetGarrisonMapID() != int32(map->GetId()))
            return;

        garrison->SetInstanceId(map->GetInstanceId());
        garrison->OnMapLoaded(map);
    }

    void OnDestroyInstance(MapInstanced* /*mapInstanced*/, Map* map) override
    {
        if (!s_initialized || !GarrisonMgr::IsGarrisonMap(map->GetId()))
            return;

        uint32 instanceId = map->GetInstanceId();
        GarrisonRegistry::ForEach([instanceId](Garrison& garrison)
        {
            if (garrison.GetInstanceId() == instanceId)
                garrison.OnMapUnloaded();
        });
    }
};

// The 6.x client opened these windows itself from npcflag2; a 3.3.5 client only sends gossip hello
class garrison_creature : public AllCreatureScript
{
public:
    garrison_creature() : AllCreatureScript("garrison_creature") { }

    bool CanCreatureGossipHello(Player* player, Creature* creature) override
    {
        if (!s_initialized)
            return false;

        uint32 flags2 = sGarrisonMgr.GetNpcFlags2(creature->GetEntry());
        CreatureTemplate const* info = creature->GetCreatureTemplate();
        bool architect = (flags2 & UNIT_NPC_FLAG2_GARRISON_ARCHITECT) != 0
            || (info && (info->IconName == "architect" || info->SubName == "Garrison Architect"));
        if (!flags2 && !architect)
            return false;

        Garrison* garrison = GarrisonRegistry::Get(player);
        if (!garrison && architect)
        {
            GarrisonRegistry::Create(player, player->GetTeamId() == TEAM_ALLIANCE ? SITE_ID_GARRISON_ALLIANCE : SITE_ID_GARRISON_HORDE);
            garrison = GarrisonRegistry::Get(player);
        }
        if (!garrison)
            return false;

        if (architect)
        {
            garrison->SendWindow(0, 1);
            return true;
        }

        if (flags2 & UNIT_NPC_FLAG2_GARRISON_MISSION_NPC)
        {
            garrison->OfferTableMissions();
            garrison->SendWindow(0, 2);
            return true;
        }

        if (flags2 & UNIT_NPC_FLAG2_SHIPMENT_ORDER)
        {
            uint32 menuId = creature->GetCreatureTemplate()->GossipMenuId;
            if (creature->IsQuestGiver())
                player->PrepareQuestMenu(creature->GetGUID());
            player->PrepareGossipMenu(creature, menuId, true);

            if (garrison->canAddShipmentOrder(creature))
            {
                auto itr = s_shipmentGossip.find(menuId);
                if (itr == s_shipmentGossip.end())
                    itr = s_shipmentGossip.find(0);
                if (itr != s_shipmentGossip.end())
                {
                    LocaleConstant locale = player->GetSession()->GetSessionDbLocaleIndex();
                    for (ShipmentGossipOption const& option : itr->second)
                    {
                        std::string text = option.OptionText;
                        if (option.OptionBroadcastTextID)
                            if (BroadcastText const* bct = sObjectMgr->GetBroadcastText(option.OptionBroadcastTextID))
                                text = bct->GetText(locale, player->getGender());
                        player->PlayerTalkClass->GetGossipMenu().AddMenuItem(-1, option.OptionIcon, text, GOSSIP_SENDER_GARRISON_SHIPMENT, option.OptionID, "", 0);
                    }
                }
            }

            player->SendPreparedGossip(creature);
            return true;
        }

        return false;
    }

    bool CanCreatureGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 /*action*/) override
    {
        if (!s_initialized || sender != GOSSIP_SENDER_GARRISON_SHIPMENT)
            return false;

        CloseGossipMenuFor(player);
        if (Garrison* garrison = GarrisonRegistry::Get(player))
            garrison->OnGossipSelect(creature);
        return true;
    }

    bool CanCreatureQuestReward(Player* player, Creature* /*creature*/, Quest const* quest, uint32 /*opt*/) override
    {
        if (s_initialized)
            if (Garrison* garrison = GarrisonRegistry::Get(player))
                garrison->OnQuestReward(quest->GetQuestId());
        return false;
    }
};

class garrison_gameobject : public AllGameObjectScript
{
public:
    garrison_gameobject() : AllGameObjectScript("garrison_gameobject") { }

    bool CanGameObjectGossipHello(Player* player, GameObject* go) override
    {
        if (!s_initialized || !GarrisonMgr::IsGarrisonMap(go->GetMapId()))
            return false;

        Garrison* garrison = GarrisonRegistry::Get(player);
        if (!garrison || garrison->GetInstanceId() != go->GetInstanceId())
            return false;

        // Player::SendLoot returns early for GAMEOBJECT_TYPE_GARRISON_SHIPMENT; Garrison::CompleteShipments loots it
        if (sGarrisonMgr.GetWoDGameObjectType(go->GetEntry()) == GAMEOBJECT_TYPE_GARRISON_SHIPMENT)
        {
            garrison->CompleteShipments(go);
            return true;
        }

        if (go->GetGoType() != GAMEOBJECT_TYPE_GOOBER)
            return false;

        uint32 spellId = go->GetGOInfo()->goober.spellId;
        if (Garrison::Plot* plot = garrison->GetPlotByFinalizer(go->GetGUID()))
        {
            if (!spellId || !garrison->HandleSpell(spellId))
                garrison->ActivateBuilding(plot->PacketInfo.GarrPlotInstanceID);
            return true;
        }

        if (spellId && !sSpellMgr->GetSpellInfo(spellId) && CastGarrisonSpell(player, garrison, spellId))
            return true;

        return false;
    }

    bool CanGameObjectQuestReward(Player* player, GameObject* /*go*/, Quest const* quest, uint32 /*opt*/) override
    {
        if (s_initialized)
            if (Garrison* garrison = GarrisonRegistry::Get(player))
                garrison->OnQuestReward(quest->GetQuestId());
        return false;
    }
};

// Blueprints, follower contracts and the garrison hearthstone cast spells the 3.3.5 client does not have
class garrison_item : public AllItemScript
{
public:
    garrison_item() : AllItemScript("garrison_item") { }

    bool CanItemUse(Player* player, Item* item, SpellCastTargets const& /*targets*/) override
    {
        if (!s_initialized)
            return false;

        std::vector<uint32> const* spells = sGarrisonMgr.GetItemSpells(item->GetEntry());
        if (!spells)
            return false;

        Garrison* garrison = GarrisonRegistry::Get(player);
        if (!garrison)
            return false;

        bool handled = false;
        for (uint32 spellId : *spells)
            handled |= CastGarrisonSpell(player, garrison, spellId);

        if (handled && item->GetTemplate()->Spells[0].SpellCharges < 0)
        {
            uint32 count = 1;
            player->DestroyItemCount(item, count, true);
        }
        return handled;
    }
};

using namespace Acore::ChatCommands;

class garrison_commandscript : public CommandScript
{
public:
    garrison_commandscript() : CommandScript("garrison_commandscript") { }

    ChatCommandTable GetCommands() const override
    {
        static ChatCommandTable garrisonTable =
        {
            { "create",    HandleCreate,    rbac::RBAC_PERM_COMMAND_HELP, Console::No },
            { "enter",     HandleEnter,     rbac::RBAC_PERM_COMMAND_HELP, Console::No },
            { "leave",     HandleLeave,     rbac::RBAC_PERM_COMMAND_HELP, Console::No },
            { "status",    HandleStatus,    rbac::RBAC_PERM_COMMAND_HELP, Console::No },
            { "upgrade",   HandleUpgrade,   rbac::RBAC_PERM_COMMAND_GM,   Console::No },
            { "downgrade", HandleDowngrade, rbac::RBAC_PERM_COMMAND_GM,   Console::No },
            { "delete",    HandleDelete,    rbac::RBAC_PERM_COMMAND_GM,   Console::No },
            { "reset",     HandleReset,     rbac::RBAC_PERM_COMMAND_GM,   Console::No },
            { "blueprint", HandleBlueprint, rbac::RBAC_PERM_COMMAND_GM,   Console::No },
            { "place",     HandlePlace,     rbac::RBAC_PERM_COMMAND_GM,   Console::No },
            { "follower",  HandleFollower,  rbac::RBAC_PERM_COMMAND_GM,   Console::No },
            { "mission",   HandleMission,   rbac::RBAC_PERM_COMMAND_GM,   Console::No },
            { "resources", HandleResources, rbac::RBAC_PERM_COMMAND_GM,   Console::No },
            { "spell",     HandleSpell,     rbac::RBAC_PERM_COMMAND_GM,   Console::No },
        };
        static ChatCommandTable table =
        {
            { "garrison", garrisonTable },
        };
        return table;
    }

    static Garrison* GetGarrison(ChatHandler* handler)
    {
        if (!s_initialized)
        {
            handler->SendSysMessage("Garrison is disabled.");
            return nullptr;
        }
        Garrison* garrison = GarrisonRegistry::Get(handler->GetSession()->GetPlayer());
        if (!garrison)
            handler->SendSysMessage("No garrison yet: .garrison create");
        return garrison;
    }

    // SPELL_EFFECT_CREATE_GARRISON from the Draenor intro quest; there is no such quest on 3.3.5
    static bool HandleCreate(ChatHandler* handler)
    {
        if (!s_initialized)
        {
            handler->SendSysMessage("Garrison is disabled.");
            return false;
        }
        Player* player = handler->GetSession()->GetPlayer();
        if (GarrisonRegistry::Get(player))
        {
            handler->SendSysMessage("You already have a garrison.");
            return false;
        }
        GarrisonRegistry::Create(player, player->GetTeamId() == TEAM_ALLIANCE ? SITE_ID_GARRISON_ALLIANCE : SITE_ID_GARRISON_HORDE);
        return true;
    }

    static bool HandleEnter(ChatHandler* handler)
    {
        if (Garrison* garrison = GetGarrison(handler))
            garrison->Enter();
        return true;
    }

    static bool HandleLeave(ChatHandler* handler)
    {
        if (Garrison* garrison = GetGarrison(handler))
            garrison->Leave();
        return true;
    }

    static bool HandleStatus(ChatHandler* handler)
    {
        Garrison* garrison = GetGarrison(handler);
        if (!garrison)
            return true;
        Player* player = handler->GetSession()->GetPlayer();
        handler->PSendSysMessage("Garrison level {} (site level {}, map {}), {} resources, {} in the cache, {} blueprints, {} followers.",
            garrison->GetGarrisonLevel(), garrison->GetSiteLevel() ? garrison->GetSiteLevel()->ID : 0, garrison->GetGarrisonMapID(),
            GarrisonCurrency::Get(player, CURRENCY_TYPE_GARRISON_RESOURCES), garrison->GetResNumber(), garrison->GetCountOfBluePrints(),
            garrison->GetCountOFollowers());
        for (Garrison::Plot* plot : garrison->GetPlots())
            if (plot->BuildingInfo.PacketInfo)
                handler->PSendSysMessage("  plot {}: building {}{}", plot->PacketInfo.GarrPlotInstanceID, plot->BuildingInfo.PacketInfo->GarrBuildingID,
                    plot->BuildingInfo.PacketInfo->Active ? "" : " (under construction)");
        return true;
    }

    static bool HandleUpgrade(ChatHandler* handler)
    {
        if (Garrison* garrison = GetGarrison(handler))
            garrison->Upgrade();
        return true;
    }

    static bool HandleDowngrade(ChatHandler* handler)
    {
        if (Garrison* garrison = GetGarrison(handler))
        {
            if (garrison->Downgrade())
                handler->PSendSysMessage("Garrison is now level {}.", garrison->GetGarrisonLevel());
            else
                handler->SendSysMessage("Garrison is already level 1.");
        }
        return true;
    }

    static bool HandleDelete(ChatHandler* handler)
    {
        if (GetGarrison(handler))
            GarrisonRegistry::Delete(handler->GetSession()->GetPlayer());
        return true;
    }

    // Wipe and start over: a fresh level 1 garrison with no resources, re-entered if the player is inside.
    static bool HandleReset(ChatHandler* handler)
    {
        Garrison* garrison = GetGarrison(handler);
        if (!garrison)
            return true;
        Player* player = handler->GetSession()->GetPlayer();
        uint32 siteId = garrison->GetSiteLevel()->SiteID;
        bool inside = GarrisonMgr::IsGarrisonMap(player->GetMapId());
        GarrisonRegistry::Delete(player);
        GarrisonCurrency::Modify(player, CURRENCY_TYPE_GARRISON_RESOURCES, -int32(GarrisonCurrency::Get(player, CURRENCY_TYPE_GARRISON_RESOURCES)));
        GarrisonRegistry::Create(player, siteId, inside);
        handler->SendSysMessage("Garrison wiped and recreated at level 1.");
        return true;
    }

    static bool HandleBlueprint(ChatHandler* handler, uint32 garrBuildingId)
    {
        if (Garrison* garrison = GetGarrison(handler))
            garrison->LearnBlueprint(garrBuildingId);
        return true;
    }

    static bool HandlePlace(ChatHandler* handler, uint32 garrPlotInstanceId, uint32 garrBuildingId)
    {
        if (Garrison* garrison = GetGarrison(handler))
            garrison->PlaceBuilding(garrPlotInstanceId, garrBuildingId);
        return true;
    }

    static bool HandleFollower(ChatHandler* handler, uint32 garrFollowerId)
    {
        if (Garrison* garrison = GetGarrison(handler))
            garrison->AddFollower(garrFollowerId);
        return true;
    }

    static bool HandleMission(ChatHandler* handler, uint32 missionRecId)
    {
        if (Garrison* garrison = GetGarrison(handler))
            garrison->AddMission(missionRecId);
        return true;
    }

    static bool HandleResources(ChatHandler* handler, int32 amount)
    {
        if (!GetGarrison(handler))
            return true;
        Player* player = handler->GetSession()->GetPlayer();
        GarrisonCurrency::Modify(player, CURRENCY_TYPE_GARRISON_RESOURCES, amount);
        handler->PSendSysMessage("Garrison resources: {}.", GarrisonCurrency::Get(player, CURRENCY_TYPE_GARRISON_RESOURCES));
        return true;
    }

    static bool HandleSpell(ChatHandler* handler, uint32 spellId)
    {
        if (Garrison* garrison = GetGarrison(handler))
            if (!CastGarrisonSpell(handler->GetSession()->GetPlayer(), garrison, spellId))
                handler->PSendSysMessage("Spell {} has no garrison effect.", spellId);
        return true;
    }
};

void AddSC_mod_esteria_garrison()
{
    new garrison_world();
    new garrison_player();
    new garrison_map();
    new garrison_creature();
    new garrison_gameobject();
    new garrison_item();
    new garrison_commandscript();
}
