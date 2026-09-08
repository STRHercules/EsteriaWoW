# Changelog

## 0.3.1 - 2026-04-05

- added `character_nemesis_monthly_kills` tracking so websites can build monthly nemesis kill leaderboards directly from the characters database

## 0.3.0 - 2026-04-04

- fixed companion addon `V2:CHUNK` reassembly so larger bootstrap and upsert payloads are rebuilt correctly client-side
- added non-rank-5 live addon upsert broadcasts after nemesis promotion so trackers receive new sightings sooner
- expanded addon zone and texture mapping for real world map tile rendering across more zones and common subzones
- refactored the companion addon into modular files for core bootstrap, data/state, communication, lifecycle, and UI concerns

## 0.2.0 - 2026-03-22

- reworked the companion addon around an AceDB-backed local cache
- replaced player-safe full snapshot sync with filtered V2 bootstrap flow
- added addon sighting report validation and persisted last-seen nemesis locations
- restricted full addon sync to GM use only
- added peer sync scaffolding for guild, party, raid, and public sharing scopes
- updated tracker UI to show stale state, source, and refresh-based behavior
