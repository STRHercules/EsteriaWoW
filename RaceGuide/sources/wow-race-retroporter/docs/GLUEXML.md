# GlueXML / Character Creation

Playable-race integration eventually touches the 3.3.5a GlueXML character-creation surface, including files such as:

- `CharacterCreate.lua`
- `CharacterCreate.xml`
- `GlueParent.lua`
- `GlueStrings.lua`

Generated Glue metadata must use the target WotLK race ID and the converted/cache-independent race assets. Retail source paths and Retail race IDs must never leak into the final character-creation contract.

For large race rosters, prefer a registry/grid/scrollable selector design over hard-coding stock Wrath's ten visual race slots.
