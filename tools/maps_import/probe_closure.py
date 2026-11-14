"""Closure + collision probe for the small packs. Read-only."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402
import closure  # noqa: E402

SRC = lib.REPO / "NewModels" / "_Maps"
SCRATCH = Path(sys.argv[1])
cf = lib.ClientFiles(Path(r"G:\3.3.5a - Dev\Data"), SCRATCH / "mpqcopy").open()
print("client index:", len(cf.index), "files in", len(cf.handles), "archives")

PACKS = {
    "Island-Project": [SRC / "Island-Project-main" / "Patch-I.mpq"],
    "SceneGaming": [SRC / "SceneGaming" / "Scene Gaming" / "patch-4.MPQ"],
    "Morza": [SRC / "Morza-Island-Araxia-Server-main" / "patch-Z.mpq"],
}
for name, mpqs in PACKS.items():
    pack_files: dict[str, bytes] = {}
    for m in mpqs:
        h = lib.open_ro(m)
        for n, _ in lib.list_archive(h):
            if n.startswith("("):
                continue
            b = lib.read_member(h, n)
            if b is not None:
                pack_files[lib.norm(n)] = b
                pack_files[lib.norm(n) + "\0name"] = n.encode()
    names = {k: v.decode() for k, v in pack_files.items() if k.endswith("\0name")}
    data = {k: v for k, v in pack_files.items() if not k.endswith("\0name")}
    adts = [(names[k + "\0name"], v) for k, v in data.items() if k.endswith(".adt")]

    def read(p, data=data):
        k = lib.norm(p)
        if k in data:
            return data[k]
        return cf.read(p)

    found, missing = closure.compute(adts, read)
    in_pack = [p for p in found if lib.norm(p) in data]
    in_client = [p for p in found if lib.norm(p) not in data]
    print(f"\n== {name}: {len(adts)} ADT, pack files {len(data)}, closure {len(found)}, in-pack {len(in_pack)}, "
          f"from-client {len(in_client)}, MISSING {len(missing)}")
    for p in sorted(missing)[:25]:
        print("   missing:", p)
    # collisions: pack file with the same path as an existing client file
    same = diff = 0
    diffs = []
    for k, v in data.items():
        if k.startswith("dbfilesclient/") or k.endswith(".trs"):
            continue
        if cf.has(k):
            cur = cf.read(k)
            if cur == v:
                same += 1
            else:
                diff += 1
                diffs.append(k)
    print(f"   path already in client: identical {same}, DIFFERENT {diff}")
    for k in diffs[:15]:
        print("   differs:", k, "(client provider:", cf.provider(k), ")")
