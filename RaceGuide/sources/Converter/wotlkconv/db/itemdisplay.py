"""ItemDisplayInfo: joining a modern item display back into Wrath's one row.

Wrath's ItemDisplayInfo names everything itself -- model and texture file
names, eight armour texture components, an icon.  Modern builds keep none of
that on the row: models and textures are resource ids resolved through
ModelFileData/TextureFileData (with race, gender, class and position carried
by ComponentModelFileData/ComponentTextureFileData), the armour components
live in ItemDisplayInfoMaterialRes, and the icon belongs to an ItemAppearance.

Every rule here was measured against a clean 3.3.5a client's own
ItemDisplayInfo.dbc on the 36,438 display ids both builds share (12.1.0.69814):

====================  ==========================================  ==========
column                source                                      agreement
====================  ==========================================  ==========
ModelName[0/1]        ModelResourcesID -> ModelFileData            99.9 / 99.8%
ModelTexture[0/1]     ModelMaterialResourcesID -> TextureFileData  98.5 / 96.3%
Texture[0..7]         ItemDisplayInfoMaterialRes by section        99.2%
InventoryIcon[0]      lowest ItemAppearance -> DefaultIconFileData 80.1% [1]
SpellVisualID         ItemRangedDisplayInfo.CastSpellVisualID      100%
GroupSoundIndex       lowest item's ItemGroupSoundsID              70.1% [2]
HelmetGeosetVisID     HelmetGeosetVis                              100%
====================  ==========================================  ==========

[1] An icon belongs to an item, and several items share a display; no choice
    per display can beat 85.5%.  [2] Wrath items have since been relinked to
    other displays; the value itself agrees 98% on Wrath's own items.

A name in the table is only useful if the client finds a file by it, and the
client looks in fixed places with fixed spellings.  So this module also says
which converted files must additionally be written where, and under what name
-- :meth:`ItemDisplayResolver.asset_aliases` -- from the same functions that
produce the column values, so the two cannot drift apart:

* helmets: Wrath stores ``Helm_X`` and loads ``Helm_X_<race prefix><M|F>.m2``;
  modern files are often ``helm_x_hu_m.m2``;
* armour textures: Wrath stores ``<base>`` (with its ``_AU``/``_TL``.. section
  suffix) and loads ``<section>Texture\\<base>_<U|M|F>.blp``; modern names often
  carry a FileDataID suffix after the gender letter;
* model textures must sit beside the model, icons in ``Interface\\Icons``.
"""

from __future__ import annotations

import os
import re
from typing import Any

from ..listfile import Listfile
from .tables import TableProvider

#: Tables the joins read.
REQUIRED_TABLES = ["ModelFileData", "ComponentModelFileData", "TextureFileData",
                   "ComponentTextureFileData", "ItemDisplayInfoMaterialRes",
                   "ItemAppearance", "ItemModifiedAppearance", "Item",
                   "ItemRangedDisplayInfo", "ChrRaces", "ItemDisplayInfo"]

#: ``Item\ObjectComponents`` folders whose models 3.3.5a can attach.  Modern
#: ``collections``, ``waist`` and cape models have no Wrath counterpart.
MODEL_FOLDERS = {"head", "shoulder", "weapon", "shield", "quiver", "ammo", "pouch"}

#: ModelType values for models Wrath has no slot for (collections, bow
#: quivers, cape and belt models).
UNUSABLE_MODEL_TYPES = {1, 2, 3, 4}

#: ItemDisplayInfoMaterialRes.ComponentSection -> Wrath folder, in the order of
#: Wrath's Texture[0..7].  Section 8 (accessory) has no Wrath column.
SECTION_FOLDERS = ["armuppertexture", "armlowertexture", "handtexture",
                   "torsouppertexture", "torsolowertexture", "leguppertexture",
                   "leglowertexture", "foottexture"]

#: ComponentTextureFileData/ComponentModelFileData.GenderIndex -> suffix letter.
GENDER_LETTERS = {0: "m", 1: "f", 3: "u"}
_GENDER_PREFERENCE = {3: 0, 0: 1, 1: 2}

_RACE_SUFFIX = re.compile(r"^(.*)_([a-z]{2})_?([mf])$")
_FID_SUFFIX = re.compile(r"_\d{5,}$")
_GENDER_WITH_FID = re.compile(r"^(.*)_[muf]_(\d{5,})$")
_GENDER = re.compile(r"^(.*)_[muf]$")


def _stem(path: str) -> str:
    return os.path.splitext(path.replace("/", "\\").rsplit("\\", 1)[-1])[0]


def _folder(path: str) -> str:
    return path.replace("/", "\\").rsplit("\\", 1)[0] if "\\" in path.replace("/", "\\") else ""


def strip_gender(stem: str) -> str:
    """``foo_lu_u_4876585`` -> ``foo_lu_4876585``; ``foo_au_m`` -> ``foo_au``."""
    m = _GENDER_WITH_FID.match(stem)
    if m:
        return f"{m.group(1)}_{m.group(2)}"
    m = _GENDER.match(stem)
    return m.group(1) if m else stem


class ItemDisplayResolver:
    """Column values and asset placement for Wrath's ItemDisplayInfo."""

    def __init__(self, tables: TableProvider, listfile: Listfile):
        self.tables = tables
        self.listfile = listfile
        self._material_bases: dict[int, tuple[int, str]] | None = None
        self._race_prefixes: dict[int, str] | None = None

    # -- helpers ----------------------------------------------------------
    def _path(self, file_id: int) -> str | None:
        return self.listfile.path_for(int(file_id)) if file_id else None

    def _race_prefix(self, race_id: int) -> str:
        if self._race_prefixes is None:
            table = self.tables.get("ChrRaces")
            self._race_prefixes = {
                rid: str(row.get("ClientPrefix") or "").lower()
                for rid, row in (table.rows.items() if table else [])}
        return self._race_prefixes.get(int(race_id), "")

    def _model_files(self, resource: int) -> list[tuple[int, str, dict]]:
        """``(FileDataID, path, component row)`` for a model resource."""
        out = []
        for row in self.tables.index("ModelFileData", "ModelResourcesID").get(resource, []):
            file_id = int(row.get("FileDataID") or row["ID"])
            path = self._path(file_id)
            if not path:
                continue
            component = self.tables.row("ComponentModelFileData", file_id) or {}
            out.append((file_id, path, component))
        return sorted(out)

    def _texture_files(self, material: int) -> list[tuple[int, str, dict]]:
        out = []
        for row in self.tables.index("TextureFileData", "MaterialResourcesID").get(material, []):
            file_id = int(row.get("FileDataID") or row["ID"])
            path = self._path(file_id)
            if not path:
                continue
            component = self.tables.row("ComponentTextureFileData", file_id) or {}
            out.append((file_id, path, component))
        return sorted(out)

    # -- models -----------------------------------------------------------
    def _model(self, row: dict, index: int) -> tuple[str, list[tuple[int, str]]]:
        """``(name without extension, [(FileDataID, Wrath path)])`` for one slot."""
        resources = row.get("ModelResourcesID") or [0, 0]
        model_types = row.get("ModelType") or [0, 0]
        resource = int(resources[index]) if index < len(resources) else 0
        if not resource or (index < len(model_types)
                            and int(model_types[index]) in UNUSABLE_MODEL_TYPES):
            return "", []
        files = self._model_files(resource)
        if not files:
            return "", []
        folder = _folder(files[0][1])
        parts = folder.split("\\")
        if len(parts) < 3 or parts[0] != "item" or parts[1] != "objectcomponents" \
                or parts[2] not in MODEL_FOLDERS:
            return "", []

        positioned = [f for f in files if int(f[2].get("PositionIndex", -1)) == index]
        if positioned:
            return _stem(positioned[0][1]), []
        raced = [f for f in files if int(f[2].get("RaceID") or 0)]
        if raced:
            classless = [f for f in raced if not int(f[2].get("ClassID") or 0)] or raced
            m = _RACE_SUFFIX.match(_stem(classless[0][1]))
            base = m.group(1) if m else _stem(classless[0][1])
            aliases = []
            for file_id, _path, component in classless:
                prefix = self._race_prefix(int(component.get("RaceID") or 0))
                gender = {0: "m", 1: "f"}.get(int(component.get("GenderIndex", -1)))
                if prefix and gender:
                    aliases.append((file_id, f"{folder}\\{base}_{prefix}{gender}.m2"))
            return base, aliases
        return _stem(files[0][1]), []

    def model_name(self, row: dict, index: int) -> str:
        name, _ = self._model(row, index)
        return f"{name}.mdx" if name else ""

    def _model_folder(self, row: dict, index: int) -> str:
        resources = row.get("ModelResourcesID") or [0, 0]
        resource = int(resources[index]) if index < len(resources) else 0
        files = self._model_files(resource) if resource else []
        if files and self.model_name(row, index):
            return _folder(files[0][1])
        return "item\\objectcomponents\\cape"

    def _model_texture(self, row: dict, index: int) -> tuple[str, int, str]:
        materials = row.get("ModelMaterialResourcesID") or [0, 0]
        material = int(materials[index]) if index < len(materials) else 0
        files = self._texture_files(material) if material else []
        if not files:
            return "", 0, ""
        file_id, path, _ = files[0]
        return _stem(path), file_id, path

    def model_texture(self, row: dict, index: int) -> str:
        return self._model_texture(row, index)[0]

    # -- armour textures --------------------------------------------------
    def _material_base(self, material: int) -> tuple[int, str] | None:
        """``(section, Wrath base name)`` for a component material."""
        if self._material_bases is None:
            self._material_bases = {}
            claimed: dict[str, int] = {}
            by_display = self.tables.index("ItemDisplayInfoMaterialRes", "MaterialResourcesID")
            for mat, rows in sorted(by_display.items()):
                section = int(rows[0].get("ComponentSection", -1))
                if not 0 <= section < len(SECTION_FOLDERS):
                    continue
                chosen = self._choose_component(int(mat))
                if chosen is None:
                    continue
                base = strip_gender(_stem(chosen[1]))
                target = f"{SECTION_FOLDERS[section]}\\{base}"
                if claimed.get(target, mat) != mat:
                    base = f"{base}_{mat}"      # a genuinely different file
                claimed.setdefault(f"{SECTION_FOLDERS[section]}\\{base}", mat)
                self._material_bases[int(mat)] = (section, base)
        return self._material_bases.get(int(material))

    def _component_files(self, material: int) -> list[tuple[int, str, dict]]:
        return [f for f in self._texture_files(material)
                if not int(f[2].get("RaceID") or 0) and not int(f[2].get("ClassID") or 0)]

    def _choose_component(self, material: int) -> tuple[int, str, dict] | None:
        files = self._component_files(material)
        if not files:
            return None
        return min(files, key=lambda f: (bool(_FID_SUFFIX.search(_stem(f[1]))),
                                         _GENDER_PREFERENCE.get(int(f[2].get("GenderIndex", 9)), 9),
                                         f[0]))

    def texture(self, row: dict, section: int) -> str:
        for res in self.tables.index("ItemDisplayInfoMaterialRes", "ItemDisplayInfoID").get(
                int(row["ID"]), []):
            if int(res.get("ComponentSection", -1)) == section:
                found = self._material_base(int(res["MaterialResourcesID"]))
                return found[1] if found else ""
        return ""

    # -- icon, sounds, visuals ---------------------------------------------
    def _appearances(self, row: dict) -> list[dict]:
        return sorted(self.tables.index("ItemAppearance", "ItemDisplayInfoID").get(
            int(row["ID"]), []), key=lambda a: a["ID"])

    def _icon(self, row: dict) -> tuple[str, int, str]:
        for appearance in self._appearances(row):
            file_id = int(appearance.get("DefaultIconFileDataID") or 0)
            path = self._path(file_id)
            if path:
                return _stem(path), file_id, path
        return "", 0, ""

    def icon(self, row: dict) -> str:
        return self._icon(row)[0]

    def spell_visual(self, row: dict) -> int:
        ranged = self.tables.row("ItemRangedDisplayInfo",
                                 int(row.get("ItemRangedDisplayInfoID") or 0))
        return int(ranged.get("CastSpellVisualID") or 0) if ranged else 0

    def group_sound(self, row: dict) -> int:
        items = []
        by_appearance = self.tables.index("ItemModifiedAppearance", "ItemAppearanceID")
        for appearance in self._appearances(row):
            items += [int(m["ItemID"]) for m in by_appearance.get(appearance["ID"], [])]
        for item_id in sorted(items):
            item = self.tables.row("Item", item_id)
            if item is not None:
                value = int(item.get("ItemGroupSoundsID") or 0)
                return value if 1 <= value <= 24 else 0
        return 0

    # -- files ------------------------------------------------------------
    def asset_aliases(self) -> dict[int, set[str]]:
        """FileDataID -> extra paths (under the patch root) the client loads it by."""
        aliases: dict[int, set[str]] = {}

        def add(file_id: int, path: str, current: str | None) -> None:
            path = path.lower()
            if current and path == current.lower():
                return
            aliases.setdefault(int(file_id), set()).add(path)

        table = self.tables.get("ItemDisplayInfo")
        for row_id, row in (table.rows.items() if table else []):
            row = {**row, "ID": row_id}
            for index in (0, 1):
                for file_id, path in self._model(row, index)[1]:
                    add(file_id, path, self._path(file_id))
                name, file_id, path = self._model_texture(row, index)
                if name:
                    add(file_id, f"{self._model_folder(row, index)}\\{name}.blp", path)
            name, file_id, path = self._icon(row)
            if name:
                add(file_id, f"interface\\icons\\{name}.blp", path)
        for material in self.tables.index("ItemDisplayInfoMaterialRes", "MaterialResourcesID"):
            found = self._material_base(int(material))
            if found is None:
                continue
            section, base = found
            for file_id, path, component in self._component_files(int(material)):
                letter = GENDER_LETTERS.get(int(component.get("GenderIndex", -1)))
                if letter:
                    add(file_id, f"item\\texturecomponents\\{SECTION_FOLDERS[section]}\\"
                                 f"{base}_{letter}.blp", path)
        return aliases


def resolver_for(ctx: Any) -> ItemDisplayResolver:
    """The per-conversion resolver, created on first use."""
    cache = ctx.cache
    if "itemdisplay" not in cache:
        if ctx.tables is None:
            raise LookupError("ItemDisplayInfo joins need other tables, and "
                              "none are available to this conversion")
        cache["itemdisplay"] = ItemDisplayResolver(ctx.tables, ctx.listfile)
    return cache["itemdisplay"]


RESOLVERS = {
    "itemdisplay.model": lambda row, ctx, index=0: resolver_for(ctx).model_name(row, index),
    "itemdisplay.model_texture": lambda row, ctx, index=0: resolver_for(ctx).model_texture(row, index),
    "itemdisplay.texture": lambda row, ctx, section=0: resolver_for(ctx).texture(row, section),
    "itemdisplay.icon": lambda row, ctx: resolver_for(ctx).icon(row),
    "itemdisplay.spell_visual": lambda row, ctx: resolver_for(ctx).spell_visual(row),
    "itemdisplay.group_sound": lambda row, ctx: resolver_for(ctx).group_sound(row),
}
