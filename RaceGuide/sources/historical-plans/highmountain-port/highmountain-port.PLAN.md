# Highmountain Tauren complete port

Requested result: RaceID 46, both Retail player models, every player customization category and its
source dependencies, complete inherited animations, Orcish/Taurahe, distinct creation/selection names,
lore and bordered portraits. Preserve the installed Mag'har, Skyborn, Mechagnome and other race profiles.

## Verified source and current limits

- Retail race 28; ChrModel 55/56; player FileDataIDs 1630218/1630402.
- Follow the models' SKID references: child skeletons 1839622/1834492, parents 1839011/1830371.
  The discovery's ChrModel SkeletonFileDataID values 4690423/4690422 actually name decorative M2s;
  using those as player skeletons is incorrect.
- Converted player models initially contain only 15/13 child sequences. The parents contain 349/341.
  Reuse the tested CRC/order-checked animation merge, retaining child overrides and external offsets.
- Initial conversion skips seven Highmountain eye BLPs and excludes shared Human eye/eyesight palettes.
  All materials reachable from customization elements must be fetched and converted.
- Nine source face `.bone` override files were omitted by the prior ports. Full parity requires their
  transforms, alongside texture faces; preserving their raw files alone is not a working port.
- Excluding only internal transmog placeholders leaves 20 male/22 female changing controls, plus one
  fixed jewelry palette per gender. The native helper supports 16 controls and five independent bytes.
  Source horn requirements reduce horn states to 97/65; the remaining selection space still exceeds the
  present per-byte codec. Related material/eye-style conditions must also be honored, not cross-applied.
- Highmountain does not yet have characters or startup records. Tauren donor displays/models are 59/60;
  Tauren startup data already covers ten classes, including the classless extensions.
- Verified language spells: 669 Orcish, 670 Taurahe. Skills: 109 and 115. Startup skill step is 0.
- The requested wow-race-retroporter repository is currently a scaffold: its discover/conversion/
  customization/DBC/SQL/Glue/package stages return actionable blocked results. The installed wotlkconv
  and existing Esteria tools provide the actual conversion path. Read its configured source settings,
  preserve raw assets under its source root, and pin build/version/content keys before additions.

## Staging completed by the preparation tool

`tools/highmountain_race_pack.py audit|prepare|portraits|glue` records every source choice, relationship,
material, geometry and bone set; caches targeted source files with content-key/SHA-256 validation;
merges inherited animations; compacts bone palettes; converts supplied portraits with the installed
metal border; and stages actual-ID Character Select metadata and create/select lore. Its result is
explicitly incomplete for rendering/persistence and has no install command.

Derived integration root: `G:\RetroPorterWork\highmountain\integration`.
Source cache: `wow-race-retroporter\sources\retail\races\highmountain_tauren`.
The existing conversion under `G:\RetroPorterWork\highmountain\output` remains immutable.

## Remaining implementation before activation

1. Extend the standalone native appearance format to cover all Highmountain controls, conditional
   geometry/material selections, and face bone transforms. Continue reading existing version-2 profiles
   without modifying their bytes. No WXL API/loader dependency or executable signature bypass.
2. Add explicit persisted extra appearance data with validated, versioned transport through character
   creation, enumeration, customization/barber, login, nearby-player updates and relog. Authenticated
   server ownership checks and source choice/requirement validation are required. Retain the five
   standard appearance fields for equipment/legacy texture composition; do not steal unrelated fields.
   Determine exact native packet/component redirects from the client binary before coding them.
3. Restore every modern material binding the converter dropped (including horn, jewelry, paint, eyes
   and eyesight). Apply only related choices authored for the active skin/horn/eye/hair selection.
4. Add collision-checked allocations, full matching root/enUS DBCs and seven mounted server DBCs.
   Register Race46 in the live race registry only when rendering/persistence is implemented.
5. Prepare the pending world/characters migrations, explicit Orcish/Taurahe startup spells/skills, and
   native race-eligibility mapping 46 -> 6. Clone verified Tauren startup/equipment/stats/totems. Tooltip
   racial descriptions must match abilities actually implemented; do not advertise Retail spells merely
   because they occur in lore or because Tauren is the compatibility donor.
6. Run the staging check and regression checks for installed races; build/test the standalone helper
   and worldserver only after explicit build authorization (AGENTS.md). Keep executable fingerprint and
   rollback checks intact. Close WoW/Eclipse before replacing archives/helper.
7. SHA-256-verify backups on C:, apply dedicated migrations transactionally, install all winning root/
   locale files and matched native/server artifacts, then recreate only ac-worldserver with --no-deps.
8. Fresh-client acceptance: both genders, every category/choice and dependency, all face shapes,
   movement/jump/dance/sit/combat/talk/weapon/cast, creation, chat languages, selection, login/relog,
   another player's view, helmets/equipment, barber, and existing race regressions.

No server/native builds, live database mutations, race activation or client installation have been done
at the asset-staging checkpoint. Approval is requested only because the repository explicitly prohibits
builds without the user's request; complete source/asset preparation can continue while awaiting it.

## Implementation checkpoint after build authorization

The user explicitly authorized helper/worldserver builds and worldserver-only restart. Implementation now
uses a six-byte codec with dedicated `extraAppearance` character storage and the formerly unused public
unit padding field. Creation transports the extra value in the unused outfit byte; roster enumeration
appends bounded Race46 GUID/value records, stripped before the stock client parser. Prepared statements
and transaction-bound saves keep persisted data tied to the character. Login/creation validate choices.
The existing enum team column remains last, preserving its consumers.

The helper's new Race46 path exposes all 20/22 changing controls, conditional geosets and materials.
Native compositor lookup redirects decode skin/paint/face into the generated DBC rows. All nine bone
shapes are baked into independently selected affected triangles, with inverse-transpose normals and
64136/56344 vertices. CRC-matched inherited animations retain 349/341 sequences. The 229 customization
materials plus seven omitted hard TXID dependencies are recovered with content-key validation.

Both genders' bordered portraits and distinct creation/selection metadata are in the three staged
archives. Full archive validation passes for duplicate IDs, matching root/locale/server data, every
referenced material, mesh/palette limits and preservation of unrelated rows/native catalogs. The native
harness passes with WXL absent, including codec defaults, invalid input and roster trailer bounds.
Highmountain's source/stage check, two-names, character-select, character-limit, Broken and retroported-race
contracts pass. The repository-wide C++ linter reports existing unrelated violations; SQL linter cannot
fetch origin/master because that remote ref does not exist.

Worldserver build is running as Docker build `ugudldegm1qnu5pt51g3kq65v`. No live client/SQL/server data
has been replaced yet. After success, install the verified stage with backups, then recreate only
`ac-worldserver --no-deps --no-build --pull never --force-recreate`. Record ready state and live-test gaps.

## Installed checkpoint

The build completed successfully and image `f4f1eed0909569c864326fc53a823e02cfa237835d5cc9471e0c7d3dc2b85d32`
is running. `highmountain_integration.py install` verified rollback copies under
`C:\Users\Zach\.codex\backups\highmountain-20261001-045931`, applied the dedicated migrations, and installed
the checked client stage and seven server DBCs. Only worldserver was recreated. It initialized in 46 seconds
and logged ready state; port 8085 accepts connections. No Race46 loading or extended schema errors appear.
Client hashes, server DBC hashes, ten race starts and explicit Orcish/Taurahe skill-step-zero rows are verified.
Automated Highmountain/native/Mechagnome/Mag'har-Skyborn and existing UI/race contracts pass.

The user has been asked to launch fresh, test both genders/all controls and face shapes, gameplay animations,
chat, select metadata/portraits, creation and relog, and leave Highmountain visible if any issue needs a live
capture. The source/installation/acceptance report is `G:\RetroPorterWork\highmountain\integration\acceptance.json`.
No live acceptance has been inferred from static tests. Initial racials/startup remain the Tauren profile;
the full independent selector UI is in creation and the stock barber remains a legacy selector UI.

## October 1 live repair checkpoints

The initial live tests exposed a sparse material table getter crash and a large-offset archive read
failure. The repaired native direct getters use resolved rows, with the stock texture cache lifecycle.
Compositor images now use indexed BLPs, and compressed archives stay below 2 GiB. The follow-up shared
fur regression was an x86 bool ABI bug: the wrapper tested EAX instead of AL. Three AL checks restored
stock setters; the user confirmed all other races fixed. Pure material and emitted-thunk ABI checks pass.

The next live test showed missing Highmountain heads. Direct memory capture proved full-face geoset3202
and the selected male face variant19601 were disabled while fragment3201 was enabled. Both base-head
geosets now map to body0, and all nine baked head variants have unconditional body sources. The two SKIN
entries, Highmountain selection catalog and matching native geometry catalog are installed consistently
with backup `C:\Users\Zach\.codex\backups\highmountain-head-20261001-063540`. Head regression checks and
main archive validation pass. Fresh-client visibility and all-face-option acceptance were requested.

The user next confirmed heads load but supplied an elongated-muzzle screenshot. The face bake had applied
BOMT rotation/scale about the model origin, instead of the influenced facial bone's pivot. The corrected
bone-relative bake fixes up to 0.6682/0.8032 units of origin error in male/female vertices. Actual face-zero
forward bounds change from 1.6627 to 0.9989 male and 1.1467 to 0.6903 female. Staged/installed model binary
checks show only position/normal bytes change, preserving weights, UVs, materials and every animation.
The two models were installed with verified backups through the existing archive installer. The
`face-pivots/last-install.json` identifies the backup. Main archive and pivot tests pass; fresh-client
shape acceptance was requested for both genders and every Face option.

## Complete animation-track reconstruction

The user confirmed face geometry and eyes, then reported invisibility during talk, fading during dance,
and equipment remaining sheathed. The first skeletal/opacity repair was disproven by the next live test:
talk remained invisible, weapons stayed sheathed, and dance crashed. The local crash at
`Errors/2026-10-01 07.49.09 Crash.txt` enters event timestamp traversal at `0x008310AC`.

`highmountain_complete_tracks.py` restores the original PEDC parent-event tables, including `$SHL`/`$SHR`
in sheath sequences89/90. It restores source opacity, UV transforms and cameras, and embeds the converted
skeletal/attachment keys in MD20 for every sequence. Alias chains resolve to the final target's spans;
the previous conversion only relocated direct aliases. This preserves all 349 male/all 341 female sequences
and the accepted geometry, materials, textures and SKINs. The check also caught corrupted inherited camera
values and confirms the reconstructed keys are finite, ordered and within serialized bounds.

`rtk proxy python -X utf8 tools/test_highmountain_complete_tracks.py` passes both models, source sheath
events, hand-key equality, alias chains and archive readback. All 43,728 unrelated archive entries compare
byte-for-byte equal. The existing backup installer deploys only the two M2 replacements in rootZ, localeZ
and PatchR; its receipt is `complete-tracks/last-install.json`. Live talk/dance/sword-and-shield attachment
acceptance remains pending a fresh launch for both genders.

Installed with verified backup `C:\Users\Zach\.codex\backups\highmountain-complete-tracks-20261001-082040`.

## Native field-cache corruption and teardown repair

The user confirmed Highmountain gameplay works, then reported logout/exit crashes on every race.
Repeated reports stop at `0x0074604E`, unlinking an NPC object's GUID-field list with a null previous link.
Live reads confirmed correctly initialized lists become corrupted during gameplay. A hardware watchpoint
on NPC 3209 captured the zero write at `0x0040CC70`, called by `0x004D533B` in the field-update cache copy.
The source unit was `0xBFE62080`; copying padding wrote to `0xBFE6351C`, the next unit's GUID-list link.

The native padding callback registration requested a field absent from the stock old-value cache table.
Its lookup fallback produced an offset beyond the NPC snapshot buffer. Removing that registration fixes
the writer; the stock destructor stays unchanged. The sixth appearance byte is read after the object's
virtual update at `0x004D6C86`, preserving network appearance changes without a cached-field observer.
The shared handler rejects non-unit objects before accessing Unit fields. `0x004F16C0` now forgets cached
extra appearance and clears the context before freeing a character component.

The x86 harness checks zero padding registrations, live sixth-byte changes, component-address reuse,
cleared context, guarded item memory, the existing sparse material getters and unrelated race geometry.
Emitted thunks preserve stock continuations and the prior AL bool checks. Foundation fingerprints and
Lua callback validation remain intact. The repository C++ linter fails on existing server/Eluna violations;
the modified standalone native files have no new whitespace/line-length violations.

Only `Wow.exe` and `EsteriaAppearance.dll` were replaced together, with backup
`C:\Users\Zach\.codex\backups\highmountain-teardown-20261001-093630`. Three MPQs and four appearance catalogs
are SHA256-identical before/after. A fresh live client showed all 24 nearby NPC GUID lists intact,
including the formerly corrupted NPC. The user confirmed repeated logout/relog, ordinary-race logout,
full client exit and Highmountain appearance/talk/dance/weapon attachment all worked without issues/crashes.
