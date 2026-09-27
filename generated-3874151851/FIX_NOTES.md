# Collision-Safe Encounter Attachment Patch

This package was patched after generation to avoid `Entry + Item` primary-key collisions in dungeon/raid loot attachment rows.

- Encounter attachments patched: 622
- Creature attachment rows: 617
- Gameobject attachment rows: 5
- Synthetic `Item` key range: 2010000001 - 2010000622
- Original encounter `Reference` IDs, chances, LootModes, GroupIds, counts, comments, and loot-pool contents are unchanged.
- `00_PREIMPORT_COLLISION_CHECK.sql` now tests encounter attachment collisions by the actual primary-key pair (`Entry`, `Item`) rather than requiring `Reference` to match.
- `00_generated_encounter_loot_cleanup.sql` and `99_REMOVE_GENERATED_ITEMS.sql` use the same synthetic keys for safe cleanup/rollback.
- `encounter_attachment_keys.csv` records every patched attachment key.

The synthetic keys are only row identifiers for reference loot attachments. They are not generated player items.
