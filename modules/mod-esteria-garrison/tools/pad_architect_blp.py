# 3.3.5 draws only power-of-two textures. Anything else is the green stand-in.
# Retail files are padded the same way in CascSource::PadBlpToPowerOfTwo; these crops were not.
import re
import struct
from pathlib import Path

ART = Path(r"g:\risServer\Esteria - Client\Interface\AddOns\Blizzard_GarrisonUI\Art")
XML = Path(r"g:\risServer\Esteria - Client\Interface\AddOns\EsteriaGarrison\Retail\Blizzard_GarrisonBuildingUI.xml")
ATLAS = Path(r"g:\risServer\Esteria - Client\Interface\AddOns\EsteriaGarrison\Retail\Atlas.lua")
BLOCK = 16
DATA = 148 + 1024


def pot(value):
    power = 1
    while power < value:
        power <<= 1
    return power


def load(path):
    data = path.read_bytes()
    if data[:4] != b"BLP2" or data[8] != 2:
        return None
    width, height = struct.unpack_from("<II", data, 12)
    offset, size = struct.unpack_from("<I", data, 20)[0], struct.unpack_from("<I", data, 84)[0]
    if width % 4 or height % 4 or offset + size > len(data):
        return None
    rows = height // 4
    row = (width // 4) * BLOCK
    body = data[offset:offset + row * rows]
    return width, height, [body[y * row:(y + 1) * row] for y in range(rows)]


def save(path, width, height, rows, pref):
    out_row = (width // 4) * BLOCK
    blob = bytearray(DATA + out_row * (height // 4))
    blob[0:4] = b"BLP2"
    struct.pack_into("<I", blob, 4, 1)
    blob[8], blob[9], blob[10], blob[11] = 2, 8, pref, 0
    struct.pack_into("<II", blob, 12, width, height)
    struct.pack_into("<I", blob, 20, DATA)
    struct.pack_into("<I", blob, 84, out_row * (height // 4))
    for y, row in enumerate(rows):
        blob[DATA + y * out_row:DATA + y * out_row + len(row)] = row
    path.write_bytes(blob)


def scale_rows(rows, src_w, dst_w, dst_rows):
    src_blocks = src_w // 4
    dst_blocks = dst_w // 4
    src_rows = len(rows)
    out = []
    for y in range(dst_rows):
        src_y = min(src_rows - 1, y * src_rows // dst_rows)
        row = rows[src_y]
        if src_blocks == dst_blocks:
            out.append(row)
            continue
        built = bytearray(dst_blocks * BLOCK)
        for x in range(dst_blocks):
            src_x = min(src_blocks - 1, x * src_blocks // dst_blocks)
            built[x * BLOCK:(x + 1) * BLOCK] = row[src_x * BLOCK:(src_x + 1) * BLOCK]
        out.append(built)
    return out


xml = XML.read_text(encoding="utf-8")
atlas = ATLAS.read_text(encoding="utf-8")
tiled = set()
for match in re.finditer(r"<Texture\b([^>]*)>", xml):
    tag = match.group(1)
    file_match = re.search(r'file="[^"]*\\([^"\\]+\.blp)"', tag)
    if file_match and ("horizTile" in tag or "vertTile" in tag):
        tiled.add(file_match.group(1))

padded = 0
for path in sorted(ART.glob("*.blp")):
    loaded = load(path)
    if not loaded:
        continue
    width, height, rows = loaded
    dst_w, dst_h = pot(width), pot(height)
    if (dst_w, dst_h) == (width, height) and struct.unpack_from("<I", path.read_bytes(), 20)[0] == DATA:
        continue
    if path.name in tiled:
        rows = scale_rows(rows, width, dst_w, dst_h // 4)
        content_w, content_h = dst_w, dst_h
    else:
        blank = bytearray((dst_w // 4) * BLOCK)
        grown = []
        for row in rows:
            grown.append(row + blank[len(row):])
        grown.extend([blank] * ((dst_h // 4) - len(rows)))
        rows = grown
        content_w, content_h = width, height
    save(path, dst_w, dst_h, rows, 7)
    padded += 1
    if path.name not in tiled:
        fraction_u = "%0.6f" % (width / dst_w)
        fraction_v = "%0.6f" % (height / dst_h)

        def retarget(match, fu=fraction_u, fv=fraction_v, name=path.name):
            element = match.group(0)
            if name not in element or "horizTile" in element or "vertTile" in element:
                return element

            def axis(value, fraction):
                number = float(value)
                if number >= 0.999:
                    return fraction
                if number <= 0.001:
                    return "0"
                return "%0.6f" % (number * float(fraction))

            if "<TexCoords" in element:
                def coords(found):
                    attrs = found.group(1)
                    for side, fraction in (("left", fu), ("right", fu), ("top", fv), ("bottom", fv)):
                        attrs = re.sub(
                            side + r'="([0-9.]+)"',
                            lambda m, side=side, fraction=fraction: '%s="%s"' % (side, axis(m.group(1), fraction)),
                            attrs, count=1)
                    return "<TexCoords" + attrs + "/>"
                return re.sub(r"<TexCoords([^>]*)/>", coords, element, count=1)
            insert = '<TexCoords left="0" right="%s" top="0" bottom="%s"/>' % (fu, fv)
            return element.replace("</Texture>", insert + "</Texture>", 1)

        xml = re.sub(
            r"<(Texture|NormalTexture|HighlightTexture|PushedTexture|DisabledTexture)\b.*?</\1>",
            retarget, xml, flags=re.S)
    atlas = re.sub(
        re.escape(path.name) + r'",(\d+),(\d+)(?:,\d+,\d+)?',
        '%s",%d,%d,%d,%d' % (path.name, content_w, content_h, dst_w, dst_h),
        atlas)

XML.write_text(xml, encoding="utf-8")
ATLAS.write_text(atlas, encoding="utf-8")
print("padded", padded, "tiled", len(tiled))
