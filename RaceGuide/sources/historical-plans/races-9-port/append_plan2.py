"""Append the Vulpera helmet-fix pass to the running plan log."""
import datetime
import pathlib

path = pathlib.Path("races-9-port.PLAN.md")
stamp = datetime.datetime.now().strftime("%Y-%m-%d")
section = f'''

## Vulpera helmet placement and face (2026-09-14, seventeenth pass)

User result: helmets now render on every race.  Two Vulpera problems remain - the helmet
sits far from the head (tilted up/forward) and covers the face while it is on.

### What the data says

`Item\\ObjectComponents\\Head` models are anchored on M2 attachment **id 11**; the client
links head components with `push 0xb` into `CharAddAttachmentLink` (`0x4eaa70`).

* Vulpera model = Eunoia `Patch-5` `character\\vulpera\\male\\vulperamale.m2`, byte-identical
  (13,403,570 bytes, sha1 `afff67eb445c`), `.anim` set also from `Patch-5`, donor's `_Vu`
  helmet models from `patch-I` - i.e. exactly the donor's own pairing.
* The Vulpera model is the only ported model with the old `0x28`-byte attachment records
  (id, bone, inline pivot, track); `M2.ReadAttachments` (`0x839080`) walks that stride, so
  the format is right.  Broken/Eredar/Pandaren have no such table at all.
* Its attachment 11 is bound to dummy bone 195 whose pivot is *equal* to the head key bone
  (56) pivot `(-0.116, 0.000, 1.089)` - the **neck joint**.  Every race whose helmets look
  right anchors it inside the skull instead: the human's is 0.184 above its head bone, the
  Pandaren's 0.187 below, and both carry stock-convention helmet geometry (origin near the
  top, mesh hanging down: human `_HuM` bbox z -0.402..+0.033).
* The donor's `_Vu` helmet geometry is authored around the *middle* of the helmet
  (bbox z -0.159..+0.256), i.e. for a different anchor convention than the stock sets that
  work everywhere else.
* Our `Wow.exe` is a different build from the donor's (7,716,352 vs 7,880,192 bytes), so the
  donor's rendering cannot be used as proof that the same numbers look right there.

### Fix

`fix_vulpera_head_attachment.py` stages a patched `vulperamale.m2` / `vulperafemale.m2` into
Patch-Y (the model itself stays in `Patch-C`) with attachment 11's pivot moved to the top of
the skull - the position of the model's own head-top dummy bone, `(-0.119, 0.000, 1.294)`
male and `(-0.119, 0.000, 1.291)` female.  Every attachment table in the file is rewritten
(the model carries five identical copies, six in the female).

`fix_item_component_prefixes.py --set 20=Hu` moves race 20 from `Vu` to the stock Human set,
so the Vulpera uses the same anchor convention (attachment at the top of the skull, helmet
geometry hanging down) as the races that render correctly.

Backups: `Backups/patch-y-before-vulpera-head-attachment-20260914-002407`,
`Backups/patch-y-before-item-component-prefixes-20260914-002414` (Patch-Y 547,837,826 bytes).

### Open

* If the helmet now sits correctly but the donor's Vulpera-specific shapes are wanted back,
  the `_Vu` set would have to be re-anchored (verts shifted from a centred to a top origin).
* Face features: with the helmet anchored correctly the face should no longer be covered;
  if anything still hides it, the next suspect is the helmet geoset-vis mask
  (`HelmetGeosetVisData.dbc`, 8 fields, no obvious per-race column).
'''
path.write_text(path.read_text(encoding="utf-8") + section, encoding="utf-8")
print("appended", len(section), "characters")
