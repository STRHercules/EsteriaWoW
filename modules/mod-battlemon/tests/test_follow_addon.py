"""Run the real addon in Lua 5.1 and drive the follower button through the real protocol callbacks.

    python tests/test_follow_addon.py "<Battlemon addon dir>"

The addon UI source is not in this repository; point it at the package copy (client/Interface/AddOns/Battlemon).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from addon_harness import load

lua = load(Path(sys.argv[1]))
lua.execute(r"""
receive('OWNEDBEGIN')
receive('OWNED\t9001\t2065\t20\t0\tM\t40\tTHUNDERSHOCK\tGROWL\t\t\tRaichu\tBM3D_2065\t0\t0')
receive('OWNED\t9002\t2971\t20\t0\tN\t40\tTACKLE\t\t\t\tPecharunt\tBM3D_2971\t1\t0')
receive('OWNEDEND')
receive('PARTYSLOTS\t9001\t0\t0\t0\t0\t0')
receive('FOLLOW\t0')      -- the sync the server sends with the owned list
assert(Battlemon.state.followerId==0 and #printed==0, 'initial sync must be silent')

Battlemon.ShowParty()
assert(button('FOLLOW').bmEnabled==false, 'nothing selected yet')

-- Pick a Pokemon that is NOT in the party: following does not need a party slot.
local r=row(9002); r.bmScripts.OnClick(r)
click(button('FOLLOW'))
assert(sent[#sent]=='FOLLOW\t9002', sent[#sent])

-- Server confirms: the button flips, the change is announced, the slot-less Pokemon stays selected.
receive('FOLLOW\t9002')
assert(Battlemon.state.followerId==9002)
assert(#printed==1 and string.find(printed[1],'follows you',1,true), printed[1])
assert(button('STOP FOLLOW'))
click(button('STOP FOLLOW'))
assert(sent[#sent]=='FOLLOW\t0', sent[#sent])
receive('FOLLOW\t0')
assert(#printed==2 and string.find(printed[2],'stops following',1,true), printed[2])
assert(button('FOLLOW'))

-- The same value arriving again (every owned-list refresh repeats it) says nothing.
receive('FOLLOW\t0'); receive('FOLLOW\t0')
assert(#printed==2)

-- Following is cosmetic: it stays available mid-battle while the party buttons lock.
Battlemon.battleActive=true
Battlemon.RefreshParty()
assert(button('FOLLOW').bmEnabled==true and button('SAVE PARTY').bmEnabled==false)
Battlemon.battleActive=false

-- A fresh login starts from nothing again.
receive('HELLO')
assert(Battlemon.state.followerId==nil)
""")
print('PASS: follower button sends FOLLOW, flips on the server echo, announces changes once, works outside the party and mid-battle.')
