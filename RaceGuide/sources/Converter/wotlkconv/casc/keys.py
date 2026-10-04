"""Encryption keys for BLTE ``E`` chunks.

Blizzard encrypts unreleased content and the keys surface later, so the key
ring is data rather than code: users point ``--casc-keys`` at the community
``WoW.txt`` (or any file of ``<16 hex key name> <32 hex key>`` lines) and
previously unreadable files start decoding.

No keys are bundled. Without one, encrypted files are reported per file and
skipped rather than failing the run.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from .. import log

_LINE = re.compile(r"^\s*([0-9A-Fa-f]{16})\s*[;, \t]\s*([0-9A-Fa-f]{32})\s*(?:[;,#].*)?$")

#: Environment variable consulted when no --casc-keys is given.
ENV_VAR = "WOTLKCONV_CASC_KEYS"

#: Filenames probed next to the install and in the working directory.
DEFAULT_NAMES = ("WoW.txt", "wow.txt", "TactKeys.txt", "casc-keys.txt")


class KeyRing:
    """Maps a BLTE key name (a 64-bit integer) to its 16-byte key."""

    __slots__ = ("_keys", "sources")

    def __init__(self) -> None:
        self._keys: dict[int, bytes] = {}
        self.sources: list[str] = []

    def __len__(self) -> int:
        return len(self._keys)

    def __bool__(self) -> bool:
        return bool(self._keys)

    def get(self, key_name: int) -> bytes | None:
        return self._keys.get(key_name)

    def add(self, key_name: int, key: bytes) -> None:
        self._keys[key_name] = key

    def update(self, lines) -> int:
        added = 0
        for line in lines:
            m = _LINE.match(line)
            if not m:
                continue
            self._keys[int(m.group(1), 16)] = bytes.fromhex(m.group(2))
            added += 1
        return added

    @classmethod
    def load(cls, path: str | os.PathLike[str]) -> KeyRing:
        ring = cls()
        p = Path(path)
        with p.open("r", encoding="utf-8", errors="replace") as fh:
            added = ring.update(fh)
        ring.sources.append(str(p))
        log.info(f"loaded {added} CASC encryption key(s) from {p}")
        return ring

    @classmethod
    def discover(cls, explicit=None, search_dirs=()) -> KeyRing:
        """Load from an explicit path, then the environment, then probe."""
        if explicit:
            return cls.load(explicit)
        env = os.environ.get(ENV_VAR)
        if env and Path(env).is_file():
            return cls.load(env)
        for directory in (*search_dirs, Path.cwd()):
            for name in DEFAULT_NAMES:
                candidate = Path(directory) / name
                if candidate.is_file():
                    return cls.load(candidate)
        return cls()
