"""Shared helpers for the standalone-map import (Risen Depths, Island-Project, Morza, SceneGaming).

Read-only against the live client, server and source packs; everything it writes goes to a stage folder.
"""

from __future__ import annotations

import ctypes as c
import hashlib
import shutil
import struct
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # Russian strings print on a cp1252 console
except Exception:  # noqa: BLE001
    pass

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "Tools"))
import cars_mount_pack as cmp  # noqa: E402  (reuses the project's StormLib wrapper)

STORM_DLL = Path(r"R:\Users\Zach\Documents\GitHub\wowdecomp\Tools\MountStudio\runtime\backend\StormLib.dll")
_storm: cmp.Storm | None = None


def storm() -> cmp.Storm:
    global _storm
    if _storm is None:
        _storm = cmp.Storm(STORM_DLL)
    return _storm


def norm(name: str) -> str:
    return name.replace("\\", "/").lower()


def winkey(name: str) -> str:
    return name.replace("/", "\\")


def list_archive(handle) -> list[tuple[str, int]]:
    """StormLib listing with a tolerant decode (some archives hold latin-1 names)."""
    s = storm()
    d = cmp.FindData()
    finder = s.dll.SFileFindFirstFile(handle, b"*", c.byref(d), None)
    out = []
    if not finder:
        return out
    while True:
        out.append((d.cFileName.split(b"\x00", 1)[0].decode("latin-1"), d.dwFileSize))
        if not s.dll.SFileFindNextFile(finder, c.byref(d)):
            break
    s.dll.SFileFindClose(finder)
    return out


def open_ro(path: Path):
    """Open an archive read-only with write-sharing, so it works while the game holds it open (no copies)."""
    s = storm()
    h = cmp.H()
    if not s.dll.SFileOpenArchive(str(path), 0, 0x300, c.byref(h)):
        raise OSError(f"SFileOpenArchive failed: {path} ({c.get_last_error()})")
    return h


def read_member(handle, name: str) -> bytes | None:
    try:
        return storm().read(handle, name)
    except OSError:
        return None


def sha(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


# --------------------------------------------------------------------------------------------- DBC

class Dbc:
    """Mutable WDBC table. String pool only grows, so existing offsets stay valid."""

    def __init__(self, data: bytes):
        magic, self.count, self.fields, self.rsize, ssize = struct.unpack_from("<4s4I", data)
        if magic != b"WDBC" or self.rsize != self.fields * 4:
            raise ValueError("unsupported WDBC layout")
        if len(data) != 20 + self.count * self.rsize + ssize:
            raise ValueError("bad WDBC size")
        self.rows = [list(struct.unpack_from(f"<{self.fields}I", data, 20 + i * self.rsize)) for i in range(self.count)]
        self.pool = bytearray(data[20 + self.count * self.rsize:])
        self._cache: dict[str, int] = {}

    def text(self, off: int) -> str:
        if not off:
            return ""
        end = self.pool.find(b"\0", off)
        return self.pool[off:end].decode("utf-8", "replace")

    def add_str(self, value: str) -> int:
        if not value:
            return 0
        if value in self._cache:
            return self._cache[value]
        off = len(self.pool)
        self.pool += value.encode("utf-8") + b"\0"
        self._cache[value] = off
        return off

    def ids(self) -> set[int]:
        return {r[0] for r in self.rows}

    def get(self, rid: int) -> list[int] | None:
        return next((r for r in self.rows if r[0] == rid), None)

    def to_bytes(self) -> bytes:
        body = b"".join(struct.pack(f"<{self.fields}I", *(v & 0xFFFFFFFF for v in r)) for r in self.rows)
        return struct.pack("<4s4I", b"WDBC", len(self.rows), self.fields, self.rsize, len(self.pool)) + body + bytes(self.pool)


def loc_texts(db: Dbc, row: list[int], start: int) -> list[str]:
    return [db.text(row[start + i]) for i in range(16)]


def best_loc(db: Dbc, row: list[int], start: int) -> str:
    texts = loc_texts(db, row, start)
    return next((t for t in texts if t), "")


def set_loc(db: Dbc, row: list[int], start: int, text: str, flags: int = 0xFFFFFFFF) -> None:
    for i in range(16):
        row[start + i] = 0
    row[start] = db.add_str(text)
    row[start + 16] = flags


def f2u(x: float) -> int:
    return struct.unpack("<I", struct.pack("<f", x))[0]


def u2f(x: int) -> float:
    return struct.unpack("<f", struct.pack("<I", x & 0xFFFFFFFF))[0]


def has_cyrillic(s: str) -> bool:
    return any("\u0400" <= ch <= "\u04ff" for ch in s)


# ---------------------------------------------------------------------------------- effective client

class ClientFiles:
    """Path -> bytes over the effective Esteria client archive set (later archive wins).

    Order is an assumption: Data root MPQs, then Data/enUS, each case-insensitively by name, with root
    custom archives after the base set. Used only for existence/dedupe checks, never to decide DBC
    winners (the DBC rebase step re-derives those at install time).
    """

    BASE = ["common", "common-2", "expansion", "lichking", "patch", "patch-2", "patch-3"]

    def __init__(self, data_dir: Path, scratch: Path):
        self.data_dir = data_dir
        self.scratch = scratch
        roots = {p.name.lower(): p for p in data_dir.glob("*.[mM][pP][qQ]")}
        locs = {p.name.lower(): p for p in (data_dir / "enUS").glob("*.[mM][pP][qQ]")}
        order: list[Path] = []
        for b in self.BASE:
            if f"{b}.mpq" in roots:
                order.append(roots.pop(f"{b}.mpq"))
        for k in sorted(locs):
            order.append(locs[k])
        for k in sorted(roots):
            order.append(roots[k])
        self.archives = order
        self.handles: list[tuple[Path, object]] = []
        self.index: dict[str, int] = {}
        self.names: dict[str, str] = {}

    def open(self) -> "ClientFiles":
        for p in self.archives:
            try:
                h = open_ro(p)
            except OSError:
                continue
            self.handles.append((p, h))
            idx = len(self.handles) - 1
            for n, _sz in list_archive(h):
                if n.startswith("("):
                    continue
                self.index[norm(n)] = idx
                self.names[norm(n)] = n
        return self

    def has(self, name: str) -> bool:
        return norm(name) in self.index

    def read(self, name: str) -> bytes | None:
        i = self.index.get(norm(name))
        if i is None:
            return None
        return read_member(self.handles[i][1], self.names[norm(name)])

    def provider(self, name: str) -> str | None:
        i = self.index.get(norm(name))
        return None if i is None else self.handles[i][0].name

    def probe(self, name: str) -> bool:
        """Existence test for files absent from listfiles: try every archive."""
        if self.has(name):
            return True
        key = winkey(name).encode("latin-1", "replace")
        s = storm()
        for _p, h in self.handles:
            fh = c.c_void_p()
            if s.dll.SFileOpenFileEx(h, key, 0, c.byref(fh)):
                s.dll.SFileCloseFile(fh)
                return True
        return False
