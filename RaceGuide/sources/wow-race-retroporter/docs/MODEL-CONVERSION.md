# Model Conversion

Model conversion starts only after `fetch` and `inventory` have produced a complete, build-pinned source cache.

Expected raw dependencies can include:

- `.m2`
- `.skin`
- `.skel`
- external `.anim`
- `.blp`
- customization child models/materials

Converters operate on staging copies under `workspace/extracted/` and write WotLK-compatible results under `workspace/converted/`.

The established tool boundary may include FixTXID, M2Mod/M2I, Blender checkpoints, skin-profile/LOD fixes, and MultiConverter. The project should log exact tool versions and never overwrite the original `sources/retail/races/<race>/` files.

Test a converted model as an NPC before wiring it into playable-race DBC and GlueXML behavior.

A structurally valid converted M2 is not automatically valid player geometry for build 12340. Modern Retail player models can retain submesh/geoset groups that the Wrath character system never selects, producing partially or mostly invisible characters even when the M2, SKIN, textures, and animations all load. When Retail declares the target race as a fallback-model race, prefer the validated Wrath-HD fallback geometry for the first playable integration and apply the Retail race-specific materials/customization art through legacy DBCs. Treat direct Retail geometry as experimental until its required modern geosets have been explicitly flattened or remapped to Wrath-visible groups.
