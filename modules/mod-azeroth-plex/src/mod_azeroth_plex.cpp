/*
 * mod-azeroth-plex -- the in-server half of AzerothPlex nearby broadcast.
 *
 * The AzerothPlex client helper plays a Plex stream and places it on a world-space screen. This
 * module is where "nearby" is decided: it owns a small TCP listener (AzerothPlex.Port) beside the
 * worldserver, each running helper opens one connection to it and identifies itself with its
 * character's GUID, and the server drives everything after that. Because the server already knows
 * every player's map and position, the client sends no position of its own -- it publishes the pose
 * of its screen, and the module hands that pose plus the encoded frames to whoever stands close
 * enough on the same map. The media never touches the game socket.
 */

#include "ScriptMgr.h"
#include "Config.h"
#include "Log.h"
#include "ObjectAccessor.h"
#include "ObjectGuid.h"
#include "Player.h"

#include "mod_azeroth_plex_protocol.h"

#include <boost/asio/executor_work_guard.hpp>
#include <boost/asio/io_context.hpp>
#include <boost/asio/ip/tcp.hpp>
#include <boost/asio/post.hpp>
#include <boost/asio/read.hpp>
#include <boost/asio/write.hpp>
#include <boost/system/error_code.hpp>

#include <algorithm>
#include <array>
#include <atomic>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <deque>
#include <memory>
#include <mutex>
#include <string>
#include <thread>
#include <unordered_map>
#include <vector>

namespace AzerothPlex
{
    namespace proto = azerothplex;

    constexpr char const* kLog = "module.azerothplex";
    constexpr uint32_t kWorldTickMs = 250;
    constexpr uint32_t kStateRefreshTicks = 4;
    constexpr size_t kMaxConnections = 64;

    struct Settings
    {
        bool enabled = true;
        uint16_t port = 8086;
        std::string bindAddress = "0.0.0.0";
        bool requireMatchingAddress = true;
        float rangeYards = 80.0f;
        uint16_t maxBroadcastersPerMap = 8;
        uint16_t maxViewersPerBroadcast = 16;
        uint32_t bitrate = 800000;
        uint16_t fps = 24;
        uint16_t width = 640;
        uint16_t height = 360;
        uint32_t minimumClientVersion = 1;
        uint16_t logLevel = 1;
    };

    class AzerothPlexServer;
    class MediaSession;

    /// Thread-safe handle to a media client, so the world tick can reach it without the lock.
    struct PlayerView
    {
        bool valid = false;
        int32 mapId = -1;
        float x = 0.0f;
        float y = 0.0f;
        float z = 0.0f;
    };

    class MediaSession : public std::enable_shared_from_this<MediaSession>
    {
    public:
        MediaSession(boost::asio::ip::tcp::socket socket, uint32_t id)
            : socket_(std::move(socket)), id_(id)
        {
        }

        boost::asio::ip::tcp::socket& Socket() { return socket_; }
        uint32_t Id() const { return id_; }
        bool IsClosed() const { return closed_.load(); }

        std::atomic<uint64_t> guid{ 0 };
        std::atomic<uint32_t> clientVersion{ 0 };
        std::atomic<bool> helloPending{ false };
        std::atomic<bool> identified{ false };
        std::atomic<bool> broadcasting{ false };
        std::atomic<bool> havePose{ false };
        std::atomic<uint32_t> watchTarget{ 0 };
        std::atomic<uint32_t> watchers{ 0 };
        std::atomic<int32_t> poseMapId{ -1 };
        std::atomic<float> poseWidth{ 8.0f };
        std::atomic<float> poseAspect{ 16.0f / 9.0f };
        std::atomic<float> poseDepthOffset{ -0.01f };
        std::atomic<float> poseAudioRange{ 60.0f };
        std::atomic<uint8_t> poseFlags{ 0 };
        std::array<std::atomic<float>, 3> poseCenter{};
        std::array<std::atomic<float>, 3> poseRight{};

        // Written on the media thread before helloPending is released; read on the world thread
        // after it is acquired, which is what makes the pair safe without a lock.
        std::string name;
        std::string address;
        uint32_t sessionId = 0;   // mirrors Id(); carried in control replies

        void Start();
        void Close();
        void SendWatching(uint32_t broadcasterId);
        void SendReject(proto::RejectCode code, std::string const& text);
        void SendState(uint32_t mapId, std::vector<proto::Broadcaster> const& broadcasters);
        void SendWelcome(proto::Welcome const& welcome);
        void QueueMedia(proto::Message type, std::vector<uint8_t> const& payload);

    private:
        enum class Kind
        {
            Control,
            ControlThenClose,
            Video,
            Audio,
        };

        void Enqueue(std::shared_ptr<std::vector<uint8_t>> message, Kind kind);
        void CloseNow();
        void ReadHeader();
        void ReadBody();
        void Handle(proto::Message type);
        void WriteNext();

        boost::asio::ip::tcp::socket socket_;
        uint32_t id_ = 0;
        std::array<uint8_t, sizeof(proto::Header)> header_{};
        std::vector<uint8_t> body_;
        std::deque<std::shared_ptr<std::vector<uint8_t>>> control_;
        std::deque<std::shared_ptr<std::vector<uint8_t>>> audio_;
        std::shared_ptr<std::vector<uint8_t>> pendingVideo_;
        bool writing_ = false;
        bool closeAfterWrite_ = false;
        std::atomic<bool> closed_{ false };
    };

    class AzerothPlexServer
    {
    public:
        static AzerothPlexServer& Instance();

        void ApplySettings(Settings const& incoming);
        void Start();
        void Stop();

        /// World thread: membership, validation and the nearby list.
        void Tick(uint32 diff);

        /// Media thread: fan one broadcaster's frame out to its viewers.
        void RelayMedia(uint32_t fromId, proto::Message type, std::vector<uint8_t> const& payload);

        Settings Current() const { return settings_; }
        uint16_t logLevel() const { return settings_.logLevel; }

    private:
        void Accept();
        std::vector<std::shared_ptr<MediaSession>> Snapshot();

        Settings settings_{};
        boost::asio::io_context io_;
        std::unique_ptr<boost::asio::ip::tcp::acceptor> acceptor_;
        std::unique_ptr<boost::asio::executor_work_guard<boost::asio::io_context::executor_type>> work_;
        std::thread thread_;
        std::mutex mutex_;
        std::unordered_map<uint32_t, std::shared_ptr<MediaSession>> sessions_;
        std::atomic<uint32_t> nextId_{ 1 };
        std::atomic<bool> running_{ false };
        uint32_t tickAccum_ = 0;
        uint32_t tickCount_ = 0;
    };

    AzerothPlexServer& AzerothPlexServer::Instance()
    {
        static AzerothPlexServer instance;
        return instance;
    }

    // --- MediaSession ----------------------------------------------------------------------

    void MediaSession::Start()
    {
        auto self = shared_from_this();
        boost::asio::post(socket_.get_executor(), [self] { self->ReadHeader(); });
    }

    void MediaSession::Close()
    {
        auto self = shared_from_this();
        boost::asio::post(socket_.get_executor(), [self] { self->CloseNow(); });
    }

    void MediaSession::CloseNow()
    {
        if (closed_.exchange(true))
            return;
        boost::system::error_code ignored;
        socket_.shutdown(boost::asio::ip::tcp::socket::shutdown_both, ignored);
        socket_.close(ignored);
    }

    void MediaSession::Enqueue(std::shared_ptr<std::vector<uint8_t>> message, Kind kind)
    {
        auto self = shared_from_this();
        boost::asio::post(socket_.get_executor(), [self, message, kind]
        {
            if (self->closed_.load())
                return;
            switch (kind)
            {
                case Kind::Control:
                    self->control_.push_back(std::move(message));
                    break;
                case Kind::ControlThenClose:
                    self->control_.push_back(std::move(message));
                    self->closeAfterWrite_ = true;
                    break;
                case Kind::Audio:
                    if (self->audio_.size() >= 8)
                        self->audio_.pop_front();
                    self->audio_.push_back(std::move(message));
                    break;
                case Kind::Video:
                    self->pendingVideo_ = std::move(message);
                    break;
            }
            self->WriteNext();
        });
    }

    void MediaSession::SendWelcome(proto::Welcome const& welcome)
    {
        auto message = std::make_shared<std::vector<uint8_t>>(sizeof(proto::Header) + sizeof(welcome));
        proto::Header header{ static_cast<uint8_t>(proto::Message::Welcome),
                              static_cast<uint16_t>(sizeof(welcome)) };
        std::memcpy(message->data(), &header, sizeof(header));
        std::memcpy(message->data() + sizeof(header), &welcome, sizeof(welcome));
        Enqueue(message, Kind::Control);
    }

    void MediaSession::SendReject(proto::RejectCode code, std::string const& text)
    {
        proto::Reject reject{};
        reject.code = static_cast<uint16_t>(code);
        std::snprintf(reject.text, sizeof(reject.text), "%s", text.c_str());
        auto message = std::make_shared<std::vector<uint8_t>>(sizeof(proto::Header) + sizeof(reject));
        proto::Header header{ static_cast<uint8_t>(proto::Message::Reject),
                              static_cast<uint16_t>(sizeof(reject)) };
        std::memcpy(message->data(), &header, sizeof(header));
        std::memcpy(message->data() + sizeof(header), &reject, sizeof(reject));
        Enqueue(message, Kind::ControlThenClose);
    }

    void MediaSession::SendWatching(uint32_t broadcasterId)
    {
        proto::Watching watching{ broadcasterId };
        auto message = std::make_shared<std::vector<uint8_t>>(sizeof(proto::Header) + sizeof(watching));
        proto::Header header{ static_cast<uint8_t>(proto::Message::Watching),
                              static_cast<uint16_t>(sizeof(watching)) };
        std::memcpy(message->data(), &header, sizeof(header));
        std::memcpy(message->data() + sizeof(header), &watching, sizeof(watching));
        Enqueue(message, Kind::Control);
    }

    void MediaSession::SendState(uint32_t mapId, std::vector<proto::Broadcaster> const& broadcasters)
    {
        size_t count = std::min<size_t>(broadcasters.size(), proto::kMaxBroadcastersPerUpdate);
        auto message = std::make_shared<std::vector<uint8_t>>(
            sizeof(proto::Header) + sizeof(proto::State) + count * sizeof(proto::Broadcaster));
        proto::Header header{ static_cast<uint8_t>(proto::Message::State),
                              static_cast<uint16_t>(sizeof(proto::State) + count * sizeof(proto::Broadcaster)) };
        proto::State state{};
        state.mapId = mapId;
        state.count = static_cast<uint16_t>(count);
        std::memcpy(message->data(), &header, sizeof(header));
        std::memcpy(message->data() + sizeof(header), &state, sizeof(state));
        if (count)
        {
            std::memcpy(message->data() + sizeof(header) + sizeof(state), broadcasters.data(),
                        count * sizeof(proto::Broadcaster));
        }
        Enqueue(message, Kind::Control);
    }

    void MediaSession::QueueMedia(proto::Message type, std::vector<uint8_t> const& payload)
    {
        if (payload.empty() || payload.size() > proto::kMaxPayloadBytes)
            return;
        auto message = std::make_shared<std::vector<uint8_t>>(sizeof(proto::Header) + payload.size());
        proto::Header header{ static_cast<uint8_t>(type), static_cast<uint16_t>(payload.size()) };
        std::memcpy(message->data(), &header, sizeof(header));
        std::memcpy(message->data() + sizeof(header), payload.data(), payload.size());
        Enqueue(message, type == proto::Message::Audio ? Kind::Audio : Kind::Video);
    }

    void MediaSession::ReadHeader()
    {
        auto self = shared_from_this();
        boost::asio::async_read(socket_, boost::asio::buffer(header_),
            [self](boost::system::error_code ec, std::size_t)
            {
                if (ec)
                {
                    self->CloseNow();
                    return;
                }
                uint16_t length = static_cast<uint16_t>(self->header_[1] | (self->header_[2] << 8));
                if (length > proto::kMaxPayloadBytes)
                {
                    self->CloseNow();
                    return;
                }
                self->body_.assign(length, 0);
                self->ReadBody();
            });
    }

    void MediaSession::ReadBody()
    {
        if (body_.empty())
        {
            Handle(static_cast<proto::Message>(header_[0]));
            return;
        }
        auto self = shared_from_this();
        boost::asio::async_read(socket_, boost::asio::buffer(body_),
            [self](boost::system::error_code ec, std::size_t)
            {
                if (ec)
                {
                    self->CloseNow();
                    return;
                }
                self->Handle(static_cast<proto::Message>(self->header_[0]));
            });
    }

    void MediaSession::Handle(proto::Message type)
    {
        switch (type)
        {
            case proto::Message::Hello:
            {
                if (body_.size() < sizeof(proto::Hello) || identified.load())
                    break;
                proto::Hello hello{};
                std::memcpy(&hello, body_.data(), sizeof(hello));
                hello.name[proto::kMaxNameBytes - 1] = '\0';
                guid.store(hello.guid);
                name.assign(hello.name);
                clientVersion.store(hello.version);
                helloPending.store(true, std::memory_order_release);
                break;
            }
            case proto::Message::Pose:
            {
                if (body_.size() < sizeof(proto::Pose))
                    break;
                proto::Pose pose{};
                std::memcpy(&pose, body_.data(), sizeof(pose));
                poseCenter[0].store(pose.centerX);
                poseCenter[1].store(pose.centerY);
                poseCenter[2].store(pose.centerZ);
                poseRight[0].store(pose.rightX);
                poseRight[1].store(pose.rightY);
                poseRight[2].store(pose.rightZ);
                poseWidth.store(pose.width);
                poseAspect.store(pose.aspect);
                poseDepthOffset.store(pose.depthOffset);
                poseAudioRange.store(pose.audioRange);
                poseMapId.store(pose.mapId);
                poseFlags.store(static_cast<uint8_t>((pose.visible ? 1 : 0) |
                                                     (pose.depthOcclusion ? 2 : 0) |
                                                     (pose.distanceAudio ? 4 : 0)));
                havePose.store(pose.mapId >= 0);
                break;
            }
            case proto::Message::Start:
                broadcasting.store(identified.load());
                break;
            case proto::Message::Stop:
                broadcasting.store(false);
                break;
            case proto::Message::Watch:
            {
                if (body_.size() < sizeof(proto::Watch))
                    break;
                proto::Watch watch{};
                std::memcpy(&watch, body_.data(), sizeof(watch));
                watchTarget.store(watch.broadcasterId);
                break;
            }
            case proto::Message::Ping:
            {
                uint32_t stamp = 0;
                if (body_.size() >= sizeof(stamp))
                    std::memcpy(&stamp, body_.data(), sizeof(stamp));
                auto message = std::make_shared<std::vector<uint8_t>>(sizeof(proto::Header) + sizeof(stamp));
                proto::Header header{ static_cast<uint8_t>(proto::Message::Pong), sizeof(stamp) };
                std::memcpy(message->data(), &header, sizeof(header));
                std::memcpy(message->data() + sizeof(header), &stamp, sizeof(stamp));
                Enqueue(message, Kind::Control);
                break;
            }
            case proto::Message::Video:
            case proto::Message::Audio:
                if (identified.load() && broadcasting.load())
                    AzerothPlexServer::Instance().RelayMedia(id_, type, body_);
                break;
            default:
                break;
        }

        if (!closed_.load())
            ReadHeader();
    }

    void MediaSession::WriteNext()
    {
        if (writing_ || closed_.load())
            return;
        std::shared_ptr<std::vector<uint8_t>> next;
        if (!control_.empty())
        {
            next = control_.front();
            control_.pop_front();
        }
        else if (pendingVideo_)
        {
            next = pendingVideo_;
            pendingVideo_.reset();
        }
        else if (!audio_.empty())
        {
            next = audio_.front();
            audio_.pop_front();
        }
        if (!next)
        {
            if (closeAfterWrite_)
                CloseNow();
            return;
        }

        writing_ = true;
        auto self = shared_from_this();
        boost::asio::async_write(socket_, boost::asio::buffer(*next),
            [self, next](boost::system::error_code ec, std::size_t)
            {
                self->writing_ = false;
                if (ec)
                {
                    self->CloseNow();
                    return;
                }
                self->WriteNext();
            });
    }

    // --- AzerothPlexServer -----------------------------------------------------------------

    void AzerothPlexServer::ApplySettings(Settings const& incoming)
    {
        settings_ = incoming;
    }

    void AzerothPlexServer::Start()
    {
        if (running_.exchange(true))
            return;
        if (!settings_.enabled)
        {
            LOG_INFO(kLog, "AzerothPlex media listener disabled by configuration.");
            running_.store(false);
            return;
        }

        boost::system::error_code ec;
        boost::asio::ip::address address = boost::asio::ip::make_address(settings_.bindAddress, ec);
        if (ec)
            address = boost::asio::ip::address_v4::any();

        acceptor_ = std::make_unique<boost::asio::ip::tcp::acceptor>(io_);
        boost::asio::ip::tcp::endpoint endpoint(address, settings_.port);
        acceptor_->open(endpoint.protocol(), ec);
        if (!ec)
            acceptor_->set_option(boost::asio::ip::tcp::acceptor::reuse_address(true), ec);
        if (!ec)
            acceptor_->bind(endpoint, ec);
        if (!ec)
            acceptor_->listen(boost::asio::socket_base::max_listen_connections, ec);
        if (ec)
        {
            LOG_ERROR(kLog, "AzerothPlex media listener could not bind {}:{} - {}", settings_.bindAddress,
                      settings_.port, ec.message());
            acceptor_.reset();
            running_.store(false);
            return;
        }

        work_ = std::make_unique<boost::asio::executor_work_guard<boost::asio::io_context::executor_type>>(
            io_.get_executor());
        thread_ = std::thread([this] { io_.run(); });
        Accept();
        LOG_INFO(kLog, "AzerothPlex media listener on {}:{} (range {} yards, {} kbps, {} fps)",
                 settings_.bindAddress, settings_.port, settings_.rangeYards, settings_.bitrate / 1000,
                 settings_.fps);
    }

    void AzerothPlexServer::Stop()
    {
        if (!running_.exchange(false))
            return;
        if (acceptor_)
        {
            boost::system::error_code ignored;
            acceptor_->close(ignored);
            acceptor_.reset();
        }
        {
            std::lock_guard lock(mutex_);
            for (auto const& entry : sessions_)
                entry.second->Close();
            sessions_.clear();
        }
        work_.reset();
        io_.stop();
        if (thread_.joinable())
            thread_.join();
        io_.restart();
        LOG_INFO(kLog, "AzerothPlex media listener stopped.");
    }

    std::vector<std::shared_ptr<MediaSession>> AzerothPlexServer::Snapshot()
    {
        std::lock_guard lock(mutex_);
        std::vector<std::shared_ptr<MediaSession>> snapshot;
        snapshot.reserve(sessions_.size());
        for (auto it = sessions_.begin(); it != sessions_.end();)
        {
            if (it->second->IsClosed())
                it = sessions_.erase(it);
            else
                snapshot.push_back((it++)->second);
        }
        return snapshot;
    }

    void AzerothPlexServer::Accept()
    {
        if (!running_.load() || !acceptor_)
            return;
        acceptor_->async_accept([this](boost::system::error_code ec, boost::asio::ip::tcp::socket socket)
        {
            if (!ec)
            {
                uint32_t id = nextId_.fetch_add(1);
                auto session = std::make_shared<MediaSession>(std::move(socket), id);
                session->sessionId = id;
                boost::system::error_code endpointError;
                auto endpoint = session->Socket().remote_endpoint(endpointError);
                session->address = endpointError ? std::string() : endpoint.address().to_string();

                bool accepted = false;
                {
                    std::lock_guard lock(mutex_);
                    if (sessions_.size() < kMaxConnections)
                    {
                        sessions_[id] = session;
                        accepted = true;
                    }
                }
                if (accepted)
                    session->Start();
                else
                    session->SendReject(proto::RejectCode::TooManyConnections,
                                        "The AzerothPlex listener is full.");
            }
            Accept();
        });
    }

    void AzerothPlexServer::RelayMedia(uint32_t fromId, proto::Message type,
                                       std::vector<uint8_t> const& payload)
    {
        std::lock_guard lock(mutex_);
        for (auto const& entry : sessions_)
        {
            auto const& session = entry.second;
            if (session->Id() == fromId || !session->identified.load())
                continue;
            if (session->watchTarget.load() != fromId)
                continue;
            session->QueueMedia(type, payload);
        }
    }

    void AzerothPlexServer::Tick(uint32 diff)
    {
        if (!running_.load() || !settings_.enabled)
            return;
        tickAccum_ += diff;
        if (tickAccum_ < kWorldTickMs)
            return;
        tickAccum_ = 0;
        ++tickCount_;

        auto sessions = Snapshot();
        if (sessions.empty())
            return;

        // Resolve every identified helper's player once. Object access belongs to this thread.
        struct Entry
        {
            std::shared_ptr<MediaSession> session;
            PlayerView view;
            std::string name;
            bool valid = false;
        };
        std::vector<Entry> entries;
        entries.reserve(sessions.size());
        for (auto const& session : sessions)
        {
            Entry entry;
            entry.session = session;

            if (session->helloPending.exchange(false, std::memory_order_acquire))
            {
                ObjectGuid guid(session->guid.load());
                Player* player = guid ? ObjectAccessor::FindConnectedPlayer(guid) : nullptr;
                if (!player || !player->IsInWorld())
                {
                    session->SendReject(proto::RejectCode::NotInWorld,
                                        "That character is not in the world yet.");
                }
                else if (session->clientVersion.load() < settings_.minimumClientVersion)
                {
                    session->SendReject(proto::RejectCode::BadProtocol,
                                        "Update AzerothPlex to join the media server.");
                }
                else if (settings_.requireMatchingAddress && !session->address.empty() &&
                         player->GetSession()->GetRemoteAddress() != session->address)
                {
                    session->SendReject(proto::RejectCode::AddressMismatch,
                                        "The media connection does not match the game session address.");
                    if (settings_.logLevel)
                    {
                        LOG_INFO(kLog, "Refused media connection for {}: game address {} vs media {}",
                                 player->GetName(), player->GetSession()->GetRemoteAddress(),
                                 session->address);
                    }
                }
                else
                {
                    session->identified.store(true);
                    proto::Welcome welcome{};
                    welcome.sessionId = session->Id();
                    welcome.tickMs = kWorldTickMs;
                    welcome.bitrate = settings_.bitrate;
                    welcome.fps = settings_.fps;
                    welcome.width = settings_.width;
                    welcome.height = settings_.height;
                    welcome.rangeYards = static_cast<uint16_t>(std::max(0.0f, settings_.rangeYards));
                    welcome.maxViewers = settings_.maxViewersPerBroadcast;
                    session->SendWelcome(welcome);
                    if (settings_.logLevel)
                    {
                        LOG_INFO(kLog, "Media session {} joined for {} ({}).", session->Id(),
                                 player->GetName(), session->address);
                    }
                }
            }

            if (session->identified.load())
            {
                ObjectGuid guid(session->guid.load());
                Player* player = guid ? ObjectAccessor::FindConnectedPlayer(guid) : nullptr;
                if (!player || !player->IsInWorld())
                {
                    session->Close();
                }
                else
                {
                    // The server already knows who this is; the handshake name is only a hint.
                    entry.name = player->GetName();
                    entry.valid = true;
                    entry.view.valid = true;
                    entry.view.mapId = static_cast<int32>(player->GetMapId());
                    entry.view.x = player->GetPositionX();
                    entry.view.y = player->GetPositionY();
                    entry.view.z = player->GetPositionZ();
                }
            }
            entries.push_back(std::move(entry));
        }

        // Broadcasters are the helpers that asked to publish with a live pose of their own.
        struct BroadcasterEntry
        {
            std::shared_ptr<MediaSession> session;
            PlayerView view;
            std::string name;
            proto::Pose pose{};
        };
        std::vector<BroadcasterEntry> broadcasters;
        for (auto const& entry : entries)
        {
            if (!entry.valid || !entry.session->broadcasting.load() || !entry.session->havePose.load())
                continue;
            auto const& session = entry.session;
            proto::Pose pose{};
            pose.mapId = session->poseMapId.load();
            if (pose.mapId < 0)
                continue;
            pose.centerX = session->poseCenter[0].load();
            pose.centerY = session->poseCenter[1].load();
            pose.centerZ = session->poseCenter[2].load();
            pose.rightX = session->poseRight[0].load();
            pose.rightY = session->poseRight[1].load();
            pose.rightZ = session->poseRight[2].load();
            pose.width = session->poseWidth.load();
            pose.aspect = session->poseAspect.load();
            pose.depthOffset = session->poseDepthOffset.load();
            pose.audioRange = session->poseAudioRange.load();
            uint8_t flags = session->poseFlags.load();
            pose.visible = (flags & 1) ? 1 : 0;
            pose.depthOcclusion = (flags & 2) ? 1 : 0;
            pose.distanceAudio = (flags & 4) ? 1 : 0;
            pose.broadcasting = 1;
            broadcasters.push_back({ session, entry.view, entry.name, pose });
        }

        for (auto& broadcaster : broadcasters)
        {
            broadcaster.session->watchers.store(0);
        }

        // Every identified helper is a viewer: nearest broadcaster on its map within range, or the
        // broadcast it asked for by name.
        for (auto const& entry : entries)
        {
            if (!entry.valid)
                continue;
            auto const& session = entry.session;
            if (session->broadcasting.load())
            {
                session->watchTarget.store(0);
                continue;
            }

            uint32_t pinned = session->watchTarget.load();
            uint32_t chosen = 0;

            if (pinned != 0)
            {
                auto found = std::find_if(broadcasters.begin(), broadcasters.end(),
                    [pinned](BroadcasterEntry const& item) { return item.session->Id() == pinned; });
                if (found != broadcasters.end() && found->pose.mapId == entry.view.mapId)
                    chosen = pinned;
            }

            if (chosen == 0)
            {
                float bestDistance = 0.0f;
                for (auto const& broadcaster : broadcasters)
                {
                    if (broadcaster.pose.mapId != entry.view.mapId)
                        continue;
                    if (broadcaster.session->watchers.load() >= settings_.maxViewersPerBroadcast)
                        continue;
                    float dx = broadcaster.pose.centerX - entry.view.x;
                    float dy = broadcaster.pose.centerY - entry.view.y;
                    float dz = broadcaster.pose.centerZ - entry.view.z;
                    float distance = std::sqrt(dx * dx + dy * dy + dz * dz);
                    if (distance > settings_.rangeYards)
                        continue;
                    if (chosen == 0 || distance < bestDistance)
                    {
                        chosen = broadcaster.session->Id();
                        bestDistance = distance;
                    }
                }
            }

            session->watchTarget.store(chosen);
            if (chosen != 0)
            {
                auto found = std::find_if(broadcasters.begin(), broadcasters.end(),
                    [chosen](BroadcasterEntry const& item) { return item.session->Id() == chosen; });
                if (found != broadcasters.end())
                    found->session->watchers.fetch_add(1);
            }
        }

        bool refresh = (tickCount_ % kStateRefreshTicks) == 0;
        for (auto const& entry : entries)
        {
            if (!entry.valid)
                continue;
            auto const& session = entry.session;
            uint32_t target = session->watchTarget.load();

            std::vector<proto::Broadcaster> list;
            for (auto const& broadcaster : broadcasters)
            {
                if (broadcaster.pose.mapId != entry.view.mapId)
                    continue;
                float dx = broadcaster.pose.centerX - entry.view.x;
                float dy = broadcaster.pose.centerY - entry.view.y;
                float dz = broadcaster.pose.centerZ - entry.view.z;
                float distance = std::sqrt(dx * dx + dy * dy + dz * dz);
                if (distance > settings_.rangeYards && broadcaster.session->Id() != target)
                    continue;

                proto::Broadcaster record{};
                record.sessionId = broadcaster.session->Id();
                record.distance = distance;
                record.viewers = static_cast<uint16_t>(
                    std::min<uint32_t>(broadcaster.session->watchers.load(), 0xFFFF));
                record.watching = (broadcaster.session->Id() == target) ? 1 : 0;
                std::snprintf(record.name, sizeof(record.name), "%s", broadcaster.name.c_str());
                record.pose = broadcaster.pose;
                list.push_back(record);
            }

            if (list.empty() && target != 0)
            {
                session->SendWatching(0);
                session->watchTarget.store(0);
            }
            else if (target != 0 && !list.empty())
            {
                bool announced = false;
                for (auto const& record : list)
                {
                    if (record.sessionId == target)
                        announced = true;
                }
                if (!announced)
                {
                    session->SendWatching(0);
                    session->watchTarget.store(0);
                }
            }

            if (refresh || !list.empty())
                session->SendState(static_cast<uint32_t>(std::max<int32>(0, entry.view.mapId)), list);
        }
    }
}

class AzerothPlexWorldScript : public WorldScript
{
public:
    AzerothPlexWorldScript() : WorldScript("AzerothPlexWorldScript") { }

    void OnAfterConfigLoad(bool /*reload*/) override
    {
        AzerothPlex::Settings settings;
        settings.enabled = sConfigMgr->GetOption<bool>("AzerothPlex.Enable", true);
        settings.port = sConfigMgr->GetOption<uint16>("AzerothPlex.Port", 8086);
        settings.bindAddress = sConfigMgr->GetOption<std::string>("AzerothPlex.BindAddress", "0.0.0.0");
        settings.requireMatchingAddress =
            sConfigMgr->GetOption<bool>("AzerothPlex.RequireMatchingAddress", true);
        settings.rangeYards =
            sConfigMgr->GetOption<float>("AzerothPlex.RangeYards", 80.0f);
        settings.maxBroadcastersPerMap =
            sConfigMgr->GetOption<uint16>("AzerothPlex.MaxBroadcastersPerMap", 8);
        settings.maxViewersPerBroadcast =
            sConfigMgr->GetOption<uint16>("AzerothPlex.MaxViewersPerBroadcast", 16);
        settings.bitrate = sConfigMgr->GetOption<uint32>("AzerothPlex.VideoBitrate", 800000);
        settings.fps = sConfigMgr->GetOption<uint16>("AzerothPlex.VideoFps", 24);
        settings.width = sConfigMgr->GetOption<uint16>("AzerothPlex.VideoWidth", 640);
        settings.height = sConfigMgr->GetOption<uint16>("AzerothPlex.VideoHeight", 360);
        settings.minimumClientVersion =
            sConfigMgr->GetOption<uint32>("AzerothPlex.RequireClientVersion", 1);
        settings.logLevel = sConfigMgr->GetOption<uint16>("AzerothPlex.LogLevel", 1);
        AzerothPlex::AzerothPlexServer::Instance().ApplySettings(settings);
    }

    void OnStartup() override
    {
        AzerothPlex::AzerothPlexServer::Instance().Start();
    }

    void OnUpdate(uint32 diff) override
    {
        AzerothPlex::AzerothPlexServer::Instance().Tick(diff);
    }

    void OnShutdown() override
    {
        AzerothPlex::AzerothPlexServer::Instance().Stop();
    }
};

void AddSC_mod_azeroth_plex()
{
    new AzerothPlexWorldScript();
}
