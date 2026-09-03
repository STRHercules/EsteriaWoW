#!/usr/bin/env python3
import argparse
import csv
import sys

MAX_MEDIUMINT_UNSIGNED = 16_777_215


def load_ranges(path):
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    required = {"pool_key", "start_entry", "end_entry", "item_class", "subclass", "inventory_type"}
    if not rows:
        raise ValueError("pool manifest is empty")
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"missing columns: {', '.join(sorted(missing))}")
    parsed = []
    names = set()
    for row in rows:
        key = row["pool_key"].strip()
        if not key or key in names:
            raise ValueError(f"duplicate/empty pool_key: {key!r}")
        names.add(key)
        item = dict(row)
        for field in required - {"pool_key"}:
            item[field] = int(item[field])
        if item["start_entry"] > item["end_entry"]:
            raise ValueError(f"{key}: start_entry > end_entry")
        if item["end_entry"] > MAX_MEDIUMINT_UNSIGNED:
            raise ValueError(f"{key}: entry exceeds MEDIUMINT UNSIGNED")
        parsed.append(item)
    return parsed


def validate_no_overlap(rows):
    ordered = sorted(rows, key=lambda x: x["start_entry"])
    for previous, current in zip(ordered, ordered[1:]):
        if current["start_entry"] <= previous["end_entry"]:
            raise ValueError(
                f"overlap: {previous['pool_key']} [{previous['start_entry']},{previous['end_entry']}] "
                f"and {current['pool_key']} [{current['start_entry']},{current['end_entry']}]"
            )


def main():
    parser = argparse.ArgumentParser(description="Validate procedural Item.dbc reservation ranges.")
    parser.add_argument("manifest")
    args = parser.parse_args()
    try:
        rows = load_ranges(args.manifest)
        validate_no_overlap(rows)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    total = sum(row["end_entry"] - row["start_entry"] + 1 for row in rows)
    print(f"OK: {len(rows)} pools, {total} permanently reserved item entries, no overlaps.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
