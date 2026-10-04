"""Working out what a file actually is.

Extensions are a hint, not proof: assets extracted by FileDataID arrive as
``1234567.unknown``, and ``.wmo`` covers both roots and groups.  Detection
therefore always looks at the bytes.

That applies to every format, not only the ones this tool converts.  A build
read straight out of CASC has no filenames at all -- the listfile supplies
them, and it never covers everything -- so a sound or a font that is only
recognised by its extension has no extension to be recognised by, and would
land as an anonymous ``.bin`` that no client will ever look up.  Each family
below is therefore identified by its signature as well, so a file keeps its
identity even when nothing names it.
"""

from __future__ import annotations

import os

from .chunks import ChunkReader
from .liquid import SKIP_REASON as LIQUID_SKIP_REASON

M2 = "m2"
SKIN = "skin"
ANIM = "anim"
SKEL = "skel"
BLP = "blp"
WMO_ROOT = "wmo"
WMO_GROUP = "wmo-group"
ADT = "adt"
WDT = "wdt"
WDL = "wdl"
DB2 = "db2"
DBC = "dbc"

# Formats that are not converted but still have to be recognised: a patch
# archive needs the ones 3.3.5a reads, and the ones it cannot read are better
# named than carried along as anonymous bytes.
WAV = "wav"
MP3 = "mp3"
OGG = "ogg"
AVI = "avi"
MP4 = "mp4"
TTF = "ttf"
OTF = "otf"
TGA = "tga"
DDS = "dds"
PNG = "png"
BLS = "bls"           # compiled shaders
TEXT = "text"         # .lua/.xml/.toc/.txt and friends
MAP_SIDECAR = "map-sidecar"   # _lgt/_occ/_fogs/_mpv .wdt, _lod .adt
LIQUID = "liquid"     # .wlw/.wlq/.wlm liquid volumes
UNKNOWN = "unknown"

# What to do with a file, once its kind is known.
CONVERT = "convert"   # needs a structural downgrade
COPY = "copy"         # 3.3.5a reads it unchanged; copy it into the patch
SKIP = "skip"         # cannot be used by 3.3.5a, or is handled elsewhere

#: Kinds this tool converts. Client databases are handled separately: they
#: need a definition, a mapping and usually the user's own table as a template,
#: so they only join a `convert` run once --dbd is supplied.
CONVERTIBLE = {M2, SKIN, ANIM, BLP, WMO_ROOT, WMO_GROUP, ADT, WDT, WDL}

#: Extensions the 3.3.5a client reads as-is. A patch archive needs these just
#: as much as the converted files, so they are copied rather than dropped.
COPY_EXTENSIONS = {
    ".ogg", ".mp3", ".wav",                    # sound and music
    ".avi",                                    # cinematics
    ".sbt",                                    # cinematic subtitles
    ".lua", ".xml", ".toc", ".xsd",            # interface
    ".txt", ".html", ".htm",
    ".ttf",                                    # fonts
    ".zmp",                                    # world map terrain blocks
    ".sig",                                    # signature beside an addon .toc
    ".wtf", ".ini",                            # configuration
}

#: Launcher, installer and operating-system files.  They travel in the same
#: archives as the game data and are not game data: a patch has no use for an
#: executable, a code signature or a macOS bundle resource.
SYSTEM_EXTENSIONS = {
    ".exe", ".dll", ".dylib", ".pak", ".bin", ".icns", ".nib",
    ".plist", ".strings", ".manifest", ".json", ".url", ".amsfolder",
    ".signed", ".csp", ".what", ".delete", ".lst",
}

_SYSTEM_REASON = ("a launcher, installer or operating-system file rather than "
                  "game data; a 3.3.5a patch archive has no use for it")

#: Extensions that exist in modern builds but cannot be used by 3.3.5a, with
#: the reason, so the report says why rather than "unrecognised".
UNSUPPORTED_EXTENSIONS = {
    ".db2": "client database; convert it with 'wotlkconv db convert', or pass "
            "--dbd to a convert run so the tables with mappings come along",
    ".tex": "Legion streamed high-resolution texture payloads; the .blp beside "
            "it already carries every mip 3.3.5a renders",
    ".phys": "physics rigs; 3.3.5a has no model physics",
    ".bone": "Legion bone override files; no 3.3.5a equivalent",
    ".meta": "per-asset metadata written beside a .blp, .m2 or .ogg; a build "
             "record rather than something any client loads",
    ".mdx": "the pre-Wrath model format; 3.3.5a loads .m2 files, and names "
            "them .mdx in its databases only out of habit",
    ".dat": "per-tile map data from builds either side of Wrath; not a file "
            "3.3.5a looks for",
    ".col": "per-tile collision data; 3.3.5a takes collision from the terrain "
            "and from each model's own collision mesh",
    ".h2o": "standalone liquid data; 3.3.5a keeps liquid in the tile's MH2O "
            "and MCLQ chunks",
    ".wwe": "world weather effects tied to a WMO; no 3.3.5a equivalent",
    ".wwf": "weather particulate definitions; no 3.3.5a equivalent",
    ".pvdata": "particulate volume data; no 3.3.5a equivalent",
    ".scn": "database scene scripts; no 3.3.5a equivalent",
    ".bls": "compiled shaders for a renderer 3.3.5a does not have; it loads "
            "its own from its own Shaders folder",
    ".wfx": "shader effect definitions for a renderer 3.3.5a does not have",
    ".srt": "the subtitle format modern cinematics use; 3.3.5a reads .sbt",
    ".m3": "not a World of Warcraft model format",
    ".mtl3lib": "not a World of Warcraft material format",
    ".png": "3.3.5a loads .blp textures, not .png",
    ".tga": "3.3.5a loads .blp textures, not .tga",
    ".dds": "3.3.5a loads .blp textures, not .dds",
    ".otf": "3.3.5a loads .ttf fonts, not .otf",
    ".mp4": "3.3.5a plays .avi cinematics, not .mp4",
    ".pm4": "development pathing data for a terrain tile; a server-side file "
            "that never reaches a retail client",
    ".pd4": "development pathing data for a world object; a server-side file "
            "that never reaches a retail client",
    ".blob": "a preload or index blob tied to the modern build's own "
             "FileDataIDs; meaningless to 3.3.5a",
    ".wlw": LIQUID_SKIP_REASON,
    ".wlm": LIQUID_SKIP_REASON,
    ".wlq": LIQUID_SKIP_REASON,
}

#: What to do with a detected kind that is not converted, and why.  Detection
#: by signature means these apply even when nothing named the file.
KIND_ACTIONS = {
    WAV: (COPY, ""),
    MP3: (COPY, ""),
    OGG: (COPY, ""),
    AVI: (COPY, ""),
    TTF: (COPY, ""),
    TEXT: (COPY, ""),
    DBC: (COPY, "already a 3.3.5a client database"),
    MP4: (SKIP, UNSUPPORTED_EXTENSIONS[".mp4"]),
    OTF: (SKIP, UNSUPPORTED_EXTENSIONS[".otf"]),
    BLS: (SKIP, UNSUPPORTED_EXTENSIONS[".bls"]),
    DDS: (SKIP, UNSUPPORTED_EXTENSIONS[".dds"]),
    PNG: (SKIP, UNSUPPORTED_EXTENSIONS[".png"]),
    TGA: (SKIP, UNSUPPORTED_EXTENSIONS[".tga"]),
    LIQUID: (SKIP, LIQUID_SKIP_REASON),
}

#: Output extension for each kind.
EXTENSIONS = {
    M2: ".m2", SKIN: ".skin", ANIM: ".anim", SKEL: ".skel", BLP: ".blp",
    WMO_ROOT: ".wmo", WMO_GROUP: ".wmo", ADT: ".adt", WDT: ".wdt",
    WDL: ".wdl", LIQUID: ".wlw",
    DB2: ".db2", DBC: ".dbc",
    WAV: ".wav", MP3: ".mp3", OGG: ".ogg", AVI: ".avi", MP4: ".mp4",
    TTF: ".ttf", OTF: ".otf",
    TGA: ".tga", DDS: ".dds", PNG: ".png", BLS: ".bls", TEXT: ".txt",
}

#: The listfile's placeholder for a file whose type it does not know.  It is a
#: statement about the name, not about the bytes, so it never decides anything
#: on its own -- detection has already looked at the content by this point.
PLACEHOLDER_EXTENSIONS = {".unk"}

#: Extensions that promise a format this tool converts.  If the bytes do not
#: back the promise the file is broken, not unrecognised, and saying so beats
#: copying it into a patch where the client will choke on it.
CONVERTIBLE_EXTENSIONS = {
    ".m2": "a model", ".skin": "a skin profile", ".anim": "an animation",
    ".skel": "a skeleton", ".blp": "a texture", ".wmo": "a world object",
    ".adt": "a terrain tile", ".wdt": "a map index",
    ".wdl": "a low-resolution heightmap", ".dbc": "a client database",
}

#: Files that sit beside a map's .wdt or .adt carrying data for systems that
#: arrived after Wrath.  Each is recognised by a chunk only it has, because the
#: extension it shares with the real map file says nothing about which it is.
MAP_SIDECAR_CHUNKS = {
    "MPLT": "per-tile light definitions (_lgt.wdt)",
    "MPL2": "per-tile light definitions (_lgt.wdt)",
    "MPL3": "per-tile light definitions (_lgt.wdt)",
    "MLTA": "light animations (_lgt.wdt)",
    "MAOI": "terrain occlusion hulls (_occ.wdt)",
    "MAOH": "terrain occlusion heightmap (_occ.wdt)",
    "MVFX": "volumetric fog (_fogs.wdt)",
    "VFOG": "volumetric fog (_fogs.wdt)",
    "MPVD": "particulate volumes (_mpv.wdt)",
    "MLHD": "the LOD terrain mesh (_lod.adt)",
    "MLVH": "the LOD terrain mesh (_lod.adt)",
    "MLLL": "the LOD terrain mesh (_lod.adt)",
    "MMFE": "a model preload list (_preload.wdt)",
}

#: Sidecar chunks that sit beside a chunk a real map file also has, so they
#: have to be looked for before the terrain test: a ``_preload.wdt`` is MVER,
#: a 4-byte ``MHDR`` and ``MMFE`` (a real tile's MHDR is 64 bytes).
_SIDECAR_BEFORE_TERRAIN = {"MMFE"}

#: Suffixes of the terrain pieces a 3.3.5a tile has no room for, and why.
UNUSED_ADT_PIECES = {
    "tex1": "the high-detail texture variant; 3.3.5a's single tile takes its "
            "layers from _tex0",
    "obj1": "the high-detail object variant; 3.3.5a's single tile takes its "
            "placements from _obj0",
    "lod": "Legion's LOD terrain mesh, for a renderer 3.3.5a does not have",
}

#: Extensions that name a Cataclysm-and-later split terrain file.
SPLIT_ADT_SUFFIXES = ("_obj0", "_obj1", "_tex0", "_tex1", "_lod")


def _riff_kind(data: bytes) -> str:
    """Tell a ``.wav`` from an ``.avi``; both are RIFF.

    The form type at byte 8 is the whole of it.  There is deliberately no
    attempt to sub-classify the WAVE further: World of Warcraft ships no
    Wwise audio at all, so a check for it could only ever be wrong about a
    sound the client can really play.
    """
    form = data[8:12]
    if form == b"AVI ":
        return AVI
    if form == b"WAVE":
        return WAV
    return UNKNOWN


def _looks_like_text(data: bytes) -> bool:
    """True when the bytes read as a text file rather than a format.

    Interface scripts, ``.toc`` manifests and translation tables have no magic
    number, so the only thing that distinguishes them from anonymous data is
    that they are text.
    """
    sample = data[:1024]
    if not sample:
        return False
    if b"\0" in sample:
        return False
    printable = sum(1 for b in sample if 0x20 <= b < 0x7F or b in (9, 10, 13))
    return printable >= len(sample) * 0.95


def _chunk_names(data: bytes, limit: int = 6) -> list[str]:
    names: list[str] = []
    try:
        for chunk in ChunkReader(data, reverse=True):
            names.append(chunk.name)
            if len(names) >= limit:
                break
    except Exception:
        pass
    return names


def detect(data: bytes, path: str = "") -> str:
    """Classify a buffer. ``path`` only breaks ties detection cannot."""
    if len(data) < 8:
        return UNKNOWN

    head = data[:4]
    if head == b"MD20":
        return M2
    if head == b"MD21":
        return M2
    if head == b"SKIN":
        return SKIN
    if head == b"BLP2" or head == b"BLP1":
        return BLP
    if head in (b"AFM2", b"AFSA", b"AFSB"):
        return ANIM
    if head in (b"SKL1", b"SKB1", b"SKA1"):
        return SKEL
    if head == b"WDBC":
        return DBC
    if head[:3] in (b"WDC", b"WDB") and head[3:4].isalnum():
        return DB2

    # -- formats this tool does not convert, but must still recognise ----
    if head == b"RIFF":
        kind = _riff_kind(data)
        if kind is not UNKNOWN:
            return kind
    if head == b"OggS":
        return OGG
    if head[:3] == b"ID3" or (head[0] == 0xFF and head[1] & 0xE0 == 0xE0):
        return MP3
    if data[4:8] == b"ftyp":
        return MP4
    if head == b"OTTO":
        return OTF
    if head in (b"\x00\x01\x00\x00", b"true", b"ttcf"):
        return TTF
    if head == b"DDS ":
        return DDS
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return PNG
    if head in (b"GXSH", b"SHAD"):
        return BLS
    if head in (b"LIQ*", b"*QIL"):
        return LIQUID
    if data.rstrip(b"\0")[-18:-2] == b"TRUEVISION-XFILE":
        return TGA

    names = _chunk_names(data)
    if names:
        if "MOHD" in names:
            return WMO_ROOT
        if "MOGP" in names:
            return WMO_GROUP
        if _SIDECAR_BEFORE_TERRAIN.intersection(names):
            return MAP_SIDECAR
        if "MHDR" in names or "MCIN" in names or "MCNK" in names:
            return ADT
        if "MPHD" in names or "MAIN" in names:
            return WDT
        if "MAOF" in names:
            return WDL
        # Last of the map formats, because a real .wdl carries the same LOD
        # mesh chunks a _lod.adt does -- it just also has the MAOF that makes
        # it a heightmap, which is what the check above settles.
        if any(n in MAP_SIDECAR_CHUNKS for n in names):
            return MAP_SIDECAR
        if names[0] == "MVER" and len(names) == 1:
            # A version and nothing else.  Retail ships these as empty map
            # sidecars -- zulaman_fogs.wdt is 12 bytes: the map has no fog --
            # so only an .adt is taken as a split terrain piece; routing a
            # .wdt to the terrain converter failed ~2,000 of them per build.
            if os.path.splitext(path)[1].lower() == ".wdt":
                return MAP_SIDECAR
            return ADT

    ext = os.path.splitext(path)[1].lower()
    if ext == ".anim":
        return ANIM
    if ext == ".adt":
        return ADT
    if ext == ".skel":
        return SKEL
    if ext == ".wdl":
        return WDL

    # Last, because anything with a signature has already been named by it.
    if _looks_like_text(data):
        return TEXT
    return UNKNOWN


def classify(kind: str, path: str = "",
             convert_databases: bool = False) -> tuple[str, str]:
    """Decide what to do with a file, returning ``(action, reason)``.

    Kinds this tool understands are converted. Everything else is judged on its
    extension: formats 3.3.5a reads unchanged are copied through so a patch
    build is complete, and formats it cannot use are skipped with a reason
    that says which.
    """
    if kind == SKEL:
        return SKIP, ("skeletons are merged into the model that references "
                      "them, not converted on their own")
    if kind == DB2:
        if convert_databases:
            return CONVERT, ""
        return SKIP, UNSUPPORTED_EXTENSIONS[".db2"]
    if kind in CONVERTIBLE:
        return CONVERT, ""
    if kind in KIND_ACTIONS:
        return KIND_ACTIONS[kind]
    if kind == MAP_SIDECAR:
        return SKIP, ("a map sidecar carrying " + _sidecar_detail(path)
                      + "; 3.3.5a keeps none of this and never looks for the "
                      "file")

    ext = os.path.splitext(path)[1].lower()
    if ext in UNSUPPORTED_EXTENSIONS:
        return SKIP, UNSUPPORTED_EXTENSIONS[ext]
    if ext in SYSTEM_EXTENSIONS:
        return SKIP, _SYSTEM_REASON
    if ext in PLACEHOLDER_EXTENSIONS:
        return COPY, ("named .unk because the listfile does not know what it "
                      "is either; nothing in the bytes identified it, so it "
                      "is carried through unchanged rather than dropped")
    if ext in COPY_EXTENSIONS:
        return COPY, ""
    if ext in CONVERTIBLE_EXTENSIONS:
        # Named as something convertible, but the bytes say otherwise.
        # Copying it would put a file the client cannot read into the patch.
        return SKIP, (f"named as {CONVERTIBLE_EXTENSIONS[ext]} ({ext}) but its "
                      f"contents are not one -- truncated, encrypted, or "
                      f"misnamed")
    if kind == UNKNOWN and ext:
        # An unrecognised extension is more likely to be data 3.3.5a can read
        # than something harmful, so carry it through and say so.
        return COPY, f"unrecognised format {ext}; copied unchanged"
    return SKIP, "unrecognised format with no extension to judge it by"


def _sidecar_detail(path: str) -> str:
    """Name what a sidecar holds, from the suffix when it has one."""
    stem = os.path.splitext(os.path.basename(path))[0].lower()
    for suffix, detail in (("_lgt", "per-tile light definitions"),
                           ("_occ", "terrain occlusion data"),
                           ("_fogs", "volumetric fog"),
                           ("_mpv", "particulate volumes"),
                           ("_lod", "the LOD terrain mesh"),
                           ("_preload", "a list of models to preload")):
        if stem.endswith(suffix):
            return detail
    return "data added after Wrath"


def adt_base_name(path: str) -> str:
    """``Azeroth_32_48_obj0.adt`` -> ``Azeroth_32_48``."""
    stem = os.path.splitext(os.path.basename(path))[0]
    lowered = stem.lower()
    for suffix in SPLIT_ADT_SUFFIXES:
        if lowered.endswith(suffix):
            return stem[: -len(suffix)]
    return stem
