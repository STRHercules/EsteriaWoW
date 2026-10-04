# Sethrak Client Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make race ID 15 load and display as Sethrak in the launched `3.3.5a` client using the re-homed donor assets.

**Architecture:** Keep race ID 15 and the server compatibility alias stable, but make all client-facing Glue keys and labels Sethrak. Build a real packed `Patch-A.MPQ` from the module's exploded source tree, preserve the existing client archive as a recoverable backup, and deploy the new archive to the exact client `Data` directory.

**Tech Stack:** WotLK 3.3.5a MPQ assets, Lua/XML Glue UI, binary DBC files, PowerShell, and the repository's existing MPQ tooling.

**Spec:** Current user request: fully implement Sethrak and make it present in `3.3.5a/`.

## Global Constraints

- Race ID 15 remains the compatibility slot.
- Sethrak client assets use `Character\\Sethrak` and `Sound\\character\\Sethrak` namespaces.
- Do not install the original Draenei-overwrite donor archive unchanged.
- Preserve the existing packed client archive through a backup before replacement.
- Do not build AzerothCore unless separately requested; this task targets client packaging and source assets.

### Task 1: Complete client Glue mappings

**Files:**
- Modify: `modules/mod-worgoblin-high-elf/data/patch-A.MPQ/Interface/GlueXML/GlueStrings.lua`
- Modify: `modules/mod-worgoblin-high-elf/data/patch-A.MPQ/Interface/GlueXML/GlueParent.lua`

- [ ] Replace the playable race 15 Ogre description keys and text with Sethrak keys and text.
- [ ] Map Sethrak ambience and lighting/background selection through the existing Orc fallback assets.
- [ ] Check that no client-facing Ogre key remains for race 15.

### Task 2: Build and deploy the client archive

**Files:**
- Read: `modules/mod-worgoblin-high-elf/data/patch-A.MPQ/`
- Deploy: `3.3.5a/Data/Patch-A.MPQ`
- Create backup beside the existing client archive.

- [ ] Identify and use an available MPQ packer that preserves all source paths.
- [ ] Pack the complete exploded patch tree into a staging archive.
- [ ] Verify the staging archive contains Sethrak models, DBCs, Glue files, and voices.
- [ ] Back up the existing client archive and replace it with the staging archive.

### Task 3: Verify the installed payload

**Checks:**
- [ ] Confirm the deployed archive exists at the launched client's `Data/Patch-A.MPQ` path.
- [ ] Confirm archive timestamp/hash differs from the old Ogre archive.
- [ ] Confirm the source and deployed payload contain Sethrak Glue keys and no stale race-15 Ogre UI keys.
- [ ] Report live-launch limitations separately from static packaging evidence.
