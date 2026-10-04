"""Append this pass to the running plan log."""
import datetime
import pathlib

path = pathlib.Path("races-9-port.PLAN.md")
stamp = datetime.datetime.now().strftime("%Y-%m-%d")
section = f'''

## Helmet cubes: the head item-component path (2026-09-14, sixteenth pass)

User report: every ported race draws its helmet as the white/blue missing-model cube,
while race 14 (Broken) renders helmets normally; Dracthyr renders one but at the wrong
offset (male forward, female back).

### Root cause

`Wow.exe` builds the model name for an equipped head item in the item-component
constructor at `0x732100`:

```asm
0x0073211c  mov  esi, [ebp + 0xc]        ; equipment slot
0x0073213d  mov  edi, 0x9f6c0c           ; "Item\\ObjectComponents\\Head\\"
0x007321e2  mov  ecx, [ecx + esi*4]      ; ChrRaces row (records at 0xad3448)
0x007321f7  mov  eax, [ecx + 0x18]       ; row + 0x18 = field 6 = ClientPrefix
0x00732202  push 0xa34d00                ; "%s%s_%s%s.mdx"
```

so the client asks for `Item\\ObjectComponents\\Head\\<ModelName>_<ClientPrefix><M|F>.mdx`
(falling back to `.m2`), and stamps the cube when that file is missing. Field 6 is the
`ChrRaces` column the port wrote from `port_race.py`'s `"prefix"` key. Slot 3 (shoulder)
takes the other branch (`0x73221d`, format `0x9e1ad0` = `%s%s`), which is why shoulder
models carry no race suffix and were never affected.

Our port invented prefixes that no archive supplies (`Er`, `Nb`, `Ve`, `Lf`, `Za`, `Di`,
`Kt`, `Il`), so every one of those races cubed its helm. Broken worked because Patch-C
ships a full `_Bk` model set; Pandaren and Vulpera (`Pa`, `Vu`) had no set in our client
at all; Dracthyr was pointed at `Dr`, which collides with Draenei - hence a helmet that
renders but sits at the Draenei offset.

### Fix

`fix_item_component_prefixes.py` rewrites `ChrRaces` field 6 in Patch-Y to the prefixes
the donor client uses for the same races, and stages the donor's two dedicated sets:

| race | was | now | source of the model set |
|---|---|---|---|
| 14 Broken | Bk | Bk | Patch-C (already complete) |
| 15 Sethrak | Se | Tr | stock Troll set |
| 16 Eredar | Er | Dr | stock Draenei set |
| 17 Nightborne | Nb | Ni | stock Night Elf set |
| 18 Pandaren | Pa | Pa | donor `_Pa` set, staged into Patch-Y |
| 19 Void Elf | Ve | Be | stock Blood Elf set |
| 20 Vulpera | Vu | Vu | donor `_Vu` set, staged into Patch-Y |
| 21 Lightforged | Lf | Dr | stock Draenei set |
| 22 Zandalari | Za | Tr | stock Troll set |
| 23 Dark Iron | Di | Dw | stock Dwarf set |
| 28 Dracthyr | Dr | Be | stock Blood Elf set |
| 29 Kul Tiran | Kt | Ni | stock Night Elf set |
| 30 Illidari (Horde) | Il | Be | stock Blood Elf set |
| 31 Illidari (Alliance) | Il | Ni | stock Night Elf set |

Staging: 3232 files (41.4 MB) under `Item\\ObjectComponents\\Head\\` - the donor copies
for all 423 head stems our client ships, both sexes, `.m2` + `00.skin`. 132 names the
donor has no dedicated model for (eyepatch, goggles, a few PvP sets) borrow the same stem
from a stock code so they still render instead of cubing.

Backup: `Backups/patch-y-before-item-component-prefixes-20260914-000154` (Patch-Y was
476,918,016 bytes, is now 520,427,625).

### Verification

* `verify_prefix_edit.py` diffs the new `ChrRaces` against the backup: exactly 11 fields
  changed, all field 6, all non-empty prefixes two characters.
* `validate_patch_y_dbcs.py`: 11 DBC entries, 0 malformed.
* `verify_helm_coverage.py`: for `Helm_Leather_B_06` (item 30935), `Helm_Cloth_A_01` and
  `Helm_Plate_D_02`, both sexes, model + skin, every custom race resolves a file.

### Still open

* Dracthyr helmet offset (male forward, female back) - the fix moves Dracthyr off the
  Draenei set onto the Blood Elf one; if the offset survives, the head attachment inside
  the ported Dracthyr M2 is the next suspect (`dump_m2_attachments.py` is still blind on
  these models).
* Sethrak is in `CharBaseInfo` with all ten classes but the user has never reported it on
  the creator; it now has a working prefix either way.
'''
path.write_text(path.read_text(encoding="utf-8") + section, encoding="utf-8")
print("appended", len(section), "characters")
