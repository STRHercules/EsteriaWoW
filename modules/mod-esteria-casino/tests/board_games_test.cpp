#include "Checkers.h"
#include "Chess.h"

#include "gtest/gtest.h"

using namespace EsteriaCasino;

namespace
{
    uint64_t Perft(Chess::Position const& pos, int depth)
    {
        if (depth == 0)
            return 1;
        uint64_t nodes = 0;
        for (Chess::Move m : pos.Legal())
        {
            Chess::Position next = pos;
            next.Apply(m);
            nodes += Perft(next, depth - 1);
        }
        return nodes;
    }

    uint64_t PerftFen(char const* fen, int depth)
    {
        return Perft(*Chess::Position::FromFen(fen), depth);
    }

    bool PlayAll(Chess::Game& game, std::vector<char const*> const& moves)
    {
        for (char const* text : moves)
            if (!game.Play(*Chess::FromText(text)))
                return false;
        return true;
    }
}

// Published perft node counts (chessprogramming.org) exercise every rule of move generation.
TEST(EsteriaCasinoChess, PerftStartPosition)
{
    Chess::Position const start = Chess::Position::Start();
    EXPECT_EQ(Perft(start, 1), 20u);
    EXPECT_EQ(Perft(start, 2), 400u);
    EXPECT_EQ(Perft(start, 3), 8902u);
    EXPECT_EQ(Perft(start, 4), 197281u);
}

TEST(EsteriaCasinoChess, PerftTrickyPositions)
{
    // "Kiwipete": castling through and out of check, en passant, promotions.
    char const* kiwipete = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1";
    EXPECT_EQ(PerftFen(kiwipete, 1), 48u);
    EXPECT_EQ(PerftFen(kiwipete, 2), 2039u);
    EXPECT_EQ(PerftFen(kiwipete, 3), 97862u);
    // Position 3: en passant discovered checks along the rank.
    char const* rook = "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1";
    EXPECT_EQ(PerftFen(rook, 1), 14u);
    EXPECT_EQ(PerftFen(rook, 2), 191u);
    EXPECT_EQ(PerftFen(rook, 3), 2812u);
    EXPECT_EQ(PerftFen(rook, 4), 43238u);
    // Position 5: promotion with capture, castling rights lost to a capture.
    char const* five = "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8";
    EXPECT_EQ(PerftFen(five, 1), 44u);
    EXPECT_EQ(PerftFen(five, 2), 1486u);
    EXPECT_EQ(PerftFen(five, 3), 62379u);
}

TEST(EsteriaCasinoChess, GameEndings)
{
    Chess::Game mate;
    ASSERT_TRUE(PlayAll(mate, { "f2f3", "e7e5", "g2g4", "d8h4" })); // fool's mate
    EXPECT_EQ(mate.Result(), Chess::Outcome::BlackWins);
    EXPECT_EQ(mate.Why(), Chess::Reason::Checkmate);
    EXPECT_FALSE(mate.Play(*Chess::FromText("a2a3"))) << "no moves after the game ends";

    Chess::Game repetition;
    ASSERT_TRUE(PlayAll(repetition, { "g1f3", "g8f6", "f3g1", "f6g8", "g1f3", "g8f6", "f3g1", "f6g8" }));
    EXPECT_EQ(repetition.Result(), Chess::Outcome::Draw);
    EXPECT_EQ(repetition.Why(), Chess::Reason::Repetition);

    Chess::Game illegal;
    EXPECT_FALSE(illegal.Play(*Chess::FromText("e2e5")));
    EXPECT_FALSE(illegal.Play(*Chess::FromText("e7e5"))) << "not black's turn";
    EXPECT_FALSE(Chess::FromText("z9a1").has_value());
    EXPECT_EQ(Chess::ToText({ 52, 60, Chess::QUEEN }), "e7e8q");

    auto stalemate = Chess::Position::FromFen("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1");
    ASSERT_TRUE(stalemate.has_value());
    EXPECT_TRUE(stalemate->Legal().empty());
    EXPECT_FALSE(stalemate->InCheck(false));
    EXPECT_TRUE(Chess::Position::FromFen("8/8/8/4k3/8/8/2B5/4K3 w - - 0 1")->InsufficientMaterial());
}

TEST(EsteriaCasinoCheckers, OpeningAndCaptures)
{
    Checkers::Game game;
    EXPECT_FALSE(game.whiteToMove) << "black moves first";
    EXPECT_EQ(game.Legal().size(), 7u);

    // Black 43-34 (d6-c5), white 20-27 (e3-d4) offers a capture black must take: 34x20.
    ASSERT_TRUE(game.Play({ 43, 34 }));
    ASSERT_TRUE(game.Play({ 20, 27 }));
    std::vector<Checkers::Path> const legal = game.Legal();
    ASSERT_EQ(legal.size(), 1u) << "the capture is compulsory";
    EXPECT_EQ(legal[0], (Checkers::Path { 34, 20 }));
    EXPECT_FALSE(game.Play({ 41, 32 })) << "a quiet move is refused while a capture exists";
    ASSERT_TRUE(game.Play({ 34, 20 }));
    EXPECT_EQ(game.board[27], 0) << "the jumped man is removed";
}

TEST(EsteriaCasinoCheckers, MultiJumpCrowningAndEnd)
{
    Checkers::Game game;
    game.board.fill(0);
    game.whiteToMove = true;
    game.board[0] = Checkers::MAN;      // a1 white man
    game.board[9] = -Checkers::MAN;     // b2 black man
    game.board[27] = -Checkers::MAN;    // d4 black man
    game.board[63] = -Checkers::MAN;    // h8 black man, keeps black alive
    std::vector<Checkers::Path> const legal = game.Legal();
    ASSERT_EQ(legal.size(), 1u);
    EXPECT_EQ(legal[0], (Checkers::Path { 0, 18, 36 })) << "a capture continues while it can";

    game.board.fill(0);
    game.board[45] = Checkers::MAN;     // f6 white man, one jump from crowning
    game.board[54] = -Checkers::MAN;    // g7
    game.board[47] = -Checkers::MAN;    // h6, keeps black alive
    ASSERT_EQ(game.Legal().size(), 1u);
    ASSERT_TRUE(game.Play({ 45, 63 }));
    EXPECT_EQ(game.board[63], Checkers::KING) << "crowned, and the move ends there";

    game.board.fill(0);
    game.whiteToMove = true;
    game.board[18] = Checkers::MAN;
    game.board[27] = -Checkers::MAN;
    ASSERT_TRUE(game.Play({ 18, 36 }));
    EXPECT_EQ(game.outcome, Checkers::Outcome::WhiteWins) << "black has nothing left to move";
}

namespace
{
    uint32_t Fixed(uint32_t) { return 0; }
}

TEST(EsteriaCasinoChessAi, FindsMateAndFreeMaterial)
{
    auto mate = Chess::Position::FromFen("6k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1");
    EXPECT_EQ(Chess::ToText(Chess::Ai::Choose(*mate, 3, 2000, Fixed, 0)), "d1d8") << "back-rank mate";
    auto queen = Chess::Position::FromFen("4k3/8/8/3q4/8/8/8/3QK3 w - - 0 1");
    EXPECT_EQ(Chess::ToText(Chess::Ai::Choose(*queen, 2, 2000, Fixed, 0)), "d1d5") << "takes the hanging queen";

    // A deep search stops on time and still answers with a legal move.
    Chess::Position const start = Chess::Position::Start();
    auto const begin = std::chrono::steady_clock::now();
    Chess::Move const m = Chess::Ai::Choose(start, 8, 300, Fixed, 0);
    auto const spent = std::chrono::steady_clock::now() - begin;
    EXPECT_LT(std::chrono::duration_cast<std::chrono::milliseconds>(spent).count(), 1500);
    bool legal = false;
    for (Chess::Move const& l : start.Legal())
        legal = legal || l == m;
    EXPECT_TRUE(legal);
}

TEST(EsteriaCasinoCheckersAi, TakesTheBiggerCapture)
{
    Checkers::Game game;
    game.board.fill(0);
    game.whiteToMove = true;
    game.board[0] = Checkers::MAN;   // can jump 9 then 27
    game.board[6] = Checkers::MAN;   // can jump 13 only
    game.board[9] = -Checkers::MAN;
    game.board[27] = -Checkers::MAN;
    game.board[13] = -Checkers::MAN;
    game.board[63] = -Checkers::MAN;
    EXPECT_EQ(Checkers::Ai::Choose(game, 4, 1000, Fixed, 0), (Checkers::Path { 0, 18, 36 }));
    Checkers::Game start;
    Checkers::Path const opening = Checkers::Ai::Choose(start, 6, 300, Fixed, 0);
    bool legal = false;
    for (Checkers::Path const& l : start.Legal())
        legal = legal || l == opening;
    EXPECT_TRUE(legal);
}
