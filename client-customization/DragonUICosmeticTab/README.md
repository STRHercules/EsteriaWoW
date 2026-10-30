# DragonUI Cosmetics tab

The client's native spellbook tab ranges drift by a few slots, so some cosmetic wings land in
General. These three files replace DragonUI's `modules/spellbook/book_{core,controls,catalog}.lua`
and add a fourth category, **Cosmetics**, that files wings by spell id (970200-970999) instead of
trusting the client's tab ranges.

- Install: `python tools/dragonui_cosmetic_tab.py` (game closed). Re-apply after updating DragonUI.
- Client tables (wing spells, visuals, icons, skill rows): `python tools/wings_bake_client_tables.py --apply`.
  Rebuilding the Esteria / Ethereal / Kyrian client packs rewrites `Spell.dbc` and undoes it; rerun it.
