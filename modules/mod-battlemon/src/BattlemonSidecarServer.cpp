#include "BattlemonSidecarServer.h"
#include "BattlemonMgr.h"
#include "BattlemonSession.h"

#include "Config.h"
#include "CryptoHash.h"
#include "DatabaseEnv.h"
#include "IoContext.h"
#include "Log.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "Random.h"
#include "GameTime.h"
#include "Util.h"

#include <boost/asio.hpp>
#include <boost/thread/thread.hpp>

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cctype>
#include <iomanip>
#include <memory>
#include <sstream>
#include <thread>
#include <unordered_map>

namespace
{
    std::string Sha256Hex(std::string const& input)
    {
        auto digest = Acore::Crypto::SHA256::GetDigestOf(input);
        std::ostringstream ss;
        ss << std::hex;
        for (uint8 b : digest)
            ss << std::setw(2) << std::setfill('0') << static_cast<int>(b);
        return ss.str();
    }

    std::string RandomToken()
    {
        static char const* kHex = "0123456789abcdef";
        std::string out;
        out.reserve(64);
        for (int i = 0; i < 32; ++i)
            out.push_back(kHex[urand(0, 15)]);
        return out;
    }

    std::string RandomPairCode()
    {
        static char const* kChars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
        std::string out;
        out.reserve(8);
        for (int i = 0; i < 8; ++i)
            out.push_back(kChars[urand(0, 31)]);
        return out;
    }

    std::string Trim(std::string s)
    {
        if (s.size() >= 3
            && static_cast<unsigned char>(s[0]) == 0xEF
            && static_cast<unsigned char>(s[1]) == 0xBB
            && static_cast<unsigned char>(s[2]) == 0xBF)
            s.erase(0, 3);
        while (!s.empty() && (s.back() == '\r' || s.back() == '\n' || s.back() == ' '))
            s.pop_back();
        size_t start = 0;
        while (start < s.size() && s[start] == ' ')
            ++start;
        return s.substr(start);
    }

    std::vector<std::string> SplitWs(std::string const& line)
    {
        std::vector<std::string> out;
        std::istringstream ss(line);
        std::string part;
        while (ss >> part)
            out.push_back(part);
        return out;
    }

    struct PairEntry
    {
        uint32 guid = 0;
        uint32 expiresAt = 0;
    };
}

struct BattlemonSidecarServer::Impl
{
    std::atomic<bool> running{ false };
    std::unique_ptr<boost::thread> thread;
    std::unique_ptr<Acore::Asio::IoContext> io;
    std::unique_ptr<boost::asio::ip::tcp::acceptor> acceptor;
    std::mutex pairLock;
    std::unordered_map<std::string, PairEntry> pairCodes;

    struct ConnState
    {
        uint32 connId = 0;
        uint32 guid = 0;
        bool authed = false;
        uint32 windowStart = 0;
        uint32 cmdCount = 0;
    };

    std::mutex connLock;
    std::unordered_map<uint32, ConnState> conns;
    std::mutex socketLock;
    std::unordered_map<uint32, std::shared_ptr<boost::asio::ip::tcp::socket>> sockets;
    uint32 nextConnId = 1;
};

BattlemonSidecarServer* BattlemonSidecarServer::instance()
{
    static BattlemonSidecarServer inst;
    return &inst;
}

void BattlemonSidecarServer::LoadConfig()
{
    _enabled = sConfigMgr->GetOption<bool>("Battlemon.Sidecar.Enable", false);
    _bind = sConfigMgr->GetOption<std::string>("Battlemon.Sidecar.Bind", "0.0.0.0");
    _port = static_cast<uint16>(sConfigMgr->GetOption<uint32>("Battlemon.Sidecar.Port", 8787));
    _pairTtl = sConfigMgr->GetOption<uint32>("Battlemon.Sidecar.PairTtlSeconds", 300);
    _maxCmdPerSec = sConfigMgr->GetOption<uint32>("Battlemon.Sidecar.MaxCommandsPerSecond", 20);
}

void BattlemonSidecarServer::EnsureTokenTable()
{
    // AC aborts the whole process on ER_NO_SUCH_TABLE (1146). Create this
    // before any pair-code exchange so a missed dbimport cannot take the realm down.
    CharacterDatabase.DirectExecute(
        "CREATE TABLE IF NOT EXISTS `battlemon_sidecar_token` ("
        "`id` int unsigned NOT NULL AUTO_INCREMENT,"
        "`guid` int unsigned NOT NULL,"
        "`token_hash` char(64) NOT NULL,"
        "`created_at` int unsigned NOT NULL DEFAULT 0,"
        "`expires_at` int unsigned NOT NULL DEFAULT 0,"
        "`revoked` tinyint unsigned NOT NULL DEFAULT 0,"
        "PRIMARY KEY (`id`),"
        "UNIQUE KEY `token_hash` (`token_hash`),"
        "KEY `guid` (`guid`)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");
}

void BattlemonSidecarServer::Start()
{
    LoadConfig();
    if (!_enabled || _impl)
        return;

    EnsureTokenTable();

    _impl = std::make_unique<Impl>();
    _impl->running = true;
    _impl->thread = std::make_unique<boost::thread>([this]() {
        try
        {
            using boost::asio::ip::tcp;
            _impl->io = std::make_unique<Acore::Asio::IoContext>();
            _impl->acceptor = std::make_unique<tcp::acceptor>(
                *_impl->io, tcp::endpoint(boost::asio::ip::make_address(_bind), _port));
            _impl->acceptor->non_blocking(true);
            LOG_INFO("module", "Battlemon sidecar listening on {}:{}", _bind, _port);

            while (_impl && _impl->running)
            {
                tcp::socket socket(*_impl->io);
                boost::system::error_code ec;
                _impl->acceptor->accept(socket, ec);
                if (!_impl || !_impl->running)
                    break;
                if (ec)
                {
                    if (ec == boost::asio::error::would_block || ec == boost::asio::error::try_again)
                    {
                        std::this_thread::sleep_for(std::chrono::milliseconds(50));
                        continue;
                    }
                    break;
                }
                auto sock = std::make_shared<boost::asio::ip::tcp::socket>(std::move(socket));
                uint32 connId = 0;
                {
                    std::lock_guard<std::mutex> g(_impl->connLock);
                    connId = _impl->nextConnId++;
                    _impl->conns[connId] = Impl::ConnState{ connId, 0, false, 0, 0 };
                }
                {
                    std::lock_guard<std::mutex> g(_impl->socketLock);
                    _impl->sockets[connId] = sock;
                }

                boost::thread([this, sock, connId]() {
                    struct HandlerGuard
                    {
                        std::atomic<uint32>& count;
                        ~HandlerGuard() { --count; }
                    };
                    ++_activeHandlers;
                    HandlerGuard handlerGuard{ _activeHandlers };

                    std::string buffer;
                    char data[1024];
                    while (_impl && _impl->running)
                    {
                        boost::system::error_code ec;
                        size_t n = sock->read_some(boost::asio::buffer(data), ec);
                        if (ec == boost::asio::error::eof || n == 0)
                            break;
                        if (ec)
                            break;
                        buffer.append(data, data + n);
                        for (;;)
                        {
                            auto pos = buffer.find('\n');
                            if (pos == std::string::npos)
                                break;
                            std::string line = Trim(buffer.substr(0, pos));
                            buffer.erase(0, pos + 1);
                            if (line.empty())
                                continue;

                            if (line.rfind("AUTH ", 0) == 0)
                            {
                                std::string token = Trim(line.substr(5));
                                auto guid = AuthenticateToken(token);
                                if (!guid)
                                {
                                    SendLines(connId, { "ERR\tbad token" }, true);
                                    break;
                                }
                                {
                                    std::lock_guard<std::mutex> lg(_leaseLock);
                                    _guidToConn[*guid] = connId;
                                }
                                {
                                    std::lock_guard<std::mutex> g(_impl->connLock);
                                    auto it = _impl->conns.find(connId);
                                    if (it != _impl->conns.end())
                                    {
                                        it->second.authed = true;
                                        it->second.guid = *guid;
                                    }
                                }
                                SendLines(connId, { "OK\tauth" });
                                continue;
                            }

                            if (line.rfind("PAIR ", 0) == 0)
                            {
                                auto parts = SplitWs(line);
                                if (parts.size() < 3)
                                {
                                    SendLines(connId, { "ERR\tusage PAIR name code" }, true);
                                    break;
                                }
                                std::string err;
                                auto token = ExchangePairCode(parts[1], parts[2], &err);
                                if (!token)
                                {
                                    SendLines(connId, { "ERR\t" + (err.empty() ? "bad pair" : err) });
                                    continue;
                                }
                                SendLines(connId, { "TOKEN\t" + *token }, true);
                                continue;
                            }

                            uint32 guid = 0;
                            bool authed = false;
                            {
                                std::lock_guard<std::mutex> g(_impl->connLock);
                                auto it = _impl->conns.find(connId);
                                if (it != _impl->conns.end() && it->second.authed)
                                {
                                    authed = true;
                                    guid = it->second.guid;
                                }
                            }
                            if (!authed)
                            {
                                SendLines(connId, { "ERR\tauth first" }, true);
                                break;
                            }

                            uint32 now = GameTime::GetGameTime().count();
                            {
                                std::lock_guard<std::mutex> g(_impl->connLock);
                                auto it = _impl->conns.find(connId);
                                if (it != _impl->conns.end())
                                {
                                    if (now != it->second.windowStart)
                                    {
                                        it->second.windowStart = now;
                                        it->second.cmdCount = 0;
                                    }
                                    ++it->second.cmdCount;
                                    if (_maxCmdPerSec && it->second.cmdCount > _maxCmdPerSec)
                                    {
                                        SendLines(connId, { "ERR\trate limited" }, true);
                                        return;
                                    }
                                }
                            }

                            if (line.rfind("BM\t", 0) != 0)
                            {
                                SendLines(connId, { "ERR\texpected BM\\t command" });
                                continue;
                            }

                            QueueInbound({ connId, guid, line });
                        }
                    }
                    uint32 leaseGuid = 0;
                    {
                        std::lock_guard<std::mutex> g(_impl->connLock);
                        auto it = _impl->conns.find(connId);
                        if (it != _impl->conns.end())
                            leaseGuid = it->second.guid;
                        _impl->conns.erase(connId);
                    }
                    if (leaseGuid)
                        RevokeLease(leaseGuid);
                    {
                        std::lock_guard<std::mutex> g(_impl->socketLock);
                        _impl->sockets.erase(connId);
                    }
                    boost::system::error_code ig;
                    sock->close(ig);
                }).detach();
            }
        }
        catch (std::exception const& e)
        {
            LOG_ERROR("module", "Battlemon sidecar failed: {}", e.what());
        }
    });
}

void BattlemonSidecarServer::Stop()
{
    if (!_impl)
        return;

    _impl->running = false;

    if (_impl->acceptor)
    {
        boost::system::error_code ec;
        _impl->acceptor->cancel(ec);
        _impl->acceptor->close(ec);
    }

    {
        std::lock_guard<std::mutex> g(_impl->socketLock);
        for (auto& pair : _impl->sockets)
        {
            boost::system::error_code ec;
            pair.second->shutdown(boost::asio::ip::tcp::socket::shutdown_both, ec);
            pair.second->close(ec);
        }
        _impl->sockets.clear();
    }

    {
        std::lock_guard<std::mutex> lg(_leaseLock);
        _guidToConn.clear();
    }

    for (int i = 0; i < 200 && _activeHandlers.load() > 0; ++i)
        std::this_thread::sleep_for(std::chrono::milliseconds(25));

    if (_activeHandlers.load() > 0)
        LOG_WARN("module", "Battlemon sidecar stopped with {} active client thread(s)", _activeHandlers.load());

    if (_impl->thread && _impl->thread->joinable())
        _impl->thread->join();

    _impl.reset();
}

void BattlemonSidecarServer::Update()
{
    if (!_enabled)
        return;

    constexpr uint32 kMaxPerTick = 32;
    for (uint32 i = 0; i < kMaxPerTick; ++i)
    {
        BattlemonSidecarInbound cmd;
        {
            std::lock_guard<std::mutex> g(_queueLock);
            if (_inbound.empty())
                break;
            cmd = std::move(_inbound.front());
            _inbound.pop();
        }
        ProcessInbound(cmd);
    }
}

bool BattlemonSidecarServer::HasLease(uint32 guid) const
{
    std::lock_guard<std::mutex> g(_leaseLock);
    return _guidToConn.find(guid) != _guidToConn.end();
}

void BattlemonSidecarServer::RevokeLease(uint32 guid)
{
    std::lock_guard<std::mutex> g(_leaseLock);
    if (guid)
        _guidToConn.erase(guid);
}

void BattlemonSidecarServer::QueueInbound(BattlemonSidecarInbound cmd)
{
    std::lock_guard<std::mutex> g(_queueLock);
    _inbound.push(std::move(cmd));
}

bool BattlemonSidecarServer::PopOutbound(BattlemonSidecarOutbound& out)
{
    std::lock_guard<std::mutex> g(_queueLock);
    if (_outbound.empty())
        return false;
    out = std::move(_outbound.front());
    _outbound.pop();
    return true;
}

void BattlemonSidecarServer::SendLines(uint32 connId, std::vector<std::string> lines, bool close)
{
    if (!_impl)
        return;

    std::shared_ptr<boost::asio::ip::tcp::socket> sock;
    {
        std::lock_guard<std::mutex> g(_impl->socketLock);
        auto it = _impl->sockets.find(connId);
        if (it == _impl->sockets.end())
            return;
        sock = it->second;
    }

    for (std::string const& line : lines)
    {
        std::string out = line;
        out.push_back('\n');
        boost::system::error_code ec;
        boost::asio::write(*sock, boost::asio::buffer(out), ec);
        if (ec)
            return;
    }
    if (close)
    {
        boost::system::error_code ec;
        sock->close(ec);
    }
}

void BattlemonSidecarServer::ProcessInbound(BattlemonSidecarInbound const& cmd)
{
    if (!sBattlemonMgr->IsEnabled())
    {
        SendLines(cmd.connId, { "ERR\tdisabled" });
        return;
    }

    BattlemonSession session;
    session.guid = cmd.guid;
    session.playerGuid = ObjectGuid::Create<HighGuid::Player>(cmd.guid);
    session.player = ObjectAccessor::FindConnectedPlayer(session.playerGuid);

    sBattlemonMgr->HandleCommand(session, cmd.line);
    SendLines(cmd.connId, session.outbox);
}

std::string BattlemonSidecarServer::CreatePairCode(uint32 guid)
{
    if (!_impl)
        return {};

    std::string code = RandomPairCode();
    PairEntry entry;
    entry.guid = guid;
    entry.expiresAt = GameTime::GetGameTime().count() + _pairTtl;

    std::lock_guard<std::mutex> g(_impl->pairLock);
    _impl->pairCodes[code] = entry;
    return code;
}

std::optional<std::string> BattlemonSidecarServer::ExchangePairCode(
    std::string const& characterName, std::string const& code, std::string* errMsg)
{
    auto fail = [&](std::string msg) -> std::optional<std::string>
    {
        if (errMsg)
            *errMsg = std::move(msg);
        return std::nullopt;
    };

    if (!_impl)
        return fail("sidecar unavailable");

    std::string codeKey = code;
    for (char& c : codeKey)
        c = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));

    PairEntry entry;
    {
        std::lock_guard<std::mutex> g(_impl->pairLock);
        auto it = _impl->pairCodes.find(codeKey);
        if (it == _impl->pairCodes.end())
            return fail("code not found (expired, already used, or worldserver restarted)");
        entry = it->second;
    }

    if (entry.expiresAt < GameTime::GetGameTime().count())
        return fail("code expired — run .battlemon link again");

    std::string escapedName = Trim(characterName);
    CharacterDatabase.EscapeString(escapedName);
    QueryResult result = CharacterDatabase.Query(
        "SELECT guid FROM characters WHERE LOWER(name) = LOWER('{}')", escapedName);
    if (!result)
        return fail("character not found — check exact toon name spelling");

    uint32 guid = result->Fetch()[0].Get<uint32>();
    if (guid != entry.guid)
        return fail("code was issued for a different character");

    std::string token = RandomToken();
    std::string hash = Sha256Hex(token);
    uint32 now = GameTime::GetGameTime().count();
    CharacterDatabase.Execute(
        "INSERT INTO battlemon_sidecar_token (guid, token_hash, created_at, expires_at, revoked) "
        "VALUES ({}, '{}', {}, 0, 0)",
        guid, hash, now);

    {
        std::lock_guard<std::mutex> g(_impl->pairLock);
        _impl->pairCodes.erase(codeKey);
    }

    return token;
}

std::optional<uint32> BattlemonSidecarServer::AuthenticateToken(std::string const& token)
{
    if (token.empty())
        return std::nullopt;
    std::string hash = Sha256Hex(token);
    QueryResult result = CharacterDatabase.Query(
        "SELECT guid FROM battlemon_sidecar_token WHERE token_hash = '{}' AND revoked = 0 "
        "AND (expires_at = 0 OR expires_at > {}) LIMIT 1",
        hash, GameTime::GetGameTime().count());
    if (!result)
        return std::nullopt;
    return result->Fetch()[0].Get<uint32>();
}

void BattlemonSidecarServer::RevokeTokensForGuid(uint32 guid)
{
    CharacterDatabase.Execute(
        "UPDATE battlemon_sidecar_token SET revoked = 1 WHERE guid = {}", guid);
}
