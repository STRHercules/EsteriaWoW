# Race Manifest

Each target race has one YAML file under `races/`.

Required identity fields:

```yaml
slug: maghar_orc
display_name: "Mag'har Orc"
retail_race_id: 36
target_race_id: 45
faction: horde
base_race: orc
```

`retail_race_id` is used only to discover source records from the selected Retail build. `target_race_id` is the WotLK/AzerothCore identity and must obey the project's race-ID policy.

The global Retail source product/build is configured in `sources/retail/build.yaml`, not duplicated as a local-client path inside every race manifest.

A race manifest may supply discovery hints and required DB2 table families:

```yaml
source:
  model_hints:
    - "Orc-derived model; inspect customization materials/geosets first"
  db2_tables:
    - ChrRaces
    - ChrRaceXChrModel
    - ChrModel
    - ChrCustomizationOption
    - ChrCustomizationChoice
    - ChrCustomizationElement
```

Hints guide discovery but do not override actual Retail data relationships.
