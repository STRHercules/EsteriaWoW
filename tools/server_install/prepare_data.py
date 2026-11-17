"""Install pinned terrain and Esteria DBCs into a dedicated server-data directory."""
import argparse
import hashlib
import json
import shutil
import struct
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[2]
BASE_URL = "https://github.com/wowgaming/client-data/releases/download/v20.0/Data.zip"
BASE_SHA256 = "a3d4df635ae6c2c8f08052c32a79e0f806955150ad36b014a823dd08a32a4610"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def destination(root, name):
    path = root.joinpath(*PurePosixPath(name).parts)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Archive path escapes data directory: {name}")
    return path


def verify(data, manifest):
    for name, expected in manifest["files"].items():
        path = destination(data, name)
        if not path.is_file() or path.stat().st_size != expected["size"] or digest(path) != expected["sha256"]:
            raise ValueError(f"Missing or modified server DBC: {name}")
    for directory in ("maps", "vmaps", "mmaps"):
        if not (data / directory).is_dir() or not any((data / directory).iterdir()):
            raise ValueError(f"Missing terrain directory: {directory}")
    count = 0
    for path in (data / "mmaps").glob("*.mmtile"):
        with path.open("rb") as stream:
            header = stream.read(12)
        if (len(header) != 12 or struct.unpack("<III", header)[0] != 0x4D4D4150
                or struct.unpack("<III", header)[2] != manifest["mmap_version"]):
            raise ValueError(f"Incompatible MMAP version: {path.name}; expected {manifest['mmap_version']}")
        count += 1
    if not count:
        raise ValueError("No navigation tiles found")


def install(data, bundle, base_archive=None):
    manifest = json.loads((bundle / "manifest.json").read_text())
    marker = data / "esteria-data.json"
    if marker.exists():
        if json.loads(marker.read_text()) != manifest:
            raise ValueError("Different Esteria snapshot in this volume; use a new volume")
        verify(data, manifest)
        print("Esteria server data verified", flush=True)
        return
    data.mkdir(parents=True, exist_ok=True)
    archive = bundle / manifest["dbc_archive"]
    if digest(archive) != manifest["sha256"]:
        raise ValueError("Esteria DBC archive checksum mismatch")
    with tempfile.TemporaryDirectory(prefix="esteria-data-") as temporary:
        base = Path(base_archive) if base_archive else Path(temporary) / "Data.zip"
        if not base_archive:
            print("Downloading pinned v20 terrain (1.2 GB compressed)...", flush=True)
            request = Request(BASE_URL, headers={"User-Agent": "EsteriaWoW-server-installer"})
            with urlopen(request, timeout=120) as response, base.open("wb") as output:
                shutil.copyfileobj(response, output)
        if digest(base) != BASE_SHA256:
            raise ValueError("Terrain checksum mismatch; use the official v20.0 Data.zip")
        with zipfile.ZipFile(base) as terrain:
            for member in terrain.infolist():
                parts = PurePosixPath(member.filename).parts
                if not parts or parts[0] not in ("maps", "vmaps", "mmaps", "Cameras") or member.is_dir():
                    continue
                target = destination(data, member.filename)
                target.parent.mkdir(parents=True, exist_ok=True)
                with terrain.open(member) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)
        with tarfile.open(archive) as dbcs:
            for member in dbcs:
                if not member.isfile():
                    continue
                if member.name not in manifest["files"]:
                    raise ValueError(f"Unexpected DBC archive member: {member.name}")
                target = destination(data, member.name)
                target.parent.mkdir(parents=True, exist_ok=True)
                with dbcs.extractfile(member) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)
    verify(data, manifest)
    marker.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("Esteria server data installed and verified", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, default=ROOT / "data/server")
    parser.add_argument("--base-archive", type=Path, help="Already downloaded official v20 Data.zip")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    try:
        if args.check_only:
            verify(args.data, json.loads((args.bundle / "manifest.json").read_text()))
        else:
            install(args.data, args.bundle, args.base_archive)
    except (ValueError, OSError, zipfile.BadZipFile, tarfile.TarError) as error:
        raise SystemExit(str(error))
