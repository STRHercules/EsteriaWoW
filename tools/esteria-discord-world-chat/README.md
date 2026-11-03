# Esteria Discord ↔ World Chat

A small, isolated two-way relay between AzerothCore's existing `mod-world-chat` and one Discord text channel.

- In-game `.chat message` and `/join World` messages appear in Discord.
- Normal messages typed in the selected Discord channel appear as `[World][Discord] Name: message` in-game.
- `.chat off` is respected. Muted players cannot send messages into Discord.
- Staff-only `.chata` / `.chath` are not forwarded.
- The bot never executes GM commands or SQL queries.
- Connections are **localhost-only**, authenticated with an independent secret, and handled off the game thread.

## Requirements

- EsteriaWoW built with the updated `modules/mod-world-chat`.
- Node.js 22.12+.
- A Discord application/bot with **Message Content Intent** enabled under Bot > Privileged Gateway Intents.
- Permissions for the bot in the target channel: View Channel, Send Messages, Read Message History.
- The Node bot must run in the **same network namespace** as `worldserver` because the relay binds to `127.0.0.1`. If the worldserver runs in Docker, putting the bot on the host does **not** make host localhost accessible to the container. Deploy both together or adapt transport behind an authenticated TLS endpoint.

## Setup

1. Create or choose a Discord bot and invite it to the intended server. Copy its bot token and the text channel ID.
2. On the game server, copy the updated `WorldChat.conf.dist` values into the active `WorldChat.conf` and set:

   ```ini
   WorldChat.Enable = true
   WorldChat.CrossFaction = true
   WorldChat.DiscordBridge.Enable = true
   WorldChat.DiscordBridge.Port = 22150
   WorldChat.DiscordBridge.Secret = "a-unique-random-secret-with-at-least-32-characters"
   ```

   CrossFaction must be true: a single public Discord channel cannot safely preserve separate Horde/Alliance world-chat audiences.

3. In `tools/esteria-discord-world-chat`, copy `.env.example` to `.env`. Fill in `DISCORD_TOKEN`, `DISCORD_CHANNEL_ID`, and the **same** `BRIDGE_SECRET`. `BRIDGE_PORT` must match the server config.
4. Run:

   ```sh
   npm install
   npm test
   npm start
   ```

5. Rebuild and restart `worldserver` with the modified `mod-world-chat` sources. The worldserver log should report that the Discord world-chat bridge is enabled. Start the Node bot before or after worldserver; the C++ worker retries when it is unavailable.

Do **not** share the `.env` file or commit your real token/secret. Do not reuse the existing `mod-chat-transmitter` bot token as the bridge secret.

## Quick acceptance checklist

1. Log into WoW, type `.chat Hello Discord`, and confirm one Discord message appears.
2. In-game `/join World`, then send another message; confirm it also appears once.
3. Type `Hello Azeroth` directly into Discord `#world-chat`; every eligible in-game player sees `[World][Discord] ...`.
4. Run `.chat off` on one character: incoming Discord messages should stop for that character only. `.chat on` restores them.
5. Confirm a muted player cannot publish to Discord. `.chata` and `.chath` should not publish.
6. Type `@everyone` in WoW and verify nobody is pinged in Discord.
7. Stop the Node bot, send messages in-game, restart it, and verify the server stays responsive. Stale queued messages older than two minutes are discarded.

## Behavior and limitations

- The bridge polls over loopback HTTP about every 400 ms. It is near-real-time, not an external public WebSocket server.
- No historical chat is stored on disk. Discord → game messages are kept in a bounded in-memory window; a new worldserver connection starts at the latest message to avoid replay.
- Only text is relayed. Embeds, attachments, Discord edits/deletes, and WoW item hyperlinks are not mirrored as interactive objects.
- Discord messages are rate-limited to five per user per ten seconds and stripped of WoW control markup. Supplementary Unicode emoji are omitted for the 3.3.5a client.
- Game → Discord messages may be retried after a transport error. Message IDs are deduplicated in the bot for ten minutes, though an ambiguous failure beyond that window could result in a duplicate.
- Do not enable the bridge if the Discord text channel contains private staff information; messages written there become visible to all eligible in-game users.

## Files

- `modules/mod-world-chat/src/DiscordBridge.cpp/.h` — local HTTP bridge and thread-safe queues.
- `modules/mod-world-chat/src/WorldChat.cpp/.h` — outbound hook and safe inbound world-chat broadcast.
- `modules/mod-world-chat/conf/WorldChat.conf.dist` — disabled-by-default settings.
- `tools/esteria-discord-world-chat/src/bot.mjs` — Discord bot and loopback HTTP service.
- `tools/esteria-discord-world-chat/src/sanitize.mjs` — message sanitization utilities.
