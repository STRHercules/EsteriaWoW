"""Hash-table probe for Eunoia MPQs: works on locked, name-stripped archives."""

from __future__ import annotations

import mmap
import struct
from pathlib import Path

DATA = Path(r"G:\Eunoia\Client\data")

_CRYPT = [0] * 0x500
_seed = 0x00100001
for _i in range(0x100):
    for _j in range(5):
        _seed = (_seed * 125 + 3) % 0x2AAAAB
        _hi = (_seed & 0xFFFF) << 16
        _seed = (_seed * 125 + 3) % 0x2AAAAB
        _CRYPT[_i + _j * 0x100] = (_hi | (_seed & 0xFFFF)) & 0xFFFFFFFF


def hash_string(name: str, htype: int) -> int:
    seed1 = 0x7FED7FED
    seed2 = 0xEEEEEEEE
    for ch in name.upper().replace("/", "\\"):
        c = ord(ch)
        seed1 = (_CRYPT[htype + c] ^ ((seed1 + seed2) & 0xFFFFFFFF)) & 0xFFFFFFFF
        seed2 = (c + seed1 + seed2 + (seed2 << 5) + 3) & 0xFFFFFFFF
    return seed1


PROBES = [
    "Character\\Human\\HumanMale.m2",
    "Character\\Orc\\OrcMale.m2",
    "DBFilesClient\\ChrRaces.dbc",
    "DBFilesClient\\CharBaseInfo.dbc",
    "DBFilesClient\\CharSections.dbc",
    "DBFilesClient\\CharHairGeosets.dbc",
    "DBFilesClient\\CharacterFacialHairStyles.dbc",
    "DBFilesClient\\CreatureModelData.dbc",
    "DBFilesClient\\CreatureDisplayInfo.dbc",
    "DBFilesClient\\ItemDisplayInfo.dbc",
    "Interface\\GlueXML\\CharacterCreate.lua",
    "Interface\\GlueXML\\GlueParent.lua",
    "Character\\Vulpera\\VulperaMale.m2",
    "Character\\Vulpera\\VulperaFemale.m2",
    "Character\\Vulpera\\VulperaMale00.skin",
    "Character\\Vulpera\\VulperaFemale00.skin",
    "Character\\Vulpera\\VulperaMale.blp",
    "Character\\Vulpera\\VulperaFemale.blp",
    "Character\\Vulpera_HD\\VulperaMale.m2",
    "Character\\Vulpera_HD\\VulperaFemale.m2",
    "Character\\VulperaHD\\VulperaMale.m2",
    "Character\\Vulpera\\Vulpera.m2",
    "Character\\Fox\\FoxMale.m2",
    "Creature\\VulperaMount\\VulperaMount.m2",
]


def main() -> None:
    archives = sorted(DATA.glob("*.mpq"), key=lambda p: p.name.casefold())
    tally: dict[str, list[str]] = {p: [] for p in PROBES}
    for path in archives:
        size = path.stat().st_size
        try:
            with open(path, "rb") as fh:
                mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
                try:
                    ident, header_size, arch32, version, shift = struct.unpack_from("<4sIIHH", mm, 0)
                    if ident != b"MPQ\x1a":
                        print(f"{path.name}: not MPQ")
                        continue
                    hash32, block32, hsize, bsize = struct.unpack_from("<IIII", mm, 16)
                    hash64 = struct.unpack_from("<Q", mm, 40)[0] if header_size >= 48 else 0
                    hpos = hash64 if hash64 + hsize * 16 <= size else hash32
                    if hpos + hsize * 16 > size:
                        print(f"{path.name}: header unusable (v{version} hs={header_size} pos={hpos} n={hsize})")
                        continue
                    blob = mm[hpos : hpos + hsize * 16]
                finally:
                    mm.close()
        except Exception as error:  # noqa: BLE001
            print(f"{path.name}: unreadable ({error})")
            continue
        words = struct.unpack_from(f"<{hsize * 4}I", blob, 0)
        found = []
        for probe in PROBES:
            h1 = hash_string(probe, 0x200)
            h2 = hash_string(probe, 0x300)
            for i in range(hsize):
                base = i * 4
                if words[base] == h1 and words[base + 1] == h2:
                    if words[base + 3] != 0xFFFFFFFF:
                        found.append(probe)
                    break
        flag = "  <== VULPERA" if any("vulpera" in n.casefold() for n in found) else ""
        print(f"{path.name}: v{version} entries={hsize} hits={len(found)}{flag}")
        for name in found:
            print(f"    {name}")
            tally[name].append(path.name)
    print("\n=== summary ===")
    for probe in PROBES:
        where = tally[probe]
        if where:
            print(f"{probe}: {', '.join(where)}")


if __name__ == "__main__":
    main()
