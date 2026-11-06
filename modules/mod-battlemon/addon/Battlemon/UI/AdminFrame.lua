Battlemon = Battlemon or {}

-- Spawn admin panel (/bm admin). The server only answers administrators, so for anyone else this just opens an
-- empty window and a chat line says why. Every number here lives on the server (battlemon_spawn_setting and
-- battlemon_spawn_zone) and is applied the moment it is saved.

local ui

-- name, label, what it does
local KNOBS = {
    { "enable", "Zone-aware spawns", "1 on, 0 off (off = the old global random pick)" },
    { "level_mode", "Level mode", "0 follow your lead, 1 zone range, 2 your level kept inside the zone range" },
    { "rarity_exponent", "Rarity strength", "0 ignore catch rate, 1 proportional, 2 rare things get very rare" },
    { "stage_step", "Stone/trade evo levels", "extra levels for evolving by stone, trade or friendship; 0 = no level gate" },
    { "leak", "Off-type leak", "0-1 chance weight for a type the zone does not list; 0 keeps them out" },
    { "weight_normal", "Normal weight", "relative weight of ordinary Pokémon" },
    { "weight_starter", "Starter weight", "relative weight of starter lines" },
    { "weight_legendary", "Legendary weight", "relative weight of legendaries and mythicals" },
}

local ROW = 28

local function clean(text)
    return (string.gsub(text or "", "[\t\r\n]", ""))
end

function Battlemon.RefreshAdmin()
    if not ui or not ui.frame:IsShown() then
        return
    end
    local admin = Battlemon.state.admin
    for _, knob in ipairs(KNOBS) do
        local box = ui.boxes[knob[1]]
        -- Do not overwrite a value that is being typed.
        if box and not box:HasFocus() then
            box:SetText(admin.settings[knob[1]] or "")
        end
    end
    local zone = admin.zone
    if zone then
        local name = (GetRealZoneText and GetRealZoneText()) or ""
        ui.zoneTitle:SetText(string.format("This zone: %s (id %d)%s", name, zone.id,
            zone.min > 0 and "" or "  |cffd0a050no rule yet — spawns as before|r"))
        if not ui.minBox:HasFocus() then ui.minBox:SetText(zone.min > 0 and tostring(zone.min) or "") end
        if not ui.maxBox:HasFocus() then ui.maxBox:SetText(zone.max > 0 and tostring(zone.max) or "") end
        if not ui.typesBox:HasFocus() then ui.typesBox:SetText(zone.types or "") end
    end
    local odds = admin.odds
    if odds then
        local lines = { string.format("Likeliest wild Pokémon here at level %d:", odds.level) }
        for i, row in ipairs(odds.list) do
            lines[#lines + 1] = string.format("%2d. %s  %.1f%%", i, row.name, row.pct)
        end
        ui.odds:SetText(table.concat(lines, "\n"))
    else
        ui.odds:SetText("Press PREVIEW to see what would spawn here.")
    end
end

local function send(verb, ...)
    local parts = { verb, ... }
    for i = 2, #parts do
        parts[i] = clean(parts[i])
    end
    Battlemon.Send("ADMIN", table.concat(parts, "\t"))
end

local function build()
    if ui then
        return ui
    end
    local f = Battlemon.MakeWindow("BattlemonAdminFrame", 640, 640)

    local title = Battlemon.Font(f, 20, "", 1, 0.90, 0.40)
    title:SetPoint("TOP", 0, -16)
    title:SetText("Spawn admin")

    local boxes = {}
    for i, knob in ipairs(KNOBS) do
        local y = -56 - (i - 1) * ROW
        local label = Battlemon.Font(f, 13, "", 0.92, 0.94, 0.98)
        label:SetPoint("TOPLEFT", 24, y)
        label:SetText(knob[2])
        local box = CreateFrame("EditBox", "BattlemonAdmin_" .. knob[1], f, "InputBoxTemplate")
        box:SetSize(70, 20)
        box:SetPoint("TOPLEFT", 190, y + 4)
        box:SetAutoFocus(false)
        box:SetMaxLetters(8)
        box:SetScript("OnEnterPressed", function(self)
            self:ClearFocus()
            send("SET", knob[1], self:GetText())
        end)
        box:SetScript("OnEscapePressed", function(self)
            self:ClearFocus()
            Battlemon.RefreshAdmin()
        end)
        boxes[knob[1]] = box
        local hint = Battlemon.Font(f, 11, "", 0.62, 0.66, 0.72)
        hint:SetPoint("LEFT", box, "RIGHT", 10, 0)
        hint:SetWidth(330)
        hint:SetJustifyH("LEFT")
        hint:SetText(knob[3])
    end

    local applyAll = Battlemon.MakeTextButton(f, 150, 26, "APPLY ALL", function()
        local admin = Battlemon.state.admin
        for _, knob in ipairs(KNOBS) do
            local text = clean(boxes[knob[1]]:GetText())
            if text ~= (admin.settings[knob[1]] or "") then
                send("SET", knob[1], text)
            end
        end
    end, 0.20, 0.30, 0.16)
    applyAll:SetPoint("TOPLEFT", 24, -56 - #KNOBS * ROW - 4)

    local zoneY = -56 - #KNOBS * ROW - 50
    local zoneTitle = Battlemon.Font(f, 14, "", 1, 0.82, 0.30)
    zoneTitle:SetPoint("TOPLEFT", 24, zoneY)

    local function small(text, x, y)
        local fs = Battlemon.Font(f, 12, "", 0.92, 0.94, 0.98)
        fs:SetPoint("TOPLEFT", x, y)
        fs:SetText(text)
    end
    small("Levels", 24, zoneY - 30)
    local minBox = CreateFrame("EditBox", "BattlemonAdmin_zoneMin", f, "InputBoxTemplate")
    minBox:SetSize(40, 20)
    minBox:SetPoint("TOPLEFT", 80, zoneY - 26)
    minBox:SetAutoFocus(false)
    minBox:SetMaxLetters(3)
    small("to", 130, zoneY - 30)
    local maxBox = CreateFrame("EditBox", "BattlemonAdmin_zoneMax", f, "InputBoxTemplate")
    maxBox:SetSize(40, 20)
    maxBox:SetPoint("TOPLEFT", 152, zoneY - 26)
    maxBox:SetAutoFocus(false)
    maxBox:SetMaxLetters(3)
    small("Types", 24, zoneY - 60)
    local typesBox = CreateFrame("EditBox", "BattlemonAdmin_zoneTypes", f, "InputBoxTemplate")
    typesBox:SetSize(460, 20)
    typesBox:SetPoint("TOPLEFT", 80, zoneY - 56)
    typesBox:SetAutoFocus(false)
    typesBox:SetMaxLetters(200)
    local typesHint = Battlemon.Font(f, 11, "", 0.62, 0.66, 0.72)
    typesHint:SetPoint("TOPLEFT", 80, zoneY - 80)
    typesHint:SetText("TYPE:weight pairs, e.g. GRASS:3,BUG:2,NORMAL:1 — a type not listed uses the off-type leak.")

    local saveZone = Battlemon.MakeTextButton(f, 150, 26, "SAVE ZONE", function()
        send("ZONE", minBox:GetText(), maxBox:GetText(), typesBox:GetText())
    end, 0.20, 0.30, 0.16)
    saveZone:SetPoint("TOPLEFT", 24, zoneY - 104)
    local preview = Battlemon.MakeTextButton(f, 150, 26, "PREVIEW", function()
        send("PREVIEW")
    end, 0.18, 0.24, 0.34)
    preview:SetPoint("LEFT", saveZone, "RIGHT", 12, 0)
    local refresh = Battlemon.MakeTextButton(f, 110, 26, "REFRESH", function()
        send("GET")
    end, 0.18, 0.24, 0.34)
    refresh:SetPoint("LEFT", preview, "RIGHT", 12, 0)

    local odds = Battlemon.Font(f, 12, "", 0.86, 0.90, 0.96)
    odds:SetPoint("TOPLEFT", 24, zoneY - 142)
    odds:SetJustifyH("LEFT")
    odds:SetJustifyV("TOP")
    odds:SetWidth(590)

    f:SetScript("OnShow", function()
        send("GET")
        Battlemon.RefreshAdmin()
    end)
    f:Hide()

    ui = { frame = f, boxes = boxes, zoneTitle = zoneTitle, minBox = minBox, maxBox = maxBox, typesBox = typesBox,
           odds = odds }
    return ui
end

function Battlemon.ShowAdmin()
    local f = build().frame
    if f:IsShown() then
        f:Hide()
    else
        f:Show()
    end
end
