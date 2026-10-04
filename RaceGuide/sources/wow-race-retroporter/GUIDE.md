# Operator Guide

## 1. Install Python

Use Python 3.12 or newer supported by the project.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## 2. Choose the Retail source

Edit:

```text
sources/retail/build.yaml
```

### Recommended: online

```yaml
mode: online
product: wow
region: us
locale: enUS
build:
  version: auto
  build_key: auto
```

This mode is designed to retrieve only required race dependencies from Retail CDN/CASC data. No local Retail install is required by preflight.

### Optional: local/offline

```yaml
mode: local
product: wow
region: us
locale: enUS
build:
  version: auto
  build_key: auto
local_client_root: D:/Games/World of Warcraft
```

The local path must look like a CASC installation with `Data/` and build/config metadata. The project reads it but does not convert in place.

## 3. Configure external tools

Edit `config/tools.yaml` and place any local converter utilities under `tools/`, or update their executable paths.

```powershell
raceporter doctor
```

In online mode, `doctor` should report that a local CASC source is not required. Missing conversion tools are reported separately.

## 4. Configure the race

Race definitions live in `races/`.

The reference race is:

```text
races/maghar_orc.yaml
```

Verify the source and target identities are intentionally distinct:

```yaml
retail_race_id: 36
target_race_id: 45
```

## 5. Fetch source data

Preview source acquisition:

```powershell
raceporter fetch maghar_orc --dry-run
```

The source-only pipeline is:

```text
preflight -> discover -> extract -> inventory
```

When adapters are implemented, successful fetch output belongs under:

```text
sources/retail/db2/
sources/retail/races/maghar_orc/
```

The source race directory should become self-contained enough that conversion does not require a full Retail client.

## 6. Inspect the dependency inventory

Before model conversion, confirm the source cache records:

- actual Retail build/build key;
- race/model/customization DB2 relationships;
- required FileDataIDs;
- model, skin, skeleton, animation, and texture dependencies;
- male/female model separation;
- hashes or other stable integrity metadata.

Do not proceed from an incomplete inventory.

## 7. Run the complete pipeline

Preview first:

```powershell
raceporter build maghar_orc --dry-run
```

Then execute implemented stages:

```powershell
raceporter build maghar_orc
```

The scaffold intentionally blocks at stages whose real adapters have not been implemented yet.

## 8. Resume safely

State is stored per race in:

```text
workspace/state/<race>.json
```

Use:

```powershell
raceporter status maghar_orc
raceporter build maghar_orc
```

Completed stages are skipped. Use `--force` only when intentionally rebuilding a stage against the same pinned source.

## 9. Re-fetch or change Retail builds

If changing the source build, treat that as a source invalidation event. Clear or archive the affected race's source cache and pipeline state before mixing assets from two Retail builds.

Do not silently update a cached race from a newer build.

## 10. Package only derived output

Raw data under `sources/`, `cache/`, and `tools/` is not package-safe. Final package staging should draw only from validated `workspace/converted/` and `workspace/generated/` content.
