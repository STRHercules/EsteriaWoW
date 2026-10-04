"""Parsing wowdev DBDefs, so modern database columns have names.

A ``.db2`` carries no column names -- only widths and offsets. The community
DBDefs repository supplies the names, types and array sizes, keyed by *layout
hash*, which is a value the file itself carries. Matching on that rather than
on a build string is exact: a table whose shape has not changed keeps the same
hash across many builds.

Definition file shape::

    COLUMNS
    int ID
    int<CreatureModelData::ID> ModelID
    string ModelName
    float GeoBox[6]

    LAYOUT 1FE1BDA4, 3B0C8F12
    BUILD 9.0.1.34490
    $id$ID<32>
    ModelID<32>
    ModelName
    GeoBox[6]

Annotations inside ``$...$`` mark the id column, columns held outside the
record ("noninline"), and relationship columns.
"""

from __future__ import annotations

import dataclasses
import os
import re
from collections.abc import Iterable, Iterator
from pathlib import Path

from .. import log
from ..errors import MissingDependencyError

#: Environment variable consulted when no --dbd is given.
ENV_VAR = "WOTLKCONV_DBD"

_COLUMN = re.compile(
    r"^\s*(?P<type>int|float|string|locstring|uint)"
    r"(?:<(?P<foreign>[^>]*)>)?\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*(?P<verified>\?)?\s*(?://.*)?$")

_FIELD = re.compile(
    r"^\s*(?:\$(?P<annotations>[^$]*)\$)?"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
    r"(?:<(?P<width>u?-?\d+)>)?"
    r"(?:\[(?P<array>\d+)\])?"
    r"\s*(?://.*)?$")

#: DBD type -> how the value should be interpreted once read.
TYPE_MAP = {
    "int": "int",
    "uint": "int",
    "float": "float",
    "string": "string",
    "locstring": "string",
}


@dataclasses.dataclass(slots=True)
class Column:
    """One column in a particular layout."""

    name: str
    type: str = "int"           # int | float | string
    bit_width: int = 32
    signed: bool = True
    array_size: int = 1
    is_id: bool = False
    #: The value is not stored in the record: the section's id list for an id,
    #: the relationship map for a relation.
    non_inline: bool = False
    #: A foreign key.  On its own (``$relation$``) it is an ordinary field in
    #: the record; only with ``noninline`` does it live in the relationship map.
    relation: bool = False
    foreign_table: str = ""
    #: Declared ``locstring``: one string per locale.  A WDC file stores just
    #: the client's own; a pre-Cataclysm ``.dbc`` stores all of them.
    localized: bool = False

    @property
    def is_string(self) -> bool:
        return self.type == "string"


@dataclasses.dataclass(slots=True)
class Layout:
    """One ``LAYOUT`` block: an ordered column list plus the builds it covers."""

    hashes: list[str] = dataclasses.field(default_factory=list)
    builds: list[str] = dataclasses.field(default_factory=list)
    columns: list[Column] = dataclasses.field(default_factory=list)

    @property
    def id_column(self) -> Column | None:
        for column in self.columns:
            if column.is_id:
                return column
        return self.columns[0] if self.columns else None

    def inline_columns(self) -> list[Column]:
        """Columns that occupy a slot in the record itself."""
        return [c for c in self.columns if not c.non_inline]

    def by_name(self, name: str) -> Column | None:
        lowered = name.lower()
        for column in self.columns:
            if column.name.lower() == lowered:
                return column
        return None


@dataclasses.dataclass(slots=True)
class Definition:
    """A parsed ``.dbd`` file: shared column types plus every layout."""

    name: str
    types: dict[str, tuple[str, str]] = dataclasses.field(default_factory=dict)
    layouts: list[Layout] = dataclasses.field(default_factory=list)

    def by_hash(self, layout_hash: int | str) -> Layout | None:
        wanted = (f"{layout_hash:08X}" if isinstance(layout_hash, int)
                  else str(layout_hash).upper())
        for layout in self.layouts:
            if wanted in layout.hashes:
                return layout
        return None

    def by_build(self, build: str) -> Layout | None:
        for layout in self.layouts:
            for entry in layout.builds:
                if _build_matches(entry, build):
                    return layout
        return None

    def by_field_count(self, inline_columns: int) -> Layout | None:
        """The layout with exactly this many columns in the record.

        DBDefs lags new builds, so a file's layout hash is often absent. The
        number of columns the file itself declares is a checkable signal:
        exactly one layout usually matches, and picking a layout with the wrong
        column count would mislabel every column after the first difference.
        """
        matches = [layout for layout in self.layouts
                   if len(layout.inline_columns()) == inline_columns]
        return matches[-1] if len(matches) == 1 else None

    def newest(self) -> Layout | None:
        return self.layouts[-1] if self.layouts else None


def _build_matches(spec: str, build: str) -> bool:
    """``9.0.1.34490`` or a ``a-b`` range against a concrete build string."""
    spec = spec.strip()
    if "-" in spec:
        low, _, high = spec.partition("-")
        return _build_key(low) <= _build_key(build) <= _build_key(high)
    return spec == build.strip()


def _build_key(build: str) -> tuple:
    return tuple(int(p) if p.isdigit() else 0 for p in build.strip().split("."))


def parse_definition(text: str, name: str = "<dbd>") -> Definition:
    """Parse one ``.dbd`` file."""
    definition = Definition(name=name)
    lines = text.splitlines()
    index = 0
    total = len(lines)

    # -- COLUMNS block --------------------------------------------------
    while index < total and lines[index].strip() != "COLUMNS":
        index += 1
    index += 1
    while index < total and lines[index].strip():
        m = _COLUMN.match(lines[index])
        if m:
            definition.types[m.group("name").lower()] = (
                m.group("type"), m.group("foreign") or "")
        index += 1

    # -- definition blocks ----------------------------------------------
    # Blocks are separated by blank lines.  Only builds from WDB6 on carry a
    # LAYOUT hash; a DBC-era block -- every 3.3.5a table -- starts straight
    # with its BUILD lines, and has to be a layout of its own rather than
    # being folded into whichever block came before it.
    current: Layout | None = None
    while index < total:
        line = lines[index].strip()
        index += 1
        if not line:
            current = None
            continue
        if line.startswith(("COMMENT", "//")):
            continue
        if current is None:
            if not line.startswith(("LAYOUT", "BUILD")):
                continue
            current = Layout()
            definition.layouts.append(current)
        if line.startswith("LAYOUT"):
            current.hashes.extend(h.strip().upper()
                                  for h in line[6:].split(",") if h.strip())
            continue
        if line.startswith("BUILD"):
            current.builds.extend(b.strip() for b in line[5:].split(",") if b.strip())
            continue

        m = _FIELD.match(line)
        if not m:
            continue
        annotations = {a.strip().lower()
                       for a in (m.group("annotations") or "").split(",") if a.strip()}
        col_name = m.group("name")
        declared_type, foreign = definition.types.get(col_name.lower(), ("int", ""))
        width_text = m.group("width")
        signed = True
        bit_width = 32
        if width_text:
            if width_text.startswith("u"):
                signed = False
                width_text = width_text[1:]
            bit_width = abs(int(width_text))
        elif declared_type in ("float", "string", "locstring"):
            bit_width = 32

        current.columns.append(Column(
            name=col_name,
            type=TYPE_MAP.get(declared_type, "int"),
            bit_width=bit_width,
            signed=signed and declared_type != "uint",
            array_size=int(m.group("array") or 1),
            is_id="id" in annotations,
            non_inline="noninline" in annotations,
            relation="relation" in annotations,
            foreign_table=foreign.split("::")[0] if foreign else "",
            localized=declared_type == "locstring",
        ))
    return definition


class DbdIndex:
    """A directory of ``.dbd`` files, looked up by table name."""

    #: Probed when neither --dbd nor the environment variable is set.
    DEFAULT_NAMES = ("definitions", "dbd", "WoWDBDefs/definitions")

    def __init__(self, directory: str | os.PathLike[str] | None = None):
        self.directory = Path(directory) if directory else None
        self._cache: dict[str, Definition | None] = {}

    def __bool__(self) -> bool:
        return self.directory is not None and self.directory.is_dir()

    @classmethod
    def discover(cls, explicit=None, search_dirs: Iterable = ()) -> DbdIndex:
        if explicit:
            index = cls(explicit)
            if not index:
                raise MissingDependencyError(
                    f"no .dbd definitions in {explicit}; point --dbd at the "
                    f"'definitions' folder of a WoWDBDefs checkout")
            log.info(f"using DBD definitions from {index.directory}")
            return index
        env = os.environ.get(ENV_VAR)
        if env and Path(env).is_dir():
            return cls(env)
        for base in (*search_dirs, Path.cwd()):
            for name in cls.DEFAULT_NAMES:
                candidate = Path(base) / name
                if candidate.is_dir():
                    return cls(candidate)
        return cls(None)

    def get(self, table: str) -> Definition | None:
        key = table.lower()
        if key in self._cache:
            return self._cache[key]
        result = None
        if self.directory is not None:
            for candidate in (f"{table}.dbd", f"{key}.dbd"):
                path = self.directory / candidate
                if path.is_file():
                    result = parse_definition(
                        path.read_text(encoding="utf-8", errors="replace"), table)
                    break
            if result is None:
                # Filenames are case-sensitive on Linux; fall back to a scan.
                for path in self.directory.glob("*.dbd"):
                    if path.stem.lower() == key:
                        result = parse_definition(
                            path.read_text(encoding="utf-8", errors="replace"),
                            table)
                        break
        self._cache[key] = result
        return result

    def tables(self) -> Iterator[str]:
        if self.directory is None:
            return iter(())
        return (p.stem for p in sorted(self.directory.glob("*.dbd")))
