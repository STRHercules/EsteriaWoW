#!/usr/bin/env python3
"""Deploy the Battlemon addon code from one client install to another.

Copies the Lua/TOC and the Data/csv catalog, fills in any missing assets/ui
art, and regenerates the chunked Data payloads in the destination. Sprite
folders are left alone: they are hundreds of megabytes and identical between
installs.

Usage:
    python tools/deploy_addon.py "<src Battlemon dir>" "<dst Battlemon dir>"
"""

import filecmp
import os
import shutil
import subprocess
import sys

CODE_FILES = ["Battlemon.lua", "Battlemon.toc"]
CODE_DIRS = ["Core", "UI"]


def copy_code(src, dst):
    for name in CODE_FILES:
        s = os.path.join(src, name)
        d = os.path.join(dst, name)
        if os.path.exists(s):
            shutil.copy2(s, d)
            print("code  ", name)

    for folder in CODE_DIRS:
        s_dir = os.path.join(src, folder)
        d_dir = os.path.join(dst, folder)
        if not os.path.isdir(s_dir):
            continue
        os.makedirs(d_dir, exist_ok=True)
        wanted = set()
        for name in sorted(os.listdir(s_dir)):
            if not name.endswith(".lua"):
                continue
            wanted.add(name)
            shutil.copy2(os.path.join(s_dir, name), os.path.join(d_dir, name))
            print("code  ", folder + "\\" + name)
        for name in sorted(os.listdir(d_dir)):
            if name.endswith(".lua") and name not in wanted:
                os.remove(os.path.join(d_dir, name))
                print("remove", folder + "\\" + name)


def copy_ui_art(src, dst):
    s_dir = os.path.join(src, "assets", "ui")
    d_dir = os.path.join(dst, "assets", "ui")
    if not os.path.isdir(s_dir):
        return
    os.makedirs(d_dir, exist_ok=True)
    for name in sorted(os.listdir(s_dir)):
        s = os.path.join(s_dir, name)
        d = os.path.join(d_dir, name)
        if not os.path.exists(d) or not filecmp.cmp(s, d, shallow=False):
            shutil.copy2(s, d)
            print("art   ", name)


def copy_csv(src, dst):
    """The CSVs are the catalog source of truth; both installs must agree."""
    s_dir = os.path.join(src, "Data", "csv")
    d_dir = os.path.join(dst, "Data", "csv")
    if not os.path.isdir(s_dir):
        return
    os.makedirs(d_dir, exist_ok=True)
    for name in sorted(os.listdir(s_dir)):
        if not name.endswith(".csv"):
            continue
        s = os.path.join(s_dir, name)
        d = os.path.join(d_dir, name)
        if not os.path.exists(d) or not filecmp.cmp(s, d, shallow=False):
            shutil.copy2(s, d)
            print("csv   ", name)


def regen_data(dst):
    here = os.path.dirname(os.path.abspath(__file__))
    exporter = os.path.join(here, "export_addon_data.py")
    subprocess.check_call([sys.executable, exporter, dst])

    # Drop payloads the exporter no longer emits (e.g. the old learnset dump,
    # which is server-side data the client never needs).
    keep = set()
    toc = os.path.join(dst, "Battlemon.toc")
    with open(toc, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line.lower().startswith("data\\") and line.lower().endswith(".lua"):
                keep.add(os.path.basename(line))
    data_dir = os.path.join(dst, "Data")
    for name in sorted(os.listdir(data_dir)):
        if name.endswith(".lua") and name not in keep:
            os.remove(os.path.join(data_dir, name))
            print("remove Data\\" + name)


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    src, dst = sys.argv[1], sys.argv[2]
    for path in (src, dst):
        if not os.path.isdir(path):
            raise SystemExit("not a directory: " + path)
    if os.path.abspath(src) == os.path.abspath(dst):
        raise SystemExit("source and destination are the same")

    copy_code(src, dst)
    copy_ui_art(src, dst)
    copy_csv(src, dst)
    regen_data(dst)
    print("\ndeployed to", dst)


if __name__ == "__main__":
    main()
