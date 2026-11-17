import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

blob = Path(r"g:\risServer\Esteria - Client\Data\Retail\Cache\Retail\wow-88d5e8ef05ec5a8446cdec93d142d7c6\decoded\2\strict\id-939606.bin").read_bytes()
start = blob.find(b"BLP2")
header = blob[start:]
width, height = struct.unpack_from("<II", header, 12)
offset = struct.unpack_from("<I", header, 20)[0]
blocks = np.frombuffer(blob[start + offset:], dtype=np.uint8)
blocks = blocks[: (width // 4) * (height // 4) * 16].reshape((-1, 16))

def rgb565(v):
    return np.stack((((v >> 11) & 31) * 255 // 31, ((v >> 5) & 63) * 255 // 63, (v & 31) * 255 // 31), axis=-1).astype(np.uint8)

c0 = blocks[:, 8].astype(np.uint16) | (blocks[:, 9].astype(np.uint16) << 8)
c1 = blocks[:, 10].astype(np.uint16) | (blocks[:, 11].astype(np.uint16) << 8)
pal = np.zeros((len(blocks), 4, 3), np.uint8)
pal[:, 0] = rgb565(c0)
pal[:, 1] = rgb565(c1)
pal[:, 2] = ((2 * pal[:, 0].astype(np.uint16) + pal[:, 1]) // 3).astype(np.uint8)
pal[:, 3] = ((pal[:, 0].astype(np.uint16) + 2 * pal[:, 1]) // 3).astype(np.uint8)
idx = np.zeros((len(blocks), 16), np.uint8)
bits = blocks[:, 12:16].astype(np.uint32)
packed = bits[:, 0] | (bits[:, 1] << 8) | (bits[:, 2] << 16) | (bits[:, 3] << 24)
for i in range(16):
    idx[:, i] = (packed >> (2 * i)) & 3
colors = pal[np.arange(len(blocks))[:, None], idx]
a0 = blocks[:, 0].astype(np.int16)
a1 = blocks[:, 1].astype(np.int16)
abits = np.zeros(len(blocks), np.uint64)
for i, shift in enumerate(range(0, 48, 8)):
    abits |= blocks[:, 2 + i].astype(np.uint64) << shift
alpha = np.zeros((len(blocks), 16), np.uint8)
for i in range(16):
    ai = (abits >> (3 * i)) & 7
    alpha[:, i] = np.where(a0 > a1,
        np.where(ai == 0, a0, np.where(ai == 1, a1, ((8 - ai) * a0 + (ai - 1) * a1) // 7)),
        np.where(ai == 0, a0, np.where(ai == 1, a1, np.where(ai == 6, 0, np.where(ai == 7, 255, ((6 - ai) * a0 + (ai - 1) * a1) // 5)))))
pixels = np.concatenate([colors, alpha[:, :, None]], axis=-1)
pixels = pixels.reshape((height // 4, width // 4, 4, 4, 4)).transpose(0, 2, 1, 3, 4).reshape(height, width, 4)
alpha = pixels[:, :, 3]
ys, xs = np.where(alpha > 16)
print("content bounds", xs.min(), ys.min(), xs.max(), ys.max(), "size", xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)
image = Image.fromarray(pixels[:468, :672], "RGBA").convert("RGB")
draw = ImageDraw.Draw(image)
marks = {
    "town": (0.35846060514, 0.63082647324),
    "small": (0.64096653461, 0.60330045223),
    "large": (0.49493408203, 0.32783597708),
}
colors = {"town": (255, 40, 40), "small": (40, 220, 255), "large": (255, 220, 40)}
for name, (nx, ny) in marks.items():
    x = int(nx * 672)
    y = int(ny * 468)
    draw.ellipse((x - 8, y - 8, x + 8, y + 8), outline=colors[name], width=3)
    print(name, "flipped px", x, y)
base = Path(r"g:\risServer\EsteriaWoW\modules\mod-esteria-garrison\tools")
image.save(base / "map_pins_preview.png")
for name, (nx, ny) in marks.items():
    x = int(nx * 672)
    y = int(ny * 468)
    image.crop((max(0, x - 70), max(0, y - 70), x + 70, y + 70)).save(base / f"pin_{name}.png")
image.crop((220, 160, 460, 340)).save(base / "yard.png")
