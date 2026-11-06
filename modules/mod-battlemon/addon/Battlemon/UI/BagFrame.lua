Battlemon = Battlemon or {}

-- The out-of-battle bag. Its real job is Revives: fainting now sticks between
-- fights, so without this the only way back is to wait out the timer. Potions
-- and cures are listed too, but the server turns them down out here because
-- damage and status never carry over.

local ui
local selectedItem = nil
local ROW = 34
local VISIBLE = 9

local REVIVES = { REVIVE = true, MAXREVIVE = true, REVIVALHERB = true }

local function itemName(internal)
    local def = (Battlemon.Items or {})[internal]
    return (def and def.name) or internal
end

-- Medicine only. Balls and everything else would just be noise on a page whose
-- whole point is patching the team up.
local function bagList()
    local t = {}
    for internal, count in pairs(Battlemon.state.bag or {}) do
        local def = (Battlemon.Items or {})[internal]
        if count > 0 and def and def.battle_use == "OnPokemon" then
            table.insert(t, { internal = internal, count = count, name = itemName(internal) })
        end
    end
    table.sort(t, function(a, b) return a.name < b.name end)
    return t
end

local function ownedList()
    local t = {}
    for _, row in pairs(Battlemon.state.owned or {}) do
        table.insert(t, row)
    end
    local name = {}
    for i = 1, #t do
        name[t[i]] = string.lower(Battlemon.FormName(t[i].formId, t[i].name) or "")
    end
    table.sort(t, function(a, b)
        -- Fainted first: they are the only ones anything here can help.
        local ad, bd = (a.hp or 0) <= 0, (b.hp or 0) <= 0
        if ad ~= bd then
            return ad
        end
        if name[a] ~= name[b] then
            return name[a] < name[b]
        end
        return (a.id or 0) < (b.id or 0)
    end)
    return t
end

local function reviveText(secs)
    if secs <= 0 then
        return "|cffd05050FAINTED|r"
    elseif secs < 60 then
        return string.format("|cffd05050FAINTED|r |cff8a8f99back in %ds|r", secs)
    end
    return string.format("|cffd05050FAINTED|r |cff8a8f99back in %dm|r", math.ceil(secs / 60))
end

function Battlemon.RefreshBag()
    if not ui or not ui.frame:IsShown() then
        return
    end

    local items = bagList()
    if selectedItem and (Battlemon.state.bag or {})[selectedItem] == nil then
        selectedItem = nil
    end
    for i = 1, VISIBLE do
        local e = items[i]
        local btn = ui.items[i]
        if e then
            btn:Show()
            btn.internal = e.internal
            btn.name:SetText(e.name)
            btn.count:SetText("x" .. e.count)
            if e.internal == selectedItem then
                Battlemon.Fill(btn.bg, 0.34, 0.28, 0.10, 1)
                btn.name:SetTextColor(1, 0.92, 0.55)
            else
                Battlemon.Fill(btn.bg, 0.12, 0.13, 0.17, 1)
                btn.name:SetTextColor(0.94, 0.95, 0.98)
            end
        else
            btn:Hide()
            btn.internal = nil
        end
    end
    if #items == 0 then
        ui.emptyBag:Show()
    else
        ui.emptyBag:Hide()
    end

    local list = ownedList()
    FauxScrollFrame_Update(ui.scroll, #list, VISIBLE, ROW)
    local offset = FauxScrollFrame_GetOffset(ui.scroll) or 0
    local usable = selectedItem and REVIVES[selectedItem]
    for i = 1, VISIBLE do
        local row = list[offset + i]
        local btn = ui.rows[i]
        if row then
            btn:Show()
            btn.ownedId = row.id
            local down = (row.hp or 0) <= 0
            Battlemon.SetPokemonTexture(btn.icon, "Front",
                Battlemon.FormSprite(row.formId, row.sprite), row.shiny)
            btn.name:SetText(Battlemon.ShinyName(Battlemon.FormName(row.formId, row.name), row.shiny))
            btn.info:SetText(down
                and reviveText(row.reviveIn or 0)
                or string.format("Lv.%d   |cff70a070ready|r", row.level or 1))
            btn.usable = (usable and down) or false
            if btn.usable then
                btn.name:SetTextColor(0.96, 0.96, 0.98)
                Battlemon.Fill(btn.bg, 0.13, 0.16, 0.20, 1)
            else
                btn.name:SetTextColor(0.58, 0.60, 0.66)
                Battlemon.Fill(btn.bg, 0.08, 0.09, 0.12, 1)
            end
        else
            btn:Hide()
            btn.ownedId = nil
            btn.usable = false
        end
    end

    if #items == 0 then
        ui.hint:SetText("No medicine. Buy Revives from the SHOP for 10 points.")
    elseif not selectedItem then
        ui.hint:SetText("Pick an item on the left, then the Pokémon to use it on.")
    elseif not REVIVES[selectedItem] then
        ui.hint:SetText("|cffd0a050" .. itemName(selectedItem) ..
            " only works during a battle.|r Damage and status never carry over.")
    else
        ui.hint:SetText("Use the " .. itemName(selectedItem) .. " on which fainted Pokémon?")
    end
end

local function build()
    if ui then
        return ui
    end
    local f = Battlemon.MakeWindow("BattlemonBagFrame", 848, 552)

    local banner = f:CreateTexture(nil, "ARTWORK")
    banner:SetPoint("TOPLEFT", 4, -4)
    banner:SetPoint("TOPRIGHT", -4, -4)
    banner:SetHeight(62)
    banner:SetTexture(Battlemon.Media("bg_city"))
    local shade = f:CreateTexture(nil, "ARTWORK")
    shade:SetAllPoints(banner)
    Battlemon.Fill(shade, 0, 0, 0, 0.45)

    local title = Battlemon.Font(f, 20, "", 1, 0.90, 0.40)
    title:SetPoint("TOP", 0, -18)
    title:SetText("Bag")

    local hint = Battlemon.Font(f, 12, "", 0.82, 0.86, 0.92)
    hint:SetPoint("TOP", 0, -44)
    hint:SetWidth(780)
    hint:SetJustifyH("CENTER")

    local itemFrame = CreateFrame("Frame", nil, f)
    itemFrame:SetPoint("TOPLEFT", 22, -78)
    itemFrame:SetSize(330, VISIBLE * ROW + 6)
    local itemBg = itemFrame:CreateTexture(nil, "BACKGROUND")
    itemBg:SetAllPoints()
    Battlemon.Fill(itemBg, 0.03, 0.04, 0.06, 0.9)

    local emptyBag = Battlemon.Font(itemFrame, 13, "", 0.7, 0.72, 0.78)
    emptyBag:SetPoint("CENTER")
    emptyBag:SetText("No medicine in the bag.")

    local items = {}
    for i = 1, VISIBLE do
        local btn = CreateFrame("Button", nil, itemFrame)
        btn:SetSize(322, ROW - 2)
        btn:SetPoint("TOPLEFT", 4, -((i - 1) * ROW) - 4)
        btn.bg = btn:CreateTexture(nil, "BACKGROUND")
        btn.bg:SetAllPoints()
        Battlemon.Fill(btn.bg, 0.12, 0.13, 0.17, 1)
        btn.name = Battlemon.Font(btn, 14, "", 0.94, 0.95, 0.98)
        btn.name:SetPoint("LEFT", 10, 0)
        btn.name:SetJustifyH("LEFT")
        btn.name:SetWidth(230)
        btn.count = Battlemon.Font(btn, 12, "", 0.78, 0.82, 0.88)
        btn.count:SetPoint("RIGHT", -10, 0)
        btn.count:SetJustifyH("RIGHT")
        btn:SetScript("OnClick", function(self)
            if self.internal then
                selectedItem = self.internal
                Battlemon.RefreshBag()
            end
        end)
        items[i] = btn
    end

    local listFrame = CreateFrame("Frame", nil, f)
    listFrame:SetPoint("TOPRIGHT", -22, -78)
    listFrame:SetSize(452, VISIBLE * ROW + 6)
    local listBg = listFrame:CreateTexture(nil, "BACKGROUND")
    listBg:SetAllPoints()
    Battlemon.Fill(listBg, 0.03, 0.04, 0.06, 0.9)

    local scroll = CreateFrame("ScrollFrame", "BattlemonBagScroll", listFrame, "FauxScrollFrameTemplate")
    scroll:SetPoint("TOPLEFT", 2, -3)
    scroll:SetPoint("BOTTOMRIGHT", -26, 3)
    scroll:SetScript("OnVerticalScroll", function(self, offset)
        FauxScrollFrame_OnVerticalScroll(self, offset, ROW, Battlemon.RefreshBag)
    end)

    local rows = {}
    for i = 1, VISIBLE do
        local btn = CreateFrame("Button", nil, listFrame)
        btn:SetSize(420, ROW - 2)
        btn:SetPoint("TOPLEFT", 4, -((i - 1) * ROW) - 4)
        btn.bg = btn:CreateTexture(nil, "BACKGROUND")
        btn.bg:SetAllPoints()
        Battlemon.Fill(btn.bg, 0.08, 0.09, 0.12, 1)
        btn.icon = btn:CreateTexture(nil, "ARTWORK")
        btn.icon:SetSize(30, 30)
        btn.icon:SetPoint("LEFT", 2, 0)
        btn.name = Battlemon.Font(btn, 14, "", 0.94, 0.95, 0.98)
        btn.name:SetPoint("LEFT", 36, 0)
        btn.name:SetJustifyH("LEFT")
        btn.name:SetWidth(190)
        btn.info = Battlemon.Font(btn, 12, "", 0.78, 0.82, 0.88)
        btn.info:SetPoint("RIGHT", -8, 0)
        btn.info:SetJustifyH("RIGHT")
        btn:SetScript("OnClick", function(self)
            if not self.ownedId or not self.usable or not selectedItem then
                return
            end
            Battlemon.Send("BAGUSE", selectedItem .. "," .. self.ownedId)
        end)
        rows[i] = btn
    end

    f:SetScript("OnShow", function()
        Battlemon.Send("PARTY")
        Battlemon.RefreshBag()
    end)

    ui = { frame = f, scroll = scroll, rows = rows, items = items,
           hint = hint, emptyBag = emptyBag }
    return ui
end

function Battlemon.BuildBag()
    return build().frame
end

function Battlemon.ShowBag()
    Battlemon.EnsureData()
    Battlemon.OpenPanel("bag")
    Battlemon.RefreshBag()
end
