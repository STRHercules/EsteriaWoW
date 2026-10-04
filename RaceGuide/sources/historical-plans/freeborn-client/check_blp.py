"""Read-only sanity check for a hand-made BLP2 texture destined for the create screen.

Uses the project's own BLP2 reader (`tools/derive_playable_race_portraits.py`) rather than a
re-derived layout, so the check agrees with the code that already packs BLP2 files for this client.
A mis-encoded texture shows up as an invisible or black button, which is hard to tell apart from a
broken XML patch, so the header, the mip chain and the encoding are all checked before packing.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from derive_playable_race_portraits import (  # noqa: E402
    BLP_DATA_OFFSET,
    _read_blp2_header,
    _validate_mip_layout,
)

ENCODINGS = {1: "palettized (raw)", 2: "DXT (compressed)", 3: "BGRA (raw)"}


def main() -> int:
    path = Path(sys.argv[1])
    data = path.read_bytes()
    print(f"{path}  {len(data)} bytes")

    (encoding, alpha_depth, alpha_encoding, has_mips, width, height), (offsets, sizes) = _read_blp2_header(
        data, path)

    print(f"  size            {width}x{height}")
    print(f"  encoding        {encoding} ({ENCODINGS.get(encoding, 'unknown')})")
    print(f"  alpha           depth {alpha_depth}, encoding {alpha_encoding}")
    print(f"  hasMips         {has_mips}")
    print(f"  data offset     {BLP_DATA_OFFSET}")
    print(f"  mip sizes       {[size for size in sizes if size]}")

    problems = []
    if encoding not in ENCODINGS:
        problems.append(f"encoding {encoding} is not a BLP2 encoding this client uses")
    if width != height:
        problems.append(f"{width}x{height} is not square")
    if width < 32 or width > 256:
        problems.append(f"{width}px is outside the range the create-screen plates use")

    try:
        ranges = _validate_mip_layout(offsets, sizes, len(data))
        print(f"  mip ranges      {ranges}")
    except ValueError as error:
        problems.append(f"mip layout: {error}")

    for problem in problems:
        print(f"  FAIL {problem}")
    if problems:
        return 1

    print("  OK: usable BLP2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
