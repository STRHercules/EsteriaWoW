# Retail DB2 Discovery

Modern race discovery should follow Retail data relationships rather than filename guesses.

## Core identity/model tables

Start with:

- `ChrRaces`
- `ChrRaceXChrModel`
- `ChrModel`

The selected race manifest provides `retail_race_id`. Discovery follows that ID to the applicable male/female character model records and their file references.

## Customization tables

The exact table set varies by Retail build, but the discovery layer should understand the families represented by:

- `ChrCustomizationOption`
- `ChrCustomizationChoice`
- `ChrCustomizationElement`
- `ChrCustomizationReq`
- `ChrCustomizationReqChoice`
- `ChrCustomizationGeoset`
- `ChrCustomizationSkinnedModel`
- `ChrCustomizationMaterial`
- `ChrCustomizationBoneSet`
- `ChrCustomizationDisplayInfo`
- `ChrCustomizationCondModel`

`ChrCustomizationElement` is especially important because a choice may resolve to geosets, skinned models, materials, bone sets, conditional models, display info, or other referenced resources.

## Normalized discovery output

The source adapter should emit normalized JSON instead of leaking backend-specific DB2 types to later pipeline stages.

Conceptually:

```json
{
  "race": {"retail_race_id": 36},
  "build": {"version": "resolved", "build_key": "resolved"},
  "models": {"male": [], "female": []},
  "customization": {"options": [], "choices": [], "elements": []},
  "file_data_ids": []
}
```

Extraction then fetches only the resulting dependency closure.
