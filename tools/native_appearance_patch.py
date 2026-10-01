"""Fingerprint-checked permanent native appearance patch for Esteria build12340."""

import argparse
import hashlib
import json
import struct
from pathlib import Path

from wow_xref import Pe

EXPECTED_SHA256 = "2cf5a5cbaa8b27c7497d181a5d08fce2861bb55d66bd12a8b4a2657a67e0c409"
CLIENT = Path(r"G:\3.3.5a - Dev\Wow.exe")
STAGE = Path(r"C:\Users\Zach\.codex\tmp\native-appearance")
EXPORTS = ("EsteriaCycle", "EsteriaWideSource", "EsteriaDrawStart", "EsteriaGeometry", "EsteriaSkin",
           "EsteriaSkillRace", "EsteriaCreateExtra", "EsteriaEnumExtra", "EsteriaSelectExtra", "EsteriaUnitExtra",
           "EsteriaRegisterExtra", "EsteriaAppearanceContext", "EsteriaSectionArguments", "EsteriaDirectSection",
           "EsteriaSectionCount", "EsteriaForgetCharacter")


def align(value, boundary):
    return (value + boundary - 1) // boundary * boundary


def patch(source=CLIENT, output=STAGE / "Wow.exe"):
    pe = Pe(source)
    if hashlib.sha256(pe.data).hexdigest() != EXPECTED_SHA256:
        raise ValueError("Wow.exe differs from the audited Esteria image; no patch applied")
    signature = b"ESTERIA_CLIENT_FOUNDATION_V3\0"
    if pe.read_va(0x00DFE000, len(signature)) != signature:
        raise ValueError("Client foundation signature differs")
    data = bytearray(pe.data)
    nt = struct.unpack_from("<I", data, 0x3C)[0]
    optional = nt + 24
    section_count = struct.unpack_from("<H", data, nt + 6)[0]
    optional_size = struct.unpack_from("<H", data, nt + 20)[0]
    new_header = optional + optional_size + section_count * 40
    if new_header + 40 > min(s[4] for s in pe.sections):
        raise ValueError("No spare PE section-header space")
    if struct.unpack_from("<H", data, optional + 70)[0] & 0x40:
        raise ValueError("ASLR image needs relocated native thunks")
    section_alignment, file_alignment = struct.unpack_from("<2I", data, optional + 32)
    rva = align(max(va + max(vs, rs) for _, va, vs, rs, _ in pe.sections), section_alignment)
    base = pe.image_base + rva
    blob = bytearray()

    def add(payload, alignment=4):
        blob.extend(bytes(align(len(blob), alignment) - len(blob)))
        offset = len(blob)
        blob.extend(payload)
        return base + offset

    imports_rva, _ = struct.unpack_from("<2I", data, optional + 104)
    descriptors = bytearray()
    current = pe.read_va(pe.image_base + imports_rva, 2048)
    for index in range(0, len(current), 20):
        descriptor = current[index:index + 20]
        if descriptor == bytes(20):
            break
        descriptors.extend(descriptor)
    names = [add(b"\0\0" + name.encode() + b"\0", 2) - pe.image_base for name in EXPORTS]
    lookup = add(struct.pack(f"<{len(names) + 1}I", *names, 0))
    iat = add(struct.pack(f"<{len(names) + 1}I", *names, 0))
    library = add(b"EsteriaAppearance.dll\0")
    descriptors.extend(struct.pack("<5I", lookup - pe.image_base, 0, 0,
                                   library - pe.image_base, iat - pe.image_base))
    descriptors.extend(bytes(20))
    import_table = add(descriptors)
    add(b"ESTERIA_APPEARANCE_NATIVE_V1\0")
    sites = []

    def offset(va):
        for _, relative, _, size, raw in pe.sections:
            if relative <= va - pe.image_base < relative + size:
                return raw + va - pe.image_base - relative
        raise ValueError(f"VA {va:x} is not file-backed")

    def redirect(va, expected, code):
        if pe.read_va(va, len(expected)) != expected:
            raise ValueError(f"Patch-site fingerprint differs at {va:x}")
        destination = base + align(len(blob), 4)
        continuation = va + len(expected)
        payload = code(destination) if callable(code) else code
        payload += b"\xE9" + struct.pack("<i", continuation - destination - len(payload) - 5)
        add(payload)
        start = offset(va)
        replacement = b"\xE9" + struct.pack("<i", destination - va - 5) + b"\x90" * (len(expected) - 5)
        data[start:start + len(expected)] = replacement
        sites.append({"va": hex(va), "before": expected.hex(), "thunk": hex(destination)})

    # Source folds preserve flags and all registers except the native destination.
    call_source = b"\xFF\x15" + struct.pack("<I", iat + 4)
    for va in (0x00829091, 0x008290BC):
        redirect(va, bytes.fromhex("0fb74e088b5710"),
                 b"\x9C\x50\x52\x57\x56" + call_source + b"\x83\xC4\x08\x89\xC1\x5A\x58\x9D\x8B\x57\x10")
    redirect(0x0083619F, bytes.fromhex("0fb75c0b0803d1"),
             b"\x9C\x50\x51\x52\x8D\x04\x0B\xFF\xB6\x70\x01\x00\x00\x50"
             + call_source + b"\x83\xC4\x08\x89\xC3\x5A\x59\x58\x9D\x03\xD1")
    redirect(0x00836240, bytes.fromhex("66895a080fb7520a"),
             bytes.fromhex("9c5089d8c1e81066894202589d66895a080fb7520a"))
    redirect(0x0082C7ED, bytes.fromhex("8b0410394508"), bytes.fromhex("0fb70410394508"))
    redirect(0x004ED945, bytes.fromhex("8b4b386a00"),
             b"\x9C\x60\x53\xFF\x15" + struct.pack("<I", iat + 12)
             + b"\x83\xC4\x04\x61\x9D\x8B\x4B\x38\x6A\x00")
    def restore_skin(destination):
        code = b"\x9C\x60\x57\xFF\x15" + struct.pack("<I", iat + 16)
        code += b"\x83\xC4\x04\x61\x9D\x8B\xCF"
        return code + b"\xE8" + struct.pack("<i", 0x00837A40 - destination - len(code) - 5)

    redirect(0x0083853C, bytes.fromhex("8bcfe8fdf4ffff"), restore_skin)
    skill_race = (b"\x9C\x50\x52\xFF\x75\x08\xFF\x15" + struct.pack("<I", iat + 20)
                  + b"\x83\xC4\x04\x89\xC1\x5A\x58\x9D")
    redirect(0x00810F0A, bytes.fromhex("8b4d0883c1ff"), skill_race + b"\x83\xC1\xFF")
    redirect(0x0081033D, bytes.fromhex("8b4d085683c1ff"), skill_race + b"\x56\x83\xC1\xFF")
    def invoke_extra(index, push, original):
        return b"\x9C\x60" + push + b"\xFF\x15" + struct.pack("<I", iat + index * 4) + b"\x83\xC4\x04\x61\x9D" + original

    # CMSG_CHAR_CREATE's existing unused outfit byte carries the sixth value, preserving packet length.
    redirect(0x006B174C, bytes.fromhex("8d4de8518bcf"),
             invoke_extra(6, b"\x8D\x45\xE8\x50", bytes.fromhex("8d4de8518bcf")))
    # Strip the authenticated roster extension before the client's stock enum handler sees it.
    redirect(0x00464F89, bytes.fromhex("8b55105752"),
             b"\x9C\x60\x83\x7D\x0C\x3B\x75\x0A\x57\xFF\x15"
             + struct.pack("<I", iat + 28) + b"\x83\xC4\x04\x61\x9D\x8B\x55\x10\x57\x52")
    # Character Select passes its component in ECX to the shared component refresh.
    redirect(0x004E3E74, bytes.fromhex("538d95f8fdffff"),
             invoke_extra(8, b"\x51", bytes.fromhex("538d95f8fdffff")))
    # Native update dispatch uses unit field 0x93; intercept its padding callback without stealing other fields.
    redirect(0x006E476E, bytes.fromhex("83c41c5f5ec3"),
             b"\x9C\x60\xFF\x15" + struct.pack("<I", iat + 40) + b"\x61\x9D\x83\xC4\x1C\x5F\x5E\xC3")
    # The common unit hair refresh provides the unit pointer in ESI and its component in EDI.
    redirect(0x0052E65D, bytes.fromhex("8b8608100000"),
             invoke_extra(9, b"\x56", bytes.fromhex("8b8608100000")))
    # Read padding from the completed object update, without registering an unsupported old-value cache slot.
    redirect(0x004D6C86, bytes.fromhex("5eb801000000"),
             invoke_extra(9, b"\x56", bytes.fromhex("5eb801000000")))
    # Release component-keyed appearance state before the stock component destructor frees the object.
    free_component = bytes.fromhex("558bec568b3580b8b600")
    redirect(0x004F16C0, free_component,
             free_component[:3] + invoke_extra(15, b"\xFF\x75\x08", free_component[3:]))
    for va, expected in ((0x004EA6B0, "558bec568bf1"), (0x004EA490, "558bec568bf1"),
                         (0x004EA2F0, "558bec8b1564b8b600"), (0x004F1FC0, "558bec83ec18")):
        redirect(va, bytes.fromhex(expected), invoke_extra(11, b"\x51", bytes.fromhex(expected)))
    redirect(0x004F3BA3, bytes.fromhex("8b4d1483f904"),
             invoke_extra(12, b"\x8D\x45\x08\x50", bytes.fromhex("8b4d1483f904")))
    redirect(0x004F3B53, bytes.fromhex("8b4d1483f904"),
             invoke_extra(12, b"\x8D\x45\x08\x50", bytes.fromhex("8b4d1483f904")))
    def direct_getter(expected, operation, cleanup, prologue=True):
        prefix = expected[:3] if prologue else b""
        # Arguments are captured before any stock getter dereferences the cached section table.
        args = b"\x8D\x45\x08" if prologue else b"\x8D\x44\x24\x28"
        handled = b"\x61\x9D" + (b"\x5D" if prologue else b"") + b"\xC2" + struct.pack("<H", cleanup)
        code = prefix + b"\x9C\x60" + args + b"\x50\x6A" + bytes([operation]) + b"\x51\xFF\x15"
        # The MSVC x86 bool return is AL; EAX's other bits may still contain a pointer on false.
        code += struct.pack("<I", iat + 52) + b"\x83\xC4\x0C\x84\xC0\x74" + bytes([len(handled)])
        return code + handled + b"\x61\x9D" + (expected[3:] if prologue else expected)

    for va, fingerprint, operation, cleanup, prologue in (
            (0x004EA0B0, "8b1564b8b600", 0, 4, False),
            (0x004EA150, "558bec8b1564b8b600", 1, 8, True),
            (0x004EA1F0, "558bec8b450c", 2, 24, True)):
        expected = bytes.fromhex(fingerprint)
        redirect(va, expected, direct_getter(expected, operation, cleanup, prologue))
    redirect(0x004F3B10, bytes.fromhex("558bec8b4d0c"),
             b"\x55\x8B\xEC\x9C\x60\x8D\x45\x08\x50\xFF\x15" + struct.pack("<I", iat + 56)
             + b"\x83\xC4\x04\x83\xF8\xFF\x74\x08\x89\x44\x24\x1C\x61\x9D\x5D\xC3"
             + b"\x61\x9D\x8B\x4D\x0C")
    call_draw = b"\xFF\x15" + struct.pack("<I", iat + 8)
    for va in (0x008205CB, 0x00820654, 0x008206D0):
        # Preserve the draw context in the descriptor's not-yet-written primitive field.
        redirect(va, bytes.fromhex("8bb690000000"), bytes.fromhex("8975f08bb690000000"))
    for va in (0x008205DD, 0x00820666):
        redirect(va, bytes.fromhex("0fb776088d4c01ff"),
                 b"\x9C\x50\x51\x52\xFF\x75\xF0\x56" + call_draw
                 + b"\x83\xC4\x08\x89\xC6\x5A\x59\x58\x9D\x8D\x4C\x01\xFF")
    redirect(0x008206DE, bytes.fromhex("0fb7560883e801"),
             b"\x9C\x50\x51\xFF\x75\xF0\x56" + call_draw
             + b"\x83\xC4\x08\x89\xC2\x59\x58\x9D\x83\xE8\x01")
    redirect(0x00820B9C, bytes.fromhex("0fb750088955d4"),
             b"\x9C\x50\x51\x56\x50" + call_draw + b"\x83\xC4\x08\x89\xC2\x59\x58\x9D\x89\x55\xD4")

    # A Lua callback must remain in the executable's existing .text validation range.
    text_section = next(s for s in pe.sections if s[0] == ".text")
    _, text_rva, text_size, _, text_raw = text_section
    cave = pe.data.rfind(b"\xCC" * 16, text_raw, text_raw + text_size)
    if cave < 0:
        raise ValueError("No verified compiler-padding callback island")
    callback_va = pe.image_base + text_rva + cave - text_raw
    data[cave:cave + 6] = b"\xFF\x25" + struct.pack("<I", iat)
    if pe.read_va(0x00AC42BC, 4) != struct.pack("<I", 0x004E0B50):
        raise ValueError("CycleCharCustomization table is no longer stock")
    struct.pack_into("<I", data, offset(0x00AC42BC), callback_va)
    raw = align(len(data), file_alignment)
    data.extend(bytes(raw - len(data)))
    data.extend(blob)
    raw_size = align(len(blob), file_alignment)
    data.extend(bytes(raw_size - len(blob)))
    struct.pack_into("<8s8I", data, new_header, b".eapp\0\0\0", len(blob), rva, raw_size, raw, 0, 0, 0, 0xE0000060)
    struct.pack_into("<H", data, nt + 6, section_count + 1)
    struct.pack_into("<I", data, optional + 56, align(rva + len(blob), section_alignment))
    struct.pack_into("<2I", data, optional + 104, import_table - pe.image_base, len(descriptors))
    struct.pack_into("<I", data, optional + 64, 0)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)
    result = {"source_sha256": EXPECTED_SHA256, "patched_sha256": hashlib.sha256(data).hexdigest(),
              "section_va": hex(base), "imports": list(EXPORTS), "lua_callback_va": hex(callback_va), "sites": sites}
    (output.parent / "exe-patch-report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=CLIENT)
    parser.add_argument("--output", type=Path, default=STAGE / "Wow.exe")
    args = parser.parse_args()
    print(json.dumps(patch(args.source, args.output), indent=2))
