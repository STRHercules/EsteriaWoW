# Upgrade from 0.1.0 or 0.1.1 to 0.1.2-preview

These instructions apply only to the supported stock core revision `e1823bb2db751a7cc0a90a8543e778449ebf7d84` with the previous module core patch already applied. Modified cores need a reviewed adaptation. Do not apply the full core patch twice.

1. Back up the core, module, configuration, databases and client archives. Preserve the working worldserver image/binary and previous module version for rollback. Stop the worldserver before activation.
2. Update this repository in `modules/mod-adaptive-autoattack` to `v0.1.2-preview`. Keep that directory name. Preserve local edits for review rather than overwriting them.
3. From the core root, check and apply the incremental patch:

```bash
git apply --check modules/mod-adaptive-autoattack/patches/upgrade-0.1.1-to-0.1.2.patch
git apply modules/mod-adaptive-autoattack/patches/upgrade-0.1.1-to-0.1.2.patch
```

4. Rebuild the worldserver with the updated module and activate the new binary/image. Verify the startup message includes `preview 0.1.2; native Auto Shot`.
5. Test bows, guns, crossbows, thrown weapons, wands, stopping attacks, melee/ranged transitions and normal equipment restrictions. Test Hunter talents that your characters actually know before declaring their interactions verified.

No SQL or client-record changes are introduced by 0.1.2 over 0.1.1. Do not rerun the original INSERT SQL. Clients already using 0.1.1's corrected tooltips need no patch replacement. Clients on 0.1.0 still need the separately documented tooltip correction; the client builder refuses an already-installed version, so preserve current patches and regenerate from your pre-installation archives with unrelated later changes merged first.

Rollback: restore the prior core/module source together with the prior working binary/image. The database and client can stay as they were before this update. Do not remove the module alone while its core integration is still compiled in.
