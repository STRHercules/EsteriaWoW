import ctypes as c
import struct
import sys
from pathlib import Path
sys.path.insert(0,r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
k=c.WinDLL('kernel32',use_last_error=True)
k.OpenProcess.argtypes=[c.c_uint32,c.c_int,c.c_uint32];k.OpenProcess.restype=c.c_void_p
k.ReadProcessMemory.argtypes=[c.c_void_p,c.c_void_p,c.c_void_p,c.c_size_t,c.POINTER(c.c_size_t)]
h=k.OpenProcess(0x410,False,int(sys.argv[1]))
def read(a,n):
 b=c.create_string_buffer(n);z=c.c_size_t();assert k.ReadProcessMemory(h,a,b,n,c.byref(z));return b.raw[:z.value]
cs=Cs(CS_ARCH_X86,CS_MODE_32)
for at in [0x4d6c86,0x52e65d,0x4ed945]:
 b=read(at,8);print(hex(at),b.hex());
 if b[0]==0xe9:
  dest=at+5+struct.unpack_from('<i',b,1)[0]
  for i in cs.disasm(read(dest,70),dest):
   print(hex(i.address),i.mnemonic,i.op_str)
   if i.mnemonic=='call'and i.op_str.startswith('dword ptr [0x'):
    ptr=int(i.op_str.split('[')[1][:-1],16);target=struct.unpack('<I',read(ptr,4))[0]
    print(' IAT target',hex(target),'bytes',read(target,30).hex())
