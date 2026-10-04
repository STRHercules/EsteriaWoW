# Vulpera cuff repaint - working set

The pale band on the forearms and shins that reads as a rolled-up sleeve is
**painted into the body skin texture**. It is not geometry and it is not an
item component. The model's forearm and shin UVs sample a hard step from dark
brown to pale cream in the atlas:

    u=0.75 v=0.38   (115,  76,  55)   dark brown
    u=0.60 v=0.40   (188, 163, 125)   pale cream

Removing the cuff means repainting that part of the atlas.

## What is in this folder

    skins-png/                    48 editable PNGs (24 male + 24 female skin
                                  variants) + manifest.json, ready to paint
    overlay_male.png              full atlas at 2x with a pixel grid and the
    overlay_female.png            model's own UV rectangles drawn on it
    zoom_arm_male_x4.png          4x crops of each region
    zoom_leg_male_x4.png
    zoom_arm_female_x4.png
    zoom_leg_female_x4.png
    atlas_heightmap_male.png      false-colour map: blue = low on the body
                                  (feet), green = hips, red = head. Use this to
                                  tell arm islands from leg islands
    forearm_band_skin_x4.png      the specific band the forearm samples

## Workflow A - paint and import (no client restart needed until the end)

1. Open the PNGs in `skins-png/` in an image editor. Each is 512x512.
2. Paint the cuff strip so the cream and the surrounding brown blend. Keep the
   alpha at full and stay inside the atlas island - painting across island
   boundaries bleeds onto other body parts.
3. Save over the same PNGs (same size, same filenames).
4. Import back into a staged archive:

       cd .agents\plans\vulpera-pandaren-playable-races
       python vulpera_skin_roundtrip.py import ^
         --patch-c "R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ" ^
         --in-dir cuff-repaint\skins-png ^
         --out cuff-repaint\staged

   That produces `cuff-repaint/staged/Patch-C-vulpera-pandaren.MPQ`. It does not
   touch your live client.
5. Close the client, back up the live archive, then copy the staged file over
   `3.3.5a - Dev\Data\Patch-C.MPQ`.

Note: the import quantises back to a 256-colour palette, so use smooth
transitions rather than hard gradients.

## Workflow B - probe first, then paint (recommended if you are unsure where)

If you cannot tell which part of the atlas is the forearm, run the UV probe.
It replaces every Vulpera skin texture with an 8x8 hue/brightness grid so you
can read off the answer from a screenshot.

    cd .agents\plans\vulpera-pandaren-playable-races
    python make_vulpera_uv_probe.py ^
      --patch-c "R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ" ^
      --out cuff-repaint\probe ^
      --reference cuff-repaint\probe\probe_reference.png

Install the staged archive from `cuff-repaint/probe/staged`, log in, and look at
the forearm. Each cell is hue = column (8 hues left to right), brightness = row
(8 levels top to bottom); `probe_reference.png` is the legend. Read off which
cells cover the cuff, then paint exactly those cells in the `skins-png/` PNGs.
Reinstall the real archive afterwards to undo the probe.

## Rollback

The live `Patch-C.MPQ` is untouched by everything above. If an import goes
wrong, restore from the backup you take before copying:

    3.3.5a - Dev\Backups\patch-c-before-portswap2-20260912-000421\Patch-C.MPQ

That is the known-good legacy state (954 MB, model 8,925,568 B).

## Background

The model itself is byte-identical to the one shipped by the Ascension client
(`patch-CHA.MPQ`, md5 9a04811ce8c3), so there is nothing to swap - the art is
the art. The Shadowlands-to-WOTLK port's higher-poly build is a different mesh
that crashes the 3.3.5a client and must not be installed.
