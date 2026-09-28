"""Extract the supplied car MPQs and build an additive WotLK car pack."""

from __future__ import annotations

import argparse
import ctypes as c
import hashlib
import json
import os
import re
import shutil
import struct
from dataclasses import dataclass, replace
from pathlib import Path


H = c.c_void_p
U = c.c_uint32
WOTLK_MODEL_VERSION = 264
MOUNT_ID_BASES = {
    "spell": 201000,
    "spell_icon": 514646,
    "item": 901000,
    "item_display": 135000,
    "creature": 3460608,
    "display": 94300,
    "model": 5000,
}
LEGACY_MOUNT_IDS = {
    "item_display": tuple(range(135000, 135089)),
    "display": tuple(range(94300, 94389)),
    "model": tuple(range(5000, 5089)),
}
FLYING_MOUNT_MODEL_STEMS = frozenset({"gameboymount", "pokemoncardmount"})
FLYING_MOUNT_SPELL_TEMPLATE_ID = 61309
# Flying Nimbus is an older custom mount outside the 111-record source pack,
# but its spell is still live and account-wide. Keep its spellbook mapping in
# this same native DBC merge.
LEGACY_CUSTOM_MOUNT_SPELL_IDS = (201111,)
MOUNT_VARIANT_SPECS = {
    "gameboymount": (
        ("Zelda DX", {11: "GameBoyMount_Case_01.blp", 12: "GameBoyMount_Screen_ZeldaDX.blp"}),
        ("Wario Land", {11: "GameBoyMount_Case_01.blp", 12: "GameBoyMount_Screen_WarioLand.blp"}),
        ("Super Mario Land", {11: "GameBoyMount_Case_01.blp", 12: "GameBoyMount_Screen_SuperMarioLand.blp"}),
        ("Pokemon Yellow", {11: "GameBoyMount_Case_01.blp", 12: "GameBoyMount_Screen_PKMNYellow.blp"}),
        ("Pokemon Silver", {11: "GameBoyMount_Case_01.blp", 12: "GameBoyMount_Screen_PKMNSilver.blp"}),
        ("Pokemon Red", {11: "GameBoyMount_Case_01.blp", 12: "GameBoyMount_Screen_PKMNRed.blp"}),
        ("Pokemon Green", {11: "GameBoyMount_Case_01.blp", 12: "GameBoyMount_Screen_PKMNGreen.blp"}),
        ("Pokemon Gold", {11: "GameBoyMount_Case_01.blp", 12: "GameBoyMount_Screen_PKMNGold.blp"}),
        ("Pokemon Blue", {11: "GameBoyMount_Case_01.blp", 12: "GameBoyMount_Screen_PKMNBlue.blp"}),
        ("Metroid 2", {11: "GameBoyMount_Case_01.blp", 12: "GameBoyMount_Screen_Metroid2.blp"}),
        ("Mega Man 2", {11: "GameBoyMount_Case_01.blp", 12: "GameBoyMount_Screen_MegaMan2.blp"}),
        ("Kirby 2", {11: "GameBoyMount_Case_01.blp", 12: "GameBoyMount_Screen_Kirby2.blp"}),
    ),
    "pokemoncardmount": (
        ("Ancient Mew", {11: "PokemonCardMount_F_01.blp", 12: "PokemonCardMount_F_02_AncientMew.blp"}),
        ("Lucario", {11: "PokemonCardMount_E_01.blp", 12: "PokemonCardMount_E_02_Lucario.blp"}),
        ("Deoxys", {11: "PokemonCardMount_E_01.blp", 12: "PokemonCardMount_E_02_Deoxys.blp"}),
        ("Arceus", {11: "PokemonCardMount_E_01.blp", 12: "PokemonCardMount_E_02_Arceus.blp"}),
        ("Sylveon", {11: "PokemonCardMount_D_01.blp", 12: "PokemonCardMount_D_02_Sylveon.blp"}),
        ("Zekrom", {11: "PokemonCardMount_C_01.blp", 12: "PokemonCardMount_C_02_Zekrom.blp"}),
        ("Reshiram", {11: "PokemonCardMount_C_01.blp", 12: "PokemonCardMount_C_02_Reshiram.blp"}),
        ("Shiny Mew", {11: "PokemonCardMount_B_01.blp", 12: "PokemonCardMount_B_02_ShinyMew.blp"}),
        ("Venusaur", {11: "PokemonCardMount_A_01.blp", 12: "PokemonCardMount_A_02_Venusaur.blp"}),
        ("Blastoise", {11: "PokemonCardMount_A_01.blp", 12: "PokemonCardMount_A_02_Blastoise.blp"}),
    ),
}
DLL_DEFAULT = Path(r"R:\Users\Zach\Downloads\battlemon\Client\wdbx-2.4.1.a-extended-dbc\x64\StormLib.dll")
SOURCE_DEFAULT = Path(
    r"R:\Users\Zach\Downloads\WoW Cars 3.3.5 900 1 2026-07-17T00-39Z KALsNGcJL(1)\WoW Cars 3.3.5"
)
MOUNT_SOURCE_DEFAULTS = (
    Path(r"R:\Users\Zach\Downloads\WoWModels\[MK8]_Standard_Kart_M-C_Pack"),
    Path(r"R:\Users\Zach\Downloads\WoWModels\beemount"),
    Path(r"R:\Users\Zach\Downloads\WoWModels\cata-legion mounts"),
    Path(r"R:\Users\Zach\Downloads\WoWModels\DrakeMountEmerald1"),
    Path(r"R:\Users\Zach\Downloads\WoWModels\Game_Boy_Mount_1.0"),
    Path(r"R:\Users\Zach\Downloads\WoWModels\murlocmount-files"),
    Path(r"R:\Users\Zach\Downloads\WoWModels\NetherGorgedGreatwyrm1(1)"),
    Path(r"R:\Users\Zach\Downloads\WoWModels\PKMN_Card_Mount_1.0"),
    Path(r"R:\Users\Zach\Downloads\WoWModels\Viridian Phase Hunter"),
    Path(r"R:\Users\Zach\Downloads\WoWModels\WhimsyshireCloudMount V2.0(1)"),
    Path(r"R:\Users\Zach\Downloads\WoWModels\HighElfHorses(3)"),
    Path(r"R:\Users\Zach\Downloads\WoWModels\Dragonflight_Mounts_Pack"),
)
NATIVE_DBC_TABLES = (
    "Spell", "Item", "ItemDisplayInfo", "CreatureDisplayInfo", "CreatureModelData", "SkillLineAbility"
)
NATIVE_DBC_SOURCE_DEFAULTS = {
    "Spell": Path(r"3.3.5a - Dev\Data\Patch-A.MPQ"),
    "Item": Path(r"3.3.5a - Dev\Data\Patch-A.MPQ"),
    "ItemDisplayInfo": Path(r"3.3.5a - Dev\Data\Patch-A.MPQ"),
    "CreatureDisplayInfo": Path(r"3.3.5a - Dev\Data\Patch-C.MPQ"),
    "CreatureModelData": Path(r"3.3.5a - Dev\Data\Patch-C.MPQ"),
    "SkillLineAbility": Path(r"3.3.5a - Dev\Data\Patch-A.MPQ"),
}
DEFAULT_MOUNT_ICON_SOURCE = Path(r"3.3.5a - Dev\Data\enUS\locale-enUS.MPQ")
DEFAULT_MOUNT_ICON_ENTRY = r"Interface\Icons\Ability_Mount_RidingHorse.blp"
REPO_DEFAULT = Path(__file__).resolve().parents[1]


class FindData(c.Structure):
    _fields_ = [
        ("cFileName", c.c_char * 260),
        ("szPlainName", c.c_char_p),
        ("dwHashIndex", U),
        ("dwBlockIndex", U),
        ("dwFileSize", U),
        ("dwFileFlags", U),
        ("dwCompSize", U),
        ("dwFileTimeLo", U),
        ("dwFileTimeHi", U),
        ("lcLocale", U),
        ("dwCrc32", U),
        ("dwDataOffset", U),
    ]


class Storm:
    def __init__(self, dll_path: Path):
        self.dll = c.WinDLL(str(dll_path), use_last_error=True)
        self._set("SFileOpenArchive", [c.c_wchar_p, U, U, c.POINTER(H)], c.c_bool)
        self._set("SFileCloseArchive", [H], c.c_bool)
        self._set("SFileFindFirstFile", [H, c.c_char_p, c.POINTER(FindData), c.c_wchar_p], H)
        self._set("SFileFindNextFile", [H, c.POINTER(FindData)], c.c_bool)
        self._set("SFileFindClose", [H], c.c_bool)
        self._set("SFileOpenFileEx", [H, c.c_char_p, U, c.POINTER(H)], c.c_bool)
        self._set("SFileGetFileSize", [H, c.POINTER(U)], U)
        self._set("SFileReadFile", [H, H, U, c.POINTER(U), H], c.c_bool)
        self._set("SFileCloseFile", [H], c.c_bool)
        self._set("SFileCreateArchive", [c.c_wchar_p, U, U, c.POINTER(H)], c.c_bool)
        self._set("SFileCreateFile", [H, c.c_char_p, c.c_uint64, U, U, U, c.POINTER(H)], c.c_bool)
        self._set("SFileSetMaxFileCount", [H, U], c.c_bool)
        self._set("SFileGetMaxFileCount", [H], U)
        self._set("SFileWriteFile", [H, H, U, U], c.c_bool)
        self._set("SFileFinishFile", [H], c.c_bool)

    def _set(self, name, args, result):
        fn = getattr(self.dll, name)
        fn.argtypes = args
        fn.restype = result

    def open_archive(self, path: Path) -> H:
        handle = H()
        if not self.dll.SFileOpenArchive(str(path), 0, 0, c.byref(handle)):
            raise OSError(f"SFileOpenArchive failed: {path} ({c.get_last_error()})")
        return handle

    def list_files(self, archive: H) -> list[tuple[str, int, int, int]]:
        data = FindData()
        finder = self.dll.SFileFindFirstFile(archive, b"*", c.byref(data), None)
        if not finder:
            raise OSError(f"SFileFindFirstFile failed ({c.get_last_error()})")
        result = []
        try:
            while True:
                name = data.cFileName.split(b"\0", 1)[0].decode("ascii")
                result.append((name, data.dwFileSize, data.dwCompSize, data.dwFileFlags))
                if not self.dll.SFileFindNextFile(finder, c.byref(data)):
                    break
        finally:
            self.dll.SFileFindClose(finder)
        return result

    def read(self, archive: H, key: str) -> bytes:
        handle = H()
        if not self.dll.SFileOpenFileEx(archive, key.encode("ascii"), 0, c.byref(handle)):
            raise OSError(f"SFileOpenFileEx failed: {key} ({c.get_last_error()})")
        try:
            size = self.dll.SFileGetFileSize(handle, None)
            buffer = c.create_string_buffer(size or 1)
            got = U()
            if not self.dll.SFileReadFile(handle, buffer, size, c.byref(got), None) or got.value != size:
                raise OSError(f"SFileReadFile failed: {key} ({c.get_last_error()})")
            return buffer.raw[:size]
        finally:
            self.dll.SFileCloseFile(handle)

    def create_archive(self, path: Path, entries: dict[str, bytes]) -> None:
        handle = H()
        flags = 0x00000001 | 0x00000002
        if not self.dll.SFileCreateArchive(str(path), flags, len(entries) + 8, c.byref(handle)):
            raise OSError(f"SFileCreateArchive failed: {path} ({c.get_last_error()})")
        try:
            for name, payload in entries.items():
                file_handle = H()
                file_flags = 0
                if not self.dll.SFileCreateFile(handle, name.encode("ascii"), 0, len(payload), 0, file_flags, c.byref(file_handle)):
                    raise OSError(f"SFileCreateFile failed: {name} ({c.get_last_error()})")
                try:
                    buffer = c.create_string_buffer(payload or b"\0")
                    if not self.dll.SFileWriteFile(file_handle, buffer, len(payload), 0x00000002):
                        raise OSError(f"SFileWriteFile failed: {name} ({c.get_last_error()})")
                finally:
                    self.dll.SFileCloseFile(file_handle)
        finally:
            self.dll.SFileCloseArchive(handle)

    def ensure_capacity(self, archive: H, extra: int) -> None:
        """Grow the MPQ hash table so `extra` new entries can be added.

        StormLib reports ERROR_DISK_FULL (112) when the hash table is full, not
        only when the volume is; an archive created with a fixed MAX_FILE_COUNT
        silently refuses new entries once it is saturated.
        """
        if extra <= 0 or not hasattr(self.dll, "SFileSetMaxFileCount"):
            return
        try:
            current = self.dll.SFileGetMaxFileCount(archive)
        except Exception:
            return
        needed = current + max(extra, 512)
        if needed > current:
            self.dll.SFileSetMaxFileCount(archive, needed)

    def replace_archive_entries(self, path: Path, entries: dict[str, bytes]) -> None:
        """Add or replace entries without reading/rebuilding unrelated MPQ files."""

        archive = self.open_archive(path)
        try:
            self.ensure_capacity(archive, len(entries))
            for name, payload in entries.items():
                file_handle = H()
                flags = 0x80000000  # MPQ_FILE_REPLACEEXISTING
                if not self.dll.SFileCreateFile(
                    archive,
                    name.encode("ascii"),
                    0,
                    len(payload),
                    0,
                    flags,
                    c.byref(file_handle),
                ):
                    raise OSError(f"SFileCreateFile failed: {name} ({c.get_last_error()})")
                try:
                    buffer = c.create_string_buffer(payload or b"\0")
                    if not self.dll.SFileWriteFile(file_handle, buffer, len(payload), 0x00000002):
                        raise OSError(f"SFileWriteFile failed: {name} ({c.get_last_error()})")
                finally:
                    self.dll.SFileCloseFile(file_handle)
        finally:
            self.dll.SFileCloseArchive(archive)


class Wdbc:
    def __init__(self, data: bytes):
        magic, self.count, self.fields, self.record_size, string_size = struct.unpack_from("<4s4I", data)
        if magic != b"WDBC" or self.record_size != self.fields * 4:
            raise ValueError("unsupported WDBC layout")
        expected = 20 + self.count * self.record_size + string_size
        if len(data) != expected:
            raise ValueError(f"invalid WDBC size: {len(data)} != {expected}")
        self.rows = [list(struct.unpack_from(f"<{self.fields}I", data, 20 + i * self.record_size)) for i in range(self.count)]
        self.strings = data[20 + self.count * self.record_size :]

    def row(self, row_id: int) -> list[int]:
        return next(row.copy() for row in self.rows if row[0] == row_id)

    def text(self, offset: int) -> str:
        if not offset:
            return ""
        end = self.strings.find(b"\0", offset)
        return self.strings[offset:end].decode("utf-8")


class StringPool:
    def __init__(self):
        self.data = bytearray(b"\0")

    def add(self, value: str) -> int:
        offset = len(self.data)
        self.data.extend(value.encode("utf-8") + b"\0")
        return offset


def build_wdbc(rows: list[list[int]], fields: int, record_size: int, strings: dict[tuple[int, int], str] | None = None) -> bytes:
    if record_size != fields * 4:
        raise ValueError("continuation rows must use four-byte fields")
    pool = StringPool()
    output = [row.copy() for row in rows]
    for key, value in (strings or {}).items():
        row_index, field_index = (0, key) if isinstance(key, int) else key
        output[row_index][field_index] = pool.add(value)
    body = b"".join(struct.pack(f"<{fields}I", *(value & 0xFFFFFFFF for value in row)) for row in output)
    return struct.pack("<4s4I", b"WDBC", len(output), fields, record_size, len(pool.data)) + body + pool.data


def mount_skill_line_ability_row(spell_id: int) -> list[int]:
    return [spell_id, 777, spell_id, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]


DBC_STRING_FIELDS = {
    "Spell": tuple(range(136, 152)) + tuple(range(153, 169)) + tuple(range(170, 186)) + tuple(range(187, 203)),
    "ItemDisplayInfo": tuple(range(1, 7)) + tuple(range(15, 23)),
    "CreatureDisplayInfo": (6, 7, 8, 9),
    "CreatureModelData": (2,),
    "SpellIcon": (1,),
}


def merge_wdbc_continuations(base: bytes, extra: bytes, table_name: str) -> bytes:
    left = Wdbc(base)
    right = Wdbc(extra)
    if (left.fields, left.record_size) != (right.fields, right.record_size):
        raise ValueError(f"continuation layout mismatch for {table_name}")
    row_sources = [(left, row) for row in left.rows] + [(right, row) for row in right.rows]
    row_sources.sort(key=lambda item: item[1][0])
    rows = [row for _, row in row_sources]
    strings: dict[tuple[int, int], str] = {}
    fields = DBC_STRING_FIELDS.get(table_name, ())
    for row_index, (table, row) in enumerate(row_sources):
        for field in fields:
            if row[field]:
                value = table.text(row[field])
                if value:
                    strings[(row_index, field)] = value
    return build_wdbc(rows, left.fields, left.record_size, strings)


def rewrite_m2_paths(data: bytes, replacements: dict[bytes, bytes]) -> bytes:
    result = bytearray(data)
    for old, new in replacements.items():
        if len(new) > len(old):
            raise ValueError(f"replacement is longer than the in-place M2 string: {old!r}")
        start = 0
        found = False
        while True:
            position = result.find(old, start)
            if position < 0:
                break
            result[position : position + len(new)] = new
            result[position + len(new) : position + len(old)] = b"\0" * (len(old) - len(new))
            start = position + len(old)
            found = True
        if not found:
            raise ValueError(f"M2 string not found: {old!r}")
    return bytes(result)


def f32(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def key_map(files: list[tuple[str, int, int, int]]) -> dict[str, str]:
    return {name.casefold(): name for name, *_ in files}


def safe_relative(name: str) -> Path:
    parts = name.replace("/", "\\").split("\\")
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise ValueError(f"unsafe MPQ path: {name}")
    return Path(*parts)


@dataclass(frozen=True)
class Mount:
    package: str
    source_root: Path
    model: Path
    source_relative: Path
    slug: str
    display_name: str
    model_version: int
    client_model_path: str
    texture_overrides: tuple[tuple[int, str], ...] = ()
    vehicle_id: int | None = None
    vehicle_seat_id: int | None = None


@dataclass(frozen=True)
class RejectedModel:
    package: str
    model: Path
    version: int


@dataclass(frozen=True)
class MountRecord:
    mount: Mount
    spell_id: int
    spell_icon_id: int
    item_id: int
    item_display_id: int
    creature_id: int
    display_id: int
    model_id: int
    spell_row: tuple[int, ...]
    item_row: tuple[int, ...]
    item_display_row: tuple[int, ...]
    creature_display_row: tuple[int, ...]
    texture_variations: tuple[str, str, str]
    creature_model_row: tuple[int, ...]
    vehicle_row: tuple[int, ...] | None = None
    vehicle_seat_row: tuple[int, ...] | None = None


def m2_version(data: bytes) -> int:
    if len(data) < 8 or data[:4] not in (b"MD20", b"MD21"):
        raise ValueError("not an M2 model")
    return struct.unpack_from("<I", data, 4)[0]


def _model_version(path: Path) -> int:
    return m2_version(path.read_bytes())


def _slug_words(value: str) -> list[str]:
    value = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", value)
    return re.findall(r"[A-Za-z0-9]+", value)


def _mount_slug(package: str, relative: Path) -> str:
    words = _slug_words(package) + [word for part in relative.parts for word in _slug_words(Path(part).stem)]
    slug = "_".join(words).lower()
    if not slug:
        raise ValueError(f"cannot derive mount slug from {package}/{relative}")
    if len(slug) > 24:
        slug = f"{slug[:10]}_{hashlib.sha1(slug.encode('ascii')).hexdigest()[:8]}"
    return slug


def _mount_name(relative: Path) -> str:
    return " ".join(_slug_words(relative.stem)).strip()


def _is_flying_mount(model_stem: str) -> bool:
    return model_stem.casefold() in FLYING_MOUNT_MODEL_STEMS


def _source_relative(root: Path, path: Path) -> Path:
    parts = list(path.relative_to(root).parts)
    while len(parts) > 1 and parts[0].casefold() in {root.name.casefold(), "wotlk"}:
        parts.pop(0)
    return Path(*parts)


def _mount_candidates(roots: tuple[Path, ...]) -> list[tuple[Path, Path, int]]:
    candidates = []
    for root in roots:
        if not root.is_dir():
            raise FileNotFoundError(root)
        for model in root.rglob("*"):
            if model.is_file() and model.suffix.casefold() == ".m2":
                candidates.append((root, model, _model_version(model)))
    return sorted(candidates, key=lambda item: (item[0].name.casefold(), str(_source_relative(item[0], item[1])).casefold()))


def rejected_models(roots: tuple[Path, ...]) -> tuple[RejectedModel, ...]:
    return tuple(
        RejectedModel(root.name, model, version)
        for root, model, version in _mount_candidates(roots)
        if version != WOTLK_MODEL_VERSION
    )


def discover_mounts(roots: tuple[Path, ...]) -> tuple[Mount, ...]:
    mounts = []
    seen_slugs: set[str] = set()
    seen_names: set[str] = set()
    for root, model, version in _mount_candidates(roots):
        if version != WOTLK_MODEL_VERSION:
            continue
        relative = _source_relative(root, model)
        slug = _mount_slug(root.name, relative)
        display_name = _mount_name(relative)
        if slug in seen_slugs:
            raise ValueError(f"duplicate mount slug: {slug}")
        if display_name.casefold() in seen_names:
            display_name = f"{display_name} ({root.name})"
        seen_slugs.add(slug)
        seen_names.add(display_name.casefold())
        mounts.append(
            Mount(
                package=root.name,
                source_root=root,
                model=model,
                source_relative=relative,
                slug=slug,
                display_name=display_name,
                model_version=version,
                client_model_path=f"Creature\\EsteriaMounts\\{slug}\\{model.name}",
            )
        )
    return tuple(mounts)


def expand_mount_variants(mounts: tuple[Mount, ...]) -> tuple[Mount, ...]:
    expanded = list(mounts)
    for mount in mounts:
        for label, textures in MOUNT_VARIANT_SPECS.get(mount.model.stem.casefold(), ()):
            variant_slug = f"{mount.slug}_{'_'.join(_slug_words(label)).lower()}"
            if len(variant_slug) > 24:
                variant_slug = f"{variant_slug[:10]}_{hashlib.sha1(variant_slug.encode('ascii')).hexdigest()[:8]}"
            expanded.append(
                replace(
                    mount,
                    slug=variant_slug,
                    display_name=f"{mount.display_name} - {label}",
                    client_model_path=f"Creature\\EsteriaMounts\\{variant_slug}\\{mount.model.name}",
                    texture_overrides=tuple(sorted(textures.items())),
                )
            )
    if len({mount.slug for mount in expanded}) != len(expanded):
        raise ValueError("duplicate mount variant slug")
    return tuple(expanded)


def mount_ids(mounts: tuple[Mount, ...], baseline: Path | None = None) -> dict[str, tuple[int, ...]]:
    count = len(mounts)
    ids = {
        name: tuple(base + index for index in range(count))
        for name, base in MOUNT_ID_BASES.items()
    }
    if baseline is None:
        return ids

    native_ranges = {
        "item_display": ("ItemDisplayInfo.dbc", 68742, (134239, 134240, 134241, 134242)),
        "display": ("CreatureDisplayInfo.dbc", 94234, (94229, 94230, 94231, 94232)),
        "model": ("CreatureModelData.dbc", 4899, (4892, 4893, 4894, 4895)),
    }
    for kind, (file_name, maximum, reserved) in native_ranges.items():
        used = {row[0] for row in Wdbc((baseline / file_name).read_bytes()).rows}
        used.update(reserved)
        available = [candidate for candidate in range(maximum - 1, 0, -1) if candidate not in used]
        if len(available) < count:
            raise ValueError(f"not enough native {kind} IDs for {count} mounts")
        base_count = sum(not mount.texture_overrides for mount in mounts)
        ids[kind] = tuple(sorted(available[:base_count])) + tuple(sorted(available[base_count:count]))
    return ids


def merge_archive_entries(existing: dict[str, bytes], additions: dict[str, bytes]) -> dict[str, bytes]:
    merged = dict(existing)
    canonical: dict[str, tuple[str, bytes]] = {name.casefold(): (name, payload) for name, payload in existing.items()}
    for name, payload in additions.items():
        key = name.casefold()
        prior = canonical.get(key)
        if prior is not None:
            if prior[1] != payload:
                raise ValueError(f"archive path collision with different bytes: {name} vs {prior[0]}")
            continue
        canonical[key] = (name, payload)
        merged[name] = payload
    return merged


def remove_existing_mount_entries(entries: dict[str, bytes]) -> dict[str, bytes]:
    return {
        name: payload
        for name, payload in entries.items()
        if not name.casefold().startswith("creature\\esteriamounts\\")
        and not (name.casefold().startswith("dbfilesclient/") and name.casefold().endswith(".dbc1-mounts"))
        and not name.casefold().startswith("interface\\icons\\inv_mount_")
    }


def _m2_texture_records(data: bytes) -> list[tuple[int, int, bytes]]:
    base = 8 if data[:4] == b"MD21" else 0
    if len(data) < base + 0x58:
        raise ValueError("M2 is too short for a texture table")
    count, offset = struct.unpack_from("<II", data, base + 0x50)
    end = base + offset + count * 16
    if end > len(data):
        raise ValueError("M2 texture table exceeds file size")
    result = []
    for index in range(count):
        record = base + offset + index * 16
        texture_type, _, length, name_offset = struct.unpack_from("<IIII", data, record)
        name = b""
        if length:
            if name_offset + length > len(data):
                raise ValueError("M2 texture name exceeds file size")
            name = data[name_offset : name_offset + length].rstrip(b"\0")
        result.append((record, texture_type, name))
    return result


def _m2_texture_entries(data: bytes) -> list[tuple[int, bytes]]:
    return [(record, name) for record, _, name in _m2_texture_records(data) if name]


def rewrite_m2_texture_paths(data: bytes, replacements: dict[bytes, str]) -> bytes:
    result = bytearray(data)
    normalized = {key.lower(): value.encode("ascii") + b"\0" for key, value in replacements.items()}
    for record, old_name in _m2_texture_entries(data):
        replacement = normalized.get(old_name.lower())
        if replacement is None:
            continue
        offset = (len(result) + 3) & ~3
        result.extend(b"\0" * (offset - len(result)))
        result.extend(replacement)
        struct.pack_into("<II", result, record + 8, len(replacement), offset)
    return bytes(result)


def rewrite_m2_texture_records(data: bytes, replacements: dict[int, str]) -> bytes:
    result = bytearray(data)
    for record, replacement in replacements.items():
        value = replacement.encode("ascii") + b"\0"
        offset = (len(result) + 3) & ~3
        result.extend(b"\0" * (offset - len(result)))
        result.extend(value)
        struct.pack_into("<II", result, record + 8, len(value), offset)
    return bytes(result)


MOUNT_TEXTURE_VARIATION_HINTS = {
    "beemount": {11: "beemount.blp", 12: "beemount_armor.blp"},
    "alliancepvpmount": {
        11: "AlliancePVPMountBlue1.blp", 12: "AlliancePVPMountBlue2.blp", 13: "AlliancePVPMountBlue3.blp",
    },
    "cranemount": {11: "CraneBlue.blp", 12: "CraneMount_Blue_2.blp"},
    "dragondeepholmmount": {
        11: "dragondeepholmmount1blue.blp", 12: "dragondeepholmmount2blue.blp", 13: "dragondeepholmmount3blue.blp",
    },
    "dragonhawk": {11: "dragonhawkskin.blp"},
    "dragonhawkmount": {11: "dragonhawkskin.blp"},
    "faeriedragoncreature": {11: "faeriedragonmount01_noalpha.blp", 12: "faeriedragonmountsaddle.blp"},
    "hordepvpmount": {
        11: "HordePVPMountBodyGreen.blp", 12: "HordePVPMountArmorGreen.blp", 13: "HordePVPMountBannerGreen.blp",
    },
    "mushanbeastmount": {11: "MushanBeastMount1Brown.blp", 12: "MushanBeastMount2Brown.blp"},
    "pandarenphoenixmount": {
        11: "PandarenPhoenixMountBody.blp", 12: "PandarenPhoenixMountSaddle.blp", 13: "PandarenPhoenixMountWing.blp",
    },
    "pandarenserpent": {11: "pandarenserpent.blp", 12: "PandarenSerpentMountSaddle_black.blp"},
    "pandarenserpentmount": {11: "pandarenserpent.blp", 12: "PandarenSerpentMountSaddle_red.blp"},
    "mdprotodrakemount": {11: "korkronprotodrake_body1.blp", 12: "korkronprotodrake_armor.blp"},
    "reddrakemount": {
        11: "RedDrakeMountRed1.blp", 12: "RedDrakeMountRed2.blp", 13: "RedDrakeMountRed3.blp",
    },
    "saber2": {11: "saber2.blp"},
    "saber2mount": {11: "saber2mount.blp"},
    "seahorsemount": {11: "Seahorse_purple.blp", 12: "Seahorse_saddle_gold.blp", 13: "SeahorseMount_purple.blp"},
    "skeletalraptormount": {11: "SkeletalRaptorBone.blp", 12: "SkeletalRaptorSaddle.blp"},
    "suramarmount": {11: "suramarmount_skin.blp"},
    "waterstridermount": {
        11: "WaterStriderMount_Blue1.blp", 12: "WaterStriderMount_Blue2.blp", 13: "WaterStriderMount_Blue_Pulse.blp",
    },
    "eagle2windmount": {11: "eagle2windmount.blp", 12: "eagle2windmount_saddle_1.blp"},
    "foxwyvernmount": {11: "foxwyvernmount_black.blp", 12: "foxwyvernmount_saddle_black.blp"},
    "kirinmount": {11: "kirinmount_blue.blp", 12: "kirinmount_saddle_blue_1.blp", 13: "kirinmount_blue.blp"},
    "lavaslugmount": {11: "lavaslugmount_blue.blp", 12: "lavaslugmount_fx_blue.blp", 13: "lavaslugmount_fx2_blue.blp"},
    "lavasnailmount": {
        11: "lavasnailmount_blue.blp", 12: "lavasnailmount_fx_blue.blp", 13: "lavasnailmount_fx2_blue.blp",
    },
    "mammoth2lavamount": {11: "mammoth2lavamount_blue.blp", 12: "mammoth2lavamount_fx_blue.blp"},
    "mammoth2mount": {11: "mammoth2mount_blue.blp"},
    "moosebullmount": {11: "moosebullmount_black.blp", 12: "moosebullmount_saddle_black.blp"},
    "primaldragonflymount": {11: "primaldragonflymount_black.blp", 12: "primaldragonflymount_saddle_1.blp"},
    "riverotterlargemount01": {11: "riverotterlargemount01_black.blp", 12: "riverotterlargemount01_saddle_black.blp"},
    "riverotterlargemount02": {11: "riverotterlargemount02_black.blp", 12: "riverotterlargemount02_saddle_black.blp"},
    "salamanderwatermount": {11: "salamanderwatermount_blue.blp", 12: "salamanderwatermount_saddle_1.blp"},
    "tallstriderprimalmount": {11: "tallstriderprimalmount_black.blp", 12: "tallstriderprimalmount_saddle_1.blp"},
    "thunderlizardprimalmount": {11: "thunderlizardprimalmount_black.blp", 12: "thunderlizardprimalmount_saddle_1.blp"},
    "gameboymount": {11: "GameBoyMount_Case_01.blp", 12: "GameBoyMount_Screen_DonkeyKong.blp"},
    "horse2mounteliteseparate": {12: "Horse2MountElite_Armor_silver.blp"},
    "horsehighelfmount - copia": {11: "horse2mountHighElf.blp", 12: "Horse2_Saddle.blp"},
    "horsehighelfmount": {11: "horse2mountHighElf.blp", 12: "Horse2_Saddle.blp"},
    "horsehighelfmountelite": {
        11: "Horse2MountElite_Body_silver.blp", 12: "Horse2MountElite_Armor_silver.blp",
    },
    "horsehighelfpaladin": {11: "paladinmount_GoldRed.blp", 12: "Horse2_Saddle_HighElf.blp"},
    "horsehighelfpaladinelite": {
        11: "Horse2MountElite_Body_Paladin.blp", 12: "Horse2MountElite_Armor_Paladin.blp",
    },
    "murlocmount": {11: "murlocmount_body.blp", 12: "murlocmount_saddle.blp"},
    "nethergorgedgreatwyrm": {11: "greatwyrm_black.blp"},
    "pokemoncardmount": {11: "PokemonCardMount_A_01.blp", 12: "PokemonCardMount_A_02_Charizard.blp"},
    "warpstalkermountbc": {11: "warpstalkermountbc_teal.blp", 12: "warpstalkermountbc_armor_teal.blp"},
    "whimsyshirecloudmount": {11: "WhimsyshireCloudMount_Happy.blp"},
}
MOUNT_TEXTURE_ALIASES = {
    "mk8standard": {
        "creature\\mk8\\emblem\\dummy.blp": "Creature\\mk8\\emblem\\emblem_dummy.blp",
        "item\\objectcomponents\\shoulder\\orbreflect02.blp": "Creature\\mk8\\standard\\ARMORREFLECT3BRIGHT.BLP",
    },
    "mk8standardreflective": {
        "creature\\mk8\\emblem\\dummy.blp": "Creature\\mk8\\emblem\\emblem_dummy.blp",
    },
    "horse2mounteliteseparate": {
        "creature\\horse2mountelite\\horse2mountelite.blp": "Horse2MountElite\\Horse2MountElite_Body_silver.blp",
    },
}
MOUNT_TEXTURE_SOURCE_OVERRIDES = {
    "scaleddrakemount": {
        "creature\\drakemount\\drakeskinscaled_01.blp": Path(
            r"R:\Users\Zach\Downloads\WoW_Content\Mounts\Drakes_and_protodrakes_pack\Creature\drakemount\drakeskinscaled_01.blp"
        ),
        "creature\\drakemount\\drakeskinscaled_02.blp": Path(
            r"R:\Users\Zach\Downloads\WoW_Content\Mounts\Drakes_and_protodrakes_pack\Creature\drakemount\drakeskinscaled_02.blp"
        ),
        "creature\\drakemount\\drakeskinscaled_03.blp": Path(
            r"R:\Users\Zach\Downloads\WoW_Content\Mounts\Drakes_and_protodrakes_pack\Creature\drakemount\drakeskinscaled_03.blp"
        ),
    },
}


def _source_relative_name(mount: Mount, path: Path) -> str:
    return str(_source_relative(mount.source_root, path)).replace(os.sep, "\\").casefold()


def _source_blp_files(mount: Mount) -> list[Path]:
    return [
        path
        for path in mount.source_root.rglob("*")
        if path.is_file()
        and path.suffix.casefold() == ".blp"
        and not path.stem.casefold().startswith("inv_")
        and "\\interface\\icons\\" not in f"\\{_source_relative_name(mount, path)}\\"
    ]


def _source_asset_candidates_by_stem(mount: Mount, texture_name: bytes) -> list[Path]:
    stem = Path(texture_name.decode("ascii", errors="ignore")).stem.casefold()
    return [path for path in _source_blp_files(mount) if path.stem.casefold() == stem]


def _mount_texture_candidates(mount: Mount, texture_type: int) -> list[Path]:
    all_files = _source_blp_files(mount)
    files = [path for path in all_files if path.parent == mount.model.parent]
    hint = MOUNT_TEXTURE_VARIATION_HINTS.get(mount.model.stem.casefold(), {}).get(texture_type)
    if hint:
        return [path for path in all_files if path.name.casefold() == hint.casefold()]
    files = [
        path for path in files
        if not any(word in path.stem.casefold() for word in (
            "reflect", "glow", "flare", "smoke", "spark", "dust", "effect", "mask", "ribbon", "scroll",
            "white8x8", "grad", "cloud", "ember", "beam", "electric", "orb",
        ))
    ]
    if texture_type == 12:
        files = [path for path in files if any(word in path.stem.casefold() for word in ("saddle", "armor", "screen"))]
    elif texture_type == 13:
        files = [
            path for path in files
            if any(word in path.stem.casefold() for word in ("wing", "banner", "pulse", "fx2"))
        ]
    else:
        files = [
            path for path in files
            if "saddle" not in path.stem.casefold()
        ]
    return sorted(files, key=lambda path: (-path.stat().st_size, str(path).casefold()))[:1]


def _mount_texture_variation_paths(mount: Mount) -> dict[int, Path]:
    if mount.texture_overrides:
        files = {
            path.name.casefold(): path
            for path in _source_blp_files(mount)
        }
        variations = {}
        for texture_type, file_name in mount.texture_overrides:
            try:
                variations[texture_type] = files[file_name.casefold()]
            except KeyError as exc:
                raise FileNotFoundError(f"requested mount texture is missing: {file_name}") from exc
        return variations

    variations = {}
    for _, texture_type, texture_name in _m2_texture_records(mount.model.read_bytes()):
        if texture_type not in (11, 12, 13) or texture_name or texture_type in variations:
            continue
        candidates = _mount_texture_candidates(mount, texture_type)
        if candidates:
            variations[texture_type] = candidates[0]
    return variations


def _source_asset_candidates(mount: Mount, texture_name: bytes) -> list[Path]:
    target = texture_name.decode("ascii", errors="ignore").replace("/", "\\").casefold()
    target_name = Path(target).name
    stock_root = target.split("\\", 1)[0] if "\\" in target else ""
    path_matches = []
    basename_matches = []
    for path in _source_blp_files(mount):
        relative = str(_source_relative(mount.source_root, path)).replace(os.sep, "\\").casefold()
        if relative == target or relative.endswith("\\" + target):
            path_matches.append(path)
        elif stock_root.casefold() not in {"item", "spells", "world", "tileset"} and (
            relative == target_name or relative.endswith("\\" + target_name)
        ):
            basename_matches.append(path)
        elif not stock_root and Path(relative).name == target_name:
            basename_matches.append(path)
    candidates = path_matches or basename_matches
    if candidates:
        return candidates

    override = MOUNT_TEXTURE_SOURCE_OVERRIDES.get(mount.model.stem.casefold(), {}).get(target)
    if override is not None:
        if not override.is_file():
            raise FileNotFoundError(f"required mount texture source is missing: {override}")
        return [override]

    alias = MOUNT_TEXTURE_ALIASES.get(mount.model.stem.casefold(), {}).get(target)
    if alias is None:
        return []
    alias = alias.replace("/", "\\").casefold()
    return [
        path
        for path in _source_blp_files(mount)
        if (
            _source_relative_name(mount, path) == alias
            or _source_relative_name(mount, path).endswith("\\" + alias)
        )
    ]


def collect_mount_entries(mount: Mount, default_icon: bytes | None = None) -> dict[str, bytes]:
    model_data = mount.model.read_bytes()
    source_assets: dict[Path, str] = {}
    replacements: dict[bytes, str] = {}
    record_replacements: dict[int, str] = {}
    entries: dict[str, bytes] = {}
    output_dir = Path(mount.client_model_path).parent
    texture_variations = _mount_texture_variation_paths(mount)
    texture_index = 0
    for record, texture_type, texture_name in _m2_texture_records(model_data):
        if not texture_name:
            if texture_type in texture_variations:
                source = texture_variations[texture_type]
                destination = str(output_dir / source.name).replace("/", "\\")
                entries[destination] = source.read_bytes()
            continue
        candidates = _source_asset_candidates(mount, texture_name) if texture_name else []
        if not candidates and texture_name.lower().endswith(b".dbc"):
            candidates = _source_asset_candidates_by_stem(mount, texture_name)
        if not candidates:
            continue
        payload = candidates[0].read_bytes()
        if any(candidate.read_bytes() != payload for candidate in candidates[1:]):
            raise ValueError(f"ambiguous source texture for {texture_name!r}: {mount.model}")
        destination = source_assets.get(candidates[0])
        if destination is None:
            texture_index += 1
            destination = (
                f"Creature\\EsteriaMounts\\{mount.slug}\\textures\\"
                f"{texture_index:02d}_{candidates[0].name}"
            )
            source_assets[candidates[0]] = destination
            entries[destination] = payload
        if texture_name:
            replacements[texture_name] = destination
        record_replacements[record] = destination

    icon_target = re.sub(r"[^a-z0-9]", "", mount.model.stem.casefold())
    icon_candidates = sorted(
        (
            path
            for path in mount.source_root.rglob("*")
            if path.is_file()
            and path.suffix.casefold() == ".blp"
            and "\\interface\\icons\\" in f"\\{_source_relative_name(mount, path)}\\"
            and (
                icon_target in re.sub(r"[^a-z0-9]", "", path.stem.casefold()).removeprefix("inv")
                or re.sub(r"[^a-z0-9]", "", path.stem.casefold()).removeprefix("inv") in icon_target
            )
        ),
        key=lambda path: (
            len(re.sub(r"[^a-z0-9]", "", path.stem.casefold()).removeprefix("inv")),
            str(path).casefold(),
        ),
    )
    if icon_candidates:
        entries[f"Interface\\Icons\\INV_Mount_{mount.slug}.blp"] = icon_candidates[0].read_bytes()
    elif default_icon is not None:
        entries[f"Interface\\Icons\\INV_Mount_{mount.slug}.blp"] = default_icon

    entries[mount.client_model_path] = rewrite_m2_texture_records(
        rewrite_m2_texture_paths(model_data, replacements), record_replacements
    )
    sibling_extensions = {".skin", ".anim", ".phys"}
    skin_siblings = []
    for sibling in mount.model.parent.iterdir():
        if sibling.is_file() and sibling.suffix.casefold() in sibling_extensions:
            entries[str(output_dir / sibling.name).replace("/", "\\")] = sibling.read_bytes()
            if sibling.suffix.casefold() == ".skin":
                skin_siblings.append(sibling)

    expected_skin_name = f"{mount.model.stem}00.skin"
    expected_skin_key = str(output_dir / expected_skin_name).replace("/", "\\")
    if not any(name.casefold() == expected_skin_key.casefold() for name in entries):
        model_stem = re.sub(r"[^a-z0-9]", "", mount.model.stem.casefold())
        candidates = [
            sibling
            for sibling in skin_siblings
            if re.sub(r"[^a-z0-9]", "", sibling.stem.casefold()).replace("00", "", 1) == model_stem
        ]
        if len(candidates) == 1:
            entries[expected_skin_key] = candidates[0].read_bytes()
        else:
            raise ValueError(f"mount has no unambiguous canonical 00.skin file: {mount.model}")

    if not any(name.casefold() == expected_skin_key.casefold() for name in entries):
        raise ValueError(f"mount has no skin file: {mount.model}")
    return entries


def _f32_from_u32(value: int) -> float:
    return struct.unpack("<f", struct.pack("<I", value & 0xFFFFFFFF))[0]


def _i32_from_u32(value: int) -> int:
    return struct.unpack("<i", struct.pack("<I", value & 0xFFFFFFFF))[0]


def _vehicle_sql_row(row: tuple[int, ...]) -> tuple[object, ...]:
    float_fields = set(range(2, 6)) | set(range(14, 34)) | {35}
    string_fields = set(range(29, 33))
    return tuple(
        "" if index in string_fields else
        _f32_from_u32(value) if index in float_fields else
        _i32_from_u32(value)
        for index, value in enumerate(row)
    )


def _vehicle_seat_sql_row(row: tuple[int, ...]) -> tuple[object, ...]:
    float_fields = set(range(3, 13)) | set(range(19, 26)) | set(range(29, 32)) | {39, 40} | set(range(46, 58))
    return tuple(
        _f32_from_u32(value) if index in float_fields else _i32_from_u32(value)
        for index, value in enumerate(row)
    )


def _m2_bounds(data: bytes) -> tuple[float, float, float, float, float, float, float]:
    if len(data) < 0xBC:
        return -1.0, -1.0, 0.0, 1.0, 1.0, 2.0, 1.0
    values = struct.unpack_from("<7f", data, 0xA0)
    if not all(map(lambda value: value == value and abs(value) < 10000, values)):
        return -1.0, -1.0, 0.0, 1.0, 1.0, 2.0, 1.0
    min_x, min_y, min_z, max_x, max_y, max_z, _ = values
    if max_x <= min_x or max_y <= min_y or max_z <= min_z:
        return -1.0, -1.0, 0.0, 1.0, 1.0, 2.0, 1.0
    width = max(0.5, min(5.0, (max_x - min_x) / 2, (max_y - min_y) / 2))
    height = max(1.0, min(8.0, max_z - min_z))
    mount_height = max(0.5, min(4.0, height * 0.45))
    return min_x, min_y, min_z, max_x, max_y, max_z, width if width else mount_height


def _blank_spell_strings(row: list[int]) -> None:
    for start, end in ((136, 152), (153, 169), (170, 186), (187, 203)):
        row[start:end] = [0] * (end - start)


def build_mount_records(mounts: tuple[Mount, ...], baseline: Path) -> tuple[MountRecord, ...]:
    spell_table = Wdbc((baseline / "Spell.dbc").read_bytes())
    spell_template = spell_table.row(23214)
    flying_spell_template = (
        spell_table.row(FLYING_MOUNT_SPELL_TEMPLATE_ID)
        if any(_is_flying_mount(mount.model.stem) for mount in mounts)
        else None
    )
    item_template = Wdbc((baseline / "Item.dbc").read_bytes()).row(18776)
    ids = mount_ids(mounts, baseline)
    vehicle_template = None
    vehicle_seat_template = None
    if any(mount.vehicle_id is not None for mount in mounts):
        vehicle_template = Wdbc((baseline / "Vehicle.dbc").read_bytes()).row(318)
        vehicle_seat_template = Wdbc((baseline / "VehicleSeat.dbc").read_bytes()).row(1541)
    records = []
    for index, mount in enumerate(mounts):
        spell_id = ids["spell"][index]
        spell_icon_id = ids["spell_icon"][index]
        item_id = ids["item"][index]
        item_display_id = ids["item_display"][index]
        creature_id = ids["creature"][index]
        display_id = ids["display"][index]
        model_id = ids["model"][index]

        is_flying_mount = _is_flying_mount(mount.model.stem)
        spell = list(flying_spell_template if is_flying_mount else spell_template)
        spell[0] = spell_id
        spell[133] = spell_icon_id
        spell[110] = creature_id
        _blank_spell_strings(spell)
        spell[152], spell[169], spell[186], spell[203] = 16712190, 0, 16712190, 16712188

        item = list(item_template)
        item[0] = item_id
        item[5] = item_display_id

        item_display = [item_display_id] + [0] * 24
        creature_display = [display_id, model_id, 0, 0, f32(1), 255, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
        texture_variations = _mount_texture_variation_paths(mount)
        min_x, min_y, min_z, max_x, max_y, max_z, width = _m2_bounds(mount.model.read_bytes())
        height = max(1.0, min(8.0, max_z - min_z))
        model = [
            model_id, 1027, 0, 0, f32(1), 3, 4, f32(18), f32(12), f32(1), 0, 0, 0, 2694,
            f32(width), f32(height), f32(max(0.5, min(4.0, height * 0.45))),
            f32(min_x), f32(min_y), f32(min_z), f32(max_x), f32(max_y), f32(max_z),
            f32(1), f32(1), 0, 0, 0,
        ]
        vehicle_row = None
        vehicle_seat_row = None
        if mount.vehicle_id is not None:
            if mount.vehicle_seat_id is None or vehicle_template is None or vehicle_seat_template is None:
                raise ValueError(f"incomplete vehicle data for mount: {mount.display_name}")
            vehicle = vehicle_template.copy()
            vehicle[0] = mount.vehicle_id
            vehicle = [mount.vehicle_seat_id if value == 2804 else value for value in vehicle]
            seat = vehicle_seat_template.copy()
            seat[0] = mount.vehicle_seat_id
            vehicle_row = tuple(vehicle)
            vehicle_seat_row = tuple(seat)
        records.append(
            MountRecord(
                mount=mount,
                spell_id=spell_id,
                spell_icon_id=spell_icon_id,
                item_id=item_id,
                item_display_id=item_display_id,
                creature_id=creature_id,
                display_id=display_id,
                model_id=model_id,
                spell_row=tuple(spell),
                item_row=tuple(item),
                item_display_row=tuple(item_display),
                creature_display_row=tuple(creature_display),
                texture_variations=tuple(
                    texture_variations[texture_type].stem if texture_type in texture_variations else ""
                    for texture_type in (11, 12, 13)
                ),
                creature_model_row=tuple(model),
                vehicle_row=vehicle_row,
                vehicle_seat_row=vehicle_seat_row,
            )
        )
    return tuple(records)


def build_mount_dbc_entries(records: tuple[MountRecord, ...], baseline: Path | None = None) -> dict[str, bytes]:
    spell_strings: dict[tuple[int, int], str] = {}
    spell_icon_strings: dict[tuple[int, int], str] = {}
    item_display_strings: dict[tuple[int, int], str] = {}
    display_strings: dict[tuple[int, int], str] = {}
    model_strings: dict[tuple[int, int], str] = {}
    for index, record in enumerate(records):
        name = record.mount.display_name
        spell_strings.update({
            (index, 136): name,
            (index, 137): name,
            (index, 170): f"Teaches you how to ride the {name}.",
            (index, 171): f"Teaches you how to ride the {name}.",
            (index, 187): "Increases movement speed by $s2%.",
            (index, 188): "Increases movement speed by $s2%.",
        })
        icon_name = f"INV_Mount_{record.mount.slug}"
        spell_icon_strings[(index, 1)] = f"Interface\\Icons\\{icon_name}"
        item_display_strings[(index, 5)] = icon_name
        for field, value in enumerate(record.texture_variations, 6):
            if value:
                display_strings[(index, field)] = value
        model_strings[(index, 2)] = record.mount.client_model_path
    skill_line_ability_spell_ids = [record.spell_id for record in records]
    for spell_id in LEGACY_CUSTOM_MOUNT_SPELL_IDS:
        if spell_id not in skill_line_ability_spell_ids:
            skill_line_ability_spell_ids.append(spell_id)

    entries = {
        "DBFilesClient/Spell.dbc1-mounts": build_wdbc(
            [list(record.spell_row) for record in records], 234, 936, spell_strings
        ),
        "DBFilesClient/Item.dbc1-mounts": build_wdbc(
            [list(record.item_row) for record in records], 8, 32
        ),
        "DBFilesClient/ItemDisplayInfo.dbc1-mounts": build_wdbc(
            [list(record.item_display_row) for record in records], 25, 100, item_display_strings
        ),
        "DBFilesClient/SpellIcon.dbc1-mounts": build_wdbc(
            [[record.spell_icon_id, 0] for record in records], 2, 8, spell_icon_strings
        ),
        "DBFilesClient/CreatureDisplayInfo.dbc1-mounts": build_wdbc(
            [list(record.creature_display_row) for record in records], 16, 64, display_strings
        ),
        "DBFilesClient/CreatureModelData.dbc1-mounts": build_wdbc(
            [list(record.creature_model_row) for record in records], 28, 112, model_strings
        ),
        "DBFilesClient/SkillLineAbility.dbc1-mounts": build_wdbc(
            [mount_skill_line_ability_row(spell_id) for spell_id in skill_line_ability_spell_ids], 14, 56
        ),
    }
    vehicle_rows = {
        record.mount.vehicle_id: list(record.vehicle_row)
        for record in records
        if record.mount.vehicle_id is not None and record.vehicle_row is not None
    }
    vehicle_seat_rows = {
        record.mount.vehicle_seat_id: list(record.vehicle_seat_row)
        for record in records
        if record.mount.vehicle_seat_id is not None and record.vehicle_seat_row is not None
    }
    if vehicle_rows:
        if baseline is None:
            raise ValueError("baseline is required for standing mount vehicle DBC entries")
        entries["DBFilesClient/Vehicle.dbc1-mounts"] = build_wdbc(
            list(vehicle_rows.values()), 40, 160
        )
        entries["DBFilesClient/VehicleSeat.dbc1-mounts"] = build_wdbc(
            list(vehicle_seat_rows.values()), 58, 232
        )
    return entries


def _sql_quote(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"


def _sql_value(value: object) -> str:
    if isinstance(value, str):
        return _sql_quote(value)
    if isinstance(value, float):
        return f"{value:.9g}"
    return str(value)


def _sql_row(values: list[object] | tuple[object, ...]) -> str:
    return "(" + ", ".join(_sql_value(value) for value in values) + ")"


def _sql_insert(
    table: str,
    columns: tuple[str, ...],
    rows: list[tuple[object, ...]],
    ids: list[int],
    id_column: str = "ID",
    verb: str = "INSERT",
    delete_first: bool = True,
    delete_ids: list[int] | None = None,
) -> str:
    lines = []
    if delete_first:
        ids_to_delete = delete_ids or ids
        lines.append(f"DELETE FROM `{table}` WHERE `{id_column}` IN ({', '.join(map(str, ids_to_delete))});")
    lines.append(f"{verb} INTO `{table}` ({', '.join(f'`{column}`' for column in columns)}) VALUES")
    lines.extend(f"{_sql_row(row)}{',' if index + 1 < len(rows) else ';'}" for index, row in enumerate(rows))
    return "\n".join(lines)


def render_mount_sql(records: tuple[MountRecord, ...]) -> str:
    if not records:
        return ""
    ids = {
        name: [getattr(record, f"{name}_id") for record in records]
        for name in ("spell", "item", "item_display", "creature", "display", "model")
    }
    spell_columns = (
        "ID", "Mechanic", "Attributes", "AttributesEx4", "AttributesEx6", "AttributesEx7", "CastingTimeIndex", "InterruptFlags",
        "AuraInterruptFlags", "ProcChance", "SpellLevel", "DurationIndex", "RangeIndex", "EquippedItemClass", "Effect_1", "Effect_2",
        "Effect_3", "EffectDieSides_1", "EffectDieSides_2", "EffectDieSides_3", "EffectBasePoints_1", "EffectBasePoints_2", "EffectBasePoints_3", "ImplicitTargetA_1",
        "ImplicitTargetA_2", "EffectAura_1", "EffectAura_2", "EffectAura_3", "EffectMiscValue_1", "EffectTriggerSpell_1", "SpellVisualID_1", "SpellIconID",
        "Name_Lang_enUS", "Name_Lang_enGB", "Name_Lang_Mask", "Description_Lang_enUS", "Description_Lang_enGB",
        "Description_Lang_Mask", "AuraDescription_Lang_enUS", "AuraDescription_Lang_enGB", "AuraDescription_Lang_Mask",
        "StartRecoveryCategory", "EffectChainAmplitude_1", "EffectChainAmplitude_2", "EffectChainAmplitude_3", "SchoolMask",
    )
    spell_rows = []
    for record in records:
        row = record.spell_row
        is_flying_mount = _is_flying_mount(record.mount.model.stem)
        spell_rows.append((
            record.spell_id, row[3], row[4], row[8] if is_flying_mount else 0, row[10], row[11], row[28], row[31],
            row[32] if is_flying_mount else 0, row[35], row[39], row[40], row[46], _i32_from_u32(row[68]),
            row[71], row[72], row[73] if is_flying_mount else 0, row[74], row[75], row[76] if is_flying_mount else 0,
            row[80], row[81], row[82] if is_flying_mount else 0, row[86], row[87], row[95], row[96],
            row[97] if is_flying_mount else 0, record.creature_id, row[116] if is_flying_mount else 0, row[131], row[133], record.mount.display_name,
            record.mount.display_name, 16712190, f"Teaches you how to ride the {record.mount.display_name}.",
            f"Teaches you how to ride the {record.mount.display_name}.", 16712190, "Increases movement speed by $s2%.",
            "Increases movement speed by $s2%.", 16712188, row[205], _f32_from_u32(row[216]), _f32_from_u32(row[217]),
            _f32_from_u32(row[218]), row[225],
        ))
    skill_line_ability_columns = (
        "ID", "SkillLine", "Spell", "RaceMask", "ClassMask", "ExcludeRace", "ExcludeClass",
        "MinSkillLineRank", "SupercededBySpell", "AcquireMethod", "TrivialSkillLineRankHigh",
        "TrivialSkillLineRankLow", "CharacterPoints1", "CharacterPoints2",
    )
    skill_line_ability_rows = [
        tuple(mount_skill_line_ability_row(record.spell_id))
        for record in records
    ]
    item_columns = (
        "ID", "ClassID", "SubclassID", "Sound_Override_Subclassid", "Material", "DisplayInfoID", "InventoryType", "SheatheType",
    )
    item_rows = [
        (row[0], row[1], row[2], _i32_from_u32(row[3]), row[4], row[5], row[6], row[7])
        for row in (record.item_row for record in records)
    ]
    item_display_columns = (
        "ID", "ModelName_1", "ModelName_2", "ModelTexture_1", "ModelTexture_2", "InventoryIcon_1", "InventoryIcon_2",
        "GeosetGroup_1", "GeosetGroup_2", "GeosetGroup_3", "Flags", "SpellVisualID", "GroupSoundIndex", "HelmetGeosetVis_1",
        "HelmetGeosetVis_2", "Texture_1", "Texture_2", "Texture_3", "Texture_4", "Texture_5", "Texture_6", "Texture_7",
        "Texture_8", "ItemVisual", "ParticleColorID",
    )
    item_display_rows = [
        (
            record.item_display_id, "", "", "", "", f"INV_Mount_{record.mount.slug}", "", 0, 0, 0, 0, 0, 10,
            0, 0, "", "", "", "", "", "", "", "", 0, 0,
        )
        for record in records
    ]
    display_columns = (
        "ID", "ModelID", "SoundID", "ExtendedDisplayInfoID", "CreatureModelScale", "CreatureModelAlpha", "TextureVariation_1",
        "TextureVariation_2", "TextureVariation_3", "PortraitTextureName", "BloodLevel", "BloodID", "NPCSoundID", "ParticleColorID",
        "CreatureGeosetData", "ObjectEffectPackageID",
    )
    display_rows = [
        (
            record.display_id, record.model_id, 0, 0, _f32_from_u32(record.creature_display_row[4]), 255,
            record.texture_variations[0], record.texture_variations[1], record.texture_variations[2],
            "", 1, 0, 0, 0, 0, 0,
        )
        for record in records
    ]
    model_columns = (
        "ID", "Flags", "ModelName", "SizeClass", "ModelScale", "BloodID", "FootprintTextureID", "FootprintTextureLength",
        "FootprintTextureWidth", "FootprintParticleScale", "FoleyMaterialID", "FootstepShakeSize", "DeathThudShakeSize", "SoundID",
        "CollisionWidth", "CollisionHeight", "MountHeight", "GeoBoxMinX", "GeoBoxMinY", "GeoBoxMinZ", "GeoBoxMaxX", "GeoBoxMaxY",
        "GeoBoxMaxZ", "WorldEffectScale", "AttachedEffectScale", "MissileCollisionRadius", "MissileCollisionPush", "MissileCollisionRaise",
    )
    model_rows = []
    for record in records:
        row = record.creature_model_row
        model_rows.append((
            record.model_id, row[1], record.mount.client_model_path, row[3], _f32_from_u32(row[4]), row[5], row[6],
            _f32_from_u32(row[7]), _f32_from_u32(row[8]), _f32_from_u32(row[9]), row[10], row[11], row[12], row[13],
            _f32_from_u32(row[14]), _f32_from_u32(row[15]), _f32_from_u32(row[16]), _f32_from_u32(row[17]), _f32_from_u32(row[18]),
            _f32_from_u32(row[19]), _f32_from_u32(row[20]), _f32_from_u32(row[21]), _f32_from_u32(row[22]), _f32_from_u32(row[23]),
            _f32_from_u32(row[24]), row[25], row[26], row[27],
        ))
    creature_template_model_columns = (
        "CreatureID", "Idx", "CreatureDisplayID", "DisplayScale", "Probability", "VerifiedBuild",
    )
    creature_template_model_rows = [
        (record.creature_id, 0, record.display_id, 1, 1, 51831)
        for record in records
    ]
    creature_template_columns = (
        "entry", "name", "IconName", "minlevel", "maxlevel", "exp", "faction", "npcflag", "rank", "dmgschool",
        "BaseAttackTime", "RangeAttackTime", "unit_class", "unit_flags", "unit_flags2", "type", "type_flags", "lootid",
        "skinloot", "VehicleId", "AIName", "MovementType", "HoverHeight", "ExperienceModifier", "RacialLeader",
        "movementId", "RegenHealth", "flags_extra", "ScriptName",
    )
    creature_template_rows = [
        (
            record.creature_id, record.mount.display_name, "", 1, 2, 0, 35, 0, 0, 0, 2000, 2000, 1, 0, 2048, 1,
            0, 0, 0, record.mount.vehicle_id or 0, "", 0, 1, 1, 0, 140, 1, 2, "",
        )
        for record in records
    ]
    creature_model_info_columns = (
        "DisplayID", "BoundingRadius", "CombatReach", "Gender", "DisplayID_Other_Gender", "VerifiedBuild",
    )
    creature_model_info_rows = [
        (
            record.display_id,
            max(0.5, _f32_from_u32(record.creature_model_row[14])),
            max(1.0, _f32_from_u32(record.creature_model_row[15])),
            2,
            0,
            51831,
        )
        for record in records
    ]
    item_template_columns = (
        "entry", "class", "subclass", "SoundOverrideSubclass", "name", "displayid", "Quality", "Flags", "FlagsExtra", "BuyCount",
        "BuyPrice", "SellPrice", "InventoryType", "AllowableClass", "AllowableRace", "ItemLevel", "RequiredLevel", "RequiredSkill",
        "RequiredSkillRank", "maxcount", "stackable", "ContainerSlots", "bonding", "description", "Material", "sheath", "RandomProperty",
        "RandomSuffix", "block", "itemset", "MaxDurability", "area", "Map", "BagFamily", "TotemCategory", "duration",
        "ItemLimitCategory", "HolidayId", "ScriptName", "DisenchantID", "FoodType", "minMoneyLoot", "maxMoneyLoot", "flagsCustom",
        "VerifiedBuild", "spellid_1", "spelltrigger_1", "spellcharges_1", "spellppmRate_1", "spellcooldown_1", "spellcategory_1",
        "spellcategorycooldown_1", "spellid_2", "spelltrigger_2", "spellcharges_2", "spellppmRate_2", "spellcooldown_2", "spellcategory_2",
        "spellcategorycooldown_2",
    )
    item_template_rows = []
    for record in records:
        values = {column: 0 for column in item_template_columns}
        values.update({
            "entry": record.item_id,
            "class": 15,
            "subclass": 5,
            "SoundOverrideSubclass": -1,
            "name": f"Reins of the {record.mount.display_name}",
            "displayid": record.item_display_id,
            "Quality": 4,
            "BuyCount": 1,
            "AllowableClass": 262143,
            "AllowableRace": -1,
            "ItemLevel": 80,
            "RequiredLevel": 40,
            "RequiredSkill": 762,
            "RequiredSkillRank": 150,
            "maxcount": 1,
            "stackable": 1,
            "bonding": 1,
            "description": f"Teaches you how to ride the {record.mount.display_name}.",
            "Material": 4,
            "BagFamily": 128,
            "ScriptName": "",
            "VerifiedBuild": 12340,
            "spellid_1": 483,
            "spellcharges_1": -1,
            "spellcooldown_1": -1,
            "spellcategory_1": 330,
            "spellcategorycooldown_1": 3000,
            "spellid_2": record.spell_id,
            "spelltrigger_2": 6,
        })
        item_template_rows.append(tuple(values[column] for column in item_template_columns))
    vehicle_columns = (
        "ID", "Flags", "TurnSpeed", "PitchSpeed", "PitchMin", "PitchMax", "SeatID_1", "SeatID_2", "SeatID_3",
        "SeatID_4", "SeatID_5", "SeatID_6", "SeatID_7", "SeatID_8", "MouseLookOffsetPitch", "CameraFadeDistScalarMin",
        "CameraFadeDistScalarMax", "CameraPitchOffset", "FacingLimitRight", "FacingLimitLeft", "MsslTrgtTurnLingering",
        "MsslTrgtPitchLingering", "MsslTrgtMouseLingering", "MsslTrgtEndOpacity", "MsslTrgtArcSpeed", "MsslTrgtArcRepeat",
        "MsslTrgtArcWidth", "MsslTrgtImpactRadius_1", "MsslTrgtImpactRadius_2", "MsslTrgtArcTexture", "MsslTrgtImpactTexture",
        "MsslTrgtImpactModel_1", "MsslTrgtImpactModel_2", "CameraYawOffset", "UilocomotionType", "MsslTrgtImpactTexRadius",
        "VehicleUIIndicatorID", "PowerDisplayID_1", "PowerDisplayID_2", "PowerDisplayID_3",
    )
    vehicle_rows = {
        record.mount.vehicle_id: _vehicle_sql_row(record.vehicle_row)
        for record in records
        if record.mount.vehicle_id is not None and record.vehicle_row is not None
    }
    vehicle_seat_columns = (
        "ID", "Flags", "AttachmentID", "AttachmentOffsetX", "AttachmentOffsetY", "AttachmentOffsetZ", "EnterPreDelay",
        "EnterSpeed", "EnterGravity", "EnterMinDuration", "EnterMaxDuration", "EnterMinArcHeight", "EnterMaxArcHeight",
        "EnterAnimStart", "EnterAnimLoop", "RideAnimStart", "RideAnimLoop", "RideUpperAnimStart", "RideUpperAnimLoop",
        "ExitPreDelay", "ExitSpeed", "ExitGravity", "ExitMinDuration", "ExitMaxDuration", "ExitMinArcHeight", "ExitMaxArcHeight",
        "ExitAnimStart", "ExitAnimLoop", "ExitAnimEnd", "PassengerYaw", "PassengerPitch", "PassengerRoll", "PassengerAttachmentID",
        "VehicleEnterAnim", "VehicleExitAnim", "VehicleRideAnimLoop", "VehicleEnterAnimBone", "VehicleExitAnimBone",
        "VehicleRideAnimLoopBone", "VehicleEnterAnimDelay", "VehicleExitAnimDelay", "VehicleAbilityDisplay", "EnterUISoundID",
        "ExitUISoundID", "UiSkin", "FlagsB", "CameraEnteringDelay", "CameraEnteringDuration", "CameraExitingDelay",
        "CameraExitingDuration", "CameraOffsetX", "CameraOffsetY", "CameraOffsetZ", "CameraPosChaseRate", "CameraFacingChaseRate",
        "CameraEnteringZoom", "CameraSeatZoomMin", "CameraSeatZoomMax",
    )
    vehicle_seat_rows = {
        record.mount.vehicle_seat_id: _vehicle_seat_sql_row(record.vehicle_seat_row)
        for record in records
        if record.mount.vehicle_seat_id is not None and record.vehicle_seat_row is not None
    }
    blocks = [
        _sql_insert(
            "creature_model_info",
            creature_model_info_columns,
            creature_model_info_rows,
            ids["display"],
            "DisplayID",
            "REPLACE",
            False,
        ),
        _sql_insert(
            "creature_template_model", creature_template_model_columns, creature_template_model_rows, ids["creature"],
            "CreatureID",
        ),
        _sql_insert(
            "creature_template",
            creature_template_columns,
            creature_template_rows,
            ids["creature"],
            "entry",
            "REPLACE",
            False,
        ),
        _sql_insert("spell_dbc", spell_columns, spell_rows, ids["spell"]),
        _sql_insert("skilllineability_dbc", skill_line_ability_columns, skill_line_ability_rows, ids["spell"]),
        _sql_insert("item_dbc", item_columns, item_rows, ids["item"]),
        _sql_insert(
            "itemdisplayinfo_dbc", item_display_columns, item_display_rows, ids["item_display"],
            delete_ids=sorted(set(ids["item_display"]) | set(LEGACY_MOUNT_IDS["item_display"])),
        ),
        _sql_insert(
            "creaturedisplayinfo_dbc", display_columns, display_rows, ids["display"],
            delete_ids=sorted(set(ids["display"]) | set(LEGACY_MOUNT_IDS["display"])),
        ),
        _sql_insert(
            "creaturemodeldata_dbc", model_columns, model_rows, ids["model"],
            delete_ids=sorted(set(ids["model"]) | set(LEGACY_MOUNT_IDS["model"])),
        ),
        _sql_insert("item_template", item_template_columns, item_template_rows, ids["item"], "entry", "REPLACE", False),
    ]
    if vehicle_rows:
        blocks.extend((
            _sql_insert("vehicle_dbc", vehicle_columns, list(vehicle_rows.values()), sorted(vehicle_rows)),
            _sql_insert("vehicleseat_dbc", vehicle_seat_columns, list(vehicle_seat_rows.values()), sorted(vehicle_seat_rows)),
        ))
    return "\n\n".join(blocks) + "\n"


def read_archive(storm: Storm, path: Path) -> dict[str, bytes]:
    archive = storm.open_archive(path)
    try:
        return {name: storm.read(archive, name) for name, *_ in storm.list_files(archive)}
    finally:
        storm.dll.SFileCloseArchive(archive)


def extract_archive(storm: Storm, source: Path, destination: Path) -> dict[str, bytes]:
    archive = storm.open_archive(source)
    try:
        files = storm.list_files(archive)
        result = {}
        for name, expected, _, _ in files:
            payload = storm.read(archive, name)
            if len(payload) != expected:
                raise ValueError(f"size mismatch in {source.name}: {name}")
            relative = safe_relative(name)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            result[name.casefold()] = payload
        return result
    finally:
        storm.dll.SFileCloseArchive(archive)


def read_archive_entry(storm: Storm, path: Path, entry_name: str) -> bytes:
    archive = storm.open_archive(path)
    try:
        key = next((name for name, *_ in storm.list_files(archive) if name.casefold() == entry_name.casefold()), None)
        if key is None:
            raise FileNotFoundError(f"{entry_name} not found in {path}")
        return storm.read(archive, key)
    finally:
        storm.dll.SFileCloseArchive(archive)


def merge_wxl_manifest(existing: bytes, additions: bytes) -> bytes:
    lines = existing.decode("utf-8").splitlines() if existing else []
    seen = {line.casefold() for line in lines if line and not line.startswith("#")}
    for line in additions.decode("utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        if line.casefold() not in seen:
            lines.append(line)
            seen.add(line.casefold())
    return ("\n".join(lines).rstrip("\n") + "\n").encode("utf-8")


@dataclass(frozen=True)
class Car:
    slug: str
    display_name: str
    source: str
    spell: int
    item: int
    creature: int
    display: int
    model: int
    item_display: int
    spell_icon: int
    vehicle: int
    seat: int
    model_name: str
    primary: str
    secondary: str | None
    glow: str | None
    reflection: str | None
    water: str | None


CARS = (
    Car("Bentley", "Bentley Continental GT", "Patch-B.mpq", 200101, 900137, 3460604, 94229, 4892, 134239, 514642, 900301, 900401, "Bentley", "CREATURE\\Motorcyclevehicle\\MotorcycleVehicle_Alliance01.BLP", None, None, "CarAssets\\CarReflection01.blp", None),
    Car("Ferrari", "Ferrari Enzo", "Patch-F.mpq", 200102, 900138, 3460605, 94230, 4893, 134240, 514643, 900302, 900402, "Ferrari", "CREATURE\\Motorcyclevehicle\\MotorcycleVehicle_Alliance01.BLP", "CREATURE\\Motorcyclevehicle\\MotorcycleVehicle_Alliance02.BLP", None, "CarAssets\\CarReflection02.blp", None),
    Car("NissanSkylineR34", "Nissan Skyline GT-R R34", "Patch-S.mpq", 200103, 900139, 3460606, 94231, 4894, 134241, 514644, 900303, 900403, "NissanR34", "CREATURE\\Motorcyclevehicle\\MotorcycleVehicle_Alliance01.BLP", "CREATURE\\Motorcyclevehicle\\MotorcycleVehicle_Alliance02.BLP", None, "CarAssets\\CarReflection01.blp", None),
    Car("Lamborghini", "Lamborghini Aventador", "Patch-L.mpq", 200104, 900140, 3460607, 94232, 4895, 134242, 514645, 900304, 900404, "Lamborghini", "Creature\\GoblinHotRod\\GoblinHotrod_01.blp", "Creature\\GoblinHotRod\\GoblinHotrod_02.blp", "Creature\\GoblinHotRod\\GoblinHotrod_02glow.blp", None, "Creature\\GoblinHotRod\\T_VFX_WATER3B.blp"),
)


def extracted_lookup(directory: Path) -> dict[str, Path]:
    return {
        str(path.relative_to(directory)).replace(os.sep, "\\").casefold(): path
        for path in directory.rglob("*")
        if path.is_file()
    }


def read_extracted(lookup: dict[str, Path], name: str) -> bytes:
    try:
        return lookup[name.casefold()].read_bytes()
    except KeyError as exc:
        raise FileNotFoundError(name) from exc


def car_texture_namespace(car: Car) -> str:
    return f"Creature\\Cars\\{car.slug}\\"


def build_client_entries(extracted: dict[str, dict[str, Path]], baseline: Path) -> tuple[dict[str, bytes], dict[str, list[int]]]:
    bases = {name: Wdbc((baseline / name).read_bytes()) for name in ("Vehicle.dbc", "VehicleSeat.dbc")}
    vehicle_base = bases["Vehicle.dbc"].row(318)
    seat_base = bases["VehicleSeat.dbc"].row(2804)
    entries: dict[str, bytes] = {}
    ids = {"vehicle": [], "seat": []}
    continuation_rows: dict[str, list[list[int]]] = {name: [] for name in ("Spell", "Item", "ItemDisplayInfo", "SpellIcon", "CreatureDisplayInfo", "CreatureModelData", "SkillLineAbility", "Vehicle", "VehicleSeat")}
    continuation_strings: dict[str, dict[tuple[int, int], str]] = {name: {} for name in continuation_rows}

    support = extracted["Patch-L.mpq"]
    support_secondary = read_extracted(support, "Creature\\GoblinHotRod\\GoblinHotrod_02.blp")
    support_glow = read_extracted(support, "Creature\\GoblinHotRod\\GoblinHotrod_02glow.blp")
    shared_sounds: dict[str, bytes] = {}

    for car_index, car in enumerate(CARS):
        lookup = extracted[car.source]
        model = read_extracted(lookup, "CREATURE\\Motorcyclevehicle\\motorcyclevehicle.m2")
        source_model_name = model[304 : 304 + struct.unpack_from("<I", model, 8)[0]].rstrip(b"\0")
        texture_code = car.slug[0].upper()
        tex_dir = car_texture_namespace(car)
        model_path = f"{tex_dir}{car.slug}.m2"
        texture_01 = f"{texture_code}01"
        texture_02 = f"{texture_code}02"
        texture_glow = f"{texture_code}02Glow"
        replacements = {
            source_model_name: car.model_name.encode("ascii"),
            b"CREATURE\\GOBLINHOTROD\\GOBLINHOTROD_01.BLP": f"{tex_dir}{texture_01}.BLP".encode("ascii"),
            b"CREATURE\\GOBLINHOTROD\\GOBLINHOTROD_02.BLP": f"{tex_dir}{texture_02}.BLP".encode("ascii"),
            b"CREATURE\\GOBLINHOTROD\\GOBLINHOTROD_02GLOW.BLP": f"{tex_dir}{texture_glow}.BLP".encode("ascii"),
        }
        reflection_path = f"Creature\\CarAssets\\{car.slug[0]}\\R.BLP"
        if car.reflection:
            reflection_name = b"CarAssets\\CarReflection01.BLP" if "01" in car.reflection else b"CarAssets\\CarReflection02.BLP"
            replacements[reflection_name] = reflection_path.encode("ascii")
        if car.water:
            replacements[b"CREATURE\\GOBLINHOTROD\\T_VFX_WATER3B.BLP"] = f"{tex_dir}Water.BLP".encode("ascii")
        model = rewrite_m2_paths(model, replacements)
        entries[model_path] = model
        entries[f"Creature\\Cars\\{car.slug}\\{car.slug}00.skin"] = read_extracted(lookup, "CREATURE\\Motorcyclevehicle\\motorcyclevehicle00.skin")

        def add_texture(destination: str, source_name: str | None, fallback: bytes | None = None):
            payload = fallback if source_name is None else read_extracted(lookup, source_name)
            if payload is None:
                raise FileNotFoundError(f"no texture for {car.slug}: {destination}")
            entries[destination] = payload

        add_texture(f"{tex_dir}{texture_01}.BLP", car.primary)
        add_texture(f"{tex_dir}{texture_02}.BLP", car.secondary, support_secondary)
        add_texture(f"{tex_dir}{texture_glow}.BLP", car.glow, support_glow)
        if car.reflection:
            entries[reflection_path] = read_extracted(lookup, car.reflection)
        if car.water:
            entries[f"{tex_dir}Water.blp"] = read_extracted(lookup, car.water)
        icon_slug = "NissanR34" if car.slug == "NissanSkylineR34" else car.slug
        icon_name = f"INV_Misc_Key_{icon_slug}"
        entries[f"Interface\\Icons\\{icon_name}.blp"] = read_extracted(lookup, "Interface\\Icons\\INV_Misc_Key_14.blp")

        for source_name, _, _, _ in [item for item in ((key, 0, 0, 0) for key in lookup) if "sound\\vehicles\\motorcyclevehicle\\" in item[0]]:
            shared_sounds[source_name] = read_extracted(lookup, source_name)

        spell = [0] * 234
        spell[0], spell[3], spell[4], spell[10], spell[11] = car.spell, 21, 269582608, 131072, 256
        spell[28], spell[31], spell[35], spell[39], spell[40], spell[46] = 16, 31, 101, 1, 21, 1
        spell[68] = 0xFFFFFFFF
        spell[71:73] = [6, 6]
        spell[74:76] = [1, 1]
        spell[80:82] = [0xFFFFFFFF, 159]
        spell[86:88] = [1, 1]
        spell[95:97] = [78, 32]
        spell[110] = car.creature
        spell[131], spell[133] = 14418, car.spell_icon
        for field in (152, 186, 203):
            spell[field] = 16712190
        spell[205], spell[216], spell[217], spell[218], spell[225] = 330, 1, 1, 1, 1
        name = car.display_name
        description = f"Rides and parks your {name}.  This is a very fast set of wheels."
        aura = "Increases movement speed by $s2%."
        continuation_rows["Spell"].append(spell)
        continuation_rows["SkillLineAbility"].append(mount_skill_line_ability_row(car.spell))
        for field, value in ((136, name), (137, name), (170, description), (171, description), (187, aura), (188, aura)):
            continuation_strings["Spell"][(car_index, field)] = value

        continuation_rows["Item"].append([car.item, 15, 5, 0xFFFFFFFF, 4, car.item_display, 0, 0])
        item_icon = icon_name
        item_display = [car.item_display, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        continuation_rows["ItemDisplayInfo"].append(item_display)
        continuation_strings["ItemDisplayInfo"][(car_index, 5)] = item_icon
        continuation_rows["SpellIcon"].append([car.spell_icon, 0])
        continuation_strings["SpellIcon"][(car_index, 1)] = f"Interface\\Icons\\{item_icon}"

        creature_display = [car.display, car.model, 0, 0, f32(1.0), 255, 0, 0, 0, 0, 1, 0, 0, 0, 0, 161]
        continuation_rows["CreatureDisplayInfo"].append(creature_display)
        for field, value in ((6, texture_01), (7, texture_02), (8, texture_glow)):
            continuation_strings["CreatureDisplayInfo"][(car_index, field)] = value

        model_row = [car.model, 1027, 0, 0, f32(1), 3, 4, f32(18), f32(12), f32(1), 0, 0, 0, 2694, f32(0.6111), f32(2.031), f32(0.762392), f32(-1.922838), f32(-0.779004), f32(-0.074658), f32(2.814294), f32(1.031971), f32(2.075215), f32(1), f32(1), 0, 0, 0]
        continuation_rows["CreatureModelData"].append(model_row)
        continuation_strings["CreatureModelData"][(car_index, 2)] = model_path

        vehicle = vehicle_base.copy()
        vehicle[0] = car.vehicle
        vehicle = [car.seat if value == 2804 else value for value in vehicle]
        continuation_rows["Vehicle"].append(vehicle)
        seat = seat_base.copy()
        seat[0] = car.seat
        continuation_rows["VehicleSeat"].append(seat)
        ids["vehicle"].append(car.vehicle)
        ids["seat"].append(car.seat)

        for name in lookup:
            if name.endswith(".blp") and ("horde01" in name or "horde02" in name):
                entries[f"Creature\\Cars\\{car.slug}\\{Path(name.replace('\\\\', '/')).name}" ] = read_extracted(lookup, name)

    for name, payload in shared_sounds.items():
        entries[name.replace("/", "\\")] = payload

    manifest = [f"DBFilesClient/{name}.dbc1-cars" for name in continuation_rows]
    entries["wxl-dbc.manifest"] = ("# Esteria additive car mounts\n" + "\n".join(manifest) + "\n").encode("utf-8")
    dbc_specs = {
        "Spell": (234, 936), "Item": (8, 32), "ItemDisplayInfo": (25, 100), "SpellIcon": (2, 8),
        "CreatureDisplayInfo": (16, 64), "CreatureModelData": (28, 112), "SkillLineAbility": (14, 56),
        "Vehicle": (40, 160), "VehicleSeat": (58, 232),
    }
    for name, rows in continuation_rows.items():
        fields, size = dbc_specs[name]
        entries[f"DBFilesClient/{name}.dbc1-cars"] = build_wdbc(rows, fields, size, continuation_strings[name])
    return entries, ids


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE_DEFAULT)
    parser.add_argument("--repo", type=Path, default=REPO_DEFAULT)
    parser.add_argument("--baseline", type=Path, default=Path(os.environ.get("TEMP", "C:/Windows/Temp")) / "esteria-cars-preflight")
    parser.add_argument("--stormlib", type=Path, default=DLL_DEFAULT)
    parser.add_argument("--mount-root", type=Path, action="append", dest="mount_roots")
    parser.add_argument("--archive", type=Path)
    parser.add_argument(
        "--output-sql",
        type=Path,
        default=Path(
            "modules/mod-custom-server/data/sql/db-world/updates/"
            "u_custom_server_2026_09_09_03_card_gameboy_mount_variants.sql"
        ),
    )
    parser.add_argument("--report", type=Path, default=Path("var/mount-build/mounts_summary.json"))
    args = parser.parse_args()

    if not args.stormlib.is_file():
        raise FileNotFoundError(args.stormlib)
    extracted_root = args.source / "Extracted"
    extracted_root.mkdir(parents=True, exist_ok=True)
    work_root = args.repo / "var" / "cars-mount-build"
    work_root.mkdir(parents=True, exist_ok=True)
    mount_work_root = args.repo / "var" / "mount-build"
    mount_work_root.mkdir(parents=True, exist_ok=True)
    storm = Storm(args.stormlib)
    extracted: dict[str, dict[str, Path]] = {}
    source_summary = {}
    for car in CARS:
        source = args.source / car.source
        destination = extracted_root / Path(car.source).stem
        archive_data = extract_archive(storm, source, destination)
        extracted[car.source] = extracted_lookup(destination)
        source_summary[car.source] = {"entries": len(archive_data), "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}

    car_entries, car_ids = build_client_entries(extracted, args.baseline)
    car_manifest = car_entries.pop("wxl-dbc.manifest")
    archive_path = args.archive or args.repo / "3.3.5a - Dev" / "Data" / "PATCH-X.MPQ"
    existing_entries = read_archive(storm, archive_path) if archive_path.is_file() else {}
    car_dbc_names = {name.casefold() for name in car_entries if name.casefold().startswith("dbfilesclient/")}
    native_dbc_names = {
        f"DBFilesClient\\{table}.dbc".casefold()
        for table in NATIVE_DBC_TABLES
    }
    native_continuation_names = {
        f"DBFilesClient/{table}.dbc1-cars".casefold()
        for table in NATIVE_DBC_TABLES
    }
    existing_for_merge = {
        name: payload
        for name, payload in remove_existing_mount_entries(existing_entries).items()
        if name.casefold() not in car_dbc_names
        and name.casefold() not in native_dbc_names
        and name.casefold() not in native_continuation_names
    }
    car_entries_for_archive = {
        name: payload
        for name, payload in car_entries.items()
        if name.casefold() not in native_continuation_names
    }
    merged = merge_archive_entries(existing_for_merge, car_entries_for_archive)

    mount_roots = tuple(args.mount_roots or MOUNT_SOURCE_DEFAULTS)
    mounts = discover_mounts(mount_roots)
    rejected = rejected_models(mount_roots)
    if len(mounts) != 89:
        raise ValueError(f"expected 89 WotLK mounts, discovered {len(mounts)}")
    if len(rejected) != 3:
        raise ValueError(f"expected 3 rejected non-WotLK models, discovered {len(rejected)}")
    mounts = expand_mount_variants(mounts)
    if len(mounts) != 111:
        raise ValueError(f"expected 111 WotLK mounts with requested variants, discovered {len(mounts)}")
    records = build_mount_records(mounts, args.baseline)
    default_mount_icon = read_archive_entry(
        storm, args.repo / DEFAULT_MOUNT_ICON_SOURCE, DEFAULT_MOUNT_ICON_ENTRY
    )
    mount_asset_entries: dict[str, bytes] = {}
    for mount in mounts:
        mount_asset_entries = merge_archive_entries(
            mount_asset_entries, collect_mount_entries(mount, default_icon=default_mount_icon)
        )
    mount_dbc_entries = build_mount_dbc_entries(records, args.baseline)
    merged = merge_archive_entries(merged, mount_asset_entries)
    combined_dbc_entries: dict[str, bytes] = {}
    for mount_name, payload in mount_dbc_entries.items():
        car_name = mount_name.replace(".dbc1-mounts", ".dbc1-cars")
        table_name = mount_name.split("/", 1)[1].split(".dbc1-", 1)[0]
        combined_dbc_entries[car_name] = merge_wdbc_continuations(car_entries[car_name], payload, table_name)
    non_native_continuations = {
        name: payload
        for name, payload in combined_dbc_entries.items()
        if name.casefold() not in native_continuation_names
    }
    non_native_names = {name.casefold() for name in non_native_continuations}
    merged = {name: payload for name, payload in merged.items() if name.casefold() not in non_native_names}
    merged = merge_archive_entries(merged, non_native_continuations)
    native_dbc_entries = {}
    for table in NATIVE_DBC_TABLES:
        source = args.repo / NATIVE_DBC_SOURCE_DEFAULTS[table]
        continuation_name = f"DBFilesClient/{table}.dbc1-cars"
        native_dbc_entries[f"DBFilesClient\\{table}.dbc"] = merge_wdbc_continuations(
            read_archive_entry(storm, source, f"DBFilesClient\\{table}.dbc"),
            combined_dbc_entries[continuation_name],
            table,
        )
    merged = merge_archive_entries(merged, native_dbc_entries)
    merged["wxl-dbc.manifest"] = merge_wxl_manifest(
        merge_wxl_manifest(existing_entries.get("wxl-dbc.manifest", b""), car_manifest),
        b"",
    )
    merged["wxl-dbc.manifest"] = (
        "\n".join(
            line for line in merged["wxl-dbc.manifest"].decode("utf-8").splitlines()
            if not line.casefold().endswith(".dbc1-mounts")
            and line.casefold() not in native_continuation_names
        ) + "\n"
    ).encode("utf-8")
    merged["(listfile)"] = (
        "\n".join(sorted(name for name in merged if name not in {"(listfile)", "(attributes)"})) + "\n"
    ).encode("utf-8")

    temp_archive = mount_work_root / "PATCH-X.with-mounts.MPQ"
    if temp_archive.exists():
        temp_archive.unlink()
    archive_entries = {name: payload for name, payload in merged.items() if name not in {"(listfile)", "(attributes)"}}
    storm.create_archive(temp_archive, archive_entries)
    check = storm.open_archive(temp_archive)
    try:
        listed = {name.casefold() for name, *_ in storm.list_files(check)}
        verification_entries = merge_archive_entries(
            merge_archive_entries(mount_asset_entries, native_dbc_entries),
            non_native_continuations,
        )
        for name, payload in verification_entries.items():
            if name.casefold() not in listed:
                raise AssertionError(f"missing packaged mount entry: {name}")
            if name.casefold().endswith(".m2") and m2_version(payload) != WOTLK_MODEL_VERSION:
                raise AssertionError(f"non-WotLK model packaged: {name}")
        required_native = {name.casefold().replace("\\", "/") for name in native_dbc_entries}
        listed_native = {
            name.casefold().replace("\\", "/")
            for name in listed
            if name.casefold().replace("\\", "/").startswith("dbfilesclient/")
            and name.casefold().endswith(".dbc")
        }
        if not required_native.issubset(listed_native):
            raise AssertionError("missing native DBC file")
        manifest = merged["wxl-dbc.manifest"].decode("utf-8").casefold()
        if any(line.endswith(".dbc1-mounts") for line in manifest.splitlines()):
            raise AssertionError("manifest still lists mount continuations")
        if b"DBFilesClient/Spell.dbc1-cars" in merged["wxl-dbc.manifest"]:
            raise AssertionError("manifest still lists native DBC continuations")
    finally:
        storm.dll.SFileCloseArchive(check)

    if archive_path.is_file():
        existing_hash = hashlib.sha256(archive_path.read_bytes()).hexdigest()
        backup = mount_work_root / f"PATCH-X-before-mounts-{existing_hash[:12]}.MPQ"
        if not backup.exists():
            os.replace(archive_path, backup)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    os.replace(temp_archive, archive_path)

    sql_path = args.repo / args.output_sql if not args.output_sql.is_absolute() else args.output_sql
    sql_path.parent.mkdir(parents=True, exist_ok=True)
    sql_path.write_text(render_mount_sql(records), encoding="utf-8", newline="\n")
    report_path = args.repo / args.report if not args.report.is_absolute() else args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    mount_id_rows = mount_ids(mounts, args.baseline)
    mount_summary = []
    for index, mount in enumerate(mounts):
        mount_summary.append({
            "package": mount.package,
            "source_model": str(mount.model),
            "source_relative": str(mount.source_relative),
            "slug": mount.slug,
            "display_name": mount.display_name,
            "model_version": mount.model_version,
            "client_model_path": mount.client_model_path,
            "spell_id": mount_id_rows["spell"][index],
            "spell_icon_id": mount_id_rows["spell_icon"][index],
            "item_id": mount_id_rows["item"][index],
            "item_display_id": mount_id_rows["item_display"][index],
            "creature_id": mount_id_rows["creature"][index],
            "display_id": mount_id_rows["display"][index],
            "model_id": mount_id_rows["model"][index],
        })
    summary = {
        "sources": source_summary,
        "mount_source_roots": [str(root) for root in mount_roots],
        "mount_count": len(mounts),
        "rejected": [{"package": item.package, "model": str(item.model), "version": item.version} for item in rejected],
        "archive": {"path": str(archive_path), "entries": len(merged), "sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest()},
        "car_ids": car_ids,
        "mounts": mount_summary,
        "sql": str(sql_path),
    }
    report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps({"archive": str(archive_path), "entries": len(merged), "mounts": len(mounts), "rejected": len(rejected), "sql": str(sql_path)}, indent=2))


if __name__ == "__main__":
    main()
