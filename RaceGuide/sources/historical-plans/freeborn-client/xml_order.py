import xml.etree.ElementTree as ET
from pathlib import Path
p = Path(r".agents\plans\freeborn-client\rollback\CharacterCreate.xml")   # stock copy from the pristine backup
root = ET.fromstring(p.read_text(encoding="utf-8"))
both, seen = [], set()
for e in root.iter():
    kids = [c.tag.split("}")[-1] for c in e]
    s = set(kids)
    if "Anchors" in s and "Layers" in s:
        both.append((e.get("name") or e.tag.split("}")[-1], kids))
print("elements in the STOCK file having both Anchors and Layers:", len(both))
for name, kids in both[:12]:
    print(f"  {name}: {kids[:8]}")
# also: any element with Layers and Scripts
ls = [(e.get("name") or e.tag.split("}")[-1], [c.tag.split("}")[-1] for c in e])
      for e in root.iter() if {"Layers","Scripts"} <= {c.tag.split("}")[-1] for c in e}]
print("elements having both Layers and Scripts:", len(ls))
for name, kids in ls[:8]:
    print(f"  {name}: {kids[:8]}")
