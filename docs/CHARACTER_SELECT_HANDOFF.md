# ECS Handoff — Esteria Character Select

Written during the R47 pass, covering all work through R47 (R47 restores row-plate zoom
to 1.10× after both 1.40× and 1.20× looked too large in-client).
Everything
below is stated from the working tree, not from memory. Where something is **not**
verified, it says so explicitly — please keep that distinction intact.

---

## 0. Status in one screen

| | |
|---|---|
| Objective | Customize the 3.3.5a glue character-select screen while retaining stock Glue controls and art |
| Code state | **R47 deployed and green.** 1224 assertions, 0 failures, 0 dead code, 0 undefined refs |
| Deployed | R47 in both target Dev MPQs, **103/103 entries verified** |
| Latest backup | `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-091455` (both archives, pre-R47 deploy) |
| **Not** verified | **R47 has not yet been visually checked in the target Dev client.** See §6. |
| Biggest open risk | **In-client visual and interaction verification** is still outstanding. See §7.2 |

---

## 1. What this is, and where it lives

ElvUI cannot touch the login/char-select UI: GlueXML loads before addons. So ECS is
shipped as **patched GlueXML inside MPQs**, not as an addon.

Everything the addon ships lives under `.agents/plans/character-select-redesign/`
(that tree is **gitignored** — see the note below), with the two documents in `docs/`:

```
docs/CHARACTER_SELECT.md          the developer reference (12 sections)
docs/CHARACTER_SELECT_HANDOFF.md  this file

.agents/plans/character-select-redesign/
src/GlueXML/          16 files (15 Lua + the TOC) -> deployed to Interface\GlueXML\
  CharacterSelect.lua   the fork's file, patched (see §4.5)
  GlueXML.toc           load order (see §3.2)
  ECS_Constants.lua     every colour, texture path, layout and motion constant
  ECS_Schema.lua        race / class / faction / portrait resolution + fallbacks
  ECS_Order.lua         THE index mapping (visible order, custom order, filter)
  ECS_Data.lua          normalized character records from GetCharacterInfo
  ECS_Persistence.lua   cvar store: codec, sharding, capacity probe, degradation
  ECS_Notes.lua         per-character notes (draft/commit/cancel)
  ECS_Anim.lua          reusable tween framework + shared driver
  ECS_Search.lua        query state, summary, name-match highlighting
  ECS_Modal.lua         reusable modal stack (see §7.7)
   ECS_Row.lua           one roster row: build, bind, layered faction art, stock suppression
  ECS_Roster.lua        pooled virtualized roster: layout, offset, drag/drop
  ECS_Tooltip.lua       detail panel content + edge-clamped anchoring
    ECS_UI.lua            chrome: search box, status, modal, drivers, stock realm-control suppression
  ECS_Integrate.lua     wiring into live glue (wraps UpdateCharacterList)
tests/                13 test_*.lua + frame_shim.lua + run_tests.py
tools/                8 python tools (generator, deploy, audits, measurement)
textures/             65 BLPs + 65 source PNGs (~8 MB)
```

Read **`docs/CHARACTER_SELECT.md`** alongside this: 12 sections covering architecture,
the index-mapping invariant, persistence format, how to add a race/faction, styling
constants and known limitations.

`.agents/plans/**` is **gitignored**, so the `grep` tool silently returns nothing
inside it — use PowerShell `Select-String` instead, or you will conclude the code does
not exist. This is the trap that costs the most time here.

**Version-control status, checked rather than assumed:** `docs/` is *not* ignored (it
already tracks `docs/100-character-support.md`), but **neither `docs/CHARACTER_SELECT.md`
nor this file is committed** — both show as untracked in `git status`. Being in `docs/`
makes them committable, nothing more; `git add docs/CHARACTER_SELECT*.md` is still
required. Do not describe the design docs as "tracked in git" until that happens.

---

## 2. Commands

```powershell
# tests (needs lupa with the lua51 runtime; runs the REAL modules on Lua 5.1)
python .agents/plans/character-select-redesign/tests/run_tests.py

# regenerate portraits/ring/note dot/search icon from the source art
python .agents/plans/character-select-redesign/tools/make_ecs_portraits.py [--check]

# audit art keys against the create screen and the client's own plates
python .agents/plans/character-select-redesign/tools/check_artkeys.py
python .agents/plans/character-select-redesign/tools/check_framing.py
python .agents/plans/character-select-redesign/tools/measure_capacity.py

# deploy (CLIENT MUST BE CLOSED - it holds the archives open)
python .agents/plans/character-select-redesign/tools/deploy.py --client-data "G:\3.3.5a - Dev\Data" --dry-run
python .agents/plans/character-select-redesign/tools/deploy.py --client-data "G:\3.3.5a - Dev\Data"
```

Deploy prerequisites, all of which the tools assume:

* client data at `G:\3.3.5a - Dev\Data` (`patch-Z.MPQ`, `enUS/patch-enUS-Z.MPQ`)
* StormLib DLL via `tools/cars_mount_pack.py` (default path is in that file)
* source portraits at `R:\Users\Zach\Pictures\Portraits` (130×130 PNGs) for the generator

`deploy.py` copies both archives to a timestamped backup **before** writing, merges
the payload, then verifies every new entry round-trips and samples pre-existing
entries to prove they are unchanged. Never treat a deploy as done without that output.

Art precedence, highest first: `enUS\patch-enUS-Z.MPQ` > `patch-Z.MPQ` > … The deploy
writes **both** because the external contract test reads both.

---

## 3. Architecture

### 3.1 Strategy: wrap, do not rewrite

`ECS_Integrate` wraps the global `UpdateCharacterList`: the stock function runs in
full, then ECS re-skins. Two live contracts force this:

* `tools/test_character_select_contract.py` (external, in the repo root `tools/`) pins
  exact strings inside `CharacterSelect.lua`. **It cannot run in this checkout** — it
  reads a client path that does not exist here — so `run_tests.py::contract_check`
  re-enforces the same assertions locally.
* `CharacterCreate.lua`'s Freeborn code re-wraps `UpdateCharacterList` and looks row
  buttons up **by name**, expecting a `…FactionIcon` child and `button:GetID()` to
  return the **real** index.

Load order matters: `ECS_Integrate.lua` is listed **after** `CharacterCreate.xml` in
the TOC so ECS wraps the already-Freeborn-wrapped function.

### 3.2 Module load order

Pure data/logic first (no frame access at load), then XML, then integration:

```
ECS_Constants Schema Order Data Persistence Notes Anim Search Modal Row Roster Tooltip UI
... GlueParent.xml ... CharacterSelect.xml ... CharacterCreate.xml ...
ECS_Integrate.lua        <- last, so its file-scope Install() can wrap everything
```

`ECS_UI` only *defines*; nothing is created until `Install` runs.

---

## 4. Invariants you must not break

### 4.1 The index mapping (the critical one)

Blizzard's list is indexed `1..numChars`; **that** index is what `SelectCharacter` /
`DeleteCharacter` / `EnterWorld` take. The roster shows a filtered, reordered view.

* `ECS.Order.visible[i]` = the **real** index of the i-th visible row.
* `ECS.Order.realToVisual[r]` = its visual position.
* Roster offsets are expressed in **visual** positions.
* **`button:SetID()` always carries the REAL index.** Never assume
  `visualIndex == realIndex`.
* When the selected character is filtered out, ECS **keeps the real selection** and
  draws no selected row. That choice cannot cause accidental entry; write no code that
  changes it without thinking about Enter World.

### 4.2 The offset is a whole row, always

`R.offset` doubles as a visual position and as the argument to `Order.RealIndexAt`,
which indexes `O.visible[pos]` **without rounding**. A fractional offset yields `nil`
for every row (blank roster) and makes the stock `UpdateCharacterSelection` build
`"CharSelectCharacterButton1.55"` → nil → error inside the glue screen. `R.ClampOffset`
floors, and that is load-bearing. Do not add a fractional scroll rate.

### 4.3 Persistence

Glue has no `SavedVariables`. The only channel is a **string cvar the client never
parses** (`Sound_VoiceChat*DriverName`, `lastCharacterDeleted`, `agentUID`, `portal`).

* `GetCVar`/`SetCVar` **throw** on names the client does not know → always `pcall`.
  An uncaught glue error can crash the client.
* Only login-registered names are writable → candidates are **probed**; integer cvars
  are normalised on load, so the store must be a string.
* Value format: `ecsN:<len>|<shard><original>`. The length prefix is essential — the
  shard contains `|`, and a delimiter split silently truncates (that bug emptied the
  account field and disabled account scoping).
* Freeborn badge hashes share two candidate cvars. ECS wraps their existing `fb:`
  records in the original-value suffix; `ECS.Schema.FreebornHashes` unwraps nested
  `ecsN` layers before matching names. Do not make consumers assume `fb:` is at byte 1.
* Payload: `v=|a=|r=|o=|n=`. `SCHEMA_VERSION = 2`.
* **Order and note keys are stored WITHOUT their realm prefix** (the record's `r=` has
  it once). At 20 chars/key a 100-character order needed 14 shards against a 6-cvar
  budget and could never be saved; compacting took it to 1219 chars.
* `P.ProbeCapacity` **measures** each cvar's real length limit (binary search on
  read-back) and restores the value it found, so measuring can never damage a record.
  `P.ShardToSlots` fills each slot to its own measured room.
* `P.SaveDegraded` retries with notes dropped so the **order** survives when notes do
  not, and the caller clears notes in memory so the UI never shows notes that will
  vanish. A failed save is surfaced in the status line.
* Stable key = `lower(realm)..":"..lower(name)`. **A rename looks like a delete plus a
  create** — the character is adopted at the tail and its note does not follow.

### 4.4 Schema

Race is resolved from the background **model string** (`GetSelectBackgroundModel`),
because the glue's `RACE_DATA` is a 1..19 **ordinal** table, not ChrRaces IDs.

* The **art key is the client's portrait FILE name**, not the model token or the source
  file name: `undead`→`Scourge`, `ZandalariTroll`→`Zandalari`, `panda`→`Pandaren`,
  `illidari`→`DemonHunterAlliance`/`DemonHunterHorde` by folder.
  `tools/check_artkeys.py` cross-checks every key against the create screen's own
  `RACE_ICON_TEXTURES` and against the plates inside the client archives.
* `S.PortraitArtKeys` gates the ECS namespace; anything else falls back to the create
  screen's plate. The same tool verifies that table against the files on disk **in both
  directions**.
* `D.AsSex` supports both signatures: stock field 6 is a race filename and field 8
  is gender 0/1; the Esteria fork returns `SEX_MALE=2` / `SEX_FEMALE=3` in field 6.
  Field 6 is normalized first so a fork's field-8 PCC value cannot turn every female
  portrait into male art.

### 4.5 CharacterSelect.lua differs from the fork's original in four places

1. keydown tests `key` (the fork referenced an undefined `arg1`);
2. `UpdateCharacterList` calls `CharacterSelectCharacterScrollFrame:UpdateScrollChildRect()`;
3. `CharacterSelect_OnVerticalScroll` calls `GlueScrollFrame_OnVerticalScroll(self, offset)`;
4. **both** arrow directions delegate to `ECS.Integrate.StepSelection(±1)`, each with
   the stock branch kept as the no-ECS fallback.

All four are contract-pinned locally. Do not undo them.

---

## 5. Interaction ownership — the bug class that dominates this codebase

**A hook ADDS a handler; it does not replace one.** Anything ECS hooks that the stock
glue already handles runs *both*, and for anything that moves state that is a bug, not
a safety net. Every serious bug found in rounds 12–17 was of this shape, and **none**
were visible to 900+ offline assertions — they were found by reading
`CharacterSelect.lua`/`CharacterSelect.xml` against ECS's code.

| # | Defect | Consequence |
|---|---|---|
| 1 | ECS hooked the scroll frame's `OnMouseWheel` in addition to stock, and moved by **0.45 of a row**, assigning `select.scrollOffset` directly (bypassing the stock clamp that rounds) | One notch scrolled twice; the fractional offset made `RealIndexAt` return nil for **every** row → blank roster; potential glue error |
| 2 | Only DOWN/RIGHT delegated to ECS's visual order; UP/LEFT still moved by server index | Under a custom order/filter, DOWN moved to the next *visible* row while UP jumped somewhere unrelated |
| 3 | `R.SyncScrollbar` set only its own `R.applyingScroll` flag (**nothing read it**) while `SetVerticalScroll` fires `OnVerticalScroll` synchronously | ECS's own scroll re-entered the stock path, which rebinds rows from **server order**, and ECS's `I.applying` guard suppressed the repair. Triggered by a filter shrinking the visible count while scrolled down |
| 4 | ECS replaced the row but left the stock `GeneralBackground` plate and **six `ButtonText*` FontStrings** visible | Stock plate drew over the ElvUI tile (and over the selected row's accent fill); stock name/level/class drew **across ECS's portrait** and beside ECS's own text, on *every* row |
| 5 | ECS positioned the pool at the stock frame's top edge instead of applying `ROSTER_TOP`, and only reconciled after `UpdateCharacterList` | Rows covered the search/header; the War Band visibility toggle could show stock row text after ECS's last pass, while the empty state remained stale |
| 6 | Stock row suppression depended on region names and used `Hide()` only; count could lag the visible War Band rows | Unlisted stock FontStrings/textures remained visible after `Show()`, and the empty state could cover a populated list |
| 7 | Stock scroll targets a 1px-wide scroll frame and uses the stock 67px row step while ECS rows live outside it at 70px spacing | Wheel events over the visible rows did not reliably reach the list; wheel/scrollbar routing must use the ECS visual offset directly |

Rules that follow, and that the next change must respect:

* **Never hook what stock already handles** unless you also suppress the stock side.
* Suppression of stock row state must run on **every refresh**, not once in
  `Build` — the stock pass re-writes and re-shows its regions each time it binds a row,
  while `Build` runs once per button.
* Two stock regions must **not** be hidden: `FactionIcon` (ECS adopts that exact
  texture and re-anchors it, which is why the Freeborn wrapper still finds it) and
  `Customize`/`RaceChange`/`FactionChange` (paid features; they anchor `TOPRIGHT` to
  the row's `TOPLEFT` at (−15, 6), i.e. outside the row, so they do not collide).
* Row buttons are safe to hook: the template binds only `OnLoad`, `OnClick`,
  `OnDoubleClick`, `OnMouseWheel`, and ECS hooks `OnMouseDown`/`OnMouseUp`/
  `OnEnter`/`OnLeave`. Every `SetScript`/`HookScript` ECS installs has been audited
  against the XML; everything else lives on an ECS-owned frame.
* Row buttons remain children of `CharacterSelectCharacterFrame` for visibility and
  action compatibility, but their visual anchors are screen-relative and use
  `ROSTER_TOP`/`ROSTER_RIGHT`. They are **not** anchored to the 1 px scroll child.
  Stock scrolls by rebinding which character each fixed row shows — ECS does the same,
  which is why `R.offset` selects *content* per slot and never displaces a row.
* The hidden War Band list toggle calls `CharacterSelect_OnEventO2` and shows the stock
  frame without going through `UpdateCharacterList`. ECS wraps that toggle and the
  relevant selection/list events so stock rows are reconciled if the path is invoked.
* Chrome is parented to **`CharacterSelectUI`**, never `UIParent`. `GlueParent` has no
  `parent` attribute (so it is a child of UIParent) and `SetGlueScreen` hides the
  screens — chrome under UIParent stayed drawn over character creation, options and the
  intro movie. The one exception is `ECSAnimDriver`, left parentless on purpose: a
  hidden parent stops `OnUpdate`, and a tween interrupted by a screen switch would
  never advance, leaving the deletion path's `onDone` (which restores the roster)
  unfired.

---

## 6. Verification status — read this before claiming anything works

**Proven offline** (1224 assertions on real Lua 5.1 via `lupa.lua51`):

order/filter/reorder/prune · a 100-character roster with exactly eight visible rows ·
explicit row/frame wheel routing and native scrollbar routing · screen-relative row anchors
· persistent stock-region suppression · Illidari display-name/race-ID/raceFilename
faction portrait mapping · default button textures · transparent list backdrop · tooltip
strata/leave behavior ·
Hero fallback · class badges/names, zones and optional notes · both `GetCharacterInfo` layouts
including both stock and fork female-sex encodings · full cvar store round-trip incl. scoping, sharding,
corruption, capacity probing and write-side degradation · note hygiene and Cancel
semantics · tween replacement/cancel/pooling · row recycling with no bleed-through ·
tooltip edge clamping over a grid of cursor positions · modal stack rules · the
whole-row offset invariant · stock row-art suppression · the persistence notice · a
simulated client restart · native action-button sizing/anchors and vanilla button texture
restore · hidden, mouse-disabled rotation controls · grey idle row art · Alliance/Horde/
Freeborn hover art and gold selection precedence · strict numeric row IDs during filtered/
short-page refresh · CharacterCreate-matched tooltip textures · stock selection changes
preserving the current visual page · both stock and fork sex encodings selecting the
correct portrait · power-of-two search icon BLP · native gold button fonts and lowered
Enter World/Create button anchors · blue Glue button art on stock actions · hidden stock
realm name/list/Warband controls · raised search and roster · Create/Delete centerline
alignment · icon-only blue Delete · 10% zoomed idle/hover/selection row art · Freeborn
hash recovery through nested ECS cvar wrappers, logo selection, and purple hover art.

`run_tests.py` also carries the **wiring audit**, which exists because of a real miss
(the drag path shipped with `UpdatePress` tested but reachable only from mouse-DOWN).
It reports, and enforces, that every public function is reached by production code,
used in-file under its local name, or exercised by a test — **anything else fails the
run**. A function referenced only by tests prints as a warning; that is where a wiring
gap hides.

**Still not verified for R45 in the target Dev client:** pixels; cursor-to-row drag
coordinates; deletion fade timing; wheel feel; and whether the capacity probe finds
enough room on the real client. The prior screenshots came from `G:\BearCave\Wow.exe`;
R28 is deployed to the requested `G:\3.3.5a - Dev\Wow.exe` client, so compare that
client before judging these fixes. Verify the result rather than trusting offline coverage.

---

## 7. Open work, in priority order

### 7.1 Duplicate realm label — fixed in round 20

The fork already displays the realm. `CharacterSelect.lua:81-101`, on the screen's show
path right beside `GetCharacterListUpdate()`:

```lua
local serverName, isPVP, isRP = GetServerName();
...
    serverName = serverName.."\n("..SERVER_DOWN..")";   -- only when not connected
...
CharSelectRealmName:SetText(serverName.." "..serverType);
CharSelectRealmName:Show();                              -- <-- line 98
```

Geometry — the two labels are drawn in nearly the same box:

* `CharSelectRealmName` is a `GlueFontDisableLarge` FontString inside
  `CharacterSelectCharacterFrame` (XML line 746), anchored `TOP (0,−10)` +
  `LEFT (+8,0)` + `RIGHT (−8,0)`: spanning that panel's width, 10 px below its top,
  centred.
* `CharacterSelectCharacterFrame` is **260×642** at `TOPRIGHT (−5, −15)` (XML line 733).
* ECS previously added a **174×30** WotLK-blue realm bar, flanked by the change-realm
  and list-visibility controls; R44 removes all three controls.

**The round-19 investigation established three constraints:**

1. **It is `Show()`n explicitly**, so hiding it once would be undone — the same trap as
   the row regions in §5.4. Suppression must run after every stock pass.
2. The boxes nearly coincide (roughly x ∈ [right−257, right−13], y ∈ [top−25, top−38])
   with *different strings*, so the stock text showed through or beside ECS's translucent
   bar before the fix.
3. **Hiding it without replacing its information would regress the UI.** The stock label
   is not merely the realm name: it carries the PvP/RP marker (`PVP_PARENTHESES` /
   `RP_PARENTHESES` / `RPPVP_PARENTHESES`) and a `(SERVER_DOWN)` note when
   `IsConnectedToServer()` is false. Before round 20, ECS's bar showed `GetRealmName()` only.

Rounds 20–43 preserved the stock label's information while removing its visual
duplicate. R44 removes the realm name entirely as requested and keeps all stock realm
controls hidden after each refresh:

* `I.RealmLabel()` calls `GetServerName()` with a direct `pcall` so it can capture all
  three returns (`name, isPVP, isRP`), selects the corresponding localized marker, and
  falls back to `I.RealmName()` if the getter is unavailable or fails;
* locale globals are read defensively, so a missing marker does not raise;
* when `IsConnectedToServer()` is false, the localized server-down note is appended
  **inline** to fit the single-line ECS bar;
* `U.SetRealmName()` now suppresses `CharSelectRealmName`, the change-realm control,
  and the Warband toggle (including label/background) after each stock refresh; it adds
  no replacement realm text;
* all three integration call sites now pass `I.RealmLabel()`.

Prior regression coverage checked RP/PvP markers and server-down status. R44 replaces
that display with empty chrome and verifies every stock realm control remains hidden
after a stock refresh.

### 7.2 In-client verification (the dominant risk)

Launch `G:\3.3.5a - Dev\Wow.exe` and check, in this order: realm name, realm-list `<`
and Warband controls are all absent; search and roster have moved up; Delete aligns vertically
with Create Character; row plates look about 10% larger; Freeborn rows show the Freeborn
logo and purple hover plate; exactly eight rows show at once and wheel/scrollbar can reach
the rest; there is no black panel behind the list; Illidari portraits load for both factions;
nav buttons use the blue WotLK appearance; hover tooltips sit above the roster; unknown
classes read `Hero`; stock text/plates do not reappear if stock refreshes; portraits,
selected row, search, drag, notes, delete and Enter World all work. Compare with the
reference screenshot and report any remaining mismatch.

Class badges now use the client's class atlas when a class has an atlas entry; custom
classes without one still have no badge. The R45 deployment has not been visually checked
in-client.

### 7.3 Two-line density — resolved by the supplied reference

The reference shows a class-coloured name and one grey zone line, with a third line only
when a character has a note. Round 20 applies that layout: level stays on the portrait
badge, absent locations display `Unknown Zone`, race/class remain searchable and
available in the detail panel, and a saved note appears on the optional third line. The
supplied image resolves the density decision.

### 7.4 Stale entries in the archives

`deploy.py` **merges** entries; it never deletes. `ECS-Portrait-DemonHunterMale.blp`
and `…Female.blp` (retired generations, ~46 KB) are still inside **both** MPQs and
referenced by nothing. Removing them needs archive surgery, not a deploy.

### 7.5 Two races have no portrait art

`Forsaken` and `Sethrak` have no plate in the client, on the create screen, or in the
source set, so their rows render no portrait (by design, rather than a wrong one).
Closing this needs new art, then a re-run of the generator.

### 7.6 Large-roster capacity is conditional on the client

A 100-character order is 1219 payload chars. `tools/measure_capacity.py` projects:
fits 6 cvars only if they hold ≈250 chars each (at 200 it needs 7, at 170 it needs 9).
The probe measures the truth at runtime; if the room is short the save fails cleanly and
the status line says so. Adding more names to `P.CANDIDATE_CVARS` is the next lever —
the probe gates them, so an unwritable name costs only a failed probe.

### 7.7 `ECS.Modal` has no production consumer

Deliberate: the only destructive flow (delete) keeps the stock confirmation, because it
gates deletion behind a typed confirm string and a protected-name list, and replacing
that with our own would weaken a safety feature for a cosmetic gain. The framework is
built and tested; if you want it used, pick a specific action with the human first.

### 7.8 Keep the docs honest

`docs/CHARACTER_SELECT.md` and `character-select-redesign.PLAN.md` both state the
assertion count as **1224**. It is updated by hand — update it whenever you add tests,
or say the count is stale.

---

## 8. Traps specific to this codebase

* **Lua 5.1 only.** No `//`, no `goto`, no `AnimationGroup`, no `#` on sparse tables.
  The client is 3.3.5a and the tests run genuine Lua 5.1.
* **`--[[ ]]` comments containing `]]` close early.** Use `--[==[ ]==]` for anything
  that quotes Lua indexing (this has already bitten once).
* **`.agents/plans/**` is gitignored** → the `grep` tool returns nothing; use
  `Select-String`.
* **`0` is truthy in Lua.** `D.AsSex(x) or D.AsSex(y)` is correct for 0; do not
  "clean up" that chain.
* **Do not add a second generator or a second serialiser.** Both existed and were
  removed as drift hazards: a parallel `Order.Serialise`/`Deserialise` pair was tested
  while production used `P.Serialise`, which made the format look covered when the live
  path was not.
* **Do not "fix" the fork's mislabelled `GetCharacterInfo` destructuring** (§4.4).
* **Do not hide `FactionIcon` or the paid-service buttons** (§5).
* **The wiring audit will fail your build** for a public function with no production
  caller, no in-file local use, and no test. That is deliberate.
* `deploy.py`, `make_ecs_portraits.py`, `check_artkeys.py` depend on
  `.agents/plans/elvui-glue-reskin/blp.py` (BLP codec) and `tools/cars_mount_pack.py`
  (StormLib wrapper). The `blp` name collides with an installed PyPI package — the
  tools insert the plan path **before** `import blp`, so keep that ordering.
* An oversized write to a cvar is **detected** by read-back verification, not trusted,
  which is why `MAX_CHUNK` tuning is safe to experiment with.

---

## 9. Decisions that need a human

1. Whether to use `ECS.Modal` for a concrete action (§7.7).
2. Whether to spend archive surgery removing the two stale BLPs (§7.4).
3. Anything requiring new art for `Forsaken`/`Sethrak` (§7.5).

---

## 10. Recent change log (why things are the way they are)

* **R12** Wiring audit introduced; 7 dead functions removed (two were silent no-ops
  targeting setters that do not exist). Invented `LoadDegraded` — an impossible
  "strip notes and re-read" recovery — then deleted it rather than ship
  plausible-looking dead code. Found the order essentially unpersistable for a full
  roster and compacted the keys (v1 → v2).
* **R13** Removed the wheel hook (blank-roster bug, §5.1). Made UP/LEFT delegate (§5.2).
  Surfaced failed saves in the status line.
* **R14** Zandalari art key fixed (it requested a file that does not exist, so those
  rows had **no portrait**). Portraits rebuilt from the 130×130 source art; the old
  generator was retired. `check_artkeys.py` added.
* **R15** Selection fill was `{0.06,0.06,0.06,0.92}` against an idle backdrop of
  `{0.06,0.06,0.06,0.80}` — the same colour, so a selected row read as unselected.
  Now uses the ElvUI accent, with tests pinning the colour distance.
* **R16** `R.SyncScrollbar` re-entrancy (§5.3). Sex convention verified against the
  stock client; UnitSex rejection pinned. Search placeholder now names the searched
  fields; magnifier icon generated and wired.
* **R17** Stock row plate **and six stock FontStrings** suppressed on every refresh
  (§5.4), with the two deliberate exceptions and their geometry verified.
* **R18** No code change: deployed on request and produced this handoff.
* **R19** No code change: deployed again, moved this document from the gitignored plans
  tree into `docs/` (committable, and still needing `git add`), and investigated §7.1 to
  implementation-ready depth. The material finding is that the stock realm label is not
  just the realm name — it carries the PvP/RP marker and a server-down note — so hiding
  it without reproducing that string would trade a visual duplicate for a small
  information regression.
* **R20** Implemented §7.1 and resolved §7.3 from the reference: ECS reproduces the
  stock realm marker and server-down note in its single-line header, suppresses the stock
  label after every refresh, and renders class-coloured name + zone (with an `Unknown
  Zone` fallback) + optional note rows.
  Regression coverage passes (1009 assertions). Both archives deployed with 75/75 entries
  verified; pre-existing sampled entries are unchanged. Backup:
  `G:\3.3.5a - Dev\Backups\character-select-ecs-20260925-050824`. In-client visual
  verification remains outstanding.
* **R21** Reworked the live layout after the screenshot showed rows at the header edge
  with stock text over them and a false empty state: row buttons now use a screen-relative
  anchor below search, the realm/title controls move into a red/gold top bar, and the
  bottom actions are restacked/skinned to match the reference. Added a class-atlas badge
  when the class has a client icon. ECS now reconciles after the War Band list toggle and
  list/selection events so stock text cannot resurface over its rows. Tests pass (1038
  assertions); both MPQs deploy with 75/75 entries verified. Backup:
  `G:\3.3.5a - Dev\Backups\character-select-ecs-20260925-061002`. In-client visual
  comparison is still open.
* **R22** Made stock suppression survive later `Show()` calls with alpha-zeroing and a
  region sweep that preserves ECS-owned regions and the Freeborn `FactionIcon`. Added a
  visible-stock-row ID fallback for count lag, and regression coverage for both fixes.
  Tests pass (1044 assertions); both archives deploy with 75/75 entries verified.
  Backup: `G:\3.3.5a - Dev\Backups\character-select-ecs-20260925-065609`. R22 still
  needs a fresh in-client comparison.
* **R23** Corrected the deployment target after discovering the screenshots were from
  `G:\BearCave\Wow.exe`; the requested target is `G:\3.3.5a - Dev\Wow.exe`. Added
  `--client-data`/`--backup-root` to the deploy tool for explicit client selection and
  deployed the current 1044-assertion payload to the Dev archives, 75/75 verified.
  Backup: `G:\3.3.5a - Dev\Backups\character-select-ecs-20260925-071134`. A fresh
  screenshot from the target Dev client is still needed.
* **R24** Capped the visible roster at eight while preserving scrolling, hid the stock
  list backdrop, mapped both Illidari factions to their generated portraits, restored
  stock button rendering, raised hover tooltips to `TOOLTIP` strata, and changed the
  unknown-class label to `Hero`. Tests pass (1068 assertions); the Dev MPQs deploy with
  75/75 entries verified. Backup:
  `G:\3.3.5a - Dev\Backups\character-select-ecs-20260925-075309`. A fresh target-client
  screenshot is still needed.
* **R25** The R24 client screenshot exposed the overflow rows calling `SetID(nil)`, which
  aborts the refresh with `Usage: ...SetID(ID)` before scroll state updates. Removed that
  invalid call, kept hidden rows' stock IDs, and made the tooltip frame hide when hover
  ends. Tests pass (1070 assertions); both Dev MPQs deploy with 75/75 entries verified.
  Backup: `G:\3.3.5a - Dev\Backups\character-select-ecs-20260925-082001`. Fresh visual
  verification remains open.
* **R26** The follow-up screenshot still could not scroll and showed the Illidari as
  unknown. Replaced wheel handling on visible rows and the one-pixel stock scroll frame
  with `I.ScrollBy`, and routed native scrollbar changes using ECS's 70px visual-row step.
  The target Dev `ChrRaces.dbc` confirms Illidari IDs **30 (Horde)** and **31 (Alliance)**;
  added real-ID overrides so the generic `Illidari` model token still selects the correct
  generated plate. Tests pass (1090 assertions); both Dev MPQs deployed with 75/75
  entries verified. Backup: `G:\3.3.5a - Dev\Backups\character-select-ecs-20260925-173207`.
  Fresh target-client verification is still needed.
* **R27** The latest screenshot confirms Illidari race data arrives from `GetCharacterInfo`
  as a display-name string on this client, so the R26 numeric overrides were bypassed.
  `ECS_Data` now preserves a textual race hint and resolves it with model metadata;
  faction-specific model tokens keep the Alliance/Horde art split. Tests cover both
  string-race layouts. Direct row/frame wheel and native scrollbar routing is covered
  end-to-end in the shim. Tests pass (1094 assertions).
* **R28** Inspected the actual Dev `ChrRaces.dbc`: Illidari rows are 30 Horde and 31
  Alliance, but `GetCharacterInfo` supplies the localized/display race string. `ECS_Data`
  now keeps that string as a race hint, schema recognizes the shared Illidari token, and
  faction-specific model tokens or IDs override to the correct portrait art. Also added
  direct wheel/scrollbar routing from the eight visible rows and a Lua test for offset
  synchronization. Tests pass (1096 assertions); both Dev MPQs deploy with 75/75 entries
  verified. Backup: `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-004931`.
  Fresh target-client verification remains open.
* **R29** Kept the stock `GetCharacterInfo` race-file string from field 6 in normalized
  data. It can carry `ILLIDARI_HORDE` / `ILLIDARI_ALLIANCE` even when field 2 and the
  background model are the shared `Illidari` label, so the portrait side is now resolved
  from that higher-specificity token. Regression coverage passes (1100 assertions); both
  Dev MPQs deploy with 75/75 entries verified. Backup:
  `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-021309`. Visual verification
  in the target client remains open.
* **R30** Resolved conflicting Illidari metadata by preferring faction-qualified Horde/
  Alliance model or race-file tokens over a generic `Illidari` label. Regression coverage
  pins a generic raceFilename alongside an Alliance-qualified model. Tests pass (1101
  assertions); both Dev MPQs deploy with 75/75 entries verified. Backup:
  `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-021906`. Fresh visual
  verification remains open.
* **R31** Converted the supplied portrait frame, red selected plate, blue hover plate
  and level border to power-of-two BLP2 assets. The roster now draws red/blue row art
  below content (red wins when hovered and selected), uses the supplied portrait frame
  and frames the level text. Offline tests pass (1123 assertions); both target Dev MPQs
  have all 78 payload entries verified and sampled existing entries are unchanged.
  Backup: `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-024203`. In-client
  visual verification remains open.
* **R32** Enlarged the portrait frame to prevent face art protruding, reduced the level
  frame to 24px and shifted the badge 6px up/left. Tightened the five text action buttons
  to their measured label widths and moved Create/Delete to the screen's bottom-right.
  Tests pass (1141 assertions); both target Dev MPQs verified all 78 payload entries and
  sampled existing entries are unchanged. Backup:
  `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-030550`. Visual verification
  remains open.
* **R33** Reconverted the updated `LevelBorder32.png` to BLP2, hid and disabled both
  rotation controls, and restored native action-button sizes and anchors. Create/Delete
  stay in the requested bottom-right position. Tests pass (1155 assertions); both target
  Dev MPQs verified all 78 payload entries and sampled existing entries are unchanged.
  Backup: `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-033159`. Visual
  verification remains open.
* **R34** Added grey idle row art, faction-specific Alliance-blue/Horde-red/Freeborn-purple
  hover art and gold selection art. Grey remains visible underneath the overlays, and
  gold selection wins over hover. Converted five row plates to power-of-two BLP2 assets.
  Tests pass (1166 assertions); both target Dev MPQs verified all 81 payload entries and
  sampled existing entries are unchanged. Backup:
  `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-035020`. Visual verification
  remains open.
* **R35** Crossfaded between grey idle and faction-hover plates so each fully hovered
  row displays only its faction color; gold still replaces hover when selected. Tests
  pass (1174 assertions); both target Dev MPQs verified all 81 payload entries and
  sampled existing entries are unchanged. Backup:
  `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-035408`. Visual verification
  remains open.
* **R36** Removed the invalid `SetID(nil)` reset so short/filter result pages can hide
  pooled rows without aborting refresh; hidden rows retain a valid numeric id until the
  next bind. Applied the character-create tooltip's exact background/border textures,
  tile geometry and colors to the roster hover tooltip. Tests pass (1183 assertions);
  both target Dev MPQs verified all 81 payload entries and sampled existing entries are
  unchanged. Backup: `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-040913`.
  Visual verification remains open.
* **R37** Replaced flat WHITE8X8 panel fills with tiled CharacterCreate tooltip textures
  and removed the flat row backdrop. The stock server-index scroll adjustment now uses
  ECS visual positions, so selecting an already-visible character preserves the list
  window. Tests pass (1188 assertions); both target Dev MPQs verified all 81 payload
  entries and sampled existing entries are unchanged. Backup:
  `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-041752`. Visual verification
  remains open.
* **R38** Deployed the finalized textured-panel and native-control styling together with
  a visual-order-aware stock selection-offset override. Selecting an already-visible
  character preserves the roster page, while an off-page selection scrolls to its visual
  row. Tests pass (1188 assertions); both target Dev MPQs verified all 81 payload
  entries and sampled existing entries are unchanged. Backup:
  `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-043538`. Visual verification
  remains open.
* **R39** Restored 19 vanilla panel/Glue button textures from the client locale archive
  plus the stock Delete-button atlas from patch-A, normalized the fork's 2/3 sex enum
  so female characters select female portraits, and regenerated the search icon as a
  32×32 BLP to remove its missing-texture green box. Tests pass (1189 assertions); both
  target Dev MPQs verified all 101 payload entries and sampled existing entries are
  unchanged. Backup:
  `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-052845`. Visual verification
  remains open.
* **R40** Restored gold-with-black-shadow Glue normal fonts, lowered Enter World and
  Create Character slightly, and added a post-selection page-preservation guard to
  complement the visual-index scroll adjustment. Tests pass (1193 assertions);
  both target Dev MPQs verified all 102 payload entries and sampled existing entries are
  unchanged. Backup: `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-054940`.
  Visual verification remains open.
* **R41** Fixed the login-time Video Options font error by sourcing GlueFontStyles.xml
  from patch-enUS.MPQ, retaining its required Options font definitions along with the
  gold Glue button fonts. Tests pass (1193 assertions); both target Dev MPQs verified
  all 102 payload entries and sampled existing entries are unchanged. Backup:
  `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-061457`. Visual verification
  remains open.
* **R42** Switched the stock Glue button image paths to the WotLK blue variant and
  applied the same treatment to the realm banner, Warband toggle and Delete button.
  Enter World/Create Character moved lower. Tests pass (1205 assertions); both target
  Dev MPQs verified all 102 payload entries and sampled existing entries are unchanged.
  Backup: `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-071727`. Visual
  verification remains open.
* **R43** Kept the blue WotLK art on standard Glue actions and the realm banner, while
  returning the Warband toggle to its own native artwork. Delete is now a compact 32px
  icon-only blue control with its stretched label cleared; the realm-list control is
  32px wide and the realm banner is 30px tall. Tests pass (1213 assertions); both target
  Dev MPQs verified all 103 payload entries and sampled existing entries are unchanged.
  Backup: `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-075847`. Visual
  verification remains open.
* **R44** Removed the realm name, realm-list `<` and Warband controls (including stock
  controls that are re-shown during refreshes); moved search from top 50 to 18 and the
  roster from top 90 to 58. Delete now anchors to Create Character's right edge at the
  same vertical centerline. Idle, hover and selected row plates are zoomed 10% by texture
  coordinates without changing row hitboxes. Tests pass (1218 assertions); both target
  Dev MPQs verified all 103 payload entries and sampled existing entries are unchanged.
  Backup: `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-083617`. Visual
  verification remains open.
* **R45** Increased row backdrop zoom from 1.10× to 1.40× (10% plus the requested
  additional 30%). Freeborn hashes are now recovered from nested ECS wrappers around
  their shared cvars, restoring the Freeborn logo and purple hover art after persistence
  writes. Tests pass (1224 assertions); both target Dev MPQs verified all 103 payload
  entries and sampled existing entries are unchanged. Backup:
  `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-090253`. Visual verification
  remains open.
* **R46** Reduced the row backdrop zoom from 1.40× to 1.20× after the user found 1.40×
  too large. Tests pass (1224 assertions); both target Dev MPQs verified all 103 payload
  entries and sampled existing entries are unchanged. Backup:
  `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-091100`. Visual verification
  of the revised scale remains open.
* **R47** Restored the row backdrop zoom to 1.10× after the user found 1.20× was still
  too large. Tests pass (1224 assertions); both target Dev MPQs verified all 103 payload
  entries and sampled existing entries are unchanged. Backup:
  `G:\3.3.5a - Dev\Backups\character-select-ecs-20260926-091455`. Visual verification
  of the restored scale remains open.
