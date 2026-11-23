#include "Blackjack.h"
#include "CasinoHouse.h"
#include "Dice.h"
#include "Slots.h"

#include "gtest/gtest.h"

#include <algorithm>
#include <random>

using namespace EsteriaCasino;
using namespace EsteriaCasino::Blackjack;

namespace
{
    // Cards by rank index (suit clubs): 0 ace, 9 ten, 12 king.
    constexpr Card A = 0, C2 = 1, C5 = 4, C6 = 5, C7 = 6, C8 = 7, C9 = 8, T = 9, K = 12;

    // A one-deck shoe that deals `order` first (cards must be distinct). The shuffle's random picks, for each
    // position from the back, whichever index holds the card wanted there; `deck` mirrors the shoe's swaps.
    Shoe Stacked(std::vector<Card> order)
    {
        Shoe shoe(1);
        std::vector<Card> deck(52);
        for (Card c = 0; c < 52; ++c)
            deck[c] = c;
        std::vector<Card> wanted = order;
        for (Card c = 0; c < 52; ++c)
            if (std::find(order.begin(), order.end(), c) == order.end())
                wanted.push_back(c);
        shoe.Shuffle([&deck, &wanted](uint32_t n)
        {
            size_t const i = n - 1;
            size_t const j = size_t(std::find(deck.begin(), deck.begin() + n, wanted[i]) - deck.begin());
            std::swap(deck[i], deck[j]);
            return uint32_t(j);
        });
        return shoe;
    }
}

TEST(EsteriaCasinoBlackjack, SoftAndHardTotals)
{
    EXPECT_EQ(Evaluate({ A, C6 }).value, 17);
    EXPECT_TRUE(Evaluate({ A, C6 }).soft);
    EXPECT_EQ(Evaluate({ A, C6, T }).value, 17);
    EXPECT_FALSE(Evaluate({ A, C6, T }).soft);
    EXPECT_EQ(Evaluate({ A, A, C9 }).value, 21);
    EXPECT_EQ(Evaluate({ K, T, C2 }).value, 22);
    EXPECT_EQ(Code(A + 39), "AS");
    EXPECT_EQ(Code(T + 13), "TD");
}

TEST(EsteriaCasinoBlackjack, ShoeHoldsEveryCardOncePerDeck)
{
    std::mt19937 rng(7);
    Shoe shoe(6);
    shoe.Shuffle([&rng](uint32_t n) { return uint32_t(rng() % n); });
    std::vector<int> seen(52, 0);
    while (shoe.Remaining())
        ++seen[shoe.Draw()];
    EXPECT_EQ(std::count(seen.begin(), seen.end(), 6), 52);
}

TEST(EsteriaCasinoBlackjack, NaturalPaysThreeToTwo)
{
    // Deal order: player, dealer, player, dealer.
    Shoe shoe = Stacked({ A, C9, K + 13, C7 });
    Round round(false);
    round.Start(shoe, 101);
    ASSERT_TRUE(round.Finished());
    EXPECT_EQ(round.OutcomeOf(round.Hands()[0]), Outcome::Blackjack);
    EXPECT_EQ(round.Paid(), 101u + 151u); // 3:2 rounds down to the copper
}

TEST(EsteriaCasinoBlackjack, DealerBlackjackTakesOnlyTheOpeningStake)
{
    Shoe shoe = Stacked({ T, A, C9, K });
    Round round(false);
    round.Start(shoe, 100);
    ASSERT_TRUE(round.Finished());
    EXPECT_FALSE(round.CanDouble());
    EXPECT_EQ(round.Paid(), 0u);
    EXPECT_EQ(round.Wagered(), 100u);
}

TEST(EsteriaCasinoBlackjack, DealerSoft17RuleIsHonoured)
{
    // Player 10+8 stands; dealer A+6 is soft 17, then draws a 2 only when hitting soft 17.
    for (bool h17 : { false, true })
    {
        Shoe shoe = Stacked({ T, A, C8, C6, C2 });
        Round round(h17);
        round.Start(shoe, 100);
        ASSERT_TRUE(round.Stand(shoe));
        ASSERT_TRUE(round.Finished());
        EXPECT_EQ(Evaluate(round.Dealer()).value, h17 ? 19 : 17);
        EXPECT_EQ(round.Paid(), h17 ? 0u : 200u);
    }
}

TEST(EsteriaCasinoBlackjack, DoubleDrawsOneCardAndDoublesTheStake)
{
    Shoe shoe = Stacked({ C5, T, C6, C7, T + 13, C8 });
    Round round(false);
    round.Start(shoe, 100);
    ASSERT_TRUE(round.CanDouble());
    EXPECT_EQ(round.ExtraStake(), 100u);
    ASSERT_TRUE(round.Double(shoe)); // 5+6+10 = 21; dealer 10+7 stands
    ASSERT_TRUE(round.Finished());
    EXPECT_EQ(round.Wagered(), 200u);
    EXPECT_EQ(round.Paid(), 400u);
}

TEST(EsteriaCasinoBlackjack, SplitAcesTakeOneCardAndAreNotBlackjack)
{
    Shoe shoe = Stacked({ A, C9, A + 13, C8, K, K + 13 });
    Round round(false);
    round.Start(shoe, 100);
    ASSERT_TRUE(round.CanSplit());
    ASSERT_TRUE(round.Split(shoe));
    ASSERT_TRUE(round.Finished());
    ASSERT_EQ(round.Hands().size(), 2u);
    for (Hand const& hand : round.Hands())
        EXPECT_EQ(round.OutcomeOf(hand), Outcome::Win); // 21 vs 17: a win, not a 3:2 blackjack
    EXPECT_EQ(round.Wagered(), 200u);
    EXPECT_EQ(round.Paid(), 400u);
}

TEST(EsteriaCasinoHouse, MaxBetCoversTheWorstCase)
{
    House house;
    house.bankroll = 1000;
    EXPECT_EQ(house.MaxBet(MaxHouseLossMultiplier, 10000), 250u);
    EXPECT_EQ(house.MaxBet(MaxHouseLossMultiplier, 100), 100u);
    ASSERT_TRUE(house.Reserve(800));
    EXPECT_EQ(house.MaxBet(MaxHouseLossMultiplier, 10000), 50u);
    EXPECT_FALSE(house.Reserve(201));
    house.bankroll = -5;
    EXPECT_EQ(house.Available(), 0u);
}

// Plays many random rounds with random legal actions. Copper is never created or lost, and the house never loses
// more than it reserved for a round.
TEST(EsteriaCasinoHouse, CopperIsConservedOverManyRounds)
{
    std::mt19937 rng(20261121);
    auto random = [&rng](uint32_t n) { return uint32_t(rng() % n); };

    House house;
    house.bankroll = 50000000;
    int64_t player = 1000000000; // random play loses fast; the player must never run dry
    int64_t const total = house.bankroll + player;

    Shoe shoe(6);
    for (int i = 0; i < 100000; ++i)
    {
        if (shoe.NeedsShuffle())
            shoe.Shuffle(random);
        uint64_t const stake = 1 + random(uint32_t(std::min<uint64_t>(house.MaxBet(MaxHouseLossMultiplier, 5000),
            uint64_t(player) / 4)));
        uint64_t const worst = stake * MaxHouseLossMultiplier;
        ASSERT_TRUE(house.Reserve(worst));
        player -= int64_t(stake);

        Round round(i % 2 == 0);
        round.Start(shoe, stake);
        while (!round.Finished())
        {
            uint32_t const pick = random(4);
            if (pick == 0 && round.CanSplit())
            {
                player -= int64_t(round.ExtraStake());
                round.Split(shoe);
            }
            else if (pick == 1 && round.CanDouble())
            {
                player -= int64_t(round.ExtraStake());
                round.Double(shoe);
            }
            else if (pick == 2)
                round.Hit(shoe);
            else
                round.Stand(shoe);
        }

        ASSERT_LE(round.Wagered(), stake * 4);
        int64_t const delta = house.Settle(worst, round.Wagered(), round.Paid());
        ASSERT_GE(delta, -int64_t(worst));
        player += int64_t(round.Paid());
        ASSERT_EQ(house.bankroll + player, total);
    }
    EXPECT_EQ(house.reserved, 0u);
}

TEST(EsteriaCasinoSlots, PayTableAndReturn)
{
    EXPECT_EQ(Slots::TotalWeight(), 32u);
    EXPECT_EQ(Slots::Pay(5, 5, 5), 500u);
    EXPECT_EQ(Slots::Pay(0, 0, 0), 4u);
    EXPECT_EQ(Slots::Pay(0, 1, 2), 1u); // any three coins: stake back
    EXPECT_EQ(Slots::Pay(0, 1, 3), 0u);
    EXPECT_EQ(Slots::Pay(4, 4, 3), 0u);
    // Published return: 31936 of 32768 weighted lines' worth of stakes.
    EXPECT_EQ(Slots::ReturnBasisPoints(), 9746u);
    for (uint32_t pay : Slots::TriplePay)
        EXPECT_LE(pay, Slots::MaxPay);

    std::array<uint32_t, Slots::SymbolCount> hits {};
    for (uint32_t roll = 0; roll < Slots::TotalWeight(); ++roll)
        ++hits[Slots::Symbol(roll)];
    for (size_t i = 0; i < Slots::SymbolCount; ++i)
        EXPECT_EQ(hits[i], Slots::Weights[i]);
}

TEST(EsteriaCasinoDice, CallsAndReturns)
{
    using Dice::Call;
    EXPECT_TRUE(Dice::Wins(Call::Under, 1, 5));
    EXPECT_FALSE(Dice::Wins(Call::Under, 3, 4));
    EXPECT_TRUE(Dice::Wins(Call::Seven, 3, 4));
    EXPECT_TRUE(Dice::Wins(Call::Over, 6, 2));
    EXPECT_TRUE(Dice::Wins(Call::Doubles, 2, 2));
    EXPECT_EQ(Dice::Paid(1000, Call::Under, 1, 1), 2330u);
    EXPECT_EQ(Dice::Paid(1001, Call::Seven, 1, 6), 5805u); // rounded down to the copper
    EXPECT_EQ(Dice::Paid(1000, Call::Over, 1, 1), 0u);
    EXPECT_EQ(Dice::CallReturnBasisPoints(Call::Under), 9708u);
    EXPECT_EQ(Dice::CallReturnBasisPoints(Call::Over), 9708u);
    EXPECT_EQ(Dice::CallReturnBasisPoints(Call::Seven), 9666u);
    EXPECT_EQ(Dice::CallReturnBasisPoints(Call::Doubles), 9666u);
    for (uint32_t bp : Dice::ReturnBasisPoints)
        EXPECT_LE(bp - 10000, Dice::MaxHouseLossMultiplier * 10000);
}
