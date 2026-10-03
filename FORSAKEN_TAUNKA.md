# Forsaken and Tauren/Taunka implementation plan

Status: research and discovery only. No implementation, archive installation, SQL mutation, build, or restart occurred.
The only authored file is this document. Findings below come from the current working tree, supplied MPQs,
the client at `G:\3.3.5a - Dev`, mounted server DBCs, and read-only queries against the running databases.

## 1. Recommended implementation

Implement **Taunka as a persistent Tauren bodytype** and **Forsaken as the existing Alliance race ID 25**.

| Player-facing choice | Persistent race | Legacy gender | Additional appearance state |
| --- | --- | --- | --- |
| Tauren / Male | 6 | 0 | Body variant 0 |
| Tauren / Female | 6 | 1 | Body variant 0 |
| Tauren / Other, tooltip "Taunka" | 6 | 0 | Body variant 1 |
| Forsaken / Male | 25 | 0 | Ordinary five appearance bytes |
| Forsaken / Female | 25 | 1 | Ordinary five appearance bytes |

This meets the requested three body choices under Tauren while preserving Tauren faction, racial mechanics,
starting data, equipment permissions, and stored race identity. Taunka must have its own model, textures,
customization lookup, preview/cache identity, and persisted discriminator. It must not replace ordinary Tauren males.

The bodytype solution does **not** make legacy gender value 2 a playable sex. Unmodified gender-dependent
addon APIs and grammatical selection will still see the Taunka body as male. The new player-facing control
represents bodytype. A third protocol sex would be a substantially larger client/core compatibility project.

Two findings materially affect the implementation:

1. The supplied "HD" Taunka M2 has the same geometry as the supplied non-HD M2. Its packaging is HD-compatible,
   but the archive label does not establish an HD geometry upgrade. See section 2.
2. Forsaken is already allocated in source and SQL, but its client and mounted server DBC row is still the old
   non-playable Broken NPC row. Its referenced Forsaken model files are missing from the current client.
   This is completion of an existing identity, not allocation of another playable race.

## 2. Verified source assets

### 2.1 Taunka

Supplied directory:

`R:\Users\Zach\Documents\GitHub\EsteriaWoW\NewModels\_Other\PlayableTaunka\`

The Taunka edit is available as both:

- `Patch-Z\Patch-Z.mpq`
- `Taunka HD models\patch-U.mpq`

These archives have identical SHA-256:

`bf0eee48986af108b69bb0e27a6e8e839f49c143a2a8554cac747d9f81459a8c`

The HD bundle's README calls the edit Patch-Z; the extracted HD directory actually calls it patch-U.
The remaining HD archives are patch-A, Patch-B, Patch-F, Patch-G, Patch-k, and Patch-T.
The edit contains 688 entries: one M2, 32 SKIN files, 103 ANIM files, 547 BLPs, three DBCs,
and two archive metadata entries.

Its model is `Character\Tauren\Male\TaurenMale.M2`, MD20 version 264, with:

- 4,169 vertices, 137 bones, 140 animation sequences, and three declared skin views.
- M2 SHA-256 `3ba5c9286f2ac8e950fdcfedf627c8691337ae8ae760d839dcd15a50d7201ad4`.
- Identical vertex data and identical `TaurenMale00.skin` to the supplied non-HD version.
- Exactly one differing byte between the two complete M2 files, at offset 426,880: HD value 6, non-HD value 8.

For comparison, the installed `Character\Tauren2\Male\TaurenMale2.m2` has 13,804 vertices and 227 bones.
The inspected Taunka body texture is 512x512; its lower-face texture is 256x128.
Do not describe the supplied mesh as an HD Tauren-body conversion.

**Quality gate:** first stage the supplied HD-compatible Taunka edit and inspect it beside the installed HD Tauren.
If matching HD geometry is mandatory and this mesh fails visual acceptance, obtain a different Taunka model or
author a Taunka head/body conversion against the actual HD Tauren skeleton, UVs, attachments, and animations.
That would be an additional asset-authoring task; changing DBC paths cannot increase this mesh's detail.
Do not silently substitute the non-HD pack or replace the installed Tauren2 model.

The edit supplies these full replacement DBCs:

- `ChrRaces.dbc`: renames race 6 to Taunka and retains stock legacy race assignments.
- `CharSections.dbc`: supplies the Taunka texture choices using race 6, gender 0.
- `CharacterFacialHairStyles.dbc`: supplies seven male Tauren facial-feature rows.

None of those whole tables is safe to install over Esteria's current tables.

The source's race-6/male sections contain 298 rows:

| Section type | Source rows | Rows carrying the player flag |
| --- | --- | --- |
| Base skin | 25 | 22 |
| Face | 199 | 199 |
| Facial-hair texture | 0 | 0 |
| Hair | 52 | 32 |
| Underwear | 22 | 22 |

Base skins 0-18 have flags 17; skins 19-21 have flags 5, including the Death Knight flag.
Skins 22-24 have flags 8 and are not player-flagged. Preserve those distinctions; do not expose NPC skins
or assume every face/skin/hair tuple exists. Hair/tail color is explicitly driven by hair color in the source README.

All 459 distinct texture paths referenced by these 298 sections were resolved by exact MPQ-name lookup:
431 are in patch-U and 28 are in Patch-B. Patch-B has unnamed enumeration entries, but these exact named reads succeed.
There were no unresolved section textures across the supplied HD bundle.
The bundle does not supply named `CharHairGeosets.dbc` or `CharHairTextures.dbc` entries at the expected paths.
Validate matching Tauren source hair-geoset data against the supplied SKIN groups instead of copying the current
HD Tauren's hair rules without checking them.

The 32 SKIN entries include standard `TaurenMale00/01/02.skin` and alternate/synthetic names.
Package the declared views and any additional runtime-referenced views; do not infer that every extra SKIN is a LOD.
The M2 has only replaceable texture types 1, 6, and 2, with no hard-coded texture filenames.
Its texture dependency routing therefore comes primarily from the section tables and component material logic.

### 2.2 Boneless Scourge for Forsaken

Supplied directory:

`G:\Downloads\Leeviathan-s_WoD_Character_Models_(3.3.5a)\`

Use the optional boneless overlay plus its matching baseline:

- `OPTIONAL - Boneless Undead\patch-I.MPQ`
- `patch-H.MPQ`, as the dependency and customization donor, not as a whole-client replacement.

The included `info.txt` explicitly targets 3.3.5a. It describes patch-I as replacing Undead players and NPCs,
and warns about unchanged NPC baked textures causing purple elbow/knee patches. Our installation must isolate
these assets to Forsaken players, leaving Horde Undead and existing NPC assets unchanged.

patch-I SHA-256:

`163aefdddd82f12051202bdbd3b8ee25f4024e66446994423e1868c5aa67746d`

It contains 153 entries: two M2s, eight SKINs, 99 ANIMs, 42 BLPs, and two metadata entries. It contains no DBCs.

| Model | Format | Vertices | Bones | Sequences | Declared views |
| --- | --- | --- | --- | --- | --- |
| `Character\Scourge\Male\ScourgeMale.m2` | MD20/264 | 16,815 | 255 | 221 | 4 |
| `Character\Scourge\Female\ScourgeFemale.m2` | MD20/264 | 17,949 | 216 | 219 | 4 |

Male M2 SHA-256: `5f4ad14457e9e9b3257908551bca26049c9d197c79c4cfa2f548b138fd1eaf34`.
Female M2 SHA-256: `ba0867444accb96dd9aced4ae3f3d1f451d9ef3dc0f98be77299a9800d20ed95`.

The matching patch-H provides:

- 814 Scourge `CharSections` rows: 452 male and 362 female.
- 30 Scourge `CharHairGeosets` rows and 25 `CharacterFacialHairStyles` rows.
- The remaining body, face, hair, feature, eye-glow, armor-support, and animation dependencies.

Use patch-I over patch-H when resolving the donor graph. Its 42 textures are an overlay, not a complete character pack.
The boneless M2s contain hard-coded paths to feature textures and normal/DK eye glows under `Character\Scourge`.
Five of those six gender-specific paths resolve in patch-H. The male
`Character\Scourge\Male\NightElfMaleEyeGlow.blp` does not exist in either supplied donor archive,
but is present in the installed root patch-Z as a 2,564-byte BLP.
Include that exact checked dependency, or validate and document an equivalent donor; do not leave an implicit
dependency on an unmodified Horde asset path in the finished Forsaken model.

These are already Wrath-format models. No Retail retroport is needed for the supplied boneless pair.
Header compatibility does not prove animation, equipment, or live compositor correctness.

## 3. Current Esteria state and the Forsaken mismatch

### 3.1 Existing identity and starting data

`src/server/shared/SharedDefines.h` already defines `RACE_FORSAKEN = 25`.
`modules/mod-custom-server/data/races/race_registry.json` already assigns:

- Species key `forsaken`, display name Forsaken, Alliance faction, Elwynn start.
- Asset owner `boneless_undead_assets`.
- Separate Horde Undead identity at race 5.

The registry also reserves NPC Taunka at race 36, with legacy ID 19, and Broken NPC at 42, with legacy ID 25.
Do not use those NPC identities for the new Tauren bodytype.

Read-only SQL queries confirmed:

- `chrraces_dbc.ID=25` is named Forsaken, flags 12, faction template 1, Alliance 0,
  BaseLanguage 7, ClientFilestring Forsaken, displays 3000020 and 3000021.
- Those displays reference model-data IDs 3000020 and 3000021.
- Model paths are `Character\RaceOverhaul\Forsaken\Male\ScourgeMale.mdx` and the female equivalent.
- Race 25 already has ten `playercreateinfo` class rows: 1,2,3,4,5,6,7,8,9,11.
- Ordinary classes start in Elwynn; class 6 starts in Ebon Hold on map 609, zone 4298.
- A Common-language skill row exists: raceMask 16777216, classMask 0, skill 98, rank 0.
- The queried stock Undead/Human racial spell IDs were not present in race-25 creation spell rows.
  This query was scoped to selected IDs; it was not a complete spell or script-grant audit.
- There were no stored race-25 characters. There were 25 Tauren characters, nine male and sixteen female.
- `characters.extraAppearance` already exists as `BIGINT UNSIGNED`.

Keep the existing starts, including the DK exception. Do not rebuild every race's starting data.
Do not change existing Tauren characters to Taunka automatically.

### 3.2 Client and mounted DBC disagree with SQL

The client root and enUS Z archives both currently contain this race-25 row:

| Field | Installed DBC value | Intended Forsaken identity |
| --- | --- | --- |
| Name / file string | Broken / Broken | Forsaken / Forsaken |
| Flags | 5, including NOT_PLAYABLE | Clear NOT_PLAYABLE |
| Male/female displays | 17576 / 17577 | Dedicated boneless displays |
| Alliance field | 2 | 0 |
| Model-data IDs | 2367 / 2368 | Dedicated boneless model rows |
| Model paths | `CHARACTER\Broken\...` | `Character\RaceOverhaul\Forsaken\...` |

The bound `modules/mod-custom-server/data/dbc/retroported-races/ChrRaces.dbc` has the same old Broken row.
The client's `CharBaseInfo.dbc` has no race-25 pair, and `CharStartOutfit.dbc` has no race-25 outfit rows.
The client lacks both Forsaken model paths currently referenced by SQL.
The checked effective `CreatureDisplayInfoExtra.dbc` has no DisplayRaceID=25 entries.
Recheck NPC references across SQL and all effective tables before changing that identity.

This explains why registry/SQL presence cannot be treated as a completed playable implementation.
Server startup loads DBC files and then calls `LoadFromDB` for the named SQL override tables
(`src/server/game/DataStores/DBCStores.cpp:227-254`). SQL can therefore repair a server store while the client
continues to see Broken. Make client files, mounted files, and SQL agree explicitly.

### 3.3 Winning archives and current models

The inspected client tables and GlueXML resolve from:

- `G:\3.3.5a - Dev\Data\enUS\patch-enUS-Z.MPQ`, with corresponding copies in root patch-Z.
- Stock Horde Undead displays 57/58 resolve to `Character\Scourge2\Male/Female\Scourge...2.m2`.
- Tauren displays 59/60 resolve to `Character\Tauren2\Male/Female\Tauren...2.m2`.

Update both winning root and locale table/UI entries. Add isolated assets through the existing pack workflow.
Do not install the donors' patch letters directly: the active client already uses those namespaces and contains
other races, mounts, appearance catalogs, and UI changes that must survive.

## 4. Why a third raw gender is the wrong implementation here

The following constraints were verified in source and the installed executable:

- Gender enum: male 0, female 1, none 2 (`SharedDefines.h:59-64`).
- `Player::IsValidGender()` accepts only values through female (`Player.h:1598`).
- Creation, Character Select enumeration, and login all call that validator.
- `Player::InitDisplayIds()` only handles male and female (`Player.cpp:10885-10908`).
- `ChrRacesEntry` has only `model_m` and `model_f`; the neutral-name fields are names, not another model slot.
- Character-creation and roster packets carry a gender byte, but that byte's capacity does not establish support.
- The existing 64-race extension still has `kSexCount=2` and race/sex caches indexed as `race*2+gender`.
- `NativeAppearance.cpp` validates several profile/catalog genders with `<2` or `>1` guards.
- The active Glue constants are `SEX_NONE=1`, `SEX_MALE=2`, `SEX_FEMALE=3`.

Read-only disassembly of the current image adds a concrete client constraint:

- `0x006D5C30` accepts a gender below 3, but returns the male ChrRaces display for 0, female display for 1,
  and zero for 2. Thus even the native lookup that tolerates 2 has no third playable model.
- `0x006DC810` resolves the race/gender model descriptor; its direct callers include `0x004E13AF`
  and Character Select's `0x004E3D84`.
- Creator cache operations at `0x004E20EB` and `0x004E2124` use `race*2+gender`.

Merely allowing gender 2 on the server, changing a Lua constant, or changing `kSexCount` to 3 would leave
model lookup, cache strides, customization, outfits, barber, and other consumers inconsistent.
`GENDER_NONE` also means a wildcard in some shapeshift model lookups. Preserve that meaning.

If a genuine third legacy sex is later required, separately audit every gender consumer, replace the two-slot
model contract, extend all native caches and their indexing/cleanup, define translation for gendered text/addons,
and migrate creation/login/customize/faction-change/barber/outfit paths together. That is outside this plan's
recommended bodytype implementation.

## 5. Taunka implementation details

### 5.1 Identity, persistence, and transport

Use one race-scoped discriminator: 0=ordinary Tauren, 1=Taunka. Require race 6 and legacy gender 0 for value 1.
Ordinary male/female characters retain zero. Reject unknown values and invalid appearance tuples at creation.

Reuse the existing appearance extension machinery:

1. Creator: store the bodytype in native creator context. Send it in the existing final outfit byte,
   which the core already repurposes for selected race-specific appearance profiles.
   For ordinary Tauren creation send zero. Do not overload a name, skin, facial style, or gender byte.
2. `HandleCharCreateOpcode`: validate the race-6 contract before constructing the player.
   Use a distinct Tauren-bodytype branch. Simply adding Tauren to `UsesExtendedAppearance()` is unsafe:
   existing ternaries would dispatch it to Earthen validation.
3. `Player::Create`: initialize persistent gender and bodytype before `InitDisplayIds()`.
   The current display initialization occurs before the existing extra-appearance assignment.
4. Save/load: persist the discriminator in the existing `extraAppearance` column using
   `CHAR_UPD_EXTENDED_APPEARANCE` in the same character transaction.
   Restore and validate it before login calls `InitDisplayIds()`.
5. Enumeration: include Tauren discriminator entries in the existing HXE1 GUID/byte roster tail.
   `EsteriaEnumExtra` already decodes HXE1 and HXE2. Keep both existing formats and mixed rosters intact.
6. Nearby players: use the existing public `UNIT_FIELD_PADDING` appearance byte and completed-update handling.
   That update field is already public; a new update-field layout or database column is unnecessary.

The current client has had lifetime corruption from registering a padding observer.
Reuse the established completed-update, owner lookup, and `EsteriaForgetCharacter` cleanup pattern;
do not activate `EsteriaRegisterExtra` or retain stale component pointers.

### 5.2 Isolated assets and data lookup

Stage the supplied model under `Character\RaceOverhaul\Taunka\Male\TaurenMale.m2`.
Retain companion basenames, relocating SKINs, ANIMs, and textures into that namespace.
Remap cloned section texture paths from `Character\Tauren\Male` to the new directory.
Preserve model/animation content except the path or material changes actually needed for isolation.

Use a **client-only, non-playable visual profile**, provisionally race-slot 54, for Taunka lookup/cache identity.
This slot is currently absent from the client race rows, registry, and playable allocations, and is within
the existing 64-race table. It is not the character's race, a new selectable race, or a server race-mask alias.

The visual profile should provide:

- A non-playable ChrRaces model descriptor with the dedicated Taunka display.
- Remapped Taunka sections and checked horn/hair-geoset rows under visual profile 54, gender 0.
- Separate customization counts and cache keys for `(54,0)` rather than `(6,0)`.
- Tauren equipment prefix/compatibility where the supplied model actually supports it.
- Any creator outfit lookup rows needed by the visual-only preview, without creating server player rows for 54.

Keep race 6's existing male/female display pair and section rows unchanged.
No character, character cache, race mask, quest condition, team assignment, or network race byte may contain 54.
If the native audit finds a path where the visual profile leaks into identity, fix the routing before deployment.

The section validator must use the Taunka profile when the discriminator is 1, including the source player/DK
flags and sparse face/hair combinations. The supplied sections have no facial-hair texture rows; the feature
control uses geometry and cannot depend on a nonexistent facial-texture section.

### 5.3 Native rendering and cache routing

The necessary change is before model selection and cache lookup, not an after-load reskin.

For Taunka, derive an effective visual profile `(54,0)` from per-character bodytype context while retaining
logical race 6. Route descriptor lookup, all creator model-cache reads/writes, customization counts,
section lookup, hair/facial geometry, and direct material setters through that effective profile.
For bodytype zero and unrelated characters, use the existing paths.

Use the existing WXL hook facility and native appearance DLL. `DarkfallenCharacterSelect.cpp` already hooks
`ResolveModelDescriptor` and Character List loading, and contains the relevant roster/component offsets.
Extend or compose that existing hook chain; do not independently overwrite an already-detoured function.
Do not change `Wow.exe` on disk or bypass its fingerprint checks.

Specific paths to cover:

- **Creator:** select/rebuild the Taunka model and its independent customization cache when Other is clicked.
  Both cache reads and writes need the effective key; a descriptor-only detour would still share male Tauren state.
- **Character Select:** obtain bodytype by roster GUID before `0x004E3D84` chooses the descriptor.
  The existing post-allocation `EsteriaSelectExtra` hook alone is too late to choose the initial model.
  Seed first section lookup as well; the existing Earthen preview fix demonstrates why setter order matters.
- **In game:** the server sends the dedicated native/current display ID. Resolve its component materials from
  Taunka data using authenticated owner appearance, including players first seen after login.
  Restore bodytype context after any late stock sanitizer, using the established owner lookup pattern.
- **Transformations:** apply Taunka routing only to the Taunka body display. Shapeshift/transform displays
  must use their normal model logic; removing the effect restores the saved native Taunka display.
- **Corpses/clones:** corpse appearance already carries native display ID and ordinary race/gender/appearance.
  Identify the dedicated Taunka display when padding/roster state is unavailable. Audit that render path before
  claiming support; the current player-unit hook does not automatically cover corpse objects.

The addresses above are verified discovery anchors for this installed image, not a complete approved patch list.
Before implementation, map every affected cache read/write, cleanup, and constructor path and capture its expected
bytes/calling convention. Prove creator and roster cache separation with an isolated native fixture before install.
Do not replace globally shared race-name pointers or mutate a single global male descriptor.

### 5.4 Server display selection and lifecycle

Add a race-6/bodytype-1 branch to the shared `Player::InitDisplayIds()` and select the dedicated Taunka display
for both native and current display IDs. Keep the ordinary male/female branches unchanged.
This shared function is used at creation, login, and GM gender changes.

Add matching `creature_model_info` data with gender 0 and validated Tauren-compatible scale/reach.
`Unit::SetDisplayId()` copies gender from that table into `UNIT_FIELD_BYTES_0`; setting it to none would corrupt
the intended legacy gender contract. Use `PLAYER_BYTES_3` as the persistent sex source when transformations
temporarily alter the display gender.

Customize, race/faction change, and GM gender changes must explicitly preserve or clear bodytype:

- Switching to female clears Taunka state and resets/remaps appearance to a valid female Tauren tuple.
- Switching away from race 6 clears the discriminator.
- Retaining Tauren/Other preserves valid saved choices.
- Failure to validate a submitted tuple must not partially update character data.

Barber support needs a bodytype-aware profile lookup. Its current handler requires style race and gender
to match the player. Generate dedicated Taunka barber rows using the visual profile, then map that profile
to Tauren only for a server-validated Taunka body. Preserve normal Tauren style IDs and appearance validation.
The normal barber need not become a bodytype-switching service; it must correctly edit an existing Taunka's choices.

### 5.5 Creator UI

Show three mutually exclusive body buttons only when logical Tauren is selected: **Male**, **Female**, **Other**.
Other's tooltip/description should identify the Taunka body. Existing Tauren race name, faction, lore, and racial
mechanics remain Tauren. Taunka body selection must not introduce a separate race-list entry.

Keep `SetSelectedSex(SEX_MALE)` for the Taunka body's legacy state and track the Other button independently.
Do not call `SetSelectedSex(4)` or use `SEX_NONE` for this choice.
Update button checks, labels, portraits, randomization, race changes, paid-customization restoration,
and customization control counts from the bodytype context.

The current creator has a Freeborn faction button centered between the two sex buttons.
Give the three body choices an explicit layout and preserve Freeborn as a separate faction control;
Other cannot occupy or repurpose that existing button. Confirm spacing and tooltips in the actual creator.
On leaving Tauren, hide Other and clear its unsaved state.

## 6. Forsaken implementation details

### 6.1 Asset isolation

Use the existing namespace `Character\RaceOverhaul\Forsaken\Male/Female`.
Preserve `ScourgeMale`/`ScourgeFemale` basenames to keep companion filename derivation predictable.

Build the dependency closure from patch-I over matching patch-H, with the explicitly resolved missing eye glow.
Copy only the assets needed by the two playable models and supported customization/equipment paths.
Exclude `(listfile)` and `(attributes)` from authored file payloads.

Rewrite all hard-coded type-0 M2 texture paths and cloned DBC texture strings into the Forsaken namespace.
When paths grow, append/rebase strings and update their lengths/offsets through the existing binary tooling;
do not perform a blind variable-length byte replacement inside M2/DBC files.
Preserve replaceable texture types, UVs, skeletons, animations, and boneless torso/pelvis textures.
Validate external-animation references and all declared skin views after relocation.

Leave `Character\Scourge`, `Character\Scourge2`, existing Horde displays 57/58, and NPC baked textures intact.
Do not install the optional patch-I directly into the active client's existing patch-I namespace.

### 6.2 Client and server DBC changes

Replace only race 25's stale identity, preserving its allocated Forsaken identity in SQL/registry.
Clone model-related settings from Scourge, then set Alliance identity deliberately:

- ID 25, name/file string Forsaken, playable flags, faction template 1, Alliance 0, team/base-language value 7.
- Dedicated male/female boneless displays; normal player displays should have no NPC baked extra row.
- Scourge equipment prefix `Sc` unless actual testing establishes a need for a new helmet asset family.
  A new prefix without matching helmet files would break equipped head models.
- No Undead starting cinematic; retain the existing Forsaken start policy.
- Fill relevant localized name variants consistently; neutral-name fields do not create another model.

Merge the following tables into both root and enUS Z archives:

| Table | Scoped operation |
| --- | --- |
| ChrRaces | Correct row 25; preserve every other playable and NPC row |
| CreatureModelData / CreatureDisplayInfo | Add dedicated model/display graph |
| CharSections | Clone matched Leeviathan race-5 rows to race 25, remap paths and unique row IDs |
| CharHairGeosets | Clone matched donor race-5 rows to 25 with new IDs |
| CharacterFacialHairStyles | Clone matched donor race-5/gender keys to 25 |
| CharHairTextures | Supply any required matched stock/donor rules, with layout-aware remapping |
| CharBaseInfo | Add `(25,2)` for the current Classless Paladin chassis UI |
| CharStartOutfit | Add race-25 outfits for supported class/gender pairs, preserving packed-byte layout |
| BarberShopStyle | Clone compatible male/female Scourge styles under race 25, preserving style meaning |
| NameGen | Clone compatible names to race 25 under new row IDs |
| HelmetGeosetVisData | Audit race-dependent visibility; add race-25 compatibility only where required |
| EmotesTextSound / VocalUISounds | Add Forsaken race-keyed mappings where needed using Scourge sound behavior |

The installed creator currently exposes only the Paladin chassis for ordinary race 6 in CharBaseInfo.
Do not expose ten independent classes just because the server retains ten creation rows.
Retain those server rows and the DK start exception for compatibility.

Synchronize the corresponding mounted server DBCs, SQL overrides, appearance validation data, and
`creature_model_info` rows. A correct mounted file can be overwritten by an old SQL override at startup.
Do not transplant donor full tables or stock legacy race numbering.

### 6.3 Faction, masks, skills, and racials

Forsaken's independent race mask is `1 << 24`, decimal 16777216 (`0x01000000`).
Keep it distinct from Horde Undead's race mask. Do not assign Forsaken the Horde mask or globally alias its team.

Verify the actual installed creation skill/spell paths and Classless behavior:

- Preserve existing Common skill 98/rank 0 and verify usable Common chat after creation and relog.
- Preserve existing weapon/class skills and action bars; correct only missing race-25 compatibility.
- Add race-25 bits to required SkillRaceClassInfo/SkillLineAbility or equipment permissions selectively.
- Reconcile client reputation defaults and server `Faction.dbc`/SQL masks for an Alliance race-25 character.
  Verify starting Alliance/Horde standings, guards, services, quests, and faction-dependent spell behavior.
- Audit hard-coded race-5 mechanics before reusing an Undead racial or cosmetic behavior.

This request does not specify new Forsaken racial abilities. Preserve the current server policy and report
the actual granted set before matching UI ability text. If stock Undead racials are chosen later, add them
explicitly to race-25 masks and verify their scripts/conditions; the model transplant does not grant them.
Do not advertise abilities copied from the Horde tooltip that the server has not granted.

### 6.4 UI and NPC protection

Add Forsaken to the creator's existing race presentation mapping, using its unique file string `FORSAKEN`.
Supply male/female portraits through the established ring/BLP pipeline, text/lore, correct Alliance background,
Character Select presentation, and character-frame portraits.
Add `FORSAKEN` to GlueParent's Alliance background routing so it does not request nonexistent `UI_Forsaken` assets.
The current creator/CharacterInfo mappings contain no Forsaken entry.

Avoid confusing visual row IDs, race-list indices, and persistent race IDs: the current CharacterInfo localization
table uses presentation indices and cannot simply receive an arbitrary `[25]` replacement.

Do not move or repurpose existing Broken NPC display/model IDs. The current client has no extra rows using race 25,
but still inspect SQL overrides, continuation files, baked-texture records, and concrete NPC display references.
If a remaining NPC customization reference uses the old race-25 meaning, migrate that scoped reference to its
existing NPC-only identity before enabling Forsaken. Preserve those NPCs' models and appearance choices.

## 7. Allocation and files to change during implementation

The following display/model candidates are currently absent from both effective client and mounted server tables,
and the read-only SQL candidate queries returned no conflicting rows:

| Asset | Candidate display ID | Candidate model-data ID |
| --- | --- | --- |
| Forsaken male | 60040 | 120057 |
| Forsaken female | 60041 | 120058 |
| Taunka body | 60042 | 120059 |

Record reservations in the existing allocation manifest and recheck immediately before staging/install.
These are proposed IDs, not reservations made by this research run. Leave old SQL display/model IDs alone unless
a complete reference audit proves removal necessary; change row 25 to the new graph consistently.

The existing CharSections allocations cover the full 450000-599999 reserved range.
Use new, collision-checked blocks, for example 600000-609999 for Forsaken and 610000-610999 for Taunka.
Likewise extend exhausted allocated ranges rather than taking another race's reserved rows.
Possible follow-on blocks are barber 458200+, outfit 21600+, and NameGen 36000+;
their actual IDs must be checked against complete effective tables and manifests before assignment.
Use composite keys for tables such as CharacterFacialHairStyles and packed records for outfits/base-info.

Expected implementation touchpoints:

- `data/retroported-races/allocation.json` and the existing race registry: document the asset reservations,
  keep Forsaken 25, and record Taunka as a Tauren body profile rather than a new playable race.
- Existing `tools/retroported_race_pack.py`, `playable_race_pack.py`, `cars_mount_pack.py` helpers:
  reuse RawWdbc, string rebasing, StormLib, archive staging, dependency checks, backup/install patterns.
  A small scoped Forsaken/Taunka pack entry point can orchestrate those helpers.
- `src/server/shared/SharedDefines.h`: a separate race-6 bodytype predicate/contract if needed,
  without changing the Gender enum or existing extended-race dispatch semantics.
- `src/server/game/Handlers/CharacterHandler.cpp`: creation validation, roster tail, body-aware barber,
  customization and race/faction-change persistence rules.
- `src/server/game/Entities/Player/Player.cpp` and `PlayerStorage.cpp`: initialized display selection,
  bodytype save/load, and preservation across native-display restoration.
- `client-customization/NativeAppearance.cpp`: creator/roster/update context, section/geometry routing,
  model-specific counts, and cleanup, while preserving the accepted existing profiles.
- `wxl-races-patcher/DarkfallenCharacterSelect.cpp` or its existing composed hook chain:
  pre-descriptor routing and independent preview-cache selection.
- Active `CharacterCreate.lua/xml`, `CharacterInfo.lua`, `GlueParent.lua`, and relevant portrait mappings:
  merge entries inside both winning Z archives, preserving current UI.
- `modules/mod-custom-server/data/dbc/retroported-races/`: scoped merged server tables.
- New SQL migrations exclusively under `data/sql/updates/pending_db_world/`.
  No characters-schema migration is required for the recommended discriminator storage.

Do not regenerate or overwrite the existing Earthen/Haranir/Highmountain source work currently dirty in this checkout.
Do not rerun broad legacy race migrations whose source numbering differs from the current client.
Before future C++/SQL/test/build work, read the matching `.agents/docs` task guidance.

Playerbots currently exclude race 25 in `IsSupportedRandomBotRace`, although the name switch recognizes Forsaken.
Keep automatic bot generation unchanged unless explicitly included in implementation scope.
A normal bot may remain an ordinary Tauren; do not automatically transform existing bots or reroll appearances.
Optional Forsaken/Taunka bot generation requires its own supported-race and appearance validation changes.

## 8. Execution order and acceptance gates

### Phase 1: freeze the baseline and stage the asset graphs

1. Recheck active client paths, archive winners, model/display reservations, existing characters, and SQL overrides.
2. Take SHA-256-verified backups of each eventual replacement, exact affected SQL rows, helper/runtime binaries,
   current server image, and relevant character appearance records. Stage large archives on a drive with room.
3. Isolate and validate the Forsaken male/female dependency closure and Taunka source closure.
4. Resolve the Taunka geometry quality gate before claiming the supplied source meets the HD requirement.
5. Generate collision-safe table merges and focused UI edits against the actual current archives.

Exit: every referenced M2/SKIN/ANIM/BLP exists, strings are valid, no unrelated row/asset changed,
and the proposed source appearance is reviewable.

### Phase 2: complete Forsaken independently

Correct client/server/SQL race 25, add the isolated models and creation/customization data,
then finish creator/roster/background/portrait/faction integration.
This phase should primarily require data and UI work; reuse the existing race enum/core machinery.
Do not add speculative core race handling when the existing data path suffices.

Exit: both genders create as race 25 on Alliance, show the boneless model in creator/Character Select/world,
retain valid appearance after relog, and Horde Undead plus Broken NPCs remain unchanged.

### Phase 3: prove Taunka routing, then add persistence and UI

1. Prove descriptor, visual-profile, and cache separation in the existing customized native client architecture.
2. Add the validated discriminator transport/save/load/display path and the Taunka appearance profile.
3. Add Other to Tauren creator state and restore it in paid customization/Character Select.
4. Complete body-aware barber, transformation restoration, corpse rendering, and observer handling.

Exit: Male, Female, and Other can appear simultaneously without shared texture/customization state;
Other remains stored/networked as Tauren and survives a full logout/relog.

### Phase 4: focused automated verification

Leave a small runnable contract check that fails if identity, dependency, allocation, or bodytype routing breaks.
Use the existing native harness for the necessary lifecycle and mixed-roster cases rather than creating a new framework.
Check at least:

- Forsaken row 25 agrees across SQL, root/locale client, and mounted server data.
- Race 5, race 6 ordinary rows, and unrelated custom assets are unchanged against the frozen baseline.
- Every selected boneless/Taunka customization tuple has matching textures and geometry rules.
- Other uses race 6/gender 0/discriminator 1; invalid races, genders, values, and tuples are rejected.
- HXE1/HXE2 mixed rosters decode without changing stock records or losing existing extended appearances.
- Taunka and ordinary Tauren have separate descriptor/cache identities and first-layer initialization.
- A completed nearby-player update and a late sanitizer cannot drop the bodytype.
- Component destruction/address reuse clears state; padding observers remain unregistered.
- Save/load preserves the discriminator before display initialization; transform removal restores the native body.

Only build when implementation has been authorized. Read `.agents/docs/build.md` first.
Compile the changed native helper/runtime and worldserver only when their C++ changes require it.
A data-only Forsaken phase does not justify a server rebuild by itself.

### Phase 5: deployment and live acceptance

Close the client before replacing archives or loaded DLLs. Install only verified staged outputs with matching backups.
Apply only the dedicated pending migration(s). Recreate only `ac-worldserver`, retaining database/auth containers
and persistent volumes; use the established `--no-deps` workflow.
Verify mounted hashes, SQL values, startup readiness, and the final archive winners after install.
Keep an explicit manual acceptance record separate from static checks.

| Area | Required live checks |
| --- | --- |
| Tauren creator | Male/Female/Other switching, tooltips, valid choices, Randomize, leaving/re-entering Tauren |
| Tauren identity | Race 6, existing Horde/team policy, Tauren racials/starts, Freeborn choice remains independent |
| Taunka persistence | Creation, logout/relog, Character Select, restart, paid customization and female/race changes |
| Taunka visibility | Local player and a second client observing ordinary male, female, and Other simultaneously |
| Taunka appearance | Every selectable skin/face/hair/color/horn tuple; hair and tail color; barber |
| Forsaken creator | Alliance entry, both genders, valid full customization, icons/lore/background, Classless chassis |
| Forsaken identity | Race 25, Common chat, expected standings, Alliance guards/services/quests, Ebon Hold exception |
| Both asset families | Naked and clothed body, boots, gloves, belts, cloaks, helmets and hair-hiding rules, weapons |
| Both animation sets | Idle/run/swim/jump/sit, emotes/dance, casting, melee/ranged, mount/dismount |
| Lifecycle | Death/corpse/resurrection, shapeshift/transform and restoration, logout, exit and preview switching |
| Existing content | Horde Undead, both normal Tauren bodies, Broken/Taunka NPCs and existing extended races |

A static MD20 header, successful import, loaded DLL, or ready worldserver does not replace these live checks.

Rollback must restore backed-up files and affected rows, then recreate only worldserver if needed.
Before rolling back after new Forsaken/Taunka characters exist, define their appearance/identity fallback;
do not remove their model/data graph and leave saved characters pointing at missing assets.
Retain the existing BIGINT appearance column and unrelated extended appearance values.

## 9. What remains unproven after this research

- No creator, game session, barbershop, corpse, equipment, or two-client visual test was performed.
- No supplied model was installed or rendered in this run.
- The complete Taunka constructor/cache detour implementation and all patch-site fingerprints remain to be authored
  and validated. The discovered native addresses establish the relevant paths, not a finished binary patch.
- All Taunka section texture references resolved; the full animation, SKIN palette, attachment, and hair-geoset
  compatibility checks still belong to staging.
- The boneless pair is Wrath-format and its customization donor is identified; full dependency closure,
  armor/helmet behavior, and per-class appearance flags still need a staged contract check.
- Forsaken reputation defaults, every hard-coded race-specific mechanic, and the full actual racial-grant policy
  need their focused implementation audit. No unrequested new racial design is assumed.
- The supplied Taunka edit does not supply a higher-detail mesh than its non-HD counterpart.
  A true HD mesh match may require additional source assets or model authoring.

## 10. Evidence pointers

Repository paths and line numbers are from this working tree and can shift during implementation.

- `src/server/shared/SharedDefines.h:59`, `:95`, `:114`: gender values, Forsaken allocation, appearance predicates.
- `src/server/shared/DataStores/DBCStructure.h:631`, `:705`: section flags and the two-display ChrRaces structure.
- `src/server/game/Entities/Player/Player.h:1598`: binary gender validator.
- `src/server/game/Entities/Player/Player.cpp:531`, `:541`, `:560`, `:1210`, `:10885`, `:15474`:
  creation/roster validation, ordering, display initialization, extended appearance transaction.
- `src/server/game/Entities/Player/PlayerStorage.cpp:5077`, `:5146`, `:5200`:
  gender/appearance load before display initialization.
- `src/server/game/Handlers/CharacterHandler.cpp:223`, `:294`, `:1618`, `:1758`, `:2056`:
  roster extensions, creation, barber/customize/faction-change handling.
- `src/server/game/Entities/Unit/Unit.cpp:13186`, `:13199`: display gender and restoration behavior.
- `src/server/game/Entities/Object/Updates/UpdateFieldFlags.cpp:311`: public appearance padding field.
- `src/server/database/Database/Implementation/CharacterDatabase.cpp:45`, `:82`, `:85`: appearance query/storage.
- `src/server/game/DataStores/DBCStores.cpp:227`, `:426`: SQL override order and ChrRaces loading.
- `src/server/game/Globals/ObjectMgr.cpp:4438`: male/female PlayerInfo display assignment.
- `client-customization/NativeAppearance.cpp:866`, `:889`, `:918`, `:952`, `:974`, `:980`, `:994`:
  existing creation/roster/update/material/context/cleanup hooks.
- `wxl-races-patcher/DarkfallenCharacterSelect.cpp:35`, `:98`, `:192`: native resolver and two-slot cache assumptions.
- `R:\Users\Zach\Documents\GitHub\AzerothPlex\build\wxl-core\extensions\races-64-esteria\MoreRaces.cpp`:
  64-race, two-sex runtime tables and customized-image validation.
- `tools/inspect_client_archive.py`, `cars_mount_pack.py`, `playable_race_pack.py`, `retroported_race_pack.py`,
  `wow_xref.py`: existing read/merge/stage/native-discovery tools.
- `modules/mod-playerbots/src/Bot/Factory/RandomPlayerbotFactory.cpp:59`, `:115`: bot support versus name mapping.
- Donor READMEs, exact archive-entry reads, effective root/enUS DBC reads, Docker mount inspection,
  and SELECT queries described in sections 2-3: current asset/identity/deployment evidence.

This plan intentionally separates confirmed local facts, proposed implementation decisions, and live acceptance gates.
