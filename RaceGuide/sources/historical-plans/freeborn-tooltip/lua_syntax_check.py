import sys
from pathlib import Path
from luaparser import ast

root = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools\freeborn_client")
body = (root / "CharacterCreate.freeborn.lua").read_text(encoding="utf-8")
block = "if not CharacterFreeborn_Init then\n" + body + "\nend\n"
try:
    tree = ast.parse(block)
except Exception as exc:
    print("LUA SYNTAX ERROR:", exc)
    sys.exit(1)
print("lua syntax: OK,", len(list(ast.walk(tree))), "nodes")
