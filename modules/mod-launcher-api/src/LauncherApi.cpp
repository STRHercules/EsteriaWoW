// mod-launcher-api: HTTP API for the Esteria launcher (account creation, character management, presence).
// HTTP threads only parse and authenticate; every game or database action is queued to the world thread.
#include "AccountMgr.h"
#include "ArenaTeamMgr.h"
#include "CalendarMgr.h"
#include "CharacterCache.h"
#include "Config.h"
#include "DBCStores.h"
#include "DatabaseEnv.h"
#include "GuildMgr.h"
#include "Log.h"
#include "ObjectAccessor.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "SpellInfo.h"
#include "SpellMgr.h"
#include "StringFormat.h"
#include "Util.h"
#include "World.h"
#include "WorldSessionMgr.h"
#include "../vendor/json.hpp"
#include <boost/asio.hpp>
#include <boost/asio/ssl.hpp>
#include <boost/beast.hpp>
#include <boost/beast/ssl.hpp>
#include <algorithm>
#include <atomic>
#include <chrono>
#include <deque>
#include <functional>
#include <future>
#include <memory>
#include <mutex>
#include <random>
#include <cmath>
#include <ctime>
#include <regex>
#include <thread>
#include <vector>
#include <unordered_map>

namespace
{
    namespace asio = boost::asio;
    namespace beast = boost::beast;
    namespace http = beast::http;
    using Json = nlohmann::json;
    using Clock = std::chrono::steady_clock;
    using Tcp = asio::ip::tcp;

    constexpr std::size_t MaxBody = 16 * 1024;
    constexpr uint32 MaxConnections = 32;
    constexpr uint32 MaxQueued = 64;

    struct Settings
    {
        bool enabled = false;
        std::string bind = "127.0.0.1";
        uint16 port = 8095;
        std::string cert;
        std::string key;
        bool registration = true;
        uint32 tokenHours = 168;
        bool charDelete = true;
        bool rename = true;
        bool customize = true;
        bool faction = true;
        bool race = true;
        bool armoryBots = false;
    };

    struct Reply
    {
        int status = 200;
        Json body = Json::object();
    };

    Reply Fail(int status, std::string const& code, std::string const& message)
    {
        return {status, {{"error", code}, {"message", message}}};
    }

    struct Presence
    {
        std::string name;
        uint8 level = 0;
        uint8 raceId = 0;
        uint8 classId = 0;
        std::string race;
        std::string cls;
        std::string zone;
        uint32 mapId = 0;
    };

    struct Token
    {
        uint32 account = 0;
        Clock::time_point expires;
    };

    struct Task
    {
        std::function<Reply()> run;
        std::promise<Reply> done;
    };

    std::string Hex(std::size_t bytes)
    {
        static std::random_device device;
        std::string out;
        char const* digits = "0123456789abcdef";
        for (std::size_t i = 0; i < bytes; ++i)
        {
            uint32 value = device() & 0xFF;
            out += digits[value >> 4];
            out += digits[value & 15];
        }
        return out;
    }

    char const* LocaleName(char const* const* names)
    {
        char const* value = names[sWorld->GetDefaultDbcLocale()];
        return value && *value ? value : names[0] ? names[0] : "";
    }

    class Api
    {
    public:
        static Api& Instance()
        {
            static Api api;
            return api;
        }

        void Configure()
        {
            Settings next;
            next.enabled = sConfigMgr->GetOption<bool>("LauncherApi.Enable", false);
            next.bind = sConfigMgr->GetOption<std::string>("LauncherApi.Bind", "127.0.0.1");
            next.port = sConfigMgr->GetOption<uint16>("LauncherApi.Port", 8095);
            next.cert = sConfigMgr->GetOption<std::string>("LauncherApi.Tls.Cert", "");
            next.key = sConfigMgr->GetOption<std::string>("LauncherApi.Tls.Key", "");
            next.registration = sConfigMgr->GetOption<bool>("LauncherApi.AllowRegistration", true);
            next.tokenHours = sConfigMgr->GetOption<uint32>("LauncherApi.TokenHours", 168);
            next.charDelete = sConfigMgr->GetOption<bool>("LauncherApi.Character.Delete", true);
            next.rename = sConfigMgr->GetOption<bool>("LauncherApi.Service.Rename", true);
            next.customize = sConfigMgr->GetOption<bool>("LauncherApi.Service.Customize", true);
            next.faction = sConfigMgr->GetOption<bool>("LauncherApi.Service.Faction", true);
            next.race = sConfigMgr->GetOption<bool>("LauncherApi.Service.Race", true);
            next.armoryBots = sConfigMgr->GetOption<bool>("LauncherApi.Armory.IncludeBots", false);
            std::lock_guard lock(mutex_);
            settings_ = next; // shortcut: listener address/TLS changes need a restart; the rest applies on reload
        }

        void Start()
        {
            Settings s = Current();
            if (!s.enabled)
                return;
            try
            {
                if (!s.cert.empty())
                {
                    tls_ = std::make_unique<asio::ssl::context>(asio::ssl::context::tls_server);
                    tls_->use_certificate_chain_file(s.cert);
                    tls_->use_private_key_file(s.key, asio::ssl::context::pem);
                }
                acceptor_ = std::make_unique<Tcp::acceptor>(io_, Tcp::endpoint(asio::ip::make_address(s.bind), s.port));
            }
            catch (std::exception const& error)
            {
                LOG_ERROR("module.launcherapi", "Could not start the launcher API: {}", error.what());
                tls_.reset();
                acceptor_.reset();
                return;
            }
            running_ = true;
            listener_ = std::thread([this] { Accept(); });
            LOG_INFO("module.launcherapi", "Launcher API listening on {}:{} ({})", s.bind, s.port, tls_ ? "TLS" : "plain HTTP");
        }

        void Stop()
        {
            running_ = false;
            if (acceptor_)
            {
                boost::system::error_code ignored;
                acceptor_->close(ignored);
            }
            if (listener_.joinable())
                listener_.join();
            for (int i = 0; i < 60 && active_ > 0; ++i)
                std::this_thread::sleep_for(std::chrono::milliseconds(50));
            std::deque<Task> pending;
            {
                std::lock_guard lock(mutex_);
                pending.swap(tasks_);
            }
            for (auto& task : pending)
                task.done.set_value(Fail(503, "shutdown", "Server is shutting down."));
        }

        // World thread: run queued API work.
        void Pump()
        {
            for (int budget = 8; budget > 0; --budget)
            {
                Task task;
                {
                    std::lock_guard lock(mutex_);
                    if (tasks_.empty())
                        return;
                    task = std::move(tasks_.front());
                    tasks_.pop_front();
                }
                try
                {
                    task.done.set_value(task.run());
                }
                catch (std::exception const& error)
                {
                    LOG_ERROR("module.launcherapi", "Launcher API task failed: {}", error.what());
                    task.done.set_value(Fail(500, "internal", "Internal error."));
                }
            }
        }

        void Track(Player* player)
        {
            Presence p;
            p.name = player->GetName();
            p.level = player->GetLevel();
            p.raceId = player->getRace();
            p.classId = player->getClass();
            p.mapId = player->GetMapId();
            if (ChrRacesEntry const* race = sChrRacesStore.LookupEntry(p.raceId))
                p.race = LocaleName(race->name);
            if (ChrClassesEntry const* cls = sChrClassesStore.LookupEntry(p.classId))
                p.cls = LocaleName(cls->name);
            if (AreaTableEntry const* area = sAreaTableStore.LookupEntry(player->GetZoneId()))
                p.zone = LocaleName(area->area_name);
            std::lock_guard lock(mutex_);
            online_[player->GetSession()->GetAccountId()] = std::move(p);
        }

        void Untrack(Player* player)
        {
            std::lock_guard lock(mutex_);
            online_.erase(player->GetSession()->GetAccountId());
        }

    private:
        Settings Current()
        {
            std::lock_guard lock(mutex_);
            return settings_;
        }

        void Accept()
        {
            while (running_)
            {
                Tcp::socket socket(io_);
                boost::system::error_code error;
                acceptor_->accept(socket, error);
                if (error)
                {
                    if (!running_)
                        return;
                    std::this_thread::sleep_for(std::chrono::milliseconds(100));
                    continue;
                }
                if (active_ >= MaxConnections)
                    continue; // socket closes
                ++active_;
                std::thread([this, s = std::move(socket)]() mutable
                {
                    try
                    {
                        Connection(std::move(s));
                    }
                    catch (std::exception const&)
                    {
                    }
                    --active_;
                }).detach();
            }
        }

        template <class Stream>
        void Exchange(Stream& stream, std::string const& ip)
        {
            beast::flat_buffer buffer;
            http::request_parser<http::string_body> parser;
            parser.body_limit(MaxBody);
            http::read(stream, buffer, parser);
            http::request<http::string_body> request = parser.release();
            Reply reply = Route(request, ip);
            http::response<http::string_body> response{static_cast<http::status>(reply.status), request.version()};
            response.set(http::field::content_type, "application/json");
            response.set(http::field::access_control_allow_origin, "*");
            response.set(http::field::access_control_allow_headers, "authorization, content-type");
            response.set(http::field::access_control_allow_methods, "GET, POST, OPTIONS");
            response.keep_alive(false);
            response.body() = reply.status == 204 ? std::string() : reply.body.dump(-1, ' ', false, Json::error_handler_t::replace);
            response.prepare_payload();
            http::write(stream, response);
        }

        void Connection(Tcp::socket socket)
        {
            boost::system::error_code ignored;
            std::string ip = socket.remote_endpoint(ignored).address().to_string();
            beast::tcp_stream plain(std::move(socket));
            plain.expires_after(std::chrono::seconds(10));
            if (tls_)
            {
                beast::ssl_stream<beast::tcp_stream> secure(std::move(plain), *tls_);
                secure.handshake(asio::ssl::stream_base::server);
                Exchange(secure, ip);
                secure.shutdown(ignored);
            }
            else
            {
                Exchange(plain, ip);
                plain.socket().shutdown(Tcp::socket::shutdown_send, ignored);
            }
        }

        // ---- routing -------------------------------------------------------------------------------------------

        Reply Route(http::request<http::string_body> const& request, std::string const& ip)
        {
            if (request.method() == http::verb::options)
                return {204, Json::object()};
            std::string target(request.target());
            target = target.substr(0, target.find('?'));
            static std::string const prefix = "/launcher/v1/";
            if (target.rfind(prefix, 0) != 0)
                return Fail(404, "not_found", "Unknown route.");
            std::string route = target.substr(prefix.size());
            while (!route.empty() && route.back() == '/')
                route.pop_back();
            bool get = request.method() == http::verb::get;
            bool post = request.method() == http::verb::post;

            Json body = Json::object();
            if (post && !request.body().empty())
            {
                body = Json::parse(request.body(), nullptr, false);
                if (!body.is_object())
                    return Fail(400, "bad_request", "Body must be a JSON object.");
            }

            Settings s = Current();
            if (get && route == "info")
                return {200, {{"name", "launcher-api"}, {"registration", s.registration},
                    {"services", {{"rename", s.rename}, {"customize", s.customize}, {"faction", s.faction}, {"race", s.race}}},
                    {"characterDelete", s.charDelete}}};
            if (get && (route == "armory" || route == "database"))
                return Lookup(route, std::string(request.target()), ip, s);
            if (post && route == "register")
                return Register(body, ip, s);
            if (post && route == "login")
                return Login(body, ip, s);

            std::string header(request[http::field::authorization]);
            uint32 account = Authenticate(header.rfind("Bearer ", 0) == 0 ? header.substr(7) : std::string());
            if (!account)
                return Fail(401, "unauthorized", "Sign in again.");

            if (post && route == "logout")
            {
                std::lock_guard lock(mutex_);
                tokens_.erase(header.substr(7));
                return {200, {{"ok", true}}};
            }
            if (get && route == "presence")
                return PresenceOf(account);

            // Everything below touches the game or databases, so it runs on the world thread.
            std::function<Reply()> work;
            if (get && route == "me")
                work = [account] { return Me(account); };
            else if (post && route == "password")
                work = [account, body] { return ChangePassword(account, body); };
            else if (post && route == "email")
                work = [account, body] { return ChangeEmail(account, body); };
            else if (get && route == "characters")
                work = [account] { return Characters(account); };
            else if (post && route.rfind("characters/", 0) == 0)
                work = CharacterAction(account, route.substr(11), body, s);
            if (!work)
                return Fail(404, "not_found", "Unknown route.");
            return OnWorld(std::move(work));
        }

        Reply OnWorld(std::function<Reply()> work)
        {
            Task task{std::move(work), {}};
            std::future<Reply> future = task.done.get_future();
            {
                std::lock_guard lock(mutex_);
                if (!running_ || tasks_.size() >= MaxQueued)
                    return Fail(503, "busy", "Server busy; retry shortly.");
                tasks_.push_back(std::move(task));
            }
            if (future.wait_for(std::chrono::seconds(8)) != std::future_status::ready)
                return Fail(503, "busy", "Server busy; retry shortly.");
            return future.get();
        }

        // ---- sessions and throttling ---------------------------------------------------------------------------

        uint32 Authenticate(std::string const& token)
        {
            std::lock_guard lock(mutex_);
            auto found = tokens_.find(token);
            if (found == tokens_.end())
                return 0;
            if (found->second.expires < Clock::now())
            {
                tokens_.erase(found);
                return 0;
            }
            return found->second.account;
        }

        std::string Issue(uint32 account, uint32 hours)
        {
            std::string token = Hex(32);
            std::lock_guard lock(mutex_);
            auto now = Clock::now();
            for (auto it = tokens_.begin(); it != tokens_.end();)
                it = it->second.expires < now ? tokens_.erase(it) : std::next(it);
            tokens_[token] = {account, now + std::chrono::hours(hours ? hours : 1)};
            return token;
        }

        // Counts a hit against `key` and reports whether the caller is over `max` hits in `seconds`.
        bool Throttled(std::string const& key, std::size_t max, int seconds, bool record)
        {
            std::lock_guard lock(mutex_);
            auto now = Clock::now();
            auto& hits = hits_[key];
            while (!hits.empty() && now - hits.front() > std::chrono::seconds(seconds))
                hits.pop_front();
            bool over = hits.size() >= max;
            if (record && !over)
                hits.push_back(now);
            if (hits.empty())
                hits_.erase(key);
            return over;
        }

        // ---- public lookups: armory and world database ---------------------------------------------------------
        // Read-only and unauthenticated. Answers are cached for a minute and throttled per IP.

        static std::string Lower(std::string text)
        {
            for (char& c : text)
                c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
            return text;
        }

        static bool Has(std::string const& hay, std::string const& lowerNeedle)
        {
            return Lower(hay).find(lowerNeedle) != std::string::npos;
        }

        static std::string UrlDecode(std::string const& text)
        {
            std::string out;
            for (std::size_t i = 0; i < text.size(); ++i)
            {
                if (text[i] == '+')
                    out += ' ';
                else if (text[i] == '%' && i + 2 < text.size() && std::isxdigit(static_cast<unsigned char>(text[i + 1])) &&
                    std::isxdigit(static_cast<unsigned char>(text[i + 2])))
                {
                    out += static_cast<char>(std::stoi(text.substr(i + 1, 2), nullptr, 16));
                    i += 2;
                }
                else
                    out += text[i];
            }
            return out;
        }

        static std::string QueryParam(std::string const& target, std::string const& key)
        {
            std::size_t mark = target.find('?');
            while (mark != std::string::npos)
            {
                std::size_t end = target.find('&', mark + 1);
                std::string pair = target.substr(mark + 1, end == std::string::npos ? std::string::npos : end - mark - 1);
                std::size_t eq = pair.find('=');
                if (eq != std::string::npos && pair.substr(0, eq) == key)
                    return UrlDecode(pair.substr(eq + 1));
                mark = end;
            }
            return {};
        }

        // Keeps letters, digits, spaces and dashes only, so the term is safe inside a LIKE pattern.
        static std::string SearchTerm(std::string const& raw)
        {
            std::string out;
            for (char c : raw)
            {
                unsigned char u = static_cast<unsigned char>(c);
                if (std::isalnum(u) || c == ' ' || c == '-' || u >= 0x80)
                    out += c;
            }
            std::size_t first = out.find_first_not_of(' ');
            out = first == std::string::npos ? std::string() : out.substr(first, out.find_last_not_of(' ') - first + 1);
            return out.substr(0, 40);
        }

        Reply Lookup(std::string const& route, std::string const& target, std::string const& ip, Settings const& s)
        {
            if (Throttled("lookup:" + ip, 120, 60, true))
                return Fail(429, "throttled", "Too many lookups; slow down.");
            std::string q = SearchTerm(QueryParam(target, "q"));
            std::string type = Lower(SearchTerm(QueryParam(target, "type")));
            std::string key = route + '|' + Lower(q) + '|' + type;
            {
                std::lock_guard lock(mutex_);
                auto found = lookups_.find(key);
                if (found != lookups_.end() && found->second.first > Clock::now())
                    return {200, found->second.second};
            }
            bool bots = s.armoryBots;
            Reply reply = OnWorld(route == "armory" ? std::function<Reply()>([q, bots] { return ArmorySearch(q, bots); })
                                                    : std::function<Reply()>([q, type] { return DatabaseSearch(q, type); }));
            if (reply.status == 200)
            {
                std::lock_guard lock(mutex_);
                if (lookups_.size() > 256)
                    lookups_.clear();
                lookups_[key] = {Clock::now() + std::chrono::seconds(60), reply.body};
            }
            return reply;
        }

        static std::string IdList(std::vector<uint32> const& ids)
        {
            std::string out;
            for (uint32 id : ids)
                out += (out.empty() ? "" : ",") + std::to_string(id);
            return out;
        }

        static Reply ArmorySearch(std::string const& q, bool includeBots)
        {
            static char const* const Slots[] = {"Head", "Neck", "Shoulder", "Shirt", "Chest", "Waist", "Legs", "Feet", "Wrist",
                "Hands", "Finger 1", "Finger 2", "Trinket 1", "Trinket 2", "Back", "Main Hand", "Off Hand", "Ranged", "Tabard"};
            std::string lower = Lower(q);
            std::string where = "c.deleteDate IS NULL";
            if (!includeBots)
            {
                std::vector<uint32> bots;
                if (QueryResult result = LoginDatabase.Query("SELECT id FROM account WHERE username LIKE 'RNDBOT%' LIMIT 5000"))
                    do
                        bots.push_back(result->Fetch()[0].Get<uint32>());
                    while (result->NextRow());
                if (!bots.empty())
                    where += " AND c.account NOT IN (" + IdList(bots) + ")";
            }
            if (!q.empty())
            {
                std::string any = "c.name LIKE '%" + q + "%' OR IFNULL(g.name, '') LIKE '%" + q + "%'";
                std::vector<uint32> races, classes, zones;
                for (uint32 i = 0; i < sChrRacesStore.GetNumRows(); ++i)
                    if (ChrRacesEntry const* race = sChrRacesStore.LookupEntry(i))
                        if (Has(LocaleName(race->name), lower))
                            races.push_back(i);
                for (uint32 i = 0; i < sChrClassesStore.GetNumRows(); ++i)
                    if (ChrClassesEntry const* cls = sChrClassesStore.LookupEntry(i))
                        if (Has(LocaleName(cls->name), lower))
                            classes.push_back(i);
                for (uint32 i = 0; i < sAreaTableStore.GetNumRows() && zones.size() < 200; ++i)
                    if (AreaTableEntry const* area = sAreaTableStore.LookupEntry(i))
                        if (Has(LocaleName(area->area_name), lower))
                            zones.push_back(i);
                if (!races.empty())
                    any += " OR c.race IN (" + IdList(races) + ")";
                if (!classes.empty())
                    any += " OR c.class IN (" + IdList(classes) + ")";
                if (!zones.empty())
                    any += " OR c.zone IN (" + IdList(zones) + ")";
                where += " AND (" + any + ")";
            }

            struct Row
            {
                uint32 guid = 0;
                Json json;
                std::vector<std::pair<uint8, Json>> gear;
                uint32 points = 0;
            };
            std::vector<Row> rows;
            std::vector<uint32> guids;
            if (QueryResult result = CharacterDatabase.Query(Acore::StringFormat(
                "SELECT c.guid, c.name, c.level, c.race, c.class, IFNULL(g.name, ''), c.zone, c.online, c.logout_time "
                "FROM characters c LEFT JOIN guild_member gm ON gm.guid = c.guid LEFT JOIN guild g ON g.guildid = gm.guildid "
                "WHERE {} ORDER BY c.online DESC, c.level DESC, c.totaltime DESC LIMIT {}", where, q.empty() ? 250 : 100)))
            {
                do
                {
                    Field* f = result->Fetch();
                    ChrRacesEntry const* race = sChrRacesStore.LookupEntry(f[3].Get<uint8>());
                    ChrClassesEntry const* cls = sChrClassesStore.LookupEntry(f[4].Get<uint8>());
                    AreaTableEntry const* area = sAreaTableStore.LookupEntry(f[6].Get<uint32>());
                    Row row;
                    row.guid = f[0].Get<uint32>();
                    row.json = {{"name", f[1].Get<std::string>()}, {"level", f[2].Get<uint8>()},
                        {"race", race ? LocaleName(race->name) : "Unknown"}, {"className", cls ? LocaleName(cls->name) : "Unknown"},
                        {"online", f[7].Get<bool>()}};
                    if (std::string guild = f[5].Get<std::string>(); !guild.empty())
                        row.json["guild"] = guild;
                    if (area)
                        row.json["zone"] = LocaleName(area->area_name);
                    if (time_t seen = static_cast<time_t>(f[8].Get<uint32>()))
                    {
                        char buffer[32];
                        std::tm utc{};
#ifdef _WIN32
                        gmtime_s(&utc, &seen);
#else
                        gmtime_r(&seen, &utc);
#endif
                        std::strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%S.000Z", &utc);
                        row.json["lastSeen"] = buffer;
                    }
                    guids.push_back(row.guid);
                    rows.push_back(std::move(row));
                } while (result->NextRow());
            }

            if (!guids.empty())
            {
                std::unordered_map<uint32, std::size_t> index;
                for (std::size_t i = 0; i < rows.size(); ++i)
                    index[rows[i].guid] = i;
                std::string list = IdList(guids);
                if (QueryResult result = CharacterDatabase.Query(Acore::StringFormat(
                    "SELECT ci.guid, ci.slot, ii.itemEntry FROM character_inventory ci JOIN item_instance ii ON ii.guid = ci.item "
                    "WHERE ci.bag = 0 AND ci.slot < 19 AND ci.guid IN ({})", list)))
                {
                    do
                    {
                        Field* f = result->Fetch();
                        ItemTemplate const* item = sObjectMgr->GetItemTemplate(f[2].Get<uint32>());
                        auto row = index.find(f[0].Get<uint32>());
                        if (!item || row == index.end())
                            continue;
                        uint8 slot = f[1].Get<uint8>();
                        rows[row->second].gear.push_back({slot, {{"slot", Slots[slot]}, {"id", item->ItemId}, {"name", item->Name1},
                            {"quality", item->Quality}, {"itemLevel", item->ItemLevel}}});
                    } while (result->NextRow());
                }
                if (QueryResult result = CharacterDatabase.Query(Acore::StringFormat(
                    "SELECT guid, achievement FROM character_achievement WHERE guid IN ({})", list)))
                {
                    do
                    {
                        Field* f = result->Fetch();
                        auto row = index.find(f[0].Get<uint32>());
                        AchievementEntry const* entry = sAchievementStore.LookupEntry(f[1].Get<uint32>());
                        if (entry && row != index.end())
                            rows[row->second].points += entry->points;
                    } while (result->NextRow());
                }
            }

            Json characters = Json::array();
            for (Row& row : rows)
            {
                std::sort(row.gear.begin(), row.gear.end(), [](auto const& a, auto const& b) { return a.first < b.first; });
                Json equipment = Json::array();
                uint32 total = 0, counted = 0;
                for (auto const& [slot, item] : row.gear)
                {
                    equipment.push_back(item);
                    if (slot != 3 && slot != 18)
                    {
                        total += item["itemLevel"].get<uint32>();
                        ++counted;
                    }
                }
                row.json["itemLevel"] = counted ? static_cast<uint32>(std::lround(double(total) / counted)) : 0;
                row.json["achievementPoints"] = row.points;
                row.json["equipment"] = std::move(equipment);
                characters.push_back(std::move(row.json));
            }
            return {200, {{"schemaVersion", 1}, {"characters", characters}}};
        }

        static Reply DatabaseSearch(std::string const& q, std::string const& type)
        {
            std::string lower = Lower(q);
            uint32 wantedId = !q.empty() && q.size() <= 9 && q.find_first_not_of("0123456789") == std::string::npos ? std::stoul(q) : 0;
            bool specific = !type.empty() && type != "all";
            std::size_t cap = specific ? 200 : 40;
            LocaleConstant locale = sWorld->GetDefaultDbcLocale();

            struct Hit
            {
                int rank;
                std::string name;
                Json json;
            };
            std::vector<Hit> hits;
            auto want = [&](char const* kind) { return !specific || type == kind; };
            // rank 0: exact id, 1: name starts with the term, 2: name contains it
            auto consider = [&](uint32 id, std::string const& name, std::function<Json()> build) {
                int rank = 3;
                if (wantedId && id == wantedId)
                    rank = 0;
                else if (!lower.empty() && !name.empty())
                {
                    std::size_t at = Lower(name).find(lower);
                    rank = at == 0 ? 1 : at != std::string::npos ? 2 : 3;
                }
                if (rank < 3)
                    hits.push_back({rank, name, build()});
            };
            Json entries = Json::array();
            auto take = [&] {
                std::sort(hits.begin(), hits.end(), [](Hit const& a, Hit const& b) {
                    if (a.rank != b.rank)
                        return a.rank < b.rank;
                    return a.name.size() != b.name.size() ? a.name.size() < b.name.size() : a.name < b.name;
                });
                for (std::size_t i = 0; i < hits.size() && i < cap; ++i)
                    entries.push_back(std::move(hits[i].json));
                hits.clear();
            };
            auto text = [](std::string const& value, std::size_t max) { return value.size() > max ? value.substr(0, max) + "..." : value; };

            if (q.empty())
            {
                // No search yet: show the legendary items as a starting point.
                if (!want("item"))
                    return {200, {{"schemaVersion", 1}, {"entries", entries}}};
                std::vector<ItemTemplate const*> legendary;
                for (auto const& [id, item] : *sObjectMgr->GetItemTemplateStore())
                    if (item.Quality == 5)
                        legendary.push_back(&item);
                std::sort(legendary.begin(), legendary.end(), [](auto a, auto b) { return a->ItemLevel > b->ItemLevel; });
                for (std::size_t i = 0; i < legendary.size() && i < 60; ++i)
                    entries.push_back({{"type", "item"}, {"id", legendary[i]->ItemId}, {"name", legendary[i]->Name1},
                        {"subtitle", "Item level " + std::to_string(legendary[i]->ItemLevel)}, {"description", legendary[i]->Description},
                        {"quality", legendary[i]->Quality}, {"level", legendary[i]->ItemLevel}});
                return {200, {{"schemaVersion", 1}, {"entries", entries}}};
            }

            if (want("item"))
            {
                for (auto const& [id, item] : *sObjectMgr->GetItemTemplateStore())
                    consider(id, item.Name1, [&] {
                        return Json{{"type", "item"}, {"id", id}, {"name", item.Name1},
                            {"subtitle", "Item level " + std::to_string(item.ItemLevel)}, {"description", item.Description},
                            {"quality", item.Quality}, {"level", item.ItemLevel}, {"requiredLevel", item.RequiredLevel}};
                    });
                take();
            }
            if (want("quest"))
            {
                for (auto const& [id, quest] : sObjectMgr->GetQuestTemplates())
                    consider(id, quest->GetTitle(), [&] {
                        std::string zone;
                        if (quest->GetZoneOrSort() > 0)
                            if (AreaTableEntry const* area = sAreaTableStore.LookupEntry(quest->GetZoneOrSort()))
                                zone = LocaleName(area->area_name);
                        return Json{{"type", "quest"}, {"id", id}, {"name", quest->GetTitle()}, {"subtitle", zone},
                            {"description", text(quest->GetDetails(), 260)}, {"level", quest->GetQuestLevel()}, {"minLevel", quest->GetMinLevel()}};
                    });
                take();
            }
            if (want("npc"))
            {
                for (auto const& [id, creature] : *sObjectMgr->GetCreatureTemplates())
                    consider(id, creature.Name, [&] {
                        return Json{{"type", "npc"}, {"id", id}, {"name", creature.Name}, {"subtitle", creature.SubName},
                            {"level", creature.maxlevel}, {"minLevel", creature.minlevel}, {"maxLevel", creature.maxlevel}};
                    });
                take();
            }
            if (want("spell"))
            {
                for (uint32 id = 1; id < sSpellMgr->GetSpellInfoStoreSize(); ++id)
                    if (SpellInfo const* spell = sSpellMgr->GetSpellInfo(id))
                    {
                        char const* name = spell->SpellName[locale];
                        if (!name || !*name)
                            continue;
                        consider(id, name, [&] {
                            char const* rank = spell->Rank[locale];
                            return Json{{"type", "spell"}, {"id", id}, {"name", name}, {"subtitle", rank ? rank : ""}};
                        });
                    }
                take();
            }
            if (want("zone"))
            {
                for (uint32 id = 0; id < sAreaTableStore.GetNumRows(); ++id)
                    if (AreaTableEntry const* area = sAreaTableStore.LookupEntry(id))
                        consider(id, LocaleName(area->area_name), [&] {
                            AreaTableEntry const* parent = area->zone ? sAreaTableStore.LookupEntry(area->zone) : nullptr;
                            return Json{{"type", "zone"}, {"id", id}, {"name", LocaleName(area->area_name)},
                                {"subtitle", parent ? LocaleName(parent->area_name) : ""}, {"mapId", area->mapid}};
                        });
                take();
            }
            return {200, {{"schemaVersion", 1}, {"entries", entries}}};
        }

        // ---- handlers ------------------------------------------------------------------------------------------

        Reply Register(Json const& body, std::string const& ip, Settings const& s)
        {
            if (!s.registration)
                return Fail(403, "disabled", "Account creation is disabled on this server.");
            if (Throttled("reg:" + ip, 5, 3600, true))
                return Fail(429, "throttled", "Too many accounts created from this address; try again later.");
            std::string username = body.value("username", "");
            std::string password = body.value("password", "");
            std::string email = body.value("email", "");
            static std::regex const nameRule("^[A-Za-z0-9]{3,17}$");
            static std::regex const emailRule("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$");
            if (!std::regex_match(username, nameRule))
                return Fail(400, "bad_username", "Account name must be 3-17 letters or digits.");
            if (password.size() < 6 || password.size() > MAX_PASS_STR)
                return Fail(400, "bad_password", "Password must be 6-16 characters.");
            if (email.size() > 120 || !std::regex_match(email, emailRule))
                return Fail(400, "bad_email", "Enter a valid email address.");
            return OnWorld([username, password, email]() -> Reply
            {
                switch (sAccountMgr->CreateAccount(username, password, email))
                {
                    case AOR_OK:
                        return {200, {{"ok", true}, {"username", username}}};
                    case AOR_NAME_ALREADY_EXIST:
                        return Fail(409, "name_taken", "That account name is already taken.");
                    default:
                        return Fail(400, "rejected", "The server rejected that account.");
                }
            });
        }

        Reply Login(Json const& body, std::string const& ip, Settings const& s)
        {
            if (Throttled("login:" + ip, 10, 600, false))
                return Fail(429, "throttled", "Too many failed sign-ins; try again in a few minutes.");
            std::string username = body.value("username", "");
            std::string password = body.value("password", "");
            Reply reply = OnWorld([username, password]() -> Reply
            {
                std::string upper = username;
                Utf8ToUpperOnlyLatin(upper);
                uint32 account = AccountMgr::GetId(upper);
                if (!account || !AccountMgr::CheckPassword(account, password))
                    return Fail(401, "bad_credentials", "Wrong account name or password.");
                return {200, {{"account", account}, {"username", upper}}};
            });
            if (reply.status != 200)
            {
                if (reply.status == 401)
                    Throttled("login:" + ip, 10, 600, true);
                return reply;
            }
            uint32 account = reply.body["account"].get<uint32>();
            reply.body.erase("account");
            reply.body["accountId"] = account; // immutable id; the social service binds identity to it
            reply.body["token"] = Issue(account, s.tokenHours);
            return reply;
        }

        static Reply Me(uint32 account)
        {
            std::string name;
            AccountMgr::GetName(account, name);
            std::string email;
            if (QueryResult result = LoginDatabase.Query(Acore::StringFormat("SELECT email FROM account WHERE id = {}", account)))
                email = result->Fetch()[0].Get<std::string>();
            return {200, {{"username", name}, {"email", email}}};
        }

        static Reply ChangePassword(uint32 account, Json const& body)
        {
            std::string current = body.value("current", "");
            std::string next = body.value("new", "");
            if (next.size() < 6 || next.size() > MAX_PASS_STR)
                return Fail(400, "bad_password", "Password must be 6-16 characters.");
            if (!AccountMgr::CheckPassword(account, current))
                return Fail(401, "bad_credentials", "Current password is wrong.");
            if (AccountMgr::ChangePassword(account, next) != AOR_OK)
                return Fail(400, "rejected", "The server rejected that password.");
            return {200, {{"ok", true}}};
        }

        static Reply ChangeEmail(uint32 account, Json const& body)
        {
            std::string password = body.value("password", "");
            std::string email = body.value("email", "");
            static std::regex const emailRule("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$");
            if (email.size() > 120 || !std::regex_match(email, emailRule))
                return Fail(400, "bad_email", "Enter a valid email address.");
            if (!AccountMgr::CheckPassword(account, password))
                return Fail(401, "bad_credentials", "Password is wrong.");
            if (AccountMgr::ChangeEmail(account, email) != AOR_OK)
                return Fail(400, "rejected", "The server rejected that email.");
            return {200, {{"ok", true}, {"email", email}}};
        }

        static Reply Characters(uint32 account)
        {
            Json live = Json::array();
            if (QueryResult result = CharacterDatabase.Query(Acore::StringFormat(
                "SELECT c.guid, c.name, c.race, c.class, c.gender, c.level, c.zone, c.map, c.online, c.at_login, "
                "c.totaltime, c.logout_time, c.money, c.totalKills, c.totalHonorPoints, c.arenaPoints, "
                "IFNULL(g.name, ''), (SELECT COUNT(*) FROM character_achievement a WHERE a.guid = c.guid) "
                "FROM characters c LEFT JOIN guild_member gm ON gm.guid = c.guid LEFT JOIN guild g ON g.guildid = gm.guildid "
                "WHERE c.account = {} AND c.deleteDate IS NULL ORDER BY c.guid", account)))
            {
                do
                {
                    Field* f = result->Fetch();
                    uint8 raceId = f[2].Get<uint8>();
                    uint8 classId = f[3].Get<uint8>();
                    ChrRacesEntry const* race = sChrRacesStore.LookupEntry(raceId);
                    ChrClassesEntry const* cls = sChrClassesStore.LookupEntry(classId);
                    AreaTableEntry const* area = sAreaTableStore.LookupEntry(f[6].Get<uint32>());
                    live.push_back({{"guid", f[0].Get<uint32>()}, {"name", f[1].Get<std::string>()},
                        {"raceId", raceId}, {"classId", classId}, {"gender", f[4].Get<uint8>()},
                        {"race", race ? LocaleName(race->name) : ""}, {"class", cls ? LocaleName(cls->name) : ""},
                        {"level", f[5].Get<uint8>()}, {"zone", area ? LocaleName(area->area_name) : ""},
                        {"online", f[8].Get<bool>()}, {"pendingService", f[9].Get<uint32>()},
                        {"playedSeconds", f[10].Get<uint32>()}, {"lastSeen", f[11].Get<uint32>()}, {"money", f[12].Get<uint32>()},
                        {"kills", f[13].Get<uint32>()}, {"honor", f[14].Get<uint32>()}, {"arena", f[15].Get<uint32>()},
                        {"guild", f[16].Get<std::string>()}, {"achievements", f[17].Get<uint64>()}});
                } while (result->NextRow());
            }
            Json deleted = Json::array();
            if (QueryResult result = CharacterDatabase.Query(Acore::StringFormat(
                "SELECT guid, deleteInfos_Name, race, class, level, deleteDate, gender FROM characters "
                "WHERE deleteInfos_Account = {} AND deleteDate IS NOT NULL ORDER BY deleteDate DESC", account)))
            {
                do
                {
                    Field* f = result->Fetch();
                    ChrRacesEntry const* race = sChrRacesStore.LookupEntry(f[2].Get<uint8>());
                    ChrClassesEntry const* cls = sChrClassesStore.LookupEntry(f[3].Get<uint8>());
                    deleted.push_back({{"guid", f[0].Get<uint32>()}, {"name", f[1].Get<std::string>()},
                        {"raceId", f[2].Get<uint8>()}, {"classId", f[3].Get<uint8>()}, {"gender", f[6].Get<uint8>()},
                        {"race", race ? LocaleName(race->name) : ""}, {"class", cls ? LocaleName(cls->name) : ""},
                        {"level", f[4].Get<uint8>()}, {"deletedAt", f[5].Get<uint32>()}});
                } while (result->NextRow());
            }
            Json acct = Json::object();
            if (QueryResult result = LoginDatabase.Query(Acore::StringFormat(
                "SELECT UNIX_TIMESTAMP(joindate), IFNULL(UNIX_TIMESTAMP(last_login), 0) FROM account WHERE id = {}", account)))
            {
                Field* f = result->Fetch();
                acct = {{"joined", f[0].Get<uint32>()}, {"lastLogin", f[1].Get<uint32>()}};
            }
            return {200, {{"characters", live}, {"deleted", deleted}, {"account", acct}}};
        }

        // route: "<guid>/delete" | "<guid>/restore" | "<guid>/service"
        static std::function<Reply()> CharacterAction(uint32 account, std::string const& route, Json const& body, Settings const& s)
        {
            std::size_t slash = route.find('/');
            if (slash == std::string::npos || slash == 0 || slash > 10 || route.find_first_not_of("0123456789") < slash)
                return {};
            uint32 guid = static_cast<uint32>(std::stoul(route.substr(0, slash)));
            std::string action = route.substr(slash + 1);
            if (action == "delete")
                return [=] { return s.charDelete ? Delete(account, guid) : Fail(403, "disabled", "Character deletion is disabled."); };
            if (action == "restore")
                return [=] { return s.charDelete ? Restore(account, guid) : Fail(403, "disabled", "Character restore is disabled."); };
            if (action == "service")
                return [=] { return Service(account, guid, body.value("service", ""), s); };
            return {};
        }

        static bool InUse(uint32 guid)
        {
            return ObjectAccessor::FindConnectedPlayer(ObjectGuid::Create<HighGuid::Player>(guid)) ||
                sWorldSessionMgr->FindOfflineSessionForCharacterGUID(guid);
        }

        static bool Owns(uint32 account, uint32 guid)
        {
            CharacterCacheEntry const* data = sCharacterCache->GetCharacterCacheByGuid(ObjectGuid::Create<HighGuid::Player>(guid));
            return data && data->AccountId == account;
        }

        static Reply Delete(uint32 account, uint32 guid)
        {
            ObjectGuid object = ObjectGuid::Create<HighGuid::Player>(guid);
            if (!Owns(account, guid))
                return Fail(404, "not_found", "No such character on this account.");
            if (InUse(guid))
                return Fail(409, "online", "Log the character out of the game first.");
            if (sGuildMgr->GetGuildByLeader(object))
                return Fail(409, "guild_leader", "Hand over guild leadership before deleting this character.");
            if (sArenaTeamMgr->GetArenaTeamByCaptain(object))
                return Fail(409, "arena_captain", "Hand over your arena team before deleting this character.");
            sScriptMgr->OnPlayerDelete(object, account);
            sCalendarMgr->RemoveAllPlayerEventsAndInvites(object);
            // The core erases the character for good unless CharDelete.Method is "unlink" (and the level
            // is above CharDelete.MinLevel). Force a soft delete so the launcher can offer a restore.
            uint32 method = sWorld->getIntConfig(CONFIG_CHARDELETE_METHOD);
            uint32 minLevel = sWorld->getIntConfig(CONFIG_CHARDELETE_MIN_LEVEL);
            sWorld->setIntConfig(CONFIG_CHARDELETE_METHOD, CHAR_DELETE_UNLINK);
            sWorld->setIntConfig(CONFIG_CHARDELETE_MIN_LEVEL, 0);
            Player::DeleteFromDB(guid, account, true, false);
            sWorld->setIntConfig(CONFIG_CHARDELETE_METHOD, method);
            sWorld->setIntConfig(CONFIG_CHARDELETE_MIN_LEVEL, minLevel);
            sWorld->UpdateRealmCharCount(account);
            LOG_INFO("module.launcherapi", "Account {} deleted character {} from the launcher", account, guid);
            return {200, {{"ok", true}}};
        }

        static Reply Restore(uint32 account, uint32 guid)
        {
            QueryResult deleted = CharacterDatabase.Query(Acore::StringFormat(
                "SELECT deleteInfos_Name FROM characters WHERE guid = {} AND deleteInfos_Account = {} AND deleteDate IS NOT NULL",
                guid, account));
            if (!deleted)
                return Fail(404, "not_found", "No such deleted character on this account.");
            std::string name = deleted->Fetch()[0].Get<std::string>();
            if (AccountMgr::GetCharactersCount(account) >= sWorld->getIntConfig(CONFIG_CHARACTERS_PER_ACCOUNT))
                return Fail(409, "full", "Your account has no free character slot.");
            if (sCharacterCache->GetCharacterGuidByName(name))
                return Fail(409, "name_taken", "Another character now uses that name.");
            CharacterDatabasePreparedStatement* stmt = CharacterDatabase.GetPreparedStatement(CHAR_SEL_CHARACTER_NAME_DATA);
            stmt->SetData(0, guid);
            PreparedQueryResult data = CharacterDatabase.Query(stmt);
            if (!data)
                return Fail(404, "not_found", "Character data is missing.");
            Field* f = data->Fetch();
            if (f[4].IsNull() || (f[4].Get<uint8>() != TEAM_ALLIANCE && f[4].Get<uint8>() != TEAM_HORDE))
                return Fail(409, "bad_team", "Character data is invalid; ask an administrator.");
            TeamId team = static_cast<TeamId>(f[4].Get<uint8>());
            stmt = CharacterDatabase.GetPreparedStatement(CHAR_UDP_RESTORE_DELETE_INFO);
            stmt->SetData(0, name);
            stmt->SetData(1, account);
            stmt->SetData(2, guid);
            CharacterDatabase.Execute(stmt);
            sCharacterCache->AddCharacterCacheEntry(ObjectGuid::Create<HighGuid::Player>(guid), account, name,
                f[2].Get<uint8>(), f[0].Get<uint8>(), f[1].Get<uint8>(), f[3].Get<uint8>(), team);
            sWorld->UpdateRealmCharCount(account);
            return {200, {{"ok", true}}};
        }

        static Reply Service(uint32 account, uint32 guid, std::string const& service, Settings const& s)
        {
            uint32 flag = 0;
            if (service == "rename" && s.rename)
                flag = AT_LOGIN_RENAME;
            else if (service == "customize" && s.customize)
                flag = AT_LOGIN_CUSTOMIZE;
            else if (service == "faction" && s.faction)
                flag = AT_LOGIN_CHANGE_FACTION;
            else if (service == "race" && s.race)
                flag = AT_LOGIN_CHANGE_RACE;
            if (!flag)
                return Fail(400, "bad_service", "That service is unavailable.");
            if (!Owns(account, guid))
                return Fail(404, "not_found", "No such character on this account.");
            if (InUse(guid))
                return Fail(409, "online", "Log the character out of the game first.");
            CharacterDatabasePreparedStatement* stmt = CharacterDatabase.GetPreparedStatement(CHAR_UPD_ADD_AT_LOGIN_FLAG);
            stmt->SetData(0, static_cast<uint16>(flag));
            stmt->SetData(1, guid);
            CharacterDatabase.Execute(stmt);
            return {200, {{"ok", true}, {"message", "Log in to that character in the game client to finish."}}};
        }

        Reply PresenceOf(uint32 account)
        {
            std::lock_guard lock(mutex_);
            auto found = online_.find(account);
            if (found == online_.end())
                return {200, {{"online", false}}};
            Presence const& p = found->second;
            return {200, {{"online", true}, {"character", {{"name", p.name}, {"level", p.level}, {"race", p.race},
                {"raceId", p.raceId}, {"class", p.cls}, {"classId", p.classId}, {"zone", p.zone}, {"map", p.mapId}}}}};
        }

        std::mutex mutex_;
        Settings settings_;
        std::unordered_map<std::string, Token> tokens_;
        std::unordered_map<std::string, std::deque<Clock::time_point>> hits_;
        std::unordered_map<std::string, std::pair<Clock::time_point, Json>> lookups_;
        std::unordered_map<uint32, Presence> online_;
        std::deque<Task> tasks_;
        asio::io_context io_;
        std::unique_ptr<asio::ssl::context> tls_;
        std::unique_ptr<Tcp::acceptor> acceptor_;
        std::thread listener_;
        std::atomic<bool> running_{false};
        std::atomic<uint32> active_{0};
    };

    class LauncherWorld final : public WorldScript
    {
    public:
        LauncherWorld() : WorldScript("LauncherApiWorld") { }
        void OnAfterConfigLoad(bool) override { Api::Instance().Configure(); }
        void OnStartup() override { Api::Instance().Start(); }
        void OnUpdate(uint32) override { Api::Instance().Pump(); }
        void OnShutdown() override { Api::Instance().Stop(); }
    };

    class LauncherPlayer final : public PlayerScript
    {
    public:
        LauncherPlayer() : PlayerScript("LauncherApiPlayer", {PLAYERHOOK_ON_LOGIN, PLAYERHOOK_ON_LOGOUT,
            PLAYERHOOK_ON_LEVEL_CHANGED, PLAYERHOOK_ON_UPDATE_ZONE}) { }
        void OnPlayerLogin(Player* player) override { Api::Instance().Track(player); }
        void OnPlayerLogout(Player* player) override { Api::Instance().Untrack(player); }
        void OnPlayerLevelChanged(Player* player, uint8) override { Api::Instance().Track(player); }
        void OnPlayerUpdateZone(Player* player, uint32, uint32) override { Api::Instance().Track(player); }
    };
}

void AddSC_launcher_api()
{
    new LauncherWorld();
    new LauncherPlayer();
}
