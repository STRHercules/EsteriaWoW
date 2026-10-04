# The complete retroporting pipeline

[Back to the guide](README.md)

## 1. Establish the target contract

Decide race ID, faction(s), authored genders, file strings, equipment prefix, classes, starts,
languages, compatibility donor, implemented racials, appearance scope and rollback before conversion.

Use [allocation.json](sources/EsteriaWoW/data/retroported-races/allocation.json), the per-race manifests
and the server registry. Reserve model/display/CharSections/hair/barber/portrait identifiers too.
Player display IDs remain below 65536 because the current `PlayerInfo` storage is uint16; a larger
CreatureModelData row ID does not have that same meaning.

Before allocation, compare effective client DBCs, mounted server DBCs, world SQL overlays and existing
characters. The target owns its ID; importing a donor ChrRaces table wholesale is not an allocation.

## 2. Pin source data

The working orchestrator is [RetroPorter](sources/RetroPorter/README.md), backed by
[Converter](sources/Converter/wotlkconv/pipeline.py).

The source-policy scaffold is
[the requested wow-race-retroporter](sources/wow-race-retroporter/README.md). Its
[sources/retail/build.yaml](sources/wow-race-retroporter/sources/retail/build.yaml) describes online
targeted acquisition, with local CASC as an optional fallback. The actual historical art conversions
also used the installed Retail CASC and Forever beta installations, followed by targeted recovery of
missing reachable FileDataIDs. Document both paths rather than claiming a generic online command
produced every shipped file.

Recorded pins:

| Source | Version/product | Build identity |
| --- | --- | --- |
| Retail modern player ports | 12.1.0.69933 / `wow` | `dcfc90fffd79ba00406ae46f5f657592` |
| Skyborne | 1.60.1.70009 / `wow_classic_beta` | Source manifests in the Skyborne workspace |

The CASC root is the WoW parent directory containing `.build.info` and `Data`, not `_retail_`.
Do not silently use today's Retail data when resuming a completed build.

## 3. Discover the dependency graph

Follow DB2 relationships, not guessed filenames:

1. ChrRaces → ChrModel → CreatureDisplayInfo/CreatureModelData.
2. ChrModel → options → choices → customization elements.
3. Elements → geosets, skinned collections, materials, BONE sets and conditional choices.
4. Materials → texture targets/layers/resources → TextureFileData.
5. Models → SKIN, skeleton, parent skeleton, animations, attachments, events and hard texture TXIDs.
6. Equipment families → race/gender variants → textures/companions and helmet visibility rules.

Use `ChrCustomizationReq` and related requirements to distinguish normal choices, class restrictions,
internal transmog placeholders and dependencies. A numeric requirement type is not a blanket class
filter. The Vulpera v2 repair is the concrete example.

Write discovery, asset plan and inventory reports. Keep FileDataID, source path when known, content key,
encoding key, SHA-256, build and parent/child dependency relationships. Retain unnamed assets by
FileDataID; guessed names are not recovered names.

## 4. Acquire only reachable data

Raw inputs remain immutable in the source cache or external work area. Conversion writes to output
directories. A missing file must be resolved from the pinned graph before source completeness is claimed.

Vulpera used additional external helpers:

- [run_source.py](sources/RetroPorterWork/vulpera/run_source.py): extract the pinned source graph.
- [inventory_source.py](sources/RetroPorterWork/vulpera/inventory_source.py): record source dependencies
  and recover local/CDN data with matching keys.
- [convert_recovered.py](sources/RetroPorterWork/vulpera/convert_recovered.py): convert recovered inputs.

Direct-BLTE recovery is not arbitrary header removal: verify the header/content identity and preserve
the original bytes and recovery report. The Converter cache supplies community listfile, WoWDBDefs and
TACT keys. Discovery still needs source definitions matching the pinned DB2 build.

## 5. Convert art, then make it player-compatible

Generic conversion produces namespaced `output/patch-root/custom/<race>/...` assets. It does not
complete the playable-race integration.

### Models and SKINs

The Wrath target uses flat MD20/M2 version 264 and matching SKIN data. Validate vertex, triangle,
submesh, texture-unit, lookup and palette ranges. Preserve referenced companions and relative paths.

Body and collection geometry must agree on bone indices. Remap by source bone identity/CRC, trim unused
vertices and preserve the selected collection LOD. Haranir's second reduced LOD retains styles within
the vertex budget; dropping half the choices is not equivalent.

Wrath vertex indices remain uint16, limiting referenced vertex numbers to 65535. Triangle **start
offsets** are a different limit. Esteria's wide-index helper reconstructs supported starts and restores
prepared SKIN arrays; it does not make arbitrary >65535-vertex meshes valid. Native palettes are capped
at 75 bones.

### Animations and events

Merge child and parent skeletons while retaining child overrides. Rebuild the animation lookup from
sequence IDs and primary variation. Resolve aliases before relocating track spans.

External sequence spans must be validated against their actual `.anim` companion. If embedded into MD20,
relocate timestamps and values consistently. Never interpret an external offset as an in-model address.

Audit skeletal transforms, attachments, opacity, UV, camera and event tracks. Having a “dance” ID in a
lookup is insufficient if its opacity fades, events are malformed or sheath triggers are missing.
Mechagnome and Highmountain both needed parent sequences; Highmountain additionally needed raw PEDC
sheath events and complete track reconstruction.

### BONE face morphs

When baking a source morph, transform weighted vertices relative to the corresponding bind pivot,
restore authored translation, and transform normals with the inverse transpose. Preserve UVs, weights,
animations and topology. Highmountain's origin-based bake stretched faces until corrected.

Check the static geometry budget. Earthen and Mechagnome face BONE morphs remain outside their shipped
scope. Keep omitted source choices in the audit instead of advertising full Retail parity.

### Materials and textures

Separate body/face compositor layers from directly rendered accessories. Source UV layout determines
which atlas belongs to a mesh; material target names alone can be misleading.

Wrath body/face composition uses validated indexed BLP layers. Direct render materials can use the
supported BGRA/opaque UV0 paths. Preserve mip chains and the standard 1172-byte BLP header where required.

Handle iris and optional glow separately. Use authored conditional colors and requirements. Avoid
enabling DK glow by default, binding iris atlases to glow sprites, or assuming layered Retail shaders
are supported by Wrath. Forgotten helmets needed correct shader table indices and restored alpha-mask
passes, not just a texture swap.

For Haranir/Vulpera/creature layers, preserve source ordering/layout in the compressed RGBA bank.
Runtime-generated BLPs use client-owned buffers and normal reference/destructor semantics.

## 6. Build a stable appearance codec

One independent option need not consume one network byte. Pack choices using mixed-radix descriptors:

`encoded = choice0 + count0 * choice1 + count0 * count1 * choice2`

Every stored byte must fit 0–255. Generate client and server descriptors from the same ordered choices.
Preserve source choice IDs separately from positional indexes. Requirements constrain randomization,
UI selection and server validation.

Five-byte families use stock transport. Highmountain/Earthen need a sixth byte; Haranir needs uint64.
See [the runtime contract](04-RUNTIME.md) and [server transport](05-SERVER.md).

Freeze installed codecs. Reordering choices changes the meaning of saved bytes even if they remain
numerically valid. Vulpera v2 uses an explicit choice-ID migration with before/after and rollback tuples.

## 7. Generate additive client/server data

Build full effective DBCs from the winning archive stack. Rebase string offsets while merging tables,
preserve packed layouts such as CharBaseInfo/CharStartOutfit, reject foreign ID collisions and preserve
unrelated rows.

Core race tables include:

| Data | Responsibility |
| --- | --- |
| ChrRaces | Numeric identity, prefix, file string, models, faction/expansion/cinematic policy |
| CreatureModelData / CreatureDisplayInfo | Asset paths, display/model links, dimensions and scaling |
| CharSections | Body/face/hair/underwear textures, variation/color/flags |
| CharHairGeosets / CharacterFacialHairStyles | Legacy mesh selections |
| CharBaseInfo / CharStartOutfit | Race/class availability and outfits |
| BarberShopStyle | Existing barber compatibility |
| SkillRaceClassInfo / SkillLineAbility | Languages, skills, spells and eligibility |
| Spell | Custom racial/mount entries and client spell presentation |

**Sort CharSections by race, sex, section type, variation and color.** The client cache assumes contiguous
groups. The October 3 exit repair preserved all 547,108 records but reduced reproduced overflows from
65 to zero. Both active Z copies need this invariant.

Server SQL supplies starts, actions, skills, spells, stats, faction and DBC overrides where used.
Generate the dedicated migration rather than importing the entire historical SQL directory.
The full standard server DBC mounts and continuation use cases are covered in [the server chapter](05-SERVER.md).

## 8. Add UI and art

Merge numeric race metadata into creator/selection tables. Keep button ordinal distinct from RaceID.
Add class availability, faction/background/fog/glow/ambience mappings, names, tooltips and male-only
constraints. Use implementation-accurate racial text.

Convert supplied PNGs through the established mask/ring/BLP pipeline and use creator, ECS and character
frame namespaces separately. Extend labels and controls without leaving an expanded race's labels on
a stock race. Preserve Freeborn wrappers and ECS load order.

## 9. Stage and install

Use current root and locale archives as merge bases, plus the separate race asset archive. Do not
install a stale race's whole “latest” archive after other races have been added.

Serialized StormLib access is required. Exclude `(listfile)` and `(attributes)` from user payload
rebuilds, use compressed temporary archives, validate entries and keep final classic MPQs below the
verified offset boundary. A stage must include source/staged hashes and a rollback plan.

Install only after validating the matching DLL/catalog/DBC/SQL/UI set. Closed clients are required for
replacement. Recreate only worldserver when server state needs refreshing. Full deployment and rollback
steps are in [08](08-OUTPUTS-AND-DEPLOYMENT.md).

## 10. Accept the playable race

Record source completeness, stage checks, installed hashes, schema/SQL readback, server readiness and
live acceptance separately. Verify creation, roster, gameplay and exit independently. A working creator
does not prove saved appearance or equipment, and an installed repair is not user-confirmed rendering.
