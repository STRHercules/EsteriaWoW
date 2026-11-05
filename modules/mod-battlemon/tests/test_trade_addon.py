"""Drive a whole Pokemon trade in the real addon through the real protocol callbacks.

    python tests/test_trade_addon.py "<Battlemon addon dir>"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from addon_harness import load

lua = load(Path(sys.argv[1]))
lua.execute(r"""
local function textOf(frame, needle)
 for _,f in ipairs(BM_FRAMES) do
  if f.bmKind=='FontString' and f:GetText() and string.find(f:GetText(), needle, 1, true) then return f:GetText() end
 end
end
local function last() return sent[#sent] end

receive('OWNEDBEGIN')
receive('OWNED\t9001\t2065\t20\t0\tM\t40\tTHUNDERSHOCK\tGROWL\t\t\tRaichu\tBM3D_2065\t0\t0')
receive('OWNED\t9002\t2971\t20\t0\tN\t40\tTACKLE\t\t\t\tPecharunt\tBM3D_2971\t1\t0')
receive('OWNEDEND')
receive('PARTYSLOTS\t9001\t0\t0\t0\t0\t0')

-- Starting a trade names the partner; with no name and no target it explains itself and sends nothing.
local before=#sent
Battlemon.StartTrade('')
assert(#sent==before and string.find(printed[#printed],'Usage',1,true), 'no name, no target: usage only')
Battlemon.StartTrade('  Bob ')
assert(last()=='TRADE\tINVITE\tBob', last())

-- An invitation from somebody else opens the answer box; declining answers DECLINE and closes it.
receive('TRADEINVITE\tAlice')
assert(BattlemonTradeInvite.bmShown and textOf(BattlemonTradeInvite,'Alice wants to trade'))
click(button('DECLINE')); assert(last()=='TRADE\tDECLINE' and not BattlemonTradeInvite.bmShown)

-- Accepting, then the server opens the trade window for both sides.
receive('TRADEINVITE\tBob')
click(button('ACCEPT')); assert(last()=='TRADE\tACCEPT')
receive('TRADE\tBob\t0\t0')
assert(BattlemonTradeFrame.bmShown, 'the trade window opens')
assert(textOf(BattlemonTradeFrame,'Trade with Bob'))
assert(button('CONFIRM TRADE').bmEnabled==false, 'nothing is on the table yet')
assert(button('OFFER SELECTED').bmEnabled==false, 'nothing selected yet')

-- Pick a Pokemon from the box (not in the party) and offer it.
local r=row(9002); r.bmScripts.OnClick(r)
click(button('OFFER SELECTED')); assert(last()=='TRADE\tOFFER\t9002', last())
receive('TRADEMON\tM\t2971\t20\t1\tN\tTACKLE\t\t\t\tPecharunt')
receive('TRADEMON\tT')
assert(Battlemon.state.trade.mine and Battlemon.state.trade.mine.level==20 and Battlemon.state.trade.mine.shiny)
assert(Battlemon.state.trade.theirs==nil)
assert(button('CONFIRM TRADE').bmEnabled==true and button('CLEAR OFFER').bmEnabled==true)

-- Their offer arrives; confirming sends CONFIRM and locks the button until something changes.
receive('TRADEMON\tT\t2065\t30\t0\tM\tTHUNDERSHOCK\tGROWL\t\t\tRaichu')
assert(Battlemon.state.trade.theirs.formId==2065 and Battlemon.state.trade.theirs.name=='Raichu')
click(button('CONFIRM TRADE')); assert(last()=='TRADE\tCONFIRM')
receive('TRADE\tBob\t1\t0')
assert(button('CONFIRM TRADE').bmEnabled==false and textOf(BattlemonTradeFrame,'You confirmed'))

-- The other side changes their offer: the server clears both confirmations and we can confirm again.
receive('TRADE\tBob\t0\t0')
assert(button('CONFIRM TRADE').bmEnabled==true)
receive('TRADE\tBob\t0\t1')
assert(textOf(BattlemonTradeFrame,'Bob confirmed'))

-- Clearing the offer and cancelling both go to the server.
click(button('CLEAR OFFER')); assert(last()=='TRADE\tOFFER\t0')
click(button('CANCEL TRADE')); assert(last()=='TRADE\tCANCEL')

-- The server ends the trade: window closed, state wiped, the reason shown.
receive('TRADEEND\tTrade complete!')
assert(not BattlemonTradeFrame.bmShown and next(Battlemon.state.trade)==nil)
assert(string.find(printed[#printed],'Trade complete!',1,true), printed[#printed])
""")
print('PASS: trade window: invite/decline/accept, offer from the box, both-confirm flow resets on change, cancel, end.')
