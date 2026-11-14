#include "DiscordBridge.h"

#include "WorldChat.h"
#include "Config.h"
#include "Log.h"
#include "Player.h"

#include <boost/asio.hpp>
#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>
#include <boost/property_tree/json_parser.hpp>

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <deque>
#include <mutex>
#include <optional>
#include <sstream>
#include <string>
#include <thread>
#include <utility>

namespace
{
    namespace asio = boost::asio;
    namespace beast = boost::beast;
    namespace http = beast::http;
    namespace pt = boost::property_tree;

    using Tcp = asio::ip::tcp;
    using Clock = std::chrono::steady_clock;

    constexpr std::size_t MaxQueue = 128;
    constexpr std::size_t MaxBatch = 16;

    struct Message
    {
        std::string author;
        std::string text;
    };

    struct Outgoing
    {
        std::string id;
        std::string author;
        std::string text;
        uint32 classId = 0;
        uint32 teamId = 0;
        Clock::time_point queuedAt = Clock::now();
    };

    struct HttpResponse
    {
        unsigned status = 0;
        std::string body;
    };

    bool IsSnowflake(std::string const& value)
    {
        return !value.empty() && value.size() <= 20 &&
            std::all_of(value.begin(), value.end(), [](unsigned char c) { return c >= '0' && c <= '9'; });
    }

    std::string EscapeGameText(std::string const& input, std::size_t limit)
    {
        std::string output;
        output.reserve(std::min(input.size(), limit));
        for (unsigned char c : input)
        {
            if (output.size() >= limit)
                break;

            if (c == '\n' || c == '\r' || c == '\t')
                c = ' ';
            if (c < 32 || c == 127)
                continue;
            if (c == '|')
            {
                if (output.size() + 2 > limit)
                    break;
                output += "||";
            }
            else
                output.push_back(static_cast<char>(c));
        }
        return output;
    }

    std::optional<HttpResponse> Exchange(uint16 port, std::string const& secret, http::verb method,
        std::string const& target, std::string const& body = {})
    {
        try
        {
            asio::io_context io;
            Tcp::resolver resolver(io);
            beast::tcp_stream stream(io);
            stream.expires_after(std::chrono::seconds(3));
            stream.connect(resolver.resolve("127.0.0.1", std::to_string(port)));

            http::request<http::string_body> request{method, target, 11};
            request.set(http::field::host, "127.0.0.1");
            request.set(http::field::user_agent, "EsteriaWorldChat/1");
            request.set("x-esteria-secret", secret);
            if (method == http::verb::post)
                request.set(http::field::content_type, "application/json");
            request.body() = body;
            request.prepare_payload();

            stream.expires_after(std::chrono::seconds(3));
            http::write(stream, request);
            beast::flat_buffer buffer;
            http::response_parser<http::string_body> parser;
            parser.body_limit(65536);
            stream.expires_after(std::chrono::seconds(3));
            http::read(stream, buffer, parser);
            auto response = parser.release();
            return HttpResponse{static_cast<unsigned>(response.result_int()), std::move(response.body())};
        }
        catch (std::exception const&)
        {
            return std::nullopt;
        }
    }

    class Bridge
    {
    public:
        static Bridge& Instance()
        {
            static Bridge instance;
            return instance;
        }

        void Configure(bool crossFaction)
        {
            enabled_ = sConfigMgr->GetOption<bool>("WorldChat.DiscordBridge.Enable", false);
            int port = sConfigMgr->GetOption<int>("WorldChat.DiscordBridge.Port", 22150);
            secret_ = sConfigMgr->GetOption<std::string>("WorldChat.DiscordBridge.Secret", "");

            if (enabled_ && (!crossFaction || port < 1 || port > 65535 || secret_.size() < 32))
            {
                enabled_ = false;
                LOG_ERROR("module.worldchat.discord",
                    "Discord bridge disabled: enable cross-faction chat and provide a valid port and 32+ character secret");
            }
            port_ = static_cast<uint16>(std::clamp(port, 1, 65535));
        }

        void Start()
        {
            if (!enabled_ || worker_.joinable())
                return;

            stopping_ = false;
            worker_ = std::thread([this] { Run(); });
            LOG_INFO("module.worldchat.discord", "Discord world-chat bridge enabled on loopback port {}", port_);
        }

        void Stop()
        {
            stopping_ = true;
            if (worker_.joinable())
                worker_.join();
        }

        void Publish(Player const& sender, std::string const& text, int team)
        {
            if (!enabled_ || team != -1)
                return;

            Outgoing message;
            message.id = std::to_string(std::chrono::system_clock::now().time_since_epoch().count())
                + "-" + std::to_string(++sequence_);
            message.author = sender.GetName();
            message.text = text.substr(0, 500);
            message.classId = sender.getClass();
            message.teamId = sender.GetTeamId();

            std::lock_guard lock(mutex_);
            if (outgoing_.size() < MaxQueue)
                outgoing_.push_back(std::move(message));
        }

        void Tick()
        {
            for (std::size_t i = 0; i < MaxBatch; ++i)
            {
                Message message;
                {
                    std::lock_guard lock(mutex_);
                    if (incoming_.empty())
                        break;
                    message = std::move(incoming_.front());
                    incoming_.pop_front();
                }
                WC::SendDiscordWorldMessage(EscapeGameText(message.author, 48),
                    EscapeGameText(message.text, 240));
            }
        }

    private:
        void SendPending()
        {
            std::optional<Outgoing> message;
            {
                std::lock_guard lock(mutex_);
                if (!outgoing_.empty())
                    message = outgoing_.front();
            }
            if (!message)
                return;

            if (Clock::now() - message->queuedAt > std::chrono::minutes(2))
            {
                RemoveSent(message->id);
                return;
            }

            pt::ptree json;
            json.put("id", message->id);
            json.put("author", message->author);
            json.put("text", message->text);
            json.put("classId", message->classId);
            json.put("teamId", message->teamId);
            std::ostringstream body;
            pt::write_json(body, json, false);

            auto response = Exchange(port_, secret_, http::verb::post, "/outgoing", body.str());
            if (response && response->status >= 200 && response->status < 300)
                RemoveSent(message->id);
        }

        void RemoveSent(std::string const& id)
        {
            std::lock_guard lock(mutex_);
            if (!outgoing_.empty() && outgoing_.front().id == id)
                outgoing_.pop_front();
        }

        void ReceivePending()
        {
            std::string const after = cursor_.empty() ? "latest" : cursor_;
            auto response = Exchange(port_, secret_, http::verb::get, "/incoming?after=" + after);
            if (!response || response->status != 200)
                return;

            try
            {
                std::istringstream body(response->body);
                pt::ptree json;
                pt::read_json(body, json);
                if (cursor_.empty())
                {
                    auto latest = json.get<std::string>("cursor", "0");
                    cursor_ = IsSnowflake(latest) ? latest : "0";
                    return;
                }

                auto messages = json.get_child_optional("messages");
                if (!messages)
                    return;

                for (auto const& item : *messages)
                {
                    std::string const id = item.second.get<std::string>("id", "");
                    if (!IsSnowflake(id))
                        continue;

                    std::string const author = item.second.get<std::string>("author", "");
                    std::string const text = item.second.get<std::string>("text", "");
                    if (author.empty() || text.empty())
                    {
                        cursor_ = id;
                        continue;
                    }

                    std::lock_guard lock(mutex_);
                    if (incoming_.size() >= MaxQueue)
                        return;
                    incoming_.push_back({author, text});
                    cursor_ = id;
                }
            }
            catch (std::exception const&)
            {
                // Bad responses are discarded. The cursor is retained so messages can be retried.
            }
        }

        void Run()
        {
            while (!stopping_)
            {
                SendPending();
                if (!stopping_)
                    ReceivePending();
                std::this_thread::sleep_for(std::chrono::milliseconds(400));
            }
        }

        bool enabled_ = false;
        uint16 port_ = 22150;
        std::string secret_;
        std::uint64_t sequence_ = 0;
        std::string cursor_;
        std::mutex mutex_;
        std::deque<Outgoing> outgoing_;
        std::deque<Message> incoming_;
        std::atomic_bool stopping_{false};
        std::thread worker_;
    };
}

namespace WC::DiscordBridge
{
    void Configure(bool crossFaction)
    {
        Bridge::Instance().Configure(crossFaction);
    }

    void Start()
    {
        Bridge::Instance().Start();
    }

    void Stop()
    {
        Bridge::Instance().Stop();
    }

    void Tick()
    {
        Bridge::Instance().Tick();
    }

    void Publish(Player const& sender, std::string const& message, int team)
    {
        Bridge::Instance().Publish(sender, message, team);
    }
}
