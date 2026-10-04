# Retail creature playable-race ports

Requested October 2, 2026. The user explicitly approved native-helper/worldserver builds and installation
with verified backups and worldserver-only recreation on the follow-up turn.

- Naga: Horde, proposed ID54, Retail race13 / ChrModel25-26; exclude helmets and feet armor.
- Tuskarr: Alliance, proposed ID55, Retail race17 / ChrModel33, male only; exclude helmets.
- Vrykul: Alliance/Horde, proposed IDs56-57, Retail race16 / ChrModel31, male only; exclude helmets.
- Human NPC: Alliance/Horde, proposed IDs58-59, Retail ThinHuman race33 / ChrModel65, male only.
- Retain the existing Human race1, NPC races32-42, Sethrak15 and all prior race ports.
- Source settings come from wow-race-retroporter/sources/retail/build.yaml. Use the prior ports' pinned
  product wow, version12.1.0.69933, build dcfc90fffd79ba00406ae46f5f657592,
  CDN43061ca8e9f0e2603c8ab50bcae97c2d. Read Retail metadata; never modify the Retail installation.
- Fetch only the selected source/customization dependencies. Store source FileDataIDs, names, keys,
  SHA-256 and dependency edges under sources/retail/races/<slug>; convert under G:/RetroPorterWork/<slug>.
- Source IDs are separate from target IDs. Client DBC winners, live world race rows, startup rows and
  characters were checked: proposed target IDs54-59 are unoccupied and have zero characters.
- Proposed model/display bands120057-120064 and60048-60055 are unoccupied in the winning client DBCs;
  final allocation additionally requires live model/display SQL and relevant DBC range checks.
- Preserve every source choice with a working rendering mapping. These are NPC races: NPC-specific
  customization requirements cannot be filtered out using the earlier playable-race-only policy.
- Audit all source SKIN geosets, actual armor coverage, socket attachments, inherited animation tracks,
  events and texture layouts. Do not label absent source geometry as supported armor.
- Retail's Tuskarr and Vrykul female ChrModel entries use the male FileDataID and placeholder choices.
  The user observed that only Naga has a proper female/body-type2 model. Use Naga both genders and the
  remaining species male only; enforce that policy in the creator and server, not just in model rows.
- Human33 is ThinHuman, whose authored geometry is male only. Enforce its gender limit in creator and
  server creation. Do not expose a cloned or phantom female model.
- Reuse existing StormLib, WDBC, native appearance and source conversion tools. Preserve installed
  appearance/geometry/material catalogs and the executable fingerprint; avoid another runtime framework.
- Generate additive DBC/client UI and scoped pending SQL. Preserve unrelated rows, assets and dirty files.
- Stage a complete, checked package before requesting compilation/deployment authorization. Backups must
  be SHA-256 verified and kept outside mountable Data directories; preserve Docker volumes.
- Server deployment, when authorized, rebuilds only code that changed and recreates only ac-worldserver.
- Static/source/packet checks and live client checks are separate. Acceptance includes every choice,
  offered gender/faction/class, creator transitions, Character Select, in-game armor and animation,
  language, nearby-player rendering, relog, logout and full client exit.

References: ChatGPT6ac03cbf-0924-83ea-bf5f-02eef9a5f4cb; Codex01a0fc66-ce21-7861-b6ed-597363ce818d,
01a0fa05-e185-7093-97c0-55de45954e79, 01a0f7f0-55e4-78a1-8d22-d31e99824e83,
01a0f684-d4ad-7bd1-bc05-19bd5c8d62de. All were read as historical context, not new instructions.
