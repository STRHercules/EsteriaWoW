"""Record the baked Vulpera anchor + geoset finding."""
import datetime
import pathlib

path = pathlib.Path("races-9-port.PLAN.md")
stamp = datetime.datetime.now().strftime("%Y-%m-%d")
section = f'''

## Vulpera anchor baked in; the ear/nose vanish is geometry, not a mask (2026-09-14, nineteenth pass)

User result: the seven calibration items no longer lose ears or nose ("looks like you fixed
that"), but the real *Skullsplitter Helm* (item 1624 -> display 15340 -> `Helm_Plate_D_03`)
still swallows them.

Checked the visibility theory first: `HelmetGeosetVisData` rows 248/306 (which the
Skullsplitter uses) differ from 285, but the Vulpera model cannot respond to them at all -
`vulperamale00.skin` and `01.skin` declare **geoset 0 for every one of their 55 / 94 batches**
(`skinSection` alone runs 0..54 / 0..93), while a stock human spreads 61 batches over geosets
0..60.  A mask can only hide whole geoset groups, so it cannot remove just the muzzle and
ears; what the user saw is the plate helmet's own shell covering them while the helmet sat
about 0.2 above the skull.  `Helm_Plate_D_03_VuM/F.m2` (the donor's Vulpera-shaped plate
helm, 6,898 bytes each) is present, so the shape is right once the anchor is.

`apply_vulpera_head_anchor.py` therefore writes the computed ideal straight into attachment
11 of the model's real table (header slot 0xF0) in Patch-Y:

| model | old pivot | new pivot |
|---|---|---|
| vulperamale | `(-0.001, 0.000, 1.270)` | `(-0.103, 0.000, 1.171)` |
| vulperafemale | `(-0.119, 0.000, 1.291)` | `(-0.093, 0.000, 1.176)` |

The ten `HelmCal*` files are re-staged as small deltas around that baked value, so one more
session can refine it if needed: A = the baked value, B 0.10 lower, C 0.10 higher, D 0.09
back, E 0.09 forward, F back+lower, G forward+lower.

Backup: `Backups/patch-y-before-vulpera-anchor-20260914-004241` (Patch-Y 603,491,971 bytes).
'''
path.write_text(path.read_text(encoding="utf-8") + section, encoding="utf-8")
print("appended", len(section), "characters")
