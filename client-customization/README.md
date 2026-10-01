# Native Skyborne appearance

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
