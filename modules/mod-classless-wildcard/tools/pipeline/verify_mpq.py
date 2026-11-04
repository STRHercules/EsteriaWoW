from pathlib import Path
import hashlib
import json
import struct
import sys

root = Path(__file__).resolve().parents[4]
module = root / 'modules/mod-classless-wildcard'
sys.path.insert(0, str(module / 'client-patch'))
from lib import coa
from lib.mpq import MPQArchive

manifest = json.loads((module / 'client-patch/coa_manifest.json').read_text())
costs = json.loads((module / 'client-patch/coa_costs.json').read_text())
with MPQArchive('G:/coa-build/batch7.MPQ') as patch:
    delivered = coa.Table(patch.read_file(coa.SPELL), 234, 'batch7 Spell')
    assert set(manifest['spells']) <= delivered.ids.keys()
    _where, raw = coa.winning_file(coa.target_archives('G:/3.3.5a - Dev'), coa.SPELL)
    original = coa.Table(raw, 234, 'existing Spell')
    for spell in original.ids:
        expected = original.row(spell)
        if str(spell) in costs:
            for col, value in zip((42, 204), costs[str(spell)]):
                struct.pack_into('<I', expected, col * 4, value)
        assert delivered.row(spell) == expected, 'Unrelated spell data changed: %d' % spell
    links = coa.Table(patch.read_file('DBFilesClient\\SpellCharges.dbc'), 2, 'charge links')
    pools = coa.Table(patch.read_file('DBFilesClient\\SpellChargesCategory.dbc'), 3, 'charge pools')
    for spell, maximum, recovery, key, _category in manifest['charges']:
        assert links.cell(spell, 1) == key
        assert pools.cell(key, 1) == maximum and pools.cell(key, 2) == recovery
    objects = coa.Table(patch.read_file('DBFilesClient\\GameObjectDisplayInfo.dbc'), 19, 'gameobject displays')
    wanted = json.loads((module / 'client-patch/coa_creatures_manifest.json').read_text())
    assert all(display in objects.ids for display in wanted['gameobject_displays_used'])
    print('Verified: %d imported spells; every existing spell row preserved except %d restored cost rows; '
          '%d charge links, %d recharge pools; summoned gameobject display table present.' %
          (len(manifest['spells']), len(costs), len(links.ids), len(pools.ids)))
path = Path('G:/coa-build/batch7.MPQ')
digest = hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()
Path('G:/coa-build/codex-batch7-20261103/patch-sha256.txt').write_text(digest + '\n')
print('MPQ SHA256', digest)
