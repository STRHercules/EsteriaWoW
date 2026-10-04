# Character Creator Race Art - Extraction Notes

Extracted 2026-09-11 from the live `3.3.5a - Dev` client. Nothing in the client or
archives was modified; these are read-only copies plus decoded PNGs.

## Folders

- `blp/` - the exact BLP files the client currently loads, byte-for-byte.
- `png/` - BLP mip 0 decoded to PNG. Edit these.
- `source/` - current winning `Interface\GlueXML\CharacterCreate.lua` and
  `CharacterCreate.xml` from `Data\Patch-C.MPQ`, for line references.
- `SHA256SUMS.txt` - baseline hashes for every extracted file.

## Files

| PNG to edit | Original BLP | Source archive | Size | Format | Role |
|---|---|---|---|---|---|
| `png/UI-CharacterCreate-Races.png` | `blp/UI-CharacterCreate-Races.blp` | `Data\PATCH-A.MPQ` | 512x256 | BLP2/DXT5 | Race button icons for every race. Lua slices it with `RACE_ICON_TCOORDS`. |
| `png/UI-CharacterCreate-RacesRound.png` | `blp/UI-CharacterCreate-RacesRound.blp` | `Data\PATCH-A.MPQ` | 512x256 | BLP2/DXT5 | Big race portrait in the info pane (`CharacterCreateRaceIcon`). |
| `png/IconBorder_F.png` | `blp/IconBorder_F.blp` | `Data\PATCH-A.MPQ` | 256x256 | BLP2/DXT5 | Circle ring drawn over every race button (faction-tinted) plus its hover glow. |
| `png/IconBorderRace_H.png` | `blp/IconBorderRace_H.blp` | `Data\PATCH-A.MPQ` | 256x256 | BLP2/DXT5 | Gold selection ring shown on the checked race button. |
| `png/IconBorder_F1.png` | `blp/IconBorder_F1.blp` | `Data\PATCH-A.MPQ` | 256x256 | BLP2/raw BGRA | Ring used by class and gender buttons; only needed if those circles should go too. |
| `png/IconBorderRace_B.png` | `blp/IconBorderRace_B.blp` | `Data\PATCH-A.MPQ` | 256x256 | BLP2/DXT5 | Not referenced by the current creator; extracted for completeness. |
| `png/UI-CharacterCreate-InfoBox.png` | `blp/UI-CharacterCreate-InfoBox.blp` | `Data\enUS\patch-enUS-2.MPQ` | 512x512 | BLP2/DXT5 | Info pane art; the circle around the big race portrait is baked into its top-left. |
| `png/UI-CharacterCreate-VulperaMale.png`, `...Female.png` | matching `.blp` | `Data\Patch-C.MPQ` | 64x64 | BLP2/raw BGRA | Existing per-race override examples; same format to copy for other races. |
| `png/UI-CharacterCreate-PandarenMale.png`, `...Female.png` | matching `.blp` | `Data\Patch-C.MPQ` | 64x64 | BLP2/raw BGRA | Same. |

## Atlas layout (Races / RacesRound, 512x256)

64x64 cells, 8 columns x 4 rows. Pixel rectangles come straight from
`RACE_ICON_TCOORDS` in `source/CharacterCreate.lua`:

| Key | PNG rect (x1-x2, y1-y2) |
|---|---|
| `HUMAN_MALE` | 0-64, 0-64 |
| `DWARF_MALE` | 64-128, 0-64 |
| `GNOME_MALE` | 128-192, 0-64 |
| `NIGHTELF_MALE` | 192-256, 0-64 |
| `DRAENEI_MALE` | 256-320, 0-64 |
| `WORGEN_MALE` | 320-384, 0-64 |
| `HIGHELF_MALE` | 384-448, 0-64 |
| `TAUREN_MALE` | 0-64, 64-128 |
| `SCOURGE_MALE` | 64-128, 64-128 |
| `TROLL_MALE` | 128-192, 64-128 |
| `ORC_MALE` | 192-256, 64-128 |
| `BLOODELF_MALE` | 256-320, 64-128 |
| `GOBLIN_MALE` | 320-384, 64-128 |
| `MAGHAR_MALE` | 384-448, 64-128 |
| `SETHRAK_MALE` | 448-512, 64-128 |
| `HUMAN_FEMALE` | 0-64, 128-192 |
| `DWARF_FEMALE` | 64-128, 128-192 |
| `GNOME_FEMALE` | 128-192, 128-192 |
| `NIGHTELF_FEMALE` | 192-256, 128-192 |
| `DRAENEI_FEMALE` | 256-320, 128-192 |
| `WORGEN_FEMALE` | 320-384, 128-192 |
| `TAUREN_FEMALE` | 0-64, 192-256 |
| `SCOURGE_FEMALE` | 64-128, 192-256 |
| `TROLL_FEMALE` | 128-192, 192-256 |
| `ORC_FEMALE` | 192-256, 192-256 |
| `BLOODELF_FEMALE` | 256-320, 192-256 |
| `GOBLIN_FEMALE` | 320-384, 192-256 |
| `MAGHAR_FEMALE` | 384-448, 192-256 |
| `SETHRAK_FEMALE` | 448-512, 192-256 |
| `HIGHELF_FEMALE` | 384-448, 128-192 |
| `BROKEN_MALE` | 384-448, 128-160 |
| `BROKEN_FEMALE` | 384-448, 160-192 |

Two entries are irregular: `HIGHELF_FEMALE` claims the whole 384-448, 128-192
cell, and `BROKEN_MALE` / `BROKEN_FEMALE` split that same cell into two 32-pixel
halves. If that overlap is not wanted, leave the atlas alone and use the
per-race override route for those keys.

## Two ways to replace the art

1. Shared atlas (fewest files): repaint the 512x256 PNGs and replace both
   `UI-CharacterCreate-Races.blp` and `UI-CharacterCreate-RacesRound.blp`.
   Keep the cell layout above.
2. Per-race override (recommended): one 64x64 image per race/gender, saved as
   `UI-CharacterCreate-<Race><Gender>.blp` and added to `RACE_ICON_TEXTURES` in
   `CharacterCreate.lua` (lines 64-69 hold the existing Pandaren/Vulpera
   entries). The override covers both the button icon and the big info-pane
   portrait and ignores atlas coordinates.

## Removing the circles

- `IconBorder_F` and `IconBorderRace_H` are the race button rings. Either delete
  the three texture blocks in `CharacterCreateEnumerateRaces()`
  (`source/CharacterCreate.lua` lines 964-994) or make those two BLPs fully
  transparent and repack them.
- `IconBorder_F1` is the same ring for class and gender buttons; make it
  transparent only if those circles should go too.
- The info-pane circle is part of the `UI-CharacterCreate-InfoBox.png` top-left
  artwork, not a separate element. Erase it there (or cover it) and repack the
  BLP.
- Keep alpha: the rings need transparent centers and edges.

## Giving files back for repack

Drop edited PNGs (preferred) or edited BLPs into this folder and say so. I will:

1. Re-encode PNGs to BLP2 with the original dimensions and a mip chain
   (raw BGRA BLP2 is accepted by the client and already used by the
   Vulpera/Pandaren icons).
2. Back up `Data\Patch-C.MPQ` first, then replace/add the entries in the copy.
3. Verify the archive entries and leave the swap for a live client check.

If you edit BLPs directly, BLP Lab, BLPConverter, or the BLP plugins for
Paint.NET / Photoshop can open and save BLP2. Editing the PNGs and handing them
back avoids format mistakes.

## Repack log

- 2026-09-11 17:50 - user-edited `png/UI-CharacterCreate-RacesRound.png`
  (Pandaren and Broken moved to column 8) encoded to BLP2 raw BGRA 512x256 with
  mips (700,224 bytes each) and packed as both `UI-CharacterCreate-Races.blp` and
  `UI-CharacterCreate-RacesRound.blp` in `Data\Patch-C.MPQ`. Entry count went
  5110 -> 5112.
  Lua changes in the same archive: added `PANDAREN_MALE` / `PANDAREN_FEMALE`
  coordinates, moved `BROKEN_MALE` / `BROKEN_FEMALE` to column 8, dropped the
  Pandaren `RACE_ICON_TEXTURES` overrides (Vulpera keeps its own file), and
  removed the race-button ring creation blocks (`IconBorder_F` /
  `IconBorderRace_H`); class and gender rings are untouched.
  Backup: `3.3.5a - Dev\Backups\patch-c-before-charcreate-art-20260911-175043\Patch-C.MPQ`.
  Live archive SHA-256 prefix: `e570c169fe009c53`. Not yet smoke-tested in the
  client.

- 2026-09-11 17:55 - follow-up after the lag / missing-effects report:
  re-encoded both atlas BLPs as BLP2/DXT5 (same format and 175,972-byte size as
  the stock files, mean abs error ~0.5 vs the 512x256 PNG) instead of raw BGRA,
  and restored the race-button hover ring (`IconBorder_F` highlight) and selected
  ring (`IconBorderRace_H` checked). The always-on faction ring
  (`staticTexture`) stays removed. Backup:
  `3.3.5a - Dev\Backups\patch-c-before-charcreate-art-fix-20260911-175529\Patch-C.MPQ`.

- 2026-09-11 18:24 - switched to independent per-race icons. 30 PNGs from
  `png/New folder/` (15 races x 2 genders) encoded to BLP2 raw BGRA 64x64 with a
  full mip chain (23,016 bytes each, pixel-identical to source) and packed under
  `Interface\Glues\CharacterCreate\UI-CharacterCreate-<Race><Gender>.blp`.
  `RACE_ICON_TEXTURES` in `CharacterCreate.lua` now holds 30 entries; `Undead`
  PNGs map to the client key `SCOURGE` and `Scourge*.blp` names. Hover
  (`IconBorder_F`) and selected (`IconBorderRace_H`) ring effects are unchanged.
  High Elf has no PNG in the set and still uses the atlas; Sethrak stays hidden;
  Mag'har is not present in the live ChrRaces.dbc. Patch-C entries: 5112 ->
  5138. Backup:
  `3.3.5a - Dev\Backups\patch-c-before-independent-race-icons-20260911-182427\Patch-C.MPQ`.

- 2026-09-11 18:35 - fixed the "every button shows the whole atlas" report. The
  18:24 per-race BLPs were raw BGRA and did not bind in the client Glue renderer,
  so each button kept its XML default texture (the race atlas) while the override
  branch had already set UVs to 0..1 - hence a whole sheet per button. All 32
  icons (High Elf added) were re-encoded as BLP2/DXT5 64x64 with mips (6,660
  bytes each, same format as the stock atlases) and packed into Patch-C. The same
  32 BLPs were also written as loose files to the WXL overlay folder
  `Data\patch-z.mpq\Interface\Glues\CharacterCreate\` as a highest-priority copy.
  `UI-CharacterCreate-Races.blp` and `UI-CharacterCreate-RacesRound.blp` in
  Patch-C were reverted to the pristine stock BLPs (RacesRound is ditched);
  hover (`IconBorder_F`) and selected (`IconBorderRace_H`) effects stay enabled.
  Patch-C entries: 5138 -> 5140. Backup:
  `3.3.5a - Dev\Backups\patch-c-before-dxt5-race-icons-20260911-183510\Patch-C.MPQ`.

- 2026-09-11 18:41 - actual root cause of the "whole atlas per button" bug: the
  generated `RACE_ICON_TEXTURES` rows had single backslashes
  (`Interface\Glues\...`) because `re.sub` consumed the doubled backslashes in
  the replacement string. The client therefore resolved an invalid texture path,
  kept the atlas bound by the XML, and the override branch's 0..1 UVs showed the
  whole sheet in every button. Fixed by inserting the table via a replacement
  function and verifying 6 backslashes per path. All 32 paths now resolve to
  archive entries. Backup:
  `3.3.5a - Dev\Backups\patch-c-before-race-icon-path-fix-20260911-184148\Patch-C.MPQ`.

- 2026-09-11 18:48 - re-encoded the user-edited High Elf male/female PNGs to
  BLP2/DXT5 64x64 (6,660 bytes each) and replaced both entries in `Patch-C.MPQ`.
  The redundant loose overlay `Data\patch-z.mpq\Interface\Glues\CharacterCreate`
  was moved out of the client to
  `3.3.5a - Dev\Backups\patch-z-interface-charcreate-20260911-184817` because the
  WXL wildcard layer scans loose files and is the prime suspect for the new
  cursor flicker / char-create hitching. Backup:
  `3.3.5a - Dev\Backups\patch-c-before-highelf-icon-fix-20260911-184817\Patch-C.MPQ`.

- 2026-09-11 18:51 - user re-edited the High Elf pair again; both re-encoded to
  BLP2/DXT5 64x64 (6,660 bytes each, confirmed different from the previous
  bytes) and replaced in `Patch-C.MPQ`. Backup:
  `3.3.5a - Dev\Backups\patch-c-before-highelf-icon-rework-20260911-185145\Patch-C.MPQ`.

- 2026-09-11 18:58 - icon fidelity fix: the DXT5 encode was visibly lossy at
  64x64 (colour/detail drift vs source). All 32 per-race icons were re-encoded as
  lossless BLP2 raw BGRA 64x64 with mip chains (23,016 bytes each) and replaced
  in `Patch-C.MPQ`; each archive entry decodes pixel-identical to its source PNG.
  Backup:
  `3.3.5a - Dev\Backups\patch-c-before-lossless-race-icons-20260911-185815\Patch-C.MPQ`.
