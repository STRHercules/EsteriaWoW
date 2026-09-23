# Freeborn Player Alignment Implementation Specification

**Project:** AzerothCore 3.3.5a, heavily customized fork
**Feature:** Third selectable player alignment, **Freeborn**
**Date:** September 22, 2026

## 1. Objective

Implement **Freeborn** as a third selectable player alignment alongside the normal Alliance and Horde experience.

Freeborn is **not** a third AzerothCore `TeamId`.

A Freeborn character must retain the Alliance/Horde team naturally determined by its race. A Human Freeborn remains internally Alliance. An Orc Freeborn remains internally Horde. Native team must continue controlling racial starting data, cinematics, languages, racial spells, native starting reputations, starting location, initial taxi data, and other race-derived behavior.

Freeborn is a separate alignment layer placed above the character's native team.

The implementation must also be designed so another custom alignment can be added later without another large core rewrite.

---

# 2. Critical architectural rule

Do **not** expand or reinterpret AzerothCore's existing `TEAM_ALLIANCE` / `TEAM_HORDE` model into a three-team model.

Do **not** make `GetTeam()`, `GetTeamId()`, `TeamIdForRace()`, race faction data, battleground arrays, or other two-team systems return a fake Freeborn team.

Instead implement:

```cpp
enum class PlayerAlignment : uint8
{
    Native   = 0,
    Freeborn = 1
};
```

Today, `Freeborn` is effectively an `isFreeborn` flag.

Persist it as an enum rather than a boolean so future alignments can be added without another schema redesign.

Design the alignment persistence, policy API, and integration points to support future alignment values. Only Native and Freeborn behavior is in scope now; do not invent additional alignments.

Conceptually:

```text
Race:          Blood Elf
Native Team:   Horde
Alignment:     Freeborn
```

NOT:

```text
Race:          Blood Elf
Team:          Freeborn
```

Provide at minimum:

```cpp
PlayerAlignment GetAlignment() const;
bool IsFreeborn() const;

TeamId GetNativeTeamId() const;
```

`GetNativeTeamId()` must always be race-derived.

Do not create a persisted `nativeTeam` field unless the existing customized core already requires one. Race is the source of truth.

---

# 3. Existing server behavior must be preserved

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

# 4. Database model

Add an alignment column to the character database.

Preferred form:

```sql
ALTER TABLE characters
ADD COLUMN alignment TINYINT UNSIGNED NOT NULL DEFAULT 0;
```

Values:

```text
0 = Native
1 = Freeborn
```

All existing characters must migrate as:

```text
alignment = 0
```

No existing character becomes Freeborn automatically.

Update all relevant prepared statements and load/save paths, including the customized fork's equivalents of:

```text
CHAR_INS_CHARACTER
CHAR_UPD_CHARACTER if required
CHAR_SEL_CHARACTER
CHAR_SEL_ENUM
CHAR_SEL_ENUM_DECLINED_NAME
character cache queries
offline character lookup queries where alignment decisions are needed
```

Alignment must survive:

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

Add alignment to `CharacterCacheEntry` or the fork's equivalent offline-character cache.

This is important because guild invitations, commands, mail/social operations, and other systems may make decisions about characters that are not currently online.

The database alignment value is the authoritative source of truth.

---

# 5. Character creation

The customized character creation screen will contain a **Freeborn button between the gender buttons**.

All playable races can be Freeborn.

Selecting Freeborn must **not** change the race ID.

Example:

```text
Human + Native   = normal Human
Human + Freeborn = Human with alignment Freeborn

Orc + Native     = normal Orc
Orc + Freeborn   = Orc with alignment Freeborn
```

The same race model, customization options, gender/body settings, class availability, and appearance data should remain available unless another existing system says otherwise.

The client must maintain an explicit state:

```cpp
PlayerAlignment selectedAlignment;
```

Do not infer Freeborn from race ID, race pane, race faction, model, or appearance.

Changing races while Freeborn is selected should keep the Freeborn selection unless the existing customized UI explicitly switches the player back to native mode.

### Character creation packet

Keep the normal 3.3.5a wire protocol unchanged if reasonably possible.

The Freeborn selection still has to reach the server.

First audit the customized client and server's `CMSG_CHAR_CREATE` serialization.

A likely solution is to encode the alignment selection into an unused/reserved portion of an existing character-create field and strip it immediately server-side.

`OutfitId` is a candidate because the current AzerothCore character creation structure already carries it, but **do not blindly reserve a bit until the customized client is audited**.

For example, if testing proves the high bit is unused:

```cpp
constexpr uint8 FREEBORN_CREATE_FLAG = 0x80;

bool requestedFreeborn = (createInfo.OutfitId & FREEBORN_CREATE_FLAG) != 0;
createInfo.OutfitId &= ~FREEBORN_CREATE_FLAG;
```

Then:

```cpp
player->SetAlignment(
    requestedFreeborn
        ? PlayerAlignment::Freeborn
        : PlayerAlignment::Native);
```

This example describes the technique, not a mandatory bit assignment.

Prove that the chosen bit/value is unused by this client before adopting it.

Do not increase packet length unless no safe compatible signaling method exists.

---

# 6. Character-select display

Freeborn characters should be visibly distinguishable on character select.

However:

**Keep the race's normal Alliance/Horde character-select background for now.**

A Human Freeborn should still use the Human/Alliance-style background.

An Orc Freeborn should still use the Orc/Horde-style background.

Add a Freeborn badge/emblem/indicator elsewhere in the character-select UI.

Because alignment is not part of the stock `SMSG_CHAR_ENUM` structure, extend the server's character enumeration database query to load alignment, then communicate the distinction to the customized client without changing packet size if possible.

Preferred technique:

Use a verified-unused client-visible flag bit in an existing enum field and teach the customized client to interpret that bit as:

```text
FREEBORN
```

Do not use a bit without first auditing all existing custom flags.

The DB `alignment` column remains authoritative. Any packet/UI bit is only a transport/display representation.

---

# 7. Alignment policy layer

Do not scatter hundreds of isolated:

```cpp
if (player->IsFreeborn())
```

checks throughout the codebase.

Create a centralized alignment policy layer.

This can live on `Player`, an `AlignmentMgr`, an `AlignmentPolicy` helper, or another architecture consistent with the current fork.

At minimum centralize concepts equivalent to:

```cpp
PlayerAlignment GetAlignment(Player const* player);

TeamId GetNativeTeamId(Player const* player);

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
```

The exact API names can differ.

The important requirement is that systems query **policy**, rather than independently inventing Freeborn behavior.

---

# 8. Player versus NPC relationship

Freeborn NPC interaction and Freeborn player hostility are separate concepts.

A Freeborn character must be able to interact with NPCs belonging to both Alliance and Horde.

Expected:

```text
Freeborn -> Alliance NPC = usable
Freeborn -> Horde NPC    = usable
Freeborn -> Neutral NPC  = normal rules
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

# 9. Freeborn versus player hostility

Outside temporary cooperative contexts, Freeborn is hostile to every other player alignment.

Expected relationship:

```text
Freeborn -> Alliance player = hostile
Freeborn -> Horde player    = hostile
Freeborn -> Freeborn player = hostile
```

This hostility is symmetric: native Alliance/Horde players are also hostile to Freeborn when normal PvP rules permit combat. In areas where PvP is disabled, ordinary Freeborn player hostility is inactive (see Section 10).

This must work even when the two characters have the same native faction.

Examples:

```text
Human Freeborn vs Human Alliance = hostile

Orc Freeborn vs Orc Horde = hostile

Human Freeborn vs Orc Freeborn = hostile

Human Freeborn vs Human Freeborn = hostile
```

This is why native `TeamId` alone cannot be used to determine player hostility.

---

# 10. Hostile does NOT mean attackable everywhere

This is critical.

Outside no-PvP areas and explicit cooperative or match contexts, Freeborn are hostile to players of every alignment. This applies symmetrically: native players are also hostile to Freeborn under the same PvP conditions.

In areas where PvP is disabled, ordinary Freeborn-versus-player hostility is inactive; do not mark players hostile solely because of alignment there. In PvP-enabled areas, alignment determines the relationship, while ordinary PvP flags and other eligibility rules still determine whether combat can occur.

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

The core difference is that once PvP rules say two hostile players may fight, Freeborn hostility must work even if their native teams would normally be the same.

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

---

# 11. Capital cities and sanctuaries

Ordinary Freeborn player hostility is inactive inside capital/main-city and sanctuary areas. Neither Freeborn nor native players may initiate ordinary hostile player combat against one another there.

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
player_alignment_safe_area
    areaId
    flags/reason
```

The no-PvP area rule suppresses ordinary Freeborn hostility; this is not merely an attack-target filter.

A Freeborn player inside such an area cannot initiate or receive normal hostile player combat.

Do not break trade, inspect, mail, chat, NPC interaction, or other noncombat operations.

---

# 12. Interaction precedence

Relationship resolution should use a clear precedence.

Recommended conceptual ordering:

```text
1. Battleground/Arena temporary team
2. Valid cooperative group context
3. Safe-area/no-PvP rules suppress ordinary Freeborn hostility
4. Freeborn player-alignment hostility when PvP is enabled
5. Existing native/faction-free server logic
```

More specifically:

### Battleground/Arena

Temporary match team is authoritative.

### LFG or valid party

Members of the same active cooperative group are friendly/assistable.

### Freeborn outside cooperative context

Hostile to Alliance, Horde, and Freeborn players.

### NPCs

Use the NPC interaction policy, not player alignment hostility.

Do not let guild membership alone make two Freeborn players friendly.

---

# 13. Manual parties and raids

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

# 14. LFG

LFG is an explicit exception to the manual grouping rule.

Freeborn can be matched with:

```text
Alliance
Horde
Freeborn
```

An LFG-created group is a cooperative context.

All members of the same LFG group must be friendly/assistable for the lifetime of that group regardless of alignment.

Do not permanently change alignment or native team.

When the LFG group ends or a player leaves it, recalculate normal alignment relationships immediately.

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

---

# 15. Guilds

Freeborn may only guild with other Freeborn characters.

Allowed:

```text
Freeborn guild -> Freeborn member
```

Disallowed:

```text
Freeborn guild -> Alliance Native member
Freeborn guild -> Horde Native member

Alliance/Horde native guild -> Freeborn member
```

A Freeborn guild should not care about the members' native racial teams.

A guild may contain, for example:

```text
Human Freeborn
Orc Freeborn
Blood Elf Freeborn
Night Elf Freeborn
```

Guild membership does **not** override Freeborn PvP hostility.

Two Freeborn guildmates remain hostile players outside a valid cooperative group.

Add alignment to offline/cache data used during guild invitations so offline/native-team assumptions cannot bypass this rule.

---

# 16. Arena teams

Freeborn arena participation is supported.

Because normal manual grouping rules allow Freeborn to manually group only with Freeborn, rated arena team/group creation should follow that same restriction unless an existing custom matchmaking system creates the group automatically.

Once the arena begins, temporary arena side assignment is authoritative.

Do not change the player's native team.

---

# 17. Communication

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

Alignment must not create a new language.

---

# 18. Trade and inspect

Freeborn may directly trade with:

```text
Alliance
Horde
Freeborn
```

This includes item trading and enchanting through the trade window.

Freeborn may inspect all player alignments.

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

---

# 19. Mail

Freeborn may send and receive mail with:

```text
Alliance
Horde
Freeborn
```

Use the server's existing faction-free mail functionality where available.

Do not introduce a Freeborn-only mailbox network.

---

# 20. Auction houses

Freeborn may use all available auction houses.

If the server already runs a unified or faction-free auction house, Freeborn should use that existing system unchanged.

Do not create a third Freeborn auction house.

---

# 21. Starting state

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
native initial taxi nodes
```

An Orc Freeborn receives the same defaults an ordinary Orc would receive.

Freeborn selection must be applied **after or alongside** normal race/class creation data without replacing that data.

---

# 22. Reputation

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

Where stock faction flags such as forced invisibility/forced reaction interfere with this requirement, add an alignment-aware exception rather than globally changing the faction.

Freeborn NPC usability should not be blocked merely because the character's native race would normally be considered an enemy of that NPC faction.

Do not rewrite the character's initial reputation values solely to achieve NPC access.

---

# 23. Quests

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

Only faction/team/race-side conditions relevant to Freeborn faction access should be alignment-aware.

---

# 24. Duplicate Alliance/Horde quests

Where the game has equivalent Alliance and Horde versions of the same quest/content, prefer the version matching the character's **native race team**.

Examples:

```text
Blood Elf Freeborn -> prefer Horde duplicate
Human Freeborn     -> prefer Alliance duplicate
```

Do not determine preference from current alignment. Freeborn is always neutral for this purpose.

Do not attempt to detect duplicate quests using fuzzy quest-name matching or objective similarity.

Add an explicit DB mapping for known paired quests.

Suggested generic table:

```sql
CREATE TABLE player_alignment_quest_pair (
    allianceQuest INT UNSIGNED NOT NULL,
    hordeQuest    INT UNSIGNED NOT NULL,
    PRIMARY KEY (allianceQuest, hordeQuest)
);
```

When a Freeborn character evaluates one of these mapped pairs:

```text
Native Alliance -> expose Alliance version
Native Horde    -> expose Horde version
```

If neither quest is mapped as an equivalent pair, Freeborn may access both sides normally.

Completing/rewarding one member of an explicitly equivalent pair should prevent reward exploitation through its counterpart unless existing quest data already handles mutual exclusion.

Do not automatically suppress unrelated opposite-faction quests.

---

# 25. Quest rewards and faction rewards

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

Where a restriction exists only because an item/reward is faction-side restricted, route eligibility through an alignment-aware check.

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

# 26. Taxi system

A Freeborn character starts with its normal race's taxi knowledge.

Example:

```text
Human Freeborn -> normal Human/Alliance initial taxi nodes
Orc Freeborn   -> normal Orc/Horde initial taxi nodes
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

# 27. Transportation

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

# 28. Battlegrounds

Freeborn can queue for battlegrounds.

When entering a battleground, assign each Freeborn participant temporarily to:

```text
TEAM_ALLIANCE
or
TEAM_HORDE
```

This is **match assignment only**.

Never modify:

```text
race
native team
alignment
reputation
character DB alignment
```

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

Freeborn should be eligible for either battleground team.

Do not automatically place a Human Freeborn on Alliance or Orc Freeborn on Horde.

Prefer normal matchmaking/team balancing.

If a Freeborn premade enters together, all members of that queued group must be assigned to the same temporary battleground team.

Inside the battleground:

```text
same temporary BG team = friendly
opposite temporary BG team = hostile
```

This temporary relationship overrides Freeborn's normal hostility.

On leaving the battleground, normal Freeborn relationships resume.

Audit the battleground code for places that incorrectly call native:

```cpp
GetTeam()
GetTeamId()
TeamIdForRace()
```

when the correct answer during the match should be:

```cpp
GetBgTeamId()
```

Do not add `TEAM_FREEBORN` to battleground arrays.

---

# 29. Arenas

Use the same principle for arenas.

Arena side is temporary match state.

Inside an arena:

```text
same arena side = friendly
opposite arena side = hostile
```

Freeborn alignment is restored automatically as the effective relationship once the match ends.

Do not create a three-sided arena implementation.

---

# 30. Freeborn safe-area PvP and BG/Arena distinction

Capital/sanctuary protection applies to the open world.

Do not let that protection accidentally disable combat inside battleground or arena maps merely because an area entry happens to contain unusual flags.

Explicit instanced battleground/arena match context has priority.

---

# 31. Conversion after creation

Characters may be converted into or out of Freeborn after creation.

Changing alignment does not automatically remove a character from an existing party, raid, or guild; membership persists. Existing group cooperation continues normally, while guild membership alone does not make players friendly. Alignment restrictions apply to new membership changes.

Changing alignment must not change race.

For this architecture:

```text
Native -> Freeborn
Freeborn -> Native
```

Returning to Native means returning to the team naturally associated with the character's current race.

If the server's existing race/faction-change service changes the character's race, `GetNativeTeamId()` naturally changes with the new race.

Alignment changes must not destructively rewrite:

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

This keeps the operation reversible.

---

# 32. GM commands

Implement generic alignment commands.

Preferred:

```text
.alignment status [player]
.alignment set freeborn [player]
.alignment set native [player]
```

Also provide convenience aliases if practical:

```text
.freeborn status
.freeborn set
.freeborn remove
```

Commands should work on online and offline characters where the command framework reasonably supports it.

Use RBAC permissions.

After changing alignment on an online character:

```text
refresh alignment state
refresh client visual indicator
re-evaluate PvP relationship
re-evaluate group/guild validity where appropriate
refresh NPC/quest visibility if needed
```

Do not require relog unless technically unavoidable.

---

# 33. Eluna

Expose alignment to Eluna.

At minimum:

```lua
player:IsFreeborn()
player:GetAlignment()
```

Also support controlled modification:

```lua
player:SetAlignment(alignment)
```

or an equivalent safe API.

Provide named constants rather than magic numbers where the Eluna binding system permits it.

Example:

```lua
PLAYER_ALIGNMENT_NATIVE
PLAYER_ALIGNMENT_FREEBORN
```

Add an alignment-changed hook if practical:

```text
OnPlayerAlignmentChanged(player, oldAlignment, newAlignment)
```

This will make future custom content much easier.

---

# 34. Script/module API

Expose enough of the alignment system that external modules do not need to duplicate core logic.

Prefer a reusable API so modules can ask:

```text
IsFreeborn
GetAlignment
CanManualGroup
CanGuildTogether
ArePlayersHostile
```

rather than importing DB columns directly.

Consider adding a `PlayerScript`/`ScriptMgr` notification when alignment changes.

---

# 35. Playerbots

Playerbots must never be Freeborn.

Do not generate Freeborn playerbots.

Do not allow the bot module to choose Freeborn during character creation.

GM conversion commands should reject converting an active/recognized playerbot to Freeborn where the playerbot API allows reliable detection.

An ordinary Alliance/Horde playerbot still counts as a **player** for relationship purposes.

Therefore:

```text
Freeborn player vs Alliance playerbot = hostile player relationship
Freeborn player vs Horde playerbot    = hostile player relationship
```

Do not accidentally treat playerbots as friendly NPCs.

---

# 36. Full client distinction

Freeborn should have clear visual identification.

Implement support for:

```text
Freeborn character-creation selection state
Freeborn character-select badge
target/portrait indication
nameplate indication
tooltip indication
custom PvP/alignment emblem where appropriate
/who distinction if supported by the customized client
```

Character-select backgrounds remain native for this phase.

Avoid adding new packet structures solely for cosmetic metadata.

For in-world metadata, prefer one of:

```text
verified unused player/update flag
existing custom client side-channel
standard addon-message side-channel
another already-existing custom protocol in this client
```

The server database alignment remains authoritative.

Do not store alignment independently in multiple client-facing flags.

---

# 37. Social/UI distinction versus combat state

A Freeborn indicator means:

```text
"This character is Freeborn"
```

It does not mean:

```text
"This character is currently attackable"
```

A Freeborn player standing in Stormwind may still display a Freeborn alignment emblem while being protected from PvP combat by the safe-area rule.

---

# 38. Native team APIs must retain their meaning

Audit the source tree for all significant uses of:

```text
GetTeam()
GetTeamId()
TeamIdForRace()
GetBgTeamId()
FACTION_MASK_ALLIANCE
FACTION_MASK_HORDE
RACEMASK_ALLIANCE
RACEMASK_HORDE
RequiredRaces
faction-template masks
```

Classify every use as one of:

```text
native race identity
NPC faction interaction
player hostility
social eligibility
quest eligibility
BG/Arena match team
cosmetic/client display
```

Do not replace every `GetTeamId()` with alignment logic.

Many calls genuinely should continue returning native Alliance/Horde.

Only replace team assumptions where the operation actually concerns alignment behavior.

---

# 39. Recommended relationship model

Do not overload one "faction" variable to answer every question.

The game effectively needs these independent concepts:

```text
Native Team
    Alliance/Horde derived from race

Player Alignment
    Native/Freeborn/future alignments

Match Team
    Alliance/Horde during BG/Arena only

Cooperative Context
    party/raid/LFG/BG/Arena

NPC Interaction Policy
    whether faction NPC services are available

PvP Relationship
    friendly/hostile; ordinary Freeborn hostility is inactive where PvP is disabled

PvP Eligibility
    whether combat is currently allowed under normal PvP rules
```

These are intentionally separate.

That separation is the core of this feature.

---

# 40. Freeborn behavior matrix

| Situation                                 | Expected behavior                   |
| ----------------------------------------- | ----------------------------------- |
| Freeborn -> Alliance NPC                  | Usable                              |
| Freeborn -> Horde NPC                     | Usable                              |
| Freeborn -> neutral NPC                   | Normal rules                        |
| Freeborn -> hostile monster               | Normal hostile behavior             |
| Freeborn -> Alliance player               | Hostile where PvP is enabled        |
| Freeborn -> Horde player                  | Hostile where PvP is enabled        |
| Freeborn -> Freeborn player               | Hostile where PvP is enabled        |
| Native player -> Freeborn                 | Hostile under the same PvP rules    |
| Freeborn in capital/sanctuary             | Non-hostile for ordinary PvP        |
| Freeborn manual group with Alliance/Horde | Disallowed                          |
| Freeborn manual group with Freeborn       | Allowed                             |
| Freeborn grouped with Freeborn            | Friendly within group               |
| Freeborn LFG with Alliance/Horde          | Allowed                             |
| Freeborn same LFG group                   | Friendly                            |
| Freeborn guild with Alliance/Horde        | Disallowed                          |
| Freeborn guild with Freeborn              | Allowed                             |
| Freeborn guildmates outside group         | Still hostile                       |
| Freeborn trade with Alliance/Horde        | Allowed                             |
| Freeborn inspect Alliance/Horde           | Allowed                             |
| Freeborn mail Alliance/Horde              | Allowed                             |
| Freeborn auction houses                   | All                                 |
| Freeborn Alliance reputation              | Allowed                             |
| Freeborn Horde reputation                 | Allowed                             |
| Freeborn Alliance quests                  | Allowed                             |
| Freeborn Horde quests                     | Allowed                             |
| Duplicate faction quest                   | Prefer native race team             |
| Freeborn taxi                             | Both sides learnable                |
| Freeborn BG                               | Temporary A/H assignment            |
| Freeborn arena                            | Temporary A/H assignment            |
| Freeborn playerbot                        | Disallowed                          |
| Alliance/Horde playerbot vs Freeborn      | Treat bot as player                 |
| Starting area/data                        | Normal race defaults                |
| Character-select background               | Native default                      |
| Character-select alignment marker         | Freeborn indicator                  |

Player-hostility entries apply only where PvP is enabled. In no-PvP areas, ordinary Freeborn hostility is inactive.

---

# 41. Testing requirements

Create automated tests where the existing test architecture permits them and an explicit manual QA checklist for client-side behavior.

At minimum test:

### Persistence

```text
create Native Human
create Freeborn Human
create Native Orc
create Freeborn Orc

restart worldserver
verify all alignments persist
verify race/native team remains unchanged
```

### Creation defaults

Verify Freeborn and Native versions of the same race receive identical:

```text
spawn
class setup
racials
languages
starting items
cinematic
homebind
starting reputation
native initial taxi nodes
```

except alignment itself.

### NPCs

Test Freeborn Human and Freeborn Horde-native race against:

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

In no-PvP areas, verify ordinary Freeborn hostility is inactive. In PvP-enabled areas, verify hostility is symmetric while attackability still follows normal PvP rules.

in:

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
Freeborn invites Native -> fail
Native guild invites Freeborn -> fail
Freeborn guild invites Freeborn -> success
```

Test online and offline/cache invite paths.

### LFG

Create mixed:

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

Verify hostility returns when Freeborn leaves the LFG group.

### Quests

Test Freeborn access to:

```text
native-side quest
opposite-side quest
class quest
profession quest
reputation-gated quest
paired Alliance/Horde quest
quest with team ConditionMgr condition
```

Verify unrelated requirements remain enforced.

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
native starting taxi mask unchanged
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

Queue several Freeborn characters with mixed native races.

Verify matchmaking can assign them to either temporary side.

Verify:

```text
same BG team friendly
opposing BG team hostile
BG UI works
objectives work
spirit guides work
scoreboard works
graveyards work
leave/rejoin works
alignment unchanged afterward
```

### Arena

Repeat equivalent temporary-team testing.

### Conversion

Test:

```text
Native -> Freeborn
Freeborn -> Native
```

online and offline.

Verify no reputation, quest, item, or taxi data is destroyed. Verify existing group and guild memberships persist through conversion.

### Eluna

Test alignment queries and setter.

### Playerbots

Verify bot generation/conversion cannot create Freeborn bots.

Verify ordinary playerbots remain valid hostile player targets for Freeborn.

---

# 42. Compatibility audit

Before considering implementation complete, search the entire core and installed modules for team assumptions.

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

player->GetTeam() != other->GetTeam()

TeamIdForRace(player->getRace())

RACEMASK_ALLIANCE
RACEMASK_HORDE
```

Do not mechanically replace them.

Determine what the code is actually asking.

---

# 43. Implementation phases

Implement in this order:

### Phase A: Audit

Document the current faction-free/custom-race/client modifications and identify conflicts.

### Phase B: Alignment foundation

Implement enum, DB persistence, Player API, CharacterCache support, and alignment-change notifications.

No gameplay modifications yet.

### Phase C: Creation/client signaling

Implement Freeborn character-creation UI and server decode.

Verify Native vs Freeborn creation produces identical native racial setup.

### Phase D: Visual signaling

Implement character-select/in-world Freeborn distinction while retaining native backgrounds.

### Phase E: NPC/reputation/quest/taxi

Implement dual-faction PvE access.

### Phase F: Player relationship policy

Implement Freeborn player hostility, safe-area protection, trade, communication, manual grouping, and guild rules.

### Phase G: LFG

Implement cooperative override.

### Phase H: Battleground/Arena

Implement temporary Alliance/Horde assignment and match-team relationship overrides.

### Phase I: Eluna/commands/modules

Implement API, commands, Playerbot protection, AutoBalance/module compatibility.

### Phase J: Regression testing

Run the complete matrix and verify Native Alliance/Horde behavior is unchanged.

Do not combine every phase into one giant unreviewable patch.

---

# 44. Required Codex deliverables

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

# 45. Non-goals

Do NOT implement:

```text
TEAM_FREEBORN in AzerothCore's core TeamId enum
three-sided battlegrounds
three-sided arenas
a Freeborn auction house
a Freeborn taxi mask
new racial starting zones
new Freeborn starting reputations
new Freeborn languages
new character-select background
Freeborn playerbots
packet-size changes unless absolutely necessary
```

These are explicitly outside this implementation.

---

# 46. Final acceptance criteria

The feature is complete when a player can:

1. Select **Freeborn** during character creation.
2. Create any playable race as Freeborn.
3. Retain that race's normal starting experience and internal Alliance/Horde team.
4. Be visibly identified as Freeborn during character creation, on character select, and in-game.
5. Freely use Alliance and Horde NPCs and services.
6. Quest for both sides.
7. Gain reputation with both sides simultaneously.
8. Learn and use both sides' taxi systems.
9. Be hostile symmetrically to Alliance, Horde, and ungrouped Freeborn players where PvP is enabled, and non-hostile in no-PvP areas.
10. Still obey normal PvP attackability rules.
11. Be completely protected from hostile player combat in capitals/main cities/sanctuaries.
12. Manually group only with Freeborn.
13. Guild only with Freeborn.
14. Communicate, trade, inspect, mail, and use AHs across alignments.
15. Join mixed-alignment LFG groups and cooperate normally inside them.
16. Enter battlegrounds/arenas using temporary Alliance/Horde match assignment.
17. Return to normal Freeborn hostility after leaving temporary cooperative contexts, unless in a no-PvP area.
18. Be converted between Native and Freeborn without destructive character changes.
19. Be queried/controlled through GM commands and Eluna.
20. Continue to coexist with the server's existing faction-free and custom-race systems.

Most importantly:

**Freeborn must be implemented as a player-alignment layer, not by corrupting AzerothCore's native Alliance/Horde team model.**
