#include "ScriptMgr.h"
#include "Chat.h"
#include "Config.h"
#include "DBCStores.h"
#include "World.h"
#include "Log.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "WorldSession.h"
#include "../vendor/json.hpp"
#include <utility>
#include <boost/asio.hpp>
#include <boost/asio/ssl.hpp>
#include <boost/beast.hpp>
#include <boost/beast/ssl.hpp>
#include <openssl/ssl.h>
#include <algorithm>
#include <chrono>
#include <condition_variable>
#include <deque>
#include <mutex>
#include <regex>
#include <thread>
#include <unordered_map>

namespace
{
    namespace asio = boost::asio;
    namespace beast = boost::beast;
    namespace http = beast::http;
    using Json = nlohmann::json;
    using Clock = std::chrono::steady_clock;
    using Tcp = asio::ip::tcp;
    constexpr std::size_t MaxBytes = 23040;
    constexpr std::size_t FragmentBytes = 180;
    constexpr std::size_t MaxFragments = 128;

    struct Settings
    {
        bool enabled = false;
        bool tls = false;
        std::string host;
        std::string port;
        std::string secret;
        std::string server;
        std::string realm;
    };
    struct Job
    {
        ObjectGuid guid;
        uint32 account = 0;
        uint64 generation = 0;
        uint32 request = 0;
        std::string payload;
        Settings settings;
    };
    struct Result
    {
        Job job;
        std::string payload;
    };
    struct Assembly
    {
        Clock::time_point started = Clock::now();
        uint32 request = 0;
        std::vector<std::string> parts;
        std::size_t bytes = 0;
    };
    struct Session
    {
        uint64 generation = 0;
        Clock::time_point window = Clock::now();
        Clock::time_point activity{}; // next character-activity report is due when this is old enough
        uint32 fragments = 0;
        uint32 requests = 0;
        Assembly assembly;
    };

    template <class Stream>
    asio::awaitable<std::string> Exchange(Stream& stream, Job const& job)
    {
        http::request<http::string_body> request{http::verb::post, "/api/v2/bridge/chat", 11};
        request.set(http::field::host, job.settings.host);
        request.set(http::field::content_type, "application/json");
        request.set(http::field::authorization, "Bearer " + job.settings.secret);
        request.body() = job.payload;
        request.prepare_payload();
        co_await http::async_write(stream, request, asio::use_awaitable);
        beast::flat_buffer buffer;
        http::response_parser<http::string_body> parser;
        parser.body_limit(MaxBytes);
        co_await http::async_read(stream, buffer, parser, asio::use_awaitable);
        auto response = parser.release();
        Json value = Json::parse(response.body());
        if (!value.is_object())
            throw std::runtime_error("Invalid bridge response");
        if (response.result_int() >= 400 && !value.contains("error"))
            throw std::runtime_error("Bridge rejected request");
        co_return response.body();
    }

    std::string Request(Job const& job)
    {
        asio::io_context io;
        asio::ssl::context context(asio::ssl::context::tls_client);
        context.set_default_verify_paths();
        Tcp::resolver resolver(io);
        beast::ssl_stream<beast::tcp_stream> stream(io, context);
        asio::steady_timer timeout(io, std::chrono::seconds(5));
        timeout.async_wait([&](boost::system::error_code error)
        {
            if (error)
                return;
            resolver.cancel();
            boost::system::error_code ignored;
            beast::get_lowest_layer(stream).socket().close(ignored);
        });
        std::string result;
        asio::co_spawn(io, [&]() -> asio::awaitable<void>
        {
            auto endpoints = co_await resolver.async_resolve(job.settings.host, job.settings.port, asio::use_awaitable);
            co_await beast::get_lowest_layer(stream).async_connect(endpoints, asio::use_awaitable);
            if (job.settings.tls)
            {
                if (!SSL_set_tlsext_host_name(stream.native_handle(), job.settings.host.c_str()))
                    throw std::runtime_error("TLS hostname setup failed");
                stream.set_verify_mode(asio::ssl::verify_peer);
                stream.set_verify_callback(asio::ssl::host_name_verification(job.settings.host));
                co_await stream.async_handshake(asio::ssl::stream_base::client, asio::use_awaitable);
                result = co_await Exchange(stream, job);
            }
            else
                result = co_await Exchange(beast::get_lowest_layer(stream), job);
        }, [&](std::exception_ptr error)
        {
            timeout.cancel();
            if (error)
                result = R"({"error":"disconnected","message":"Social service unavailable; retry the same request."})";
        });
        io.run();
        return result;
    }

    class Bridge
    {
    public:
        static Bridge& Instance()
        {
            static Bridge bridge;
            return bridge;
        }

        void Configure()
        {
            Settings next;
            next.enabled = sConfigMgr->GetOption<bool>("EsteriaChat.Enable", false);
            next.secret = sConfigMgr->GetOption<std::string>("EsteriaChat.BridgeSecret", "");
            next.server = sConfigMgr->GetOption<std::string>("EsteriaChat.ServerId", "esteria");
            next.realm = sConfigMgr->GetOption<std::string>("EsteriaChat.RealmId", "1");
            std::string origin = sConfigMgr->GetOption<std::string>("EsteriaChat.ApiOrigin", "http://127.0.0.1:7384");
            std::smatch match;
            if (!std::regex_match(origin, match, std::regex(R"((http|https)://([A-Za-z0-9.-]+)(?::([0-9]{1,5}))?/?)")))
                next.enabled = false;
            else
            {
                next.tls = match[1] == "https";
                next.host = match[2];
                next.port = match[3].matched ? match[3].str() : next.tls ? "443" : "80";
                if (!next.tls && next.host != "127.0.0.1" && next.host != "localhost")
                    next.enabled = false;
            }
            if (next.secret.size() < 32)
                next.enabled = false;
            if (!next.enabled && sConfigMgr->GetOption<bool>("EsteriaChat.Enable", false))
                LOG_ERROR("module.esteriachat", "Chat disabled: use TLS or loopback and a 32+ character bridge secret");
            settings_ = std::move(next);
        }

        void Start()
        {
            worker_ = std::thread([this]
            {
                for (;;)
                {
                    Job job;
                    {
                        std::unique_lock lock(mutex_);
                        ready_.wait(lock, [this] { return stopping_ || !jobs_.empty(); });
                        if (stopping_)
                            return;
                        job = std::move(jobs_.front());
                        jobs_.pop_front();
                    }
                    std::string response;
                    try
                    {
                        response = Request(job);
                    }
                    catch (...)
                    {
                        response = R"({"error":"disconnected","message":"Social service unavailable."})";
                    }
                    std::lock_guard lock(mutex_);
                    if (results_.size() < 128)
                        results_.push_back({std::move(job), std::move(response)});
                }
            });
        }

        void Stop()
        {
            {
                std::lock_guard lock(mutex_);
                stopping_ = true;
                jobs_.clear();
            }
            ready_.notify_all();
            if (worker_.joinable())
                worker_.join();
        }

        void Login(Player* player)
        {
            sessions_[player->GetGUID()] = Session{++generation_};
        }

        void Logout(Player* player)
        {
            Submit(player, 0, Json{{"op", "logout"}});
            sessions_.erase(player->GetGUID());
        }

        void Receive(Player* player, std::string const& message)
        {
            if (!settings_.enabled)
                return;
            auto& session = sessions_[player->GetGUID()];
            auto now = Clock::now();
            if (now - session.window > std::chrono::minutes(1))
            {
                session.window = now;
                session.fragments = 0;
                session.requests = 0;
            }
            if (++session.fragments > 480)
                return;
            std::smatch match;
            if (!std::regex_match(message, match, std::regex(R"(EC1\t1:([0-9]{1,9}):([0-9]{1,3}):([0-9]{1,3}):([\s\S]{1,180}))")))
                return;
            uint32 request = std::stoul(match[1]);
            std::size_t index = std::stoul(match[2]);
            std::size_t count = std::stoul(match[3]);
            if (!request || !index || index > count || count > MaxFragments)
                return;
            auto& assembly = session.assembly;
            if (assembly.request != request || now - assembly.started > std::chrono::seconds(15))
            {
                if (++session.requests > 60)
                    return;
                assembly = Assembly{now, request, std::vector<std::string>(count), 0};
            }
            if (assembly.parts.size() != count || !assembly.parts[index - 1].empty())
                return;
            assembly.parts[index - 1] = match[4];
            assembly.bytes += assembly.parts[index - 1].size();
            if (assembly.bytes > MaxBytes)
            {
                assembly = {};
                return;
            }
            if (std::any_of(assembly.parts.begin(), assembly.parts.end(), [](auto const& part) { return part.empty(); }))
                return;
            std::string payload;
            for (auto const& part : assembly.parts)
                payload += part;
            assembly = {};
            try
            {
                Json value = Json::parse(payload);
                if (!value.is_object())
                    return;
                Submit(player, request, std::move(value));
            }
            catch (...)
            {
                Reply(player, request, R"({"error":"bad_request","message":"Invalid chat request."})");
            }
        }

        void Tick()
        {
            std::deque<Result> completed;
            {
                std::lock_guard lock(mutex_);
                completed.swap(results_);
            }
            for (auto& result : completed)
            {
                auto session = sessions_.find(result.job.guid);
                if (session == sessions_.end() || session->second.generation != result.job.generation || !result.job.request)
                    continue;
                Player* player = ObjectAccessor::FindPlayer(result.job.guid);
                if (player && player->GetSession()->GetAccountId() == result.job.account)
                    Reply(player, result.job.request, result.payload);
            }
            uint32 budget = 16;
            while (!outbound_.empty() && budget--)
            {
                auto packet = std::move(outbound_.front());
                outbound_.pop_front();
                auto session = sessions_.find(packet.guid);
                Player* player = ObjectAccessor::FindPlayer(packet.guid);
                if (!player || session == sessions_.end() || session->second.generation != packet.generation)
                    continue;
                WorldPacket data;
                ChatHandler::BuildChatPacket(data, CHAT_MSG_WHISPER, LANG_ADDON, player, player, packet.message);
                player->GetSession()->SendPacket(&data);
            }
            for (auto& entry : sessions_)
            {
                if (Clock::now() - entry.second.assembly.started > std::chrono::seconds(15))
                    entry.second.assembly = {};
                if (Clock::now() - entry.second.activity > std::chrono::seconds(30))
                {
                    entry.second.activity = Clock::now();
                    if (Player* player = ObjectAccessor::FindPlayer(entry.first))
                        ReportActivity(player);
                }
            }
        }

    private:
        struct Packet { ObjectGuid guid; uint64 generation; std::string message; };

        // Worldserver-owned character facts for account friends. Identity still comes from the session in Submit.
        void ReportActivity(Player* player)
        {
            std::string zone;
            if (AreaTableEntry const* area = sAreaTableStore.LookupEntry(player->GetZoneId()))
                zone = area->area_name[sWorld->GetDefaultDbcLocale()];
            Submit(player, 0, Json{{"op", "activity"}, {"activity", {{"level", player->GetLevel()},
                {"class", uint32(player->getClass())}, {"race", uint32(player->getRace())}, {"zone", zone}}}});
        }

        void Submit(Player* player, uint32 request, Json value)
        {
            value["protocolVersion"] = 1;
            value["serverId"] = settings_.server;
            value["realmId"] = settings_.realm;
            value["gameId"] = player->GetSession()->GetAccountId();
            value["gameName"] = player->GetName();
            value.erase("accountId");
            value.erase("token");
            auto session = sessions_.find(player->GetGUID());
            if (session == sessions_.end())
                return;
            std::lock_guard lock(mutex_);
            if (stopping_ || !settings_.enabled || jobs_.size() >= 128)
            {
                if (request)
                    Reply(player, request, R"({"error":"busy","message":"Chat bridge busy; retry shortly."})");
                return;
            }
            jobs_.push_back({player->GetGUID(), player->GetSession()->GetAccountId(), session->second.generation,
                request, value.dump(), settings_});
            ready_.notify_one();
        }

        void Reply(Player* player, uint32 request, std::string const& payload)
        {
            if (payload.empty() || payload.size() > MaxBytes || outbound_.size() + MaxFragments > 2048)
                return;
            std::size_t count = (payload.size() + FragmentBytes - 1) / FragmentBytes;
            for (std::size_t i = 0; i < count; ++i)
                outbound_.push_back({player->GetGUID(), sessions_[player->GetGUID()].generation,
                    "EC1\t1:" + std::to_string(request) + ":" + std::to_string(i + 1) + ":" + std::to_string(count) +
                    ":" + payload.substr(i * FragmentBytes, FragmentBytes)});
        }

        Settings settings_;
        std::unordered_map<ObjectGuid, Session> sessions_;
        uint64 generation_ = 0;
        std::mutex mutex_;
        std::condition_variable ready_;
        std::deque<Job> jobs_;
        std::deque<Result> results_;
        std::deque<Packet> outbound_;
        std::thread worker_;
        bool stopping_ = false;
    };

    class ChatWorld final : public WorldScript
    {
    public:
        ChatWorld() : WorldScript("EsteriaChatWorld") { }
        void OnAfterConfigLoad(bool) override { Bridge::Instance().Configure(); }
        void OnStartup() override { Bridge::Instance().Start(); }
        void OnUpdate(uint32) override { Bridge::Instance().Tick(); }
        void OnShutdown() override { Bridge::Instance().Stop(); }
    };

    class ChatPlayer final : public PlayerScript
    {
    public:
        // OnPlayerCanUseChat(..., Player* receiver) is dispatched under CAN_PLAYER_USE_PRIVATE_CHAT; registering
        // ON_CHAT_WITH_RECEIVER instead left the bridge deaf and the client read its own request back as the reply.
        ChatPlayer() : PlayerScript("EsteriaChatPlayer", {PLAYERHOOK_ON_LOGIN, PLAYERHOOK_ON_LOGOUT,
            PLAYERHOOK_CAN_PLAYER_USE_PRIVATE_CHAT}) { }
        void OnPlayerLogin(Player* player) override { Bridge::Instance().Login(player); }
        void OnPlayerLogout(Player* player) override { Bridge::Instance().Logout(player); }
        bool OnPlayerCanUseChat(Player* player, uint32 type, uint32 language, std::string& message,
            Player* receiver) override
        {
            if (type != CHAT_MSG_WHISPER || language != LANG_ADDON || message.rfind("EC1\t", 0) != 0)
                return true;
            if (receiver == player)
                Bridge::Instance().Receive(player, message);
            return false;
        }
    };
}

void AddSC_esteria_chat()
{
    new ChatWorld();
    new ChatPlayer();
}
