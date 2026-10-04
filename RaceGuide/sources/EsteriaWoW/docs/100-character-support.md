# Esteria 100-Character Support

Esteria now targets 100 ordinary characters per account and per realm.

## Server

The ordinary limits default to 100 in `WorldConfig.cpp` and in the active/distributed worldserver configuration:

```ini
CharactersPerAccount = 100
CharactersPerRealm = 100
```

Deleted-character restoration, character account transfer, player dumps, and playerbot hiring use
`CONFIG_CHARACTERS_PER_ACCOUNT`. The existing `SMSG_CHAR_ENUM` count remains `uint8`; the auth
`realmcharacters.numchars` column remains `tinyint unsigned`, both of which represent 100.

No database schema change is required. `HeroicCharactersPerRealm` remains a separate limit.

## Client executable

Target:

```text
3.3.5a - Dev\Wow.exe
```

The verified build-12340 instruction was:

```text
File offset 0x6404C: 80 7D FF 0A C7 45 F8
Limit byte  0x6404F: 0A
```

The patched instruction is:

```text
File offset 0x6404C: 80 7D FF 64 C7 45 F8
```

Hashes:

```text
Original/backup: be4ccde69622f1fb01d25e5e429e8c16bf2bc66fcafd5b73442e74da9bedfe81
Patched:        7e642c5c90202520f2a575ce59daaffa29157e46e94cf8536f25467fed4a7624
```

If the executable changes, do not reuse `0x6404F` blindly. Locate the character-enum comparison,
validate the complete original instruction bytes, patch only the proven limit byte, and record the
new original/patched hashes. The backup is under:

```text
3.3.5a - Dev\Backups\character-limit-20260918\Wow.exe
```

## Character-select UI

The current eight reusable character rows remain in place. `CharacterSelect.scrollOffset` is clamped
to:

```text
0 .. max(GetNumCharacters() - MAX_CHARACTERS_DISPLAYED, 0)
```

Visible row `i` displays actual character `scrollOffset + i`. The scrollbar snaps to the existing
67-pixel row spacing, and mouse-wheel movement changes the offset by one row. Button IDs and paid
service IDs are rewritten to the actual character index, so delete, rename, login, and service
actions do not fall back to the visible-row number.

The modified payload is mirrored in:

```text
3.3.5a - Dev\Data\patch-Z.MPQ
3.3.5a - Dev\Data\enUS\patch-enUS-Z.MPQ
```

Patch-Z hashes after repack:

```text
patch-Z.MPQ:       9459ea0e28f995202f4613c3051ce3960105bb734f8d7e02869cd5acea64db13
patch-enUS-Z.MPQ:   5c4b57a26e4a10ee72a752c0cb95dbdbd4225f56831ebd723a38c7b603b59a10
```

Backups of both archives and the staging archive are in:

```text
3.3.5a - Dev\Backups\character-limit-20260918\Data
```

## Verification boundary

`python tools/test_character_limit_contract.py` passes, including server/config, executable-byte,
archive-payload, XML, and actual-index assertions. XML parses successfully. No AzerothCore build,
server restart, client launch, or live create/select/login/delete smoke test was performed.
