#!/usr/bin/env python3
"""Regenerate the addon's Data/*CSV.lua payloads from Data/csv/*.csv.

The 3.3.5 client chokes on very large Lua files, so every payload is emitted as
numbered parts of at most CHUNK_BYTES and reassembled at load time.

Usage:
    python tools/export_addon_data.py "D:/path/to/Interface/AddOns/Battlemon"
"""

import os
import sys

CHUNK_BYTES = 90000

# name -> (csv file, lua file stem). Order matches the .toc load order.
PAYLOADS = [
    ("types", "types.csv", "TypesCSV"),
    ("type_chart", "type_chart.csv", "Type_chartCSV"),
    ("abilities", "abilities.csv", "AbilitiesCSV"),
    ("moves", "moves.csv", "MovesCSV"),
    ("items", "items.csv", "ItemsCSV"),
    ("species", "species.csv", "SpeciesCSV"),
    ("forms", "forms.csv", "FormsCSV"),
]


def chunk_lines(text):
    """Split text into chunks of whole lines, each below CHUNK_BYTES."""
    chunks, cur, size = [], [], 0
    for line in text.splitlines(True):
        n = len(line.encode("utf-8"))
        if cur and size + n > CHUNK_BYTES:
            chunks.append("".join(cur))
            cur, size = [], 0
        cur.append(line)
        size += n
    if cur:
        chunks.append("".join(cur))
    return chunks


def write_payload(addon_dir, key, csv_name, stem):
    src = os.path.join(addon_dir, "Data", "csv", csv_name)
    with open(src, encoding="utf-8", newline="") as fh:
        text = fh.read()
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.endswith("\n"):
        text += "\n"
    if "]]" in text:
        raise SystemExit("%s contains ']]' and cannot be embedded in a long string" % csv_name)

    chunks = chunk_lines(text)
    written = []
    for i, chunk in enumerate(chunks, 1):
        name = stem if len(chunks) == 1 else "%s%d" % (stem, i)
        path = os.path.join(addon_dir, "Data", name + ".lua")
        body = [
            "-- Auto-generated from Data/csv/%s. Do not edit by hand." % csv_name,
            "BattlemonRawCSV = BattlemonRawCSV or {}",
            "BattlemonRawCSV.%s_parts = BattlemonRawCSV.%s_parts or {}" % (key, key),
            "BattlemonRawCSV.%s_parts[%d] = [[%s]]" % (key, i, chunk),
            "",
        ]
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(body))
        written.append("Data\\" + name + ".lua")
    return written


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    addon_dir = sys.argv[1]

    stale = set()
    for key, csv_name, stem in PAYLOADS:
        for f in os.listdir(os.path.join(addon_dir, "Data")):
            if f.startswith(stem) and f.endswith(".lua"):
                stale.add(os.path.join(addon_dir, "Data", f))

    files = []
    for key, csv_name, stem in PAYLOADS:
        written = write_payload(addon_dir, key, csv_name, stem)
        for rel in written:
            stale.discard(os.path.join(addon_dir, rel.replace("Data\\", "Data" + os.sep)))
        files.extend(written)
        print("%-12s -> %d part(s)" % (key, len(written)))

    for path in sorted(stale):
        os.remove(path)
        print("removed stale %s" % os.path.basename(path))

    print("\nTOC block:")
    for f in files:
        print(f)


if __name__ == "__main__":
    main()
