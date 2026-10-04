"""Does opening Patch-Y for write break reads from the other handles?"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fix_item_component_prefixes as fix

storm = fix.Storm(fix.DLL_DEFAULT)
ours = fix.open_archives(storm, fix.CLIENT, fix.OUR_ORDER)
donor = fix.open_archives(storm, fix.DONOR, fix.DONOR_ORDER)
key = "Item\\ObjectComponents\\Head\\Helm_Eyepatch_A_02_BeM.m2"
print("before patch-y open:", fix.read(storm, ours, key)[0])

handle = fix.H()
opened = storm.dll.SFileOpenArchive(str(fix.PATCH_Y), 0, 0, handle)
print("patch-y write open:", opened, "value:", handle.value)
print("after patch-y open:", fix.read(storm, ours, key)[0])
print("donor read after:", fix.read(storm, donor, "Item\\ObjectComponents\\Head\\Helm_Cloth_A_01_PaM.m2")[0])
if handle.value:
    storm.dll.SFileCloseArchive(handle)
for _name, item in ours + donor:
    storm.dll.SFileCloseArchive(item)
