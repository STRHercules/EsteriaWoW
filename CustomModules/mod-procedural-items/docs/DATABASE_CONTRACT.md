# Database contract

The generated item has two persistent identities:

- `item_template.entry`: the canonical WoW/AzerothCore item definition.
- `mod_procedural_item.item_entry`: immutable provenance tying that entry to its seed, generator version, pool, role, quality, source, and creation time.

`mod_procedural_id_range` is the server mirror of the client `Item.dbc` reservation manifest. It is not merely configuration: changing an allocated range can break old items, so migrations should be append-only in production.

`mod_procedural_display_pool` is intentionally empty after install. Every row is an assertion that the named display ID was verified against Esteria's exact client data. This is what prevents the generator from creating an otherwise valid item with a red `?`/incorrect visual.

Allocation policy is first-unused within a compatible pool for v0.1. The permanent-used set must include both generated metadata and canonical `item_template` occupancy before an entry is assigned.
