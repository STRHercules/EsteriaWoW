# Esteria Character Select — Implementation Audit (§1)

Conducted before any modification. Everything below is evidence-backed; anything I
could not confirm from files is marked **NOT CONFIRMED**.

---

## 1. Which files control Character Select

Resolved empirically by MPQ load order (later archive wins):

| File | Winning archive | Notes |
|---|---|---|
| `Interface\GlueXML\CharacterSelect.xml` | `enUS\patch-enUS-Z.MPQ` | 84 KB, heavily customised |
| `Interface\GlueXML\CharacterSelect.lua` | `enUS\patch-enUS-Z.MPQ` | 38 KB (~860 lines) |
| `Interface\GlueXML\CharacterInfo.lua` | `enUS\patch-enUS-Z.MPQ` | race/class info tables |
| `Interface\GlueXML\GlueParent.lua` | `enUS\patch-enUS-Z.MPQ` | glue root, backgrounds, camera |
| `Interface\GlueXML\GlueButtons.xml` | `patch-A.MPQ` | button templates |
| `Interface\GlueXML\GlueTemplates.xml` | `patch-A.MPQ` | checkbox/slider/scroll templates |
| `Interface\GlueXML\GlueFontStyles.xml` | `enUS\patch-enUS-2.MPQ` | text colours |
| `Interface\GlueXML\GlueXML.toc` | `enUS\patch-enUS-Z.MPQ` | load order |

**Load order is explicit and extensible.** `GlueXML.toc` contains a literal
`## add new files after here` marker (line 6) and `## This Always Runs Last, Add New
Items above it.` (line 37). `CharacterSelect.xml` loads at line 19 and pulls in its
own Lua via `<Script file="CharacterSelect.lua"/>`. This is the sanctioned hook for
splitting new modules in (§36).

`CharacterCreate.xml` loads at line 21, i.e. **after** CharacterSelect — already relied
on by existing code (see the load-order warning at `CharacterCreate.lua:1846`).

## 2. Has it already been customised?

**Yes, extensively. Do not treat this as stock Blizzard GlueXML.**

- `CharacterSelect.xml:1` — `<!-- Autora: Noa -->` → the client runs a modified
  **retail-interface fork**, not Blizzard's originals.
- `patch-A.MPQ` carries a custom glue art set (`Interface\GLUES\CHARACTERCREATE\*`,
  `Interface\GLUES\Common\*`, `Interface\GLUES\CharacterSelect\*`).
- Esteria custom races, Freeborn support and per-race art are layered on top in
  `patch-C.MPQ`, `patch-Y.MPQ`, `patch-Z.MPQ`, `patch-enUS-Z.MPQ`.
- Live backups of prior edits exist inside the archive itself:
  `AccountLogin.lua.before-framelevel-20260904.bak`, `.before-logo-675-…`,
  `.before-logo-center-…`, `.pre-warwithin.bak`.

## 3. Client patches / DLL hooks affecting character selection

- **Client EXE is patched** — see §4.
- **`WarcraftXL.dll`** with a full symbol map at `G:\3.3.5a - Dev\wxl-symbols.json`
  (15 KB, ~400 named addresses: `M2.CharInit`, `M2.CharAddItemBySlot`,
  `WorldMap.EnterWorld`, `Scene.*`, `Wmo.*`, `Weather.*`). This is the engine-level
  modding surface. Anything requiring camera or model work beyond GlueXML belongs
  here, isolated and documented (§28).
- Also present: `wxl-hub.exe`, `wxl-patcher.exe`, `Scan.dll`, `db.cfg`-style install
  manifests (`ClasslessWildcard-install.json`).

## 4. Character count currently supported — **already 100**

`100-character-support` is implemented at all three layers:

- **Server**: `CONFIG_CHARACTERS_PER_ACCOUNT` / `CONFIG_CHARACTERS_PER_REALM`,
  set to `100` (`src/server/game/World/WorldConfig.cpp`, `worldserver.conf*`).
- **Client EXE**: one limit byte at offset `0x6404C`, validated as `80 7D FF 64`
  (was `… FF 0A` = 10).
- **Glue**: `CharacterSelect.lua:10` — `MAX_CHARACTERS_PER_REALM = 100;`

## 5. How scrolling is currently implemented — **already actual-index**

**This is the most important finding. Large-roster scrolling already exists and works.**

```
CharacterSelect.lua:9    MAX_CHARACTERS_DISPLAYED = 8;
CharacterSelect.lua:22   self.scrollOffset = 0;
CharacterSelect.lua:253  CharacterSelect_ClampScrollOffset(offset)
CharacterSelect.lua:264  CharacterSelect_ApplyScrollOffset()
CharacterSelect.lua:294  CharacterSelect_SetScrollOffset(offset)
CharacterSelect.lua:311  CharacterSelect_OnVerticalScroll(self, offset)
CharacterSelect.lua:574  for actualIndex = scrollOffset+1, min(numChars, scrollOffset+MAX_CHARACTERS_DISPLAYED)
CharacterSelect.lua:752  button:SetID((CharacterSelect.scrollOffset or 0) + i);
CharacterSelect.lua:478  local maxOffset = math.max(numChars - MAX_CHARACTERS_DISPLAYED, 0);
```

So the architecture is **already the one the spec asks for**:

- a fixed pool of **8 reusable row frames** (§25 frame pooling — exists),
- a `scrollOffset` mapping viewport position → **real character index**,
- rows carry the **real index** via `SetID(scrollOffset + i)`,
- clamping, wheel handling and a native scrollbar (`SetVerticalScroll`) wired up.

**Consequence for the redesign:** I must extend this indirection, not replace it. Today
`viewportRow → realIndex` is a simple additive offset. Search + custom order turn that
into an arbitrary permutation, so the correct generalisation is an explicit
`visualOrder[]` array consumed by the existing pool, keeping `SetID` carrying the real
index. That preserves every existing action while making the mapping total (§24).

## 6. Persistent storage from GlueXML — **solved, with prior art**

There are **no `SavedVariables` in glue** (glue runs before addons). But a previous
agent already solved restart-surviving persistence and documented it at
`CharacterCreate.lua:1858-1930`. Their findings, verbatim in spirit:

> 1. `GetCVar`/`SetCVar` raise *"Couldn't find CVar named `<x>`"* for any name the client
>    does not already know. Never call either outside `pcall` — an uncaught glue error
>    here takes the screen down and can crash the client.
> 2. An argument is evaluated BEFORE `pcall` is entered.
> 3. **Only names the engine registers at the login screen are writable.** Being present
>    in `Config.wtf` does not imply `SetCVar` accepts it, and integer cvars are
>    **normalised on load** (`readTOS`/`readEULA` became `"1"`; `gameTip` was clipped to a
>    valid index — the value was on disk but not what the client loaded).

**The proven store**: *string* cvars the client never parses. The live implementation
uses `Sound_VoiceChatInputDriverName` / `Sound_VoiceChatOutputDriverName` — voice-chat
device names, inert because voice chat does not exist in 3.3.5.

Working pattern (`CharacterCreate.lua:2145-2210`):

```lua
CharacterFreeborn_SafeSet(cvar, CharacterFreeborn_BadgeMarker .. table.concat(list, ",") .. "|" .. original);
local check = CharacterFreeborn_SafeGet(cvar);   -- read-back verification
```

i.e. marker prefix + delimited payload + **preservation of the cvar's original value** +
**read-back confirmation**. This survives client restart and is read on the character-select
screen at the start of the next session.

**Design decision for this project:** a `CharacterPersistence` module that **probes a
candidate cvar pool at runtime** (write-marked value, read back, keep the ones that
stick) and **shards** the record across however many it finds. This gives capacity beyond
the two known-good cvars and degrades gracefully. Backed by an optional in-world addon
mirror (the existing `FreebornClaim` pattern: glue carries via cvar → addon persists to
`SavedVariables` on login), which also provides unbounded note text.

## 7-10. Race / class / faction / Freeborn IDs

Delegated to a parallel repository audit; recorded in `character-select-redesign.AUDIT-IDS.md`
once complete. **Not guessed here.**

## 11. Existing custom texture directories and conventions

Inventory only — these are already referenced by the winning XML and must be reused (§26):

- `Interface\Glues\CharacterSelect\` — 24 entries incl. `uicharacterselectglues2x`
  (2048×2048 background atlas), `128redbuttonpart2` (1024×512 button atlas),
  `FreebornLogo.blp`, `Glue-CharacterSelect-Highlight`
- `Interface\Glues\CharacterCreate\` — race/gender/class button art, `charactercreate.blp`
  (5.5 MB), `UI-RotationRight-Big-{Up,Down}`, `CharacterCreate-LabelFrame`
- `Interface\Glues\Common\` — `generic.blp`, `Arrow.blp`, `perks.blp`, button set
- `Interface\<Category>\<Name>.blp` — stock-style naming, DXT-compressed BLP2

## 12. Extra character info beyond stock 3.3.5a

Delegated (see §7-10). Stock 3.3.5a `GetCharacterList()` entries are known to carry name,
level, race, class, sex, zone, guild and flags; whether this fork adds fields is pending.

## 13. Reusable UI helper libraries

**None exist in glue.** There is no shared glue library, no animation framework and no
modal framework — `AnimationGroup` is not available in 3.3.5a. Every existing screen
hand-rolls its own `OnUpdate`.

However, two **reusable patterns** do exist and should be lifted rather than reinvented:

- the **safe-cvar helpers** (`CharacterFreeborn_SafeGet/SafeSet`, `CharacterCreate.lua:1909`)
- the **load-order discipline**: never touch a frame at file scope, because the XML
  creates frames *after* the Lua executes (`CharacterCreate.lua:1846-1852`)

## Deployment mechanism

The repo already has a sanctioned, manifest-driven client patch toolchain — use it, not
ad-hoc scripts:

```
modules/mod-classless-wildcard/client-patch/
    install.py            manifest-driven installer
    lib/mpq.py            pure-Python MPQ  (MPQArchive read, write_archive write)
    lib/blp.py            BLP codec
    lib/clientfs.py       client file system
    lib/charcreate.py     character-create patching
    lib/exepatch.py       EXE patching
```

## Visual language

Already established by the preceding ElvUI glue work (see
`../elvui-glue-reskin/elvui-glue-reskin.PLAN.md`): `Interface\BUTTONS\WHITE8X8` as the
single flat texel, `backdropfadecolor 0.06,0.06,0.06 @ alpha 0.80`, a hard 1 px
`bordercolor 0,0,0` rim, accent `#FD7A2B`, text `#E5E3E3`. **Square corners, translucent,
no bevel.** The roster should be built from this same vocabulary.

---

## Risks and constraints discovered

1. **The screen is already heavily customised.** A rewrite that ignores the existing
   `scrollOffset` / `SetID` architecture and the retail-interface fork will regress 100-char
   support, custom races and Freeborn. Extend, don't replace.
2. **Glue errors can crash the client.** All cvar access must go through `pcall`
   (documented crash risk, `CharacterCreate.lua:1860`).
3. **No animation primitives.** A lightweight single-controller animation framework is
   required (§7); dozens of permanent `OnUpdate` handlers are a real performance risk.
4. **Frame access at file scope is fatal.** Load-order discipline is mandatory.
5. **The client was running** during this audit, locking the MPQs. All writes must happen
   with the client closed (the existing installer already enforces this).
