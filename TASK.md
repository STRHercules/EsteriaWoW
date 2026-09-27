# Freeborn third TeamId: Esteria implementation guide

**Baseline:** EsteriaWoW checkout inspected September 23, 2026. This is an implementation handoff, not a claim
that Freeborn is already implemented or live. Source request:
`Freeborn_Third_TeamId_Implementation_Specification.md`.

## 1. Contract to implement

Freeborn is a real, persisted player `TeamId`. Keep three distinct answers:

- Persistent player team: `Player::GetTeamId()` / `characters.teamId` = Alliance, Horde, or Freeborn.
- Race origin: `GetOriginTeamId()` / real race DBC = Alliance or Horde.
- BG/arena match side: `GetBgTeamId()` / match assignment = Alliance or Horde.

Required examples: Human Freeborn = `(Freeborn, Alliance)`; Orc Freeborn = `(Freeborn, Horde)`.
Neither a race ID, DBC faction-template ID, flag, nor `TEAM_NEUTRAL` is Freeborn identity. A Freeborn character's
race, model, start data, and race-origin `ChrRaces.TeamID` stay unchanged. Do not add a third BG/arena side.

The checked-in enum is `TEAM_ALLIANCE=0`, `TEAM_HORDE=1`, `TEAM_NEUTRAL=2` in
`src/server/shared/SharedDefines.h:768-773`. Reserve `TEAM_FREEBORN=3` **if** the final full-tree and external-module
numeric audit finds no collision. Preserve `TEAM_NEUTRAL=2`. The separate `Team` enum uses DBC-style `HORDE=67`,
`ALLIANCE=469`, and `TEAM_OTHER=0`; do not convert those values to `TeamId` values.

## 2. Confirmed Esteria baseline and immediate hazards

These are source/config observations, not live-client or live-DB results.

- `Player.h:2142-2145`, `Player.cpp:6007-6035`: `GetTeamId(true)` derives origin, while
  `SetFactionForRace()` overwrites `m_team`. Preserve the former and separate faction-template refresh from
  persistent-team mutation.
- `Player.cpp:526,2283`, `PlayerStorage.cpp:5167`, `Unit.cpp:14981`: creation, login, GM-state restore, and
  unit restore call `SetFactionForRace()`. None may silently reset Freeborn to origin.
- `Player.h:2330`, `Battleground.cpp:692-698`: `GetBgTeamId()` falls back to persistent team, but BG side
  arrays require a value below `TEAM_NEUTRAL`. Establish a validated A/H match side before indexing.
- `SharedDefines.h:3725-3752`: `GetPvPTeamId()` maps any non-A/H value to PvP neutral. Never convert
  persistent Freeborn through it when a match side is required.
- `BattlegroundQueue.cpp:148-149,221-245`: queue `teamId` starts as player team and feeds two-side wait arrays.
  Assign Freeborn a two-side queue/match team without changing persistent or origin team.
- `CharacterDatabase.cpp:43-76,337-347`, `Player.cpp:15122,15242`: enum, login, insert, and update SQL omit
  `teamId`. Add it and keep bind/result offsets aligned.
- `CharacterCache.h:27-41`, `CharacterCache.cpp:63-115,291-301`: cache stores race; offline team lookup derives
  from race; a missing entry returns `0` (Alliance). Cache persisted team, distinguish misses from Alliance,
  and refresh on creation, conversion, race change, and dump import.
- `CharacterHandler.cpp:265-278`, `Player.cpp:485-490`: create packet carries `OutfitId`, currently ignored by
  `Player::Create()`. Treat it only as a candidate transport field until the client is audited.
- `LFGMgr.h:428-439`, `LFGMgr.cpp:999-1051`: two-slot raid-browser stores index by `GetTeamId()`. Route Freeborn
  through a validated display bucket or redesign that store; never index with `3`.
- `LFGMgr.cpp:2714-2719`: cross-faction LFG routes its internal team to Alliance. Keep that routing separate
  from persistent team and verify mixed LFG cooperation.
- `ConditionMgr.cpp:126`: any non-Alliance player becomes Horde for `CONDITION_TEAM`. Define Freeborn behavior
  explicitly; never let the ternary classify it as Horde.
- `mod-world-chat/src/WorldChat.h:60`, `WorldChat.cpp:126`: `TeamColored` has three entries indexed by team ID.
  Add a checked Freeborn color/label or switch; ID `3` must not index this array.
- `LuaEngine/methods/*/MapMethods.h`: `team >= TEAM_NEUTRAL` means all teams. Replace range tests with an
  explicit neutral-sentinel test so Freeborn `3` is filterable.

The repo's race registry currently lists IDs `1-28` plus Darkfallen `43/44` in
`modules/mod-custom-server/data/races/race_registry.json:78-325`. Darkfallen `43/44` share a race mask but have
opposite origin teams. The registry is not proof that every ID is selectable in the active client or present in
the deployed DBCs. “Any playable race” means every race actually accepted by the deployed server/client pair.
Do not backfill from a stock race table, displayed race name, or race mask.

`env/dist/etc/worldserver.conf:4493-4534` enables the existing two-side chat/channel/group/guild/arena/auction
settings; `env/dist/etc/modules/WorldChat.conf:22` enables cross-faction world chat. These are file values, not
proof of the running container's effective config. `mod-Faction-Free` is a manual patch package, not an ordinary
CMake module (`Modules.md:146-148`). Preserve verified existing behavior, and compare the deployed source/DBC
and config before claiming Freeborn can use both sides' NPCs.

## 3. Foundation and migration work package

1. Freeze a baseline: record commit, dirty-tree diff, running worldserver build/config, character DB schema,
   `SELECT race, COUNT(*) FROM characters GROUP BY race`, and hashes of active server DBCs and client archives.
   Back up the character DB before migration. Do not overwrite the unrelated deleted
   `FREEBORN-IMPLEMENTATION.md` working-tree entry.
2. Inspect deployed `ChrRaces.dbc`: for every race in `characters` and every selectable race, resolve the current
   race `TeamID` through the same logic as `Player::TeamIdForRace()` (`1` Horde, `7` Alliance at
   `Player.cpp:6007-6023`). Abort migration on missing/invalid rows. Compare with the registry, especially
   Darkfallen `43/44`, rather than assuming either source alone is authoritative.
3. Add one incremental migration under `data/sql/updates/pending_db_characters/`. Introduce nullable
   `characters.teamId` first; backfill all existing rows to `0`/`1` from the verified race-ID mapping; assert
   zero null/unmapped/invalid values; then make it `TINYINT UNSIGNED NOT NULL`. Do not default unknown rows to
   Alliance, and do not migrate any existing character to `3`. MySQL DDL may commit implicitly: use a tested
   backup/rollback plan, not an assumed all-or-nothing transaction. Do not edit base/archive/merged SQL.
4. Add `TEAM_FREEBORN` in `SharedDefines.h`; keep `TeamIdForRace()` race-derived. Add
   `GetOriginTeamId()` using the player's **real** race (`getRace(true)` is the existing origin convention),
   `IsFreeborn()`, and a validated persistent-team setter. Keep `GetTeamId(true)` as a compatibility alias until
   its callers are classified. The setter accepts only `0`, `1`, `3`; it updates DB/cache and fires a team-change
   notification once, with a distinct initial-load path that does not issue an update.
5. Refactor `SetFactionForRace()` so refreshing a race faction template no longer overwrites persisted team.
   Re-check every caller in the baseline table, including GM exit and charm/transform restoration. On create,
   initialize native origin team before start-data setup, then apply requested Freeborn team. On load, read and
   validate `characters.teamId` after real race is known; reject corrupt values instead of silently recasting.
6. Update `CHAR_INS_CHARACTER`, `CHAR_UPD_CHARACTER`, `CHAR_SEL_CHARACTER`, both enum queries, their bind/result
   offsets, `_SaveCharacter()`, `LoadFromDB()`, and `Player::BuildEnumData()`. Append enum query fields after the
   current columns so existing index assumptions remain stable. Update `CharacterCacheEntry`, startup/refresh
   SQL, create, rename/customize/race-change paths, and `Tools/PlayerDump.cpp` import/export handling.
7. Keep race change and Freeborn conversion separate. The existing faction-change handler
   (`CharacterHandler.cpp:2084-2606`) rewrites taxi, quests, reputation, guild, and arena membership. A
   Freeborn-only team conversion must not call that destructive path. A race change while Freeborn updates origin
   from the new race but leaves persisted team `3`; a native race/faction change sets its new origin team.

**Foundation gate:** Existing characters all read back as origin team; native and Freeborn test characters retain
the exact DB/API team after logout and worldserver restart. Creation, login, GM exit, transform/charm recovery,
cache refresh, and race change do not reset Freeborn. No client release before this gate passes.

## 4. Character creation and client signaling

The active developer client contains `Data/patch-Z.MPQ` and `Data/enUS/patch-enUS-Z.MPQ`; the project packer
targets both (`tools/darkfallen_race_pack.py:44-48,1231-1249`). The older unpacked Worgoblin
`CharacterCreate.lua` still says `MAX_RACES=15` in
`modules/mod-worgoblin-high-elf/data/patch-A.MPQ/Interface/GlueXML/CharacterCreate.lua:2`.
Inspect the **winning** GlueXML in both active archives and the active `Wow.exe`/`Client.dll`/`WarcraftXL.dll`
contract before editing; lower-priority unpacked Lua is only a reference.

1. Add the requested Freeborn button between the gender buttons in winning `CharacterCreate.xml` and matching
   Lua. Keep explicit selection state when race/gender changes. Deselecting Freeborn restores the selected
   race's origin team. Preserve the race ID, appearance, class availability, and start template.
2. Trace the actual client `CMSG_CHAR_CREATE` writer and current `OutfitId` values. If one `OutfitId` bit is
   proven unused end to end, reserve it in a named client/server contract; decode and clear it at the server
   trust boundary. Reject malformed or unsupported values. Old clients must still create native characters.
   Do not assume `0x80` or change packet length merely because the source spec offered it as an example.
3. Apply creation restrictions deliberately: expansion/class/race validation still uses the selected race;
   account team policy and any team-disabled mask must evaluate the requested persistent team explicitly.
   The current `CharacterHandler.cpp:280-288,477-490` checks only race-origin team; settle the Freeborn account
   and disable-mask rules in that path before enabling creation.
   Run the native Human/Orc and Freeborn Human/Orc four-case creation matrix before expanding to every
   selectable race.
4. Add `teamId` to the character enum DB query and derive a Freeborn marker from it. Use only a flag bit or
   existing side channel proven free in the exact customized client. Keep racial select background from the
   actual race; add a separate Freeborn badge. Do not use shared display names to infer identity.
5. For in-world portrait, nameplate, tooltip, `/who`, and emblem requirements, select one verified existing
   update/addon/WXL transport. All presentation data is derived from `characters.teamId`; do not persist a
   second client-side truth. Validate hostile target/assist behavior in the client: server reaction changes may
   need client runtime support if the client still predicts race-faction friendliness.
6. Before writing MPQs, hash and back up the winning root and enUS archives, patch both as needed with the
   repository StormLib tooling, verify entry round-trips and priority, then test after a full client restart.
   Do not alter `Wow.exe` or bypass its image fingerprint contract without separate authorization.

**Client gate:** the UI creates both native and Freeborn versions of the same race, the server stores the
requested team, character select shows Freeborn without losing the race background, and in-world indicators
and targeting agree after relog. An MPQ self-test alone is not this gate.

## 5. Relationship and PvE work package

Use the existing central reaction/attack paths instead of per-spell patches. `Unit::GetReactionTo()` already
handles owner, duel, raid, FFA, reputation, and a `ScriptMgr::IfNormalReaction` hook
(`Unit.cpp:7125-7220`). `_IsValidAttackTarget()` and `_IsValidAssistTarget()` are the enforcement paths
(`Unit.cpp:10751-10945`). Resolve pets, guardians, vehicles, and charmed units through their affecting player.

Relationship precedence for a Freeborn-involved pair:

1. Same owner/self, duel, and active BG/arena side follow explicit context rules. A match side is always A/H.
2. Same valid party/raid/LFG group is friendly, assistable, and nonattackable while that group lasts.
3. In sanctuary/capital and other no-PvP areas, suppress ordinary Freeborn hostility and hostile targeting.
4. Otherwise Freeborn versus A, H, **or another Freeborn** is hostile symmetrically only when existing PvP
   eligibility permits attack. Trading, whispering, and inspecting remain independent permissions.
5. Native A/H versus native A/H and ordinary monster behavior follow existing Esteria policy.

Important edge: the source's “ordinary hostility” wording and its “completely protected in capitals” acceptance
line conflict for explicit duels. The current core checks duel before sanctuary
(`Unit.cpp:10860-10882`). Resolve this as a product decision before implementing the safe-area branch;
the strict acceptance interpretation blocks Freeborn-involved duels in capitals and sanctuaries too.
Use `AREA_FLAG_CAPITAL`, `AREA_FLAG_SLAVE_CAPITAL2`, and `AREA_FLAG_SANCTUARY` from `DBCEnums.h:239-245`;
verify effective zone/subzone behavior, especially on PvP realms, rather than hardcoding city names.
Do not force the FFA flag to simulate Freeborn hostility.

For player-versus-NPC, first prove the running Faction-Free DBC/core behavior for both Freeborn origins, guards,
neutral vendors, and monsters. Grant A/H service interactions without making all creatures friendly. Update
`ReputationMgr`, quest eligibility, `CONDITION_TEAM`, taxi node discovery, and faction-side reward checks only
at the actual gate that rejects Freeborn. Preserve class, level, profession, prerequisite, and true race
requirements. Existing origin-based start taxi and reputation setup should remain origin-based
(`PlayerTaxi.cpp:36-81`, `Player.cpp:6150`). Do not make every non-Alliance Freeborn a Horde character through
fallback ternaries (`ConditionMgr.cpp:126`, `Player.cpp:6250`).

For equivalent A/H quest pairs, start with a reviewed list of actual IDs and existing exclusive-group data.
Add a dedicated mapping migration only for pairs that need it. Prefer origin-side presentation and prevent
double rewards; unrelated opposite-side quests remain available. Avoid a speculative empty mapping table.

**PvE/PvP gate:** a Freeborn Human and Horde-origin Freeborn can use A/H NPC services, gain/save both reps,
learn/save both taxi networks, and quest both sides. Freeborn-to-A/H and Freeborn-to-Freeborn attacks are
symmetric in PvP-enabled contexts, blocked where PvP eligibility forbids them, and group healing works.

## 6. Social, grouping, LFG, and instance work package

- Manual group/raid: In `GroupHandler.cpp:119` and accept/reinvite paths, allow Freeborn only with Freeborn.
  Keep native A/H config behavior. `AllowTwoSide.Interaction.Group=1` must not bypass this special rule.
- Guild: Gate invite, accept, petition, and offline/cache paths by persistent team (`Guild.cpp:1494,1537`,
  `PetitionsHandler.cpp:458`). Freeborn guilds may mix race origins; guild membership does not grant friendship.
- Arena team: Restrict Freeborn membership at invite, accept, and charter paths; keep native behavior. Match
  combat uses A/H side (`ArenaTeamHandler.cpp:132,183`).
- LFG: Allow mixed A/H/Freeborn matchmaking. `LFGMgr::SetTeam()` remains a queue/group bucket, not a persistent
  team mutation. Verify healing, loot, teleport, reconnect, and relationship reset on leave.
- Raid browser: Its four `[2]` stores and all `GetTeamId()` indices need explicit two-side routing or keyed
  storage. Cover add, browse, remove, cache, and reconnect.
- BG/arena: `GroupQueueInfo::teamId`, wait/score/objective/graveyard arrays, queue entry, and
  `SetBattlegroundId()` use a validated A/H match side. `Player::GetTeamId()` stays Freeborn; avoid origin-only
  assignment.
- Open-world graveyards and honor: Audit `Player.cpp:5031,11499,6325,6644` and
  `GridNotifiers.h:125-153`; select origin, match, or PvP relationship explicitly.
- Chat, trade, mail, AH: Preserve current cross-faction options. Test Freeborn through
  `ChatHandler.cpp:429`, `TradeHandler.cpp:827`, `MailHandler.cpp:187-224`, channels, world chat, and auctions.

The specification deliberately grandfathers existing group/guild memberships through conversion while
restricting **new** invitations. Record this exception in command behavior and QA: a converted member can remain
in an otherwise mixed guild, but guild membership does not make Freeborn guildmates friendly. Do not silently
remove members or use the destructive faction-change routine to enforce the new-invite rule.

**Instance gate:** Freeborn can queue on either A/H BG side and join rated/skirmish arena as allowed. Queue,
entry, score, objectives, spirit guide, leave, and rejoin all preserve `GetTeamId()==TEAM_FREEBORN`; every
match-indexed value is 0 or 1. Mixed LFG works and hostility returns after separation.

## 7. Commands, Eluna, and modules

Add RBAC-protected `.playerteam status`, `.playerteam set freeborn`, and `.playerteam set native` operations
through the single validated setter. Online/offline updates must refresh DB, cache, client marker, reaction,
and relevant visibility. Reject unrecognized/bot targets and invalid enum values. Status reports persistent
and origin teams. A bot must never be generated or converted as Freeborn; normal A/H bots remain player targets.

The existing AzerothCore Eluna `Player:GetTeam()` returns `GetTeamId()`
(`src/server/game/LuaEngine/methods/AzerothCore/PlayerMethods.h:1435-1437`). Preserve that API's current meaning;
add named `GetTeamId`, `GetOriginTeamId`, `IsFreeborn`, and a safe setter as needed, with constants. Audit all
five Eluna method families, especially `MapMethods.h` range-sentinel checks, plus global team filters and
script hooks. The existing `OnPlayerUpdateFaction` hook is a faction-template event, not automatically the new
persistent-team-changed event. Modules should use the core API, not query `characters.teamId` themselves.

Finish a bounded whole-tree audit of `GetTeamId()`, `GetTeamId(true)`, `TEAM_NEUTRAL`, `TEAM_ALLIANCE/HORDE`,
`MAX_TEAMS`, A/H ternaries, `[2]`, and team-as-index in enabled modules. Classify each use as persistent,
origin, match, sentinel, or social policy. Prioritize `mod-playerbots`, `mod-world-chat`, `mod-anticheat`,
custom race code, AutoBalance if enabled, and any active Faction-Free replacement files. Do not mechanically
replace every `GetTeamId()` with origin or increase every array to three.

## 8. Verification and release sequence

Follow repo task rules before implementation: read `.agents/docs/cpp-guidelines.md` for C++,
`.agents/docs/sql-guidelines.md` for migrations, `.agents/docs/cpp-scripts.md` for script work, the relevant
systems docs, and `.agents/docs/build.md` before requested builds/tests. Keep SQL in pending update paths.

- A — Baseline: live schema/race inventory, deployed DBC/archive hashes, effective config/modules, call-site
  classification, and rollback backup.
- B — Persistence: migration counts/readback, four Human/Orc creation cases, relog/restart, race change, dump
  import, online/offline cache, and zero accidental Freeborn migrations.
- C — Client: create-packet capture, root/enUS archive round-trip, native/Freeborn creator/select, in-world UI,
  relog, and targeting.
- D — Behavior: A/H/Freeborn NPCs, quests, reputation, taxi, PvP flags/areas, pets, social invitations,
  trade/mail/chat/AH, and mixed LFG.
- E — Two-side safety: Freeborn BG/arena queue and match matrix, checked side indices, objectives, scoreboard,
  graveyards, and focused assertions or sanitizer coverage where practical.
- F — Regression: native A/H, custom races including Darkfallen, Playerbots, Eluna, enabled modules, and
  migration/diff review.

Build only when explicitly requested under the repository rules. This document request does not authorize
a build, DB migration, MPQ edit, or worldserver restart. Keep runtime assertions, DB receipts,
archive self-tests, and live WoW behavior as separate evidence. Report any manual client gate still open.

For each phase, hand off files changed, migration/backup, client and server contract, focused checks, and
remaining risks. The end state must satisfy the source specification's complete behavior matrix without
changing native character behavior or using persistent `TEAM_FREEBORN` in two-sided arrays.
