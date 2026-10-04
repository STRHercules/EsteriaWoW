"""Client database reading and downgrading (``.db2`` -> ``.dbc``)."""

from .convert import convert_db2, find_template, table_name_for
from .db2 import Db2Table, inspect_db2, parse_db2
from .dbc import DbcBuilder, DbcTable, inspect_dbc
from .dbd import DbdIndex, parse_definition
from .mapping import MappingLibrary, TableMapping

__all__ = [
    "Db2Table",
    "DbcBuilder",
    "DbcTable",
    "DbdIndex",
    "MappingLibrary",
    "TableMapping",
    "convert_db2",
    "find_template",
    "inspect_db2",
    "inspect_dbc",
    "parse_db2",
    "parse_definition",
    "table_name_for",
]
