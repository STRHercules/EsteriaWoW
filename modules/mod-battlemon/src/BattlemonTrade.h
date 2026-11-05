#ifndef BATTLEMON_TRADE_H
#define BATTLEMON_TRADE_H

#include "Define.h"
#include "ObjectGuid.h"

#include <memory>
#include <mutex>
#include <string>
#include <unordered_map>

class Player;

// Pokemon-for-Pokemon trading between two online players, in range or remotely. The server owns the whole
// exchange: invite, accept, each side's offer, a confirmation from both, then one all-or-nothing database update.
// Changing an offer cancels both confirmations, so nobody can swap what was agreed after the fact.
// Requests (addon -> server): TRADE <INVITE name | ACCEPT | DECLINE | CANCEL | OFFER ownedId | CONFIRM | STATE>.
class BattlemonTrade
{
public:
    static BattlemonTrade* instance();

    void LoadConfig();
    void Handle(Player* player, std::string const& arg);
    void OnLogout(Player* player);
    // Drops invitations and trades nobody is answering; called every few seconds.
    void Expire();

private:
    struct Session
    {
        ObjectGuid side[2];       // [0] invited [1]
        bool accepted = false;
        uint32 offer[2] = {0, 0}; // battlemon_owned.id each side puts up, 0 = nothing
        bool confirmed[2] = {false, false};
        bool committing = false;  // set once both have confirmed, so a repeated click cannot start a second commit
        uint32 touched = 0;       // unix seconds of the last change
    };

    BattlemonTrade() = default;

    std::shared_ptr<Session> Find(ObjectGuid guid);
    bool InRange(Player* a, Player* b) const;
    void Send(Session const& s);
    void Close(std::shared_ptr<Session> const& s, std::string const& why);
    void Commit(std::shared_ptr<Session> const& s, Player* a, Player* b);

    bool _enabled = true;
    bool _remote = true;
    float _distance = 40.0f;

    std::mutex _lock;
    std::unordered_map<ObjectGuid, std::shared_ptr<Session>> _sessions; // both sides point at the same Session
};

#define sBattlemonTrade BattlemonTrade::instance()

#endif
