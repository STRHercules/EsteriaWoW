# Installation on an existing AzerothCore server

Requires your running AzerothCore setup, its existing build environment, your own 3.3.5a build 12340 client, Git and Python 3.10+. No second server is required by the module, though testing separately is recommended. No core edits are required. Upgrading an older version? Use [the migration guide](UPGRADE-0.2.0.md) instead.

## 1. Back up

Save your source changes, configuration, world/character database backups, existing binaries or Docker images, and client patch archives. Record your current core revision. Tested revision: e1823bb2db751a7cc0a90a8543e778449ebf7d84; do not reset your server to it and discard local work.

## 2. Install the module

From your AzerothCore source root:

```bash
git clone https://github.com/CWO4PapaBear/Auto-Attack-Forever.git modules/mod-adaptive-autoattack
python3 modules/mod-adaptive-autoattack/tools/prepare_server.py --core .
```

The installation folder must use that name. The check never edits files; it detects missing hooks and old integration symbols but is not a complete compatibility test. Do not install mod-ranged-autoattack alongside it.

## 3. Check reserved IDs

Run in your world database. Both results must be empty on a fresh installation:

```sql
SELECT Id FROM spell_dbc WHERE Id BETWEEN 970100 AND 970102;
SELECT ID, Spell FROM skilllineability_dbc WHERE ID BETWEEN 970100 AND 970102 OR Spell BETWEEN 970100 AND 970102;
```

Resolve collisions rather than overwriting unrelated records. The included SQL uses INSERT and is intended to run once. Existing users should not repeat it.

## 4. Build and configure

Use your existing AzerothCore reconfigure/build/install workflow with modules enabled. For an existing native CMake build directory, replacing the example paths:

```bash
cmake -S /path/to/azerothcore -B /path/to/existing-build -DMODULES=static
cmake --build /path/to/existing-build --parallel 2
cmake --install /path/to/existing-build
```

Keep your existing CMake options and installation prefix. Adjust parallel jobs for available memory. Docker users must rebuild the worldserver image through their existing Compose setup, then recreate that service; native build commands do not update a Docker image. Service names and commands depend on your deployment.

Apply data/sql/db-world/2026_09_14_00_adaptive_autoattack.sql once through the normal module database updater. If your setup requires a separate db-import image, rebuild/run that updater first. Do not both manually import and rerun the same SQL via the updater. Copy conf/adaptive_autoattack.conf.dist to your deployed etc/modules/adaptive_autoattack.conf and leave AdaptiveAutoAttack.Enable = 1. Restart the new worldserver after installation and database update.

## 5. Generate client patches

From the module directory, using your own unpatched client and a new output directory:

```bash
python3 tools/build_client.py --client "/path/to/WoW-3.3.5a" --output "/path/to/new-client-patches" --locale enUS
```

On Windows use `python` instead of `python3` if needed. The builder preserves unrelated entries from existing Z archives and writes only to the output directory. It rejects reserved-ID collisions and cannot update an already-installed version automatically.

## 6. Install client files

Close WoW. Back up Data/patch-Z.MPQ and Data/enUS/patch-enUS-Z.MPQ (substitute your locale). Copy the generated Data directory into the client. Both base and locale archives must match. Copy client-addon/AdaptiveAutoAttack to Interface/AddOns and enable it for dynamic Blizzard action-bar icons. Fully restart WoW and log in.

## 7. Verify

The log should contain `no-core prototype 1; stock wand timing` (the tested source marker). Auto Melee and Auto Ranged appear in General. Test each weapon type your class can equip, with ammunition where required. Verify repeated attacks, right-click and hotbar starts, cancellation, melee switching and return to ranged distance. Wands use stock startup timing. The module grants no weapon proficiencies, equipment permissions or Hunter talents.

To disable, set AdaptiveAutoAttack.Enable = 0 and restart. Learned controls and client labels remain; restore your backups for complete removal. Version 0.2.0 requires no core patch to undo. See [validation](VALIDATION.md) for remaining compatibility checks.
