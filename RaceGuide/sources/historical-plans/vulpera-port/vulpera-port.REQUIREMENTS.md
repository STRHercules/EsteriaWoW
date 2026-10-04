# Vulpera Retail rebase

Authorized October 2, 2026 by the user request and repeated `proceed` instructions, including required
native/worldserver builds and deployment. Existing dirty Earthen, Haranir, Skyborne and UI work is preserved.

- Identity remains Esteria race 20, Horde, `Vulpera`, prefix `Vu`, display IDs 60006/60007 and existing classes,
  starts, languages and racial mechanics. This is an appearance/model replacement, not a new race identity.
- Source: Retail product wow 12.1.0.69933, build dcfc90fffd79ba00406ae46f5f657592,
  CDN 43061ca8e9f0e2603c8ab50bcae97c2d. Retail race35, ChrModel69/70, M2 FileDataIDs1890761/1890759.
- Retain eight playable fur colors, six faces, six snouts, six male/eight female ears, three patterns,
  fourteen ordinary eyes plus the class-restricted DK eye, earrings and all four source eyesight states.
  Constant Hair Style remains encoded. Source class restrictions apply. Internal/NPC/transmog placeholders
  remain in the source audit and are not player options. This graph has no BONE morphs or collection models.
- Five stock appearance bytes fit all included independent choices. Source choice IDs, order and mixed-radix
  factors are frozen in G:/RetroPorterWork/vulpera/integration/codec.json. No new packet extension or schema.
- All source body vertices, selectable authored meshes, 336 animation sequences per gender, attachments,
  events, opacity/UV/camera tracks and hard texture dependencies are included. Final equipment paths must
  preserve stock armor groups and source-derived atlas mapping; no arbitrary old helmet anchor calibration.
- The current two male Paladins (GUID423/499) need a guarded semantic appearance migration, preserving their
  race/class/GUID and unrelated character state. Back up original tuples and exact migrated values.
- Creator independent controls and source class restrictions, Character Select, local/nearby player render,
  saved appearance, relog and component lifetime all use the existing repaired native helper.
- Stock barber retains the prior combined-value interface; preservation and validation must work. An
  independent-control in-game barber is a separate UI feature, not a prerequisite for creator parity.
- Active client G:/3.3.5a - Dev, enUS. Patch current global/locale Z archives from verified copies; namespace
  models under custom/vulpera/native. Preserve existing portraits, race layout, tooltips and gameplay data.
- Build helper in C:/Users/Zach/.codex/tmp/vulpera. Preserve Wow.exe and the WXL foundation fingerprint.
  Backups live outside Data. Server changes require one build and worldserver-only recreation, no volume reset.
- Gates: dependency closure, source geoset/material coverage, atlas/animation bounds, codec/class checks,
  unchanged unrelated DBC rows, native existing-race/lifetime regressions, verified install hashes.
- Live acceptance is separate: both genders/every control, randomize and stock-race transitions; saved
  characters; walk/run/jump/dance/talk/combat/cast/mount/sheath; gloves/sleeves/boots/pants/belt/cloak/helmets;
  nearby players; logout/relog/full client exit. Do not claim these checks from static evidence.

Linked historical reference chats: Maghar01a0f1f5-6392-7472-8a83-b0d84b06ff67,
Mechagnome01a0f629-08d3-7572-96f9-00be2deed0f7, Earthen01a0f7f0-55e4-78a1-8d22-d31e99824e83,
Highmountain01a0f684-d4ad-7bd1-bc05-19bd5c8d62de, Haranir01a0fa05-e185-7093-97c0-55de45954e79.
