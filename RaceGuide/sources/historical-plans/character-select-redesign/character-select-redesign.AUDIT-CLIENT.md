# Character Select — Client-Side Audit Findings

Companion to `character-select-redesign.AUDIT.md`. Produced by a read-only audit of the
**winning (deployed)** glue files. All four files are byte-identical across
`deployed-root`, `deployed-locale` and `winning`.

| File | Lines |
|---|---|
| `CharacterSelect.lua` | 1124 |
| `CharacterSelect.xml` | 1632 |
| `GlueParent.lua` | 645 |
| `CharacterInfo.lua` | 639 |

---

## Character data — the one ambiguous thing, and how to handle it

Sole full read (`CharacterSelect.lua:575`):

```lua
local name, race, class, level, zone, sex, ghost, PCC, PRC, PFC = GetCharacterInfo(actualIndex);
```

Stock 3.3.5a returns a **different positional layout**
(`name, race, class, level, zone, raceFilename, classFilename, gender, ghost, PCC`).
The fork treats field 6 as `sex` and 7 as `ghost`; stock has field 6 as `raceFilename`.

**The real signature is NOT CONFIRMED** — there is no C source or definition available,
and the fork's field names may simply be wrong.

**Design decision:** `ECS_Data` builds `CharacterData` from only the fields that agree
between both layouts — **1 `name`, 2 `race` (ID), 3 `class` (ID), 4 `level`, 5 `zone`** —
and treats fields 6–10 as **optional, shape-validated** extras (a sex value must be a
number in 0..1, else discarded). This makes the roster correct regardless of which
signature the binary actually has, and cannot produce a wrong-looking row.

Custom beyond stock: two paid-service flags (`PRC`, `PFC`) and the API
`GetSelectBackgroundModel(index)`. Whether `PRC`/`PFC` are client-custom: NOT CONFIRMED.

## APIs and events actually used

- `GetCharacterListUpdate()` on show (only when `IsConnectedToServer()`), else a local
  `UpdateCharacterList()`. **No `GetCharacterList()` / `RequestCharacterList()` exist.**
- Events: `CHARACTER_LIST_UPDATE`, `ADDON_LIST_UPDATE`, `UPDATE_SELECTED_CHARACTER`,
  `SELECT_LAST_CHARACTER`, `SELECT_FIRST_CHARACTER`, `SUGGEST_REALM`,
  `FORCE_RENAME_CHARACTER`.
- `GetNumCharacters()`, `GetCharacterInfo(index)`, `SelectCharacter(id)`, `EnterWorld()`,
  `DeleteCharacter(index)`, `RenameCharacter(index, text)`, `CreateCharacter(name)`,
  `SetGlueScreen(name)`, `SetBackgroundModel`, `GetSelectBackgroundModel`.

## Selection / enter world — two gaps the spec explicitly requires fixing

- Selection state is `CharacterSelect.selectedIndex`; the highlight is applied by
  `UpdateCharacterSelection` (:463) using `LockHighlight`/`UnlockHighlight` against rows
  whose `SetID(actualIndex)` was stored at :577.
- `SelectCharacter(id)` is the C call that actually changes the selected character (:888).
- `CharacterSelect_EnterWorld()` (:1015) → `EnterWorld()`.
- **Gap 1: there is NO double-entry guard** (§18 asks to protect against accidental double
  execution). Needs adding.
- **Gap 2: `CharacterSelect_OnKeyDown` DOWN/RIGHT tests `arg1` instead of `key`**
  (:334), so keyboard down/right navigation is dead (§30).

## Scrolling — the structural fact that shapes the whole roster design

- `MAX_CHARACTERS_DISPLAYED = 8`, `CHARACTER_SELECT_ROW_HEIGHT = 67`,
  `MAX_CHARACTERS_PER_REALM = 100`.
- **The XML defines 10 row buttons** (`CharSelectCharacterButton1..10`) **but only 8 are
  ever populated** — all loops are bounded by 8 (:464, :497, :509, :750). Buttons 9–10 sit
  below the 560 px viewport and are dead. There are also 3×10 paid-service buttons.
- **The row buttons are SIBLINGS of the scroll frame, not children of the scroll child.**
  Therefore `SetVerticalScroll` moves *nothing visually*; scrolling re-windows the fixed
  buttons over entries `scrollOffset+1 .. scrollOffset+8` (:574). The scroll child's height
  is grown by `maxOffset*67` (:493) purely so the scrollbar range is derived from content,
  with `scrollUpdating` (:266, :312) breaking the feedback loop.
- This is a **re-windowing virtual list**, i.e. exactly the §25 pooling model. I will keep
  it and generalise the index source, not replace it.

## Animation — a global driver already exists; extend it, do not add a second

- **No `AnimationGroup` / `CreateAnimationGroup`** in 3.3.5a (grep-confirmed).
- `GlueParent.lua` already hand-rolls fading: `GlueFrameFade` / `GlueFrameFadeIn` /
  `GlueFrameFadeOut` / `GlueFrameFadeUpdate`, a `FADEFRAMES` table, and
  **`GlueParent.xml:14-16` runs one shared `OnUpdate` → `GlueFrameFadeUpdate(elapsed)`**.
- **Consequence for §7:** the "one animation controller" the spec asks for **already
  exists**. `ECS_Anim` must *extend* `FADEFRAMES`/`GlueFrameFadeUpdate` rather than install
  a competing driver, otherwise two drivers fight over frame alpha.

## Persistence — confirmed absent in glue

Zero matches for `SavedVariables`, `RegisterSavedVariables`, `SetSavedVariable`,
`WriteFile`, `AppendToFile` across all deployed glue Lua. Everything is in-memory
(`selectedIndex`, `scrollOffset`, `RACE_NAME_CACHE`, …). Confirms the audit's conclusion:
**the cvar shard store is the only path** (see main audit §6).

## Portraits — the art to reuse already exists

No `SetPortraitTexture`, no per-row model, no race icons. Rows currently draw 2D atlas
slices of `uicharacterselectglues2x` plus a **60×60 faction badge** from
`FACTION_ICONS = { …\AllianceLogo, …\HordeLogo }` (:569-572).

**But 64×64 per-race male/female portraits already exist** — produced by earlier race work
as `Interface\Glues\CharacterCreate\UI-CharacterCreate-<Race><Male|Female>.blp`
(see `tools/derive_playable_race_portraits.py`). §4 can therefore use real per-race art
today, with a circular frame texture layered over it to get the §4 "near-circular"
appearance without any unstable masking hack.

## Faction model — only two factions exist in code

- `FACTION_ICONS` = Alliance / Horde only.
- `GetFactionForRaceName` **defaults unknown names to "Horde"** (:482, :510) and caches by
  name in `RACE_NAME_CACHE` which is **never invalidated** — a real hazard for custom races.
- `GetFactionForRaceID` falls through to `RACE_DATA` and defaults to "Alliance".
- `GlueParent.lua` hardcodes `allianceRaces` (13 ids) / `hordeRaces` (16 ids) sets,
  `CHARACTER_MODEL_LIGHT` (Alliance/Horde/DeathKnight only), and race-keyed fog/glow/
  ambience/light tables.
- **Freeborn is not a faction in these tables.** The existing mechanism is a client-side
  **name-hash badge**: `CharacterCreate.lua` hashes the chosen character name, stores it in
  cvars, and `CharacterFreeborn_ApplyBadges` matches row names against those hashes to swap
  in `Interface\Glues\CharacterSelect\FreebornLogo`. `characters.teamId` remains the only
  server-side truth.
- **Design consequence:** `ECS.FactionStyle` must treat Freeborn as a *third* style entry
  resolved via the existing name-hash mechanism, not via a TeamID, and must never default
  an unknown race to Horde/Alliance as the current code does — it must fall back to a
  neutral style (§14).

## Race/class tables and known bugs

- `RACE_DATA` (CharacterInfo:390-410) covers raceIDs 1–19, exported to `_G`.
- `ALLIANCE_RACES={1,2,3,4,5,6,7,16,18}`, `HORDE_RACES={8,9,10,11,12,13,14,15,17,19}`.
- `RaceTooltipPositions` covers only stock race IDs and falls back to CENTER for every
  custom race.
- **Latent bugs found** (relevant because the redesign touches these paths):
  1. `RACE_DATA[3].glueString = "NIGHT_ELF"` while every other table uses `"NIGHTELF"`,
     breaking `_G[baseKey.."_MALE"]` lookups in `GetFactionForRaceName`.
  2. `Races_Informations[14]` is assigned twice (:212 then :214) — the second wins.
  3. `RACE_NAME_CACHE` never invalidated.
  4. Buttons 9–10 unreachable.
  5. No double-enter guard.
  6. `OnKeyDown` down/right dead.

  Items 1–3 are exactly the kind of thing that makes a custom race render wrong, so the
  `ECS_Schema` layer will **bypass** `GetFactionForRaceName`/`RACE_DATA` rather than depend
  on them, and treat the existing tables as legacy.

## Load order

TOC line 19 = `CharacterSelect.xml` (which pulls `CharacterSelect.lua`); line 20 =
`CharacterInfo.lua`. So **CharacterInfo.lua loads after CharacterSelect.lua** — currently
safe only because all cross-references sit inside function bodies. New `ECS_*` modules
must obey the same rule: **no frame or cross-module access at file scope**.
