import struct
import urllib.request
from pathlib import Path

ids = [
    132355, 135826, 136197, 236412, 236458, 236695, 237538,
    254105, 254651, 254652, 298659, 298680, 1035504,
]
cache = Path(r"g:\risServer\Esteria - Client\Data\Retail\Cache\Retail\wow-88d5e8ef05ec5a8446cdec93d142d7c6\decoded\2\strict")

def checksum(data):
    value = 14695981039346656037
    for byte in data:
        value ^= byte
        value = (value * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return value

for fdid in ids:
    dest = cache / ("id-%d.bin" % fdid)
    if dest.exists():
        print("have", fdid)
        continue
    url = "https://wago.tools/api/casc/%d?download" % fdid
    request = urllib.request.Request(url, headers={"User-Agent": "esteria"})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read()
    if payload[:4] != b"BLP2":
        print("bad", fdid, payload[:8])
        continue
    header = struct.pack("<IIQ", 0x31434457, len(payload), checksum(payload))
    dest.write_bytes(header + payload)
    print("ok", fdid, len(payload))
