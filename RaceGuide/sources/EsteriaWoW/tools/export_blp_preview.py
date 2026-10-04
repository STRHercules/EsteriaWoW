"""Export archive/source BLPs to PNG for visual comparison."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from PIL import Image

from cars_mount_pack import DLL_DEFAULT, Storm


def main() -> int:
    out = pathlib.Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    storm = Storm(DLL_DEFAULT)
    for spec in sys.argv[2:]:
        parts = spec.split("|")
        if len(parts) == 2:
            source, label = parts
            data = pathlib.Path(source).read_bytes()
        else:
            archive, entry, label = parts
            handle = storm.open_archive(pathlib.Path(archive))
            try:
                data = storm.read(handle, entry)
            finally:
                storm.dll.SFileCloseArchive(handle)
        target = out / f"{label}.png"
        import io
        import struct

        if data[:4] == b"BLP2" and data[8:12] == bytes((3, 8, 8, 1)):
            width, height = struct.unpack("<2I", data[12:20])
            offsets = struct.unpack("<16I", data[20:84])
            base = data[offsets[0] : offsets[0] + width * height * 4]
            image = Image.frombytes("RGBA", (width, height), base, "raw", "BGRA").convert("RGBA")
        else:
            image = Image.open(io.BytesIO(data)).convert("RGBA")
        if max(image.size) > 512:
            scale = 512 / max(image.size)
            image = image.resize(
                (max(1, int(image.width * scale)), max(1, int(image.height * scale))),
                Image.Resampling.NEAREST,
            )
        image.save(target)
        print(f"{label}: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
