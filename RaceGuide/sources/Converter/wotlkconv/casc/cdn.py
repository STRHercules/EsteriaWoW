"""Files a partial install does not store, fetched from Blizzard's CDN.

A retail install streams some of its build on demand -- on 12.1.0.69814, 4,550
files (9.6 GB) including world map textures, voice-over and a few models.
Everything needed to find them is already on disk:

* ``.build.info`` names the CDN hosts and path;
* the CDN config (``Data/config/..``) lists the build's archives;
* ``Data/indices`` holds every archive's ``.index``, the *archive-group* index
  that merges them (encoding key -> archive, offset, size), and the index of
  loose files kept outside any archive.

So a missing file is located locally, and only its own bytes are fetched: an
HTTP range request into the archive that holds it, or the loose file whole.

Nothing is trusted on arrival.  An encoding key is the MD5 of the BLTE header
it names (checked on every one of 99 locally stored files), so a download that
does not hash to its key is rejected; the storage additionally checks that the
decoded content hashes to its content key.  Verified downloads are cached by
encoding key, so parallel workers and later runs never fetch a file twice.
"""

from __future__ import annotations

import bisect
import hashlib
import mmap
import os
import struct
import urllib.request
from collections.abc import Callable
from pathlib import Path

from .. import log
from ..errors import MalformedFileError, MissingDependencyError
from .config import BuildInfo, config_path, parse_config

#: Bytes of the footer every CDN ``.index`` ends with.
FOOTER_SIZE = 28

#: How long one request may stall before the next host is tried.
TIMEOUT_SECONDS = 60

#: ``fetch(url, offset, size) -> bytes``; ``offset`` is None for a whole file.
Fetcher = Callable[[str, "int | None", int], bytes]


class CdnError(MissingDependencyError):
    """A file could not be fetched from, or verified against, the CDN."""


def blte_header_md5(encoded: bytes) -> bytes:
    """The encoding key a BLTE stream should have: MD5 of its header.

    A stream with no chunk table (header size 0) is hashed whole.
    """
    if len(encoded) < 8 or encoded[:4] != b"BLTE":
        return b""
    header_size = struct.unpack_from(">I", encoded, 4)[0]
    return hashlib.md5(encoded[:header_size] if header_size else encoded).digest()


class CdnIndex:
    """One CDN ``.index``, searched in place rather than loaded.

    Entries are sorted by key into fixed-size blocks, and a table of each
    block's last key follows them, so a lookup is a bisect plus a scan of one
    block.  The archive-group index of a retail build has 4.7 million entries;
    mapping the file lets every worker share the operating system's pages.
    """

    def __init__(self, path: Path):
        self.path = path
        size = path.stat().st_size
        if size < FOOTER_SIZE:
            raise MalformedFileError(f"{path.name}: only {size} bytes")
        with path.open("rb") as handle:
            self._map = mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ)
        footer = self._map[size - FOOTER_SIZE:]
        (version, _unk1, _unk2, block_kb, self.offset_bytes, self.size_bytes,
         self.key_bytes, checksum) = footer[8:16]
        self.count = int.from_bytes(footer[16:20], "little")
        if version != 1 or not block_kb or not self.key_bytes:
            raise MalformedFileError(
                f"{path.name}: unrecognised index footer (version {version}, "
                f"block {block_kb} KiB, key {self.key_bytes} bytes)")
        self.block = block_kb * 1024
        self.entry = self.key_bytes + self.size_bytes + self.offset_bytes
        body = size - FOOTER_SIZE
        per_block = self.block + self.key_bytes + checksum
        self.blocks = body // per_block
        if self.blocks * per_block != body:
            raise MalformedFileError(
                f"{path.name}: {body} bytes of blocks and table of contents do "
                f"not divide into {per_block}-byte blocks")
        toc = self.blocks * self.block
        k = self.key_bytes
        self._last_keys = [bytes(self._map[toc + i * k: toc + (i + 1) * k])
                           for i in range(self.blocks)]

    def find(self, ekey: bytes) -> tuple[int, int, int] | None:
        """``(size, archive number, offset)``, or None.

        The archive number is -1 for a loose-file index, whose entries have no
        offset; it is 0 for a single archive's own index.
        """
        key = ekey[:self.key_bytes]
        block = bisect.bisect_left(self._last_keys, key)
        if block >= self.blocks:
            return None
        start = block * self.block
        k, s = self.key_bytes, self.size_bytes
        for i in range(self.block // self.entry):
            at = start + i * self.entry
            here = self._map[at:at + k]
            if here == key:
                size = int.from_bytes(self._map[at + k:at + k + s], "big")
                rest = self._map[at + k + s:at + self.entry]
                if self.offset_bytes == 0:
                    return size, -1, 0
                if self.offset_bytes == 6:
                    return (size, int.from_bytes(rest[:2], "big"),
                            int.from_bytes(rest[2:], "big"))
                return size, 0, int.from_bytes(rest, "big")
        return None

    def close(self) -> None:
        self._map.close()


def http_fetch(url: str, offset: int | None, size: int) -> bytes:
    """GET ``url``, or just ``size`` bytes of it from ``offset``."""
    headers = {}
    if offset is not None:
        headers["Range"] = f"bytes={offset}-{offset + size - 1}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        if offset is not None and response.status != 206:
            # A server that ignores the range would send the whole archive.
            raise CdnError(f"{url}: asked for a byte range, got HTTP "
                           f"{response.status}")
        return response.read()


class CdnSource:
    """Locates and fetches the files of one build that are not stored locally."""

    def __init__(self, install_dir: str | os.PathLike[str], build: BuildInfo,
                 cache_dir: str | os.PathLike[str],
                 fetch: Fetcher | None = None):
        data_dir = Path(install_dir) / "Data"
        if not build.cdn_hosts or not build.cdn_path:
            raise MissingDependencyError(
                f".build.info names no CDN hosts for {build.product}, so files "
                f"it does not store cannot be fetched")
        cfg_path = config_path(data_dir, build.cdn_key)
        if not cfg_path.is_file():
            raise MissingDependencyError(
                f"CDN config {build.cdn_key} is missing from {cfg_path}")
        cfg = parse_config(cfg_path.read_text(encoding="utf-8", errors="replace"))
        self.hosts = list(build.cdn_hosts)
        self.path = build.cdn_path.strip("/")
        self.archives: list[str] = cfg.get("archives", [])
        self.cache_dir = Path(cache_dir)
        self.fetch = fetch or http_fetch
        self._indices = data_dir / "indices"
        self._group = self._open(cfg.get("archive-group", [""])[0])
        self._loose = self._open(cfg.get("file-index", [""])[0])
        self._per_archive: dict[int, CdnIndex] = {}
        self.fetched = 0
        if self._group is None:
            log.debug("no archive-group index; searching each archive's index")

    def _open(self, key: str) -> CdnIndex | None:
        path = self._indices / f"{key}.index" if key else None
        return CdnIndex(path) if path and path.is_file() else None

    # -- locating ---------------------------------------------------------
    def locate(self, ekey: bytes) -> tuple[str, int | None, int] | None:
        """``(path under the CDN root, offset or None, size)`` of a file."""
        hit = self._group.find(ekey) if self._group else self._search_archives(ekey)
        if hit is not None:
            size, archive, offset = hit
            if not 0 <= archive < len(self.archives):
                raise MalformedFileError(
                    f"archive-group entry for {ekey.hex()} names archive "
                    f"{archive} of {len(self.archives)}")
            name = self.archives[archive]
            return f"data/{name[:2]}/{name[2:4]}/{name}", offset, size
        if self._loose is not None:
            loose = self._loose.find(ekey)
            if loose is not None:
                key = ekey.hex()
                return f"data/{key[:2]}/{key[2:4]}/{key}", None, loose[0]
        return None

    def _search_archives(self, ekey: bytes) -> tuple[int, int, int] | None:
        for number, name in enumerate(self.archives):
            index = self._per_archive.get(number)
            if index is None:
                index = self._open(name)
                if index is None:
                    continue
                self._per_archive[number] = index
            hit = index.find(ekey)
            if hit is not None:
                return hit[0], number, hit[2]
        return None

    # -- reading ----------------------------------------------------------
    def _cache_path(self, ekey: bytes) -> Path:
        key = ekey.hex()
        return self.cache_dir / key[:2] / key

    def read(self, ekey: bytes, what: str = "file") -> bytes:
        """The BLTE-encoded bytes of ``ekey``, verified, from cache or CDN."""
        cached = self._cache_path(ekey)
        if cached.is_file():
            data = cached.read_bytes()
            if blte_header_md5(data) == ekey:
                return data
            log.warn(f"cached CDN file {cached.name} does not match its key; "
                     f"fetching it again")

        where = self.locate(ekey)
        if where is None:
            raise CdnError(
                f"{what} ({ekey.hex()[:18]}) is not stored locally and is in "
                f"none of this build's CDN archive or loose-file indices")
        rel, offset, size = where
        problems = []
        for host in self.hosts:
            url = f"http://{host}/{self.path}/{rel}"
            try:
                data = self.fetch(url, offset, size)
            except (OSError, CdnError) as exc:
                problems.append(f"{host}: {exc}")
                continue
            if len(data) != size:
                problems.append(f"{host}: {len(data)} bytes, expected {size}")
                continue
            if blte_header_md5(data) != ekey:
                problems.append(f"{host}: content does not hash to its key")
                continue
            cached.parent.mkdir(parents=True, exist_ok=True)
            partial = cached.with_name(f"{cached.name}.{os.getpid()}.part")
            partial.write_bytes(data)
            os.replace(partial, cached)
            self.fetched += 1
            return data
        raise CdnError(f"{what} ({ekey.hex()[:18]}) could not be fetched: "
                       + "; ".join(problems))

    def close(self) -> None:
        for index in (self._group, self._loose, *self._per_archive.values()):
            if index is not None:
                index.close()
