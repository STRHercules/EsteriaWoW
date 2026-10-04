# AppearanceBuddy Global Eluna State Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:verification-before-completion to verify the runtime fix.

**Goal:** Create AzerothCore's missing global Eluna state so AIO server handlers and AppearanceBuddy can register and exchange messages.

**Architecture:** Initialize the world's `ElunaInfo` with the reserved global key and create its `Eluna` instance immediately after the Eluna script cache is loaded. Leave map-state creation unchanged; AIO will then load once in the world state (`map=-1`) and per-map scripts will continue to load normally.

**Tech Stack:** C++20, AzerothCore Eluna, CMake/Docker Compose.

**Spec:** Runtime evidence from AIO diagnostics: all loaded states reported `server=true main=false` for maps 530, 0, 1, 571, and 369; `World::_elunaInfo` has no initialization and no `sElunaMgr->Create` call exists for the world state.

## Global Constraints

- Preserve existing dirty work and database volumes.
- Modify only the core world initialization needed for the missing global state.
- Do not change SQL or client addon files.
- Verify the C++ style check, build, worldserver readiness, and AIO state initialization before claiming completion.

---

### Task 1: Add the global Eluna state

**Files:**
- Modify: `src/server/game/World/World.cpp:326-333`

**Interfaces:**
- Consumes: `sElunaConfig`, `sElunaLoader`, `sElunaMgr`, and `ElunaInfoKey::MakeGlobalKey`.
- Produces: `World::_elunaInfo` bound to the global state and a world `Eluna` instance that runs all global Lua scripts.

- [ ] **Step 1: Run the failing static check**

Run:

```powershell
$world = Get-Content -Raw 'src/server/game/World/World.cpp'
if ($world -notmatch 'MakeGlobalKey\(0\).*sElunaMgr->Create') { exit 1 }
```

Expected: exit 1 because the global state is currently absent.

- [ ] **Step 2: Add the minimal implementation**

Immediately after `sElunaLoader->LoadScripts();` in the existing `ELUNA` startup block, add:

```cpp
        _elunaInfo = { ElunaInfoKey::MakeGlobalKey(0) };
        sElunaMgr->Create(nullptr, _elunaInfo);
```

- [ ] **Step 3: Run the static check again**

Run the same PowerShell assertion. Expected: exit 0.

- [ ] **Step 4: Run the C++ style check**

Run:

```powershell
python apps/codestyle/codestyle-cpp.py
```

Expected: exit 0 with no errors for the changed file.

### Task 2: Build and verify the runtime

**Files:**
- Modify: the generated Docker worldserver image only; preserve Compose volumes.

**Interfaces:**
- Consumes: the patched `World.cpp` and existing Docker build configuration.
- Produces: a worldserver binary with a `map=-1` Eluna state and functioning AIO server hooks.

- [ ] **Step 1: Identify the configured build target**

Run `docker compose config` and inspect the `ac-worldserver` build/image configuration before invoking a build.

- [ ] **Step 2: Build only the worldserver target**

Use the repository's configured Docker build command; do not remove volumes or reset unrelated changes.

- [ ] **Step 3: Recreate only `ac-worldserver`**

Restart/recreate the worldserver with the patched image and preserve `ac-database` and all persistent volumes.

- [ ] **Step 4: Verify startup and AIO state**

Confirm `worldserver-daemon ready`, an AIO diagnostic line with `main=true map=-1`, no Lua startup errors, and a client `/ab` request producing AIO receive/send output.
