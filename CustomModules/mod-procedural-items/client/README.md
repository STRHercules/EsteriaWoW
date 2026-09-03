# Client pool contract

WotLK 3.3.5a must know every procedural **entry ID** before that entry is used by the server. The server may generate the item's mutable/query-driven data later, but the entry itself must belong to the Esteria client patch's prepared `Item.dbc` pool.

## Workflow

1. Edit `item_pool_ranges.csv` to define non-overlapping ID pools.
2. Run `python tools/validate_client_pool.py client/item_pool_ranges.csv`.
3. Run `python tools/generate_client_pool_manifest.py client/item_pool_ranges.csv --output build/item_pool_manifest.csv`.
4. Feed the expanded manifest into your DBC patch pipeline and create matching `Item.dbc` rows.
5. Keep `item_class`, `subclass`, and `inventory_type` identical between the pool declaration and the generated server template.
6. Populate `mod_procedural_display_pool` only with display IDs verified in the exact client build's `ItemDisplayInfo.dbc`.

## Non-negotiable rules

- An allocated entry is permanent. Never recycle it for a different generated item.
- Never generate outside the prepared client pool.
- Never invent a display ID.
- A missing compatible display is a generation failure, not permission to fall back to an unknown asset.
- Adding brand-new models/icons still requires a client patch; generating a new name/stats combination from prepared IDs and existing verified displays does not.

The starter manifest reserves 6,000 development entries. Grow it only when the client patch and database reservation table are updated together.
