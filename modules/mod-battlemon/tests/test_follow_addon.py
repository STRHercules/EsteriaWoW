"""Run the real addon in Lua 5.1 and drive the follower button through the real protocol callbacks.

    python tests/test_follow_addon.py "<Battlemon addon dir>"

The addon UI source is not in this repository; point it at the package copy (client/Interface/AddOns/Battlemon).
"""
import importlib.util
from pathlib import Path
import sys

from lupa.lua51 import LuaRuntime

M = Path(__file__).resolve().parents[1]
addon = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location('smoke', M / 'tools/smoke_ui.py')
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)

lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute(smoke.PRELUDE)
lua.execute(r"""
SlashCmdList={}; StaticPopupDialogs={}; sent={}; printed={}; BattlemonDB={}
function GetTime() return 100 end
function UnitName() return 'Tester' end
function SendAddonMessage(prefix,payload) sent[#sent+1]=payload end
function hooksecurefunc(object, method, hook)
 local original=object[method]
 object[method]=function(...) original(...); hook(...) end
end
local mt=getmetatable(CreateFrame('Frame'))
function mt:GetAlpha() return self.alpha or 1 end
function mt:SetAlpha(a) self.alpha=a end
function mt:SetModel(path) self.path=path end
function mt:SetFacing(value) self.facing=value end
function receive(payload)
 for _,f in ipairs(BM_FRAMES) do
  if f.bmScripts.OnEvent then f.bmScripts.OnEvent(f,'CHAT_MSG_ADDON','BM',payload,'WHISPER','Tester') end
 end
end
function button(text)
 for _,f in ipairs(BM_FRAMES) do
  if f.bmKind=='Button' and f.text and f.text:GetText()==text then return f end
 end
 error('Missing button '..text)
end
function click(b)
 assert(b.bmEnabled~=false,'Disabled button '..tostring(b.text and b.text:GetText()))
 b.bmScripts.OnClick(b,'LeftButton')
end
function row(ownedId)
 for _,f in ipairs(BM_FRAMES) do
  if f.bmKind=='Button' and f.ownedId==ownedId and f.bmScripts.OnClick then return f end
 end
 error('Missing row '..ownedId)
end
""")
for line in (addon / 'Battlemon.toc').read_text(encoding='utf-8').splitlines():
    if line.endswith('.lua'):
        lua.execute((addon / line.replace('\\', '/')).read_text(encoding='utf-8-sig'))
lua.execute(r"""
Battlemon.Print=function(text) printed[#printed+1]=text end
Battlemon.LoadData()
Battlemon.EnsureProfileDB()
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
