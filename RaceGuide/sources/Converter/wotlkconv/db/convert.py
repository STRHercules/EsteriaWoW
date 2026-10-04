"""Turning a modern ``.db2`` into a 3.3.5a ``.dbc``.

Two things have to line up: the *data*, which comes out of the DB2 with column
names supplied by a DBD definition, and the *layout*, which comes from a
mapping file and ideally from the user's own client ``.dbc`` used as a
template.

Merging onto a template is the normal case. Converting a model is useless until
something references it, and what references it is a row in a table the user
already has -- so new rows are appended to their existing table rather than
replacing it, and ``--id-offset`` moves the modern ids into a range that will
not collide with Blizzard's.
"""

from __future__ import annotations

import dataclasses
import os
import time
from collections.abc import Sequence
from typing import Any

from ..errors import ConversionError
from ..listfile import Listfile
from ..options import Options
from ..report import FileResult, Status
from . import dbd
from .db2 import Db2Table, parse_db2
from .dbc import DbcBuilder, DbcTable
from .mapping import (
    ColumnMap,
    MappingLibrary,
    TableMapping,
    TransformContext,
    apply_row,
    missing_sources,
    resolve_columns,
)
from .target import (
    LOCSTRING_FLAGS,
    WOTLK_BUILD,
    auto_map,
    cross_check,
    layout_from_dbd,
    layout_from_field_count,
)
from .target import describe as describe_layout


def table_name_for(path: str) -> str:
    """``dbfilesclient/creaturedisplayinfo.db2`` -> ``creaturedisplayinfo``."""
    stem = os.path.splitext(os.path.basename(path.replace("\\", "/")))[0]
    return stem


def find_template(directory: str | os.PathLike[str] | None,
                  table: str) -> bytes | None:
    """Look for ``<Table>.dbc`` in a directory, case-insensitively."""
    if not directory:
        return None
    from pathlib import Path

    base = Path(directory)
    if not base.is_dir():
        return None
    wanted = f"{table}.dbc".lower()
    for candidate in base.iterdir():
        if candidate.is_file() and candidate.name.lower() == wanted:
            return candidate.read_bytes()
    return None


def _row_matches(row: dict[str, Any], where: Sequence[tuple[str, str]]) -> bool:
    for column, expected in where:
        value = row.get(column)
        if isinstance(value, list):
            if not any(str(v) == expected for v in value):
                return False
        elif str(value) != expected:
            return False
    return True


def convert_db2(data: bytes, source_name: str, opts: Options,
                listfile: Listfile | None = None,
                definitions: dbd.DbdIndex | None = None,
                library: MappingLibrary | None = None,
                template_data: bytes | None = None,
                table: str | None = None,
                result: FileResult | None = None,
                tables=None) -> tuple[bytes, FileResult]:
    """Convert one client database. Returns (DBC bytes, result).

    ``tables`` (a :class:`~.tables.TableProvider`) gives resolvers the other
    tables a mapping joins against, such as ItemDisplayInfo's.
    """
    started = time.time()
    res = result or FileResult(source=source_name, kind="db2")
    res.kind = "db2"
    res.bytes_in = len(data)
    listfile = listfile or Listfile()
    library = library or MappingLibrary(opts.db_mappings or None)

    table_name = table or table_name_for(source_name)
    parsed: Db2Table = parse_db2(data, source_name, definitions, table_name)
    res.source_version = (f"{parsed.magic} {len(parsed.rows)} row(s), "
                          f"{len(parsed.columns)} column(s)")

    if not parsed.named:
        res.fail("db2.no_definition",
                 f"no DBD definition for {table_name}, so its columns are "
                 f"anonymous and cannot be mapped by name. Pass --dbd pointing "
                 f"at the 'definitions' folder of a WoWDBDefs checkout")
        res.elapsed = time.time() - started
        return b"", res

    if parsed.encrypted_sections:
        res.lossy("db2.encrypted",
                  f"{parsed.encrypted_sections} section(s) are encrypted and "
                  f"were skipped, losing {parsed.skipped_records} row(s); "
                  f"supply the TACT key with --casc-keys if you have it",
                  sections=parsed.encrypted_sections,
                  records=parsed.skipped_records)

    # -- the 3.3.5a side of the table -------------------------------------
    mapping = library.get(table_name)
    definition = definitions.get(table_name) if definitions else None
    target = layout_from_dbd(definition) if definition else None

    if target is not None:
        res.info("db2.layout_from_definition",
                 f"3.3.5a layout taken from {table_name}'s own definition: "
                 f"{describe_layout(target)}")
    elif mapping is not None and mapping.target_field_count:
        target = layout_from_field_count(mapping.target_field_count,
                                         mapping.source)
        res.warn("db2.unverified_layout",
                 f"{table_name} has no definition covering build "
                 f"{WOTLK_BUILD}, so the mapping's own field count "
                 f"({mapping.target_field_count}) is being used unchecked. "
                 f"Pass --template with your client's {table_name}.dbc, or "
                 f"update your DBDefs checkout")
    elif definition is not None and not template_data:
        # The definition knows the table and its Wrath history, and has no
        # layout for Wrath: the table did not exist then (none of the 951 such
        # tables in 12.1 is among a clean 3.3.5a client's 246).  The client
        # never reads it, so there is nothing to write -- that is a skip, not
        # a failure.  A template .dbc for it would contradict that, and is
        # still handled as an error below.
        res.status = Status.SKIPPED
        res.info("db2.not_in_wrath",
                 f"{table_name} did not exist in 3.3.5a: its definition has no "
                 f"layout for build {WOTLK_BUILD}, so the client has no such "
                 f"table and nothing is written")
        res.elapsed = time.time() - started
        return b"", res
    else:
        extra = ""
        if template_data:
            # A .dbc carries no column names, so it can confirm a width but
            # never supply a layout: every column would have to be matched by
            # position, which is how the old hardcoded tables went wrong.
            extra = (" A --template was given, but a .dbc records only the "
                     "number of columns, not their names, so it cannot say "
                     "what belongs in them.")
        res.fail("db2.no_layout",
                 f"nothing describes the 3.3.5a {table_name}: its definition "
                 f"has no layout for build {WOTLK_BUILD} (so the table "
                 f"probably did not exist in Wrath), and there is no mapping "
                 f"pinning its columns by index." + extra +
                 f" Update your DBDefs checkout, or write a mapping for "
                 f"{table_name} that gives each column an \"index\"")
        res.elapsed = time.time() - started
        return b"", res

    field_sizes = [f.size for f in target.fields]
    if target.narrow_fields:
        res.info("db2.field_widths",
                 f"{len(target.narrow_fields)} 3.3.5a column(s) are narrower "
                 f"than four bytes; records are {sum(field_sizes)} bytes",
                 record_size=sum(field_sizes))

    if mapping is None:
        # Nothing table-specific to say: both sides are named, so the columns
        # that kept their names map themselves.
        mapping = TableMapping(table=table_name, source="<auto>",
                               id_index=target.id_index)

    # -- template cross-check ---------------------------------------------
    template: DbcTable | None = None
    if template_data:
        template = DbcTable.parse(template_data, f"{table_name}.dbc",
                                  field_sizes=field_sizes)
        problem = cross_check(target, template.field_count, table_name)
        if problem:
            res.fail("db2.layout_mismatch", problem,
                     template_fields=template.field_count,
                     layout_fields=target.field_count)
            res.elapsed = time.time() - started
            return b"", res
        res.info("db2.template",
                 f"layout confirmed against {table_name}.dbc "
                 f"({template.field_count} fields, {len(template)} existing "
                 f"row(s))")

    field_count = target.field_count

    # -- columns ----------------------------------------------------------
    try:
        columns = resolve_columns(mapping, target, mapping.source)
    except ConversionError as exc:
        res.fail("db2.mapping_mismatch", str(exc))
        res.elapsed = time.time() - started
        return b"", res

    claimed = {c.index for c in columns if c.index is not None}
    auto = auto_map(target, parsed.columns, claimed)
    for match in auto:
        columns.append(ColumnMap(index=match.target.index,
                                 target=(match.target.name,),
                                 target_array_index=match.array_index,
                                 type=match.target.type,
                                 source=(match.source,),
                                 array_index=match.array_index))
    # An id that moves has to move everywhere it is referenced, including in
    # columns nobody had to write a mapping line for.
    shifts = {name.lower() for name in mapping.id_offset_columns}
    if shifts:
        columns = [dataclasses.replace(c, id_offset=True)
                   if any(t.lower() in shifts for t in c.target) else c
                   for c in columns]

    if auto:
        res.info("db2.auto_mapped",
                 f"{len(auto)} column(s) matched by name between the two "
                 f"builds; {len(claimed)} came from the mapping",
                 auto=len(auto), explicit=len(claimed))

    # A locstring's other locales stay empty and its mask is the one every
    # enUS table carries; neither is a column anyone could map.
    mapped = {c.index for c in columns}
    for field in target.fields:
        if field.role == "locale_flags" and field.index not in mapped:
            columns.append(ColumnMap(index=field.index, target=(field.name,),
                                     target_array_index=field.array_index,
                                     type="uint", const=LOCSTRING_FLAGS))
    unmapped = [f.label for f in target.fields
                if f.index not in {c.index for c in columns}
                and not f.conventional]
    if unmapped:
        res.lossy("db2.columns_unmapped",
                  f"{len(unmapped)} 3.3.5a column(s) have no source and were "
                  f"written as zero: " + ", ".join(unmapped[:10]),
                  columns=unmapped)

    absent = missing_sources(columns, parsed.column_names())
    if absent:
        res.lossy("db2.columns_absent",
                  f"{len(absent)} mapped column(s) do not exist in this build's "
                  f"{table_name} and were written as their defaults: "
                  + ", ".join(c.describe() for c in absent[:8]),
                  columns=[c.describe() for c in absent])

    # A few Wrath tables have no id column at all (CharBaseInfo is RaceID and
    # ClassID; PaperDollItemFrame is a name and a slot).  Keying their rows by
    # the first field collapsed every race to one row, so such a table is
    # keyed by the modern row id, and merging appends rather than matching.
    keyed = any(f.is_id for f in target.fields) or not target.named
    merge = bool(template) and opts.db_merge
    builder = DbcBuilder(field_count, template if merge else None,
                         field_sizes=field_sizes)
    if merge and keyed:
        builder.index_existing(mapping.id_index)
    existing_before = len(builder.records)

    if any(c.resolve for c in columns):
        if tables is None:
            res.fail("db2.tables_unavailable",
                     f"{table_name}'s columns are joined from other tables "
                     f"({', '.join(mapping.requires_tables) or 'see its mapping'}), "
                     f"and this conversion has no way to read them")
            res.elapsed = time.time() - started
            return b"", res
        absent_tables = tables.missing(list(mapping.requires_tables))
        if absent_tables:
            res.lossy("db2.tables_missing",
                      f"{len(absent_tables)} table(s) the joins need could not "
                      f"be read, so the columns built from them are empty: "
                      + ", ".join(absent_tables), tables=absent_tables)
    ctx = TransformContext(listfile, opts.path_prefix, tables)

    # -- rows -------------------------------------------------------------
    wanted_ids = set(opts.db_row_ids) if opts.db_row_ids else None
    where = opts.db_where
    added = replaced = 0
    for row_id, row in parsed:
        if wanted_ids is not None and row_id not in wanted_ids:
            continue
        if where and not _row_matches(row, where):
            continue
        values = apply_row(columns, row, ctx, opts.db_id_offset,
                           mapping.source)
        target_id = (values.get(mapping.id_index, ("uint", row_id))[1]
                     if keyed else row_id)
        if builder.add(values, int(target_id), mapping.id_index):
            added += 1
        else:
            replaced += 1

    if ctx.missing:
        sample = sorted(ctx.missing)[:8]
        res.lossy("db2.unresolved_files",
                  f"{len(ctx.missing)} FileDataID(s) referenced by this table "
                  f"are not in the listfile, so their paths came out empty "
                  f"(e.g. {', '.join(str(i) for i in sample)})",
                  count=len(ctx.missing))

    if added == 0 and replaced == 0:
        res.warn("db2.no_rows",
                 "no rows matched the selection, so the output only carries "
                 "whatever the template already had")

    out = builder.serialize()
    res.bytes_out = len(out)
    res.target_version = (f"DBC {field_count} fields, "
                          f"{len(builder.records)} row(s)")
    res.extra.update({
        "table": table_name,
        "source_rows": len(parsed.rows),
        "rows_added": added,
        "rows_replaced": replaced,
        "rows_kept": existing_before,
        "id_offset": opts.db_id_offset,
        "merged": merge,
        "layout": target.origin,
        "fields": field_count,
    })
    res.info("db2.converted",
             f"{added} row(s) added" + (f", {replaced} replaced" if replaced else "")
             + (f", {existing_before} kept from the template" if merge else ""))
    if res.status is Status.OK:
        res.status = Status.LOSSY if absent else Status.OK
    res.elapsed = time.time() - started
    return out, res
