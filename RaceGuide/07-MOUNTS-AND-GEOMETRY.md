# Mounts, geosets, armor and additional model content

[Back to the guide](README.md)

## Custom mount integration

Two maintained packers cover the earlier supplied vehicle/mount material and later imports:

- [cars_mount_pack.py](sources/EsteriaWoW/tools/cars_mount_pack.py)
- [mount_pack_batch2.py](sources/EsteriaWoW/tools/mount_pack_batch2.py)

Historical import/render/deployment helpers are also in `historical-plans/car-mounts`,
`esteria-mount-import` and `mount-render-fix`. The original donor packages are external input directories;
the source catalog records their defaults. The packers preserve source/model naming and report IDs.

The first packer expects 111 discovered WotLK mount records with the requested variants. Flying Nimbus,
spell 201111, is an older special mount outside that 111-record discovery set. Content includes supplied
cars/karts and novelty mount packs, with GameBoy variants such as Zelda, Wario, Mario, Pokémon, Metroid,
Mega Man and Kirby, plus authored Pokémon-card texture variants.

Recorded allocation bases:

| Kind | Base |
| --- | ---: |
| Spell | 201000 |
| Item | 901000 |
| SpellIcon | 514646 |
| ItemDisplayInfo | 135000 |
| Creature entry | 3460608 |
| CreatureDisplayInfo | 94300 |
| CreatureModelData | 5000 |

These are allocation policy, not proof that every integer in a range is a live mount. Mount display
IDs can be above 65535 without violating the separate **player** display-ID band.

The mount dependency chain is:

~~~mermaid
flowchart LR
    I[Learning item] --> S[Mount spell]
    S --> C[Mounted aura display]
    C --> D[CreatureDisplayInfo]
    D --> M[CreatureModelData]
    M --> A[M2 SKIN animation textures]
    S --> B[SkillLineAbility and mount tab]
~~~

Generate the item/spell/template/DBC graph consistently. Validate spell icon, aura display,
creature/model rows and all physical files. A usable learning item is not proof that the mount tab can
list the learned spell.

## Pets/Mounts tab and Classless

Custom mount spells map through SkillLineAbility to skill line **777**. Native skill/ability DBC rows,
saved learned spells and Classless skill attribution are separate layers.

Classless originally treated certain mounts as class skills or rejected their lines. Its source tracks
mount skill lines separately, so mount admission/listing follows the intended collection path instead
of class-spell attribution. Account-mount sharing also needs saved character/account behavior.

A concrete observed follow-up involved learning item 901092/spell 201092: learning/persistence did not
prove Pets/Mounts visibility. The winning root/locale DBCs and Classless filtering needed alignment.

`PATCH-X.MPQ` contains the earlier pack and `Patch-W.MPQ` the later batch. Either can be shadowed by the
higher Z archives. The batch-two deployment mirrors its native DBC changes into winning root/locale Z
copies. Server DBC/SQL changes must agree with those effective files.

## Mount outputs and use

The packers generate archive stages, native DBC tables/continuations where appropriate, SQL, model
inventories and human test lists. Batch two writes `additems.txt` containing concrete GM learning-item
commands for each generated record. Use those output IDs rather than guessing.

~~~powershell
python tools/mount_pack_batch2.py --stage
~~~

This stages output. `--deploy-client` is the separate client mutation path. SQL/import/restart behavior
must be scoped to the generated migration. `cars_mount_pack.py` has explicit source/repo/baseline/
StormLib/mount-root/archive/output-SQL/report arguments; inspect its defaults before using another client.

Live validation includes learning, summoning, animation, mount-tab visibility, relog and account-sharing
on a second character. Do not remove saved spells or refresh bots just to rerun an art pack.

## Cosmetic geosets versus equipment geosets

A geoset is a selectable mesh group, not a texture or an item. Each race's body/collection SKIN declares
the meshes; legacy selectors, packed cosmetic choices and equipment visibility choose which render.

Keep these layers separate:

1. Source cosmetic choices and their prerequisite/related choices.
2. Complete unconditional body/head geometry.
3. Clothing overlays and stock equipment groups.
4. Custom native geometry/material rules.
5. Helmet/boot/robe overrides applied after cosmetic selection.

Remapping a whole group as “customization” can accidentally hide the base head. Treating boots as
cosmetic feet can show toes through footwear. Correct ordering restores cosmetics when equipment is
removed rather than baking equipment state into saved appearance.

## Concrete geoset work by family

| Family | Implemented geometry work |
| --- | --- |
| Skyborne | Merge feather/accessory collections; hairstyle-related feather meshes and color groups 4000–4799 |
| Mechagnome | Mechanical arm/leg/body collections; remap away from stock equipment selectors |
| Highmountain | Body/head repair, all nine pivot-correct BONE variants, compact palettes and wide SKIN recovery |
| Earthen | Shoulder/torso/arm/leg/hand/belt collections; boots select rounded feet and barefoot toes |
| Haranir | Reduced collection LOD with preserved styles, fur/quills/jewelry/clothing choices; feet issue deferred |
| Vulpera | Preserve primary authored geosets; head 3202, tail/feet compositor regions and per-helmet hides |
| Tuskarr | Rounded foot geometry and robe fallback keeping calf mesh visible |
| Forgotten | Boot/leg/cloak remaps, helmet attachment/fitting and alpha/reflection material repairs |

The creator can cover some choices with class preview clothing. Verify body geometry naked/barefoot and
with actual equipment before concluding an option is a no-op.

## Helmets, prefixes and attachments

The equipment prefix resolves race/gender component names. Vulpera uses `Vu` and Forgotten `Th`.
Changing a prefix to another race may locate a file while breaking fit, identity or authored hides.

The Vulpera equipment stage converts 550 variants for 275 of 277 installed families and aliases Retail
`_vu_m/f` to Wrath `_VuM/F` paths. The two named missing families and undocumented visibility condition 32
are kept in the coverage report. Unconditional HelmetGeosetData hides become equipment-dependent
selection records; they are applied after cosmetics and undone when the helmet is removed.

Older Vulpera helmet calibration scripts remain in `historical-plans/races-9-port`. They investigated
attachment 11, donor geometry, prefixes and bounding boxes. They are superseded by the Retail rebase for
normal reproduction. Identical donor helmet vertices do not fix a wrong anchor or bone transform.

Kul Tiran has focused head-attachment, helmet-display and helmet-pack tools. Their contract tests
preserve unrelated display/model rows and attachment geometry. The obsolete experimental Vulpera
head-diagnostic DLL is historical evidence, not a default component to install; its unsafe structure
argument was a separate crash source.

Forgotten repairs use `thinhuman_equipment_repair.py`. A later material correction restored alpha-mask
passes and shader lookup indices for 131 helmet families. Correct textures alone do not repair omitted
passes or a sampler that addresses the wrong UV source.

## NPC models are not player models

An NPC normally resolves `creature_template` model IDs through CreatureDisplayInfo/CreatureModelData.
A player uses its race/gender graph and appearance/equipment composition. HD player replacement does
not automatically replace every NPC using that species.

The included tools `repair_hd_npcs_highelf_darkfallen.py` and HD model audit/migration helpers trace
those display/model/asset paths. Verify concrete affected NPC entries rather than inferring from a
shared visible species name.

## Dreadlord override

The later donor port is a separate NPC override, not a playable race allocation. Its source is
[dreadlord_override_pack.py](sources/EsteriaWoW/tools/dreadlord_override_pack.py), with reports under
`G:\RetroPorterWork\dreadlord` and archive `Data\Patch-Dr.MPQ`.

The first export omitted Wrath's UV lookup table. The corrected pack validates all 28 draw batches and
preserves source/backup evidence. The chat reports deployment and requests fresh visual confirmation.

Verified live NPC test entries were 8716 (normal) and 9516 (green Lord Banehollow). For a deliberate GM
smoke test, the recorded commands are:

~~~text
.npc add temp 8716
.npc add temp 9516
~~~

The reported display IDs for temporary player preview were 130 and 8609. These are test references,
not permission for the documentation utility to spawn or morph anything.

## HD baselines and rollback history

Earlier WoD/Ascension HD replacements, corrective restores and collision audits are retained in the
source index. A rollback restored the accepted narrow player-display contract and selected DBCs.
Later accepted modern ports depend on that actual baseline and their own asset namespaces.

Do not install an old global HD stage or wholesale donor archive over the current custom graph.
Read the historical reports to understand the root cause, then use today's effective DBC/assets and
focused additive repair.
