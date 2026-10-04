import sys
from pathlib import Path
ROOT = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(ROOT / "tools"))
from cars_mount_pack import DLL_DEFAULT, Storm
CLIENT = Path(r"G:\3.3.5a - Dev")
LUA = "Interface\\GlueXML\\CharacterCreate.lua"
def read(a):
    s = Storm(DLL_DEFAULT); h = s.open_archive(a)
    try: return s.read(h, LUA).decode("utf-8")
    finally: s.dll.SFileCloseArchive(h)
stock = read(CLIENT / "Data" / "_freeborn-backups" / "20260924T063018Z" / "patch-Z.MPQ")
dep = read(CLIENT / "Data" / "patch-Z.MPQ")
i = dep.index("-- >>> freeborn-third-team")
prefix = dep[:i].rstrip("\n")
print("stock tail :", repr(stock[-60:]))
print("prefix tail:", repr(prefix[-60:]))
print("equal      :", prefix == stock.rstrip("\n"))
print("equal(raw) :", dep[:i] == stock)
# first difference
n = min(len(prefix), len(stock.rstrip("\n")))
for k in range(n):
    if prefix[k] != stock.rstrip("\n")[k]:
        print("first diff at char", k)
        print("  stock :", repr(stock.rstrip("\n")[k-40:k+40]))
        print("  prefix:", repr(prefix[k-40:k+40]))
        break
else:
    print("common region identical; lengths", len(prefix), len(stock.rstrip("\n")))
