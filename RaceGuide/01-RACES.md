# Races, identities and customization

[Back to the guide](README.md)

## Identity, presentation and eligibility

The current client rows are in [RACE_ROWS.md](reference/RACE_ROWS.md). The
[server registry](sources/EsteriaWoW/modules/mod-custom-server/data/races/race_registry.json) records
faction, start, asset owner and compatibility donor. There is verified legacy drift for IDs 24–27.

A race needs a numeric ID, file string, visible name, model/display rows, equipment prefix,
faction/start policy, legacy eligibility mask and UI metadata. Button slots and localized names cannot
substitute for identity.

## Modern ports

| Family | Esteria identity | Changing creator controls M/F | Transport |
| --- | --- | ---: | --- |
| Mag'har Orc | 45 Horde | Five legacy selectors | Five stock bytes |
| Highmountain Tauren | 46 Horde | 20 / 22 | Five stock bytes + one extra byte |
| Mechagnome | 47 Alliance | 12 / 11 | Five stock bytes |
| Earthen | 48 Alliance, 49 Horde | 16 / 16 | Five stock bytes + one extra byte |
| Haranir | 50 Alliance, 51 Horde | 29 / 28 | Five stock bytes + uint64 extension |
| Skyborne | 52 High Order Alliance, 53 Windshaper Horde | 10 / 9 | Five stock bytes |
| Vulpera Retail rebase | 20 Horde | 9 / 9 | Five stock bytes, codec v2 |
| Naga | 54 Horde | One changing field in five-field layout | Five stock bytes |
| Tuskarr | 55 Alliance, male only | Four changing fields in five-field layout | Five stock bytes |
| Vrykul | 56 Alliance; 57 Horde supported but creator-hidden | Four changing fields, male only | Five stock bytes |
| Forgotten / ThinHuman | 58 Alliance, 59 Horde, male only | Four changing fields | Five stock bytes |

The six expanded families are Skyborne, Mechagnome, Highmountain, Earthen, Haranir and Vulpera. The
creature ports reuse native material/geometry support but keep five-field layouts. One-choice fields
are constants: Highmountain has 21/23 authored fields, and Vulpera ten, without adding changing controls.

**All barbers still use the legacy combined-value interface.** Expanded creator controls do not imply
an independently expanded barber.

## Existing families and stock customization additions

| IDs | Presentation | Notes |
| --- | --- | --- |
| 1–8, 10–11 | Original ten Wrath races | Legacy selectors plus additive choices |
| 9 / 12 / 13 | Goblin / Worgen / High Elf | Worgoblin/custom baseline |
| 14 | Broken | Horde replacement; custom racial mechanics |
| 15 | Sethrak | In data, hidden in creator |
| 16 / 17 | Eredar / Nightborne | Existing player assets |
| 18 / 19 | Alliance Pandaren / Void Elf | Existing imported player assets |
| 20 | Vulpera | New Retail graph, original ID retained |
| 21 / 22 / 23 | Lightforged / Zandalari / Dark Iron | Existing imported player assets |
| 24–27 | Server policy: Broken/Forsaken/Pandaren variants | Client identity drift below |
| 28 / 29 | Dracthyr / Kul Tiran | Existing player assets |
| 30 / 31 | Illidari Horde / Alliance | Blood Elf DH-derived assets |
| 43 / 44 | Darkfallen Alliance / Horde | Shared name, distinct identity |

Server policy reserves NPC-only IDs 32–42; those rows are absent from the inspected client full table
but exist as server SQL overlays. Capacity for 0–63 does not mean 64 complete race packages.

An additive Ascension customization installation added **435 skin, 56 face and 220 hair-color
selections** across the two genders of the ten original races. These are aggregate additions, not
per-race totals. It preserved models and legacy selectors, excluded known-broken donor DK combinations,
and passed installation/data checks. Creator, barber and relog visual acceptance remain separate.

## Mag'har Orc

Retail 36 maps to Esteria 45. The final port uses working HD Orc2/Wrath geometry with Retail Mag'har
textures baked through its actual UVs. Converted Retail geometry caused invisible bodies and was
superseded. Both genders have nine independent skin colors and nine faces in the legacy selectors.

The successful face repair corrected UV/compositor assumptions and an invalid facial-hair overlay.
Backup MPQs under mountable `Data` also overrode new textures; they were moved outside that tree.

Mag'har could report default Orcish while showing no known language despite correctly saved skills and
spells. `EsteriaSkillRace(45)` maps skill eligibility to Orc 2 without changing identity. Exact roster
identity restores Mag'har names/portraits rather than inherited Orc presentation.

Both genders, skin/face cycling and later chat/select touchups were live-confirmed.
Sources: [packer](sources/EsteriaWoW/tools/retroported_race_pack.py),
[manifest](sources/EsteriaWoW/data/retroported-races/maghar.json),
[touchups](sources/EsteriaWoW/tools/race_touchup_pack.py).

## Skyborne

The donor is **WoW: Forever beta 1.60.1.70009**, product `wow_classic_beta`. Source races 95/96 share
ChrModel 218/219; targets are 52/53.

Both genders have skin 5, face textures 10, hair colors 32, eyes 26, eyebrows 4, feathers on/off,
feather colors 8 and ears 3. Male hair has 25 styles and beard 13; female hair has 29 styles. Horns,
face BONE morphs and tattoos are excluded/unimplemented.

Five stored bytes pack the independent controls. Native object offsets differ from packet order;
fixing those offsets corrected selectors that changed the wrong feature. Wide SKIN recovery restored
body/face meshes parked by the current model reader. Feather meshes follow their related hairstyle;
bald choices have none, and color variants use groups 4000–4799.

The talking crash came from treating external `.anim` offsets as model-relative offsets during
rewriting. The reader now preserves external spans. The original cinematic crash's exact cause was
not independently established; the subsequent first-login test passed.

Visible bodies, controls, feather mapping, rotation placement, portraits, chat and first login were
user-confirmed. Armor/barber coverage remains separate.
Sources: [visual preparation](sources/EsteriaWoW/tools/skyborne_visual_pack.py),
[native pack](sources/EsteriaWoW/tools/expanded_appearance_pack.py).

## Mechagnome

Retail 37 maps to Alliance 47, with Gnome startup/racial compatibility and Common/Gnomish. Controls cover
skin, face, hair/color, male facial hair, arm/leg upgrades, modification, eyes, paint, eyesight and eye
style; the female has no changing beard control.

Body and mechanical collections require bone/palette remapping and equipment-safe geoset assignments.
The initial models kept only 61–63 child-skeleton sequences. Parent inheritance restored **352 male /
359 female sequences**, including movement, combat, dance and casting.

Ordinary iris and optional glow are separate materials. Using the iris atlas on the DK glow produced
bright squares. Male beards use the source hair atlas, not the eyebrow-overlay target.

Creation, login, chat and controls were live-confirmed before the final animation/eye/beard repair.
That repair was installed with passing checks, but the linked chat ends at a retest request. Face BONE
morphs and restricted DK skins remain outside the port.
Sources: [pack](sources/EsteriaWoW/tools/mechagnome_race_pack.py),
[inheritance](sources/EsteriaWoW/tools/mechagnome_animations.py).

## Highmountain Tauren

Retail 28 maps to Horde 46. All ordinary authored choices are retained; six internal transmog
placeholders are excluded. Jewelry Color is constant. The exact labels/counts are in
[CUSTOMIZATION_OPTIONS.md](reference/CUSTOMIZATION_OPTIONS.md).

Controls cover face/skin, horns/markings/colors/wraps/decorations, hair/beard/foremane, eyes/eyesight,
body paint/colors, piercings, headdress, tail/decorations and gender-specific jewelry. Source prerequisites
constrain related accessories and eye styles.

All nine source BONE head overrides are baked, while the visible Face selector has five male/four female
choices. Baking uses bind pivots, weighted positions and inverse-transpose normals. Merged geometry is
64,136 male / 56,344 female vertices; animation inheritance retains 349/341 sequences.

Tauren startup/racial compatibility and Orcish/Taurahe at skill step zero are used. Full Retail
Highmountain racial abilities are not implemented.

The required repairs establish reusable rules:

1. Normalize encoded values before every sparse material lookup.
2. Emit indexed compositor BLPs.
3. Test x86 bool returns in `AL`, preserving ordinary-race fallback setters.
4. Restore complete heads as body geometry instead of exclusive group-32 choices.
5. Bake face transforms around bone pivots.
6. Bind ordinary eyes through the supported opaque single-UV0 path.
7. Restore parent PEDC sheath events plus opacity/UV/camera tracks.
8. Remove unsupported padding observers and invalidate cached component state on free.

A hardware watchpoint proved the padding observer caused an out-of-range field-cache write into an NPC
GUID-list link. The final helper reads completed updates directly and rejects non-units. User confirmation
covers appearance, talk/dance, equipment, repeated relog, ordinary-race logout and full exit without crashes.

## Earthen

Retail 84/85 share ChrModel 195/196; targets are 48/49. Alliance inherits Dwarf compatibility,
Common/Dwarven and Dun Morogh; Horde inherits Orc compatibility, Orcish and Durotar.

Sixteen controls per gender cover skin, face texture, hair/color, beard, gems, eyes/eyesight, eyebrows,
belt, both shoulders, torso, arms, legs and hands. Ten face textures remain. Baking every BONE face shape
alongside full accessories exceeds the Wrath geometry budget, so face morphs remain unimplemented.

Six-byte persistence, a dedicated selection catalog and compact collections retain 361/355 sequences.
Existing executable redirects cover this port.

Saved choices were intact in the DB and received by the client, but stock sanitation clamped them.
The repair restores validated bytes after late overwrite, resolves component ownership on fresh login
and derives base textures for blank roster previews. `EARTHENHORDE` also needed a background-map entry.

Belt is None/Gem. Rounded feet appear in boots and toes return barefoot. The user confirmed “All fixed!”
after persistence, Character Select, belt and feet tests.

## Haranir

Retail source races 86/91 share ChrModel 200/201 and map to Esteria targets 50/51 by explicit allocation.
The Retail file string is Harronir. Alliance uses Night Elf compatibility and Teldrassil; Horde uses
Troll eligibility while its registry start is Durotar.

There are 29 male/28 female controls: skin/face, fur patterns/colors, hair/highlights, spines/colors,
tusks, eyebrows, ears, eyes/eyesight, nose, jewelry, feet, clothing colors, necklaces, paint and
gender-specific beard/sideburn/moustache or eyelashes/underclothes.
[The generated catalog](reference/CUSTOMIZATION_OPTIONS.md) gives every exact choice count.

Eleven used bytes fit a thirteen-byte contract: five normal bytes plus uint64 extension. Creation uses
`HRC1`, rosters `HXE2` and DB storage uint64. The installed codec is frozen.

Body plus the second reduced collection LOD retains 57,411/54,660 vertices, 401/397 sequences and 37/36
events. All selectable collection styles remain under the Wrath vertex limit. Nose uses source meshes,
so this source does not need another BONE bake.

Compressed RGBA banks provide runtime texture layers. Relative-file and absolute-file candidates failed
in the native resolver. The working loader supplies validated BLP buffers through client-owned memory.
An initial candidate used `cdecl` for `SMemAlloc` and crashed; the proven allocator is `stdcall`.

The user confirmed both genders, fur/accessories, Character Select and in-game rendering. Feet behavior
was explicitly deferred. Loincloth visibility under preview clothing was not fully established. Retail
Haranir racial mechanics are not implemented.

## Vulpera Retail rebase

Race 20, Horde affiliation, `Vu`, displays 60006/60007 and established startup policy are preserved.
The visual graph is pinned to Retail 12.1.0.69933, key `dcfc90fffd79ba00406ae46f5f657592`.
Model rows 112885/112886 point to the new native paths.

Codec v2 has Face 6, Fur Color 8, Ears 6 male/8 female, Snout 6, Eyes 33, Earrings 2, Pattern 3,
Eyesight 4 and Eye Style 3. Hair Style is constant. Slit/Star/Glow depends on fourteen authored palettes.
Class masks apply only when the source requirement carries a class condition.

The first port's eight-control scope and broad `ReqType == 3` filtering are superseded. Migration uses
stable source choice IDs; the formerly constant facial-style byte stores Eye Style. No extra transport
fields or column are required.

The authored primary SKIN has 22,163/22,487 vertices, 336 sequences and 24/25 events. Skin-extra/head
keeps its full atlas. Tail/feet need compositor regions 8/9. Legacy button ordinal 17 needs exact race-20
metadata to activate the expanded picker.

Ordinary eye-glow fallback is now 1700, with explicit DK/Primalist effects preserved. Helmet coverage
is 550 variants for 275/277 installed families. BloodKnight_D and AhnQiraj_A have no matching named Retail
variant; visibility condition 32 remains undocumented.

The current acceptance record still says live visual acceptance pending after the latest repair.

## Creature ports and Forgotten

The [shared creature pack](sources/EsteriaWoW/tools/creature_race_pack.py) stages all four species together:

- Naga has both genders and six skins; helmets and feet are intentionally hidden.
- Tuskarr is male-only with seven skin/hair/color/features choices. A later feet/robe repair rounds feet
  and keeps calves visible. Fresh visual acceptance after that install remains pending.
- Vrykul is male-only with six skins/styles/features and five hair colors. Preview/display scale is
  reduced; Horde 57 remains supported server-side but hidden in creation. Language and hair bindings
  have later repairs.
- Forgotten is the visible name for ThinHuman 58/59. Asset paths, `Th` prefix and binary names stay
  `ThinHuman`. It has four skins/styles/colors, one face and seven facial-hair choices. Boot/cloak/
  helmet fitting and material repairs are in
  [the equipment tool](sources/EsteriaWoW/tools/thinhuman_equipment_repair.py).

Female UI entries for the three male-only species select the male body and reuse male art; they do not
represent authored female models. Latest equipment/chat/naming repairs still need the stated retests.

## Darkfallen and older repairs

Darkfallen 43/44 share displays 60028/60029 but keep distinct faction identity. Both visible names are
Darkfallen, so faction/portrait logic uses actual ID or an unambiguous file string. The older hard-coded
32-race select path required runtime extension.

The pack filters skin/body rows against available textures while preserving compatible Blood Elf hair
references. Starts, racials, languages and skill eligibility have dedicated migrations.
[Server racial source](sources/EsteriaWoW/modules/mod-custom-server/src/darkfallen_racials.cpp) and
[the packer](sources/EsteriaWoW/tools/darkfallen_race_pack.py) are included.

Kul Tiran/Illidari failures also needed missing physical M2/SKIN payloads; consistent DBCs and extension
load logs could not replace those files. HD migration/rollback tools remain historical recipes.

## Legacy identity drift to reconcile

Current client ChrRaces says 24 Fel Orc, 25 Broken, 26 empty, and has no 27 row. Server SQL/registry policy
says Alliance Broken, Forsaken, Horde Pandaren and Horde Broken. These are verified differences.
Reconcile DBC, SQL overlays, UI, bot policy and saved characters before moving or expanding these IDs.
Do not apply a blanket donor-table replacement to resolve them.
