Battlemon = Battlemon or {}

local ui
local selectedId = 0
local ROW = 34
local VISIBLE = 11

local function ownedList()
    return Battlemon.GetSortedOwnedRows()
end

local function slotOf(ownedId)
    for s = 1, 6 do
        if Battlemon.state.partySlots[s] == ownedId then
            return s
        end
    end
end

local function editBlocked()
    if Battlemon.InBattle and Battlemon.InBattle() then
        Battlemon.Print("You can't rearrange your party during a battle.")
        return true
    end
    return false
end

local function refreshSortLabel()
    if ui and ui.sortBtn then
        ui.sortBtn.text:SetText("Sort: " .. Battlemon.SortModeLabel())
    end
end

-- Cache of the sorted owned-Pokemon list. GetSortedOwnedRows() rebuilds and
-- fully re-sorts the whole owned collection (IsFavorite() called on both
-- sides of every comparison) every time it's called. Scrolling calls
-- RefreshParty on every wheel tick/drag update but never changes the
-- collection or its sort order, so redoing that sort every tick is wasted
-- work that shows up as choppy scrolling. scrollOnly=true reuses the last
-- computed list instead.
local cachedList

function Battlemon.RefreshParty(scrollOnly)
    if not ui or not ui.frame:IsShown() then
        return
    end
    refreshSortLabel()
    local list
    if scrollOnly and cachedList then
        list = cachedList
    else
        list = ownedList()
        cachedList = list
    end
    FauxScrollFrame_Update(ui.scroll, #list, VISIBLE, ROW)
    local offset = FauxScrollFrame_GetOffset(ui.scroll) or 0
    for i = 1, VISIBLE do
        local row = list[offset + i]
        local btn = ui.rows[i]
        if row then
            btn:Show()
            Battlemon.PaintOwnedRow(btn, row, selectedId, slotOf(row.id), "party")
        else
            btn:Hide()
            btn.ownedId = nil
        end
    end
    if #list == 0 then
        ui.empty:Show()
    else
        ui.empty:Hide()
    end

    local locked = Battlemon.InBattle and Battlemon.InBattle()

    for s = 1, 6 do
        local slot = ui.slots[s]
        local row = Battlemon.state.owned[Battlemon.state.partySlots[s] or 0]
        slot.label:SetText(s == 1 and "LEAD" or ("SLOT " .. s))
        if row then
            slot.name:SetText(Battlemon.ShinyName(Battlemon.FormName(row.formId, row.name), row.shiny))
            slot.info:SetText("Lv." .. (row.level or 1) .. Battlemon.OwnedFaintTag(row)
                .. ((row.held or "") ~= "" and ("  |cffa8c8ff" .. (((Battlemon.Items or {})[row.held] or {}).name or row.held) .. "|r") or "")
                .. (row.id == (Battlemon.state.followerId or 0) and "  |cff80ff80FOLLOWS|r" or ""))
            Battlemon.SetPokemonTexture(slot.icon, "Front", Battlemon.FormSprite(row.formId, row.sprite), row.shiny)
            slot.icon:Show()
            if locked then
                Battlemon.Fill(slot.bg, 0.10, 0.11, 0.13, 1)
            else
                Battlemon.Fill(slot.bg, 0.13, 0.16, 0.20, 1)
            end
        else
            slot.name:SetText("(empty)")
            slot.info:SetText("")
            slot.icon:Hide()
            Battlemon.Fill(slot.bg, 0.09, 0.09, 0.12, 1)
        end
        slot.name:SetTextColor(locked and 0.62 or 0.94, locked and 0.64 or 0.95, locked and 0.70 or 0.98)
    end

    Battlemon.SetButtonEnabled(ui.moves, selectedId ~= 0 and not locked)
    Battlemon.SetButtonEnabled(ui.save, not locked)
    Battlemon.SetButtonEnabled(ui.favorite, selectedId ~= 0 and not locked)
    -- Following is cosmetic, so it also works mid-battle and for Pokémon that are not in the party.
    Battlemon.SetButtonEnabled(ui.follow, selectedId ~= 0)
    Battlemon.SetButtonEnabled(ui.item, selectedId ~= 0)
    if ui.follow then
        local following = selectedId ~= 0 and selectedId == (Battlemon.state.followerId or 0)
        ui.follow.text:SetText(following and "STOP FOLLOW" or "FOLLOW")
    end
    if ui.favorite then
        local fav = selectedId ~= 0 and Battlemon.IsFavorite(selectedId)
        ui.favorite.text:SetText(fav and "UNFAVORITE" or "FAVORITE")
    end

    if locked then
        ui.hint:SetText("|cffd0a050Your party is locked while a battle is running.|r Switch Pokémon from the battle menu.")
    elseif selectedId ~= 0 then
        local row = Battlemon.state.owned[selectedId]
        ui.hint:SetText(row
            and ("Selected " .. Battlemon.FormName(row.formId, row.name) .. " — click a slot to place it. Right-click a slot to clear it.")
            or "Click a Pokémon, then a slot.")
    else
        ui.hint:SetText("Click a Pokémon on the left, then click a slot. Slot 1 leads the battle.")
    end
end

local function assignToSlot(slot)
    if selectedId == 0 or editBlocked() then
        return
    end
    for i = 1, 6 do
        if Battlemon.state.partySlots[i] == selectedId then
            Battlemon.state.partySlots[i] = 0
        end
    end
    Battlemon.state.partySlots[slot] = selectedId
    Battlemon.RefreshParty()
end

local function build()
    if ui then
        return ui
    end
    local f = Battlemon.MakeWindow("BattlemonPartyFrame", 848, 552)

    local banner = f:CreateTexture(nil, "ARTWORK")
    banner:SetPoint("TOPLEFT", 4, -4)
    banner:SetPoint("TOPRIGHT", -4, -4)
    banner:SetHeight(62)
    banner:SetTexture(Battlemon.Media("bg_forest"))
    local shade = f:CreateTexture(nil, "ARTWORK")
    shade:SetAllPoints(banner)
    Battlemon.Fill(shade, 0, 0, 0, 0.45)

    local title = Battlemon.Font(f, 20, "", 1, 0.90, 0.40)
    title:SetPoint("TOP", 0, -18)
    title:SetText("Party")

    local hint = Battlemon.Font(f, 12, "", 0.82, 0.86, 0.92)
    hint:SetPoint("TOP", 0, -44)
    hint:SetWidth(780)
    hint:SetJustifyH("CENTER")

    local sortBtn = Battlemon.MakeTextButton(f, 160, 24, "Sort: Default", function()
        Battlemon.CyclePartySort()
        refreshSortLabel()
        Battlemon.RefreshParty()
        if Battlemon.RefreshTeams then
            Battlemon.RefreshTeams()
        end
    end, 0.14, 0.15, 0.20)
    sortBtn:SetPoint("TOPLEFT", 22, -72)
    sortBtn.text:SetFont("Fonts\\FRIZQT__.TTF", 12, "")

    local listFrame = CreateFrame("Frame", nil, f)
    listFrame:SetPoint("TOPLEFT", 22, -100)
    listFrame:SetSize(380, VISIBLE * ROW + 6)
    local listBg = listFrame:CreateTexture(nil, "BACKGROUND")
    listBg:SetAllPoints()
    Battlemon.Fill(listBg, 0.03, 0.04, 0.06, 0.9)

    local empty = Battlemon.Font(listFrame, 13, "", 0.7, 0.72, 0.78)
    empty:SetPoint("CENTER")
    empty:SetText("No Pokémon caught yet.")

    local scroll = CreateFrame("ScrollFrame", "BattlemonPartyScroll", listFrame, "FauxScrollFrameTemplate")
    scroll:SetPoint("TOPLEFT", 2, -3)
    scroll:SetPoint("BOTTOMRIGHT", -26, 3)
    scroll:SetScript("OnVerticalScroll", function(self, offset)
        FauxScrollFrame_OnVerticalScroll(self, offset, ROW, function() Battlemon.RefreshParty(true) end)
    end)

    local rows = {}
    for i = 1, VISIBLE do
        local btn = Battlemon.MakeOwnedRow(listFrame, ROW, function(ownedId)
            selectedId = ownedId
            Battlemon.RefreshParty()
        end, function(ownedId)
            if ownedId and ownedId > 0 then
                Battlemon.ToggleFavorite(ownedId)
                Battlemon.RefreshParty()
                if Battlemon.RefreshTeams then
                    Battlemon.RefreshTeams()
                end
            end
        end)
        btn:SetSize(348, ROW - 2)
        btn:SetPoint("TOPLEFT", 4, -((i - 1) * ROW) - 4)
        rows[i] = btn
    end

    local slots = {}
    for s = 1, 6 do
        local btn = CreateFrame("Button", nil, f)
        btn:SetSize(390, 50)
        btn:SetPoint("TOPRIGHT", -22, -78 - ((s - 1) * 56))
        btn.bg = btn:CreateTexture(nil, "BACKGROUND")
        btn.bg:SetAllPoints()
        Battlemon.Fill(btn.bg, 0.09, 0.09, 0.12, 1)
        btn.icon = btn:CreateTexture(nil, "ARTWORK")
        btn.icon:SetSize(38, 38)
        btn.icon:SetPoint("LEFT", 46, 0)
        btn.label = Battlemon.Font(btn, 11, "", 1, 0.82, 0.30)
        btn.label:SetPoint("LEFT", 8, 0)
        btn.label:SetJustifyH("LEFT")
        btn.name = Battlemon.Font(btn, 14, "", 0.94, 0.95, 0.98)
        btn.name:SetPoint("LEFT", 92, 0)
        btn.name:SetJustifyH("LEFT")
        btn.name:SetWidth(220)
        btn.info = Battlemon.Font(btn, 12, "", 0.80, 0.84, 0.90)
        btn.info:SetPoint("RIGHT", -10, 0)
        btn.info:SetJustifyH("RIGHT")
        btn:RegisterForClicks("LeftButtonUp", "RightButtonUp")
        btn:SetScript("OnClick", function(_, button)
            if button == "RightButton" then
                if editBlocked() then
                    return
                end
                Battlemon.state.partySlots[s] = 0
                Battlemon.RefreshParty()
                return
            end
            assignToSlot(s)
        end)
        btn:SetScript("OnEnter", function(self)
            if not Battlemon.state.owned[Battlemon.state.partySlots[s] or 0] then
                Battlemon.Fill(self.bg, 0.16, 0.16, 0.20, 1)
            else
                Battlemon.Fill(self.bg, 0.19, 0.23, 0.28, 1)
            end
        end)
        btn:SetScript("OnLeave", function()
            Battlemon.RefreshParty()
        end)
        slots[s] = btn
    end

    local save = Battlemon.MakeTextButton(f, 150, 44, "SAVE PARTY", function()
        if editBlocked() then
            return
        end
        local parts = {}
        for i = 1, 6 do
            parts[i] = tostring(Battlemon.state.partySlots[i] or 0)
        end
        Battlemon.Send("SETPARTY", table.concat(parts, ","))
        Battlemon.Print("Party saved.")
    end, 0.20, 0.30, 0.16)
    save:SetPoint("BOTTOMLEFT", 40, 28)

    local favorite = Battlemon.MakeTextButton(f, 120, 44, "FAVORITE", function()
        if selectedId == 0 or editBlocked() then
            return
        end
        Battlemon.ToggleFavorite(selectedId)
        Battlemon.RefreshParty()
        if Battlemon.RefreshTeams then
            Battlemon.RefreshTeams()
        end
    end, 0.18, 0.24, 0.34)
    favorite:SetPoint("LEFT", save, "RIGHT", 12, 0)

    local moves = Battlemon.MakeTextButton(f, 110, 44, "MOVES", function()
        Battlemon.ShowMoves(selectedId)
    end, 0.18, 0.24, 0.34)
    moves:SetPoint("LEFT", favorite, "RIGHT", 12, 0)

    local follow = Battlemon.MakeTextButton(f, 130, 44, "FOLLOW", function()
        if selectedId == 0 then
            return
        end
        local following = selectedId == (Battlemon.state.followerId or 0)
        Battlemon.Send("FOLLOW", following and "0" or tostring(selectedId))
    end, 0.18, 0.30, 0.24)
    follow:SetPoint("LEFT", moves, "RIGHT", 12, 0)

    -- Trade with the player you are targeting (or use /bm trade <name>).
    local tradeBtn = Battlemon.MakeTextButton(f, 100, 44, "TRADE", function()
        Battlemon.StartTrade()
    end, 0.30, 0.24, 0.16)
    tradeBtn:SetPoint("LEFT", follow, "RIGHT", 12, 0)

    -- Give the selected Pokémon an item to hold, or take its item back.
    local itemBtn = Battlemon.MakeTextButton(f, 100, 44, "ITEM", function()
        if selectedId ~= 0 then
            Battlemon.ShowItemPicker(selectedId)
        end
    end, 0.24, 0.22, 0.34)
    itemBtn:SetPoint("LEFT", tradeBtn, "RIGHT", 12, 0)

    f:SetScript("OnShow", function()
        Battlemon.Send("PARTY")
        Battlemon.Send("LEARNQ")
        Battlemon.RefreshParty()
    end)

    ui = { frame = f, scroll = scroll, rows = rows, slots = slots, hint = hint,
           empty = empty, moves = moves, save = save, favorite = favorite, follow = follow, item = itemBtn,
           sortBtn = sortBtn }
    return ui
end

function Battlemon.BuildParty()
    return build().frame
end

function Battlemon.ShowParty()
    Battlemon.EnsureData()
    Battlemon.OpenPanel("party")
    Battlemon.RefreshParty()
end
