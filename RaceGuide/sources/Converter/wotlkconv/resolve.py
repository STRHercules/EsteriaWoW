"""Finding the sibling files a model needs.

Converting one M2 pulls in its skins, its skeleton, its external animations and
its textures.  Where those live on disk depends entirely on how the user
extracted them, and the three layouts in common use are:

* **by FileDataID** -- ``1234567.skel`` next to ``1234568.m2`` (CASCExplorer's
  "no listfile" dump, and what ``wow.export`` writes in ID mode)
* **by in-game path** -- ``character/human/male/humanmale.m2`` mirroring the
  archive tree
* **flat** -- everything in one directory, basenames only

:class:`AssetSource` tries all three so the caller never has to care, and can
fall back to an open CASC install when the companion was never extracted at
all -- which is the normal case when converting straight out of a game
install.
"""

from __future__ import annotations

import os
from collections import OrderedDict
from collections.abc import Sequence
from pathlib import Path

from . import log
from .listfile import Listfile, to_posix

#: Bytes of companion files remembered between lookups.  Skeletons and skins
#: are shared by many models converted near each other, so a small window pays
#: for itself; an unbounded one kept every companion of a whole build in each
#: worker, growing ~30 MB a minute apiece on a retail install.
CACHE_BYTES = 128 * 1024 * 1024
CACHE_ENTRIES = 8192


class AssetSource:
    """Locates companion assets for the file currently being converted."""

    def __init__(self, listfile: Listfile | None = None,
                 roots: Sequence[str | os.PathLike[str]] = (),
                 extensions: Sequence[str] = (), casc=None,
                 cache_bytes: int = CACHE_BYTES,
                 cache_entries: int = CACHE_ENTRIES):
        self.listfile = listfile or Listfile()
        self.roots: list[Path] = [Path(r) for r in roots]
        self.extensions = list(extensions) or [".m2", ".skel", ".skin", ".anim",
                                               ".blp", ".bone", ".wmo"]
        self.casc = casc
        self.cache_bytes = cache_bytes
        self.cache_entries = cache_entries
        self._cache: OrderedDict[str, bytes | None] = OrderedDict()
        self._cached_bytes = 0
        self._index: dict[str, Path] | None = None

    # -- cache ----------------------------------------------------------
    def _recall(self, key: str) -> tuple[bool, bytes | None]:
        if key not in self._cache:
            return False, None
        self._cache.move_to_end(key)
        return True, self._cache[key]

    def _remember(self, key: str, result: bytes | None) -> None:
        """Keep a lookup, least recently used first out once over budget."""
        previous = self._cache.pop(key, None)
        if previous:
            self._cached_bytes -= len(previous)
        self._cache[key] = result
        self._cached_bytes += len(result) if result else 0
        while self._cache and (self._cached_bytes > self.cache_bytes
                               or len(self._cache) > self.cache_entries):
            _old_key, old = self._cache.popitem(last=False)
            if old:
                self._cached_bytes -= len(old)

    # -- roots ----------------------------------------------------------
    def add_root(self, root: str | os.PathLike[str]) -> None:
        p = Path(root)
        if p.is_file():
            p = p.parent
        if p not in self.roots:
            self.roots.append(p)
            self._index = None

    def _basename_index(self) -> dict[str, Path]:
        """Lazily index every candidate file under the roots by lowercase name."""
        if self._index is not None:
            return self._index
        index: dict[str, Path] = {}
        exts = set(self.extensions)
        for root in self.roots:
            if not root.is_dir():
                continue
            for dirpath, _dirnames, filenames in os.walk(root):
                for fn in filenames:
                    if os.path.splitext(fn)[1].lower() in exts:
                        index.setdefault(fn.lower(), Path(dirpath) / fn)
        self._index = index
        log.debug(f"indexed {len(index)} companion files under "
                  f"{', '.join(str(r) for r in self.roots) or '(no roots)'}")
        return index

    # -- lookup ---------------------------------------------------------
    def _read(self, path: Path) -> bytes | None:
        try:
            return path.read_bytes()
        except OSError:
            return None

    def by_path(self, game_path: str) -> bytes | None:
        """Find a file given its in-game path (``\\`` or ``/`` separated)."""
        key = f"p:{game_path.lower()}"
        hit, cached = self._recall(key)
        if hit:
            return cached
        rel = to_posix(game_path)
        result: bytes | None = None
        for root in self.roots:
            candidate = root / rel
            if candidate.is_file():
                result = self._read(candidate)
                break
        if result is None:
            found = self._basename_index().get(os.path.basename(rel).lower())
            if found is not None:
                result = self._read(found)
        self._remember(key, result)
        return result

    def by_file_id(self, file_id: int, extension: str = "") -> bytes | None:
        """Find a file given its FileDataID, trying ID-named files first."""
        if not file_id:
            return None
        key = f"i:{file_id}:{extension}"
        hit, cached = self._recall(key)
        if hit:
            return cached

        result: bytes | None = None
        exts = [extension] if extension else self.extensions
        for root in self.roots:
            for ext in exts:
                candidate = root / f"{file_id}{ext}"
                if candidate.is_file():
                    result = self._read(candidate)
                    break
            if result is not None:
                break

        if result is None:
            path = self.listfile.path_for(file_id)
            if path:
                result = self.by_path(path)

        if result is None and self.casc is not None:
            # Files on disk win, so a user's edited copy overrides the install.
            data, why = self.casc.try_read_file_id(file_id)
            if data is None:
                log.debug(f"CASC lookup for {file_id} failed: {why}")
            result = data

        self._remember(key, result)
        return result

    def loader_for(self, extension: str):
        """Return a ``(file_id) -> bytes | None`` closure, for chain walkers."""
        return lambda fid: self.by_file_id(fid, extension)


