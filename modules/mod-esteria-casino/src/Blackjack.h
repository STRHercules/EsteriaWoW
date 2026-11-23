/* Blackjack rules, kept free of game types so they can be unit tested.
 *
 * Rules: 6-deck shoe, dealer peeks for blackjack, blackjack pays 3:2 (rounded down to the copper), double on any
 * first two cards except split aces, one split of equal-point cards, split aces get one card each, and a 21 after a
 * split is not a blackjack. The dealer hits soft 17 when `hitSoft17` is set.
 */
#ifndef ESTERIA_CASINO_BLACKJACK_H
#define ESTERIA_CASINO_BLACKJACK_H

#include <cstdint>
#include <functional>
#include <string>
#include <utility>
#include <vector>

namespace EsteriaCasino::Blackjack
{
    // 0..51: rank = card % 13 (0 ace, 1..8 two..nine, 9 ten, 10..12 jack..king), suit = card / 13 (C, D, H, S).
    using Card = uint8_t;

    // Largest net amount the house can lose on one round, as a multiple of the opening stake: split and double both
    // hands, win both.
    constexpr uint32_t MaxHouseLossMultiplier = 4;

    inline uint8_t Points(Card card)
    {
        uint8_t const rank = card % 13;
        return rank == 0 ? 1 : rank >= 9 ? 10 : rank + 1;
    }

    // Two-character code the addon draws: rank then suit, e.g. "AS", "TD".
    inline std::string Code(Card card)
    {
        return { "A23456789TJQK"[card % 13], "CDHS"[card / 13] };
    }

    struct Total
    {
        uint8_t value;
        bool soft; // an ace counts as 11
    };

    inline Total Evaluate(std::vector<Card> const& cards)
    {
        uint32_t sum = 0;
        bool ace = false;
        for (Card card : cards)
        {
            sum += Points(card);
            ace = ace || Points(card) == 1;
        }
        if (ace && sum + 10 <= 21)
            return { uint8_t(sum + 10), true };
        return { uint8_t(sum), false };
    }

    // Uniform in [0, n); the server passes a CSPRNG, tests pass a seeded generator.
    using RandomBelow = std::function<uint32_t(uint32_t n)>;

    class Shoe
    {
    public:
        explicit Shoe(uint32_t decks = 6) : _decks(decks) { }

        void Shuffle(RandomBelow const& random)
        {
            _cards.clear();
            for (uint32_t d = 0; d < _decks; ++d)
                for (Card c = 0; c < 52; ++c)
                    _cards.push_back(c);
            for (size_t i = _cards.size() - 1; i > 0; --i)
                std::swap(_cards[i], _cards[random(uint32_t(i + 1))]);
            _next = 0;
        }

        // Reshuffle between rounds once three quarters are dealt; a round never needs more than ~25 cards.
        bool NeedsShuffle() const { return _cards.empty() || _next * 4 >= _cards.size() * 3; }
        Card Draw() { return _cards[_next++]; }
        size_t Remaining() const { return _cards.size() - _next; }

    private:
        uint32_t _decks;
        std::vector<Card> _cards;
        size_t _next = 0;
    };

    enum class Outcome : uint8_t
    {
        Lose,
        Push,
        Win,
        Blackjack,
    };

    struct Hand
    {
        std::vector<Card> cards;
        uint64_t stake = 0;
        bool fromSplit = false;
        bool doubled = false;
        bool done = false;

        bool IsBlackjack() const { return !fromSplit && cards.size() == 2 && Evaluate(cards).value == 21; }
        bool IsBust() const { return Evaluate(cards).value > 21; }
    };

    class Round
    {
    public:
        explicit Round(bool hitSoft17) : _hitSoft17(hitSoft17) { }

        // Deals player, dealer, player, dealer. A blackjack on either side ends the round at once.
        void Start(Shoe& shoe, uint64_t stake)
        {
            _hands.assign(1, Hand { {}, stake });
            _dealer.clear();
            _active = 0;
            _finished = false;
            _hands[0].cards.push_back(shoe.Draw());
            _dealer.push_back(shoe.Draw());
            _hands[0].cards.push_back(shoe.Draw());
            _dealer.push_back(shoe.Draw());

            if (_hands[0].IsBlackjack() || DealerBlackjack())
            {
                _hands[0].done = true;
                _finished = true;
            }
        }

        bool CanHit() const { return !_finished; }
        bool CanStand() const { return !_finished; }

        bool CanDouble() const
        {
            if (_finished)
                return false;
            Hand const& hand = _hands[_active];
            return hand.cards.size() == 2 && !(hand.fromSplit && Points(hand.cards[0]) == 1);
        }

        bool CanSplit() const
        {
            if (_finished || _hands.size() != 1)
                return false;
            Hand const& hand = _hands[0];
            return hand.cards.size() == 2 && Points(hand.cards[0]) == Points(hand.cards[1]);
        }

        // The stake the caller must collect before Double or Split.
        uint64_t ExtraStake() const { return _hands[_active].stake; }

        bool Hit(Shoe& shoe)
        {
            if (!CanHit())
                return false;
            Hand& hand = _hands[_active];
            hand.cards.push_back(shoe.Draw());
            if (Evaluate(hand.cards).value >= 21)
                FinishHand(shoe);
            return true;
        }

        bool Stand(Shoe& shoe)
        {
            if (!CanStand())
                return false;
            FinishHand(shoe);
            return true;
        }

        bool Double(Shoe& shoe)
        {
            if (!CanDouble())
                return false;
            Hand& hand = _hands[_active];
            hand.stake *= 2;
            hand.doubled = true;
            hand.cards.push_back(shoe.Draw());
            FinishHand(shoe);
            return true;
        }

        bool Split(Shoe& shoe)
        {
            if (!CanSplit())
                return false;
            Hand second { { _hands[0].cards[1] }, _hands[0].stake, true };
            _hands[0].cards.pop_back();
            _hands[0].fromSplit = true;
            _hands.push_back(second);
            _hands[0].cards.push_back(shoe.Draw());
            _hands[1].cards.push_back(shoe.Draw());

            if (Points(_hands[0].cards[0]) == 1)
            {
                // Split aces take one card each and stand.
                _hands[0].done = _hands[1].done = true;
                _active = 1;
                FinishHand(shoe);
            }
            else if (Evaluate(_hands[0].cards).value == 21)
                FinishHand(shoe);
            return true;
        }

        // Ends the round as if the player stood on every open hand (disconnect, logout).
        void StandAll(Shoe& shoe)
        {
            while (!_finished)
                FinishHand(shoe);
        }

        Outcome OutcomeOf(Hand const& hand) const
        {
            if (hand.IsBust())
                return Outcome::Lose;
            bool const dealerBlackjack = DealerBlackjack();
            if (hand.IsBlackjack())
                return dealerBlackjack ? Outcome::Push : Outcome::Blackjack;
            if (dealerBlackjack)
                return Outcome::Lose;
            uint8_t const player = Evaluate(hand.cards).value;
            uint8_t const dealer = Evaluate(_dealer).value;
            if (dealer > 21 || player > dealer)
                return Outcome::Win;
            return player == dealer ? Outcome::Push : Outcome::Lose;
        }

        // Copper handed back to the player for one hand, stake included.
        static uint64_t Return(Hand const& hand, Outcome outcome)
        {
            switch (outcome)
            {
                case Outcome::Blackjack: return hand.stake + hand.stake * 3 / 2;
                case Outcome::Win: return hand.stake * 2;
                case Outcome::Push: return hand.stake;
                default: return 0;
            }
        }

        uint64_t Wagered() const
        {
            uint64_t total = 0;
            for (Hand const& hand : _hands)
                total += hand.stake;
            return total;
        }

        uint64_t Paid() const
        {
            uint64_t total = 0;
            for (Hand const& hand : _hands)
                total += Return(hand, OutcomeOf(hand));
            return total;
        }

        bool Finished() const { return _finished; }
        size_t Active() const { return _active; }
        std::vector<Hand> const& Hands() const { return _hands; }
        std::vector<Card> const& Dealer() const { return _dealer; }

    private:
        bool DealerBlackjack() const { return _dealer.size() == 2 && Evaluate(_dealer).value == 21; }

        void FinishHand(Shoe& shoe)
        {
            _hands[_active].done = true;
            while (_active < _hands.size() && _hands[_active].done)
                ++_active;
            if (_active < _hands.size())
            {
                // A split hand that already holds 21 stands on its own.
                if (Evaluate(_hands[_active].cards).value == 21)
                    FinishHand(shoe);
                return;
            }

            _active = _hands.size() - 1;
            _finished = true;
            bool anyLive = false;
            for (Hand const& hand : _hands)
                anyLive = anyLive || !hand.IsBust();
            if (!anyLive)
                return;
            for (;;)
            {
                Total const total = Evaluate(_dealer);
                if (total.value > 17 || (total.value == 17 && !(total.soft && _hitSoft17)))
                    break;
                _dealer.push_back(shoe.Draw());
            }
        }

        bool _hitSoft17;
        std::vector<Hand> _hands;
        std::vector<Card> _dealer;
        size_t _active = 0;
        bool _finished = false;
    };
}

#endif
