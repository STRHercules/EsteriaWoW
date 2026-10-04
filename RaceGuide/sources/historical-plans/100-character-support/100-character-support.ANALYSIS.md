# 100-Character Support Requirements

## Goal

Support up to 100 playable characters per account and realm in the Esteria AzerothCore/WotLK stack, including character enumeration, creation, restoration/import paths, client enumeration, and character-select navigation.

## Approved architecture

- Keep the existing `uint8` character count protocol and `tinyint unsigned` realm-character counter; both represent 100.
- Make AzerothCore's existing configuration authoritative at 100 and replace remaining account-cap literals with the configured account limit.
- Patch only the verified build-12340 executable byte at file offset `0x6404F`, after validating `80 7D FF 0A`; replace `0A` with `64`.
- Preserve the current character-select presentation with eight reusable rows. Add a Glue scrollbar backed by a pixel-to-row offset and mouse-wheel handlers on the list and row buttons.
- Map every visible row to `scrollOffset + row`, and use the actual character index for selection, login, deletion, rename, and paid-service actions.
- Update both active mirrored Glue payloads: `Data\\patch-Z.MPQ` and `Data\\enUS\\patch-enUS-Z.MPQ`.

## Current evidence

- Target executable: `3.3.5a - Dev\\Wow.exe`.
- Target SHA-256 before patch: `be4ccde69622f1fb01d25e5e429e8c16bf2bc66fcafd5b73442e74da9bedfe81`.
- Verified instruction: `80 7D FF 0A C7 45 F8` at file offset `0x6404C`; limit byte is `0x6404F`.
- Active Glue files in both Patch-Z archives currently contain `MAX_CHARACTERS_DISPLAYED = 8` and `MAX_CHARACTERS_PER_REALM = 8`.
- `realmcharacters.numchars` is `tinyint unsigned`.

## Non-goals

- No database schema change.
- No changes to unrelated level-10, heroic-character, dungeon, or gameplay limits.
- No 100-frame character-select UI.
- No server build, client launch, or live gameplay claim in this change unless separately requested.
