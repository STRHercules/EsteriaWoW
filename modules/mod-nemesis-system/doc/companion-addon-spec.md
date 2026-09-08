# Nemesis Companion Addon Specification

## Purpose

The Nemesis Companion Addon is a World of Warcraft 3.3.5a client addon for `mod-nemesis-system`.
It provides players with a standalone, movable, zoomable map window that displays active nemeses across the realm using live server-fed updates.

The addon is intended to answer three questions quickly:

1. Where is the nemesis?
2. How dangerous is it?
3. Is it relevant to me, my party, or my guild?

## Goals

- Display all active realm-wide nemeses in a standalone addon window.
- Show each nemesis's last known location on a zoomable map.
- Show nemesis level, numeric rank, and named rank tier.
- Show relationship indicators for own, party, guild, or public nemeses.
- Show zone name, last seen age, and target/reward/threat indicators.
- Support live updates from the server while the player is online.
- Support click tooltip details and waypoint creation.
- Remain compatible with the WoW 3.3.5a client API.

## Non-Goals

- Replacing the default world map.
- Real-time creature tracking at sub-second precision.
- Exact combat-state synchronization.
- Cross-realm data sharing.
- Dependence on retail-only map APIs.

## User Experience

### Main Window

The addon provides a standalone frame named `NemesisTrackerFrame`.

Required behavior:

- Movable and closable.
- Resizable within a bounded min/max size.
- Mouse wheel zoom support.
- Drag-to-pan support if the map is zoomed in.
- Search or quick filter optional in a later phase.
- Slash command to open and close the frame.
- Optional minimap button in a later phase.

### Layout

The default layout should contain:

- Header area:
  - addon title
  - current zone filter or realm scope label
  - refresh age / connection status
  - manual refresh button
- Left panel:
  - scrollable nemesis list
- Center panel:
  - zoomable map canvas
- Bottom or right detail panel:
  - selected nemesis details
  - waypoint action button

### Nemesis List

Each row should display:

- Nemesis name
- Creature level
- Rank number
- Rank tier label
- Zone name
- Relationship icon
- Last seen age
- Reward/threat indicator

Row interactions:

- Single click selects and centers that nemesis on the map.
- Mouseover shows summary tooltip.
- Double click creates waypoint if supported.

### Map Canvas

The map canvas is a texture-backed custom map view, not the default WorldMapFrame.

Required features:

- Zone-based map rendering for the selected zone or continent.
- Zoom levels suitable for seeing local clusters and broader region placement.
- Marker plotting using normalized coordinates derived from server map and world position data.
- Marker clustering is optional in a later phase.
- Selected marker highlight.
- Different marker visuals for own, party, guild, and public nemeses.
- Marker tooltip on hover.
- Click marker to select.
- Right click marker to open waypoint action menu if available.

### Tooltip Details

Tooltip content should include:

- Nemesis name
- Creature level
- Rank number and rank tier
- Zone name
- Last seen text
- Coordinates if available to the client representation
- Relationship status:
  - Your nemesis
  - Party nemesis
  - Guild nemesis
  - Public bounty
- Reward indicator
- Threat indicator
- Affix list if the server provides it

### Detail Panel

The selected nemesis detail panel should include:

- Full name
- Level
- Rank number
- Rank tier label
- Zone
- Last seen timestamp or relative age
- Last known location text
- Relationship badges
- Reward estimate or category
- Threat estimate or category
- Affixes if available
- `Set Waypoint` button
- `Track` or `Pin` button in a later phase

## Data Model

Each nemesis entry maintained client-side should use a structure equivalent to:

```lua
{
    spawnId = 0,
    creatureEntry = 0,
    name = "",
    mapId = 0,
    zoneId = 0,
    zoneName = "",
    posX = 0,
    posY = 0,
    posZ = 0,
    mapX = 0,
    mapY = 0,
    level = 0,
    rank = 1,
    rankTier = "Marked",
    affixMask = 0,
    affixText = "",
    targetGuid = 0,
    targetName = "",
    relation = "public",
    rewardClass = "bounty",
    threatClass = "medium",
    lastSeenEpoch = 0,
    lastSeenText = "just now",
    isAlive = true,
    isTracked = false,
}
```

## Rank Presentation

The addon should show both numeric rank and a named tier.

Recommended initial mapping:

- Rank 1: `Marked`
- Rank 2: `Hated`
- Rank 3: `Relentless`
- Rank 4: `Legendary`
- Rank 5: `Mythic`

The display should always show the numeric rank even if the named tiers are adjusted later.

Example:

- `Rank 3 - Relentless`

## Relationship Semantics

The user requested realm-wide visibility with special indicators.
The server should classify each active nemesis for the receiving player.

Relationship values:

- `own`: the player is the current target owner.
- `party`: the target owner is in the player's current party.
- `guild`: the target owner is in the player's guild.
- `public`: none of the above.

Recommended icon/color semantics:

- `own`: red sword or skull highlight
- `party`: blue party-dot
- `guild`: green crest
- `public`: neutral gold marker

Priority order if multiple relations apply:

- `own` > `party` > `guild` > `public`

## Reward Indicator Semantics

The server should send a coarse reward category so the addon does not need to reproduce all server reward math.

Recommended values:

- `revenge`
- `bounty`
- `shared`
- `none`

Display examples:

- `Revenge Cache`
- `Bounty Reward`
- `Party Reward`
- `No Reward`

## Threat Indicator Semantics

The addon should show a simple, player-readable difficulty indicator.
The server should compute this from level delta, rank, and optionally affixes.

Recommended values:

- `low`
- `medium`
- `high`
- `extreme`

Optional detail string examples:

- `High threat: rank and level advantage`
- `Extreme threat: multi-affix nemesis`

## Last Seen Semantics

The user requested last known location rather than exact live position.

Server expectations:

- Update location when the nemesis is loaded, promoted, engaged, killed, or periodically sampled.
- Persist the most recent sampled coordinates and timestamp.
- Treat the stored location as last known, not guaranteed live exact position.

Client expectations:

- Show relative text such as `Seen 35s ago`, `Seen 4m ago`, `Seen 2h ago`.
- Fade or de-emphasize stale markers after configurable thresholds.

Recommended thresholds:

- Fresh: 0-60 seconds
- Warm: 1-10 minutes
- Stale: 10+ minutes

## Server to Addon Communication

### Transport

Use a WoW 3.3.5a-compatible message transport.

Recommended primary strategy:

- Server sends addon payloads through `SMSG_MESSAGECHAT` using `LANG_ADDON` or the existing system-message compatibility pattern already used by other modules in this repository.
- Client listens on `CHAT_MSG_SYSTEM` and `CHAT_MSG_ADDON` and filters messages with the `Nemesis` prefix.

Recommended prefix:

- `Nemesis`

Rationale:

- Compatible with WotLK client behavior.
- Matches patterns already present in the repository.
- Avoids relying on retail-only client APIs.

### Message Constraints

Messages must remain short enough for chat payload safety.
Bulk snapshots should be chunked.

Recommendations:

- Use versioned message headers.
- Chunk snapshot payloads when many nemeses are active.
- Include an update sequence number for reassembly.
- Keep field order fixed.
- Prefer machine-friendly tokens over verbose labels.

### Message Types

Recommended message families:

- `HELLO`
- `SNAPSHOT_BEGIN`
- `SNAPSHOT_ENTRY`
- `SNAPSHOT_END`
- `UPSERT`
- `REMOVE`
- `PING`
- `PONG`
- `WAYPOINT_ACK`
- `ERROR`

### Handshake Flow

1. Addon loads and registers prefix handling.
2. Addon requests sync using a player-accessible command path or addon message fallback.
3. Server replies with `HELLO` and capability flags.
4. Server sends full snapshot in chunks.
5. Server pushes `UPSERT` and `REMOVE` deltas live while player remains online.
6. Addon marks connection stale if heartbeats stop.

### Suggested Payload Formats

Header format:

```text
Nemesis\tV1:<TYPE>:...
```

#### HELLO

```text
Nemesis\tV1:HELLO:<capabilities>:<snapshotIntervalMs>:<heartbeatMs>
```

Example capabilities tokens:

- `waypoint`
- `affixes`
- `threat`
- `reward`
- `guildrel`

#### SNAPSHOT_BEGIN

```text
Nemesis\tV1:SNAPSHOT_BEGIN:<sequence>:<count>:<serverTime>
```

#### SNAPSHOT_ENTRY

```text
Nemesis\tV1:SNAPSHOT_ENTRY:<sequence>:<index>:<spawnId>:<entry>:<name>:<mapId>:<zoneId>:<zoneName>:<x>:<y>:<z>:<mapX>:<mapY>:<level>:<rank>:<rankTier>:<affixMask>:<affixText>:<targetGuid>:<targetName>:<relation>:<rewardClass>:<threatClass>:<lastSeenEpoch>
```

If payload size becomes too large, split into compact form and move human-readable strings to optional detail requests.

#### SNAPSHOT_END

```text
Nemesis\tV1:SNAPSHOT_END:<sequence>
```

#### UPSERT

```text
Nemesis\tV1:UPSERT:<spawnId>:<mapId>:<zoneId>:<zoneName>:<x>:<y>:<z>:<mapX>:<mapY>:<level>:<rank>:<rankTier>:<affixMask>:<affixText>:<relation>:<rewardClass>:<threatClass>:<lastSeenEpoch>
```

#### REMOVE

```text
Nemesis\tV1:REMOVE:<spawnId>:<reason>
```

Suggested reasons:

- `dead`
- `expired`
- `cleared`
- `invalid`

#### PING/PONG

```text
Nemesis\tV1:PING:<serverTime>
Nemesis\tV1:PONG:<serverTime>
```

## Client to Server Requests

The addon should support a minimal request surface.
On 3.3.5a, this may need to be implemented through chat commands rather than pure addon messages.

Recommended requests:

- Request full sync
- Request single nemesis details by spawn id
- Request waypoint for selected nemesis

Recommended player command bridge:

- `.nemesis addon sync`
- `.nemesis addon detail <spawnId>`
- `.nemesis addon waypoint <spawnId>`

If the server later supports hidden addon-message request handling safely for players, the addon can switch transports without changing the UI contract.

## Server Responsibilities

The module should be extended to provide an addon-facing service layer.

### Required Server Data Enrichment

The current module already stores or can derive:

- spawn id
- creature entry
- map id
- home position / stored position
- rank
- affix mask
- target owner guid
- creation and promotion timestamps

The addon contract additionally needs:

- creature name
- creature level
- zone id and zone name
- last seen timestamp
- player-relative relation classification
- reward category for receiving player
- threat category for receiving player
- optional rank tier label
- optional affix text
- optional normalized map coordinates

### Recommended Service Functions

Suggested internal responsibilities:

- Build realm snapshot for a requesting player.
- Build one nemesis payload for a specific receiving player.
- Classify relation state against the receiving player's own GUID, party, and guild.
- Compute reward category from existing revenge and bounty rules.
- Compute threat category.
- Push updates to subscribed online players.
- Rate limit broadcast frequency.

### Update Triggers

Push `UPSERT` when:

- a nemesis is created
- a nemesis ranks up
- a nemesis changes last known location by threshold
- a nemesis target ownership changes
- a nemesis becomes stale/fresh enough to matter visually
- a player logs in and needs initial sync

Push `REMOVE` when:

- a nemesis dies
- a nemesis expires
- GM command clears it
- stored data is invalidated

### Sampling Policy for Last Known Position

To keep overhead bounded, do not stream every movement update.

Recommended policy:

- Sample last known position at most every 10-30 seconds per loaded nemesis.
- Also update on promotion, combat enter, combat leave, evade return, and death.
- Only persist or push if moved more than a configured distance threshold.

This fits the user's requirement for last known location while avoiding noisy traffic.

## Map Coordinate Handling

Because the addon uses a standalone map, server world coordinates must be translated into coordinates the client can plot.

Recommended approach:

- Server sends `mapId`, `zoneId`, `posX`, `posY`, `posZ`.
- Addon maintains a lookup table of zone map textures and conversion metadata.
- If possible, server also sends normalized `mapX` and `mapY` for the selected zone to simplify rendering.

Preferred contract:

- Server is authoritative for normalization if reliable helpers are available.
- Client falls back to raw zone coordinates only if normalization metadata exists in addon tables.

## Waypoint Integration

The user requested marker tooltip and waypoint support.

Recommended behavior:

- Primary waypoint integration should target a 3.3.5-compatible waypoint addon if one is installed.
- Fallback behavior should copy or print coordinates in chat.
- No hard dependency should be required for MVP.

Waypoint priority order:

1. Compatible external waypoint addon if detected.
2. Internal temporary tracked coordinate marker inside addon map.
3. Chat output with zone and coordinates.

Suggested detection targets:

- TomTom-like addon if present in the user's client pack.
- Otherwise internal pin only.

## Addon Architecture

Recommended addon folder:

```text
NemesisTracker/
  NemesisTracker.toc
  Core.lua
  Constants.lua
  Data.lua
  Comm.lua
  MapData.lua
  UI/MainFrame.lua
  UI/MapCanvas.lua
  UI/NemesisList.lua
  UI/Tooltip.lua
  UI/DetailPanel.lua
  Integrations/Waypoints.lua
```

### Suggested Module Responsibilities

- `Core.lua`
  - startup
  - slash commands
  - saved variables
  - event registration
- `Comm.lua`
  - message parsing
  - sync lifecycle
  - chunk reassembly
- `Data.lua`
  - client store of active nemeses
  - selection state
  - freshness handling
- `MapData.lua`
  - zone texture lookup
  - coordinate transforms
- `UI/MainFrame.lua`
  - root frame and layout
- `UI/MapCanvas.lua`
  - rendering, zoom, pan, markers
- `UI/NemesisList.lua`
  - scroll list and sorting
- `UI/DetailPanel.lua`
  - selected nemesis details and actions
- `Integrations/Waypoints.lua`
  - optional waypoint addon bridge

## UI State and Settings

Recommended saved settings:

- frame position
- frame size
- zoom level per zone or global
- last selected zone
- show stale markers toggle
- show public markers toggle
- show guild markers toggle
- sound/alert preferences
- waypoint integration enabled toggle

## Sorting and Filtering

MVP sorting options:

- by last seen
- by rank
- by zone
- by relation
- by threat

MVP filters:

- all
- own
- party
- guild
- public
- current zone

## Performance Constraints

The addon must remain lightweight on 3.3.5a clients.

Recommendations:

- Full snapshot on login/open.
- Delta updates afterward.
- Avoid redrawing all markers every frame.
- Use throttled UI refresh at 0.1-0.25 second cadence.
- Reuse marker frames from a pool.
- Limit tooltip updates to hovered marker changes.

Server recommendations:

- Do not scan every creature every tick for addon updates.
- Reuse the existing active nemesis store.
- Push only on meaningful state changes.
- Batch snapshot sends across frames or world ticks if needed.

## Failure Handling

The addon should degrade gracefully.

Cases:

- No server support:
  - show disconnected state
  - keep UI operable but empty
- Partial fields missing:
  - display placeholders
- Waypoint integration unavailable:
  - fallback to chat coordinates
- Snapshot interrupted:
  - discard incomplete sequence after timeout

## Security and Abuse Considerations

- Only server-generated data should be trusted for nemesis state.
- Player requests should be rate limited.
- Player-accessible commands used for addon sync must not expose GM-only commands.
- The addon should not reveal hidden or invalid creatures.
- The server should only expose currently active nemesis records.

## Recommended Implementation Phases

### Phase A: Server Contract Foundation

- Add addon sync command path for normal players.
- Build snapshot and delta payload generation.
- Add per-player relation classification.
- Add last seen timestamp and zone name to outgoing payloads.

### Phase B: Addon MVP

- Standalone frame.
- Nemesis list.
- Map canvas with zoom and select.
- Snapshot ingest and live upsert/remove handling.
- Tooltip and detail panel.

### Phase C: Waypoints and Polish

- Waypoint integration.
- Sort/filter controls.
- Better marker art and rank visuals.
- Stale marker fading and connection status.

### Phase D: Advanced Enhancements

- Optional alerts for own/party/guild nemesis updates.
- Affix icons.
- Search.
- Route or multi-target planning.

## Open Technical Decisions

These are the remaining implementation decisions to confirm before coding:

1. Whether the server should use hidden system-message transport, true addon-message transport, or support both.
2. Whether normalized map coordinates should be computed server-side, client-side, or both.
3. Which waypoint addon, if any, should be the primary integration target.
4. Whether affix text should be sent directly or reconstructed client-side from affix mask constants.
5. Whether threat should be coarse static categories or personalized against the receiving player's level and group state.

## Recommended Defaults

For the first implementation pass, use these defaults:

- Transport: prefixed hidden system messages with optional addon-message support.
- Sync: full snapshot on login and on opening the frame, then live deltas.
- Sampling: 15-second last-known-position updates when loaded and moving meaningfully.
- Waypoints: internal pin plus optional external integration.
- Threat: coarse categories computed server-side.
- Reward: coarse categories computed server-side.

## Acceptance Criteria

The addon is considered MVP-complete when:

- A normal player can open a standalone nemesis tracker window.
- The window displays all active realm nemeses from the server.
- Each nemesis shows name, level, numeric rank, rank tier, zone, last seen, reward, and threat.
- The map supports zooming and selecting nemesis markers.
- Marker visuals distinguish own, party, guild, and public nemeses.
- The addon updates live without needing reloads.
- Clicking a nemesis shows a tooltip and allows waypoint creation or fallback coordinate output.

## Notes for Implementation

This specification is intentionally aligned with the current `mod-nemesis-system` runtime state already present in `src/NemesisSystem.cpp` and with the 3.3.5-compatible addon communication pattern already used elsewhere in this repository.
The next coding step should be to implement the server-client data contract before building the full addon UI.
