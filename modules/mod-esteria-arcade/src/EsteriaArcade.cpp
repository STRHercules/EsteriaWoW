/*
 * Esteria arcade cabinets. A cabinet is a gameobject (type 2, ScriptName go_esteria_arcade) whose entry has a row in
 * esteria_arcade_cabinet naming the game and the price. Paying starts a session: the server sends the game and the
 * character's saved battery RAM + resume state (character_arcade_save) to the client's Arcade extension, which runs
 * the libretro core. Battery RAM comes back every 30 s while it changes; on quit the client sends both and QUIT.
 * Walking away (or a teleport, or logging out) ends the session: STOP goes to the client, which uploads and quits;
 * uploads are accepted for a grace period after that.
 * Spectators: the player's client streams a small picture of the cabinet screen (VIEW); the server relays it to the
 * players around (same packet, with the cabinet guid) and sends VIEW_END when the game stops. One player per cabinet.
 *
 * Wire: see wowdecomp Extensions/Arcade/src/Arcade.cpp. Blobs are opaque to the server ([u32 rawSize][zlib]).
 */
#include "Chat.h"
#include "DatabaseEnv.h"
#include "GameObject.h"
#include "GameObjectScript.h"
#include "Log.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "ScriptedGossip.h"
#include "ServerScript.h"
#include "StringFormat.h"
#include "WorldPacket.h"
#include "WorldScript.h"
#include "WorldSession.h"

#include <unordered_map>

namespace
{
    enum : uint8 { S_START = 1, S_DATA = 2, S_STOP = 3, S_VIEW = 4, S_VIEW_END = 5, C_DATA = 1, C_QUIT = 2, C_VIEW = 3 };
    enum : uint8 { KIND_SRAM = 0, KIND_STATE = 1 };
    constexpr uint32 CHUNK = 8000;
    constexpr uint32 MAX_BLOB = 16u << 20;
    constexpr float REACH = 8.0f;          // yards from the cabinet before the game stops
    constexpr uint32 GRACE_MS = 60000;     // how long a stopped session still accepts its final uploads
    constexpr uint32 TEXT_ID = 3610001;    // "The cabinet hums..."
    constexpr float VIEW_RANGE = 60.0f;    // spectators within this many yards of the player see the stream
    constexpr uint32 VIEW_BYTES_PER_SECOND = 96 * 1024; // relayed per session; more is dropped (the client resyncs)
    enum Action : uint32 { ACTION_PLAY = 1, ACTION_STOP = 2 };

    struct Game { std::string title, core, rom; };
    struct Cabinet { uint32 game = 0; uint32 price = 0; };

    std::unordered_map<uint32, Game> games;
    std::unordered_map<uint32, Cabinet> cabinets; // by gameobject entry

    struct Upload
    {
        std::vector<uint8> data;
        uint32 got = 0;
    };

    struct Session
    {
        uint32 id = 0;
        uint32 account = 0;
        uint32 game = 0;
        ObjectGuid player;
        ObjectGuid cabinet;
        uint32 map = 0;
        float x = 0, y = 0, z = 0;
        bool stopping = false;
        uint32 stoppedAt = 0;
        uint32 viewSecond = 0, viewBytes = 0;
        Upload up[2];
    };

    // By session id. A stopped session stays for GRACE_MS so its final uploads (sent while walking away, logging out
    // or starting another cabinet) still land; active maps each account to its one running session.
    std::unordered_map<uint32, Session> sessions;
    std::unordered_map<uint32, uint32> active;
    uint32 lastSessionId = 0;

    Session* Active(uint32 account)
    {
        auto a = active.find(account);
        if (a == active.end())
            return nullptr;
        auto s = sessions.find(a->second);
        return s == sessions.end() || s->second.stopping ? nullptr : &s->second;
    }

    std::string Hex(std::vector<uint8> const& data)
    {
        static char const digits[] = "0123456789ABCDEF";
        std::string out;
        out.reserve(data.size() * 2);
        for (uint8 b : data)
        {
            out += digits[b >> 4];
            out += digits[b & 15];
        }
        return out;
    }

    void Store(Session const& s, uint8 kind, std::vector<uint8> const& blob)
    {
        char const* column = kind == KIND_SRAM ? "sram" : "state";
        CharacterDatabase.Execute(Acore::StringFormat(
            "INSERT INTO `character_arcade_save` (`guid`, `game`, `{0}`) VALUES ({1}, {2}, X'{3}') "
            "ON DUPLICATE KEY UPDATE `{0}` = VALUES(`{0}`), `updated` = CURRENT_TIMESTAMP",
            column, s.player.GetCounter(), s.game, Hex(blob)));
    }

    void SendBlob(WorldSession* session, uint32 id, uint8 kind, std::vector<uint8> const& blob)
    {
        uint32 const total = uint32(blob.size());
        for (uint32 offset = 0; offset < total; offset += CHUNK)
        {
            uint32 const n = std::min(CHUNK, total - offset);
            WorldPacket data(SMSG_ESTERIA_ARCADE, 14 + n);
            data << uint8(S_DATA) << id << kind << total << offset;
            data.append(blob.data() + offset, n);
            session->SendPacket(&data);
        }
    }

    // Tells the players around that the cabinet's screen goes back to its attract picture.
    void SendViewEnd(Session const& s)
    {
        if (Player* player = ObjectAccessor::FindConnectedPlayer(s.player); player && player->IsInWorld())
        {
            WorldPacket data(SMSG_ESTERIA_ARCADE, 13);
            data << uint8(S_VIEW_END) << s.id << s.cabinet.GetRawValue();
            player->SendMessageToSetInRange(&data, VIEW_RANGE, false);
        }
    }

    bool CabinetBusy(ObjectGuid cabinet, uint32 account)
    {
        for (auto const& [id, s] : sessions)
            if (!s.stopping && s.cabinet == cabinet && s.account != account)
                return true;
        return false;
    }

    void SendStop(WorldSession* session, Session& s, char const* reason)
    {
        if (s.stopping)
            return;
        s.stopping = true;
        s.stoppedAt = getMSTime();
        active.erase(s.account);
        SendViewEnd(s);
        if (session)
        {
            WorldPacket data(SMSG_ESTERIA_ARCADE, 6 + strlen(reason));
            data << uint8(S_STOP) << s.id << std::string(reason);
            session->SendPacket(&data);
        }
    }

    void Start(Player* player, GameObject* go, Cabinet const& cabinet)
    {
        auto game = games.find(cabinet.game);
        if (game == games.end())
            return;
        WorldSession* session = player->GetSession();
        if (!player->HasEnoughMoney(cabinet.price))
        {
            ChatHandler(session).SendNotification("You don't have enough money to play.");
            return;
        }

        uint32 const account = session->GetAccountId();
        if (CabinetBusy(go->GetGUID(), account))
        {
            ChatHandler(session).SendNotification("Someone is already playing this cabinet.");
            return;
        }
        if (Session* old = Active(account))
            SendStop(session, *old, "replaced");

        std::vector<uint8> sram, state;
        if (QueryResult saved = CharacterDatabase.Query(Acore::StringFormat(
            "SELECT `sram`, `state` FROM `character_arcade_save` WHERE `guid` = {} AND `game` = {}",
            player->GetGUID().GetCounter(), cabinet.game)))
        {
            Field* f = saved->Fetch();
            if (!f[0].IsNull()) sram = f[0].Get<Binary>();
            if (!f[1].IsNull()) state = f[1].Get<Binary>();
        }

        if (cabinet.price)
            player->ModifyMoney(-int32(cabinet.price));

        Session s;
        s.id = ++lastSessionId;
        s.account = account;
        s.game = cabinet.game;
        s.player = player->GetGUID();
        s.cabinet = go->GetGUID();
        s.map = go->GetMapId();
        s.x = go->GetPositionX();
        s.y = go->GetPositionY();
        s.z = go->GetPositionZ();
        sessions[s.id] = std::move(s);
        active[account] = lastSessionId;

        WorldPacket data(SMSG_ESTERIA_ARCADE, 64);
        data << uint8(S_START) << lastSessionId << game->second.core << game->second.rom << game->second.title
             << uint32(sram.size()) << uint32(state.size()) << go->GetGUID().GetRawValue(); // cabinet: its screen shows the game
        session->SendPacket(&data);
        SendBlob(session, lastSessionId, KIND_SRAM, sram);
        SendBlob(session, lastSessionId, KIND_STATE, state);
        LOG_INFO("module.arcade", "{} started {} (session {}, paid {}, sram {} B, state {} B)", player->GetName(),
            game->second.title, lastSessionId, cabinet.price, sram.size(), state.size());
    }

    // Client -> server. Returns true when the packet was ours (consumed).
    bool Handle(WorldSession* session, WorldPacket const& packet)
    {
        WorldPacket p(packet);
        try
        {
            uint8 sub;
            uint32 id;
            p >> sub >> id;
            auto it = sessions.find(id);
            if (it == sessions.end() || it->second.account != session->GetAccountId())
                return true;
            Session& s = it->second;
            if (sub == C_QUIT)
            {
                if (!s.stopping)
                {
                    active.erase(s.account);
                    SendViewEnd(s);
                }
                sessions.erase(it);
                return true;
            }
            if (sub == C_VIEW)
            {
                // u32 frame, u8 flags, u32 total, u32 offset, bytes: relayed as is, with the cabinet in front
                Player* player = session->GetPlayer();
                size_t const n = p.size() - p.rpos();
                if (s.stopping || !player || !player->IsInWorld() || n < 13 || n > 9000)
                    return true;
                uint32 const second = getMSTime() / 1000;
                if (second != s.viewSecond)
                {
                    s.viewSecond = second;
                    s.viewBytes = 0;
                }
                if ((s.viewBytes += uint32(n)) > VIEW_BYTES_PER_SECOND)
                    return true;
                WorldPacket data(SMSG_ESTERIA_ARCADE, 13 + n);
                data << uint8(S_VIEW) << s.id << s.cabinet.GetRawValue();
                data.append(p.contents() + p.rpos(), n);
                player->SendMessageToSetInRange(&data, VIEW_RANGE, false);
                return true;
            }
            if (sub != C_DATA)
                return true;
            uint8 kind;
            uint32 total, offset;
            p >> kind >> total >> offset;
            size_t const n = p.size() - p.rpos();
            if (kind > KIND_STATE || !total || total > MAX_BLOB || offset > total || n > total - offset)
                return true;
            Upload& up = s.up[kind];
            if (up.data.size() != total || offset == 0) // a new upload (battery RAM is resent while it changes)
            {
                up.data.assign(total, 0);
                up.got = 0;
            }
            std::memcpy(up.data.data() + offset, p.contents() + p.rpos(), n);
            up.got += uint32(n);
            if (up.got >= total)
            {
                Store(s, kind, up.data);
                up = Upload();
            }
        }
        catch (ByteBufferException const&)
        {
        }
        return true;
    }

    class go_esteria_arcade : public GameObjectScript
    {
    public:
        go_esteria_arcade() : GameObjectScript("go_esteria_arcade") { }

        bool OnGossipHello(Player* player, GameObject* go) override
        {
            auto cabinet = cabinets.find(go->GetEntry());
            if (cabinet == cabinets.end() || !games.contains(cabinet->second.game))
                return false; // plain DB gossip
            ClearGossipMenuFor(player);
            std::string const& title = games[cabinet->second.game].title;
            std::string const price = cabinet->second.price
                ? Acore::StringFormat("Insert a coin ({}) and play {}.", GoldText(cabinet->second.price), title)
                : Acore::StringFormat("Play {}.", title);
            AddGossipItemFor(player, GOSSIP_ICON_MONEY_BAG, price, GOSSIP_SENDER_MAIN, ACTION_PLAY);
            if (Active(player->GetSession()->GetAccountId()))
                AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Stop playing.", GOSSIP_SENDER_MAIN, ACTION_STOP);
            SendGossipMenuFor(player, TEXT_ID, go->GetGUID());
            return true;
        }

        bool OnGossipSelect(Player* player, GameObject* go, uint32 /*sender*/, uint32 action) override
        {
            CloseGossipMenuFor(player);
            auto cabinet = cabinets.find(go->GetEntry());
            if (action == ACTION_PLAY && cabinet != cabinets.end() && player->IsWithinDistInMap(go, REACH))
                Start(player, go, cabinet->second);
            else if (action == ACTION_STOP)
                if (Session* running = Active(player->GetSession()->GetAccountId()))
                    SendStop(player->GetSession(), *running, "quit");
            return true;
        }

    private:
        static std::string GoldText(uint32 copper)
        {
            std::string out;
            if (copper >= 10000) out += std::to_string(copper / 10000) + "g ";
            if (copper % 10000 >= 100) out += std::to_string(copper % 10000 / 100) + "s ";
            if (copper % 100) out += std::to_string(copper % 100) + "c ";
            if (!out.empty()) out.pop_back();
            return out;
        }
    };

    class arcade_packets : public ServerScript
    {
    public:
        arcade_packets() : ServerScript("esteria_arcade_packets", {SERVERHOOK_CAN_PACKET_RECEIVE}) { }

        bool CanPacketReceive(WorldSession* session, WorldPacket const& packet) override
        {
            if (packet.GetOpcode() != CMSG_ESTERIA_ARCADE)
                return true;
            Handle(session, packet);
            return false;
        }
    };

    class arcade_world : public WorldScript
    {
    public:
        arcade_world() : WorldScript("esteria_arcade_world", {WORLDHOOK_ON_STARTUP, WORLDHOOK_ON_UPDATE}) { }

        void OnStartup() override
        {
            games.clear();
            cabinets.clear();
            if (QueryResult r = WorldDatabase.Query("SELECT `id`, `title`, `core`, `rom` FROM `esteria_arcade_game`"))
                do
                {
                    Field* f = r->Fetch();
                    games[f[0].Get<uint32>()] = {f[1].Get<std::string>(), f[2].Get<std::string>(), f[3].Get<std::string>()};
                } while (r->NextRow());
            if (QueryResult r = WorldDatabase.Query("SELECT `entry`, `game`, `price` FROM `esteria_arcade_cabinet`"))
                do
                {
                    Field* f = r->Fetch();
                    cabinets[f[0].Get<uint32>()] = {f[1].Get<uint32>(), f[2].Get<uint32>()};
                } while (r->NextRow());
            LOG_INFO("server.loading", "Esteria arcade: {} games, {} cabinets.", games.size(), cabinets.size());
        }

        void OnUpdate(uint32 diff) override
        {
            if ((timer += diff) < 1000)
                return;
            timer = 0;
            uint32 const now = getMSTime();
            for (auto it = sessions.begin(); it != sessions.end();)
            {
                Session& s = it->second;
                if (s.stopping)
                {
                    it = getMSTimeDiff(s.stoppedAt, now) > GRACE_MS ? sessions.erase(it) : std::next(it);
                    continue;
                }
                Player* player = ObjectAccessor::FindConnectedPlayer(s.player);
                if (!player || !player->IsInWorld() || player->GetMapId() != s.map
                    || player->GetDistance(s.x, s.y, s.z) > REACH)
                    SendStop(player ? player->GetSession() : nullptr, s, player ? "walked away" : "logged out");
                ++it;
            }
        }

    private:
        uint32 timer = 0;
    };
}

void AddSC_esteria_arcade()
{
    new go_esteria_arcade();
    new arcade_packets();
    new arcade_world();
}
