# Tauren Third-Gender (Taunka Body) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the PlayableTaunka asset pack as a third, separately selectable Tauren body alongside the existing Tauren male and Tauren female, without altering how either existing Tauren body renders.

**Architecture:** Gender `2` becomes a legal stored value (`GENDER_NONE` already reserves it). A new display ID below 65536 points at a new model path `Character\Taunka\Male\TaunkaMale.M2`, which is the pack's existing MD20 v264 M2 copied out of its Tauren-male identity. Because the 3.3.5a client derives skin/anim filenames from the model file name, every name-bound binary is copied and renamed under the `TaunkaMale` prefix rather than referenced. Because body textures are reached through `CharSections.TextureName_*`, the small set of Tauren-male sex-0 DBC rows is duplicated as sex-2 rows with texture names rewritten. The native layer supplies what the stock client has no slot for: a third model path, a third creator control, and a widened gender domain in its binary catalogs. The server side is a small, surgical set of changes: admit gender 2, add a third display-ID slot, and audit the ~10 places that branch on gender.

**Tech Stack:** Python 3, WDBC (WDBC v1), StormLib, AzerothCore C++20, MySQL `pending_db_*` migrations, native `EsteriaAppearance.dll` (x86, MSVC).

**Spec:** User request, plus the asset pack at `NewModels/_Other/PlayableTaunka/`. Preceding analysis in this directory's conversation; facts are restated in "Established Facts" so the plan is self-contained.

---

## Scope

**In scope — what this delivers:**

- A third creator control and third body option for race 6.
- A unique body: Taunka geometry, unique body/face textures (709 BLPs).
- Tauren male and Tauren female render **byte-identically** to today.

**Explicitly out of scope — the pack cannot deliver these, and the plan does not pretend otherwise:**

| Not delivered | Why | Where noted |
|---|---|---|
| Unique animation set | The pack ships 59 retuned Tauren anims out of Tauren male's full set. Same skeleton, Tauren's motion. | Task 3 |
| Unique horns / hair / facial hair / armor cosmetics | The M2 is geoset-compatible with Tauren male, so it can only *borrow* Tauren male's customization space. Taunka horns/fur are baked into the body. | Task 1 gate, Task 7 |
| Unique voice | Pack contains no sound files. A new display ID with no `CreatureSoundData` row is **silent**. | Task 8 |

If a genuinely distinct third bodytype (own cosmetics, own animation, own voice) is the real requirement, stop and use the `highmountain_race_pack.py` retroport pipeline instead — that path was built for exactly that and is a multi-week project.

**Naming and ID decisions (fixed, do not re-litigate):**

- Model/skin/anim/texture prefix: `TaunkaMale`. Chosen because the M2's internal MD20 name field already reads `TaunkaMale`, so **no binary name patching is required**.
- New display ID: candidate **60008** (the 60000+ band is the Esteria custom band: 60000/60001, 60002/60003, 60004/60005, 60006/60007 are taken). Must be confirmed collision-free by Task 2 before it is written anywhere. Reserve 60008, 60009, 60010.
- Gender value: reuse existing `GENDER_NONE = 2` (`src/server/shared/SharedDefines.h:63`). Do not add a fourth enum value.
- New world table: `player_race_gender_model (race, gender, displayId)`, loaded in the same place `PlayerInfo` is loaded.

## Global Constraints

- **Display ID must be < 65536.** `PlayerInfo::displayId_*` is `uint16` (`src/server/game/Entities/Player/Player.h:331-332`). A larger ID silently truncates. Stated policy at `docker-compose.override.yml:20-33`.
- **Do not replace any existing client entry.** Abort on a same-path, different-byte collision. Tauren male's `Character\Tauren\Male\*` and its `CharSections` sex-0 texture names are immutable.
- **Patch layer is `patch-Z`.** DBCs and Glue must be byte-identical in both `G:\3.3.5a - Dev\Data\patch-Z.MPQ` and `G:\3.3.5a - Dev\Data\enUS\patch-enUS-Z.MPQ`. M2/SKIN/ANIM/BLP assets go in the global `patch-Z.MPQ` **only**. Writing to `patch-A`/`patch-C` "can look correct in static inspection while CharacterCreate still consumes stale global rows" (`docs/CHARACTER_SELECT_HANDOFF.md:104`).
- **Server DBCs are `modules/mod-custom-server/data/dbc/retroported-races/`.** Full-table files, bind-mounted read-only. Do not use `.dbc1` continuations for appearance identity — the same comment at `docker-compose.override.yml:20-33`.
- **Do not configure or build unless explicitly asked.** Do not edit SQL outside `data/sql/updates/pending_db_*/`. `data/sql/base/`, `data/sql/archive/`, `data/sql/updates/db_*/` are immutable.
- **Back up and SHA-256 every external file before writing**, including `Wow.exe`. Always patch from the original verified backup executable, never from an already-patched one.
- **Preserve unrelated dirty worktree changes.** The Taunka pack lives in-repo under `NewModels/`; do not reorganize it.
- **No loose-file overlay in `Data\`.** The WXL wildcard layer scans loose files and a loose overlay directory has previously caused cursor flicker and char-create hitching.

## Review Focus

Reviewer: these are the five ways this plan goes wrong.

1. **A missing anim or skin file.** The client resolves `<modelname><animid>.anim` and `<modelname><profile>.skin` by convention. A single missing file is a frozen or broken animation sequence, not a fallback. Task 3 must produce a completeness proof, not a file count.
2. **Tauren male silently becomes Taunka.** Any new `CharSections` row or texture write that lands on a sex-0 or stock `TaurenMale*.blp` name breaks the two existing bodies. The name-collision test in Task 7 is the gate.
3. **Gender-2 characters flip to male after a shapeshift.** `Unit::SetDisplayId` rewrites the gender byte from `creature_model_info` on *every* display change (`src/server/game/Entities/Unit/Unit.cpp:13186-13192`), and the loader forces any value `> 2` to `GENDER_MALE` (`src/server/game/Globals/ObjectMgr.cpp:1759-1762`). Task 9 must prove a druid/bear form and back returns to 2.
4. **A ternary silently picks the female branch.** ~145 `getGender()` comparison sites exist; value 2 falls into the `else` arm of `== GENDER_MALE ? A : B`. Task 9 enumerates the reachable set — do not "fix" the 125 non-Tauren disguise sites.
5. **Static validation reported as proof.** The Highmountain record reads "contracts pass" alongside "live acceptance remains pending." No DBC hash, contract test, or native harness output demonstrates that a character renders. Task 15 is the only place that claim may be made, and only from live evidence.

---

## Established Facts

Verified against this checkout. Line numbers are current.

**Gender plumbing (server):**

| Fact | Location |
|---|---|
| `Gender { MALE=0, FEMALE=1, NONE=2 }` | `src/server/shared/SharedDefines.h:59-64` |
| `IsValidGender` is `Gender <= GENDER_FEMALE` — the only validator | `src/server/game/Entities/Player/Player.h:1598` |
| Called at create / enum / load / condition-load | `Player.cpp:531`, `Player.cpp:1205`, `PlayerStorage.cpp:5076`, `ConditionMgr.cpp:2221` |
| `InitDisplayIds` switches on gender, `default:` logs an error and returns **without setting a display ID** | `src/server/game/Entities/Player/Player.cpp:10880-10904` |
| `PlayerInfo` has only `displayId_m` / `displayId_f`, both `uint16` | `src/server/game/Entities/Player/Player.h:321-341` |
| Both are filled from `ChrRacesEntry::model_m` / `model_f` — never persisted, no DB column | `src/server/game/Globals/ObjectMgr.cpp:4438-4439`, `src/server/shared/DataStores/DBCStores.h:706-712` |
| `playercreateinfo` has no `sex` and no `displayId` column | `data/sql/base/db_world/playercreateinfo.sql` |
| `Unit::SetDisplayId` overwrites `UNIT_FIELD_BYTES_0[2]` from `creature_model_info.Gender` | `src/server/game/Entities/Unit/Unit.cpp:13186-13192` |
| Loader rejects `Gender > 2`, coercing to `GENDER_MALE` | `src/server/game/Globals/ObjectMgr.cpp:1759-1762` |
| `creature_model_info.Gender` column default is 2 and 2 passes validation | `data/sql/base/db_world/creature_model_info.sql:23-31` |
| Persisted gender is `PLAYER_BYTES_3[0]`, saved from there | `Player.cpp:15210`, loaded `PlayerStorage.cpp:5142` |
| Canonical-gender workaround precedent (shapeshift reads `PLAYER_BYTES_3`) | `src/server/game/Globals/ObjectMgr.cpp:1897-1927`, comment at `:1906` |
| `characters.gender` is `tinyint unsigned` — no schema change needed | `data/sql/base/db_characters/characters.sql:29` |
| `spell_area.gender == 2` already means "unrestricted" — free pass | `src/server/game/Spells/SpellMgr.cpp:1062-1066` |
| `player_shapeshift_model.GenderID == 2` already means "both genders" | `data/sql/base/db_world/player_shapeshift_model.sql` |
| Gender-dependent spell sites that matter for Tauren | `SpellAuraEffects.cpp:2685-2715` (Tauren pairs, ternary), `:5219-5229` and `:5250-5258` (`switch`, `default: break;` = no illusion) |
| Other reachable gender sites | `PlayerGossip.cpp:182,185`; `CharacterHandler.cpp:1582-1592` (barber); `ConditionMgr.cpp:148`; `AchievementMgr.cpp:358-361`; `Player.cpp:635` (CharStartOutfit); `SpellHandler.cpp:760-772` (mirror image); `cs_modify.cpp:959-976`; `cs_misc.cpp:2424` |
| No `item_template.gender` and no server-side item gender gate | `data/sql/base/db_world/item_template.sql`, `src/server/game/Entities/Item/ItemTemplate.h` |
| No server-side animation system exists | core sends only spell anim IDs |

**Client gender axis (DBC schemas, from `modules/mod-worgoblin-high-elf/data/DBC/CSV from DBC/`):**

| Table | Gender column | Consequence |
|---|---|---|
| `ChrRaces` | `MaleDisplayId` / `FemaleDisplayId` only | No third slot. Model path is `Character\{ClientPrefix}\{token}\{ClientFilestring}{token}.M2` and the token is a stock 2-way gender. |
| `CharSections` | `SexID` | Body textures and geoset choices. Must be duplicated for sex 2. |
| `CharacterFacialHairStyles` | `SexID` | Facial hair geosets. |
| `CharHairGeosets` | `SexID` | Scalp/hair geosets. |
| `BarberShopStyle` | `Sex` | Barber options. |
| `CharStartOutfit` | `SexID` | Starting gear. |
| `EmotesTextSound` | `SexID` | Voice/emote audio. |
| `CreatureDisplayInfoExtra` | `DisplaySexID` | Creator randomize defaults, per display ID. |
| `CreatureSoundData` | keyed by `DisplayID` | **A new display ID with no row is silent.** |
| `VocalUISounds` | keyed by `RaceID` | Fine as-is. |

**Asset pack (`NewModels/_Other/PlayableTaunka/`):**

| Fact | Evidence |
|---|---|
| `Non-HD model/Character/Tauren/Male/TaurenMale.M2` is **MD20 version 264** — the TBC/WotLK format 3.3.5a reads | header probe, 1,409,376 bytes |
| The M2 contains 7,126 strings and **zero** `.skin` / `.anim` / `.blp` filenames | same probe |
| Its only embedded name is `TaunkaMale` | same probe |
| ⇒ Skins, anims and body textures are resolved by naming convention off the model file name | the pack works today purely by sitting at `Character\Tauren\Male\TaurenMale*` |
| 16 `TaurenMale*.skin`, 59 `TaurenMale*.anim`, 709 `TaurenMale*.blp` (face upper/lower ×10 each, skin ×10, naked torso/pelvis, `_Extra` variants) | folder inventory |
| 16 `M24BC*.skin` + 44 `M24BC*.anim` are Cata part-file assets, ignored by a 3.3.5a client | Cata naming scheme; see HD gate |
| The 3 DBCs in `Non-HD model/DBFilesClient/` are **Cataclysm 4.x** — `ChrRaces` 21 rows with Cata race IDs, `CreatureDisplayInfoExtra` 15,475 rows, `CharacterFacialHairStyles.SexID` up to 10 | diff against `DBCs/` |
| `Taunka HD models/*.mpq` target Warmane/Ascension per its own `ReadME.txt` | `ReadME.txt` |

**Native layer (`client-customization/`):**

| Fact | Detail |
|---|---|
| 15 exports, index = IAT slot, order load-bearing | `EsteriaCycle`(0) … `EsteriaSectionCount`(14) |
| Race identity in the client's character struct | `+0x18` race, `+0x1C` gender, `+0x38` model instance |
| Character-select roster record | stride `0x198`, character pointer at `+0x188`, redirect `0x004E3E74` |
| Create / enum redirects | `0x006B174C` / `0x00464F89` (`HXE1` trailer, magic `0x31455848`) |
| Extended appearance field | `UNIT_FIELD_PADDING` = `OBJECT_END + 0x008D`; native registers type 3, byte offset `0x234`, size 4 via `0x004D5BA0` |
| `EsteriaHighmountain.bin` | magic `0x314D4845`, v1, 156-byte records, **validates `gender < 2`** (`NativeAppearance.cpp:602`) |
| `EsteriaAppearance.bin` | magic `0x50504145`, **v2**, 64 profiles keyed by race **and gender** |
| `EsteriaAppearanceMaterials.bin` | magic `0x544D4145`, v1, 188-byte records |
| `EsteriaAppearanceGeometry.bin` | magic `0x4D474145`, v1, 128-byte path + SKIN blob |
| The customization index is built from the **full `CharSections.dbc`**, sized from max RaceID — geoset comparison uses the low uint16 ID | README |
| `native_appearance_patch.py` pins `EXPECTED_SHA256 = 2cf5a5cb…e0c409` and 30 per-site byte fingerprints | script |

**Tooling (real flags, no guessing):**

```
python tools/inspect_client_archive.py <archive> [--match SUBSTR] [--extract ENTRY ...] [--out DIR] [--stormlib PATH]
python tools/find_mpq_paths.py <root> <term> [<term> ...] [--recursive]
python tools/wow_xref.py <Wow.exe> xref|calls <hexVA> ...   |   disasm <hexVA> <count>
python tools/native_appearance_patch.py [--source PATH] [--output PATH]
python tools/retroported_race_pack.py {plan|build|validate|install|install-appearance|install-runtime} --race ID
python tools/creator_portrait_layout.py {build|refresh-ui|install} [--client PATH]
python tools/race_portrait_pack.py [--source] [--root-archive] [--backup-dir] [--apply]
```

---

## File Map

| Path | Role in this plan |
|---|---|
| `NewModels/_Other/PlayableTaunka/Non-HD model/Character/Tauren/Male/TaurenMale.M2` | Source M2. Read-only donor. |
| `NewModels/_Other/PlayableTaunka/Non-HD model/Character/Tauren/Male/TaurenMale*.skin/.anim/.blp` | Source binaries. Read-only donors. |
| `NewModels/_Other/PlayableTaunka/Taunka HD models/*.mpq` | HD candidate set. Inspected, then almost certainly rejected. |
| `NewModels/_Other/PlayableTaunka/Non-HD model/DBFilesClient/*.dbc` | Cata 4.x. **Discard.** |
| `modules/mod-custom-server/data/dbc/retroported-races/*.dbc` | Server-side canonical DBCs to modify. |
| `client-customization/NativeAppearance.cpp`, `.def` | Native layer to widen. |
| `client-customization/build-native.bat` | Native build entry. |
| `tools/taunka_gender_pack.py` | **Create.** The packer: extract, fork, rename, DBC row duplication, catalog emission. |
| `tools/test_taunka_gender_contract.py` | **Create.** Contract test for this feature. |
| `data/sql/updates/pending_db_world/rev_*_taunka_gender.sql` | **Create.** `player_race_gender_model` + `creature_model_info` + `CreatureDisplayInfo`-adjacent world rows. |
| `data/sql/updates/pending_db_characters/` | Only if a new column is proven necessary. Expected: none. |
| `src/server/game/Entities/Player/Player.{h,cpp}` | Gender validation, third display slot. |
| `src/server/game/Globals/ObjectMgr.{h,cpp}` | Load `player_race_gender_model`. |
| `src/server/game/Spells/Auras/SpellAuraEffects.cpp` | Gender ternary/switch audit. |
| `src/server/game/Entities/Unit/Unit.cpp` | `SetDisplayId` gender clobber, player path. |
| `src/server/scripts/Commands/cs_modify.cpp`, `cs_misc.cpp` | GM command and `.pinfo` string. |

---

### Task 0: Snapshot and inventory (read-only)

**Files:** Inspect only, all of `NewModels/_Other/PlayableTaunka/`, `G:\3.3.5a - Dev\Data\`.
**Interfaces:** Consumes nothing. Produces an inventory file the rest of the plan cites.

- [ ] **Step 1: Record SHA-256 of every pack file and every `Wow.exe`/MPQ that will be touched.** Write the manifest to `.agents/plans/tauren-third-gender/evidence/manifest.txt`. Nothing is modified in this task.

- [ ] **Step 2: Inventory the effective live DBCs, not the repo copies.**

```
python tools/audit_effective_character_dbcs.py
```
Expected: Tauren's stock display pair, and confirmation of which archive copy actually wins per table. Treat `DBCs/` in the repo root as non-authoritative.

- [ ] **Step 3: Enumerate Tauren male's complete client-side file set.**

```
python tools/find_mpq_paths.py "G:\3.3.5a - Dev\Data" "TaurenMale" --recursive
```
Expected: a complete list of `TaurenMale*.m2`, `TaurenMale*.skin`, `TaurenMale*.anim`, `TaurenMale*.blp` entries with their archive and internal path. This list is the completeness oracle for Task 3.

- [ ] **Step 4: Record the Tauren anim-ID coverage of the pack.** 59 pack anims versus Tauren male's full set. Write the missing-ID list to `evidence/anim-gaps.txt`. A gap is a frozen animation, not a fallback.

- [ ] **Step 5: Record which live patch layer each needed file currently lives in**, to predict Task 13's staging cost.

Run: all four steps above, no writes outside `evidence/`.
Expected: four evidence files exist; Tauren's stock display pair and the anim gap list are known numbers before any code exists.

---

### Task 1: HD gate — decide whether the HD set is usable

**Files:** Inspect only: `NewModels/_Other/PlayableTaunka/Taunka HD models/*.mpq`, `Non-HD model/patch-4.mpq`, `Patch-Z/Patch-Z.mpq`.
**Interfaces:** Consumes Task 0 manifest. Produces a written ruling that Tasks 2+ depend on.

The pack is named "HD" and the request is for the HD files. The evidence says the HD MPQs are not WotLK assets. Resolve it explicitly rather than assuming.

- [ ] **Step 1: List the contents of every MPQ in the pack.**

```
python tools/inspect_client_archive.py "NewModels\_Other\PlayableTaunka\Taunka HD models\patch-A.mpq" --match .m2
python tools/inspect_client_archive.py "NewModels\_Other\PlayableTaunka\Taunka HD models\patch-A.mpq" --match M24BC
```
Repeat for `Patch-B.MPQ`, `Patch-F.MPQ`, `Patch-G.MPQ`, `Patch-k.mpq`, `Patch-T.mpq`, `patch-U.mpq`.

- [ ] **Step 2: Classify each archive.** An archive is WotLK-usable only if every model entry is MD20 v264 **and** no entry uses the Cata `M24BC*` part-file naming. Record the ruling per archive.

- [ ] **Step 3: Apply the decision rule.**
  - **If any archive is MD20 v264 and Tauren/Taunka-scoped** → it is a superset of the Non-HD set; prefer it as the donor for Task 3 and record which extra files it carries.
  - **If all HD archives are MD21 or `M24BC*`-scoped** → they target a Cata-era client. **Reject them**, plan the Non-HD set as the shipping body, and record the ruling. The `M24BC*` files in the Non-HD folder are rejected on the same grounds.

- [ ] **Step 4: Write the ruling to `evidence/hd-ruling.md` with a cost-if-wrong note.**

Run: the `inspect_client_archive.py` calls above.
Expected: `evidence/hd-ruling.md` exists and names exactly one donor set. No MPQ is modified.

---

### Task 2: Allocate the display ID and prove it is free

**Files:** Inspect only: `G:\3.3.5a - Dev\Data\**`, `modules/mod-custom-server/data/dbc/retroported-races/*.dbc`.
**Interfaces:** Consumes Task 1 donor ruling. Produces the display ID used by Tasks 5, 9, 13.

- [ ] **Step 1: Audit the candidate band for collisions across every archive and the server DBCs.**

```
python tools/diagnose_ascension_hd_collisions.py
python tools/audit_reforged_custom_collisions.py
```
Expected: 60008, 60009, 60010 are unclaimed as display IDs, model IDs, and `CreatureModelData` IDs.

- [ ] **Step 2: If any candidate is taken, walk upward to the next free ID** and record the allocation. Never reuse an ID that appears in any archive, including backups.

- [ ] **Step 3: Assert the allocation is < 65536.** If a free ID cannot be found below 65536, **stop and escalate** — the `uint16` display slot is a hard architectural limit, and the answer becomes a new race ID instead of a third gender.

- [ ] **Step 4: Write the allocation to `evidence/display-id.txt`.**

Run: both audit scripts.
Expected: one allocated display ID, provably unused, below 65536.

---

### Task 3: M2 and skin-profile feasibility gate

**Files:** Inspect only: the donor M2, Tauren male's stock M2. Create: `tools/taunka_gender_pack.py` (anatomy only, no output).
**Interfaces:** Consumes Tasks 0–2. Produces the go/no-go for the "borrow Tauren cosmetics" decision.

This is the gate that decides whether the DBC work is a small row duplication or a large one. **Do not proceed past a no-go.**

- [ ] **Step 1: Parse the M2 header and record:** magic/version, skin-profile count, geoset count and each geoset's ID and vertex count, bone count, texture-replaceable count, bounding radius, and the 64-byte internal name.

- [ ] **Step 2: Compare against Tauren male's stock M2** from the archive found in Task 0.

- [ ] **Step 3: Assert the skin-profile count matches Tauren male's.** If the Taunka M2 declares more or fewer profiles than Tauren male has `TaurenMale*.skin` files, the convention-based profile index will desync and cosmetics will composite wrongly. A mismatch here forces authoring the missing profiles, which is out of this plan's scope — **stop and report.**

- [ ] **Step 4: Assert geoset ID compatibility.** Tauren male's `CharSections` sex-0 rows index geosets by ID. If the Taunka M2's geoset set contains Tauren male's IDs at the same indices, cosmetics compose as-is. Record any geoset present in one model and absent in the other, in both directions.

- [ ] **Step 5: Record the 65535-vertex check.** Compare prepared vertex counts against the Wrath limit; the Highmountain models already run 64,136 / 56,344, so headroom is known to be tight.

- [ ] **Step 6: Write the verdict to `evidence/m2-gate.md`:** `BORROW` (proceed with sex-0 geoset data reused for sex 2) or `DUPLICATE-WHOLE-SET` (every sex-0 row must be authored for sex 2 — re-estimate before continuing).

Run: `python tools/taunka_gender_pack.py anatomy --m2 <path> --compare <path>`
Expected: `evidence/m2-gate.md` with an explicit `BORROW` or `DUPLICATE-WHOLE-SET`.

---

### Task 4: Add the failing contract test

**Files:** Create `tools/test_taunka_gender_contract.py`.
**Interfaces:** Consumes the evidence files from Tasks 0–3. Produces the red test every later task must turn green.

Follow the house pattern (`tools/test_darkfallen_contract.py`, `tools/test_native_appearance.py`): `main()` + `unittest`, no flags, read-only assertions, pinned paths.

- [ ] **Step 1: Write the assertions.** Each must be individually named and independently fixable:
  1. `Player::IsValidGender` admits 2 for race 6.
  2. `PlayerInfo` has a third display slot and it is populated for race 6.
  3. `InitDisplayIds` has an explicit gender-2 arm with no `default:`-returns-nothing path.
  4. `Unit::SetDisplayId` does not overwrite the gender byte for players.
  5. `creature_model_info` has a row for the allocated display ID with `Gender = 2` and non-zero bounding radius and combat reach.
  6. `player_race_gender_model` has a `(6, 2, <displayId>)` row and the migration is idempotent.
  7. Tauren male's `CharSections` sex-0 rows are **byte-identical** to the pre-change baseline.
  8. The staged client carries a sex-2 `CharSections` row set whose `TextureName_*` all begin `TaunkaMale`.
  9. No `TaurenMale*.blp` entry in any archive was rewritten (hash comparison against the Task 0 manifest).
  10. Every `TaunkaMale<animid>.anim` the client can request for race 6 exists in the staged global `patch-Z`.
  11. Every `TaunkaMale<NN>.skin` for `NN` in the M2's profile count exists.
  12. `CreatureSoundData` has a row for the allocated display ID.
  13. `CharStartOutfit` has race-6 sex-2 rows for all nine classes.
  14. Both Z archives carry byte-identical DBCs and Glue.
  15. Native catalogs admit gender 2 (the `gender < 2` check is widened, not deleted).

- [ ] **Step 2: Run it and confirm every assertion is red for the right reason** — a missing feature, not a broken test.

Run: `python tools/test_taunka_gender_contract.py -v`
Expected: all 15 fail. Any pass before implementation is a defective assertion — fix the test first.

---

### Task 5: Server — admit gender 2 and add the third display slot

**Files:**
- Modify: `src/server/shared/SharedDefines.h` (comment on `GENDER_NONE`, no new value)
- Modify: `src/server/game/Entities/Player/Player.h` at `IsValidGender` and `PlayerInfo`
- Modify: `src/server/game/Entities/Player/Player.cpp` at `InitDisplayIds`
- Modify: `src/server/game/Globals/ObjectMgr.{h,cpp}` — new loader beside `LoadPlayerInfo`

**Interfaces:**
- Consumes: allocated display ID (Task 2), `player_race_gender_model` (Task 6).
- Produces: `PlayerInfo::displayId_n` (`uint16`), `ObjectMgr::GetPlayerGenderModel(race, gender)`.

- [ ] **Step 1: Widen `IsValidGender` to admit 2.** Keep the upper bound; do not add a third enum value.

- [ ] **Step 2: Add `uint16 displayId_n` to `PlayerInfo`**, and populate it in `LoadPlayerInfo` (`ObjectMgr.cpp:4354-4447`) from the new table, defaulting to `displayId_m` when no row exists so every other race is untouched.

- [ ] **Step 3: Give `InitDisplayIds` an explicit gender-2 arm** and remove the `default:`-returns-nothing behavior at `Player.cpp:10900-10902`. A malformed gender must now log **and** fall back to a valid display ID, not leave the player display-less.

- [ ] **Step 4: Load `player_race_gender_model`** as a `std::unordered_map<std::pair<uint8,uint8>, uint16>` beside the existing `_playerInfo` map, with the same prepared-statement and error-logging conventions.

- [ ] **Step 5: Turn contract assertions 1, 2 and 3 green.**

Run: `python tools/test_taunka_gender_contract.py -v` (assertions 1–3)
Expected: 1–3 pass, 4–15 still red.

---

### Task 6: Server — the pending world migration

**Files:** Create `data/sql/updates/pending_db_world/rev_*_taunka_gender.sql`.
**Interfaces:** Consumes: display ID (Task 2). Produces: the two tables Task 5 reads.

- [ ] **Step 1: Create `player_race_gender_model`** — `(race TINYINT UNSIGNED, gender TINYINT UNSIGNED, displayId INT UNSIGNED, PRIMARY KEY (race, gender))`. Follow the shape and comment style of `data/sql/base/db_world/player_shapeshift_model.sql`.

- [ ] **Step 2: Insert `(6, 2, <displayId>)`.** Insert no other rows. Add `gender <= 2` as a check or document the bound in a comment.

- [ ] **Step 3: Insert the `creature_model_info` row** for the display ID: `Gender = 2`, `BoundingRadius` and `CombatReach` copied from Tauren male's stock display entry. This is what makes `Unit::SetDisplayId` write 2 rather than a race-dependent value (`ObjectMgr.cpp:1759-1762` accepts 2 as the permissive default).

- [ ] **Step 4: Make the migration idempotent** — `INSERT ... ON DUPLICATE KEY UPDATE` or delete-then-insert. Audit scripts probe pending migrations for idempotency.

- [ ] **Step 5: Touch no other table.** No `characters` mutation. No `item_template` change — there is no gender column.

Run: `python tools/test_taunka_gender_contract.py -v` (assertions 5, 6)
Expected: 5–6 pass.

---

### Task 7: Client DBCs — duplicate the sex-keyed rows

**Files:**
- Modify: `modules/mod-custom-server/data/dbc/retroported-races/CharSections.dbc`, `BarberShopStyle.dbc`, `CharStartOutfit.dbc`, `CreatureDisplayInfo.dbc`, `CreatureModelData.dbc`, `ChrRaces.dbc` (if needed)
- Modify: the same tables staged into both Z archives
- Modify only if the Task 3 gate says `DUPLICATE-WHOLE-SET`: `CharacterFacialHairStyles`, `CharHairGeosets`

**Interfaces:** Consumes: `evidence/m2-gate.md`, Task 0 inventory. Produces: sex-2 rows for race 6.

- [ ] **Step 1: Extract Tauren male's sex-0 row set from the live `CharSections.dbc`** for race 6: every section type, every variation index, every color index.

- [ ] **Step 2: Emit a sex-2 copy of each row** with a fresh row ID, **preserving the `Geoset`/`Variation`/`Color` values verbatim** and rewriting only `TextureName_1/2/3` to the `TaunkaMale*` equivalents. Never mutate a sex-0 row.

- [ ] **Step 3: Map every texture name.** The 709 pack textures are named `TaurenMale{Region}{NN}_{CC}.blp`; each becomes `TaunkaMale{Region}{NN}_{CC}.blp`. Enumerate the full list and assert a 1:1 mapping with no unmapped and no orphaned source texture.

- [ ] **Step 4: Duplicate `BarberShopStyle` race-6 sex-0 rows as sex 2**, and add race-6 sex-2 `CharStartOutfit` rows for all nine classes, copying the sex-0 item lists.

- [ ] **Step 5: Add `CreatureDisplayInfo` and `CreatureModelData` rows** for the display ID, mirroring Tauren male's values.

- [ ] **Step 6: Decide `CreatureDisplayInfoExtra` deliberately.** Its `DisplaySexID` feeds the creator's randomize. Try `DisplayRaceID = 6, DisplaySexID = 2` first; if the stock randomize misbehaves, set `DisplaySexID = 0` and let the native layer override on selection. Record which was chosen and why.

- [ ] **Step 7: Do not add a `ChrRaces` row.** The third gender is not a race. `ChrRaces` has two display columns and stays untouched; the path and display ID come from the native layer.

- [ ] **Step 8: Preserve all non-owned rows and grow the string block monotonically** — `changed.strings.startswith(original.strings)`, the invariant `test_native_appearance.py` enforces.

- [ ] **Step 9: Turn contract assertions 7, 8, 13 green.** Assertion 7 is the regression gate: Tauren male's rows must be byte-identical to the Task 0 baseline.

Run: `python tools/test_taunka_gender_contract.py -v` (assertions 7, 8, 13)
Expected: 7–8 and 13 pass. If assertion 7 fails, stop — a sex-0 row was mutated.

---

### Task 8: Client — sound rows for the new display ID

**Files:** Modify `CreatureSoundData.dbc` (client + server if mounted), `EmotesTextSound.dbc`.
**Interfaces:** Consumes: display ID. Produces: audible third gender.

- [ ] **Step 1: Add a `CreatureSoundData` row keyed to the new display ID**, copying Tauren male's sound IDs. Without this the body is **silent** — footsteps, combat, death, fidget all missing — because the table is keyed by `DisplayID`, not by race.

- [ ] **Step 2: Add race-6 sex-2 `EmotesTextSound` rows**, or set `SexID = 2` handling to fall back to sex 0. Record which. A third-gender player who cannot emit voice grunts is a visible defect.

- [ ] **Step 3: Leave `VocalUISounds` alone** — it is race-keyed and race 6 already has Tauren rows.

Run: `python tools/test_taunka_gender_contract.py -v` (assertion 12)
Expected: 12 passes.

---

### Task 9: Server — the gender-branch audit

**Files:** Modify only where proven necessary: `SpellAuraEffects.cpp`, `PlayerGossip.cpp`, `CharacterHandler.cpp`, `ConditionMgr.cpp`, `AchievementMgr.cpp`, `Player.cpp`, `Unit.cpp`, `SpellHandler.cpp`, `cs_modify.cpp`, `cs_misc.cpp`.

**Interfaces:** Consumes: gender 2 admitted (Task 5). Produces: no silent female-branch fallthrough for race 6.

- [ ] **Step 1: Enumerate the reachable set, do not blanket-patch.** Only these sites are reachable by a gender-2 Tauren. 125 of the ~190 `getGender()` hits are in `SpellAuraEffects.cpp` for Blood Elf/Orc/Troll/Undead disguises and are **out of scope**.

| Site | Failure mode at value 2 |
|---|---|
| `SpellAuraEffects.cpp:2685-2715` | ternary → female model |
| `SpellAuraEffects.cpp:5219-5229`, `:5250-5258` | `default: break;` → no illusion at all |
| `Player.cpp:635` + `DBCStores.cpp:880` | no `CharStartOutfit` row → no starting gear (covered by Task 7) |
| `CharacterHandler.cpp:1582-1592` | barber rejects → covered by Task 7 |
| `PlayerGossip.cpp:182,185` | wrong gendered text variant |
| `ConditionMgr.cpp:148` | `CONDITION_GENDER` never matches 2 |
| `AchievementMgr.cpp:358-361` | gender criteria unreachable |
| `SpellHandler.cpp:760-772` | mirror image reports gender 2 (cosmetic only) |
| `cs_misc.cpp:2424` | `.pinfo` prints "Female" |
| `cs_modify.cpp:959-976` | `.modify gender` cannot set 2 |

- [ ] **Step 2: Fix the clobber at `Unit::SetDisplayId` (`Unit.cpp:13186-13192`).** With the Task 6 `creature_model_info` row the write is already 2 for this display, but any *shapeshift* writes that form's gender instead. Adopt the existing `ObjectMgr.cpp:1906` precedent: treat `PLAYER_BYTES_3[0]` as canonical and stop deriving character gender from the active display model.

- [ ] **Step 3: Add a regression assertion** that a stored gender-2 character survives druid bear form (7090 → 29414) and returns to 2, and that Wild Form (22836) resolves through `player_shapeshift_model` with the `GenderID = 2` "both genders" fallback.

- [ ] **Step 4: Turn contract assertion 4 green.**

Run: `python tools/test_taunka_gender_contract.py -v` (assertion 4)
Expected: 4 passes; assertion 3's shape-shift clause passes.

---

### Task 10: Extract and fork the assets

**Files:** Create `tools/taunka_gender_pack.py` fork stage; output staged under `G:\3.3.5a - Dev\Data\Staging\`.
**Interfaces:** Consumes: Task 1 donor ruling, Task 3 gate. Produces: the `TaunkaMale*` file tree.

- [ ] **Step 1: Extract the donor M2 and its files from the chosen archive set.** Use `inspect_client_archive.py --extract ... --out`, or copy from the loose Non-HD folder when Task 1 selected it.

- [ ] **Step 2: Copy Tauren male's full `.skin` and `.anim` set from the live archives** (Task 0 list) and rename each to the `TaunkaMale` prefix. The 59 retuned pack anims overwrite their same-numbered Tauren counterparts **after** the copy. This ordering is the whole trick: Tauren anims for completeness, pack anims for the Taunka feel.

- [ ] **Step 3: Copy and rename all 709 textures.** Do not move; Tauren male keeps its originals.

- [ ] **Step 4: Copy the M2 to `Character\Taunka\Male\TaunkaMale.M2`.** Verify the internal name field already reads `TaunkaMale`. If it does not, stop — the plan's no-patch assumption is void and this becomes a binary string edit with a length check.

- [ ] **Step 5: Prove completeness against Task 0's list:** every anim ID Tauren can request, every skin profile index, every referenced texture. Emit `evidence/fork-manifest.txt` with expected-vs-present counts and zero gaps.

- [ ] **Step 6: Assert zero byte-level change to any `TaurenMale*` file.**

Run: `python tools/taunka_gender_pack.py fork --donor <path> --client "G:\3.3.5a - Dev" --stage`
Expected: `evidence/fork-manifest.txt` with zero gaps and zero modified `TaurenMale*` files.

---

### Task 11: Native — widen the gender domain

**Files:** Modify `client-customization/NativeAppearance.cpp`, `NativeAppearance.def`.
**Interfaces:** Consumes: Task 2 display ID, Task 3 gate. Produces: gender 2 accepted by the native layer.

- [ ] **Step 1: Widen the catalog gender checks.** `NativeAppearance.cpp:602` validates `gender < 2`; `EsteriaAppearance.bin` v2 profiles are keyed by race **and gender** and are capped at 64. Decide and record: bump `EsteriaAppearance.bin` to **v3** with a widened domain, or emit gender-2 records into a new sibling catalog. Bumping a version invalidates existing Highmountain/Skyborne state, so the safer default is a **new sibling catalog** and a version bump only if the 64-profile cap is genuinely hit.

- [ ] **Step 2: Supply the model path.** The stock client builds `Character\{ClientPrefix}\{token}\{ClientFilestring}{token}.M2` with a two-way gender token. Add a redirect at the path-construction site that, for race 6 + gender 2, returns `Taunka\Male\TaunkaMale.M2` and the display ID from Task 2. The customization lookups (`EsteriaDirectSection`, `EsteriaSectionArguments`, `EsteriaSectionCount`) are the existing hook points.

- [ ] **Step 3: Reverse-engineer the sex dimension before assuming it.** Use `tools/wow_xref.py <Wow.exe> xref <hexVA>` / `disasm` on the customization-index builder. If the sex dimension is a fixed 2-entry array, an unchecked `sex = 2` writes out of bounds — **this is the single highest-risk unknown in the plan.** If it cannot be widened safely, escalate: the alternative is a new race ID, not a third gender.

- [ ] **Step 4: Do not add a new `.eapp` redirect site** without updating the per-site fingerprint table in `native_appearance_patch.py`; it raises `Patch-site fingerprint differs` on any mismatch, and the export order is IAT-indexed and load-bearing.

- [ ] **Step 5: Build and run both harnesses.**

```
rtk proxy cmd /c client-customization\build-native.bat C:\Users\Zach\.codex\tmp\taunka-gender
```
Expected: `TestNativeAppearance.exe` and `TestHighmountainMaterials.exe` pass; `TestHighmountainMaterials` needs `/DYNAMICBASE:NO /BASE:0x04000000`.

- [ ] **Step 6: Patch a copy of the exe from the original verified backup** and confirm all 30 existing site fingerprints still match.

```
python tools/native_appearance_patch.py --source "G:\3.3.5a - Dev\Wow.exe" --output "C:\Users\Zach\.codex\tmp\taunka-gender\Wow.exe"
```

- [ ] **Step 7: Turn contract assertion 15 green.**

Run: `python tools/test_native_appearance.py` and `python tools/test_taunka_gender_contract.py -v` (assertion 15)
Expected: both pass, and every existing Highmountain/Skyborne profile still round-trips.

---

### Task 12: Glue — third creator control and portraits

**Files:** Modify `Interface/GlueXML/CharacterCreate.lua`, `CharacterCreate.xml`, `CharacterSelect.lua`, `CharacterSelect.xml`; staged into **both** Z archives byte-identically.
**Interfaces:** Consumes: display ID, Task 7 rows. Produces: a selectable third option that survives relog.

- [ ] **Step 1: Add the third control.** Existing code string-switches `"MALE"`/`"FEMALE"` in three places (`CharacterCreate.lua:207-215`, `:299-303`, `:434-466`). Extend to a three-way token. Do not reuse the literal `"NONE"`.

- [ ] **Step 2: Add `RACE_ICON_TCOORDS` entries** for the third gender. Watch the known trap: `re.sub` in the icon generator eats doubled backslashes in these keys.

- [ ] **Step 3: Lay the control out.** `tools/creator_portrait_layout.py {build|refresh-ui|install}`. The Highmountain creator occupies two columns; verify the third control does not overlap or reflow existing races.

- [ ] **Step 4: Add portraits** via `tools/race_portrait_pack.py --apply`, masked inside the existing ECS border.

- [ ] **Step 5: Make the select screen round-trip gender 2.** The client caches appearance locally; a third value that does not persist shows the wrong body at selection after relog. The select record is stride `0x198` with the character pointer at `+0x188` and gender at `+0x1C`; the existing `EsteriaSelectExtra` redirect at `0x004E3E74` is the hook.

- [ ] **Step 6: Keep `CharacterSelect.lua` and `CharacterSelect.xml` virtual-scroll behavior intact.** Do not regress the contract that both Z archives' `OnKeyDown` handles DOWN/RIGHT without `arg1`.

- [ ] **Step 7: Turn contract assertion 14 green.**

Run: `python tools/test_character_select_contract.py`, `python tools/test_login_persistence_contract.py`, `python tools/test_character_limit_contract.py`
Expected: all three pass; the new Glue is byte-identical across both Z archives.

---

### Task 13: Stage and install

**Files:** `G:\3.3.5a - Dev\Data\patch-Z.MPQ`, `...\enUS\patch-enUS-Z.MPQ`; `modules/mod-custom-server/data/dbc/retroported-races/`.
**Interfaces:** Consumes: everything above. Produces: a live client and a rebuilt `ac-worldserver`.

- [ ] **Step 1: Follow the documented staging sequence** (`docs/RETROPORTED_RACES_IMPLEMENTATION.md` §5.4): hash → timestamped backup → merge assets into staged global Z → merge DBCs into staged global Z → merge the **same** DBC bytes into staged locale Z → patch Glue in both → read back every entry → reopen every WDBC and validate header, row count and string offsets → only then install.

- [ ] **Step 2: Assets into global `patch-Z` only.** DBCs and Glue into both, byte-identical.

- [ ] **Step 3: Copy the server DBCs to `modules/mod-custom-server/data/dbc/retroported-races/`** and extend the bind mounts in `docker-compose.override.yml` only if a new table file is added.

- [ ] **Step 4: Import the pending migrations** and rebuild `ac-worldserver` only — never the whole image, to preserve Docker volumes.

- [ ] **Step 5: Confirm server readiness with no DBC load errors**, and that the startup log shows the expected continuation/overlay lines.

- [ ] **Step 6: Confirm staged client and server DBC hashes match** for all seven mounted tables.

Run: `python tools/test_taunka_gender_contract.py -v` (assertions 9, 10, 11)
Expected: 9–11 pass — no `TaurenMale*` file rewritten, no anim gap, no skin gap.

---

### Task 14: Full regression sweep

**Files:** none modified.
**Interfaces:** Consumes: installed state. Produces: a green baseline.

- [ ] **Step 1: Run the mandatory regression set** (`docs/RETROPORTED_RACES_IMPLEMENTATION.md` §6.9):

```
python tools/test_character_select_contract.py
python tools/test_character_limit_contract.py
python tools/test_freeborn_team_pack.py
python tools/test_broken_client_contract.py
python tools/test_playable_race_contract.py
```

- [ ] **Step 2: Run the appearance and race suites:** `test_native_appearance.py`, `test_playable_race_pack.py`, `test_darkfallen_contract.py`, `test_retroported_race_contract.py`, `test_highmountain_race_pack.py`, `test_mechagnome_race_pack.py`, `test_race_touchup_pack.py`, `test_race_portrait_pack.py`, `test_skyborne_visual_pack.py`, `test_two_names_contract.py`.

- [ ] **Step 3: Run `test_taunka_gender_contract.py` in full.** All 15 green.

- [ ] **Step 4: Re-run `audit_effective_character_dbcs.py` and `audit_reforged_custom_collisions.py`** and confirm the new rows win from `patch-Z` and collide with nothing.

Expected: zero failures. Any failure here is a blocker, not a known-issue.

---

### Task 15: Final verification and evidence report

**Files:** Create `evidence/acceptance.md`.
**Interfaces:** Consumes: all prior tasks. Produces: the only artifact permitted to make acceptance claims.

- [ ] **Step 1: Live-client acceptance, fresh client, no cached state.** Every item is required; static checks prove none of them:
  1. Create a gender-2 Tauren of each class; body is Taunka, horns/fur correct.
  2. Create a gender-0 and gender-1 Tauren; **both are byte-for-byte unchanged** from the pre-change baseline.
  3. Full creator randomization, all color variants, facial hair, hair.
  4. Full armor set: shoulders, chest, legs, boots, gloves, waist, plus cloaks and helmets with `HelmetGeosetVisData` attachment.
  5. Weapons in hand, two-hander, ranged, shield.
  6. Every animation: idle, walk, run, swim, jump, combat idle, melee swings, ranged fire, sit, kneel, swim, dance, emotes, death, resurrection.
  7. Voice and footsteps present (Task 8) — not silent.
  8. Mounts, vehicles, flight, and Tauren Wild Form / Animal Form round-trip back to gender 2.
  9. First login, relog, character select, Nearby players' view.
  10. Barber shop.
  11. Tauren racials, Weapon Totem, War Stomp, Mail Specialization — no regression.
  12. Mail, auction house, vendor, guild, party, Who list, name-query responses.
  13. Level-1 start outfit correct.
  14. Two clients side by side, both directions.

- [ ] **Step 2: Record SHA-256 of every installed artifact** and the exact build hashes of `ac-worldserver` and the patched `Wow.exe`.

- [ ] **Step 3: Write `evidence/acceptance.md` stating plainly which of the 14 items were observed and which were not.** Follow the Highmountain precedent, which recorded passing contracts alongside "live acceptance remains pending" — that honesty is the point.

Run: the live checklist.
Expected: `evidence/acceptance.md` exists and does not overstate what was verified.

---

## Rollback

Fully reversible, and cheap, because nothing existing is modified:

1. Restore `patch-Z.MPQ` and `enUS\patch-enUS-Z.MPQ` from the Task 0 timestamped backups.
2. Restore the original verified `Wow.exe` (never re-patch a patched binary).
3. Revert `docker-compose.override.yml` and the seven DBCs in `modules/mod-custom-server/data/dbc/retroported-races/`.
4. Revert the C++ commit and rebuild `ac-worldserver` only.
5. Delete the staged `TaunkaMale*` tree.
6. Gender-2 characters already created keep a `characters.gender = 2` row. If the feature is withdrawn, that is harmless — `BuildEnumData` will refuse to build enum data for them (`Player.cpp:1205`) and they will simply not appear on the select screen. No data repair is required; do not mass-`UPDATE characters`.

## Handoff

Report build, test, import, and live-client status exactly. No build, SQL import, client DBC smoke, or live character-creation claim is valid unless it was actually run.

Two things a reader of this plan must not conclude without evidence:

- The asset is **not** a unique third bodytype. It is a unique body and unique textures on Tauren's rig, animation set, cosmetic space, and voice. That gap is deliberate and scoped in the table above.
- The highest-risk item is **Task 11 Step 3** — whether the client's customization index can accept a third sex value at all. Everything else is mechanical. If that answer is no, the correct outcome is a new race ID, not a forced third gender.
