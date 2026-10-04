# Race Retroporter Scaffold Implementation Plan

> **For agentic workers:** execute changes test-first and keep source acquisition, conversion, generation, and packaging boundaries separate.

**Goal:** Build the initial repository scaffold for targeted Retail race acquisition and WotLK/AzerothCore retroport automation.

**Architecture:** Python 3.12 orchestrates YAML configuration, a CDN-first Retail source profile, optional local CASC fallback, per-race source caches, external converter adapters, resumable state, validation, and safe package assembly.

**Tech Stack:** Python 3.12, PyYAML, pytest, Windows external WoW modding tools.

**Spec:** `docs/superpowers/specs/2026-08-29-race-retroporter-design.md`

## Completed scaffold tasks

- [x] Create root documentation and agent operating rules.
- [x] Create `sources/retail/build.yaml` with online default and local fallback.
- [x] Create targeted DB2/race source-cache directories and disposable CASC cache.
- [x] Create project/race/tool configuration and race-ID registry.
- [x] Create Python config models that resolve online/local source settings.
- [x] Create stable full pipeline and source-only fetch stage subset.
- [x] Create CLI commands: doctor, fetch, plan, build, status, reset.
- [x] Make online preflight independent of a local Retail installation.
- [x] Keep local CASC validation when `mode: local` is selected.
- [x] Make `sources/`, `cache/`, and `tools/` package-unsafe.
- [x] Create Mag'har Orc reference manifest with Retail ID 36 and target ID 19.
- [x] Add tests covering config, source modes, fetch stages, state, CLI, and package safety.
- [x] Document Retail DB2 discovery, model conversion, customization flattening, AzerothCore, GlueXML, and packaging boundaries.
