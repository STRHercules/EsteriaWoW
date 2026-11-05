"""The addon's X_ITEMS list must name exactly the items the server's XItemStat() accepts.

    python tests/test_xitems_addon.py "<Battlemon addon dir>"
"""
import re
import sys
from pathlib import Path

M = Path(__file__).resolve().parents[1]
lua = (Path(sys.argv[1]) / 'UI' / 'BattleFrame.lua').read_text(encoding='utf-8')
cpp = (M / 'src' / 'BattlemonMgr.cpp').read_text(encoding='utf-8')

client = set(re.findall(r'(X[A-Z]+) = true', re.search(r'local X_ITEMS = \{(.*?)\}', lua, re.S).group(1)))
body = re.search(r'bool XItemStat\(.*?\n    \}\n', cpp, re.S).group(0)
server = set(re.findall(r'item == "(X[A-Z]+)"', body))
assert client == server and len(server) == 6, (client, server)

# Everything the server accepts is for sale, so a player can actually get it.
shop = ''.join(p.read_text(encoding='utf-8') for p in (M / 'data/sql/db-world/base').glob('*shop*.sql'))
for item in server:
    assert f"('{item}'," in shop, item
print('ok', sorted(server))
