"""Every Battlemon.Follower.* and Battlemon.Trade.* option read by the code must be documented in conf/mod_battlemon.conf.dist."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
code = open(os.path.join(ROOT, 'src', 'BattlemonFollower.cpp'), encoding='utf-8').read() +     open(os.path.join(ROOT, 'src', 'BattlemonTrade.cpp'), encoding='utf-8').read()
conf = open(os.path.join(ROOT, 'conf', 'mod_battlemon.conf.dist'), encoding='utf-8').read()
used = re.findall(r'GetOption<\w+>\("(Battlemon\.(?:Follower|Trade)\.\w+)"', code)
assert len(used) == 5, used
for name in used:
    assert re.search(r'^' + re.escape(name) + r' = ', conf, re.M), name
print('ok', used)
