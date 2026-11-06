Battlemon = Battlemon or {}

local ui
-- Tall enough for a name plus a two-line description: the item blurbs run past
-- 100 characters, and a shorter row ran them into the name above.
local ROW = 56
local VISIBLE = 8

local function itemName(internal)
    local def = (Battlemon.Items or {})[internal]
    return (def and def.name) or internal
end

local function held(internal)
    return (Battlemon.state.bag or {})[internal] or 0
end

local function buy(internal, qty)
    Battlemon.Send("BUY", internal .. "," .. tostring(qty))
end

function Battlemon.RefreshShop()
    if not ui or not ui.frame:IsShown() then
        return
    end
    local list = Battlemon.state.shop or {}
    local points = Battlemon.state.points or 0
    ui.points:SetText(string.format("|cffffd45a%d|r Battlemon Points", points))

    FauxScrollFrame_Update(ui.scroll, #list, VISIBLE, ROW)
    local offset = FauxScrollFrame_GetOffset(ui.scroll) or 0
    for i = 1, VISIBLE do
        local e = list[offset + i]
        local row = ui.rows[i]
        if e then
            row:Show()
            row.internal = e.internal
            local def = (Battlemon.Items or {})[e.internal]
            row.name:SetText(itemName(e.internal))
            row.desc:SetText((def and def.description) or "")
            row.cost:SetText(string.format("|cffffd45a%d|r pts", e.cost))
            row.owned:SetText(string.format("have %d", held(e.internal)))

            local canOne = points >= e.cost
            local canFive = points >= e.cost * 5
            Battlemon.SetButtonEnabled(row.buy1, canOne)
            Battlemon.SetButtonEnabled(row.buy5, canFive)
            if canOne then
                row.name:SetTextColor(0.96, 0.96, 0.98)
                Battlemon.Fill(row.bg, 0.10, 0.11, 0.15, 1)
            else
                row.name:SetTextColor(0.55, 0.56, 0.60)
                Battlemon.Fill(row.bg, 0.06, 0.07, 0.09, 1)
            end
        else
            row:Hide()
            row.internal = nil
        end
    end

    if #list == 0 then
        ui.empty:Show()
    else
        ui.empty:Hide()
    end
end

local function build()
    if ui then
        return ui
    end
    local f = Battlemon.MakeWindow("BattlemonShopFrame", 848, 552)

    local banner = f:CreateTexture(nil, "ARTWORK")
    banner:SetPoint("TOPLEFT", 4, -4)
    banner:SetPoint("TOPRIGHT", -4, -4)
    banner:SetHeight(60)
    banner:SetTexture(Battlemon.Media("bg_city"))
    local shade = f:CreateTexture(nil, "ARTWORK")
    shade:SetAllPoints(banner)
    Battlemon.Fill(shade, 0, 0, 0, 0.45)

    local title = Battlemon.Font(f, 20, "", 1, 0.90, 0.40)
    title:SetPoint("TOP", 0, -14)
    title:SetText("Poké Mart")

    local points = Battlemon.Font(f, 13, "", 0.88, 0.92, 0.98)
    points:SetPoint("TOP", title, "BOTTOM", 0, -4)

    -- The shelf runs to the bottom edge, so the footnote lives up in the header.
    local hint = Battlemon.Font(f, 12, "", 0.80, 0.84, 0.90)
    hint:SetPoint("TOP", 0, -66)
    hint:SetWidth(780)
    hint:SetJustifyH("CENTER")
    hint:SetText("Points come from winning battles. Potions are used from the BAG in combat; balls are thrown once the foe faints.")

    local listFrame = CreateFrame("Frame", nil, f)
    listFrame:SetPoint("TOPLEFT", 16, -86)
    listFrame:SetSize(816, VISIBLE * ROW + 6)
    local listBg = listFrame:CreateTexture(nil, "BACKGROUND")
    listBg:SetAllPoints()
    Battlemon.Fill(listBg, 0.03, 0.04, 0.06, 0.9)

    local empty = Battlemon.Font(listFrame, 13, "", 0.7, 0.72, 0.78)
    empty:SetPoint("CENTER")
    empty:SetText("The shelves are empty. Type /bm to reconnect.")

    local scroll = CreateFrame("ScrollFrame", "BattlemonShopScroll", listFrame, "FauxScrollFrameTemplate")
    scroll:SetPoint("TOPLEFT", 2, -3)
    scroll:SetPoint("BOTTOMRIGHT", -26, 3)
    scroll:SetScript("OnVerticalScroll", function(self, offset)
        FauxScrollFrame_OnVerticalScroll(self, offset, ROW, Battlemon.RefreshShop)
    end)

    local rows = {}
    for i = 1, VISIBLE do
        local row = CreateFrame("Frame", nil, listFrame)
        row:SetSize(784, ROW - 4)
        row:SetPoint("TOPLEFT", 4, -((i - 1) * ROW) - 4)
        row.bg = row:CreateTexture(nil, "BACKGROUND")
        row.bg:SetAllPoints()
        Battlemon.Fill(row.bg, 0.10, 0.11, 0.15, 1)

        row.name = Battlemon.Font(row, 15, "", 0.96, 0.96, 0.98)
        row.name:SetPoint("TOPLEFT", 10, -7)
        row.name:SetJustifyH("LEFT")
        row.name:SetWidth(240)

        -- Anchored below the name and growing down, so a blurb that wraps runs
        -- into the empty half of the row instead of back over the name.
        row.desc = Battlemon.Font(row, 11, "", 0.72, 0.76, 0.82)
        row.desc:SetPoint("TOPLEFT", 10, -27)
        row.desc:SetJustifyH("LEFT")
        row.desc:SetJustifyV("TOP")
        row.desc:SetWidth(460)

        row.cost = Battlemon.Font(row, 14, "", 1, 0.86, 0.42)
        row.cost:SetPoint("TOPLEFT", 500, -8)
        row.cost:SetJustifyH("LEFT")

        row.owned = Battlemon.Font(row, 11, "", 0.70, 0.78, 0.70)
        row.owned:SetPoint("TOPLEFT", 500, -30)
        row.owned:SetJustifyH("LEFT")

        row.buy1 = Battlemon.MakeTextButton(row, 84, 32, "BUY", function()
            if row.internal then
                buy(row.internal, 1)
            end
        end, 0.20, 0.30, 0.16)
        row.buy1:SetPoint("RIGHT", -108, 0)

        row.buy5 = Battlemon.MakeTextButton(row, 84, 32, "BUY x5", function()
            if row.internal then
                buy(row.internal, 5)
            end
        end, 0.18, 0.24, 0.34)
        row.buy5:SetPoint("RIGHT", -12, 0)

        rows[i] = row
    end

    f:SetScript("OnShow", function()
        Battlemon.Send("SHOP")
        Battlemon.RefreshShop()
    end)

    ui = { frame = f, scroll = scroll, rows = rows, points = points, empty = empty }
    return ui
end

function Battlemon.BuildShop()
    return build().frame
end

function Battlemon.ShowShop()
    Battlemon.EnsureData()
    Battlemon.OpenPanel("shop")
    Battlemon.RefreshShop()
end
