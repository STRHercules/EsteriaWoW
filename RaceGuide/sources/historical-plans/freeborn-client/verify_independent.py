"""Independent verification of the deployed Freeborn client patch.

Deliberately does not import the packer or the contract test: it re-derives everything from the
deployed archives and the pristine backup, so a bug in my own checking code cannot hide a problem.

The strongest check here is that removing the injected button from the deployed XML reproduces the
pristine stock file byte for byte, and that the deployed Lua's stock prefix matches the pristine
Lua byte for byte -- i.e. the only change is the addition.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

CLIENT = Path(r"G:\3.3.5a - Dev")
PRISTINE = CLIENT / "Data" / "_freeborn-backups" / "20260924T063018Z"
BUTTON = "CharacterCreateFreebornButton"
LUA_BEGIN = "-- >>> freeborn-third-team (managed block, do not edit) >>>"
LUA_END = "-- <<< freeborn-third-team (managed block) <<<"
HEADER = "-- Freeborn third player team: character-creation selection."
LUA = "Interface\\GlueXML\\CharacterCreate.lua"
XML = "Interface\\GlueXML\\CharacterCreate.xml"

failures: list[str] = []


def check(condition: bool, message: str) -> None:
    print(("  ok   " if condition else "  FAIL ") + message)
    if not condition:
        failures.append(message)


def read(archive: Path, entry: str) -> str:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(archive)
    try:
        return storm.read(handle, entry).decode("utf-8")
    finally:
        storm.dll.SFileCloseArchive(handle)


stock_lua = read(PRISTINE / "patch-Z.MPQ", LUA)
stock_xml = read(PRISTINE / "patch-Z.MPQ", XML)
addon_source = read(CLIENT / "Data" / "patch-Z.MPQ", "Interface\\AddOns\\FreebornClaim\\FreebornClaim.lua")

for archive in (CLIENT / "Data" / "patch-Z.MPQ", CLIENT / "Data" / "enUS" / "patch-enUS-Z.MPQ"):
    print(f"=== {archive.name} ===")
    lua = read(archive, LUA)
    xml = read(archive, XML)

    check(lua.count(LUA_BEGIN) == 1, f"exactly one managed block (got {lua.count(LUA_BEGIN)})")
    check(lua.count(LUA_END) == 1, f"exactly one block terminator (got {lua.count(LUA_END)})")
    check(lua.count("if not CharacterFreeborn_Init then") == 1,
          f"exactly one block guard (got {lua.count('if not CharacterFreeborn_Init then')})")
    check(lua.count(HEADER) == 1, f"exactly one revision header (got {lua.count(HEADER)})")

    # The name must be sent exactly as typed: no transformer, no injected character, and the
    # stock accept path does the create call. Scoped to the injected block -- the stock file above
    # it legitimately contains `CreateCharacter(`.
    block = lua[lua.index(LUA_BEGIN):lua.index(LUA_END) + len(LUA_END)]
    check("CharacterFreeborn_CreateName" not in lua, "the name is never transformed")
    check("CreateCharacter(" not in block, "the wrapper delegates to the stock accept path")
    check('" "' not in block, "no space is injected into a name")

    # The choice is recorded by hashing the typed name into cvar names this client already knows.
    # Re-derived here without the packer, straight from the archives. The addon ships in the root
    # archive only, so it is read once above.
    carriers = re.search(r"CharacterFreeborn_CarrierCVars = \{([^}]*)\}", block)
    check(carriers is not None, "the create screen declares which cvars carry the choice")
    if carriers:
        names = re.findall(r'"([^"]+)"', carriers.group(1))
        check(len(names) > 0, f"at least one carrier cvar is declared (got {names})")
        check(
            all(f'"{name}"' in addon_source for name in names),
            f"the addon reads the same carrier cvars as the create screen ({names})",
        )
    check("CharacterFreeborn_NameHash" in block, "the create screen hashes the chosen name")
    check("CharacterFreeborn_SafeSet(name," in block, "the record is written through the guard")
    check("CharacterFreeborn_StoreBadge(record)" in block, "the emblem record is stored by this screen")

    # A record has to stay a plain number inside INT_MAX: that is the only value shape this client
    # stores, and a "fb:"-prefixed marker was silently refused in the field.
    base = re.search(r"CharacterFreeborn_RecordBase = (\d+)", block)
    mod = re.search(r"CharacterFreeborn_RecordMod = (\d+)", block)
    check(base is not None and mod is not None, "the record encoding is declared")
    if base and mod:
        check(
            int(base.group(1)) + int(mod.group(1)) - 1 <= 2147483647,
            "a record stays inside INT_MAX",
        )

    # Stock prefix must be untouched: the injected block is appended after it, so everything
    # before the sentinel has to match the pristine file exactly.
    start = lua.index(LUA_BEGIN)
    prefix = lua[:start].rstrip("\n")
    check(prefix == stock_lua.rstrip("\n"), "stock Lua prefix is byte-identical to the pristine backup")

    # No statement at the block's top level may touch a frame: line 1846 of the shipped file did,
    # which aborted the chunk before any function was defined.
    block = lua[lua.index(LUA_BEGIN):lua.index(LUA_END) + len(LUA_END)]
    unsafe = []
    for number, raw in enumerate(block.splitlines(), 1):
        if not raw.startswith("    ") or raw.startswith("     "):
            continue
        line = raw.strip()
        if not line or line.startswith("--"):
            continue
        if line.startswith(("function ", "local ")) or line in ("end", "end;") or line.startswith("CharacterFreeborn_"):
            continue
        unsafe.append(f"L{number}:{line}")
    check(not unsafe, f"no load-time frame access in the block (found {unsafe})")

    # XML: removing the injected button must reproduce the pristine file exactly.
    check(xml.count(f'name="{BUTTON}"') == 1, f"button declared once (got {xml.count(f'name=\"{BUTTON}\"')})")
    button_text = (ROOT / "tools" / "freeborn_client" / "CharacterCreate.freeborn.xml").read_text(
        encoding="utf-8").strip("\n")
    line_start = xml.rfind("\n", 0, xml.index(f'<CheckButton name="{BUTTON}"')) + 1
    without = xml[:line_start] + xml[line_start + len(button_text) + 1:]
    check(without == stock_xml, "removing the button reproduces the pristine stock XML exactly")
    check("<Anchors>" in button_text, "button carries its own anchor")

    # The claim addon rides the root archive only.
    if archive.name == "patch-Z.MPQ":
        for name in ("FreebornClaim.toc", "FreebornClaim.lua"):
            entry = "Interface\\AddOns\\FreebornClaim\\" + name
            payload = read(archive, entry)
            source = (ROOT / "tools" / "freeborn_client" / "addon" / "FreebornClaim" / name).read_text(
                encoding="utf-8")
            check(payload == source, f"{entry} matches the payload")
    print()

if failures:
    print(f"{len(failures)} independent check(s) FAILED")
    raise SystemExit(1)

print("independent verification: PASS")
