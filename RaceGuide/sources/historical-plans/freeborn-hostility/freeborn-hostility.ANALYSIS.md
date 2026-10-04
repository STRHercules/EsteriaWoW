# Freeborn player hostility: why the client shows Friendly, and what can change it

Report: a Freeborn Night Elf (`Francesca`, `characters.teamId = 3`) and a native Alliance Night
Elf (`Larry`) were both PvP-flagged in Stranglethorn Vale. They render as **Friendly (green)** and
neither can attack the other. Expected: hostile to one another.

## 1. Established facts (source + deployed DBC, not inference)

### 1.1 The server already reports them hostile

`Unit::GetReactionTo` was extended for Freeborn (`src/server/game/Entities/Unit/Unit.cpp:7184-7188`):

```cpp
// Outside safe areas and match/group overrides, Freeborn identity is hostile both ways.
if (selfPlayerOwner && targetPlayerOwner &&
    !selfPlayerOwner->pvpInfo.IsInNoPvPArea && !targetPlayerOwner->pvpInfo.IsInNoPvPArea &&
    IsFreebornHostilePlayerTeamPair(selfPlayerOwner->GetTeamId(), targetPlayerOwner->GetTeamId()))
    return REP_HOSTILE;
```

`IsFreebornHostilePlayerTeamPair` (`SharedDefines.h:781`) is true whenever either side is
`TEAM_FREEBORN`, so the server's reaction for this pair is `REP_HOSTILE`. Stranglethorn Vale is
not a sanctuary and `pvpInfo.IsInNoPvPArea` is only set for sanctuaries/capitals
(`PlayerUpdates.cpp:1247-1251`, `1344-1350`), so the Freeborn branch applies.

`Unit::_IsValidAttackTarget` (`Unit.cpp:10764`) then passes the pair:

- line 10820 rejects only when a reaction is **friendly**; hostile passes.
- line 10876 rejects sanctuary/sanctuary; not the case here.
- line 10885 `if (target->IsPvP()) return true;` - both characters are PvP-flagged.

So `CMSG_ATTACKSWING` would be accepted by the server. **The block is client-side**: the client
decides the name colour and refuses to start the attack before the packet is ever sent.

(Caveat worth checking on the next live run: `_IsValidAttackTarget` line 10773-10775 returns
false when *either* character is a GM, so both test characters must have GM mode off.)

### 1.2 The deployed client's faction data has every player friendly to every other player

The running client loads `DBFilesClient\FactionTemplate.dbc` from `Patch-F.MPQ`
(the Faction-Free package, `modules/mod-Faction-Free/dbc/FactionTemplate.dbc`, SHA-256
`a344d554…`; `PATCH-A.MPQ` also ships one but `F` > `A` in patch load order, and neither
`patch-Z.MPQ` nor `patch-enUS-Z.MPQ` carries the table). The player rows in the deployed table:

| ID  | race template     | ourMask | friendlyMask | hostileMask |
| --- | ----------------- | ------- | ------------ | ----------- |
| 1   | PLAYER, Human     | 3       | **6**        | **8**       |
| 2   | PLAYER, Orc       | 5       | **6**        | **8**       |
| 4   | PLAYER, Night Elf | 3       | **6**        | **8**       |
| 5   | PLAYER, Undead    | 5       | **6**        | **8**       |
| 115 | PLAYER, Gnome     | 3       | **6**        | **8**       |
| 1610| PLAYER, Blood Elf | 5       | **6**        | **8**       |

Masks are the four client faction groups: `1` all players, `2` Alliance players, `4` Horde
players, `8` monsters. So in this fork every player is friendly to **both** player groups and
hostile only to monsters (stock is `friendlyMask = 2|4`, `hostileMask = 12|10`). Two
consequences:

- `Larry` and `Francesca` share faction template `4` (`ChrRaces.dbc` `FactionID` for race 4), and
  `FactionTemplateEntry::IsFriendlyTo` short-circuits on `faction == entry.faction`. Friendly.
- The same template is what the Freeborn is given today: `Player::SetFactionForRace`
  (`Player.cpp:6079-6088`) still assigns the race's `FactionID` for Freeborn characters, because
  the Freeborn work only separated persistent team from faction refresh.

### 1.3 Nothing the server currently sends to the client distinguishes Freeborn

`TEAM_FREEBORN` exists only in the server's `TeamId`; `characters.teamId` is not part of
`SMSG_CHAR_ENUM`'s presentation fields, and the in-world indicator is the `FreebornClaim` addon
(chat/addon channel), not a unit field. The client therefore has no Freeborn input at all: it
resolves both characters as Night Elf -> template 4.

## 2. The decision that gates the fix

Player-versus-player hostility in the 3.3.5a client is computed **client-side**. The server's
`GetReactionTo` override cannot change a name colour or unblock the attack action. So the fix has
to change a field the client reads for a player unit. The candidate levers are:

| # | Lever | Scope | Notes |
| - | ----- | ----- | ----- |
| A | `UNIT_FIELD_FACTIONTEMPLATE` (a Freeborn faction-template row) | per character, server-sent | Works only if the client resolves a **player** unit's faction from the update field; needs a row that exists in the client DBC, which this fork can ship as a WXL continuation file (`Data/dbc-continuations/*.dbc1-*`, already proven by Battlemon). Conflicts with `FREEBORN_IMPLEMENTATION_GUIDE.md` line 101 ("do not change … faction templates to fake the team"), so it must be framed as a hostility/relationship template, not as team identity. |
| B | `UNIT_BYTE2_FLAG_FFA_PVP` (`UpdateFFAPvPState`, `PlayerUpdates.cpp:1474`) | per character, server-sent, no DBC work | The client's own "attackable regardless of team" state (Gurubashi/arena). But `_IsValidAttackTarget` - which AC documents as a port of the client's `Unit::CanAttack` - requires **both** sides to be FFA-flagged (`Unit.cpp:10888`), so an unflagged native could not attack an FFA Freeborn; and the friendly reaction check precedes it. Likely fixes Freeborn-vs-Freeborn only. |
| C | `PLAYER_BYTES_3` byte 3 | per character, server-sent | Set by `Player::SetBattlegroundId` (`Player.cpp:12634`) as the **battleground/arena side** byte; 0 for everyone outside a match, so it cannot discriminate players in the open world. Useful only if the client also reads it outside matches. |
| D | race (`ChrRaces.dbc` `FactionID` / `TeamID`) | per race | If the client resolves a player's faction from race rather than the update field, no per-character server field can fix this; it would take a `Wow.exe` patch. Freeborn must stay on its native race, so this path is closed. |

**Open question, being answered by client reverse-engineering
(`.agents/plans/client-hostility-re/`): does the 3.3.5a client resolve a *player* unit's reaction
from `UNIT_FIELD_FACTIONTEMPLATE`, from race DBCs, or from a flag?**

### Cheapest live experiment that settles lever A vs D (2 minutes, no code change)

`.modify faction <factionTemplateId>` runs `Unit::SetFaction` on the selected player
(`src/server/scripts/Commands/cs_modify.cpp:289-297`), which writes `UNIT_FIELD_FACTIONTEMPLATE`
and therefore reaches the client as a normal update field.

1. Select `Francesca` with the GM character and run `.modify faction 14` (template 14 is
   `Monster`: `ourMask 8`, `friendlyMask 0`, `hostileMask 1` in the deployed table).
2. Look at `Francesca` from `Larry`'s client.
3. `.modify faction 4` (Night Elf) or `.reset` restores her.

- If her name turns **red/attackable** for `Larry`, the client reads the update field and lever A
  is the fix.
- If she stays **green**, the client derives player faction from race and only a client binary
  patch can fix it.

## 3. Server-side work that is right regardless

- Re-check the two extra conditions that can silently block the live test: GM mode
  (`_IsValidAttackTarget:10773`) and sanctuary (`:10876`).
- `Unit::RestoreFaction` (`Unit.cpp:14991`) restores a player's template via
  `SetFactionForRace`, so whatever a Freeborn is given must be re-applied by both
  `SetFactionForRace` and the charm/`RestoreFaction` path.
- A Freeborn's pet inherits the owner's template (`Pet::SetFaction(owner->GetFaction())`), which
  is what the specification asks for, but it also means the template choice propagates.
- Battlegrounds assign a Freeborn an Alliance/Horde match side (`PvpSideOfTeam`), so if lever A is
  used the template must follow the match side inside a match and revert on leave, or BG
  teammates would render hostile.
- The relationship and the attack permission stay separate, per the specification: a Freeborn
  being hostile does not mean an unflagged player may attack one.

## 4. Status

- Client RE: in progress (`client-hostility-re`).
- No source change made yet; nothing built or deployed.
