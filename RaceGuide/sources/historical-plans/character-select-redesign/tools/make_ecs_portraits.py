"""Generate the ECS portrait set from the supplied race art.

Source art: `R:\\Users\\Zach\\Pictures\\Portraits` - 56 PNGs at 130x130, the
UNMASKED originals the client's 64x64 circular plates were made from. Each has a
solid black background outside the face, so a circular mask supplies the shape.

This replaces the earlier approach of masking the client's own plates, which was
pointless: those plates are already circular (measured corner alpha 0 on all 62 of
them), so masking them again only softened an edge that was already cut. Deriving
from the originals also means ECS owns its art and no longer needs the client
archives open to regenerate it.

Also converts the supplied character-select art into BLP2 textures and regenerates
the procedural note dot and search icon, so this one tool owns the whole ECS texture
set.

Usage:
    python .agents/plans/character-select-redesign/tools/make_ecs_portraits.py
    python .agents/plans/character-select-redesign/tools/make_ecs_portraits.py --check
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parents[2]
sys.path.insert(0, str(REPO / ".agents" / "plans" / "elvui-glue-reskin"))

from blp import encode_blp_bgra  # noqa: E402

SOURCE_DIR = Path(r"R:\Users\Zach\Pictures\Portraits")
UI_SOURCE_DIR = Path(r"R:\Users\Zach\Pictures\UI\Secondary\Smaller")
UI_VARIANT_SOURCE_DIR = UI_SOURCE_DIR / "New folder"
OUT_BLP = ROOT / "textures"
OUT_PNG = ROOT / "textures" / "source-png"

# The roster draws portraits at C.PORTRAIT_SIZE (46px). 64 matches the client's own
# plates and leaves headroom if that constant grows, without the ~3MB that 96+ costs.
PORTRAIT_SIZE = 64
SUPERSAMPLE = 4

# The mask is inscribed with a 1px inset rather than edge-to-edge. The shipped
# plates leave ~4.4px of margin (a circle only 0.864 of the frame), which puts a
# visible gap between the face and the 50px ring drawn over it; filling the frame
# closes that gap without clipping the face's own edge.
MASK_INSET = 1

DOT_SIZE = 32
DOT_COLOUR = (253, 122, 43, 255)   # ElvUI accent #FD7A2B

# Magnifier for the search box. Drawn rather than sourced: it is three shapes, and
# a generated one keeps the set reproducible without another art dependency.
ICON_SIZE = 32   # power-of-two BLP size; the screen renders it at 12px
ICON_COLOUR = (200, 200, 200, 255)

# The client expects power-of-two BLP dimensions. The long status treatments are
# resampled to 1024x256 and stretched across one 258x70 roster row; the portrait
# border is padded to 128x128 so its source pixels are not distorted.
UI_ART: dict[str, tuple[Path, tuple[int, int]]] = {
    "ECS-Portrait-Border": (UI_SOURCE_DIR / "PortraitBorder.png", (128, 128)),
    "ECS-Row-Idle-Grey": (UI_VARIANT_SOURCE_DIR / "GreyLarge.png", (1024, 256)),
    "ECS-Row-Hover-Alliance-Blue": (UI_VARIANT_SOURCE_DIR / "BlueLarge.png", (1024, 256)),
    "ECS-Row-Hover-Horde-Red": (UI_VARIANT_SOURCE_DIR / "RedLarge.png", (1024, 256)),
    "ECS-Row-Hover-Freeborn-Purple": (UI_VARIANT_SOURCE_DIR / "PurpleLarge.png", (1024, 256)),
    "ECS-Row-Selected-Gold": (UI_VARIANT_SOURCE_DIR / "GoldLarge.png", (1024, 256)),
    "ECS-Level-Border": (UI_SOURCE_DIR / "LevelBorder32.png", (32, 32)),
}

# Source stem -> art key. The art key is the name the CLIENT uses for the portrait
# file, which is NOT the model token or the source file name:
#   * the client ships UI-CharacterCreate-Zandalari<sex>, not ...-ZandalariTroll;
#   * the undead plate is UI-CharacterCreate-Scourge<sex>;
#   * the create screen's Zandalari token is ZANDALARITROLL and its Illidari tokens
#     are ILLIDARI_ALLIANCE / ILLIDARI_HORDE, which is why illidari art is keyed per
#     faction and the two factions are genuinely different art (verified).
# tools/check_artkeys.py validates this whole table against the create screen.
ART_KEYS: dict[tuple[str, str, str], str] = {
    ("darkfallen", "_alliance", "Alliance"): "Darkfallen",
    ("darkfallen", "_horde", "Horde"): "DarkfallenHorde",
    ("illidari", "", "Alliance"): "DemonHunterAlliance",
    ("illidari", "", "Horde"): "DemonHunterHorde",
    ("undead", "", "Horde"): "Scourge",
    ("ZandalariTroll", "", "Horde"): "Zandalari",
    ("panda", "", "Alliance"): "Pandaren",
    ("worgen", "2", "Alliance"): "Worgen",
    ("kultiranhuman", "", "Alliance"): "KulTiran",
    ("darkirondwarf", "", "Alliance"): "DarkIron",
    ("highelf", "", "Alliance"): "HighElf",
    ("voidelf", "", "Alliance"): "VoidElf",
    ("nightelf", "", "Alliance"): "NightElf",
    ("lightforged", "", "Alliance"): "Lightforged",
    ("dracthyr-visage", "", "Horde"): "Dracthyr",
    ("bloodelf", "", "Horde"): "BloodElf",
    ("nightborne", "", "Horde"): "Nightborne",
    ("human", "", "Alliance"): "Human",
    ("dwarf", "", "Alliance"): "Dwarf",
    ("gnome", "", "Alliance"): "Gnome",
    ("draenei", "", "Alliance"): "Draenei",
    ("orc", "", "Horde"): "Orc",
    ("tauren", "", "Horde"): "Tauren",
    ("troll", "", "Horde"): "Troll",
    ("goblin", "", "Horde"): "Goblin",
    ("broken", "", "Horde"): "Broken",
    ("eredar", "", "Horde"): "Eredar",
    ("vulpera", "", "Horde"): "Vulpera",
}

STEM = re.compile(r"^(?P<base>.+?)-(?P<sex>male|female)(?P<variant>2|_alliance|_horde)?$", re.I)


def circular_mask(width: int, height: int, inset: int = 0) -> Image.Image:
    """Antialiased inscribed-circle mask, built oversized and downsampled.

    A 64x64 circle drawn directly has a visibly stepped rim; building it at 4x and
    resampling with LANCZOS gives a smooth edge in the final texture.
    """
    big_w, big_h = width * SUPERSAMPLE, height * SUPERSAMPLE
    mask = Image.new("L", (big_w, big_h), 0)
    radius = (min(big_w, big_h) / 2.0) - (inset * SUPERSAMPLE)
    centre_x, centre_y = big_w / 2.0, big_h / 2.0
    ImageDraw.Draw(mask).ellipse(
        [centre_x - radius, centre_y - radius, centre_x + radius, centre_y + radius], fill=255
    )
    return mask.resize((width, height), Image.LANCZOS)


def dot_texture(size: int = DOT_SIZE) -> Image.Image:
    big = size * SUPERSAMPLE
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    radius = (big / 2.0) - 2 * SUPERSAMPLE
    ImageDraw.Draw(img).ellipse(
        [big / 2.0 - radius, big / 2.0 - radius, big / 2.0 + radius, big / 2.0 + radius],
        fill=DOT_COLOUR,
    )
    return img.resize((size, size), Image.LANCZOS)


def load_ui_art(source_path: Path, size: tuple[int, int]) -> Image.Image:
    """Load supplied transparent art and normalize it to client-safe dimensions."""
    if not source_path.exists():
        raise SystemExit(f"character-select art not found: {source_path}")

    image = Image.open(source_path).convert("RGBA")
    if source_path.name == "PortraitBorder.png":
        canvas = Image.new("RGBA", size, (0, 0, 0, 0))
        canvas.alpha_composite(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
        return canvas

    return image.resize(size, Image.Resampling.LANCZOS)


def search_icon_texture(size: int = ICON_SIZE) -> Image.Image:
    """A magnifier: a ring plus a handle, drawn oversampled then downsampled.

    Anything drawn at 24px directly comes out stepped, so this follows the same
    supersample-then-resample rule as the portrait mask.
    """
    big = size * SUPERSAMPLE
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    stroke = max(1, round(big * 0.09))

    # lens: upper-left, inscribed in the top-left ~70% of the canvas
    inset = big * 0.12
    lens = big * 0.56
    draw.ellipse([inset, inset, inset + lens, inset + lens],
                 outline=ICON_COLOUR, width=stroke)

    # handle: from the lens edge out to the lower-right corner, with a round cap
    start = inset + lens * 0.74
    end = big - inset * 0.9
    draw.line([start, start, end, end], fill=ICON_COLOUR, width=stroke)
    cap = stroke / 2.0
    draw.ellipse([end - cap, end - cap, end + cap, end + cap], fill=ICON_COLOUR)

    return img.resize((size, size), Image.LANCZOS)


def build_portrait(path: Path) -> Image.Image:
    source = Image.open(path).convert("RGBA")
    # The source art is fully opaque with a black background, so the alpha channel
    # carries no shape of its own: the mask supplies the entire silhouette.
    scaled = source.resize((PORTRAIT_SIZE, PORTRAIT_SIZE), Image.LANCZOS)
    scaled.putalpha(Image.composite(
        scaled.getchannel("A"),
        Image.new("L", scaled.size, 0),
        circular_mask(PORTRAIT_SIZE, PORTRAIT_SIZE, MASK_INSET),
    ))
    return scaled


def collect() -> dict[str, Path]:
    """Output stem (`<artKey><Male|Female>`) -> source path.

    Keyed by the FULL stem, not just the art key: every art key ships two files and
    keying by art key alone collapsed each male/female pair into one collision.
    """
    found: dict[str, Path] = {}
    problems: list[str] = []
    for path in sorted(SOURCE_DIR.rglob("*.png")):
        stem = re.sub(r"^Charactercreate-races_", "", path.stem, flags=re.I)
        match = STEM.match(stem)
        if not match:
            problems.append(f"unparsed source name: {path.name}")
            continue
        base = match.group("base")
        variant = (match.group("variant") or "").casefold()
        side = path.parent.name
        art_key = ART_KEYS.get((base, variant, side))
        if art_key is None:
            problems.append(f"no art key for {path.name} (base={base!r} variant={variant!r} side={side})")
            continue
        name = f"{art_key}{match.group('sex').title()}"
        if name in found:
            problems.append(f"{name} claimed twice: {found[name].name} and {path.name}")
            continue
        found[name] = path
    for problem in problems:
        print(f"  WARNING {problem}")
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="report coverage without writing any files")
    args = parser.parse_args()

    if not SOURCE_DIR.exists():
        raise SystemExit(f"source portraits not found: {SOURCE_DIR}")

    portraits = collect()
    print(f"source portraits mapped: {len(portraits)} art keys")

    if args.check:
        for name in sorted(portraits):
            print(f"  ECS-Portrait-{name:<24} <- {portraits[name].parent.name}/{portraits[name].name}")
        for name, (source_path, size) in sorted(UI_ART.items()):
            if not source_path.exists():
                raise SystemExit(f"character-select art not found: {source_path}")
            print(f"  {name:<38} <- {source_path.name} ({size[0]}x{size[1]})")
        return 0

    OUT_BLP.mkdir(parents=True, exist_ok=True)
    OUT_PNG.mkdir(parents=True, exist_ok=True)

    for name, path in sorted(portraits.items()):
        image = build_portrait(path)
        (OUT_BLP / f"ECS-Portrait-{name}.blp").write_bytes(encode_blp_bgra(image))
        image.save(OUT_PNG / f"ECS-Portrait-{name}.png")

    for name, (source_path, size) in sorted(UI_ART.items()):
        image = load_ui_art(source_path, size)
        (OUT_BLP / f"{name}.blp").write_bytes(encode_blp_bgra(image))
        image.save(OUT_PNG / f"{name}.png")

    dot = dot_texture()
    (OUT_BLP / "ECS-Note-Dot.blp").write_bytes(encode_blp_bgra(dot))
    dot.save(OUT_PNG / "ECS-Note-Dot.png")

    icon = search_icon_texture()
    (OUT_BLP / "ECS-Search-Icon.blp").write_bytes(encode_blp_bgra(icon))
    icon.save(OUT_PNG / "ECS-Search-Icon.png")

    # PRUNE anything this run did not produce. The previous generator derived from
    # the client plates and emitted art keys that no longer exist (the base
    # `DemonHunter` pair, whose client plates are blank); leaving them behind shipped
    # two dead textures and made the directory disagree with the sources. Pruning
    # keeps "what is on disk" and "what the mapping says" the same thing.
    keep = {f"ECS-Portrait-{name}.blp" for name in portraits}
    keep |= {f"{name}.blp" for name in UI_ART}
    keep |= {"ECS-Note-Dot.blp", "ECS-Search-Icon.blp"}
    for existing in sorted(OUT_BLP.glob("*.blp")):
        if existing.name not in keep:
            print(f"  pruning stale {existing.name}")
            existing.unlink()
    keep_png = {name[:-4] + ".png" for name in keep}
    for existing in sorted(OUT_PNG.glob("*.png")):
        if existing.name not in keep_png:
            print(f"  pruning stale {existing.name}")
            existing.unlink()

    blps = sorted(OUT_BLP.glob("*.blp"))
    total = sum(p.stat().st_size for p in blps)
    print(f"written: {len(blps)} BLPs, {total / 1024:.0f} KB total")
    print(f"source PNGs -> {OUT_PNG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
