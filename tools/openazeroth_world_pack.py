"""OpenAzeroth + five starting zones: inventory, staging and validation.

Implements the data route in
`.agents/plans/openazeroth-starting-zones/openazeroth-starting-zones.HANDOFF.md`.

Read-only unless a subcommand explicitly writes into the staging root. The
repository's existing StormLib binding (`cars_mount_pack.Storm`) and the client
archive resolver (`lib.clientfs.ClientFiles`) are reused; no new framework.
"""

from __future__ import annotations

import argparse
import ctypes as c
import hashlib
import json
import os
import re
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "modules" / "mod-classless-wildcard" / "client-patch"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from lib.clientfs import ClientFiles  # noqa: E402

CLIENT_DEFAULT = Path(r"G:\3.3.5a - Dev")
ZEPPELIN_ROOT = Path(r"G:\Downloads\Zeppelin\Data")
REFRORGED_ROOT = Path(
    r"G:\Downloads\HDWoWModels\Project Reforged\Custom_Starting_Zones_Isolated_2026-10-04"
)
SIRUS_ROOT = Path(r"D:\Sirus\_client\World of Warcraft Sirus\Risen_Depths_Extract_2026-10-04")
PLAN_ROOT = ROOT / ".agents" / "plans" / "openazeroth-starting-zones"
STAGING_ROOT = Path(r"C:\esteria-openazeroth")
LOCALE = "enUS"

# Named Zeppelin sources; hashes re-verified 2026-10-05.
SOURCE_ARCHIVES = {
    "O": (
        ZEPPELIN_ROOT / "PATCH-O.MPQ",
        "8b917b0f44cf986977f7562801512392d0c4587dd2565032ee9188cad514951d",
    ),
    "T": (
        ZEPPELIN_ROOT / "PATCH-T.MPQ",
        "f6775358a20d2b6b5928a6b233d544463ddba0049ff21c79dc066fe5bbf8ed33",
    ),
    "Z": (
        ZEPPELIN_ROOT / "PATCH-Z.MPQ",
        "bc440b5100b66bcf2781cfcbf6b21252c5fdf500e23c50024911c89724f1dbef",
    ),
}

# Maps in scope. The handoff proposed eight; Deepholm and the four donor
# race-start maps were dropped on 2026-10-05, leaving the two continents plus
# OpenAzeroth's Heart of Azeroth.
TERRAIN_MAPS = {
    0: ("Azeroth", "O"),
    1: ("Kalimdor", "O"),
    1469: ("MaelstromShaman", "O"),
}
OMITTED_TERRAIN = {
    646: ("Deephome", "omitted: 6,641 MCNK chunks use an alpha encoding the WotLK extractor cannot read"),
    815: ("Giln", "omitted: Reforged Worgen start dropped"),
    1773: ("custom_troll", "omitted: Reforged Troll start dropped"),
    1775: ("custom_tuskarr", "omitted: Reforged Tuskarr start dropped"),
    10001: ("Sirus2", "omitted: Sirus Naga start dropped"),
}


def retained_azeroth_tiles() -> set[tuple[int, int]]:
    """The 66 Esteria Azeroth tiles OpenAzeroth omits and the merge must keep."""

    tiles = {(x, y) for x in range(3, 10) for y in range(54, 61)}
    tiles |= {(x, 60) for x in range(10, 27)}
    return tiles


class AdtError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def fcc(data: bytes, offset: int) -> bytes:
    return data[offset : offset + 4]


def cid(name: str) -> bytes:
    """WoW stores ADT/WDT/WMO chunk ids byte-reversed ("MVER" -> "REVM").

    The repository extractor encodes the same quirk, e.g.
    MPHDMagic = { {"D", "H", "P", "M"} } in src/tools/map_extractor/wdt.cpp.
    """

    return name.encode("ascii")[::-1]

# --------------------------------------------------------------------------- MPQ


@dataclass
class Archive:
    """One opened MPQ with a lazily built entry table."""

    key: str
    path: Path
    storm: Storm
    handle: int = 0
    _entries: dict[str, tuple[int, int, int]] | None = field(default=None, repr=False)

    def open(self, read_only: bool = True) -> None:
        if self.handle:
            return
        handle = c.c_void_p()
        flags = 0x00000100 if read_only else 0  # MPQ_OPEN_READ_ONLY
        if not self.storm.dll.SFileOpenArchive(str(self.path), 0, flags, c.byref(handle)):
            raise OSError(f"SFileOpenArchive failed: {self.path} ({c.get_last_error()})")
        self.handle = handle

    @property
    def entries(self) -> dict[str, tuple[int, int, int]]:
        if self._entries is None:
            if not self.handle:
                self.open()
            self._entries = {
                name: (size, comp, flags)
                for name, size, comp, flags in self.storm.list_files(self.handle)
            }
        return self._entries

    def read(self, name: str) -> bytes:
        if not self.handle:
            self.open()
        return self.storm.read(self.handle, name)

    def close(self) -> None:
        if self.handle:
            self.storm.dll.SFileCloseArchive(self.handle)
            self.handle = 0


# --------------------------------------------------------------------------- ADT/WDT


def _mcnk_offsets(data: bytes, mcin_off: int) -> tuple[int, int]:
    """Resolve the MCIN cell table and the base its MCNK offsets are relative to."""

    cells = mcin_off + 8
    for index in range(256):
        raw = u32(data, cells + index * 16)
        if not raw:
            continue
        for base in (0, mcin_off, mcin_off + 8):
            if 0 <= raw + base <= len(data) - 4 and fcc(data, raw + base) == cid("MCNK"):
                return cells, base
        raise AdtError(f"MCIN cell {index} offset {raw} does not land on MCNK")
    raise AdtError("MCIN has no populated cells")


def parse_adt(data: bytes, deep: bool = False) -> dict:
    """Parse a combined (MVER 18) ADT; raises AdtError on the split T format."""

    if fcc(data, 0) != cid("MVER"):
        raise AdtError("missing MVER")
    if fcc(data, 12) != cid("MHDR"):
        raise AdtError("missing MHDR (split-ADT format?)")
    version = u32(data, 8)
    base = 20  # MHDR data start; MHDR offsets are relative to it.
    mcin_off = base + u32(data, base + 4)
    if fcc(data, mcin_off) != cid("MCIN"):
        raise AdtError("MHDR MCIN offset does not land on MCIN")
    cells, mnk_base = _mcnk_offsets(data, mcin_off)
    result = {"version": version, "mhdr_flags": u32(data, base), "chunks": []}
    if not deep:
        return result
    for index in range(256):
        raw = u32(data, cells + index * 16)
        if not raw:
            continue
        at = raw + mnk_base
        layers = u32(data, at + 20)
        chunk = {
            "ix": u32(data, at + 12),
            "iy": u32(data, at + 16),
            "layers": layers,
            "area": u32(data, at + 60),
            "size_mcal": u32(data, at + 48),
        }
        if layers > 1 and chunk["size_mcal"] > 8:
            block = (chunk["size_mcal"] - 8) // (layers - 1)
            chunk["alpha_block"] = block
            chunk["alpha_format"] = {2048: "small", 4096: "big"}.get(block, f"unknown:{block}")
        else:
            chunk["alpha_block"] = 0
            chunk["alpha_format"] = "none"
        result["chunks"].append(chunk)
    return result


def parse_wdt(data: bytes) -> dict:
    if fcc(data, 0) != cid("MVER"):
        raise AdtError("missing MVER in WDT")
    if fcc(data, 12) != cid("MPHD"):
        raise AdtError("missing MPHD in WDT")
    mphd_size = u32(data, 16)
    mphd = [u32(data, 20 + 4 * i) for i in range(mphd_size // 4)]
    main_off = 20 + mphd_size
    if fcc(data, main_off) != cid("MAIN"):
        raise AdtError("missing MAIN in WDT")
    body = main_off + 8
    active = []
    for y in range(64):
        for x in range(64):
            entry = body + (y * 64 + x) * 8
            if entry + 8 > len(data):
                break
            if u32(data, entry):
                active.append((x, y))
    return {"mphd": mphd, "active": active}


def parse_tile_name(name: str) -> tuple[str, int, int] | None:
    """Return (map_dir, x, y) for a combined ADT key, else None."""

    lowered = name.lower()
    parts = lowered.split("\\")
    if len(parts) < 3 or parts[0] != "world" or parts[1] != "maps" or not lowered.endswith(".adt"):
        return None
    pieces = parts[-1][:-4].rsplit("_", 2)
    if len(pieces) != 3:
        return None
    try:
        return parts[2], int(pieces[1]), int(pieces[2])
    except ValueError:
        return None


def terrain_key(map_dir: str, x: int, y: int) -> str:
    return f"World\\Maps\\{map_dir}\\{map_dir}_{x}_{y}.adt"


def wdt_key(map_dir: str) -> str:
    return f"World\\Maps\\{map_dir}\\{map_dir}.wdt"


def wdl_key(map_dir: str) -> str:
    return f"World\\Maps\\{map_dir}\\{map_dir}.wdl"


def classify(entries: dict[str, tuple[int, int, int]]) -> dict:
    out = {"total": len(entries), "terrain": {}, "dbc": [], "assets": {}}
    suffixes = {".m2": "m2", ".skin": "skin", ".blp": "blp", ".wmo": "wmo"}
    for name in entries:
        lowered = name.lower()
        parsed = parse_tile_name(name)
        if parsed:
            out["terrain"][parsed[0]] = out["terrain"].get(parsed[0], 0) + 1
        elif lowered.startswith("dbfilesclient\\") and lowered.endswith(".dbc"):
            out["dbc"].append(name.split("\\")[-1])
        suffix = "." + lowered.rsplit(".", 1)[-1]
        if suffix in suffixes:
            out["assets"][suffixes[suffix]] = out["assets"].get(suffixes[suffix], 0) + 1
    out["dbc"].sort()
    return out

class DirSource:
    """A harvested extraction tree (Reforged/Sirus) indexed by WoW-style key."""

    def __init__(self, key: str, root: Path):
        self.key = key
        self.root = root
        self._paths: dict[str, tuple[str, Path]] = {}
        self.duplicates = 0
        if not root.is_dir():
            return
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            lowers = [part.lower() for part in path.parts]
            if "maps" not in lowers:
                continue
            index = len(lowers) - 1 - lowers[::-1].index("maps")
            if index < 1 or lowers[index - 1] != "world":
                continue
            rel = "\\".join(path.parts[index + 1 :])
            name = "World\\Maps\\" + rel
            folded = name.lower()
            if folded in self._paths:
                self.duplicates += 1
                continue
            self._paths[folded] = (name, path)

    @property
    def entries(self) -> dict[str, tuple[int, int, int]]:
        return {name: (path.stat().st_size, 0, 0) for name, path in self._paths.values()}

    def read(self, name: str) -> bytes:
        entry = self._paths.get(name.lower())
        if entry is None:
            raise FileNotFoundError(name)
        return entry[1].read_bytes()

    def close(self) -> None:
        return None

# --------------------------------------------------------------------------- Commands


def command_inventory(args: argparse.Namespace) -> dict:
    storm = Storm(args.dll)
    result = {"client": str(args.client), "sources": {}}
    for key, (path, expected) in SOURCE_ARCHIVES.items():
        if not path.is_file():
            result["sources"][key] = {"path": str(path), "missing": True}
            continue
        actual = sha256_file(path)
        archive = Archive(key, path, storm)
        archive.open()
        try:
            summary = classify(archive.entries)
        finally:
            archive.close()
        summary.update(
            {
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": actual,
                "sha256_expected": expected,
                "sha256_match": actual == expected,
            }
        )
        result["sources"][key] = summary
    for key, root in (("REFRORGED", REFRORGED_ROOT), ("SIRUS", SIRUS_ROOT)):
        result["sources"][key] = {"path": str(root), "exists": root.is_dir()}
    return result


def command_terrain(args: argparse.Namespace) -> dict:
    storm = Storm(args.dll)
    sources: dict[str, object] = {
        key: Archive(key, path, storm) for key, (path, _) in SOURCE_ARCHIVES.items()
    }
    dir_roots = {"REFRORGED": REFRORGED_ROOT, "SIRUS": SIRUS_ROOT}
    for key in sorted({src for _, src in TERRAIN_MAPS.values()} & set(dir_roots)):
        sources[key] = DirSource(key, dir_roots[key])
    result = {"maps": {}, "retained_azeroth": sorted(retained_azeroth_tiles())}
    try:
        for map_id, (map_dir, source) in TERRAIN_MAPS.items():
            src = sources[source]
            entry: dict = {"map_id": map_id, "dir": map_dir, "source": source, "wdt": None, "wdl": False}
            lookup = {name.lower(): name for name in src.entries}
            key = wdt_key(map_dir).lower()
            if key in lookup:
                wdt = parse_wdt(src.read(lookup[key]))
                xs = [x for x, _ in wdt["active"]]
                ys = [y for _, y in wdt["active"]]
                entry["wdt"] = {
                    "mphd": wdt["mphd"],
                    "mphd_flags": wdt["mphd"][0] if wdt["mphd"] else None,
                    "active": len(wdt["active"]),
                    "bounds": [min(xs), max(xs), min(ys), max(ys)] if xs else None,
                }
            entry["wdl"] = wdl_key(map_dir).lower() in lookup
            entry["adt_tiles"] = sorted(
                (x, y)
                for name in src.entries
                if (parsed := parse_tile_name(name)) and parsed[0] == map_dir.lower()
                for x, y in [(parsed[1], parsed[2])]
            )
            entry["adt_count"] = len(entry["adt_tiles"])
            if isinstance(src, DirSource):
                entry["duplicate_versions"] = src.duplicates
            result["maps"][str(map_id)] = entry
        azeroth = result["maps"].get("0", {})
        if azeroth.get("adt_count"):
            present = {(x, y) for x, y in azeroth["adt_tiles"]}
            retained = retained_azeroth_tiles()
            result["azeroth_retention"] = {
                "retained_absent_from_donor": sorted(retained - present),
                "retained_present_in_donor": sorted(retained & present),
            }
    finally:
        for src in sources.values():
            src.close()
    return result

def command_alpha(args: argparse.Namespace) -> dict:
    """Alpha block format for the retained Azeroth tiles (section 6 conversion)."""

    client = _client_files(args.client / "Data")
    report: dict = {"formats": {}, "layers": {}, "chunks": 0, "absent": [], "unknown_tiles": {}, "archive": {}}
    try:
        for x, y in sorted(retained_azeroth_tiles()):
            key = terrain_key("Azeroth", x, y)
            try:
                payload, archive_path = client.find(key)
            except FileNotFoundError:
                report["absent"].append([x, y])
                continue
            report["archive"][Path(archive_path).name] = report["archive"].get(Path(archive_path).name, 0) + 1
            parsed = parse_adt(payload, deep=True)
            for chunk in parsed["chunks"]:
                fmt = chunk["alpha_format"].split(":")[0]
                report["formats"][fmt] = report["formats"].get(fmt, 0) + 1
                report["layers"][chunk["layers"]] = report["layers"].get(chunk["layers"], 0) + 1
                if fmt == "unknown":
                    report["unknown_tiles"].setdefault(chunk["alpha_format"], []).append([x, y])
                report["chunks"] += 1
    finally:
        client.close()
    return report


SAMPLE_TRS = (b"dir: Azeroth\r\nAzeroth\\map30_48.blp\tdeadbeef.blp\r\n"
              b"dir: Kalimdor\r\nKalimdor\\map00_00.blp\t56c593320dbef597058dc1a8082b754b.blp\r\n")


def command_selftest(args: argparse.Namespace) -> dict:
    """Smallest thing that fails if the retention rule or ADT parser break."""

    tiles = retained_azeroth_tiles()
    assert len(tiles) == 66, len(tiles)
    assert {(x, y) for x in range(3, 10) for y in range(54, 61)} <= tiles
    assert (26, 60) in tiles and (10, 60) in tiles
    assert (2, 60) not in tiles and (3, 61) not in tiles and (27, 60) not in tiles
    assert parse_tile_name("World\\Maps\\Azeroth\\Azeroth_30_47.adt") == ("azeroth", 30, 47)
    assert parse_tile_name("World\\Maps\\LostIsles\\LostIsles_47_25_obj0.adt") is None
    assert parse_tile_name("World\\Maps\\LostIsles\\LostIsles_47_25.adt") == ("lostisles", 47, 25)

    storm = Storm(args.dll)
    o_archive = Archive("O", SOURCE_ARCHIVES["O"][0], storm)
    o_archive.open()
    try:
        combined = parse_adt(o_archive.read("World\\Maps\\Azeroth\\Azeroth_30_47.adt"), deep=True)
    finally:
        o_archive.close()
    assert combined["version"] == 18, combined["version"]
    assert len(combined["chunks"]) == 256, len(combined["chunks"])

    archive = Archive("T", SOURCE_ARCHIVES["T"][0], storm)
    archive.open()
    try:
        name = next(
            n for n in archive.entries
            if (parsed := parse_tile_name(n)) and parsed[0] == "lostisles"
        )
        try:
            parse_adt(archive.read(name))
        except AdtError:
            split_rejected = True
        else:
            split_rejected = False
    finally:
        archive.close()
    assert split_rejected, "split T ADT parsed as combined"

    # Minimap helpers: the trs rewrite has to be byte-exact, and the zone rect
    # has to land on the same tiles the archive names use.
    sample = _trs_bytes(_trs_sections(SAMPLE_TRS))
    assert sample == SAMPLE_TRS, sample
    gilneas = _tiles_for_rect((3439.583251953125, 293.75, -533.3333129882812, -2631.25))
    assert gilneas == {(a, b) for a in range(25, 32) for b in range(33, 37)}, sorted(gilneas)
    assert (26, 33) in gilneas and (33, 25) not in gilneas and (31, 37) not in gilneas
    lost = _tiles_for_rect((-8416.6689453125, -12931.2490234375, 2347.916748046875, -662.5003051757812))
    assert lost == {(a, b) for a in range(47, 57) for b in range(27, 34)}, sorted(lost)
    kezan = _tiles_for_rect((-10670.8330078125, -12022.916015625, -8264.5830078125, -9164.5830078125))
    assert kezan == {(a, b) for a in range(52, 55) for b in range(47, 50)}, sorted(kezan)
    return {"retained_tiles": len(tiles), "split_format_rejected": True,
            "minimap_round_trip": True, "gilneas_tiles": len(gilneas)}


# ------------------------------------------------------------------ terrain build

ALPHA_SMALL_BLOCK = 2048
ALPHA_BIG_BLOCK = 4096
# Calibration knob. The client expands one small-alpha byte into two pixels; this
# names which nibble is the first (even-indexed) pixel. Both orders were measured
# on the retained tiles (see stage report); the smoother one is used.
SMALL_ALPHA_LOW_NIBBLE_FIRST = True

MCNK_FIELD_OFFSETS = {
    "offsMCVT": 28,
    "offsMCNR": 32,
    "offsMCLY": 36,
    "offsMCRF": 40,
    "offsMCAL": 44,
    "sizeMCAL": 48,
    "offsMCSH": 52,
    "sizeMCSH": 56,
    "offsMCSE": 96,
    "offsMCLQ": 104,
    "offsMCCV": 124,
}
MCNK_MOVING_FIELDS = ("offsMCVT", "offsMCNR", "offsMCLY", "offsMCRF", "offsMCAL",
                      "offsMCSH", "offsMCSE", "offsMCLQ", "offsMCCV")


def expand_alpha_block(block: bytes, low_first: bool = SMALL_ALPHA_LOW_NIBBLE_FIRST) -> bytes:
    """Expand one 2048-byte 4-bit alpha block to the native 4096-byte 8-bit form."""

    if len(block) != ALPHA_SMALL_BLOCK:
        raise AdtError(f"small alpha block must be {ALPHA_SMALL_BLOCK} bytes, got {len(block)}")
    out = bytearray(ALPHA_BIG_BLOCK)
    for index, byte in enumerate(block):
        low = (byte & 0x0F) * 17
        high = (byte >> 4) * 17
        if low_first:
            out[2 * index] = low
            out[2 * index + 1] = high
        else:
            out[2 * index] = high
            out[2 * index + 1] = low
    return bytes(out)


def convert_adt_small_to_big(data: bytes, low_first: bool = SMALL_ALPHA_LOW_NIBBLE_FIRST) -> tuple[bytes, dict]:
    """Rewrite a combined ADT so every MCAL uses the 8-bit big-alpha layout."""

    if fcc(data, 0) != cid("MVER") or u32(data, 8) != 18:
        raise AdtError("expected a combined MVER 18 ADT")
    base = 20
    mcin_off = base + u32(data, base + 4)
    if fcc(data, mcin_off) != cid("MCIN"):
        raise AdtError("MHDR MCIN offset does not land on MCIN")
    cells, mnk_base = _mcnk_offsets(data, mcin_off)
    entries = []
    for index in range(256):
        raw = u32(data, cells + index * 16)
        if raw:
            entries.append((index, raw, raw + mnk_base))
    if not entries:
        raise AdtError("ADT has no MCNK chunks")
    first = min(at for _, _, at in entries)
    for slot in range(2, 12):
        if base + u32(data, base + 4 * slot) >= first and u32(data, base + 4 * slot):
            raise AdtError("MHDR chunk extends into the MCNK region")

    out = bytearray(data[:first])
    new_cells = bytearray(data[cells : cells + 256 * 16])
    stats = {"chunks": 0, "converted": 0, "layers": 0, "delta": 0}
    for index, raw, at in entries:
        chunk_size = u32(data, at + 4)
        chunk_end = at + 8 + chunk_size
        size_mcal = u32(data, at + 48)
        offs_mcal = u32(data, at + 44)
        if size_mcal <= 8 or not offs_mcal:
            new_at = len(out)
            out += data[at:chunk_end]
            new_size = chunk_size
        else:
            layers = (size_mcal - 8) // ALPHA_SMALL_BLOCK
            if layers < 1 or size_mcal != 8 + layers * ALPHA_SMALL_BLOCK:
                raise AdtError(f"unexpected MCAL size {size_mcal}")
            mcal_at = at + offs_mcal
            if fcc(data, mcal_at) != cid("MCAL") or u32(data, mcal_at + 4) != layers * ALPHA_SMALL_BLOCK:
                raise AdtError("MCAL header does not match the MCNK alpha size")
            old = data[mcal_at + 8 : mcal_at + 8 + layers * ALPHA_SMALL_BLOCK]
            new = b"".join(
                expand_alpha_block(old[i * ALPHA_SMALL_BLOCK : (i + 1) * ALPHA_SMALL_BLOCK], low_first)
                for i in range(layers)
            )
            delta = len(new) - len(old)
            body = bytearray(data[at + 8 : chunk_end])
            cut = offs_mcal - 8
            body = (
                body[:cut]
                + bytearray(cid("MCAL"))
                + struct.pack("<I", layers * ALPHA_BIG_BLOCK)
                + bytearray(new)
                + body[cut + 8 + len(old) :]
            )
            struct.pack_into("<I", body, MCNK_FIELD_OFFSETS["sizeMCAL"] - 8, 8 + layers * ALPHA_BIG_BLOCK)
            for name in MCNK_MOVING_FIELDS:
                pos = MCNK_FIELD_OFFSETS[name] - 8
                value = struct.unpack_from("<I", body, pos)[0]
                if value > offs_mcal:
                    struct.pack_into("<I", body, pos, value + delta)
            new_at = len(out)
            out += cid("MCNK") + struct.pack("<I", len(body)) + bytes(body)
            new_size = len(body)
            stats["converted"] += 1
            stats["layers"] += layers
            stats["delta"] += delta
        struct.pack_into("<II", new_cells, index * 16, new_at - mnk_base, 8 + new_size)
        stats["chunks"] += 1
    out[cells : cells + 256 * 16] = new_cells
    return bytes(out), stats


def merge_wdt_main(base: bytes, extra_tiles) -> tuple[bytes, list]:
    """Activate `extra_tiles` in a WDT's MAIN table, preserving every other entry."""

    wdt = parse_wdt(base)
    body = 20 + len(wdt["mphd"]) * 4 + 8
    out = bytearray(base)
    added = []
    for x, y in extra_tiles:
        pos = body + (y * 64 + x) * 8
        if not u32(out, pos):
            struct.pack_into("<I", out, pos, 1)
            added.append((x, y))
    return bytes(out), sorted(added)


def parse_wdl(data: bytes) -> dict:
    """Return the MAOF table and the byte range each populated WDL tile occupies."""

    off = 0
    while off + 8 <= len(data):
        size = u32(data, off + 4)
        if fcc(data, off) == cid("MAOF"):
            values = list(struct.unpack_from(f"<{size // 4}I", data, off + 8))
            starts = sorted({v for v in values if v})
            spans = {}
            for position, start in enumerate(starts):
                end = starts[position + 1] if position + 1 < len(starts) else len(data)
                spans[start] = end - start
            return {"maof_offset": off + 8, "values": values, "spans": spans}
        off += 8 + size
    raise AdtError("WDL has no MAOF chunk")


def merge_wdl(donor: bytes, client: bytes, tiles) -> tuple[bytes, list]:
    """Copy client low-res tile blobs into the donor WDL where the donor is empty."""

    donor_wdl = parse_wdl(donor)
    client_wdl = parse_wdl(client)
    out = bytearray(donor)
    taken = []
    for x, y in tiles:
        index = y * 64 + x
        if donor_wdl["values"][index] or not client_wdl["values"][index]:
            continue
        start = client_wdl["values"][index]
        blob = client[start : start + client_wdl["spans"][start]]
        new_start = len(out)
        out += blob
        struct.pack_into("<I", out, donor_wdl["maof_offset"] + index * 4, new_start)
        taken.append((x, y))
    return bytes(out), sorted(taken)

CLIENT_DBC_BASELINES = ("Map", "AreaTable", "WorldMapArea", "WorldMapOverlay")
SERVER_AREATABLE = ROOT / "modules" / "mod-fly-anywhere" / "data" / "patch" / "server" / "AreaTable.dbc"

# World map entries the client has no row for. Each one is a zone that now exists
# on a map the client already has (0 Azeroth, 1 Kalimdor) whose root row 14/13 is
# byte-identical to the donor's, so the donor rects, parents and overlay rows drop
# in unmodified. 611 (GilneasCity) has no overlay rows of its own; its base art is
# Interface\WorldMap\GilneasCity\GilneasCity1..12.
WORLD_MAP_ZONES = {539: "Gilneas", 544: "TheLostIsles", 605: "Kezan", 611: "GilneasCity"}
MINIMAP_TRS = "Textures\\Minimap\\md5translate.trs"
MINIMAP_TILE_SPAN = 533.33333

# Section 4/10/11 ID reservations, checked free against client + server + live SQL on 2026-10-05.
RESERVED_MAPS = {
    1469: {"dir": "MaelstromShaman", "instance": 0, "area": None, "expansion": 0, "source": "O"},
}
# Heart of Azeroth's area set is selected from the scoped terrain, so nothing is
# reserved by number yet. The dropped maps' reservations (Giln 5179-5209 and the
# borrowed 51000-51007, Sirus 10004-10465, Troll 50506, Tuskarr 11435) are no
# longer allocated.
RESERVED_AREAS: list = []
AREA_BIT_CEILING = 4096
AREA_BIT_FLOOR = 3618


def _scope_maps(spec: str) -> list:
    """Resolve a --maps argument, rejecting anything the scope dropped."""

    wanted = [int(part) for part in spec.split(",") if part.strip()] if spec else sorted(TERRAIN_MAPS)
    out_of_scope = [m for m in wanted if m not in TERRAIN_MAPS]
    if out_of_scope:
        detail = "; ".join(
            f"{m} {OMITTED_TERRAIN[m][0]}: {OMITTED_TERRAIN[m][1]}"
            if m in OMITTED_TERRAIN
            else f"{m}: unknown map id"
            for m in out_of_scope
        )
        raise SystemExit(f"requested maps are not in scope: {detail}")
    return wanted


STAGE_TERRAIN = STAGING_ROOT / "terrain"


def verify_adt(data: bytes) -> list:
    """Structural self-check for a combined ADT; returns a list of problems."""

    problems = []
    base = 20
    mcin_off = base + u32(data, base + 4)
    if fcc(data, mcin_off) != cid("MCIN"):
        return ["MHDR MCIN offset does not land on MCIN"]
    try:
        cells, mnk_base = _mcnk_offsets(data, mcin_off)
    except AdtError as exc:
        return [str(exc)]
    spans = []
    for index in range(256):
        raw = u32(data, cells + index * 16)
        declared = u32(data, cells + index * 16 + 4)
        if not raw:
            continue
        at = raw + mnk_base
        if at + 8 > len(data):
            problems.append(f"cell {index} offset past end of file")
            continue
        chunk_size = u32(data, at + 4)
        if declared != 8 + chunk_size:
            problems.append(f"cell {index} MCIN size {declared} != 8+{chunk_size}")
        end = at + 8 + chunk_size
        if end > len(data):
            problems.append(f"cell {index} chunk past end of file")
            continue
        spans.append((at, end))
        for name in MCNK_MOVING_FIELDS:
            value = u32(data, at + MCNK_FIELD_OFFSETS[name])
            if value and value >= chunk_size + 8:
                problems.append(f"cell {index} {name}={value} outside the chunk")
        size_mcal = u32(data, at + 48)
        offs_mcal = u32(data, at + 44)
        if size_mcal > 8:
            if offs_mcal + size_mcal > chunk_size + 8:
                problems.append(f"cell {index} MCAL overruns the chunk")
            elif fcc(data, at + offs_mcal) != cid("MCAL"):
                problems.append(f"cell {index} offsMCAL does not land on MCAL")
    if spans != sorted(spans):
        problems.append("MCNK chunks are not in ascending file order")
    for (_, first_end), (second_start, _) in zip(spans, spans[1:]):
        if first_end != second_start:
            problems.append(f"MCNK chunks are not contiguous at {first_end}")
            break
    return problems


def _stage_write(rel: str, payload: bytes, entry: dict) -> None:
    target = STAGE_TERRAIN / Path(rel.replace("\\", "/"))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    entry["written"] += 1
    entry["bytes"] += len(payload)


def command_stage(args: argparse.Namespace) -> dict:
    """Write staged terrain for the OpenAzeroth maps (0, 1, 646, 1469 by default)."""

    wanted = _scope_maps(args.maps)
    storm = Storm(args.dll)
    o = Archive("O", SOURCE_ARCHIVES["O"][0], storm)
    z = Archive("Z", SOURCE_ARCHIVES["Z"][0], storm)
    o.open()
    z.open()
    client = _client_files(args.client / "Data")
    report = {"staging_root": str(STAGE_TERRAIN), "maps": {}, "retained_azeroth": {"converted": 0}}
    try:
        for map_id in wanted:
            map_dir, source = TERRAIN_MAPS[map_id]
            if source != "O":
                raise SystemExit(
                    f"map {map_id} ({map_dir}) is not an OpenAzeroth map; resolve source versions first"
                )
            entry = {"dir": map_dir, "source": source, "written": 0, "bytes": 0,
                     "adts": 0, "converted": 0, "layers": 0, "wdt_activated": 0, "wdl_merged": 0}
            tiles = sorted(
                (parsed[1], parsed[2])
                for name in o.entries
                if (parsed := parse_tile_name(name)) and parsed[0] == map_dir.lower()
            )
            lookup = {name.lower() for name in o.entries}
            wdt = o.read(wdt_key(map_dir))
            wdl = o.read(wdl_key(map_dir)) if wdl_key(map_dir).lower() in lookup else None
            overrides = {}
            if map_id == 1:
                overrides[(52, 28)] = z.read(terrain_key(map_dir, 52, 28))
            if map_id == 0:
                retained = sorted(retained_azeroth_tiles())
                collisions = [t for t in retained if t in set(tiles)]
                if collisions:
                    raise AdtError(f"retained tiles would overwrite donor terrain: {collisions[:5]}")
                client_wdl, _ = client.find(wdl_key(map_dir))
                for x, y in retained:
                    payload, _ = client.find(terrain_key(map_dir, x, y))
                    converted, stats = convert_adt_small_to_big(payload)
                    problems = verify_adt(converted)
                    if problems:
                        raise AdtError(f"converted {map_dir}_{x}_{y} failed verification: {problems[:3]}")
                    _stage_write(terrain_key(map_dir, x, y), converted, entry)
                    entry["converted"] += 1
                    entry["layers"] += stats["layers"]
                    report["retained_azeroth"]["converted"] += 1
                wdt, added = merge_wdt_main(wdt, retained)
                entry["wdt_activated"] = len(added)
                if wdl is not None:
                    wdl, merged = merge_wdl(wdl, client_wdl, retained)
                    entry["wdl_merged"] = len(merged)
            for x, y in tiles:
                payload = overrides.get((x, y)) or o.read(terrain_key(map_dir, x, y))
                _stage_write(terrain_key(map_dir, x, y), payload, entry)
                entry["adts"] += 1
            _stage_write(wdt_key(map_dir), wdt, entry)
            if wdl is not None:
                _stage_write(wdl_key(map_dir), wdl, entry)
            report["maps"][str(map_id)] = entry
    finally:
        client.close()
        o.close()
        z.close()
    return report


def command_validate_stage(args: argparse.Namespace) -> dict:
    """Re-read the staged terrain tree and check structure, counts and alpha equality."""

    wanted = _scope_maps(args.maps)
    client = _client_files(args.client / "Data")
    report = {"maps": {}, "problems": []}
    try:
        for map_id in wanted:
            map_dir, _ = TERRAIN_MAPS[map_id]
            root = STAGE_TERRAIN / "World" / "Maps" / map_dir
            if not root.is_dir():
                report["problems"].append(f"{map_dir}: staged directory missing")
                continue
            wdt = parse_wdt((root / f"{map_dir}.wdt").read_bytes())
            active = sorted(wdt["active"])
            adts = sorted(
                (int(p.stem.rsplit("_", 2)[1]), int(p.stem.rsplit("_", 2)[2]))
                for p in root.glob("*.adt")
            )
            entry = {"active": len(active), "adts": len(adts), "big": 0, "small": 0, "none": 0,
                     "index_order": 0, "alpha_reencoded": 0}
            if sorted(active) == sorted(adts):
                entry["index_order"] = 1
            else:
                report["problems"].append(f"{map_dir}: WDT active set != ADT set")
            for x, y in adts:
                payload = (root / f"{map_dir}_{x}_{y}.adt").read_bytes()
                problems = verify_adt(payload)
                if problems:
                    report["problems"].append(f"{map_dir}_{x}_{y}: {problems[:2]}")
                parsed = parse_adt(payload, deep=True)
                for chunk in parsed["chunks"]:
                    entry[chunk["alpha_format"].split(":")[0]] = entry.get(chunk["alpha_format"].split(":")[0], 0) + 1
                if map_id == 0 and (x, y) in retained_azeroth_tiles():
                    original, _ = client.find(terrain_key(map_dir, x, y))
                    expected, _ = convert_adt_small_to_big(original)
                    if expected == payload:
                        entry["alpha_reencoded"] += 1
                    else:
                        report["problems"].append(f"{map_dir}_{x}_{y}: staged bytes differ from re-encoding")
            report["maps"][str(map_id)] = entry
    finally:
        client.close()
    report["ok"] = not report["problems"]
    return report

# ------------------------------------------------------------------ asset closure

# Donor patch precedence observed in the Zeppelin install, highest first.
ZEPPELIN_SUPPLIENTS = ("Z", "X", "T", "Q", "O", "M", "L", "I", "G", "A")
ADT_HEAD_SLOTS = {"MTEX": 2, "MMDX": 3, "MMID": 4, "MWMO": 5, "MWID": 6, "MDDF": 7, "MODF": 8}
# Archives this tool writes must never count as "the client already has it" - the
# previous patch they contain is exactly what is being regenerated, and reading it
# back silently drops every file it held.
OWN_CLIENT_ARCHIVES = ("patch-q.mpq", "patch-l.mpq")

# common-3.MPQ is a Cataclysm-era archive name. The 3.3.5a client only loads
# common/common-2/expansion/lichking plus `patch-*`, so anything that lives only in
# common-3 is INVISIBLE to the client and must be imported, not reused. The earlier
# run wrongly listed it as a client source, which is why the exported terrain
# referenced a Draenor WMO the client could never open.
EXTRA_DONOR_ARCHIVES = ("common-3.MPQ",)


def _adt_head_chunk(data: bytes, slot: int) -> bytes:
    off = u32(data, 20 + 4 * slot)
    if not off:
        return b""
    at = 20 + off
    return data[at + 8 : at + 8 + u32(data, at + 4)]


def adt_reference_block(path: Path) -> bytes:
    """Read one staged ADT.

    MCLY lives inside the MCNK region, so the texture-use counts need the whole
    file, not just the name tables at the head.
    """

    return path.read_bytes()


def _split_strings(blob: bytes) -> list:
    return [part.decode("latin-1") for part in blob.split(b"\0") if part]


def _canonical(path: str) -> str:
    """One spelling per archive path: backslashes, upper case.

    Sources disagree on case and separators for the same file; merging them keeps
    the report unambiguous and matches how the client resolves paths anyway.
    """

    return path.replace("/", "\\").upper()


def _normalize_reference(path: str) -> str:
    """Collapse repeated separators; some donor ADTs double their backslashes."""

    out = path.replace("/", "\\")
    while "\\\\" in out:
        out = out.replace("\\\\", "\\")
    return out


PLACEHOLDER_RE = re.compile(r"^error_\d+\.blp$", re.IGNORECASE)


def resolve_reference(name: str, index: list) -> tuple:
    """Resolve one reference the way the client would. Returns (key used, hits)."""

    key = _canonical(_normalize_reference(name))
    candidates = [key]
    if key.endswith(".MDX") or key.endswith(".MDL"):
        # Both are legacy spellings of the same model; the client's loader accepts
        # them and looks for the .m2 file.
        candidates.append(key[:-4] + ".M2")
    for candidate in candidates:
        hits = [label for label, table in index if candidate in table]
        if hits:
            return candidate, hits
    return key, []


def adt_references(data: bytes) -> dict:
    """Collect the texture, doodad and WMO references an ADT actually uses."""

    textures = _split_strings(_adt_head_chunk(data, ADT_HEAD_SLOTS["MTEX"]))
    mmdx_blob = _adt_head_chunk(data, ADT_HEAD_SLOTS["MMDX"])
    mmid_blob = _adt_head_chunk(data, ADT_HEAD_SLOTS["MMID"])
    mwmo = _split_strings(_adt_head_chunk(data, ADT_HEAD_SLOTS["MWMO"]))
    mddf = _adt_head_chunk(data, ADT_HEAD_SLOTS["MDDF"])
    modf = _adt_head_chunk(data, ADT_HEAD_SLOTS["MODF"])

    doodads = []
    for offset in struct.unpack_from(f"<{len(mmid_blob) // 4}I", mmid_blob):
        if offset >= len(mmdx_blob):
            continue
        end = mmdx_blob.find(b"\0", offset)
        doodads.append(mmdx_blob[offset : end if end >= 0 else len(mmdx_blob)].decode("latin-1"))

    texture_uses = {}
    doodad_uses = {}
    wmo_uses = {}
    effects = set()
    cells, mnk_base = _mcnk_offsets(data, 20 + u32(data, 24))
    for index in range(256):
        raw = u32(data, cells + index * 16)
        if not raw:
            continue
        at = raw + mnk_base
        layers = u32(data, at + 20)
        mcly = u32(data, at + 36)
        if layers and mcly:
            for layer in range(layers):
                entry = at + mcly + layer * 16
                texture_id, _flags, _offset, effect = struct.unpack_from("<4I", data, entry)
                if texture_id < len(textures):
                    name = _canonical(textures[texture_id])
                    texture_uses[name] = texture_uses.get(name, 0) + 1
                if effect:
                    effects.add(effect)

    def _placement_names(blob: bytes, stride: int, names, uses: dict) -> None:
        if not names or not blob:
            return
        for position in range(0, len(blob) - stride + 1, stride):
            name_id = u32(blob, position)
            if name_id < len(names):
                name = _canonical(names[name_id])
                uses[name] = uses.get(name, 0) + 1

    _placement_names(mddf, 36, doodads, doodad_uses)
    _placement_names(modf, 64, mwmo, wmo_uses)
    return {
        "textures": texture_uses,
        "doodads": doodad_uses,
        "wmos": wmo_uses,
        "ground_effects": sorted(effects),
    }


def _list_names(storm: Storm, handle) -> set:
    """List an archive's listfile, tolerating non-ASCII names.

    `cars_mount_pack.Storm.list_files` decodes as strict ASCII and dies on the
    first Latin-1 byte in a community archive's listfile.
    """

    from cars_mount_pack import FindData

    data = FindData()
    finder = storm.dll.SFileFindFirstFile(handle, b"*", c.byref(data), None)
    names = set()
    if not finder:
        return names
    try:
        while True:
            names.add(data.cFileName.split(b"\0", 1)[0].decode("latin-1").upper())
            if not storm.dll.SFileFindNextFile(finder, c.byref(data)):
                break
    finally:
        storm.dll.SFileFindClose(finder)
    return names


def _archive_names(storm: Storm, path: Path) -> set:
    archive = Archive(path.name, path, storm)
    try:
        archive.open()
        return _list_names(storm, archive.handle)
    except OSError:
        return set()
    finally:
        archive.close()


def build_resolution_index(storm: Storm, client_data: Path) -> list:
    """Ordered (label, uppercase name set) for every donor and client archive."""

    index = []
    for label, path in _source_archives(storm, client_data):
        index.append((label, _archive_names(storm, Path(path))))
    return index


def command_assets(args: argparse.Namespace) -> dict:
    """Inventory and resolve every terrain reference for the in-scope maps."""

    wanted = _scope_maps(args.maps)
    storm = Storm(args.dll)
    tiles = {key: [] for key in TERRAIN_MAPS.values()}
    for map_id in wanted:
        map_dir, _ = TERRAIN_MAPS[map_id]
        root = STAGE_TERRAIN / "World" / "Maps" / map_dir
        for path in sorted(root.glob("*.adt")):
            tiles[(map_dir, "O")].append(path)
    references = {"textures": {}, "doodads": {}, "wmos": {}, "ground_effects": set()}
    tiles_by_path = {"textures": {}, "doodads": {}, "wmos": {}}
    for (map_dir, _source), paths in tiles.items():
        for path in paths:
            label = path.stem
            found = adt_references(adt_reference_block(path))
            for kind in ("textures", "doodads", "wmos"):
                bucket = references[kind]
                for name, uses in found[kind].items():
                    bucket[name] = bucket.get(name, 0) + uses
                    tiles_by_path[kind].setdefault(name, set()).add(label)
            references["ground_effects"].update(found["ground_effects"])

    index = build_resolution_index(storm, args.client / "Data")
    derived = {}
    for name in list(references["doodads"]):
        stem, dot, tail = name.rpartition(".")
        if dot and tail.lower() == "m2":
            derived[stem + "00.skin"] = 0
    report = {
        "archives": [label for label, _ in index],
        "counts": {kind: len(references[kind]) for kind in ("textures", "doodads", "wmos")},
        "ground_effect_ids": sorted(references["ground_effects"]),
        "resolved": {},
        "unresolved": {},
        "placeholders": {},
        "client_collisions": {},
        "anomalies": [],
    }
    for kind, names in references.items():
        if kind == "ground_effects":
            continue
        resolved = {}
        unresolved = {}
        for name in sorted(names):
            key, hits = resolve_reference(name, index)
            if hits:
                resolved[name] = hits
                if any(h.startswith("client:") for h in hits) and any(
                    h.startswith("zeppelin:") for h in hits
                ):
                    report["client_collisions"][name] = hits
                if key != name:
                    report["anomalies"].append({"path": name, "resolved_as": key})
            elif PLACEHOLDER_RE.match(name.rsplit("\\", 1)[-1]):
                report["placeholders"][name] = {
                    "uses": names[name],
                    "tiles": sorted(tiles_by_path[kind][name]),
                }
            else:
                unresolved[name] = {
                    "uses": names[name],
                    "tiles": sorted(tiles_by_path[kind][name]),
                }
        report["resolved"][kind] = resolved
        report["unresolved"][kind] = unresolved
    return report


def command_ids(args: argparse.Namespace) -> dict:
    """Verify the target IDs are free in the current client and server tables."""

    from playable_race_pack import RawWdbc

    result: dict = {
        "client": {},
        "server": {},
        "reserved_maps": sorted(RESERVED_MAPS),
        "reserved_areas": sorted(RESERVED_AREAS),
    }
    client = _client_files(args.client / "Data")
    tables: dict[str, object] = {}
    try:
        for name in CLIENT_DBC_BASELINES:
            payload, path = client.find(f"DBFilesClient\\{name}.dbc")
            table = RawWdbc(payload)
            tables[name] = table
            result["client"][name] = {
                "rows": table.count,
                "fields": table.fields,
                "record_size": table.record_size,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "archive": Path(path).name,
            }
    finally:
        client.close()
    map_ids = {int.from_bytes(row[:4], "little") for row in tables["Map"].records}
    area_ids = {int.from_bytes(row[:4], "little") for row in tables["AreaTable"].records}
    wma_ids = {int.from_bytes(row[:4], "little") for row in tables["WorldMapArea"].records}
    server_table = RawWdbc(SERVER_AREATABLE.read_bytes())
    server_ids = {int.from_bytes(row[:4], "little") for row in server_table.records}
    result["server"]["AreaTable"] = {
        "rows": server_table.count,
        "fields": server_table.fields,
        "record_size": server_table.record_size,
        "sha256": hashlib.sha256(SERVER_AREATABLE.read_bytes()).hexdigest(),
        "path": str(SERVER_AREATABLE),
        "area_bit_max": max(int.from_bytes(row[12:16], "little") for row in server_table.records),
    }
    result["client"]["AreaTable"]["area_bit_max"] = max(
        int.from_bytes(row[12:16], "little") for row in tables["AreaTable"].records
    )
    result["collisions"] = {
        "maps": sorted(set(RESERVED_MAPS) & map_ids),
        "areas_client": sorted(set(RESERVED_AREAS) & area_ids),
        "areas_server": sorted(set(RESERVED_AREAS) & server_ids),
        "world_map_area": sorted(set(RESERVED_AREAS) & wma_ids),
    }
    result["free"] = not any(result["collisions"].values())
    result["area_bit_allocation"] = {"floor": AREA_BIT_FLOOR, "ceiling": AREA_BIT_CEILING, "allocated": {}}
    return result


def _crc_table(storm: Storm, path: Path) -> dict:
    """Upper-case name -> (size, MPQ block CRC32). Cheaper than reading bytes."""

    from cars_mount_pack import FindData

    archive = Archive(path.name, path, storm)
    table: dict = {}
    try:
        archive.open()
    except OSError:
        return table
    try:
        data = FindData()
        finder = storm.dll.SFileFindFirstFile(archive.handle, b"*", c.byref(data), None)
        if not finder:
            return table
        try:
            while True:
                key = data.cFileName.split(b"\0", 1)[0].decode("latin-1").upper()
                table[key] = (data.dwFileSize, data.dwCrc32)
                if not storm.dll.SFileFindNextFile(finder, c.byref(data)):
                    break
        finally:
            storm.dll.SFileFindClose(finder)
    finally:
        archive.close()
    return table


def _source_archives(storm: Storm, client_data: Path) -> list:
    """Ordered (label, path) for every donor and client archive, donor priority first."""

    sources = []
    for key in ZEPPELIN_SUPPLIENTS:
        path = SOURCE_ARCHIVES.get(key, (None, None))[0] or ZEPPELIN_ROOT / f"PATCH-{key}.MPQ"
        if path.is_file():
            sources.append((f"zeppelin:{key}", path))
    from lib.clientfs import archive_chain

    for name in EXTRA_DONOR_ARCHIVES:
        extra = client_data / name
        if extra.is_file():
            sources.append((f"donor:{name}", extra))
    never_ours = set(OWN_CLIENT_ARCHIVES) | _client_baseline_archives()
    for entry in archive_chain(str(client_data), LOCALE):
        if Path(entry).name.lower() in never_ours:
            continue
        sources.append((f"client:{Path(entry).name}", Path(entry)))
    return sources


def _read_archive_file(sources: dict, label: str, name: str, storm: Storm) -> bytes:
    archive = Archive(label, sources[label], storm)
    archive.open()
    try:
        return archive.read(name)
    finally:
        archive.close()


def command_collisions(args: argparse.Namespace) -> dict:
    """Classify every referenced path as reuse, import or byte conflict.

    Comparison uses the MPQ block table (size + CRC32) rather than decompressing
    thousands of files; `--verify N` deep-checks the first N supposedly identical
    pairs with sha256.
    """

    assets_path = Path(args.assets) if args.assets else PLAN_ROOT / "openazeroth-starting-zones.assets.json"
    assets = json.loads(assets_path.read_text(encoding="utf-8"))
    storm = Storm(args.dll)
    sources = dict(_source_archives(storm, args.client / "Data"))
    tables = {label: _crc_table(storm, path) for label, path in sources.items()}
    index = [(label, set(table)) for label, table in tables.items()]
    donors = [label for label in sources if label.startswith("zeppelin:")]
    clients = [label for label in sources if label.startswith("client:")]
    verdicts = ("client_only", "donor_only", "identical", "different")
    summary = dict.fromkeys(verdicts, 0)
    by_kind: dict = {}
    buckets: dict = {verdict: [] for verdict in verdicts}
    for kind, entries in assets["resolved"].items():
        counts = by_kind.setdefault(kind, dict.fromkeys(verdicts, 0))
        for name, hits in entries.items():
            key, _ = resolve_reference(name, index)
            donor = next((label for label in donors if label in hits), None)
            client = next((label for label in clients if label in hits), None)
            if donor is None:
                verdict = "client_only"
            elif client is None:
                verdict = "donor_only"
            elif tables[donor].get(key) == tables[client].get(key):
                verdict = "identical"
            else:
                verdict = "different"
            summary[verdict] += 1
            counts[verdict] += 1
            if verdict == "client_only":
                continue
            record = {"path": name, "key": key, "kind": kind}
            if verdict == "donor_only":
                record.update(source=donor, size=tables[donor][key][0])
            else:
                record.update(
                    donor=donor,
                    client=client,
                    donor_size=tables[donor].get(key, (0, 0))[0],
                    client_size=tables[client].get(key, (0, 0))[0],
                )
            buckets[verdict].append(record)
    verified = 0
    for entry in buckets["identical"][: args.verify]:
        donor_bytes = _read_archive_file(sources, entry["donor"], entry["key"], storm)
        client_bytes = _read_archive_file(sources, entry["client"], entry["key"], storm)
        if hashlib.sha256(donor_bytes).digest() != hashlib.sha256(client_bytes).digest():
            raise SystemExit(f"size+CRC said identical but sha256 differs: {entry['key']}")
        verified += 1
    return {
        "policy_note": (
            "Policy revised 2026-10-05 after live testing: 'identical' and 'client_only' reuse the "
            "client's copy, but 'different' now takes the DONOR's copy as well as 'donor_only'. The "
            "terrain for maps 0/1 was replaced wholesale, so the donor's asset versions are the ones "
            "it was authored against; keeping Esteria's left landmarks like Stormwind built from a "
            "different WMO and group set than the ground they stand on."
        ),
        "summary": summary,
        "by_kind": by_kind,
        "verified_identical": verified,
        "donor_only": sorted(buckets["donor_only"], key=lambda item: -item["size"]),
        "different": sorted(
            buckets["different"], key=lambda item: -abs(item["donor_size"] - item["client_size"])
        ),
        "counts": {"donor_only": len(buckets["donor_only"]), "different": len(buckets["different"])},
    }

def _companions(key: str) -> list:
    """Candidate companion files for one donor import.

    M2 models need their `NN.skin` views; WMO roots need their numbered group
    files. Probing the archive tables is cheaper and more reliable than trusting a
    half-understood header.
    """

    stem, dot, tail = key.rpartition(".")
    if not dot:
        return []
    if tail == "M2":
        return [f"{stem}{index:02d}.SKIN" for index in range(16)]
    if tail == "WMO":
        return [f"{stem}_{index:03d}.WMO" for index in range(400)]
    return []


def command_imports(args: argparse.Namespace) -> dict:
    """Expand the donor-only imports into a complete file list with companions."""

    collisions_path = (
        Path(args.assets) if args.assets else PLAN_ROOT / "openazeroth-starting-zones.collisions.json"
    )
    collisions = json.loads(collisions_path.read_text(encoding="utf-8"))
    storm = Storm(args.dll)
    sources = dict(_source_archives(storm, args.client / "Data"))
    tables = {label: _crc_table(storm, path) for label, path in sources.items()}
    index = [(label, set(table)) for label, table in tables.items()]
    roots = list(collisions["donor_only"]) + [
        {"path": entry["path"], "key": entry["key"], "source": entry["donor"],
         "size": entry["donor_size"]}
        for entry in collisions["different"]
    ]
    entries = {}
    for root in roots:
        entries[root["key"]] = {
            "role": "root",
            "source": root["source"],
            "size": root["size"],
        }
        for companion in _companions(root["key"]):
            if companion in entries:
                continue
            hits = [label for label, table in index if companion in table]
            if not hits:
                continue
            donor = next((label for label in hits if label.startswith("zeppelin:")), None)
            client = next((label for label in hits if label.startswith("client:")), None)
            if donor is None:
                continue
            entries[companion] = {
                "role": "companion",
                "source": donor,
                "size": tables[donor][companion][0],
                "client_copy": bool(client),
            }
    companions = [item for item in entries.values() if item["role"] == "companion"]
    return {
        "roots": len(roots),
        "files": len(entries),
        "companion_bytes": sum(item["size"] for item in companions),
        "total_bytes": sum(item["size"] for item in entries.values()),
        "companions_on_client": sum(1 for item in companions if item["client_copy"]),
        "unresolved_companions": sum(
            1 for root in roots for companion in _companions(root["key"]) if companion not in entries
        ),
        "entries": dict(sorted(entries.items())),
    }

M2_TEXTURES_OFFSET = 0x50
PRINTABLE_RUN_RE = re.compile(rb"[ -~]{6,220}")


def m2_texture_names(data: bytes) -> tuple:
    """Texture paths embedded in an MD20/MD21 model.

    The M2Array at 0x50 gives the declared count; the names themselves are the
    printable `.blp` runs in the file. Both are returned so the caller can check
    that the scan and the header agree instead of trusting either alone.
    """

    if data[:4] not in (b"MD20", b"MD21"):
        raise ValueError("not an M2 file")
    declared = struct.unpack_from("<I", data, M2_TEXTURES_OFFSET)[0]
    names = [
        run.decode("latin-1")
        for run in PRINTABLE_RUN_RE.findall(data)
        if run.lower().endswith(b".blp")
    ]
    return names, declared


def wmo_references(data: bytes) -> dict:
    """Texture and doodad paths named by a WMO root file."""

    result = {"textures": [], "doodads": [], "declared_textures": None, "groups": None}
    off = 0
    while off + 8 <= len(data):
        tag = fcc(data, off)[::-1]
        size = u32(data, off + 4)
        body = data[off + 8 : off + 8 + size]
        if tag == b"MOHD":
            result["declared_textures"] = u32(data, off + 8)
            result["groups"] = u32(data, off + 12)
        elif tag == b"MOTX":
            result["textures"] = _split_strings(body)
        elif tag == b"MODN":
            result["doodads"] = _split_strings(body)
        off += 8 + size
    return result


ARCHIVE_ROOT = STAGING_ROOT / "archives"
ARCHIVE_MAX_FILES = 0x00000003  # StormLib V4: hi-block table, needed past 4 GiB
ARCHIVE_COMPRESSION = 0x00000002  # MPQ_COMPRESSION_ZLIB
# Without MPQ_FILE_COMPRESS on the file itself, SFileWriteFile's compression mask
# is ignored and the payload is stored verbatim - which pushed a first attempt into
# the 4 GiB v1 ceiling.
ARCHIVE_FILE_FLAGS = 0x00000200  # MPQ_FILE_COMPRESS


def _write_archive(storm: Storm, path: Path, items: list, label: str) -> dict:
    """Stream entries into a new MPQ; one file is held in memory at a time."""

    handle = c.c_void_p()
    if path.exists():
        # SFileCreateArchive refuses to overwrite (ERROR_ALREADY_EXISTS); truncating
        # the previous build is cheaper than deleting it.
        with path.open("r+b") as handle_file:
            handle_file.truncate(0)
    if not storm.dll.SFileCreateArchive(
        str(path), ARCHIVE_MAX_FILES, len(items) + 64, c.byref(handle)
    ):
        raise OSError(f"SFileCreateArchive failed: {path} ({c.get_last_error()})")
    written = 0
    raw = 0
    try:
        for name, provider in items:
            payload = provider()
            file_handle = c.c_void_p()
            key = name.encode("latin-1")
            if not storm.dll.SFileCreateFile(
                handle, key, 0, len(payload), 0, ARCHIVE_FILE_FLAGS, c.byref(file_handle)
            ):
                raise OSError(f"SFileCreateFile failed: {name} ({c.get_last_error()})")
            try:
                buffer = c.create_string_buffer(payload or b"\\0")
                if not storm.dll.SFileWriteFile(file_handle, buffer, len(payload), ARCHIVE_COMPRESSION):
                    raise OSError(f"SFileWriteFile failed: {name} ({c.get_last_error()})")
            finally:
                storm.dll.SFileCloseFile(file_handle)
            written += 1
            raw += len(payload)
            if written % 200 == 0:
                print(f"  {label}: {written}/{len(items)} entries, {raw / 1e6:.0f} MB raw", flush=True)
    finally:
        storm.dll.SFileCloseArchive(handle)
    return {"path": str(path), "entries": written, "raw_bytes": raw, "bytes": path.stat().st_size}


def command_pack(args: argparse.Namespace) -> dict:
    """Write the staged terrain and the donor imports into new patch archives."""

    closure_path = Path(args.assets) if args.assets else PLAN_ROOT / "openazeroth-starting-zones.closure.json"
    closure = json.loads(closure_path.read_text(encoding="utf-8"))
    copies = closure["files"]
    storm = Storm(args.dll)
    sources = dict(_source_archives(storm, args.client / "Data"))
    # The output names are explicit, not "whatever letter happens to be free": the
    # same two archives are referenced by the extraction view and by the client
    # install, and re-running pack must not silently move them.
    ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)
    terrain_letter = args.terrain_letter.upper()
    asset_letter = args.asset_letter.upper()

    terrain = []
    for map_dir in sorted({TERRAIN_MAPS[map_id][0] for map_id in TERRAIN_MAPS}):
        root = STAGE_TERRAIN / "World" / "Maps" / map_dir
        for path in sorted(root.iterdir()):
            if path.is_file():
                name = f"World\\Maps\\{map_dir}\\{path.name}"
                terrain.append((name, (lambda p: (lambda: p.read_bytes()))(path)))
    assets = []
    for name, info in sorted(copies.items()):
        source = info["source"]
        read_name = info.get("read_as", name)
        assets.append((name, (lambda s, n: (lambda: _read_archive_file(sources, s, n, storm)))(source, read_name)))

    terrain_archive = ARCHIVE_ROOT / f"patch-{terrain_letter}.mpq"
    asset_archive = ARCHIVE_ROOT / f"patch-{asset_letter}.mpq"
    report = {"only": args.only}
    if args.only in ("both", "terrain"):
        report["terrain"] = _write_archive(storm, terrain_archive, terrain, terrain_letter)
    if args.only in ("both", "assets"):
        report["assets"] = _write_archive(storm, asset_archive, assets, asset_letter)
    report["total_bytes"] = sum(part["bytes"] for key, part in report.items() if isinstance(part, dict))
    report["total_entries"] = sum(part["entries"] for key, part in report.items() if isinstance(part, dict))
    return report


# Documented stand-ins for references no supplied archive can satisfy. The donor
# terrain places `Creature\FrogDuck\FrogDuck.m2` on Azeroth_30_47 next to Stormwind
# and no archive has it; the client's own frog is the closest native critter, and
# shipping it under the referenced key keeps the client from failing SafeOpen on
# that tile.
MODEL_SUBSTITUTIONS = (
    ("CREATURE\\FROGDUCK\\FROGDUCK.M2", "CREATURE\\FROG\\FROG.M2"),
    ("CREATURE\\FROGDUCK\\FROGDUCK00.SKIN", "CREATURE\\FROG\\FROG00.SKIN"),
)


def command_closure(args: argparse.Namespace) -> dict:
    """Resolve the embedded references of every imported model and WMO root."""

    imports_path = Path(args.assets) if args.assets else PLAN_ROOT / "openazeroth-starting-zones.imports.json"
    imports = json.loads(imports_path.read_text(encoding="utf-8"))
    storm = Storm(args.dll)
    sources = dict(_source_archives(storm, args.client / "Data"))
    tables = {label: _crc_table(storm, path) for label, path in sources.items()}
    index = [(label, set(table)) for label, table in tables.items()]
    donors = [label for label in sources if label.startswith("zeppelin:")]
    clients = [label for label in sources if label.startswith("client:")]

    def pick(path: str):
        hits = [label for label, table in index if path in table]
        donor = next((label for label in donors if label in hits), None)
        client = next((label for label in clients if label in hits), None)
        return donor, client

    files = dict(imports["entries"])
    substitutions = {}
    for target, source in MODEL_SUBSTITUTIONS:
        if target in files:
            continue
        donor, client = pick(source)
        holder = donor or client
        if holder is None:
            continue
        record = {"role": "substitution", "source": holder, "size": tables[holder][source][0],
                  "read_as": source, "from": source}
        files[target] = record
        substitutions[target] = record
    queue = [key for key, info in files.items() if info["role"] == "root"]
    added: dict = {}
    notes: list = []
    unresolved: list = []
    reuse = 0
    depth = 0
    while queue and depth < 4:
        depth += 1
        next_queue = []
        for key in queue:
            info = files[key]
            if info["source"] not in sources:
                continue
            try:
                payload = _read_archive_file(sources, info["source"], key, storm)
            except OSError:
                unresolved.append({"path": key, "reason": "root unreadable"})
                continue
            wanted: list = []
            if key.endswith(".M2"):
                names, declared = m2_texture_names(payload)
                if declared != len(names):
                    notes.append({"path": key, "note": f"M2 declares {declared} textures, scanned {len(names)}"})
                wanted = names
            elif key.endswith(".WMO"):
                refs = wmo_references(payload)
                if refs["declared_textures"] != len(refs["textures"]):
                    notes.append({
                        "path": key,
                        "note": f"WMO declares {refs['declared_textures']} textures, parsed {len(refs['textures'])}",
                    })
                wanted = refs["textures"] + refs["doodads"]
            for name in wanted:
                candidate = _canonical(_normalize_reference(name))
                if candidate.endswith(".MDX"):
                    candidate = candidate[:-4] + ".M2"
                if candidate in files:
                    continue
                donor, client = pick(candidate)
                if client is not None:
                    reuse += 1
                    continue
                if donor is None:
                    unresolved.append({"path": candidate, "reason": f"referenced by {key}"})
                    continue
                record = {
                    "role": "dependency",
                    "source": donor,
                    "size": tables[donor][candidate][0],
                    "client_copy": False,
                    "referenced_by": key,
                }
                files[candidate] = record
                added[candidate] = record
                next_queue.append(candidate)
        queue = next_queue
    return {
        "roots": imports["roots"],
        "initial_files": imports["files"],
        "dependency_files": len(added),
        "total_files": len(files),
        "total_bytes": sum(info["size"] for info in files.values()),
        "reused_from_client": reuse,
        "notes": notes,
        "unresolved": unresolved,
        "depth_reached": depth,
        "added": dict(sorted(added.items())),
        "substitutions": dict(sorted(substitutions.items())),
        "files": dict(sorted(files.items())),
    }


BOOKKEEPING = ("(LISTFILE)", "(ATTRIBUTES)", "(SIGNATURE)", "(USERDATA)")


def command_validate_pack(args: argparse.Namespace) -> dict:
    """Read the written archives back and re-check structure and counts."""

    closure_path = Path(args.assets) if args.assets else PLAN_ROOT / "openazeroth-starting-zones.closure.json"
    closure = json.loads(closure_path.read_text(encoding="utf-8"))
    storm = Storm(args.dll)
    problems = []
    report = {"archives": {}, "problems": problems}
    expected_terrain = sum(
        1
        for map_id in TERRAIN_MAPS
        for path in (STAGE_TERRAIN / "World" / "Maps" / TERRAIN_MAPS[map_id][0]).iterdir()
        if path.is_file()
    )
    terrain_entries = 0
    asset_entries = 0
    for path in sorted(ARCHIVE_ROOT.glob("patch-*.mpq")):
        if path.stat().st_size == 0:
            continue
        archive = Archive(path.name, path, storm)
        archive.open()
        try:
            names = sorted(name for name in _list_names(storm, archive.handle) if name not in BOOKKEEPING)
            adts = [name for name in names if name.endswith(".ADT")]
            report["archives"][path.name] = {
                "entries": len(names),
                "adts": len(adts),
                "bytes": path.stat().st_size,
            }
            if adts:
                terrain_entries = len(names)
                for name in names:
                    if name.endswith(".WDT"):
                        parsed = parse_wdt(archive.read(name))
                        report.setdefault("wdt_active", {})[name] = len(parsed["active"])
                for name in adts[:5] + adts[-5:]:
                    issues = verify_adt(archive.read(name))
                    if issues:
                        problems.append(f"{path.name}:{name}: {issues[:2]}")
            else:
                asset_entries = len(names)
        finally:
            archive.close()
    report["terrain_entries"] = terrain_entries
    report["asset_entries"] = asset_entries
    report["expected_terrain"] = expected_terrain
    report["expected_assets"] = len(closure["files"])
    if terrain_entries != expected_terrain:
        problems.append(f"terrain entries {terrain_entries} != {expected_terrain}")
    if asset_entries != len(closure["files"]):
        problems.append(f"asset entries {asset_entries} != {len(closure['files'])}")
    report["ok"] = not problems
    return report

def _asset_summary(report: dict) -> dict:
    return {
        "archives": report["archives"],
        "counts": report["counts"],
        "ground_effect_ids": report["ground_effect_ids"],
        "unresolved": report["unresolved"],
        "placeholders": report["placeholders"],
        "anomaly_count": len(report["anomalies"]),
        "client_donor_collisions": len(report["client_collisions"]),
    }


AREA_FIELDS = {"id": 0, "continent": 1, "parent": 2, "bit": 3, "flags": 4, "explore": 10}
AREA_NAME_FIELDS = tuple(range(11, 27))
MAP_FIELDS = {"id": 0, "directory": 1, "instance": 2, "entrance_map": 59,
              "entrance_x": 60, "entrance_y": 61, "time_of_day": 62, "expansion": 63}
MAP_NAME_FIELDS = tuple(range(5, 21))
WMA_FIELDS = {"id": 0, "map": 1, "area": 2, "name": 3, "left": 4, "right": 5, "top": 6,
              "bottom": 7, "parent": 10}
WORLDMAPOVERLAY_FIELDS = {"id": 0, "map_area": 1, "area_first": 2, "area_last": 5,
                          "texture": 8, "width": 9, "height": 10}


def _dbc_rows(data: bytes) -> tuple:
    from playable_race_pack import RawWdbc

    table = RawWdbc(data)
    return table, {int.from_bytes(row[:4], "little"): row for row in table.records}


def _dbc_string(table, record: bytes, field: int) -> str:
    offset = int.from_bytes(record[field * 4 : field * 4 + 4], "little")
    if not offset:
        return ""
    end = table.strings.find(b"\0", offset)
    return table.strings[offset : end if end >= 0 else len(table.strings)].decode("utf-8", "replace")


def _client_baseline_archives() -> set:
    """Head the client's own data files, minus the patch this tool installs.

    Once patch-enUS-7 is installed it wins every lookup, so reading the "client"
    row set back out of it would make each merge pass a no-op - the same trap
    OWN_CLIENT_ARCHIVES covers for the asset chain. Excluding it keeps the checks
    against the client's real baseline (patch-enUS-6 and below).
    """

    return {f"patch-{LOCALE}-{VIEW_LOCALE_SLOT}.MPQ".lower()}


def _client_files(client_data: Path) -> ClientFiles:
    return ClientFiles(str(client_data), LOCALE, exclude=_client_baseline_archives())


def _client_table(client_data: Path, name: str) -> bytes:
    files = _client_files(client_data)
    try:
        return files.find(f"DBFilesClient\\{name}.dbc")[0]
    finally:
        files.close()


def staged_area_usage(args: argparse.Namespace) -> dict:
    """Area ids actually referenced by the staged terrain, per map."""

    usage: dict = {}
    for map_id in _scope_maps(args.maps):
        map_dir, _ = TERRAIN_MAPS[map_id]
        counts: dict = {}
        for path in sorted((STAGE_TERRAIN / "World" / "Maps" / map_dir).glob("*.adt")):
            for chunk in parse_adt(path.read_bytes(), deep=True)["chunks"]:
                counts[chunk["area"]] = counts.get(chunk["area"], 0) + 1
        usage[map_id] = counts
    return usage


def command_areas(args: argparse.Namespace) -> dict:
    """Compare the terrain's area ids against the client and donor AreaTable."""

    usage = staged_area_usage(args)
    client_table, client_rows = _dbc_rows(_client_table(args.client / "Data", "AreaTable"))
    storm = Storm(args.dll)
    donors = {}
    for key in ("O", "Z"):
        archive = Archive(key, SOURCE_ARCHIVES[key][0], storm)
        archive.open()
        try:
            payload = archive.read("DBFilesClient\\AreaTable.dbc")
        finally:
            archive.close()
        table, rows = _dbc_rows(payload)
        donors[key] = (table, rows)

    def parent_of(area_id: int):
        row = client_rows.get(area_id)
        source = "client"
        if row is None:
            for key in ("Z", "O"):
                if area_id in donors[key][1]:
                    row = donors[key][1][area_id]
                    source = key
                    break
        if row is None:
            return None, None
        return int.from_bytes(row[8:12], "little"), source

    report = {"maps": {}, "missing_total": 0, "background_only": []}
    for map_id, counts in usage.items():
        ids = sorted(counts)
        missing = [area for area in ids if area not in client_rows]
        report["maps"][str(map_id)] = {
            "distinct_areas": len(ids),
            "chunks": sum(counts.values()),
            "missing_from_client": len(missing),
            "missing_ids": missing,
            "root_candidates": [(area, counts[area]) for area in ids
                                if counts[area] == max(counts.values())][:5],
        }
        report["missing_total"] += len(missing)
        for area in missing:
            if area == 0:
                report["background_only"].append(map_id)
    parents = {}
    for map_id, entry in report["maps"].items():
        for area in entry["missing_ids"]:
            chain = []
            current = area
            seen = set()
            while current not in seen:
                seen.add(current)
                parent, source = parent_of(current)
                if parent in (None, 0) or parent == current:
                    break
                chain.append({"area": parent, "source": source,
                              "in_client": parent in client_rows})
                current = parent
            parents[area] = chain
    report["parent_chains"] = parents
    report["client_rows"] = client_table.count
    report["donor_rows"] = {key: donors[key][0].count for key in donors}
    report["client_area_bit_max"] = max(
        int.from_bytes(row[12:16], "little") for row in client_rows.values()
    )
    return report

DBC_ROOT = STAGING_ROOT / "dbc"
AREA_BIT_START = 3618
AREA_BIT_LIMIT = 4096


def _build_dbc(fields: int, record_size: int, records: list, pool: bytes) -> bytes:
    header = struct.pack("<4s4I", b"WDBC", len(records), fields, record_size, len(pool))
    return header + b"".join(records) + pool


def _rebase_strings(table, record: bytes, pool: bytearray, fields) -> bytes:
    out = bytearray(record)
    for field in fields:
        text = _dbc_string(table, record, field)
        if not text:
            struct.pack_into("<I", out, field * 4, 0)
            continue
        offset = len(pool)
        pool.extend(text.encode("utf-8"))
        pool.append(0)
        struct.pack_into("<I", out, field * 4, offset)
    return bytes(out)


def _fallback_area_row(area: int, map_id: int, record_size: int, pool: bytearray) -> bytes:
    """Neutral, explicitly labelled row for an area no donor patch defines."""

    row = bytearray(record_size)
    struct.pack_into("<I", row, 0, area)
    struct.pack_into("<I", row, 4, map_id)
    offset = len(pool)
    pool.extend(f"Unnamed Area {area}".encode("utf-8"))
    pool.append(0)
    struct.pack_into("<I", row, 11 * 4, offset)
    return bytes(row)


def _is_sorted_by_id(records: list) -> bool:
    ids = [int.from_bytes(record[:4], "little") for record in records]
    return ids == sorted(ids)


def command_dbc(args: argparse.Namespace) -> dict:
    """Merge the donor Map/AreaTable/WorldMapArea rows the terrain needs."""

    wanted = _scope_maps(args.maps)
    usage = staged_area_usage(args)
    client_data = args.client / "Data"
    client_map = _dbc_rows(_client_table(client_data, "Map"))
    client_area = _dbc_rows(_client_table(client_data, "AreaTable"))
    client_wma = _dbc_rows(_client_table(client_data, "WorldMapArea"))
    client_overlay = _dbc_rows(_client_table(client_data, "WorldMapOverlay"))
    storm = Storm(args.dll)
    donor = {}
    for key in ("O", "Z"):
        archive = Archive(key, SOURCE_ARCHIVES[key][0], storm)
        archive.open()
        try:
            donor[key] = {
                name: _dbc_rows(archive.read(f"DBFilesClient\\{name}.dbc"))
                for name in ("Map", "AreaTable", "WorldMapArea", "WorldMapOverlay")
            }
        finally:
            archive.close()

    used_ids = set(client_area[1])
    used_bits = {int.from_bytes(row[12:16], "little") for row in client_area[1].values()}
    for key in donor:
        used_bits |= {int.from_bytes(row[12:16], "little") for row in donor[key]["AreaTable"][1].values()}

    # Which map each area is actually used on, and which areas are absent locally.
    area_map: dict = {}
    for map_id, counts in usage.items():
        for area in counts:
            area_map.setdefault(area, set()).add(map_id)
    # The zone overlays added further down label sub-areas by area id. A sub-area
    # with no AreaTable row still draws its texture but has no name, so those ids
    # get the same treatment as the terrain's own. One case in practice: 4911
    # "Volcanoth's Lair", named by the Lost Isles' Lostpeak overlay.
    overlay_areas = 0
    for wma_id in sorted(WORLD_MAP_ZONES):
        wma_row = donor["O"]["WorldMapArea"][1].get(wma_id)
        if wma_row is None:
            continue
        continent = int.from_bytes(wma_row[4:8], "little")
        for row in donor["O"]["WorldMapOverlay"][1].values():
            if int.from_bytes(row[4:8], "little") != wma_id:
                continue
            for field in range(WORLDMAPOVERLAY_FIELDS["area_first"],
                               WORLDMAPOVERLAY_FIELDS["area_last"] + 1):
                area = int.from_bytes(row[field * 4:field * 4 + 4], "little")
                if area and area not in used_ids and area not in area_map:
                    area_map[area] = {continent}
                    overlay_areas += 1
    missing = sorted(area for area in area_map if area and area not in used_ids)

    source_of: dict = {}
    rows = []
    pool = bytearray(client_area[0].strings)
    conflicts = []
    fallbacks = []
    allocations = {}
    next_bit = AREA_BIT_START
    for area in missing:
        row = None
        for key in ("Z", "O"):
            if area in donor[key]["AreaTable"][1]:
                row = donor[key]["AreaTable"][1][area]
                source_of[area] = key
                break
        if row is None:
            fallback = bytes(_fallback_area_row(area, sorted(area_map[area])[0], client_area[0].record_size, pool))
            rows.append(fallback)
            fallbacks.append({"area": area, "continent": sorted(area_map[area])[0],
                              "name": f"Unnamed Area {area}"})
            continue
        maps = sorted(area_map[area])
        record = _rebase_strings(donor[source_of[area]]["AreaTable"][0], row, pool, AREA_NAME_FIELDS)
        out = bytearray(record)
        continent = int.from_bytes(row[4:8], "little")
        if len(maps) > 1:
            conflicts.append({"area": area, "reason": f"used on maps {maps}, keeping donor continent {continent}"})
        elif continent != maps[0]:
            struct.pack_into("<I", out, 4, maps[0])
        donor_bit = int.from_bytes(row[12:16], "little")
        if donor_bit:
            while next_bit in used_bits and next_bit < AREA_BIT_LIMIT:
                next_bit += 1
            if next_bit >= AREA_BIT_LIMIT:
                raise SystemExit(f"area bit space exhausted at {next_bit}")
            struct.pack_into("<I", out, 12, next_bit)
            used_bits.add(next_bit)
            allocations[str(area)] = {"donor_bit": donor_bit, "bit": next_bit, "source": source_of[area]}
            next_bit += 1
        rows.append(bytes(out))

    area_records = list(client_area[1].values()) + rows
    if _is_sorted_by_id(list(client_area[1].values())):
        area_records.sort(key=lambda record: int.from_bytes(record[:4], "little"))
    merged_area = _build_dbc(client_area[0].fields, client_area[0].record_size, area_records, bytes(pool))

    # Map rows: any in-scope map the client lacks.
    map_pool = bytearray(client_map[0].strings)
    map_rows = []
    map_added = []
    for map_id in wanted:
        if map_id in client_map[1]:
            continue
        row = None
        for key in ("O",):
            if map_id in donor[key]["Map"][1]:
                row = donor[key]["Map"][1][map_id]
                break
        if row is None:
            conflicts.append({"map": map_id, "reason": "no donor Map row"})
            continue
        record = _rebase_strings(donor["O"]["Map"][0], row, map_pool, (1,) + MAP_NAME_FIELDS)
        out = bytearray(record)
        struct.pack_into("<I", out, MAP_FIELDS["instance"] * 4, 0)
        struct.pack_into("<I", out, MAP_FIELDS["expansion"] * 4, 0)
        struct.pack_into("<i", out, MAP_FIELDS["entrance_map"] * 4, -1)
        struct.pack_into("<f", out, MAP_FIELDS["entrance_x"] * 4, 0.0)
        struct.pack_into("<f", out, MAP_FIELDS["entrance_y"] * 4, 0.0)
        map_rows.append(bytes(out))
        map_added.append(map_id)
    map_records = list(client_map[1].values()) + map_rows
    if _is_sorted_by_id(list(client_map[1].values())):
        map_records.sort(key=lambda record: int.from_bytes(record[:4], "little"))
    merged_map = _build_dbc(client_map[0].fields, client_map[0].record_size, map_records, bytes(map_pool))

    # WorldMapArea rows for maps the client has no entry for.
    wma_pool = bytearray(client_wma[0].strings)
    wma_rows = []
    wma_added = []
    wma_retargeted = []
    known_maps = {int.from_bytes(row[4:8], "little") for row in client_wma[1].values()}
    for map_id in wanted:
        if map_id in known_maps:
            continue
        o_wma = donor["O"]["WorldMapArea"]
        for wma_id, row in sorted(o_wma[1].items()):
            if int.from_bytes(row[4:8], "little") != map_id:
                continue
            record = bytearray(_rebase_strings(o_wma[0], row, wma_pool, (WMA_FIELDS["name"],)))
            dominant = max(usage[map_id], key=usage[map_id].get)
            struct.pack_into("<I", record, WMA_FIELDS["area"] * 4, dominant)
            wma_retargeted.append({"id": wma_id, "donor_area": int.from_bytes(row[8:12], "little"),
                                   "area": dominant})
            wma_rows.append(bytes(record))
            wma_added.append(wma_id)

    # WorldMapArea rows for zones the ported terrain put on a map the client has.
    world_map_zones = []
    for wma_id in sorted(WORLD_MAP_ZONES):
        if wma_id in client_wma[1]:
            continue
        row = None
        for key in ("O", "Z"):
            table = donor[key]["WorldMapArea"]
            if wma_id in table[1]:
                row = table[1][wma_id]
                break
        if row is None:
            raise SystemExit(f"no donor WorldMapArea row {wma_id} ({WORLD_MAP_ZONES[wma_id]})")
        record = _rebase_strings(table[0], row, wma_pool, (WMA_FIELDS["name"],))
        wma_rows.append(record)
        wma_added.append(wma_id)
        world_map_zones.append({
            "id": wma_id,
            "name": _dbc_string(table[0], row, WMA_FIELDS["name"]),
            "map": int.from_bytes(row[4:8], "little"),
            "area": int.from_bytes(row[8:12], "little"),
            "parent": int.from_bytes(row[40:44], "little"),
        })
    wma_records = list(client_wma[1].values()) + wma_rows
    if _is_sorted_by_id(list(client_wma[1].values())):
        wma_records.sort(key=lambda record: int.from_bytes(record[:4], "little"))
    merged_wma = _build_dbc(client_wma[0].fields, client_wma[0].record_size, wma_records, bytes(wma_pool))

    # WorldMapOverlay rows that draw (and label) those zones' sub-areas. The
    # texture they name is resolved by the client as
    # Interface\WorldMap\<zone name>\<texture name><n>, so the zone art has to
    # ship with them - command_client_dbc copies the donor's whole zone folder.
    added_zone_ids = {zone["id"] for zone in world_map_zones}
    overlay_pool = bytearray(client_overlay[0].strings)
    overlay_rows = []
    overlay_added = []
    for wma_id in sorted(added_zone_ids):
        for overlay_id, row in sorted(donor["O"]["WorldMapOverlay"][1].items()):
            if int.from_bytes(row[4:8], "little") != wma_id:
                continue
            if overlay_id in client_overlay[1]:
                raise SystemExit(f"WorldMapOverlay {overlay_id} already exists in the client")
            record = _rebase_strings(donor["O"]["WorldMapOverlay"][0], row, overlay_pool,
                                     (WORLDMAPOVERLAY_FIELDS["texture"],))
            overlay_rows.append(record)
            overlay_added.append(overlay_id)
    overlay_records = list(client_overlay[1].values()) + overlay_rows
    if _is_sorted_by_id(list(client_overlay[1].values())):
        overlay_records.sort(key=lambda record: int.from_bytes(record[:4], "little"))
    merged_overlay = _build_dbc(client_overlay[0].fields, client_overlay[0].record_size,
                                overlay_records, bytes(overlay_pool))

    DBC_ROOT.mkdir(parents=True, exist_ok=True)
    written = {}
    for name, payload in (("Map", merged_map), ("AreaTable", merged_area),
                          ("WorldMapArea", merged_wma), ("WorldMapOverlay", merged_overlay)):
        path = DBC_ROOT / f"{name}.dbc"
        path.write_bytes(payload)
        written[name] = {"path": str(path), "bytes": len(payload)}
    check_areas = _dbc_rows(merged_area)[1]
    bits = [int.from_bytes(row[12:16], "little") for row in check_areas.values()]
    nonzero_bits = [bit for bit in bits if bit]
    verification = {
        "areas_still_missing": sorted(area for area in area_map if area and area not in check_areas),
        "area_ids_sorted": _is_sorted_by_id(list(check_areas.values())),
        "duplicate_area_bits": len(nonzero_bits) - len(set(nonzero_bits)),
        "area_bit_over_limit": sum(1 for bit in nonzero_bits if bit >= AREA_BIT_LIMIT),
        "map_row_count": _dbc_rows(merged_map)[0].count,
        "map_1469_present": 1469 in _dbc_rows(merged_map)[1],
        "world_map_area_row_count": _dbc_rows(merged_wma)[0].count,
        "world_map_overlay_row_count": _dbc_rows(merged_overlay)[0].count,
        "world_map_zones_present": sorted(wma_id for wma_id in WORLD_MAP_ZONES
                                          if wma_id in _dbc_rows(merged_wma)[1]),
    }
    report = {
        "written": written,
        "verification": verification,
        "area_rows_before": client_area[0].count,
        "area_rows_added": len(rows),
        "area_rows_after": len(area_records),
        "map_rows_before": client_map[0].count,
        "maps_added": map_added,
        "overlay_areas_added": overlay_areas,
        "world_map_area_added": wma_added,
        "area_bits_allocated": len(allocations),
        "area_bit_range": [AREA_BIT_START, next_bit - 1] if allocations else None,
        "allocations": allocations,
        "fallbacks": fallbacks,
        "world_map_area_retargeted": wma_retargeted,
        "world_map_zones": world_map_zones,
        "world_map_overlay_added": overlay_added,
        "conflicts": conflicts,
    }
    (DBC_ROOT / "allocations.json").write_text(
        json.dumps({"areas": allocations, "maps": map_added, "world_map_area": wma_added},
                   indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report

SQL_ROOT = STAGING_ROOT / "sql"
PENDING_WORLD_SQL = ROOT / "data" / "sql" / "updates" / "pending_db_world"
# The bound server AreaTable (mod-fly-anywhere) sets these on every row; new rows
# must match or flying is silently disabled over the imported terrain.
SERVER_AREA_FLAG_ADD = 0x00004400
DBC_LOCALES = ("enUS", "enGB", "koKR", "frFR", "deDE", "enCN", "zhCN", "enTW",
               "zhTW", "esES", "esMX", "ruRU", "ptPT", "ptBR", "itIT", "Unk")
AREATABLE_COLUMNS = (
    ("ID", "int"), ("ContinentID", "int"), ("ParentAreaID", "int"), ("AreaBit", "int"),
    ("Flags", "int"), ("SoundProviderPref", "int"), ("SoundProviderPrefUnderwater", "int"),
    ("AmbienceID", "int"), ("ZoneMusic", "int"), ("IntroSound", "int"), ("ExplorationLevel", "int"),
) + tuple((f"AreaName_Lang_{locale}", "str") for locale in DBC_LOCALES) + (
    ("AreaName_Lang_Mask", "int"), ("FactionGroupMask", "int"),
    ("LiquidTypeID_1", "int"), ("LiquidTypeID_2", "int"), ("LiquidTypeID_3", "int"),
    ("LiquidTypeID_4", "int"), ("MinElevation", "float"), ("Ambient_Multiplier", "float"),
    ("Lightid", "int"),
)
MAP_COLUMNS = (
    ("ID", "int"), ("Directory", "str"), ("InstanceType", "int"), ("Flags", "int"), ("PVP", "int"),
) + tuple((f"MapName_Lang_{locale}", "str") for locale in DBC_LOCALES) + (
    ("MapName_Lang_Mask", "int"), ("AreaTableID", "int"),
) + tuple((f"MapDescription0_Lang_{locale}", "str") for locale in DBC_LOCALES) + (
    ("MapDescription0_Lang_Mask", "int"),
) + tuple((f"MapDescription1_Lang_{locale}", "str") for locale in DBC_LOCALES) + (
    ("MapDescription1_Lang_Mask", "int"), ("LoadingScreenID", "int"), ("MinimapIconScale", "float"),
    ("CorpseMapID", "int"), ("CorpseX", "float"), ("CorpseY", "float"),
    ("TimeOfDayOverride", "int"), ("ExpansionID", "int"), ("RaidOffset", "int"), ("MaxPlayers", "int"),
)
WORLDMAPAREA_COLUMNS = (
    ("ID", "int"), ("MapID", "int"), ("AreaID", "int"), ("AreaName", "str"),
    ("LocLeft", "float"), ("LocRight", "float"), ("LocTop", "float"), ("LocBottom", "float"),
    ("DisplayMapID", "int"), ("DefaultDungeonFloor", "int"), ("ParentWorldMapID", "int"),
)
WORLDMAPOVERLAY_COLUMNS = (
    ("ID", "int"), ("MapAreaID", "int"), ("AreaID_1", "int"), ("AreaID_2", "int"),
    ("AreaID_3", "int"), ("AreaID_4", "int"), ("MapPointX", "int"), ("MapPointY", "int"),
    ("TextureName", "str"), ("TextureWidth", "int"), ("TextureHeight", "int"),
    ("OffsetX", "int"), ("OffsetY", "int"), ("HitRectTop", "int"), ("HitRectLeft", "int"),
    ("HitRectBottom", "int"), ("HitRectRight", "int"),
)


def _sql_literal(text: str) -> str:
    return "'" + text.replace("\\", "\\\\").replace("'", "''") + "'"


def _sql_value(table, record: bytes, index: int, kind: str) -> str:
    if kind == "str":
        text = _dbc_string(table, record, index)
        return _sql_literal(text) if text else "NULL"
    raw = record[index * 4 : index * 4 + 4]
    if kind == "float":
        return repr(struct.unpack("<f", raw)[0])
    value = int.from_bytes(raw, "little")
    # The SQL columns are signed INT; every u32 bit pattern round-trips, but a
    # value at or above 2^31 (a -1 sentinel like CorpseMapID or TimeOfDayOverride)
    # has to be written as its signed form or MySQL rejects it.
    return str(value - (1 << 32) if value >= (1 << 31) else value)


def _sql_rows(table, records: list, columns) -> str:
    lines = []
    for record in records:
        values = [_sql_value(table, record, index, kind) for index, (_name, kind) in enumerate(columns)]
        lines.append("(" + ", ".join(values) + ")")
    return ",\n".join(lines)


def command_sql(args: argparse.Namespace) -> dict:
    """Generate named-column SQL for the SQL-backed server DBC stores."""

    merged = {}
    for name in ("Map", "AreaTable", "WorldMapArea", "WorldMapOverlay"):
        merged[name] = _dbc_rows((STAGING_ROOT / "dbc" / f"{name}.dbc").read_bytes())
    client = {
        name: _dbc_rows(_client_table(args.client / "Data", name))
        for name in ("Map", "AreaTable", "WorldMapArea", "WorldMapOverlay")
    }
    specs = (
        ("areatable_dbc", "AreaTable", AREATABLE_COLUMNS, True),
        ("map_dbc", "Map", MAP_COLUMNS, False),
        ("worldmaparea_dbc", "WorldMapArea", WORLDMAPAREA_COLUMNS, False),
        ("worldmapoverlay_dbc", "WorldMapOverlay", WORLDMAPOVERLAY_COLUMNS, False),
    )
    statements = []
    summary = {}
    for table_name, dbc_name, columns, flying in specs:
        table, rows = merged[dbc_name]
        known = client[dbc_name][1]
        new_ids = sorted(set(rows) - set(known))
        if not new_ids:
            continue
        records = []
        for area_id in new_ids:
            record = bytearray(rows[area_id])
            if flying:
                flags = int.from_bytes(record[16:20], "little")
                struct.pack_into("<I", record, 16, flags | SERVER_AREA_FLAG_ADD)
            records.append(bytes(record))
        column_sql = ", ".join(f"`{name}`" for name, _ in columns)
        statements.append(
            f"-- {table_name}: {len(new_ids)} new row(s)\n"
            f"DELETE FROM `{table_name}` WHERE `ID` IN ({', '.join(str(i) for i in new_ids)});\n"
            f"INSERT INTO `{table_name}` ({column_sql}) VALUES\n"
            f"{_sql_rows(table, records, columns)};"
        )
        summary[table_name] = new_ids
    stamp = "20261005010000000"
    body = (
        "-- OpenAzeroth starting zones: server-side DBC store rows.\n"
        "-- Generated by tools/openazeroth_world_pack.py sql from the same normalized metadata\n"
        "-- as the merged client DBCs. Additive only: no existing row is modified.\n"
        "-- AreaTable Flags carry the mod-fly-anywhere bits (0x4400) that every bound row has;\n"
        "-- donor flags alone would silently disable flying over the imported terrain.\n"
        "\n" + "\n\n".join(statements) + "\n"
    )
    SQL_ROOT.mkdir(parents=True, exist_ok=True)
    staged = SQL_ROOT / f"rev_{stamp}.sql"
    staged.write_text(body, encoding="utf-8", newline="\n")
    result = {
        "staged_sql": str(staged),
        "bytes": len(body),
        "rows": {key: len(value) for key, value in summary.items()},
        "installed": False,
    }
    if getattr(args, "install_sql", False):
        target = PENDING_WORLD_SQL / staged.name
        target.write_text(body, encoding="utf-8", newline="\n")
        result["installed"] = str(target)
    return result

VIEW_ROOT = STAGING_ROOT / "extract-view"
VIEW_DATA = VIEW_ROOT / "Data"
# map_extractor has a hard-coded archive list that stops at patch-5.MPQ; vmap4_extractor
# scans patch.MPQ and patch-1..99. A single numeric name therefore has to be <= 5 for
# the map extractor, and the locale DBC patch has to outrank the client's own
# patch-enUS-6.mpq, which the locale scan reaches first.
VIEW_TERRAIN_SLOT = 5
VIEW_ASSET_SLOT = 6
VIEW_LOCALE_SLOT = 7
VIEW_STOCK_ROOT = ("common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ",
                   "patch.MPQ", "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq")
VIEW_STOCK_LOCALE = ("locale-enUS.MPQ", "expansion-locale-enUS.MPQ", "lichking-locale-enUS.MPQ",
                     "patch-enUS.MPQ", "patch-enUS-2.MPQ", "patch-enUS-3.MPQ",
                     "patch-enUS-5.MPQ", "patch-enUS-6.mpq")


def _link(source: Path, target: Path, log: list) -> str:
    if target.exists():
        return "present"
    try:
        os.link(source, target)
        return "hardlink"
    except OSError:
        pass
    try:
        os.symlink(source, target)
        return "symlink"
    except OSError as exc:
        log.append({"target": str(target), "error": str(exc)})
        return "missing"


def command_extract_view(args: argparse.Namespace) -> dict:
    """Materialize the isolated extraction-client view the map/vmap tools consume."""

    client_data = args.client / "Data"
    storm = Storm(args.dll)
    for directory in (VIEW_DATA, VIEW_DATA / LOCALE, VIEW_DATA / "out"):
        directory.mkdir(parents=True, exist_ok=True)
    log: list = []
    links = {}
    for name in VIEW_STOCK_ROOT:
        source = client_data / name
        if source.is_file():
            links[name] = _link(source, VIEW_DATA / name, log)
    for name in VIEW_STOCK_LOCALE:
        source = client_data / LOCALE / name
        if source.is_file():
            links[f"{LOCALE}/{name}"] = _link(source, VIEW_DATA / LOCALE / name, log)
    for slot, archive in ((VIEW_TERRAIN_SLOT, ARCHIVE_ROOT / f"patch-{args.terrain_letter}.mpq"),
                          (VIEW_ASSET_SLOT, ARCHIVE_ROOT / f"patch-{args.asset_letter}.mpq")):
        if archive.is_file():
            links[f"patch-{slot}.MPQ"] = _link(archive, VIEW_DATA / f"patch-{slot}.MPQ", log)

    # The extractor walks every row of Map.dbc, so the view gets a restricted table
    # with only the in-scope maps; AreaTable stays complete so area lookups resolve.
    map_table, map_rows = _dbc_rows((STAGING_ROOT / "dbc" / "Map.dbc").read_bytes())
    keep = sorted(set(TERRAIN_MAPS) & set(map_rows))
    scoped_map = _build_dbc(
        map_table.fields, map_table.record_size,
        [map_rows[map_id] for map_id in keep], map_table.strings,
    )
    dbc_items = [("DBFilesClient\\Map.dbc", (lambda payload: (lambda: payload))(scoped_map))]
    for name in ("AreaTable", "WorldMapArea"):
        path = STAGING_ROOT / "dbc" / f"{name}.dbc"
        dbc_items.append((f"DBFilesClient\\{name}.dbc", (lambda q: (lambda: q.read_bytes()))(path)))
    locale_archive = VIEW_DATA / LOCALE / f"patch-{LOCALE}-{VIEW_LOCALE_SLOT}.MPQ"
    written = _write_archive(storm, locale_archive, dbc_items, "dbc")
    manifest = {
        "view_root": str(VIEW_ROOT),
        "terrain_slot": VIEW_TERRAIN_SLOT,
        "asset_slot": VIEW_ASSET_SLOT,
        "locale_slot": VIEW_LOCALE_SLOT,
        "links": links,
        "errors": log,
        "dbc_archive": written,
        "map_rows_in_view": keep,
        "notes": [
            "map_extractor reads only common/common-2/lichking/expansion/patch/patch-2..patch-5",
            "vmap4_extractor scans patch.MPQ and patch-1..99",
            f"locale DBC archive is patch-{LOCALE}-{VIEW_LOCALE_SLOT}.MPQ so it outranks the client's patch-enUS-6.mpq",
        ],
    }
    (VIEW_ROOT / "view.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    return manifest

def _tiles_for_rect(rect) -> set:
    """ADT/minimap tile ids under a WorldMapArea rect (left, right, top, bottom).

    WorldMapArea's LocLeft/LocRight are *world Y* and LocTop/LocBottom are *world
    X* - the map frame is transposed against the world axes. Measured on rows the
    client and the terrain agree on:

        Stormwind (terrain X -9600..-8000, Y 0..1600) has dbc (1723, -15, -7996, -9154)
        Elwynn    (terrain X -10133..-6933, Y -2133..2133) has dbc (1535, -1935, -7940, -10254)
        Goldshire's world (-9448, 68) is in tile Az Azeroth_31_49, i.e. A from Y, B from X

    so A comes from left/right and B from top/bottom. Reading them the other way
    round points every zone at the transposed corner of the map, which is where
    the ported Gilneas/Lost Isles minimaps went wrong the first time.
    """

    left, right, top, bottom = rect
    y0, y1 = sorted((left, right))
    x0, x1 = sorted((top, bottom))

    def index(value: float) -> int:
        # Rect bounds sit exactly on tile borders often enough that truncation
        # alone loses (or invents) a column: -533.3333 / 533.3333 is 0.99999996,
        # so 32 - that truncates to 32 instead of 33.
        return int(value + 1e-6)

    return {
        (a, b)
        for a in range(index(32 - y1 / MINIMAP_TILE_SPAN), index(32 - y0 / MINIMAP_TILE_SPAN) + 1)
        for b in range(index(32 - x1 / MINIMAP_TILE_SPAN), index(32 - x0 / MINIMAP_TILE_SPAN) + 1)
    }


def _trs_sections(payload: bytes) -> list:
    """Parse md5translate.trs into [(dir, [(source, target)]), ...] in file order."""

    sections = []
    for line in payload.decode("utf-8").split("\r\n"):
        if not line:
            continue
        if line.startswith("dir:"):
            sections.append((line[4:].strip(), []))
            continue
        if not sections:
            raise ValueError("md5translate.trs entry before any dir:")
        source, target = line.split("\t")
        sections[-1][1].append((source, target))
    return sections


def _trs_bytes(sections: list) -> bytes:
    lines = []
    for name, entries in sections:
        lines.append(f"dir: {name}")
        lines.extend(f"{source}\t{target}" for source, target in entries)
    return ("\r\n".join(lines) + "\r\n").encode("utf-8")


MINIMAP_TILE_PIXELS = 256
# The client maps ground textures onto world coordinates at eight repeats per
# 533.33-yard tile (World\Maps\<map>\<map>_<A>_<B>.adt), so one repeat is
# 66.6667 yards and one MCNK cell (8 per chunk) is a 2x2 pixel block.
GROUND_TEXTURE_SPAN = MINIMAP_TILE_SPAN / 8.0


def _chunk_payloads(data: bytes) -> dict:
    """{tag: payload} for the top-level ADT chunks (MTEX, MDDF, ...)."""

    out = {}
    off = 0
    while off + 8 <= len(data):
        tag = fcc(data, off)[::-1].decode("latin-1")
        size = u32(data, off + 4)
        out.setdefault(tag, data[off + 8 : off + 8 + size])
        off += 8 + size
    return out


def _terrain_tiles_by_area(map_dir: str) -> dict:
    """Staged terrain of one map: area id -> set of (A, B) tiles."""

    out: dict = {}
    for path in sorted((STAGE_TERRAIN / "World" / "Maps" / map_dir).glob("*.adt")):
        stem = path.stem.split("_")
        tile = (int(stem[-2]), int(stem[-1]))
        for chunk in parse_adt(path.read_bytes(), deep=True)["chunks"]:
            out.setdefault(chunk["area"], set()).add(tile)
    return out


def _alpha_plane(data: bytes, at: int, offs_mcal: int, size_mcal: int, rel: int, fmt: str):
    """One 64x64 alpha plane for a texture layer, or None when there is none."""

    import numpy as np

    if not offs_mcal or not rel or rel >= size_mcal:
        return None
    block = ALPHA_BIG_BLOCK if fmt == "big" else ALPHA_SMALL_BLOCK
    payload = data[at + offs_mcal + 8 + rel : at + offs_mcal + 8 + rel + block]
    if len(payload) < block:
        return None
    if fmt == "big":
        return np.frombuffer(payload, np.uint8).reshape(64, 64)
    return np.frombuffer(expand_alpha_block(payload), np.uint8).reshape(64, 64)


def render_terrain_tile(map_dir: str, tile: tuple, loader) -> bytes | None:
    """Draw one 533-yard tile of staged terrain the way the radar shows it.

    Base ground texture plus up to three blended layers, sampled per MCNK cell
    at the client's world texture coordinates. No shadows, water or doodads -
    the client's own minimap tiles are a render of the same ground. None when
    the tile is not staged.
    """

    import numpy as np
    from PIL import Image
    from lib.blp import encode_palettized

    a, b = tile
    path = STAGE_TERRAIN / "World" / "Maps" / map_dir / f"{map_dir}_{a}_{b}.adt"
    if not path.is_file():
        return None
    data = path.read_bytes()
    mtex = [name.decode("latin-1")
            for name in _chunk_payloads(data).get("MTEX", b"").split(b"\0") if name]
    base = 20
    cells, mnk = _mcnk_offsets(data, base + u32(data, base + 4))
    origin_x = (32 - b - 1) * MINIMAP_TILE_SPAN
    origin_y = (32 - a - 1) * MINIMAP_TILE_SPAN
    step = GROUND_TEXTURE_SPAN / 8.0
    canvas = np.zeros((MINIMAP_TILE_PIXELS, MINIMAP_TILE_PIXELS, 3), np.uint8)
    cell_index = (np.arange(8) + 0.5) * 8
    painted = 0
    for index in range(256):
        raw = u32(data, cells + index * 16)
        if not raw:
            continue
        at = raw + mnk
        cx, cy = u32(data, at + 12), u32(data, at + 16)
        layers = u32(data, at + 20)
        offs_mcly, offs_mcal = u32(data, at + 36), u32(data, at + 44)
        size_mcal = u32(data, at + 48)
        if not offs_mcly or layers < 1 or not (0 <= cx < 16 and 0 <= cy < 16):
            continue
        block = (size_mcal - 8) // (layers - 1) if layers > 1 and size_mcal > 8 else 0
        fmt = {ALPHA_BIG_BLOCK: "big", ALPHA_SMALL_BLOCK: "small"}.get(block, "none")
        xs = origin_x + (cx * 8 + np.arange(8) + 0.5) * step
        ys = origin_y + (cy * 8 + np.arange(8) + 0.5) * step
        colour = None
        for layer in range(min(layers, 4)):
            entry = at + offs_mcly + 8 + layer * 16
            texture_id = u32(data, entry)
            if texture_id >= len(mtex):
                continue
            texture = loader(mtex[texture_id])
            if texture is None:
                continue
            ix = np.mod((xs / GROUND_TEXTURE_SPAN * texture.shape[1]).astype(np.int32), texture.shape[1])
            iy = np.mod((ys / GROUND_TEXTURE_SPAN * texture.shape[0]).astype(np.int32), texture.shape[0])
            rgb = texture[np.ix_(iy, ix)].astype(np.float32)
            if layer == 0:
                colour = rgb
                continue
            if colour is None:
                continue
            plane = _alpha_plane(data, at, offs_mcal, size_mcal, u32(data, entry + 8), fmt)
            if plane is None:
                continue
            alpha = plane[np.ix_(cell_index.astype(int), cell_index.astype(int))].astype(np.float32)
            weight = (alpha / 255.0)[:, :, None]
            colour = colour * (1.0 - weight) + rgb * weight
        if colour is None:
            continue
        # Below the water line the client draws water, not the seabed: tint by
        # depth from the MCVT inner 8x8 heights (81 floats past the 9x9 grid).
        offs_mcvt = u32(data, at + 28)
        if offs_mcvt:
            inner = struct.unpack_from("<64f", data, at + offs_mcvt + 8 + 81 * 4)
            depth = np.clip(np.array(inner, np.float32).reshape(8, 8) * -1.0 / 30.0, 0.0, 1.0)
            if depth.any():
                water = np.array([38.0, 74.0, 122.0], np.float32)
                mix = (depth * 0.9)[:, :, None]
                colour = colour * (1.0 - mix) + water * mix
        canvas[cy * 16 : cy * 16 + 16, cx * 16 : cx * 16 + 16] = np.repeat(
            np.repeat(colour.astype(np.uint8), 2, axis=0), 2, axis=1)
        painted += 1
    if not painted:
        return None
    return encode_palettized(Image.fromarray(canvas, "RGB").convert("RGBA"))


def command_client_dbc(args: argparse.Namespace) -> dict:
    """Build the client-facing locale patch.

    Carries the merged DBCs plus what they imply on screen: the world map art for
    every WORLD_MAP_ZONES row the merge added, and the minimap tiles for those
    zones, both taken from the donor whose terrain was installed. The minimap
    entries replace the client's own for the same tiles - the terrain there is
    the donor's now, and the old art is a different map.
    """

    storm = Storm(args.dll)
    client_data = args.client / "Data"
    merged_map = _dbc_rows((DBC_ROOT / "Map.dbc").read_bytes())
    merged_wma = _dbc_rows((DBC_ROOT / "WorldMapArea.dbc").read_bytes())
    merged_overlay = _dbc_rows((DBC_ROOT / "WorldMapOverlay.dbc").read_bytes())

    items = []
    for name in ("Map", "AreaTable", "WorldMapArea", "WorldMapOverlay"):
        path = DBC_ROOT / f"{name}.dbc"
        items.append((f"DBFilesClient\\{name}.dbc", (lambda q: (lambda: q.read_bytes()))(path)))

    directories = {int.from_bytes(row[:4], "little"): _dbc_string(merged_map[0], row, MAP_FIELDS["directory"])
                   for row in merged_map[1].values()}
    wanted: dict = {}
    zones = []
    for wma_id in sorted(WORLD_MAP_ZONES):
        row = merged_wma[1].get(wma_id)
        if row is None:
            raise SystemExit(f"merged WorldMapArea has no row {wma_id} ({WORLD_MAP_ZONES[wma_id]})")
        rect = struct.unpack_from("<4f", row, WMA_FIELDS["left"] * 4)
        map_id = int.from_bytes(row[WMA_FIELDS["map"] * 4:WMA_FIELDS["map"] * 4 + 4], "little")
        map_dir = directories[map_id]
        tiles = _tiles_for_rect(rect)
        wanted.setdefault(map_dir, set()).update(tiles)
        zones.append({"id": wma_id, "name": _dbc_string(merged_wma[0], row, WMA_FIELDS["name"]),
                      "map": map_id, "directory": map_dir, "rect": list(rect), "tiles": len(tiles)})

    # Every overlay row belonging to one of the new zones, keyed by that zone, so
    # each zone's folder can be checked against the textures it is told to draw.
    overlay_textures = {}
    for row in merged_overlay[1].values():
        field = WORLDMAPOVERLAY_FIELDS["map_area"] * 4
        area = int.from_bytes(row[field:field + 4], "little")
        if area in WORLD_MAP_ZONES:
            overlay_textures.setdefault(area, []).append(
                (int.from_bytes(row[:4], "little"),
                 _dbc_string(merged_overlay[0], row, WORLDMAPOVERLAY_FIELDS["texture"])))

    donor = Archive("O", SOURCE_ARCHIVES["O"][0], storm)
    donor.open()
    try:
        entries = donor.entries
        lower = {name.lower() for name in entries}
        art = {}
        for zone in zones:
            prefix = f"interface\\worldmap\\{zone['name'].lower()}\\"
            folder = sorted(name for name in entries if name.lower().startswith(prefix))
            if not folder:
                raise SystemExit(f"donor has no world map art under {prefix}")
            for name in folder:
                items.append((name, (lambda p: (lambda: p))(donor.read(name))))
            missing = []
            for overlay_id, texture in overlay_textures.get(zone["id"], []):
                if not texture:
                    continue
                record = merged_overlay[1][overlay_id]
                wide = -(-int.from_bytes(record[WORLDMAPOVERLAY_FIELDS["width"] * 4:][:4], "little") // 256)
                tall = -(-int.from_bytes(record[WORLDMAPOVERLAY_FIELDS["height"] * 4:][:4], "little") // 256)
                for index in range(1, wide * tall + 1):
                    path = f"{prefix}{texture.lower()}{index}.blp"
                    if path not in lower:
                        missing.append(path)
            if missing:
                raise SystemExit(f"donor art missing for {zone['name']}: {missing[:4]}")
            art[zone["name"]] = {"files": len(folder),
                                 "bytes": sum(entries[name][0] for name in folder)}

        # Every tile the zones' terrain occupies, plus the WorldMapArea rects, so
        # a player standing on the edge of a zone still gets art.
        terrain_by_area: dict = {}
        for zone in zones:
            map_dir = zone["directory"]
            if map_dir not in terrain_by_area:
                terrain_by_area[map_dir] = _terrain_tiles_by_area(map_dir)
            row = merged_wma[1][zone["id"]]
            areas = {int.from_bytes(row[8:12], "little")}
            for overlay_id, _texture in overlay_textures.get(zone["id"], []):
                areas |= {int.from_bytes(merged_overlay[1][overlay_id][f * 4:f * 4 + 4], "little")
                          for f in range(WORLDMAPOVERLAY_FIELDS["area_first"],
                                         WORLDMAPOVERLAY_FIELDS["area_last"] + 1)} - {0}
            for area in areas:
                wanted.setdefault(map_dir, set()).update(terrain_by_area[map_dir].get(area, set()))

        client_files = _client_files(client_data)
        try:
            trs_payload = client_files.find(MINIMAP_TRS)[0]
            sections = _trs_sections(trs_payload)
            if _trs_bytes(sections) != trs_payload:
                raise SystemExit("md5translate.trs does not round-trip; refusing to rewrite it")
            donors = {name.lower(): {source.lower(): (source, target) for source, target in rows}
                      for name, rows in _trs_sections(donor.read(MINIMAP_TRS))}
            known = {name.lower(): (name, rows) for name, rows in sections}

            textures: dict = {}

            def load_texture(name: str):
                """Decode one ground texture once; None when nobody ships it."""

                key = name.lower()
                if key not in textures:
                    payload = None
                    try:
                        payload = client_files.find(name)[0]
                    except FileNotFoundError:
                        try:
                            payload = donor.read(name)
                        except OSError:
                            payload = None
                    image = None
                    if payload:
                        import numpy as np
                        from PIL import Image
                        from lib.blp import decode_blp
                        try:
                            width, height, rgba = decode_blp(payload)
                            image = np.asarray(
                                Image.frombytes("RGBA", (width, height), rgba).convert("RGB"), np.uint8)
                        except Exception:
                            image = None
                    textures[key] = image
                return textures[key]

            shipped = {}
            minimap = {}
            for map_dir in sorted(wanted):
                if map_dir.lower() not in known:
                    sections.append((map_dir, []))
                    known[map_dir.lower()] = (map_dir, sections[-1][1])
                rows = known[map_dir.lower()][1]
                index = {source.lower(): position for position, (source, _) in enumerate(rows)}
                available = donors.get(map_dir.lower(), {})
                added = replaced = absent = rendered = 0
                for tile in sorted(wanted[map_dir]):
                    source = f"{map_dir}\\map{tile[0]}_{tile[1]}.blp"
                    payload = render_terrain_tile(map_dir, tile, load_texture)
                    if payload is not None:
                        target = f"{map_dir}_{tile[0]}_{tile[1]}.blp"
                        rendered += 1
                    else:
                        hit = available.get(source.lower())
                        if hit is None or ("textures\\minimap\\" + hit[1]).lower() not in lower:
                            absent += 1
                            continue
                        target = hit[1]
                        payload = donor.read("Textures\\Minimap\\" + target)
                    if target.lower() in shipped:
                        entry = index.get(source.lower())
                        if entry is not None:
                            rows[entry] = (source, target)
                        continue
                    shipped[target.lower()] = target
                    items.append((f"Textures\\Minimap\\{target}", (lambda p: (lambda: p))(payload)))
                    if source.lower() in index:
                        rows[index[source.lower()]] = (source, target)
                        replaced += 1
                    else:
                        rows.append((source, target))
                        index[source.lower()] = len(rows) - 1
                        added += 1
                minimap[map_dir] = {"tiles": len(wanted[map_dir]), "added": added,
                                    "replaced": replaced, "rendered": rendered,
                                    "no_art": absent}
            items.append((MINIMAP_TRS, (lambda p: (lambda: p))(_trs_bytes(sections))))
        finally:
            client_files.close()
    finally:
        donor.close()

    target = ARCHIVE_ROOT / f"patch-{LOCALE}-{VIEW_LOCALE_SLOT}.MPQ"
    report = _write_archive(storm, target, items, "client-dbc")
    report["install_to"] = str(args.client / "Data" / LOCALE / target.name)
    report["rows"] = {name: _dbc_rows((DBC_ROOT / f"{name}.dbc").read_bytes())[0].count
                      for name in ("Map", "AreaTable", "WorldMapArea", "WorldMapOverlay")}
    report["world_map_zones"] = zones
    report["world_map_art"] = art
    report["minimap"] = minimap
    report["minimap_tiles_shipped"] = len(shipped)
    return report

def command_strip_mfbo(args: argparse.Namespace) -> dict:
    """Clear the MHDR "has MFBO" bit on the staged terrain.

    Every OpenAzeroth tile carries an MFBO height plane (max +3000, min -3000
    everywhere), while the client's original continent tiles had none. Clearing the
    flag makes the client ignore those chunks - the same state the working terrain
    was in. The chunk bytes are left in place and simply stop being referenced.
    """

    changed = []
    for map_id in _scope_maps(args.maps):
        map_dir, _ = TERRAIN_MAPS[map_id]
        for path in sorted((STAGE_TERRAIN / "World" / "Maps" / map_dir).glob("*.adt")):
            data = bytearray(path.read_bytes())
            flags = struct.unpack_from("<I", data, 20)[0]
            if flags & 1:
                struct.pack_into("<I", data, 20, flags & ~1)
                path.write_bytes(bytes(data))
                changed.append(path.stem)
    return {"files_changed": len(changed), "sample": changed[:8]}

def command_manifest(args: argparse.Namespace) -> dict:
    """Assemble the permanent allocation/provenance manifest from live sources."""

    closure_args = argparse.Namespace(dll=args.dll, client=args.client, assets=None)
    manifest = {
        "generated_by": "tools/openazeroth_world_pack.py manifest",
        "handoff": ".agents/plans/openazeroth-starting-zones/openazeroth-starting-zones.HANDOFF.md",
        "sources": command_inventory(args)["sources"],
        "terrain": command_terrain(args),
        "ids": command_ids(args),
        "reservations": {
            "maps": RESERVED_MAPS,
            "areas": sorted(RESERVED_AREAS),
            "area_bits": {"floor": AREA_BIT_FLOOR, "ceiling": AREA_BIT_CEILING},
        },
        "assets": _asset_summary(command_assets(args)),
        "asset_conflicts": {
            key: value
            for key, value in command_collisions(argparse.Namespace(
                dll=args.dll, client=args.client, assets=None, verify=0
            )).items()
            if key in ("policy_note", "summary", "by_kind", "verified_identical", "counts")
        },
        "donor_imports": {
            key: value for key, value in command_imports(closure_args).items() if key != "entries"
        },
        "import_closure": {
            key: value for key, value in command_closure(closure_args).items() if key != "added"
        },
        "dbc": {
            key: value
            for key, value in command_dbc(argparse.Namespace(
                dll=args.dll, client=args.client, maps=""
            )).items()
            if key in ("area_rows_before", "area_rows_added", "area_rows_after", "maps_added",
                       "world_map_area_added", "world_map_area_retargeted", "world_map_zones",
                       "world_map_overlay_added", "area_bits_allocated", "area_bit_range",
                       "fallbacks", "conflicts", "verification")
        },
        "server_sql": {
            key: value
            for key, value in command_sql(argparse.Namespace(
                dll=args.dll, client=args.client, maps="", install_sql=False
            )).items()
        },
        "retained_azeroth_tiles": sorted(retained_azeroth_tiles()),
        "substitutions": [],
        "open_items": [
            "CREATURE\\FROGDUCK\\FROGDUCK.M2 missing (1 placement on Azeroth_30_47)",
            "ERROR_1/2/3.BLP placeholders in use on Azeroth 43_25, 45_25, 46_19, 46_24",
            "DUNGEONS\\CUSTOM\\HUMAN\\MM_CELLAR_WALL_01_NEW.BLP missing (3 Keepwall tunnel WMOs)",
            "458 paths exist in both a donor and the client; the client's copy is kept by default",
            "safe start/service/graveyard/exit coordinates require GM survey after geometry install",
            "vmmap/mmaps extraction tooling availability unverified",
        ],
    }
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "inventory", "terrain", "alpha", "ids", "manifest", "assets", "collisions",
            "imports", "closure", "areas", "dbc", "sql", "extract-view", "strip-mfbo", "client-dbc", "pack",
            "validate-pack", "stage", "validate-stage", "selftest",
        ),
    )
    parser.add_argument("--dll", type=Path, default=DLL_DEFAULT)
    parser.add_argument("--client", type=Path, default=CLIENT_DEFAULT)
    parser.add_argument("--maps", default="")
    parser.add_argument("--assets", type=Path)
    parser.add_argument("--verify", type=int, default=0)
    parser.add_argument("--install-sql", action="store_true")
    parser.add_argument("--only", choices=("both", "terrain", "assets"), default="both")
    parser.add_argument("--terrain-letter", default="Q")
    parser.add_argument("--asset-letter", default="L")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    handlers = {
        "inventory": command_inventory,
        "terrain": command_terrain,
        "alpha": command_alpha,
        "ids": command_ids,
        "manifest": command_manifest,
        "assets": command_assets,
        "collisions": command_collisions,
        "imports": command_imports,
        "closure": command_closure,
        "areas": command_areas,
        "dbc": command_dbc,
        "sql": command_sql,
        "extract-view": command_extract_view,
        "strip-mfbo": command_strip_mfbo,
        "client-dbc": command_client_dbc,
        "pack": command_pack,
        "validate-pack": command_validate_pack,
        "stage": command_stage,
        "validate-stage": command_validate_stage,
        "selftest": command_selftest,
    }
    result = handlers[args.command](args)
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8", newline="\n")
    else:
        print(text)


if __name__ == "__main__":
    main()
