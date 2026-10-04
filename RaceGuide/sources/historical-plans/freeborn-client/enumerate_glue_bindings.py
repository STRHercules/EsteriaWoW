"""Enumerate the Lua functions registered in the client's GLUE (pre-world) state.

`SetCharacterCreateFacing` is a glue-only binding, so its name pointer lives inside the
glue state's Lua function table.  Finding that table lets us enumerate every function the
glue environment exposes -- decisive for "can the character-create screen reach SetCVar?".

Usage:  python enumerate_glue_bindings.py "G:\\3.3.5a - Dev\\Wow.exe" [anchor_name]
"""

from __future__ import annotations

import struct
import sys


def read_sections(data: bytes):
    pe_off = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe_off : pe_off + 4] != b"PE\0\0":
        raise SystemExit("not a PE file")
    image_base = struct.unpack_from("<I", data, pe_off + 0x34)[0]
    n_sections = struct.unpack_from("<H", data, pe_off + 0x06)[0]
    opt_size = struct.unpack_from("<H", data, pe_off + 0x14)[0]
    sec_off = pe_off + 0x18 + opt_size
    sections = []
    for i in range(n_sections):
        base = sec_off + i * 40
        name = data[base : base + 8].rstrip(b"\0").decode("ascii", "replace")
        vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", data, base + 8)
        sections.append((name, vaddr, vsize, rawptr, rawsize))
    return image_base, sections


def off_to_va(sections, off: int):
    for _name, vaddr, vsize, rawptr, rawsize in sections:
        if rawptr <= off < rawptr + rawsize:
            return vaddr + (off - rawptr)
    return None


def va_to_off(sections, va: int):
    for _name, vaddr, vsize, rawptr, rawsize in sections:
        if vaddr <= va < vaddr + max(vsize, rawsize):
            cand = rawptr + (va - vaddr)
            if 0 <= cand < len(sections) + (1 << 62):
                return cand
    return None


def cstr(data: bytes, off: int, limit: int = 80) -> str:
    if off is None or not (0 <= off < len(data)):
        return ""
    end = data.find(b"\0", off, off + limit)
    if end < 0:
        return ""
    raw = data[off:end]
    if not raw or any(b < 0x20 or b > 0x7E for b in raw):
        return ""
    return raw.decode("ascii")


def main() -> int:
    exe = sys.argv[1]
    anchor = sys.argv[2] if len(sys.argv) > 2 else "SetCharacterCreateFacing"
    data = open(exe, "rb").read()
    image_base, sections = read_sections(data)
    print(f"image base 0x{image_base:08X}, {len(sections)} sections")

    needle = anchor.encode() + b"\0"
    anchor_offs = []
    start = 0
    while True:
        hit = data.find(needle, start)
        if hit < 0:
            break
        anchor_offs.append(hit)
        start = hit + 1
    print(f"'{anchor}' string occurrences: {[hex(o) for o in anchor_offs]}")

    for aoff in anchor_offs:
        ava = off_to_va(sections, aoff)
        print(f"\n--- string at file 0x{aoff:X} (VA 0x{ava:08X}) ---")
        for label, target in (("VA", ava), ("RVA", ava - image_base)):
            packed = struct.pack("<I", target)
            hits = []
            s = 0
            while True:
                h = data.find(packed, s)
                if h < 0:
                    break
                hits.append(h)
                s = h + 1
            print(f"  pointers to {label} 0x{target:08X}: {len(hits)} -> {[hex(h) for h in hits[:8]]}")
            for h in hits[:4]:
                # luaL_Reg entries are {name, func}; the name pointer may sit anywhere in the
                # entry, so normalise to the entry start and walk both directions.
                entry = h if (h % 4 == 0) else h
                names = []
                cursor = entry
                while True:
                    prev = cursor - 8
                    if prev < 0:
                        break
                    p = struct.unpack_from("<I", data, prev)[0]
                    if cstr(data, va_to_off(sections, p) or -1) == "":
                        break
                    cursor = prev
                    if len(names) > 400:
                        break
                    names.append(prev)
                names.reverse()
                names.append(entry)
                out = []
                cursor = entry + 8
                while len(out) < 800:
                    p = struct.unpack_from("<I", data, cursor)[0]
                    txt = cstr(data, va_to_off(sections, p) or -1)
                    if txt == "":
                        break
                    out.append(txt)
                    cursor += 8
                back = []
                cursor = entry
                while len(back) < 800:
                    cursor -= 8
                    if cursor < 0:
                        break
                    p = struct.unpack_from("<I", data, cursor)[0]
                    txt = cstr(data, va_to_off(sections, p) or -1)
                    if txt == "":
                        break
                    back.append(txt)
                names = list(reversed(back)) + [anchor] + out
                print(f"\n  === entry candidate at 0x{h:X}: {len(names)} names ===")
                for n in names:
                    print("     ", n)
                return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
