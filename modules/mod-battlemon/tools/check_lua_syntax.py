import os
import sys
from luaparser import ast

root = sys.argv[1]
targets = []
for dirpath, _, files in os.walk(root):
    if os.path.basename(dirpath) in ("Data", "tools", "__pycache__"):
        continue
    for f in files:
        if f.endswith(".lua"):
            targets.append(os.path.join(dirpath, f))

bad = 0
for path in sorted(targets):
    src = open(path, encoding="utf-8").read()
    try:
        ast.parse(src)
        print("OK   ", os.path.relpath(path, root))
    except Exception as exc:
        bad += 1
        print("FAIL ", os.path.relpath(path, root), "->", exc)
print("checked", len(targets), "files,", bad, "failures")
