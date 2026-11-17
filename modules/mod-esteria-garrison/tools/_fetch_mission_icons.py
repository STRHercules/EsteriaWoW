"""Download the garrison mission-type icon sheet from the CDN into the client decoded cache."""
import hashlib
import struct
import urllib.request
from pathlib import Path

FDID = 1000173
BUILD = "88d5e8ef05ec5a8446cdec93d142d7c6"
CACHE = Path(r"g:\risServer\Esteria - Client\Data\Retail\Cache\Retail") / ("wow-" + BUILD) / "decoded" / "2" / "strict" / ("id-%d.bin" % FDID)
LOCAL = Path(r"g:\risServer\_ref\retail_ui\interface\garrison\garrisonmissiontypeicons.blp")
URLS = [
    "https://wow.tools/casc/file/fdid?build=12.1.5.70448&filedataid=%d" % FDID,
    "https://wago.tools/api/casc/fdid?build=12.1.5.70448&filedataid=%d" % FDID,
    "https://wago.tools/api/casc/%d?download" % FDID,
]

def checksum(data: bytes) -> int:
    value = 14695981039346656037
    for byte in data:
        value ^= byte
        value = (value * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return value

def fetch() -> bytes:
    for url in URLS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            print("url", url, "status", resp.status, "bytes", len(data), "magic", data[:4])
            if data[:4] == b"BLP2":
                return data
        except Exception as exc:
            print("fail", url, type(exc).__name__, exc)
    raise SystemExit("CDN did not return a BLP")

def main():
    data = fetch()
    local = LOCAL.read_bytes()
    print("local", len(local), "sha", hashlib.sha256(local).hexdigest()[:16])
    print("cdn ", len(data), "sha", hashlib.sha256(data).hexdigest()[:16], "same", data == local)
    width, height = struct.unpack_from("<II", data, 12)
    print("size", width, height)
    envelope = struct.pack("<IIQ", 0x31434457, len(data), checksum(data)) + data
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_bytes(envelope)
    print("wrote", CACHE, "envelope", len(envelope))

if __name__ == "__main__":
    main()
