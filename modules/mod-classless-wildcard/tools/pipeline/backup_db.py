from pathlib import Path
import gzip
import subprocess

out = Path('G:/coa-build/codex-batch7-20261103')
for database in ('acore_world', 'acore_characters', 'acore_auth', 'acore_playerbots'):
    path = out / (database + '.sql.gz')
    if path.exists():
        print('Backup already saved:', path.name, path.stat().st_size)
        continue
    part = path.with_suffix(path.suffix + '.part')
    command = ['docker', 'exec', 'ac-database', 'sh', '-c',
               'mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" --single-transaction --quick '
               '--set-gtid-purged=OFF --routines --events --triggers ' + database]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    with gzip.open(part, 'wb', compresslevel=1) as backup:
        while chunk := process.stdout.read(1024 * 1024):
            backup.write(chunk)
    error = process.stderr.read().decode('utf-8', errors='replace')
    if process.wait():
        raise SystemExit('Backup failed for ' + database + ': ' + error)
    with gzip.open(part, 'rb') as backup:
        last = b''
        while chunk := backup.read(1024 * 1024):
            last = chunk
        assert b'Dump completed' in last, 'missing complete dump footer'
    part.rename(path)
    print('Saved and verified:', path.name, path.stat().st_size, flush=True)
