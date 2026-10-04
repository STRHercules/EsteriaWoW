import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
import expanded_appearance_pack as e
import native_appearance_patch as n
import retroported_race_pack as p

client = p.CLIENT_DEFAULT
stage = e.STAGE / 'pack'
stage_report = p.load_json(e.STAGE / 'expanded-pack-report.json')
processes = subprocess.run(['tasklist', '/FO', 'CSV', '/NH'], capture_output=True, text=True, check=True).stdout.lower()
assert 'wow.exe' not in processes and 'eclipse.exe' not in processes
assert p.sha256(client / 'Wow.exe') == n.EXPECTED_SHA256
backup = Path('C:/Users/Zach/.codex/backups') / ('native-appearance-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True)
print('BACKUP ' + str(backup), flush=True)
relatives = (p.GLOBAL_ARCHIVE_REL, p.ASSET_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL)
before = {}
for relative in (*relatives, Path('Wow.exe')):
    source = client / relative
    expected = p.sha256(source)
    if relative in relatives:
        assert expected == stage_report['source_hashes'][str(relative)]
        assert p.sha256(stage / relative) == stage_report['stage_hashes'][str(relative)]
    target = backup / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    assert p.sha256(target) == expected
    before[str(relative)] = expected
    print('BACKUP VERIFIED ' + str(relative), flush=True)
for relative in (Path('EsteriaAppearance.dll'), Path('EsteriaAppearance.bin')):
    if (client / relative).exists():
        shutil.copy2(client / relative, backup / relative)
server = backup / 'server-dbc'
server.mkdir()
for table in p.SERVER_DBC_TABLES:
    source = p.SERVER_DBC_ROOT / (table + '.dbc')
    shutil.copy2(source, server / source.name)
    assert p.sha256(source) == p.sha256(server / source.name)
sql_command = ['docker', 'exec', '-i', 'ac-database', 'sh', '-c',
               'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot --batch --skip-column-names acore_characters']

def sql(text):
    return subprocess.run(sql_command, input=text, capture_output=True, text=True, check=True).stdout

raw = sql('SELECT guid,race,gender,skin,face,hairStyle,hairColor,facialStyle,online '
          'FROM characters WHERE race IN (52,53);')
rows = [list(map(int, row.split('\t'))) for row in raw.splitlines()]
assert all(row[8] == 0 and row[3] < 5 and row[4] < 4 and row[5] < 4 and row[6] < 8 and row[7] < 4 for row in rows)
(backup / 'character-appearance-before.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
rollback = []
for guid, race, gender, skin, face, hair, color, feature, online in rows:
    rollback.append(f'UPDATE `characters` SET `skin`={skin},`face`={face},`hairStyle`={hair},'
                    f'`hairColor`={color},`facialStyle`={feature} WHERE `guid`={guid} AND `race`={race};')
rollback.append('DELETE FROM `esteria_appearance_schema` WHERE `race` IN (52,53);')
(backup / 'rollback-character-appearance.sql').write_text(
    'START TRANSACTION;\n' + '\n'.join(rollback) + '\nCOMMIT;\n', encoding='utf-8')
for relative in relatives:
    target = client / relative
    temporary = target.with_suffix(target.suffix + '.appearance-next')
    shutil.copy2(stage / relative, temporary)
    assert p.sha256(temporary) == stage_report['stage_hashes'][str(relative)]
    os.replace(temporary, target)
    print('INSTALLED ' + str(relative), flush=True)
for table in p.SERVER_DBC_TABLES:
    source = stage / 'server' / 'dbc' / (table + '.dbc')
    target = p.SERVER_DBC_ROOT / source.name
    shutil.copy2(source, target)
    assert p.sha256(source) == p.sha256(target)
for name in ('EsteriaAppearance.dll', 'EsteriaAppearance.bin', 'Wow.exe'):
    source = e.STAGE / name
    target = client / name
    temporary = target.with_suffix(target.suffix + '.appearance-next')
    shutil.copy2(source, temporary)
    assert p.sha256(source) == p.sha256(temporary)
    os.replace(temporary, target)
    print('INSTALLED ' + name, flush=True)
migration = Path(r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\data\sql\updates\pending_db_characters\rev_20260930004000000.sql')
sql(migration.read_text(encoding='utf-8'))
after = sql('SELECT guid,race,gender,skin,face,hairStyle,hairColor,facialStyle,online '
            'FROM characters WHERE race IN (52,53);')
(backup / 'character-appearance-after.tsv').write_text(after, encoding='utf-8')
record = {'backup': str(backup), 'before_hashes': before,
          'installed_hashes': {str(r): p.sha256(client / r) for r in (*relatives, Path('Wow.exe'))},
          'helper_sha256': p.sha256(client / 'EsteriaAppearance.dll'),
          'native_catalog_sha256': p.sha256(client / 'EsteriaAppearance.bin'),
          'characters_migrated': len(rows), 'controls': list(e.LABELS)}
(backup / 'install-report.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
(e.STAGE / 'last-install.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record), flush=True)
