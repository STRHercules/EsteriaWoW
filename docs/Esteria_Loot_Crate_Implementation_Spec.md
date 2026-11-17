# Esteria — Loot Crates, Keys & Dynamic Gold Economy

**Implementation specification — v1.0**  
**Platform:** AzerothCore (WotLK 3.3.5a), Esteria's custom client (`wowdecomp`), existing character/inventory and Auction House systems.  
**Deliverable:** A server-authoritative, fully configurable loot-crate feature with a custom in-game UI.  
**Status:** Design specification; not implemented. Example numbers are proposals, not established Esteria balance values.

---

## 1. Feature vision

Introduce a CS:GO-style crate-opening experience to Esteria, with themed crates, matching tradable keys, a responsive gold-based key market, configurable rewards, rotating exclusives, and visually memorable openings. The system should create lasting demand for gold without undermining the player economy or compromising core progression.

**Non-negotiable principles**

1. **Gold sink:** Gold paid for keys minted by the game is permanently removed from circulation. Reselling a key on the Auction House transfers gold between players, apart from ordinary AH fees; it is not a second full sink.
2. **Server authority:** Purchases, pricing, eligibility, reward rolls, item creation, and delivery are validated on the server. The client is presentation only.
3. **Transparent odds:** Each active crate edition displays the complete pool and the true effective probabilities before opening; the total must equal 100%.
4. **One key, one crate, one reward:** Each successful opening consumes exactly one matching key and crate and awards exactly one result, unless a particular edition openly defines bonus rewards.
5. **Player economy:** Keys are real, unbound, stackable inventory items that can be traded, mailed, and listed on the AH. Crate tradability is configurable and should default to tradable as well.
6. **Content-driven:** Designers can configure new crates, reward pools, themes, prices, exclusives, and rotations without hard-coding each release.
7. **No hidden outcome manipulation:** No silent weighting by purchase history, spend, account status, or animation behavior. Any pity/duplicate protection mechanic must be explicitly advertised and reflected in displayed odds.
8. **Backward-compatible development:** Prefer an isolated AzerothCore module and a dedicated client UI package; inspect Esteria's existing systems before adding hooks or modifying core code.

## 2. Reference behavior and visual direction

The attached **Astral Case of the Observer** screenshots and videos show the desired interaction pattern:

- Dark, high-contrast fantasy window with a case title, case icon, short description, and count of cases remaining in the player's bags.
- Prominent horizontal **reward reel**, with rarity-colored item cards passing beneath a fixed gold center indicator.
- A clear **UNLOCK / UNLOCKING…** primary action; opening locks input until a result is established.
- Below the reel, a **“Contains one of the following”** grid showing item icons, labels, quality colors, and individual drop rates.
- Familiar WoW item tooltips, including ownership/“Already known” indicators when appropriate.
- Visually distinct result reveals: e.g., **Epic** with violet rays and **Legendary** with intense gold rays.
- Post-reveal actions: **Open Another**, **Preview**, and **Close**.
- Smooth reel deceleration and a deliberate center stop; the roll is decided on the server before that motion begins.

**Reference odds example (for UI testing only):** Seven rewards at 12% each, one at 10%, and three at 2% each = **100%**. These percentages are from the attachment, not recommended balance for every Esteria crate.

**Esteria art direction:** Custom crate illustrations, item-card borders, animated starfields/particles, rarity-specific sounds, subtle glows, high-tier reveals, and themed reel backdrops. UI quality must be consistent with Esteria's existing item-tooltip border/animation direction. Do not reuse copyrighted retail UI art as final original assets without a suitable right to do so.

## 3. Terminology and data concepts

- **Crate type:** Basic, Rare, Epic, Legendary, Artifact, Cosmetic, Premium, or Custom/Bespoke. This is a *container category*, not necessarily an item quality.
- **Crate edition:** A named, dated release of a crate type, with a specific appearance and immutable reward-pool version, e.g. **Astral Observer — Season One**.
- **Key type:** A distinct inventory item that unlocks compatible crate editions. Keys may be shared within a deliberately configured crate family but are never silently interchangeable.
- **Reward rarity:** Common, Uncommon, Rare, Epic, Legendary, Artifact, or an explicitly custom display classification. This is separate from the crate tier.
- **Reward kind:** Gear, mount, pet, cosmetic appearance, housing decoration, blueprint, toy, emote, effect, crafting material, consumable, or other supported item/unlock.
- **Reward pool version:** Frozen list of reward entries, weights, rules, and effective dates attached to an edition.
- **Primary key purchase:** A key purchased from Esteria's own UI; destroys gold and mints a key.
- **Secondary key purchase:** A player buying an existing key from another player at the Auction House.
- **Opening transaction:** Unique, auditable record tying the consumed crate/key to exactly one committed reward.

## 4. Crate catalog and progression ceilings

The following tiers are initial **design defaults**, not hardcoded rules. Use per-edition minimum/maximum reward quality and eligible reward kinds. A crate's *maximum reward ceiling* means lower-tier cases cannot roll items above their configured ceiling.

| Crate tier | Default minimum | Default maximum | Identity / purpose | Matching key |
|---|---|---|---|---|
| **Basic** | Common | Rare | Entry-level materials, simple cosmetics, modest gear | Basic Key |
| **Rare** | Uncommon | Epic | Better materials and gear, uncommon collectibles | Rare Key |
| **Epic** | Rare | Legendary | Valuable gear and more ambitious themed collections | Epic Key |
| **Legendary** | Epic | Artifact | High-end collectibles, select top-end equipment | Legendary Key |
| **Artifact** | Epic | Artifact | Endgame-oriented rewards and distinctive artifacts | Artifact Key |
| **Cosmetic** | Any visual rarity | Any visual rarity | Appearances, mounts, pets, decorations, emotes; no required combat-power gain | Cosmetic Key |
| **Premium** | Epic | Artifact / named exclusive | More expensive; stronger baseline rewards and curated high-quality pool | Premium Key |
| **Custom / Bespoke** | Configured | Configured | Event, faction, raid, zone, holiday, guild, or special themed releases | Assigned bespoke key |

**Constraints:**

- **Premium** describes an expensive, higher-floor reward pool; it does **not** require real-money payment. Default payment is gold.
- **Cosmetic** is a reward/theme classification, not a new native WotLK item quality value.
- **Custom/Bespoke** is an authoring category, not permission for players to define arbitrary rewards or odds. Admin-approved templates and validation are mandatory.
- New custom qualities, if desired, require a separately planned client/server item-quality extension. Do not assume the stock 3.3.5a quality enumerations support arbitrary additions.
- Maintain separate equipment item-level caps, slot restrictions, character-level restrictions, and season progression limits so crates do not invalidate dungeon, raid, PvP, crafting, and exploration rewards.
- Crates may contain exclusive housing décor, collectible variants, transmog/appearance unlocks, emote scrolls, effects, and toys to integrate with other Esteria systems.

## 5. Acquisition, key ownership, and trading

**Crates can enter the economy through** configured world drops, bosses, quests, achievements, professions, events, vendors, the AH, or a future dedicated crate store. Each source is independently enabled per crate edition. Drop acquisition does not automatically include a key unless a special promotion explicitly specifies it.

**Keys can enter the economy through** the crate UI's primary gold purchase and explicitly authorized event/quest reward grants. Normal production keys are not free-spawning unless set by a designer.

**Trading behavior:**

- Each key is a real inventory item with a unique item template ID. Its stack behavior, tooltip, family, and icon are defined in item metadata.
- Keys must be unbound at creation, tradeable in direct trades, listable on the AH, mailable, and bankable. Avoid special handling that accidentally introduces soulbinding.
- Crates should also be tradeable by default; exceptions must be clearly disclosed.
- The AH remains player-set pricing: supply, demand, bidding, and buyouts decide individual key listing prices. The primary UI price is independent of sellers' listing prices.
- When the UI offers **Buy from Auction House**, either open a supported filtered AH view or provide an explicitly implemented remote market bridge. Do not imply vanilla 3.3.5a can browse or buy from the AH without appropriate context/authorization.
- All usual trade, mailbox, AH, account ownership, duplication, and item-validation protections apply.

## 6. Dynamic gold pricing — game-sold keys

### 6.1 Purpose

Each key family has a server-wide primary sale price that reacts to **verified demand**. Higher real purchase volume gradually raises the price; weak demand lets it drift back toward a baseline. This is inspired by the *market responsiveness* of WoW Tokens, but is **not** a literal replica: game-sold keys have an effectively unlimited supply unless designers impose a stock limit.

### 6.2 Proposed pricing controls

| Setting | Suggested default | Meaning |
|---|---:|---|
| Base price | Per key family | Configured starting gold price |
| Price floor | 50% of base | Lowest permitted automatic price |
| Price cap | 300% of base | Highest permitted automatic price |
| Recalculation interval | 30 minutes | Price moves in measured steps, not on every click |
| Max change per interval | 1% | Dampens rapid manipulation |
| Max change per 24 hours | 10% | Daily circuit breaker |
| Demand window | Smoothed 24h volume plus 7d baseline | Reduces noise from short spikes |
| Quote lifetime | 30 seconds | Short-lived server-issued checkout quote |
| Quantity cap per request | Configurable; start at 10 | Limits accidental bulk purchases and RPC spam |

**Algorithm requirements (no specific formula mandated):**

1. Record successful primary key purchases, not attempted clicks or canceled quotes.
2. Compare rolling verified purchase rates with a configurable normal demand target.
3. Apply smoothed upward or downward movement under floor/cap and time-based circuit breakers.
4. Make upward movements more conservative when volume is concentrated in a few accounts; include anti-manipulation alerts.
5. **Do not automatically use AH listing prices or listing counts as a price oracle** in v1. Sellers can manipulate listings; AH economics can be shown separately as information.
6. Never retroactively change a key's purchase price after checkout.
7. All quantities use server-side gold/copper integers, checked for overflow and the supported character money cap.
8. If price metrics fail, hold the last valid price or fall back to a safe configured baseline; never return a zero or negative cost.

**Illustration:** A Basic Key starts at **100g**. Sustained high primary demand may increase the UI quote gradually toward **110g** (subject to caps); weak demand can reduce it gradually. These numbers demonstrate the mechanism only.

**Gold flow:** A 100g UI purchase removes 100g from the world and creates one key. If the key later sells for 140g on the AH, those 140g move from buyer to seller, minus ordinary AH costs; no additional 140g is minted or destroyed by the key system. This distinction should appear in economy analytics.

**Optional future feature:** Allow players to compare the primary quote to recent AH buyout prices, clearly labeled as informational and potentially stale. Any direct AH order from the crate UI must use authoritative auction transactions.

## 7. Loot tables, probabilities, eligibility, and rotations

### 7.1 Reward-table authoring

Every active edition has a validated, **immutable pool version** containing:

- Reward item/unlock identifier, reward kind, quantity, display name, icon, visual rarity, native item quality, and asset dependencies.
- Exact **integer weight**, with weights summing to a published total (e.g. 10,000 basis points or higher precision). Client percentages are computed from these values.
- Minimum/maximum player eligibility, season/level rules, forbidden combinations, and award-delivery method.
- Edition exclusivity, start/end timestamps, ownership recognition, and duplicate policy.
- A preview asset reference when a renderable model exists; otherwise icon/tooltip fallback.

**Default selection method:** One direct weighted choice among eligible **published entries**, not an undocumented second-stage reroll. The admin system rejects pools with missing items, mismatched keys, impossible requirements, disallowed reward quality, zero weights, sum errors, or references to absent client assets.

### 7.2 Displayed odds

- The UI shows individual item percentages and a rarity/category summary.
- The complete displayed list is the actual list the server will draw from, including any conditional eligibility changes.
- Percentages must total **100%** at the displayed precision; use consistent rounding and an exact-value tooltip where necessary.
- The opening locks a specific pool-version ID, so a rotation or hot reload cannot silently change probabilities halfway through.
- If an item is unusable by a character, use a documented policy: either exclude it **before** showing personalized odds, or allow it as a tradeable result and communicate that clearly. Never silently replace a winning reward after drawing it.
- Player history, premium account status, key price, and reel stopping behavior do not modify hidden odds.

### 7.3 Duplicate ownership

- Display **Already Known / Owned** for learnable mounts, pets, appearance unlocks, and other detectable collectibles.
- **Default v1:** Duplicates remain possible and tradeable where supported, as in the reference UI.
- If duplicate protection, pity, upgrade streaks, or salvage are later introduced, they must be **edition-specific, fully visible**, and have their effective per-player odds recomputed before opening.
- A unique reward that cannot be usefully awarded more than once needs an explicit configurable duplicate policy: tradeable token, alternate reward of disclosed value, or pre-roll exclusion; no silent reward deletion.

### 7.4 Rotating exclusives

- Use seasonal editions (recommended 4–8 weeks as a starting cadence, configurable), event editions, and rare featured items.
- Show **Featured**, **Limited Edition**, **Ends [date/time]**, and **Returns TBD** labels with a countdown where appropriate.
- **Recommended rule:** A crate's edition and pool version are locked when that crate enters circulation. Existing unopened crates retain their clearly labeled edition after a rotation; new crates use the new edition. This prevents a player from buying or finding a crate under one advertised table and unknowingly receiving another.
- Publishing a rotation creates a **new version**. Do not mutate a pool already tied to issued crates or completed openings.
- Keys can remain reusable across editions of the same family only if explicitly configured; the UI must show compatibility.
- Retirement removes an edition from *new distribution*, not from players' lawful inventories.

## 8. Player-facing UI and opening animation

### 8.1 Access points

- Use a crate item in bags (right-click / custom Use behavior).
- Dedicated launcher/menu icon or in-game **Loot Crates** button.
- Optional themed NPCs or premium shop entry points, without requiring an NPC once the full interface is supported.

### 8.2 Primary screen layout

**Header:** Crate name, themed artwork, edition tag, remaining crate count, key count, and close button.  
**Reel:** Horizontal ribbon of rarity-coded rewards, fixed gold pointer, soft edge masks, responsive selection glow.  
**Actions:** **Open Crate** if key held, **Buy Key — [current price]** otherwise, optional **Find on AH**, optional **Preview Rewards**.  
**Contents:** Responsive grid of all potential rewards with icon, name, visual grade, exact odds, owned status, tooltips, and preview action.  
**Footer:** Relevant odds disclosure, edition expiration, gold balance, price quote expiry, sound/animation preferences.

**UI behaviors:**

- If no crate: show **You need this crate** and its possible sources.
- If crate but no key: show matching key with current UI gold quote and an AH search action.
- If insufficient gold: disable checkout and explain why.
- If key is held: show exactly how many can be opened and display a single-open confirmation if configured.
- If reward preview has a usable model, offer a 3D spin/inspect or dressing-room view; otherwise show a stable icon and full tooltip. Never invent a missing 3D model.
- Show current and effective odds **before** the gold/key is committed.

### 8.3 Animation state machine

1. **Idle:** Pool and odds loaded from server. Gold quote and key counts validated.
2. **Pending authorization:** User presses Open; block repeated clicks and request a unique opening ID.
3. **Committed:** Server validates ownership, consumes exactly one matching key and crate, rolls once, durably records reward and its delivery plan, then returns the authorized result.
4. **Spinning:** Client animates many item cards beneath the gold marker with easing, particles, soft audio cues, and increasing anticipation. The result is fixed.
5. **Settling:** Center marker aligns with the server-selected item. Adjacent cards dim; selected card glows.
6. **Reveal:** Full-screen/overlay rarity-specific presentation and sound; Epic uses violet, Legendary gold, Artifact its own recognizable treatment, Cosmetic/Premium reflect *reward rarity* rather than merely the crate category.
7. **Claimed:** Reward is already delivered or durably queued; show **Open Another**, **Preview**, **Close**. Buttons never trigger a second award for the same opening.

**Suggested motion:** 6–9 seconds standard, with a faster/reduced-motion mode. Provide **Skip Animation** after the outcome is already committed; skipping affects visuals only. Do not make players wait on animation to secure their item.

**Accessibility:** Reduced motion, mute/volume settings, screen-scale support, text descriptions of rarity (not color alone), keyboard navigation, and no flash-only information.

### 8.4 Feedback polish

- Distinct reveal intensities for low-, mid-, and high-tier rewards.
- Separate music stingers from interface sounds so a player can mute one without losing all audio.
- Optional server-wide first-discovery or jackpot announcements with opt-out and spam throttling.
- After an opening, update bag counts, owned statuses, display odds for the next eligible opening, and last reward history immediately.

## 9. Server architecture

**Implement as a dedicated AzerothCore module wherever practical**, avoiding invasive core modifications. Use existing module/script hooks first; add narrowly scoped Esteria-specific hooks only where needed. Client work should integrate with the existing custom client UI and patch/update pipeline.

### Client implementation strategy

The 3.3.5a interface is highly Lua-driven. Esteria can package a native-feeling UI as custom client assets/frames while keeping business logic inside AzerothCore. If the existing `wowdecomp` project exposes a supported native UI entry point or communication hook, use it; otherwise use the project's established addon/custom RPC bridge. Treat a new custom opcode as a deliberate protocol change requiring coordinated launcher/client/server releases, not as a default shortcut. No client rendering path is permitted to compute prices or roll rewards.

### Components

1. **Crate Catalog Service:** Defines types, editions, key compatibility, acquisition sources, and assets.
2. **Reward Pool Manager:** Validates immutable pool versions, eligibility, odds, exclusivity, and effective tables.
3. **Key Pricing Service:** Maintains server-global prices, moving demand metrics, quote signatures/IDs, guardrails, and history.
4. **Key Purchase Service:** Validates current gold and quotes, charges gold, mints keys, and logs the actual destroyed amount.
5. **Opening/Reward Service:** Validates key/crate, allocates idempotency IDs, rolls weighted selection, consumes inventory, records reward, and guarantees eventual delivery.
6. **Auction/Trade Integration:** Makes item templates normally marketable and optionally exposes filtered AH results through authorized server calls.
7. **Client Communication Layer:** Defines versioned authenticated client-server requests and responses using Esteria's supported integration path. No trust in client-supplied odds, reward IDs, gold, or ownership.
8. **Admin & Analytics:** Author/publish pools, override safe configuration, issue test grants, manage rolls, inspect sinks and distribution, and flag suspected manipulation.

### Conceptual network operations

- `ListCratesAndEditions` → enabled crates, active offers, client asset references.
- `GetCrateDetails` → compatible key, counts, immutable pool version, effective exact odds, eligibility.
- `GetKeyQuote` → key type, unit price, quantity limit, price/version, short expiration, quote token.
- `BuyKey` → quote token and quantity; returns authoritative updated gold/key counts and receipt.
- `RequestOpening` → crate instance and matching key instance (or qualified stack), edition/pool version, client idempotency request ID.
- `GetOpeningStatus` → committed result and delivery status after reconnect/crash.
- `GetHistory` → player's recent crate openings and receipts.
- `GetKeyMarketLink` → filtered key search or AH integration metadata, if implemented.

The server independently verifies every requested object and its current ownership. Never accept a `rewardId`, final reel position, quoted price, or random seed chosen by the client.

## 10. Persistence and data model

Use migrations and clear table ownership; names below are conceptual and can be adapted to Esteria naming conventions.

| Entity | Essential fields |
|---|---|
| `loot_crate_type` | ID, slug, type/tier, key family, name, theme, active flag, default tradability |
| `loot_crate_edition` | ID, type ID, edition name, edition item template, start/end, immutable pool version, lifecycle status |
| `loot_key_type` | ID, matching item template, compatibility group, pricing profile, tradability |
| `loot_reward_pool_version` | Version ID, edition ID, published timestamp, checksum, total weights, immutable state |
| `loot_reward_entry` | Pool version, reward item/unlock ID, reward kind, integer weight, rarity/quality, quantity, eligibility, duplicates policy |
| `loot_key_price_state` | Key family, base/floor/cap, demand metrics, last price, recalculation times, halt/fallback flag |
| `loot_key_purchase` | Unique receipt ID, account/character, key type, quantity, unit price, total gold removed, time, status |
| `loot_opening` | Unique opening ID, account/character, crate and key instance IDs, pool version, winning entry, RNG/audit reference, state, timestamps |
| `loot_reward_delivery` | Opening ID, awarded instance/spell, delivery medium, claim state, retry count, error reason |
| `loot_economy_audit` | Event ID, account/character, event type, key/crate/reward refs, gold delta, reconciliation refs |
| `loot_admin_action` | Actor, permission, before/after version, justification, time |

Persist enough item-instance ownership information to reconcile trade, bank, AH, and mail transitions. Keep audit/history bounded and indexed; do not repeatedly query the full history in the opening hot path.

## 11. Atomicity, RNG, fraud resistance, and recovery

**Correctness rules:**

- Each action receives a unique idempotency ID. Repeating a successful buy/open request returns its existing receipt/result; it never creates another key or reward.
- A key purchase must not debit gold without either minting the key or leaving a durable recoverable purchase state.
- An opening must not consume a crate/key without a durable, recoverable reward-delivery record.
- Use the character DB's supported transactional boundaries for coupled inventory and audit mutations. Where award delivery (e.g., mail) spans boundaries, use a **durable outbox/reconciliation worker**, not an assumption that separate systems are magically one transaction.
- Roll server-side with a well-seeded, unbiased RNG and integer weights; record the pool version, winner, and RNG audit metadata without leaking exploitable state.
- Never send an uncommitted reward as a guaranteed final prize. Once committed, the prize is owed even if the client disconnects or skips the animation.
- If bags are full, use a validated, retry-safe fallback such as in-game mail. If an unlock is account-wide or spell-based, use a deduplicated unlock grant.
- A relog, realm restart, network timeout, or crash resumes/reconciles the opening, rather than rerolling it.
- Rate-limit requests; guard against replay, fake quote IDs, stale ownership, concurrent opens on a shared stack, AH listing transitions, item cloning, duplicate delivery, overflow, and compromised client parameters.
- Log every privileged admin grant, odds change, price override, and withdrawal of an edition.

**Recommended transactional states:** `Requested → Reserved → Committed → Delivery Pending → Delivered → Revealed/Viewed`; retry from any persisted state. `Reserved` must not strand inventory permanently if the request cannot commit.

## 12. Economy integrity and balance

- For every new crate edition, define a **gold sink target**, expected reward value, inflation impact, supply pathways, and likely AH price range. Treat all numeric targets as live-tunable design values, not guaranteed player returns.
- Measure gold destroyed through initial key sales separately from gold traded on the AH.
- Do not let common drops routinely vendor for more gold than the typical key price; otherwise the feature can become a gold faucet.
- Keep powerful equipment restricted by progression season, level/ilvl ceiling, and balance review. Cosmetic and housing rewards can add collector demand without power escalation.
- Higher-tier crates raise the **floor and/or ceiling** of reward quality, but should not nullify the uniqueness of boss, crafted, exploration, or prestige rewards.
- Avoid hidden guaranteed jackpot paths and off-ledger staff grants. If pity is introduced, fund and expose it in the published odds model.
- Default to **gold-only** for primary key purchase. The original request's unfinished “Players can also spend …” is an unresolved payment requirement. A future universal in-game shop currency may be supported **only after** its exchange rate, source, sink effect, and disclosure rules are decided. Real-money purchase is **not** included in v1.
- If any real-money-purchased currency is later permitted to buy randomized rewards, separately review applicable legal, platform, disclosure, and age-protection requirements before launch.

## 13. Admin tools and content workflow

**Required staff capabilities:**

1. Create crate families and assign matching key items.
2. Create editions, attach artwork, choose loot-source distribution, and set active dates.
3. Add rewards, set integer weights, rarity, exact item identifiers, quantity, prerequisites, and duplicate behavior.
4. Preview the resulting percentages and summary by reward rarity.
5. Run **publish-time validation** on odds, reward ceilings, eligibility, references, client assets, tradability, and database dependencies.
6. Publish immutable edition versions; schedule future rotations and archive old ones.
7. Configure per-family gold base/floor/cap and demand settings; pause sales safely without invalidating owned keys.
8. Simulate dry-run openings in a test realm, including guaranteed forced-result visual tests that cannot be used in production rewards.
9. Inspect purchase/open/delivery receipts, suspicious purchasing spikes, price changes, reward distributions, and failures.
10. Recover failed deliveries idempotently, with a two-person review process for exceptional manual compensation.

**Analytics dashboard:** Total keys minted; gold destroyed; key stock currently held/listed if obtainable; crate edition distribution; opened crates by tier; top reward counts; aggregate expected vs actual outcome rates; new-key sales by hour/day; average quoted price; AH indicative prices (if collected); delivery failures; abandoned openings; invalid/replayed requests. Admin-only rolls and QA items are excluded from production statistics.

## 14. Optional expansions — not v1 blockers

- **Bulk Open / Open 5 / Open 10:** Each opening receives a distinct ledger entry, key/crate consumption, and reward. Show a compact results screen.
- **Collection journal:** Owned/unowned case rewards, season completion, housing décor catalog, mount/pet previews, and tradeable duplicate summaries.
- **Cosmetic shards / duplicate recycling:** Explicit exchange formulas, no hidden impact to normal RNG.
- **Event keys and profession-crafted cases:** Fixed, validated recipes and event supply quotas.
- **Player profile display:** Optional showcase of legendary first discoveries, jackpots, or rare crate-exclusive cosmetics.
- **Price history graph:** Transparent per-key primary quote history, with a separate AH market price indicator.
- **Personalized accessibility and theme settings:** UI scaling, custom reel speed, reduced motion, and colorblind-grade labels.
- **Special bespoke experiences:** Zone-specific world-chest visuals, encounter-specific reel effects, guild event crates, class fantasy packs, seasonal collector bundles, and housing decoration cases.

## 15. Development phases and dependency order

### Phase 0 — Discovery and integration audit
- Inspect existing AzerothCore forks/modules, Esteria client UI/patch loader, custom client-server communication, inventory hooks, item ID conventions, the AH implementation, custom item assets, and any existing shop/universal currency systems.
- Document actual supported extension points. Confirm client build/patch compatibility, and reserve non-colliding item IDs.

### Phase 1 — Functional backend MVP
- Configurable crate/key catalog and one test edition.
- Physical tradeable keys and crates; stable matching rules.
- Fixed-price UI gold purchase as an initial toggleable pricing mode.
- Authoritative one-roll opening with immutable table, inventory consumption, unique receipt, and recoverable reward delivery.
- Item templates/client icons/preview fallbacks; test opening flow and core audit logs.

### Phase 2 — Client experience
- Complete crate browser, full odds grid, key checkout, owned-status badges, compatible-key inventory counts.
- Animated center-pointer reel, rarity effects, preview, opening result screen, sound, reduced motion, reconnect recovery.

### Phase 3 — Market and dynamic pricing
- Verified-demand estimator, guarded price updates, quote lifecycle, per-key price history, admin overrides, monitoring.
- AH key tradability verification and optional filtered AH navigation.

### Phase 4 — Content and live operation
- All eight crate tiers, themed art, content templates, seasonal editions and scheduled rotations.
- Balance simulations, staff dashboards, price safeguards, operational runbook, logs, and alerts.

### Phase 5 — Optional enhancements
- Collection journal, bulk openings, duplicate recycling, special bespoke formats, enhanced 3D reward previews, analytics-driven tuning.

## 16. Acceptance tests / definition of done

**Core behavior**
- A player with the correct crate/key can open exactly one reward; wrong-family key is rejected without item loss.
- Player with zero keys can view the current exact price, buy a key with gold, and use it; gold decreases by precisely the quoted amount.
- Key and crate trading, mail, banking, and AH listing work as their item metadata promises.
- The pool displayed before opening matches the server-side version used for selection and totals 100%.
- The pointer always stops on the server-committed reward; skipping or closing the animation cannot alter or duplicate it.
- Bags-full fallback delivers exactly once; an already-known collectible is clearly marked.

**Reliability and security**
- Repeated buy/open packets with the same transaction ID cannot generate items or rewards twice.
- Simultaneous opens on the same item stack do not overspend or overconsume.
- Disconnect or crash at every transaction state returns the original committed reward or safely unwinds a not-yet-committed action.
- Client-forged price, reward, key ID, and ownership fields are rejected.
- Changing price during a valid quote follows the published quote semantics and never charges an undisclosed amount.
- Rotating an edition cannot rewrite unopened issued crates' promised tables.

**Balance and telemetry**
- Simulate at least 1,000,000 opening trials per representative pool and compare observed frequencies with configured weights using appropriate statistical tolerances; separately verify tiny-probability pools.
- Audit reports correctly distinguish primary key gold destruction from player AH transfers.
- Sharp demand changes respect floor/cap, maximum rate, and fallback behavior.
- Reward quantity, item templates, equipment restrictions, and character currency limits pass validation.

**Client quality**
- All eight crate categories are represented coherently; tooltips and preview fallbacks work even when no 3D model exists.
- Animations are smooth at common WotLK client resolutions and can be skipped/reduced without influencing reward state.
- UI feedback is legible with disabled sounds, color-blind presentation, and enlarged scaling.

## 17. Open decisions for Esteria's design owner

These are product choices, not implementation blockers for Phase 1; build configurable defaults and record decisions before release:

1. **Additional payment route:** What was intended after “Players can also spend…”? Universal shop currency, event currency, fragments, or something else?
2. **Crate sources:** Which editions drop from content versus require gold purchase? Should crates themselves ever cost gold?
3. **Key family sharing:** Does one Premium Key cover every Premium edition, or are keys matched to each individual crate family?
4. **Progression ceiling:** Maximum permitted item level and combat stats for each tier and each season.
5. **Ownership/duplicate policy:** Allow tradeable duplicates (default) or enable an advertised protection/exchange mechanic for selected editions?
6. **AH integration:** Standard in-person AH listing/search (minimum) or a custom remote AH search/buy panel (later)?
7. **Season cadence:** Duration, return policy for exclusives, and whether old editions stay permanently tradeable (recommended yes).
8. **Pricing constants:** Actual base gold amounts, maximum price movement, purchase limits, and initial target demand by key family.

## 18. Notes for the implementing agent

Before editing code, inspect the **actual** Esteria repositories and current module conventions. Produce a brief integration map showing which files, hooks, database tables, custom UI components, item definitions, network messages, and asset packaging points you will touch. Do not assume any system is absent or present without inspecting it. Reuse existing modules and common services. Keep server-authoritative logic separate from presentation. Use additive migrations, feature flags, test-realm fixtures, security tests, and rollbacks. Do not modify unrelated item-quality systems, break native AH behavior, or duplicate existing shop mechanics merely to support crates. Preserve multiplayer consistency and crash recovery above animation polish.

### Reference documentation for technical discovery

- AzerothCore — [Create a Module](https://www.azerothcore.org/wiki/create-a-module) and [ScriptAI hooks](https://www.azerothcore.org/wiki/hooks-script).
- AzerothCore — [`item_template` fields, quality, flags, and bonding](https://www.azerothcore.org/wiki/item_template).
- AzerothCore — [`auctionhouse` persistent auctions](https://www.azerothcore.org/wiki/auctionhouse).
- AzerothCore — [Client item-data caching](https://www.azerothcore.org/wiki/client-cache-wdb).
- The supplied Astral Case of the Observer screenshots and opening videos: visual inspiration only, not server code or approved reward economy settings.

---

**Implementation outcome:** A flexible crate/key framework, not a one-off Astral Case clone: content authors can ship new themed crates and seasons without rewriting the feature, while every purchase and reward remains economically auditable and technically safe.
