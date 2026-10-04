import csv
import ctypes as c
import ctypes.wintypes as w
import io
import json
import struct
import subprocess

k = c.WinDLL('kernel32', use_last_error=True)
k.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
k.OpenProcess.restype = w.HANDLE
k.ReadProcessMemory.argtypes = [w.HANDLE, c.c_void_p, c.c_void_p, c.c_size_t, c.POINTER(c.c_size_t)]
k.CloseHandle.argtypes = [w.HANDLE]
processes = subprocess.check_output(['tasklist', '/FO', 'CSV', '/NH'], text=True)
for process in csv.reader(io.StringIO(processes)):
    if process[0].lower() != 'wow.exe':
        continue
    h = k.OpenProcess(0x1010, False, int(process[1]))

    def read(a, n):
        b = c.create_string_buffer(n)
        got = c.c_size_t()
        if not k.ReadProcessMemory(h, a, b, n, c.byref(got)):
            return b''
        return b.raw[:got.value]

    def u(a):
        b = read(a, 4)
        return int.from_bytes(b, 'little') if len(b) == 4 else 0

    ch = u(0xb6b1a0)
    inst = u(ch + 0x38)
    model = u(inst + 0x2c)
    skin = u(model + 0x170)
    arr = u(skin + 0x20)
    vis = u(inst + 0x9c)
    draw = u(model + 0x18c)
    count = u(skin + 0x1c)
    assert count < 1024
    result = {'pid': int(process[1]), 'ch': hex(ch), 'inst': hex(inst), 'model': hex(model),
              'skin': hex(skin), 'draw': hex(draw), 'skinheader': read(skin, 48).hex(),
              'geometry': [u(ch + 0x144 + i * 4) for i in range(19)],
              'appearance': [u(ch + i) for i in (0x18, 0x1c, 0x24, 0x28, 0x2c, 0x30, 0x34)],
              'model_flags': [u(model + i) for i in (0x190, 0x178, 0x17c)],
              'code': {hex(a): read(a, 12).hex() for a in (0x829091, 0x8290bc, 0x83619f, 0x836240,
                         0x82c7ed, 0x8205cb, 0x8205dd, 0x8206d0, 0x8206de, 0x838490, 0x835ae0)},
              'sections': []}
    for i in range(count):
        blob = read(arr + i * 48, 48)
        if len(blob) != 48:
            break
        geo, high, start, vertices, index, indices = struct.unpack_from('<6H', blob)
        runtime = read(draw + i * 48, 48)
        result['sections'].append({'i': i, 'geo': geo, 'high': high, 'vertices': vertices,
                                   'start': index | high << 16, 'indices': indices, 'vis': u(vis + i * 4),
                                   'draw': runtime[:12].hex()})
    from pathlib import Path
    Path(__file__).with_name('live-geometry.json').write_text(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != 'sections'}, indent=2))
    print(json.dumps([s for s in result['sections'] if s['vis'] or s['geo'] == 0], indent=2))
    k.CloseHandle(h)
