# Runtime DLLs and every Esteria binary catalog

[Back to the guide](README.md)

## The three race/runtime components

| Component | Loader |
| --- | --- |
| `races-64-esteria.dll` | WXL, `Extensions\races-64-esteria\` |
| `z-darkfallen-character-select.dll` | WXL, `Extensions\z-darkfallen-character-select\` |
| `EsteriaAppearance.dll` | Permanent `Wow.exe` import, client root |

Sources:

- [MoreRaces.cpp](sources/WarcraftXL/extensions/races-64-esteria/MoreRaces.cpp)
- [DarkfallenCharacterSelect.cpp](sources/EsteriaWoW/wxl-races-patcher/DarkfallenCharacterSelect.cpp)
- [NativeAppearance.cpp](sources/EsteriaWoW/client-customization/NativeAppearance.cpp)

All three are Win32/x86 DLLs for client build 12340. Their source is included. The installed manifests,
entry names and versions are in [current-state.json](evidence/current-state.json), and every observed
DLL's hash is in [CLIENT_ARTIFACTS.md](reference/CLIENT_ARTIFACTS.md).

### 64-race extension

The original source is under `AzerothPlex\build\wxl-core\extensions\races-64-esteria\MoreRaces.cpp`;
the installed client directory originally contained the DLL, README, verifier and manifest.

The extension validates the customized `ESTERIA_CLIENT_FOUNDATION_V3` image and patch-site bytes.
It allocates a 64-race/two-gender model table, copies the original 0x100-byte table into a 0x200-byte
table, redirects eight references, expands clear/cleanup counts and extends the fallback race-name table.
It preserves existing name pointers and supplies fallback pointers for later slots.

It also adapts the extended-race restriction branch. It does not erase identity checks or edit the
executable on disk. The expected character-limit byte at `0x00464C4F` is checked as 0x64 and preserved;
the 100-character change belongs to the existing client foundation.

The manifest declares WXL ABI 1.1, extension ID `races-64-esteria` and entry
`races-64-esteria.dll`. Build using the WarcraftXL extension target discovered by its CMake source.
A direct x86 compilation can use the included `include/wxl/PluginApi.h` and Windows SDK; follow the
actual project build settings and export contract. The full WXL build additionally needs its vendor
dependencies, which are not duplicated in this source handoff.

The extension is specific to the audited customized baseline. A generic stock 12340 executable is not
equivalent. Keep `HasExpectedClientImage()` and per-site checks. Source for the original foundation
injection itself was not found in the captured trees; obtaining the verified baseline is a replication
prerequisite, not a reason to bypass the fingerprint.

### Character-select runtime extension

The folder begins with `z-` and its manifest's entry is `z-darkfallen-character-select.dll`.
A second older `darkfallen-character-select.dll` exists in the directory, but filesystem presence alone
does not prove it loads. Use the manifest and runtime log to identify the selected entry.

The source grew from Darkfallen roster diagnostics into the select/runtime bridge. It preserves a
bounded roster record size of 0x198, correct model-descriptor/load hooks, Darkfallen hair safety clamps
and the first/last-name client validation patch. It deliberately does not overwrite Mag'har's native
CharSections variation hierarchy with UI counts.

Use [build-runtime.bat](sources/EsteriaWoW/wxl-races-patcher/build-runtime.bat). The output is
`darkfallen-character-select.next.dll`; the runtime installer copies that reviewed result to the
manifest's entry name. The manifest requires the 64-race extension.

### Independent appearance helper

`Wow.exe` imports the helper directly; there is no WXL subscribe/load/API dependency for customization.
[NativeAppearance.def](sources/EsteriaWoW/client-customization/NativeAppearance.def) defines the exported
ABI. [HaranirMaterials.inl](sources/EsteriaWoW/client-customization/HaranirMaterials.inl) implements the
shared runtime texture generation/loading path.

The helper supplies:

- Independent option count/labels/value/cycle/preview/restore/randomization through the existing Lua
  customization callback.
- Decoding packed stock and extended appearance fields.
- Skill eligibility aliases for actual extended-race IDs.
- Wide SKIN start/index handling and restoration of prepared geometry.
- Cosmetic geoset and material selection, followed by equipment visibility rules.
- Creation/roster extension handling and late network-appearance restoration.
- Completed-unit-update observation and component-free cache cleanup.
- Compositor BLP creation, client-owned layer buffers and render-material references.

The permanent patcher is
[native_appearance_patch.py](sources/EsteriaWoW/tools/native_appearance_patch.py). It validates the exact
source executable, foundation signature, instruction bytes and Lua callback table before adding the
`.eapp` section/imports/redirects. It checks for unsupported image features rather than blindly writing.

Packet order is `skin, face, hairStyle, hairColor, facialStyle`. Creator-object offsets are hairColor
0x24, skin 0x28, face 0x2C, facialStyle 0x30 and hairStyle 0x34. Confusing those orders caused the initial
misrouted selectors.

## Catalogs in the client root

These are generated data consumed by the helper, not standalone libraries or server database files.
Keep the matching catalogs with the DLL, client model paths and codecs.

| File | Purpose and generator | Captured count |
| --- | --- | ---: |
| `EsteriaAppearance.bin` | Shared Skyborne/Mechagnome option descriptors; expanded/mechagnome packers | 6 profiles |
| `EsteriaAppearanceGeometry.bin` | Prepared SKIN arrays; extended by later ports | 17 profiles |
| `EsteriaAppearanceMaterials.bin` | Shared direct material bindings, notably Skyborne/Mechagnome | 792 records |
| `EsteriaHighmountain.bin` | Highmountain geometry/material/face selections | 1,047 records |
| `EsteriaEarthen.bin` | Earthen geometry/material selections | 300 records |
| `EsteriaHaranir.bin` | Haranir geometry/material/layer selections | 1,492 records |
| `EsteriaHaranirTextures.bin` | Compressed source-derived Haranir RGBA layers | 986 images |
| `EsteriaVulpera.bin` | Vulpera cosmetic/material and equipment-dependent selections | 2,051 records |
| `EsteriaVulperaTextures.bin` | Compressed source-derived Vulpera RGBA layers | 392 images |
| `EsteriaNaga.bin` | Naga five-field geometry/material selections | 40 records |
| `EsteriaNagaTextures.bin` | Naga runtime texture layers | 36 images |
| `EsteriaTuskarr.bin` | Tuskarr selections, including body/equipment mappings | 58 records |
| `EsteriaTuskarrTextures.bin` | Tuskarr runtime texture layers | 42 images |
| `EsteriaVrykul.bin` | Vrykul selections and material bindings | 80 records |
| `EsteriaVrykulTextures.bin` | Vrykul runtime texture layers | 39 images |
| `EsteriaThinHuman.bin` | Forgotten selections; technical namespace remains ThinHuman | 46 records |
| `EsteriaThinHumanTextures.bin` | Forgotten runtime texture layers | 32 images |

Counts come from the installed headers, not old documentation that described fewer initial profiles.
Sizes and SHA-256 are in the artifact catalog.

### Binary formats

All catalog headers begin with little-endian uint32 magic, version and count.

- **EAPP / version 2:** fixed shared profile with race, gender, option count and 16 descriptors. A
  descriptor carries field offset, radix count/factor and optional geometry mapping. This catalog's
  16-descriptor limit does not limit specialized Highmountain/Haranir codecs.
- **EAGM / version 1:** 128-byte terminated model path, payload size and prepared SKIN payload per
  profile. The native loader checks ranges, palettes, vertices and triangle windows.
- **EAMT / version 1:** shared material-selection records; exact layout is in the native structs and
  packers.
- **EHM1 / version 1:** specialized bounded selections. Each 156-byte record includes gender, kind,
  target/value, up to three packed selectors and a terminated 128-byte material path.
- **EHT1 / version 1:** compressed RGBA image bank with per-image identity/layout and offsets. Read the
  shared native texture-bank structs for the exact descriptor shape; it is not an MPQ or a BLP archive.

Kind-specific interpretation matters: geometry, face/material, layered composition and equipment hides
must follow the matching helper version. Do not hand-edit counts or assume every EHM1 record has the
same rendering action.

## Persistence tiers

| Tier | Families | Contract |
| --- | --- | --- |
| Five bytes | Skyborne, Mechagnome, Vulpera, creature ports | Existing creation/roster/DB fields |
| Six bytes | Highmountain, Earthen | Unused creation outfit byte; HXE1 roster trailer; low padding word |
| Five + uint64 | Haranir | HRC1 creation trailer; HXE2 roster trailer; unit/object padding words |

For Skyborne, for example:

| Stored byte | Packed meaning |
| --- | --- |
| skin | skin + 5 × eye |
| face | face + 10 × beard |
| hairStyle | hairstyle + hairstyleCount × ears |
| hairColor | hair color |
| facialStyle | eyebrows + 4 × feathers + 8 × feather color |

Client/server validation must agree on option ordering and prerequisites. Additional randomizer and
preview state uses the same validated descriptor set, not separately invented counts.

## Lifetime and calling convention rules

These rules came from proven live failures:

- Native x86 bool returns are read from `AL`; testing all of EAX can suppress stock setters.
- The client allocator is `stdcall` with the checked `ret 16` fingerprint. The failed cdecl candidate
  double-cleaned the stack.
- Allocate compositor buffers through the client's allocator when its destructor will free them.
- Maintain texture refcounts and dirty flags when replacing existing layers.
- Do not register `UNIT_FIELD_PADDING` with the unsupported old-value observer cache.
- Read extra fields after completed object updates; reject item/non-unit objects before Unit access.
- Clear component address-keyed caches before stock free so address reuse cannot inherit another race.

Runtime images are cached below
`Interface\AddOns\EsteriaAppearanceCache\<family>`. The client directory must be writable. This cache
does not store character choices and can be rebuilt; database appearance fields are the persistent state.

## Rebuild and deploy

[build-native.bat](sources/EsteriaWoW/client-customization/build-native.bat) uses MSVC x86, C++20 and
static CRT. It compiles the DLL and three native harnesses: appearance ABI/transport, materials/lifetime,
and customization choices. It includes the generated server headers through their normal relative paths.

Stage the helper without touching the loaded DLL. Generate any required executable changes from the
verified original baseline using the current patcher. Run checks, close WoW/Eclipse, make hash-verified
backups, install the reviewed pair and catalogs, then start a fresh client.

A later catalog/helper-only port may need no new executable patch. Haranir and Vulpera use existing
redirects; copying an old patched executable during such an update can undo the accepted teardown repair.

## Other installed DLLs and extensions

The artifact/manifest audit also inventories WarcraftXL, loader/proxy/decoder/support DLLs and installed
extensions for DB2/DBC, modern assets, zoom, weather/vegetation, housing, loot beams, Plex and other features.
These are source-installed or supplied components with separate ownership, not all authored race DLLs.

Available WXL source is included. Vendor libraries, CoA visuals, legacy client libraries and independent
extension repositories are not claimed to have source here merely because a binary is installed.
For broader server/module content use [05](05-SERVER.md); for exact observed entries/hashes use
[the artifact reference](reference/CLIENT_ARTIFACTS.md).
