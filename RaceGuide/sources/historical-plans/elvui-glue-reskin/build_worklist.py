"""Build the complete remaining-work list.

1. Resolve the winning archive for EVERY Interface\\GlueXML\\* file in load order.
2. Extract each winner.
3. Scan all winning Lua/XML for referenced Interface\\... textures.
4. Report which referenced textures are still stock (not already reskinned).
"""

from __future__ import annotations

import ctypes as c
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools")))

from cars_mount_pack import Storm, FindData, DLL_DEFAULT  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from resolve_glue import load_order, DATA  # noqa: E402

WINNING = HERE / "winning"
STAGED = HERE / "staging"

TEXTURE_RE = re.compile(
    r"Interface[\\/](?:Glues|Buttons|DialogFrame|Tooltips|tooltips|PaperDollInfoFrame|"
    r"ChatFrame|QuestFrame|HelpFrame|Common|OptionsFrame|FrameGeneral|TooltipDataProcessor)"
    r"[\\/][^\"'\s,\)\]]+",
    re.IGNORECASE,
)


def list_safe(storm, archive) -> list[str]:
    data = FindData()
    finder = storm.dll.SFileFindFirstFile(archive, b"*", c.byref(data), None)
    if not finder:
        return []
    out: list[str] = []
    try:
        while True:
            out.append(data.cFileName.split(b"\0", 1)[0].decode("latin-1"))
            if not storm.dll.SFileFindNextFile(finder, c.byref(data)):
                break
    finally:
        storm.dll.SFileFindClose(finder)
    return out


def main() -> int:
    storm = Storm(DLL_DEFAULT)
    order = load_order()

    winners: dict[str, tuple[str, object]] = {}  # path.casefold -> (archive_rel, handle)
    handles = {}
    for rel in order:
        path = DATA / rel
        if not path.exists():
            continue
        try:
            handle = storm.open_archive(path)
        except OSError:
            continue
        handles[rel] = handle
        for name in list_safe(storm, handle):
            if name.casefold().startswith("interface\\gluexml\\"):
                winners[name.casefold()] = (rel, handle)

    WINNING.mkdir(parents=True, exist_ok=True)
    print(f"resolved {len(winners)} GlueXML files\n")

    referenced: dict[str, set[str]] = {}
    for key, (rel, handle) in sorted(winners.items()):
        payload = storm.read(handle, key)
        target = WINNING / Path(key.replace("\\", "/")).name
        target.write_bytes(payload)
        text = payload.decode("utf-8", "replace")
        for match in TEXTURE_RE.finditer(text):
            ref = match.group(0).rstrip("\\/"); 
            if ref.casefold().endswith((".blp", ".tga", ".png")):
                ref = ref.rsplit(".", 1)[0]
            referenced.setdefault(ref, set()).add(target.name)

    # what is already handled?
    staged = set()
    for path in STAGED.rglob("*"):
        if path.is_file():
            staged.add(path.stem.casefold())
    # textures the client already resolves from a custom patch (patch-A etc.)
    custom_prefixes = ("Glues\\Common\\Glue-Panel-Button", "Glues\\Common\\Glues-BigButton",
                       "Glues\\Common\\Arrow", "Glues\\CharacterSelect\\128redbuttonpart2",
                       "Glues\\CharacterCreate\\UI-RotationRight-Big",
                       "Buttons\\UI-CheckBox", "Buttons\\UI-ScrollBar", "Buttons\\UI-Panel-MinimizeButton")

    print(f"{len(referenced)} distinct Interface textures referenced by glue Lua/XML\n")
    print("=== NOT YET RESKINNED (candidates) ===")
    remaining = []
    for ref in sorted(referenced, key=str.casefold):
        stem = Path(ref.replace("\\", "/")).stem.casefold()
        already = stem in staged or any(ref.casefold().startswith(p.casefold()) for p in custom_prefixes)
        if not already:
            remaining.append(ref)
    for ref in remaining:
        users = ", ".join(sorted(referenced[ref])[:3])
        print(f"  {ref}\n        used by: {users}")
    print(f"\n{len(remaining)} candidates")

    for handle in handles.values():
        storm.dll.SFileCloseArchive(handle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
