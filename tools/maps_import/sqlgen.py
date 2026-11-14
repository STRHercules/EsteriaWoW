"""Emit INSERTs shaped to the live acore_world schema (read-only SHOW COLUMNS / SELECT)."""

from __future__ import annotations

import subprocess
from functools import lru_cache

import sqlrows


def mysql(sql: str, db: str = "acore_world") -> str:
    r = subprocess.run(["docker", "exec", "-i", "ac-database", "mysql", "-uroot", "-ppassword", "--default-character-set=utf8mb4",
                        "-N", db], input=sql.encode("utf-8"), capture_output=True)
    out = (r.stdout + r.stderr).decode("utf-8", "replace")
    return "\n".join(l for l in out.splitlines() if "Using a password" not in l)


@lru_cache(maxsize=None)
def live_columns(table: str) -> list[tuple[str, str, bool, str | None]]:
    """(name, type, nullable, default)."""
    out = mysql(f"SHOW COLUMNS FROM `{table}`;")
    cols = []
    for l in out.splitlines():
        p = l.split("\t")
        if len(p) < 5 or l.startswith("ERROR"):
            continue
        cols.append((p[0], p[1], p[2] == "YES", None if p[4] == "NULL" else p[4]))
    if not cols:
        raise RuntimeError(f"no live table {table}: {out[:200]}")
    return cols


def live_ids(table: str, col: str, ids) -> set[int]:
    ids = sorted({int(i) for i in ids})
    if not ids:
        return set()
    found: set[int] = set()
    for i in range(0, len(ids), 500):
        chunk = ids[i:i + 500]
        out = mysql(f"SELECT `{col}` FROM `{table}` WHERE `{col}` IN ({','.join(map(str, chunk))});")
        found |= {int(x) for x in out.split() if x.lstrip("-").isdigit()}
    return found


def live_scalar(sql: str):
    out = mysql(sql).strip()
    return None if not out or out == "NULL" else out


def emit(table: str, rows: list[dict], renames: dict[str, str] | None = None, header: bool = True) -> str:
    """INSERT statement for rows (dicts). Source columns absent from the live table are dropped; live NOT NULL
    columns without a default that the source lacks get 0 / ''. `renames` maps source column -> live column."""
    if not rows:
        return ""
    cols = live_columns(table)
    names = [c[0] for c in cols]
    renames = renames or {}
    use = list(names)
    out_rows = []
    dropped = set()
    for r in rows:
        rr = {renames.get(k, k): v for k, v in r.items()}
        dropped |= {k for k in rr if k not in names}
        out_rows.append(rr)
    # live columns we can omit (nullable or defaulted) are left to MySQL; the rest are filled
    chosen = []
    for n, typ, nullable, default in cols:
        present = any(n in rr for rr in out_rows)
        if present:
            chosen.append(n)
        elif not nullable and default is None and "auto_increment" not in typ:
            chosen.append(n)
    lines = []
    for rr in out_rows:
        vals = []
        for n in chosen:
            if n in rr and rr[n] is None and not next(c for c in cols if c[0] == n)[2]:
                typ = next(c[1] for c in cols if c[0] == n)
                dflt = next(c[3] for c in cols if c[0] == n)
                numeric = any(x in typ for x in ("int", "float", "double", "decimal"))
                vals.append(sqlrows.sql_lit(dflt) if dflt is not None and not numeric else (dflt or "0") if numeric else "''")
            elif n in rr:
                vals.append(sqlrows.sql_lit(rr[n]))
            else:
                typ = next(c[1] for c in cols if c[0] == n)
                vals.append("0" if any(t in typ for t in ("int", "float", "double", "decimal")) else "''")
        lines.append("(" + ", ".join(vals) + ")")
    head = f"-- {table}: {len(rows)} rows" + (f" (source-only columns dropped: {', '.join(sorted(dropped))})" if dropped else "") + "\n" if header else ""
    return head + f"INSERT INTO `{table}` (" + ", ".join(f"`{c}`" for c in chosen) + ") VALUES\n" + ",\n".join(lines) + ";\n"
