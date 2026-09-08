/*
 * mod-mount-evolved - Ranger's War Horse
 * Full Feature Version - Rebuilt
 */

#include "Config.h"
#include "improved_bank.h"
#include "ScriptMgr.h"
#include "Player.h"
#include "Chat.h"
#include "ScriptedGossip.h"
#include "ScriptedCreature.h"
#include "Creature.h"
#include "GossipDef.h"
#include "DatabaseEnv.h"
#include "ObjectMgr.h"
#include "GameObject.h"
#include "ObjectAccessor.h"
#include "Vehicle.h"
#include "VehicleScript.h"
#include "SpellMgr.h"
#include "DBCStores.h"
#include "GameTime.h"
#include "SpellAuraDefines.h"
#include "Map.h"
#include "MotionMaster.h"
#include "SpellScript.h"
#include "Chat.h"
#include "Channel.h"

// Module configuration
struct LoyalSteedConfig
{
    bool     Enable             = true;
    bool     StorageEnable      = true;
    bool     FastTravelEnable   = true;
    uint32   MaxLocations       = 20;
    bool     ContinentOnly      = true;
    bool     CampEnable         = true;
    bool     AppearanceEnable   = true;
} sLoyalSteedConfig;

#define HORSE_NPC_ENTRY      900010

uint32 GetRaceDisplayId(uint8 race)
{
    switch (race)
    {
        case RACE_HUMAN:    return 8469;   // Warhorse
        case RACE_DWARF:    return 13340;  // Alterac Ram
        case RACE_GNOME:    return 6569;   // Blue Mechanostrider
        case RACE_NIGHTELF: return 6448;   // Striped Nightsaber
        case RACE_DRAENEI:  return 17906;  // Great Elite Elekk
        case RACE_ORC:      return 207;    // Riding Wolf
        case RACE_TROLL:    return 4806;   // Emerald Raptor
        case RACE_TAUREN:   return 11641;  // Brown Kodo
        case RACE_UNDEAD_PLAYER: return 5050;  // Skeletal Horse
        case RACE_BLOODELF: return 18696;  // Red Hawkstrider
        default:            return 8469;   // Default to Warhorse
    }
}
#define MAPLE_SEED_ITEM_ID   17034
#define DEFAULT_DISPLAY_ID   28918
#define MOUNTS_PER_PAGE      20
#define TRAVEL_PER_PAGE      20

enum HorseGossip
{
    GOSSIP_SADDLEBAGS        = 20,
    GOSSIP_FAST_TRAVEL       = 21,
    GOSSIP_MOUNT             = 22,
    GOSSIP_FOLLOW            = 23,
    GOSSIP_WAIT              = 24,
    GOSSIP_CAMP              = 25,
    GOSSIP_APPEARANCE        = 26,
    GOSSIP_PREV_MOUNT        = 27,
    GOSSIP_NEXT_MOUNT        = 28,
    GOSSIP_PREV_TRAVEL       = 29,
    GOSSIP_NEXT_TRAVEL       = 30,
    GOSSIP_REMEMBER_LOCATION = 31,
    GOSSIP_FORGET_LOCATION   = 32,
    GOSSIP_PREV_FORGET       = 33,
    GOSSIP_NEXT_FORGET       = 34,
    GOSSIP_MOUNT_BASE        = 100,
    GOSSIP_TRAVEL_BASE       = 500,
    GOSSIP_FORGET_BASE       = 800
};

struct MountInfo
{
    uint32 spellId;
    uint32 displayId;
    std::string name;
};

static const uint32 CAMPFIRE_ENTRY  = 29784;
static const uint32 TENT_ENTRY      = 19295;
static const uint32 LANTERN_ENTRY   = 179977;
static const uint32 BOW_ENTRY       = 19645;
static const uint32 PACK_ENTRY      = 161504;
static const uint32 MUG_ENTRY       = 181307;

void SafeRemoveControlled(Player* player, Creature* horse)
{
    if (!player || !horse) return;
    auto itr = player->m_Controlled.find(horse);
    if (itr != player->m_Controlled.end())
        player->m_Controlled.erase(itr);
}

void FullRemoveControlled(Player* player, Creature* horse)
{
    if (!player || !horse) return;
    SafeRemoveControlled(player, horse);
}

bool IsHorseOwner(Player* player, Creature* creature)
{
    if (!player || !creature) return false;
    // First check by saved horse GUID
    QueryResult result = CharacterDatabase.Query(
        "SELECT horse_guid FROM rangers_war_horse_owner WHERE owner_guid = {}",
        player->GetGUID().GetCounter());
    if (!result) return false;
    uint32 savedGuid = result->Fetch()[0].Get<uint32>();
    uint32 creatureGuid = creature->GetGUID().GetCounter();
    // If GUIDs match, ownership confirmed
    if (savedGuid == creatureGuid)
        return true;
    // If saved GUID is 0 (e.g. after login/death), check display ID and update GUID
    if (savedGuid == 0)
    {
        QueryResult dispResult = CharacterDatabase.Query(
            "SELECT display_id FROM rangers_war_horse_owner WHERE owner_guid = {}",
            player->GetGUID().GetCounter());
        if (!dispResult) return false;
        uint32 savedDisplayId = dispResult->Fetch()[0].Get<uint32>();
        if (creature->GetDisplayId() == savedDisplayId ||
            creature->GetNativeDisplayId() == savedDisplayId)
        {
            // Update horse_guid so future checks work
            CharacterDatabase.Execute(
                "UPDATE rangers_war_horse_owner SET horse_guid = {} WHERE owner_guid = {}",
                creatureGuid, player->GetGUID().GetCounter());
            return true;
        }
    }
    return false;
}

void DespawnCampsite(Creature* horse)
{
    if (!horse) return;
    std::vector<uint32> campEntries = { CAMPFIRE_ENTRY, TENT_ENTRY, LANTERN_ENTRY, BOW_ENTRY, PACK_ENTRY, MUG_ENTRY };
    for (uint32 entry : campEntries)
    {
        std::list<GameObject*> objs;
        GetGameObjectListWithEntryInGrid(objs, horse, entry, 15.0f);
        for (GameObject* go : objs)
        {
            go->SetRespawnTime(0);
            go->Delete();
        }
    }
}

void SpawnCampsite(Creature* horse)
{
    if (!horse) return;
    Map* map = horse->GetMap();
    if (!map) return;

    float hx = horse->GetPositionX();
    float hy = horse->GetPositionY();
    float ho = horse->GetOrientation();

    auto SpawnObj = [&](uint32 entry, float dx, float dy) {
        float x = hx + dx;
        float y = hy + dy;
        float z = map->GetHeight(x, y, horse->GetPositionZ() + 5.0f);
        horse->SummonGameObject(entry, x, y, z, ho, 0, 0, 0, 0, 0);
    };

    SpawnObj(CAMPFIRE_ENTRY,  -4.5f * std::cos(ho),  -4.5f * std::sin(ho));
    SpawnObj(TENT_ENTRY,      -8.0f * std::cos(ho),  -8.0f * std::sin(ho));
    SpawnObj(LANTERN_ENTRY,   -4.5f * std::cos(ho) + 2.0f * std::sin(ho),  -4.5f * std::sin(ho) - 2.0f * std::cos(ho));
    SpawnObj(BOW_ENTRY,       -4.5f * std::cos(ho) - 2.0f * std::sin(ho),  -4.5f * std::sin(ho) + 2.0f * std::cos(ho));
    SpawnObj(PACK_ENTRY,      -7.5f * std::cos(ho) + 1.5f * std::sin(ho), -7.5f * std::sin(ho) - 1.5f * std::cos(ho));
    SpawnObj(MUG_ENTRY,       -4.0f * std::cos(ho) - 0.8f * std::sin(ho), -4.0f * std::sin(ho) + 0.8f * std::cos(ho));
}

std::vector<MountInfo> GetPlayerMounts(Player* player)
{
    std::vector<MountInfo> mounts;
    for (uint32 spellId = 0; spellId < sSpellMgr->GetSpellInfoStoreSize(); ++spellId)
    {
        SpellInfo const* spellInfo = sSpellMgr->GetSpellInfo(spellId);
        if (!spellInfo) continue;
        if (!player->HasSpell(spellId)) continue;

        bool isMount = false;
        for (uint8 i = 0; i < MAX_SPELL_EFFECTS; ++i)
        {
            if (spellInfo->Effects[i].ApplyAuraName == SPELL_AURA_MOUNTED)
            {
                isMount = true;
                break;
            }
        }
        if (!isMount) continue;

        uint32 displayId = DEFAULT_DISPLAY_ID;
        for (uint8 i = 0; i < MAX_SPELL_EFFECTS; ++i)
        {
            if (spellInfo->Effects[i].ApplyAuraName == SPELL_AURA_MOUNTED)
            {
                uint32 creatureEntry = spellInfo->Effects[i].MiscValue;
                if (creatureEntry)
                {
                    if (CreatureTemplate const* cInfo = sObjectMgr->GetCreatureTemplate(creatureEntry))
                    {
                        if (CreatureModel const* model = cInfo->GetRandomValidModel())
                            displayId = model->CreatureDisplayID;
                        else if (!cInfo->Models.empty())
                            displayId = cInfo->Models[0].CreatureDisplayID;
                    }
                }
                break;
            }
        }

        mounts.push_back({ spellId, displayId, spellInfo->SpellName[0] });
    }
    return mounts;
}

// Forward declarations
struct npc_rangers_war_horse_AI;

Creature* SummonHorseForPlayer(Player* player, uint32 savedDisplayId)
{
    if (!player) return nullptr;

    // Despawn ALL existing horses for this player before spawning a new one
    std::list<Creature*> existing;
    player->GetCreatureListWithEntryInGrid(existing, HORSE_NPC_ENTRY, 200.0f);
    for (Creature* old : existing)
        old->DespawnOrUnsummon();

    // Check if horse should spawn at camp position
    QueryResult campCheck = CharacterDatabase.Query(
        "SELECT is_camping, camp_x, camp_y, camp_z, camp_o, camp_map FROM rangers_war_horse_owner WHERE owner_guid = {}",
        player->GetGUID().GetCounter());
    bool isCamping = false;
    bool hasCampsite = false;
    float campX = 0, campY = 0, campZ = 0, campO = 0;
    uint32 campMap = 0;
    if (campCheck)
    {
        uint8 campState = campCheck->Fetch()[0].Get<uint8>();
        isCamping = campState > 0;
        hasCampsite = campState == 2;
        campX = campCheck->Fetch()[1].Get<float>();
        campY = campCheck->Fetch()[2].Get<float>();
        campZ = campCheck->Fetch()[3].Get<float>();
        campO = campCheck->Fetch()[4].Get<float>();
        campMap = campCheck->Fetch()[5].Get<uint32>();
    }

    float x, y, z;
    float o = player->GetOrientation();
    if (isCamping && campX != 0 && campMap == player->GetMapId())
    {
        x = campX;
        y = campY;
        z = campZ;
        o = campO;
    }
    else
        player->GetClosePoint(x, y, z, 2.0f);

    Creature* horse = player->SummonCreature(HORSE_NPC_ENTRY, x, y, z, o, TEMPSUMMON_MANUAL_DESPAWN);
    if (horse)
    {
        FullRemoveControlled(player, horse);
        if (savedDisplayId && savedDisplayId != DEFAULT_DISPLAY_ID)
            horse->SetDisplayId(savedDisplayId);
        horse->SetSpeed(MOVE_WALK, 1.0f);
        horse->SetSpeed(MOVE_RUN, 1.0f);
        if (isCamping)
        {
            horse->GetMotionMaster()->Clear();
            horse->GetMotionMaster()->MoveIdle();
            if (hasCampsite)
                SpawnCampsite(horse);
        }
        else
        {
            horse->GetMotionMaster()->MoveFollow(player, 4.0f, M_PI);
        }
        // Save new horse GUID to DB so IsHorseOwner works correctly
        CharacterDatabase.Execute(
            "UPDATE rangers_war_horse_owner SET horse_guid = {} WHERE owner_guid = {}",
            horse->GetGUID().GetCounter(), player->GetGUID().GetCounter());
    }
    return horse;
}

struct npc_rangers_war_horse_AI : public ScriptedAI
{
    npc_rangers_war_horse_AI(Creature* c) : ScriptedAI(c), _ownerGuid(ObjectGuid::Empty), _followTimer(0), _shouldFollow(false), _dismountX(0.0f), _dismountY(0.0f), _dismountZ(0.0f), _hasDismountPos(false), _isCamping(false) {}

    ObjectGuid _ownerGuid;
    uint32 _followTimer;
    bool _shouldFollow;
    float _dismountX;
    float _dismountY;
    float _dismountZ;
    bool _hasDismountPos;
    bool _isCamping;

    void SetOwner(ObjectGuid guid) { _ownerGuid = guid; }

    void SetCamping(bool camping)
    {
        _isCamping = camping;
        if (camping)
        {
            scheduler.CancelAll();
            me->GetMotionMaster()->Clear();
            me->GetMotionMaster()->MoveIdle();
        }
    }

    void TriggerFollow(float x, float y, float z)
    {
        if (_isCamping) return;
        _dismountX = x;
        _dismountY = y;
        _dismountZ = z;
        _hasDismountPos = true;
        _shouldFollow = false;

        scheduler.CancelAll();
        scheduler.Schedule(Milliseconds(600), [this](TaskContext /*ctx*/)
        {
            if (!_hasDismountPos) return;
            me->NearTeleportTo(_dismountX, _dismountY, _dismountZ, me->GetOrientation());
            me->GetMotionMaster()->Clear();
            me->SetSpeed(MOVE_RUN, 1.0f);
            me->SetSpeed(MOVE_WALK, 1.0f);
            if (Player* owner = ObjectAccessor::GetPlayer(*me, _ownerGuid))
                me->GetMotionMaster()->MoveFollow(owner, 4.0f, M_PI);
            _hasDismountPos = false;
        });
    }

    void UpdateAI(uint32 diff) override
    {
        scheduler.Update(diff);
    }
};

class npc_rangers_war_horse : public CreatureScript
{
public:
    npc_rangers_war_horse() : CreatureScript("npc_rangers_war_horse") { }

    CreatureAI* GetAI(Creature* creature) const override
    {
        return new npc_rangers_war_horse_AI(creature);
    }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        if (!sLoyalSteedConfig.Enable)
        {
            CloseGossipMenuFor(player);
            return true;
        }
        if (!IsHorseOwner(player, creature))
        {
            ChatHandler(player->GetSession()).PSendSysMessage("|cffff0000This is not your horse!|r");
            return true;
        }

        ClearGossipMenuFor(player);
        if (sLoyalSteedConfig.StorageEnable)
            AddGossipItemFor(player, GOSSIP_ICON_MONEY_BAG, "Ranger's Saddlebags",    GOSSIP_SENDER_MAIN, GOSSIP_SADDLEBAGS);
        if (sLoyalSteedConfig.FastTravelEnable)
        {
            AddGossipItemFor(player, GOSSIP_ICON_TAXI,      "Fast Travel",            GOSSIP_SENDER_MAIN, GOSSIP_FAST_TRAVEL);
            AddGossipItemFor(player, GOSSIP_ICON_CHAT,      "Remember this location", GOSSIP_SENDER_MAIN, GOSSIP_REMEMBER_LOCATION, "Remember your current location?", 0, false);
            AddGossipItemFor(player, GOSSIP_ICON_CHAT,      "Forget a location",      GOSSIP_SENDER_MAIN, GOSSIP_FORGET_LOCATION);
        }
        AddGossipItemFor(player, GOSSIP_ICON_BATTLE,    "Mount Up",                   GOSSIP_SENDER_MAIN, GOSSIP_MOUNT);
        AddGossipItemFor(player, GOSSIP_ICON_CHAT,      "Follow Me",                  GOSSIP_SENDER_MAIN, GOSSIP_FOLLOW);
        AddGossipItemFor(player, GOSSIP_ICON_CHAT,      "Wait Here",                  GOSSIP_SENDER_MAIN, GOSSIP_WAIT);
        if (sLoyalSteedConfig.CampEnable)
            AddGossipItemFor(player, GOSSIP_ICON_CHAT,  "Set Up Camp",                GOSSIP_SENDER_MAIN, GOSSIP_CAMP);
        if (sLoyalSteedConfig.AppearanceEnable)
            AddGossipItemFor(player, GOSSIP_ICON_INTERACT_1, "Change Appearance",     GOSSIP_SENDER_MAIN, GOSSIP_APPEARANCE);
        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 action) override
    {
        if (!IsHorseOwner(player, creature))
        {
            CloseGossipMenuFor(player);
            return true;
        }

        // Forward mod-improved-bank gossip actions
        ImprovedBank::PagedData& pagedData = sImprovedBank->GetPagedData(player);

        if (sender == GOSSIP_SENDER_MAIN + 1)
            return sImprovedBank->TakePagedDataAction(player, creature, action - GOSSIP_ACTION_INFO_DEF);

        if (sender == GOSSIP_SENDER_MAIN + 2)
            return sImprovedBank->AddPagedData(player, creature, action - GOSSIP_ACTION_INFO_DEF);

        if (sender == GOSSIP_SENDER_MAIN + 20)
        {
            sImprovedBank->BuildDepositItemCatalogue(player);
            return sImprovedBank->AddPagedData(player, creature, 0);
        }

        if (sender == GOSSIP_SENDER_MAIN + 21)
        {
            sImprovedBank->BuildItemSubClassesCatalogue(player, pagedData, ImprovedBank::PAGED_DATA_TYPE_DEPOSIT_SUBCLASS, pagedData.itemClass);
            return sImprovedBank->AddPagedData(player, creature, 0);
        }

        if (sender == GOSSIP_SENDER_MAIN + 22)
        {
            sImprovedBank->BuildWithdrawItemCatalogue(player);
            return sImprovedBank->AddPagedData(player, creature, 0);
        }

        if (sender == GOSSIP_SENDER_MAIN + 23)
        {
            sImprovedBank->BuildItemSubClassesCatalogue(player, pagedData, ImprovedBank::PAGED_DATA_TYPE_WITHDRAW_SUBCLASS, pagedData.itemClass);
            return sImprovedBank->AddPagedData(player, creature, 0);
        }

        ClearGossipMenuFor(player);

        if (action == GOSSIP_SADDLEBAGS)
        {
            ClearGossipMenuFor(player);
            AddGossipItemFor(player, GOSSIP_ICON_VENDOR,    "Deposit...",            GOSSIP_SENDER_MAIN, GOSSIP_ACTION_INFO_DEF + 10);
            AddGossipItemFor(player, GOSSIP_ICON_VENDOR,    "Deposit all reagents...", GOSSIP_SENDER_MAIN, GOSSIP_ACTION_INFO_DEF + 11);
            AddGossipItemFor(player, GOSSIP_ICON_MONEY_BAG, "Withdraw...",           GOSSIP_SENDER_MAIN, GOSSIP_ACTION_INFO_DEF + 12);
            AddGossipItemFor(player, GOSSIP_ICON_CHAT,      "< Back",                GOSSIP_SENDER_MAIN, GOSSIP_ACTION_INFO_DEF + 13);
            SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
            return true;
        }

        if (action == GOSSIP_ACTION_INFO_DEF + 10)
        {
            sImprovedBank->BuildDepositItemCatalogue(player);
            return sImprovedBank->AddPagedData(player, creature, 0);
        }

        if (action == GOSSIP_ACTION_INFO_DEF + 11)
        {
            uint32 count = 0;
            sImprovedBank->DepositAllReagents(player, &count);
            if (count == 0)
                ChatHandler(player->GetSession()).SendSysMessage("No reagents found to deposit.");
            else
                ChatHandler(player->GetSession()).PSendSysMessage("Deposited {} reagents.", count);
            CloseGossipMenuFor(player);
            return true;
        }

        if (action == GOSSIP_ACTION_INFO_DEF + 12)
        {
            sImprovedBank->BuildWithdrawItemCatalogue(player);
            return sImprovedBank->AddPagedData(player, creature, 0);
        }

        if (action == GOSSIP_ACTION_INFO_DEF + 13)
        {
            return OnGossipHello(player, creature);
        }

        // mod-improved-bank back button (page 0 back)
        if (action == GOSSIP_ACTION_INFO_DEF)
        {
            ClearGossipMenuFor(player);
            AddGossipItemFor(player, GOSSIP_ICON_VENDOR,    "Deposit...",              GOSSIP_SENDER_MAIN, GOSSIP_ACTION_INFO_DEF + 10);
            AddGossipItemFor(player, GOSSIP_ICON_VENDOR,    "Deposit all reagents...", GOSSIP_SENDER_MAIN, GOSSIP_ACTION_INFO_DEF + 11);
            AddGossipItemFor(player, GOSSIP_ICON_MONEY_BAG, "Withdraw...",             GOSSIP_SENDER_MAIN, GOSSIP_ACTION_INFO_DEF + 12);
            AddGossipItemFor(player, GOSSIP_ICON_CHAT,      "< Back",                  GOSSIP_SENDER_MAIN, GOSSIP_ACTION_INFO_DEF + 13);
            SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
            return true;
        }

        if (action == GOSSIP_MOUNT)
        {
            CloseGossipMenuFor(player);
            // Reset camp state so horse follows on next summon
            DespawnCampsite(creature);
            if (npc_rangers_war_horse_AI* ai = dynamic_cast<npc_rangers_war_horse_AI*>(creature->GetAI()))
                ai->SetCamping(false);
            CharacterDatabase.Execute(
                "UPDATE rangers_war_horse_owner SET is_camping = 0 WHERE owner_guid = {}",
                player->GetGUID().GetCounter());
            QueryResult mountResult = CharacterDatabase.Query(
                "SELECT mount_spell_id FROM rangers_war_horse_owner WHERE owner_guid = {}",
                player->GetGUID().GetCounter());
            uint32 mountSpell = 22717;
            if (mountResult)
                mountSpell = mountResult->Fetch()[0].Get<uint32>();
            player->CastSpell(player, mountSpell, TRIGGERED_FULL_MASK);
            return true;
        }

        if (action == GOSSIP_FOLLOW)
        {
            CloseGossipMenuFor(player);
            DespawnCampsite(creature);
            creature->GetMotionMaster()->Clear();
            creature->SetSpeed(MOVE_RUN, 1.0f);
            creature->SetSpeed(MOVE_WALK, 1.0f);
            creature->GetMotionMaster()->MoveFollow(player, 4.0f, M_PI);
            if (npc_rangers_war_horse_AI* ai = dynamic_cast<npc_rangers_war_horse_AI*>(creature->GetAI()))
                ai->SetCamping(false);
            CharacterDatabase.Execute(
                "UPDATE rangers_war_horse_owner SET is_camping = 0 WHERE owner_guid = {}",
                player->GetGUID().GetCounter());
            return true;
        }

        if (action == GOSSIP_WAIT)
        {
            CloseGossipMenuFor(player);
            if (npc_rangers_war_horse_AI* ai = dynamic_cast<npc_rangers_war_horse_AI*>(creature->GetAI()))
                ai->SetCamping(true);
            CharacterDatabase.Execute(
                "UPDATE rangers_war_horse_owner SET is_camping = 1, camp_x = {}, camp_y = {}, camp_z = {}, camp_o = {}, camp_map = {} WHERE owner_guid = {}",
                creature->GetPositionX(), creature->GetPositionY(), creature->GetPositionZ(), creature->GetOrientation(), creature->GetMapId(), player->GetGUID().GetCounter());
            return true;
        }

        if (action == GOSSIP_CAMP)
        {
            CloseGossipMenuFor(player);
            DespawnCampsite(creature);
            SpawnCampsite(creature);
            if (npc_rangers_war_horse_AI* ai = dynamic_cast<npc_rangers_war_horse_AI*>(creature->GetAI()))
                ai->SetCamping(true);
            CharacterDatabase.Execute(
                "UPDATE rangers_war_horse_owner SET is_camping = 2, camp_x = {}, camp_y = {}, camp_z = {}, camp_o = {}, camp_map = {} WHERE owner_guid = {}",
                creature->GetPositionX(), creature->GetPositionY(), creature->GetPositionZ(), creature->GetOrientation(), creature->GetMapId(), player->GetGUID().GetCounter());
            return true;
        }

        if (action == GOSSIP_APPEARANCE)
        {
            ShowAppearancePage(player, creature, 0);
            return true;
        }

        if (action == GOSSIP_PREV_MOUNT)
        {
            uint32 page = (sender > 0) ? sender - 1 : 0;
            ShowAppearancePage(player, creature, page);
            return true;
        }

        if (action == GOSSIP_NEXT_MOUNT)
        {
            ShowAppearancePage(player, creature, sender + 1);
            return true;
        }

        if (action >= GOSSIP_MOUNT_BASE && action < GOSSIP_TRAVEL_BASE)
        {
            uint32 idx = action - GOSSIP_MOUNT_BASE;
            std::vector<MountInfo> mounts = GetPlayerMounts(player);
            if (idx < mounts.size())
            {
                uint32 displayId = mounts[idx].displayId;
                uint32 spellId = mounts[idx].spellId;
                creature->SetDisplayId(displayId);
                CharacterDatabase.Execute(
                    "UPDATE rangers_war_horse_owner SET display_id = {}, mount_spell_id = {} WHERE owner_guid = {}",
                    displayId, spellId, player->GetGUID().GetCounter());
                ChatHandler(player->GetSession()).PSendSysMessage("|cff69CCF0Appearance changed!|r");
            }
            CloseGossipMenuFor(player);
            return true;
        }

        if (action == GOSSIP_FAST_TRAVEL)
        {
            ShowTravelPage(player, creature, 0);
            return true;
        }

        if (action == GOSSIP_PREV_TRAVEL)
        {
            uint32 page = (sender > 0) ? sender - 1 : 0;
            ShowTravelPage(player, creature, page);
            return true;
        }

        if (action == GOSSIP_NEXT_TRAVEL)
        {
            ShowTravelPage(player, creature, sender + 1);
            return true;
        }

        if (action >= GOSSIP_TRAVEL_BASE && action < GOSSIP_FORGET_BASE)
        {
            uint32 pointId = action - GOSSIP_TRAVEL_BASE;
            HandleFastTravel(player, creature, pointId);
            return true;
        }

        if (action == GOSSIP_REMEMBER_LOCATION)
        {
            uint32 guid = player->GetGUID().GetCounter();
            QueryResult cnt = CharacterDatabase.Query(
                "SELECT COUNT(*) FROM rangers_horse_travel_points WHERE owner_guid = {}",
                guid);
            if (cnt && cnt->Fetch()[0].Get<uint32>() >= sLoyalSteedConfig.MaxLocations)
            {
                ChatHandler(player->GetSession()).PSendSysMessage("You can only remember up to {} locations. Forget one first.", sLoyalSteedConfig.MaxLocations);
                CloseGossipMenuFor(player);
                return true;
            }
            // Use zone name as location name
            uint32 zoneId = player->GetAreaId();
            std::string locationName = "Unknown Location";
            if (AreaTableEntry const* zone = sAreaTableStore.LookupEntry(zoneId))
                locationName = zone->area_name[0];
            float saveX = player->GetPositionX();
            float saveY = player->GetPositionY();
            float saveZ = player->GetMap()->GetHeight(player->GetPositionX(), player->GetPositionY(), player->GetPositionZ(), true);
            if (saveZ <= INVALID_HEIGHT) saveZ = player->GetPositionZ();
            CharacterDatabase.Execute(
                "INSERT INTO rangers_horse_travel_points (owner_guid, name, map_id, x, y, z, orientation) VALUES ({}, \"{}\", {}, {}, {}, {}, {})",
                guid, locationName,
                player->GetMapId(),
                saveX,
                saveY,
                saveZ,
                player->GetOrientation());
            ChatHandler(player->GetSession()).PSendSysMessage("|cff69CCF0Your horse remembers: {}|r", locationName);
            CloseGossipMenuFor(player);
            return true;
        }

        if (action == GOSSIP_FORGET_LOCATION)
        {
            ShowForgetPage(player, creature, 0);
            return true;
        }

        if (action == GOSSIP_PREV_FORGET)
        {
            uint32 page = (sender > 0) ? sender - 1 : 0;
            ShowForgetPage(player, creature, page);
            return true;
        }

        if (action == GOSSIP_NEXT_FORGET)
        {
            ShowForgetPage(player, creature, sender + 1);
            return true;
        }

        if (action >= GOSSIP_FORGET_BASE)
        {
            uint32 pointId = action - GOSSIP_FORGET_BASE;
            CharacterDatabase.Execute(
                "DELETE FROM rangers_horse_travel_points WHERE id = {} AND owner_guid = {}",
                pointId, player->GetGUID().GetCounter());
            ChatHandler(player->GetSession()).SendSysMessage("|cff69CCF0Location forgotten.|r");
            CloseGossipMenuFor(player);
            return true;
        }

        return true;
    }

private:

    bool OnGossipSelectCode(Player* player, Creature* creature, uint32 /*sender*/, uint32 action, const char* code) override
    {
        ChatHandler(player->GetSession()).PSendSysMessage("CODE CALLED action=%u code=%s", action, code ? code : "null");
        if (action == GOSSIP_REMEMBER_LOCATION)
        {
            std::string locationName = code ? code : "";
            if (locationName.empty())
                locationName = "Unknown Location";
            uint32 guid = player->GetGUID().GetCounter();
            QueryResult cnt = CharacterDatabase.Query(
                "SELECT COUNT(*) FROM rangers_horse_travel_points WHERE owner_guid = {}",
                guid);
            if (cnt && cnt->Fetch()[0].Get<uint32>() >= sLoyalSteedConfig.MaxLocations)
            {
                ChatHandler(player->GetSession()).PSendSysMessage("You can only remember up to {} locations. Forget one first.", sLoyalSteedConfig.MaxLocations);
                CloseGossipMenuFor(player);
                return true;
            }
            CharacterDatabase.Execute(
                "INSERT INTO rangers_horse_travel_points (owner_guid, name, map_id, x, y, z, orientation) VALUES ({}, \"{}\", {}, {}, {}, {}, {})",
                guid, locationName,
                player->GetMapId(),
                player->GetPositionX(),
                player->GetPositionY(),
                player->GetPositionZ(),
                player->GetOrientation());
            ChatHandler(player->GetSession()).PSendSysMessage("|cff69CCF0Your horse remembers: {}|r", locationName);
            CloseGossipMenuFor(player);
            return true;
        }
        return false;
    }

    void ShowAppearancePage(Player* player, Creature* creature, uint32 page)
    {
        std::vector<MountInfo> mounts = GetPlayerMounts(player);
        uint32 total = (uint32)mounts.size();
        uint32 start = page * MOUNTS_PER_PAGE;

        if (start >= total && total > 0)
            page = (total - 1) / MOUNTS_PER_PAGE, start = page * MOUNTS_PER_PAGE;

        ClearGossipMenuFor(player);

        for (uint32 i = start; i < std::min(start + MOUNTS_PER_PAGE, total); ++i)
            AddGossipItemFor(player, GOSSIP_ICON_INTERACT_1, mounts[i].name, page, GOSSIP_MOUNT_BASE + i);

        if (page > 0)
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "<< Previous", page, GOSSIP_PREV_MOUNT);
        if (start + MOUNTS_PER_PAGE < total)
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Next >>", page, GOSSIP_NEXT_MOUNT);

        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
    }

    void ShowTravelPage(Player* player, Creature* creature, uint32 page)
    {
        uint32 guid = player->GetGUID().GetCounter();
        QueryResult result;
        if (sLoyalSteedConfig.ContinentOnly)
        {
            uint32 currentMap = player->GetMapId();
            result = CharacterDatabase.Query(
                "SELECT id, name FROM rangers_horse_travel_points WHERE owner_guid = {} AND map_id = {} ORDER BY id",
                guid, currentMap);
        }
        else
        {
            result = CharacterDatabase.Query(
                "SELECT id, name FROM rangers_horse_travel_points WHERE owner_guid = {} ORDER BY id",
                guid);
        }

        std::vector<std::pair<uint32, std::string>> points;
        if (result)
        {
            do
            {
                uint32 id = result->Fetch()[0].Get<uint32>();
                std::string name = result->Fetch()[1].Get<std::string>();
                points.push_back({ id, name });
            } while (result->NextRow());
        }

        uint32 total = (uint32)points.size();
        uint32 perPage = TRAVEL_PER_PAGE;
        uint32 start = page * perPage;

        ClearGossipMenuFor(player);

        if (total == 0)
        {
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "No locations remembered on this continent.", GOSSIP_SENDER_MAIN, GOSSIP_FAST_TRAVEL);
        }
        else
        {
            for (uint32 i = start; i < std::min(start + perPage, total); ++i)
                AddGossipItemFor(player, GOSSIP_ICON_TAXI, points[i].second, page, GOSSIP_TRAVEL_BASE + points[i].first);
        }

        if (page > 0)
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "<< Previous", page, GOSSIP_PREV_TRAVEL);
        if (start + perPage < total)
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Next >>", page, GOSSIP_NEXT_TRAVEL);
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "< Back", GOSSIP_SENDER_MAIN, GOSSIP_ACTION_INFO_DEF + 13);

        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
    }

    void ShowForgetPage(Player* player, Creature* creature, uint32 page)
    {
        uint32 guid = player->GetGUID().GetCounter();
        QueryResult result = CharacterDatabase.Query(
            "SELECT id, name FROM rangers_horse_travel_points WHERE owner_guid = {} ORDER BY id",
            guid);

        std::vector<std::pair<uint32, std::string>> points;
        if (result)
        {
            do
            {
                uint32 id = result->Fetch()[0].Get<uint32>();
                std::string name = result->Fetch()[1].Get<std::string>();
                points.push_back({ id, name });
            } while (result->NextRow());
        }

        uint32 total = (uint32)points.size();
        uint32 perPage = TRAVEL_PER_PAGE;
        uint32 start = page * perPage;

        ClearGossipMenuFor(player);

        if (total == 0)
        {
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "No locations to forget.", GOSSIP_SENDER_MAIN, GOSSIP_FORGET_LOCATION);
        }
        else
        {
            for (uint32 i = start; i < std::min(start + perPage, total); ++i)
                AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Forget: " + points[i].second, page, GOSSIP_FORGET_BASE + points[i].first);
        }

        if (page > 0)
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "<< Previous", page, GOSSIP_PREV_FORGET);
        if (start + perPage < total)
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Next >>", page, GOSSIP_NEXT_FORGET);
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "< Back", GOSSIP_SENDER_MAIN, GOSSIP_ACTION_INFO_DEF + 13);

        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
    }

    void HandleFastTravel(Player* player, Creature* creature, uint32 pointId)
    {
        uint32 guid = player->GetGUID().GetCounter();
        QueryResult result = CharacterDatabase.Query(
            "SELECT map_id, x, y, z, orientation, name FROM rangers_horse_travel_points WHERE id = {} AND owner_guid = {}",
            pointId, guid);

        if (!result)
        {
            CloseGossipMenuFor(player);
            return;
        }

        Field* fields = result->Fetch();
        uint32 mapId      = fields[0].Get<uint32>();
        float x           = fields[1].Get<float>();
        float y           = fields[2].Get<float>();
        float z           = fields[3].Get<float>();
        float orientation = fields[4].Get<float>();
        std::string name  = fields[5].Get<std::string>();

        // Mount up player before teleport
        QueryResult mountResult = CharacterDatabase.Query(
            "SELECT mount_spell_id FROM rangers_war_horse_owner WHERE owner_guid = {}",
            guid);
        uint32 mountSpell = 22717;
        if (mountResult)
            mountSpell = mountResult->Fetch()[0].Get<uint32>();

        CloseGossipMenuFor(player);

        // Reset camp state so horse follows on arrival
        DespawnCampsite(creature);
        CharacterDatabase.Execute(
            "UPDATE rangers_war_horse_owner SET is_camping = 0 WHERE owner_guid = {}",
            guid);
        // Despawn horse — it travels ahead
        creature->DespawnOrUnsummon(1000ms);

        // Cast mount spell and teleport
        player->CastSpell(player, mountSpell, TRIGGERED_FULL_MASK);
        // Reset fall information to prevent fall damage on arrival
        player->SetFallInformation(0, z);
        player->TeleportTo(mapId, x, y, z, orientation);

        ChatHandler(player->GetSession()).PSendSysMessage("|cff69CCF0Your horse gallops ahead to {}...|r", name);
    }

};

class vehicle_rangers_war_horse : public VehicleScript
{
public:
    vehicle_rangers_war_horse() : VehicleScript("npc_rangers_war_horse") { }

    void OnAddPassenger(Vehicle* veh, Unit* passenger, int8 /*seatId*/) override
    {
        if (!passenger || !passenger->IsPlayer()) return;
        Creature* horse = veh->GetBase()->ToCreature();
        if (!horse) return;
        DespawnCampsite(horse);
    }

    void OnRemovePassenger(Vehicle* veh, Unit* passenger) override
    {
        if (!passenger || !passenger->IsPlayer()) return;
        Player* player = passenger->ToPlayer();
        Creature* horse = veh->GetBase()->ToCreature();
        if (!horse) return;
        if (npc_rangers_war_horse_AI* ai = dynamic_cast<npc_rangers_war_horse_AI*>(horse->GetAI()))
        {
            ai->SetOwner(player->GetGUID());
            ai->TriggerFollow(player->GetPositionX(), player->GetPositionY(), player->GetPositionZ());
        }
    }
};

class item_rangers_war_horse_deed : public ItemScript
{
public:
    item_rangers_war_horse_deed() : ItemScript("item_rangers_war_horse_deed") { }

    bool OnUse(Player* player, Item* /*item*/, SpellCastTargets const& /*targets*/) override
    {
        if (!sLoyalSteedConfig.Enable)
        {
            ChatHandler(player->GetSession()).SendSysMessage("The Loyal Steed system is currently disabled.");
            return true;
        }
        QueryResult result = CharacterDatabase.Query(
            "SELECT horse_guid FROM rangers_war_horse_owner WHERE owner_guid = {}",
            player->GetGUID().GetCounter());
        if (result)
        {
            ChatHandler(player->GetSession()).PSendSysMessage("|cffff0000You already have a Loyal Steed!|r");
            return true;
        }

        // Get race-appropriate display ID
        uint32 displayId = GetRaceDisplayId(player->getRace());
        // Teach the companion spell
        player->learnSpell(900012);
        // Insert DB record
        CharacterDatabase.Execute(
            "INSERT INTO rangers_war_horse_owner (owner_guid, horse_guid, display_id) VALUES ({}, 0, {})",
            player->GetGUID().GetCounter(), displayId);
        // Destroy the deed
        player->DestroyItemCount(900001, 1, true);
        ChatHandler(player->GetSession()).PSendSysMessage("|cff69CCF0Your Loyal Steed has bonded with you! Find the spell in your spellbook.|r");
        return true;
    }
};

class playerscript_rangers_war_horse : public PlayerScript
{
public:
    playerscript_rangers_war_horse() : PlayerScript("playerscript_rangers_war_horse") { }

    void OnPlayerLogin(Player* player) override
    {
        // Clear stale horse guid on login — horse must be resummoned via companion spell
        CharacterDatabase.Execute(
            "UPDATE rangers_war_horse_owner SET horse_guid = 0 WHERE owner_guid = {}",
            player->GetGUID().GetCounter());
    }

    void OnPlayerLogout(Player* player) override
    {
        bool isMounted = player->HasAuraType(SPELL_AURA_MOUNTED);

        // Despawn by saved GUID
        QueryResult result = CharacterDatabase.Query(
            "SELECT horse_guid FROM rangers_war_horse_owner WHERE owner_guid = {}",
            player->GetGUID().GetCounter());
        if (result)
        {
            uint32 horseGuid = result->Fetch()[0].Get<uint32>();
            if (horseGuid)
            {
                if (Creature* horse = player->GetMap()->GetCreature(ObjectGuid::Create<HighGuid::Unit>(HORSE_NPC_ENTRY, horseGuid)))
                {
                    DespawnCampsite(horse);
                    horse->DespawnOrUnsummon();
                }
            }
        }

        // Also scan nearby to catch companion-summoned horses — only despawn our own
        std::list<Creature*> nearbyHorses;
        player->GetCreatureListWithEntryInGrid(nearbyHorses, HORSE_NPC_ENTRY, 200.0f);
        for (Creature* nearby : nearbyHorses)
        {
            if (!IsHorseOwner(player, nearby)) continue;
            DespawnCampsite(nearby);
            nearby->DespawnOrUnsummon();
        }

        CharacterDatabase.Execute(
            "UPDATE rangers_war_horse_owner SET horse_guid = 0, logged_out_mounted = {} WHERE owner_guid = {}",
            isMounted ? 1 : 0, player->GetGUID().GetCounter());
    }

    void OnPlayerJustDied(Player* player) override
    {
        QueryResult result = CharacterDatabase.Query(
            "SELECT horse_guid FROM rangers_war_horse_owner WHERE owner_guid = {}",
            player->GetGUID().GetCounter());
        if (!result) return;

        uint32 horseGuid = result->Fetch()[0].Get<uint32>();
        if (!horseGuid) return;

        if (Creature* horse = player->GetMap()->GetCreature(ObjectGuid::Create<HighGuid::Unit>(HORSE_NPC_ENTRY, horseGuid)))
        {
            DespawnCampsite(horse);
            horse->DespawnOrUnsummon();
        }

        CharacterDatabase.Execute(
            "UPDATE rangers_war_horse_owner SET horse_guid = 0 WHERE owner_guid = {}",
            player->GetGUID().GetCounter());

        ChatHandler(player->GetSession()).PSendSysMessage(
            "|cffff0000Your Loyal Steed has fled! Use your deed to resummon it.|r");
    }

    void OnPlayerPVPKill(Player* killer, Player* /*killed*/) override
    {
        QueryResult result = CharacterDatabase.Query(
            "SELECT horse_guid, display_id FROM rangers_war_horse_owner WHERE owner_guid = {}",
            killer->GetGUID().GetCounter());
        if (!result) return;

        uint32 horseGuid = result->Fetch()[0].Get<uint32>();
        uint32 displayId = result->Fetch()[1].Get<uint32>();

        if (Creature* existing = killer->GetMap()->GetCreature(ObjectGuid::Create<HighGuid::Unit>(HORSE_NPC_ENTRY, horseGuid)))
        {
            if (existing->IsAlive())
            {
                FullRemoveControlled(killer, existing);
                return;
            }
        }

        std::list<Creature*> nearbyHorses;
        killer->GetCreatureListWithEntryInGrid(nearbyHorses, HORSE_NPC_ENTRY, 200.0f);
        for (Creature* nearby : nearbyHorses)
        {
            if (nearby->IsAlive())
            {
                CharacterDatabase.Execute(
                    "UPDATE rangers_war_horse_owner SET horse_guid = {} WHERE owner_guid = {}",
                    nearby->GetGUID().GetCounter(), killer->GetGUID().GetCounter());
                return;
            }
        }

        Creature* horse = SummonHorseForPlayer(killer, displayId);
        if (horse)
        {
            CharacterDatabase.Execute(
                "UPDATE rangers_war_horse_owner SET horse_guid = {} WHERE owner_guid = {}",
                horse->GetGUID().GetCounter(), killer->GetGUID().GetCounter());
        }
    }

    void OnPlayerLeaveCombat(Player* player) override
    {
        QueryResult result = CharacterDatabase.Query(
            "SELECT horse_guid, display_id FROM rangers_war_horse_owner WHERE owner_guid = {}",
            player->GetGUID().GetCounter());
        if (!result) return;

        uint32 horseGuid = result->Fetch()[0].Get<uint32>();
        uint32 displayId = result->Fetch()[1].Get<uint32>();

        // Only respawn if player had a horse out before combat
        if (!horseGuid) return;

        // Don't respawn if horse is camping
        QueryResult campResult = CharacterDatabase.Query(
            "SELECT is_camping FROM rangers_war_horse_owner WHERE owner_guid = {}",
            player->GetGUID().GetCounter());
        if (campResult && campResult->Fetch()[0].Get<uint8>() > 0) return;

        if (Creature* existing = player->GetMap()->GetCreature(ObjectGuid::Create<HighGuid::Unit>(HORSE_NPC_ENTRY, horseGuid)))
            if (existing->IsAlive())
                return;

        std::list<Creature*> nearbyHorses;
        player->GetCreatureListWithEntryInGrid(nearbyHorses, HORSE_NPC_ENTRY, 200.0f);
        for (Creature* nearby : nearbyHorses)
        {
            if (nearby->IsAlive())
            {
                CharacterDatabase.Execute(
                    "UPDATE rangers_war_horse_owner SET horse_guid = {} WHERE owner_guid = {}",
                    nearby->GetGUID().GetCounter(), player->GetGUID().GetCounter());
                return;
            }
        }

        Creature* horse = SummonHorseForPlayer(player, displayId);
        if (horse)
        {
            CharacterDatabase.Execute(
                "UPDATE rangers_war_horse_owner SET horse_guid = {} WHERE owner_guid = {}",
                horse->GetGUID().GetCounter(), player->GetGUID().GetCounter());
        }
    }

    void OnPlayerUpdate(Player* player, uint32 diff) override
    {
        static std::unordered_map<uint32, uint32> timers;
        static std::unordered_map<uint32, bool> wasMounted;
        uint32 guid = player->GetGUID().GetCounter();

        // Detect mount/dismount events
        bool isMounted = player->HasAuraType(SPELL_AURA_MOUNTED);
        bool wasMountedLast = wasMounted.count(guid) ? wasMounted[guid] : false;
        wasMounted[guid] = isMounted;

        if (!wasMountedLast && isMounted)
        {
            // Player just mounted — despawn horse
            QueryResult mountResult = CharacterDatabase.Query(
                "SELECT horse_guid FROM rangers_war_horse_owner WHERE owner_guid = {}",
                guid);
            if (mountResult)
            {
                uint32 horseGuid = mountResult->Fetch()[0].Get<uint32>();
                if (Creature* horse = player->GetMap()->GetCreature(ObjectGuid::Create<HighGuid::Unit>(HORSE_NPC_ENTRY, horseGuid)))
                    horse->DespawnOrUnsummon();
                // Also scan nearby in case guid is stale
                std::list<Creature*> nearbyHorses;
                player->GetCreatureListWithEntryInGrid(nearbyHorses, HORSE_NPC_ENTRY, 200.0f);
                for (Creature* nearby : nearbyHorses)
                    nearby->DespawnOrUnsummon();
                CharacterDatabase.Execute(
                    "UPDATE rangers_war_horse_owner SET horse_guid = 0 WHERE owner_guid = {}",
                    guid);
            }
        }
        else if (wasMountedLast && !isMounted && player->IsAlive())
        {
            // Player just dismounted — respawn horse at player position
            // Don't respawn if horse is camping
            QueryResult dismountResult = CharacterDatabase.Query(
                "SELECT display_id, is_camping FROM rangers_war_horse_owner WHERE owner_guid = {}",
                guid);
            if (dismountResult)
            {
                bool isCamping = dismountResult->Fetch()[1].Get<uint8>() > 0;
                if (!isCamping)
                {
                    uint32 displayId = dismountResult->Fetch()[0].Get<uint32>();
                    Creature* horse = SummonHorseForPlayer(player, displayId);
                    if (horse)
                    {
                        CharacterDatabase.Execute(
                            "UPDATE rangers_war_horse_owner SET horse_guid = {} WHERE owner_guid = {}",
                            horse->GetGUID().GetCounter(), guid);
                    }
                }
            }
        }

        timers[guid] += diff;
        if (timers[guid] < 5000) return;
        timers[guid] = 0;

        if (!player->IsAlive() || player->IsInCombat()) return;

        QueryResult result = CharacterDatabase.Query(
            "SELECT horse_guid, display_id FROM rangers_war_horse_owner WHERE owner_guid = {}",
            guid);
        if (!result) return;

        uint32 horseGuid = result->Fetch()[0].Get<uint32>();
        uint32 displayId = result->Fetch()[1].Get<uint32>();

        if (!horseGuid) return;

        // First check by saved GUID
        if (Creature* existing = player->GetMap()->GetCreature(ObjectGuid::Create<HighGuid::Unit>(HORSE_NPC_ENTRY, horseGuid)))
            if (existing->IsAlive())
                return;

        // Second check: scan nearby creatures to avoid duplicate spawns
        std::list<Creature*> nearbyHorses;
        player->GetCreatureListWithEntryInGrid(nearbyHorses, HORSE_NPC_ENTRY, 30.0f);
        for (Creature* nearby : nearbyHorses)
        {
            if (nearby->IsAlive())
            {
                // Update DB to match existing horse
                CharacterDatabase.Execute(
                    "UPDATE rangers_war_horse_owner SET horse_guid = {} WHERE owner_guid = {}",
                    nearby->GetGUID().GetCounter(), guid);
                return;
            }
        }

        Creature* horse = SummonHorseForPlayer(player, displayId);
        if (horse)
        {
            CharacterDatabase.Execute(
                "UPDATE rangers_war_horse_owner SET horse_guid = {} WHERE owner_guid = {}",
                horse->GetGUID().GetCounter(), guid);
        }
    }
};

class spell_rangers_war_horse_summon : public SpellScript
{
    PrepareSpellScript(spell_rangers_war_horse_summon);

    bool Load() override
    {
        return GetCaster()->IsPlayer();
    }

    SpellCastResult CheckCast()
    {
        Player* player = GetCaster()->ToPlayer();
        if (!player) return SPELL_FAILED_ERROR;

        // If horse is alive — dismiss it and cancel the summon
        std::list<Creature*> nearbyHorses;
        player->GetCreatureListWithEntryInGrid(nearbyHorses, HORSE_NPC_ENTRY, 200.0f);
        for (Creature* nearby : nearbyHorses)
        {
            if (nearby->IsAlive())
            {
                DespawnCampsite(nearby);
                nearby->DespawnOrUnsummon();
                CharacterDatabase.Execute(
                    "UPDATE rangers_war_horse_owner SET horse_guid = 0, is_camping = 0 WHERE owner_guid = {}",
                    player->GetGUID().GetCounter());
                return SPELL_FAILED_DONT_REPORT;
            }
        }
        return SPELL_CAST_OK;
    }

    void HandleEffect(SpellEffIndex effIndex)
    {
        PreventHitDefaultEffect(effIndex);
        Player* player = GetCaster()->ToPlayer();
        if (!player) return;

        QueryResult result = CharacterDatabase.Query(
            "SELECT display_id FROM rangers_war_horse_owner WHERE owner_guid = {}",
            player->GetGUID().GetCounter());
        if (!result) return;

        uint32 displayId = result->Fetch()[0].Get<uint32>();
        Creature* horse = SummonHorseForPlayer(player, displayId);
        if (horse)
        {
            CharacterDatabase.Execute(
                "UPDATE rangers_war_horse_owner SET horse_guid = {}, is_camping = 0 WHERE owner_guid = {}",
                horse->GetGUID().GetCounter(), player->GetGUID().GetCounter());
        }
    }

    void Register() override
    {
        OnCheckCast += SpellCheckCastFn(spell_rangers_war_horse_summon::CheckCast);
        OnEffectHit += SpellEffectFn(spell_rangers_war_horse_summon::HandleEffect, EFFECT_0, SPELL_EFFECT_SUMMON);
    }
};

class worldscript_loyal_steed : public WorldScript
{
public:
    worldscript_loyal_steed() : WorldScript("worldscript_loyal_steed") {}

    void OnAfterConfigLoad(bool /*reload*/) override
    {
        sLoyalSteedConfig.Enable           = sConfigMgr->GetOption<bool>("LoyalSteed.Enable", true);
        sLoyalSteedConfig.StorageEnable    = sConfigMgr->GetOption<bool>("LoyalSteed.Storage.Enable", true);
        sLoyalSteedConfig.FastTravelEnable = sConfigMgr->GetOption<bool>("LoyalSteed.FastTravel.Enable", true);
        sLoyalSteedConfig.MaxLocations     = sConfigMgr->GetOption<uint32>("LoyalSteed.FastTravel.MaxLocations", 20);
        sLoyalSteedConfig.ContinentOnly    = sConfigMgr->GetOption<bool>("LoyalSteed.FastTravel.ContinentOnly", true);
        sLoyalSteedConfig.CampEnable       = sConfigMgr->GetOption<bool>("LoyalSteed.Camp.Enable", true);
        sLoyalSteedConfig.AppearanceEnable = sConfigMgr->GetOption<bool>("LoyalSteed.Appearance.Enable", true);
    }
};

void Addmod_mount_evolvedScripts()
{
    new npc_rangers_war_horse();
    new vehicle_rangers_war_horse();
    new item_rangers_war_horse_deed();
    new playerscript_rangers_war_horse();
    new worldscript_loyal_steed();
    RegisterSpellScript(spell_rangers_war_horse_summon);
}
