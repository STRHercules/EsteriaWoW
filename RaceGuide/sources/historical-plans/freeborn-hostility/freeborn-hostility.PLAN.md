# Freeborn hostility — fix plan (blocked on one client fact)

Companion to `freeborn-hostility.ANALYSIS.md`. Nothing here is implemented yet.

## 0. The one open fact

The server is already hostile (`Unit::GetReactionTo` returns `REP_HOSTILE` for any Freeborn
pair outside sanctuaries) and `Unit::_IsValidAttackTarget` would accept `CMSG_ATTACKSWING`. The
client is what shows green and refuses to start the attack, so the fix must change something the
**client** reads for a player unit.

The 3.3.5a client can only see: the unit's `UNIT_FIELD_FACTIONTEMPLATE` update field, the byte
flags (`UNIT_FIELD_BYTES_2` PvP/FFA/sanctuary), `PLAYER_BYTES_3` byte 3, and the race in
`UNIT_FIELD_BYTES_0`. `TEAM_FREEBORN` is not on the wire at all.

**Probe (2 minutes, no build, no DBC change)** — GM-select `Francesca` and run
`.modify faction 14` (template `Monster`: `ourMask 8`, `friendlyMask 0`, `hostileMask 1`), then
look at her from `Larry`'s client. `.modify faction 4` (or `.reset`) restores her.

- Name turns red / attackable ⇒ the client resolves a player's faction from the update field and
  the plan below is the right one.
- Name stays green ⇒ the client derives a player's faction from race/client DBCs and **no
  server-side field can fix this**; it needs a `Wow.exe` patch or a race-level change, which the
  Freeborn contract forbids (`FREEBORN_IMPLEMENTATION_GUIDE.md:101`).

## 1. Why the obvious row is wrong

The deployed `FactionTemplate.dbc` (identical on the client in `Patch-F.MPQ` and on the server,
SHA-256 `a344d554…`) is the Faction-Free package: **every player template is hostile only to
monsters** (`hostileMask 8`) and friendly to both player groups (`friendlyMask 6`). So on this
realm even Alliance vs Horde is friendly in the open world; only battleground sides, duels and
Gurubashi-style FFA areas produce player hostility.

A Freeborn therefore has to be given its own row. The naive row (`ourMask 9`, `friendlyMask 0`,
`hostileMask 9`) does make players hostile to a Freeborn, but because players' `hostileMask` is
`8` (the monster group), the Freeborn has to sit in the monster group, and the simulation over the
live `creature_template` factions shows the cost:

| Candidate row | creature templates that would aggro a Freeborn |
| --- | --- |
| `ourMask 9`, `friendlyMask 0`, `hostileMask 9` | 319 / 647 (≈15 200 spawn entries) |
| `ourMask 17` (adds a fifth group bit) + player rows updated | monsters only |
| `ourMask 1` + player rows listing the Freeborn faction as an enemy | monsters only |

Only monsters *should* attack a Freeborn, so the fix must not reuse the monster bit.

## 2. Planned change (if the probe confirms)

### 2.1 DBC rows — additive, via the mechanisms this fork already uses

1. **A Freeborn faction template row.** Override one of the 194 rows that no
   `creature_template` references, e.g. row `2086`/`2087` (faction 529), with:

   | field | value | why |
   | --- | --- | --- |
   | `faction` | a spare `Faction.dbc` id with `reputationListID < 0` | keeps the reputation path out of the way, so masks/enemy lists decide; must not equal any other template's faction, or `IsFriendlyTo` short-circuits on equality |
   | `factionFlags` | `0x48` (same as the player rows) | player-like behaviour, not a guard or a monster |
   | `ourMask` | `1` (all players) | monsters (`hostileMask 1`) attack the Freeborn, guards (`hostileMask 8`) do not |
   | `friendlyMask` | `0` | nothing is friendly to it |
   | `hostileMask` | `1 \| 8 = 9` | the Freeborn sees all players and all monsters as hostile |
   | `enemyFaction` | empty | - |

2. **Player templates list the Freeborn faction as an enemy.** Add the Freeborn `faction` id to
   `enemyFaction[0]` of every template a player can wear: `1, 2, 3, 4, 5, 6, 115, 116, 1610, 1629`
   and the RaceID-to-FactionID set in the deployed `ChrRaces.dbc`. `FactionTemplateEntry::IsHostileTo`
   checks `enemyFaction` **before** the masks, so this makes every player hostile to a Freeborn
   without touching `hostileMask`, i.e. without dragging guards or city NPCs in. It also uses only
   the four existing group bits, so it does not depend on the client honouring a fifth bit.

3. **Delivery, no file replacement in the game tree:**
   - server: `data/dbc-continuations/FactionTemplate.dbc1-freeborn` — `mod-wxl-dbc` already
     registers `sFactionTemplateStore` (`WxlDbcRegistry.cpp:90`), so this is picked up at startup
     with a worldserver restart, no rebuild;
   - client: the same rows must reach `DBFilesClient\FactionTemplate.dbc`. The `wxl-extended-dbc`
     extension's table list does not name `FactionTemplate` (it does name `Faction` and
     `FactionGroup`), so the safe route is the proven one: write the patched table into the
     project's own `patch-Z.MPQ` with the Storm workflow used by `tools/freeborn_team_pack.py`
     (SHA-256-verified backups, round-trip check after write).

### 2.2 Server code

- `Player::SetFactionForRace` (`Player.cpp:6079`): a Freeborn keeps the new template; every other
  character keeps `ChrRaces.FactionID` exactly as today. The existing early-out
  (`!IsFreeborn() && GetTeamId() != GetOriginTeamId()`) already isolates the branch.
- `Player::SetPersistentTeamId` / the claim path (`Server/FreebornClaim.h`): re-apply the template
  when a character becomes Freeborn, because `Player::Create` runs `SetFactionForRace` before the
  claim arrives.
- `Unit::RestoreFaction` (`Unit.cpp:14991`) already routes through `SetFactionForRace`, so charm
  and `_oldFactionId` restore keep working.
- Battlegrounds: `Player::SetBattlegroundId` (`Player.cpp:12625`) already maps the match side; the
  template must follow the match side inside a match (origin template) and revert on leave, or a
  Freeborn's own BG team would render hostile. Verify how the client decides BG hostility before
  choosing between "swap the template per match" and "leave masks alone in matches".
- Pets inherit `owner->GetFaction()` (`Pet::SetFaction`), which is what the specification wants.
- Relationship stays separate from permission: an unflagged native still cannot attack a Freeborn
  (`Player::IsPvP()` gate in `Unit::_IsValidAttackTarget`).

### 2.3 Tests and docs

- Extend `src/test/server/game/Combat/FreebornTeamTest.cpp` with the reaction matrix over the
  patched rows (Alliance/Horde/Freeborn/monster/guard/civilian, both directions).
- Add a generator + contract test for the two DBC artifacts (server continuation, client table),
  asserting every untouched row is byte-identical to the deployed base and that the only changed
  rows are the Freeborn row and the player `enemyFaction[0]` slots.
- Record the deployment in a plan doc and note that a Faction-Free module reinstall would drop the
  row.

## 3. Alternatives, and when they win

- **FFA PvP byte flag** (`UNIT_BYTE2_FLAG_FFA_PVP`, `Player::UpdateFFAPvPState`): server-only, no
  DBC, matches "hostile to everyone including other Freeborn" and the safe-area rule. But the
  client's `CanAttack` (ported at `Unit.cpp:10888`) requires **both** sides to be FFA-flagged, and
  the friendly reaction check comes first, so it likely fixes Freeborn-vs-Freeborn only. Worth
  adding *in addition* if the faction row confirms, not instead of it.
- **`PLAYER_BYTES_3` byte 3**: set per battleground/arena side (`Player.cpp:12634`); 0 for
  everyone outside a match, so it cannot discriminate players in the open world.
- **Client binary patch**: only if the probe fails. Out of scope for this slice; it changes the
  client contract the Freeborn feature deliberately avoided.

## 4. Status

- Blocked on the probe (or on the client reverse-engineering now running in
  `.agents/plans/client-hostility-re/`).
- No source, DBC, client archive or database has been modified.
