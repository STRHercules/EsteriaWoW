# WXL Vulpera Head Diagnostic Requirements

Goal: add a client-local, no-op WarcraftXL diagnostic extension that records the live Vulpera
head-slot dispatch when character equipment is attached.

Constraints:

* Target only the build-12340 fixed address `0x004F2640` (`M2.CharModelSlotDispatch`).
* Observe only race 20 dispatches for internal model slot 0 (head in this client build).
* Preserve the core's documented `__fastcall(cmo, edx, modelSlot, itemData, postFlag)` ABI and always forward the call unchanged.
* Do not edit `Wow.exe`, MPQs, SQL, server state, or client rendering data.
* Emit one descriptor dump per character-model instance to the WarcraftXL log.
* Verify the built DLL exports `WXL_Query` and `WXL_Load` and that its manifest names the DLL.
