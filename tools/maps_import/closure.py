"""Dependency closure of ADT/WDT/M2/WMO files (3.3.5a formats)."""

from __future__ import annotations

import struct
from typing import Callable, Iterable


def chunks(data: bytes, start: int = 0):
    pos = start
    while pos + 8 <= len(data):
        tag = data[pos:pos + 4][::-1].decode("latin-1")  # chunks are stored reversed on disk
        size = struct.unpack_from("<I", data, pos + 4)[0]
        yield tag, pos + 8, size
        pos += 8 + size


def _strings(blob: bytes) -> list[str]:
    return [s.decode("latin-1") for s in blob.split(b"\0") if s]


def adt_refs(data: bytes) -> tuple[list[str], list[str], list[str]]:
    """(textures, m2 models, wmos) named by a monolithic 3.3.5 ADT."""
    tex: list[str] = []
    mdx: list[str] = []
    wmo: list[str] = []
    for tag, off, size in chunks(data):
        blob = data[off:off + size]
        if tag == "MTEX":
            tex = _strings(blob)
        elif tag == "MMDX":
            mdx = _strings(blob)
        elif tag == "MWMO":
            wmo = _strings(blob)
    return tex, mdx, wmo


def m2_refs(data: bytes) -> tuple[list[str], int]:
    """(texture paths with a fixed filename, M2 version). Skin files are derived by the caller."""
    if data[:4] != b"MD20":
        return [], 0
    version = struct.unpack_from("<I", data, 4)[0]
    n_tex, ofs_tex = struct.unpack_from("<II", data, 80)
    out = []
    for i in range(n_tex):
        t_type, _fl, n_len, n_ofs = struct.unpack_from("<IIII", data, ofs_tex + i * 16)
        if t_type == 0 and n_len > 1 and n_ofs + n_len <= len(data):
            out.append(data[n_ofs:n_ofs + n_len].split(b"\0", 1)[0].decode("latin-1"))
    return out, version


def m2_skins(path: str, data: bytes) -> list[str]:
    n_views = struct.unpack_from("<I", data, 68)[0]
    base = path.rsplit(".", 1)[0]
    return [f"{base}{i:02d}.skin" for i in range(n_views)]


def wmo_root_refs(data: bytes) -> tuple[list[str], list[str], int]:
    """(textures, doodad models, group count) of a WMO root file."""
    tex: list[str] = []
    doodads: list[str] = []
    groups = 0
    for tag, off, size in chunks(data):
        blob = data[off:off + size]
        if tag == "MOHD":
            groups = struct.unpack_from("<I", blob, 4)[0]
        elif tag == "MOTX":
            tex = _strings(blob)
        elif tag == "MODN":
            doodads = _strings(blob)
    return tex, doodads, groups


def wmo_group_textures(data: bytes) -> list[str]:
    return []  # group files reference materials by index into the root's MOTX


def compute(roots: Iterable[tuple[str, bytes]], read: Callable[[str], bytes | None], seed: Iterable[str] = ()) -> tuple[dict[str, bytes], set[str]]:
    """Walk from ADT bytes. Returns (path -> bytes for everything found, set of unresolved paths).

    `read` resolves a path to bytes from whichever source the caller prefers, or None when absent.
    """
    found: dict[str, bytes] = {}
    missing: set[str] = set()
    todo: list[str] = []
    seen: set[str] = set()

    def want(p: str) -> None:
        k = p.replace("/", "\\")
        if k.lower() in seen:
            return
        todo.append(k)

    for s in seed:
        want(s)
    for _name, data in roots:
        tex, mdx, wmo = adt_refs(data)
        for t in tex:
            want(t)
        for m in mdx:
            want(m.rsplit(".", 1)[0] + ".m2")
        for w in wmo:
            want(w)
    while todo:
        p = todo.pop()
        lk = p.lower()
        if lk in seen:
            continue
        seen.add(lk)
        blob = read(p)
        if blob is None:
            missing.add(p)
            continue
        found[p] = blob
        if lk.endswith(".m2"):
            texs, _v = m2_refs(blob)
            for t in texs:
                want(t)
            for s in m2_skins(p, blob):
                want(s)
        elif lk.endswith(".wmo"):
            base = lk.rsplit(".", 1)[0]
            tex, doodads, groups = wmo_root_refs(blob)
            if groups and not (base[-4:-3] == "_" and base[-3:].isdigit()):
                for t in tex:
                    want(t)
                for d in doodads:
                    want(d.rsplit(".", 1)[0] + ".m2")
                orig = p.rsplit(".", 1)[0]
                for g in range(groups):
                    want(f"{orig}_{g:03d}.wmo")
    return found, missing


def patch_adt_areas(data: bytes, fn) -> bytes:
    """Rewrite every MCNK area id through fn(old) -> new. MCNK header area id sits at +52."""
    b = bytearray(data)
    for tag, off, _size in chunks(data):
        if tag == "MCNK":
            old = struct.unpack_from("<I", b, off + 52)[0]
            struct.pack_into("<I", b, off + 52, fn(old))
    return bytes(b)


def adt_area_ids(data: bytes) -> set[int]:
    return {struct.unpack_from("<I", data, off + 52)[0] for tag, off, _s in chunks(data) if tag == "MCNK"}


def parse_trs(text: str) -> dict[str, str]:
    """md5translate.trs lines: 'Dir\mapX_Y.blp<TAB>file.blp' (plus 'dir: Name' headers). Returns key -> value."""
    out: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if "	" in line:
            k, v = line.split("	", 1)
            out[k] = v
    return out
