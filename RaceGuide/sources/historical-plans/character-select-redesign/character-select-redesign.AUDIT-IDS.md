# Character Select — ID & System Inventory (audit companion)

Consolidated from a read-only repository audit. These are the authoritative
sources; plan documents in `.agents/plans/` are **stale** in places (noted below).

> **Note:** `.agents/plans/**` is gitignored, so ripgrep-based search silently
> returns nothing there. Use `Select-String` or direct file reads in that tree.

## Authoritative sources

| What | Where |
|---|---|
| Client race rows | `G:\3.3.5a - Dev\Data\patch-Z.MPQ` → `DBFilesClient\ChrRaces.dbc` (32 rows) |
| Server race truth | `modules/mod-custom-server/data/sql/db-world/updates/dbc/chrraces_dbc.sql` + migrations for race 14 and 43/44 |
| Machine registry | `modules/mod-custom-server/data/races/race_registry.json` |
| C++ enum | `src/server/shared/SharedDefines.h:70-100` |
| Enum contract test | `tools/test_playable_race_contract.py` (EXPECTED_RACE_MAP, lines 18-33) |

## Race ids (real id space — reaches **44**)

1-11 stock · 12 Worgen(A) · 13 HighElf(A) · **14 Broken(H)** · 15 Sethrak(H) · 16 Eredar(H)
· 17 Nightborne(H) · 18 Pandaren(A) · 19 VoidElf(A) · 20 Vulpera(H) · 21 LightforgedDraenei(A)
· 22 ZandalariTroll(H) · 23 DarkIronDwarf(A) · 24 Broken(A) · 25 Forsaken(A) · 26 Pandaren(H)
· **27 Broken(H) — server only, no client row** · 28 Dracthyr(H) · 32-42 NPC-only (playability=0)
· **43 Darkfallen(A)** · **44 Darkfallen(H)**

All are male+female; there is **no single-gender race**.

**Race 14 was repurposed** from Mag'har Orc to Broken by the 2026-09-17 migration — the
base SQL still says "Maghar Orc". Race 14 also appears in `CharacterCreate.lua` lore as a
double-assigned `Races_Informations[14]`.

**Unresolved drift (needs a product decision, not a code fix):**
client rows 24/25/26 are stale vs server SQL (client 24=FelOrc, 25=Broken; server
24=Broken(A), 25=Forsaken(A), 26=Pandaren(H)); and client-only races 29/30/31 (KulTiran,
Illidari) have **no server registration**.

## Limits

| Layer | Value | Where |
|---|---|---|
| Characters per realm/account | **100** | `WorldConfig.cpp:230` (`value > 0 && value <= 100`), `worldserver.conf:2021,2029` |
| Client EXE char byte | `0x6404F` = `0x64` | verified bytes `80 7D FF 64` at `0x6404C` |
| Glue displayed rows | 8 | `CharacterSelect.lua:9` |
| Glue max per realm | 100 | `CharacterSelect.lua:10` |
| Client `MAX_RACES` | **40** | `CharacterCreate.lua:5`; XML defines 40 race buttons |
| Runtime race table | 32 → **64** | `Extensions\races-64-esteria\races-64-esteria.dll` (**already deployed**; the plan doc's checkboxes are stale) |
| Server race limit | **no `MAX_RACES` constant** | real limit is the 32-bit race mask, `SharedDefines.h:110`, with `DARKFALLEN_RACE_MASK = 0x80000000u` reused for 43/44 |
| Classes | 10 rows, ids 1-9 + 11 (no Monk) | `MAX_CLASSES 12`, `SharedDefines.h:162` |

**No custom classes exist.** The realm uses a *classless* system: `mod-classless-wildcard`
reuses the **Paladin chassis (class 2)** and presents it as "Hero".

## Factions / teams

`SharedDefines.h:770-773` — `TEAM_ALLIANCE=0`, `TEAM_HORDE=1`, `TEAM_NEUTRAL=2`,
**`TEAM_FREEBORN=3`**.

## Freeborn = a persistent TEAM, **not a race**

- Stored per character in `characters.teamId = 3`; claimed via
  `src/server/game/Server/FreebornClaim.h`, addon `FreebornClaim` sends `"team\t3"`.
- Faction data: `FREEBORN_TEMPLATE_ID=2237`, `FREEBORN_FACTION_ID=893`.
- **All 95 client references live in `CharacterCreate.lua`.** `CharacterSelect.lua` and
  `GlueParent.lua` contain **zero**. That file boundary must be respected.

## Character-select reality check (live `CharacterSelect.lua`, 1124 lines)

- Virtual scroll already works: `SetScrollOffset` :294, `ScrollBy` :305,
  `OnVerticalScroll` :311, child height `viewportHeight + maxOffset*ROW_HEIGHT` :493,
  `maxOffset = max(numChars - 8, 0)` :478.
- Row mapping: `:574` loop over `scrollOffset+1 .. min(numChars, scrollOffset+8)`;
  `:575` reads exactly **10** return values from `GetCharacterInfo`;
  `:577`/`:730` store `button:SetID(actualIndex)`.
- Already displayed: name, level, race, class, zone, Alive/Dead, class colour
  (`CLASS_COLORS` :540), faction icon (`FACTION_ICONS` :569).
- **No portraits** in this file; **no ordering/sorting anywhere** (server order only).

## THE HAZARD — ordinal space vs real id space

`CharacterCreate.lua:986` does `local raceID = index;` and passes an **enumeration
ordinal** into `GetFactionForRace`. `CharacterInfo.lua`'s `RACE_DATA` (slots 1-19),
`ALLIANCE_RACES={1,2,3,4,5,6,7,16,18}` and `HORDE_RACES={8,9,10,11,12,13,14,15,17,19}` are
a **parallel ordinal table, deliberately not ChrRaces ids. Do not "correct" them.**

`RACE_DATA[n]` is therefore only coincidentally right for stock ids 1-11, where ordinal
== real id. This is precisely why the existing `GetFactionForRaceName` defaults unknown
races to "Horde".

**ECS therefore resolves race from the background MODEL FILE STRING** via
`GetSelectBackgroundModel(index)` — the same signal the existing custom faction override at
`CharacterSelect.lua:586-594` already trusts. `RACE_DATA` is consulted numerically only for
ids 1-11 and the result is tagged `source = "ordinal-fallback"` so callers know it is
low-confidence.

## Existing contracts that must not break

1. **`tools/test_character_select_contract.py`** pins, in `CharacterSelect.lua`:
   - `CharacterSelect_OnKeyDown(self,key)` must contain
     `elseif ( key == "DOWN" or key == "RIGHT" )` and must **not** contain `arg1`
   - `UpdateCharacterList()` must contain the exact scroll-child height expression and
     `CharacterSelectCharacterScrollFrame:UpdateScrollChildRect()`
   - `CharacterSelect_OnVerticalScroll` must contain `GlueScrollFrame_OnVerticalScroll(self, offset)`
     and `CharacterSelect_SetScrollOffset(offset / CHARACTER_SELECT_ROW_HEIGHT)`
   - XML: scroll frame `256x560` with a `CharacterSelectCharacterScrollChild`

   **This test is currently RED** (`arg1` is present in the deployed file) and it cannot run
   in this checkout at all, because it reads `ROOT / "3.3.5a - Dev"` while the client lives on
   `G:` — the same defect affects `tools/test_character_limit_contract.py`.

2. **`CharacterFreeborn_ApplyBadges`** (`CharacterCreate.lua:2216`) **wraps
   `UpdateCharacterList`** and expects:
   - row buttons named `CharSelectCharacterButton1..N`
   - a child texture `…FactionIcon` on each row
   - `button:GetID()` to keep returning the **real** character index
   - it re-anchors the badge to `button TOPLEFT + (200,-35)` at 44×44

   A roster rewrite must therefore keep the row names, keep `FactionIcon` alive, and keep
   `GetID()` meaning the real index. ECS reuses Freeborn membership via
   `CharacterFreeborn_BadgeHashes` / `CharacterFreeborn_RecordFor` rather than
   reimplementing the cvar store.

## Tools worth reusing

`tools/playable_race_pack.py`, `tools/darkfallen_race_pack.py`, `tools/race_portrait_pack.py`,
`tools/derive_playable_race_portraits.py`, `tools/freeborn_faction_pack.py`,
`tools/freeborn_team_pack.py`, `tools/check_glue_race_tables.py`, `tools/wow_xref.py`,
and the MPQ/WDBC/BLP library at
`modules/mod-classless-wildcard/client-patch/lib/{mpq,dbc,charcreate,gluestrings,blp}.py`.
