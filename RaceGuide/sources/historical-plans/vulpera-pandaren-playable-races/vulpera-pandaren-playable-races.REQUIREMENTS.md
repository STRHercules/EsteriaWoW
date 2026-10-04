# Vulpera Horde and Pandaren Alliance

## Status

Approved staged design. This document is the implementation boundary for the
current `TASK.md` revision. It does not authorize Horde Pandaren, Ogre,
Forsaken, Kul Tiran, new racial abilities, Monk class 10, or replacement of
existing client packages.

## Source of truth

The authored registry and existing SQL map are authoritative:

| ID | Identity | Faction | This change |
|---:|---|---|---|
| 15 | Sethrak | Horde | Preserve; keep out of PlayerBots |
| 18 | Pandaren Alliance | Alliance | Enable and expose |
| 20 | Vulpera | Horde | Enable and expose |
| 26 | Pandaren Horde | Horde | Preserve row; disable and hide |

Race masks remain 32-bit. Existing character rows are never remapped or
deleted. The current live preflight found four ID-15 characters and zero
characters at IDs 18, 20, and 26. Live `playercreateinfo` currently covers
classes `1-9,11` for all three target rows.

The current C++ enum block is not merely missing three values: its custom
values conflict with the registry and would create duplicate `switch` cases
if only Pandaren/Vulpera were changed. Reconcile the complete custom enum
block with the registry, including explicit Sethrak and Dracthyr values, and
remove stale Ogre identity usage rather than assigning it a fake race ID.

## Staged implementation

### Stage 1: server race contract

Change only the shared race identity declarations and the PlayerBots seam.

- Align `SharedDefines.h` with registry IDs.
- Preserve `RaceMgr`, `ObjectMgr`, and character-creation validation paths;
  they already consume DBC/SQL data dynamically.
- Replace the numeric upper-bound PlayerBots gate with an explicit supported
  race policy. Admit current supported races plus IDs 18 and 20. Reject ID 15,
  ID 26, and every deferred custom race.
- Keep faction balancing, expansion checks, disabled-race masks,
  `PlayerInfo` validation, appearance checks, and generic `playerbots_names`
  fallback intact.
- Keep explicit target cases in `CombineRaceAndGender()` and map both genders
  to the existing generic name category.
- Audit PlayerBots race-name, travel, factory, and appearance switches for
  accidental ID-based exclusion or mislabeling. Change only a confirmed seam.

### Stage 2: corrective world migration

Add one later module world update. Do not edit applied race migrations.

The update will:

1. Select and report character counts for IDs 15, 18, 20, and 26 before any
   state change.
2. Preserve ID 15 and all existing character data.
3. Clear only `CHRRACES_FLAGS_NOT_PLAYABLE` for IDs 18 and 20.
4. Set only `CHRRACES_FLAGS_NOT_PLAYABLE` for ID 26.
5. Leave all unrelated `ChrRaces` flags, faction IDs, display IDs, start
   profiles, and migration history unchanged.
6. Validate target `playercreateinfo` rows for classes `1-9,11`, valid
   `charstartoutfit_dbc` rows for both genders, race stats, skills, spells,
   actions, and faction/language data.

The migration must be idempotent and must not silently delete or reinterpret
characters. Existing `elwynn` and `durotar` profiles remain the target start
locations.

### Stage 3: DBC and client assets

Use extracted assets selectively. Preserve original MPQs and baseline DBCs.

- Source models/textures from `patch-CHA.mpq` extracted `Character` paths.
- Source donor DBC rows from the extracted root `DBFilesClient`, not from the
  model-only `patch-CHA.mpq` directory.
- Remap donor Vulpera rows to ID 20 and donor Pandaren rows to ID 18.
- Generate only required continuation rows for the listed DBC tables. Keep
  ID 26 data present but non-playable and do not add a Horde Pandaren UI path.
- Add `NameGen` rows or explicitly use the existing generic-name fallback;
  do not invent racial abilities.
- Reuse the existing `mod-wxl-dbc` continuation and derived-index seam. Do
  not replace its current dirty implementation or add a second loader.
- Treat Patch-B as authoritative. Merge only race-specific icons, strings,
  lighting/faction entries, and two button definitions using existing
  templates/anchors. Keep button ordinals separate from actual DBC race IDs.
- Keep exactly one authoritative copy of each Glue file. Never copy a donor
  `Interface`, `GlueXML`, `SharedXML`, or `Glues` directory wholesale.
- Stage extracted/repacked output separately before replacing or deploying any
  client file. Verify path collisions and byte-preserve unrelated files.

## Data flow

```text
registry IDs
  -> SharedDefines / PlayerBots policy
  -> corrective world SQL
  -> server DBC overlays and derived indexes
  -> client DBC continuations + Patch-B Glue additions
  -> character-create request with actual ID 18 or 20
  -> Player::Create() using existing start/class/data paths
```

## Verification

Test-first for production C++: add the smallest focused check for the explicit
PlayerBots race policy, run it red, implement, then run it green. Add static
data checks for enum/registry uniqueness, target class coverage, race-mask
coverage, DBC row remapping, Glue ordinal/ID separation, and package path
collisions.

Run focused C++ and SQL linters after edits. Do not configure or build unless
explicitly requested by the user. Static checks do not claim live gameplay.
The final gate remains manual client/server smoke for race selection, both
genders, all enabled classes, creation, login, relog/restart, equipment,
jump, mount, barber, character select, and random PlayerBot creation.

## Non-goals and safety boundaries

- No source changes to `RaceMgr`, `ObjectMgr`, `Player::Create()`, or
  `CharacterHandler` unless a focused failing check proves an existing seam
  cannot support the two IDs.
- No database volume destruction, broad applied-migration edits, character
  migration, or client package overwrite.
- No claim of complete playability from SQL, DBC, MPQ, build, or static checks
  alone.
