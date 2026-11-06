"""Build worldserver with mod-esteria-housing in the isolated housing-build container (a snapshot of coa-lead, so the
shared CoA build tree is never touched), then wrap it in an image. Same steps as mod-classless-wildcard's
verify_build.py + package_runtime.py.

    python build.py                    # build only
    python build.py esteria-housing:1  # build, then package the image
"""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

os.environ["MSYS_NO_PATHCONV"] = "1"
root = Path(__file__).resolve().parents[3]
out = Path("G:/housing-build")
out.mkdir(exist_ok=True)
container = "housing-build"
for source, target in [("src/.", "/azerothcore/src/"),
                       ("modules/mod-esteria-housing/.", "/azerothcore/modules/mod-esteria-housing/"),
                       ("modules/mod-esteria-toolchest/.", "/azerothcore/modules/mod-esteria-toolchest/")]:
    subprocess.run(["docker", "exec", container, "mkdir", "-p", target], check=True)
    # str + "/." on purpose: Path would drop the trailing "." and docker cp would nest the folder inside the target
    subprocess.run(["docker", "cp", str(root) + "/" + source, container + ":" + target], check=True)
command = ["docker", "exec", container, "sh", "-c",
           "cd /azerothcore/build && cmake . && ninja -j12 -k0 worldserver && ninja install"]
with (out / "server-build.log").open("w", encoding="utf-8") as log:
    result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
print("Server build exit", result.returncode)
print("\n".join((out / "server-build.log").read_text(encoding="utf-8", errors="replace").splitlines()[-15:]))
if result.returncode or len(sys.argv) < 2:
    raise SystemExit(result.returncode)

tag = sys.argv[1]
runtime = out / ("runtime-" + tag.split(":")[-1])
runtime.mkdir(exist_ok=False)
binary = "/azerothcore/env/dist/bin/worldserver"
subprocess.run(["docker", "cp", container + ":" + binary, str(runtime / "worldserver")], check=True)
subprocess.run(["docker", "cp", container + ":/azerothcore/env/dist/lib/liblua52.so", str(runtime / "liblua52.so")], check=True)
with (runtime / "worldserver").open("rb") as file:
    digest = hashlib.file_digest(file, "sha256").hexdigest()
assert digest == subprocess.check_output(["docker", "exec", container, "sha256sum", binary], text=True).split()[0]
assert b"npc_esteria_housing_steward" in (runtime / "worldserver").read_bytes(), "module not linked"
base = subprocess.check_output(["docker", "inspect", "-f", "{{.Config.Image}}", "ac-worldserver"], text=True).strip()
(runtime / "Dockerfile").write_text(f"FROM {base}\n"
    "COPY --chown=acore:acore --chmod=755 worldserver /azerothcore/env/dist/bin/worldserver\n"
    "COPY --chown=acore:acore liblua52.so /azerothcore/env/dist/lib/liblua52.so\n", encoding="utf-8", newline="\n")
result = subprocess.run(["docker", "build", "--no-cache", "-t", tag, str(runtime)], capture_output=True, text=True)
print("Runtime package exit", result.returncode, "binary SHA256", digest)
if result.returncode:
    print(result.stdout[-2000:], result.stderr[-2000:])
raise SystemExit(result.returncode)
