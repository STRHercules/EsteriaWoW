# Esteria Playable Race Expansion — Vulpera Horde & Pandaren Alliance (Additive Patch-B Integration)

Draft revision only. No source, SQL, DBC, MPQ, or client files were changed.

## 1. Scope

Implement only these two playable race identities:

| Race | Faction | Proposed identity |
|---|---|---|
| Vulpera | Horde | Existing custom-race identity using the extracted Vulpera models and customization data |
| Pandaren | Alliance | Alliance-specific Pandaren identity using the extracted Pandaren models and customization data |

The following are explicitly out of scope for this revision:

- Horde Pandaren
- Kul Tiran
- Forsaken
- Ogre
- Replacing Sethrak
- New custom racial abilities
- Ascension/CoA custom classes
- Pandaren Monk; class \`10\` remains reserved in the current Esteria class contract

The initial race/class matrix remains Esteria’s existing classes \`1–9\` and \`11\`.

## 2. Current Esteria constraints

The core is already mostly data-driven:

- \`RaceMgr::LoadRaces()\` derives playable, faction, and maximum race values from \`ChrRaces.dbc\`.
- \`ObjectMgr::LoadPlayerInfo()\` consumes \`playercreateinfo\` and \`ChrRaces\` model references.
- Character creation uses \`CharBaseInfo\`, \`CharStartOutfit\`, \`CharSections\`, and \`SkillRaceClassInfo\`.
- The current DBC loader has an \`OnAfterLoadDBCStores()\` seam through \`mod-wxl-dbc\`.
- Race masks remain 32-bit, so new IDs must stay at or below 32.

Relevant files:

- [SharedDefines.h](R:\\Users\\Zach\\Documents\\GitHub\\EsteriaWoW\\src\\server\\shared\\SharedDefines.h:68)
- [RaceMgr.cpp](R:\\Users\\Zach\\Documents\\GitHub\\EsteriaWoW\\src\\server\\game\\Entities\\Player\\RaceMgr.cpp:47)
- [ObjectMgr.cpp](R:\\Users\\Zach\\Documents\\GitHub\\EsteriaWoW\\src\\server\\game\\Globals\\ObjectMgr.cpp:4346)
- [race_registry.json](R:\\Users\\Zach\\Documents\\GitHub\\EsteriaWoW\\modules\\mod-custom-server\\data\\races\\race_registry.json:78)

### Race-ID reconciliation

The repository currently contains two competing custom-race maps.

\`race_registry.json\`, \`chrraces_dbc.sql\`, and \`race_sync.sql\` currently use:

- \`18\` Pandaren Alliance
- \`20\` Vulpera Horde
- \`26\` Pandaren Horde

\`SharedDefines.h\` and \`ConquestOfEsteria.md\` instead label:

- \`19\` Vulpera
- \`21–22\` Pandaren variants

This revision should preserve the authored registry/SQL map because it is also used by the generated model and start-data migrations:

| ID | Race | Scope |
|---:|---|---|
| 18 | Pandaren Alliance | Enable |
| 20 | Vulpera Horde | Enable |
| 26 | Pandaren Horde | Preserve, leave out of scope |

Before implementation, confirm the live database and existing character counts. Do not silently remap existing race IDs. Sethrak ID15 remains unchanged in this revision.

No new race ID is required, so ID29 and additional mask expansion are not part of this work.

## 3. Asset audit

All inspected target character models are \`MD20\` version \`264\`, compatible with the WotLK-era model format.

Core attachment IDs checked:

- \`0, 1, 2\`: shoulders
- \`3\`: shield
- \`10\`: head
- \`13\`: main-hand
- \`14\`: off-hand

| Race | Assets | Jump sequences 37/38/39 | Gear attachment result | Status |
|---|---|---|---|---|
| Vulpera | \`patch-CHA.mpq\\Character\\vulpera\\male|female\` | Present for both sexes | Complete checked set for both sexes | Strong model-level candidate |
| Pandaren Alliance | \`patch-CHA.mpq\\Character\\Pandaren\\male|female\` | Present for both sexes | Complete checked set for both sexes | Strong model-level candidate |

These two are the only target races in this revision that passed the basic two-gender jump and equipment-point audit. That is model-level evidence, not proof of complete playability.

### Vulpera

Available:

\`\`\`text
G:\\Ascension\\Ascension\\resources\\ascension-live\\Data\\Extracted\\patch-CHA.mpq\\Character\\vulpera\\male\\vulperamale.m2
G:\\Ascension\\Ascension\\resources\\ascension-live\\Data\\Extracted\\patch-CHA.mpq\\Character\\vulpera\\female\\vulperafemale.m2
\`\`\`

The package contains:

- Separate male and female models.
- 48 external animation files per gender.
- Complete checked attachment points for both genders.
- 504 \`CharSections\` rows.
- 26 extracted start-outfit rows.
- Extensive skin, face, hair, and eye textures.

The extracted root \`NameGen.dbc\` has no Vulpera name rows. Random-name support therefore needs dedicated rows or an explicit fallback.

The extracted client DBC uses Vulpera as donor race ID19, while the recommended Esteria target is ID20. All race-specific DBC rows must be remapped to ID20 rather than copied by numeric identity.

### Pandaren Alliance

Available:

\`\`\`text
G:\\Ascension\\Ascension\\resources\\ascension-live\\Data\\Extracted\\patch-CHA.mpq\\Character\\Pandaren\\male\\pandarenmale.m2
G:\\Ascension\\Ascension\\resources\\ascension-live\\Data\\Extracted\\patch-CHA.mpq\\Character\\Pandaren\\female\\pandarenfemale.m2
\`\`\`

The package contains:

- Separate male and female models.
- 201 male external animation files.
- 210 female external animation files.
- Complete checked attachment points for both genders.
- 1,364 \`CharSections\` rows.
- 26 extracted start-outfit rows.

The extracted client DBC uses Pandaren as donor race ID20, while the recommended Alliance target is ID18. Appearance, hair, face, and start-outfit rows must be remapped to ID18.

The Horde Pandaren row remains preserved but disabled/out of scope. It must not be exposed by the character creator in this change.

The extracted root \`NameGen.dbc\` has no Pandaren name rows.

## 4. Client and Glue strategy

Use the current Esteria character creator as the authoritative UI:

\`\`\`text
G:\\Ascension\\Ascension\\resources\\ascension-live\\Data\\Extracted\\patch-b.mpq\\Interface\\GlueXML\\CharacterCreate.lua
G:\\Ascension\\Ascension\\resources\\ascension-live\\Data\\Extracted\\patch-b.mpq\\Interface\\GlueXML\\CharacterCreate.xml
G:\\Ascension\\Ascension\\resources\\ascension-live\\Data\\Extracted\\patch-b.mpq\\Interface\\SharedXML\\SharedConstants.lua
\`\`\`

The current patch-B creator has:

- \`MAX_RACES = 11\`.
- 11 statically defined race buttons.
- CoA/archetype support.
- Custom class-preview logic.
- Race icons sourced through \`RACE_ICON_TCOORDS\`.

\`MAX_RACES\` here is UI button capacity, not the highest DBC race ID. The final button count must equal the existing visible race manifest plus Vulpera and Alliance Pandaren. Horde Pandaren must not be added to the visible list.

Do not replace the current creator with another implementation or import any donor Glue package wholesale.

### Patch-B preservation contract

The existing `patch-b.mpq` is the authoritative Esteria client interface package. It is the base to add to, not a package to replace or rebuild from another race package.

The following existing Patch-B systems must remain authoritative and intact:

- `Interface\GlueXML\CharacterCreate.lua`
- `Interface\GlueXML\CharacterCreate.xml`
- `Interface\GlueXML\GlueParent.lua`
- `Interface\GlueXML\GlueXML.toc`
- `Interface\GlueXML\AccountLogin.lua` and `AccountLogin.xml`
- `Interface\GlueXML\CharacterSelect.lua` and `CharacterSelect.xml`
- Existing `Interface\SharedXML\*` files
- Existing `Interface\Glues\*` files and background models

The only permitted client work for this race change is additive or narrowly merged:

- Add Vulpera and Pandaren race icon/round-icon BLPs under `Interface\Glues\CharacterCreate\`.
- Add a missing race-specific backdrop asset only when the existing Human/Alliance or Orc/Horde backdrop cannot be reused.
- Add Vulpera and Pandaren character models, skins, animations, and textures under their `Character\...` paths. These are gameplay assets, not replacements for the interface.
- Add the minimum race-button definitions and anchors to the existing `CharacterCreate.xml`.
- Add only the required race icon coordinates, race strings, and optional lighting/ambience entries to the existing Lua tables.
- Add only required Glue load-order entries if a genuinely new file is needed.
- Merge only the required client DBC rows into the existing DBC set.

The following actions are forbidden for this scope:

- Do not replace the existing `CharacterCreate.lua`, `CharacterCreate.xml`, `GlueParent.lua`, or `GlueXML.toc` with donor copies.
- Do not copy an entire donor `Interface`, `GlueXML`, `SharedXML`, or `Glues` directory into Patch-B.
- Do not import a second copy of any authoritative login, character-select, or character-create file.
- Do not delete, rename, or overwrite existing Patch-B interface files or background assets.
- Do not change the current login screen, character-select screen, or existing character-creation behavior except where required to expose the two new race entries.
- Do not import Ogre, Forsaken, or Kul Tiran Glue/interface files; those races are deferred.

The final Patch-B change must be reviewable as an additive file manifest plus small merges into the existing creator. If a packaging step would overwrite an existing Patch-B file, stop and resolve the merge instead of accepting the overwrite.

### Required Glue changes

1. Expand the race-button pool only as required by the final enabled manifest, using the existing Patch-B button template, style, frame, and layout conventions. Do not redesign or replace the character-creation screen.

2. Keep UI ordinal indexes separate from actual race IDs. A button index must never be assumed to equal the DBC race ID.

3. Add icon support for Vulpera and Pandaren male/female portraits. \`patch-CHA.mpq\` contains the character models and textures but not a complete new-race creation icon set.

4. Add:

   - \`RACE_INFO_VULPERA\`
   - \`RACE_INFO_PANDAREN\`
   - Female fallbacks where required
   - Racial ability strings only if abilities are separately approved

5. Use faction-aware presentation:

   - Vulpera → Horde backdrop, ambience, and faction data
   - Pandaren Alliance → Alliance backdrop, ambience, and faction data

6. Ensure the final creator has one authoritative copy of:

   - \`CharacterCreate.lua\`
   - \`CharacterCreate.xml\`
   - \`GlueParent.lua\`
   - Race localization strings

7. Do not add a Horde Pandaren button, Horde Pandaren strings, or Horde Pandaren selection path in this revision.

## 5. DBC and client-data work

DBC work is separate from the Patch-B interface merge. It must also be additive: merge only the Vulpera and Alliance Pandaren rows into the existing client/server DBC composition and preserve every unrelated existing row and file.

Do not copy the extracted \`DBFilesClient\` directory wholesale. Its donor IDs and race flags do not match the Esteria registry.

Required DBC surfaces:

- \`ChrRaces.dbc\`
- \`CharBaseInfo.dbc\`
- \`CharStartOutfit.dbc\`
- \`CharSections.dbc\`
- \`CharacterFacialHairStyles.dbc\`
- \`CharHairGeosets.dbc\`
- \`CharHairTextures.dbc\`
- \`BarberShopStyle.dbc\`
- \`SkillLine.dbc\`
- \`SkillLineAbility.dbc\`
- \`SkillRaceClassInfo.dbc\`
- \`NameGen.dbc\`
- \`CreatureModelData.dbc\`
- \`CreatureDisplayInfo.dbc\`
- \`CreatureDisplayInfoExtra.dbc\`, when required
- \`HelmetGeosetVisData.dbc\`
- \`ItemDisplayInfo.dbc\`
- \`Faction.dbc\`
- \`FactionTemplate.dbc\`

Important rules:

- Remap extracted Vulpera donor rows from race19 to Esteria race20.
- Remap extracted Pandaren donor rows from race20 to Esteria Alliance race18.
- Keep the Horde Pandaren row at race26 preserved but not playable.
- Clear only the non-playable bit for the two enabled target rows after all dependent data exists.
- Preserve \`CAN_MOUNT\` and other model-appropriate flags.
- Use Alliance faction/language data for Pandaren Alliance.
- Use Horde faction/language data for Vulpera.
- Add \`NameGen\` rows for Vulpera and Pandaren, or explicitly disable random-name behavior for them.
- Add the target race bits to \`SkillLineAbility\` and \`SkillRaceClassInfo\` for languages and intended proficiencies.
- Keep \`.mdx\` versus \`.m2\` model path conventions consistent with the existing client loader and current Esteria data.
- Rebuild or validate secondary indexes after DBC continuation injection.

## 6. Server and SQL work

Current relevant data:

- [u_custom_server_2026_08_29_races.sql](R:\\Users\\Zach\\Documents\\GitHub\\EsteriaWoW\\modules\\mod-custom-server\\data\\sql\\db-world\\updates\\u_custom_server_2026_08_29_races.sql)
- [u_custom_server_2026_09_02_race_models.sql](R:\\Users\\Zach\\Documents\\GitHub\\EsteriaWoW\\modules\\mod-custom-server\\data\\sql\\db-world\\updates\\u_custom_server_2026_09_02_race_models.sql)
- [u_custom_server_2026_09_02_race_sync.sql](R:\\Users\\Zach\\Documents\\GitHub\\EsteriaWoW\\modules\\mod-custom-server\\data\\sql\\db-world\\updates\\u_custom_server_2026_09_02_race_sync.sql)
- [u_custom_server_2026_09_03_race_scope.sql](R:\\Users\\Zach\\Documents\\GitHub\\EsteriaWoW\\modules\\mod-custom-server\\data\\sql\\db-world\\updates\\u_custom_server_2026_09_03_race_scope.sql)
- [chrraces_dbc.sql](R:\\Users\\Zach\\Documents\\GitHub\\EsteriaWoW\\modules\\mod-custom-server\\data\\sql\\db-world\\updates\\dbc\\chrraces_dbc.sql)

The current scope migration disables IDs \`14–28\`, and a later migration re-enables only Sethrak ID15. Do not edit those applied migrations. Add a later corrective migration for Vulpera and Alliance Pandaren.

That migration should:

1. Preflight the update table and count existing characters at IDs18, 20, 26, and 15.
2. Leave Sethrak ID15 unchanged.
3. Enable only ID18 Pandaren Alliance and ID20 Vulpera Horde.
4. Leave ID26 Pandaren Horde disabled and out of the character creator.
5. Align \`ChrRaces\`, model/display references, faction, language, and client files with the selected IDs.
6. Verify \`playercreateinfo\` exists for classes \`1–9\` and \`11\` for both target races.
7. Verify race-specific starting skills and spells without inventing new racial abilities.
8. Verify valid starter outfits for every enabled class and both sexes.
9. Use the existing \`elwynn\` Alliance and \`durotar\` Horde start profiles unless separate starting zones are approved.
10. Keep existing race IDs, character rows, and applied migration history intact.
11. Ensure the PlayerBots name and appearance path has valid data for IDs18 and20 without enabling ID26 or other deferred races.

The existing generated all-race skill mask through ID28 is sufficient; no new ID29 mask expansion is required.

## 7. Minimal code changes

If the existing registry/SQL IDs are retained, server C++ changes should be limited:

- Align the custom enum values in \`SharedDefines.h\` with the authoritative map:
  - Pandaren Alliance → \`18\`
  - Vulpera → \`20\`
  - Pandaren Horde remains \`26\` but out of scope
- Update enum reflection metadata only if custom race values are used through that path.
- Reuse the existing \`RaceMgr\`, \`ObjectMgr\`, DBC loader, and character-creation validation paths.

No new race-specific logic should be needed in \`RaceMgr\`, \`Player::Create\`, or \`CharacterHandler\` merely to register these two races.

### PlayerBots

PlayerBots support is included for Vulpera Horde and Pandaren Alliance only. Horde Pandaren and every other deferred race must remain excluded.

The primary implementation surface is:

- `R:\Users\Zach\Documents\GitHub\EsteriaWoW\modules\mod-playerbots\src\Bot\Factory\RandomPlayerbotFactory.cpp`
- `R:\Users\Zach\Documents\GitHub\EsteriaWoW\modules\mod-playerbots\src\Bot\Factory\RandomPlayerbotFactory.h`

Required behavior:

- Replace the current broad `race > RACE_BROKEN_PLAYER` rejection with an explicit bot-supported-race policy that admits only Vulpera ID20 and Pandaren Alliance ID18 in addition to the existing supported races.
- Keep Horde Pandaren ID26, Sethrak ID15, and all other custom races excluded.
- Preserve the expansion check, disabled-race-mask check, faction balancing, and `PlayerInfo` validation.
- Ensure `IsAlliance(race)` resolves Vulpera as Horde and Pandaren Alliance as Alliance from the final `ChrRaces` rows.
- Keep explicit `CombineRaceAndGender()` cases for both target races and map them to a valid name category.
- Ensure `HasRandomBotAppearanceData()` finds skin, face, hair, and any required facial-hair sections for both genders.
- Keep the existing generic `playerbots_names` fallback unless race-specific bot name pools are separately approved. The client `NameGen.dbc` requirement and the PlayerBots name table are separate concerns.
- Ensure random bot creation reaches `Player::Create()` with valid race/class/start-outfit data for every enabled class.
- Audit other PlayerBots race switches, race-name tables, factory limits, travel/teleport logic, and appearance assumptions for accidental exclusion or mislabeling.

PlayerBots does not need race-specific combat AI for these two races; class behavior remains class-driven. The change is complete only when bot creation, appearance selection, faction assignment, and classic-race behavior are all verified.

## 8. Recommended implementation order

1. Freeze the registry/SQL race map and inspect live character counts.
2. Preserve ID15 Sethrak and ID26 Horde Pandaren unchanged.
3. Build an asset manifest for the Vulpera and Pandaren models, skins, animations, and textures.
4. Remap donor DBC rows to Vulpera ID20 and Alliance Pandaren ID18.
5. Add missing \`NameGen\` rows and creation icon assets.
6. Create an explicit additive Patch-B file allowlist and verify that no existing interface path will be overwritten.
7. Merge the two race entries into the current Patch-B Glue creator using its existing templates and behavior.
8. Update and validate the PlayerBots race allowlist, name category, appearance selection, and bot creation path.
9. Add a later corrective server migration enabling IDs18 and20.
10. Validate creation, login, starter data, equipment, jump, mount, relog, and random-bot behavior.
11. Keep all deferred race work separate from this change.

## 9. Definition of done

For Vulpera Horde and Pandaren Alliance:

- Only the intended faction entry is visible.
- The creator sends the correct actual race ID.
- Both genders load with the correct model and customization options.
- All enabled classes have valid start-outfit data.
- Starting skills, spells, stats, action bars, language, and faction are correct.
- Characters log in, log out, relog, and survive restart.
- Head, shoulders, shield, main-hand, and off-hand equipment render correctly.
- Jumping and mounting work as intended.
- Character select, character create, paper doll, barber, and world models render correctly.
- The existing Patch-B login screen remains unchanged.
- The existing Patch-B character-select screen remains unchanged.
- The existing Patch-B character-creation screen and behavior remain unchanged apart from the two additional race entries.
- No duplicate Glue files or path collisions shadow the current interface implementation.
- Horde Pandaren, Sethrak, and all other deferred race identities remain unchanged.
- Existing current-race characters are not silently reinterpreted.

Static DBC/model checks are not sufficient; live character creation and equipment validation remain the final gate.

The [Adding a New Race tutorial](https://github.com/Hextv/Adding-a-New-Race-Step-by-Step-Tutorial-3.3.5) remains useful as a DBC/Glue checklist, but its TrinityCore-oriented ID and UI assumptions must be adapted to Esteria’s existing registry and migrations.
