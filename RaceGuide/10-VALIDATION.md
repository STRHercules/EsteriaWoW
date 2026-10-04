# Developer verification checklist

[Back to the guide](README.md)

## Source and allocation

- [ ] Pin source version/product/build/encoding identity.
- [ ] Separate Retail RaceID from target RaceID.
- [ ] Check client DBC, server DBC/SQL, registry, UI and saved-character ownership.
- [ ] Reserve model/display/appearance/barber/portrait IDs; keep player displays below 65536.
- [ ] Verify complete reachable FileDataID closure, including hard TXID and parent skeleton data.
- [ ] Preserve immutable raw sources and record recovery/conversion losses.

## Model and appearance data

- [ ] Validate M2/SKIN arrays, lookup tables, native palettes and vertex limits.
- [ ] Validate every external or embedded animation span and alias target.
- [ ] Check skeletal/attachment/opacity/UV/camera/event tracks, especially talk/dance/sheath.
- [ ] Preserve all scoped collection choices and their dependencies.
- [ ] Verify BONE pivots/normals and total static geometry budget.
- [ ] Match body/face/accessory UV layouts and supported material shader paths.
- [ ] Keep ordinary iris distinct from optional glow.
- [ ] Verify BLP headers/palette/alpha/mips and compressed bank bounds.
- [ ] Freeze codecs and migrate reordered saved choices by stable source IDs.
- [ ] Validate class/gender restrictions and randomization.

## Client/server integration

- [ ] Rebase DBC string pools and preserve packed record layouts/unrelated rows.
- [ ] Sort CharSections by race, sex, section type, variation and color.
- [ ] Resolve effective root/locale files, not a convenient loose backup.
- [ ] Match display/model paths and actual payload files.
- [ ] Confirm starts/outfits/actions/skills/spells/languages/stat compatibility.
- [ ] Verify dedicated migration receipt and read back affected data.
- [ ] Confirm extraAppearance type/high bits and matched create/enum/update/save/load contracts.
- [ ] Preserve donor-mask aliases without changing actual numeric/faction identity.
- [ ] Check bots and legacy/custom race regressions.
- [ ] Verify exact creator metadata, faction/background/portrait mappings and ECS real-index binding.

## Native ABI and lifetime

- [ ] Fingerprint the original executable and every replaced instruction.
- [ ] Preserve foundation, character-limit and ordinary-race fallback paths.
- [ ] Confirm x86 bool predicates use AL.
- [ ] Confirm SMemAlloc calling convention and client-owned buffer/destructor pairing.
- [ ] Do not register unsupported padding observers.
- [ ] Reject non-units/items before unit-field reads.
- [ ] Clear component-owned references and address-keyed appearance cache on free.
- [ ] Exercise mixed HXE1/HXE2 roster tails, HRC1 creation and high-word persistence.
- [ ] Match DLL/catalog/model/header versions.

## Focused existing checks

Run only the suites relevant to the changed contract and any concrete shared regression:

~~~powershell
python -m unittest tools.test_retroported_race_pack tools.test_retroported_race_contract
python -m unittest tools.test_native_appearance tools.test_highmountain_teardown_repair
python -m unittest tools.test_mechagnome_race_pack tools.test_earthen_race_pack tools.test_haranir_race_pack
python -m unittest tools.test_vulpera_race_pack tools.test_vulpera_models tools.test_vulpera_creator
python -m unittest tools.test_character_ui tools.test_two_names_contract tools.test_character_select_contract
python -m unittest tools.test_creature_race_pack tools.test_creature_animations
~~~

Some suites read installed client/assets or specific staged baselines. Use their source prerequisites;
a missing baseline is not a passing test. The native build script runs the three matching native
harnesses. Historical C++/SQL lint output includes repository-wide failures and missing origin/master
conditions; do not claim those gates are green just because a focused port check passed.

## Backed-up installation

- [ ] Stage from current archives and verify source/stage hashes.
- [ ] Keep compressed classic MPQs inside tested offset limits.
- [ ] Serialize StormLib writes and verify replaced entries.
- [ ] Record original helper/executable/catalog/DBC/character rows and rollback SQL/image.
- [ ] Close client/Eclipse and stop only worldserver when required.
- [ ] Import only the reviewed named migration(s).
- [ ] Recreate only ac-worldserver with no dependency/volume replacement.
- [ ] Read back installed hashes, schema/migrations and readiness/errors.

## Live acceptance for each authored gender and faction

- [ ] Fresh launch: login screen, options, account persistence and navigation.
- [ ] Creator: correct names/factions/tooltips/portraits, class/gender restrictions and previews.
- [ ] Cycle every scoped choice; verify independent labels and dependencies.
- [ ] Randomize names/last name/appearance; hover, cancel and commit dropdown choices.
- [ ] Switch expanded→stock→expanded; restore labels/materials and wheel/zoom behavior.
- [ ] Create a new character, including first-login cinematic and normal chat.
- [ ] Roster: correct race/faction/portrait/model and saved appearance.
- [ ] Game: same appearance, nearby-player view and full-resolution materials.
- [ ] Movement/jump/sit/dance/talk/cast/combat and drawn/sheath equipment.
- [ ] Armor: naked, boots on/off, robe, gloves, shoulder, cloak, shield and representative helmets.
- [ ] Barber: legacy behavior remains valid; record its scope separately.
- [ ] Logout/relog repeatedly, ordinary-race logout and full client exit.
- [ ] ECS: search/reorder/notes/scroll/key navigation; enter/delete target actual character.
- [ ] Mounts: learn, mount tab, summon, relog and second-character sharing where implemented.
- [ ] Capture new screenshots/crash reports and the exact installed hashes.

Do not mark a known deferred item accepted. Use [the current matrix](09-EVIDENCE-AND-GAPS.md) as the
starting point and add the actual target-machine retest evidence.

## Verify this documentation package

~~~powershell
rtk proxy python -X utf8 RaceGuide/tools/capture_snapshot.py --verify
rtk proxy python -X utf8 RaceGuide/tools/verify_guide.py
~~~

These check snapshot integrity, extracted-source hashes and authored guide links/structure. They do
not run gameplay tests. A developer on another machine can verify the handoff without fetching Retail
or starting the server.
