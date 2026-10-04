import copy
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
import expanded_appearance_pack as e
import retroported_race_pack as p
from wod_model_migration import rebuild_archive_streaming

client = p.CLIENT_DEFAULT
stage = e.STAGE / 'pack'
(stage / 'Data' / 'enUS').mkdir(parents=True, exist_ok=True)
report = p.load_json(e.ROOT / 'preparation.json')
manifest = p.load_manifest('skyborne')
names = p.load_json(p._build_root('skyborne') / 'build-report.json')['dbc_tables']
storm = p.Storm(p.DLL_DEFAULT)
tables = {name: p._read_archive_entry(storm, client / p.GLOBAL_ARCHIVE_REL, p.DBC_ROOT + name + '.dbc')
          for name in names}
section_table = p.RawWdbc(tables['CharSections'])
section_start = max(p._value(row, 0) for row in section_table.records) + 1
tables, allocation = e.expand_tables(tables, report, section_start)
print(json.dumps(allocation), flush=True)
dbcs = {p.DBC_ROOT + name + '.dbc': data for name, data in tables.items()}
create = p._read_archive_entry(storm, client / p.LOCALE_ARCHIVE_REL, p.GLUE_ROOT + 'CharacterCreate.lua').decode()
gui = {p.GLUE_ROOT + 'CharacterCreate.lua': e.gui(create).encode()}
for relative in (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL):
    print('COMPACT ' + str(relative), flush=True)
    rebuild_archive_streaming(storm, client / relative, stage / relative)
    storm.replace_archive_entries(stage / relative, {**dbcs, **gui})
asset = client / p.ASSET_ARCHIVE_REL
shutil.copy2(asset, stage / p.ASSET_ARCHIVE_REL)
art = {'\\'.join(path.relative_to(e.ART).parts): path.read_bytes()
       for path in e.ART.rglob('*') if path.is_file()}
storm.replace_archive_entries(stage / p.ASSET_ARCHIVE_REL, art)
storm.replace_archive_entries(stage / p.LOCALE_ARCHIVE_REL, art)
server = stage / 'server' / 'dbc'
server.mkdir(parents=True, exist_ok=True)
for name in p.SERVER_DBC_TABLES:
    (server / (name + '.dbc')).write_bytes(tables[name])
result = {'race_ids': [52, 53], 'codec': 'native-byte-codec-v1', 'options': report['labels'],
          'allocations': allocation, 'dbc_tables': names,
          'source_hashes': {str(r): p.sha256(client / r)
                            for r in (p.GLOBAL_ARCHIVE_REL, p.ASSET_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL)},
          'stage_hashes': {str(r): p.sha256(stage / r)
                           for r in (p.GLOBAL_ARCHIVE_REL, p.ASSET_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL)},
          'archive_sizes': {str(r): (stage / r).stat().st_size
                            for r in (p.GLOBAL_ARCHIVE_REL, p.ASSET_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL)}}
(e.STAGE / 'expanded-pack-report.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result), flush=True)
