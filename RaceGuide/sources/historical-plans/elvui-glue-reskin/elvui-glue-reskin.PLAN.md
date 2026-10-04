# ElvUI glue reskin (login / char select / char create)

## Goal

Make the client's **glue screens** (login, realm list, character select, character
create, options, dialogs) match **ElvUI 6.09's default dark theme**, and remove
stock Warcraft chrome — above all the **red buttons**.

## Why this is not an addon change

ElvUI is an addon. Addons do not load until after the glue screens, so ElvUI can
never touch the login or character-select screens. Extending "ElvUI" to them means
patching the client's **GlueXML** and **glue textures** inside MPQ archives.

## Environment

| Item | Value |
|---|---|
| Client | `G:\3.3.5a - Dev` |
| ElvUI | 6.09 (AzerothCore WotLK distribution), served from `PATCH-V.mpq` → `Interface\AddOns\ElvUI` |
| MPQ tooling | StormLib at `R:\Users\Zach\Downloads\battlemon\Client\wdbx-2.4.1.a-extended-dbc\x64\StormLib.dll`, wrapped by `tools/cars_mount_pack.py` |
| Write targets | `Data\patch-Z.MPQ`, `Data\enUS\patch-enUS-Z.MPQ` (highest load order) |

## How the glue actually resolves (measured, not assumed)

Load order was resolved empirically in `resolve_glue.py`:

| File | Winning archive | Notes |
|---|---|---|
| `Interface\Glues\Common\Glue-Panel-Button-*` | **`patch-A.MPQ`** | retail-interface art, **1024×256 DXT5**; Blizzard stock is only 256×64 |
| `Interface\GlueXML\GlueButtons.xml` | **`patch-A.MPQ`** | same texture paths + TexCoords as stock |
| `Interface\GlueXML\AccountLogin.{lua,xml}` | **`patch-A.MPQ`** | War Within overlay applied (`.pre-warwithin.bak` present) |
| `Interface\GlueXML\GlueFontStyles.xml` | **`enUS\patch-enUS-2.MPQ`** | still gold; adds fonts stock lacks |
| `Interface\GlueXML\CharacterSelect/CharacterCreate/GlueParent` | `enUS\patch-enUS-Z.MPQ` | existing Esteria custom-race work |
| `Interface\Buttons\UI-CheckBox-*`, scrollbars | `enUS\locale-enUS.MPQ` | untouched Blizzard stock |

`patch-A.MPQ` contains unused leftovers (`RedButtonUp/Down/Disable/Highlight`,
`glue-panel-button-*-v2`) — nothing references them, so they were left alone.

## Palette (ElvUI 6.09 `Settings/Profile.lua` defaults)

| Token | Value | Hex |
|---|---|---|
| `backdropcolor` | `0.10, 0.10, 0.10` | `#1A1A1A` |
| `backdropfadecolor` | `0.06, 0.06, 0.06, a=0.8` | `#0F0F0F` |
| `bordercolor` | `0, 0, 0` | `#000000` |
| `valuecolor` (accent) | `0.99, 0.48, 0.17` | `#FD7A2B` |
| text | `0.898, 0.890, 0.890` | `#E5E3E3` |

## Approach: silhouette-preserving recolour

Rather than author new art (which would break every existing `TexCoords` crop), each
stock texture is decoded, its **alpha mask kept as-is**, and its RGB shading remapped
into the ElvUI ramp. Dimensions and mip count are preserved exactly.

Three transforms:

- **`ramp`** — remap visible luminance onto `RAMP_LO..RAMP_HI`. Used for button faces.
- **`glow`** — keep luminance *shape*, retint hue. Required for `alphaMode="ADD"`
  layers and for textures whose glyph lives in RGB with flat alpha (arrows, ticks,
  minimise X, rotation icons) — a flat tint would collapse these into solid squares.
  This bug was hit and fixed three times.
- **`dered`** — hue-targeted: recolour **only** red pixels (hue near 0°, saturated),
  leaving everything else byte-identical. Needed for button *atlases* that mix red
  faces with already-dark buttons and gold glyph icons (`128redbuttonpart2`), where a
  blanket ramp would erase the icons.

## How ElvUI actually constructs an element (measured, not assumed)

From `ElvUI/Core/Toolkit.lua` `SetTemplate` (line 80) and `Core/Core.lua`:

```lua
-- Media/SharedMedia.lua:179
E.Media.Textures.White8x8 = [[Interface\BUTTONS\WHITE8X8]]   -- one plain white pixel

frame:SetBackdrop({
    bgFile   = E.media.blankTex,   -- the same plain white pixel
    edgeFile = E.media.blankTex,
    tile = false, tileSize = 0,
    edgeSize = E.mult,             -- 1 physical pixel
    insets = {left = 0, right = 0, top = 0, bottom = 0}
})
frame:SetBackdropColor(backdropr, backdropg, backdropb, backdropa)
frame:SetBackdropBorderColor(borderr, borderg, borderb)
```

So every ElvUI element is:

1. **one flat white pixel** (`Interface\BUTTONS\WHITE8X8`), stretched — not tiled art
2. tinted with `backdropcolor 0.10,0.10,0.10` (Default) or
   `backdropfadecolor 0.06,0.06,0.06` **at alpha 0.80** (Transparent)
3. given a hard **1px rim** from the same pixel, `bordercolor 0,0,0`
4. optionally inner (`iborder`) + outer (`oborder`) 1px black rims for the double edge

The consequences are exactly the three things the first pass got wrong:
**square corners, translucency, no bevel or gradient.**

The first pass preserved the stock alpha silhouette (rounded, bevelled, fully opaque)
and only recoloured it — so the red slabs simply became *black rounded* slabs. The
fix below replaces the geometry, not just the hue.

## Approach: silhouette-preserving recolour, then real geometry

For **chrome without baked art** (buttons, panel backgrounds) the stock silhouette is
discarded and an ElvUI quad is drawn into the exact TexCoord region the XML samples:

- **`quad`** — flat sharp-cornered fill at `backdropfade` alpha + a rim whose source
  width is scaled down so ~1px lands on screen (the region is stretched to the button).
- **`quad_glyph`** — as above, but stamps back the baked-in glyph. Needed where an
  atlas cell contains a semantic icon on the button face (`128redbuttonpart2` carries a
  gold eye and a gold trash can). The glyph is selected by being **bright AND
  saturated**, which keeps the gold icon while rejecting the grey stone bevel — the
  bevel is bright but almost colourless, so a brightness-only test left stone fragments.
- **`panel`** — uniform fill at a fixed alpha for tiled `bgFile` textures.

For everything else the original silhouette-preserving transforms still apply:

- **`ramp`** — remap visible luminance onto `RAMP_LO..RAMP_HI`. Used for stone chrome
  (tabs, dialog borders, help frame) where the shape *is* the content.
- **`glow`** — keep luminance shape, retint hue. Required for `alphaMode="ADD"` layers
  and for glyphs that live in RGB with flat alpha (arrows, ticks, minimise X).
- **`dered`** — hue-targeted: recolour **only** red pixels, leaving the rest untouched.

## Coverage

The remaining work was not guessed: `build_worklist.py` resolves the winning archive
for all 70 `Interface\GlueXML\*` files in load order, extracts them, and scans them for
referenced `Interface\...` textures — producing a list of 95 textures still resolving to
stock art. The reskin now covers all six screens named in the objective:

| Screen | Reskinned chrome |
|---|---|
| **Login** | `Glue-Panel-Button-*`, `redbutton2x`, `BorderAlert`, `UI-Tooltip-*`, `Common-Input-Border`, fonts |
| **Realm list** | `UI-Character-{Active,InActive}Tab`, `UI-Character-ScrollBar`, `UI-QuestLogTitleHighlight`, `HelpFrame-*`, `Glues-TOS-TopRight`, `UI-SortArrow`, tooltips |
| **Char select** | `Glue-Panel-Button-*`, `128redbuttonpart2`, `Glue-CharacterSelect-Highlight`, `UI-PaidCharacterCustomization-Button`, tooltips, tabs |
| **Char create** | `Glue-Panel-Button-*`, `UI-RotationRight-Big-*`, `Arrow`, `CharacterCreate-LabelFrame`, tooltips |
| **Options** | `UI-OptionsFrame-{Active,InActive}Tab`, `UI-OptionsFrame-Spacer`, `UI-CheckBox-*`, `UI-SliderBar-*`, `UI-{Minus,Plus}Button-*`, dropdown arrows |
| **Dialogs** | `UI-DialogBox-{Background,Border,Header}`, `BorderAlert`, `UI-ChatInputBorder-*`, `UI-CheckBox-*`, buttons |
| **Tooltips** | `UI-Tooltip-{Background,Border}`, `ui-tooltip-border-maw{,Black}`, `Glue-Tooltip-{Background,Border}` |

## Deliverables

**83 textures** (`staging/root/Interface/...`), generated from the **live** archives:

- `Glues\Common\Glue-Panel-Button-{Up,Down,Disabled,Highlight,Glow,Up-Blue,Down-Blue,Highlight-Blue}.blp`
- `Glues\Common\Glues-BigButton-{Up,Down,Rays}.blp`, `Arrow.blp`, `redbutton2x.blp`
- `Glues\Common\Glue-Tooltip-{Background,Border}.blp`, `Glues-Splash` untouched
- `Tooltips\UI-Tooltip-{Background,Border}.blp`, `tooltips\{BorderAlert,Glue-Tooltip-Border,ui-tooltip-border-maw,ui-tooltip-border-mawBlack}.blp`
- `DialogFrame\UI-DialogBox-{Background,Border,Header}.blp`
- `PaperDollInfoFrame\UI-Character-{ActiveTab,InActiveTab,Tab-Highlight,ScrollBar}.blp`
- `OptionsFrame\UI-OptionsFrame-{ActiveTab,InActiveTab,Spacer}.blp`
- `QuestFrame\UI-Quest{LogTitleHighlight,TitleHighlight}.blp`
- `HelpFrame\HelpFrame-{TopLeft,Top,BotLeft,Bottom,BotRight}.blp`
- `Glues\Login\{Glues-TOS-TopRight,UI-BackArrow}.blp`, `Common\Common-Input-Border.blp`
- `Buttons\UI-CheckBox-*`, `UI-ScrollBar-*`, `UI-SliderBar-*`, `UI-Panel-Button-*`,
  `UI-{Minus,Plus}Button-*`, `UI-Panel-MinimizeButton-*`, `UI-SortArrow`,
  `ButtonHilight-Square`, `UI-Common-MouseHilight`,
  `UI-PaidCharacterCustomization-Button`
- `ChatFrame\UI-ChatInputBorder-{Left,Right}`, `ChatFrame{ExpandArrow,ColorSwatch}`, `UI-ChatIcon-ScrollDown-*`
- `Glues\CharacterSelect\{128redbuttonpart2,Glue-CharacterSelect-Highlight}.blp`
- `Glues\CharacterCreate\{UI-RotationRight-Big-Up,UI-RotationRight-Big-Down,CharacterCreate-LabelFrame}.blp`

**1 GlueXML override**: `GlueXML\GlueFontStyles.xml` — 31 colour swaps (gold `1.0,0.78,0` →
`#E5E3E3`; semantic green/red/yellow retuned to ElvUI's GOOD/BAD/NEUTRAL). Every font
name and attribute is preserved so `inherits` chains cannot break.

## Deliberately NOT changed

The dividing line: **chrome and navigation glyphs are reskinned; semantic content is preserved.**

- `generic.blp` (512×512) — supplies the edit-box pieces; the login edit boxes already
  render correctly dark, so touching it is risk without reward.
- `perks.blp` (1024×2048) — a shared multi-purpose widget kit (parchment panel, sliders,
  a green button, gold icons, "NEW" flash) used across screens; recolouring it wholesale
  would damage unrelated UI with no gain on the red-button goal.
- `charactercreate.blp` (5.5 MB) — serves as **both** the character-create screen
  background and button art, so a blanket recolour would wreck the backdrop.
- Semantic icons: `DialogAlertIcon`, `UI-Dialog-Icon-AlertNew`, `UI-GuildButton-PublicNote-Up`,
  race/class/gender art. Recolouring these loses meaning rather than removing chrome.
- Credits parchment (`Glues\Credits\Parchment1-8`, `Border1`) — a deliberate parchment
  scroll; darkening it reads as broken rather than themed.
- Splash art (`Glues-Splash-*`) and the `Glues-WoW-*Logo` wordmarks — branding, already
  customised by the user.
- 3D models (`.mdx`) and `RedButton*.blp` / `glue-panel-button-*-v2.blp` in `patch-A.MPQ`
  — the latter are dead assets, nothing references them.

## Backups

`G:\3.3.5a - Dev\Backups\elvui-glue-reskin-20260925-021650\` holds full copies of
`patch-Z.MPQ` and `patch-enUS-Z.MPQ` as they were before this change.

## Verification

- `apply_patch.py` — per archive: entry counts before/after, byte-for-byte round-trip of
  every written entry, and byte-for-byte identity of sampled pre-existing entries.
- `verify_result.py` — driven by the staging tree:
  1. **84/84** staged entries resolve from a `-Z` archive (highest load order)
  2. colour audit over every texture — **0** with stock crimson (1 intentional accent)
  3. no gold colour definitions remain in `GlueFontStyles.xml`
  4. **geometry audit** — for each button/panel, the four exact corners of the sampled
     TexCoord region must be *covered* (the stock art was transparent there, which is
     what produced the rounded look) **and** the fill probed inside the rim must equal
     `backdropfade` alpha (204/255 = 0.80). All pass.
  5. sampled pre-existing entries diffed against the backup archive — unchanged

The geometry audit is what distinguishes this revision from the first: it fails on a
rounded opaque slab even when the colour is perfectly correct.

