from pathlib import Path
import gzip
import subprocess

out = Path('G:/coa-build/codex-batch7-20261103')
command = ['docker', 'exec', '-i', 'ac-database', 'sh', '-c', 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD"']
for source, target in (('acore_world', 'coa_b7_world'), ('acore_characters', 'coa_b7_characters'),
                       ('acore_auth', 'coa_b7_auth'), ('acore_playerbots', 'coa_b7_playerbots')):
    check = subprocess.run(command, input=('CREATE DATABASE IF NOT EXISTS `%s` CHARACTER SET utf8mb4;\n' % target).encode(),
                           capture_output=True)
    if check.returncode:
        raise SystemExit('Scratch database creation failed: ' + check.stderr.decode())
    process = subprocess.Popen(command[:-1] + [command[-1] + " " + target], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    with gzip.open(out / (source + '.sql.gz'), 'rb') as dump:
        try:
            while chunk := dump.read(1024 * 1024):
                process.stdin.write(chunk)
        except BrokenPipeError:
            raise SystemExit(process.stderr.read().decode())
    process.stdin.close()
    error = process.stderr.read().decode('utf-8', errors='replace')
    if process.wait():
        raise SystemExit('Scratch import failed for ' + target + ': ' + error)
    print('Restored isolated database', target, flush=True)
