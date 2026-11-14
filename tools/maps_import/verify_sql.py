"""Dry-run the staged SQL into a throwaway schema built with CREATE TABLE ... LIKE acore_world.* (strict mode, twice)."""
import re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sqlgen

d = Path(__file__).resolve().parents[2] / "exports" / "maps-import-20261112" / "server" / "sql"
files = sorted(d.glob("*.sql"))
tabs = set()
for f in files:
    tabs |= set(re.findall(r"(?i)(?:INSERT\s+INTO|DELETE\s+FROM)\s+`?(\w+)`?", f.read_text(encoding="utf-8")))
sqlgen.mysql("DROP DATABASE IF EXISTS mi_verify; CREATE DATABASE mi_verify CHARACTER SET utf8mb4;", db="mysql")
for t in sorted(tabs):
    sqlgen.mysql(f"CREATE TABLE mi_verify.`{t}` LIKE acore_world.`{t}`;", db="mysql")


def run(f):
    r = subprocess.run(["docker", "exec", "-i", "ac-database", "mysql", "-uroot", "-ppassword", "--default-character-set=utf8mb4", "mi_verify"],
                       input=("SET sql_mode='STRICT_TRANS_TABLES';\n" + f.read_text(encoding="utf-8")).encode(), capture_output=True)
    return [l for l in r.stderr.decode(errors="replace").splitlines() if "ERROR" in l]


bad = 0
for label in ("first apply", "re-apply"):
    for f in files:
        e = run(f)
        bad += bool(e)
        print(label, f.name, e[:3] or "ok")
print(sqlgen.mysql("SELECT table_name, table_rows FROM information_schema.tables WHERE table_schema='mi_verify' AND table_rows>0 ORDER BY 1;", db="mysql"))
orph = sqlgen.mysql("SELECT COUNT(*) FROM mi_verify.creature c LEFT JOIN mi_verify.creature_template t ON t.entry=c.id LEFT JOIN acore_world.creature_template l ON l.entry=c.id WHERE t.entry IS NULL AND l.entry IS NULL;", db="mysql").strip()
print("creature spawns without any template:", orph)
sqlgen.mysql("DROP DATABASE mi_verify;", db="mysql")
print("RESULT:", "FAIL" if bad or orph != "0" else "PASS")
