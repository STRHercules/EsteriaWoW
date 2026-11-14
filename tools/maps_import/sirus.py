"""Read-only access to the local Sirus client (source of Risen Depths). Probe-based: no listfile needed."""

from __future__ import annotations

import ctypes as c
from pathlib import Path

import lib

SIRUS = Path(r"D:\Sirus\_client\World of Warcraft Sirus\Data")
BASE = ["common", "common-2", "expansion", "lichking", "patch", "patch-2", "patch-3"]


class Sirus:
    def __init__(self):
        roots = {p.name.lower(): p for p in SIRUS.glob("*.[mM][pP][qQ]")}
        locs = {p.name.lower(): p for p in (SIRUS / "ruRU").glob("*.[mM][pP][qQ]")}
        low = [roots.pop(f"{b}.mpq") for b in BASE if f"{b}.mpq" in roots]
        order = low + [locs[k] for k in sorted(locs)] + [roots[k] for k in sorted(roots)]
        self.order = order
        self.handles = []
        for p in order:
            try:
                self.handles.append((p, lib.open_ro(p)))
            except OSError:
                pass
        # highest priority first
        self.handles.reverse()

    def read(self, name: str) -> bytes | None:
        r = self.read_from(name)
        return None if r is None else r[1]

    def read_from(self, name: str):
        s = lib.storm()
        key = name.replace("/", "\\").encode("latin-1", "replace")
        for p, h in self.handles:
            fh = c.c_void_p()
            if s.dll.SFileOpenFileEx(h, key, 0, c.byref(fh)):
                try:
                    size = s.dll.SFileGetFileSize(fh, None)
                    buf = c.create_string_buffer(size or 1)
                    got = lib.cmp.U()
                    ok = s.dll.SFileReadFile(fh, buf, size, c.byref(got), None)
                finally:
                    s.dll.SFileCloseFile(fh)
                if ok and got.value == size:
                    return p.name, buf.raw[:size]
        return None

    def providers(self, name: str) -> list[str]:
        s = lib.storm()
        key = name.replace("/", "\\").encode("latin-1", "replace")
        out = []
        for p, h in self.handles:
            fh = c.c_void_p()
            if s.dll.SFileOpenFileEx(h, key, 0, c.byref(fh)):
                s.dll.SFileCloseFile(fh)
                out.append(p.name)
        return out
