Battlemon = Battlemon or {}

local ui
local ownedId = 0
local picks = { "", "", "", "" }
local selectedSlot = 1
local filter = ""
local freeOnly = false
local ROW = 24
local VISIBLE = 15

-- The server refuses move changes mid-battle; mirror that in the UI so the
-- button never looks available when it isn't. BattleFrame owns the answer.
local function inBattle()
    return Battlemon.InBattle and Battlemon.InBattle() or false
end

-- Ignore a pool that belongs to a Pokemon we are no longer looking at.
local function learnset()
    local ls = Battlemon.state.learnset
    if not ls or ls.ownedId ~= ownedId then
        return { ownedId = ownedId, cost = 0, moves = {}, ready = false }
    end
    return ls
end

local function moveDef(internal)
    return (Battlemon.MovesByInternal or {})[internal or ""]
end

local function moveLabel(internal)
    local mv = moveDef(internal)
    return (mv and mv.name) or internal or ""
end

local function pointsLeft()
    return Battlemon.state.points or 0
end

-- What this set of picks would cost right now: tutor moves that have never been
-- paid for on this Pokemon, and only the ones actually slotted.
local function pendingCost()
    local ls = learnset()
    local cost = 0
    for i = 1, 4 do
        if picks[i] ~= "" then
            for _, m in ipairs(ls.moves or {}) do
                if m.internal == picks[i] and m.tutor and not m.paid then
                    cost = cost + (ls.cost or 0)
                end
            end
        end
    end
    return cost
end

local function isPicked(internal)
    for i = 1, 4 do
        if picks[i] == internal then
            return i
        end
    end
end

local function resetPicks()
    local row = (Battlemon.state.owned or {})[ownedId]
    for i = 1, 4 do
        picks[i] = (row and row.move and row.move[i]) or ""
    end
    selectedSlot = 1
end

local function poolEntries()
    local ls = learnset()
    local needle = string.lower(filter)
    local out = {}
    for _, m in ipairs(ls.moves or {}) do
        local mv = moveDef(m.internal)
        local name = (mv and mv.name) or m.internal
        local free = (not m.tutor) or m.paid
        if (not freeOnly or free)
            and (needle == "" or string.find(string.lower(name), needle, 1, true)
                or (mv and mv.type and string.find(string.lower(mv.type), needle, 1, true))) then
            table.insert(out, { entry = m, def = mv, name = name, free = free })
        end
    end
    table.sort(out, function(a, b)
        if a.free ~= b.free then
            return a.free
        end
        if a.free and (a.entry.level or 0) ~= (b.entry.level or 0) then
            return (a.entry.level or 0) < (b.entry.level or 0)
        end
        return a.name < b.name
    end)
    return out
end

local function assign(internal)
    local at = isPicked(internal)
    if at then
        picks[at] = ""
    else
        picks[selectedSlot] = internal
        selectedSlot = (selectedSlot % 4) + 1
    end
    Battlemon.RefreshMoves()
end

function Battlemon.RefreshMoves()
    if not ui or not ui.frame:IsShown() then
        return
    end
    local ls = learnset()
    local row = (Battlemon.state.owned or {})[ownedId]

    if row then
        ui.title:SetText(Battlemon.ShinyName(Battlemon.FormName(row.formId, row.name), row.shiny))
        ui.sub:SetText(string.format("Level %d   ·   |cffffd45a%d|r points   ·   tutor move |cffffd45a%d|r",
            row.level or 1, pointsLeft(), ls.cost or 0))
        Battlemon.SetPokemonTexture(ui.icon, "Front", Battlemon.FormSprite(row.formId, row.sprite), row.shiny)
        ui.icon:Show()
    else
        ui.title:SetText("Moves")
        ui.sub:SetText("")
        ui.icon:Hide()
    end

    for i = 1, 4 do
        local btn = ui.slots[i]
        local mv = moveDef(picks[i])
        if picks[i] == "" then
            btn.name:SetText("(empty)")
            btn.name:SetTextColor(0.55, 0.56, 0.60)
            btn.info:SetText("")
        else
            btn.name:SetText(moveLabel(picks[i]))
            btn.name:SetTextColor(Battlemon.TypeRGB(mv and mv.type))
            btn.info:SetText(mv and string.format("%s   ·   Pow %s   ·   PP %s",
                mv.category or "", tostring(mv.power or "-"), tostring(mv.pp or "-")) or "")
        end
        if i == selectedSlot then
            Battlemon.Fill(btn.bg, 0.34, 0.28, 0.10, 1)
        else
            Battlemon.Fill(btn.bg, 0.11, 0.12, 0.16, 1)
        end
    end

    local list = poolEntries()
    FauxScrollFrame_Update(ui.scroll, #list, VISIBLE, ROW)
    local offset = FauxScrollFrame_GetOffset(ui.scroll) or 0
    for i = 1, VISIBLE do
        local e = list[offset + i]
        local btn = ui.rows[i]
        if e then
            btn:Show()
            btn.internal = e.entry.internal
            btn.name:SetText(e.name)
            btn.name:SetTextColor(Battlemon.TypeRGB(e.def and e.def.type))
            local mv = e.def
            btn.info:SetText(mv and string.format("%s  ·  %s  ·  Pow %s  ·  PP %s",
                mv.type or "", mv.category or "", tostring(mv.power or "-"), tostring(mv.pp or "-")) or "")
            if not e.entry.tutor then
                -- Level 0 is the catalog's marker for a move known on evolution.
                local lv = e.entry.level or 1
                btn.tag:SetText(lv == 0 and "evo" or ("Lv." .. tostring(lv)))
                btn.tag:SetTextColor(0.62, 0.86, 0.62)
            elseif e.entry.paid then
                btn.tag:SetText("owned")
                btn.tag:SetTextColor(0.62, 0.86, 0.62)
            else
                btn.tag:SetText(tostring(ls.cost or 0) .. " pts")
                btn.tag:SetTextColor(1, 0.82, 0.36)
            end
            if isPicked(e.entry.internal) then
                Battlemon.Fill(btn.bg, 0.16, 0.26, 0.16, 1)
            else
                Battlemon.Fill(btn.bg, 0.08, 0.09, 0.12, 1)
            end
        else
            btn:Hide()
            btn.internal = nil
        end
    end

    local cost = pendingCost()
    if not ls.ready then
        ui.hint:SetText("Loading move pool...")
    elseif cost > pointsLeft() then
        ui.hint:SetText(string.format("|cffff6060Costs %d points, you have %d.|r", cost, pointsLeft()))
    elseif cost > 0 then
        ui.hint:SetText(string.format("Saving will spend |cffffd45a%d|r points.", cost))
    else
        ui.hint:SetText("Click a slot, then a move. Click a picked move again to clear it.")
    end
    Battlemon.SetButtonEnabled(ui.save, ls.ready and cost <= pointsLeft())
    ui.freeBtn.text:SetText(freeOnly and "ALL MOVES" or "FREE ONLY")
end

local function build()
    if ui then
        return ui
    end
    local f = Battlemon.MakeWindow("BattlemonMoveFrame", 848, 552)

    local banner = f:CreateTexture(nil, "ARTWORK")
    banner:SetPoint("TOPLEFT", 4, -4)
    banner:SetPoint("TOPRIGHT", -4, -4)
    banner:SetHeight(62)
    banner:SetTexture(Battlemon.Media("bg_mountain"))
    local shade = f:CreateTexture(nil, "ARTWORK")
    shade:SetAllPoints(banner)
    Battlemon.Fill(shade, 0, 0, 0, 0.45)

    local icon = f:CreateTexture(nil, "OVERLAY")
    icon:SetSize(44, 44)
    icon:SetPoint("TOPLEFT", 16, -8)

    local title = Battlemon.Font(f, 20, "", 1, 0.90, 0.40)
    title:SetPoint("TOP", 0, -14)
    title:SetText("Moves")

    local sub = Battlemon.Font(f, 12, "", 0.86, 0.90, 0.96)
    sub:SetPoint("TOP", title, "BOTTOM", 0, -4)

    local slots = {}
    for i = 1, 4 do
        local btn = CreateFrame("Button", nil, f)
        btn:SetSize(300, 54)
        btn:SetPoint("TOPLEFT", 18, -78 - ((i - 1) * 60))
        btn.bg = btn:CreateTexture(nil, "BACKGROUND")
        btn.bg:SetAllPoints()
        Battlemon.Fill(btn.bg, 0.11, 0.12, 0.16, 1)
        btn.slot = Battlemon.Font(btn, 11, "", 1, 0.82, 0.30)
        btn.slot:SetPoint("TOPLEFT", 8, -6)
        btn.slot:SetText("MOVE " .. i)
        btn.name = Battlemon.Font(btn, 15, "", 0.94, 0.95, 0.98)
        btn.name:SetPoint("TOPLEFT", 66, -6)
        btn.name:SetJustifyH("LEFT")
        btn.info = Battlemon.Font(btn, 11, "", 0.76, 0.80, 0.86)
        btn.info:SetPoint("BOTTOMLEFT", 66, 7)
        btn.info:SetJustifyH("LEFT")
        btn:RegisterForClicks("LeftButtonUp", "RightButtonUp")
        btn:SetScript("OnClick", function(_, button)
            if button == "RightButton" then
                picks[i] = ""
            end
            selectedSlot = i
            Battlemon.RefreshMoves()
        end)
        slots[i] = btn
    end

    local search = CreateFrame("EditBox", "BattlemonMoveSearch", f, "InputBoxTemplate")
    search:SetSize(240, 20)
    search:SetPoint("TOPLEFT", 344, -80)
    search:SetAutoFocus(false)
    search:SetMaxLetters(24)
    search:SetScript("OnTextChanged", function(self)
        filter = self:GetText() or ""
        if ui then
            FauxScrollFrame_SetOffset(ui.scroll, 0)
            local bar = getglobal("BattlemonMoveScrollScrollBar")
            if bar then
                bar:SetValue(0)
            end
        end
        Battlemon.RefreshMoves()
    end)
    search:SetScript("OnEscapePressed", function(self)
        self:SetText("")
        self:ClearFocus()
    end)

    local freeBtn
    freeBtn = Battlemon.MakeTextButton(f, 106, 22, "FREE ONLY", function()
        freeOnly = not freeOnly
        if freeOnly then
            freeBtn:SetTint(0.16, 0.30, 0.18)
        else
            freeBtn:SetTint(0.18, 0.20, 0.27)
        end
        Battlemon.RefreshMoves()
    end)
    freeBtn:SetPoint("TOPRIGHT", -18, -78)

    local listFrame = CreateFrame("Frame", nil, f)
    listFrame:SetPoint("TOPLEFT", 336, -108)
    listFrame:SetSize(494, VISIBLE * ROW + 6)
    local listBg = listFrame:CreateTexture(nil, "BACKGROUND")
    listBg:SetAllPoints()
    Battlemon.Fill(listBg, 0.03, 0.04, 0.06, 0.9)

    local scroll = CreateFrame("ScrollFrame", "BattlemonMoveScroll", listFrame, "FauxScrollFrameTemplate")
    scroll:SetPoint("TOPLEFT", 2, -3)
    scroll:SetPoint("BOTTOMRIGHT", -26, 3)
    scroll:SetScript("OnVerticalScroll", function(self, offset)
        FauxScrollFrame_OnVerticalScroll(self, offset, ROW, Battlemon.RefreshMoves)
    end)

    local rows = {}
    for i = 1, VISIBLE do
        local btn = CreateFrame("Button", nil, listFrame)
        btn:SetSize(462, ROW - 2)
        btn:SetPoint("TOPLEFT", 4, -((i - 1) * ROW) - 4)
        btn.bg = btn:CreateTexture(nil, "BACKGROUND")
        btn.bg:SetAllPoints()
        Battlemon.Fill(btn.bg, 0.08, 0.09, 0.12, 1)
        btn.name = Battlemon.Font(btn, 13, "", 0.94, 0.95, 0.98)
        btn.name:SetPoint("LEFT", 6, 0)
        btn.name:SetJustifyH("LEFT")
        btn.name:SetWidth(140)
        btn.info = Battlemon.Font(btn, 11, "", 0.74, 0.78, 0.84)
        btn.info:SetPoint("LEFT", 150, 0)
        btn.info:SetJustifyH("LEFT")
        btn.info:SetWidth(240)
        btn.tag = Battlemon.Font(btn, 11, "", 1, 0.82, 0.36)
        btn.tag:SetPoint("RIGHT", -6, 0)
        btn.tag:SetJustifyH("RIGHT")
        btn:SetScript("OnClick", function(self)
            if self.internal then
                assign(self.internal)
            end
        end)
        rows[i] = btn
    end

    -- Kept inside the move-slot column: the list runs almost to the bottom edge
    -- on the right, so there is no full-width footer to sit in.
    local hint = Battlemon.Font(f, 12, "", 0.82, 0.86, 0.92)
    hint:SetPoint("TOPLEFT", 20, -330)
    hint:SetWidth(300)
    hint:SetJustifyH("LEFT")

    local save = Battlemon.MakeTextButton(f, 180, 40, "SAVE MOVES", function()
        local parts = { tostring(ownedId) }
        for i = 1, 4 do
            table.insert(parts, picks[i])
        end
        Battlemon.Send("SETMOVES", table.concat(parts, ","))
    end, 0.20, 0.30, 0.16)
    save:SetPoint("BOTTOMLEFT", 20, 24)

    local revert = Battlemon.MakeTextButton(f, 110, 40, "REVERT", function()
        resetPicks()
        Battlemon.RefreshMoves()
    end)
    revert:SetPoint("LEFT", save, "RIGHT", 12, 0)

    ui = {
        frame = f, slots = slots, rows = rows, scroll = scroll, search = search,
        title = title, sub = sub, icon = icon, hint = hint, save = save, freeBtn = freeBtn,
    }
    return ui
end

-- The MOVES tab can be clicked with nothing selected on the Party page, so fall
-- back to whoever leads the party rather than opening a manager with no Pokemon
-- behind it, which just sits on "Loading move pool..." forever.
local function defaultOwnedId()
    local owned = Battlemon.state.owned or {}
    if ownedId ~= 0 and owned[ownedId] then
        return ownedId
    end
    local slots = Battlemon.state.partySlots or {}
    for i = 1, 6 do
        local id = slots[i] or 0
        if id ~= 0 and owned[id] then
            return id
        end
    end
    local first
    for id in pairs(owned) do
        if not first or id < first then
            first = id
        end
    end
    return first or 0
end

function Battlemon.ShowMoves(id)
    if inBattle() then
        Battlemon.Print("You can't change moves during a battle.")
        return
    end
    id = tonumber(id) or 0
    if id == 0 then
        id = defaultOwnedId()
    end
    if id == 0 then
        Battlemon.Print("Catch a Pokémon first.")
        return
    end
    Battlemon.EnsureData()
    ownedId = id
    filter = ""
    build()
    ui.search:SetText("")
    resetPicks()
    -- The pool is level and purchase dependent, so always ask the server.
    Battlemon.state.learnset = { ownedId = id, cost = 0, moves = {}, ready = false }
    Battlemon.Send("LEARNSET", tostring(id))
    Battlemon.OpenPanel("moves")
    Battlemon.RefreshMoves()
end

function Battlemon.BuildMoves()
    return build().frame
end
