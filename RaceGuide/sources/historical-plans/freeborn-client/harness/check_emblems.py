"""Confirm the two shipped emblems in the deployed archive are present and identical."""

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

storm = Storm(DLL_DEFAULT)
handle = storm.open_archive(r"G:\3.3.5a - Dev\Data\patch-Z.MPQ")
try:
    select = storm.read(handle, "Interface\\Glues\\CharacterSelect\\FreebornLogo.blp")
    create = storm.read(handle, "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Freeborn.blp")
finally:
    storm.dll.SFileCloseArchive(handle)

for label, blob in (("select emblem", select), ("create plate ", create)):
    print(f"  {label}: {len(blob)} bytes  sha256 {hashlib.sha256(blob).hexdigest()[:16]}  magic {blob[:4]!r}")
print("  identical:", select == create)
