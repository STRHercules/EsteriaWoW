"""Stop the glue screens from breaking on the ported races.

`CharacterSelect.lua` and `GlueParent.lua` both do
`PlayGlueAmbience(GlueAmbienceTracks[strupper(name)], 4.0)`. For a race that has
no entry the argument is nil, the native call errors out, and the character
select screen aborts - which is why freshly created characters never appeared in
the list. Two fixes: give the ported races the same glue tables the stock races
have (fog, glow, ambience, lights), and make both call sites tolerate a missing
track so this can never take a screen down again.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402
sys.path.insert(0, str(REPO / ".agents/plans/races-9-port"))
from inspect_client_races import Client  # noqa: E402

PATCH_Y = REPO / "3.3.5a - Dev/Data/Patch-Y.MPQ"
PARENT_KEY = "Interface\\GlueXML\\GlueParent.lua"
SELECT_KEY = "Interface\\GlueXML\\CharacterSelect.lua"
# race filestring -> stock race whose glue data it borrows
RACES = {
    "EREDAR": "ORC",
    "NIGHTBORNE": "ORC",
    "ZANDALARITROLL": "ORC",
    "DRACTHYR": "ORC",
    "ILLIDARI": "ORC",
    "VOIDELF": "HUMAN",
    "LIGHTFORGEDDRAENEI": "HUMAN",
    "DARKIRONDWARF": "HUMAN",
    "KULTIRAN": "HUMAN",
}


def patch_parent(lua: str) -> tuple[str, list[str]]:
    changes = []
    anchors = {
        "CharModelFogInfo": 'CharModelFogInfo["VULPERA"] = CharModelFogInfo["ORC"];',
        "CharModelGlowInfo": 'CharModelGlowInfo["VULPERA"] = CharModelGlowInfo["ORC"];',
        "GlueAmbienceTracks": 'GlueAmbienceTracks["VULPERA"] = GlueAmbienceTracks["ORC"];',
    }
    for table, anchor in anchors.items():
        if anchor not in lua:
            raise SystemExit(f"anchor missing for {table}")
        lines = [line for line in lua.splitlines() if f'{table}["' in line]
        additions = [
            f'{table}["{race}"] = {table}["{source}"];' for race, source in RACES.items() if f'{table}["{race}"]' not in lua
        ]
        if additions:
            lua = lua.replace(anchor, anchor + "\n" + "\n".join(additions), 1)
            changes.append(f"{table}: +{len(additions)} races")
    # RaceLights lives further down the file
    anchor = 'RaceLights["VULPERA"] = RaceLights["ORC"];'
    if anchor in lua:
        additions = [
            f'RaceLights["{race}"] = RaceLights["{source}"];' for race, source in RACES.items() if f'RaceLights["{race}"]' not in lua
        ]
        if additions:
            lua = lua.replace(anchor, anchor + "\n" + "\n".join(additions), 1)
            changes.append(f"RaceLights: +{len(additions)} races")
    # guard the ambience call in SetBackgroundModel
    pattern = re.compile(r"(\n\s*)PlayGlueAmbience\(GlueAmbienceTracks\[nameupper\], 4\.0\);")
    if pattern.search(lua):
        def replacement(match: re.Match) -> str:
            indent = match.group(1)
            return (
                f"{indent}local ambience = GlueAmbienceTracks[nameupper] or GlueAmbienceTracks[\"HUMAN\"];\n"
                f"{indent}if ( ambience ) then\n"
                f"{indent}    PlayGlueAmbience(ambience, 4.0);\n"
                f"{indent}end"
            )

        lua = pattern.sub(replacement, lua, count=1)
        changes.append("SetBackgroundModel: ambience call guarded")
    return lua, changes


def patch_select(lua: str) -> tuple[str, list[str]]:
    pattern = re.compile(
        r"(\n\s*)if \( CurrentModel \) then\n(\s*)PlayGlueAmbience\(GlueAmbienceTracks\[strupper\(CurrentModel\)\], 4\.0\);"
    )
    match = pattern.search(lua)
    if match is None:
        return lua, []
    indent = match.group(1)
    replacement = (
        f"{indent}if ( CurrentModel ) then\n"
        f"{indent}    local ambience = GlueAmbienceTracks[strupper(CurrentModel)] "
        f'or GlueAmbienceTracks["HUMAN"];\n'
        f"{indent}    if ( ambience ) then\n"
        f"{indent}        PlayGlueAmbience(ambience, 4.0);\n"
        f"{indent}    end"
    )
    lua = lua[: match.start()] + replacement + lua[match.end() :]
    return lua, ["CharacterSelect_OnShow: ambience call guarded"]


def patch_parent_background_races(lua: str) -> tuple[str, list[str]]:
    """Teach SetBackgroundModel's own race tables about the ported races.

    Both of its branches (`CharacterCreate` -> SetCharCustomizeBackground, otherwise
    SetCharSelectBackground) fall through to
    `Interface\\Glues\\Models\\UI_<name>\\UI_<name>.m2` for a race key they do not know.
    Those scenes only exist for the stock races, so the scene never builds and the
    actor shows up as the placeholder cube - the creator hit this first, the character
    select screen hits it now. Declaring the ported races as alliance/horde sends them
    down the shared UI_ALLIANCE / UI_HORDE scenes the stock races already use.
    """
    changes = []
    groups = (
        ("allianceRaces", ("VOIDELF", "LIGHTFORGEDDRAENEI", "DARKIRONDWARF", "KULTIRAN")),
        ("hordeRaces", ("EREDAR", "NIGHTBORNE", "ZANDALARITROLL", "DRACTHYR", "ILLIDARI")),
    )
    for table, races in groups:
        pattern = re.compile(r"(local " + table + r" = \{)(.*?)(\n\s*\};)", re.S)
        match = pattern.search(lua)
        if match is None:
            raise SystemExit(f"anchor missing for {table}")
        additions = [race for race in races if f'["{race}"] = true' not in match.group(2)]
        if additions:
            block = "".join(f'\n        ["{race}"] = true,' for race in additions)
            lua = lua[: match.end(2)] + block + lua[match.end(2) :]
            changes.append(f"{table}: +{len(additions)} races")
    return lua, changes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    storm = Storm(DLL_DEFAULT)
    client = Client()
    updates: dict[str, bytes] = {}
    patchers = ((PARENT_KEY, (patch_parent, patch_parent_background_races)), (SELECT_KEY, (patch_select,)))
    for key, chain in patchers:
        payload = client.find(key)
        if payload is None:
            print(f"{key}: not found in the client")
            continue
        original = payload.decode("utf-8")
        lua = original
        for patcher in chain:
            lua, changes = patcher(lua)
            for line in changes:
                print(f"{Path(key).name}: {line}")
        if lua != original:
            updates[key] = lua.encode("utf-8")
    if not updates:
        print("nothing to change")
        return
    if args.dry_run:
        print("dry run - Patch-Y untouched")
        return
    storm.replace_archive_entries(PATCH_Y, updates)
    print(f"Patch-Y updated: {sorted(updates)}")


if __name__ == "__main__":
    main()
