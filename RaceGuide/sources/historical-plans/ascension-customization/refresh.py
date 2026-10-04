"""Update the already-verified package after tightening the donor palette filter."""
import hashlib
import json
import pathlib
import struct
import sys

sys.path.insert(0, 'tools')
from cars_mount_pack import DLL_DEFAULT, Storm
from playable_race_pack import RawWdbc

root = pathlib.Path(r'C:\Users\Zach\.codex\tmp\ascension-customization')
manifest = json.loads((root / 'install-manifest.json').read_text())
if manifest['status'] != 'verified':
    raise ValueError('Only a previously verified package may be refreshed')


def sha(path):
    digest = hashlib.sha256()
    with pathlib.Path(path).open('rb') as f:
        while data := f.read(1024 * 1024):
            digest.update(data)
    return digest.hexdigest()


for item in manifest['files'].values():
    if sha(item['source']) != item['before_sha256']:
        raise ValueError('Live input changed since packaging')
for label in ('root', 'locale'):
    if sha(manifest['files'][label]['staged']) != manifest['files'][label]['after_sha256']:
        raise ValueError('Verified archive changed before refresh')
entries = {}
for name in ('CharSections', 'BarberShopStyle'):
    path = root / 'staged' / (name + '.dbc')
    before = RawWdbc((root / 'server-before' / (name + '.dbc')).read_bytes())
    after = RawWdbc(path.read_bytes())
    if before.records != after.records[:before.count] or not after.strings.startswith(before.strings):
        raise ValueError('An original row or string changed')
    entries['DBFilesClient\\' + name + '.dbc'] = path.read_bytes()
    manifest['files'][name].update(after_sha256=sha(path), added_rows=after.count-before.count)
    if name == 'CharSections':
        refs = set()
        for record in after.records[before.count:]:
            row = struct.unpack('<10I', record)
            for field in (4, 5, 6):
                if row[field]:
                    refs.add(after.strings[row[field]:].split(b'\0', 1)[0])
        manifest['referenced_textures'] = len(refs)
storm = Storm(DLL_DEFAULT)
for label in ('root', 'locale'):
    path = pathlib.Path(manifest['files'][label]['staged'])
    storm.replace_archive_entries(path, entries)
    handle = storm.open_archive(path)
    try:
        for name, data in entries.items():
            if storm.read(handle, name) != data:
                raise ValueError('Refreshed DBC did not round-trip')
    finally:
        storm.dll.SFileCloseArchive(handle)
    manifest['files'][label].update(after_sha256=sha(path), bytes=path.stat().st_size)
(root / 'install-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('Verified archive DBCs refreshed; originals remain preserved')
