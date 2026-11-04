#!/usr/bin/env python3
"""Bring Conquest of Azeroth class code into src/coa/.

  python port_coa.py --coa-core R:/.../azerothcore-wotlk-coa AscensionBarbarian.cpp ...

Copies each named file from the CoA core's src/server/coa, includes CoAPort.h,
and rewrites the plain class tests ("unit->getClass() == CLASS_X" and "!=")
into HasCoAKit. Whatever class test it cannot rewrite mechanically (a switch
on getClass(), a class stored or compared some other way) is listed with its
line so it is fixed by hand. Re-running overwrites the copies, so hand edits
belong in a file this does not copy, or are re-applied after.
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(os.path.dirname(HERE), "src", "coa")

EQ = re.compile(r"([A-Za-z_][\w>\-.()]*?)->getClass\(\)\s*==\s*(CLASS_[A-Z_]+|\d+)\b")
NE = re.compile(r"([A-Za-z_][\w>\-.()]*?)->getClass\(\)\s*!=\s*(CLASS_[A-Z_]+|\d+)\b")


def port(text):
    text = NE.sub(r"!HasCoAKit(\1, \2)", text)
    text = EQ.sub(r"HasCoAKit(\1, \2)", text)
    if '#include "CoAPort.h"' not in text:
        text = re.sub(r'(#include "[^"]+"\n)', r'\1#include "CoAPort.h"\n', text, count=1)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coa-core", required=True)
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()
    src = os.path.join(args.coa_core, "src", "server", "coa")
    left = 0
    for name in args.files:
        text = open(os.path.join(src, name), encoding="utf-8").read()
        out = port(text)
        with open(os.path.join(DEST, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(out)
        for no, line in enumerate(out.split("\n"), 1):
            if "getClass()" in line:
                print("%s:%d: %s" % (name, no, line.strip()))
                left += 1
    print("%d file(s) ported, %d class test(s) left for hand edits" % (len(args.files), left))
    return 0


if __name__ == "__main__":
    sys.exit(main())
