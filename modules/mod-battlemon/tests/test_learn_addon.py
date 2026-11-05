"""Drive the "forget a move to learn a new one" prompt in the real addon through the real protocol callbacks.

    python tests/test_learn_addon.py "<Battlemon addon dir>"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from addon_harness import load

lua = load(Path(sys.argv[1]))
lua.execute(r"""
local function starts(frameText, prefix) return frameText and string.sub(frameText, 1, #prefix) == prefix end
local function find(prefix)
 for i=#BM_FRAMES,1,-1 do
  local f=BM_FRAMES[i]
  if f.bmKind=='Button' and f.text and starts(f.text:GetText(), prefix) then return f end
 end
 error('Missing button starting with '..prefix)
end
local function titleOf(frame)
 for _,f in ipairs(BM_FRAMES) do
  if f.bmKind=='FontString' and f.bmParent==frame and f:GetText() and string.find(f:GetText(),'wants to learn',1,true) then return f:GetText() end
 end
end

assert(Battlemon.MovesByInternal.VINEWHIP and Battlemon.MovesByInternal.TACKLE, 'real move data is loaded')

-- The server found a fifth move for a Pokemon that knows four.
receive('LEARNOFFER\t9001\tVINEWHIP\tTACKLE\tGROWL\tLEECHSEED\tGROWTH\tBulbasaur')
assert(BattlemonLearnFrame.bmShown, 'the prompt opens')
assert(titleOf(BattlemonLearnFrame)=='Bulbasaur wants to learn Vine Whip!', titleOf(BattlemonLearnFrame))
find('Forget Tackle'); find('Forget Growl'); find('Forget Leech Seed'); find('Forget Growth')

-- Forgetting the second move answers with that slot; the prompt closes.
click(find('Forget Growl'))
assert(sent[#sent]=='LEARNREPLY\t9001\tVINEWHIP\t2', sent[#sent])
assert(not BattlemonLearnFrame.bmShown)

-- Declining answers slot 0.
receive('LEARNOFFER\t9001\tRAZORLEAF\tTACKLE\tVINEWHIP\tLEECHSEED\tGROWTH\tBulbasaur')
click(find("Don't learn Razor Leaf"))
assert(sent[#sent]=='LEARNREPLY\t9001\tRAZORLEAF\t0', sent[#sent])
assert(not BattlemonLearnFrame.bmShown)

-- While one prompt is open a different offer must not replace it; the server sends it after the answer.
receive('LEARNOFFER\t9001\tVINEWHIP\tTACKLE\tGROWL\tLEECHSEED\tGROWTH\tBulbasaur')
receive('LEARNOFFER\t9002\tEMBER\tSCRATCH\tGROWL\tSMOKESCREEN\tTACKLE\tCharmander')
assert(titleOf(BattlemonLearnFrame)=='Bulbasaur wants to learn Vine Whip!', 'the first prompt stays')
-- The same offer arriving again (every refresh may repeat it) is harmless.
receive('LEARNOFFER\t9001\tVINEWHIP\tTACKLE\tGROWL\tLEECHSEED\tGROWTH\tBulbasaur')
click(find('Forget Tackle'))
assert(sent[#sent]=='LEARNREPLY\t9001\tVINEWHIP\t1', sent[#sent])
receive('LEARNOFFER\t9002\tEMBER\tSCRATCH\tGROWL\tSMOKESCREEN\tTACKLE\tCharmander')
assert(titleOf(BattlemonLearnFrame)=='Charmander wants to learn Ember!')

-- Opening the party screen also asks whether anything is waiting.
Battlemon.ShowParty()
local asked=false
for _,m in ipairs(sent) do if m=='LEARNQ' then asked=true end end
assert(asked, 'the party screen asks for pending offers')
""")
print('PASS: learn prompt shows the offer, answers with the chosen slot or 0, keeps one prompt at a time, party screen asks.')
