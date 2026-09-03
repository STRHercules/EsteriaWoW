# Runtime ItemTemplate registration

## Why this scaffold does not fake it

The current AzerothCore `ObjectMgr` module-facing API exposes item-template lookup as const access. A generated row can be persisted to `item_template`, but a running worldserver still needs a safe way to add that template to both live item-template stores before an `Item` instance can reliably use it.

Calling the full item-template loader for every drop is deliberately rejected. Casting away constness to mutate `ObjectMgr` internals is also rejected.

## Preferred core extension

Add a small, reviewed core API whose sole job is to register one validated `ItemTemplate` at runtime. The implementation must:

1. Reject duplicate entries unless the existing template is byte-for-byte/canonically equivalent.
2. Update every item-template lookup structure atomically from the world thread.
3. Preserve pointer/reference safety for existing `ItemTemplate` consumers.
4. Refuse entries outside configured procedural ranges.
5. Return a status/error instead of partially registering an item.
6. Be covered by core tests for lookup, item creation, auction/mail persistence, and restart reload.

`src/core/RuntimeContracts.h` is the module-side seam. The future AzerothCore adapter should implement `IRuntimeItemRegistry`; the generator never talks to `ObjectMgr` directly.

## Restart-safe path

Regardless of runtime registration, every allocated item must be written to the canonical `item_template` table and to `mod_procedural_item` before it can be handed to a player. On the next normal worldserver startup, AzerothCore loads the persisted template through its ordinary item-template loader.
