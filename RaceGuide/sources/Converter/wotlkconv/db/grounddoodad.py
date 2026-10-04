"""Ground clutter: the grass and pebbles GroundEffectDoodad names.

3.3.5a's ``GroundEffectDoodad.Doodadpath`` is a bare file name such as
``ElwFlo01.mdl``, which the client loads from ``World\\NoDXT\\Detail\\``.
Retail names the model by FileDataID instead, and most of those models still
sit in that folder -- but a few hundred have moved elsewhere
(``models\\world\\nodxt\\detail``, expansion doodad folders).  Those get a copy
in ``world\\nodxt\\detail`` under their own name, or under their name plus
their FileDataID when a different model already has that name, and the table
points at the copy.
"""

from __future__ import annotations

from typing import Any

from ..listfile import Listfile

DETAIL_FOLDER = "world\\nodxt\\detail\\"


class GroundDoodadNames:
    """Doodadpath for every GroundEffectDoodad row, and the copies it needs."""

    def __init__(self, tables, listfile: Listfile):
        self.names: dict[int, str] = {}
        #: FileDataID -> the path under the detail folder it is copied to.
        self.copies: dict[int, str] = {}
        table = tables.get("GroundEffectDoodad")
        if table is None:
            return
        taken: dict[str, int] = {}
        for fid, path in listfile:
            if path.startswith(DETAIL_FOLDER) and path.endswith(".m2"):
                taken[path[len(DETAIL_FOLDER):-3]] = fid
        for row_id in sorted(table.rows):
            file_id = int(table.rows[row_id].get("ModelFileID") or 0)
            path = listfile.path_for(file_id) if file_id else None
            if not path or not path.endswith(".m2"):
                self.names[row_id] = ""
                continue
            if path.startswith(DETAIL_FOLDER):
                self.names[row_id] = path[len(DETAIL_FOLDER):-3] + ".mdl"
                continue
            stem = path.rsplit("\\", 1)[-1][:-3]
            if taken.get(stem, file_id) != file_id:
                stem = f"{stem}_{file_id}"
            taken[stem] = file_id
            self.copies[file_id] = f"{DETAIL_FOLDER}{stem}.m2"
            self.names[row_id] = f"{stem}.mdl"

    def aliases(self) -> dict[int, set[str]]:
        return {fid: {path} for fid, path in self.copies.items()}


def names_for(ctx: Any) -> GroundDoodadNames:
    if "grounddoodad" not in ctx.cache:
        if ctx.tables is None:
            raise LookupError("GroundEffectDoodad paths need the table itself, "
                              "and no tables are available to this conversion")
        ctx.cache["grounddoodad"] = GroundDoodadNames(ctx.tables, ctx.listfile)
    return ctx.cache["grounddoodad"]


RESOLVERS = {
    "grounddoodad.path": lambda row, ctx: names_for(ctx).names.get(int(row["ID"]), ""),
}
