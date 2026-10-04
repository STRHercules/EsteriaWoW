import dataclasses
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from wotlkconv.casc.config import BuildInfo

ROOT = Path(r"G:\RetroPorterWork\vulpera")
REPO = Path(r"R:\Users\Zach\Documents\GitHub\RetroPorter")
SOURCE = Path(r"G:\Blizzard\World of Warcraft")
EXPECTED = ("wow", "12.1.0.69933", "dcfc90fffd79ba00406ae46f5f657592")
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)


def verify_source():
    build = BuildInfo.load(SOURCE, "wow")
    actual = (build.product, build.version, build.build_key)
    if actual != EXPECTED:
        raise RuntimeError(f"Retail build changed: expected {EXPECTED}, found {actual}")
    return build


if __name__ == "__main__":
    build = verify_source()
    pin = dataclasses.asdict(build)
    pin["source_root"] = str(SOURCE)
    pin["build_info_sha256"] = hashlib.sha256((SOURCE / ".build.info").read_bytes()).hexdigest()
    (REPORTS / "source-pin.json").write_text(json.dumps(pin, indent=2) + "\n", encoding="utf-8")
    stages = {
        "check": ["unittest", "discover", "-s", "tests", "-p", "test_vulpera.py"],
        "extract": ["retroporter", "extract-db2", "--race", "vulpera"],
        "discover": ["retroporter", "discover", "--race", "vulpera"],
        "plan": ["retroporter", "plan-assets", "--race", "vulpera"],
        "dryrun": ["retroporter", "convert-assets", "--race", "vulpera", "--dry-run"],
        "convert": ["retroporter", "convert-assets", "--race", "vulpera"],
    }
    for stage in sys.argv[1:]:
        verify_source()
        command = ["rtk", "python", "-m", *stages[stage]]
        log_path = REPORTS / f"{stage}.log"
        print(f"START {stage}: {subprocess.list2cmdline(command)}", flush=True)
        with log_path.open("w", encoding="utf-8") as log:
            log.write(subprocess.list2cmdline(command) + "\n")
            log.flush()
            result = subprocess.run(command, cwd=REPO, stdout=log, stderr=subprocess.STDOUT)
        verify_source()
        print(f"END {stage}: exit={result.returncode} log={log_path}", flush=True)
        if result.returncode:
            raise SystemExit(result.returncode)
