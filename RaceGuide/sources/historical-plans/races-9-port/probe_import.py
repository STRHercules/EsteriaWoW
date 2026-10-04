import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
print("script REPO:", REPO)
print("inserting:", str(REPO / "tools"))
sys.path.insert(0, str(REPO / "tools"))
print("sys.path[0:3]:", sys.path[:3])
try:
    import cars_mount_pack
    print("ok:", cars_mount_pack.__file__)
except Exception as exc:
    print("failed:", type(exc).__name__, exc)
    print("tools listing:", list((REPO / "tools").glob("cars*")))
