# Esteria Retail race retroport and addition pipeline

Drafted October 2, 2026, from the five referenced Codex chats and their current local implementation.

This is an operator guide and design draft. It describes future work; no conversion, code change, build,
database import, client deployment, or server restart was performed while preparing it.

## 1. What this pipeline produces

A playable race needs two completed parts:

1. **A Wrath asset port:** models, SKINs, animations, attachments, textures, cosmetic collections and materials.
2. **An Esteria addition:** stable race identity, appearance encoding, client rendering, persistent choices,
   DBCs, server startup data, languages, creator/selection UI, portraits and verified deployment.

A successful asset conversion completes only part of the first item. A visible creator model completes
only one rendering path. Neither establishes that the race is playable or that every Retail feature exists.

The repeatable sequence is:

```text
Define race and scope
  -> reserve identifiers and freeze source build
  -> discover and close the source dependency graph
  -> convert and prepare playable geometry/animation/materials
  -> define and freeze the appearance codec
  -> integrate rendering, packets, persistence and race compatibility
  -> merge DBCs, startup data, GlueXML and portraits
  -> stage and validate a complete package
  -> back up and deploy the matching client/server package
  -> accept creator, selection, gameplay, relog and regressions separately
```

Use each stage's output as the next stage's input. Save a receipt at every boundary so an interruption
resumes from a verified checkpoint rather than restarting or assuming an incomplete installation succeeded.

## 2. What the five ports actually established

### Identity and compatibility

These are the reviewed Esteria allocations, not IDs to copy into a new race.

| Race | Retail ID(s) | Esteria ID(s) | Visual family | Gameplay compatibility |
| --- | --- | --- | --- | --- |
| Mag'har Orc | 36 | 45, Horde | Orc | Orc |
| Highmountain Tauren | 28 | 46, Horde | Tauren | Tauren |
| Mechagnome | 37 | 47, Alliance | Gnome | Gnome |
| Earthen | 84/85 | 48 Alliance, 49 Horde | Dwarf | Dwarf / Orc |
| Haranir | 86/91 | 50 Alliance, 51 Horde | Night Elf | Night Elf / Troll |

Retail identity, Esteria identity, visual family and legacy gameplay mask are separate concepts. Haranir
Horde illustrates this: it uses a Night Elf visual family and Troll gameplay compatibility while remaining
Haranir race 51. Neither its display name nor its skeleton determines its faction.

### Mag'har: reuse a working skeleton/model when that is the correct scope

The initial converted Retail geometry produced mostly invisible bodies. The working version returned to
the installed HD Orc2 models and baked the Retail appearance into their UV layout. It retained nine skin
colors and nine independent face textures per gender, with the working Orc hair/facial geometry.

The face repair required projecting the Retail face through the target model's UVs. Unverified rectangular
crops and a palette-byte experiment did not solve it. A second confirmed problem was an invalid facial-hair
overlay. Backup MPQs left under `Data` were also mounted and overriding the corrected files.

The final fix combined correct UV baking, correct overlay routing and removal of backup archives from the
mountable directory. Later work restored true race names/portraits and client language eligibility. Both
genders' faces, skin/face cycling and the later chat/UI touchups received user confirmation.

**Reusable lesson:** a compatible HD base plus source-derived appearance can be a valid scoped port, but
it is not a claim that all Retail geometry, face morphs or independent customization controls were ported.

Primary implementation: `tools/retroported_race_pack.py`, `tools/race_touchup_pack.py`.

### Mechagnome: collections, materials and inherited animations are distinct work

The body was merged with its mechanical collection, preserving four arm upgrades, two leg upgrades and
twenty modifications. Independent controls were packed into the five normal appearance bytes. The creator
exposes twelve controls, hiding the female facial-hair control whose only value is the default.

The first playable test confirmed creation, login, chat and customization, but exposed missing movement,
combat and emote animations. Only the child skeleton's 61/63 sequences had survived. The repair merged
CRC-matched parent tracks into 352/359 sequences, kept child overrides, fixed aliases/variation links,
rebuilt lookups and included the inherited external ANIM files.

Eye color belongs on the opaque eyeball material. The optional additive glow uses separate sprite textures;
binding the iris atlas to that glow caused bright squares. Male beard meshes needed the source hair atlas,
not the eyebrow/facial overlay. These repairs were installed and checked automatically, but the referenced
chat ends with the final animation/material gameplay retest still requested.

Retail face BONE morphs and restricted DK skin choices remain unported. Racials use the Gnome profile.

Primary implementation: `tools/mechagnome_race_pack.py`, `tools/mechagnome_animations.py`.

### Highmountain: the first complete six-byte transport and face-shape bake

Twenty changing male controls and twenty-two female controls exceeded the five-byte representation.
Highmountain added a sixth appearance byte across creation, character enumeration, save/load and nearby
player updates. All five male/four female face BONE variants were baked into geometry.

The initial implementation then exposed several independent failures:

- Sparse DBC lookups still indexed encoded values after validation had normalized them.
- A native boolean wrapper tested EAX instead of AL, skipping ordinary races' material setters.
- Head geometry was treated as an exclusive cosmetic group and hidden.
- Face transforms were applied around the model origin instead of each facial bone's bind pivot.
- Iris materials retained unsupported Retail shader/sampler behavior.
- Incomplete parent events/material tracks caused talking invisibility, dance fading/crashes and bad sheathing.
- Registering an observer for an unsupported padding field corrupted adjacent NPC memory on logout/exit.

The final animation repair restored parent events, including sheath triggers, plus skeletal, attachment,
opacity, UV and camera tracks. The field-observer registration was removed; the helper reads completed
updates directly and clears component state on destruction. The user confirmed working appearance,
talk/dance/equipment, repeated logout/relog, ordinary-race logout and full client exit without crashes.

Racials/startup use Tauren compatibility. Independent Retail controls are available in the creator; the
stock barber still has its legacy combined-value interface.

Primary implementation: `tools/highmountain_race_pack.py`, `tools/highmountain_integration.py`,
`tools/highmountain_appearance.py`, `tools/highmountain_faces.py`, `tools/highmountain_complete_tracks.py`.

### Earthen: correct saved data can still be overwritten by the client

Earthen reused the six-byte path for both factions and sixteen independent controls per gender. Its models
retain 361/355 animation sequences and 39/40 event tracks. The converted dance lookup also needed rebuilding.

The database and network carried the correct non-default bytes, but stock initialization clamped the
render component to ordinary DBC values. Restoring them only in an early update callback did not work.
The shared callback now finds the owning Player by component pointer, reads validated player data and
restores the encoded appearance after the stock sanitizer. It also works when no earlier callback captured
the component. Cached context is erased when the component is freed.

Character Select needed a separate fix: seed identity/appearance context from the matching roster entry
before the first texture validation. Horde also needed an explicit background mapping. The Gem belt was
moved from the equipped-waist geoset group to its own selector. Boots choose the rounded foot mesh; bare
feet choose the toe mesh. The user confirmed all reported follow-ups fixed.

Face textures are present, but the ten Retail face BONE morphs were not implemented because duplicating
them with all accessories exceeded the SKIN budget. Retail racials remain unported.

Primary implementation: `tools/earthen_race_pack.py`, `tools/earthen_touchup.py`.

### Haranir: larger persistence and runtime composition

Haranir retained twenty-nine male/twenty-eight female ordinary controls. The data needs eleven used bytes
within a thirteen-byte contract: five stock bytes plus an eight-byte extension. It widened
`characters.extraAppearance` to BIGINT UNSIGNED and added race-specific creation/roster transport while
preserving older races' packet formats.

The base bodies retained 401/397 sequences and 37/36 events. Full-resolution collection merging exceeded
uint16 SKIN limits; the authored second reduced collection LOD retained every selectable accessory style
and produced 57,411 male/54,660 female combined vertices. Native palettes retain the established 75-bone cap.
The Nose selector retains authored face meshes; this source graph did not require an additional BONE bake.

Runtime composition follows source texture sections/layer order for skin, fur, paint, hair/highlights,
eyesight and accessories. A dynamic cache avoids baking every possible combination in advance.

The first live test exposed invalid generated BLP headers and rejected cache filenames. Absolute paths
also failed. The working repair feeds validated BLP buffers to native decoders with client-owned memory
and reference-counted materials. An initial allocator declaration used the wrong calling convention and
crashed; it was rolled back and corrected to the checked native ABI.

The user confirmed both genders' textures, fur, most controls, Character Select and in-game rendering.
**The feet-control issue is explicitly deferred.** Loincloth-color behavior was not separately conclusively
accepted in the chat. The later standard-label restoration passed its Lua check, but its requested fresh
Haranir-to-Draenei retest has no subsequent user confirmation in the referenced chat. Do not report these
as completed live checks. Retail racials and a replacement independent-control barber remain outside scope.

Primary implementation: `tools/haranir_race_pack.py`, `tools/haranir_render_repair.py`,
`tools/haranir_live_render.py`.

## 3. Workspace and existing tools

Use the current tools as references rather than writing another converter or generic framework first.

| Location | Role |
| --- | --- |
| `R:\Users\Zach\Documents\GitHub\EsteriaWoW` | Playable-race integration and deployment |
| `R:\Users\Zach\Documents\GitHub\wow-race-retroporter` | Source configuration, manifests and pipeline scaffold |
| `R:\Users\Zach\Documents\GitHub\RetroPorter` | Working `retroporter` discovery/conversion tooling |
| Installed `wotlkconv` | CASC, DB2, M2/SKIN/SKEL/ANIM and BLP conversion |
| `G:\RetroPorterWork\<slug>` | Discovery reports and converted/derived assets |
| `C:\Users\Zach\.codex\tmp\<slug>` | Install/build staging used by recent ports |
| `C:\Users\Zach\.codex\backups\<slug>-<timestamp>` | Recent rollback packages and install receipts |
| `G:\3.3.5a - Dev` | Reviewed development client; verify before each deployment |

The scaffold's `raceporter fetch/plan/build` commands are not a complete one-command Esteria installer.
The completed ports combined its configuration with `retroporter`/`wotlkconv` and race-specific Esteria
scripts. Do not treat a scaffold stage marked complete as proof of converted or installed assets.

Its target-ID configuration also contains older proposals: for example, `mechagnome: 22` conflicts with
Esteria's implemented race 47. Reconcile configurations against the installed Esteria contracts before
using them. Do not propagate those proposed IDs into the live server.

The latest customization implementation is `client-customization/EsteriaAppearance.dll`, imported by
the patched executable, independently of WXL customization APIs. WXL still provides the existing 64-race
foundation and other features. Early chats discussing a WXL customization implementation are superseded
by the later native helper. A new race does not automatically require another executable patch.

## 4. Start every new race with this worksheet

Create `.agents/plans/<slug>-port/<slug>-port.REQUIREMENTS.md` and fill every item before implementation.

### Identity and source

- Race name, project slug, Retail race ID(s), Retail ChrModel ID(s), male/female FileDataIDs.
- Source product, region, locale, version, build key and CDN key.
- Esteria target ID(s), faction(s), paired-race relationship and exact client file strings.
- Visual base family, separate legacy gameplay/skill mask race, startup profile and allowed classes.
- DBC/display/model/customization/outfit/name allocations with collision evidence.
- Whether the target already has characters or startup rows; appearance migration policy if it does.

### Feature scope

- Every ordinary control and choice per gender, including source choice IDs and dependencies.
- Explicit treatment of NPC-only, internal, restricted and class-specific choices.
- Face texture support versus actual BONE/mesh face-shape support.
- Collection accessories, fur/paint/material layers, eye/glow behavior and equipment overrides.
- Required movement, combat, emote, talk, cast, mount and weapon-socket behavior.
- Whether gameplay uses a compatibility racial profile or newly implemented Retail abilities.
- Creator controls, Character Select, in-game rendering, nearby-player visibility and persistence.
- Barber scope: existing combined-value behavior or a separately implemented independent-control UI.
- Male/female portraits for each faction, lore and tooltip text.
- Named deferred features and an acceptance test for each included feature.

### Operational inputs

- Actual client/archive/server-DBC locations, active locale and effective archive precedence.
- Current executable/helper/catalog fingerprints and source revision/tool versions.
- Available disk space for copied archives, conversion, backup and the previous server image.
- Build authorization when native/server changes require compilation; executable-write authorization
  only if a new executable patch is actually required.

**Gate:** a new race has a coherent identity, explicit scope and complete identifier allocation. Never
reuse an occupied ID or silently transform existing characters into a new race.

## 5. Stage A: freeze the source and discover the full graph

1. Inspect the configured source and cached reports before extracting anything.
2. Pin the actual build, product and content/encoding keys. Keep the source immutable after acquisition.
3. Discover the male/female models and all applicable customization records from the same build.
4. Record stable FileDataIDs, logical paths where known, hashes and dependency edges.
5. Filter choices using their actual source requirements, recording each exclusion and its reason.

The discovery graph should include the relevant relationships among:

- `ChrRaces`, `ChrModel` and race/model links.
- `ChrCustomizationOption`, `ChrCustomizationChoice`, `ChrCustomizationElement`.
- Requirement records and prerequisite-choice relationships.
- Customization geosets, materials, BoneSets, texture resources and model collections.
- `ChrModelMaterial`, `ChrModelTextureLayer` and component texture layout/section records where needed.
- Base M2s, all required SKIN/LOD files, referenced child/parent skeletons, ANIMs, BONEs and BLPs.
- Hard TXID dependencies outside the customization inventory, including eye lenses, glow and environment maps.

For local CASC input, use the World of Warcraft parent folder containing `.build.info` and `Data`, rather
than `_retail_`. The reviewed local Retail source was `G:\Blizzard\World of Warcraft`, product `wow`.
For future online input, fetch only the reachable FileDataIDs; do not require or download a full client.

Save `reports/discovery.json`, `reports/asset-plan.json`, a pinned build record and a dependency inventory.
If the source updates, start a new explicit source version; do not mix new layers with old skeletons.

**Gate:** every included control has a traceable source definition and every required asset has a pinned
identity. A missing encrypted/unavailable dependency is a named checkpoint, not an invented replacement.

## 6. Stage B: convert, then prove dependency closure

Run the working converter against the planned files, retaining raw inputs in ignored source caches and
derived outputs under `G:\RetroPorterWork\<slug>`. Target model files should become Wrath-readable MD20,
with compatible SKINs, external animation handling and BLPs.

After conversion, walk the output models and catalogs again:

1. Resolve every referenced texture, SKIN, ANIM and collection input.
2. Compare planned IDs with successful conversions and omissions.
3. Fetch only missing reachable dependencies using the pinned content/encoding keys.
4. Convert those additions and re-run closure checks.
5. Check hashes and decoded structure, not just the existence of a filename.

Earthen initially omitted nine customization textures; Haranir omitted twenty-five. The Mag'har chat also
showed that a converter reporting zero failures can still have missing model references. A plan can be
incomplete even if every file it selected converted successfully.

Use race-specific asset paths such as `custom\<slug>\native\male\...` to isolate the port. Sharing a known
working model, as Mag'har does, is an explicit decision; do not overwrite stock models accidentally.

**Gate:** the playable runtime dependency closure is complete. Report planned, converted, recovered,
excluded and unresolved assets separately.

## 7. Stage C: prepare complete playable models

### Choose the geometry strategy from the actual source

Use a working compatible HD base with baked appearance when that satisfies the selected scope. Otherwise
retain the converted base model and merge its authored collection geometry. Do not pick the strategy from
the skeleton-family label alone: similar bones do not prove matching vertices, UVs, materials or bind pivots.

Before merging, match collection bones to player bones by proven identity, such as the existing CRC checks.
Retain parents, bind transforms, animation links, weights, attachments and material assignments. Remove only
explicitly excluded source choices. Every included style must remain selectable after preparation.

### Check both kinds of geometry limits

- SKIN uint16 addressing must remain within the checked 65,535 budget, including rebased collection indices.
- Mesh/triangle windows and native draw-start/index-buffer paths must also fit the runtime implementation.
- Compact each draw's bone palette to the supported native cap of 75.
- Validate submesh ranges, triangles, bone indices, palette indices and all offset/count pairs after merging.

A model can fit the vertex budget and still fail because a large triangle offset is mishandled. The shared
native wide-index/SKIN recovery exists for that separate issue; it does not make uint16 vertex indices unlimited.

When the complete collection is too large, first look for an authored lower LOD that retains every included
style. Haranir used that path. If full face duplication still exceeds the budget, record a scope gap or design
a real runtime morph implementation; never silently delete styles to claim a complete port.

### Restore the entire animation graph

Follow the M2's actual skeleton references through their parent chain. Merge inherited sequences/tracks,
preserving child overrides and verified bone identity. Rebuild sequence lookups from animation IDs and
variations; repair alias/next-variation references after sequence reordering.

Validate all of the following against their actual storage:

- Skeletal translation, rotation and scale.
- Attachment animations and attachment IDs.
- Parent event timestamp arrays, including sheath/unsheath triggers.
- Opacity, color, texture/UV and camera tracks, plus global sequences.
- Every external timestamp/value span against its companion ANIM length.
- Embedded keys after relocation; alias chains must point to the final relocated span.

Do not rewrite an external-file offset as though it points into the M2. Do not fill missing dynamic tracks
with arbitrary constants. A sequence-count check alone missed Highmountain's event and opacity failures.

**Gate:** representative idle, walk/run, jump, sit, dance, attack, cast, talk and sheath/unsheath paths have
valid lookups and complete tracks/events. Final behavior still requires the live acceptance matrix.

## 8. Stage D: define the customization contract before saving characters

Build one authoritative option table per gender. Each entry records the source option/choice IDs, displayed
order/label, allowed choices, prerequisite choices, defaults, geometry selections and material/layer effects.
One UI selector must correspond to one named feature; list any source choice that intentionally changes more.

Changing a prerequisite must restore a dependent feature to an allowed authored default. Highmountain horn
accessories and Mechagnome pupil/eye relationships are examples. Randomize must produce valid combinations.

### Pick the smallest encoding that preserves the requested choices

| Contract | Use it when | Existing example |
| --- | --- | --- |
| Five stock bytes | All independent choices can fit without losing included states | Mechagnome |
| Five stock bytes plus one byte | Five cannot fit; six can | Highmountain, Earthen |
| Five stock bytes plus uint64 | The prior representation cannot retain all choices | Haranir |

The stock byte order is skin, face, hairStyle, hairColor and facialStyle. Native component property offsets
are a separate layout: do not assume packet order equals object-field order.

The existing encodings use mixed-radix packing: combine choice indices with factors derived from the other
choice counts, keeping each byte's capacity at most 256. Decode using the same factors on both client and
server. Include dependency validation in addition to range validation.

For example, Mechagnome's stored skin byte combines `skin + 8 * paint + 24 * eyesight`. Eight skins,
three paints and four eyesight choices need 96 values, so they fit in one byte. The decoder recovers skin
modulo eight, paint from the next factor and eyesight from the remaining factor. This is an existing
race-specific example, not a default formula for races with different choice counts.

Haranir's contract has thirteen available bytes and eleven used packing bins. This means five stock bytes
plus a uint64 extension, not thirteen bytes appended to every packet.

### Freeze the installed encoding

Save a codec descriptor/hash and generate matching client/server definitions from the same data. Once
characters exist, do not reorder choices, change factors/counts or reinterpret stored bytes without an
explicit appearance migration. Stable source choice IDs should remain traceable through that migration.

Validate defaults, extrema, dependent-choice resets and representative complete round trips. Check high
extension values above 32 bits whenever a uint64 format is used. A database column widened to BIGINT is
insufficient if one query reader, packet builder or helper still truncates to uint32.

**Gate:** every included choice is representable, source dependencies are respected and the installed
codec cannot drift silently.

## 9. Stage E: geometry, face shapes and texture composition

### Translate the source choices into native selections

Assign distinct cosmetic groups for accessories that must remain independent of equipped armor. Earthen's
Gem belt needed its own group because the equipped-waist selector otherwise hid it. Keep body fragments
unconditional when they are actually parts of the base body; Highmountain heads were hidden by treating
their source group as an exclusive cosmetic control.

Equipment behavior is part of the selection contract. Define booted versus barefoot meshes, gloves versus
hands, pants/loincloth visibility, helmet effects and weapon attachments. Select the proven mesh using the
actual equipped display state; do not infer boots merely from a foot appearance byte.

### Distinguish face textures from face shapes

Wrath cannot simply load Retail `.bone` customization overrides. Where shape parity is included, translate
the source BoneSet matrices into weighted vertex changes and inverse-transpose normal changes. Apply
rotation/scale around each affected bone's bind pivot, then restore its pivot and authored translation.

Keep UVs, weights, animation data and topology stable unless the source mapping specifically requires a
change. Validate each face variant. Highmountain's successful shape bake is the reference; Mechagnome and
Earthen face texture selectors must not be described as completed Retail BONE morphs.

### Bake or compose to the target UV layout

Map source component sections and layer order to the actual target model UVs. Test skin, upper/lower face,
hair, facial overlays, fur, paint and accessory layers independently. Do not reuse another race's rectangular
crop merely because the textures have the same dimensions.

Mag'har uses UV projection into Orc2. Haranir uses the source component layouts/layer ordering and runtime
composition. The latter is appropriate when the number of combinations makes exhaustive prebaking wasteful.

### Match the decoder used by each texture path

- Body/face compositor layers use the established indexed BLP format; the checked body path uses
  compression 1, alpha size 0 and alpha type 8. Alpha overlays use their appropriate checked alpha format.
- A standard generated BLP header/palette area and complete valid mip offsets are required. Haranir's
  checked cache files use a 1,172-byte header area and mip chains.
- Render-only textures can use the proven BGRA/native decoder path. They are not interchangeable with
  indexed compositor layers merely because both have a `.blp` suffix.
- Eyes use the proven opaque, unlit UV0 iris path where Retail shaders are unsupported. Keep optional glow,
  lens and sprite materials separate and preserve their source relationships.
- Preserve source hair/beard atlas bindings. An eyebrow overlay is not a beard texture.

For dynamic composition, treat cached textures as disposable render output; saved choices belong in the
character data. Haranir caches visited combinations under
`Interface\AddOns\EsteriaAppearanceCache\Haranir`; the client directory must be writable.

Verify the actual runtime loader, decoder and material binding. Successful offline decode does not prove
the client accepts a cache filename. Use the existing checked buffer loader and ownership model rather than
adding global file-loading overrides. Match the allocator's calling convention and checked fingerprint.

**Gate:** every control selects the intended geometry/material/layer in the prepared catalogs, and a
fresh-client capture proves the required textures actually load. No green error texture or unrelated atlas.

## 10. Stage F: integrate every appearance transport and rendering path

Reuse the current native helper and the server's shared compatibility/appearance functions. Inspect all
callers before extending them. New race IDs do not join existing hard-coded predicates automatically.

### Required path coverage

| Path | Contract to verify |
| --- | --- |
| Creator | Correct selector indices, native setters, defaults, dependencies and randomization |
| Character creation | Range/dependency validation and the matching race-specific packet encoding |
| Database save/load | One character transaction, full extension width, preserved old values |
| Character enumeration | Authenticated race/GUID/appearance and bounded mixed-roster extension parsing |
| Character Select | Identity/context established before its first material lookup |
| In-game local player | Encoded bytes restored after late stock clamps and component initialization |
| Nearby player | Full appearance in completed public updates, including later changes |
| Cleanup | Context and cached bytes erased on component destruction/address reuse |
| Barber | Explicit current behavior and preservation of the extra state |

For the six-byte path, Highmountain used the stock creation outfit byte as the race-specific extension,
`extraAppearance` for storage and a GUID/byte `HXE1` roster trailer. Haranir uses a twelve-byte creation
trailer containing uint64 plus `HRC1`, and a GUID/uint64 `HXE2` tail after the retained `HXE1` tail.
The native reader bounds and removes these tails before stock roster parsing. Legacy packet formats remain
unchanged outside the races that opt into the corresponding contract.

Nearby-player transport uses reviewed unused Unit/Object padding words. Verify both the server's public
update visibility and the native field layout before adding a consumer. **Do not register a stock field
observer for padding:** it has no old-value cache entry and previously corrupted neighboring NPC memory.
Read completed updates using the proven hook instead.

Earthen proved that an early update callback alone is insufficient. A new render component can appear
after the callback, and stock sanitization can later clamp encoded choices. Preserve the existing bounded
owner lookup and post-sanitizer restoration. Seed Character Select from its roster entry before the first
skin lookup rather than waiting for later setters.

### Native invariants inherited from the repairs

- Fingerprint the exact supported client/helper/patch sites; preserve foundation and race-table guards.
- Match calling conventions, stack cleanup, registers, boolean AL returns and object offsets.
- Reject non-unit/item objects before accessing Unit fields.
- Follow client allocation, destructor and reference-count ownership; release replaced materials correctly.
- Clear component context before stock cleanup and handle reused component addresses.
- Restore stock material/geometry behavior when the component does not belong to an expanded race.
- Keep the final no-observer-registration repair even if an older document describes the initial registration.

**Gate:** native harnesses cover mixed rosters, malformed/truncated input, the exact encoded patterns,
late overwrites, no-earlier-capture initialization, non-player objects and component lifetime. The live logout
and ordinary-race tests remain mandatory.

## 11. Stage G: DBCs, gameplay identity, startup data and languages

### Allocate and merge against the installed tables

Use `data/retroported-races/allocation.json` and the race manifests as the starting allocation ledger.
Verify the actual effective client DBCs and server database before reserving new values. Current global
ranges are not evidence that an individual ID is unused.

The reviewed race integration touches the relevant parts of:

- `ChrRaces`: actual race identity, file strings, display IDs, team and compatibility metadata.
- `CreatureModelData`, `CreatureDisplayInfo` and any required display-extra/model-information rows.
- `CharSections`, `CharHairGeosets`, `CharHairTextures`, `BarberShopStyle`.
- `CharBaseInfo`, `CharStartOutfit`, `NameGen`, and skill/language eligibility tables where required.
- `Spell` only when the selected racial/spell integration actually needs it.

Build complete merged WDBC tables with valid record sizes, string offsets and preserved unrelated rows.
Fail on allocations owned by another race. Keep display IDs within the actual consuming field's limits;
the earlier invalid 150045/150046 Mag'har display allocation was replaced, not a pattern to reuse.

The current server pack has seven synchronized DBC files: `ChrRaces`, `CharStartOutfit`, `CharSections`,
`BarberShopStyle`, `CreatureDisplayInfo`, `CreatureModelData` and `Spell`. They live under
`modules/mod-custom-server/data/dbc/retroported-races`. Inspect the effective continuation/mount path too;
the presence of an on-disk file does not prove the running container loaded it.

### Add an identity, not a donor-ID substitution

Update the applicable server race enumeration, playable-race bounds/predicates, registry, pairing and
compatibility helpers. Inspect `GetLegacyMaskRaceForRace`, `GetVisualBaseRaceForRace` and
`GetPairedRaceForRace` in `SharedDefines.h`, plus all consumers affected by the new allocation.

Keep the actual race ID in character identity and faction decisions. Map only the intended legacy
eligibility/gameplay checks to the donor profile. Do not put a custom race above 32 into a legacy 32-bit
race mask by a blind shift; trace the current compatibility abstraction and field width.

Clone only the selected startup profile's relevant rows, including start position, race stats, items,
actions, totem models where applicable, starting skills and spells. The recent pack uses
`playercreateinfo`, `player_race_stats`, `playercreateinfo_item`, `playercreateinfo_action`,
`player_totem_model`, `custom_race_start_spell` and `custom_race_start_skill`.
Audit the existing `playercreateinfo_skills`/spell paths where that profile also depends on them.
Provide valid startup data for every class exposed in the creator, including a deliberate DK policy.

### Languages need client and server agreement

| Existing race/profile | Startup languages |
| --- | --- |
| Mag'har / Orc | Orcish |
| Highmountain / Tauren | Orcish, Taurahe |
| Mechagnome / Gnome | Common, Gnomish |
| Earthen Alliance / Dwarf | Common, Dwarven |
| Earthen Horde / Orc | Orcish |
| Haranir Alliance / Night Elf | Common, Darnassian |
| Haranir Horde / Troll | Orcish, Troll language |

Check starting language skills, spells, skill step and persistent eligibility together. Mechagnome's
language rows required skill step zero to match the working startup profile. Mag'har already had its skill
and spell saved, but client eligibility checks hid the skill and rejected chat. Fix that layer rather than
adding duplicate database rows.

The live acceptance check includes language visibility/default language, ordinary chat and chat after relog.
If the saved skill vanishes on load, trace skill eligibility and save/load; if it is saved correctly but
unusable, trace native/DBC eligibility as well.

### Scope migrations and preserve unrelated state

Place new SQL only in `data/sql/updates/pending_db_world/` or `pending_db_characters/` as appropriate.
Back up affected rows and appearances, record unrelated-row fingerprints and import only the named migrations
for this port. Record migration checksums/receipts and read back the actual imported rows.

Reuse the current BIGINT UNSIGNED `extraAppearance` schema where it satisfies the new contract. Do not run
Haranir's schema widening again unnecessarily. Do not alter base/archive/merged SQL or unrelated characters,
bot-refresh data or startup profiles as a side effect of a race addition.

**Gate:** the client, server DBCs, race registry, core compatibility and scoped database rows agree on the
same race and appearance contract. Names/tooltips advertise only implemented racial mechanics.

## 12. Stage H: creator, selection, portraits and labels

Integrate the current UI rather than replacing it with a generic generated creator. Inspect the winning
archive entries before modifying any GlueXML.

Relevant existing files include `CharacterCreate.lua/XML`, `CharacterInfo.lua`, `GlueStrings.lua`,
`GlueParent.lua`, `CharacterSelect.lua`, `ECS_Schema.lua` and `ECS_Integrate.lua`, as applicable.

1. Add exact race-ID metadata, file-string tokens, localized names, lore and faction grouping.
2. Map the race's actual ID to its name and portraits; a donor background model is not identity.
3. Provide both faction background aliases for dual-faction races. `EARTHENHORDE` was missing initially.
4. Add independent controls using the shared callbacks; validate button index versus native descriptor.
5. Reset all stock labels and layout when leaving an expanded race. Haranir left labels 1/2 changed while
   only 3-5 were restored, making Draenei's skin control appear to be its Hair Style control.
6. Display authored names such as `None`/`Gem` where a numeric selector obscures meaning.
7. Preserve the current race-button layout, name-field/customize flow, single-line names and cursor tooltips.

### Portrait workflow

- Start with the supplied gender/faction PNGs and retain those originals.
- Reuse `tools/race_portrait_pack.py` and the installed creator ring/mask treatment.
- Convert derived portraits to BLP with valid alpha/mips and the established art names.
- Creator icons include the established metal border; ECS selection art uses its existing frame/mask.
  Do not accidentally apply the creator ring twice inside the ECS frame.
- Register and package each exact path for both character creation and selection; add character-frame
  portraits where that existing integration requires them.
- Validate male/female and faction-specific art, selection highlights, tooltip name/lore and background.

**Gate:** fresh creator and Character Select screens show the correct race, portraits, faction/background
and control labels; switching back to stock/previous races restores their own labels and behavior.

## 13. Stage I: package the effective client and server outputs

The reviewed client archives are:

- `Data\patch-Z.MPQ`: effective global DBCs and shared integration content.
- `Data\enUS\patch-enUS-Z.MPQ`: locale/shared GlueXML and matching table copies.
- `Data\Patch-R.MPQ`: namespaced race payload where selected by the integration package.

Inspect actual precedence instead of assuming a newly named archive wins. Core character DBC resolution
in this runtime is global-first; updating only the locale copy previously left stale global rows active.
Install matching full global/locale DBCs and the same seven server files. Check every required winning
GlueXML/model/texture entry, including any duplicate entry in another mounted archive.

Prepare a temporary copy of each affected archive, then merge only the required runtime dependency closure.
Preserve unrelated entries and verify hashes/readbacks. Use the repository StormLib tooling; do not assume
7z is an MPQ editor. Exclude generated `(listfile)`/`(attributes)` metadata from ordinary payload import.
Serialize access to the same archive and close lock holders before final replacement.

Use supported compression and keep each classic archive below the checked 2 GiB boundary. Highmountain's
first root archive exceeded that boundary and needed a verified compressed repack. Validate file offsets
and extractability with an independent reader as well as the writer's own round trip.

**All backups belong outside `Data` and other mountable roots.** A renamed `.MPQ` backup can still be loaded
by this client's wildcard support. Mag'har's mounted backups overrode its newly installed textures.

The staged package also includes the helper, matching appearance/geometry/material/selection catalogs,
any required encoded texture bank, server DBCs, scoped migrations, codec manifest and install report.
Preserve existing race profiles/catalogs when adding new profiles.

**Gate:** staged archive entries, helper/catalogs, server tables and migrations form one matching package;
all required files are readable and unrelated payloads remain unchanged.

## 14. Stage J: validate, back up and deploy

### Before deployment

Read the repository's applicable build, C++, SQL and self-review guidance when implementing this design.
Compilation requires explicit authorization under Esteria's AGENTS.md. Use a scratch output for a loaded
helper; never deploy a DLL into an open client.

Run focused existing checks for the changed areas, then only the regression checks needed to cover shared
contracts. Existing references include:

- `tools/test_retroported_race_pack.py`, `tools/test_retroported_race_contract.py`.
- `tools/test_mechagnome_race_pack.py`.
- `tools/test_highmountain_race_pack.py`, `tools/test_highmountain_complete_tracks.py`.
- `tools/test_highmountain_teardown_repair.py` and native lifetime/material harnesses.
- `tools/test_earthen_race_pack.py`, `tools/test_haranir_race_pack.py`.
- `tools/test_native_appearance.py`, `tools/test_race_touchup_pack.py`, `tools/test_race_portrait_pack.py`.

Record test coverage and any required gate that could not run. A passed harness, migration receipt and
ready worldserver are separate evidence from a passed live client test.

### Deployment order

1. Finish the stage and verify executable/helper/catalog signatures, source hashes and codec consistency.
2. Build the helper only if it changed. Build worldserver only if its code changed and the build is authorized.
3. Preserve/tag the previous server image when deploying a new one. Create a SHA-256-verified rollback
   package for every replaced client/server file and affected database row/appearance.
4. Close WoW/Eclipse and other archive/DLL lock holders. Preserve account/WTF and unrelated client data.
5. Verify the live inputs still match the backup/stage expectations. Reject a stale stage or unfamiliar image.
6. Stop only `ac-worldserver` when server data/schema/code are changing. Apply the approved scoped migrations
   and install the matching files while it is stopped; record readback and preserve old character values.
7. Recreate only `ac-worldserver` using the selected verified image and the existing persistent volumes.
8. Wait for ready state, inspect race-loading errors, verify migration receipts and installed file hashes.
9. Launch a fresh client and run the acceptance matrix below.

A helper-only, catalog-only or GlueXML-only repair needs no database mutation or worldserver restart when
the server contract is unchanged. Conversely, installing new client appearance bytes against an old server
that does not understand them is not a valid intermediate release.

The reviewed worldserver-only recreation command, once a matching image is selected, is:

```powershell
rtk docker compose up -d --no-deps --no-build --pull never --force-recreate ac-worldserver
```

Do not use `docker compose down -v`. Do not rebuild auth/database services to deploy a race.

### Rollback

Restore the matched client helper/catalog/archive/executable set and server DBC/image from the install
receipt, with affected clients closed and worldserver stopped when required. Restore only the affected
world rows and any appearance values whose encoding changed. Verify hashes and start the restored server.

If the new contract introduced wider appearance values, retain the widened database column on rollback
unless a separately validated data migration proves narrowing cannot truncate characters. Existing new-race
characters also need an explicit retention/migration/disable policy. Do not delete them to satisfy an
installer's initial empty-target guard.

## 15. Live acceptance matrix

Use both genders and every supported faction. Keep evidence per path; a creator screenshot cannot close
an in-game, persistence or cleanup gate. Start with a fresh process after replacing archives/helper files.

| Area | Required check |
| --- | --- |
| Creator | Bodies/faces visible; each choice changes its named feature; dependencies and Randomize valid |
| Creator transitions | Expanded race to stock and back; gender/faction switch; correct labels/layout/textures |
| Character creation | Every offered class has a valid start; required defaults and full appearance saved |
| First login | Correct faction/location, equipment, intro/cinematic policy and visible full appearance |
| Gameplay rendering | Skin/face/hair/accessories remain correct after later updates and equipment changes |
| Animations | Walk/run, jump, sit, dance, talk, attacks, casting, mount and sheath/unsheath |
| Equipment | Boots on/off, gloves, pants, belt, cloak, helmet and weapon sockets; hide/show toggles |
| Languages | Skill visible, correct default/known languages, chat works before and after relog |
| Character Select | Actual race name, portrait, tooltip, faction/background and saved appearance |
| Persistence | Logout/relog and full restart preserve stock bytes and the full extension |
| Nearby players | Another client sees correct choices initially and after relevant updates |
| Lifetime | Repeated logout/relog, ordinary-race logout and client exit complete without corruption |
| Barber | Current supported controls work and extra choices are retained; gaps recorded honestly |
| Regressions | Stock races plus Mag'har, Mechagnome, Highmountain, Earthen, Haranir and Skyborne as relevant |

Every selectable hairstyle, face, accessory and material choice needs a checked path. For dependency-heavy
controls, also exercise valid prerequisite transitions. Features masked by starter equipment must be checked
with that equipment removed; do not infer that a feet/loincloth choice works because its byte changes.

For appearance failures, compare four concrete states: selected UI choices, stored database bytes, received
player/roster bytes and live render-component fields/materials/geosets. Fix the first divergence rather than
rewriting downstream state without evidence.

For animation failures, capture the selected sequence and its actual event/key spans. For crashes, preserve
the stack, executable/helper hashes and active race/action. A warning, green fallback or successful model
allocation is an observation, not a proven root cause. Keep failed hypotheses in the port report.

### Completion states

- **Source complete:** pinned dependency closure available.
- **Stage validated:** prepared assets/data/native checks pass.
- **Installed:** live files/rows and running image match the stage.
- **Live accepted:** the agreed matrix passed, with evidence and any explicit deferrals listed.
- **Retail parity:** only claim this if face morphs, included controls, racial mechanics and requested UI
  surfaces actually match the defined Retail scope.

## 16. Practical entry points for repeating the work

These are existing commands and script families, not a ready generic adapter for an unknown race. A new
race first needs its manifest/registration and the race-specific descriptors described above. Do not
substitute a new slug into a tool whose accepted races or allocations do not yet include it.

### Source conversion example

From the installed `RetroPorter` environment, the existing Haranir source workflow is:

```powershell
rtk proxy python -m retroporter doctor
rtk proxy python -m retroporter extract-db2 --race haranir
rtk proxy python -m retroporter discover --race haranir
rtk proxy python -m retroporter plan-assets --race haranir
rtk proxy python -m retroporter convert-assets --race haranir --dry-run
rtk proxy python -m retroporter convert-assets --race haranir
```

For a different source product, use the actual `--source-root`/`--source-product` options on extraction,
planning and conversion as supported by the current CLI. Discovery consumes the already extracted race
DB2 set. Pin and verify the chosen build before conversion.

### Esteria data-preparation references

Run from the Esteria repository, only when performing an authorized implementation:

| Race | Existing data-preparation order |
| --- | --- |
| Mag'har | `retroported_race_pack.py plan/build/validate --race maghar`; retain later touchup repairs |
| Mechagnome | `mechagnome_animations.py`, then `mechagnome_race_pack.py prepare/build/validate` |
| Highmountain | Race prepare, appearance generation, integration prepare, face bake, hard textures |
| Earthen | `earthen_race_pack.py acquire`, `portraits`, `prepare`, `stage` |
| Haranir | `haranir_race_pack.py acquire`, `prepare`, `stage`; preserve current loader repair |

For Highmountain, the concrete scripts are `highmountain_race_pack.py prepare`,
`highmountain_appearance.py`, `highmountain_integration.py prepare`, `highmountain_faces.py`, then
`highmountain_race_pack.py hard-textures`. Follow with its integration `build`/`validate` and the completed
track/head/eye/lifetime contracts. An old initial-stage snapshot is not equivalent to the final accepted port.

The shared native build entry point is `client-customization/build-native.bat <scratch-output>`.
Do not copy an old executable patch command into a new race unless the currently installed executable
actually needs an additional hook and its source fingerprint is verified. Earthen and Haranir reused
existing executable imports.

Each install/refresh tool has its own guards and side effects. Read its action/CLI and latest receipt
before invocation, especially existing-character guards and automatic migration imports. Do not run the
historical install sequence blindly on already populated race IDs.

## 17. Minimum artifacts to retain per race

Keep the following together, outside mountable client directories:

1. Requirements worksheet, identity/DBC allocations and explicit feature/exclusion list.
2. Source build, inventories, dependency graph and content/encoding hashes.
3. Conversion/preparation reports: geometry budgets, sequence/event coverage and material closure.
4. Frozen codec, source choice mapping, client/server catalog/header versions and hashes.
5. Complete staged file manifest and exact scoped migrations.
6. Automated check results plus separately recorded live acceptance by path.
7. Install receipt: prior/current client hashes, server image, server DBC hashes and migration receipts.
8. Verified rollback files/SQL, character policy and known deferrals.

Existing `G:\RetroPorterWork\<slug>\integration\acceptance.json` and backup `install-report.json` receipts
provide the model for this record. Raw Retail assets remain local/ignored. Version the instructions,
manifests and integration code rather than committing source caches or generated archives.

The easiest next port is one whose source graph fits the existing helper catalogs, appearance capacity and
animation/material paths. In that case, add race descriptors and scoped data rather than another transport,
renderer or framework. Extend shared code only for a specific source feature the current path cannot express.

## 18. Evidence and references

All five chats were read, including older pages needed for the original integration steps. Their contents
were used as historical evidence, then cross-checked against current local manifests/scripts and the native
customization README. This document is not a fresh runtime audit; the live results above are the recorded
user confirmations, with unconfirmed/deferred items identified separately.

Referenced chats:

- [Resume Mag'har face asset fix][maghar-chat]
- [Port Mechagnome race][mechagnome-chat]
- [Port Earthen race][earthen-chat]
- [Port Highmountain Tauren race][highmountain-chat]
- [Port Haranir race][haranir-chat]

Primary local references, relative to `R:\Users\Zach\Documents\GitHub\EsteriaWoW`:

- `client-customization/README.md`: native contracts, chronological repairs and reproduction/rollback notes.
- `data/retroported-races/allocation.json` and the five race manifests: implemented IDs and appearance modes.
- `tools/retroported_race_pack.py`: baseline allocations, DBC/UV/BLP/archive integration and validation.
- Race-specific scripts listed in sections 2 and 16, plus their focused contract checks.
- `src/server/shared/SharedDefines.h`: actual identity, compatibility and paired-race helpers.
- Character creation/enumeration, Player save/load and update-field code referenced by those integrations.
- `wow-race-retroporter/AGENTS.md`, source configuration and CLI: source/scaffold boundary.
- `RetroPorter/README.md` and `src/retroporter/cli.py`: working discovery/conversion command boundary.

Older memory guidance helped locate foundation/archive checks. Current chats and source were used to
confirm the architecture; the final native customization behavior supersedes earlier WXL-only guidance.

[maghar-chat]: thread://01a0f1f5-6392-7472-8a83-b0d84b06ff67?hostId=local
[mechagnome-chat]: thread://01a0f629-08d3-7572-96f9-00be2deed0f7?hostId=local
[earthen-chat]: thread://01a0f7f0-55e4-78a1-8d22-d31e99824e83?hostId=local
[highmountain-chat]: thread://01a0f684-d4ad-7bd1-bc05-19bd5c8d62de?hostId=local
[haranir-chat]: thread://01a0fa05-e185-7093-97c0-55de45954e79?hostId=local
