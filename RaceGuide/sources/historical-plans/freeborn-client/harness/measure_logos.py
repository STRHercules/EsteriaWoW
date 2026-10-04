"""Measure the visible (non-transparent) content of the character-select logos.

The Freeborn emblem is drawn into the same 60x60 slot the Alliance/Horde logos use, so if its
artwork fills the image while theirs has padding, it looks bigger. This reports each one's content
bounding box so the drawn size can match.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

CLIENT = Path(r"G:\3.3.5a - Dev")
LOGO_DIR = "Interface\\Glues\\CharacterSelect\\"
LOGOS = ("AllianceLogo.blp", "HordeLogo.blp", "FreebornLogo.blp")


def read_blp2_content(blob: bytes) -> tuple[int, int, int, int, int, int]:
    """(width, height, content_width, content_height, min_x, min_y) or zeros for no alpha."""
    width, height = struct.unpack_from("<II", blob, 12)
    alpha_off = struct.unpack_from("<I", blob, 24)[0]
    if alpha_off == 0 or width == 0 or height == 0:
        return width, height, width, height, 0, 0

    # BLP2 with alphaDepth 8 keeps a full-width alpha plane per mip.
    alpha = blob[alpha_off:alpha_off + width * height]
    if len(alpha) < width * height:
        return width, height, width, height, 0, 0

    min_x, min_y, max_x, max_y = width, height, -1, -1
    for i in range(width * height):
        if alpha[i] > 8:
            x, y = i % width, i // width
            min_x, max_x = min(min_x, x), max(max_x, x)
            min_y, max_y = min(min_y, y), max(max_y, y)
    if max_x < 0:
        return width, height, 0, 0, 0, 0
    return width, height, max_x - min_x + 1, max_y - min_y + 1, min_x, min_y


def main() -> int:
    archives = [CLIENT / "Data" / "patch-Z.MPQ"]
    archives += sorted((CLIENT / "Data").glob("*.MPQ"))
    archives += sorted((CLIENT / "Data" / "enUS").glob("*.MPQ"))

    storm = Storm(DLL_DEFAULT)
    for name in LOGOS:
        found = False
        for archive in archives:
            try:
                handle = storm.open_archive(archive)
            except OSError:
                continue
            try:
                blob = storm.read(handle, LOGO_DIR + name)
            except OSError:
                continue
            finally:
                storm.dll.SFileCloseArchive(handle)

            width, height, cw, ch, min_x, min_y = read_blp2_content(blob)
            scale = 60.0 / width
            print(f"  {name:20s} from {archive.name}")
            print(f"      image {width}x{height}  content {cw}x{ch} at ({min_x},{min_y})")
            if cw:
                print(f"      in a 60x60 slot the content is {cw * scale:.1f}x{ch * scale:.1f} px")
            found = True
            break
        if not found:
            print(f"  {name:20s} NOT FOUND in any archive")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
