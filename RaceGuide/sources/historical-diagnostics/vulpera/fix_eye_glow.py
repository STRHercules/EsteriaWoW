import hashlib
import json
import os
import shutil
import struct
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
import vulpera_race_pack as v
import test_vulpera_models

live = v.p.CLIENT_DEFAULT / 'EsteriaVulpera.bin'
stage = v.STAGE / live.name
receipt = v.p.load_json(v.STAGE / 'last-install.json')
before = live.read_bytes()
digest = hashlib.sha256(before).hexdigest()
assert digest == receipt['installed_hashes'][live.name], 'Live catalog changed since installation'
assert stage.read_bytes() == before, 'Staged catalog differs from the installed catalog'
magic, version, count = struct.unpack_from('<3I', before)
assert (magic, version) == (0x314D4845, 1) and len(before) == 12 + count * 156
after = bytearray(before)
changed = []
for i in range(count):
    offset = 12 + i * 156
    gender, kind, target, value, *selectors = struct.unpack_from('<7I', before, offset)
    if kind == 0 and target == 17 and selectors == [0xffffffff] * 3:
        assert value == 1701
        struct.pack_into('<I', after, offset + 12, 1700)
        changed.append((gender, i))
assert len(changed) == 2 and {gender for gender, _ in changed} == {0, 1}
backup = Path(r'C:\Users\Zach\.codex\backups') / ('vulpera-eye-glow-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True, exist_ok=False)
shutil.copy2(live, backup / live.name)
assert v.p.sha256(backup / live.name) == digest
source = (v.p.ROOT / 'tools/vulpera_models.py').read_text()
old_line = 'record(gender, 0, group, group * 100 + (1 if group == 17 else 0))'
new_line = 'record(gender, 0, group, group * 100)'
assert source.count(new_line) == 1
(backup / 'vulpera_models.before.py').write_text(source.replace(new_line, old_line), encoding='utf-8', newline='\n')
stage.write_bytes(after)
try:
    test_vulpera_models.main()
    assert live.read_bytes() == before, 'Live catalog changed before replacement'
    temporary = live.with_suffix('.bin.vulpera-next')
    temporary.write_bytes(after)
    assert temporary.read_bytes() == after
    os.replace(temporary, live)
    assert live.read_bytes() == after
except Exception:
    stage.write_bytes(before)
    shutil.copy2(backup / live.name, live)
    raise
fix = {'backup': str(backup), 'before_sha256': digest, 'after_sha256': v.p.sha256(live),
       'changed_records': changed, 'default_glow_geoset': 1700,
       'authored_glow_choices_preserved': [14, 29, 30, 31, 32],
       'checks': 'PASS: both genders, all 33 eye colors and all four vision settings',
       'live_visual_acceptance': 'pending fresh client restart'}
build = v.p.load_json(v.STAGE / 'build-report.json')
build['companion_hashes'][live.name] = fix['after_sha256']
v.save(v.STAGE / 'build-report.json', build)
receipt['installed_hashes'][live.name] = fix['after_sha256']
receipt['companion_hashes'][live.name] = fix['after_sha256']
receipt['eye_glow_fix'] = fix
receipt['live_client_test'] = 'not_performed_after_eye_glow_fix'
v.save(v.STAGE / 'last-install.json', receipt)
v.save(backup / 'install-report.json', fix)
acceptance = v.p.load_json(v.ROOT / 'integration/acceptance.json')
acceptance.update(eye_glow_fix=fix, live_accepted=False)
v.save(v.ROOT / 'integration/acceptance.json', acceptance)
print(json.dumps(fix, indent=2))
