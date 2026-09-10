#ifndef BATTLEMON_SIDECAR_SERVER_H
#define BATTLEMON_SIDECAR_SERVER_H

#include "Define.h"

#include <atomic>
#include <memory>
#include <mutex>
#include <optional>
#include <queue>
#include <string>
#include <unordered_map>
#include <vector>

class BattlemonMgr;

struct BattlemonSidecarInbound
{
    uint32 connId = 0;
    uint32 guid = 0;
    std::string line;
};

struct BattlemonSidecarOutbound
{
    uint32 connId = 0;
    std::vector<std::string> lines;
    bool close = false;
};

class BattlemonSidecarServer
{
public:
    static BattlemonSidecarServer* instance();

    void LoadConfig();
    void Start();
    void Stop();
    void Update();

    bool IsEnabled() const { return _enabled; }
    uint16 GetPort() const { return _port; }

    bool HasLease(uint32 guid) const;
    void RevokeLease(uint32 guid);

    // Pairing + long-lived tokens (hashed at rest).
    std::string CreatePairCode(uint32 guid);
    std::optional<std::string> ExchangePairCode(std::string const& characterName, std::string const& code,
                                                std::string* errMsg = nullptr);
    std::optional<uint32> AuthenticateToken(std::string const& token);
    void RevokeTokensForGuid(uint32 guid);

    void QueueInbound(BattlemonSidecarInbound cmd);
    bool PopOutbound(BattlemonSidecarOutbound& out);

private:
    BattlemonSidecarServer() = default;

    void ProcessInbound(BattlemonSidecarInbound const& cmd);
    void SendLines(uint32 connId, std::vector<std::string> lines, bool close = false);
    void EnsureTokenTable();

    bool _enabled = false;
    std::string _bind = "0.0.0.0";
    uint16 _port = 8787;
    uint32 _pairTtl = 300;
    uint32 _maxCmdPerSec = 20;

    mutable std::mutex _leaseLock;
    std::unordered_map<uint32, uint32> _guidToConn;

    mutable std::mutex _queueLock;
    std::queue<BattlemonSidecarInbound> _inbound;
    std::queue<BattlemonSidecarOutbound> _outbound;

    struct Impl;
    std::unique_ptr<Impl> _impl;
    std::atomic<uint32> _activeHandlers{ 0 };
};

#define sBattlemonSidecar BattlemonSidecarServer::instance()

#endif
