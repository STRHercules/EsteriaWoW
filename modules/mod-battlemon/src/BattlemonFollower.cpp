#include "BattlemonFollower.h"
#include "BattlemonMgr.h"
#include "BattlemonModelCatalog.h"
#include "BattlemonOverworld.h"

#include "Chat.h"
#include "Config.h"
#include "Creature.h"
#include "DatabaseEnv.h"
#include "Map.h"
#include "MotionMaster.h"
#include "ObjectAccessor.h"
#include "ObjectMgr.h"
#include "PetDefines.h"
#include "Player.h"
#include "TemporarySummon.h"

#include <algorithm>

namespace
{
constexpr uint32 TICK_MS = 1000;
constexpr uint32 SUMMON_COOLDOWN_MS = 3000;
constexpr float MAX_DISTANCE = 60.0f; // further than this the follower is lost; resummon it beside the player

void Tell(Player* player, std::string const& text)
{
    ChatHandler(player->GetSession()).SendSysMessage(text);
}
}

BattlemonFollower* BattlemonFollower::instance()
{
    static BattlemonFollower inst;
    return &inst;
}

void BattlemonFollower::LoadConfig()
{
    _enabled = sConfigMgr->GetOption<bool>("Battlemon.Follower.Enable", true);
    _distance = std::clamp(sConfigMgr->GetOption<float>("Battlemon.Follower.Distance", 2.0f), 0.5f, 10.0f);
}

uint32 BattlemonFollower::Chosen(Player* player)
{
    std::lock_guard<std::mutex> guard(_lock);
    auto it = _states.find(player->GetGUID());
    return it == _states.end() ? 0 : it->second.ownedId;
}

bool BattlemonFollower::Choose(Player* player, uint32 ownedId)
{
    if (!_enabled)
    {
        Tell(player, "Following Pokemon are disabled on this server.");
        return false;
    }
    uint32 const guid = player->GetGUID().GetCounter();
    if (ownedId)
    {
        // Ownership comes from the database row, never from what the player typed.
        BattlemonOwned const row = sBattlemonMgr->LoadOwnedById(ownedId);
        if (!row.id || row.guid != guid || !BattlemonOverworldIds::FormEntry(row.formId)
            || !sObjectMgr->GetCreatureTemplate(BattlemonOverworldIds::FormEntry(row.formId)))
        {
            Tell(player, "That Pokemon cannot follow you.");
            return false;
        }
    }

    ObjectGuid actor;
    {
        std::lock_guard<std::mutex> lock(_lock);
        if (ownedId)
        {
            State& st = _states[player->GetGUID()];
            actor = st.actor;
            st.ownedId = ownedId;
            st.actor = ObjectGuid::Empty; // despawned below; Tick brings the new one
            st.summonCooldownMs = 0;
        }
        else if (auto it = _states.find(player->GetGUID()); it != _states.end())
        {
            actor = it->second.actor;
            _states.erase(it);
        }
    }
    DespawnActor(player, actor);

    if (ownedId)
        CharacterDatabase.Execute("REPLACE INTO battlemon_follower (guid, owned_id) VALUES ({}, {})", guid, ownedId);
    else
        CharacterDatabase.Execute("DELETE FROM battlemon_follower WHERE guid = {}", guid);
    return true;
}

void BattlemonFollower::OnLogin(Player* player)
{
    if (!_enabled)
        return;
    QueryResult result = CharacterDatabase.Query(
        "SELECT owned_id FROM battlemon_follower WHERE guid = {}", player->GetGUID().GetCounter());
    if (!result)
        return;
    std::lock_guard<std::mutex> lock(_lock);
    _states[player->GetGUID()].ownedId = result->Fetch()[0].Get<uint32>();
}

void BattlemonFollower::OnLogout(Player* player)
{
    ObjectGuid actor;
    {
        std::lock_guard<std::mutex> lock(_lock);
        auto it = _states.find(player->GetGUID());
        if (it == _states.end())
            return;
        actor = it->second.actor;
        _states.erase(it);
    }
    DespawnActor(player, actor);
}

void BattlemonFollower::Despawn(Player* player)
{
    ObjectGuid actor;
    {
        std::lock_guard<std::mutex> lock(_lock);
        auto it = _states.find(player->GetGUID());
        if (it == _states.end())
            return;
        actor = it->second.actor;
        it->second.actor = ObjectGuid::Empty;
    }
    DespawnActor(player, actor);
}

void BattlemonFollower::DespawnActor(Player* player, ObjectGuid actor)
{
    if (actor.IsEmpty())
        return;
    if (Creature* creature = ObjectAccessor::GetCreature(*player, actor))
        creature->DespawnOrUnsummon();
}

bool BattlemonFollower::ShouldShow(Player* player) const
{
    return player->IsInWorld() && player->IsAlive() && !player->IsMounted() && !player->IsInFlight()
        && !player->GetVehicle() && !player->InBattleground()
        && !sBattlemonMgr->HasActiveEncounter(player) && !sBattlemonMgr->IsExternallyReserved(player->GetGUID());
}

ObjectGuid BattlemonFollower::Summon(Player* player, uint32 ownedId)
{
    BattlemonOwned const row = sBattlemonMgr->LoadOwnedById(ownedId);
    uint32 const entry = BattlemonOverworldIds::FormEntry(row.formId);
    if (!row.id || row.guid != player->GetGUID().GetCounter() || !sObjectMgr->GetCreatureTemplate(entry))
        return ObjectGuid::Empty;

    TempSummon* summon = player->SummonCreature(entry, player->GetNearPosition(_distance, M_PI), TEMPSUMMON_MANUAL_DESPAWN);
    if (!summon)
        return ObjectGuid::Empty;
    // Owned creatures are skipped by the overworld's click-to-battle, so it never starts a wild fight.
    summon->SetOwnerGUID(player->GetGUID());
    summon->SetReactState(REACT_PASSIVE);
    BattlemonOverworld::instance()->ApplyLook(summon, row.formId, row.shiny);
    summon->GetMotionMaster()->MoveFollow(player, _distance, MINI_PET_FOLLOW_ANGLE);
    return summon->GetGUID();
}

void BattlemonFollower::Tick(Player* player, uint32 diff)
{
    // shortcut: one mutex-guarded map hit per player update; move the state onto the Player (DataMap) if
    // profiling ever shows contention between map threads.
    uint32 ownedId = 0;
    ObjectGuid actor;
    {
        std::lock_guard<std::mutex> lock(_lock);
        if (_states.empty())
            return;
        auto it = _states.find(player->GetGUID());
        if (it == _states.end())
            return;
        State& st = it->second;
        st.summonCooldownMs = st.summonCooldownMs > diff ? st.summonCooldownMs - diff : 0;
        st.timerMs += diff;
        if (st.timerMs < TICK_MS)
            return;
        st.timerMs = 0;
        ownedId = st.ownedId;
        actor = st.actor;
    }

    Creature* creature = actor.IsEmpty() ? nullptr : ObjectAccessor::GetCreature(*player, actor);
    if (!_enabled || !ShouldShow(player))
    {
        if (creature)
            Despawn(player);
        return;
    }
    // Wrong map, dead, or left behind: drop it and let the next summon put it beside the player.
    if (creature && (!creature->IsAlive() || creature->GetMap() != player->GetMap()
        || creature->GetExactDist(player) > MAX_DISTANCE))
    {
        Despawn(player);
        return;
    }
    if (creature)
        return;

    {
        std::lock_guard<std::mutex> lock(_lock);
        auto it = _states.find(player->GetGUID());
        if (it == _states.end() || it->second.summonCooldownMs)
            return;
        it->second.summonCooldownMs = SUMMON_COOLDOWN_MS;
    }
    ObjectGuid const made = Summon(player, ownedId);
    if (made.IsEmpty() && sBattlemonMgr->LoadOwnedById(ownedId).guid != player->GetGUID().GetCounter())
    {
        // Traded away, sealed in a ball or deleted: forget it instead of retrying forever.
        Choose(player, 0);
        return;
    }
    std::lock_guard<std::mutex> lock(_lock);
    if (auto it = _states.find(player->GetGUID()); it != _states.end())
        it->second.actor = made;
}
