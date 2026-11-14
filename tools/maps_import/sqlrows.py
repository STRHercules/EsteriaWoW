"""Tiny INSERT/UPDATE reader for the Morza SQL exports (no MySQL needed, no DELETEs are ever replayed)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Table:
    name: str
    rows: list[dict] = field(default_factory=list)


_INS = re.compile(r"(?is)\b(?:INSERT|REPLACE)\s+(?:IGNORE\s+)?INTO\s+`?(\w+)`?\s*\((.*?)\)\s*VALUES\s*")
_UPD = re.compile(r"(?is)\bUPDATE\s+`?(\w+)`?\s+SET\s+(.*?)\s+WHERE\s+(.*?);")


def _strip_comments(text: str) -> str:
    out = []
    for line in text.splitlines():
        s = line.lstrip()
        if s.startswith("--") or s.startswith("#"):
            continue
        out.append(line)
    return "\n".join(out)


def _tuple_stream(text: str, pos: int):
    """Yield (values, end_pos) for each tuple in a VALUES list starting at pos."""
    n = len(text)
    while pos < n:
        while pos < n and text[pos] in " \t\r\n,":
            pos += 1
        if pos >= n or text[pos] != "(":
            return
        pos += 1
        vals = []
        cur = []
        in_str = False
        depth = 0
        quoted = False
        while pos < n:
            ch = text[pos]
            if in_str:
                if ch == "\\" and pos + 1 < n:
                    nxt = text[pos + 1]
                    cur.append({"n": "\n", "r": "\r", "t": "\t", "0": "\0"}.get(nxt, nxt))
                    pos += 2
                    continue
                if ch == "'":
                    if pos + 1 < n and text[pos + 1] == "'":
                        cur.append("'")
                        pos += 2
                        continue
                    in_str = False
                    pos += 1
                    continue
                cur.append(ch)
                pos += 1
                continue
            if ch == "'":
                if "".join(cur).strip():           # source typo: a value followed by a string with no comma
                    vals.append(_val("".join(cur), quoted))
                cur = []                            # drop whitespace before the opening quote
                in_str = True
                quoted = True
                pos += 1
            elif quoted and ch.isspace():          # whitespace after a closing quote is not part of the value
                pos += 1
            elif ch == "(":
                depth += 1
                cur.append(ch)
                pos += 1
            elif ch == ")" and depth:
                depth -= 1
                cur.append(ch)
                pos += 1
            elif ch == ")":
                vals.append(_val("".join(cur), quoted))
                pos += 1
                break
            elif ch == "," and depth == 0:
                vals.append(_val("".join(cur), quoted))
                cur = []
                quoted = False
                pos += 1
            else:
                cur.append(ch)
                pos += 1
        yield vals, pos
        while pos < n and text[pos] in " \t\r\n":
            pos += 1
        if pos < n and text[pos] == ";":
            return


def _val(raw: str, quoted: bool):
    if quoted:
        return raw
    s = raw.strip()
    if s.upper() == "NULL":
        return None
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return ("RAW", s)


def parse(text: str) -> tuple[dict[str, Table], list[str]]:
    """Returns (tables, unhandled statements). UPDATEs on a single key are folded into the rows."""
    text = _strip_comments(text.lstrip("﻿"))
    tables: dict[str, Table] = {}
    pos = 0
    while True:
        m = _INS.search(text, pos)
        if not m:
            break
        cols = [c.strip().strip("`") for c in m.group(2).split(",")]
        t = tables.setdefault(m.group(1), Table(m.group(1)))
        end = m.end()
        for vals, end in _tuple_stream(text, m.end()):
            if len(vals) < len(cols) and len(vals) >= len(cols) - 3:
                vals = vals + [None] * (len(cols) - len(vals))  # trailing optional columns missing in the export
            if len(vals) != len(cols):
                raise ValueError(f"{m.group(1)}: {len(vals)} values for {len(cols)} columns")
            t.rows.append(dict(zip(cols, vals)))
        pos = max(end, m.end())
    unhandled = []
    for m in _UPD.finditer(text):
        table, sets, where = m.group(1), m.group(2), m.group(3)
        t = tables.get(table)
        wm = re.fullmatch(r"\(?\s*`?(\w+)`?\s*=\s*(-?\d+)\s*\)?", where.strip())
        if not t or not wm:
            unhandled.append(m.group(0)[:200])
            continue
        key, kv = wm.group(1), int(wm.group(2))
        pairs = re.findall(r"`?(\w+)`?\s*=\s*('(?:[^'\\]|\\.)*'|-?[\d.]+|NULL)", sets)
        for r in t.rows:
            if r.get(key) == kv:
                for c, v in pairs:
                    r[c] = None if v == "NULL" else (v[1:-1] if v.startswith("'") else (float(v) if "." in v else int(v)))
    return tables, unhandled


def sql_lit(v) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, tuple):
        return v[1]
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("\\", "\\\\").replace("'", "''").replace("\0", "\\0") + "'"
