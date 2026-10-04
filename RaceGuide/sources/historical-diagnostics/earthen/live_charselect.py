import ctypes as c
import struct
import sys
k=c.WinDLL('kernel32',use_last_error=True)
k.OpenProcess.argtypes=[c.c_uint32,c.c_int,c.c_uint32];k.OpenProcess.restype=c.c_void_p
k.ReadProcessMemory.argtypes=[c.c_void_p,c.c_void_p,c.c_void_p,c.c_size_t,c.POINTER(c.c_size_t)]
h=k.OpenProcess(0x410,False,int(sys.argv[1]))
def read(a,n):
 b=c.create_string_buffer(n);z=c.c_size_t();assert k.ReadProcessMemory(h,a,b,n,c.byref(z));return b.raw[:z.value]
def u(a):return struct.unpack('<I',read(a,4))[0]
count=u(0xb6b23c);rows=u(0xb6b240)
assert count<=100
print('selected index',u(0xac436c),'roster rows',count)
for i in range(count):
 row=rows+i*0x198;b=read(row,0x198)
 if b[0x178]not in (48,49):continue
 component=u(row+0x188)
 print('row',i,'guid',struct.unpack_from('<Q',b)[0], 'appearance',list(b[0x178:0x180]),'component',hex(component))
 if component:
  print('fields',[(hex(x),u(component+x))for x in [0x18,0x1c,0x28,0x2c,0x34,0x24,0x30]],'instance',hex(u(component+0x38)))
  print('compositor',[(hex(x),hex(u(component+x)))for x in [0x3c,0x190,0x194,0x198,0x19c,0x1a0,0x1a4,0x1a8]])
  instance=u(component+0x38)
  if instance:
   model=u(instance+0x2c);skin=u(model+0x170);meshes=u(skin+0x20);vis=u(instance+0x9c);n=u(skin+0x1c)
   assert n<1024
   print('enabled feet',[geo for index in range(n) for geo in [struct.unpack('<H',read(meshes+index*48,2))[0]]if 2000<=geo<2100 and u(vis+index*4)])
