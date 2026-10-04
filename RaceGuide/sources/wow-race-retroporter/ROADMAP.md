# Roadmap

## Phase 1: Source architecture scaffold

- [x] Python CLI and project config
- [x] YAML race manifests and target race-ID registry
- [x] resumable pipeline state
- [x] online/local Retail source profile
- [x] targeted source/cache directory contract
- [x] `raceporter fetch` source-only pipeline surface
- [x] package exclusion for `sources/`, `cache/`, and `tools/`
- [x] Mag'har Orc reference manifest

## Phase 2: Retail discovery

- [ ] resolve selected Retail product/build from the online source
- [ ] pin actual build/build key into source manifests
- [ ] retrieve required race/customization DB2 tables
- [ ] resolve `retail_race_id` through race/model relationships
- [ ] normalize customization dependency graph
- [ ] write deterministic discovery JSON

## Phase 3: Targeted extraction

- [ ] resolve every required FileDataID
- [ ] fetch M2/SKIN/SKEL/ANIM/BLP dependencies only
- [ ] support online and local CASC backends through one interface
- [ ] preserve logical names when known
- [ ] hash and inventory source assets
- [ ] make `raceporter fetch maghar_orc` complete through `inventory`

## Phase 4: Mag'har model conversion

- [ ] NPC-first converted model test package
- [ ] M2Mod/FixTXID/MultiConverter adapters
- [ ] animation/skeleton handling
- [ ] texture/material normalization
- [ ] armor/attachment verification checkpoints

## Phase 5: Character customization

- [ ] normalize Retail options/choices/elements
- [ ] flatten minimum viable Mag'har customization set
- [ ] generate WotLK CharSections/hair/facial-hair inputs
- [ ] expand customization after minimum viable profile validates

## Phase 6: AzerothCore + GlueXML

- [ ] generate target ChrRaces/CharBaseInfo inputs
- [ ] generate `playercreateinfo*` SQL
- [ ] generate character-creation metadata/fragments
- [ ] validate race/class/gender matrix

## Phase 7: Generalize

- [ ] Highmountain Tauren manifest
- [ ] Kul Tiran manifest
- [ ] Mechagnome manifest
- [ ] Earthen manifest
- [ ] Dracthyr-specific design
- [ ] optional `raceporter fetch --all-races` discovery/fetch workflow
