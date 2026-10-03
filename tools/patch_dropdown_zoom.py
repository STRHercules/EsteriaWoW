"""Guard the installed v180 GlueZoom wheel callback; preserve its camera calibration and all other code."""

import hashlib
import json
import struct
from pathlib import Path

from wow_xref import Pe
from native_appearance_patch import align

SOURCE = Path("G:/3.3.5a - Dev/Extensions/wxl-glue-zoom/wxl-glue-zoom.dll")
OUTPUT = Path("C:/Users/Zach/.codex/tmp/character-ui/native/wxl-glue-zoom.dll")
EXPECTED = "074320262d6bba338f16ca7c62bfe16ce1677ef10f3553e0d0788667f9b2d844"


def patch():
    pe = Pe(SOURCE)
    if hashlib.sha256(pe.data).hexdigest() != EXPECTED:
        raise ValueError("GlueZoom fingerprint differs; the v180 guard is not applicable")
    entry = 0x10001A50
    if pe.read_va(entry, 8) != bytes.fromhex("558bece8e8f5ffff"):
        raise ValueError("GlueZoom wheel callback differs")
    data = bytearray(pe.data)
    nt = struct.unpack_from("<I", data, 0x3C)[0]
    optional = nt + 24
    count, size = struct.unpack_from("<H", data, nt + 6)[0], struct.unpack_from("<H", data, nt + 20)[0]
    section_header = optional + size + count * 40
    if section_header + 40 > min(s[4] for s in pe.sections):
        raise ValueError("No room for a PE section header")
    section_align, file_align = struct.unpack_from("<II", data, optional + 32)
    rva = align(max(s[1] + max(s[2], s[3]) for s in pe.sections), section_align)
    base = pe.image_base + rva
    import_rva = struct.unpack_from("<I", data, optional + 104)[0]
    descriptors = []
    while True:
        descriptor = pe.read_va(pe.image_base + import_rva + len(descriptors) * 20, 20)
        if descriptor == bytes(20):
            break
        if len(descriptor) != 20 or len(descriptors) > 64:
            raise ValueError("Invalid import table")
        descriptors.append(descriptor)
    blob = bytearray((len(descriptors) + 2) * 20)

    def add(payload, boundary=4):
        offset = align(len(blob), boundary)
        blob.extend(bytes(offset - len(blob)))
        blob.extend(payload)
        return offset

    dll = add(b"EsteriaAppearance.dll\0", 1)
    symbol = add(b"\0\0EsteriaDropdownWheelBlocked\0", 2)
    lookup = add(struct.pack("<II", rva + symbol, 0))
    iat = add(struct.pack("<II", rva + symbol, 0))
    for i, descriptor in enumerate(descriptors):
        blob[i * 20:(i + 1) * 20] = descriptor
    struct.pack_into("<IIIII", blob, len(descriptors) * 20, rva + lookup, 0, 0, rva + dll, rva + iat)
    code_offset = align(len(blob), 16)
    code_va = base + code_offset
    # Preserve the callback's registers/flags; a blocked wheel returns before changing zoomTarget.
    code = bytearray(b"\x9C\x60\xFF\x15" + struct.pack("<I", base + iat)
                     + b"\x84\xC0\x74\x03\x61\x9D\xC3\x61\x9D\x55\x8B\xEC")
    code += b"\xE8" + struct.pack("<i", 0x10001040 - (code_va + len(code) + 5))
    code += b"\xE9" + struct.pack("<i", entry + 8 - (code_va + len(code) + 5))
    assert add(code, 16) == code_offset
    old_reloc_rva, old_reloc_size = struct.unpack_from("<II", data, optional + 136)
    relocations = pe.read_va(pe.image_base + old_reloc_rva, old_reloc_size)
    site = rva + code_offset + 4
    relocations += struct.pack("<IIHH", site & ~4095, 12, 0x3000 | (site & 4095), 0)
    relocation_offset = add(relocations)
    entry_offset = next(raw + entry - pe.image_base - va for _, va, virtual, raw_size, raw in pe.sections
                        if va <= entry - pe.image_base < va + max(virtual, raw_size))
    data[entry_offset:entry_offset + 8] = b"\xE9" + struct.pack("<i", code_va - entry - 5) + b"\x90" * 3
    raw = align(len(data), file_align)
    data.extend(bytes(raw - len(data)))
    data.extend(blob)
    raw_size = align(len(blob), file_align)
    data.extend(bytes(raw_size - len(blob)))
    struct.pack_into("<8s8I", data, section_header, b".ezui\0\0\0", len(blob), rva, raw_size, raw,
                     0, 0, 0, 0xE0000060)
    struct.pack_into("<H", data, nt + 6, count + 1)
    struct.pack_into("<I", data, optional + 56, align(rva + len(blob), section_align))
    struct.pack_into("<II", data, optional + 104, rva, (len(descriptors) + 2) * 20)
    struct.pack_into("<II", data, optional + 136, rva + relocation_offset, len(relocations))
    struct.pack_into("<I", data, optional + 64, 0)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(data)
    report = {"source_hash": EXPECTED, "patched_hash": hashlib.sha256(data).hexdigest(),
              "callback_rva": hex(entry - pe.image_base), "guard_rva": hex(rva + code_offset)}
    OUTPUT.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    print(json.dumps(patch(), indent=2))
