"""Create a side-by-side WoD runtime isolation client.

The diagnostic client uses the known-working donor Wow.exe/runtime DLLs and the
current Esteria data/model/DBC payload, but deliberately replaces the isolation
copy's active GlueXML with the donor's known-working GlueXML.  This avoids the
stock/donor executable rejecting Esteria's custom login UI while still testing
the exact WoD race assets and DBCs currently installed in Esteria.

The live client is never modified.  Most Data files are hard-linked read-only
into the isolation tree; Data/enUS/patch-enUS-Z.MPQ is a private copy because it
receives the donor GlueXML overlay.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOL_DIR))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from mount_pack_batch2 import client_archive_chain  # noqa: E402

DONOR = Path(r"F:\Wrath of the Lich King 3.3.5a (wod models)")
CLIENT = Path(r"G:\3.3.5a - Dev")
DEFAULT_OUTPUT = CLIENT / "_WOD_RUNTIME_ISOLATION"
LOCALE = "enUS"
LOCALE_Z = f"patch-{LOCALE}-Z.MPQ"

RUNTIME_FILES = (
    "Wow.exe",
    "WowError.exe",
    "Battle.net.dll",
    "dbghelp.dll",
    "DivxDecoder.dll",
    "ijl15.dll",
    "msvcr80.dll",
    "Scan.dll",
    "unicows.dll",
)


def remove_tree_or_junction(path: Path) -> None:
    """Remove a local directory or junction without following a junction target."""

    if not path.exists() and not path.is_symlink():
        return
    # Windows directory junctions report as directories. cmd/rmdir removes the
    # reparse point itself rather than recursing into its target.
    result = subprocess.run(
        ["cmd.exe", "/c", "fsutil", "reparsepoint", "query", str(path)],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        subprocess.run(["cmd.exe", "/c", "rmdir", str(path)], check=True)
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def make_junction(link: Path, target: Path) -> None:
    remove_tree_or_junction(link)
    result = subprocess.run(
        ["cmd.exe", "/c", "mklink", "/J", str(link), str(target)],
        check=True,
        capture_output=True,
        text=True,
    )
    print(result.stdout.strip())


def hardlink_or_copy(source: Path, target: Path) -> str:
    """Hard-link a same-volume file, falling back to a normal copy."""

    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        target.unlink()
    try:
        os.link(source, target)
        return "hardlink"
    except OSError:
        shutil.copy2(source, target)
        return "copy"


def build_isolated_data(out: Path) -> Path:
    """Mirror Esteria Data without sharing the locale Z archive by inode."""

    source_data = CLIENT / "Data"
    target_data = out / "Data"
    remove_tree_or_junction(target_data)
    target_data.mkdir(parents=True)

    linked = 0
    copied = 0
    junctions = 0

    for child in source_data.iterdir():
        target = target_data / child.name
        if child.is_dir() and child.name.casefold() != LOCALE.casefold():
            make_junction(target, child)
            junctions += 1
            continue
        if child.is_file():
            mode = hardlink_or_copy(child, target)
            linked += mode == "hardlink"
            copied += mode == "copy"

    source_locale = source_data / LOCALE
    target_locale = target_data / LOCALE
    target_locale.mkdir(parents=True, exist_ok=True)
    for child in source_locale.iterdir():
        target = target_locale / child.name
        if child.is_dir():
            make_junction(target, child)
            junctions += 1
            continue
        if child.name.casefold() == LOCALE_Z.casefold():
            shutil.copy2(child, target)
            copied += 1
        else:
            mode = hardlink_or_copy(child, target)
            linked += mode == "hardlink"
            copied += mode == "copy"

    private_locale_z = target_locale / LOCALE_Z
    if not private_locale_z.is_file():
        raise RuntimeError(f"Private isolation locale archive was not created: {private_locale_z}")

    print(f"isolated Data: {linked} hard-linked files, {copied} copied files, {junctions} directory junctions")
    print(f"private writable archive: {private_locale_z}")
    return private_locale_z


def collect_donor_glue(storm: Storm) -> dict[str, bytes]:
    """Resolve the donor's effective GlueXML namespace highest-priority first."""

    winners: dict[str, tuple[str, Path]] = {}
    for archive_path in client_archive_chain(DONOR / "Data", LOCALE):
        handle = storm.open_archive(archive_path)
        try:
            for name, *_ in storm.list_files(handle):
                folded = name.casefold()
                if not folded.startswith("interface\\gluexml\\"):
                    continue
                if folded not in winners:
                    winners[folded] = (name, archive_path)
        finally:
            storm.dll.SFileCloseArchive(handle)

    if not winners:
        raise RuntimeError("No donor GlueXML files were discovered")

    by_archive: dict[Path, list[tuple[str, str]]] = {}
    for folded, (name, archive_path) in winners.items():
        by_archive.setdefault(archive_path, []).append((folded, name))

    payloads: dict[str, bytes] = {}
    for archive_path, entries in by_archive.items():
        handle = storm.open_archive(archive_path)
        try:
            for _, name in entries:
                payloads[name] = storm.read(handle, name)
        finally:
            storm.dll.SFileCloseArchive(handle)

    required = r"Interface\GlueXML\GlueXML.toc".casefold()
    if required not in {name.casefold() for name in payloads}:
        raise RuntimeError("Donor effective GlueXML is missing GlueXML.toc")
    return payloads


def overlay_donor_glue(private_locale_z: Path) -> int:
    """Replace the isolation archive's active GlueXML with donor-known-good files."""

    storm = Storm(DLL_DEFAULT)
    payloads = collect_donor_glue(storm)
    storm.replace_archive_entries(private_locale_z, payloads)

    verify = storm.open_archive(private_locale_z)
    try:
        for name, expected in payloads.items():
            actual = storm.read(verify, name)
            if actual != expected:
                raise RuntimeError(f"GlueXML verification failed for {name}")
    finally:
        storm.dll.SFileCloseArchive(verify)

    print(f"overlaid {len(payloads)} donor-effective GlueXML files into isolation enUS-Z")
    return len(payloads)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    out = args.output.resolve()

    if not DONOR.is_dir():
        raise SystemExit(f"Donor client is missing: {DONOR}")
    if not (CLIENT / "Data").is_dir():
        raise SystemExit(f"Esteria Data directory is missing: {CLIENT / 'Data'}")
    if not DLL_DEFAULT.is_file():
        raise SystemExit(f"StormLib is missing: {DLL_DEFAULT}")

    out.mkdir(parents=True, exist_ok=True)

    for name in RUNTIME_FILES:
        source = DONOR / name
        if not source.is_file():
            raise SystemExit(f"Required donor runtime file is missing: {source}")
        shutil.copy2(source, out / name)
        print(f"copied {name}")

    # Fresh local runtime state. No root-level WarcraftXL, proxy renderer,
    # Extensions, or addon directory is copied into the isolation client.
    for name in ("Cache", "Interface", "Logs"):
        path = out / name
        remove_tree_or_junction(path)
        path.mkdir()

    source_wtf = CLIENT / "WTF"
    target_wtf = out / "WTF"
    remove_tree_or_junction(target_wtf)
    if source_wtf.is_dir():
        shutil.copytree(source_wtf, target_wtf)
    else:
        target_wtf.mkdir()

    private_locale_z = build_isolated_data(out)
    glue_count = overlay_donor_glue(private_locale_z)

    # Explicitly prove the files that must *not* exist in the isolated root.
    forbidden = (
        "WarcraftXL.dll",
        "Client.dll",
        "d3d9.dll",
        "version.dll",
        "CoAVolFog.dll",
        "Extensions",
    )
    leaked = [name for name in forbidden if (out / name).exists()]
    if leaked:
        raise SystemExit(f"Isolation root unexpectedly contains: {leaked}")

    print()
    print(f"Isolation client ready: {out}")
    print(f"Launch: {out / 'Wow.exe'}")
    print(f"Esteria Data payload mirrored from: {CLIENT / 'Data'}")
    print(f"Donor GlueXML overlay files: {glue_count}")
    print("WarcraftXL/proxy runtime: absent")
    print("Live Esteria client: untouched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
