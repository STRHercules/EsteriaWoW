/* Fixed-limit Texas Hold'em for up to six seats, kept free of game types so it can be unit tested.
 *
 * Cards use the blackjack encoding (Blackjack.h): rank = card % 13 with 0 the ace, suit = card / 13. Bets come in
 * two sizes: the big blind before the turn, twice it on the turn and river; a street allows one bet and three raises
 * (the big blind counts as the first bet before the flop). A player who can't cover a full raise may still call,
 * all-in if short. Side pots split by contribution. The rake is a share of the pot, capped, and taken only when the
 * hand saw a flop.
 */
#ifndef ESTERIA_CASINO_HOLDEM_H
#define ESTERIA_CASINO_HOLDEM_H

#include <algorithm>
#include <array>
#include <cstdint>
#include <functional>
#include <string>
#include <vector>

namespace EsteriaCasino::Holdem
{
    using Card = uint8_t;
    constexpr int SEATS = 6;
    constexpr int MAX_BETS = 4; // a bet and three raises per street

    inline int Value(Card c) { return c % 13 == 0 ? 14 : c % 13 + 1; } // 2..14
    inline int Suit(Card c) { return c / 13; }

    // Comparable strength of exactly five cards: category in the top bits, then the deciding ranks.
    inline uint32_t Evaluate5(std::array<Card, 5> const& cards)
    {
        std::array<int, 15> count {};
        bool flush = true;
        for (Card c : cards)
        {
            ++count[Value(c)];
            flush = flush && Suit(c) == Suit(cards[0]);
        }
        // Ranks ordered by (count, rank), highest first.
        std::vector<std::pair<int, int>> groups;
        for (int v = 14; v >= 2; --v)
            if (count[v])
                groups.push_back({ count[v], v });
        std::stable_sort(groups.begin(), groups.end(), [](auto const& a, auto const& b) { return a.first > b.first; });

        int straightHigh = 0;
        if (groups.size() == 5)
        {
            if (groups[0].second - groups[4].second == 4)
                straightHigh = groups[0].second;
            else if (groups[0].second == 14 && groups[1].second == 5)
                straightHigh = 5; // the wheel: A-2-3-4-5
        }

        uint32_t category;
        if (straightHigh && flush)
            category = 8;
        else if (groups[0].first == 4)
            category = 7;
        else if (groups[0].first == 3 && groups[1].first == 2)
            category = 6;
        else if (flush)
            category = 5;
        else if (straightHigh)
            category = 4;
        else if (groups[0].first == 3)
            category = 3;
        else if (groups[0].first == 2 && groups[1].first == 2)
            category = 2;
        else if (groups[0].first == 2)
            category = 1;
        else
            category = 0;

        uint32_t value = category << 20;
        if (straightHigh)
            return value | uint32_t(straightHigh) << 16;
        int shift = 16;
        for (auto const& g : groups)
        {
            value |= uint32_t(g.second) << shift;
            shift -= 4;
        }
        return value;
    }

    // Best five of five to seven cards.
    inline uint32_t Best(std::vector<Card> const& cards)
    {
        uint32_t best = 0;
        size_t const n = cards.size();
        for (size_t a = 0; a < n; ++a)
            for (size_t b = a + 1; b < n; ++b)
                for (size_t c = b + 1; c < n; ++c)
                    for (size_t d = c + 1; d < n; ++d)
                        for (size_t e = d + 1; e < n; ++e)
                            best = std::max(best, Evaluate5({ cards[a], cards[b], cards[c], cards[d], cards[e] }));
        return best;
    }

    inline char const* CategoryName(uint32_t value)
    {
        static char const* names[] = { "High Card", "Pair", "Two Pair", "Three of a Kind", "Straight", "Flush",
                                       "Full House", "Four of a Kind", "Straight Flush" };
        return names[std::min<uint32_t>(value >> 20, 8)];
    }

    using RandomBelow = std::function<uint32_t(uint32_t)>;

    inline std::vector<Card> Shuffled(RandomBelow const& random)
    {
        std::vector<Card> deck(52);
        for (Card c = 0; c < 52; ++c)
            deck[c] = c;
        for (size_t i = deck.size() - 1; i > 0; --i)
            std::swap(deck[i], deck[random(uint32_t(i + 1))]);
        return deck;
    }

    enum class Street : uint8_t
    {
        Idle,
        Preflop,
        Flop,
        Turn,
        River,
    };

    enum class Action : uint8_t
    {
        Fold,
        Check,
        Call,
        Bet,
        Raise,
    };

    struct Seat
    {
        uint64_t id = 0; // 0 when empty
        uint64_t stack = 0;
        uint64_t bet = 0;          // this street
        uint64_t contributed = 0;  // this hand
        bool inHand = false;
        bool folded = false;
        bool allIn = false;
        bool acted = false;
        std::array<Card, 2> hole {};
    };

    struct Result
    {
        std::array<uint64_t, SEATS> won {};
        std::array<uint32_t, SEATS> value {}; // hand strength of every player at showdown, else 0
        uint64_t pot = 0;
        uint64_t rake = 0;
        bool showdown = false;
    };

    class Table
    {
    public:
        Table(uint64_t smallBlind, uint64_t bigBlind, uint32_t rakeBasisPoints, uint64_t rakeCap)
            : _small(smallBlind), _big(bigBlind), _rakeBp(rakeBasisPoints), _rakeCap(rakeCap) { }

        std::array<Seat, SEATS> seats {};
        std::vector<Card> board;
        Street street = Street::Idle;
        int button = -1;
        int toAct = -1;
        uint64_t currentBet = 0;
        int bets = 0;
        uint64_t handNumber = 0;

        uint64_t BigBlind() const { return _big; }
        uint64_t SmallBlind() const { return _small; }
        uint64_t BetSize() const { return street == Street::Turn || street == Street::River ? _big * 2 : _big; }
        Result const& Last() const { return _last; }
        bool InHand() const { return street != Street::Idle; }

        uint64_t Pot() const
        {
            uint64_t pot = 0;
            for (Seat const& s : seats)
                pot += s.contributed;
            return pot;
        }

        int Ready() const
        {
            int n = 0;
            for (Seat const& s : seats)
                n += (s.id && s.stack > 0) ? 1 : 0;
            return n;
        }

        // Deals a hand from `deck` (top card first) when two or more seated players have chips.
        bool Start(std::vector<Card> deck)
        {
            if (InHand() || Ready() < 2)
                return false;
            _deck = std::move(deck);
            _next = 0;
            board.clear();
            _last = Result();
            ++handNumber;
            for (Seat& s : seats)
            {
                s.bet = s.contributed = 0;
                s.folded = s.allIn = s.acted = false;
                s.inHand = s.id && s.stack > 0;
            }
            button = NextIn(button);
            bool const headsUp = Ready() == 2;
            int const sb = headsUp ? button : NextIn(button);
            int const bb = NextIn(sb);
            Post(sb, _small);
            Post(bb, _big);
            for (int round = 0; round < 2; ++round)
                for (int i = 1, seat = button; i <= SEATS; ++i)
                {
                    seat = (button + i) % SEATS;
                    if (seats[seat].inHand)
                        seats[seat].hole[round] = _deck[_next++];
                }
            street = Street::Preflop;
            currentBet = _big;
            bets = 1;
            toAct = NextToAct(bb);
            if (toAct < 0)
                FinishStreet();
            return true;
        }

        uint64_t CallAmount(int seat) const
        {
            Seat const& s = seats[seat];
            return std::min(s.stack, currentBet > s.bet ? currentBet - s.bet : 0);
        }

        // Letters of the actions `seat` may take now: f fold, k check, c call, b bet, r raise.
        std::string Legal(int seat) const
        {
            if (!InHand() || seat != toAct)
                return "";
            Seat const& s = seats[seat];
            std::string out = "f";
            if (s.bet >= currentBet)
                out += 'k';
            else
                out += 'c';
            if (bets < MAX_BETS)
            {
                uint64_t const need = (currentBet - std::min(currentBet, s.bet)) + BetSize();
                if (s.stack > need || (s.stack == need && need > 0))
                    out += currentBet == 0 ? 'b' : 'r';
            }
            return out;
        }

        bool Act(int seat, Action action)
        {
            char const letter = "fkcbr"[int(action)];
            if (Legal(seat).find(letter) == std::string::npos)
                return false;
            Seat& s = seats[seat];
            switch (action)
            {
                case Action::Fold:
                    s.folded = true;
                    break;
                case Action::Check:
                    break;
                case Action::Call:
                    Put(seat, CallAmount(seat));
                    break;
                case Action::Bet:
                case Action::Raise:
                    currentBet += BetSize();
                    Put(seat, currentBet - s.bet);
                    ++bets;
                    for (int i = 0; i < SEATS; ++i)
                        if (i != seat)
                            seats[i].acted = false;
                    break;
            }
            s.acted = true;

            if (Live() == 1)
            {
                Award();
                return true;
            }
            toAct = NextToAct(seat);
            if (toAct < 0)
                FinishStreet();
            return true;
        }

        // The timeout default: check when free, otherwise fold.
        Action Default(int seat) const
        {
            return Legal(seat).find('k') != std::string::npos ? Action::Check : Action::Fold;
        }

    private:
        int NextIn(int from) const
        {
            for (int i = 1; i <= SEATS; ++i)
            {
                int const seat = ((from < 0 ? -1 : from) + i + SEATS) % SEATS;
                if (seats[seat].inHand || (street == Street::Idle && seats[seat].id && seats[seat].stack > 0))
                    return seat;
            }
            return -1;
        }

        void Put(int seat, uint64_t amount)
        {
            Seat& s = seats[seat];
            amount = std::min(amount, s.stack);
            s.stack -= amount;
            s.bet += amount;
            s.contributed += amount;
            if (!s.stack)
                s.allIn = true;
        }

        void Post(int seat, uint64_t blind) { Put(seat, blind); }

        int Live() const
        {
            int n = 0;
            for (Seat const& s : seats)
                n += (s.inHand && !s.folded) ? 1 : 0;
            return n;
        }

        bool CanAct(Seat const& s) const { return s.inHand && !s.folded && !s.allIn; }

        // The next seat after `from` that still owes an action this street, or -1 when the street is done.
        int NextToAct(int from) const
        {
            int actors = 0;
            for (Seat const& s : seats)
                actors += CanAct(s) ? 1 : 0;
            for (int i = 1; i <= SEATS; ++i)
            {
                int const seat = (from + i) % SEATS;
                Seat const& s = seats[seat];
                if (!CanAct(s))
                    continue;
                // A lone player facing no bet (everyone else all-in) has nothing to decide.
                if (actors == 1 && s.bet >= currentBet)
                    return -1;
                if (!s.acted || s.bet < currentBet)
                    return seat;
            }
            return -1;
        }

        void FinishStreet()
        {
            for (;;)
            {
                if (street == Street::River)
                {
                    Award();
                    return;
                }
                for (Seat& s : seats)
                {
                    s.bet = 0;
                    s.acted = false;
                }
                currentBet = 0;
                bets = 0;
                int const deal = street == Street::Preflop ? 3 : 1;
                for (int i = 0; i < deal; ++i)
                    board.push_back(_deck[_next++]);
                street = Street(int(street) + 1);
                toAct = NextToAct(button);
                if (toAct >= 0)
                    return; // betting continues; otherwise the board runs out
            }
        }

        void Award()
        {
            Result r;
            r.pot = Pot();
            bool const flopSeen = !board.empty();
            r.rake = flopSeen ? std::min<uint64_t>(r.pot * _rakeBp / 10000, _rakeCap) : 0;
            r.showdown = Live() > 1;
            if (r.showdown)
                for (int i = 0; i < SEATS; ++i)
                    if (seats[i].inHand && !seats[i].folded)
                    {
                        std::vector<Card> cards(board);
                        cards.push_back(seats[i].hole[0]);
                        cards.push_back(seats[i].hole[1]);
                        r.value[i] = Best(cards);
                    }

            // Layers of the pot by contribution level; each goes to the best live hand that paid into it.
            std::vector<uint64_t> levels;
            for (Seat const& s : seats)
                if (s.inHand && s.contributed)
                    levels.push_back(s.contributed);
            std::sort(levels.begin(), levels.end());
            levels.erase(std::unique(levels.begin(), levels.end()), levels.end());
            uint64_t previous = 0, rake = r.rake, carry = 0;
            std::vector<int> lastWinners;
            for (uint64_t level : levels)
            {
                uint64_t layer = carry;
                std::vector<int> eligible;
                for (int i = 0; i < SEATS; ++i)
                {
                    Seat const& s = seats[i];
                    if (!s.inHand)
                        continue;
                    layer += std::min(s.contributed, level) - std::min(s.contributed, previous);
                    if (!s.folded && s.contributed >= level)
                        eligible.push_back(i);
                }
                previous = level;
                uint64_t const taken = std::min(rake, layer);
                rake -= taken;
                layer -= taken;
                if (eligible.empty())
                {
                    carry = layer;
                    continue;
                }
                carry = 0;
                uint32_t best = 0;
                for (int i : eligible)
                    best = std::max(best, r.value[i]);
                std::vector<int> winners;
                for (int k = 1; k <= SEATS; ++k) // odd chips go first to the left of the button
                {
                    int const i = (button + k) % SEATS;
                    if (std::find(eligible.begin(), eligible.end(), i) != eligible.end() && r.value[i] == best)
                        winners.push_back(i);
                }
                for (size_t w = 0; w < winners.size(); ++w)
                    r.won[winners[w]] += layer / winners.size() + (w < layer % winners.size() ? 1 : 0);
                lastWinners = winners;
            }
            if (carry && !lastWinners.empty())
                r.won[lastWinners[0]] += carry;

            for (int i = 0; i < SEATS; ++i)
            {
                seats[i].stack += r.won[i];
                seats[i].bet = 0;
                seats[i].acted = false;
            }
            _last = r;
            street = Street::Idle;
            toAct = -1;
            currentBet = 0;
        }

        uint64_t _small, _big;
        uint32_t _rakeBp;
        uint64_t _rakeCap;
        std::vector<Card> _deck;
        size_t _next = 0;
        Result _last;
    };
    // The house player: its hand's equity against every live opponent, by Monte Carlo over the unseen cards,
    // weighed against the price of calling. It raises strength, calls when the pot pays for it, checks when free,
    // and bluffs a little when nobody has bet.
    namespace Bot
    {
        inline double Equity(std::array<Card, 2> const& hole, std::vector<Card> const& board, int opponents, int trials,
            RandomBelow const& random)
        {
            if (opponents <= 0)
                return 1.0;
            std::vector<Card> deck;
            for (Card c = 0; c < 52; ++c)
                if (c != hole[0] && c != hole[1] && std::find(board.begin(), board.end(), c) == board.end())
                    deck.push_back(c);
            size_t const missing = 5 - board.size();
            size_t const need = missing + 2 * size_t(opponents);
            double won = 0;
            for (int t = 0; t < trials; ++t)
            {
                for (size_t i = 0; i < need; ++i)
                    std::swap(deck[i], deck[i + random(uint32_t(deck.size() - i))]);
                std::vector<Card> cards(board);
                cards.insert(cards.end(), deck.begin(), deck.begin() + missing);
                std::vector<Card> mine(cards);
                mine.push_back(hole[0]);
                mine.push_back(hole[1]);
                uint32_t const value = Best(mine);
                int ties = 0;
                bool lost = false;
                for (int o = 0; o < opponents && !lost; ++o)
                {
                    std::vector<Card> theirs(cards);
                    theirs.push_back(deck[missing + 2 * o]);
                    theirs.push_back(deck[missing + 2 * o + 1]);
                    uint32_t const other = Best(theirs);
                    lost = other > value;
                    ties += other == value ? 1 : 0;
                }
                if (!lost)
                    won += 1.0 / (ties + 1);
            }
            return won / trials;
        }

        inline Action Decide(Table const& t, int seat, RandomBelow const& random, int trials = 150)
        {
            std::string const legal = t.Legal(seat);
            if (legal.empty())
                return Action::Fold;
            int opponents = 0;
            for (int i = 0; i < SEATS; ++i)
                opponents += (i != seat && t.seats[i].inHand && !t.seats[i].folded) ? 1 : 0;
            double const equity = Equity(t.seats[seat].hole, t.board, opponents, trials, random);
            uint64_t const call = t.CallAmount(seat);
            double const odds = call ? double(call) / double(t.Pot() + call) : 0.0;
            double const strength = equity * (opponents + 1); // 1.0 is an average hand at this table
            bool const raise = legal.find('r') != std::string::npos;
            bool const bet = legal.find('b') != std::string::npos;
            if ((raise || bet) && (strength > 1.5 || equity > 0.75 || (!call && random(100) < 6)))
                return raise ? Action::Raise : Action::Bet;
            if (legal.find('k') != std::string::npos)
                return Action::Check;
            if (equity >= odds + 0.04)
                return Action::Call;
            return Action::Fold;
        }
    }
}

#endif
