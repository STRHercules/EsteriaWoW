# Login, character creation, Character Select and portraits

[Back to the guide](README.md)

## Why GlueXML matters

Login, creator and Character Select load before normal addons. Their code is under
`Interface\GlueXML` inside the effective client archives, with visual assets in `Interface\Glues`,
`Interface\Loginscreen` and related namespaces. In-game AIO/ElvUI code is a different delivery path.

The active Lua/XML/TOC snapshot is in `sources/client-active/Interface/GlueXML`. It is preferable to an
older staging folder when documenting current behavior. [current-state.json](evidence/current-state.json)
records the supplying archive and SHA-256 for each extracted file.

## Login screen

The current [AccountLogin.lua](sources/client-active/Interface/GlueXML/AccountLogin.lua) and
[AccountLogin.xml](sources/client-active/Interface/GlueXML/AccountLogin.xml) implement the customized
background/scene, buttons and account controls. The script references
`Interface/Loginscreen/Background.blp` and `Interface\Loginscreen\Scene\`, loads model/scene data and has
remember-account/password dialog behavior.

Later login-persistence work preserved the account-name CVar path across the custom UI. Its deployment
helpers are retained in `sources/historical-plans/login-persistence-fix`. The current code and underlying
native persistence behavior should be tested together; copying a Lua label alone does not prove saved
login state.

Earlier interface work adapted a Retail-style Glue overlay and reskinned it using prepared fonts,
textures and XML/Lua patches. The source tools are included in
`sources/historical-plans/elvui-glue-reskin`: extraction/resolution, source worklist, font/texture
generation, patching, visual previews and result checks. [UI.md](sources/EsteriaWoW/UI.md) is an early
draft and must not be used as today's complete race list or deployment state.

Keep login assets and existing options/addon/realm dialogs in the effective stack. The source snapshot
does not include all original binary artwork; resolve those dependencies from the matching baseline.

## Creator identity and layout

The current files are:

- [CharacterCreate.lua](sources/client-active/Interface/GlueXML/CharacterCreate.lua)
- [CharacterCreate.xml](sources/client-active/Interface/GlueXML/CharacterCreate.xml)
- [CharacterInfo.lua](sources/client-active/Interface/GlueXML/CharacterInfo.lua)
- [GlueParent.lua](sources/client-active/Interface/GlueXML/GlueParent.lua)
- [GlueStrings.lua](sources/client-active/Interface/GlueXML/GlueStrings.lua)

The key mapping is:

`button ordinal → actual RaceID → file string → faction / class policy / portrait / native profile`

Vulpera's legacy ordinal 17 is actual race 20. Missing that exact metadata prevented native controls
from activating. Shared visible names such as Darkfallen/Earthen/Haranir cannot distinguish factions.

The modern additions expanded race/class enumeration while keeping the customized screen, added the
seven-column faction portrait layout, supplied bordered race art, names/lore/racial tooltips and
file-string background/fog/glow/ambience mappings. Creator-hidden races and male-only bodies are
explicit policies rather than fake gender models.

The creator separates selection from customization. First/Last Name fields remain hidden during race
selection and appear in customization. The action label says Customize. Rotation controls are centered
under the name fields; the final version keeps one smooth rotation pair using the incremented art.

Expanded control panels are split into balanced left/right columns toward the screen edges. Labels
are widened and every option resolves its matching descriptor. On leaving an expanded race, standard
Skin Color/Face/Hair Style/Hair Color/Features labels and selector IDs are restored; extra controls hide.
The Haranir→Draenei regression proved this reset is required.

## Dropdowns, previews and randomization

[CustomizationDropdown.lua](sources/EsteriaWoW/tools/character_ui/CustomizationDropdown.lua) and the active
creator implement selectable option lists. The installed dropdown code is embedded in the creator;
the tool's standalone Lua file is its build input, not a required separate active TOC entry.
Hover previews a value; leave/cancel restores the original;
click commits the choice. The native helper supplies full packed preview/restore state for expanded
profiles. Dropdown scrolling must not zoom the model.

Later dice repairs restored name and appearance randomizers and added independent last-name
randomization. Appearance randomization observes dependencies/class restrictions. Randomizing a
different control must not overwrite saved unrelated encoded values.

The maintained UI tools are:

| Tool | Responsibility |
| --- | --- |
| `creator_portrait_layout.py` | Faction grid, portrait placement and capacity |
| `character_ui_pack.py` | Creator/select appearance, labels and dropdown integration |
| `customization_layout.py` | Split control columns and positioning |
| `customization_buttons.py` | Dice/name/rotation button art and behavior |
| `customization_label_repair.py` | Reset labels on expanded→stock transitions |
| `patch_dropdown_zoom.py` | Dropdown wheel behavior |
| `two_names_client_pack.py` | First/last-name fields and compatibility |
| `race_touchup_pack.py` | Exact identity, select presentation, tooltips and language follow-ups |

Source and parser declarations are in [ALL_TOOLS.md](reference/ALL_TOOLS.md).

## Esteria Character Select (ECS)

ECS wraps the existing Glue roster instead of replacing its character bindings. It adds circular race
portraits, class/faction/zone presentation, notes, search, drag reorder, virtualized rows, tooltip and
client-side persistence while retaining enter/create/delete/options/addons/back behavior.

Active source files beginning `ECS_` are captured. The full developer references are
[CHARACTER_SELECT.md](sources/EsteriaWoW/docs/CHARACTER_SELECT.md) and
[CHARACTER_SELECT_HANDOFF.md](sources/EsteriaWoW/docs/CHARACTER_SELECT_HANDOFF.md); some historical status
paragraphs are superseded by the current audit.

| Module family | Responsibility |
| --- | --- |
| Constants / Schema | Layout/art constants and numeric race/class/faction presentation |
| Order / Data | Visual↔actual index mapping and normalized character tuples |
| Persistence / Notes | Sharded CVars, stored order, notes, draft/commit/cancel |
| Search / Anim / Modal | Filtering, pooled animation driver and modal ownership |
| Row / Roster | Decorated stock rows, virtual viewport, scroll/wheel/drag behavior |
| Tooltip / UI / Integrate | Screen controls, cursor placement and wrapped update binding |

The critical invariant is `button:GetID() == real character index`. Filtered/reordered visual position
must never become the index passed to select, enter or delete. Scroll offsets advance by whole rows.
The stock function binds first, Freeborn badges wrap it, then ECS decorates it.

Pure ECS Lua loads early. `ECS_Integrate.lua` loads after CharacterCreate.xml so it wraps the already
Freeborn-wrapped update. [GlueXML.toc](sources/client-active/Interface/GlueXML/GlueXML.toc) records the
actual load order.

ECS persistence uses bounded, sharded CVars because ordinary addon SavedVariables are unavailable in
Glue. Preserve the realm/character identity contract. Test order/notes after restart and after deletion
or realm switches, including degraded storage-capacity handling.

Later presentation fixes keep long names on one line, anchor tooltips beneath the cursor using a
consistent coordinate scale, use exact race identity for Mag'har/Skyborne portraits/names, reduce the
Vrykul preview size and update creator/select scrollbar placement.

## 100-character roster support

The source/patch policy allows up to 100 characters per realm, while ECS shows a smaller virtual
viewport. This is separate from 64 race-ID support.

Earlier scroll-child repairs call `UpdateScrollChildRect()` after height changes. Large-roster work also
coordinates XML/Lua button capacity, key/wheel routing and the preserved binary character-limit byte.
Sources and payloads are in `historical-plans/100-character-support`; do not apply an older select file
over the current ECS snapshot.

## Portrait pipeline

Supplied PNGs from `R:\Users\Zach\Pictures\Portraits` are included in `sources/Portraits`.
[portraits.json](evidence/portraits.json) records original paths, sizes and hashes.

The source directories distinguish Alliance/Horde/Custom art, including Mag'har, both Skyborne factions,
Mechagnome, Highmountain, both Earthen/Haranir factions and later creature portraits.

The process is:

1. Select the correct faction/gender image and preserve the original.
2. Crop/resize using the established portrait framing.
3. Apply the existing metal ring/alpha mask for creator buttons.
4. Encode the supported BLP palette/alpha/mip format.
5. Generate masked ECS art in its own namespace; its row border is handled by ECS.
6. Add character-frame race portraits and exact schema/file-string keys.
7. Stage and verify in both root/locale winning archives, then check framing in the client.

The core tools are [race_portrait_pack.py](sources/EsteriaWoW/tools/race_portrait_pack.py),
[derive_playable_race_portraits.py](sources/EsteriaWoW/tools/derive_playable_race_portraits.py) and
[creature_portrait_pack.py](sources/EsteriaWoW/tools/creature_portrait_pack.py). Race-specific packers
reuse them rather than inventing another art format.

The ECS tools are in `historical-plans/character-select-redesign/tools`, including `make_ecs_portraits.py`,
`check_artkeys.py`, `check_framing.py`, source/plate comparison, capacity measurement and deployment.
Several late portraits were generated after older art-completeness notes; use the current supplied
inputs and actual effective keys.

## Archive deployment

Patch both `Data\patch-Z.MPQ` and `Data\enUS\patch-enUS-Z.MPQ` when they contain the affected Glue file.
A root-only edit can be shadowed by locale. Use StormLib, current merge bases, verified backups and
entry readbacks. Close WoW/Eclipse before replacement and launch fresh afterward.

Check runtime layout and interactions at the user's resolution. Static Lua/frame-shim checks establish
binding/state behavior; they do not establish that the rendered artwork or tooltip looks right.
