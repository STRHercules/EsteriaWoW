"""FileDataID -> path resolution.

Legion (M2 v272) moved every asset cross-reference from an inline filename to a
numeric FileDataID.  A 3.3.5a client has no FileDataID table at all -- it opens
paths out of MPQ archives -- so every reference has to be turned back into a
string before the asset can be written.  That mapping only exists in the
community listfile, which the user supplies.

Accepted input formats (auto-detected per line):

* ``1234567;world/foo/bar.m2``   -- wowdev community listfile (CSV, semicolon)
* ``1234567,world/foo/bar.m2``   -- comma-separated variant
* ``1234567 world/foo/bar.m2``   -- whitespace-separated variant

Lines that do not start with digits are ignored, so a header row is harmless.
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterable, Iterator
from pathlib import Path

from . import log
from .errors import MissingDependencyError

_LINE = re.compile(r"^\s*(\d+)\s*[;,\t ]\s*(.+?)\s*$")

#: Environment variable consulted when no --listfile is passed.
ENV_VAR = "WOTLKCONV_LISTFILE"

#: Locations probed for a listfile when neither flag nor env var is set.
DEFAULT_NAMES = ("listfile.csv", "community-listfile.csv", "listfile.txt")


def normalise(path: str) -> str:
    r"""Normalise an in-game path to the client's convention.

    The 3.3.5a client is case-insensitive but MPQ hashing is not, so tools
    conventionally store backslash-separated, lower-cased paths.
    """
    return path.replace("/", "\\").strip().lower()


def to_posix(path: str) -> str:
    """Inverse of :func:`normalise`, for laying files out on disk."""
    return path.replace("\\", "/").strip()


class Listfile:
    """Bidirectional FileDataID <-> path map."""

    __slots__ = ("_by_id", "_by_path", "source")

    def __init__(self, source: str = "<empty>") -> None:
        self._by_id: dict[int, str] = {}
        self._by_path: dict[str, int] = {}
        self.source = source

    # -- construction ---------------------------------------------------
    @classmethod
    def load(cls, path: str | os.PathLike[str]) -> Listfile:
        p = Path(path)
        if not p.is_file():
            raise MissingDependencyError(f"listfile not found: {p}")
        lf = cls(str(p))
        with p.open("r", encoding="utf-8", errors="replace") as fh:
            lf.update(fh)
        log.info(f"loaded {len(lf)} listfile entries from {p}")
        return lf

    @classmethod
    def discover(cls, explicit: str | os.PathLike[str] | None = None,
                 search_dirs: Iterable[str | os.PathLike[str]] = ()) -> Listfile:
        """Load from an explicit path, then ``$WOTLKCONV_LISTFILE``, then probe.

        Returns an empty listfile rather than raising when nothing is found;
        conversions that actually need it raise at the point of use so that
        FileDataID-free inputs still convert without one.
        """
        if explicit:
            return cls.load(explicit)
        env = os.environ.get(ENV_VAR)
        if env:
            return cls.load(env)
        probes: list[Path] = []
        for d in (*search_dirs, Path.cwd()):
            for name in DEFAULT_NAMES:
                probes.append(Path(d) / name)
        for candidate in probes:
            if candidate.is_file():
                return cls.load(candidate)
        return cls()

    def update(self, lines: Iterable[str]) -> None:
        by_id = self._by_id
        by_path = self._by_path
        for line in lines:
            m = _LINE.match(line)
            if not m:
                continue
            fdid = int(m.group(1))
            path = normalise(m.group(2))
            if not path:
                continue
            by_id[fdid] = path
            # First writer wins: the listfile is roughly ordered oldest-first,
            # and the oldest path for a FileDataID is the one WotLK-era data used.
            by_path.setdefault(path, fdid)

    # -- lookup ---------------------------------------------------------
    def __len__(self) -> int:
        return len(self._by_id)

    def __bool__(self) -> bool:
        return bool(self._by_id)

    def __contains__(self, fdid: int) -> bool:
        return fdid in self._by_id

    def __iter__(self) -> Iterator[tuple[int, str]]:
        return iter(self._by_id.items())

    def path_for(self, fdid: int) -> str | None:
        return self._by_id.get(fdid)

    def id_for(self, path: str) -> int | None:
        return self._by_path.get(normalise(path))

    def require_path(self, fdid: int, what: str = "asset") -> str:
        path = self._by_id.get(fdid)
        if path is None:
            raise MissingDependencyError(
                f"no listfile entry for {what} FileDataID {fdid}; "
                f"supply a newer listfile with --listfile"
            )
        return path


def placeholder_path(fdid: int, kind: str) -> str:
    """Deterministic stand-in path for an unresolved FileDataID.

    Used when the caller asked to keep converting despite an incomplete
    listfile.  It is the name a build gives a file it has no listfile entry
    for, ``unknown/<id>.<ext>``, so when the file is in the build the
    reference finds it; when it is not, the reference points at an asset the
    user has to supply or repoint themselves.
    """
    return normalise(f"unknown/{fdid}.{kind}")
