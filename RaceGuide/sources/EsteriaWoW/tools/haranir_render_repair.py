"""Install checked Haranir rendering repairs with verified rollback copies and explicit live receipts."""

import argparse
import json
import os
import shutil
import subprocess
import struct
from datetime import datetime
from pathlib import Path

import haranir_race_pack as h

STAGE = Path("C:/Users/Zach/.codex/tmp/haranir-render")


def validate():
    from wow_xref import Pe
    client = Pe(h.p.CLIENT_DEFAULT / "Wow.exe")
    if client.read_va(0x0076E597, 3) != bytes.fromhex("c21000"):
        raise ValueError("Client allocator ABI differs from the audited stdcall implementation")
    for name in ("TestNativeAppearance.exe", "TestHighmountainMaterials.exe"):
        subprocess.run([str(STAGE / name), str(STAGE / "EsteriaAppearance.dll")], check=True)
    root = STAGE / "Interface/AddOns/EsteriaAppearanceCache/Haranir"
    files = list(root.glob("*.blp"))
    if not files:
        raise ValueError("Native compositor did not produce its material fixtures")
    for file in files:
        data = file.read_bytes()
        parsed = h.p.Blp.parse(data)
        if struct.unpack_from("<I", data, 20)[0] != 1172 or not data[11]:
            raise ValueError("Nonstandard BLP header/mip chain: " + file.name)
        bitmap = parsed.decode_level(0)
        if len(bitmap.data) != parsed.width * parsed.height * 4:
            raise ValueError("Incomplete native BLP pixels")
    return {"harnesses": "PASS", "native_blps": len(files),
            "decoder": "validated buffers, native allocator and reference lifecycle"}


def install():
    validate()
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("Close WoW/Eclipse before replacing their loaded helper")
    receipt = h.p.load_json(h.STAGE / "last-install.json")
    name = "EsteriaAppearance.dll"
    live, source = h.p.CLIENT_DEFAULT / name, STAGE / name
    before = h.p.sha256(live)
    if before != receipt["installed_hashes"][name]:
        raise ValueError("Live helper differs from its installation receipt")
    preserved = {str(relative): h.p.sha256(h.p.CLIENT_DEFAULT / relative) for relative in
        (h.p.GLOBAL_ARCHIVE_REL, h.p.LOCALE_ARCHIVE_REL, h.p.ASSET_ARCHIVE_REL, Path("Wow.exe"))}
    preserved.update({file.name: h.p.sha256(file) for file in h.p.CLIENT_DEFAULT.glob("Esteria*.bin")})
    backup = Path("C:/Users/Zach/.codex/backups") / ("haranir-render-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup.mkdir(parents=True)
    shutil.copy2(live, backup / name)
    if h.p.sha256(backup / name) != before:
        raise ValueError("Helper rollback copy differs")
    temporary = live.with_suffix(".dll.haranir-render-next")
    shutil.copy2(source, temporary)
    if h.p.sha256(temporary) != h.p.sha256(source):
        raise ValueError("Helper install copy differs")
    os.replace(temporary, live)
    after = h.p.sha256(live)
    if any(h.p.sha256(h.p.CLIENT_DEFAULT / key) != digest for key, digest in preserved.items()):
        raise ValueError("Unrelated client files changed")
    import expanded_appearance_pack as native
    for directory in (h.STAGE, h.e.STAGE, h.e.h.STAGE, native.STAGE):
        file = directory / "last-install.json"
        if file.exists():
            data = h.p.load_json(file)
            data["installed_hashes"][name] = after
            data["latest_haranir_render_backup"] = str(backup)
            h.save(file, data)
    shutil.copy2(source, h.STAGE / name)
    report = {"backup": str(backup), "before_sha256": before, "installed_sha256": after,
        "preserved_hashes": preserved, "status": "installed_awaiting_live_texture_readback"}
    h.save(STAGE / "last-install.json", report)
    h.save(backup / "install-report.json", report)
    acceptance = h.p.load_json(h.ROOT / "integration/acceptance.json")
    acceptance.update(status=report["status"], live_acceptance="failed_initial_rendering",
        latest_render_repair=report)
    acceptance["installed_hashes"][name] = after
    h.save(h.ROOT / "integration/acceptance.json", acceptance)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("validate", "install"))
    print(json.dumps({"validate": validate, "install": install}[parser.parse_args().action](), indent=2))
