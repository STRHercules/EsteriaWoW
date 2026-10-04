"""Resolve, extract and preview arbitrary textures from the client's load order."""

from __future__ import annotations

import ctypes as c
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools")))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image  # noqa: E402
from cars_mount_pack import Storm, FindData, DLL_DEFAULT  # noqa: E402
from blp import decode_blp, describe_blp  # noqa: E402
from resolve_glue import load_order, DATA  # noqa: E402

OUT = Path(__file__).resolve().parent / "extra_preview"


def list_safe(storm, archive) -> set[str]:
    data = FindData()
    finder = storm.dll.SFileFindFirstFile(archive, b"*", c.byref(data), None)
    if not finder:
        return set()
    out: set[str] = set()
    try:
        while True:
            out.add(data.cFileName.split(b"\0", 1)[0].decode("latin-1").casefold())
            if not storm.dll.SFileFindNextFile(finder, c.byref(data)):
                break
    finally:
        storm.dll.SFileFindClose(finder)
    return out


def main() -> int:
    targets = sys.argv[1:]
    storm = Storm(DLL_DEFAULT)
    available = []
    for rel in load_order():
        path = DATA / rel
        if not path.exists():
            continue
        try:
            handle = storm.open_archive(path)
        except OSError:
            continue
        try:
            names = list_safe(storm, handle)
        finally:
            storm.dll.SFileCloseArchive(handle)
        available.append((rel, names))

    OUT.mkdir(parents=True, exist_ok=True)
    for target in targets:
        key = target.casefold()
        # substring match so a path can be given without its extension
        holders = [
            rel
            for rel, names in available
            if any(key == n or key + ".blp" == n or key + ".tga" == n for n in names)
        ]
        if not holders:
            print(f"{target}: NOT FOUND in any archive")
            continue
        winner = holders[-1]
        handle = storm.open_archive(DATA / winner)
        try:
            actual = next(
                n
                for n in list(sorted(available_name for rel, names in available
                                     if rel == winner for available_name in names))
                if n.casefold() == key or n.casefold() in (key + ".blp", key + ".tga")
            )
            raw = storm.read(handle, actual)
        finally:
            storm.dll.SFileCloseArchive(handle)
        try:
            image = decode_blp(raw)
        except Exception as exc:
            print(f"{target}: decode failed {exc} ({describe_blp(raw)}) via {winner}")
            continue
        preview = image.convert("RGBA")
        if max(preview.size) > 1024:
            scale = 1024 / max(preview.size)
            preview = preview.resize(
                (max(1, int(preview.width * scale)), max(1, int(preview.height * scale))),
                Image.Resampling.LANCZOS,
            )
        safe = target.replace("\\", "_").replace("/", "_")
        preview.save(OUT / f"{safe}.png")
        print(
            f"{target}\n    winner={winner} {describe_blp(raw)} size={image.size} "
            f"-> {safe}.png"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
