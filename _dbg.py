from lupa.lua51 import LuaRuntime
from pathlib import Path
SRC = Path(".agents/plans/character-select-redesign/src/GlueXML")
L = LuaRuntime(unpack_returned_tuples=True)
for n in ["ECS_Constants.lua","ECS_Schema.lua","ECS_Order.lua","ECS_Data.lua","ECS_Persistence.lua"]:
    L.execute((SRC/n).read_text(encoding="utf-8"))
L.execute(r'''
local P = ECS.Persistence
local values, writes = {}, 0
local backend = {
  get = function(n) return values[n] end,
  set = function(n,v) writes = writes + 1; values[n] = v; return true end,
}
P.SetBackend(backend)
local SLOTS = {
  { name="Sound_VoiceChatInputDriverName",  original="1" },
  { name="Sound_VoiceChatOutputDriverName", original="1" },
  { name="Sound_OutputDriverName",          original="0" },
}
local slots = P.ProbeCandidates(SLOTS, backend)
print("writable slots:", #slots)
local store = P.MakeStore("ZACHGM","Esteria",{"esteria:nat","esteria:zach"},{["esteria:nat"]="Main tank"})
local payload = P.Serialise(store)
print("payload:", payload)
print("payload len:", #payload)
local shards = P.Shard(payload)
print("shards:", #shards)
local ok, err = P.Save(store, slots)
print("save:", tostring(ok), tostring(err))
for _,s in ipairs(slots) do print("  cvar", s.name, "=", tostring(values[s.name])) end
local loaded, r = P.Load("ZACHGM","Esteria",slots)
print("load:", tostring(loaded), "reason:", tostring(r))
print("raw first value:", tostring(values["Sound_VoiceChatInputDriverName"]))
local shard, orig = P.UnwrapValue(values["Sound_VoiceChatInputDriverName"])
print("unwrapped shard:", tostring(shard), "orig:", tostring(orig))
''')
