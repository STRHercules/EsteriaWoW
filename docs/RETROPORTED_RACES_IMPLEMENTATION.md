# Esteria Retroported Race Implementation Plan

## Purpose

This document is the implementation contract for adding the six races already retroported under `G:\RetroPorterWork` into the existing Esteria 3.3.5a client and AzerothCore server.

Target races:

1. Mag'har Orc
2. Highmountain Tauren
3. Mechagnome
4. Earthen
5. Haranir
6. Skyborne

The source assets are already converted to Wrath-compatible M2/SKIN/ANIM/BLP payloads. Do **not** redo the Retail/Forever extraction unless a source asset is proven missing or corrupt. Work from the canonical patch roots in `G:\RetroPorterWork`.

This is not a generic custom-race guide. It is written for the current Esteria stack:

- repository: `R:\Users\Zach\Documents\GitHub\EsteriaWoW`
- dev client: `G:\3.3.5a - Dev`
- server: local Docker Compose stack from this repository
- active client high-priority archives: `Data\patch-Z.MPQ` and `Data\enUS\patch-enUS-Z.MPQ`
- active native extension: `G:\3.3.5a - Dev\Extensions\races-64-esteria\races-64-esteria.dll`
- active runtime log confirms `races-64-esteria` is loaded
- client build: 3.3.5a build 12340
- race configuration registry: `modules/mod-custom-server/data/races/race_registry.json`
- existing race/client pack tooling: `tools/playable_race_pack.py`, `tools/darkfallen_race_pack.py`, `tools/race_portrait_pack.py`
- server DBC loader supports continuations through `modules/mod-wxl-dbc`, but retroported playable-race identity/model/appearance data must use full standard `.dbc` files
- existing custom-race module/data: `modules/mod-custom-server`, `modules/mod-worgoblin-high-elf`

The local AzerothCore containers were stopped when this plan was written. Do not infer live DB state from repository SQL alone. Bring the Docker stack up only during the validation stages described below.

---

# 1. Non-negotiable rules

Codex must follow these rules throughout the implementation.

1. **Implement one race at a time.** Do not add all DBC rows first and debug six races simultaneously.
2. **Mag'har is the pilot race.** No second race starts until Mag'har passes the complete acceptance gate.
3. **Never replace the current Z archives with donor archives.** Merge into the existing live `patch-Z.MPQ` / `patch-enUS-Z.MPQ` contract.
4. **Back up both Z archives before every install.** Hash them before and after.
5. **Use the effective live DBCs as the merge base.** The current winning DBCs are in Z, not clean stock 3.3.5a files.
6. **Keep server and client DBC rows generated from one manifest and one full-DBC build.** The exact generated `.dbc` bytes used by the client must be mounted into the server's normal `data/dbc` path for tables the server consumes. Never hand-maintain two different copies of a race row.
7. **Do not use `.dbc1-*` continuations for retroported playable-race identity, player models, player displays, appearance, barber, outfits or racial spells.** Existing unrelated continuation-backed systems such as Freeborn/Battlemon may remain as-is.
8. **Player `CreatureDisplayInfo` IDs must be <= 65535.** AzerothCore stores `PlayerInfo::displayId_m/f` as `uint16`. A higher ID silently wraps to another display and can render the wrong creature/player model.
9. **Every converted player M2 must pass dependency closure before packaging.** Resolve its embedded/hard BLP references (including modern TXID-derived references) and prove every referenced texture exists in the final global patch.
10. **Do not overwrite existing race IDs 1-44.** IDs 32-42 remain reserved NPC race IDs. Darkfallen owns 43/44.
11. **Do not assign new 32-bit race-mask bits.** There are none left.
12. **Do not put Blizzard-derived converted binaries in Git.** The repository stores manifests, generators, tests, SQL and docs only. Generated client payload stays outside Git under `G:\RetroPorterWork` and staging folders.
13. **Do not point DBC model paths back at stock race paths.** Always point at the converted namespace `custom\<race>\...` so these races cannot overwrite Orc, Tauren, Gnome, Dwarf, Night Elf or Blood Elf art.
14. **Do not modify `G:\RetroPorterWork` source outputs in place except by rerunning/fixing RetroPorter itself.** If Esteria-specific geometry must be baked or altered, write a derived artifact tree such as `G:\RetroPorterWork\<race>\integration\patch-root`.
15. **A race is not complete because character creation renders it.** It must pass login, relog, armor, helmet, barber, mount, death, combat, emote, faction, Freeborn, class and PlayerBots smoke tests.

---

# 2. Current client/server reality

## 2.1 Client race capacity is already extended

The installed client has:

```text
G:\3.3.5a - Dev\Extensions\races-64-esteria\races-64-esteria.dll
```

Its README states that it expands the runtime race tables to **64 race IDs** without patching `Wow.exe` on disk. The WarcraftXL log confirms it loads successfully.

Therefore RaceIDs above 44 are valid implementation targets. The new races do **not** require another executable patch just to exist.

The current winning `CharacterCreate.lua` in `patch-enUS-Z.MPQ` uses:

```lua
MAX_RACES = 40;
```

The live character-creation XML currently contains race buttons through 40. Adding the full dual-faction versions below raises the visible playable-race count beyond 40. The Glue layer must therefore be expanded to at least 42 entries. Set the implementation ceiling to **64** so it matches the native race extension and does not need another rewrite later.

## 2.2 Existing race IDs

The winning live `ChrRaces.dbc` currently contains normal/custom rows through 31 plus Darkfallen 43/44. IDs 32-42 are reserved for NPC races in Esteria's registry.

Do not reuse them.

## 2.3 32-bit race masks are exhausted

Current server code contains:

```cpp
if (race >= RACE_HUMAN && race <= 32)
    return 1u << (race - 1);
```

Darkfallen 43/44 already share the special `0x80000000` mask.

There is no unique 32-bit bit remaining for six or nine new playable race rows. A correct implementation must separate:

- **exact RaceID**: who the race actually is
- **legacy compatibility mask**: which old 3.3.5a race bit should be used for legacy quests/items/conditions
- **visual base race**: which existing race supplies compatible legacy character rules when necessary
- **faction/team**: Alliance/Horde/Freeborn behavior

Do not attempt a 64-bit conversion of every WotLK DBC RaceMask field. Those DBC formats are 32-bit and the client expects them that way.

## 2.4 Current client patch precedence

For character data the effective custom layer is:

```text
Data\patch-Z.MPQ
Data\enUS\patch-enUS-Z.MPQ
```

Both currently carry overlapping character DBC/Glue content, and the locale Z archive can shadow global Z entries. When a race changes a DBC or Glue file, generate the same authoritative version into both Z archives unless a file is intentionally global-only.

Assets such as M2/SKIN/ANIM/BLP belong in global `patch-Z.MPQ` only.

Before modifying the live client, always stage and validate an archive copy first.

---

# 3. Permanent RaceID allocation

Use this Esteria allocation unless a collision is discovered before implementation begins:

| Esteria ID | Race row | Faction | Visual base | Legacy compatibility mask owner |
| ---: | --- | --- | --- | --- |
| 45 | Mag'har Orc | Horde | Orc | Orc (2) |
| 46 | Highmountain Tauren | Horde | Tauren | Tauren (6) |
| 47 | Mechagnome | Alliance | Gnome | Gnome (7) |
| 48 | Earthen | Alliance | Dwarf | Dwarf (3) |
| 49 | Earthen | Horde | Dwarf | Orc (2) |
| 50 | Haranir | Alliance | Night Elf | Night Elf (4) |
| 51 | Haranir | Horde | Night Elf | Troll (8) |
| 52 | High Order Skyborne | Alliance | Blood Elf-like | High Elf (13) |
| 53 | Windshaper Skyborne | Horde | Blood Elf-like | Blood Elf (10) |

Why nine rows for six visual races:

- Retail Earthen has paired faction rows.
- Retail Haranir has paired faction rows.
- Forever Skyborne has High Order and Windshaper faction rows.
- Esteria already has precedent for one visual species backed by paired RaceIDs (`Pandaren`, `Broken`, `Darkfallen`).

Add these pairs to `race_registry.json`:

```text
earthen:   Alliance 48 / Horde 49
haranir:   Alliance 50 / Horde 51
skyborne:  Alliance 52 / Horde 53
```

Do not use Retail/Forever RaceIDs 36, 28, 37, 84/85, 86/91 or 95/96 as Esteria IDs.

---

# 4. Add a real extended-race compatibility layer first

This is Phase 0 and must be completed before Mag'har.

## 4.1 Extend server race enums

Update at minimum:

```text
src/server/shared/SharedDefines.h
src/server/shared/enuminfo_SharedDefines.cpp
```

Add constants 45-53. Keep the old values unchanged.

Do not increase the normal bit-shift range beyond 32.

## 4.2 Introduce explicit race compatibility metadata

Add a small constexpr/data-driven profile for custom RaceIDs. It should expose at least:

```text
raceId
speciesKey
legacyMaskRaceId
visualBaseRaceId
faction
pairedRaceId (optional)
```

Recommended API shape:

```cpp
bool IsExtendedPlayableRace(uint32 raceId);
uint32 GetLegacyRaceMaskForRace(uint32 raceId);
uint8 GetVisualBaseRaceForRace(uint32 raceId);
```

`GetRaceMaskForRace()` may delegate to `GetLegacyRaceMaskForRace()` for these new IDs, but the distinction must be explicit in code and tests.

Expected legacy mask aliases:

```text
45 -> Orc bit
46 -> Tauren bit
47 -> Gnome bit
48 -> Dwarf bit
49 -> Orc bit
50 -> Night Elf bit
51 -> Troll bit
52 -> High Elf bit
53 -> Blood Elf bit
```

Never map an Alliance and Horde version of the same new species to the same legacy bit. That would contaminate `RaceMgr::_allianceRaceMask` and `_hordeRaceMask`.

## 4.3 Prevent mask aliases from granting the wrong racials

A legacy-mask alias is for old content compatibility. It must **not** mean:

```text
Mag'har automatically receives every Orc racial row
Earthen Horde automatically receives Orc racials
Haranir Horde automatically receives Troll racials
Skyborne Alliance automatically receives all High Elf exact-race behavior
```

The current `playercreateinfo_skills` and `playercreateinfo_spell_custom` paths are mask-based. For RaceIDs 45-53, stop treating those mask rows as authoritative exact-race start data.

Implement exact-race startup data owned by `mod-custom-server`, for example:

```text
custom_race_start_skill
  raceId
  classMask
  skill
  rank
  comment

custom_race_start_spell
  raceId
  classMask
  spell
  note
```

Load these for extended races after the normal player-info structures are allocated. Copy generic class skills from the chosen host profile, then explicitly add each race's languages and racials.

Alternative implementation is acceptable only if it provides the same exact-RaceID separation and has tests proving host racials do not leak.

## 4.4 Audit race-mask call sites

At minimum inspect all callers found under:

```text
ObjectMgr.cpp
RaceMgr.cpp
AchievementMgr.cpp
ConditionMgr.cpp
ServerMailMgr.cpp
Unit.h / Unit.cpp
CharacterHandler.cpp
Player.cpp
mod-playerbots
```

Classify each use as one of:

- exact-race identity
- broad legacy content compatibility
- faction/team membership

Use exact RaceID for identity, compatibility mask for old quest/item/condition data, and `ChrRaces`/RaceMgr faction state for team membership.

## 4.5 Add contract tests before adding race assets

Create a test such as:

```text
tools/test_retroported_race_contract.py
```

It must assert:

- IDs 45-53 are unique.
- NPC IDs 32-42 are untouched.
- Darkfallen 43/44 remain untouched.
- each new ID resolves a nonzero compatibility mask.
- Alliance/Horde paired rows do not share one bit across opposing factions.
- `RaceMgr` can size storage to at least 54 entries.
- exact-race startup data does not grant host-only racials.

Do not proceed until these tests pass.

---

# 5. Build one generator for all six races

Do not write one-off scripts for every race.

Create a project tool, recommended path:

```text
tools/retroported_race_pack.py
```

Use existing code from these tools rather than reimplementing StormLib/WDBC support:

```text
tools/playable_race_pack.py
tools/darkfallen_race_pack.py
tools/race_portrait_pack.py
tools/cars_mount_pack.py
```

The tool must support:

```powershell
python tools/retroported_race_pack.py plan --race maghar
python tools/retroported_race_pack.py build --race maghar
python tools/retroported_race_pack.py validate --race maghar
python tools/retroported_race_pack.py install --race maghar
```

`install` must never be the only way to test. `plan/build/validate` operate on staging first.

## 5.1 Generator inputs

Create a repository manifest directory, for example:

```text
data/retroported-races/
  allocation.json
  maghar.json
  highmountain.json
  mechagnome.json
  earthen.json
  haranir.json
  skyborne.json
```

Each race manifest should contain:

```text
Esteria RaceID(s)
source patch root
client file string
name
faction
visual base race
legacy mask race
male model path
female model path
optional collection models
skin mapping
face mapping
hair mapping
hair-color mapping
facial-feature/preset mapping
barber mapping
class list
start profile
languages
racial spells
totem/druid-form fallback profile
portrait/background keys
```

## 5.2 Effective DBC merge base

The generator must read the winning tables from the **live/staged Z archives**, not `DBCs/` and not clean stock files.

Read at minimum:

```text
ChrRaces.dbc
CreatureModelData.dbc
CreatureDisplayInfo.dbc
CreatureDisplayInfoExtra.dbc
CharSections.dbc
CharHairGeosets.dbc
CharHairTextures.dbc
CharacterFacialHairStyles.dbc
BarberShopStyle.dbc
CharBaseInfo.dbc
CharStartOutfit.dbc
NameGen.dbc
HelmetGeosetVisData.dbc
VocalUISounds.dbc
EmotesTextSound.dbc
SkillLineAbility.dbc
SkillRaceClassInfo.dbc
```

Use `tools/audit_effective_character_dbcs.py` as precedent for reading effective archives.

## 5.3 ID allocation manifest

Do not scatter new DBC IDs through Python.

Maintain an allocation file with reserved ranges for:

```text
CreatureModelData
CreatureDisplayInfo
CreatureDisplayInfoExtra
CharSections
CharHairGeosets
CharacterFacialHairStyles
BarberShopStyle
CharStartOutfit
NameGen
```

Before build, scan both live Z DBCs and server `*_dbc` SQL tables when available. Abort on collision.

Do not assume the next integer is safe.

## 5.4 Client archive staging

For every build:

1. hash live `patch-Z.MPQ` and `patch-enUS-Z.MPQ`;
2. copy them to a timestamped staging/backup directory;
3. merge race assets into staged global Z;
4. merge generated DBCs into staged global Z;
5. merge the exact same generated character DBCs into staged locale Z;
6. patch Glue in both archives when that file exists in both;
7. enumerate/read back every inserted entry;
8. reopen every generated WDBC and validate header/row counts/string offsets;
9. only then permit `install`.

Keep the final global patch below the classic MPQ size ceiling. Existing tools already contain MPQ size validation code; reuse it.

---

# 6. Extend the existing CharacterCreate and CharacterSelect screens

This phase is **additive only**. Codex must extend Esteria's current character-create and character-select screens. It must not replace them with stock GlueXML, donor GlueXML, Retail/Forever GlueXML, an older Worgoblin screen, or a newly invented parallel screen.

The current Esteria screens already contain substantial project-specific behavior that must survive unchanged:

- the current CharacterCreate visual layout, tooltips, race/class panels and gender controls;
- the Freeborn creation control and its wrappers;
- the current race icons and custom race information;
- the current CharacterSelect/ECS roster layout;
- the 100-character scrolling/select behavior;
- faction badges and Freeborn badges;
- existing Darkfallen special handling until it is generalized;
- current background, lighting, fog and ambience behavior;
- all currently working races and their ordering.

**Do not solve this task by dropping in complete replacement copies of `CharacterCreate.lua`, `CharacterCreate.xml`, `CharacterSelect.lua`, `CharacterSelect.xml`, `CharacterInfo.lua`, `GlueParent.lua`, or `GlueStrings.lua`.** Patch the live winning files surgically and retain all unrelated code.

The winning Glue currently comes from the Z layer. Audit both copies before every change:

```text
G:\3.3.5a - Dev\Data\patch-Z.MPQ
G:\3.3.5a - Dev\Data\enUS\patch-enUS-Z.MPQ
```

At the time this document was written, the effective copy resolves from `patch-enUS-Z.MPQ`. If both archives carry a changed Glue file, keep both copies coherent.

The relevant existing files are:

```text
Interface\GlueXML\CharacterCreate.lua
Interface\GlueXML\CharacterCreate.xml
Interface\GlueXML\CharacterInfo.lua
Interface\GlueXML\GlueParent.lua
Interface\GlueXML\GlueStrings.lua
Interface\GlueXML\CharacterSelect.lua
Interface\GlueXML\CharacterSelect.xml
Interface\GlueXML\GlueXML.toc
```

## 6.1 Preserve the current screen and add capacity

The live `CharacterCreate.lua` currently declares:

```lua
MAX_RACES = 40;
```

and the live `CharacterCreate.xml` currently declares static buttons:

```text
CharacterCreateRaceButton1
...
CharacterCreateRaceButton40
```

using the existing `CharacterCreateRaceButtonTemplate`.

Extend this exact system to support the new entries. Either:

1. add `CharacterCreateRaceButton41` through `CharacterCreateRaceButton64` using the **same existing template**, or
2. minimally refactor the current container so it creates additional buttons from that same template at runtime.

Do not redesign the screen as part of the race port.

Set `MAX_RACES = 64` so the Glue capacity matches the installed `races-64-esteria` runtime extension. The extra buttons are capacity, not an instruction to show 64 races simultaneously. Preserve the current positioning code and extend its existing wrapping/scrolling/paging behavior as needed.

Existing race order must remain stable unless a separate UI task explicitly changes it. Append the new races to the project-owned presentation order rather than sorting every race numerically and reshuffling the current screen.

## 6.2 Separate UI button slot from actual RaceID

This is required before RaceIDs 45-53 can be considered correctly implemented.

The live Glue still contains ordinal assumptions. In particular, the current `CharacterCreateEnumerateRaces(...)` does the equivalent of:

```lua
local raceID = index;
button = _G["CharacterCreateRaceButton"..index];
button.raceFileString = fileString;
```

and the XML template currently calls:

```lua
CharacterRace_OnClick(self, self:GetID());
```

`SetCharacterRace(id)` also checks a button with logic equivalent to `if i == id`.

That must **not** be carried forward for high/non-contiguous RaceIDs. The XML button ID is a UI slot. It is not the authoritative character RaceID.

Extend the existing code so every visible race button carries both values:

```lua
button.uiSlot = index
button.raceID = actualRaceID
button.raceFileString = fileString
```

The stock 3.3.5a selection functions still operate on the **enumeration/UI slot**, so do not pass RaceID 45 directly to `SetSelectedRace`. Keep the existing slot-based selection call intact and carry the exact RaceID beside it.

Use the two values deliberately:

```text
button.uiSlot / button:GetID()
    SetSelectedRace
    GetSelectedRace comparisons
    locating/positioning the button
    stock class-selection flow that expects the enumeration slot

button.raceID
    project-owned faction lookup
    race tooltip metadata
    Freeborn exact-race state
    exact-race diagnostics/tests
    mapping the selected slot back to the RaceID saved/sent by the native client
```

Recommended helpers inside the existing Glue, not a new screen:

```lua
CharacterCreate_GetRaceIDForButton(button)
CharacterCreate_GetRaceIDForSlot(uiSlot)
CharacterCreate_GetButtonForRaceID(raceID)
CharacterCreate_GetUISlotForRaceID(raceID)
```

`SetCharacterRace(uiSlot)` may keep `CharacterCreate.selectedRace` as the UI slot for compatibility with the rest of the existing screen, but it must also set `CharacterCreate.selectedRaceID` from the selected button's `raceID`.

The existing XML click path may remain:

```lua
CharacterRace_OnClick(self, self:GetID());
```

provided `CharacterRace_OnClick`/`SetCharacterRace` update `selectedRaceID` from `self.raceID`. The key rule is that project-owned metadata must never infer the exact RaceID from the UI slot. Tests should require `raceID` for every enabled button.

### Resolving the actual RaceID

The Esteria client foundation documents a native `GetAvailableRaceIDs()` API. Verify that it is exposed by the **active** `Client.dll` before depending on it. If available, pair the IDs it returns with the current `GetAvailableRaces()` enumeration.

If the active API cannot provide a reliable one-to-one list, extend the existing project-owned `CharacterInfo.lua` race metadata with an explicit FileString-to-RaceID table. Do not infer RaceID from button position.

For paired species, use distinct internal file strings so the mapping is unambiguous even when the display name is shared. The integration plan should use distinct keys along the lines of:

```text
Earthen / EarthenHorde
Haranir / HaranirHorde
Skyborne / SkyborneHorde
```

or equally explicit High Order/Windshaper keys if that is the final naming decision.

The exact visible race name can still be identical or species-focused. The internal file string must remain unique when faction identity differs.

## 6.3 Add each new race to the existing CharacterInfo data

Do not create a second race-information subsystem. Extend the live tables/functions already exported by `CharacterInfo.lua`.

For every new exact RaceID add/update the existing equivalents of:

```text
Races_Informations
raceInfoByFileString
RACE_DATA
ALLIANCE_RACES
HORDE_RACES
raceLocalization
GetRaceName
GetFactionForRaceID
GetFactionForRaceName
```

Keep all existing rows intact.

The current file already has hand-maintained entries for races such as Broken, Darkfallen, Kul Tiran and Illidari. Follow that pattern but remove ordinal assumptions for the new IDs.

Each new race entry must define at least:

```text
actual RaceID
unique ClientFileString
visible race name
Alliance/Horde faction
race-description token
racial ability names/descriptions
creation-screen art key
```

Paired species must have two exact RaceIDs in `RACE_DATA`, even when both point to the same `Races_Informations` descriptive object.

Do not overwrite or renumber current `RACE_DATA` entries to make room.

## 6.4 Add the race to the existing CharacterCreate enumeration

For each race implementation phase, Codex must prove the following sequence works on the existing screen:

1. the new `ChrRaces.dbc` row is present in the winning client DBC;
2. the client enumerates the race through the existing `GetAvailableRaces()` path;
3. `CharacterCreateEnumerateRaces(...)` receives its name/FileString/enabled triple;
4. that triple is bound to the correct **actual** RaceID;
5. an unused existing race button slot is populated;
6. the new icon is assigned through the existing `RACE_ICON_TEXTURES` / icon fallback logic;
7. the button receives the same current border, highlight, tooltip and checked-state behavior as existing races;
8. clicking it calls the existing character-create flow with the correct RaceID;
9. class availability refreshes normally;
10. sex switching keeps the same race selected;
11. the five customization controls refresh for the new race;
12. Back/Create/Freeborn controls continue to use the current screen implementation.

A new race is **not** considered implemented if it can only be created through a command, DB edit or temporary test button.

## 6.5 Creation-screen icon and presentation assets

Add race/sex icon art using the existing naming and portrait tooling. Prefer `tools/race_portrait_pack.py` and the current texture-table mechanism rather than adding one-off Lua texture code.

Expected paths are:

```text
Interface\Glues\CharacterCreate\UI-CharacterCreate-<FileString>Male.blp
Interface\Glues\CharacterCreate\UI-CharacterCreate-<FileString>Female.blp
```

Add corresponding keys to the existing `RACE_ICON_TEXTURES` mapping.

For faction-paired entries, either share the same portrait texture or provide faction-specific variants. Do not duplicate model/texture payload solely because there are two faction RaceIDs.

Add the race's existing-screen presentation metadata to `GlueParent.lua` by extending, not replacing:

```text
CharModelFogInfo
CharModelGlowInfo
GlueAmbienceTracks
RaceLights
background/model routing tables
```

A compatible existing Human/Orc/Dwarf/NightElf/Tauren/BloodElf background may be inherited initially. A new custom background is polish and must not block race creation.

## 6.6 CharacterSelect requires support, not a replacement screen

Do **not** add a second character-select screen and do not restore stock `CharacterSelect.lua/xml`.

Esteria's current CharacterSelect is already heavily customized and includes:

- the ECS roster presentation;
- custom row backgrounds;
- faction badges;
- scroll-offset logic for the expanded character limit;
- Freeborn integration;
- selected-character background/model routing.

The new races must flow through this existing roster.

There is no need to create one static XML roster row per race. A character-select row is populated from `GetCharacterInfo(actualIndex)`. What must be added is the race metadata that lets the existing row correctly interpret the returned character.

For each new exact RaceID/FileString:

1. ensure the server sends the exact RaceID in the character enumeration packet;
2. ensure the high-ID runtime model table resolves the race/sex display correctly;
3. ensure `GetCharacterInfo()` returns the intended visible race name;
4. extend `GetFactionForRaceName`/race metadata so the correct faction badge appears;
5. extend selected-character background routing for the new FileString;
6. extend fog/glow/light/ambience tables for the new FileString;
7. preserve the existing selected-character 3D model path;
8. preserve Freeborn badge behavior;
9. preserve the current scroll offset and row IDs for 100-character support.

The existing `CharacterSelect.lua` has a Darkfallen-specific faction workaround based on `GetSelectBackgroundModel(actualIndex)`. Generalize that concept into a table keyed by the returned model/FileString instead of adding six more race-specific `if` blocks. For example:

```lua
local RACE_FACTION_BY_MODEL_KEY = {
    DARKFALLEN = "Alliance",
    DARKFALLENHORDE = "Horde",
    EARTHEN = "Alliance",
    EARTHENHORDE = "Horde",
    HARANIR = "Alliance",
    HARANIRHORDE = "Horde",
    SKYBORNE = "Alliance",
    SKYBORNEHORDE = "Horde",
}
```

Use the actual final FileStrings from the generated `ChrRaces.dbc`; the names above illustrate the required structure.

This is especially important for paired species because `GetCharacterInfo()` can return the same localized species name for both factions. Faction must therefore be resolvable from exact RaceID or unique model/FileString, not only from the visible name.

## 6.7 CharacterSelect 3D model verification

The roster row itself is not enough. Selecting the character must display the new model in the existing CharacterSelect scene.

For each new race/sex verify:

```text
ChrRaces.model_m / model_f
    -> CreatureDisplayInfo
    -> CreatureModelData
    -> custom\<race> converted M2
```

and verify the native model-descriptor table for that high RaceID/sex is populated by the existing `races-64-esteria` / generalized race runtime extension.

Do not fake the selected model with a GlueXML creature model override. The selected character must resolve through the same actual character race/display path used in game so equipment, customization and relog behavior match.

## 6.8 Freeborn compatibility

Esteria allows all races to opt into Freeborn behavior. Extend the existing Freeborn wrappers; do not replace their CharacterCreate or CharacterSelect hooks.

Ensure all RaceIDs 45-53:

- display the existing Freeborn toggle on CharacterCreate;
- preserve the exact RaceID while changing team behavior;
- do not accidentally switch to the paired Alliance/Horde species row when Freeborn is selected;
- display the existing Freeborn badge correctly on CharacterSelect;
- continue to use the same character-list row and selected-character model;
- retain trade/chat/group/guild behavior defined by the Freeborn system.

Add all new RaceIDs to Freeborn tests.

## 6.9 Mandatory additive UI regression tests

Create `tools/test_retroported_race_glue_contract.py` or extend the current race contract tests.

At minimum assert against the **effective live Z-layer files** that:

- `MAX_RACES >= 53` and preferably equals the 64-race runtime capacity;
- existing `CharacterCreateRaceButton1..40` still exist and retain the existing template;
- capacity exists for the new race buttons;
- every enabled race button stores an explicit actual `raceID`;
- every enabled race button has both a UI slot and `button.raceID`, and selection preserves the stock slot-based `SetSelectedRace` flow while recording the exact RaceID;
- `SetCharacterRace` locates a button by its stored RaceID;
- all pre-existing race FileStrings remain in `CharacterInfo.lua`;
- RaceIDs 45-53 and their FileStrings are present;
- current Freeborn hooks are still present;
- the current CharacterSelect scroll functions are still present;
- the current ECS row layout code is still present;
- existing Darkfallen/Kul Tiran/Illidari mappings remain present;
- new faction/model-key mappings are present;
- both `patch-Z.MPQ` and `patch-enUS-Z.MPQ` contain coherent copies of every Glue file modified in both archives.

Run the existing UI/race regressions too:

```text
tools/test_character_select_contract.py
tools/test_character_limit_contract.py
tools/test_freeborn_team_pack.py
tools/test_broken_client_contract.py
tools/test_playable_race_contract.py
```

If an existing screen behavior disappears, the phase fails even if the new race can be created.

---

# 7. Runtime customization support for RaceIDs 45-53

Do **not** manually seed WotLK customization counts for the retroported races. Reverse-engineering the live 3.3.5a client during the Mag'har pilot proved that the table at the customization pointer is not five simple UI counters. The client builds a nested `{count, pointer}` index directly from the full `CharSections.dbc`, sized from the maximum loaded RaceID. Each race/gender/section entry contains an outer variation count plus a pointer to per-variation color-count arrays.

Writing values such as `9 skins` or `3 faces` into `entry[0]` corrupts that native index. RaceID 45 does not require a manual high-ID count patch as long as:

- the full standard `ChrRaces.dbc` contains RaceID 45;
- the full standard `CharSections.dbc` contains complete RaceID 45 rows;
- client and server use the same generated full DBCs;
- the row `Flags`, variation indices, and color indices satisfy the native lookup rules.

The existing Darkfallen hair clamp in `wxl-races-patcher/DarkfallenCharacterSelect.cpp` is a separate legacy safety fix and can remain. Do not generalize that clamp into synthetic Mag'har/Highmountain/etc. counts unless a future binary audit proves a race genuinely needs it.

## 7.1 `CharSections.Flags` is part of customization availability

The native skin/face iterators validate each candidate through `CharSections.Flags`. The Mag'har pilot originally cloned dark Orc donor rows with `Flags = 0x5`. Those rows are accepted by the Death Knight applicability path but rejected by normal classes, causing Skin Color to test every candidate and wrap back to color 0. Face rows were rejected by the same path and could leave the head compositor unresolved/green.

For generated appearance rows intended to be shared by both ordinary classes and Death Knights, Esteria uses `Flags = 0x11`. Binary inspection confirmed that `0x11` satisfies all seven native applicability predicates used by skin, face, hair, facial-feature, and underwear selection while keeping a single style/color row per appearance.

Every retroported-race contract test must inspect the final staged `CharSections.dbc` and assert the intended flags. Never assume a visually similar donor row has compatible applicability flags.

Keep character-select/model-resolution logging behind a debug flag. Add verification for the native DBC-built customization hierarchy rather than writing synthetic counts into client memory.

---

# 8. Modern customization strategy

3.3.5a character data has five legacy appearance bytes:

```text
skin
face
hairStyle
hairColor
facialStyle
```

Retail/Forever races have many more independent dimensions. A full Esteria integration must intentionally flatten them.

## 8.1 Required v1 mapping

Every race must expose at least:

```text
Skin Color -> skin
Face -> face
Hair Style -> hairStyle
Hair Color -> hairColor
Primary race feature/preset -> facialStyle
```

`facialStyle` may represent a **combined feature preset**, not literally facial hair. For example one index can encode a valid combination of horn/jewelry/tattoo extras.

This gives every race stable character creation, persistence and barber support without changing the 3.3.5a character packet/database format.

## 8.2 True 1:1 modern customization is a later protocol project

If every modern category must remain independently selectable, that requires a separate custom appearance protocol because the stock character record cannot store 20+ independent choices.

That project would require:

- custom character appearance table keyed by GUID;
- native client hooks to expose additional controls and send values;
- server packet/extension channel;
- character-select reconstruction;
- barber replacement UI;
- persistence/migration code.

Do not make the six-race rollout depend on this. For this plan, "fully implemented" means fully playable/stable with all important visual families accessible through valid legacy fields or curated combined presets.

---

# 9. Collection-model geometry strategy

Retail's `ChrCustomizationSkinnedModel` does not exist in Wrath. Do not try to load Retail DB2 behavior at runtime.

Use **geoset baking** where practical:

1. duplicate the converted base player M2 into an integration work tree;
2. import compatible collection-model submeshes;
3. bind imported vertices to matching base skeleton bones;
4. assign stable, unused player-model geoset IDs;
5. expose those geosets through `CharHairGeosets` and/or `CharacterFacialHairStyles` feature slots;
6. validate total vertices stay below 65,535;
7. preserve equipment geoset conventions so armor can still hide body sections correctly.

Write a reusable geometry tool instead of manual edits. Recommended work tree:

```text
G:\RetroPorterWork\<race>\integration\patch-root\custom\<race>\...
```

## 9.1 Vertex budget rules

- **Skyborne:** base + both small collections can fit comfortably. Prefer baking all useful collection geometry into the base M2.
- **Mechagnome:** base (~18k) + collection (~26k) is within the Wrath ceiling. Baking the useful mechanical collection into each sex's base M2 is practical.
- **Earthen:** female collection is ~60.6k before adding the base. Do not merge the entire collection. Extract only selected geosets or create curated model variants.
- **Haranir:** collection models are ~55-60k plus ~24k base. Do not merge the entire collection. Select/prune important geosets or use curated variants.
- **Mag'har / Highmountain:** primary v1 appearance does not depend on a large external collection merge.

## 9.2 `.bone` overrides

Modern `.bone` overrides have no native Wrath equivalent.

For initial integration:

- exclude feature choices that visibly depend on unsupported `.bone` transforms;
- do not ship a broken option just because its texture exists.

For later parity, implement a bone-baking path that reads the source `.bone` transform and bakes the selected transform into a derived M2 variant. Never copy `.bone` files into the 3.3.5a patch and assume the client will use them.

---

# 10. Server-side race data per race

For each new exact RaceID create/clone the following as appropriate:

```text
playercreateinfo
player_race_stats
playercreateinfo_action
playercreateinfo_item
exact race start skills
exact race start spells
languages
racials
CharBaseInfo
CharStartOutfit
reputation/faction defaults
shaman totem model mapping
druid shapeshift fallback mapping
name generation
```

Esteria currently exposes broad all-class support. Unless the user explicitly changes that policy, generate the same class set used by `race_registry.json`:

```text
1, 2, 3, 4, 5, 6, 7, 8, 9, 11
```

Death Knight uses Ebon Hold start data.

Use the closest visual/gameplay host as the data template, then replace languages/racials deliberately.

## 10.1 Default start profiles

Use existing Esteria start profiles for the first implementation:

```text
Mag'har Horde        -> durotar
Highmountain Horde   -> mulgore
Mechagnome Alliance  -> dun_morogh
Earthen Alliance     -> dun_morogh
Earthen Horde        -> durotar
Haranir Alliance     -> teldrassil
Haranir Horde        -> durotar
Skyborne Alliance    -> elwynn (or the existing High Elf profile)
Skyborne Horde       -> eversong
DK                    -> ebon_hold
```

These are compatibility starts, not attempts to backport modern starting zones.

---

# 11. Race 1: Mag'har Orc (Esteria 45)

## 11.1 Source assets

Canonical source:

```text
G:\RetroPorterWork\maghar\output\patch-root
```

Core models:

```text
custom\maghar\character\orc\male\orcmale_hd.m2
custom\maghar\character\orc\female\orcfemale_hd.m2
custom\maghar\character\orc\male\orcmaleupright.m2
```

Converted output status:

```text
430 written
0 failed
9 skipped eye textures
27 unsupported .bone overrides
```

## 11.2 Use the existing Mag'har module only as data precedent

There is an older Mag'har implementation under:

```text
modules/mod-worgoblin-high-elf/modpaks/F-032_mod-maghar
```

It contains useful precedent for:

- starting data
- racials
- shaman totems
- forms
- DBC table coverage
- faction/language data

Do **not** reuse its old RaceID 14. Esteria currently uses 14 for Broken.

Do **not** reuse its old model/display rows blindly. Generate new IDs pointing at the new `custom\maghar` models.

## 11.3 Appearance v1

Map:

```text
skin        = clan skin color
face        = clan face
hairStyle   = hair style
hairColor   = hair color
facialStyle = beard/sideburn/tusk preset
```

Choose hunched or upright as the default male model for v1. Recommended: use the standard converted male model first, then expose upright later through a native/model-variant enhancement. Retail upright is a conditional model swap and is not a normal geoset.

Use a stable default eye set because nine eye BLPs are unavailable.

## 11.4 Mag'har acceptance gate

Before moving to Highmountain verify:

- create male/female
- every class creates
- log in/relog
- skin/face/hair/hair color/features persist
- barber can change supported fields
- normal armor all major slots
- helmets show/hide expected ears/tusks
- weapons attach correctly
- mounts seat correctly
- swim/jump/fall/death/emotes/combat work
- Horde language/faction behavior correct
- Mag'har racials only on Mag'har
- Orc does not gain Mag'har racials
- Freeborn Mag'har works
- PlayerBot can create/use race 45
- worldserver restart reloads the race cleanly

Only after this passes may the generic pipeline be reused.

---

# 12. Race 2: Highmountain Tauren (Esteria 46)

Source:

```text
G:\RetroPorterWork\highmountain\output\patch-root
```

Models:

```text
custom\highmountain\character\highmountaintauren\male\highmountaintaurenmale.m2
custom\highmountain\character\highmountaintauren\female\highmountaintaurenfemale.m2
```

Status:

```text
279 files
0 failed
7 skipped eye textures
9 unsupported .bone assets
```

Appearance v1:

```text
skin        = skin color
face        = face
hairStyle   = hair / foremane style
hairColor   = hair-compatible color
facialStyle = horn/beard/body-paint preset
```

Prioritize horn style before jewelry/tail decoration. Verify the surprisingly small converted sequence counts visually in client.

Clone Tauren collision, mount-height, language, shaman/totem and druid-form behavior unless race-specific behavior is deliberately supplied.

Acceptance gate is the Mag'har gate plus:

- horn clipping
- Tauren-sized helmets
- mount seat height
- body paint preset persistence
- druid/shaman fallback behavior

---

# 13. Race 3: Mechagnome (Esteria 47)

Source:

```text
G:\RetroPorterWork\mechagnome\output\patch-root
```

Base models:

```text
custom\mechagnome\character\mechagnome\male\mechagnomemale.m2
custom\mechagnome\character\mechagnome\female\mechagnomefemale.m2
```

Collection models:

```text
custom\mechagnome\item\objectcomponents\collections\collections_mechagnome_mg_m.m2
custom\mechagnome\item\objectcomponents\collections\collections_mechagnome_mg_f.m2
```

Status:

```text
360 files
0 failed
2 skipped textures
28 unsupported .bone overrides
```

## 13.1 Required geometry work

Mechagnome arms, legs and many modifications are collection geosets. Before DBC appearance work, build derived male/female player models that bake the useful collection geometry into the base models.

The combined vertex budget is practical.

Preserve separate geoset groups for:

```text
arm upgrade
leg upgrade
head/ear/antenna/visor modification
```

## 13.2 Appearance mapping

Recommended:

```text
skin        = skin color
face        = face
hairStyle   = hair style
hairColor   = hair color
facialStyle = mechanical configuration preset
```

The feature preset should choose a valid arm/leg/modification combination. Do not expose a choice whose required collection submesh was not baked.

Clone Gnome collision/scale/start behavior. Validate gloves, boots and pants especially because mechanical limb geometry can conflict with normal equipment geosets.

---

# 14. Race 4: Earthen (Esteria 48/49)

Source:

```text
G:\RetroPorterWork\earthen\output\patch-root
```

Base models:

```text
custom\earthen\character\earthendwarf\earthendwarfmale.m2
custom\earthen\character\earthendwarf\earthendwarffemale.m2
```

Collections:

```text
custom\earthen\item\objectcomponents\collections\earthenextras_ed_m.m2
custom\earthen\item\objectcomponents\collections\earthenextras_ed_f.m2
```

Important constraint:

```text
female collection ~= 60,596 vertices
```

Do not concatenate the full collection into the base model.

## 14.1 Build one visual species, two faction rows

RaceIDs 48 and 49 should point at the same generated male/female displays/models. Only faction/team/start/language data differs.

Use separate `ChrRaces` ClientFileStrings if Glue needs distinct faction lookup keys, for example:

```text
Earthen
EarthenHorde
```

Keep one shared art key for portraits/backgrounds.

## 14.2 Geometry strategy

Select a curated subset of collection geosets that represents:

```text
horns/gems
shoulder/torso detail
arm/hand detail
leg/belt detail
```

Prune unused collection submeshes before merge. Validate the final player M2 remains below 65,535 vertices.

Appearance mapping:

```text
skin        = stone/skin color
face        = face
hairStyle   = hair
hairColor   = hair/gem-compatible color
facialStyle = Earthen feature preset
```

Acceptance must test both faction IDs and confirm one faction's character creation cannot silently save as the other ID.

---

# 15. Race 5: Haranir (Esteria 50/51)

Source:

```text
G:\RetroPorterWork\haranir\output\patch-root
```

Base:

```text
custom\haranir\character\harronir\harronirmale.m2
custom\haranir\character\harronir\harronirfemale.m2
```

Collections:

```text
custom\haranir\models\item\unk_exp11_6255032_hr_m\6255032_hr_m.m2
custom\haranir\models\item\unk_exp11_6255031_hr_f\6255031_hr_f.m2
```

Status:

```text
1,028 files
0 failed
25 skipped BLPs
250 linked modern skinned-model choices in source discovery
```

Haranir is the most customization-heavy target. Do not attempt a blind full collection merge.

## 15.1 Geometry strategy

Create a deliberately pruned set of collection submeshes for visible categories such as:

```text
spines
shoulder spines
important jewelry/accessories
core face/body decorations
```

Keep the first integration under the vertex limit and reserve geoset ranges in the allocation manifest.

## 15.2 Two factions

IDs 50/51 share art. Alliance uses Night Elf compatibility for legacy masks/start behavior; Horde uses Troll compatibility. Exact race data supplies the actual Haranir racials/languages.

Appearance v1:

```text
skin        = skin/fur color
face        = face
hairStyle   = hair
hairColor   = hair color
facialStyle = Haranir feature preset
```

Test ears, hair, helmets, shoulder armor and back items carefully because the model has many silhouette-changing options.

---

# 16. Race 6: Skyborne (Esteria 52/53)

Source:

```text
G:\RetroPorterWork\skyborne\output\patch-root
```

Forever source identities:

```text
95 = High Order Skyborne
96 = Windshaper Skyborne
```

Esteria maps those concepts to 52/53, not the original IDs.

Base models:

```text
custom\skyborne\models\creature\unk_exp00_7478487\7478487.m2
custom\skyborne\models\creature\unk_exp00_7478494\7478494.m2
```

Dedicated collections:

```text
custom\skyborne\models\unknown\unk_exp00_7845093\7845093.m2
custom\skyborne\models\unknown\unk_exp00_7845092\7845092.m2
```

Shared converted Demon Hunter collections:

```text
custom\skyborne\item\objectcomponents\collections\demonhuntergeosets_be_m.m2
custom\skyborne\item\objectcomponents\collections\demonhuntergeosets_be_f.m2
```

Status:

```text
1,219 files
0 failed
0 skipped
40 unsupported .bone overrides
```

Skyborne is unusually friendly for baking because the extra collection models are small. Merge the useful Skyborne and Demon Hunter collection geosets into derived player models while staying below the vertex ceiling.

Appearance v1:

```text
skin        = skin color
face        = face
hairStyle   = hair
hairColor   = hair color
facialStyle = horn/feather/tattoo/accessory preset
```

High Order (52) and Windshaper (53) share art but have separate faction/start/language/racial profiles.

## 16.1 Initial curated integration, September 30, 2026

The original pack remains unchanged. Its twelve missing hard texture dependencies were recovered into
`G:\RetroPorterWork\skyborne\integration\patch-root`, bringing the closed input tree to 1,231 files.
The local Forever source had advanced to build 70124; all 118 regenerated M2/SKIN/ANIM files were byte-identical
to the build-70009 outputs before supplemental textures were accepted. Provenance is recorded in
`integration\dependency-closure.json`.

`tools/skyborne_visual_pack.py prepare` builds isolated runtime models and native indexed compositor textures.
Selected eyebrow, feather, and horn collection meshes are bound through matching bone-name CRCs and remapped
to legacy geoset groups. Body, head, feet, and eyes are mapped into the native player path; modern cape masks
are omitted. The source animation filenames are preserved, with 53 companions per gender.

The first version offers five authored blue/purple skins, four face textures, four hair styles, eight hair colors,
and four eyebrow/feather feature presets for each gender. Demon Hunter horns and ordinary Blood Elf skin tones
are excluded at the user's request. Face textures vary independently of skin; the forty source
`.bone` face-shape overrides are deliberately not applied. Geometry remains the neutral source head.
The curated SKIN is compacted below 65,536 triangle indices. Larger source index tables encode their upper
bits in the geoset DWORD, which the native character visibility selector treats as an unsupported geoset ID.
The first version therefore prunes surplus hairstyles, modern boot variants, cape variants, and duplicate eyes.

The shared installer delegates Skyborne data generation to `tools/skyborne_race_pack.py` and preserves the
existing Mag'har entries in Patch-R. Both Z archives and the seven server DBCs receive matching full tables.
High Order uses the existing High Elf gameplay profile, and Windshaper uses Blood Elf, including their current
starting locations, languages, class defaults, and racials. Dedicated Skyborne racials remain a later content pass.

Reproducible entry points:

```powershell
python tools/skyborne_visual_pack.py prepare
python tools/retroported_race_pack.py build --race skyborne
python tools/test_skyborne_visual_pack.py -v
python tools/test_skyborne_race_pack.py -v
python tools/retroported_race_pack.py install --race skyborne
```

The world starter migration is `data/sql/updates/pending_db_world/rev_20260930003000000.sql`.
The user confirmed both genders' body visibility, blue skin choices, and eyebrow/feather feature cycling in
CharacterCreate after the visibility and palette corrections. Live textures were captured and compared to
staging after normalizing the client's palette padding, with matching body/face data and no neon-green pixels.
Character creation, login, CharacterSelect, movement, armor, helmets, barber, mount seating, and relog still
require live acceptance.

## 16.2 Native appearance expansion, September 30, 2026

Skyborne's active manifest now selects `native-byte-codec-v1`. The permanent fingerprint-checked executable
imports a standalone appearance helper; customization has no WXL dependency. WXL continues to supply the
existing race-capacity and unrelated features. The initial curated builder rejects native mode to prevent
accidental downgrade. Build, installation, catalog schemas, option counts, and rollback are documented in
`client-customization/README.md`.

Both genders now have separate skin, face texture, hairstyle, hair color, eye color, eyebrows, feathers,
feather color, and ears controls; males also have facial hair. Expanded models remain isolated under
`custom\skyborne\expanded`. Face `.bone` morphs and tattoos remain unapplied. The barber UI still uses combined
encoded selections. The first native visual test exposed incorrect character-object offsets and an existing
WXL MD20 reader clearing meshes with extended triangle starts. The corrected catalog uses the verified native
setter offsets; prepared SKIN palettes fit Wrath's limits, and the permanent native initializer restores the
complete matching geometry arrays before filling buffers. The user confirmed repaired body visibility for both
genders. Feather meshes now follow their source hairstyle dependencies. The user confirmed the feather
correction and rotation controls below the first/last name fields. New-character login/relog, armor/helmet,
and barber smoke remain untested for the expanded codec.

The two Z archives and seven mounted server DBCs are synchronized. CharSections reserves IDs `455000..519999`,
with 56,000 current rows at `456188..512187`. The one existing character was migrated once and subsequent
native installations preserve its encoded appearance. Backups are outside client Data on C:.

Because Skyborne reuses Blood Elf textures, preserve the `custom\skyborne` namespace. Never make its generated DBC point at stock Blood Elf texture/model paths when a converted copy exists.

## 16.3 Supplied portraits and compact creator layout, September 30, 2026

`tools/creator_portrait_layout.py build` converts the six supplied PNGs in
`R:\Users\Zach\Pictures\Portraits` for male/female Mag'har and both Skyborne factions. Creator icons use the
existing metal ring and circular mask from `tools/race_portrait_pack.py`. CharacterSelect/paper-doll portraits
use the same masked art without a baked ring, matching the existing portrait pipeline. All output is 64x64
BLP2 with seven mips. Skyborne faction images remain distinct through `Skyborne` and `SkyborneHorde` paths;
Mag'har now has explicit creator icon mappings instead of the old atlas fallback.

The creator uses seven columns per faction with width-dependent icon sizing and wrapping rows. Faction
headings are centered above each grid. Existing enumeration order, exact RaceID selection, tooltips,
Freeborn, native appearance controls, and rotation anchors are retained. Lua syntax and all 64 button anchors
were checked at widths 800, 1024, 1834, and 2560. This only changes client art and GlueXML.

`tools/creator_portrait_layout.py install` verifies staged hashes, backs up all three archives on C:, then
replaces changed copies of global Z, locale Z, and Patch-R. Backups remain outside client Data. Restore files
listed in `replaced_archives` from the recorded backup to undo an update; no server restart is required.
The supplied images and generated BLPs stay outside Git. Archive readbacks and unchanged identity/appearance
DBCs are verified. The user confirmed the portraits and compact layout, followed by both name fields hidden
until customization and the corrected `Customize` button text. Both fields appear together after opening
customization. The completed creator UI was visually accepted on September 30, 2026.

## 16.4 Chat, animation and Character Select touchups, October 1, 2026

The supplied Skyborn chat crash was traced to animation 60, variant 1, playing invalid timestamp pointers
after the runtime generator rebased external ANIM spans while rewriting flat MD20. Native external spans
are now marked before serialization, and a regression check preserves every external bone track span and
validates the failing talk sequence against its companion file. This fixes the asset flow instead of suppressing
chat/emotes. The prior cinematic crash had a different heap-allocation stack; a fresh first-login test passed
after the repairs, but that earlier stack's exact cause was not independently established.

The server already persisted Orcish on Mag'har and Orcish/Thalassian on Windshaper Skyborn. The client exposed
no languages because its 32-bit skill/spell eligibility checks used the high actual RaceID instead of its legacy
mask race. Two fingerprint-checked native redirects now match the server's eligibility mapping for IDs 45,
52, and 53, preserving identity and unrelated races. No SQL mutation or worldserver rebuild was needed.

ECS now resolves the actual packet RaceID through the native helper, registers Mag'har Orc/Skyborn labels and
factions, and loads six portraits in its own namespace. Long names do not wrap and fit their existing row;
tooltip placement uses consistent parent-scale coordinates and prefers below the cursor. Creator Skyborn
tooltips have separate names/descriptions and preserve the existing racial ability data.

The installed files are backed up under `C:\Users\Zach\.codex\backups\race-touchups-20261001-011659`.
The user confirmed the requested Character Select, language/chat, and fresh Skyborn login checks on
October 1, 2026. `tools/race_touchup_pack.py` rebuilds/installs this layer; `tools/test_race_touchup_pack.py`
and the standalone native harness verify the corrected contracts.

---

# 17. DBC generation details

For every race row, generate at least the following.

## 17.1 `CreatureModelData`

Clone geometry/collision values from the closest working Esteria host race, then replace:

```text
ID
ModelName
collision dimensions if model inspection proves the host values are wrong
mount height if seating is wrong
```

Do not copy Retail CreatureModelData semantics directly.

## 17.2 `CreatureDisplayInfo`

Create male/female display rows pointing at the generated CreatureModelData IDs. Clone safe scale/alpha defaults from the visual base race.

## 17.3 `ChrRaces`

Set:

```text
RaceID
flags
faction template
male/female display IDs
TeamID/BaseLanguage fields matching Esteria's existing conventions
ClientPrefix
ClientFileString
Alliance field
localized names
customization labels
expansion
```

For paired species, use shared displays and separate faction row fields.

## 17.4 `CharSections`

Generate deterministic rows for skin/face/hair texture composition from RetroPorter discovery reports.

Do not copy every Retail material combination. Build only combinations reachable from the five legacy appearance fields/presets.

Validate every referenced BLP exists in the staged patch.

## 17.5 `CharHairGeosets` and `CharacterFacialHairStyles`

Resolve the **actual converted M2 geoset IDs**. Do not assume Retail `GeosetType` equals Wrath `GeosetID`.

For baked collection geometry, assign and document stable new geoset IDs.

## 17.6 Barber

Generate `BarberShopStyle` only after creation mappings are stable. Every barber option must correspond to a valid creation appearance and survive relog.

Do not expose unsupported modern categories as fake barber types.

## 17.7 `CreatureDisplayInfoExtra`

Generate/clone rows where required for equipped-item/NPC-style displays and set `DisplayRaceID` to the exact Esteria race row. Test item rendering on character select and in world.

## 17.8 Helmets

Audit `HelmetGeosetVisData` and race-specific ear/horn visibility. Extend rows only where current helmet data would hide required geometry or leave severe clipping.

---

# 18. Server SQL and Docker integration

Put new SQL under the normal module-owned update path, following repository SQL rules:

```text
modules/mod-custom-server/data/sql/db-world/updates/
```

If core schema support for exact race start skills/spells is added, put schema/update SQL in the appropriate pending/module update location and keep it idempotent.

Do not edit AzerothCore historical base/archive SQL.

## 18.1 Server DBC synchronization

Retroported playable races use **full standard DBCs**, not race-specific `.dbc1-*` continuation files.

Use the effective winning full DBC from the current Esteria client as the merge base. Generate the new full table once, then deploy the **same generated bytes** to both sides:

```text
client Data\patch-Z.MPQ\DBFilesClient\<Table>.dbc
client Data\enUS\patch-enUS-Z.MPQ\DBFilesClient\<Table>.dbc
server data/dbc/<Table>.dbc
```

For Docker development, mount the generated full server DBC from `modules/mod-custom-server/data/dbc/retroported-races/` into `/azerothcore/env/dist/data/dbc/<Table>.dbc`. That deployment directory is intentionally gitignored because the generated files contain Blizzard client data. The packer must hash-verify that the server copy is byte-identical to the generated client table.

The server must resolve the same:

```text
ChrRaces IDs
CreatureModelData IDs
CreatureDisplayInfo IDs
CreatureDisplayInfoExtra IDs when used
CharSections rows relevant to validation
CharStartOutfit rows
Barber rows
Spell rows used for custom racials
```

AzerothCore also applies SQL-backed `*_dbc` overlays after loading the binary file. Query those tables after database import and make sure they do not contain stale rows that overwrite the generated race/model/display identity.

`mod-wxl-dbc` remains valid for existing systems deliberately designed around continuations, such as the Freeborn faction continuation and other unrelated custom content. Do **not** use that mechanism for the retroported playable races themselves.

### Player display-ID constraint

Before accepting any `CreatureDisplayInfo` allocation for a playable race, assert:

```text
0 < displayId <= 65535
```

`PlayerInfo::displayId_m` and `PlayerInfo::displayId_f` are `uint16`. A display ID above 65535 wraps before `Player::InitDisplayIds()` uses it. This previously turned Mag'har display `150045` into `18973`, which is an existing Gnome display. The reserved retroported-race player-display band is therefore `60030-60047` unless a later audited allocation changes it.

### Model/texture dependency closure

Before packaging a race, inspect every converted player/collection M2 and prove that every hard texture reference resolves in the final global patch. Modern M2 TXID references must be included in the RetroPorter asset plan even when they were not reached through the customization DB2 graph. Validation must fail on a missing referenced BLP rather than allowing a neon-green model into the client.

## 18.2 Docker validation flow

Current Compose services are:

```text
ac-database
ac-db-import
ac-worldserver
ac-authserver
ac-client-data-init
```

Recommended validation sequence after a race's server work is ready:

```powershell
docker compose build ac-db-import ac-worldserver ac-authserver ac-client-data-init
docker compose up -d ac-database
docker compose up --build ac-db-import
docker compose up -d --build ac-client-data-init ac-authserver ac-worldserver
```

If the normal project workflow uses a different production compose file, use that file consistently instead. Do not run two stacks binding 3724/8085 at once.

Then inspect:

```powershell
docker compose ps
docker logs ac-worldserver --tail 300
docker logs ac-authserver --tail 100
```

Worldserver startup must show no invalid race, invalid raceMask, missing DBC row, missing start skill/spell or playercreateinfo errors for the new race.

## 18.3 Query the live DB after import

Verify the exact new rows with SQL queries against:

```text
chrraces_dbc
creaturemodeldata_dbc
creaturedisplayinfo_dbc
charsections_dbc
barbershopstyle_dbc
charstartoutfit_dbc
playercreateinfo
player_race_stats
custom exact-race startup tables
```

Repository files are not proof that the persistent Docker volume applied the update.

---

# 19. PlayerBots integration

Esteria uses `mod-playerbots`. Add all RaceIDs 45-53 to any direct race switch/array that is not already driven by `RaceMgr`.

At minimum audit:

```text
modules/mod-playerbots/src/Mgr/Travel/TravelNode.cpp
modules/mod-playerbots/src/Mgr/Travel/TravelMgr.cpp
modules/mod-playerbots/src/Util/EncounterHelpers.cpp
modules/mod-playerbots/src/Bot/Factory/*
```

Use each race's start/visual host profile for travel heuristics. Do not index fixed 12-race arrays with RaceID 53.

Add a smoke test that can create/randomize one bot of each new exact RaceID without crash.

---

# 20. Tests Codex must add

Build a race test suite, not a collection of manual notes.

Recommended tests:

```text
tools/test_retroported_race_contract.py
tools/test_retroported_race_pack.py
tools/test_retroported_race_glue.py
tools/test_retroported_race_assets.py
tools/test_retroported_race_dbcs.py
```

Assertions should cover:

- RaceIDs 45-53
- registry pairing
- exact model/display paths
- all staged assets exist
- M2 version 264
- every M2 under vertex ceiling
- every generated DBC parses
- no duplicate DBC IDs
- all string offsets valid
- both Z archives contain identical generated race DBC bytes
- Glue supports 64 buttons
- all new `ClientFileString` keys have icon/background/portrait entries
- every CharSections path exists
- hair/facial geosets exist in target M2
- no base race asset path is overwritten
- Freeborn code recognizes all new RaceIDs
- server enum and registry IDs match
- PlayerBots arrays are safe up to RaceID 53

Run existing regression tests too, especially:

```text
tools/test_broken_client_contract.py
tools/test_darkfallen_contract.py
tools/test_playable_race_contract.py
tools/test_character_select_contract.py
tools/test_character_limit_contract.py
tools/test_freeborn_team_pack.py
```

A new race is not allowed to break Broken, Darkfallen, Illidari, Freeborn or the 100-character selector.

---

# 21. Per-race manual QA checklist

Run this complete checklist for **every** race row before moving on.

## Character creation

- race appears once in correct faction/species presentation
- male and female preview loads
- class buttons valid
- all five legacy customization dimensions cycle without crash
- Randomize never selects invalid indices
- generated name works
- creation packet saves the intended exact RaceID
- Freeborn creation preserves intended race

## Character select

- portrait correct
- faction badge correct
- model renders after fresh login
- 100-character scrolling/order remains correct
- paired species do not display as each other

## In world

- login location correct
- language correct
- racials correct
- no host-race-only racial leakage
- faction/reputation correct
- Freeborn behavior correct
- walk/run/sprint/jump/fall/swim
- combat ready/attack/cast/channel
- sit/sleep/kneel/emotes
- corpse/death/ghost/resurrection
- mount seating
- taxi
- hearth
- teleport

## Equipment

Test at least:

```text
shirt
chest
robe
pants
boots
gloves
belt
shoulders
cloak
helmet
one-hand weapon
two-hand weapon
shield
offhand
ranged weapon
```

Inspect clipping and attachment points in both sexes.

## Barber

- supported categories present
- cost calculated
- apply succeeds
- relog persists
- invalid combinations rejected instead of crashing

## Persistence

- logout/login
- server restart
- client restart
- faction/team data unchanged
- appearance unchanged

---

# 22. Implementation order and hard gates

Use this exact order:

```text
Phase 0  Extended RaceID / compatibility-mask architecture
Phase 1  Generic retroported-race generator + tests
Phase 2  Mag'har 45
Phase 3  Highmountain 46
Phase 4  Mechagnome 47
Phase 5  Earthen 48/49
Phase 6  Haranir 50/51
Phase 7  Skyborne 52/53
Phase 8  Final combined regression / production packaging
```

Why this order:

- Mag'har has the strongest existing Esteria precedent and simplest model architecture.
- Highmountain proves the pipeline on a dedicated modern race without large external collection geometry.
- Mechagnome proves collection-geoset baking while comfortably under the vertex ceiling.
- Earthen proves paired factions plus aggressive collection pruning.
- Haranir is the largest customization graph and should reuse all prior machinery.
- Skyborne has clean assets and small collection meshes, but its source is Forever rather than Retail, so it is best integrated after the common tooling is mature.

Do not commit six half-working races. Each phase ends with a usable race and a regression-safe repository.

## 22.1 Current Phase 0-2 checkpoint (2026-09-29)

Phase 0, Phase 1, and the corrected non-visual implementation portion of Phase 2 are complete in the current working tree. The first visual Mag'har pass exposed two integration bugs: player display IDs `150045/150046` exceeded AzerothCore's `uint16` player-display storage, and the converted M2 dependency set omitted nine hard-referenced BLPs. The second visual pass proved a deeper client-compatibility issue: the converted Retail Mag'har M2 retained modern replaceable/material texture types (including types 11 and 15), while the Retail clan skin/face textures use modern atlas dimensions that are not valid Wrath `CharSections` fragments. Those defects are now treated as pipeline constraints rather than patched only for the test character.

Verified before the next visual acceptance pass:

- RaceIDs 45-53 and their legacy-mask/visual-base/paired-race helpers compile in the Docker worldserver;
- exact-race startup spell/skill tables are installed and loaded by the world database path;
- the generic retroported-race packer builds, validates, transactionally backs up, and installs against `G:\\3.3.5a - Dev`;
- Mag'har RaceID 45 is present in both winning Z archives with converted `G:\\RetroPorterWork\\maghar` assets;
- Mag'har now uses player display IDs `60030/60031`, both safely below 65536, resolving to reserved custom model IDs `120045/120046`;
- visual QA of RetroPorter's directly converted Retail Orc M2s showed that build 12340 does not select the modern base-body/head geoset groups correctly: the models load, but most of both sexes disappear while only a few compatible geosets remain visible. Retail itself marks Mag'har as an Orc model-fallback race, so the production Race45 model rows now deliberately use the known-good `Character\\Orc2\\Male\\OrcMale2.m2` / `Character\\Orc2\\Female\\OrcFemale2.m2` Wrath-HD geometry. The retroported Retail Mag'har skin/face/hair materials remain race-specific through `CharSections`; direct Retail geometry stays an experimental future path until its modern geosets are explicitly flattened/remapped;
- obsolete Mag'har displays `150045/150046` are removed from the generated full `CreatureDisplayInfo.dbc`;
- RetroPorter now discovers direct M2 TXID texture dependencies; the Mag'har source output grew from 430 to 439 written files and contains all nine previously omitted hard-referenced BLPs;
- the live CharacterCreate files keep UI slot selection separate from exact RaceID and resolve `Maghar` to RaceID 45 even though the legacy `GetAvailableRaceIDs()` foundation export only enumerates the original 27 IDs;
- the existing CharacterCreate and CharacterSelect screens are extended in place rather than replaced;
- the WarcraftXL runtime hook still preserves the existing Darkfallen safety clamp, but no longer writes synthetic Mag'har customization counts **or intercepts Mag'har Skin/Face cycling**. The former `Maghar_CustomizationRouter` Cartesian-product hack is removed. Race45 now uses the stock client customization router and the native DBC-built `{count,pointer}` hierarchy from the full `CharSections.dbc`;
- the live 64-race foundation verifier passes;
- RaceID 45 now emits **522** `CharSections` rows using native selector semantics. Each sex has 9 section-0 Skin rows, 81 section-1 Face rows (9 face styles x 9 skin colors), normal hair/facial-hair rows, and 9 underwear rows. Skin remains `0..8`; Face remains `0..8`. The previous 81-value encoded Skin field is gone;
- the first derived-skin attempt used DXT1 BLP2. Although Converter considered those files generically Wrath-compatible, 3.3.5a's dynamic character compositor rendered every derived body skin neon green. Derived player-body `CharSections` textures must therefore match Esteria's proven Orc2 contract: paletted/indexed BLP2 (`compression=1`, `alpha_size=0`, `alpha_type=8`) with one shared 256-color palette and normal mip levels. The corrected baker now emits that exact layout, and the validator rejects derived Mag'har body skins that do not match it;
- the Mag'har pilot proved that 3.3.5a builds its live character customization/model hierarchy from the global `patch-Z.MPQ` copies of core character DBCs. A newer locale-Z `CharSections.dbc` or `CreatureModelData.dbc` can therefore look correct in static inspection while CharacterCreate still consumes stale global rows. The retroported-race build now streaming-rebuilds `patch-Z.MPQ` into a fresh MPQ and writes the exact same generated full DBCs to both global Z and locale Z; validation rejects any global/locale DBC mismatch. This also reclaimed roughly 2 GiB of dead replacement blocks from the old near-4 GiB archive. Global Mag'har appearance art remains isolated in dedicated `Data\\Patch-R.MPQ` under unique `custom\\maghar\\derived\\native\\...` paths, while the active geometry uses the proven Orc2 HD model paths already present in Z;
- the same pass binds the Retail Mag'har pelvis/torso underwear textures directly because their dimensions match the Wrath slots, and binds the 512x256 Retail `orcclanhair` textures into the proven Orc2 hair/facial-hair rows. Hairstyle/facial-hair geometry remains Orc2 until the modern geosets are ported safely;
- Race45 uses section-appropriate applicability flags: normal Skin/Hair/Underwear rows use `0x11`, while Face rows use the native Wrath face flag `0x1`. This mirrors the working Orc2 table instead of forcing one flag across all sections;
- the Retail Mag'har `clanskin` is split into a **skin-only** 512x512 body base plus a **skin-only** 512x512 extra-head base. Face choice is no longer baked into the section-0 head texture. Retail `clanfaceupper` is converted into the native Wrath face layers using `FaceUpper = (0,320) 256x64` and `FaceLower = (0,384) 256x128` for every 9x9 face/skin combination. The current bake emits 18 bodies, 18 base heads, and 324 face fragments (360 derived BLPs total), all paletted BLP2 (`compression=1`, `alpha_size=0`, `alpha_type=8`) with stock-compatible mip counts;
- the validator now rejects runtime player M2s that still carry unsupported modern texture types 11/15 and removes all stale RaceID 45 rows from Mag'har's reserved `CharSections` allocation before regenerating a smaller compatibility set;
- the playable-race pipeline no longer emits or deploys `*.dbc1-retroported-races` files. The same seven full standard DBCs are installed into both client Z archives and the server's normal `data/dbc` path;
- Docker-mounted `ChrRaces.dbc`, `CreatureDisplayInfo.dbc`, `CreatureModelData.dbc`, and `CharSections.dbc` hashes match the generated host DBC hashes exactly;
- the server still loads unrelated existing continuation-backed systems, but no `retroported-races` continuation is present;
- Mag'har receives 40 exact-race racial assignments (four racials across ten enabled classes);
- Docker `ac-database`, `ac-authserver`, and `ac-worldserver` start successfully, worldserver reaches ready state, and the realm is online at `127.0.0.1:8085`;
- the corrected retroported-race contract/build suite passes before visual acceptance;
- CharacterSelect, 100-character support, Broken, general playable-race, Darkfallen (27 tests), and Freeborn regression contracts all pass against the corrected live client.

Phase 2's **Orc2-contract visibility baseline is visually accepted**. The current installed pass is now pending visual acceptance of the 9 Retail-derived body skins, Retail underwear, and Retail clan hair colors. After those render cleanly, proceed to modern face-material baking, additional facial features/body paint, and finally any geometry-level Mag'har hairstyle/accessory work. Relog/barber persistence, equipment/mount animations, racials, and existing-screen regressions remain part of the final Phase 2 gate.

Do not start Phase 3 until that Mag'har acceptance gate passes.

---

# 23. Final packaging

When all races pass:

1. build one final staged `patch-Z.MPQ` from the current production Z plus all six race payloads;
2. build matching `patch-enUS-Z.MPQ` with authoritative DBC/Glue rows;
3. verify MPQ hashes and readback;
4. ensure no duplicate/lower patch shadows new DBCs;
5. regenerate launcher manifests/packages through the existing Esteria launcher workflow;
6. preserve the current loose-folder/zip delivery rules for any launcher-managed patch directories;
7. rebuild/import Docker server changes;
8. run the complete six-race smoke suite against the local server;
9. test a clean/new client install, not only the developer client that has accumulated old patches.

The final deliverables should include:

```text
repository manifests/generator/tests
server C++ changes
server SQL updates
WarcraftXL runtime extension update if required
staged client Z archives
race integration report with hashes
per-race QA results
rollback backup hashes
```

---

# 24. Definition of done

The six-race project is complete when:

- Mag'har, Highmountain, Mechagnome, Earthen, Haranir and Skyborne are selectable in the Esteria client;
- paired races have correct Alliance/Horde IDs;
- all race IDs persist correctly to the character DB;
- all races log into the Docker server without race-mask or DBC errors;
- all important converted art is used from `G:\RetroPorterWork` through the `custom\...` namespace;
- armor, helmets, weapons and mounts work in both sexes;
- the supported appearance set works at creation and barber and persists after relog;
- collection-model races use deliberately baked/pruned geometry rather than missing Retail runtime attachments;
- unsupported `.bone` choices are excluded or deliberately baked, never silently exposed broken;
- racials/languages/classes/start data are exact to the new race rather than leaking from compatibility masks;
- Freeborn works for every new race;
- PlayerBots handles every new RaceID safely;
- Broken, Darkfallen, Illidari and all existing races still work;
- character select still supports 100 characters;
- all client/server regression tests pass;
- a clean client can receive the final package through the normal Esteria launcher/update path.

Only then should the race block be considered production-ready.
