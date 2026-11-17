# ESTERIA — Retail World of Warcraft Trading Post Implementation

## 1. Project Objective

Implement a complete, production-ready **World of Warcraft Retail-inspired Trading Post system** for Esteria, built on our custom World of Warcraft 3.3.5a client and AzerothCore server.

**Primary objective:** Reproduce the retail Trading Post as closely as technically possible, including its user interface, immersive 3D item previews, animations, camera behavior, player interactions, server-side functionality, monthly catalogue rotations, purchases, item freezing, monthly activities, account-wide rewards, and persistence.

This must not be a simple custom vendor, ordinary shop window, gossip menu, or static catalogue.

The Trading Post should feel like a native Blizzard feature that has been fully backported into our customized 3.3.5a client.

We have access to:
- Our custom/decompiled 3.3.5a client source.
- The AzerothCore server source.
- Client rendering, UI, interface, and asset systems.
- Custom server modules and database infrastructure.
- Retail client assets that may be investigated for compatibility and adaptation.
- Our existing custom systems, currencies, collection features, and progression mechanics.

**Do not assume retail UI code or assets can simply be copied into 3.3.5a.** Examine the implementation and port or recreate the necessary dependencies using our existing architecture.

The supplied screenshots are the visual and interaction references.

## 2. Implementation Principles

Prioritize the following, in order:

1. Retail behavioral fidelity.
2. Retail visual and animation fidelity.
3. Fully functional client/server integration.
4. Database persistence and account-wide consistency.
5. Compatibility with Esteria's existing custom systems.
6. Maintainability and extensibility.

Every visible interface element must be functional.

Every purchase, currency transaction, reward, and ownership change must be validated server-side.

Avoid placeholder buttons, mock data, hardcoded demonstrations, temporary scripted shortcuts, and UI-only simulations presented as completed functionality.

Where full fidelity is not possible, document the limitation and implement the closest technically practical native equivalent.

## 3. Research and Reverse-Engineering Requirements

Before implementation, investigate the actual retail Trading Post architecture.

Relevant retail components include:

- `Blizzard_PerksProgram`
- `Blizzard_PerksProgram.lua`
- `Blizzard_PerksProgramProducts.lua`
- `Blizzard_PerksProgramModel.lua`
- `Blizzard_PerksProgramFooter.lua`
- `Blizzard_PerksProgramElements.lua`
- Related XML, templates, animations, localization, and supporting assets.
- Retail `C_PerksProgram` API behavior.
- Retail model-scene, preview-camera, and character-rendering systems.

Reference:
https://github.com/Gethe/wow-ui-source

Investigate the following:

- How the Trading Post UI opens and closes.
- How the client enters and exits its immersive viewing mode.
- How products are fetched and displayed.
- How the selected product determines the 3D preview.
- How models are animated, positioned, rotated, and swapped.
- How character appearances are previewed.
- How freeze operations work.
- How cart checkout, purchase confirmation, and refunds work.
- How the interface displays ownership, currency, prices, and expiration.
- Which functions are client-side and which require authoritative server behavior.
- Which retail dependencies are missing from 3.3.5a.

Do not mistake retail UI source for the retail server implementation. Build the required backend functionality independently.

Produce a feature-by-feature compatibility assessment before changing source code.

---

# PART I — WORLD INTERACTION AND USER EXPERIENCE

## 4. Trading Post Locations

Create functional Trading Post locations inspired by their retail equivalents.

Initial locations:

- Stormwind — Alliance Trading Post.
- Orgrimmar — Horde Trading Post.

The location should resemble retail's physical storefront, featuring:

- Trading Post stalls and structures.
- Appropriate faction-themed architecture.
- Merchant NPCs.
- Collector's Cache.
- Display mannequins.
- Stable areas showing featured mounts.
- Cosmetic merchandise displays.
- Decorative props.
- Appropriate lighting, ambient sounds, and NPC animations.

Both factions should have access to the same underlying rotating catalogue and currency wallet unless a specific offer is faction-restricted.

Location-specific presentation may differ.

### NPC Interaction

When a player approaches and interacts with the designated Trading Post merchant:

1. Validate the player's interaction with the NPC.
2. Load the account's Trading Post state.
3. Retrieve the active catalogue and current currency balance.
4. Transition the camera into the Trading Post browsing interface.
5. Open the immersive catalogue overlay.
6. Display the first eligible or currently selected product.
7. Render its 3D preview in the storefront environment.
8. Allow interaction with the catalogue without leaving the browsing scene.

The result should closely reproduce retail's Trading Post interface rather than opening an ordinary merchant window.

## 5. Immersive Trading Post Interface

Match the structure and behavior of the supplied screenshots.

### Left Side — Catalogue

Display a dark, semi-transparent catalogue panel featuring:

- Filter controls.
- Product icons.
- Product names.
- Product prices.
- Universal currency icon.
- Remaining availability time.
- Owned or purchased indicators.
- Selected-item highlighting.
- Scrollable inventory.
- Frozen-item area at the bottom.

Catalogue rows should preserve the classic Blizzard presentation, including Warcraft-style typography, gold-accented selections, and recognizable item-quality styling.

Clicking an item must update the central 3D preview and right-side details without reopening the interface.

Implement relevant category filtering:

- All items.
- Mounts.
- Pets.
- Toys.
- Cosmetic armor appearances.
- Cosmetic weapon appearances.
- Ensembles and appearance bundles.
- Illusions and visual effects.
- Other supported cosmetic categories.
- Owned.
- Unowned.
- Affordable.

Support retail-style filtering behavior where available; use Esteria-specific extensions only where necessary.

### Center — Interactive Preview

The central portion of the screen must use an immersive 3D presentation.

Depending on the selected product, show:

**Mounts**
- The player's character mounted on the selected mount.
- Appropriate mount scale and positioning.
- Correct mount animations.
- Relevant visual effects and particles.
- Race-appropriate character positioning.
- Mount entrance or special animations where available.

**Armor Cosmetics**
- The player's character wearing the selected appearance.
- The appearance applied temporarily for preview only.
- Correct race, gender, equipment slot, and attachment behavior.
- Appropriate handling of ensembles or multi-slot sets.

**Weapon Cosmetics**
- The character holding or displaying the selected weapon appearance.
- Correct attachment locations.
- Supported idle, combat, and special weapon animations.
- Proper visual enchantment or illusion effects.

**Pets**
- A fully rendered pet model.
- Correct idle and special animations.
- Appropriate scale and framing.
- The player may be displayed alongside the pet where retail does so.

**Toys and Special Cosmetics**
- The actual model, effect, or relevant animation wherever technically possible.
- A suitable dedicated preview mode when the item does not fit a normal character model.

### Preview Controls

Implement retail-equivalent interactive controls:

- Rotate left.
- Rotate right.
- Hide player.
- Hide armor.
- Toggle applicable mount special animations.
- Toggle applicable weapon/combat animations.
- Navigate between catalogue products.
- Exit the preview.
- Support any additional camera controls confirmed in the retail implementation.

Do not add arbitrary controls that interfere with retail-style interaction.

Preview rotation and camera movement should be smooth and responsive.

Switching between products should update the displayed model without creating unnecessary scene reloads or visible glitches.

### Right Side — Item Information

Show an information panel containing:

- Product category.
- Product name.
- Flavor description.
- Applicable requirements.
- Remaining availability time.
- Relevant collection or ownership information.

The displayed information must match the selected catalogue entry.

### Bottom Controls

Reproduce the relevant retail controls:

- Leave.
- Preview rotation.
- Hide Player / Hide Armor controls when applicable.
- Purchase.
- Refund when eligible.
- Cart interactions if supported in the retail version being replicated.

Purchase buttons must accurately reflect item eligibility and wallet balance.

Unavailable actions should be visibly disabled, with clear explanations.

## 6. Camera and Scene Behavior

This is a major requirement.

The interface should feel like the player is browsing a physical Trading Post in the game world.

Investigate and reproduce the retail approach to:

- Camera placement.
- Camera transitions.
- Field of view.
- Preview-model positioning.
- Character framing.
- Preview scene depth.
- World backdrop visibility.
- Model lighting.
- Particle rendering.
- Transition animations.
- UI fade-in and fade-out behavior.

The physical Trading Post should remain visually integrated with the browsing experience.

Investigate whether Esteria's client renderer can reproduce retail's relevant model-scene functionality directly.

If not, implement the closest available alternative using the custom client source.

Do not replace the desired experience with a basic 2D item icon or generic dressing-room frame.

On exit, restore the previous normal gameplay camera and controls reliably.

---

# PART II — CATALOGUE AND COMMERCE

## 7. Monthly Rotating Catalogue

Implement a server-controlled, persistent monthly product catalogue.

The default retail-style rotation should occur on the first day of each calendar month.

Support:

- Monthly collections.
- Themed seasonal offerings.
- Limited-time cosmetic releases.
- Returning products from previous rotations.
- Featured items.
- Different prices per product.
- Independently scheduled special offers.
- Configurable rotation schedules.
- Optional event-specific catalogue extensions.

Each product should store enough information to support:

- Unique product identifier.
- Product type/category.
- Underlying item, spell, appearance, mount, or unlock reference.
- Preview asset references.
- Price.
- Currency type.
- Availability window.
- Ownership restrictions.
- Purchase restrictions.
- Associated visual effects or preview configuration.
- Frozen-item behavior.
- Promotional metadata.
- Rotation history.

A rotation must not require recompiling the client or restarting the world server.

The client should retrieve available products from authoritative server data.

### Rotation Behavior

When a new catalogue activates:

1. The previous month's normal offers expire.
2. Previously purchased rewards remain owned.
3. The player's currency balance persists.
4. Frozen offers remain available.
5. Newly scheduled products become available.
6. The monthly activity set is refreshed.
7. The monthly progress reward changes.
8. All active clients receive or retrieve updated catalogue state.

Use authoritative server time, with a clearly defined rotation timezone.

A rotation must be safe to execute multiple times without duplicating rewards or changing completed transactions.

## 8. Item Freezing

Reproduce retail's frozen-item system.

Players can reserve one currently offered product so it remains purchasable after its normal rotation expires.

### Expected Interaction

1. Player selects an item in the catalogue.
2. Player drags the product into the frozen-item slot or uses an equivalent retail-supported interaction.
3. The interface visually acknowledges the frozen item.
4. Server records the frozen offer.
5. The frozen product remains available across monthly resets.

The frozen item must retain its reserved purchase offer until purchased, removed, or replaced.

### Replacing Frozen Items

If a player attempts to freeze another item while the slot is occupied:

- Show an appropriate confirmation.
- Explain that the existing frozen offer will be replaced.
- Require confirmation before replacing it.
- Update the server-side record.
- Restore the old offer to ordinary availability only if its rotation is still active.

Do not allow two frozen products unless explicitly configured as an Esteria-specific extension.

Frozen-item data should be account-wide and persist across logout, character switching, crashes, and server restarts.

## 9. Product Purchases

Build fully transactional server-side purchasing.

### Purchase Flow

1. Player selects an eligible product.
2. The interface displays the price and purchase action.
3. Player clicks Purchase.
4. A confirmation dialog identifies the item and cost.
5. Server revalidates the offer and account.
6. Server validates sufficient currency.
7. Currency is deducted.
8. The reward entitlement is granted.
9. Purchase history is recorded.
10. The interface updates ownership and balance.
11. A successful purchase animation and sound play.

All steps affecting currency, purchase history, and entitlement must be atomic or recoverable.

### Purchase Validation

The server must independently validate:

- Product existence.
- Active or frozen availability.
- Account ownership.
- Duplicate purchase eligibility.
- Actual price.
- Currency balance.
- Product restrictions.
- Reward validity.
- Transaction state.

Never trust a price, item ID, ownership flag, or currency amount supplied by the client.

Protect against simultaneous purchases from multiple characters, duplicated requests, interrupted sessions, and replayed transactions.

## 10. Shopping Cart and Refunds

Investigate the contemporary retail Shopping Cart behavior and recreate it where technically practical.

Support:

- Adding products to a cart.
- Removing products.
- Displaying total cost.
- Purchase confirmation.
- Server-authoritative checkout.
- Clear cart and failed checkout states.

A cart checkout must be all-or-nothing where possible, rather than silently purchasing only some items.

### Refunds

Implement a retail-inspired refund system, with an approximately two-hour eligibility window as a configurable baseline.

Only refund an item if the server confirms that its transaction and reward state remain eligible.

Requirements:

- Refund confirmation.
- Original purchase-price refund.
- Ownership or entitlement revocation.
- Proper handling of appearance unlocks and mounts.
- Protection against refunds after an item has been irreversibly consumed or used.
- Immutable purchase/refund audit trail.
- Prevention of duplicate refunds.

Do not implement refunds by simply awarding currency and deleting an inventory item without checking related collection unlocks.

---

# PART III — REWARDS AND ACCOUNT COLLECTIONS

## 11. Strictly Cosmetic Rewards

The Trading Post must never distribute combat advantages.

Allowed categories:

- Mounts.
- Companions and battle pets.
- Toys.
- Cosmetic armor appearances.
- Cosmetic weapon appearances.
- Ensembles.
- Cosmetic enchantment illusions.
- Decorative effects.
- Cosmetic-only novelties.

**Important:** Armor and weapon appearances are allowed, but they must not provide combat statistics, weapon damage upgrades, procs, bonuses, or special advantages.

For Esteria's custom cosmetic items, ensure that their appearance and functional equipment data are separated appropriately.

## 12. Account-Wide Unlocks

Where supported by Esteria, Trading Post rewards should unlock account-wide.

Buying a mount, toy, appearance, or cosmetic should grant the appropriate account entitlement.

Ensure purchases synchronize across characters.

Investigate our existing collection systems before implementing anything new.

If our current 3.3.5a client lacks retail's account-wide collection behavior, integrate with the custom collection infrastructure already present in Esteria or extend it.

Account-wide purchase history and ownership must not be based solely on the presence of an item in one character's inventory.

Handle:

- Already-owned products.
- Character restrictions.
- Partial collection ownership.
- Ensemble ownership.
- Duplicate appearances.
- Character deletion.
- Character transfers between supported realms.
- Account collection synchronization.
- Failed reward delivery.

---

# PART IV — UNIVERSAL CURRENCY INTEGRATION

## 13. Shared Cosmetic & Convenience Currency

The Trading Post must integrate with Esteria's existing or planned **Universal Cosmetic & Convenience Currency**.

Do not introduce an entirely separate independent currency system unless it is required as an internal adapter.

The Trading Post should operate as one consumer of the universal currency.

The wallet should support:

- Account-wide balances.
- Persistent transaction records.
- Server-side balance validation.
- Currency grants.
- Currency deductions.
- Refunds.
- Administrator adjustments.
- Configurable earning restrictions.
- Real-time balance updates.
- Protection against currency duplication.

All systems consuming this currency should use the same authoritative wallet service.

### Earning the Currency

Players should be able to earn currency by participating in regular Esteria gameplay, including:

- Questing.
- Dungeons.
- Raids.
- PvP.
- World events.
- Exploration.
- Achievements.
- Profession activities.
- Seasonal events.
- Loot Crates.
- Casino and minigame participation.
- Additional supported progression systems.

Currency grants should be based on configurable, validated gameplay events rather than arbitrary client requests.

For repeatable activities, implement appropriate eligibility checks, anti-farming safeguards, and configurable earning limits.

Casino and loot-crate integration must be designed so players cannot repeatedly generate currency through no-risk, self-funding loops.

Do not make purchasing randomized rewards necessary to complete the monthly Trading Post progression system.

### Currency Philosophy

The universal currency should reward participation across many gameplay styles.

A player who prefers questing should be able to earn meaningful currency.

A player who primarily raids or participates in PvP should also have viable earning paths.

Avoid forcing players into one specific activity.

Do not grant more valuable cosmetic currency simply because an activity involves higher combat power or greater player expenditure unless explicitly configured.

## 14. Retail-Style Collector's Cache

Implement the physical Collector's Cache at each Trading Post.

Retail baseline behavior:

- A monthly collectible currency grant.
- A one-time introductory bonus, if configured.
- A distinct interaction with the cache.
- Clear visual feedback when claiming rewards.

For Esteria, make the monthly amount configurable.

Use 500 currency as an initial retail-style reference value, subject to the economy configuration.

Each eligible account may collect its monthly allocation only once.

Claiming it on one character must prevent duplicate claims on another.

Support unclaimed monthly allocations according to an explicitly defined policy.

The cache should visually indicate when a reward is available.

---

# PART V — TRAVELER'S LOG

## 15. Monthly Activity System

Reproduce retail's Traveler's Log as closely as practical.

This is an integral feature, not an optional achievement list.

Create a dedicated interface panel or tab for:

- Monthly activities.
- Activity categories.
- Activity descriptions.
- Progress counters.
- Completion states.
- Monthly progress bar.
- Currency reward thresholds.
- Featured monthly completion reward.
- Time remaining in the current month.

The retail baseline commonly provides up to 500 additional Trader's Tender through monthly activities, with a separate completion reward.

Esteria should integrate these mechanics with the universal currency, using configurable values.

### Activity Types

Support objectives such as:

**Questing**
- Complete quests.
- Complete daily or repeatable objectives.
- Finish designated questlines.

**Dungeons**
- Complete eligible dungeons.
- Defeat specific bosses.
- Complete dungeon objectives.

**Raids**
- Defeat raid encounters.
- Complete eligible raid activities.

**PvP**
- Participate in battlegrounds.
- Win eligible matches.
- Complete PvP objectives.

**Exploration**
- Discover new locations.
- Complete exploration milestones.

**Professions**
- Craft eligible items.
- Gather resources.
- Complete profession challenges.

**Esteria Systems**
- Participate in housing activities.
- Complete perk-related objectives.
- Participate in approved loot-crate activities.
- Complete casino or minigame objectives.
- Participate in seasonal custom events.

The implementation should support new activity types without requiring extensive changes to the Traveler's Log UI.

### Monthly Progression

Players should accumulate progress points from completed activities.

Implement configurable reward thresholds.

A default retail-style example:

| Progress | Currency Reward |
|---|---|
| 200 points | 100 |
| 400 points | 100 |
| 600 points | 100 |
| 800 points | 100 |
| 1,000 points | 100 + monthly completion reward |

These are starting defaults, not hardcoded restrictions.

Multiple different activities should contribute toward the same monthly bar.

Players should not need to complete every available activity to reach the maximum reward.

### Monthly Completion Reward

At full progression, the player receives an exclusive cosmetic reward.

Examples:

- A mount.
- A companion.
- An ensemble.
- A toy.
- A cosmetic effect.

The reward must have a preview in the Traveler's Log where supported.

Track completion account-wide and prevent duplicate awards.

### Activity Tracking

Progress must be updated from authoritative server events.

Track unique encounters or eligible completions where necessary.

Do not award progression based solely on unverified client notifications.

Support:

- Repeated eligible objectives.
- Account-wide objective completion.
- Monthly reset.
- In-progress objective tracking.
- Progress notifications.
- Reward-claim state.
- Multiple simultaneous objectives.
- Capped progression.
- Bonus progress periods when configured.

---

# PART VI — BACKEND ARCHITECTURE

## 16. Server Systems

Create or extend server-side services responsible for:

1. Trading Post catalogue management.
2. Monthly rotation scheduling.
3. Universal currency wallet integration.
4. Item purchase validation.
5. Item ownership and entitlements.
6. Frozen-item management.
7. Collector's Cache grants.
8. Traveler's Log activity tracking.
9. Monthly completion rewards.
10. Shopping cart checkout.
11. Refund eligibility and processing.
12. Account state synchronization.
13. Administrative tools.
14. Transaction auditing.

Prefer clean AzerothCore module integration rather than scattering feature-specific logic throughout unrelated core systems.

Reuse existing Esteria services where applicable.

### Suggested Persistent Data Model

Inspect existing database structures first.

If required, introduce entities equivalent to:

- `trading_post_products`
- `trading_post_rotations`
- `trading_post_rotation_products`
- `trading_post_account_state`
- `trading_post_frozen_items`
- `trading_post_purchases`
- `trading_post_refunds`
- `trading_post_activity_definitions`
- `trading_post_monthly_activities`
- `trading_post_activity_progress`
- `trading_post_monthly_rewards`
- `trading_post_account_reward_claims`
- `trading_post_admin_audit`

These names are conceptual. Adapt the schema to the existing project.

Use appropriate keys, indexes, constraints, and transaction boundaries.

Avoid duplicating existing wallet or collection data into separate competing authoritative tables.

### Required Backend Guarantees

- Server authority over prices and balances.
- Persistent account-wide state.
- Safe concurrent transactions.
- Idempotent claims and purchase requests.
- Correct behavior across monthly boundaries.
- Recovery from interrupted operations.
- Clear transaction and entitlement logs.
- No duplicate currency claims.
- No duplicate rewards from replayed requests.
- No unvalidated client-controlled currency grants.

## 17. Client/Server Communication

Investigate our custom protocol and client networking implementation.

Determine the cleanest method for transmitting:

- Catalogue information.
- Product selection data.
- Wallet balance.
- Purchase requests and results.
- Refund requests and results.
- Frozen-item operations.
- Monthly activity progress.
- Collection ownership status.
- Rotation time information.

Prefer native or appropriately extended client/server communication, taking advantage of our available client source.

Do not use insecure addon messages as the authoritative foundation for purchases or currency.

Implement clear request/response semantics and state synchronization.

After a purchase, the interface must display the result confirmed by the server, not an assumed client-side success.

---

# PART VII — ASSETS, UI AND ANIMATIONS

## 18. Retail Assets

Investigate retail Trading Post assets and determine which are compatible or can be adapted.

Relevant categories include:

- UI textures.
- Currency icons.
- Window decorations.
- Buttons.
- Scrollbars.
- Frozen-slot artwork.
- Merchant stalls.
- Signage.
- Mannequins.
- Preview backdrops.
- Model scenes.
- Animations.
- Sound effects.
- Lighting effects.
- Collection presentation assets.

Use our available asset pipeline and existing client modifications where appropriate.

Maintain the original retail visual language wherever practical.

Do not silently replace unavailable retail assets with unrelated generic interface artwork.

Document unavailable assets and create a compatibility solution where feasible.

## 19. Animation Fidelity

Replicate the feel of the retail browsing interface.

Required animation categories:

- UI entrance.
- UI exit.
- Product selection transition.
- Model appearance transition.
- Mount entrance or summon animation.
- Mount idle animation.
- Weapon animation.
- Character preview idle animation.
- Frozen-item confirmation.
- Purchase success.
- Currency collection.
- Monthly reward unlock.

Use relevant sound cues to reinforce interactions.

Preserve responsiveness: animations should enhance the experience without blocking normal interaction unnecessarily.

## 20. Preview Engine

Develop a reusable preview implementation for the supported reward types.

The engine must account for:

- Different races and character sizes.
- Mount scale.
- Model orientation.
- Weapon attachment points.
- Equipment appearances.
- Multiple equipment slots.
- Model animation sequences.
- Visual effects.
- Camera framing.
- Preview cleanup and resource release.

Where the modern retail model-scene functionality cannot be directly ported, construct a compatible client-side implementation.

The preview must never actually grant or equip the product permanently before purchase.

---

# PART VIII — ADMINISTRATION AND LIVE OPERATIONS

## 21. Administration

Provide a clean configuration and administrative interface suitable for running a persistent MMO server.

Administrators must be able to:

- Add products.
- Remove products.
- Set prices.
- Configure availability.
- Schedule monthly rotations.
- Select monthly progression rewards.
- Configure Traveler's Log activities.
- Change activity requirements.
- Configure earning rates.
- Configure monthly currency allocations.
- Inspect account balances.
- View purchase and refund history.
- Correct individual account issues.
- Schedule seasonal events.
- Preview future catalogue rotations.

Prefer database/configuration-driven operations over hardcoded C++ changes.

Support controlled hot reloads where practical.

All administrative currency and entitlement changes must be logged.

---

# PART IX — TESTING AND ACCEPTANCE

## 22. Mandatory User Journey Tests

Test the following complete experiences.

### Scenario A — First-Time Visitor

1. New player approaches the Trading Post.
2. Interacts with the merchant.
3. Receives the onboarding experience.
4. Opens the shop.
5. Browses multiple products.
6. Previews a mount.
7. Rotates its model.
8. Toggles Hide Player.
9. Exits the shop.
10. Collects the introductory or monthly cache reward.

All interactions must work without errors.

### Scenario B — Buying a Mount

1. Player selects a mount.
2. The character appears riding the mount in the preview.
3. The proper animations play.
4. Player confirms purchase.
5. Currency decreases.
6. The mount entitlement is awarded.
7. The shop reflects ownership.
8. The purchased mount becomes available through Esteria's collection system.

### Scenario C — Buying Cosmetics

1. Player previews armor appearances.
2. The preview correctly displays those appearances.
3. Existing equipment is not changed.
4. Player buys the cosmetic.
5. Appearance entitlement is granted.
6. Other eligible characters can access the unlock.
7. No combat statistics are awarded.

### Scenario D — Freezing an Item

1. Player freezes an item.
2. Logs out.
3. Switches characters.
4. The frozen item remains visible.
5. The month rotates.
6. The frozen item remains available.
7. Player buys it.
8. The frozen slot updates correctly.

### Scenario E — Traveler's Log

1. Player opens the monthly activity interface.
2. Completes qualifying gameplay activities.
3. Activity counters update.
4. Progress points accumulate.
5. Threshold rewards become available.
6. Currency is granted once.
7. Full progression grants the monthly cosmetic reward.
8. Progress remains consistent across characters.

### Scenario F — Concurrency and Failure

Test:

- Double-clicked purchases.
- Two characters purchasing simultaneously.
- Disconnect during purchase.
- Server restart during rotation.
- Duplicate claim requests.
- Purchase with insufficient funds.
- Purchase after offer expiration.
- Purchase of an already-owned product.
- Refund after expiration.
- Duplicate refund attempts.
- Client and server catalogue mismatch.
- Malformed or unauthorized requests.
- Invalid preview assets.

Ensure no test can generate duplicate currency or unintended entitlements.

## 23. Performance Requirements

The Trading Post must not noticeably degrade normal gameplay performance.

Evaluate:

- UI opening time.
- Catalogue retrieval.
- Model loading.
- Camera transitions.
- Animation performance.
- Network traffic.
- Database query efficiency.
- Large catalogues.
- Multiple simultaneous users.
- Rotation processing.

Use caching or incremental state updates where appropriate, without compromising server authority.

---

# PART X — IMPLEMENTATION WORKFLOW

## 24. Initial Repository Audit

Before editing code:

1. Inspect Esteria's current client architecture.
2. Inspect the AzerothCore server and custom modules.
3. Locate existing currency and collection systems.
4. Locate relevant UI and model-preview code.
5. Locate camera-control and animation hooks.
6. Determine existing custom communication methods.
7. Check existing asset support.
8. Identify features that can be reused.
9. Identify missing retail dependencies.
10. Determine the safest integration architecture.

Do not assume a feature is absent without searching the repository.

## 25. Implementation Phases

Organize the work into meaningful phases.

**Phase 1 — Research and Compatibility**
- Map retail functionality.
- Audit current source.
- Identify dependencies.
- Produce implementation architecture.

**Phase 2 — Backend Foundation**
- Catalogue.
- Rotation system.
- Universal wallet integration.
- Purchases.
- Ownership.
- Frozen items.
- Database persistence.

**Phase 3 — Client Integration**
- Trading Post interface.
- Camera behavior.
- Catalogue browsing.
- 3D previews.
- UI animations.
- Client/server synchronization.

**Phase 4 — Progression**
- Collector's Cache.
- Traveler's Log.
- Monthly activities.
- Completion rewards.

**Phase 5 — Extended Commerce**
- Cart checkout.
- Refund functionality.
- Additional product categories.
- Returning and seasonal offers.

**Phase 6 — Testing and Polish**
- End-to-end testing.
- Account-wide consistency.
- Animation and visual fidelity.
- Performance.
- Failure recovery.

Each phase must result in working, testable functionality rather than disconnected prototypes.

## 26. Required Deliverables

Provide:

1. Retail feature comparison.
2. Architecture assessment.
3. Compatibility and dependency findings.
4. Implementation plan mapped to the actual repositories.
5. Server implementation.
6. Client implementation.
7. Necessary database migrations.
8. Configuration files.
9. Asset integration instructions.
10. Administrative functionality.
11. Test coverage and verification results.
12. Documentation of limitations and deviations.

For each completed feature, identify the source files changed and describe how the functionality was tested.

Do not claim a feature is operational until its client/server behavior has been verified.

## 27. Final Success Criteria

The implementation is successful when:

- Players can physically visit the Trading Post.
- Interacting with its NPC opens an immersive retail-style catalogue.
- Products are presented with functional 3D previews.
- Mounts display the player's character riding them.
- Cosmetic equipment previews correctly.
- Preview controls and animations function.
- Purchases and refunds are server-authoritative.
- Products rotate automatically.
- Frozen items persist through rotations.
- The account-wide wallet stays synchronized.
- Rewards correctly unlock in the appropriate collections.
- The Collector's Cache functions.
- The Traveler's Log tracks actual gameplay.
- Monthly progression awards rewards correctly.
- The system survives disconnects, restarts, and concurrent transactions.
- The UI behaves and looks substantially like retail's Trading Post.
- No shop product provides combat advantages.

### Final Direction

Treat this as a **native retail feature backport**, not a generic shop addon.

We have access to our modified client source and server code, so do not restrict the design to what an ordinary 3.3.5a addon could accomplish.

Recreate the actual player experience, not merely the appearance of the interface.

Preserve retail behavior wherever possible, while making deliberate, documented modifications for Esteria's universal currency, progression systems, and cosmetic ecosystem.

Begin with the repository audit and retail compatibility mapping, then proceed through the implementation phases using the actual codebase.

The finished system should feel like Blizzard's Trading Post was built directly into Esteria.