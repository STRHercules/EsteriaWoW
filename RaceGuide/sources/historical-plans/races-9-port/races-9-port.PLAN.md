# races-9-port: custom race creation-screen fixes

Live client: `3.3.5a - Dev` (Esteria/WoWXL build, `Esteria.exe` 7.72 MB). All race
data the character creator reads lives in `Data/Patch-Y.MPQ`; the ported art
lives in `Data/Patch-D.MPQ` (Eredar/Nightborne/VoidElf/Lightforged/Zandalari/
DarkIron/Dracthyr) and `Patch-E/G` (Zandalari/DarkIron/Dracthyr,
KulTiran/Illidari). Rebuilt by `port_race.py`; DBC/glue repair by
`fix_patch_y.py`; art post-step by `retag_voidelf_ears.py`.

## Fixed 2026-09-13 (second pass)

1. **Every class except Death Knight showed a placeholder cube.**
   `CharacterCreate.lua` -> `SetBackgroundModel` looks the race's
   `ClientFilestring` up in `allianceRaces`/`hordeRaces`; anything missing falls
   through to `SetCharCustomizeBackground("Interface\Glues\Models\UI_<key>\UI_<key>.m2")`
   and there is no such scene for our races, so the customise scene fails to
   build and the actor renders as a cube. Death Knight worked only because its
   key resolves to the stock `UI_DeathKnight` scene. Fix: `RACE_BACKGROUND_KEYS`
   entries mapping our nine keys to `HUMAN`/`ORC` (same pattern the earlier
   Vulpera/Pandaren work used).
2. **Eredar was a cube even on Death Knight.** After the Eunoia harvest its
   `CreatureModelData` row pointed at `Character\eredar\Male\Race_EredarMale.m2`,
   a file we never staged. Both Eredar model rows now point at the shipped
   `Character\Eredar\{Male,Female}\Eredar*.m2`.
3. **Death Knight (and every other class) previewed naked.** The outfit rows for
   races 16-30 were the leftovers of the "strip all gear" diagnostic build (all
   item slots `-1`). `CharStartOutfit` rows are rebuilt from Vulpera's rows (20
   per race, all ten classes, gear intact - the DK row carries the Acherus set).
4. **Ears / tusks (Void Elf, Zandalari).** The port copied `CharSections` and
   `CharHairGeosets` from the donor client but not
   `CharacterFacialHairStyles.dbc`, the table that maps a race's facial
   customisation choice onto geosets - Eunoia ships 39 rows for their Void Elf
   and 225 for their Zandalari, while our client had almost none. It also left
   every race with the wrong `ChrRaces` customisation strings (fields 65-67), so
   a Void Elf advertised `EARRINGS` as nothing and a Zandalari `TUSKS` as
   `EARRINGS`. Both are now donor-faithful: the rows are copied per race and the
   strings come from the module SQL (`NORMAL/EARRINGS/NORMAL` for Void Elf,
   `TUSKS/TUSKS/NORMAL` for Zandalari, `HORNS` for Lightforged, and so on).
   The earlier geoset re-tag experiment (Void Elf ear submeshes 702 -> 7) did
   not change anything in game and has been reverted; `Patch-D` skins are
   pristine again and `retag_voidelf_ears.py` is kept for reference only.

## Open

## In-game rendering (2026-09-13, fourth pass)

The creator screen and the in-game/character-select path resolve models
differently: the creator uses `ChrRaces` display ids, in game the client builds
`Character\<ClientFilestring>\<Gender>\<ClientFilestring><Gender>.m2` plus its
`.skin` LODs. Two races had nothing at that path:

    KulTiran -> shipped as CHARACTER\Naga_\male\kultiranmale.m2
    Illidari -> shipped as Character\BloodElf_Dh\Male\BloodElfMale_DH.m2

`stage_filestring_model_aliases.py` copies both genders (model + `.mdx` + four
skins) onto the filestring names in `Patch-G`. The other seven races already
resolve there (only letter case differs, and MPQ lookups are case-insensitive).

`CharacterSelect.lua:60` also crashed every time the character list opened for a
ported race: `PlayGlueAmbience(GlueAmbienceTracks[strupper(CurrentModel)], 4.0)`
was handed nil, which errors and aborts the screen - so a freshly created
character never showed up. `fix_glue_ambience.py` adds the nine races to
`CharModelFogInfo`, `CharModelGlowInfo`, `GlueAmbienceTracks` and `RaceLights`
in `GlueParent.lua` and guards the call in `CharacterSelect.lua` (and in
`SetBackgroundModel`) so a missing track can never take a screen down again.

Rebuild order after a full `port_race.py` run: `fix_patch_y.py`,
`fix_glue_ambience.py`, `fix_lightforged_glow.py`,
`stage_filestring_model_aliases.py`.

## Lightforged skin overlay (2026-09-13, third pass)

`Character\Eredar\...\Eredar*.m2` and
`character\lightforgeddraenei\...\lightforgeddraenei*.m2` are the same model to
within 46 bytes (name string plus one table entry). The only functional
difference is entry 14 of the model texture-replace table: the Eredar, whose
glowing skin renders in this client, binds `(4, 4)`; the Lightforged bound
`(2, 4)`, which this client does not draw - so the Lightforged lost the golden
rune overlay that lives in `lightforgeddraeneimaleskinEXTRA_*.blp`. Both
Lightforged models (male/female, `.m2` and `.mdx`) now carry `(4, 4)`;
`fix_lightforged_glow.py` does it and the pre-change `Patch-D` is in
`Backups\patch-d-before-voidelf-ears-20260913-153829`.

If another race is missing an overlay, compare its model's replace table against
a race whose overlay works (same procedure).

Second pass on the same tables: the female models bound the last entry
`(0, 52)` where the males bind `(0, 4)`, which matches the report that only the
Lightforged males showed the hand/foot effect. All four models (Eredar and
Lightforged, both genders, plus their `.mdx` twins) now carry the male
arrangement - `entry 14 = (4, 4)`, `entry 20 = (0, 4)`. The Eredar male's own
bytes were verified unchanged against the rollback archive, so the "Eredar lost
it" report cannot have come from its file data; with every model aligned, a
creator that reuses model state between races can no longer make the two look
different.

- Ears are still unverified in game after the facial-feature import. If they
  still do not show, the next lever is the per-race customisation *choice*
  (the creation screen's personalise panel) - cycling it should switch the
  geoset family the client draws and tell us which table drives it.
- `inspect_geoset_bones.py` exists but its bone stride/pivot parse is not
  trustworthy yet (world pivots came out above the model's height); fix the
  record layout before relying on it.
- Server-side `chrraces_dbc` display ids in `mod-custom-server` have not been
  re-keyed to the harvested ids (client-only change so far).

## Player display ids (2026-09-13, fifth pass)

Logging the ported races in showed them as lashers: `Creature\LasherOrchid\LasherOrchid.mdx`
for Nightborne, `Creature\Lasher\Lasher.mdx` for Zandalari, night elf / tauren females. The
creation screen stayed correct because it resolves the client's own `ChrRaces` donor ids;
the world model comes from the display id the server sends, and that value never survived:

- `PlayerInfo::displayId_m/f` is `uint16` (`src/server/game/Entities/Player/Player.h`) while
  `ChrRacesEntry::model_m/f` is `uint32`, so `chrraces_dbc` id 90004 wrapped to 24468 and the
  client drew whatever stock `CreatureDisplayInfo` 24468 points at.
- Eunoia never hit this: every one of their race rows is below 65536 (Nightborne 33070/32902,
  Zandalari 28/29, Eredar 2/3, ...). Esteria's own working custom races already follow the rule
  with a 60000 band - Sethrak 60000/60001, Broken 60002/60003, Pandaren 60004/60005, Vulpera
  60006/60007.

The nine ported races now live in 60008-60025 on both sides:

| race | id | male | female |
|---|---:|---:|---:|
| Eredar | 16 | 60008 | 60009 |
| Nightborne | 17 | 60010 | 60011 |
| Void Elf | 19 | 60012 | 60013 |
| Lightforged Draenei | 21 | 60014 | 60015 |
| Zandalari Troll | 22 | 60016 | 60017 |
| Dark Iron Dwarf | 23 | 60018 | 60019 |
| Dracthyr | 28 | 60020 | 60021 |
| Kul Tiran | 29 | 60022 | 60023 |
| Illidari | 30 | 60024 | 60025 |

Changed: client `Data\Patch-Y.MPQ` (`CreatureDisplayInfo` rows re-keyed onto the same model
ids), live `acore_world.chrraces_dbc` + `creaturedisplayinfo_dbc`, every SQL source that carried
the old ids (`rev_1787850000002_race_models.sql`, `rev_1787850000003_races_29_30.sql`, new
`rev_1787850000004_race_display_id_band.sql`, `u_custom_server_2026_08_30_race_models.sql`,
`u_custom_server_2026_09_02_race_sync.sql`, `dbc/chrraces_dbc.sql`), `port_race.py`, and the new
script `fix_display_id_band.py` (also usable as a dry run).

Still above 65535, all non-playable in the client's `ChrRaces` so they cannot be created:
Sethrak 15 (90000/90001), Broken 24/27 (90018/90019), Forsaken 25 (90020/90021), Pandaren 26
(90006/90007), Skeleton 40 (94135/94136). Re-key them the same way before enabling any of them.

### Character-select cubes (2026-09-13, sixth pass)

In world and in the creator the races are right, but selecting one of them on the character
select screen drew the placeholder cube. `CharacterSelect_SelectCharacter` hands
`GetSelectBackgroundModel(id)` - the race filestring, e.g. `Nightborne` - to the glue
`SetBackgroundModel`, and that function's own `allianceRaces`/`hordeRaces` tables do not know
the ported races, so both branches (creator -> `SetCharCustomizeBackground`, otherwise
`SetCharSelectBackground`) fall through to
`Interface\Glues\Models\UI_<Race>\UI_<Race>.m2`. Only `UI_Dracthyr` of that family exists, so
the scene never builds and the actor comes up as a cube. This is the same failure the creator
had before `RACE_BACKGROUND_KEYS`.

`fix_glue_ambience.py` now also declares the ported races in those tables - VOIDELF,
LIGHTFORGEDDRAENEI, DARKIRONDWARF, KULTIRAN as alliance and EREDAR, NIGHTBORNE, ZANDALARITROLL,
DRACTHYR, ILLIDARI as horde - which sends both screens (and the customize/race-change paths)
down the shared `UI_ALLIANCE` / `UI_HORDE` scenes the stock races use. Fixing it inside
`SetBackgroundModel` instead of adding a second call-site mapping keeps one mechanism; a
caller-side map for `CharacterSelect.lua` was written first and then reverted.

Rebuild order after a full `port_race.py` run: `fix_patch_y.py`, `fix_glue_ambience.py`,
`fix_lightforged_glow.py`, `stage_filestring_model_aliases.py`.

## Start data, portraits and camera (2026-09-13, seventh pass)

Four follow-ups once the races rendered correctly in world, creator and select:

1. **Language and class skills.** `playercreateinfo_spell_custom` carried only ~31 hand-written
   rows per race, so a new character missed the weapon-skill spells (One-Handed Swords/Axes,
   Defense, Bows/Guns, ...) and the language spell the client needs before it will send chat
   ("You don't know that language"). Each race now copies a whole faction-appropriate stock
   class block set: Eredar/Nightborne <- Blood Elf, Void Elf <- Night Elf, Lightforged <- Draenei,
   Zandalari <- Troll, Dark Iron <- Dwarf, Dracthyr <- Orc (Kul Tiran and Illidari were already
   cloned from Dwarf/Blood Elf). Language rows land on 669 (Orcish) for Horde races and 668
   (Common) for Alliance. Existing characters keep their old set - `.reset spells` re-runs
   `LearnDefaultSkills()`/`LearnCustomSpells()` for them.
2. **Client language field.** Void Elf, Lightforged and Dark Iron shipped the donor's
   `BaseLanguage = 1` (Orcish) and `Alliance = 1` while the server says 7/0, so the client asked
   to chat in a language the character never learned. Patch-Y now matches the server.
3. **Unit frame portraits.** Display rows 33070/32902 (Nightborne) and 33174 (Void Elf male)
   carried `DisplayidExtra` references to extras no client we own ships, so the portrait renderer
   came up empty. Every stock race ships `DisplayidExtra = 0` on its player display row; all
   three now do too (the extra row that had been imported for 33174 was retired).
4. **Camera framing.** All 18 race model rows in `CreatureModelData` were clones of one template
   (collision 2.03/1.00, bounding box maxZ 1.568), so the camera focused around the waist/knees
   instead of the head. The rows now carry Eunoia's own numbers for the same model files
   (Nightborne 2.519, Zandalari 3.022, Kul Tiran 2.615, ...) on both the client and
   `creaturemodeldata_dbc`.

New tooling: `fix_race_visuals.py` (client camera/extras/language),
`fix_race_start_spells.py` -> `rev_1787850000005_race_start_spells.sql`,
`fix_race_modeldata_sql.py` -> `rev_1787850000006_race_modeldata.sql`.

## Vulpera world-entry crash and revert (2026-09-13, eighth pass)

`ERROR #132 (0xC0000005)` at `0x008285EB`, local player `Foxbow` (Vulpera, race 20),
reported right after the seventh pass. `Logs/wxl-core.log` shows the client was a
fresh launch (`wxl-core starting` 20:02:21, crash 20:02:31), so nothing stale: the
aligned rows themselves took the client down.

`0x008285EB` is not `M2.Read*`. It sits in the client's **M2 track/keyframe lookup**:
the faulting instruction is `cmp edx, dword ptr [esi + ecx*4]`, the binary search
that brackets a time against a track's keyframe-time array, so the track's key
pointer was invalid. The addresses come from the symbol table embedded in
`WarcraftXL.dll` (find it at file offset `0x839a8`: `{name pointer, code address}`
records, 391 entries); the nearest entries are `M2.FindTrackKey` `0x8284d0` and
`M2.TrackEvalQuat` `0x828680`, and the code between them is the key-bracket helper.
Read-only tooling for this: `disasm_at.py`, `find_lua_api.py`, `find_refs.py`.

What changed for the two races at 19:43/19:48 and is now reverted
(`revert_vulpera_pandaren.py`, backup
`Backups/patch-y-before-vulpera-revert-20260913-200419`): `ChrRaces` displays
`141254/141255` (Vulpera) and `141687/141688` (Pandaren) had been pointed at the ids
the server sends (`60006/60007`, `60004/60005`), their display rows had been linked
to extras `45441-45444`, and their `ExplorationSoundID` set to `4140/4141`. The
nine ported races keep their 60008-60025 rows, their extras and their sound values.

Verified with `diff_patch_y.py` against
`Backups/patch-y-before-vulpera-pandaren-align-20260913-194303/Patch-Y.MPQ`:
`CreatureDisplayInfo` and `CreatureDisplayInfoExtra` are identical again, and
`ChrRaces` differs only in the nine races' `ExplorationSoundID` (4140/4141, kept as
the only surviving part of that experiment). Races 18/20 are byte-for-byte back to
the rows they had while Foxbow was playable.

Open risk: if the crash returns with the reverted rows, the next suspect is the
Vulpera model's own animation data (Patch-C
`character\vulpera\male\vulperamale.m2`, 320 sequences / 287 key bones against
83-224 for the customs that render cleanly - flagged back on 2026-09-11). The
signature matches the Nimbus MD20 precedent, and the repair route is the same as
`stage_race_anims.py`: re-stage the model's external `.anim` set from
`G:\Eunoia\Client`. Note `check_anim_coverage.py` mis-reads sequence records (it
prints impossible paths such as `humanmale14564-16606.anim` for stock Human), so its
"missing" counts must not be trusted until that stride is fixed.

## Chat gate and player display rows (2026-09-13, ninth pass)

Two separate data bugs, both client-side, both now fixed.

**Chat.** The client decides which languages a character knows in
`GetNumLanguages` (`Wow.exe` 0x500760): it walks `Languages.dbc`, resolves each
language id to its spell, finds that spell in `SkillLineAbility.dbc` (records at
`0xad45b4`, stride 0x38, matched on field +8) through `0x812410`, and then looks for
the row's *SkillLine* id in the player's skill table. `0x812410` rejects any row
whose `RaceMask` does not contain the player's race, so the ported races counted
zero languages and the client refused to send chat - "You don't know that
language" - even with the skill at 300/300 in the Skills tab.

Esteria had already patched exactly those masks for their own races: Common (668)
carries `7245` = races 1,3,4,7,11,12,13 and Orcish (669) `25522` = races
2,5,6,8,9,10,14,15 - which is why Broken could always chat. `fix_language_masks.py`
ORs bits for races 16,17,18,19,20,21,22,23,28,29,30 (`0x387F8000`) into all nine
language rows; it writes the patched `SkillLineAbility.dbc` into `Patch-Y` (which
loads after `Patch-C`, the archive that ships the stock copy) - backup
`Backups/patch-y-before-language-masks-20260913-202458`. Mask bits only gate
recognition, so nobody gains a language they were not granted: the character still
needs the skill.

Server side, `LearnDefaultSkill()` calls `GetSkillRaceClassInfo()` first
(`Player.cpp`), and the stock `skillraceclassinfo_dbc` masks stop at race 15, so
`playercreateinfo_skills`' language rows (which already exist for our races) never
applied. `rev_1787850000010_race_language_skills.sql` widens those masks in
`skillraceclassinfo_dbc` and `skilllineability_dbc`; it is applied to the live DB.
Existing characters already carry the skill, so only characters created *after* a
worldserver restart need it.

**Portraits.** `CreatureDisplayInfo.TextureVariation_1/2/3` and
`PortraitTextureName` are *string* offsets into the DBC's own string pool. Every
stock player row, Esteria's working customs (Broken 60002, Sethrak 60000) and the
donor's own player rows for these races carry `0`; the ported rows 60008-60025
carried `51` in all four fields, and the older Vulpera/Pandaren rows
(141254/141255, 141687/141688) carried it in the last four. Offset 51 is not a
string start in our pool at all - it lands inside `HumanMaleCitizenLow` - because
those rows were re-keyed from donor *NPC* rows whose offsets only resolve against
the donor's pool (`check_donor_pool.py` proves the donor rows are 0 there).

`fix_display_row_strings.py` zeroes `ExtendedDisplayInfoID` plus those four string
fields on the 22 affected rows, which also removes the extras links the eighth pass
had added (based on the wrong premise that Vulpera/Pandaren portraits rendered).
Backup: `Backups/patch-y-before-display-strings-20260913-202934`. The `920`
ObjectEffectPackageID and `BloodLevel 0` are left alone - they are effect fields,
not portrait data.

## Legacy races and creation-time languages (2026-09-13, tenth pass)

User result after the ninth pass: the ported races have portraits, and
Nightborne/Zandalari/Dracthyr/Eredar/Void Elf/Dark Iron/Lightforged/Illidari can also
talk. Still broken: Kul Tiran cannot talk, Pandaren and Vulpera have neither
portraits nor chat.

**Kul Tiran (29).** `playercreateinfo_skills` had no Common (98) row for race 29 -
and none for Orcish (109) on race 30 - so a newly created character of those races
learned no language at all, and `LearnDefaultSkill()` is also the only place the
skill is granted. `rev_1787850000011_race_language_creation.sql` adds the faction
language row for all eleven custom races (Common for 18/19/21/23/29, Orcish for
16/17/20/22/28/30) and
`modules/mod-custom-server/data/sql/db-characters/race_language_backfill_faction.sql`
gives the skill to any existing custom-race character missing it. Both are applied
to the live databases; a worldserver restart is needed before the creation rows are
read.

**Pandaren/Vulpera.** Their `ChrRaces` rows still pointed at the pre-60000 ids
(`141687/141688`, `141254/141255`) while the server sends `60004-60007`, so the
client cannot map the player's display back to the race - the same thing that had to
be fixed for the nine. Their display rows `60004-60007` also still carried the bogus
`51` string offsets; the ninth pass only covered `60008-60025` and the two legacy
male/female pairs, so `fix_display_row_strings.py` now covers `60004-60025` plus
those four rows (backup `Backups/patch-y-before-display-strings-20260913-204211`).

`align_legacy_races.py` re-points those race rows at the server ids without the
extras links the old script added. Pandaren is aligned as of this pass (backup
`Backups/patch-y-before-legacy-align-20260913-204154`); **Vulpera is deliberately
held back** because the identical change on 13 Sep 19:43 crashed Foxbow at
`0x8285EB`, and that run also linked extras `45441-45444`. Once Pandaren proves the
align is safe on a clean row, run `align_legacy_races.py --race 20`; if Foxbow
crashes again the cause is the Vulpera model rather than the DBC, and
`revert_vulpera_pandaren.py` (or `--race` support in the new script) puts it back.

## Vulpera chat: race 20 is excluded from the client's skill table (2026-09-13, eleventh pass)

User result: Pandaren has portraits *and* can talk; Vulpera and Kul Tiran have
portraits but cannot talk. Vulpera's portraits came from the display-row string fix
alone, so the alignment is not what gates portraits.

The whole language chain is now mapped, in this order:

1. `Languages.dbc` - **shipped by `enUS/locale-enUS.MPQ`, not by any `Data\*.MPQ`** -
   enumerates 17 language ids (1 Orcish ... 7 Common ... 38 Goblin Binary). It is the
   list `GetNumLanguages` walks.
2. For each id the client resolves the language's spell and looks up
   `SkillLineAbility.dbc` (`0x812410`, records at `0xad45b4`, stride 0x38).
3. `0x810ed0(skill, race, class)` then requires a **`SkillRaceClassInfo.dbc`** record
   whose `RaceMask`/`ClassMask` match (records at `0xD3F610`, stride 0x20); only then
   is `0x810320` used for the SkillLineAbility masks.
4. Finally the row's SkillLine id must be present in the player's skill array.

Step 3 is Vulpera's blocker: nearly every stock row in that table carries
`RaceMask = 0xFFF7FFFF`, the "all races" mask **with bit 19 cleared - race 20
excluded**, because race 20 is an NPC race in stock data. So every language lookup
for a playable Vulpera failed and the client ended up with no languages at all.
`fix_skillrace_masks.py` ORs bit 19 back into all 206 such rows and ships the patched
`SkillRaceClassInfo.dbc` in `Patch-Y` (backup
`Backups/patch-y-before-skillrace-masks-20260913-205241`).

Kul Tiran does not fit that story: race 29 is inside every mask (`0xFFF7FFFF`
includes bit 28), the display ids match the server, and character `Bigg` (guid 427)
carries Common plus seven other languages. By the chain above his list should be
non-empty and his default ("Common", from `ChrRaces.BaseLanguage = 7`) is one of
them, so the next step is the exact refusal text: the client's own
`ERR_CANT_SPEAK_LANGAGE` ("You cannot speak that language.") means the *client* list
is empty, while the server's string 806 ("You don't know that language.") means the
message *was* sent and the server rejected the language id it carried.

## Vulpera crash: model and .anim files came from different donors (2026-09-13, twelfth pass)

Second Vulpera session ended the same way as the first - `ERROR #132` at
`0x008285EB`, i.e. inside the keyframe bracket search of `M2.FindTrackKey`
(`M2.FindTrackKey+0x11b`). The register dump shows the search index at
`ECX = 0x1FFFFFFF` (`(lo + hi) >> 1` with `HI = 0x3FFFFFFE`), so the track's key
array was garbage. The stack frames sit under `M2.CacheWaitThread`, i.e. the model
*load* thread, not the render path - the client was building a model whose animation
data did not match it.

That is exactly what the files say. `compare_vulpera_model.py` shows our shipped
Vulpera model, its four `.skin` LODs and its textures are **byte-identical to
`G:\Eunoia\Client\data\Patch-5.mpq`**, but `compare_vulpera_anims.py` shows all 48
external animations per gender differ from that same archive - ours are the older
`patch-CHA.mpq` set (male `0060-00.anim`: 102,624 bytes vs the donor's 196,640, and
every other file differs too). `stage_eunoia_vulpera.py` copied the Eunoia model,
skins and textures but never the `.anim` files, so the client has been pairing the
HD model with another model's animation data since that staging ran - which is also
why the crash only exists for Vulpera.

`stage_vulpera_anims.py` copies the donor's 96 files (48 per gender,
5,494,704 bytes) into `Patch-Y` (backup
`Backups/patch-y-before-vulpera-anims-20260913-205912`); `compare_vulpera_anims.py`
now reports `differing=0` for both genders. Do the same check when any other model
is re-staged from a donor: model, `.skin`, textures **and** `.anim` must come from
one source.

## Starter skills, proficiencies and quests (2026-09-13, thirteenth pass)

User result: Vulpera and a fresh Kul Tiran both have portraits and speech, Vulpera
no longer crashes. Remaining gap: the ported races learn none of their class's
weapon/armour skills (a Vulpera Hunter cannot equip the starting axes or crossbow)
and cannot pick up the quests of the zone they start in.

Both come from the same design gap - a custom race is only a `ChrRaces` row, so every
per-race creation table still stops at race 14.

* **Equipping.** `Player::CanUseItem()` (`PlayerStorage.cpp`) fails with
  `EQUIP_ERR_NO_REQUIRED_PROFICIENCY` when `GetSkillValue(proto->RequiredSkill) == 0`,
  so the item needs the weapon *skill line* (44 Axes, 45 Bows, ...). Those come from
  `playercreateinfo_skills` through `Player::LearnDefaultSkill()`, which starts with
  `GetSkillRaceClassInfo(skill, race, class); if (!rcInfo) return;` - and the
  server's `SkillRaceClassInfo.dbc` masks stopped at race 14. The rows themselves
  were missing too: a Vulpera Hunter had `50, 95, 109, 162, 183, 415, 777, 778`,
  an Orc Hunter has `44, 45, 98, 109, 111, 113, 115, 125, 137, 313, 315, 673, 759`.
* **Quests.** `quest_template.AllowableRaces` never had the custom race bits, so the
  starter NPCs simply had nothing to offer.

**Fix: every custom race adopts the stock race whose starting zone it uses.**

| start zone | host | custom races |
|---|---|---|
| Durotar (Valley of Trials) | 2 Orc | 14 Broken, 16 Eredar, 20 Vulpera, 22 Zandalari, 28 Dracthyr |
| Eversong | 10 Blood Elf | 17 Nightborne, 30 Illidari |
| Elwynn | 1 Human | 18 Pandaren, 19 Void Elf |
| Azuremyst | 11 Draenei | 21 Lightforged Draenei |
| Dun Morogh | 3 Dwarf | 23 Dark Iron Dwarf, 29 Kul Tiran |

The host's rows are copied into `playercreateinfo_skills`, `playercreateinfo_action`
and `playercreateinfo_cast_spell` for every custom race, and into
`playercreateinfo_spell_custom` for 14/18/20 (the three that had almost none - 3 to 6
rows per class instead of ~90). `rev_1787850000012_race_start_skills.sql` holds those
statements, `rev_1787850000013_race_start_quests.sql` widens
`quest_template.AllowableRaces` per host race (race 20 now sees 2235 quests, the same
set Orc sees). Both are applied to the live world DB.

`fix_server_skillrace.py` ORs each custom race's bit into the server's
`SkillRaceClassInfo.dbc` wherever its host race's bit is set (316 rows). The patched
file is in `modules/mod-custom-server/data/dbc/SkillRaceClassInfo.dbc`, copied into
the worldserver data volume, and bind-mounted read-only in
`docker-compose.override.yml` (same pattern as the FlyAnywhere `AreaTable.dbc`) so a
volume rebuild cannot silently revert it. Backup:
`Backups/server-dbc-before-skillrace-20260913-211042`.

Skills are re-learned on every login (`PlayerStorage.cpp` calls
`LearnDefaultSkills()` while loading a character), so existing characters pick their
weapon skills up on the next login; class *ability* spells still need `.reset spells`
because `LearnCustomSpells()` only runs at creation or on that command.

## Starter gear vs. starter skills (2026-09-13, fourteenth pass)

User report: a Vulpera Hunter starts with a **two-handed axe (12282)** and a **crossbow
(23347)** but is only granted Axes (44) and Bows (45); a Dark Iron Warrior starts with a
**two-handed sword (49778)** while the Dwarf block grants 44/46/172 plus maces.

The two sides come from different places and never agreed: the *skills* are the host race's
block (`rev_1787850000012`), while the *outfit* rows in `charstartoutfit_dbc` were rebuilt
from the old Vulpera rows, so any race/class can carry gear its host never grants.
`Player::CanUseItem()` and the client both want the item's skill line, which is why the
character cannot equip its own starting weapon.

`fix_starter_gear_skills.py` walks `charstartoutfit_dbc` for every custom race and class,
resolves each starting item's `class`/`subclass` to the skill line (two-handed axe 172,
crossbow 226, two-handed sword 55, staff 136, dagger 173, thrown 176, one-handed mace 54,
shield 433, cloth 415, leather 414, mail 413, plate 293) and inserts the missing
`playercreateinfo_skills` rows for **that race and class only**. 186 rows, written to
`rev_1787850000014_race_starter_outfit_skills.sql` and applied to the live world DB.

`SkillRaceClassInfo` had to widen with it: the server's DB table only carried the stock
masks a second time, so `LearnDefaultSkill()` would have ignored the new rows exactly like
before. Both copies are patched - the world DB table and the DBC in the data volume (337
rows; every non-zero mask now carries the custom race bits), the latter also saved to
`modules/mod-custom-server/data/dbc/SkillRaceClassInfo.dbc` and bind-mounted. Backup:
`Backups/server-dbc-before-skillrace-20260913-212618`.

Verified: Vulpera Hunter = 44, 45, 172, 226; Vulpera/Dark Iron Warrior = 43, 44, 55, 172;
Death Knight rows include plate 293 and cloth 415; Shaman rows include mace 54, leather 414
and shield 433.

Trade-off worth knowing: this grants the outfit's proficiencies at level 1 even where the
stock game trains them later (a Hunter's two-handed axe and crossbow are level 20 trainer
skills). The alternative is to point the outfits back at the host race's kit instead of the
old Vulpera rows - a `CharStartOutfit` change on both the client and the server.

## Alliance Illidari (2026-09-13, fifteenth pass)

The donor ships **two** Illidari races - its 24 "Illidari NightElf" (Alliance, Common,
displays 67/70 -> `Character\NightElf_Dh\...`) and its 27 "Illidari Blood Elf" (Horde,
Orcish, displays 12/24) - and only the Blood Elf half was ported, which is why Alliance
listed 12 races against Horde's 13.

Added the Alliance counterpart as **race 31**, cloned from race 30:

* client (`add_alliance_illidari_client.py`): `ChrRaces` row 31 (faction 1, alliance 0,
  Common, displays 60026/60027, same `Illidari` filestring so model path and race icon resolve),
  display rows 60026/60027, `CharBaseInfo` for all ten classes, `CharSections`/
  `CharHairGeosets`/`CharacterFacialHairStyles` clones and 20 `CharStartOutfit` rows.
* server (`rev_1787850000015_alliance_illidari.sql`): `chrraces_dbc` row 31,
  `creaturedisplayinfo_dbc` 60026/60027, 20 `charstartoutfit_dbc` rows, the Night Elf
  `playercreateinfo` start (Teldrassil), the Night Elf class kit (755 spells, skills, 45 action
  rows), the outfit's skill lines, and the Night Elf quest set (2401 quests).
* masks: the client's `SkillLineAbility` language rows and the server's `SkillRaceClassInfo`
  now carry bit 30 as well (`RACE_BITS`/`HOSTS` gained race 31).

The creator's race list is client-side (`ChrRaces.alliance` + `CharBaseInfo`), so no Lua list
edit was needed - the race simply appears on the Alliance side. One cosmetic gap: both races
share the `Illidari` filestring, so they also share the Horde glue background scene, and the
Alliance one currently uses the Blood Elf Illidari model. Using the donor's NightElf_Dh model
would mean staging that model, its skins, textures and `.anim` set from Eunoia.

`add_race_name_strings.py` also defines `RACE_14`..`RACE_31` in Patch-Y's
`Interface\GlueXML\CharacterCreate.lua`, where the creator reads `_G["RACE_"..id]`; until now
the custom races were listed as "Race 16" and so on.

Backups: `patch-y-before-alliance-illidari-20260913-224819`,
`patch-y-before-language-masks-20260913-224915`,
`server-dbc-before-skillrace-20260913-224915`,
`patch-y-before-race-names-20260913-225100`.

First build after that crashed the client on boot with
`ERROR #134 ... DBFilesClient\CharBaseInfo.dbc: Cannot read string table`: the rewrite of that
table wrote `string_size = 1` in the header but dropped the single byte of pool data, so the
client refused the file. `add_alliance_illidari_client.py` now appends the pool (padding it back
to the declared size if an earlier run already truncated it), and
`validate_patch_y_dbcs.py` checks the WDBC size invariant
(`20 + rows * record + pool == file size`) for every DBC in Patch-Y - run it after any DBC edit.
All 11 entries pass now; backups `patch-y-before-alliance-illidari-20260913-225254` and
`...-225318` cover the broken and repaired archives.

Next report: the Alliance Illidari rendered with a broken (skull-like) face. The clone script
had matched `CharSections` and `CharHairGeosets` on **field 0**, which is the row *ID* in both
tables - the race lives in field 1 (`CharacterFacialHairStyles` is the odd one out, race in
field 0 and no id). Race 31 therefore had no skin/face/hair rows at all, and the client fell
back to whatever texture it could find. Cloning now uses the right column and hands the clones
fresh ids (backup `patch-y-before-alliance-illidari-20260913-225609`); race 31 carries the same
7253 `CharSections`, 46 `CharHairGeosets` and 220 `CharacterFacialHairStyles` rows as race 30.
Lesson for the next table: check which column actually holds the race before cloning.


## Helmet cubes: the head item-component path (2026-09-14, sixteenth pass)

User report: every ported race draws its helmet as the white/blue missing-model cube,
while race 14 (Broken) renders helmets normally; Dracthyr renders one but at the wrong
offset (male forward, female back).

### Root cause

`Wow.exe` builds the model name for an equipped head item in the item-component
constructor at `0x732100`:

```asm
0x0073211c  mov  esi, [ebp + 0xc]        ; equipment slot
0x0073213d  mov  edi, 0x9f6c0c           ; "Item\ObjectComponents\Head\"
0x007321e2  mov  ecx, [ecx + esi*4]      ; ChrRaces row (records at 0xad3448)
0x007321f7  mov  eax, [ecx + 0x18]       ; row + 0x18 = field 6 = ClientPrefix
0x00732202  push 0xa34d00                ; "%s%s_%s%s.mdx"
```

so the client asks for `Item\ObjectComponents\Head\<ModelName>_<ClientPrefix><M|F>.mdx`
(falling back to `.m2`), and stamps the cube when that file is missing. Field 6 is the
`ChrRaces` column the port wrote from `port_race.py`'s `"prefix"` key. Slot 3 (shoulder)
takes the other branch (`0x73221d`, format `0x9e1ad0` = `%s%s`), which is why shoulder
models carry no race suffix and were never affected.

Our port invented prefixes that no archive supplies (`Er`, `Nb`, `Ve`, `Lf`, `Za`, `Di`,
`Kt`, `Il`), so every one of those races cubed its helm. Broken worked because Patch-C
ships a full `_Bk` model set; Pandaren and Vulpera (`Pa`, `Vu`) had no set in our client
at all; Dracthyr was pointed at `Dr`, which collides with Draenei - hence a helmet that
renders but sits at the Draenei offset.

### Fix

`fix_item_component_prefixes.py` rewrites `ChrRaces` field 6 in Patch-Y to the prefixes
the donor client uses for the same races, and stages the donor's two dedicated sets:

| race | was | now | source of the model set |
|---|---|---|---|
| 14 Broken | Bk | Bk | Patch-C (already complete) |
| 15 Sethrak | Se | Tr | stock Troll set |
| 16 Eredar | Er | Dr | stock Draenei set |
| 17 Nightborne | Nb | Ni | stock Night Elf set |
| 18 Pandaren | Pa | Pa | donor `_Pa` set, staged into Patch-Y |
| 19 Void Elf | Ve | Be | stock Blood Elf set |
| 20 Vulpera | Vu | Vu | donor `_Vu` set, staged into Patch-Y |
| 21 Lightforged | Lf | Dr | stock Draenei set |
| 22 Zandalari | Za | Tr | stock Troll set |
| 23 Dark Iron | Di | Dw | stock Dwarf set |
| 28 Dracthyr | Dr | Be | stock Blood Elf set |
| 29 Kul Tiran | Kt | Ni | stock Night Elf set |
| 30 Illidari (Horde) | Il | Be | stock Blood Elf set |
| 31 Illidari (Alliance) | Il | Ni | stock Night Elf set |

Staging: 3232 files (41.4 MB) under `Item\ObjectComponents\Head\` - the donor copies
for all 423 head stems our client ships, both sexes, `.m2` + `00.skin`. 132 names the
donor has no dedicated model for (eyepatch, goggles, a few PvP sets) borrow the same stem
from a stock code so they still render instead of cubing.

Backup: `Backups/patch-y-before-item-component-prefixes-20260914-000154` (Patch-Y was
476,918,016 bytes, is now 520,427,625).

### Verification

* `verify_prefix_edit.py` diffs the new `ChrRaces` against the backup: exactly 11 fields
  changed, all field 6, all non-empty prefixes two characters.
* `validate_patch_y_dbcs.py`: 11 DBC entries, 0 malformed.
* `verify_helm_coverage.py`: for `Helm_Leather_B_06` (item 30935), `Helm_Cloth_A_01` and
  `Helm_Plate_D_02`, both sexes, model + skin, every custom race resolves a file.

### Still open

* Dracthyr helmet offset (male forward, female back) - the fix moves Dracthyr off the
  Draenei set onto the Blood Elf one; if the offset survives, the head attachment inside
  the ported Dracthyr M2 is the next suspect (`dump_m2_attachments.py` is still blind on
  these models).
* Sethrak is in `CharBaseInfo` with all ten classes but the user has never reported it on
  the creator; it now has a working prefix either way.


## Vulpera helmet placement and face (2026-09-14, seventeenth pass)

User result: helmets now render on every race.  Two Vulpera problems remain - the helmet
sits far from the head (tilted up/forward) and covers the face while it is on.

### What the data says

`Item\ObjectComponents\Head` models are anchored on M2 attachment **id 11**; the client
links head components with `push 0xb` into `CharAddAttachmentLink` (`0x4eaa70`).

* Vulpera model = Eunoia `Patch-5` `character\vulpera\male\vulperamale.m2`, byte-identical
  (13,403,570 bytes, sha1 `afff67eb445c`), `.anim` set also from `Patch-5`, donor's `_Vu`
  helmet models from `patch-I` - i.e. exactly the donor's own pairing.
* The Vulpera model is the only ported model with the old `0x28`-byte attachment records
  (id, bone, inline pivot, track); `M2.ReadAttachments` (`0x839080`) walks that stride, so
  the format is right.  Broken/Eredar/Pandaren have no such table at all.
* Its attachment 11 is bound to dummy bone 195 whose pivot is *equal* to the head key bone
  (56) pivot `(-0.116, 0.000, 1.089)` - the **neck joint**.  Every race whose helmets look
  right anchors it inside the skull instead: the human's is 0.184 above its head bone, the
  Pandaren's 0.187 below, and both carry stock-convention helmet geometry (origin near the
  top, mesh hanging down: human `_HuM` bbox z -0.402..+0.033).
* The donor's `_Vu` helmet geometry is authored around the *middle* of the helmet
  (bbox z -0.159..+0.256), i.e. for a different anchor convention than the stock sets that
  work everywhere else.
* Our `Wow.exe` is a different build from the donor's (7,716,352 vs 7,880,192 bytes), so the
  donor's rendering cannot be used as proof that the same numbers look right there.

### Fix

`fix_vulpera_head_attachment.py` stages a patched `vulperamale.m2` / `vulperafemale.m2` into
Patch-Y (the model itself stays in `Patch-C`) with attachment 11's pivot moved to the top of
the skull - the position of the model's own head-top dummy bone, `(-0.119, 0.000, 1.294)`
male and `(-0.119, 0.000, 1.291)` female.  Every attachment table in the file is rewritten
(the model carries five identical copies, six in the female).

`fix_item_component_prefixes.py --set 20=Hu` moves race 20 from `Vu` to the stock Human set,
so the Vulpera uses the same anchor convention (attachment at the top of the skull, helmet
geometry hanging down) as the races that render correctly.

Backups: `Backups/patch-y-before-vulpera-head-attachment-20260914-002407`,
`Backups/patch-y-before-item-component-prefixes-20260914-002414` (Patch-Y 547,837,826 bytes).

### Open

* If the helmet now sits correctly but the donor's Vulpera-specific shapes are wanted back,
  the `_Vu` set would have to be re-anchored (verts shifted from a centred to a top origin).
* Face features: with the helmet anchored correctly the face should no longer be covered;
  if anything still hides it, the next suspect is the helmet geoset-vis mask
  (`HelmetGeosetVisData.dbc`, 8 fields, no obvious per-race column).


## Vulpera head attachment: the table the client actually reads (2026-09-14, eighteenth pass)

The previous pass patched the wrong copy.  The Vulpera model carries several identical
23-record `id/bone/pivot` tables (at 0x171e20, 0x2e4230, 0x451b40, 0x5befb0, 0x5bf790 for
the male), but **none of them is referenced by the header** - they are leftovers.  The
attachment array the client parses is the one the header points at, and for the Vulpera that
is header slot **0xF0** (43 records at 0x674c36), the same slot that carries the human's 39
attachments at 0x859e0 (verified against the human/gnome header layout: slots 0xD8/0xE0/0xE8/
0xF0/0xF8 line up index for index).

Real values, after reading slot 0xF0 in both genders:

| model | attachment 11 bone | pivot |
|---|---|---|
| vulperamale | 195 | `(-0.001, 0.000, 1.270)` |
| vulperafemale | 195 | `(-0.119, 0.000, 1.291)` |

That anchor sits about 0.2 *above* the skull - the helm floats high, which is exactly what
the first Vulpera screenshot showed.  The unreferenced tables say `(-0.116, 0.000, 1.089)`,
which is why editing them changed nothing in game.

`retune_vulpera_helm_calibration.py` computes the ideal offset from the model itself: the
bounding box of the vertices weighted to the head bone and its descendants (ear tips above
`head bone z + 0.30` excluded, since the ears are meant to stick out) minus the helmet's own
vertex box, minus the real anchor.  Male: `dx -0.102, dz -0.099`; female: `dx +0.025,
dz -0.115`.  Seven leather-helm items (50679, 50713, 51494, 51825, 50073, 47688, 47690) carry
their own copy of the donor Vulpera leather helm, shifted around that ideal:

| item | variant | offset from the ideal |
|---|---|---|
| 50679 | A | none (computed ideal) |
| 50713 | B | 0.10 lower |
| 51494 | C | 0.10 higher |
| 51825 | D | 0.09 back |
| 50073 | E | 0.09 forward |
| 47688 | F | back + lower |
| 47690 | G | forward + lower |

All seven rows now carry the same helmet geoset-vis pair (`285`) so the comparison is about
fit only: round one's "ears and nose vanish" on 47688/47690 came from those rows' own vis
ids (248/306 and 246/307), not from the shift.

Backup: `Backups/patch-y-before-vulpera-calibration2-20260914-003909` (Patch-Y 575,924,170
bytes).


## Vulpera anchor baked in; the ear/nose vanish is geometry, not a mask (2026-09-14, nineteenth pass)

User result: the seven calibration items no longer lose ears or nose ("looks like you fixed
that"), but the real *Skullsplitter Helm* (item 1624 -> display 15340 -> `Helm_Plate_D_03`)
still swallows them.

Checked the visibility theory first: `HelmetGeosetVisData` rows 248/306 (which the
Skullsplitter uses) differ from 285, but the Vulpera model cannot respond to them at all -
`vulperamale00.skin` and `01.skin` declare **geoset 0 for every one of their 55 / 94 batches**
(`skinSection` alone runs 0..54 / 0..93), while a stock human spreads 61 batches over geosets
0..60.  A mask can only hide whole geoset groups, so it cannot remove just the muzzle and
ears; what the user saw is the plate helmet's own shell covering them while the helmet sat
about 0.2 above the skull.  `Helm_Plate_D_03_VuM/F.m2` (the donor's Vulpera-shaped plate
helm, 6,898 bytes each) is present, so the shape is right once the anchor is.

`apply_vulpera_head_anchor.py` therefore writes the computed ideal straight into attachment
11 of the model's real table (header slot 0xF0) in Patch-Y:

| model | old pivot | new pivot |
|---|---|---|
| vulperamale | `(-0.001, 0.000, 1.270)` | `(-0.103, 0.000, 1.171)` |
| vulperafemale | `(-0.119, 0.000, 1.291)` | `(-0.093, 0.000, 1.176)` |

The ten `HelmCal*` files are re-staged as small deltas around that baked value, so one more
session can refine it if needed: A = the baked value, B 0.10 lower, C 0.10 higher, D 0.09
back, E 0.09 forward, F back+lower, G forward+lower.

Backup: `Backups/patch-y-before-vulpera-anchor-20260914-004241` (Patch-Y 603,491,971 bytes).


## Vulpera on the Goblin set - tried and reverted (2026-09-14)

Set race 20 `ClientPrefix` to `Go` and staged the missing `_Go` head aliases (all 411
stems resolved). It did not help in game, so the prefix, the staged aliases, the DB row
and the scripts were reverted to the `Vu` state. The `Vu` donor set with the anchor baked
in the nineteenth pass is current again.


## Vulpera on the Gnome set (2026-09-14, twenty-first pass)

Second prefix experiment: race 20 `ClientPrefix` `Vu` -> `Gn`, with the missing `_Gn` head
aliases staged (496 donor/borrowed files plus `HelmCalA..G` copies of their `_Vu` twins).
All 411 head stems resolve; `verify_helm_coverage.py` reports race 20 all present.

Backup: `Backups/patch-y-before-vulpera-gnome-prefix-20260914-130142` (contains `REVERT.md`).
Result: superseded by the `Wo` attempt below.


## Vulpera on the Worgen set (2026-09-14, twenty-second pass)

Third prefix experiment: race 20 `ClientPrefix` `Gn` -> `Wo`, with the missing `_Wo` head
aliases staged (82 donor/borrowed files plus `HelmCalA..G` copies of their `_Vu` twins).
All 411 head stems resolve; `verify_helm_coverage.py` reports race 20 all present.

Backup: `Backups/patch-y-before-vulpera-worgen-prefix-20260914-130752` (contains `REVERT.md`).
Result (user, corrected): the HEROIC Geistlord's Punishment Sack (50713 -> 64429 ->
`HelmCalB`, 0.10 lower than the baked value) fits perfectly; the NORMAL one (50073 -> 64427
-> `HelmCalE`, 0.09 forward) does not. Both are calibration copies of the donor Vulpera
leather helm whose `_Wo` files are byte-identical to the `_Vu` ones, so the difference is
the variant offset, not the prefix: "lower" lands, "forward" does not.
Next: test `HelmCalA` (50679, the baked ideal) and `HelmCalD` (51825, 0.09 back) to see
whether the ideal floats ~0.10 high and which way the horizontal error points. A normal-model
helm (Skullsplitter, 1624 -> display 15340 -> `Helm_Plate_D_03`) is still the stock-set check.
