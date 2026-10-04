"""Ship the Vulpera HD model's missing eye textures into Patch-C and PATCH-X.

The donor M2 files reference:
    character\\vulpera\\male\\VulperaMale_DK_Eyes.blp
    Character\\Vulpera\\female\\vulperafemale_DK_Eyes.blp
Neither exists in any archive, so the client binds nothing and renders the
affected surfaces black. Both files ship inside the donor's Vulpera_HD folder.
"""

from __future__ import annotations

import argparse
import datetime
import gc
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm

B = chr(92)
DONOR_ROOT = Path(r"G:\\Esteria\\RaceWork\\Latest\\patch-p\\Character\\Vulpera_HD")
DATA = REPO / "3.3.5a - Dev" / "Data"
TARGET_ARCHIVES = ("Patch-C.MPQ", "PATCH-X.MPQ")

ENTRIES = {
    B.join(["character", "vulpera", "male", "VulperaMale_DK_Eyes.blp"]):
        DONOR_ROOT / "Male" / "VulperaMale_DK_Eyes.blp",
    B.join(["Character", "Vulpera", "female", "vulperafemale_DK_Eyes.blp"]):
        DONOR_ROOT / "Female" / "vulperafemale_DK_Eyes.blp",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DATA)
    parser.add_argument("--archives", nargs="*", default=list(TARGET_ARCHIVES))
    parser.add_argument("--backup-root", type=Path, default=REPO / "3.3.5a - Dev" / "Backups")
    parser.add_argument("--staging", type=Path, default=REPO / "var" / "vulpera-eyes-stage")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    payload = {}
    for key, path in ENTRIES.items():
        if not path.exists():
            raise SystemExit("donor file missing: %s" % path)
        payload[key] = path.read_bytes()
        print("stage %8d bytes  %s" % (len(payload[key]), key))

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for name in args.archives:
        live = args.data_dir / name
        if not live.exists():
            print("skip %s: not found" % name)
            continue
        staging = args.staging / name
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True)
        staged = staging / name
        print("=== %s: copying (%.0f MB)" % (name, live.stat().st_size / 1e6))
        shutil.copy2(live, staged)
        storm = Storm(DLL_DEFAULT)
        storm.replace_archive_entries(staged, payload)
        del storm
        gc.collect()

        check = Storm(DLL_DEFAULT)
        handle = check.open_archive(staged)
        try:
            names = {n.casefold(): n for n, *_ in check.list_files(handle)}
        finally:
            check.dll.SFileCloseArchive(handle)
            del check
            gc.collect()
        for key in payload:
            if key.casefold() not in names:
                raise SystemExit("VERIFY FAIL: %s missing from %s" % (key, name))
        print("    verify: both eye textures present in staged %s" % name)

        if args.dry_run:
            print("    dry run: staged at %s" % staged)
            continue
        backup_dir = args.backup_root / ("%s-before-vulpera-eyes-%s" % (name.lower().replace(".mpq", ""), stamp))
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / live.name
        shutil.copy2(live, backup)
        os.replace(staged, live)
        shutil.rmtree(staging, ignore_errors=True)
        print("    installed %s (%.0f MB); rollback %s" % (live, live.stat().st_size / 1e6, backup))

if __name__ == "__main__":
    main()
