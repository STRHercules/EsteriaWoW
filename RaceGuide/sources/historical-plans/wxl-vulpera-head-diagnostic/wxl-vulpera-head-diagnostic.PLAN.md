# WXL Vulpera Head Diagnostic Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reversible WarcraftXL extension that logs the Vulpera head-slot dispatch without changing rendering.

**Architecture:** The extension installs one chainable detour at `M2.CharModelSlotDispatch` (`0x004F2640`), a seam already used by WarcraftXL's own character-model feature. Its `__fastcall` thunk remaps race 20's internal head slot (0 in this client build) to a client-only display clone, then forwards all arguments unchanged.

**Tech Stack:** C++20, MSVC x86, WarcraftXL Plugin API v1, Python standard library verifier.

**Spec:** `.agents/plans/wxl-vulpera-head-diagnostic/wxl-vulpera-head-diagnostic.REQUIREMENTS.md`

## Global Constraints

* Build for x86 and client build 12340 only.
* The hook is diagnostic-only: it must not write renderer state or alter arguments.
* Deployment is local under `3.3.5a - Dev/Extensions/wxl-vulpera-head-diagnostic/`.

---

### Task 1: Create the loadable diagnostic extension

**Files:**
- Create: `3.3.5a - Dev/Extensions/wxl-vulpera-head-diagnostic/wxl-vulpera-head-diagnostic.cpp`
- Create: `3.3.5a - Dev/Extensions/wxl-vulpera-head-diagnostic/wxl.json`

**Interfaces:**
- Consumes: `WXL_Api::HookAttach`, `WXL_Api::Log` from `wxl/PluginApi.h`.
- Produces: exported `WXL_Query()` and `WXL_Load()` and a manifest pointing at the resulting DLL.

- [ ] Define the chained `__fastcall` trampoline and detour signatures as `void(void*, void*, uint32_t, void*, uint32_t)`, preserving the EDX slot between the receiver and stack arguments.
- [ ] Filter `cmo + 0x18` for race 20 and model slot 0, replace only the first display-ID DWORD with the client-only clone when mapped, then invoke the original unchanged.
- [ ] Attach the detour to `0x004F2640` and refuse to load when the API/client-build versions do not match.

### Task 2: Verify the built artifact

**Files:**
- Create: `3.3.5a - Dev/Extensions/wxl-vulpera-head-diagnostic/verify_extension.py`
- Test: `3.3.5a - Dev/Extensions/wxl-vulpera-head-diagnostic/verify_extension.py`

**Interfaces:**
- Consumes: the built DLL and `wxl.json` manifest.
- Produces: nonzero exit if the PE exports or manifest entry are wrong.

- [ ] Parse the DLL's PE export table using `struct` and assert it exports `WXL_Query` and `WXL_Load`.
- [ ] Assert the manifest entry equals `wxl-vulpera-head-diagnostic.dll`.
- [ ] Run the verifier after compiling with MSVC x86.
