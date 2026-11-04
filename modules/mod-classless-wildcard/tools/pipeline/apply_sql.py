from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[4]
out = Path('G:/coa-build/codex-batch7-20261103')
database = sys.argv[1]
assert database in ('coa_b7_world', 'acore_world')
files = ['cw_spells_coa.sql', 'cw_coa_scripts.sql', 'cw_coa_creatures.sql',
         'cw_coa_creatures_displays.sql', 'cw_coa_enchantments.sql']
command = ['docker', 'exec', '-i', 'ac-database', 'sh', '-c',
           'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" ' + database]
for name in files:
    path = root / 'modules/mod-classless-wildcard/data/sql/db-world' / name
    with path.open('rb') as sql:
        result = subprocess.run(command, stdin=sql, capture_output=True)
    error = result.stderr.decode('utf-8', errors='replace')
    (out / (database + '-' + name + '.log')).write_text(error, encoding='utf-8')
    if result.returncode:
        raise SystemExit(name + ': ' + error)
    print(database, name, 'applied successfully', flush=True)
