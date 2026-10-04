# Reproduction recipes and command map

[Back to the guide](README.md)

These are the real entry points found in source. Commands are grouped by stage; they are not a script
to execute against an already-populated live server. First read the installer's current guards, stage
hashes and migration scope. Some initial-port installers require empty target rows/characters.

## Set up a developer copy

Use a complete Esteria checkout at the recorded revision, then apply any needed snapshot source changes.
`sources/EsteriaWoW` is a source overlay, not a replacement for all of AzerothCore. Restore historical
plan subtrees to their original `.agents/plans/<slug>` location if a historical tool resolves siblings
through `__file__`. Keep current active GlueXML snapshots separate from older plan source.

Observed environment: Windows, Python 3.14.4 x64, Pillow 12.2.0, lupa 2.8, capstone 5.0.9 and Converter
0.1.0 from commit `d71523c645ebe1313e15fe47fbea57577adf8c80`. Additional detected packages are recorded in
[python-environment.json](evidence/python-environment.json). Native DLL builds require the x86 MSVC
environment even though Python/StormLib inspection uses x64.

Example setup, using your own checkout locations:

~~~powershell
python -m pip install "Pillow==12.2.0" "lupa==2.8" "capstone==5.0.9" "PyYAML==6.0.3"
python -m pip install "git+https://github.com/Bar3b0n3s/Converter.git@d71523c645ebe1313e15fe47fbea57577adf8c80"
python -m pip install -e "R:\Users\Zach\Documents\GitHub\RetroPorter"
~~~

Install the scaffold's own dependencies if importing its configuration helpers. Its
[pyproject](sources/wow-race-retroporter/pyproject.toml) defines its supported Python/dependency contract.
The captured installed Converter source is retained for byte-level comparison with the pinned release.

Path configuration for the working orchestrator:

~~~powershell
$env:RETROPORTER_RETAIL_ROOT = 'G:\Blizzard\World of Warcraft'
$env:RETROPORTER_WRATH_ROOT = 'G:\3.3.5a - Dev'
$env:RETROPORTER_WORK_ROOT = 'G:\RetroPorterWork'
$env:RETROPORTER_PRODUCT = 'wow'
python -m retroporter doctor
~~~

Other variables: `RETROPORTER_LISTFILE`, `RETROPORTER_DBD` and `RETROPORTER_KEYS`. Several Esteria packers
still use literal `G:` work roots, `C:` stages and `R:` source roots; update the constants in your developer
copy or reproduce that layout. Do not assume those environment variables retarget every packer.

The actual x64 StormLib default is
`R:\Users\Zach\Downloads\battlemon\Client\wdbx-2.4.1.a-extended-dbc\x64\StormLib.dll`.
Use the tool's `--stormlib` flag when exposed, otherwise change `DLL_DEFAULT` in your copy.

Original local commands use the RTK wrapper. It is an output proxy, not part of the conversion format.
Outside this workstation, the equivalent `python`/`docker`/`git` command can run without `rtk proxy`.

## Common source/art stage

~~~powershell
python -m retroporter extract-db2 --race highmountain
python -m retroporter discover --race highmountain
python -m retroporter plan-assets --race highmountain
python -m retroporter convert-assets --race highmountain --dry-run
python -m retroporter convert-assets --race highmountain
~~~

Supported working slugs include `maghar`, `highmountain`, `mechagnome`, `earthen`, `haranir`, `skyborne`
and `vulpera`. Follow each manifest's source product/build. Converted output alone is not installable.

The requested scaffold uses different slug/API conventions such as `maghar_orc` and
`highmountain_tauren`:

~~~powershell
python -m raceporter doctor
python -m raceporter fetch maghar_orc --dry-run
python -m raceporter plan maghar_orc
python -m raceporter build maghar_orc --dry-run
~~~

Those describe the scaffold. Its unimplemented generic adapters must not be presented as a replacement
for `retroporter` and the working Esteria integration code.

## Mag'har legacy port

After the source/art stage:

~~~powershell
python tools/retroported_race_pack.py plan --race maghar
python tools/retroported_race_pack.py build --race maghar
python tools/retroported_race_pack.py validate --race maghar
~~~

The final builder uses Orc2 geometry and Mag'har appearance, including the corrected facial-hair
routing and UV bake. It does not install the abandoned Retail geometry experiment.

The packer exposes `install`, `install-appearance` and `install-runtime` separately. Use `install` only
with a validated stage and the intended first-port server migration. Appearance/runtime repair paths
have narrower purposes and different preserved-file checks. The latest Mag'har/Skyborne select/chat
follow-up is [race_touchup_pack.py](sources/EsteriaWoW/tools/race_touchup_pack.py).

## Skyborne source and native expansion

Use the Forever source explicitly:

~~~powershell
python -m retroporter extract-db2 --race skyborne `
  --source-root "D:\Blizzard\World of Warcraft" --source-product wow_classic_beta
python -m retroporter discover --race skyborne
python -m retroporter plan-assets --race skyborne
python -m retroporter convert-assets --race skyborne `
  --source-root "D:\Blizzard\World of Warcraft" --source-product wow_classic_beta
~~~

Initial curated visual preparation is `tools/skyborne_visual_pack.py prepare`. The installed native
mode is recorded in `data/retroported-races/skyborne.json`; the curated builder refuses to downgrade it.

Native appearance preparation:

~~~powershell
python tools/expanded_appearance_pack.py prepare
cmd /c client-customization\build-native.bat C:\Users\Zach\.codex\tmp\native-appearance
python tools/native_appearance_patch.py --source C:\Users\Zach\.codex\backups\native-appearance-20260930-220154\Wow.exe
python tools/expanded_appearance_pack.py build
python tools/test_native_appearance.py -v
~~~

The named executable is the original verified backup, not the already-patched live executable.
On another machine, supply your matching backed-up baseline using `--source` and optional `--output`.

With the stage and saved-character mapping reviewed, the installer is
`expanded_appearance_pack.py install`. Its character migration is
`data/sql/updates/pending_db_characters/rev_20260930004000000.sql`. Preserve the exact five-byte codec,
external animation spans and hairstyle-dependent feather geometry. Touchups also update portrait and
chat eligibility.

## Mechagnome

~~~powershell
python tools/mechagnome_race_pack.py prepare
cmd /c client-customization\build-native.bat C:\Users\Zach\.codex\tmp\mechagnome
python tools/mechagnome_race_pack.py build
python tools/mechagnome_race_pack.py validate
python tools/test_mechagnome_race_pack.py
~~~

`prepare` calls the animation inheritance logic and creates merged mechanical geometry/materials.
Inspect `mechagnome_animations.py` for the parent/child reconstruction contract. `refresh` is the
later data refresh path; `install` is the guarded installation path. Its dedicated world migration is
`rev_20261001005000000.sql`. This five-byte family does not need another extra-appearance column.

## Highmountain

Base preparation:

~~~powershell
python tools/highmountain_race_pack.py prepare
python tools/highmountain_appearance.py
python tools/highmountain_integration.py prepare
python tools/highmountain_faces.py
python tools/highmountain_race_pack.py hard-textures
~~~

The first stage establishes codec/material selections and face variants. Reproduction must also
include the repairs that turned that stage into the accepted final port:

| Tool | Purpose / exposed operation |
| --- | --- |
| `highmountain_creator_repair.py` | Encoded sparse-table getters and compositor BLP corrections |
| `highmountain_head_repair.py` | Complete body/head geoset and baked-face selection |
| `highmountain_faces.py repair-pivots` | Pivot-relative face positions/normals |
| `highmountain_eye_repair.py` | Supported ordinary iris material path |
| `highmountain_complete_tracks.py prepare` | Full parent events/opacity/UV/camera and skeletal/attachment tracks |
| `highmountain_teardown_repair.py prepare` | Corrected executable/helper pair without unsafe field registration |

These repair scripts use explicit stage baselines and selected catalogs. Inspect their stage directories
and `install` operations before applying them. Do not replay an old intermediate executable over the
final helper. Native patch generation must use the current patcher and original verified executable.

Then build the native helper, generate the checked executable pair, and use:

~~~powershell
python tools/highmountain_integration.py build
python tools/highmountain_integration.py validate
python tools/test_highmountain_race_pack.py
python tools/test_highmountain_teardown_repair.py
~~~

Initial installation needs a matching worldserver build, its dedicated world/characters migrations
`rev_20261001006000000.sql`, and the first-port empty-target checks. Later teardown installation only
replaces the checked executable/DLL pair and preserves race assets/catalogs.

## Earthen

~~~powershell
python tools/earthen_race_pack.py acquire
python tools/earthen_race_pack.py portraits
python tools/earthen_race_pack.py prepare
python tools/earthen_race_pack.py stage
python tools/test_earthen_race_pack.py
cmd /c client-customization\build-native.bat C:\Users\Zach\.codex\tmp\earthen
~~~

Build worldserver for the new race/codec integration. Use `earthen_race_pack.py backup`, then its
`install` with only `rev_20261001100000000.sql`. The six-byte schema already exists.

`earthen_touchup.py` exposes `prepare`, `validate`, `install`, `refresh-native` and `feet`. It contains
the accepted persistence/preview/belt and boot-aware foot fixes. Do not stop at the original stage:
older README paragraphs still say live acceptance pending even though the later user retest passed.

## Haranir

~~~powershell
python tools/haranir_race_pack.py acquire
python tools/haranir_race_pack.py prepare
python tools/haranir_race_pack.py stage
python tools/test_haranir_race_pack.py
cmd /c client-customization\build-native.bat C:\Users\Zach\.codex\tmp\haranir
~~~

`prepare` includes source-derived ordinary options/materials. `portraits` and `header` are independently
exposed operations. The generated server header and catalog must remain consistent with the frozen codec.

Build the matching server, run `backup`, stop only worldserver, use `install`, then recreate that service.
The world and character migrations both use filename `rev_20261002120000000.sql` in their different
pending directories. The character migration widens `extraAppearance` to BIGINT UNSIGNED.

The final helper-only texture repair is:

~~~powershell
python tools/haranir_render_repair.py validate
python tools/haranir_render_repair.py install
~~~

That installer reads the existing stage/current files; build the updated helper into its expected
stage first. It preserves the executable/archives/catalogs. Use
`haranir_live_render.py <pid>` for read-only live texture-binding evidence. Do not deploy the earlier
failed file-loader or wrong-ABI candidate.

## Vulpera Retail rebase and v2 follow-up

Source recovery helpers live in the Vulpera work directory; their snapshots are included. Review their
pinned build/content-key assumptions before acquisition. The maintained pack exposes:

~~~powershell
python tools/vulpera_race_pack.py audit
python tools/vulpera_race_pack.py header
python tools/vulpera_race_pack.py prepare
python tools/vulpera_equipment.py
python tools/vulpera_race_pack.py stage
~~~

The helmet catalog and final equipment refresh are Python library functions, not additional packer
CLI actions. Their APIs are `equipment_catalog` and `refresh_equipment` in the source. The original
invocations and parser declarations are preserved in the tool index and source snapshots.

Prepare the matching helper and run `vulpera_race_pack.py validate`. The initial character mapping
comes from `vulpera_migration.py` and `rev_20261002200000000.sql`. The v2 repair uses
`vulpera_render_repair.py prepare` and `install` with `rev_20261002220000000.sql`.
Both are data-dependent migrations for existing saved characters; generate mappings for your own
population rather than copying this machine's GUID-specific SQL.

The blue-glow correction is retained in
[fix_eye_glow.py](sources/historical-diagnostics/vulpera/fix_eye_glow.py) and recorded in the acceptance
report. The native selection catalog's normal fallback must be 1700 while authored special effects remain.

## Naga, Tuskarr, Vrykul and Forgotten

~~~powershell
python tools/creature_race_pack.py discover
python tools/creature_race_pack.py acquire
python tools/creature_race_pack.py convert
python tools/creature_race_pack.py prepare
python tools/creature_race_pack.py reserve
python tools/creature_race_pack.py sql
python tools/creature_race_pack.py stage
~~~

`--race` may be repeated for source/preparation work. Final `stage` requires all four species as one
merged graph. `candidates` is source-candidate acquisition, not deployment.

The world migration is `rev_20261002230000000.sql`. A matching helper/server and recorded backup are
required for initial `install`. Latest repairs:

~~~powershell
python tools/thinhuman_equipment_repair.py prepare
python tools/thinhuman_equipment_repair.py check
python tools/tuskarr_equipment_repair.py prepare
python tools/tuskarr_equipment_repair.py check
~~~

Each exposes a separate `install`. ThinHuman additionally exposes `materials`. Language eligibility,
Horde Vrykul suppression and Forgotten naming have separate historical source/receipts; they preserve
asset names and supported server IDs.

## Darkfallen, stock additions, portraits and other content

- `darkfallen_race_pack.py` and `apply_darkfallen_archive_fixes.py` handle the Darkfallen pack and later
  root/locale Glue repair. Its existing [handoff](sources/EsteriaWoW/DARKFALLEN-REBOOT-HANDOFF.md) details
  the dedicated migration and server readbacks.
- `ascension_customization_pack.py --self-check` validates the additive planning logic. Normal invocation
  stages the supplied extracted donor. Installation helpers live in `historical-plans/ascension-customization`.
- `race_portrait_pack.py` stages art by default; `--apply` is explicit deployment and takes `--backup-dir`.
- `customization_layout.py` and `customization_buttons.py` expose `check`, `prepare` and `install`.
- `character_ui_pack.py` exposes `prepare` and `install` for creator/dropdown/select changes.
- `mount_pack_batch2.py --stage` stages mounts; `--deploy-client` is deployment.
- `dreadlord_override_pack.py build` builds its override stage, and `check` verifies it.

[ALL_TOOLS.md](reference/ALL_TOOLS.md) contains the exact source docstring and parser declarations for
every captured Python entry, including diagnostics and libraries without a CLI. Use that inventory
when a historical command differs from a maintained entry point.
