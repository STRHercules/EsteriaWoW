"""One-shot: does any client patch contain the garrison WDT files?"""
import ctypes as c
import sys
from pathlib import Path

sys.path.insert(0, r"G:\risServer\EsteriaWoW\tools")
from cars_mount_pack import Storm, H  # noqa: E402

storm = Storm(Path(r"G:\risServer\Esteria - Client\StormLib.dll"))
data = Path(r"G:\risServer\Esteria - Client\Data")
needles = [
    "World\\Maps\\1331\\1331.wdt",
    "World\\Maps\\1330\\1330.wdt",
    "World\\Maps\\1158\\1158.wdt",
    "World\\Maps\\1159\\1159.wdt",
    "World\\Maps\\1152\\1152.wdt",
    "World\\Maps\\1153\\1153.wdt",
]
patches = sorted(set(data.glob("*.MPQ")) | set(data.glob("*.mpq")), key=lambda p: p.name.lower())
print(f"patches {len(patches)}", flush=True)
for p in patches:
    h = H()
    # STREAM_FLAG_READ_ONLY | STREAM_FLAG_WRITE_SHARE: the client may still hold the archives
    if not storm.dll.SFileOpenArchive(str(p), 0, 0x300, c.byref(h)):
        print(f"SKIP {p.name} ({c.get_last_error()})", flush=True)
        continue
    try:
        hits = []
        for n in needles:
            fh = H()
            if storm.dll.SFileOpenFileEx(h, n.encode("ascii"), 0, c.byref(fh)):
                sz = storm.dll.SFileGetFileSize(fh, None)
                storm.dll.SFileCloseFile(fh)
                hits.append(f"{n.split(chr(92))[-1]}:{sz}")
        if "garrison" in p.name.lower():
            files = storm.list_files(h)
            print(f"GARRISON {p.name} entries={len(files)}", flush=True)
            for name, size, _, _ in files:
                print(f"  {name} {size}", flush=True)
        if hits:
            print(f"HIT {p.name} {hits}", flush=True)
    finally:
        storm.dll.SFileCloseArchive(h)
print("done", flush=True)
