# Esteria Character Select — Architecture & Implementation Plan

Companion to `character-select-redesign.AUDIT.md`. Read the audit first: it establishes
what already exists and therefore what must **not** be rewritten.

---

## Build status

**Rounds 1-4 — audit + every pure-logic layer complete.** No client files touched
yet; nothing deployed.

| Artifact | State |
|---|---|
| `ECS_Constants.lua` | written — all tunables centralised (spec 35) |
| `ECS_Schema.lua` | written — race/class/faction with fallbacks (spec 14/15/27/33) |
| `ECS_Order.lua` | written — visual↔real mapping (spec 24) |
| `ECS_Data.lua` | written — normalized records, safe under BOTH GetCharacterInfo layouts (spec 23) |
| `ECS_Persistence.lua` | written — sharded cvar store, versioned, read-back verified (spec 11/34) |
| `ECS_Notes.lua` | written — note hygiene + editor draft/commit/cancel state machine (spec 12) |
| `ECS_Anim.lua` | written — one self-disabling pooled tween driver (spec 7/32) |
| `ECS_Search.lua` | written — query semantics, Escape rules, summary/empty states, match highlighting (spec 8/30/31) |
| `ECS_Modal.lua` | written — bounded modal stack, safe replacement, accept/cancel/escape rules (spec 21) |
| `ECS_Row.lua` | written — decorates the EXISTING row buttons: translucent surface, circular portrait, class badge/name, zone, optional note, level badge, faction emblem (spec 3/4/5/6/25/27) |
| `ECS_Roster.lua` | written — virtualised scrolling over the fixed row pool, selection, drag-reorder, deletion animation (spec 3/5/9/10/20/29/30) |
| `ECS_Tooltip.lua` | written — detail content with fallbacks, edge-clamped placement, hover-delay timer (spec 13/33) |
| `ECS_UI.lua` | written — search field, status, tooltip panel, modal overlay, notes editor, hover easing, stock realm-control suppression |
| `ECS_Integrate.lua` | written — wraps `UpdateCharacterList`, wires drag/notes/delete, drives ECS without editing its binding logic |
| `tools/make_ecs_portraits.py` | written — generates the ECS art from the shipped portraits |
| `textures/` | **65 BLPs (~8 MB)** + source PNGs: 56 portraits, seven supplied UI assets, note dot and search icon |
| `tests/frame_shim.lua` | written — WoW frame API emulation so row/roster/UI building is testable headless |
| `tests/` (13 files) | **1224 assertions, 0 failures** on real **Lua 5.1**, plus the contract-pin and wiring-audit checks |
| `docs/CHARACTER_SELECT.md` | written — the developer reference (all 12 required sections) |
| `tools/measure_capacity.py` | written — measures the persistable payload against the cvar budget |
| **Deployment** | **R47 DONE — 103 entries merged into both Dev MPQs, 103/103 round-trip verified, sampled pre-existing entries unchanged** |
| Remaining | **Verify R47 in the target Dev client** (pixels, Freeborn logo/hover art, restored row-plate scale, scrolling, drag), the measured-capacity outcome, optional notes addon mirror |

```
Lua runtime: Lua 5.1
modules    : ECS_Constants, ECS_Schema, ECS_Order, ECS_Data, ECS_Persistence,
             ECS_Notes, ECS_Anim, ECS_Search, ECS_Modal, ECS_Row, ECS_Roster,
             ECS_Tooltip, ECS_UI, ECS_Integrate
assertions : 1224 passed, 0 failed
```

Backup: `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-091455\` (both archives,
pre-R47 deploy).

### What remains, honestly

Everything the spec asks for is written, tested offline and deployed. What is **not**
established is that it looks and behaves correctly in the client, because that
cannot be verified from here: pixels and layout at the user's resolution, and the
deletion fade timing.

Two things that would have made the screen visibly broken were found and fixed while
hardening the unverifiable paths:

* **Drag never worked.** `UpdatePress` was only reachable from mouse-down, which
  fires once, so the drop target never moved and every release was a no-op reorder.
  A polling drag driver now runs while the button is held.
* **The hover slide was never applied.** `ECS_Row.SetOffsetX` stored the value but
  nothing anchored the row with it. The offset is now applied to the anchor, and only
  to the one row that changed rather than the whole pool.

Pointer Y is also no longer raw screen space: it is derived from the row parent's own
top edge, so it does not depend on where the roster sits at a given resolution.

### Texture assets

`tools/make_ecs_portraits.py` reads the **unmasked 130×130 source portraits** and
writes circular-masked copies into the ECS namespace, because 3.3.5a glue has no
reliable runtime texture masking and spec 4 asks for art rather than a rendering
hack. The shared CharacterCreate art is left untouched (spec 26), and the ECS copies
are drawn in preference to it because ECS controls the framing.

It replaced an earlier generator that read the client's `UI-CharacterCreate-*.blp`
plates instead. That was pointless and is recorded here so it is not reintroduced:
those plates are **already circular** (corner alpha 0 on all 62 of them), so masking
them again only softened an edge that had already been cut, and `GetPortrait` never
asked for the result anyway. Deriving from the sources also means ECS owns its art
and the generator no longer needs the client archives open.

What the new generator must get right:

* **The art key is the client's FILE name, not the model token or the source name.**
  `undead` → `Scourge`, `ZandalariTroll` → `Zandalari`, `panda` → `Pandaren`,
  `illidari` → `DemonHunterAlliance`/`DemonHunterHorde` by folder (the two factions
  are genuinely different art), `darkfallen_horde` → `DarkfallenHorde`. Guessing any
  of these renders no portrait, silently.
* **The sources have a black background, not transparency.** A centre-row scan for
  "non-black" is therefore not a reliable face measurement — dark armour and hair
  read as background — so the mask is a fixed 1px-inset inscribed circle rather than
  one derived from the art.
* **Male and female must be keyed separately.** Keying the mapping by art key alone
  collapsed every pair into a collision (28 warnings, 28 keys instead of 56).
* **It prunes what it did not produce**, so the directory and the mapping cannot
  disagree and dead textures cannot survive a regeneration.

### Integration: wrap, do not rewrite

`ECS_Integrate.lua` changes **nothing** in the deployed `CharacterSelect.lua`'s
binding logic. It wraps `UpdateCharacterList` exactly as the existing Freeborn code
already does — stock binding runs first (keeping every pinned string, the scroll
maths and the Freeborn badges intact), then ECS re-skins the rows and, when a
custom order or a filter is active, re-points them at the correct **real** indices.
With no order and no filter the two agree, so ECS is a pure visual layer.

The only edits to the existing file are three bug fixes the contract required
(below), each verified by a reproduced contract check in the test runner.

### Contract findings

`tools/test_character_select_contract.py` **cannot run in this checkout** (it reads
`ROOT / "3.3.5a - Dev"`, but the client lives on `G:`). Its assertions were
reproduced locally instead, which exposed that it has been **red for three
independent reasons**, not the one the audit noticed:

1. `CharacterSelect_OnKeyDown` tested `arg1` (nil) instead of `key` — DOWN/RIGHT
   navigation was dead. Now tests `key` and, when ECS is loaded, walks the
   **visual** order rather than server order.
2. `UpdateScrollChildRect()` was **absent entirely** — the scrollbar kept a stale
   range after the child grew.
3. `GlueScrollFrame_OnVerticalScroll(self, offset)` was **absent entirely** — the
   stock scroll helper was never being delegated to.

All three are now satisfied, and the test runner enforces the same pins on every
run so a future edit cannot silently break them.

### Bugs the tests caught (and fixed)

### Roster design: visual offset, real index

The row buttons are **siblings** of the scroll frame, not children of the scroll
child, so `SetVerticalScroll` moves nothing visually — it is a re-windowing virtual
list and always was. ECS keeps that shape (it is what "100 characters, 8 frames"
already means here) but changes **what the offset counts**:

* the existing code offsets by raw server index, which was only correct while
  visual order equalled server order;
* ECS offsets by **visual position** and resolves through `ECS_Order.visible[]`;
* `button:SetID()` still carries the **real** index, so every existing action —
  select, delete, enter world, and the Freeborn wrapper — keeps working unchanged.

Tests pin the case where the two genuinely diverge (custom order **and** a filter
active at once), because that is the one a translation mistake would expose.

All geometry is pure (`ComputeLayout` / `SlotForY` / `ClampOffset`), so resolution
independence is verified at several viewport heights rather than assumed, and a
zero row height cannot divide by zero.

### Bugs the tests caught (and fixed)

### Row design: decorate, do not recreate

`CharacterSelect.xml` already defines the ten row buttons and the live Freeborn
wrapper reaches into them **by name**. So `ECS_Row` does not build new rows — it
decorates the existing ones and thereafter only rebinds data. That satisfies the
pooling requirement (spec 25) for free and keeps both existing contracts intact:
the button keeps its name, a child texture named `…FactionIcon` still exists, and
`button:GetID()` still returns the **real** index. Tests pin all three.

The emblem slot is deliberately placed at `TOPLEFT + (200, -35)` at 44×44 — the
exact anchor `CharacterFreeborn_ApplyBadges` uses — so the existing Freeborn
wrapper and ECS agree on placement instead of fighting over it.

### Bugs the tests caught (and fixed)

### Bugs the tests caught (and fixed)

1. **Saved order silently discarded on the login screen.** `ComputeOrder` pruned saved
   keys against the *current* roster, so calling `SetCustomOrder` before the server
   answered pruned every key against an empty list and threw the whole order away. Now it
   only prunes when a roster actually exists. Regression test `8g`-`8i`.
2. **Pipe truncation in the store wrapper.** `UnwrapValue` split on `|` with a non-greedy
   match, but the shard payload itself contains `|`. Every store was silently truncated to
   `v=1`, the account field was emptied, and the account scope check was therefore
   skipped — **another account's order and notes would have been applied**. Fixed with a
   length-prefixed wrapper; regression test `4e`/`4f`.
3. **Backend not threaded through `Save`/`Load`.** They always used the real
   `GetCVar`/`SetCVar` regardless of injection, so every persistence test passed against a
   dead backend.
4. **`ProbeCandidates` used a table as the cvar name.** Slot tables were passed straight to
   `GetCVar`, which would fail against the real client.

Several further failures were **test** bugs, not module bugs (missing `A.Reset()` between
sections; assertions that ignored the default `quadOut` easing and the `ANIM_MAX_DT` delta
clamp; a substring expectation that contradicted the actual match). Each time I verified
the module's behaviour on a clean slate before touching it, and corrected the test rather
than bending the module to match.

Two hard integration constraints must hold for every later phase (details in
`character-select-redesign.AUDIT-IDS.md`):

1. `tools/test_character_select_contract.py` pins exact strings inside
   `CharacterSelect.lua`, including that `arg1` must be **absent** from the keydown
   handler. That test is currently **red** and cannot run in this checkout (it reads a
   client path that does not exist here).
2. `CharacterFreeborn_ApplyBadges` wraps `UpdateCharacterList` and needs row buttons named
   `CharSelectCharacterButtonN` with a `…FactionIcon` child, and `button:GetID()` still
   returning the **real** character index.

## Guiding constraint

The audit found that **100-character support with an 8-row reusable pool and actual-index
scrolling is already implemented and deployed**, and that the screen is a heavily
customised retail-interface fork carrying custom races and Freeborn. Therefore:

> **Extend the existing indirection; never replace the existing frame pool or the
> `SetID(realIndex)` contract.**

Today the mapping is `viewportRow → scrollOffset + row` — valid only while visual order
equals server order. Every new feature (search, custom order) breaks that assumption. The
single most important structural change is to turn the additive offset into an explicit
order array, after which every remaining feature is additive.

## Module layout (§36)

Glue has no module system, but `GlueXML.toc` has a documented extension point. New files
are registered there and communicate through a single global namespace, `ECS`
(Esteria Character Select). Physical files:

```
Interface\GlueXML\
    ECS_Constants.lua      # §35  every tunable, one place
    ECS_Data.lua           # §23  normalized CharacterData + server list ingestion
    ECS_Schema.lua         # §14/§15/§27  Race / Class / FactionStyle tables + fallbacks
    ECS_Order.lua          # §24  visualOrder[] <-> realIndex mapping (the core)
    ECS_Persistence.lua    # §11/§34  cvar shard store, versioning, migration
    ECS_Notes.lua          # §12  per-character notes
    ECS_Anim.lua           # §7   one controller, pooled tweens
    ECS_Modal.lua          # §21  modal/notification framework
    ECS_Row.lua            # §3/§4/§5/§6  row visual construction + pooling
    ECS_Roster.lua         # §3/§9/§10  viewport, scroll, drag-reorder
    ECS_Search.lua         # §8   local filtering
    ECS_Tooltip.lua        # §13  hover/detail panel
    CharacterSelect.lua    # existing — minimally edited to delegate
```

Load order matters and is enforced by the TOC:

1. `ECS_Constants`, `ECS_Schema`, `ECS_Data`, `ECS_Order`, `ECS_Persistence`,
   `ECS_Notes`, `ECS_Anim`, `ECS_Modal` — **pure Lua, no frame access**
2. `ECS_Row`, `ECS_Roster`, `ECS_Search`, `ECS_Tooltip` — define functions only
3. `CharacterSelect.xml` → `CharacterSelect.lua` — existing wiring, calls into `ECS`
4. All frame mutation happens inside `OnLoad`/`OnShow`, never at file scope
   (the crash documented at `CharacterCreate.lua:1846`)

## Visual index mapping (§24) — the critical invariant

```
visualOrder          : array of realIndex, length = number of VISIBLE rows
realToVisible        : realIndex -> position in visualOrder, or nil if filtered out
rowPool[i].character : CharacterData for the row at viewport slot i
```

- `visualOrder` is produced by `ECS_Order`: start from server order, apply saved custom
  order, then apply the active search filter. It is **derived state**, rebuilt only on
  invalidation — never per frame.
- The existing pool keeps `button:SetID(realIndex)` from `visualOrder[scrollOffset + i]`,
  so `GetID()` continues to mean exactly what the stock code expects. **No existing
  action needs to change its index handling.**
- Every operation resolves through `CharacterData`, never through a visual position:
  select, delete, enter world, notes, drag, tooltip.
- **Filtered-but-selected rule (§8):** keep the real selection, render no selected row
  while it is filtered out. This is the option that cannot cause accidental entry —
  choosing "select first visible" could silently move the selection onto a different
  character.

## CharacterData (§23)

```lua
CharacterData = {
    realIndex,   -- server index, authoritative
    stableKey,   -- realm .. ":" .. lower(name)   (§11; GUID NOT CONFIRMED exposed to glue)
    name, level, raceID, raceName, classID, className, sex,
    zone, factionID, portrait, note, customOrder,
}
```

Fields actually populated are set in `ECS_Data` from whatever `GetCharacterList()`
returns in this client (enumerated in the audit's ID companion). Unknown/missing values
become `nil` and every consumer must tolerate nil (§33).

## Persistence (§11, §34)

**Mechanism:** cvar shard store — the only restart-surviving channel glue has (audit §6).

```
format:  <marker><version>|<account>|<realm>|<payload>|<original>
marker:  "ecs1:"
        e.g.  ecs1:1|ACCOUNT|Esteria|o=3,1,2,0;n=a1b2:Main%20tank|1
```

- `version` first (§34); unknown/newer version → ignore the store and fall back to
  **server order** rather than blocking login.
- Order payload is a compact index permutation; notes are only appended for characters
  that actually have one, keyed by a short hash of `stableKey`.
- **Realm-aware and account-aware** so keys cannot leak between realms (§11).
- Discovered by **probing the cvar pool at runtime**: write a marked probe, read it back,
  keep the cvars that stick. Shard the payload across all that succeed. Never call
  `GetCVar`/`SetCVar` outside `pcall` (documented client-crash risk).
- Always preserve the cvar's pre-existing value in the trailing `|original` field, as the
  existing badge implementation does.
- **Tolerance (§11):** stale entries for deleted/renamed characters are dropped on load;
  unknown characters are appended (configurable head/tail). A corrupt store must never
  fail the roster — worst case is server order.

*Known limitation:* cvar values are length-bounded and the bound is not discoverable
offline. This is why the store is sharded and why the design degrades to order-only
(notes dropped) rather than failing. **The degradation is write-side** — a *read* can
never fail because of the notes (`P.Deserialise` simply yields no notes from a bad
`n=` field), so a "strip the notes and re-read" recovery is unimplementable and was
removed rather than kept as plausible-looking dead code. The measured limit and what
it costs are in `docs/CHARACTER_SELECT.md` limitation 4: a full 100-character order
still needs 8 shards against 6 cvars, so large-roster ordering is not yet durable.
An optional in-world addon mirror (`FreebornClaim` pattern) removes the bound entirely
and is planned as a follow-up, not a dependency.

## Faction / race / class abstraction (§14, §15, §27)

Data-driven tables with a guaranteed neutral fallback — **no `if alliance else horde`
anywhere**:

```lua
ECS.FactionStyle[teamID] = { name, emblem, accent, border, text }   -- fallback = neutral
ECS.Race[raceID]         = { name, icon, faction, portraitable }    -- fallback = "Unknown"
ECS.Class[classID]       = { name, color, icon }                    -- fallback = classless
```

Colour is an **accent only** (§27): faction tints the border, class tints a secondary
detail. The row surface stays neutral translucent black so no row turns solid red/blue.

Custom races must render and stay selectable with fallback art (§15) — the roster must
degrade, never error.

## Frame pooling & virtualization (§9, §25)

Reuse the existing 8 rows, generalised to `POOL_SIZE = ceil(viewport / ROW_HEIGHT) + 2`.
A recycled row must be **fully reset** before reuse: text, portrait, faction texture,
note indicator, selected state, hover state, drag state, callbacks, and any in-flight
tween. A dedicated `ECS.Row:Reset(row)` is the only place that clears state, so a
character's data can never flash on another character's row.

## Animation framework (§7)

One shared controller, not N `OnUpdate` handlers:

- a single `OnUpdate` on a hidden driver frame steps all active tweens,
- tweens are pooled; finished tweens are recycled,
- the driver **stops itself** when no tweens are active (idle cost = zero),
- easings: `linear`, `quadIn/Out/InOut`, `cubicOut`, `backOut` for selection pop.

Drives fades, slide-ins, hover interpolation, selection transitions, drag offset,
deletion shrink/collapse and modal fade (§7's full list).

## Phased delivery (§40)

Audit-driven status — several phases are **already satisfied** by existing code:

| # | Phase | Status |
|---|---|---|
| 1 | Audit existing implementation | **done** (this doc + audit) |
| 2 | Normalized character-data layer | to build |
| 3 | Real/visual index mapping | **generalize existing** `scrollOffset` |
| 4 | Replace visual roster | to build (rows restyled over existing pool) |
| 5 | Large-roster scrolling | **exists** (100-char, wheel, scrollbar) |
| 6 | Selection synchronisation | extend existing |
| 7 | Search / filtering | to build |
| 8 | Persistent custom ordering | to build (`ECS_Persistence`) |
| 9 | Drag-and-drop reorder | to build |
| 10 | Character notes | to build |
| 11 | Custom tooltips / details | to build |
| 12 | Freeborn / custom faction styling | to build (needs audit IDs) |
| 13 | Custom-race-safe metadata | to build |
| 14 | Deletion animation | to build |
| 15 | Modal framework | to build |
| 16 | Final polish | to build |
| 17 | Performance audit | to build |
| 18 | Regression testing | to build |

Each phase ships independently and is verifiable, per the spec's "do not attempt to
rewrite the entire screen in one uncontrolled pass".

## Testing (§41)

Offline-verifiable before any client run:

- **Index-mapping unit tests** in plain Lua/Python: given a server order, a saved order
  and a filter, assert `visualOrder` and that every `visualOrder[i]` resolves to the
  intended `CharacterData`. This is the "must enter the character that is visually
  selected" invariant, tested without a client.
- **Persistence round-trip tests**: encode → shard → reassemble → assert equality;
  plus corrupt/truncated/foreign-version stores must degrade to server order.
- **Fallback tests**: unknown race/faction/class IDs must produce a renderable row.

In-client matrix (0 / 1 / 10 / 100 characters; Alliance / Horde / Freeborn / custom race;
search active and empty; reordered then restarted; saved notes; resolutions 1280×720 →
2560×1440) is manual, and will be reported as run or not-run — not assumed.

## Open questions carried forward

1. Exact `GetCharacterList()` field set in this fork (audit companion).
2. Whether a character GUID is exposed to glue — decides `stableKey` quality (§11).
3. Practical cvar value length bound — decides notes capacity vs addon mirror.
4. Custom race/class/faction ID tables (audit companion).
