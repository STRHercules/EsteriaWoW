"""Read live build12340 object notification lists and watch a selected list link."""
import ctypes as c
import struct
import sys

k = c.WinDLL('kernel32', use_last_error=True)
for name, args, result in (
    ('OpenProcess', [c.c_uint32, c.c_int, c.c_uint32], c.c_void_p),
    ('ReadProcessMemory', [c.c_void_p, c.c_void_p, c.c_void_p, c.c_size_t, c.POINTER(c.c_size_t)], c.c_int),
    ('CloseHandle', [c.c_void_p], c.c_int),
):
    fn = getattr(k, name)
    fn.argtypes, fn.restype = args, result

pid = int(sys.argv[1])
process = k.OpenProcess(0x410, False, pid)
if not process:
    raise c.WinError(c.get_last_error())

def read(address, size):
    buffer = c.create_string_buffer(size)
    count = c.c_size_t()
    if not k.ReadProcessMemory(process, address, buffer, size, c.byref(count)) or count.value != size:
        raise c.WinError(c.get_last_error())
    return bytes(buffer)

def u32(address):
    return struct.unpack('<I', read(address, 4))[0]

connection = u32(0xc79ce0)
manager = u32(connection + 0x2ed0)
objects = []
pointer = u32(manager + 0xac)
seen = set()
while pointer and not pointer & 1 and pointer not in seen and len(objects) < 10000:
    seen.add(pointer)
    blob = read(pointer, 0xe0)
    kind = struct.unpack_from('<I', blob, 0x14)[0]
    guid = struct.unpack_from('<Q', blob, 0x30)[0]
    head = struct.unpack_from('<3I', blob, 0x44)
    objects.append((pointer, kind, guid, head))
    pointer = struct.unpack_from('<I', blob, 0x3c)[0]
print('manager', hex(manager), 'objects', len(objects), flush=True)
if len(sys.argv) > 2:
    target = int(sys.argv[2], 16)
    print('target', hex(target), 'kind', u32(target + 0x14),
          'guid', hex(struct.unpack('<Q', read(target + 0x30, 8))[0]),
          'head', read(target + 0x44, 12).hex(), flush=True)
for pointer, kind, guid, head in objects:
    if kind != 3:
        continue
    print(hex(pointer), 'type', kind, 'guid', hex(guid), 'GUID-list', [hex(x) for x in head], flush=True)
k.CloseHandle(process)
