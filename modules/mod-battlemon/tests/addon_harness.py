"""Shared Lua 5.1 harness: load the real Battlemon addon against the UI mocks and expose helpers.

    lua = load(Path(addon_dir))
    lua.execute("receive('FOLLOW\t0')")   # as if the server had sent it

Helpers defined in Lua: receive(payload), button(text), click(frame), row(ownedId), sent (outgoing messages),
printed (Battlemon.Print lines). The addon UI source is not in this repository: pass the package copy
(client/Interface/AddOns/Battlemon).
"""
import importlib.util
from pathlib import Path

from lupa.lua51 import LuaRuntime

M = Path(__file__).resolve().parents[1]


def load(addon: Path) -> LuaRuntime:
    spec = importlib.util.spec_from_file_location('smoke', M / 'tools/smoke_ui.py')
    smoke = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(smoke)
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(smoke.PRELUDE)
    lua.execute(r"""
SlashCmdList={}; StaticPopupDialogs={}; sent={}; printed={}; BattlemonDB={}
function GetTime() return 100 end
function UnitName() return 'Tester' end
function GetRealZoneText() return 'Elwynn Forest' end
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
""")
    return lua
