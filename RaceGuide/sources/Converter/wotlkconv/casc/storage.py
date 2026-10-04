"""Reading files straight out of a local CASC install.

Putting the pieces together, resolving one FileDataID means::

    root      FileDataID -> content key
    encoding  content key -> encoding key
    index     encoding key -> (archive number, offset, size)
    data.NNN  bytes at that offset, behind a 30-byte entry header
    BLTE      decode the stream

Only *local* storage is read, and that is a real boundary rather than a
limitation to work around.  A modern install is a catalogue with a cache
behind it: the root table lists every file the build has, while the archives
on disk hold only what this machine has actually downloaded.  The rest is
streamed from Blizzard's CDN as the game asks for it.

Fetching those would mean pulling content the user has not installed, from
Blizzard's servers, on their connection -- so this tool does not.  A file that
is listed but not stored is reported as not installed, with the difference
spelled out, and :meth:`CascStorage.coverage` says up front how much of the
build is actually readable here, so the gap is known before a conversion run
rather than discovered as a pile of failures afterwards.
"""

from __future__ import annotations

import dataclasses
import hashlib
import os
import struct
from pathlib import Path

from .. import log
from ..errors import MalformedFileError, MissingDependencyError
from . import blte
from .cdn import CdnSource, Fetcher
from .config import BuildInfo
from .encoding import EncodingTable
from .index import ARCHIVE_ENTRY_HEADER, LocalIndex
from .keys import KeyRing
from .root import LOCALE_NAMES, RootTable


class FileNotInstalledError(MissingDependencyError):
    """The file exists in the build but its data is not on this machine."""


@dataclasses.dataclass(slots=True)
class Coverage:
    """How much of the build this machine actually holds.

    ``listed`` counts what the root table names; ``local`` counts what can be
    read without touching the network.  The two differ on any install that has
    not downloaded everything, which is most of them.
    """

    listed: int
    local: int
    #: Named by root, but the encoding table has no key for it.
    no_encoding: int
    #: Keyed, but no local archive holds it: the CDN would have to be asked.
    not_downloaded: int
    #: Set when only part of the build was measured.
    sampled: int = 0

    @property
    def measured(self) -> int:
        return self.sampled or self.listed

    @property
    def fraction(self) -> float:
        return self.local / self.measured if self.measured else 0.0

    def describe(self) -> str:
        where = (f"{self.local} of {self.measured} files"
                 + (f" sampled from {self.listed}" if self.sampled else ""))
        return (f"{where} ({self.fraction * 100:.1f}%) are stored on this "
                f"machine; {self.not_downloaded} would have to come from the "
                f"CDN and {self.no_encoding} have no encoding entry")


@dataclasses.dataclass(slots=True)
class StorageStats:
    product: str
    version: str
    build: str
    locale: str
    files: int
    index_buckets: int
    encoding_entries: int
    keys: int


class CascStorage:
    """Read-only view of a local CASC install."""

    def __init__(self, install_dir: Path, build: BuildInfo, index: LocalIndex,
                 encoding: EncodingTable, root: RootTable, keys: KeyRing,
                 locale_name: str):
        self.install_dir = install_dir
        self.build = build
        self.index = index
        self.encoding = encoding
        self.root = root
        self.keys = keys
        self.locale_name = locale_name
        self._handles: dict[int, object] = {}
        self._data_dir = install_dir / "Data" / "data"
        #: Set to fetch what the install does not store; see :mod:`.cdn`.
        self.cdn: CdnSource | None = None

    # -- construction ---------------------------------------------------
    @classmethod
    def open(cls, install_dir: str | Path, *, product: str | None = None,
             locale: str = "enus", keys: KeyRing | None = None,
             cdn_cache: str | os.PathLike[str] | None = None,
             cdn_fetch: Fetcher | None = None) -> CascStorage:
        """Open an install.  With ``cdn_cache``, files it does not store are
        fetched from Blizzard's CDN, verified, and kept in that directory."""
        install_dir = Path(install_dir)
        keys = keys or KeyRing()
        build = BuildInfo.load(install_dir, product)
        log.info(f"opening CASC install: {build.describe()}")

        data_dir = install_dir / "Data" / "data"
        if not data_dir.is_dir():
            raise MissingDependencyError(
                f"{data_dir} does not exist; --casc wants the folder that "
                f"contains Data/, not Data/ itself")
        index = LocalIndex(data_dir)
        if not index.bucket_count:
            raise MissingDependencyError(
                f"no .idx index files in {data_dir}; the install may be "
                f"mid-update")

        storage = cls(install_dir, build, index, EncodingTable(), RootTable(),
                      keys, locale)
        if cdn_cache is not None:
            storage.cdn = CdnSource(install_dir, build, cdn_cache, cdn_fetch)

        raw = storage._read_by_ekey(bytes.fromhex(build.encoding_ekey), "encoding")
        storage.encoding = EncodingTable.parse(raw, "encoding")
        log.debug(f"encoding table: {len(storage.encoding)} content keys")

        locale_bits = LOCALE_NAMES.get(locale.lower().replace("_", ""))
        if locale_bits is None:
            raise MissingDependencyError(
                f"unknown locale {locale!r}; try one of "
                f"{', '.join(sorted(LOCALE_NAMES))}")
        root_raw = storage.read_by_ckey(bytes.fromhex(build.root_ckey), "root")
        storage.root = RootTable.parse(root_raw, locale_bits, "root")
        log.info(f"CASC ready: {len(storage.root)} files, locale {locale}")
        return storage

    # -- low level ------------------------------------------------------
    def _archive(self, number: int):
        handle = self._handles.get(number)
        if handle is None:
            path = self._data_dir / f"data.{number:03d}"
            if not path.is_file():
                raise FileNotInstalledError(
                    f"archive {path.name} is missing from the install")
            handle = path.open("rb")
            self._handles[number] = handle
        return handle

    def _read_by_ekey(self, ekey: bytes, what: str = "file",
                      zero_encrypted: bool = False) -> bytes:
        entry = self.index.find(ekey)
        if entry is None:
            if self.cdn is not None:
                return blte.decode(self.cdn.read(ekey, what), self.keys,
                                   zero_encrypted)
            raise FileNotInstalledError(
                f"{what} {ekey.hex()[:18]} is not in the local index; this "
                f"install streams it from the CDN rather than storing it "
                f"on disk (--casc-cdn fetches it)")
        handle = self._archive(entry.archive)
        handle.seek(entry.offset)
        raw = handle.read(entry.size)
        if len(raw) < ARCHIVE_ENTRY_HEADER:
            raise MalformedFileError(
                f"{what}: archive entry is only {len(raw)} bytes")
        declared = struct.unpack_from("<I", raw, 16)[0]
        if declared and declared <= len(raw):
            raw = raw[:declared]
        return blte.decode(raw[ARCHIVE_ENTRY_HEADER:], self.keys,
                           zero_encrypted)

    def read_by_ckey(self, ckey: bytes, what: str = "file",
                     zero_encrypted: bool = False) -> bytes:
        ekey = self.encoding.ekey_for(ckey)
        if ekey is None:
            raise FileNotInstalledError(
                f"{what} {ckey.hex()[:16]} has no entry in the encoding table")
        from_cdn = self.cdn is not None and self.index.find(ekey) is None
        data = self._read_by_ekey(ekey, what, zero_encrypted)
        # A fetched file has already matched its encoding key; the content has
        # to match its content key too.  Not checkable when encrypted parts
        # were zeroed, which is the point of zeroing them.
        if from_cdn and not zero_encrypted and hashlib.md5(data).digest() != ckey:
            raise MalformedFileError(
                f"{what}: the file fetched from the CDN decodes to content "
                f"that does not match its content key {ckey.hex()[:16]}")
        return data

    # -- public ---------------------------------------------------------
    def __contains__(self, file_id: int) -> bool:
        return file_id in self.root

    def file_ids(self):
        return self.root.file_ids()

    def read_file_id(self, file_id: int, zero_encrypted: bool = False) -> bytes:
        """Read one file. Raises on missing, not-installed or encrypted.

        ``zero_encrypted`` reads a file whose encrypted parts cannot be
        decrypted anyway, with those parts zeroed -- for client databases,
        whose unreleased rows sit in sections of their own that the reader
        skips.  Anything else with a hole in it is simply corrupt.
        """
        ckey = self.root.ckey_for(file_id)
        if ckey is None:
            raise MissingDependencyError(
                f"FileDataID {file_id} is not in this build's root table")
        return self.read_by_ckey(ckey, f"FileDataID {file_id}", zero_encrypted)

    def try_read_file_id(self, file_id: int, zero_encrypted: bool = False
                         ) -> tuple[bytes | None, str]:
        """Read a file, returning ``(data, "")`` or ``(None, reason)``."""
        try:
            return self.read_file_id(file_id, zero_encrypted), ""
        except blte.EncryptedChunkError as exc:
            return None, str(exc)
        except (MissingDependencyError, MalformedFileError) as exc:
            return None, str(exc)

    def coverage(self, sample: int = 0) -> Coverage:
        """Count how many of the build's files are readable without the CDN.

        Nothing is decoded -- this walks the same three lookups a read does
        and stops at the index, so it costs dictionary lookups rather than I/O.
        ``sample`` measures an evenly spread subset of a large install instead
        of all of it.
        """
        ids = sorted(self.root.file_ids())
        step = max(1, len(ids) // sample) if sample and sample < len(ids) else 1
        chosen = ids[::step] if step > 1 else ids

        local = no_encoding = not_downloaded = 0
        for file_id in chosen:
            ckey = self.root.ckey_for(file_id)
            ekey = self.encoding.ekey_for(ckey) if ckey else None
            if ekey is None:
                no_encoding += 1
            elif self.index.find(ekey) is None:
                not_downloaded += 1
            else:
                local += 1
        return Coverage(listed=len(ids), local=local, no_encoding=no_encoding,
                        not_downloaded=not_downloaded,
                        sampled=len(chosen) if step > 1 else 0)

    def stats(self) -> StorageStats:
        return StorageStats(
            product=self.build.product or "wow",
            version=self.build.version,
            build=self.build.build_name or self.build.build_key[:8],
            locale=self.locale_name,
            files=len(self.root),
            index_buckets=self.index.bucket_count,
            encoding_entries=len(self.encoding),
            keys=len(self.keys),
        )

    def close(self) -> None:
        for handle in self._handles.values():
            handle.close()  # type: ignore[attr-defined]
        self._handles.clear()
        if self.cdn is not None:
            self.cdn.close()

    def __enter__(self) -> CascStorage:
        return self

    def __exit__(self, *_exc) -> None:
        self.close()
