"""Derive deterministic 64x64 BLP2 Glue portraits from race face textures."""

from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path

from PIL import Image


RACE_SOURCES = {
    "PandarenMale": Path("Pandaren/male/pandamalefacelower00_00.blp"),
    "PandarenFemale": Path("Pandaren/female/pandafemalefacelower00_00.blp"),
    "VulperaMale": Path("vulpera/male/vulperamalefacelower00_00.blp"),
    "VulperaFemale": Path("vulpera/female/vulperafemalefacelower00_00.blp"),
}

PORTRAIT_NAMES = tuple(f"UI-CharacterCreate-{key}.blp" for key in RACE_SOURCES)
CROP_BOX = (128, 0, 384, 224)
BLP_HEADER_SIZE = 148
BLP_PALETTE_SIZE = 1024
BLP_DATA_OFFSET = BLP_HEADER_SIZE + BLP_PALETTE_SIZE
PORTRAIT_SIZE = 64


def _read_blp2_header(data: bytes, path: Path) -> tuple[tuple[int, ...], tuple[int, ...]]:
    if data[:4] != b"BLP2":
        raise ValueError(f"{path}: expected BLP2 magic")
    if len(data) < BLP_DATA_OFFSET:
        raise ValueError(f"{path}: truncated BLP2 header")

    fields = struct.unpack("<4BII", data[8:20])
    offsets = struct.unpack("<16I", data[20:84])
    sizes = struct.unpack("<16I", data[84:148])
    return fields, (offsets, sizes)


def decode_source_face(path: Path) -> Image.Image:
    data = path.read_bytes()
    fields, (offsets, sizes) = _read_blp2_header(data, path)
    alpha_depth, alpha_encoding, has_mipmaps, blp_type, width, height = fields
    if (alpha_depth, alpha_encoding, has_mipmaps, blp_type) != (1, 8, 8, 1):
        raise ValueError(f"{path}: unsupported source BLP2 fields {fields[:4]}")
    if (width, height) != (512, 256):
        raise ValueError(f"{path}: expected 512x256 face texture, got {width}x{height}")
    if offsets[0] != BLP_DATA_OFFSET or sizes[0] != width * height * 2:
        raise ValueError(f"{path}: unexpected indexed BLP2 base layout")

    palette = data[BLP_HEADER_SIZE:BLP_DATA_OFFSET]
    base = data[offsets[0] : offsets[0] + sizes[0]]
    color_indices = base[: width * height]
    alpha = base[width * height :]
    if not any(alpha):
        raise ValueError(f"{path}: source alpha is empty")

    image = Image.frombytes("P", (width, height), color_indices)
    image.putpalette(palette, rawmode="BGRA")
    rgba = image.convert("RGBA")
    rgba.putalpha(Image.frombytes("L", (width, height), alpha))
    return rgba


def _bgra_mip_bytes(image: Image.Image, size: int) -> bytes:
    mip = image.resize((size, size), Image.Resampling.LANCZOS).convert("RGBA")
    return mip.tobytes("raw", "BGRA")


def encode_portrait(image: Image.Image, header_template: bytes) -> bytes:
    if len(header_template) < BLP_DATA_OFFSET:
        raise ValueError("portrait header template is truncated")
    if header_template[:4] != b"BLP2":
        raise ValueError("portrait header template is not BLP2")
    if header_template[8:12] != bytes((3, 8, 8, 1)):
        raise ValueError("portrait header template is not the expected raw BGRA BLP2 variant")
    if struct.unpack("<II", header_template[12:20]) != (PORTRAIT_SIZE, PORTRAIT_SIZE):
        raise ValueError("portrait header template is not 64x64")

    offsets = struct.unpack("<16I", header_template[20:84])
    sizes = struct.unpack("<16I", header_template[84:148])
    expected_sizes = tuple((max(1, PORTRAIT_SIZE >> mip)) ** 2 * 4 for mip in range(7))
    if tuple(sizes[:7]) != expected_sizes or offsets[0] != BLP_DATA_OFFSET:
        raise ValueError("portrait header template has an unexpected mip layout")

    output = bytearray(header_template[:BLP_DATA_OFFSET])
    for mip, size in enumerate(max(1, PORTRAIT_SIZE >> level) for level in range(7)):
        output.extend(_bgra_mip_bytes(image, size))
    if len(output) != BLP_DATA_OFFSET + sum(expected_sizes):
        raise AssertionError("encoded portrait length does not match its header")
    return bytes(output)


def validate_portrait(data: bytes, path: Path) -> None:
    fields, (offsets, sizes) = _read_blp2_header(data, path)
    alpha_depth, alpha_encoding, has_mipmaps, blp_type, width, height = fields
    if (alpha_depth, alpha_encoding, has_mipmaps, blp_type) != (3, 8, 8, 1):
        raise ValueError(f"{path}: output BLP2 fields do not match Ogre portrait headers")
    if (width, height) != (PORTRAIT_SIZE, PORTRAIT_SIZE):
        raise ValueError(f"{path}: output dimensions are not 64x64")
    if offsets[0] != BLP_DATA_OFFSET or sizes[0] != PORTRAIT_SIZE * PORTRAIT_SIZE * 4:
        raise ValueError(f"{path}: output base mip layout is invalid")

    base = data[offsets[0] : offsets[0] + sizes[0]]
    decoded = Image.frombytes("RGBA", (PORTRAIT_SIZE, PORTRAIT_SIZE), base, "raw", "BGRA")
    alpha = decoded.getchannel("A")
    if alpha.getextrema()[1] == 0:
        raise ValueError(f"{path}: output alpha is empty")
    if decoded.getbbox() is None:
        raise ValueError(f"{path}: output pixels are empty")


def derive_portraits(source_root: Path, output_dir: Path, header_template_path: Path) -> None:
    header_template = header_template_path.read_bytes()
    output_dir.mkdir(parents=True, exist_ok=True)

    for key, relative_source in RACE_SOURCES.items():
        source_path = source_root / relative_source
        image = decode_source_face(source_path)
        portrait = image.crop(CROP_BOX).resize((PORTRAIT_SIZE, PORTRAIT_SIZE), Image.Resampling.LANCZOS)
        encoded = encode_portrait(portrait, header_template)
        output_path = output_dir / f"UI-CharacterCreate-{key}.blp"
        output_path.write_bytes(encoded)
        validate_portrait(encoded, output_path)
        digest = hashlib.sha256(encoded).hexdigest()
        print(
            f"{key}: source={source_path} crop={CROP_BOX} output={output_path} "
            f"header=BLP2/raw-BGRA/64x64/mips=7 sha256={digest}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--header-template", type=Path, required=True)
    args = parser.parse_args()
    derive_portraits(args.source_root, args.output_dir, args.header_template)


if __name__ == "__main__":
    main()
