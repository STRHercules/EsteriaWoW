import json
from pathlib import Path
import subprocess

from run_source import REPO, REPORTS, ROOT, verify_source


if __name__ == "__main__":
    verify_source()
    inventory = json.loads((REPORTS / "source-inventory.json").read_text(encoding="utf-8"))
    sources = [row["raw_path"] for row in inventory["assets"] if row.get("source_layout") == "direct-blte"]
    command = [
        "rtk", "python", "-m", "wotlkconv", "convert", *sources,
        "--listfile", str(Path.home() / ".cache" / "wotlkconv" / "community-listfile.csv"),
        "--path-prefix", r"custom\vulpera", "-o", str(ROOT / "output" / "patch-root" / "custom" / "vulpera"),
        "--report", str(REPORTS / "asset-convert-recovered.json"), "-j", "4",
    ]
    with (REPORTS / "convert-recovered.log").open("w", encoding="utf-8") as log:
        log.write(subprocess.list2cmdline(command) + "\n")
        log.flush()
        result = subprocess.run(command, cwd=REPO, stdout=log, stderr=subprocess.STDOUT)
    verify_source()
    print(f"Recovered source conversions: {len(sources)}, exit={result.returncode}")
    raise SystemExit(result.returncode)
