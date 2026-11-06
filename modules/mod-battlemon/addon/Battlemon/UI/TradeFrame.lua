Battlemon = Battlemon or {}

-- Pokémon-for-Pokémon trading. Everything is decided by the server (it owns the offers and both confirmations);
-- this window only shows its state and sends requests: TRADE INVITE/ACCEPT/DECLINE/OFFER/CONFIRM/CANCEL.
-- Changing an offer cancels both confirmations on the server, so the buttons here simply mirror what it reports.

local ui, invite
local selectedId = 0
local ROW = 34
local VISIBLE = 9

Battlemon.state.trade = Battlemon.state.trade or {}

local function trade()
    return Battlemon.state.trade
end

local function send(verb, arg)
    Battlemon.Send("TRADE", arg and (verb .. "\t" .. arg) or verb)
end

local function describe(mon)
    if not mon then
        return "Nothing offered yet."
    end
    local moves = {}
    for i = 1, 4 do
        if mon.moves[i] and mon.moves[i] ~= "" then
            local def = (Battlemon.MovesByInternal or {})[mon.moves[i]]
            moves[#moves + 1] = (def and def.name) or mon.moves[i]
        end
    end
    return string.format("Lv.%d  %s\n%s", mon.level, mon.gender == "M" and "Male" or (mon.gender == "F" and "Female" or ""),
        table.concat(moves, ", "))
end

local function paintCard(card, mon)
    if mon then
        card.name:SetText(Battlemon.ShinyName(Battlemon.FormName(mon.formId, mon.name), mon.shiny))
        Battlemon.SetPokemonTexture(card.icon, "Front", Battlemon.FormSprite(mon.formId, ""), mon.shiny)
        card.icon:Show()
    else
        card.name:SetText("(nothing)")
        card.icon:Hide()
    end
    card.info:SetText(describe(mon))
end

function Battlemon.RefreshTrade()
    if not ui or not ui.frame:IsShown() then
        return
    end
    local t = trade()
    ui.title:SetText("Trade with " .. (t.partner or "?"))
    paintCard(ui.mine, t.mine)
    paintCard(ui.theirs, t.theirs)
    ui.theirsLabel:SetText((t.partner or "They") .. " offers")

    local list = Battlemon.GetSortedOwnedRows()
    FauxScrollFrame_Update(ui.scroll, #list, VISIBLE, ROW)
    local offset = FauxScrollFrame_GetOffset(ui.scroll) or 0
    for i = 1, VISIBLE do
        local row = list[offset + i]
        local btn = ui.rows[i]
        if row then
            btn:Show()
            Battlemon.PaintOwnedRow(btn, row, selectedId, nil, "party")
        else
            btn:Hide()
            btn.ownedId = nil
        end
    end

    local anything = t.mine ~= nil or t.theirs ~= nil
    Battlemon.SetButtonEnabled(ui.offer, selectedId ~= 0)
    Battlemon.SetButtonEnabled(ui.clear, t.mine ~= nil)
    Battlemon.SetButtonEnabled(ui.confirm, anything and not t.myConfirm)
    if t.myConfirm and t.theirConfirm then
        ui.status:SetText("Completing the trade…")
    elseif t.myConfirm then
        ui.status:SetText("You confirmed. Waiting for " .. (t.partner or "them") .. "…")
    elseif t.theirConfirm then
        ui.status:SetText((t.partner or "They") .. " confirmed. Check the offers, then confirm.")
    elseif anything then
        ui.status:SetText("Both of you must confirm. Changing an offer cancels the confirmations.")
    else
        ui.status:SetText("Pick a Pokémon on the left and press OFFER.")
    end
end

local function build()
    if ui then
        return ui
    end
    local f = Battlemon.MakeWindow("BattlemonTradeFrame", 780, 540)
    local title = Battlemon.Font(f, 20, "", 1, 0.90, 0.40)
    title:SetPoint("TOP", 0, -16)

    local listFrame = CreateFrame("Frame", nil, f)
    listFrame:SetPoint("TOPLEFT", 22, -58)
    listFrame:SetSize(360, VISIBLE * ROW + 6)
    local bg = listFrame:CreateTexture(nil, "BACKGROUND")
    bg:SetAllPoints()
    Battlemon.Fill(bg, 0.03, 0.04, 0.06, 0.9)
    local scroll = CreateFrame("ScrollFrame", "BattlemonTradeScroll", listFrame, "FauxScrollFrameTemplate")
    scroll:SetPoint("TOPLEFT", 2, -3)
    scroll:SetPoint("BOTTOMRIGHT", -26, 3)
    scroll:SetScript("OnVerticalScroll", function(self, offset)
        FauxScrollFrame_OnVerticalScroll(self, offset, ROW, function() Battlemon.RefreshTrade() end)
    end)
    local rows = {}
    for i = 1, VISIBLE do
        local btn = Battlemon.MakeOwnedRow(listFrame, ROW, function(ownedId)
            selectedId = ownedId
            Battlemon.RefreshTrade()
        end, nil)
        btn:SetSize(328, ROW - 2)
        btn:SetPoint("TOPLEFT", 4, -((i - 1) * ROW) - 4)
        rows[i] = btn
    end

    local function card(label, y)
        local c = CreateFrame("Frame", nil, f)
        c:SetSize(340, 120)
        c:SetPoint("TOPRIGHT", -22, y)
        local cbg = c:CreateTexture(nil, "BACKGROUND")
        cbg:SetAllPoints()
        Battlemon.Fill(cbg, 0.09, 0.11, 0.15, 1)
        c.label = Battlemon.Font(c, 12, "", 1, 0.82, 0.30)
        c.label:SetPoint("TOPLEFT", 10, -8)
        c.label:SetText(label)
        c.icon = c:CreateTexture(nil, "ARTWORK")
        c.icon:SetSize(64, 64)
        c.icon:SetPoint("LEFT", 12, -8)
        c.name = Battlemon.Font(c, 15, "", 0.94, 0.95, 0.98)
        c.name:SetPoint("TOPLEFT", 90, -30)
        c.name:SetJustifyH("LEFT")
        c.name:SetWidth(240)
        c.info = Battlemon.Font(c, 12, "", 0.80, 0.84, 0.90)
        c.info:SetPoint("TOPLEFT", 90, -54)
        c.info:SetJustifyH("LEFT")
        c.info:SetJustifyV("TOP")
        c.info:SetWidth(240)
        return c
    end
    local mine = card("You offer", -58)
    local theirs = card("They offer", -192)
    local theirsLabel = theirs.label

    local offer = Battlemon.MakeTextButton(f, 170, 36, "OFFER SELECTED", function()
        if selectedId ~= 0 then
            send("OFFER", tostring(selectedId))
        end
    end, 0.18, 0.30, 0.24)
    offer:SetPoint("TOPLEFT", 22, -58 - VISIBLE * ROW - 18)
    local clear = Battlemon.MakeTextButton(f, 150, 36, "CLEAR OFFER", function()
        send("OFFER", "0")
    end, 0.18, 0.24, 0.34)
    clear:SetPoint("LEFT", offer, "RIGHT", 10, 0)

    local status = Battlemon.Font(f, 13, "", 0.92, 0.94, 0.98)
    status:SetPoint("TOPRIGHT", -22, -340)
    status:SetWidth(340)
    status:SetJustifyH("LEFT")

    local confirm = Battlemon.MakeTextButton(f, 200, 46, "CONFIRM TRADE", function()
        send("CONFIRM")
    end, 0.20, 0.34, 0.16)
    confirm:SetPoint("BOTTOMRIGHT", -22, 24)
    local cancel = Battlemon.MakeTextButton(f, 150, 46, "CANCEL TRADE", function()
        send("CANCEL")
    end, 0.34, 0.18, 0.16)
    cancel:SetPoint("RIGHT", confirm, "LEFT", -12, 0)

    f:SetScript("OnShow", function()
        Battlemon.Send("PARTY")
        send("STATE")
        Battlemon.RefreshTrade()
    end)
    f:Hide()
    ui = { frame = f, title = title, scroll = scroll, rows = rows, mine = mine, theirs = theirs,
           theirsLabel = theirsLabel, offer = offer, clear = clear, confirm = confirm, status = status }
    return ui
end

local function buildInvite()
    if invite then
        return invite
    end
    local f = Battlemon.MakeWindow("BattlemonTradeInvite", 380, 150)
    f:ClearAllPoints()
    f:SetPoint("TOP", 0, -140)
    local text = Battlemon.Font(f, 15, "", 0.94, 0.95, 0.98)
    text:SetPoint("TOP", 0, -26)
    text:SetWidth(340)
    local accept = Battlemon.MakeTextButton(f, 150, 40, "ACCEPT", function()
        f:Hide()
        send("ACCEPT")
    end, 0.20, 0.34, 0.16)
    accept:SetPoint("BOTTOMLEFT", 24, 22)
    local decline = Battlemon.MakeTextButton(f, 150, 40, "DECLINE", function()
        f:Hide()
        send("DECLINE")
    end, 0.34, 0.18, 0.16)
    decline:SetPoint("BOTTOMRIGHT", -24, 22)
    f:Hide()
    invite = { frame = f, text = text }
    return invite
end

-- Slash and button entry point. With no name it uses your target, if that is a player.
function Battlemon.StartTrade(name)
    name = name and string.gsub(name, "^%s*(.-)%s*$", "%1") or ""
    if name == "" and UnitExists and UnitExists("target") and UnitIsPlayer("target") then
        name = UnitName("target") or ""
    end
    if name == "" then
        Battlemon.Print("Usage: |cffffff00/bm trade <player>|r (or target a player first).")
        return
    end
    send("INVITE", name)
end

-- Server messages -----------------------------------------------------------------------------------------------

Battlemon.OnNet("TRADEINVITE", function(a)
    local w = buildInvite()
    w.text:SetText((a[2] or "Someone") .. " wants to trade Pokémon with you.")
    w.frame:Show()
end)

Battlemon.OnNet("TRADE", function(a)
    local t = trade()
    t.partner = a[2]
    t.myConfirm = a[3] == "1"
    t.theirConfirm = a[4] == "1"
    if invite then
        invite.frame:Hide()
    end
    local w = build()
    if not w.frame:IsShown() then
        selectedId = 0
        w.frame:Show()
    end
    Battlemon.RefreshTrade()
end)

Battlemon.OnNet("TRADEMON", function(a)
    local t = trade()
    local mon
    if a[3] then
        mon = { formId = tonumber(a[3]) or 0, level = tonumber(a[4]) or 1, shiny = (a[5] == "1"), gender = a[6] or "N",
                moves = { a[7] or "", a[8] or "", a[9] or "", a[10] or "" }, name = a[11] or "" }
    end
    if a[2] == "M" then
        t.mine = mon
    else
        t.theirs = mon
    end
    Battlemon.RefreshTrade()
end)

Battlemon.OnNet("TRADEEND", function(a)
    Battlemon.state.trade = {}
    selectedId = 0
    if ui then
        ui.frame:Hide()
    end
    if invite then
        invite.frame:Hide()
    end
    Battlemon.Print("Pokémon trade: " .. (a[2] or "ended."))
end)
