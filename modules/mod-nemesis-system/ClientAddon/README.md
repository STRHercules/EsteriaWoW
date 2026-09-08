# Client Addon

Copy the `NemesisTracker` folder into your WoW 3.3.5a `Interface/AddOns/` directory.

`NemesisTracker` now embeds the Ace3 libraries it uses, so no separate `Ace3` addon install is required.

Slash commands:

- `/nemesistracker`
- `/ntrack`
- `/ntrack sync`

Current status:

- receives `Nemesis` addon payloads from `mod-nemesis-system`
- supports chunk reassembly, snapshot ingest, and upsert/remove handling
- shows a standalone window with a live nemesis list
- includes a zoomable and pannable placeholder map canvas
- prints waypoint coordinates for the selected nemesis

The current map canvas is a first-pass plotting surface. It does not yet render real zone textures or normalized zone metadata.
