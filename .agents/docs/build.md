# Build & tests

## Default Esteria server build

When a server build is requested, reuse the persistent `housing-build` container:

```powershell
powershell -NoProfile -File apps/docker/build-server.ps1
```

This selects `worldserver` and lets CMake/Ninja rebuild only changed sources and
their dependencies. Use `-Target authserver` or `-Target dbimport` only if that
application needs rebuilding. Use `-DryRun` to inspect Ninja's pending work without
compiling; pending CMake regeneration can prevent it from listing later steps.

Synchronize only the intended source changes into the builder before compiling.
Its source tree is separate from this checkout and contains integrated server
work; do not overwrite it wholesale. Keep `/azerothcore/build` and its configured
compiler/options to retain incremental objects. Do not clean, recreate the builder,
or run `docker compose build` for routine edits. Shared header changes can still
require broad recompilation; static modules still require archiving and linking.

Use a fresh configuration/full image build only for initial setup, a required
toolchain/configuration change, or demonstrated build-cache corruption. Explain
the reason before discarding existing artifacts. Building does not install,
package, or deploy the executable; follow the task's deployment scope separately.

## Initial native setup and tests

Out-of-source build is required (in-source is blocked).

```bash
mkdir -p build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=$HOME/azeroth-server -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DSCRIPTS=static -DMODULES=static
make -j$(nproc) && make install
```

C++20 required (`CMAKE_CXX_STANDARD 20`). Useful flags: `BUILD_TESTING=ON` (Google Test), `NOPCH=1` (disable precompiled headers). Full set in `conf/dist/config.cmake`. `compile_commands.json` is exported automatically.

Tests (Google Test, in `src/test/`): configure `-DBUILD_TESTING=ON`, then `ctest` or `./src/test/unit_tests` from the build dir.
