# Conquest of Esteria

Audit and transport plan for bringing the custom classes from:

G:\Downloads\azerothcore-wotlk-coa-main\azerothcore-wotlk-coa-main

into the current server:

R:\Users\Zach\Documents\GitHub\EsteriaWoW

Audit date: 2026-09-10

This is a read-only analysis and migration design. No source, SQL, DBC, client, or configuration files were changed by this audit.

## Executive conclusion

The donor is not a drop-in AzerothCore module and the current server does not yet contain the donor classes.

The complete transport requires three coordinated layers:

1. Core class and spell-engine changes.
2. The donor Ascension/CoA class module and its generated class data.
3. Matching world SQL plus an external client/server DBC and client UI package.

The classic WotLK classes must remain unchanged:

- Warrior: 1
- Paladin: 2
- Hunter: 3
- Rogue: 4
- Priest: 5
- Death Knight: 6
- Shaman: 7
- Mage: 8
- Warlock: 9
- Druid: 11

The donor adds real class IDs 12 through 32. ID 10 is reserved for the Ascension classless/free-pick shell and is not one of the requested classes. It must not be reused for a custom class.

The safest target architecture is an additive mod-ascension-compat module plus narrowly merged core hunks. Do not replace the current core with the donor core: the two trees differ in 142 common source files, and the current working tree already contains unrelated dirty changes.

## Audit basis and current state

### Donor tree

The downloaded donor has no Git metadata, so its exact commit and applied database state cannot be recovered from the directory itself.

The donor contains:

- One module directory: modules/mod-ascension-compat.
- 224 module source/header files, approximately 2.74 MB.
- 19 class/release documents, approximately 145 KB.
- Five Manastorm/bug-report test files.
- Three module SQL files:
  - one character-database collections schema;
  - one approximately 25.5 MB appearance/item-template snapshot;
  - one custom-class identity/race/stats/action schema.
- A large set of root pending world SQL migrations covering class bootstrapping and per-class completion.
- No MPQ files.
- No DBC files.
- No client executable or DLL.
- No client Glue/UI addon.
- No CharacterAdvancementData.json source input used to generate the embedded class arrays.

The donor README describes mod-ascension-compat as a compatibility boundary for a copied Ascension 3.3.5a client. It also explicitly warns that source presence is not proof of official backend parity or complete gameplay parity.

Important packaging defect: modules/mod-ascension-compat has no CMakeLists.txt or module-specific CMake file. The normal root CMake module scan only adds module directories that are build-wired. As received, this donor module is therefore a source package, not a confirmed buildable module.

### Current server tree

The current checkout is Git branch main at commit 760fbfa.

The working tree is dirty with existing core, module, SQL, log, DBC, and asset changes. Those changes belong to the current server and must be preserved.

The current core still has:

- class IDs 1 through 11 only;
- MAX_CLASSES = 12;
- the stock CLASSMASK_ALL_PLAYABLE;
- no CLASS_BARBARIAN through CLASS_SPIRIT_MAGE definitions;
- no donor Ascension class source;
- no donor class pending SQL package.

The current checkout does contain modules/mod-custom-server source, but that directory has no CMakeLists.txt; static source presence must not be treated as proof that its C++ is in the runtime image. The current mod-wxl-dbc directory is separately present as an untracked, build-wired module and must be preserved when merging class DBC support.

The current root Spell.dbc is:

- SHA-256: D5CCE1A83550DCFA9EB2F0251DBB11FD24C272534B2B1A9B230924A44D817AB3;
- 49,839 records;
- maximum spell ID 80,864;
- no records with IDs at or above 500,000.

The donor class source references custom spell IDs such as 500002, 680441, 800058, 801816, 807389, and 804972. All of those are absent from the current root Spell.dbc.

The donor class completion documents reference a different effective server Spell.dbc hash:

7651A1FC8C13640268F8E316917379AECB234F8AD5B52CC9801C0A0D68A16FE7

That DBC is not present in the donor directory and must be obtained or reconstructed from the matching external CoA data package.

A source-to-source hash comparison found:

- 1,763 donor src files considered;
- 1,618 identical to the current server;
- 142 different;
- three present only in the donor:
  - src/server/game/Entities/Player/LiveClassResourcePolicy.h
  - src/server/game/Miscellaneous/LocalLevelScaling.h
  - src/server/game/Spells/SpellChargeState.h

The 142 differences are not all class-related. They include unrelated upstream/core changes, so whole-file replacement would overwrite current functionality.

## Complete custom-class inventory

The donor class enum maps internal legacy-style identifiers to different player-facing class names in several cases. The internal identifier is part of the saved/server contract and must not be casually renamed.

The ClassSpells array contains 844 current class-spell entries. Counts below are the entries per class in that array.

| ID | Internal enum | Client name | Fallback class | Base power | Custom resource/state | Dedicated donor source | ClassSpells |
| ---: | --- | --- | --- | --- | --- | --- | ---: |
| 12 | CLASS_BARBARIAN | Barbarian | Rogue | Energy | Barbarian resource, aura 805813, max 10 | AscensionBarbarian prefix, 8 files | 29 |
| 13 | CLASS_WITCH_DOCTOR | Witch Doctor | Shaman | Mana | Class-specific brewing, auras, summons | AscensionWitchDoctor prefix, 8 files | 45 |
| 14 | CLASS_DEMON_HUNTER | Felsworn | Rogue | Energy | Felfury, aura 800058 | AscensionFelsworn prefix, 8 files | 46 |
| 15 | CLASS_WITCH_HUNTER | Witch Hunter | Hunter | Mana | Rage/tonics/torch and field state | AscensionWitchHunter prefix, 20 files | 37 |
| 16 | CLASS_STORMBRINGER | Stormbringer | Shaman | Mana | Static, aura 803102, max 100 | Shared mechanics/data only | 40 |
| 17 | CLASS_FLESHWARDEN | Knight of Xoroth | Warrior | Rage | Demonfire, aura 500906, max 6 | AscensionXoroth prefix, 8 files | 43 |
| 18 | CLASS_GUARDIAN | Guardian | Warrior | Energy | Formations, shield, standards, favor | AscensionGuardian prefix, 11 files | 45 |
| 19 | CLASS_MONK | Templar | Rogue | Energy | Oath chain and combo auras | AscensionTemplar prefix, 11 files | 34 |
| 20 | CLASS_SON_OF_ARUGAL | Bloodmage | Druid | Rage | Bloodmage resource and Blood Thirst | Shared generated data only | 38 |
| 21 | CLASS_RANGER | Ranger | Hunter | Focus | Advantage, aura 804329, max 5 | AscensionRanger prefix, 4 files | 39 |
| 22 | CLASS_CHRONOMANCER | Chronomancer | Priest | Mana | Echo Fragment, aura 804455, max 5 | Shared 19–25 mechanics/data | 34 |
| 23 | CLASS_NECROMANCER | Necromancer | Warlock | Runic Power | Life Force and owned minion occupancy | AscensionNecromancer prefix, 8 files | 45 |
| 24 | CLASS_PYROMANCER | Pyromancer | Mage | Mana | Heat 807389, Ember 807533 | AscensionPyromancer prefix, 8 files | 34 |
| 25 | CLASS_CULTIST | Cultist | Paladin | Mana | Insanity 500706, Void Rune 800431 | AscensionCultist prefix, 8 files | 41 |
| 26 | CLASS_STARCALLER | Starcaller | Druid | Energy | Lunar Phase, aura 802985 | AscensionStarcaller prefix, 8 files | 39 |
| 27 | CLASS_SUN_CLERIC | Sun Cleric | Priest | Mana | Solar Power 500149 and Sunset 804584 | AscensionSunCleric prefix, 8 files | 40 |
| 28 | CLASS_TINKER | Tinker | Hunter | Mana | Scrap, aura 801816, max 100 | AscensionTinker prefix, 19 files | 39 |
| 29 | CLASS_PROPHET | Venomancer | Shaman | Mana | Brood Mark, aura 804972, max 5 | AscensionVenomancer prefix, 19 files | 51 |
| 30 | CLASS_REAPER | Reaper | Rogue | Runic Power | Reaped Soul, Soul Fragment, Soul Infusion | AscensionReaper prefix, 8 files | 38 |
| 31 | CLASS_WILDWALKER | Primalist | Druid | Mana | Earthshaping, aura 680441, max 15 | AscensionPrimalist prefix, 4 files | 41 |
| 32 | CLASS_SPIRIT_MAGE | Runemaster | Shaman | Mana | Arcane/fire/frost sigils | AscensionRunemaster prefix, 12 files | 46 |

The internal names that differ from the player-facing names are intentional:

| Internal ID/name | Player-facing name |
| --- | --- |
| 14 / Demon Hunter | Felsworn |
| 17 / Fleshwarden | Knight of Xoroth |
| 19 / Monk | Templar |
| 20 / Son of Arugal | Bloodmage |
| 29 / Prophet | Venomancer |
| 31 / Wildwalker | Primalist |
| 32 / Spirit Mage | Runemaster |

Do not introduce a CLASS_VENOMANCER constant or remap class 29 without updating every server, SQL, DBC, client, and saved-character reference.

### Resource manifest

The donor resource service is not a simple mana/rage switch. It combines native power bars, aura-stack resources, thresholds, event-driven gains, costs, and custom client state.

The generated resource data contains:

- 32 resource-display rows;
- seven threshold rules;
- 165 aura/resource gain rules;
- 16 native-power gain rules;
- 55 resource-cost rules.

The resource displays are:

| Class | Resource display |
| --- | --- |
| Barbarian | 805813, max 10 |
| Felsworn | 800058 Felfury |
| Stormbringer | 803102 Static, max 100 |
| Knight of Xoroth | 500906 Demonfire, max 6 |
| Templar | 704576 Oath chain plus five combo auras |
| Bloodmage | 680687 resource and 706613 Blood Thirst |
| Ranger | 804329 Advantage, max 5 |
| Chronomancer | 804455 Echo Fragment, max 5 |
| Necromancer | 525004 visual Life Force and 805011 total Life Force |
| Pyromancer | 807389 Heat and 807533 Ember |
| Cultist | 500706 Insanity and 800431 Void Rune |
| Starcaller | 802985 Lunar Phase |
| Sun Cleric | 500149 Solar Power and 804584 Sunset |
| Tinker | 801816 Scrap, max 100 |
| Venomancer | 804972 Brood Mark, max 5 |
| Reaper | 500363 Reaped Soul, 805077 Soul Fragment, 803031 Soul Infusion |
| Primalist | 680441 Earthshaping, max 15 |
| Runemaster | 500282/500271/500285 arcane/fire/frost sigils |

Witch Doctor and Witch Hunter primarily use native power types plus class-specific auras rather than a row in this display table.

## Donor source layout

### Common class/runtime source

These files are shared dependencies and must be included for a complete class port:

- modules/mod-ascension-compat/src/AscensionCompat.cpp
  - custom-class creation;
  - starter kits;
  - class spell progression;
  - specialization/talent handling;
  - proficiency synchronization;
  - resource costs/gains/thresholds;
  - class repair and diagnostic commands;
  - client authentication/resource messages;
  - collection, mount, local scaling, and tradesman code in the same translation unit.
- AscensionClassMechanics.cpp
- AscensionClassMechanics12To17.cpp
- AscensionClassMechanics19To25.cpp
- AscensionClassMechanics26To32.cpp
- AscensionConditionalCombat.cpp and .h
- AscensionAuraAmounts.cpp and .h
- AscensionHealingStatSelectors.cpp and .h
- AscensionChangelogCompat.cpp and .h
- AscensionChangelogData.h
- AscensionCustomClassData.h
- AscensionCustomResourceData.h
- AscensionCoATalentData.h
- AscensionSpellProgressionData.h
- AscensionTaughtAbilityData.h
- AscensionLiveBaselineData.h
- AscensionFreshCharacterCheck.cpp and .h
- AscensionFreshCharacterExpectations.h
- AscensionAmmunitionData.h
- MP_loader.cpp

The generated arrays are important runtime data, not documentation:

- AscensionCustomClassData.h:
  - 844 current class spells;
  - 270 legacy-generated class spells;
  - 50 obsolete class spells;
  - 142 unresolved trainer spells;
  - 127 class proficiency rows;
  - 14 talent-to-proficiency rows;
  - 21 legacy starter kits;
  - 206 exact live starter-item placements.
- AscensionSpellProgressionData.h:
  - 2,709 rank/progression rows.
- AscensionCoATalentData.h:
  - 3,618 talent-entry rows;
  - eight selectable-free entries;
  - 25 automatic dependency rows.
- AscensionLiveBaselineData.h:
  - 315 baseline spells;
  - 449 class skill rows;
  - 243 proficiency rows;
  - 25 unresolved skills.
- AscensionFreshCharacterExpectations.h:
  - one expected fresh-character case for each of the 21 custom classes;
  - expected health, stats, active power, and power maxima.

### Per-class source surfaces

The donor has complete dedicated source groups for most classes:

- Barbarian:
  - AscensionBarbarian.cpp/.h
  - AscensionBarbarianAbilities.cpp
  - AscensionBarbarianCompletion.cpp/.h
  - AscensionBarbarianEvents.cpp
  - AscensionBarbarianScaling.cpp/.h
- Witch Doctor:
  - AscensionWitchDoctorAbilities.cpp
  - AscensionWitchDoctorAuras.cpp
  - AscensionWitchDoctorBrewing.cpp
  - AscensionWitchDoctorCoefficients.h
  - AscensionWitchDoctorCompletion.cpp/.h
  - AscensionWitchDoctorEvents.cpp
  - AscensionWitchDoctorSummons.cpp
- Felsworn:
  - AscensionFelsworn.cpp/.h
  - AscensionFelswornAbilities.cpp
  - AscensionFelswornAuras.cpp
  - AscensionFelswornContracts.cpp
  - AscensionFelswornData.h
  - AscensionFelswornEvents.cpp
  - AscensionFelswornSummons.cpp
- Witch Hunter:
  - AscensionWitchHunterAbilities.cpp
  - Coefficient, completion, defenses, events, flames, scaling, stake, summons, targeting, tonics, tonic talents, torch, and torchlight files.
- Knight of Xoroth:
  - AscensionXoroth.cpp/.h
  - AscensionXorothAbilities.cpp
  - AscensionXorothAuras.cpp
  - AscensionXorothContracts.cpp
  - AscensionXorothData.h
  - AscensionXorothEvents.cpp
  - AscensionXorothSummons.cpp
- Guardian:
  - AscensionGuardianAbilities.cpp
  - AscensionGuardianCompletion.cpp/.h
  - AscensionGuardianDrums.cpp
  - AscensionGuardianEvents.cpp
  - AscensionGuardianFavor.cpp
  - AscensionGuardianResources.cpp/.h
  - AscensionGuardianStandardData.h
  - AscensionGuardianStandards.cpp
  - AscensionGuardianTalents.cpp
- Templar:
  - AscensionTemplar.cpp/.h
  - AscensionTemplarAbilities.cpp
  - AscensionTemplarAuras.cpp
  - AscensionTemplarContracts.cpp
  - AscensionTemplarData.h
  - AscensionTemplarEvents.cpp
  - AscensionTemplarLibrams.cpp/.h
  - AscensionTemplarSummons.cpp
  - AscensionTemplarTemporaryLibramProcs.cpp
- Ranger:
  - AscensionRangerAssault.cpp
  - AscensionRangerDamage.cpp/.h
  - AscensionRangerScaling.cpp
- Necromancer:
  - AscensionNecromancer.cpp/.h
  - AscensionNecromancerAbilities.cpp
  - AscensionNecromancerAuras.cpp
  - AscensionNecromancerContracts.cpp
  - AscensionNecromancerData.h
  - AscensionNecromancerEvents.cpp
  - AscensionNecromancerSummons.cpp
- Pyromancer:
  - AscensionPyromancer.cpp/.h
  - AscensionPyromancerAbilities.cpp
  - AscensionPyromancerAuras.cpp
  - AscensionPyromancerContracts.cpp
  - AscensionPyromancerData.h
  - AscensionPyromancerEvents.cpp
  - AscensionPyromancerSummons.cpp
- Cultist:
  - AscensionCultist.cpp/.h
  - AscensionCultistAbilities.cpp
  - AscensionCultistAuras.cpp
  - AscensionCultistContracts.cpp
  - AscensionCultistData.h
  - AscensionCultistEvents.cpp
  - AscensionCultistSummons.cpp
- Starcaller:
  - AscensionStarcaller.cpp/.h
  - AscensionStarcallerAbilities.cpp
  - AscensionStarcallerAuras.cpp
  - AscensionStarcallerContracts.cpp
  - AscensionStarcallerData.h
  - AscensionStarcallerEvents.cpp
  - AscensionStarcallerMechanics.cpp
- Sun Cleric:
  - AscensionSunCleric.cpp/.h
  - AscensionSunClericAbilities.cpp
  - AscensionSunClericAuras.cpp
  - AscensionSunClericContracts.cpp
  - AscensionSunClericData.h
  - AscensionSunClericEvents.cpp
  - AscensionSunClericSummons.cpp
- Tinker:
  - AscensionTinker.cpp/.h
  - AscensionTinkerAbilities.cpp
  - AscensionTinkerAugmentations.cpp
  - AscensionTinkerAugmentationTalents.cpp
  - AscensionTinkerAuras.cpp
  - AscensionTinkerCombatSymbiosis.cpp/.h
  - AscensionTinkerCombustion.cpp/.h
  - AscensionTinkerContracts.cpp
  - AscensionTinkerData.h
  - AscensionTinkerEvents.cpp
  - AscensionTinkerHacking.cpp
  - AscensionTinkerOverload.cpp/.h
  - AscensionTinkerRockadier.cpp/.h
  - AscensionTinkerSummons.cpp
- Venomancer:
  - AscensionVenomancer.cpp/.h
  - AscensionVenomancerAbilities.cpp
  - AscensionVenomancerAuras.cpp
  - AscensionVenomancerCatalyst.cpp/.h
  - AscensionVenomancerContracts.cpp
  - AscensionVenomancerData.h
  - AscensionVenomancerEvents.cpp
  - AscensionVenomancerSummons.cpp
  - AscensionVenomancerVenomData.h
  - AscensionVenomancerVenomPayloads.cpp/.h
  - AscensionVenomancerVenomProcs.cpp/.h
  - AscensionVenomancerVenoms.cpp/.h
  - AscensionVenomancerVenomTalents.cpp/.h
- Reaper:
  - AscensionReaperDeathwind.cpp/.h
  - AscensionReaperDirge.cpp/.h
  - AscensionReaperPainmail.cpp/.h
  - AscensionReaperSoulStrike.cpp/.h
- Primalist:
  - AscensionPrimalistEarthshaping.cpp/.h
  - AscensionPrimalistSpiritBeast.cpp/.h
- Runemaster:
  - AscensionRunemasterBrand.cpp/.h
  - AscensionRunemasterDamageModifiers.cpp/.h
  - AscensionRunemasterEchoes.cpp/.h
  - AscensionRunemasterGlyphs.cpp/.h
  - AscensionRunemasterScaling.cpp/.h
  - AscensionRunemasterZenith.cpp/.h

There are no dedicated AscensionStormbringer, AscensionBloodmage, or AscensionChronomancer source prefixes. Their spell/progression/resource entries are in shared generated data and cross-class mechanics. Chronomancer also has explicit shared handling in AscensionClassMechanics19To25.cpp. Those three classes require their own acceptance tests; a source-file prefix count must not be used as a reason to omit them.

### Loader registration

Every class source group is registered from MP_loader.cpp. The loader calls:

- common compatibility/resource/bug-report services;
- Barbarian completion, event, and ability scripts;
- Guardian standards, favor, events, completion, abilities, talents, and drums;
- Ranger damage, scaling, and assault;
- Witch Hunter tonics, tonic talents, torch, flames, torchlight, stake, completion, events, abilities, defenses, and summons;
- Witch Doctor completion, events, abilities, brewing, auras, and summons;
- Necromancer base, contracts, summons, events, abilities, and auras;
- Xoroth, Starcaller, Pyromancer, Cultist, Venomancer, Tinker, Sun Cleric, Felsworn, and Templar groups;
- Reaper Dirge, Tinker Overload, Runemaster Glyphs/Brand/Scaling/Zenith/Echoes;
- Primalist Earthshaping/Spirit Beast;
- Venomancer Catalyst/Venoms;
- Tinker augmentations, augmentation talents, Hacking, Rockadier, Combustion, and Combat Symbiosis.

A missing loader call makes a class feature inert while still allowing the server to compile. Loader coverage is therefore a required acceptance check.

## Core changes required for the class port

The donor core has class-aware changes spread through the gameplay and spell engine. These need three-way merging into the current core.

### Identity and class capacity

Required donor behavior:

- Add class IDs 12–32 to src/server/shared/SharedDefines.h.
- Set MAX_CLASSES to 33.
- Use the 32-bit playable mask that includes IDs 1–9, 11–32 and excludes ID 10.
- Add IsAscensionClass().
- Add GetLegacyClassForCustomClass() fallback mappings.
- Update src/server/shared/enuminfo_SharedDefines.cpp:
  - class names;
  - enum index mapping;
  - enum count of 31 playable classes, excluding the reserved classless ID 10.

The real class ID must remain in the player record. Fallback mappings are only for legacy core paths such as stats, skills, relics, armor, shields, and weapon handling.

The current core already has a ClassContext and OnPlayerIsClass script seam. Reuse it. The donor module supplies the custom-class answers for contexts where a custom class should behave like its fallback class while retaining its own identity for class abilities and persistence.

### Player creation, progression, and persistence

Required donor pieces:

- src/server/game/Entities/Player/Player.h
- src/server/game/Entities/Player/Player.cpp
- src/server/game/Spells/SpellChargeState.h
- src/server/game/Entities/Player/LiveClassResourcePolicy.h

They provide or support:

- correct default power for custom classes;
- Ranger Focus regeneration;
- creation-only live baseline spells, skills, and proficiencies;
- exact live starter item placement;
- custom-class item repair;
- temporary spell replacements without destroying permanent ownership;
- class/rank progression;
- spell-charge storage in PlayerSettings;
- charge recovery and restoration;
- client charge-state packets;
- custom class equipment/range behavior;
- no-ammo custom ranged attacks;
- custom active-power/form transitions.

Custom class resources are mainly auras and native powers, not a new database column. They still depend on normal character aura, character spell, action-bar, and player-setting persistence.

The donor class service deliberately limits login reconciliation to its own generated class grants. It should not be allowed to remove arbitrary quest rewards, purchased spells, or unrelated custom-server spells from classic characters.

The donor specialization map is held in memory and cleared on logout. The source provides local specialization/talent commands and client authentication, but no complete custom character-advancement packet implementation is visible in this module. Persistent talent/spec replay must be tested and may require a separate client integration.

### Unit and stat/combat engine

Required donor files include:

- src/server/game/Entities/Unit/Unit.h
- src/server/game/Entities/Unit/Unit.cpp
- src/server/game/Entities/Unit/StatSystem.cpp
- src/server/game/AI/CreatureAISelector.cpp

The changes cover:

- custom-class fallback decisions;
- 32-bit class masks, including class ID 32 bit handling;
- class-specific attack power and ranged attack power;
- class-specific spell-power and healing coefficients;
- stat-from-stat and max-mana-from-stat aura conversions;
- custom crit, guaranteed-crit, ignore-armor, resilience, and conditional combat behavior;
- resolved damage/healing copies without double coefficients;
- actual-damage/effective-healing proc routing;
- custom melee range and polearm behavior;
- no-ammo ranged damage;
- custom pet, summon, charm, and class-specific creature AI selection;
- owner-based minion health, armor, threat, and damage;
- conditional movement/channel behavior;
- custom class-specific power receipt.

The current getClassMask implementation must be checked for safe unsigned shifting through class 32. The donor changes it to a uint32 shift.

### Spell and aura engine

Required donor changes include:

- src/server/game/Spells/SpellDefines.h
- src/server/game/Spells/SpellInfo.h
- src/server/game/Spells/SpellInfo.cpp
- src/server/game/Spells/Spell.h
- src/server/game/Spells/Spell.cpp
- src/server/game/Spells/SpellEffects.cpp
- src/server/game/Spells/SpellMgr.cpp
- src/server/game/Spells/Auras/SpellAuraDefines.h
- src/server/game/Spells/Auras/SpellAuraEffects.h
- src/server/game/Spells/Auras/SpellAuraEffects.cpp
- src/server/game/Spells/Auras/SpellAuras.cpp

The donor extends the 3.3.5 spell model:

- spell effects through ID 198;
- TOTAL_SPELL_EFFECTS = 199;
- Ascension effect handlers for cooldown changes, mana/health restore, aura refresh, aura stacks, aura duration, delayed triggers, cooldown reset, and spell-charge restoration;
- auras through ID 366;
- Ascension aura handlers for stat conversions, max-mana conversions, hit chance, flat AP/SP, crit, ignore armor, absorb, healing received, and instant mana-cost changes;
- AURA_STATE_ASCENSION_POISONED;
- SPELLMOD_MAX_AURA_STACKS;
- SPELLMOD_SPELL_COST_REFUND_ON_FAIL;
- SPELLVALUE_MELEE_ATTACK_TYPE;
- custom SpellInfo flags:
  - UseRangedAttackPowerForDamage;
  - UsesMaxManaForCost;
  - AscensionIgnoreAbsorbAndResistance;
  - AscensionIgnoreAbsorb;
  - AscensionInheritsResolvedAmount;
  - IgnoreSpellLevelPenalty;
  - charge recovery key/category/time/max charges;
  - IsDeprecatedForPlayers;
- per-cast script snapshots and one-shot event guards;
- custom damage/healing result fields;
- family matching for custom class spell families 18 through 38.

Not every extended effect is implemented by the core. Unknown donor effects are intentionally safe/no-op until a class-specific script owns them. The final DBC and the class scripts must therefore be kept synchronized.

The donor uses class family number equal to class ID plus six for many class checks:

- Barbarian family 18;
- Witch Doctor family 19;
- Felsworn family 20;
- Witch Hunter family 21;
- Stormbringer family 22;
- Knight of Xoroth family 23;
- Guardian family 24;
- Templar family 25;
- Bloodmage family 26;
- Ranger family 27;
- Chronomancer family 28;
- Necromancer family 29;
- Pyromancer family 30;
- Cultist family 31;
- Starcaller family 32;
- Sun Cleric family 33;
- Tinker family 34;
- Venomancer family 35;
- Reaper family 36;
- Primalist family 37;
- Runemaster family 38.

### Script hook API

The donor adds hook declarations, dispatchers, and call sites. The current core has some existing script hooks, but the donor-specific hooks below are not present in the current server’s normal script API and must be merged:

AllSpellScript:

- ALLSPELLHOOK_ON_BEFORE_EFFECTS;
- ALLSPELLHOOK_ON_CALCULATED_TARGET;
- ALLSPELLHOOK_ON_HIT_RESULT;
- ALLSPELLHOOK_ON_SUCCESSFUL_INTERRUPT;
- ALLSPELLHOOK_ON_SUCCESSFUL_STEAL;
- ALLSPELLHOOK_ON_INTERRUPT_DURATION;
- ALLSPELLHOOK_ON_CRIT_CHANCE.

UnitScript:

- UNITHOOK_ON_BLOCK;
- UNITHOOK_ON_PERIODIC_DAMAGE_RESULT;
- UNITHOOK_MODIFY_SPELL_EFFECT_BASE_VALUE;
- UNITHOOK_CAN_UNIT_ATTACK;
- UNITHOOK_SPELL_MAGNET_TARGET;
- UNITHOOK_ON_SEND_AURA_UPDATE.

PlayerScript:

- PLAYERHOOK_ON_CREATE_INITIAL_ITEMS;
- PLAYERHOOK_ON_GET_AMMO_DISPLAY;
- PLAYERHOOK_ON_NORMALIZE_ACTION_BUTTON_SPELL;
- PLAYERHOOK_ON_SPELL_CHARGE_CONSUMED;
- PLAYERHOOK_ON_SPELL_COOLDOWN_CALCULATED.

The corresponding changes are in:

- src/server/game/Scripting/ScriptDefines/AllSpellScript.h/.cpp;
- src/server/game/Scripting/ScriptDefines/UnitScript.h/.cpp;
- src/server/game/Scripting/ScriptDefines/PlayerScript.h/.cpp;
- src/server/game/Scripting/ScriptMgr.h;
- spell, player, aura, and unit call sites.

These hooks are not cosmetic. The class code uses them to:

- spend and restore resources after native validation;
- distinguish a miss from a failed cast;
- snapshot damage before effects;
- add targets to one native spell instance;
- observe successful interrupts and spell steals;
- alter crit chance before the native roll;
- admit periodic damage and block events;
- modify base values before native effect modifiers;
- block invalid class targeting;
- send custom aura amounts;
- install exact creation items;
- preserve temporary action-bar replacements;
- maintain custom spell charges.

### Client/network compatibility core

These donor files are relevant only if the target is the copied Ascension/CoA client rather than a stock WotLK client:

- src/server/apps/authserver/Server/AuthSession.cpp/.h;
- src/server/game/Server/WorldSocket.cpp;
- src/server/game/Handlers/CharacterHandler.cpp;
- related ScriptMgr and packet call sites.

They support:

- the local Ascension authentication challenge;
- loopback-only plaintext world headers;
- extension opcode ranges 1311 through 2515;
- classless class 10 mapping to a warrior shell;
- custom spell-modifier packet layout;
- custom character-advancement authentication;
- custom appearance/resource/charge messages.

Plaintext compatibility must remain restricted to the intended loopback/local client path. It must not become a general remote-server bypass.

The donor’s CharacterDatabase.cpp additions are primarily Manastorm persistence statements, not custom-class requirements. Do not add them unless Manastorm is intentionally included.

## SQL and database transport

### Database rules

For the current repository:

- New world SQL belongs in data/sql/updates/pending_db_world or the owning module’s database directory.
- Do not edit data/sql/base.
- Do not edit data/sql/archive.
- Do not edit merged data/sql/updates/db_* files.
- Do not use mysql --force for a generated migration.
- Take a database backup before applying any class package.
- Preserve the persistent Docker volumes.
- Never use docker compose down -v for this work.

The donor pending files contain broad DELETE, REPLACE, and generated snapshot operations. They are not safe to apply merely because they are named pending.

### Class foundation SQL

The donor contains multiple overlapping class bootstrap mechanisms. They must be reconciled, not stacked blindly.

modules/mod-ascension-compat/data/sql/db-world/2026_08_27_00_ascension_custom_classes.sql:

- creates ascension_custom_class;
- creates ascension_custom_class_race;
- inserts 21 class identity rows;
- inserts 124 allowed class/race pairs;
- creates playercreateinfo rows for those pairs from existing racial starts;
- copies fallback player_class_stats rows to classes 12–32;
- adds Attack action 6603 to the custom class creation rows;
- deletes/rebuilds class 12–32 rows in its own tables.

data/sql/updates/pending_db_world/rev_1787754600000000000.sql:

- creates ascension_custom_class_spell;
- contains a generated class spell catalog;
- adds custom item templates used by class starter data;
- adds playercreateinfo_item rows;
- adds playercreateinfo_spell_custom rows;
- carries 229 observed class bootstrap tuples, 82 item-template tuples, 106 starter-item tuples, and 196 starting-spell tuples in the received file.

data/sql/updates/pending_db_world/rev_20260831_03_local_class_starters.sql:

- adds one starter roster block for each class ID 12–32;
- uses race 0 class-wide starter rows;
- carries older/deprecated baseline cleanup rows.

data/sql/updates/pending_db_world/rev_20260903_01_live_class_baseline.sql:

- uses temporary before/after tables and an exact guard;
- synchronizes live class baseline spells, skills, proficiencies, stats, and rank data;
- is a generated snapshot, not a general-purpose migration;
- must be compared against the target database before reuse.

data/sql/updates/pending_db_world/rev_20260831_01_local_spell_progression.sql:

- supplies the SQL spell_ranks snapshot corresponding to the 2,709 generated rank rows.

data/sql/updates/pending_db_world/rev_20260831_02_local_coa_changelog.sql:

- supplies reviewed spell_bonus_data changes from the local CoA changelog audit.

data/sql/updates/pending_db_world/rev_20260906_03_any_race_class.sql:

- adds 86 selected playercreateinfo class/race rows;
- is not the same matrix as the 124-row ascension_custom_class_race table;
- must not be stacked with the 124-row policy without an explicit reconciliation.

The target should use one reviewed class/race manifest. For the stated goal of bringing all donor class options over, the donor module’s 124-row matrix is the broader explicit policy. It covers only stock race IDs and does not cover the current server’s custom race IDs 12 through 27.

### Donor class/race matrix

Race IDs used by the donor matrix:

- 1 Human
- 2 Orc
- 3 Dwarf
- 4 Night Elf
- 5 Undead
- 6 Tauren
- 7 Gnome
- 8 Troll
- 10 Blood Elf
- 11 Draenei

The 124 donor-approved pairs are:

| Class | Allowed donor race IDs |
| --- | --- |
| 12 Barbarian | 1, 2, 3, 5, 6, 8 |
| 13 Witch Doctor | 1, 2, 8 |
| 14 Felsworn | 2, 4, 10, 11 |
| 15 Witch Hunter | 1, 4, 5 |
| 16 Stormbringer | 1, 2, 3, 5, 6, 7, 8, 10, 11 |
| 17 Knight of Xoroth | 2, 10, 11 |
| 18 Guardian | 1, 2, 3, 4, 5, 6, 8, 10, 11 |
| 19 Templar | 1, 3, 5, 10, 11 |
| 20 Bloodmage | 1, 4, 5, 8, 10 |
| 21 Ranger | 1, 2, 3, 4, 5, 7, 8, 10 |
| 22 Chronomancer | 1, 7, 10, 11 |
| 23 Necromancer | 1, 2, 5, 7, 8, 10, 11 |
| 24 Pyromancer | 1, 2, 3, 4, 5, 6, 7, 8, 10, 11 |
| 25 Cultist | 1, 2, 3, 4, 5, 6, 7, 8, 10, 11 |
| 26 Starcaller | 4, 6, 10, 11 |
| 27 Sun Cleric | 1, 3, 6, 10 |
| 28 Tinker | 1, 2, 3, 5, 7, 10, 11 |
| 29 Venomancer | 4, 5, 8 |
| 30 Reaper | 1, 5, 8, 10, 11 |
| 31 Primalist | 2, 3, 4, 6, 8, 11 |
| 32 Runemaster | 1, 2, 3, 4, 5, 6, 7, 10, 11 |

There is no donor class/race row for Goblin race 9 or for the current custom races. If custom classes must also be available to Worgen, High Elf, Broken, Sethrak/Ogre, Eredar, Nightborne, Void Elf, Vulpera, Zandalari, Pandaren, Forsaken, Lightforged, or Dark Iron, that is a separate race/class expansion and client-data task.

### Per-class and shared world SQL

The following donor world SQL files contain class behavior bindings, coefficients, procs, templates, models, rank links, or group rules. They must be migrated as a dependency set after target collision checks.

Early/shared package:

- rev_1788102000000000000.sql
- rev_20260906_01_barbarian_damage_coefficients.sql
- rev_20260906_02_guardian_standards.sql
- rev_20260906_03_any_race_class.sql
- rev_20260907_01_class_parity_ranger_aspects.sql
- rev_20260907_02_exclusive_self_buffs.sql
- rev_20260907_08_raid_power_buffs.sql
- rev_20260907_11_allied_buff_exclusivity.sql
- rev_20260907_19_progression_rank_case.sql
- rev_20260908_01_guardian_coefficients.sql
- rev_20260908_02_guardian_favor.sql
- rev_20260908_05_guardian_completion.sql
- rev_20260908_06_barbarian_completion.sql
- rev_20260908_07_witch_hunter_completion.sql
- rev_20260908_08_class_completion_runtime.sql
- rev_20260909_08_class_block_proc_admission.sql
- rev_20260909_09_class_startup_validation.sql
- rev_20260909_10_raid_damage_reduction_group.sql

Ranger and Witch Hunter:

- rev_20260907_03_ranger_rusty_shiv.sql
- rev_20260907_04_ranger_skullpiercer.sql
- rev_20260907_05_ranger_underhanded.sql
- rev_20260907_06_ranger_instinctual_combatant.sql
- rev_20260907_07_ranger_assault_damage.sql
- rev_20260907_09_witch_hunter_tonics.sql
- rev_20260907_10_witch_hunter_tonic_supply.sql
- rev_20260907_12_witch_hunter_tonic_procs.sql
- rev_20260907_13_witch_hunter_torch.sql
- rev_20260907_14_witch_hunter_flames.sql
- rev_20260907_15_witch_hunter_torchlight.sql
- rev_20260907_16_witch_hunter_flourish.sql
- rev_20260907_17_witch_hunter_spellpower.sql
- rev_20260907_18_witch_hunter_stake.sql

Tinker, Primalist, Runemaster, Venomancer, and Reaper:

- rev_20260907_20_tinker_augmentations.sql
- rev_20260907_21_primalist_earthshaping.sql
- rev_20260907_22_runemaster_glyphs.sql
- rev_20260907_23_venomancer_catalyst.sql
- rev_20260907_24_runemaster_brand.sql
- rev_20260907_26_tinker_augmentation_talents.sql
- rev_20260907_27_reaper_deathwind.sql
- rev_20260907_28_runemaster_scaling.sql
- rev_20260907_29_tinker_hacking.sql
- rev_20260907_30_tinker_rockadier.sql
- rev_20260907_31_primalist_spirit_beast.sql
- rev_20260907_32_runemaster_zenith.sql
- rev_20260907_33_tinker_combat_symbiosis.sql
- rev_20260907_34_primalist_king_mountain.sql
- rev_20260907_35_tinker_overload.sql
- rev_20260907_36_reaper_dirge.sql
- rev_20260907_37_runemaster_echoes.sql
- rev_20260907_38_tinker_combustion.sql
- rev_20260907_39_venomancer_venoms.sql

Later class completion:

- rev_20260909_00_witch_doctor_completion.sql
- rev_20260909_01_necromancer_completion.sql
- rev_20260909_02_necromancer_runtime.sql
- rev_20260909_03_necromancer_summon_sizes.sql
- rev_20260909_04_templar_completion.sql
- rev_20260909_05_felsworn_completion.sql
- rev_20260909_06_starcaller_completion.sql
- rev_20260909_07_knight_of_xoroth_completion.sql
- rev_20260909_11_pyromancer_completion.sql
- rev_20260909_12_cultist_completion.sql
- rev_20260909_13_sun_cleric_completion.sql
- rev_20260910_14_venomancer_completion.sql
- rev_20260910_15_tinker_completion.sql

These files collectively touch:

- spell_bonus_data;
- spell_proc;
- spell_script_names;
- spell_linked_spell;
- spell_group;
- spell_group_stack_rules;
- spell_ranks;
- creature_template;
- creature_template_model;
- creature_model_info;
- creature_template_spell;
- pet_levelstats;
- gameobject_template;
- item_template;
- item loot/vendor rows in the separate Manastorm package.

Omitting spell_script_names or spell_proc rows will silently disable portions of the class scripts. Omitting creature/gameobject/model rows will leave summons, fields, portals, traps, turrets, pets, or visual helpers broken.

Every guarded creature, model, gameobject, pet-level, and group definition needs an absent-or-exact preflight. Existing conflicting rows must be rejected and reviewed; they must not be overwritten because the donor value happens to have the same name.

### SQL that is not required for the classes

The following donor data is separate from the requested class transport:

- modules/mod-ascension-compat/data/sql/db-characters/2026_08_26_00_ascension_collections.sql
  - account_appearance_collection;
  - character_appearance;
  - character_appearance_settings;
  - account_vanity_collection.
- modules/mod-ascension-compat/data/sql/db-world/2026_08_26_01_ascension_appearance_item_templates.sql
  - approximately 25.5 MB of visual/query-only item templates;
  - item_template_ascension_compat marker table;
  - tied to Item.dbc hash 6A5B559B5EAC8FBF8E219CE463EB6684BC7F1B16760A043E3D7462AA495478BB.
- rev_20260908_03_manastorm_rewards.sql;
- rev_20260908_04_manastorm_reward_tiers.sql;
- pending_db_characters/rev_20260908_00_manastorm.sql;
- pending_db_characters/rev_20260908_01_manastorm_progression.sql;
- pending_db_characters/rev_20260908_02_manastorm_cache_delivery.sql.

Manastorm, account collections, vanity, the Tradesman's Scroll, local level scaling, mount wrappers, and GitHub bug reporting are donor features, not prerequisites for the custom class IDs or their combat mechanics.

The class service and collection service are co-located in AscensionCompat.cpp. If the implementation keeps that file intact, the collection/client-data dependencies must still be supplied or deliberately disabled. If a class-only module is desired, separating those services is a later implementation decision; it is not safe to omit arbitrary headers or loader calls without tracing their callers.

## Client, DBC, and asset dependencies

The donor source package does not contain the client package. Server source and SQL alone will not make the new classes selectable or visually complete.

A complete client/server package needs matching versions of the following.

### Class identity and character creation

- ChrClasses.dbc:
  - rows 12–32;
  - player-facing names;
  - display-power values;
  - class flags and expansion values;
  - class icon/selection metadata.
- CharBaseInfo.dbc:
  - class/race starting information where used by the client.
- CharStartOutfit.dbc:
  - start outfits for every supported class/race/sex combination.
- SkillRaceClassInfo.dbc:
  - class/race skill visibility and restrictions.
- SkillLineAbility.dbc:
  - client-visible class/proficiency ability relationships where required.
- TalentTab.dbc, Talent.dbc, and any CoA talent data used by the client.
- CharacterCreate Glue XML/Lua:
  - class button count;
  - class IDs and display names;
  - class/race filtering;
  - faction grouping;
  - class icons and descriptions;
  - class creation payloads.
- Matching client-side class/advancement/resource addon or overlay.

The current repository already contains custom race IDs 12–27 and several staged DBC/MPQ candidates. Those are unrelated race contracts and must remain intact. A class ID and a race ID can both numerically be 14 or 15 because they are different fields, but every generator, DBC table, UI filter, and SQL row must use the correct domain.

### Spell and class data

- A matching server Spell.dbc;
- the same logical spell rows on the client;
- all custom spell IDs referenced by the 844 class-spell array and per-class SQL;
- custom families 18–38;
- spell names, descriptions, rank chains, icons, visual IDs, costs, effects, aura types, target masks, and class flags;
- any client-side Spell.dbc continuation files used by the current WXL DBC system.

The current server Spell.dbc is stock-sized and has no donor custom IDs. It cannot be used for the class port without the matching external data.

### Summons, models, and visuals

Depending on the class and the exact selected reconstruction, the package may also need:

- CreatureDisplayInfo.dbc;
- CreatureModelData.dbc;
- CreatureModelInfo.dbc;
- GameObjectDisplayInfo.dbc;
- SpellVisual.dbc;
- Item.dbc;
- M2 and skin files;
- MPQ load-order entries;
- client-side model and texture files;
- server DBC continuation rows.

Several donor class documents intentionally use native model fallbacks and state that no new DBC is required for that class. That does not eliminate the identity or Spell.dbc requirements, and it does not prove that the selected native model renders correctly.

Witch Doctor and Necromancer source packages specifically refer to external model DBC candidates. Templar, Witch Hunter, and several summon-heavy packages also have client/UI/model acceptance dependencies. The donor directory does not include those candidate files.

### Executable, DLL, and packet compatibility

The custom client may need:

- a patched WoW.exe/DLL for extended class capacity;
- matching signature handling;
- extended class creation and advancement packet support;
- extension opcode dispatch;
- resource, charge, aura-amount, and collection UI handling.

The current Worgoblin/ARAC client work and current mod-wxl-dbc mechanism do not automatically provide CoA class support.

The current working tree contains an untracked mod-wxl-dbc implementation that loads DBC continuation rows after base DBC load and rebuilds derived indexes. If it remains the chosen server DBC path, custom class DBC continuations must use its exact WotLK record layouts and the matching client continuation files. Preserve its dirty core changes and do not replace them with donor versions.

## Current-server integration hazards

### PlayerBots

The donor has no PlayerBots custom-class AI.

The current mod-playerbots code contains:

- MAX_CLASSES-sized arrays;
- hard-coded class loops;
- class/spec name tables for stock classes;
- switch statements for stock class combat behavior;
- factory and travel logic that assumes stock class specs;
- item/stat weighting based on stock class semantics.

After MAX_CLASSES becomes 33, those arrays may be large enough, but their contents and switch behavior will still not understand classes 12–32. Custom classes could otherwise be created as bots and then receive unknown specs, invalid gear, empty rotations, or class-specific crashes.

The safest initial policy is:

- preserve all existing classic PlayerBots;
- exclude classes 12–32 from random bot generation, add-class generation, travel/spec selection, and bot maintenance;
- do not map custom classes to a stock AI unless that mapping is explicitly accepted;
- add custom-class bot AI only as a separate task.

Changing factory code would not migrate or repair existing bots. Existing bot rows and accounts must be counted before any policy change.

### Existing custom races

The donor class matrix covers only stock race IDs 1–11, omitting Goblin 9. The current server defines custom races including:

- Worgen 12;
- High Elf 13;
- Broken 14;
- current Sethrak/Ogre slot 15;
- Eredar 16;
- Nightborne 17;
- Void Elf 18;
- Vulpera 19;
- Zandalari Troll 20;
- Pandaren variants 21–22;
- Broken faction variants 23–24;
- Forsaken 25;
- Lightforged Draenei 26;
- Dark Iron Dwarf 27.

Do not assume the donor classes are valid for those races. If they are desired, extend the class/race, client DBC, client Glue, skill, start-position, and model contracts deliberately.

### Existing spell-learning modules

The current server has mod-individual-progression and PlayerBots spell-maintenance paths. The former mod-learn-spells path was removed because Classless owns spell grants. Audit the remaining paths for:

- MAX_CLASSES assumptions;
- class masks;
- rank selection;
- starter spell grants;
- fallback class behavior;
- removal of unavailable spells;
- interaction with temporary spell replacements.

The donor class service is rank-aware and class-scoped. A broad existing learner must not give a custom class the wrong stock spell or the wrong rank.

### Existing DBC changes

The current working tree has dirty DBC loader/index changes and staged custom-race DBC data. Use one authoritative DBC composition path and keep these domains separate:

- base WotLK DBC;
- existing race continuations/overlays;
- donor custom class/spell continuations;
- model/display continuations;
- client MPQ/loose-file overrides.

Validate derived indexes after any post-load DBC injection. A loaded DBC row without its secondary lookup index can still appear present while class creation, talents, skills, or models fail at runtime.

### Existing SQL and update state

The current server has persistent Docker databases and current custom SQL. The donor files contain historical/generated snapshots whose revision names may not exist in the current update table.

Before applying anything in a future implementation:

- inspect the target update table;
- count existing class 12–32 characters, if any;
- count existing starter items and custom spell rows;
- check every donor item, creature, gameobject, model, proc, group, and spell binding;
- compare exact existing rows;
- create new target revisions where required;
- preserve applied SQL hashes;
- never silently reinterpret a previously used class or race ID.

The current class port is additive. Existing classic characters, class 1–11 rows, classic starter data, current race data, and existing module-owned records must remain intact.

## Recommended transport order

### 1. Freeze the target contract

Decide before implementation:

- all 21 donor classes, IDs 12–32;
- whether the 124 donor race/class pairs are the target;
- whether current custom races also receive the classes;
- whether the copied Ascension client is mandatory;
- whether collections, Manastorm, local scaling, mount wrappers, and bug reporting are in scope;
- whether custom classes are excluded from PlayerBots initially.

The default safe choice is all 21 classes, donor stock-race matrix only, no class 10, classic PlayerBots preserved but custom classes excluded from bot AI.

### 2. Preserve and record current state

Create a source/DB/client backup outside the repository.

Record:

- current Git status and HEAD;
- current core and module hashes;
- current database update table;
- current class/race/playercreateinfo rows;
- current DBC/MPQ manifests and hashes;
- current PlayerBots character/account counts;
- current custom-race IDs and client files.

Do not clean the working tree or discard unrelated changes.

### 3. Port the core ABI by merged hunks

Merge only the donor changes required for:

- class IDs and enum metadata;
- custom class masks and fallback mapping;
- player creation/starter hooks;
- class-aware stats and combat;
- spell effects, aura types, and SpellInfo fields;
- spell-charge state;
- custom resource and damage/healing hooks;
- required script hook APIs;
- custom client protocol, only if the CoA client is selected.

Reuse current implementations where they already provide the same hook or DBC functionality. Do not copy the donor’s 142 differing files wholesale.

### 4. Wire the module

Add a repository-native CMakeLists.txt for mod-ascension-compat and register:

- every donor source translation unit;
- MP_loader.cpp;
- the module configuration;
- module world/character SQL paths.

Keep the donor source boundary intact unless a deliberate class-only split is approved. Verify every MP_loader registration.

### 5. Supply matching DBC and client assets

Obtain or reconstruct the missing external package:

- custom Spell.dbc;
- ChrClasses and character-creation rows;
- class/race/start outfit/skill/talent records;
- model/display DBC candidates;
- matching client UI/Glue;
- MPQ/loose files;
- executable/DLL support if required.

Merge these with the current custom-race and WXL DBC package. Do not overwrite existing current race IDs or patches.

### 6. Reconcile and migrate SQL

Use the donor files as source evidence, not as blind imports.

Build a target dependency set in the current repository’s pending/module SQL layout:

1. class identity and class/race manifest;
2. class spell/bootstrap and starter item definitions;
3. baseline spell/rank/proficiency data;
4. common spell groups and class-independent support;
5. Guardian/Barbarian shared foundations;
6. Ranger/Witch Hunter;
7. Witch Doctor/Necromancer/Templar;
8. Felsworn/Starcaller/Knight of Xoroth;
9. Pyromancer/Cultist/Sun Cleric/Venomancer;
10. Tinker;
11. Reaper/Primalist/Runemaster;
12. guarded creature/model/gameobject corrections.

The exact class package order must follow the target database’s actual state. A later completion SQL file must not be applied without its matching source, DBC, and preceding definitions.

### 7. Build and import only when explicitly authorized

This audit did not configure, build, test, import SQL, restart Docker, or launch a client.

When authorized, the relevant gates are independent:

- core/module compile;
- SQL updater/import;
- worldserver startup;
- DBC/model validation;
- client login and character creation;
- class combat and UI behavior;
- PlayerBots regression;
- restart/relog behavior.

A successful compile or SQL import is not proof that a class is selectable or playable.

## Acceptance checklist

### Static/source checks

- All 21 IDs exist in core and enum metadata.
- ID 10 remains reserved and is not exposed as a custom class.
- MAX_CLASSES and every class-indexed array are safe through ID 32.
- getClassMask uses unsigned bit 31 handling.
- Current classic enum values and masks are unchanged.
- All donor module sources are build-wired.
- All MP_loader registration functions are present.
- Every generated class array is byte-preserved or regenerated from a verified matching input.
- Custom Spell.dbc IDs and family numbers match the C++/SQL contract.
- No donor source file assumes an unavailable core API.
- Current dirty DBC/module/race work is preserved.
- git diff --check passes after implementation.

### Database checks

- Every class 12–32 has the intended identity, fallback, power, stats, start location, action, skills, spells, and starter items.
- Every selected class/race combination has one valid playercreateinfo row.
- Existing class 1–11 rows are unchanged.
- Existing current-race rows are unchanged unless separately approved.
- Every spell_script_names and spell_proc row resolves to a matching spell.
- Every creature/gameobject/model/pet-level row is absent or exactly compatible before insertion.
- No existing character is remapped.
- No old class or race ID is silently reinterpreted.
- Update history and hashes are preserved.

### Client/server creation checks

For each class 12–32:

- the class appears with the correct player-facing name;
- only intended races are selectable;
- both sexes load;
- the creation packet reaches the server with the intended class ID;
- creation succeeds;
- the correct home/start location is used;
- starter spells, skills, action bar, stats, health, and power are correct;
- starter equipment appears in the exact intended slots;
- the character logs in, logs out, and relogs;
- the character survives a restart;
- the character can equip normal class-valid gear;
- the client displays the correct resource/talent/action state.

For classic classes 1–11:

- creation, login, spells, starter gear, talents, equipment, DK restrictions, and existing custom-race combinations still work;
- no custom class spells are learned;
- no custom class resource message is emitted.

### Gameplay checks

For every custom class:

- native cast validation occurs before resource spending;
- costs and gains occur once;
- misses, immunity, interrupts, dispels, and triggered helpers follow the class contract;
- rank upgrades occur at the correct level;
- temporary spells and action-bar replacements restore permanent ownership;
- cooldowns and charges survive relog where intended;
- damage/healing copies do not double-apply coefficients or critical rolls;
- summons have correct ownership, threat, leash, death, despawn, and map/phase cleanup;
- forms and class-specific native powers recover correctly;
- resource UI and aura amounts match server state.

For Tinker specifically, verify Scrap, augmentations, Mechsuit, turrets, Rockadier, Hacking, Overload, Combustion, and Combat Symbiosis.

For Venomancer specifically, verify Brood Mark, spider/beetle forms, Venom payload/proc/talent handling, Catalyst, poison ownership, Parasite, Lair, Burrow, Skitter, and summons.

For the three classes without dedicated source prefixes—Stormbringer, Bloodmage, and Chronomancer—perform a full independent creation/progression/resource/combat test instead of treating generated data presence as proof of parity.

### PlayerBots checks

Until custom AI exists:

- random and add-class bot generation excludes IDs 12–32;
- classic bot generation remains unchanged;
- existing bots do not receive custom class spells;
- travel/spec/config arrays do not index invalid custom specs;
- custom-class characters can still group with bots as ordinary players.

## Known limitations and non-claims

The donor source is a local reconstruction, not the official Ascension backend.

The donor documents contain explicit local choices for missing coefficients, proc timing, summon scaling, movement, model fallbacks, and damage/healing behavior. Those choices should be preserved as source policy only after review; they are not proof of official values.

The received donor directory does not prove:

- a linked build;
- a configured module;
- an applied database;
- a matching client;
- a working client class-creation screen;
- rendered models;
- live combat;
- relog/restart persistence;
- PlayerBots compatibility;
- multiplayer behavior;
- official gameplay parity.

The source’s own class documents repeatedly separate source completion from build, SQL application, client installation, and gameplay acceptance. This transport plan keeps those gates separate.

## Source evidence index

Donor:

- modules/mod-ascension-compat/README.md
- modules/mod-ascension-compat/src/MP_loader.cpp
- modules/mod-ascension-compat/src/AscensionCompat.cpp
- modules/mod-ascension-compat/src/AscensionCustomClassData.h
- modules/mod-ascension-compat/src/AscensionCustomResourceData.h
- modules/mod-ascension-compat/src/AscensionCoATalentData.h
- modules/mod-ascension-compat/src/AscensionSpellProgressionData.h
- modules/mod-ascension-compat/src/AscensionLiveBaselineData.h
- modules/mod-ascension-compat/src/AscensionFreshCharacterExpectations.h
- modules/mod-ascension-compat/data/sql/db-world/2026_08_27_00_ascension_custom_classes.sql
- modules/mod-ascension-compat/data/sql/db-characters/2026_08_26_00_ascension_collections.sql
- modules/mod-ascension-compat/data/sql/db-world/2026_08_26_01_ascension_appearance_item_templates.sql
- modules/mod-ascension-compat/docs/*.md
- data/sql/updates/pending_db_world/rev_1787754600000000000.sql
- data/sql/updates/pending_db_world/rev_20260831_01_local_spell_progression.sql
- data/sql/updates/pending_db_world/rev_20260831_03_local_class_starters.sql
- data/sql/updates/pending_db_world/rev_20260903_01_live_class_baseline.sql
- data/sql/updates/pending_db_world/rev_20260906_03_any_race_class.sql
- data/sql/updates/pending_db_world/rev_20260906_* through rev_20260910_15 class packages
- src/server/shared/SharedDefines.h
- src/server/shared/enuminfo_SharedDefines.cpp
- src/server/game/Entities/Player/Player.cpp and Player.h
- src/server/game/Entities/Unit/Unit.cpp, Unit.h, and StatSystem.cpp
- src/server/game/Spells/*
- src/server/game/Scripting/ScriptDefines/*

Current server:

- src/server/shared/SharedDefines.h
- src/server/shared/enuminfo_SharedDefines.cpp
- src/server/game/Entities/Player/*
- src/server/game/Entities/Unit/*
- src/server/game/Spells/*
- src/server/game/Scripting/ScriptDefines/*
- modules/mod-playerbots/*
- modules/mod-worgoblin-high-elf/*
- modules/mod-wxl-dbc/*
- modules/mod-custom-server/*
- data/sql/base/db_world/*
- data/sql/updates/pending_db_world/*
- Spell.dbc

Bottom line: transplant the donor’s 21 real class IDs and the complete class engine/data bundle additively. Keep classes 1–11 and their current races untouched. Treat the donor client/DBC package, current PlayerBots, DBC continuation work, and database collision state as first-class dependencies, not afterthoughts.
