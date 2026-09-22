# Upgrade to 0.2.0

Back up source, module, binaries/images, configuration, databases and client patches. Keep the patch from the version actually installed.

1. Remove only the old module integration from CombatHandler.cpp, SpellHandler.cpp, Unit.cpp and Spell.cpp. On the exact supported baseline, check reversal of your installed version's patch first:

```bash
git apply --reverse --check modules/mod-adaptive-autoattack/patches/azerothcore-e1823bb.patch
```

Only if the check passes:

```bash
git apply --reverse modules/mod-adaptive-autoattack/patches/azerothcore-e1823bb.patch
```

The historical full patch bundled here matches 0.1.2. For older or adapted integrations use the corresponding old patch. If reversal fails, review the four files manually; do not force it or discard unrelated changes. Do not reset databases.

2. Update the module and run the read-only check from the core root:

```bash
python3 modules/mod-adaptive-autoattack/tools/prepare_server.py --core .
```

3. Reconfigure, rebuild and install using your existing server build process. Stop the worldserver for deployment and restart the new build. Never run both old core callbacks and new hooks.
4. Keep your configuration, existing three spell records, General-tab mappings, client patches and addon. Do not rerun the original INSERT SQL or run the client generator against an already patched client. No new client data or database changes are required.
5. Test all weapon types, starts, stops and melee/ranged transitions. Stock wand startup timing is intentional.

The startup log retains `no-core prototype 1; stock wand timing` to preserve exact tested source. Rollback requires restoring the previous module, matching core integration and binary together; this upgrade does not require database rollback.
