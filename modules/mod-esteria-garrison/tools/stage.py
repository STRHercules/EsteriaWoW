"""Garrison on the housing stage realm (housing_dev_* clones, worldserver 8099, authserver 3725). Never writes acore_*.

    python stage.py apply              # garrison characters + world SQL on the clones (after housing's stage.py clone/apply)
    python stage.py start <image>      # housing stage start, with EsteriaGarrison.Enable = 1
    python stage.py check              # container state and the garrison/error lines of the worldserver log
    python stage.py stop
"""
import re
import subprocess
import sys
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE.parent / "mod-esteria-housing" / "tools"))
import stage as housing  # noqa: E402


def apply():
    housing.run_file.__globals__["MODULE"] = MODULE  # run_file prints paths relative to the module it serves
    housing.run_file(housing.CLONE["acore_characters"], MODULE / "sql/characters/garrison_characters.sql")
    housing.run_file(housing.CLONE["acore_world"], MODULE / "sql/world/garrison_world.sql")
    housing.run_file(housing.CLONE["acore_world"], MODULE / "sql/world/garrison_dbc_world.sql")
    housing.run_file(housing.CLONE["acore_world"], MODULE / "sql/world/garrison_worldmap_world.sql")


def prepare():
    housing_prepare()
    conf = (MODULE / "conf/esteria_garrison.conf.dist").read_text(encoding="utf-8")
    (housing.OUT / "stage/etc/modules/esteria_garrison.conf").write_text(
        housing.set_option(conf, "EsteriaGarrison.Enable", "1"), encoding="utf-8", newline="\n")


housing_prepare = housing.prepare
housing.prepare = prepare


def check():
    for name in (housing.WORLD, housing.AUTH):
        state = subprocess.run(["docker", "inspect", "-f", "{{.State.Status}} exit {{.State.ExitCode}}", name],
                               capture_output=True, text=True)
        print(name, state.stdout.strip() or state.stderr.strip())
    logs = subprocess.run(["docker", "logs", housing.WORLD], capture_output=True, text=True, encoding="utf-8", errors="replace")
    text = (logs.stdout + logs.stderr).replace(housing.password(), "[redacted]")
    (housing.OUT.parent / "garrison-build" / "stage-startup.log").write_text(text, encoding="utf-8")
    wanted = [l for l in text.splitlines() if re.search(r"garrison|error|assert|world initialized|ready\.\.\.", l, re.I)]
    print("\n".join(wanted[-40:] if wanted else text.splitlines()[-15:]))


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    {"apply": apply, "start": lambda: housing.start(sys.argv[2]), "check": check, "stop": housing.stop}.get(
        action, lambda: print(__doc__))()
