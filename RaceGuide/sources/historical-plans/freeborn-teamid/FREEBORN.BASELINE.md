# Freeborn TeamId baseline

Captured 2026-09-23 before source edits. This local plan is gitignored.

## Checkout

- HEAD: `432614a05930223aa4f36a82136749c506dcb34f`
- Pre-existing changes preserved: deleted `FREEBORN-IMPLEMENTATION.md`, modified `TASK.md`, untracked `.codex-remote-attachments/`, untracked `Freeborn_Third_TeamId_Implementation_Specification.md`.
- No source edits at baseline capture.

## Runtime

- `ac-database` started by explicit user request; `mysql:8.4`, healthy. No SQL statements changed data; a consistent pre-migration dump was made.
- `ac-worldserver` remains stopped; last container image `acore/ac-wotlk-worldserver:master`, image ID `sha256:04ea706531dae4c95e345706143da941ddfa911ccb25beb071295771a1be796a`.
- Effective running worldserver config/build cannot be confirmed while stopped. `env/dist/etc/worldserver.conf` is only the mounted file; `Updates.EnableDatabases = 7`.
- No worldserver, importer, build, or migration started/applied.

## Character database

- `acore_characters.characters` has no `teamId` column.
- Table data/index size: 25.1 MB; 416 characters total.
- Existing race counts: `1:33, 2:45, 3:25, 4:31, 5:31, 6:25, 7:24, 8:27, 9:27, 10:33, 11:30, 12:30, 13:39, 14:3, 18:1, 19:1, 20:1, 21:3, 28:3, 30:2, 31:1, 43:1`.
- Every existing race maps through the deployed `chrraces_dbc` overlay: DBC field 7 (`TeamID`, exposed as SQL `BaseLanguage`) is `1` Horde or `7` Alliance. No current row is unmapped or invalid.
- Effective SQL DBC table contains race IDs through 44. It includes race 29 (Kul Tiran), 30/31 (Illidari), and 43/44 (Darkfallen); registry omits 29-31. Migration map must use data, not registry or race masks.
- RaceMgr::LoadRaces excludes CHRRACES_FLAGS_NOT_PLAYABLE; active creator Lua enumerates GetAvailableRaces(). Migration maps current character races plus active client DBC rows with playable flags. Other IDs stay NULL and fail the final NOT NULL migration step.
- Pre-migration dump: `R:\Users\Zach\Documents\EsteriaWoW-Backups\freeborn-pre-migration-20260923\acore_characters.sql.gz`; SHA-256 `f91b0858d3b2d307055073ef027267ae85cf847a5e04b16d5c7d92a0b911caff`. Gzip decompression and presence of character-table DDL verified. Dump not restored/tested.

## Server/client data

- Base server `/data/dbc/ChrRaces.dbc`: 26 rows; SHA-256 `0987c7071a1267d636e29e9f35bb592eba62d2f2f4686b090db7865dd26fb139`. The deployed world DB overlay supplies custom race rows; base file alone is incomplete.
- SHA-256 manifest for 246 DBC files in the server data volume: `R:\Users\Zach\Documents\EsteriaWoW-Backups\freeborn-pre-migration-20260923\server-data-volume-dbc.sha256`.
- Server bind-mounted `AreaTable.dbc` SHA-256 `4e1b3495ca7bcd4929ada743a506d845c12e8a58b6cbc8a7447f5dce9718c4d7`; `SkillRaceClassInfo.dbc` SHA-256 `71cbaf79c8ae853740dedabe194498e44c1054441fb9e4540df0d172c6025258` (both also appear in the volume manifest).
- Active root/enUS client `ChrRaces.dbc` entries each contain 32 identical rows, including races 29-31 and 43-44. No loose race DBC/continuation file found; client `wxl-dbc.manifest` is empty.
- Active root/enUS `CharacterCreate.lua` both report `MAX_RACES = 40` and call `CharacterCreateEnumerateRaces(GetAvailableRaces())`; live creator behavior is not confirmed.
- Client SHA-256: root `patch-Z.MPQ` `bad1009bd752838c538123d16e7936878828f6f44968c0192eb3d26c986056b3`; locale `patch-enUS-Z.MPQ` `2e2aab0c88978f0bd600c5811d4893eb7714b3ca32cdac78210e90ea8bb31cd1`; `Wow.exe` `7e642c5c90202520f2a575ce59daaffa29157e46e94cf8536f25467fed4a7624`; `Client.dll` `528bcb5c9525c1407fd680476cb258da9c404170a648c6fb0a15bbe38b04bc1e`; `WarcraftXL.dll` `558db91db921a6e6872c7c40b17e777689fabbe7d794dc1a5835e79513e2813e`.

## Source hazards confirmed

- `TeamId` is Alliance `0`, Horde `1`, Neutral sentinel `2`; value `3` unused in the core enum. `Team` is a separate DBC-style enum.
- `Player::SetFactionForRace()` currently overwrites `m_team`; `GetTeamId(true)` derives race origin.
- Character select/login/insert/update/cache queries omit persisted team.
- Core, enabled-module candidates, and Playerbots contain many persistent-team comparisons and team-indexed arrays. Phase H must route match arrays through validated A/H sides; Phase I must handle Eluna/modules. No mechanical array expansion.
- Code review and runtime gates remain pending; this baseline does not claim Freeborn behavior is live.
