# Troubleshooting

## `doctor` says local Retail CASC is missing

Check `sources/retail/build.yaml`. If you intended the normal online workflow, use:

```yaml
mode: online
```

If you intentionally selected `mode: local`, set `local_client_root` to a valid Retail CASC installation containing `Data/` and build/config metadata.

## Online mode works in preflight but `fetch` blocks at discover

That is expected in the current scaffold until a real online Retail CDN/DB2 discovery adapter is implemented. `fetch --dry-run` shows the intended source stages without pretending bytes were downloaded.

## A race source cache mixes files from different builds

Do not continue conversion. Archive/delete the affected `sources/retail/races/<race>/` cache and clear the race's pipeline state, then re-fetch against one pinned build.

## Conversion tool is missing

Update `config/tools.yaml` or place the required executable under the configured `tools/` path. Source fetching and conversion-tool readiness are reported separately.

## Raw Retail assets appear in a package staging set

Treat this as a packaging bug. `sources/` and `cache/` are never package-safe paths.
