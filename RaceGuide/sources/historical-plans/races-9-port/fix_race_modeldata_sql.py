"""Sync the server's CreatureModelData rows for the ported races with the client.

Clients and servers share the model geometry: Patch-Y now carries Eunoia's own
collision/mount/bounding-box numbers for the 18 race models, and the server's
`creaturemodeldata_dbc` overlay must say the same thing. Field types are taken from the
table schema so float columns get real floats, not their bit patterns.
"""

from __future__ import annotations

import argparse
import struct
import subprocess
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / ".agents/plans/races-9-port"))
sys.path.insert(0, str(REPO / "tools"))
from inspect_client_races import Client  # noqa: E402

OUT = REPO / "modules/mod-custom-server/data/sql/updates/pending_db_world/rev_1787850000006_race_modeldata.sql"
MODEL_ROWS = list(range(3632, 3658))

FIELDS = {
    1: "Flags", 3: "SizeClass", 4: "ModelScale", 5: "BloodID", 6: "FootprintTextureID",
    7: "FootprintTextureLength", 8: "FootprintTextureWidth", 9: "FootprintParticleScale",
    10: "FoleyMaterialID", 11: "FootstepShakeSize", 12: "DeathThudShakeSize", 13: "SoundID",
    14: "CollisionWidth", 15: "CollisionHeight", 16: "MountHeight",
    17: "GeoBoxMinX", 18: "GeoBoxMinY", 19: "GeoBoxMinZ",
    20: "GeoBoxMaxX", 21: "GeoBoxMaxY", 22: "GeoBoxMaxZ",
    23: "WorldEffectScale", 24: "AttachedEffectScale",
    25: "MissileCollisionRadius", 26: "MissileCollisionPush", 27: "MissileCollisionRaise",
}


def query(sql: str) -> list[list[str]]:
    proc = subprocess.run(
        ["docker", "exec", "ac-database", "mysql", "-uroot", "-ppassword", "acore_world", "-N", "-e", sql],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.split("\t") for line in proc.stdout.splitlines() if line.strip()]


def as_float(value: int) -> float:
    return struct.unpack("<f", struct.pack("<I", value & 0xFFFFFFFF))[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    types = {name: kind for name, kind, *_ in query("SHOW COLUMNS FROM creaturemodeldata_dbc;")}
    models = Client().table("DBFilesClient\\CreatureModelData.dbc")
    rows = {r[0]: r for r in models.rows}

    statements = ["-- Race model geometry for the ported races (collision, mount height, bounding box)."]
    for row_id in MODEL_ROWS:
        row = rows.get(row_id)
        if row is None:
            continue
        parts = []
        for index, column in FIELDS.items():
            if "float" in types[column]:
                parts.append(f"`{column}` = {round(as_float(row[index]), 6)}")
            else:
                parts.append(f"`{column}` = {row[index]}")
        statements.append(f"UPDATE `creaturemodeldata_dbc` SET {', '.join(parts)} WHERE `ID` = {row_id};")

    payload = "\n".join(statements) + "\n"
    OUT.write_text(payload, encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)} ({len(statements) - 1} updates)")

    if args.apply:
        proc = subprocess.run(
            ["docker", "exec", "-i", "ac-database", "mysql", "-uroot", "-ppassword", "acore_world"],
            input=payload,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise SystemExit(f"apply failed: {proc.stderr}")
        print("applied to acore_world")


if __name__ == "__main__":
    main()
