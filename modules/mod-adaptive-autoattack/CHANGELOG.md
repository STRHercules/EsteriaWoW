# Changelog

## 0.2.0-preview

- Replace all core integration edits with existing ServerScript and UnitScript hooks.
- Preserve native Auto Shot dispatch, all five weapon types and automatic melee/ranged switching.
- Retain stock wand startup timing and normal equipment restrictions.
- Build and gameplay validated on unmodified stock AzerothCore.
- Replace patch installer with a read-only preflight; document migration from older patched versions.
- Existing spell IDs, SQL and client patches remain compatible.
- Record successful Wild Quiver testing on the preceding native-shot implementation.


## 0.1.2-preview

- Dispatch native Auto Shot (75) for bows, guns and crossbows on every class. The universal control is sufficient; native Auto Shot need not be learned separately.
- Preserve ordinary native Auto Shot when the controller is not managing it, including while the module is disabled.
- Remove the artificial 500 ms first-repeat floor only for custom wand spell 970102. Preserve remaining cooldowns and normal shot intervals.
- Keep native spell records, weapon restrictions, talents and passive grants unchanged. No new Hunter haste bonus is granted.
- Recorded 67 Hunter shots and 38 Warrior shot attempts using spell 75. The Warrior had not learned Auto Shot. Wild Quiver was not learned on either test character and remains unverified.
- User confirmed snappier wand startup. Latest changes were built on the modified playerbots core; a new full stock-core build remains pending.

## 0.1.1-preview

- Replaced inherited Auto Shot tooltip text with a description of automatic ranged/melee switching. Auto Ranged no longer claims a Hunter attack-speed bonus.
- Gave the hidden thrown and wand implementation spells their own descriptions.
- Verified that generated patches change only the custom spell descriptions; gameplay values and other spell text remain unchanged.
- This is a client-builder correction. Server code and SQL are unchanged from 0.1.0-preview, so the server startup message still identifies that controller version.
- Existing installations should restore their pre-installation client archives before regenerating patches; the builder intentionally refuses already-installed custom spell IDs. Back up current archives and follow the installation guide rather than overwriting unrelated patches.

## 0.1.0-preview

- Packaged the tested automatic ranged/melee controller as Adaptive Auto Attack.
- Included required core integration and weapon-based wand school selection.
- Included a local client builder with the final thrown-repeat corrections.
- Preserved all equipment class and proficiency restrictions; every character receives the unified controls.
- Added an enable setting, logout cleanup and optional Blizzard action-bar icons.
- Added guarded installation documentation, rollback guidance and release validation checklist.

Stock-core build, activation and user-reported ordinary-class combat validation subsequently passed on September 14, 2026. Extended checks remain listed in docs/VALIDATION.md.
