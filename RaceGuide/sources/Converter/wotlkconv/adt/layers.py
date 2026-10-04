"""Texture layers of a map chunk, cut down to what 3.3.5a can draw.

A chunk paints its ground with a base texture and up to three more, each
blended over the ones below through its own 64x64 alpha map.  3.3.5a keeps
exactly four layer slots; Cataclysm and later allow eight (retail Azeroth has
more than four on 15,000 chunks), and an old reader walks off the end of its
array.

When a chunk has too many, the upper layers that show least are dropped.  How
much a layer shows is its alpha at each point times how much of it the layers
above leave uncovered, summed over the chunk (sampled every fourth texel,
which is plenty to rank four to eight layers).  The kept layers' alpha maps
are carried over byte for byte and re-indexed into a rebuilt ``MCAL``.

A layer whose texture has no file behind it (retail tiles occasionally name
FileDataID 0) is dropped too.  If that is the base, the lowest layer that does
have a texture becomes the base and loses its alpha map, since a base covers
everything.
"""

from __future__ import annotations

import dataclasses
import struct

MAX_LAYERS = 4
LAYER_SIZE = 16
FLAG_USE_ALPHA = 0x100
FLAG_COMPRESSED = 0x200
ALPHA_VALUES = 64 * 64
#: Every fourth texel in each direction.
_SAMPLES = [y * 64 + x for y in range(0, 64, 4) for x in range(0, 64, 4)]


def read_alpha(mcal: bytes, offset: int, flags: int, big: bool
               ) -> tuple[bytes, bytes] | None:
    """(the layer's encoded bytes, its 4096 decoded values), or None if the
    map runs past the end of ``MCAL``."""
    if flags & FLAG_COMPRESSED:
        values = bytearray()
        pos = offset
        while len(values) < ALPHA_VALUES:
            if pos >= len(mcal):
                return None
            control = mcal[pos]
            pos += 1
            count = control & 0x7F
            if control & 0x80:
                if pos >= len(mcal):
                    return None
                values += bytes((mcal[pos],)) * count
                pos += 1
            else:
                values += mcal[pos:pos + count]
                pos += count
        return bytes(mcal[offset:pos]), bytes(values[:ALPHA_VALUES])
    size = ALPHA_VALUES if big else ALPHA_VALUES // 2
    if offset + size > len(mcal):
        return None
    raw = bytes(mcal[offset:offset + size])
    if big:
        return raw, raw
    values = bytes(((raw[i // 2] >> (4 if i & 1 else 0)) & 0xF) * 17
                   for i in range(ALPHA_VALUES))
    return raw, values


@dataclasses.dataclass(slots=True)
class LimitedLayers:
    mcly: bytes
    mcal: bytes
    #: The source index of each layer written, in order.
    kept: list[int] = dataclasses.field(default_factory=list)
    #: For each of the 64 cells of the chunk's 8x8 grid, the written layer
    #: that shows most there.
    most_visible: list[int] = dataclasses.field(default_factory=list)
    #: Layers dropped because their texture has no file.
    untextured: int = 0
    #: Layers dropped to fit four.
    over_limit: int = 0
    #: Layers dropped because their alpha map runs past the end of MCAL.
    unreadable: int = 0


def limit_layers(mcly: bytes, mcal: bytes, untextured: set[int], big: bool
                 ) -> LimitedLayers | None:
    """Rebuild ``MCLY`` and ``MCAL`` with at most four textured layers.

    ``untextured`` holds the MTEX indices with no file behind them.  Returns
    None when the chunk needs no change.
    """
    count = len(mcly) // LAYER_SIZE
    layers = [list(struct.unpack_from("<IIIi", mcly, i * LAYER_SIZE))
              for i in range(count)]
    keep = [i for i, layer in enumerate(layers) if layer[0] not in untextured]
    if count <= MAX_LAYERS and len(keep) == count:
        return None
    result = LimitedLayers(b"", b"", untextured=count - len(keep))

    alphas: dict[int, tuple[bytes, bytes] | None] = {}
    for i in list(keep[1:]):
        flags = layers[i][1]
        if not flags & FLAG_USE_ALPHA:
            alphas[i] = None
            continue
        alphas[i] = read_alpha(mcal, layers[i][2], flags, big)
        if alphas[i] is None:
            # Stripping the alpha would paint the layer over everything below.
            keep.remove(i)
            result.unreadable += 1

    while len(keep) > MAX_LAYERS:
        weights = {}
        for position, i in enumerate(keep[1:], start=1):
            above = [alphas.get(j) for j in keep[position + 1:]]
            own = alphas.get(i)
            weight = 0.0
            for s in _SAMPLES:
                shown = own[1][s] / 255.0 if own else 1.0
                for other in above:
                    shown *= 1.0 - (other[1][s] / 255.0 if other else 1.0)
                weight += shown
            weights[i] = weight
        keep.remove(min(weights, key=lambda i: (weights[i], -i)))
        result.over_limit += 1

    result.kept = list(keep)
    result.most_visible = _most_visible(keep, alphas)

    out_mcly = bytearray()
    out_mcal = bytearray()
    for position, i in enumerate(keep):
        texture, flags, _offset, effect = layers[i]
        alpha = alphas.get(i)
        if position == 0 or alpha is None:
            flags &= ~(FLAG_USE_ALPHA | FLAG_COMPRESSED)
            offset = 0
        else:
            offset = len(out_mcal)
            out_mcal += alpha[0]
        out_mcly += struct.pack("<IIIi", texture, flags, offset, effect)
    result.mcly, result.mcal = bytes(out_mcly), bytes(out_mcal)
    return result


def _most_visible(keep: list[int], alphas: dict[int, tuple[bytes, bytes] | None]
                  ) -> list[int]:
    """Per cell of the 8x8 grid, the position in ``keep`` of the layer that
    shows most, the same way the layers were ranked (four texels a cell)."""
    out = []
    for cy in range(8):
        for cx in range(8):
            texels = [(cy * 8 + dy) * 64 + cx * 8 + dx
                      for dy in (2, 6) for dx in (2, 6)]
            best, best_weight = 0, -1.0
            for position, i in enumerate(keep):
                above = [alphas.get(j) for j in keep[position + 1:]]
                own = alphas.get(i) if position else None
                weight = 0.0
                for t in texels:
                    shown = own[1][t] / 255.0 if own else 1.0
                    for other in above:
                        shown *= 1.0 - (other[1][t] / 255.0 if other else 1.0)
                    weight += shown
                if weight > best_weight:
                    best, best_weight = position, weight
            out.append(best)
    return out


def remap_predominant(texture_map: bytes, limited: LimitedLayers) -> bytes:
    """Re-index a map chunk's 8x8 low-quality texture map (2 bits a cell,
    header offset 0x40) to the layers that were kept.

    A cell keeps its layer when that layer survived, at its new position; a
    cell whose layer was dropped takes the kept layer that shows most there.
    The map picks which layer's ground-effect doodads grow in the cell and
    what distant terrain draws, so an index left pointing at a dropped slot
    grows another texture's clutter.
    """
    position = {source: new for new, source in enumerate(limited.kept)}
    out = bytearray(16)
    for cell in range(64):
        old = (texture_map[cell // 4] >> (cell % 4 * 2)) & 0x3
        new = position.get(old)
        if new is None:
            new = limited.most_visible[cell] if limited.most_visible else 0
        out[cell // 4] |= (new & 0x3) << (cell % 4 * 2)
    return bytes(out)
