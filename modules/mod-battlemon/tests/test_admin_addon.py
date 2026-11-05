"""Drive the spawn admin panel in the real addon through the real protocol callbacks.

    python tests/test_admin_addon.py "<Battlemon addon dir>"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from addon_harness import load

lua = load(Path(sys.argv[1]))
lua.execute(r"""
-- What the server sends for GET: every knob, this zone's rule, then END.
receive('ADMIN\tSET\tenable\t1')
receive('ADMIN\tSET\tlevel_mode\t0')
receive('ADMIN\tSET\trarity_exponent\t1')
receive('ADMIN\tSET\tstage_step\t16')
receive('ADMIN\tSET\tleak\t0.15')
receive('ADMIN\tSET\tweight_normal\t94')
receive('ADMIN\tSET\tweight_starter\t5')
receive('ADMIN\tSET\tweight_legendary\t1')
receive('ADMIN\tZONE\t12\t1\t10\tNORMAL:3,GRASS:3')
receive('ADMIN\tEND')

Battlemon.ShowAdmin()
assert(sent[#sent]=='ADMIN\tGET', 'opening the panel asks for the current state: '..tostring(sent[#sent]))
receive('ADMIN\tEND')
local function box(name) return _G['BattlemonAdmin_'..name] end
assert(box('level_mode'):GetText()=='0' and box('weight_normal'):GetText()=='94')
assert(box('zoneMin'):GetText()=='1' and box('zoneMax'):GetText()=='10')
assert(box('zoneTypes'):GetText()=='NORMAL:3,GRASS:3')

-- Enter in a box saves that one knob.
box('level_mode'):SetText('2')
box('level_mode').bmScripts.OnEnterPressed(box('level_mode'))
assert(sent[#sent]=='ADMIN\tSET\tlevel_mode\t2', sent[#sent])
receive('ADMIN\tSET\tlevel_mode\t2')   -- the server applies it and sends the state back

-- APPLY ALL sends only what differs from the server, and never a tab or newline from the text box.
local before=#sent
box('leak'):SetText('0.5\tx\n')
box('weight_legendary'):SetText('0')
click(button('APPLY ALL'))
assert(#sent==before+2, 'only the two changed knobs are sent, got '..(#sent-before))
local got={}
for i=before+1,#sent do got[sent[i]]=true end
assert(got['ADMIN\tSET\tleak\t0.5x'] and got['ADMIN\tSET\tweight_legendary\t0'])

-- Saving the zone sends levels and types for the zone the server reports.
box('zoneMin'):SetText('5'); box('zoneMax'):SetText('15'); box('zoneTypes'):SetText('FIRE:3,ROCK:2')
click(button('SAVE ZONE'))
assert(sent[#sent]=='ADMIN\tZONE\t5\t15\tFIRE:3,ROCK:2', sent[#sent])

-- Preview asks, and the answer is listed with its level.
click(button('PREVIEW'))
assert(sent[#sent]=='ADMIN\tPREVIEW')
receive('ADMIN\tODDS\t8\tPidgey~12.5\tMr. Mime~3.0\tType: Null~0.4')
receive('ADMIN\tEND')
local shown=Battlemon.state.admin.odds
assert(shown.level==8 and #shown.list==3 and shown.list[2].name=='Mr. Mime' and shown.list[3].name=='Type: Null')

-- A zone with no rule is shown as such and leaves the boxes empty.
receive('ADMIN\tZONE\t1519\t0\t0\t')
receive('ADMIN\tEND')
assert(box('zoneMin'):GetText()=='' and box('zoneTypes'):GetText()=='')

-- Not an administrator: the server only says so; the panel must not crash on an empty state.
Battlemon.state.admin = { settings = {} }
Battlemon.RefreshAdmin()
""")
print('PASS: admin panel asks on open, saves single knobs and APPLY ALL (changed only, sanitised), saves the zone, shows a preview.')
