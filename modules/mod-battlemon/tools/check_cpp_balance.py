# -*- coding: utf-8 -*-
"""Cheap structural sanity check for the module sources.

Not a compiler: it only strips comments and literals and confirms the bracket
nesting still closes, which catches the kind of slip a hand edit introduces.

Usage:
    python tools/check_cpp_balance.py src/BattlemonMgr.cpp ...
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PAIRS = {"{": "}", "(": ")", "[": "]"}


def strip(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r'"(\\.|[^"\\])*"', '""', text)
    text = re.sub(r"'(\\.|[^'\\])*'", "''", text)
    return text


def check(path: Path) -> bool:
    text = strip(path.read_text(encoding="utf-8"))
    stack = []
    line = 1
    for ch in text:
        if ch == "\n":
            line += 1
        elif ch in PAIRS:
            stack.append((ch, line))
        elif ch in PAIRS.values():
            if not stack or PAIRS[stack[-1][0]] != ch:
                print(f"{path.name}: unexpected '{ch}' on line {line}")
                return False
            stack.pop()
    if stack:
        ch, line = stack[-1]
        print(f"{path.name}: unclosed '{ch}' from line {line}")
        return False
    print(f"OK    {path.name}")
    return True


def main() -> None:
    paths = [Path(p) for p in sys.argv[1:]]
    if not paths:
        raise SystemExit(__doc__)
    if not all(check(p) for p in paths):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
