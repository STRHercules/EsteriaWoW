Battlemon = Battlemon or {}

-- The all-in-one shell. Every page is one of the existing panel windows, adopted
-- as a child and stripped of its own chrome, so there is a single copy of each
-- layout serving both the unified window and the separate-windows mode.

local PAD = 10
-- A bare strip above the tabs. The pages cover the whole content area and eat
-- their own mouse input, so without it there is nowhere left to grab and drag.
local TITLE_H = 24
local TAB_H = 28
local TAB_GAP = 2
local TAB_DROP = 8
-- Fits the widest page (Pokedex, 848x552) and the battle scene (780x540).
local CONTENT_W, CONTENT_H = 848, 552
local FRAME_W = CONTENT_W + PAD * 2
local FRAME_H = CONTENT_H + TITLE_H + TAB_H + TAB_DROP + PAD * 2

local SHELL_NAME = "BattlemonMainFrame"

local main
local current
local panels = {}

local PAGES = {
    { key = "home",   label = "HOME",
      build = function() return Battlemon.BuildHub() end,
      refresh = function() return Battlemon.RefreshHub and Battlemon.RefreshHub() end },
    { key = "party",  label = "PARTY",
      build = function() return Battlemon.BuildParty() end,
      refresh = function() return Battlemon.RefreshParty and Battlemon.RefreshParty() end },
    { key = "teams",  label = "TEAMS",
      build = function() return Battlemon.BuildTeams() end,
      refresh = function() return Battlemon.RefreshTeams and Battlemon.RefreshTeams() end },
    -- The move manager needs a Pokemon chosen and its pool requested, which is
    -- what ShowMoves does; opening the bare page would show an empty manager.
    { key = "moves",  label = "MOVES",
      build = function() return Battlemon.BuildMoves() end,
      open = function() return Battlemon.ShowMoves() end,
      refresh = function() return Battlemon.RefreshMoves and Battlemon.RefreshMoves() end },
    { key = "dex",    label = "POKéDEX",
      build = function() return Battlemon.BuildDex() end,
      refresh = function() return Battlemon.RefreshDex and Battlemon.RefreshDex() end },
    { key = "bag",    label = "BAG",
      build = function() return Battlemon.BuildBag() end,
      refresh = function() return Battlemon.RefreshBag and Battlemon.RefreshBag() end },
    { key = "shop",   label = "SHOP",
      build = function() return Battlemon.BuildShop() end,
      refresh = function() return Battlemon.RefreshShop and Battlemon.RefreshShop() end },
    { key = "battle", label = "BATTLE", battleOnly = true,
      build = function() return Battlemon.BuildBattle() end },
}

local function pageFor(key)
    for i = 1, #PAGES do
        if PAGES[i].key == key then
            return PAGES[i]
        end
    end
end

function Battlemon.Unified()
    BattlemonDB = BattlemonDB or {}
    return BattlemonDB.splitWindows ~= true
end

local function battleLive()
    return Battlemon.InBattle and Battlemon.InBattle() or false
end

-- Unified mode hides each page's X; closing the shell (X or Escape) must RUN if a
-- fight is live. Split-window toggles suppress this so the battle panel survives.
local function hideShell(suppressForfeit)
    if not main then
        return
    end
    if suppressForfeit then
        main.frame.bmSuppressForfeit = true
    end
    main.frame:Hide()
end

-- Adopting a panel: it keeps its own size and centres in the content area, so a
-- layout built against a fixed frame size still lands where its author put it.
local function embed(frame, host)
    if not frame or frame.bmEmbedded then
        return
    end
    frame:SetParent(host)
    frame:ClearAllPoints()
    frame:SetPoint("CENTER", host, "CENTER", 0, 0)
    -- Dragging must go dead as well as being pointless: StartMoving on a frame
    -- that is no longer movable throws.
    frame:RegisterForDrag()
    frame:SetMovable(false)
    frame:SetClampedToScreen(false)
    frame:SetToplevel(false)
    frame:SetFrameStrata(host:GetFrameStrata())
    if frame.bmEdge then frame.bmEdge:Hide() end
    if frame.bmBg then frame.bmBg:Hide() end
    if frame.bmClose then frame.bmClose:Hide() end
    Battlemon.EscClose(frame.bmName, false)
    frame.bmEmbedded = true
end

local function detach(frame)
    if not frame or not frame.bmEmbedded then
        return
    end
    frame:Hide()
    frame:SetParent(UIParent)
    frame:ClearAllPoints()
    frame:SetPoint("CENTER")
    frame:SetMovable(true)
    frame:SetClampedToScreen(true)
    frame:RegisterForDrag("LeftButton")
    frame:SetToplevel(true)
    frame:SetFrameStrata("DIALOG")
    if frame.bmEdge then frame.bmEdge:Show() end
    if frame.bmBg then frame.bmBg:Show() end
    if frame.bmClose then frame.bmClose:Show() end
    Battlemon.EscClose(frame.bmName, true)
    frame.bmEmbedded = nil
end

local function updateTabs()
    if not main then
        return
    end
    local st = Battlemon.state or {}
    main.purse:SetText(string.format("Poké Balls |cffffffff%d|r    Points |cffffffff%d|r",
        (st.bag and st.bag.POKEBALL) or 0, st.points or 0))
    for i = 1, #PAGES do
        local page = PAGES[i]
        local btn = main.tabs[page.key]
        if btn then
            Battlemon.SetButtonEnabled(btn, (not page.battleOnly) or battleLive())
            if page.key == current then
                btn:SetTint(0.44, 0.28, 0.52)
            else
                btn:SetTint(0.16, 0.17, 0.24)
            end
        end
    end
end

local function buildShell()
    if main then
        return main
    end
    local f = Battlemon.MakeWindow(SHELL_NAME, FRAME_W, FRAME_H)

    local titleBar = f:CreateTexture(nil, "ARTWORK")
    titleBar:SetPoint("TOPLEFT", 4, -4)
    titleBar:SetPoint("TOPRIGHT", -4, -4)
    titleBar:SetHeight(TITLE_H + 2)
    Battlemon.Fill(titleBar, 0.11, 0.09, 0.14, 1)

    local title = Battlemon.Font(f, 14, "", 1, 0.88, 0.38)
    title:SetPoint("TOPLEFT", 14, -9)
    title:SetText("Battlemon")

    -- Worth carrying in the title bar: with one window the wallet would
    -- otherwise only be readable on Home and in the shop.
    local purse = Battlemon.Font(f, 12, "", 0.86, 0.90, 0.96)
    purse:SetPoint("TOPRIGHT", -36, -9)
    purse:SetJustifyH("RIGHT")

    local tabs = {}
    local n = #PAGES
    local tw = math.floor((CONTENT_W - TAB_GAP * (n - 1)) / n)
    -- Rounding leaves a few pixels over; spend them on the outer margins so the
    -- strip stays centred on the content below it.
    local x0 = PAD + math.floor((CONTENT_W - (n * tw + (n - 1) * TAB_GAP)) / 2)
    for i = 1, n do
        local page = PAGES[i]
        local btn = Battlemon.MakeTextButton(f, tw, TAB_H, page.label, function()
            if page.open then
                page.open()
            else
                Battlemon.OpenPanel(page.key)
            end
        end, 0.16, 0.17, 0.24)
        btn:SetPoint("TOPLEFT", x0 + (i - 1) * (tw + TAB_GAP), -(PAD + TITLE_H))
        btn.text:SetFont("Fonts\\FRIZQT__.TTF", 13, "")
        tabs[page.key] = btn
    end

    local content = CreateFrame("Frame", nil, f)
    content:SetSize(CONTENT_W, CONTENT_H)
    content:SetPoint("TOPLEFT", PAD, -(PAD + TITLE_H + TAB_H + TAB_DROP))
    local contentBg = content:CreateTexture(nil, "BACKGROUND")
    contentBg:SetAllPoints()
    Battlemon.Fill(contentBg, 0.03, 0.04, 0.06, 0.92)

    f:SetScript("OnHide", function(self)
        if self.bmSuppressForfeit then
            self.bmSuppressForfeit = nil
            return
        end
        if battleLive() and Battlemon.ForfeitBattle then
            Battlemon.ForfeitBattle()
        end
    end)
    f.bmClose:SetScript("OnClick", function()
        f:Hide()
    end)

    main = { frame = f, content = content, tabs = tabs, purse = purse }
    return main
end

local function panelFor(page)
    local f = panels[page.key]
    if not f then
        f = page.build()
        if not f then
            return nil
        end
        panels[page.key] = f
        f:Hide()
    end
    if Battlemon.Unified() then
        buildShell()
        embed(f, main.content)
    end
    return f
end

-- The single entry point every Show* funnels into. In split mode it is just
-- "show that window"; in unified mode it raises the shell and swaps the page.
function Battlemon.OpenPanel(key)
    local page = pageFor(key)
    if not page then
        return nil
    end
    if not Battlemon.Unified() then
        local f = panelFor(page)
        if f then
            f:Show()
        end
        return f
    end

    buildShell()
    main.frame:Show()
    local f = panelFor(page)
    if not f then
        return nil
    end
    if current and current ~= key and panels[current] then
        panels[current]:Hide()
    end
    current = key
    f:Show()
    updateTabs()
    if page.refresh then
        pcall(page.refresh)
    end
    return f
end

-- A page that hides itself (a finished battle, mostly) would leave the shell
-- showing an empty content area, so hand focus back to Home.
function Battlemon.PanelClosed(key)
    if not main or not Battlemon.Unified() or current ~= key then
        return
    end
    if main.frame:IsShown() then
        Battlemon.OpenPanel("home")
    else
        current = nil
    end
end

function Battlemon.MainShown()
    return (main ~= nil) and main.frame:IsShown() and true or false
end

function Battlemon.HideMain()
    hideShell(false)
end

function Battlemon.RefreshMain()
    if main and main.frame:IsShown() then
        updateTabs()
    end
end

function Battlemon.SetSplitMode(on)
    BattlemonDB = BattlemonDB or {}
    local want = on and true or false
    if BattlemonDB.splitWindows == want then
        return
    end
    BattlemonDB.splitWindows = want

    local was = current
    if want then
        if main then
            hideShell(true)
            Battlemon.EscClose(SHELL_NAME, false)
        end
        for _, f in pairs(panels) do
            detach(f)
        end
        current = nil
        Battlemon.ShowHub()
        -- Detaching hid every panel, which would abandon a fight in progress.
        if battleLive() and panels.battle then
            panels.battle:Show()
        end
    else
        buildShell()
        Battlemon.EscClose(SHELL_NAME, true)
        for _, f in pairs(panels) do
            f:Hide()
            embed(f, main.content)
        end
        current = nil
        Battlemon.OpenPanel(battleLive() and "battle" or (was or "home"))
    end
end
