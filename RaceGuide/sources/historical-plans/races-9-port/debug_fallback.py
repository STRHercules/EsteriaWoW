"""Reproduce the fallback lookup through the fix script's own helpers."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fix_item_component_prefixes as fix

storm = fix.Storm(fix.DLL_DEFAULT)
ours = fix.open_archives(storm, fix.CLIENT, fix.OUR_ORDER)
donor = fix.open_archives(storm, fix.DONOR, fix.DONOR_ORDER)
print("ours archives:", [name for name, _h in ours])
for key in [
    "Item\\ObjectComponents\\Head\\Helm_Eyepatch_A_02_BeM.m2",
    "Item\\ObjectComponents\\Head\\Helm_Goggles_B_04_DwM.m2",
    "Item\\ObjectComponents\\Head\\Helm_Goggles_B_04_PaM.m2",
]:
    print(key.split("\\")[-1], "->", fix.read(storm, ours, key)[0])
for _name, handle in ours + donor:
    storm.dll.SFileCloseArchive(handle)
