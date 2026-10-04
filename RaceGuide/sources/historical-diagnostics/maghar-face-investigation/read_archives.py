import ctypes as c
import ctypes.wintypes as w
import struct
import sys

pid = int(sys.argv[1])
nt = c.WinDLL('ntdll')
k = c.WinDLL('kernel32', use_last_error=True)
nt.NtQuerySystemInformation.argtypes = [w.ULONG, c.c_void_p, w.ULONG, c.POINTER(w.ULONG)]
k.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
k.OpenProcess.restype = w.HANDLE
k.DuplicateHandle.argtypes = [w.HANDLE, w.HANDLE, w.HANDLE, c.POINTER(w.HANDLE), w.DWORD, w.BOOL, w.DWORD]
k.GetCurrentProcess.restype = w.HANDLE
k.GetFileType.argtypes = [w.HANDLE]
k.GetFinalPathNameByHandleW.argtypes = [w.HANDLE, w.LPWSTR, w.DWORD, w.DWORD]
k.CloseHandle.argtypes = [w.HANDLE]
size = 1 << 20
while True:
    buffer = c.create_string_buffer(size)
    needed = w.ULONG()
    status = nt.NtQuerySystemInformation(64, buffer, size, c.byref(needed))
    if status == 0:
        break
    if status != -1073741820:
        raise OSError(hex(status & 0xffffffff))
    size = max(size * 2, needed.value)
count = struct.unpack_from('<Q', buffer)[0]
process = k.OpenProcess(0x40, False, pid)
for i in range(count):
    _, owner, handle, _, _, _, _, _ = struct.unpack_from('<QQQIHHII', buffer, 16 + i * 40)
    if owner != pid:
        continue
    duplicate = w.HANDLE()
    if not k.DuplicateHandle(process, handle, k.GetCurrentProcess(), c.byref(duplicate), 0, False, 2):
        continue
    try:
        if k.GetFileType(duplicate) != 1:
            continue
        path = c.create_unicode_buffer(4096)
        if k.GetFinalPathNameByHandleW(duplicate, path, len(path), 0):
            if '.mpq' in path.value.lower():
                print(path.value, flush=True)
    finally:
        k.CloseHandle(duplicate)
k.CloseHandle(process)
