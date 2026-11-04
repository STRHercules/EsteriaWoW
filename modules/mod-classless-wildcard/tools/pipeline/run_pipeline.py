from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[4]
out = Path('G:/coa-build/codex-batch7-20261103')
module = root / 'modules/mod-classless-wildcard'
source = 'R:/Users/Zach/Documents/GitHub/azerothcore-wotlk-coa'
client = 'G:/3.3.5a - Dev'
steps = [
    ('catalog', ['python', '-u', str(module / 'data/sql/generators/gen_coa_import.py'),
        '--coa-client', 'G:/CoAClient/Client', '--coa-core', source, '--target-client', client,
        '--server-spell-dbc', str(root / 'modules/mod-custom-server/data/dbc/retroported-races/Spell.dbc'),
        '--world-spell-ids', str(out / 'world-spell-ids-before-coa.txt'),
        '--coverage', str(root / '.agents/plans/coa-classless-integration/coa-classless-integration.COVERAGE.json')]),
    ('scripts', ['python', '-u', str(module / 'tools/coa_sql_slice.py'), '--coa-core', source]),
    ('creatures', ['python', '-u', str(module / 'tools/coa_creature_slice.py'), '--coa-core', source]),
    ('patch', ['python', '-u', str(module / 'client-patch/build_coa_patch.py'),
        '--coa-client', 'G:/CoAClient/Client', '--target-client', client, '--out', 'G:/coa-build/batch7.MPQ']),
]
for name, command in steps:
    with (out / (name + '.log')).open('w', encoding='utf-8') as log:
        result = subprocess.run(command, cwd=root, stdout=log, stderr=subprocess.STDOUT)
    print(name, 'exit', result.returncode, flush=True)
    print('\n'.join((out / (name + '.log')).read_text(encoding='utf-8', errors='replace').splitlines()[-4:]), flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)
