# Freeborn Third TeamId Implementation Specification

**Project:** AzerothCore 3.3.5a, heavily customized fork

**Feature:** True third persistent player `TeamId`, **Freeborn**

**Revised:** September 23, 2026

**Architecture revision:** This version replaces the earlier alignment-layer design. `TEAM_FREEBORN` is now a required, first-class persistent player `TeamId`.

---


## 1. Objective

Implement **Freeborn** as a true third persistent player `TeamId` alongside Alliance and Horde.

A Freeborn character must return `TEAM_FREEBORN` from the server API that represents the character's persistent player team.

Example:

```text
Human Native:
    Race: Human
    Player TeamId: TEAM_ALLIANCE
    Origin TeamId: TEAM_ALLIANCE

Human Freeborn:
    Race: Human
    Player TeamId: TEAM_FREEBORN
    Origin TeamId: TEAM_ALLIANCE

Orc Native:
    Race: Orc
    Player TeamId: TEAM_HORDE
    Origin TeamId: TEAM_HORDE

Orc Freeborn:
    Race: Orc
    Player TeamId: TEAM_FREEBORN
    Origin TeamId: TEAM_HORDE
```

Freeborn therefore becomes a first-class server-side player team, not an `isFreeborn` flag and not a separate `PlayerAlignment` layered above Alliance/Horde.

However, the character's race still has an **origin team** derived from race. The origin team remains Alliance or Horde and is used only where the game genuinely needs race-derived legacy data such as starting zones, cinematics, racial languages, starting reputations, initial taxi data, paired faction quest preference, and other race-origin behavior.

The implementation must explicitly separate:

```text
Persistent Player TeamId
    TEAM_ALLIANCE / TEAM_HORDE / TEAM_FREEBORN

Origin TeamId
    TEAM_ALLIANCE / TEAM_HORDE, derived from race

Match TeamId
    TEAM_ALLIANCE / TEAM_HORDE during battlegrounds and arenas
```

Freeborn must be treated as a real third player team without turning every two-sided subsystem in WoW into a three-sided subsystem.

## 2. Critical architectural rule

Add a real, unique `TEAM_FREEBORN` value to AzerothCore's player `TeamId` model.

Do **not** reuse:

```text
TEAM_NEUTRAL
TEAM_OTHER
an unused faction-template ID
a race ID
an alignment flag
a PvP flag
```

as a substitute for `TEAM_FREEBORN`.

The exact numeric value for `TEAM_FREEBORN` must be selected only after auditing the customized fork's current `TeamId` enum and all sentinel values. Do not assume a stock numeric value and do not collide with `TEAM_NEUTRAL` or any custom team values already present.

Conceptually:

```cpp
enum TeamId : uint8
{
    TEAM_ALLIANCE = /* existing value */,
    TEAM_HORDE    = /* existing value */,
    // preserve existing neutral/sentinel values exactly as required
    TEAM_FREEBORN = /* new unique non-colliding value */
};
```

For a Freeborn player:

```cpp
player->GetTeamId() == TEAM_FREEBORN
```

must be true.

Provide an explicit race-origin helper:

```cpp
TeamId Player::GetOriginTeamId() const;
```

with behavior equivalent to:

```cpp
TeamId Player::GetOriginTeamId() const
{
    return TeamIdForRace(getRace());
}
```

`GetOriginTeamId()` must always return the Alliance/Horde team naturally associated with the player's race.

`TeamIdForRace()` itself should remain race-derived. Selecting Freeborn must not change the race-to-origin-team mapping.

At minimum provide or preserve APIs equivalent to:

```cpp
TeamId GetTeamId() const;        // persistent player team: A/H/Freeborn
TeamId GetOriginTeamId() const;  // race-derived A/H origin
TeamId GetBgTeamId() const;      // temporary match side when applicable
bool IsFreeborn() const;         // GetTeamId() == TEAM_FREEBORN
```

### Team-count and array safety

Adding a third `TeamId` does **not** mean every existing two-element team array should become three elements.

Audit every use of:

```text
MAX_TEAMS
TEAM_COUNT
TeamId as an array index
TEAM_ALLIANCE / TEAM_HORDE loops
GetTeamId() as an array index
```

Classify the subsystem before changing it.

If an array represents **persistent player teams**, extend or redesign it to safely support Freeborn.

If an array represents **battleground/arena sides**, it remains exactly two-sided and must be indexed by the match team, not the persistent player team.

If an array represents **race-origin Alliance/Horde data**, it remains two-sided and must use `GetOriginTeamId()` or another explicit origin-team helper.

Do not simply increase a global `MAX_TEAMS` constant and assume every caller becomes correct.

### `GetTeam()` versus `GetTeamId()`

Audit the fork's `GetTeam()` separately.

If `GetTeam()` represents a legacy faction-group/DBC value rather than the player `TeamId`, do not invent a fake DBC faction value just to mirror `TEAM_FREEBORN`. Add or use explicit helpers instead.

The required invariant is:

```text
Player::GetTeamId()      = persistent team identity
Player::GetOriginTeamId() = race-origin Alliance/Horde identity
Player::GetBgTeamId()     = temporary BG/Arena side
```

Those concepts must not be collapsed into one variable.

## 3. Existing server behavior must be preserved

This server already has extensive faction-free functionality.

Before making changes, audit the current source tree and identify every existing modification/module affecting:

```text

cross-faction NPC interaction

cross-faction chat

cross-faction mail

cross-faction auction houses

cross-faction vendors/trainers

cross-faction grouping

cross-faction guilds

cross-faction trade

faction reputation

quest restrictions

taxi access

battlegrounds

arenas

LFG

playerbots

custom races

character creation

client runtime patches

Eluna

```

Do not replace working faction-free functionality with stock AzerothCore behavior.

Freeborn rules should be layered over the current server behavior.

For non-Freeborn characters, behavior should remain unchanged unless a change is explicitly required by this specification.

---

## 4. Database model

Persist the player's actual team identity in the character database.

Preferred conceptual form:

```sql
ALTER TABLE characters
ADD COLUMN teamId TINYINT UNSIGNED NOT NULL;
```

The persisted value represents:

```text
TEAM_ALLIANCE
TEAM_HORDE
TEAM_FREEBORN
```

Use the actual enum values defined by the customized core. Do not hardcode numeric values in the specification until the fork has been audited.

### Existing-character migration

Existing characters must migrate to the team naturally associated with their race:

```text
Human -> TEAM_ALLIANCE
Orc -> TEAM_HORDE
etc.
```

Because this server contains custom races, do not use a stock race list blindly.

The migration must account for every currently playable race in the customized fork.

A safe migration strategy is:

1. Add the new column in a temporary state that allows identifying uninitialized rows.
2. Backfill every existing character from the current race-to-team mapping.
3. Verify that no character remains unmapped.
4. Make the column non-null/authoritative.
5. Do not convert any existing character to `TEAM_FREEBORN` automatically.

If the repository's migration framework supports a server-side or generated migration that reuses the fork's custom race mapping, prefer that over duplicating an incomplete stock race table in SQL.

### Persistence paths

Update all relevant prepared statements and load/save paths, including the customized fork's equivalents of:

```text
CHAR_INS_CHARACTER
CHAR_UPD_CHARACTER
CHAR_SEL_CHARACTER
CHAR_SEL_ENUM
CHAR_SEL_ENUM_DECLINED_NAME
character cache queries
offline character lookup queries
race/faction-change services
```

The persistent `teamId` must survive:

```text
logout/login
server restart
character rename
character customization
race change
faction/race-change services
character cache reload
offline GM commands
```

Add `teamId` to `CharacterCacheEntry` or the fork's equivalent offline-character cache.

This is important because guild invitations, commands, mail/social operations, and other systems may make decisions about characters that are not currently online.

The database `teamId` is the authoritative persistent player-team source.

Race remains the authoritative source for `GetOriginTeamId()`.

Do not persist a second `originTeamId` unless the customized fork already has a concrete requirement for one.

## 5. Character creation

The customized character creation screen will contain a **Freeborn button between the gender buttons**.

All playable races can be created as Freeborn.

Selecting Freeborn must **not** change the race ID.

The client should maintain explicit team selection state equivalent to:

```cpp
TeamId selectedPlayerTeam;
```

For a normal race selection:

```text
selectedPlayerTeam = TeamIdForRace(selectedRace)
```

When the Freeborn option is selected:

```text
selectedPlayerTeam = TEAM_FREEBORN
```

Examples:

```text
Human + normal mode   -> TEAM_ALLIANCE
Human + Freeborn      -> TEAM_FREEBORN
Orc + normal mode     -> TEAM_HORDE
Orc + Freeborn        -> TEAM_FREEBORN
```

The same race model, customization options, gender/body settings, class availability, and appearance data should remain available unless another existing system says otherwise.

Changing races while Freeborn is selected should keep:

```text
selectedPlayerTeam = TEAM_FREEBORN
```

unless the customized UI explicitly switches the player back to normal faction mode.

If the player deselects Freeborn, restore the selected team from the newly selected race:

```cpp
selectedPlayerTeam = TeamIdForRace(selectedRace);
```

Do not infer Freeborn from race ID, model, appearance, faction pane, or starting location.

### Character creation packet

Keep the normal 3.3.5a wire protocol unchanged if reasonably possible.

The Freeborn team selection still has to reach the server.

First audit the customized client and server's `CMSG_CHAR_CREATE` serialization.

A likely compatible solution is to encode the Freeborn selection into an unused/reserved portion of an existing character-create field and strip it immediately server-side.

`OutfitId` is a candidate because the current AzerothCore character creation structure already carries it, but **do not blindly reserve a bit until the customized client is audited**.

For example, if testing proves a high bit is unused:

```cpp
constexpr uint8 FREEBORN_CREATE_FLAG = 0x80;

bool requestedFreeborn =
    (createInfo.OutfitId & FREEBORN_CREATE_FLAG) != 0;

createInfo.OutfitId &= ~FREEBORN_CREATE_FLAG;
```

Then, after the normal race/class creation template has been resolved:

```cpp
TeamId playerTeam = requestedFreeborn
    ? TEAM_FREEBORN
    : TeamIdForRace(createInfo.Race);

player->SetPlayerTeamId(playerTeam);
```

The exact setter name may differ.

This example describes the signaling technique, not a mandatory bit assignment.

Prove that the chosen field/bit is unused by this customized client before adopting it.

Do not increase packet length unless no safe compatible signaling method exists.

### Creation ordering

Normal race/class initialization must still use race-origin information where appropriate.

A Freeborn Human must receive Human creation data before/while its persistent team is set to `TEAM_FREEBORN`.

Do not let a generic `GetTeamId()` call during creation accidentally replace Human/Orc/etc. starting templates with nonexistent Freeborn starting templates.

Where creation logic needs the race's original faction, use:

```cpp
GetOriginTeamId()
```

or the equivalent race-derived helper.

## 6. Character-select display

Freeborn characters should be visibly distinguishable on character select.

A Freeborn character's stored player team is:

```text
TEAM_FREEBORN
```

However, for this phase keep the race's normal Alliance/Horde character-select background.

Examples:

```text
Human Freeborn -> Human/Alliance-style racial background
Orc Freeborn   -> Orc/Horde-style racial background
```

That background is a race-origin presentation choice, not the character's persistent TeamId.

Add a Freeborn badge/emblem/indicator elsewhere in the character-select UI.

Because stock `SMSG_CHAR_ENUM` does not have a third-team presentation field, extend the character enumeration database query to load `teamId`, then communicate Freeborn state to the customized client without changing packet size if possible.

Preferred technique:

Use a verified-unused client-visible flag bit in an existing enum field and teach the customized client to interpret that bit as:

```text
TEAM_FREEBORN
```

Do not use a bit without first auditing all existing custom flags.

The DB `teamId` remains authoritative. Any packet/UI bit is only a transport/display representation.

The client-side visual marker must not become a second independent source of truth.

## 7. Team policy layer

A true third `TeamId` does not eliminate the need for centralized relationship policy.

Freeborn has intentionally unusual rules:

```text
Freeborn and Freeborn share the same TeamId
but are normally hostile to one another outside cooperative contexts.

Freeborn can trade with Alliance/Horde
while remaining hostile to them for PvP purposes.

Freeborn can use both Alliance and Horde NPC services.
```

Therefore, do not assume:

```cpp
a->GetTeamId() == b->GetTeamId()
```

always means friendly, assistable, group-compatible, or non-hostile.

Do not scatter hundreds of isolated:

```cpp
if (player->GetTeamId() == TEAM_FREEBORN)
```

checks throughout the codebase.

Create a centralized player-team policy layer.

This can live on `Player`, a `PlayerTeamMgr`, a `TeamPolicy` helper, or another architecture consistent with the current fork.

At minimum centralize concepts equivalent to:

```cpp
TeamId GetPlayerTeamId(Player const* player);
TeamId GetOriginTeamId(Player const* player);

bool ArePlayersHostile(
    Player const* source,
    Player const* target);

bool CanAttackPlayer(
    Player const* attacker,
    Player const* target);

bool CanAssistPlayer(
    Player const* source,
    Player const* target);

bool CanManualGroup(
    Player const* inviter,
    Player const* target);

bool CanGuildTogether(
    Player const* source,
    Player const* target);

bool CanTradeWith(
    Player const* source,
    Player const* target);

bool CanCommunicateWith(
    Player const* source,
    Player const* target);

bool CanUseFactionNpc(
    Player const* player,
    Creature const* creature);
```

The exact API names can differ.

The important requirement is that systems query **team-aware policy** rather than independently inventing Freeborn behavior.

`TEAM_FREEBORN` is a first-class identity. It is **not** a guarantee of universal same-team friendliness.

## 8. Player versus NPC relationship

Freeborn NPC interaction and Freeborn player hostility are separate concepts.

A Freeborn character must be able to interact with NPCs belonging to both Alliance and Horde.

Expected:

```text

Freeborn -> Alliance NPC = usable

Freeborn -> Horde NPC    = usable

Freeborn -> Neutral NPC  = normal rules

```

This includes:

```text

questgivers

vendors

trainers

bankers

auctioneers

innkeepers

stable masters

flight masters

repair NPCs

spirit healers where applicable

barbers

faction transportation NPCs

reputation vendors

guards

```

Do not make hostile monsters friendly merely because they are NPCs.

The override concerns Alliance/Horde faction allegiance, not all creatures.

Reuse the server's existing faction-free NPC infrastructure wherever possible.

### Player-controlled units

A pet, guardian, summon, vehicle, charmed unit, etc. controlled by a player must follow the **player relationship rules**, not the friendly-NPC rules.

For relationship resolution, audit usage of helpers such as:

```cpp

GetAffectingPlayer()

GetCharmerOrOwnerPlayerOrPlayerItself()

```

A Horde player's pet is still part of that Horde player's PvP relationship.

A Freeborn player's pet inherits the Freeborn player's relationship.

---

## 9. Freeborn versus player hostility

Outside temporary cooperative contexts and no-PvP areas, `TEAM_FREEBORN` is hostile to every persistent player team.

Expected relationship:

```text
TEAM_FREEBORN -> TEAM_ALLIANCE = hostile
TEAM_FREEBORN -> TEAM_HORDE    = hostile
TEAM_FREEBORN -> TEAM_FREEBORN = hostile
```

This hostility is symmetric:

```text
TEAM_ALLIANCE -> TEAM_FREEBORN = hostile
TEAM_HORDE    -> TEAM_FREEBORN = hostile
TEAM_FREEBORN -> TEAM_FREEBORN = hostile
```

when normal PvP rules permit combat.

This is intentionally different from normal same-team behavior.

Two Freeborn players share:

```text
GetTeamId() == TEAM_FREEBORN
```

but are still normally hostile to one another unless a higher-priority cooperative context overrides that relationship.

Examples:

```text
Human Freeborn vs Human Alliance = hostile
Orc Freeborn vs Orc Horde = hostile
Human Freeborn vs Orc Freeborn = hostile
Human Freeborn vs Human Freeborn = hostile
```

The Human/Orc race origin must not affect these persistent team relationships.

Do not fall back to `GetOriginTeamId()` for ordinary player-versus-player team hostility.

That helper exists for race-origin systems, not for deciding the player's current faction identity.

## 10. Hostile does NOT mean attackable everywhere

This is critical.

Outside no-PvP areas and explicit cooperative or match contexts, Freeborn are hostile to players of every team. This applies symmetrically: Alliance and Horde players are also hostile to Freeborn under the same PvP conditions.

In areas where PvP is disabled, ordinary Freeborn-versus-player hostility is inactive; do not mark players hostile solely because one or both players use `TEAM_FREEBORN`.

In PvP-enabled areas, persistent player team determines the relationship, while ordinary PvP flags and other eligibility rules still determine whether combat can actually occur.

Do not implement permanent forced FFA PvP.

On a PvE-style ruleset, merely standing near another hostile player should not automatically make that player attackable.

Freeborn should participate in PvP using the server's normal concepts such as:

```text
PvP flags
contested zones
FFA PvP areas
battlegrounds
arenas
duels
other existing PvP rules
```

The core difference is that once PvP rules say two hostile players may fight, `TEAM_FREEBORN` hostility must work correctly, including Freeborn-versus-Freeborn.

Audit the central attack/reaction paths, especially the fork's equivalents of:

```cpp
GetReactionTo()
IsHostileTo()
IsFriendlyTo()
IsValidAttackTarget()
_IsValidAttackTarget()
IsValidAssistTarget()
```

Do not patch individual damaging spells one at a time.

Do not let stock code short-circuit Freeborn-versus-Freeborn as friendly merely because:

```cpp
source->GetTeamId() == target->GetTeamId()
```

is true.

## 11. Capital cities and sanctuaries

Ordinary Freeborn player hostility is inactive inside capital/main-city and sanctuary areas. Neither Freeborn nor Alliance/Horde players may initiate ordinary hostile player combat against one another there.

They must still remain selectable for:

```text

inspect

trade

whisper

social interaction

```

"Not targetable" in this requirement means **not a valid hostile attack target**, not invisible or impossible to select with the mouse.

Use area metadata rather than a hardcoded Stormwind/Orgrimmar list wherever possible.

At minimum recognize existing area flags equivalent to:

```text

AREA_FLAG_CAPITAL

AREA_FLAG_SLAVE_CAPITAL2

AREA_FLAG_SANCTUARY

```

If the customized server has custom cities that do not carry those flags, add a configurable DB-backed safe-area override rather than adding scattered hardcoded area IDs.

Suggested table:

```text

player_team_safe_area

    areaId

    flags/reason

```

The no-PvP area rule suppresses ordinary Freeborn hostility; this is not merely an attack-target filter.

A Freeborn player inside such an area cannot initiate or receive normal hostile player combat.

Do not break trade, inspect, mail, chat, NPC interaction, or other noncombat operations.

---

## 12. Interaction precedence

Relationship resolution should use a clear precedence.

Recommended conceptual ordering:

```text
1. Battleground/Arena temporary match team
2. Valid cooperative group context
3. Safe-area/no-PvP rules suppress ordinary Freeborn hostility
4. Persistent player-team relationship
5. Existing faction-free server logic where still applicable
```

More specifically:

### Battleground/Arena

Temporary match team is authoritative for combat inside the match.

A Freeborn player's persistent team remains `TEAM_FREEBORN`, but `GetBgTeamId()` or the equivalent match-side helper returns Alliance or Horde for that match.

### LFG or valid party

Members of the same active cooperative group are friendly/assistable even where their persistent team rules would otherwise make them hostile.

### Freeborn outside cooperative context

`TEAM_FREEBORN` is hostile to Alliance, Horde, and other Freeborn players where PvP is enabled.

### NPCs

Use NPC interaction policy, not the generic player-team hostility policy.

Do not let guild membership alone make two Freeborn players friendly.

## 13. Manual parties and raids

Freeborn may manually group only with other Freeborn characters.

Allowed:

```text

Freeborn + Freeborn

```

Disallowed:

```text

Freeborn + Alliance

Freeborn + Horde

```

This applies to normal manually created parties and raids.

Preserve whatever cross-faction grouping behavior already exists between ordinary Alliance and Horde characters.

Freeborn is the special restriction.

Once Freeborn players are members of the same valid party/raid, group membership must temporarily override their normal Freeborn-vs-Freeborn hostility so the group functions normally.

Party members must be:

```text

friendly

heal-able

buff-able

resurrect-able

nonattackable by one another

```

When they leave the group, ordinary Freeborn hostility returns immediately.

---

## 14. LFG

LFG is an explicit exception to the normal manual grouping rule.

Freeborn can be matched with:

```text
TEAM_ALLIANCE
TEAM_HORDE
TEAM_FREEBORN
```

An LFG-created group is a cooperative context.

All members of the same LFG group must be friendly/assistable for the lifetime of that group regardless of persistent player team.

Do not permanently change:

```text
GetTeamId()
the DB teamId
race
GetOriginTeamId()
```

to make LFG work.

When the LFG group ends or a player leaves it, recalculate normal team relationships immediately.

Audit:

```text
LFGMgr
group creation
LFG teleport
instance entry
group removal
kick/removal
disband
reconnect while in LFG
```

If existing LFG code assumes every player team is Alliance or Horde, adapt the matchmaking eligibility layer to accept `TEAM_FREEBORN` while keeping the cooperative group relationship independent of persistent team.

## 15. Guilds

Freeborn may only guild with other Freeborn characters.

Allowed:

```text
TEAM_FREEBORN guild -> TEAM_FREEBORN member
```

Disallowed:

```text
Freeborn guild -> TEAM_ALLIANCE member
Freeborn guild -> TEAM_HORDE member
Alliance/Horde native guild -> TEAM_FREEBORN member
```

A Freeborn guild should not care about the members' race-origin teams.

A Freeborn guild may contain, for example:

```text
Human Freeborn
Orc Freeborn
Blood Elf Freeborn
Night Elf Freeborn
```

because all of them have:

```text
GetTeamId() == TEAM_FREEBORN
```

Guild membership does **not** override Freeborn PvP hostility.

Two Freeborn guildmates remain hostile players outside a valid cooperative group.

Add persistent `teamId` to offline/cache data used during guild invitations so offline race-origin assumptions cannot bypass this rule.

Do not use `GetOriginTeamId()` to determine Freeborn guild eligibility.

## 16. Arena teams

Freeborn arena participation is supported.

Because normal manual grouping rules allow Freeborn to manually group only with Freeborn, rated arena team/group creation should follow that same restriction unless an existing custom matchmaking system creates the group automatically.

Persistent membership checks should use:

```text
TEAM_FREEBORN
```

not race-origin Alliance/Horde.

Once the arena begins, temporary arena side assignment is authoritative for combat.

The player's persistent:

```text
GetTeamId() == TEAM_FREEBORN
```

must remain unchanged.

Do not convert the player's persistent TeamId merely to place them on an arena side.

## 17. Communication

Freeborn can communicate with Alliance, Horde, and other Freeborn players.

Support:

```text
/say
/yell
/whisper
channels
party
raid
guild
emotes
other existing faction-free chat paths
```

Do not grant every language skill merely to accomplish this.

Preserve racial languages and use the server's existing faction-free communication behavior wherever possible.

`TEAM_FREEBORN` must not create a new language unless a separate future feature explicitly adds one.

Persistent team and language knowledge are separate systems.

## 18. Trade and inspect

Freeborn may directly trade with:

```text
TEAM_ALLIANCE
TEAM_HORDE
TEAM_FREEBORN
```

This includes item trading and enchanting through the trade window.

Freeborn may inspect players of all three persistent teams.

Do not equate:

```text
CanTradeWith()
```

with:

```text
IsFriendlyTo()
```

They are intentionally different concepts.

A hostile Freeborn may be permitted to trade with a Horde player while still being a hostile PvP relationship outside the trade interaction.

Normal restrictions such as combat state, distance, death, logout, etc. should remain.

Direct healing/buffing of hostile non-group players should **not** become allowed merely because trade is allowed.

## 19. Mail

Freeborn may send and receive mail with:

```text

Alliance

Horde

Freeborn

```

Use the server's existing faction-free mail functionality where available.

Do not introduce a Freeborn-only mailbox network.

---

## 20. Auction houses

Freeborn may use all available auction houses.

If the server already runs a unified or faction-free auction house, Freeborn should use that existing system unchanged.

Do not create a third Freeborn auction house.

---

## 21. Starting state

A newly created Freeborn character uses the exact normal creation template for its race and class.

Examples:

A Human Freeborn receives normal Human:

```text

starting location

starting spells

racial skills

languages

starting items

starting reputations

cinematic

homebind

origin-side initial taxi nodes

```

An Orc Freeborn receives the same defaults an ordinary Orc would receive.

Freeborn selection must be applied **after or alongside** normal race/class creation data without replacing that data.

---

## 22. Reputation

Freeborn can earn reputation with both Alliance and Horde factions.

A Freeborn player may simultaneously reach, for example:

```text

Exalted with Stormwind

Exalted with Orgrimmar

```

Do not automatically mirror, convert, delete, or reset reputations.

Starting reputation remains the character's normal racial starting reputation.

Audit `ReputationMgr` for assumptions that:

```text

opposing-faction reputation must remain hidden

opposing-faction reputation must remain forced hostile

opposing-faction reputation cannot increase

own-side reputation must be forced peaceful

```

Freeborn must be able to store, update, display, and advance reputations from both sides.

Where stock faction flags such as forced invisibility/forced reaction interfere with this requirement, add a Freeborn-team-aware exception rather than globally changing the faction.

Freeborn NPC usability should not be blocked merely because the character's race would normally be considered an enemy of that NPC faction.

Do not rewrite the character's initial reputation values solely to achieve NPC access.

---

## 23. Quests

Freeborn can obtain quests from both Alliance and Horde questgivers.

Audit:

```cpp

Player::CanSeeStartQuest()

Player::CanTakeQuest()

Player::SatisfyQuestRace()

Player::SatisfyQuestPreviousQuest()

Player::SatisfyQuestExclusiveGroup()

ConditionMgr quest-related team checks

questgiver visibility

quest accept handlers

quest reward handlers

```

For Freeborn characters, faction/race-side quest restrictions should not prevent access to opposite-faction content.

Continue enforcing unrelated requirements:

```text

class

level

skill

profession

reputation

prerequisite quest

daily/weekly limits

seasonal requirements

other gameplay requirements

```

Do not globally bypass every `ConditionMgr` condition.

Only faction/team/race-side conditions relevant to Freeborn faction access should be Freeborn-team-aware.

---

## 24. Duplicate Alliance/Horde quests

Where the game has equivalent Alliance and Horde versions of the same quest/content, prefer the version matching the character's **origin race team**.

Examples:

```text
Blood Elf Freeborn -> origin Horde -> prefer Horde duplicate
Human Freeborn     -> origin Alliance -> prefer Alliance duplicate
```

Do not determine this preference from `GetTeamId()` because a Freeborn player returns:

```text
TEAM_FREEBORN
```

For this specific legacy-content decision, use:

```cpp
GetOriginTeamId()
```

or the equivalent race-derived helper.

Do not attempt to detect duplicate quests using fuzzy quest-name matching or objective similarity.

Add an explicit DB mapping for known paired quests.

Suggested generic table:

```sql
CREATE TABLE player_team_quest_pair (
    allianceQuest INT UNSIGNED NOT NULL,
    hordeQuest    INT UNSIGNED NOT NULL,
    PRIMARY KEY (allianceQuest, hordeQuest)
);
```

When a Freeborn character evaluates one of these mapped pairs:

```text
Origin Alliance -> expose Alliance version
Origin Horde    -> expose Horde version
```

If neither quest is mapped as an equivalent pair, Freeborn may access both sides normally.

Completing/rewarding one member of an explicitly equivalent pair should prevent reward exploitation through its counterpart unless existing quest data already handles mutual exclusion.

Do not automatically suppress unrelated opposite-faction quests.

## 25. Quest rewards and faction rewards

Freeborn can obtain Alliance and Horde faction rewards.

This includes:

```text

quest rewards

reputation rewards

tabards

mount access

faction vendors

other side-specific rewards

```

Do not globally remove every true race restriction from every item.

Where a restriction exists only because an item/reward is faction-side restricted, route eligibility through a Freeborn-team-aware check.

Preserve genuine requirements such as:

```text

class

profession

level

skill

specific gameplay prerequisites

```

Audit the customized server's existing race-mask implementation before changing item/spell masks.

Do not assume stock race masks or stock playable-race lists.

---

## 26. Taxi system

A Freeborn character starts with its normal race's taxi knowledge.

Example:

```text

Human Freeborn -> normal Human/Alliance initial taxi nodes

Orc Freeborn   -> normal Orc/Horde initial taxi nodes

```

After creation, Freeborn may discover and use both Alliance and Horde flight paths.

Audit:

```text

taxi-node learning

flightmaster gossip

taxi node visibility

taxi destination validation

team-specific taxi filtering

taximask save/load

taxi route calculation

```

Do not invent a third taxi mask.

Use the existing character taxi storage and simply allow Freeborn to learn/use both sides.

---

## 27. Transportation

Freeborn may use both factions':

```text

boats

zeppelins

portals

teleports

transport NPCs

other faction transportation

```

Reuse existing faction-free transport behavior where possible.

---

## 28. Battlegrounds

Freeborn can queue for battlegrounds.

A Freeborn player's persistent team remains:

```text
TEAM_FREEBORN
```

before, during, and after the battleground.

When entering a battleground, assign each Freeborn participant temporarily to one of the two existing match sides:

```text
TEAM_ALLIANCE
or
TEAM_HORDE
```

This is **match assignment only**.

Never modify the persistent:

```text
race
characters.teamId
Player::GetTeamId()
GetOriginTeamId()
reputation
```

to represent battleground placement.

Use the battleground system's existing temporary team state.

Audit the current fork's equivalents of:

```text
GroupQueueInfo::teamId
Player::SetBattlegroundId()
Player::GetBgTeamId()
BattlegroundQueue
BattlegroundMgr
BattleGroundHandler
Battleground::AddPlayer()
Battleground::RemovePlayerAtLeave()
```

Freeborn should be eligible for either battleground side.

Do not automatically place a Human Freeborn on Alliance or an Orc Freeborn on Horde.

Prefer normal matchmaking/team balancing.

If a Freeborn premade enters together, all members of that queued group must be assigned to the same temporary battleground side.

Inside the battleground:

```text
same GetBgTeamId() = friendly
opposite GetBgTeamId() = hostile
```

This temporary relationship overrides the normal persistent `TEAM_FREEBORN` hostility rules.

On leaving the battleground, normal Freeborn relationships resume.

### Two-sided battleground arrays remain two-sided

Adding `TEAM_FREEBORN` to the persistent `TeamId` enum must **not** cause battleground side arrays to become three-sided automatically.

Any structure that represents exactly two battleground sides must remain indexed by the temporary match team.

Audit code for patterns such as:

```cpp
array[player->GetTeamId()]
```

inside battleground logic.

If the array is a match-side array, that is wrong for a Freeborn player and must use the match team:

```cpp
array[player->GetBgTeamId()]
```

or the fork's equivalent safe side index.

Do not add a third battleground side.

Do not create three-sided battleground objectives, graveyards, scoreboards, or win conditions.

## 29. Arenas

Use the same principle for arenas.

A Freeborn player's persistent team remains:

```text
TEAM_FREEBORN
```

Arena side is temporary match state.

Inside an arena:

```text
same arena side = friendly
opposite arena side = hostile
```

Use the arena/match-side API for combat and team-indexed match structures.

Do not index two-sided arena arrays using a Freeborn player's persistent `GetTeamId()`.

When the match ends, the player still has:

```text
GetTeamId() == TEAM_FREEBORN
```

and normal Freeborn relationships resume automatically.

Do not create a three-sided arena implementation.

## 30. Freeborn safe-area PvP and BG/Arena distinction

Capital/sanctuary protection applies to the open world.

Do not let that protection accidentally disable combat inside battleground or arena maps merely because an area entry happens to contain unusual flags.

Explicit instanced battleground/arena match context has priority.

---

## 31. Conversion after creation

Characters may be converted into or out of `TEAM_FREEBORN` after creation.

Supported operations for this feature are conceptually:

```text
origin/native team -> TEAM_FREEBORN
TEAM_FREEBORN -> origin/native team
```

Converting into Freeborn sets the persistent player team to:

```text
TEAM_FREEBORN
```

Converting out of Freeborn sets the persistent player team to the team naturally associated with the character's current race:

```cpp
SetPlayerTeamId(GetOriginTeamId());
```

or the fork's equivalent.

Changing persistent team does not automatically remove a character from an existing party, raid, or guild; membership persists. Existing group cooperation continues normally, while guild membership alone does not make players friendly. Team restrictions apply to new membership changes.

Changing persistent team must not change race.

If the server's existing race/faction-change service changes the character's race:

- `GetOriginTeamId()` must naturally reflect the new race.
- If the character is currently `TEAM_FREEBORN`, the persistent team remains `TEAM_FREEBORN`.
- If the character is not Freeborn, the faction/race-change service should update the persistent team to the appropriate Alliance/Horde team as part of its normal conversion behavior.

Team changes must not destructively rewrite:

```text
reputation
quests
items
spells
taxi nodes
achievements
titles
```

unless an existing faction-change service explicitly does so for another reason.

This keeps Freeborn conversion reversible.

The persistent `teamId` column is the source of truth for the player's current team.

Race remains the source of truth for origin team.

## 32. GM commands

Implement generic player-team commands.

Preferred naming should avoid colliding with any existing AzerothCore `.team` command.

For example:

```text
.playerteam status [player]
.playerteam set freeborn [player]
.playerteam set native [player]
```

Where:

```text
set freeborn -> TEAM_FREEBORN
set native   -> TeamIdForRace(currentRace)
```

Also provide convenience aliases if practical:

```text
.freeborn status
.freeborn set
.freeborn remove
```

Commands should work on online and offline characters where the command framework reasonably supports it.

Use RBAC permissions.

Do not expose arbitrary unsupported `TeamId` values through the command parser.

After changing team on an online character:

```text
refresh persistent team state
refresh client Freeborn visual indicator
re-evaluate PvP relationship
re-evaluate group/guild eligibility where appropriate
refresh NPC/quest visibility if needed
refresh any cached team-dependent data
```

Do not require relog unless technically unavoidable.

A status command should report both:

```text
Persistent TeamId: TEAM_FREEBORN
Origin TeamId: TEAM_ALLIANCE
```

for a Human Freeborn, for example.

## 33. Eluna

Expose the third player team cleanly to Eluna.

Existing Eluna APIs that return the player's actual `TeamId` should return `TEAM_FREEBORN` for a Freeborn player after this feature is implemented.

At minimum expose behavior equivalent to:

```lua
player:IsFreeborn()
player:GetTeamId()
player:GetOriginTeamId()
```

Also support controlled modification through a safe API such as:

```lua
player:SetPlayerTeamId(teamId)
```

or an equivalent restricted setter.

Provide named constants rather than magic numbers where the Eluna binding system permits it:

```lua
TEAM_ALLIANCE
TEAM_HORDE
TEAM_FREEBORN
```

Do not require scripts to know the numeric value of `TEAM_FREEBORN`.

Add a team-changed hook if practical:

```text
OnPlayerTeamChanged(player, oldTeamId, newTeamId)
```

This will make custom content much easier.

If the existing Eluna `GetTeam()` API exposes a different legacy concept than `TeamId`, preserve its documented meaning and add an explicit `GetTeamId()`/`GetOriginTeamId()` binding rather than silently changing unrelated semantics.

## 34. Script/module API

Expose enough of the team system that external modules do not need to duplicate core logic or read the DB column directly.

Prefer a reusable API so modules can ask:

```text
IsFreeborn
GetTeamId
GetOriginTeamId
CanManualGroup
CanGuildTogether
ArePlayersHostile
CanUseFactionNpc
```

rather than inspecting race masks or importing `characters.teamId` themselves.

Consider adding a `PlayerScript`/`ScriptMgr` notification when the persistent team changes.

Modules must be able to distinguish:

```text
persistent player team
race-origin team
temporary match team
```

without guessing from race or battleground state.

## 35. Playerbots

Playerbots must never be Freeborn.

Do not generate Freeborn playerbots.

Do not allow the bot module to choose Freeborn during character creation.

GM conversion commands should reject converting an active/recognized playerbot to Freeborn where the playerbot API allows reliable detection.

An ordinary Alliance/Horde playerbot still counts as a **player** for relationship purposes.

Therefore:

```text

Freeborn player vs Alliance playerbot = hostile player relationship

Freeborn player vs Horde playerbot    = hostile player relationship

```

Do not accidentally treat playerbots as friendly NPCs.

---

## 36. Full client distinction

Freeborn should have clear visual identification as a true third player team.

Implement support for:

```text
Freeborn character-creation selection state
Freeborn character-select badge
target/portrait indication
nameplate indication
tooltip indication
custom Freeborn team/PvP emblem where appropriate
/who distinction if supported by the customized client
```

Character-select backgrounds remain race-origin based for this phase.

The client does not need to become a fully three-faction stock UI everywhere at once.

Avoid adding new packet structures solely for cosmetic metadata when an existing verified-safe custom channel can carry the distinction.

For in-world metadata, prefer one of:

```text
verified unused player/update flag
existing custom client side-channel
standard addon-message side-channel
another already-existing custom protocol in this client
```

The server database `teamId` remains authoritative.

Do not store Freeborn identity independently in multiple client-facing flags.

Any client flag is only a presentation/transport representation of:

```text
GetTeamId() == TEAM_FREEBORN
```

## 37. Social/UI distinction versus combat state

A Freeborn indicator means:

```text
"This character's persistent player team is TEAM_FREEBORN."
```

It does not mean:

```text
"This character is currently attackable."
```

A Freeborn player standing in Stormwind may still display a Freeborn team emblem while being protected from PvP combat by the safe-area rule.

Likewise, a Freeborn player inside a battleground may still be identified as Freeborn in persistent-character UI even though the match temporarily assigns that player to the Alliance or Horde battleground side.

Persistent team identity and current combat eligibility must remain separate.

## 38. Team APIs and origin-team semantics

Audit the source tree for all significant uses of:

```text
GetTeam()
GetTeamId()
TeamIdForRace()
GetBgTeamId()
MAX_TEAMS
TEAM_NEUTRAL
TEAM_ALLIANCE
TEAM_HORDE
FACTION_MASK_ALLIANCE
FACTION_MASK_HORDE
RACEMASK_ALLIANCE
RACEMASK_HORDE
RequiredRaces
faction-template masks
team-indexed arrays
```

Classify every use as one of:

```text
persistent player-team identity
race-origin identity
NPC faction interaction
player hostility
social eligibility
quest eligibility
BG/Arena match team
cosmetic/client display
two-sided array indexing
```

Then use the correct source.

### Persistent player-team identity

Use:

```cpp
player->GetTeamId()
```

A Freeborn player returns:

```text
TEAM_FREEBORN
```

### Race-origin identity

Use:

```cpp
player->GetOriginTeamId()
```

or:

```cpp
TeamIdForRace(player->getRace())
```

This is appropriate for legacy data such as race-derived starting defaults and explicit paired Alliance/Horde content.

### BG/Arena match identity

Use:

```cpp
player->GetBgTeamId()
```

or the equivalent temporary match-side API.

Do not mechanically replace every `GetTeamId()` call with origin-team logic just to keep old code compiling.

Likewise, do not mechanically extend every Alliance/Horde array to three entries merely because `TEAM_FREEBORN` now exists.

The question at every call site is:

```text
"What concept is this code actually asking for?"
```

That audit is mandatory for a safe third-TeamId implementation.

## 39. Recommended relationship model

Do not overload one "faction" variable to answer every question.

The game now needs these independent concepts:

```text
Persistent Player Team
    TEAM_ALLIANCE / TEAM_HORDE / TEAM_FREEBORN
    Stored in the character DB.
    Returned by Player::GetTeamId().

Origin Team
    TEAM_ALLIANCE / TEAM_HORDE
    Derived from race.
    Used for race-origin legacy content only.

Match Team
    TEAM_ALLIANCE / TEAM_HORDE during BG/Arena only.
    Temporary and never persisted as the player's real team.

Cooperative Context
    party / raid / LFG / BG / Arena
    Can temporarily override normal hostility.

NPC Interaction Policy
    determines whether faction NPC services are available.

PvP Relationship
    friendly/hostile.
    Freeborn-vs-Freeborn is normally hostile despite identical TeamId.

PvP Eligibility
    whether combat is currently allowed under normal PvP rules.
```

These are intentionally separate.

The key architectural rule is:

```text
TEAM_FREEBORN is real.

Origin Alliance/Horde ancestry is also real.

They answer different questions.
```

A Human Freeborn is not internally Alliance for player-team identity.

It is:

```text
Persistent Team: TEAM_FREEBORN
Origin Team:     TEAM_ALLIANCE
```

An Orc Freeborn is:

```text
Persistent Team: TEAM_FREEBORN
Origin Team:     TEAM_HORDE
```

That distinction is the core of this feature.

## 40. Freeborn behavior matrix

| Situation | Expected behavior |
| --- | --- |
| Freeborn player's `GetTeamId()` | `TEAM_FREEBORN` |
| Human Freeborn `GetOriginTeamId()` | `TEAM_ALLIANCE` |
| Orc Freeborn `GetOriginTeamId()` | `TEAM_HORDE` |
| Freeborn -> Alliance NPC | Usable |
| Freeborn -> Horde NPC | Usable |
| Freeborn -> neutral NPC | Normal rules |
| Freeborn -> hostile monster | Normal hostile behavior |
| Freeborn -> Alliance player | Hostile where PvP is enabled |
| Freeborn -> Horde player | Hostile where PvP is enabled |
| Freeborn -> Freeborn player | Hostile where PvP is enabled |
| Alliance/Horde player -> Freeborn | Hostile under the same PvP rules |
| Freeborn in capital/sanctuary | Non-hostile for ordinary PvP |
| Freeborn manual group with Alliance/Horde | Disallowed |
| Freeborn manual group with Freeborn | Allowed |
| Freeborn grouped with Freeborn | Friendly within group |
| Freeborn LFG with Alliance/Horde | Allowed |
| Freeborn same LFG group | Friendly |
| Freeborn guild with Alliance/Horde | Disallowed |
| Freeborn guild with Freeborn | Allowed |
| Freeborn guildmates outside group | Still hostile |
| Freeborn trade with Alliance/Horde | Allowed |
| Freeborn inspect Alliance/Horde | Allowed |
| Freeborn mail Alliance/Horde | Allowed |
| Freeborn auction houses | All |
| Freeborn Alliance reputation | Allowed |
| Freeborn Horde reputation | Allowed |
| Freeborn Alliance quests | Allowed |
| Freeborn Horde quests | Allowed |
| Duplicate faction quest | Prefer origin race team |
| Freeborn taxi | Both sides learnable |
| Freeborn BG persistent team | Remains `TEAM_FREEBORN` |
| Freeborn BG match side | Temporary Alliance/Horde assignment |
| Freeborn arena persistent team | Remains `TEAM_FREEBORN` |
| Freeborn arena match side | Temporary Alliance/Horde assignment |
| Freeborn playerbot | Disallowed |
| Alliance/Horde playerbot vs Freeborn | Treat bot as player |
| Starting area/data | Normal race defaults via origin team |
| Character-select background | Origin-race default |
| Character-select team marker | Freeborn indicator |

Player-hostility entries apply only where PvP is enabled. In no-PvP areas, ordinary Freeborn hostility is inactive.

Sharing `TEAM_FREEBORN` does not by itself make two Freeborn players friendly.

## 41. Testing requirements

Create automated tests where the existing test architecture permits them and an explicit manual QA checklist for client-side behavior.

At minimum test:

### TeamId persistence

Create:

```text
Native Human
Freeborn Human
Native Orc
Freeborn Orc
```

Verify before and after worldserver restart:

```text
Native Human:
    GetTeamId() == TEAM_ALLIANCE
    GetOriginTeamId() == TEAM_ALLIANCE

Freeborn Human:
    GetTeamId() == TEAM_FREEBORN
    GetOriginTeamId() == TEAM_ALLIANCE

Native Orc:
    GetTeamId() == TEAM_HORDE
    GetOriginTeamId() == TEAM_HORDE

Freeborn Orc:
    GetTeamId() == TEAM_FREEBORN
    GetOriginTeamId() == TEAM_HORDE
```

Verify the DB `teamId` values persist exactly.

Verify no existing migrated character becomes Freeborn accidentally.

### Team enum and array safety

Audit/test code paths that index arrays by `TeamId`.

Specifically test that a Freeborn player's `TEAM_FREEBORN` value cannot cause:

```text
out-of-bounds access
incorrect battleground side indexing
incorrect arena side indexing
incorrect Alliance/Horde legacy table lookup
incorrect neutral-team behavior
```

Add assertions or safe conversion helpers where practical.

### Creation defaults

Verify Freeborn and normal versions of the same race receive identical:

```text
spawn
class setup
racials
languages
starting items
cinematic
homebind
starting reputation
origin-side initial taxi nodes
```

except for persistent player `TeamId`.

Verify no creation code attempts to look up nonexistent Freeborn race-start data merely because:

```text
GetTeamId() == TEAM_FREEBORN
```

### NPCs

Test Freeborn Human and Freeborn Horde-origin race against:

```text
Stormwind NPC
Orgrimmar NPC
Alliance guard
Horde guard
neutral vendor
hostile monster
```

### PvP

Test hostility in both directions:

```text
Human Freeborn vs Human Alliance
Human Freeborn vs Orc Horde
Human Freeborn vs Orc Freeborn
Human Freeborn vs Human Freeborn
Human Alliance vs Human Freeborn
Orc Horde vs Human Freeborn
```

In no-PvP areas, verify ordinary Freeborn hostility is inactive.

In PvP-enabled areas, verify hostility is symmetric while attackability still follows normal PvP rules.

Test:

```text
capital city
sanctuary
friendly territory
contested area
PvP-flagged state
unflagged state
FFA PvP area
```

Verify hostility and attackability are separate.

Verify two Freeborn players are not automatically friendly merely because their `GetTeamId()` values match.

### Groups

Test:

```text
Freeborn invites Alliance -> fail
Freeborn invites Horde -> fail
Freeborn invites Freeborn -> success
Freeborn group members can heal/buff/resurrect one another
leave group -> hostility returns
```

### Guilds

Test:

```text
Freeborn guild invites Alliance -> fail
Freeborn guild invites Horde -> fail
Alliance/Horde guild invites Freeborn -> fail
Freeborn guild invites Freeborn -> success
```

Test online and offline/cache invite paths.

Verify mixed-origin Freeborn members can share one guild:

```text
Human Freeborn
Orc Freeborn
Blood Elf Freeborn
Night Elf Freeborn
```

### LFG

Create a mixed:

```text
Alliance
Horde
Freeborn
```

LFG group.

Verify all members can:

```text
enter
heal
buff
resurrect
loot
complete dungeon
leave cleanly
```

Verify the Freeborn player's persistent `GetTeamId()` remains `TEAM_FREEBORN` for the entire dungeon.

Verify hostility returns when the Freeborn player leaves the cooperative group.

### Quests

Test Freeborn access to:

```text
origin-side quest
opposite-side quest
class quest
profession quest
reputation-gated quest
paired Alliance/Horde quest
quest with team ConditionMgr condition
```

Verify unrelated requirements remain enforced.

Verify paired quest preference uses `GetOriginTeamId()`, not `GetTeamId()`.

### Reputation

Verify a Freeborn character can gain:

```text
Stormwind reputation
Orgrimmar reputation
```

on the same character.

Verify save/reload.

Verify rep vendors.

### Taxi

Verify:

```text
origin-side starting taxi mask unchanged
Alliance node learnable
Horde node learnable
both remain after relog
both routes usable
```

### Trade/social

Verify Freeborn can:

```text
whisper Alliance/Horde
trade Alliance/Horde
receive enchant through trade
inspect Alliance/Horde
mail Alliance/Horde
use AH
```

without making those players globally friendly.

### Battleground

Queue several Freeborn characters with mixed origin races.

Verify each still has:

```text
GetTeamId() == TEAM_FREEBORN
```

while matchmaking can assign them to either temporary Alliance/Horde side.

Verify:

```text
GetBgTeamId() is Alliance or Horde
same BG team friendly
opposing BG team hostile
BG UI works
objectives work
spirit guides work
scoreboard works
graveyards work
leave/rejoin works
persistent TeamId unchanged afterward
```

Specifically test every two-sided BG array touched by a Freeborn player.

### Arena

Repeat equivalent persistent-team versus temporary-match-team testing.

### Conversion

Test:

```text
Alliance-origin -> Freeborn
Horde-origin -> Freeborn
Freeborn -> origin/native team
```

online and offline.

Verify no reputation, quest, item, or taxi data is destroyed.

Verify existing group and guild memberships persist through conversion.

Verify returning from Freeborn uses the character's current race to determine Alliance/Horde origin.

### Race/faction change while Freeborn

Verify:

```text
Human Freeborn -> race change to Orc
```

results in:

```text
GetTeamId() == TEAM_FREEBORN
GetOriginTeamId() == TEAM_HORDE
```

without losing Freeborn identity.

### Eluna

Test:

```text
GetTeamId()
GetOriginTeamId()
IsFreeborn()
SetPlayerTeamId()
team-changed hook
```

### Playerbots

Verify bot generation/conversion cannot create Freeborn bots.

Verify ordinary Alliance/Horde playerbots remain valid hostile player targets for Freeborn.

## 42. Compatibility audit

Before considering implementation complete, search the entire core and installed modules for assumptions that player `TeamId` can only be Alliance or Horde.

At minimum audit:

```text
Player
Unit / WorldObject reaction code
ObjectMgr
CharacterHandler
CharacterDatabase
CharacterCache
ReputationMgr
Quest system
ConditionMgr
NPC handlers
Group
Guild
LFGMgr
BattlegroundMgr
BattlegroundQueue
Battleground
Arena
Taxi
Mail
AuctionHouse
Trade
Chat
Social
Spell target validation
Pet/guardian ownership
Playerbots
AutoBalance
Eluna
custom faction-free code
custom race code
custom client runtime
```

Pay special attention to code patterns like:

```cpp
player->GetTeamId() == other->GetTeamId()
player->GetTeamId() != other->GetTeamId()
player->GetTeam() != other->GetTeam()
TeamIdForRace(player->getRace())
array[player->GetTeamId()]
for (... team < MAX_TEAMS ...)
RACEMASK_ALLIANCE
RACEMASK_HORDE
```

Every use must be classified.

Ask:

```text
Does this code need the persistent player team?
Does it need the race-origin Alliance/Horde team?
Does it need the temporary BG/Arena match side?
Is it indexing a two-sided data structure?
Is it using a neutral/sentinel TeamId?
```

Do not mechanically replace these calls.

### Required third-TeamId audit

Search specifically for:

```text
switch (TeamId)
switch (GetTeamId())
TEAM_ALLIANCE
TEAM_HORDE
TEAM_NEUTRAL
MAX_TEAMS
TEAM_COUNT
std::array<..., 2>
[2]
teamId == 0
teamId == 1
```

where those patterns are team-related.

Any switch over persistent player team must explicitly decide what `TEAM_FREEBORN` means.

Any two-sided match/origin structure must not accidentally accept `TEAM_FREEBORN` as an index.

Compile warnings, sanitizers, assertions, and automated tests should be used to catch unsafe assumptions where available.

## 43. Implementation phases

Implement in this order:

### Phase A: Audit

Document the current faction-free/custom-race/client modifications.

Audit the existing `TeamId`, `Team`, `TEAM_NEUTRAL`, `MAX_TEAMS`, team-indexed arrays, battleground side structures, and every major `GetTeamId()` call site.

Determine a unique non-colliding `TEAM_FREEBORN` value before editing the enum.

### Phase B: Third-TeamId foundation

Implement:

```text
TEAM_FREEBORN
persistent characters.teamId
Player::GetTeamId() third-team behavior
Player::GetOriginTeamId()
CharacterCache support
safe setters
team-change notifications
migration of existing characters
```

No broad gameplay modifications yet.

Compile and test persistence before moving on.

### Phase C: Creation/client signaling

Implement Freeborn character-creation UI and server decode.

Verify:

```text
Freeborn creation stores TEAM_FREEBORN
normal creation stores race-derived Alliance/Horde
Freeborn and normal versions receive identical race/class starting data
```

### Phase D: Visual signaling

Implement character-select/in-world Freeborn distinction while retaining race-origin backgrounds.

### Phase E: NPC/reputation/quest/taxi

Implement dual-faction PvE access.

Use origin team only where legacy race-origin content genuinely requires it.

### Phase F: Player relationship policy

Implement Freeborn player hostility, Freeborn-vs-Freeborn hostility, safe-area protection, trade, communication, manual grouping, and guild rules.

### Phase G: LFG

Implement cooperative override without changing persistent `TeamId`.

### Phase H: Battleground/Arena

Implement temporary Alliance/Horde match assignment.

Audit every two-sided array so persistent `TEAM_FREEBORN` is never used as an unsafe match-side index.

### Phase I: Eluna/commands/modules

Implement API, commands, Playerbot protection, AutoBalance/module compatibility, and team-change hooks.

### Phase J: Regression testing

Run the complete matrix.

Verify:

```text
Alliance behavior remains unchanged
Horde behavior remains unchanged
Freeborn returns TEAM_FREEBORN
origin-team behavior remains race-correct
two-sided BG/Arena systems remain stable
```

Do not combine every phase into one giant unreviewable patch.

## 44. Required Codex deliverables

For each implementation phase, provide:

```text

files changed

reason for each change

database migration

client changes

server changes

new APIs

compatibility concerns

tests performed

remaining known issues

```

Keep SQL migrations compatible with the repository's existing migration layout.

Do not manually edit base SQL if this fork expects incremental migrations.

Compile after meaningful core phases rather than waiting until the end.

Do not suppress compiler warnings to make the feature build.

---

## 45. Non-goals

Do NOT implement:

```text
a separate PlayerAlignment enum as the authoritative Freeborn identity
an isFreeborn-only architecture
three-sided battlegrounds
three-sided arenas
a Freeborn auction house
a Freeborn taxi mask
new racial starting zones
new Freeborn starting reputations
new Freeborn languages
a mandatory new character-select background
Freeborn playerbots
packet-size changes unless absolutely necessary
a fake DBC faction-template value solely to make TEAM_FREEBORN exist
automatic conversion of all two-sided arrays into three-sided arrays
```

`TEAM_FREEBORN` **is** explicitly in scope and is required.

The goal is a true third persistent player TeamId, while retaining two-sided subsystems where their gameplay is still intentionally Alliance-versus-Horde.

## 46. Final acceptance criteria

The feature is complete when a player can:

1. Select **Freeborn** during character creation.

2. Create any playable race as Freeborn.

3. Have the created character persist:

```text
GetTeamId() == TEAM_FREEBORN
```

4. Retain a correct race-derived origin team through:

```text
GetOriginTeamId()
```

5. Retain that race's normal starting experience, racial data, languages, cinematic, starting reputations, and initial taxi state.

6. Be visibly identified as Freeborn during character creation, on character select, and in-game.

7. Freely use Alliance and Horde NPCs and services.

8. Quest for both sides.

9. Gain reputation with both sides simultaneously.

10. Learn and use both sides' taxi systems.

11. Be hostile symmetrically to Alliance, Horde, and ungrouped Freeborn players where PvP is enabled, and non-hostile in no-PvP areas.

12. Still obey normal PvP attackability rules.

13. Be completely protected from hostile player combat in capitals/main cities/sanctuaries.

14. Manually group only with Freeborn.

15. Guild only with Freeborn.

16. Communicate, trade, inspect, mail, and use AHs across all three player teams.

17. Join mixed-team LFG groups and cooperate normally inside them.

18. Enter battlegrounds/arenas using temporary Alliance/Horde match assignment while the persistent player TeamId remains `TEAM_FREEBORN`.

19. Return to normal Freeborn hostility after leaving temporary cooperative contexts, unless in a no-PvP area.

20. Be converted between `TEAM_FREEBORN` and the character's race-origin Alliance/Horde team without destructive character changes.

21. Remain `TEAM_FREEBORN` through race changes while `GetOriginTeamId()` updates to match the new race.

22. Be queried/controlled through GM commands, core APIs, modules, and Eluna.

23. Continue to coexist with the server's existing faction-free and custom-race systems.

24. Never use persistent `TEAM_FREEBORN` as an unsafe index into two-sided battleground/arena/origin-team arrays.

Most importantly:

**Freeborn must be implemented as a real, unique, persistent third `TeamId`. Race-derived Alliance/Horde origin remains a separate concept used only where legacy race-origin behavior requires it.**
