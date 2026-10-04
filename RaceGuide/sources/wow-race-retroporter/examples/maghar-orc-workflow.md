# Mag'har Orc Reference Workflow

1. Keep `sources/retail/build.yaml` in the default `mode: online`, or configure an optional local CASC source.
2. Run `raceporter doctor`.
3. Run `raceporter fetch maghar_orc --dry-run`.
4. Implement/enable the Retail discovery backend and resolve Retail race ID `36`.
5. Follow race -> ChrModel -> customization relationships rather than guessing model filenames.
6. Fetch only the required DB2 and FileDataID dependency closure into `sources/retail/`.
7. Verify the per-race manifest and inventory are pinned to one Retail build.
8. Copy/stage source files into `workspace/` for model conversion. Never modify the source cache in place.
9. Test the converted Mag'har model as an NPC before character-creation integration.
10. Flatten a minimum viable customization set, then generate WotLK DBC, AzerothCore SQL, and GlueXML outputs.
