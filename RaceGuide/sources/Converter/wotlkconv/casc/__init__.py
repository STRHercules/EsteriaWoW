"""Reading a local CASC install (Warlords of Draenor and later).

CASC replaced MPQ as World of Warcraft's storage format, and everything the
converter wants lives inside it.  This package implements enough of it to pull
files out by FileDataID: BLTE decoding, the local ``.idx`` indices, the
encoding table and the root table.

Only local installs are read; nothing is fetched from Blizzard's CDN, and
``CascStorage.coverage`` reports how much of the build that leaves readable.
"""

from .blte import EncryptedChunkError
from .blte import decode as blte_decode
from .keys import KeyRing
from .storage import CascStorage, Coverage, FileNotInstalledError, StorageStats

__all__ = [
                      "CascStorage",
                      "Coverage",
                      "EncryptedChunkError",
                      "FileNotInstalledError",
                      "KeyRing",
                      "StorageStats",
                      "blte_decode",
]
