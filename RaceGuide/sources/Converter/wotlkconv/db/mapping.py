"""Declarative DB2 column -> DBC column mappings.

Both sides of a conversion come from DBDefs: the modern layout from the file's
own hash, the 3.3.5a one from the table's ``BUILD 3.3.5.12340`` layout. Because
both are named, columns whose names survived map themselves -- see
:func:`wotlkconv.db.target.auto_map`. A mapping file only has to describe what
actually changed.

    {
      "table": "CreatureDisplayInfo",
      "columns": [
        {"target": "TextureVariation", "array_index": 0, "type": "string",
         "from": "TextureVariationFileDataID", "transform": "basename"},
        {"target": "ModelID", "from": "ModelID", "id_offset": true}
      ]
    }

``target`` names the 3.3.5a column; ``index`` addresses it by position instead,
for the rare table with no definition covering Wrath. Columns the mapping does
not list and auto-mapping cannot match are written as zero. ``from`` may be a
list, in which case the first column the source actually has wins -- which is
how one mapping covers several builds whose column names drifted.
"""

from __future__ import annotations

import dataclasses
import json
import os
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from ..errors import ConversionError
from ..listfile import Listfile, normalise
from .dbc import TYPES

BUILTIN_DIR = Path(__file__).parent / "builtin"


def _strip_extension(path: str) -> str:
    return os.path.splitext(path)[0]


@dataclasses.dataclass(slots=True)
class ColumnMap:
    """How one 3.3.5a field gets its value."""

    #: Resolved once the target layout is known; one of these two is given.
    index: int | None = None
    #: Candidate 3.3.5a column names, first match wins. Several are allowed
    #: because a definition may spell a renamed column either way.
    target: tuple[str, ...] = ()
    target_array_index: int = 0
    type: str = "uint"
    source: tuple[str, ...] = ()
    array_index: int | None = None
    const: Any = None
    default: Any = None
    transform: str = ""
    scale: float | None = None
    #: Add the run's id offset, for the id column and references to it.
    id_offset: bool = False
    note: str = ""
    #: A row-level resolver (see :data:`RESOLVERS`) for a value that has to be
    #: joined from other tables rather than read out of one column, and its
    #: keyword arguments.
    resolve: str = ""
    args: dict[str, Any] = dataclasses.field(default_factory=dict)

    @property
    def label(self) -> str:
        if self.target:
            name = "|".join(self.target)
            if self.target_array_index:
                return f"{name}[{self.target_array_index}]"
            return name
        return f"field {self.index}"

    def describe(self) -> str:
        if self.const is not None:
            return f"{self.label} = {self.const!r}"
        if self.resolve:
            return f"{self.label} <- {self.resolve}({self.args or ''})"
        return f"{self.label} <- {'|'.join(self.source) or '?'}"


@dataclasses.dataclass
class TableMapping:
    """A whole table's worth of column maps."""

    table: str
    target_field_count: int = 0
    id_index: int = 0
    columns: list[ColumnMap] = dataclasses.field(default_factory=list)
    description: str = ""
    #: Columns whose value is a row id and so must move with --id-offset,
    #: whether they were mapped explicitly or matched by name.
    id_offset_columns: tuple[str, ...] = ()
    source: str = "<builtin>"
    #: Other tables the mapping's resolvers join against.
    requires_tables: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, payload: dict, source: str = "<memory>") -> TableMapping:
        mapping = cls(
            table=payload["table"],
            target_field_count=int(payload.get("target_field_count", 0)),
            id_index=int(payload.get("id_index", 0)),
            description=payload.get("description", ""),
            id_offset_columns=tuple(payload.get("id_offset_columns", [])),
            source=source,
            requires_tables=tuple(payload.get("requires_tables", [])),
        )
        seen: set[tuple] = set()
        for spec in payload.get("columns", []):
            index = int(spec["index"]) if "index" in spec else None
            raw_target = spec.get("target")
            if isinstance(raw_target, str):
                target: tuple[str, ...] = (raw_target,)
            elif raw_target:
                target = tuple(raw_target)
            else:
                target = ()
            if index is None and not target:
                raise ConversionError(
                    f"{source}: a column has neither 'target' nor 'index'")
            array_index = int(spec.get("target_array_index",
                                       spec.get("array_index", 0) if target
                                       else 0))
            key = (index, tuple(t.lower() for t in target), array_index)
            if key in seen:
                raise ConversionError(
                    f"{source}: target {target or index} is mapped twice")
            seen.add(key)
            kind = spec.get("type", "uint")
            if kind not in TYPES:
                raise ConversionError(
                    f"{source}: field {index} has unknown type {kind!r}; "
                    f"expected one of {', '.join(TYPES)}")
            raw_from = spec.get("from")
            if isinstance(raw_from, str):
                sources: tuple[str, ...] = (raw_from,)
            elif raw_from:
                sources = tuple(raw_from)
            else:
                sources = ()
            resolve = spec.get("resolve", "")
            if resolve and resolve not in RESOLVERS:
                raise ConversionError(
                    f"{source}: unknown resolver {resolve!r}; known resolvers "
                    f"are {', '.join(sorted(RESOLVERS))}")
            if not sources and "const" not in spec and not resolve:
                raise ConversionError(
                    f"{source}: field {index} has neither 'from', 'const' nor "
                    f"'resolve'")
            mapping.columns.append(ColumnMap(
                index=index, target=target, target_array_index=array_index,
                type=kind, source=sources,
                array_index=spec.get("array_index"),
                const=spec.get("const"),
                default=spec.get("default"),
                transform=spec.get("transform", ""),
                scale=spec.get("scale"),
                id_offset=bool(spec.get("id_offset", False)),
                note=spec.get("note", ""),
                resolve=resolve,
                args=dict(spec.get("args", {})),
            ))
        if mapping.target_field_count:
            widest = max((c.index for c in mapping.columns
                          if c.index is not None), default=-1)
            if widest >= mapping.target_field_count:
                raise ConversionError(
                    f"{source}: field {widest} is mapped but the table only "
                    f"has {mapping.target_field_count} fields")
        return mapping

    @classmethod
    def load(cls, path: str | os.PathLike[str]) -> TableMapping:
        p = Path(path)
        return cls.from_dict(json.loads(p.read_text(encoding="utf-8")), str(p))


class MappingLibrary:
    """Built-in mappings, with a user directory taking precedence."""

    def __init__(self, user_dir: str | os.PathLike[str] | None = None):
        self.user_dir = Path(user_dir) if user_dir else None
        self._cache: dict[str, TableMapping | None] = {}

    def get(self, table: str) -> TableMapping | None:
        key = table.lower()
        if key in self._cache:
            return self._cache[key]
        result = None
        for directory in (self.user_dir, BUILTIN_DIR):
            if directory is None or not directory.is_dir():
                continue
            for candidate in directory.glob("*.json"):
                if candidate.stem.lower() == key:
                    result = TableMapping.load(candidate)
                    break
            if result is not None:
                break
        self._cache[key] = result
        return result

    def tables(self) -> list[str]:
        names: dict[str, str] = {}
        for directory in (BUILTIN_DIR, self.user_dir):
            if directory is None or not directory.is_dir():
                continue
            for candidate in sorted(directory.glob("*.json")):
                names[candidate.stem.lower()] = candidate.stem
        return sorted(names.values())


# ---------------------------------------------------------------------------
# Transforms
# ---------------------------------------------------------------------------
class TransformContext:
    """What a transform needs beyond the value itself."""

    __slots__ = ("cache", "listfile", "missing", "path_prefix", "tables")

    def __init__(self, listfile: Listfile | None = None, path_prefix: str = "",
                 tables=None):
        self.listfile = listfile or Listfile()
        self.path_prefix = path_prefix
        self.missing: set[int] = set()
        #: Other tables, for resolvers that join; see :mod:`.tables`.
        self.tables = tables
        #: Per-conversion state a resolver builds once.
        self.cache: dict[str, Any] = {}

    def path_for(self, file_id: int) -> str:
        path = self.listfile.path_for(int(file_id))
        if path is None:
            self.missing.add(int(file_id))
            return ""
        if self.path_prefix:
            path = normalise(self.path_prefix.rstrip("\\/") + "\\" + path)
        return path


def _t_path(value: Any, ctx: TransformContext) -> str:
    return ctx.path_for(value) if value else ""


def _t_model_path(value: Any, ctx: TransformContext) -> str:
    """FileDataID -> path with an ``.mdx`` extension.

    3.3.5a DBCs name models with the Warcraft III extension and the client
    swaps it for ``.m2`` when it opens the file, so a ``.m2`` path here simply
    does not load.
    """
    path = ctx.path_for(value) if value else ""
    return _strip_extension(path) + ".mdx" if path else ""


def _t_basename(value: Any, ctx: TransformContext) -> str:
    """FileDataID -> bare filename, no directory and no extension.

    Texture variation columns hold names the client resolves against the
    model's own directory.
    """
    path = ctx.path_for(value) if value else ""
    return _strip_extension(os.path.basename(path.replace("\\", "/"))) if path else ""


def _t_identity(value: Any, _ctx: TransformContext) -> Any:
    return value


def _t_clamp_zero(value: Any, _ctx: TransformContext) -> Any:
    """Wrath has no -1 "unset" in columns modern builds give one."""
    try:
        return max(int(value), 0)
    except (TypeError, ValueError):
        return 0


def _t_wrath_item_flags(value: Any, _ctx: TransformContext) -> int:
    """Only ItemDisplayInfo flag bits 1, 2 and 4 existed in Wrath."""
    try:
        return int(value) & 0x7
    except (TypeError, ValueError):
        return 0


def _t_wrath_liquid_vertex_format(value: Any, _ctx: TransformContext) -> int:
    """3.3.5a has no vertex format 3 (height, UV and depth); keep the UVs."""
    try:
        return 1 if int(value) == 3 else int(value)
    except (TypeError, ValueError):
        return 0


TRANSFORMS = {
    "": _t_identity,
    "identity": _t_identity,
    "path": _t_path,
    "model_path": _t_model_path,
    "basename": _t_basename,
    "lower": lambda v, _c: str(v).lower(),
    "upper": lambda v, _c: str(v).upper(),
    "strip_extension": lambda v, _c: _strip_extension(str(v)),
    "clamp_zero": _t_clamp_zero,
    "wrath_item_flags": _t_wrath_item_flags,
    "wrath_liquid_vertex_format": _t_wrath_liquid_vertex_format,
}

# Row-level resolvers, by name: ``fn(row, ctx, **args) -> value``.  These sit
# here rather than at the top of the file because each of them imports the
# transform table defined above; importing them any earlier is a cycle.  None
# imports anything from this module, so the dependency only runs one way.
from .grounddoodad import RESOLVERS as _GROUND_RESOLVERS  # noqa: E402
from .itemdisplay import RESOLVERS as _ITEM_RESOLVERS  # noqa: E402
from .liquidtypes import RESOLVERS as _LIQUID_RESOLVERS  # noqa: E402


def _r_skybox_model(row: dict[str, Any], ctx: TransformContext) -> str:
    """The skybox model, where 3.3.5a's LightSkybox.Name holds it.

    Legion moved the model to SkyboxFileDataID and newer rows use Name for a
    description ("12ZAM Sky 01"), which 3.3.5a and Noggit would try to load
    as a file.
    """
    path = _t_model_path(row.get("SkyboxFileDataID") or 0, ctx)
    if path:
        return path
    name = str(row.get("Name") or "")
    return name if name.lower().endswith((".mdx", ".mdl", ".m2")) else ""


#: LoadingScreens columns holding the image, most 3.3.5a-like first.
LOADING_SCREEN_IMAGES = ("NarrowScreenFileDataID", "WideScreen169FileDataID",
                         "WideScreenFileDataID", "MainImageFileDataID")


def _r_loading_screen_file(row: dict[str, Any], ctx: TransformContext) -> str:
    """The loading screen image, which Legion moved to FileDataID columns.

    3.3.5a loads ``FileName`` (and, where ``HasWideScreen`` is set, the same
    name with ``Wide`` before the extension); with it empty, entering the map
    loads a file called "".
    """
    for column in LOADING_SCREEN_IMAGES:
        path = _t_path(row.get(column) or 0, ctx)
        if path:
            return path
    return str(row.get("FileName") or "")


def _r_loading_screen_wide(row: dict[str, Any], ctx: TransformContext) -> int:
    """1 when the wide image is the narrow one's name plus ``wide``, which is
    the only name 3.3.5a derives."""
    narrow = _t_path(row.get("NarrowScreenFileDataID") or 0, ctx)
    wide = _t_path(row.get("WideScreenFileDataID") or 0, ctx)
    if narrow and wide:
        return int(wide.lower() == _strip_extension(narrow).lower() + "wide.blp")
    return int(row.get("HasWideScreen") or 0)


def _r_loading_screen_name(row: dict[str, Any], ctx: TransformContext) -> str:
    name = str(row.get("Name") or "")
    if name:
        return name
    path = _r_loading_screen_file(row, ctx)
    return _strip_extension(os.path.basename(path.replace("\\", "/"))) if path else ""


RESOLVERS = {**_ITEM_RESOLVERS, **_GROUND_RESOLVERS, **_LIQUID_RESOLVERS,
             "lightskybox.model": _r_skybox_model,
             "loadingscreens.file": _r_loading_screen_file,
             "loadingscreens.wide": _r_loading_screen_wide,
             "loadingscreens.name": _r_loading_screen_name}


# ---------------------------------------------------------------------------
# Applying a mapping
# ---------------------------------------------------------------------------
def _coerce(value: Any, kind: str) -> Any:
    if kind == "string":
        return "" if value is None else str(value)
    if kind == "float":
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def apply_row(columns: Sequence[ColumnMap], row: dict[str, Any],
              ctx: TransformContext, id_offset: int = 0,
              source_name: str = "<mapping>") -> dict[int, tuple[str, Any]]:
    """Turn one modern row into ``{target index: (type, value)}``.

    Every column must already carry a resolved ``index``; see
    :func:`resolve_columns`.
    """
    out: dict[int, tuple[str, Any]] = {}
    for column in columns:
        if column.index is None:
            continue
        if column.const is not None:
            value: Any = column.const
        elif column.resolve:
            try:
                value = RESOLVERS[column.resolve](row, ctx, **column.args)
            except LookupError as exc:
                raise ConversionError(f"{source_name}: {column.label}: {exc}") from exc
        else:
            value = None
            for name in column.source:
                if name in row:
                    value = row[name]
                    break
            if isinstance(value, list):
                index = column.array_index or 0
                value = value[index] if index < len(value) else None
            if value is None:
                value = column.default

        if value is None:
            value = "" if column.type == "string" else 0

        transform = TRANSFORMS.get(column.transform)
        if transform is None:
            raise ConversionError(
                f"{source_name}: unknown transform {column.transform!r}; "
                f"known transforms are {', '.join(sorted(TRANSFORMS))}")
        value = transform(value, ctx)

        if column.scale is not None and column.type in ("float", "int", "uint"):
            value = _coerce(value, column.type) * column.scale
        if column.id_offset and id_offset and column.type != "string":
            numeric = _coerce(value, column.type)
            if numeric:
                value = numeric + id_offset

        out[column.index] = (column.type, _coerce(value, column.type))
    return out


def resolve_columns(mapping: TableMapping, target, source_name: str
                    ) -> list[ColumnMap]:
    """Turn each mapped column's target name into a field index.

    A name the 3.3.5a table does not have is an error rather than a silent
    skip: it means the mapping was written against a different build, and
    quietly dropping the column would produce a table that looks converted.
    """
    resolved: list[ColumnMap] = []
    for column in mapping.columns:
        if column.index is not None:
            if column.index >= target.field_count:
                raise ConversionError(
                    f"{source_name}: field {column.index} is mapped but the "
                    f"table has {target.field_count} fields")
            resolved.append(column)
            continue
        field = None
        for candidate in column.target:
            field = target.by_name(candidate, column.target_array_index)
            if field is not None:
                break
        if field is None:
            if not target.named:
                raise ConversionError(
                    f"{source_name}: {column.label!r} is mapped by name, but "
                    f"the 3.3.5a {mapping.table} layout came from "
                    f"{target.origin}, which gives the number of columns and "
                    f"not their names. Either add a definition covering the "
                    f"Wrath build, or pin this column with \"index\"")
            raise ConversionError(
                f"{source_name}: the 3.3.5a {mapping.table} has no column "
                f"{column.label!r}. Its columns are: "
                + ", ".join(target.column_names()))
        resolved.append(dataclasses.replace(column, index=field.index,
                                            type=column.type or field.type))
    return resolved


def missing_sources(columns: Sequence[ColumnMap],
                    available: Iterable[str]) -> list[ColumnMap]:
    """Mapped columns whose source is absent from this build's table."""
    have = {name.lower() for name in available}
    out = []
    for column in columns:
        if column.const is not None or not column.source:
            continue
        if not any(name.lower() in have for name in column.source):
            out.append(column)
    return out
