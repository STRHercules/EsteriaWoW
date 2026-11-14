"""Staging context: effective-client access, DBC baselines (client and live server), ID allocation, reports."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import closure
import dbcdelta
import lib

REPO = lib.REPO
STAGE = REPO / "exports" / "maps-import-20261112"
CLIENT_DATA = Path(r"G:\3.3.5a - Dev\Data")
SRC = REPO / "NewModels" / "_Maps"

CLIENT_TABLES = ["Map", "AreaTable", "AreaTrigger", "WorldSafeLocs", "WorldMapArea", "WorldMapOverlay", "AreaPOI",
                 "LoadingScreens", "Light", "LightParams", "LightSkybox", "LightIntBand", "LightFloatBand",
                 "ZoneMusic", "ZoneIntroMusicTable", "SoundAmbience", "SoundEntries", "SoundProviderPreferences"]
SERVER_TABLES = ["Map", "AreaTable", "AreaTrigger", "WorldSafeLocs"]


@dataclass
class Tele:
    name: str
    map: int
    x: float
    y: float
    z: float
    o: float = 0.0
    note: str = ""


@dataclass
class Ctx:
    cf: lib.ClientFiles
    client: dict[str, lib.Dbc]
    server: dict[str, lib.Dbc]
    delta: dbcdelta.Delta = field(default_factory=dbcdelta.Delta)
    assets: dict[str, dict[str, bytes]] = field(default_factory=dict)   # archive key -> {path: bytes}
    trs_lines: list[str] = field(default_factory=list)
    sql: dict[str, list[str]] = field(default_factory=dict)             # sql file name -> statements
    server_files: dict[str, bytes] = field(default_factory=dict)         # relative path under STAGE/server -> bytes
    teles: list[Tele] = field(default_factory=list)
    report: list[str] = field(default_factory=list)
    used_bits: set[int] = field(default_factory=set)

    def log(self, msg: str) -> None:
        print(msg, flush=True)
        self.report.append(msg)

    def used_ids(self, table: str) -> set[int]:
        s = set()
        if table in self.client:
            s |= self.client[table].ids()
        if table in self.server:
            s |= self.server[table].ids()
        s |= {r[0] for r in self.delta.rows.get(table, [])}
        return s

    def new_bit(self) -> int:
        b = 1
        while b in self.used_bits:
            b += 1
        if b >= 4096:
            raise RuntimeError("no free AreaBit left (exploration bitfield is 4096 wide)")
        self.used_bits.add(b)
        return b

    def exists_in(self, table: str, rid: int) -> bool:
        return table in self.client and self.client[table].get(rid) is not None


def docker_cp(name: str, dst: Path) -> bytes:
    dst.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["docker", "cp", f"ac-worldserver:/azerothcore/env/dist/data/dbc/{name}.dbc", str(dst)],
                       capture_output=True)
    if r.returncode:
        raise RuntimeError(f"docker cp {name}: {r.stderr.decode(errors='replace')}")
    return dst.read_bytes()


def build_ctx(scratch: Path) -> Ctx:
    cf = lib.ClientFiles(CLIENT_DATA, scratch).open()
    client = {}
    for t in CLIENT_TABLES:
        b = cf.read(f"DBFilesClient\\{t}.dbc")
        if b is not None:
            client[t] = lib.Dbc(b)
    server = {}
    for t in SERVER_TABLES:
        server[t] = lib.Dbc(docker_cp(t, scratch / "serverdbc" / f"{t}.dbc"))
    ctx = Ctx(cf, client, server)
    ctx.used_bits = {r[3] for r in client["AreaTable"].rows} | {r[3] for r in server["AreaTable"].rows}
    ctx.used_bits.discard(0)
    for t, d in client.items():
        ctx.log(f"baseline client {t}: {len(d.rows)} rows (provider {cf.provider('DBFilesClient/' + t + '.dbc')})")
    for t, d in server.items():
        ctx.log(f"baseline server {t}: {len(d.rows)} rows")
    return ctx


def filter_assets(ctx: Ctx, key: str, pack: dict[str, bytes], always_ship_prefixes: tuple[str, ...] = ()) -> None:
    """Ground rule: ship only paths that are new to the client. Same bytes are deduped, different bytes keep
    Esteria's existing file (nothing stock or existing is ever replaced)."""
    out = ctx.assets.setdefault(key, {})
    same = diff = skipped = 0
    kept: list[str] = []
    for path, data in pack.items():
        k = lib.norm(path)
        base = k.rsplit("/", 1)[-1]
        if base in ("thumbs.db", "(listfile)", "(attributes)") or k.startswith("dbfilesclient/") or k.endswith(".trs"):
            skipped += 1
            continue
        if k.startswith(always_ship_prefixes) and not ctx.cf.has(path):
            out[path] = data
            continue
        if ctx.cf.has(path):
            cur = ctx.cf.read(path)
            if cur == data:
                same += 1
            else:
                diff += 1
                kept.append(f"{path}  esteria={len(cur)}B  pack={len(data)}B")
            continue
        out[path] = data
    if kept:
        (STAGE / "reports").mkdir(parents=True, exist_ok=True)
        (STAGE / "reports" / f"kept-existing-{key}.txt").write_text(chr(10).join(kept) + chr(10), encoding="utf-8")
    ctx.log(f"[{key}] ships {len(out)} files; dropped identical {same}, kept-existing(different) {diff}, ignored {skipped}")


def closure_report(ctx: Ctx, key: str, adts: list[tuple[str, bytes]]) -> None:
    shipped = {lib.norm(p): d for p, d in ctx.assets.get(key, {}).items()}

    def read(p: str):
        k = lib.norm(p)
        return shipped[k] if k in shipped else ctx.cf.read(p)

    found, missing = closure.compute(adts, read)
    ctx.log(f"[{key}] dependency closure from {len(adts)} ADT: {len(found)} files resolved, {len(missing)} missing")
    for m in sorted(missing)[:40]:
        ctx.log(f"    MISSING: {m}")
