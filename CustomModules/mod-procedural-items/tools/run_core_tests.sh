#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${TMPDIR:-/tmp}/mod-procedural-items-tests"
mkdir -p "$BUILD_DIR"
g++ -std=c++20 -Wall -Wextra -Wpedantic \
  -I"$ROOT/src" \
  "$ROOT/tests/test_core.cpp" \
  "$ROOT/src/core/IdPool.cpp" \
  "$ROOT/src/core/AppearanceCatalog.cpp" \
  "$ROOT/src/core/ItemGenerator.cpp" \
  -o "$BUILD_DIR/test_core"
"$BUILD_DIR/test_core"
