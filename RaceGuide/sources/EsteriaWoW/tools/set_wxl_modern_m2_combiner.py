"""Toggle WarcraftXL modern-M2 combiner for the Esteria client.

The WoD player models are already native WotLK M2 v264 assets.  WarcraftXL's
modern-M2 extension installs an additional batch/texture combiner by default,
which is unnecessary for those models and can alter their layered character
texture path.  This helper writes the extension's supported config key while
keeping every other WarcraftXL feature enabled.
"""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

DEFAULT_CLIENT = Path(r"G:\3.3.5a - Dev")
CFG_REL = Path("Extensions") / "wxl-modern-m2" / "wxl-modern-m2.cfg"
KEY = "WXL_M2_COMBINER_PATCH_ENABLED"


def render(existing: str, enabled: bool) -> str:
    value = "1" if enabled else "0"
    lines = existing.splitlines()
    out: list[str] = []
    replaced = False
    for line in lines:
        if line.strip().upper().startswith(KEY + "="):
            out.append(f"{KEY}={value}")
            replaced = True
        else:
            out.append(line)
    if not replaced:
        if out and out[-1].strip():
            out.append("")
        out.append(f"{KEY}={value}")
    return "\r\n".join(out) + "\r\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-root", type=Path, default=DEFAULT_CLIENT)
    parser.add_argument("--enable", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    cfg = args.client_root / CFG_REL
    existing = cfg.read_text(encoding="utf-8", errors="replace") if cfg.exists() else ""
    desired = render(existing, args.enable)

    print(f"cfg={cfg}")
    print(f"exists={cfg.exists()}")
    print(f"desired={KEY}={'1' if args.enable else '0'}")
    if not args.apply:
        print("would_write=true")
        return 0

    cfg.parent.mkdir(parents=True, exist_ok=True)
    if cfg.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = cfg.with_name(cfg.name + f".bak-{stamp}")
        shutil.copy2(cfg, backup)
        print(f"backup={backup}")
    cfg.write_text(desired, encoding="utf-8", newline="")
    verify = cfg.read_text(encoding="utf-8", errors="strict")
    if f"{KEY}={'1' if args.enable else '0'}" not in verify:
        raise RuntimeError("config verification failed")
    print("written=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
