# Procedural Items Design

## Purpose

Build an AzerothCore WotLK 3.3.5a module that can eventually create persistent Diablo/Borderlands-style equipment while preserving native WoW item behavior: correct item links, names, tooltip stats, icons/models, trade/mail/AH persistence, and restart safety.

## Architecture

The system is split into five boundaries:

1. **Client contract:** a pre-registered `Item.dbc` entry-ID pool divided by compatible static identity (`class`, `subclass`, `inventory_type`).
2. **Pure generator:** deterministic C++20 code that creates a draft from seed, level, quality, role, and pool key.
3. **Appearance catalog:** a verified allow-list of `ItemDisplayInfo.dbc` display IDs. Missing compatible assets fail closed.
4. **Persistence:** append-only entry allocation, canonical `item_template` row, and procedural provenance metadata.
5. **Runtime registry:** a narrow adapter that registers the persisted template into AzerothCore's live item-template stores. This requires a safe core API and is intentionally not fabricated in v0.1.

## Identity rules

An entry is allocated once and never recycled. The same entry must always mean the same generated item for the life of the server/database. Static client identity may never conflict with the entry's prepared `Item.dbc` row.

## Determinism

Generation is versioned. Given the same generation version, seed, and request, the pure generator must return the same draft. The scaffold uses SplitMix64 instead of standard-library random distributions so results do not depend on library implementation details.

## Visual correctness

The server never guesses a display ID. `mod_procedural_display_pool` begins empty and operators populate it only after verifying IDs against the exact Esteria client build. A generation request with no compatible appearance is rejected.

## Persistence ordering

Before a player can receive an item, the future transactional service must: choose an unused prepared entry, generate the draft, persist the complete canonical `item_template`, persist provenance, safely register the runtime template, then create/deliver the item instance. Failures before registration/delivery must not create a usable half-item.

## Runtime integration

AzerothCore currently exposes item-template lookup through `ObjectMgr`, but module code should not mutate its stores through casts or reload the entire item-template table for each drop. The preferred solution is a minimal reviewed core API for one-template runtime registration, behind `IRuntimeItemRegistry`.

## Initial scope

v0.1 implements the repository scaffold, pure deterministic generator, ID-pool model, verified appearance model, DB schema, client-manifest tools, and startup wiring. Live template insertion, full `item_template` mapping, GM commands, loot hooks, and advanced item mechanics follow after the runtime registry contract is proven.
