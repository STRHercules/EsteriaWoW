"""Housing stage realm: housing_dev_* clones of acore_*, the housing SQL, and a separate worldserver + authserver.
Never writes to acore_* (dumps read them with --single-transaction). Patterned on mod-classless-wildcard/tools/pipeline.

    python stage.py dump              # mysqldump acore_{world,characters,auth,playerbots} -> G:/housing-build/backup
    python stage.py clone             # (re)create housing_dev_* from those dumps; refuses if they exist unless --replace
    python stage.py apply             # housing SQL + stage realmlist row on the clones
    python stage.py rollback          # housing rollback SQL on the clones
    python stage.py test-migration    # apply, check, rollback, check, apply again (needs clones)
    python stage.py start <image>     # stage worldserver (port 8099) + authserver (port 3725)
    python stage.py check             # container state and the housing lines of the worldserver log
    python stage.py stop
"""
import gzip
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

os.environ["MSYS_NO_PATHCONV"] = "1"
MODULE = Path(__file__).resolve().parents[1]
REPO = MODULE.parents[1]
LIVE_ETC = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\env\dist\etc")  # configuration the realm runs with
OUT = Path("G:/housing-build")
SOURCES = ("acore_world", "acore_characters", "acore_auth", "acore_playerbots")
CLONE = {s: s.replace("acore_", "housing_dev_") for s in SOURCES}
WORLD_PORT, AUTH_PORT = 8099, 3725
WORLD, AUTH, NETWORK = "housing-stage", "housing-stage-auth", "esteriawow_ac-network"


def mysql(database="", sql=None, stdin=None, check=True):
    command = ["docker", "exec", "-i", "ac-database", "sh", "-c", 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -N ' + database]
    result = subprocess.run(command, input=sql.encode() if sql is not None else None, stdin=stdin, capture_output=True)
    error = "\n".join(l for l in result.stderr.decode(errors="replace").splitlines() if "Using a password" not in l)
    if check and result.returncode:
        raise SystemExit(f"mysql {database}: {error}")
    return result.stdout.decode(errors="replace")


def password():
    info = json.loads(subprocess.check_output(["docker", "inspect", "ac-database"]))[0]
    value = dict(v.split("=", 1) for v in info["Config"]["Env"])["MYSQL_ROOT_PASSWORD"]
    assert ";" not in value and "\n" not in value
    return value


def databases():
    return set(mysql(sql="SHOW DATABASES;").split())


def dump():
    (OUT / "backup").mkdir(parents=True, exist_ok=True)
    for database in SOURCES:
        path = OUT / "backup" / (database + ".sql.gz")
        part = path.with_suffix(".gz.part")
        command = ["docker", "exec", "ac-database", "sh", "-c", 'mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" --single-transaction '
                   "--quick --set-gtid-purged=OFF --routines --events --triggers " + database]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with gzip.open(part, "wb", compresslevel=1) as backup:
            while chunk := process.stdout.read(1 << 20):
                backup.write(chunk)
        error = process.stderr.read().decode(errors="replace")
        if process.wait():
            raise SystemExit(f"dump {database}: {error}")
        with gzip.open(part, "rb") as backup:
            last = b""
            while chunk := backup.read(1 << 20):
                last = chunk
        assert b"Dump completed" in last, "dump has no completion footer"
        part.replace(path)
        print("dumped", database, path.stat().st_size, flush=True)


def clone(replace):
    existing = databases() & set(CLONE.values())
    if existing and not replace:
        raise SystemExit(f"{sorted(existing)} already exist; pass --replace to drop and re-clone them")
    for source, target in CLONE.items():
        assert target.startswith("housing_dev_")
        mysql(sql=f"DROP DATABASE IF EXISTS `{target}`; CREATE DATABASE `{target}` CHARACTER SET utf8mb4;")
        command = ["docker", "exec", "-i", "ac-database", "sh", "-c", f'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" {target}']
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        with gzip.open(OUT / "backup" / (source + ".sql.gz"), "rb") as data:
            while chunk := data.read(1 << 20):
                process.stdin.write(chunk)
        process.stdin.close()
        error = process.stderr.read().decode(errors="replace")
        if process.wait():
            raise SystemExit(f"import {target}: {error}")
        print("cloned", source, "->", target, flush=True)


def run_file(database, path):
    assert database.startswith("housing_dev_"), database
    with open(path, "rb") as sql:
        mysql(database, stdin=sql)
    print("applied", path.relative_to(MODULE), "to", database, flush=True)


REALM_SQL = (f"UPDATE `realmlist` SET `name` = 'Esteria Housing Dev', `address` = '127.0.0.1', `localAddress` = '127.0.0.1', "
             f"`port` = {WORLD_PORT} WHERE `id` = 1;")


def apply():
    run_file(CLONE["acore_world"], MODULE / "sql/world/housing_world.sql")
    run_file(CLONE["acore_world"], MODULE / "sql/world/housing_commerce_world.sql")
    run_file(CLONE["acore_world"], MODULE / "sql/world/housing_adventure_world.sql")
    run_file(CLONE["acore_world"], MODULE / "sql/world/housing_collections_world.sql")
    run_file(CLONE["acore_world"], MODULE / "sql/world/housing_household_world.sql")
    run_file(CLONE["acore_characters"], MODULE / "sql/characters/housing_characters.sql")
    mysql(CLONE["acore_auth"], REALM_SQL)
    print("realmlist 1 ->", f"127.0.0.1:{WORLD_PORT} in", CLONE["acore_auth"])


def rollback():
    run_file(CLONE["acore_world"], MODULE / "sql/world/housing_world_rollback.sql")
    run_file(CLONE["acore_world"], MODULE / "sql/world/housing_commerce_world_rollback.sql")
    run_file(CLONE["acore_characters"], MODULE / "sql/characters/housing_characters_rollback.sql")


def counts():
    w, c = CLONE["acore_world"], CLONE["acore_characters"]
    sql = (f"SELECT (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{w}' AND table_name LIKE 'housing%'),"
           f" (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{c}' AND table_name LIKE 'housing%'),"
           f" (SELECT COUNT(*) FROM `{w}`.gameobject_template WHERE entry BETWEEN 9500000 AND 9500399),"
           f" (SELECT COUNT(*) FROM `{w}`.gameobjectdisplayinfo_dbc WHERE ID BETWEEN 60000 AND 60399),"
           f" (SELECT COUNT(*) FROM `{w}`.creature_template WHERE entry = 9500100),"
           f" (SELECT COUNT(*) FROM `{w}`.map_dbc WHERE ID = 2783), (SELECT COUNT(*) FROM `{w}`.instance_template WHERE map = 2783);")
    return tuple(int(v) for v in mysql(sql=sql).split())


def test_migration():
    names = "world tables, char tables, GO templates, display rows, steward, map_dbc 2783, instance_template 2783"
    print("columns:", names)
    apply(); after = counts(); print("after apply   ", after)
    rooms = len(__import__("make_slice").ROOM_MODELS)
    assert after[:2] == (4, 7) and after[2:5] == (20 + rooms, 20 + rooms, 1) and after[5:] == (1, 1), after  # decor + room kit
    if mysql(CLONE["acore_world"], "SELECT COUNT(*) FROM housing_decor_catalog WHERE enabled = 1;").strip() != "20":
        raise SystemExit("catalog does not hold 20 enabled rows")
    rollback(); gone = counts(); print("after rollback", gone)
    assert gone == (0,) * 7, gone
    apply(); print("after re-apply", counts())
    print("migration apply + rollback + re-apply: OK")


def set_option(text, name, value):
    line = f"{name} = {value}"
    pattern = r"^" + re.escape(name) + r"\s*=.*$"
    return re.sub(pattern, lambda _m: line, text, flags=re.M) if re.search(pattern, text, re.M) else text + "\n" + line + "\n"


def prepare():
    etc = OUT / "stage/etc"
    if etc.exists():
        shutil.rmtree(etc)
    shutil.copytree(LIVE_ETC, etc)
    (OUT / "stage/logs").mkdir(parents=True, exist_ok=True)
    world = etc / "worldserver.conf"
    s = world.read_text(encoding="utf-8")
    for key, source in (("LoginDatabaseInfo", "acore_auth"), ("WorldDatabaseInfo", "acore_world"),
                        ("CharacterDatabaseInfo", "acore_characters")):
        s = set_option(s, key, f'"ac-database;3306;root;{password()};{CLONE[source]}"')
    for key, value in (("WorldServerPort", str(WORLD_PORT)), ("Updates.EnableDatabases", "0"), ("Console.Enable", "0"),
                       ("Ra.Enable", "0"), ("SOAP.Enabled", "0"), ("RealmID", "1")):
        s = set_option(s, key, value)
    world.write_text(s, encoding="utf-8", newline="\n")
    for conf in (etc / "modules").glob("*.conf"):
        t = conf.read_text(encoding="utf-8", errors="replace")
        if "AiPlayerbot." in t:
            for name in ("AiPlayerbot.Enabled", "AiPlayerbot.RandomBotAutologin"):
                t = set_option(t, name, "0")
            t = set_option(t, "PlayerbotsDatabaseInfo", f'"ac-database;3306;root;{password()};{CLONE["acore_playerbots"]}"')
            conf.write_text(t, encoding="utf-8", newline="\n")
    housing = (MODULE / "conf/esteria_housing.conf.dist").read_text(encoding="utf-8")
    (etc / "modules/esteria_housing.conf").write_text(set_option(housing, "EsteriaHousing.Enable", "1"),
                                                      encoding="utf-8", newline="\n")
    auth = etc / "authserver.conf"
    if auth.exists():
        a = set_option(auth.read_text(encoding="utf-8"), "LoginDatabaseInfo",
                       f'"ac-database;3306;root;{password()};{CLONE["acore_auth"]}"')
        auth.write_text(a, encoding="utf-8", newline="\n")
    print("stage config in", etc, "(contains the DB password; not in any repo)")


def start(image):
    prepare()
    etc, logs = OUT / "stage/etc", OUT / "stage/logs"
    pw = password()
    db = lambda name: "ac-database;3306;root;" + pw + ";" + CLONE[name]
    world = ["docker", "run", "-d", "--name", WORLD, "--network", NETWORK, "-p", f"{WORLD_PORT}:{WORLD_PORT}",
             "--volumes-from", "ac-worldserver:ro", "-v", f"{etc}:/azerothcore/env/dist/etc:rw",
             "-v", f"{logs}:/azerothcore/env/dist/logs:rw", "--entrypoint", "/azerothcore/env/dist/bin/worldserver",
             "-e", "AC_DATA_DIR=/azerothcore/env/dist/data", "-e", "AC_UPDATES_ENABLE_DATABASES=0",
             "-e", "AC_LOGIN_DATABASE_INFO=" + db("acore_auth"), "-e", "AC_WORLD_DATABASE_INFO=" + db("acore_world"),
             "-e", "AC_CHARACTER_DATABASE_INFO=" + db("acore_characters"),
             "-e", "AC_PLAYERBOTS_DATABASE_INFO=" + db("acore_playerbots"),
             image, "-c", "/azerothcore/env/dist/etc/worldserver.conf"]
    auth_image = subprocess.check_output(["docker", "inspect", "-f", "{{.Config.Image}}", "ac-authserver"], text=True).strip()
    auth = ["docker", "run", "-d", "--name", AUTH, "--network", NETWORK, "-p", f"{AUTH_PORT}:3724",
            "-e", "AC_LOGIN_DATABASE_INFO=" + db("acore_auth"), "-e", "AC_UPDATES_ENABLE_DATABASES=0", auth_image]
    for command in (world, auth):
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode:
            raise SystemExit("start failed: " + result.stderr.replace(pw, "[redacted]"))
    print(f"started {WORLD} (127.0.0.1:{WORLD_PORT}) and {AUTH} (127.0.0.1:{AUTH_PORT}) on housing_dev_*")


def check():
    pw = password()
    for name in (WORLD, AUTH):
        state = subprocess.run(["docker", "inspect", "-f", "{{.State.Status}} exit {{.State.ExitCode}}", name],
                               capture_output=True, text=True)
        print(name, state.stdout.strip() or state.stderr.strip())
    logs = subprocess.run(["docker", "logs", WORLD], capture_output=True, text=True, encoding="utf-8", errors="replace")
    text = (logs.stdout + logs.stderr).replace(pw, "[redacted]")
    (OUT / "stage-startup.log").write_text(text, encoding="utf-8")
    lines = text.splitlines()
    wanted = [l for l in lines if re.search(r"housing|error|assert|world initialized|ready\.\.\.", l, re.I)]
    print("\n".join(wanted[-30:] if wanted else lines[-15:]))


def stop():
    for name in (WORLD, AUTH):
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)
    print("removed", WORLD, AUTH)


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    {"dump": dump, "clone": lambda: clone("--replace" in sys.argv), "apply": apply, "rollback": rollback,
     "test-migration": test_migration, "start": lambda: start(sys.argv[2]), "check": check, "stop": stop,
     "prepare": prepare}.get(action, lambda: print(__doc__))()
