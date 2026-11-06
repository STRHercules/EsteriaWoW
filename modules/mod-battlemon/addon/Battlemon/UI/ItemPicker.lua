Battlemon = Battlemon or {}

-- Give a Pokémon an item to hold, or take it back (Party screen → ITEM). The server decides everything: it takes the
-- item from the bag, hands any old one back, and refuses outside a safe moment. This window lists what is in the bag
-- that a Pokémon can hold and sends GIVE / TAKE.

local ui
local ownedId = 0
local offset = 0
local VISIBLE = 10

-- What the server accepts as a held item (src/BattlemonHeldItems.h). tests/test_helditems_data.py keeps the two lists
-- identical.
local HOLDABLE = {
    CHARCOAL = true, MYSTICWATER = true, MIRACLESEED = true, MAGNET = true, NEVERMELTICE = true, BLACKBELT = true,
    POISONBARB = true, SOFTSAND = true, SHARPBEAK = true, TWISTEDSPOON = true, SILVERPOWDER = true,
    HARDSTONE = true, SPELLTAG = true, DRAGONFANG = true, BLACKGLASSES = true, METALCOAT = true, SILKSCARF = true,
    CHOICEBAND = true, CHOICESPECS = true, CHOICESCARF = true, MUSCLEBAND = true, WISEGLASSES = true,
    LIFEORB = true, EXPERTBELT = true, FOCUSSASH = true, LEFTOVERS = true, BLACKSLUDGE = true,
    ORANBERRY = true, SITRUSBERRY = true, CHERIBERRY = true, CHESTOBERRY = true, PECHABERRY = true,
    RAWSTBERRY = true, ASPEARBERRY = true, LUMBERRY = true, LUCKYEGG = true, EVERSTONE = true, DESTINYKNOT = true,
}

local function itemName(internal)
    local def = (Battlemon.Items or {})[internal]
    return (def and def.name) or internal
end

local function holdableBag()
    local list = {}
    for internal, count in pairs(Battlemon.state.bag or {}) do
        if HOLDABLE[internal] and count > 0 then
            list[#list + 1] = { internal = internal, count = count, name = itemName(internal) }
        end
    end
    table.sort(list, function(a, b) return a.name < b.name end)
    return list
end

function Battlemon.RefreshItemPicker()
    if not ui or not ui.frame:IsShown() then
        return
    end
    local row = Battlemon.state.owned[ownedId]
    if not row then
        ui.frame:Hide()
        return
    end
    ui.title:SetText(Battlemon.FormName(row.formId, row.name))
    local held = row.held or ""
    ui.current:SetText(held ~= "" and ("Holding: " .. itemName(held)) or "Holding nothing.")
    Battlemon.SetButtonEnabled(ui.take, held ~= "")

    local list = holdableBag()
    offset = math.max(0, math.min(offset, #list - VISIBLE))
    for i = 1, VISIBLE do
        local e = list[offset + i]
        local btn = ui.buttons[i]
        if e then
            btn:Show()
            btn.item = e.internal
            btn.text:SetText(string.format("%s   x%d", e.name, e.count))
        else
            btn:Hide()
            btn.item = nil
        end
    end
    if #list == 0 then
        ui.hint:SetText("You have no items a Pokémon can hold. The Center shop sells some.")
    elseif #list > VISIBLE then
        ui.hint:SetText(string.format("Click an item to give it. Scroll for more (%d-%d of %d).", offset + 1,
            math.min(offset + VISIBLE, #list), #list))
    else
        ui.hint:SetText("Click an item to give it. Any item it already holds goes back to your bag.")
    end
end

local function build()
    if ui then
        return ui
    end
    local f = Battlemon.MakeWindow("BattlemonItemPicker", 440, 470)
    f:EnableMouseWheel(true)
    f:SetScript("OnMouseWheel", function(_, delta)
        offset = offset - delta
        Battlemon.RefreshItemPicker()
    end)
    local title = Battlemon.Font(f, 18, "", 1, 0.90, 0.40)
    title:SetPoint("TOP", 0, -16)
    local current = Battlemon.Font(f, 13, "", 0.86, 0.90, 0.96)
    current:SetPoint("TOP", 0, -44)

    local buttons = {}
    for i = 1, VISIBLE do
        local b = Battlemon.MakeTextButton(f, 396, 28, "", function(self)
            if self.item then
                Battlemon.Send("GIVE", string.format("%d\t%s", ownedId, self.item))
            end
        end, 0.14, 0.18, 0.24)
        b:SetPoint("TOP", 0, -72 - (i - 1) * 31)
        b.text:SetFont("Fonts\\FRIZQT__.TTF", 13, "")
        buttons[i] = b
    end
    local take = Battlemon.MakeTextButton(f, 396, 34, "TAKE ITEM BACK", function()
        Battlemon.Send("TAKE", tostring(ownedId))
    end, 0.30, 0.20, 0.16)
    take:SetPoint("BOTTOM", 0, 44)
    local hint = Battlemon.Font(f, 11, "", 0.62, 0.66, 0.72)
    hint:SetPoint("BOTTOM", 0, 18)
    hint:SetWidth(396)
    f:Hide()
    ui = { frame = f, title = title, current = current, buttons = buttons, take = take, hint = hint }
    return ui
end

function Battlemon.ShowItemPicker(id)
    ownedId = id
    offset = 0
    local w = build()
    w.frame:Show()
    Battlemon.Send("BAG") -- the bag may have changed since it was last sent
    Battlemon.RefreshItemPicker()
end

Battlemon.OnNet("OWNEDEND", function() Battlemon.RefreshItemPicker() end)
Battlemon.OnNet("BAG", function() Battlemon.RefreshItemPicker() end)
