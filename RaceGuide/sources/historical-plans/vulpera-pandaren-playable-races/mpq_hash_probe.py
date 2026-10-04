"""Resolve MPQ contents by name hash.

Works on archives whose file names were stripped (hash-only) and on archives a
running game client holds open exclusively, because it reads the hash table
with plain file I/O instead of going through StormLib.
"""

from __future__ import annotations

import argparse
import glob
import mmap
import struct
from pathlib import Path

_CRYPT = [0] * 0x500
_seed = 0x00100001
for _i in range(0x100):
    for _j in range(5):
        _seed = (_seed * 125 + 3) % 0x2AAAAB
        _hi = (_seed & 0xFFFF) << 16
        _seed = (_seed * 125 + 3) % 0x2AAAAB
        _CRYPT[_i + _j * 0x100] = (_hi | (_seed & 0xFFFF)) & 0xFFFFFFFF


def hash_string(name: str, htype: int) -> int:
    seed1 = 0x7FED7FED
    seed2 = 0xEEEEEEEE
    for ch in name.upper().replace("/", "\\"):
        c = ord(ch)
        seed1 = (_CRYPT[htype + c] ^ ((seed1 + seed2) & 0xFFFFFFFF)) & 0xFFFFFFFF
        seed2 = (c + seed1 + seed2 + (seed2 << 5) + 3) & 0xFFFFFFFF
    return seed1


def decrypt_block(words: list[int], key: int) -> list[int]:
    """Undo MPQ block encryption (Blizzard's DecryptBlock)."""
    seed = 0xEEEEEEEE
    out = []
    for value in words:
        seed = (seed + _CRYPT[0x400 + (key & 0xFF)]) & 0xFFFFFFFF
        plain = (value ^ ((key + seed) & 0xFFFFFFFF)) & 0xFFFFFFFF
        key = ((((~key & 0xFFFFFFFF) << 0x15) + 0x11111111) | (key >> 0x0B)) & 0xFFFFFFFF
        seed = (plain + seed + (seed << 5) + 3) & 0xFFFFFFFF
        out.append(plain)
    return out


def _plausible(words: list[int], block_entries: int) -> float:
    """Fraction of named entries whose block index fits the block table."""
    named = 0
    good = 0
    for i in range(0, len(words), 4):
        index = words[i + 3]
        if index == 0xFFFFFFFF:
            continue
        named += 1
        if index < block_entries:
            good += 1
    return good / named if named else 0.0


def read_hash_map(path: Path) -> tuple[dict[int, int], dict[str, int]]:
    """Return {(hashA << 32) | hashB: entry_index} plus header diagnostics."""
    size = path.stat().st_size
    with open(path, "rb") as fh:
        with mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            ident, header_size, _arch32, version, _shift = struct.unpack_from("<4sIIHH", mm, 0)
            if ident != b"MPQ\x1a":
                raise ValueError(f"{path.name}: not an MPQ")
            h32, _b32, hsize, bsize = struct.unpack_from("<IIII", mm, 16)
            hpos = h32
            if header_size >= 44 and version >= 1:
                # v2 header: the high 16 bits of both table offsets live at 0x28/0x2A.
                hash_hi, _block_hi = struct.unpack_from("<HH", mm, 40)
                hpos |= hash_hi << 32
            if hsize == 0 or hpos + hsize * 16 > size:
                raise ValueError(f"{path.name}: unusable header (v{version} entries={hsize} pos={hpos})")
            blob = mm[hpos : hpos + hsize * 16]
    words = list(struct.unpack_from(f"<{hsize * 4}I", blob, 0))
    encrypted = _plausible(words, bsize) < 0.5
    if encrypted:
        words = decrypt_block(words, hash_string("(hash table)", 0x300))
    table: dict[int, int] = {}
    for i in range(hsize):
        base = i * 4
        if words[base + 3] == 0xFFFFFFFF:
            continue
        table[(words[base] << 32) | words[base + 1]] = i
    info = {
        "version": version,
        "entries": hsize,
        "block_entries": bsize,
        "hash_pos": hpos,
        "encrypted": encrypted,
    }
    return table, info


def lookup(table: dict[int, int], name: str) -> int | None:
    key = (hash_string(name, 0x100) << 32) | hash_string(name, 0x200)
    return table.get(key)


def load_lines(path: Path | None) -> list[str]:
    if path is None:
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    return [line.strip() for line in text.splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archives", required=True, help="glob for archives")
    parser.add_argument("--names-file", type=Path, help="file with one probe path per line")
    parser.add_argument("--listfile", type=Path, help="resolve every name in a listfile")
    parser.add_argument("--limit", type=int, default=40, help="max resolved listfile names to print")
    parser.add_argument("--grep", default="", help="only print listfile hits whose name matches")
    arguments = parser.parse_args()

    names = load_lines(arguments.names_file)
    listfile_names = load_lines(arguments.listfile)

    archives = [Path(path) for path in glob.glob(arguments.archives)]
    for archive in sorted(archives, key=lambda p: p.name.casefold()):
        try:
            table, info = read_hash_map(archive)
        except Exception as error:  # noqa: BLE001
            print(f"{archive.name}: {error}")
            continue
        hits = [name for name in names if lookup(table, name) is not None]
        resolved = 0
        samples: list[str] = []
        for name in listfile_names:
            if lookup(table, name) is None:
                continue
            resolved += 1
            if len(samples) < arguments.limit and (
                not arguments.grep or arguments.grep.casefold() in name.casefold()
            ):
                samples.append(name)
        print(
            f"{archive.name}: v{info['version']} entries={info['entries']} named={len(table)} "
            f"probe_hits={len(hits)} listfile_resolved={resolved}"
        )
        for name in hits:
            print(f"    HIT {name}")
        for name in samples:
            print(f"    list {name}")


if __name__ == "__main__":
    main()
