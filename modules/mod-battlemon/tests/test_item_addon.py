"""Drive the held-item picker in the real addon through the real protocol callbacks.

    python tests/test_item_addon.py "<Battlemon addon dir>"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from addon_harness import load

lua = load(Path(sys.argv[1]))
lua.execute(r"""
local function starts(text, prefix) return text and string.sub(text, 1, #prefix) == prefix end
local function find(prefix)
 for i=#BM_FRAMES,1,-1 do
  local f=BM_FRAMES[i]
  if f.bmKind=='Button' and f.text and starts(f.text:GetText(), prefix) and f:IsShown() then return f end
 end
 error('Missing visible button starting with '..prefix)
end
local function visible(prefix)
 for i=#BM_FRAMES,1,-1 do
  local f=BM_FRAMES[i]
  if f.bmKind=='Button' and f.text and starts(f.text:GetText(), prefix) and f:IsShown() then return true end
 end
 return false
end
local function text(needle)
 for _,f in ipairs(BM_FRAMES) do
  if f.bmKind=='FontString' and f:GetText() and string.find(f:GetText(), needle, 1, true) then return f:GetText() end
 end
end

-- Raichu holds Leftovers; Pecharunt holds nothing. The held item is the last field of an OWNED line.
receive('OWNEDBEGIN')
receive('OWNED\t9001\t2065\t20\t0\tM\t40\tTHUNDERSHOCK\tGROWL\t\t\tRaichu\tBM3D_2065\t0\t0\tLEFTOVERS')
receive('OWNED\t9002\t2971\t20\t0\tN\t40\tTACKLE\t\t\t\tPecharunt\tBM3D_2971\t1\t0\t')
receive('OWNEDEND')
receive('PARTYSLOTS\t9001\t9002\t0\t0\t0\t0')
assert(Battlemon.state.owned[9001].held=='LEFTOVERS' and Battlemon.state.owned[9002].held=='')
-- Only holdable things in the bag are offered: a Potion is not, a Choice Band and Life Orb are.
receive('BAG\t0\tLIFEORB:2\tPOTION:5\tCHOICEBAND:1\tLEFTOVERS:0')

Battlemon.ShowParty()
assert(button('ITEM').bmEnabled==false, 'nothing selected yet')
assert(text('Leftovers'), 'the party slot shows what the lead is holding')

-- Opening the picker asks for a fresh bag and lists the holdable items.
local r=row(9001); r.bmScripts.OnClick(r)
click(button('ITEM'))
assert(BattlemonItemPicker.bmShown and sent[#sent]=='BAG', sent[#sent])
assert(text('Holding: Leftovers'), text('Holding'))
assert(visible('Choice Band') and visible('Life Orb'), 'holdable items are listed')
assert(not visible('Potion') and not visible('Leftovers'), 'a Potion is not holdable and a Leftovers x0 is not in the bag')

-- Giving sends the Pokemon and the item; taking sends the Pokemon.
click(find('Life Orb')); assert(sent[#sent]=='GIVE\t9001\tLIFEORB', sent[#sent])
assert(button('TAKE ITEM BACK').bmEnabled==true)
click(button('TAKE ITEM BACK')); assert(sent[#sent]=='TAKE\t9001', sent[#sent])

-- The server answers with the new state: nothing held, so there is nothing to take, and the bag is refreshed.
receive('OWNEDBEGIN')
receive('OWNED\t9001\t2065\t20\t0\tM\t40\tTHUNDERSHOCK\tGROWL\t\t\tRaichu\tBM3D_2065\t0\t0\t')
receive('OWNEDEND')
receive('BAG\t0\tLIFEORB:2\tCHOICEBAND:1\tLEFTOVERS:1')
assert(text('Holding nothing.') and button('TAKE ITEM BACK').bmEnabled==false)
assert(visible('Leftovers'), 'the returned item is back in the list')

-- A Pokemon that disappears (traded away) closes the picker instead of leaving a stale window.
receive('OWNEDBEGIN')
receive('OWNEDEND')
assert(not BattlemonItemPicker.bmShown)
""")
print('PASS: item picker lists holdable bag items, sends GIVE/TAKE, follows the server state, closes if the Pokemon is gone.')
