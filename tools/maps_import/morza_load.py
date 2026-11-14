"""Load the Morza Island server SQL into a scratch schema (mi_morza) and report table/key facts.

Nothing here touches acore_world: the scratch schema is created with CREATE TABLE ... LIKE, so it always
mirrors the live column layout, and SQL that does not fit that layout fails loudly.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\NewModels\_Maps\Morza-Island-Araxia-Server-main")
SCHEMA = "mi_morza"
THIES = ROOT / "Azerothcore Update by Thiesant"
# Thiesant's update replaces these folders; Quest / Plants / DBC Table Info only exist as originals.
FOLDERS = [(THIES / d) for d in ("Concert", "Critters", "Enemies", "Gambling Hall", "Game Objects", "Items",
                                 "Town Folk", "Trainer", "Vendor")] + [ROOT / d for d in ("Quest", "Plants", "DBC Table Info", "Items")]


def mysql(sql: str, db: str | None = None, force: bool = False) -> str:
    cmd = ["docker", "exec", "-i", "ac-database", "mysql", "-uroot", "-ppassword", "--default-character-set=utf8mb4", "-N"]
    if force:
        cmd.append("--force")
    if db:
        cmd.append(db)
    r = subprocess.run(cmd, input=sql.encode("utf-8"), capture_output=True)
    out = (r.stdout + r.stderr).decode("utf-8", "replace")
    return "\n".join(l for l in out.splitlines() if "Using a password" not in l)


def clean(text: str) -> str:
    text = text.lstrip("\ufeff")
    return re.sub(r"(?m)^--(?=\S)", "-- ", text)  # MySQL needs whitespace after the comment dashes


def main() -> None:
    tables = set()
    for d in FOLDERS:
        for p in d.rglob("*.sql"):
            t = p.read_text(encoding="utf-8", errors="replace")
            tables |= set(re.findall(r"(?i)(?:INSERT\s+(?:IGNORE\s+)?INTO|REPLACE\s+INTO|DELETE\s+FROM|UPDATE)\s+`?(\w+)`?", t))
    print("tables:", sorted(tables))
    mysql(f"DROP DATABASE IF EXISTS {SCHEMA}; CREATE DATABASE {SCHEMA} CHARACTER SET utf8mb4;")
    for t in sorted(tables):
        out = mysql(f"CREATE TABLE {SCHEMA}.`{t}` LIKE acore_world.`{t}`;")
        if out.strip():
            print("  create", t, out.strip()[:200])
    errors = 0
    files = 0
    for d in FOLDERS:
        for p in sorted(d.glob("*.sql")):
            files += 1
            out = mysql("SET FOREIGN_KEY_CHECKS=0; SET sql_mode='';\n" + clean(p.read_text(encoding="utf-8", errors="replace")),
                        db=SCHEMA, force=True)
            if "ERROR" in out:
                errors += 1
                print("ERR", p.relative_to(ROOT), out.strip()[:300])
    print("files", files, "with errors", errors)
    print(mysql("SELECT table_name, table_rows FROM information_schema.tables WHERE table_schema='mi_morza' ORDER BY 1;"))


if __name__ == "__main__":
    main()
