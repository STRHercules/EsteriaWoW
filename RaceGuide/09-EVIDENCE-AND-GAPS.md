# Conversation reconciliation and known gaps

[Back to the guide](README.md)

## Evidence hierarchy

Current source, effective client files and live readbacks establish installed state. User retests
establish only their named live scenarios. A tool report establishes its recorded static/stage result.
Older planning paragraphs and “installed, please test” replies cannot override later evidence.

All pages of the six supplied chats were read. Compact final/acceptance messages, changed paths and
referenced script tokens are retained in [conversations.json](evidence/conversations.json). Later
creature/UI/equipment/naming/exit/stock-customization/Dreadlord chats were also read and summarized in
[supplemental-conversations.json](evidence/supplemental-conversations.json).

## The six requested conversations

### [Resume Mag'har face asset fix](codex://threads/01a0f1f5-6392-7472-8a83-b0d84b06ff67)

Mag'har UV/overlay/archive repair; Skyborne curated→native expansion; portraits, names and chat.
The final state keeps Orc2 geometry for Mag'har and native expansion for Skyborne. User retests passed.

### [Port Mechagnome race](codex://threads/01a0f629-08d3-7572-96f9-00be2deed0f7)

Mechanical collections and independent controls, followed by parent animations and eye/beard repairs.
The latest visual retest is not recorded as completed.

### [Port Highmountain Tauren race](codex://threads/01a0f684-d4ad-7bd1-bc05-19bd5c8d62de)

Full choices, BONE faces, compositor/ABI/heads/pivots/eyes/tracks/teardown repairs. The final helper
removes unsafe padding observation. Gameplay, relog, ordinary-race logout and full exit were confirmed.

### [Port Earthen race](codex://threads/01a0f7f0-55e4-78a1-8d22-d31e99824e83)

Six-byte port and saved-field/owner/roster/belt/feet repairs. Final “All fixed!” supersedes the
earlier acceptance-pending paragraphs.

### [Port Haranir race](codex://threads/01a0fa05-e185-7093-97c0-55de45954e79)

uint64 persistence, ordinary controls and corrected native texture-buffer loading. Both genders,
select and gameplay were confirmed. Feet remain deferred; the failed candidate report is historical.

### [Rebase Vulpera to retail assets](codex://threads/01a0fc66-ce21-7861-b6ed-597363ce818d)

Visual rebase, helmets, codec v2, creator identity, head/tail and glow repairs. Nine changing controls
and 33 eyes supersede the eight-control first-port policy. Final live acceptance remains pending.

The Haranir conversation explicitly defers feet. This guide does not quietly reclassify that as fixed.
The latest Vulpera selection header and codec prove installed v2/glow data, not the user's visual retest.

## Later work incorporated

The supplemental records cover:

- Naga/Tuskarr/Vrykul/ThinHuman playable creature conversion, portraits and preview scaling.
- Vrykul/ThinHuman language eligibility and creator-hidden Horde Vrykul.
- ThinHuman boot/leg/cloak/head fixes, then helmet shader/alpha/reflection repairs.
- Tuskarr rounded feet and robe calf fallback.
- ThinHuman's player-facing Forgotten rename without renaming technical assets.
- Split/widened picker UI, hover/commit/restore, dropdown wheel behavior and dice/randomizers.
- Additive Ascension options for the original ten races.
- Dreadlord override and missing UV lookup.
- October 3 CharSections group-order/exit-crash repair.

These explain why the current client has more catalogs and races than a guide derived only from the six
older conversations would list.

## Current data differences

[The live audit](evidence/current-state.json) captures these differences explicitly:

1. ChrRaces has 47 client/server base rows, but semantic differences at 58/59 reflect the Forgotten
   client rename; the server mounted file still carries its earlier text.
2. CharSections has 547,108 records on both sides with identical row multiset/string pool. The client
   order is fixed for contiguous cache groups; the server file retains an earlier ordering.
3. SkillRaceClassInfo has 328 effective client rows and 364 mounted server rows with different eligibility
   policy. Native aliases are part of the client side.
4. Client legacy IDs 24–27 disagree with registry/SQL policy, and NPC reservations 32–42 are server-side
   overlays absent from the inspected client base.
5. SQL overlays include 1–44 legacy/reserved rows while modern 45–59 identity is supplied by the mounted
   standard DBC path. Source/registry presence alone does not prove every legacy UI branch is coherent.

These are documented findings. No client/server files were changed to force hash equality during
documentation.

## Exit repair is distinct from Highmountain teardown repair

The Highmountain crash was proven by a watchpoint: unsupported padding observer registration wrote
outside an NPC's old-field cache. The corrected native helper avoids that observer.

The later client-exit crash was traced through appearance-cache cleanup into heap cleanup. Both Z
archives had CharSections groups split across the table. Reproducing the client allocation logic
found 65 out-of-bounds writes; sorting unchanged records eliminated the reproduced overflows.

The later repair preserved 547,108 records and 70,505 unrelated archive entries and updated shared
writers. The chat reported no new crash file after an observed closure, but controlled computer-use
exit testing was stopped. Treat a controlled fresh exit regression as still needed. A sorted table
is not evidence that every lifetime bug is impossible.

## Live acceptance matrix

| Feature | Evidence available | Remaining named scope |
| --- | --- | --- |
| Mag'har | Both faces and selectors, portraits, chat/select touchups confirmed | Broader equipment/barber matrix |
| Skyborne | Bodies/controls/feathers/portraits/chat/first login confirmed | Armor/barber/persistence matrix |
| Mechagnome | Creation/login/chat/controls before final repair | Final animation/eye/beard retest |
| Highmountain | Appearance/talk/dance/equipment and exit/relog confirmed | Equipment/nearby-player coverage |
| Earthen | Saved appearance, roster, Gem belt and boots/barefoot confirmed | Wider race/class/equipment coverage |
| Haranir | Both genders, textures/fur/roster/game confirmed | Deferred feet; clothing/choice/persistence |
| Vulpera | Source/codec/native/stage/install evidence | Final v2 face/tail/eye/glow/helmet/exit retest |
| Creature ports | Installed conversion/art/material/data repairs | Latest chat/equipment/rename visual checks |
| Original-race additions | Additive DBC/art, prior selections preserved | Creator/barber/relog visuals |
| Dreadlord | Corrected UV table and all draw batches checked; installed | Normal/green live NPC confirmation |
| CharSections exit repair | Current sorted client table and preserved rows | Controlled fresh exit regression |

“No live confirmation in the record” is not a claim that the feature is broken. It is a limit on what
this handoff can certify.

## Reproducibility inputs and unresolved source gaps

- A matching customized foundation executable is required. The appearance patcher/64-race extension
  reject unfamiliar images. The initial foundation injector source was not found in captured trees.
- Full raw assets, extracted DB2s, CASC blocks, MPQs, runtime texture banks and vendor binaries remain
  external inputs. The source handoff records locations/builds/hashes and gives regeneration stages.
- Converter source is captured from the installed package and pinned Git provenance. Compare it if a
  newer package changes parsing/layout behavior.
- Historical installers have fixed stages, expected baseline hashes and sometimes character GUIDs.
  Those are guards and original evidence; review them for a new target rather than removing them.
- One referenced temporary file, `C:\Users\Zach\.codex\tmp\vulpera\inspect.py`, was no longer present.
  Its reference is preserved; the maintained tools and other probes are recovered.
- Earthen/Mechagnome/Skyborne have declared unimplemented face morph/tattoo/restricted-choice scopes.
- Retail racial mechanics are not implied by visual parity.
- The independent expanded barber UI does not exist.
- The working source contains uncommitted MoveCast changes without a matching live-build claim.

## Why some source README statements are stale

The native README accumulates initial install notes and later corrections. Highmountain's original
field registration explanation, Earthen's initial acceptance-pending note, Haranir's failed-loader
candidate and Vulpera v1's filter/counts remain useful history but are superseded.

This guide describes the final repair chain and observed state. Source snapshots intentionally preserve
the originals for provenance rather than silently editing historical reports.

## Audit boundaries

Documentation work used source reads, MPQ extraction, checksums, SELECT/SHOW queries and limited container
state/mount inspection. It did not run source acquisition, model conversion, a native/server build,
SQL import, client patching, live character creation, NPC spawning or service restarts.

Large MPQs were inventoried by size, and selected effective entries were parsed/hashed. That is not a
fresh all-payload verification of every archive. Recorded historical checks are identified as such.
