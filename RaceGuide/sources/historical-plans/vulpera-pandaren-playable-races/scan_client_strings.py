"""Find continuation-loading strings in the dev client binaries."""

from __future__ import annotations

from pathlib import Path

CLIENT = Path(__file__).resolve().parents[3] / "3.3.5a - Dev"
NEEDLES = (b"dbc1-", b"dbc-continuation", b"DBFilesClient", b"DBCFiles", b"continuation")


def printable(data: bytes) -> bool:
    return all(32 <= byte < 127 for byte in data)


def main() -> None:
    for name in ("Wow.exe", "WarcraftXL.dll", "Esteria.exe", "Client.dll"):
        path = CLIENT / name
        if not path.is_file():
            continue
        data = path.read_bytes()
        print(f"== {name} ({len(data)} bytes) ==")
        for needle in NEEDLES:
            start = 0
            found = []
            while len(found) < 4:
                index = data.find(needle, start)
                if index < 0:
                    break
                snippet = data[max(0, index - 40) : index + 60]
                if printable(snippet):
                    found.append(snippet.decode("ascii", "replace"))
                start = index + 1
            for snippet in found:
                print(f"  [{needle.decode()}] ...{snippet}...")


if __name__ == "__main__":
    main()
