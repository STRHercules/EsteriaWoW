# Esteria — Client & Gameplay Idea Backlog

> **Working notes / brainstorming document.** A collection of client, gameplay, UI, and world-system ideas for Esteria. These are concepts, not finalized implementation requirements or a prioritized roadmap.

> **Placeholders:** `X`, `Y`, and question marks indicate values or decisions to be determined. Ideas with no detailed specification are retained under **Unscoped / Exploratory Ideas**.

## Contents

1. [Client, UI & Integrations](#1-client-ui--integrations)
2. [Character Creation & Identity](#2-character-creation--identity)
3. [Classes, Progression & Scaling](#3-classes-progression--scaling)
4. [Travel, Exploration & World Events](#4-travel-exploration--world-events)
5. [PvP, Factions & Wilderness](#5-pvp-factions--wilderness)
6. [Dungeons, Quests & Challenges](#6-dungeons-quests--challenges)
7. [Economy, Loot & Vendors](#7-economy-loot--vendors)
8. [Housing, Guilds & Professions](#8-housing-guilds--professions)
9. [Hunter & Warlock Pets](#9-hunter--warlock-pets)
10. [Companion Pets & Hired Companions](#10-companion-pets--hired-companions)
11. [Battlemon / Pokémon](#11-battlemon--pokémon)
12. [Seasonal Content & Rotations](#12-seasonal-content--rotations)
13. [Systems to Port & Reference Projects](#13-systems-to-port--reference-projects)
14. [Unscoped / Exploratory Ideas](#14-unscoped--exploratory-ideas)

**Newly detailed concepts:** [Diablo-style world loot](#diablo-style-physical-loot-drops--loot-beams) · [Deployable camps & Garrisons](#deployable-camps--garrisons) · [New gear tiers](#new-item-quality-tiers) · [The Living Inn character select](#character-selection-the-living-inn) · [Nat Pagle: Fishing Challenges & Bounties](#nat-pagle--fishing-challenges-bounties--unique-rewards) · [Fictional Drugs / Chems](#fictional-drugs--riskreward-consumables) · [Gambling, Casinos & Lottery](#gambling-casinos--gold-wagering-minigames)

**November 2026 idea additions:** [Cooperative rituals & spell forging](#cooperative-super-spells--group-rituals) · [Player-steered ships](#traversable-ocean--player-controlled-ships) · [Crime & bounty hunting](#crime-notoriety--player-bounties) · [Player contracts & Dungeon Forge](#player-created-contract-boards) · [Player-run NPC jobs](#player-run-jobs--npc-role-replacement--fivem-inspiration) · [Combat pet genetics & breeding](#combat-pet-genetics--individual-values-effort--breeding) · [Rentable alternate-character bots](#rent-your-alternate-characters-as-player-hired-bots) · [Dynamic weather & snow](#dynamic-snow-accumulation-across-azeroth).

---

## 1. Client, UI & Integrations

### Client / Engine Upgrades

- **32-bit limit removal / upgrade**
  - Uncap the amount of gold a player can carry.
  - Remove 32-bit-related limits on health, resources, armor, strength, and other stats.
  - **Goal:** Avoid 32-bit limits altogether.
- **Native controller support.**
- **Mobile client.**

### Character Selection: The Living Inn

> **Core concept:** Replace the static character-selection backdrop with a **living, animated inn** where *all of the account's characters* appear to be spending time together between adventures. Think of it as a **living fish tank** of your characters: the room continues to feel alive even when the player is not interacting with the menu.

#### The Inn & Ambient Atmosphere

- Load a fully rendered, explorable-looking **inn interior** as the character-selection scene, with a bar, tables, chairs, fireplace, doors, and other Warcraft-themed details.
- Populate the inn with the player's existing characters as visible, individually recognizable 3D figures—not just portraits or a single character standing in front of a backdrop.
- Use each character's **saved race, appearance, equipped gear/transmog where supported, and other eligible visual customizations**. This is a display of the roster, not a change to the actual characters or their logged-out locations.
- Keep the scene active while the character list is open: characters move between social spots, chat, emote, eat, drink, relax, and generally behave like adventurers waiting for the next session.
- Add layered inn ambience: fireplace crackling, clinking mugs, low conversation, footsteps, occasional laughter, and appropriate background music.
- Provide enough usable locations and animation variations for both small and large rosters; characters without an available table seat can stand, lean, or mingle.
- Treat the inn as a **presentation scene**, not a shared in-game location: characters are not actually online, consuming inventory items, gaining rewards, or changing their world positions.

#### Autonomous Character Behavior (The Fish Tank)

- Give each displayed character a simple **ambient activity controller** that selects believable actions and destinations:
  - Walk around the inn and pause near points of interest.
  - Sit down at tables or at the bar, then stand up when changing activities.
  - Drink from a mug, eat a meal, or idle with a relaxed pose.
  - Converse with another character, face them, and perform complementary talk/listen, laugh, nod, or gesture animations.
  - Wave, salute, cheer, read, stretch, warm up by the fire, or play other race-appropriate emotes.
- Allow occasional **paired or group interactions** so the characters appear aware of each other rather than performing unrelated loops.
- Use weighted random behavior, varied animation timings, and short pauses to prevent the room from feeling synchronized or repetitive.
- Coordinate movement through predefined routes/interaction points or a scene navigation mesh; avoid characters walking through tables, other characters, or the camera.
- Favor personality through visual staging and varied emotes. Any flavor dialogue is **noncanonical ambience**, not simulated real player chat or actual actions taken by the character.
- On returning to character selection, the inn can start in a different believable arrangement rather than resetting every character to an identical pose.

#### Character Selection & Cinematic Focus

- Retain a clear, scrollable **character list** with name, level, class/archetype, and other existing character details. The inn remains visible behind or beside the list.
- **When a character is highlighted/selected:**
  1. Identify that character wherever they currently are in the inn and visually emphasize them.
  2. Smoothly **pan/dolly the camera** to frame them, even if they were across the room or sitting at a table.
  3. Interrupt their current ambient behavior cleanly. If seated, they **finish standing up**; if walking, they stop at a safe point.
  4. Have them **turn to face the camera/player**.
  5. Play a clear, character-appropriate **salute** as the signature selection gesture.
  6. Hold a pleasant, readable hero pose while the character remains selected; optionally return to a subtle idle after the salute.
- Selecting a different character releases the previous one back into the ambient scene and repeats this sequence for the newly selected character.
- Ensure the focus camera does not clip through furniture or obscure the selected character; use fallback camera anchors for crowded spots.
- Support mouse, keyboard, and controller navigation through the same selection-and-focus behavior.
- **Selection is not login:** merely highlighting a character should never enter the game. Login still requires the player's explicit Play/Enter World action (or the existing equivalent).

#### Enter World Transition

- Once the player confirms **Enter World**, transition from the selected character's salute/hero pose into the game using the smoothest feasible camera or visual handoff.
- The actual playable character must spawn at their **real saved world location**, not at the inn. The inn is only the menu presentation.
- Where a seamless camera transition is not technically feasible between the menu scene and the saved location, use a short thematic transition or loading presentation rather than implying a literal spatial move from the inn.
- Preserve the earlier **Live Azeroth Map** concept as an *optional future transition*: a stylized map could briefly highlight the character's saved location between the inn and entering the world. It is **not** the default character-selection scene.

#### Character Roster, Pets & Optional Polish

- Display every eligible character on the account, while gracefully handling high character counts through staging/visibility rules so the scene remains readable and performant.
- Consider optional appearances by a character's favorite companion pet, hunter/warlock pet, or **Journey Companion** if those systems can safely supply display-only models; do not require them for the first implementation.
- Consider visually distinct inn themes or cosmetic ambience presets in a later phase; keep a single dependable default inn for the first release.
- Cross-faction rosters should be supported in a **neutral presentation inn** rather than prevented from appearing together by in-world faction rules.
- Optional touches: subtle nameplates on hover, a portrait or character-details card while focused, lighting that draws attention to the selected character, and contextual idle sounds.

#### Reactive Inn: Account Memory, Spirits, Pets & Customization

Let the character-selection inn feel like an evolving record of the player's adventures—not just a randomized animation loop.

- **Account accomplishments:** Reflect earned achievements or major milestones with eligible trophies, statues, banners, or keepsakes inside the inn. For example, an achievement could place a statue in a corner or a trophy above the fireplace.
- **Character celebrations:** Characters who recently reached maximum level, became Grand Master in a profession, or achieved another significant milestone can receive a short, contextual celebration from the other displayed characters.
- **Ghostly dead characters:** When a roster character's saved in-world state is dead, render that character in an appropriate translucent/ghost presentation in the inn instead of portraying them as alive. Do not resurrect or otherwise modify their real character state.
- **Tamed pets:** Allow a displayed character to appear with their currently selected/tamed combat pet; where supported, show the pet resting, accompanying its master, or performing harmless ambient behavior.
- **Companion pets:** Allow selected noncombat companions to wander, sleep, or interact with inn furniture. Limit the total number on display for performance and crowding.
- **Customizable inn interior:** Let players personalize the inn with unlocked themes, furniture arrangements, lighting, decorations, trophies, and other eligible visual options. Treat the inn as a display-only customization layer rather than an actual housing inventory or world plot.
- Respect player-configured visibility, animation intensity, and accessibility preferences; avoid placing important character selection controls behind cosmetic objects.

> **Progression boundary:** Displayed milestones and inventory-dependent cosmetics must come from authoritative account/character records. The inn must never award achievements, consume items, spawn live pets, or let cosmetic customization alter saved world data.

#### Technical / Implementation Boundaries

- This is a **custom 3D character-select scene and UI feature**, not ordinary stock AzerothCore 3.3.5a behavior; expect client rendering, animation, scene-camera, UI, and roster-appearance integration work.
- The server remains authoritative for roster data and login. Do not create actual simultaneously logged-in player entities for characters merely displayed in the inn.
- Build the scene around a small activity-state machine (for example: `Walking`, `Socializing`, `Seated`, `Eating`, `Drinking`, `Focused`, `Saluting`) with clean transitions and cancellation when selection changes.
- Selection must preempt ambient animation; movement/seat occupancy should recover safely when a focused character leaves or returns.
- Stream/cache character appearances where feasible, limit expensive background updates, and include performance settings for lower-end clients.
- Provide a robust **static-character or simplified-inn fallback** if scene assets, animation support, or 3D initialization fail.
- Respect loading, disconnected, deleted, and newly created character states; never expose another account's character data.

**Desired experience:** Opening Esteria feels like walking into the inn where all your adventurers hang out. You see them joking, eating, and relaxing. Click one, the camera finds them, they stand or stop, turn toward you, **salute**, and await your decision to enter Azeroth.

### Server-Driven Item Definitions — Reduce Item Cache Dependency
Explore removing the 3.3.5a client's reliance on a persistent, manually refreshed **item cache** by resolving item templates and descriptions directly from the Esteria server.

- Request item data from the server when an item is first encountered or its definition is missing, rather than depending on outdated local cache files or client restarts.
- Support live updates to custom item names, tooltips, quality tiers, visuals, and server-defined attributes after an item template changes.
- Prefer **versioned requests, invalidation messages, and bounded client-side memory caching** over continuously polling every item on every frame; a server-polling fallback can be used when push invalidation is unavailable.
- Preserve responsive item links, inventory views, inspection, vendors, and the Auction House when the connection is slow or temporarily interrupted.
- Prevent one client's cached item data from becoming authoritative for item stats, ownership, or trades.

> **Technical investigation:** Identify which client systems assume `WDB` / item-cache persistence and which need protocol or rendering changes. The target is a **server-authoritative, automatically refreshed catalog**, not a performance-damaging stream of redundant requests.

### Built-in Addon Repository
- Add an in-game addon browser accessible from character selection.
- Connect the browser to a GitHub repository of addons.
- Provide:
  - Category tabs.
  - Search functionality.
  - Click-to-install addon flow, including a confirmation prompt.
  - Real-time download/installation and Lua refresh so the addon is enabled and ready to use.
  - The ability to fully uninstall browser-installed addons from the default addon window.
- **Preserve** conventional manual addon installation.

### Animated Item Tooltips & Rarity Borders
Upgrade item tooltips so inspecting gear feels more rewarding, especially for new item qualities and rare drops.

- Add **rarity-specific borders, frames, glow effects, and subtle animations** to item tooltips.
- Give special-quality items distinctive presentation without obscuring item names, stats, requirements, or comparison text.
- Support optional animated accents, particles, or a 3D item preview where the client can render them reliably.
- Connect the style definitions to the existing qualities and the proposed **Cosmetic, Cosmic, and Astral** tiers (see [New Item Quality Tiers](#new-item-quality-tiers)).
- Provide **reduced-motion / disable-animation settings** for accessibility and lower-end hardware.

> **Implementation boundary:** Tooltip styling is client-side; item quality and actual item properties remain server-authoritative. New visual effects must not require custom addons to read an item correctly.

### Animated 3D Equipment Effects

Give equipped armor, weapons, and exceptional accessories **visible 3D effects attached to the character**, beyond standard enchant glows.

- Examples include hovering magical spheres, orbiting runes, floating relic shards, animated halos, wisps, miniature constellations, or other effects positioned relative to a character's equipment.
- Support attachment points, positional offsets, animation loops, and optional reactions to combat, emotes, or spell casting.
- Let the item definition determine its effect, so other nearby players see the same eligible visuals without requiring a custom addon.
- Integrate effects with Cosmetic, Cosmic, Astral, cursed, sentient, and Artifact-style equipment where appropriate.
- Add clutter controls, effect-quality settings, and reduced-motion options to preserve visibility and performance in groups.

> These are item-linked **visual attachments** unless an associated item explicitly defines a separate server-validated gameplay effect.

### DragonUI & Classless Resources

- Integrate classless resource bars natively into DragonUI:
  - Mana.
  - Energy.
  - Rage.

### Proximity Voice Chat

- **Addon settings:**
  - Audio device.
  - Audio quality.
  - Push-to-talk (PTT), toggle, always-on, or voice detection.
  - Rebindable PTT/toggle keys.
  - Audience/access controls: everyone, faction, party, guild, friends, or off.
- Display a **speaking indicator** above the speaking character.
  - Also show the speaker a live indicator with an audio visualizer bar.
- Players with compatible access settings can hear one another.
- Spatial volume scales by distance: louder when nearby, quieter farther away.

### Fortnite Dance Emotes — Sound Integration

- Add synchronized **music and sound effects** to the Fortnite-inspired dance emote animations already available or being ported into Esteria.
- Map each dance to an appropriate track or sound cue, with server-visible emote triggers and local audio playback.
- Start, stop, and loop audio in time with the corresponding animation; cancel both when the emote ends, movement interrupts it, or a new emote begins.
- Treat nearby players as optional spatial-audio listeners, with distance falloff and a separate **mute emote music** setting.
- Use properly licensed, original, or otherwise authorized audio rather than assuming that music from Fortnite can be redistributed.

### Discord Integration

- Create a **two-way Discord bridge** for in-game world chat.

---

## 2. Character Creation & Identity

### Character Creation Overhaul

- Experience-rate selection (possibly alongside a scaling toggle).
- Challenge modes.

### Character Biography

- Add an **optional Biography screen** during character creation; players may leave it blank or skip it.
- Fields:
  - Birth city.
  - Parents' names.
  - Background (e.g., Soldier, Urchin, Apostle, Trader).
  - Age.
  - Faith.
  - Story: up to **2,048 characters** of custom character backstory.
- Add **Biography** to the portrait right-click menu for other players.
- Open a polished, retail-like character profile with the stored details, a 3D portrait, and a 3D model.
- Allow profiles to feature optional extras, such as:
  - Achievements and location.
  - Favorite mounts.
  - Favorite companion pets, hunter pets, warlock demons, or Pokémon.

### Custom Titles & Name Colors

- Let players set custom titles in real time.
  - Support **prefix** and **suffix** titles.
- Allow customization of nameplate name color, title color, and guild-name color.
- Make these customizations unlockable with gold.

### New Starting Zones

- Naga starting zone.
- Tuskarr starting zone.
- Troll starting zone.
- Goblin starting zone.
- Worgen starting zone.
- Investigate later-expansion cores for extractable starting-zone data/maps, including:
  - Allied races (e.g., Pandaren).
  - Skyborne.

---

## 3. Classes, Progression & Scaling

### Classless Builds & Archetypes

- Support **multiple saved build loadouts** in the classless system.
- Add stock WoW and **CoA** classes as selectable **Archetypes**.
- Add the ability to **save and share builds** directly from the character advancement screen:
  - Export a build as a code.
  - Upload builds to the server.
  - Browse shared builds through an in-game server browser.

### Character Scaling Options

- During character creation, offer:
  - Item scaling.
  - World scaling.

### Combat, Class & Resource Investigations

- Balance all **CoA abilities and talents** for level 80.
- Investigate UI and client integration for new custom CoA resources.
- Investigate why classless characters are labeled **Paladin**; consider **Hero** instead.
- Finish **Centaur and Ethereal racials**.
  - Make use of the Ethereal afterimage effect.
- Integrate **CoA Manastorm** in its entirety.
- Consider CoA-related systems and tuning:
  - Challenges and dungeon difficulty.
  - Manastorm.
  - Bazaar.
  - Item scaling.
  - Mystic enchants.
  - Warcraft Reborn **Hero** classes and spell twins.
  - Wildcard cards.
  - Prestige.
  - XP hotspots and tuning multipliers.

### Persistent Combat Stealth — Toggleable Ability

Introduce an ability that lets a character **remain stealthed while attacking**, rather than having the first offensive action automatically break stealth.

- Make it a **toggleable combat stance / aura** with a clear buff icon, status indicator, and activation/deactivation control.
- While active, eligible damaging abilities and attacks do not remove the stance's stealth effect. Define which spells, area effects, objectives, and interactions should override it.
- Balance the advantage with a **continuous health drain while toggled on** (for example, a configurable percentage of maximum health per second); final cost, cooldown, and unlock method are **TBD**.
- Decide whether the drain can reduce health to zero or automatically deactivates at a minimum-health threshold.
- Keep detection rules, line of sight, damage attribution, threat, and reveal effects functional so this does not grant invulnerability or untargetable damage.
- Consider distinct PvE/PvP tuning, especially in battlegrounds, arenas, and rotating Wilderness zones.

> **Implementation boundary:** Stealth state, attack permissions, health costs, and PvP interactions must be evaluated **server-side**; a purely cosmetic invisible character is not sufficient.

### Cooperative Super-Spells & Group Rituals

Allow two or more players to **combine coordinated spells into a new effect** that none could cast alone. Larger rituals become social, tactical encounters of their own.

| Combination | Example combined result |
| --- | --- |
| Fire + Wind | **Firestorm** — a sustained or spreading area attack |
| Frost + Water | **Frozen Battlefield** — a wide icy zone with movement/control effects |
| Holy + Shadow | **Twilight Nova** — a hybrid burst with an unusual light/dark effect |
| Three Warlocks channeling | **Demonic Monstrosity** — a temporary summoned creature |
| Five Mages channeling | **Arcane Bridge** — a temporary traversable crossing over a ravine |

- Support spell-pair combinations, multi-caster channels, and elaborate **ritual circles** requiring players to occupy positions, keep channeling, and defend against attacks.
- Show what each participant contributes, their remaining channel time, required proximity, and whether the group has satisfied the spell's conditions.
- Specify interruption, disconnect, failure, reagent, cooldown, and player-count rules. Failed rituals should not create invisible or orphaned effects.
- Choose whether recipes are discovered through exploration, professions, FATE progression, or other unlock paths.
- Apply sensible PvE/PvP balance limits; collaborative power should not bypass encounter, movement, or map restrictions.

> **Implementation dependency:** Cooperative casting needs synchronized server-side ritual state and a custom client presentation. It is more than two ordinary casts happening at the same time.

### Spell Forging — Player-Designed Abilities

Give classless characters a **spell workshop** for assembling their own abilities from approved components, making buildcraft feel experimental rather than limited to predetermined spell lists.

- Combine interchangeable **projectiles, beams, traps, elements, delivery methods, secondary effects, and activation conditions**.
- Every component consumes part of a finite **power budget**. More ambitious designs need additional investment, trade-offs, longer cooldowns, or limitations.
- Provide an editor with a live summary of expected damage/control/utility, reagent costs, targeting, cast time, cooldown, and final appearance.
- Let players save named spell templates, equip a limited set to their builds, and optionally share blueprint codes without transferring unauthorized unlocks.
- Validate all component combinations and final calculations server-side; prohibit arbitrary scripts, infinite loops, unrestricted summons, or limitless movement/teleport effects.
- Consider spell-forging discoveries as a progression track tied to Paths of FATE, monster abilities, and character archetypes, while retaining clear balancing controls.

> **Design decision:** Determine how crafted spells consume available classless slots, FATE points, or another capacity budget before exposing unrestricted combinations.

### Monster Ability Harvesting

Turn creature hunting into a distinct progression activity in which characters can **study and learn a limited selection of monster abilities**.

- Example unlocks: a **Basilisk's Petrifying Gaze**, a **Nerubian's Web Snare**, or a limited **Dragon Breath** attack.
- Require an eligible encounter, observation, special study action, rare component, or achievement rather than granting every ability from merely killing a creature.
- Use the existing **Pet/Creature Codex** idea to catalog which species can teach abilities, where they appear, and the player's research progress.
- Equip only a limited number of monster abilities at once; use **FATE points or a separate capacity pool** so one character cannot freely combine every harvested power.
- Define player-size, target, cooldown, and PvP limitations for abilities originally designed for NPC encounters.
- Keep harvested player abilities distinct from the creature's own NPC spell template so patches to monsters do not unpredictably alter player builds.

### Elemental Physics & Spell-Environment Interactions

Make spellcasting respond to the immediate environment, creating tactical moments with **temporary, localized changes**.

- Rain wets terrain; Frost can freeze puddles or water surfaces; Lightning can electrify water; Fire can ignite flammable oil; Wind can redirect eligible gas clouds or projectiles.
- A Mage could freeze a stretch of river into a crossing; an enemy Shaman could shatter that ice while the party traverses it.
- Define a small vocabulary of server-recognized surface states (such as `Wet`, `Frozen`, `Burning`, `Electrified`) and explicit interaction rules.
- Keep dangerous reactions bounded by duration, area, encounter context, and performance budget. Avoid permanently editing continent terrain or destructively changing shared quest geometry.
- Make spell interactions readable through effects, audio, and clear warnings, with reduced-effects fallbacks when possible.

> **Engineering note:** A full general-purpose physics simulation is not required. Begin with authored terrain/surface interactions and approved dynamic objects, then expand only where the client and server can reliably agree on collision and damage.

### Legion-Style Artifact Weapon Progression

Explore adapting **Legion Artifact Weapons** into Esteria's level-80 and classless progression model.

- Obtain distinctive named weapons through questlines, class/archetype challenges, raids, or long-term discoveries.
- Unlock a weapon-specific progression tree with active or passive bonuses, visual changes, artifact appearances, and optional ability modifiers.
- Respect original Artifact-themed identity where it fits, while deciding how talents adapt to custom classes, build loadouts, and freely traded equipment.
- Clarify whether progress follows **the physical weapon**, a specific character, or account unlocks—especially important because Esteria plans to remove Soulbound restrictions.
- Place bounds on upgrade power, catch-up paths, and compatibility with new Cosmetic/Cosmic/Astral item tiers.

> **Exploratory port:** Retail Artifact data and mechanics are not assumed to work unchanged in a customized 3.3.5a client.

### Account-wide Progression

- Make **all reputation account-wide**.

### Tradable Reputation Tokens

Allow players to **withdraw earned reputation** into an itemized token that can be traded, mailed, or sold and then redeemed by another player.

- Token creation removes the specified reputation amount from the creator; redemption credits that same amount to the recipient for the designated faction.
- Show faction, reputation amount, restrictions, and creator information in the token's tooltip.
- Prevent players from withdrawing below permitted standing floors, creating negative or invalid faction standing, or granting rep with ineligible factions.
- Creation and redemption must be **atomic** to prevent duplicated reputation when transactions, mail, or character transfers fail.
- **Important interaction with account-wide reputation:** Define whether withdrawal/redeeming changes a shared account ledger or a character ledger. The source account must lose the credited amount exactly once; its alternate characters must not retain a duplicated balance.
- Decide whether reputation rank gates, achievements, and unlocks are recalculated when standing falls after a withdrawal.
- Allow players to now continue to grow their reputation passed the maximum to bank 'extra' reputation.

> The intent is **real transfer of earned reputation**, not creation of free reputation or cosmetic token copies.

### Tome of Knowledge

- An item that grants bonus experience on use. Optional variant that offers limited time exp boost.
- Proposed drop rates:
  - **Very low:** Open-world drops.
  - **Low:** Dungeon bosses.
  - **Medium:** Raid bosses.

### Sit Means Rest

- Sitting immediately begins health regeneration, whether via the **X** key, `/sit`, or sitting on furniture.
- Remaining seated for long enough begins generating rested XP at a very slow rate.

---

## 4. Travel, Exploration & World Events

### Waystones / Gateways

- Replace the Waystone icon with the **Esteria icon**.
- Build a **teleport taxi service** using Waystones/Gateways.

### Traversable Ocean & Player-Controlled Ships

Connect **Eastern Kingdoms and Kalimdor** through an ocean players can physically traverse, with **player-steered ships** replacing the need to rely exclusively on scripted ferries.

- Let captains manually control steering, travel speed, and navigation while passengers remain aboard and can move around safe deck areas.
- Introduce suitable ship classes—from small vessels to larger guild/group craft—with permissions for captains, crew, and passengers.
- Support voyages, ports, open-water landmarks, storms, hazards, pirates, and ocean encounters that turn travel into an actual activity.
- Keep conventional ferry services available as accessible or lower-effort alternatives unless explicitly removed by a later design decision.
- Plan for ocean travel between continent/map boundaries; if the existing world geometry cannot form a seamless continuous ocean, research custom map work and a convincing server-coordinated crossing/loading transition.
- Handle disconnections, ship ownership, boarding, falling overboard, combat, relog locations, and vehicles carrying multiple characters without duplication or lost passengers.

> **Technical reality check:** A truly continuous navigable ocean is a **world-map, client streaming, vehicle, and network synchronization project**, not a simple replacement for a taxi path. Preserve the full ambition while evaluating seamless versus transitional navigation.

### Mount Bonding & Individual Talent Trees

Reward repeated use of a favorite mount with an individual **bond/proficiency level** and unlockable mount talents.

- Gain bond experience by riding **that specific mount**, not from unrelated mounts or AFK standing still.
- Give each mount its own talent point progression and configurable tree of utility, traversal, or cosmetic bonuses.
- Possible perks include improved handling, stamina, terrain behavior, safe passenger seating, special emotes, or appearance effects, subject to PvP and travel balance.
- Show bond progress, unlocked traits, and respec choices in a dedicated mount collection interface.
- Track the progression per owned mount identity and define what happens when a mount is shared, traded, or summoned through a differently named item.

### Multi-Passenger "Bus" Mounts

- Add large mounts or rideable vehicles with **a driver plus five or more passengers**.
- Passengers occupy real synchronized seats, can board/exit through interaction, and travel with the driver rather than teleporting alongside them.
- Include themed variants such as wagons, large creatures, magical conveyances, or guild transports.
- Support safe mounting, dismounting, combat restrictions, logout handling, companion seating, and terrain validation.
- Integrate with the Journey Companion system and other supported multi-seat mount mechanics.

### Buildable, Pilotable Siege Engines

- Allow players and guilds to **construct and operate siege vehicles**, inspired by the responsive, player-directed movement of Dragonflight-style dragon controls rather than static scripted artillery.
- Consider tanks, battering rams, cannons, mobile towers, and fantasy siege mounts with their own handling, passenger seats, attacks, durability, and repair costs.
- Make crafting and deployment consume real resources and obey placement or event restrictions.
- Support driver/gunner roles and meaningful steering/movement controls within the capabilities of the customized client.
- Define where siege engines can be used (such as faction wars, open-world events, or approved PvP zones) to avoid blocking quest hubs or trivializing ordinary encounters.

### Retail Toys & Traversal Gadgets

- Research porting selected retail toy functionality, beginning with the **Hang Glider** and **Gnomish Gravity Well**.
- Preserve their recognizable movement/physics fantasy while adapting interactions to 3.3.5a movement, collision, and anti-cheat systems.
- Determine cooldowns, acquisition sources, and prohibited zones so toys do not bypass encounter boundaries or create unintended flight exploits.

### Flightmaster Whistle

- Add a Flightmaster Whistle system or item.

### Roaming Beasts & Bosses

- Spawn powerful hostile creatures across **more than `X` possible locations** in Azeroth.
- Creatures randomly roam after spawning, making the open world less predictable.
- Distinguishing visual cues:
  - Larger creature models.
  - Visible aura.
  - Hostile disposition.
- Scale their levels roughly to the zone average, with some variation above/below it.
- Allow drops of equipment and recipes, at substantially lower rates than comparable dungeon rewards.

### Adaptive Enemies — Persistent Battlefield Ranks

Allow individual hostile NPCs to **learn from victories**: when they defeat a player or another eligible NPC, they can rise in rank and become more formidable until someone finally kills them.

1. **Private**
2. **Corporal**
3. **Sergeant**
4. **Lieutenant**
5. **General**
6. **Warlord**

- Each promotion increases the NPC's relevant stats, combat threat, and potential loot quantity or rarity.
- Change the NPC's **name color/rank presentation** so adventurers can recognize a veteran enemy before attacking.
- Persist the upgraded NPC's rank and state across server restarts; the accumulated rank remains until the creature dies.
- After the ranked NPC dies, its eventual replacement **respawns at the standard starting rank**, rather than inheriting the previous life’s progression.
- Distinguish real victories from staged deaths, allied NPC loops, summoned minions, or intentional farming; cap growth and reward generation appropriately.
- Consider special titles or world-map rumors for unusually high-rank enemies, linking the concept to roaming bosses and hunting contracts.

> **State model:** Rank belongs to a **specific living spawn instance**, not permanently to every NPC sharing the same creature template.

### Traveling Caravans

- Caravans travel the world with guards.
- Sell basic items.
- Can be attacked.

### Traveling Merchants

- Roaming merchants that **cannot** be attacked.
- Sell exclusive merchandise.

### Random World Encounters

- Bounty hunters.
- Assassins.
- Camps.
- Monsters (beasts/demons).
- Roaming bosses.

### Random Zone-Wide Events & World Conditions

Temporarily transform eligible zones with unusual environmental events, each with a defined spawn chance, duration, ruleset, and visual announcement.

- **Low Gravity:** For `X` minutes, gravity is reduced in a designated zone; jumps, falls, and certain physics interactions behave differently.
- **Blood Moon:** A rare nighttime event turns the sky red, enlarges and reddens hostile creatures, and grants them temporary stat increases. Pair the increased danger with appropriately balanced reward opportunities.
- Support additional future zone modifiers without treating every anomaly as a permanent weather type.
- Present event boundaries, time remaining, affected mechanics, and opt-in/avoidance options where feasible.
- Prevent overlapping events from producing broken movement, impossible quests, or unbounded difficulty; use explicit stacking and exclusion rules.
- Keep event state server-authoritative and synchronized for all players participating in the same zone or phase.

### Nightfall & Storm Danger

- Make travel and combat **more dangerous after dark** or during sufficiently strong storms, independent of or alongside special Blood Moon events.
- Potential consequences include tougher roaming packs, altered NPC aggression, reduced visibility, hazardous winds, or unique nocturnal enemies.
- Use the zone's validated local time/weather state rather than merely assuming a visual client effect is active for everyone.
- Tie increased danger to discoverable resources, special encounters, or optional rewards without making essential leveling impossible during certain real-world hours.
- Make the danger predictable through clear weather cues, warnings, and safe places to shelter.

### Dynamic Snow Accumulation Across Azeroth

- Let **snow visibly accumulate wherever it is actually snowing**, not only in world zones that already have permanent snow geometry.
- Build temporary snow coverage on eligible roofs, ground surfaces, props, vegetation, and buildings regardless of a zone's usual climate.
- Scale accumulation by snowfall intensity/duration and let it fade or melt when the weather changes; avoid permanently editing terrain files.
- Prioritize appropriate shader/material overlays and surface rules, with distance-based rendering and graphical quality options.
- Prevent accumulated snow from inadvertently changing collision, character paths, gathering nodes, or PvP visibility unless separate mechanics explicitly require it.

> **Client dependency:** Accumulation on arbitrary existing world surfaces will need renderer/material work; a simple change to the weather particle system is not enough.

### The Spirit World — Gameplay After Death

Instead of death being only a grayscale run to a corpse, introduce an **optional parallel spirit realm** with content that living characters cannot ordinarily see or access.

- Dead players enter a ghostly presentation of the familiar world and can encounter **spirit-only NPCs**, hidden passages, strange landmarks, or new questlines.
- Offer quests involving the recovery of **lost memories** and exploration of the stories behind particular places or characters.
- Add hostile spirits that hunt wandering souls and meaningful but bounded risks to spirit-form exploration.
- Create puzzles requiring cooperation between **one living player and one dead player**, each interacting with unique objects in their own state.
- Preserve standard graveyard/corpse resurrection as an option; spirit-realm participation is not mandatory to revive.
- Prevent ghost-only quests from trapping characters, bypassing PvP deaths, duplicating rewards, or entering inaccessible map locations.

> **Technical boundary:** Spirit-only NPC visibility, interactions, puzzles, and phase state require explicit client/server rules; the existing ghost visual effect alone will not create this new gameplay layer.

### Faction Wars

- Add faction wars occurring across the open world.

### Camping & Survival

- Hunger and thirst.
- Temperature.
- Disease and sickness.

---

## 5. PvP, Factions & Wilderness

### Gold Duels

- When a player selects **Duel** from another player's portrait menu, present two options:
  1. Standard duel.
  2. Gold duel.
- For a gold duel, let the challenger enter the gold wager - if the challengee accepts they must match the wager to add to the pot.
- Award the pot gold to the winner when the duel finishes.

### RuneScape-style Wilderness Zones

- Randomly choose **`X` high-level zones** and designate them as Wilderness zones for **`Y` hours**.
- During that window:
  - Force PvP on for anyone inside the zone.
  - Make all players hostile to one another **regardless of faction** (e.g., Alliance vs. Alliance).
  - On death, spawn a loot pouch at the player's corpse containing some of their gold, equipped gear, and inventory items.
    - The owner can loot the pouch immediately.
    - Other players can loot it after **`X` seconds/minutes**.
    - Unrecovered pouch contents get put into a unique Bloody Auction House, where unrecovered bag contents are placed for a cost
  - Increase XP, gold, reputation, and honor gains.
  - Award a small amount of arena points alongside honor for honorable kills.
  - Increase enemy power in the zone.
  - Give **Freeborn** higher honor/arena-point payouts and cause their player kills to drop more gold than those of other factions.
  - **Disable corpse-site revival** while inside the Wilderness zone.

---

### Crime, Notoriety & Player Bounties

Introduce an **outlaw/criminal system** layered over open-world PvP, with escalating notoriety, public manhunts, criminal-only vendors, and player-funded bounties.

#### Pickpocketing & Theft

- Let players attempt to **pickpocket gold from another player**, with a success calculation, restrictions, and a **per-target cooldown** to prevent repeat harassment of the same victim.
- **Original proposed penalty:** A pickpocket attempt forcibly enables the thief's PvP flag and **locks it on for 30 real-world days**. Keep this rule as an explicit design proposal; determine exceptions and whether such a long lock is workable before implementation.
- Notify the victim when theft succeeds or fails; place a visible marker over the thief to expose them to witnesses or pursuers.
- Inside active **Wilderness zones**, successful pickpockets also have a small chance to steal eligible **inventory items**, in addition to gold.
- Specify protected items, no-steal conditions, transfer caps, cooldowns, inventory constraints, failure behavior, and server-side ownership validation.

#### Crimes, Murder & Notoriety

- Raise a character's criminal **notoriety** as qualifying crimes accumulate, with the degree tied to crime severity.
- Count kills of other players in **open-world PvP** as **murder**, creating a substantial negative/criminal notoriety change; exclude Battlegrounds and Arenas as requested.
- Clarify self-defense, duels, faction wars, Wilderness rules, mutually consensual combat, repeat-kill farming, and group participation before treating every open-world kill identically.
- Show a criminal's wanted status in appropriate nameplate/inspection UI and display qualifying wanted criminals on both **world map and minimap**, subject to map disclosure/refresh rules.

#### Automatic & Player-Funded Bounties

- Generate an **automatic bounty** after a sufficient amount of crime; scale it with the seriousness or accumulated severity of the criminal's actions.
- Let other players post additional gold bounties on specified characters. **Automatic and player-funded bounties stack** to form the advertised total.
- Award the bounty to the player credited with the **killing blow** against the criminal, preserving that explicit design goal.
- Escrow player-funded bounty gold before listing; prevent repeated self-claims, alts/collusion, staged kills, and cross-account payout exploits.
- Define whether bounties persist across logout, whether criminal death clears notoriety, and how a failed/expired player bounty is refunded.

#### Fences & Criminal Markets

- Add **Fences**: vendors that serve wanted players or those with sufficient criminal standing.
- Sell specialized pickpocketing tools and **stun consumables** (such as an on-use Kidney Shot–style effect), subject to cooldowns and PvP protections.
- Buy collected **player ears** at better-than-normal value, linking crime to the existing Ears trophy/currency system.
- Consider distinctive criminal mounts, armor, contracts, and cosmetic unlocks while preserving fair counterplay for law-abiding players.

> **Safety and economy boundary:** Actual theft of in-game assets can easily become abusive. Treat consent/PvP-zone rules, protected inventories, exploit resistance, and grievance recovery as first-class design decisions without quietly removing the intended outlaw fantasy.

### Ears

- Ala Diablo, killing an enemy player in open world pvp awards the one who landed the killing blow a physical item that is the 'Ear' of the slain player.
- Ears will show the time and date of when the ear was claimed, and who it belongs to
- Ears can be used as currency, or reagents for future crafting systems
- Vendor who sells exclusive armors/mounts, etc for ears

---

## 6. Dungeons, Quests & Challenges

### Adventure Company

- A dedicated dungeon faction offering **rotating contracts at maximum difficulty**.
- Completing contracts earns reputation, unique rewards, and standing with an elite challenge-focused organization.

### Slayer Contracts / Hunter's Guilds

- Introduce Hunter's Guilds with rotating contracts targeting:
  - Creature types and families.
  - Specific zones.
  - Elite targets.
- Include contract streaks, rare encounters, reputation, and exclusive rewards.

### Ad Hoc / Procedural Quests

- Procedurally generated quests.
- Quest board for discovering/accepting them.

### Player-Created Contract Boards

Let players publish **custom contracts** on public or player-owned boards—effectively player-authored quests that others can accept and complete for a reward funded by the creator.

- Contract examples:
  - **Gathering:** Deliver `X` specified resources or crafted items.
  - **Reputation:** Earn or transfer a specified amount of eligible faction reputation.
  - **Escort:** Escort the contract creator or designated character from **Stormwind to Ironforge**, or along another agreed route.
  - **Power-leveling:** Complete agreed dungeon runs or help the client reach a specified level or XP milestone.
- Creators can specify an objective, quantity, prerequisites, time limit, eligibility restrictions, and offered payout.
- Supported payments include **gold, specific items, and reputation**. Gold/items are supplied by the creator in advance; reputation rewards are deducted from the creator through the reputation-transfer system.
- Hold all promised rewards in server-side **escrow** and distribute them only when objective completion is validated.
- Maintain a browser with searchable categories, reputation/trust information, accepted contracts, claim status, and a record of completions or failures.
- Use objective-specific authoritative event tracking for gathering, escorts, dungeon progress, and reputation rather than trusting a free-text completion claim.
- Define cancellation, expired contracts, refunds, partial completion, party sharing, and dispute rules before enabling contracts with valuable rewards.

> **Cross-system opportunity:** Player-run innkeepers, blacksmiths, merchants, quest givers, and resource-gathering jobs can all issue contracts through the same board infrastructure. This complements, rather than replaces, the NPC-generated quest boards.

### Dungeon Sigils — Player-Selected Difficulty Modifiers

Let a party apply a **Sigil to a dungeon before entry** to modify encounter behavior in exchange for explicit reward bonuses.

| Example Sigil | Dungeon modifier | Proposed bonus |
| --- | --- | --- |
| **Sanguine** | All eligible enemies gain `X%` lifesteal | **+20% gold** |
| **Combustible** | Enemies explode on death | **+20% experience** |
| **Multiplying** | Enemies split on death | **+25% reputation** |

- Show a sigil's full modifier, eligible instances, difficulty impact, duration, and reward multipliers before the group confirms entry.
- Decide whether one or multiple sigils may be applied, and provide stacking rules so combinations do not create accidental infinite farming loops.
- Lock the chosen ruleset for the instance run; track which group/instance owns the modifier and how replacement players are handled.
- Scale reward bonuses from **actual qualifying completions/kills**, not simply from activating a sigil, and prevent recursive split mobs from creating unbounded XP or loot.
- Offer collectible sigils, crafting recipes, rare drops, or challenge rewards as possible acquisition sources.

> These are deliberately selected player modifiers; they can coexist with **Adventure Company maximum-difficulty contracts** and should reuse difficulty infrastructure where appropriate.

### Dungeon Forge — Player-Created Adventures

Give players a simplified **in-game level editor** to assemble and share instanced adventures using approved building blocks.

- Select rooms, corridors, decor, enemies, environmental hazards, encounter objectives, and supported scripted event templates from a curated palette.
- Build objectives such as defeat a boss, defend a position, retrieve a relic, survive waves, escort a character, or solve a puzzle.
- Offer preview/testing tools, validator warnings, and resource budgets for enemy counts, object counts, pathfinding, and scripted triggers.
- Publish validated adventures to a **community browser** with ratings, recommended levels, difficulty tags, version history, and leaderboards.
- Let creators update or retire a published map without corrupting existing runs; maintain moderation and reporting mechanisms.
- Reward players with a tightly controlled list of **approved rewards** or progression currencies—never with creator-specified unlimited gold/items.
- Do not allow arbitrary executable scripts, arbitrary NPC templates, unsafe world teleports, or unrestricted item generation in published content.

> **Core promise:** Community creators could eventually provide a constantly expanding collection of custom adventures without needing permanent developer-authored dungeons for every new idea.

### Nat Pagle — Fishing Challenges, Bounties & Unique Rewards

Build a fishing progression loop around **Nat Pagle** as a recognizable fishing mentor, with rotating objectives, rare catches, and rewards beyond ordinary vendor fish. Keep it compatible with baseline Fishing while giving dedicated anglers a reason to explore Azeroth.

#### Fishing Challenges

- Introduce **daily, weekly, and special-event fishing challenges** available from Nat Pagle or associated angler NPCs.
- Rotate challenge objectives across different playstyles:
  - **Regional catches:** Catch named fish in designated lakes, coastlines, rivers, or zones.
  - **Rare specimens:** Land an uncommon or unusually rare fish from an eligible fishing pool.
  - **School fishing:** Catch fish directly from specific fishing schools rather than using purchased items.
  - **Conditions:** Fish during particular weather, time-of-day, or seasonal events **where the server can actually validate those conditions**.
  - **Timed challenges:** Catch an eligible set of fish before a challenge timer expires.
  - **Collection challenges:** Complete a themed set of distinct fish for an Angler's Ledger entry.
- Include beginner, experienced, and **master angler** tiers; scale difficulty through locations, skill requirements, rarity, or objectives rather than raw character damage.
- Show active objectives, progress, eligible locations, remaining time, and reward previews in a compact **Fishing Journal / Angler's Ledger** UI.
- Keep challenge progress when players log out, with clear handling for daily/weekly resets and expired timers.

#### Fishing Bounties & Reputation

- Add a rotating **Fishing Bounty Board** with requests from settlements, chefs, researchers, and other NPCs for particular catches.
- Distinguish **delivery bounties** (eligible fish may be supplied from inventory) from **personal-catch bounties** (the character must catch the fish after accepting the contract).
- Support optional multi-stage expeditions that direct players to new waters, discover rare schools, or catch a legendary specimen.
- Award gold, Fishing skill-related materials, profession resources, and reputation with an angler organization or Nat Pagle's faction where applicable.
- Add milestone ranks, completion streaks **without punitive permanent resets**, and reputation-based access to special contracts.
- Optionally feature a periodic fishing tournament with a defined start/end, clear scoring, and cosmetic recognition for winners.

#### Unique Rewards & Collectibles

- Offer a rotating reward catalog of **exclusive fishing poles, bobbers, lures, tackle boxes, outfits, pets, mounts, toys, titles, and housing decor** such as mounted trophy fish.
- Award **Angler's Ledger achievements** for regional collections, rare catches, total challenges completed, and mastery of different waters.
- Reserve the most distinctive cosmetic prizes for meaningful milestones, while allowing useful fishing supplies to remain accessible to casual players.
- Cross-link trophy fish and fishing-themed furniture to the housing decor acquisition system; actual consumable fish remain real inventory items.

> **Implementation boundary:** Standard 3.3.5a fishing data may not track every proposed condition or trophy attribute. Personal-catch verification, weather/time checks, custom fish sizes, leaderboards, and persistent journals require explicit server-side tracking. Reward eligibility must be validated server-side; merely owning or trading a fish should not satisfy a personal-catch objective.

### Retail Activities to Port

- **Garrisons** — potentially including missions and companions; see the [placeable retail housing + Garrison hybrid](#retail-housing--garrison-hybrid--placeable-garrisons).
- **Torghast**.
- **Mage Tower**.
- **Withered Army Training**.

---

## 7. Economy, Loot & Vendors

### Remove the Soulbound Mechanic

- Remove **Soulbound / Bind on Pickup / Bind on Equip / Bind on Use** behavior as a default item restriction across Esteria.
- Allow players to **trade, mail, sell, auction, and transfer previously bound equipment and eligible collectibles** through the existing economy systems.
- Review legacy binding flags, equip handlers, quest rewards, boss loot, achievements, and imported retail items so they do not silently re-bind items.
- Handle genuinely nontransferable things (for example, quest progress, account entitlements, or character-specific unlock states) through explicit **eligibility / ownership rules**, not a generic Soulbound flag.
- Keep loot ownership and initial pickup permissions separate from post-acquisition item trading; removing Soulbound must not allow players to bypass encounter credit or loot distribution.

### Advanced Crafting — Bespoke, Persistent Items

Let artisans customize the **identity of a crafted item**, creating genuinely distinctive equipment or goods from known recipes.

- Starting from an eligible crafting recipe, give the crafter limited controls over the **item name, written description, visual appearance, and maker's signature**.
- Retain the underlying recipe's required materials, item type, approved stats, and legal appearance options; personalization should not permit arbitrary item powers.
- Save each result as a persistent **individual item instance**, with its custom identity surviving trading, mailing, storage, auction sales, and server restarts until the item is destroyed.
- Display the artisan's signature and optional creation history in the item's tooltip; allow the name/description to be inspected through item links and trade windows.
- Implement moderation, text limits, item-name uniqueness policy, and immutable provenance for signatures where needed.
- Consider related crafting contracts, player-owned blacksmith/leatherworker shops, legendary commissions, and cosmetic quality tiers.

> **Technical dependency:** Per-item metadata must travel with the item instance. Updating only a shared `item_template` row would incorrectly rename every item made from the same recipe.

### New Item Quality Tiers

Extend Esteria's item-quality system with three additional labels and matching visual identities:

| Tier | Proposed role | Presentation |
| --- | --- | --- |
| **Cosmetic** | Fashion, transmog, and appearance-oriented items; generally not a power upgrade | Dedicated color, tooltip border, inventory accent, and loot-beam style |
| **Cosmic** | High-end gear quality above conventional item qualities, with custom progression rules | Distinct quality color, animated frame, and world-drop effect |
| **Astral** | A further exceptional gear quality for especially rare rewards | Unique premium-looking frame, animation, and loot-beam effect |

- Add support to item templates, quality enums, tooltips, item links, bags, chat, vendors, loot windows, and all other quality-aware UI.
- Define **Cosmic and Astral** stat budgets, drop sources, upgrade paths, and relative ordering before balancing the tiers.
- Treat **Cosmetic** as an explicitly defined display quality rather than automatically assigning higher combat stats. Whether it sits in the numerical rarity progression remains **TBD**.
- Ensure the new tiers integrate with [animated tooltips](#animated-item-tooltips--rarity-borders), [Diablo-style physical drops](#diablo-style-physical-loot-drops--loot-beams), loot crates, and the cosmetic shop.
- Audit 3.3.5a client/server assumptions that item qualities stop at existing values; do not repurpose a vanilla quality ID in a way that breaks old items.

### Cursed Equipment — Powerful Rewards with Strange Consequences

Occasionally award **exceptionally rare cursed items** that pair desirable powers with distinctive, sometimes bizarre gameplay drawbacks.

- Example curse mechanics: a weapon grows stronger after consecutive kills but attracts hostile spirits; armor raises defenses but periodically changes the player's movement; a relic grants rare vision while revealing the wearer to special enemies.
- Display enough information for players to understand the curse's key risks without necessarily revealing every narrative secret immediately.
- Add questlines that allow the owner to **tame, transfer, suppress, or deliberately amplify** a curse, creating a meaningful relationship with one prized item.
- Preserve the item's curse state, branching upgrades, and consequences across transfers in accordance with the removal of Soulbound rules.
- Ensure trade windows clearly reveal curses and irreversible decisions; limit abusive PvP, uncontrollable group hazards, and impossible-to-remove penalties.
- Cross-link curses to the Spirit World, Necromancy, rare world bosses, and sentient equipment.

### Sentient Equipment & Talking Weapons

Give selected weapons and armor **personalities, dialogue, and relationships** with their wearers.

- A sword may praise aggressive combat, complain when neglected, react to particular enemy families, or sulk after being replaced by a stronger axe.
- Unlock new dialogue, item lore, cosmetic responses, personal quests, and possibly bounded progression through continued use or major accomplishments.
- Let multiple equipped sentient items occasionally **argue or converse with each other**, using context-aware barks rather than endless repetitive audio.
- Record the object's relevant relationship/progression state with clear rules for trade, sale, and inheritance by a new owner.
- Include mute/text-only settings and cooldowns to prevent dialogue spam; only validated item data should grant gameplay benefits.

> **Relationship to Cursed Items:** A cursed item can also be sentient, but neither system should be a prerequisite for the other.

### Diablo-Style Physical Loot Drops & Loot Beams

Replace the standard **open-corpse-container loot experience** for eligible PvE kills with loot that **bursts outward into the surrounding world**, similar to Diablo.

#### World Drops & Pickup

- On death, roll the creature's loot on the **server** and spawn the resulting items as separate world pickups scattered around the corpse.
- Show **each item as a 3D representation of that specific item**—preferably its existing weapon, armor, consumable, or object model, with a suitable fallback for assets without a world-ready model.
- Add a brief, satisfying **scatter / bounce / land** animation, respecting terrain, slopes, and nearby obstacles.
- Allow players to interact with the physical object to pick up its corresponding item; preserve inventory-full handling, quest eligibility, group loot rights, and anti-duplication protections.
- Allow players to toggle auto-pick up which will automatically magnet the dropped items to them to pick them up, instead of picking them up manually individually.
- Define a sensible despawn/cleanup period and recovery behavior for disconnects or server restarts.

#### Individual Loot Beams

- Give **every separate item its own vertical loot beam** or other distinctive highlight, color-coded by its real rarity or tier.
- Apply special styles for **Cosmetic, Cosmic, and Astral** drops, with adjustable intensity and optional sound cues.
- Offer settings to reduce beam effects, hide common-item beams, or simplify 3D world pickups in crowded combat situations.
- Keep loot readable when many enemies die together by using spacing, clustering/visibility limits, and performance-aware rendering.

> **Scope distinction:** This initially replaces **NPC corpse loot**, not the separate **Wilderness player-death loot pouch** in Section 5. Existing companion/pet auto-loot ideas should target eligible ground pickups instead of trying to open empty corpses. Currency pickup behavior and party roll presentation require an explicit design decision.

### Black Market Auction House

- Sell exclusive mounts as a **gold sink**.

### Loot Crates

- Use as a gold sink: players buy keys with gold to open crates.
- There will be numerous types of crates each with coorresponding keys and potential contents
- There will be premium crates with premium keys that have much higher quality base items
- Most rewards are basic items, with chances at rarer rewards.
- Crate tiers:
  1. Basic.
  2. Rare.
  3. Epic.
  4. Legendary.
  5. Artifact.
  6. Cosmetics
  7. Cosmetic Currency
- Higher tiers have different maximum reward ceilings.
- Allow keys to be traded/sold between players.
- Include an attractive opening animation and exclusive rotating rewards.

### Diablo-style Gambling Vendor

- Rotate available stock **every time the shop window opens**.
- Display an unidentified icon instead of showing the item in advance.
- Increase gold prices as the player spends more that day.
- Possible rewards include basic, rare, epic, and legendary items, mounts, etc.

### Server-Wide Lottery
- Players an buy a ticket for X gold, or multiple tickets
- Players who purchase tickets are recorded on the server, with how many tickets they have
- Gold spent on tickets server-wide is placed into an escrow pool
- Every 30 days a winner is drawn from the ticket holder database
    - When the winner is drawn, announce to the server the winner and their winnings
    - When the winner is drawn, the winner can go to the lottery NPC to redeem their gold
    - When the winner is drawn, the ticket holder table is cleared and the lottery starts over

### Turn Junk into XP
- Generate random zone-specific bounties for gray/junk items.
- Add **Garbage Collector** NPCs that reward XP rather than copper for junk items.
- Add a **FATE perk** that converts junk items directly into XP.

### Universal Cosmetic & Convenience Currency
Create a **single, universal shop currency** for Esteria's cosmetic and convenience offerings rather than maintaining several unrelated balances.

- Use one clearly named currency, preferably **account-wide**, for cosmetics, appearances, mounts, pets, decor, toys, and approved convenience services.
- Connect the **Trading Post** and any overlapping cosmetic / convenience vendors to this same wallet so rewards work consistently across storefronts.
- Let players earn the currency through defined in-game activities and events; whether there are any additional acquisition channels remains **TBD**.
- Show the wallet total, item prices, purchase previews, and transaction history in a unified shop interface.
- Store balances and purchases server-side, validate every debit/credit, and prevent duplicate grants or inconsistent balances across characters.
- Keep **combat power, competitive advantage, and core progression** outside the convenience catalog unless deliberately addressed by a separate balance decision.

> **Design dependency:** Decide how existing Trading Post balances and rewards migrate before replacing its currency; avoid leaving players with unusable earned tokens.

### Trading Post
- Rotate exclusive mounts and cosmetics.
- Integrate its rewards and wallet with the [universal cosmetic & convenience currency](#universal-cosmetic--convenience-currency).
- Earn its currency by participating in:
  - Questing.
  - Dungeons.
  - Raids.
  - PvP.

### Chinese Worldbreaker Vendors
- Add **whelping vendors**.

### Fictional Drugs / Risk–Reward Consumables
Introduce **fictional drugs or chems**, inspired by the tradeoffs of *Skyrim* and *Fallout*, as a distinct consumable category: stronger short-term benefits than ordinary convenience items, but with **predictable drawbacks, tolerance, and potential addiction**. These are game mechanics, not real-world substances or recipes.

#### Consumable Types & Effects

| Example Esteria item | Inspiration | Temporary benefit | Drawback / crash |
| --- | --- | --- | --- |
| **Moon-Dust Elixir** | Skooma-style stimulant | Increased movement speed and resource regeneration | Reduced stamina/defenses or a short sluggishness effect afterward |
| **Quickstep Tonic** | Jet-style chem | Brief personal haste or reduced cast time | Post-effect fatigue, lowered regeneration, or temporary vulnerability |
| **War-Rage Serum** | Psycho-style combat drug | Increased damage or critical-strike output | Lower armor/resistances, reduced healing received, or a stronger comedown |
| **Dreamleaf Draught** | Calming or restorative substance | Increased recovery or reduced incoming stress effects | Slower movement or diminished damage output while active |

- Create multiple **strength and rarity tiers**, with stronger versions trading higher impact for longer cooldowns or greater side effects.
- Define **duration, stacking rules, cooldowns, and crashes** in item tooltips so players know the cost before use.
- Add visible effects, appropriate animations, and character aura indicators without obscuring normal combat information.
- Keep gameplay effects **character-local**: a Jet-like product may apply haste, but must not slow down the world or other players on a multiplayer server.

#### Addiction, Tolerance & Withdrawal

- Track repeated use by **substance family**, not through an unexplained random debuff.
- Frequent use may build **tolerance**, shortening the benefit or requiring a longer recovery interval before full effectiveness returns.
- An optional **addiction / dependency state** introduces temporary withdrawal penalties after excessive use, such as reduced regeneration, weaker stats, or increased cooldowns.
- Allow recovery through time away from the substance, healer/NPC treatment, or game-defined remedies. Avoid permanent, inescapable penalties.
- Make the player-facing UI explain current tolerance, dependency, the expected drawback, and how to recover.
- Persist relevant states and cooldowns across logout, character changes, and restarts to prevent trivial reset exploits; handle offline recovery consistently.

#### Crafting, Discovery & New Profession

- Introduce a dedicated **Chemistry / Apothecary profession**, separate from ordinary Alchemy or as a deliberate specialization if profession-slot limits make that preferable.
- Allow players to discover recipes from quests, hidden laboratories, rare drops, faction rewards, and travelling merchants.
- Source **fictional reagents** from gathering, world loot, creature drops, and specialist vendors; do not require real-world drug-making formulas.
- Craft weaker consumables early in the profession, unlocking more specialized formulas, safer versions, and withdrawal remedies at higher skill.
- Scatter limited quantities of finished consumables through **dungeons, caches, bandit camps, world events, and unusual vendors**.
- Permit trading or auctioning where appropriate, with clear binding rules and safeguards against duplicated inventory or recipe rewards.

#### Balance & World Integration

- Configure where these items are allowed, reduced, or disabled: world PvE, dungeons, raids, battlegrounds, arenas, and private duels may each need different rules.
- Prevent benefits from stacking into mandatory raid or competitive PvP builds; use mutually exclusive chem categories, diminishing returns, or shared cooldowns when necessary.
- Integrate discovery, black-market merchants, roleplay quests, and the **Camping & Survival** disease/sickness concept without making drug use a required progression path.
- Log consumption and resulting server-side aura/state changes for anti-exploit review.

> **Design rule:** Substance effects, side effects, addiction risk, and recovery must be transparent and manageable. Avoid punishing players indefinitely or creating a best-in-slot consumable that everyone is effectively forced to use.

### Gambling, Casinos & Gold-Wagering Minigames

Build optional **in-world casinos and player-versus-player wagering** around server-run minigames. Unlike purely recreational housing table games, this system supports actual **in-game gold stakes**, with clearly defined rules, payouts, and protections against scams or gold duplication.

#### Supported Games

- **Chess and checkers:** Challenge another player, agree to a gold stake, take turns, and finish a rules-enforced match. Include a spectator mode and configurable move timer.
- **Card games:** Introduce one or more original Azeroth-themed games with public rules, supported hands/decks, and server-validated turns or draws.
- **Slot machines:** Place interactive machines in casino venues, using server-authoritative randomized results and a published prize table.
- **Dice or other quick games (optional):** Offer short, low-stakes matches for players who do not want a full board-game session.
- Use themed tables, dealers, machine models, animations, sounds, and a dedicated lightweight UI showing stakes, rules, turns, and outcomes.

#### Gold Wagers & Settlement

- Allow **friendly no-stakes play**, or let participants jointly accept a gold wager before the match begins.
- Check that each player owns the required gold, then hold both stakes in **server-side escrow** before starting; neither player can change the agreed amount mid-match.
- Resolve wins, losses, ties, forfeits, and timeouts against authoritative game state. Draws should follow a clearly stated refund or replay policy.
- Settle wagers in an **atomic transaction** to avoid duplicate payouts, lost funds, or exploits during disconnects and crashes.
- Establish clear cancellation rules: refund escrow for matches canceled before play or interrupted by server failure; apply published timeout/forfeit rules once a valid match begins.
- Support optional venue fees or a configurable **house cut**, shown before wager confirmation.

#### Casino House & Lottery

- Create casino NPCs or authorized venues that host games and track **house earnings** from defined fees or NPC games.
- Allocate a configurable portion of eligible **house winnings** to a shared **lottery jackpot** rather than generating unlimited prize gold.
- Let players purchase lottery tickets **using in-game gold only**, with visible ticket cost, draw schedule, prize rules, and jackpot total.
- Run lottery draws server-side, record winning tickets, settle or mail prizes exactly once, and define what happens if no eligible ticket wins (for example, a rollover).
- Publish odds and payout rules for chance-based games; keep prize pools, draws, and payouts auditable by administrators.
- Optional casino reputation, decorative trophies, and cosmetic achievements can reward participation without inflating combat power.

#### Permissions, Security & Economy

- Keep **real-money stakes, cash-out, and real-world prize redemption out of scope**; gold must remain an in-game currency.
- Use server-authoritative rules and unpredictable server-side random outcomes where chance is involved. Never trust client-reported wins, balances, or dice rolls.
- Add per-character or per-account wager limits, cooldowns, opt-out controls, and suspicious-transfer / collusion monitoring.
- Keep detailed audit records of game IDs, participants, escrow, result, house cut, and final payouts.
- Separate casino wagering permissions from ordinary housing permissions; **placeable home chess/checkers tables stay non-wagering** unless a distinct, explicitly enabled casino system is designed for them.
- Review applicable platform/server rules and legal requirements before enabling gold wagering publicly, especially if any paid currency or real-world transfer is possible elsewhere in the ecosystem.

> **Scope distinction:** This is separate from the **Diablo-style Gambling Vendor** and from the non-wagering [housing table games](#table-games). All three may share visual assets, but should not share unvalidated currency-handling logic.

---

## 8. Housing, Guilds & Professions

Expand Esteria housing beyond static decoration with customizable environments, collaborative building, social venues, decor progression, and optional interactive activities. The features below are **concepts**, not a finalized implementation order.

**Housing sections:** [Deployable camps & Garrisons](#deployable-camps--garrisons) · [Property & ownership](#property--ownership) · [Interactive home & atmosphere](#interactive-home--atmosphere) · [Social & collaborative experiences](#social--collaborative-experiences) · [Housing creation & decor progression](#housing-creation--decor-progression) · [Functional rooms & optional activities](#functional-rooms--optional-activities) · [Guild progression](#guild-progression)

### Deployable Camps & Garrisons

#### Deployable C.A.M.P.s — Fallout 76 Inspiration

Introduce portable, **player-placeable C.A.M.P.s** for temporary bases throughout the open world, separate from full permanent homes and Garrisons.

- Let players deploy a camp at an eligible location using a placement preview / hologram, then **reposition or pack it up** when relocating.
- Support a compact build area with **tents, campfires, shelters, workstations, storage, seating, decor, and useful service objects** as they are unlocked.
- Reuse the housing placement and decorating tools where possible, including snapping, rotation, permissions, blueprints, and ownership tracking.
- Save a camp layout so relocating it does not require manually rebuilding every furniture piece.
- Define camp budgets, number of active camps, relocation costs/cooldowns, and persistence while the owner is offline (**TBD**).
- Enforce placement restrictions around quest objectives, entrances, towns, roads, combat-critical areas, other players' properties, and unstable terrain.
- Handle occupied or invalid locations safely on login: offer relocation/redeployment instead of silently deleting objects.

> **Scope distinction:** A **C.A.M.P.** is a lightweight, relocatable campsite. It should not automatically grant all the buildings, NPC systems, or progression of a full Garrison.

#### Retail Housing + Garrison Hybrid — Placeable Garrisons

Combine the **freeform decorating, object placement, and collection systems of retail housing** with the **functional buildings, NPCs, followers, and progression of Warlords of Draenor Garrisons**.

- Let players **place an entire Garrison** on a permitted plot or designated world location, instead of limiting it to the original fixed Draenor site.
- Build the settlement from configurable **structures and building plots**—for example, barracks, workshops, stables, crafting buildings, farms, taverns, defenses, and mission facilities.
- Allow **retail-style indoor and outdoor decorating** across the Garrison: furnishings, dyes, movable objects, signs, lights, trophies, and custom layouts.
- Support building construction, upgrades, unlocking new plots, staff / followers, and the existing [housing mission board](#housing-mission-board).
- Let owners choose exterior themes, building positions, pathways, and eligible cosmetic architectural variations, subject to collision and budget limits.
- Integrate compatible pieces from Esteria's **property permissions, co-decorating, professions, player shops, taverns, and guild-space** concepts.
- Keep each Garrison's functional systems and rewards **server-authoritative**; decorative props must not accidentally duplicate NPC services or item-producing buildings.
- Decide whether public-world Garrisons are fully persistent or use instancing / phasing to prevent settlement overlap, performance issues, and crowding.

> **Design relationship:** **C.A.M.P. = mobile mini-base; housing = personal property; Garrison = placeable, upgradeable settlement.** Reuse placement and decor infrastructure across all three, while giving each its own capacity and progression rules.

### Property & Ownership

#### Place Houses Almost Anywhere

- Allow players to place houses in the open world **within reasonable restrictions**.
- Consider excluding cities and placement areas that would interfere with:
  - Quests and events.
  - Existing structures.
  - Cave entrances.
  - Other important world features.
- Potentially an extremely expensive unlock (example: **10,000,000 gold**).
- Include a yard/land plot with the home.

#### Housing Mission Board

- Add a placeable housing mission board similar to the retail Garrison mission board.
- Send units/ships on missions for XP, loot, and other rewards.
- Level up units/ships to unlock more rewarding missions.

#### Housing-related Professions

- **Sales**
  - Gain profession experience from making sales.
  - Unlock benefits such as higher profits or more available sale slots.
- **Homemaker / Landlord**
  - Gate housing capacity limits behind profession level.
  - Example: a **Grand Master** might unlock a capacity of **5,000 furniture pieces**.
- **Woodworking**.
- **Farming**.
  - Grow and harvest crops.
- **Woodcutting**.

#### Renting Houses to Other Players

1. **Player A** builds/decorates a property and lists it in an in-game real-estate browser.
2. **Player B** rents it, paying an amount set by Player A at an interval chosen by Player A (daily, weekly, or monthly).

### Interactive Home & Atmosphere

#### Functional Doors & Secret Doors

Let builders place doors that operate as interactive objects rather than static decorations.

- Open, close, lock, or unlock doors through player interaction.
- Configure **door access independently** from overall property entry permissions.
- Offer standard doors, gates, sliding panels, hidden bookshelves, and other themed options.
- Link secret doors to hidden switches, levers, pressure plates, or configured triggers.
- Support auto-close timers and optional owner-only controls.
- Validate passage and lock states **server-side**, so unauthorized players cannot bypass restricted areas.

#### Jukebox

Place a music player that controls the property's ambient soundtrack.

- Select from a curated library of eligible in-game music tracks.
- Build playlists and toggle shuffle, repeat, volume, and playback zones where supported.
- Allow the owner to permit guests to request or change tracks.
- Persist the selected playlist and playback configuration.
- Apply music locally to the relevant housing area rather than changing unrelated world audio.

#### Time-of-Day Controls

Let owners select the time and lighting mood of their housing environment.

- Choose dynamic time or a fixed time such as dawn, noon, sunset, or midnight.
- Update compatible world lighting, sky effects, and visible lighting through windows.
- Where the environment supports it, synchronize exterior window views with the selected time.
- Keep changes **scoped to the property or housing instance**, not the global world.
- Allow preset configurations to be saved as part of property settings.

> **Technical note:** Window/lighting updates may require custom client-side rendering support; they are not guaranteed by the existing 3.3.5a systems.

#### Weather Controls

Give owners control over visible weather and atmosphere in outdoor or compatible housing areas.

- Select weather presets such as clear skies, rain, snow, fog, and storms.
- Support dynamic weather or a fixed preset.
- Apply appropriate environmental visuals and sounds where supported.
- Keep effects local to the housing area and independent of public-zone weather.
- Coordinate weather settings with time-of-day and interior/exterior transitions.

### Social & Collaborative Experiences

#### Guestbooks

Allow homeowners to place a guestbook for visitors to leave messages.

- Visitors can sign, leave a short note, and optionally select a greeting or reaction.
- Owners can view entries by date and remove inappropriate entries.
- Provide spam limits, text moderation, and reporting controls.
- Allow the owner to restrict who can write and who can read the guestbook.
- Preserve entries across server restarts; offer pagination for heavily visited properties.

#### Co-Decorating

Let homeowners invite others to help decorate without transferring ownership of the property.

- Add a separate **edit permission** beside existing visitor access, granting decoration rights to selected party/raid members, friends, or guild members, independently of who may visit.
- Trusted decorators can place, move, rotate, scale, and store decor inside and outside the house, using the **owner's decor budget**.
- Decor placed by a helper comes from the **helper's storage**; storing that piece returns it to **whoever placed it**.
- Room layout, house style and parts, plot placement, upgrades, and permissions remain **owner-only**.
- Record who placed or changed each piece (the existing edit log keeps the placing character) so owners can review and undo changes.
- Revoking edit permission takes effect **immediately**, including for anyone currently editing.

### Housing Creation & Decor Progression

#### Housing Blueprints

Allow builders to save and reuse **furniture layouts and room designs**.

- Save a selected group of objects, an entire room, or an eligible property layout as a named blueprint.
- Preserve compatible positions, rotations, scales, visual variants, and allowed cosmetic settings.
- Preview a blueprint before applying it and report missing or incompatible furniture.
- Require the destination property to have the necessary furniture or unlocked objects before placement.
- Allow personal blueprint libraries, sharing with friends, and sale of original layout designs through an approved system.
- Support an undo/rollback action for blueprint placement when feasible.
- Check plot boundaries, object limits, collisions, and property permissions before applying a layout.

> **Security boundary:** Blueprints must **never** copy real inventory, shop listings, vendor earnings, stored chest items, personal or guild bank data, bound destinations, privileged permissions, or other ownership-sensitive state. They represent arrangements and permitted cosmetic configuration—not free duplicates of assets.

#### Decor Acquisition & House Level

Make collecting decor part of play instead of buying everything for gold from the catalog.

- Add **decor vendors** in the neighborhood with rotating stock, priced in gold or other currencies.
- Award decor as **quest rewards** and through **loot tables** (dungeon, raid, and world drops), achievements, professions, and events, using retail's decor-to-item links where available.
- Add **world treasure hunts** that lead players to hidden decor around the world.
- Grant **house experience** the first time a decor piece is acquired (retail's per-decor first-acquisition XP), raising a **house level** that unlocks larger budgets, more rooms/floors, and new exterior styles.
- Keep the gold catalog for basic furniture so new homeowners can still furnish a house.
- Show where an unowned decor piece comes from in the decor chest's catalog.

> **Design dependency:** Both house-level progression and the proposed Homemaker/Landlord profession affect housing capacity. Decide how their limits and unlocks interact before implementing them.

#### Retail Decor Coverage

Close the remaining gaps in the retail decor catalog.

- **Five retail decor models** are excluded because they rely on shader effects the client cannot yet draw (**two retail shader combinations**).
- Add those shader effects to the client's model renderer; this should also resolve other retail models using them.
- Re-check newly released retail decor against the client and add compatible models as they become available.

#### Decor Dyes

Let players recolor decor, as retail housing does.

- Use retail's per-model dye data (dye slots and their color and influence maps) to recolor marked parts of a decor piece.
- Add a **dye picker** to the decor editor for the selected piece, showing colors the player has unlocked.
- Save chosen dyes with each placed piece so everyone sees the same colors inside and outside the house.
- Implement a new decor shader in the client renderer that blends the chosen colors through the dye maps.

#### World Doodads as Decor

Investigate offering the game world's doodads—props placed in zones and cities—as decor.

- Survey which doodads make good decor, such as furniture, crates, plants, and banners from familiar zones.
- Confirm each doodad loads, renders, and scales correctly when placed; assign a name, category, placement surface, and price.
- Decide how each is unlocked (for example, by visiting or completing content from its source zone) so it fits the acquisition system above.

### Tinkering — Player-Owned Automatons & Production Lines

Introduce a **Tinkering profession** for constructing machines that perform real in-world jobs, including within housing, C.A.M.P.s, or Garrisons.

- **Mining drills:** Extract limited eligible mineral resources while fueled or maintained.
- **Conveyor belts:** Move eligible physical input items between compatible machines and storage points.
- **Sorting machines:** Organize containers by item type, rarity, profession, or configurable filters.
- **Mechanical assistants:** Perform narrow tasks defined by the owner, such as delivery within a plot, tidying, or collection.
- **Automated crafting stations:** Process supplied reagents into defined outputs according to known recipes and throughput limits.
- **Security constructs:** Patrol an authorized property or help with the optional housing-defense encounters.
- Give machines recipes, build costs, power/fuel or maintenance needs, ownership, permissions, and visible operating states.
- Make production lines genuinely functional—players could watch ore travel into a workshop and finished goods reach a storage bin—without allowing unattended infinite wealth generation.
- Put clear caps on output rates, resource extraction, concurrent machines, offline simulation, and server load.
- Define interaction with housing placement budgets, profession progression, inventory transfers, and property visitors.

> **Economy rule:** Automation must consume real inputs and use server-side inventory transactions; moving a visible item model on a conveyor must never mint additional copies of the item.

### Functional Rooms & Optional Activities

#### Home Defense System

Introduce an optional **PvE defense mode** in which a property becomes the setting for wave-based encounters.

- Let owners place defenses such as guards, turrets, traps, barricades, and support objects.
- Start encounters from a housing control interface or defensive command object.
- Spawn attacker waves with configurable challenge tiers and themes.
- Scale difficulty using supported rules for group size and progression.
- Permit friends or authorized guests to join the defense.
- Show wave progress, objectives, surviving defenses, and end-of-event results.
- Run each encounter in an **isolated event instance or equivalent isolated state** so ordinary visitors are unaffected.
- Restore all decorative furniture and permanent structures after the event; **no persistent destruction**.
- Offer optional progression or cosmetic rewards with cooldowns/limits to prevent reward farming exploits.

#### Functional Kitchen

Create a kitchen area with usable cooking stations and interactive furniture.

- Place stoves, ovens, preparation tables, cooking fires, counters, and storage fixtures.
- Craft supported food and drink recipes using the appropriate profession rules.
- Provide animations for supported cooking or preparation interactions.
- Optionally connect kitchen storage to tavern inventory through explicit owner actions.
- Allow owners to designate kitchen staff or public cooking access if those systems are enabled.
- Keep cosmetic food displays separate from actually crafted, consumable items.

#### Player-Owned Taverns

Turn a property into a functioning tavern with a **Bartender NPC**, seating, and consumable sales.

- Stock food, drinks, and eligible crafted consumables for purchase.
- Let the owner configure menu items, prices, bartender appearance, and greetings.
- Allow visitors to sit at tables, counters, and other compatible furniture.
- Support ordering from the bartender or, where feasible, interactive tables.
- Offer temporary **resting or social bonuses** while visiting or after using tavern services.
- Allow decorations, lighting, jukeboxes, and other housing systems to contribute to tavern atmosphere.
- Keep the tavern accessible and stocked while the owner is offline, subject to visitor permissions.

> **Balance rule:** Bonuses should be modest, clearly described, and designed not to replace stronger combat consumables or become mandatory for competitive content.

#### Private PvP Arenas

Let homeowners create controlled dueling and practice spaces within their property.

- Designate an arena area and configure boundaries, starting positions, and spectator spots.
- Support consensual duels, team skirmishes, and optional custom match rules.
- Add match controls for starting, ending, resetting, and selecting participants.
- Offer a simple scoreboard for wins, losses, rounds, and match duration.
- Keep arena combat separated from visitors who are not participating.
- Prevent permanent damage to house objects from PvP combat.
- Allow spectators without automatically making them combat targets.

> **Design rule:** Private arena matches should not award official ranked PvP progression unless Esteria deliberately integrates them with its ranked systems.

#### Table Games

Introduce placeable, interactive games for social spaces.

- Start with chess, checkers, dice, or original Azeroth-themed tabletop games.
- Let visitors join, spectate, leave, or restart matches through a simple interface.
- Track turns and enforce rules server-side where competitive outcomes matter.
- Support tables and themed game pieces as placeable furniture.
- Optionally show non-monetary achievements or friendly records.
- Avoid automated real-money or gold wagering mechanics in these housing table games.

> **Scope distinction:** These social table games are separate from the general gambling/casino ideas in [Economy, Loot & Vendors](#7-economy-loot--vendors).

### Player-Run Jobs & NPC Role Replacement — FiveM Inspiration

Let a player **take over the role of an eligible NPC** and become the actual interactive service provider for other players until they quit or go offline.

#### Assuming a Role

- An eligible player targets an available job NPC and chooses **Assume Job**.
- The original NPC is **temporarily removed or suppressed** while the player takes over that specific service role.
- Other players can right-click the working player and access the appropriate **NPC-style shop, dialogue, training, quests, or service menu**.
- On **Quit Job**, disconnect, logout, or lease expiry, the original NPC returns with its normal functions. Avoid leaving towns permanently without crucial services.
- Validate one active occupant per job position and restore NPC services safely after crashes or server restarts.
- Consider job progression, reputation, wages, tips, custom storefronts, and a city-wide vacancy browser.

#### Example Jobs & Unique Services

| Job | Potential player-facing functions |
| --- | --- |
| **Innkeeper** | Set a hearth location selected by the working innkeeper; offer rested services. Under the original concept, the **player-set hearth remains active only while that innkeeper is online**. |
| **Blacksmith** | Operate a player-owned shop, fulfill crafted work orders, and issue resource contracts. |
| **Leatherworker** | Run a shop, fulfill armor commissions, and post material-buying contracts. |
| **Bartender** | Sell existing or custom drinks and food; request ingredients through contracts. |
| **Quest Giver** | Publish bespoke, server-validated quests and offer player-funded rewards. |
| **Merchant** | Stock eligible items for sale, configure listings, and post trade contracts. |
| **Trainer** | Train other players in eligible skills over time according to defined caps and training costs. |
| **Mailman / Postmaster** | Physically deliver or process queued mail between locations; under the proposed system, **mail items remain pending until a player mail carrier processes them**. |
| **Farmer** | Place and tend farms, grow crops/reagents, sell harvests, or earn controlled passive income. |

#### Safeguards & Integration

- Provide a job interface for current duties, stock, earnings, deliveries, contracts, and service pricing, with explicit limits on what a player-run NPC can change.
- Keep NPC quest rewards, skill training, mailbox transfers, hearth bindings, and all other privileged actions **server-authoritative**; roleplay access is not GM access.
- **Mail delivery dependency:** Because player-carried mail can stall if nobody accepts the job, design a recovery/timeout/fallback procedure. Keep the human-delivery goal, but never permanently lose paid items or mail.
- **Hearth dependency:** Decide the player's respawn/hearth fallback when the working innkeeper logs off; the temporary job should not strand customers in invalid locations.
- Integrate job supplies with advanced crafting, farmer crops, player contracts, taverns, Garrison workshops, and the broader player-driven economy.

> **Design distinction:** Players take over NPC **functions and presentation temporarily**; they do not gain the NPC's administrator permissions, inventory ownership, or private server script access.

### Guild Progression

- Bring in the **Cataclysm guild leveling system**.

---

## 9. Hunter & Warlock Pets

### Expanded Tameable Families

- Add taming for:
  - Demons.
  - Dragons.
  - Dragonkin.
  - Elementals.
  - Undead.
  - Mechanical creatures.
- **Possibilities to explore:** Humanoids and giants.
- Allow users with beast pets to **ride their pets**.
- Support **multiple simultaneously active pets**; see [Combat Pet UI, Remote Storage & Multi-Pet Teams](#combat-pet-ui-remote-storage--multi-pet-teams).

### Expanded Pet Storage

- Uncap combat-pet storage, with remote access and persistent identities.
- Replace the default Stable Master interface with a **Pokémon-style pet bank**; see [Combat Pet UI, Remote Storage & Multi-Pet Teams](#combat-pet-ui-remote-storage--multi-pet-teams).

### Combat Pet Genetics — Individual Values, Effort & Breeding

Extend tameable **combat pets** with a Pokémon-inspired **IV/EV-style development system**, independently of the separate Battlemon collectible Pokémon game.

- Give every tameable NPC species/family defined **base stats** and each eligible wild NPC its **own individualized starting stat spread and inherited/rolled values** when spawned or tamed.
- Track effort/training gains from eligible combat and activities, with explicit caps and rules for how they affect stat growth.
- Include a **breeding system** so players can pair compatible pets and gradually pursue ideal stat combinations across generations.
- Determine eligible pet families, breeding cooldowns, offspring inheritance, rarity, and how many new pets can be generated to prevent overproduction.
- Keep clear differences between a creature's **species base stats**, its individual values, trained values, talents, and temporary buffs.
- Provide a fair route for players who prefer a favorite pet's appearance to remain useful without forcing endless competitive breeding.

### Combat Pet UI, Remote Storage & Multi-Pet Teams

- Replace or expand the default Pet/Stable interface with a richer **pet character sheet** showing 3D previews, individual/base/trained stats, family, traits, learned abilities, talents, bonding, and breeding information.
- Make combat-pet **storage effectively unlimited**, accessible remotely through an account/character-appropriate storage interface rather than requiring repeated Stable Master visits.
- Allow a character to **summon multiple active combat pets simultaneously** and mix eligible families, such as **Beast + Dragonkin**, under class/archetype and balance rules.
- Give players clear squad controls for target assignment, follow/stay, attack/defend, formations, and dismissal, with an easy way to manage individual pets.
- Allow stored or selected pets to **roam around player housing** as non-destructive ambient occupants, using safe movement boundaries and a configurable display limit.
- Preserve persistent pet identity, stats, and inventories across death, stabling, breeding, relocation, or logout; do not silently replace a unique pet with its generic NPC template.

> **Interaction with existing concepts:** The Pet Codex describes discoverable tameable species; this system tracks **owned individual pets**. Both should link to one another without conflating individual combat-pet genetics with the separate Battlemon IV/EV rules.

### Pet Codex / Pokédex

- Unlock the Codex UI when a character learns a taming ability.
- Show a comprehensive catalog of creatures tameable by that character's available pet families.
- Each creature entry should support:
  - 3D model preview.
  - Spawn location.
  - Level.
  - Other relevant creature data.
- Require **Beast Lore**, **Dragon Lore**, etc. on a target to record its information.
- Track unrecorded tameable creatures on the minimap.
- Award milestones for taming discoveries, including:
  - Companion pets.
  - Mounts.
  - Cosmetics.
- Distribute milestone rewards through achievements and mail.

### Necromancy — A Dedicated Crafting & Summoning Profession

Explore **Necromancy as a genuine profession/progression path**, rather than simply adding another skeleton-summoning spell.

- Gather eligible remains, study spirits, research formulas, and assemble **custom undead servants** from creature components.
- Let combinations influence appearance, movement, durability, and abilities. Examples include:
  - A skeletal warrior with the mobility of a spider.
  - A plague-bearing ghoul enhanced with protective armor.
  - A skeletal mage whose spells depend on installed magical components.
- Store constructed-servant designs and component provenance; allow controlled repairs, upgrades, and optional cosmetic personalization.
- Limit concurrent servants, power budgets, command complexity, and interactions with the classless spell system.
- Distinguish assembled undead from **Hunter/Warlock tameable pets**, Battlemon, and hired Journey Companions; define how simultaneous summons coexist.
- Provide quests and NPCs that connect Necromancy with the Spirit World, rare cursed items, and forbidden world locations.

> **Implementation note:** Constructed servant state should be based on server-approved component combinations, not unrestricted creature/spell assembly on the client.

---

## 10. Companion Pets & Hired Companions

### Premium Companion Pet Services

- Premium companion pets with useful services:
  - Vendor.
  - Quest giver.
  - Teleporter.
  - Trainer.

### Companion Pet Overhaul

- Give noncombat companion pets practical functions:
  - Loot eligible nearby **world drops / ground pickups**, replacing corpse looting when Diablo-style loot is enabled.
  - Act as a target dummy or distract enemies.
- Add Tamagotchi-like care needs: happiness, food, and water.
- Let pets gain levels and XP from activities such as looting, play, and care.

### Journey Companion System

#### Hiring & Customization

- Add companion recruitment NPCs to capital cities such as **Stormwind, Orgrimmar, and Dalaran**.
- Let players hire an NPC adventuring companion.
- Present all available playable races as companion race options.
- Allow full player-like appearance customization (hairstyle, hair color, etc.).
- Save the chosen appearance persistently.
- Allow a lost companion to be retrieved from the city NPC for a small fee.

#### Levels, Stats & Equipment

- At hiring, companions match their master's level and receive corresponding stats.
- Companions have unique stats and subsequently gain their own XP/levels alongside their master.
- Equip companions with weapons, armor, trinkets, etc., applying their stat bonuses as if the companion were a player.
- Provide a dedicated character-style interface with:
  - 3D model.
  - Character stats.
  - Equipment paper doll.
  - Inventory access.
- Give companions their own spellbooks and talents.
- Let companions select talents/abilities automatically or accept player-assigned selections; **player choices override automatic choices**.

#### Combat & Utility

- Revive a fallen companion by right-clicking or by using an applicable resurrection spell.
- Let companions collect eligible **physical world loot drops** (and loot corpses only where traditional loot remains enabled).
- Allow companions to distract enemies or take a tank/aggro role.
- Configurable combat AI modes:
  - Melee DPS.
  - Ranged DPS.
  - Magic user.
  - Healer/support.
  - Tank.
- Companions can enter dungeons/raids with players **without affecting player-party counts**.

#### Following, Mounting & Needs

- Track companion happiness, hunger, thirst, and rest.
- Automatically mount/dismount when their owner does.
- Seat the companion in an available passenger seat when the owner uses a mount with **2+ seats**.
- Optionally show a hired companion alongside its player in the **Living Inn character-selection scene** using a display-only representation (see [The Living Inn](#character-selection-the-living-inn)); similarly consider hunter pets when supported.

#### Ambient Dialogue & Reactions

- Periodic incidental dialogue and ambient noises (chatter, coughs, sneezes, sighs, etc.).
- Contextual callouts for:
  - Enemies that aggro the group.
  - Entering combat.
  - Additional enemies joining combat.
  - Low health.
  - Hunger or low food.
  - Thirst or low water.
  - Tiredness.
  - Leaving combat.
  - Looting corpses.

### Rent Your Alternate Characters as Player-Hired Bots

Allow a player to offer **their own alternate characters** as AI-controlled mercenaries that **other players can hire**—a character-based extension of the Journey Companion system.

- Owners opt in individual eligible alts and post hire terms (fee, duration, role, supported activities, and availability) in an in-game mercenary marketplace.
- The hiring player can recruit a listed alt as a **server-controlled bot companion** with an appearance and combat role based on the real character's saved build and gear, within approved limits.
- Support configurable service roles such as tank, healer, melee/ranged damage, or utility, with AI distinct from a player-controlled login session.
- Define whether hired bots may accompany customers in open world, dungeons, raids, or selected private events and how they interact with party limits and rewards.
- Give owners an earnings ledger, opt-out/recall controls, and clear protections for stored items, consumables, progression, and reputation.
- A rented alt must **never expose the account credentials** or grant the borrower direct control of the owner's actual character/session.
- Decide what happens when the owner logs in on the rented alt, cancels the offer, becomes unavailable, or changes its equipment during a hire.
- Use copies/snapshots or narrowly scoped AI control to ensure that rental use cannot steal gear, trade away inventory, consume valuable resources, or corrupt the owner's saved world position.

> **Key distinction:** This is **renting the *service* of an alternate character as a bot**, not transferring ownership or allowing another player to log into that character.

---

## 11. Battlemon / Pokémon

### Spawning & Progression

- Rework Pokémon spawns for more logical placement.
  - Add an admin addon panel with spawn configuration controls.
- Use move-learning behavior similar to the mainline Pokémon games.
- Rebalance stats, base values, and growth curves.
- Include **IVs/EVs**.
- Add breeding.
- Implement the **Pokémon Trainer profession** (present in source, but not implemented).

### Overworld Interaction

- Let the player choose a Pokémon to follow them around the world.

### Items & Services

- Pokémon item vendors.
- Potions, Poké Balls, berries, etc.
- **PokéCenter**.
- **Poké Box** for digital Pokémon storage.

### Trading & Battling

- Trade Pokémon directly with nearby players or remotely.
- Battle players directly or remotely.

### Pokémon as WoW Items

- Represent captured Pokémon as WoW items (Poké Balls containing their Pokémon).
- Permit those items to be sold on the **Auction House**.

---

## 12. Seasonal Content & Rotations

### Seasonal Content & Rewards

- Refine existing seasonal activities and their rewards.

### XP Weekends

- Support an XP weekend event with a configurable schedule **or** a manual on/off toggle.

---

## 13. Systems to Port & Reference Projects

### Ascension-inspired Systems

- **Worldforged items**.

### External Game / Technology References

| Area | Reference repositories |
| --- | --- |
| Skateboarding | [TonyWasAProSkater](https://github.com/LANCommander/TonyWasAProSkater) · [skate3recomp](https://github.com/mchughalex/skate3recomp) |
| Cars / driving | [nfsmwpc-recompiled](https://github.com/codepdbh/nfsmwpc-recompiled) · [SpaghettiKart](https://github.com/HarbourMasters/SpaghettiKart) |
| Pokémon | [gen1recomp](https://github.com/bryanthaboi/gen1recomp) |

> These links are inspiration/research references, not implementation instructions or claims of compatibility.

---

## 14. Unscoped / Exploratory Ideas

The following idea remains a placeholder for later definition:

- **Additional housing concepts** — further possibilities beyond the detailed housing entries in Section 8.

**Previously expanded from the original notes:** [Nat Pagle fishing](#nat-pagle--fishing-challenges-bounties--unique-rewards) · [Fictional drugs / chems](#fictional-drugs--riskreward-consumables) · [Casinos and gold wagering](#gambling-casinos--gold-wagering-minigames).

**Additional November 2026 brainstorm ideas:** Integrated into the existing topical sections above rather than appended as an unorganized list. All additions remain **concept proposals**, not approved implementation requirements.

---

**End of working idea backlog. No priorities or implementation feasibility are implied by section order.**
