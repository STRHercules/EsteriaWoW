/* What every casino game shares: settings, the house account, the gold ledger, escrowed rounds, messaging, and the
 * entry points each game file exposes to the script hooks in EsteriaCasino.cpp.
 *
 * Every function here runs on the world thread (addon packets, gossip, logout and world updates all do), so the
 * state needs no lock. Gold moves follow one rule: change the character's money, append the receipt rows, save the
 * money, all inside one CharacterDatabaseTransaction the caller commits.
 */
#ifndef ESTERIA_CASINO_COMMON_H
#define ESTERIA_CASINO_COMMON_H

#include "CasinoHouse.h"
#include "DatabaseEnvFwd.h"
#include "Define.h"
#include "ObjectGuid.h"

#include <string>
#include <string_view>

class Creature;
class WorldObject;
class Player;

namespace EsteriaCasino::Server
{
    struct Settings
    {
        bool enabled = false;
        uint64 dailyCap = 100000000;
        float maxDistance = 12.0f;
        uint32 lotteryShareBp = 1000; // of the house's positive results, fed to the lottery pool
    };

    extern Settings settings;
    extern House house;
    extern bool houseLoaded;

    enum RoundState : uint8
    {
        ROUND_OPEN = 0,
        ROUND_SETTLED = 1,
        ROUND_REFUNDED = 2,
    };

    struct Allowance
    {
        uint32 day = 0;
        uint64 wagered = 0;
        uint32 excludedUntil = 0;
    };

    bool Open(); // enabled and the house loaded
    uint64 NextRoundId();
    uint32 Now();
    uint32 SecureBelow(uint32 n); // CSPRNG, uniform in [0, n)
    std::string GoldText(uint64 copper);

    Allowance& AllowanceFor(uint32 account);
    void SaveAllowance(CharacterDatabaseTransaction trans, uint32 account, Allowance const& allowance);
    void AppendLedger(CharacterDatabaseTransaction trans, uint64 round, ObjectGuid::LowType guid, int64 playerDelta,
        int64 houseDelta, char const* reason);

    void Send(Player* player, std::string const& body);
    void SendTo(ObjectGuid guid, std::string const& body); // only if online
    void Refuse(Player* player, char const* code);
    bool Near(Player* player, ObjectGuid npc);

    // Refusal code for staking `stake` now (exclusion, daily cap, gold, a failed save), or nullptr.
    char const* StakeRefusal(Player* player, uint64 stake);
    // Takes `stake` from the player into a new open round (money, round row, ledger, daily total, saved money).
    void TakeStake(Player* player, CharacterDatabaseTransaction trans, uint64 round, char const* game,
        uint32 dealerEntry, uint64 stake, std::string const& note);
    // Pays copper to a character: into their bags when online and it fits, otherwise by mail. True when mailed.
    bool Pay(ObjectGuid guid, CharacterDatabaseTransaction trans, uint64 copper, std::string const& body);
    void CloseRound(CharacterDatabaseTransaction trans, uint64 round, uint64 paid, std::string const& result);
    // Books the house's net result of a round (already applied to house.bankroll by House::Settle): updates the
    // bankroll row and moves the lottery's share of a positive result into the pool.
    void BookHouse(CharacterDatabaseTransaction trans, int64 delta, uint64 round);

    // Chess and checkers (CasinoBoardGames.cpp).
    void LoadBoardConfig();
    void OpenBoardLobby(Player* player, WorldObject* npc);
    bool HandleBoardMessage(Player* player, std::string_view command, std::string_view args);
    void BoardLogin(Player* player);
    void BoardLogout(Player* player);
    void BoardUpdate(uint32 diff);

    // Texas Hold'em (CasinoPoker.cpp).
    void LoadPokerConfig();
    void OpenPoker(Player* player, WorldObject* npc);
    bool HandlePokerMessage(Player* player, std::string_view command, std::string_view args);
    void PokerLogout(Player* player);
    void PokerUpdate(uint32 diff);
    bool PokerSeated(ObjectGuid guid);

    // The lottery (CasinoLottery.cpp).
    void LoadLotteryConfig();
    void LoadLottery();
    void OpenLottery(Player* player, Creature* npc);
    bool HandleLotteryMessage(Player* player, std::string_view command, std::string_view args);
    void LotteryUpdate();
    bool LotteryLoaded();
    void AddToLottery(CharacterDatabaseTransaction trans, uint64 copper);
    uint64 LotteryPool();
}

#endif
