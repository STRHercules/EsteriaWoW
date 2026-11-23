/* Chess rules, kept free of game types so they can be unit tested (perft counts in tests/board_games_test.cpp).
 *
 * Squares run 0 = a1 .. 63 = h8 (rank * 8 + file). Pieces are signed: positive white, negative black, magnitude
 * 1 pawn, 2 knight, 3 bishop, 4 rook, 5 queen, 6 king. Full rules: castling, en passant, promotion, check, mate,
 * stalemate, the fifty-move rule, threefold repetition and insufficient material.
 */
#ifndef ESTERIA_CASINO_CHESS_H
#define ESTERIA_CASINO_CHESS_H

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <functional>
#include <map>
#include <optional>
#include <string>
#include <vector>

namespace EsteriaCasino::Chess
{
    enum PieceType : int8_t
    {
        EMPTY = 0,
        PAWN = 1,
        KNIGHT = 2,
        BISHOP = 3,
        ROOK = 4,
        QUEEN = 5,
        KING = 6,
    };

    enum Castling : uint8_t
    {
        WHITE_SHORT = 1,
        WHITE_LONG = 2,
        BLACK_SHORT = 4,
        BLACK_LONG = 8,
    };

    struct Move
    {
        uint8_t from = 0;
        uint8_t to = 0;
        int8_t promotion = 0; // piece type, or 0

        bool operator==(Move const& other) const
        {
            return from == other.from && to == other.to && promotion == other.promotion;
        }
    };

    inline int File(int sq) { return sq % 8; }
    inline int Rank(int sq) { return sq / 8; }

    // "e2e4", "e7e8q".
    inline std::string ToText(Move m)
    {
        std::string out = { char('a' + File(m.from)), char('1' + Rank(m.from)), char('a' + File(m.to)),
                            char('1' + Rank(m.to)) };
        if (m.promotion)
            out += " pnbrqk"[m.promotion];
        return out;
    }

    inline std::optional<Move> FromText(std::string const& text)
    {
        if (text.size() != 4 && text.size() != 5)
            return std::nullopt;
        auto square = [](char f, char r) -> int
        {
            return (f >= 'a' && f <= 'h' && r >= '1' && r <= '8') ? (r - '1') * 8 + (f - 'a') : -1;
        };
        int const from = square(text[0], text[1]);
        int const to = square(text[2], text[3]);
        if (from < 0 || to < 0)
            return std::nullopt;
        Move m { uint8_t(from), uint8_t(to), 0 };
        if (text.size() == 5)
        {
            std::string const kinds = "nbrq";
            size_t const k = kinds.find(text[4]);
            if (k == std::string::npos)
                return std::nullopt;
            m.promotion = int8_t(KNIGHT + k);
        }
        return m;
    }

    class Position
    {
    public:
        std::array<int8_t, 64> board {};
        bool whiteToMove = true;
        uint8_t castling = 0;
        int8_t enPassant = -1; // square a pawn may capture onto, or -1
        int halfmoves = 0;     // since the last capture or pawn move
        int fullmoves = 1;

        static Position Start()
        {
            return *FromFen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
        }

        static std::optional<Position> FromFen(std::string const& fen)
        {
            Position p;
            size_t i = 0;
            int rank = 7, file = 0;
            std::string const letters = "pnbrqk";
            for (; i < fen.size() && fen[i] != ' '; ++i)
            {
                char const c = fen[i];
                if (c == '/')
                {
                    --rank;
                    file = 0;
                }
                else if (c >= '1' && c <= '8')
                    file += c - '0';
                else
                {
                    size_t const k = letters.find(char(c | 0x20));
                    if (k == std::string::npos || rank < 0 || file > 7)
                        return std::nullopt;
                    p.board[rank * 8 + file] = int8_t((k + 1) * (c >= 'a' ? -1 : 1));
                    ++file;
                }
            }
            if (++i >= fen.size())
                return std::nullopt;
            p.whiteToMove = fen[i] == 'w';
            i += 2;
            for (; i < fen.size() && fen[i] != ' '; ++i)
            {
                switch (fen[i])
                {
                    case 'K': p.castling |= WHITE_SHORT; break;
                    case 'Q': p.castling |= WHITE_LONG; break;
                    case 'k': p.castling |= BLACK_SHORT; break;
                    case 'q': p.castling |= BLACK_LONG; break;
                    default: break;
                }
            }
            ++i;
            if (i + 1 < fen.size() && fen[i] != '-')
                p.enPassant = int8_t((fen[i + 1] - '1') * 8 + (fen[i] - 'a'));
            return p;
        }

        // 64 characters a1..h8: "PNBRQK" white, "pnbrqk" black, '.' empty.
        std::string BoardText() const
        {
            std::string out(64, '.');
            for (int sq = 0; sq < 64; ++sq)
                if (board[sq])
                    out[sq] = board[sq] > 0 ? "PNBRQK"[board[sq] - 1] : "pnbrqk"[-board[sq] - 1];
            return out;
        }

        // Identity of the position for repetition: board, side, castling rights and en passant.
        std::string Key() const
        {
            return BoardText() + (whiteToMove ? 'w' : 'b') + char('A' + castling) + char('a' + enPassant + 1);
        }

        bool Attacked(int sq, bool byWhite) const
        {
            int const sign = byWhite ? 1 : -1;
            int const f = File(sq), r = Rank(sq);
            auto at = [&](int ff, int rr) -> int8_t
            {
                return (ff < 0 || ff > 7 || rr < 0 || rr > 7) ? int8_t(127) : board[rr * 8 + ff];
            };
            // Pawns attack diagonally forward from their own side.
            int const pr = r - sign;
            if (at(f - 1, pr) == sign * PAWN || at(f + 1, pr) == sign * PAWN)
                return true;
            static int const knight[8][2] = { { 1, 2 }, { 2, 1 }, { 2, -1 }, { 1, -2 }, { -1, -2 }, { -2, -1 },
                                              { -2, 1 }, { -1, 2 } };
            for (auto const& d : knight)
                if (at(f + d[0], r + d[1]) == sign * KNIGHT)
                    return true;
            for (int df = -1; df <= 1; ++df)
                for (int dr = -1; dr <= 1; ++dr)
                    if ((df || dr) && at(f + df, r + dr) == sign * KING)
                        return true;
            static int const rays[8][2] = { { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 }, { 1, 1 }, { 1, -1 },
                                            { -1, 1 }, { -1, -1 } };
            for (int k = 0; k < 8; ++k)
            {
                bool const straight = k < 4;
                for (int ff = f + rays[k][0], rr = r + rays[k][1]; ; ff += rays[k][0], rr += rays[k][1])
                {
                    int8_t const piece = at(ff, rr);
                    if (piece == 127)
                        break;
                    if (!piece)
                        continue;
                    if (piece == sign * QUEEN || piece == sign * (straight ? ROOK : BISHOP))
                        return true;
                    break;
                }
            }
            return false;
        }

        int KingSquare(bool white) const
        {
            for (int sq = 0; sq < 64; ++sq)
                if (board[sq] == (white ? KING : -KING))
                    return sq;
            return -1;
        }

        bool InCheck(bool white) const
        {
            int const king = KingSquare(white);
            return king >= 0 && Attacked(king, !white);
        }

        void Apply(Move m)
        {
            int8_t const piece = board[m.from];
            int const type = std::abs(piece);
            bool const capture = board[m.to] != 0 || (type == PAWN && m.to == enPassant);
            if (type == PAWN && m.to == enPassant)
                board[m.to + (whiteToMove ? -8 : 8)] = 0;
            board[m.to] = m.promotion ? int8_t(m.promotion * (whiteToMove ? 1 : -1)) : piece;
            board[m.from] = 0;
            if (type == KING && std::abs(m.to - m.from) == 2)
            {
                // The rook jumps over the king.
                int const rank = Rank(m.from) * 8;
                if (m.to > m.from)
                {
                    board[rank + 5] = board[rank + 7];
                    board[rank + 7] = 0;
                }
                else
                {
                    board[rank + 3] = board[rank];
                    board[rank] = 0;
                }
            }
            enPassant = (type == PAWN && std::abs(m.to - m.from) == 16) ? int8_t((m.from + m.to) / 2) : int8_t(-1);
            auto clearRights = [this](int sq)
            {
                if (sq == 0) castling &= ~WHITE_LONG;
                if (sq == 7) castling &= ~WHITE_SHORT;
                if (sq == 56) castling &= ~BLACK_LONG;
                if (sq == 63) castling &= ~BLACK_SHORT;
                if (sq == 4) castling &= ~(WHITE_SHORT | WHITE_LONG);
                if (sq == 60) castling &= ~(BLACK_SHORT | BLACK_LONG);
            };
            clearRights(m.from);
            clearRights(m.to);
            halfmoves = (capture || type == PAWN) ? 0 : halfmoves + 1;
            if (!whiteToMove)
                ++fullmoves;
            whiteToMove = !whiteToMove;
        }

        std::vector<Move> Legal() const
        {
            std::vector<Move> moves;
            Pseudo(moves);
            std::vector<Move> legal;
            for (Move m : moves)
            {
                Position next = *this;
                next.Apply(m);
                if (!next.InCheck(whiteToMove))
                    legal.push_back(m);
            }
            return legal;
        }

        // Neither side can ever mate: kings alone, or kings and one minor piece.
        bool InsufficientMaterial() const
        {
            int minors = 0;
            for (int8_t piece : board)
            {
                int const type = std::abs(piece);
                if (type == PAWN || type == ROOK || type == QUEEN)
                    return false;
                if (type == KNIGHT || type == BISHOP)
                    ++minors;
            }
            return minors <= 1;
        }

    private:
        void Pseudo(std::vector<Move>& out) const
        {
            int const sign = whiteToMove ? 1 : -1;
            for (int sq = 0; sq < 64; ++sq)
            {
                int8_t const piece = board[sq];
                if (piece * sign <= 0)
                    continue;
                int const type = std::abs(piece);
                int const f = File(sq), r = Rank(sq);
                auto add = [&](int to)
                {
                    if (type == PAWN && (Rank(to) == 7 || Rank(to) == 0))
                        for (int8_t promo : { QUEEN, ROOK, BISHOP, KNIGHT })
                            out.push_back({ uint8_t(sq), uint8_t(to), promo });
                    else
                        out.push_back({ uint8_t(sq), uint8_t(to), 0 });
                };
                auto own = [&](int to) { return board[to] * sign > 0; };
                auto enemy = [&](int to) { return board[to] * sign < 0; };
                if (type == PAWN)
                {
                    int const step = 8 * sign;
                    int const one = sq + step;
                    if (one >= 0 && one < 64 && !board[one])
                    {
                        add(one);
                        bool const home = whiteToMove ? r == 1 : r == 6;
                        if (home && !board[one + step])
                            add(one + step);
                    }
                    for (int df : { -1, 1 })
                    {
                        int const ff = f + df;
                        if (ff < 0 || ff > 7 || one < 0 || one >= 64)
                            continue;
                        int const to = one + df;
                        if (enemy(to) || to == enPassant)
                            add(to);
                    }
                }
                else if (type == KNIGHT || type == KING)
                {
                    static int const knight[8][2] = { { 1, 2 }, { 2, 1 }, { 2, -1 }, { 1, -2 }, { -1, -2 },
                                                      { -2, -1 }, { -2, 1 }, { -1, 2 } };
                    static int const king[8][2] = { { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 }, { 1, 1 }, { 1, -1 },
                                                    { -1, 1 }, { -1, -1 } };
                    for (auto const& d : (type == KNIGHT ? knight : king))
                    {
                        int const ff = f + d[0], rr = r + d[1];
                        if (ff < 0 || ff > 7 || rr < 0 || rr > 7 || own(rr * 8 + ff))
                            continue;
                        add(rr * 8 + ff);
                    }
                    if (type == KING)
                        Castle(sq, out);
                }
                else
                {
                    static int const rays[8][2] = { { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 }, { 1, 1 }, { 1, -1 },
                                                    { -1, 1 }, { -1, -1 } };
                    int const first = type == BISHOP ? 4 : 0;
                    int const last = type == ROOK ? 4 : 8;
                    for (int k = first; k < last; ++k)
                        for (int ff = f + rays[k][0], rr = r + rays[k][1]; ff >= 0 && ff <= 7 && rr >= 0 && rr <= 7;
                             ff += rays[k][0], rr += rays[k][1])
                        {
                            int const to = rr * 8 + ff;
                            if (own(to))
                                break;
                            add(to);
                            if (board[to])
                                break;
                        }
                }
            }
        }

        void Castle(int sq, std::vector<Move>& out) const
        {
            bool const white = whiteToMove;
            int const home = white ? 4 : 60;
            if (sq != home || Attacked(home, !white))
                return;
            uint8_t const shortRight = white ? WHITE_SHORT : BLACK_SHORT;
            uint8_t const longRight = white ? WHITE_LONG : BLACK_LONG;
            int8_t const rook = white ? ROOK : -ROOK;
            if ((castling & shortRight) && board[home + 3] == rook && !board[home + 1] && !board[home + 2] &&
                !Attacked(home + 1, !white) && !Attacked(home + 2, !white))
                out.push_back({ uint8_t(home), uint8_t(home + 2), 0 });
            if ((castling & longRight) && board[home - 4] == rook && !board[home - 1] && !board[home - 2] &&
                !board[home - 3] && !Attacked(home - 1, !white) && !Attacked(home - 2, !white))
                out.push_back({ uint8_t(home), uint8_t(home - 2), 0 });
        }
    };

    enum class Outcome : uint8_t
    {
        Ongoing,
        WhiteWins,
        BlackWins,
        Draw,
    };

    enum class Reason : uint8_t
    {
        None,
        Checkmate,
        Stalemate,
        FiftyMoves,
        Repetition,
        Material,
        Resignation,
        Time,
        Agreement,
        Forfeit,
    };

    class Game
    {
    public:
        Game() : _pos(Position::Start()) { _seen[_pos.Key()] = 1; }

        Position const& Pos() const { return _pos; }
        Outcome Result() const { return _outcome; }
        Chess::Reason Why() const { return _reason; }
        std::string const& Last() const { return _last; }

        // Plays a move if it is legal in the current position; settles mate, stalemate and the draw rules.
        bool Play(Move m)
        {
            if (_outcome != Outcome::Ongoing)
                return false;
            std::vector<Move> const legal = _pos.Legal();
            bool found = false;
            for (Move const& l : legal)
                found = found || l == m;
            if (!found)
                return false;
            _pos.Apply(m);
            _last = ToText(m);
            int const seen = ++_seen[_pos.Key()];
            bool const check = _pos.InCheck(_pos.whiteToMove);
            if (_pos.Legal().empty())
                End(check ? (_pos.whiteToMove ? Outcome::BlackWins : Outcome::WhiteWins) : Outcome::Draw,
                    check ? Chess::Reason::Checkmate : Chess::Reason::Stalemate);
            else if (_pos.halfmoves >= 100)
                End(Outcome::Draw, Chess::Reason::FiftyMoves);
            else if (seen >= 3)
                End(Outcome::Draw, Chess::Reason::Repetition);
            else if (_pos.InsufficientMaterial())
                End(Outcome::Draw, Chess::Reason::Material);
            return true;
        }

        void End(Outcome outcome, Chess::Reason reason)
        {
            if (_outcome != Outcome::Ongoing)
                return;
            _outcome = outcome;
            _reason = reason;
        }

    private:
        Position _pos;
        std::map<std::string, int> _seen;
        Outcome _outcome = Outcome::Ongoing;
        Chess::Reason _reason = Chess::Reason::None;
        std::string _last;
    };

    // The house opponent: material plus piece-square tables, searched with alpha-beta and a capture extension
    // until a depth or a time limit. Pure computation on a copy of the position, so it may run off the world thread.
    namespace Ai
    {
        constexpr int MATE = 100000;
        constexpr std::array<int, 7> VALUE = { 0, 100, 320, 330, 500, 900, 0 };

        // Piece-square tables from white's side, rank 8 first (Tomasz Michniewski's simplified evaluation).
        constexpr std::array<std::array<int, 64>, 7> TABLE = { {
            {},
            { // pawn
                  0,   0,   0,   0,   0,   0,   0,   0,
                 50,  50,  50,  50,  50,  50,  50,  50,
                 10,  10,  20,  30,  30,  20,  10,  10,
                  5,   5,  10,  25,  25,  10,   5,   5,
                  0,   0,   0,  20,  20,   0,   0,   0,
                  5,  -5, -10,   0,   0, -10,  -5,   5,
                  5,  10,  10, -20, -20,  10,  10,   5,
                  0,   0,   0,   0,   0,   0,   0,   0
            },
            { // knight
                -50, -40, -30, -30, -30, -30, -40, -50,
                -40, -20,   0,   0,   0,   0, -20, -40,
                -30,   0,  10,  15,  15,  10,   0, -30,
                -30,   5,  15,  20,  20,  15,   5, -30,
                -30,   0,  15,  20,  20,  15,   0, -30,
                -30,   5,  10,  15,  15,  10,   5, -30,
                -40, -20,   0,   5,   5,   0, -20, -40,
                -50, -40, -30, -30, -30, -30, -40, -50
            },
            { // bishop
                -20, -10, -10, -10, -10, -10, -10, -20,
                -10,   0,   0,   0,   0,   0,   0, -10,
                -10,   0,   5,  10,  10,   5,   0, -10,
                -10,   5,   5,  10,  10,   5,   5, -10,
                -10,   0,  10,  10,  10,  10,   0, -10,
                -10,  10,  10,  10,  10,  10,  10, -10,
                -10,   5,   0,   0,   0,   0,   5, -10,
                -20, -10, -10, -10, -10, -10, -10, -20
            },
            { // rook
                  0,   0,   0,   0,   0,   0,   0,   0,
                  5,  10,  10,  10,  10,  10,  10,   5,
                 -5,   0,   0,   0,   0,   0,   0,  -5,
                 -5,   0,   0,   0,   0,   0,   0,  -5,
                 -5,   0,   0,   0,   0,   0,   0,  -5,
                 -5,   0,   0,   0,   0,   0,   0,  -5,
                 -5,   0,   0,   0,   0,   0,   0,  -5,
                  0,   0,   0,   5,   5,   0,   0,   0
            },
            { // queen
                -20, -10, -10,  -5,  -5, -10, -10, -20,
                -10,   0,   0,   0,   0,   0,   0, -10,
                -10,   0,   5,   5,   5,   5,   0, -10,
                 -5,   0,   5,   5,   5,   5,   0,  -5,
                  0,   0,   5,   5,   5,   5,   0,  -5,
                -10,   5,   5,   5,   5,   5,   0, -10,
                -10,   0,   5,   0,   0,   0,   0, -10,
                -20, -10, -10,  -5,  -5, -10, -10, -20
            },
            { // king
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -20, -30, -30, -40, -40, -30, -30, -20,
                -10, -20, -20, -20, -20, -20, -20, -10,
                 20,  20,   0,   0,   0,   0,  20,  20,
                 20,  30,  10,   0,   0,  10,  30,  20
            }
        } };

        // Centipawns for the side to move.
        inline int Evaluate(Position const& p)
        {
            int score = 0;
            for (int sq = 0; sq < 64; ++sq)
            {
                int8_t const piece = p.board[sq];
                if (!piece)
                    continue;
                int const type = std::abs(piece);
                // The tables list rank 8 first: a white piece reads its square mirrored, a black piece reads it as is.
                int const value = VALUE[type] + TABLE[type][piece > 0 ? (sq ^ 56) : sq];
                score += piece > 0 ? value : -value;
            }
            return p.whiteToMove ? score : -score;
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

        // Captures and promotions first, the most valuable victim taken by the cheapest attacker first.
        inline void Order(Position const& p, std::vector<Move>& moves)
        {
            auto score = [&p](Move const& m)
            {
                int const victim = std::abs(p.board[m.to]);
                return victim * 100 - std::abs(p.board[m.from]) + m.promotion * 1000;
            };
            std::stable_sort(moves.begin(), moves.end(),
                [&score](Move const& a, Move const& b) { return score(a) > score(b); });
        }

        inline int Quiesce(Position const& p, int alpha, int beta, Search& s, int depth)
        {
            int const stand = Evaluate(p);
            if (stand >= beta || depth == 0 || s.OutOfTime())
                return stand;
            alpha = std::max(alpha, stand);
            std::vector<Move> moves = p.Legal();
            Order(p, moves);
            for (Move const& m : moves)
            {
                if (!p.board[m.to] && !m.promotion)
                    break; // ordered: the captures came first
                Position next = p;
                next.Apply(m);
                int const score = -Quiesce(next, -beta, -alpha, s, depth - 1);
                if (score >= beta)
                    return score;
                alpha = std::max(alpha, score);
            }
            return alpha;
        }

        inline int Negamax(Position const& p, int depth, int alpha, int beta, int ply, Search& s)
        {
            std::vector<Move> moves = p.Legal();
            if (moves.empty())
                return p.InCheck(p.whiteToMove) ? -MATE + ply : 0;
            if (p.halfmoves >= 100)
                return 0;
            if (depth == 0)
                return Quiesce(p, alpha, beta, s, 4);
            Order(p, moves);
            int best = -MATE * 2;
            for (Move const& m : moves)
            {
                if (s.OutOfTime())
                    break;
                Position next = p;
                next.Apply(m);
                int const score = -Negamax(next, depth - 1, -beta, -alpha, ply + 1, s);
                best = std::max(best, score);
                alpha = std::max(alpha, score);
                if (alpha >= beta)
                    break;
            }
            return best;
        }

        // The house's move: iterative deepening to `maxDepth` within `milliseconds`. `noise` (centipawns) blurs
        // each root move's score so easier levels make human mistakes.
        inline Move Choose(Position const& p, int maxDepth, int milliseconds,
            std::function<uint32_t(uint32_t)> const& random, int noise)
        {
            std::vector<Move> moves = p.Legal();
            if (moves.empty())
                return {};
            Order(p, moves);
            Search s;
            s.deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(milliseconds);
            std::vector<int> jitter(moves.size(), 0);
            if (noise > 0)
                for (int& j : jitter)
                    j = int(random(uint32_t(noise * 2 + 1))) - noise;
            Move best = moves.front();
            for (int depth = 1; depth <= maxDepth; ++depth)
            {
                int alpha = -MATE * 2;
                Move iterationBest = moves.front();
                bool complete = true;
                for (size_t i = 0; i < moves.size(); ++i)
                {
                    Position next = p;
                    next.Apply(moves[i]);
                    int const score = -Negamax(next, depth - 1, -MATE * 2, -alpha, 1, s) + jitter[i];
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
                if (s.stopped || alpha >= MATE - 100)
                    break;
            }
            return best;
        }
    }
}

#endif
