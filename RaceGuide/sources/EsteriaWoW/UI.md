## Draft: Retail-style interface with Esteria custom races

Draft only—no files or client data would be changed.

### Core approach

Use `G:\Esteria\WoW-Retail-Interface-main` as the visual/interface base, while keeping Worgoblin as the authoritative source for custom-race behavior and data.

| Area | Source of truth |
|---|---|
| Login, character select, layout, buttons, artwork | New Retail-style interface |
| Custom-race behavior and compatibility | Existing Worgoblin implementation |
| Race models and DBC files | Worgoblin `patch-A.MPQ` |
| Server registration and gameplay | `modules\mod-worgoblin-high-elf` |
| Race/class/start data | Existing matching Worgoblin DBC and SQL |
| Client executable handling | Existing patched Esteria executable |

This assumes permission to modify the new interface, since its README prohibits derivative works.

### 1. Start from the working Esteria client

The new interface is only an overlay, not a complete client. I would begin with the current known-good Esteria 3.3.5a client and add the new files into the existing client structure:

- `GlueXML\*` → `Interface\GlueXML\*`
- `Glues\*` → `Interface\Glues\*`
- `GluesVideo\*` → `Interface\GluesVideo\*`
- `cinematics\*` → `Interface\cinematics\*`
- `Loginscreen\*` → `Interface\Loginscreen\*`
- `tooltips\*` → `Interface\tooltips\*`

I would not replace the entire `Interface` directory or overwrite Worgoblin’s DBC/model files.

### 2. Merge the Glue load order

The new interface’s `GlueXML.toc` would become the base, but it references files that are not included in that repository. Existing client Glue files would remain in place.

Important changes:

- Ensure `CharacterInfo.lua` loads before `CharacterCreate.lua`.
- Keep all required base XML files from the existing client.
- Remove or provide missing optional references such as `XML_TXXUI.xml`, `XML_IXXUI.xml`, and `LocalizationPost.xml`.
- Ensure only one authoritative copy exists for `CharacterCreate.lua`, `CharacterCreate.xml`, `GlueParent.lua`, and `GlueStrings.lua`.

### 3. Rebuild the character-creation screen around 15 race slots

The new interface currently supports only:

- `MAX_RACES = 10`
- Ten race buttons
- Five Alliance races and five Horde races
- Race information only for IDs 1–10

I would retain its visual design but expand the actual race layer to the current Esteria set:

Alliance:

1. Human
2. Dwarf
3. Night Elf
4. Gnome
5. Draenei
6. Worgen
7. High Elf

Horde:

1. Orc
2. Undead
3. Tauren
4. Troll
5. Blood Elf
6. Goblin
7. Mag’har Orc
8. Sethrak

The XML would receive buttons 11–15, and the positioning code would be changed from two five-item vertical lists to two compact two-column grids. That allows all 15 races to fit without adding a new scrolling system.

I would verify whether `GetSelectedRace()` returns an actual DBC race ID or an ordinal UI index before merging the logic. The interface would use an explicit mapping:

`UI slot → actual race ID → client file string → faction`

That prevents the common failure where the button displays one race but sends another race ID to the server.

### 4. Merge Worgoblin race presentation data

The new interface’s `CharacterCreate.lua` would remain the base, with the following Worgoblin pieces carried over:

- `MAX_RACES = 15`
- Expanded male/female icon coordinates
- Worgen, High Elf, Goblin, Mag’har, and Sethrak file strings
- Custom race ordering and faction mapping
- Existing `CharacterChangeFixup()` behavior
- Correct model/background handling for custom races
- Custom race tooltip and ability data

`CharacterInfo.lua` would be expanded with entries for the five custom races. Its current `RACE_DATA`, `ALLIANCE_RACES`, `HORDE_RACES`, tooltip positions, and fallback logic would all be updated so custom races are not treated as missing or automatically Alliance.

### 5. Merge strings without losing the new interface

The new `GlueStrings.lua` already contains much of the retail-style localization structure, but it lacks some Worgoblin entries.

I would merge in:

- `RACE_INFO_HIGHELF`
- `RACE_INFO_MAGHAR`
- `RACE_INFO_SETHRAK`
- Any missing female variants
- `ABILITY_INFO_HIGHELF*`
- `ABILITY_INFO_MAGHAR*`
- `ABILITY_INFO_SETHRAK*`
- Any Worgoblin-specific Worgen/Goblin strings not already present

The new localized string format would be preserved rather than replacing the entire file with the older Worgoblin file.

### 6. Preserve Worgoblin’s client data

The new interface contains no replacement for the custom race data, so I would retain Worgoblin’s:

- `ChrRaces.dbc`
- `CharBaseInfo.dbc`
- `CharStartOutfit.dbc`
- `SkillRaceClassInfo.dbc`
- `CreatureDisplayInfo*.dbc`
- `CreatureModelData.dbc`
- `CharSections.dbc`
- `NameGen.dbc`
- Custom character models, textures, and sounds

The same compatible DBC set must exist on both the client and the worldserver. The new interface would not modify server C++ or relink the Worgoblin module.

### 7. Keep ARAC and custom class combinations intact

The interface should continue using:

- `GetAvailableClasses()`
- `IsRaceClassValid()`
- Existing Worgoblin/ARAC DBC and SQL data

That means the screen reflects the actual client/server race-class permissions instead of hardcoding a new list. The ten standard class descriptions in the new interface can remain; only the race/class availability source needs to stay synchronized.

### 8. Final patch structure

I would use:

- Existing Worgoblin patch for custom DBCs, models, and race assets
- One later-loading Retail UI patch containing the merged Glue and interface files
- No duplicate character-creation files in later patches
- No optional patch that hides the extra races
- The same patched executable/signature handling already required by Worgoblin

### Definition of done

The result would need to prove:

- All 15 races appear for both genders.
- Each button selects the correct actual race ID.
- Each race shows the correct model, name, faction, icon, tooltip, and customization options.
- Custom class combinations match the server.
- New characters receive the correct start location, spells, skills, action bars, and outfit.
- Existing Worgen, Goblin, High Elf, Mag’har, and Sethrak characters still log in correctly.
- No duplicate or missing Glue files cause Lua/XML errors.