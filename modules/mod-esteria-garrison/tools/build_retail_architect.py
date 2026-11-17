# Builds the retail architect window (Blizzard_GarrisonBuildingUI) for the 3.3.5 client.
# Atlas pieces are cropped from the retail UiTextureAtlas sheets. The frame XML is Blizzard's.
import csv, re, struct
from pathlib import Path

ROOT = Path(r"g:\risServer")
DB2 = ROOT / "_ref" / "retail_ui" / "dbfilesclient"
REF = ROOT / "_ref" / "retail_ui"
OUT = ROOT / "Esteria - Client" / "Interface" / "AddOns" / "Blizzard_GarrisonUI"
ART = OUT / "Art"
BUILDING_XML = ROOT / "_ref" / "retail_ui" / "interface" / "addons" / "blizzard_garrisonui" / "mainline" / "blizzard_garrisonbuildingui.xml"
BUILDING_LUA = ROOT / "_ref" / "retail_ui" / "interface" / "addons" / "blizzard_garrisonui" / "mainline" / "blizzard_garrisonbuildingui.lua"
SHARED_XML = ROOT / "_ref" / "retail_ui" / "interface" / "addons" / "blizzard_garrisontemplates" / "blizzard_garrisonsharedtemplates.xml"


def u32(b, p):
    return struct.unpack_from("<I", b, p)[0]


def strings(data, start, size):
    end = start + size
    p = start
    while p < end and data[p] == 0:
        p += 1
    out = []
    while p < end:
        z = data.find(b"\x00", p)
        if z < 0 or z >= end:
            break
        if z > p:
            out.append(data[p:z].decode("utf-8", "replace"))
        p = z + 1
    return out


def header(data):
    o = 136
    rec, fc, rs, ss = struct.unpack_from("<4I", data, o)
    o = 136 + 36 + 4
    total, bitpacked, lookup, fsis, common, pallet, sections = struct.unpack_from("<7I", data, o)
    o += 28
    sh = []
    for _ in range(sections):
        tact, foff, nrec, strsz, ore, idsz, relsz, offmap, copyc = struct.unpack_from("<Q8I", data, o)
        sh.append((foff, nrec, strsz))
        o += 40
    return sh


def load_atlases():
    el = (DB2 / "uitextureatlaselement.db2").read_bytes()
    sh = header(el)
    enames = strings(el, sh[0][0] + sh[0][1] * 8, sh[0][2])
    id_to_name = {}
    for i, name in enumerate(enames):
        _off, eid = struct.unpack_from("<II", el, sh[0][0] + i * 8)
        id_to_name[eid] = name

    mem = (DB2 / "uitextureatlasmember.db2").read_bytes()
    mh = header(mem)
    members = {}
    base = mh[0][0]
    for i in range(mh[0][1]):
        raw = mem[base + i * 32:base + i * 32 + 30]
        _name, mid, atlas, w, h, left, right, top, bottom, elem, ow, oh, flags, canvas = struct.unpack("<II10HBB", raw)
        name = id_to_name.get(elem)
        if not name:
            continue
        width = ow or w or max(0, right - left)
        height = oh or h or max(0, bottom - top)
        members[name] = (atlas, left, right, top, bottom, width, height)

    atlas = (DB2 / "uitextureatlas.db2").read_bytes()
    ah = header(atlas)
    sheets = {}
    base = ah[0][0]
    for i in range(ah[0][1]):
        eid, fdid, w, h, _canvas = struct.unpack_from("<IIHHB", atlas, base + i * 16)
        sheets[eid] = (fdid, w, h)
    return members, sheets


def dxt5(data, width, height):
    bw, bh = (width + 3) // 4, (height + 3) // 4
    rgba = bytearray(width * height * 4)

    def rgb565(v):
        return (((v >> 11) & 31) * 255 // 31, ((v >> 5) & 63) * 255 // 63, (v & 31) * 255 // 31)

    for by in range(bh):
        for bx in range(bw):
            block = data[(by * bw + bx) * 16:(by * bw + bx) * 16 + 16]
            a0, a1 = block[0], block[1]
            pal = [a0, a1]
            if a0 > a1:
                for i in range(1, 7):
                    pal.append(((7 - i) * a0 + i * a1) // 7)
            else:
                for i in range(1, 5):
                    pal.append(((5 - i) * a0 + i * a1) // 5)
                pal.extend((0, 255))
            bits = 0
            for i in range(6):
                bits |= block[2 + i] << (8 * i)
            alpha = [pal[(bits >> (3 * i)) & 7] for i in range(16)]
            c0 = block[8] | (block[9] << 8)
            c1 = block[10] | (block[11] << 8)
            col = [rgb565(c0), rgb565(c1)]
            if c0 > c1:
                col.append(tuple((2 * col[0][i] + col[1][i]) // 3 for i in range(3)))
                col.append(tuple((col[0][i] + 2 * col[1][i]) // 3 for i in range(3)))
            else:
                col.append(tuple((col[0][i] + col[1][i]) // 2 for i in range(3)))
                col.append((0, 0, 0))
            cb = block[12] | (block[13] << 8) | (block[14] << 16) | (block[15] << 24)
            for i in range(16):
                x, y = bx * 4 + i % 4, by * 4 + i // 4
                if x >= width or y >= height:
                    continue
                r, g, b = col[(cb >> (2 * i)) & 3]
                o = (y * width + x) * 4
                rgba[o:o + 4] = bytes((r, g, b, alpha[i]))
    return rgba


def blp_header(path):
    data = path.read_bytes()
    if data[:4] != b"BLP2":
        return None
    return data, data[8], data[10], u32(data, 12), u32(data, 16), u32(data, 20), u32(data, 84)


def load_sheet(path):
    opened = blp_header(path)
    if not opened:
        return None
    data, encoding, alpha, width, height, offset, size = opened
    if encoding != 2 or alpha != 7:
        return None
    return width, height, dxt5(data[offset:offset + size], width, height)


def write_blp(path, width, height, rgba):
    # DXT5. The running client draws raw BGRA (encoding 3) as the green fallback.
    import numpy as np
    pad_w, pad_h = (width + 3) & ~3, (height + 3) & ~3
    src = np.frombuffer(bytes(rgba), dtype=np.uint8).reshape(height, width, 4)
    image = np.zeros((pad_h, pad_w, 4), np.uint8)
    image[:height, :width] = src
    if pad_w > width:
        image[:, width:] = image[:, width - 1:width]
    if pad_h > height:
        image[height:, :] = image[height - 1:height, :]
    bh, bw = pad_h // 4, pad_w // 4
    blocks = image.reshape(bh, 4, bw, 4, 4).swapaxes(1, 2)
    rgb = blocks[..., :3].astype(np.int16).reshape(bh, bw, 16, 3)
    alpha = blocks[..., 3].astype(np.int16).reshape(bh, bw, 16)
    a0, a1 = alpha.max(axis=2), alpha.min(axis=2)
    coef0 = np.array([7, 0, 6, 5, 4, 3, 2, 1], np.int16)
    coef1 = np.array([0, 7, 1, 2, 3, 4, 5, 6], np.int16)
    pal_a = (coef0 * a0[..., None] + coef1 * a1[..., None]) // 7
    aindex = np.abs(alpha[..., None] - pal_a[:, :, None, :]).argmin(axis=3).astype(np.uint64)
    aindex[a0 == a1] = 0
    abits = (aindex << (3 * np.arange(16, dtype=np.uint64))).sum(axis=2)
    lum = rgb.sum(axis=-1)
    bright = rgb[np.arange(bh)[:, None], np.arange(bw)[None, :], lum.argmax(axis=2)]
    dark = rgb[np.arange(bh)[:, None], np.arange(bw)[None, :], lum.argmin(axis=2)]
    e0 = (((bright[..., 0] >> 3) << 11) | ((bright[..., 1] >> 2) << 5) | (bright[..., 2] >> 3)).astype(np.int32)
    e1 = (((dark[..., 0] >> 3) << 11) | ((dark[..., 1] >> 2) << 5) | (dark[..., 2] >> 3)).astype(np.int32)
    swap = e0 < e1
    e0, e1 = np.where(swap, e1, e0), np.where(swap, e0, e1)
    e0 = np.where((e0 == e1) & (e0 < 65535), e0 + 1, e0)

    def from565(v):
        return np.stack((((v >> 11) & 31) * 255 // 31, ((v >> 5) & 63) * 255 // 63, (v & 31) * 255 // 31), axis=-1).astype(np.int16)

    p0, p1 = from565(e0), from565(e1)
    pal_c = np.stack((p0, p1, (2 * p0 + p1) // 3, (p0 + 2 * p1) // 3), axis=2)
    cindex = ((rgb[:, :, :, None, :] - pal_c[:, :, None, :, :]) ** 2).sum(axis=-1).argmin(axis=3).astype(np.uint32)
    cbits = (cindex << (2 * np.arange(16, dtype=np.uint32))).sum(axis=2)
    packed = np.zeros((bh, bw, 16), np.uint8)
    packed[..., 0] = a0.astype(np.uint8)
    packed[..., 1] = a1.astype(np.uint8)
    for shift in range(6):
        packed[..., 2 + shift] = ((abits >> (8 * shift)) & 255).astype(np.uint8)
    packed[..., 8] = (e0 & 255).astype(np.uint8)
    packed[..., 9] = ((e0 >> 8) & 255).astype(np.uint8)
    packed[..., 10] = (e1 & 255).astype(np.uint8)
    packed[..., 11] = ((e1 >> 8) & 255).astype(np.uint8)
    for shift in range(4):
        packed[..., 12 + shift] = ((cbits >> (8 * shift)) & 255).astype(np.uint8)
    payload = packed.reshape(-1).tobytes()
    hdr = bytearray(148)
    hdr[0:4] = b"BLP2"
    struct.pack_into("<I", hdr, 4, 1)
    hdr[8], hdr[9], hdr[10], hdr[11] = 2, 8, 7, 0
    struct.pack_into("<II", hdr, 12, pad_w, pad_h)
    struct.pack_into("<I", hdr, 20, 148)
    struct.pack_into("<I", hdr, 84, len(payload))
    path.write_bytes(hdr + payload)
    return pad_w, pad_h


def crop(rgba, sw, sh, left, top, right, bottom, flip_u, flip_v):
    w, h = max(1, right - left), max(1, bottom - top)
    out = bytearray(w * h * 4)
    for y in range(h):
        sy = bottom - 1 - (y if not flip_v else h - 1 - y) if False else (top + (h - 1 - y if flip_v else y))
        # Keep the source top-left origin. flip_v mirrors vertically.
        sy = top + (h - 1 - y if flip_v else y)
        if sy < 0 or sy >= sh:
            continue
        for x in range(w):
            sx = left + (w - 1 - x if flip_u else x)
            if sx < 0 or sx >= sw:
                continue
            out[(y * w + x) * 4:(y * w + x) * 4 + 4] = rgba[(sy * sw + sx) * 4:(sy * sw + sx) * 4 + 4]
    return w, h, out


def safe_name(name):
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in name)


def wanted(name):
    return name.startswith("Garr") or name.startswith("_Garr") or name.startswith("!Garr")


def slice_template(text, name):
    marker = 'name="%s"' % name
    start = text.find(marker)
    if start < 0:
        raise SystemExit("missing template " + name)
    start = text.rfind("<", 0, start)
    def opens(i, tag):
        if not text.startswith("<" + tag, i):
            return False
        nxt = text[i + len(tag) + 1:i + len(tag) + 2]
        return nxt in (" ", ">", "\n", "\r", "\t", "/")

    depth = 0
    i = start
    while i < len(text):
        if opens(i, "Frame") or opens(i, "Button"):
            depth += 1
        elif text.startswith("</Frame>", i) or text.startswith("</Button>", i):
            depth -= 1
            if depth == 0:
                return text[start:text.find(">", i) + 1]
        i += 1
    raise SystemExit("unclosed template " + name)


def flip_of(body):
    m = re.search(r'<TexCoords\b([^>]*)/?>', body)
    if not m:
        return False, False
    attrs = m.group(1)
    def val(key):
        mm = re.search(key + r'="([0-9.]+)"', attrs)
        return float(mm.group(1)) if mm else None
    left, right, top, bottom = val("left"), val("right"), val("top"), val("bottom")
    return (left == 1.0 and right == 0.0), (top == 1.0 and bottom == 0.0)


def transform(xml, files, sizes):
    xml = re.sub(r"<Animations>.*?</Animations>", "", xml, flags=re.S)
    xml = re.sub(r"<KeyValues>.*?</KeyValues>", "", xml, flags=re.S)
    xml = re.sub(r'\s+mixin="[^"]*"', "", xml)
    xml = xml.replace('parentArray="Buttons"', 'parentKey="Button1"')

    def add_name(match):
        tag, attrs, end = match.group(1), match.group(2), match.group(3)
        if "parentKey=" not in attrs or re.search(r'\bname=', attrs):
            return match.group(0)
        key = re.search(r'parentKey="([^"]+)"', attrs).group(1)
        attrs = attrs.replace('parentKey="', 'name="$parent%s" parentKey="' % key, 1)
        return "<%s%s%s" % (tag, attrs, end)

    xml = re.sub(r"<([A-Za-z0-9]+)\b([^>]*parentKey=\"[^\"]+\"[^>]*?)(/?>)", add_name, xml)
    xml = re.sub(r'relativeKey="\$parent\.([A-Za-z0-9_]+)"', r'relativeTo="$parent\1"', xml)
    xml = re.sub(r'relativeKey="\$parent"', r'relativeTo="$parent"', xml)

    elem = re.compile(
        r"<(Texture|NormalTexture|HighlightTexture|PushedTexture)\b([^>]*)/>|"
        r"<(Texture|NormalTexture|HighlightTexture|PushedTexture)\b([^>]*)>(.*?)</\3>",
        re.S)

    def repl(m):
        if m.group(1):
            tag, attrs, body, close = m.group(1), m.group(2), "", "/>"
        else:
            tag, attrs, body, close = m.group(3), m.group(4), m.group(5), ">"
        am = re.search(r'atlas="([^"]+)"', attrs)
        if not am:
            return m.group(0)
        name = am.group(1)
        had_size = 'useAtlasSize="true"' in attrs
        tiled = 'horizTile="true"' in attrs or 'vertTile="true"' in attrs
        flip_u, flip_v = flip_of(body) if tiled else (False, False)
        path = files.get((name, flip_u, flip_v)) or files.get((name, False, False))
        if not path:
            return m.group(0)
        attrs = re.sub(r'\satlas="[^"]*"', ' file="%s"' % path, attrs, count=1)
        attrs = re.sub(r'\suseAtlasSize="true"', "", attrs)
        if tiled:
            body = re.sub(r"\s*<TexCoords\b[^>]*/>", "", body)
            body = re.sub(r"\s*<TexCoords\b[^>]*>.*?</TexCoords>", "", body, flags=re.S)
        if had_size and name in sizes:
            w, h = sizes[name]
            body = '<Size x="%d" y="%d"/>' % (max(1, w), max(1, h)) + body
            close = ">"
        if close == "/>":
            return "<%s%s/>" % (tag, attrs)
        return "<%s%s>%s</%s>" % (tag, attrs, body, tag)

    xml = elem.sub(repl, xml)
    return xml


STUB = r'''<Ui xmlns="http://www.blizzard.com/wow/ui/">
	<Font name="GameFontNormalMed3" inherits="GameFontNormal" virtual="true"/>
	<Font name="GameFontHighlightMedium" inherits="GameFontHighlight" virtual="true"/>
	<Font name="GameFontBlackSmall" inherits="GameFontNormalSmall" virtual="true"/>
	<Button name="MainHelpPlateButton" virtual="true">
		<Size x="32" y="32"/>
	</Button>
	<Button name="GarrisonMissionFollowerOrCategoryListButtonTemplate" virtual="true">
		<Size x="260" y="20"/>
	</Button>
	<Frame name="TooltipBackdropTemplate" virtual="true">
		<Backdrop bgFile="Interface\DialogFrame\UI-DialogBox-Background" edgeFile="Interface\Tooltips\UI-Tooltip-Border" tile="true">
			<EdgeSize><AbsValue val="16"/></EdgeSize>
			<TileSize><AbsValue val="16"/></TileSize>
			<BackgroundInsets><AbsInset left="4" right="4" top="4" bottom="4"/></BackgroundInsets>
		</Backdrop>
	</Frame>
	<Frame name="GarrisonListTemplateHeader" virtual="true">
		<Scripts>
			<OnLoad>
				self.Initialize = function() end
				self.SetSortFuncs = function() end
				self.ScrollBox = { SetDataProvider = function() end }
			</OnLoad>
		</Scripts>
	</Frame>
	<Frame name="BaseBasicFrameTemplate" virtual="true">
		<Layers>
			<Layer level="OVERLAY">
				<FontString name="$parentTitleText" parentKey="TitleText" inherits="GameFontNormal">
					<Anchors>
						<Anchor point="TOP" x="0" y="-5"/>
					</Anchors>
				</FontString>
			</Layer>
		</Layers>
		<Frames>
			<Button name="$parentClose" inherits="UIPanelCloseButton">
				<Anchors>
					<Anchor point="TOPRIGHT" x="2" y="1"/>
				</Anchors>
			</Button>
		</Frames>
	</Frame>
</Ui>
'''


def main():
    members, sheets = load_atlases()
    needed = {name: info for name, info in members.items() if wanted(name)}
    print("atlas names", len(needed))
    fdids = {info[0]: sheets[info[0]][0] for info in needed.values() if info[0] in sheets}
    listfile = {}
    with (ROOT / "_ref" / "community-listfile.csv").open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if ";" not in line:
                continue
            num, path = line.split(";", 1)
            if num.isdigit() and int(num) in fdids.values():
                listfile[int(num)] = path.strip()
    sheet_path = {}
    sheet_size = {}
    for atlas_id, fdid in fdids.items():
        rel = listfile.get(fdid, "")
        path = REF / rel.replace("\\", "/").lower()
        if not path.exists():
            path = REF / "interface" / "garrison" / Path(rel).name.lower()
        sheet_path[atlas_id] = (fdid, path)
        opened = blp_header(path) if path.exists() else None
        if opened:
            sheet_size[atlas_id] = (opened[3], opened[4])
    partial = set()
    for atlas, left, right, top, bottom, _w, _h in needed.values():
        size = sheet_size.get(atlas)
        if not size:
            continue
        sw, sh = size
        sheet_name = sheet_path[atlas][1].name
        shared = sheet_name.startswith("garrisonuiatlas") or sheet_name in (
            "garrisonbuildingui.blp", "garrisoncurrencyicons.blp", "garrisonmapshadowmoonplots.blp",
            "garrisonbuildings1a.blp")
        if shared and (left > 2 or top > 2 or right < sw - 2 or bottom < sh - 2):
            partial.add(atlas)
    decoded = {}
    for atlas_id in partial:
        fdid, path = sheet_path[atlas_id]
        print("crop sheet", atlas_id, path.name)
        decoded[atlas_id] = load_sheet(path)

    ART.mkdir(parents=True, exist_ok=True)
    files = {}
    lua_rows = []
    for name, (atlas, left, right, top, bottom, width, height) in sorted(needed.items()):
        size = sheet_size.get(atlas)
        fdid, sheet = sheet_path.get(atlas, (None, None))
        shared = sheet and (sheet.name.startswith("garrisonuiatlas") or sheet.name in (
            "garrisonbuildingui.blp", "garrisoncurrencyicons.blp", "garrisonmapshadowmoonplots.blp",
            "garrisonbuildings1a.blp"))
        full = (not shared) and fdid
        if full:
            path = "retail/%d.blp" % fdid
            files[(name, False, False)] = path
            lua_rows.append('["%s"]={"%s",%d,%d}' % (name.replace('"', '\\"'), path, max(1, right - left), max(1, bottom - top)))
            continue
        if atlas not in decoded or not decoded[atlas]:
            continue
        sw, sh, rgba = decoded[atlas]
        right = min(right, sw)
        bottom = min(bottom, sh)
        left = min(left, right - 1)
        top = min(top, bottom - 1)
        w, h, piece = crop(rgba, sw, sh, left, top, right, bottom, False, False)
        fname = safe_name(name) + ".blp"
        write_blp(ART / fname, w, h, piece)
        art_path = "Interface\\AddOns\\Blizzard_GarrisonUI\\Art\\" + fname
        files[(name, False, False)] = art_path
        lua_rows.append('["%s"]={"%s",%d,%d}' % (name.replace('"', '\\"'), art_path.replace("\\", "\\\\"), w, h))
    print("cropped", len(lua_rows))

    # Tiled textures that mirror the piece need a second crop. Do that while transforming.
    extra = {}

    def ensure_flip(name, flip_u, flip_v):
        key = (name, flip_u, flip_v)
        if key in files or name not in needed:
            return files.get(key)
        atlas, left, right, top, bottom, width, height = needed[name]
        if atlas not in decoded:
            return None
        sw, sh, rgba = decoded[atlas]
        w, h, piece = crop(rgba, sw, sh, left, top, min(right, sw), min(bottom, sh), flip_u, flip_v)
        suffix = ("_u" if flip_u else "") + ("_v" if flip_v else "")
        fname = safe_name(name) + suffix + ".blp"
        write_blp(ART / fname, w, h, piece)
        files[key] = "Interface\\AddOns\\Blizzard_GarrisonUI\\Art\\" + fname
        return files[key]

    shared = SHARED_XML.read_text(encoding="utf-8")
    building = BUILDING_XML.read_text(encoding="utf-8")
    # The retail file starts with a schema line the 3.3.5 parser does not need.
    building = re.sub(r"^<Ui\b[^>]*>", "<Ui>", building, count=1)
    head = slice_template(shared, "GarrisonUITemplate") + "\n" + slice_template(shared, "MaterialFrameTemplate")
    xml = "<Ui>\n" + head + "\n" + building.split(">", 1)[1]
    # Pre-pass: any tiled texture with a flip must have a mirrored file before transform.
    for m in re.finditer(r"<(?:Texture|NormalTexture|HighlightTexture|PushedTexture)\b([^>]*atlas=\"([^\"]+)\"[^>]*(?:horizTile|vertTile)=\"true\"[^>]*)>(.*?)</(?:Texture|NormalTexture|HighlightTexture|PushedTexture)>", xml, re.S):
        name = m.group(2)
        if 'horizTile="true"' in m.group(1) or 'vertTile="true"' in m.group(1):
            fu, fv = flip_of(m.group(3))
            if fu or fv:
                ensure_flip(name, fu, fv)
    sizes = {name: (info[5], info[6]) for name, info in needed.items()}
    xml = transform(xml, files, sizes)
    # Plot template needs inert animation objects because the animation block is not in 3.3.5.
    xml = xml.replace(
        "self:RegisterForDrag(\"LeftButton\");",
        "self:RegisterForDrag(\"LeftButton\");\n"
        "\t\t\t\tlocal idle = { Play = function() end, Stop = function() end, IsPlaying = function() return false end }\n"
        "\t\t\t\tif not self.BuildingGlowPulseAnim then self.BuildingGlowPulseAnim = idle end\n"
        "\t\t\t\tif not self.BuildingCreateFlareAnim then self.BuildingCreateFlareAnim = idle end",
        1)
    (OUT / "Blizzard_GarrisonBuildingUI.xml").write_text(xml, encoding="utf-8")
    (OUT / "Stub.xml").write_text(STUB, encoding="utf-8")
    (OUT / "Atlas.lua").write_text("EsteriaArchitectAtlas={\n" + ",\n".join(lua_rows) + "\n}\n", encoding="utf-8")
    lua = BUILDING_LUA.read_text(encoding="utf-8")
    lua = lua.replace(
        "\t\tif (not list.Buttons[i]) then\n"
        "\t\t\tlist.Buttons[i] = CreateFrame(\"BUTTON\", nil, list, \"GarrisonBuildingListButtonTemplate\");\n"
        "\t\t\tlist.Buttons[i]:SetPoint(\"TOP\", prevButton, \"BOTTOM\", 0, 2);\n"
        "\t\tend\n",
        "\t\tlist.Buttons = list.Buttons or {}\n"
        "\t\tif (not list.Buttons[i]) then\n"
        "\t\t\tlist.Buttons[i] = CreateFrame(\"BUTTON\", nil, list, \"GarrisonBuildingListButtonTemplate\");\n"
        "\t\t\tif prevButton then\n"
        "\t\t\t\tlist.Buttons[i]:SetPoint(\"TOP\", prevButton, \"BOTTOM\", 0, 2);\n"
        "\t\t\telse\n"
        "\t\t\t\tlist.Buttons[i]:SetPoint(\"TOP\", list, \"TOP\", 0, -10);\n"
        "\t\t\tend\n"
        "\t\tend\n")
    lua = lua.replace(
        "function GarrisonBuildingTab_Select(self)\n"
        "\tGarrisonBuildingList_SelectTab(self)\n"
        "\tGarrisonBuildingListButton_Select(GarrisonBuildingFrame.BuildingList.Buttons[1]);\n"
        "end\n",
        "function GarrisonBuildingTab_Select(self)\n"
        "\tGarrisonBuildingList_SelectTab(self)\n"
        "\tlocal button = GarrisonBuildingFrame.BuildingList.Buttons and GarrisonBuildingFrame.BuildingList.Buttons[1];\n"
        "\tif button then\n"
        "\t\tGarrisonBuildingListButton_Select(button);\n"
        "\tend\n"
        "end\n")
    (OUT / "Blizzard_GarrisonBuildingUI.lua").write_text(lua, encoding="utf-8")
    print("xml atlas left", xml.count('atlas="'))
    print("relativeKey left", xml.count("relativeKey="))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
