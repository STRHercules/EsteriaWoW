# mod-esteria-casino

Gold-wager games: **Blackjack**, **Slots** and **Goblin Dice** against the house; **Chess**, **Checkers** and
**Texas Hold'em** between players; and the **Esteria Lottery**. Design and roadmap:
`.agents/plans/esteria-casino/esteria-casino.PLAN.md` (local, gitignored).

- Server: `src/EsteriaCasino.cpp` (wire protocol documented at the top), pure rules in `src/Blackjack.h`,
  `src/Slots.h`, `src/Dice.h`, `src/Chess.h`, `src/Checkers.h`, `src/Holdem.h`, `src/Lottery.h` and
  `src/CasinoHouse.h`; the PvP games and the lottery live in `CasinoBoardGames.cpp`, `CasinoPoker.cpp` and
  `CasinoLottery.cpp` on top of `CasinoCommon.h`. Unit tests in `tests/` (chess perft, side pots, conservation).
- Client: `wowdecomp/Addons/EsteriaCasino` (Lua window, `make_art.py`, `build_mpq.py`, `test_casino.py`).

| NPC | Entry | Game | Published return |
|---|---|---|---|
| Blackjack Dealer | 9600000 | 6-deck blackjack, 3:2, dealer stands on soft 17 | ~99.5% with good play |
| Fizzle Spinwheel | 9600001 | 3 reels, one line, WoW-icon symbols, top line 500x | 97.46% |
| Grizzik Knucklebones | 9600002 | 2d6: under 7 / over 7 pay 2.33x, seven / doubles 5.8x | 97.08% / 96.66% |
| Grandmaster Pell | 9600003 | chess and checkers, challenge + escrowed stakes, clocks, spectators | winner takes both, 5% cut |
| Card Shark Vexa | 9600004 | fixed-limit Hold'em, 2-6 seats, buy-in held as escrow | 5% rake, capped, no flop no drop |
| Lucky Nozzlebit | 9600005 | pick 4 of 20; 3 matches win a fixed prize, 4 share the jackpot | pool = tickets + 10% of house wins |

Slots and dice settle in the same commit that takes the stake. Bets are capped so the unreserved bankroll covers
the worst case: 4x for blackjack, 499x for slots, 5x for dice.

## Install

1. Apply `data/sql/db-characters/esteria_casino.sql` to the characters DB and `data/sql/db-world/esteria_casino.sql`
   to the world DB (module SQL is not auto-applied on Esteria images).
2. Copy `conf/esteria_casino.conf.dist` next to `worldserver.conf` as `esteria_casino.conf`, and set
   `EsteriaCasino.Enable = 1`. The casino also needs `CharacterDatabase.WorkerThreads = 1`.
3. Restart, spawn the NPCs with `.npc add 9600000` .. `9600005`, and fund the house from a GM
   character: `.casino fund <gold>`. An empty house takes no bets.
4. Client: `python make_art.py` in the addon folder (reads the asset packs from `G:\Downloads\HDWoWModels\BoardGames`),
   then `python build_mpq.py <client>/Data/patch-ZzzzzzzzzzzZCasino.MPQ` with the client closed.

## Commands

| Command | Who | Does |
|---|---|---|
| `.casino status` | player | today's staked total and any self-exclusion |
| `.casino optout <days>` | player | self-exclusion; can only be extended |
| `.casino house` | admin | bankroll, reserved, available, current table limit |
| `.casino fund <gold>` / `.casino withdraw <gold>` | admin | move the GM character's own gold in or out |
| `.casino round <id>` | GM | audit one round |

Every copper moved has a `casino_ledger` row. Rounds left open by a crash are refunded by mail at the next start.

## Art licensing

The asset packs forbid redistribution and this repo is public: never commit the source PNGs or the generated
`Art/*.blp` (gitignored). Credits: "Casino Table UI Kit by MCreative", "PARLOUR by najjar320".
