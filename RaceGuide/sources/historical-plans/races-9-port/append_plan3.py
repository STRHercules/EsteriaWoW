"""Record the attachment-table finding and the calibration round."""
import datetime
import pathlib

path = pathlib.Path("races-9-port.PLAN.md")
stamp = datetime.datetime.now().strftime("%Y-%m-%d")
section = f'''

## Vulpera head attachment: the table the client actually reads (2026-09-14, eighteenth pass)

The previous pass patched the wrong copy.  The Vulpera model carries several identical
23-record `id/bone/pivot` tables (at 0x171e20, 0x2e4230, 0x451b40, 0x5befb0, 0x5bf790 for
the male), but **none of them is referenced by the header** - they are leftovers.  The
attachment array the client parses is the one the header points at, and for the Vulpera that
is header slot **0xF0** (43 records at 0x674c36), the same slot that carries the human's 39
attachments at 0x859e0 (verified against the human/gnome header layout: slots 0xD8/0xE0/0xE8/
0xF0/0xF8 line up index for index).

Real values, after reading slot 0xF0 in both genders:

| model | attachment 11 bone | pivot |
|---|---|---|
| vulperamale | 195 | `(-0.001, 0.000, 1.270)` |
| vulperafemale | 195 | `(-0.119, 0.000, 1.291)` |

That anchor sits about 0.2 *above* the skull - the helm floats high, which is exactly what
the first Vulpera screenshot showed.  The unreferenced tables say `(-0.116, 0.000, 1.089)`,
which is why editing them changed nothing in game.

`retune_vulpera_helm_calibration.py` computes the ideal offset from the model itself: the
bounding box of the vertices weighted to the head bone and its descendants (ear tips above
`head bone z + 0.30` excluded, since the ears are meant to stick out) minus the helmet's own
vertex box, minus the real anchor.  Male: `dx -0.102, dz -0.099`; female: `dx +0.025,
dz -0.115`.  Seven leather-helm items (50679, 50713, 51494, 51825, 50073, 47688, 47690) carry
their own copy of the donor Vulpera leather helm, shifted around that ideal:

| item | variant | offset from the ideal |
|---|---|---|
| 50679 | A | none (computed ideal) |
| 50713 | B | 0.10 lower |
| 51494 | C | 0.10 higher |
| 51825 | D | 0.09 back |
| 50073 | E | 0.09 forward |
| 47688 | F | back + lower |
| 47690 | G | forward + lower |

All seven rows now carry the same helmet geoset-vis pair (`285`) so the comparison is about
fit only: round one's "ears and nose vanish" on 47688/47690 came from those rows' own vis
ids (248/306 and 246/307), not from the shift.

Backup: `Backups/patch-y-before-vulpera-calibration2-20260914-003909` (Patch-Y 575,924,170
bytes).
'''
path.write_text(path.read_text(encoding="utf-8") + section, encoding="utf-8")
print("appended", len(section), "characters")
