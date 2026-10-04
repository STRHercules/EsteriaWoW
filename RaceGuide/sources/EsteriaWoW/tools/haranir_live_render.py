"""Read-only creator diagnostics: loaded Haranir meshes, character layers and actual texture bindings."""

import ctypes as c
import json
import struct
import sys

k = c.WinDLL("kernel32", use_last_error=True)
k.OpenProcess.argtypes = [c.c_uint32, c.c_int, c.c_uint32]
k.OpenProcess.restype = c.c_void_p
k.ReadProcessMemory.argtypes = [c.c_void_p, c.c_void_p, c.c_void_p, c.c_size_t, c.POINTER(c.c_size_t)]
k.CloseHandle.argtypes = [c.c_void_p]


def capture(pid):
    handle = k.OpenProcess(0x410, False, pid)
    if not handle:
        raise OSError(c.get_last_error())

    def read(address, size):
        buffer, count = c.create_string_buffer(size), c.c_size_t()
        if not address or not k.ReadProcessMemory(handle, address, buffer, size, c.byref(count)):
            raise OSError(hex(address))
        if count.value != size:
            raise OSError("Short process read")
        return buffer.raw

    def u(address):
        return struct.unpack("<I", read(address, 4))[0]

    try:
        component = u(0x00B6B1A0)
        if not component or u(component + 0x18) not in (50, 51):
            raise ValueError("Leave a Haranir visible in Character Create")
        result = {"component": hex(component), "fields": {hex(at): u(component + at)
            for at in (0x18, 0x1C, 0x24, 0x28, 0x2C, 0x30, 0x34)}, "layers": []}
        for kind in range(5):
            for slot in range(3):
                pointer = u(component + 0x194 + (kind * 3 + slot) * 4)
                if pointer:
                    result["layers"].append({"kind": kind, "slot": slot, "pointer": hex(pointer),
                        "path": read(pointer + 0x24, 128).split(b"\0")[0].decode(errors="replace"),
                        "flags": hex(u(pointer + 0xB0)), "image": hex(u(pointer + 0xAC))})
        instance = u(component + 0x38)
        if not instance:
            raise ValueError("Creator model instance is absent")
        model, visible, bindings = u(instance + 0x2C), u(instance + 0x9C), u(instance + 0xA4)
        header, skin = u(model + 0x150), u(model + 0x170)
        result.update(instance=hex(instance), flags=hex(u(instance + 0x10)),
            model_path=read(model + 0x3C, 128).split(b"\0")[0].decode(errors="replace"), textures=[], meshes=[])
        count, table = u(header + 0x50), u(header + 0x54)
        if count > 256:
            raise ValueError("Unexpected native texture table length")
        for i in range(count):
            pointer = u(bindings + i * 4)
            row = {"index": i, "type": u(table + i * 16), "pointer": hex(pointer)}
            if pointer:
                data = read(pointer, 160)
                row["texture_data"] = data.hex()
                row["width"], row["height"] = struct.unpack_from("<2H", data, 0x4C)
                row["name"] = data[0x6C:].split(b"\0")[0].decode(errors="replace")
            result["textures"].append(row)
        count, table = u(skin + 0x1C), u(skin + 0x20)
        if count > 1024:
            raise ValueError("Unexpected native mesh table length")
        for i in range(count):
            mesh = read(table + i * 48, 48)
            result["meshes"].append({"index": i, "id": struct.unpack_from("<H", mesh)[0],
                "visible": u(visible + i * 4), "vertices": struct.unpack_from("<H", mesh, 6)[0]})
        return result
    finally:
        k.CloseHandle(handle)


if __name__ == "__main__":
    print(json.dumps(capture(int(sys.argv[1])), indent=2))
