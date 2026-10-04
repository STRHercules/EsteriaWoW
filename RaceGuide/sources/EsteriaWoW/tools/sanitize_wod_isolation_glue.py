"""Remove donor-nonexistent GlueXML entries from the private WoD isolation client.

The live Esteria client is never modified. If an offending isolation archive is
hard-linked to the live client, this script first replaces the isolation link
with a private byte-for-byte copy before removing entries with StormLib.
"""

from __future__ import annotations

import ctypes as c
import os
import shutil
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from cars_mount_pack import DLL_DEFAULT, H, Storm, U  # noqa: E402
from compare_wod_isolation_glue import DONOR, ISOLATION, effective_glue  # noqa: E402

LIVE_DATA = Path(r"G:\3.3.5a - Dev\Data")
ISO_DATA = ISOLATION


def ensure_remove_api(storm: Storm) -> None:
    fn = storm.dll.SFileRemoveFile
    fn.argtypes = [H, c.c_char_p, U]
    fn.restype = c.c_bool


def is_same_file(a: Path, b: Path) -> bool:
    try:
        return os.path.samefile(a, b)
    except OSError:
        return False


def private_copy_if_needed(iso_archive: Path) -> None:
    relative = iso_archive.relative_to(ISO_DATA)
    live_archive = LIVE_DATA / relative
    if not live_archive.is_file() or not is_same_file(iso_archive, live_archive):
        return
    temp = iso_archive.with_suffix(iso_archive.suffix + ".private-copy")
    if temp.exists():
        temp.unlink()
    shutil.copy2(live_archive, temp)
    iso_archive.unlink()
    temp.replace(iso_archive)
    if is_same_file(iso_archive, live_archive):
        raise RuntimeError(f"failed to detach isolation archive from live file: {iso_archive}")
    print(f"detached private copy: {iso_archive}")


def remove_entry(storm: Storm, archive_path: Path, entry: str) -> None:
    private_copy_if_needed(archive_path)
    handle = storm.open_archive(archive_path)
    try:
        if not storm.dll.SFileRemoveFile(handle, entry.encode("ascii"), 0):
            error = c.get_last_error()
            raise OSError(f"SFileRemoveFile failed: {archive_path} :: {entry} ({error})")
    finally:
        storm.dll.SFileCloseArchive(handle)
    print(f"removed {entry} from {archive_path.name}")


def main() -> int:
    storm = Storm(DLL_DEFAULT)
    ensure_remove_api(storm)

    donor_hashes, _ = effective_glue(DONOR, storm)
    for pass_index in range(1, 21):
        iso_hashes, iso_sources = effective_glue(ISOLATION, storm)
        extras = sorted(set(iso_hashes) - set(donor_hashes))
        if not extras:
            print(f"no donor-nonexistent effective GlueXML entries remain after {pass_index - 1} pass(es)")
            break
        print(f"pass {pass_index}: removing {len(extras)} extra effective GlueXML entries")
        for key in extras:
            source_text = iso_sources.get(key)
            if not source_text:
                raise RuntimeError(f"no source archive for extra GlueXML entry: {key}")
            remove_entry(storm, Path(source_text), key)
    else:
        raise RuntimeError("GlueXML sanitization did not converge")

    donor_hashes, _ = effective_glue(DONOR, storm)
    iso_hashes, iso_sources = effective_glue(ISOLATION, storm)
    differences = sorted(
        key for key in set(donor_hashes) | set(iso_hashes)
        if donor_hashes.get(key) != iso_hashes.get(key)
    )
    print(f"donor effective GlueXML files: {len(donor_hashes)}")
    print(f"isolation effective GlueXML files: {len(iso_hashes)}")
    print(f"remaining effective differences: {len(differences)}")
    for key in differences[:50]:
        print(f"  {key} <- {iso_sources.get(key, '<missing>')}")
    return 1 if differences else 0


if __name__ == "__main__":
    raise SystemExit(main())
