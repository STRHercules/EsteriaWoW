/*
 * Esteria arcade cabinets. A cabinet is a gameobject (type 2, ScriptName go_esteria_arcade) whose entry has a row in
 * esteria_arcade_cabinet naming the game and the price. Paying starts a session: the server sends the game and the
 * character's saved battery RAM + resume state (character_arcade_save) to the client's Arcade extension, which runs
 * the libretro core. Battery RAM comes back every 30 s while it changes; on quit the client sends both and QUIT.
 * Walking away (or a teleport, or logging out) ends the session: STOP goes to the client, which uploads and quits;
 * uploads are accepted for a grace period after that.
 * Spectators: the player's client streams a small picture of the cabinet screen (VIEW); the server relays it to the
 * players around (same packet, with the cabinet guid) and sends VIEW_END when the game stops. One player per cabinet.
 * House cabinets: every cabinet is also housing decor (housing_decor_catalog -> the same gameobject entry). Placed in a
 * house, the owning account plays free; guests pay the house's guest price, which collects in esteria_arcade_house
 * until the owner takes it from any of their cabinets.
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

#include <mutex>
#include <unordered_map>

// mod-esteria-housing: the account owning the house a placed decor object belongs to, 0 when it is not placed decor.
uint32 EsteriaHousingDecorOwner(GameObject const* go);
// mod-esteria-housing: placement id of a placed decor object (0 if none), the display hook it spawns with, a respawn.
uint64 EsteriaHousingPlacedId(GameObject const* go);
extern uint32 (*EsteriaHousingDecorDisplay)(uint64 placed);
bool EsteriaHousingRespawnDecor(GameObject* go);

namespace
{
    enum : uint8 { S_START = 1, S_DATA = 2, S_STOP = 3, S_VIEW = 4, S_VIEW_END = 5, S_NET_ADDR = 6, S_NET = 7,
                   C_DATA = 1, C_QUIT = 2, C_VIEW = 3, C_NET_JOIN = 4, C_NET = 5 };
    enum : uint8 { KIND_SRAM = 0, KIND_STATE = 1 };
    constexpr uint32 CHUNK = 8000;
    constexpr uint32 MAX_BLOB = 16u << 20;
    constexpr float REACH = 8.0f;          // yards from the cabinet before the game stops
    constexpr uint32 GRACE_MS = 60000;     // how long a stopped session still accepts its final uploads
    constexpr uint32 TEXT_ID = 3610001;    // "The cabinet hums..."
    constexpr float VIEW_RANGE = 60.0f;    // spectators within this many yards of the player see the stream
    constexpr uint32 VIEW_BYTES_PER_SECOND = 96 * 1024; // relayed per session; more is dropped (the client resyncs)
    // The arcade network: a virtual LAN between the cabinets playing the same game (StarCraft's LAN games). The
    // server gives each joined session an address (10.77.x.y) and relays datagrams, stamped with the sender's address.
    constexpr uint32 NET_BASE = 0x0A4D0000;              // 10.77.0.0
    constexpr uint32 NET_BROADCAST = 0xFFFFFFFF;
    constexpr uint32 NET_MAX = 2048;                     // one datagram (the client's kNetMax)
    constexpr uint32 NET_BYTES_PER_SECOND = 64 * 1024;   // per session; StarCraft needs about 1 KiB/s
    constexpr uint32 NET_PACKETS_PER_SECOND = 400;
    enum Action : uint32 { ACTION_PLAY = 1, ACTION_STOP = 2, ACTION_PRICE = 3, ACTION_COLLECT = 4, ACTION_LOOKS = 5,
                           ACTION_LOOK = 100 }; // ACTION_LOOK + skin id

    struct Game { std::string title, core, rom; };
    struct Cabinet { uint32 game = 0; uint32 price = 0; };

    std::unordered_map<uint32, Game> games;
    std::unordered_map<uint32, Cabinet> cabinets; // by gameobject entry

    // Cabinet skins (esteria_arcade_skin): another model for a cabinet placed in a house. Skin 0 is the cabinet's own
    // Lionheart look; the others are unlocked per account with gold (character_arcade_skin) and chosen per placement.
    struct Skin { uint32 id = 0, display = 0, price = 0; std::string name; };
    std::vector<Skin> skins;                            // by id, loaded at startup
    std::mutex skinLock;                                // placedSkin is read from map threads as decor spawns
    std::unordered_map<uint64, uint32> placedSkin;      // housing placement -> skin id

    Skin const* SkinById(uint32 id)
    {
        for (Skin const& k : skins)
            if (k.id == id)
                return &k;
        return nullptr;
    }

    uint32 SkinDisplay(uint64 placed)
    {
        std::lock_guard<std::mutex> guard(skinLock);
        auto it = placedSkin.find(placed);
        Skin const* skin = it == placedSkin.end() ? nullptr : SkinById(it->second);
        return skin ? skin->display : 0;
    }

    bool Unlocked(uint32 account, uint32 skin)
    {
        return CharacterDatabase.Query(Acore::StringFormat(
            "SELECT 1 FROM `character_arcade_skin` WHERE `account` = {} AND `skin` = {}", account, skin)) != nullptr;
    }

    constexpr uint32 HOUSE_PRICE = 5000;           // a house's guest price until its owner sets one
    constexpr uint32 HOUSE_PRICE_MAX = 10000000;   // 1000 gold

    std::string GoldText(uint64 copper)
    {
        if (!copper)
            return "free";
        std::string out;
        if (copper >= 10000) out += std::to_string(copper / 10000) + "g ";
        if (copper % 10000 >= 100) out += std::to_string(copper % 10000 / 100) + "s ";
        if (copper % 100) out += std::to_string(copper % 100) + "c ";
        out.pop_back();
        return out;
    }

    struct HouseArcade { uint32 price = HOUSE_PRICE; uint64 earnings = 0; };

    HouseArcade HouseOf(uint32 owner)
    {
        HouseArcade h;
        if (QueryResult r = CharacterDatabase.Query(Acore::StringFormat(
            "SELECT `guest_price`, `earnings` FROM `esteria_arcade_house` WHERE `account` = {}", owner)))
        {
            h.price = r->Fetch()[0].Get<uint32>();
            h.earnings = r->Fetch()[1].Get<uint64>();
        }
        return h;
    }

    // What this player pays at this cabinet: the house's guest price in a house (free for its owner), else the
    // cabinet's own price.
    uint32 PriceFor(Player* player, GameObject* go, Cabinet const& cabinet, uint32& owner)
    {
        owner = EsteriaHousingDecorOwner(go);
        if (!owner)
            return cabinet.price;
        return owner == player->GetSession()->GetAccountId() ? 0 : HouseOf(owner).price;
    }

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
        uint32 netAddr = 0;                              // 0 until C_NET_JOIN
        uint32 netSecond = 0, netBytes = 0, netPackets = 0;
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
        uint32 owner = 0;
        uint32 const price = PriceFor(player, go, cabinet, owner);
        if (!player->HasEnoughMoney(price))
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

        if (price)
        {
            player->ModifyMoney(-int32(price));
            if (owner)  // a guest at a house cabinet: the coin goes to the house
                CharacterDatabase.Execute(Acore::StringFormat(
                    "INSERT INTO `esteria_arcade_house` (`account`, `guest_price`, `earnings`) VALUES ({0}, {1}, {2}) "
                    "ON DUPLICATE KEY UPDATE `earnings` = `earnings` + {2}", owner, HOUSE_PRICE, price));
        }

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
            game->second.title, lastSessionId, price, sram.size(), state.size());
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
            if (sub == C_NET_JOIN)
            {
                if (s.stopping || s.netAddr)
                    return true;
                // the lowest free address among this game's cabinets; .0 and .255 are never handed out (the client
                // treats any x.y.z.255 as a broadcast)
                for (uint32 i = 1; i < 0xFFFF && !s.netAddr; ++i)
                {
                    if ((i & 0xFF) == 0 || (i & 0xFF) == 0xFF)
                        continue;
                    bool taken = false;
                    for (auto const& [oid, o] : sessions)
                        taken = taken || (!o.stopping && o.game == s.game && o.netAddr == (NET_BASE | i));
                    if (!taken)
                        s.netAddr = NET_BASE | i;
                }
                WorldPacket data(SMSG_ESTERIA_ARCADE, 9);
                data << uint8(S_NET_ADDR) << s.id << s.netAddr;
                session->SendPacket(&data);
                return true;
            }
            if (sub == C_NET)
            {
                // u32 to, u16 srcPort, u16 dstPort, bytes -> each cabinet of the same game it is for, from s.netAddr
                uint32 to;
                uint16 srcPort, dstPort;
                p >> to >> srcPort >> dstPort;
                size_t const n = p.size() - p.rpos();
                if (s.stopping || !s.netAddr || n > NET_MAX)
                    return true;
                uint32 const second = getMSTime() / 1000;
                if (second != s.netSecond)
                {
                    s.netSecond = second;
                    s.netBytes = s.netPackets = 0;
                }
                if ((s.netBytes += uint32(n)) > NET_BYTES_PER_SECOND || ++s.netPackets > NET_PACKETS_PER_SECOND)
                    return true;  // dropped, as a congested LAN would; the game resends
                for (auto const& [oid, o] : sessions)
                {
                    if (oid == s.id || o.stopping || o.game != s.game || !o.netAddr || (to != NET_BROADCAST && to != o.netAddr))
                        continue;
                    Player* peer = ObjectAccessor::FindConnectedPlayer(o.player);
                    if (!peer)
                        continue;
                    WorldPacket data(SMSG_ESTERIA_ARCADE, 13 + n);
                    data << uint8(S_NET) << o.id << s.netAddr << srcPort << dstPort;
                    data.append(p.contents() + p.rpos(), n);
                    peer->GetSession()->SendPacket(&data);
                }
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
            uint32 owner = 0;
            uint32 const price = PriceFor(player, go, cabinet->second, owner);
            bool const mine = owner && owner == player->GetSession()->GetAccountId();
            std::string const play = mine ? Acore::StringFormat("Play {} (your cabinet: free).", title)
                : price ? Acore::StringFormat("Insert a coin ({}) and play {}.", GoldText(price), title)
                : Acore::StringFormat("Play {}.", title);
            AddGossipItemFor(player, GOSSIP_ICON_MONEY_BAG, play, GOSSIP_SENDER_MAIN, ACTION_PLAY);
            if (Active(player->GetSession()->GetAccountId()))
                AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Stop playing.", GOSSIP_SENDER_MAIN, ACTION_STOP);
            if (mine)
            {
                HouseArcade const house = HouseOf(owner);
                AddGossipItemFor(player, GOSSIP_ICON_INTERACT_1,
                    Acore::StringFormat("Set what guests pay at your cabinets (now {}).", GoldText(house.price)),
                    GOSSIP_SENDER_MAIN, ACTION_PRICE, "Gold per game for guests (0 for free, up to 1000):", 0, true);
                if (house.earnings)
                    AddGossipItemFor(player, GOSSIP_ICON_MONEY_BAG,
                        Acore::StringFormat("Collect your cabinets' earnings ({}).", GoldText(house.earnings)),
                        GOSSIP_SENDER_MAIN, ACTION_COLLECT);
                if (!skins.empty())
                    AddGossipItemFor(player, GOSSIP_ICON_TABARD, "Change this cabinet's look.", GOSSIP_SENDER_MAIN, ACTION_LOOKS);
            }
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
            {
                if (Session* running = Active(player->GetSession()->GetAccountId()))
                    SendStop(player->GetSession(), *running, "quit");
            }
            else if (action == ACTION_COLLECT)
                Collect(player, go);
            else if (action == ACTION_LOOKS)
                Looks(player, go);
            else if (action >= ACTION_LOOK)
                ChooseLook(player, go, action - ACTION_LOOK);
            return true;
        }

        bool OnGossipSelectCode(Player* player, GameObject* go, uint32 /*sender*/, uint32 action, char const* code) override
        {
            CloseGossipMenuFor(player);
            uint32 const owner = EsteriaHousingDecorOwner(go);
            if (action != ACTION_PRICE || !owner || owner != player->GetSession()->GetAccountId() || !code)
                return true;
            char* end = nullptr;
            double const gold = std::strtod(code, &end);
            if (end == code || gold < 0 || gold * 10000 > HOUSE_PRICE_MAX)
            {
                ChatHandler(player->GetSession()).SendNotification("Enter a number of gold from 0 to 1000.");
                return true;
            }
            uint32 const copper = uint32(gold * 10000 + 0.5);
            CharacterDatabase.Execute(Acore::StringFormat(
                "INSERT INTO `esteria_arcade_house` (`account`, `guest_price`, `earnings`) VALUES ({0}, {1}, 0) "
                "ON DUPLICATE KEY UPDATE `guest_price` = {1}", owner, copper));
            ChatHandler(player->GetSession()).PSendSysMessage("Guests now pay {} per game at your arcade cabinets.", GoldText(copper));
            return true;
        }

    private:
        static bool Mine(Player* player, GameObject* go)
        {
            uint32 const owner = EsteriaHousingDecorOwner(go);
            return owner && owner == player->GetSession()->GetAccountId() && EsteriaHousingPlacedId(go);
        }

        static void Looks(Player* player, GameObject* go)
        {
            if (!Mine(player, go))
                return;
            uint32 const account = player->GetSession()->GetAccountId();
            uint32 current = 0;
            {
                std::lock_guard<std::mutex> guard(skinLock);
                if (auto it = placedSkin.find(EsteriaHousingPlacedId(go)); it != placedSkin.end())
                    current = it->second;
            }
            ClearGossipMenuFor(player);
            AddGossipItemFor(player, GOSSIP_ICON_TABARD, current ? "Lionheart (the original look)."
                : "Lionheart (the original look) - in use.", GOSSIP_SENDER_MAIN, ACTION_LOOK);
            for (Skin const& k : skins)
            {
                if (k.id == current)
                    AddGossipItemFor(player, GOSSIP_ICON_TABARD, k.name + " - in use.", GOSSIP_SENDER_MAIN, ACTION_LOOK + k.id);
                else if (!k.price || Unlocked(account, k.id))
                    AddGossipItemFor(player, GOSSIP_ICON_TABARD, k.name + ".", GOSSIP_SENDER_MAIN, ACTION_LOOK + k.id);
                else
                    AddGossipItemFor(player, GOSSIP_ICON_MONEY_BAG,
                        Acore::StringFormat("Unlock {} ({}).", k.name, GoldText(k.price)), GOSSIP_SENDER_MAIN,
                        ACTION_LOOK + k.id, Acore::StringFormat("Unlock the {} look for all your arcade cabinets?", k.name),
                        k.price, false);
            }
            SendGossipMenuFor(player, TEXT_ID, go->GetGUID());
        }

        static void ChooseLook(Player* player, GameObject* go, uint32 id)
        {
            Skin const* skin = SkinById(id);
            if (!Mine(player, go) || (id && !skin))
                return;
            for (auto const& [sid, s] : sessions)
                if (!s.stopping && s.cabinet == go->GetGUID())
                    return ChatHandler(player->GetSession()).SendNotification("Someone is playing this cabinet.");
            uint32 const account = player->GetSession()->GetAccountId();
            if (skin && skin->price && !Unlocked(account, id))
            {
                if (!player->HasEnoughMoney(skin->price))
                    return ChatHandler(player->GetSession()).SendNotification("You don't have enough gold.");
                CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
                trans->Append(Acore::StringFormat(
                    "INSERT IGNORE INTO `character_arcade_skin` (`account`, `skin`) VALUES ({}, {})", account, id));
                player->ModifyMoney(-int32(skin->price));
                player->SaveGoldToDB(trans);
                CharacterDatabase.CommitTransaction(trans);
                ChatHandler(player->GetSession()).PSendSysMessage("You unlock the {} cabinet look.", skin->name);
            }
            uint64 const placed = EsteriaHousingPlacedId(go);
            {
                std::lock_guard<std::mutex> guard(skinLock);
                if (id)
                    placedSkin[placed] = id;
                else
                    placedSkin.erase(placed);
            }
            CharacterDatabase.Execute(id
                ? Acore::StringFormat("REPLACE INTO `esteria_arcade_placed_skin` (`placed_id`, `skin`) VALUES ({}, {})", placed, id)
                : Acore::StringFormat("DELETE FROM `esteria_arcade_placed_skin` WHERE `placed_id` = {}", placed));
            EsteriaHousingRespawnDecor(go); // the client only builds a gameobject's model when it first sees it
        }

        static void Collect(Player* player, GameObject* go)
        {
            uint32 const owner = EsteriaHousingDecorOwner(go);
            if (!owner || owner != player->GetSession()->GetAccountId())
                return;
            uint64 const earnings = HouseOf(owner).earnings;
            if (!earnings)
                return;
            if (uint64(player->GetMoney()) + earnings > MAX_MONEY_AMOUNT)
            {
                ChatHandler(player->GetSession()).SendNotification("You can't carry that much gold.");
                return;
            }
            // Take exactly what was read: coins guests add meanwhile stay for next time.
            CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
            trans->Append(Acore::StringFormat(
                "UPDATE `esteria_arcade_house` SET `earnings` = `earnings` - {} WHERE `account` = {}", earnings, owner));
            player->ModifyMoney(int32(earnings));
            player->SaveGoldToDB(trans);
            CharacterDatabase.CommitTransaction(trans);
            ChatHandler(player->GetSession()).PSendSysMessage("You collect {} from your arcade cabinets.", GoldText(earnings));
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
            skins.clear();
            if (QueryResult r = WorldDatabase.Query("SELECT `id`, `display_id`, `price`, `name` FROM `esteria_arcade_skin` ORDER BY `id`"))
                do
                {
                    Field* f = r->Fetch();
                    skins.push_back({f[0].Get<uint32>(), f[1].Get<uint32>(), f[2].Get<uint32>(), f[3].Get<std::string>()});
                } while (r->NextRow());
            {
                std::lock_guard<std::mutex> guard(skinLock);
                placedSkin.clear();
                if (QueryResult r = CharacterDatabase.Query("SELECT `placed_id`, `skin` FROM `esteria_arcade_placed_skin`"))
                    do
                        placedSkin[r->Fetch()[0].Get<uint64>()] = r->Fetch()[1].Get<uint32>();
                    while (r->NextRow());
            }
            EsteriaHousingDecorDisplay = SkinDisplay;
            LOG_INFO("server.loading", "Esteria arcade: {} games, {} cabinets, {} cabinet looks.", games.size(),
                cabinets.size(), skins.size());
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
