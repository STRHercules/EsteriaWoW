# AzerothCore and server-side Esteria changes

[Back to the guide](README.md)

## What the change inventory means

The exact core delta is captured against `a29b5dc`, the repository's September 2 AC import, at working
HEAD `758f66fdeafbe9e6247951754e52eceb528c37be` plus current uncommitted changes.

This is not a claim that every delta was authored for a race or differs from today's upstream. It includes
the playerbot baseline, standard Eluna integration, Freeborn/classless hooks, content-script changes and
Esteria modifications. Only the `origin` Esteria remote was present during the audit; older docs describing
an `upstream` remote and `custom-server` branch are historical.

- [CORE_FILES.md](reference/CORE_FILES.md) lists every captured core/build file with additions/deletions.
- [server-since-core-import.patch](evidence/server-since-core-import.patch) preserves the exact diff for
  core/build and selected integration modules.
- `sources/EsteriaWoW` preserves current changed files and the relevant module/tool/header sources.
- [MODULES.md](reference/MODULES.md) inventories all source-installed module directories.

The module list establishes presence, not runtime activation. Use the complete repository for modules
not bundled in this focused source overlay.

## Race IDs, masks and compatibility

[SharedDefines.h](sources/EsteriaWoW/src/server/shared/SharedDefines.h) adds the custom race enums and
bounded compatibility helpers. The client table handles IDs 0–63; `RaceMgr` derives server maximum
from valid loaded rows. It builds mask sets through `GetRaceMaskForRace` rather than an unchecked
`1 << (race - 1)` for a high ID.

The old APIs still use 32-bit masks. They are not globally widened. Extended races alias a donor mask:

| Actual RaceID | Legacy eligibility donor |
| --- | --- |
| 45 Mag'har | 2 Orc |
| 46 Highmountain | 6 Tauren |
| 47 Mechagnome | 7 Gnome |
| 48 / 49 Earthen | 3 Dwarf / 2 Orc |
| 50 / 51 Haranir | 4 Night Elf / 8 Troll |
| 52 / 53 Skyborne | 13 High Elf / 10 Blood Elf |
| 54 Naga | 10 Blood Elf |
| 55 Tuskarr | 3 Dwarf |
| 56 / 58 Vrykul/Forgotten Alliance | 1 Human |
| 57 / 59 Vrykul/Forgotten Horde | 2 Orc |

Darkfallen 43/44 share mask `0x80000000`. Shared masks do not establish faction or numeric identity.
The actual race still drives roster display, models, starts and team. Eligibility aliases are used
for existing skill/spell/item/quest APIs, with explicit handling of racial admission where needed.

Read the distinction between legacy-mask race and visual-base race in the registry. Haranir Horde,
for example, can use Troll eligibility and its own model/actual race.

Sources:
[RaceMgr.cpp](sources/EsteriaWoW/src/server/game/Entities/Player/RaceMgr.cpp),
[DBCStores.cpp](sources/EsteriaWoW/src/server/game/DataStores/DBCStores.cpp),
[Player.cpp](sources/EsteriaWoW/src/server/game/Entities/Player/Player.cpp) and
[ObjectMgr.cpp](sources/EsteriaWoW/src/server/game/Globals/ObjectMgr.cpp).

## Race/class startup and language repair

The current readback has ten start rows for each listed playable race/class policy:
classes 1,2,3,4,5,6,7,8,9,11. That is an observed server policy, not the Retail class list.

Creation integration supplies starts, outfits, actions, skills, spells and donor-compatible stat data.
Normal language spells and skills must both exist and survive save/load. Language skills are initialized
at step zero where required by the core.

`SkillRaceClassInfo` matters: `LearnDefaultSkill` can reject an otherwise correct skill. SkillLineAbility
and skill/race metadata can also cause a learned spell to be stripped. The Darkfallen skill-220 fix and
Mag'har/Skyborne client eligibility repair addressed different layers of this problem.

The server mounts an expanded SkillRaceClassInfo DBC. Its 364 records differ from the effective client's
328 records, whose native eligibility redirects use compatibility donors. They must be checked by
behavior and mapping; replacing either file solely to make its hash match the other can undo a fix.

Playerbots need the same ID/visibility/appearance policy. The source snapshot includes
`modules/mod-playerbots/src/Bot/Factory`. Supported race IDs and generated appearance validation must
not be inferred from UI button ordinal or an NPC race number. A refresh of existing bots is separate
from installing a model port.

## Appearance creation, enumeration, save and login

Relevant source files:

- [CharacterHandler.cpp](sources/EsteriaWoW/src/server/game/Handlers/CharacterHandler.cpp)
- [WorldSession.h](sources/EsteriaWoW/src/server/game/Server/WorldSession.h)
- [PlayerStorage.cpp](sources/EsteriaWoW/src/server/game/Entities/Player/PlayerStorage.cpp)
- [CharacterDatabase.cpp](sources/EsteriaWoW/src/server/database/Database/Implementation/CharacterDatabase.cpp)
- [UpdateFieldFlags.cpp](sources/EsteriaWoW/src/server/game/Entities/Object/Updates/UpdateFieldFlags.cpp)

Generated codecs are `HighmountainAppearance.h`, `EarthenAppearance.h`, `HaranirAppearance.h`,
`VulperaAppearance.h` and `CreatureAppearance.h` under `src/server/shared`.

### Six-byte families

Highmountain/Earthen use the unused final outfit byte in normal `CMSG_CHAR_CREATE` as the sixth
appearance byte. Server validation checks the race/gender codec before creation.

The extra value is saved in the character transaction and carried in `UNIT_FIELD_PADDING`.
Character enumeration appends race-specific GUID/extra-byte pairs, then count and `HXE1` magic
`0x31455848`. The native reader bounds and removes that trailer before stock roster parsing.

### Haranir uint64 extension

Creation appends uint64 appearance plus `HRC1` magic `0x31435248`. The handler validates the trailer
length, signature and every encoded value.

Mixed rosters retain HXE1 and append HXE2 GUID/uint64 records, count and magic `0x32455848`.
Live units use the low Unit padding word and high Object padding word. The current DB column is
`extraAppearance BIGINT UNSIGNED NOT NULL DEFAULT 0`.

Loading validates saved fields and restores them consistently. Saving/re-enumeration/nearby updates
must preserve high bits. The native helper additionally repairs late stock sanitation; DB readback
alone did not solve Earthen's initially plain in-game model.

### Five-byte families

Skyborne, Mechagnome, Vulpera and the creature ports preserve the stock byte transport. Vulpera validates
class-specific choices; the creature codec rejects unsupported genders. The same generated codec must
govern new creation, loading, roster display and randomization.

## Player display width and dimensions

The accepted player model/display band is below 65536. A previous HD import explored larger player
display IDs and widening storage, then rolled back. Do not use that abandoned approach as today's
race-allocation contract.

CreatureModelData IDs may be larger; they resolve the model behind a display. Model dimensions, scale
and collision fallback checks are distinct from player display storage. The core diff also includes
collision-dimension regression tests and mmaps/config/content changes; inspect the exact file inventory
before adapting an upstream core.

## Full DBC mounts and continuation support

The current Compose override mounts full standard files from
`modules/mod-custom-server/data/dbc/retroported-races` into the worldserver's `data/dbc`:

ChrRaces, CharStartOutfit, CharSections, BarberShopStyle, CreatureDisplayInfo, CreatureModelData and Spell.

It separately mounts SkillRaceClassInfo and the fly-anywhere AreaTable. These are bind-mounted outputs;
having a source DBC in another repository directory does not make it effective.

`mod-wxl-dbc` implements bounded in-memory continuation loading after DBC stores load. Core additions
include the after-load hook, DBC merge methods and layouts. The relevant
[module documentation](sources/EsteriaWoW/modules/mod-wxl-dbc/README.md) and source are included.

Freeborn's FactionTemplate continuation is still separately mounted. Current race/model/appearance
identity uses full DBCs; do not reintroduce obsolete continuation copies that override them later.

World SQL `*_dbc` tables can overlay loaded DBC values. Legacy race 24–27 and NPC reservations are
concrete examples. The live readback is in [current-state.json](evidence/current-state.json).

## Dedicated migrations

| Change | Pending filename / scope |
| --- | --- |
| Initial modern race start policy | World `rev_20260929001000000.sql` and related dated race migrations |
| Skyborne startup | World `rev_20260930003000000.sql` |
| Skyborne saved-byte remap | Characters `rev_20260930004000000.sql` |
| Mechagnome | World `rev_20261001005000000.sql` |
| Highmountain + six-byte schema | World/characters `rev_20261001006000000.sql` |
| Earthen | World `rev_20261001100000000.sql` |
| Haranir + uint64 schema | World/characters `rev_20261002120000000.sql` |
| Vulpera rebase | Characters `rev_20261002200000000.sql` |
| Vulpera v2 | Characters `rev_20261002220000000.sql` |
| Creature player ports | World `rev_20261002230000000.sql` |

Historical module updates and older racial/start fixes are also snapshotted. Do not import all of them
into a current database. Check each installer's migration allow-list and the updater receipt first.
A receipt state `PENDING` can mean an applied pending migration; it is not itself evidence of nonexecution.

Preserve immutable base/archive/merged SQL. New development follows the repository's pending-directory
rules. Existing module updates were copied without editing them.

## Custom racial behavior

Broken and Darkfallen have explicit runtime/server racial implementations and SQL, not just tooltip
text. The core diff includes Broken repair-cost, mana-drain and periodic healing interactions and their
contracts. Locate their exact implementation through the source/file index rather than assuming every
imported family has Retail racials.

The newer visual ports generally inherit declared donor startup/racial compatibility. Mechagnome,
Highmountain, Earthen and Haranir do not implement all Retail racial abilities. UI text must describe
the implemented behavior.

## Freeborn, faction interaction and first/last names

Freeborn is a persistent third team, `TEAM_FREEBORN = 3`, distinct from temporary neutral values.
Source changes cover saved teamId, login/roster transport, hostility/cooperation, conditions, quests,
groups/guilds, guards, reputations and faction-change behavior.

Creation still begins on the race-origin team. The creator records the Freeborn choice and the claim
path applies it after a valid character exists. Mask aliases cannot decide Freeborn identity.
[Freeborn tools](sources/EsteriaWoW/tools/freeborn_team_pack.py) and historical implementation plans
are included, along with a Freeborn combat/condition test.

First/last names extend the existing client/server name contract. The runtime validator patch, creator
fields/randomizers and shared server checks must agree; user-facing “Last Name” is not a second
character record. See [two_names_client_pack.py](sources/EsteriaWoW/tools/two_names_client_pack.py).

The source also supports a 100-character per-realm policy and enlarged select roster. This is separate
from 64-race capacity. Check account/realm limits and roster binding together.

## Eluna, AIO and other core integration

Standard Eluna is integrated through CMake, core dispatch and `src/server/game/LuaEngine`; ALE is not
the standard engine used here. Added hooks cover player/world, creature/gameobject, spell/aura, quest,
guild, inventory and related lifecycle events. The exact source delta preserves ordering and
prevention semantics.

AIO Lua is mounted from `modules/mod-worgoblin-high-elf/lua_scripts`. Its global Eluna world transport
and LANG_ADDON routing are part of the custom environment. Cache delivery does not prove client-side
addon UI execution; do not apply GlueXML fixes to an in-game addon cache or vice versa.

Other recorded systems include classless Hero progression/skills/talents/pets/loot, Battlemon and its
overworld support, account collections, housing/rewards/progression and the modules in the inventory.
Module README/config/source is the authority for each subsystem's actual switch and limits.

## Current dirty core feature

The working checkout has uncommitted `MoveCast.Enabled` changes in Unit, Spell and WorldConfig.
They gate movement-cast checks and auto-repeat behavior behind a default-false option. They are included
as source state, without asserting they are present in the inspected running image or live-tested.

Other dirty packer/test/manifests and logs were preserved. This documentation task did not rebuild the
server or mutate any database to make the snapshot appear cleaner.

## Rebuild boundary

For a C++ change, rebuild the matching worldserver when authorized, import only its required migrations
and recreate only `ac-worldserver` with `--no-deps`. A Lua/config/data-only repair has a different scope.
Do not replace database volumes or rebuild/restart unrelated services as part of race deployment.
