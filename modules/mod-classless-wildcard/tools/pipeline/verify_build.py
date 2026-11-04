from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[4]
out = Path('G:/coa-build/codex-batch7-20261103')
for source, target in [('src/.', '/azerothcore/src/'),
                       ('modules/mod-classless-wildcard/.', '/azerothcore/modules/mod-classless-wildcard/')]:
    # str + "/." on purpose: Path would drop the trailing "." and docker cp would nest the folder inside the target
    subprocess.run(['docker', 'cp', str(root) + '/' + source, 'coa-lead:' + target], check=True)
command = ['docker', 'exec', 'coa-lead', 'sh', '-c',
           'cd /azerothcore/build && cmake . && ninja -j12 -k0 worldserver && ninja install']
with (out / 'server-build.log').open('w', encoding='utf-8') as log:
    result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
print('Server build exit', result.returncode)
print('\n'.join((out / 'server-build.log').read_text(encoding='utf-8', errors='replace').splitlines()[-15:]))
raise SystemExit(result.returncode)
