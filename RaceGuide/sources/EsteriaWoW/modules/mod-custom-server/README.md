# mod-custom-server

`mod-custom-server` is the primary home for server-specific custom gameplay
and infrastructure that can be implemented through AzerothCore's module APIs.

Prefer hooks and module APIs over direct modifications to AzerothCore core
source. Core changes should be reserved for functionality that cannot be
implemented cleanly through existing hooks.

The root `modules/CMakeLists.txt` discovers this module automatically. Put
future C++ sources under `src/`, configuration defaults under `conf/`, and
module SQL under `data/sql/db-auth/`, `data/sql/db-characters/`, or
`data/sql/db-world/` as appropriate.

This starter module intentionally contains no gameplay behavior.
