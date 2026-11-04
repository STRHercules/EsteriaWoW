from pathlib import Path
import hashlib
import subprocess
import sys

# a fresh build context per tag: Docker Desktop has served a stale copy of a worldserver overwritten in place
out = Path('G:/coa-build/codex-batch7-20261103') / ('runtime-' + sys.argv[1].split(':')[-1])
out.mkdir(exist_ok=False)
# the installed copy (verify_build.py installs): its runpath is env/dist/lib, the build tree's is not
source = '/azerothcore/env/dist/bin/worldserver'
subprocess.run(['docker', 'exec', 'coa-lead', 'test', '-x', source], check=True)
subprocess.run(['docker', 'cp', 'coa-lead:' + source, str(out / 'worldserver')], check=True)
with (out / 'worldserver').open('rb') as file:
    digest = hashlib.file_digest(file, 'sha256').hexdigest()
expected = subprocess.check_output(['docker', 'exec', 'coa-lead', 'sha256sum', source], text=True).split()[0]
assert digest == expected
data = (out / 'worldserver').read_bytes()
assert b'cw_coa_direct_modifiers' in data and b'cw_coa_charge_learning' in data, 'final source not linked'
subprocess.run(['docker', 'cp', 'coa-lead:/azerothcore/env/dist/lib/liblua52.so', str(out / 'liblua52.so')], check=True)
(out / 'Dockerfile').write_text('FROM esteria-coa:20261103d\n'
    'COPY --chown=acore:acore --chmod=755 worldserver /azerothcore/env/dist/bin/worldserver\n'
    'COPY --chown=acore:acore liblua52.so /azerothcore/env/dist/lib/liblua52.so\n',
    encoding='utf-8', newline='\n')
(out / 'worldserver.sha256').write_text(digest + '\n')
with (out.parent / 'runtime-image.log').open('w', encoding='utf-8') as log:
    result = subprocess.run(['docker', 'build', '--no-cache', '-t', sys.argv[1], str(out)],  # new tag, e.g. esteria-coa:20261103m
                            stdout=log, stderr=subprocess.STDOUT)
print('Runtime package exit', result.returncode, 'binary SHA256', digest)
if result.returncode:
    print('\n'.join((out.parent / 'runtime-image.log').read_text(errors='replace').splitlines()[-12:]))
raise SystemExit(result.returncode)
