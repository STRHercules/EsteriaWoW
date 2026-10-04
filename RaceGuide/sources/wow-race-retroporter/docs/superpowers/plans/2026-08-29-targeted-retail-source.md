# Targeted Retail Source Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use a test-first implementation workflow and verify the complete suite before completion.

**Goal:** Revise the scaffold from a repository-local full Retail client to a targeted online/local source architecture.

**Architecture:** `ProjectConfig` owns source/cache paths and loads a `RetailSourceConfig` from `sources/retail/build.yaml`. Online mode passes preflight without a client. Local mode validates an external CASC root. `fetch` runs the source-only stage subset. Raw source/cache paths are rejected by packaging.

**Tech Stack:** Python 3.12, PyYAML, pytest.

**Spec:** `docs/superpowers/specs/2026-08-29-targeted-retail-source-design.md`

## Tasks

- [x] Add failing tests for online defaults, local fallback, source/cache paths, fetch CLI, fetch stage subset, and package exclusions.
- [x] Add `RetailSourceConfig` and updated `ProjectConfig` fields.
- [x] Load `sources/retail/build.yaml` from project config.
- [x] Update preflight and doctor behavior for online/local modes.
- [x] Add `fetch` command and `FETCH_STAGE_NAMES`.
- [x] Update source-stage guidance for targeted FileDataID extraction.
- [x] Replace old `retail/` directory with `sources/retail/` and `cache/casc/` contracts.
- [x] Update Git ignore and package safety rules.
- [x] Update all root/reference/agent documentation.
- [x] Verify tests, CLI smoke checks, path safety, and final ZIP extraction.
