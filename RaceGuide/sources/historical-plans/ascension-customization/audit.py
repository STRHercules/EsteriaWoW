import collections
import hashlib
import json
import pathlib
import struct
import sys

sys.path.insert(0, 'tools')
sys.path.insert(0, 'modules/mod-classless-wildcard/client-patch')
from cars_mount_pack import Wdbc
from lib.clientfs import ClientFiles

ROOT = pathlib.Path(r'C:\Users\Zach\.codex\tmp\ascension-customization')
RACES = {1: 'Human', 2: 'Orc', 3: 'Dwarf', 4: 'NightElf', 5: 'Scourge',
         6: 'Tauren', 7: 'Gnome', 8: 'Troll', 10: 'BloodElf', 11: 'Draenei'}
tree = {x['path'].lower(): x for x in json.loads((ROOT / 'upstream-tree.json').read_text())['tree']}
base = {n: Wdbc((ROOT / 'client-before' / (n + '.dbc')).read_bytes()) for n in
        ('CharSections', 'CharHairGeosets', 'CharacterFacialHairStyles', 'ChrRaces',
         'CreatureDisplayInfo', 'CreatureModelData')}
donor = {n: Wdbc((ROOT / 'donor-dbc' / (n + '.dbc')).read_bytes()) for n in
         ('CharSections', 'CharHairGeosets', 'CharacterFacialHairStyles')}
client = ClientFiles(r'G:\3.3.5a - Dev\Data', 'enUS')
result = []
for race, name in RACES.items():
    for gender, sex in enumerate(('Male', 'Female')):
        current = [r for r in base['CharSections'].rows if r[1:3] == [race, gender]]
        incoming = [r for r in donor['CharSections'].rows if r[1:3] == [race, gender]]
        summary = {'race': race, 'sex': sex}
        for source, rows in (('base', current), ('donor', incoming)):
            summary[source] = {str(t): {'variations': sorted({r[8] for r in rows if r[3] == t and r[7] & 1}),
                                       'colors': sorted({r[9] for r in rows if r[3] == t and r[7] & 1})}
                               for t in range(5)}
        display = base['ChrRaces'].row(race)[4 + gender]
        model = base['CreatureDisplayInfo'].row(display)[1]
        path = base['CreatureModelData'].text(base['CreatureModelData'].row(model)[2])
        skin_path = path[:-3] + '00.skin'
        data, provider = client.find(skin_path)
        count, offset = struct.unpack_from('<2I', data, 28)
        geometry = {struct.unpack_from('<H', data, offset + i * 48)[0] for i in range(count)}
        cg = [r[1:] for r in base['CharHairGeosets'].rows if r[1:3] == [race, gender]]
        dg = [r[1:] for r in donor['CharHairGeosets'].rows if r[1:3] == [race, gender]]
        cf = [r for r in base['CharacterFacialHairStyles'].rows if r[:2] == [race, gender]]
        df = [r for r in donor['CharacterFacialHairStyles'].rows if r[:2] == [race, gender]]
        summary.update(model=path, provider=provider, missing_hair_geosets=[r for r in dg if r[3] and r[3] not in geometry],
                       new_hair_rows=[r for r in dg if r not in cg], new_facial_rows=[r for r in df if r not in cf])
        # Content hashes identify donor files even though Esteria uses Race2 paths.
        equal = missing = different = 0
        refs = set()
        for r in incoming:
            if r[7] & 1 and not r[7] & 4:
                refs.update(donor['CharSections'].text(r[f]) for f in (4, 5, 6) if r[f])
        for original in sorted(refs):
            normalized = original.replace('\\', '/').lower()
            parts = original.split('\\')
            if parts[0].lower() == 'character' and parts[1].lower() == name.lower():
                parts[1] += '2'
            candidate = '\\'.join(parts)
            try:
                payload, _ = client.find(candidate)
            except FileNotFoundError:
                missing += 1
                continue
            sha = hashlib.sha1(b'blob ' + str(len(payload)).encode() + b'\0' + payload).hexdigest()
            entry = tree.get(normalized)
            if entry and sha == entry['sha']:
                equal += 1
            else:
                different += 1
        summary['texture_comparison'] = dict(equal=equal, missing=missing, different=different, refs=len(refs))
        result.append(summary)
        print(json.dumps({k: v for k, v in summary.items() if k not in ('base', 'donor')}) , flush=True)
client.close()
(ROOT / 'audit.json').write_text(json.dumps(result, indent=2))
