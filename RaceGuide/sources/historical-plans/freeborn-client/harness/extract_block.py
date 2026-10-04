"""Extract the managed Freeborn block from the DEPLOYED archive, for offline Lua execution."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

BEGIN = "-- >>> freeborn-third-team (managed block, do not edit) >>>"
END = "-- <<< freeborn-third-team (managed block) <<<"
LUA = "Interface\\GlueXML\\CharacterCreate.lua"
ADDON = "Interface\\AddOns\\FreebornClaim\\FreebornClaim.lua"

archive = Path(sys.argv[1])
out = Path(__file__).resolve().parent / "block.lua"

storm = Storm(DLL_DEFAULT)
handle = storm.open_archive(archive)
try:
    text = storm.read(handle, LUA).decode("utf-8")
    addon = storm.read(handle, ADDON).decode("utf-8")
finally:
    storm.dll.SFileCloseArchive(handle)

start = text.index(BEGIN)
stop = text.index(END) + len(END)
block = text[start:stop]
out.write_text(block, encoding="utf-8", newline="\n")
print(f"extracted {len(block)} bytes, {block.count(chr(10)) + 1} lines -> {out}")
print("first line:", block.splitlines()[0])
print("last line :", block.splitlines()[-1])

addon_out = Path(__file__).resolve().parent / "addon.lua"
addon_out.write_text(addon, encoding="utf-8", newline="\n")
print(f"extracted addon {len(addon)} bytes -> {addon_out}")
