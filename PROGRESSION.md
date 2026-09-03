# Unified AzerothCore Progression Ecosystem

## Objective

Implement and integrate the following AzerothCore systems into one cohesive progression ecosystem:

1. `Youpeoples/Prestige-and-Draft-Mode`
2. `teodorgross/mod-seasonpass` / Dream Path
3. `vibecoder99-cmd/echoes-of-the-worldsoul`
4. `silviu20092/mod-mythic-plus`
5. `InstanceForge/mod-dungeon-master`

The five systems must feel like parts of one server design rather than independent modules.

## Execution Status (2026-08-27)

Phase 2 Prestige & Draft is the active gate. Phase 1 client assets are staged
in the working client. The current checkout is `custom-server` at
`af4835044b9b0284c8ed47b575e3912bdae488a0` and the existing Docker stack is
running with PlayerBots, standard Eluna, AutoBalance, Challenge Modes, and
Individual Progression enabled. The active client already contains unrelated
patch content, including `Patch-O.mpq`; client launch and gameplay remain
separate verification gates.

Current boundaries:

* `mod-playerbots`, `mod-autobalance`, `mod-challenge-modes`,
  `mod-individual-progression`, and `mod-learn-spells` are already present.
* `Echoes of the Worldsoul` is in live Phase 1 staging. The adapted C++ bridge
  is built into the active worldserver image, the pending character/world SQL
  is imported, the canonical standard Eluna scripts are active, and the
  load-time probe has passed. Its client assets are now staged; live client
  launch and gameplay/regression gates remain open.
* `Prestige-and-Draft-Mode` is manually live-staged: character/world SQL,
  Lua scripts, server DBCs, `patch-P.mpq`, and the `PrestigeSystem` addon are
  installed; Standard/Draft gameplay gates remain open.
* `mod-seasonpass` is an alpha C++/SQL/addon project whose current config does
  not expose the internal Prestige, Paragon, or mob-scaling gates required by
  this document.
* `mod-mythic-plus` has no README or CMake file in the audited revision and its
  shipped SQL currently defines levels 1 through 7; it requires a source and
  compatibility audit before installation.
* `mod-dungeon-master` includes the expected CMake/config/SQL pieces but is
  explicitly early-development software and must be isolated from AutoBalance
  and Challenge Modes before it is enabled.

No additional roadmap C++ module beyond the existing baseline has been
installed. The required database backup is complete outside the repository.
Echoes and Prestige runtime staging is recorded below; client launch,
player-login, regression, and gameplay verification remain gated.
Permanent progression must remain independent from seasonal and run-only
systems.

## Phase 0 Evidence Record (2026-08-27)

This is an inventory checkpoint, not a claim of live gameplay compatibility.

| Area | Confirmed baseline | Gate |
| --- | --- | --- |
| Core and Lua | `custom-server` @ `af483504`; Eluna @ `58d76521`; `Eluna.Enabled = 1` | Recorded; ALE absent |
| Runtime | Database healthy; auth/world up; database import complete | Startup evidence only |
| Existing scaling | AutoBalance on; no exclusions; minimum players `1`; Challenge Modes on | Isolate before M+/DM |
| Existing progression | Individual Progression + PlayerBots active; bot autologin; max `80` | Gameplay unrun |
| Roadmap modules | Echoes Phase 1 live-staged; SeasonPass, M+, DM absent; Prestige is external | Echoes gameplay gates open |
| Client / DBC | `Patch-A.MPQ`/`Patch-O.mpq` present; Fly Anywhere `AreaTable`; no `Patch-P` | Merge + client tests |
| Database safety | Docker uses a persistent database volume | Backup complete outside repo; hashes recorded below |

## Phase 0 Audit Record (2026-08-27)

### Database backup

The pre-import database backup is complete outside the repository at
`C:\Users\Zach\AppData\Local\Temp\azeroth-progression-backup-20260827`.
The recorded SHA-256 values are:

| Dump | Size | SHA-256 |
| --- | ---: | --- |
| `acore_auth.sql` | 184,082 bytes | `d3d54cb2028c37fdedd0d678b06d9775b0cfa950f0cfabcfd26f635e88599b6e` |
| `acore_characters.sql` | 23,620,430 bytes | `680113ee522176a30191ee05414b78824ae37c0610f00cde0466f8d87c1bd476` |
| `acore_world.sql` | 541,716,300 bytes | `b5d842bf7763df8abb883a4782cd2d140a6383dd796d545dbd3f4f0288c5d305` |

### Echoes compatibility audit

Audit target: `v1.6.0-rc1` at commit
`844bc639287d0a63564891434de7e18cb975b107` in the separate audit checkout.
`git apply --check` passes, but the release is not compatible with this core
as-is:

* The C++ patch calls `ApplyStatBuffMod` and `HandleStatModifier`; the current
  core exposes `HandleStatFlatModifier` instead. Adapt the patch to the local
  stat API before applying or building it.
* Lua's `LevelAbsorbScalar` is zero for levels 1-9, linear through level 80,
  and reaches `1.0` at level 80; the C++ patch uses a different square-root
  formula. Choose one shared progression contract before staging it.
* The C++ patch references threat-reduction spell `900001`, but the audited
  release supplies no matching Spell.dbc patch or server spell definition.
* Account/character ownership is inconsistent across `ap_mastery`, talents,
  attunement, snapshots, sinks, and residue. It does not yet satisfy the
  account-wide progression contract in this document.
* Synchronous database queries occur in login, refresh, equipped-item scan,
  and damage-hook paths. These need a cache/async-safe design before runtime
  use at scale.
* Lua performs runtime schema creation and `ALTER TABLE` operations. The
  schema must be installed through SQL first; `full_schema.sql` also needs to
  include the session, visage, and aura tables/columns added at runtime.
* Custom items `900010` and `900011` require a clean 3.3.5a `Item.dbc`, a new
  MPQ, and the addon. The active client already contains unrelated patches, so
  this remains a separate client-packaging step.
* Eluna source APIs appear present locally; the included runtime probe is now
  staged in the canonical Echoes Lua directory but has not been executed.

The audit findings above are the pre-staging compatibility baseline. Phase 1
resolved the local stat API, shared scalar, account ownership, SQL-owned
schema, and load-time probe seams. Threat reduction remains guarded until its
spell/client data exists; synchronous database reads remain a known scale
limitation for regression review. The live evidence below confirms SQL
import, Lua activation/probe, and C++ build/activation; client asset staging is
now confirmed, while client launch and gameplay verification remain open.

## Phase 1 Echoes Staging Record (2026-08-27)

The following artifacts remain staged in this repository, with live evidence
recorded for the completed installation gates:

* [x] Adapt the C++ stat bridge and register it through
  `modules/mod-custom-server/src/MP_loader.cpp`.
* [x] Add the character/world pending SQL updates, including the account-wide
  schema and custom item definitions.
* [x] Add the 20-file standard Eluna set under
  `lua_scripts/custom/echoes/` with runtime DDL removed.
* [x] Add the static contract at `apps/test_echoes_phase1.py`.
* [x] Import SQL into the live databases; all 22 Echoes `ap_*` character
  tables and world items `900010`/`900011` are present.
* [x] Copy/activate Lua in the live server and run the Eluna probe; the
  required registration and character-database APIs are available.
* [x] Build and activate the C++ module in the rebuilt worldserver image.
* [x] Install client Item.dbc/MPQ/addon assets. The working client contains
  `Data\Patch-Z.mpq` (SHA-256
  `93d2d7cc27f77fcd143a30b81a6e69e5b1147b8fedc8d62d5377f925a96ba05a`) and
  `Interface\AddOns\EchoesOfTheWorldsoulBridge`.
* [ ] Run compatibility, regression, alt, and attunement checks.

## Phase 2 Prestige & Draft Staging Record (2026-08-27)

The install boundary is verified; player-facing behavior remains untested:

* [x] Import the pending character and world SQL updates into the persistent
  `acore_characters` and `acore_world` databases. The world DBC tables contain
  `150` `dbc_skillline`, `10219` `dbc_skilllineability`, and `5174` `dbc_spells`
  rows; Chromie entry `2069426` has its template, model, and two spawns.
* [x] Stage the six standard-Eluna Prestige/Draft scripts under
  `lua_scripts/custom/prestige_draft/` and activate them in the live server.
* [x] Install the merged `CharBaseInfo.dbc` and `CharTitles.dbc` files in the
  persistent server client-data volume, and install client `Data\Patch-P.mpq`
  (SHA-256
  `e4454b83aaae2600a824dd51bf04481d8ea66d86d94d5ca96f9b6378d35437af`).
* [x] Install the `Interface\AddOns\PrestigeSystem` addon in the working
  client.
* [x] Restart the active worldserver; it reached `ready` with `exit=0` and
  `restarts=0`. Fresh logs show the Eluna probe and no Prestige Lua load/API
  errors.
* [x] Run `apps/test_prestige_draft_phase2.py` and the scoped SQL codestyle
  check; both pass.
* [ ] Verify Standard Prestige.
* [ ] Verify Draft Prestige.
* [ ] Verify leaving Draft, gear mail, and spell learning.

The intended architecture is:

```text
PRESTIGE & DRAFT
Character replay / alternate leveling builds
             ↓
DUNGEON MASTER
Procedural + roguelike dungeon gameplay
             ↓
MYTHIC+
Structured timed endgame dungeon pushing
             ↓
DREAM PATH
Seasonal goals spanning all activities
             ↓
ECHOES OF THE WORLDSOUL
Permanent account + gear progression
```

The player-facing identity is:

```text
Prestige
= Replay my character.

Draft
= Make this Prestige run play differently.

Dungeon Master
= Give me unpredictable dungeon adventures.

Mythic+
= Give me structured competitive dungeon progression.

Dream Path
= Tell me what this season rewards.

Worldsoul
= Make everything I do contribute to permanent progression.
```

---

# 1. Mandatory Ownership Rules

Each system must have a clearly defined responsibility.

| Feature                     | Owner            |
| --------------------------- | ---------------- |
| Character levels            | AzerothCore      |
| Prestige rank               | Prestige & Draft |
| Standard Prestige           | Prestige & Draft |
| Draft Prestige              | Prestige & Draft |
| Draft spells                | Prestige & Draft |
| Procedural dungeon sessions | Dungeon Master   |
| Roguelike dungeon chains    | Dungeon Master   |
| Dungeon Master tiers        | Dungeon Master   |
| Mythic Keystone             | Mythic+          |
| Mythic+ level               | Mythic+          |
| Mythic+ timer               | Mythic+          |
| Mythic+ leaderboard         | Mythic+          |
| Mythic+ affixes             | Mythic+          |
| Season tier                 | Dream Path       |
| Daily/weekly goals          | Dream Path       |
| Seasonal events             | Dream Path       |
| Seasonal runes              | Dream Path       |
| Dream Chests                | Dream Path       |
| Dream Renown                | Dream Path       |
| Permanent account power     | Echoes           |
| Item attunement             | Echoes           |
| Essence                     | Echoes           |
| Mastery                     | Echoes           |
| Crucible                    | Echoes           |
| Legacy Forge                | Echoes           |
| World Threat                | Echoes           |

Do not allow two modules to independently own the same progression concept.

---

# 2. Prestige & Draft

`Prestige-and-Draft-Mode` is the canonical Prestige system.

Preserve:

* max-level Prestige
* Standard Prestige
* Draft Prestige
* Prestige count
* Draft spell selection
* Draft spell rarity
* Draft bans/rerolls
* Prestige rewards
* Prestige history
* leaving Draft Mode
* normal non-Draft Prestige

Draft Mode must remain optional.

At Prestige:

```text
Level 80
   ↓
Prestige
   ↓
Choose:

[ Standard Prestige ]
or
[ Draft Prestige ]
```

Standard Prestige:

```text
Normal class
Normal class spells
Normal leveling
```

Draft Prestige:

```text
Draft spell pool
Random choices
Cross-class builds
Alternative leveling experience
```

Never globally force Draft Mode.

---

# 3. Dream Path

Dream Path is the seasonal progression layer.

Preserve:

* Season Path
* Adventure Track
* Hero Track
* daily objectives
* weekly objectives
* seasonal objectives
* Dream Chests
* pity mechanics
* runes
* class sets
* events
* event zones
* bounties
* Dungeon of the Week
* World Boss objectives
* Dream Storms
* fishing contracts
* supply runs
* achievements
* collections
* shop
* seasonal statistics
* addon UI

Dream Path should reward players for interacting with all other progression systems.

---

# 4. Disable Dream Path's Competing Prestige/Paragon Systems

Prestige & Draft owns Prestige.

Echoes owns permanent account progression.

Therefore Dream Path's internal Prestige/Paragon systems must be feature-gated.

Add configuration if necessary:

```ini
SeasonPass.InternalPrestige.Enable = 0
SeasonPass.InternalParagon.Enable = 0
SeasonPass.PrestigeMobScaling.Enable = 0
```

Do not permanently delete upstream implementations.

When disabled:

* Dream Path cannot reset character levels.
* Dream Path cannot maintain its own Prestige rank.
* Dream Path cannot award permanent Paragon stats.
* Dream Path cannot replace the displayed player level with its Prestige value.
* Dream Path Prestige scaling cannot alter creature difficulty.

---

# 5. Dream Renown

After completing the normal Season Path:

```text
Tier 1
 ↓
...
 ↓
Tier 100
 ↓
Dream Renown
```

Dream Renown is seasonal repeatable progression.

It may reward:

* Dream Chests
* currency
* cosmetics
* mounts
* toys
* titles
* collection progress
* moderate seasonal rewards

It must not become another permanent Paragon system.

Dream Renown resets each season.

---

# 6. Echoes of the Worldsoul

Echoes is the permanent account progression layer.

Preserve:

* Attunement
* Essence
* Mastery
* Crucible
* Legacy Forge
* Attunement Rack
* Resonant Drops
* Legacy Surge
* Visage
* World Threat
* Worldsoul Voice
* Worldsoul Residue
* account-wide progression
* extension APIs

Permanent character power should primarily originate here.

Dream Path power should primarily be seasonal.

Dungeon Master power should primarily be run-specific.

Draft power should primarily exist for the current Prestige run.

---

# 7. Install mod-mythic-plus

Repository:

```text
https://github.com/silviu20092/mod-mythic-plus
```

Install under:

```text
azerothcore-wotlk/modules/mod-mythic-plus
```

Then:

1. rerun CMake
2. rebuild AzerothCore
3. confirm `mod_mythic_plus.conf.dist` is generated
4. deploy module configuration
5. apply module SQL if automatic import does not occur
6. verify worldserver startup
7. spawn/configure Mythic+ NPC

Default upstream NPC entry:

```text
200005
```

Test using:

```text
.npc add 200005
```

---

# 8. Mythic+ Role

Mythic+ is the server's canonical:

**structured timed dungeon challenge system.**

It owns:

* Mythic+ level
* Mythic Keystone
* M+ activation
* M+ timer
* M+ completion state
* M+ rewards
* M+ standings
* M+ boss tracking
* M+ dungeon-specific scaling
* M+ affixes

The loop should remain:

```text
Choose M+ Level
       ↓
Acquire Keystone
       ↓
Enter eligible dungeon
       ↓
Group leader activates Keystone
       ↓
Countdown
       ↓
Timed Mythic+ run
       ↓
Final boss
       ↓
Timer evaluation
       ↓
Rewards + statistics
```

---

# 9. Mythic+ Dungeon Expansion

Audit:

```text
mythic_plus_capable_dungeon
```

Support as many viable Classic, TBC, and WotLK 5-player dungeons as practical.

Old dungeons should be usable at max level where supported.

Document:

```text
map
map difficulty
final boss
timer
scaling
eligible affixes
reward table
```

Do not simply enable every instance without testing encounter scripts.

---

# 10. Mythic+ Level Curve

Audit existing `mythic_plus_level` data.

Create a sensible progression curve.

Conceptually:

```text
M+1
M+2
M+3
...
M+10
...
M+20+
```

The system should provide gradual difficulty rather than enormous jumps.

Affixes should enter progressively.

Avoid excessive stat multiplication.

---

# 11. Mythic+ Rewards

Mythic+ rewards should support the greater progression ecosystem.

Potential reward types:

```text
Normal dungeon gear
Better-quality dungeon gear
Dream Path Season Points
Dream Path objective credit
Dream Chests
Echoes Essence
Attunable equipment
Cosmetics
Titles
Leaderboard recognition
```

Do not directly award huge permanent stats.

Echoes owns that progression.

---

# 12. Mythic+ → Dream Path

Add seasonal objectives such as:

```text
Complete a Mythic+ dungeon
Complete Mythic+ 3 or higher
Complete Mythic+ 5 or higher
Complete Mythic+ 10 or higher
Beat a Mythic+ timer
Beat 3 Mythic+ timers
Defeat 25 Mythic+ bosses
Complete the Dungeon of the Week as Mythic+
Complete a Mythic+ during Draft Prestige
```

Example:

```text
MYTHIC_PLUS_COMPLETE
    ↓
Dream Path
    + season points
    + objective progress
```

Do not award objective credit twice because both the final boss and dungeon completion fired.

---

# 13. Mythic+ → Echoes

Mythic+ gameplay should interact naturally with Echoes.

Allow:

* equipment attunement
* normal Essence generation
* boss-related Echoes rewards
* applicable Resonance systems
* normal gear progression

Optionally provide modest bonus Essence for successful timed clears.

Example:

```text
M+7 completed
Timer beaten

Base Echoes rewards
+
small challenge bonus
```

Avoid disproportionately large permanent rewards from repeatedly farming a trivial fast key.

---

# 14. Mythic+ + Prestige

Default policy:

Mythic+ is principally intended for max-level gameplay.

A Prestige character that has returned to level 1 should not normally enter level-80 Mythic+ content.

At level 80:

```text
Prestige character
      ↓
May run Mythic+
      ↓
May remain at 80 indefinitely
      ↓
May Prestige again later
```

This creates an intentional decision:

```text
Stay at 80:
push Mythic+

OR

Prestige:
begin another leveling journey
```

Do not force players to Prestige immediately upon reaching cap.

---

# 15. Install mod-dungeon-master

Repository:

```text
https://github.com/InstanceForge/mod-dungeon-master
```

Install under:

```text
azerothcore-wotlk/modules/mod-dungeon-master
```

Then:

1. rerun CMake
2. rebuild AzerothCore
3. apply world SQL
4. apply character SQL
5. deploy `mod_dungeon_master.conf`
6. restart worldserver
7. verify NPC spawning
8. verify normal mode
9. verify Roguelike Mode

The Dungeon Master NPC entry is:

```text
500000
```

Manual spawn:

```text
.npc add 500000
```

---

# 16. Dungeon Master Role

Dungeon Master owns:

**procedural and roguelike dungeon experiences.**

It must NOT become another Mythic+ implementation.

Normal Dungeon Master gameplay:

```text
Talk to Dungeon Master
        ↓
Choose difficulty
        ↓
Choose scaling
        ↓
Choose creature theme
        ↓
Choose dungeon
        ↓
Instance is prepared
        ↓
Themed enemies populate instance
        ↓
Boss encounter
        ↓
Completion rewards
```

Roguelike gameplay:

```text
Choose Roguelike
        ↓
Dungeon Floor 1
        ↓
Clear
        ↓
Run-specific buff
        ↓
Dungeon Floor 2
        ↓
Increasing difficulty
        ↓
Additional affixes
        ↓
Continue
        ↓
Party eventually wipes
        ↓
Record highest progression
```

---

# 17. Dungeon Master vs Mythic+

These systems must remain clearly distinct.

## Dungeon Master

Focus:

```text
Randomness
Exploration
Replayability
Roguelike runs
Random themes
Random bosses
Level scaling
Infinite dungeon chains
```

## Mythic+

Focus:

```text
Known dungeon
Known route
Timer
Keystone
Competitive difficulty
Leaderboard
Optimization
```

Do NOT merge their progression numbers.

A player reaching:

```text
Dungeon Master Roguelike Tier 12
```

does not mean:

```text
Mythic+ 12
```

They are independent challenge formats.

---

# 18. Dungeon Master + Prestige

This is a major integration opportunity.

Dungeon Master supports level-scaled gameplay and should be available during Prestige leveling.

Example:

```text
Prestige 5
Level 26
Draft Mode

Talk to Dungeon Master
        ↓
Choose Scale to Party
        ↓
Scarlet Monastery-style procedural run
        ↓
Enemies scale to level 26
        ↓
Draft build gets tested
        ↓
XP
Dream Path progression
Gear attunement
```

This gives Prestige characters a second leveling path besides questing.

---

# 19. Dungeon Master Leveling Policy

Allow:

```text
Normal Prestige
Draft Prestige
Non-Prestige characters
```

to enter appropriately scaled Dungeon Master content.

Reward XP normally unless configuration says otherwise.

Prevent:

```text
infinite trivial Dungeon Master spam
→ instant level 80
```

Audit:

```text
Rewards.XPMultiplier
cooldown
difficulty
party scaling
run duration
```

Tune XP to remain useful without completely replacing the rest of Azeroth.

---

# 20. Dungeon Master Roguelike Power

Dungeon Master currently grants stacking run-specific stats during Roguelike runs.

These buffs must remain:

```text
SESSION ONLY
```

They must disappear when:

* run ends
* group wipes
* session aborts
* player leaves session
* player logs out if session cannot resume
* worldserver restarts

Never convert Dungeon Master temporary buffs into permanent Echoes progression.

---

# 21. Dungeon Master → Dream Path

Add seasonal objectives including:

```text
Complete a Dungeon Master run
Complete 3 Dungeon Master runs
Complete Grandmaster difficulty
Defeat a themed Dungeon Master boss
Complete an Undead themed run
Complete a Demon themed run
Complete a Random Chaos run
Reach Roguelike floor 3
Reach Roguelike floor 5
Reach Roguelike floor 10
Clear 25 total Roguelike floors
Complete a Dungeon Master run during Draft Mode
```

This provides excellent seasonal variety.

Dream Path can deliberately rotate themes.

Example:

```text
Weekly Goal:
The Dead Will Rise

Complete:
3 Undead Rising Dungeon Master runs

Reward:
Dream Chest
+ Season Points
```

---

# 22. Dungeon Master → Echoes

Dungeon Master enemies and bosses may contribute toward normal Echoes systems.

Allow:

* normal equipment attunement
* moderate Essence generation
* eligible item drops
* permanent progression through legitimate gameplay

However, procedurally generated high-density enemy packs must be audited for Essence farming exploits.

Introduce reward normalization if required.

For example:

```text
Echoes.DungeonMaster.TrashEssenceMultiplier = 0.5
Echoes.DungeonMaster.BossEssenceMultiplier = 1.0
```

Only implement multipliers if actual testing demonstrates they are necessary.

---

# 23. Dungeon Master Reward Exploit Protection

Explicitly test:

```text
high-density trash farming
repeated boss respawn
session reset abuse
intentional wipe farming
disconnect/rejoin
teleport escape
group disband
leader change
instance reset
```

Dungeon Master must not become an infinite source of:

* Dream Chests
* Essence
* rare gear
* permanent stats
* Prestige credit

---

# 24. Dungeon Master Affixes

Dungeon Master's Roguelike Mode includes its own affix system.

Those affixes belong exclusively to the active Dungeon Master session.

Examples include:

```text
Fortified
Tyrannical
Raging
Bolstering
Savage
```

They should not leak into ordinary instances.

---

# 25. Mythic+ Affixes vs Dungeon Master Affixes

Do not attempt to make both systems share a single implementation immediately.

Maintain:

```text
Mythic+ affix engine
        =
Mythic+ sessions

Dungeon Master affix engine
        =
Dungeon Master Roguelike sessions
```

Later, a shared affix abstraction may be considered if worthwhile.

Do not rewrite both projects solely for architectural purity.

---

# 26. Affix Conflict Prevention

Add a normalized instance-mode concept:

```cpp
enum class ProgressionInstanceMode
{
    NORMAL,
    MYTHIC_PLUS,
    DUNGEON_MASTER,
    DUNGEON_MASTER_ROGUELIKE
};
```

Equivalent implementation is acceptable.

At runtime, determine the active mode.

Do not permit an instance to simultaneously be:

```text
MYTHIC_PLUS
+
DUNGEON_MASTER_ROGUELIKE
```

These modes are mutually exclusive.

---

# 27. Existing Challenge Modes

The server already contains another Challenge Modes system.

Audit it before enabling Mythic+ and Dungeon Master globally.

The intended policy should be:

```text
Normal dungeon:
Challenge Modes may operate if configured.

Mythic+ dungeon:
Mythic+ owns challenge scaling.

Dungeon Master:
Dungeon Master owns scaling.

Dungeon Master Roguelike:
Dungeon Master owns scaling.
```

Disable conflicting Challenge Mode scaling inside M+ and Dungeon Master sessions unless explicit compatibility has been verified.

---

# 28. AutoBalance

AutoBalance must be tested carefully.

Do not blindly stack:

```text
AutoBalance scaling
×
Mythic+ scaling
×
Dungeon Master scaling
```

Add integration rules.

Recommended default:

```text
Normal dungeon
→ AutoBalance allowed

Mythic+
→ Mythic+ primary scaling
→ AutoBalance disabled or compatibility profile

Dungeon Master
→ Dungeon Master primary scaling
→ AutoBalance disabled or compatibility profile

Dungeon Master Roguelike
→ Dungeon Master owns scaling
```

If AutoBalance can safely provide only party-size corrections without fighting module scaling, document and configure that explicitly.

---

# 29. World Threat

Echoes World Threat is an additional risk/reward layer.

Avoid uncontrolled multiplicative scaling.

Recommended policy:

```text
Open world:
World Threat = full behavior

Normal dungeon:
World Threat = configurable

Mythic+:
World Threat rewards allowed
World Threat enemy-stat scaling disabled/reduced

Dungeon Master:
World Threat rewards allowed
World Threat enemy-stat scaling disabled/reduced

Dungeon Master Roguelike:
World Threat scaling disabled
```

Dungeon Master Roguelike already escalates indefinitely.

It does not need another exponential scaling system sitting on top of it.

---

# 30. Shared Dungeon Events

Extend the progression integration layer.

Add normalized events:

```text
DUNGEON_RUN_BEGIN
DUNGEON_RUN_COMPLETE
DUNGEON_RUN_FAIL

MYTHIC_PLUS_BEGIN
MYTHIC_PLUS_BOSS_KILL
MYTHIC_PLUS_COMPLETE
MYTHIC_PLUS_TIMER_BEAT
MYTHIC_PLUS_FAIL

DUNGEON_MASTER_BEGIN
DUNGEON_MASTER_COMPLETE
DUNGEON_MASTER_FAIL

ROGUELIKE_BEGIN
ROGUELIKE_FLOOR_COMPLETE
ROGUELIKE_RUN_END
```

Include context:

```text
player
group
map
difficulty
mode
level
tier
floor
elapsed time
timer result
theme
boss
```

Do not directly couple Dream Path to private C++ internals when a bridge event can be used.

---

# 31. Integration Architecture

Use:

```text
ProgressionIntegration/
├── progression_core.lua
├── progression_events.lua
├── prestige_bridge.lua
├── dream_path_bridge.lua
├── worldsoul_bridge.lua
├── mythic_plus_bridge.cpp/.h
├── dungeon_master_bridge.cpp/.h
├── spell_ownership.lua
├── dungeon_mode.cpp/.h
└── progression_config.lua
```

Exact layout may vary.

Keep integration patches isolated.

---

# 32. Dream Path Becomes the Cross-System Quest Layer

Dream Path should understand all major server activities.

Seasonal objective categories should include:

```text
LEVELING
PRESTIGE
DRAFT
QUESTING
DUNGEONS
RAIDS
MYTHIC_PLUS
DUNGEON_MASTER
ROGUELIKE
WORLDSOUL
ATTUNEMENT
WORLD_THREAT
EXPLORATION
CRAFTING
COLLECTIONS
```

This makes Dream Path the connective tissue of the server.

---

# 33. Example Seasonal Week

Example:

```text
WEEK: Into the Depths
```

Objectives:

```text
Complete 5 normal dungeons
Complete 2 Dungeon Master runs
Reach Roguelike Floor 5
Complete Mythic+ 3
Beat a Mythic+ timer
Attune 3 dungeon items
Kill 20 dungeon bosses
```

Optional challenge:

```text
Complete a Dungeon Master run
while Draft Mode is active.
```

Rewards:

```text
Season Points
Dream Chests
cosmetics
seasonal currency
```

Not large permanent stats.

---

# 34. Prestige + Dungeon Master + Dream Path Example

```text
Level 33
Prestige 4
Draft Active
       ↓
Dungeon Master
       ↓
Random Demon-themed Razorfen run
       ↓
Scaled enemies
       ↓
Draft spells used
       ↓
Boss defeated
       ↓
XP
       ↓
Dream Path objective progress
       ↓
Item attunement progress
       ↓
Possible gear rewards
```

One activity contributes to several systems without duplicating ownership.

---

# 35. Level 80 Gameplay Example

```text
Level 80
Prestige 7
       ↓
Choose activity
```

### Path A

```text
Mythic+ 8
→ beat timer
→ leaderboard
→ Dream Path credit
→ attunement
→ Essence
```

### Path B

```text
Dungeon Master Roguelike
→ floor 1
→ floor 2
→ floor 3
→ ...
→ wipe
→ leaderboard
→ Dream Path credit
→ attunement
```

### Path C

```text
Raid
→ Echoes progression
→ Dream Path progression
```

### Path D

```text
Prestige again
→ Level 1
→ new Draft build
```

---

# 36. PlayerBots

Test PlayerBots with both dungeon modules.

Required tests:

```text
Human + 1 bot
Human + 4 bots
2 humans + bots
full human group
solo
```

For Mythic+:

* leader activation must work
* bots must enter correctly
* bosses must count correctly
* timer must not break
* bots must not independently receive account progression
* human credit must not duplicate

For Dungeon Master:

* bots must teleport with the session
* bots must recognize custom enemies
* bots must survive floor transitions
* bots must not cause false abandon detection
* bots must not count as independent seasonal accounts

A human using bots should still receive legitimate completion credit.

---

# 37. Mythic+ Keystone Handling

Audit the Keystone system.

Test:

* solo player
* grouped player
* group leader
* non-leader
* full inventory
* duplicate Keystone acquisition
* logout
* disconnect
* dungeon reset
* wipe
* timer expiration
* abandoned run
* server restart

Prevent Keystone duplication.

---

# 38. Mythic+ Completion Tracking

Verify:

```text
boss kills
combat time
completion time
timer result
group composition
map
M+ level
```

Persist correctly.

Dream Path integration must consume completion events, not independently infer them from boss kills.

---

# 39. Dungeon Master Persistent Statistics

Preserve separate statistics for:

```text
Normal Dungeon Master
Roguelike Dungeon Master
```

Do not merge them with Mythic+ leaderboards.

Recommended player-facing categories:

```text
MYTHIC+

Highest Level
Fastest Clears
Timed Clears
Bosses Defeated
```

and:

```text
DUNGEON MASTER

Runs Completed
Fastest Run
Highest Roguelike Tier
Most Floors
Total Floors
```

---

# 40. Unified Progression Summary

Extend the player progression display.

Example:

```text
PROGRESSION

Character
Level: 46
Prestige: 6
Mode: Draft

Dream Path
Season: 2
Tier: 72
Renown: 3

Worldsoul
Mastery: 14
Essence: 5,921
Threat: Daring

Mythic+
Highest Completed: +8
Highest Timed: +6

Dungeon Master
Runs: 27
Highest Difficulty: Grandmaster
Roguelike Best: Floor 9
```

---

# 41. Spell Ownership

Maintain explicit spell-source tracking.

Sources:

```text
NORMAL_CLASS
DRAFT
DREAM_RUNE
ITEM
QUEST
GM
OTHER
```

Do not remove a spell while another active source still owns it.

Example:

```text
Blink

DRAFT
+
DREAM_RUNE
```

Removing the rune must leave Blink because Draft still grants it.

---

# 42. mod-learn-spells Compatibility

Use per-player behavior.

```text
DraftActive = false
→ normal spell learning

DraftActive = true
→ suppress conflicting automatic class spell learning
```

Do not globally disable automatic spell learning.

---

# 43. Prestige + Echoes Persistence

Prestige must never erase Worldsoul progress.

Before Prestige:

1. save Echoes account state
2. save attunement state
3. save item state
4. validate save
5. perform Prestige

After:

1. reload account progression
2. validate item ownership
3. validate attunement
4. validate Essence/Mastery/Crucible

If permanent progression cannot be safely saved:

```text
ABORT PRESTIGE
```

---

# 44. Item Handling

Test all item sources:

```text
normal dungeon
raid
Mythic+
Dungeon Master
Dungeon Master Roguelike
Dream Chest
quest
crafted
```

against:

```text
Random Enchants
Item Upgrade
Echoes Attunement
Legacy Forge
```

Avoid permanent-stat exploits.

---

# 45. Mythic+ Reward Item Attunement

Items rewarded by Mythic+ should be normal valid items compatible with Echoes.

Test:

```text
M+ reward
→ equip
→ attune
→ upgrade
→ replace
→ Legacy Forge
```

---

# 46. Dungeon Master Reward Item Attunement

Test:

```text
Dungeon Master reward
→ equip
→ attune
→ Prestige
→ retrieve item
→ attunement preserved
```

Also test Roguelike rewards.

---

# 47. Difficulty Ownership

Use this final rule table.

| Content                | Primary Difficulty Owner      |
| ---------------------- | ----------------------------- |
| Open world             | World Threat / normal systems |
| Normal dungeon         | AutoBalance                   |
| Challenge Mode dungeon | Challenge Modes               |
| Mythic+                | mod-mythic-plus               |
| Dungeon Master         | mod-dungeon-master            |
| DM Roguelike           | mod-dungeon-master            |
| Raids                  | existing raid systems         |

Only one system should own primary HP/damage scaling per activity.

---

# 48. Reward Ownership

| Reward Type             | Primary Owner    |
| ----------------------- | ---------------- |
| Dungeon gear            | Dungeon system   |
| Temporary run buff      | Dungeon Master   |
| Keystone                | Mythic+          |
| Seasonal rewards        | Dream Path       |
| Permanent account power | Echoes           |
| Draft spells            | Prestige & Draft |
| Random gear affixes     | Random Enchants  |
| Item ranks              | Item Upgrade     |

---

# 49. Client Integration

Create a unified client package for systems requiring client modifications.

Do not overwrite DBCs sequentially.

Pipeline:

```text
Clean WotLK DBC
      ↓
Existing server modifications
      ↓
Prestige/Draft changes
      ↓
Echoes Item.dbc changes
      ↓
Other required client changes
      ↓
Validation
      ↓
Unified MPQ
```

Mythic+ and Dungeon Master should remain server-side unless actual upstream functionality requires additional client assets.

Do not invent unnecessary client dependencies.

---

# 50. Installation Order

## Phase 0: Audit

* [x] Backup databases. Completed outside the repository; dump paths and
  SHA-256 values are recorded in the Phase 0 audit record above.
* [x] Record AzerothCore revision: `custom-server` at
  `af4835044b9b0284c8ed47b575e3912bdae488a0`.
* [x] Record Eluna revision: standard Eluna at
  `58d7652138887783228b9727bd1fa4e08f00342b`.
* [x] Inventory modules: current baseline recorded; all five roadmap systems remain absent.
* [x] Inventory client patches: existing `Patch-A.MPQ` and `Patch-O.mpq` recorded;
  no `Patch-P.mpq` staged.
* [x] Inventory DBC edits: Fly Anywhere server `AreaTable.dbc` recorded; roadmap DBCs remain unstaged.
* [x] Document AutoBalance configuration: global and instance-family scaling enabled,
  no per-instance exclusions, minimum players `1`.
* [x] Document Challenge Modes configuration: `ChallengeModes.Enable = 1`.
* [x] Document PlayerBots configuration: enabled, random-bot autologin enabled,
  max random-bot level `80`, database updates enabled.

---

## Phase 1: Echoes

* [x] Install SQL.
* [x] Install Lua.
* [x] Install required C++ component.
* [x] Build.
* [ ] Install client assets.
* [x] Run load-time compatibility probe.
* [ ] Run upstream regression suite.
* [ ] Verify alts.
* [ ] Verify attunement.
* [ ] Verify player-login migration and stat reapplication.
* [ ] Verify live Echoes gameplay, including sinks, rack, forge, visage, and
  Worldsoul rewards.

The completed installation evidence is recorded above; the unchecked items
are live client, regression, player-login, and gameplay gates.

Do not proceed until stable.

---

## Phase 2: Prestige & Draft

* [x] Install SQL.
* [x] Install Lua.
* [x] Install DBC modifications.
* [x] Install addon.
* [ ] Verify Standard Prestige.
* [ ] Verify Draft Prestige.
* [ ] Verify leaving Draft.
* [ ] Verify gear mail.
* [ ] Verify spell learning.

---

## Phase 3: Prestige + Echoes

The Phase 3 bridge is staged in the canonical Echoes and Prestige scripts. It
flushes the current Echoes caches and player state before either Prestige path,
validates account/character rows and returned equipment ownership, and runs a
delayed post-login comparison. The static contracts and repository checks pass;
this is not live gameplay evidence.

* [x] Implement persistence bridge.
* [ ] Test Prestige with attuned equipment.
* [ ] Test Essence persistence.
* [ ] Test Mastery persistence.
* [ ] Test Crucible persistence.
* [ ] Test account progression.

## Phase 3 Persistence Bridge Staging Record (2026-08-27)

* [x] Gate Standard/Draft Prestige before draft-state, item, level, or
  starting-gear changes.
* [x] Guard the Echoes Rack mutation hook during starter-gear restoration.
* [x] Add the Phase 3 static contract and re-run the Phase 1/Phase 2 focused
  contracts.
* [x] Run `git diff --check` and `docker compose config --quiet`.
* [ ] Run live attuned-equipment, Essence, Mastery, Crucible, alternate-
  character, mail, Prestige, and relogin scenarios.

Known boundary: the pending post-Prestige checkpoint is held in worldserver
Lua memory, so a server/script restart between preflight and login skips that
comparison. Durable restart recovery requires a schema change and is outside
the existing Phase 1 schema constraint. Prestige's current Eluna mail helper
also recreates returned items from their entry; physical item-instance fidelity
and attunement behavior remain live validation gates.

---

## Phase 4: Dream Path

* [x] Install C++ module.
* [x] Install SQL.
* [x] Install addon.
* [ ] Verify season path.
* [ ] Verify runes.
* [ ] Verify objectives.
* [ ] Verify Dream Chests.
* [x] Disable internal Prestige.
* [x] Disable internal Paragon.
* [x] Disable Prestige mob scaling.
* [x] Implement Dream Renown.

Source/config/client staging is complete while compilation, SQL application,
server load, and client gameplay remain open.

---

## Phase 5: Mythic+

* [ ] Clone module.
* [ ] Rerun CMake.
* [ ] Rebuild.
* [ ] Deploy config.
* [ ] Verify SQL.
* [ ] Spawn NPC 200005.
* [ ] Verify Keystone acquisition.
* [ ] Verify M+ activation.
* [ ] Verify timer.
* [ ] Verify affixes.
* [ ] Verify rewards.
* [ ] Verify tracking.
* [ ] Verify leaderboard.

Do not integrate Dream Path yet.

First prove stock Mythic+ functionality.

---

## Phase 6: Dungeon Master

* [ ] Clone module.
* [ ] Rerun CMake.
* [ ] Rebuild.
* [ ] Apply world SQL.
* [ ] Apply character SQL.
* [ ] Deploy config.
* [ ] Verify NPC 500000.
* [ ] Verify themed runs.
* [ ] Verify six difficulty tiers.
* [ ] Verify level scaling.
* [ ] Verify party scaling.
* [ ] Verify Roguelike Mode.
* [ ] Verify floor transition.
* [ ] Verify affixes.
* [ ] Verify leaderboards.

Remember that the project is early-development software.

Treat crashes, incomplete cleanup, scaling errors, and edge cases as expected test targets rather than assuming production readiness.

---

## Phase 7: Dungeon Scaling Integration

* [x] Detect active instance mode.
* [x] Prevent M+ + Dungeon Master overlap.
* [x] Prevent AutoBalance conflicts.
* [x] Prevent Challenge Modes conflicts.
* [x] Prevent World Threat scaling conflicts.
* [ ] Test normal dungeons afterward.

## Phase 7 Staging Record (2026-08-28)

* [x] Added a per-instance `Map::CustomData` mode marker for Normal,
  Mythic+, Dungeon Master, and Roguelike ownership.
* [x] Mythic+ claims before Keystone consumption and when restoring an active
  saved run; conflicting Dungeon Master/Roguelike ownership is rejected.
* [x] Dungeon Master and Roguelike claim before population; conflicting
  ownership fails through existing session cleanup.
* [x] AutoBalance now skips special-mode map refreshes, creature lifecycle
  scaling, and encounter rewards while normal dungeons retain the existing
  path.
* [x] Audited Challenge Modes as player restriction/XP behavior without an
  enemy-stat scaler; no Challenge Modes implementation change was needed.
* [x] Audited Echoes World Threat as reward/momentum/attunement behavior with
  no enemy-stat scaler; no World Threat implementation change was needed.
* [x] Phase 7 static contract and `git diff --check` pass.

No SQL, client assets, server configuration, or scaling formulas changed.
The normal-dungeon-after-special-mode check and all Mythic+, Dungeon Master,
Roguelike, Challenge Modes, and World Threat client gameplay checks remain
open because no live gameplay run was performed in this phase.

---

## Phase 8: Dream Path + Dungeon Systems

* [x] Add M+ objective events.
* [x] Add DM objective events.
* [x] Add Roguelike objectives.
* [x] Add weekly rotations.
* [x] Prevent duplicate credit.
* [x] Add Season Point rewards.
* [x] Add Dream Chest rewards.

## Phase 8 Static Staging Record (2026-08-28)

* [x] Added the no-op-safe progression event bridge and registered the Dream Path consumer.
* [x] Added database-defined weekly filters/rotations and persistent per-character event claims.
* [x] Added guarded M+, Dungeon Master, and Roguelike lifecycle producers.
* [x] Phase 8 static contract and `git diff --check` pass.
* [ ] Full C++/SQL codestyle remains blocked by pre-existing repository violations; SQL lint also requires the missing `origin/master` ref and flags the required portable `information_schema` guards.
* [ ] Run live M+ begin/boss/completion/timer/depleted-run checks.
* [ ] Run live Dungeon Master success/failure and Roguelike floor/wipe checks.
* [ ] Validate DB rotation edits, duplicate callbacks, restart deduplication, bots, and multiplayer behavior.

---

## Phase 9: Prestige + Dungeon Master

* [ ] Test level 10.
* [ ] Test level 20.
* [ ] Test level 40.
* [ ] Test level 60.
* [ ] Test level 70.
* [ ] Test level 80.
* [ ] Test Standard Prestige.
* [ ] Test Draft Prestige.
* [ ] Test bots.
* [ ] Balance XP.

---

## Phase 10: Echoes + Dungeon Systems

* [ ] Test attunement inside M+.
* [ ] Test attunement inside DM.
* [ ] Test attunement inside Roguelike.
* [ ] Audit Essence rates.
* [ ] Audit high-density farm exploits.
* [ ] Audit boss credit.
* [ ] Audit duplicate rewards.

---

## Phase 11: PlayerBots

* [ ] M+ solo + bots.
* [ ] M+ group + bots.
* [ ] DM solo + bots.
* [ ] DM Roguelike + bots.
* [ ] Transition between DM floors.
* [ ] Boss credit.
* [ ] Loot.
* [ ] Dream Path credit.
* [ ] Echoes credit.
* [ ] Disconnect/reconnect.

---

## Phase 12: Unified Client Pack

* [ ] Merge DBCs.
* [ ] Build unified MPQ.
* [ ] Stage addons.
* [ ] Validate clean client.
* [ ] Document installation.

---

# 51. Full Regression Matrix

Test combinations including:

```text
Normal character
Standard Prestige
Draft Prestige
Level 80
Solo
Human group
PlayerBots group
World Threat enabled
World Threat disabled
```

Against:

```text
Normal dungeon
Challenge Mode
Mythic+
Dungeon Master
Dungeon Master Roguelike
Raid
Open world
```

Do not assume success in one combination proves another.

---

# 52. Critical M+ Exploit Tests

* [ ] Duplicate Keystone.
* [ ] Keystone activation outside eligible instance.
* [ ] Non-leader activation.
* [ ] Group manipulation after activation.
* [ ] Logout during timer.
* [ ] Disconnect during timer.
* [ ] Reset instance.
* [ ] Change difficulty.
* [ ] Kill final boss before expected bosses.
* [ ] Timer reward duplication.
* [ ] Multiple completion callbacks.
* [ ] PlayerBot reward duplication.
* [ ] Dream Path completion duplication.
* [ ] Echoes boss reward duplication.

---

# 53. Critical Dungeon Master Exploit Tests

* [ ] Session reset farming.
* [ ] Trash respawn farming.
* [ ] Boss respawn farming.
* [ ] Roguelike floor rollback.
* [ ] Roguelike buff persistence after exit.
* [ ] Logout with run buffs.
* [ ] Death during floor transition.
* [ ] Group leader disconnect.
* [ ] Group disband.
* [ ] Party member enters late.
* [ ] Player leaves instance.
* [ ] Server restart.
* [ ] Duplicate reward callback.
* [ ] XP farming at low difficulty.
* [ ] Essence farming from dense packs.

---

# 54. Performance

Profile:

```text
creature spawn
creature scaling
kill hooks
boss hooks
attunement updates
Dream Path events
M+ timer
DM session manager
DM floor transitions
PlayerBot AI
database writes
```

Avoid synchronous SQL per creature kill wherever practical.

Cache progression state appropriately.

---

# 55. Failure Safety

If Dream Path fails:

```text
M+
Dungeon Master
Prestige
Echoes
```

should continue whenever possible.

If the integration bridge fails:

```text
base dungeon modules
```

should still function independently.

If permanent Echoes state cannot save during a destructive Prestige operation:

```text
abort Prestige
```

If a Dungeon Master session fails:

```text
safely terminate session
remove temporary buffs
return players
preserve permanent progression
```

If Mythic+ state becomes invalid:

```text
cancel run cleanly
do not award completion
do not consume/create duplicate rewards
```

---

# 56. Configuration

Provide integration configuration similar to:

```lua
ProgressionConfig = {
    Prestige = {
        Enable = true,
        Draft = true,
    },

    DreamPath = {
        Enable = true,
        DisableInternalPrestige = true,
        DisableInternalParagon = true,
        DreamRenown = true,
    },

    Echoes = {
        Enable = true,
        PersistAcrossPrestige = true,
    },

    MythicPlus = {
        Enable = true,
        DreamPathObjectives = true,
        EchoesRewards = true,
    },

    DungeonMaster = {
        Enable = true,
        Roguelike = true,
        PrestigeLeveling = true,
        DreamPathObjectives = true,
        EchoesProgression = true,
    },

    Difficulty = {
        PreventScalingStack = true,
    },

    PlayerBots = {
        FilterBotProgression = true,
    }
}
```

Use native module configuration where possible.

The integration config should control bridges, not unnecessarily duplicate every upstream configuration value.

---

# 57. Documentation

Create:

```text
docs/progression/
├── ARCHITECTURE.md
├── INSTALL.md
├── CONFIGURATION.md
├── PRESTIGE.md
├── DREAM_PATH.md
├── WORLDSOUL.md
├── MYTHIC_PLUS.md
├── DUNGEON_MASTER.md
├── DIFFICULTY_OWNERSHIP.md
├── REWARDS.md
├── PLAYERBOTS.md
├── CLIENT_PACK.md
├── SPELL_OWNERSHIP.md
├── TESTING.md
├── BALANCE.md
└── UPSTREAM_TRACKING.md
```

---

# 58. Upstream Maintainability

Do not unnecessarily fork/rewrite upstream modules.

Priority:

```text
configuration
     ↓
public hooks/APIs
     ↓
integration adapters
     ↓
small patches
     ↓
direct rewrites only if unavoidable
```

Record every upstream modification.

Include:

```text
repository
upstream commit
file
original behavior
modified behavior
reason
integration dependency
rebase instructions
```

---

# 59. Final Acceptance Test

The following must work:

```text
Create character
       ↓
Level normally
       ↓
Dream Path progresses
       ↓
Echoes attunes gear
       ↓
Run Dungeon Master content
       ↓
Level through procedural dungeons
       ↓
Reach 80
       ↓
Run Mythic+
       ↓
Beat timed dungeons
       ↓
Advance Dream Path
       ↓
Advance Worldsoul
       ↓
Choose Prestige
       ↓
Standard OR Draft
       ↓
Return to level 1
       ↓
Prestige count remains
       ↓
Worldsoul remains
       ↓
Dream Path remains
       ↓
Run level-scaled Dungeon Master content
       ↓
Reach 80 again
       ↓
Return to Mythic+
       ↓
Repeat
```

---

# 60. Season Reset Acceptance Test

When a new Dream Path season begins:

```text
Prestige
KEEP

Draft history
KEEP

Worldsoul
KEEP

Mythic+ personal records
KEEP

Dungeon Master lifetime records
KEEP

Dream Path Tier
RESET

Dream Renown
RESET

Season objectives
RESET

Season rewards
RESET
```

Historical seasonal statistics may be archived.

---

# 61. The Desired Endgame

The final server should offer several distinct answers to:

> "What should I do tonight?"

### Replay Azeroth

```text
Prestige + Draft
```

### Run unpredictable dungeons

```text
Dungeon Master
```

### Push difficult timed content

```text
Mythic+
```

### Work toward current seasonal goals

```text
Dream Path
```

### Improve the account permanently

```text
Echoes of the Worldsoul
```

These should reinforce each other without becoming duplicates.

The intended gameplay loop is:

```text
                  ┌───────────────┐
                  │ DREAM PATH    │
                  │ Seasonal Goals│
                  └───────┬───────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
  PRESTIGE/DRAFT    DUNGEON MASTER      MYTHIC+
   Replay 1–80       Roguelike Runs    Endgame Push
         │                │                │
         └────────────────┼────────────────┘
                          ▼
                  ECHOES/WORLDSOUL
                 Permanent Progress
                          │
                          ▼
                       REPEAT
```

The server should ultimately feel less like:

```text
WotLK + a bunch of modules
```

and more like:

```text
a persistent WotLK Classic+ RPG
with seasons,
roguelike dungeon runs,
Mythic+,
Prestige,
randomized builds,
gear attunement,
and account-wide progression.
```

---

# 62. Do Not Do

* [ ] Do not maintain multiple Prestige systems.
* [ ] Do not maintain multiple permanent Paragon systems.
* [ ] Do not make Draft mandatory.
* [ ] Do not make Dungeon Master tiers equal Mythic+ levels.
* [ ] Do not activate Mythic+ inside Dungeon Master sessions.
* [ ] Do not activate Dungeon Master inside Mythic+ sessions.
* [ ] Do not blindly stack AutoBalance with M+ scaling.
* [ ] Do not blindly stack AutoBalance with DM scaling.
* [ ] Do not stack Challenge Modes over Mythic+.
* [ ] Do not stack Challenge Modes over Dungeon Master.
* [ ] Do not stack full World Threat scaling over DM Roguelike.
* [ ] Do not allow Dungeon Master temporary buffs to persist outside runs.
* [ ] Do not let PlayerBots receive independent account progression.
* [ ] Do not award Dream Path completion twice.
* [ ] Do not allow dynamic item bonuses to create permanent Echoes exploits.
* [ ] Do not overwrite DBC modifications from another system.
* [ ] Do not proceed with Prestige if permanent state cannot be persisted.
* [ ] Do not rewrite upstream modules unless integration truly requires it.
* [ ] Do not assume early-development Dungeon Master functionality is production-safe without testing.

# End Goal

Build a progression ecosystem where every major part of Azeroth remains useful:

**Prestige & Draft** makes leveling replayable.

**Dungeon Master** makes the dungeon library replayable and unpredictable at almost any level.

**Mythic+** gives level-80 players a structured escalating dungeon challenge with timers, affixes and rankings.

**Dream Path** gives every activity seasonal purpose.

**Echoes of the Worldsoul** ensures that all of that play contributes toward permanent account progression.

A player should be able to spend one night leveling a bizarre Draft character through randomized dungeons, another night pushing Mythic+ timers, and another farming attuned equipment, while all three nights still advance the same broader seasonal and permanent progression ecosystem.
