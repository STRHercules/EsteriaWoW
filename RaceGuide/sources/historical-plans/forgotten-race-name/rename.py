"""Back up, stage, and install only the Forgotten presentation data."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import creature_race_pack as c
import test_forgotten_race_name as check

p = c.p
PLAN = Path(__file__).resolve().parent
REPORT = PLAN / 'install.json'
RELATIVES = (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL)
DBC_KEY = p.DBC_ROOT + 'ChrRaces.dbc'
SERVER = p.SERVER_DBC_ROOT / 'ChrRaces.dbc'


def closed_client():
    processes = subprocess.check_output(['tasklist', '/FO', 'CSV', '/NH'], text=True).lower()
    if any(name in processes for name in ('wow.exe', 'eclipse.exe', 'mpqeditor.exe')):
        raise RuntimeError('Close WoW/Eclipse/MPQEditor before installing the race-name change')


def rename_dbc(data):
    table = p.RawWdbc(data)
    if (table.fields, table.record_size) != (69, 276):
        raise ValueError('Unexpected ChrRaces layout')
    rows, pool = [], bytearray(table.strings)
    offset = p._append_string(pool, 'Forgotten')
    found = set()
    for row in table.records:
        race = p._value(row, 0)
        if race in (58, 59):
            expected = b'ThinHuman' if race == 58 else b'ThinHumanHorde'
            if p._string(table.strings, p._value(row, 44)) != expected:
                raise ValueError('Race ID belongs to another file string')
            found.add(race)
            for field in check.NAME_FIELDS:
                if p._string(table.strings, p._value(row, field * 4)) not in (b'Human', b'Forgotten'):
                    raise ValueError('Unexpected existing name in target race')
                row = p._replace(row, field * 4, 4, offset)
        rows.append(row)
    if found != {58, 59}:
        raise ValueError('Expected both ThinHuman race rows')
    result = table.build(rows, bytes(pool))
    check.check_races(result)
    for old, new in zip(table.records, p.RawWdbc(result).records, strict=True):
        for field in range(table.fields):
            if p._value(old, 0) not in (58, 59) or field not in check.NAME_FIELDS:
                assert old[field * 4:field * 4 + 4] == new[field * 4:field * 4 + 4]
    return result


def rename_glue(name, data):
    text = data.decode('utf-8-sig')
    if name in ('CharacterInfo.lua', 'ECS_Schema.lua'):
        count = 0
        lines = text.splitlines(keepends=True)
        for index, line in enumerate(lines):
            if re.search('thinhuman', line, re.I):
                lines[index], replaced = re.subn(r'(\bname\s*=\s*)"Human"', r'\1"Forgotten"', line)
                count += replaced
        text = ''.join(lines)
        if name == 'CharacterInfo.lua':
            text, replaced = re.subn(r'(info\.Name=)"Human"(?=;\nRaceInfoByFileString\.THINHUMAN(?:HORDE)?=)',
                                    r'\1"Forgotten"', text)
            count += replaced
            text += c.FORGOTTEN_GLUE
        if count != 4:
            raise ValueError(f'Expected four {name} display labels, found {count}')
    else:
        text, count = re.subn(r'(\bTHINHUMAN(?:HORDE)?=)"Human"', r'\1"Forgotten"', text)
        if count != 2:
            raise ValueError(f'Expected two GlueStrings display labels, found {count}')
    return text.encode('utf-8')


def stage():
    closed_client()
    backup = Path('G:/EsteriaBackups') / ('forgotten-name-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup.mkdir(parents=True, exist_ok=False)
    report = {'backup': str(backup), 'source_hashes': {}, 'stage_hashes': {},
              'exe_hash': p.sha256(p.CLIENT_DEFAULT / 'Wow.exe'), 'status': 'preparing'}
    storm = p.Storm(p.DLL_DEFAULT)
    for relative in RELATIVES:
        live, saved, staged = p.CLIENT_DEFAULT / relative, backup / relative, backup / 'staged' / relative
        saved.parent.mkdir(parents=True, exist_ok=True)
        staged.parent.mkdir(parents=True, exist_ok=True)
        digest = p.sha256(live)
        shutil.copy2(live, saved)
        if p.sha256(saved) != digest:
            raise ValueError('Archive backup hash differs')
        report['source_hashes'][str(relative)] = digest
        print('BACKED UP', relative, digest, flush=True)
        handle = storm.open_archive(saved)
        try:
            metadata = {key: values for key, *values in storm.list_files(handle)}
            updates = {DBC_KEY: rename_dbc(storm.read(handle, DBC_KEY))}
            glue = {name: rename_glue(name, storm.read(handle, p.GLUE_ROOT + name)) for name in check.FILES}
            check.check_glue(glue)
            updates.update({p.GLUE_ROOT + name: data for name, data in glue.items()})
        finally:
            storm.dll.SFileCloseArchive(handle)
        shutil.copy2(saved, staged)
        storm.replace_archive_entries(staged, updates)
        handle = storm.open_archive(staged)
        try:
            after = {key: values for key, *values in storm.list_files(handle)}
            assert set(after) == set(metadata)
            for key, values in metadata.items():
                if key not in updates and not key.startswith('('):
                    assert after[key] == values, key
            for key, data in updates.items():
                assert storm.read(handle, key) == data, key
        finally:
            storm.dll.SFileCloseArchive(handle)
        assert staged.stat().st_size < 0x80000000
        report['stage_hashes'][str(relative)] = p.sha256(staged)
        print('STAGED', relative, 'four entries; unrelated archive entries preserved', flush=True)
    report['server_hash'] = p.sha256(SERVER)
    shutil.copy2(SERVER, backup / 'ChrRaces.before.dbc')
    assert p.sha256(backup / 'ChrRaces.before.dbc') == report['server_hash']
    (backup / 'ChrRaces.dbc').write_bytes(rename_dbc(SERVER.read_bytes()))
    check.check(backup / 'staged', backup / 'ChrRaces.dbc')
    report['status'] = 'staged'
    REPORT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (backup / 'install.json').write_bytes(REPORT.read_bytes())
    print('READY', backup, flush=True)


def install():
    closed_client()
    report = json.loads(REPORT.read_text())
    assert report['status'] == 'staged'
    backup = Path(report['backup'])
    check.check(backup / 'staged', backup / 'ChrRaces.dbc')
    assert p.sha256(p.CLIENT_DEFAULT / 'Wow.exe') == report['exe_hash']
    assert p.sha256(SERVER) == report['server_hash']
    for relative in RELATIVES:
        assert p.sha256(p.CLIENT_DEFAULT / relative) == report['source_hashes'][str(relative)]
        assert p.sha256(backup / 'staged' / relative) == report['stage_hashes'][str(relative)]
    closed_client()
    try:
        for relative in RELATIVES:
            destination = p.CLIENT_DEFAULT / relative
            temporary = destination.with_suffix('.forgotten-next')
            shutil.copy2(backup / 'staged' / relative, temporary)
            assert p.sha256(temporary) == report['stage_hashes'][str(relative)]
            os.replace(temporary, destination)
            print('INSTALLED', destination, flush=True)
        # Preserve the bind-mounted file itself; Docker currently mounts this inode.
        SERVER.write_bytes((backup / 'ChrRaces.dbc').read_bytes())
        check.check()
        assert p.sha256(p.CLIENT_DEFAULT / 'Wow.exe') == report['exe_hash']
    except Exception:
        for relative in RELATIVES:
            shutil.copy2(backup / relative, p.CLIENT_DEFAULT / relative)
        SERVER.write_bytes((backup / 'ChrRaces.before.dbc').read_bytes())
        raise
    report.update(status='installed', server_installed_hash=p.sha256(SERVER))
    REPORT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (backup / 'install.json').write_bytes(REPORT.read_bytes())
    print('DONE', backup, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('stage', 'install'))
    args = parser.parse_args()
    stage() if args.action == 'stage' else install()
