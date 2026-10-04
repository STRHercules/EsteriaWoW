# Freeborn client slice — status and open hazards

## Delivered in this slice

| Piece | Where |
| --- | --- |
| Freeborn button between the gender buttons | `Interface\GlueXML\CharacterCreate.xml` in `patch-Z.MPQ` + `patch-enUS-Z.MPQ` |
| Selection state + no second source of truth | `Interface\GlueXML\CharacterCreate.lua` (guarded block, wrapped stock functions) |
| Create signal | create name carries exactly one trailing space |
| Server trust boundary | `WorldSession::HandleCharCreateOpcode` strips the token, resolves `RequestedTeamId` |
| Persistence | `Player::Create` applies `TEAM_FREEBORN` last, after all race-origin start data |
| Repack + backups | `tools/freeborn_team_pack.py --install`, backups in `Data\_freeborn-backups\<utc>\` with SHA-256 |
| Contract test | `tools/test_freeborn_team_pack.py` |

Verified native-preserving: the disable mask and the one-account-one-side rule keep evaluating
origin for natives; `Player::Create` callers that never go through the session handler
(playerbots, test drivers) default to `TEAM_NEUTRAL` and stay on their race-origin team.

## Why not `OutfitId`

The glue creation binding table inside `Wow.exe` (the `.\CharacterCreation.cpp` string block,
file offset `0x005f42d7`, `CreateCharacter` name VA `0x009F5BB0`) contains no outfit/team setter:

```
GetCreateBackgroundModel IsRaceClassRestricted IsRaceClassValid CustomizeExistingCharacter
CreateCharacter GetRandomName SetCharacterCreateFacing GetCharacterCreateFacing
RandomizeCharCustomization CycleCharCustomization SetSelectedClass SetSelectedSex SetSelectedRace
GetSelectedClass GetSelectedSex GetSelectedRace GetFacialHairCustomization GetHairCustomization
GetClassesForRace GetAvailableClasses GetAvailableRaces GetFactionForRace GetNameForRace
ResetCharCustomize SetCharCustomizeBackground SetCharCustomizeFrame
```

`CreateCharacter(name)` takes the name only; appearance is reachable only through
`CycleCharCustomization`, which is bounded to valid options. `Client.dll` is a 3 KB stub and
`WarcraftXL.dll` exposes only M2/Wmo/Scene graphics symbols. So the spec's `OutfitId` bit is only
reachable by patching `Wow.exe` (a code-injection patch, gated by `TASK.md` §4.6), while the
trailing-space token needs no binary change. The name argument is the one create field Lua owns.

## OPEN HAZARD — two-sided arrays indexed by persistent team (NOT fixed here)

`TEAM_FREEBORN == 3` is now persisted, so any two-element store indexed by `GetTeamId()` reads out
of bounds. `std::array<T,2>::operator[]` and raw array indexing do not bounds-check, so this is
undefined behaviour, generally a crash. **43 direct-index sites:**

| File | Sites | Store |
| --- | --- | --- |
| `OutdoorPvP.cpp` | 7 (`44,54,280,297,347,543,649`) | `OutdoorPvP.h:153,272` `std::array<PlayerSet,2> _activePlayers/_players` |
| `Battlefield.cpp` | 21 | `Battlefield.h:390-393,422` `[PVP_TEAMS_COUNT]` (`SharedDefines.h:3729` = 2) |
| `BattlefieldWG.cpp` | 1 (`1084`) | `WGQuest[player->GetTeamId()][2]` |
| `BattlegroundIC.cpp` | 6 (`77-79,546,548,551`) | BG side arrays |
| `BattlegroundEY.cpp` | 2 (`557,558`) | BG side arrays |
| `LFGMgr.cpp` | 6 (`999,1000,1040,1045,1050,1051`) | `LFGMgr.h:429-439,629-630` `[2]` raid-browser stores |

Reachability: the `OutdoorPvP` and `Battlefield` paths are reached by walking into an outdoor-PvP
zone or Wintergrasp; the rest by queuing for a battleground or opening the raid browser. This is
the `TASK.md` §6 / §28 "two-side safety" work package, and it needs the product decision §28
reserves (which side a Freeborn is assigned for a match), so it was left out rather than
half-applied.

### Compiler-derived cross-check: incomplete `TeamId` switches are latent, not live

Building with `-DWITH_WARNINGS=ON` flags switches over `TeamId` that add no `default:` — an
authoritative list, because the warning fires exactly where an enumerator is unhandled:

```
BattlefieldWG.h:1430        warning: enumeration value 'TEAM_FREEBORN' not handled in switch
OutdoorPvPTF.cpp:126        warning: enumeration value 'TEAM_FREEBORN' not handled in switch
OutdoorPvPTF.cpp:154        warning: enumeration value 'TEAM_FREEBORN' not handled in switch
```

All three were traced and are **not reachable with `TEAM_FREEBORN`**, so they are latent gaps rather
than live hazards — recorded so the §6 slice closes them with a defensive `default:` rather than
rediscovering them:

- `BattlefieldWG.h:1430` `GiveControlTo` — `teamControl` is initialised to `TEAM_NEUTRAL` (L1421) and
  only ever fed `GetAttackerTeam()`/`GetDefenderTeam()`, i.e. the battlefield's own two sides. A
  Freeborn team would fall through and silently leave the workshop uncontrolled, not crash.
- `OutdoorPvPTF.cpp:126,154` `ResetZoneToTeamControlled` / `ResetToTeamControlled` — callers pass
  `TEAM_NEUTRAL` (L255) or `controllingTeam`, which is computed as
  `hordeTowers > allianceTowers ? TEAM_HORDE : TEAM_ALLIANCE` (L372). Always A or H.

The other `case TEAM_ALLIANCE`/`case TEAM_HORDE` switches in the tree (`OutdoorPvPZM.cpp`,
`OutdoorPvPSI.cpp`, `PlayerTaxi.cpp`, `spell_quest.cpp`, `boss_chess_event.cpp`) drew no warning,
so they either carry a `default:` or do not switch over `TeamId`.

Fixed here because it fires on the first social action: `mod-world-chat`
`TeamColored[sender.GetTeamId()]` was a 3-element array; it is now 4 elements and bounds-checked.

## RESOLVED — the client's name rule, and the token position it forces

`Interface\GlueXML\GlueStrings.lua` (in `patch-enUS-Z.MPQ`) states the rule outright:

```
CHAR_NAME_INVALID_SPACE   = "You cannot use a space as the first or last character of your name";
CHAR_NAME_INVALID_CHARACTER = "Names can only contain letters";
CHAR_NAME_TOO_SHORT       = "Names must be at least 2 characters";
CHAR_NAME_TOO_LONG        = "Names must be no more than 12 characters";
```

So spaces **are** legal in player names, but never in the first or last position. That means:

- The original trailing-space token was **provably dead** — the client rejects it locally with
  `CHAR_NAME_INVALID_SPACE` and never sends `CMSG_CHAR_CREATE`. This is now asserted in the
  contract test (`Name.back() == ' '` must not appear in the handler).
- An **interior** space is exactly what the client permits, so the token is one space placed
  immediately after the first character. `CharacterFreeborn_CreateName` computes the first
  character's UTF-8 byte length and injects there; the handler accepts the token only when
  exactly one space is present and the text before it decodes to exactly one character.
- The token counts toward the client's 12-character limit, so **a Freeborn name is at most 11
  characters**. A 12-character name fails the client's own length check, which fails safe: no
  character is created rather than a silently native one.

The earlier `0x6B0F90` / `0x7E1E90` / `0x00AD91F0` analysis below is what prompted this check;
the message table was the client's copy of the `CHAR_NAME_*` enum, and `GlueStrings.lua` supplied
the semantics.

## Earlier analysis (retained): the client validates the create name

`CGCharacterCreation::CreateCharacter` (`Wow.exe` `0x004E0380`, reached from the glue binding
`Script_CreateCharacter` at `0x004E0C60`) calls a name validator and refuses to send when it
fails, showing a localized dialog instead.

- `0x6B0F90(name)` is a thin wrapper: it calls `0x7E1E90` and returns `result + 0x57`.
- The caller only proceeds when that equals `0x57`, i.e. when the validator returned **0**.
- The failure codes come from the client's own copy of the `CHAR_NAME_*` enum, tabled at
  `0x00AD91F0` and mapped to messages by `0x6B0F40`:

```
0x57 CHAR_NAME_SUCCESS        0x5c CHAR_NAME_INVALID_CHARACTER   0x63 CHAR_NAME_INVALID_SPACE
0x58 CHAR_NAME_FAILURE        0x5d CHAR_NAME_MIXED_LANGUAGES     0x64 CHAR_NAME_CONSECUTIVE_SPACES
0x59 CHAR_NAME_NO_NAME        0x5e CHAR_NAME_PROFANE             0x65..0x66 Russian silent chars
0x5a CHAR_NAME_TOO_SHORT      0x5f CHAR_NAME_RESERVED            0x67 DECLENSION_DOESNT_MATCH
0x5b CHAR_NAME_TOO_LONG       0x60..0x62 apostrophe / 3-consecutive
```

So the client has explicit `CHAR_NAME_INVALID_SPACE` / `CHAR_NAME_CONSECUTIVE_SPACES` handling,
and a trailing space is the canonical *invalid* space position. Two readings remain, and they
differ in outcome:

1. Player names allow no spaces at all (the usual WoW rule). The space codes and the
   `cmp [ebp-8], 0x18` (24-character) space-length rule found in the sibling validator
   `0x7E1F60` belong to the **guild/pet/arena-team** name paths that share this enum — guild
   names are the 24-character ones, player names are 12. Under this reading the name channel is
   unusable and only an `OutfitId` bit works.
2. Some space positions are legal for player names. Then a token at an interior position would
   pass where a trailing one does not.

`0x7E1E90` marshals five caller-supplied class flags into the core validator `0x7E18C0`, so
which classes are permitted is data-driven and was not resolved further.

`GlueStrings.lua` settled it: spaces are legal except in the first or last position, so reading 2
applied and the token moved to an interior position. No `Wow.exe` patch was needed.

## How to verify the live client

1. Fully quit and relaunch the client (GlueXML is read at startup only).
2. Character creation: the **Freeborn** pick sits between the male and female picks.
   Select it, type a name of **2–11 characters**, click **Create**.
3. Server side, either of these is conclusive:

```
docker logs --since 5m ac-worldserver | Select-String "Freeborn|persistent team"
docker exec ac-database mysql -uroot -ppassword -e \
  "SELECT name, race, teamId FROM characters ORDER BY guid DESC LIMIT 3;" acore_characters
```

Expected: `Account N requested a Freeborn character named 'Borix'` followed by
`Create Character: Borix ... (persistent team 3)`, and `teamId = 3` on the new row.

Failure modes and what they mean:

| Symptom | Meaning |
| --- | --- |
| No Freeborn pick on screen | the GlueXML override did not load (check `exe_patched`, archive priority) |
| "You cannot use a space as the first or last character of your name" | the token left the interior position, i.e. the Lua block in the archive is stale |
| "Names must be no more than 12 characters" | the name was 12 characters; the token costs one |
| Row exists with `teamId = 0/1` | the client sent no token; the client-side injection did not run |
| No log line, no row | creation failed after the token step (name taken, disabled, etc.) |

## Round-2 additions

- **Stock-vocabulary validation.** `assert_vocabulary_is_stock` parses the *deployed* archive and
  proves every element and attribute inside the injected button already exists elsewhere in the
  same file, and that the child ordering (`Layers` then `Scripts`) matches the stock race button.
  No UI schema (`UI.xsd`) ships with the client, so this is the strongest structural check
  available; it rules out the inject-a-tag-the-parser-does-not-know failure mode.
- **Creation diagnostics.** The handler logs `Account N requested a Freeborn character named '…'`
  when it detects the token, and the creation log line now carries `(persistent team N)`. That is
  what makes a live test self-verifying and distinguishes "client never sent it" from "server did
  not decode it". The pre-existing 200-column log line was reflowed while adding the field.

## Round-3 additions

- **The boundary is now an explicit, executed unit.** The decode moved out of the 2,700-line
  handler into `src/server/game/Server/FreebornCreateToken.h` (`FreebornCreateToken::Extract`),
  which states the wire contract, the client rule that forces the token's position, and every
  rejection in one place. The handler is now one call plus its comment.
- **The two halves share one rule, literally.** The client sized the first character from its UTF-8
  lead byte while the server used `Utf8toWStr` on the prefix — equivalent for valid UTF-8, but two
  implementations of one contract. Both now use the same lead-byte table, so
  `assert_token_agreement` can assert the exact thresholds appear on both sides rather than
  asserting they are probably equivalent. (Dropping `Utf8toWStr` costs no safety: a malformed name
  still fails `normalizePlayerName` / `CheckPlayerName` afterwards, so the only difference is which
  error code the client sees.)
- **`tools/freeborn_token_selftest.cpp` executes the production header** on the host with no
  project build, which matters because the objective asks to *prove* the boundary and the live GUI
  test is blocked on a human:

```
cl /nologo /std:c++20 /EHsc /W4 /I src\server\game\Server ^
   tools\freeborn_token_selftest.cpp /Fe:freeborn_token_selftest.exe
```

  16 cases and the width table, all passing: accepted (`B o`, `B orix`, `Ü nter`, `€ x`, `𝕏 x`);
  rejected (no space, empty, single character, trailing space, leading space, two spaces, prefix of
  two or three characters, truncated lead byte). Writing the table immediately caught a mistake in
  my own understanding — for an ASCII name the client injects at index 1, so the token is
  `B orix`, not `Bor ix`.

## Round-4 fix — the create screen broke, and why the checks missed it

The user's client showed, at launch:

```
Interface\GlueXML\CharacterCreate.lua:1846: attempt to index global 'CharacterCreate' (a nil value)
```

and no Freeborn pick on the creation screen. Two separate defects, one hiding the other.

**1. The block touched a frame at load time.** The Glue XML creates the `CharacterCreate` frame
*after* the script file has executed, so the block's top-level
`CharacterCreate.selectedFreeborn = false;` was a nil index. Because a runtime error aborts the
whole chunk, none of the functions below it were ever defined either — which is why the button had
no positioning and no textures. Fixed by moving all frame access inside functions and creating the
state on first use (`CharacterFreeborn_IsSelected`, `CharacterFreeborn_SetSelected`).

**2. A stale revision survived the previous repack.** The first shipped revision predated the
managed-block sentinels, so round 2's packer appended a SECOND copy instead of replacing it. The
deployed file carried the legacy block at L1833 and the managed block at L1963; the legacy one
errored first, so the good one never ran. Fixed by canonicalising: the earliest revision marker
(header line or sentinel) is walked back over the revision's `-- =====` banner and the whole
injected region is replaced by one current block.

**Why the checks missed it — both were my fault, and both are now closed:**

- The "stale trailing-space call = 0" check used PowerShell `Select-String -SimpleMatch` with a
  regex-escaped pattern, so it searched for literal backslashes and always returned 0. A
  meaningless pass. All such checks now run in Python with real literals.
- Only the *payload* was shape-checked; the deployed file never was. `assert_lua_block_shape` and
  `assert_xml_button_shape` now run against the Lua and XML read back **out of both deployed
  archives**, asserting exactly one block, one guard, one header, no stale token call, no
  load-time frame access, and an anchored button.

**Independent verification** (`.agents/plans/freeborn-client/verify_independent.py`), which
deliberately imports neither the packer nor the contract test, proves the archives are clean:

```
stock Lua prefix is byte-identical to the pristine backup      ok
removing the button reproduces the pristine stock XML exactly   ok
no load-time frame access in the block (found [])               ok
```

So the only difference from the pre-Freeborn client is the addition — no stock code was rewritten.

**Button anchoring.** The XML now gives the button its own `<Anchors>`, so if a Lua wrapper ever
fails to run the pick is still visible rather than invisible. Element order is `Anchors`, `Layers`,
`Scripts`, matching `CharacterCreateNameEdit`, `CharCreateOkayButton`, `CharCreateBackButton` and
`CharacterCreateIconButtonTemplate` in the stock file; the contract test now asserts that order
against that evidence instead of a hardcoded guess.

Client-only change: no worldserver rebuild was needed, and the deployed server already carries the
matching interior-space token decode.

### Not done: the Freeborn emblem art

The user supplied `G:\Downloads\Freeborn.png` (314x314 RGBA). Using it as the button face needs a
PNG -> BLP2 encoder, and neither `tools/derive_playable_race_portraits.py` nor
`tools/cars_mount_pack.py` writes BLP2 (both only read and validate it). The button currently uses
the template's generic round plate plus its "Freeborn" label. The safe route for the emblem is to
reuse a known-good BLP2 from the client as a container and replace its pixel payload, keeping the
header and mip layout valid.

## Round-5 — the name channel is dead, and a field-width bug found while checking

### 1. The client refuses spaces in character names (proven, not inferred)

Selecting Freeborn and pressing Accept produced `Names can only contain letters`
(`CHAR_NAME_INVALID_CHARACTER`) on "Dobb", and **the server logged no token request at all**. A
space that reached the server would have failed `normalizePlayerName` and produced
`CHAR_NAME_NO_NAME` ("Enter a name for your character"), a different message — so the rejection is
client-side, before the packet is sent.

This means the round-2 reading was wrong. `CHAR_NAME_INVALID_SPACE` ("...as the first or last
character...") does **not** describe player names; character names are letters-only, and the
space/apostrophe codes plus the 24-character limit belong to the sibling validators that share
that enum (guild/pet/arena-team — the 24-character rule in `0x7E1F60` is a guild-name rule). The
whole name channel is therefore unusable: any name the client will send is a name a player can
type.

Remaining channels, none of which is obviously right — this needs a product decision:

- **Patch `Wow.exe`** (the spec's original intent; `TASK.md` 4.6 requires separate authorization).
  Either widen the character-name charset so the existing interior-space token gets through, or
  reserve an `OutfitId` bit gated by a CVar the button sets (that one needs injected code).
- **Deferred in-world conversion** (no binary patch): the button records the intent in a CVar --
  in memory is enough, since creating and logging in happen in one client session -- and an addon
  shipped in the same archive applies it on first login through a server-side player command. Not
  atomic; needs an addon plus that command, which `TASK.md` 32 wants anyway.
- **Letter-only name token** (no binary patch): the client doubles the first letter (`DDobb`) and
  the server collapses it. Fits the letters-only rule and keeps the length cost, but a native
  whose name genuinely starts with a same-case doubled letter would be misread, and a name already
  starting with a doubled letter cannot be made Freeborn (three consecutive letters are refused).

### 2. `teamId` was being read with the wrong field width (fixed)

While checking the logs for the token I found, repeatedly:

```
Character 478 has invalid persistent team id 122624; don't build enum.
```

`characters.teamId` is `TINYINT UNSIGNED`, so no row can hold 122624. `Field::GetData` reads a raw
prepared-statement field with `*reinterpret_cast<T const*>(data.value)`, so `Get<uint32>()` on a
one-byte column reads three bytes of the neighbouring row — which is exactly why every logged
value's **low byte was that row's real teamId** and the rest was garbage. The effect was that
`BuildEnumData` refused those characters, silently dropping them from the character list (including
the user's own 478-487 and 492).

Fixed at all five read sites, each now `Get<uint8>()`: `Player::BuildEnumData`,
`PlayerStorage.cpp:5099` (`LoadFromDB` — so login was exposed to the same misread),
`CharacterCache.cpp:87,129`, `CharacterHandler.cpp:2058` (race/faction change),
`cs_character.cpp:251` (deleted-character restore). Rebuilt and deployed; the guard
`assert_team_id_reads_are_byte_wide` in the contract test bans the exact wrong expressions so it
cannot come back.

Caveat on the evidence: no client has requested a character list since the restart, so "no errors
now" is not yet proof. The proof is the code path plus the shape of the bad values. Confirming it
needs one character-select visit.

## Round-6 — the name carrier is gone; a deferred claim replaces it

The user's rule: **a Freeborn name must follow exactly the same rules as an Alliance or Horde
name.** The only create field GlueXML can influence is the name, so that rule ends the whole
name-carrier family -- space, doubled letter and case convention alike. Every name token, the
interior-space decode, and the "allow spaces" exe patch were removed (`FreebornCreateToken.h`,
`tools/freeborn_token_selftest.cpp` and the patch tool are deleted; `RequestedTeamId` and its
apply block in `Player::Create` went with them). `ChatHandler.cpp`'s disable-mask check went back
to the race origin.

What exists now:

| Piece | Where |
| --- | --- |
| Freeborn button, selection state, plate texture | `Interface\GlueXML\CharacterCreate.xml`, `CharacterCreate.lua` |
| The choice, recorded | `SetCVar("freebornPending", <typed name>)` -- cleared on every non-Freeborn creation |
| The claim | `Interface\AddOns\FreebornClaim` -- on first world entry, if the CVar matches the logged-in name, whispers `FREEBORN\tclaim` to itself |
| The claim handler | `src/server/game/Server/FreebornClaim.h`, called from the `LANG_ADDON` branch in `ChatHandler.cpp` |
| The button plate | `Interface\Glues\CharacterCreate\UI-CharacterCreate-Freeborn.blp` (user-supplied, 64x64 BGRА, validated against the project's own BLP2 reader) |

The name reaches the server **exactly as typed**, and no name rule changes. The character is
created on its race-origin team and becomes Freeborn moments later, on first login, before
anything has happened to it.

The addon-message transport is the one this project already uses (`ClasslessWildcard.lua:78` does
`SendAddonMessage(PREFIX, msg, "WHISPER", UnitName("player"))`), it requires `AddonChannel = 1`
(it is), and a client may send the envelope at any time: Freeborn is a choice a player makes about
their own character, and the claim can only touch the sender's own character.

### Assumptions this design rests on, and how to see which one failed

1. **`SetCVar` works from the GlueXML create screen.** Verified only that the binding exists in
   `Wow.exe`; whether it is exposed at the glue screen is not something I can test without the
   client. The call is wrapped in `pcall`, so if it is not, the create screen still works and no
   claim happens.
2. **The addon is enabled.** New addons default to enabled, but it has to be in the client's list.
3. **The CVar survives from the create screen into the world**, which it should: same process,
   CVars are C-side.

Failure tells them apart: no `Player <name> ... claimed Freeborn` line in the worldserver log with
a character that *is* Freeborn-eligible means the claim never arrived (1, 2, or the CVar); a claim
line with a native character in the database would mean the handler or the setter.

## Round-7 — in-game readout, and what the character-select badge still needs

**In-game check, no permissions needed.** The claim addon now also answers `/freeborn`: it sends
the `FREEBORN\tstatus` envelope and the server replies with
`[Freeborn] persistent team X, origin team Y`. That works for any player, which matters because GM
commands are gated by RBAC and the player-facing path should not be.

**GM command.** `.playerteam status|set freeborn|set native [player]`, online or offline. Reads the
live player for online targets and the character cache for offline ones; the setter goes through
`Player::SetPersistentTeamId` online, and writes the database plus the cache offline. Protected by
new RBAC permission 1000 (`RBAC_PERM_COMMAND_PLAYERTEAM`, the custom range declared at the end of
`RBAC.h`), granted to group 197 — verified to be reachable as administrator (192) -> gamemaster
(193) -> 197 "Role: Gamemaster Commands", the same group that grants the other character commands.

**Operational gotcha worth remembering:** pending SQL is applied by the `ac-db-import` container,
whose image bakes `data/sql` at build time. A newly added pending file is invisible until that
image is rebuilt (`docker compose build ac-db-import && docker compose up -d ac-db-import`). The
worldserver image does not contain `data/sql` at all. That is why the auth migration needed an
extra step while the character one did not.

### The character-select logo: where it is, and what blocks it

The hook points are known exactly:

- `CharacterSelect.lua:569` — `FACTION_ICONS = { Alliance = "...\CharacterSelect\AllianceLogo", Horde = "...\HordeLogo" }`
- `CharacterSelect.lua:586` — `local faction = GetCharacterFaction(race)`; the logo is **race-derived**
- `CharacterSelect.lua:619-631` — the 60x60 `FactionIcon` texture picks `FACTION_ICONS[faction]`

The blocker is the marker. `CharacterSelect.lua:575` unpacks exactly ten values from
`GetCharacterInfo(index)` — `name, race, class, level, zone, sex, ghost, petClass, petRace,
petFamily` — and **none of them is the raw flags field**, so a Freeborn bit in `SMSG_CHAR_ENUM`
would not reach the GlueXML today. `BuildEnumData` builds that flags field from
`CHARACTER_FLAG_*` (`Player.cpp:1222-1262`, setting RESTING/HIDE_HELM/HIDE_CLOAK/GHOST/RENAME/
LOCKED_BY_BILLING/DECLINED), and the client carries a long list of named `UNK*` bits, but "the
server does not set it" is not proof that "the client does not read it".

So the next step is an audit, not a guess: find out whether `GetCharacterInfo` returns a
raw-flags value beyond the ten the fork's Lua reads (a one-line client experiment would settle it,
or reading the binding), and if it does, drive the badge from a proven-free `CHARACTER_FLAG_*`
bit. The texture is ready either way: the same BLP at
`Interface\Glues\CharacterSelect\FreebornLogo.blp` drops straight into the 60x60 slot.

## Round-8 — the CVar bridge is falsified, the client is packed, and a testable fork

The user's report after round 7 was `pending='nil' probe='nil'`. That is a *different* failure from
"the choice was empty": WoW's `GetCVar` returns `''` for a cvar that exists but is empty, and
`nil` only for a cvar that does not exist at all. So neither write ever landed, and the probe
could not report its own failure because it reported *through the same missing API*. Three
independent checks now agree:

1. **No create-screen binding can set any create-packet byte but the name.** The glue registration
   blob (`.\CharacterCreation.cpp`, file `0x5f4300`-`0x5f4a00`) lists every create/select binding:
   `CreateCharacter`, `SetCharacterCreateFacing`/`GetCharacterCreateFacing`,
   `SetCharacterSelectFacing`/`GetCharacterSelectFacing`, `GetCharacterInfo`, `GetNumCharacters`,
   `GetFactionForRace`, `GetSelectBackgroundModel`, `SelectCharacter`, `CustomizeExistingCharacter`,
   `SetSelectedRace/Sex/Class`, `RandomizeCharCustomization`, `CycleCharCustomization`, … and
   **no outfit, team or appearance setter of any kind**.
2. **The stock GlueXML never uses the CVar API.** `SetCVar`/`GetCVar` appear in none of
   `CharacterCreate.lua`, `CharacterInfo.lua`, `CharacterSelect.lua`, `GlueParent.lua` — the only
   hits in the deployed archive are this project's own injected lines. A curated glue API that
   omits it fits every observation.
3. **No Freeborn cvar reached `WTF`** — not `Config.wtf`, not any `config-cache.wtf`. Registered
   cvars are what the client persists; a custom name would not be persisted either way, so this
   only bounds the story, it does not decide it.

**`Wow.exe` is packed, so binary patching is not a reliable route.** `.rdata` `0x5df000`, `.text`
is plain x86 with 42,820 DWORDs that *look* like `.rdata` pointers, yet an exact search for the
address of *any* of its own string constants returns **zero** references — including `gxWindow`
(a cvar the client certainly reads) and `CreateCharacter`. Sections `.wxl` and `.estria`
(`ESTERIA_CLIENT_FOUNDATION_V3`) are the loader's. Whatever builds the binding and cvar tables,
it is not statically present in the file. The `OutfitId` design in the header of this document
therefore needs dynamic analysis or an injected gate, and blind byte patching must not be
attempted. Treat "patch Wow.exe" as unavailable unless the user explicitly accepts that risk.

The user chose: **one more instrumented client test before deciding**, plus a glue-side
investigation of the character-select badge. That is what round 8 deployed.

### What round 8 deployed (diagnostics only — no behaviour change)

`tools/freeborn_client/CharacterCreate.freeborn.lua` gained a clearly-marked temporary section.
It is appended to the *same* managed block, so no new packer path was needed: `GlueXML.toc` loads
`CharacterSelect.xml` before `CharacterCreate.xml`, so when this block runs the select screen's
globals already exist and can be wrapped from here.

- **Panel 1/2 (character create)** reports `type(GetCVar)`, `type(SetCVar)`,
  `type(SendAddonMessage)`, `type(SendChatMessage)`, then write round-trips for a **custom** name
  and for **registered** names (`showGameTips`, `checkAddonVersion` — written and restored in the
  same call, so no setting is left changed), and a live `selected=` flag that must flip when the
  Freeborn button is clicked.
- **Panel 2/2 (character select)** reports how many values `GetCharacterInfo` actually returns,
  every value past the ten the stock Lua reads, `GetFactionForRace`/`GetSelectBackgroundModel`
  for the selected character, and every `_G` function whose name contains team/faction/pvp.

`tools/freeborn_client/addon/FreebornClaim/FreebornClaim.lua` gained `worldWrite=` in its
`/freeborn` report — the same write test run in the *world* state. Comparing the two separates
"the glue screen has no CVar API" from "this client rejects CVar names it does not already know".
Its login handler now also says so out loud when it matches, and **keeps** a non-matching
`pending` value instead of dropping it (so `/freeborn` can still report what the create screen
recorded). Clearing on match is unchanged, so a reload still cannot claim twice.

### Offline execution of the deployed Lua (new, and reusable)

`.agents/plans/freeborn-client/harness/` runs the **deployed** block and addon under fengari
(pure-JS Lua, installed to `%TEMP%\freeborn-luavm`) against WoW API stubs:

```
python .agents/plans/freeborn-client/harness/extract_block.py "G:\3.3.5a - Dev\Data\patch-Z.MPQ"
cd .agents/plans/freeborn-client/harness
$env:NODE_PATH = "$env:TEMP\freeborn-luavm\node_modules"
node run.js custom-ok 12          # also: registered-only, no-cvar
node run_addon.js custom-ok Dobby Dobby
```

This is the check that would have caught round 4's nil-index before it reached the client, and it
proves the three environments produce *distinguishable* panel text. It is a Lua 5.3 VM, not 5.1,
so it validates syntax, nil indexing and logic, not 5.1-specific semantics.

### How to read the result

| Panel 1/2 shows | Meaning | Consequence |
| --- | --- | --- |
| `GetCVar=nil SetCVar=nil` | the glue state has no CVar API | the CVar bridge is impossible; choose a different channel |
| `writes: custom=OK …` | custom names are accepted on the create screen | if `/freeborn` then shows `pending='<name>'`, the bridge works and creation-time selection needs no patch |
| `writes: custom=NO(nil) showGameTips=OK` | only names the client already knows are accepted | the bridge must borrow a *registered* cvar, which is the player's own setting — ask before writing one |

The in-world `/freeborn` line decides the last mile: `pending` non-empty proves a glue write
survived into the world session; `probe='true:true'` proves the write call succeeded even after
the claim cleared `pending`.

## Round-9 — the client's CVar rule, my crash, and a two-path bridge

The round-8 diagnostics ran in the live client and answered the question, at the cost of a bug of
mine that broke the create screen and then crashed the client:

```
Interface\GlueXML\CharacterCreate.lua:2016: Couldn't find CVar named 'freebornPendingWriteTest'
```

**The glue state has the CVar API, and it is strict: `GetCVar`/`SetCVar` raise for any name the
client does not already know.** That is the `registered-only` branch, not `no-cvar`. It also means
a CVar bridge is possible, but only through a cvar name the client already has.

### The crash, and the guard that now prevents it

Deployed line 2016 was `local before = GetCVar(name);` — **bare**. `pcall` was around every
`SetCVar` and around the panel, but not around that read, so the error escaped into the glue
screen, which is not robust enough to survive it. Fixed by funnelling every access through
`CharacterFreeborn_SafeGet`/`SafeSet`, and — more importantly — by making
`tools/test_freeborn_team_pack.py` enforce the invariant that would have caught it: **no line in
the block may call `GetCVar(` or `SetCVar(` unless it also contains `pcall(`.** That replaces the
old assertion, which only matched one exact source string and so passed while a bare read sat two
lines away.

Panel 2/2 also reported `GetCharacterInfo(1) unavailable`, which was my bug too:
`CharacterSelect.selectedIndex` was `0`, and in Lua `0 or 1` is `0`, so the probe asked for index
zero. It now clamps to 1 and retries, and reports which index answered.

### The bridge this implies

Two records, both written **only when Freeborn was chosen** (an intervening native creation must
not wipe an unclaimed choice), and neither able to claim a later character on its own because the
addon also matches the created name:

1. `freebornPending` — our own cvar name, written through `SetCVar`'s third (`scriptCvar`)
   argument, the only documented way to ask for a name the client does not already know. Clean if
   it works; the panel reports `unknown name -> OK` when it does.
2. `gameTip` — a cvar the client already knows, holding a hash of the typed name. This borrows a
   real setting: `gameTip` is the index of the next game tip, tips are off on this account
   (`showGameTips "0"`), so the parked number is invisible, and the addon gives the cvar back
   (`"0"`) on the login that consumes it. Nothing else reads it.

The hash is `(h * 31 + byte) % 2147483647` over the lowercased name, duplicated in both files; the
contract test now asserts both sides spell the carrier cvar identically and both hash at all.

Verified offline in `harness/` for four client modes (`custom-ok`, `registered-only`,
`three-arg-ok`, `no-cvar`) and five addon scenarios (claim by name, claim by carrier hash, mismatch,
foreign hash, nothing recorded), including "no double claim on the second login" and "the carrier
is untouched when Freeborn was not selected" (`gameTip` stays `76`).

### Still the user's call

The carrier borrows one of the player's own cvars. If that is not acceptable, the alternatives are
an in-world confirmation step (no borrowing, but the create-screen button stops being
authoritative) or the case-only name token that was offered in round 8.

## Round-10 — the writable set is small, and what it implies

The live run answered the round-9 questions:

| Panel 1/2 line | Result | Meaning |
| --- | --- | --- |
| `unknown name` | rejected | custom cvar names are refused |
| `3-arg SetCVar` | rejected | the `scriptCvar` argument does **not** register a name |
| `known name` (`showGameTips`) | rejected | being in `Config.wtf` does **not** mean `SetCVar` accepts it |
| `checkAddonVersion` | **OK** | at least one registered engine cvar *is* writable at glue |

In-world it read `carrier='76' pending='nil' probe='nil'` — the carrier had not moved, so nothing
crossed. `gameTip` and `showGameTips` live in `Config.wtf` yet are rejected, so the writable set is
not "whatever is persisted": it is whatever the engine happens to register at the login screen.
That is why the carrier is now **probed and judged, not assumed**: for each candidate the block
writes a hash-sized number, reads it back, and reports `exact` (survives verbatim) or `clip(1)`
(a cvar with boolean semantics would silently destroy the identity) before restoring the original.

Carriers now: `readTOS`, `readEULA`, `taintLog`, `checkAddonVersion`. All four are near-inert
(`readTOS`/`readEULA` only ever get a truthiness test that is already true, `taintLog` only writes
debug logs, `checkAddonVersion` only gates the addon version check) and the addon puts every one of
them back the moment it claims. The block writes the hash of the chosen name into each; the addon
claims when any of them matches the hash of the character that logged in, and reports what it saw
via `/freeborn` either way.

### The second bug of mine, same family as the first

`pcall(CharacterFreeborn_DiagPanel, ..., CharacterFreeborn_SelectDiagLines())` **evaluates the
builder before entering the pcall**, so the builder's errors escape it. That is what produced
`2154: Usage: GetFactionForRace(index)` on the select screen — and, because
`CHARACTER_LIST_UPDATE` re-renders the panel with real data, it fired exactly when the list
arrived, leaving the panel showing its earlier "no name yet" render. Both builders are now pcall'd
themselves, `GetFactionForRace` is no longer called from the select probe (the stock select code
uses `GetSelectBackgroundModel`, which the probe now uses too), and the contract test asserts that
each builder is pcall'd on its own. Nothing here crashed the client this time — only a dialog.

### Badge status

The runtime `_G` scan for team/faction/pvp functions found only race-to-faction helpers:
`GetFactionForRace`, `GetFactionForRaceName`, `GetRacesByFaction`, `GetRaceNamesByFaction`. There is
**no per-character team accessor at glue**, so the character-select badge cannot ask for the team
directly: it needs either an extra return value from `GetCharacterInfo` (the arity is now measured
by panel 2/2) or a client-side record of which names are Freeborn.

## Round-11 — the record crosses, the claim never ran, and the badge is in

The round-10 run answered everything it was built to answer:

- **Every probed carrier writes `exact`** on the create screen, including `gameTip` and
  `showGameTips`, which the previous build reported as rejected — so "writable" depends on the
  cvar, and only a live probe can tell.
- **`GetCharacterInfo` returns exactly 10 values** — the same ten the stock Lua reads. There is no
  hidden flags/team value, so the client cannot be asked for a character's team. The badge must be
  client-local.
- **The hash crossed the glue/world boundary**: in world, `readTOS`, `readEULA` and
  `checkAddonVersion` all held `107340`, the hash of the character just created. `taintLog`
  reverted to `1`, so it is not a carrier — dropped.
- **The addon never claimed**, and the proof is that the carriers were *still armed*. The cause was
  my own `if ( not isInitialLogin ) then return end` gate at the top of the world-entry handler: a
  gate that never opens does nothing, silently, forever. It is removed. The safety property that
  actually matters is "clear the record before sending", which the code already had, so a second
  world entry still cannot claim twice. The handler body is now pcall'd and reports its own error
  in chat, and prints the event args whenever a record is waiting, so the next silent failure is
  impossible. The contract test now asserts the gate is **absent**.

Carriers are now `readEULA` and `checkAddonVersion` — the two that demonstrably cross — with
`taintLog` dropped.

### The badge

Implemented on the client-local route the arity result forces:

- When the addon claims, it parks the character's name hash in `readTOS` as a marked record
  (`fb:3088907,...`, capped at 16). `readTOS` only ever gets a truthiness test, so a list of digits
  keeps it "accepted"; unlike the carriers it is deliberately **not** restored, because it is the
  badge's memory. The marker keeps the cvar's own earlier value (`1`) from ever parsing as a hash.
- The managed block wraps `UpdateCharacterList`/`CharacterSelect_OnEvent`, and after the stock list
  runs it hashes each visible character's name and paints
  `Interface\Glues\CharacterSelect\FreebornLogo` over the Alliance/Horde icon for the ones in the
  record. Nothing is patched in `CharacterSelect.lua`; the same block already had the wrapper.
- The packer ships that emblem (the same plate bytes as the button) as a second archive entry.

Verified in the harness: only the matching character's icon changes; a marker-less legacy value
paints nothing; a foreign hash claims nothing and leaves the record armed for the right character.

## Round-12 — the claim works; the record failed on value shape

**The feature works end to end.** After the round-11 build, `characters.teamId` for `Loo` is `3`
(`TEAM_FREEBORN`), the addon reported `persistent team Freeborn, origin team Alliance`, and the
carriers read back at their resting values because the addon consumed and returned them. The first
real claim, the first real database write, and the first real client-driven team change all
happened in that run.

**The badge record did not stick, and the reason was the value's shape.** `readTOS` still read `"1"`
in `Config.wtf`, so the write was *refused*, not overwritten: this client rejects a value that is
not a number on a cvar it parses as one. My `fb:`-prefixed marker was invented for unambiguous
parsing and was silently refused. `taintLog` reverting to `1` in the previous round is the same
phenomenon. So the rule now is: **a record is a plain number**, and nothing else is attempted.

A record is `1000000000 + (hash % 1000000000)`:

- always exactly ten digits and always below `INT_MAX`, which is the shape proven to survive;
- never confusable with a cvar's own resting value (`"1"`, `"76"`, `"0"`), which is what the marker
  was for — the offset does the same job inside the value instead of prefixing it;
- hash collisions only within `% 1000000000`, i.e. negligible, and the consequence is one wrong
  emblem.

Roles are disjoint and both sides agree by contract test:

| cvar | role | lifetime |
| --- | --- | --- |
| `checkAddonVersion` | the create screen parks the chosen name's record | consumed and restored to `"0"` on claim |
| `readTOS`, `readEULA` | where the addon parks claimed characters' records | permanent: the badge's memory |

**The harness now models value validation** — a non-digit or over-`INT_MAX` value on a numeric cvar
is refused — and the runner asserts that the wrong shape is refused. That is the check that would
have caught this before the field, so this class of failure cannot ship silently again.

Added `/freeborn claim`: it asks for the current character explicitly and remembers its emblem,
which is how a character claimed before records existed (i.e. `Loo`) gets badged.

## Round-13 — the emblem works, and the reason it kept failing

A live select screen read `FREEBORN DIAG: records gameTip=1000107340, checkAddonVersion=0, carrier 1,
matched=1 painted=1`, with `Loo`'s row showing the Freeborn emblem instead of the Alliance lion. The
diagnostic line was temporary and has been removed; the in-world `/freeborn` probe remains.

**The record had been written correctly all along. The client was erasing it.** `readTOS` held
`1003268070` (Joop's record, visible in `Config.wtf` right after the session that wrote it) and read
`"1"` immediately after the *next* client start. So the memory was gone before the character-select
screen ran, and the paint code found nothing to paint. `readEULA` is the same class of cvar. This is
the second failure in this project caused by not knowing how the client treats a particular cvar;
the contract test now *forbids* badge memory in `readTOS`/`readEULA` so it cannot be reintroduced.

The rule that came out of it: **the emblem is read at the START of a session, so its memory must
survive a client restart.** The claim carrier has the opposite requirement — it only has to survive
*within* one session, because the create screen and the login that claims it are the same client run.
That is why the roles are now:

| cvar | role | why it is safe |
| --- | --- | --- |
| `readTOS` | claim carrier, restored to `"1"` on claim | survives within a session (proven), and the client normalising it later does not matter |
| `gameTip`, `checkAddonVersion` | emblem records, never restored | not normalised by the client, and their only consumers are a tip index and a version-check flag, so a number is harmless |

Capacity is therefore **two Freeborn characters at a time**. More needs either a packed record (two
hashes per cvar) or another durable cvar; both are cheap but neither has been done.

## Round-14 — the two-sided stores, and the product decision behind them

The user chose: **a Freeborn counts as the team its race implies** wherever the server keeps one
entry per side. That closes the out-of-bounds reads (43 sites in the earlier notes) and gives the
Freeborn a side in battlegrounds, battlefields and outdoor PvP instead of none.

The change is wide but provably neutral: `PvpSideOfTeam(persistent, origin)` is the **identity for
TEAM_ALLIANCE and TEAM_HORDE**, so only Freeborn characters can behave differently. That is the
property to hold on to if this code is ever revisited.

`src/server/game/Server/PlayerTeamSide.h` holds the rule, so it can be included by the files that
need it without touching `Player.h` (which would rebuild most of the tree):

- **165 sites in 19 files** across `Battlegrounds/`, `Battlefield/`, `OutdoorPvP/` and
  `scripts/OutdoorPvP/` now go through `PvpSideOf`, including every store that was indexed by a
  player's team.
- **`Player::SetBattlegroundId` maps the team it stores.** One line, and it fixes both `bgTeamId`
  (which every battleground store, graveyard, start position and score reads) and the client's own
  team byte in `PLAYER_BYTES_3`, which previously said "Horde" for any team that was not Alliance.
- **The raid browser and achievement title reward** were indexing two-element stores too, and the
  **channel lookups** returned `nullptr` for a Freeborn, i.e. silently no channels at all. Mapped.
- An audit for anything else that indexes, switches on, or looks up a channel by a player's team
  now comes back clean; the only remaining use is `GetBgTeamId()`'s fallback in `Player.h`, which
  returns the persistent team only when the character is *not* in a battleground, and is compared
  rather than used as an index.

Two rules were applied by script (`map_pvp_team.py`, `map_channel_team.py`, `map_other_team.py`)
rather than by hand, and each script refuses to change a file when the number of matches is not
what it expects -- which is how two wrong counts were caught instead of being guessed at.

## Round-15 — the emblem is now permanent and automatic

The live run that confirmed the emblem also showed it reverting on the next client start, and the
reason was the third instance of the same trap: `Config.wtf` **did** contain
`SET gameTip "1000107340"` -- the record was on disk -- but `gameTip` is parsed as a number, so the
client clipped it to a valid tip index when it loaded. `readTOS`/`readEULA` had already been caught
being rewritten to `"1"`. The lesson is now a rule in the contract test:

> **The emblem memory must be a STRING cvar the client never parses.** `NEVER_EMBLEM_MEMORY` in
> `test_freeborn_team_pack.py` lists every integer cvar that has already burned this project, and
> the test fails if one of them is ever used as the badge store again.

The store is now `Sound_VoiceChatInputDriverName` (falling back to `...OutputDriverName`), which are
voice-chat device names for a feature that does not exist in 3.3.5, so arbitrary text there is
inert. Being strings, one cvar holds **every** Freeborn character at once -- the two-character limit
is gone -- in the form

```
fb:<record>,<record>,...|<whatever the cvar held before>
```

with the client's own value preserved behind the bar.

**It is automatic.** The character-select screen cannot be asked for a team, and no client-side
channel can carry one, so the addon asks the server on every login (the STATUS query it always had)
and watches for the reply. The server's existing line -- `persistent team Freeborn` -- is the answer
that matters, and on seeing it the addon records the character's emblem itself. No player input, and
no dependence on `/freeborn claim`, which remains as a manual fallback. Both directions are covered
by the harness (`run_auto.js`): a Freeborn reply records the emblem, a Horde reply records nothing.

## Round-16 — the STATUS reply crashed the client (fixed)

The first live run of the round-15 build died with `ERROR #134 (0x85100086) Fatal Condition` on entering
the world, three times in five minutes (`Errors/2026-09-24 06.24.48`, `06.29.22`, `06.29.52`).

The cause was the STATUS reply, not the Freeborn state: it went out as
`BuildChatPacket(..., CHAT_MSG_ADDON, LANG_ADDON, ...)`. `BuildChatPacket` writes the type as **one
byte** (`Chat.cpp:391`) and `CHAT_MSG_ADDON` is `0xFFFFFFFF`, so the wire carried `0xFF`. The client's
chat formatter (`ChatFrame.cpp`, `Wow.exe` `0x509DD0`) validates its chat-type argument before doing
anything else -- `cmp ebx, 0x3E; jge <fatal>` -- and `0xFF >= 62`, so it raised its own fatal condition.
Every character crashed, not just Freeborn, because the addon asks STATUS on every
`PLAYER_ENTERING_WORLD`.

This is the same class of mistake as the cvar traps in rounds 13 and 15: a value chosen for its meaning
on one side of the boundary, without checking what the other side does with the bytes. Two independent
checks would have caught it -- the core's own `AddonChannelCommandHandler::Send` (`Chat.cpp:1107`) sends
server -> client addon replies as `CHAT_MSG_WHISPER` + `LANG_ADDON`, and the addon's own
`SendAddonMessage(PREFIX, body, "WHISPER", ...)` names the type it expects. `CHAT_MSG_ADDON` is a
client-side *event*, never a packet type.

Fixed in `src/server/game/Server/FreebornClaim.h`: the reply is now `CHAT_MSG_WHISPER` + `LANG_ADDON`.
The contract is otherwise untouched, so the emblem path and `/freeborn claim` are unaffected. Full
evidence chain and reusable dump tooling: `.agents/plans/freeborn-login-crash/`.

## Verification boundary

Automated, and run against the **deployed** archives on every install:

- `python tools/test_freeborn_team_pack.py` — payloads, transforms, server contract, claim
  contract, `teamId` field width, live archives, create contract. All PASS.
- `python .agents/plans/freeborn-client/verify_independent.py` — re-derives everything without
  importing the packer: stock Lua prefix byte-identical to the pristine backup, exactly one
  managed block/terminator/guard/header, name never transformed, wrapper delegates to stock, the
  button is declared once, and removing it reproduces the pristine XML exactly. PASS in both
  archives.
- The harness above executes the deployed block and addon: no syntax or nil-index errors in any
  of `custom-ok`, `registered-only`, `no-cvar`, the wrappers delegate to the stock functions, and
  the claim fires exactly once for a matching name.

Manual, and the only thing left that matters:

- Clicking Freeborn on the create screen and confirming the panels and `/freeborn` (round 8), then
  `characters.teamId = 3` for the character that was created.
- A Freeborn character must not queue for a battleground or enter Wintergrasp/outdoor-PvP until the
  43-site two-sided-array slice in this document lands.

Backups: `G:\3.3.5a - Dev\Data\_freeborn-backups\<utc>\` holds hash-verified copies of every archive
before each install; `20260924T063018Z` is the pristine, pre-Freeborn pair. The packer's `--install`
round-trips and verifies after writing.


## Round-17 — the Freeborn pick explains itself on hover

The button said only "Freeborn" (the stock one-line `GlueTooltip`), which is the one control on the
screen whose meaning is not visible on the screen. It now carries a hover panel that says what the
team is: free of both factions, no allegiance, cities open, quests from either side, free grouping
and guilding with other Freeborn, no grouping or guilding with Alliance or Horde, and complete
mutual hostility.

The border is the race tooltips' border, not a lookalike: it is the same background, the same
`Interface\Tooltips\ui-tooltip-border-maw` edge texture, the same 16px tile and the same 4px insets
as the stock `local Backdrop2` the race tooltips paint with. The block spells the table out instead
of borrowing that local -- an appended block that indexes an unresolved name takes the whole create
screen down -- so the contract test reads the four settings out of the DEPLOYED stock prefix and
requires the managed block to repeat them. If the client ever restyles its race tooltips, the test
fails instead of the two drifting apart.

The frame is built on the first `OnEnter` (never at load time), parented to `CharacterCreateFrame`
so it hides with the screen, sized from its own wrapped text the way `UpdateRaceTooltip` does, and
anchored `BOTTOM` to the button's `TOP` at +24 -- clear of the button's own "Freeborn" label. It
hides on `OnLeave`, on a fresh visit to the screen (`CharacterCreate_OnShow`) and in the
paid-service path, where the button is hidden under a live mouse and no `OnLeave` would arrive.

Evidence: `python tools/test_freeborn_team_pack.py` (payload, transforms, server/claim contract,
`teamId` width, both live archives incl. the backdrop-drift check) PASS;
`.agents/plans/freeborn-client/verify_independent.py` PASS in both archives, with the stock Lua
prefix still byte-identical to the pristine backup and button removal still reproducing the stock
XML; and the fengari harness (`harness/run.js`, all three modes) shows one frame, strata TOOLTIP,
parent CharacterCreateFrame, 300 wide, edge `ui-tooltip-border-maw` at 16, colour 0,0,0,1, shown on
enter, hidden on leave, not rebuilt on the second hover, hidden after `OnShow`.

Open: the in-client look (label clearance, panel height against real font metrics) is a manual gate;
nothing else about this change is unverified.
