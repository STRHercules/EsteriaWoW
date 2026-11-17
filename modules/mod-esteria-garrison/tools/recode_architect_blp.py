# Rewrites the cropped architect BLPs as DXT5 and keeps the frame sizes in step.
import importlib.util
import re
import struct
from pathlib import Path

import numpy as np

ROOT = Path(r"g:\risServer")
spec = importlib.util.spec_from_file_location(
    "arch", ROOT / "EsteriaWoW" / "modules" / "mod-esteria-garrison" / "tools" / "build_retail_architect.py")
arch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arch)

art = ROOT / "Esteria - Client" / "Interface" / "AddOns" / "Blizzard_GarrisonUI" / "Art"
addon = ROOT / "Esteria - Client" / "Interface" / "AddOns" / "EsteriaGarrison" / "Retail"
xml_path = addon / "Blizzard_GarrisonBuildingUI.xml"
atlas_path = addon / "Atlas.lua"
xml = xml_path.read_text(encoding="utf-8")
atlas = atlas_path.read_text(encoding="utf-8")

converted = 0
for path in sorted(art.glob("*.blp")):
    data = path.read_bytes()
    if len(data) < 148 or data[:4] != b"BLP2" or data[8] != 3:
        continue
    width, height = struct.unpack_from("<II", data, 12)
    offset = struct.unpack_from("<I", data, 20)[0]
    raw = np.frombuffer(data, dtype=np.uint8, offset=offset, count=width * height * 4).reshape(-1, 4)
    rgba = np.empty_like(raw)
    rgba[:, 0], rgba[:, 1], rgba[:, 2], rgba[:, 3] = raw[:, 2], raw[:, 1], raw[:, 0], raw[:, 3]
    arch.write_blp(path, width, height, rgba.tobytes())
    converted += 1

for path in sorted(art.glob("*.blp")):
    data = path.read_bytes()
    width, height = struct.unpack_from("<II", data, 12)
    pattern = re.escape(path.name) + r'(.{0,240}?)<Size x="(\d+)" y="(\d+)"/>'

    def swap(match, width=width, height=height):
        if int(match.group(2)) == width and int(match.group(3)) == height:
            return match.group(0)
        old = '<Size x="%s" y="%s"/>' % (match.group(2), match.group(3))
        new = '<Size x="%d" y="%d"/>' % (width, height)
        return match.group(0).replace(old, new, 1)

    xml = re.sub(pattern, swap, xml)
    atlas = re.sub(
        re.escape(path.name) + r'",\d+,\d+',
        '%s",%d,%d' % (path.name, width, height),
        atlas)

xml_path.write_text(xml, encoding="utf-8")
atlas_path.write_text(atlas, encoding="utf-8")
sample = art / "Garr_WoodFrameCorner.blp"
blob = sample.read_bytes()
print("converted", converted, "resized", resized, "corner enc", blob[8], "pref", blob[10], "size", struct.unpack_from("<II", blob, 12))
