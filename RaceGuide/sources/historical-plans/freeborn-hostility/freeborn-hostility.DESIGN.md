# Freeborn hostility — confirmed mechanism and fix design

Supersedes the "blocked" section of `freeborn-hostility.PLAN.md` (kept for the history of the
investigation). Evidence: `.agents/plans/client-hostility-re/FINDINGS.md` (client disassembly,
raw instruction bytes) plus the live server/client DBCs read in this session.

## 1. Root cause (proved)

* The server is already hostile: `Unit::GetReactionTo` returns `REP_HOSTILE` for any Freeborn pair
  outside sanctuaries, and `Unit::_IsValidAttackTarget` would accept `CMSG_ATTACKSWING`.
* The 3.3.5a client decides player-vs-player friendliness **entirely from the two units'
  `UNIT_FIELD_FACTIONTEMPLATE` update fields**:
  `0x007254bb` reads `[[unit+0xd0]+0xc4]` and `0x0071f770` uses that value **directly as a
  `FactionTemplate.dbc` row id**. No race lookup, no `ChrRaces.dbc`, no `PLAYER_BYTES_3`, no
  `PLAYER_FLAGS` anywhere on the reaction → colour → attack path.
  Name colour comes from `UnitSelectionColor` (`0x0060da00` → `0x00521bf0`) keyed off
  `CanAttack`/reaction.
* The deployed `FactionTemplate.dbc` is identical on client (`Patch-F.MPQ`) and server
  (SHA-256 `a344d554…`): **every player template is `friendlyMask 6`, `hostileMask 8`** — friendly
  to both player groups, hostile only to the monster group. Both `Larry` and `Francesca` wear
  template `4` (`ChrRaces.dbc` RaceID 4 → FactionID 4), so the client computes *friendly* and
  refuses to start the attack. On this realm even native Alliance vs Horde is friendly in the open
  world; only battleground sides, duels and FFA areas produce hostility.
* `TEAM_FREEBORN` never reaches the client, so nothing today distinguishes a Freeborn from its
  race's native faction.

## 2. Attackability is separate and already satisfied

The client's `CanAttack` (`0x00729740`) allows a player-vs-player attack when the reaction is not
friendly **and** either the target has `UNIT_FIELD_BYTES_2` byte 1 bit `0x01` (PvP flag) and
neither side is in a sanctuary (`0x7299b5` → `0x7299c9`), or both have the FFA bit `0x04`
(`0x7299d9` → `0x7299e0`). That mirrors AzerothCore's port exactly (`Unit.cpp:10885-10891`). With
both characters `/pvp`-flagged, turning the reaction hostile is sufficient for both directions.

## 3. Fix design (masks only, additive bit)

Introduce a **fifth faction group bit `V = 16`** ("Freeborn"). The client's mask comparison is a
plain 32-bit `test` (`0x0071544e`, `0x007154aa`), so a bit above the four stock bits is honoured
everywhere (the "four bits only" limitation is in the *race-availability* function, which this
change does not touch because `ChrRaces.dbc` is unchanged).

| row | change | effect |
| --- | --- | --- |
| player templates `1,2,3,4,5,6,115,116,1610,1629` (the FactionIDs the deployed `ChrRaces.dbc` uses) | `ourMask \|= 16` (`3→19`, `5→21`) | makes "is a player" addressable by a bit NPCs do not have |
| the Freeborn template `F` | `ourMask 9` (`1\|8`), `friendlyMask 6`, `hostileMask 24` (`8\|16`), `factionFlags 0x48`, `faction` = an unused `Faction.dbc` id with `reputationListID < 0` | see matrix below |

Resulting matrix (mask semantics: hostile is tested before friendly, in both the core and the
client at `0x00715440`):

| pair | result |
| --- | --- |
| Freeborn → player | hostile (`24 & 19 = 16`) — red name, `CanAttack` gate passes |
| player → Freeborn | hostile (`8 & 9 = 8`) — red name, `CanAttack` gate passes |
| Freeborn → Freeborn | hostile (`24 & 9 = 1`) — matches the specification |
| monster → Freeborn / Freeborn → monster | hostile (`1 & 9`, `24 & 8`) — PvE unchanged |
| Freeborn → guard / civilian | friendly (`friendlyMask 6 & ourMask 3/2`) — no red NPCs |
| guard → Freeborn | mask says hostile, but `GetFactionReactionTo` returns the Freeborn's **reputation** with the guard's faction (all capital/neutral factions have `reputationListID >= 0`), so no aggro; the same reputation branch is what the client uses for NPC colour |
| player → player, player → NPC, NPC → NPC | unchanged: `16` is absent from every non-Freeborn `ourMask` |

`faction` must not be shared with another template (`IsFriendlyTo` short-circuits on equal faction
ids) and must have no reputation (`0x71f81a`-style reputation lookups must fall through to the
masks). A spare row id should be reused rather than a new one appended, so both sides resolve it
from their existing tables.

## 4. Implementation slices

1. **DBC artifact** (source of truth in the repo, e.g. `modules/mod-custom-server/data/dbc/`):
   a generator that starts from the deployed table and rewrites exactly the rows above, with a
   contract test asserting every other row is byte-identical.
   * server: `data/dbc-continuations/FactionTemplate.dbc1-freeborn` — `mod-wxl-dbc` registers
     `sFactionTemplateStore` (`WxlDbcRegistry.cpp:90`), so a worldserver restart applies it, no
     rebuild;
   * client: the same rows must reach `DBFilesClient\FactionTemplate.dbc`. The
     `wxl-extended-dbc` table list does not name `FactionTemplate`, so use the proven path:
     write the patched table into the project's own `patch-Z.MPQ` / `patch-enUS-Z.MPQ` with the
     Storm workflow that `tools/freeborn_team_pack.py` already uses (SHA-256 backups, round-trip
     verification).
2. **Apply the template to Freeborn characters** — `Player::SetFactionForRace` (`Player.cpp:6079`)
   keeps the Freeborn row for Freeborn characters and the race template for everyone else; the
   claim path (`Server/FreebornClaim.h` / `SetPersistentTeamId`) re-applies it because
   `Player::Create` runs before the claim; `Unit::RestoreFaction` (`Unit.cpp:14991`) already routes
   through `SetFactionForRace`; inside a battleground the template must follow the match side
   (`SetBattlegroundId` already maps it with `PvpSideOfTeam`) so BG teammates are not coloured
   hostile.
   *Interim option with no rebuild:* the same apply-on-login logic as an Eluna script in the
     bind-mounted `lua_scripts/` (Eluna exposes `Player:GetTeamId()` and `Unit:SetFaction()`), so
     the row and the client patch can be validated in minutes before spending a worldserver build.
3. **Tests / docs**: extend `src/test/server/game/Combat/FreebornTeamTest.cpp` with the reaction
   matrix; document the deployment and the fact that reinstalling `mod-Faction-Free` would drop the
   row.

## 5. Live verification (after deploying the DBC artifacts, before any build)

1. `.modify faction <F row id>` on `Francesca`, look at her from `Larry`'s client:
   expect a red name; with both `/pvp`-flagged, expect auto-attack to start in both directions.
2. `.modify faction 4` (or `.reset`) restores her.
3. Without the server change, a Freeborn is still indistinguishable from a native: the template has
   to be applied by code or by the interim Eluna script.

## 6. Status

Nothing modified yet: no source, DBC, client archive, database or container.
