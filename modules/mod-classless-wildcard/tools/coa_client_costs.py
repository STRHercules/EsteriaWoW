"""Restore authoritative costs after retiring the legacy client cost floor."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

MODULE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MODULE / 'client-patch'))
from lib import coa


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target-client', required=True)
    parser.add_argument('--server-spell-dbc', required=True)
    args = parser.parse_args()
    server = coa.Table(Path(args.server_spell_dbc).read_bytes(), 234, 'server Spell.dbc')
    costs = {spell: [server.cell(spell, 42), server.cell(spell, 204)] for spell in server.ids}
    query = subprocess.run(['docker', 'exec', 'ac-database', 'sh', '-c',
        'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -N -B -e '
        '"SELECT ID,ManaCost,ManaCostPct FROM acore_world.spell_dbc"'],
        capture_output=True, check=True)
    for line in query.stdout.decode('utf-8').splitlines():
        spell, flat, percent = map(int, line.split('\t'))
        costs[spell] = [flat, percent]
    _archive, data = coa.winning_file(coa.target_archives(args.target_client), coa.SPELL)
    target = coa.Table(data, 234, 'target Spell.dbc')
    changed = {spell: value for spell, value in costs.items() if spell in target.ids and
               [target.cell(spell, 42), target.cell(spell, 204)] != value}
    path = MODULE / 'client-patch/coa_costs.json'
    path.write_text(json.dumps(changed, sort_keys=True, indent=1) + '\n', encoding='utf-8', newline='\n')
    print('Restored cost data for %d existing client spells; no other fields change.' % len(changed))


if __name__ == '__main__':
    main()
