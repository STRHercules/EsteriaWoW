"""Run the module's SQL, and every SQL statement its C++ issues, against a real MySQL.

    python tests/test_sql_in_mysql.py

Starts a throwaway container from the LOCAL image mysql:8.4 (no pull, no volumes, no published ports, removed at the
end), builds fresh world and characters schemas from the module's own SQL, applies every file twice (they must be safe
to re-run), then executes each statement found in src/*.cpp with its {} placeholders replaced by 0, each inside its own
rolled-back transaction. That catches wrong table and column names, bad syntax and missing migrations, which an
uncompiled module cannot otherwise show. Skips (exit 0) when docker or the image is not available. It never touches any
other container.
"""
import glob
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(ROOT))
SRC = os.path.join(ROOT, 'src')
IMAGE = 'mysql:8.4'
NAME = 'bm-sqlcheck-%d' % os.getpid()
PASSWORD = 'bmtest'

MACROS = {  # macros that stand for column lists inside the C++ SQL strings
    'BM_IND_COLS': 'iv_hp, iv_atk, iv_def, iv_spa, iv_spd, iv_spe, ev_hp, ev_atk, ev_def, ev_spa, ev_spd, ev_spe, '
                   'nature, ability_slot, ot_guid',
}


def docker(*args, stdin=None, check=True):
    return subprocess.run(['docker', *args], stdin=stdin, capture_output=True, text=True, encoding='utf-8',
                          errors='replace', check=check)


def mysql(database, sql_text=None, path=None, force=False):
    cmd = ['exec', '-i', NAME, 'mysql', '-uroot', '-p' + PASSWORD, '--default-character-set=utf8mb4']
    if force:
        cmd.append('--force')
    if database:
        cmd += ['-D', database]
    if path:
        with open(path, 'rb') as f:
            r = subprocess.run(['docker', *cmd], stdin=f, capture_output=True)
    else:
        r = subprocess.run(['docker', *cmd], input=sql_text.encode('utf-8'), capture_output=True)
    return r.returncode, r.stdout.decode('utf-8', 'replace'), r.stderr.decode('utf-8', 'replace')


def split_args(text):
    args, depth, cur, i, n = [], 0, [], 0, len(text)
    while i < n:
        c = text[i]
        if c in '"\'':
            j = i + 1
            while j < n and text[j] != c:
                j += 2 if text[j] == '\\' else 1
            cur.append(text[i:j + 1])
            i = j + 1
            continue
        if c in '([{':
            depth += 1
        elif c in ')]}':
            depth -= 1
        if c == ',' and depth == 0:
            args.append(''.join(cur).strip())
            cur = []
        else:
            cur.append(c)
        i += 1
    if ''.join(cur).strip():
        args.append(''.join(cur).strip())
    return args


def literal(arg):
    rest = re.sub(r'"(?:[^"\\]|\\.)*"|\w+', '', arg)
    if rest.strip():
        return None
    out = []
    for lit, name in re.findall(r'"((?:[^"\\]|\\.)*)"|(\w+)', arg):
        if name:
            if name not in MACROS:
                return None
            out.append(MACROS[name])
        else:
            out.append(lit.replace('\\"', '"').replace("\\'", "'"))
    return ''.join(out)


def statements_in_cpp():
    """[(database, sql)] for every literal SQL statement the C++ issues."""
    found = []
    call = re.compile(r'(WorldDatabase|CharacterDatabase|trans)\s*(?:\.|->)\s*(DirectExecute|Execute|Query|Append)\s*\(')
    for path in sorted(glob.glob(os.path.join(SRC, '*.cpp'))):
        text = open(path, encoding='utf-8').read()
        for m in call.finditer(text):
            depth, i = 1, m.end()
            while i < len(text) and depth:
                c = text[i]
                if c == '"':
                    i += 1
                    while text[i] != '"':
                        i += 2 if text[i] == '\\' else 1
                elif c == '(':
                    depth += 1
                elif c == ')':
                    depth -= 1
                i += 1
            args = split_args(text[m.end():i - 1])
            sql = literal(args[0]) if args else None
            if not sql or not re.match(r'\s*(SELECT|INSERT|UPDATE|DELETE|REPLACE)\b', sql, re.I):
                continue
            db = 'acore_world' if m.group(1) == 'WorldDatabase' else 'acore_characters'
            found.append((db, sql, os.path.basename(path), text.count('\n', 0, m.start()) + 1))
    return found


def wait_ready():
    for _ in range(90):
        logs = docker('logs', NAME, check=False)
        if re.search(r'port: 3306\s+MySQL Community Server', logs.stdout + logs.stderr):
            code, _, _ = mysql(None, 'SELECT 1;')
            if code == 0:
                return True
        time.sleep(2)
    return False


def main():
    if subprocess.run(['docker', 'image', 'inspect', IMAGE], capture_output=True).returncode != 0:
        print('SKIP: docker or the local image %s is not available' % IMAGE)
        return 0
    docker('run', '-d', '--rm', '--pull', 'never', '--name', NAME, '-e', 'MYSQL_ROOT_PASSWORD=' + PASSWORD, IMAGE)
    failures = []
    try:
        assert wait_ready(), 'mysql did not start'
        for db in ('acore_world', 'acore_characters'):
            mysql(None, 'CREATE DATABASE %s CHARACTER SET utf8mb4;' % db)

        # the one core table the module's SQL writes to
        base = os.path.join(REPO, 'data', 'sql', 'base', 'db_world', 'item_template.sql')
        code, _, err = mysql('acore_world', path=base)
        assert code == 0, err
        # the sidecar reads the core `characters` table by name; a two-column stand-in is enough to check that query
        mysql('acore_characters', 'CREATE TABLE characters (guid int unsigned NOT NULL PRIMARY KEY, '
                                  'name varchar(12) NOT NULL);')

        files = [('acore_world', p) for p in sorted(glob.glob(os.path.join(ROOT, 'data/sql/db-world/base/*.sql')))] + \
                [('acore_characters', p) for p in sorted(glob.glob(os.path.join(ROOT, 'data/sql/db-characters/base/*.sql')))]
        for round_ in (1, 2):   # the second round proves every file is safe to re-run
            for db, path in files:
                code, _, err = mysql(db, path=path)
                if code != 0:
                    failures.append('round %d %s: %s' % (round_, os.path.basename(path), err.strip()[:300]))

        # row counts that prove the big files really loaded and did not duplicate on the re-run
        def one(db, sql):
            return mysql(db, sql + ';')[1].split()[-1] if mysql(db, sql + ';')[1].split() else '?'
        checks = {
            ('acore_world', 'SELECT COUNT(*) FROM battlemon_species_ev'): 1025,
            ('acore_world', 'SELECT COUNT(*) FROM item_template WHERE entry BETWEEN 960000 AND 963999'): 2050,
            ('acore_world', 'SELECT COUNT(*) FROM battlemon_spawn_zone'): 59,
        }
        for (db, sql), want in checks.items():
            got = one(db, sql)
            if got != str(want):
                failures.append('%s -> %s, expected %s' % (sql, got, want))
        moves = one('acore_world', 'SELECT COUNT(DISTINCT id) = COUNT(*) FROM battlemon_species_moves')
        if moves != '1':
            failures.append('battlemon_species_moves ids are not unique')

        # every statement the C++ issues, against the real schema
        found = statements_in_cpp()
        assert len(found) > 100, len(found)
        by_db = {'acore_world': [], 'acore_characters': []}
        for db, sql, fname, line in found:
            if 'CASE id' in sql:   # assembled at runtime from pieces; checked by hand below
                continue
            by_db[db].append((re.sub(r'\{[^{}]*\}', '0', sql), fname, line))
        for db, items in by_db.items():
            script, lines = [], {}
            for sql, fname, line in items:
                script.append('START TRANSACTION;')
                script.append(sql.strip().rstrip(';') + ';')
                lines[len(script)] = (fname, line, sql)
                script.append('ROLLBACK;')
            code, out, err = mysql(db, '\n'.join(script) + '\n', force=True)
            for m in re.finditer(r'ERROR (\d+) \((\w+)\) at line (\d+): (.*)', err):
                fname, line, sql = lines.get(int(m.group(3)), ('?', 0, ''))
                failures.append('%s:%d  %s  [%s]' % (fname, line, m.group(4).strip(), sql.strip()[:90]))

        # the trade swap is built from pieces at runtime; run its real shape
        swap = ("START TRANSACTION; UPDATE battlemon_owned SET guid = CASE id WHEN 1 THEN 20 WHEN 2 THEN 10 END "
                "WHERE id IN (1,2) AND (SELECT c FROM (SELECT COUNT(*) AS c FROM battlemon_owned WHERE "
                "(id = 1 AND guid = 10) OR (id = 2 AND guid = 20)) AS t) = 2; ROLLBACK;")
        code, _, err = mysql('acore_characters', swap)
        if code != 0:
            failures.append('trade swap: ' + err.strip()[:200])
        print('applied %d module SQL files twice; ran %d C++ statements' % (len(files), len(found)))
    finally:
        docker('rm', '-f', NAME, check=False)
    for f in failures:
        print('FAIL', f)
    if failures:
        return 1
    print('ok')
    return 0


if __name__ == '__main__':
    sys.exit(main())
