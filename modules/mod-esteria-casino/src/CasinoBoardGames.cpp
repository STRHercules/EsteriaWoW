/*
 * Chess and checkers between players, for a gold stake or for free, at the Grandmaster NPC.
 *
 * A player posts a challenge (game, stake, minutes per side); another player near a Grandmaster accepts it. Both
 * stakes leave the characters in one commit before the first move, and settle in one commit at the end: the winner
 * takes both minus the house cut on the winnings, a draw returns both stakes with no cut. Rules and clocks are run
 * here (Chess.h, Checkers.h); the client only proposes moves from the list the server sends. A player who logs out
 * has a grace period to come back before forfeiting; the clock keeps running. A server restart refunds both stakes
 * (the startup sweep in EsteriaCasino.cpp).
 *
 * The house opponent (Chess.h / Checkers.h Ai) plays free practice games only: it can be beaten, so it never takes
 * a stake. Its search runs on a worker thread with a time limit and the move is applied on the world thread.
 *
 * client -> server
 *   GL                          lobby again
 *   GC:<c|k>:<stake>:<minutes>  post a challenge (c chess, k checkers)
 *   GX                          withdraw my challenge
 *   GA:<challenge>              accept a challenge
 *   GM:<move>                   chess "e2e4"/"e7e8q", checkers "40-31" or "35-21-7"
 *   GR | GD | GN                resign, offer (or accept) a draw, decline a draw
 *   GW:<match> | GQ             watch a match, stop watching
 *   GH:<c|k>:<level>:<minutes>  play the house (level 1 easy, 2 normal, 3 hard); always free, never staked
 *
 * server -> client
 *   O:board:<maxStake>:<cutBp>:<defaultMinutes>
 *   GL:<id>:<c|k>:<host>:<stake>:<minutes>:<mine> ... GLE      open challenges
 *   GG:<id>:<c|k>:<side0>:<side1>:<stake> ... GGE              matches to watch
 *   GS:<match>:<c|k>:<side0>:<side1>:<stake>:<you>             a match opens; you 0/1, or -1 watching
 *   GB:<match>:<board64>:<toMove>:<last>:<clock0>:<clock1>:<status>
 *       chess board "PNBRQKpnbrqk."; checkers "wWbB."; side 0 moves first (white in chess, black in checkers);
 *       clocks in seconds; status words joined by ',': check, offer0/offer1 (draw offered), away0/away1
 *   GV:<move>,<move>,... ... GVE                               your legal moves, when it is your turn
 *   GE:<match>:<winner 0|1|2 draw>:<reason>:<paidToYou>
 */
#include "CasinoCommon.h"
#include "Checkers.h"
#include "Chess.h"

#include "Chat.h"
#include "Config.h"
#include "Creature.h"
#include "CreatureScript.h"
#include "DatabaseEnv.h"
#include "Log.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "ScriptedGossip.h"
#include "StringConvert.h"
#include "StringFormat.h"
#include "Tokenize.h"
#include "WorldSession.h"

#include <algorithm>
#include <array>
#include <future>
#include <random>
#include <limits>
#include <map>
#include <set>
#include <unordered_map>

using namespace EsteriaCasino;
using namespace EsteriaCasino::Server;

namespace
{
    enum class Kind : uint8
    {
        Chess,
        Checkers,
    };

    enum GossipAction : uint32
    {
        GOSSIP_ACTION_LOBBY = 1,
    };

    char Letter(Kind kind) { return kind == Kind::Chess ? 'c' : 'k'; }
    char const* Name(Kind kind) { return kind == Kind::Chess ? "chess" : "checkers"; }

    struct BoardConfig
    {
        uint64 maxStake = 100000000; // 10,000 gold
        uint32 cutBp = 500;          // 5% of the winnings
        uint32 minutes = 10;
        uint32 graceSeconds = 60;
    } boardConfig;

    struct Challenge
    {
        uint64 id;
        Kind kind;
        ObjectGuid host;
        std::string hostName;
        uint64 stake;
        uint32 minutes;
        ObjectGuid npc;
        uint32 npcEntry;
    };

    struct Match
    {
        uint64 id = 0;
        Kind kind = Kind::Chess;
        uint32 npcEntry = 0;
        std::array<ObjectGuid, 2> players;
        std::array<std::string, 2> names;
        uint64 stake = 0;
        std::array<uint64, 2> rounds {}; // escrow rounds, 0 for a free game
        Chess::Game chess;
        Checkers::Game checkers;
        std::string last;
        std::array<int64, 2> clockMs {};
        std::array<uint32, 2> awayUntil {}; // disconnect deadline, 0 while present
        std::set<ObjectGuid> watchers;
        int drawOffer = -1;
        int houseSide = -1; // the side the house plays, or -1 between players
        int level = 0;
        int64 houseDelayMs = 0;
        std::future<std::string> thinking; // the house's move being searched

        int ToMove() const
        {
            return kind == Kind::Chess ? (chess.Pos().whiteToMove ? 0 : 1) : (checkers.whiteToMove ? 1 : 0);
        }

        int SideOf(ObjectGuid guid) const
        {
            return players[0] == guid ? 0 : players[1] == guid ? 1 : -1;
        }
    };

    uint64 nextId = 1;
    std::map<uint64, Challenge> challenges;
    std::map<uint64, Match> matches;
    std::unordered_map<ObjectGuid, uint64> playing;
    std::unordered_map<ObjectGuid, uint64> watching;
    std::unordered_map<ObjectGuid, ObjectGuid> lobbyNpc; // players with the lobby open, and where
    // Searches still running for matches that already ended; dropped once they finish, so a resignation never waits.
    std::vector<std::future<std::string>> orphans;

    char const* LevelName(int level) { return level == 1 ? "Easy" : level == 3 ? "Hard" : "Normal"; }

    std::string BoardText(Match const& m)
    {
        return m.kind == Kind::Chess ? m.chess.Pos().BoardText() : m.checkers.BoardText();
    }

    std::vector<std::string> LegalMoves(Match const& m)
    {
        std::vector<std::string> out;
        if (m.kind == Kind::Chess)
            for (Chess::Move const& move : m.chess.Pos().Legal())
                out.push_back(Chess::ToText(move));
        else
            for (Checkers::Path const& path : m.checkers.Legal())
                out.push_back(Checkers::ToText(path));
        return out;
    }

    uint32 Seconds(int64 ms) { return ms <= 0 ? 0 : uint32((ms + 999) / 1000); }

    void SendBoard(Player* to, Match const& m, int side)
    {
        std::string status;
        auto add = [&status](std::string const& word) { status += (status.empty() ? "" : ",") + word; };
        if (m.kind == Kind::Chess && m.chess.Pos().InCheck(m.chess.Pos().whiteToMove))
            add("check");
        if (m.drawOffer >= 0)
            add(Acore::StringFormat("offer{}", m.drawOffer));
        for (int i = 0; i < 2; ++i)
            if (m.awayUntil[i])
                add(Acore::StringFormat("away{}", i));
        Send(to, Acore::StringFormat("GB:{}:{}:{}:{}:{}:{}:{}", m.id, BoardText(m), m.ToMove(), m.last,
            Seconds(m.clockMs[0]), Seconds(m.clockMs[1]), status));
        if (side != m.ToMove())
            return;
        // Addon messages stop at 255 bytes, so the move list goes in chunks.
        std::string chunk;
        for (std::string const& move : LegalMoves(m))
        {
            if (chunk.size() + move.size() + 1 > 200)
            {
                Send(to, "GV:" + chunk);
                chunk.clear();
            }
            chunk += (chunk.empty() ? "" : ",") + move;
        }
        if (!chunk.empty())
            Send(to, "GV:" + chunk);
        Send(to, "GVE");
    }

    void SendState(Player* to, Match const& m, int side)
    {
        Send(to, Acore::StringFormat("GS:{}:{}:{}:{}:{}:{}", m.id, Letter(m.kind), m.names[0], m.names[1], m.stake,
            side));
        SendBoard(to, m, side);
    }

    void Broadcast(Match const& m)
    {
        for (int i = 0; i < 2; ++i)
            if (Player* player = ObjectAccessor::FindConnectedPlayer(m.players[i]))
                SendBoard(player, m, i);
        for (ObjectGuid const& watcher : m.watchers)
            if (Player* player = ObjectAccessor::FindConnectedPlayer(watcher))
                SendBoard(player, m, -1);
    }

    void SendOpen(Player* player)
    {
        Send(player, Acore::StringFormat("O:board:{}:{}:{}", boardConfig.maxStake, boardConfig.cutBp,
            boardConfig.minutes));
    }

    void SendLobby(Player* player)
    {
        for (auto const& [id, c] : challenges)
            Send(player, Acore::StringFormat("GL:{}:{}:{}:{}:{}:{}", id, Letter(c.kind), c.hostName, c.stake,
                c.minutes, c.host == player->GetGUID() ? 1 : 0));
        Send(player, "GLE");
        for (auto const& [id, m] : matches)
            Send(player, Acore::StringFormat("GG:{}:{}:{}:{}:{}", id, Letter(m.kind), m.names[0], m.names[1], m.stake));
        Send(player, "GGE");
    }

    // Everyone browsing the lobby sees challenges and matches come and go.
    void RefreshLobbies()
    {
        for (auto const& [guid, npc] : lobbyNpc)
            if (!playing.contains(guid) && !watching.contains(guid))
                if (Player* player = ObjectAccessor::FindConnectedPlayer(guid))
                    SendLobby(player);
    }

    void CancelChallenges(ObjectGuid host)
    {
        bool changed = false;
        for (auto it = challenges.begin(); it != challenges.end();)
        {
            if (it->second.host == host)
            {
                it = challenges.erase(it);
                changed = true;
            }
            else
                ++it;
        }
        if (changed)
            RefreshLobbies();
    }

    void StopWatching(ObjectGuid guid)
    {
        auto it = watching.find(guid);
        if (it == watching.end())
            return;
        if (auto m = matches.find(it->second); m != matches.end())
            m->second.watchers.erase(guid);
        watching.erase(it);
    }

    char const* ReasonText(Chess::Reason reason)
    {
        switch (reason)
        {
            case Chess::Reason::Checkmate: return "checkmate";
            case Chess::Reason::Stalemate: return "stalemate";
            case Chess::Reason::FiftyMoves: return "fifty";
            case Chess::Reason::Repetition: return "repetition";
            case Chess::Reason::Material: return "material";
            default: return "end";
        }
    }

    // Ends a match exactly once: pays out, books the house cut, tells both players and the watchers, forgets it.
    void Finish(uint64 id, int winner, char const* reason)
    {
        auto it = matches.find(id);
        if (it == matches.end())
            return;
        Match m = std::move(it->second);
        matches.erase(it);
        if (m.thinking.valid())
            orphans.push_back(std::move(m.thinking));

        std::array<uint64, 2> paid {};
        if (m.stake)
        {
            uint64 const cut = winner >= 0 ? m.stake * boardConfig.cutBp / 10000 : 0;
            int64 const delta = house.Settle(0, cut, 0);
            CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
            for (int i = 0; i < 2; ++i)
            {
                paid[i] = winner < 0 ? m.stake : (i == winner ? 2 * m.stake - cut : 0);
                std::string const result = Acore::StringFormat("{} match {} vs {}: {} {}", Name(m.kind), id,
                    m.names[1 - i], winner < 0 ? "draw" : (i == winner ? "won" : "lost"), reason);
                bool const mailed = Pay(m.players[i], trans, paid[i],
                    Acore::StringFormat("Your {} match against {} has ended.", Name(m.kind), m.names[1 - i]));
                CloseRound(trans, m.rounds[i], paid[i], result);
                AppendLedger(trans, m.rounds[i], m.players[i].GetCounter(), mailed ? 0 : int64(paid[i]),
                    i == winner ? int64(cut) : 0, mailed ? "mailed" : "settle");
            }
            if (delta)
                BookHouse(trans, delta, m.rounds[winner]);
            CharacterDatabase.CommitTransaction(trans);
        }

        LOG_INFO("module.casino", "{} match {}: {} vs {}, stake {}, {} ({})", Name(m.kind), id, m.names[0], m.names[1],
            m.stake, winner < 0 ? std::string("draw") : m.names[winner] + " wins", reason);
        std::string const verdict = Acore::StringFormat("GE:{}:{}:{}", id, winner < 0 ? 2 : winner, reason);
        for (int i = 0; i < 2; ++i)
        {
            if (m.players[i].IsEmpty())
                continue; // the house
            playing.erase(m.players[i]);
            if (Player* player = ObjectAccessor::FindConnectedPlayer(m.players[i]))
                Send(player, Acore::StringFormat("{}:{}", verdict, paid[i]));
        }
        for (ObjectGuid const& watcher : m.watchers)
        {
            watching.erase(watcher);
            SendTo(watcher, verdict + ":0");
        }
        RefreshLobbies();
    }

    // After a move: the rules' own endings (mate, stalemate, draws, a side with no moves).
    void SettleIfOver(Match& m)
    {
        if (m.kind == Kind::Chess)
        {
            switch (m.chess.Result())
            {
                case Chess::Outcome::WhiteWins: return Finish(m.id, 0, ReasonText(m.chess.Why()));
                case Chess::Outcome::BlackWins: return Finish(m.id, 1, ReasonText(m.chess.Why()));
                case Chess::Outcome::Draw: return Finish(m.id, -1, ReasonText(m.chess.Why()));
                default: return Broadcast(m);
            }
        }
        switch (m.checkers.outcome)
        {
            case Checkers::Outcome::BlackWins: return Finish(m.id, 0, "nomoves");
            case Checkers::Outcome::WhiteWins: return Finish(m.id, 1, "nomoves");
            case Checkers::Outcome::Draw: return Finish(m.id, -1, "quiet");
            default: return Broadcast(m);
        }
    }

    void Create(Player* player, std::string_view args)
    {
        std::vector<std::string_view> parts = Acore::Tokenize(args, ':', true);
        if (parts.size() != 3 || (parts[0] != "c" && parts[0] != "k"))
            return Refuse(player, "amount");
        std::optional<uint64> stake = Acore::StringTo<uint64>(parts[1]);
        std::optional<uint32> minutes = Acore::StringTo<uint32>(parts[2]);
        if (!stake || !minutes || *minutes < 1 || *minutes > 60)
            return Refuse(player, "amount");
        if (!Open())
            return Refuse(player, "closed");
        auto npc = lobbyNpc.find(player->GetGUID());
        if (npc == lobbyNpc.end() || !Near(player, npc->second))
            return Refuse(player, "range");
        if (playing.contains(player->GetGUID()))
            return Refuse(player, "playing");
        if (PokerSeated(player->GetGUID()))
            return Refuse(player, "seated");
        if (*stake > boardConfig.maxStake)
            return Refuse(player, "max");
        if (*stake)
            if (char const* refusal = StakeRefusal(player, *stake))
                return Refuse(player, refusal);
        WorldObject* creature = ObjectAccessor::GetWorldObject(*player, npc->second);
        CancelChallenges(player->GetGUID());
        uint64 const id = nextId++;
        challenges[id] = { id, parts[0] == "c" ? Kind::Chess : Kind::Checkers, player->GetGUID(), player->GetName(),
                           *stake, *minutes, npc->second, creature ? creature->GetEntry() : 0 };
        RefreshLobbies();
    }

    void Accept(Player* player, std::string_view args)
    {
        std::optional<uint64> id = Acore::StringTo<uint64>(args);
        auto it = id ? challenges.find(*id) : challenges.end();
        if (it == challenges.end())
            return Refuse(player, "gone");
        Challenge const c = it->second;
        Player* host = ObjectAccessor::FindConnectedPlayer(c.host);
        if (!Open())
            return Refuse(player, "closed");
        if (!host || c.host == player->GetGUID())
            return Refuse(player, "gone");
        if (host->GetSession()->GetAccountId() == player->GetSession()->GetAccountId())
            return Refuse(player, "account");
        auto npc = lobbyNpc.find(player->GetGUID());
        if (npc == lobbyNpc.end() || !Near(player, npc->second))
            return Refuse(player, "range");
        if (playing.contains(player->GetGUID()) || playing.contains(c.host))
            return Refuse(player, "playing");
        if (PokerSeated(player->GetGUID()) || PokerSeated(c.host))
            return Refuse(player, "seated");
        if (c.stake)
        {
            if (char const* refusal = StakeRefusal(player, c.stake))
                return Refuse(player, refusal);
            if (StakeRefusal(host, c.stake))
                return Refuse(player, "host");
        }

        challenges.erase(it);
        CancelChallenges(player->GetGUID());
        uint64 const matchId = nextId++;
        Match& m = matches[matchId];
        m.id = matchId;
        m.kind = c.kind;
        m.npcEntry = c.npcEntry;
        m.stake = c.stake;
        int const hostSide = int(SecureBelow(2));
        m.players[hostSide] = host->GetGUID();
        m.players[1 - hostSide] = player->GetGUID();
        m.names[hostSide] = host->GetName();
        m.names[1 - hostSide] = player->GetName();
        m.clockMs = { int64(c.minutes) * 60000, int64(c.minutes) * 60000 };
        if (m.stake)
        {
            // Both stakes leave together: neither player can be charged for a match that didn't start.
            CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
            for (int i = 0; i < 2; ++i)
            {
                m.rounds[i] = NextRoundId();
                TakeStake(i == hostSide ? host : player, trans, m.rounds[i], Name(m.kind), m.npcEntry, m.stake,
                    Acore::StringFormat("{} match {} vs {}", Name(m.kind), matchId, m.names[1 - i]));
            }
            CharacterDatabase.CommitTransaction(trans);
        }
        for (int i = 0; i < 2; ++i)
        {
            playing[m.players[i]] = matchId;
            StopWatching(m.players[i]);
            Player* p = i == hostSide ? host : player;
            SendOpen(p);
            SendState(p, m, i);
        }
        LOG_INFO("module.casino", "{} match {} starts: {} vs {}, stake {}", Name(m.kind), matchId, m.names[0],
            m.names[1], m.stake);
        RefreshLobbies();
    }

    void Move(Player* player, std::string_view args)
    {
        auto p = playing.find(player->GetGUID());
        if (p == playing.end())
            return Refuse(player, "noround");
        Match& m = matches.at(p->second);
        int const side = m.SideOf(player->GetGUID());
        if (side != m.ToMove())
            return Refuse(player, "turn");
        bool played = false;
        if (m.kind == Kind::Chess)
        {
            if (std::optional<Chess::Move> move = Chess::FromText(std::string(args)))
                played = m.chess.Play(*move);
        }
        else
        {
            Checkers::Path path;
            for (std::string_view part : Acore::Tokenize(args, '-', false))
                if (std::optional<uint32> sq = Acore::StringTo<uint32>(part); sq && *sq < 64)
                    path.push_back(uint8(*sq));
            played = path.size() >= 2 && m.checkers.Play(path);
        }
        if (!played)
            return Refuse(player, "move");
        m.last = std::string(args);
        m.drawOffer = -1;
        SettleIfOver(m);
    }

    // The house's view of the board in its own favour (centipawns or checkers points).
    int HouseScore(Match const& m)
    {
        if (m.kind == Kind::Chess)
        {
            int const score = Chess::Ai::Evaluate(m.chess.Pos());
            return (m.chess.Pos().whiteToMove == (m.houseSide == 0)) ? score : -score;
        }
        int const score = Checkers::Ai::Evaluate(m.checkers);
        return (m.checkers.whiteToMove == (m.houseSide == 1)) ? score : -score;
    }

    // A free practice game against the house.
    void PlayHouse(Player* player, std::string_view args)
    {
        std::vector<std::string_view> parts = Acore::Tokenize(args, ':', true);
        std::optional<uint32> level = parts.size() == 3 ? Acore::StringTo<uint32>(parts[1]) : std::nullopt;
        std::optional<uint32> minutes = parts.size() == 3 ? Acore::StringTo<uint32>(parts[2]) : std::nullopt;
        if (!level || !minutes || *level < 1 || *level > 3 || *minutes < 1 || *minutes > 60 ||
            (parts[0] != "c" && parts[0] != "k"))
            return Refuse(player, "amount");
        if (!Open())
            return Refuse(player, "closed");
        auto npc = lobbyNpc.find(player->GetGUID());
        if (npc == lobbyNpc.end() || !Near(player, npc->second))
            return Refuse(player, "range");
        if (playing.contains(player->GetGUID()))
            return Refuse(player, "playing");
        if (PokerSeated(player->GetGUID()))
            return Refuse(player, "seated");
        CancelChallenges(player->GetGUID());
        StopWatching(player->GetGUID());
        uint64 const id = nextId++;
        Match& m = matches[id];
        m.id = id;
        m.kind = parts[0] == "c" ? Kind::Chess : Kind::Checkers;
        m.level = int(*level);
        int const you = int(SecureBelow(2));
        m.houseSide = 1 - you;
        m.players[you] = player->GetGUID();
        m.names[you] = player->GetName();
        m.names[m.houseSide] = Acore::StringFormat("The House ({})", LevelName(m.level));
        m.clockMs = { int64(*minutes) * 60000, int64(*minutes) * 60000 };
        m.houseDelayMs = 900;
        playing[player->GetGUID()] = id;
        SendOpen(player);
        SendState(player, m, you);
        LOG_INFO("module.casino", "{} plays the house at {} ({})", player->GetName(), Name(m.kind), LevelName(m.level));
        RefreshLobbies();
    }

    // Starts the house's search on a worker thread: a copy of the position, a seeded generator, a time limit.
    void Think(Match& m)
    {
        // Depth, milliseconds and root-score noise per level (index 1 easy .. 3 hard).
        static int const chessDepth[] = { 0, 1, 3, 5 }, chessMs[] = { 0, 150, 700, 1500 },
            chessNoise[] = { 0, 120, 25, 0 };
        static int const draughtsDepth[] = { 0, 2, 5, 9 }, draughtsMs[] = { 0, 150, 600, 1500 },
            draughtsNoise[] = { 0, 60, 10, 0 };
        uint32 const seed = SecureBelow(std::numeric_limits<uint32>::max());
        int const l = m.level;
        if (m.kind == Kind::Chess)
        {
            Chess::Position const pos = m.chess.Pos();
            m.thinking = std::async(std::launch::async, [pos, l, seed]()
            {
                std::mt19937 rng(seed);
                auto random = [&rng](uint32_t n) { return uint32_t(rng() % n); };
                return Chess::ToText(Chess::Ai::Choose(pos, chessDepth[l], chessMs[l], random, chessNoise[l]));
            });
        }
        else
        {
            Checkers::Game const game = m.checkers;
            m.thinking = std::async(std::launch::async, [game, l, seed]()
            {
                std::mt19937 rng(seed);
                auto random = [&rng](uint32_t n) { return uint32_t(rng() % n); };
                return Checkers::ToText(Checkers::Ai::Choose(game, draughtsDepth[l], draughtsMs[l], random,
                    draughtsNoise[l]));
            });
        }
    }

    // Applies the house's move, exactly as a player's would be checked and played.
    void PlayHouseMove(Match& m, std::string const& text)
    {
        bool played = false;
        if (m.kind == Kind::Chess)
        {
            if (std::optional<Chess::Move> move = Chess::FromText(text))
                played = m.chess.Play(*move);
        }
        else
        {
            Checkers::Path path;
            for (std::string_view part : Acore::Tokenize(text, '-', false))
                if (std::optional<uint32> sq = Acore::StringTo<uint32>(part); sq && *sq < 64)
                    path.push_back(uint8(*sq));
            played = path.size() >= 2 && m.checkers.Play(path);
        }
        if (!played)
        {
            LOG_ERROR("module.casino", "The house proposed an illegal move '{}' in match {}; it resigns.", text, m.id);
            return Finish(m.id, 1 - m.houseSide, "resign");
        }
        m.last = text;
        m.drawOffer = -1;
        m.houseDelayMs = 900;
        SettleIfOver(m);
    }

    void OfferDraw(Player* player)
    {
        auto p = playing.find(player->GetGUID());
        if (p == playing.end())
            return Refuse(player, "noround");
        Match& m = matches.at(p->second);
        int const side = m.SideOf(player->GetGUID());
        if (m.houseSide >= 0)
        {
            // The house takes a draw only when it stands clearly worse.
            if (HouseScore(m) < -150)
                return Finish(m.id, -1, "agreement");
            return Refuse(player, "declined");
        }
        if (m.drawOffer == 1 - side)
            return Finish(m.id, -1, "agreement");
        m.drawOffer = side;
        Broadcast(m);
    }
}

namespace EsteriaCasino::Server
{
    void LoadBoardConfig()
    {
        boardConfig.maxStake = std::min<uint64>(uint64(std::numeric_limits<int32>::max()) / 2,
            sConfigMgr->GetOption<uint64>("EsteriaCasino.Board.MaxStake", 100000000));
        boardConfig.cutBp = std::min(5000u, sConfigMgr->GetOption<uint32>("EsteriaCasino.Board.HouseCut", 500));
        boardConfig.minutes = std::clamp(sConfigMgr->GetOption<uint32>("EsteriaCasino.Board.Minutes", 10), 1u, 60u);
        boardConfig.graceSeconds = sConfigMgr->GetOption<uint32>("EsteriaCasino.Board.DisconnectGrace", 60);
    }

    void OpenBoardLobby(Player* player, WorldObject* npc)
    {
        lobbyNpc[player->GetGUID()] = npc->GetGUID();
        SendOpen(player);
        if (auto p = playing.find(player->GetGUID()); p != playing.end())
        {
            Match const& m = matches.at(p->second);
            return SendState(player, m, m.SideOf(player->GetGUID()));
        }
        StopWatching(player->GetGUID());
        SendLobby(player);
    }

    bool HandleBoardMessage(Player* player, std::string_view command, std::string_view args)
    {
        ObjectGuid const guid = player->GetGUID();
        if (command == "HI")
        {
            // After a /reload the window comes back on the running match.
            if (auto p = playing.find(guid); p != playing.end())
            {
                Match const& m = matches.at(p->second);
                SendOpen(player);
                SendState(player, m, m.SideOf(guid));
            }
            return false; // the other games answer HI too
        }
        if (command.size() != 2 || command[0] != 'G')
            return false;
        switch (command[1])
        {
            case 'L':
                if (lobbyNpc.contains(guid))
                    SendLobby(player);
                break;
            case 'C': Create(player, args); break;
            case 'X': CancelChallenges(guid); break;
            case 'A': Accept(player, args); break;
            case 'M': Move(player, args); break;
            case 'R':
                if (auto p = playing.find(guid); p != playing.end())
                    Finish(p->second, 1 - matches.at(p->second).SideOf(guid), "resign");
                break;
            case 'D': OfferDraw(player); break;
            case 'H': PlayHouse(player, args); break;
            case 'N':
                if (auto p = playing.find(guid); p != playing.end())
                {
                    Match& m = matches.at(p->second);
                    if (m.drawOffer == 1 - m.SideOf(guid))
                    {
                        m.drawOffer = -1;
                        Broadcast(m);
                    }
                }
                break;
            case 'W':
            {
                std::optional<uint64> id = Acore::StringTo<uint64>(args);
                auto m = id ? matches.find(*id) : matches.end();
                if (m == matches.end() || playing.contains(guid))
                {
                    Refuse(player, "gone");
                    break;
                }
                StopWatching(guid);
                watching[guid] = *id;
                m->second.watchers.insert(guid);
                SendState(player, m->second, -1);
                break;
            }
            case 'Q':
                StopWatching(guid);
                lobbyNpc.erase(guid);
                break;
            default:
                return false;
        }
        return true;
    }

    void BoardLogin(Player* player)
    {
        auto p = playing.find(player->GetGUID());
        if (p == playing.end())
            return;
        Match& m = matches.at(p->second);
        m.awayUntil[m.SideOf(player->GetGUID())] = 0;
        Broadcast(m);
    }

    void BoardLogout(Player* player)
    {
        ObjectGuid const guid = player->GetGUID();
        StopWatching(guid);
        lobbyNpc.erase(guid);
        CancelChallenges(guid);
        auto p = playing.find(guid);
        if (p == playing.end())
            return;
        Match& m = matches.at(p->second);
        if (m.houseSide >= 0)
            return Finish(m.id, m.houseSide, "forfeit"); // a practice game simply ends
        m.awayUntil[m.SideOf(guid)] = Now() + boardConfig.graceSeconds;
        Broadcast(m);
    }

    void BoardUpdate(uint32 diff)
    {
        std::erase_if(orphans, [](std::future<std::string>& f)
        {
            return f.wait_for(std::chrono::seconds(0)) == std::future_status::ready;
        });
        std::vector<std::pair<uint64, std::pair<int, char const*>>> ended;
        std::vector<std::pair<uint64, std::string>> houseMoves;
        uint32 const now = Now();
        for (auto& [id, m] : matches)
        {
            int const side = m.ToMove();
            if (side == m.houseSide)
            {
                // The house's clock never runs; it thinks after a short pause so its move reads as a move.
                if (m.thinking.valid())
                {
                    if (m.thinking.wait_for(std::chrono::seconds(0)) == std::future_status::ready)
                        houseMoves.push_back({ id, m.thinking.get() });
                }
                else if ((m.houseDelayMs -= diff) <= 0)
                    Think(m);
                continue;
            }
            m.clockMs[side] -= diff;
            if (m.clockMs[side] <= 0)
                ended.push_back({ id, { 1 - side, "time" } });
            else
                for (int i = 0; i < 2; ++i)
                    if (m.awayUntil[i] && now >= m.awayUntil[i])
                    {
                        ended.push_back({ id, { 1 - i, "forfeit" } });
                        break;
                    }
        }
        for (auto const& [id, result] : ended)
            Finish(id, result.first, result.second);
        for (auto const& [id, text] : houseMoves)
            if (auto m = matches.find(id); m != matches.end())
                PlayHouseMove(m->second, text);
    }
}

class npc_esteria_casino_board : public CreatureScript
{
public:
    npc_esteria_casino_board() : CreatureScript("npc_esteria_casino_board") { }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        ClearGossipMenuFor(player);
        if (Open())
            AddGossipItemFor(player, GOSSIP_ICON_MONEY_BAG, "Play chess or checkers.", GOSSIP_SENDER_MAIN,
                GOSSIP_ACTION_LOBBY);
        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature);
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* creature, uint32 /*sender*/, uint32 action) override
    {
        CloseGossipMenuFor(player);
        if (action == GOSSIP_ACTION_LOBBY && Open())
            OpenBoardLobby(player, creature);
        return true;
    }
};

void AddCasinoBoardScripts()
{
    new npc_esteria_casino_board();
}
