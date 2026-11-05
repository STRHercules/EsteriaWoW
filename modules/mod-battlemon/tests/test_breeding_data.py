"""The breeding rules lean on catalog data: egg groups, hatch steps, evolution lines and egg moves."""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catalog import SQL, base_species, evolution_links, load_species

species = load_species()
links = evolution_links(species)
assert len(species) >= 1025, len(species)

# every dex species has egg groups and a sane hatch time (steps are multiples of one 256-step cycle)
for sid, s in species.items():
    if sid <= 1025:
        assert s['egg_groups'], (sid, s['name'])
        assert s['hatch'] >= 256 and s['hatch'] % 256 == 0, (sid, s['hatch'])

# the special groups the rules look for exist where the games put them
assert species[132]['egg_groups'] == 'Ditto', species[132]['egg_groups']
assert 'Undiscovered' in species[172]['egg_groups'], 'Pichu is a baby'
assert 'Undiscovered' in species[150]['egg_groups'], 'Mewtwo is a legendary'
assert species[1]['egg_groups'] == 'Monster,Grass' and 'Monster' in species[4]['egg_groups']
assert species[25]['gender'] != 'Genderless' and species[81]['gender'] == 'Genderless'   # Magnemite

# the base of an evolution line is what hatches: Pikachu and Raichu come from Pichu
assert base_species(25, links) == 172 and base_species(26, links) == 172
assert base_species(3, links) == 1 and base_species(1, links) == 1 and base_species(132, links) == 132

# Egg moves are looked up on the species that hatches (the first stage of the line), so every line that has egg
# moves anywhere must have them on its first stage. (A few adults also list them; that is harmless.)
egg = open(os.path.join(SQL, '2026_11_05_02_battlemon_egg_moves.sql'), encoding='utf-8').read()
egg_species = {int(m) for m in re.findall(r"^\((\d+), '\w+'\)", egg, re.M)}
assert len(egg_species) > 300, len(egg_species)
lost = sorted(sid for sid in egg_species if base_species(sid, links) not in egg_species)
assert not lost, 'egg moves that a hatching baby could never inherit: %s' % lost[:10]
print('ok', len(egg_species), 'species with egg moves')
