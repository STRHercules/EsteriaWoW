import json
import pathlib
import time
import urllib.request
import zipfile

root = pathlib.Path(r'C:\Users\Zach\.codex\tmp\ascension-customization')
commit = json.loads((root / 'upstream-commit.json').read_text())['sha']
archive = root / 'upstream.zip'
if not archive.exists():
    temp = root / 'upstream.zip.part'
    last = time.monotonic()
    with urllib.request.urlopen('https://codeload.github.com/Ijostrom/Ascension_Character_Customization/zip/' + commit,
                                timeout=120) as source, temp.open('wb') as target:
        while data := source.read(1024 * 1024):
            target.write(data)
            if time.monotonic() - last > 15:
                print('Downloaded', round(target.tell() / 1e6), 'MB', flush=True)
                last = time.monotonic()
    temp.replace(archive)
with zipfile.ZipFile(archive) as donor:
    print('ZIP ready:', archive.stat().st_size, 'bytes;', len(donor.infolist()), 'entries', flush=True)
