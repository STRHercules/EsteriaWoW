"""Other client databases, read on demand while converting one.

Most tables convert on their own.  A few cannot: modern ItemDisplayInfo no
longer names its models, textures or icon, and reaching them means joining
ModelFileData, TextureFileData, ItemDisplayInfoMaterialRes, ItemAppearance and
more.  This gives a conversion those tables -- out of the install it is reading,
or out of a folder of extracted ``.db2`` files -- parsed once and indexed on
the columns the joins use.
"""

from __future__ import annotations

import os
from collections import defaultdict
from pathlib import Path
from typing import Any

from .. import log
from ..errors import ConverterError
from ..listfile import Listfile
from . import dbd
from .db2 import Db2Table, parse_db2


class TableProvider:
    """Parses and caches client databases by table name."""

    def __init__(self, definitions: dbd.DbdIndex, *, storage=None,
                 listfile: Listfile | None = None,
                 directory: str | os.PathLike[str] | None = None):
        self.definitions = definitions
        self.storage = storage
        self.listfile = listfile
        self.directory = Path(directory) if directory else None
        self._tables: dict[str, Db2Table | None] = {}
        self._indices: dict[tuple[str, str], dict[Any, list[dict]]] = {}
        self._file_ids: dict[str, int] | None = None

    def _file_id(self, name: str) -> int | None:
        if self.listfile is None:
            return None
        if self._file_ids is None:
            prefix = "dbfilesclient\\"
            self._file_ids = {path[len(prefix):-4]: fid for fid, path in self.listfile
                              if path.startswith(prefix) and path.endswith(".db2")}
        return self._file_ids.get(name.lower())

    def _read(self, name: str) -> bytes | None:
        if self.directory is not None:
            for candidate in self.directory.iterdir():
                if candidate.name.lower() == f"{name.lower()}.db2":
                    return candidate.read_bytes()
        if self.storage is not None:
            file_id = self._file_id(name)
            if file_id is not None:
                data, why = self.storage.try_read_file_id(file_id, zero_encrypted=True)
                if data is None:
                    log.warn(f"{name}.db2 could not be read for a join: {why}")
                return data
        return None

    def get(self, name: str) -> Db2Table | None:
        """The parsed table, or None when it is not available."""
        key = name.lower()
        if key not in self._tables:
            data = self._read(name)
            table = None
            if data is not None:
                try:
                    table = parse_db2(data, f"{name}.db2", self.definitions, name)
                except ConverterError as exc:
                    log.warn(f"{name}.db2 could not be parsed for a join: {exc}")
            self._tables[key] = table
        return self._tables[key]

    def row(self, name: str, row_id: int) -> dict | None:
        table = self.get(name)
        return table.rows.get(int(row_id)) if table is not None else None

    def index(self, name: str, column: str) -> dict[Any, list[dict]]:
        """Rows of ``name`` grouped by ``column``; each row carries its ``ID``."""
        key = (name.lower(), column)
        if key not in self._indices:
            grouped: dict[Any, list[dict]] = defaultdict(list)
            table = self.get(name)
            if table is not None:
                for row_id, row in table.rows.items():
                    value = row.get(column)
                    if value is not None:
                        grouped[value].append({**row, "ID": row_id})
            self._indices[key] = dict(grouped)
        return self._indices[key]

    def missing(self, names: list[str]) -> list[str]:
        return [n for n in names if self.get(n) is None]

    def clear(self) -> None:
        """Drop everything parsed, so a worker does not keep it between jobs."""
        self._tables.clear()
        self._indices.clear()
