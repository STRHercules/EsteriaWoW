# Broken racials - standalone install

Four custom racials for the Broken player race (race 14), extracted from EsteriaWoW so another
AzerothCore 3.3.5a server can install them.

| ID | Spell | Type | Effect |
| --- | --- | --- | --- |
| 110001 | Salvager | Passive | +10 Engineering and Mining; repair costs reduced 10% |
| 110002 | Krokul Cunning | Passive | Enemies detect you 5 yards closer |
| 110003 | Fel-Scarred | Passive | +10 Shadow resistance; mana-drain and mana-burn effects on you are 10% weaker |
| 110004 | Echo of the Naaru | Active, 180 s cooldown | Restores 15% of maximum health over 10 s (5 ticks of 3%) |

## Contents

```
mod-broken-racials/                              drop-in module
  CMakeLists.txt
  src/loader.h
  src/broken_racials.cpp                         login grant, repair discount, Echo aura script
  src/BrokenRacialEffects.h
  src/BrokenRacialEffects.cpp                    shared math
  data/sql/db-world/updates/u_broken_racials_2026_10_05_00.sql
                                                 all world-DB data, idempotent
```

## Requirements

- AzerothCore 3.3.5a with modules enabled.
- A playable Broken race on **race id 14** (race mask `8192`). Change every `14` and `8192`
  together if yours differs (see "Different race id").
- Client `Spell.dbc` rows `110001`-`110004` with matching names, icons and tooltips. Esteria's
  patched client ships them; without them the racials still function but show no name or icon.
- The old copied Mag'har racials `20549`-`20552` must be free to remove: the login hook strips
  them from Broken characters.

## Install

1. Copy `mod-broken-racials/` into your server's `modules/` directory.
2. Apply the two core hooks below to `src/server/game/Spells/SpellEffects.cpp`.
3. Rebuild `worldserver`. CMake picks the module up automatically.
4. Start `worldserver`. The DB updater applies the module SQL to `acore_world` on first boot. To
   apply it by hand instead:

   ```
   mysql -u <user> -p acore_world < mod-broken-racials/data/sql/db-world/updates/u_broken_racials_2026_10_05_00.sql
   ```

5. Log in on a Broken character. Existing characters get the racials on login; new characters get
   them at creation, with Echo of the Naaru on the action bar.

## Core hooks

Fel-Scarred's mana-drain reduction lives in two core functions, `Spell::EffectPowerDrain` and
`Spell::EffectPowerBurn`. In both, directly after the resilience block and before the
`ModifyPower` call, add:

```cpp
    if (PowerType == POWER_MANA && unitTarget->IsPlayer()
        && unitTarget->ToPlayer()->getRace() == 14) // Broken race id
        power = CalculatePct(power, 90);
```

`Spell::EffectPowerDrain` shape:

```cpp
    if (PowerType == POWER_MANA)
        power -= unitTarget->GetSpellCritDamageReduction(power);

    int32 newDamage = -(unitTarget->ModifyPower(PowerType, -int32(power)));
```

`Spell::EffectPowerBurn` shape:

```cpp
    if (PowerType == POWER_MANA)
        power -= unitTarget->GetSpellCritDamageReduction(power);

    int32 newDamage = -(unitTarget->ModifyPower(PowerType, -power));
```

Everything else (login grant, repair discount, Echo of the Naaru scaling) is in the module.

## Different race id

Change these together:

- `BROKEN_RACE_ID` in `mod-broken-racials/src/broken_racials.cpp`
- the `14` in the two core hooks
- `8192` (the race-14 bit) and `race = 14` in the SQL file

## Uninstall

Delete the `spell_script_names` row for `110004`, the `playercreateinfo_spell_custom` rows for the
Broken race mask, the `skilllineability_dbc` rows `31459`-`31462`, the `skillline_dbc` row `792`,
the `skillraceclassinfo_dbc` row `1141` and the four `spell_dbc` rows `110001`-`110004`, then
rebuild without the module.

## Extraction notes

- SQL sections 1-3 are cloned from the EsteriaWoW pending migrations
  `rev_1788720000000000000.sql` and `rev_1788800000000000000.sql`; section 1 also carries the full
  base `spell_dbc` rows so the file works on a server that has never seen these spell ids.
- The racials are keyed to race 14 only. Esteria's Broken Alliance (24) and Broken Horde (27)
  variants do not get this set.
- Checked here: statement structure and 234 columns per spell row. Not built and not run against a
  live client or server.
