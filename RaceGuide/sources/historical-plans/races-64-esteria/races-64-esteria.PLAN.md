# races-64-esteria Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runtime-only `races-64-esteria` WarcraftXL extension that upgrades the existing Esteria 32-race foundation to 64 races without modifying `Wow.exe` on disk.

**Architecture:** Fork Dokman’s `MoreRaces.cpp` runtime patcher into the local WXL extension source tree. Replace stock-client validation with an Esteria signature plus exact patch-site fingerprints, preserve the existing Esteria table/name data, apply all writes through the existing page-protection and rollback path, and deploy the resulting x86 DLL into the client extension directory.

**Tech Stack:** C++20, MSVC Win32, WarcraftXL Plugin API v1, Win32 `VirtualAlloc`/`VirtualProtect`, Python standard-library PE/manifest verifier, CMake Visual Studio generator.

**Spec:** User request in this thread dated 2026-09-19; the live baseline is `R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Wow.exe`.

## Global Constraints

* Never write to `3.3.5a - Dev\Wow.exe`; all changes are runtime patches from the DLL.
* Require the `ESTERIA_CLIENT_FOUNDATION_V3` signature at VA `0x00DFE000` before any allocation or write.
* Require all eight original table references to equal `0x00DFE220`.
* Require `0x004CDA43 == 0x00DFE400`, clear size `0x100` at `0x004E1C34`, cleanup count `22` at `0x004E1E9B`, the stock six-byte branch at `0x004DFAF0`, and character limit `0x64` at `0x00464C4F`.
* Allocate `0x200` bytes for `64 * 2 * sizeof(uint32_t)` and copy the existing first `0x100` bytes before redirecting references.
* Copy all 32 existing name pointers from `0x00DFE400`; use the dummy fallback for IDs `28..63` and never overwrite the existing IDs `0..27`.
* Do not write `0x00464C4F`; preserve the independently configured character limit of 100.
* Preserve fingerprint failure, page-protection restoration, instruction-cache flush, and partial-write rollback behavior.
* Report `races-64-esteria` from `WXL_Query`, and keep the source/output path separate from the existing `wxl-races-patcher` DLL.

## Review Focus

* A stock or differently customized client must fail validation before `VirtualAlloc` or `VirtualProtect`.
* A client with the Esteria signature but one stale patch-site value must fail closed rather than partially patch.
* Existing table bytes and custom name pointers must be copied before redirection; IDs 28–63 must resolve to safe fallback pointers.
* A failed page-protection/write operation must roll back already-written sites and retain allocations if a dangling branch/pointer would otherwise result.
* The final DLL must be Win32 and export `WXL_Query` and `WXL_Load` while the client hash remains unchanged.

---

### Task 1: Add the contract verifier and extension identity

**Files:**
- Create: `3.3.5a - Dev/Extensions/races-64-esteria/verify_extension.py`
- Create: `3.3.5a - Dev/Extensions/races-64-esteria/wxl.json`

**Interfaces:**
- Consumes: the target client PE, the built DLL, and the extension manifest.
- Produces: a nonzero exit for missing/wrong artifacts and a zero exit only when the Esteria baseline, PE exports, Win32 machine type, plugin name, and manifest entry agree.

- [ ] Write the verifier first. Parse the PE section table with `struct`, map preferred VAs using the image base, and assert the signature, eight `0x00DFE220` references, name pointer, `0x100` clear size, `22` cleanup count, six-byte branch fingerprint, and `0x64` character limit. Parse the DLL export directory and assert `WXL_Query` and `WXL_Load`; scan ASCII strings for `races-64-esteria`; assert the manifest extension id and entry are `races-64-esteria` and `races-64-esteria.dll`.
- [ ] Run `rtk python "3.3.5a - Dev/Extensions/races-64-esteria/verify_extension.py" --client "3.3.5a - Dev/Wow.exe" --dll "3.3.5a - Dev/Extensions/races-64-esteria/races-64-esteria.dll" --manifest "3.3.5a - Dev/Extensions/races-64-esteria/wxl.json"` before the DLL/source exists and record the expected missing-artifact failure.
- [ ] Add a manifest whose extension id and DLL entry are `races-64-esteria` / `races-64-esteria.dll`, with no client patching step.

### Task 2: Implement the Esteria runtime fork

**Files:**
- Create: `R:\Users\Zach\Documents\GitHub\AzerothPlex\build\wxl-core\extensions\races-64-esteria\MoreRaces.cpp`

**Interfaces:**
- Consumes: `wxl/PluginApi.h` and the fixed build-12340 client addresses.
- Produces: `WXL_Query`, `WXL_Load`, and the runtime patch state used by the temporary WXL CMake build.

- [ ] Copy the upstream patch/rollback structure and replace stock constants with the Esteria constants in Global Constraints.
- [ ] Make `HasExpectedClientImage()` check the exact signature, all eight table references, the name pointer, clear size, cleanup count, the six-byte restriction fingerprint, and the untouched `0x64` character limit; return false on any mismatch.
- [ ] Allocate `0x304` bytes: `0x200` memory-table bytes, `0x100` name-table bytes, and one four-byte dummy fallback. Copy `0x100` bytes from `0x00DFE220`, copy 32 pointers from `0x00DFE400`, then set only IDs `28..63` to the dummy pointer.
- [ ] Keep the existing 25-byte restriction thunk and its relative-branch range checks, changing only the installed table/count/name values and removing the character-limit patch from the patch array.
- [ ] Set the plugin name and log tag to `races-64-esteria`; retain the upstream rollback behavior if any write or protection restore fails.
- [ ] Add a source-contract check to the verifier for the no-character-limit-write rule and the exact allocation/copy/fallback constants, then run it against the new source.

### Task 3: Build, deploy, and verify the runtime artifact

**Files:**
- Create: `3.3.5a - Dev/Extensions/races-64-esteria/races-64-esteria.dll`

**Interfaces:**
- Consumes: the WXL core source tree and Task 2’s extension source.
- Produces: the client-local runtime DLL and verification evidence; does not change the client executable.

- [ ] Configure an isolated temporary build with `cmake -S "R:\Users\Zach\Documents\GitHub\AzerothPlex\build\wxl-core" -B "C:\Users\Zach\AppData\Local\Temp\races-64-esteria-build-20260919" -A Win32 -DCLIENT_PATH="R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev"`.
- [ ] Build only target `races-64-esteria` with `cmake --build ... --config Release --target races-64-esteria`; let its post-build copy place the DLL under `Extensions\races-64-esteria`.
- [ ] Run the verifier against the deployed DLL, source, manifest, and client. Recompute the client SHA-256 and compare it with `Backups\races-64-esteria-20260919-001\Wow.exe`; run the repository C++ codestyle command only if it covers the new source path.
- [ ] Report static/build/package evidence separately from the unperformed live client launch and race-creation smoke test.
