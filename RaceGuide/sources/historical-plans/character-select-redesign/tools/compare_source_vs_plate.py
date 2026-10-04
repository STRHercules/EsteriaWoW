"""Is the client plate a faithful rendition of the supplied source?

If it is, the sources buy nothing at the 46px the roster draws. Compares the client
plate against a fresh mask+downscale of the supplied 130x130 source, and also checks
whether the supplied illidari (DemonHunter) art is intact - the client's own
DemonHunter plates measured 0.024 opaque, i.e. effectively blank.

Usage:
    python .agents/plans/character-select-redesign/tools/compare_source_vs_plate.py
"""

from __future__ import annotations

import ctypes
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parents[2]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / ".agents" / "plans" / "elvui-glue-reskin"))

from blp import decode_blp  # noqa: E402
from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

SOURCES = Path(r"R:\Users\Zach\Pictures\Portraits")
DATA = Path(r"G:\3.3.5a - Dev\Data")
SUPERSAMPLE = 4


def fresh_from_source(source: Image.Image, size: int) -> Image.Image:
    flat = Image.new("RGBA", source.size, (0, 0, 0, 0))
    flat.alpha_composite(source.convert("RGBA"))
    big = (size * SUPERSAMPLE, size * SUPERSAMPLE)
    mask = Image.new("L", big, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, big[0] - 1, big[1] - 1), fill=255)
    # mask at the working resolution, so the rim is antialiased at the final size
    scaled = flat.resize((size, size), Image.LANCZOS)
    scaled.putalpha(Image.composite(scaled.getchannel("A"),
                                    Image.new("L", (size, size), 0),
                                    mask.resize((size, size), Image.LANCZOS)))
    return scaled


def opaque_ratio(img: Image.Image) -> float:
    histogram = img.convert("RGBA").getchannel("A").histogram()
    return histogram[255] / float(img.width * img.height)


storm = Storm(DLL_DEFAULT)
# StormLib refuses to open the same archive twice, so handles are opened once and
# reused; the first version of this script re-opened and died on a sharing violation.
_handles: dict[Path, object] = {}


def open_once(archive: Path):
    if archive not in _handles:
        _handles[archive] = storm.open_archive(archive)
    return _handles[archive]


def read_plate(name: str):
    for archive in (DATA / "patch-Z.MPQ", DATA / "patch-A.MPQ"):
        if not archive.exists():
            continue
        try:
            return decode_blp(storm.read(
                open_once(archive),
                f"Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-{name}.blp"))
        except OSError:
            continue
    return None


plate = read_plate("HumanMale")

source_path = next(SOURCES.rglob("Charactercreate-races_human-male.png"))
source = Image.open(source_path).convert("RGBA")

if plate is not None:
    fresh = fresh_from_source(source, 64)
    diff = ImageChops.difference(plate.convert("RGB"), fresh.convert("RGB"))
    # only compare where the fresh mask is opaque, so the rim is not counted
    box = fresh.getchannel("A").point(lambda v: 255 if v == 255 else 0)
    stat = Image.new("L", diff.size, 0)
    stat.paste(diff.convert("L"), mask=box)
    pixels = box.histogram()[255]
    total = sum(i * n for i, n in enumerate(stat.histogram()))
    print(f"client plate vs fresh-from-source, inside the circle ({pixels}px):")
    print(f"  mean abs RGB difference : {total / max(pixels, 1):.2f} / 255")
    print(f"  plate opaque ratio      : {opaque_ratio(plate):.3f}")
    print(f"  fresh opaque ratio      : {opaque_ratio(fresh):.3f}")
    print()

print("supplied illidari (DemonHunter) sources:")
for path in sorted(SOURCES.rglob("*illidari*.png")):
    img = Image.open(path).convert("RGBA")
    print(f"  {path.parent.name:<9} {path.name:<48} opaque={opaque_ratio(img):.3f}")

print()
print("client DemonHunter plates:")
for name in ("DemonHunterMale", "DemonHunterAllianceMale", "DemonHunterHordeMale"):
    img = read_plate(name)
    if img is not None:
        print(f"  {name:<28} opaque={opaque_ratio(img):.3f}")
