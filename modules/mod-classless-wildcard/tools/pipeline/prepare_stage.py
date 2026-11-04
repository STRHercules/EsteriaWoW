from pathlib import Path
import re
import shutil

root = Path(__file__).resolve().parents[4]
out = Path('G:/coa-build/codex-batch7-20261103/stage')
shutil.copytree(root / 'env/dist/etc', out / 'etc', dirs_exist_ok=True)
(out / 'logs').mkdir(exist_ok=True)

def set_option(text, name, value):
    line = name + ' = ' + value
    pattern = r'^' + re.escape(name) + r'\s*=.*$'
    return re.sub(pattern, lambda _match: line, text, flags=re.M) if re.search(pattern, text, re.M) else text + '\n' + line + '\n'

p = out / 'etc/worldserver.conf'
s = p.read_text(encoding='utf-8')
for key, name in [('LoginDatabaseInfo', 'coa_b7_auth'), ('WorldDatabaseInfo', 'coa_b7_world'),
                  ('CharacterDatabaseInfo', 'coa_b7_characters')]:
    pattern = r'^' + key + r'\s*=\s*"([^"\n]+)"'
    match = re.search(pattern, s, re.M)
    assert match, key + ' missing'
    values = match.group(1).split(';')
    values[-1] = name
    s = set_option(s, key, '"' + ';'.join(values) + '"')
for key, value in [('WorldServerPort', '8095'), ('Updates.EnableDatabases', '0'),
                    ('Console.Enable', '0'), ('Ra.Enable', '0'), ('SOAP.Enabled', '0')]:
    s = set_option(s, key, value)
p.write_text(s, encoding='utf-8', newline='\n')
for p in (out / 'etc/modules').glob('*.conf'):
    s = p.read_text(encoding='utf-8', errors='replace')
    for name in ('AiPlayerbot.Enabled', 'AiPlayerbot.RandomBotAutologin'):
        s = set_option(s, name, '0')
    p.write_text(s, encoding='utf-8', newline='\n')
print('Prepared isolated configuration and logs; all three databases point to coa_b7_* schemas.')
