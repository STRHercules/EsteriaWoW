# Task Board

## v0.1 scaffold

- [x] Establish module layout and config.
- [x] Add deterministic pure-C++ generator core.
- [x] Add permanent client item-ID pool model.
- [x] Add verified appearance catalog with fail-closed behavior.
- [x] Add world DB metadata schema.
- [x] Add client manifest validation/expansion tools.
- [x] Add standalone tests and architecture docs.

## v0.2 runtime registry

- [ ] Implement and test a minimal AzerothCore core API for registering one validated `ItemTemplate` at runtime.
- [ ] Add an AzerothCore `IRuntimeItemRegistry` adapter.
- [ ] Prove pointer/reference safety and duplicate behavior under core tests.

## v0.3 persistence + command

- [ ] Map `GeneratedItemDraft` to the complete `item_template` row using server generation rules.
- [ ] Make persistence transactional: reserve ID, write canonical template, write provenance, register runtime template.
- [ ] Add a permission-safe `.pitem generate` GM command.
- [ ] Add validation output that shows pool key, seed, entry, display, and generated stats.

## v0.4 loot integration

- [ ] Add configurable creature/world drop hook.
- [ ] Add source context and level/quality/role selection.
- [ ] Add anti-flood limits and generation metrics.
