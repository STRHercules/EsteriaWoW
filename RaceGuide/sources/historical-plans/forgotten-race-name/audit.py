import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import retroported_race_pack as p
from mechagnome_race_pack import sql

OUT = Path(__file__).resolve().parent
storm = p.Storm(p.DLL_DEFAULT)
pattern = re.compile(r'thinhuman|\[58\]|\[59\]', re.I)
for label, relative in (('root', p.GLOBAL_ARCHIVE_REL), ('locale', p.LOCALE_ARCHIVE_REL)):
    handle = storm.open_archive(p.CLIENT_DEFAULT / relative)
    try:
        races = p.RawWdbc(storm.read(handle, p.DBC_ROOT + 'ChrRaces.dbc'))
        print(label, 'DBC', races.count, races.fields, races.record_size)
        for record in races.records:
            race = p._value(record, 0)
            if race in (1, 58, 59):
                strings = {field: p._string(races.strings, p._value(record, field * 4)).decode('utf-8')
                           for field in p.STRING_FIELDS['ChrRaces'] if p._value(record, field * 4)}
                print('RACE', race, json.dumps(strings))
        for key, *_ in storm.list_files(handle):
            if key.lower().endswith('.lua'):
                text = storm.read(handle, key).decode('utf-8-sig')
                matches = [(i, line) for i, line in enumerate(text.splitlines(), 1) if pattern.search(line)]
                if matches:
                    dest = OUT / label / key
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_text(text, encoding='utf-8', newline='\n')
                    print(label, key, json.dumps(matches))
    finally:
        storm.dll.SFileCloseArchive(handle)

with p.ClientFiles(str(p.CLIENT_DEFAULT / 'Data'), 'enUS') as client:
    for name in ('ChrRaces.dbc',):
        print('WINNER', name, client.find(p.DBC_ROOT + name)[1])
    for name in ('CharacterInfo.lua', 'GlueStrings.lua', 'ECS_Schema.lua', 'CharacterSelect.lua',
                 'CharacterCreate.lua'):
        data, winner = client.find(p.GLUE_ROOT + name)
        print('WINNER', name, winner)
        dest = OUT / 'effective' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
print('SQL_COLUMNS', sql('SHOW COLUMNS FROM chrraces_dbc;'))
print('SQL_RACES', sql('SELECT * FROM chrraces_dbc WHERE ID IN (1,58,59);'))
