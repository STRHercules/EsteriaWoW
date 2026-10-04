import ctypes as c
import json
import struct
import sys
from pathlib import Path

k = c.WinDLL('kernel32', use_last_error=True)
k.OpenProcess.argtypes = [c.c_uint32, c.c_int, c.c_uint32]
k.OpenProcess.restype = c.c_void_p
k.ReadProcessMemory.argtypes = [c.c_void_p, c.c_void_p, c.c_void_p, c.c_size_t, c.POINTER(c.c_size_t)]
k.CloseHandle.argtypes = [c.c_void_p]
process = k.OpenProcess(0x410, False, int(sys.argv[1]))
assert process
def read(address, size):
    buffer = c.create_string_buffer(size)
    n = c.c_size_t()
    if not address or not k.ReadProcessMemory(process, address, buffer, size, c.byref(n)) or n.value != size:
        raise OSError(hex(address))
    return bytes(buffer)
def u(address):
    return struct.unpack('<I', read(address,4))[0]
connection = u(0xc79ce0)
manager = u(connection+0x2ed0)
pointer = u(manager+0xac)
objects=[]
seen=set()
while pointer and not pointer & 1 and pointer not in seen and len(seen)<10000:
    seen.add(pointer)
    if u(pointer+0x14) == 4:
        component = u(pointer+0xb4c)
        fields = u(pointer+0xd0)
        player_fields = u(pointer+0x8)
        row={'unit':hex(pointer),'guid':struct.unpack('<Q',read(pointer+0x30,8))[0],
             'component':hex(component),'fields':hex(fields),'player_fields':hex(player_fields),
             'appearance':{hex(at):u(component+at)for at in [0x18,0x1c,0x24,0x28,0x2c,0x30,0x34]},
             'padding':u(fields+0x8d*4),'player_bytes_raw':[hex(u(player_fields+at*4))for at in [0x36,0x94,0x95]],
             'appearance_network':read(u(pointer+0x1008)+0x14,5).hex(),
             'geometry':[u(component+0x144+i*4)for i in range(19)]}
        instance=u(component+0x38)
        model=u(instance+0x2c)
        skin=u(model+0x170)
        count=u(skin+0x1c)
        assert count<1024
        meshes=u(skin+0x20)
        visible=u(instance+0x9c)
        row['model_path']=read(model+0x3c,128).split(b'\0')[0].decode(errors='replace')
        row['meshes']=[{'id':struct.unpack('<H',read(meshes+i*48,2))[0],'visible':u(visible+i*4)}for i in range(count)]
        objects.append(row)
    pointer=u(pointer+0x3c)
k.CloseHandle(process)
Path(__file__).with_name('live-appearance.json').write_text(json.dumps(objects,indent=2))
for row in objects:
    print({key:value for key,value in row.items()if key!='meshes'})
    print('visible',[m for m in row['meshes']if m['visible']])
