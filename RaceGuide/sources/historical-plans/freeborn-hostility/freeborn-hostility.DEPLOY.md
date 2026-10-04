# Freeborn hostility — deployed artifacts, verification, revert

Updated after the first live test failed. Two findings from that round:

1. **The Eluna apply path could never work in this tree.** `RegisterPlayerEvent`-based Lua is
   inert here: every Eluna hook entry point is defined but never called
   (`Eluna::OnLogin` — `src/server/game/LuaEngine/hooks/PlayerHooks.cpp:417` — plus `OnLogout`,
   `OnChat`, `OnUpdateZone`, `OnSpellCast`, … have zero callers anywhere in the tree, and no module
   or `PlayerScript` subclass forwards to them). The interim script was removed; the apply is now
   core code. Side note worth a separate look: the fork's other event-driven Lua scripts
   (`racials.lua`, `transmog.lua`, `teach_riding_worgen.lua`) rely on the same missing bridge.
2. The DBC rows and the client table were deployed correctly (server log:
   `FactionTemplate.dbc1-freeborn -> 15 row(s) into FactionTemplate.dbc`).

## Quest access across both factions (third revision)

3.3.5 expresses faction-side quest availability two ways, and both blocked Freeborn characters:

| gate | live data | before | now |
| --- | --- | --- | --- |
| `quest_template.AllowableRaces` (`SatisfyQuestRace`, used by `CanSeeStartQuest` and `CanTakeQuest`) | 2542 quests carry a mask that excludes Night Elf (Horde-side and custom-race masks, e.g. `2821317554`); 2401 include it | a Freeborn Night Elf was refused with `INVALIDREASON_QUEST_FAILED_WRONG_RACE` for every opposite-side quest | `SatisfiesQuestRaceMask` lets a Freeborn ignore the mask; natives still match their own race |
| `CONDITION_TEAM` (`ConditionMgr`, the `GetTeamId() == TEAM_ALLIANCE ? ALLIANCE : HORDE` ternary) | 535 condition rows (276 Alliance, 259 Horde) on creature/gameobject/reference loot, gossip menus, spell targets, spell-click events and SmartAI events; none on quest availability | a Freeborn was classified as **Horde**, so Alliance-side conditions silently failed while Horde-side ones passed | `SatisfiesTeamCondition` satisfies either side for a Freeborn and never classifies it as Horde |

Both helpers live in `src/server/shared/SharedDefines.h` and are covered by
`FreebornTeamTest.QuestRaceMaskDoesNotBlockFreeborn` and
`FreebornTeamTest.TeamConditionsAreSatisfiedByBothSidesForFreeborn`.

Worth knowing:

* Faction-masked quests become available on both sides at once, so a Freeborn sees both the
  Alliance and the Horde variant of paired quests. The specification's "prefer the origin side's
  duplicate" rule is **not** implemented — it needs a quest-pair mapping, and it is a preference
  (extra options), not a blocker.
* Satisfying both sides of a `CONDITION_TEAM` can make both variants eligible where content assumed
  exactly one (two loot rows, two gossip options). The specification asks for both sides' rewards,
  but this is where to watch for doubled content.
* Reputation-gated quests behave as for any character: a Freeborn starts with its race's standings
  and can earn the other side's reputation, which the Faction-Free data already permits.
* Note for future data work: the Faction-Free module's `UPDATE quest_template SET AllowableRaces =
  1791 WHERE AllowableRaces IN (1101, 690)` only covered masks that were exactly the stock team
  masks; the fork's custom-race masks (high bits) never matched, which is why 2542 quests are still
  one-side-only.

## Group and guild policy (second revision)

Hostility worked after the first rebuild; this revision adds the two social rules from the
specification. Both are *additive*: they ignore `AllowTwoSide.Interaction.Group/Guild/Arena`, which
this realm has enabled, and they compare persistent teams only (never race origin).

| rule | where |
| --- | --- |
| Freeborn manually group only with Freeborn | `HandleGroupInviteOpcode` (rejects with `ERR_PLAYER_WRONG_FACTION`) and `HandleGroupAcceptOpcode` (re-checks, because an invite can be stale). The helper `IsTeamCompatibleWithGroup` resolves a group's kind from its leader and every member, reading offline members from the character cache. |
| Freeborn guild only with Freeborn | `Guild::AddMember` — the single choke point used by invite accept, charter turn-in, the GM `.guild add` command and `mod-starter-guild`. The guild's kind is its leader's persistent team. `Guild::HandleInviteMember` rejects early with `ERR_GUILD_NOT_ALLIED`. |
| Freeborn sign only a Freeborn's charter | `HandlePetitionSignOpcode`, guild charter branch (`ERR_GUILD_NOT_ALLIED`). The turn-in re-checks through `Guild::AddMember`. |
| Freeborn arena team only with Freeborn | `HandlePetitionSignOpcode`, arena charter branch (`ERR_ARENA_TEAM_NOT_ALLIED`), per the specification's "arena team/group creation follows the same restriction". |
| Starter guild skips Freeborn | `modules/mod-starter-guild/src/mod_starterguild.cpp` — the starter guilds are native, and the hook otherwise retries on every level-up. |
| Shared predicate | `IsFreebornCooperativeTeamPair` in `src/server/shared/SharedDefines.h`, covered by `FreebornTeamTest.CooperationIsLimitedToMatchingFreebornState`. |

Deliberately unchanged:

* **Grouped players are not hostile.** `Unit::GetReactionTo` already returns `REP_FRIENDLY` for
  `IsInRaidWith` (parties and raids) *before* the Freeborn hostility branch, so grouped Freeborn —
  and mixed LFG groups — cannot attack each other. Note the client still paints a grouped Freeborn
  hostile, because its reaction comes only from faction templates; the server refuses the attack.
* **Guild membership does not make players friendly.** Two Freeborn guildmates outside a group stay
  hostile, as the specification requires.
* Battleground, arena, battlefield and LFG groups are cooperative contexts and never pass through
  the manual handlers, so mixed LFG still works.
* Trade, mail, chat, whispers, inspect and auction house remain unrestricted across teams.

Verification for this revision: `Francesca` (Freeborn) must fail to invite or be invited by
`Larry` (Alliance) with a faction error, and must be able to invite another Freeborn; a Freeborn
must fail to join an Alliance/Horde guild (invite, charter signature and `.guild add`) while two
Freeborn can guild together; and a Freeborn + native party must not be attackable if one somehow
already exists.

## What is changed

### DBC (deployed, no build needed)

Generated from the base table `modules/mod-Faction-Free/dbc/FactionTemplate.dbc`, SHA-256
`a344d554…` — the table the client loads from `Patch-F.MPQ` and the server from
`env/dist/data/dbc/`:

| row | change |
| --- | --- |
| `1,2,3,4,5,6,83,84,115,116,1610,1629,1801,1802` (every template a player can wear) | `ourMask \|= 16`; `hostileMask \|= 8` (only 83/84 lacked it) |
| new row `2237` (`faction 893`, an unused `Faction.dbc` id with `reputationListID < 0`) | `ourMask 9`, `friendlyMask 6`, `hostileMask 24`, `flags 0x48` |

Resulting relationships: Freeborn ↔ any player hostile both ways, Freeborn ↔ Freeborn hostile,
Freeborn ↔ monsters hostile both ways (PvE unchanged), Freeborn → guards/civilians friendly, and
every other pair byte-identical to before.

Deployment:

| piece | location |
| --- | --- |
| server rows (live) | `ac-worldserver:/azerothcore/env/dist/data/dbc-continuations/FactionTemplate.dbc1-freeborn` — that path is the named volume `esteriawow_ac-client-data`, so it survives container recreation |
| server rows (repo copy) | `modules/mod-custom-server/data/dbc-continuations/FactionTemplate.dbc1-freeborn` (SHA-256 `2adbed4f…`, identical to the deployed file); to make the rows reproducible from a checkout — and survive a volume reset — bind-mount that file over the volume path the way `AreaTable.dbc` and `SkillRaceClassInfo.dbc` already are: `- ./modules/mod-custom-server/data/dbc-continuations/FactionTemplate.dbc1-freeborn:/azerothcore/env/dist/data/dbc-continuations/FactionTemplate.dbc1-freeborn:ro` |
| client table (archive) | `Data\patch-Z.MPQ` → `DBFilesClient\FactionTemplate.dbc` |
| client table (folder patch, hedge) | `Data\patch-K.mpq\DBFilesClient\FactionTemplate.dbc` — the same folder-patch route WarcraftXL already serves (`CreatureDisplayInfo.dbc1-battlemon` is read from there) |
| client backups | `Data\_freeborn-hostility-backups\20260924T233242Z\patch-Z.MPQ` (SHA-256 `774fcf8c…`) |

### Core (needs a worldserver image rebuild)

* `src/server/shared/SharedDefines.h`: `FREEBORN_FACTION_TEMPLATE = 2237`.
* `Player::SetFactionForRace` (`Player.cpp`): a Freeborn outside a battleground wears
  `FREEBORN_FACTION_TEMPLATE`, everyone else keeps `ChrRaces.FactionID`. This is the single choke
  point that login, creation, race change, `.reset`, charm/disguise restore
  (`Unit::RestoreFaction`) and the Freeborn claim all route through.
* `Player::SetPersistentTeamId`: re-applies the template when a character becomes or stops being
  Freeborn.
* `Player::SetBattlegroundId`: refreshes the template on battleground entry and exit, so inside a
  match a Freeborn keeps its race template and its own side stays friendly.
* A `LOG_INFO("server", "Freeborn <name> wears faction template 2237")` line fires whenever the
  template changes, so the next test is diagnosable from `env/dist/logs/Server.log`.

## Verification

1. Rebuild and recreate the worldserver:
   `docker compose up -d --build ac-worldserver`
2. Fully exit and relaunch the game client (the DBC layer is read at startup).
3. Log in as `Francesca`. `env/dist/logs/Server.log` must gain
   `Freeborn Francesca wears faction template 2237`.
4. Log in as `Larry`, meet in Stranglethorn Vale, `/pvp` on both. Expect from **both** clients:
   hostile/red name and auto-attack working.
5. Checks that must NOT change: city guards/civilians stay friendly to `Francesca`, ordinary mobs
   still attack her, two native characters behave exactly as before.

If step 3 logs but step 4 still shows green, the remaining suspect is the client-side table
delivery (the `patch-Z.MPQ` entry and the `patch-K.mpq` folder copy are both our patched table, so
the next step would be to confirm which archive the client actually reads — the client's
`Logs\wxl-core.log` shows the WXL storage layer's activity).

## Revert

```powershell
# core: git restore src/server/game/Entities/Player/Player.cpp src/server/shared/SharedDefines.h
# client
python tools\freeborn_faction_pack.py --restore-client `
  "G:\3.3.5a - Dev\Data\_freeborn-hostility-backups\20260924T233242Z\patch-Z.MPQ"
Remove-Item "G:\3.3.5a - Dev\Data\patch-K.mpq\DBFilesClient\FactionTemplate.dbc"
# server rows
docker exec ac-worldserver rm /azerothcore/env/dist/data/dbc-continuations/FactionTemplate.dbc1-freeborn
docker restart ac-worldserver
```

## Known limits

* Battlegrounds keep the previous behaviour (race template inside a match): BG hostility on this
  faction-free realm is unchanged, and the Freeborn's own side is never coloured hostile.
* Pre-existing, unrelated: because the deployed table makes every player template friendly to both
  groups, native Alliance vs Horde is also friendly in the open world. That is the Faction-Free
  package's design, not something this change introduces.
