"""Stage the standalone map imports. Writes only under exports/maps-import-20261112/; never touches the client,
the live DB/containers, or any build."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import closure  # noqa: E402
import ctx as C  # noqa: E402
import dbcdelta  # noqa: E402
import lib  # noqa: E402
import sqlgen  # noqa: E402

ARCHIVE_NAMES = {
    "Island": "Patch-ZzzzzzzzzzMapIslandProject.MPQ",
    "Scene": "Patch-ZzzzzzzzzzMapSceneGaming.MPQ",
    "Morza": "Patch-ZzzzzzzzzzMapMorzaCustomMaps.MPQ",
    "Risen": "Patch-ZzzzzzzzzzMapRisenDepths.MPQ",
}
DBC_ARCHIVE = "Patch-ZZZZZZZZZZZZZZZZZZZZZZZZZZMapsImportDbc.MPQ"  # 26 Z: sorts after Patch-Z*25*HousingDev
TRS = "Textures\Minimap\md5translate.trs"


def write_outputs(ctx: C.Ctx) -> None:
    S = C.STAGE
    for sub in ("client", "client-dbc/DBFilesClient", "server/dbc", "server/sql", "server/data", "reports"):
        (S / sub).mkdir(parents=True, exist_ok=True)
    ctx.delta.dump(S / "reports" / "dbc-delta.json")

    # merged DBCs (client baseline = current effective winners, server baseline = live container copies)
    dbc_entries: dict[str, bytes] = {}
    applied_client = dbcdelta.apply_delta(ctx.delta, ctx.client)
    for t in applied_client:
        data = ctx.client[t].to_bytes()
        (S / "client-dbc" / "DBFilesClient" / f"{t}.dbc").write_bytes(data)
        dbc_entries[f"DBFilesClient\{t}.dbc"] = data
    applied_server = dbcdelta.apply_delta(ctx.delta, ctx.server, only=set(C.SERVER_TABLES))
    for t in applied_server:
        (S / "server" / "dbc" / f"{t}.dbc").write_bytes(ctx.server[t].to_bytes())
    ctx.log(f"client DBC rows added: {applied_client}")
    ctx.log(f"server DBC rows added: {applied_server}")

    # minimap translate file: current effective file plus only the new directory blocks
    if ctx.trs_lines:
        cur = (ctx.cf.read(TRS) or b"").decode("utf-8", "replace")
        have = {l.strip().lower() for l in cur.splitlines() if l.lower().startswith("dir:")}
        add = []
        for l in ctx.trs_lines:
            if l.lower().startswith("dir:") and l.strip().lower() in have:
                raise RuntimeError(f"minimap dir already present in the effective client: {l}")
            add.append(l)
        merged = cur.rstrip("\r\n") + "\r\n" + "\r\n".join(add) + "\r\n"
        dbc_entries[TRS] = merged.encode("utf-8")
        (S / "client-dbc" / "md5translate.trs").write_bytes(dbc_entries[TRS])
        ctx.log(f"minimap translate: +{len([l for l in add if not l.lower().startswith('dir:')])} lines "
                f"(effective file provider: {ctx.cf.provider(TRS)})")

    st = lib.storm()
    for old in (S / "client").glob("*.MPQ"):
        old.unlink()
    st.create_archive(S / "client" / DBC_ARCHIVE, dbc_entries)
    for key, files in ctx.assets.items():
        if files:
            st.create_archive(S / "client" / ARCHIVE_NAMES[key], {k: v for k, v in files.items()})
            ctx.log(f"packed {ARCHIVE_NAMES[key]}: {len(files)} files, {sum(map(len, files.values())) / 1e6:.1f} MB")

    # server SQL + tele
    names = [t.name for t in ctx.teles]
    clash = sqlgen.mysql(f"SELECT name FROM game_tele WHERE name IN ({','.join(repr(n) for n in names)});").split()
    if clash:
        ctx.log(f"WARNING game_tele names already in use: {clash}")
    ids = list(range(2000, 2000 + len(ctx.teles)))
    if sqlgen.live_scalar("SELECT COUNT(*) FROM game_tele WHERE id >= 2000") != "0":
        ctx.log("WARNING game_tele ids >= 2000 are already in use")
    rows = [{"id": i, "position_x": t.x, "position_y": t.y, "position_z": t.z, "orientation": t.o, "map": t.map, "name": t.name}
            for i, t in zip(ids, ctx.teles)]
    ctx.sql["maps_game_tele.sql"] = [f"DELETE FROM `game_tele` WHERE `id` BETWEEN {ids[0]} AND {ids[-1]};", sqlgen.emit("game_tele", rows)]
    for name, parts in ctx.sql.items():
        body = "\n".join(p for p in parts if p)
        (S / "server" / "sql" / name).write_text(body + "\n", encoding="utf-8")
    for rel, data in ctx.server_files.items():
        dst = S / "server" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
    (S / "reports" / "stage-report.txt").write_text("\n".join(ctx.report) + "\n", encoding="utf-8")


def main() -> None:
    which = set(sys.argv[2:]) or {"island", "scene", "morza", "risen"}
    scratch = Path(sys.argv[1])
    ctx = C.build_ctx(scratch)
    import maps_small
    if "island" in which:
        maps_small.do_island(ctx)
    if "scene" in which:
        maps_small.do_scene(ctx)
    if "morza" in which:
        maps_small.do_morza_client(ctx)
        import morza_server
        morza_server.do_morza_server(ctx)
    if "risen" in which:
        import risen
        risen.do_risen(ctx)
    write_outputs(ctx)


if __name__ == "__main__":
    main()
