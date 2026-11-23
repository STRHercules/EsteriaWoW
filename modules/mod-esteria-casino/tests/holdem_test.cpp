#include "Holdem.h"

#include "gtest/gtest.h"

#include <random>

using namespace EsteriaCasino::Holdem;

namespace
{
    // Cards by rank letter and suit letter, in the blackjack encoding: "AS", "TD", "2C".
    Card C(char const* code)
    {
        std::string const ranks = "A23456789TJQK", suits = "CDHS";
        return Card(suits.find(code[1]) * 13 + ranks.find(code[0]));
    }

    uint32_t Hand(std::vector<char const*> codes)
    {
        std::vector<Card> cards;
        for (char const* code : codes)
            cards.push_back(C(code));
        return Best(cards);
    }

    // A deck whose first cards are `top` (in order), then everything else.
    std::vector<Card> Deck(std::vector<char const*> top)
    {
        std::vector<Card> deck;
        for (char const* code : top)
            deck.push_back(C(code));
        for (Card c = 0; c < 52; ++c)
            if (std::find(deck.begin(), deck.end(), c) == deck.end())
                deck.push_back(c);
        return deck;
    }

    uint64_t Chips(Table const& table)
    {
        uint64_t total = 0;
        for (Seat const& s : table.seats)
            total += s.stack + s.contributed * (table.InHand() ? 1 : 0);
        return total;
    }
}

TEST(EsteriaCasinoHoldem, HandRankings)
{
    uint32_t const royal = Hand({ "AS", "KS", "QS", "JS", "TS" });
    uint32_t const quads = Hand({ "9C", "9D", "9H", "9S", "2C" });
    uint32_t const boat = Hand({ "3C", "3D", "3H", "KS", "KC" });
    uint32_t const flush = Hand({ "2H", "7H", "9H", "JH", "KH" });
    uint32_t const straight = Hand({ "5C", "6D", "7H", "8S", "9C" });
    uint32_t const wheel = Hand({ "AC", "2D", "3H", "4S", "5C" });
    uint32_t const trips = Hand({ "QC", "QD", "QH", "2S", "7C" });
    uint32_t const twoPair = Hand({ "JC", "JD", "4H", "4S", "AC" });
    uint32_t const pair = Hand({ "TC", "TD", "2H", "5S", "8C" });
    uint32_t const high = Hand({ "AC", "JD", "8H", "5S", "3C" });
    std::vector<uint32_t> const order = { royal, quads, boat, flush, straight, wheel, trips, twoPair, pair, high };
    for (size_t i = 1; i < order.size(); ++i)
        EXPECT_GT(order[i - 1], order[i]) << i;
    EXPECT_STREQ(CategoryName(wheel), "Straight");
    EXPECT_STREQ(CategoryName(royal), "Straight Flush");
    // Kickers decide equal categories; suits never do.
    EXPECT_GT(Hand({ "AC", "AD", "KH", "5S", "3C" }), Hand({ "AH", "AS", "QH", "5D", "3D" }));
    EXPECT_EQ(Hand({ "AC", "AD", "KH", "5S", "3C" }), Hand({ "AH", "AS", "KD", "5D", "3D" }));
    // Best five of seven: the board's straight beats the hole pair.
    EXPECT_EQ(Hand({ "2C", "2D", "5H", "6S", "7C", "8D", "9H" }), Hand({ "5H", "6S", "7C", "8D", "9H" }));
}

TEST(EsteriaCasinoHoldem, HeadsUpBlindsAndCap)
{
    Table table(50, 100, 0, 0);
    table.seats[0] = { 1, 10000 };
    table.seats[3] = { 2, 10000 };
    ASSERT_TRUE(table.Start(Deck({})));
    // Heads-up: the button posts the small blind and acts first before the flop.
    EXPECT_EQ(table.button, 0);
    EXPECT_EQ(table.seats[0].bet, 50u);
    EXPECT_EQ(table.seats[3].bet, 100u);
    EXPECT_EQ(table.toAct, 0);
    EXPECT_EQ(table.Legal(0), "fcr");
    EXPECT_EQ(table.Legal(3), "") << "not their turn";

    // Big blind + three raises caps the street.
    ASSERT_TRUE(table.Act(0, Action::Raise)); // 200
    ASSERT_TRUE(table.Act(3, Action::Raise)); // 300
    ASSERT_TRUE(table.Act(0, Action::Raise)); // 400, the cap
    EXPECT_EQ(table.Legal(3), "fc");
    ASSERT_TRUE(table.Act(3, Action::Call));
    EXPECT_EQ(table.street, Street::Flop);
    EXPECT_EQ(table.board.size(), 3u);
    EXPECT_EQ(table.toAct, 3) << "after the flop the big blind acts first heads-up";
    EXPECT_EQ(table.Legal(3), "fkb");
    ASSERT_TRUE(table.Act(3, Action::Bet));
    EXPECT_EQ(table.seats[3].bet, 100u) << "small bet on the flop";
    ASSERT_TRUE(table.Act(0, Action::Call));
    EXPECT_EQ(table.street, Street::Turn);
    ASSERT_TRUE(table.Act(3, Action::Bet));
    EXPECT_EQ(table.seats[3].bet, 200u) << "big bet on the turn";
    ASSERT_TRUE(table.Act(0, Action::Fold));
    EXPECT_FALSE(table.InHand());
    EXPECT_EQ(table.Last().won[3], 400u * 2 + 100u * 2 + 200u) << "the uncontested pot";
    EXPECT_EQ(table.seats[0].stack + table.seats[3].stack, 20000u);
}

TEST(EsteriaCasinoHoldem, SidePotsAndRake)
{
    // Three players all in before the flop: seat 1 short (300), seats 2 and 3 deep. Seat 1 holds the best hand,
    // seat 2 the second best: seat 1 takes the main pot, seat 2 the side pot.
    Table table(50, 100, 500, 1000); // 5% rake, capped at 1000
    table.seats[1] = { 11, 300 };
    table.seats[2] = { 12, 2000 };
    table.seats[3] = { 13, 2000 };
    table.button = 0; // the next hand's button moves to seat 1
    // Deal order from left of button (seat 2): seat2, seat3, seat1, seat2, seat3, seat1, then the board.
    ASSERT_TRUE(table.Start(Deck({ "KC", "2C", "AC", "KD", "7D", "AD", "3H", "8S", "JD", "4C", "9H" })));
    EXPECT_EQ(table.button, 1);
    // Fixed limit caps the action, so play it out: everyone calls down.
    while (table.InHand())
    {
        int const seat = table.toAct;
        std::string const legal = table.Legal(seat);
        ASSERT_FALSE(legal.empty());
        table.Act(seat, legal.find('r') != std::string::npos ? Action::Raise
                       : legal.find('b') != std::string::npos ? Action::Bet
                       : legal.find('c') != std::string::npos ? Action::Call : Action::Check);
    }
    Result const& r = table.Last();
    EXPECT_TRUE(r.showdown);
    uint64_t const short1 = 300;
    uint64_t const main = short1 * 3;
    uint64_t const side = r.pot - main;
    EXPECT_EQ(r.rake, std::min<uint64_t>(r.pot * 500 / 10000, 1000));
    EXPECT_EQ(r.won[1], main - std::min(r.rake, main)) << "aces win the main pot, which pays the rake first";
    EXPECT_EQ(r.won[2], side - (r.rake > main ? r.rake - main : 0)) << "kings win the side pot";
    EXPECT_EQ(r.won[3], 0u);
    EXPECT_EQ(table.seats[1].stack + table.seats[2].stack + table.seats[3].stack + r.rake, 4300u);
}

TEST(EsteriaCasinoHoldem, NoFlopNoRake)
{
    Table table(50, 100, 500, 1000);
    table.seats[0] = { 1, 1000 };
    table.seats[1] = { 2, 1000 };
    table.seats[2] = { 3, 1000 };
    ASSERT_TRUE(table.Start(Deck({})));
    ASSERT_TRUE(table.Act(table.toAct, Action::Fold));
    ASSERT_TRUE(table.Act(table.toAct, Action::Fold));
    EXPECT_FALSE(table.InHand());
    EXPECT_EQ(table.Last().rake, 0u);
    EXPECT_EQ(table.seats[0].stack + table.seats[1].stack + table.seats[2].stack, 3000u);
}

// Random seats, stacks and legal actions: chips are only ever moved between stacks and the rake.
TEST(EsteriaCasinoHoldem, ChipsAreConservedOverManyHands)
{
    std::mt19937 rng(7331);
    auto random = [&rng](uint32_t n) { return uint32_t(rng() % n); };
    Table table(5, 10, 500, 30);
    uint64_t total = 0;
    for (int i = 0; i < SEATS; ++i)
    {
        table.seats[i] = { uint64_t(i + 1), 50 + random(400) };
        total += table.seats[i].stack;
    }
    uint64_t raked = 0;
    for (int hand = 0; hand < 20000; ++hand)
    {
        if (table.Ready() < 2)
            for (int i = 0; i < SEATS; ++i)
                if (!table.seats[i].stack)
                {
                    table.seats[i].stack = 100; // a rebuy
                    total += 100;
                }
        ASSERT_TRUE(table.Start(Shuffled(random)));
        int guard = 0;
        while (table.InHand())
        {
            ASSERT_LT(++guard, 200);
            int const seat = table.toAct;
            std::string const legal = table.Legal(seat);
            ASSERT_FALSE(legal.empty());
            char const pick = legal[random(uint32_t(legal.size()))];
            ASSERT_TRUE(table.Act(seat, Action(std::string("fkcbr").find(pick))));
            if (table.InHand())
            {
                ASSERT_EQ(Chips(table) + raked, total);
            }
        }
        raked += table.Last().rake;
        ASSERT_EQ(Chips(table) + raked, total);
    }
}

TEST(EsteriaCasinoHoldem, BotEquityAndChoices)
{
    std::mt19937 rng(99);
    auto random = [&rng](uint32_t n) { return uint32_t(rng() % n); };
    double const aces = Bot::Equity({ C("AS"), C("AH") }, {}, 1, 3000, random);
    double const junk = Bot::Equity({ C("7C"), C("2D") }, {}, 1, 3000, random);
    EXPECT_TRUE(aces > 0.80 && aces < 0.90) << aces;
    EXPECT_TRUE(junk > 0.28 && junk < 0.42) << junk;
    EXPECT_EQ(Bot::Equity({ C("AS"), C("AH") }, {}, 0, 10, random), 1.0);

    // Heads-up, seat 0 on the button holds aces and acts first: it raises.
    Table table(50, 100, 0, 0);
    table.seats[0] = { 1, 10000 };
    table.seats[3] = { 2, 10000 };
    ASSERT_TRUE(table.Start(Deck({ "KD", "AS", "7C", "AH" })));
    ASSERT_EQ(table.toAct, 0);
    EXPECT_EQ(Bot::Decide(table, 0, random), Action::Raise);
}

// A table of house players runs itself: every decision is legal and no chip is created or lost.
TEST(EsteriaCasinoHoldem, BotsPlayLegallyAndConserveChips)
{
    std::mt19937 rng(4242);
    auto random = [&rng](uint32_t n) { return uint32_t(rng() % n); };
    Table table(5, 10, 500, 30);
    uint64_t total = 0;
    for (int i = 0; i < 4; ++i)
    {
        table.seats[i] = { uint64_t(i + 1), 400 };
        total += 400;
    }
    uint64_t raked = 0;
    for (int hand = 0; hand < 300 && table.Ready() >= 2; ++hand)
    {
        ASSERT_TRUE(table.Start(Shuffled(random)));
        int guard = 0;
        while (table.InHand())
        {
            ASSERT_LT(++guard, 200);
            ASSERT_TRUE(table.Act(table.toAct, Bot::Decide(table, table.toAct, random, 30)));
        }
        raked += table.Last().rake;
        ASSERT_EQ(Chips(table) + raked, total);
    }
}
