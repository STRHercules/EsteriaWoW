# Validation — 0.2.0 preview

On September 15, 2026 the hook-based module compiled and linked against stock AzerothCore revision e1823bb2db751a7cc0a90a8543e778449ebf7d84. All four previously edited core files matched their original Git blobs. Startup and login/world listening ports were verified with ten ordinary classes retained.

The tester reported successful bow, gun, crossbow, thrown and wand testing, automatic repetition and melee/ranged switching. Local controller regression checks passed with the old AttackStop callback removed. Released C++ files match the tested prototype byte for byte, including its diagnostic startup label.

Stock wand startup timing is intentional. A male dwarf wand projectile appearing to launch from the left was reproduced with stock Shoot on the same client; it is not unique to this module. No client model correction is included.

Native Auto Shot and Wild Quiver were traced on the preceding modified-core implementation: 831 damaging Auto Shots and 117 Wild Quiver damage events with rank 3 reported. This verifies proc operation, not exact probability. The hook build retains the same native spell dispatch; a dedicated new Hunter trace on it is still desirable.

Remaining checks: other core revisions, configurations with competing packet hooks, high latency/packet loss, malformed requests, disable/re-enable, extended interruption/vehicle/possession scenarios, third-party action bars, non-enUS clients and full migration/rollback matrices. Vehicles and possession retain native command handling. Custom servers that permit nonstandard wand users need separate damage-school review; ordinary class equipment restrictions remain unchanged.

This remains a preview. Do not claim universal compatibility or competitive-PvP readiness.
