# Tools

The project is an orchestrator. It should use specialized WoW tools through adapters rather than reimplement every binary format.

## Source acquisition

### WoW.Export

Useful for browsing Retail data, model preview, dependency discovery, and targeted export. Online-capable workflows are preferred because they remove the requirement for a repository-local Retail install.

Expected adapter role:

```text
discover
extract
```

### CASC backend

A programmatic CASC/CDN backend is the long-term preferred source adapter for reproducible automation. The backend may be implemented with a suitable CASC/TACT library or delegated to a tool that supports online Retail builds.

Required logical capabilities:

```text
resolve Retail build
retrieve DB2 by FileDataID/name
retrieve arbitrary FileDataID
cache downloaded payloads
support local CASC as an alternate byte source
```

### CASCExplorer

Useful as an assisted/manual fallback when working from a local CASC installation. It should not be a mandatory dependency for online source mode.

## Model retroport tools

### M2Mod

Used for modern M2 inspection, M2I conversion/rebuild, skin-profile handling, and model surgery checkpoints.

### FixTXID / MultiConverter

Used in established modern-to-WotLK retroport workflows to normalize model features and produce 3.3.5-compatible model data.

### Blender

Optional manual checkpoint for geometry, skin-profile, geoset, attachment, or mesh corrections that cannot be safely automated.

## DBC and package tools

### WDBX Editor / compatible DBC tooling

Useful for inspection and validation. The project should eventually generate deterministic record inputs without requiring manual editing for every race.

### Ladik's MPQ Editor / compatible MPQ tooling

Used only at final 3.3.5 package assembly. MPQ tools have nothing to do with Retail source acquisition because modern Retail uses CASC.

## Tool policy

- Tool binaries stay under `tools/` or another configured local path and are ignored by Git.
- Adapters log exact command lines and versions.
- Source adapters write raw data to `sources/` and temporary bytes to `cache/`.
- Converters consume copies/staging data under `workspace/`.
- No converter may mutate source caches or a local Retail installation in place.
