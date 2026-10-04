"""Probe Eunoia archives by exact MPQ path (works even when names are stripped)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

DATA = Path(r"G:\Eunoia\Client\data")

DBC = "DBFilesClient\\"
CHA = "Character\\"
PROBES = [
    DBC + "ChrRaces.dbc",
    DBC + "CharBaseInfo.dbc",
    DBC + "CharSections.dbc",
    DBC + "CharHairGeosets.dbc",
    DBC + "CharHairTextures.dbc",
    DBC + "CharacterFacialHairStyles.dbc",
    DBC + "CreatureModelData.dbc",
    DBC + "CreatureDisplayInfo.dbc",
    DBC + "CharStartOutfit.dbc",
    DBC + "NameGen.dbc",
    "Interface\\GlueXML\\CharacterCreate.lua",
    "Interface\\GlueXML\\GlueParent.lua",
    CHA + "Vulpera\\VulperaMale.m2",
    CHA + "Vulpera\\VulperaFemale.m2",
    CHA + "Vulpera\\VulperaMale00.skin",
    CHA + "Vulpera\\VulperaFemale00.skin",
    CHA + "Vulpera_HD\\VulperaMale.m2",
    CHA + "Vulpera_HD\\VulperaFemale.m2",
    CHA + "VulperaHD\\VulperaMale.m2",
    CHA + "Fox\\FoxMale.m2",
    CHA + "Vulpera\\VulperaMale.blp",
    "Creature\\VulperaMount\\VulperaMount.m2",
]


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    archives = sorted(DATA.glob("*.mpq"), key=lambda p: p.name.casefold())
    for path in archives:
        try:
            archive = storm.open_archive(path)
        except Exception as error:  # noqa: BLE001
            print(f"{path.name}: OPEN FAILED ({error})")
            continue
        try:
            hits = []
            for probe in PROBES:
                try:
                    payload = storm.read(archive, probe)
                except Exception:  # noqa: BLE001
                    continue
                hits.append((probe, len(payload)))
            if hits:
                print(f"{path.name}: {len(hits)} hit(s)")
                for name, size in hits:
                    print(f"    {name} = {size:,}")
        finally:
            storm.dll.SFileCloseArchive(archive)
    print("done")


if __name__ == "__main__":
    main()
