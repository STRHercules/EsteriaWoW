"""Import retail Garr*/CharShipment* DB2 tables (wago.tools CSV) into acore_world as db2_<snake_name>."""
import csv
import re
import subprocess
import sys
from pathlib import Path

CSV_DIR = Path(r"G:\risServer\_ref\garr_csv")
OUT_SQL = Path(__file__).resolve().parent.parent / "data" / "sql" / "db-world" / "garrison_db2.sql"
MYSQL = [r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe", "--host=127.0.0.1", "-uacore", "-pacore", "--default-character-set=utf8mb4", "acore_world"]

INT_RE = re.compile(r"^-?\d+$")
FLOAT_RE = re.compile(r"^-?(\d+\.\d*|\.\d+|\d+)([eE][-+]?\d+)?$")


def snake(name: str) -> str:
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", name).lower()


def column_type(values):
    if all(INT_RE.match(v) for v in values if v != ""):
        ints = [int(v) for v in values if v != ""]
        if not ints or (min(ints) >= -2**31 and max(ints) < 2**31):
            return "INT", int
        return "BIGINT", int
    if all(FLOAT_RE.match(v) for v in values if v != ""):
        return "FLOAT", float
    return "TEXT", str


def quote(value, kind):
    if kind is str:
        return "'" + value.replace("\\", "\\\\").replace("'", "\\'").replace("\r", "\\r").replace("\n", "\\n") + "'"
    return value if value != "" else "0"


def table_sql(path: Path) -> str:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    header, data = rows[0], rows[1:]
    columns = [snake(h.replace("_lang", "")) for h in header]
    types = [column_type([r[i] for r in data]) for i in range(len(header))]
    table = "db2_" + snake(path.stem)
    out = [f"DROP TABLE IF EXISTS `{table}`;", f"CREATE TABLE `{table}` ("]
    out += [f"  `{c}` {t[0]} NOT NULL{' DEFAULT 0' if t[0] != 'TEXT' else ''}," for c, t in zip(columns, types)]
    out.append("  PRIMARY KEY (`id`)\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    for start in range(0, len(data), 500):
        chunk = data[start:start + 500]
        values = ",\n".join("(" + ",".join(quote(v, t[1]) for v, t in zip(r, types)) + ")" for r in chunk)
        out.append(f"INSERT INTO `{table}` (`" + "`,`".join(columns) + f"`) VALUES\n{values};")
    print(f"{table}: {len(data)} rows, {len(columns)} columns")
    return "\n".join(out)


def game_objects_csv() -> Path:
    """GameObjects.db2 rows GarrisonMgr reads: plots/buildings/shipment chests and anything owned by a garrison map."""
    src = Path(r"G:\risServer\_ref\wago_GameObjects.csv")
    out = CSV_DIR / "GameObjects.csv"
    maps = {"1152", "1330", "1153", "1158", "1331", "1159"}
    with src.open(encoding="utf-8", newline="") as f, out.open("w", encoding="utf-8", newline="") as o:
        reader = csv.DictReader(f)
        writer = csv.DictWriter(o, fieldnames=reader.fieldnames)
        writer.writeheader()
        for r in reader:
            if r["TypeID"] in ("38", "39", "45") or r["OwnerID"] in maps:
                writer.writerow(r)
    return out


def main():
    game_objects_csv()
    sql = "\n\n".join(table_sql(p) for p in sorted(CSV_DIR.glob("*.csv"))) + "\n"
    OUT_SQL.parent.mkdir(parents=True, exist_ok=True)
    OUT_SQL.write_text(sql, encoding="utf-8")
    print(f"wrote {OUT_SQL}")
    if "--apply" in sys.argv:
        subprocess.run(MYSQL, input=sql.encode("utf-8"), check=True)
        print("applied to acore_world")


if __name__ == "__main__":
    main()
