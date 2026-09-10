#!/usr/bin/env python3
"""Headless smoke test for the Battlemon UI layer.

Loads Core/Util.lua, Core/UI.lua and every UI/*.lua against a stub of the parts
of the 3.3.5 API they touch, then drives the panel switching that the client
would: opening each page, flipping between the unified window and separate
windows, and running a battle to its end. Catches the nil calls and ordering
mistakes that otherwise only show up as a Lua error in game.

Usage:
    python tools/smoke_ui.py "<Battlemon addon dir>"
"""

import os
import sys

from lupa import LuaRuntime

PRELUDE = r"""
UISpecialFrames = {}
local frames = {}
local nextId = 0

local FrameMT = {}
FrameMT.__index = function(t, k)
    local v = rawget(FrameMT, k)
    if v ~= nil then return v end
    -- Widget methods are PascalCase; anything else is an addon field that has
    -- not been set, and must read as nil rather than as a truthy no-op.
    if type(k) == "string" and string.match(k, "^%u") then
        return function() end
    end
    return nil
end

local function newFrame(kind, name, parent, template)
    nextId = nextId + 1
    local f = setmetatable({
        bmKind = kind, bmTemplate = template, bmParent = parent,
        bmShown = false, bmW = 0, bmH = 0, bmPoints = 0,
        bmStrata = "MEDIUM", bmMovable = false, bmDrag = false,
        bmScripts = {}, bmChildren = {}, bmId = nextId, bmGlobal = name,
    }, FrameMT)
    if name then _G[name] = f end
    frames[#frames + 1] = f
    return f
end

function FrameMT:CreateTexture() return newFrame("Texture", nil, self) end
function FrameMT:CreateFontString() return newFrame("FontString", nil, self) end
function FrameMT:SetSize(w, h) self.bmW, self.bmH = w, h end
function FrameMT:SetWidth(w) self.bmW = w end
function FrameMT:SetHeight(h) self.bmH = h end
function FrameMT:GetWidth() return self.bmW end
function FrameMT:GetHeight() return self.bmH end
function FrameMT:SetPoint() self.bmPoints = self.bmPoints + 1 end
function FrameMT:ClearAllPoints() self.bmPoints = 0 end
function FrameMT:GetNumPoints() return self.bmPoints end
function FrameMT:Show()
    self.bmShown = true
    local fn = self.bmScripts.OnShow
    if fn then fn(self) end
end
function FrameMT:Hide()
    self.bmShown = false
    local fn = self.bmScripts.OnHide
    if fn then fn(self) end
end
function FrameMT:IsShown() return self.bmShown end
function FrameMT:IsVisible()
    local f = self
    while f do
        if not f.bmShown then return false end
        f = f.bmParent
    end
    return true
end
function FrameMT:SetParent(p) self.bmParent = p end
function FrameMT:GetParent() return self.bmParent end
function FrameMT:SetFrameStrata(s) self.bmStrata = s end
function FrameMT:GetFrameStrata() return self.bmStrata end
function FrameMT:SetFrameLevel(l) self.bmLevel = l end
function FrameMT:GetFrameLevel() return self.bmLevel or 1 end
function FrameMT:SetMovable(v) self.bmMovable = v and true or false end
function FrameMT:IsMovable() return self.bmMovable end
function FrameMT:RegisterForDrag(...) self.bmDrag = select("#", ...) > 0 end
function FrameMT:StartMoving()
    if not self.bmMovable then
        error("StartMoving on a frame that is not movable: " .. tostring(self.bmGlobal))
    end
end
function FrameMT:SetScript(name, fn) self.bmScripts[name] = fn end
function FrameMT:GetScript(name) return self.bmScripts[name] end
function FrameMT:HookScript(name, fn) self.bmScripts[name] = fn end
function FrameMT:SetChecked(v) self.bmChecked = v and true or false end
function FrameMT:GetChecked() return self.bmChecked end
function FrameMT:Enable() self.bmEnabled = true end
function FrameMT:Disable() self.bmEnabled = false end
function FrameMT:GetText() return self.bmText or "" end
function FrameMT:SetText(t) self.bmText = t end
function FrameMT:Click()
    local fn = self.bmScripts.OnClick
    if fn then fn(self, "LeftButton") end
end
-- WoW only fires OnDragStart for a frame that registered a drag button, so
-- clearing the registration is what actually makes an embedded page inert.
function FrameMT:Drag()
    if not self.bmDrag then return false end
    local fn = self.bmScripts.OnDragStart
    if fn then fn(self) end
    return true
end

function CreateFrame(kind, name, parent, template)
    local f = newFrame(kind, name, parent, template)
    if template and string.find(template, "UICheckButtonTemplate") and name then
        _G[name .. "Text"] = newFrame("FontString", name .. "Text", f)
    end
    return f
end

UIParent = newFrame("Frame", "UIParent")
UIParent.bmShown = true
Minimap = newFrame("Frame", "Minimap", UIParent)

function getglobal(n) return _G[n] end
function tinsert(t, v) table.insert(t, v) end
function GetTime() return 100 end
function PlaySound() end
function FauxScrollFrame_Update() end
function FauxScrollFrame_GetOffset() return 0 end
function FauxScrollFrame_SetOffset() end
function FauxScrollFrame_OnVerticalScroll() end
GameTooltip = newFrame("Frame", "GameTooltip", UIParent)
DEFAULT_CHAT_FRAME = { AddMessage = function() end }

-- Most widgets are anonymous, so tests reach them through their label. Searches
-- newest first, since later-built frames are the ones a test just triggered.
function BM_FIND(text)
    for i = #frames, 1, -1 do
        if frames[i].bmText == text then return frames[i] end
    end
end

-- Labels repeat across panels ("MOVES" is both a tab and a party button), so
-- pin the lookup to the frame the button belongs to. depth is how many frames
-- sit between the button and root: 1 for a direct child, 2 for a scroll row.
function BM_BUTTON(root, text, depth)
    depth = depth or 1
    for i = 1, #frames do
        local f = frames[i]
        if f.bmText == text and f.bmParent then
            local a = f.bmParent
            for _ = 1, depth do
                a = a and a.bmParent
            end
            if a == root then return f.bmParent end
        end
    end
end

-- The visible party rows, in order. Row labels are the FontStrings three deep
-- (label -> row button -> list frame -> panel); the "Lv." line beside each one
-- is filtered out, and hidden rows keep stale text so they are skipped too.
function BM_PARTY_ROWS()
    local out = {}
    for i = 1, #frames do
        local f = frames[i]
        local btn = f.bmParent
        if f.bmKind == "FontString" and btn and btn.bmShown and btn.bmParent
                and btn.bmParent.bmParent == _G.BattlemonPartyFrame
                and f.bmText and f.bmText ~= ""
                and not string.find(f.bmText, "Lv%.") then
            out[#out + 1] = f.bmText
        end
    end
    return table.concat(out, ",")
end

BM_FRAMES = frames
"""

STUBS = r"""
Battlemon = Battlemon or {}
Battlemon.state = {
    owned = {}, partySlots = { 0, 0, 0, 0, 0, 0 }, bag = { POKEBALL = 5 },
    shop = {}, points = 120, ready = true, readyIn = 0, learnset = nil,
}
Battlemon.Items = {}
Battlemon.Species = {}
Battlemon.Forms = {}
Battlemon.FormsList = {}
Battlemon.sent = {}
function Battlemon.Send(cmd, arg)
    table.insert(Battlemon.sent, cmd .. (arg and (" " .. tostring(arg)) or ""))
end
Battlemon.net = {}
function Battlemon.OnNet(cmd, fn) Battlemon.net[cmd] = fn end
function Battlemon.EnsureData() end
function Battlemon.SetPokemonTexture() return true end
function Battlemon.FormName(_, name) return name or "???" end
function Battlemon.FormSprite(_, sprite) return sprite or "0025_Pikachu" end
function Battlemon.FormLabel() return "Pikachu" end
function Battlemon.SplitFormName(name) return nil, name end
function Battlemon.ShinyName(name) return name end
function Battlemon.SetBattlerTextures() end
function Battlemon.TypeRGB() return 1, 1, 1 end
function Battlemon.ParseBattler() return {} end
Battlemon.Types = {}
"""

DRIVE = r"""
local log = {}
local function say(s) log[#log + 1] = s end

local function shownPages()
    local out = {}
    for _, name in ipairs({ "BattlemonHubFrame", "BattlemonPartyFrame", "BattlemonMoveFrame",
                            "BattlemonDexFrame", "BattlemonShopFrame", "BattlemonBagFrame",
                            "BattlemonFrame" }) do
        local f = _G[name]
        if f and f:IsShown() then out[#out + 1] = name end
    end
    return table.concat(out, ",")
end

local function assertEq(what, got, want)
    if tostring(got) ~= tostring(want) then
        error(string.format("%s: got %s, want %s", what, tostring(got), tostring(want)), 0)
    end
    say("ok  " .. what)
end

local function escCount(name)
    local n = 0
    for _, v in ipairs(UISpecialFrames) do
        if v == name then n = n + 1 end
    end
    return n
end

-- Default is the all-in-one window.
assertEq("default mode is unified", Battlemon.Unified(), true)

Battlemon.ShowHub()
local shell = _G.BattlemonMainFrame
assertEq("shell exists", shell ~= nil, true)
assertEq("shell shown", shell:IsShown(), true)
assertEq("shell size", shell:GetWidth() .. "x" .. shell:GetHeight(), "868x632")
assertEq("home is the visible page", shownPages(), "BattlemonHubFrame")
assertEq("hub reparented into the shell", _G.BattlemonHubFrame:GetParent() ~= UIParent, true)
assertEq("hub is not draggable while embedded", _G.BattlemonHubFrame:IsMovable(), false)
assertEq("hub off the escape list", escCount("BattlemonHubFrame"), 0)
assertEq("shell on the escape list", escCount("BattlemonMainFrame"), 1)

-- Every tab builds its page and swaps cleanly.
for _, key in ipairs({ "party", "moves", "dex", "shop", "bag", "home" }) do
    Battlemon.OpenPanel(key)
end
assertEq("one page visible after cycling tabs", select(2, string.gsub(shownPages(), ",", "")), 0)

-- Panels adopted later must also lose their chrome and drag.
Battlemon.OpenPanel("dex")
assertEq("dex embedded", _G.BattlemonDexFrame:GetParent() ~= UIParent, true)
assertEq("only the dex is visible", shownPages(), "BattlemonDexFrame")
assertEq("dragging an embedded page is inert", _G.BattlemonDexFrame:Drag(), false)

-- The server sends the party lead as a battler on login, so a populated
-- Battlemon.battle must not read as a fight in progress.
Battlemon.battle = { player = { name = "Pikachu", hp = 18, maxhp = 18, moves = {} } }
assertEq("party lead alone is not a battle", Battlemon.InBattle(), false)
Battlemon.OpenPanel("home")
local battleTab = BM_BUTTON(_G.BattlemonMainFrame, "BATTLE")
assertEq("battle tab disabled out of combat", battleTab.bmEnabled, false)

-- The party MOVES button reads the same signal, and was stuck greyed out.
-- hp mirrors the OWNED packet, which only refreshes between fights.
Battlemon.state.owned[7] = { id = 7, name = "Pikachu", level = 20, formId = 1, sprite = "0025_Pikachu", hp = 18 }
-- Zubat reads as fainted in the roster: it went down in an earlier fight and
-- the OWNED packet has not been refreshed since. The battle snapshot below is
-- what decides whether it can be sent out.
Battlemon.state.owned[8] = { id = 8, name = "Zubat", level = 30, formId = 1, hp = 0, reviveIn = 2400 }
Battlemon.state.owned[9] = { id = 9, name = "Abra", level = 2, formId = 1, hp = 8 }
Battlemon.state.partySlots[1] = 7
Battlemon.OpenPanel("party")
assertEq("party listed by name, not by level", BM_PARTY_ROWS(), "Abra,Pikachu,Zubat")
local partyMoves = BM_BUTTON(_G.BattlemonPartyFrame, "MOVES")
assertEq("party MOVES disabled with nothing selected", partyMoves.bmEnabled, false)
BM_BUTTON(_G.BattlemonPartyFrame, "Pikachu", 2):Click()
assertEq("party MOVES enabled out of combat", partyMoves.bmEnabled, true)

-- A live battle: the WILD packet must open the battle page.
Battlemon.battleActive = true
Battlemon.battle.enemy = { name = "Diglett", hp = 12, maxhp = 12 }
Battlemon.OpenPanel("battle")
assertEq("battle page visible", shownPages(), "BattlemonFrame")
assertEq("battle tab live", Battlemon.InBattle(), true)
assertEq("battle tab enabled in combat", battleTab.bmEnabled, true)

-- Tabbing away stops nudge() pumping the queue, so coming back has to restart
-- it or the command menu never returns and the fight is unplayable.
local commands = BM_FIND("BAG").bmParent.bmParent
assertEq("command menu up during the fight", commands:IsShown(), true)
Battlemon.OpenPanel("home")
assertEq("battle page hidden behind another tab", _G.BattlemonFrame:IsShown(), false)
commands:Hide()
Battlemon.OpenPanel("battle")
assertEq("command menu restored on return", commands:IsShown(), true)

-- A fainted lead owes the server a switch. Picking the Pokemon that just went
-- down used to bounce back to the command menu and offer an attack the server
-- silently refuses, so the turn looked like it happened but did nothing.
-- Timers are collected rather than run inline: the client receives a whole
-- turn's packets in one burst and only then plays the message queue.
local realAfter = Battlemon.After
local timers = {}
Battlemon.After = function(_, fn) timers[#timers + 1] = fn end
local function drain()
    local guard = 0
    while #timers > 0 and guard < 200 do
        table.remove(timers, 1)()
        guard = guard + 1
    end
end
function Battlemon.ParseBattler(a)
    return { name = a[2], hp = tonumber(a[3]) or 0, maxhp = tonumber(a[4]) or 1,
             partySlot = tonumber(a[5]) or 1, moves = {} }
end
Battlemon.state.partySlots[2] = 8
Battlemon.state.partySlots[3] = 9

-- Stands in for the BPARTY packet, which Net.lua parses and this harness does
-- not load. The switch menu reads only this, never state.owned.
local function bparty(rows)
    Battlemon.battle = Battlemon.battle or {}
    Battlemon.battle.party = {}
    for slot = 1, 6 do
        local r = rows[slot]
        if r then
            Battlemon.battle.party[slot] = {
                slot = slot, ownedId = r[1], hp = r[2], maxhp = r[3],
                level = r[4], active = r[5] or false, name = r[6], shiny = false,
            }
        end
    end
end

bparty({ { 7, 0, 18, 20, true, "Pikachu" },
         { 8, 22, 22, 30, false, "Zubat" },
         { 9, 8, 8, 2, false, "Abra" } })
Battlemon.net.P({ "P", "Pikachu", "0", "18", "1" })
Battlemon.net.MSG({ "MSG", "Pikachu fainted!" })
Battlemon.net.SWITCHNEED({ "SWITCHNEED" })
drain()
local downRow = BM_FIND("1.  Pikachu   Lv.20   |cffd05050FAINTED|r").bmParent
local liveRow = BM_FIND("2.  Zubat   Lv.30   22/22").bmParent
assertEq("switch prompt up, not the command menu", commands:IsShown(), false)
assertEq("the fainted slot cannot be picked", downRow.bmEnabled, false)
-- The bug this replaced: Zubat is fainted in state.owned, and reading that is
-- what left a whole roster red and unclickable with a switch still owed.
assertEq("a healthy slot can be picked", liveRow.bmEnabled, true)

local escape = BM_FIND("|cffff8080RUN FROM BATTLE|r")
assertEq("a forced switch offers a way out", escape ~= nil and escape.bmParent:IsShown(), true)

local sent = #Battlemon.sent
downRow:Click()
drain()
assertEq("clicking the fainted slot sends nothing", #Battlemon.sent, sent)
assertEq("still on the switch prompt", commands:IsShown(), false)

-- Leaving the battle page and coming back must not settle the debt either.
Battlemon.OpenPanel("home")
Battlemon.OpenPanel("battle")
drain()
assertEq("the switch is still owed after tabbing away", commands:IsShown(), false)

liveRow:Click()
assertEq("switching to a healthy slot is sent", Battlemon.sent[#Battlemon.sent], "SWITCH 2")
Battlemon.net.MSG({ "MSG", "Go! Zubat!" })
Battlemon.net.P({ "P", "Zubat", "22", "22", "2" })
bparty({ { 7, 0, 18, 20, false, "Pikachu" },
         { 8, 22, 22, 30, true, "Zubat" },
         { 9, 8, 8, 2, false, "Abra" } })
drain()
assertEq("command menu returns once a switch lands", commands:IsShown(), true)

-- Party edits are a server round-trip. Letting one through mid-fight showed a
-- new name in the switch menu while the battle still held the old Pokemon.
Battlemon.OpenPanel("party")
local partySave = BM_BUTTON(_G.BattlemonPartyFrame, "SAVE PARTY")
assertEq("party locked during a battle", partySave.bmEnabled, false)
Battlemon.sent = {}
partySave:Click()
assertEq("a locked party sends nothing", #Battlemon.sent, 0)
Battlemon.OpenPanel("battle")
drain()
Battlemon.After = realAfter

-- Ending the battle hands focus back to Home rather than leaving a blank shell.
Battlemon.battle = nil
Battlemon.battleActive = nil
Battlemon.PanelClosed("battle")
assertEq("home after the battle ends", shownPages(), "BattlemonHubFrame")
assertEq("battle tab disabled again", battleTab.bmEnabled, false)

-- Flip to separate windows via the checkbox the user actually clicks.
local cb = _G.BattlemonSplitCheck
assertEq("checkbox exists", cb ~= nil, true)
cb:SetChecked(true)
cb:Click()
assertEq("split mode stored", BattlemonDB.splitWindows, true)
assertEq("shell hidden", _G.BattlemonMainFrame:IsShown(), false)
assertEq("shell off the escape list", escCount("BattlemonMainFrame"), 0)
assertEq("hub back on the escape list", escCount("BattlemonHubFrame"), 1)
assertEq("hub detached", _G.BattlemonHubFrame:GetParent() == UIParent, true)
assertEq("hub draggable again", _G.BattlemonHubFrame:IsMovable(), true)
assertEq("hub is the open window", shownPages(), "BattlemonHubFrame")
assertEq("a detached window drags again", _G.BattlemonHubFrame:Drag(), true)

-- Separate windows stack rather than replace.
Battlemon.ShowDex()
assertEq("dex opens alongside the hub", shownPages(), "BattlemonHubFrame,BattlemonDexFrame")

-- And back again, mid-session, with pages already built.
cb:SetChecked(false)
cb:Click()
assertEq("unified mode stored", BattlemonDB.splitWindows, false)
assertEq("shell shown again", _G.BattlemonMainFrame:IsShown(), true)
assertEq("single page after returning", shownPages(), "BattlemonHubFrame")
assertEq("dex re-embedded", _G.BattlemonDexFrame:GetParent() ~= UIParent, true)

-- Toggling from the minimap button closes and reopens the whole shell.
Battlemon.ToggleHub()
assertEq("toggle closes the shell", _G.BattlemonMainFrame:IsShown(), false)
Battlemon.ToggleHub()
assertEq("toggle reopens the shell", _G.BattlemonMainFrame:IsShown(), true)

-- The party MOVES button still reaches the move manager.
Battlemon.OpenPanel("party")
partyMoves:Click()
assertEq("party MOVES opens the manager", shownPages(), "BattlemonMoveFrame")

-- The MOVES tab is clicked with nothing selected, so it must adopt the lead
-- rather than opening a manager with no Pokemon behind it.
Battlemon.sent = {}
Battlemon.OpenPanel("home")
BM_BUTTON(_G.BattlemonMainFrame, "MOVES"):Click()
assertEq("moves tab opens the page", shownPages(), "BattlemonMoveFrame")
assertEq("moves tab requests a pool", Battlemon.sent[#Battlemon.sent], "LEARNSET 7")

-- Starting a fight from the unified window switches to the battle page.
Battlemon.battleActive = true
Battlemon.battle = { player = { name = "Pikachu", hp = 10, maxhp = 10, moves = {} },
                     enemy = { name = "Diglett", hp = 10, maxhp = 10 } }
Battlemon.OpenPanel("battle")
assertEq("battle page from unified", shownPages(), "BattlemonFrame")

-- Starting a fight while in split mode opens the battle as its own window.
Battlemon.SetSplitMode(true)
assertEq("battle survives the switch to split", _G.BattlemonFrame:IsShown(), true)
Battlemon.SetSplitMode(false)
assertEq("battle survives the switch back", shownPages(), "BattlemonFrame")

-- Moves are a server-side no during a fight, and the UI has to agree.
Battlemon.ShowMoves(7)
assertEq("no move edits mid-fight", shownPages(), "BattlemonFrame")

-- The out-of-battle bag: pick a Revive, then the fainted Pokemon it targets.
-- Only a fainted row may be clicked, and only once an item is chosen.
Battlemon.battle = nil
Battlemon.battleActive = nil
Battlemon.state.bag.REVIVE = 2
Battlemon.Items.REVIVE = { name = "Revive", battle_use = "OnPokemon" }
Battlemon.Items.POKEBALL = { name = "Poké Ball", battle_use = "OnFoe" }
Battlemon.OpenPanel("bag")
assertEq("bag page visible", shownPages(), "BattlemonBagFrame")
Battlemon.sent = {}
BM_FIND("Zubat").bmParent:Click()
assertEq("no target until an item is chosen", #Battlemon.sent, 0)
BM_FIND("Revive"):GetParent():Click()
Battlemon.RefreshBag()
assertEq("a healthy Pokemon is not a revive target", BM_FIND("Abra").bmParent.usable, false)
BM_FIND("Zubat").bmParent:Click()
assertEq("reviving the fainted one is sent", Battlemon.sent[#Battlemon.sent], "BAGUSE REVIVE,8")

-- The real entry point: a wild encounter arriving with the addon closed.
Battlemon.battle = nil
Battlemon.battleActive = nil
Battlemon.OpenPanel("home")
Battlemon.HideMain()
assertEq("shell closed", _G.BattlemonMainFrame:IsShown(), false)
Battlemon.net.WILD({ "WILD" })
assertEq("a wild encounter opens the shell", _G.BattlemonMainFrame:IsShown(), true)
assertEq("a wild encounter shows the battle", shownPages(), "BattlemonFrame")
assertEq("battle tab enabled during the encounter", Battlemon.InBattle(), true)

return table.concat(log, "\n")
"""

CORE = ["Core/Util.lua", "Core/UI.lua"]
PANELS = [
    "UI/MainFrame.lua",
    "UI/HubFrame.lua",
    "UI/PartyFrame.lua",
    "UI/DexFrame.lua",
    "UI/MoveFrame.lua",
    "UI/ShopFrame.lua",
    "UI/BagFrame.lua",
    "UI/BattleFrame.lua",
]


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    root = sys.argv[1]
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(PRELUDE)
    lua.execute(STUBS)
    for rel in CORE + PANELS:
        path = os.path.join(root, rel.replace("/", os.sep))
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        try:
            lua.execute(src)
        except Exception as exc:
            print("LOAD FAIL", rel, "->", exc)
            return 1
        print("loaded", rel)
    print()
    try:
        print(lua.execute(DRIVE))
    except Exception as exc:
        print("DRIVE FAIL ->", exc)
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
