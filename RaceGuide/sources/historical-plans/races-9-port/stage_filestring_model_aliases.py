"""Stage character models under the path the client derives from ClientFilestring.

In game the client builds a character's model from the race's `ClientFilestring`:
`Character\\<Filestring>\\<Gender>\\<Filestring><Gender>.m2` plus its `.skin`
LODs (`Human` -> `Character\\Human\\Male\\HumanMale.m2`, and so on). The port
only staged Eunoia's own folder names, so two races have nothing to load in game:

    KulTiran -> CHARACTER\\Naga_\\male\\kultiranmale.m2
    Illidari -> Character\\BloodElf_Dh\\Male\\BloodElfMale_DH.m2

Both now also exist under their filestring paths. Every other ported race
already resolves because only the letter case differs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / ".agents/plans/races-9-port"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from inspect_client_races import Client  # noqa: E402

PATCH_G = REPO / "3.3.5a - Dev/Data/Patch-G.MPQ"
B = chr(92)
# race filestring -> (male source stem, female source stem)
RACES = {
    "KulTiran": (
        "CHARACTER" + B + "Naga_" + B + "male" + B + "kultiranmale",
        "CHARACTER" + B + "Naga_" + B + "Female" + B + "kultiranfemale",
    ),
    "Illidari": (
        "Character" + B + "BloodElf_Dh" + B + "Male" + B + "BloodElfMale_DH",
        "Character" + B + "BloodElf_Dh" + B + "Female" + B + "BloodElfFemale_DH",
    ),
}
SUFFIXES = ("", ".m2", ".mdx") + tuple(f"0{lod}.skin" for lod in range(4))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    client = Client()
    updates: dict[str, bytes] = {}
    for race, stems in RACES.items():
        for gender, source in zip(("Male", "Female"), stems):
            alias = f"Character{B}{race}{B}{gender}{B}{race}{gender}"
            for suffix in SUFFIXES:
                if suffix and client.find(alias + suffix) is not None:
                    print(f"{alias + suffix}: already present")
                    continue
                payload = client.find(source + suffix)
                if payload is None:
                    print(f"  source missing: {source + suffix}")
                    continue
                updates[alias + suffix] = payload
                print(f"{alias + suffix}: staged from {source + suffix} ({len(payload):,} bytes)")
    if not updates:
        print("nothing to stage")
        return
    if args.dry_run:
        print("dry run - Patch-G untouched")
        return
    storm = Storm(DLL_DEFAULT)
    storm.replace_archive_entries(PATCH_G, updates)
    print(f"Patch-G updated with {len(updates)} files")


if __name__ == "__main__":
    main()
