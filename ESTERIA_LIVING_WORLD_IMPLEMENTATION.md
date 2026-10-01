# Esteria Living World
## AzerothCore 3.3.5a Implementation Specification

**Project:** Esteria  
**Platform:** AzerothCore, World of Warcraft 3.3.5a  
**Recommended module:** `mod-esteria-living-world`  
**Status:** Design / implementation specification  
**Primary goal:** Transform Esteria from a mostly static MMORPG world into a persistent simulation where players, NPCs, towns, businesses, property, crime, trade, relationships, and government affect one another over time.

---

# 1. Design Philosophy

The systems in this document should not be implemented as isolated features.

The goal is to create a shared simulation where:

- Players can own homes, shops, farms, and guild property.
- NPCs have identities, homes, jobs, schedules, families, and memories.
- Settlements have changing prosperity, safety, food, morale, population, and wealth.
- Businesses depend on local population, supply, prices, employees, and prosperity.
- Caravans physically move goods between settlements.
- Crime affects local safety and guard activity.
- Citizenship affects access to civic privileges.
- Government gives high-standing players limited influence over a settlement.
- Player actions can create stories that become rumors and newspaper articles.
- Marriage, property, fame, morality, citizenship, business ownership, and social class become alternate forms of progression.

The most important rule is:

> Every major system should either consume state from another system, change state in another system, or both.

Example:

1. Wolves become unusually numerous outside Lakeshire.
2. Livestock losses reduce the settlement's Food value.
3. Food prices rise.
4. A bounty is generated for wolves.
5. The innkeeper begins spreading a rumor about livestock attacks.
6. A player completes the bounty.
7. Safety and Food recover.
8. The player gains Lakeshire civic standing and Renown.
9. The weekly newspaper reports that the livestock problem was resolved.
10. Shops selling food see their margins return to normal.

That loop is what makes the world feel alive.

---

# 2. AzerothCore Architecture

AzerothCore already provides a modular scripting system with hooks for players, creatures, gameobjects, world updates, maps, guilds, weather, game events, mail, loot, auctions, and other systems.

The preferred implementation is one large Esteria module with several internal managers rather than many disconnected modules.

Recommended layout:

```text
modules/
└── mod-esteria-living-world/
    ├── CMakeLists.txt
    ├── conf/
    │   └── LivingWorld.conf.dist
    ├── src/
    │   ├── LivingWorldLoader.cpp
    │   ├── LivingWorldDefines.h
    │   ├── LivingWorldConfig.h
    │   ├── LivingWorldConfig.cpp
    │   │
    │   ├── Core/
    │   │   ├── LivingWorldMgr.h
    │   │   ├── LivingWorldMgr.cpp
    │   │   ├── EventBus.h
    │   │   ├── EventBus.cpp
    │   │   ├── Scheduler.h
    │   │   └── Scheduler.cpp
    │   │
    │   ├── Settlement/
    │   │   ├── SettlementMgr.h
    │   │   ├── SettlementMgr.cpp
    │   │   ├── CitizenshipMgr.h
    │   │   ├── CitizenshipMgr.cpp
    │   │   ├── GovernmentMgr.h
    │   │   └── GovernmentMgr.cpp
    │   │
    │   ├── Property/
    │   │   ├── PropertyMgr.h
    │   │   ├── PropertyMgr.cpp
    │   │   ├── HousingMgr.h
    │   │   ├── HousingMgr.cpp
    │   │   ├── BusinessMgr.h
    │   │   ├── BusinessMgr.cpp
    │   │   ├── EmployeeMgr.h
    │   │   └── EmployeeMgr.cpp
    │   │
    │   ├── Society/
    │   │   ├── MarriageMgr.h
    │   │   ├── MarriageMgr.cpp
    │   │   ├── RenownMgr.h
    │   │   ├── RenownMgr.cpp
    │   │   ├── MoralityMgr.h
    │   │   ├── MoralityMgr.cpp
    │   │   ├── RelationshipMgr.h
    │   │   └── RelationshipMgr.cpp
    │   │
    │   ├── NPC/
    │   │   ├── ProceduralNpcMgr.h
    │   │   ├── ProceduralNpcMgr.cpp
    │   │   ├── ScheduleMgr.h
    │   │   ├── ScheduleMgr.cpp
    │   │   ├── HouseholdMgr.h
    │   │   └── HouseholdMgr.cpp
    │   │
    │   ├── Economy/
    │   │   ├── EconomyMgr.h
    │   │   ├── EconomyMgr.cpp
    │   │   ├── CaravanMgr.h
    │   │   ├── CaravanMgr.cpp
    │   │   ├── AgricultureMgr.h
    │   │   ├── AgricultureMgr.cpp
    │   │   ├── FishingEconomyMgr.h
    │   │   └── FishingEconomyMgr.cpp
    │   │
    │   ├── Crime/
    │   │   ├── CrimeMgr.h
    │   │   ├── CrimeMgr.cpp
    │   │   ├── TheftMgr.h
    │   │   ├── TheftMgr.cpp
    │   │   ├── BountyMgr.h
    │   │   └── BountyMgr.cpp
    │   │
    │   ├── World/
    │   │   ├── IncidentMgr.h
    │   │   ├── IncidentMgr.cpp
    │   │   ├── EcologyMgr.h
    │   │   ├── EcologyMgr.cpp
    │   │   ├── RumorMgr.h
    │   │   ├── RumorMgr.cpp
    │   │   ├── ChronicleMgr.h
    │   │   └── ChronicleMgr.cpp
    │   │
    │   └── Scripts/
    │       ├── LivingWorldPlayerScript.cpp
    │       ├── LivingWorldCreatureScript.cpp
    │       ├── LivingWorldGameObjectScript.cpp
    │       ├── LivingWorldWorldScript.cpp
    │       ├── LivingWorldGuildScript.cpp
    │       ├── LivingWorldWeatherScript.cpp
    │       └── LivingWorldCommands.cpp
    │
    └── data/
        └── sql/
            ├── db_world/
            └── db_characters/
```

Do not put simulation logic directly into script hooks.

Hooks should call managers.

Example:

```cpp
void LivingWorldPlayerScript::OnPlayerCompleteQuest(Player* player, Quest const* quest)
{
    sLivingWorld->OnQuestCompleted(player, quest);
}
```

The manager decides whether the action affects:

- Renown
- citizenship
- NPC relationships
- settlement prosperity
- morality
- crime
- business state
- newspaper history

This prevents duplicate logic.

---

# 3. Static Data vs Persistent Simulation State

Use two categories of data.

## 3.1 World Database

Use `acore_world` for definitions that describe what *can exist*.

Examples:

- settlements
- property definitions
- business types
- NPC archetypes
- possible names
- occupations
- schedules
- caravan routes
- commodity definitions
- crop definitions
- incident templates
- government office definitions
- civic reward thresholds
- social title requirements
- rumor templates

These values are configuration.

They should change mainly through SQL updates.

## 3.2 Characters Database

Use `acore_characters` for state that changes while the server runs.

Examples:

- who owns a property
- who rents a property
- business balance
- current employees
- marriage records
- player Renown
- player morality
- citizenship
- wanted levels
- active government terms
- current settlement prosperity
- current regional supply
- persistent procedural NPCs
- NPC relationships
- active caravans
- active incidents
- crop growth
- ecological population indexes
- newspaper event history

Although some of these values are world state rather than character state, `acore_characters` is the safer initial home because it is the database that already contains persistent gameplay state.

A future version can move world simulation state into a dedicated module database if desired.

---

# 4. Core Living World Manager

Create a singleton-style service:

```cpp
LivingWorldMgr* sLivingWorld;
```

It owns or exposes subsystem managers:

```cpp
sLivingWorld->Settlements();
sLivingWorld->Properties();
sLivingWorld->Businesses();
sLivingWorld->NPCs();
sLivingWorld->Economy();
sLivingWorld->Crime();
sLivingWorld->Relationships();
sLivingWorld->Incidents();
sLivingWorld->Government();
sLivingWorld->Chronicle();
```

## 4.1 Initialization

At world startup:

1. Load configuration.
2. Load settlement definitions.
3. Load property definitions.
4. Load economy commodity definitions.
5. Load procedural NPC definitions and persistent instances.
6. Load active businesses.
7. Load current settlement simulation state.
8. Load active caravans.
9. Load current incidents.
10. Load government terms.
11. Reconcile expired timers.
12. Resume simulation.

## 4.2 Tick Rates

Do not run the entire simulation every world update.

Recommended frequencies:

| System | Frequency |
|---|---:|
| nearby spouse check | 2 to 5 seconds |
| active NPC movement/schedule check | 10 to 30 seconds |
| incidents | 1 minute |
| caravans | normal CreatureAI movement |
| settlement aggregation | 5 minutes |
| supply/demand update | 15 minutes |
| ecology update | 30 minutes |
| farm growth calculation | timestamp based |
| business income simulation | hourly |
| rent | daily or weekly |
| government | hourly validation |
| newspaper | weekly |
| database snapshot | 5 to 15 minutes |

Use timestamps whenever possible.

A crop does not need to "grow" every minute.

Store:

```text
planted_at
crop_type
growth_modifier
```

When the plot is queried, calculate the growth stage from elapsed time.

---

# 5. Event Bus

Create a lightweight internal event system.

Example event types:

```cpp
enum class LivingWorldEventType
{
    PlayerQuestCompleted,
    PlayerKilledCreature,
    PlayerBoughtProperty,
    PlayerSoldProperty,
    PlayerMovedResidence,
    MarriageCreated,
    MarriageEnded,
    ShopOpened,
    ShopClosed,
    BusinessPurchase,
    EmployeeHired,
    EmployeeFired,
    RentCollected,
    TenantEvicted,
    CrimeCommitted,
    TheftSucceeded,
    TheftFailed,
    WantedLevelChanged,
    BountyCompleted,
    CaravanDeparted,
    CaravanArrived,
    CaravanDestroyed,
    IncidentStarted,
    IncidentCompleted,
    IncidentFailed,
    SettlementTierChanged,
    GovernmentOfficeChanged,
    CitizenJoined,
    CitizenLeft,
    NpcHelped,
    NpcRobbed,
    RareEmployeeRecruited,
    GuildPropertyPurchased
};
```

Each event can include:

```cpp
struct LivingWorldEvent
{
    LivingWorldEventType Type;
    ObjectGuid PlayerGuid;
    ObjectGuid SecondaryPlayerGuid;
    uint32 SettlementId;
    uint32 NpcId;
    uint32 PropertyId;
    uint32 BusinessId;
    int64 Amount;
    std::string Metadata;
};
```

Systems subscribe to relevant events.

Example:

`CaravanDestroyed`

causes:

- destination Supply decreases
- Safety decreases
- Crime increases
- a bounty can be generated
- rumors are generated
- a newspaper event is logged

This shared event bus is the backbone of the Living World.

---

# 6. Settlements

Every supported town becomes a simulation object.

Example settlements:

```text
Stormwind
Goldshire
Lakeshire
Darkshire
Westfall / Sentinel Hill
Ironforge
Kharanos
Booty Bay
Ratchet
Orgrimmar
Crossroads
Thunder Bluff
Silvermoon
Undercity
Shattrath
Dalaran
```

Start small.

Do not attempt to simulate every WoW settlement in version 1.

Recommended initial test settlements:

- Goldshire
- Lakeshire
- Darkshire
- Booty Bay

These provide several different environments while remaining manageable.

## 6.1 Settlement Definition

Create:

```sql
lw_settlement
```

Suggested fields:

```text
id
name
map_id
zone_id
area_id
faction_mode
center_x
center_y
center_z
radius
base_population
base_wealth
base_food
base_safety
base_morale
base_trade
government_enabled
property_enabled
crime_enabled
economy_enabled
```

## 6.2 Runtime State

Create:

```sql
lw_settlement_state
```

Fields:

```text
settlement_id
population
wealth
food
safety
morale
trade
crime
prosperity
last_update
prosperity_tier
```

Recommended internal range:

```text
0 to 1000
```

Do not expose raw numbers directly to players initially.

Expose tiers:

```text
Destitute
Struggling
Stable
Prosperous
Thriving
Renowned
```

Use hysteresis.

Example:

Do not instantly switch between `Stable` and `Prosperous` when a value crosses one point.

Require the value to move significantly into the next range.

This prevents visible systems from constantly changing.

---

# 7. Dynamic Town Prosperity

Prosperity should be calculated from multiple settlement values.

Example formula:

```text
Prosperity =
    Wealth * 0.30
  + Food * 0.20
  + Safety * 0.20
  + Morale * 0.15
  + Trade * 0.10
  + PopulationHealth * 0.05
```

Weights should be configurable.

## Positive events

Examples:

- successful caravan arrival
- players buying local goods
- player-owned shops succeeding
- completing local bounties
- town donations
- successful public works
- festivals
- high tenant occupancy
- farms producing food
- guild investments

## Negative events

Examples:

- caravan loss
- high crime
- failed incidents
- excessive landlord exploitation
- food shortages
- shop closures
- bandit activity
- ecological problems
- farm failure

## Visible effects

Tie prosperity tiers to actual world changes.

Examples:

### Low prosperity

- fewer decorative NPCs
- fewer market stalls
- beggar NPCs
- boarded windows
- fewer guards
- damaged props
- reduced vendor inventory
- higher criminal incident chance

### High prosperity

- additional guards
- additional merchants
- decorative banners
- musicians
- richer market stalls
- fountains or flowers
- special vendors
- construction projects
- improved street activity

Prefer spawn groups.

Each tier can activate or deactivate predefined creature and gameobject groups.

Do not dynamically modify thousands of individual spawns every tick.

---

# 8. Property System

Properties represent physical buildings or parcels in the existing world.

Types:

```text
Residence
Commercial
Farm
Inn
Guild Hall
Warehouse
Estate
Special
```

Create:

```sql
lw_property_template
```

Fields:

```text
property_id
settlement_id
name
property_type
map_id
entrance_x
entrance_y
entrance_z
entrance_o
interior_mode
base_price
weekly_tax
max_tenants
max_employees
prestige
required_civic_standing
required_renown
flags
```

Ownership:

```sql
lw_property_owner
```

Fields:

```text
property_id
owner_type
owner_guid
purchased_at
purchase_price
residence_enabled
rent_policy
condition_value
last_tax_payment
```

`owner_type`:

```text
PLAYER
GUILD
SYSTEM
```

---

# 9. Existing Buildings and Private Ownership

Existing WoW buildings create an important technical limitation.

A normal world building exists in one shared map.

If Player A owns the Goldshire cottage, the physical cottage is still visible to Player B.

Three implementation modes should be supported.

## Mode A: Public Physical Property

The building remains in the public world.

Ownership controls:

- furniture interactions
- storage
- bed bonuses
- rent
- property management
- hearth location
- shop controls
- NPC tenant behavior

Other players can physically walk inside.

This is the simplest mode.

## Mode B: Door to Private Interior

The existing exterior remains public.

Interacting with the property door sends authorized players into a private interior.

The private interior can be:

- an instance map
- a custom housing map
- a reusable interior map with separate instance IDs

This provides true privacy.

It is the preferred long-term design for residences.

## Mode C: Shared Interior With Permissioned Objects

The physical interior remains shared but:

- chests only open for authorized players
- beds only work for residents
- furniture can only be changed by owners
- shop management only works for owners
- visitors have no ownership powers

## Do Not Use One Phase Bit Per Player

3.3.5a phasing is not an appropriate scalable solution for thousands of private homes.

Use property permissions or actual instancing instead.

---

# 10. Purchasing a Home

Players interact with:

- a deed sign
- a real-estate broker
- the front door
- a town property clerk

Gossip menu:

```text
Property: Rosewood Cottage
Price: 1,250 Gold
Weekly Tax: 8 Gold
Current Occupant: Elric and Anna Hale
Condition: Good

[Purchase Property]
[Inspect Property]
[View Local Property Rules]
```

On purchase:

1. Validate citizenship if required.
2. Validate civic standing.
3. Validate ownership limits.
4. Validate gold.
5. Deduct purchase price.
6. Create ownership record.
7. Log transaction.
8. Award Renown.
9. Modify settlement Wealth.
10. Generate newspaper event if valuable enough.
11. Assign existing NPC occupants as tenants unless the player chooses owner occupancy.

---

# 11. Existing NPC Pays Rent vs Player Moves In

When a purchased property already contains a procedural NPC household, the owner gets a choice.

```text
Keep Current Tenants
Move Into Property
```

## Keep Current Tenants

The household stays.

The player becomes landlord.

The NPC family pays rent.

Their happiness depends on:

- rent
- home condition
- furniture quality
- settlement Safety
- settlement Food
- settlement Prosperity
- relationship with landlord

## Move Into Property

The NPC household receives a notice period.

Example:

```text
24 real-world hours
```

After the notice:

- the household searches for another residence
- the property becomes owner occupied
- the player can set it as primary residence

Evicting happy tenants without cause can affect:

- Landlord Morality
- Good/Evil alignment
- local NPC reputation

Do not instantly delete tenants.

That destroys the illusion of a living town.

---

# 12. Renting Property to NPCs

Tenant simulation should be persistent.

Create:

```sql
lw_property_tenant
```

Fields:

```text
property_id
household_id
rent_amount
lease_started
next_rent_due
happiness
arrears
notice_state
last_payment
```

## Tenant Happiness

Suggested formula:

```text
Base Happiness
+ property condition
+ furnishing quality
+ neighborhood safety
+ settlement prosperity
+ landlord relationship
- rent burden
- unresolved maintenance requests
```

## Rent Payment

At due time:

```text
effective_rent = base_rent * rent_policy_modifier
```

Possible outcomes:

- paid in full
- partial payment
- missed payment
- tenant leaves
- tenant requests assistance
- tenant relationship changes

Tenant income should be simulated from occupation and town economy.

A poor farmer should not magically pay the same rent as a wealthy merchant.

---

# 13. Landlord Morality

Create a separate Landlord Morality score.

Recommended range:

```text
-1000 to +1000
```

Example tiers:

```text
-1000 to -751  Slumlord
-750  to -251  Exploitative
-250  to +250  Ordinary
+251  to +750  Fair
+751  to +1000 Benevolent
```

Actions:

### Positive

- low rent
- forgiving missed rent
- repairing homes quickly
- improving property condition
- helping tenants
- funding neighborhood projects

### Negative

- excessive rent
- repeated evictions
- leaving property in poor condition
- exploiting shortages to raise rent
- intimidation
- illegal eviction

Landlord Morality should influence global Good/Evil, but should remain a separate statistic.

This allows someone to be:

- generally heroic but a terrible landlord
- morally questionable but surprisingly fair to tenants

That creates more interesting characters.

---

# 14. Marriage

Marriage is a character-to-character persistent relationship.

Create:

```sql
lw_marriage
```

Fields:

```text
marriage_id
player1_guid
player2_guid
created_at
ceremony_settlement_id
ring1_item_guid
ring2_item_guid
shared_residence_property_id
status
```

Statuses:

```text
ENGAGED
MARRIED
SEPARATED
DIVORCED
```

## Ceremony

Use a marriage officiant NPC.

Flow:

1. Player A proposes to Player B.
2. Player B accepts.
3. Both choose ceremony.
4. Optional fee.
5. Rings are created.
6. The two actual ring item GUIDs are stored in `lw_marriage`.
7. Marriage becomes active.
8. Server announcement can be optional.
9. Newspaper event is generated.
10. Shared property permissions are updated.

The marriage should be between characters, not automatically every character on the account.

---

# 15. Wedding Ring Bonus

The bonus only activates when:

- both characters are married to each other
- both are online
- both have their assigned wedding rings equipped
- they are within the configured range
- neither marriage is inactive

Suggested range:

```text
100 yards
```

Recommended buffs:

- bonus XP from kills
- bonus quest XP
- scaling primary stats
- small reputation bonus
- small Renown bonus

Example:

```text
Bond of Matrimony
+10% experience gained
+3% primary stats
+5% Renown earned
```

The stat bonus can scale with level.

Avoid enormous combat scaling.

Marriage should be useful without becoming mandatory for every competitive player.

## Implementation

Use:

- `PlayerScript::OnPlayerGiveXP`
- quest XP hooks
- periodic player proximity check
- a custom aura spell for visible stat bonuses

Do not recalculate every frame.

Check spouse eligibility every few seconds.

---

# 16. Shared Marriage Features

Marriage can additionally grant:

- shared home permissions
- spouse access list
- shared residence hearth option
- spouse property visitor rights
- joint household name
- anniversary tracking
- marriage achievements
- special housing decorations
- spouse recall with a long cooldown
- shared household Renown

Do not automatically merge character gold.

Shared money creates support and exploit problems.

If a joint account is desired later, implement an explicit Household Treasury.

---

# 17. Renown / Fame

Renown represents how well-known a character is across Esteria.

Create:

```sql
lw_player_renown
```

Fields:

```text
guid
renown
lifetime_renown
renown_tier
last_updated
```

Recommended values:

```text
Unknown
Recognized
Known
Notable
Famous
Celebrated
Legendary
```

Renown can be earned from:

- quests
- raids
- rare kills
- exploration
- owning successful businesses
- solving incidents
- government service
- bounty completion
- town projects
- marriages and social events
- major donations
- defending caravans
- major guild achievements

Use diminishing returns.

Farming the same low-level action should rapidly become worthless.

---

# 18. Local Fame vs Global Fame

Separate:

```text
Global Renown
Settlement Civic Standing
NPC Relationship
```

These are not the same thing.

A player can be:

- globally famous
- hated in Booty Bay
- beloved in Darkshire
- unknown to one specific NPC

This distinction is important.

---

# 19. Good / Evil Alignment

Create:

```sql
lw_player_morality
```

Recommended range:

```text
-1000 Evil
0 Neutral
+1000 Good
```

Do not calculate morality solely from quests.

Living World actions should contribute.

## Good actions

Examples:

- helping stranded NPCs
- protecting caravans
- donating food
- forgiving rent
- saving civilians
- completing lawful bounties
- returning stolen items
- funding town improvements

## Evil actions

Examples:

- stealing
- robbing businesses
- extortion
- unjust eviction
- illegal contracts
- attacking civilians
- sabotaging caravans
- fencing stolen goods

Alignment should mostly affect:

- NPC reactions
- rumors
- titles
- cosmetic rewards
- access to certain contracts
- certain merchants
- social dialogue
- newspaper descriptions

Avoid giving one morality direction an obviously superior combat advantage.

---

# 20. Local Citizenship

Players can declare one primary home settlement.

Create:

```sql
lw_citizenship
```

Fields:

```text
guid
settlement_id
joined_at
civic_standing
lifetime_civic_points
residence_property_id
last_changed
```

Possible ranks:

```text
Visitor
Resident
Citizen
Established Citizen
Respected Citizen
Patron
Civic Leader
```

## Gaining Standing

Examples:

- living in settlement
- owning property
- spending money locally
- completing local jobs
- completing local bounties
- helping local NPCs
- protecting caravans
- donating to public works
- running a successful local shop
- government service

## Losing Standing

Examples:

- local crime
- unpaid civic taxes
- exploiting residents
- sabotaging the settlement
- abandoning office responsibilities

## Rewards

Higher standing can unlock:

- property purchase
- better property
- local titles
- special merchants
- government candidacy
- civic contracts
- town services
- reduced local fees
- access to warehouses
- festival participation
- exclusive housing decorations

Changing citizenship should have a cooldown.

Example:

```text
30 days
```

This prevents players from instantly changing cities for rewards.

---

# 21. Player Government

Government should provide influence, not GM powers.

Possible offices:

```text
Mayor
Sheriff
Treasurer
Magistrate
Trade Master
Steward
Harbormaster
```

Create:

```sql
lw_government_office
lw_government_term
```

## Office Definition

Fields:

```text
office_id
settlement_id
office_type
min_civic_standing
min_renown
term_length
cooldown_after_term
powers_mask
```

## Term

Fields:

```text
office_id
player_guid
term_started
term_ends
status
```

## Initial Selection Model

For version 1, use:

- eligibility requirements
- application
- system selection based on civic standing and recent contribution

Later, add player elections.

This keeps the first implementation manageable.

## Mayor

Can choose between predefined public projects.

Example:

```text
Fund Market Expansion
Repair Roads
Increase Guard Funding
Sponsor Harvest Festival
Subsidize Food
```

## Sheriff

Can:

- prioritize bounty categories
- request additional patrols
- fund temporary guard presence

## Treasurer

Can allocate a limited civic budget among predefined categories.

## Trade Master

Can:

- subsidize one commodity category
- sponsor a caravan route
- temporarily reduce market fees

## Magistrate

Can:

- choose between predefined penalties
- pardon a limited number of low-level crimes
- post high-profile bounties

Every power must:

- use predefined options
- have cooldowns
- have budget limits
- be logged
- never allow direct arbitrary gold creation
- never allow arbitrary punishment of players

---

# 22. Procedural Named NPCs

Procedural NPCs should be created once and persist.

They are not random disposable spawns.

Each NPC receives:

- first name
- surname
- sex
- race
- age category
- occupation
- personality traits
- settlement
- household
- residence
- workplace
- schedule
- wealth class
- relationship links
- personal relationship values with players

Create:

```sql
lw_npc
```

Fields:

```text
npc_id
creature_entry
spawn_guid
first_name
last_name
race
gender
age_group
occupation_id
settlement_id
household_id
home_property_id
work_property_id
wealth
personality_mask
morality
alive
created_at
```

---

# 23. Procedural NPC Naming Limitation

The stock 3.3.5a creature query returns a creature's name from its creature template entry.

That means multiple spawned creatures using one creature entry normally share one client-visible name.

There are two valid implementations.

## Option A: Reserved Unique Creature Entry Pool

Reserve a range such as:

```text
900000 to 909999
```

Each persistent procedural NPC gets a unique creature template entry.

The entry stores:

```text
Mara Whitcombe
Baker
```

Advantages:

- module-friendly
- minimal core changes
- normal nameplates work

Disadvantages:

- many creature template rows
- template changes need careful loading
- large NPC populations consume entry IDs

Recommended for the first production version.

## Option B: Small Core Extension for Dynamic Creature Query Names

Add a hook around creature query response generation.

The module supplies:

```text
name
subname
```

based on the actual spawn GUID.

Advantages:

- one archetype entry can represent many named NPCs
- cleaner data model
- easier large populations

Disadvantages:

- requires a small AzerothCore core patch or new upstream-style hook

Recommended long-term if Esteria intends to support thousands of procedural NPCs.

---

# 24. NPC Archetypes

Do not generate every NPC completely randomly.

Use controlled archetypes.

Examples:

```text
Baker
Farmer
Blacksmith
Stablehand
Guard
Innkeeper
Fisher
Merchant
Dockworker
Hunter
Carpenter
Tailor
Miner
Jeweler
Teacher
Child
Retired Soldier
Noble
Beggar
Smuggler
```

Each archetype defines:

- possible models
- clothing
- work hours
- income
- social class
- possible home types
- personality weights
- possible incidents
- possible relationships

---

# 25. NPC Personality

Use a bitmask or small trait list.

Examples:

```text
Friendly
Shy
Greedy
Generous
Dishonest
Brave
Cowardly
Lazy
Hardworking
Religious
Suspicious
Romantic
Proud
Gossipy
Loyal
Ambitious
```

Do not attempt a full personality AI.

Traits modify probabilities.

Example:

A Gossipy NPC:

- spreads rumors more often

A Greedy merchant:

- prefers higher margins

A Brave civilian:

- is more likely to assist during an incident

A Suspicious NPC:

- detects theft more easily

Simple modifiers create believable differences.

---

# 26. NPC Families and Households

Create:

```sql
lw_household
lw_household_member
```

Household fields:

```text
household_id
surname
home_property_id
wealth
food_security
happiness
created_at
```

Relationship types:

```text
SPOUSE
PARENT
CHILD
SIBLING
ROOMMATE
DEPENDENT
```

A household should:

- share a residence
- share some finances
- react to events involving family
- relocate together where appropriate

Example:

If a player's shop employs Mara Whitcombe and the player helps Mara's spouse during an incident, Mara can gain relationship affinity too.

---

# 27. NPC Schedules

Create schedule templates.

Example baker:

```text
05:00 Wake
05:30 Walk to bakery
06:00 Work
12:00 Lunch
13:00 Work
18:00 Visit market
19:00 Tavern
21:00 Walk home
22:00 Sleep
```

Schedule table:

```sql
lw_npc_schedule
```

Fields:

```text
schedule_id
npc_id
day_mask
start_minute
end_minute
activity
target_type
target_id
x
y
z
o
```

Activities:

```text
HOME
SLEEP
WORK
TRAVEL
SHOP
TAVERN
SOCIAL
PATROL
SCHOOL
MARKET
FISH
FARM
IDLE
```

## Movement

For nearby loaded NPCs:

- use normal movement generators
- waypoint movement
- point movement
- spline/pathfinding

For NPCs outside loaded player areas:

Do not physically simulate every step.

Use "offline simulation."

Example:

At 13:00 the database says Mara should be at the bakery.

When the grid loads, spawn or relocate Mara at the correct schedule location.

This is dramatically cheaper than simulating thousands of NPCs constantly.

---

# 28. NPC Jobs

Jobs should serve multiple systems.

A job determines:

- income
- work schedule
- workplace
- shop staffing
- town production
- available rumors
- incidents
- NPC clothing
- local supply contributions

Examples:

A farmer increases regional Food.

A miner increases Ore supply.

A town guard improves Safety.

A merchant improves Trade.

A healer slightly improves Morale.

This means the NPC population itself affects the town simulation.

---

# 29. NPC Relationships With Players

Create:

```sql
lw_npc_player_relationship
```

Fields:

```text
npc_id
player_guid
affinity
trust
fear
respect
last_interaction
flags
```

Do not create a row for every player and every NPC.

Only create records after meaningful interaction.

Example affinity scale:

```text
-1000 Nemesis
-500  Disliked
-100   Wary
0      Stranger
100    Acquaintance
300    Friend
600    Trusted
900    Beloved
```

Interactions:

### Positive

- rescue NPC
- complete personal contract
- frequent purchases
- employ NPC fairly
- help family member
- reduce rent
- repair their home

### Negative

- rob NPC
- attack NPC
- overcharge rent
- fire unfairly
- harm family
- fail important incident

Relationship effects:

- greetings
- discounts
- refusal of service
- rumor sharing
- gifts
- job offers
- rare quests
- willingness to work for the player

---

# 30. Traveling Merchants

Traveling merchants are persistent NPC businesses that move between settlements.

Create:

```sql
lw_traveling_merchant
```

Fields:

```text
merchant_id
npc_id
route_id
inventory_profile
current_stop
next_departure
```

A merchant route might be:

```text
Goldshire -> Lakeshire -> Darkshire -> Stormwind
```

Inventory changes based on:

- origin
- destination
- settlement supply
- merchant specialty
- recent purchases

Rumors announce merchant arrivals.

Example:

> A traveling jeweler from Ironforge has set up near the Darkshire inn.

---

# 31. Merchant Caravans

Caravans physically transport economic supply.

Create:

```sql
lw_caravan_route
lw_caravan
lw_caravan_cargo
```

Route definition:

```text
route_id
origin_settlement
destination_settlement
path_id
travel_time
risk
frequency
escort_enabled
```

Runtime caravan:

```text
caravan_id
route_id
state
departed_at
expected_arrival
leader_spawn_guid
cargo_value
```

States:

```text
PREPARING
TRAVELING
UNDER_ATTACK
ARRIVED
DESTROYED
CANCELLED
```

## Cargo

Use commodity categories.

Examples:

```text
FOOD
GRAIN
MEAT
FISH
ORE
CLOTH
HERBS
MEDICINE
LUMBER
LUXURY
TOOLS
```

When a caravan arrives:

```text
destination supply += cargo
trade += value
wealth += tax effect
```

When destroyed:

```text
destination supply -= expected shipment
safety -= penalty
crime += penalty
```

Then generate:

- bounty opportunity
- rumor
- world incident
- newspaper entry

---

# 32. Caravan Escorts

Players can accept an escort contract.

Reward:

- gold
- Renown
- local civic standing
- NPC affinity
- possible business reputation

Do not spawn a separate caravan for every player.

Use shared world caravans.

Multiple players can help the same one.

---

# 33. Regional Supply and Demand

Do not attempt fully dynamic pricing for every WoW item.

Use commodity groups.

Create:

```sql
lw_commodity
lw_settlement_commodity
```

Commodity:

```text
commodity_id
name
base_price_index
item_group
decay_rate
```

Settlement state:

```text
settlement_id
commodity_id
supply
demand
price_index
last_update
```

Suggested price index:

```text
0.50 to 2.00
```

Example formula:

```text
scarcity = target_supply / max(current_supply, minimum_supply)
price_index = clamp(scarcity * demand_modifier, 0.50, 2.00)
```

Smooth changes over time.

Do not let one player dumping 5,000 Iron Bars instantly crash the entire economy.

---

# 34. Dynamic Vendor Pricing

Stock AzerothCore vendor pricing is largely based around static item and vendor data.

For Living World dynamic prices, use one of two approaches.

## Option A: Living World Storefront UI

Use Gossip or a custom addon interface.

The module calculates:

- price
- stock
- owner margin
- tax

Then manually performs the transaction.

This requires no global vendor-price core patch.

## Option B: Add a Core Price Override Hook

Add hooks such as:

```cpp
OnCalculateVendorBuyPrice(...)
OnCalculateVendorSellPrice(...)
```

The Living World module then adjusts price by settlement commodity indexes.

This is the cleaner long-term solution if dynamic pricing should apply to ordinary WoW vendors too.

---

# 35. Purchase Shops

Commercial properties use the same Property system.

A player purchases:

```text
building
license
business
```

Do not make "shop" ownership simply a weekly money printer.

Create:

```sql
lw_business
```

Fields:

```text
business_id
property_id
owner_guid
business_type
name
cash_balance
quality
reputation
advertising_level
stock_capacity
opened_at
last_simulated
```

Business types:

```text
General Store
Blacksmith
Armorer
Weaponsmith
Alchemy Shop
Herbalist
Tailor
Leatherworker
Bakery
Inn
Fishmonger
Jeweler
Stable
Furniture Shop
Bookshop
Specialty Shop
```

---

# 36. Player-Owned Storefronts

Storefronts should support two inventory sources.

## Simulated Inventory

Generated from:

- business type
- local supply
- employees
- business quality
- settlement prosperity

## Player Consignment Inventory

Owner deposits actual items for sale.

Create:

```sql
lw_business_inventory
```

Fields:

```text
business_id
item_guid
seller_guid
quantity
price
listed_at
expires_at
```

For player consignment, use actual item instances.

Do not duplicate the item.

Move it into escrow storage while listed.

When sold:

- buyer receives item
- seller/business ledger receives gold
- local economy receives transaction data
- taxes are applied

---

# 37. Shop Management

Owner controls:

- shop type
- business name
- opening policy
- margins
- employee roster
- advertising
- stock priority
- specialty product
- shop quality upgrades
- storage capacity

Example management menu:

```text
The Golden Griffin
Blacksmith
Reputation: 72
Weekly Revenue: 426g
Weekly Expenses: 191g
Employees: 3 / 4
Stock: 68%
Customer Satisfaction: 81%

[View Ledger]
[Manage Employees]
[Manage Stock]
[Set Pricing Policy]
[Purchase Upgrade]
[Advertise]
[Collect Earnings]
```

---

# 38. Business Simulation

Business income should depend on the world.

Example:

```text
CustomerDemand =
    settlement_population
  * settlement_prosperity
  * business_need
  * business_reputation
  * advertising
```

Revenue:

```text
Demand * average_margin * stock_availability
```

Expenses:

```text
employee wages
property tax
restocking
maintenance
advertising
```

Avoid creating unlimited gold.

Use settlement economic budgets.

A town with 40 simulated residents should not generate 50,000 gold per week.

---

# 39. Employees

Create:

```sql
lw_employee
```

Fields:

```text
employee_id
npc_id
business_id
role
wage
skill
morale
hired_at
```

Traits can modify business results.

Examples:

```text
Efficient
Friendly
Dishonest
Lazy
Talented
Famous
Hardworking
Clumsy
Charismatic
Experienced
```

Examples:

`Efficient`

- lower restocking cost

`Friendly`

- higher customer satisfaction

`Dishonest`

- may steal business income
- slightly improves black-market opportunities

`Famous`

- increases customer traffic

`Lazy`

- lowers productivity

---

# 40. Rare Employees and Specialists

Some named NPCs can be recruited only through special events or quest chains.

Example:

```text
Master Smith Durgan Anvilscar
```

Recruitment condition:

- rescue from incident
- complete crafting quest chain
- reach high affinity

Benefits:

- unlock rare recipes
- improve shop quality
- enable specialty inventory
- increase business prestige

Rare employees should be characters in the world, not menu upgrades.

---

# 41. Seasonal Agriculture

Farms are a property type.

Create:

```sql
lw_farm_plot
```

Fields:

```text
plot_id
property_id
crop_id
planted_at
growth_modifier
fertility
moisture
state
```

Crop definition:

```sql
lw_crop
```

Fields:

```text
crop_id
name
growth_time
preferred_season
preferred_weather
yield_min
yield_max
commodity_id
```

Growth uses timestamps.

At harvest:

```text
yield =
base yield
* fertility
* weather modifier
* season modifier
* farmer skill
```

Harvest contributes to:

- owner inventory
- regional Food supply
- business supply if contracted

---

# 42. Seasons

The Living World should expose a current season.

Example:

```text
Spring
Summer
Autumn
Winter
```

Season can be:

- real-world calendar based
- Esteria custom calendar based

Recommended:

Use an Esteria season calendar so the system is controllable.

Season affects:

- crop yield
- fish availability
- certain incidents
- NPC schedules
- festivals
- caravan demand
- commodity demand

---

# 43. Fishing Economy

Track fishing harvest by region.

Create:

```sql
lw_fishing_region
lw_fishing_state
```

Each region has:

- common fish
- specialty fish
- stock index
- restaurant demand
- seasonal multiplier

Player catches can contribute small supply changes.

Rare fish can be requested by:

- inns
- restaurants
- collectors
- festivals
- traveling merchants

Do not punish ordinary fishing heavily.

The economy should add opportunities, not make fishing unusable.

---

# 44. Ecology and Hunting

Do not simulate individual animal reproduction.

Use population indexes.

Create:

```sql
lw_ecology_population
```

Fields:

```text
zone_id
species_group
population_index
target_population
birth_rate
predation_rate
last_update
```

Example groups:

```text
Wolf
Deer
Boar
Bear
Spider
Raptor
Predator
Prey
```

Creature kills reduce the population index.

Periodic simulation moves the value toward equilibrium.

Example:

```text
wolves low
-> deer growth increases

deer high
-> crop/livestock incidents increase

deer high
-> wolf recovery increases
```

## World Effect

Population index can alter:

- respawn time
- spawn-group activation
- incident probability
- bounty generation

Avoid constantly creating and deleting individual creatures.

---

# 45. World Incidents

Incidents are small dynamic events.

Create:

```sql
lw_incident_template
lw_incident
```

Templates include:

```text
Broken Wagon
Wolf Attack
Store Robbery
House Fire
Missing Person
Escaped Prisoner
Bandit Ambush
Sick Traveler
Lost Child
Caravan Attack
Merchant Dispute
Crop Disease
Dock Accident
Rare Merchant Arrival
```

Each template defines:

```text
eligible settlement types
required prosperity range
required safety range
required season
weight
duration
spawn groups
success conditions
failure conditions
rewards
consequences
```

---

# 46. Incident Director

Every minute or few minutes:

1. Calculate incident budget by settlement.
2. Check active incident count.
3. Evaluate possible incident templates.
4. Weight based on world state.
5. Roll.
6. Spawn incident if selected.
7. Add rumor.
8. Add bounty if appropriate.

Example:

Low Safety increases:

- robbery
- bandit attack
- kidnapping
- caravan ambush

Low Food increases:

- theft
- begging
- crop-related requests

High Prosperity increases:

- festivals
- traveling merchants
- luxury trade

This makes events look random while still reflecting the simulation.

---

# 47. Crime System

Crime is local.

Create:

```sql
lw_player_crime
```

Fields:

```text
guid
settlement_id
wanted_points
bounty_value
last_crime
last_decay
status
```

Crime types:

```text
Theft
Assault
Murder
Robbery
Smuggling
Trespassing
Property Damage
Illegal Contract
Caravan Sabotage
```

Wanted tiers:

```text
0      Clean
1      Suspected
2      Wanted
3      Dangerous
4      Notorious
5      Most Wanted
```

Wanted points decay slowly if no new crimes occur.

Serious crimes decay more slowly.

---

# 48. Guard Reaction

Guard behavior depends on:

- wanted level
- local Safety
- current guard funding
- government policy
- player citizenship
- player disguise status if added later

Possible responses:

```text
warning
fine
attempted arrest
hostility
reinforcement call
bounty creation
```

Do not make every small theft an instant death sentence.

Crime becomes more interesting when escalation exists.

---

# 49. Stealing Gold From Other Players

Player theft should be possible but heavily constrained to prevent griefing.

Only gold can be stolen.

Never allow theft of:

- equipped items
- inventory items
- soulbound items
- quest items
- currencies represented by items
- guild bank assets

## Suggested Requirements

The thief must:

- be alive
- be near the victim
- not be in combat
- not be in a battleground or arena
- not be in a raid or dungeon
- not be in a sanctuary unless the settlement explicitly allows crime
- satisfy a cooldown
- use a dedicated Pickpocket Player action

The target must:

- be online
- be alive
- not be on a loading screen
- not have recently been stolen from
- not be the thief's own account
- not be in the thief's group

## Theft Amount

Use a capped formula.

Example:

```text
min(
    target_gold * 0.005,
    thief_level * configured_value,
    absolute_maximum
)
```

This prevents catastrophic losses.

Example hard cap:

```text
5 to 20 gold
```

depending on Esteria's economy.

## Success Chance

Depends on:

- thief level
- target level
- target awareness
- thief crime skill if implemented
- whether thief is behind target
- local guard presence
- NPC witnesses

## Failure

Failure can:

- reveal thief
- increase wanted level
- alert guards
- create PvP eligibility if Esteria wants that rule
- create a bounty
- give target temporary theft immunity

## Anti-Grief Rules

Use:

- per-thief cooldown
- per-target cooldown
- target immunity after theft
- daily theft income cap
- same-account block
- transaction logging
- suspicious transfer detection

Do not make theft the most profitable activity in the game.

It should be a criminal playstyle, not a gold-generation exploit.

---

# 50. Bounty Board

Every settlement can have a physical bounty board GameObject.

Categories:

```text
Hunt
Bandit
Escort
Recovery
Delivery
Investigation
Creature Control
Crime
Community
```

Create:

```sql
lw_bounty
```

Fields:

```text
bounty_id
settlement_id
bounty_type
target_type
target_id
created_at
expires_at
reward_gold
reward_renown
reward_civic
status
generated_by
```

Sources:

- incident
- ecology problem
- wanted criminal
- caravan attack
- government action
- random civic need

Bounties should use actual active world conditions where possible.

---

# 51. Crime Bounties on Players

High wanted levels can generate a player bounty.

Important restrictions:

- only use it where world PvP rules make sense
- do not turn sanctuary areas into forced PvP
- do not allow alt-account bounty farming
- use reward cooldowns for repeatedly killing the same criminal
- reduce bounty only through legitimate capture/kill rules

An alternative to forced PvP is:

```text
Wanted player interacts with guards
-> surrender
-> fine or jail timer
```

This supports criminal roleplay even on a mostly PvE server.

---

# 52. Rumor System

Rumors should describe real active state.

Do not generate meaningless fake statements.

Sources:

- active incidents
- caravan failures
- rare merchant arrivals
- high-profile crimes
- weddings
- government changes
- settlement prosperity changes
- rare creature activity
- ecology problems
- business openings
- public projects

Create:

```sql
lw_rumor
```

Fields:

```text
rumor_id
settlement_id
source_event_id
text_key
created_at
expires_at
priority
```

NPCs with `Gossipy` trait can expose more rumors.

Innkeepers always expose major rumors.

Example gossip:

```text
[Ask about local rumors]
```

Possible response:

> The grain caravan from Goldshire should have arrived yesterday. Folks are starting to worry.

That rumor should correspond to an actual delayed caravan.

---

# 53. Town Criers

Town criers announce high-priority local events.

Examples:

```text
"Hear ye! The eastern caravan road has reopened!"
"The Mayor has approved repairs to the market square!"
"A reward has been posted for the capture of Garrick Blackhand!"
```

Do not spam.

Use cooldowns.

Only announce:

- major incidents
- government changes
- prosperity tier changes
- festivals
- important bounties
- notable marriages if players opt in

---

# 54. Esteria Chronicle

Create a server history ledger.

```sql
lw_world_event_log
```

Fields:

```text
event_id
event_type
created_at
settlement_id
primary_guid
secondary_guid
npc_id
property_id
business_id
value
headline_key
metadata
importance
```

The Chronicle generator runs weekly.

Sections:

```text
Realm News
Town News
Trade
Society
Crime
Guilds
Property
Government
Notable Adventures
Upcoming Events
```

Delivery options:

1. Newspaper vendor item
2. Gossip kiosk
3. Mail
4. Custom addon panel
5. Website/API later

Example:

```text
THE ESTERIA CHRONICLE

Darkshire Trade Route Restored
Local adventurers cleared the northern road after repeated attacks on grain caravans.

Rosewood Bakery Changes Hands
A new owner has purchased the bakery property near the town square.

Wedding Bells in Stormwind
[Player A] and [Player B] were married this week.
```

Players should be able to opt out of having marriage or property purchases publicly named.

---

# 55. Social Classes and Titles

Social progression should be separate from combat progression.

Possible classes:

```text
Resident
Citizen
Landowner
Landlord
Merchant
Innkeeper
Shopkeeper
Magnate
Patron
Philanthropist
Artisan
Farmer
Fisher
Explorer
Bounty Hunter
Outlaw
Notorious Outlaw
Civic Leader
Mayor
Sheriff
Noble
```

Do not assign classes manually.

Derive them from achievements.

Examples:

```text
Landowner
Own 1 qualifying property

Magnate
Own 5 businesses with positive profit

Philanthropist
Donate X gold and complete Y civic projects

Outlaw
Reach Wanted Tier 4

Patron
Reach high civic standing and finance town projects
```

## Custom Titles

New WoW title strings can require client-side DBC support.

Esteria already uses a custom client, so custom title support can be added through the appropriate title DBC/client patch.

Until then:

- use existing titles where appropriate
- use addon UI titles
- use gossip profile labels

---

# 56. Guild Property

Reuse the Property system.

Set:

```text
owner_type = GUILD
owner_guid = guild_id
```

Property types:

```text
Guild Hall
Warehouse
Fort
Inn
Ship
Compound
Workshop
Embassy
```

Guild permissions should map to guild rank permissions.

Possible upgrades:

- larger storage
- trophy hall
- meeting room
- guild hearth
- crafting room
- cosmetic guards
- stable
- vendor lease
- guild notice board

Avoid mandatory raid combat bonuses.

Guild property should mainly provide:

- identity
- convenience
- economy
- social spaces
- prestige

---

# 57. Guild Property Economy

Guild property can participate in the world.

Examples:

A guild warehouse:

- increases caravan capacity
- reduces business storage costs

A guild inn:

- earns modest local income
- increases town Trade

A guild fort:

- contributes Safety
- provides visual guard presence

A guild workshop:

- improves local industrial commodity supply

Cap effects to prevent one guild from controlling the entire settlement simulation.

---

# 58. Business and Property Taxes

Taxes are a gold sink and economic control tool.

Possible taxes:

```text
property tax
commercial license
sales tax
guild property upkeep
market listing fee
```

Taxes go into a simulated settlement treasury.

Create:

```sql
lw_settlement_treasury
```

Fields:

```text
settlement_id
balance
income_week
expense_week
last_update
```

Government projects consume this treasury.

Do not allow office holders to withdraw treasury money directly.

---

# 59. Public Projects

Government and players can fund projects.

Create:

```sql
lw_public_project
```

Examples:

```text
Market Expansion
Road Repair
Guard Barracks
Festival
Farm Subsidy
Dock Expansion
Town Decorations
Caravan Protection
Clinic
```

Stages:

```text
PROPOSED
FUNDING
CONSTRUCTION
COMPLETE
EXPIRED
```

Players donate:

- gold
- lumber
- ore
- cloth
- food

Completion affects the settlement.

Where possible, show construction stages using spawn groups.

---

# 60. Relationship Between All Systems

Example complete loop:

1. Darkshire has low Food.
2. Food price index rises.
3. A player-owned bakery earns higher margins but has trouble getting grain.
4. Goldshire dispatches a grain caravan.
5. Bandits attack the caravan.
6. Players ignore it.
7. Caravan is destroyed.
8. Darkshire Food falls further.
9. Safety decreases.
10. Rumors spread.
11. A bounty appears.
12. A criminal player begins stealing more often because guard funding is weak.
13. The Sheriff funds patrols.
14. Players complete the bandit bounty.
15. Civic standing rises.
16. A new caravan succeeds.
17. Food begins recovering.
18. Bakery inventory improves.
19. Town prosperity improves.
20. Newspaper reports the recovery.

No single feature creates this story.

The interaction between systems creates it.

---

# 61. AzerothCore Hook Mapping

Use AzerothCore hooks where they already exist.

Recommended examples:

## `WorldScript`

Use for:

- module startup
- shutdown
- configuration loading
- lightweight scheduler tick

Do not execute expensive database loops every `OnWorldUpdate`.

## `PlayerScript`

Use for:

- login
- logout
- XP modification
- quest completion
- creature kill credit
- money changes
- reputation-related integration
- marriage aura checks
- crime interactions
- Renown events

## `CreatureScript`

Use for:

- procedural NPC gossip
- shopkeepers
- government NPCs
- marriage officiants
- traveling merchants
- employee NPCs

## `GameObjectScript`

Use for:

- property deeds
- doors
- storage
- bounty boards
- newspaper stands
- farm plots
- shop management objects

## `GuildScript`

Use for:

- guild property cleanup
- guild ownership validation
- disband behavior
- rank changes

## `WeatherScript`

Use for:

- agriculture modifiers
- fishing modifiers
- incident weighting

## `GameEventScript`

Use for:

- seasonal festivals
- scheduled world celebrations

## `LootScript`

Use for:

- economy observation
- optional money-flow metrics

## `MailScript`

Use for:

- rent notices
- business payouts
- government notices
- newspaper delivery

---

# 62. When a Core Hook Should Be Added

Prefer a module-only implementation.

Add a small AzerothCore hook only when the module cannot cleanly accomplish the behavior.

Strong candidates:

1. dynamic creature query name override
2. dynamic vendor buy-price override
3. dynamic vendor sell-price override
4. optional custom guard response decision
5. optional custom spawn population multiplier

Any core addition should expose a generic hook.

Do not hardcode Esteria-specific logic directly into AzerothCore core files.

Example:

Bad:

```cpp
if (EsteriaLivingWorldEnabled)
    price *= GetDarkshirePrice();
```

Good:

```cpp
sScriptMgr->OnCalculateVendorBuyPrice(player, vendor, item, price);
```

Then the module changes `price`.

---

# 63. Server Commands

Add GM/admin commands.

Examples:

```text
.lw status
.lw settlement list
.lw settlement info <id>
.lw settlement set <id> <stat> <value>
.lw property info <id>
.lw property owner <id>
.lw property transfer <id> <player>
.lw property reset <id>
.lw npc info <npcId>
.lw npc regenerate <npcId>
.lw npc schedule <npcId>
.lw business info <id>
.lw caravan list
.lw caravan spawn <routeId>
.lw incident list
.lw incident start <templateId> <settlementId>
.lw crime info <player>
.lw crime clear <player>
.lw renown <player>
.lw morality <player>
.lw citizenship <player>
.lw government info <settlement>
.lw simulate <hours>
```

A simulation command is especially valuable for testing.

Example:

```text
.lw simulate 168
```

Runs seven simulated days without waiting a real week.

---

# 64. Configuration

Example `LivingWorld.conf.dist`:

```ini
LivingWorld.Enable = 1

LivingWorld.Tick.IntervalMS = 1000
LivingWorld.Settlement.UpdateMinutes = 5
LivingWorld.Economy.UpdateMinutes = 15
LivingWorld.Ecology.UpdateMinutes = 30
LivingWorld.Business.UpdateMinutes = 60

LivingWorld.Property.Enable = 1
LivingWorld.Property.MaxPlayerOwned = 5

LivingWorld.Marriage.Enable = 1
LivingWorld.Marriage.XPBonusPct = 10
LivingWorld.Marriage.StatBonusPct = 3
LivingWorld.Marriage.Range = 100

LivingWorld.Renown.Enable = 1
LivingWorld.Morality.Enable = 1

LivingWorld.Crime.Enable = 1
LivingWorld.Crime.PlayerTheft.Enable = 1
LivingWorld.Crime.PlayerTheft.MaxGold = 10
LivingWorld.Crime.PlayerTheft.TargetCooldownMinutes = 60

LivingWorld.NPC.Enable = 1
LivingWorld.NPC.MaxActiveProceduralNPCs = 500
LivingWorld.NPC.OfflineScheduleSimulation = 1

LivingWorld.Caravan.Enable = 1
LivingWorld.Incident.Enable = 1
LivingWorld.Chronicle.Enable = 1
```

Every major system should be independently configurable.

---

# 65. Logging

Add dedicated log categories.

Examples:

```text
module.livingworld
module.livingworld.property
module.livingworld.business
module.livingworld.economy
module.livingworld.npc
module.livingworld.crime
module.livingworld.government
```

Log important transactions.

Especially:

- gold transfers
- property purchases
- property transfers
- business payouts
- theft
- government spending
- marriage creation/deletion
- bounty rewards
- guild property changes

---

# 66. Transaction Safety

Any action moving significant gold or ownership should use database transactions.

Examples:

Property purchase:

```text
deduct player gold
insert owner record
insert transaction ledger
```

These should succeed or fail together.

Business sale:

```text
remove escrow item
grant buyer item
credit business
record sale
```

Theft:

```text
validate victim funds
deduct victim
credit thief
record crime
record theft ledger
```

Never trust the client for:

- price
- ownership
- amount
- eligibility
- income
- wanted level
- business balance

The server calculates everything.

---

# 67. Gold Ledger

Create:

```sql
lw_financial_ledger
```

Fields:

```text
transaction_id
transaction_type
source_type
source_id
destination_type
destination_id
amount
created_at
metadata
```

Transaction types:

```text
PROPERTY_PURCHASE
PROPERTY_SALE
RENT
BUSINESS_SALE
EMPLOYEE_WAGE
TAX
THEFT
BOUNTY_REWARD
GOVERNMENT_EXPENSE
CARAVAN_TRADE
PUBLIC_DONATION
```

This makes economy debugging possible.

---

# 68. Performance Rules

## Never

- query every property every world tick
- save every NPC every movement step
- simulate every NPC when no players are near
- recalculate the entire economy after each purchase
- run thousands of SQL statements individually when a batch works
- spawn every procedural NPC in unloaded zones

## Prefer

- cached managers
- timestamps
- dirty flags
- periodic batch writes
- event aggregation
- spawn groups
- offline simulation
- lazy loading
- settlement-level summaries

---

# 69. Offline NPC Simulation

This is critical.

A player does not care whether an NPC physically walked through an unloaded Elwynn Forest grid at 3:17 AM.

If no players are nearby:

```text
NPC simulation = logical state
```

Store:

```text
current activity
expected destination
activity start
activity end
```

When a player loads the area:

```text
determine where NPC should currently be
spawn/relocate there
resume physical movement
```

This allows thousands of persistent NPCs without thousands of active AI objects.

---

# 70. Client Interface

All systems can initially function using:

- Gossip
- GameObjects
- Mail
- Chat commands
- NPC text
- existing vendor UI where possible

However, Esteria has a custom client.

A later custom addon can provide:

```text
Living World panel
Property browser
Business management
Settlement status
Citizen profile
Government interface
Bounty board
Marriage profile
Renown profile
Crime status
Chronicle reader
```

The server remains authoritative.

The addon only displays information and sends requests.

---

# 71. Suggested Living World UI

Main panel:

```text
ESTERIA

Character
  Renown
  Morality
  Social Titles

Home
  Residence
  Properties
  Tenants

Business
  Shops
  Employees
  Ledger

Community
  Citizenship
  Civic Standing
  Government
  Bounties

World
  Settlement Status
  Trade
  Rumors
  Chronicle

Relationships
  Marriage
  NPC Relationships
```

This is optional for the first implementation.

---

# 72. Implementation Phases

Do not attempt all features simultaneously.

## Phase 0: Framework

Implement:

- `mod-esteria-living-world`
- managers
- database loading
- event bus
- scheduler
- configuration
- commands
- logging
- ledger

Acceptance criteria:

- server loads module
- module loads tables
- `.lw status` works
- simulation can be toggled
- no gameplay changes yet

---

## Phase 1: Settlements

Implement:

- settlement definitions
- settlement state
- prosperity calculation
- civic standing framework
- state admin commands

Acceptance criteria:

- four test towns load
- prosperity changes can be simulated
- values persist across restart

---

## Phase 2: Property

Implement:

- property definitions
- purchase
- sale
- residence
- NPC tenant
- rent
- condition
- property permissions
- landlord morality

Acceptance criteria:

- player buys a building
- existing NPC household remains as tenant
- rent is paid
- player can later move in
- ownership survives restart

---

## Phase 3: Marriage + Renown + Morality

Implement:

- marriage ceremony
- paired ring GUID tracking
- spouse proximity buff
- XP bonus
- scaling stat aura
- Renown
- Good/Evil
- social event logging

Acceptance criteria:

- married players receive bonus only with correct rings and proximity
- Renown persists
- morality changes through Living World actions

---

## Phase 4: Persistent Procedural NPCs

Implement:

- NPC generator
- names
- occupations
- households
- homes
- schedules
- offline simulation
- basic player affinity

Acceptance criteria:

- named family persists after restart
- NPC leaves home for job
- NPC returns home later
- relationship changes persist

---

## Phase 5: Shops

Implement:

- commercial property
- business creation
- employees
- simulated demand
- expenses
- player-owned storefront
- ledger

Acceptance criteria:

- shop can profit or lose money
- employee traits matter
- town economy influences demand

---

## Phase 6: Regional Economy + Caravans

Implement:

- commodity groups
- supply/demand
- price index
- caravan routes
- caravan cargo
- escort contracts
- failed caravan consequences

Acceptance criteria:

- caravan loss creates a shortage
- shortage changes economic state
- successful caravan restores supply

---

## Phase 7: Incidents + Rumors + Bounties

Implement:

- incident director
- bounty board
- rumor generation
- town crier
- event log

Acceptance criteria:

- incidents reflect settlement conditions
- rumors correspond to real events
- bounty completion changes settlement state

---

## Phase 8: Crime

Implement:

- wanted levels
- local crime
- guards
- player gold theft
- player criminal bounties
- surrender/fine flow

Acceptance criteria:

- theft is logged
- victim cannot be repeatedly griefed
- guards react based on wanted level
- wanted status is local

---

## Phase 9: Citizenship + Government

Implement:

- citizenship
- civic ranks
- offices
- terms
- treasury
- public projects

Acceptance criteria:

- high-standing player can hold office
- office powers use restricted predefined actions
- public spending affects settlement

---

## Phase 10: Agriculture + Fishing + Ecology

Implement:

- farms
- crops
- seasons
- fishing stock
- creature population indexes
- ecology-driven incidents

Acceptance criteria:

- farms feed economy
- overhunting changes population index
- ecology affects incidents or respawns

---

## Phase 11: Chronicle + Social Titles

Implement:

- weekly history aggregation
- town newspaper
- public opt-out
- social achievement titles

Acceptance criteria:

- Chronicle references real server events
- social titles derive from real activity

---

## Phase 12: Guild Property

Implement:

- guild owner type
- guild halls
- warehouses
- upgrades
- guild economic contributions

Acceptance criteria:

- guild property persists
- guild rank permissions work
- disband safely releases property

---

# 73. Minimum Viable Living World

The first version that will already feel substantially different from normal WoW should include:

1. four simulated settlements
2. property ownership
3. NPC tenants
4. marriage
5. Renown
6. morality
7. persistent named NPC families
8. NPC schedules
9. player-owned shops
10. regional commodities
11. caravans
12. town prosperity
13. world incidents
14. rumors
15. bounty boards

Government, ecology, agriculture, newspaper generation, and guild property can safely come later.

---

# 74. Recommended Initial Test Story

Use Darkshire as the first complete vertical slice.

Implement:

```text
10 properties
2 commercial shops
2 farms
20 procedural residents
5 families
1 inn
1 blacksmith
1 baker
1 traveling merchant
1 caravan route from Goldshire
5 incident types
1 bounty board
1 town crier
citizenship
prosperity
food supply
safety
crime
```

Then test this scenario:

1. Server starts with Stable prosperity.
2. Grain caravan is destroyed.
3. Food decreases.
4. Bakery supply decreases.
5. Food prices rise.
6. Rumor appears.
7. Bounty appears.
8. Players kill bandits.
9. New caravan departs.
10. Caravan arrives.
11. Food recovers.
12. Civic standing is awarded.
13. Town crier announces restored trade.
14. Chronicle records the event.

If this feels alive, the architecture works.

Then expand to the rest of Azeroth.

---

# 75. Database Table Summary

## World / Definitions

```text
lw_settlement
lw_property_template
lw_business_type
lw_commodity
lw_crop
lw_npc_archetype
lw_npc_name_pool
lw_occupation
lw_schedule_template
lw_caravan_route
lw_incident_template
lw_government_office
lw_social_title
lw_public_project_template
lw_fishing_region
```

## Characters / Persistent State

```text
lw_settlement_state
lw_settlement_commodity
lw_settlement_treasury

lw_property_owner
lw_property_tenant
lw_property_access

lw_business
lw_business_inventory
lw_employee

lw_marriage
lw_player_renown
lw_player_morality
lw_citizenship
lw_player_crime

lw_npc
lw_household
lw_household_member
lw_npc_schedule
lw_npc_player_relationship

lw_caravan
lw_caravan_cargo

lw_incident
lw_bounty
lw_rumor

lw_government_term
lw_public_project

lw_farm_plot
lw_fishing_state
lw_ecology_population

lw_world_event_log
lw_financial_ledger
```

---

# 76. Core Data Relationships

```text
Settlement
├── Properties
│   ├── Residence
│   │   └── Household
│   ├── Business
│   │   └── Employees
│   └── Guild Property
│
├── Citizens
│   └── Government Offices
│
├── NPC Population
│   ├── Households
│   ├── Jobs
│   ├── Schedules
│   └── Relationships
│
├── Economy
│   ├── Commodities
│   ├── Shops
│   ├── Farms
│   ├── Fishing
│   └── Caravans
│
├── Safety
│   ├── Crime
│   ├── Wanted Players
│   ├── Guards
│   └── Bounties
│
└── World Activity
    ├── Incidents
    ├── Rumors
    ├── Public Projects
    └── Chronicle
```

---

# 77. Important Design Rules

## Rule 1: Persistence Matters More Than Complexity

A simple NPC who:

- has a name
- has a spouse
- owns a home
- works at the bakery
- remembers the player

will feel more alive than an advanced random NPC that disappears after restart.

## Rule 2: Consequences Must Be Visible

If prosperity changes, show it.

If crime rises, show more danger.

If a caravan fails, reduce supply.

If a player becomes famous, NPCs should react.

Numbers hidden in SQL do not create a living world.

## Rule 3: Avoid Pure Passive Income

Property and shops should involve:

- taxes
- maintenance
- employees
- tenants
- economy
- local conditions

Otherwise they become login-and-collect systems.

## Rule 4: Do Not Simulate What Nobody Can See

Offline simulation should use state transitions and timestamps.

Do not run thousands of invisible AIs.

## Rule 5: Players Should Create History

Record meaningful events.

A living world becomes convincing when players can look back and say:

> I remember when Darkshire had the grain shortage.

---

# 78. Recommended Development Target

Create one module:

```text
mod-esteria-living-world
```

Keep almost all Esteria-specific behavior inside it.

Only add generic hooks to AzerothCore core when a module hook does not already exist.

The first technical milestone should not be "implement all features."

It should be:

> Create a persistent Darkshire simulation where one property, one family, one shop, one caravan, one incident, one rumor, and one player action all affect the same settlement state.

Once that vertical slice works, every system in this document becomes an extension of the same architecture rather than a separate experiment.

---

# 79. AzerothCore References

Useful upstream references:

- AzerothCore module skeleton:  
  https://github.com/azerothcore/skeleton-module

- AzerothCore scripting hooks overview:  
  https://www.azerothcore.org/wiki/hooks-script

- AzerothCore C++ hook reference:  
  https://www.azerothcore.org/wiki/hooks-script-reference

- AzerothCore custom SQL layout:  
  https://www.azerothcore.org/wiki/sql-directory

- AzerothCore source:  
  https://github.com/azerothcore/azerothcore-wotlk

The module system should be preferred over editing core logic directly. Generic hooks can be added only where the existing script API cannot support a Living World requirement.

---

# 80. Final Target

The final experience should make a player feel that Esteria exists even when they are not personally progressing a quest chain.

A player should be able to log in and discover:

- their tenant paid rent
- their shop had a good week because Ironforge ore prices fell
- their spouse is online and their wedding ring bonus activates
- a family they know has moved to another house
- a caravan disappeared outside Darkshire
- the town is offering a bounty
- the innkeeper is talking about the disappearance
- the Mayor funded additional guards
- crime has fallen
- a rare merchant has arrived
- their citizenship rank increased
- the Chronicle mentions a guild's new hall
- a familiar NPC remembers something the player did last week

That is the target.

Not more menus.

Not more currencies.

A world that remembers.
