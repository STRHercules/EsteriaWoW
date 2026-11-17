import importlib.util
from pathlib import Path

p = Path(r"g:\risServer\EsteriaWoW\modules\mod-esteria-garrison\tools\build_retail_architect.py")
spec = importlib.util.spec_from_file_location("arch", p)
arch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arch)

art = Path(r"g:\risServer\Esteria - Client\Interface\AddOns\Blizzard_GarrisonUI\Art")
names = [
    "GarrMission_FollowerPartyBox_Sm.blp",
    "GarrMission_EncounterAbilityBorder-Lg.blp",
    "GarrMission_EncounterBar-Elite.blp",
    "GarrMission_EncounterBar-PortraitRing.blp",
    "GarrMission_PortraitRing_Glow.blp",
]
for name in names:
    path = art / name
    data = path.read_bytes()
    print(name, "enc", data[8], "alpha", data[10], "w", arch.u32(data, 12), "h", arch.u32(data, 16))
    sheet = arch.load_sheet(path)
    if not sheet:
        print("  no dxt5")
        continue
    w, h, rgba = sheet
    minx, miny, maxx, maxy = w, h, 0, 0
    for y in range(h):
        row = y * w * 4
        for x in range(w):
            if rgba[row + x * 4 + 3] > 8:
                if x < minx:
                    minx = x
                if y < miny:
                    miny = y
                if x > maxx:
                    maxx = x
                if y > maxy:
                    maxy = y
    print("  opaque", minx, miny, maxx, maxy)
