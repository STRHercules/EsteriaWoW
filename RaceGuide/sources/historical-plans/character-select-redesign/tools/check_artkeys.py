"""Cross-check ECS art keys against the CREATE SCREEN's own portrait mapping.

ECS resolves a portrait as `UI-CharacterCreate-<artKey><Male|Female>`, so the art
key has to match the file the rest of the client uses. `CharacterCreate.lua` already
maps every race token to its plate in `RACE_ICON_TEXTURES`, which makes it the
authoritative source - and it is not the same as the race token:

    ["ZANDALARITROLL_MALE"] = "...\\UI-CharacterCreate-ZandalariMale"

which is exactly the mismatch this checks for.

Usage:
    python .agents/plans/character-select-redesign/tools/check_artkeys.py
"""

from __future__ import annotations

import re
from pathlib import Path

from lupa.lua51 import LuaRuntime

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parents[2]
SRC = ROOT / "src" / "GlueXML"

# The deployed fork's create screen (extracted from the client archives).
CANDIDATES = [
    REPO / ".agents" / "plans" / "elvui-glue-reskin" / "extracted" / "deployed-root" / "CharacterCreate.lua",
    REPO / ".agents" / "plans" / "freeborn-client" / "deployed_check" / "CharacterCreate.lua",
]

create_lua = next((p for p in CANDIDATES if p.exists()), None)
if create_lua is None:
    raise SystemExit("could not find the deployed CharacterCreate.lua")

text = create_lua.read_text(encoding="utf-8", errors="replace")
block = text[text.index("RACE_ICON_TEXTURES"):]
block = block[: block.index("}")]

authoritative: dict[str, dict[str, str]] = {}
for token, sex, art in re.findall(
    r'\["([A-Z0-9_]+)_(MALE|FEMALE)"\]\s*=\s*"[^"]*?UI-CharacterCreate-([A-Za-z0-9_]+)"',
    block,
):
    # The art capture is greedy and keeps the sex suffix ("BloodElfMale"), because
    # the file name ends with it. Strip it, or every single comparison below reads
    # as a mismatch and the tool reports 27 false positives instead of 1 real one.
    if not art.endswith(sex.title()):
        continue
    authoritative.setdefault(token, {})[sex] = art[: -len(sex)]

lua = LuaRuntime(unpack_returned_tuples=True)
for name in ("ECS_Constants.lua", "ECS_Schema.lua"):
    lua.execute((SRC / name).read_text(encoding="utf-8"))

raw = lua.eval(
    r"""
(function()
    local S = ECS.Schema; local out = {};
    for i = 1, #S.RaceByModelKey do
        local e = S.RaceByModelKey[i];
        if type(e) == "table" and type(e[2]) == "table" and e[2].artKey then
            out[#out+1] = e[1] .. "\t" .. e[2].artKey;
        end
    end
    return table.concat(out, "\n");
end)()
"""
)
pairs = [line.split("\t") for line in raw.splitlines() if line.strip()]

print(f"create-screen tokens with a portrait : {len(authoritative)}")
print(f"ECS schema tokens with an art key    : {len(pairs)}")
print()

problems = 0
for token, art_key in sorted(pairs):
    entry = authoritative.get(token)
    if entry is None:
        # No create-screen mapping: the token is ECS-only, so the shipped art (if
        # any) is the only reference. Report rather than assume.
        print(f"  NO CREATE MAPPING  {token:<20} artKey={art_key!r}")
        problems += 1
        continue
    male = entry.get("MALE")
    if male != art_key:
        print(f"  ART KEY MISMATCH   {token:<20} ECS={art_key!r} create-screen={male!r}")
        problems += 1

if problems == 0:
    print("every ECS art key matches the create screen's mapping")
else:
    print()
    print(f"{problems} ECS art key(s) disagree with the create screen")

# ---------------------------------------------------------------- client plates
# The definitive test: does the art file ECS will request actually exist? The
# create-screen table can only tell us the intended name. This needs the client,
# so it is skipped cleanly when the archives are not present.
client_note = ""
try:
    import ctypes
    import sys

    REPO_STR = str(REPO)
    if REPO_STR not in sys.path:
        sys.path.insert(0, REPO_STR)
    sys.path.insert(0, str(REPO / "tools"))
    from cars_mount_pack import FindData, Storm, DLL_DEFAULT  # noqa: E402

    data_dir = Path(r"G:\3.3.5a - Dev\Data")
    archives = [data_dir / "patch-Z.MPQ", data_dir / "patch-A.MPQ",
                data_dir / "enUS" / "patch-enUS-Z.MPQ"]
    if any(a.exists() for a in archives):
        plate_prefix = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-"
        storm = Storm(DLL_DEFAULT)
        plates: set[str] = set()
        for archive in archives:
            if not archive.exists():
                continue
            handle = storm.open_archive(archive)
            finder_data = FindData()
            finder = storm.dll.SFileFindFirstFile(
                handle, b"*", ctypes.byref(finder_data), None
            )
            if not finder:
                continue
            try:
                while True:
                    entry = finder_data.cFileName.split(b"\0", 1)[0].decode("latin-1")
                    if entry.casefold().startswith(plate_prefix.casefold()):
                        plates.add(entry[len(plate_prefix):])
                    if not storm.dll.SFileFindNextFile(finder, ctypes.byref(finder_data)):
                        break
            finally:
                storm.dll.SFileFindClose(finder)

        missing_plate = []
        for token, art_key in sorted(pairs):
            for sex in ("Male", "Female"):
                if f"{art_key}{sex}.blp" not in plates:
                    missing_plate.append((token, art_key, sex))
        print()
        print(f"client plates found                    : {len(plates)}")
        if missing_plate:
            print(f"ECS art keys with NO client plate ({len(missing_plate)}):")
            for token, art_key, sex in missing_plate:
                print(f"  {token:<14} artKey={art_key + sex + '.blp'!r}")
        else:
            print("every ECS art key resolves to a real client plate")
except Exception as exc:  # noqa: BLE001 - a missing client must not fail the check
    client_note = f"  (client plate check skipped: {exc})"
if client_note:
    print(client_note)

# Reverse direction: art the create screen can show that ECS has no token for.
ecs_tokens = {token for token, _ in pairs}
unreached = sorted(set(authoritative) - ecs_tokens)
print()
print(f"create-screen tokens no ECS schema token reaches ({len(unreached)}):")
for token in unreached:
    print(f"  {token:<22} -> {authoritative[token].get('MALE')}")

# ---------------------------------------------------------------- ECS portrait set
# `S.PortraitArtKeys` decides which portraits the roster asks ECS for, and the
# generated files are what actually exist. A key listed but not generated asks for a
# missing texture (no portrait); a file generated but not listed is dead weight in
# the MPQ. Both directions are checked.
generated = {p.name[len("ECS-Portrait-"):-len(".blp")]
             for p in (ROOT / "textures").glob("ECS-Portrait-*.blp")}
generated_keys = {name[:-4] for name in generated if name.endswith("Male")}

listed = lua.eval(r"""
(function()
    local out = {};
    for key in pairs(ECS.Schema.PortraitArtKeys) do out[#out+1] = key end
    return table.concat(out, "\n");
end)()
""")
listed_keys = {line for line in listed.splitlines() if line.strip()}

print()
print(f"portraits generated on disk : {len(generated_keys)} art keys")
print(f"keys listed in PortraitArtKeys: {len(listed_keys)}")

listed_missing = sorted(listed_keys - generated_keys)
generated_unlisted = sorted(generated_keys - listed_keys)
if listed_missing:
    print(f"LISTED BUT NOT GENERATED ({len(listed_missing)}) - these render no portrait:")
    for key in listed_missing:
        print(f"  {key}")
if generated_unlisted:
    print(f"GENERATED BUT NOT LISTED ({len(generated_unlisted)}) - dead weight in the MPQ:")
    for key in generated_unlisted:
        print(f"  {key}")
if not listed_missing and not generated_unlisted:
    print("PortraitArtKeys and the generated files agree")
