# AzerothCore Integration

AzerothCore integration consumes normalized target data, not raw Retail IDs.

Important world database surfaces include:

- `playercreateinfo`
- `playercreateinfo_action`
- `playercreateinfo_item`
- `playercreateinfo_skills`
- starting spell/custom spell tables as appropriate

Modern AzerothCore also derives playable/max/faction race masks from `ChrRaces` through `RaceMgr`, but race-specific C++ constants or special behavior may still require core changes.

Keep all target race IDs within the project's documented WotLK race-mask policy unless a separate core/client mask expansion is intentionally designed.
