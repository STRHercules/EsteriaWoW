"""Static contract checks for the Esteria 64-race runtime extension."""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path


class VerificationError(RuntimeError):
    """Raised when an extension contract is not satisfied."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


class PeImage:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data = path.read_bytes()
        require(self.data[:2] == b"MZ", f"{path} is not a DOS PE image")
        pe_offset = struct.unpack_from("<I", self.data, 0x3C)[0]
        require(self.data[pe_offset : pe_offset + 4] == b"PE\0\0", f"{path} has no PE signature")

        file_header = pe_offset + 4
        self.machine, section_count, _, _, _, optional_size, _ = struct.unpack_from(
            "<HHIIIHH", self.data, file_header
        )
        optional = file_header + 20
        self.magic = struct.unpack_from("<H", self.data, optional)[0]
        require(self.magic == 0x10B, f"{path} is not a PE32 image")
        self.image_base = struct.unpack_from("<I", self.data, optional + 28)[0]

        section_table = optional + optional_size
        self.sections: list[tuple[str, int, int, int, int]] = []
        for index in range(section_count):
            section = section_table + index * 40
            name = self.data[section : section + 8].split(b"\0", 1)[0].decode("ascii", "replace")
            virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from(
                "<IIII", self.data, section + 8
            )
            self.sections.append((name, virtual_address, virtual_size, raw_size, raw_offset))

        self.optional_offset = optional

    def rva_to_offset(self, rva: int, size: int = 1) -> int:
        for _, virtual_address, virtual_size, raw_size, raw_offset in self.sections:
            section_size = max(virtual_size, raw_size)
            if virtual_address <= rva < virtual_address + section_size:
                offset = raw_offset + rva - virtual_address
                require(offset + size <= raw_offset + raw_size, f"RVA 0x{rva:X} is not file-backed")
                return offset
        raise VerificationError(f"RVA 0x{rva:X} is not mapped by a PE section")

    def read_va(self, address: int, size: int) -> bytes:
        require(address >= self.image_base, f"VA 0x{address:08X} is below the image base")
        return self.data[self.rva_to_offset(address - self.image_base, size) :][0:size]

    def read_u8(self, address: int) -> int:
        return self.read_va(address, 1)[0]

    def read_u32(self, address: int) -> int:
        return struct.unpack("<I", self.read_va(address, 4))[0]

    def read_cstring_va(self, address: int) -> str:
        require(address != 0, "unexpected null string pointer")
        offset = self.rva_to_offset(address - self.image_base)
        end = self.data.find(b"\0", offset)
        require(end != -1, f"string at VA 0x{address:08X} is unterminated")
        return self.data[offset:end].decode("ascii", "replace")

    def export_names(self) -> set[str]:
        export_rva, export_size = struct.unpack_from("<II", self.data, self.optional_offset + 96)
        require(export_rva != 0 and export_size != 0, f"{self.path} has no export directory")
        export_offset = self.rva_to_offset(export_rva, 40)
        fields = struct.unpack_from("<IIHHIIIIIII", self.data, export_offset)
        name_count = fields[7]
        names_rva = fields[9]
        names_offset = self.rva_to_offset(names_rva, name_count * 4)
        return {
            self.read_rva_cstring(struct.unpack_from("<I", self.data, names_offset + index * 4)[0])
            for index in range(name_count)
        }

    def read_rva_cstring(self, rva: int) -> str:
        offset = self.rva_to_offset(rva)
        end = self.data.find(b"\0", offset)
        require(end != -1, f"string at RVA 0x{rva:X} is unterminated")
        return self.data[offset:end].decode("ascii", "replace")


def verify_client(path: Path) -> None:
    image = PeImage(path)
    require(image.machine == 0x14C, f"{path} is not x86")
    require(image.image_base == 0x00400000, f"unexpected image base 0x{image.image_base:08X}")
    require(
        image.read_va(0x00DFE000, len(b"ESTERIA_CLIENT_FOUNDATION_V3\0"))
        == b"ESTERIA_CLIENT_FOUNDATION_V3\0",
        "Esteria foundation signature mismatch",
    )

    table_references = (
        0x004E157D,
        0x004E16A3,
        0x004E15B5,
        0x004E20EE,
        0x004E222A,
        0x004E2127,
        0x004E1E94,
        0x004E1C3A,
    )
    for address in table_references:
        require(image.read_u32(address) == 0x00DFE220, f"table reference mismatch at 0x{address:08X}")
    require(image.read_u32(0x004CDA43) == 0x00DFE400, "race-name pointer mismatch")
    require(image.read_u32(0x004E1C34) == 0x100, "memory clear size mismatch")
    require(image.read_u32(0x004E1E9B) == 22, "cleanup count mismatch")
    require(
        image.read_va(0x004DFAF0, 6) == bytes.fromhex("0F 87 3C 01 00 00"),
        "extended-race branch fingerprint mismatch",
    )
    require(image.read_u8(0x00464C4F) == 0x64, "character limit is not 100")

    expected_names = (
        None,
        "Human",
        "Orc",
        "Dwarf",
        "NightElf",
        "Scourge",
        "Tauren",
        "Gnome",
        "Troll",
        "Goblin",
        "BloodElf",
        "Draenei",
        "Worgen",
        "HighElf",
        "MagharOrc",
        "Ogre",
        "Eredar",
        "Nightborne",
        "Pandaren_Alliance",
        "VoidElf",
        "Vulpera",
        "LightforgedDraenei",
        "ZandalariTroll",
        "DarkIronDwarf",
        "Broken_Alliance",
        "Forsaken",
        "Pandaren_Horde",
        "Broken_Horde",
    )
    name_pointers = [image.read_u32(0x00DFE400 + index * 4) for index in range(32)]
    require(name_pointers[0] == 0, "race-name slot 0 must remain null")
    for race_id, expected in enumerate(expected_names[1:], 1):
        require(name_pointers[race_id] != 0, f"race-name slot {race_id} is null")
        require(image.read_cstring_va(name_pointers[race_id]) == expected, f"race-name slot {race_id} changed")
    require(name_pointers[28:] == [0, 0, 0, 0], "unexpected baseline names in slots 28..31")


def verify_dll(path: Path) -> None:
    image = PeImage(path)
    require(image.machine == 0x14C, f"{path} is not a Win32 DLL")
    require({"WXL_Query", "WXL_Load"} <= image.export_names(), "WXL exports are incomplete")
    require(b"races-64-esteria" in path.read_bytes(), "DLL does not identify as races-64-esteria")


def verify_manifest(path: Path) -> None:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    extension = manifest.get("extension", {})
    require(extension.get("id") == "races-64-esteria", "manifest extension id mismatch")
    require(extension.get("entry") == "races-64-esteria.dll", "manifest DLL entry mismatch")


def verify_source(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    required = (
        "kEsteriaFoundationSignatureVa = 0x00DFE000",
        "kOriginalMemoryTableVa = 0x00DFE220",
        "kOriginalRaceNameTableVa = 0x00DFE400",
        "kOriginalClearSize = 0x100",
        "kOriginalCleanupCount = 22",
        "kExpectedCharacterLimit = 0x64",
        "kRaceCount = 64",
        "kSexCount = 2",
        "kExistingRaceNameCount = 32",
        "kFirstFallbackRace = 28",
        "kMemoryTableSize = kRaceCount * kSexCount * sizeof(uint32_t)",
        "kOriginalMemoryTableSize = 0x100",
        "std::array<Patch, 12>",
        "races-64-esteria",
        "std::memcpy(g_data, reinterpret_cast<const void*>(RuntimeAddress(kOriginalMemoryTableVa)),\n                    kOriginalMemoryTableSize)",
        "std::memcpy(raceNames, reinterpret_cast<const void*>(RuntimeAddress(kOriginalRaceNameTableVa)),\n                    kExistingRaceNameCount * sizeof(uint32_t))",
        "for (uint32_t race = kFirstFallbackRace; race < kRaceCount; ++race)",
    )
    for needle in required:
        require(needle in source, f"source contract missing: {needle}")
    require("MakePatch(kCharacterLimitVa" not in source, "source still patches the character limit")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", type=Path, required=True)
    parser.add_argument("--dll", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source", type=Path)
    args = parser.parse_args()

    try:
        verify_client(args.client)
        verify_dll(args.dll)
        verify_manifest(args.manifest)
        if args.source:
            verify_source(args.source)
    except (OSError, struct.error, json.JSONDecodeError, VerificationError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print("PASS: Esteria client, DLL, manifest, and source contracts verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
