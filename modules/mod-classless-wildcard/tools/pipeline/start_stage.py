from pathlib import Path
import json
import subprocess
import sys

out = Path('G:/coa-build/codex-batch7-20261103/stage')
info = json.loads(subprocess.check_output(['docker', 'inspect', 'ac-database']))[0]
environment = dict(value.split('=', 1) for value in info['Config']['Env'])
password = environment['MYSQL_ROOT_PASSWORD']
assert ';' not in password and '\n' not in password
command = ['docker', 'run', '-d', '--name', 'coa-codex-stage', '--network', 'container:ac-database',
           '--volumes-from', 'ac-worldserver:ro',
           '-v', str(out / 'etc') + ':/azerothcore/env/dist/etc:rw',
           '-v', str(out / 'logs') + ':/azerothcore/env/dist/logs:rw',
           '--entrypoint', '/azerothcore/env/dist/bin/worldserver',
           '-e', 'AC_DATA_DIR=/azerothcore/env/dist/data', '-e', 'AC_UPDATES_ENABLE_DATABASES=0']
for key, database in [('AC_LOGIN_DATABASE_INFO', 'coa_b7_auth'), ('AC_WORLD_DATABASE_INFO', 'coa_b7_world'),
                       ('AC_CHARACTER_DATABASE_INFO', 'coa_b7_characters'),
                       ('AC_PLAYERBOTS_DATABASE_INFO', 'coa_b7_playerbots')]:
    command += ['-e', key + '=127.0.0.1;3306;root;' + password + ';' + database]
image = sys.argv[1]  # e.g. esteria-coa:20261103m
command += [image, '-c', '/azerothcore/env/dist/etc/worldserver.conf']
result = subprocess.run(command, capture_output=True, text=True)
if result.returncode:
    raise SystemExit('Isolated startup failed: ' + result.stderr)
print('Started isolated worldserver:', result.stdout.strip(), 'using four cloned databases.')
