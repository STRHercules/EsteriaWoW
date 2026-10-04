# Vulpera/Pandaren world-entry crash: archive priority root cause

Date: 2026-09-11 (follow-up to the 2026-09-11 race session)

## Symptom

Vulpera (race 20) and Pandaren (race 18) render in character create and in the
character list, but entering the world raises `ERROR #134 (0x85100086) Fatal
Condition` in `Wow.exe` with an identical stack on every attempt.

## Root cause

The client resolves two different sources for the character model:

* glue screens (create/list) use `ChrRaces.dbc` (race -> `MaleDisplayId`), which
  is only shipped by `Patch-C.MPQ`;
* the world uses the display id the server sends in `UNIT_FIELD_DISPLAYID`,
  which `Player::InitDisplayIds()` takes from the world DB `chrraces_dbc`
  (`ObjectMgr.cpp:4430`).

Both then resolve through `CreatureDisplayInfo.dbc` / `CreatureModelData.dbc`.
**`PATCH-X.MPQ` loads after `Patch-C.MPQ` and ships its own copies of both
tables**, so every edit made to Patch-C's copies was invisible to the client.

Evidence (WXL startup log, `3.3.5a - Dev/Logs/wxl-core.log`):

```
wxl-extended-dbc: merged 'DBFilesClient\CreatureDisplayInfo.dbc' + 1 continuation(s)
    -> 29187 rows (3162 appended-ish, 0 replaced/overwritten, 0 skipped)
wxl-extended-dbc: merged 'DBFilesClient\CreatureModelData.dbc' + 1 continuation(s)
    -> 4655 rows (3162 appended-ish, ...)
```

PATCH-X has 26025 + 3162 = 29187 display rows and 1493 + 3162 = 4655 model rows;
Patch-C has 25913 / 1377. The client therefore read PATCH-X's tables.

Consequence: display ids `60004-60007` (the per-race player displays invented for
this feature and only added to Patch-C) do not exist client-side, so the world
model lookup returned nothing and the client raised the fatal condition. Glue
worked because Patch-C's `ChrRaces` pointed at `141254/141687`, which PATCH-X
does provide.

## Second cause: the world path truncates the player display id to 16 bits

After the first fix the characters entered the world but rendered as the wrong
races: Pandaren -> Night Elf, Vulpera -> Tauren. Both are the 16-bit truncation
of the donor ids:

```
141254 & 0xFFFF = 10182 -> CreatureDisplayInfo 10182 -> model 59  -> Tauren male
141687 & 0xFFFF = 10615 -> CreatureDisplayInfo 10615 -> model 56  -> Night Elf
```

The glue screens accept the full 32-bit id, the in-world player path does not.
This is the same 16-bit constraint the earlier session found when it introduced
`60004-60007`; those rows were only written to Patch-C, which PATCH-X shadows,
so the client never saw them and raised the fatal condition instead.

## Fix

* `PATCH-X.MPQ` `CreatureDisplayInfo.dbc` now carries 16-bit clones of the donor
  rows: 60004/60005 -> models 112929/112930 (Pandaren), 60006/60007 ->
  112885/112886 (Vulpera). Entries are inserted in id order (26029 rows).
  Backup: `3.3.5a - Dev/Backups/patch-x-before-display-20260911-150004/`.
* World DB `chrraces_dbc`: race 18 -> 60004/60005, race 20 -> 60006/60007, the
  same ids the client now resolves. The client's Patch-C `ChrRaces` keeps the
  32-bit donor ids for the glue path, which renders correctly.
* Module SQL kept in sync: `dbc/chrraces_dbc.sql`, `u_custom_server_2026_09_02_race_sync.sql`,
  `u_custom_server_2026_08_30_race_models.sql`, `pending_db_world/rev_1787850000002_race_models.sql`.
* `CreatureSoundData.dbc` (Patch-C, not shadowed by PATCH-X) now carries the four
  sound kits the models reference: 6278/6279 (Vulpera) and 4012/4080 (Pandaren),
  copied from stock Goblin and Tauren rows whose `SoundEntries` all exist locally.
  Every other playable race in this client resolves its `CreatureModelData.SoundID`;
  these four were the only gaps.

## Verification

`verify_player_display_chain.py` mirrors the real load order (...Patch-C ->
PATCH-X), resolves race -> display -> model -> asset + sound kit for the glue
ids and for the 16-bit world ids, and rejects any world id >= 65536:
`chain failures: 0`.

## Open risk

The models now resolve correctly to 16-bit display ids, so any remaining problem
is model content: these two M2s declare 320/326 sequences and 287/289 key bones
versus 83-224 sequences and 27-80 key bones for the custom models that already
render in-world.

## Follow-up: speculative model edits reverted (2026-09-11)

The crash hunt had also cleared the M2 `globalFlags` combiner bit (`0x8` ->
`0x0`) and forced `numSkinProfiles` from 1 to 4 with duplicated `.skin` files.
Both were guesses at the crash and both were made before the truncation cause
was known. Bit `0x8` is "use texture combiner combos", which the Vulpera model
needs for its multi-texture layers (eye glow, armour overlay on the body), so
clearing it matches the two remaining defects: pure black Vulpera eyes and the
forearm sleeve/bracer area falling back to body skin.

All four `.m2` files are therefore restored to the donor bytes
(`restore_donor_models.py`); an asset hash sweep confirms every other Vulpera
and Pandaren file (2006 files, `.blp`/`.skin`/`.anim` included) is already
byte-identical to `patch-CHA.mpq`. Backup of the pre-restore archive:
`3.3.5a - Dev/Backups/patch-c-before-donor-models-<stamp>/Patch-C.MPQ`.

## Open: arm armour ("bracers/gloves") on a bare-armed Vulpera

**Resolved diagnosis (UV probe, same day):** the bands are painted into the
race's own body skin textures, not armour. With the 8x8 UV probe installed, the
arms render identically with the shirt on and off, and replacing the skin
texture changed exactly those areas - so no component-texture or client issue is
involved. The Atlas art carries a dark fur band on the forearm plus dark paws,
and our copy of every one of those BLPs is byte-identical to `patch-CHA.mpq`.
All 24 skin variants carry the band, so changing skin tone does not avoid it.

Automated repaints were attempted and rejected (previews kept beside the probe
images): region colour lift (visible rectangle), smooth global remap (flattened
fur), arm masks from bone records (this model's bone array does not follow the
WotLK layout), arm masks from vertex positions (over-captures ~3/4 of the
atlas), and mirroring the upper-arm fur over the forearm columns (visible
mirrored duplicate). None were installed; Patch-C stayed on the donor bytes.

Remaining route is a hand repaint of the forearm strip. Tooling is in place:
`vulpera_skin_roundtrip.py export|import` converts all 48 BLPs to PNGs (and the
painted PNGs back to palettised BLPs inside a staged Patch-C), with the PNGs in
`vulpera-skins-png/`.

After the restore the eyes are correct, but the Vulpera forearms show the leather
shirt's sleeve texture. Evidence gathered so far:

* Foxbow equips only shirt 148 (`ItemDisplayInfo` 9976), pants 147 (9975) and
  boots 129 (9977); the bracer and glove slots are empty, so nothing should be
  on the arms.
* Display 9976 carries component textures `Leather_A_02_Sleeve_AU` (index 0 =
  upper arm), `_Chest_TU` and `_Chest_TL` only - no lower-arm or hand texture.
* The client builds these overlays in its `CCharacterComponent` subsystem
  (`Item\TextureComponents\%s\%s_%s.blp`, `componentTextureLevel` /
  `componentThread` CVars, `M2.CharValidateComponentData`, `M2.CharAllocComponent`,
  `M2.CharCreateBaseTexture`, `M2.CharAddItemBySlot` in the WarcraftXL symbol
  table). The region tables live in `Wow.exe`: no
  `CharComponentTextureLayouts.dbc` / `CharComponentTextureSections.dbc` exists
  in this client, in the base archives, or in the donor extraction.

So the overlay is placed using the client's per-race layout and races 18/20 are
not in that table - the sleeve lands over the forearms instead of the upper arm.
Not fixable from DBC or asset data alone unless the models/textures are
re-authored to the layout the client falls back to.

### Refined (same day): it is Vulpera-only, not "all custom races"

The user confirmed Pandaren (race 18) arms are correct and only the Vulpera is
affected. Both characters wear shirts whose `ItemDisplayInfo` carries the same
upper-arm component texture (`Squire's Shirt` 3265 -> `Cloth_A_01Blue_Sleeve_AU`,
`Rugged Trapper's Shirt` 9976 -> `Leather_A_02_Sleeve_AU`), and bracer/glove
slots are empty on both, so the mechanism is identical and the difference is the
model:

* Human and Broken `.skin` batches never use `textureCount = 2`; Pandaren has one
  such batch on the torso (geoset 0) - the correct armour-overlay behaviour.
* Vulpera has six two-layer batches, but they sit on head/eye geosets
  (1, 2, 3, 4 - centres near z=1.19) and are what the combiner flag fix restored.
* Vulpera's `textureCoordCombos` is `(0, 1, 65535, 1)` and three batches use
  entry 2 (the `0xFFFF` sentinel), again head/eye work, not arms.

So the arms are painted by the client's component overlay against the Vulpera's
own UV layout, which puts the forearms inside the region the client reserves for
the upper arm. Fixing that is art/model work (re-UV or re-texture the Vulpera
arms) or a client-side change (WarcraftXL adding race 20 to its component region
table); no DBC or MPQ data edit can move those rectangles.

### MPQ-only repair path (no client change)

The rectangles stay in `Wow.exe`, but the other half of the mapping - the model's
UVs - is ours (`character\vulpera\*\*.m2` plus the matching `.blp` texels in
Patch-C). Because the sleeve is pasted *over* whatever the rect covers, moving
the Vulpera's upper-arm UV island inside the sleeve rect and moving the forearm
island to the area the upper arm samples today (fur on fur) removes the false
bracer without touching the client:

1. Probe run: ship a labelled UV-grid body texture, screenshot, and read which
   texture cells the forearm/upper arm sample.
2. Cluster the arm vertices into UV islands (vertex UVs + triangle indices),
   swap the two islands per gender, rebuild the `.m2`, and re-check in game.

Measured starting points: Vulpera male key bones ArmL/R = 40/42 (forearm, 1012
verts), ShoulderL/R = 31/33 (upper arm, 1394 verts); female ArmL/R = 41/44
(1216) / ShoulderL/R = 31/34 (1732). Both arm vertex sets currently span most of
the atlas, so a proper island split is required before any swap.

Cheap alternative that needs no model work: clear `TextureName[0]`
(`Leather_A_02_Sleeve_AU`) on `ItemDisplayInfo` 9976 in PATCH-X. That removes the
false bracer on every race, but also removes that shirt's sleeve everywhere and
does not generalise to other chest items.
