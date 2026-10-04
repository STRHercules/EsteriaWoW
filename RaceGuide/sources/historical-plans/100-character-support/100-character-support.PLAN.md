# 100-Character Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Raise Esteria's account/realm character capacity to 100 across AzerothCore, the verified 3.3.5a client, and the mirrored character-select Glue payloads.

**Architecture:** Reuse AzerothCore's existing config and `uint8` enumeration path. Patch the one verified native client limit byte, then keep the existing eight Glue rows reusable while a native Glue scrollbar and mouse-wheel offset select actual character indexes.

**Tech Stack:** AzerothCore C++20, INI configuration, WotLK 3.3.5a build-12340 PE, GlueXML/Lua, existing `modules/mod-classless-wildcard/client-patch/lib/mpq.py` MPQ reader/writer, standalone Python contract test.

**Spec:** `.agents/plans/100-character-support/100-character-support.ANALYSIS.md`

## Global Constraints

- Preserve all unrelated dirty work in the checkout.
- Do not edit immutable SQL files or change the database schema.
- Keep the server authoritative; client checks are convenience/compatibility only.
- Validate the exact original client bytes before changing the executable.
- Patch both mirrored Patch-Z Glue archives and verify their payloads match.
- Do not configure or build; use focused static/contract checks only.

---

### Task 1: Add the failing cross-layer contract test

**Files:**
- Create: `tools/test_character_limit_contract.py`

**Interfaces:**
- Consumes the checked-in server/config sources, `3.3.5a - Dev\\Wow.exe`, and both active Patch-Z archives.
- Produces one standalone executable check that fails until all three layers implement the approved contract.

- [ ] **Step 1: Write the failing test**

Add assertions for: server defaults/range `100`, all runtime/distributed config values `100`, no selected server path retaining `charcount >= 10`, the executable bytes `80 7D FF 64` at `0x6404C`, and both Glue archives containing `MAX_CHARACTERS_PER_REALM = 100`, actual-index scrolling helpers, and the scroll frame XML.

- [ ] **Step 2: Run the test and verify the expected failure**

Run `python tools/test_character_limit_contract.py`. It must fail against the current `10`/`50` server settings or unpatched `0A` client byte, proving the test is red for the intended reason.

### Task 2: Make the server limit configurable at 100

**Files:**
- Modify: `src/server/game/World/WorldConfig.cpp:230-234`
- Modify: `src/server/apps/worldserver/worldserver.conf.dist:2016-2029`
- Modify: `env/dist/etc/worldserver.conf.dist:2016-2029`
- Modify: `env/dist/etc/worldserver.conf:2016-2029`
- Modify: `src/server/scripts/Commands/cs_character.cpp:226,1076`
- Modify: `src/server/game/Tools/PlayerDump.cpp:766-768`
- Modify: `modules/mod-playerbots/src/Ai/Base/Actions/HireAction.cpp:7-35`

**Interfaces:**
- Consumes `CONFIG_CHARACTERS_PER_ACCOUNT` and `CONFIG_CHARACTERS_PER_REALM`.
- Produces server-side creation, restoration, dump/import, account-transfer, and playerbot-hire behavior capped by those values.

- [ ] **Step 1: Change defaults and validation**

Set both ordinary character defaults to `100`; change the realm validator to `value > 0 && value <= 100` and its description to `> 0 && <= 100`. Leave `HeroicCharactersPerRealm` unchanged.

- [ ] **Step 2: Update distributed and active configuration**

Set `CharactersPerAccount = 100` and `CharactersPerRealm = 100` in all four listed config files, including the active `env/dist/etc/worldserver.conf`.

- [ ] **Step 3: Replace remaining ordinary-character literals**

Use `sWorld->getIntConfig(CONFIG_CHARACTERS_PER_ACCOUNT)` for deleted-character restore, character account transfer, player dumps, and playerbot hire. Add `#include "World.h"` to `HireAction.cpp` if required by its direct config access.

- [ ] **Step 4: Run the contract test**

Run `python tools/test_character_limit_contract.py`; the server assertions must pass while the client assertions remain red.

### Task 3: Patch the verified native client limit

**Files:**
- Modify: `3.3.5a - Dev\\Wow.exe`
- Preserve: `3.3.5a - Dev\\Backups\\character-limit-20260918\\Wow.exe`

**Interfaces:**
- Consumes the exact PE byte signature at file offset `0x6404C`.
- Produces a build-12340 client that accepts character counts through `0x64`.

- [ ] **Step 1: Validate the original signature and backup hash**

Require the current bytes at `0x6404C:0x64050` to equal `80 7D FF 0A` and require the backup hash to equal the current pre-patch hash before writing.

- [ ] **Step 2: Apply the one-byte replacement**

Replace only byte offset `0x6404F` (`0A`) with `64`; refuse the operation if the full original signature is not present.

- [ ] **Step 3: Verify the patched bytes and hash**

Check for `80 7D FF 64` at `0x6404C` and run the contract test. Record the resulting SHA-256 in the support document.

### Task 4: Add offset-based Glue scrolling and repack both Patch-Z archives

**Files:**
- Modify payload: `Data\\patch-Z.MPQ::Interface\\GlueXML\\CharacterSelect.lua`
- Modify payload: `Data\\patch-Z.MPQ::Interface\\GlueXML\\CharacterSelect.xml`
- Mirror payloads into: `Data\\enUS\\patch-enUS-Z.MPQ`
- Preserve backups under: `3.3.5a - Dev\\Backups\\character-limit-20260918\\Data\\`

**Interfaces:**
- `CharacterSelect_ScrollBy(delta)`, `CharacterSelect_SetScrollOffset(offset)`, and `CharacterSelect_OnVerticalScroll(frame, offset)` maintain a clamped `CharacterSelect.scrollOffset`.
- Visible row `i` displays actual character `CharacterSelect.scrollOffset + i`.
- The existing eight row buttons and existing paid-service/delete/rename functions continue to consume actual indexes.

- [ ] **Step 1: Add the failing Glue behavior assertions**

The contract test must require the 100-character constant, scroll-offset helpers, actual-index mapping, mouse-wheel handlers, and `GlueScrollFrameTemplate` character scrollbar in both archives.

- [ ] **Step 2: Implement the Lua offset helpers**

Clamp the offset to `0..max(GetNumCharacters() - MAX_CHARACTERS_DISPLAYED, 0)`, snap scrollbar pixel positions to the existing row spacing, keep the selected character visible, and guard programmatic scrollbar updates against recursive callbacks.

- [ ] **Step 3: Remap the existing list population**

Populate the eight reusable buttons from `scrollOffset + 1` through `scrollOffset + MAX_CHARACTERS_DISPLAYED`; call `button:SetID(actualIndex)` and set the matching customization/race/faction action button IDs. Map selected highlighting back to the visible row.

- [ ] **Step 4: Add the Glue scrollbar and wheel handlers**

Add a narrow `GlueScrollFrameTemplate` with a dummy scroll child to generate the standard scrollbar, anchor its scrollbar beside the existing list, and route wheel events from the list and row buttons to one-row offset changes. Keep the current list geometry and appearance.

- [ ] **Step 5: Repack and mirror the archives**

Read all existing Patch-Z entries, replace only the two Glue files, write temporary rebuilt archives, verify `(listfile)` and payload hashes, then replace the active root and `enUS` Patch-Z files. Do not modify Patch-A or lower-priority archives.

- [ ] **Step 6: Run the contract test**

Run `python tools/test_character_limit_contract.py`; all static server, executable, and Glue assertions must pass.

### Task 5: Document and perform final focused verification

**Files:**
- Create: `docs/100-character-support.md`

- [ ] **Step 1: Document the final contracts**

Record modified server files, config values, executable offset/signatures/hashes, active archive payloads, offset formula, backup location, and the fact that live client/server smoke testing was not performed.

- [ ] **Step 2: Run focused static checks**

Run the standalone contract test, `git diff --check` for repository text changes, and the C++ codestyle script only if it does not configure/build. Do not run a server build or live client test.

- [ ] **Step 3: Review the scoped diff**

Inspect only requested text files plus generated client artifacts; verify unrelated pre-existing dirty files are unchanged and report the exact verification boundary.
