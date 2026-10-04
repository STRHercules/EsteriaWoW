"""Structured per-file conversion results.

Downgrading is lossy by nature, and the interesting output of a batch run is
not "did it crash" but "what did it have to throw away".  Every converter
records those decisions here so the CLI can print a summary and emit JSON for
scripted pipelines.
"""

from __future__ import annotations

import dataclasses
import json
import os
import time
from collections.abc import Iterable, Iterator
from enum import Enum
from pathlib import Path
from typing import Any


class Status(str, Enum):
    OK = "ok"
    #: Converted, but something the 3.3.5a client cannot express was dropped.
    LOSSY = "lossy"
    #: Already a valid 3.3.5a asset; copied through unchanged.
    PASSTHROUGH = "passthrough"
    #: Not converted on its own because another output already carries it --
    #: a model's skins, a WMO's groups, a tile's _tex0 and _obj0 pieces.
    MERGED = "merged"
    SKIPPED = "skipped"
    FAILED = "failed"


#: Severity ordering used when folding note levels into a file status.
_RANK = {Status.OK: 0, Status.PASSTHROUGH: 0, Status.MERGED: 0,
         Status.SKIPPED: 1, Status.LOSSY: 2, Status.FAILED: 3}


@dataclasses.dataclass(slots=True)
class Note:
    """One thing worth telling the user about a single file."""

    level: str  # "info" | "lossy" | "warn" | "error"
    code: str   # stable machine-readable identifier, e.g. "m2.particle.multitexture"
    message: str
    detail: dict[str, Any] = dataclasses.field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        d = {"level": self.level, "code": self.code, "message": self.message}
        if self.detail:
            d["detail"] = self.detail
        return d


@dataclasses.dataclass(slots=True)
class FileResult:
    source: str
    target: str | None = None
    kind: str = "unknown"
    status: Status = Status.OK
    source_version: str | None = None
    target_version: str | None = None
    bytes_in: int = 0
    bytes_out: int = 0
    elapsed: float = 0.0
    notes: list[Note] = dataclasses.field(default_factory=list)
    extra: dict[str, Any] = dataclasses.field(default_factory=dict)
    #: The input this result accounts for.  Several results may name one
    #: input -- an animation every model sharing a skeleton writes under its
    #: own name, a model split in two -- and the accounting counts it once.
    file_id: int | None = None

    # -- note helpers ---------------------------------------------------
    def _add(self, level: str, code: str, message: str, **detail: Any) -> None:
        self.notes.append(Note(level, code, message, detail))

    def info(self, code: str, message: str, **detail: Any) -> None:
        self._add("info", code, message, **detail)

    def lossy(self, code: str, message: str, **detail: Any) -> None:
        """Record data that could not survive the downgrade."""
        self._add("lossy", code, message, **detail)
        self.bump(Status.LOSSY)

    def warn(self, code: str, message: str, **detail: Any) -> None:
        self._add("warn", code, message, **detail)

    def fail(self, code: str, message: str, **detail: Any) -> None:
        self._add("error", code, message, **detail)
        self.bump(Status.FAILED)

    def bump(self, status: Status) -> None:
        """Raise the status to ``status`` if that is more severe than current."""
        if _RANK[status] > _RANK[self.status]:
            self.status = status

    @property
    def ok(self) -> bool:
        return self.status is not Status.FAILED

    def as_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "source": self.source,
            "target": self.target,
            "kind": self.kind,
            "status": self.status.value,
            **({"file_id": self.file_id} if self.file_id is not None else {}),
            "bytes_in": self.bytes_in,
            "bytes_out": self.bytes_out,
            "elapsed_ms": round(self.elapsed * 1000, 2),
        }
        if self.source_version:
            d["source_version"] = self.source_version
        if self.target_version:
            d["target_version"] = self.target_version
        if self.notes:
            d["notes"] = [n.as_dict() for n in self.notes]
        if self.extra:
            d["extra"] = self.extra
        return d


@dataclasses.dataclass(slots=True)
class Report:
    """Aggregate of a whole run.

    A whole retail build reports on nearly two million files, and holding a
    result object for each one grows the process by gigabytes before the
    report is written -- then serialising them all at once needs as much
    again.  With ``spool`` set, each result is written to that file as a JSON
    line the moment it arrives; only the counts and the failures stay in
    memory, and :meth:`write_json` streams the spool into the report.
    """

    files: list[FileResult] = dataclasses.field(default_factory=list)
    started: float = dataclasses.field(default_factory=time.time)
    finished: float | None = None
    spool: Path | None = None
    _handle: Any = None
    _counts: dict[str, int] = dataclasses.field(default_factory=dict)
    _total: int = 0
    _failed: list[FileResult] = dataclasses.field(default_factory=list)
    #: One bit per FileDataID already accounted for (~1 MB for a whole build).
    _seen: bytearray = dataclasses.field(default_factory=bytearray)
    _books: dict[str, int] = dataclasses.field(default_factory=dict)
    _extra_outputs: int = 0

    def _book(self, result: FileResult) -> None:
        """Count an input once, under the status of its first result."""
        fid = result.file_id
        if fid is not None:
            byte, bit = fid >> 3, 1 << (fid & 7)
            if byte >= len(self._seen):
                self._seen.extend(bytes(byte + 1 - len(self._seen) + (1 << 16)))
            if self._seen[byte] & bit:
                self._extra_outputs += 1
                return
            self._seen[byte] |= bit
        s = result.status.value
        self._books[s] = self._books.get(s, 0) + 1

    def add(self, result: FileResult) -> FileResult:
        self._book(result)
        if self.spool is None:
            self.files.append(result)
            return result
        if self._handle is None:
            # The report usually sits in the output folder, which a fresh run
            # has not created yet when the planner's results arrive.
            if str(self.spool) != os.devnull:
                self.spool.parent.mkdir(parents=True, exist_ok=True)
            self._handle = open(self.spool, "w", encoding="utf-8")  # noqa: SIM115
        self._handle.write(json.dumps(result.as_dict()) + "\n")
        self._total += 1
        status = result.status.value
        self._counts[status] = self._counts.get(status, 0) + 1
        if result.status is Status.FAILED:
            # Enough to say what failed and why, without the rest of the notes.
            self._failed.append(FileResult(
                source=result.source, kind=result.kind, status=result.status,
                notes=[n for n in result.notes if n.level == "error"]))
        return result

    def extend(self, results: Iterable[FileResult]) -> None:
        for result in results:
            self.add(result)

    def close(self) -> None:
        self.finished = time.time()
        if self._handle is not None:
            self._handle.close()
            self._handle = None

    # -- aggregates -----------------------------------------------------
    def counts(self) -> dict[str, int]:
        if self.spool is not None:
            return dict(self._counts)
        out: dict[str, int] = {}
        for f in self.files:
            out[f.status.value] = out.get(f.status.value, 0) + 1
        return out

    @property
    def total(self) -> int:
        return self._total if self.spool is not None else len(self.files)

    @property
    def failed(self) -> list[FileResult]:
        if self.spool is not None:
            return list(self._failed)
        return [f for f in self.files if f.status is Status.FAILED]

    @property
    def lossy(self) -> list[FileResult]:
        if self.spool is not None:
            raise RuntimeError("a spooled report keeps only counts of lossy "
                               "files; use counts()")
        return [f for f in self.files if f.status is Status.LOSSY]

    def file_dicts(self) -> Iterator[dict[str, Any]]:
        """Every file's result as it appears in the JSON report."""
        if self.spool is None:
            yield from (f.as_dict() for f in self.files)
            return
        if self._handle is not None:
            self._handle.flush()
        if not self.spool.exists():
            return
        with self.spool.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    yield json.loads(line)

    def accounting(self) -> dict[str, int]:
        """Where every input file ended up.

        The point of this is that it adds up: a run that read N files reports
        N files, so a format nobody thought about cannot quietly disappear
        between the planner and the output.
        """
        counts = self._books
        written = sum(counts.get(s.value, 0) for s in
                      (Status.OK, Status.LOSSY, Status.PASSTHROUGH))
        merged = counts.get(Status.MERGED.value, 0)
        skipped = counts.get(Status.SKIPPED.value, 0)
        failed = counts.get(Status.FAILED.value, 0)
        return {
            "inputs": written + merged + skipped + failed,
            "written": written,
            "merged": merged,
            "skipped": skipped,
            "failed": failed,
            "results": self.total,
            "extra_outputs": self._extra_outputs,
        }

    def as_dict(self) -> dict[str, Any]:
        return {**self.as_dict_without_files(), "files": list(self.file_dicts())}

    def write_json(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        if self.spool is None:
            Path(path).write_text(
                json.dumps(self.as_dict(), indent=2, sort_keys=False) + "\n",
                encoding="utf-8",
            )
            return
        # Streamed: the header as usual, then one file per line, never all
        # of them in memory at once.
        head = self.as_dict_without_files()
        text = json.dumps(head, indent=2, sort_keys=False)
        with Path(path).open("w", encoding="utf-8") as out:
            out.write(text[:-2] + ',\n  "files": [')
            out.writelines(("," if index else "") + "\n    " + json.dumps(entry) for index, entry in enumerate(self.file_dicts()))
            out.write("\n  ]\n}\n")

    def as_dict_without_files(self) -> dict[str, Any]:
        return {
            "tool": "wotlkconv",
            "target": {"patch": "3.3.5a", "build": 12340},
            "started": self.started,
            "finished": self.finished,
            "elapsed_s": round((self.finished or time.time()) - self.started, 3),
            "counts": self.counts(),
            "accounting": self.accounting(),
        }

    def summary_lines(self, verbose: bool = False) -> list[str]:
        counts = self.counts()
        total = self.total
        parts = [f"{counts.get(s.value, 0)} {s.value}" for s in Status
                 if counts.get(s.value)]
        lines = [f"{total} file(s): " + ", ".join(parts) if parts
                 else f"{total} file(s)"]
        books = self.accounting()
        if books["merged"] or books["skipped"]:
            lines.append(
                f"  every input accounted for: {books['written']} written, "
                f"{books['merged']} carried by another file, "
                f"{books['skipped']} skipped, {books['failed']} failed")
        for f in self.file_dicts() if verbose else (
                r.as_dict() for r in self.failed):
            notes = f.get("notes", [])
            if f["status"] == Status.FAILED.value:
                for n in notes:
                    if n["level"] == "error":
                        lines.append(f"  FAILED {f['source']}: {n['message']}")
            elif verbose and notes:
                lines.append(f"  {f['status'].upper()} {f['source']}")
                for n in notes:
                    lines.append(f"      [{n['level']}] {n['message']}")
        return lines
