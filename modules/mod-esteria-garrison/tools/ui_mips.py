"""Mipmaps for the garrison UI textures, which retail ships with one level: drawn smaller than native (most of the
architect, mission and report windows) they alias into jagged edges.

    python ui_mips.py retail             # data/ui_seeds.txt originals -> G:/garrison-build/retail-mipped/<fdid>.bin
    python ui_mips.py addon <src> <dst>  # every .blp under <src> (Blizzard_GarrisonUI\\Art) -> <dst>, same names

Re-encoded as BLP2 DXT5 (DXT1 when fully opaque) with every mip down to 1x1 by the housing world-map writer
(wowdecomp docs/housing/tools/ui/make_worldmap.py blp). retail_assets.py pack takes a mipped file over the original.
"""
import struct
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, r"R:\Users\Zach\Documents\GitHub\wowdecomp\docs\housing\tools\ui")
from make_worldmap import blp  # noqa: E402

CACHE = Path(r"G:\garrison-build\retail-originals")
MIPPED = Path(r"G:\garrison-build\retail-mipped")


def remip(src, dst):
    data = src.read_bytes()
    if data[8] == 3:  # uncompressed BGRA (the landing-page atlas sheets): Pillow cannot read it
        width, height = struct.unpack_from("<2I", data, 12)
        offset = struct.unpack_from("<I", data, 20)[0]
        rgba = Image.frombytes("RGBA", (width, height), data[offset:offset + width * height * 4], "raw", "BGRA")
    else:
        rgba = Image.open(src).convert("RGBA")
    opaque = rgba.getextrema()[3][0] == 255
    dst.write_bytes(blp(rgba, opaque))


def main():
    mode = sys.argv[1]
    if mode == "retail":
        MIPPED.mkdir(parents=True, exist_ok=True)
        ids = [line.split(".")[0] for line in (HERE.parent / "data" / "ui_seeds.txt").read_text().split()]
        done = 0
        for fdid in ids:
            src = CACHE / f"{fdid}.bin"
            if src.exists() and src.read_bytes()[:4] == b"BLP2":
                remip(src, MIPPED / f"{fdid}.bin")
                done += 1
        print(f"{done} retail UI textures mipped into {MIPPED}")
    else:
        src, dst = Path(sys.argv[2]), Path(sys.argv[3])
        files = sorted(src.rglob("*.blp"))
        for path in files:
            out = dst / path.relative_to(src)
            out.parent.mkdir(parents=True, exist_ok=True)
            remip(path, out)
        print(f"{len(files)} addon textures mipped into {dst}")


if __name__ == "__main__":
    main()
