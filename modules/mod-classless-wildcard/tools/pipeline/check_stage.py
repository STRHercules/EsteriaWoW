from pathlib import Path
import json
import re
import subprocess

out = Path('G:/coa-build/codex-batch7-20261103')
info = json.loads(subprocess.check_output(['docker', 'inspect', 'ac-database']))[0]
password = dict(value.split('=', 1) for value in info['Config']['Env'])['MYSQL_ROOT_PASSWORD']
state = json.loads(subprocess.check_output(['docker', 'inspect', 'coa-codex-stage']))[0]
result = subprocess.run(['docker', 'logs', 'coa-codex-stage'], capture_output=True, text=True,
                        encoding='utf-8', errors='replace')
text = result.stdout + result.stderr
text = text.replace(password, '[redacted]')
(out / 'isolated-startup.log').write_text(text, encoding='utf-8')
print('Isolated worldserver', state['State']['Status'], 'exit', state['State']['ExitCode'])
lines = text.splitlines()
interesting = [line for line in lines if any(token in line.lower() for token in
    ('assertion', 'validate()', 'not assigned', 'failed to', 'error:', 'unknown column',
     'library built', 'coa ability', 'world initialized', 'ready...', 'cannot connect', 'could not connect'))]
print('\n'.join(interesting[-35:]) if interesting else '\n'.join(lines[-10:]))
ready = bool(re.search(r'World Initialized|ready\.\.\.', text, re.I))
print('Ready marker present:', ready)
if state['State']['Status'] != 'running':
    print('\n'.join(lines[-15:]))
