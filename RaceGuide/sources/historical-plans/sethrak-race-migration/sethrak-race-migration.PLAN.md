# Sethrak Race Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Worgoblin module's playable Ogre presentation with Sethrak assets from the supplied patch-D.mpq while retaining numeric race slot 15 for compatibility.

**Architecture:** Keep ID 15 and the existing server-side gameplay contract, but make Sethrak the visible race and client asset namespace. Extract the supplied MPQ into the module's exploded patch-A.MPQ source tree, rename/repath model, animation, texture, and voice assets, and update project-owned DBC/SQL data without overwriting Draenei assets.

**Tech Stack:** PowerShell, MPQ archive tooling, WotLK 3.3.5a M2/BLP/WAV assets, AzerothCore DBC SQL, JSON.

**Spec:** Approved in chat on 2026-09-03.

## Global Constraints

- Preserve numeric race ID 15 and the internal `RACE_OGRE` compatibility symbol.
- Do not leave the Sethrak asset package dependent on `Character\\Draenei` or `Sound\\Character\\Draenei` paths.
- Preserve existing race faction, classes, start profile, skills, PlayerBot compatibility, and NPC Ogre assets.
- Do not reuse model-data IDs 4892/4893 because custom cars already reserve them.
- SQL edits belong in `data/sql/updates/pending_db_world/` unless they are project-owned module data already under the custom module.
- Do not configure or build; validate with static asset, DBC/SQL, namespace, and diff checks.

### Task 1: Prepare Sethrak asset namespace

**Files:**
- Create: `modules/mod-worgoblin-high-elf/data/patch-A.MPQ/Character/Sethrak/`
- Create: `modules/mod-worgoblin-high-elf/data/patch-A.MPQ/Creature/Sethrak/` only if embedded paths are normalized
- Create: `modules/mod-worgoblin-high-elf/data/patch-A.MPQ/Sound/Character/SethrakMalePC/`
- Create: `modules/mod-worgoblin-high-elf/data/patch-A.MPQ/Sound/Character/SethrakFemalePC/`
- Source: `R:\Users\Zach\Downloads\Sethrak_for_Draenei_female_&_male+voice_attack,deatk_etc._v3\\patch-D.mpq`

- [ ] Extract patch-D.mpq to a temporary audit directory without modifying the source archive.
- [ ] Copy male/female model, skin, animation, and required texture assets into Sethrak-named target paths.
- [ ] Keep model basename and external animation basename consistent after renaming.
- [ ] Copy the 42 WAV files into Sethrak-specific paths and rewrite their logical filenames for DBC mapping.
- [ ] Verify no generated Sethrak asset path contains `Draenei`.

### Task 2: Convert the Worgoblin F-033 owner data

**Files:**
- Modify: `modules/mod-worgoblin-high-elf/modpaks/F-033_mod-playable-ogres/dbc/[BASE,F-033]_chrraces.sql`
- Modify: `modules/mod-worgoblin-high-elf/modpaks/F-033_mod-playable-ogres/dbc/[BASE,F-033]_creaturemodeldata.sql`
- Modify: `modules/mod-worgoblin-high-elf/modpaks/F-033_mod-playable-ogres/dbc/[BASE,F-033]_creaturedisplayinfo.sql`
- Modify: `modules/mod-worgoblin-high-elf/modpaks/F-033_mod-playable-ogres/dbc/[BASE,F-033]_creaturedisplayinfoextra.sql`
- Modify: `modules/mod-worgoblin-high-elf/modpaks/F-033_mod-playable-ogres/dbc/[BASE,F-033]_charsections.sql`
- Modify: `modules/mod-worgoblin-high-elf/modpaks/F-033_mod-playable-ogres/dbc/[BASE,F-033]_charbaseinfo.sql`
- Modify: `modules/mod-worgoblin-high-elf/modpaks/F-033_mod-playable-ogres/dbc/[BASE,F-033]_charstartoutfit.sql`
- Modify: `modules/mod-worgoblin-high-elf/modpaks/F-033_mod-playable-ogres/sql/db-world/base/` Sethrak-facing labels and texture paths

- [ ] Rename visible race labels and source-owned variables/comments from Ogre to Sethrak while retaining ID-15 semantics.
- [ ] Set `ClientPrefix`/`ClientFilestring` to the Sethrak namespace and point model records at collision-free Sethrak model-data/display records.
- [ ] Replace Ogre skin/face texture paths with Sethrak paths and disable unsupported hair/facial selections rather than referencing missing textures.
- [ ] Retain all current class/start/skill/action/stat behavior under race ID 15.
- [ ] Preserve NPC Ogre paths and records outside the playable race owner.

### Task 3: Update project-owned race registry and server DBC data

**Files:**
- Modify: `modules/mod-custom-server/data/races/race_registry.json`
- Modify: `modules/mod-custom-server/data/sql/db-world/updates/dbc/chrraces_dbc.sql`
- Modify: `modules/mod-custom-server/data/sql/db-world/updates/dbc/creaturemodeldata_dbc.sql`
- Modify: `modules/mod-custom-server/data/sql/db-world/updates/dbc/creaturedisplayinfo_dbc.sql`
- Modify: `modules/mod-custom-server/data/sql/db-world/updates/dbc/creaturedisplayinfoextra_dbc.sql`
- Create: `data/sql/updates/pending_db_world/rev_<timestamp>.sql` only for required main-repository world updates

- [ ] Change the registry's race-15 species key/display/source ownership to Sethrak.
- [ ] Preserve the server-side faction and class contract.
- [ ] Resolve all model/display ID collisions against custom cars and existing DBC rows before choosing IDs.
- [ ] Keep server DBC records synchronized with the Worgoblin modpak records.

### Task 4: Character creator and voice integration

**Files:**
- Modify: `modules/mod-worgoblin-high-elf/data/patch-A.MPQ/Interface/GLUES/CHARACTERCREATE/UI-CharacterCreate-Races.blp` if the existing atlas is editable
- Modify: relevant character creator XML/atlas source if present
- Modify: voice-related project-owned DBC SQL rows

- [ ] Use the supplied v2.2 character-creator atlas/icon as the visual source for the existing race-15 button.
- [ ] Keep the existing button slot and selection flow; change only its label/portrait to Sethrak.
- [ ] Map male/female attack, wound, crit, pre-aggro, and death sounds to Sethrak-specific sound paths.
- [ ] Verify no final Sethrak voice record points to Draenei paths.

### Task 5: Static verification

- [ ] Validate MPQ extraction/repack entry names, sizes, and representative M2/BLP/WAV signatures.
- [ ] Validate DBC/SQL race-15 rows, model paths, display references, sound references, and collision-free IDs.
- [ ] Search final Sethrak-owned assets/data for `Draenei` and report only provenance documentation if any remains.
- [ ] Run `python apps/codestyle/codestyle-sql.py` if new main-repository SQL is created.
- [ ] Run `git diff --check` in the main repository and `git diff --check` in the nested Worgoblin repository.
- [ ] Report live-client gaps separately: launch, character creation, armor/geosets, barber, mounts, druid forms, combat/death audio, relog, and multiplayer.
