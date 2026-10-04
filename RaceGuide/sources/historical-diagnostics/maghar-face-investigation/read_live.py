import csv
import ctypes as c
import ctypes.wintypes as w
import hashlib
import io
import json
import struct
import subprocess
from pathlib import Path

k = c.WinDLL('kernel32', use_last_error=True)
k.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
k.OpenProcess.restype = w.HANDLE
k.ReadProcessMemory.argtypes = [w.HANDLE, c.c_void_p, c.c_void_p, c.c_size_t, c.POINTER(c.c_size_t)]
k.CloseHandle.argtypes = [w.HANDLE]
processes = subprocess.run(['tasklist', '/FO', 'CSV', '/NH'], capture_output=True, text=True, check=True).stdout
for process in csv.reader(io.StringIO(processes)):
    if process[0].lower() != 'wow.exe':
        continue
    pid = int(process[1])
    h = k.OpenProcess(0x1010, False, pid)

    def read(address, size):
        buffer = c.create_string_buffer(size)
        got = c.c_size_t()
        if not k.ReadProcessMemory(h, address, buffer, size, c.byref(got)):
            return b''
        return buffer.raw[:got.value]

    def u(address):
        data = read(address, 4)
        return struct.unpack('<I', data)[0] if len(data) == 4 else 0

    def text(address, size=128):
        return read(address, size).split(b'\0', 1)[0].decode('ascii', errors='replace')

    character = u(0xb6b1a0)
    result = {'pid': pid, 'character': hex(character), 'resolution': u(0xb6b5fc),
              'selection': {name: u(character + offset) for name, offset in
                            [('race', 0x18), ('sex', 0x1c), ('class', 0x20), ('hair', 0x24),
                             ('skin', 0x28), ('face', 0x2c), ('hairColor', 0x30), ('facial', 0x34)]},
              'code': {hex(address): read(address, 16).hex() for address in
                       [0x4ea0b0, 0x4ea490, 0x4ea1f0, 0x4ea6b0, 0x4f3930, 0x4f07d0, 0x825260]},
              'regions': [struct.unpack('<4I', read(0xb6b888 + i * 16, 16)) for i in range(10)],
              'textures': []}
    if character:
        from PIL import Image

        resolution = result['resolution']
        levels = u(0xb6b870)
        pixels = read(u(levels), resolution * resolution * 4) if 0 < resolution <= 2048 else b''
        if len(pixels) == resolution * resolution * 4:
            image = Image.frombytes('RGBA', (resolution, resolution), pixels, 'raw', 'BGRA')
            image_path = Path(__file__).parent / f'live-{pid}-composed.png'
            image.save(image_path)
            result['composed_image'] = str(image_path)
            result['composed_neon_pixels'] = sum(pixel[:3] == (0, 255, 0) for pixel in image.getdata())
        result['dirty'] = hex(u(character + 0xc))
        result['rebuild'] = hex(u(character + 8))
        result['compose_request'] = hex(u(character + 0x52c))
        for slot in range(15):
            entry = u(character + 0x194 + slot * 4)
            if not entry:
                continue
            data = read(entry, 0xb4)
            image = u(entry + 0xac)
            header = read(image, 20)
            texture = {'slot': slot, 'entry': hex(entry), 'name': text(entry + 0x24),
                       'width_height': struct.unpack_from('<2H', data, 0x1c),
                       'mips': data[0x20], 'alpha': data[0x21], 'flags': hex(u(entry + 0xb0)),
                       'image': hex(image), 'image_header': header.hex(), 'pending': hex(u(entry + 0x18))}
            if header[:4] == b'BLP2':
                offsets = struct.unpack('<16I', read(image + 20, 64))
                sizes = struct.unpack('<16I', read(image + 84, 64))
                length = max(offset + size for offset, size in zip(offsets, sizes))
                blob = read(image, length)
                texture['hash'] = hashlib.sha256(blob).hexdigest()
                (Path(__file__).parent / f'live-{pid}-slot{slot}.blp').write_bytes(blob)
            result['textures'].append(texture)
        instance = u(character + 0x38)
        bindings = u(instance + 0xa4)
        result['instance'] = hex(instance)
        result['bindings'] = [hex(u(bindings + i * 4)) for i in range(7)] if bindings else []
        for i in range(7):
            handle = u(bindings + i * 4)
            if handle:
                result.setdefault('gpu_handles', []).append({'slot': i, 'handle': hex(handle),
                                                           'raw': read(handle, 192).hex()})
    k.CloseHandle(h)
    (Path(__file__).parent / f'live-{pid}.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result), flush=True)
