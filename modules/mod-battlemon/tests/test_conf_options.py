"""Every Battlemon.Follower.*, .Trade.* and .Breeding.* option read by the code must be documented in
conf/mod_battlemon.conf.dist, and every option documented there must actually be read."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
code = ''.join(open(os.path.join(ROOT, 'src', f), encoding='utf-8').read()
               for f in ('BattlemonFollower.cpp', 'BattlemonTrade.cpp', 'BattlemonMgr.cpp'))
conf = open(os.path.join(ROOT, 'conf', 'mod_battlemon.conf.dist'), encoding='utf-8').read()
pattern = r'Battlemon\.(?:Follower|Trade|Breeding)\.\w+'
used = sorted(set(re.findall(r'GetOption<\w+>\("(' + pattern + r')"', code)))
assert len(used) == 11, used
for name in used:
    assert re.search(r'^' + re.escape(name) + r' = ', conf, re.M), name + ' is read but not documented'
documented = set(re.findall(r'^(' + pattern + r') = ', conf, re.M))
assert documented == set(used), sorted(documented ^ set(used))
print('ok', len(used), 'options')
