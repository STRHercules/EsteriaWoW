#include "BattlemonNpcTrainers.h"
#include "BattlemonTrainerProgression.h"
#include "BattlemonBattles.h"
#include "BattlemonEffectCatalog.h"
#include "BattlemonNativeEffects.h"
#include "BattlemonBattle.h"
#include "BattlemonMgr.h"
#include "BattlemonSidecarServer.h"
#include "BattlemonOverworld.h"
#include "Chat.h"
#include "Config.h"
#include "Creature.h"
#include "DBCStores.h"
#include "GameTime.h"
#include "Map.h"
#include "MapMgr.h"
#include "MotionMaster.h"
#ifdef MOD_PLAYERBOTS
#include "Playerbots.h"
#endif
#include "ObjectAccessor.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "Random.h"
#include "StringFormat.h"
#include "Spell.h"
#include "WorldPacket.h"
#include "WorldSession.h"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <limits>
#include <sstream>
#include <utility>

namespace
{
    constexpr uint32 MaxCommandBytes = 240;
    constexpr uint32 CommandIntervalMs = 150;
    constexpr uint32 ActorLifetimeMs = 3600000;
    constexpr float Pi = 3.14159265359f;

    enum BattleMotion : uint32
    {
        MotionAdvance = 1,
        MotionReturn = 2,
        MotionStomp = 3
    };

    // Presentation packets only: never construct/cast a Spell or apply its effects.
    // Wire layout follows Spell::SendSpellStart/SendSpellGo for one unit target.
    void SendNativeVisual(Creature* caster, Creature* target, uint32 spell, uint8 cast, uint32 windup, bool launch)
    {
        SpellCastTargets targets;
        targets.SetUnitTarget(target);
        WorldPacket packet(launch ? SMSG_SPELL_GO : SMSG_SPELL_START, 80);
        packet << caster->GetPackGUID() << caster->GetPackGUID();
        packet << cast << spell;
        if (launch)
        {
            packet << uint32(CAST_FLAG_UNKNOWN_9) << uint32(GameTime::GetGameTimeMS().count());
            packet << uint8(1) << target->GetGUID() << uint8(0); // one hit, no misses
        }
        else
            packet << uint32(CAST_FLAG_NONE) << int32(windup);
        targets.Write(packet);
        caster->SendMessageToSet(&packet, true);
    }

    bool IsBot(Player* player)
    {
        return player && player->GetSession() && player->GetSession()->IsBot();
    }
}

BattlemonBattles& BattlemonBattles::Instance()
{
    static BattlemonBattles service;
    return service;
}

uint64 BattlemonBattles::Now()
{
    return static_cast<uint64>(std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count());
}

BattlemonBattles::BattlemonBattles()
{
    _scheduler.Schedule(std::chrono::milliseconds(200), [this](TaskContext context)
    {
        Poll();
        context.Repeat(std::chrono::milliseconds(200));
    });
}

void BattlemonBattles::LoadConfig()
{
    OnCatalogReload();
    _enabled = sConfigMgr->GetOption<bool>("BattlemonBattles.Enable", true);
    _allowClassic = sConfigMgr->GetOption<bool>("BattlemonBattles.AllowClassic", true);
    _defaultPet = sConfigMgr->GetOption<std::string>("BattlemonBattles.DefaultMode", "pet") != "classic";
    _duelsEnabled = sConfigMgr->GetOption<bool>("BattlemonBattles.EnableDuels", true);
    _botsEnabled = sConfigMgr->GetOption<bool>("BattlemonBattles.EnableBotDuels", true);
    _generateBots = sConfigMgr->GetOption<bool>("BattlemonBattles.GenerateBotTeams", true);
    _worldActors = sConfigMgr->GetOption<bool>("BattlemonBattles.WorldActors", true);
    _nativeSpellVisuals = sConfigMgr->GetOption<bool>("BattlemonBattles.NativeSpellVisuals", true);
    _teamSize = static_cast<uint8>(std::clamp(sConfigMgr->GetOption<uint32>("BattlemonBattles.TeamSize", 6), 1u, 6u));
    _turnSeconds = std::clamp(sConfigMgr->GetOption<uint32>("BattlemonBattles.TurnSeconds", 45), 10u, 300u);
    _inviteSeconds = std::clamp(sConfigMgr->GetOption<uint32>("BattlemonBattles.InviteSeconds", 30), 5u, 120u);
    _botThinkMs = std::clamp(sConfigMgr->GetOption<uint32>("BattlemonBattles.BotThinkMilliseconds", 1500), 200u, 10000u);
    _actorEntry = sConfigMgr->GetOption<uint32>("BattlemonBattles.ActorEntry", 60000);
    _distance = std::clamp(sConfigMgr->GetOption<float>("BattlemonBattles.MaxDistance", 25.0f), 5.0f, 100.0f);
}

bool BattlemonBattles::IsReserved(ObjectGuid guid) const
{
    std::lock_guard<std::mutex> guard(_queueMutex);
    return _reserved.count(guid) != 0;
}

void BattlemonBattles::Enqueue(ObjectGuid player, std::string const& message, bool disconnect)
{
    if (message.size() > MaxCommandBytes)
        return;
    std::lock_guard<std::mutex> guard(_queueMutex);
    if (_inputs.size() < 4096 || disconnect)
        _inputs.push_back({player, message, disconnect, false});
}

bool BattlemonBattles::IsPlaybackBusy(ObjectGuid guid) const
{
    std::lock_guard<std::mutex> guard(_queueMutex);
    return _playbackUntil.count(guid) != 0;
}

uint64 BattlemonBattles::PlaybackAt(ObjectGuid guid) const
{
    std::lock_guard<std::mutex> guard(_queueMutex);
    auto it = _playbackUntil.find(guid);
    return it == _playbackUntil.end() ? 0 : it->second;
}

bool BattlemonBattles::OnPacket(Player* player, std::string const& payload)
{
    if (!player)
        return false;
    std::string const command = payload.substr(0, payload.find('\t', 3));
    bool const effect = command == "BM\tFX";
    bool const sceneEvent = effect || command == "BM\tWILD" || command == "BM\tEND";
    std::lock_guard<std::mutex> guard(_queueMutex);
    bool const timed = _timedPlayers.count(player->GetGUID()) && (sceneEvent || command == "BM\tP"
        || command == "BM\tE" || command == "BM\tMSG" || command == "BM\tAIL"
        || command == "BM\tWEATHER" || command == "BM\tBPARTY" || command == "BM\tCATCH"
        || command == "BM\tSWITCHNEED");
    if (timed || sceneEvent)
    {
        _inputs.push_back({player->GetGUID(), payload, false, true, timed});
        if (timed && effect)
            _playbackUntil[player->GetGUID()] = std::numeric_limits<uint64>::max();
    }
    return timed;
}

void BattlemonBattles::SetPlayback(ObjectGuid player, uint64 until)
{
    if (player.IsEmpty())
        return;
    {
        std::lock_guard<std::mutex> guard(_queueMutex);
        _playbackUntil[player] = until;
    }
    SendRaw(ObjectAccessor::FindPlayer(player), "BMB\tPLAYBACK\t1");
}

void BattlemonBattles::Deliver(ObjectGuid player, std::string const& payload, uint64 at)
{
    _deliveries.push_back({player, payload, at});
}

void BattlemonBattles::ClearPlayback(ObjectGuid player)
{
    _deliveries.erase(std::remove_if(_deliveries.begin(), _deliveries.end(),
        [player](Delivery const& delivery) { return delivery.player == player; }), _deliveries.end());
    {
        std::lock_guard<std::mutex> guard(_queueMutex);
        _playbackUntil.erase(player);
    }
    SendRaw(ObjectAccessor::FindPlayer(player), "BMB\tPLAYBACK\t0");
}

void BattlemonBattles::FlushPlayback()
{
    uint64 const now = Now();
    for (auto it = _deliveries.begin(); it != _deliveries.end();)
    {
        if (it->at > now)
        {
            ++it;
            continue;
        }
        SendRaw(ObjectAccessor::FindPlayer(it->player), it->payload);
        it = _deliveries.erase(it);
    }
    std::vector<ObjectGuid> ready;
    {
        std::lock_guard<std::mutex> guard(_queueMutex);
        for (auto it = _playbackUntil.begin(); it != _playbackUntil.end();)
            if (it->second <= now)
            {
                ready.push_back(it->first);
                it = _playbackUntil.erase(it);
            }
            else
                ++it;
    }
    for (ObjectGuid player : ready)
        SendRaw(ObjectAccessor::FindPlayer(player), "BMB\tPLAYBACK\t0");
}

void BattlemonBattles::Update(uint32 diff)
{
    std::deque<Input> pending;
    {
        std::lock_guard<std::mutex> guard(_queueMutex);
        pending.swap(_inputs);
    }
    for (Input const& input : pending)
        Process(input);
    _scheduler.Update(diff);
    FlushPlayback();
}

void BattlemonBattles::Send(Player* player, std::string const& payload)
{
    if (!player)
        return;
    std::string const command = payload.substr(0, payload.find('\t'));
    bool const presentation = command == "P" || command == "E" || command == "AIL" || command == "WEATHER"
        || command == "TEAM" || command == "TEAMCLEAR" || command == "TURN" || command == "LOG" || command == "END";
    uint64 const at = PlaybackAt(player->GetGUID());
    if (presentation && at > Now())
        Deliver(player->GetGUID(), "BMB\t" + payload, at);
    else
        SendRaw(player, "BMB\t" + payload);
}

void BattlemonBattles::SendRaw(Player* player, std::string const& payload) const
{
    if (!player || !player->GetSession() || IsBot(player))
        return;
    WorldPacket packet;
    std::string const& message = payload;
    ChatHandler::BuildChatPacket(packet, CHAT_MSG_WHISPER, message.c_str(), LANG_ADDON,
        CHAT_TAG_NONE, player->GetGUID(), player->GetName());
    player->SendDirectMessage(&packet);
}

void BattlemonBattles::Broadcast(Duel const& duel, std::string const& payload)
{
    for (ObjectGuid guid : duel.players)
        Send(ObjectAccessor::FindPlayer(guid), payload);
}

bool BattlemonBattles::Eligible(Player* player) const
{
    return player && player->IsInWorld() && player->IsAlive() && !player->IsInCombat()
        && !player->IsInFlight() && !player->IsFlying() && !player->GetTransport()
        && !player->IsBeingTeleported() && player->GetSession();
}

bool BattlemonBattles::Near(Player* a, Player* b) const
{
    return Eligible(a) && Eligible(b) && a->GetMap() == b->GetMap()
        && a->InSamePhase(b) && a->IsWithinDistInMap(b, _distance) && a->IsWithinLOSInMap(b);
}

bool BattlemonBattles::PetMode(ObjectGuid guid) const
{
    auto it = _preferences.find(guid);
    return _enabled && (!_allowClassic || (it == _preferences.end() ? _defaultPet : it->second));
}

void BattlemonBattles::Process(Input const& input)
{
    if (input.disconnect)
    {
        CancelPlayer(input.player);
        if (!ObjectAccessor::FindPlayer(input.player))
        {
            _preferences.erase(input.player);
            std::lock_guard<std::mutex> guard(_queueMutex);
            _timedPlayers.erase(input.player);
        }
        _lastCommand.erase(input.player);
        return;
    }
    Player* player = ObjectAccessor::FindPlayer(input.player);
    if (!player)
        return;
    if (!input.trainer.IsEmpty())
    {
        BeginTrainer(player, player->GetMap()->GetCreature(input.trainer));
        return;
    }
    if (input.packet)
    {
        bool const timed = input.deferred;
        if (timed && input.message == "BM\tWILD")
        {
            ClearPlayback(input.player);
            BattlemonEncounter encounter;
            if (sBattlemonMgr->GetBattleSnapshot(player, encounter) && encounter.activeSlot
                && encounter.activeSlot <= encounter.party.size())
                ShowScene(player, encounter.party[encounter.activeSlot - 1], encounter.enemy);
        }
        if (input.message.compare(0, 7, "BM\tEND\t") == 0)
            EndScene(input.player);
        else if (input.message.compare(0, 6, "BM\tFX\t") == 0)
        {
            std::istringstream effect(input.message.substr(6));
            unsigned side;
            std::string move;
            if (effect >> side >> move && side < 2)
                Animate(input.player, static_cast<uint8>(side), move);
            if (timed)
            {
                auto scene = _scenes.find(input.player);
                SetPlayback(input.player, scene == _scenes.end() ? Now() : scene->second.animationAt);
            }
        }
        if (timed)
        {
            // Pending FX uses a sentinel in the cross-thread action gate. Packet
            // timing must use the scene cursor at this exact point in event order.
            auto scene = _scenes.find(input.player);
            Deliver(input.player, input.message, scene == _scenes.end() ? Now() : scene->second.animationAt);
        }
        return;
    }
    std::istringstream stream(input.message);
    std::string command;
    stream >> command;
    uint64 const now = Now();
    if (command != "FORFEIT" && _lastCommand[input.player] + CommandIntervalMs > now)
        return;
    _lastCommand[input.player] = now;
    if (command == "HELLO" || command == "MODE")
    {
        _preferences.try_emplace(input.player, _defaultPet);
        std::string mode;
        stream >> mode;
        if (command == "MODE" && !IsPlaybackBusy(input.player) && !IsReserved(input.player)
            && !sBattlemonMgr->HasActiveEncounter(player))
        {
            if (mode == "pet" || (mode == "classic" && _allowClassic))
                _preferences[input.player] = mode == "pet";
        }
        {
            std::lock_guard<std::mutex> guard(_queueMutex);
            if (PetMode(input.player))
                _timedPlayers.insert(input.player);
            else
                _timedPlayers.erase(input.player);
        }
        Send(player, Acore::StringFormat("MODE\t{}\t{}\t{}", PetMode(input.player) ? "pet" : "classic",
            _enabled && _allowClassic ? 1 : 0, _enabled && _duelsEnabled ? 1 : 0));
        if (auto it = _byPlayer.find(input.player); it != _byPlayer.end())
        {
            Duel& duel = _duels.at(it->second);
            ObjectGuid const other = duel.players[0] == input.player ? duel.players[1] : duel.players[0];
            Player* opponent = ObjectAccessor::FindPlayer(other);
            Send(player, "START\tDUEL\t" + (opponent ? opponent->GetName() : duel.trainerName));
            Publish(duel);
        }
        return;
    }
    if (!_enabled || !sBattlemonMgr->IsEnabled())
    {
        Send(player, "ERROR\tPet battles are disabled on this realm.");
        return;
    }
    if (command == "FORFEIT")
    {
        CancelPlayer(input.player);
        if (sBattlemonMgr->HasActiveEncounter(player))
            sBattlemonMgr->HandleAddon(player, "BM\tRUN");
        return;
    }
    if (command == "CHALLENGE")
        Challenge(player);
    else if (command == "ACCEPT" || command == "DECLINE")
    {
        auto it = _invites.find(input.player);
        if (it == _invites.end())
            return;
        Invite const invite = it->second;
        _invites.erase(it);
        Player* challenger = ObjectAccessor::FindPlayer(invite.from);
        if (command == "ACCEPT" && invite.expires >= now)
            Begin(challenger, player);
        else
            Send(challenger, "NOTICE\tYour duel invitation was declined or expired.");
        Send(player, "INVITECLOSE");
    }
    else if (command == "ACTION")
    {
        uint32 revision = 0;
        uint32 index = 0;
        std::string kind;
        if (!(stream >> revision >> kind >> index) || index > 6)
            return;
        if (kind == "MOVE" && index >= 1 && index <= 4)
            Submit(player, revision, {ActionKind::Move, static_cast<uint8>(index - 1)});
        else if (kind == "SWITCH" && index >= 1)
            Submit(player, revision, {ActionKind::Switch, static_cast<uint8>(index - 1)});
        else if (kind == "STRUGGLE" && index == 0)
            Submit(player, revision, {ActionKind::Struggle, 0});
    }
}

void BattlemonBattles::Challenge(Player* player)
{
    if (IsPlaybackBusy(player->GetGUID()))
        return;
    Player* target = ObjectAccessor::FindPlayer(player->GetTarget());
    if (!_duelsEnabled || !target || target == player || !Near(player, target)
        || IsReserved(player->GetGUID()) || IsReserved(target->GetGUID())
        || sBattlemonMgr->HasActiveEncounter(player) || sBattlemonMgr->HasActiveEncounter(target)
        || sBattlemonMgr->HasRemoteSession(player)
        || sBattlemonMgr->HasRemoteSession(target))
    {
        Send(player, "ERROR\tSelect an available nearby player or playerbot outside combat.");
        return;
    }
    if (IsBot(target))
    {
        if (_botsEnabled)
            Begin(player, target);
        else
            Send(player, "ERROR\tPlayerbot duels are disabled.");
        return;
    }
    for (auto const& pending : _invites)
        if (pending.second.from == player->GetGUID())
        {
            Send(player, "ERROR\tWait for your pending invitation to expire or be answered.");
            return;
        }
    if (_invites.count(target->GetGUID()))
    {
        Send(player, "ERROR\tThat player already has a pending invitation.");
        return;
    }
    _invites[target->GetGUID()] = {player->GetGUID(), Now() + _inviteSeconds * 1000};
    Send(target, "INVITE\t" + player->GetName());
    Send(player, "NOTICE\tDuel invitation sent to " + target->GetName() + ".");
}

void BattlemonBattles::ChallengeTrainer(Player* player, Creature* trainer)
{
    if (!player || !trainer)
        return;
    std::lock_guard<std::mutex> guard(_queueMutex);
    if (_inputs.size() < 4096)
        _inputs.push_back({player->GetGUID(), "", false, false, false, trainer->GetGUID()});
}

bool BattlemonBattles::DuelValid(Duel const& duel) const
{
    Player* player = ObjectAccessor::FindPlayer(duel.players[0]);
    if (duel.trainer.IsEmpty())
        return Near(player, ObjectAccessor::FindPlayer(duel.players[1]));
    if (!Eligible(player))
        return false;
    Creature* trainer = player->GetMap()->GetCreature(duel.trainer);
    // The player enters a private battle phase; the public trainer stays in its original phase.
    return trainer && trainer->IsAlive() && !trainer->IsInCombat()
        && trainer->GetEntry() == duel.trainerEntry && player->GetDistance(trainer) <= _distance;
}

void BattlemonBattles::BeginTrainer(Player* player, Creature* trainer)
{
    if (!_enabled || !_duelsEnabled || !sBattlemonMgr->ShouldHandle(player) || !Eligible(player)
        || !trainer || !trainer->IsAlive() || trainer->IsInCombat()
        || !BattlemonNpcTrainers::Find(trainer->GetEntry()) || !player->InSamePhase(trainer)
        || !player->IsWithinDistInMap(trainer, INTERACTION_DISTANCE) || !player->IsWithinLOSInMap(trainer)
        || IsReserved(player->GetGUID()) || IsPlaybackBusy(player->GetGUID())
        || sBattlemonMgr->HasActiveEncounter(player) || sBattlemonMgr->HasRemoteSession(player))
    {
        Send(player, "ERROR\tThe trainer is unavailable. Remain nearby and outside combat.");
        return;
    }
    Duel duel;
    duel.id = _nextId++;
    duel.players[0] = player->GetGUID();
    duel.trainer = trainer->GetGUID();
    duel.trainerEntry = trainer->GetEntry();
    duel.trainerName = trainer->GetName();
    duel.bots[1] = true;
    duel.teams[0] = sBattlemonMgr->BuildDuelParty(player, _teamSize);
    if (duel.teams[0].empty())
    {
        Send(player, "ERROR\tYou need a conscious Pokemon within your profession's level limit.");
        return;
    }
    uint32 total = 0;
    for (BattlemonBattler const& member : duel.teams[0])
        total += member.level;
    uint32 const count = static_cast<uint32>(duel.teams[0].size());
    uint32 const level = (total + count / 2) / count;
    duel.teams[1] = sBattlemonMgr->BuildTrainerTeam(trainer->GetEntry(), level, _teamSize);
    if (duel.teams[1].empty())
    {
        Send(player, "ERROR\tThis trainer's Pokemon roster is missing from the installed catalog.");
        return;
    }
    duel.deadline = Now() + _turnSeconds * 1000;
    duel.botAt = Now() + _botThinkMs;
    {
        std::lock_guard<std::mutex> guard(_queueMutex);
        _reserved.insert(player->GetGUID());
    }
    _byPlayer[player->GetGUID()] = duel.id;
    _duels.emplace(duel.id, std::move(duel));
    Duel& stored = _duels.at(_byPlayer.at(player->GetGUID()));
    BmCtx context{nullptr, sBattlemonMgr, &stored.field, false};
    context.output = [this, &stored](std::string const& text) { Broadcast(stored, "LOG\t" + text); };
    Send(player, "START\tDUEL\t" + stored.trainerName);
    BmOnSwitchIn(context, stored.teams[0][0], stored.teams[1][0]);
    BmOnSwitchIn(context, stored.teams[1][0], stored.teams[0][0]);
    Publish(stored);
}

void BattlemonBattles::Begin(Player* a, Player* b)
{
    if ((a && IsPlaybackBusy(a->GetGUID())) || (b && IsPlaybackBusy(b->GetGUID())))
        return;
    if (!Near(a, b) || IsReserved(a->GetGUID()) || IsReserved(b->GetGUID())
        || sBattlemonMgr->HasActiveEncounter(a) || sBattlemonMgr->HasActiveEncounter(b)
        || sBattlemonMgr->HasRemoteSession(a)
        || sBattlemonMgr->HasRemoteSession(b))
    {
        Send(a, "ERROR\tBoth players must remain nearby and available.");
        Send(b, "ERROR\tThe duel could not start.");
        return;
    }
    Duel duel;
    duel.id = _nextId++;
    duel.players = {a->GetGUID(), b->GetGUID()};
    duel.bots = {IsBot(a), IsBot(b)};
    duel.teams[0] = sBattlemonMgr->BuildDuelParty(a, _teamSize);
    if (duel.bots[1] && _generateBots && !duel.teams[0].empty())
    {
        uint32 totalLevel = 0;
        for (BattlemonBattler const& member : duel.teams[0])
            totalLevel += std::clamp(member.level, 1u, 100u);
        uint32 const members = static_cast<uint32>(duel.teams[0].size());
        uint32 const average = (totalLevel + members / 2) / members;
        duel.teams[1] = sBattlemonMgr->BuildGeneratedTeam(average, a->GetLevel(), _teamSize);
    }
    else
        duel.teams[1] = sBattlemonMgr->BuildDuelParty(b, _teamSize);
    if (duel.teams[0].empty() || duel.teams[1].empty())
    {
        Send(a, "ERROR\tBoth sides need at least one conscious Pokemon in their party.");
        Send(b, "ERROR\tBoth sides need at least one conscious Pokemon in their party.");
        return;
    }
    uint64 const ready = std::max(Now(), PlaybackAt(duel.players[0]));
    duel.deadline = ready + _turnSeconds * 1000;
    duel.botAt = ready + _botThinkMs;
#ifdef MOD_PLAYERBOTS
    for (Player* participant : {a, b})
        if (IsBot(participant))
            if (PlayerbotAI* ai = GET_PLAYERBOT_AI(participant))
            {
                participant->GetMotionMaster()->Clear();
                participant->StopMoving();
                ai->SetNextCheckDelay(2000);
            }
#endif
    {
        std::lock_guard<std::mutex> guard(_queueMutex);
        for (ObjectGuid guid : duel.players)
            _reserved.insert(guid);
    }
    for (ObjectGuid guid : duel.players)
    {
        _byPlayer[guid] = duel.id;
    }
    for (auto pending = _invites.begin(); pending != _invites.end();)
    {
        if (_byPlayer.count(pending->first) || _byPlayer.count(pending->second.from))
        {
            Send(ObjectAccessor::FindPlayer(pending->first), "INVITECLOSE");
            pending = _invites.erase(pending);
        }
        else
            ++pending;
    }
    _duels.emplace(duel.id, std::move(duel));
    Duel& stored = _duels.at(_byPlayer.at(a->GetGUID()));
    BmCtx context{nullptr, sBattlemonMgr, &stored.field, false};
    context.output = [this, &stored](std::string const& text) { Broadcast(stored, "LOG\t" + text); };
    Send(a, "START\tDUEL\t" + b->GetName());
    Send(b, "START\tDUEL\t" + a->GetName());
    BmOnSwitchIn(context, stored.teams[0][0], stored.teams[1][0]);
    BmOnSwitchIn(context, stored.teams[1][0], stored.teams[0][0]);
    Publish(stored);
}

int BattlemonBattles::Bench(Duel const& duel, uint8 side) const
{
    for (uint8 i = 0; i < duel.teams[side].size(); ++i)
        if (i != duel.active[side] && duel.teams[side][i].hp > 0 && !duel.teams[side][i].fainted)
            return i;
    return -1;
}

void BattlemonBattles::Switch(Duel& duel, uint8 side, uint8 index)
{
    BmOnSwitchOut(duel.teams[side][duel.active[side]]);
    duel.active[side] = index;
    duel.forced[side] = false;
    BmCtx context{nullptr, sBattlemonMgr, &duel.field, false};
    context.output = [this, &duel](std::string const& text) { Broadcast(duel, "LOG\t" + text); };
    BattlemonBattler& incoming = duel.teams[side][index];
    Broadcast(duel, "LOG\tGo, " + incoming.name + "!");
    BmOnSwitchIn(context, incoming, duel.teams[1 - side][duel.active[1 - side]]);
}

void BattlemonBattles::Submit(Player* player, uint32 revision, Action action)
{
    auto const it = _byPlayer.find(player->GetGUID());
    if (it == _byPlayer.end())
        return;
    Duel& duel = _duels.at(it->second);
    SubmitSide(duel, duel.players[0] == player->GetGUID() ? 0 : 1, revision, action);
}

void BattlemonBattles::SubmitSide(Duel& duel, uint8 side, uint32 revision, Action action)
{
    Player* player = ObjectAccessor::FindPlayer(duel.players[side]);
    if (IsPlaybackBusy(duel.players[0]) || (player && IsPlaybackBusy(player->GetGUID())))
        return;
    if (Now() >= duel.deadline)
    {
        Send(player, "ERROR\tThe turn deadline has passed.");
        return;
    }
    if (!DuelValid(duel))
    {
        Finish(duel.id, -1, "Duelists must remain nearby and outside WoW combat.");
        return;
    }
    BattlemonBattler const& active = duel.teams[side][duel.active[side]];
    if (revision != duel.revision || duel.actions[side].kind != ActionKind::None)
    {
        Send(player, "ERROR\tThat turn has already changed. Waiting for the current state.");
        Publish(duel);
        return;
    }
    bool const replacing = duel.forced[0] || duel.forced[1];
    if (replacing && (!duel.forced[side] || action.kind != ActionKind::Switch))
    {
        Send(player, "ERROR\tChoose a conscious replacement before the next round.");
        return;
    }
    if (action.kind == ActionKind::Switch)
    {
        if (action.index >= duel.teams[side].size() || action.index == duel.active[side]
            || duel.teams[side][action.index].hp <= 0 || duel.teams[side][action.index].fainted)
        {
            Send(player, "ERROR\tThat Pokemon cannot switch in.");
            return;
        }
        if (replacing)
        {
            Switch(duel, side, action.index);
            ++duel.revision;
            duel.deadline = Now() + _turnSeconds * 1000;
            duel.botAt = Now() + _botThinkMs;
            Publish(duel);
            return;
        }
    }
    else if (active.hp <= 0 || active.fainted)
        return;
    else if (action.kind == ActionKind::Move)
    {
        if (action.index >= active.moves.size() || !active.moves[action.index].def
            || (!active.charging && !active.mustRecharge && active.moves[action.index].pp <= 0))
        {
            Send(player, "ERROR\tThat move has no PP or is unavailable.");
            return;
        }
        if (!BmMoveAllowed(active, active.moves[action.index]))
        {
            Send(player, "ERROR\tLocked into " + active.choiceMove + " by its Choice item.");
            return;
        }
    }
    else if (action.kind == ActionKind::Struggle)
    {
        if (std::any_of(active.moves.begin(), active.moves.end(), [](BattlemonSlot const& move)
            { return move.def && move.pp > 0; }))
        {
            Send(player, "ERROR\tUse an available move before Struggle.");
            return;
        }
    }
    else
        return;
    duel.actions[side] = action;
    Send(player, "WAIT");
    if (duel.actions[0].kind != ActionKind::None && duel.actions[1].kind != ActionKind::None)
        Resolve(duel);
}

void BattlemonBattles::Resolve(Duel& duel)
{
    auto priority = [&duel](uint8 side)
    {
        Action const action = duel.actions[side];
        if (action.kind == ActionKind::Switch)
            return 100;
        BattlemonBattler const& battler = duel.teams[side][duel.active[side]];
        if (battler.charging)
            if (BattlemonMoveDef const* move = sBattlemonMgr->GetMove(battler.chargeMove))
                return move->priority;
        return action.kind == ActionKind::Move ? battler.moves[action.index].def->priority : 0;
    };
    int32 const priorityA = priority(0);
    int32 const priorityB = priority(1);
    uint32 const speedA = BmEffectiveSpeed(duel.teams[0][duel.active[0]], duel.field);
    uint32 const speedB = BmEffectiveSpeed(duel.teams[1][duel.active[1]], duel.field);
    uint8 const first = priorityA > priorityB || (priorityA == priorityB
        && (speedA > speedB || (speedA == speedB && urand(0, 1)))) ? 0 : 1;
    BmCtx context{nullptr, sBattlemonMgr, &duel.field, false};
    context.output = [this, &duel](std::string const& text) { Broadcast(duel, "LOG\t" + text); };
    for (uint8 step = 0; step < 2; ++step)
    {
        uint8 const side = step == 0 ? first : 1 - first;
        Action const action = duel.actions[side];
        if (action.kind == ActionKind::Switch)
        {
            Switch(duel, side, action.index);
            continue;
        }
        BattlemonBattler& actor = duel.teams[side][duel.active[side]];
        BattlemonBattler& target = duel.teams[1 - side][duel.active[1 - side]];
        if (actor.fainted || actor.hp <= 0 || target.fainted || target.hp <= 0)
            continue;
        context.uturn = false;
        BattlemonSlot struggle;
        BattlemonMoveDef fallback;
        BattlemonSlot* move = nullptr;
        if (action.kind == ActionKind::Move)
            move = &actor.moves[action.index];
        else
        {
            struggle.def = sBattlemonMgr->GetMove("STRUGGLE");
            if (!struggle.def)
            {
                fallback.internalName = "STRUGGLE";
                fallback.name = "Struggle";
                fallback.type = "NORMAL";
                fallback.category = "Physical";
                fallback.power = 50;
                fallback.accuracy = 100;
                fallback.functionCode = "RecoilQuarterOfDamageDealt";
                struggle.def = &fallback;
            }
            move = &struggle;
        }
        context.animation = [this, &duel, owner = duel.players[0]](bool playerSide, std::string const& moveName)
        {
            Animate(owner, playerSide ? 0 : 1, moveName);
            auto scene = _scenes.find(owner);
            uint64 const until = scene == _scenes.end() ? Now() : scene->second.animationAt;
            for (ObjectGuid participant : duel.players)
                SetPlayback(participant, until);
        };
        BmRunSingleAction(context, actor, target, move, side == 0);
        for (uint8 viewer = 0; viewer < 2; ++viewer)
            for (uint8 relative = 0; relative < 2; ++relative)
            {
                uint8 const index = relative == 0 ? viewer : 1 - viewer;
                Send(ObjectAccessor::FindPlayer(duel.players[viewer]), sBattlemonMgr->FormatBattlerState(
                    duel.teams[index][duel.active[index]], relative == 0 ? 'P' : 'E').substr(3));
            }
        if (context.uturn && actor.hp > 0 && Bench(duel, side) >= 0)
            duel.forced[side] = true;
    }
    BattlemonBattler& a = duel.teams[0][duel.active[0]];
    BattlemonBattler& b = duel.teams[1][duel.active[1]];
    // Clear one-turn effects and process the survivor even when its opponent fainted.
    BmEndOfRound(context, a, b);
    std::array<bool, 2> defeated = {};
    for (uint8 side = 0; side < 2; ++side)
    {
        BattlemonBattler& active = duel.teams[side][duel.active[side]];
        if (active.hp <= 0 || active.fainted)
        {
            active.fainted = true;
            duel.forced[side] = Bench(duel, side) >= 0;
            defeated[side] = !duel.forced[side];
        }
    }
    if (defeated[0] || defeated[1])
    {
        Publish(duel);
        Finish(duel.id, defeated[0] && defeated[1] ? -1 : (defeated[0] ? 1 : 0), "Battle finished.");
        return;
    }
    duel.actions = {};
    ++duel.revision;
    uint64 const ready = std::max(Now(), PlaybackAt(duel.players[0]));
    duel.deadline = ready + _turnSeconds * 1000;
    duel.botAt = ready + _botThinkMs;
    Publish(duel);
}

void BattlemonBattles::Publish(Duel& duel)
{
    for (uint8 side = 0; side < 2; ++side)
    {
        Player* player = ObjectAccessor::FindPlayer(duel.players[side]);
        if (!player || IsBot(player))
            continue;
        for (uint8 relative = 0; relative < 2; ++relative)
        {
            uint8 const index = relative == 0 ? side : 1 - side;
            BattlemonBattler const& active = duel.teams[index][duel.active[index]];
            std::string const encoded = sBattlemonMgr->FormatBattlerState(active, relative == 0 ? 'P' : 'E');
            Send(player, encoded.substr(3));
            Send(player, std::string("AIL\t") + (relative == 0 ? "P\t" : "E\t") + BmStatusCode(active.status));
        }
        Send(player, "TEAMCLEAR");
        for (uint8 i = 0; i < duel.teams[side].size(); ++i)
        {
            BattlemonBattler const& battler = duel.teams[side][i];
            Send(player, Acore::StringFormat("TEAM\t{}\t{}\t{}\t{}\t{}\t{}", i + 1, battler.name,
                battler.level, battler.hp, battler.maxHp, duel.active[side] == i ? 1 : 0));
        }
        Send(player, "WEATHER\t" + BmWeatherCode(duel.field.weather));
        uint64 const ready = std::max(Now(), PlaybackAt(player->GetGUID()));
        uint64 const remaining = duel.deadline > ready ? (duel.deadline - ready + 999) / 1000 : 0;
        std::string const phase = duel.forced[side] ? "SWITCH"
            : (duel.forced[1 - side] || duel.actions[side].kind != ActionKind::None ? "WAIT" : "CHOOSE");
        Send(player, Acore::StringFormat("TURN\t{}\t{}\t{}", duel.revision, phase, remaining));
    }
    if (Player* owner = ObjectAccessor::FindPlayer(duel.players[0]))
        ShowScene(owner, duel.teams[0][duel.active[0]], duel.teams[1][duel.active[1]]);
}

void BattlemonBattles::BotChoose(Duel& duel, uint8 side)
{
    if (!duel.bots[side] || duel.actions[side].kind != ActionKind::None)
        return;
    Player* bot = ObjectAccessor::FindPlayer(duel.players[side]);
    if (!bot && (side != 1 || duel.trainer.IsEmpty()))
        return;
    if (duel.forced[side])
    {
        int const replacement = Bench(duel, side);
        if (replacement >= 0)
            SubmitSide(duel, side, duel.revision, {ActionKind::Switch, static_cast<uint8>(replacement)});
        return;
    }
    if (duel.forced[1 - side])
        return;
    BattlemonBattler const& actor = duel.teams[side][duel.active[side]];
    BattlemonBattler const& target = duel.teams[1 - side][duel.active[1 - side]];
    int best = -1;
    float bestScore = -1.0f;
    for (uint8 i = 0; i < actor.moves.size(); ++i)
    {
        BattlemonSlot const& slot = actor.moves[i];
        if (!slot.def || (slot.pp <= 0 && !actor.charging && !actor.mustRecharge))
            continue;
        BattlemonMoveDef const& move = *slot.def;
        float const effect = sBattlemonMgr->TypeChartMul(move.type, BmType1(target))
            * sBattlemonMgr->TypeChartMul(move.type, BmType2(target));
        float score = std::max(0, move.power) * effect * (BmHasType(actor, move.type.c_str()) ? 1.5f : 1.0f);
        score *= move.accuracy <= 0 ? 1.0f : move.accuracy / 100.0f;
        if (!move.power)
            score = target.status == BmStatus::None ? 25.0f : 5.0f;
        if (actor.hp < actor.maxHp / 2 && move.functionCode.find("HealUser") != std::string::npos)
            score += 60.0f;
        score += frand(0.0f, 12.0f);
        if (score > bestScore)
        {
            bestScore = score;
            best = i;
        }
    }
    if (best < 0)
        SubmitSide(duel, side, duel.revision, {ActionKind::Struggle, 0});
    else
        SubmitSide(duel, side, duel.revision, {ActionKind::Move, static_cast<uint8>(best)});
}

void BattlemonBattles::Finish(uint64 id, int winner, std::string const& reason)
{
    auto it = _duels.find(id);
    if (it == _duels.end())
        return;
    std::array<ObjectGuid, 2> const players = it->second.players;
    if (!it->second.trainer.IsEmpty() && winner == 0)
        BattlemonTrainerProgression::AwardPractice(ObjectAccessor::FindPlayer(players[0]));
    for (uint8 side = 0; side < 2; ++side)
    {
        if (players[side].IsEmpty())
            continue;
        Player* player = ObjectAccessor::FindPlayer(players[side]);
        Send(player, "LOG\t" + reason);
        Send(player, std::string("END\t") + (winner < 0 ? "DRAW" : (winner == side ? "WIN" : "LOSE")));
#ifdef MOD_PLAYERBOTS
        if (IsBot(player))
            if (PlayerbotAI* ai = GET_PLAYERBOT_AI(player))
                ai->SetNextCheckDelay(0);
#endif
        _byPlayer.erase(players[side]);
        EndScene(players[side]);
    }
    _duels.erase(it);
    std::lock_guard<std::mutex> guard(_queueMutex);
    for (ObjectGuid guid : players)
        _reserved.erase(guid);
}

void BattlemonBattles::CancelPlayer(ObjectGuid player)
{
    if (auto it = _byPlayer.find(player); it != _byPlayer.end())
        for (ObjectGuid participant : _duels.at(it->second).players)
            ClearPlayback(participant);
    ClearPlayback(player);
    if (auto it = _byPlayer.find(player); it != _byPlayer.end())
    {
        Duel const& duel = _duels.at(it->second);
        Finish(duel.id, duel.players[0] == player ? 1 : 0, "Opponent left the duel.");
    }
    for (auto it = _invites.begin(); it != _invites.end();)
    {
        if (it->first == player || it->second.from == player)
        {
            Send(ObjectAccessor::FindPlayer(it->first), "INVITECLOSE");
            it = _invites.erase(it);
        }
        else
            ++it;
    }
    ClearScene(player);
}

void BattlemonBattles::OnCatalogReload()
{
    std::vector<ObjectGuid> playing;
    {
        std::lock_guard<std::mutex> guard(_queueMutex);
        for (auto const& entry : _playbackUntil)
            playing.push_back(entry.first);
    }
    for (ObjectGuid player : playing)
        ClearPlayback(player);
    while (!_duels.empty())
        Finish(_duels.begin()->first, -1, "Pet battles reset for a configuration or catalog reload.");
    while (!_scenes.empty())
        ClearScene(_scenes.begin()->first);
    for (auto const& invite : _invites)
        Send(ObjectAccessor::FindPlayer(invite.first), "INVITECLOSE");
    _invites.clear();
}

void BattlemonBattles::Poll()
{
    uint64 const now = Now();
    for (auto it = _invites.begin(); it != _invites.end();)
    {
        if (it->second.expires < now)
        {
            Send(ObjectAccessor::FindPlayer(it->first), "INVITECLOSE");
            Send(ObjectAccessor::FindPlayer(it->second.from), "NOTICE\tDuel invitation expired.");
            it = _invites.erase(it);
        }
        else
            ++it;
    }
    // A bot action may finish/erase its duel. Iterate stable ids and re-resolve.
    std::vector<uint64> ids;
    for (auto const& entry : _duels)
        ids.push_back(entry.first);
    for (uint64 id : ids)
    {
        auto it = _duels.find(id);
        if (it == _duels.end())
            continue;
        Duel& duel = it->second;
        Player* a = ObjectAccessor::FindPlayer(duel.players[0]);
        Player* b = ObjectAccessor::FindPlayer(duel.players[1]);
        if (!DuelValid(duel) || !SceneValid(duel.players[0]))
        {
            int const winner = !duel.trainer.IsEmpty() ? -1 : (!Eligible(a) ? 1 : (!Eligible(b) ? 0 : -1));
            Finish(id, winner, "Duel ended: a player left, entered combat or moved out of range.");
            continue;
        }
#ifdef MOD_PLAYERBOTS
        for (Player* participant : {a, b})
            if (IsBot(participant))
                if (PlayerbotAI* ai = GET_PLAYERBOT_AI(participant))
                    ai->SetNextCheckDelay(2000);
#endif
        if (now >= duel.deadline)
        {
            bool const owesA = duel.forced[0] || (!duel.forced[1] && duel.actions[0].kind == ActionKind::None);
            bool const owesB = duel.forced[1] || (!duel.forced[0] && duel.actions[1].kind == ActionKind::None);
            Finish(id, owesA == owesB ? -1 : (owesA ? 1 : 0), "Turn timed out.");
            continue;
        }
        if (now >= duel.botAt)
        {
            BotChoose(duel, 0);
            it = _duels.find(id);
            if (it != _duels.end())
                BotChoose(it->second, 1);
        }
    }
    std::vector<ObjectGuid> finishedScenes;
    for (auto const& entry : _scenes)
        if (entry.second.ending && (now >= entry.second.animationAt || !SceneValid(entry.first)))
            finishedScenes.push_back(entry.first);
    for (ObjectGuid owner : finishedScenes)
        ClearScene(owner);
    for (auto const& preference : _preferences)
    {
        auto scene = _scenes.find(preference.first);
        if (scene != _scenes.end() && scene->second.ending)
            continue;
        if (_byPlayer.count(preference.first))
            continue;
        Player* player = ObjectAccessor::FindPlayer(preference.first);
        BattlemonEncounter encounter;
        bool const active = player && sBattlemonMgr->GetBattleSnapshot(player, encounter);
        if (!active || !PetMode(preference.first))
        {
            ClearScene(preference.first);
            continue;
        }
        if (!Eligible(player) || !SceneValid(preference.first))
        {
            sBattlemonMgr->RunAway(player);
            ClearScene(preference.first);
            continue;
        }
        if (encounter.activeSlot && encounter.activeSlot <= encounter.party.size())
            ShowScene(player, encounter.party[encounter.activeSlot - 1], encounter.enemy);
    }
}

void BattlemonBattles::EndScene(ObjectGuid owner)
{
    auto it = _scenes.find(owner);
    if (it != _scenes.end() && it->second.animationAt > Now() && SceneValid(owner))
        it->second.ending = true;
    else
        ClearScene(owner);
}

void BattlemonBattles::ClearScene(ObjectGuid owner)
{
    auto it = _scenes.find(owner);
    if (it == _scenes.end())
        return;
    if (Map* map = sMapMgr->FindMap(it->second.map, it->second.instance))
    {
        for (ObjectGuid guid : it->second.actors)
            if (Creature* actor = map->GetCreature(guid))
                actor->DespawnOrUnsummon();
        for (ObjectGuid guid : it->second.effects)
            if (Creature* effect = map->GetCreature(guid))
                effect->DespawnOrUnsummon();
    }
    for (uint8 side = 0; side < 2; ++side)
        if (Player* player = ObjectAccessor::FindPlayer(it->second.participants[side]))
            if (it->second.phase && player->GetPhaseMask() == it->second.phase)
                player->SetPhaseMask(it->second.previousPhases[side], true);
    _scenes.erase(it);
}

void BattlemonBattles::ShowScene(Player* owner, BattlemonBattler const& a, BattlemonBattler const& b)
{
    if (!_worldActors || !owner || !sObjectMgr->GetCreatureTemplate(_actorEntry))
        return;
    auto previous = _scenes.find(owner->GetGUID());
    if (previous != _scenes.end() && previous->second.ending)
        ClearScene(owner->GetGUID());
    auto [it, added] = _scenes.try_emplace(owner->GetGUID());
    Scene& scene = it->second;
    if (added)
    {
        scene.origin = owner->GetPosition();
        scene.map = owner->GetMapId();
        scene.instance = owner->GetInstanceId();
        scene.participants[0] = owner->GetGUID();
        if (auto duel = _byPlayer.find(owner->GetGUID()); duel != _byPlayer.end())
            scene.participants = _duels.at(duel->second).players;
        // ANYWHERE means visible in every phase, not ownership of every phase bit.
        // In particular, a GM observer must not exhaust the entire battle phase pool.
        uint32 occupied = PHASEMASK_NORMAL;
        auto reserve = [&occupied](uint32 mask)
        {
            if (mask != PHASEMASK_ANYWHERE)
                occupied |= mask;
        };
        for (auto const& spawn : sObjectMgr->GetAllCreatureData())
            if (spawn.second.mapid == scene.map)
                reserve(spawn.second.phaseMask);
        for (auto const& spawn : sObjectMgr->GetAllGOData())
            if (spawn.second.mapid == scene.map)
                reserve(spawn.second.phaseMask);
        for (auto const& existing : _scenes)
            if (existing.second.map == scene.map && existing.second.instance == scene.instance)
                reserve(existing.second.phase);
        for (auto const& reference : owner->GetMap()->GetPlayers())
            if (Player* player = reference.GetSource())
                reserve(player->GetPhaseMask());
        for (uint32 bit = 0x40000000; bit >= 0x00010000; bit >>= 1)
            if (!(occupied & bit))
            {
                scene.phase = bit;
                break;
            }
        if (!scene.phase)
        {
            Send(owner, "NOTICE\tNo private battle phase is available. Battle cancelled.");
            return;
        }
        for (uint8 side = 0; side < 2; ++side)
            if (Player* player = ObjectAccessor::FindPlayer(scene.participants[side]))
            {
                scene.previousPhases[side] = player->GetPhaseMask();
                player->SetPhaseMask(scene.phase, true);
            }
    }
    if (!SceneValid(owner->GetGUID()))
        return;
    std::array<BattlemonBattler const*, 2> const battlers = {&a, &b};
    for (uint8 side = 0; side < 2; ++side)
    {
        BattlemonBattler const& battler = *battlers[side];
        uint32 const display = BattlemonOverworld::DisplayId(battler.formId, battler.shiny);
        if (!sCreatureDisplayInfoStore.LookupEntry(display))
            continue;
        Creature* actor = owner->GetMap()->GetCreature(scene.actors[side]);
        if (actor && scene.displays[side] == display)
        {
            actor->SetMaxHealth(static_cast<uint32>(std::max(1, battler.maxHp)));
            actor->SetHealth(static_cast<uint32>(std::max(1, battler.hp)));
            continue;
        }
        if (actor)
            actor->DespawnOrUnsummon();
        float const facing = scene.origin.GetOrientation();
        float const lateral = side == 0 ? -7.0f : 7.0f;
        float const x = scene.origin.GetPositionX() + 8.0f * std::cos(facing) - lateral * std::sin(facing);
        float const y = scene.origin.GetPositionY() + 8.0f * std::sin(facing) + lateral * std::cos(facing);
        float z = scene.origin.GetPositionZ();
        owner->UpdateAllowedPositionZ(x, y, z);
        actor = owner->SummonCreature(_actorEntry, x, y, z, facing + (side == 0 ? Pi / 2 : -Pi / 2),
            TEMPSUMMON_TIMED_DESPAWN, ActorLifetimeMs);
        if (!actor)
            continue;
        actor->SetPhaseMask(scene.phase, true);
        scene.homes[side] = actor->GetPosition();
        actor->SetReactState(REACT_PASSIVE);
        actor->SetImmuneToAll(true);
        actor->ReplaceAllNpcFlags(UNIT_NPC_FLAG_NONE);
        actor->SetUnitFlag(UNIT_FLAG_NOT_SELECTABLE);
        actor->SetDisplayId(display);
        actor->SetNativeDisplayId(display);
        actor->SetName(battler.name);
        actor->SetMaxHealth(static_cast<uint32>(std::max(1, battler.maxHp)));
        actor->SetHealth(static_cast<uint32>(std::max(1, battler.hp)));
        float scale = 1.0f;
        float hover = 0.0f;
        sBattlemonOverworld->ComputeNudge(battler.formId, scale, hover);
        actor->SetObjectScale(scale);
        actor->StopMoving();
        scene.actors[side] = actor->GetGUID();
        scene.displays[side] = display;
    }
}

void BattlemonBattles::Leave(Player* player)
{
    if (player)
        CancelPlayer(player->GetGUID());
}

bool BattlemonBattles::SceneValid(ObjectGuid owner) const
{
    auto it = _scenes.find(owner);
    if (it == _scenes.end())
        return true;
    Scene const& scene = it->second;
    if (!scene.phase)
        return false;
    for (ObjectGuid guid : scene.participants)
    {
        if (guid.IsEmpty())
            continue;
        Player* player = ObjectAccessor::FindPlayer(guid);
        if (!player || player->GetMapId() != scene.map || player->GetInstanceId() != scene.instance
            || player->GetPhaseMask() != scene.phase || player->GetDistance(scene.origin) > _distance)
            return false;
    }
    return true;
}

void BattlemonBattles::Animate(ObjectGuid owner, uint8 side, std::string const& move)
{
    if (_nativeSpellVisuals && AnimateNative(owner, side, move))
        return;
    auto it = _scenes.find(owner);
    if (it == _scenes.end() || side > 1)
        return;
    Scene& scene = it->second;
    uint64 const now = Now();
    uint64 const at = std::max(now, scene.animationAt);
    auto plan = BattlemonEffects::Plans.find(move);
    static std::vector<BattlemonEffects::Action> const fallback = {{1, 0, 0, 1100, false, false}};
    auto const& actions = plan == BattlemonEffects::Plans.end() ? fallback : plan->second;
    uint32 duration = 1100;
    for (auto const& action : actions)
        duration = std::max(duration, action.delay + action.duration);
    scene.animationAt = at + duration + 100;
    ObjectGuid const actorGuid = scene.actors[side];
    Position const home = scene.homes[side];
    Position const target = scene.homes[1 - side];
    uint32 const mapId = scene.map;
    uint32 const instance = scene.instance;
    auto resolve = [this, owner, side, actorGuid, mapId, instance]() -> Creature*
    {
        auto current = _scenes.find(owner);
        if (current == _scenes.end() || current->second.actors[side] != actorGuid)
            return nullptr;
        Map* map = sMapMgr->FindMap(mapId, instance);
        return map ? map->GetCreature(actorGuid) : nullptr;
    };
    for (auto const& action : actions)
    {
        uint64 const delay = at - now + action.delay;
        if (action.kind == 0)
        {
            _scheduler.Schedule(std::chrono::milliseconds(delay),
                [this, resolve, owner, home, target, action](TaskContext)
            {
                Creature* actor = resolve();
                Player* player = ObjectAccessor::FindPlayer(owner);
                if (!actor || !player || !sCreatureDisplayInfoStore.LookupEntry(action.display))
                    return;
                Position origin = action.target || action.inverted ? target : home;
                Position endpoint = action.inverted ? home : target;
                origin.m_positionZ += 1.25f;
                origin.SetOrientation(std::atan2(endpoint.GetPositionY() - origin.GetPositionY(),
                    endpoint.GetPositionX() - origin.GetPositionX()));
                Creature* effect = player->SummonCreature(_actorEntry, origin,
                    TEMPSUMMON_TIMED_DESPAWN, action.duration);
                if (!effect)
                    return;
                effect->SetPhaseMask(actor->GetPhaseMask(), true);
                effect->SetReactState(REACT_PASSIVE);
                effect->SetImmuneToAll(true);
                effect->ReplaceAllNpcFlags(UNIT_NPC_FLAG_NONE);
                effect->SetUnitFlag(UNIT_FLAG_NOT_SELECTABLE);
                effect->SetDisplayId(action.display);
                effect->SetNativeDisplayId(action.display);
                effect->SetObjectScale(1.0f);
                effect->SetName("");
                _scenes.at(owner).effects.push_back(effect->GetGUID());
            });
            continue;
        }
        _scheduler.Schedule(std::chrono::milliseconds(delay), [resolve, home, target, action](TaskContext)
        {
            if (Creature* actor = resolve())
            {
                actor->HandleEmoteCommand(EMOTE_ONESHOT_ATTACK1H);
                Position forward = home;
                float const fraction = action.kind == 2 ? 0.3f : 0.12f;
                forward.m_positionX += (target.GetPositionX() - home.GetPositionX()) * fraction;
                forward.m_positionY += (target.GetPositionY() - home.GetPositionY()) * fraction;
                if (action.kind == 3)
                    actor->GetMotionMaster()->MoveJump(home, 1.0f, 5.0f, MotionStomp);
                else if (action.kind == 1)
                    actor->GetMotionMaster()->MoveJump(forward, 6.0f, 3.0f, MotionAdvance);
                else
                    actor->GetMotionMaster()->MovePoint(MotionAdvance, forward, FORCED_MOVEMENT_RUN, 6.0f, false);
            }
        });
        _scheduler.Schedule(std::chrono::milliseconds(delay + action.duration / 2),
            [resolve, home](TaskContext)
        {
            if (Creature* actor = resolve())
                actor->GetMotionMaster()->MovePoint(MotionReturn, home, FORCED_MOVEMENT_RUN, 6.0f, false);
        });
        _scheduler.Schedule(std::chrono::milliseconds(delay + action.duration),
            [resolve, home](TaskContext)
        {
            if (Creature* actor = resolve())
                actor->SetFacingTo(home.GetOrientation());
        });
    }
}

bool BattlemonBattles::AnimateNative(ObjectGuid owner, uint8 side, std::string const& move)
{
    auto it = _scenes.find(owner);
    if (it == _scenes.end() || side > 1 || !SceneValid(owner))
        return false;
    BattlemonMoveDef const* definition = sBattlemonMgr->GetMove(move);
    auto const profile = BattlemonNativeEffects::Select(move, definition ? definition->type : "NORMAL",
        definition ? definition->category : "Physical");
    SpellEntry const* spell = sSpellStore.LookupEntry(profile.spell);
    if (!spell || !spell->SpellVisual[0] || !sSpellVisualStore.LookupEntry(spell->SpellVisual[0]))
        return false;

    Scene& scene = it->second;
    uint8 const targetSide = profile.self ? side : 1 - side;
    ObjectGuid const actorGuid = scene.actors[side];
    ObjectGuid const targetGuid = scene.actors[targetSide];
    Position const home = scene.homes[side];
    Position const destination = scene.homes[targetSide];
    uint32 const mapId = scene.map;
    uint32 const instance = scene.instance;
    auto resolve = [this, owner, side, targetSide, actorGuid, targetGuid, mapId, instance]()
        -> std::pair<Creature*, Creature*>
    {
        auto current = _scenes.find(owner);
        if (current == _scenes.end() || current->second.actors[side] != actorGuid
            || current->second.actors[targetSide] != targetGuid || !SceneValid(owner))
            return {nullptr, nullptr};
        Map* map = sMapMgr->FindMap(mapId, instance);
        if (!map)
            return {nullptr, nullptr};
        return {map->GetCreature(actorGuid), map->GetCreature(targetGuid)};
    };
    auto [actor, target] = resolve();
    if (!actor || !target)
        return false;
    uint32 const flight = spell->Speed > 0.0f && !profile.self
        ? static_cast<uint32>(std::clamp(actor->GetDistance(target) / spell->Speed * 1000.0f, 0.0f, 1200.0f)) : 0;
    uint64 const now = Now();
    uint64 const delay = std::max(now, scene.animationAt) - now;
    uint32 const finish = profile.windup + (profile.repeats - 1) * profile.interval + flight + 450;
    scene.animationAt = now + delay + finish;
    uint8 const firstCast = ++scene.visualCast;
    scene.visualCast += static_cast<uint8>(profile.repeats - 1);

    _scheduler.Schedule(std::chrono::milliseconds(delay), [resolve, home, destination, profile, firstCast](TaskContext)
    {
        auto [caster, victim] = resolve();
        if (!caster || !victim)
            return;
        caster->SetFacingTo(home.GetOrientation());
        if (profile.lunge && !profile.self)
        {
            Position forward = home;
            forward.m_positionX += (destination.GetPositionX() - home.GetPositionX()) * 0.32f;
            forward.m_positionY += (destination.GetPositionY() - home.GetPositionY()) * 0.32f;
            caster->GetMotionMaster()->MovePoint(MotionAdvance, forward, FORCED_MOVEMENT_RUN, 14.0f, false);
        }
        SendNativeVisual(caster, victim, profile.spell, firstCast, profile.windup, false);
    });
    for (uint32 pulse = 0; pulse < profile.repeats; ++pulse)
    {
        uint64 const launch = delay + profile.windup + pulse * profile.interval;
        _scheduler.Schedule(std::chrono::milliseconds(launch), [resolve, profile, firstCast, pulse](TaskContext)
        {
            auto [caster, victim] = resolve();
            if (!caster || !victim)
                return;
            if (profile.lunge)
                caster->HandleEmoteCommand(EMOTE_ONESHOT_ATTACK1H);
            SendNativeVisual(caster, victim, profile.spell, static_cast<uint8>(firstCast + pulse), 0, true);
        });
        if (!profile.self)
            _scheduler.Schedule(std::chrono::milliseconds(launch + flight), [resolve](TaskContext)
            {
                auto [caster, victim] = resolve();
                if (caster && victim)
                    victim->HandleEmoteCommand(EMOTE_ONESHOT_WOUND);
            });
    }
    if (profile.lunge)
        _scheduler.Schedule(std::chrono::milliseconds(delay + profile.windup + 120), [resolve, home](TaskContext)
        {
            auto [caster, victim] = resolve();
            if (caster && victim)
                caster->GetMotionMaster()->MovePoint(MotionReturn, home, FORCED_MOVEMENT_RUN, 14.0f, false);
        });
    _scheduler.Schedule(std::chrono::milliseconds(delay + finish - 20), [resolve, home](TaskContext)
    {
        auto [caster, victim] = resolve();
        if (caster && victim)
            caster->SetFacingTo(home.GetOrientation());
    });
    return true;
}
