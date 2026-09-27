# Esteria Character Select (ECS)

Developer reference for the customised 3.3.5a character-selection screen.

Written so nobody has to reverse-engineer this again. Companion planning material,
the full audit and the verification logs live in
`.agents/plans/character-select-redesign/` (gitignored).

---

## 1. What this is

A custom character-management interface layered over the stock 3.3.5a glue screen:
a virtualised roster with circular race portraits and artwork-backed row states,
search filtering, drag-and-drop reordering, persistent client-side ordering,
per-character notes, and a detail tooltip — while keeping every existing action
(select, enter world, create, delete, AddOns, Options, Back) working unchanged.

## 2. Architecture

Fifteen Lua modules under `Interface\GlueXML\`, loaded by `GlueXML.toc`:

| Module | Responsibility |
|---|---|
| `ECS_Constants.lua` | every tunable and texture path (spec §35) |
| `ECS_Schema.lua` | race / class / faction presentation + fallbacks |
| `ECS_Order.lua` | the visual↔real index mapping and filtering |
| `ECS_Data.lua` | normalises the client's positional character tuple |
| `ECS_Persistence.lua` | sharded cvar store (the only restart-surviving channel) |
| `ECS_Notes.lua` | note text hygiene + editor draft/commit/cancel |
| `ECS_Anim.lua` | one pooled, self-disabling tween controller |
| `ECS_Search.lua` | query semantics, summary states, match highlighting |
| `ECS_Modal.lua` | bounded modal stack |
| `ECS_Row.lua` | decorates existing row buttons with circular portraits, class badges/names, zones, optional notes, and faction emblems |
| `ECS_Roster.lua` | eight-row viewport, explicit wheel/scrollbar routing, selection, drag, delete fade |
| `ECS_Tooltip.lua` | detail content + edge-clamped placement |
| `ECS_UI.lua` | search field, status line, tooltip panel, modal overlay, notes editor, stock realm-control suppression |
| `ECS_Integrate.lua` | wraps the stock `UpdateCharacterList` to drive all of the above |
| `CharacterSelect.lua` | the stock/customised file — **three bug fixes only** |

**Load order matters.** Core modules load early (pure Lua, no frame access).
`ECS_Integrate.lua` loads **after** `CharacterCreate.xml`, because it wraps
`UpdateCharacterList` and so does the Freeborn code in that file — running last
means ECS wraps the already-wrapped function, so the stock binding and the Freeborn
badges both run before ECS re-skins the rows.

## 3. Why it wraps instead of rewriting

`CharacterSelect.lua` is a heavily customised retail-interface fork carrying the
Esteria race work, and two live contracts depend on it:

* `tools/test_character_select_contract.py` pins exact strings inside it;
* `CharacterCreate.lua`'s `CharacterFreeborn_ApplyBadges` re-wraps
  `UpdateCharacterList` and reaches into the row buttons **by name**, expecting a
  child texture `…FactionIcon` and `button:GetID()` to return the **real** index.

So ECS changes nothing in that file's **binding logic**. The stock function runs in
full, then ECS re-skins. With no custom order and no filter the two agree, and ECS
is a pure visual layer.

The one exception is `CharacterSelect_OnKeyDown`, where the arrow keys have to be
*delegated* rather than wrapped: see §3.1.

### 3.1 Interaction ownership — read this before hooking anything

A hook ADDS a handler; it does not replace one. Hooking something the stock glue
already handles runs both, and for anything that *moves state* that is a bug, not a
double safety net. Two real defects came from exactly this, and both were found by
reading `CharacterSelect.xml` rather than by any test:

* **The wheel.** The scroll frame already binds `OnMouseWheel` to
  `CharacterSelect_ScrollBy(delta)`, and that path is not a dead end: ScrollBy →
  `CharacterSelect_SetScrollOffset` → `CharacterSelect_RefreshVisibleList` →
  `UpdateCharacterList` → the ECS wrapper. ECS hooked the wheel as well and moved
  its own offset, so one notch scrolled twice — and worse, it moved by
  `SCROLL_SPEED = 0.45` of a row and assigned `select.scrollOffset` **directly**,
  bypassing `CharacterSelect_ClampScrollOffset` (which rounds). A fractional offset
  then broke two things, because the offset doubles as a **visual position**:
  `O.RealIndexAt(5.55)` is `O.visible[5.55]` = `nil`, so *every* pooled row hid and
  one notch blanked the roster; and the stock `UpdateCharacterSelection` builds
  `"CharSelectCharacterButton"..(selectedIndex - scrollOffset)`, so a fractional
  offset yields a nil lookup and errors inside the glue screen. **ECS no longer
  touches the wheel**, and `R.ClampOffset` floors so the "offset is a whole row"
  invariant holds for any caller.
* **The arrow keys.** These must delegate, because the stock handler walks
  `selectedIndex ± 1` in **server index** space, which stops matching what the user
  can see the moment a custom order or a filter is active. Only DOWN/RIGHT used to
  delegate, so DOWN moved to the next *visible* row while UP jumped to an unrelated
  server index. Both directions now call `ECS.Integrate.StepSelection(±1)`, each
  with the stock branch kept as the no-ECS fallback.
* **The scroll re-entrancy guard.** `R.SyncScrollbar` applies ECS's offset with
  `frame:SetVerticalScroll(...)`, which fires `OnVerticalScroll` **synchronously**.
  `CharacterSelect_OnVerticalScroll` only returns early when
  `CharacterSelect.scrollUpdating` is set — the flag stock's own
  `CharacterSelect_ApplyScrollOffset` uses around its identical call. ECS set only
  its own `R.applyingScroll` flag, which **nothing read**, so the guard guarded
  nothing and ECS's own scroll re-entered the stock path:
  `CharacterSelect_SetScrollOffset` → `CharacterSelect_RefreshVisibleList` →
  `UpdateCharacterList`, which rebinds the rows from **server order** — and ECS's
  `I.applying` guard then suppressed the re-skin that would have repaired them. It
  bites whenever the clamped value differs from the stock `scrollOffset`, which is
  exactly what a search filter does when it shrinks the visible count while the
  roster is scrolled down. ECS now sets and **restores** `scrollUpdating` around the
  call. Skipping the glue helper there is safe: it only sets the scrollbar widget's
  value and toggles its arrow buttons, and `SetVerticalScroll` already updates the
  scrollbar — stock skips it in the same way.
* **The stock row plate and its text.** `UpdateCharacterList` writes a complete row
  presentation onto every **populated** row, and ECS replaces all of it:
  * `GeneralBackground` — 243×62 cut from `uicharacterselectglues2x`, **shown** at
    BACKGROUND **sublevel 1**, above the backdrop and above ECS's tint at sublevel 0,
    so it drew stock art over the ElvUI surface with the selected row's accent fill
    underneath it.
  * `Background` — shown at OVERLAY sublevel 2 (above ECS's portrait and text), but the
    stock code never gives it a texture, so it draws nothing; hidden anyway so ECS does
    not depend on that staying true.
  * **six FontStrings** — `Name` at (0,−8) and `Level`/`Separator`/`Class` at
    (0…30,−25), all at OVERLAY and anchored to the row's TOPLEFT. OVERLAY is above
    ECS's ARTWORK portrait and level with ECS's own text, so every row drew the stock
    name/level/class **across ECS's portrait** and beside ECS's own name/zone. This was
    the largest miss: it affected every row, always, and the shim has no stock regions
    so nothing offline could see it.
  All of it must be suppressed on **every refresh**, not once in `Build`: the stock
  pass re-writes and re-shows these each time it binds a row while `Build` runs once
  per button. Two regions are deliberately **not** suppressed — `FactionIcon`, which
  ECS adopts (re-anchored and resized) so it keeps the name the Freeborn wrapper looks
  up; and the `Customize`/`RaceChange`/`FactionChange` buttons, which are a paid
  feature anchored `TOPRIGHT` to the row's `TOPLEFT` at (−15, 6) — outside the row, so
  they neither collide nor need moving.
Related: the row buttons remain children of **`CharacterSelectCharacterFrame`** so the
stock visibility and action contracts remain intact, but ECS explicitly anchors them
to the screen-relative roster column below the raised search field. They are not
children of the 1px-wide scroll child, so nothing inside the ScrollFrame moves
visually. Stock scrolls by rebinding which character each fixed row shows, and ECS
does the same — which is why `R.offset` selects *content* per slot and never displaces a row.

Row buttons are safe to hook: `CharSelectCharacterButtonTemplate` binds only
`OnLoad`, `OnClick`, `OnDoubleClick` and `OnMouseWheel`, and ECS hooks
`OnMouseDown`/`OnMouseUp`/`OnEnter`/`OnLeave`, which stock does not use.

Every `SetScript`/`HookScript` ECS installs was audited against the XML, not
spot-checked. The only stock-owned frame ECS hooks at all is the row button, and
only on scripts the template leaves unbound. Everything else is an ECS-owned frame
(`ECSAnimDriver`, `ECSUIDriver`, `ECSDragDriver`, the search box, the modal and the
notes editor). ECS also zeroes the row's stock HighlightTexture, deliberately:
`LockHighlight` then becomes invisible and ECS draws the selection itself, so
`UpdateCharacterSelection` highlighting the wrong row under a custom order or a
filter costs nothing visually.

### 3.2 Chrome is parented to the screen, never to UIParent

`GlueParent.xml` declares `<Frame name="GlueParent" setAllPoints="true">` with **no
parent attribute**, so GlueParent is a child of UIParent, and the glue screens are
children of GlueParent. `SetGlueScreen()` (`GlueParent.lua:215`) switches screens by
calling `frame:Hide()` on every frame in `GlueScreenInfo`, then `Show()` on the one
asked for — and `GlueScreenInfo["charselect"] = "CharacterSelect"`.

So **anything parented to UIParent is a sibling of GlueParent and is never hidden.**
Chrome built that way stayed drawn after Back, over the realm list, character
creation, the options panel, the credits and the intro movie — with a live search
`EditBox` still calling `ECS.Integrate.Refresh()` when typed into.

`ECS.UI.PreferredParent()` returns `CharacterSelectUI` → `CharacterSelect` →
`UIParent`, and that is what `ECS.UI.Build` uses. `CharacterSelect` is a `ModelFFX`
whose UI child `CharacterSelectUI` holds the screen's widgets; both are
`setAllPoints`, so anchoring to either covers exactly what UIParent did and the
layout is unchanged, but the chrome now inherits the screen's show/hide.

The one deliberate exception is `ECSAnimDriver`, which is left parentless: a hidden
parent stops `OnUpdate`, so a tween interrupted by a screen switch would never
advance, leaving the driver shown and the deletion path's `onDone` (which restores
the roster) unfired. It is invisible and takes no mouse input, so it cannot leak the
way the search box did.

## 4. Character index mapping — the critical invariant

Blizzard's character list is authoritative and indexed `1..numChars`. **That** index
is what `SelectCharacter` / `DeleteCharacter` / `EnterWorld` take. The roster shows a
filtered, reordered view, so the two stop agreeing as soon as search or a custom
order exists.

```
ECS.Order.visible[i]       = real index of the i-th VISIBLE row
ECS.Order.realToVisual[r]  = i, or nil when r is filtered out
```

Rules that must not be broken:

* the roster offsets by **visual position**, never by server index;
* `button:SetID()` always carries the **real** index, which is what keeps every
  existing action working;
* every operation resolves through `CharacterData`, never through a visual position;
* when the selected character is filtered out the **real selection is kept** and no
  selected row is drawn. This is the option that cannot cause accidental entry.

Tests cover the case where the two genuinely diverge (custom order **and** a filter
active at once).

## 5. Persistence format

Glue has no `SavedVariables` — it runs before addons and cannot write files. The only
restart-surviving channel is a **string cvar the client never parses**, established
by the existing Freeborn badge code. Hard-won rules encoded in `ECS_Persistence`:

1. `GetCVar`/`SetCVar` **raise** on a name the client does not know — every access is
   `pcall`-wrapped, because an uncaught glue error here can crash the client.
2. Only names registered at the login screen are writable, so candidates are
   **probed** (write a marked value, read it back, keep what sticks).
3. Integer cvars are normalised on load, so the store must be a string.
4. Read-back verification is mandatory; a write may be silently refused.

```
cvar value:  ecs1:<shardLength>|<shard><original value>
payload   :  v=<version>|a=<account>|r=<realm>|o=<order>|n=<notes>
```

* **Order and note keys are stored without their realm prefix.** The key is
  `lower(realm)..":"..lower(name)`, so every entry in a roster repeated the same
  realm — and `P.Encode` escapes `:` to `%3A`, costing 20 chars per character. The
  record's `r=` field carries the realm once; the read path re-attaches it. This is
  not cosmetic: at 20 chars per key a 100-character order needed 14 shards against a
  6-cvar budget, so it could never be saved. `SCHEMA_VERSION` is **2**; a v1 record is
  ignored (spec 34) and the next save writes v2.
* The **length prefix** is essential: the shard payload itself contains `|`, so a
  delimiter-based split silently truncates the store (that bug emptied the account
  field and defeated account scoping).
* The payload is **sharded** across every cvar that passes probing; capacity is
  measured per cvar, not assumed (see limitation 4). `P.ProbeCapacity` binary-searches
  the longest value each cvar returns intact and restores what it found, exactly as
  `ProbeCandidates` does, so measuring can never damage a stored record.
* Scope is **account → realm**. A blank field matches anything, for tolerance.
* Degradation is **write-side**, because capacity is the failure that actually
  happens: `P.SaveDegraded` retries with the notes dropped, so a reorder still
  persists when the notes no longer fit. It reports whether notes were sacrificed,
  and the caller clears them in memory too, so the UI never shows notes that are
  guaranteed to vanish.
* Corrupt, foreign-version or truncated stores are **ignored**, and the caller falls
  back to server order. A bad store must never block entry.
* Keys are `lower(realm)..":"..lower(name)` — no GUID is exposed to glue, and both
  parts are case-insensitive. **A rename therefore looks like a delete plus a
  create**: the character is adopted at the tail and its note does not follow.

## 6. Adding a custom race

1. Register it server-side as usual (see `modules/mod-custom-server`) and ship the
   client `ChrRaces.dbc` row.
2. Drop the 64×64 portrait plate in as
   `Interface\Glues\CharacterCreate\UI-CharacterCreate-<ArtKey><Male|Female>.blp`
   (follow `tools/derive_playable_race_portraits.py`).
3. Add the model token to `ECS.Schema.RaceByModelKey` with its `artKey`.
4. Run `python .agents/plans/character-select-redesign/tools/check_artkeys.py`. It
   cross-checks every art key against the create screen's own `RACE_ICON_TEXTURES`
   mapping and against the plates actually inside the client archives.
5. If you want an explicit display name or faction, add one entry to
   `ECS.Schema.RaceOverride[realRaceID]`.

> **The art key is the portrait FILE name, and it is not always the model token.**
> Zandalari trolls ship `UI-CharacterCreate-Zandalari<sex>.blp` while the create
> screen's token is `ZANDALARITROLL`, and ECS's `artKey` said `ZandalariTroll` — so
> the row asked for a file that does not exist and rendered **no portrait at all**,
> silently, with nothing raising. `check_artkeys.py` found it and now reports it:
> as of the last run the only art keys with no plate are `Forsaken` and `Sethrak`,
> which have no portrait art in the client *or* on the create screen either.

**The `ECS-Portrait-*` namespace is ECS's own portrait set**, generated from the
unmasked 130×130 source art by `tools/make_ecs_portraits.py` and drawn in preference
to the create screen's plates:

* `S.PortraitArtKeys` lists the art keys ECS has a copy of; `S.GetPortrait` returns
  `C.TEX.portraitNs .. artKey .. sex` for those and falls back to
  `C.TEX.create .. "UI-CharacterCreate-" .. artKey .. sex` for anything else, so a
  newly added race or a partial install still renders a face.
* It matters because **framing** is the visible property, not resolution. The roster
  draws at 46px, so the client's 64px plates are already oversampled — but those
  plates inscribe a circle only 0.864 of their frame (measured: 0.586 opaque area,
  identical across all 62 of them), which leaves a gap between the face and the 50px
  ring drawn over it. The ECS copies mask with a 1px inset (0.666 opaque) so the face
  meets the ring.
* The mask is built at 4× and resampled with LANCZOS, because a 64px circle drawn
  directly has a visibly stepped rim.
* The sources have a solid **black** background rather than transparency, so the mask
  supplies the whole silhouette — there is no alpha in the source to reuse.
* The generator **prunes** anything it did not produce. The previous generator
  derived from the client plates and emitted art keys that no longer exist (the base
  `DemonHunter` pair, whose client plates are blank at 0.024 opaque); leaving those
  behind shipped dead textures and let the directory disagree with the sources.
* `tools/check_artkeys.py` verifies `PortraitArtKeys` against the generated files in
  both directions: a key listed but not generated renders no portrait, and a file
  generated but not listed is dead weight in the MPQ.
* The supplied `PortraitBorder.png`, `LevelBorder32.png` and five large row plates
  are converted to BLP2 by the same generator. The plates are padded or resampled to
  power-of-two dimensions for the 3.3.5a client. Grey is the idle state; hover
  crossfades to Alliance-blue, Horde-red or Freeborn-purple, while gold selection
  takes priority over hover.
* The generator emits the search magnifier as a 32×32 power-of-two BLP, drawn at its
  smaller UI size. `deploy.py` restores stock Glue/UI panel-button textures from
  `locale-enUS.MPQ` and the Delete-button atlas from `patch-A.MPQ`, then generates a
  WotLK-blue variant for the compact icon-only Delete control. These override the
  custom flat BLPs in the higher-priority target patches.
* The generator draws the note dot (ElvUI accent) and search magnifier at 4× and
  resamples them, because anything drawn at its final size comes out stepped.
  `SEARCH_TEXT_INSET` must clear the icon or the placeholder and any typed text run
  underneath it; `test_ui` asserts that geometry.
* **`Forsaken` and `Sethrak` have no portrait art anywhere** — not in the client, not
  on the create screen, not in the source set — so both fall back and render no
  portrait rather than a wrong one.

**Unregistered races still work**: `ECS.Schema.GetRace` falls back to a neutral
record, the row renders with `Unknown Race`, and there is no portrait rather than a
wrong one.

> **Hazard to respect:** `CharacterInfo.lua`'s `RACE_DATA` / `ALLIANCE_RACES` /
> `HORDE_RACES` are a parallel **1..19 ORDINAL** table, not `ChrRaces` IDs, and
> `CharacterCreate.lua` passes an enumeration ordinal into `GetFactionForRace` by
> design. Do not "correct" those. ECS therefore resolves race from the background
> **model file string**, which is the same signal the existing custom faction
> override already trusts.

## 7. Adding a faction / TeamID

Add one entry to `ECS.Schema.FactionStyle[teamID]`:

```lua
[4] = { name = "Whatever", emblem = "Interface\\...", accent = { r, g, b } },
```

That is the whole change. There is deliberately no `if alliance else horde`
anywhere — factions are table lookups with a neutral fallback, so an unknown ID
renders as neutral rather than breaking the UI. Colour is an **accent only**: it
tints the row rim and the emblem, never the fill.

**Freeborn is special and already handled.** It is a persistent *team* (TeamID 3),
not a race, and the glue character list carries no team field. ECS reuses the
client's existing name-hash record (`CharacterFreeborn_BadgeHashes` /
`CharacterFreeborn_RecordFor`) rather than duplicating that store, and renders the
same badge at the same anchor slot (`TOPLEFT + (200, -35)`, 44×44) that
`CharacterFreeborn_ApplyBadges` uses — so the two agree instead of fighting.
ECS stores its persistence shards in those same cvars and preserves their prior
contents behind `ecsN:<length>|<shard>` wrappers. `ECS.Schema.FreebornHashes` unwraps
those layers before parsing `fb:` records so Freeborn identity survives ECS saves.

## 8. Changing the styling

Everything visual is in `ECS_Constants.lua`:

* `COLOUR` — text, faction accents, dragTarget and danger
* `TEX` — every texture path, including portrait/level borders, grey idle plate,
  faction-specific hover plates, gold selected plate and blue Glue button art
* Layout — `ROW_HEIGHT`, `ROSTER_WIDTH`, `ROSTER_RIGHT`, `ROSTER_TOP`, `SEARCH_TOP`,
  `POOL_SIZE` (8 visible rows), portrait/level border sizes, class-icon and emblem
  geometry, native Glue-button sizing, blue action buttons, icon-only Delete, realm-list
  suppression, bottom-right spacing, and `ROW_ART_SCALE` for the Large row backdrops
* Motion — `FADE_DURATION`, `HOVER_DURATION`, `SELECTION_DURATION`,
  `DELETE_DURATION`, `SLIDE_DURATION`, `DRAG_THRESHOLD`, `TOOLTIP_DELAY`
* Capacity — `POOL_SIZE`, `VIEWPORT_HEIGHT`

Character-select panels use the same tiled Glue tooltip textures as CharacterCreate.
Standard Glue action buttons use the blue WotLK art with native gold-shadow fonts. The
realm name, realm-list control and Warband toggle are hidden; search begins at the top
of the screen and the roster is raised to follow it. Delete uses the icon-only blue
atlas and shares Create Character's vertical centerline. Idle, hover and selected row
plates zoom by 10% inside their row geometry. Roster rows have no flat frame fill or
rim: supplied artwork provides the row surface, with selection taking priority over
hover.

## 9. Client binary / DLL changes

**None were required for ECS.** All of it is GlueXML, Lua and BLP assets.

Pre-existing client changes this work relies on but did not make:

* `Wow.exe` byte at `0x6404C` (`80 7D FF 64`) — the 100-character client limit,
  already patched by the `100-character-support` work.
* `Extensions\races-64-esteria\races-64-esteria.dll` — expands the runtime race table.
* `WarcraftXL.dll` + `wxl-symbols.json` — engine-level modding surface. Anything
  needing camera or model work beyond GlueXML belongs there, not here.

## 10. Testing

```
python .agents/plans/character-select-redesign/tests/run_tests.py
```

Runs the **actual module sources** on a genuine **Lua 5.1** runtime (`lupa.lua51`,
matching the client's interpreter family) against a WoW frame API emulation. No
client needed.

**1224 assertions, 0 failures.** It also compiles `CharacterSelect.lua` (which cannot
be *executed* headlessly) and re-enforces the `tools/` contract pins locally,
because that test cannot run in this checkout — it reads `ROOT/"3.3.5a - Dev"` while
the client lives on `G:`.

The runner also carries a **wiring audit**, which exists because of a real miss: the
drag path shipped with `UpdatePress` defined and unit-tested but reachable only from
mouse-DOWN. It reports, and the invariant it now *enforces*, is that every public
function is reached by production code, used in-file under its local name, or
exercised by a test — anything else fails the run. A function referenced only by
tests is printed as a warning, because that is where a wiring gap hides.

Covered offline: order/filter/reorder/prune, a 100-character roster with an 8-row
visible window and explicit wheel/scrollbar range, raised search/roster geometry, hidden
realm/Warband controls across refreshes, Delete/Create vertical alignment, 10% row-art
zoom, Freeborn hash recovery through nested ECS cvar wrappers, the Freeborn emblem and
purple hover art, persistent
stock-region suppression, Illidari display-name/race-ID/raceFilename faction-art mapping,
War Band refresh/count fallback,
default button textures, transparent list backdrop, tooltip strata/leave behavior, Hero
fallback, class badges and class-coloured names with zone/optional notes, both possible
`GetCharacterInfo` field
layouts, the full cvar store round-trip including scoping and corruption, the
measured-capacity probe and capacity-aware sharding, note hygiene
and Cancel semantics, tween replacement/cancel/pooling, row recycling with no
bleed-through, tooltip edge clamping as a property over a grid of cursor positions,
modal stack rules, the whole-row offset invariant, the persistence notice, and a
simulated client restart.

**Not verified offline** (needs the client): pixels, cursor-to-row drag coordinates,
the deletion fade timing, and wheel feel. Note that the wheel bugs in §3.1 were
found by reading the XML, not by a test — the offline suite cannot exercise the glue
key/wheel dispatch, so anything ECS *hooks* must be checked against
`CharacterSelect.xml` by hand.

## 11. Deploying

```
python .agents/plans/character-select-redesign/tools/deploy.py --dry-run
python .agents/plans/character-select-redesign/tools/deploy.py
```

Close the client first — it holds the archives open. The script backs up both
`patch-Z.MPQ` and `patch-enUS-Z.MPQ` to `G:\3.3.5a - Dev\Backups\character-select-ecs-<timestamp>\`,
merges the payload into **both** (the contract test reads both), then verifies every
new entry round-trips and sampled pre-existing entries are unchanged.

## 12. Known limitations

1. **Deletion animation is best-effort.** The stock confirmation is deliberately kept
   (it gates deletion behind a typed confirm string and a protected-name list;
   replacing it would weaken a safety feature for a cosmetic gain). ECS fades the row
   whose character disappeared and defers the refresh, with a guard tween so a lost
   callback cannot leave a stale roster. Timing is unverified in-client and, if it
   looks wrong, degrades to no animation rather than a stuck list.
2. **Drag behaviour unverified in-client.** Two things were found and fixed while
   hardening it, but neither could be confirmed on screen:
   * the drag only ever ran on mouse-DOWN, so the drop target never moved and a
     release was always a no-op reorder. A drag driver now polls while the button
     is held (and hides itself the moment the drag ends, so idle cost is zero);
   * the pointer Y was raw screen space. It is now derived from the **row parent's
     own top edge** (`GetTop()`), so it does not depend on where the roster sits at
     a given resolution. If that geometry is unavailable the code reports `nil`
     rather than dragging against a wrong coordinate.
3. **Notes capacity.** Notes share the cvar store, which is length-bounded (the bound
   is not discoverable offline). Notes dominate the payload and are capped by it:
   measured, 100 characters with 20-char notes need 27 shards against a 6-cvar
   budget, so a large roster's notes cannot all persist. They are not silently
   dropped — `P.SaveDegraded` sacrifices them to keep the ORDER, and the caller
   clears them in memory so nothing is shown that will not come back. An in-world
   addon mirror (the `FreebornClaim` pattern) would remove the bound and is not
   implemented.
4. **Large-roster ordering depends on measured cvar capacity.** Measured, not
   suspected, and the gap against spec 11 is now *self-diagnosing* rather than
   guessed:
   * `P.Encode` leaves plain ASCII names alone, so once the realm is stored once
     (v2) a key costs only its own length: a 100-character order is **1219 payload
     chars**, down from 2219.
   * `P.ProbeCapacity` therefore **measures** each cvar at discovery — binary
     searching the longest value that reads back intact — and records the payload
     room on the slot. `P.ShardToSlots` then fills each slot to *its own* measured
     room. Nothing assumes `MAX_CHUNK` any more.
   * The limit matters: 100 characters fits 6 cvars only at a measured limit of
     ≈250 chars each (room 226 → 6 shards). At 200 it needs 7, at 170 it needs 9.
     Run `tools/measure_capacity.py` for the projected table.
   * So durability for a full roster is **conditional on the client**: if the
     probed room is short, the save fails cleanly (`SaveDegraded` will already have
     given up the notes) and the order is not persisted. The next lever is more
     candidate cvars in `P.CANDIDATE_CVARS` — the probe gates them, so a name that
     is not writable costs nothing but a failed probe.
   * Surfaced, not silent: a failed save shows `Order not saved - storage full` in
     the status line in the danger colour, and a degraded save says
     `Notes cleared - storage full` instead — the order did survive in that case, so
     telling the user "not saved" would be wrong. Both take priority over the search
     summary, because they are the only messages that report something actually lost.
4. **`GetCharacterInfo` field order is ambiguous.** Stock puts `raceFilename` where
   the fork reads `sex`. ECS trusts only fields 1–5 (identical in both) and
   shape-validates 6–10, so a wrong guess costs a portrait's gender, never a race,
   class, level or zone.
5. **Client/server race drift at 24/25/26** is unresolved (client rows are stale vs
   server SQL) and races 29/30/31 exist client-side with no server registration.
   ECS degrades safely either way, but this needs a product decision.
