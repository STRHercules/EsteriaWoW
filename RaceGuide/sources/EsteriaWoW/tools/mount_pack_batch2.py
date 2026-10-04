"""Build and deploy Esteria mount batch #2 as native 3.3.5a data.

The 71 ready mounts live under ``NewModels/_Mounts``.  Their assets are shipped
in a new ``Patch-W.MPQ``.  This pack deliberately does *not* use WarcraftXL
extended-DBC continuation files: it builds complete native WDBC tables instead.

The developer client already has higher-priority X/Y/Z archives carrying some
of the same DBC paths.  Therefore the native tables are also mirrored into the
existing root and locale Z archives at deploy time, after making byte-for-byte
backups.  Patch-W remains the owner of the batch-2 model/icon assets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import string
from dataclasses import replace
from datetime import datetime
from pathlib import Path

import cars_mount_pack as cars


_ORIGINAL_M2_TEXTURE_RECORDS = cars._m2_texture_records
_ORIGINAL_SOURCE_ASSET_CANDIDATES = cars._source_asset_candidates

REPO = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO / "NewModels" / "_Mounts"
BASELINE = REPO / "DBCs"
STAGE_ROOT = REPO / "var" / "mount-build" / "batch2"
CLIENT_ROOT_DEFAULT = Path(r"G:\3.3.5a - Dev")
STORMLIB_DEFAULT = cars.DLL_DEFAULT
WOTLK_MODEL_VERSION = 264
FLYING_MOUNT_SPELL_TEMPLATE_ID = 32235  # Golden Gryphon: conventional seated flying-mount behavior.

# CreatureDisplayInfo scale corrections. Infernal matches its Legion donor row;
# Kukulkan is a non-WoW donor whose mesh is authored several times larger than
# the surrounding mount set, so it needs an explicit downscale.
DISPLAY_SCALE_OVERRIDES = {
    "infernalmount": 0.9,
    "kukulkan": 0.3,
}

# Named texture aliases carried by source M2 exports. Celestial Cat's type-11
# texture was exported as a FileDataID placeholder; the supplied BLP is the
# exact retail file behind that ID.
TEXTURE_ALIASES = {
    "celestialcatmount": {
        "unknown\\5846547.blp": "CelestialCatMount.blp",
    },
}

ID_BASES = {
    "spell": 201200,
    "spell_icon": 514800,
    "item": 901200,
    "item_display": 68800,
    "creature": 3460800,
    "display": 94500,
    "model": 5100,
}

NATIVE_DBC_TABLES = (
    "Spell",
    "Item",
    "ItemDisplayInfo",
    "SpellIcon",
    "CreatureDisplayInfo",
    "CreatureModelData",
    "SkillLineAbility",
)

EXCLUDED_MODEL_STEMS = {
    "gul'dan",                       # MD21/v274, not WotLK native.
    "slatebackroamer",              # Missing canonical .skin.
    "cape_special_ibelinfox_b_01",  # Ibelin Fox cape component, not a mount.
}

DISPLAY_NAMES = {
    "babymurlocice": "Baby Murloc Ice",
    "batmount_30thanniv": "30th Anniversary Bat",
    "brontosaurusmount2": "Brontosaurus",
    "foxibelinpet": "Ibelin Fox",
    "gryphonmount_30thanniv": "30th Anniversary Gryphon",
    "hippogryphmount_30thanniv": "30th Anniversary Hippogryph",
    "murlocice": "Ice Murloc",
    "windridermount_30thanniv": "30th Anniversary Wind Rider",
    "rostrumstormgryphon_blue": "Storm Gryphon (Blue)",
    "catslimemount": "Cat Slime",
    "celestialcatmount": "Celestial Cat",
    "viciousalliancewolf": "Vicious Alliance Wolf",
    "deathhound": "Deathhound",
    "dreamowl_firemount": "Dream Owl (Fire)",
    "dreamowl_purple_mount": "Dream Owl (Purple)",
    "dreamsaber": "Dream Saber",
    "emeralddreamstag": "Emerald Dream Stag",
    "encrypted06": "Encrypted 06",
    "9fa_fae_soulpod_cart02": "Fae Soulpod Cart",
    "motorcyclefelreavermount": "Fel Reaver Motorcycle",
    "infernalmount": "Infernal",
    "kukulkan": "Kukulkan",
    "magicalfishmount": "Magical Fish",
    "netherwingmount": "Netherwing Drake",
    "blizzardphoenixmount": "Blizzard Phoenix",
    "phoenix2darkwell": "Darkwell Phoenix",
    "ragnarosmount": "Ragnaros",
    "shadebeastflying": "Shadebeast (Flying)",
    "shadebeastmount": "Shadebeast",
    "skeletalwarhorse2": "Skeletal Warhorse",
    "snailrockmount": "Snail Rock",
    "squirrelflyingmount": "Flying Squirrel",
    "jediinterceptor": "Jedi Interceptor",
    "landspeeder": "Landspeeder",
    "razorcrest": "Razor Crest",
    "sithinfiltrator": "Sith Infiltrator",
    "xwing2": "X-Wing",
    "technolope": "Technolope",
    "undeadpaladinmount": "Undead Paladin Charger",
    "undeadpaladinmount_sencilla": "Undead Paladin Charger (Sencilla)",
    "pvpwarhorse2": "PvP Warhorse",
    "wooddragonmount": "Wood Dragon",
}

FLYING_MODEL_STEMS = frozenset({
    "batmount_30thanniv",
    "gryphonmount_30thanniv",
    "hippogryphmount_30thanniv",
    "windridermount_30thanniv",
    "rostrumstormgryphon_blue",
    "dreamowl_firemount",
    "dreamowl_purple_mount",
    "dreamsaber",
    "emeralddreamstag",
    "encrypted06",
    "netherwingmount",
    "blizzardphoenixmount",
    "phoenix2darkwell",
    "shadebeastflying",
    "squirrelflyingmount",
    "wooddragonmount",
    "brontosaurusmount2",
    "kukulkan",
    "catslimemount",
    "magicalfishmount",
    "ragnarosmount",
    "celestialcatmount",
    "technolope",
    "9fa_fae_soulpod_cart02",
    "jediinterceptor",
    "landspeeder",
    "razorcrest",
    "sithinfiltrator",
    "xwing2",
})


def _color_triplet(prefix: str, color: str) -> dict[int, str]:
    lower = color.lower()
    return {
        11: f"{prefix}_{lower}.blp",
        12: f"{prefix}_glow_1_{lower}.blp",
        13: f"{prefix}_glow_2_{lower}.blp",
    }


VARIANT_SPECS = {
    "dreamsaber": tuple(
        (color, _color_triplet("dreamsaber", color))
        for color in ("Blue", "Green", "Purple", "Yellow")
    ),
    "infernalmount": tuple(
        (
            color,
            {
                # Retail CreatureDisplayInfo rows for this model use metal in
                # TextureVariation_1/type 11, rock in _2/type 12, and FX in
                # _3/type 13. The original batch-2 generator had 11/12 swapped.
                11: f"infernalmount_metal_{color.lower()}.blp",
                12: f"infernalmount_rock_{color.lower()}.blp",
                13: f"infernalmount_fx_{('purple' if color == 'Red' else color.lower())}.blp",
            },
        )
        for color in ("Blue", "Green", "Ice", "Lava", "Red")
    ),
    "shadebeastflying": tuple(
        (color, {11: f"shadebeastflying_{color.lower()}.blp"})
        for color in ("Black", "Blue", "Gray", "Orange", "Red")
    ),
    "shadebeastmount": tuple(
        (
            color,
            {
                11: f"shadebeastmount_{color.lower()}.blp",
                12: f"shadebeastmount_armor_{color.lower()}.blp",
            },
        )
        for color in ("Black", "Blue", "Gray", "Orange", "Red")
    ),
    "skeletalwarhorse2": tuple(
        (
            color,
            {
                11: f"skeletalwarhorse2_01_{color.lower()}.blp",
                12: f"skeletalwarhorse2_02_{color.lower()}.blp",
            },
        )
        for color in ("Black", "Brown", "Green", "Midnight", "Purple", "Red", "White")
    ),
    "pvpwarhorse2": (
        ("Alliance", {11: "pvpwarhorse2_alliance_skin.blp", 12: "pvpwarhorse2_alliance_armor.blp"}),
        ("Horde", {11: "pvpwarhorse2_horde_skin.blp", 12: "pvpwarhorse2_horde_armor.blp"}),
        ("White", {11: "pvpwarhorse2_white_skin.blp", 12: "pvpwarhorse2_white_armor.blp"}),
    ),
}

# Explicit defaults for otherwise-empty CreatureDisplayInfo texture slots.  The
# color-labelled records above still exist as distinct variants; these defaults
# make the unsuffixed base record render deterministically instead of relying on
# the batch-1 heuristic.
TEXTURE_HINTS = {
    "babymurlocice": {11: "BabymurlocIce.blp"},
    "murlocice": {11: "MurlocIce.blp"},
    "windridermount_30thanniv": {
        11: "windridermount_30thanniv_body.blp",
        12: "windridermount_30thanniv_armor.blp",
    },
    "rostrumstormgryphon_blue": {
        11: "rostrumstormgryphon_skin_blue1.blp",
        12: "rostrumstormgryphon_armor_blue.blp",
        13: "rostrumstormgryphon_skin_blue2.blp",
    },
    "emeralddreamstag": {
        11: "emeralddreamstag_frost.blp",
        12: "emeralddreamstag_glow_frost.blp",
        13: "emeralddreamstag_eyeglow_frost.blp",
    },
    "motorcyclefelreavermount": {
        11: "motorcyclefelreavermount_fel.blp",
        12: "motorcyclefelreavermount_glow_1_fel.blp",
        13: "motorcyclefelreavermount_glow_2_fel.blp",
    },
    "snailrockmount": {
        11: "snailrockmount_pink.blp",
        12: "snailrockmount_saddle_4.blp",
        13: "snailrockmount_spec_4.blp",
    },
    "squirrelflyingmount": {
        11: "squirrelflyingmount_body_brown.blp",
        12: "squirrelflyingmount_saddle_brown.blp",
        13: "squirrelflyingmount_fx_brown.blp",
    },
    "dreamsaber": _color_triplet("dreamsaber", "Blue"),
    "infernalmount": {
        11: "infernalmount_metal_red.blp",
        12: "infernalmount_rock_red.blp",
        13: "infernalmount_fx_purple.blp",
    },
    "shadebeastflying": {11: "shadebeastflying_black.blp"},
    "shadebeastmount": {
        11: "shadebeastmount_red.blp",
        12: "shadebeastmount_armor_red.blp",
    },
    "skeletalwarhorse2": {
        11: "skeletalwarhorse2_01_black.blp",
        12: "skeletalwarhorse2_02_black.blp",
    },
    "pvpwarhorse2": {
        11: "pvpwarhorse2_alliance_skin.blp",
        12: "pvpwarhorse2_alliance_armor.blp",
    },
}

PATCH_SUFFIXES = [str(number) for number in range(2, 10)] + list(string.ascii_uppercase)
BASE_ARCHIVES = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ"]
LOCALE_ARCHIVES = [
    "base-{loc}.MPQ",
    "locale-{loc}.MPQ",
    "speech-{loc}.MPQ",
    "expansion-locale-{loc}.MPQ",
    "expansion-speech-{loc}.MPQ",
    "lichking-locale-{loc}.MPQ",
    "lichking-speech-{loc}.MPQ",
    "patch-{loc}.MPQ",
]


def _case_insensitive_file(directory: Path, name: str) -> Path | None:
    candidate = directory / name
    if candidate.is_file():
        return candidate
    if not directory.is_dir():
        return None
    lower = name.casefold()
    for child in directory.iterdir():
        if child.is_file() and child.name.casefold() == lower:
            return child
    return None


def client_archive_chain(data_dir: Path, locale: str = "enUS", exclude: set[str] | None = None) -> list[Path]:
    """Return the stock/WXL archive stack highest-priority first."""

    blocked = {value.casefold() for value in (exclude or set())}
    low_to_high: list[Path] = []
    for name in BASE_ARCHIVES:
        path = _case_insensitive_file(data_dir, name)
        if path and path.name.casefold() not in blocked:
            low_to_high.append(path)
    for suffix in PATCH_SUFFIXES:
        path = _case_insensitive_file(data_dir, f"patch-{suffix}.MPQ")
        if path and path.name.casefold() not in blocked:
            low_to_high.append(path)

    locale_dir = data_dir / locale
    for template in LOCALE_ARCHIVES:
        path = _case_insensitive_file(locale_dir, template.format(loc=locale))
        if path and path.name.casefold() not in blocked:
            low_to_high.append(path)
    for suffix in PATCH_SUFFIXES:
        path = _case_insensitive_file(locale_dir, f"patch-{locale}-{suffix}.MPQ")
        if path and path.name.casefold() not in blocked:
            low_to_high.append(path)
    return list(reversed(low_to_high))


def configure_cars() -> None:
    """Put the proven batch-1 helper module into batch-2 mode."""

    def clean_m2_texture_records(data: bytes) -> list[tuple[int, int, bytes]]:
        # The Star Wars exports store a few names as ``*.blp\\0lp``.  The first
        # NUL is the real terminator; bytes after it are exporter garbage.
        return [
            (record, texture_type, name.split(b"\0", 1)[0])
            for record, texture_type, name in _ORIGINAL_M2_TEXTURE_RECORDS(data)
        ]

    def batch2_source_asset_candidates(mount: cars.Mount, texture_name: bytes) -> list[Path]:
        target = texture_name.decode("ascii", errors="ignore").replace("/", "\\").casefold()
        source_files = cars._source_blp_files(mount)
        if target.startswith(f"creature\\{mount.model.parent.name.casefold()}\\"):
            local = mount.model.parent / Path(target).name
            if local.is_file():
                return [local]
        relatives = {
            cars._source_relative_name(mount, path): path
            for path in source_files
        }
        exact = relatives.get(target)
        if exact is not None:
            return [exact]
        if target.startswith("creature\\"):
            # Several source packs are rooted *inside* their Creature directory
            # (StarWars and Deathhound in particular).  Prefer that structural
            # match before falling back to basename-wide lookup, otherwise files
            # such as armorreflect4.blp are ambiguous across sibling mounts.
            trimmed = target[len("creature\\"):]
            exact = relatives.get(trimmed)
            if exact is not None:
                return [exact]
        return _ORIGINAL_SOURCE_ASSET_CANDIDATES(mount, texture_name)

    cars._m2_texture_records = clean_m2_texture_records
    cars._source_asset_candidates = batch2_source_asset_candidates
    cars.MOUNT_ID_BASES = dict(ID_BASES)
    cars.FLYING_MOUNT_MODEL_STEMS = FLYING_MODEL_STEMS
    cars.FLYING_MOUNT_SPELL_TEMPLATE_ID = FLYING_MOUNT_SPELL_TEMPLATE_ID
    cars.MOUNT_VARIANT_SPECS = {}
    cars.MOUNT_TEXTURE_VARIATION_HINTS = {**cars.MOUNT_TEXTURE_VARIATION_HINTS, **TEXTURE_HINTS}
    cars.MOUNT_TEXTURE_ALIASES = {**cars.MOUNT_TEXTURE_ALIASES, **TEXTURE_ALIASES}
    cars.LEGACY_CUSTOM_MOUNT_SPELL_IDS = ()
    cars.LEGACY_MOUNT_IDS = {"item_display": (), "display": (), "model": ()}

    def fixed_mount_ids(mounts: tuple[cars.Mount, ...], baseline: Path | None = None) -> dict[str, tuple[int, ...]]:
        del baseline
        return {
            name: tuple(base + index for index in range(len(mounts)))
            for name, base in ID_BASES.items()
        }

    cars.mount_ids = fixed_mount_ids


def source_roots() -> tuple[Path, ...]:
    return tuple(sorted((path for path in SOURCE_ROOT.iterdir() if path.is_dir()), key=lambda path: path.name.casefold()))


def discover_base_mounts() -> tuple[cars.Mount, ...]:
    mounts: list[cars.Mount] = []
    seen_slugs: set[str] = set()
    seen_names: set[str] = set()
    for root, model, version in cars._mount_candidates(source_roots()):
        if version != WOTLK_MODEL_VERSION or model.stem.casefold() in EXCLUDED_MODEL_STEMS:
            continue
        relative = cars._source_relative(root, model)
        display_name = DISPLAY_NAMES.get(model.stem.casefold())
        if display_name is None:
            raise ValueError(f"batch-2 model is not in the approved 42-model inventory: {model}")
        slug = cars._mount_slug(root.name, relative)
        if slug in seen_slugs:
            raise ValueError(f"duplicate mount slug: {slug}")
        if display_name.casefold() in seen_names:
            raise ValueError(f"duplicate mount display name: {display_name}")
        seen_slugs.add(slug)
        seen_names.add(display_name.casefold())
        mounts.append(cars.Mount(
            package=root.name,
            source_root=root,
            model=model,
            source_relative=relative,
            slug=slug,
            display_name=display_name,
            model_version=version,
            client_model_path=f"Creature\\EsteriaMounts\\{slug}\\{model.name}",
        ))
    if len(mounts) != 42:
        raise ValueError(f"expected 42 approved base mount models, found {len(mounts)}")
    return tuple(mounts)


def _variant_slug(mount: cars.Mount, label: str) -> str:
    value = f"{mount.slug}_{'_'.join(cars._slug_words(label)).lower()}"
    if len(value) > 24:
        value = f"{value[:10]}_{hashlib.sha1(value.encode('ascii')).hexdigest()[:8]}"
    return value


def expand_variants(mounts: tuple[cars.Mount, ...]) -> tuple[cars.Mount, ...]:
    expanded = list(mounts)
    for mount in mounts:
        for label, textures in VARIANT_SPECS.get(mount.model.stem.casefold(), ()):
            slug = _variant_slug(mount, label)
            expanded.append(replace(
                mount,
                slug=slug,
                display_name=f"{mount.display_name} - {label}",
                client_model_path=f"Creature\\EsteriaMounts\\{slug}\\{mount.model.name}",
                texture_overrides=tuple(sorted(textures.items())),
            ))
    if len(expanded) != 71:
        raise ValueError(f"expected 71 mount records after variants, found {len(expanded)}")
    if len({mount.slug.casefold() for mount in expanded}) != 71:
        raise ValueError("duplicate batch-2 mount slug")
    if len({mount.display_name.casefold() for mount in expanded}) != 71:
        raise ValueError("duplicate batch-2 mount display name")
    return tuple(expanded)


def validate_source_assets(mounts: tuple[cars.Mount, ...]) -> None:
    """Fail on custom creature textures or empty variant slots we cannot resolve."""

    for mount in mounts:
        model_data = mount.model.read_bytes()
        variations = cars._mount_texture_variation_paths(mount)
        for _, texture_type, texture_name in cars._m2_texture_records(model_data):
            if not texture_name:
                if texture_type in (11, 12, 13) and texture_type not in variations:
                    raise ValueError(
                        f"unresolved texture-variation slot type {texture_type}: {mount.model} ({mount.display_name})"
                    )
                continue
            normalized = texture_name.decode("ascii", errors="ignore").replace("/", "\\")
            root = normalized.split("\\", 1)[0].casefold()
            if root == "creature" and not cars._source_asset_candidates(mount, texture_name):
                raise FileNotFoundError(f"unresolved custom creature texture {normalized}: {mount.model}")

        expected_skin = f"{mount.model.stem}00.skin".casefold()
        skins = {path.name.casefold() for path in mount.model.parent.iterdir() if path.is_file() and path.suffix.casefold() == ".skin"}
        if expected_skin not in skins:
            raise FileNotFoundError(f"canonical 00.skin is missing for {mount.model}")


def collect_asset_entries(mounts: tuple[cars.Mount, ...], default_icon: bytes) -> dict[str, bytes]:
    entries: dict[str, bytes] = {}
    for mount in mounts:
        mount_entries = cars.collect_mount_entries(mount, default_icon=default_icon)
        output_dir = Path(mount.client_model_path).parent
        for sibling in mount.model.parent.iterdir():
            if sibling.is_file() and sibling.suffix.casefold() == ".anim_mappings":
                mount_entries[str(output_dir / sibling.name).replace("/", "\\")] = sibling.read_bytes()
        entries = cars.merge_archive_entries(entries, mount_entries)
    return entries


def merge_wdbc_replace_rows(base: bytes, extra: bytes, table_name: str) -> bytes:
    """Merge WDBC rows by ID, replacing matching IDs so reruns stay idempotent."""

    left = cars.Wdbc(base)
    right = cars.Wdbc(extra)
    if (left.fields, left.record_size) != (right.fields, right.record_size):
        raise ValueError(f"WDBC layout mismatch for {table_name}")
    incoming_ids = {row[0] for row in right.rows}
    row_sources = [(left, row) for row in left.rows if row[0] not in incoming_ids]
    row_sources.extend((right, row) for row in right.rows)
    row_sources.sort(key=lambda pair: pair[1][0])
    rows = [row for _, row in row_sources]
    if len({row[0] for row in rows}) != len(rows):
        raise ValueError(f"duplicate IDs remain after native merge for {table_name}")

    strings: dict[tuple[int, int], str] = {}
    for row_index, (table, row) in enumerate(row_sources):
        for field in cars.DBC_STRING_FIELDS.get(table_name, ()):
            if row[field]:
                value = table.text(row[field])
                if value:
                    strings[(row_index, field)] = value
    return cars.build_wdbc(rows, left.fields, left.record_size, strings)


def read_winning_client_dbc(storm: cars.Storm, data_dir: Path, table: str, locale: str = "enUS") -> tuple[bytes, Path]:
    key = f"DBFilesClient\\{table}.dbc"
    # Never read our own lower-priority W archive back in as a future baseline.
    blocked = {"patch-w.mpq", f"patch-{locale.lower()}-w.mpq"}
    for archive_path in client_archive_chain(data_dir, locale, blocked):
        handle = storm.open_archive(archive_path)
        try:
            names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
            actual = names.get(key.casefold())
            if actual is not None:
                return storm.read(handle, actual), archive_path
        finally:
            storm.dll.SFileCloseArchive(handle)
    raise FileNotFoundError(f"no active client archive contains {key}")


def build_native_dbcs(
    storm: cars.Storm,
    client_data: Path,
    continuations: dict[str, bytes],
    locale: str = "enUS",
) -> tuple[dict[str, bytes], dict[str, str]]:
    native: dict[str, bytes] = {}
    sources: dict[str, str] = {}
    for table in NATIVE_DBC_TABLES:
        continuation_key = f"DBFilesClient/{table}.dbc1-mounts"
        base, source = read_winning_client_dbc(storm, client_data, table, locale)
        payload = merge_wdbc_replace_rows(base, continuations[continuation_key], table)
        cars.Wdbc(payload)  # Hard WDBC-size/layout validation.
        native[f"DBFilesClient\\{table}.dbc"] = payload
        sources[table] = str(source)
    return native, sources


def _default_icon(storm: cars.Storm, client_root: Path) -> bytes:
    locale = client_root / "Data" / "enUS" / "locale-enUS.MPQ"
    return cars.read_archive_entry(storm, locale, cars.DEFAULT_MOUNT_ICON_ENTRY)


def apply_record_overrides(records: tuple[cars.MountRecord, ...]) -> tuple[cars.MountRecord, ...]:
    corrected: list[cars.MountRecord] = []
    for record in records:
        scale = DISPLAY_SCALE_OVERRIDES.get(record.mount.model.stem.casefold())
        if scale is None:
            corrected.append(record)
            continue
        display = list(record.creature_display_row)
        display[4] = cars.f32(scale)
        corrected.append(replace(record, creature_display_row=tuple(display)))
    return tuple(corrected)


def build_records() -> tuple[cars.MountRecord, ...]:
    configure_cars()
    mounts = expand_variants(discover_base_mounts())
    validate_source_assets(mounts)
    return apply_record_overrides(cars.build_mount_records(mounts, BASELINE))


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest(records: tuple[cars.MountRecord, ...], dbc_sources: dict[str, str]) -> dict[str, object]:
    return {
        "batch": 2,
        "record_count": len(records),
        "native_dbc_only": True,
        "extended_dbc_continuations": False,
        "id_bases": ID_BASES,
        "dbc_sources": dbc_sources,
        "records": [
            {
                "name": record.mount.display_name,
                "slug": record.mount.slug,
                "source": str(record.mount.model),
                "model_path": record.mount.client_model_path,
                "flying": record.mount.model.stem.casefold() in FLYING_MODEL_STEMS,
                "spell": record.spell_id,
                "spell_icon": record.spell_icon_id,
                "item": record.item_id,
                "item_display": record.item_display_id,
                "creature": record.creature_id,
                "display": record.display_id,
                "model": record.model_id,
                "textures": list(record.texture_variations),
            }
            for record in records
        ],
    }


def stage(client_root: Path, stormlib: Path, locale: str = "enUS") -> tuple[Path, tuple[cars.MountRecord, ...]]:
    configure_cars()
    mounts = expand_variants(discover_base_mounts())
    validate_source_assets(mounts)
    records = apply_record_overrides(cars.build_mount_records(mounts, BASELINE))
    if len(records) != 71:
        raise ValueError(f"expected 71 records, found {len(records)}")

    storm = cars.Storm(stormlib)
    default_icon = _default_icon(storm, client_root)
    assets = collect_asset_entries(mounts, default_icon)
    continuation_entries = cars.build_mount_dbc_entries(records, BASELINE)
    native_dbcs, dbc_sources = build_native_dbcs(storm, client_root / "Data", continuation_entries, locale)

    for key in continuation_entries:
        if ".dbc1-" not in key:
            raise AssertionError(f"unexpected continuation key: {key}")
    patch_entries = cars.merge_archive_entries(assets, native_dbcs)
    if any(".dbc1-" in name.casefold() for name in patch_entries):
        raise AssertionError("Patch-W must not contain extended-DBC continuation files")
    if any(name.casefold() == "wxl-dbc.manifest" for name in patch_entries):
        raise AssertionError("Patch-W must not contain a WXL DBC manifest")

    # StormLib owns the reserved (listfile)/(attributes) pseudo-files.  Feeding
    # either one to SFileCreateFile fails with ERROR_AVI_FILE (10003); the
    # archive writer creates its own internal listing for normal entries.
    STAGE_ROOT.mkdir(parents=True, exist_ok=True)
    native_dir = STAGE_ROOT / "native-dbc"
    native_dir.mkdir(parents=True, exist_ok=True)
    patch_path = STAGE_ROOT / "Patch-W.MPQ"
    if patch_path.exists():
        patch_path.unlink()
    storm.create_archive(patch_path, patch_entries)

    for entry_name, payload in native_dbcs.items():
        (native_dir / Path(entry_name).name).write_bytes(payload)

    sql_text = cars.render_mount_sql(records)
    # The live AzerothCore world schema names these two SQL overlay columns
    # CharacterPoints_1/_2 (with underscores), while the WDBC field helpers use
    # CharacterPoints1/2. Batch #1's proven migration uses the underscored SQL
    # names, so normalize only the SQL text here; the binary DBC layout is unchanged.
    sql_text = sql_text.replace("`CharacterPoints1`", "`CharacterPoints_1`")
    sql_text = sql_text.replace("`CharacterPoints2`", "`CharacterPoints_2`")
    (STAGE_ROOT / "u_custom_server_2026_09_27_00_mounts_batch2.sql").write_text(
        sql_text, encoding="utf-8", newline="\n"
    )
    manifest = _manifest(records, dbc_sources)
    manifest["patch_w_sha256"] = _hash(patch_path)
    manifest["patch_w_entries"] = len(patch_entries)
    (STAGE_ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (STAGE_ROOT / "additems.txt").write_text(
        "\n".join(f".additem {record.item_id}  # {record.mount.display_name}" for record in records) + "\n",
        encoding="utf-8",
    )
    return patch_path, records


def _read_staged_native() -> dict[str, bytes]:
    native_dir = STAGE_ROOT / "native-dbc"
    result = {}
    for table in NATIVE_DBC_TABLES:
        path = native_dir / f"{table}.dbc"
        if not path.is_file():
            raise FileNotFoundError(f"stage first; missing {path}")
        payload = path.read_bytes()
        cars.Wdbc(payload)
        result[f"DBFilesClient\\{table}.dbc"] = payload
    return result


def deploy_client(client_root: Path, stormlib: Path, locale: str = "enUS") -> Path:
    patch_source = STAGE_ROOT / "Patch-W.MPQ"
    if not patch_source.is_file():
        raise FileNotFoundError("Patch-W is not staged; run --stage first")
    native_dbcs = _read_staged_native()
    data = client_root / "Data"
    root_z = _case_insensitive_file(data, "patch-Z.MPQ")
    locale_z = _case_insensitive_file(data / locale, f"patch-{locale}-Z.MPQ")
    if root_z is None or locale_z is None:
        raise FileNotFoundError("both root and locale Z archives are required for native DBC deployment")

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    backup_root = client_root / "Backups" / f"mount-batch2-{timestamp}"
    backup_root.mkdir(parents=True, exist_ok=False)
    shutil.copy2(root_z, backup_root / root_z.name)
    shutil.copy2(locale_z, backup_root / locale_z.name)

    patch_target = data / "Patch-W.MPQ"
    if patch_target.exists():
        shutil.copy2(patch_target, backup_root / patch_target.name)
    shutil.copy2(patch_source, patch_target)

    storm = cars.Storm(stormlib)
    storm.replace_archive_entries(root_z, native_dbcs)
    storm.replace_archive_entries(locale_z, native_dbcs)

    # Verify both highest-priority mirrors contain every batch-2 row.
    for archive_path in (root_z, locale_z):
        for table, id_base in (
            ("Spell", ID_BASES["spell"]),
            ("Item", ID_BASES["item"]),
            ("ItemDisplayInfo", ID_BASES["item_display"]),
            ("SpellIcon", ID_BASES["spell_icon"]),
            ("CreatureDisplayInfo", ID_BASES["display"]),
            ("CreatureModelData", ID_BASES["model"]),
            ("SkillLineAbility", ID_BASES["spell"]),
        ):
            payload = cars.read_archive_entry(storm, archive_path, f"DBFilesClient\\{table}.dbc")
            table_data = cars.Wdbc(payload)
            ids = {row[0] for row in table_data.rows}
            missing = [value for value in range(id_base, id_base + 71) if value not in ids]
            if missing:
                raise AssertionError(f"{archive_path}: {table} missing batch-2 IDs {missing[:5]}")

    patch_entries = cars.read_archive(storm, patch_target)
    if any(".dbc1-" in name.casefold() for name in patch_entries):
        raise AssertionError("deployed Patch-W unexpectedly contains extended DBC files")
    model_paths = {
        entry["model_path"].casefold()
        for entry in json.loads((STAGE_ROOT / "manifest.json").read_text(encoding="utf-8"))["records"]
    }
    actual_paths = {name.casefold() for name in patch_entries}
    missing_models = sorted(model_paths - actual_paths)
    if missing_models:
        raise AssertionError(f"Patch-W is missing model entries: {missing_models[:5]}")
    return backup_root


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client", type=Path, default=CLIENT_ROOT_DEFAULT)
    parser.add_argument("--stormlib", type=Path, default=STORMLIB_DEFAULT)
    parser.add_argument("--locale", default="enUS")
    parser.add_argument("--stage", action="store_true", help="Build Patch-W, native DBCs, manifest, SQL, and additem list.")
    parser.add_argument("--deploy-client", action="store_true", help="Deploy staged Patch-W and mirror native DBCs into winning Z archives.")
    args = parser.parse_args()
    if not args.stage and not args.deploy_client:
        parser.error("choose --stage and/or --deploy-client")

    if args.stage:
        patch_path, records = stage(args.client, args.stormlib, args.locale)
        print(f"staged {len(records)} mounts: {patch_path}")
        print(f"Patch-W SHA-256: {_hash(patch_path)}")
    if args.deploy_client:
        backup = deploy_client(args.client, args.stormlib, args.locale)
        print(f"client deployed; backups: {backup}")


if __name__ == "__main__":
    main()
