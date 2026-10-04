"""Draw exact installed Tuskarr triangles for a bounded geometry audit."""

import math
from pathlib import Path
import struct
import sys

from PIL import Image, ImageDraw
from wotlkconv.m2 import parse_m2, parse_skin

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
import creature_race_pack as c

KEY = r'custom\tuskarr\native\male\tuskarrmale.m2'
with c.p.ClientFiles(str(c.p.CLIENT_DEFAULT / 'Data'), 'enUS') as files:
    model = parse_m2(files.find(KEY)[0])
    skin = parse_skin(files.find(KEY[:-3] + '00.skin')[0])

def surfaces(model, skin):
    result = {}
    for mesh in skin.submeshes:
        geoset, level, _, _, start, count = struct.unpack_from('<6H', mesh)
        start |= level << 16
        result.setdefault(geoset, []).extend([
            [struct.unpack_from('<3f', model.vertices, skin.vertices[i] * 48)
             for i in skin.indices[at:at + 3]]
            for at in range(start, start + count, 3)])
    return result


legacy = surfaces(model, skin)
stage = c.WORK / 'tuskarr/integration/equipment-repair'
updated = surfaces(parse_m2((stage / 'Tuskarr.m2').read_bytes()), parse_skin((stage / 'Tuskarr00.skin').read_bytes()))

image = Image.new('RGB', (1500, 1050), 'white')
draw = ImageDraw.Draw(image)
for column, (data, geosets, label) in enumerate((
        (legacy, (10000, 501), 'Installed feet / calves'),
        (updated, (10000, 501), 'Rounded feet / calves'),
        (updated, (10000, 1302), 'Rounded feet / robe calf fallback'))):
    triangles = [(triangle, (142, 158, 171) if i == 0 else (213, 163, 66))
                 for i, geoset in enumerate(geosets) for triangle in data[geoset]]
    for row, (azimuth, elevation) in enumerate(((0.0, 0.15), (math.pi / 2, 0.05))):
        left, top = column * 500, row * 525
        draw.text((left + 15, top + 10), f'{label}; view {row}', fill='black')
        records = []
        for points, color in triangles:
            if max(p[2] for p in points) > 0.95:
                continue
            projected = []
            depths = []
            for x, y, z in points:
                depth = x * math.cos(azimuth) + y * math.sin(azimuth)
                horizontal = y * math.cos(azimuth) - x * math.sin(azimuth)
                vertical = z * math.cos(elevation) - depth * math.sin(elevation)
                projected.append((left + 250 + horizontal * 360, top + 455 - vertical * 430))
                depths.append(depth)
            records.append((sum(depths), projected, color))
        for _, points, color in sorted(records):
            draw.polygon(points, fill=color, outline=(75, 83, 92))
image.save(Path(__file__).with_name('feet-repair.png'))
print(Path(__file__).with_name('feet-repair.png'))
