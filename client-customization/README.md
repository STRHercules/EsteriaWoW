# Native Skyborne appearance

## Vulpera Retail rebase (RaceID 20)

The later blue-eye follow-up changed cosmetic group17's fallback from1701 (the additive DK glow sprite)
to1700 (no sprite). Source-selected Death Knight/Primalist effects retain their explicit1701..1705 records;
ordinary eye colors and eyesight overlays no longer inherit a permanent blue glow. The check enumerates
both genders, every eye color and every eyesight setting against the runtime catalog's first-match order.
Deployment replaces only `EsteriaVulpera.bin`; a fresh client restart reloads the cached selection records.

The October 2 visual follow-up corrected three first-port mistakes. The creator's legacy Vulpera button
ordinal17 lacked exact race20 metadata, so the expanded native controls never activated. `CharacterInfo.lua`
now supplies that identity and a Lua5.1 check exercises both genders and stock-race transitions. The head
default now selects complete head3202 rather than neck ring3201. Tail/feet UVs lie in Wrath face-compositor
regions8/9; exact source body/pattern crops populate those regions through the checked upper/lower buffers.
No source vertices were moved and no material-validator guard was bypassed.

Codec v2 follows the Highmountain retention policy for all authored non-Transmog choices. It exposes nine
changing controls, including33 eye colors and Eye Style Slit/Star/Glow. The latter is available only with
its fourteen authored source palettes; ordinary, DK and Primalist eyes use their source default. Class
requirements apply only when the source requirement's class bit is set. The old first-port `ReqType == 3`
filter incorrectly removed these source choices. Existing fields are migrated by stable source choiceIDs,
and the previously constant facial-style byte now stores Eye Style. No extra packet bytes or schema are needed.

`tools/vulpera_render_repair.py` prepares and installs this guarded update. Focused checks include
`tools/test_vulpera_creator.py`, `tools/test_vulpera_models.py`, and native assertions for palette restrictions,
actual texture slots, both compositor face buffers, cleanup and unchanged five-byte creation packets.
The original paragraphs below describe the initial v1 installation; the v2 corrections above supersede its
choice filtering and control counts. A fresh-client visual acceptance remains separate from these checks.

`tools/vulpera_race_pack.py` replaces the legacy race 20 player graph from pinned Retail 12.1.0.69933,
build `dcfc90fffd79ba00406ae46f5f657592`. Identity, Horde affiliation, prefix Vu, displays 60006/60007,
classes, starts and implemented racial mechanics stay intact. The two model rows 112885/112886 point to
`custom\vulpera\native\male\vulperamale.m2` and its female counterpart. No executable patch is needed.

The codec retains eight independently changing controls per gender: Fur Color 8, Face 6, Snout 6,
Ears 6 male/8 female, Pattern 3, Eye Color 14 ordinary plus the DK eye, Earrings 2, Eyesight 4. The source's single
Hair Style remains a hidden constant. Five stock bytes suffice; there is no new creation/roster/padding
extension. Source class masks constrain the creator, randomizer and server validation. Internal/NPC/transmog
placeholders are inventoried rather than offered as ordinary player choices.

`tools/vulpera_models.py` preserves every geoset in the primary authored SKIN, 336 sequences, 24 male/25 female
events and original attachments. External animation keys are embedded, palettes respect 75 bones, and the
existing native geometry catalog handles 92,562 male/94,956 female triangle indices. Models retain 22,163 male/
22,487 female primary vertices. Retail's additional unused vertex payload is not copied into the playable M2.
The source has no separate collection or BONE customization graph; face texture and snout mesh are separate.

Retail uses 2048 x 1024 skin atlases. The left standard component atlas maps to Wrath's 512 x 512 body compositor;
right-square vertices are separated by material and retain their complete authored skinExtra/head atlas on
slot 8. No low-resolution face rearrangement is needed. `EsteriaVulpera.bin` reuses the bounded selection
format; `EsteriaVulperaTextures.bin` reuses the checked compressed RGBA bank and client-owned buffer loaders.
Class changes normalize invalid restricted choices, while render updates restore authenticated packed fields
after stock sanitation. Existing Haranir/Earthen teardown and buffer ownership rules remain in effect.

`tools/vulpera_equipment.py` converts 550 source Vulpera helmet variants for 275 of 277 installed head-model
families and their reachable companions/textures. Wrath `_VuM/F` paths alias the source `_vu_m/f` outputs.
Two legacy families have no matching named Retail variants: `Helm_Plate_BloodKnight_D` and
`Helm_Robe_AhnQiraj_A`. They remain a named coverage gap. The source `HelmetGeosetData` unconditional
race 35 hides become kind 4 selection records keyed by actual equipped display. The helper applies them
after cosmetic selection, restoring accessories when the helmet is removed. Source condition 32 has no
documented meaning in the installed definitions; it is recorded in `integration/helmet-catalog.json` and
retains existing stock behavior instead of an invented hide rule. Helmet visual fit still requires gameplay.

`tools/vulpera_migration.py` produces the guarded character update in
`data/sql/updates/pending_db_characters/rev_20261002200000000.sql`. Only GUID 423/499 are affected; their fur,
pattern, face, snout and eyes map through old textures/geosets to source choice IDs. Old mismatched ring/ear
combinations become authored Retail accessory combinations. Original tuples and rollback SQL are retained
outside mountable client directories. The stock barber continues using combined values; an independent
in-game barber UI is not added by this port.

Reproduction: source `G:\RetroPorterWork\vulpera\run_source.py`, `inventory_source.py` and
`convert_recovered.py` preserve source keys, hashes and direct-BLTE header recovery. Then run `header`,
`prepare`, equipment preparation, `stage`, `equipment_catalog`, `refresh_equipment`, focused native build,
`validate`, migration preparation and `backup`. Keep final companion/migration hashes current. Stop only
worldserver for `install`, then recreate it with `docker compose up -d --no-deps --force-recreate ac-worldserver`.
`tools/test_vulpera_race_pack.py` and the native harnesses verify codecs, class restrictions, all included
choice fingerprints, source vertices/geosets, atlases, animation/event closure, wide SKIN recovery, texture
buffer loading, helmet hides, cleanup, archive readbacks, DBC agreement and unchanged unrelated rows.
Installation receipts live in `C:\Users\Zach\.codex\tmp\vulpera\last-install.json`.

Automated checks and an installed matching image do not establish live acceptance. Creator/gender/class
switches, every choice, saved characters, nearby appearance, armor/helmets, movement/combat/emotes,
relog and full exit still require an active-client check. Retail racial abilities are not part of this visual rebase.

## Haranir port (RaceIDs 50/51, installed)

`tools/haranir_race_pack.py` stages the pinned Retail Haranir graph from
`G:\RetroPorterWork\haranir`. The initial conversion omitted 25 files; reachable playable textures are
recovered by FileDataID and checked against the pinned content keys. Raw assets stay in the retroporter's
ignored source cache. All four supplied Alliance/Horde portraits use the existing creator ring and ECS art
namespaces. The creator exposes every ordinary control: 29 male and 28 female options in two columns.

The full choices require more than the prior six-byte format. `HaranirAppearance.h` encodes them in eleven
used bytes within a thirteen-byte contract: five stock appearance bytes and an eight-byte extension. The
first five packing bins contain the ordinary skin, face, hair, color and facial choices; secondary controls
share those bins where capacity permits. The generated codec is frozen after installation. NPC/internal
and restricted skin/eye/hair-color placeholders are excluded; ordinary eyesight choices remain available.

`CMSG_CHAR_CREATE` receives a twelve-byte Haranir-only trailer (uint64 extension plus `HRC1` signature),
validated before creating the character. Mixed Character Select rosters append an `HXE2` GUID/uint64 tail
after the unchanged `HXE1` tail; the existing native hook strips both before stock parsing. The characters
column `extraAppearance` widens to BIGINT UNSIGNED without changing existing values. Player save/load uses
the same character transaction. Live nearby-player updates carry the extension in the unused Unit/Object
padding words. The helper reads completed updates and retains the proven owner lookup and component-free
cleanup. It never registers a padding observer or changes the client executable. Item update guards stay
in place. The native harness covers mixed roster tails, creation bytes, high-word persistence, late stock
overwrites, both genders' compositor output and the existing teardown/address-reuse checks.

The full-resolution body retains all 401/397 sequences and 37/36 events. External skeletal keys are embedded
and animation lookups regenerated from IDs. Every selectable accessory style survives in the authored
second reduced collection LOD; body plus collection totals 57411 male/54660 female vertices. This fits
Wrath's 65535 SKIN limit without deleting styles or inventing simplified geometry. Native palettes retain
the established 75-bone cap. The Nose selector retains the source's face meshes; no extra face BONE bake
is required by this source graph. Boots select rounded feet, while barefoot feet retain the player's
Normal/Clawed choice.

`EsteriaHaranir.bin` extends the existing bounded selection format with material-layer records.
`EsteriaHaranirTextures.bin` contains source-derived RGBA layers compressed with Windows LZNT1. Retail
texture-layer ordering and section layouts drive skin, body/face fur, paint, hair/highlight, eyesight, quill,
jewelry and clothing composition. The helper uses Windows Imaging Component to produce the indexed body
and face BLPs required by the stock compositor. Render-only materials use BGRA BLPs. Visited combinations
are cached under `Interface\AddOns\EsteriaAppearanceCache\Haranir`; the cache is disposable and contains no
saved choices. Runtime generation occurs in the client directory, so that directory must be writable.

The first live render exposed a missing integration gate: the native file resolver rejected the generated
relative paths, so body/face layers had failure flag `0x100000` and no image buffer; accessory bindings
shared the green error texture. Absolute paths alone also failed and were recorded as a disproven repair.
The checked cache BLPs now have the standard 1172-byte header and mip chains. Indexed layers receive
validated buffers allocated through the client's `SMemAlloc`; the stock layer destructor owns and frees
those buffers. Render materials use the existing native BLP decoder and CGTexture constructor, with
reference-counted component ownership. No global file-loading flag, executable, archive or source model
changes are needed for this repair.

The first buffer-loader candidate crashed because `SMemAlloc` was declared `cdecl` instead of `stdcall`;
both caller and callee removed its four arguments. That candidate was rolled back. The corrected harness
now mirrors the native ABI, and the repair checks the installed allocator's `ret 16` fingerprint. Live
reads confirm all body/face buffers and material bindings load correctly. The user confirmed no green
textures, working fur/customization on both genders, and correct Character Select/in-game rendering.
The corrected DLL has verified rollback copies under
`C:\Users\Zach\.codex\backups\haranir-render-20261001-225812`. `tools/haranir_render_repair.py validate/install`
reproduces the helper-only deployment; `tools/haranir_live_render.py <pid>` captures creator bindings without
writing process memory. The feet-control issue is explicitly deferred at the user's request.

Alliance/Horde compatibility profiles use Night Elf/Troll starts, language skills at step zero and their
existing racial mechanics. Retail Haranir racials are not implemented. The stock barber edits combined
appearance values; independent controls are available in the creator. This port does not replace the barber.

Reproduction: `acquire`, `prepare`, `stage`, then `tools/test_haranir_race_pack.py`. Build the native helper
into `C:\Users\Zach\.codex\tmp\haranir` with `client-customization\build-native.bat`, and build worldserver.
With WoW/Eclipse closed, run `backup`, stop only `ac-worldserver`, then run `install` and recreate worldserver
with `--no-deps --no-build --pull never`. Rollback copies and the prior image tag are recorded in
`C:\Users\Zach\.codex\backups\haranir-*\install-report.json`. Restore its replaced client/server files and
run `rollback-world.sql` with worldserver stopped. Retain the widened column on rollback to avoid truncating
new appearance values; any existing Haranir characters require a separate explicit rollback policy.

Automated data/native checks pass. Global C++ lint reports existing unrelated violations; SQL lint cannot
fetch this repository's missing `origin/master`. Fresh-client acceptance must still cover both factions and
genders, every control and Randomize, creation, normal chat, equipment, movement/emotes/casting, Character
Select, saved appearance on relog, nearby players, logout/client exit and an unrelated race.

Installation is complete with verified rollback copies under
`C:\Users\Zach\.codex\backups\haranir-20261001-203208`. Worldserver image
`264a515de23bf55f7bd68ac863edef75dab9cb8880a5668e906dc5047cdc311b` reached ready state without Race50/51
loading errors. All eleven client files and seven mounted server DBCs match the stage. Both migration
receipts, BIGINT storage, ten class starts per faction and language skill step zero are verified. The
executable, earlier race catalogs, saved character appearances and unrelated startup data are preserved.
The data contract passes against the installed files and verified pre-install baseline. Live acceptance
remains pending; the complete record is `G:\RetroPorterWork\haranir\integration\acceptance.json`.

## Earthen port (RaceIDs 48/49, installed)

The first live test found three follow-ups. `EARTHENHORDE` was absent from GlueParent's Horde background
table, causing a nonexistent `UI_EarthenHorde` load and a blank Character Select. The sourced Belt choice
zero is `None`, so the creator now labels `None`/`Gem` instead of `1/2`. The actual Gem collection used
geoset 1805, shared with stock equipped-waist geometry; its mesh and catalog selector now use group41
(4105), preserving the ordinary body/armor mesh and all vertices/materials.

Live reads of Rutherford Johnson (GUID518) proved network/database appearance bytes
`[40,79,153,68,90,43]` survived, while the native component was clamped to `[12,9,0,12,0]`. The completed
player update callback alone was insufficient: stock `0x004E9D50` sanitizes properties later against
ordinary DBC counts, and the initial update can finish before the component exists. Both early-restoration
and early-capture attempts were disproven by fresh-client reads. The revised shared geometry/material
callback finds the owning Player object by its component pointer and reads the validated player data
directly. It then restores the encoded bytes after the sanitizer. This is a bounded owner-list lookup during
dirty component rebuilds; no unit pointer is retained. Component destruction erases cached values,
preserving the tested teardown/address-reuse contract. Highmountain and non-player paths retain their
previous behavior. Both native harnesses pass, including no earlier capture, the exact saved-pattern
regression, late overwrite, and hairstyle/Gem belt selection for the owner fixture.
`tools/earthen_touchup.py prepare`, `validate`, `install` stages four archive entry changes plus the matched
helper/geometry/selection catalogs. The repair is installed with hash-verified backup
`C:\Users\Zach\.codex\backups\earthen-touchup-20261001-183021`. No executable, server or database change
was needed. The user confirmed the Gem belt visible. The revised helper was installed separately with
verified backups. The final owner-lookup DLL backup is
`C:\Users\Zach\.codex\backups\earthen-native-20261001-184511`. A fresh logged-in client read confirms all six
saved bytes now match `[40,79,153,68,90,43]`, with hairstyle4011, beard102, belt4105, shoulders4203/4303,
torso4402, arms4503, hands4603 and legs4701 enabled. User visual/relog/client-exit acceptance is pending.

The user then confirmed all in-game options visible, but the Character Select screenshot showed black
body/face with working hair/accessories. The preview had zero base/face compositor layers despite correct
encoded fields. Its first base-section validation runs before the setters establish resolver context.
`EsteriaSelectExtra` now obtains authenticated identity and appearance from the matching roster row,
restores the sixth-byte roster extension, and seeds context before that first validation. The native harness
reproduces a newly allocated blank preview and checks its first skin lookup. This helper-only repair is
installed with backup `C:\Users\Zach\.codex\backups\earthen-native-20261001-185129`; preview and teardown
live retest is pending.

The user confirmed the preview now looks good. A final foot follow-up showed overlapping toes/boot soles.
Both runtime models retained alternate Retail foot geosets 2001-2008, all visible because Wrath does not
select group20. The catalog now selects default2001 and hides the seven alternatives for both genders;
existing records, model geometry and armor selectors remain intact. `earthen_touchup.py feet` installed
only that catalog with verified backup `C:\Users\Zach\.codex\backups\earthen-feet-20261001-185656`.
The native owner fixture now checks that precisely one foot mesh is enabled. Feet live retest is pending.

The user clarified that boots must hide toe shape. A source mesh comparison confirms2001 is the bare
toe mesh and2002 is the rounded shoe mesh. Native inventory slot7 dispatches to component visual slot6,
stored at `0x440`; Rutherford's Recruit's Boots use display10141. The shared Earthen selector now chooses
2002 when that equipped-boot display is nonzero and2001 when it is zero, so live boot removal/equipping
changes the same component selector. The harness checks boots on/off and retained saved appearance.
The helper is installed with verified backup `C:\Users\Zach\.codex\backups\earthen-native-20261001-190402`;
boot-aware feet visual retest remains pending.

Final live acceptance: the user confirmed **"All fixed!"** after the gameplay customization, Character
Select, Gem belt and boots-on/off foot retests. All reported follow-ups are resolved. Rollback backups and
the exact installed hashes remain in `G:\RetroPorterWork\earthen\integration\acceptance.json` and the
corresponding backup install receipts. Face BONE morphs and Retail racial abilities remain outside this port.

Retail Earthen races 84/85 share ChrModel 195/196. Esteria uses separate Alliance/Horde identities 48/49,
distinct file strings `Earthen`/`EarthenHorde`, and the four supplied faction/gender portraits. The existing
ring/mask/BLP pipeline supplies creator, Character Select and character-frame portraits.

`tools/earthen_race_pack.py` follows the pinned Retail discovery and source configuration in
`wow-race-retroporter`. Missing reachable textures, model TXIDs and BONE inputs are fetched by FileDataID
with content/encoding hashes. The Retail installation is read only. Source additions remain in the ignored
`sources/retail/races/earthen` cache; derived output stays in `G:\RetroPorterWork\earthen\integration`.

Both genders have 16 independent controls: skin, face texture, hair style/color, beard style, gem color,
eye color, eyesight, eyebrows, belt, each shoulder, torso, arms, legs and hands. NPC horn/hand effects,
internal placeholders and NPC-only choices are excluded by the sourced requirement type. The ten face
textures are retained. Baking all ten BONE face shapes alongside the complete accessories exceeds the
Wrath SKIN uint16 budget, so face bone morphs are **not implemented** in this port. Cached BONE data is
retained for a future runtime vertex morph implementation.

`EarthenAppearance.h` encodes these choices in six bytes. Capacities are male `{196,80,165,196,165,50}`
and female `{196,80,165,196,165,32}`. The native/server code extends Highmountain's existing create, roster,
unit-update, save and load paths to 48/49. It preserves the tested no-registration teardown repair and
uses a separate `EsteriaEarthen.bin` selection catalog. Existing native catalogs are preserved; only the
geometry catalog gains the two Earthen profiles. The existing executable imports already cover this
extension, so **no executable patch is needed**.

The models retain 361/355 animation sequences and 39/40 event tracks. External keys are embedded using
the established animation reader. The converted male dance lookup pointed at sequence 698 instead of 69;
all lookups are regenerated from each sequence's ID and primary variation. Body and collection material
defaults remain inline global constants, including opacity for every animation. Ordinary collection meshes
are trimmed before merging, CRC-matched to the player bones, and use native palettes capped at 75 bones.
Eye atlases and eyesight overlays use the checked opaque UV0 material path. Female Left eyesight names
both an iris overlay and a lens material; the overlay uses the shared Human atlas while the lens keeps
its separate source TXID. The package includes only the runtime dependency closure, keeping each copied
merge archive below the classic 2 GB boundary.

Reproduce the data stage with `tools/earthen_race_pack.py acquire`, `portraits`, `prepare`, `stage`, then
`tools/test_earthen_race_pack.py`. Stages live at `C:\Users\Zach\.codex\tmp\earthen`. The next authorized
step is to compile `client-customization/build-native.bat` into that directory, run its native harnesses,
build the matching worldserver, install with verified backups and import only
`data/sql/updates/pending_db_world/rev_20261001100000000.sql`. The existing `characters.extraAppearance`
schema is reused. Alliance inherits the Dwarf start/compatibility profile and Common/Dwarven; Horde
inherits the Orc start/compatibility profile and Orcish. Retail Earthen racial abilities are not implemented.

The data contract and eight race-ID tests pass. The native helper and worldserver have been compiled;
both native harnesses pass, including Highmountain materials/lifetime and the Earthen codec/resolver checks.
The port is installed and worldserver is ready on image
`sha256:91cc3ecfad68a3ee8db7797b2d6ba0862904c944d5bdda9601f4e146702b151c`.
Rollback files and the previous server image are preserved in
`C:\Users\Zach\.codex\backups\earthen-20261001-104947`. All nine installed client files and seven mounted
server DBC hashes match the stage. Earthen's migration receipt is
`26E79289C5B5C72B60FB1A2A431E2CAD8A3FA4E5` in state `PENDING`; each faction has ten creation rows.
Unrelated startup rows and the auth/database containers remain unchanged. The acceptance record is
`G:\RetroPorterWork\earthen\integration\acceptance.json`. `earthen_race_pack.py backup` and `install`
implement the hash, empty-target, executable fingerprint, rollback, schema and scoped migration guards.

The global C++ linter reports existing violations outside this change; the SQL linter cannot fetch
the repository's missing `origin/master`. Scoped whitespace and migration checks pass.
Live acceptance remains pending. Checks must cover both genders and factions, every control,
armor/weapons, movement/emotes/casting, chat, Character Select, barber, saved
appearance after relog, logout/client exit, and the already accepted Highmountain/Mechagnome/Skyborn paths.

## Highmountain Tauren port (RaceID 46)

Highmountain uses Retail race 28 and ChrModel 55/56. The models' actual SKID references resolve to
child skeletons 1839622/1834492 and parents 1839011/1830371. The conversion merges all 349 male and
341 female sequences, retains child overrides, and packages every inherited external animation. The
animation check validates each external bone timestamp/value span against its actual companion file.
Initial converter outputs for parent-only sequences are replaced with the inherited payloads.

All player choices are retained, including special eye palettes. Only six internal transmog placeholders
are excluded. There are 20 changing male controls and 22 female controls; jewelry color has one authored
value. Conditional horn styles, markings, wraps and decorations follow source requirement choices.
Dependent accessories reset to their authored default when their prerequisite changes. Eye style applies
only to the eye palettes that reference it. Eyesight overlays are composed with their selected iris.

The five normal appearance bytes plus an explicit sixth byte preserve all choices. The last stock
`CMSG_CHAR_CREATE` outfit byte is unused by the core and carries this extension for Race46 only.
`characters.extraAppearance` stores it with the same character transaction. `UNIT_FIELD_PADDING`, which
has no existing gameplay consumers, becomes a public update field and carries the extension to nearby
clients. Native UnitFields starts at unit offset `0xD0`; the padding DWORD is at relative offset `0x234`.
Field-change registration uses type 3, byte offset `0x234`, size 4. Character enumeration appends only
Race46 GUID/extra-byte pairs, followed by a count and `HXE1` magic. The native reader bounds the trailer
and removes it before the stock roster parser runs. Existing character fields and team identity remain
unchanged. `HighmountainAppearance.h` is generated from the same choice descriptors and validates saved
bytes and horn dependencies on creation and login.

`EsteriaHighmountain.bin` has three uint32 header fields: magic `0x314D4845`, version 1 and record count.
Each 156-byte selection stores gender, kind, target, value, three packed option/value selectors and a
128-byte terminated material path. Geometry records select source geoset groups; material records bind
eyes and antlers; face records select baked head triangles only when both their source geometry and face
choice are active. Existing version-2 appearance and material catalogs remain byte-identical.

All nine face bone overrides are baked from their BIDA/BOMT matrices into weighted vertex positions and
inverse-transpose normals. Affected triangles have separate face geosets, with animations unchanged.
Male/female geometry stays under Wrath's 65535 vertex limit at 64136/56344 vertices. The existing native
wide-index and skin-array recovery handles their expanded triangle buffers and compact 75-bone palettes.

The legacy compositor resolves skin, paint, paint color and face choices through the shared native
CharSections lookup. This retains ordinary equipment composition. Native direct material selections
restore antler and iris bindings; the stock optional glow keeps its authored atlas. Source hard TXID
dependencies are fetched separately from the customization material inventory and content-key verified.

Highmountain inherits Tauren startup, equipment, stat and initial racial data, with explicit Orcish/Taurahe
spells 669/670 and skills 109/115 at skill step 0. Eligibility maps Race46 to Tauren's mask. Its creator
tooltip uses distinct Highmountain lore and the implemented Tauren racial profile; it does not advertise
unimplemented Retail abilities. Creation uses the supplied portraits with the installed metal ring;
selection uses masked BLPs inside the existing ECS border. Creator controls occupy two columns.
The stock barber retains its legacy selectors; the independent full selector UI is in creation.

Preparation uses the requested `wow-race-retroporter` source configuration and pins build
12.1.0.69933 / `dcfc90fffd79ba00406ae46f5f657592` under its source cache. Retail is never modified.
Derived art stays under `G:\RetroPorterWork\highmountain\integration`, and install stages stay on C:.
The requested repository's default pipeline stages are scaffolds, so the actual conversion reuses the
installed `wotlkconv` and the working Esteria integration tools.

Reproduction: `highmountain_race_pack.py prepare`, `highmountain_appearance.py`,
`highmountain_integration.py prepare`, `highmountain_faces.py`, then
`highmountain_race_pack.py hard-textures`. Build the helper into
`C:\Users\Zach\.codex\tmp\highmountain` and fingerprint-patch a copy of the original verified executable
with `native_appearance_patch.py`. Run `highmountain_integration.py build`, `validate`, and
`test_highmountain_race_pack.py`. Installation requires a matching worldserver build, closed WoW/Eclipse,
no existing Race46 characters/start rows, and SHA-256-verified client/server backups. It applies only the
dedicated pending migrations. Recreate only `ac-worldserver` afterward, preserving all Docker volumes.

Asset and native checks do not establish live rendering. Both genders, every control/choice, face shape,
movement/combat/talking, first login, languages, select portraits/tooltips, login/relog, nearby-player view,
equipment/helmets and unrelated race regressions require fresh-client acceptance.

The October 1 installation is deployed with verified backups under
`C:\Users\Zach\.codex\backups\highmountain-20261001-045931`. Worldserver image
`f4f1eed0909569c864326fc53a823e02cfa237835d5cc9471e0c7d3dc2b85d32` reached ready state with no Race46 loading
errors. Installed client and seven server DBC hashes match the stage. Highmountain, native helper,
Mechagnome, Mag'har/Skyborn touchups, two-names, select/limit, Broken and race contracts pass. The complete
record is `G:\RetroPorterWork\highmountain\integration\acceptance.json`; live acceptance remains pending.

The first live creator test exposed a sparse-table access at `0x004EA198` and a female body-file read
failure. Native validation normalized encoded choices, but the head/hair/layer getters subsequently
indexed the original values directly. The repaired getters resolve one row before using its texture;
their cache/refcount/dirty-bit behavior follows the stock setters. Compositor body/face assets now use
the working indexed BLP format (compression 1, alpha size 0, alpha type 8). The three archives are
Zlib-compressed, under 2 GiB, and all 43734 payload entries were verified unchanged by repacking except
the intentional 2160 compositor-format conversions. The root shrank from 3563853159 to 1398742364 bytes.

A follow-up live test exposed a wrapper ABI error: C++ x86 `bool` returns in AL, while the handwritten
wrappers tested full EAX. Dirty upper bytes incorrectly skipped the ordinary race material setters and
left Highmountain fur on Human/Night Elf/Mechagnome models. All three wrappers now test AL. The native
material harness exercises hairstyle one against a sparse zero-only table, encoded skin/face selection,
layer refcount updates and stock-race exclusion. The Python check also asserts the AL predicate in each
emitted thunk and verifies compressed file offsets with an independent MPQ reader.
The executable correction is installed with backup
`C:\Users\Zach\.codex\backups\highmountain-native-20261001-061134`; fresh-client texture acceptance is pending.

The user then confirmed the stock races' textures were restored, but both Highmountain heads remained
invisible. Live male geometry showed the small head fragment 3201 visible, the full face 3202 hidden,
and selected baked face variant 19601 hidden. Group32 had incorrectly been treated as an exclusive
customization group. Both 3201/3202 now use body geoset0, and all nine corresponding baked-face records
use the unconditional body source. Only those SKIN IDs and catalog selectors change; triangles, material
bindings, the executable and stock-race profiles remain unchanged. The matching native geometry recovery
catalog also contains these repaired SKINs. All nine variants and archive/catalog readbacks pass.
The repair is installed with verified backups under
`C:\Users\Zach\.codex\backups\highmountain-head-20261001-063540`; live head acceptance remains pending.

The user confirmed faces became visible but reported severely stretched muzzle geometry. The original
BOMT bake applied scale/rotation around the model origin. It now transforms each influenced vertex
relative to that facial bone's bind pivot, then restores the pivot and authored translation. All nine
face variants are retained. The rotation/scale regression and binary model comparison confirm only
vertex positions/normals change; bone weights, UVs, animation data, texture bindings and SKIN topology
remain unchanged. The male face-zero forward bound falls from 1.6627 to 0.9989, and the female from
1.1467 to 0.6903. The pivot repair is installed; fresh-client shape acceptance remains pending.

The user confirmed face geometry is fixed after a fresh launch. The remaining missing eyes retained
Retail shader144, two duplicated slot5 samplers and alpha-key blending. Both iris batches now use the
working Mechagnome path: one opaque, unlit UV0 sample from replaceable slot5 with shader0. Separate
group17 glow materials stay unchanged. The matching restored SKIN catalog is updated. Tests verify
accepted vertices, animations, submesh/index/bone arrays and unrelated batches are byte-identical.
The eye binding repair is installed with verified backup
`C:\Users\Zach\.codex\backups\highmountain-eyes-20261001-065746`; live iris acceptance remains pending.

The user confirmed eyes fixed, then reported invisibility while talking, fading during dance and weapon
socket problems. The first skeletal/opacity repair did not resolve the live symptoms; dance then crashed
while traversing malformed event timestamps. `tools/highmountain_complete_tracks.py` restores the raw PEDC
parent events, including the left/right sheath triggers, source opacity/UV/camera tracks, and embeds all
skeletal and attachment keys in MD20. Alias chains use the final target's relocated spans. All 349/341
sequences remain available, and accepted face/eye geometry, materials and SKINs are preserved. The user
subsequently reported Highmountain gameplay working.

Logout/exit crashes at `0x0074604E` were a separate native field-cache overwrite. A hardware watchpoint
captured `0x004D533B` copying UNIT_FIELD_PADDING into an adjacent NPC's GUID-list link. Padding is absent
from the stock old-value cache table, so registering an observer for it produces an out-of-range fallback
offset. `EsteriaRegisterExtra` now keeps its exported ABI without registering that unsupported field.
The hook after object updates at `0x004D6C86` reads the sixth appearance byte directly; non-unit objects
are rejected before Unit fields are accessed. The component-free hook at `0x004F16C0` invalidates the
component's extra byte and cached context before stock cleanup.

`tools/test_highmountain_teardown_repair.py` checks the x86 update/free continuations, retained AL bool
tests, native customization/material behavior, live sixth-byte changes, guarded item memory and component
address reuse. `tools/highmountain_teardown_repair.py install` replaces only the checked executable/DLL
pair, preserves all race assets/catalogs by SHA256, and makes verified rollback copies. The installed
backup is `C:\Users\Zach\.codex\backups\highmountain-teardown-20261001-093630`. Fresh-client memory reads
showed all 24 nearby NPC lists intact. The user confirmed repeated logout/relog, ordinary-race logout,
full exit and Highmountain appearance/talk/dance/equipment checks passed with no issues or crashes.

## Mechagnome port (RaceID 47)

`tools/mechagnome_race_pack.py` adds the converted Mechagnome assets from
`G:\RetroPorterWork\mechagnome` to the existing client. Both player models include the complete mechanical
collection: four arms, two legs, and twenty ear/antenna/visor modifications. Native selectors keep these
independent from hair and facial hair. The creator has twelve controls; the female facial-hair control is
hidden because its sole choice is the default. Source data supplies eight ordinary skins, fourteen face
textures, seven male/nine female hairstyles, seven hair colors, six male facial hairs, thirty-three eye
colors, three paints, four eyesight choices and three pupil styles. Pupil styles apply to the related
dragon-eye palettes; ordinary eye palettes remain unchanged, matching their source relationships.

The five appearance bytes use these encodings:

- `skin = skin + 8 * paint + 24 * eyesight`
- `face = face + 14 * facialHair`
- `hairStyle = hairstyle + hairstyleCount * arm + hairstyleCount * 4 * leg`
- `hairColor = hairColor + 7 * eyeColor`
- `facialStyle = modification + 20 * pupilStyle`

Internal transmog placeholders, two unavailable special skins and three restricted death-knight skins
are excluded from the ordinary skin selector. All fourteen face textures are included, but the Retail
`.bone` face-shape transforms are not applied, as with the Skyborne port. This is a texture/geometry port,
not complete Retail face-shape parity. The stock barber cycles the combined values.

`EsteriaAppearanceMaterials.bin` adds bounded native eye-material selections. Its header has magic
`0x544D4145`, version 1, and record count; each 188-byte record contains race/gender/replaceable texture slot,
three `{offset, factor, count, value}` selectors, and a terminated 128-byte texture path. The helper uses
the native extra-head load/set/release calls for eye slot 5.
The existing executable redirects stay intact.

Race47 uses Gnome compatibility/start data and the initial Gnome racial profile. Common and Gnomish are
explicit startup spells/skills; native skill eligibility maps Race47 to Gnome without changing race identity.
Portrait PNGs are converted with the installed metal ring for creation and the ECS frame for selection.
Both Z archives contain matching full DBCs, and the server receives the same seven generated DBC files.

Reproduction: run `tools/mechagnome_animations.py` to cache and convert the two inherited skeletons,
then run `prepare` and build the helper with
`client-customization\build-native.bat C:\Users\Zach\.codex\tmp\mechagnome`. Preparation writes the combined
appearance/geometry catalogs used by the helper harness. Next run `build`, `validate`, and `install`, then
`tools/test_mechagnome_race_pack.py` to include its live database language check.
Installation requires WoW/Eclipse closed and refuses unfamiliar executables,
stale archives, or existing Race47 characters/start data. It verifies backups on C:, applies the pending
world migration transactionally, and records rollback SQL and file hashes. Recreate only `ac-worldserver`
after installing. No core server rebuild is needed because the running core already supports Race47.

The October 1 installation is complete with verified rollback copies under
`C:\Users\Zach\.codex\backups\mechagnome-20261001-021341` and the subsequent rendering refresh under
`mechagnome-20261001-022712`. The refresh preserves Skyborne's creator spacing. Worldserver reached ready
state after the language rows
were corrected to skill step 0, matching the Gnome startup rows. All seven mounted server DBC hashes match
the generated tables. Mechagnome, native helper, Mag'har/Skyborne, character-select/limit, Broken,
playable-race, Darkfallen and Freeborn checks pass.

The user's subsequent live test confirmed creation, login, chat and independent customization controls.
It exposed missing gameplay animations, broken eyes in both sexes and flat male facial hair. The original
conversion kept only the child skeleton's 61/63 sequences and malformed partial lookups. The repair merges
the CRC-matched parent tracks into a complete 352/359-sequence table, preserves the child's overrides and
bind pivots, remaps aliases/variation chains, rebuilds ID lookups and packages the inherited external ANIMs.
It verifies walking, running, attacks, weapon ready, jumping, sitting, dancing and casting keyframe ranges.

Eye color belongs to the group-33 eyeball using UV0 with an opaque material. Group 17 is an optional additive
glow using its own hard sprite textures and UVs; it stays hidden for ordinary colors, appears for the source
DK choice (index 14), and selects groups 1702-1705 for primal colors. Applying the iris atlas to that glow
produced the bright squares seen in the user's screenshot. Male beard meshes use the source's type-6 hair
atlas; the target-8 facial-hair texture is an eyebrow overlay and was an incorrect beard replacement.
The repair restores the source beard binding and leaves saved appearance bytes and server data unchanged.
Animation/material live acceptance after this repair remains pending.

Live rendering, every mechanical/material choice, chat, creation, selection, equipment, barber and relog
remain manual acceptance checks until confirmed in the client.

`Wow.exe` imports `EsteriaAppearance.dll` directly. Customization does not use a WXL extension,
API, loader callback, or message. WXL still supplies Esteria's existing 64-race support and other features.
The permanent patch validates the exact original executable and each replaced instruction. It preserves the
foundation signature, Lua callback validation, race-table fingerprints, and character-limit byte.

Both race IDs 52 and 53 expose five blue/purple skins, ten face textures, 32 hair colors, 26 eye colors,
four eyebrow styles, feathers on/off, eight feather colors, and three ears. Male hair has 25 styles and
13 beard choices; female hair has 29 styles. Horns are excluded. Face bone morphs and tattoos are not applied.
The stock barber UI still cycles combined encoded values; it does not have these independent creator controls.

The existing appearance bytes retain their normal network and database transport:

| Stored byte | Encoding |
| --- | --- |
| skin | skin + 5 * eye |
| face | face + 10 * beard |
| hairStyle | hairstyle + hairstyleCount * ears |
| hairColor | hair color |
| facialStyle | eyebrows + 4 * feathers + 8 * feather color |

Native character-object offsets differ from packet order: hairColor is `0x24`, skin `0x28`, face `0x2C`,
facialStyle `0x30`, and hairStyle `0x34`. The catalog descriptors use these offsets. Creator changes call the
native setters to refresh materials and geometry. Beard and ear geometry overrides apply to all character
components, including character select and in-game units.
Feather geometry follows the source's related hairstyle choice: only that hairstyle's collection mesh is
enabled, with color variants in geoset groups `4000..4799`. Bald choices have no feather mesh. Rotation
controls are anchored below the first/last name fields.

`EsteriaAppearance.bin` starts with three little-endian uint32s: magic `0x50504145`, version 2, profile count.
Each fixed profile has race, gender, option count, and 16 descriptors. Each descriptor contains offset, count,
factor, optional geometry offset, and 32 geometry choices. Unused descriptors are zero. Profiles support up to
16 controls, 64 profiles, and a maximum encoded value of 255 in each appearance field. Future races require
their own asset and DBC preparation; they can reuse this codec and native callbacks.

`EsteriaAppearanceGeometry.bin` contains two prepared SKIN profiles, each preceded by a 128-byte terminated
model path and a uint32 byte length. Its header is magic `0x4D474145`, version 1, profile count. Array ranges,
triangle windows, vertex limits, and bone palette limits are checked before use. The native initializer restores
these arrays for the matching expanded model paths, preserving geometry that the current WXL MD20 reader
otherwise parks when its triangle offsets exceed 65535. This repair does not alter WXL or use its APIs.
Prepared meshes use compact native palettes, capped at 75 bones. Executable redirects widen index reads,
buffer writes, and draw starts; geoset comparison uses the low uint16 ID, preserving the high index word.

## October 1 client integration repairs

`EsteriaSkillRace` maps only eligibility checks for races 45, 52, and 53 onto their server-compatible
Orc, High Elf, and Blood Elf masks. Redirects at `0x00810F0A` and `0x0081033D` cover the shared skill/spell
metadata checks. Character identity and saved languages are unchanged. This restores language visibility
and chat for the affected races, whose language skills and spells were already saved correctly.

`CycleCharCustomization("EA_SELECT", index)` returns the actual roster race and gender from the same bounded
`0x198`-byte records used by native `GetCharacterInfo`. ECS uses it for these three races, with explicit
schema entries and six new ECS portrait textures. It avoids identifying Mag'har as its Orc background model
or treating Skyborn as unknown. Names stay on one line; tooltip positions use the cursor and anchor parent's
same coordinate scale and prefer below the cursor.

The Skyborn talking crash at `0x00828565` used a rewritten external animation offset as an in-model offset.
The female talk variant (sequence 144) must preserve its rotation timestamp span `(58, 1024)` in the companion
`74784940060-01.anim`. `read_player_model` now marks native external sequences before rewriting flat MD20,
preserving their timestamp/value spans for all bones. Source animations and geometry remain unchanged.

Build/install and regression entry points are `tools/race_touchup_pack.py` and `tools/test_race_touchup_pack.py`.
The user confirmed chat on Mag'har/Skyborn, the new Skyborn first-login test, and Character Select fixes on
October 1, 2026. The earlier cinematic failure had a heap-allocation stack; its exact original cause was not
independently established, and the fresh first-login acceptance test passed after the repairs.

## Rebuild and install

Generated assets stay outside Git. Defaults are `G:\RetroPorterWork\skyborne\integration\expanded`,
`C:\Users\Zach\.codex\tmp\native-appearance`, and client `G:\3.3.5a - Dev`.
Use the original verified executable from the initial backup as the patch source after the first install.

```powershell
rtk proxy python -X utf8 tools/expanded_appearance_pack.py prepare
rtk proxy cmd /c client-customization\build-native.bat C:\Users\Zach\.codex\tmp\native-appearance
rtk proxy python -X utf8 tools/native_appearance_patch.py --source C:\Users\Zach\.codex\backups\native-appearance-20260930-220154\Wow.exe
rtk proxy python -X utf8 tools/expanded_appearance_pack.py build
rtk proxy python -X utf8 tools/test_native_appearance.py -v
rtk proxy python -X utf8 tools/expanded_appearance_pack.py install
rtk docker compose up -d --no-deps --no-build --pull never --force-recreate ac-worldserver
```

Close WoW and Eclipse before installation. The installer rejects stale stages and unfamiliar executables,
backs up all replaced files and server DBCs on C:, verifies copies with SHA-256, and records appearances plus
rollback SQL. The pending characters migration preserves curated appearances once per race; subsequent
native installs do not remap them. `data/retroported-races/skyborne.json` records native mode and allocations.
The old curated builder rejects native mode to prevent accidental downgrade.

## Rollback and live checks

Use the backup named by `last-install.json`. With WoW/Eclipse closed and Skyborne characters offline,
restore its executable, helper/catalogs, three archives, and seven `server-dbc` files. Remove a newly installed
companion only if the install report shows no previous copy. Execute that backup's
`rollback-character-appearance.sql`, then recreate only `ac-worldserver` and launch a fresh client.
For rollback to the initial curated version, restore the initial backup and its appearance SQL together.

Static checks and the helper harness do not prove rendering. Verify both genders, each independent control,
randomization, existing character select, new creation, login/relog, armor, and one unrelated race. The initial
expanded install exposed wrong object offsets and WXL load-time mesh parking. The user confirmed both
genders' bodies, independent controls, hairstyle-specific feathers/colors, and rotation controls below the
name fields on September 30, 2026. New-character login/relog, armor/helmet, and barber smoke remain untested.

## Cosmetic wings on Character Select

`CosmeticWings.inl` reuses the installed native roster, preview and component teardown hooks.
Worldserver reads saved infinite self-applied auras and sends only members of wing group 9100 in a
`CWG1` trailer (GUID plus spell ID). The native helper strips it before stock parsing, alongside
`HXE1` and `HXE2`. Knowing a wing spell without its aura does not equip it.

`tools/cosmetic_wings_character_select.py prepare` resolves Cosmetics skill line 779 through the
installed Spell/SpellVisual state kit and back attachment 16 into `EsteriaCosmeticWings.bin`. It
checks server visual agreement, model presence, scales and native attachment fingerprints.
The helper retains an independent child reference across stock preview refreshes, detaches only
its own wing, and releases that reference when the character component is destroyed.
No schema migration, executable patch or MPQ replacement is required.

After explicit build authorization, prepare the catalog, then use `client-customization/build-native.bat`
with `C:\Users\Zach\.codex\tmp\wings-select` as its output directory.
The build runs the existing native checks and the new `TestCosmeticWings.exe` when the catalog exists.
Close WoW/Eclipse and run the preparation tool with `install` to install the DLL and catalog with
hash-verified rollback copies. Install the client helper before recreating the rebuilt
`ac-worldserver` with `docker compose up -d --no-deps --no-build --pull never --force-recreate ac-worldserver`.

Verification: `python -m unittest discover -s tools -p test_cosmetic_wings_character_select.py`;
`TestCosmeticWings.exe` checks mixed trailers, character isolation, repeat renders, parent refresh,
removal, delayed loading and teardown. The live protocol case is
`TestSession_CosmeticWingCharacterSelect` in `e2e/suites/protocol/session/`.
Its oracle follows real casts and cancellation through logout and the returned roster trailer.
Live visual acceptance still requires a fresh client: wing/no-wing characters, changing wings,
removing an aura, repeated character switches, custom races of both genders, and logout/client exit.
