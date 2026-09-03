#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path
from validate_client_pool import load_ranges, validate_no_overlap


def main():
    parser = argparse.ArgumentParser(description="Expand range reservations into one row per Item.dbc entry.")
    parser.add_argument("ranges")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = load_ranges(args.ranges)
    validate_no_overlap(rows)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["entry", "pool_key", "item_class", "subclass", "inventory_type"])
        count = 0
        for row in rows:
            for entry in range(row["start_entry"], row["end_entry"] + 1):
                writer.writerow([entry, row["pool_key"], row["item_class"], row["subclass"], row["inventory_type"]])
                count += 1
    print(f"Wrote {count} Item.dbc reservation rows to {output}")


if __name__ == "__main__":
    main()
