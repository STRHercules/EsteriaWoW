"""Generate ElvUI-styled replacements for the LIVE glue textures.

Sources are resolved in real client load order: patch-A.MPQ first (the
retail-interface art that actually renders), then locale-enUS.MPQ (Blizzard
stock, which still supplies Interface\\Buttons\\* chrome and the Disabled
button that patch-A omits).

Every replacement preserves the source texture's ALPHA silhouette and its exact
dimensions/mip count, so the GlueXML TexCoords keep framing correctly and no
frame definition needs touching.

ElvUI 6.09 palette (Settings/Profile.lua defaults):
    backdropcolor     0.10, 0.10, 0.10   #1A1A1A
    backdropfadecolor 0.06, 0.06, 0.06   #0F0F0F
    bordercolor       0.00, 0.00, 0.00   #000000
    valuecolor        0.99, 0.48, 0.17   #FD7A2B
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools")))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image, ImageDraw  # noqa: E402
from cars_mount_pack import Storm, DLL_DEFAULT  # noqa: E402
from blp import decode_blp, encode_blp_bgra, describe_blp  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT_ROOT = HERE / "staging" / "root" / "Interface"
PREVIEW = HERE / "preview_out"

DATA = Path(r"G:\3.3.5a - Dev\Data")
SOURCES = [
    DATA / "patch-A.MPQ",          # retail-interface art (wins for Glues\Common)
    DATA / "enUS" / "locale-enUS.MPQ",  # Blizzard stock (wins for Buttons)
]

# ElvUI palette
BACKDROP = (0.10, 0.10, 0.10)
BACKDROP_FADE = (0.06, 0.06, 0.06)
BORDER = (0.00, 0.00, 0.00)
ACCENT = (0.99, 0.48, 0.17)

RAMP_LO = (0.015, 0.015, 0.015)
RAMP_HI = (0.170, 0.170, 0.170)


def srgb(value: float) -> int:
    return max(0, min(255, round(value * 255)))


def _percentile(values: list[int], fraction: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    return ordered[int(fraction * (len(ordered) - 1))]


def _normalise(luminance: list[int], alpha: list[int]) -> tuple[int, int]:
    visible = [l for l, a in zip(luminance, alpha) if a > 8]
    if not visible:
        return 0, 255
    lo = _percentile(visible, 0.02)
    hi = _percentile(visible, 0.99)
    if hi <= lo:
        hi = min(255, lo + 1)
    return lo, hi


def remap_luminance(image, low=RAMP_LO, high=RAMP_HI, alpha_scale=1.0, alpha_floor=0):
    """Keep the stock alpha silhouette; remap visible shading onto low..high."""
    rgba = image.convert("RGBA")
    width, height = rgba.size
    a_px = list(rgba.getchannel("A").get_flattened_data())
    l_px = list(rgba.convert("L").get_flattened_data())
    lo, hi = _normalise(l_px, a_px)

    out = Image.new("RGBA", (width, height))
    out_px = out.load()
    for index in range(width * height):
        a = a_px[index]
        x, y = index % width, index // width
        if a == 0:
            out_px[x, y] = (0, 0, 0, 0)
            continue
        t = (l_px[index] - lo) / (hi - lo)
        t = 0.0 if t < 0 else (1.0 if t > 1 else t)
        out_px[x, y] = (
            srgb(low[0] + (high[0] - low[0]) * t),
            srgb(low[1] + (high[1] - low[1]) * t),
            srgb(low[2] + (high[2] - low[2]) * t),
            int(max(alpha_floor, min(255, a * alpha_scale))),
        )
    return out


def flat_fill(image, color, alpha_scale=1.0):
    rgba = image.convert("RGBA")
    out = Image.new("RGBA", rgba.size, (srgb(color[0]), srgb(color[1]), srgb(color[2]), 255))
    alpha = rgba.getchannel("A")
    if alpha_scale != 1.0:
        alpha = alpha.point(lambda v: int(max(0, min(255, v * alpha_scale))))
    out.putalpha(alpha)
    return out


def decolor(image, color, alpha_scale=1.0):
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    out = Image.new("RGBA", rgba.size, (srgb(color[0]), srgb(color[1]), srgb(color[2]), 255))
    if alpha_scale != 1.0:
        alpha = alpha.point(lambda v: int(max(0, min(255, v * alpha_scale))))
    out.putalpha(alpha)
    return out


def glow(image, color, alpha_scale=1.0, gamma=1.0):
    """Re-tint an ADD-blended texture: shape lives in RGB luminance, not alpha."""
    rgba = image.convert("RGBA")
    width, height = rgba.size
    a_px = list(rgba.getchannel("A").get_flattened_data())
    l_px = list(rgba.convert("L").get_flattened_data())
    lo, hi = _normalise(l_px, a_px)

    out = Image.new("RGBA", (width, height))
    out_px = out.load()
    for index in range(width * height):
        a = a_px[index]
        x, y = index % width, index // width
        if a == 0:
            out_px[x, y] = (0, 0, 0, 0)
            continue
        t = (l_px[index] - lo) / (hi - lo)
        t = 0.0 if t < 0 else (1.0 if t > 1 else t)
        t = t**gamma
        out_px[x, y] = (
            srgb(color[0] * t),
            srgb(color[1] * t),
            srgb(color[2] * t),
            int(max(0, min(255, a * alpha_scale))),
        )
    return out


def dered(
    image,
    low=(0.020, 0.020, 0.020),
    high=(0.170, 0.170, 0.170),
    hue_limit=20,
    sat_min=0.30,
    val_min=0.12,
):
    """Recolour only RED pixels, leaving everything else byte-identical.

    Needed for multi-purpose button atlases (e.g. 128redbuttonpart2) that mix red
    button faces with already-dark buttons and gold glyph icons. A blanket ramp
    would erase the icons, so detection is by HUE: red faces sit near 0 degrees,
    gold glyphs near 50, and neutral chrome has almost no saturation.
    """
    rgba = image.convert("RGBA")
    width, height = rgba.size
    hsv = rgba.convert("RGB").convert("HSV")
    a_px = list(rgba.getchannel("A").get_flattened_data())
    h_px = list(hsv.getchannel("H").get_flattened_data())
    s_px = list(hsv.getchannel("S").get_flattened_data())
    v_px = list(hsv.getchannel("V").get_flattened_data())

    def is_red(idx: int) -> bool:
        if a_px[idx] <= 8:
            return False
        hue = h_px[idx]
        return (
            (hue <= hue_limit or hue >= 256 - hue_limit)
            and s_px[idx] >= int(sat_min * 255)
            and v_px[idx] >= int(val_min * 255)
        )

    candidates = [v_px[i] for i in range(width * height) if is_red(i)]
    if candidates:
        lo = _percentile(candidates, 0.03)
        hi = _percentile(candidates, 0.97)
    else:
        lo, hi = 0, 255
    if hi <= lo:
        hi = min(255, lo + 1)

    out = Image.new("RGBA", (width, height))
    out_px = out.load()
    src = rgba.load()
    recoloured = 0
    for index in range(width * height):
        x, y = index % width, index // width
        if not is_red(index):
            out_px[x, y] = src[x, y]
            continue
        t = (v_px[index] - lo) / (hi - lo)
        t = 0.0 if t < 0 else (1.0 if t > 1 else t)
        out_px[x, y] = (
            srgb(low[0] + (high[0] - low[0]) * t),
            srgb(low[1] + (high[1] - low[1]) * t),
            srgb(low[2] + (high[2] - low[2]) * t),
            a_px[index],
        )
        recoloured += 1
    return out


def flat_alpha(image, color, alpha):
    """Uniform flat fill at a fixed alpha, ignoring the source entirely.

    This is the glue equivalent of ElvUI's tiled bgFile: a plain quad with no
    baked border or bevel. The frame's own <Backdrop edgeFile> draws the rim.
    """
    return Image.new(
        "RGBA",
        image.size,
        (srgb(color[0]), srgb(color[1]), srgb(color[2]), int(max(0, min(255, alpha * 255)))),
    )


def elvui_quad(image, panels):
    """Draw sharp-cornered translucent panels, discarding the stock art.

    Mirrors how ElvUI actually builds a element: a flat quad (its blankTex)
    plus a hard 1px rim, at backdropfadecolor alpha. No rounded corners, no
    bevel, no gradient -- everything the stock silhouette carried is dropped.

    `panels` is a list of dicts:
        rect      (x0, y0, x1, y1) in source pixels, x1/y1 exclusive
        fill      (r, g, b) 0..1
        alpha     0..1
        border    (r, g, b) 0..1 or None to skip the rim
        border_px source-pixel rim width (scaled down when the region is
                  stretched, so ~1px lands on screen)
    """
    out = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(out)
    for panel in panels:
        x0, y0, x1, y1 = panel["rect"]
        # clamp to the texture so a bad rect can never write out of bounds
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(image.width, x1), min(image.height, y1)
        if x1 <= x0 or y1 <= y0:
            continue
        fill = panel.get("fill", BACKDROP_FADE)
        alpha = panel.get("alpha", 0.80)
        draw.rectangle(
            [x0, y0, x1 - 1, y1 - 1],
            fill=(srgb(fill[0]), srgb(fill[1]), srgb(fill[2]), int(alpha * 255)),
        )
        border = panel.get("border", BORDER)
        width = panel.get("border_px", 3)
        if border is not None and width > 0:
            draw.rectangle(
                [x0, y0, x1 - 1, y1 - 1],
                outline=(srgb(border[0]), srgb(border[1]), srgb(border[2]), 255),
                width=min(width, max(1, (x1 - x0) // 2), max(1, (y1 - y0) // 2)),
            )
    return out


def _is_red_hue(hue, sat, val, hue_limit=20, sat_min=0.30, val_min=0.12):
    if val < int(val_min * 255):
        return False
    if sat < int(sat_min * 255):
        return False
    return hue <= hue_limit or hue >= 256 - hue_limit


def elvui_quad_with_glyph(image, panels, glyph_min_value=110, glyph_min_sat=70, glyph_alpha_floor=210):
    """Sharp translucent ElvUI quad that preserves a baked-in glyph.

    Some glue atlases bake a semantic icon (a gold eye, a gold trash can) into the
    button face. Replacing the whole cell would erase the icon; keeping the stock
    cell would keep the rounded opaque slab. So draw the quad, then stamp back only
    the glyph pixels, leaving the face flat and sharp.

    A glyph pixel must be BOTH bright and saturated: that keeps the gold icon while
    rejecting the grey stone bevel and its dashed highlights, which are bright but
    almost colourless.
    """
    out = elvui_quad(image, panels)
    src = image.convert("RGBA")
    hsv = src.convert("RGB").convert("HSV")
    h_px = list(hsv.getchannel("H").get_flattened_data())
    s_px = list(hsv.getchannel("S").get_flattened_data())
    v_px = list(hsv.getchannel("V").get_flattened_data())
    src_px = list(src.get_flattened_data())
    out_px = out.load()
    width = out.width
    for panel in panels:
        x0, y0, x1, y1 = panel["rect"]
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(out.width, x1), min(out.height, y1)
        panel_min_value = panel.get("glyph_min_value", glyph_min_value)
        panel_min_sat = panel.get("glyph_min_sat", glyph_min_sat)
        for y in range(y0, y1):
            for x in range(x0, x1):
                index = y * width + x
                r, g, b, a = src_px[index]
                if a == 0 or v_px[index] < panel_min_value or s_px[index] < panel_min_sat:
                    continue
                if _is_red_hue(h_px[index], s_px[index], v_px[index]):
                    continue
                out_px[x, y] = (r, g, b, max(a, glyph_alpha_floor))
    return out


def build(image, spec):
    kind = spec["kind"]
    if kind == "ramp":
        return remap_luminance(
            image,
            spec.get("low", RAMP_LO),
            spec.get("high", RAMP_HI),
            spec.get("alpha_scale", 1.0),
            spec.get("alpha_floor", 0),
        )
    if kind == "flat":
        return flat_fill(image, spec["color"], spec.get("alpha_scale", 1.0))
    if kind == "tint":
        return decolor(image, spec["color"], spec.get("alpha_scale", 1.0))
    if kind == "glow":
        return glow(image, spec["color"], spec.get("alpha_scale", 1.0), spec.get("gamma", 1.0))
    if kind == "dered":
        return dered(
            image,
            spec.get("low", (0.020, 0.020, 0.020)),
            spec.get("high", (0.170, 0.170, 0.170)),
            spec.get("hue_limit", 20),
            spec.get("sat_min", 0.30),
            spec.get("val_min", 0.12),
        )
    if kind == "panel":
        return flat_alpha(image, spec.get("color", BACKDROP_FADE), spec.get("alpha", 0.80))
    if kind == "quad":
        return elvui_quad(image, spec["panels"])
    if kind == "quad_glyph":
        return elvui_quad_with_glyph(
            image,
            spec["panels"],
            spec.get("glyph_min_value", 110),
            spec.get("glyph_min_sat", 70),
            spec.get("glyph_alpha_floor", 210),
        )
    raise ValueError(f"unknown kind {kind}")


GC = r"Interface\Glues\Common"
B = r"Interface\Buttons"

# output path -> {source path, transform}
SPECS: dict[str, dict] = {}


def add(out_path, source_path, **spec):
    # MPQ lookup hashes the full filename, so the extension is required.
    if "." not in Path(out_path.replace("\\", "/")).name:
        out_path = f"{out_path}.blp"
    if "." not in Path(source_path.replace("\\", "/")).name:
        source_path = f"{source_path}.blp"
    SPECS[out_path] = {"source": source_path, **spec}


# ---- glue panel buttons ----
# The stock art is a rounded, bevelled, fully-opaque red slab. ElvUI's language is
# the opposite: a flat sharp quad at backdropfadecolor alpha with a hard 1px rim.
# GlueButtons.xml samples these at TexCoords 0..0.578125 x 0..0.75, so the quad is
# drawn into exactly that region and the rest is left transparent.
PANEL_BTN_RECT = (0, 0, 592, 192)          # 1024x256 source -> 170x45 button
PANEL_BTN_UP = {"rect": PANEL_BTN_RECT, "fill": BACKDROP, "alpha": 0.80, "border_px": 3}
PANEL_BTN_DOWN = {"rect": PANEL_BTN_RECT, "fill": (0.04, 0.04, 0.04), "alpha": 0.85, "border_px": 3}
for name in ("Glue-Panel-Button-Up", "Glue-Panel-Button-Up-Blue"):
    add(rf"{GC}\{name}.blp", rf"{GC}\{name}.blp", kind="quad", panels=[PANEL_BTN_UP])
for name in ("Glue-Panel-Button-Down", "Glue-Panel-Button-Down-Blue"):
    add(rf"{GC}\{name}.blp", rf"{GC}\{name}.blp", kind="quad", panels=[PANEL_BTN_DOWN])
# patch-A omits Disabled, so Blizzard stock supplies it (256x64, same TexCoords)
add(
    rf"{GC}\Glue-Panel-Button-Disabled.blp",
    rf"{GC}\Glue-Panel-Button-Disabled.blp",
    kind="quad",
    panels=[{"rect": (0, 0, 148, 48), "fill": (0.07, 0.07, 0.07), "alpha": 0.60, "border_px": 1}],
)

# ---- ADD-blended highlight / glow layers (TexCoords 0..0.625 x 0..0.6875) ----
add(
    rf"{GC}\Glue-Panel-Button-Highlight.blp",
    rf"{GC}\Glue-Panel-Button-Highlight.blp",
    kind="quad",
    panels=[{"rect": (0, 0, 160, 44), "fill": (0.14, 0.14, 0.14), "alpha": 0.55, "border": None}],
)
add(
    rf"{GC}\Glue-Panel-Button-Highlight-Blue.blp",
    rf"{GC}\Glue-Panel-Button-Highlight-Blue.blp",
    kind="quad",
    panels=[{"rect": (0, 0, 80, 22), "fill": (0.14, 0.14, 0.14), "alpha": 0.55, "border": None}],
)
# the glow keeps ElvUI's accent so hover still reads as "value" coloured
add(rf"{GC}\Glue-Panel-Button-Glow.blp", rf"{GC}\Glue-Panel-Button-Glow.blp", kind="glow", color=ACCENT, gamma=0.85)

# ---- big buttons ----
add(
    rf"{GC}\Glues-BigButton-Up.blp",
    rf"{GC}\Glues-BigButton-Up.blp",
    kind="ramp",
    low=(0.035, 0.035, 0.035),
    high=(0.185, 0.185, 0.185),
)
add(
    rf"{GC}\Glues-BigButton-Down.blp",
    rf"{GC}\Glues-BigButton-Down.blp",
    kind="ramp",
    low=(0.008, 0.008, 0.008),
    high=(0.095, 0.095, 0.095),
)
add(rf"{GC}\Glues-BigButton-Rays.blp", rf"{GC}\Glues-BigButton-Rays.blp", kind="glow", color=(0.60, 0.33, 0.13), alpha_scale=0.55)

# ---- Blizzard checkbox chrome: kills the green tick ----
add(rf"{B}\UI-CheckBox-Check.blp", rf"{B}\UI-CheckBox-Check.blp", kind="glow", color=ACCENT)
add(rf"{B}\UI-CheckBox-Check-Disabled.blp", rf"{B}\UI-CheckBox-Check-Disabled.blp", kind="glow", color=(0.45, 0.45, 0.45))
add(rf"{B}\UI-CheckBox-Up.blp", rf"{B}\UI-CheckBox-Up.blp", kind="ramp", low=(0.055, 0.055, 0.055), high=(0.160, 0.160, 0.160))
add(rf"{B}\UI-CheckBox-Down.blp", rf"{B}\UI-CheckBox-Down.blp", kind="ramp", low=(0.020, 0.020, 0.020), high=(0.100, 0.100, 0.100))
add(rf"{B}\UI-CheckBox-Highlight.blp", rf"{B}\UI-CheckBox-Highlight.blp", kind="glow", color=(0.40, 0.40, 0.40))

# ---- scrollbars / knob / minimize (glue dialogs, char list, options) ----
# Arrow glyphs live in the stock RGB (alpha is an opaque plate), so use the
# luminance-preserving glow path rather than a flat tint.
for name in ("Up", "Down", "Disabled", "Highlight"):
    arrow_colour = (0.45, 0.45, 0.45) if name == "Disabled" else (0.86, 0.86, 0.86)
    if name == "Highlight":
        arrow_colour = (1.00, 1.00, 1.00)
    add(
        rf"{B}\UI-ScrollBar-ScrollUpButton-{name}.blp",
        rf"{B}\UI-ScrollBar-ScrollUpButton-{name}.blp",
        kind="glow",
        color=arrow_colour,
    )
    add(
        rf"{B}\UI-ScrollBar-ScrollDownButton-{name}.blp",
        rf"{B}\UI-ScrollBar-ScrollDownButton-{name}.blp",
        kind="glow",
        color=arrow_colour,
    )
add(rf"{B}\UI-ScrollBar-Knob.blp", rf"{B}\UI-ScrollBar-Knob.blp", kind="ramp", low=(0.060, 0.060, 0.060), high=(0.190, 0.190, 0.190))
add(rf"{B}\UI-Panel-MinimizeButton-Up.blp", rf"{B}\UI-Panel-MinimizeButton-Up.blp", kind="glow", color=(0.80, 0.80, 0.80))
add(rf"{B}\UI-Panel-MinimizeButton-Down.blp", rf"{B}\UI-Panel-MinimizeButton-Down.blp", kind="glow", color=(0.55, 0.55, 0.55))
add(rf"{B}\UI-Panel-MinimizeButton-Highlight.blp", rf"{B}\UI-Panel-MinimizeButton-Highlight.blp", kind="glow", color=(1.00, 1.00, 1.00))

# ---- character select / create inline button art ----
# CharacterSelect.xml samples this 1024x512 atlas at explicit TexCoords for three
# buttons. The cells bake a semantic glyph into the red face (gold eye on the
# Normal/Pushed cells, gold trash can on Normal2), so use the quad+glyph path:
# flat sharp translucent ElvUI face, with the glyph stamped back on top.
#   Normal  = 0.252929688..0.379882813 x 0.515625..0.753906250
#   Pushed  = 0.378906250..0.505859375 x 0.515625..0.753906250
#   Normal2 = 0.001953125..0.126953125 x 0..0.248046875
#   Pushed2 = 0.128906250..0.253906250 x 0..0.248046875
#   Highlight (ADD) = 0.253906250..0.378906250 x 0..0.248046875
add(
    r"Interface\Glues\CharacterSelect\128redbuttonpart2.blp",
    r"Interface\Glues\CharacterSelect\128redbuttonpart2.blp",
    kind="quad_glyph",
    panels=[
        {"rect": (259, 264, 389, 386), "fill": BACKDROP, "alpha": 0.80, "border_px": 2},
        {"rect": (388, 264, 518, 386), "fill": (0.04, 0.04, 0.04), "alpha": 0.85, "border_px": 2,
         "glyph_min_value": 78},
        {"rect": (2, 0, 130, 127), "fill": BACKDROP, "alpha": 0.80, "border_px": 2},
        {"rect": (132, 0, 260, 127), "fill": (0.04, 0.04, 0.04), "alpha": 0.85, "border_px": 2,
         "glyph_min_value": 78},
        {"rect": (260, 0, 388, 127), "fill": (0.14, 0.14, 0.14), "alpha": 0.50, "border": None},
    ],
)
# dark buttons carrying gold glyphs -> keep the button, lighten the glyph
add(
    r"Interface\Glues\CharacterCreate\UI-RotationRight-Big-Up.blp",
    r"Interface\Glues\CharacterCreate\UI-RotationRight-Big-Up.blp",
    kind="glow",
    color=(0.86, 0.86, 0.86),
)
add(
    r"Interface\Glues\CharacterCreate\UI-RotationRight-Big-Down.blp",
    r"Interface\Glues\CharacterCreate\UI-RotationRight-Big-Down.blp",
    kind="glow",
    color=(0.60, 0.60, 0.60),
)
# gold triangle used as the $parentIcon overlay on character-create buttons
add(r"Interface\Glues\Common\Arrow.blp", r"Interface\Glues\Common\Arrow.blp", kind="glow", color=(0.86, 0.86, 0.86))


# =====================================================================
# Remaining stock chrome on the realm list, options, dialogs and tooltips
# (discovered by scanning the winning glue Lua/XML for Interface references)
# =====================================================================

def add_many(paths, kind, **spec):
    for path in paths:
        add(path, path, kind=kind, **spec)


# tiling tooltip/dialog backdrops -> flat ElvUI fill at backdropfadecolor alpha,
# so the 3D scene reads through instead of a solid black slab
add_many(
    [
        r"Interface\Tooltips\UI-Tooltip-Background",
        r"Interface\DialogFrame\UI-DialogBox-Background",
        r"Interface\Glues\Common\Glue-Tooltip-Background",
    ],
    "panel",
    color=BACKDROP_FADE,
    alpha=0.80,
)

# border / edge atlases -> dark grey rim so panels still read against the backdrop
add_many(
    [
        r"Interface\Tooltips\UI-Tooltip-Border",
        r"Interface\tooltips\BorderAlert",
        r"Interface\tooltips\Glue-Tooltip-Border",
        r"Interface\tooltips\ui-tooltip-border-maw",
        r"Interface\tooltips\ui-tooltip-border-mawBlack",
        r"Interface\DialogFrame\UI-DialogBox-Border",
        r"Interface\DialogFrame\UI-DialogBox-Header",
        r"Interface\ChatFrame\UI-ChatInputBorder-Left",
        r"Interface\ChatFrame\UI-ChatInputBorder-Right",
        r"Interface\Common\Common-Input-Border",
        r"Interface\HelpFrame\HelpFrame-TopLeft",
        r"Interface\HelpFrame\HelpFrame-Top",
        r"Interface\HelpFrame\HelpFrame-BotLeft",
        r"Interface\HelpFrame\HelpFrame-Bottom",
        r"Interface\HelpFrame\HelpFrame-BotRight",
        r"Interface\Glues\Login\Glues-TOS-TopRight",
    ],
    "ramp",
    low=(0.055, 0.055, 0.055),
    high=(0.280, 0.280, 0.280),
)

# realm-list / options tabs, scrollbar and slider chrome (stone -> flat dark)
add_many(
    [
        r"Interface\PaperDollInfoFrame\UI-Character-ActiveTab",
        r"Interface\PaperDollInfoFrame\UI-Character-InActiveTab",
        r"Interface\PaperDollInfoFrame\UI-Character-ScrollBar",
        r"Interface\OptionsFrame\UI-OptionsFrame-ActiveTab",
        r"Interface\OptionsFrame\UI-OptionsFrame-InActiveTab",
        r"Interface\OptionsFrame\UI-OptionsFrame-Spacer",
        r"Interface\Buttons\UI-SliderBar-Background",
        r"Interface\Buttons\UI-SliderBar-Button-Horizontal",
        r"Interface\Buttons\UI-Panel-Button-Up",
        r"Interface\Buttons\UI-Panel-Button-Down",
        r"Interface\Buttons\UI-Panel-Button-Disabled",
        r"Interface\Buttons\UI-Panel-Button-Disabled-Down",
    ],
    "ramp",
    low=(0.030, 0.030, 0.030),
    high=(0.200, 0.200, 0.200),
)

# ADD-blended tab/title highlights -> neutral sheen instead of blue/white blaze
add_many(
    [
        r"Interface\PaperDollInfoFrame\UI-Character-Tab-Highlight",
        r"Interface\QuestFrame\UI-QuestLogTitleHighlight",
        r"Interface\QuestFrame\UI-QuestTitleHighlight",
        r"Interface\Buttons\ButtonHilight-Square",
        r"Interface\Buttons\UI-Common-MouseHilight",
        r"Interface\Buttons\UI-Panel-Button-Highlight",
    ],
    "glow",
    color=(0.38, 0.38, 0.38),
)

# small glyph buttons: keep the glyph, drop the gold
add_many(
    [
        r"Interface\Buttons\UI-SortArrow",
        r"Interface\Buttons\UI-MinusButton-UP",
        r"Interface\Buttons\UI-PlusButton-Hilight",
        r"Interface\Glues\Login\UI-BackArrow",
        r"Interface\ChatFrame\ChatFrameExpandArrow",
        r"Interface\ChatFrame\UI-ChatIcon-ScrollDown-Up",
        r"Interface\ChatFrame\UI-ChatIcon-ScrollDown-Disabled",
        r"Interface\ChatFrame\ChatFrameColorSwatch",
    ],
    "glow",
    color=(0.84, 0.84, 0.84),
)
add_many(
    [
        r"Interface\Buttons\UI-MinusButton-DOWN",
        r"Interface\ChatFrame\UI-ChatIcon-ScrollDown-Down",
    ],
    "glow",
    color=(0.55, 0.55, 0.55),
)

# another red button set referenced by the login screen -> de-red, keep the icons
add(
    r"Interface\Glues\Common\redbutton2x",
    r"Interface\Glues\Common\redbutton2x",
    kind="dered",
)

# remaining chrome found on the character-select / dropdown chrome
add(
    r"Interface\Buttons\UI-PaidCharacterCustomization-Button",
    r"Interface\Buttons\UI-PaidCharacterCustomization-Button",
    kind="dered",
)
add(
    r"Interface\Glues\CharacterCreate\CharacterCreate-LabelFrame",
    r"Interface\Glues\CharacterCreate\CharacterCreate-LabelFrame",
    kind="ramp",
    low=(0.030, 0.030, 0.030),
    high=(0.190, 0.190, 0.190),
)
add(
    r"Interface\Glues\CharacterSelect\Glue-CharacterSelect-Highlight",
    r"Interface\Glues\CharacterSelect\Glue-CharacterSelect-Highlight",
    kind="glow",
    color=(0.42, 0.42, 0.42),
)

# NOTE: semantic icons are deliberately preserved (alert icons, guild note,
# race/class art) -- only chrome and navigation glyphs are reskinned.


def main() -> int:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    storm = Storm(DLL_DEFAULT)
    handles = {}
    for archive in SOURCES:
        if archive.exists():
            handles[archive] = storm.open_archive(archive)

    written, missing = 0, []
    try:
        for out_path, spec in SPECS.items():
            raw = None
            used = None
            for archive, handle in handles.items():
                try:
                    raw = storm.read(handle, spec["source"])
                    used = archive.name
                    break
                except OSError:
                    continue
            if raw is None:
                missing.append(spec["source"])
                print(f"MISSING {spec['source']}")
                continue

            image = decode_blp(raw)
            stock_desc = describe_blp(raw)
            result = build(image, spec)
            encoded = encode_blp_bgra(result)

            target = OUT_ROOT / Path(out_path.replace("\\", "/")[len("Interface/"):])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(encoded)

            safe = out_path.replace("\\", "_").replace("/", "_")
            result.save(PREVIEW / f"{safe}.png")
            combo = Image.new("RGBA", (image.width * 2 + 8, image.height), (32, 32, 32, 255))
            combo.alpha_composite(image.convert("RGBA"), (0, 0))
            combo.alpha_composite(result.convert("RGBA"), (image.width + 8, 0))
            combo.convert("RGB").save(PREVIEW / f"{safe}-compare.png")

            print(
                f"{out_path}\n    src={used} {stock_desc} -> {describe_blp(encoded)} kind={spec['kind']}"
            )
            written += 1
    finally:
        for archive, handle in handles.items():
            storm.dll.SFileCloseArchive(handle)

    print(f"\nwrote {written} textures to {OUT_ROOT}")
    if missing:
        print(f"missing {len(missing)}: {missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
