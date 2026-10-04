"""Median-cut palette generation for BLP2 ``compression = 1`` textures.

Palettised BLPs are still the right choice for two things 3.3.5a cares about:
UI art, where DXT ringing is obvious against flat colour, and minimap tiles.
The algorithm is plain median cut with a per-box average representative, which
is what Blizzard's own BLP tooling produced.
"""

from __future__ import annotations

from collections.abc import Sequence


def _box_split_channel(colours: Sequence[tuple[int, int, int]],
                       idx: Sequence[int]) -> tuple[int, int, int]:
    """Return (channel, lo, hi) for the widest channel in this box."""
    lo = [255, 255, 255]
    hi = [0, 0, 0]
    for i in idx:
        c = colours[i]
        for ch in range(3):
            v = c[ch]
            if v < lo[ch]:
                lo[ch] = v
            if v > hi[ch]:
                hi[ch] = v
    # Weight channels the way luminance does, so a wide but perceptually dull
    # channel does not win the split over a narrow, visible one.
    weights = (0.30, 0.59, 0.11)
    best = 0
    best_span = -1.0
    for ch in range(3):
        span = (hi[ch] - lo[ch]) * weights[ch]
        if span > best_span:
            best_span = span
            best = ch
    return best, lo[best], hi[best]


def build_palette(rgba: Sequence[int], max_colours: int = 256) -> list[tuple[int, int, int]]:
    """Median-cut palette over the opaque-ish pixels of an RGBA buffer."""
    # Histogram first: images are hugely repetitive and median cut only needs
    # distinct colours, which collapses a 512x512 texture to a few thousand.
    hist: dict[tuple[int, int, int], int] = {}
    for p in range(0, len(rgba), 4):
        key = (rgba[p], rgba[p + 1], rgba[p + 2])
        hist[key] = hist.get(key, 0) + 1

    colours = list(hist.keys())
    counts = [hist[c] for c in colours]
    if len(colours) <= max_colours:
        return colours + [(0, 0, 0)] * (max_colours - len(colours))

    boxes: list[list[int]] = [list(range(len(colours)))]
    while len(boxes) < max_colours:
        # Split the box with the largest weighted spread; stop when none can.
        target = -1
        target_span = 0.0
        for bi, box in enumerate(boxes):
            if len(box) < 2:
                continue
            _ch, lo, hi = _box_split_channel(colours, box)
            span = (hi - lo) * sum(counts[i] for i in box) ** 0.25
            if span > target_span:
                target_span = span
                target = bi
        if target < 0:
            break
        box = boxes.pop(target)
        ch, _lo, _hi = _box_split_channel(colours, box)
        box.sort(key=lambda i: colours[i][ch])
        # Split at the weighted median so both halves carry similar pixel mass.
        total = sum(counts[i] for i in box)
        acc = 0
        cut = 1
        for n, i in enumerate(box):
            acc += counts[i]
            if acc * 2 >= total:
                cut = max(1, min(n + 1, len(box) - 1))
                break
        boxes.append(box[:cut])
        boxes.append(box[cut:])

    palette: list[tuple[int, int, int]] = []
    for box in boxes:
        wsum = 0
        acc = [0, 0, 0]
        for i in box:
            w = counts[i]
            wsum += w
            c = colours[i]
            acc[0] += c[0] * w
            acc[1] += c[1] * w
            acc[2] += c[2] * w
        if wsum:
            palette.append((acc[0] // wsum, acc[1] // wsum, acc[2] // wsum))
    while len(palette) < max_colours:
        palette.append((0, 0, 0))
    return palette[:max_colours]


class PaletteMapper:
    """Nearest-colour lookup with a coarse 5-5-5 cache.

    Exact nearest-neighbour over 256 entries for every pixel is the single
    slowest thing in the whole converter; caching by quantised colour cuts the
    work by two orders of magnitude with no visible difference.
    """

    __slots__ = ("_cache", "palette")

    def __init__(self, palette: Sequence[tuple[int, int, int]]):
        self.palette = list(palette)
        self._cache: dict[int, int] = {}

    def index_of(self, r: int, g: int, b: int) -> int:
        key = ((r >> 3) << 10) | ((g >> 3) << 5) | (b >> 3)
        hit = self._cache.get(key)
        if hit is not None:
            return hit
        best = 0
        best_d = 1 << 30
        for i, (pr, pg, pb) in enumerate(self.palette):
            dr = r - pr
            dg = g - pg
            db = b - pb
            d = dr * dr * 3 + dg * dg * 6 + db * db
            if d < best_d:
                best_d = d
                best = i
                if d == 0:
                    break
        self._cache[key] = best
        return best

    def map_image(self, rgba: Sequence[int]) -> bytearray:
        out = bytearray(len(rgba) // 4)
        index_of = self.index_of
        for n, p in enumerate(range(0, len(rgba), 4)):
            out[n] = index_of(rgba[p], rgba[p + 1], rgba[p + 2])
        return out
