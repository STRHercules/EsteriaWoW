# WotLK DBC Mapping

After model/customization normalization, the generated target data can touch:

- `ChrRaces.dbc`
- `CharBaseInfo.dbc`
- `CharStartOutfit.dbc`
- `CharSections.dbc`
- `CharHairGeosets.dbc`
- `CharacterFacialHairStyles.dbc`
- `SkillRaceClassInfo.dbc`
- `SkillLineAbility.dbc`
- `CreatureModelData.dbc`
- `CreatureDisplayInfo.dbc`
- `CreatureDisplayInfoExtra.dbc`

Do not copy Retail DB2 rows directly into WotLK DBCs. Retail source tables describe modern assets and customization; the generator must emit WotLK-compatible records using the project's assigned target race ID.
