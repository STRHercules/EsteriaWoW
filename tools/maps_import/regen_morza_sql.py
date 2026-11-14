"""Regenerate only server/sql/morza_world.sql (no client reads, no MPQ writes)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ctx as C, maps_small, morza_server

c = C.Ctx(None, {}, {})
maps_small_gy = None
c.sql["morza_world.sql"] = []
# the graveyard rows come from do_morza_client; rebuild them the same way from the existing file header block
old = (C.STAGE / "server" / "sql" / "morza_world.sql").read_text(encoding="utf-8")
head = old.split("-- Morza Island / CustomMaps", 1)[0]
import lib, sqlgen
m_wsl = lib.Dbc((C.SRC / "Morza-Island-Araxia-Server-main" / "Patch-Z-(MPQ)" / "DBFilesClient" / "WorldSafeLocs.dbc").read_bytes())
r = m_wsl.get(maps_small.MORZA_WSL_OLD)
c.sql["morza_world.sql"] += [
    f"DELETE FROM `game_graveyard` WHERE `ID` = {maps_small.MORZA_WSL};",
    sqlgen.emit("game_graveyard", [{"ID": maps_small.MORZA_WSL, "Map": 5000, "x": lib.u2f(r[2]), "y": lib.u2f(r[3]), "z": lib.u2f(r[4]), "Comment": "Morza Island GY"}]),
    f"DELETE FROM `graveyard_zone` WHERE `ID` = {maps_small.MORZA_WSL};",
    sqlgen.emit("graveyard_zone", [{"ID": maps_small.MORZA_WSL, "GhostZone": 4988, "Faction": 0, "Comment": "Morza Island"}]),
]
morza_server.do_morza_server(c)
body = "\n".join(p for p in c.sql["morza_world.sql"] if p)
(C.STAGE / "server" / "sql" / "morza_world.sql").write_text(head + body + "\n", encoding="utf-8")
print("\n".join(c.report))
