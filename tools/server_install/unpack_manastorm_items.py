"""Verify the recovered Manastorm dataset and write a new SQL file; never connects to MySQL."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "data/server/manastorm"


def verified_sql(bundle=BUNDLE):
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    archive = (bundle / manifest["archive"]).resolve()
    if not archive.is_relative_to(bundle.resolve()):
        raise ValueError("Manastorm archive path escapes bundle directory")
    data = archive.read_bytes()
    if hashlib.sha256(data).hexdigest() != manifest["sha256"]:
        raise ValueError("Manastorm archive checksum mismatch")
    sql = gzip.decompress(data)
    if len(sql) != manifest["sql_bytes"] or hashlib.sha256(sql).hexdigest() != manifest["sql_sha256"]:
        raise ValueError("Manastorm SQL checksum mismatch")
    return sql


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="New SQL file; existing files are never overwritten")
    args = parser.parse_args()
    try:
        sql = verified_sql()
        if args.output:
            with args.output.open("xb") as output:
                output.write(sql)
            print(f"Verified Manastorm item SQL written to {args.output}")
        else:
            print(f"Manastorm item dataset verified ({len(sql):,} SQL bytes)")
    except (OSError, ValueError, gzip.BadGzipFile) as error:
        raise SystemExit(str(error))
