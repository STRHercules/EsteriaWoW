"""User-facing conversion knobs, shared by every format module."""

from __future__ import annotations

import dataclasses
from enum import Enum


class TextureFormat(str, Enum):
    #: Pick per texture: DXT1 opaque, DXT1 for 1-bit alpha, DXT5 for gradients.
    AUTO = "auto"
    DXT1 = "dxt1"
    DXT3 = "dxt3"
    DXT5 = "dxt5"
    #: 256-colour palettised -- smaller and cleaner for UI art.
    PAL = "pal"
    #: Uncompressed BGRA; largest, but lossless.
    RAW = "raw"
    #: Re-encode into whatever the source already used, when 3.3.5a allows it.
    KEEP = "keep"


class UnresolvedPolicy(str, Enum):
    #: Abort the file when a FileDataID has no listfile entry.
    FAIL = "fail"
    #: Write a deterministic ``unknown/<id>.<ext>`` path instead.
    PLACEHOLDER = "placeholder"
    #: Drop the reference entirely (texture slot becomes empty).
    STRIP = "strip"


@dataclasses.dataclass(slots=True)
class Options:
    """Everything the converters can be told to do differently."""

    # -- global ---------------------------------------------------------
    overwrite: bool = False
    dry_run: bool = False
    jobs: int = 1

    # -- references -----------------------------------------------------
    unresolved: UnresolvedPolicy = UnresolvedPolicy.PLACEHOLDER
    #: Prefix prepended to every resolved in-game path, e.g. "custom\\mypatch".
    path_prefix: str = ""
    #: Name outputs after the listfile path when the input is named by
    #: FileDataID (``1234567.m2`` -> ``world/foo/bar.m2``).
    name_from_listfile: bool = True
    #: Write every output into the destination root instead of mirroring the
    #: input's directory structure.
    flatten: bool = False
    #: Copy formats 3.3.5a reads unchanged (sound, interface, fonts) into the
    #: output rather than dropping them. A patch archive needs them too.
    copy_unconverted: bool = True

    # -- textures -------------------------------------------------------
    texture_format: TextureFormat = TextureFormat.AUTO
    #: 0 disables the cap.
    max_texture_size: int = 1024  # BLP_SOFT_MAX_DIMENSION
    force_power_of_two: bool = True
    #: Rebuild BC5 normal maps' Z channel into blue during transcode.
    reconstruct_normal_z: bool = True
    #: Alpha below this becomes fully transparent in DXT1 punch-through blocks.
    dxt1_alpha_cutoff: int = 128

    # -- models ---------------------------------------------------------
    #: Emit warnings rather than failing when a model exceeds a soft limit.
    strict_limits: bool = False
    strip_particles: bool = False
    strip_ribbons: bool = False
    strip_cameras: bool = False
    strip_lights: bool = False
    #: Convert a Legion+ model whose SKID skeleton could not be found. The
    #: result has no bones and no animations, so this is off by default.
    allow_missing_skeleton: bool = False
    #: Also write the converted .skin / .anim companions next to the model.
    convert_companions: bool = True

    # -- client databases -------------------------------------------------
    #: Directory of user mapping JSON files, taking precedence over built-ins.
    db_mappings: str = ""
    #: A genuine 3.3.5a ``.adt`` to read file conventions off, rather than
    #: relying on the documented default.  See ``adt.convert``.
    adt_reference: str = ""
    #: Directory searched for ``<Table>.dbc`` templates.
    db_templates: str = ""
    #: Append to the template's rows rather than starting a fresh table.
    db_merge: bool = True
    #: Added to converted row ids (and to references marked ``id_offset``) so
    #: they do not collide with the ids the client already has.
    db_id_offset: int = 0
    #: Only convert these row ids; empty means every row.
    db_row_ids: tuple[int, ...] = ()
    #: ``(column, value)`` filters a row must match to be converted.
    db_where: tuple[tuple[str, str], ...] = ()

    # -- world ----------------------------------------------------------
    #: Merge Cataclysm+ split ADTs (_obj0/_tex0) back into one monolithic file.
    merge_split_adt: bool = True
    #: Split a WMO group that outgrew 16-bit indices into several groups, with
    #: the root updated to reference them. Self-contained, so on by default.
    split_oversized_groups: bool = True
    #: Split a model that outgrew 16-bit indices into several .m2 files. Off by
    #: default: the extra files are new assets nothing references yet, so the
    #: user has to place them.
    split_oversized_models: bool = False

    def texture_ext_cap(self) -> int:
        return self.max_texture_size if self.max_texture_size > 0 else 1 << 30
