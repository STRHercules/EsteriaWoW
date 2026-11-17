# Server data snapshot: 2026-11-17

`esteria-dbc-20261117.tar.gz` contains `dbc/` and `dbc-continuations/` from the working
Esteria realm's data directory. It contains no client executable, models, textures,
accounts or characters. `manifest.json` records archive and individual file hashes.

Continuations supply additional display, model and spell rows, including Incarnations.
The matching public database overrides are installed by
`zzzz_20261117030000000_server_dbc_reference.sql`. Binary DBC files and SQL overrides
are both required: neither alone describes the effective server data.
The `zzzz_` filename applies this snapshot after legacy module updates, which
otherwise overwrite or collide with the newer reference rows.

The standalone Compose stack installs pinned upstream v20.0 maps/vmaps/mmaps and
this DBC snapshot through `tools/server_install/prepare_data.py`. The upstream
archive SHA-256 comes from GitHub's immutable v20.0 release asset digest.

This supplies stock terrain and custom race/spell/display definitions. Extra
ported worlds and retail housing neighborhoods need matching client terrain/model
data. Server geometry for Housing/Garrison is not supplied by the upstream archive;
fixed-Z prototypes tolerate its absence with collision/pathing limits. Housing and Garrison remain
off by default. The matching extended client is a separate distribution.

To refresh this snapshot, capture `dbc/` and `dbc-continuations/` from the intended
server revision, regenerate all hashes, and export its public overrides with
`tools/server_install/export_reference_data.py`. Publish the archive, SQL and
manifest together, and bump the snapshot-specific data volume key in
`compose.server.yml`. Do not replace these files with a raw client extraction or
export any authentication or character data.
