"""A tiny RGBA image buffer with the resampling the BLP pipeline needs.

Deliberately not Pillow: the converter must work on a bare Python install, and
the only operations required are box-downscale, bilinear upscale and mip chain
generation.
"""

from __future__ import annotations

import dataclasses


def next_pot(v: int) -> int:
    """Smallest power of two >= ``v``."""
    if v <= 1:
        return 1
    return 1 << (v - 1).bit_length()


def prev_pot(v: int) -> int:
    """Largest power of two <= ``v``."""
    if v <= 1:
        return 1
    return 1 << (v.bit_length() - 1)


def nearest_pot(v: int) -> int:
    """Whichever power of two is closest, preferring the smaller on a tie."""
    lo = prev_pot(v)
    hi = next_pot(v)
    return lo if (v - lo) <= (hi - v) else hi


def is_pot(v: int) -> bool:
    return v > 0 and (v & (v - 1)) == 0


@dataclasses.dataclass(slots=True)
class Image:
    """Straight (non-premultiplied) 8-bit RGBA."""

    width: int
    height: int
    data: bytearray

    @classmethod
    def new(cls, width: int, height: int, fill: tuple[int, int, int, int] = (0, 0, 0, 0)) -> Image:
        return cls(width, height, bytearray(bytes(fill) * (width * height)))

    @classmethod
    def from_rgba(cls, width: int, height: int, data: bytes | bytearray) -> Image:
        expected = width * height * 4
        buf = bytearray(data)
        if len(buf) < expected:
            buf += bytes(expected - len(buf))
        elif len(buf) > expected:
            del buf[expected:]
        return cls(width, height, buf)

    # -- inspection -----------------------------------------------------
    @property
    def pixels(self) -> int:
        return self.width * self.height

    def alpha_stats(self) -> tuple[int, int, bool]:
        """Return (min alpha, max alpha, whether alpha is only 0 or 255)."""
        alphas = self.data[3::4]
        lo = min(alphas) if alphas else 255
        hi = max(alphas) if alphas else 255
        binary = all(a == 0 or a == 255 for a in alphas)
        return lo, hi, binary

    def is_opaque(self) -> bool:
        return min(self.data[3::4], default=255) == 255

    def copy(self) -> Image:
        return Image(self.width, self.height, bytearray(self.data))

    def to_bgra(self) -> bytearray:
        out = bytearray(self.data)
        out[0::4], out[2::4] = self.data[2::4], self.data[0::4]
        return out

    @classmethod
    def from_bgra(cls, width: int, height: int, data: bytes | bytearray) -> Image:
        img = cls.from_rgba(width, height, data)
        src = bytes(img.data)
        img.data[0::4], img.data[2::4] = src[2::4], src[0::4]
        return img

    # -- resampling -----------------------------------------------------
    def halve(self) -> Image:
        """2x2 box filter, the standard mip reduction.

        Degenerate levels (1xN or Nx1) only average along the axis that is
        actually shrinking, which is what the client's own mip chains do.
        """
        w, h = self.width, self.height
        nw = max(1, w // 2)
        nh = max(1, h // 2)
        src = self.data
        dst = bytearray(nw * nh * 4)
        sstride = w * 4
        wide = w > 1
        tall = h > 1
        x_step = 2 if wide else 1
        y_step = 2 if tall else 1
        di = 0
        for y in range(nh):
            row0 = (y * y_step) * sstride
            row1 = row0 + sstride if tall else row0
            for x in range(nw):
                sx = (x * x_step) * 4
                p0 = row0 + sx
                taps = [p0]
                if wide:
                    taps.append(p0 + 4)
                if tall:
                    taps.append(row1 + sx)
                    if wide:
                        taps.append(row1 + sx + 4)
                n = len(taps)
                half = n // 2
                for c in range(4):
                    total = 0
                    for p in taps:
                        total += src[p + c]
                    dst[di + c] = (total + half) // n
                di += 4
        return Image(nw, nh, dst)

    def resize(self, width: int, height: int) -> Image:
        """Area-average when shrinking, bilinear when growing."""
        if width == self.width and height == self.height:
            return self.copy()
        if width <= self.width and height <= self.height:
            return self._resize_box(width, height)
        return self._resize_bilinear(width, height)

    def _resize_box(self, nw: int, nh: int) -> Image:
        w, h = self.width, self.height
        src = self.data
        dst = bytearray(nw * nh * 4)
        sstride = w * 4
        # Precompute source spans so the inner loop stays arithmetic-free.
        x_spans = [(x * w // nw, max(x * w // nw + 1, (x + 1) * w // nw)) for x in range(nw)]
        di = 0
        for y in range(nh):
            y0 = y * h // nh
            y1 = max(y0 + 1, (y + 1) * h // nh)
            for x in range(nw):
                x0, x1 = x_spans[x]
                tr = tg = tb = ta = 0
                count = 0
                for sy in range(y0, y1):
                    base = sy * sstride
                    for sx in range(x0, x1):
                        p = base + sx * 4
                        tr += src[p]
                        tg += src[p + 1]
                        tb += src[p + 2]
                        ta += src[p + 3]
                        count += 1
                half = count // 2
                dst[di] = (tr + half) // count
                dst[di + 1] = (tg + half) // count
                dst[di + 2] = (tb + half) // count
                dst[di + 3] = (ta + half) // count
                di += 4
        return Image(nw, nh, dst)

    def _resize_bilinear(self, nw: int, nh: int) -> Image:
        w, h = self.width, self.height
        src = self.data
        dst = bytearray(nw * nh * 4)
        sstride = w * 4
        x_map = []
        for x in range(nw):
            fx = ((x + 0.5) * w / nw) - 0.5
            x0 = int(fx) if fx >= 0 else -1
            frac = fx - x0
            x0c = min(max(x0, 0), w - 1)
            x1c = min(max(x0 + 1, 0), w - 1)
            x_map.append((x0c * 4, x1c * 4, frac))
        di = 0
        for y in range(nh):
            fy = ((y + 0.5) * h / nh) - 0.5
            y0 = int(fy) if fy >= 0 else -1
            fry = fy - y0
            r0 = min(max(y0, 0), h - 1) * sstride
            r1 = min(max(y0 + 1, 0), h - 1) * sstride
            for x0, x1, frx in x_map:
                for c in range(4):
                    a = src[r0 + x0 + c]
                    b = src[r0 + x1 + c]
                    cc = src[r1 + x0 + c]
                    d = src[r1 + x1 + c]
                    top = a + (b - a) * frx
                    bot = cc + (d - cc) * frx
                    dst[di + c] = int(top + (bot - top) * fry + 0.5)
                di += 4
        return Image(nw, nh, dst)

    def mip_chain(self, levels: int | None = None) -> list[Image]:
        """Full mip chain starting with this image, down to 1x1."""
        chain = [self]
        cur = self
        while cur.width > 1 or cur.height > 1:
            if levels is not None and len(chain) >= levels:
                break
            cur = cur.halve()
            chain.append(cur)
        return chain
