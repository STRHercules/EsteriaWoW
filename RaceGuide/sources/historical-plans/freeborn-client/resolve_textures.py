"""Resolve candidate GlueXML textures across the client's real archive chain.

A missing texture means an invisible Freeborn button, so the plate/border textures the new
button references must be proven to resolve somewhere in the client's load chain.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

CLIENT = Path(r"G:\3.3.5a - Dev")

CANDIDATES = (
    "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Gender_Round.blp",
    "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-GenderMale.blp",
    "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-GenderFemale.blp",
    "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Races.blp",
    "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-RacesRound.blp",
    "Interface\\Glues\\CharacterCreate\\IconBorder_F1.blp",
    "Interface\\Glues\\CharacterCreate\\IconBorderRace_H.blp",
)

# Load order low -> high; later archives win, so scan high -> low for resolution.
ARCHIVES = (
    "Data\\common.MPQ",
    "Data\\common-2.MPQ",
    "Data\\common-3.MPQ",
    "Data\\expansion.MPQ",
    "Data\\lichking.MPQ",
    "Data\\patch.MPQ",
    "Data\\patch-2.MPQ",
    "Data\\patch-3.MPQ",
    "Data\\PATCH-A.MPQ",
    "Data\\Patch-C.MPQ",
    "Data\\PATCH-V.mpq",
    "Data\\PATCH-X.MPQ",
    "Data\\Patch-Y.MPQ",
    "Data\\patch-Z.MPQ",
    "Data\\enUS\\locale-enUS.MPQ",
    "Data\\enUS\\patch-enUS-2.MPQ",
    "Data\\enUS\\patch-enUS-Z.MPQ",
)


def main() -> int:
    storm = Storm(DLL_DEFAULT)
    for archive_rel in ARCHIVES:
        path = CLIENT / archive_rel
        if not path.is_file():
            print(f"{archive_rel}: MISSING FILE")
            continue
        try:
            handle = storm.open_archive(path)
        except Exception as error:  # noqa: BLE001
            print(f"{archive_rel}: OPEN FAILED {error}")
            continue
        found = []
        try:
            for entry in CANDIDATES:
                try:
                    storm.read(handle, entry)
                except Exception:  # noqa: BLE001
                    continue
                found.append(Path(entry).name)
        finally:
            storm.dll.SFileCloseArchive(handle)
        print(f"{archive_rel}: {', '.join(found) if found else '-'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
