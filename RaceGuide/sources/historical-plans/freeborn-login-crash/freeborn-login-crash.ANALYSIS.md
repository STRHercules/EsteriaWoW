# Freeborn login crash — ERROR #134 (0x85100086)

**Symptom.** `Wow.exe` dies with `ERROR #134 (0x85100086) Fatal Condition` shortly after entering the
world. Reported for a Freeborn character; the dumps show it was actually *every* login.

**Verdict.** The server answered the `FreebornClaim` addon's login STATUS query with
`ChatHandler::BuildChatPacket(..., CHAT_MSG_ADDON, LANG_ADDON, ...)`. `BuildChatPacket` writes the chat
type as **one byte** (`Chat.cpp:391`), and `CHAT_MSG_ADDON == 0xFFFFFFFF` truncates to `0xFF`. The 3.3.5a
client rejects any chat type `>= 62` at the entry of its chat-message formatter by raising its own fatal
condition, so the reply crashed the client every time the addon asked — i.e. once per login, for every
character. Fixed in `src/server/game/Server/FreebornClaim.h` by sending the reply as
`CHAT_MSG_WHISPER` + `LANG_ADDON`, the encoding the core already uses for server -> client addon replies.

## Evidence

Three crashes, minutes apart, same signature: `G:\3.3.5a - Dev\Errors\2026-09-24 06.2{4,9}.{48,22,52} Error.{txt,dmp}`
(the first is 68 s after the 06:23 archive install).

1. **It is not a segfault.** The top frame of the "current thread" is inside the client's own fatal-error
   wrapper: `0x772AA0` pushes the literal `0x85100086` and calls the reporter. `0x8889B0` above it is the
   `FatalCondition("%s", msg, ...)` helper; `0x50AD91` is a tiny noreturn block `FatalCondition("", "")`
   — a `default:` reached from the function below it.

2. **The raiser is the chat-message formatter.** Resolving each return address back to its `call`:

   ```
   0x50AD91 FatalCondition("")            default block of the function below
   0x50C3AA -> 0x509DD0                   chat message display, ChatFrame.cpp
   0x50EBC9 -> 0x50BE70                   parses SMSG_MESSAGECHAT (Player_C.h assert block)
   0x632029 (call eax) -> 0x50EBA0        the opcode handler
   0x6324C9 -> 0x631FE0                   packet dispatcher: uint16 opcode -> handler table
   ```

   `0x631FE0` is the generic dispatcher: read a `uint16` opcode, bound it by `0x51F`, index
   `[edi + op*4 + 0x53C]` for the handler and `[edi + op*4 + 0x19B8]` for its user data, call it.
   `0x50BE70` reads `uint8` chat type, `uint32` language, 8-byte sender GUID, `uint32`, then switches on
   the type byte against `0xC`, `0xE`, `0x29`, `0x2A`, `0x10`, `0xF`, `0xD`, `0x2F`, `8`, `7`, `9`,
   `0x19`, `0x24`-`0x26`, `0x2E`, `0x30`, `0x31` — exactly the `CHAT_MSG_*` values. `0x509DD0` references
   `.\ChatFrame.cpp`, `CHAT_SAY_UNKNOWN`, `CHAT_FILTERED`, `|Hquest:`, `LAUGH_WORD%d`, `PARTY`/`RAID`/
   `GUILD`/`BATTLEGROUND`/`WHISPER`/`SYSTEM`.

3. **The argument values come straight out of the minidump.** The dumps carry the full thread stacks, so
   the formatter's frame (`ebp = 0x0CABFD30`) can be read directly. Its return address is `0x0050C3AF`
   and its arguments are, in all three crashes:

   | arg | value | meaning |
   | --- | --- | --- |
   | 0 | heap ptr | sender name/object |
   | **1** | **`0xFF`** | **chat type — the value the client validates** |
   | 3 | `0xFFFFFFFF` | `LANG_ADDON` |
   | 6 | `0x009E14FF` | `""` |
   | 7 | `0x1F3` / `0x1F2` | sender GUID low (Kekelol is `0x1F3`) |

   `0x509DD0` checks its second argument *first*: `mov ebx, [ebp+0xC]; cmp ebx, 0x3E; jge 0x50AD91`.
   `0xFF >= 62`, so the fatal condition fires before any other processing.

4. **Why the client accepts the whisper encoding.** `0x509DD0` skips its whisper/emote fix-up when
   `[ebp+0x14] == -1` (`0x509EC7`), i.e. the client's model of an addon message is *a normal chat type
   plus `LANG_ADDON`*. The core agrees: `AddonChannelCommandHandler::Send` (`Chat.cpp:1107`) uses
   `CHAT_MSG_WHISPER` + `LANG_ADDON`, and the addon asks with `SendAddonMessage(PREFIX, body, "WHISPER", ...)`.
   `CHAT_MSG_ADDON` is a client-side *event* name, not a wire type.

## The fix

`src/server/game/Server/FreebornClaim.h`, STATUS reply only — `CHAT_MSG_ADDON` -> `CHAT_MSG_WHISPER`.
`LANG_ADDON` is unchanged, so the client still routes the body to `CHAT_MSG_ADDON` and never draws it.

## Verification

1. Rebuild `worldserver` (nothing else changed) and restart it.
2. Log in any character. The addon asks STATUS once per session; the client must stay alive and the
   reply must not appear in the chat frame.
3. Log in a Freeborn character and confirm `/freeborn` still reports `persistent team Freeborn`, and the
   character-select emblem is still written (the reply contract is unchanged — prefix `FREEBORN`, body
   `team\t3`).
4. `G:\3.3.5a - Dev\Errors\` must gain no new `Error.dmp` in the session.

## Related sites worth a look (not the reported crash)

`CHAT_MSG_ADDON` may never be passed as a packet type anywhere. Still on the list:

- `CreatureTextMgr::SendChat(..., CHAT_MSG_ADDON, LANG_ADDON, ...)` is safe only because line 312
  substitutes the `creature_text` row's own type — a row with type `>= 62` would crash every client that
  receives it.
- `LuaEngine` `SendAddonMessage` takes the type from the script (`CHECKVAL<uint8>`), so a Lua call that
  passes `CHAT_MSG_ADDON` reintroduces exactly this crash.
- `MAX_CHAT_MSG_TYPE` is `0x34` (52) and the client's own bound is 62; every real `ChatMsg` value other
  than `CHAT_MSG_ADDON` is in range.

## Tooling left behind

Written for this diagnosis and reusable for any client crash:

- `dump_exception.py` — parses a WoW 32-bit minidump: streams, modules, thread contexts (the dumps have
  no exception stream; the handler thread sits in a wait, so read the thread stacks instead).
- `disasm.py` — PE32 + capstone helper: `func <va>`, `range <va> <n>`, `stack <dump> <esp>`, `str <va>`.
- `resolve_frames.py`, `find_callers.py`, `find_tables.py`, `scan_strings.py` — return-address -> call
  site, caller search, switch-table search, and embedded file/message-string scan.
