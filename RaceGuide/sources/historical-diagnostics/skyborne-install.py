import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
import retroported_race_pack as pack

client = pack.CLIENT_DEFAULT
processes = subprocess.run(['tasklist', '/FO', 'CSV', '/NH'], capture_output=True, text=True, check=True).stdout.lower()
assert 'wow.exe' not in processes and 'eclipse.exe' not in processes, 'Client must stay closed during installation'
assert not (client / 'Data' / '_two-names-backups').exists()
backup = client.parent / '3.3.5a - Backups' / ('skyborne-world-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir()
tables = {'playercreateinfo': 'race', 'player_race_stats': 'Race', 'playercreateinfo_item': 'race',
          'playercreateinfo_action': 'race', 'player_totem_model': 'RaceID'}
command = ['docker', 'exec', '-i', 'ac-database', 'sh', '-c',
           'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot --batch --skip-column-names acore_world']

def sql(text):
    return subprocess.run(command, input=text, capture_output=True, text=True, check=True).stdout

counts = {}
for table, field in tables.items():
    counts[table] = int(sql(f'SELECT COUNT(*) FROM `{table}` WHERE `{field}` IN (52,53);').strip())
assert not any(counts.values()), 'Skyborne start rows already exist; inspect ownership before replacing them'
(backup / 'before.json').write_text(json.dumps(counts, indent=2) + '\n', encoding='utf-8')
rollback = '\n'.join(f'DELETE FROM `{table}` WHERE `{field}` IN (52,53);' for table, field in tables.items())
(backup / 'rollback.sql').write_text('START TRANSACTION;\n' + rollback + '\nCOMMIT;\n', encoding='utf-8')
migration = Path(r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\data\sql\updates\pending_db_world\rev_20260930003000000.sql')
text = migration.read_text(encoding='utf-8')
sql('START TRANSACTION;\n' + text + '\nCOMMIT;\n')
after = {table: int(sql(f'SELECT COUNT(*) FROM `{table}` WHERE `{field}` IN (52,53);').strip())
         for table, field in tables.items()}
assert after['playercreateinfo'] == 20 and after['player_race_stats'] == 2
(backup / 'after.json').write_text(json.dumps(after, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'world_backup': str(backup), 'start_rows': after}), flush=True)
result = pack.install('skyborne', client)
print(json.dumps(result), flush=True)
