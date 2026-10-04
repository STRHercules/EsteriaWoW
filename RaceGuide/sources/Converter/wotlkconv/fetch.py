"""Getting the two things a patch build needs but the game does not ship.

A conversion is only as good as its references.  Modern assets name their
textures, models and animations by FileDataID, and modern databases carry no
column names at all, so without the community listfile every reference comes
out empty and without WoWDBDefs every table is refused.  Both are public,
both are maintained by the same community that documented the formats, and
neither is in the game folder.

Fetching them is therefore useful but never automatic.  It reaches out to the
network, downloads a couple of hundred megabytes and writes to a cache
directory, and a tool should not do any of that because it felt like it --
``--fetch`` asks for it explicitly, the URLs are named in the output, and
anything already cached is reused rather than downloaded again.
"""

from __future__ import annotations

import io
import os
import urllib.request
import zipfile
from pathlib import Path

from . import log
from .errors import ConverterError

#: Every filename in every build Blizzard has published, as FileDataID;path.
LISTFILE_URL = ("https://github.com/wowdev/wow-listfile/releases/latest/"
                "download/community-listfile.csv")

#: Published TACT keys, for content that shipped encrypted and was later
#: released.  Unreleased content stays encrypted whatever this holds.
KEYS_URL = "https://raw.githubusercontent.com/wowdev/TACTKeys/master/WoW.txt"

#: The column definitions, as a source archive so no git client is needed.
DBDEFS_URL = "https://github.com/wowdev/WoWDBDefs/archive/refs/heads/master.zip"

#: How long to wait on a stalled connection before giving up.
TIMEOUT_SECONDS = 120


def default_cache() -> Path:
    """Where downloads are kept between runs."""
    base = os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache")
    return Path(base) / "wotlkconv"


def _download(url: str, dest: Path) -> Path:
    """Fetch ``url`` to ``dest``, via a temporary file so a failure leaves
    no half-written cache entry behind."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_suffix(dest.suffix + ".part")
    log.info(f"downloading {url}")
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            size = int(response.headers.get("Content-Length") or 0)
            written = 0
            with partial.open("wb") as out:
                while chunk := response.read(1 << 20):
                    out.write(chunk)
                    written += len(chunk)
    except OSError as exc:
        partial.unlink(missing_ok=True)
        raise ConverterError(f"could not download {url}: {exc}") from exc
    if size and written != size:
        partial.unlink(missing_ok=True)
        raise ConverterError(
            f"{url} ended early: {written} bytes of {size}")
    partial.replace(dest)
    log.info(f"saved {written / 1e6:.1f} MB to {dest}")
    return dest


def fetch_listfile(cache: Path | None = None, *, force: bool = False,
                   url: str = LISTFILE_URL) -> Path:
    """The community listfile, downloaded once and reused after that."""
    cache = Path(cache) if cache else default_cache()
    dest = cache / "community-listfile.csv"
    if dest.is_file() and not force:
        log.info(f"using the cached listfile at {dest}")
        return dest
    return _download(url, dest)


def fetch_keys(cache: Path | None = None, *, force: bool = False,
               url: str = KEYS_URL) -> Path:
    """The community TACT key list, downloaded once and reused after that."""
    cache = Path(cache) if cache else default_cache()
    dest = cache / "WoW.txt"
    if dest.is_file() and not force:
        log.info(f"using the cached TACT keys at {dest}")
        return dest
    return _download(url, dest)


def fetch_definitions(cache: Path | None = None, *, force: bool = False,
                      url: str = DBDEFS_URL) -> Path:
    """The WoWDBDefs ``definitions`` folder, out of the source archive.

    Only the ``.dbd`` files are kept: the archive also carries code and tests
    this tool has no use for.
    """
    cache = Path(cache) if cache else default_cache()
    dest = cache / "definitions"
    if dest.is_dir() and any(dest.glob("*.dbd")) and not force:
        log.info(f"using the cached definitions at {dest}")
        return dest

    archive = _download(url, cache / "WoWDBDefs.zip")
    dest.mkdir(parents=True, exist_ok=True)
    written = 0
    try:
        with zipfile.ZipFile(io.BytesIO(archive.read_bytes())) as zf:
            for entry in zf.namelist():
                if not entry.lower().endswith(".dbd"):
                    continue
                if "definitions/" not in entry:
                    continue
                (dest / Path(entry).name).write_bytes(zf.read(entry))
                written += 1
    except (zipfile.BadZipFile, OSError) as exc:
        raise ConverterError(f"could not read {archive}: {exc}") from exc
    if not written:
        raise ConverterError(
            f"{url} held no .dbd definitions; the archive layout may have "
            f"changed, so pass --dbd with your own WoWDBDefs checkout")
    log.info(f"extracted {written} table definition(s) to {dest}")
    return dest
