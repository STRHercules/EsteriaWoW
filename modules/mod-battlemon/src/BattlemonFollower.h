#ifndef BATTLEMON_FOLLOWER_H
#define BATTLEMON_FOLLOWER_H

#include "Define.h"
#include "ObjectGuid.h"

#include <mutex>
#include <string>
#include <unordered_map>

class Player;

// A chosen Pokemon walks behind its trainer. It is a cosmetic summoned creature (the Pokemon's own overworld
// creature template, owned by the player, passive and untargetable); the Pokemon itself is untouched.
// It hides while mounted, on a taxi, in a battleground, in a Battlemon battle or duel, and on map changes,
// and comes back by itself afterwards. The choice is stored in battlemon_follower.
class BattlemonFollower
{
public:
    static BattlemonFollower* instance();

    void LoadConfig();

    // ownedId 0 = stop following. Returns false (and tells the player) when the Pokemon cannot follow.
    bool Choose(Player* player, uint32 ownedId);
    // The chosen battlemon_owned.id, 0 when none.
    uint32 Chosen(Player* player);

    void OnLogin(Player* player);
    void OnLogout(Player* player);
    void Despawn(Player* player);
    // Called from PlayerScript::OnPlayerUpdate; does real work about once a second.
    void Tick(Player* player, uint32 diff);

private:
    struct State
    {
        uint32 ownedId = 0;
        ObjectGuid actor;
        uint32 timerMs = 0;
        uint32 summonCooldownMs = 0;
    };

    BattlemonFollower() = default;

    bool ShouldShow(Player* player) const;
    ObjectGuid Summon(Player* player, uint32 ownedId);
    void DespawnActor(Player* player, ObjectGuid actor);

    bool _enabled = true;
    float _distance = 2.0f;

    std::mutex _lock;
    std::unordered_map<ObjectGuid, State> _states;
};

#define sBattlemonFollower BattlemonFollower::instance()

#endif
