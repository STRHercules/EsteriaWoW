"""Consolidated module wiring and preservation checks; does not configure or compile."""
from pathlib import Path
import ast
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
cmake = (ROOT / 'CMakeLists.txt').read_text(encoding='utf-8')
configs = json.loads((ROOT / 'tests/legacy_config_options.json').read_text(encoding='utf-8'))
NEW_OPTION_PREFIXES = ('Battlemon.Follower.', 'Battlemon.Trade.', 'Battlemon.Breeding.')
registered = re.findall(r'AC_ADD_CONFIG_FILE\("\$\{CMAKE_CURRENT_LIST_DIR\}/conf/([^"\n]+)"\)', cmake)
assert len(registered) == len(set(registered)) == 3
assert set(registered) == set(configs)
assert cmake.count('AC_ADD_SCRIPT(') == 1
for filename, expected in configs.items():
    text = (ROOT / 'conf' / filename).read_text(encoding='utf-8')
    pairs = re.findall(r'^([A-Za-z][\w.]*)\s*=\s*(.+)$', text, re.M)
    actual = {key: value.strip() for key, value in pairs}
    assert len(pairs) == len(actual), 'Duplicate config option: ' + filename
    # The original options must keep their names and defaults. New features may add options, but only under the
    # prefixes below (each is documented in the .conf.dist and checked by test_conf_options.py).
    changed = {key: (value, actual.get(key)) for key, value in expected.items() if actual.get(key) != value}
    assert not changed, 'Original config options removed or changed in %s: %s' % (filename, changed)
    added = [key for key in actual if key not in expected and not key.startswith(NEW_OPTION_PREFIXES)]
    assert not added, 'Unexpected new config options in %s: %s' % (filename, added)
assert sum(map(len, configs.values())) == 56
sources = list((ROOT / 'src').glob('*.cpp')) + list((ROOT / 'src').glob('*.h'))
combined = '\n'.join(p.read_text(encoding='utf-8') for p in sources)
entrypoints = re.findall(r'void\s+(Addmod_\w+Scripts)\s*\(\)\s*\{', combined)
assert entrypoints == ['Addmod_battlemonScripts'], entrypoints
loader = (ROOT / 'src/mod_battlemon_loader.cpp').read_text(encoding='utf-8')
body = loader[loader.index('void Addmod_battlemonScripts()'):]
for function in ['AddSC_battlemon', 'AddSC_battlemon_sidecar', 'AddSC_battlemon_overworld', 'AddSC_battlemon_battles']:
    assert len(re.findall(r'void\s+' + function + r'\s*\(\)\s*\{', combined)) == 1, function
    assert body.count(function + '();') == 1, function
assert 'SetExtension(&BattlemonBattles::Instance())' in combined
assert '../../mod-battlemon' not in combined
for old in ['mod-battlemon-overworld', 'mod-battlemon-battles']:
    assert not (ROOT.parent / old).exists(), 'Retired module still present: ' + old
    for directory in ['tools', 'tests']:
        for path in (ROOT / directory).rglob('*.py'):
            if path.name == 'test_module_layout.py':
                continue
            assert old not in path.read_text(encoding='utf-8-sig'), str(path)
for folder in ['tools', 'tests']:
    for path in (ROOT / folder).rglob('*.py'):
        ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
for name, expected in json.loads((ROOT / 'tests/consolidated_sql_hashes.json').read_text()).items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
for addon in ['Battlemon', 'BattlemonBattles']:
    assert (ROOT / 'addon' / addon / (addon + '.toc')).is_file(), addon
assert (ROOT / 'tools/pixelmon/convert.py').is_file()
assert (ROOT / 'data/3d/dbc-manifest.json').is_file()
assert (ROOT / 'assets/battle-effects/manifest.json').is_file()
print('PASS: one module/entry point, four exactly-once script groups, all 56 config values, 29 unchanged SQL files, both addons and relocated tools/assets.')
