"""Port a custom race from G:\\Eunoia\\Client into the Esteria dev client.

Everything is written into a new Patch-D.MPQ, so reverting is "delete the file".

Per race it stages:
  * male/female .m2 and their four .skin LODs, renamed to the path the server
    SQL already expects
  * every texture the donor's CharSections rows reference, plus the model's own
    hardcoded textures
  * client DBC rows: ChrRaces, CreatureModelData, CreatureDisplayInfo,
    CharSections, CharHairGeosets, CharBaseInfo
  * CharacterCreate.lua entries for the race icon
"""

from __future__ import annotations

import ctypes as c
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / ".agents/plans/vulpera-pandaren-playable-races"))

from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc  # noqa: E402
from mpq_hash_probe import lookup, read_hash_map  # noqa: E402

CLIENT_DATA = REPO / "3.3.5a - Dev/Data"
PATCH_D = CLIENT_DATA / "Patch-D.MPQ"
PATCH_E = CLIENT_DATA / "Patch-E.MPQ"
PATCH_G = CLIENT_DATA / "Patch-G.MPQ"
PATCH_Y = CLIENT_DATA / "Patch-Y.MPQ"
EUNOIA_DATA = Path(r"G:\Eunoia\Client\data")
EUNOIA_DBC = REPO / ".agents/plans/vulpera-pandaren-playable-races/eunoia-dbc"
OUT = REPO / ".agents/plans/races-9-port"
MPQ_OPEN_READ_ONLY = 0x00000100
MPQ_COMPRESSION_ZLIB = 0x00000002
# External .anim files are loaded during model init; a mismatched set makes the
# client drop the model (placeholder cube), so they stay opt-in.
STAGE_ANIMS = False
FLAVOUR = {
    "EREDAR": "Eredar are the ancient, fel-touched draenei who wield immense arcane and demonic power.",
    "NIGHTBORNE": "Nightborne are the children of Suramar, steeped in the Nightwell and its arcane gifts.",
    "VOIDELF": "Void elves channel the shadow between the stars, wielding entropy as a weapon.",
    "LIGHTFORGEDDRAENEI": "Lightforged draenei are infused with the Light, forged to wage the eternal war against the Legion.",
    "ZANDALARITROLL": "Zandalari trolls are the proud, ancient forebears of all trollkind, blessed by their loa.",
    "DARKIRONDWARF": "Dark Iron dwarves are born of the fire beneath Blackrock, hardened and fiercely independent.",
    "DRACTHYR": "Dracthyr are ancient draconic soldiers, wielding the magic of all five dragonflights.",
    "KULTIRAN": "Kul Tirans are the hardy seafarers of Boralus, steeped in the tides and old ways of Drustvar.",
    "ILLIDARI": "Illidari are demon hunters who bound themselves to fel power to hunt the Burning Legion.",
}


def decode_blp(data: bytes) -> Image.Image:
    """Decode a BLP2 icon (DXT5 or raw BGRA) into an RGBA image."""
    if data[:4] != b"BLP2":
        raise ValueError("not a BLP2 file")
    compression = data[8]
    width, height = struct.unpack_from("<II", data, 12)
    offset, size = struct.unpack_from("<II", data, 20)[0], struct.unpack_from("<II", data, 84)[0]
    payload = data[offset : offset + size]
    if compression == 3:
        array = np.frombuffer(payload, dtype=np.uint8).reshape(height, width, 4)
        return Image.fromarray(array[:, :, [2, 1, 0, 3]], "RGBA")
    if compression != 2:
        raise ValueError(f"unsupported BLP compression {compression}")
    out = np.zeros((height, width, 4), dtype=np.uint8)
    pos = 0
    for by in range(0, height, 4):
        for bx in range(0, width, 4):
            a0, a1 = payload[pos], payload[pos + 1]
            alpha_bits = int.from_bytes(payload[pos + 2 : pos + 8], "little")
            pos += 8
            c0, c1 = struct.unpack_from("<HH", payload, pos)
            color_bits = int.from_bytes(payload[pos + 4 : pos + 8], "little")
            pos += 8
            alphas = [a0, a1]
            if a0 > a1:
                alphas += [int(((7 - i) * a0 + i * a1) / 7) for i in range(1, 7)]
            else:
                alphas += [int(((5 - i) * a0 + i * a1) / 5) for i in range(1, 5)] + [0, 255]
            colors = []
            for value in (c0, c1):
                r, g, b = (value >> 11) & 0x1F, (value >> 5) & 0x3F, value & 0x1F
                colors.append(((r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2)))
            if c0 > c1:
                colors.append(tuple((2 * colors[0][i] + colors[1][i]) // 3 for i in range(3)))
                colors.append(tuple((colors[0][i] + 2 * colors[1][i]) // 3 for i in range(3)))
            else:
                colors.append(tuple((colors[0][i] + colors[1][i]) // 2 for i in range(3)))
                colors.append((0, 0, 0))
            for py in range(4):
                for px in range(4):
                    index = py * 4 + px
                    alpha = alphas[(alpha_bits >> (3 * index)) & 7]
                    red, green, blue = colors[(color_bits >> (2 * index)) & 3]
                    out[by + py, bx + px] = (red, green, blue, alpha)
    return Image.fromarray(out, "RGBA")


def encode_blp2_bgra(image: Image.Image) -> bytes:
    """Write the uncompressed BLP2 layout the client renders (comp=3, full mip chain)."""
    width, height = image.size
    mips: list[bytes] = []
    current = image
    while True:
        array = np.array(current.convert("RGBA"))
        mips.append(array[:, :, [2, 1, 0, 3]].tobytes())
        if current.width == 1 and current.height == 1:
            break
        current = current.resize((max(1, current.width // 2), max(1, current.height // 2)), Image.BOX)
    header = bytearray(148)
    header[0:4] = b"BLP2"
    struct.pack_into("<I", header, 4, 1)
    header[8], header[9], header[10], header[11] = 3, 8, 8, 1
    struct.pack_into("<II", header, 12, width, height)
    offset = 148 + 1024
    for index, mip in enumerate(mips[:16]):
        struct.pack_into("<I", header, 20 + 4 * index, offset)
        struct.pack_into("<I", header, 84 + 4 * index, len(mip))
        offset += len(mip)
    return bytes(header) + bytes(1024) + b"".join(mips)

# One entry per target race. display ids match mod-custom-server race_models SQL.
RACES = [
    {
        "key": "eredar",
        "race_id": 16,
        "eunoia_race": 16,
        "name": "Eredar",
        "prefix": "Er",
        "client_file": "Eredar",
        "male": ("Character\\eredar\\Male\\Race_EredarMale", "Character\\Eredar\\Male\\EredarMale", 60008, 3632),
        "female": ("Character\\eredar\\Female\\Race_EredarFemale", "Character\\Eredar\\Female\\EredarFemale", 60009, 3633),
        "icon": (r"Interface\Glues\CharacterCreate\UI-CharacterCreate-Draenei", None),
        "display_pair": (2, 3),
        "outfit_template": 11,
    },
    {
        "key": "nightborne",
        "race_id": 17,
        "eunoia_race": 13,
        "name": "Nightborne",
        "prefix": "Nb",
        "client_file": "Nightborne",
        "male": ("character\\nightborne\\male\\nightbornemale", "Character\\Nightborne\\Male\\NightborneMale", 60010, 3634),
        "female": ("character\\nightborne\\female\\nightbornefemale", "Character\\Nightborne\\Female\\NightborneFemale", 60011, 3635),
        "icon": (r"Interface\Glues\CharacterCreate\UI-CharacterCreate-Nightborne", "nightborne"),
        "display_pair": (33070, 32902),
        "outfit_template": 4,
    },
    {
        "key": "voidelf",
        "race_id": 19,
        "eunoia_race": 15,
        "name": "Void Elf",
        "prefix": "Ve",
        "client_file": "VoidElf",
        "male": ("character\\voidelf\\male\\voidelfmale", "Character\\Voidelf\\Male\\VoidelfMale", 60012, 3638),
        "female": ("character\\voidelf\\female\\voidelffemale", "Character\\Voidelf\\Female\\VoidelfFemale", 60013, 3639),
        "icon": (r"Interface\Glues\CharacterCreate\UI-CharacterCreate-VoidElf", "voidelf"),
        "display_pair": (33174, 1),
        "outfit_template": 10,
    },
    {
        "key": "lightforged",
        "race_id": 21,
        "eunoia_race": 20,
        "name": "Lightforged Draenei",
        "prefix": "Lf",
        "client_file": "LightforgedDraenei",
        "male": ("character\\lightforgeddraenei\\male\\lightforgeddraeneimale", "Character\\lightforgeddraenei\\male\\lightforgeddraeneimale", 60014, 3642),
        "female": ("character\\lightforgeddraenei\\female\\lightforgeddraeneifemale", "Character\\lightforgeddraenei\\female\\lightforgeddraeneifemale", 60015, 3643),
        "icon": (r"Interface\Glues\CharacterCreate\UI-CharacterCreate-Lightforged", "lightforged"),
        "display_pair": (32, 34),
        "outfit_template": 11,
    },
    {
        "key": "zandalari",
        "race_id": 22,
        "eunoia_race": 18,
        "name": "Zandalari Troll",
        "prefix": "Za",
        "client_file": "ZandalariTroll",
        "male": ("character\\zandalaritroll\\male\\zandalaritrollmale", "Character\\zandalaritroll\\male\\zandalaritrollmale", 60016, 3644),
        "female": ("character\\zandalaritroll\\female\\zandalaritrollfemale", "Character\\zandalaritroll\\female\\zandalaritrollfemale", 60017, 3645),
        "icon": (r"Interface\Glues\CharacterCreate\UI-CharacterCreate-Zandalari", "zandalari"),
        "display_pair": (28, 29),
        "outfit_template": 8,
        "patch": "e",
    },
    {
        "key": "darkiron",
        "race_id": 23,
        "eunoia_race": 29,
        "name": "Dark Iron Dwarf",
        "prefix": "Di",
        "client_file": "DarkIronDwarf",
        "male": ("character\\darkirondwarf\\male\\darkirondwarfmale", "Character\\Darkirondwarf\\male\\darkirondwarfMale", 60018, 3646),
        "female": ("character\\darkirondwarf\\female\\darkirondwarffemale", "Character\\Darkirondwarf\\female\\darkirondwarfFemale", 60019, 3647),
        "icon": (r"Interface\Glues\CharacterCreate\UI-CharacterCreate-DarkIron", "darkirondwarf"),
        "display_pair": (27298, 14754),
        "outfit_template": 3,
        "patch": "e",
    },
    {
        "key": "dracthyr",
        "race_id": 28,
        "eunoia_race": 17,
        "name": "Dracthyr",
        "prefix": "Dr",
        "client_file": "Dracthyr",
        "male": ("character\\dracthyr\\male\\dracthyrmale", "Character\\Dracthyr\\Male\\DracthyrMale", 60020, 3652),
        "female": ("character\\dracthyr\\female\\dracthyrfemale", "Character\\Dracthyr\\Female\\DracthyrFemale", 60021, 3653),
        "icon": (r"Interface\Glues\CharacterCreate\UI-CharacterCreate-Dracthyr", "dracthyr"),
        "display_pair": (5, 6),
        "outfit_template": 1,
        "patch": "e",
    },
    {
        "key": "kultiran",
        "race_id": 29,
        "eunoia_race": 31,
        "name": "Kul Tiran",
        "prefix": "Kt",
        "client_file": "KulTiran",
        "male": ("CHARACTER\\Naga_\\male\\kultiranmale", "CHARACTER\\Naga_\\male\\kultiranmale", 60022, 3654),
        "female": ("CHARACTER\\Naga_\\Female\\kultiranfemale", "CHARACTER\\Naga_\\Female\\kultiranfemale", 60023, 3655),
        "icon": (r"Interface\Glues\CharacterCreate\UI-CharacterCreate-KulTiran", "kultiran"),
        "display_pair": (37, 41),
        "outfit_template": 3,
        "chrraces_template": 11,
        "model_templates": (3632, 3633),
        "display_templates": (90002, 90003),
        "patch": "g",
        "flags": 12,
        "faction": 1,
        "alliance": 0,
        "language": 7,
    },
    {
        "key": "illidari",
        "race_id": 30,
        "eunoia_race": 27,
        "name": "Illidari",
        "prefix": "Il",
        "client_file": "Illidari",
        "male": ("Character\\BloodElf_Dh\\Male\\BloodElfMale_DH", "Character\\BloodElf_Dh\\Male\\BloodElfMale_DH", 60024, 3656),
        "female": ("Character\\BloodElf_Dh\\Female\\BloodElfFemale_DH", "Character\\BloodElf_Dh\\Female\\BloodElfFemale_DH", 60025, 3657),
        "icon": (r"Interface\Glues\CharacterCreate\UI-CharacterCreate-BloodElf", None),
        "display_pair": (12, 24),
        "outfit_template": 10,
        "chrraces_template": 10,
        "model_templates": (3638, 3639),
        "display_templates": (90008, 90009),
        "patch": "g",
        "flags": 12,
        "faction": 2,
        "alliance": 1,
        "language": 1,
    },
]


class Source:
    """Read-only access to the donor client, searching its archives by priority."""

    def __init__(self) -> None:
        self.storm = Storm(DLL_DEFAULT)
        self.handles: dict[str, object] = {}

    def handle(self, name: str):
        if name not in self.handles:
            h = H()
            if not self.storm.dll.SFileOpenArchive(str(EUNOIA_DATA / name), 0, MPQ_OPEN_READ_ONLY, c.byref(h)):
                raise OSError(f"open {name} failed ({c.get_last_error()})")
            self.handles[name] = h
        return self.handles[name]

    def read(self, name: str) -> bytes | None:
        for archive in ("Patch-5.mpq", "Patch-4.mpq", "Patch-9.mpq", "Patch-8.mpq", "patch-I.mpq", "Patch-6.mpq", "Patch-7.mpq"):
            try:
                return self.storm.read(self.handle(archive), name)
            except Exception:  # noqa: BLE001
                continue
        return None

    def close(self) -> None:
        for handle in self.handles.values():
            self.storm.dll.SFileCloseArchive(handle)
        self.handles.clear()


class PatchWriter:
    """Incremental Patch-D.MPQ writer (create once, stream entries in)."""

    def __init__(self, path: Path, capacity: int) -> None:
        self.storm = Storm(DLL_DEFAULT)
        self.handle = H()
        flags = 0x00000001 | 0x00000002
        if not self.storm.dll.SFileCreateArchive(str(path), flags, capacity + 16, c.byref(self.handle)):
            raise OSError(f"create archive failed ({c.get_last_error()})")

    def add(self, name: str, payload: bytes) -> None:
        file_handle = H()
        if not self.storm.dll.SFileCreateFile(self.handle, name.encode("ascii"), 0, len(payload), 0, 0, c.byref(file_handle)):
            raise OSError(f"create {name} failed ({c.get_last_error()})")
        try:
            buffer = c.create_string_buffer(payload or b"\0")
            if not self.storm.dll.SFileWriteFile(file_handle, buffer, len(payload), MPQ_COMPRESSION_ZLIB):
                raise OSError(f"write {name} failed ({c.get_last_error()})")
        finally:
            self.storm.dll.SFileCloseFile(file_handle)

    def close(self) -> None:
        self.storm.dll.SFileCloseArchive(self.handle)


def load_client_dbc(name: str, storm: Storm) -> bytes:
    """Highest-priority version of a client DBC (later patch name wins)."""
    found: list[tuple[str, bytes]] = []
    own = {"patch-d.mpq", "patch-e.mpq", "patch-g.mpq", "patch-y.mpq", "patch-zz.mpq"}
    for path in sorted(CLIENT_DATA.glob("*.mpq")) + sorted(CLIENT_DATA.glob("*.MPQ")):
        if path.name.casefold() in own:
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, MPQ_OPEN_READ_ONLY, c.byref(handle)):
            continue
        try:
            payload = storm.read(handle, name)
            found.append((path.name, payload))
        except Exception:  # noqa: BLE001
            pass
        finally:
            storm.dll.SFileCloseArchive(handle)
    if not found:
        raise FileNotFoundError(name)
    found.sort(key=lambda item: item[0].casefold())
    return found[-1][1]


def dbc_rows_with_pool(data: bytes) -> tuple[list[list[int]], int, int, int, bytearray]:
    dbc = Wdbc(data)
    return [row[:] for row in dbc.rows], dbc.fields, dbc.record_size, dbc.count, bytearray(dbc.strings)


def dbc_from(rows: list[list[int]], fields: int, pool: bytearray) -> bytes:
    body = b"".join(struct.pack(f"<{fields}I", *(value & 0xFFFFFFFF for value in row)) for row in rows)
    return struct.pack("<4s4I", b"WDBC", len(rows), fields, fields * 4, len(pool)) + body + bytes(pool)


def pool_add(pool: bytearray, value: str) -> int:
    offset = len(pool)
    pool.extend(value.encode("utf-8") + b"\0")
    return offset


def retag_geoset(skin: bytes, from_id: int, to_id: int) -> bytes:
    """Move submeshes between geoset ids (see retag_voidelf_ears.py)."""
    vals = struct.unpack_from("<10I", skin, 4)
    n_sub, ofs_sub = vals[6], vals[7]
    out = bytearray(skin)
    for index in range(n_sub):
        offset = ofs_sub + index * 48
        if struct.unpack_from("<H", skin, offset)[0] == from_id:
            struct.pack_into("<H", out, offset, to_id)
    return bytes(out)


def sql_rows(path: Path, table: str) -> dict[int, list[object]]:
    """Parse `(id, 12, 'text', NULL, ...)` tuples out of a mod SQL update file."""
    text = path.read_text(encoding="utf-8", errors="replace")
    matches = list(re.finditer(r"INSERT\s+INTO\s+`?" + re.escape(table) + r"`?", text, re.I))
    if not matches:
        raise SystemExit(f"no INSERT INTO {table} in {path.name}")
    start = matches[-1].end()
    stop = text.find(";", start)
    text = text[start: stop if stop > 0 else len(text)]
    rows: dict[int, list[object]] = {}
    for match in re.finditer(r"\(\s*(\d+)\s*,", text):
        start = match.start() + 1
        depth = 0
        index = start
        while index < len(text):
            char = text[index]
            if char == "'":
                index += 1
                while index < len(text) and text[index] != "'":
                    index += 1
            elif char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    break
                depth -= 1
            index += 1
        body = text[start:index]
        values: list[object] = []
        for token in re.findall(r"'[^']*'|[^,]+", body):
            token = token.strip()
            if not token:
                continue
            if token.startswith("'"):
                values.append(token[1:-1].replace("\\\\", "\\"))
            elif token.upper() == "NULL":
                values.append(None)
            else:
                try:
                    values.append(int(token))
                except ValueError:
                    try:
                        values.append(float(token))
                    except ValueError:
                        values.append(None)
        if values:
            rows[int(values[0])] = values
    return rows


MODEL_FLOAT_FIELDS = {4, 7, 8, 9, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27}
DISPLAY_FLOAT_FIELDS = {4}


def row_to_ints(values: list[object], pool: bytearray, floats: set[int] | None = None) -> list[int]:
    floats = floats or set()
    row: list[int] = []
    for index, value in enumerate(values):
        if isinstance(value, str):
            row.append(pool_add(pool, value))
        elif index in floats and value is not None:
            row.append(struct.unpack("<I", struct.pack("<f", float(value)))[0])
        else:
            row.append(0 if value is None else int(value) & 0xFFFFFFFF)
    return row


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    storm = Storm(DLL_DEFAULT)
    source = Source()
    eunoia_sections = Wdbc((EUNOIA_DBC / "CharSections.dbc").read_bytes())
    eunoia_geosets = Wdbc((EUNOIA_DBC / "CharHairGeosets.dbc").read_bytes())
    sql_root = REPO / "modules/mod-custom-server/data/sql/db-world/updates"
    server_chrraces = sql_rows(sql_root / "dbc/chrraces_dbc.sql", "chrraces_dbc")
    pending = REPO / "modules/mod-custom-server/data/sql/updates/pending_db_world/rev_1787850000002_race_models.sql"
    server_models = sql_rows(pending, "creaturemodeldata_dbc")
    server_displays = sql_rows(pending, "creaturedisplayinfo_dbc")
    newer = REPO / "modules/mod-custom-server/data/sql/updates/pending_db_world/rev_1787850000003_races_29_30.sql"
    server_chrraces.update(sql_rows(newer, "chrraces_dbc"))
    server_models.update(sql_rows(newer, "creaturemodeldata_dbc"))
    server_displays.update(sql_rows(newer, "creaturedisplayinfo_dbc"))

    report: dict[str, dict] = {}
    seen: set[str] = set()
    anim_tables = []
    for archive in sorted(EUNOIA_DATA.glob("*.mpq")):
        try:
            anim_tables.append(read_hash_map(archive)[0])
        except Exception:  # noqa: BLE001
            continue
    writers: dict[str, PatchWriter | None] = {}
    patch_paths = {"d": PATCH_D, "e": PATCH_E, "g": PATCH_G, "y": PATCH_Y}
    active = {"key": "d"}

    def stage(name: str, payload: bytes) -> None:
        key = name.casefold()
        if key in seen:
            return
        seen.add(key)
        target = active["key"]
        if target not in writers:
            path = patch_paths[target]
            if path.exists():
                path.unlink()
            writers[target] = PatchWriter(path, 20000)
        writer = writers[target]
        if writer is None:
            return
        writer.add(name, payload)

    # ---- client DBCs (loaded once, merged per race) -----------------------
    chrraces_rows, chrraces_fields, _record, _count, chrraces_pool = dbc_rows_with_pool(
        load_client_dbc("DBFilesClient\\ChrRaces.dbc", storm)
    )
    sections_rows, sections_fields, _r, _c, sections_pool = dbc_rows_with_pool(
        load_client_dbc("DBFilesClient\\CharSections.dbc", storm)
    )
    geosets_rows, geosets_fields, _r, _c, geosets_pool = dbc_rows_with_pool(
        load_client_dbc("DBFilesClient\\CharHairGeosets.dbc", storm)
    )
    modeldata_rows, modeldata_fields, _r, _c, modeldata_pool = dbc_rows_with_pool(
        load_client_dbc("DBFilesClient\\CreatureModelData.dbc", storm)
    )
    display_rows, display_fields, _r, _c, display_pool = dbc_rows_with_pool(
        load_client_dbc("DBFilesClient\\CreatureDisplayInfo.dbc", storm)
    )
    sections_next_id = max(row[0] for row in sections_rows) + 1
    geosets_next_id = max(row[0] for row in geosets_rows) + 1
    modeldata_ids = {row[0] for row in modeldata_rows}
    display_ids = {row[0] for row in display_rows}
    # Vulpera/Pandaren rows are known-good in this client: clone their shape so the
    # new races get character-model flags and a plain (non-creature) display row.
    client_model_template = {
        "male": next(row for row in modeldata_rows if row[0] == 112885),
        "female": next(row for row in modeldata_rows if row[0] == 112886),
    }
    client_display_template = {
        "male": next(row for row in display_rows if row[0] == 141254),
        "female": next(row for row in display_rows if row[0] == 141255),
    }
    vulpera_row = next(row for row in chrraces_rows if row[0] == 20)

    for spec in RACES:
        active["key"] = spec.get("patch", "d")
        race_id = spec["race_id"]
        donor_id = spec["eunoia_race"]
        entry: dict[str, object] = {"race": spec["name"], "race_id": race_id, "art": 0, "skins": 0, "missing": []}

        # ---- art ---------------------------------------------------------
        for gender, (source_stem, target_stem, _display, _model) in (("male", spec["male"]), ("female", spec["female"])):
            model = source.read(source_stem + ".mdx") or source.read(source_stem + ".m2")
            if model is None:
                entry["missing"].append(source_stem)
                continue
            entry.setdefault("target_paths", {})[gender] = target_stem + ".mdx"
            stage(target_stem + ".mdx", model)
            stage(target_stem + ".m2", model)
            entry["art"] = int(entry["art"]) + 1
            for index in range(4):
                skin = source.read(f"{source_stem}0{index}.skin")
                if skin is None:
                    entry["missing"].append(f"{source_stem}0{index}.skin")
                    continue
                if spec["key"] == "voidelf":
                    # the client only draws group-7 variant 0, so the ears
                    # (702 in every LOD) have to ride on it
                    skin = retag_geoset(skin, 702, 7)
                stage(f"{target_stem}0{index}.skin", skin)
                entry["skins"] = int(entry["skins"]) + 1
            # hardcoded textures inside the model
            texture_count, texture_offset = struct.unpack_from("<II", model, 0x50)
            for index in range(texture_count):
                ttype, _flags, fcount, foffset = struct.unpack_from("<IIII", model, texture_offset + index * 16)
                if ttype or not fcount:
                    continue
                name = model[foffset:foffset + fcount].split(b"\x00")[0].decode("ascii", "replace")
                payload = source.read(name)
                if payload:
                    stage(name, payload)

        # textures referenced by their CharSections rows
        texture_names = sorted(
            {
                eunoia_sections.text(row[field])
                for row in eunoia_sections.rows
                if row[1] == donor_id
                for field in (4, 5, 6)
                if eunoia_sections.text(row[field])
            }
        )
        for name in texture_names:
            payload = source.read(name)
            if payload is None and not name.lower().endswith(".blp"):
                payload = source.read(name + ".blp")
            if payload is None:
                entry["missing"].append(name)
                continue
            stage(name, payload)
        entry["textures"] = len(texture_names) - len([m for m in entry["missing"]])

        report[spec["key"]] = entry

        # ---- ChrRaces row (mirror the server row, keep our display ids) ----
        server_row = server_chrraces.get(race_id)
        if server_row is None:
            template_id = spec.get("chrraces_template")
            server_row = next((list(row) for row in chrraces_rows if row[0] == template_id), None)
            if server_row is None:
                raise SystemExit(f"no ChrRaces row or template for race {race_id}")
        values = list(server_row)
        values[0] = race_id
        # adopt the engine-facing fields from the race that provably renders in this
        # client (Vulpera): flags, sounds, cinematic, customisation strings
        for field in (1, 3, 7, 8, 9, 10, 12, 13, 62, 63, 64, 65, 66, 67, 68):
            if field < len(values) and field < len(vulpera_row):
                values[field] = vulpera_row[field]
        for field, key in ((1, "flags"), (2, "faction"), (7, "language"), (13, "alliance")):
            if key in spec:
                values[field] = spec[key]
        values[4] = spec["male"][2]
        values[5] = spec["female"][2]
        values[6] = spec["prefix"]
        values[11] = spec["client_file"]
        # custom-race rows in this client fill every locale slot (the shipped DBCs
        # have shifted locale columns, so an empty slot reads as a nil name)
        for start in (14, 30, 46):
            for index in range(start, start + 16):
                if index < len(values):
                    values[index] = spec["name"]
        new_row = row_to_ints(values, chrraces_pool)
        for index, row in enumerate(chrraces_rows):
            if row[0] == race_id:
                chrraces_rows[index] = new_row
                break
        else:
            chrraces_rows.append(new_row)

        # ---- CreatureModelData + CreatureDisplayInfo ----------------------
        for index, (gender, display_id, model_id) in enumerate(
            (
                ("male", spec["male"][2], spec["male"][3]),
                ("female", spec["female"][2], spec["female"][3]),
            )
        ):
            target_path = entry.get("target_paths", {}).get(gender)
            if model_id not in modeldata_ids and target_path:
                row = list(client_model_template[gender])
                row[0] = model_id
                # custom races in this client are referenced with a literal .m2 path
                row[2] = pool_add(modeldata_pool, target_path.replace(".mdx", ".m2"))
                modeldata_rows.append(row)
                modeldata_ids.add(model_id)
            if display_id not in display_ids:
                row = list(client_display_template[gender])
                row[0] = display_id
                row[1] = model_id
                display_rows.append(row)
                display_ids.add(display_id)

        # ---- CharSections / CharHairGeosets -------------------------------
        sections_rows = [row for row in sections_rows if row[1] != race_id]
        geosets_rows = [row for row in geosets_rows if row[1] != race_id]
        donor_sections = 0
        for row in eunoia_sections.rows:
            if row[1] != donor_id:
                continue
            new = list(row)
            new[0] = sections_next_id
            sections_next_id += 1
            new[1] = race_id
            for field in (4, 5, 6):
                text = eunoia_sections.text(row[field])
                new[field] = pool_add(sections_pool, text) if text else 0
            sections_rows.append(new)
            donor_sections += 1
        entry["sections"] = donor_sections

        donor_geosets = 0
        for row in eunoia_geosets.rows:
            if row[1] != donor_id:
                continue
            new = list(row)
            new[0] = geosets_next_id
            geosets_next_id += 1
            new[1] = race_id
            geosets_rows.append(new)
            donor_geosets += 1
        entry["hair_geosets"] = donor_geosets

        # ---- race icon -----------------------------------------------------
        icon_base, donor_icon = spec["icon"]
        if donor_icon:
            for gender, suffix in (("male", "Male"), ("female", "Female")):
                name = f"Interface\\GLUES\\CHARACTERCREATE\\CharacterCreateIcons\\raceicon128-{donor_icon}-{gender}.blp"
                payload = source.read(name)
                if payload is None:
                    entry["missing"].append(name)
                    continue
                icon = decode_blp(payload).resize((64, 64), Image.LANCZOS)
                stage(f"{icon_base.replace(chr(92)*2, chr(92))}{suffix}.blp", encode_blp2_bgra(icon))
                entry["icon"] = "staged"

        # ---- external animations (only some donor sets use them) -----------
        staged_anims = 0
        for gender in (("male", "female") if STAGE_ANIMS else ()):
            source_stem = spec[gender][0]
            for index in range(0, 1400):
                name = f"{source_stem}{index:04d}-00.anim"
                if not any(lookup(table, name) is not None for table in anim_tables):
                    continue
                payload = source.read(name)
                if payload:
                    stage(name, payload)
                    staged_anims += 1
        entry["anims"] = staged_anims

    # keep one row per race id (guards against earlier duplicate rows)
    deduped: list[list[int]] = []
    seen_ids: set[int] = set()
    for row in chrraces_rows:
        if row[0] in seen_ids:
            continue
        seen_ids.add(row[0])
        deduped.append(row)
    chrraces_rows = deduped

    print("art gathered:", json.dumps(report, indent=2)[:1200])
    print("total staged entries:", len(seen))
    source.close()

    # ---- CharBaseInfo (byte rows) -----------------------------------------
    baseinfo_data = load_client_dbc("DBFilesClient\\CharBaseInfo.dbc", storm)
    magic, count, fields, record, _strings = struct.unpack_from("<4s4I", baseinfo_data, 0)
    width = record // fields
    code = {1: "B", 2: "H", 4: "I"}[width]
    baseinfo_rows = [
        list(struct.unpack_from(f"<{fields}{code}", baseinfo_data, 20 + index * record)) for index in range(count)
    ]
    classes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11]
    for spec in RACES:
        baseinfo_rows = [row for row in baseinfo_rows if row[0] != spec["race_id"]]
        baseinfo_rows.extend([[spec["race_id"], class_id] for class_id in classes])
    baseinfo_rows.sort(key=lambda row: (row[0], row[1]))
    body = b"".join(struct.pack(f"<{fields}{code}", *row) for row in baseinfo_rows)
    baseinfo_out = struct.pack("<4s4I", b"WDBC", len(baseinfo_rows), fields, fields * width, 1) + body + b"\0"

    # ---- glue: race icon entries ------------------------------------------
    glue = load_client_dbc("Interface\\GlueXML\\CharacterCreate.lua", storm).decode("utf-8", "replace")
    icon_lines = []
    for spec in RACES:
        for gender, suffix in (("male", "Male"), ("female", "Female")):
            key = f'{spec["client_file"].upper()}_{gender.upper()}'
            texture = (spec["icon"][0] + suffix).replace("\\", "\\\\")
            icon_lines.append(f'\t["{key}"] = "{texture}",')
    marker = "RACE_ICON_TEXTURES = {"
    if marker in glue:
        glue = glue.replace(marker, marker + "\n" + "\n".join(icon_lines), 1)
    else:
        raise SystemExit("RACE_ICON_TEXTURES table not found in glue")
    glue = re.sub(r"MAX_RACES\s*=\s*\d+", "MAX_RACES = 40", glue, count=1)
    glue = glue.replace(
        'GetFlavorText("RACE_INFO_"..strupper(fileString), GetSelectedSex()).."|n|n"',
        '(GetFlavorText("RACE_INFO_"..strupper(fileString), GetSelectedSex()) or "").."|n|n"',
    )
    # a race whose faction template is unknown to the client must not break the creator
    glue = glue.replace(
        "local backdropColor = FACTION_BACKDROP_COLOR_TABLE[faction];",
        'local backdropColor = FACTION_BACKDROP_COLOR_TABLE[faction] or FACTION_BACKDROP_COLOR_TABLE["Horde"] or FACTION_BACKDROP_COLOR_TABLE["Alliance"];',
    )
    # The creator builds its scene from a background key; a key with no
    # UI_<key>.m2 leaves every non-DK class showing the placeholder cube.
    background_keys = "\n".join(
        f'        ["{key}"] = "{value}",'
        for key, value in (
            ("EREDAR", "ORC"),
            ("NIGHTBORNE", "ORC"),
            ("ZANDALARITROLL", "ORC"),
            ("DRACTHYR", "ORC"),
            ("ILLIDARI", "ORC"),
            ("VOIDELF", "HUMAN"),
            ("LIGHTFORGEDDRAENEI", "HUMAN"),
            ("DARKIRONDWARF", "HUMAN"),
            ("KULTIRAN", "HUMAN"),
        )
    )
    background_marker = '["MAGHAR"] = "ORC",'
    if background_marker in glue and '["VOIDELF"]' not in glue:
        glue = glue.replace(background_marker, background_marker + "\n" + background_keys, 1)
    # the longer race list needs a tighter grid than the stock 118/100 step
    glue = re.sub(r"local rowSpacing = \d+", "local rowSpacing = 80", glue, count=1)
    glue = re.sub(r"local columnSpacing = \d+", "local columnSpacing = 100", glue, count=1)

    # ---- creator XML: make room for extra race buttons ---------------------
    xml = load_client_dbc("Interface\\GlueXML\\CharacterCreate.xml", storm).decode("utf-8", "replace")
    highest = max(int(n) for n in re.findall(r'name="CharacterCreateRaceButton(\d+)"', xml))
    extra = "".join(
        f'\n                                <CheckButton name="CharacterCreateRaceButton{n}" inherits="CharacterCreateRaceButtonTemplate" id="{n}"/>'
        for n in range(highest + 1, 41)
    )
    anchor = f'name="CharacterCreateRaceButton{highest}"'
    if anchor in xml:
        end = xml.find("/>", xml.find(anchor)) + 2
        xml = xml[:end] + extra + xml[end:]
    else:
        raise SystemExit("race button anchor not found in CharacterCreate.xml")

    # ---- RACE_INFO tooltips ------------------------------------------------
    # ---- CharStartOutfit: clone a sibling race for preview gear ------------
    outfit_data = load_client_dbc("DBFilesClient\\CharStartOutfit.dbc", storm)
    o_magic, o_count, o_fields, o_record, o_string_size = struct.unpack_from("<4s4I", outfit_data, 0)
    o_strings = outfit_data[20 + o_count * o_record : 20 + o_count * o_record + o_string_size]
    outfit_rows = [
        bytearray(outfit_data[20 + index * o_record : 20 + (index + 1) * o_record]) for index in range(o_count)
    ]
    existing_races = {row[4] for row in outfit_rows}
    outfit_next_id = max(int.from_bytes(bytes(row[0:4]), "little") for row in outfit_rows) + 1
    outfit_added = 0
    for spec in RACES:
        # clone the outfit rows of the one custom race this client already dresses
        template = 20
        if not template:
            continue
        outfit_rows[:] = [r for r in outfit_rows if r[4] != spec["race_id"]]
        for row in [r for r in outfit_rows if r[4] == template]:
            new_row = bytearray(row)
            new_row[0:4] = outfit_next_id.to_bytes(4, "little")
            new_row[4] = spec["race_id"]
            outfit_rows.append(new_row)
            outfit_next_id += 1
            outfit_added += 1
    outfit_out = (
        struct.pack("<4s4I", b"WDBC", len(outfit_rows), o_fields, o_record, len(o_strings))
        + b"".join(bytes(row) for row in outfit_rows)
        + o_strings
    )
    print(f"CharStartOutfit: added {outfit_added} rows")

    # DBC rows are binary-searched by their key, so the tables must stay sorted.
    # Re-key onto display ids the client already knows, overwriting the rows behind
    # them (newly appended ids are never resolved by this client's creator).
    path_by_race = {spec["race_id"]: spec for spec in RACES}
    for spec in RACES:
        pair = spec.get("display_pair")
        if not pair:
            continue
        for chr_row in chrraces_rows:
            if chr_row[0] == spec["race_id"]:
                chr_row[4], chr_row[5] = pair
                break
        for gender, display_id in (("male", pair[0]), ("female", pair[1])):
            display_row = next((r for r in display_rows if r[0] == display_id), None)
            if display_row is None:
                continue
            model_id = display_row[1]
            target = spec.get("target_paths", {}).get(gender) if "target_paths" in spec else None
        # paths were recorded per race while staging; look them up from the report
        entry = report.get(spec["key"], {})
        for gender, display_id in (("male", pair[0]), ("female", pair[1])):
            target = entry.get("target_paths", {}).get(gender)
            if not target:
                continue
            display_row = next((r for r in display_rows if r[0] == display_id), None)
            if display_row is None:
                continue
            for model_row in modeldata_rows:
                if model_row[0] == display_row[1]:
                    model_row[2] = pool_add(modeldata_pool, target.replace(".mdx", ".m2"))
                    break
    chrraces_rows.sort(key=lambda row: row[0])
    modeldata_rows.sort(key=lambda row: row[0])
    display_rows.sort(key=lambda row: row[0])
    sections_rows.sort(key=lambda row: row[0])
    geosets_rows.sort(key=lambda row: row[0])
    outfit_rows.sort(key=lambda row: int.from_bytes(bytes(row[0:4]), "little"))

    # ---- CharacterInfo.lua: per-race tooltip / info panel text --------------
    info_lua = load_client_dbc("Interface\\GlueXML\\CharacterInfo.lua", storm).decode("utf-8", "replace")
    info_entries = ""
    for spec in RACES:
        text = FLAVOUR.get(spec["client_file"].upper(), spec["name"])
        info_entries += (
            f'\n[{spec["race_id"]}] = {{\n'
            f'      Name = "{spec["name"]}",\n'
            f'      Description = "{text}",\n'
            f'}};\n'
        )
    marker = "Races_Informations = {"
    if marker in info_lua:
        info_lua = info_lua.replace(marker, marker + "\n" + info_entries, 1)
    else:
        info_lua = None

    strings_lua = None
    for patch_name in ("PATCH-A.MPQ", "Patch-C.MPQ", "PATCH-X.MPQ"):
        handle = H()
        if not storm.dll.SFileOpenArchive(str(CLIENT_DATA / patch_name), 0, MPQ_OPEN_READ_ONLY, c.byref(handle)):
            continue
        try:
            strings_lua = storm.read(handle, "Interface\\GlueXML\\GlueStrings.lua").decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            strings_lua = None
        storm.dll.SFileCloseArchive(handle)
        if strings_lua and "RACE_INFO_HIGHELF" in strings_lua:
            break
    if strings_lua and "RACE_INFO_HIGHELF" in strings_lua:
        flavour = {
            "EREDAR": "Eredar are the ancient, fel-touched draenei who wield immense arcane and demonic power.",
            "NIGHTBORNE": "Nightborne are the children of Suramar, steeped in the Nightwell and its arcane gifts.",
            "VOIDELF": "Void elves channel the shadow between the stars, wielding entropy as a weapon.",
            "LIGHTFORGEDDRAENEI": "Lightforged draenei are infused with the Light, forged to wage the eternal war against the Legion.",
            "ZANDALARITROLL": "Zandalari trolls are the proud, ancient forebears of all trollkind, blessed by their loa.",
            "DARKIRONDWARF": "Dark Iron dwarves are born of the fire beneath Blackrock, hardened and fiercely independent.",
            "DRACTHYR": "Dracthyr are ancient draconic soldiers, wielding the magic of all five dragonflights.",
            "KULTIRAN": "Kul Tirans are the hardy seafarers of Boralus, steeped in the tides and old ways of Drustvar.",
            "ILLIDARI": "Illidari are demon hunters who bound themselves to fel power to hunt the Burning Legion.",
        }
        additions = []
        for key, text in flavour.items():
            additions.append(f'["RACE_INFO_{key}"] = {{ ["enUS"] = "{text}" }},')
            additions.append(f'["RACE_INFO_{key}_FEMALE"] = {{ ["enUS"] = "{text}" }},')
        anchor = '["RACE_INFO_HIGHELF"]'
        if anchor in strings_lua:
            strings_lua = strings_lua.replace(anchor, "\n".join(additions) + "\n" + anchor, 1)
        else:
            strings_lua = None

    # ---- write Patch-D.MPQ -------------------------------------------------
    if "y" not in writers:
        if PATCH_Y.exists():
            PATCH_Y.unlink()
        writers["y"] = PatchWriter(PATCH_Y, 64)
    final = writers["y"]
    if final is None:
        raise SystemExit("no patch was written")
    final.add("DBFilesClient\\ChrRaces.dbc", dbc_from(chrraces_rows, chrraces_fields, chrraces_pool))
    final.add("DBFilesClient\\CharSections.dbc", dbc_from(sections_rows, sections_fields, sections_pool))
    final.add("DBFilesClient\\CharHairGeosets.dbc", dbc_from(geosets_rows, geosets_fields, geosets_pool))
    final.add("DBFilesClient\\CreatureModelData.dbc", dbc_from(modeldata_rows, modeldata_fields, modeldata_pool))
    final.add("DBFilesClient\\CreatureDisplayInfo.dbc", dbc_from(display_rows, display_fields, display_pool))
    final.add("DBFilesClient\\CharBaseInfo.dbc", baseinfo_out)
    final.add("DBFilesClient\\CharStartOutfit.dbc", outfit_out)
    final.add("Interface\\GlueXML\\CharacterCreate.lua", glue.encode("utf-8"))
    final.add("Interface\\GlueXML\\CharacterCreate.xml", xml.encode("utf-8"))
    if strings_lua:
        final.add("Interface\\GlueXML\\GlueStrings.lua", strings_lua.encode("utf-8"))
    if info_lua:
        final.add("Interface\\GlueXML\\CharacterInfo.lua", info_lua.encode("utf-8"))
    for writer in writers.values():
        if writer is not None:
            writer.close()

    manifest = OUT / "port-manifest.json"
    manifest.write_text(json.dumps(report, indent=2), encoding="utf-8")
    for key, path in patch_paths.items():
        if path.exists():
            print(f"\n{path.name}: {path.stat().st_size:,} bytes")
    print(f"manifest {manifest}")


if __name__ == "__main__":
    main()
