# Complete Python tool and library index

Generated from source ASTs; no listed script was executed.
Historical scripts retain original paths and may mutate archives or databases.
Use the maintained entry points in [the recipes](../03-RECIPES.md) for deployment.

Exact parser declarations and imports: [tool-index.json](../evidence/tool-index.json).

## Converter/wotlkconv/__init__.py

[Source](../sources/Converter/wotlkconv/__init__.py)

wotlkconv -- convert modern World of Warcraft assets to 3.3.5a (build 12340). The package is import-safe with
no third-party dependencies; the command line entry point lives in :mod:`wotlkconv.cli`.

## Converter/wotlkconv/__main__.py

[Source](../sources/Converter/wotlkconv/__main__.py)

Allow ``python -m wotlkconv``.

## Converter/wotlkconv/adt/__init__.py

[Source](../sources/Converter/wotlkconv/adt/__init__.py)

ADT terrain tile, WDT map index and WDL heightmap reading and downgrading.

## Converter/wotlkconv/adt/convert.py

[Source](../sources/Converter/wotlkconv/adt/convert.py)

Terrain tiles. Cataclysm split each ADT into four files -- ``Zone_32_48.adt`` for heights, ``_tex0`` for
texture layers, ``_obj0`` for doodad and WMO placements, plus LOD variants. 3.3.5a reads one monolithic tile
with an ``MCIN`` index, which Cataclysm dropped because it no longer needed it. Merging them back means
walking all 256 map chunks in lockstep across the three files, reassembling each ``MCNK`` from pieces that now
live in different places, and recomputing every offset: * ``MCNK`` sub-chunk offsets are relative to the start
of the chunk *including* its 8-byte header, so they all move. * ``MCRD`` (doodad refs) and ``MCRW`` (WMO refs)
concatenate back into a single ``MCRF``, with the two counts written into the chunk header. * ``MCIN`` has to
be built from scratch. * ``MHDR``'s offsets, which are relative to the start of its own payload, are rewritten
to match the new layout. * Doodad and WMO placements that name their asset by FileDataID get the name tables
back (:mod:`.placements`), because 3.3.5a can only follow a name. * Liquid instances are re-encoded in the
vertex formats 3.3.5a reads (:mod:`.mh2o`). Cataclysm's high-resolution 8x8 hole mask is folded down to the
4x4 mask Wrath renders, and the chunks that only exist after Wrath are dropped. One detail of ``MCIN`` has two
readings. Each entry gives the file offset of an ``MCNK`` and a size, and the size is either the chunk's
payload or that payload plus the 8-byte chunk header. The offset is unambiguous -- it points at the header --
so a reader that seeks there and then trusts the chunk's own size field, as the client does, cannot be misled
either way; only a tool that takes ``MCIN``'s size as the extent of the chunk can be. For that reader the
header-inclusive value is the safe one: it spans the whole chunk, where the payload-only value would stop 8
bytes short and cut off the end of the last sub-chunk. So that is the default. It is not left as a guess,
though: point ``--reference-adt`` at any genuine 3.3.5a tile and the convention is read off it directly, by
comparing each entry's size against the size the chunk itself declares.

## Converter/wotlkconv/adt/layers.py

[Source](../sources/Converter/wotlkconv/adt/layers.py)

Texture layers of a map chunk, cut down to what 3.3.5a can draw. A chunk paints its ground with a base texture
and up to three more, each blended over the ones below through its own 64x64 alpha map. 3.3.5a keeps exactly
four layer slots; Cataclysm and later allow eight (retail Azeroth has more than four on 15,000 chunks), and an
old reader walks off the end of its array. When a chunk has too many, the upper layers that show least are
dropped. How much a layer shows is its alpha at each point times how much of it the layers above leave
uncovered, summed over the chunk (sampled every fourth texel, which is plenty to rank four to eight layers).
The kept layers' alpha maps are carried over byte for byte and re-indexed into a rebuilt ``MCAL``. A layer
whose texture has no file behind it (retail tiles occasionally name FileDataID 0) is dropped too. If that is
the base, the lowest layer that does have a texture becomes the base and loses its alpha map, since a base
covers everything.

## Converter/wotlkconv/adt/mh2o.py

[Source](../sources/Converter/wotlkconv/adt/mh2o.py)

Terrain liquids (``MH2O``). The chunk kept its shape from Wrath to now: a header per map chunk, then liquid
instances, each with an optional exists-bitmap and a block of vertex data. What changed is the second word of
an instance. In 3.3.5a it is the *liquid vertex format* (LVF), which says what the vertex block holds: ====
=================================== =============== LVF per vertex bytes ====
=================================== =============== 0 height (float) + depth (u8) 5 1 height (float) + UV (2 x
u16) 8 2 depth (u8) 1 3 height + UV + depth (Cataclysm on) 9 ==== ===================================
=============== From Warlords of Draenor on, a value of 42 or more is a ``LiquidObject`` id instead, and the
format has to be looked up: Ocean (liquid type 2) is always depth-only, and every other type uses the vertex
format of its ``LiquidMaterial``. Nearly every retail instance is written that way, so an old reader takes an
object id for a format it has never heard of. (Both halves of that rule were checked against the vertex block
sizes of 94,000 retail instances; every one agreed.) 3.3.5a only knows formats 0 to 2, and picks between them
by the kind of liquid, as its own Northrend tiles and Noggit's writer both show: magma and slime carry UVs
(1), ocean lying flat at height 0 is depth-only (2), and everything else is height and depth (0). So each
instance is decoded in its retail format and re-encoded in the one 3.3.5a expects for its liquid, with a
missing height filled from the instance's minimum, a missing depth as fully deep and missing UVs laid out the
way Noggit lays out new ones. The liquid type id itself is kept; the converted ``LiquidType.dbc`` carries
every retail type. A tile whose instances already use 3.3.5a formats is left byte for byte.

## Converter/wotlkconv/adt/placements.py

[Source](../sources/Converter/wotlkconv/adt/placements.py)

Doodad and WMO placements, and the name tables they point into. A 3.3.5a placement (``MDDF`` for models,
``MODF`` for WMOs) names its asset indirectly: ``nameId`` indexes ``MMID``/``MWID``, whose entries are offsets
into the ``MMDX``/``MWMO`` string blob. Battle for Azeroth added a flag that turns ``nameId`` into a
FileDataID instead, and from then on Blizzard wrote every placement that way and stopped writing the name
tables at all. An old reader has no idea the flag exists. It takes the FileDataID as an index into a name
table that is empty, which is undefined behaviour in the client and a crash in Noggit. So every such entry has
its FileDataID looked up in the listfile, the path is added to a rebuilt name table (once, however many
placements share it), ``nameId`` is pointed at that slot and the flag is cleared. Entries that already carry a
name index keep pointing at the same name. When a FileDataID has no listfile entry the unresolved-reference
policy decides: fail the file, point the placement at a deterministic placeholder, or drop it. Dropping a
placement moves every later entry down a slot, so the map chunks' ``MCRF`` references are renumbered to match
-- see :func:`remap_references`.

## Converter/wotlkconv/adt/wdl.py

[Source](../sources/Converter/wotlkconv/adt/wdl.py)

Low-resolution terrain heightmaps. A ``.wdl`` is what the client draws where the real terrain has not been
streamed in yet -- the far-off hills on the horizon. One 17x17 grid of 16-bit heights, plus the 16x16 grid
that sits between those points, stands in for each of the map's 64x64 tiles. That part did not change.
``MAOF`` still indexes the map, ``MARE`` still holds the two grids, ``MAHO`` still masks out holes. What
Legion added is a second, unrelated thing living in the same file: the ``ML*`` chunks, which carry a real LOD
mesh -- vertices, indices, skirts, and their own copies of the doodad and WMO placements -- for a renderer
3.3.5a does not have. So converting one is a matter of keeping the three chunks that still mean something and
dropping the rest. The catch is ``MAOF``: its 4096 entries are absolute file offsets, so dropping anything
ahead of the ``MARE`` blocks moves every one of them and they all have to be rewritten. Wrath also expects the
low-detail WMO tables, which Legion stopped writing; empty ones are emitted in their place so the file has the
shape the old client reads.

## Converter/wotlkconv/adt/wdt.py

[Source](../sources/Converter/wotlkconv/adt/wdt.py)

WDT -- the per-map tile index. Small file, but terrain is unusable without it: ``MAIN`` says which of the
64x64 tiles exist, and ``MPHD`` says how the client should read the ADTs it finds. BfA added ``MAID``, which
names every tile's files by FileDataID; 3.3.5a derives those names from the map name instead, so ``MAID`` is
dropped. A map that is one big WMO (a dungeon, usually) places it with a single ``MODF`` entry. Since BfA that
entry names the WMO by FileDataID and ``MWMO`` is left out, which 3.3.5a cannot follow, so the name is looked
up and written back -- the same repair terrain tiles get, see :mod:`.placements`. One flag matters more than
the rest. ``MPHD.flags & 0x4`` ("big alpha") tells the client that ``MCAL`` holds 8-bit alpha maps rather than
4-bit ones. Cataclysm and later always write the 8-bit form, so a converted map needs that bit set or every
terrain texture blend comes out wrong -- the converter sets it and says so.

## Converter/wotlkconv/binio.py

[Source](../sources/Converter/wotlkconv/binio.py)

Little-endian binary reading/writing helpers shared by every format module. Everything Blizzard ships is
little-endian, so the helpers here hard-code that rather than carrying an endianness parameter around.

## Converter/wotlkconv/blp/__init__.py

[Source](../sources/Converter/wotlkconv/blp/__init__.py)

BLP2 texture reading, writing and downgrading.

## Converter/wotlkconv/blp/bcn.py

[Source](../sources/Converter/wotlkconv/blp/bcn.py)

Block-compression codecs used by BLP2 textures. Decoders cover every encoding that has appeared in a BLP2
alpha_type field: BC1 (DXT1), BC2 (DXT3), BC3 (DXT5), BC4 and BC5. Encoders cover only the three the 3.3.5a
client can sample -- BC1, BC2 and BC3 -- because those are the only ones worth producing. Everything is
deliberately dependency-free: a modding toolchain that needs a compiler or a wheel to run is a toolchain
people stop using. The hot paths use precomputed tables and local-variable binding rather than numpy.

## Converter/wotlkconv/blp/blp.py

[Source](../sources/Converter/wotlkconv/blp/blp.py)

BLP2 container read/write. Header layout (1172 bytes, little-endian):: char magic[4] 'BLP2' uint32 version 1
uint8 compression 1 palette, 2 block-compressed, 3/4 raw BGRA uint8 alpha_size 0, 1, 4 or 8 bits uint8
alpha_type "preferred format" -- see PreferredFormat uint8 has_mips uint32 width, height uint32
mip_offsets[16] uint32 mip_sizes[16] uint32 palette[256] BGRA, present whatever the compression is 3.3.5a
understands compression 1, 2 (with alpha_type 0/1/7) and 3. Legion-era files additionally use alpha_type 11
(BC5) for normal maps, which is what makes a straight copy of a modern texture fail on the old client.

## Converter/wotlkconv/blp/convert.py

[Source](../sources/Converter/wotlkconv/blp/convert.py)

BLP downgrade: make any modern texture something 3.3.5a can sample. Three things break a modern BLP on the old
client: 1. ``alpha_type = 11`` (BC5). Legion normal maps use it and 3.3.5a has no decoder, so the texture has
to be transcoded. 2. Non-power-of-two dimensions, which the old client only tolerates for unmipped UI
textures. 3. Sheer size. The 32-bit 3.3.5a binary has a small texture budget and 2K/4K art from Dragonflight
will evict everything else. When none of those apply -- which is the common case, because Blizzard still ships
DXT1/DXT5 for most diffuse art -- the block payload is copied through untouched so no generation loss is
introduced.

## Converter/wotlkconv/blp/image.py

[Source](../sources/Converter/wotlkconv/blp/image.py)

A tiny RGBA image buffer with the resampling the BLP pipeline needs. Deliberately not Pillow: the converter
must work on a bare Python install, and the only operations required are box-downscale, bilinear upscale and
mip chain generation.

## Converter/wotlkconv/blp/quantize.py

[Source](../sources/Converter/wotlkconv/blp/quantize.py)

Median-cut palette generation for BLP2 ``compression = 1`` textures. Palettised BLPs are still the right
choice for two things 3.3.5a cares about: UI art, where DXT ringing is obvious against flat colour, and
minimap tiles. The algorithm is plain median cut with a per-box average representative, which is what
Blizzard's own BLP tooling produced.

## Converter/wotlkconv/casc/__init__.py

[Source](../sources/Converter/wotlkconv/casc/__init__.py)

Reading a local CASC install (Warlords of Draenor and later). CASC replaced MPQ as World of Warcraft's storage
format, and everything the converter wants lives inside it. This package implements enough of it to pull files
out by FileDataID: BLTE decoding, the local ``.idx`` indices, the encoding table and the root table. Only
local installs are read; nothing is fetched from Blizzard's CDN, and ``CascStorage.coverage`` reports how much
of the build that leaves readable.

## Converter/wotlkconv/casc/blte.py

[Source](../sources/Converter/wotlkconv/casc/blte.py)

BLTE -- the block container everything in CASC is wrapped in. Every file stored in a CASC archive is a BLTE
stream: a header listing chunks, then the chunks themselves, each tagged with how it was encoded. Decoding is
the first thing that has to work before any of the higher-level tables (encoding, root) can even be read,
because those are BLTE-encoded too. Chunk modes ----------- ``N`` stored verbatim, ``Z`` zlib, ``4`` LZ4
block, ``F`` a nested BLTE stream, ``E`` encrypted (Salsa20 or ARC4) wrapping one of the others. Note the
header and chunk sizes are **big-endian**, unlike every other Blizzard format.

## Converter/wotlkconv/casc/cdn.py

[Source](../sources/Converter/wotlkconv/casc/cdn.py)

Files a partial install does not store, fetched from Blizzard's CDN. A retail install streams some of its
build on demand -- on 12.1.0.69814, 4,550 files (9.6 GB) including world map textures, voice-over and a few
models. Everything needed to find them is already on disk: * ``.build.info`` names the CDN hosts and path; *
the CDN config (``Data/config/..``) lists the build's archives; * ``Data/indices`` holds every archive's
``.index``, the *archive-group* index that merges them (encoding key -> archive, offset, size), and the index
of loose files kept outside any archive. So a missing file is located locally, and only its own bytes are
fetched: an HTTP range request into the archive that holds it, or the loose file whole. Nothing is trusted on
arrival. An encoding key is the MD5 of the BLTE header it names (checked on every one of 99 locally stored
files), so a download that does not hash to its key is rejected; the storage additionally checks that the
decoded content hashes to its content key. Verified downloads are cached by encoding key, so parallel workers
and later runs never fetch a file twice.

## Converter/wotlkconv/casc/config.py

[Source](../sources/Converter/wotlkconv/casc/config.py)

``.build.info`` and the build/CDN config files. A CASC install bootstraps like this:: .build.info -> the
active build's config hash Data/config/xx/yy/… -> build config: hashes of the root and encoding files
Data/data/*.idx -> where an EKey lives inside data.NNN Data/data/data.NNN -> the bytes ``.build.info`` is a
``|``-separated table whose header row carries typed column names (``Build Key!HEX:16``); the build config is
plain ``key = value`` lines where a value may be several space-separated hashes.

## Converter/wotlkconv/casc/encoding.py

[Source](../sources/Converter/wotlkconv/casc/encoding.py)

The encoding table: content key -> encoding key. Everything else in CASC names files by *content* key (the MD5
of the file's bytes), but the archives are indexed by *encoding* key (the MD5 of the BLTE stream those bytes
are stored as). The encoding table is the bridge, and it is itself stored BLTE-encoded and referenced by EKey,
which is why the build config lists both keys for it. Layout (all multi-byte fields big-endian):: char
magic[2] = "EN" uint8 version, cKeySize, eKeySize uint16 cKeyPageKiB, eKeyPageKiB uint32 cKeyPageCount,
eKeyPageCount uint8 unused uint32 especBlockSize char espec[especBlockSize] struct { uint8 firstKey[cKeySize];
uint8 pageMd5[16]; } cKeyPageIndex[...] uint8 cKeyPages[cKeyPageCount][cKeyPageKiB * 1024] Each page holds
entries of ``uint8 keyCount; uint40 fileSize; cKey; eKey*n`` until a zero ``keyCount`` marks the end of the
page.

## Converter/wotlkconv/casc/index.py

[Source](../sources/Converter/wotlkconv/casc/index.py)

Local CASC indices -- ``Data/data/*.idx``. Each ``.idx`` covers one of sixteen buckets and maps the first nine
bytes of an EKey to a position inside a ``data.NNN`` archive. Which bucket a key lives in is derived from the
key itself, so a lookup only ever has to parse one index file; they are loaded lazily and cached. Entry layout
(18 bytes):: uint8 key[9] first nine bytes of the EKey uint40 position big-endian: top 10 bits archive number,
low 30 offset uint32 size little-endian, the whole archive entry incl. its header

## Converter/wotlkconv/casc/keys.py

[Source](../sources/Converter/wotlkconv/casc/keys.py)

Encryption keys for BLTE ``E`` chunks. Blizzard encrypts unreleased content and the keys surface later, so the
key ring is data rather than code: users point ``--casc-keys`` at the community ``WoW.txt`` (or any file of
``<16 hex key name> <32 hex key>`` lines) and previously unreadable files start decoding. No keys are bundled.
Without one, encrypted files are reported per file and skipped rather than failing the run.

## Converter/wotlkconv/casc/root.py

[Source](../sources/Converter/wotlkconv/casc/root.py)

The root table: FileDataID -> content key. This is the file that makes FileDataIDs mean anything. Three shapes
exist: *Pre-8.2* -- a bare sequence of blocks, each ``numRecords, contentFlags, localeFlags`` followed by ID
deltas, content keys and name hashes. *8.2 and later* -- the same blocks behind a ``TSFM`` header, with name
hashes omitted when the block's content flags say so. 10.1.7 added an explicit header-size/version prefix,
which is detected rather than assumed. *Header version 2* (11.1 onwards) -- the block header grows to 17 bytes
and reorders: ``numRecords, localeFlags, flags1, flags2, flags3:u8``. The content flags this reader needs sit
in the first two words (platform and violence bits in ``flags1``, no-name-hash in ``flags2``); the trailing
byte is not interpreted. FileDataIDs are stored as deltas: ``id = previous + delta + 1``. One FileDataID can
be listed by several blocks -- per locale, a low-violence variant beside the normal one, a macOS variant
beside the Windows one -- and the low-violence copy is not reliably listed last. Blocks are therefore ranked,
and each FileDataID resolves to the best-ranked block that lists it rather than to whichever came first.

## Converter/wotlkconv/casc/salsa20.py

[Source](../sources/Converter/wotlkconv/casc/salsa20.py)

Stream ciphers used by BLTE's encrypted (``E``) chunks. Blizzard ships unreleased content encrypted and
publishes the keys later, so a CASC reader that cannot decrypt is a CASC reader that silently misses files.
Both ciphers are tiny, so they are implemented here rather than pulling in a crypto dependency for two
algorithms used on a handful of files. Nothing here is used to protect data -- it only reads what Blizzard
wrote.

## Converter/wotlkconv/casc/storage.py

[Source](../sources/Converter/wotlkconv/casc/storage.py)

Reading files straight out of a local CASC install. Putting the pieces together, resolving one FileDataID
means:: root FileDataID -> content key encoding content key -> encoding key index encoding key -> (archive
number, offset, size) data.NNN bytes at that offset, behind a 30-byte entry header BLTE decode the stream Only
*local* storage is read, and that is a real boundary rather than a limitation to work around. A modern install
is a catalogue with a cache behind it: the root table lists every file the build has, while the archives on
disk hold only what this machine has actually downloaded. The rest is streamed from Blizzard's CDN as the game
asks for it. Fetching those would mean pulling content the user has not installed, from Blizzard's servers, on
their connection -- so this tool does not. A file that is listed but not stored is reported as not installed,
with the difference spelled out, and :meth:`CascStorage.coverage` says up front how much of the build is
actually readable here, so the gap is known before a conversion run rather than discovered as a pile of
failures afterwards.

## Converter/wotlkconv/chunks.py

[Source](../sources/Converter/wotlkconv/chunks.py)

Generic IFF-style chunk handling. Every chunked Blizzard format uses the same physical layout:: char magic[4]
uint32 size uint8 data[size] The catch is the spelling of ``magic``. ADT/WDT/WMO store it byte-reversed
("REVM" for ``MVER``), while the M2 chunk table introduced in Legion stores it in reading order ("MD21").
Rather than hard-coding a guess per format, a :class:`ChunkReader` can be told which convention to use, or
asked to work it out from a set of names it expects to see.

## Converter/wotlkconv/cli.py

[Source](../sources/Converter/wotlkconv/cli.py)

Command line interface. wotlkconv convert IN... -o OUT downgrade assets into OUT wotlkconv inspect FILE...
report what a file is and whether 3.3.5a can load it wotlkconv plan IN... list what a convert run would do
wotlkconv listfile PATH sanity-check a community listfile wotlkconv casc info|list|extract read a game install
directly wotlkconv db convert|tables turn client databases into 3.3.5a .dbc

Parser declarations:

```python
parser.add_argument('--version', action='version', version=f'wotlkconv {__version__}')
common.add_argument('-v', '--verbose', action='count', default=0, help='show per-file detail; repeat for debug output')
common.add_argument('-q', '--quiet', action='store_true', help='only report errors')
common.add_argument('--no-color', action='store_true', help='disable coloured output')
sub.add_parser('convert', parents=[common, casc_opts, db_opts], help='downgrade assets for 3.3.5a')
conv.add_argument('-o', '--out', required=True, metavar='DIR', help='destination directory')
conv.add_argument('--no-recursive', action='store_true', help='do not descend into subdirectories')
refs.add_argument('--flatten', action='store_true', help='write every output into the destination root')
sel.add_argument('--include-from', metavar='PATH', help='file of globs, one per line (# comments allowed)')
tex.add_argument('--allow-npot', action='store_true', help='keep non-power-of-two dimensions instead of resizing')
mdl.add_argument('--strip-particles', action='store_true', help='remove particle emitters')
mdl.add_argument('--strip-ribbons', action='store_true', help='remove ribbon emitters')
mdl.add_argument('--strip-cameras', action='store_true', help='remove cameras')
mdl.add_argument('--strip-lights', action='store_true', help='remove lights')
mdl.add_argument('--strict', action='store_true', help='treat exceeding a 3.3.5a soft limit as an error')
mdl.add_argument('--no-merge-adt', action='store_true', help='do not merge split terrain tiles')
outg.add_argument('-f', '--overwrite', action='store_true', help='replace files that already exist')
outg.add_argument('-n', '--dry-run', action='store_true', help='convert but write nothing')
outg.add_argument('--report', metavar='PATH', help='write a machine-readable JSON report')
sub.add_parser('inspect', parents=[common], help='describe files and their 3.3.5a compatibility')
insp.add_argument('inputs', nargs='+', metavar='FILE')
insp.add_argument('--json', action='store_true', help='emit JSON')
sub.add_parser('plan', parents=[common], help='list the work a convert run would do')
pl.add_argument('inputs', nargs='+', metavar='IN')
pl.add_argument('--no-recursive', action='store_true')
sub.add_parser('build', parents=[common, casc_opts, db_opts], help='extract and convert a whole patch in one go')
bld.add_argument('inputs', nargs='*', metavar='IN', help='folders to build from; omit when reading --casc')
bld.add_argument('-o', '--out', required=True, metavar='DIR', help='destination directory for the finished patch')
bld.add_argument('-l', '--listfile', metavar='PATH', help='community listfile; fetched with --fetch if absent')
bld.add_argument('-s', '--search-dir', action='append', default=[], metavar='DIR')
bld.add_argument('--cache-dir', metavar='DIR', help='where --fetch keeps its downloads (default: ~/.cache/wotlkconv)')
bld.add_argument('--exclude', action='append', default=[], metavar='GLOB')
bld.add_argument('--include-from', metavar='PATH')
bld.add_argument('--fileid', action='append', default=[], type=int, metavar='ID')
bld.add_argument('-j', '--jobs', type=int, default=1, metavar='N')
bld.add_argument('-f', '--overwrite', action='store_true')
bld.add_argument('-n', '--dry-run', action='store_true')
sub.add_parser('casc', parents=[common, casc_opts], help='inspect or extract from a game install')
casc_sub.add_parser('info', parents=[common, casc_opts], help='show what build the install holds')
casc_sub.add_parser('list', parents=[common, casc_opts], help='list files matching a path glob')
cl.add_argument('--include', action='append', default=[], metavar='GLOB')
cl.add_argument('-l', '--listfile', metavar='PATH')
cl.add_argument('--limit', type=int, default=100, metavar='N')
casc_sub.add_parser('extract', parents=[common, casc_opts], help='extract files without converting them')
ce.add_argument('-o', '--out', required=True, metavar='DIR')
ce.add_argument('--include', action='append', default=[], metavar='GLOB')
ce.add_argument('--fileid', action='append', default=[], type=int, metavar='ID')
ce.add_argument('-l', '--listfile', metavar='PATH')
ce.add_argument('-f', '--overwrite', action='store_true')
sub.add_parser('db', parents=[common], help='convert client databases to 3.3.5a .dbc')
db_sub.add_parser('convert', parents=[common, db_opts], help='convert .db2 files into .dbc')
dc.add_argument('inputs', nargs='+', metavar='FILE')
dc.add_argument('-o', '--out', required=True, metavar='DIR')
dc.add_argument('-l', '--listfile', metavar='PATH')
dc.add_argument('--table', metavar='NAME', help='table name, when the filename does not carry it')
dc.add_argument('-f', '--overwrite', action='store_true')
dc.add_argument('--report', metavar='PATH')
db_sub.add_parser('tables', parents=[common], help='list the tables that have a mapping')
dt.add_argument('--db-mappings', metavar='DIR')
dt.add_argument('--verbose-columns', action='store_true', help="also print each mapping's columns")
sub.add_parser('listfile', parents=[common], help='sanity-check a community listfile')
lf.add_argument('path', metavar='PATH')
```

Long declarations for this entry are preserved in the linked tool-index.json.

## Converter/wotlkconv/db/__init__.py

[Source](../sources/Converter/wotlkconv/db/__init__.py)

Client database reading and downgrading (``.db2`` -> ``.dbc``).

## Converter/wotlkconv/db/bits.py

[Source](../sources/Converter/wotlkconv/db/bits.py)

Little-endian bit-field reading. From Legion onwards a DB2 record is not a struct but a bit stream: a column
may start mid-byte and be any width from 1 to 64 bits, chosen per column to be just wide enough for the values
that table actually holds.

## Converter/wotlkconv/db/convert.py

[Source](../sources/Converter/wotlkconv/db/convert.py)

Turning a modern ``.db2`` into a 3.3.5a ``.dbc``. Two things have to line up: the *data*, which comes out of
the DB2 with column names supplied by a DBD definition, and the *layout*, which comes from a mapping file and
ideally from the user's own client ``.dbc`` used as a template. Merging onto a template is the normal case.
Converting a model is useless until something references it, and what references it is a row in a table the
user already has -- so new rows are appended to their existing table rather than replacing it, and ``--id-
offset`` moves the modern ids into a range that will not collide with Blizzard's.

## Converter/wotlkconv/db/db2.py

[Source](../sources/Converter/wotlkconv/db/db2.py)

Reading modern client databases (``.db2``). Cataclysm renamed ``.dbc`` to ``.db2`` and, from Legion onwards,
stopped storing records as plain structs. A WDC-family table packs each column to the minimum width its values
need, hoists constant columns into a side table, and replaces repeated values with indices into a palette.
Records can also be scattered across sections, duplicated through a copy table, addressed by a sparse offset
map, and -- for unreleased content -- encrypted. Supported magics: =========== =============================
=================================== ``WDC5`` The War Within WDC4 body behind a schema string ``WDC4``
Dragonflight as WDC3 ``WDC3`` BfA 8.2 .. Shadowlands sections, 40-byte section header ``WDC2`` BfA 8.0
sections, 36-byte section header ``WDC1`` Legion 7.3 bitpacking, one implicit section ===========
============================= =================================== Earlier magics (``WDB2`` through ``WDB6``,
Cataclysm to Legion 7.2) are refused rather than read. They lay their records out differently enough -- no
field-storage table, and string offsets measured from the string block rather than from the field -- that
reading one as if it were a WDC would produce plausible-looking wrong values instead of an error. Every build
that ships assets this tool converts uses WDC1 or later. Column names, types and array sizes come from a DBD
definition matched on the file's own layout hash; without one the columns are still readable, just anonymous.

## Converter/wotlkconv/db/dbc.py

[Source](../sources/Converter/wotlkconv/db/dbc.py)

3.3.5a client databases (``.dbc``). The format is as simple as the modern one is not:: char magic[4] = 'WDBC'
uint32 record_count uint32 field_count uint32 record_size == the sum of the field widths uint32
string_block_size uint8 records[record_count][record_size] uint8 strings[string_block_size] Nearly every field
is four bytes, but not all: five of a 3.3.5a client's tables pack some columns into single bytes
(CharBaseInfo, CharStartOutfit, PowerDisplay, SpellChainEffects, SpellItemEnchantmentCondition), and the
header records only the total. The definitions' widths reproduce the record size of every one of a clean
client's 245 tables, so a caller that knows the layout passes ``field_sizes``; without it the four-byte layout
is required. Nothing in the file says whether a field is an int, a float or an offset into the string block
either -- the client knows, and any tool has to be told. That matters for merging. When new rows are appended
to a table the user already has, this module **keeps the original records and string block byte for byte and
appends to them**. Existing string offsets stay valid, so the merge needs to know the types only of the fields
it actually writes, never of the ones it copies through. Getting a field type wrong elsewhere in the row
cannot corrupt anything.

## Converter/wotlkconv/db/dbd.py

[Source](../sources/Converter/wotlkconv/db/dbd.py)

Parsing wowdev DBDefs, so modern database columns have names. A ``.db2`` carries no column names -- only
widths and offsets. The community DBDefs repository supplies the names, types and array sizes, keyed by
*layout hash*, which is a value the file itself carries. Matching on that rather than on a build string is
exact: a table whose shape has not changed keeps the same hash across many builds. Definition file shape::
COLUMNS int ID int<CreatureModelData::ID> ModelID string ModelName float GeoBox[6] LAYOUT 1FE1BDA4, 3B0C8F12
BUILD 9.0.1.34490 $id$ID<32> ModelID<32> ModelName GeoBox[6] Annotations inside ``$...$`` mark the id column,
columns held outside the record ("noninline"), and relationship columns.

## Converter/wotlkconv/db/grounddoodad.py

[Source](../sources/Converter/wotlkconv/db/grounddoodad.py)

Ground clutter: the grass and pebbles GroundEffectDoodad names. 3.3.5a's ``GroundEffectDoodad.Doodadpath`` is
a bare file name such as ``ElwFlo01.mdl``, which the client loads from ``World\NoDXT\Detail\``. Retail names
the model by FileDataID instead, and most of those models still sit in that folder -- but a few hundred have
moved elsewhere (``models\world\nodxt\detail``, expansion doodad folders). Those get a copy in
``world\nodxt\detail`` under their own name, or under their name plus their FileDataID when a different model
already has that name, and the table points at the copy.

## Converter/wotlkconv/db/itemdisplay.py

[Source](../sources/Converter/wotlkconv/db/itemdisplay.py)

ItemDisplayInfo: joining a modern item display back into Wrath's one row. Wrath's ItemDisplayInfo names
everything itself -- model and texture file names, eight armour texture components, an icon. Modern builds
keep none of that on the row: models and textures are resource ids resolved through
ModelFileData/TextureFileData (with race, gender, class and position carried by
ComponentModelFileData/ComponentTextureFileData), the armour components live in ItemDisplayInfoMaterialRes,
and the icon belongs to an ItemAppearance. Every rule here was measured against a clean 3.3.5a client's own
ItemDisplayInfo.dbc on the 36,438 display ids both builds share (12.1.0.69814): ====================
========================================== ========== column source agreement ====================
========================================== ========== ModelName[0/1] ModelResourcesID -> ModelFileData 99.9 /
99.8% ModelTexture[0/1] ModelMaterialResourcesID -> TextureFileData 98.5 / 96.3% Texture[0..7]
ItemDisplayInfoMaterialRes by section 99.2% InventoryIcon[0] lowest ItemAppearance -> DefaultIconFileData
80.1% [1] SpellVisualID ItemRangedDisplayInfo.CastSpellVisualID 100% GroupSoundIndex lowest item's
ItemGroupSoundsID 70.1% [2] HelmetGeosetVisID HelmetGeosetVis 100% ====================
========================================== ========== [1] An icon belongs to an item, and several items share
a display; no choice per display can beat 85.5%. [2] Wrath items have since been relinked to other displays;
the value itself agrees 98% on Wrath's own items. A name in the table is only useful if the client finds a
file by it, and the client looks in fixed places with fixed spellings. So this module also says which
converted files must additionally be written where, and under what name --
:meth:`ItemDisplayResolver.asset_aliases` -- from the same functions that produce the column values, so the
two cannot drift apart: * helmets: Wrath stores ``Helm_X`` and loads ``Helm_X_<race prefix><M|F>.m2``; modern
files are often ``helm_x_hu_m.m2``; * armour textures: Wrath stores ``<base>`` (with its ``_AU``/``_TL``..
section suffix) and loads ``<section>Texture\<base>_<U|M|F>.blp``; modern names often carry a FileDataID
suffix after the gender letter; * model textures must sit beside the model, icons in ``Interface\Icons``.

## Converter/wotlkconv/db/lightbands.py

[Source](../sources/Converter/wotlkconv/db/lightbands.py)

LightIntBand and LightFloatBand, rebuilt from LightData. 3.3.5a keeps a sky's day cycle in two tables
addressed by arithmetic on the LightParams id: eighteen colour bands at ``id * 18 - 17 + n`` and six float
bands at ``id * 6 - 5 + n``, each up to sixteen (time, value) keys. Legion folded both into LightData -- one
row per param per time of day, one column per band -- and the old tables are gone, so a converted LightParams
names skies 3.3.5a cannot find. The columns were matched to the bands against a clean 3.3.5a client, over the
615 params whose key times are unchanged since Wrath: each colour band has exactly one column whose values
agree, the fog distance, fog multiplier and cloud density float bands likewise. The other three float bands
have no column any more; 3.3.5a's own tables hold one value in nearly every key (1.0, 0.95 and 1.0), which is
written instead.

## Converter/wotlkconv/db/liquidtypes.py

[Source](../sources/Converter/wotlkconv/db/liquidtypes.py)

LiquidType textures and materials 3.3.5a can draw. 3.3.5a animates a liquid from ``Texture[0]``, a ``%d``
pattern it fills in with frames 1 to 30 -- every animation in its own archives has exactly those thirty -- and
draws it with one of three LiquidMaterials: water, magma or procedural water. Legion rebuilt liquids around
new materials that take a set of still textures (shallow, deep, specular, shore, emissive), so most retail
liquid types have no animation in ``Texture[0]`` at all, and a few have one whose frames are not all the same
size. 3.3.5a (and Noggit, which loads the frames as one texture array) cannot use either. A type whose
animation is complete keeps its textures and, if 3.3.5a has it, its material. Any other type gets the textures
and material of the 3.3.5a liquid of the same kind (``SoundBank``: water, ocean, magma, slime), taken from the
client's own first four LiquidType rows.

## Converter/wotlkconv/db/mapping.py

[Source](../sources/Converter/wotlkconv/db/mapping.py)

Declarative DB2 column -> DBC column mappings. Both sides of a conversion come from DBDefs: the modern layout
from the file's own hash, the 3.3.5a one from the table's ``BUILD 3.3.5.12340`` layout. Because both are
named, columns whose names survived map themselves -- see :func:`wotlkconv.db.target.auto_map`. A mapping file
only has to describe what actually changed. { "table": "CreatureDisplayInfo", "columns": [ {"target":
"TextureVariation", "array_index": 0, "type": "string", "from": "TextureVariationFileDataID", "transform":
"basename"}, {"target": "ModelID", "from": "ModelID", "id_offset": true} ] } ``target`` names the 3.3.5a
column; ``index`` addresses it by position instead, for the rare table with no definition covering Wrath.
Columns the mapping does not list and auto-mapping cannot match are written as zero. ``from`` may be a list,
in which case the first column the source actually has wins -- which is how one mapping covers several builds
whose column names drifted.

## Converter/wotlkconv/db/tables.py

[Source](../sources/Converter/wotlkconv/db/tables.py)

Other client databases, read on demand while converting one. Most tables convert on their own. A few cannot:
modern ItemDisplayInfo no longer names its models, textures or icon, and reaching them means joining
ModelFileData, TextureFileData, ItemDisplayInfoMaterialRes, ItemAppearance and more. This gives a conversion
those tables -- out of the install it is reading, or out of a folder of extracted ``.db2`` files -- parsed
once and indexed on the columns the joins use.

## Converter/wotlkconv/db/target.py

[Source](../sources/Converter/wotlkconv/db/target.py)

Working out the 3.3.5a side of a table. The layouts this converter writes into used to be hardcoded guesses,
which is the worst place for a guess: a `.dbc` with the wrong number of columns loads and renders nonsense
rather than failing. They do not have to be guessed. DBDefs carries a ``BUILD 3.3.5.12340`` layout for every
table that existed in Wrath, listing exactly the columns that build had, in order, with their types and array
sizes. That is the same source the modern side of the conversion already depends on, and it is authoritative
in a way a hand-written table never is -- so it is used in preference to anything the mapping declares, and a
template `.dbc` cross-checks it. Because both sides are then named, most columns map themselves: a modern
``CollisionHeight`` and a Wrath ``CollisionHeight`` are the same thing. A mapping file only has to describe
the columns that actually changed -- the FileDataIDs that used to be paths, and the handful Blizzard renamed.

## Converter/wotlkconv/detect.py

[Source](../sources/Converter/wotlkconv/detect.py)

Working out what a file actually is. Extensions are a hint, not proof: assets extracted by FileDataID arrive
as ``1234567.unknown``, and ``.wmo`` covers both roots and groups. Detection therefore always looks at the
bytes. That applies to every format, not only the ones this tool converts. A build read straight out of CASC
has no filenames at all -- the listfile supplies them, and it never covers everything -- so a sound or a font
that is only recognised by its extension has no extension to be recognised by, and would land as an anonymous
``.bin`` that no client will ever look up. Each family below is therefore identified by its signature as well,
so a file keeps its identity even when nothing names it.

## Converter/wotlkconv/errors.py

[Source](../sources/Converter/wotlkconv/errors.py)

Exception hierarchy for the converter.

## Converter/wotlkconv/fetch.py

[Source](../sources/Converter/wotlkconv/fetch.py)

Getting the two things a patch build needs but the game does not ship. A conversion is only as good as its
references. Modern assets name their textures, models and animations by FileDataID, and modern databases carry
no column names at all, so without the community listfile every reference comes out empty and without
WoWDBDefs every table is refused. Both are public, both are maintained by the same community that documented
the formats, and neither is in the game folder. Fetching them is therefore useful but never automatic. It
reaches out to the network, downloads a couple of hundred megabytes and writes to a cache directory, and a
tool should not do any of that because it felt like it -- ``--fetch`` asks for it explicitly, the URLs are
named in the output, and anything already cached is reused rather than downloaded again.

## Converter/wotlkconv/limits.py

[Source](../sources/Converter/wotlkconv/limits.py)

Hard and soft limits of the 3.3.5a (build 12340) client. "Hard" means the client will refuse to load or will
crash; "soft" means the asset loads but renders wrongly, or only works because live Blizzard data never went
that far. Everything here is used by the validators so that a conversion either produces a file the 3.3.5a
client accepts, or says clearly why it can't.

## Converter/wotlkconv/liquid.py

[Source](../sources/Converter/wotlkconv/liquid.py)

Liquid volumes -- ``.wlw``, ``.wlm`` and ``.wlq``. Retail ships a handful of these beside its maps, and
**3.3.5a never loads them.** It takes liquid from each terrain tile's ``MCLQ``/``MH2O`` and each world
object's ``MLIQ``; none of its archives contains a liquid volume, and its executable has no file name pattern
that could ask for one (it has the ones for ``.adt`` and ``.wdt``). So they are recognised -- by signature,
since retail's are unnamed -- and skipped with that reason, never converted or copied. This module still reads
the header, for ``inspect`` and for the report. The layout below is proven on every liquid volume in
12.1.0.69814 (106 files) and MoP Classic 5.5.4 (1): each is exactly ``16 + 360 x blocks + 4 + 76 x secondary
blocks + 1`` bytes, and a version 2 file with no blocks is a valid 21 bytes. Versions 0 and 1 are not present
in any build or client available to check, so their trailing layout is not enforced. ====== ======
============================================================= offset type field ====== ======
============================================================= 0x00 4s magic ``*QIL`` (``LIQ*`` reversed; both
are accepted) 0x04 u16 version 0x06 u16 unknown -- 1 in every real file 0x08 u16 liquid type: a ``LiquidType``
row id 0x0A u16 padding 0x0C u32 block count, then 360-byte blocks .. u32 secondary block count, then 76-byte
blocks .. u8 trailing byte (version 2) ====== ======
=============================================================

## Converter/wotlkconv/listfile.py

[Source](../sources/Converter/wotlkconv/listfile.py)

FileDataID -> path resolution. Legion (M2 v272) moved every asset cross-reference from an inline filename to a
numeric FileDataID. A 3.3.5a client has no FileDataID table at all -- it opens paths out of MPQ archives -- so
every reference has to be turned back into a string before the asset can be written. That mapping only exists
in the community listfile, which the user supplies. Accepted input formats (auto-detected per line): *
``1234567;world/foo/bar.m2`` -- wowdev community listfile (CSV, semicolon) * ``1234567,world/foo/bar.m2`` --
comma-separated variant * ``1234567 world/foo/bar.m2`` -- whitespace-separated variant Lines that do not start
with digits are ignored, so a header row is harmless.

## Converter/wotlkconv/log.py

[Source](../sources/Converter/wotlkconv/log.py)

Minimal levelled logging with optional ANSI colour. Kept dependency-free and separate from :mod:`logging` so
that the CLI can stay quiet by default and still emit structured per-file diagnostics.

## Converter/wotlkconv/m2/__init__.py

[Source](../sources/Converter/wotlkconv/m2/__init__.py)

M2 model reading, downgrading and writing.

## Converter/wotlkconv/m2/anim.py

[Source](../sources/Converter/wotlkconv/m2/anim.py)

External animation files. 3.3.5a reads a ``.anim`` as one flat blob: the M2's per-sequence track sub-arrays
carry offsets that point straight into it. Legion wrapped that blob in an ``AFM2`` chunk, and a model whose
rig lives in a ``.skel`` splits it three ways, each chunk addressed by its own set of tracks and each counting
its offsets from its own start: * ``AFM2`` -- the model's own tracks (colours, texture animation, particles,
and bones or attachments the model defines itself); * ``AFSB`` -- the skeleton's bones, which is where nearly
all of a character's keyframes are; * ``AFSA`` -- the skeleton's attachments. Converting lays the three end to
end and moves the skeleton tracks' offsets by wherever their chunk landed, so every track addresses the one
flat file the client opens. Dropping ``AFSB`` instead -- it looks optional, sitting beside the chunk that used
to be the whole file -- leaves every bone of an external animation pointing at keyframes that are not there.
Relocation covers the sequences the file is named after and any alias that plays them
(``SEQUENCE_ALIAS_FLAG``): an alias has no file of its own and carries the same spans, into this one. What is
not obvious for ``AFM2`` is *where* the offsets baked into the model are counted from: the start of the
``AFM2`` payload, or the start of the whole file eight bytes earlier. Guessing wrong shifts every keyframe
array by eight bytes, which does not crash -- it animates wrongly. So it is not guessed. The model names, for
each sequence it keeps outside itself, the exact ``(offset, length)`` of every keyframe array this file is
expected to hold; those spans have to fit the file, and under only one of the two readings do they land inside
it and finish exactly where it ends. That is measured per file, and the payload is emitted to match whichever
reading the spans actually support.

## Converter/wotlkconv/m2/convert.py

[Source](../sources/Converter/wotlkconv/m2/convert.py)

Top-level M2 conversion: the model plus everything that travels with it. A single ``.m2`` is never self-
contained. 3.3.5a expects to find ``<model>00.skin`` .. ``<model>03.skin`` and ``<model><anim>-<sub>.anim``
beside it, whereas a modern extraction names those files by FileDataID (or does not include them at all). This
module converts the model, then goes looking for its companions and renames them into the layout the old
client globs for.

## Converter/wotlkconv/m2/downgrade.py

[Source](../sources/Converter/wotlkconv/m2/downgrade.py)

Turning a modern M2 into one the 3.3.5a client will load. The work splits into four kinds of change:
**Container.** Unwrap ``MD21`` and drop every sibling chunk, because 3.3.5a reads a flat MD20 and stops at the
header. **Re-externalised data.** Legion moved bones, sequences and attachments into a ``.skel`` file and
every asset reference into a FileDataID. Both have to come back inline -- the skeleton merged into the model,
the IDs resolved to paths through the community listfile. **Struct layout.** ``M2Sequence``, ``M2Camera`` and
``M2Particle`` changed shape after Wrath and are mapped field by field. **Feature clamping.** Blend modes,
flag bits, emitter shapes and texture types that postdate 3.3.5a are folded onto the nearest thing the old
client renders, and every such fold is recorded on the :class:`~wotlkconv.report.FileResult` so the user knows
what changed.

## Converter/wotlkconv/m2/model.py

[Source](../sources/Converter/wotlkconv/m2/model.py)

Parsing M2 models, from Wrath's flat MD20 through to modern chunked files. Modern files (Legion 272 and
everything after) wrap the old MD20 blob in an ``MD21`` chunk and move cross-references out of the blob
entirely: textures, skins, animations and physics are named by FileDataID in sibling chunks rather than by
path. The parser normalises both shapes into one :class:`M2Model`.

## Converter/wotlkconv/m2/schemas.py

[Source](../sources/Converter/wotlkconv/m2/schemas.py)

Field schemas for every M2 sub-struct, per format era. Structs that never changed between 264 and 274 are
defined once. The three that did change get one schema per era plus a mapping in
:mod:`wotlkconv.m2.downgrade`: =============== ========================= ============================ struct
264 (Wrath) 272+ (Legion .. TWW) =============== ========================= ============================
M2Sequence ``blend_time: u32`` ``blend_time_in/out: u16`` M2Camera ``fov: f32`` (100 bytes) ``fov: M2Track``
(116 bytes) M2Particle 476 bytes 492 bytes (+multi-texture) =============== =========================
============================

## Converter/wotlkconv/m2/skel.py

[Source](../sources/Converter/wotlkconv/m2/skel.py)

Legion+ ``.skel`` skeleton files. From Legion onwards Blizzard hoisted the shared parts of a model -- bones,
key bone lookups, attachments, global loops and the sequence table -- out of the M2 and into a ``.skel`` file
referenced by the ``SKID`` chunk, so that every variant of a race or creature could share one rig. A 3.3.5a M2
has nowhere to put that: the client reads bones and sequences straight out of the model. So converting any
Legion-era character model means folding the skeleton back in, which is what this module exists to do.
Skeletons can themselves chain to a parent skeleton via ``SKPD``; the loader follows that chain and the first
definition of each section wins.

## Converter/wotlkconv/m2/skin.py

[Source](../sources/Converter/wotlkconv/m2/skin.py)

``.skin`` profiles -- the per-LOD draw data that sits next to an M2. A skin holds the vertex/index lists, the
submesh table and the draw batches. The 3.3.5a header is 48 bytes; Legion appended an
``M2Array<M2ShadowBatch>`` for its shadow pass, giving 56. Nothing else about the file changed, so a downgrade
is mostly "drop the shadow batches, then check that the model still fits inside 16-bit indices and the old
renderer's per-batch limits".

## Converter/wotlkconv/m2/split.py

[Source](../sources/Converter/wotlkconv/m2/split.py)

Compacting and splitting models that outgrew 16-bit indices. A ``.skin`` addresses the model's vertices
through a ``uint16`` array, so no skin profile -- modern or Wrath -- can reach past vertex 65 535. A model
with more than that is unrenderable by any client, not just the old one, and there are two reasons it happens:
**Dead vertices.** The model carries geometry no submesh draws. Compacting the vertex array to what is
actually referenced is lossless and usually brings the model back under the limit on its own, so it is always
tried first. **Genuinely too much geometry.** Then the model is split into several, each with its own vertex
array and skins but sharing the rig, materials and textures. That produces files nothing references yet, so
unlike the WMO case it is off by default: the user has to place the extra pieces.

## Converter/wotlkconv/m2/texcoords.py

[Source](../sources/Converter/wotlkconv/m2/texcoords.py)

Which UV set each texture unit of a batch samples. 3.3.5a answers that through the model's
``textureCoordCombos`` table (the "texture unit lookup"): a batch names a run of ``textureCount`` entries
starting at ``textureCoordComboIndex``, and each entry says 0 for the first UV set, 1 for the second, or -1
for sphere-mapped environment coordinates. The client builds the batch's shader from those values and never
checks the index. Retail stopped using the table. The vertex shader is chosen from the batch's shader id
instead, the table is written empty, and a batch's index is 0 or 0xFFFF -- past the end of it either way. A
converted model that kept that would have 3.3.5a read whatever bytes follow the table as UV selectors, and
Noggit logs every such batch and substitutes its own guess. So when a batch's run is out of range, the run it
needs is worked out and the batch pointed at it, appending to the table only what is not already there. For a
batch whose shader id carries the 0x8000 flag the retail shader table names the vertex shader, which spells
the units out (``Diffuse_T1_Env`` is UV set 0 then environment mapping). Any other batch gets the plain
reading the old client used by default: the first unit on UV set 0, the second on UV set 1. Batches already in
range are left exactly as they are.

## Converter/wotlkconv/m2/types.py

[Source](../sources/Converter/wotlkconv/m2/types.py)

Schema-driven codec for the structs inside an M2. Most M2 sub-structures (bones, colours, lights, ribbons,
attachments, events, texture transforms) are byte-identical between version 264 and version 274 -- what
changed between Wrath and Legion is the *container*, not these. Describing them as field schemas rather than
hand-written read/write pairs means one generic walker handles both directions, and the handful of structs
that really did change (M2Sequence, M2Particle, M2Camera) only need a second schema plus an explicit field
mapping. Field kinds ----------- ``('p', fmt)`` a struct.Struct format, read as a tuple (scalars unwrapped)
``('arr', kind)`` ``M2Array<kind>``; ``kind='char'`` yields a Python ``str`` ``('trk', kind)``
``M2Track<kind>`` -- per-sequence timestamp/value sub-arrays ``('trkb',)`` ``M2TrackBase`` -- timestamps only,
used by M2Event ``('ptrk', kind)`` ``M2PartTrack<kind>`` -- particle FBlock (times + values)

## Converter/wotlkconv/m2/write.py

[Source](../sources/Converter/wotlkconv/m2/write.py)

Serialising an :class:`~wotlkconv.m2.model.M2Model` as a 3.3.5a MD20. The writer is deliberately version-
locked: it only ever emits version 264 with the flat header 3.3.5a expects, no MD21 wrapper and no sibling
chunks. Layout is two-pass -- the header is emitted with zeroed ``(count, offset)`` pairs whose payloads are
queued and patched by :meth:`~wotlkconv.m2.types.DeferredWriter.flush`.

## Converter/wotlkconv/minimap.py

[Source](../sources/Converter/wotlkconv/minimap.py)

Minimap tiles, where 3.3.5a looks for them. Retail keeps a map's minimap at
``World\Minimaps\<map>\mapXX_YY.blp`` and a WMO's at ``World\Minimaps\WMO\<path>\<name>_NNN_XX_YY.blp``.
3.3.5a does not look there. It reads ``Textures\Minimap\md5translate.trs``, which maps each of those names to
a file in ``Textures\Minimap`` named by a hash:: dir: Azeroth
Azeroth\map32_48.blp<TAB>1fcd95d6d410e7557d6b62081c5e87b5.blp So each minimap tile is written under a hashed
name and the index is built to match. Blizzard hashed the file's contents; any stable unique name does, so the
name is hashed instead, which lets a tile's destination be known before it is converted. Retail's
``noliquid_`` variants have no 3.3.5a counterpart and are left where they are. The index replaces the client's
own, so it lists every minimap in the build, not just the ones a narrowed run happens to convert.

## Converter/wotlkconv/options.py

[Source](../sources/Converter/wotlkconv/options.py)

User-facing conversion knobs, shared by every format module.

## Converter/wotlkconv/pipeline.py

[Source](../sources/Converter/wotlkconv/pipeline.py)

Batch conversion: discovery, output naming and execution. The pipeline turns a pile of paths into a list of
jobs and runs them. Two things make that less trivial than it sounds: * **Terrain arrives in pieces.**
``Zone_32_48.adt``, ``_tex0`` and ``_obj0`` are one logical tile and have to be converted together, so they
are grouped by base name before any work starts. * **Extractions are named inconsistently.** A file dumped by
FileDataID has no path at all, so with a listfile the output is renamed to the in-game path the client will
look for.

## Converter/wotlkconv/report.py

[Source](../sources/Converter/wotlkconv/report.py)

Structured per-file conversion results. Downgrading is lossy by nature, and the interesting output of a batch
run is not "did it crash" but "what did it have to throw away". Every converter records those decisions here
so the CLI can print a summary and emit JSON for scripted pipelines.

## Converter/wotlkconv/resolve.py

[Source](../sources/Converter/wotlkconv/resolve.py)

Finding the sibling files a model needs. Converting one M2 pulls in its skins, its skeleton, its external
animations and its textures. Where those live on disk depends entirely on how the user extracted them, and the
three layouts in common use are: * **by FileDataID** -- ``1234567.skel`` next to ``1234568.m2``
(CASCExplorer's "no listfile" dump, and what ``wow.export`` writes in ID mode) * **by in-game path** --
``character/human/male/humanmale.m2`` mirroring the archive tree * **flat** -- everything in one directory,
basenames only :class:`AssetSource` tries all three so the caller never has to care, and can fall back to an
open CASC install when the companion was never extracted at all -- which is the normal case when converting
straight out of a game install.

## Converter/wotlkconv/wmo/__init__.py

[Source](../sources/Converter/wotlkconv/wmo/__init__.py)

WMO reading and downgrading.

## Converter/wotlkconv/wmo/bsp.py

[Source](../sources/Converter/wotlkconv/wmo/bsp.py)

Rebuilding a WMO group's collision tree. ``MOBN``/``MOBR`` hold an axis-aligned BSP over the group's
triangles, and the client uses it for every collision and line-of-sight query. Splitting a group renumbers its
triangles, which invalidates the original tree -- so the tree has to be rebuilt, not carried over. A group
without one is a group players walk through. Node layout (16 bytes):: uint16 flags 0/1/2 = split on X/Y/Z, 0x4
= leaf int16 negChild child on the negative side, -1 for none int16 posChild uint16 faceCount leaves only
uint32 faceStart leaves only: offset into MOBR float planeDist internal nodes only: where the split sits

## Converter/wotlkconv/wmo/convert.py

[Source](../sources/Converter/wotlkconv/wmo/convert.py)

WMO downgrade: root file plus every group that belongs to it.

## Converter/wotlkconv/wmo/group.py

[Source](../sources/Converter/wotlkconv/wmo/group.py)

WMO group files -- the actual geometry. A group is ``MVER`` plus one ``MOGP`` whose payload is a 68-byte
header followed by sub-chunks. The header size never changed, so the work is in the sub-chunks: * ``MOVX``
(32-bit indices) has to become ``MOVI`` (16-bit). When the group has more than 65 536 vertices that is
impossible, and the group is split into several -- see :mod:`wotlkconv.wmo.split`. * ``MPY2`` (16-bit material
ids) has to become ``MOPY`` (8-bit). * Extra ``MOTV``/``MOCV`` layers beyond the two the old renderer binds
are dropped, and the header flags that advertise them are corrected to match. * Shadowlands reused ``MOBA``'s
bounding-box bytes for a wide material id, so when that layout is detected the boxes are recomputed from the
geometry rather than left as garbage the client would cull against.

## Converter/wotlkconv/wmo/root.py

[Source](../sources/Converter/wotlkconv/wmo/root.py)

WMO root files. The nominal version never moved off 17, which makes modern WMOs look deceptively compatible.
What actually changed is where the *references* live: * ``MODI`` replaced ``MODN`` -- doodads are FileDataIDs,
not filenames, and ``MODD.nameIndex`` became an index into that array instead of a byte offset. * ``MOSI``
replaced ``MOSB`` for the skybox. * ``GFID`` lists the group files by FileDataID, where 3.3.5a globs for
``<root>_000.wmo`` .. ``<root>_NNN.wmo`` next to the root. * When ``MOTX`` is absent, ``SMOMaterial``'s
texture fields hold FileDataIDs directly rather than byte offsets into it. Add a pile of Legion/BfA-only
chunks the old parser would choke on, and the conversion is: rebuild the string tables, repoint everything at
them, clamp the material shaders, and drop what is left.

## Converter/wotlkconv/wmo/split.py

[Source](../sources/Converter/wotlkconv/wmo/split.py)

Splitting a WMO group that outgrew 16-bit indices. ``MOVI`` stores triangle indices as ``uint16``, so a 3.3.5a
group can address at most 65 536 vertices. Shadowlands introduced ``MOVX`` with 32-bit indices precisely
because groups had grown past that, and those groups cannot be narrowed -- but a WMO is a *collection* of
groups, and nothing stops it having more of them. So an oversized group is split into several, and the root
file is updated to reference them. That makes the fix self-contained: the result is one WMO with more groups,
not a set of files the user has to wire up. Each part gets its own vertex arrays, its own render batches with
recomputed bounds, and a freshly built collision tree, because the original tree indexes triangle numbers the
split invalidates.

## EsteriaWoW/modules/mod-classless-wildcard/client-addon/art-source/build_art.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-addon/art-source/build_art.py)

Rebuild the addon's die textures from the new artwork. Sources (dropped into the addon folder):
mystery_die_<rarity>_transparent.png -> reveal frames, centre is the window icon.png -> the closed die crest,
with the "?" Everything is written as 32-bit uncompressed bottom-up TGA (desc 0x08), which is what the
existing files are and what the 3.3.5 client reads. Sizes are kept identical to the files being replaced so no
layout code has to move.

## EsteriaWoW/modules/mod-classless-wildcard/client-addon/gen_rays.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-addon/gen_rays.py)

Paint ClasslessWildcard/rays.tga, the starburst that turns behind the die. The reveal already has glow.tga,
but that is a soft radial blob: measured across angles its alpha varies by 9 of 255, so rotating it would look
like nothing moving at all. This draws something with structure instead -- alternating long and short beams
radiating from a hollow centre -- so the addon can spin it and have the spin read. White, with all the shape
in the alpha channel: the addon tints it per rarity with SetVertexColor and blends it additively, so one file
serves every tier. The centre is empty because the die covers it, and the alpha falls to zero well inside the
edges. That matters: 3.3.5 has no Texture:SetRotation, so rotation is done by feeding SetTexCoord a rotated
quad, whose corners sample outside 0..1 and clamp to the edge pixels. With a transparent border there is
nothing there to smear. python3 gen_rays.py # writes ClasslessWildcard/rays.tga Deterministic: same output
every run, so a rebuild is a no-op in git unless the numbers below change.

## EsteriaWoW/modules/mod-classless-wildcard/client-addon/syntaxcheck.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-addon/syntaxcheck.py)

Syntax-check the addon's Lua against the interpreter the game actually runs. WoW 3.3.5a embeds Lua 5.1.
Checking against anything newer is worse than not checking: 5.2+ accept syntax 5.1 rejects (goto, integer
division, \z escapes), so a file could pass here and still error out on login. This only COMPILES the chunk.
Nothing is executed, so the WoW API being absent does not matter -- undefined globals are a runtime concern,
not a syntax one. Run: python3 syntaxcheck.py (checks every .lua beside this script) python3 syntaxcheck.py
FILE ... (checks the files named) Needs lupa: python3 -m pip install --user lupa

## EsteriaWoW/modules/mod-classless-wildcard/client-addon/test_addon_flow.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-addon/test_addon_flow.py)

Load the whole addon under Lua 5.1 against a stubbed WoW API and drive it with server messages, without a game
client. syntaxcheck.py proves the addon parses and test_statpanel.py proves one pair of text helpers. This
goes further: it runs the file top to bottom the way the client would, feeds it the same pipe-delimited
messages the server sends, and clicks its buttons, so a nil field or a wrong branch in a message handler fails
here instead of as a red error box in game. The WoW API is faked with one generic "stub" object: any
CapitalCase method works (Show/Hide/IsShown/SetText/GetText/SetScript/Enable/Disable track their state, size
getters return numbers, everything else returns another stub), and lowercase fields behave like a plain table
so the addon's own bookkeeping on frames is untouched. Only the API calls whose return values the addon reads
are spelled out. Covered flows: * the Archetypes button and flyout (Classless only, mirrors the NPC's "Apply a
starter archetype" menu) * the first-login wizard: path page, archetype page, sizing, empty slate Run: python3
test_addon_flow.py

## EsteriaWoW/modules/mod-classless-wildcard/client-addon/test_statpanel.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-addon/test_statpanel.py)

Render the stat-panel strings under Lua 5.1, without a game client. The syntax checker only proves the addon
parses. This proves the per-point text a player actually reads comes out right, by lifting the
Rate/StatPerPoint pair straight out of the addon and running them against a stubbed CW.stats -- the same shape
the server fills in from the ST message. Run: python3 test_statpanel.py

## EsteriaWoW/modules/mod-classless-wildcard/client-patch/install.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-patch/install.py)

One-step client setup for mod-classless-wildcard. Point this at a World of Warcraft 3.3.5a folder and it does
everything the client side needs: * builds a data patch from the player's OWN client files and drops it in
Data/ (every class shows as Hero; the creation screen lists one class) * installs the ClasslessWildcard addon
* clears the client Cache so the new data is picked up The default install never modifies Wow.exe. The
optional --creation-text flag also rewrites the creation-screen class blurb; because that is a signed
interface file, --creation-text also applies the well-known "allow custom interface" patch to Wow.exe (backed
up first) so the client loads it. Confirmed working on a stock 3.3.5a build 12340 client. Off by default
because it edits the executable. Everything is reversible with --uninstall. Requires nothing but Python 3.7+.
No compiler, no StormLib, no other packages.

Parser declarations:

```python
parser.add_argument('wow_folder', nargs='?', help='the folder containing Wow.exe and Data')
parser.add_argument('--uninstall', action='store_true', help='remove everything this installer added')
parser.add_argument('--dry-run', action='store_true', help='show what would happen, write nothing')
parser.add_argument('--yes', '-y', action='store_true', help='do not ask for confirmation')
parser.add_argument('--locale', help='patch only this locale, e.g. enUS')
parser.add_argument('--name', default='Hero', help='what every class is called (default: Hero)')
parser.add_argument('--no-addon', dest='addon', action='store_false', help='do not install the in-game addon')
```

Long declarations for this entry are preserved in the linked tool-index.json.

## EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/__init__.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/__init__.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/blp.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/blp.py)

Write BLP2 textures the 3.3.5a client can read, and draw the Hero icon. Only what the client patch needs:
encode a 256-colour palettized BLP2 (the most broadly supported uncompressed BLP format) and render the class-
icon atlas so every class shows one "Hero" emblem instead of its old class icon. Palettized BLP2 layout
(encoding 1, 8-bit alpha, full mip chain) -- matched byte-for-byte against the genuine enc=1 textures the
3.3.5a client ships (header 01 08 08 01: encoding 1, alphaDepth 8, alphaType 8, hasMips 1): "BLP2" 4 bytes
type uint32 1 encoding uint8 1 (palettized) alphaDepth uint8 8 alphaType uint8 8 (8-bit alpha; NOT 0 -- 0
fails to load) hasMips uint8 1 (a full mip chain IS required, or icons break) width uint32 height uint32
mipOffsets[16] uint32 mipSizes[16] uint32 palette[256] BGRA 1024 bytes per mip level: <w*h index bytes><w*h
alpha bytes>, halving down to 1x1 Rendering uses Pillow if present; if it is not, the whole Hero-icon step is
skipped by the installer, so this stays an optional extra with no hard dependency.

## EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/charcreate.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/charcreate.py)

Make the character-creation screen read as classless. The server offers one class per race (the Warrior shell,
shown as "Hero"), so the creation screen already displays a single class button. This appends a small hook to
CharacterCreate.lua that hides that leftover button entirely, leaving the Hero name and description, so the
screen looks intentionally classless rather than like a game with exactly one class. Append-only: the client's
own CharacterCreate.lua is passed through byte for byte and the hook is added at the end, wrapping
CharacterCreateEnumerateClasses so the buttons are hidden after the original code has set everything up. Class
selection is separate state (SetCharacterClass, driven by GetSelectedClass), so hiding the buttons does not
affect character validity. This is loaded only because the exe "allow custom interface" patch is applied with
--creation-text; without it the client would reject the modified file.

## EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/clientfs.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/clientfs.py)

The client's view of its own data files. WoW does not read one archive, it reads a stack of them, and a file
in a higher-priority archive shadows the same file lower down. If we patched a base archive's copy of
ChrClasses.dbc while a community patch higher in the stack shipped its own, our edit would be invisible. So we
resolve files the way the client does -- highest priority first -- and we install our patch above everything
already present.

## EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/dbc.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/dbc.py)

The DBC edits the classless client patch needs. ChrClasses.dbc - what every class is called on screen, and
that it has a ranged slot rather than a relic slot. CharBaseInfo.dbc - which race/class pairs the creation
screen offers. SkillRaceClassInfo.dbc - which class skill lines the client accepts for the character.
SkillLineAbility.dbc - which class each class spell belongs to, which is what actually decides the spellbook's
tab set. Spell.dbc - the class tool a spell demands before it may be cast. Both are rewritten from the copy
already winning in the client's archive stack, so a community patch's version is preserved rather than
reverted.

## EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/elemental.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/elemental.py)

Elemental ability variants, client side. The generator (data/sql/generators/gen_elemental_variants.py) writes
the server's spell rows and, from the same run, elemental_manifest.json. This module turns that manifest into
the client's half: Spell.dbc one appended row per variant rank, copied from the base spell's own row in THIS
player's client and patched with the manifest's field overrides and text SpellVisual.dbc one row per variant:
the base visual with the element's impact kit SpellIcon.dbc one row per (base icon, element)
SkillLineAbility.dbc one row per variant, so it files under its base's tab Interface/Icons/ one painted icon
per (base icon, element), built from the player's own copy of the base icon Everything is appended to the
player's own tables, so a community patch's rows survive, and nothing of Blizzard's is carried in the
repository: the manifest holds ids, overrides and text, not copies of rows or art. Pillow is required by the
installer; without it apply() refuses to paint and the install stops. (Earlier versions fell back to the base
icons, which is how variants ended up looking exactly like the ability they came from.) Without it the
variants would still work and simply show their base's icon.

## EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/exepatch.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/exepatch.py)

Let a 3.3.5a Wow.exe load custom (unsigned) GlueXML / FrameXML. Replacing an interface file the client signs
-- GlueStrings.lua, for the Hero creation-screen text -- makes the client reject the whole set with "Your
login interface files are corrupt". The fix is the well-known "allow custom interface" binary patch: it forces
the interface signature-scope check to always report the accepted scope, so modified UI files load. The byte
patterns below are the ones used by the Project Reforged 3.3.5 patcher (https://github.com/Stormhand-
dev/WoW-3.3.5-Patcher---Project-Reforged), which is in use on a live server. They are applied here only after
verifying each one matches the target exe EXACTLY ONCE, so a client this set does not fit is refused rather
than corrupted. A backup is always written first, and restore() puts the original back. Each replacement is
the same length as what it replaces (in-place byte edits: je/jz/jg -> jmp, and `mov eax,1` -> `mov eax,3`), so
offsets never move.

## EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/forged.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/forged.py)

Client side of the forged spells: the Hero tab and the spells under it. What this appends to the player's own
tables: SkillLine.dbc one row, the Hero line itself. Without it the tab has no name and no icon. Spell.dbc one
row per forged spell and per hidden companion SpellVisual.dbc one row per recombined look: a donor's row with
some of its kit slots pointed elsewhere. Each kit carries its own sound, so this is where a new spell gets a
look and a sound that no stock spell has, without new art. SkillLineAbility.dbc one row per visible spell,
which is what files it under the Hero tab. Hidden companions deliberately get none. Nothing of Blizzard's
lives in the repository: the manifest holds ids and the columns each row changes, and every row is built by
copying the player's own donor row and applying that diff. A community patch's edits to columns this does not
touch survive. The row appenders for Spell.dbc and SkillLineAbility.dbc are elemental.py's, unchanged: the
manifest is written in the shape they already read, so there is one implementation of each rather than two
that can drift.

## EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/gluestrings.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/gluestrings.py)

Rewrite the character-creation screen's class copy to the classless pitch. The 3.3.5a creation screen reads
two kinds of string out of Interface\GlueXML\GlueStrings.lua: CLASS_<TOKEN> the long paragraph, |n for line
breaks CLASS_<TOKEN>_FEMALE the same paragraph, female phrasing CLASS_INFO_<TOKEN><N> the short bullet list, N
= 0..5 Every class token gets the same Hero copy, so whichever chassis a player picks reads identically. Only
those keys are touched; the other ~860 strings in the file are passed through byte for byte.

## EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/mpq.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/mpq.py)

Minimal, dependency-free MPQ reader/writer for the 3.3.5a client. Only what mod-classless-wildcard needs: pull
a handful of files out of the client's archives, and write a small patch archive back. No StormLib, no
compiler, no external packages -- players run the installer with nothing but a stock Python 3. Reading
supports the archive features WotLK-era MPQs actually use: v1-v4 headers, >4 GiB archives via the hi-block
table, encrypted files, single-unit files, sector CRCs, and zlib / bzip2 / PKWARE-DCL / stored sectors.
Writing deliberately emits the simplest thing the client accepts: a v1 archive whose files are stored
uncompressed and unencrypted. Our payloads are a few hundred KiB at most, so compression buys nothing and
every byte of it would be another way to be subtly wrong.

## EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/outfit.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/outfit.py)

Dress the character-creation preview in the Hero starter gear. CharStartOutfit.dbc drives the gear shown on
the previewed character (by DisplayInfoID). Left alone, the shell class (Paladin) previews in whatever a
Paladin starts with -- and that varies by race and shows a weapon. Instead this rebuilds every Hero's shell-
class row to wear exactly the neutral starter kit the module equips at first login (Recruit's
shirt/pants/boots), with no weapon, because the module drops the starter weapons into the bag rather than
equipping them. So the creation preview matches what a new Hero actually wears. The item ids here mirror the
module's default `StarterKit.Equip` (`38,39,40`). Their display ids and slots are resolved from the client's
own CharStartOutfit data, so nothing is invented; if a realm changes StarterKit.Equip to different armour,
update STARTER_ITEMS to match. It also fills real gaps: the Paladin shell is only vanilla-creatable by four
races, so the other six (and any race missing a row) get a shell-class row added, built the same way, so no
Hero previews naked. None of this needs the exe patch -- it is data. It ships with --creation-text only to
keep all the visual extras behind one flag.

## EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/pkware.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-patch/lib/pkware.py)

PKWARE DCL "explode" decompression, as used by some MPQ sectors. WotLK-era archives compress essentially
everything with zlib, so this path is rarely taken. It is implemented anyway because a re-packed or community
patch archive higher in the client's load order may use it. Port of the format described by Mark Adler's
blast.c: a bit stream, LSB first, with a two-byte header (literal coding mode, dictionary size) followed by
literals and length/distance back-references drawn from fixed Huffman codes.

## EsteriaWoW/modules/mod-classless-wildcard/client-patch/preview_elemental_icons.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-patch/preview_elemental_icons.py)

Render every shipped base icon in every element, from a real client's art, into one preview sheet, so a hue
change can be judged before anyone reinstalls. python3 preview_elemental_icons.py [WOW_FOLDER] [--out
preview.png] Reads the base icons through the client's archive chain exactly as the installer does, paints
them with lib/elemental.render_icon, and lays them out at twice the 36px the game draws icons at. Column one
is the untouched base. Writes nothing to the client. Needs Pillow.

Parser declarations:

```python
ap.add_argument('wow_folder', nargs='?', help='World of Warcraft 3.3.5a folder (autodetected if omitted)')
ap.add_argument('--out', default=os.path.join(HERE, 'elemental_icons_preview.png'))
ap.add_argument('--manifest', default=elemental.manifest_path())
```

## EsteriaWoW/modules/mod-classless-wildcard/client-patch/selftest.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-patch/selftest.py)

Exercise the whole client-patch pipeline against a real client, read-only. python3 selftest.py
"B:/World.of.Warcraft.3.3.5a" Resolves every source file through the client's archive stack, applies each
transform, builds the archives in a temp folder, reads them back, and checks the results. Nothing in the
client is written to. Exits non-zero on any failure.

## EsteriaWoW/modules/mod-classless-wildcard/client-patch/test_elemental.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-patch/test_elemental.py)

Check the elemental-variant client step against extracted DBCs, no client needed. python3 test_elemental.py
--dbc "B:/New folder/dbc" Appends every variant in elemental_manifest.json to real Spell, SpellVisual,
SpellIcon and SkillLineAbility tables, re-parses the results, reads the new rows back and compares them with
the manifest. Icon painting is exercised on a synthetic BLP, because the client's icon art lives in its
archives, not in a DBC extract. Exits non-zero on any failure. selftest.py covers the same step against a real
client.

Parser declarations:

```python
ap.add_argument('--dbc', required=True, help='directory holding extracted 3.3.5a DBCs')
ap.add_argument('--manifest', default=elemental.manifest_path())
```

## EsteriaWoW/modules/mod-classless-wildcard/client-patch/test_forged.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/client-patch/test_forged.py)

Check the forged spell rows before they ever reach a server. Reads the generator's own outputs --
forged_manifest.json and cw_spells_forged.sql -- and asserts the properties that keep the set safe: nothing
inherits a class family, nothing is auto-granted, nothing sits off the curve, and no hidden companion can show
up in a spellbook tab. Run: python3 test_forged.py [CLIENT_DIR] With a client directory it also applies the
rows to that client's own tables in memory and reads them back, which is the only way to know the appends land
where the game will look for them. Nothing is written to the client.

## EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/analyze_prices.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/analyze_prices.py)

What did real 3.3.5 items actually cost? Reads the core's item_template and reports median BuyPrice by
required level, quality and slot class, so our vendor prices can be based on the game's own spread instead of
invented numbers.

## EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/check_displays.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/check_displays.py)

Does every item's artwork match what the item claims to be? `displayid` drives both the inventory icon and the
3D model. Nothing in item_template ties it to `class` / `subclass` / `InventoryType`, so an item can happily
call itself a Thrown weapon while wearing a two-handed axe's icon -- which is exactly what shipped. This reads
the core's item_template, records which (class, subclass, InventoryType) combinations each display id is
really used with, and then checks every item in our packs against that. A display used by real Thrown weapons
is a valid look for our Thrown weapon; anything else is a mismatch. Run: python check_displays.py

## EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/displaypick.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/displaypick.py)

Pick artwork that actually belongs to the item. `displayid` is the single field driving both an item's
inventory icon and its 3D model and texture. Nothing in item_template ties it to `class`, `subclass` or
`InventoryType`, so a row can call itself a Thrown weapon and wear a two-handed axe's model. Several of ours
did. The only safe source of a display id is a real item of the same (class, subclass, slot): if Blizzard
hangs that art on a mail chestpiece, it is mail chest art, model and texture included. Two extra preferences
on top of that: * item level. Picking art by level means band-1 gear looks like starter gear and band-80 gear
looks like raid gear, instead of a level 1 Hero carrying a tier 10 model. * name. A candidate whose real name
shares words with ours ("Longbow", "Javelin", "Gauntlets") is the one a player would expect to see. The parsed
pool is cached in displays_pool.json so the 40 MB core dump is only read when it changes.

## EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/fix_displays.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/fix_displays.py)

Give the hand-written item packs artwork that matches what they are. The original packs picked display ids by
eye. Ten of the first twelve items were wearing art belonging to a different item type: a Thrown javelin with
a display no real item uses at all, a gun with a leather helmet's model, a shield with a fishing pole's, a
robe with a rifle's. This rewrites `displayid` in place using displaypick, which only ever offers art that
real items of the same class, subclass and slot actually wear -- so the icon, the model and the texture all
agree with the tooltip. The generated tiered gear does not need this: gen_tiered_gear.py picks from the same
pool when it builds. Run: python fix_displays.py

## EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/gen_archetypes.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/gen_archetypes.py)

Author, validate and write the starter archetypes: full level 1 to 80 build templates for the Classless path.
An archetype is a list of ability lines and talent ranks. A Hero who follows one gets its abilities bought
strictly in build order, each as soon as it is unlocked and affordable, and each talent rank as soon as its
tier, prerequisite and Talent Essence allow, in list order. The builds live in this file as spell and talent
NAMES; the script resolves them against the client's DBCs and the core's trainer data exactly the way the
module's BuildLibrary does, simulates a Hero following each build from 1 to 80 on the shipped essence
schedule, refuses to write anything that would stall, and emits ../db-world/cw_archetypes.sql. Elemental
variants ("Fiery Heroic Strike") are part of the pool too, read from the client manifest the variant generator
writes and registered the way LoadVariants does: the base line's levels and class, one rarity tier up. A build
names them like any other ability, under the base attack's class. Run: python3 gen_archetypes.py validate +
write the SQL python3 gen_archetypes.py --catalog Rogue list what the pool offers a class (abilities with
unlock level and cost, talents by tier) to pick from python3 gen_archetypes.py --dbc DIR --core DIR --conf
FILE --out FILE --manifest client-patch/elemental_manifest.json Needs the 3.3.5a DBC extract (Spell,
SkillLine, SkillLineAbility, Talent, TalentTab) and the core checkout for
data/sql/base/db_world/trainer_spell.sql and spell_ranks.sql.

Parser declarations:

```python
ap.add_argument('--dbc', default=DEFAULT_DBC)
ap.add_argument('--core', default=DEFAULT_CORE, help='AzerothCore checkout (for trainer_spell.sql, spell_ranks.sql)')
ap.add_argument('--conf', default=DEFAULT_CONF)
ap.add_argument('--out', default=OUT_SQL)
ap.add_argument('--catalog', metavar='CLASS', help='print the pool for one class and exit')
ap.add_argument('--ledger', action='store_true', help='print every purchase of the simulation')
```

Long declarations for this entry are preserved in the linked tool-index.json.

## EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/gen_elemental_variants.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/gen_elemental_variants.py)

Generate elemental variants of the pool's physical strikes. A variant is the base ability dealt as an element
instead of Physical, at 85% of the base's own weapon multiplier, with the element's own signature in the
second of the spell's three effect slots: a spell-power-scaled hit for Arcane, a lifesteal hit for Holy, a
burn for Fire, a poison for Poison, a snare for Frost, an attack-speed cut for Earth, a healing cut for
Shadow. Its tooltip is the base's own description, modified for the element. The shape is Blizzard's own Frost
Strike; see PLAN-elemental-variants.md. Reads the client's extracted DBCs and writes two things from ONE
source, so the server's numbers and the client's tooltips cannot drift: ../db-world/cw_spells_elemental.sql
server rows (spell_dbc, skilllineability_dbc, spell_ranks, cw_ability_variants) ../../../client-
patch/elemental_manifest.json what the installer appends to the player's own Spell.dbc, SpellVisual, SpellIcon
and SkillLineAbility, and the icon recipes Run: python3 gen_elemental_variants.py [--dbc DIR] [--bases
NAME,NAME,...] [--elements fire,frost,...] [--ranks first|top|all] Defaults are the shipped set: every
eligible base, every element, every rank. The Phase 1 wave was --bases "Sinister Strike,Heroic
Strike,Backstab,Raptor Strike,Claw,Maul" and the Phase 0 spike --bases "Sinister Strike" --elements fire
--ranks first

Parser declarations:

```python
ap.add_argument('--dbc', default=DEFAULT_DBC, help='directory of extracted 3.3.5a DBCs')
ap.add_argument('--bases', default='ALL', help='comma-separated base ability names, or ALL')
ap.add_argument('--elements', default='ALL', help='comma-separated element keys, or ALL')
ap.add_argument('--ranks', default='all', choices=('first', 'top', 'all'))
ap.add_argument('--coefficient', type=int, default=85, help='weapon damage kept, percent')
ap.add_argument('--sp-coefficient', type=float, default=0.15, help='spell power coefficient of the add')
ap.add_argument('--out-sql', default=OUT_SQL)
ap.add_argument('--out-manifest', default=OUT_MANIFEST)
```

## EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/gen_forged_spells.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/gen_forged_spells.py)

Build the forged spells: brand-new abilities that belong to no class. Reads the client's extracted DBCs and
writes two things from ONE source, so the server's numbers and the client's tooltips cannot drift: ../db-
world/cw_spells_forged.sql server rows (skillline_dbc, skillraceclassinfo_dbc, spell_dbc,
skilllineability_dbc, spell_ranks, cw_forged_spells) ../../../client-patch/forged_manifest.json what the
installer appends to the player's own SkillLine, Spell, SpellVisual and SkillLineAbility Run: python3
gen_forged_spells.py [--dbc DIR] [--only KEY,KEY,...] Every spell is a donor row with fields overridden, never
a row built from nothing: that way attributes, interrupt flags and equipped-item requirements come from a
spell the game already ships and already works. Damage and healing come off the anchors in CURVE, which were
measured from the median of every trainable class rank at that level. Anything the curve cannot price -- a
damage reduction, an interrupt lockout -- is a literal, checked by hand against a named spell and recorded in
the recipe's `compare` field.

Parser declarations:

```python
ap.add_argument('--dbc', default=DEFAULT_DBC)
ap.add_argument('--only', default='', help='comma separated recipe keys')
ap.add_argument('--out-sql', default=OUT_SQL)
ap.add_argument('--out-manifest', default=OUT_MANIFEST)
```

## EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/gen_item_manifest.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/gen_item_manifest.py)

Write the client manifest for our items: client-patch/items_manifest.json. The client draws a STOCK item's
icon straight away because Item.dbc already holds its class, subclass, display and slot -- GetItemIcon and
GetItemInfo read that without asking the server. A custom item has no Item.dbc row, so nothing can draw it
until the server answers an item query, and anything that renders a bag from a saved list (Bagnon and friends)
paints INV_Misc_QuestionMark instead. Clearing the client's Cache makes that worse, not better: it throws away
the one copy the client had. So the client patch appends a row per generated item. This writes what it needs.
Material and SheatheType are not in item_template. They are copied from a stock item with the same (class,
subclass, InventoryType) -- the same donor idea the spell generator uses -- so sheathing and the sound a
weapon makes stay right. Run: python gen_item_manifest.py

## EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/gen_tiered_gear.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/gen_tiered_gear.py)

Generate cw_items_tiered.sql -- classless gear across the whole level range. The first two item packs all sat
at item level 40 / required 35, so there was nothing to buy while levelling and nothing at the cap. This lays
the same "stat combination the class system would never allow" idea across nine level bands, from a fresh Hero
at level 1 to level 80. Prices come from the medians of real 3.3.5 items (analyze_prices.py), so band-1 gear
costs a few silver and a level 80 piece over a hundred gold. This file only defines the items. Which shelf the
Hero Advancement NPC puts each one on is gen_vendor_lists.py's job -- rerun it after changing anything here,
since it reads the generated SQL back to lay the shop out. Run: python gen_tiered_gear.py (writes ../db-
world/cw_items_tiered.sql)

## EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/gen_vendor_lists.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/gen_vendor_lists.py)

Lay the Hero Advancement shop out as browsable lists. SMSG_LIST_INVENTORY carries at most MAX_VENDOR_ITEMS =
150 entries and the core drops the overflow without a word, so a single flat list could never show all 250
items. Worse, one list of 250 is miserable to shop in even if it fit. WorldSession::SendListInventory(guid,
vendorEntry) reads its items from `sObjectMgr->GetNpcVendorItemList(vendorEntry)` rather than from the
creature, so one NPC can front any number of separate lists, each with its own 150 budget.
Player::BuyItemFromVendorSlot resolves purchases through WorldSession::GetCurrentVendor(), so buying works
from a sublist unchanged. The shop is split by category and then by level bracket, so any one list is small
enough to read. Nothing is hidden: every list also has an "all levels" variant, and every one of them stays
well under the cap. One thing to know if you edit this: conditions are looked up with the CREATURE's entry
(`vendor->GetEntry()` in SendListInventory), not the vendor list's, so a `conditions` row would apply to every
sublist at once. The old level-window conditions are therefore dropped -- the level brackets do that job now,
and do it visibly. Writes ../db-world/cw_world_vendor_lists.sql (applied after cw_world_base) and
../../../src/ClasslessVendorLists.h (the same layout for the gossip menu, so the two cannot drift) Run: python
gen_vendor_lists.py

## EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/reprice_items.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/reprice_items.py)

Reprice the hand-written item packs and the heirlooms. Everything was priced far too high: the packs asked
15-30 gold for level-35 gear, and the heirlooms 70-120 gold. Heirlooms in particular are meant to be bought
EARLY and grow with the character, so a price no low-level Hero can reach defeats the point of them entirely.
Prices now follow the same curve the generated tiered gear uses, and heirlooms get a flat, deliberately cheap
price so they can be picked up while levelling. The INSERT column list is parsed from each file, so this keeps
working if the column order ever changes. Run: python reprice_items.py

## EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/validate_items.py

[Source](../sources/EsteriaWoW/modules/mod-classless-wildcard/data/sql/generators/validate_items.py)

Validate every generated/hand-written item file before it reaches a DB. Display ids are checked against the
client's ItemDisplayInfo.dbc, which is what actually decides whether an item renders -- not against ids other
items happen to use.

## EsteriaWoW/src/server/game/LuaEngine/docs/ElunaDoc/__init__.py

[Source](../sources/EsteriaWoW/src/server/game/LuaEngine/docs/ElunaDoc/__init__.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/src/server/game/LuaEngine/docs/ElunaDoc/__main__.py

[Source](../sources/EsteriaWoW/src/server/game/LuaEngine/docs/ElunaDoc/__main__.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/src/server/game/LuaEngine/docs/ElunaDoc/parser.py

[Source](../sources/EsteriaWoW/src/server/game/LuaEngine/docs/ElunaDoc/parser.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/apply_darkfallen_archive_fixes.py

[Source](../sources/EsteriaWoW/tools/apply_darkfallen_archive_fixes.py)

Apply the Darkfallen archive content to the live client Z archives. This is the in-place deployment path for
an already-staged Z pair: it patches only the entries whose content changed and leaves everything else (the
multi-hundred-MB HD and asset payloads) untouched. Every entry comes from the transforms in
``tools/darkfallen_race_pack.py``, so the result matches a fresh packer run. Entries covered per archive: *
``CharacterInfo.lua`` - race metadata and the racial spell list (the list changed when Endurance was replaced
by Crimson Thirst). * ``GlueParent.lua`` / ``CharacterCreate.lua`` / ``CharacterSelect.lua`` - backdrop, fog,
lighting, portraits and faction detection (repairs the earlier Void Elf ``Races_Informations[19]`` alias and
the missing TemporaryPortrait pair). * ``ChrRaces.dbc`` - the two race rows, including the per-faction client
file strings. * ``Spell.dbc`` - the Darkfallen racial spells (Crimson Thirst, Children of the Night) and the
Cannibalize -> Vampiric Sustenance rename. * ``GlueStrings.lua`` (locale archive only) - localized race and
ability text. Archives are SHA-256 backed up before they are touched, and read back afterwards.

Parser declarations:

```python
parser.add_argument('--root-archive', required=True, type=Path)
parser.add_argument('--locale-archive', required=True, type=Path)
parser.add_argument('--backup-dir', required=True, type=Path)
parser.add_argument('--apply', action='store_true')
```

## EsteriaWoW/tools/apply_wod_clientservices_patch.py

[Source](../sources/EsteriaWoW/tools/apply_wod_clientservices_patch.py)

Library, test, or historical helper; inspect its source before use.

Parser declarations:

```python
parser.add_argument('--client-exe', type=Path, default=Path('G:\\3.3.5a - Dev\\Wow.exe'))
parser.add_argument('--donor-exe', type=Path, default=Path('F:\\Wrath of the Lich King 3.3.5a (wod models)\\Wow.exe'))
parser.add_argument('--apply', action='store_true')
```

## EsteriaWoW/tools/ascension_character_appearance_repair.py

[Source](../sources/EsteriaWoW/tools/ascension_character_appearance_repair.py)

Audit/remap saved stock-race character appearance bytes for the live Ascension HD contract.

Parser declarations:

```python
parser.add_argument('--client-root', type=Path, default=Path('G:\\3.3.5a - Dev'))
parser.add_argument('--stormlib', type=Path, default=DLL_DEFAULT)
parser.add_argument('--apply', action='store_true')
```

## EsteriaWoW/tools/ascension_customization_pack.py

[Source](../sources/EsteriaWoW/tools/ascension_customization_pack.py)

Append Ascension appearance choices without changing installed choices or models. The input ZIP must match its
GitHub tree manifest. Only playable, ordinary customizations for the ten supplied HD races are used; donor NPC
and DK data are excluded. Stage first, review merge-report.json, then install the artifacts.

Parser declarations:

```python
parser.add_argument('--self-check', action='store_true')
parser.add_argument('--workspace', type=Path, default=Path('C:\\Users\\Zach\\.codex\\tmp\\ascension-customization'))
parser.add_argument('--client', type=Path, default=Path('G:\\3.3.5a - Dev'))
```

Long declarations for this entry are preserved in the linked tool-index.json.

## EsteriaWoW/tools/ascension_hd_migration.py

[Source](../sources/EsteriaWoW/tools/ascension_hd_migration.py)

Library, test, or historical helper; inspect its source before use.

Parser declarations:

```python
parser.add_argument('--ascension-root', type=Path, required=True)
parser.add_argument('--client-archive', type=Path, action='append')
parser.add_argument('--server-base', type=Path)
parser.add_argument('--server-output', type=Path)
```

## EsteriaWoW/tools/audit_ascension_hd_tables.py

[Source](../sources/EsteriaWoW/tools/audit_ascension_hd_tables.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/audit_effective_character_dbcs.py

[Source](../sources/EsteriaWoW/tools/audit_effective_character_dbcs.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/audit_reforged_custom_collisions.py

[Source](../sources/EsteriaWoW/tools/audit_reforged_custom_collisions.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/audit_wod_appearance_ids.py

[Source](../sources/EsteriaWoW/tools/audit_wod_appearance_ids.py)

Audit stock-race appearance row IDs against the working WoD donor.

## EsteriaWoW/tools/audit_wod_asset_bytes.py

[Source](../sources/EsteriaWoW/tools/audit_wod_asset_bytes.py)

Exhaustively compare donor WoD character assets with Esteria's resolved live bytes.

## EsteriaWoW/tools/audit_wod_texture_resolution.py

[Source](../sources/EsteriaWoW/tools/audit_wod_texture_resolution.py)

Read-only audit that every donor stock-race CharSections texture resolves in Esteria.

## EsteriaWoW/tools/audit_wod_w_assets.py

[Source](../sources/EsteriaWoW/tools/audit_wod_w_assets.py)

Audit visible and directly-addressable WoD patch-w character assets against live Esteria.

## EsteriaWoW/tools/cars_mount_pack.py

[Source](../sources/EsteriaWoW/tools/cars_mount_pack.py)

Extract the supplied car MPQs and build an additive WotLK car pack.

Parser declarations:

```python
parser.add_argument('--source', type=Path, default=SOURCE_DEFAULT)
parser.add_argument('--repo', type=Path, default=REPO_DEFAULT)
parser.add_argument('--stormlib', type=Path, default=DLL_DEFAULT)
parser.add_argument('--mount-root', type=Path, action='append', dest='mount_roots')
parser.add_argument('--archive', type=Path)
parser.add_argument('--report', type=Path, default=Path('var/mount-build/mounts_summary.json'))
```

Long declarations for this entry are preserved in the linked tool-index.json.

## EsteriaWoW/tools/character_ui_pack.py

[Source](../sources/EsteriaWoW/tools/character_ui_pack.py)

Stage and install focused creator/roster GlueXML changes with verified MPQ backups.

Parser declarations:

```python
parser.add_argument('action', choices=('prepare', 'install'))
```

## EsteriaWoW/tools/check_glue_race_tables.py

[Source](../sources/EsteriaWoW/tools/check_glue_race_tables.py)

Read-only check: the live GlueParent.lua defines each race table before using it.

## EsteriaWoW/tools/compare_wod_isolation_glue.py

[Source](../sources/EsteriaWoW/tools/compare_wod_isolation_glue.py)

Compare effective GlueXML payloads between the WoD donor and isolation client.

## EsteriaWoW/tools/create_wod_runtime_isolation.py

[Source](../sources/EsteriaWoW/tools/create_wod_runtime_isolation.py)

Create a side-by-side WoD runtime isolation client. The diagnostic client uses the known-working donor
Wow.exe/runtime DLLs and the current Esteria data/model/DBC payload, but deliberately replaces the isolation
copy's active GlueXML with the donor's known-working GlueXML. This avoids the stock/donor executable rejecting
Esteria's custom login UI while still testing the exact WoD race assets and DBCs currently installed in
Esteria. The live client is never modified. Most Data files are hard-linked read-only into the isolation tree;
Data/enUS/patch-enUS-Z.MPQ is a private copy because it receives the donor GlueXML overlay.

Parser declarations:

```python
parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
```

## EsteriaWoW/tools/creator_portrait_layout.py

[Source](../sources/EsteriaWoW/tools/creator_portrait_layout.py)

Install six supplied Mag'har/Skyborne portraits and a compact faction race grid.

Parser declarations:

```python
parser.add_argument('command', choices=('build', 'refresh-ui', 'install'))
parser.add_argument('--client', type=Path, default=pack.CLIENT_DEFAULT)
```

## EsteriaWoW/tools/creature_animation_repair.py

[Source](../sources/EsteriaWoW/tools/creature_animation_repair.py)

Adapt missing NPC player actions from CRC-matched bones in the installed player rigs.

Parser declarations:

```python
parser.add_argument('action', choices=('stage', 'install'))
```

## EsteriaWoW/tools/creature_portrait_pack.py

[Source](../sources/EsteriaWoW/tools/creature_portrait_pack.py)

Install the seven supplied NPC-race portraits and hide redundant single-gender creator buttons.

Parser declarations:

```python
parser.add_argument('action', choices=('stage', 'install'))
```

## EsteriaWoW/tools/creature_race_pack.py

[Source](../sources/EsteriaWoW/tools/creature_race_pack.py)

Port the requested Retail NPC race assets without changing installed client/server files.

Parser declarations:

```python
parser.add_argument('--race', choices=tuple(SPECS), action='append')
```

Long declarations for this entry are preserved in the linked tool-index.json.

## EsteriaWoW/tools/customization_buttons.py

[Source](../sources/EsteriaWoW/tools/customization_buttons.py)

Repair creator dice buttons and keep one centered pair of smooth rotation controls.

Parser declarations:

```python
parser.add_argument('action', choices=('check', 'prepare', 'install'))
```

## EsteriaWoW/tools/customization_label_repair.py

[Source](../sources/EsteriaWoW/tools/customization_label_repair.py)

Restore stock picker labels after expanded races; replace only the winning creator Lua entries.

Parser declarations:

```python
parser.add_argument('action', choices=('prepare', 'install'))
```

## EsteriaWoW/tools/customization_layout.py

[Source](../sources/EsteriaWoW/tools/customization_layout.py)

Split extended creator controls around the preview; preserve both client archive layers.

Parser declarations:

```python
parser.add_argument('action', choices=('check', 'prepare', 'install'))
```

## EsteriaWoW/tools/darkfallen_race_pack.py

[Source](../sources/EsteriaWoW/tools/darkfallen_race_pack.py)

Build an additive Darkfallen race pack from the active WotLK MPQs.

Parser declarations:

```python
parser.add_argument('--print-contract', action='store_true')
parser.add_argument('--root-archive', type=Path, default=ROOT / ARCHIVE_NAME)
parser.add_argument('--locale-archive', type=Path, default=ROOT / LOCALE_ARCHIVE_NAME)
parser.add_argument('--source', type=Path, default=ASSET_ROOT)
parser.add_argument('--output-root', type=Path)
parser.add_argument('--stormlib', type=Path, default=DLL_DEFAULT)
```

Long declarations for this entry are preserved in the linked tool-index.json.

## EsteriaWoW/tools/derive_playable_race_portraits.py

[Source](../sources/EsteriaWoW/tools/derive_playable_race_portraits.py)

Derive deterministic 64x64 BLP2 Glue portraits from race face textures.

Parser declarations:

```python
parser.add_argument('--output-dir', type=Path, required=True)
parser.add_argument('--header-template', type=Path, required=True)
parser.add_argument('--source-root', type=Path)
parser.add_argument(f'--{key.lower()}', type=Path)
```

## EsteriaWoW/tools/diagnose_ascension_hd_collisions.py

[Source](../sources/EsteriaWoW/tools/diagnose_ascension_hd_collisions.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/dreadlord_override_pack.py

[Source](../sources/EsteriaWoW/tools/dreadlord_override_pack.py)

Build/check the standalone NPC override from the audited, immutable dreadlord source cache.

Parser declarations:

```python
parser.add_argument('action', choices=('build', 'check'))
```

## EsteriaWoW/tools/earthen_race_pack.py

[Source](../sources/EsteriaWoW/tools/earthen_race_pack.py)

Reproduce Earthen 48/49 from the pinned Retail graph and current Esteria merge base.

Parser declarations:

```python
parser.add_argument('action', choices=('audit', 'acquire', 'portraits', 'prepare', 'stage', 'backup', 'install'))
```

## EsteriaWoW/tools/earthen_touchup.py

[Source](../sources/EsteriaWoW/tools/earthen_touchup.py)

Repair Earthen backgrounds, belt selection and native gameplay appearance without server/data migration.

Parser declarations:

```python
parser.add_argument('action', choices=('prepare', 'validate', 'install', 'refresh-native', 'feet'))
```

## EsteriaWoW/tools/expanded_appearance_pack.py

[Source](../sources/EsteriaWoW/tools/expanded_appearance_pack.py)

Data-driven native appearance codec and Skyborne expansion preparation.

Parser declarations:

```python
parser.add_argument('command', choices=('prepare', 'build', 'install'))
parser.add_argument('--client', type=Path, default=p.CLIENT_DEFAULT)
```

## EsteriaWoW/tools/export_blp_preview.py

[Source](../sources/EsteriaWoW/tools/export_blp_preview.py)

Export archive/source BLPs to PNG for visual comparison.

## EsteriaWoW/tools/finalize_ascension_hd_stock_ids.py

[Source](../sources/EsteriaWoW/tools/finalize_ascension_hd_stock_ids.py)

Library, test, or historical helper; inspect its source before use.

Parser declarations:

```python
parser.add_argument('--client-root', type=Path, default=DEFAULT_CLIENT)
parser.add_argument('--ascension-root', type=Path, default=DEFAULT_ASCENSION)
parser.add_argument('--stormlib', type=Path, default=DLL_DEFAULT)
parser.add_argument('--apply', action='store_true')
```

## EsteriaWoW/tools/find_mpq_paths.py

[Source](../sources/EsteriaWoW/tools/find_mpq_paths.py)

Library, test, or historical helper; inspect its source before use.

Parser declarations:

```python
parser.add_argument('root', type=Path)
parser.add_argument('terms', nargs='+')
parser.add_argument('--recursive', action='store_true')
```

## EsteriaWoW/tools/fix_ascension_hd_followups.py

[Source](../sources/EsteriaWoW/tools/fix_ascension_hd_followups.py)

Library, test, or historical helper; inspect its source before use.

Parser declarations:

```python
parser.add_argument('--client-root', type=Path, default=DEFAULT_CLIENT)
parser.add_argument('--ascension-root', type=Path, default=DEFAULT_ASCENSION)
parser.add_argument('--stormlib', type=Path, default=DLL_DEFAULT)
parser.add_argument('--apply', action='store_true')
```

## EsteriaWoW/tools/freeborn_faction_pack.py

[Source](../sources/EsteriaWoW/tools/freeborn_faction_pack.py)

Build the Freeborn player-hostility FactionTemplate rows and deploy them. Why this exists --------------- The
3.3.5a client decides player-versus-player friendliness entirely from the two units'
`UNIT_FIELD_FACTIONTEMPLATE` update fields: the value is used directly as a `FactionTemplate.dbc` row id
(`Wow.exe` `0x0071f770`, reached from the reaction core `0x007251c0` and from `CanAttack` `0x00729740`). The
deployed table is the Faction-Free package, where every player template is `friendlyMask 6 / hostileMask 8` -
friendly to both player groups - so a Freeborn character, which still wears its race's template, renders
Friendly to everyone. The rows this module writes: * a fifth faction group bit `V = 16`
(`FREEBORN_GROUP_MASK`) is added to the `ourMask` of every template a player can wear, so "is a player" is
addressable by a bit no NPC has; * a dedicated Freeborn template row (new id `FREEBORN_TEMPLATE_ID`) with
`ourMask 1|8`, `friendlyMask 6`, `hostileMask 8|16`, which is hostile to players both ways, hostile to
monsters both ways (so PvE is unchanged), friendly to both sides' NPCs, and hostile to other Freeborn.
Everything else in the table is copied byte-for-byte; the contract test proves that. Deployment ---------- *
server: `mod-wxl-dbc` registers `sFactionTemplateStore` (`WxlDbcRegistry.cpp:90`), so the continuation file
(`FactionTemplate.dbc1-freeborn`) dropped into `data/dbc-continuations/` is merged at startup - no worldserver
rebuild. * client: `wxl-extended-dbc`'s supported-table list does not name `FactionTemplate`, so the full
patched table is written into the project's own highest-priority archive (`patch-Z.MPQ`) with a
SHA-256-verified backup, the same workflow `tools/freeborn_team_pack.py` uses.

Parser declarations:

```python
parser.add_argument('--base', type=Path, help='base FactionTemplate.dbc (default: deployed copy)')
parser.add_argument('--dbc-out', type=Path, help='write the full patched table here')
parser.add_argument('--continuation-out', type=Path, help='write the changed-rows continuation here')
parser.add_argument('--client-root', type=Path, default=CLIENT_ROOT)
parser.add_argument('--install-client', action='store_true')
parser.add_argument('--restore-client', type=Path, help='restore this backed-up archive')
parser.add_argument('--stormlib', type=Path, default=DLL_DEFAULT)
parser.add_argument('--print-contract', action='store_true')
parser.add_argument('--print-rows', action='store_true')
```

## EsteriaWoW/tools/freeborn_team_pack.py

[Source](../sources/EsteriaWoW/tools/freeborn_team_pack.py)

Patch the winning GlueXML character-creation files with the Freeborn third-team pick. Adds a Freeborn
CheckButton between the gender buttons and the Lua that keeps its selection state and hands the worldserver a
Freeborn.create token on CMSG_CHAR_CREATE. The token is exactly one trailing space on the create name. The
glue client holds character-create state in C and Lua can only pass the name to CreateCharacter(), so the name
is the only field a GlueXML-only patch can reach. A space is never legal in a player name, so the token cannot
collide with a real name; the worldserver strips it before validating or storing the name. See
src/server/game/Handlers/CharacterHandler.cpp. Both patch-Z.MPQ and patch-enUS-Z.MPQ carry these files, and
the locale archive loads last, so both are patched. Nothing here touches Wow.exe, DBCs, art assets, or packet
layouts.

Parser declarations:

```python
parser.add_argument('--client-root', type=Path, default=CLIENT_ROOT)
parser.add_argument('--root-archive', type=Path)
parser.add_argument('--locale-archive', type=Path)
parser.add_argument('--output-root', type=Path)
parser.add_argument('--install', action='store_true')
parser.add_argument('--print-contract', action='store_true')
parser.add_argument('--stormlib', type=Path, default=DLL_DEFAULT)
```

## EsteriaWoW/tools/haranir_live_render.py

[Source](../sources/EsteriaWoW/tools/haranir_live_render.py)

Read-only creator diagnostics: loaded Haranir meshes, character layers and actual texture bindings.

## EsteriaWoW/tools/haranir_race_pack.py

[Source](../sources/EsteriaWoW/tools/haranir_race_pack.py)

Stage the complete Haranir player graph without changing the installed clients or server.

Long declarations for this entry are preserved in the linked tool-index.json.

## EsteriaWoW/tools/haranir_render_repair.py

[Source](../sources/EsteriaWoW/tools/haranir_render_repair.py)

Install checked Haranir rendering repairs with verified rollback copies and explicit live receipts.

Parser declarations:

```python
parser.add_argument('action', choices=('validate', 'install'))
```

## EsteriaWoW/tools/highmountain_animation_repair.py

[Source](../sources/EsteriaWoW/tools/highmountain_animation_repair.py)

Rebuild inherited skeletal tracks while preserving accepted Highmountain geometry and materials.

Parser declarations:

```python
parser.add_argument('command', choices=('prepare', 'install'))
```

## EsteriaWoW/tools/highmountain_appearance.py

[Source](../sources/EsteriaWoW/tools/highmountain_appearance.py)

Stable six-byte Highmountain codec shared by the native helper and server validator.

## EsteriaWoW/tools/highmountain_complete_tracks.py

[Source](../sources/EsteriaWoW/tools/highmountain_complete_tracks.py)

Restore PEDC gameplay events and embed all Highmountain animation keys into native MD20.

Parser declarations:

```python
parser.add_argument('command', choices=('prepare', 'install'))
```

## EsteriaWoW/tools/highmountain_creator_repair.py

[Source](../sources/EsteriaWoW/tools/highmountain_creator_repair.py)

Repair Race46 material access and repack its installed archive payloads for the classic reader.

Parser declarations:

```python
parser.add_argument('command', choices=('prepare', 'install', 'refresh-helper', 'refresh-executable'))
```

## EsteriaWoW/tools/highmountain_eye_repair.py

[Source](../sources/EsteriaWoW/tools/highmountain_eye_repair.py)

Bind Highmountain iris meshes through the proven Wrath opaque UV0 material path.

Parser declarations:

```python
parser.add_argument('command', choices=('prepare', 'install'))
```

## EsteriaWoW/tools/highmountain_faces.py

[Source](../sources/EsteriaWoW/tools/highmountain_faces.py)

Bake Retail BIDA/BOMT face overrides into selectable Wrath meshes without altering animation tracks.

## EsteriaWoW/tools/highmountain_head_repair.py

[Source](../sources/EsteriaWoW/tools/highmountain_head_repair.py)

Restore Highmountain's full base head and its baked face variants, preserving the installed codec.

Parser declarations:

```python
parser.add_argument('command', choices=('prepare', 'install'))
```

## EsteriaWoW/tools/highmountain_integration.py

[Source](../sources/EsteriaWoW/tools/highmountain_integration.py)

Generate Race46 rendering, DBC and matched archive stages from verified Highmountain inputs.

Parser declarations:

```python
parser.add_argument('command', choices=('prepare', 'build', 'refresh-glue', 'refresh-assets', 'validate', 'install'))
```

## EsteriaWoW/tools/highmountain_race_pack.py

[Source](../sources/EsteriaWoW/tools/highmountain_race_pack.py)

Audit and stage the complete Highmountain source; never install an incomplete port.

Parser declarations:

```python
parser.add_argument('command', choices=('audit', 'prepare', 'portraits', 'glue', 'hard-textures'))
```

## EsteriaWoW/tools/highmountain_teardown_repair.py

[Source](../sources/EsteriaWoW/tools/highmountain_teardown_repair.py)

Deploy the paired native teardown repair without changing accepted race assets.

Parser declarations:

```python
parser.add_argument('command', choices=('prepare', 'install'))
```

## EsteriaWoW/tools/inspect_client_archive.py

[Source](../sources/EsteriaWoW/tools/inspect_client_archive.py)

Read-only StormLib inspector for the active WotLK client archives.

Parser declarations:

```python
parser.add_argument('archive', type=Path)
parser.add_argument('--match', default='')
parser.add_argument('--extract', nargs='*', default=[])
parser.add_argument('--out', type=Path)
parser.add_argument('--stormlib', type=Path, default=DLL_DEFAULT)
```

## EsteriaWoW/tools/mechagnome_animations.py

[Source](../sources/EsteriaWoW/tools/mechagnome_animations.py)

Flatten Mechagnome's inherited Retail skeleton animations into its native M2.

## EsteriaWoW/tools/mechagnome_race_pack.py

[Source](../sources/EsteriaWoW/tools/mechagnome_race_pack.py)

Prepare and install Race47 using the existing native appearance and MPQ pipeline.

Parser declarations:

```python
parser.add_argument('command', choices=('prepare', 'build', 'validate', 'install', 'refresh'))
```

## EsteriaWoW/tools/mount_pack_batch2.py

[Source](../sources/EsteriaWoW/tools/mount_pack_batch2.py)

Build and deploy Esteria mount batch #2 as native 3.3.5a data. The 71 ready mounts live under
``NewModels/_Mounts``. Their assets are shipped in a new ``Patch-W.MPQ``. This pack deliberately does *not*
use WarcraftXL extended-DBC continuation files: it builds complete native WDBC tables instead. The developer
client already has higher-priority X/Y/Z archives carrying some of the same DBC paths. Therefore the native
tables are also mirrored into the existing root and locale Z archives at deploy time, after making byte-for-
byte backups. Patch-W remains the owner of the batch-2 model/icon assets.

Parser declarations:

```python
parser.add_argument('--client', type=Path, default=CLIENT_ROOT_DEFAULT)
parser.add_argument('--stormlib', type=Path, default=STORMLIB_DEFAULT)
parser.add_argument('--locale', default='enUS')
parser.add_argument('--stage', action='store_true', help='Build Patch-W, native DBCs, manifest, SQL, and additem list.')
```

Long declarations for this entry are preserved in the linked tool-index.json.

## EsteriaWoW/tools/native_appearance_patch.py

[Source](../sources/EsteriaWoW/tools/native_appearance_patch.py)

Fingerprint-checked permanent native appearance patch for Esteria build12340.

Parser declarations:

```python
parser.add_argument('--source', type=Path, default=CLIENT)
parser.add_argument('--output', type=Path, default=STAGE / 'Wow.exe')
```

## EsteriaWoW/tools/patch_dropdown_zoom.py

[Source](../sources/EsteriaWoW/tools/patch_dropdown_zoom.py)

Guard the installed v180 GlueZoom wheel callback; preserve its camera calibration and all other code.

## EsteriaWoW/tools/patch_kultiran_head_attachment.py

[Source](../sources/EsteriaWoW/tools/patch_kultiran_head_attachment.py)

Re-anchor Kul Tiran head components to the character model's head geometry.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
parser.add_argument('--target', type=Path, default=PATCH_Y)
parser.add_argument('--source', type=Path, default=PATCH_G)
```

## EsteriaWoW/tools/patch_kultiran_helmet_display.py

[Source](../sources/EsteriaWoW/tools/patch_kultiran_helmet_display.py)

Restore the original display-model stem for the Kul Tiran Geistlord helms.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
parser.add_argument('--target', type=Path, default=PATCH_Y)
```

## EsteriaWoW/tools/patch_kultiran_helmet_pack.py

[Source](../sources/EsteriaWoW/tools/patch_kultiran_helmet_pack.py)

Add Eunoia's Kul Tiran head components and fix the client race prefix.

Parser declarations:

```python
parser.add_argument('--target', type=Path, default=DEFAULT_TARGET)
parser.add_argument('--donor', type=Path, default=DEFAULT_DONOR)
parser.add_argument('--stormlib', type=Path, default=DEFAULT_STORMLIB)
parser.add_argument('--backup-dir', type=Path)
```

## EsteriaWoW/tools/playable_race_pack.py

[Source](../sources/EsteriaWoW/tools/playable_race_pack.py)

Build an additive WDBC/model pack for Vulpera and Alliance Pandaren.

Parser declarations:

```python
parser.add_argument('--no-assets', action='store_true')
```

Long declarations for this entry are preserved in the linked tool-index.json.

## EsteriaWoW/tools/race_portrait_pack.py

[Source](../sources/EsteriaWoW/tools/race_portrait_pack.py)

Convert the supplied race portrait PNGs into the BLP2 files this client loads. Sources:
<Pictures>\Portraits\Alliance\Charactercreate-races_<race>-<gender>[_alliance].png
<Pictures>\Portraits\Horde\Charactercreate-races_<race>-<gender>[_horde].png Destinations, per race and
gender: Interface\CharacterFrame\TemporaryPortrait-<Male|Female>-<ClientFileString>.blp The character-select
and paper-doll portrait. The client builds this name from ChrRaces field 11 plus "Male"/"Female" (Wow.exe
0x006181C0), and a missing file is what draws the placeholder portrait on the character-select screen. the
Interface\Glues\CharacterCreate\UI-CharacterCreate-... path the client's own RACE_ICON_TEXTURES table already
points at (creation-screen race buttons). Images are written as 64x64 BLP2 raw BGRA with 7 mips, byte-
identical in format to the client's existing race icons, with a circular alpha mask so the square source art
sits correctly in the round portrait frames.

Parser declarations:

```python
parser.add_argument('--source', type=Path, default=DEFAULT_SOURCE)
parser.add_argument('--root-archive', type=Path, default=Path('G:\\3.3.5a - Dev\\Data\\patch-Z.MPQ'))
parser.add_argument('--locale-archive', type=Path, default=Path('G:\\3.3.5a - Dev\\Data\\enUS\\patch-enUS-Z.MPQ'))
parser.add_argument('--backup-dir', type=Path)
parser.add_argument('--apply', action='store_true')
```

Long declarations for this entry are preserved in the linked tool-index.json.

## EsteriaWoW/tools/race_touchup_pack.py

[Source](../sources/EsteriaWoW/tools/race_touchup_pack.py)

Repair retroported race animation, language eligibility and Character Select presentation.

Parser declarations:

```python
parser.add_argument('command', choices=('build', 'install'))
parser.add_argument('--client', type=Path, default=p.CLIENT_DEFAULT)
```

## EsteriaWoW/tools/repair_ascension_hd_live.py

[Source](../sources/EsteriaWoW/tools/repair_ascension_hd_live.py)

Library, test, or historical helper; inspect its source before use.

Parser declarations:

```python
parser.add_argument('--client-root', type=Path, default=DEFAULT_CLIENT)
parser.add_argument('--ascension-root', type=Path, default=DEFAULT_ASCENSION)
parser.add_argument('--apply', action='store_true')
```

## EsteriaWoW/tools/repair_hd_npcs_highelf_darkfallen.py

[Source](../sources/EsteriaWoW/tools/repair_hd_npcs_highelf_darkfallen.py)

Library, test, or historical helper; inspect its source before use.

Parser declarations:

```python
parser.add_argument('--client-root', type=Path, default=DEFAULT_CLIENT)
parser.add_argument('--f-donor', type=Path, default=DEFAULT_F_DONOR)
parser.add_argument('--ascension-root', type=Path, default=DEFAULT_ASCENSION)
parser.add_argument('--darkfallen-root', type=Path, default=DEFAULT_DARKFALLEN)
parser.add_argument('--stormlib', type=Path, default=DLL_DEFAULT)
parser.add_argument('--stage-only', action='store_true')
parser.add_argument('--apply-staged', type=Path)
```

## EsteriaWoW/tools/replace_wod_with_ascension_hd.py

[Source](../sources/EsteriaWoW/tools/replace_wod_with_ascension_hd.py)

Replace Esteria's failed F: WoD stock-race splice with Ascension's HD races. The migration is intentionally
surgical and reversible: * backs up the live Z/enUS-Z archives, Wow.exe, and temporary donor patch-T; *
removes the F: donor's stock character payload from patch-Z, restoring any entries that already existed in the
pre-WoD backup; * imports only Ascension's isolated Race2 asset families (Human2..Draenei2); * replaces only
stock-race appearance rows with Ascension's HD race contract; * restores the stock display/model/extra rows
changed by the F: migration; * appends Ascension's dedicated HD display/model/extra rows; * changes only the
stock ChrRaces male/female display IDs; * preserves custom races and unrelated DBC rows; * reverts the one
F-donor-only Wow.exe byte patch if it is still present; * removes patch-T only when it is byte-identical to
the staged donor W archive; * produces server DBC continuation files matching the new player display IDs. No
server binary, SQL, custom-race asset, or unrelated DBC row is modified.

Parser declarations:

```python
parser.add_argument('--client-root', type=Path, default=DEFAULT_CLIENT)
parser.add_argument('--ascension-root', type=Path, default=DEFAULT_ASCENSION)
parser.add_argument('--wod-donor-root', type=Path, default=DEFAULT_WOD_DONOR)
parser.add_argument('--pre-wod-backup', type=Path, default=DEFAULT_PRE_WOD_BACKUP)
parser.add_argument('--stormlib', type=Path, default=DLL_DEFAULT)
parser.add_argument('--apply', action='store_true')
```

## EsteriaWoW/tools/restore_esteria_custom_after_reforged.py

[Source](../sources/EsteriaWoW/tools/restore_esteria_custom_after_reforged.py)

Library, test, or historical helper; inspect its source before use.

Parser declarations:

```python
parser.add_argument('--stormlib', type=Path, default=DLL_DEFAULT)
parser.add_argument('--stage-only', action='store_true')
parser.add_argument('--apply-staged', type=Path)
```

## EsteriaWoW/tools/retroported_race_pack.py

[Source](../sources/EsteriaWoW/tools/retroported_race_pack.py)

Build, validate, and install Esteria retroported-race client/server packs. Phase 1 intentionally starts with
Mag'har Orc but keeps the build machinery manifest-driven. The live Esteria Z archives are always treated as
the merge base. Install is transactional: back up and hash-verify both live Z archives, validate staged
output, then replace them.

Parser declarations:

```python
parser.add_argument('--race', required=True)
parser.add_argument('--client', type=Path, default=CLIENT_DEFAULT)
parser.add_argument('--runtime-dll', type=Path, default=RUNTIME_BUILD_DEFAULT)
```

Long declarations for this entry are preserved in the linked tool-index.json.

## EsteriaWoW/tools/sanitize_wod_isolation_glue.py

[Source](../sources/EsteriaWoW/tools/sanitize_wod_isolation_glue.py)

Remove donor-nonexistent GlueXML entries from the private WoD isolation client. The live Esteria client is
never modified. If an offending isolation archive is hard-linked to the live client, this script first
replaces the isolation link with a private byte-for-byte copy before removing entries with StormLib.

## EsteriaWoW/tools/scan_wxl_character_hooks.py

[Source](../sources/EsteriaWoW/tools/scan_wxl_character_hooks.py)

Scan deployed WarcraftXL extension DLLs for character/customization hook strings.

## EsteriaWoW/tools/set_wxl_modern_m2_combiner.py

[Source](../sources/EsteriaWoW/tools/set_wxl_modern_m2_combiner.py)

Toggle WarcraftXL modern-M2 combiner for the Esteria client. The WoD player models are already native WotLK M2
v264 assets. WarcraftXL's modern-M2 extension installs an additional batch/texture combiner by default, which
is unnecessary for those models and can alter their layered character texture path. This helper writes the
extension's supported config key while keeping every other WarcraftXL feature enabled.

Parser declarations:

```python
parser.add_argument('--client-root', type=Path, default=DEFAULT_CLIENT)
parser.add_argument('--enable', action='store_true')
parser.add_argument('--apply', action='store_true')
```

## EsteriaWoW/tools/show_glue_calls.py

[Source](../sources/EsteriaWoW/tools/show_glue_calls.py)

Print the SetBackgroundModel call sites in the live Glue Lua files.

## EsteriaWoW/tools/skyborne_race_pack.py

[Source](../sources/EsteriaWoW/tools/skyborne_race_pack.py)

Skyborne's curated race data, using the shared retroported-race installer.

## EsteriaWoW/tools/skyborne_visual_pack.py

[Source](../sources/EsteriaWoW/tools/skyborne_visual_pack.py)

Prepare dependency-closed Skyborne art and curated Wrath player models.

Parser declarations:

```python
parser.add_argument('command', choices=('prepare',))
```

## EsteriaWoW/tools/socket_stress_heavy.py

[Source](../sources/EsteriaWoW/tools/socket_stress_heavy.py)

Socket Stress Test for AzerothCore Tests authserver and worldserver connection handling under heavy load.
Usage: python3 socket_stress_heavy.py [duration_seconds] [auth_threads] [world_threads] Defaults: duration:
300 seconds (5 minutes) auth_threads: 100 world_threads: 150

## EsteriaWoW/tools/stage_wod_w_dependency_patch.py

[Source](../sources/EsteriaWoW/tools/stage_wod_w_dependency_patch.py)

Stage or remove the donor WoD patch-w archive as a lower-priority dependency patch. This preserves the donor
MPQ's internal filename hashes, including anonymous entries that cannot be recovered from its listfile. The
live Esteria patch-Z remains higher priority and therefore continues to win for the 12,701 X assets already
verified byte-for-byte.

Parser declarations:

```python
parser.add_argument('action', choices=('apply', 'remove', 'status'))
```

## EsteriaWoW/tools/test_ascension_hd_migration.py

[Source](../sources/EsteriaWoW/tools/test_ascension_hd_migration.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/test_broken_client_contract.py

[Source](../sources/EsteriaWoW/tools/test_broken_client_contract.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/test_cars_mount_pack.py

[Source](../sources/EsteriaWoW/tools/test_cars_mount_pack.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/test_character_limit_contract.py

[Source](../sources/EsteriaWoW/tools/test_character_limit_contract.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/test_character_select_contract.py

[Source](../sources/EsteriaWoW/tools/test_character_select_contract.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/test_character_ui.py

[Source](../sources/EsteriaWoW/tools/test_character_ui.py)

Run the actual patched Lua against small Glue/native fixtures, without launching WoW.

## EsteriaWoW/tools/test_classless_compat.py

[Source](../sources/EsteriaWoW/tools/test_classless_compat.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/test_classless_mount_contract.py

[Source](../sources/EsteriaWoW/tools/test_classless_mount_contract.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/test_creature_animations.py

[Source](../sources/EsteriaWoW/tools/test_creature_animations.py)

Check the reported actions against source ANIM keys and the prepared native models.

## EsteriaWoW/tools/test_creature_race_pack.py

[Source](../sources/EsteriaWoW/tools/test_creature_race_pack.py)

Run with python tools/test_creature_race_pack.py after preparing and staging the NPC race pack.

## EsteriaWoW/tools/test_darkfallen_contract.py

[Source](../sources/EsteriaWoW/tools/test_darkfallen_contract.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/test_earthen_race_pack.py

[Source](../sources/EsteriaWoW/tools/test_earthen_race_pack.py)

Run after earthen_race_pack.py prepare/stage; checks source selections and archive preservation.

## EsteriaWoW/tools/test_forgotten_race_name.py

[Source](../sources/EsteriaWoW/tools/test_forgotten_race_name.py)

Check the installed Forgotten names: python tools/test_forgotten_race_name.py.

Parser declarations:

```python
parser.add_argument('--client', type=Path, default=c.p.CLIENT_DEFAULT)
parser.add_argument('--server', type=Path, default=c.p.SERVER_DBC_ROOT / 'ChrRaces.dbc')
```

## EsteriaWoW/tools/test_freeborn_faction_pack.py

[Source](../sources/EsteriaWoW/tools/test_freeborn_faction_pack.py)

Contract test for the Freeborn player-hostility FactionTemplate rows. Run: python
tools/test_freeborn_faction_pack.py

## EsteriaWoW/tools/test_freeborn_team_pack.py

[Source](../sources/EsteriaWoW/tools/test_freeborn_team_pack.py)

Contract test for the Freeborn client patch and its claim path. Run: python tools/test_freeborn_team_pack.py
Hermetic checks cover the GlueXML payload, the addon, the transforms, and the server sources; the live checks
read the deployed archives. Cross-boundary checks matter here more than usual: the create screen, the addon
and the server have to agree on the CVar name and the addon-message envelope, and a drift between them fails
silently. Note on the earlier design: an interior-space token in the create name was tried and abandoned. The
client refuses a space in a character name ("Names can only contain letters"), and a Freeborn name has to
follow exactly the same rules as an Alliance or Horde one, so nothing about the name carries the flag.

## EsteriaWoW/tools/test_haranir_race_pack.py

[Source](../sources/EsteriaWoW/tools/test_haranir_race_pack.py)

Verify every Haranir control, transport byte, source material and staged archive before installation.

## EsteriaWoW/tools/test_highmountain_animation_repair.py

[Source](../sources/EsteriaWoW/tools/test_highmountain_animation_repair.py)

Check complete opaque sequences, inherited hand transforms and accepted geometry/material preservation.

## EsteriaWoW/tools/test_highmountain_complete_tracks.py

[Source](../sources/EsteriaWoW/tools/test_highmountain_complete_tracks.py)

Check inline animation ranges, source events, opacity, hands and preserved art.

## EsteriaWoW/tools/test_highmountain_creator_repair.py

[Source](../sources/EsteriaWoW/tools/test_highmountain_creator_repair.py)

Check the repaired archive boundaries, compositor format and native getter regression.

## EsteriaWoW/tools/test_highmountain_eye_repair.py

[Source](../sources/EsteriaWoW/tools/test_highmountain_eye_repair.py)

Check the iris binding, authored UVs and preservation of the accepted face geometry.

## EsteriaWoW/tools/test_highmountain_face_pivots.py

[Source](../sources/EsteriaWoW/tools/test_highmountain_face_pivots.py)

Verify facial bone pivots and that the staged repair changes only vertex positions/normals.

## EsteriaWoW/tools/test_highmountain_head_repair.py

[Source](../sources/EsteriaWoW/tools/test_highmountain_head_repair.py)

Verify every baked head variant is unconditional and only the intended SKIN IDs changed.

## EsteriaWoW/tools/test_highmountain_race_pack.py

[Source](../sources/EsteriaWoW/tools/test_highmountain_race_pack.py)

Run after highmountain_race_pack.py prepare; exercises source and staged asset contracts.

## EsteriaWoW/tools/test_highmountain_teardown_repair.py

[Source](../sources/EsteriaWoW/tools/test_highmountain_teardown_repair.py)

Check the new update/free thunks, retained getter ABI and native lifetime behavior.

## EsteriaWoW/tools/test_login_persistence_contract.py

[Source](../sources/EsteriaWoW/tools/test_login_persistence_contract.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/test_mechagnome_race_pack.py

[Source](../sources/EsteriaWoW/tools/test_mechagnome_race_pack.py)

Native Race47 appearance byte, geometry, and staged integration checks.

## EsteriaWoW/tools/test_mount_pack_batch2.py

[Source](../sources/EsteriaWoW/tools/test_mount_pack_batch2.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/test_native_appearance.py

[Source](../sources/EsteriaWoW/tools/test_native_appearance.py)

Checks the independent native patch, byte codec, and expanded model data.

## EsteriaWoW/tools/test_patch_kultiran_head_attachment.py

[Source](../sources/EsteriaWoW/tools/test_patch_kultiran_head_attachment.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/test_patch_kultiran_helmet_display.py

[Source](../sources/EsteriaWoW/tools/test_patch_kultiran_helmet_display.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/test_playable_race_contract.py

[Source](../sources/EsteriaWoW/tools/test_playable_race_contract.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/test_playable_race_pack.py

[Source](../sources/EsteriaWoW/tools/test_playable_race_pack.py)

Contract tests for the additive Vulpera/Pandaren client pack.

## EsteriaWoW/tools/test_race_portrait_pack.py

[Source](../sources/EsteriaWoW/tools/test_race_portrait_pack.py)

Focused checks for the race portrait converter.

## EsteriaWoW/tools/test_race_scope_corrective_sql.py

[Source](../sources/EsteriaWoW/tools/test_race_scope_corrective_sql.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/test_race_touchup_pack.py

[Source](../sources/EsteriaWoW/tools/test_race_touchup_pack.py)

Regression checks for the observed talking-animation crash and selection metadata.

## EsteriaWoW/tools/test_retroported_race_contract.py

[Source](../sources/EsteriaWoW/tools/test_retroported_race_contract.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/test_retroported_race_pack.py

[Source](../sources/EsteriaWoW/tools/test_retroported_race_pack.py)

Library, test, or historical helper; inspect its source before use.

## EsteriaWoW/tools/test_skyborne_race_pack.py

[Source](../sources/EsteriaWoW/tools/test_skyborne_race_pack.py)

Focused acceptance checks for Skyborne's staged client/server data.

## EsteriaWoW/tools/test_skyborne_visual_pack.py

[Source](../sources/EsteriaWoW/tools/test_skyborne_visual_pack.py)

Runnable checks for the staged Skyborne runtime, without changing the client.

## EsteriaWoW/tools/test_two_names_contract.py

[Source](../sources/EsteriaWoW/tools/test_two_names_contract.py)

Contract checks for Esteria's first + last name character creation integration.

## EsteriaWoW/tools/test_vulpera_creator.py

[Source](../sources/EsteriaWoW/tools/test_vulpera_creator.py)

Exercise exact race identity and all Vulpera creator controls using WoW's Lua 5.1 runtime.

## EsteriaWoW/tools/test_vulpera_models.py

[Source](../sources/EsteriaWoW/tools/test_vulpera_models.py)

Regress the source head selection and the UV/material path used by the tail.

## EsteriaWoW/tools/test_vulpera_race_pack.py

[Source](../sources/EsteriaWoW/tools/test_vulpera_race_pack.py)

Check source controls, atlas projection, animation closure and the exact staged Vulpera merge.

## EsteriaWoW/tools/thinhuman_equipment_repair.py

[Source](../sources/EsteriaWoW/tools/thinhuman_equipment_repair.py)

Fit ThinHuman equipment to the pinned Retail reference and install a backed-up client-only repair.

Parser declarations:

```python
parser.add_argument('command', choices=('prepare', 'check', 'install', 'materials'))
```

## EsteriaWoW/tools/tuskarr_equipment_repair.py

[Source](../sources/EsteriaWoW/tools/tuskarr_equipment_repair.py)

Round the installed Tuskarr feet and retain its calves when Wrath selects a robe.

Parser declarations:

```python
parser.add_argument('command', choices=('prepare', 'check', 'install'))
```

## EsteriaWoW/tools/two_names_client_pack.py

[Source](../sources/EsteriaWoW/tools/two_names_client_pack.py)

Install Esteria's first + last name character-create UI into the winning GlueXML archives. The live Esteria
interface is assembled into patch-Z.MPQ and patch-enUS-Z.MPQ. This tool patches those winning files surgically
so it does not replace unrelated race, Freeborn, or retail-style UI work. It creates timestamped backups and
verifies every staged archive before replacing it.

Parser declarations:

```python
parser.add_argument('--client-root', type=Path, default=CLIENT_ROOT)
parser.add_argument('--stormlib', type=Path, default=DLL_DEFAULT)
parser.add_argument('--install', action='store_true')
```

## EsteriaWoW/tools/vulpera_equipment.py

[Source](../sources/EsteriaWoW/tools/vulpera_equipment.py)

Convert same-build Retail Vulpera helmet variants used by the installed Wrath items.

## EsteriaWoW/tools/vulpera_migration.py

[Source](../sources/EsteriaWoW/tools/vulpera_migration.py)

Guard the two existing Vulpera appearances while rebasing their authored Retail features.

## EsteriaWoW/tools/vulpera_models.py

[Source](../sources/EsteriaWoW/tools/vulpera_models.py)

Prepare the authored Vulpera mesh, animation graph and source texture layers for Wrath.

## EsteriaWoW/tools/vulpera_race_pack.py

[Source](../sources/EsteriaWoW/tools/vulpera_race_pack.py)

Rebase Esteria race 20 on a pinned Retail Vulpera source; preserve its gameplay identity.

Parser declarations:

```python
parser.add_argument('action', choices=('audit', 'header', 'prepare', 'stage', 'validate', 'backup', 'install'))
```

## EsteriaWoW/tools/vulpera_render_repair.py

[Source](../sources/EsteriaWoW/tools/vulpera_render_repair.py)

Install the corrected Vulpera creator/material graph with a guarded v1-to-v2 appearance migration.

Parser declarations:

```python
parser.add_argument('action', choices=('prepare', 'install'))
```

## EsteriaWoW/tools/wod_character_appearance_repair.py

[Source](../sources/EsteriaWoW/tools/wod_character_appearance_repair.py)

Audit/remap saved stock-race character appearance bytes for the WoD donor contract. Only stock races are
considered. Values already supported by the donor remain unchanged. Unsupported values are mapped to the
numerically nearest valid donor choice for that race/sex. Apply mode snapshots every changed row and writes a
restore SQL file before updating the live characters database.

Parser declarations:

```python
parser.add_argument('--donor-root', type=Path, default=Path('F:\\Wrath of the Lich King 3.3.5a (wod models)'))
parser.add_argument('--client-root', type=Path, default=Path('G:\\3.3.5a - Dev'))
parser.add_argument('--stormlib', type=Path, default=DLL_DEFAULT)
parser.add_argument('--apply', action='store_true')
```

## EsteriaWoW/tools/wod_model_appearance_repair.py

[Source](../sources/EsteriaWoW/tools/wod_model_appearance_repair.py)

Repair Esteria's WoD stock-race appearance contract after the initial model splice. This is deliberately
narrower than the original migration: - backs up the currently migrated patch-Z/enUS-Z; - imports donor
CharSections-referenced textures that live only in patch-w.mpq; - replaces stock-race rows in CharHairGeosets,
CharacterFacialHairStyles, and BarberShopStyle with the donor client's active rows; - preserves all non-
stock/custom race rows; - rebuilds staged MPQs to discard stale replacement blocks; - validates donor equality
for the stock appearance contract before install. It does not touch Wow.exe, SQL, server code, or custom-race
appearance rows.

Parser declarations:

```python
parser.add_argument('--client-root', type=Path, default=Path('G:\\3.3.5a - Dev'))
parser.add_argument('--donor-root', type=Path, default=Path('F:\\Wrath of the Lich King 3.3.5a (wod models)'))
parser.add_argument('--stormlib', type=Path, default=DLL_DEFAULT)
parser.add_argument('--apply', action='store_true')
```

## EsteriaWoW/tools/wod_model_migration.py

[Source](../sources/EsteriaWoW/tools/wod_model_migration.py)

Safely splice the F: WoD stock-race model pack into Esteria's active Z patches. The migration is intentionally
narrow: - backs up Data/patch-Z.MPQ and Data/enUS/patch-enUS-Z.MPQ first; - copies all Character/ and
Textures/ assets from the donor patch-x.mpq; - replaces only stock-race CharSections rows; - replaces only
CreatureDisplayInfo rows that use the donor stock-race player/NPC models; - replaces the corresponding
CreatureModelData and CreatureDisplayInfoExtra rows; - preserves all unrelated/custom Esteria DBC rows; -
stages and validates both MPQs before atomically replacing the live files. This script does not touch Wow.exe,
server code, SQL, or Patch-Zz.mpq.

Parser declarations:

```python
parser.add_argument('--client-root', type=Path, default=Path('G:\\3.3.5a - Dev'))
parser.add_argument('--donor-root', type=Path, default=Path('F:\\Wrath of the Lich King 3.3.5a (wod models)'))
parser.add_argument('--stormlib', type=Path, default=DLL_DEFAULT)
```

Long declarations for this entry are preserved in the linked tool-index.json.

## EsteriaWoW/tools/wow_xref.py

[Source](../sources/EsteriaWoW/tools/wow_xref.py)

Read-only xref/disassembly helper for Wow.exe (capstone based).

## RetroPorter/src/retroporter/__init__.py

[Source](../sources/RetroPorter/src/retroporter/__init__.py)

Esteria Retail -> 3.3.5a retroport helpers.

## RetroPorter/src/retroporter/__main__.py

[Source](../sources/RetroPorter/src/retroporter/__main__.py)

Library, test, or historical helper; inspect its source before use.

## RetroPorter/src/retroporter/assets.py

[Source](../sources/RetroPorter/src/retroporter/assets.py)

Library, test, or historical helper; inspect its source before use.

## RetroPorter/src/retroporter/cli.py

[Source](../sources/RetroPorter/src/retroporter/cli.py)

Library, test, or historical helper; inspect its source before use.

Parser declarations:

```python
sub.add_parser('doctor')
sub.add_parser('extract-db2')
extract.add_argument('--race', choices=sorted(RACES), default='maghar')
extract.add_argument('--source-root')
extract.add_argument('--source-product')
sub.add_parser('discover')
discover.add_argument('--race', choices=sorted(RACES), default='maghar')
sub.add_parser('plan-assets')
plan_assets.add_argument('--race', choices=sorted(RACES), default='maghar')
plan_assets.add_argument('--source-root')
plan_assets.add_argument('--source-product')
sub.add_parser('convert-assets')
convert.add_argument('--race', choices=sorted(RACES), default='maghar')
convert.add_argument('--dry-run', action='store_true')
convert.add_argument('--source-root')
convert.add_argument('--source-product')
sub.add_parser('prepare-player-runtime')
runtime.add_argument('--race', choices=sorted(RACES), default='maghar')
```

## RetroPorter/src/retroporter/config.py

[Source](../sources/RetroPorter/src/retroporter/config.py)

Library, test, or historical helper; inspect its source before use.

## RetroPorter/src/retroporter/discovery.py

[Source](../sources/RetroPorter/src/retroporter/discovery.py)

Library, test, or historical helper; inspect its source before use.

## RetroPorter/src/retroporter/player_runtime.py

[Source](../sources/RetroPorter/src/retroporter/player_runtime.py)

Library, test, or historical helper; inspect its source before use.

## RetroPorter/src/retroporter/races.py

[Source](../sources/RetroPorter/src/retroporter/races.py)

Library, test, or historical helper; inspect its source before use.

## RetroPorter/src/retroporter/wotlk.py

[Source](../sources/RetroPorter/src/retroporter/wotlk.py)

Library, test, or historical helper; inspect its source before use.

## RetroPorter/tests/test_discovery.py

[Source](../sources/RetroPorter/tests/test_discovery.py)

Library, test, or historical helper; inspect its source before use.

## RetroPorter/tests/test_player_runtime.py

[Source](../sources/RetroPorter/tests/test_player_runtime.py)

Library, test, or historical helper; inspect its source before use.

## RetroPorter/tests/test_skyborne_prep.py

[Source](../sources/RetroPorter/tests/test_skyborne_prep.py)

Library, test, or historical helper; inspect its source before use.

## RetroPorter/tests/test_vulpera.py

[Source](../sources/RetroPorter/tests/test_vulpera.py)

Library, test, or historical helper; inspect its source before use.

## RetroPorterWork/vulpera/convert_recovered.py

[Source](../sources/RetroPorterWork/vulpera/convert_recovered.py)

Library, test, or historical helper; inspect its source before use.

## RetroPorterWork/vulpera/inventory_source.py

[Source](../sources/RetroPorterWork/vulpera/inventory_source.py)

Library, test, or historical helper; inspect its source before use.

## RetroPorterWork/vulpera/run_source.py

[Source](../sources/RetroPorterWork/vulpera/run_source.py)

Library, test, or historical helper; inspect its source before use.

## client-active/Extensions/races-64-esteria/verify_extension.py

[Source](../sources/client-active/Extensions/races-64-esteria/verify_extension.py)

Static contract checks for the Esteria 64-race runtime extension.

Parser declarations:

```python
parser.add_argument('--client', type=Path, required=True)
parser.add_argument('--dll', type=Path, required=True)
parser.add_argument('--manifest', type=Path, required=True)
parser.add_argument('--source', type=Path)
```

## historical-diagnostics/build-expanded-stage.py

[Source](../sources/historical-diagnostics/build-expanded-stage.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/earthen/check_sql.py

[Source](../sources/historical-diagnostics/earthen/check_sql.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/earthen/finalize_checks.py

[Source](../sources/historical-diagnostics/earthen/finalize_checks.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/earthen/live_appearance.py

[Source](../sources/historical-diagnostics/earthen/live_appearance.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/earthen/live_charselect.py

[Source](../sources/historical-diagnostics/earthen/live_charselect.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/earthen/live_hooks.py

[Source](../sources/historical-diagnostics/earthen/live_hooks.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/earthen/verify_install.py

[Source](../sources/historical-diagnostics/earthen/verify_install.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/highmountain/record_complete_tracks.py

[Source](../sources/historical-diagnostics/highmountain/record_complete_tracks.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/highmountain/record_teardown.py

[Source](../sources/historical-diagnostics/highmountain/record_teardown.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/highmountain/teardown_debug.py

[Source](../sources/historical-diagnostics/highmountain/teardown_debug.py)

Read live build12340 object notification lists and watch a selected list link.

## historical-diagnostics/highmountain/track_diagnostic.py

[Source](../sources/historical-diagnostics/highmountain/track_diagnostic.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/install-native-appearance.py

[Source](../sources/historical-diagnostics/install-native-appearance.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/maghar-face-investigation/analyze_uv.py

[Source](../sources/historical-diagnostics/maghar-face-investigation/analyze_uv.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/maghar-face-investigation/bake_probe.py

[Source](../sources/historical-diagnostics/maghar-face-investigation/bake_probe.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/maghar-face-investigation/read_archives.py

[Source](../sources/historical-diagnostics/maghar-face-investigation/read_archives.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/maghar-face-investigation/read_live.py

[Source](../sources/historical-diagnostics/maghar-face-investigation/read_live.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/native-appearance/probe_geometry.py

[Source](../sources/historical-diagnostics/native-appearance/probe_geometry.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/race-final-touchups/investigate.py

[Source](../sources/historical-diagnostics/race-final-touchups/investigate.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/skyborne-install.py

[Source](../sources/historical-diagnostics/skyborne-install.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/verify_helm_coverage.py

[Source](../sources/historical-diagnostics/verify_helm_coverage.py)

For the helm the user tested, confirm every custom race's resolved files exist.

## historical-diagnostics/vulpera/fix_eye_glow.py

[Source](../sources/historical-diagnostics/vulpera/fix_eye_glow.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/vulpera/helmet_alias_probe.py

[Source](../sources/historical-diagnostics/vulpera/helmet_alias_probe.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/vulpera/legacy_probe.py

[Source](../sources/historical-diagnostics/vulpera/legacy_probe.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/vulpera/repair_checkpoint.py

[Source](../sources/historical-diagnostics/vulpera/repair_checkpoint.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/vulpera/source_probe.py

[Source](../sources/historical-diagnostics/vulpera/source_probe.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/vulpera/update_install_plan.py

[Source](../sources/historical-diagnostics/vulpera/update_install_plan.py)

Library, test, or historical helper; inspect its source before use.

## historical-diagnostics/vulpera/verify_install.py

[Source](../sources/historical-diagnostics/vulpera/verify_install.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/ascension-customization/audit.py

[Source](../sources/historical-plans/ascension-customization/audit.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/ascension-customization/download.py

[Source](../sources/historical-plans/ascension-customization/download.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/ascension-customization/install.py

[Source](../sources/historical-plans/ascension-customization/install.py)

Snapshot, package, verify, and install the staged additive customization data.

Parser declarations:

```python
parser.add_argument('--install', action='store_true')
```

## historical-plans/ascension-customization/refresh.py

[Source](../sources/historical-plans/ascension-customization/refresh.py)

Update the already-verified package after tightening the donor palette filter.

## historical-plans/character-select-redesign/tests/run_tests.py

[Source](../sources/historical-plans/character-select-redesign/tests/run_tests.py)

Offline test runner for the Esteria Character Select Lua modules. Runs the REAL module sources on a genuine
Lua 5.1 runtime (lupa.lua51), which is the interpreter family the WoW 3.3.5a client uses. This lets the
critical visual-index / real-index invariant be proven WITHOUT launching the client. Usage: python
.agents/plans/character-select-redesign/tests/run_tests.py

## historical-plans/character-select-redesign/tools/check_artkeys.py

[Source](../sources/historical-plans/character-select-redesign/tools/check_artkeys.py)

Cross-check ECS art keys against the CREATE SCREEN's own portrait mapping. ECS resolves a portrait as `UI-
CharacterCreate-<artKey><Male|Female>`, so the art key has to match the file the rest of the client uses.
`CharacterCreate.lua` already maps every race token to its plate in `RACE_ICON_TEXTURES`, which makes it the
authoritative source - and it is not the same as the race token: ["ZANDALARITROLL_MALE"] = "...\UI-
CharacterCreate-ZandalariMale" which is exactly the mismatch this checks for. Usage: python
.agents/plans/character-select-redesign/tools/check_artkeys.py

## historical-plans/character-select-redesign/tools/check_framing.py

[Source](../sources/historical-plans/character-select-redesign/tools/check_framing.py)

Is the portrait circle FRAMED consistently across the client's race plates? Every row shows its portrait at
the same size, so if the plates disagree about how much of their 64x64 frame the circle occupies, the faces on
screen come out at different sizes from row to row. That is the one quality property a regenerated set can
guarantee and the shipped plates may not: masking from the 130x130 sources inscribes an identical circle in
every portrait. Usage: python .agents/plans/character-select-redesign/tools/check_framing.py

## historical-plans/character-select-redesign/tools/check_models.py

[Source](../sources/historical-plans/character-select-redesign/tools/check_models.py)

Check which race MODEL directories the client actually ships. ECS resolves a race by finding a token as a
SUBSTRING of the normalised background model path (`S.GetRaceByModel`), returns the FIRST token that matches,
and takes its `artKey`. So two things are worth checking against the real client, neither of which any offline
Lua test can see: * a model directory that carries art but that no token can reach (its rows fall back to
"Unknown Race" with no portrait); * a more specific variant that a broader token swallows first - e.g. if the
client ships `DarkfallenHorde` and `Darkfallen`, the single `DARKFALLEN` token claims both and the Horde
variant gets Alliance art. Usage: python .agents/plans/character-select-redesign/tools/check_models.py

## historical-plans/character-select-redesign/tools/compare_source_vs_plate.py

[Source](../sources/historical-plans/character-select-redesign/tools/compare_source_vs_plate.py)

Is the client plate a faithful rendition of the supplied source? If it is, the sources buy nothing at the 46px
the roster draws. Compares the client plate against a fresh mask+downscale of the supplied 130x130 source, and
also checks whether the supplied illidari (DemonHunter) art is intact - the client's own DemonHunter plates
measured 0.024 opaque, i.e. effectively blank. Usage: python .agents/plans/character-select-
redesign/tools/compare_source_vs_plate.py

## historical-plans/character-select-redesign/tools/deploy.py

[Source](../sources/historical-plans/character-select-redesign/tools/deploy.py)

Deploy the Esteria Character Select payload into the live client archives. Adds, into BOTH patch-Z.MPQ and
patch-enUS-Z.MPQ (the contract test reads both): Interface\GlueXML\ECS_*.lua the ECS modules
Interface\GlueXML\CharacterSelect.lua with the keydown + scroll fixes Interface\GlueXML\GlueXML.toc with the
ECS load order Interface\Glues\CharacterSelect\ECS-*.blp portraits and row art vanilla panel/Glue button
textures restored from locale-enUS.MPQ extended GlueFontStyles.xml plus the CharacterCreate tooltip font
merged in Backs up both archives first, then verifies: every new entry round-trips byte for byte, and sampled
pre-existing entries are untouched. The client MUST be closed - a running game holds these archives open.
Usage: python .agents/plans/character-select-redesign/tools/deploy.py --client-data "G:\BearCave\Data"

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true', help='list the payload without touching archives')
```

Long declarations for this entry are preserved in the linked tool-index.json.

## historical-plans/character-select-redesign/tools/inspect_sources.py

[Source](../sources/historical-plans/character-select-redesign/tools/inspect_sources.py)

Inspect the supplied source portrait PNGs. Answers the questions that decide how to use them: how big they are
(a source that is larger than the 64x64 client plates can be downscaled to a sharper roster portrait), whether
they are already circular, and which race/sex keys they cover versus the ones ECS references. Usage: python
.agents/plans/character-select-redesign/tools/inspect_sources.py

## historical-plans/character-select-redesign/tools/make_ecs_portraits.py

[Source](../sources/historical-plans/character-select-redesign/tools/make_ecs_portraits.py)

Generate the ECS portrait set from the supplied race art. Source art: `R:\Users\Zach\Pictures\Portraits` - 56
PNGs at 130x130, the UNMASKED originals the client's 64x64 circular plates were made from. Each has a solid
black background outside the face, so a circular mask supplies the shape. This replaces the earlier approach
of masking the client's own plates, which was pointless: those plates are already circular (measured corner
alpha 0 on all 62 of them), so masking them again only softened an edge that was already cut. Deriving from
the originals also means ECS owns its art and no longer needs the client archives open to regenerate it. Also
converts the supplied character-select art into BLP2 textures and regenerates the procedural note dot and
search icon, so this one tool owns the whole ECS texture set. Usage: python .agents/plans/character-select-
redesign/tools/make_ecs_portraits.py python .agents/plans/character-select-
redesign/tools/make_ecs_portraits.py --check

Parser declarations:

```python
parser.add_argument('--check', action='store_true', help='report coverage without writing any files')
```

## historical-plans/character-select-redesign/tools/measure_capacity.py

[Source](../sources/historical-plans/character-select-redesign/tools/measure_capacity.py)

Measure the persisted payload against the cvar storage budget. The custom order has to survive a logout for a
roster of up to 100 characters (server cap). The store is percent-encoded and sharded across probed string
cvars, so the question "does a full roster even fit?" is arithmetic, not opinion. This prints the real numbers
from the REAL modules on Lua 5.1 rather than an estimate: payload size, shards needed, and the shards
available in the best case (all six candidate cvars writable) versus the proven case (the first two, which the
existing Freeborn implementation demonstrates do persist). Usage: python .agents/plans/character-select-
redesign/tools/measure_capacity.py

## historical-plans/darkfallen-hd/generate_darkfallen_attempts.py

[Source](../sources/historical-plans/darkfallen-hd/generate_darkfallen_attempts.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/elvui-glue-reskin/apply_patch.py

[Source](../sources/historical-plans/elvui-glue-reskin/apply_patch.py)

Merge the ElvUI glue reskin into the live client patch archives. Targets patch-Z.MPQ (root) and patch-
enUS-Z.MPQ (locale) -- the highest-priority archives, which is the same convention the existing custom race
glue work uses. Verification built in: * records entry counts before/after * re-reads a sample of PRE-EXISTING
entries and confirms their bytes are unchanged * re-reads every newly written entry and confirms the bytes
round-trip

## historical-plans/elvui-glue-reskin/blp.py

[Source](../sources/historical-plans/elvui-glue-reskin/blp.py)

Minimal BLP2 codec for WotLK 3.3.5a client textures. Supports decode of paletted (1), DXT (2: DXT1/DXT3/DXT5)
and raw BGRA (3), and encode as raw BGRA BLP2 with mipmaps -- the variant this client already loads (see
tools/derive_playable_race_portraits.py). Header layout (BLP2): [0:4] magic 'BLP2' [4:8] uint32 type (0=JPEG,
1=uncompressed, 2=DXT) [8] uint8 compression (1=paletted, 2=DXT, 3=raw BGRA) [9] uint8 alphaDepth [10] uint8
alphaEncoding (DXT: 0=DXT1, 1=DXT3, 7=DXT5) [11] uint8 hasMips [12:16] uint32 width [16:20] uint32 height
[20:84] uint32 offsets[16] [84:148] uint32 lengths[16] [148:1172] palette (256 * BGRA)

## historical-plans/elvui-glue-reskin/build_worklist.py

[Source](../sources/historical-plans/elvui-glue-reskin/build_worklist.py)

Build the complete remaining-work list. 1. Resolve the winning archive for EVERY Interface\GlueXML\* file in
load order. 2. Extract each winner. 3. Scan all winning Lua/XML for referenced Interface\... textures. 4.
Report which referenced textures are still stock (not already reskinned).

## historical-plans/elvui-glue-reskin/extract_addon.py

[Source](../sources/historical-plans/elvui-glue-reskin/extract_addon.py)

Extract every Interface\AddOns\<prefix> file from an MPQ into a staging tree.

## historical-plans/elvui-glue-reskin/extract_glue.py

[Source](../sources/historical-plans/elvui-glue-reskin/extract_glue.py)

Extract GlueXML files from client MPQs into a staging tree (read-only on source).

## historical-plans/elvui-glue-reskin/extract_live.py

[Source](../sources/historical-plans/elvui-glue-reskin/extract_live.py)

Extract the live (patch-A) glue button art + definitions for analysis.

## historical-plans/elvui-glue-reskin/find_entries.py

[Source](../sources/historical-plans/elvui-glue-reskin/find_entries.py)

Case-insensitive substring search over MPQ entry names, tolerant of non-ASCII names.

## historical-plans/elvui-glue-reskin/make_fonts.py

[Source](../sources/historical-plans/elvui-glue-reskin/make_fonts.py)

Rewrite GlueFontStyles.xml into the ElvUI 6.09 text palette. The stock glue font styles are built around gold
(1.0, 0.78, 0.0) text with NORMAL_FONT_COLOR = (1.0, 0.82, 0). That gold is the "stock Warcraft" text colour
visible on the login, realm-list and dialog screens. This keeps every font NAME and every
inherits/justifyH/outline/spacing attribute intact (other glue files inherit them) and only swaps colours, so
nothing can break from a missing font definition.

## historical-plans/elvui-glue-reskin/make_textures.py

[Source](../sources/historical-plans/elvui-glue-reskin/make_textures.py)

Generate ElvUI-styled replacements for the LIVE glue textures. Sources are resolved in real client load order:
patch-A.MPQ first (the retail-interface art that actually renders), then locale-enUS.MPQ (Blizzard stock,
which still supplies Interface\Buttons\* chrome and the Disabled button that patch-A omits). Every replacement
preserves the source texture's ALPHA silhouette and its exact dimensions/mip count, so the GlueXML TexCoords
keep framing correctly and no frame definition needs touching. ElvUI 6.09 palette (Settings/Profile.lua
defaults): backdropcolor 0.10, 0.10, 0.10 #1A1A1A backdropfadecolor 0.06, 0.06, 0.06 #0F0F0F bordercolor 0.00,
0.00, 0.00 #000000 valuecolor 0.99, 0.48, 0.17 #FD7A2B

## historical-plans/elvui-glue-reskin/preview_resolved.py

[Source](../sources/historical-plans/elvui-glue-reskin/preview_resolved.py)

Resolve, extract and preview arbitrary textures from the client's load order.

## historical-plans/elvui-glue-reskin/resolve_glue.py

[Source](../sources/historical-plans/elvui-glue-reskin/resolve_glue.py)

Resolve which MPQ wins for each GlueXML path, using WoW 3.3.5a archive load order.

## historical-plans/elvui-glue-reskin/scan_all_mpqs.py

[Source](../sources/historical-plans/elvui-glue-reskin/scan_all_mpqs.py)

Scan every MPQ in a client Data tree for GlueXML / login-related entries.

## historical-plans/elvui-glue-reskin/verify_result.py

[Source](../sources/historical-plans/elvui-glue-reskin/verify_result.py)

Verify the deployed reskin end-to-end, driven by the staging tree. Checks: 1. every staged entry resolves from
a -Z archive (highest load order) 2. every staged BLP decodes and contains no stock crimson red (ElvUI accent
orange is allowed and reported separately) 3. GlueFontStyles.xml contains no gold colour definitions 4.
sampled pre-existing entries are byte-identical to the backups

## historical-plans/eunoia-race-port/analyse_eunoia_races.py

[Source](../sources/historical-plans/eunoia-race-port/analyse_eunoia_races.py)

Read-only inventory of the races shipped in G:\Eunoia\Client. For every ChrRaces row: resolve the model paths,
then check which of those models, skins and CharSections textures actually exist in their archives.

## historical-plans/forgotten-race-name/audit.py

[Source](../sources/historical-plans/forgotten-race-name/audit.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/forgotten-race-name/finish_stage.py

[Source](../sources/historical-plans/forgotten-race-name/finish_stage.py)

Finish the validated archive stage after correcting the server-only prefix test.

## historical-plans/forgotten-race-name/frame_sources.py

[Source](../sources/historical-plans/forgotten-race-name/frame_sources.py)

Record the winning native race-label consumers for the requested in-game UI.

## historical-plans/forgotten-race-name/rename.py

[Source](../sources/historical-plans/forgotten-race-name/rename.py)

Back up, stage, and install only the Forgotten presentation data.

Parser declarations:

```python
parser.add_argument('action', choices=('stage', 'install'))
```

## historical-plans/freeborn-client/check_blp.py

[Source](../sources/historical-plans/freeborn-client/check_blp.py)

Read-only sanity check for a hand-made BLP2 texture destined for the create screen. Uses the project's own
BLP2 reader (`tools/derive_playable_race_portraits.py`) rather than a re-derived layout, so the check agrees
with the code that already packs BLP2 files for this client. A mis-encoded texture shows up as an invisible or
black button, which is hard to tell apart from a broken XML patch, so the header, the mip chain and the
encoding are all checked before packing.

## historical-plans/freeborn-client/check_cvar_bindings.py

[Source](../sources/historical-plans/freeborn-client/check_cvar_bindings.py)

Check which glue-available bindings exist for a CVar / addon-message based Freeborn channel. If GlueXML can
call SetCVar, a Freeborn choice can be persisted client-side and applied by an in-world addon after login,
which needs no Wow.exe patch and no name token.

## historical-plans/freeborn-client/diff_prefix.py

[Source](../sources/historical-plans/freeborn-client/diff_prefix.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-client/dry_run.py

[Source](../sources/historical-plans/freeborn-client/dry_run.py)

Dry-run the Freeborn GlueXML transforms against the real client archives. Reads only the two GlueXML entries,
applies both transforms, proves the anchor matched and the XML stays well-formed, and writes the results for
diff inspection. Changes nothing.

## historical-plans/freeborn-client/dump_blob.py

[Source](../sources/historical-plans/freeborn-client/dump_blob.py)

Dump NUL-separated string blobs from Wow.exe (binding names, cvar names).

## historical-plans/freeborn-client/dump_glue_bindings.py

[Source](../sources/historical-plans/freeborn-client/dump_glue_bindings.py)

Dump the glue Lua binding names near the character-creation setters in Wow.exe. If the customized client
exposed a Lua-controllable outfit/team/create field, its binding name would sit in the same string table as
SetSelectedRace / SetSelectedSex. Absence here is evidence that no such binding exists.

## historical-plans/freeborn-client/dump_name_codes.py

[Source](../sources/historical-plans/freeborn-client/dump_name_codes.py)

Dump the glue name-validation message table. 0x006B0F40 maps a validation code to a message via the string-
pointer table at 0x00AD91F0 (valid for codes 1..103). 0x006B0F90 returns `validator(...) + 0x57`, so code 0x57
means the validator returned 0 (accepted) and codes 0x58.. are the distinct rejection reasons.

## historical-plans/freeborn-client/enumerate_glue_bindings.py

[Source](../sources/historical-plans/freeborn-client/enumerate_glue_bindings.py)

Enumerate the Lua functions registered in the client's GLUE (pre-world) state. `SetCharacterCreateFacing` is a
glue-only binding, so its name pointer lives inside the glue state's Lua function table. Finding that table
lets us enumerate every function the glue environment exposes -- decisive for "can the character-create screen
reach SetCVar?". Usage: python enumerate_glue_bindings.py "G:\3.3.5a - Dev\Wow.exe" [anchor_name]

## historical-plans/freeborn-client/find_blob_refs.py

[Source](../sources/historical-plans/freeborn-client/find_blob_refs.py)

Find every DWORD anywhere in Wow.exe that points into the character-creation name blob, and classify the
referencing section -- reveals how the client stores Lua binding names.

## historical-plans/freeborn-client/find_create_character.py

[Source](../sources/historical-plans/freeborn-client/find_create_character.py)

Locate Wow.exe's Script_CreateCharacter and check whether it validates the name. The glue binding tables are
arrays of {name, function} pairs, so the dword after the "CreateCharacter" string pointer is the handler. We
then look for a space/whitespace test in the handler, which would reject the trailing-space Freeborn token
before it is ever sent.

## historical-plans/freeborn-client/harness/check_emblems.py

[Source](../sources/historical-plans/freeborn-client/harness/check_emblems.py)

Confirm the two shipped emblems in the deployed archive are present and identical.

## historical-plans/freeborn-client/harness/extract_block.py

[Source](../sources/historical-plans/freeborn-client/harness/extract_block.py)

Extract the managed Freeborn block from the DEPLOYED archive, for offline Lua execution.

## historical-plans/freeborn-client/harness/measure_logos.py

[Source](../sources/historical-plans/freeborn-client/harness/measure_logos.py)

Measure the visible (non-transparent) content of the character-select logos. The Freeborn emblem is drawn into
the same 60x60 slot the Alliance/Horde logos use, so if its artwork fills the image while theirs has padding,
it looks bigger. This reports each one's content bounding box so the drawn size can match.

## historical-plans/freeborn-client/inspect_deployed_lua.py

[Source](../sources/historical-plans/freeborn-client/inspect_deployed_lua.py)

Locate every injected Freeborn revision in a deployed CharacterCreate.lua. The first shipped revision predated
the managed-block sentinels, so re-running the packer appended a second copy instead of replacing it. This
reports the boundaries precisely so the canonicaliser can be sure it removes all of them.

## historical-plans/freeborn-client/locate_binding_table.py

[Source](../sources/historical-plans/freeborn-client/locate_binding_table.py)

Locate every occurrence of a binding name and show which section it lives in.

## historical-plans/freeborn-client/map_channel_team.py

[Source](../sources/historical-plans/freeborn-client/map_channel_team.py)

Point the channel lookups at the character's PvP side. ChannelMgr::forTeam returns nullptr for anything that
is not Alliance or Horde, so without this a Freeborn simply has no custom channels at all. The mapping is the
identity for Alliance and Horde. Usage: python map_channel_team.py # dry run python map_channel_team.py
--apply

## historical-plans/freeborn-client/map_other_team.py

[Source](../sources/historical-plans/freeborn-client/map_other_team.py)

Map the remaining team uses that are an index, a switch, or a PvP decision. These are outside the battleground
directories but have the same two properties: a Freeborn could index a two-element store with TEAM_FREEBORN,
or a Freeborn is silently on no side at all. The mapping is the identity for Alliance and Horde, so nothing
changes for any other character. Usage: python map_other_team.py # dry run python map_other_team.py --apply

## historical-plans/freeborn-client/map_pvp_team.py

[Source](../sources/historical-plans/freeborn-client/map_pvp_team.py)

Map every player-team use in the two-sided PvP code through PvpSideOf(). The mapping is the identity for
Alliance and Horde, so the only characters whose behaviour can change are Freeborn -- which is the point: they
must never index a two-element store with TEAM_FREEBORN. Usage: python map_pvp_team.py # dry run, prints every
change python map_pvp_team.py --apply # rewrites the files

## historical-plans/freeborn-client/probe_exe_refs.py

[Source](../sources/historical-plans/freeborn-client/probe_exe_refs.py)

Probe how Wow.exe references Lua binding-name strings (validates the VA mapping).

## historical-plans/freeborn-client/probe_text_encryption.py

[Source](../sources/historical-plans/freeborn-client/probe_text_encryption.py)

Is the on-disk .text of Wow.exe plain x86, or encrypted by the loader? Counts DWORDs in .text that point into
.rdata (string/const data). A normal MSVC binary has thousands; an encrypted-on-disk .text has ~none.

## historical-plans/freeborn-client/resolve_name_check.py

[Source](../sources/historical-plans/freeborn-client/resolve_name_check.py)

Resolve the glue create routine's name validation. 0x004E0380 (CGCharacterCreation::CreateCharacter) calls
0x6b0f90(name) and only continues when the result is 0x57; anything else shows a dialog built from a code via
0x6b0f40. If that check rejects a space, the trailing-space token never reaches the wire.

## historical-plans/freeborn-client/resolve_textures.py

[Source](../sources/historical-plans/freeborn-client/resolve_textures.py)

Resolve candidate GlueXML textures across the client's real archive chain. A missing texture means an
invisible Freeborn button, so the plate/border textures the new button references must be proven to resolve
somewhere in the client's load chain.

## historical-plans/freeborn-client/scan_client_bindings.py

[Source](../sources/historical-plans/freeborn-client/scan_client_bindings.py)

Read-only scan of the dev client binaries for glue/Lua binding names and packet fields. Extracts printable
ASCII runs and reports the ones matching character-creation, team/faction, or outfit keywords. Used to
determine whether a Freeborn selection can reach CMSG_CHAR_CREATE without patching Wow.exe.

## historical-plans/freeborn-client/show_final.py

[Source](../sources/historical-plans/freeborn-client/show_final.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-client/validate_ref_scan.py

[Source](../sources/historical-plans/freeborn-client/validate_ref_scan.py)

Sanity-check: resolve what the DWORDs found in .text actually point at.

## historical-plans/freeborn-client/verify_independent.py

[Source](../sources/historical-plans/freeborn-client/verify_independent.py)

Independent verification of the deployed Freeborn client patch. Deliberately does not import the packer or the
contract test: it re-derives everything from the deployed archives and the pristine backup, so a bug in my own
checking code cannot hide a problem. The strongest check here is that removing the injected button from the
deployed XML reproduces the pristine stock file byte for byte, and that the deployed Lua's stock prefix
matches the pristine Lua byte for byte -- i.e. the only change is the addition.

## historical-plans/freeborn-client/which_archives.py

[Source](../sources/historical-plans/freeborn-client/which_archives.py)

Report which client archives contain the winning GlueXML character-creation files. Determines the exact set of
archives a Freeborn GlueXML patch must touch, and whether any higher-priority archive overrides patch-Z.mpq.

## historical-plans/freeborn-client/xml_order.py

[Source](../sources/historical-plans/freeborn-client/xml_order.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/compare_client_dbc.py

[Source](../sources/historical-plans/freeborn-hostility/compare_client_dbc.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/dump_chrraces.py

[Source](../sources/historical-plans/freeborn-hostility/dump_chrraces.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/dump_chrraces2.py

[Source](../sources/historical-plans/freeborn-hostility/dump_chrraces2.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/dump_faction_ids.py

[Source](../sources/historical-plans/freeborn-hostility/dump_faction_ids.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/dump_factiontemplate.py

[Source](../sources/historical-plans/freeborn-hostility/dump_factiontemplate.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/find_free_rows.py

[Source](../sources/historical-plans/freeborn-hostility/find_free_rows.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/find_reusable_row.py

[Source](../sources/historical-plans/freeborn-hostility/find_reusable_row.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/find_spare_rows.py

[Source](../sources/historical-plans/freeborn-hostility/find_spare_rows.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/pick_ids.py

[Source](../sources/historical-plans/freeborn-hostility/pick_ids.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/probe_extdbc.py

[Source](../sources/historical-plans/freeborn-hostility/probe_extdbc.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/probe_extdbc2.py

[Source](../sources/historical-plans/freeborn-hostility/probe_extdbc2.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/probe_extdbc3.py

[Source](../sources/historical-plans/freeborn-hostility/probe_extdbc3.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/probe_wxl_exports.py

[Source](../sources/historical-plans/freeborn-hostility/probe_wxl_exports.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/probe_wxl_strings.py

[Source](../sources/historical-plans/freeborn-hostility/probe_wxl_strings.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/probe_wxl_utf16.py

[Source](../sources/historical-plans/freeborn-hostility/probe_wxl_utf16.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/scan_client_chrraces.py

[Source](../sources/historical-plans/freeborn-hostility/scan_client_chrraces.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/scan_client_dbc.py

[Source](../sources/historical-plans/freeborn-hostility/scan_client_dbc.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/simulate_final.py

[Source](../sources/historical-plans/freeborn-hostility/simulate_final.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/simulate_row.py

[Source](../sources/historical-plans/freeborn-hostility/simulate_row.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-hostility/verify_client_deploy.py

[Source](../sources/historical-plans/freeborn-hostility/verify_client_deploy.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/freeborn-login-crash/disasm.py

[Source](../sources/historical-plans/freeborn-login-crash/disasm.py)

Minimal PE32 helper + capstone disassembler for Wow.exe 3.3.5a (image base 0x400000). Usage: python disasm.py
func <va> # show the function containing <va> python disasm.py range <va> [n] # disassemble n instructions
from <va> python disasm.py stack <dump> <esp> # walk the EBP chain in a minidump's memory

## historical-plans/freeborn-login-crash/dump_exception.py

[Source](../sources/historical-plans/freeborn-login-crash/dump_exception.py)

Parse a WoW 3.3.5a minidump (32-bit) and print the exception record + registers. Usage: python
dump_exception.py <file.dmp> [more.dmp ...]

## historical-plans/freeborn-login-crash/find_callers.py

[Source](../sources/historical-plans/freeborn-login-crash/find_callers.py)

Find call/jmp sites to a VA inside Wow.exe and print the function that contains them.

## historical-plans/freeborn-login-crash/find_tables.py

[Source](../sources/historical-plans/freeborn-login-crash/find_tables.py)

Find switch jump tables in the exe that point into a function, and decode them.

## historical-plans/freeborn-login-crash/resolve_frames.py

[Source](../sources/historical-plans/freeborn-login-crash/resolve_frames.py)

Given a WoW crash stack (return addresses), resolve the call/jmp before each one.

## historical-plans/freeborn-login-crash/scan_strings.py

[Source](../sources/historical-plans/freeborn-login-crash/scan_strings.py)

Scan a VA range for pushed/moved immediate operands that point at strings.

## historical-plans/freeborn-tooltip/lua_syntax_check.py

[Source](../sources/historical-plans/freeborn-tooltip/lua_syntax_check.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/login-persistence-fix/deploy.py

[Source](../sources/historical-plans/login-persistence-fix/deploy.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/login-persistence-fix/deploy_all.py

[Source](../sources/historical-plans/login-persistence-fix/deploy_all.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/add_alliance_illidari_client.py

[Source](../sources/historical-plans/races-9-port/add_alliance_illidari_client.py)

Add an Alliance Illidari (race 31) to the client's Patch-Y by cloning race 30. Eunoia ships two Illidari races
- 24 "Illidari NightElf" (Alliance, Common) and 27 "Illidari Blood Elf" (Horde, Orcish) - but only the Blood
Elf one was ported, which is why Alliance shows 12 races against Horde's 13 in the creator. The client builds
the creator's race list from `ChrRaces.alliance` plus `CharBaseInfo`, so a cloned row with `alliance = 0` puts
the new race on the Alliance side with no Lua changes. Cloned per table: * `ChrRaces` - race 30 -> 31, faction
1, alliance 0, Common, displays 60026/60027 * `CreatureDisplayInfo` - display rows 60024/60025 -> 60026/60027
(same model ids) * `CharBaseInfo` - every (30, class) -> (31, class) * `CharSections`, `CharHairGeosets`,
`CharacterFacialHairStyles` - race 30 rows -> 31 * `CharStartOutfit` - race 30 rows -> 31 (the packed race
byte inside field 1)

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/add_race_name_strings.py

[Source](../sources/historical-plans/races-9-port/add_race_name_strings.py)

Give the custom races their names in the creator's race lists. `CharacterCreate.lua` builds the race list with
`_G["RACE_" .. raceID]`, which only exists for the stock races, so the custom ones have been listed as "Race
16" and so on. This appends the missing globals to Patch-Y's copy of that file.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/align_legacy_races.py

[Source](../sources/historical-plans/races-9-port/align_legacy_races.py)

Point Pandaren and Vulpera's client ChrRaces rows at the display ids the server sends. The nine ported races
work because `ChrRaces` and the world DB agree on the display id: the client can map the player's display back
to the race, which is what gives it a portrait and a language list. Pandaren (18) and Vulpera (20) still
disagree - the client says 141687/141688 and 141254/141255 while the server sends 60004-60007 - so both still
render as plain creatures with no portrait and no known languages. This is the `align_vulpera_pandaren.py`
change without the extras links: display rows 60004-60007 already carry `ExtendedDisplayInfoID = 0` and no
bogus string offsets, the state every working race uses. Revert with `revert_vulpera_pandaren.py` if it turns
bad.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
parser.add_argument('--race', type=int, action='append', help='limit to one race id (default: both)')
```

## historical-plans/races-9-port/align_vulpera_pandaren.py

[Source](../sources/historical-plans/races-9-port/align_vulpera_pandaren.py)

Point the remaining custom races' client rows at the display ids the server sends. Broken (race 14) works:
client `ChrRaces` says 60002/60003 and the server sends exactly that. Vulpera and Pandaren use 141254/141255
and 141687/141688 in the client while the server sends 60006/60007 and 60004/60005, so the client never maps
the player's display id back to a race - no portrait, and no known languages (the chat gate). This aligns
them, the same way the nine ported races were aligned, and re-links the extras the port dropped.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/all_attachments.py

[Source](../sources/historical-plans/races-9-port/all_attachments.py)

Full attachment list for the Vulpera, human and pandaren models.

## historical-plans/races-9-port/append_plan.py

[Source](../sources/historical-plans/races-9-port/append_plan.py)

Append this pass to the running plan log.

## historical-plans/races-9-port/append_plan2.py

[Source](../sources/historical-plans/races-9-port/append_plan2.py)

Append the Vulpera helmet-fix pass to the running plan log.

## historical-plans/races-9-port/append_plan3.py

[Source](../sources/historical-plans/races-9-port/append_plan3.py)

Record the attachment-table finding and the calibration round.

## historical-plans/races-9-port/append_plan4.py

[Source](../sources/historical-plans/races-9-port/append_plan4.py)

Record the baked Vulpera anchor + geoset finding.

## historical-plans/races-9-port/apply_vulpera_head_anchor.py

[Source](../sources/historical-plans/races-9-port/apply_vulpera_head_anchor.py)

Bake the corrected head anchor into the Vulpera models and keep a small calibration ring. The client reads
attachment 11 from the array at header slot 0xF0 (43 records at 0x674c36 for the male). This rewrites that
record's pivot to the position computed from the model's own skull geometry, so every Vulpera helmet (`_Vu`
stem) sits on the head instead of ~0.2 above it, then re-stages the seven calibration stems with only the
*deltas* around that value so a refinement can still be picked in one session. Usage: python
apply_vulpera_head_anchor.py --dry-run python apply_vulpera_head_anchor.py

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/attachment_records.py

[Source](../sources/historical-plans/races-9-port/attachment_records.py)

Full attachment record for the head slot (id 11) across models.

## historical-plans/races-9-port/attachments_ordered.py

[Source](../sources/historical-plans/races-9-port/attachments_ordered.py)

Find the M2 attachment table by its ordered ids and print each pivot.

## historical-plans/races-9-port/breakdown_pa_vu.py

[Source](../sources/historical-plans/races-9-port/breakdown_pa_vu.py)

Break the donor's Pa/Vu head files down by kind.

## historical-plans/races-9-port/broken_head_attachment.py

[Source](../sources/historical-plans/races-9-port/broken_head_attachment.py)

Head attachment record of the working donor-style races (Broken, Eredar, Pandaren).

## historical-plans/races-9-port/build_vulpera_helm_calibration.py

[Source](../sources/historical-plans/races-9-port/build_vulpera_helm_calibration.py)

Stage seven Vulpera helmet variants so the anchor can be picked in one game session. Each variant is the
donor's Vulpera leather helm model with its vertices shifted by a different (back/forward, up/down) offset,
published under its own model stem, and seven leather helm items are re-pointed at those stems through
`ItemDisplayInfo`. Equipping the items in game shows every candidate at once instead of one client restart per
guess. Usage: python build_vulpera_helm_calibration.py --dry-run python build_vulpera_helm_calibration.py

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/character_flags.py

[Source](../sources/historical-plans/races-9-port/character_flags.py)

M2 global flags of the player models involved.

## historical-plans/races-9-port/character_header_raw.py

[Source](../sources/historical-plans/races-9-port/character_header_raw.py)

Raw header of the Vulpera model.

## historical-plans/races-9-port/check_donor_pool.py

[Source](../sources/historical-plans/races-9-port/check_donor_pool.py)

Check whether the ported display rows' string offsets are valid in the donor pool.

## historical-plans/races-9-port/check_fallback_reads.py

[Source](../sources/historical-plans/races-9-port/check_fallback_reads.py)

Do the borrowed-fallback names actually exist in our archives?

## historical-plans/races-9-port/check_helm_model_files.py

[Source](../sources/historical-plans/races-9-port/check_helm_model_files.py)

Which archive (if any) serves a helmet model file, ours vs donor. Usage: python check_helm_model_files.py
[name ...] Defaults to the three models the item trace resolved.

## historical-plans/races-9-port/check_order.py

[Source](../sources/historical-plans/races-9-port/check_order.py)

Verify DBC row ids are strictly ascending (the client binary-searches these tables).

## historical-plans/races-9-port/check_pa_vu_textures.py

[Source](../sources/historical-plans/races-9-port/check_pa_vu_textures.py)

Do the donor's Pa/Vu head models reference textures, and can we supply them?

## historical-plans/races-9-port/check_patch_y_capacity.py

[Source](../sources/historical-plans/races-9-port/check_patch_y_capacity.py)

How much room does Patch-Y's hash table have?

## historical-plans/races-9-port/check_playable_races.py

[Source](../sources/historical-plans/races-9-port/check_playable_races.py)

Is the Sethrak row (15) playable, and what are the faction/flag fields for our races?

## historical-plans/races-9-port/check_shoulders.py

[Source](../sources/historical-plans/races-9-port/check_shoulders.py)

Shoulder component coverage per code, ours vs donor.

## historical-plans/races-9-port/check_starter_gear.py

[Source](../sources/historical-plans/races-9-port/check_starter_gear.py)

Compare each custom race's starting outfit with the weapon skills it is granted. The server's
`CharStartOutfit.dbc` (data volume, not the client's copy) drives the items a new character receives;
`Player::CanUseItem()` refuses anything whose `RequiredSkill` the character has no value in, so an outfit the
race's skill block was not written for produces "you are not proficient" on the character's own starting
weapon.

Parser declarations:

```python
parser.add_argument('--sql', action='store_true', help='emit the fix statements')
```

## historical-plans/races-9-port/check_stem_codes.py

[Source](../sources/historical-plans/races-9-port/check_stem_codes.py)

What codes exist for the stems the donor has no Pa/Vu model for?

## historical-plans/races-9-port/compare_attachment_bone.py

[Source](../sources/historical-plans/races-9-port/compare_attachment_bone.py)

Compare the bone that hosts the head attachment in the human against the Vulpera's.

## historical-plans/races-9-port/compare_component_models.py

[Source](../sources/historical-plans/races-9-port/compare_component_models.py)

Compare donor/staged per-race item component models against stock codes by hash.

## historical-plans/races-9-port/compare_donor_displays.py

[Source](../sources/historical-plans/races-9-port/compare_donor_displays.py)

Compare donor CreatureDisplayInfo rows with the rows our client ships for the same models.

## historical-plans/races-9-port/compare_donor_rows.py

[Source](../sources/historical-plans/races-9-port/compare_donor_rows.py)

Field-by-field diff of our ChrRaces rows against the donor rows they were ported from.

## historical-plans/races-9-port/compare_head_pivots.py

[Source](../sources/historical-plans/races-9-port/compare_head_pivots.py)

Compare CreatureDisplayInfo/CreatureModelData rows and head pivots across races.

## historical-plans/races-9-port/compare_helmet_vis.py

[Source](../sources/historical-plans/races-9-port/compare_helmet_vis.py)

Compare HelmetGeosetVisData across our client and the donor.

## historical-plans/races-9-port/compare_skin_geosets.py

[Source](../sources/historical-plans/races-9-port/compare_skin_geosets.py)

List the geoset indices each model's level-0 .skin declares. Helmets in WotLK are drawn as character geosets
in the 1500+/1900+ range, so a model whose skin profile has no entries up there cannot show a hood or helm -
the client falls back to its missing-geometry placeholder (the blue/white checker cube).

## historical-plans/races-9-port/compare_vulpera_anim_sources.py

[Source](../sources/historical-plans/races-9-port/compare_vulpera_anim_sources.py)

Which donor archive serves each Vulpera .anim file, and do they differ?

## historical-plans/races-9-port/compare_vulpera_anims.py

[Source](../sources/historical-plans/races-9-port/compare_vulpera_anims.py)

Compare our Vulpera external .anim set with the donor client's, file by file.

## historical-plans/races-9-port/compare_vulpera_model.py

[Source](../sources/historical-plans/races-9-port/compare_vulpera_model.py)

Compare the shipped Vulpera model/skins/textures with the donor archive.

## historical-plans/races-9-port/compare_vulpera_rows.py

[Source](../sources/historical-plans/races-9-port/compare_vulpera_rows.py)

Numeric comparison of the Vulpera display/model rows, ours vs donor.

## historical-plans/races-9-port/convert_eredar_from_lightforged.py

[Source](../sources/historical-plans/races-9-port/convert_eredar_from_lightforged.py)

Finish the Eredar player-model conversion by copying the port's edits from the Lightforged. The donor's Eredar
player model and the donor's Lightforged model are the same mesh (23,816,416 vs 23,816,432 bytes, identical
header arrays and identical texture-replace tables). Our shipped Lightforged renders correctly because the
port edited it; this finds those edits by diffing the two Lightforged copies and replays them onto the Eredar,
matching each difference to its array entry through the file's own header offsets (the Eredar is 16 bytes
shorter, so raw offsets do not line up).

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/count_attachment_tables.py

[Source](../sources/historical-plans/races-9-port/count_attachment_tables.py)

Count candidate attachment tables in the Vulpera model (are there several?).

## historical-plans/races-9-port/coverage_shoulder_head.py

[Source](../sources/historical-plans/races-9-port/coverage_shoulder_head.py)

Coverage of Item\ObjectComponents\Shoulder and Head per race code, plus byte totals.

## historical-plans/races-9-port/crop_head_zoom.py

[Source](../sources/historical-plans/races-9-port/crop_head_zoom.py)

Crop and upscale the head area of the user's screenshot.

## historical-plans/races-9-port/crop_new_shot.py

[Source](../sources/historical-plans/races-9-port/crop_new_shot.py)

Zoom the new Vulpera screenshot.

## historical-plans/races-9-port/crop_tight.py

[Source](../sources/historical-plans/races-9-port/crop_tight.py)

Tight crop of the helmet/head region for a clear read of the offset.

## historical-plans/races-9-port/debug_fallback.py

[Source](../sources/historical-plans/races-9-port/debug_fallback.py)

Reproduce the fallback lookup through the fix script's own helpers.

## historical-plans/races-9-port/debug_fallback2.py

[Source](../sources/historical-plans/races-9-port/debug_fallback2.py)

Does opening Patch-Y for write break reads from the other handles?

## historical-plans/races-9-port/debug_fallback3.py

[Source](../sources/historical-plans/races-9-port/debug_fallback3.py)

Replicate the staging loop with diagnostics.

## historical-plans/races-9-port/diff_patch_y.py

[Source](../sources/historical-plans/races-9-port/diff_patch_y.py)

Diff DBC entries between two Patch-Y archives: python diff_patch_y.py <old.mpq> <new.mpq> [key ...].

## historical-plans/races-9-port/disasm_at.py

[Source](../sources/historical-plans/races-9-port/disasm_at.py)

Disassemble a window of a PE image: python disasm_at.py <exe> <hex-address> [length].

## historical-plans/races-9-port/disasm_va.py

[Source](../sources/historical-plans/races-9-port/disasm_va.py)

Disassemble a VA range of Wow.exe.

## historical-plans/races-9-port/donor_vulpera_sources.py

[Source](../sources/historical-plans/races-9-port/donor_vulpera_sources.py)

Every donor archive that ships the Vulpera model/skins, with sizes and hashes.

## historical-plans/races-9-port/dump_all_helmet_vis.py

[Source](../sources/historical-plans/races-9-port/dump_all_helmet_vis.py)

Dump every HelmetGeosetVisData row in our client.

## historical-plans/races-9-port/dump_attachment_pivots.py

[Source](../sources/historical-plans/races-9-port/dump_attachment_pivots.py)

Dump the head attachment pivot of each character model. Attachment records in the v264 M2 are 0x28 bytes:
+0x00 u32 id, +0x04 u16 bone, +0x06 u16 unk, +0x08 vec3 pivot, +0x14 u16 interpolation, u16 globalSequence,
+0x18 timestamps, +0x20 values

## historical-plans/races-9-port/dump_bone_tracks.py

[Source](../sources/historical-plans/races-9-port/dump_bone_tracks.py)

Decode the head attachment's bone tracks (translation/rotation/scale).

## historical-plans/races-9-port/dump_bones.py

[Source](../sources/historical-plans/races-9-port/dump_bones.py)

Dump M2 bone records (modern layout) and follow the head attachment's bone chain.

## historical-plans/races-9-port/dump_calibration_vis.py

[Source](../sources/historical-plans/races-9-port/dump_calibration_vis.py)

HelmetGeosetVis ids for the calibration items plus the original test helm.

## historical-plans/races-9-port/dump_chrraces_by_id.py

[Source](../sources/historical-plans/races-9-port/dump_chrraces_by_id.py)

ChrRaces rows keyed by their real id field, all string-looking fields shown.

## historical-plans/races-9-port/dump_chrraces_honest.py

[Source](../sources/historical-plans/races-9-port/dump_chrraces_honest.py)

Dump ChrRaces records honestly: header, record size, and every field of a few races.

## historical-plans/races-9-port/dump_chrraces_prefix.py

[Source](../sources/historical-plans/races-9-port/dump_chrraces_prefix.py)

Print ChrRaces field 6 (ClientPrefix) + name field per archive, as a control.

## historical-plans/races-9-port/dump_chrraces_rows.py

[Source](../sources/historical-plans/races-9-port/dump_chrraces_rows.py)

Dump every string-resolving field of selected ChrRaces rows, ours and donor.

## historical-plans/races-9-port/dump_dbc.py

[Source](../sources/historical-plans/races-9-port/dump_dbc.py)

Dump rows from any client DBC (read-only): python dump_dbc.py <key> [column] [value].

## historical-plans/races-9-port/dump_donor_chrraces.py

[Source](../sources/historical-plans/races-9-port/dump_donor_chrraces.py)

Dump donor ChrRaces prefixes from its locale archives (last one wins).

## historical-plans/races-9-port/dump_exe_strings.py

[Source](../sources/historical-plans/races-9-port/dump_exe_strings.py)

Dump the ASCII strings in a window of Wow.exe.

## historical-plans/races-9-port/dump_helmet_geoset_vis.py

[Source](../sources/historical-plans/races-9-port/dump_helmet_geoset_vis.py)

Dump HelmetGeosetVisData rows used by helm 30935, plus the header shape.

## historical-plans/races-9-port/dump_item_display_rows.py

[Source](../sources/historical-plans/races-9-port/dump_item_display_rows.py)

Dump raw ItemDisplayInfo rows for the item ids we are tracing.

## historical-plans/races-9-port/dump_languages_dbc.py

[Source](../sources/historical-plans/races-9-port/dump_languages_dbc.py)

Dump DBFilesClient\Languages.dbc (it lives in the locale MPQ, not Data\*.MPQ).

## historical-plans/races-9-port/dump_m2_attach2.py

[Source](../sources/historical-plans/races-9-port/dump_m2_attach2.py)

Locate and dump M2 attachment records (v264) for character models. M2 header (version 264): magic, version,
name[64], then a run of {count, offset} descriptors. Attachment records are {u32 id, u16 bone, u16 unk,
M2Track position, u8 animateAttached}; the position track's value array holds the pivot.

## historical-plans/races-9-port/dump_m2_attachments.py

[Source](../sources/historical-plans/races-9-port/dump_m2_attachments.py)

Locate and dump a model's attachment table. Attachment records start with their id (0, 1, 2, ...), so the
table can be found without knowing the exact header layout: scan for an array whose first dword of each record
counts up.

## historical-plans/races-9-port/dump_m2_header.py

[Source](../sources/historical-plans/races-9-port/dump_m2_header.py)

Print the M2 header array descriptors so the layout can be read off directly.

## historical-plans/races-9-port/dump_model_box.py

[Source](../sources/historical-plans/races-9-port/dump_model_box.py)

Header + bounding box of head component models, ours vs donor.

## historical-plans/races-9-port/dump_prefix_correct.py

[Source](../sources/historical-plans/races-9-port/dump_prefix_correct.py)

Correct ChrRaces prefix dump: field 6 resolved by byte offset into the pool.

## historical-plans/races-9-port/dump_race_suffix_table.py

[Source](../sources/historical-plans/races-9-port/dump_race_suffix_table.py)

Dump the per-race pointer table the item-component path builder indexes.

## historical-plans/races-9-port/dump_skin_geosets_all.py

[Source](../sources/historical-plans/races-9-port/dump_skin_geosets_all.py)

All geoset/skinSection pairs in the Vulpera skins vs a stock race's.

## historical-plans/races-9-port/dump_skin_header.py

[Source](../sources/historical-plans/races-9-port/dump_skin_header.py)

Dump the header of character .skin files (old WotLK layout).

## historical-plans/races-9-port/dump_stock_chrraces.py

[Source](../sources/historical-plans/races-9-port/dump_stock_chrraces.py)

Print id/flags/faction/displays/filestring for every ChrRaces row of a client install.

## historical-plans/races-9-port/dump_vis_fields.py

[Source](../sources/historical-plans/races-9-port/dump_vis_fields.py)

Exact field indices of the helmet geoset-vis ids in ItemDisplayInfo rows.

## historical-plans/races-9-port/dump_vulpera_model_rows.py

[Source](../sources/historical-plans/races-9-port/dump_vulpera_model_rows.py)

Dump CreatureModelData rows for the Vulpera models with every string field.

## historical-plans/races-9-port/edit_add_set.py

[Source](../sources/historical-plans/races-9-port/edit_add_set.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/edit_compare_rows.py

[Source](../sources/historical-plans/races-9-port/edit_compare_rows.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/edit_fix_script.py

[Source](../sources/historical-plans/races-9-port/edit_fix_script.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/edit_fix_script2.py

[Source](../sources/historical-plans/races-9-port/edit_fix_script2.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/edit_fix_script3.py

[Source](../sources/historical-plans/races-9-port/edit_fix_script3.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/edit_fix_script4.py

[Source](../sources/historical-plans/races-9-port/edit_fix_script4.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/edit_fix_script5.py

[Source](../sources/historical-plans/races-9-port/edit_fix_script5.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/edit_fix_script6.py

[Source](../sources/historical-plans/races-9-port/edit_fix_script6.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/edit_fix_script7.py

[Source](../sources/historical-plans/races-9-port/edit_fix_script7.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/edit_head_top.py

[Source](../sources/historical-plans/races-9-port/edit_head_top.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/edit_plot_fix.py

[Source](../sources/historical-plans/races-9-port/edit_plot_fix.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/find_attachment_descriptor.py

[Source](../sources/historical-plans/races-9-port/find_attachment_descriptor.py)

Which header slot points at each model's attachment table?

## historical-plans/races-9-port/find_attachment_link_calls.py

[Source](../sources/historical-plans/races-9-port/find_attachment_link_calls.py)

What attachment ids does the client link item components to?

## historical-plans/races-9-port/find_attachment_table.py

[Source](../sources/historical-plans/races-9-port/find_attachment_table.py)

Brute-force locate the attachment array: ordered small ids at a fixed stride.

## historical-plans/races-9-port/find_dbc_helper_calls.py

[Source](../sources/historical-plans/races-9-port/find_dbc_helper_calls.py)

Find call sites of two DBC helpers and show the surrounding push constants.

## historical-plans/races-9-port/find_dbc_objects.py

[Source](../sources/historical-plans/races-9-port/find_dbc_objects.py)

Which DBC objects are passed to the row-lookup helper 0x4cfd90?

## historical-plans/races-9-port/find_donor_chrraces.py

[Source](../sources/historical-plans/races-9-port/find_donor_chrraces.py)

Find ChrRaces.dbc anywhere in the donor client.

## historical-plans/races-9-port/find_failing_difference.py

[Source](../sources/historical-plans/races-9-port/find_failing_difference.py)

Find fields where the two failing races differ from every working race. Working set (reported in game):
16,17,18,19,21,22,23,28,30 (Pandaren talks). Failing: 20 (Vulpera), 29 (Kul Tiran).

## historical-plans/races-9-port/find_head_bone.py

[Source](../sources/historical-plans/races-9-port/find_head_bone.py)

Which bone index carries the Head key bone, and how do the head attachments sit?

## historical-plans/races-9-port/find_helmet_vis_string.py

[Source](../sources/historical-plans/races-9-port/find_helmet_vis_string.py)

Find the HelmetGeosetVisData string and its references in Wow.exe.

## historical-plans/races-9-port/find_lua_api.py

[Source](../sources/historical-plans/races-9-port/find_lua_api.py)

Locate a Lua API registration entry (name -> handler) inside a WoW client executable. Usage: python
find_lua_api.py <exe> <api-name> [<api-name> ...] Prints the registration record, the raw handler dword and a
disassembly window.

## historical-plans/races-9-port/find_path_builder.py

[Source](../sources/historical-plans/races-9-port/find_path_builder.py)

Locate race-prefix strings and ObjectComponents references in the client binaries.

## historical-plans/races-9-port/find_prefix_offsets.py

[Source](../sources/historical-plans/races-9-port/find_prefix_offsets.py)

Find which ChrRaces row/field references the strings we care about.

## historical-plans/races-9-port/find_refs.py

[Source](../sources/historical-plans/races-9-port/find_refs.py)

Find code/data references to an absolute address: python find_refs.py <exe> <hex-address> [limit].

## historical-plans/races-9-port/find_tables_relaxed.py

[Source](../sources/historical-plans/races-9-port/find_tables_relaxed.py)

Find attachment tables whose ids are consecutive but do not start at 0.

## historical-plans/races-9-port/fix_display_id_band.py

[Source](../sources/historical-plans/races-9-port/fix_display_id_band.py)

Move the nine ported races out of the 900xx display-id band. AzerothCore stores a player's display id in
`PlayerInfo::displayId_m/f`, which is a `uint16` (src/server/game/Entities/Player/Player.h), while `ChrRaces`
itself is `uint32`. 90004 therefore wrapped to 24468 and the client drew
`Creature\LasherOrchid\LasherOrchid.mdx` for a Nightborne. Sethrak (60000/60001), Broken (60002/60003),
Pandaren (60004/60005) and Vulpera (60006/60007) already sit in the sub-65536 band; this rewrites the client
half for the nine ported races into the free 60008-60025 slots, matching the SQL/DB change made by the same
fix.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/fix_display_row_strings.py

[Source](../sources/historical-plans/races-9-port/fix_display_row_strings.py)

Clear the donor string offsets that leaked into the ported races' player display rows.
`CreatureDisplayInfo.TextureVariation_1/2/3` and `PortraitTextureName` are *string* offsets into the DBC's own
string pool. Every stock player row, every one of Esteria's working custom rows (Broken 60002/60003, Sethrak
60000/60001) and the donor's own player rows for these races carry 0 there. The ported rows 60008-60025
instead carry ``51`` in all four fields, because the rows were re-keyed from donor *NPC* rows whose offsets
only resolve against the donor's pool - in our pool offset 51 lands inside "HumanMaleCitizenLow", i.e. it is
not a string at all. The same four fields are garbage on the older Vulpera/Pandaren player rows
(141254/141255, 141687/141688), which is why those two never had portraits either. This zeroes field 3
(`ExtendedDisplayInfoID`), fields 6-8 (`TextureVariation_*`) and field 9 (`PortraitTextureName`) on those
rows, matching the server DB (`creaturedisplayinfo_dbc`) and the player-row shape every working race uses.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/fix_glue_ambience.py

[Source](../sources/historical-plans/races-9-port/fix_glue_ambience.py)

Stop the glue screens from breaking on the ported races. `CharacterSelect.lua` and `GlueParent.lua` both do
`PlayGlueAmbience(GlueAmbienceTracks[strupper(name)], 4.0)`. For a race that has no entry the argument is nil,
the native call errors out, and the character select screen aborts - which is why freshly created characters
never appeared in the list. Two fixes: give the ported races the same glue tables the stock races have (fog,
glow, ambience, lights), and make both call sites tolerate a missing track so this can never take a screen
down again.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/fix_item_component_prefixes.py

[Source](../sources/historical-plans/races-9-port/fix_item_component_prefixes.py)

Make helmets (and other head components) resolve for every custom race. Wow.exe builds the model path in the
item-component code at 0x732100: sprintf(buffer, "%s%s_%s%s.mdx", path, modelName, ChrRaces->ClientPrefix,
sex) `path` is `Item\ObjectComponents\Head\` (0x9f6c0c), `modelName` comes from `ItemDisplayInfo.ModelName`,
and `ClientPrefix` is `ChrRaces` field 6 - the code reads it as `[row + 0x18]`. When the resulting file is
absent the client draws its white/blue missing-model cube. Our port invented per-race prefixes (`Er`, `Nb`,
`Ve`, `Lf`, `Za`, `Di`, `Kt`, `Il`) that no archive supplies, which is why every ported race cubes its helm
while race 14 (Broken, prefix `Bk`) renders fine - Patch-C ships a full `_Bk` model set. The donor client
solves it by pointing each race at a code it already ships a set for (Eredar -> Draenei, Zandalari -> Troll,
Void Elf/Illidari -> Blood Elf, ...); Pandaren and Vulpera carry dedicated `_Pa`/`_Vu` sets. Staging fills
only the names the client cannot already resolve - the donor's copy where it has one, otherwise a borrowed
stock model - so stock art is never overwritten. `--stage-code` stages an extra code (for experiments) without
editing STAGE_CODES. Usage: python fix_item_component_prefixes.py --dry-run python
fix_item_component_prefixes.py

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
parser.add_argument('--skip-stage', action='store_true')
parser.add_argument('--force-stage', action='store_true', help='re-stage names the client already resolves')
```

Long declarations for this entry are preserved in the linked tool-index.json.

## historical-plans/races-9-port/fix_language_masks.py

[Source](../sources/historical-plans/races-9-port/fix_language_masks.py)

Let the client recognise the ported races' language skills. `GetNumLanguages()` (Wow.exe 0x500760) walks
`Languages.dbc` and for each row asks `0x6e0640(player, languageId, &out)`. That helper resolves the
language's spell id, finds the `SkillLineAbility.dbc` row for that spell (`0x812410`, records at `0xad45b4`,
stride 0x38), and then looks for the row's *SkillLine* id in the player's skill table. `0x812410` refuses rows
whose `RaceMask` does not contain the player's race, so a custom race is simply never counted - the client
reports zero languages and refuses to send chat ("You don't know that language"). Esteria already patched
exactly these masks for their own custom races: Common 668 carries mask 7245 (races 1,3,4,7,11,12,13) and
Orcish 669 mask 25522 (races 2,5,6,8,9,10,14,15). Our nine ported races plus Pandaren/Vulpera are in none of
them. This ORs those races into every language row that has a non-zero mask. The mask only gates recognition -
a character still has to *have* the skill - so widening it cannot hand anybody a language they were not
granted.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/fix_lightforged_glow.py

[Source](../sources/historical-plans/races-9-port/fix_lightforged_glow.py)

Make the Lightforged skin overlay render like the Eredar one. The Eredar and Lightforged models we ship are
the same file to within 46 bytes. The only functional difference is `CreatureModelData`-independent: entry 14
of the model's texture-replace table, `(4, 4)` on the Eredar (whose skin glow renders in this client) against
`(2, 4)` on the Lightforged. Everything else - textures, texture animations, transforms, geosets - is
identical. This copies the Eredar's replace entry onto the Lightforged model so the Lightforged skin overlay
(the golden rune layer in `lightforgeddraeneimaleskinEXTRA_*.blp`) is bound the same way.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/fix_patch_y.py

[Source](../sources/historical-plans/races-9-port/fix_patch_y.py)

Repair the live Patch-Y: background scene keys, model paths, starting outfits. Three fixes, all written back
into `3.3.5a - Dev/Data/Patch-Y.MPQ`: 1. `CharacterCreate.lua` gains `RACE_BACKGROUND_KEYS` entries for the
nine ported races. Without them `SetBackgroundModel` is handed a race key with no `UI_<Race>.m2` scene, the
customize scene fails to build, and the character renders as the placeholder cube for every class except Death
Knight (whose key resolves to the stock `UI_DeathKnight` scene). 2. `CreatureModelData` paths for those races
are pointed at the models we ship, so Eredar stops looking for Eunoia's `Race_EredarMale.m2`. 3.
`CharStartOutfit` rows for the races are rebuilt from Vulpera's rows with the gear left in place (the previous
diagnostic build blanked every item slot, which is why the previews came up naked).

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/fix_race_display_extras.py

[Source](../sources/historical-plans/races-9-port/fix_race_display_extras.py)

Give the nine ported races the same display -> extra link the working custom races have. `add_extra_rows.py`
from the Vulpera/Pandaren work shows the contract: each custom race's player display row carries a
`DisplayidExtra` that points at a `CreatureDisplayInfoExtra` row whose RaceID/Gender match the race.
Vulpera/Pandaren were built that way (60006 -> 45443, race 20), and their unit frame portraits render. The
ported races were shipped with `DisplayidExtra = 0` (and their dangling references were later cleared), which
is why their portraits come up empty. This adds extra rows 45445-45462 (race 16..30, male/female) cloned from
the Sethrak template that the working rows use, and links the 60008-60025 display rows to them.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/fix_race_exploration_sound.py

[Source](../sources/historical-plans/races-9-port/fix_race_exploration_sound.py)

Set ChrRaces.ExplorationSoundID (field 3) on the ported races. Perfect correlation across the client's table:
races 1-15 all carry a non-zero ExplorationSoundID (4140-4147) and render portraits / know their languages,
while races 16-30 - including Vulpera and Pandaren - carry 0 and do neither. Broken (14, 4141) is the user-
confirmed working case. Copy a same-faction stock race's value.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/fix_race_languages.py

[Source](../sources/historical-plans/races-9-port/fix_race_languages.py)

Grant every playable-race language to the ported races. The client refuses chat with ERR_CANT_SPEAK_LANGAGE
and the server answers LANG_NOT_LEARNED_LANGUAGE ("You don't know that language") because the language id the
client sends has no matching skill on the character. Rather than guess which id the client picks, give every
ported race the full set of playable-race languages.

Parser declarations:

```python
parser.add_argument('--apply', action='store_true')
```

## historical-plans/races-9-port/fix_race_modeldata_sql.py

[Source](../sources/historical-plans/races-9-port/fix_race_modeldata_sql.py)

Sync the server's CreatureModelData rows for the ported races with the client. Clients and servers share the
model geometry: Patch-Y now carries Eunoia's own collision/mount/bounding-box numbers for the 18 race models,
and the server's `creaturemodeldata_dbc` overlay must say the same thing. Field types are taken from the table
schema so float columns get real floats, not their bit patterns.

Parser declarations:

```python
parser.add_argument('--apply', action='store_true')
```

## historical-plans/races-9-port/fix_race_start_spells.py

[Source](../sources/historical-plans/races-9-port/fix_race_start_spells.py)

Give the ported races a full class spell set (weapon skills, stances, language). The nine ported races only
carried ~31 hand-written rows in `playercreateinfo_spell_custom`, so a new character missed the weapon-skill
spells (One-Handed Swords/Axes/..., Defense, Bows, Guns, ...) and the language spell, even though
`playercreateinfo_skills` already hands out Defense/Unarmed/Cloth and one class tab. Copying a faction-
appropriate stock race's class blocks fixes both. Runs read-only against the live DB and writes
`rev_1787850000005_race_start_spells.sql`; pass --apply to also run it.

Parser declarations:

```python
parser.add_argument('--apply', action='store_true')
```

## historical-plans/races-9-port/fix_race_visuals.py

[Source](../sources/historical-plans/races-9-port/fix_race_visuals.py)

Fix the ported races' camera data, portrait displays and chat language in Patch-Y. 1. CreatureModelData: every
one of the 18 race model rows was written as a clone of one template (collision 2.03/1.00, bounding box maxZ
1.568) instead of the model's own numbers, so the camera framed the character around the waist or knees. Copy
the values Eunoia ships for the same model files. 2. CreatureDisplayInfo: display rows 33070/32902
(Nightborne) and 33174 (Void Elf male) carried `DisplayidExtra` references that no client we own can satisfy;
every stock race ships 0 there. Drop back to 0 and retire the leftover extra row. 3. ChrRaces: Void
Elf/Lightforged/Dark Iron carried the donor's Horde language (1) while the server says Alliance/Common (7/0);
align the client rows.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/fix_server_skillrace.py

[Source](../sources/historical-plans/races-9-port/fix_server_skillrace.py)

Let the ported races inherit their host race's rows in the server's SkillRaceClassInfo.dbc.
`Player::LearnDefaultSkill()` (Player.cpp) starts with `SkillRaceClassInfoEntry const* rcInfo =
GetSkillRaceClassInfo(skill, race, class); if (!rcInfo) return;` so a skill listed in
`playercreateinfo_skills` is only actually applied when this DBC has a row whose RaceMask/ClassMask match. The
stock rows stop at race 14 (masks 16383 / 14592 / ...), so every custom race silently learned nothing: a
Vulpera Hunter ends up without Axes (44) or Bows (45), and `Player::CanUseItem()` reports
EQUIP_ERR_NO_REQUIRED_PROFICIENCY (`GetSkillValue(proto->RequiredSkill) == 0`) when they try to equip their
starting gear. Each custom race inherits the rows of the stock race whose starting zone it uses: 14 Broken, 16
Eredar, 20 Vulpera, 22 Zandalari, 28 Dracthyr -> 2 Orc (Durotar) 17 Nightborne, 30 Illidari -> 10 Blood Elf
(Eversong) 18 Pandaren, 19 Void Elf -> 1 Human (Elwynn) 21 Lightforged Draenei -> 11 Draenei (Azuremyst) 23
Dark Iron Dwarf, 29 Kul Tiran -> 3 Dwarf (Dun Morogh) Run with --dry-run to see the row deltas, or --write to
copy the patched file into the worldserver's data volume (a backup of the original is kept next to this
script).

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
parser.add_argument('--write', action='store_true')
```

## historical-plans/races-9-port/fix_skillrace_masks.py

[Source](../sources/historical-plans/races-9-port/fix_skillrace_masks.py)

Let the client accept race 20 (Vulpera) wherever its tables say "all races". The client's language check
resolves every language through `SkillRaceClassInfo.dbc`: `0x812410` finds the `SkillLineAbility` row for the
language's spell and then calls `0x810ed0(skill, race, class)`, which walks this table's records (stride 0x20)
and requires `raceMask & (1 << (race - 1))`. Almost every stock row carries `0xFFF7FFFF` - the "all races"
mask with **bit 19 cleared, i.e. race 20 excluded** - because race 20 is an NPC race in the stock table. Our
playable Vulpera *is* race 20, so every one of its language lookups fails and the client ends up with an empty
language list: `/say` then reports "You cannot speak that language". This is why Vulpera is the only ported
race that cannot chat. This ORs bit 19 back into every `0xFFF7FFFF` row and ships the patched table in
`Patch-Y`.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/fix_starter_gear_skills.py

[Source](../sources/historical-plans/races-9-port/fix_starter_gear_skills.py)

Grant every custom race/class the skills its own starting outfit needs. The outfits were rebuilt from the old
Vulpera rows and do not match the host race's weapon kit: a Vulpera Hunter starts with a two-handed axe
(12282) and a crossbow (23347) while the Orc block gives Axes (44) and Bows (45); a Dark Iron Warrior starts
with a two-handed sword (49778) while the Dwarf block gives Axes (44), Guns (46), Two-Handed Axes (172) and
Maces. `Player::CanUseItem()` and the client both want the matching skill line, so this walks the outfit rows
in `charstartoutfit_dbc`, maps each item's class/subclass to its skill, and adds the missing
`playercreateinfo_skills` rows for that race and class only.

Parser declarations:

```python
parser.add_argument('--write', action='store_true')
```

## historical-plans/races-9-port/fix_stem_line.py

[Source](../sources/historical-plans/races-9-port/fix_stem_line.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/fix_verify.py

[Source](../sources/historical-plans/races-9-port/fix_verify.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/fix_vulpera_head_attachment.py

[Source](../sources/historical-plans/races-9-port/fix_vulpera_head_attachment.py)

Move the Vulpera's head attachment to the top of the skull. Every race whose helmets render correctly has
`ChrRaces.ClientPrefix` pointing at a stock model set, and its `Item\ObjectComponents\Head` attachment (M2
attachment id 11) sits *inside* the skull - the human's is 0.18 above its head bone. The ported Vulpera model
(Patch-5 via Patch-C) instead anchors attachment 11 exactly on its head bone, i.e. at the neck, so any helm
lands low/forward and covers the face. The model already carries a head-top dummy bone (bone 197, pivot
-0.119/0.000/1.294) that marks where the skull ends. This rewrites the attachment's pivot to that point, in
every attachment table the model contains (the file has several identical copies), and stages the patched
model into `Patch-Y` so `Patch-C` stays untouched. Usage: python fix_vulpera_head_attachment.py --dry-run
python fix_vulpera_head_attachment.py

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/gen_alliance_illidari_sql.py

[Source](../sources/historical-plans/races-9-port/gen_alliance_illidari_sql.py)

Generate the world-SQL update that adds the Alliance Illidari (race 31). Clones the Horde Illidari (race 30)
and gives it the Alliance side of the donor's pair: Stormwind faction, Common, displays 60026/60027, and the
Night Elf start (Teldrassil) so the race learns the Night Elf class kit, its quests and its action bars.

## historical-plans/races-9-port/gen_race_start_sql.py

[Source](../sources/historical-plans/races-9-port/gen_race_start_sql.py)

Generate the two world-SQL updates that give the custom races a stock race's start. Every custom race adopts
the starting zone it uses, so it inherits that zone's stock race: Orc (2) <- 14 Broken, 16 Eredar, 20 Vulpera,
22 Zandalari, 28 Dracthyr (Durotar) Blood Elf (10) <- 17 Nightborne, 30 Illidari (Eversong) Human (1) <- 18
Pandaren, 19 Void Elf (Elwynn) Draenei (11) <- 21 Lightforged Draenei (Azuremyst) Dwarf (3) <- 23 Dark Iron
Dwarf, 29 Kul Tiran (Dun Morogh) Rows copied: `playercreateinfo_skills` (weapon/armor/class skill lines - this
is what `Player::CanUseItem()` needs before an item can be equipped), `playercreateinfo_spell_custom` (class
abilities and proficiency spells, only for the three races that had almost none), `playercreateinfo_action`
(starter action bars) and `playercreateinfo_cast_spell`. The quest update widens
`quest_template.AllowableRaces` with the custom race's bit for every quest its host race can take, which is
what lets a Vulpera Hunter pick up the Valley of Trials quests.

## historical-plans/races-9-port/grant_remaining_languages.py

[Source](../sources/historical-plans/races-9-port/grant_remaining_languages.py)

Grant the remaining server-side languages (Draconic/Demonic/Titan/Kalimag) so any language id the client sends
resolves to a skill the character has.

## historical-plans/races-9-port/grep_archive_helm.py

[Source](../sources/historical-plans/races-9-port/grep_archive_helm.py)

Grep archive listfiles for a substring (default: helmet model stems).

## historical-plans/races-9-port/grep_client_lua.py

[Source](../sources/historical-plans/races-9-port/grep_client_lua.py)

Search the client's Interface files for a Lua pattern: python grep_client_lua.py <pattern> [file-filter].

## historical-plans/races-9-port/grep_geoset_strings.py

[Source](../sources/historical-plans/races-9-port/grep_geoset_strings.py)

Search both binaries for geoset/helmet related strings.

## historical-plans/races-9-port/head_geometry_band.py

[Source](../sources/historical-plans/races-9-port/head_geometry_band.py)

Where is the Vulpera's head geometry, and where does an attached helm land?

## historical-plans/races-9-port/helm_bbox_table.py

[Source](../sources/historical-plans/races-9-port/helm_bbox_table.py)

Bounding boxes of the same helm across race codes (offset 0xA0 in these files).

## historical-plans/races-9-port/helm_global_flags.py

[Source](../sources/historical-plans/races-9-port/helm_global_flags.py)

M2 global flags of the helm models we have staged.

## historical-plans/races-9-port/helm_header_raw.py

[Source](../sources/historical-plans/races-9-port/helm_header_raw.py)

Raw header dump of two helm models.

## historical-plans/races-9-port/helm_model_layout.py

[Source](../sources/historical-plans/races-9-port/helm_model_layout.py)

Header descriptors + vertex box for the three helm models.

## historical-plans/races-9-port/helm_vertex_box.py

[Source](../sources/historical-plans/races-9-port/helm_vertex_box.py)

Vertex bounding box of item component models (where is the geometry authored?).

## historical-plans/races-9-port/helm_vertex_stride.py

[Source](../sources/historical-plans/races-9-port/helm_vertex_stride.py)

Find the vertex stride for the helm models by matching their bounding box.

## historical-plans/races-9-port/hunt_debug.py

[Source](../sources/historical-plans/races-9-port/hunt_debug.py)

Hunt for the head attachment record in models whose table is not id-ordered.

## historical-plans/races-9-port/hunt_head_attachment.py

[Source](../sources/historical-plans/races-9-port/hunt_head_attachment.py)

Hunt for the head attachment record in models whose table is not id-ordered.

## historical-plans/races-9-port/inspect_client_races.py

[Source](../sources/historical-plans/races-9-port/inspect_client_races.py)

Read-only dump of the live client's race tables (ChrRaces, display/model, customisation). Run with no
arguments for the full report, or `--model <path>` to list the geosets a model's level-0 .skin actually
contains.

Parser declarations:

```python
parser.add_argument('--model', action='append', default=[])
parser.add_argument('--race', type=int, action='append', default=[])
```

## historical-plans/races-9-port/inspect_display_rows.py

[Source](../sources/historical-plans/races-9-port/inspect_display_rows.py)

Print CreatureDisplayInfo fields 6-10 and the resolved portrait texture for chosen rows.

## historical-plans/races-9-port/inspect_extras.py

[Source](../sources/historical-plans/races-9-port/inspect_extras.py)

Dump CreatureDisplayInfoExtra rows: python inspect_extras.py <first> <last>.

## historical-plans/races-9-port/inspect_geoset_bones.py

[Source](../sources/historical-plans/races-9-port/inspect_geoset_bones.py)

Report which bones each geoset is skinned to, with bone bind positions. Ear meshes hang off dedicated ear
bones, so this is what identifies them without guessing from bounding boxes.

Parser declarations:

```python
parser.add_argument('model')
parser.add_argument('--lod', type=int, default=0)
parser.add_argument('--lateral', type=float, default=0.08)
```

## historical-plans/races-9-port/inspect_geoset_bounds.py

[Source](../sources/historical-plans/races-9-port/inspect_geoset_bounds.py)

Per-geoset bounding boxes for a client model, to locate ear/head meshes.

Parser declarations:

```python
parser.add_argument('model')
parser.add_argument('--lod', type=int, default=0)
```

## historical-plans/races-9-port/inspect_race_row.py

[Source](../sources/historical-plans/races-9-port/inspect_race_row.py)

Read-only dump of one or more ChrRaces rows plus the display/model/extra chain.

## historical-plans/races-9-port/inspect_skullsplitter.py

[Source](../sources/historical-plans/races-9-port/inspect_skullsplitter.py)

Skullsplitter Helm: what model and geoset-vis does it use, and does a Vu copy exist?

## historical-plans/races-9-port/inventory_components.py

[Source](../sources/historical-plans/races-9-port/inventory_components.py)

Inventory donor per-race item component models (Head, Shoulder) for codes we lack.

## historical-plans/races-9-port/list_head_models.py

[Source](../sources/historical-plans/races-9-port/list_head_models.py)

All distinct Item\ObjectComponents\Head file names in ours vs donor.

## historical-plans/races-9-port/list_patch_y.py

[Source](../sources/historical-plans/races-9-port/list_patch_y.py)

What is inside Patch-Y right now (names only).

## historical-plans/races-9-port/map_helm_coverage.py

[Source](../sources/historical-plans/races-9-port/map_helm_coverage.py)

Donor ChrRaces prefixes, plus per-prefix helmet model coverage in both clients.

## historical-plans/races-9-port/map_helm_prefixes.py

[Source](../sources/historical-plans/races-9-port/map_helm_prefixes.py)

Which race/sex suffixes exist for helmet object models, ours vs donor. Also prints the ChrRaces ClientPrefix
for every race so the two can be compared.

## historical-plans/races-9-port/patch_anchor_script.py

[Source](../sources/historical-plans/races-9-port/patch_anchor_script.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/patch_retune.py

[Source](../sources/historical-plans/races-9-port/patch_retune.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/patch_retune2.py

[Source](../sources/historical-plans/races-9-port/patch_retune2.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/patch_retune3.py

[Source](../sources/historical-plans/races-9-port/patch_retune3.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/patch_retune4.py

[Source](../sources/historical-plans/races-9-port/patch_retune4.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/patch_verify_anchor.py

[Source](../sources/historical-plans/races-9-port/patch_verify_anchor.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/plot_fit_skull.py

[Source](../sources/historical-plans/races-9-port/plot_fit_skull.py)

Fit view restricted to the skull and ear vertices (by dominant bone weight).

## historical-plans/races-9-port/plot_fit_views.py

[Source](../sources/historical-plans/races-9-port/plot_fit_views.py)

Accurate side/front fit view: Vulpera head vertices vs candidate helmets. Parser validated against the models'
own bounding boxes: vertices = M2Array at 0x3C, record stride 0x30 (48), bounding box at 0xA0.

## historical-plans/races-9-port/plot_head_fit_zoom.py

[Source](../sources/historical-plans/races-9-port/plot_head_fit_zoom.py)

Zoomed side-view fit plot: Vulpera head vertices vs the two helm models at the pivot.

## historical-plans/races-9-port/plot_vulpera_helm_fit.py

[Source](../sources/historical-plans/races-9-port/plot_vulpera_helm_fit.py)

Plot the Vulpera head-region vertices and the attached helm's vertices. The helm is a rigid model: its rest-
pose vertices plus the attachment pivot give its position. Drawing both as point clouds answers where the
client will put it.

## historical-plans/races-9-port/port_race.py

[Source](../sources/historical-plans/races-9-port/port_race.py)

Port a custom race from G:\Eunoia\Client into the Esteria dev client. Everything is written into a new
Patch-D.MPQ, so reverting is "delete the file". Per race it stages: * male/female .m2 and their four .skin
LODs, renamed to the path the server SQL already expects * every texture the donor's CharSections rows
reference, plus the model's own hardcoded textures * client DBC rows: ChrRaces, CreatureModelData,
CreatureDisplayInfo, CharSections, CharHairGeosets, CharBaseInfo * CharacterCreate.lua entries for the race
icon

## historical-plans/races-9-port/probe_import.py

[Source](../sources/historical-plans/races-9-port/probe_import.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/probe_string_pool.py

[Source](../sources/historical-plans/races-9-port/probe_string_pool.py)

Show CreatureDisplayInfo's string pool head and what offset 51 lands on.

## historical-plans/races-9-port/read_client_file.py

[Source](../sources/historical-plans/races-9-port/read_client_file.py)

Read a file straight out of the client archives (stock MPQs have no listfile). Usage: python
read_client_file.py "Interface\FrameXML\ChatFrame.lua" [pattern]

## historical-plans/races-9-port/read_real_attachments.py

[Source](../sources/historical-plans/races-9-port/read_real_attachments.py)

Read the Vulpera's real attachment array (header slot 0xF0) and the human's for contrast.

## historical-plans/races-9-port/read_slot_100.py

[Source](../sources/historical-plans/races-9-port/read_slot_100.py)

Read the array the Vulpera header points at from slot 0x100 (29 records).

## historical-plans/races-9-port/read_va_string.py

[Source](../sources/historical-plans/races-9-port/read_va_string.py)

Read C strings at given VAs in Wow.exe.

## historical-plans/races-9-port/repair_paths.py

[Source](../sources/historical-plans/races-9-port/repair_paths.py)

Library, test, or historical helper; inspect its source before use.

## historical-plans/races-9-port/retag_voidelf_ears.py

[Source](../sources/historical-plans/races-9-port/retag_voidelf_ears.py)

Make the Void Elf ear geometry render in this client. Bounds analysis (`inspect_geoset_bounds.py`) puts the
Void Elf ears on geoset `702` in every LOD - the only head mesh that protrudes sideways (y +-0.178 male,
+-0.174 female). The client renders the race's base geoset and the geosets its customisation tables name, and
nothing ever names group 7, so the ears stay hidden; the working custom races instead carry their ears on a
geoset the client reaches. Re-tagging the ear submeshes to geoset `7` folds them into the base variant the
client already draws, leaving every other submesh untouched.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/retune_vulpera_helm_calibration.py

[Source](../sources/historical-plans/races-9-port/retune_vulpera_helm_calibration.py)

Retune the Vulpera helm calibration around the computed ideal anchor. The Vulpera model's real attachment
array lives at header slot 0xF0 (43 records at 0x674c36). Entry 11 (the head slot) is `bone 195, pivot
(-0.001, 0.000, 1.270)`, which puts the donor Vulpera helm about 0.19 above the skull. The ideal offset is
computed here from the model itself: skull bounding box (vertices weighted to the head bone and its
descendants) minus the helmet's bounding box, then seven variants spread around it. Usage: python
retune_vulpera_helm_calibration.py --dry-run python retune_vulpera_helm_calibration.py

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/revert_vulpera_pandaren.py

[Source](../sources/historical-plans/races-9-port/revert_vulpera_pandaren.py)

Revert the Vulpera/Pandaren client changes (they crash the client on Foxbow). Restores the state that was
stable before the alignment: the races point back at their 141xxx display rows, the display->extra links are
cleared again and ExplorationSoundID returns to 0. The nine ported races keep their 60008-60025 alignment and
extras.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/sample_shoulders.py

[Source](../sources/historical-plans/races-9-port/sample_shoulders.py)

Sample shoulder component names.

## historical-plans/races-9-port/stage_eredar_model_textures.py

[Source](../sources/historical-plans/races-9-port/stage_eredar_model_textures.py)

Stage every texture the donor's Eredar player models reference. The player models carry their own texture list
(paths embedded in the M2 string block), and the files behind those paths only exist in the donor client, so
the race rendered untextured after the swap. This reads the `.blp` paths out of the two staged models, checks
which are missing from our client, and copies them from Eunoia into Patch-D.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/stage_eredar_player_model.py

[Source](../sources/historical-plans/races-9-port/stage_eredar_player_model.py)

Stage the donor's *player* Eredar model over the NPC one our race currently uses. Race 16 points at
`Character\Eredar\{Male,Female}\Eredar{Male,Female}.m2`, which the port staged as a creature-style model: it
has no player geoset layout and no helm attachments, so every helmet - hood geoset or attached model - comes
out as the client's error box. Eunoia's own Eredar race uses `character\eredar\<gender>
ace_eredar<gender>.m2`, a regular player model. This copies that model, its `.mdx` twin, its four `.skin` LODs
and its external `.anim` set over our path (nothing else in the client references `Character\Eredar\` - the
NPC eredar live under `Creature\Eredar\`).

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/stage_filestring_model_aliases.py

[Source](../sources/historical-plans/races-9-port/stage_filestring_model_aliases.py)

Stage character models under the path the client derives from ClientFilestring. In game the client builds a
character's model from the race's `ClientFilestring`:
`Character\<Filestring>\<Gender>\<Filestring><Gender>.m2` plus its `.skin` LODs (`Human` ->
`Character\Human\Male\HumanMale.m2`, and so on). The port only staged Eunoia's own folder names, so two races
have nothing to load in game: KulTiran -> CHARACTER\Naga_\male\kultiranmale.m2 Illidari ->
Character\BloodElf_Dh\Male\BloodElfMale_DH.m2 Both now also exist under their filestring paths. Every other
ported race already resolves because only the letter case differs.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/stage_race_anims.py

[Source](../sources/historical-plans/races-9-port/stage_race_anims.py)

Stage the ported models' external .anim files from Eunoia into Patch-Y. `port_race.py` deliberately left these
out (`STAGE_ANIMS = False`), but Eunoia's HD models do carry external sequences (e.g.
character\voidelf\male\voidelfmale0060-00.anim), and the client loads them during model init. Each staged
model gets the full set under its own name so the client never sees a mismatched animation set.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/stage_vulpera_anims.py

[Source](../sources/historical-plans/races-9-port/stage_vulpera_anims.py)

Stage the donor's Vulpera external animations, which match the model we ship. `stage_eunoia_vulpera.py` copied
Eunoia's HD model, its four `.skin` LODs and the textures, but not the external `.anim` files. Ours are the
older set from `patch-CHA.mpq` and differ in size and content for all 48 animations per gender (e.g. male
`0060-00.anim`: 102,624 bytes vs the donor's 196,640). The client loads sequences out of those files, so a
mismatched set gives it garbage track data - the crash both times was inside the keyframe search
(`M2.FindTrackKey`, `0x8285EB`, binary search over the key time array with a wild index). This copies every
`<stem>%04d-%02d.anim` the donor has into `Patch-Y`, so the HD model and its animations come from the same
source again.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/trace_helm_path_code.py

[Source](../sources/historical-plans/races-9-port/trace_helm_path_code.py)

Find the client code that builds Item\ObjectComponents\Head paths. Usage: python trace_helm_path_code.py <raw-
offset-of-string> [window]

## historical-plans/races-9-port/trace_item_display.py

[Source](../sources/historical-plans/races-9-port/trace_item_display.py)

Trace an item id to the model and texture files the client will ask for. python trace_item_display.py 30935

## historical-plans/races-9-port/trace_vulpera_models.py

[Source](../sources/historical-plans/races-9-port/trace_vulpera_models.py)

Resolve race -> display -> model path for Vulpera in ours and the donor.

## historical-plans/races-9-port/tune_race_button_spacing.py

[Source](../sources/historical-plans/races-9-port/tune_race_button_spacing.py)

Tighten the character creator's race-button grid. `CharacterCreate_PositionRaceButtons()` lays the faction
race buttons out in a two-column grid (`columnSpacing = 118`, `rowSpacing = 100`) starting 120 units from the
top-left/top-right corner. With the ported race list that step leaves too much air between the icons, so it is
reduced here.

Parser declarations:

```python
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/races-9-port/validate_patch_y_dbcs.py

[Source](../sources/historical-plans/races-9-port/validate_patch_y_dbcs.py)

Check every DBC in Patch-Y for the WDBC size invariant the client enforces: file size == 20 + rows * record +
string pool, and that the string pool is present.

## historical-plans/races-9-port/verify_calibration.py

[Source](../sources/historical-plans/races-9-port/verify_calibration.py)

Verify the staged calibration entries.

## historical-plans/races-9-port/verify_calibration2.py

[Source](../sources/historical-plans/races-9-port/verify_calibration2.py)

Confirm the retuned variants land where intended (world box vs the Vulpera skull).

## historical-plans/races-9-port/verify_calibration3.py

[Source](../sources/historical-plans/races-9-port/verify_calibration3.py)

Verify the staged variants really carry the intended vertex shift.

## historical-plans/races-9-port/verify_helm_coverage.py

[Source](../sources/historical-plans/races-9-port/verify_helm_coverage.py)

For the helm the user tested, confirm every custom race's resolved files exist.

## historical-plans/races-9-port/verify_prefix_edit.py

[Source](../sources/historical-plans/races-9-port/verify_prefix_edit.py)

Diff Patch-Y ChrRaces against the backup: only field 6 should move.

## historical-plans/races-9-port/vulpera_attachment_tables.py

[Source](../sources/historical-plans/races-9-port/vulpera_attachment_tables.py)

Compare the five attachment tables inside the Vulpera model, and find the header's.

## historical-plans/tuskarr-feet-robe/audit.py

[Source](../sources/historical-plans/tuskarr-feet-robe/audit.py)

Draw exact installed Tuskarr triangles for a bounded geometry audit.

## historical-plans/vulpera-pandaren-playable-races/add_creature_sound_rows.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/add_creature_sound_rows.py)

Add CreatureSoundData rows for the Vulpera/Pandaren player models. CreatureModelData.SoundID points at
CreatureSoundData. Rows 6278/6279 (Vulpera) and 4012/4080 (Pandaren) came from the Ascension donor and are
absent from this client, which leaves the world unit-sound lookup empty. Copy stock player rows whose
SoundEntries all exist locally.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/add_extra_rows.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/add_extra_rows.py)

Add CreatureDisplayInfoExtra rows for Pandaren/Vulpera like the working Sethrak rows.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/add_player_display_rows.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/add_player_display_rows.py)

Clone Pandaren/Vulpera display rows into the 16-bit player display range.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/add_skin_profiles.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/add_skin_profiles.py)

Give the custom race models four skin profiles like every working player model.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/add_starter_textures.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/add_starter_textures.py)

Copy the missing starter_barbarian item textures into Patch-C.

Parser declarations:

```python
parser.add_argument('--source', type=Path, required=True)
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/align_client_chrraces.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/align_client_chrraces.py)

Point the client's ChrRaces rows at the same 16-bit display ids the server sends.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/align_server_chrraces.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/align_server_chrraces.py)

Point the server-side ChrRaces.dbc at the 16-bit player display ids too.

## historical-plans/vulpera-pandaren-playable-races/apply_background_fix.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/apply_background_fix.py)

Patch the CharacterCreate.lua background fallback into Patch-C.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/apply_glue_fixes.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/apply_glue_fixes.py)

Apply the Broken background registration and ambience guard to Patch-C.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/build_server_dbc.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/build_server_dbc.py)

Build server runtime DBCs: client Patch-C rows win, server-only rows kept.

Parser declarations:

```python
parser.add_argument('--client', type=Path, required=True)
parser.add_argument('--server', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--disable-races', type=int, nargs='*', default=[])
```

## historical-plans/vulpera-pandaren-playable-races/check_all_archives.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_all_archives.py)

Resolve every start-outfit item asset for races 18/20 across all archives.

## historical-plans/vulpera-pandaren-playable-races/check_anim_coverage.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_anim_coverage.py)

List declared M2 sequences vs shipped .anim files for custom races.

## historical-plans/vulpera-pandaren-playable-races/check_anim_headers.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_anim_headers.py)

Compare external animation file headers between working and custom race models.

## historical-plans/vulpera-pandaren-playable-races/check_anim_pairs.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_anim_pairs.py)

Compare a model's declared animation entries with the .anim files the client can load. The WotLK client loads
external animation data as `<stem><animID:04d>-<subAnimID:02d>.anim`; an entry with no file leaves the client
without the track data it is about to evaluate. Usage: python check_anim_pairs.py <stem> [<stem> ...]
(default: the custom race models)

## historical-plans/vulpera-pandaren-playable-races/check_broken_chain.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_broken_chain.py)

Overlap + model-chain check for the Broken and Sethrak races.

## historical-plans/vulpera-pandaren-playable-races/check_charvariations.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_charvariations.py)

Locate CharVariations.dbc across every client archive and report its contents.

## historical-plans/vulpera-pandaren-playable-races/check_display_chain.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_display_chain.py)

Verify target race display/model chains across the winning archives.

## historical-plans/vulpera-pandaren-playable-races/check_display_extra.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_display_extra.py)

Check CreatureDisplayInfoExtra coverage for the custom player display ids.

## historical-plans/vulpera-pandaren-playable-races/check_donor_display_textures.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_donor_display_textures.py)

Compare target CreatureDisplayInfo texture fields between donor and Patch-C.

## historical-plans/vulpera-pandaren-playable-races/check_extra_rows.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_extra_rows.py)

Inspect the CreatureDisplayInfoExtra rows referenced by custom race displays.

## historical-plans/vulpera-pandaren-playable-races/check_extra_tables.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_extra_tables.py)

Inspect CharVariations / CreatureDisplayInfoGeosetData in donor and client.

## historical-plans/vulpera-pandaren-playable-races/check_geoset_data.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_geoset_data.py)

Check donor CreatureDisplayInfoGeosetData rows for the target race displays.

## historical-plans/vulpera-pandaren-playable-races/check_glue_assets.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_glue_assets.py)

Confirm Pandaren/Vulpera glue portrait assets resolve in the dev client.

## historical-plans/vulpera-pandaren-playable-races/check_glue_syntax.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_glue_syntax.py)

Structural checks on the live GlueParent.lua (missing commas, guard, BROKEN).

## historical-plans/vulpera-pandaren-playable-races/check_item_rows.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_item_rows.py)

Diagnose ItemDisplayInfo rows used by races 18/20 start outfits.

## historical-plans/vulpera-pandaren-playable-races/check_model_extensions.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_model_extensions.py)

Compare CharacterModelData paths for custom races between PATCH-A and Patch-C.

## historical-plans/vulpera-pandaren-playable-races/check_model_paths.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_model_paths.py)

Resolve target race display -> model path -> asset presence in Patch-C.

## historical-plans/vulpera-pandaren-playable-races/check_model_sounds.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_model_sounds.py)

Check the SoundID referenced by the custom race model rows.

## historical-plans/vulpera-pandaren-playable-races/check_model_texture_files.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_model_texture_files.py)

Check every texture a custom race M2 references: existence and dimensions.

## historical-plans/vulpera-pandaren-playable-races/check_outfit_models.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_outfit_models.py)

Trace start-outfit item models for races 18/20 through ItemDisplayInfo.

## historical-plans/vulpera-pandaren-playable-races/check_outfit_vs_donor.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_outfit_vs_donor.py)

Compare start-outfit ItemDisplayInfo rows between Patch-C and the donor.

## historical-plans/vulpera-pandaren-playable-races/check_race_display_ids.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_race_display_ids.py)

Check which candidate player display ids exist in the client and what they model.

## historical-plans/vulpera-pandaren-playable-races/check_section_textures.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_section_textures.py)

Verify CharSections texture paths for races 18/20 exist in Patch-C.

## historical-plans/vulpera-pandaren-playable-races/check_skin_profiles.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/check_skin_profiles.py)

Read numSkinProfiles from each custom race M2 and compare with shipped .skin files.

## historical-plans/vulpera-pandaren-playable-races/clear_combiner_flag.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/clear_combiner_flag.py)

Clear the M2 texture-combiner flag on the custom race models.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/compare_anim_sets.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/compare_anim_sets.py)

Compare animation file sets between custom race models.

## historical-plans/vulpera-pandaren-playable-races/compare_asset_bytes.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/compare_asset_bytes.py)

Hash-compare race model/skin/anim files between donor extraction and Patch-C.

## historical-plans/vulpera-pandaren-playable-races/compare_char_sections.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/compare_char_sections.py)

Compare CharSections section types/variations for races 18 and 20.

## historical-plans/vulpera-pandaren-playable-races/compare_chrraces_rows.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/compare_chrraces_rows.py)

Dump ChrRaces fields side by side for working and crashing custom races.

## historical-plans/vulpera-pandaren-playable-races/compare_customization.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/compare_customization.py)

Compare hair/customization table coverage between stock and custom races.

## historical-plans/vulpera-pandaren-playable-races/compare_m2_header.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/compare_m2_header.py)

Compare M2 header array counts/offsets between working and crashing models.

## historical-plans/vulpera-pandaren-playable-races/compare_model_data.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/compare_model_data.py)

Compare CreatureModelData rows: custom donor vs packaged vs working races.

## historical-plans/vulpera-pandaren-playable-races/compare_model_textures.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/compare_model_textures.py)

Compare M2 texture type slots between the Vulpera and Pandaren character models.

## historical-plans/vulpera-pandaren-playable-races/compare_race_assets.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/compare_race_assets.py)

Compare Vulpera/Pandaren asset coverage between the donor extraction and Patch-C.

## historical-plans/vulpera-pandaren-playable-races/compare_race_tables.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/compare_race_tables.py)

Per-race row counts for character tables: PATCH-A vs Patch-C vs PATCH-X.

## historical-plans/vulpera-pandaren-playable-races/count_archive_entries.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/count_archive_entries.py)

Compare entry counts between two archives.

## historical-plans/vulpera-pandaren-playable-races/diagnose_broken.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/diagnose_broken.py)

Compare race 14/15 outfit + model chains between the backup and the live archive.

## historical-plans/vulpera-pandaren-playable-races/diff_dbc_sets.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/diff_dbc_sets.py)

List donor DBC tables that the client archives do not contain.

## historical-plans/vulpera-pandaren-playable-races/diff_race_tables.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/diff_race_tables.py)

Row-level diff of race tables between client Patch-C and the server runtime.

## historical-plans/vulpera-pandaren-playable-races/disable_client_sethrak.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/disable_client_sethrak.py)

Set the client's ChrRaces NOT_PLAYABLE flag on race 15 to match the server.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/disasm_132.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/disasm_132.py)

Disassemble around the #132 faulting instruction.

## historical-plans/vulpera-pandaren-playable-races/disasm_crash.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/disasm_crash.py)

Disassemble the crashing frames of Wow.exe to identify the failing code.

## historical-plans/vulpera-pandaren-playable-races/dump_blp_headers.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/dump_blp_headers.py)

BLP dimensions for Vulpera vs Pandaren skin/extra textures.

## historical-plans/vulpera-pandaren-playable-races/dump_charvariations.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/dump_charvariations.py)

Dump CharVariations rows from the client locale archive and the donor.

## historical-plans/vulpera-pandaren-playable-races/dump_chrraces.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/dump_chrraces.py)

Dump ChrRaces rows from any DBC or MPQ for comparison.

Parser declarations:

```python
parser.add_argument('paths', nargs='+', type=Path)
parser.add_argument('--races', type=int, nargs='*')
```

## historical-plans/vulpera-pandaren-playable-races/dump_display_fields.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/dump_display_fields.py)

Print every field for a couple of display rows to spot anomalies.

## historical-plans/vulpera-pandaren-playable-races/dump_extra_reference.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/dump_extra_reference.py)

Dump the Sethrak extra rows and compare SoundEntries coverage with the donor.

## historical-plans/vulpera-pandaren-playable-races/dump_geosets.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/dump_geosets.py)

Show GeosetGroup values for the preview display rows.

## historical-plans/vulpera-pandaren-playable-races/dump_item_rows.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/dump_item_rows.py)

Print selected ItemDisplayInfo rows from an archive.

## historical-plans/vulpera-pandaren-playable-races/dump_m2_arrays.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/dump_m2_arrays.py)

Dump every M2 header array (count@offset) for working and crashing models.

## historical-plans/vulpera-pandaren-playable-races/dump_vulpera_sections.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/dump_vulpera_sections.py)

Show CharSections texture assignments for races 18/20 male, low variations.

## historical-plans/vulpera-pandaren-playable-races/eunoia_extract.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/eunoia_extract.py)

Read files out of Eunoia's client archives with StormLib in read-only mode. The running client holds the MPQs
open exclusively, but MPQ_OPEN_READ_ONLY still opens them for shared reading.

## historical-plans/vulpera-pandaren-playable-races/extract_entries.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/extract_entries.py)

Extract selected archive entries to a folder for inspection.

Parser declarations:

```python
parser.add_argument('--archive', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('names', nargs='+')
```

## historical-plans/vulpera-pandaren-playable-races/find_race_sounds.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/find_race_sounds.py)

Look for Pandaren/Vulpera named sound entries in the client.

## historical-plans/vulpera-pandaren-playable-races/find_starter_assets.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/find_starter_assets.py)

Scan Ascension archives for the missing starter_barbarian item textures.

## historical-plans/vulpera-pandaren-playable-races/fix_blood_fields.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/fix_blood_fields.py)

Normalise blood fields on the custom player display rows to stock player values.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/fix_display_textures.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/fix_display_textures.py)

Clear the corrupted texture overrides on the Pandaren/Vulpera display rows.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/fix_model_sound.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/fix_model_sound.py)

Replace the dangling SoundID on the Pandaren model rows with an existing entry.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/fix_race_display_sql.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/fix_race_display_sql.py)

Point every server-side race display mapping at the ids the client actually ships.

## historical-plans/vulpera-pandaren-playable-races/fix_race_display_sql_16bit.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/fix_race_display_sql_16bit.py)

Second pass: use the 16-bit player display ids (60004-60007).

## historical-plans/vulpera-pandaren-playable-races/flat_vulpera_textures.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/flat_vulpera_textures.py)

Flat-colour diagnostic for the Vulpera body. Rewrites the 256-entry palette of every Vulpera body texture so
the whole surface renders in one tone. Pixel indices, mip data, alpha bytes and file size are all untouched -
only the RGB of each palette entry changes. Purpose: tell paint apart from geometry. A painted colour feature
disappears into a flat surface; a modelled one still shows its silhouette.

Parser declarations:

```python
parser.add_argument('--live', type=Path, default=LIVE)
parser.add_argument('--backup-root', type=Path, default=REPO / '3.3.5a - Dev' / 'Backups')
parser.add_argument('--staging', type=Path, default=REPO / 'var' / 'flat-test')
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/vulpera-pandaren-playable-races/hide_unselected_race_border.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/hide_unselected_race_border.py)

Stop drawing the always-on circular border around character-create race icons. CharacterCreateEnumerateRaces
creates three textures per race button: staticTexture always visible, IconBorder_F tinted by faction <- remove
highlightTexture hover only, alpha 0.5 ADD (keep) checkedTexture selected only, IconBorderRace_H ADD (keep)
The XML defines none of them, so hiding staticTexture right after creation is enough. Class and gender buttons
use the same pattern with IconBorder_F1 and are deliberately left alone.

Parser declarations:

```python
parser.add_argument('--live', type=Path, default=LIVE)
parser.add_argument('--staging', type=Path, default=REPO / 'var' / 'race-border-fix')
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/vulpera-pandaren-playable-races/hide_vulpera_ankle.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/hide_vulpera_ankle.py)

Hide the body submeshes that sit entirely at ankle height. Reads pristine skins from a pre-change archive,
restores normal textures, keeps the arm fix (geosets 802/803) and additionally empties any geoset-0 submesh
whose whole vertical extent is below Z_LIMIT. For the male Vulpera that selects exactly one submesh (82
triangles); the female has none that qualify.

Parser declarations:

```python
parser.add_argument('--source', type=Path, required=True)
parser.add_argument('--live', type=Path, default=REPO / '3.3.5a - Dev' / 'Data' / 'Patch-C.MPQ')
parser.add_argument('--backup-root', type=Path, default=REPO / '3.3.5a - Dev' / 'Backups')
parser.add_argument('--staging', type=Path, default=REPO / 'var' / 'ankle-test')
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/vulpera-pandaren-playable-races/hide_vulpera_boots.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/hide_vulpera_boots.py)

Stage a Vulpera build with the arm sleeves and leg boots geosets hidden. Reads the skins from a pristine pre-
hide archive so this is a clean single change: sleeves 802/803 (confirmed to be the arm cuffs) plus the boot
variants 501-505 (candidates for the remaining leg cuffs). The previously hidden leg geosets 902/903 are
restored by reading from the pristine source. Geoset IDs, levels, vertex buffers and batches are all left
intact; only the submesh vertex/index ranges are zeroed.

Parser declarations:

```python
parser.add_argument('--source', type=Path, required=True, help='pristine archive to read the skins from')
parser.add_argument('--live', type=Path, default=REPO / '3.3.5a - Dev' / 'Data' / 'Patch-C.MPQ')
parser.add_argument('--backup-root', type=Path, default=REPO / '3.3.5a - Dev' / 'Backups')
parser.add_argument('--staging', type=Path, default=REPO / 'var' / 'geoset-hide2')
parser.add_argument('--dry-run', action='store_true')
```

Long declarations for this entry are preserved in the linked tool-index.json.

## historical-plans/vulpera-pandaren-playable-races/hide_vulpera_cuff.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/hide_vulpera_cuff.py)

Hide the Vulpera wrist-cuff geoset (1801) by emptying its submeshes. The Vulpera skin profiles carry a
66-vertex ring at forearm height that the working races do not have. Zeroing that submesh's vertex/index range
removes it from the draw list without touching buffers, batches or any other geoset.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/hide_vulpera_geosets.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/hide_vulpera_geosets.py)

Hide specific geosets in the Vulpera skin profiles (test build). Empties the vertex and index ranges of every
submesh belonging to the given geoset IDs, so the client draws nothing for them. Geoset ID and level are left
intact, and batches are untouched, so nothing else shifts. Default targets are the armour geosets: 802, 803 ->
group 08, Wristbands / Sleeves 902, 903 -> group 09, Legs (kneepads / legcuffs) This is a diagnostic build:
with these hidden the Vulpera shows no sleeves or legcuffs even when armour is equipped.

Parser declarations:

```python
parser.add_argument('--live', type=Path, default=REPO / '3.3.5a - Dev' / 'Data' / 'Patch-C.MPQ')
parser.add_argument('--geosets', type=int, nargs='*', default=list(DEFAULT_GEOSETS))
parser.add_argument('--targets', nargs='*', default=list(DEFAULT_TARGETS))
parser.add_argument('--backup-root', type=Path, default=REPO / '3.3.5a - Dev' / 'Backups')
parser.add_argument('--staging', type=Path, default=REPO / 'var' / 'geoset-hide')
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/vulpera-pandaren-playable-races/inspect_display_rows.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/inspect_display_rows.py)

Dump all CreatureDisplayInfo fields for the custom player displays.

## historical-plans/vulpera-pandaren-playable-races/inspect_orphans.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/inspect_orphans.py)

Show server-only CharStartOutfit/CharSections rows and client coverage.

## historical-plans/vulpera-pandaren-playable-races/locate_item_assets.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/locate_item_assets.py)

Find where start-outfit item models/textures live for races 18/20.

## historical-plans/vulpera-pandaren-playable-races/make_vulpera_uv_probe.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/make_vulpera_uv_probe.py)

Replace the Vulpera body skin textures with a UV probe grid. Column encodes hue (8 hues), row encodes
brightness (8 levels), palette index is row*8+col. Reading the colours off a screenshot tells which texture
cell each body part samples, and which cells the client overwrites with the armour sleeve.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--reference', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/map_vulpera_arm_uvs.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/map_vulpera_arm_uvs.py)

Rasterise which texels the Vulpera forearm / upper arm actually sample. Reads the live model out of Patch-C,
labels triangles by the key bones of their vertices (ArmL/R = forearm, ShoulderL/R = upper arm), rasterises
their UVs into the body texture space, and writes a couple of overlay images for inspection.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--model', default='character\\vulpera\\male\\vulperamale.m2')
parser.add_argument('--skin', default='character\\vulpera\\male\\vulperamale00.skin')
parser.add_argument('--texture', default='character\\vulpera\\male\\vulperamaleskin00_00.blp')
```

## historical-plans/vulpera-pandaren-playable-races/measure_table_gaps.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/measure_table_gaps.py)

Rows present in PATCH-A but absent from Patch-C, per character table.

## historical-plans/vulpera-pandaren-playable-races/mpq_hash_probe.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/mpq_hash_probe.py)

Resolve MPQ contents by name hash. Works on archives whose file names were stripped (hash-only) and on
archives a running game client holds open exclusively, because it reads the hash table with plain file I/O
instead of going through StormLib.

Parser declarations:

```python
parser.add_argument('--archives', required=True, help='glob for archives')
parser.add_argument('--names-file', type=Path, help='file with one probe path per line')
parser.add_argument('--listfile', type=Path, help='resolve every name in a listfile')
parser.add_argument('--limit', type=int, default=40, help='max resolved listfile names to print')
parser.add_argument('--grep', default='', help='only print listfile hits whose name matches')
```

## historical-plans/vulpera-pandaren-playable-races/normalize_model_paths.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/normalize_model_paths.py)

Rewrite CreatureModelData .mdx paths to .m2 when the .m2 file is present.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/parse_minidump.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/parse_minidump.py)

Parse the minidump header for the exception record and the faulting module.

## historical-plans/vulpera-pandaren-playable-races/per_race_counts.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/per_race_counts.py)

Per-race row counts for race tables, client Patch-C vs server runtime.

## historical-plans/vulpera-pandaren-playable-races/probe_eunoia_mpq.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/probe_eunoia_mpq.py)

Hash-table probe for Eunoia MPQs: works on locked, name-stripped archives.

## historical-plans/vulpera-pandaren-playable-races/rebuild_patch_c_entries.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/rebuild_patch_c_entries.py)

Regenerate the corrected ChrRaces + CharacterCreate.lua and stage an updated Patch-C.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/rebuild_patch_c_pass2.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/rebuild_patch_c_pass2.py)

Pass 2: stock preview outfits, revert Ascension item rows, restore Broken rows.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--stock-item-table', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/repaint_vulpera_arms.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/repaint_vulpera_arms.py)

Lift the dark fur band off the Vulpera forearm in the body skin textures. The probe run showed the "bracers"
are painted into the race's own skin texture: a warm, saturated dark band on the forearm strip (columns 1-2 of
the atlas). Desaturated darks (paw pads, nose) and bright fur are left alone, so the paws keep their pads and
the rest of the body is untouched.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--preview', type=Path)
```

## historical-plans/vulpera-pandaren-playable-races/repaint_vulpera_arms_masked.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/repaint_vulpera_arms_masked.py)

Repaint only the Vulpera arm islands, located from the model geometry. Arm vertices are picked by position
(well outside the torso in X, above the hips, below the neck) instead of bone tables, their UV triangles are
rasterised into a mask, and the dark warm band inside that mask gets a gentle gamma lift so the fur reads as
one piece while shading survives.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--preview', type=Path)
parser.add_argument('--dump-mask', type=Path)
```

## historical-plans/vulpera-pandaren-playable-races/restore_donor_models.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/restore_donor_models.py)

Restore the Vulpera/Pandaren M2 files to the donor bytes. The earlier crash hunt cleared the M2 texture-
combiner flag (0x8) and forced four skin profiles on these four models. The crash turned out to be 16-bit
display-id truncation, so those edits were unnecessary and invert the models away from the donor's known-good
rendering (eye/glow layers, LOD skins).

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--donor', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/restore_race_icons.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/restore_race_icons.py)

Restore the per-race character-create icons into Patch-C. A later step reverted both the icon files and the
Lua table that wires them, so every race except Pandaren and Vulpera fell back to the shared Races atlas.
Sources: pre-dxt5 (18:35 backup) - 30 uncompressed per-race icons (comp=3, 23016 B), the same format the live
Pandaren/Vulpera icons use post-dxt5 (18:58 backup) - the two HighElf icons, which only exist in DXT form -
the 32-entry RACE_ICON_TEXTURES table for the Lua

Parser declarations:

```python
parser.add_argument('--live', type=Path, default=LIVE)
parser.add_argument('--staging', type=Path, default=REPO / 'var' / 'race-icons-fix')
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/vulpera-pandaren-playable-races/revert_client_chrraces.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/revert_client_chrraces.py)

Restore the client ChrRaces target-race rows to the values that rendered in the list.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
```

## historical-plans/vulpera-pandaren-playable-races/scan_client_archives.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/scan_client_archives.py)

List which client archives carry the race/creation files and where they rank.

## historical-plans/vulpera-pandaren-playable-races/scan_client_strings.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/scan_client_strings.py)

Find continuation-loading strings in the dev client binaries.

## historical-plans/vulpera-pandaren-playable-races/scan_eunoia_byname.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/scan_eunoia_byname.py)

Probe Eunoia archives by exact MPQ path (works even when names are stripped).

## historical-plans/vulpera-pandaren-playable-races/set_vulpera_model.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/set_vulpera_model.py)

Point the Vulpera model rows back at the non-HD model in Patch-C and PATCH-X. The donor's Vulpera_HD mesh is a
retail-era export. In the 3.3.5a client it loses the mouth and ear pieces and renders the tail and back of the
head black, while the non-HD build keeps every customization part. Use --to hd to switch back to the HD paths.

Parser declarations:

```python
parser.add_argument('--to', choices=sorted(MODEL_PATHS), default='legacy')
parser.add_argument('--data-dir', type=Path, default=DATA)
parser.add_argument('--archives', nargs='*', default=list(TARGET_ARCHIVES))
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/vulpera-pandaren-playable-races/stage_eunoia_vulpera.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/stage_eunoia_vulpera.py)

Stage Eunoia's working Vulpera package into the dev client's Patch-C. Source:
G:\Eunoia\Client\data\Patch-5.mpq (opened read-only, since that client may be running) plus its
CharSections.dbc. Writes into R:\...\3.3.5a - Dev\Data\Patch-C.MPQ: * HD models and their four skin LODs, per
gender * every Vulpera texture their CharSections references, plus the two hardcoded eye textures baked into
their models * CharSections.dbc race-20 rows repointed at the tail / naked-torso layers * CharHairGeosets.dbc
and CharHairTextures.dbc race-20 rows replaced with their race-9 rows, so hair follows the HD model's geoset
numbering Patch-C is backed up before anything is written.

## historical-plans/vulpera-pandaren-playable-races/stage_hd_vulpera_models.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/stage_hd_vulpera_models.py)

Stage the donor Vulpera_HD model set into Patch-C and repoint the model rows. The donor server ships its
working Vulpera as Character\Vulpera_HD\... and points its CreatureModelData there. Our pack referenced the
non-HD character\vulpera\... build instead, which carries extra arm geometry that shows up as wrist cuffs.
This adds the HD files to Patch-C and repoints model rows 112885/112886 to them.

Parser declarations:

```python
parser.add_argument('--data-dir', type=Path, default=DATA)
parser.add_argument('--archives', nargs='*', default=list(TARGET_ARCHIVES))
parser.add_argument('--backup-root', type=Path, default=REPO / '3.3.5a - Dev' / 'Backups')
parser.add_argument('--staging', type=Path, default=REPO / 'var' / 'vulpera-hd-stage')
parser.add_argument('--skip-models', action='store_true', help='only repoint DBC rows; do not add model files')
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/vulpera-pandaren-playable-races/stage_slport_patchx.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/stage_slport_patchx.py)

Stage the Shadowlands-to-WOTLK Vulpera port into PATCH-X.

## historical-plans/vulpera-pandaren-playable-races/stage_slport_vulpera.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/stage_slport_vulpera.py)

Swap in the Shadowlands-to-WOTLK Vulpera port files. Stages Character\Vulpera\{Male,Female}\* from the port
into Patch-C and PATCH-X at character\vulpera\{male,female}\* (the port already uses the legacy naming), and
points CreatureModelData rows 112885/112886 at the port models. Files the port does not provide (legacy
01/02/03 skins, extra-*.blp) are left untouched.

Parser declarations:

```python
parser.add_argument('--data-dir', type=Path, default=DATA)
parser.add_argument('--archives', nargs='*', default=list(TARGET_ARCHIVES))
parser.add_argument('--backup-root', type=Path, default=REPO / '3.3.5a - Dev' / 'Backups')
parser.add_argument('--staging', type=Path, default=REPO / 'var' / 'slport-stage')
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/vulpera-pandaren-playable-races/stage_vulpera_hd_textures.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/stage_vulpera_hd_textures.py)

Ship the Vulpera HD model's missing eye textures into Patch-C and PATCH-X. The donor M2 files reference:
character\vulpera\male\VulperaMale_DK_Eyes.blp Character\Vulpera\female\vulperafemale_DK_Eyes.blp Neither
exists in any archive, so the client binds nothing and renders the affected surfaces black. Both files ship
inside the donor's Vulpera_HD folder.

Parser declarations:

```python
parser.add_argument('--data-dir', type=Path, default=DATA)
parser.add_argument('--archives', nargs='*', default=list(TARGET_ARCHIVES))
parser.add_argument('--backup-root', type=Path, default=REPO / '3.3.5a - Dev' / 'Backups')
parser.add_argument('--staging', type=Path, default=REPO / 'var' / 'vulpera-eyes-stage')
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/vulpera-pandaren-playable-races/swap_port_vulpera.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/swap_port_vulpera.py)

Swap in the Shadowland-to-WOTLK port's Vulpera model, correctly paired. The port ships one valid skin per
gender (profile 00) plus three `_lod0N.skin` files whose vertex indices overflow the model. Our own 01/02/03
slots hold data sized for the outgoing 17,276-vertex mesh, which overflows the port's 15,383-vertex mesh and
produced the screen-filling triangles on the last try. So: write the port M2, write the port's 00 skin into
all four profile slots, carry the animations and textures, and skip the orphan lod skins entirely.

Parser declarations:

```python
parser.add_argument('--data-dir', type=Path, default=DATA)
parser.add_argument('--archive', default='Patch-C.MPQ')
parser.add_argument('--backup-root', type=Path, default=REPO / '3.3.5a - Dev' / 'Backups')
parser.add_argument('--staging', type=Path, default=REPO / 'var' / 'portswap2')
parser.add_argument('--dry-run', action='store_true')
```

## historical-plans/vulpera-pandaren-playable-races/sync_server_dbc.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/sync_server_dbc.py)

Compare client Patch-C DBC tables against the worldserver runtime copies.

Parser declarations:

```python
parser.add_argument('--patch-c', type=Path, required=True)
parser.add_argument('--server-dbc', type=Path)
parser.add_argument('--export-root', type=Path)
```

## historical-plans/vulpera-pandaren-playable-races/trace_outfit_textures.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/trace_outfit_textures.py)

List preview-outfit item textures for races 18/20 and their archive variants.

## historical-plans/vulpera-pandaren-playable-races/verify_final_state.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/verify_final_state.py)

Final verification of the live Patch-C: preview outfits and dropped Ascension rows.

## historical-plans/vulpera-pandaren-playable-races/verify_item_rows.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/verify_item_rows.py)

Assert merged ItemDisplayInfo rows match donor strings for the start outfits.

## historical-plans/vulpera-pandaren-playable-races/verify_player_display_chain.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/verify_player_display_chain.py)

Resolve the custom-race display chain the way the live client does. PATCH-X.MPQ loads after Patch-C.MPQ and
ships its own CreatureDisplayInfo / CreatureModelData, so those two tables come from PATCH-X while ChrRaces
and CreatureSoundData come from Patch-C. This script mirrors that priority and fails loudly when a link is
missing.

## historical-plans/vulpera-pandaren-playable-races/vulpera_skin_roundtrip.py

[Source](../sources/historical-plans/vulpera-pandaren-playable-races/vulpera_skin_roundtrip.py)

Export the Vulpera body skins to PNG and import painted PNGs back to Patch-C. export: writes one PNG per BLP
next to a manifest (plain RGB, 512x512). import: quantises each PNG back to a 256-colour palette BLP, keeping
the original header/mip layout, and stages a replacement archive.

Parser declarations:

```python
sub.add_parser(name)
p.add_argument('--patch-c', type=Path, required=True)
p.add_argument('--in-dir', type=Path, required=True)
p.add_argument('--out', type=Path, default=None)
```

## wow-race-retroporter/src/raceporter/__init__.py

[Source](../sources/wow-race-retroporter/src/raceporter/__init__.py)

WoW Race Retroporter orchestration package.

## wow-race-retroporter/src/raceporter/__main__.py

[Source](../sources/wow-race-retroporter/src/raceporter/__main__.py)

Library, test, or historical helper; inspect its source before use.

## wow-race-retroporter/src/raceporter/acore/__init__.py

[Source](../sources/wow-race-retroporter/src/raceporter/acore/__init__.py)

AzerothCore SQL generation belongs here.

## wow-race-retroporter/src/raceporter/adapters/__init__.py

[Source](../sources/wow-race-retroporter/src/raceporter/adapters/__init__.py)

External-tool adapters.

## wow-race-retroporter/src/raceporter/adapters/base.py

[Source](../sources/wow-race-retroporter/src/raceporter/adapters/base.py)

Library, test, or historical helper; inspect its source before use.

## wow-race-retroporter/src/raceporter/cli.py

[Source](../sources/wow-race-retroporter/src/raceporter/cli.py)

Library, test, or historical helper; inspect its source before use.

Parser declarations:

```python
parser.add_argument('--project-root', type=Path, help='Repository root; auto-detected by default')
subs.add_parser('doctor', help='Validate repository, Retail source profile, and configured tools')
subs.add_parser('fetch', help='Discover and cache source assets for a race')
fetch.add_argument('race')
fetch.add_argument('--dry-run', action='store_true')
fetch.add_argument('--force', action='store_true')
subs.add_parser('plan', help='Show stage status for a race')
plan.add_argument('race')
subs.add_parser('build', help='Run/resume the full retroport pipeline')
build.add_argument('race')
build.add_argument('--dry-run', action='store_true')
build.add_argument('--force', action='store_true')
subs.add_parser('status', help='Print saved stage state')
status.add_argument('race')
subs.add_parser('reset', help='Clear saved stage state')
reset.add_argument('race')
```

## wow-race-retroporter/src/raceporter/config.py

[Source](../sources/wow-race-retroporter/src/raceporter/config.py)

Library, test, or historical helper; inspect its source before use.

## wow-race-retroporter/src/raceporter/dbc/__init__.py

[Source](../sources/wow-race-retroporter/src/raceporter/dbc/__init__.py)

WotLK DBC normalization and writer backends belong here.

## wow-race-retroporter/src/raceporter/glue/__init__.py

[Source](../sources/wow-race-retroporter/src/raceporter/glue/__init__.py)

GlueXML generation/patching belongs here.

## wow-race-retroporter/src/raceporter/models.py

[Source](../sources/wow-race-retroporter/src/raceporter/models.py)

Library, test, or historical helper; inspect its source before use.

## wow-race-retroporter/src/raceporter/packaging.py

[Source](../sources/wow-race-retroporter/src/raceporter/packaging.py)

Library, test, or historical helper; inspect its source before use.

## wow-race-retroporter/src/raceporter/pipeline.py

[Source](../sources/wow-race-retroporter/src/raceporter/pipeline.py)

Library, test, or historical helper; inspect its source before use.

## wow-race-retroporter/src/raceporter/retail/__init__.py

[Source](../sources/wow-race-retroporter/src/raceporter/retail/__init__.py)

Retail DB2/model discovery backends belong here.

## wow-race-retroporter/src/raceporter/stages/__init__.py

[Source](../sources/wow-race-retroporter/src/raceporter/stages/__init__.py)

Pipeline stage implementations.

## wow-race-retroporter/src/raceporter/stages/base.py

[Source](../sources/wow-race-retroporter/src/raceporter/stages/base.py)

Library, test, or historical helper; inspect its source before use.

## wow-race-retroporter/src/raceporter/stages/preflight.py

[Source](../sources/wow-race-retroporter/src/raceporter/stages/preflight.py)

Library, test, or historical helper; inspect its source before use.

## wow-race-retroporter/src/raceporter/stages/scaffold.py

[Source](../sources/wow-race-retroporter/src/raceporter/stages/scaffold.py)

Library, test, or historical helper; inspect its source before use.

## wow-race-retroporter/src/raceporter/state.py

[Source](../sources/wow-race-retroporter/src/raceporter/state.py)

Library, test, or historical helper; inspect its source before use.

## wow-race-retroporter/src/raceporter/validation/__init__.py

[Source](../sources/wow-race-retroporter/src/raceporter/validation/__init__.py)

Cross-stage validation rules belong here.

## wow-race-retroporter/tests/conftest.py

[Source](../sources/wow-race-retroporter/tests/conftest.py)

Library, test, or historical helper; inspect its source before use.

## wow-race-retroporter/tests/test_cli.py

[Source](../sources/wow-race-retroporter/tests/test_cli.py)

Library, test, or historical helper; inspect its source before use.

## wow-race-retroporter/tests/test_config.py

[Source](../sources/wow-race-retroporter/tests/test_config.py)

Library, test, or historical helper; inspect its source before use.

## wow-race-retroporter/tests/test_package.py

[Source](../sources/wow-race-retroporter/tests/test_package.py)

Library, test, or historical helper; inspect its source before use.

## wow-race-retroporter/tests/test_pipeline.py

[Source](../sources/wow-race-retroporter/tests/test_pipeline.py)

Library, test, or historical helper; inspect its source before use.

## wow-race-retroporter/tests/test_preflight.py

[Source](../sources/wow-race-retroporter/tests/test_preflight.py)

Library, test, or historical helper; inspect its source before use.

## wow-race-retroporter/tests/test_state.py

[Source](../sources/wow-race-retroporter/tests/test_state.py)

Library, test, or historical helper; inspect its source before use.

