from pathlib import Path
import json
import struct
import sys

root = Path(__file__).resolve().parents[4]
module = root / 'modules/mod-classless-wildcard'
sys.path.insert(0, str(module / 'client-patch'))
from lib.mpq import MPQArchive, write_archive
from lib import coa

path = Path('G:/coa-build/batch7.MPQ')
with MPQArchive(str(path)) as archive:
    names = archive.read_file('(listfile)').decode('utf-8').splitlines()
    files = {name: archive.read_file(name) for name in names if name and name != '(listfile)'}
manifest = json.loads((module / 'client-patch/coa_manifest.json').read_text())
rows = manifest['spell_affect']
spells = coa.Table(files[coa.SPELL], 234, 'CoA power contracts')
for key, power in manifest.get('client_power_overrides', {}).items():
    sid = int(key)
    assert sid in manifest['spells']
    struct.pack_into('<I', spells.records, spells.ids[sid] * spells.rec + 41 * 4, power)
files[coa.SPELL] = spells.data()
files['DBFilesClient\\EsteriaSpellAffect.dbc'] = struct.pack('<4s4I', b'WDBC', len(rows), 3, 12, 1) + b''.join(
    struct.pack('<3I', index + 1, modifier, target) for index, (modifier, target) in enumerate(rows)) + b'\0'
temporary = path.with_name('batch7-with-affect.MPQ')
write_archive(str(temporary), files)
with MPQArchive(str(temporary)) as archive:
    for name, data in files.items():
        assert archive.read_file(name) == data, 'Archive content changed: ' + name
temporary.replace(path)
print('Added %d exact client modifier routes; read back and verified all %d members.' % (len(rows), len(files)))
