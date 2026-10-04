"""Snapshot, package, verify, and install the staged additive customization data."""
import argparse
import hashlib
import json
import os
import pathlib
import shutil
import struct
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, 'tools')
sys.path.insert(0, 'modules/mod-classless-wildcard/client-patch')
from cars_mount_pack import Storm, DLL_DEFAULT, Wdbc
from playable_race_pack import RawWdbc
from lib.clientfs import ClientFiles

ROOT = pathlib.Path(r'C:\Users\Zach\.codex\tmp\ascension-customization')
STAGE = ROOT / 'staged'
CLIENT = pathlib.Path(r'G:\3.3.5a - Dev')
SERVER = pathlib.Path('modules/mod-custom-server/data/dbc/retroported-races').resolve()
TABLES = ('CharSections', 'BarberShopStyle')
ARCHIVES = {'root': CLIENT / 'Data/patch-Z.MPQ', 'locale': CLIENT / 'Data/enUS/patch-enUS-Z.MPQ'}


def run(*args):
    return subprocess.run(['rtk', *args], check=True, capture_output=True, text=True).stdout


def sha(path):
    digest = hashlib.sha256()
    with pathlib.Path(path).open('rb') as f:
        while data := f.read(1024 * 1024):
            digest.update(data)
    return digest.hexdigest()


def load_manifest():
    return json.loads((ROOT / 'install-manifest.json').read_text())


def save(manifest):
    (ROOT / 'install-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


def prepare():
    storm = Storm(DLL_DEFAULT)
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup = pathlib.Path(r'C:\Users\Zach\.codex\workspace-backups\EsteriaWoW') / (stamp + '-ascension-customization')
    backup.mkdir(parents=True, exist_ok=False)
    packaged = STAGE / 'archives'
    packaged.mkdir(exist_ok=True)
    manifest = {'backup': str(backup), 'files': {}, 'status': 'preparing'}
    save(manifest)
    # Freeze the client archives and actual bind-mounted server tables, verifying each copy.
    for label, source in [*ARCHIVES.items(), *((n, SERVER / (n + '.dbc')) for n in TABLES)]:
        target = backup / (label + source.suffix)
        before = sha(source)
        shutil.copy2(source, target)
        if sha(target) != before or sha(source) != before:
            raise ValueError('Source changed during backup: ' + str(source))
        manifest['files'][label] = {'source': str(source), 'backup': str(target), 'before_sha256': before}
        save(manifest)
        print('Backed up and hash-verified:', label, flush=True)

    sections = RawWdbc((STAGE / 'CharSections.dbc').read_bytes())
    old_sections = RawWdbc((ROOT / 'client-before/CharSections.dbc').read_bytes())
    refs = set()
    for record in sections.records[old_sections.count:]:
        values = struct.unpack('<10I', record)
        if any(values[f] > 255 for f in (8, 9)) or values[7] & 4:
            raise ValueError('Invalid appended appearance byte or DK row')
        for field in (4, 5, 6):
            if values[field]:
                refs.add(sections.strings[values[field]:].split(b'\0', 1)[0].decode('ascii'))
    assets = {str(p.relative_to(STAGE / 'assets')).replace('/', '\\'): p
              for p in (STAGE / 'assets').rglob('*.blp')}
    used_assets = {k: p for k, p in assets.items() if k in refs}
    client = ClientFiles(str(CLIENT / 'Data'), 'enUS')
    for ref in refs:
        if ref not in used_assets:
            client.find(ref)
    for ref in used_assets:
        try:
            client.find(ref)
        except FileNotFoundError:
            continue
        raise ValueError('New asset path already exists: ' + ref)
    client.close()
    entries = {k: p.read_bytes() for k, p in used_assets.items()}
    entries.update({'DBFilesClient\\' + n + '.dbc': (STAGE / (n + '.dbc')).read_bytes() for n in TABLES})
    manifest['assets_installed'] = len(used_assets)
    manifest['assets_bytes'] = sum(p.stat().st_size for p in used_assets.values())
    manifest['referenced_textures'] = len(refs)
    for label in ARCHIVES:
        original = pathlib.Path(manifest['files'][label]['backup'])
        target = packaged / (label + '.MPQ')
        old = storm.open_archive(original)
        try:
            for n in TABLES:
                if storm.read(old, 'DBFilesClient\\' + n + '.dbc') != (ROOT / 'client-before' / (n + '.dbc')).read_bytes():
                    raise ValueError('Client snapshot no longer matches the merge input')
        finally:
            storm.dll.SFileCloseArchive(old)
        shutil.copy2(original, target)
        storm.replace_archive_entries(target, entries)
        if target.stat().st_size >= 2**32:
            raise ValueError('MPQ exceeded the classic client archive limit')
        old, new = storm.open_archive(original), storm.open_archive(target)
        preserved = 0
        try:
            for name, *_ in storm.list_files(old):
                if name.lower() in ('(listfile)', '(attributes)'):
                    continue
                if name.lower() in {('dbfilesclient\\' + n + '.dbc').lower() for n in TABLES}:
                    continue
                if storm.read(old, name) != storm.read(new, name):
                    raise ValueError('Existing archive entry changed: ' + name)
                preserved += 1
            for name, data in entries.items():
                if storm.read(new, name) != data:
                    raise ValueError('Archive round-trip failed: ' + name)
        finally:
            storm.dll.SFileCloseArchive(old)
            storm.dll.SFileCloseArchive(new)
        manifest['files'][label].update(staged=str(target), after_sha256=sha(target),
                                        preserved_entries=preserved, bytes=target.stat().st_size)
        save(manifest)
        print('Verified unchanged existing entries and new payloads:', label, preserved, flush=True)
    for n in TABLES:
        frozen = pathlib.Path(manifest['files'][n]['backup'])
        if frozen.read_bytes() != (ROOT / 'server-before' / (n + '.dbc')).read_bytes():
            raise ValueError('Server snapshot no longer matches the merge input')
        before, after = RawWdbc(frozen.read_bytes()), RawWdbc((STAGE / (n + '.dbc')).read_bytes())
        if after.records[:before.count] != before.records or not after.strings.startswith(before.strings):
            raise ValueError('An existing server DBC row changed')
        added_ids = [int.from_bytes(r[:4], 'little') for r in after.records[before.count:]]
        old_ids = {int.from_bytes(r[:4], 'little') for r in before.records}
        if len(set(added_ids)) != len(added_ids) or set(added_ids) & old_ids:
            raise ValueError('Appended DBC IDs collide')
        manifest['files'][n].update(staged=str(STAGE / (n + '.dbc')), after_sha256=sha(STAGE / (n + '.dbc')),
                                   preserved_rows=before.count, added_rows=after.count-before.count)
    manifest['status'] = 'verified'
    save(manifest)
    print('Ready to install:', json.dumps({k: v for k, v in manifest.items() if k != 'files'}), flush=True)


def install():
    manifest = load_manifest()
    if manifest['status'] != 'verified':
        raise ValueError('Packaging and verification must finish before installation')
    if 'wow.exe' in run('tasklist', '/FI', 'IMAGENAME eq Wow.exe', '/FO', 'CSV').lower():
        raise ValueError('Close WoW before installing')
    for item in manifest['files'].values():
        if sha(item['source']) != item['before_sha256'] or sha(item['staged']) != item['after_sha256']:
            raise ValueError('Source or staged file changed since verification')
    running = run('docker', 'inspect', 'ac-worldserver', '--format', '{{.State.Running}}').strip() == 'true'
    manifest['server_was_running'] = running
    save(manifest)
    temps = {}
    for label in ARCHIVES:
        item = manifest['files'][label]
        temp = pathlib.Path(item['source']).with_suffix('.ascension-next.MPQ')
        if temp.exists():
            raise ValueError('Install temporary file already exists: ' + str(temp))
        shutil.copy2(item['staged'], temp)
        if sha(temp) != item['after_sha256']:
            raise ValueError('Client install copy failed')
        temps[label] = temp
    if running:
        run('docker', 'stop', '-t', '60', 'ac-worldserver')
    try:
        for n in TABLES:
            # Preserve the inode referenced by the server's individual read-only bind mounts.
            shutil.copyfile(manifest['files'][n]['staged'], manifest['files'][n]['source'])
        for label, temp in temps.items():
            os.replace(temp, manifest['files'][label]['source'])
        for item in manifest['files'].values():
            if sha(item['source']) != item['after_sha256']:
                raise ValueError('Installed file hash mismatch')
        if running:
            run('docker', 'start', 'ac-worldserver')
        for n in TABLES:
            observed = ROOT / ('live-' + n + '.dbc')
            run('docker', 'cp', 'ac-worldserver:/azerothcore/env/dist/data/dbc/' + n + '.dbc', str(observed))
            if sha(observed) != manifest['files'][n]['after_sha256']:
                raise ValueError('Container still sees an old bound DBC')
    except Exception:
        run('docker', 'stop', '-t', '60', 'ac-worldserver')
        for n in TABLES:
            shutil.copyfile(manifest['files'][n]['backup'], manifest['files'][n]['source'])
        for label in ARCHIVES:
            target = pathlib.Path(manifest['files'][label]['source'])
            restore = target.with_suffix('.ascension-restore.MPQ')
            shutil.copy2(manifest['files'][label]['backup'], restore)
            os.replace(restore, target)
        if running:
            run('docker', 'start', 'ac-worldserver')
        raise
    manifest['status'] = 'installed'
    save(manifest)
    shutil.copy2(ROOT / 'install-manifest.json', pathlib.Path(manifest['backup']) / 'install-manifest.json')
    print('Installed and hash-verified. Backup:', manifest['backup'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    install() if args.install else prepare()
