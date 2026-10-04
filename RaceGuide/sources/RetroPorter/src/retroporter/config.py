from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Config:
    retail_root: Path = Path(os.environ.get("RETROPORTER_RETAIL_ROOT", r"G:\Blizzard\World of Warcraft"))
    wrath_root: Path = Path(os.environ.get("RETROPORTER_WRATH_ROOT", r"G:\3.3.5a - Dev"))
    work_root: Path = Path(os.environ.get("RETROPORTER_WORK_ROOT", r"G:\RetroPorterWork"))
    product: str = os.environ.get("RETROPORTER_PRODUCT", "wow")
    listfile: Path = Path(os.environ.get("RETROPORTER_LISTFILE", str(Path.home() / ".cache" / "wotlkconv" / "community-listfile.csv")))
    dbd_dir: Path = Path(os.environ.get("RETROPORTER_DBD", str(Path.home() / ".cache" / "wotlkconv" / "definitions")))
    keys: Path = Path(os.environ.get("RETROPORTER_KEYS", str(Path.home() / ".cache" / "wotlkconv" / "WoW.txt")))


DEFAULT = Config()
