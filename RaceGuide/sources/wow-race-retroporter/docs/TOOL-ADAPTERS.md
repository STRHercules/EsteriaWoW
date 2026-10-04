# Tool Adapter Contract

External tools and libraries must be wrapped behind narrow adapters.

## Source adapters

Online and local source backends should expose the same logical operations:

```text
resolve_build
fetch_db2
resolve_file
fetch_file
```

Online mode may use a CDN/CASC-capable library or WoW.Export integration. Local mode may use the same library against a local CASC installation or an assisted CASC tool.

Source adapters must:

1. pin/record the actual Retail build;
2. fetch only requested dependencies;
3. write temporary transfer data under `cache/casc/`;
4. write durable raw race inputs under `sources/retail/`;
5. log tool/backend versions and actions;
6. never mutate a local Retail installation.

## Conversion adapters

Converters consume copied/staged data under `workspace/`, never `sources/` in place. Each adapter must report inputs, outputs, command/version metadata, and validation results.
