# Esteria Gameplay Expansion
## Expanded Hunter Taming, Animal Companion, and Custom Hearthstone

## 1. Objective

Implement three new gameplay systems for the AzerothCore 3.3.5a server:

1. **Expanded Hunter Taming**
   - Tame Drake
   - Tame Dragonkin
   - Tame Elemental
   - Tame Undead
   - Tame Mechanical

2. **Animal Companion**
   - New Hunter talent.
   - Allows a Hunter to fight with two pets simultaneously.
   - The normal active Hunter pet remains the primary pet.
   - The pet stored in the **first stable slot** becomes the secondary companion.
   - Secondary companion deals **70% normal pet damage**.
   - Relevant Hunter pet spells, talents, buffs, and commands should affect both pets.

3. **Custom Hearthstone**
   - Independent of the normal Hearthstone.
   - Player chooses a custom outdoor-world bind point.
   - Item dialogue provides Bind and Recall options.
   - Recall has a **2-hour cooldown**.
   - Changing the bind point does **not** trigger or reset the cooldown.

The implementation should be module-driven wherever reasonably possible.

Core modifications should be minimal, generic, documented, and limited to functionality that cannot safely be provided through the AzerothCore scripting/module APIs.

---

# 2. General Requirements

## 2.1 Repository Inspection

Before changing anything:

1. Read the repository's `AGENTS.md`.
2. Read relevant documentation under `.agents/`, `docs/`, and module documentation.
3. Inspect existing custom spell, DBC, module, database, and Patch-W workflows.
4. Determine existing custom ID ranges before allocating anything.
5. Search for existing implementations that overlap these systems.
6. Do not overwrite or duplicate existing custom IDs.
7. Do not assume the current upstream AzerothCore layout exactly matches documentation. Verify against the checked-out source.

Record all allocated IDs and touched files in an implementation log.

Do not invent IDs and then hope they are available.

---

# 3. Architecture

Prefer creating or extending an Esteria gameplay module with clearly separated components.

Suggested organization:

```text
modules/
  mod-esteria-gameplay/
    src/
      ExpandedTaming.cpp
      AnimalCompanion.cpp
      CustomHearthstone.cpp
      EsteriaGameplay.h
    data/
      sql/
```

Exact structure may be adapted to the repository's existing module conventions.

Client-side changes should use the project's existing custom client patch workflow.

Server and client DBC data must remain synchronized.

---

# 4. Workstream A: Expanded Hunter Taming

## 4.1 Required Taming Abilities

Implement five distinct Hunter abilities:

```text
Tame Drake
Tame Dragonkin
Tame Elemental
Tame Undead
Tame Mechanical
```

These are separate from vanilla:

```text
Tame Beast
```

Vanilla Tame Beast must continue behaving normally.

The custom abilities should use the normal Hunter taming presentation wherever practical:

- channeled tame
- target validation
- tame failure responses
- creation of a persistent Hunter pet
- pet naming behavior
- stable compatibility
- pet talents
- pet leveling
- happiness
- feeding where applicable
- pet spellbook
- dismissal/revival
- persistence across logout/restart

AzerothCore currently structurally treats a creature as tameable only when it is a Beast, has a family, and has the tameable creature flag. This restriction must be expanded carefully rather than simply removed.

---

# 5. New Pet Families

Create real Hunter pet families for:

```text
Drake
Dragonkin
Elemental
Undead
Mechanical
```

`Drake` is deliberately separate from `Dragonkin`.

This distinction is important.

Example:

```text
Creature Type: Dragonkin
Pet Family: Drake
```

versus:

```text
Creature Type: Dragonkin
Pet Family: Dragonkin
```

This allows creatures such as drakes to have distinct family behavior without treating every Dragonkin pet identically.

Update `CreatureFamily.dbc` using unused custom family IDs verified against the project.

AzerothCore loads `CreatureFamily.dbc` directly, and Hunter pet talent handling uses the family's `petTalentType`, so the new families should integrate into the existing Ferocity/Cunning/Tenacity system rather than creating a fourth pet talent architecture.

Assign each new family an appropriate existing pet talent category after examining current balance and family conventions.

Document the final mapping.

---

# 6. Explicit Tameability

Do **not** automatically make every:

- Dragonkin
- Elemental
- Undead
- Mechanical

creature tameable.

Only explicitly approved creature templates should be tameable.

A creature must still require:

1. an approved pet family;
2. the tameable creature flag;
3. an allowed creature type;
4. the appropriate custom tame spell;
5. normal Hunter ownership/pet eligibility checks.

This prevents bosses, quest NPCs, special event creatures, scripted NPCs, and unintended mobs from becoming pets merely because they share a creature type.

---

# 7. Taming Validation Model

Create a central helper instead of scattering spell IDs throughout the core.

Conceptually:

```cpp
enum class EsteriaTameCategory
{
    Beast,
    Drake,
    Dragonkin,
    Elemental,
    Undead,
    Mechanical
};
```

Implement a policy/helper similar to:

```cpp
bool CanTameCreatureWithSpell(
    Player const* hunter,
    Creature const* creature,
    SpellInfo const* tameSpell);
```

The helper must distinguish between:

### Vanilla Tame Beast

Only normal Beast targets valid under existing rules.

### Tame Drake

Only targets assigned to the custom **Drake** family.

### Tame Dragonkin

Only targets assigned to the custom **Dragonkin** family.

Do not allow this spell to accidentally absorb the Drake family simply because both creatures have Dragonkin creature type.

### Tame Elemental

Only approved Elemental-family targets.

### Tame Undead

Only approved Undead-family targets.

### Tame Mechanical

Only approved Mechanical-family targets.

---

# 8. Minimal Core Change for Taming

AzerothCore's current `CreatureTemplate::IsTameable()` explicitly rejects non-Beasts.

This creates two separate problems:

1. initial taming;
2. loading/swapping an already-tamed custom pet from the stable.

Stable handling also validates stored Hunter pets through `IsTameable()`.

Therefore, merely bypassing the initial tame cast is insufficient.

Implement the smallest maintainable core extension necessary to distinguish:

```text
"structurally valid Hunter pet"
```

from:

```text
"valid target for this particular taming spell"
```

Preferred architecture:

```cpp
CreatureTemplate::IsHunterPetTameable(...)
```

or equivalent generic helper/hook.

It should support:

```text
Beast
Dragonkin
Elemental
Undead
Mechanical
```

provided the creature has a valid Hunter pet family and tameable flag.

Then perform spell-specific category validation separately.

Vanilla `Tame Beast` must still reject non-Beasts.

Do not make `Tame Beast` capable of taming all flagged creatures.

---

# 9. Taming Spell Creation

Create custom `Spell.dbc` entries based on the behavior of vanilla Tame Beast.

Allocate verified unused custom spell IDs.

Required spells:

```text
Tame Drake
Tame Dragonkin
Tame Elemental
Tame Undead
Tame Mechanical
```

Use the standard tame creature effect where practical.

AzerothCore's existing tame effect already:

- creates the `Pet`
- removes the original creature
- levels the new pet appropriately
- registers it as the Hunter's minion
- initializes talents
- saves it as the current pet
- initializes the pet spell UI

so this existing path should be reused rather than replaced with an entirely separate custom pet system.

---

# 10. Custom Family Abilities

Each new family must be capable of having normal Hunter pet family abilities.

At minimum, ensure infrastructure works for assigning family spells through existing pet spell mechanisms.

Do not invent new family spells merely to satisfy implementation unless necessary for testing.

For development testing, it is acceptable to assign an existing harmless/testable pet ability temporarily.

Document that test assignment if used.

Final family abilities can be balanced separately.

---

# 11. Expanded Taming Acceptance Tests

Test at least one creature from every new family.

### Drake

```text
Tame Drake -> succeeds
Tame Dragonkin -> fails on Drake-family target
Tame Beast -> fails
```

### Dragonkin

```text
Tame Dragonkin -> succeeds
Tame Drake -> fails
Tame Beast -> fails
```

### Elemental

```text
Tame Elemental -> succeeds
Tame Beast -> fails
```

### Undead

```text
Tame Undead -> succeeds
Tame Beast -> fails
```

### Mechanical

```text
Tame Mechanical -> succeeds
Tame Beast -> fails
```

For every successful custom pet:

- summon
- dismiss
- revive
- rename
- stable
- unstabilize
- relog
- restart worldserver
- level
- gain/use pet talents
- attack
- follow
- stay
- passive
- defensive
- aggressive
- family abilities

must continue working.

Also verify normal Beast taming has not regressed.

---

# 12. Workstream B: Animal Companion

## 12.1 Feature Definition

Add a new Hunter talent:

# Animal Companion

The talent allows a Hunter to have two combat pets simultaneously.

Architecture:

```text
Hunter
  |
  +-- Primary Pet
  |     Real HUNTER_PET
  |     Existing pet bar
  |     Existing stable CurrentPet
  |
  +-- Animal Companion
        Guardian/minion-style companion
        Derived from first stable slot
        AI controlled
```

Do **not** attempt to implement two independent primary Hunter `Pet` objects.

AzerothCore maintains one primary pet GUID through `SUMMON_SLOT_PET`, making a true dual-primary-pet implementation invasive across pet packets, stable state, ownership, spell handling, and client UI.

---

# 13. Animal Companion Talent

Implement `Animal Companion` as a real Hunter talent visible in the Beast Mastery talent tree.

Requirements:

- one rank
- Beast Mastery tree
- teaches/applies a passive aura
- passive aura is the authoritative check for whether Animal Companion should exist

Inspect the current talent layout before choosing the row/column.

Do not overwrite another talent.

Do not introduce UI overlap.

Use a valid custom Talent/Spell ID from the project's established ranges.

If placing the talent requires client DBC modification, update the appropriate talent/spell DBC data in the client patch.

---

# 14. Companion Source

The secondary pet is always sourced from:

# First Stable Slot

Not:

- current active pet
- first available stable pet
- last-used pet
- random stable pet

Specifically:

```text
PET_SAVE_FIRST_STABLE_SLOT
```

or the checked-out AzerothCore equivalent.

AzerothCore already exposes the first-stable-slot concept in its pet save/stable logic.

If the first stable slot is empty:

```text
No companion is summoned.
```

This is valid behavior and should not produce an error loop.

---

# 15. Companion Lifecycle

The secondary companion should exist when all are true:

```text
Player is a Hunter
Animal Companion talent is active
Primary Hunter pet exists
First stable slot contains a valid living Hunter pet
Player is in a state where pets may exist
```

Spawn/re-evaluate the companion on relevant events including:

- login
- talent learned
- talent removed/reset
- talent spec changed
- primary pet summoned
- primary pet revived
- stable pet configuration changed
- entering world
- map transition where summons need reconstruction

Despawn it when appropriate including:

- Animal Companion talent removed
- talent reset
- primary pet dismissed/stabled
- player logout
- player deletion
- invalid owner state
- first stable slot becomes empty
- companion pet becomes invalid

Do not write the companion back into the stable as a second active pet.

Its authoritative persistence remains the existing first stable slot pet data.

---

# 16. Companion Representation

Instantiate the secondary animal using AzerothCore's guardian/minion/summon infrastructure rather than assigning it to `SUMMON_SLOT_PET`.

It must inherit or derive from the stable pet:

- creature entry
- display/model
- family
- appropriate level
- owner
- faction
- basic pet stat scaling
- applicable passive family abilities

The companion should visually represent the pet in the first stable slot.

Do not mutate the stored stable pet record merely because the companion is currently summoned.

---

# 17. Companion Damage

The Animal Companion deals:

# 70% normal pet damage

This reduction should affect:

- melee auto attacks
- family offensive abilities
- Hunter-triggered companion attacks
- damaging pet spells

Prefer a single centralized modifier/aura rather than manually changing every ability.

Conceptually:

```text
Companion Damage Modifier = 0.70
```

Health is **not** reduced to 70%.

Armor is **not** automatically reduced to 70%.

The requested modifier concerns outgoing damage.

If a generic aura cannot reliably affect every pet damage source, implement a centralized companion damage modifier in the module/core hook.

Avoid per-spell hacks.

---

# 18. Pet Commands

The player only needs the normal primary pet bar.

Do not implement a second standard pet action bar.

Mirror appropriate primary pet commands to Animal Companion:

- Attack
- Follow
- Stay
- Passive
- Defensive
- Aggressive

If the primary pet attacks a player-selected target because of a direct pet command, the companion should also engage that target.

If the Hunter recalls the primary pet, the companion should return as well.

Keep companion movement offset slightly so the two pets do not continuously occupy the exact same point.

Use normal follow-angle/follow-distance mechanics where possible.

---

# 19. Hunter Abilities and Talents

Relevant Hunter abilities must affect **both pets** wherever technically sensible.

Explicitly test and integrate:

```text
Kill Command
Bestial Wrath
Mend Pet
Intimidation
Master's Call
Spirit Bond
pet-related Hunter talents
pet-related Hunter buffs
pet-related passive scaling
```

The intent is:

> Animal Companion should feel like a second Hunter combat pet, not a decorative summon.

However, do not accidentally double player-side effects that are intended to exist only once.

Example:

If a passive causes:

```text
Hunter gains X benefit while a pet is active
```

Animal Companion should satisfy the pet condition where appropriate, but should not automatically grant `2X` unless the underlying mechanic is explicitly pet-instance based.

Pet-side effects should generally apply to both pets.

---

# 20. Kill Command

When Kill Command or the checked-out 3.3.5a equivalent triggers a pet attack:

```text
Primary pet executes normal effect.
Animal Companion executes equivalent effect.
```

Animal Companion's resulting damage remains subject to the 70% modifier.

Do not consume twice the Hunter's resource/cooldown merely because two pets respond.

---

# 21. Bestial Wrath

When Bestial Wrath affects the primary pet, apply the appropriate pet-side Bestial Wrath effect to Animal Companion as well.

Do not create a second independent Hunter cooldown.

One cast controls both.

---

# 22. Mend Pet

Mend Pet should heal both:

```text
Primary Pet
Animal Companion
```

Use the normal heal magnitude/scaling for each pet unless the game's existing mechanics require another interpretation.

Animal Companion's 70% damage modifier must not reduce incoming healing.

---

# 23. Intimidation and Master's Call

Where these abilities instruct or empower the Hunter pet, extend the behavior to Animal Companion.

Avoid:

- duplicate cooldown consumption
- duplicate Hunter resource cost
- unintended double crowd-control duration stacking

If both pets attempt the same non-stackable crowd-control spell, ensure behavior remains deterministic.

---

# 24. Stable Changes

If the Hunter changes the pet located in first stable slot:

1. remove the existing Animal Companion;
2. load the new first-slot pet data;
3. spawn the new companion if all requirements are met.

Do not require relogging.

Do not cache a companion CreatureEntry indefinitely.

The stable remains authoritative.

---

# 25. Animal Companion Safety Cases

Explicitly test:

- first stable slot empty
- first stable pet dead
- primary pet dead
- primary pet dismissed
- Hunter mounts
- Hunter dismounts
- Hunter teleports
- Hunter changes map
- Hunter enters instance
- Hunter dies
- Hunter resurrects
- Hunter logs out
- server restart
- talent reset
- dual spec switch
- stable pet changed
- stable pet removed
- companion dies

There must never be:

- duplicate companions
- orphaned summons
- companion persistence after talent removal
- two primary pet GUIDs
- stable database corruption

---

# 26. Workstream C: Custom Hearthstone

## 26.1 Overview

Create a separate custom item.

Working name may be chosen from existing project naming conventions.

It must **not** replace or modify:

```text
Hearthstone
Innkeeper homebind
normal Hearthstone cooldown
```

The custom Hearthstone stores its own destination.

---

# 27. Item Interaction

Right-clicking the custom Hearthstone opens a dialogue/gossip interface.

Options:

```text
Recall to Bound Location
Bind to Current Location
Cancel
```

AzerothCore's ItemScript interface supports item use and item gossip selection, so this should be implemented primarily through the module.

---

# 28. Bind Location Storage

Create module-owned CharacterDatabase persistence.

Suggested table:

```sql
character_custom_hearth
```

Suggested fields:

```text
guid
map_id
zone_id
area_id
position_x
position_y
position_z
orientation
updated_at
```

Use the project's SQL migration conventions.

`guid` should uniquely identify the character.

Do not store this only in memory.

The destination must survive:

- logout
- crash
- restart
- client restart

---

# 29. Binding Restrictions

The custom Hearthstone may only bind while the player is:

```text
alive
out of combat
not on a transport
not in a battleground
not in an arena
not inside a dungeon
not inside a raid
in the normal outdoor world
```

Outdoor world zones are otherwise allowed.

Cities are allowed.

Enemy territory is allowed unless another existing server rule prevents it.

Do not arbitrarily maintain a hardcoded zone allowlist if map/instance APIs can determine eligibility.

Create a reusable helper:

```cpp
bool CanUseCustomHearth(Player const* player);
```

Use this for both binding and recall.

---

# 30. Recall Restrictions

Recall is also prohibited when:

```text
dead
in combat
on a transport
inside battleground
inside arena
inside dungeon
inside raid
```

This prevents the custom Hearthstone from becoming a special dungeon, raid, or PvP escape mechanic.

---

# 31. Binding Behavior

Selecting:

```text
Bind to Current Location
```

stores:

```text
Map
Zone
Area
X
Y
Z
Orientation
```

for that character.

Binding:

- does not teleport the player
- does not consume the item
- does not trigger cooldown
- does not reset an existing cooldown
- can be performed even while Recall remains on cooldown, provided the player otherwise meets location restrictions

Provide clear confirmation text such as:

```text
Your custom Hearthstone has been bound to this location.
```

---

# 32. Recall Behavior

Selecting:

```text
Recall to Bound Location
```

should:

1. verify a custom location exists;
2. verify player state;
3. verify stored map and coordinates remain valid;
4. begin the custom Hearthstone cast;
5. teleport the player after successful cast;
6. trigger the 2-hour cooldown.

Use a Hearthstone-like cast time rather than an instant teleport unless the existing Esteria design establishes another convention.

Recommended:

```text
10-second cast
```

Movement, damage, or other normal cast interruption should interrupt the recall.

Interrupted recall must not trigger the 2-hour cooldown.

---

# 33. Cooldown

Cooldown:

# 2 hours

Equivalent:

```text
7,200 seconds
7,200,000 milliseconds
```

Use AzerothCore's standard spell cooldown infrastructure rather than a module timer wherever possible.

The core already supports explicit spell/category cooldown handling.

The cooldown must:

- persist across relog
- persist across worldserver restart
- be authoritative server-side
- display correctly to the client where practical
- only begin after a successful recall
- remain unchanged when rebinding

The normal Hearthstone cooldown must remain completely independent.

---

# 34. Invalid Destination Handling

Before teleporting, validate the stored location.

If invalid:

```text
Do not teleport.
Do not start cooldown.
Inform the player.
```

Do not send the player to map `0,0,0`.

Do not fall back silently to the normal homebind.

If a map/zone has become invalid due to future server changes, require the player to bind a new location.

---

# 35. Custom Hearthstone Dialogue

Suggested presentation:

```text
Custom Hearthstone

Bound Location:
<Zone / Area name>

Recall to Bound Location
Bind to Current Location
Cancel
```

If no destination exists:

```text
Bound Location:
Not Set

Bind to Current Location
Cancel
```

Do not offer a functional Recall option until a destination exists.

If retrieving localized area names is straightforward, display them.

Do not make area-name display a blocker for the underlying feature.

---

# 36. Client Work

The client patch should include every client-side database/resource change needed for the features.

Likely client changes include:

```text
CreatureFamily.dbc
Spell.dbc
Talent.dbc
possibly TalentTab-related data
custom item data/icon references as required by project architecture
```

Inspect the existing custom client implementation before deciding exact files.

Do not replace unrelated DBC data.

Merge custom rows into the current project state.

Server-side DBC copies must match client-side data.

---

# 37. SQL Work

Provide proper migration files for:

### World database

As needed for:

- custom item
- spell script bindings
- creature family/tameability assignments
- custom creature template flags
- related spell configuration

### Character database

For:

```text
character_custom_hearth
```

Avoid destructive migrations.

Do not modify unrelated rows.

Every SQL change must be reproducible from migration files.

---

# 38. Configuration

Where appropriate, expose module configuration for values that may reasonably change later.

Suggested:

```ini
Esteria.AnimalCompanion.Enable = 1
Esteria.AnimalCompanion.DamageMultiplier = 0.70

Esteria.CustomHearth.Enable = 1
Esteria.CustomHearth.CooldownSeconds = 7200
```

The requested defaults remain:

```text
Animal Companion damage = 70%
Custom Hearth cooldown = 2 hours
```

Do not make core-required behavior depend on magic constants scattered across source files.

---

# 39. Logging

Add useful debug logging for:

```text
custom tame validation
Animal Companion spawn/despawn
invalid stable companion
custom Hearth bind
custom Hearth recall
custom Hearth invalid destination
```

Do not spam logs every AI update tick.

---

# 40. Implementation Order

Implement in this order.

## Phase 1: Discovery

Document:

- existing custom ID ranges
- existing DBC workflow
- existing Patch workflow
- existing custom Hunter changes
- relevant module hooks
- exact core locations requiring modification

Do not begin by blindly editing upstream code.

## Phase 2: Expanded Taming Core Support

Implement the generic structural tameability change first.

Verify vanilla Beast taming still works.

## Phase 3: New Pet Families

Add:

```text
Drake
Dragonkin
Elemental
Undead
Mechanical
```

Synchronize server/client DBC data.

## Phase 4: Custom Tame Spells

Implement all five spells and spell-specific target validation.

## Phase 5: Custom Pet Testing

Tame, stable, load, relog, restart.

Do not proceed until non-Beast pets survive normal Hunter pet lifecycle operations.

## Phase 6: Animal Companion Talent

Add the Beast Mastery talent and passive.

## Phase 7: Animal Companion Guardian

Implement stable-slot loading, guardian creation, lifecycle, and AI.

## Phase 8: Companion Combat Integration

Implement:

- 70% damage
- commands
- Kill Command
- Bestial Wrath
- Mend Pet
- Intimidation
- Master's Call
- related talents/buffs

## Phase 9: Custom Hearthstone

Implement item, dialogue, persistence, validation, teleport, and cooldown.

## Phase 10: Regression Testing

Perform full Hunter and Hearthstone regression testing.

## Phase 11: Packaging

Build the server/module and create the updated client patch using the repository's existing packaging workflow.

---

# 41. Required Regression Tests

Existing systems must still work.

Test:

### Hunter

```text
normal Tame Beast
normal Beast pet
exotic Beast pet
stable
stable swapping
Call Pet
Dismiss Pet
Revive Pet
Mend Pet
pet talents
dual spec
talent reset
mounting
teleports
logout/login
```

### Custom Families

```text
Drake
Dragonkin
Elemental
Undead
Mechanical
```

### Animal Companion

```text
with first stable slot
without first stable slot
different stable pet
dead stable pet
talent active
talent inactive
70% damage verification
commands
Hunter pet spells
logout/login
server restart
```

### Custom Hearthstone

```text
bind outdoors
rebind outdoors
recall
2-hour cooldown
rebind during cooldown
relog during cooldown
server restart during cooldown
normal Hearthstone remains independent
combat rejection
dead rejection
transport rejection
BG rejection
arena rejection
dungeon rejection
raid rejection
invalid stored destination
```

---

# 42. Damage Verification

Do not simply eyeball the Animal Companion's damage.

Create a controlled test.

For example:

```text
Primary pet average attack = X
Equivalent companion baseline = approximately 0.70X
```

Account for RNG, armor, crits, and ability differences.

Use enough attacks to establish that the multiplier is actually being applied.

Test at least:

- auto attack
- physical pet ability
- magical pet ability if available
- Kill Command response

---

# 43. No Client Protocol Rewrite

This implementation specifically does **not** require:

- two standard pet action bars
- two primary `Pet` GUIDs
- custom pet packets
- rewriting the 3.3.5 pet UI protocol

Animal Companion is intentionally implemented as:

```text
1 real Hunter Pet
+
1 server-managed companion
```

This constraint is intentional.

Do not expand scope into a true dual-primary-pet client architecture.

---

# 44. Non-Goals

Do not implement unless required for these features:

- third pet
- multiple Animal Companion stable slots
- custom companion UI
- separate companion action bar
- companion talent window
- entirely new pet talent trees
- mass-tame permission for every Dragonkin/Undead/etc.
- replacing vanilla Tame Beast
- replacing vanilla Hearthstone
- changing inn homebind behavior
- custom Hearth locations inside instances
- cooldown reduction mechanics for the custom Hearthstone

---

# 45. Core Modification Policy

If core modification is required:

1. keep it small;
2. make it generic;
3. document why a module hook was insufficient;
4. avoid Esteria-specific spell IDs directly in generic core where possible;
5. expose an appropriate script hook/helper if that keeps custom policy in the module;
6. preserve upstream behavior when the module is disabled.

Ideal separation:

```text
AzerothCore:
Provides generic capability/hook.

Esteria module:
Decides which custom tame spell accepts which custom family.
```

Avoid:

```cpp
if (spellId == 900123)
```

inside unrelated upstream systems if it can reasonably live inside the module.

---

# 46. Implementation Documentation

Create an implementation record containing:

```text
Custom spell IDs
Custom talent ID
Custom item ID
Custom CreatureFamily IDs
Creature templates enabled for testing
SQL migration filenames
DBC files modified
Core files modified
Module files created
Client patch files changed
Build command
Package command
Test characters used
Testing results
Known limitations
```

If the repository uses `.agents/plans/`, create an appropriate task directory there.

Otherwise place the implementation notes under `docs/`.

---

# 47. Build Requirements

After implementation:

1. compile the relevant module/server;
2. resolve compiler warnings introduced by this work;
3. package the client changes;
4. verify server/client DBC synchronization;
5. verify SQL migrations apply cleanly;
6. launch/test according to repository instructions where permitted.

Do not report the feature complete merely because the project compiles.

Compilation is only the first acceptance gate.

---

# 48. Definition of Done

This task is complete only when all of the following are true.

### Expanded Taming

- [ ] Tame Drake exists.
- [ ] Tame Dragonkin exists.
- [ ] Tame Elemental exists.
- [ ] Tame Undead exists.
- [ ] Tame Mechanical exists.
- [ ] Drake is a separate family from Dragonkin.
- [ ] Approved non-Beast creatures can become persistent Hunter pets.
- [ ] Vanilla Tame Beast remains Beast-only.
- [ ] New pets survive stable/relog/restart.
- [ ] New pets support normal Hunter pet mechanics.

### Animal Companion

- [ ] Animal Companion exists as a Hunter talent.
- [ ] Primary pet remains the only true active Hunter Pet.
- [ ] First stable slot supplies companion.
- [ ] Companion spawns/despawns correctly.
- [ ] Companion deals 70% damage.
- [ ] Normal commands affect both pets.
- [ ] Kill Command affects both.
- [ ] Bestial Wrath affects both.
- [ ] Mend Pet affects both.
- [ ] Intimidation integration works.
- [ ] Master's Call integration works.
- [ ] Relevant pet talents/buffs work.
- [ ] No stable corruption occurs.
- [ ] No duplicate companion occurs after relog/map changes.

### Custom Hearthstone

- [ ] Custom item exists.
- [ ] Right-click opens dialogue.
- [ ] Player can bind an eligible outdoor location.
- [ ] Player can recall to that location.
- [ ] Recall cooldown is exactly 2 hours.
- [ ] Rebinding does not trigger/reset cooldown.
- [ ] Destination persists.
- [ ] Cooldown persists.
- [ ] Combat is rejected.
- [ ] Death is rejected.
- [ ] Transport use is rejected.
- [ ] BG/arena use is rejected.
- [ ] Dungeon/raid use is rejected.
- [ ] Normal Hearthstone remains unaffected.

---

# 49. Final Deliverables

At completion provide:

1. all source changes;
2. module changes;
3. core patch, if required;
4. world SQL migrations;
5. character SQL migrations;
6. updated server-side DBC files;
7. updated client patch/package;
8. successful build output;
9. implementation notes;
10. tested custom IDs;
11. list of creatures used for tame testing;
12. concise test report identifying what was tested in-game versus only statically verified.

Do not claim successful gameplay validation for anything that was only inspected in source or SQL.

Do not leave generated IDs, TODO placeholders, or guessed values in the final implementation.