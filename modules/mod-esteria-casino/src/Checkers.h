/* American checkers (English draughts), kept free of game types so they can be unit tested.
 *
 * Squares run 0 = a1 .. 63 = h8; only dark squares ((rank + file) even) are used. White starts on ranks 1-3 and
 * moves up, black starts on ranks 6-8, moves down and moves first. Men move diagonally forward, kings both ways, one
 * square. Captures are compulsory and a capturing piece must keep jumping while it can; a man that reaches the far
 * row is crowned and its move ends. A side with no legal move loses. Eighty plies without a capture or a man moving
 * is a draw.
 */
#ifndef ESTERIA_CASINO_CHECKERS_H
#define ESTERIA_CASINO_CHECKERS_H

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <functional>
#include <string>
#include <vector>

namespace EsteriaCasino::Checkers
{
    // Positive white, negative black; 1 man, 2 king.
    constexpr int8_t MAN = 1;
    constexpr int8_t KING = 2;
    constexpr int DRAW_PLIES = 80;

    using Path = std::vector<uint8_t>; // start square, then every landing square

    inline std::string ToText(Path const& path)
    {
        std::string out;
        for (uint8_t sq : path)
            out += (out.empty() ? "" : "-") + std::to_string(sq);
        return out;
    }

    enum class Outcome : uint8_t
    {
        Ongoing,
        WhiteWins,
        BlackWins,
        Draw,
    };

    class Game
    {
    public:
        Game()
        {
            for (int sq = 0; sq < 64; ++sq)
                if ((sq / 8 + sq % 8) % 2 == 0)
                    board[sq] = sq < 24 ? MAN : sq >= 40 ? -MAN : 0;
        }

        std::array<int8_t, 64> board {};
        bool whiteToMove = false; // black moves first
        int quietPlies = 0;
        Outcome outcome = Outcome::Ongoing;

        // 64 characters: 'w' 'W' white man/king, 'b' 'B' black, '.' empty.
        std::string BoardText() const
        {
            std::string out(64, '.');
            for (int sq = 0; sq < 64; ++sq)
                if (board[sq])
                    out[sq] = board[sq] > 0 ? (board[sq] == KING ? 'W' : 'w') : (board[sq] == -KING ? 'B' : 'b');
            return out;
        }

        std::vector<Path> Legal() const
        {
            std::vector<Path> jumps, steps;
            int const sign = whiteToMove ? 1 : -1;
            for (int sq = 0; sq < 64; ++sq)
            {
                if (board[sq] * sign <= 0)
                    continue;
                auto b = board;
                b[sq] = 0; // the jumping piece has left its square
                Path path { uint8_t(sq) };
                Jumps(b, board[sq], sq, path, jumps);
                if (!jumps.empty())
                    continue;
                for (auto const& d : Directions(board[sq]))
                {
                    int const to = Step(sq, d[0], d[1]);
                    if (to >= 0 && !board[to])
                        steps.push_back({ uint8_t(sq), uint8_t(to) });
                }
            }
            return jumps.empty() ? steps : jumps;
        }

        bool Play(Path const& path)
        {
            if (outcome != Outcome::Ongoing)
                return false;
            bool found = false;
            for (Path const& legal : Legal())
                found = found || legal == path;
            if (!found)
                return false;
            Move(path);
            if (Legal().empty())
                outcome = whiteToMove ? Outcome::BlackWins : Outcome::WhiteWins;
            else if (quietPlies >= DRAW_PLIES)
                outcome = Outcome::Draw;
            return true;
        }

        // Makes a move already known to be legal: the board, the draw counter and the turn, nothing else.
        void Move(Path const& path)
        {
            int8_t piece = board[path.front()];
            bool const manMoved = std::abs(piece) == MAN;
            bool const capture = std::abs(path[1] - path[0]) > 9;
            board[path.front()] = 0;
            for (size_t i = 1; i < path.size(); ++i)
                if (std::abs(path[i] - path[i - 1]) > 9)
                    board[(path[i] + path[i - 1]) / 2] = 0;
            int const last = path.back();
            if (manMoved && (piece > 0 ? last / 8 == 7 : last / 8 == 0))
                piece = int8_t(piece * KING);
            board[last] = piece;
            // Only kings shuffling without capturing count toward the draw.
            quietPlies = (capture || manMoved) ? 0 : quietPlies + 1;
            whiteToMove = !whiteToMove;
        }

    private:
        static std::vector<std::array<int, 2>> Directions(int8_t piece)
        {
            if (std::abs(piece) == KING)
                return { { 1, 1 }, { 1, -1 }, { -1, 1 }, { -1, -1 } };
            int const forward = piece > 0 ? 1 : -1;
            return { { forward, 1 }, { forward, -1 } };
        }

        // The square `n` diagonal steps away (dr ranks, df files per step), or -1 off the board.
        static int Step(int sq, int dr, int df, int n = 1)
        {
            int const r = sq / 8 + dr * n, f = sq % 8 + df * n;
            return (r < 0 || r > 7 || f < 0 || f > 7) ? -1 : r * 8 + f;
        }

        // Extends `path` through every capture from `sq`; a path that can't continue is a complete move.
        void Jumps(std::array<int8_t, 64>& b, int8_t piece, int sq, Path& path, std::vector<Path>& out) const
        {
            bool extended = false;
            for (auto const& d : Directions(piece))
            {
                int const over = Step(sq, d[0], d[1]);
                int const to = Step(sq, d[0], d[1], 2);
                if (to < 0 || b[to] || b[over] * piece >= 0)
                    continue;
                extended = true;
                int8_t const taken = b[over];
                b[over] = 0;
                path.push_back(uint8_t(to));
                bool const crowned = std::abs(piece) == MAN && (piece > 0 ? to / 8 == 7 : to / 8 == 0);
                if (crowned)
                    out.push_back(path); // crowning ends the move
                else
                    Jumps(b, piece, to, path, out);
                path.pop_back();
                b[over] = taken;
            }
            if (!extended && path.size() > 1)
                out.push_back(path);
        }
    };
    // The house opponent: men, kings, advancement and the centre, searched with alpha-beta until a depth or a time
    // limit. Pure computation on a copy of the game, so it may run off the world thread.
    namespace Ai
    {
        constexpr int WIN = 100000;

        // Points for the side to move.
        inline int Evaluate(Game const& g)
        {
            int score = 0;
            for (int sq = 0; sq < 64; ++sq)
            {
                int8_t const piece = g.board[sq];
                if (!piece)
                    continue;
                int const rank = sq / 8, file = sq % 8;
                int value = std::abs(piece) == KING ? 175 : 100 + 4 * (piece > 0 ? rank : 7 - rank);
                if (file >= 2 && file <= 5 && rank >= 2 && rank <= 5)
                    value += 6; // the centre
                score += piece > 0 ? value : -value;
            }
            return g.whiteToMove ? score : -score;
        }

        struct Search
        {
            std::chrono::steady_clock::time_point deadline;
            bool stopped = false;
            uint32_t nodes = 0;

            bool OutOfTime()
            {
                if ((++nodes & 255) == 0 && std::chrono::steady_clock::now() >= deadline)
                    stopped = true;
                return stopped;
            }
        };

        inline int Negamax(Game const& g, int depth, int alpha, int beta, int ply, Search& s)
        {
            std::vector<Path> const moves = g.Legal();
            if (moves.empty())
                return -WIN + ply;
            if (g.quietPlies >= DRAW_PLIES)
                return 0;
            // Forced captures are searched one ply deeper so the horizon never cuts an exchange in half.
            bool const capturing = std::abs(moves[0][1] - moves[0][0]) > 9;
            if (depth <= 0 && !capturing)
                return Evaluate(g);
            int best = -WIN * 2;
            for (Path const& path : moves)
            {
                if (s.OutOfTime())
                    break;
                Game next = g;
                next.Move(path);
                int const score = -Negamax(next, depth - 1, -beta, -alpha, ply + 1, s);
                best = std::max(best, score);
                alpha = std::max(alpha, score);
                if (alpha >= beta)
                    break;
            }
            return best;
        }

        // The house's move: iterative deepening to `maxDepth` within `milliseconds`; `noise` blurs root scores.
        inline Path Choose(Game const& g, int maxDepth, int milliseconds,
            std::function<uint32_t(uint32_t)> const& random, int noise)
        {
            std::vector<Path> const moves = g.Legal();
            if (moves.empty())
                return {};
            Search s;
            s.deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(milliseconds);
            std::vector<int> jitter(moves.size(), 0);
            if (noise > 0)
                for (int& j : jitter)
                    j = int(random(uint32_t(noise * 2 + 1))) - noise;
            Path best = moves.front();
            for (int depth = 1; depth <= maxDepth; ++depth)
            {
                int alpha = -WIN * 2;
                Path iterationBest = moves.front();
                bool complete = true;
                for (size_t i = 0; i < moves.size(); ++i)
                {
                    Game next = g;
                    next.Move(moves[i]);
                    int const score = -Negamax(next, depth - 1, -WIN * 2, -alpha, 1, s) + jitter[i];
                    if (s.stopped && depth > 1)
                    {
                        complete = false;
                        break;
                    }
                    if (score > alpha)
                    {
                        alpha = score;
                        iterationBest = moves[i];
                    }
                }
                if (!complete)
                    break;
                best = iterationBest;
                if (s.stopped || alpha >= WIN - 100)
                    break;
            }
            return best;
        }
    }
}

#endif
