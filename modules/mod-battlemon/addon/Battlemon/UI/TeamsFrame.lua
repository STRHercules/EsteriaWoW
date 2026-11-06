Battlemon = Battlemon or {}

local ui
local selectedId = 0
local ROW = 34
local VISIBLE = 11
local PRESET_ROW = 28
local PRESET_VISIBLE = 7

StaticPopupDialogs["BATTLEMON_DELETE_TEAM"] = {
    text = "Delete team \"%s\"?",
    button1 = YES,
    button2 = NO,
    OnAccept = function(_, data)
        if data and Battlemon.RemoveTeamPreset(data.index) then
            Battlemon.ResetTeamDraft()
            if ui and ui.nameBox then
                ui.nameBox:SetText("")
            end
            if ui and ui.presetScroll then
                ui.presetScroll:SetVerticalScroll(0)
            end
            Battlemon.RefreshTeams()
        end
    end,
    timeout = 0,
    whileDead = 1,
    hideOnEscape = 1,
}

local function editBlocked()
    if Battlemon.InBattle and Battlemon.InBattle() then
        Battlemon.Print("You can't edit teams during a battle.")
        return true
    end
    return false
end

local function draftSlotOf(ownedId)
    for s = 1, 6 do
        if Battlemon.teamDraft.party[s] == ownedId then
            return s
        end
    end
end

local function refreshSortLabel()
    if ui and ui.sortBtn then
        ui.sortBtn.text:SetText("Sort: " .. Battlemon.SortModeLabel())
    end
end

local function syncNameBox()
    if ui and ui.nameBox and not ui.nameBox:HasFocus() then
        ui.nameBox:SetText(Battlemon.teamDraft.name or "")
    end
end

local function paintDraftSlot(btn, slot)
    local locked = Battlemon.InBattle and Battlemon.InBattle()
    local id = Battlemon.teamDraft.party[slot] or 0
    local row = Battlemon.state.owned[id]
    btn.label:SetText(tostring(slot) .. ".")
    if row then
        local down = (row.hp or 0) <= 0 and " |cffd05050(down)|r" or ""
        btn.name:SetText(Battlemon.ShinyName(Battlemon.FormName(row.formId, row.name), row.shiny) .. down)
        Battlemon.SetPokemonTexture(btn.icon, "Front", Battlemon.FormSprite(row.formId, row.sprite), row.shiny)
        btn.icon:Show()
        Battlemon.Fill(btn.bg, locked and 0.10 or 0.13, locked and 0.11 or 0.16, locked and 0.13 or 0.20, 1)
    else
        btn.name:SetText("empty")
        btn.icon:Hide()
        Battlemon.Fill(btn.bg, 0.09, 0.09, 0.12, 1)
    end
    btn.name:SetTextColor(locked and 0.62 or 0.94, locked and 0.64 or 0.95, locked and 0.70 or 0.98)
end

local function assignDraftSlot(slot)
    if selectedId == 0 or editBlocked() then
        return
    end
    local party = Battlemon.teamDraft.party
    if party[slot] == selectedId then
        party[slot] = 0
    else
        for i = 1, 6 do
            if party[i] == selectedId then
                party[i] = 0
            end
        end
        party[slot] = selectedId
    end
    Battlemon.teamDraft.party = Battlemon.SanitizeParty(party)
    Battlemon.RefreshTeams()
end

function Battlemon.RefreshTeams()
    if not ui or not ui.frame:IsShown() then
        return
    end
    refreshSortLabel()
    syncNameBox()

    local list = Battlemon.GetSortedOwnedRows()
    FauxScrollFrame_Update(ui.scroll, #list, VISIBLE, ROW)
    local offset = FauxScrollFrame_GetOffset(ui.scroll) or 0
    for i = 1, VISIBLE do
        local row = list[offset + i]
        local btn = ui.rows[i]
        if row then
            btn:Show()
            Battlemon.PaintOwnedRow(btn, row, selectedId, draftSlotOf(row.id), "draft")
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
        paintDraftSlot(ui.slots[s], s)
    end

    local presets = Battlemon.GetTeamPresets()
    FauxScrollFrame_Update(ui.presetScroll, #presets, PRESET_VISIBLE, PRESET_ROW)
    local presetOffset = FauxScrollFrame_GetOffset(ui.presetScroll) or 0
    for i = 1, PRESET_VISIBLE do
        local preset = presets[presetOffset + i]
        local btn = ui.presetRows[i]
        if preset then
            btn:Show()
            btn.index = presetOffset + i
            btn.label:SetText(preset.name or "?")
            if btn.index == Battlemon.teamDraft.selectedIndex then
                Battlemon.Fill(btn.bg, 0.34, 0.28, 0.10, 1)
                btn.label:SetTextColor(1, 0.92, 0.55)
            else
                Battlemon.Fill(btn.bg, 0.12, 0.13, 0.17, 1)
                btn.label:SetTextColor(0.94, 0.95, 0.98)
            end
        else
            btn:Hide()
            btn.index = nil
        end
    end
    if #presets == 0 then
        ui.presetEmpty:Show()
    else
        ui.presetEmpty:Hide()
    end

    Battlemon.SetButtonEnabled(ui.loadBtn, not locked)
    Battlemon.SetButtonEnabled(ui.saveBtn, not locked)
    Battlemon.SetButtonEnabled(ui.newBtn, not locked)
    Battlemon.SetButtonEnabled(ui.delBtn, not locked and Battlemon.teamDraft.selectedIndex > 0)
    for s = 1, 6 do
        Battlemon.SetButtonEnabled(ui.slots[s], not locked)
    end

    if locked then
        ui.hint:SetText("|cffd0a050Team editing is locked while a battle is running.|r")
    elseif selectedId ~= 0 then
        local row = Battlemon.state.owned[selectedId]
        ui.hint:SetText(row
            and ("Selected " .. Battlemon.FormName(row.formId, row.name) .. " — click a draft slot on the right.")
            or "Click a Pokémon, then a draft slot.")
    else
        ui.hint:SetText("Build a lineup, save it, then load it as your active party.")
    end
end

local function selectPreset(index)
    if not Battlemon.LoadTeamDraftFromPreset(index) then
        return
    end
    syncNameBox()
    Battlemon.RefreshTeams()
end

local function build()
    if ui then
        return ui
    end
    local f = Battlemon.MakeWindow("BattlemonTeamsFrame", 848, 552)

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
    title:SetText("Teams")

    local hint = Battlemon.Font(f, 12, "", 0.82, 0.86, 0.92)
    hint:SetPoint("TOP", 0, -44)
    hint:SetWidth(780)
    hint:SetJustifyH("CENTER")

    local sortBtn = Battlemon.MakeTextButton(f, 160, 24, "Sort: Default", function()
        Battlemon.CyclePartySort()
        refreshSortLabel()
        Battlemon.RefreshTeams()
        if Battlemon.RefreshParty then
            Battlemon.RefreshParty()
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

    local scroll = CreateFrame("ScrollFrame", "BattlemonTeamsScroll", listFrame, "FauxScrollFrameTemplate")
    scroll:SetPoint("TOPLEFT", 2, -3)
    scroll:SetPoint("BOTTOMRIGHT", -26, 3)
    scroll:SetScript("OnVerticalScroll", function(self, offset)
        FauxScrollFrame_OnVerticalScroll(self, offset, ROW, Battlemon.RefreshTeams)
    end)

    local rows = {}
    for i = 1, VISIBLE do
        local btn = Battlemon.MakeOwnedRow(listFrame, ROW, function(ownedId)
            selectedId = ownedId
            Battlemon.RefreshTeams()
        end, function(ownedId)
            if ownedId and ownedId > 0 then
                Battlemon.ToggleFavorite(ownedId)
                Battlemon.RefreshTeams()
                if Battlemon.RefreshParty then
                    Battlemon.RefreshParty()
                end
            end
        end)
        btn:SetSize(348, ROW - 2)
        btn:SetPoint("TOPLEFT", 4, -((i - 1) * ROW) - 4)
        rows[i] = btn
    end

    local right = CreateFrame("Frame", nil, f)
    right:SetPoint("TOPRIGHT", -22, -78)
    right:SetSize(390, 450)

    local nameLabel = Battlemon.Font(right, 12, "", 0.78, 0.82, 0.88)
    nameLabel:SetPoint("TOPLEFT", 0, 0)
    nameLabel:SetText("Team name")

    local nameBox = CreateFrame("EditBox", nil, right)
    nameBox:SetSize(250, 24)
    nameBox:SetPoint("TOPLEFT", 0, -18)
    nameBox:SetAutoFocus(false)
    nameBox:SetFontObject("ChatFontNormal")
    nameBox:SetTextInsets(6, 6, 2, 2)
    local nameBg = nameBox:CreateTexture(nil, "BACKGROUND")
    nameBg:SetAllPoints()
    Battlemon.Fill(nameBg, 0.08, 0.09, 0.12, 1)
    nameBox:SetScript("OnTextChanged", function(self)
        Battlemon.teamDraft.name = self:GetText() or ""
    end)
    nameBox:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)
    nameBox:SetScript("OnEnterPressed", function(self) self:ClearFocus() end)

    local saveBtn = Battlemon.MakeTextButton(right, 90, 24, "SAVE", function()
        if editBlocked() then
            return
        end
        Battlemon.teamDraft.name = nameBox:GetText() or ""
        local ok, msg, index = Battlemon.SaveTeamPreset(
            Battlemon.teamDraft.name,
            Battlemon.teamDraft.party,
            Battlemon.teamDraft.selectedIndex
        )
        if not ok then
            Battlemon.Print(msg or "Could not save team.")
            return
        end
        Battlemon.teamDraft.selectedIndex = index
        Battlemon.RefreshTeams()
    end, 0.20, 0.30, 0.16)
    saveBtn:SetPoint("LEFT", nameBox, "RIGHT", 8, 0)
    saveBtn.text:SetFont("Fonts\\FRIZQT__.TTF", 12, "")

    local loadBtn = Battlemon.MakeTextButton(right, 140, 28, "LOAD PARTY", function()
        Battlemon.ApplyDraftToParty()
    end, 0.18, 0.24, 0.34)
    loadBtn:SetPoint("TOPLEFT", 0, -50)

    local slots = {}
    for s = 1, 6 do
        local col = (s - 1) % 3
        local row = math.floor((s - 1) / 3)
        local btn = CreateFrame("Button", nil, right)
        btn:SetSize(122, 52)
        btn:SetPoint("TOPLEFT", col * 128, -88 - row * 58)
        btn.bg = btn:CreateTexture(nil, "BACKGROUND")
        btn.bg:SetAllPoints()
        btn.label = Battlemon.Font(btn, 11, "", 1, 0.82, 0.30)
        btn.label:SetPoint("TOPLEFT", 6, -4)
        btn.icon = btn:CreateTexture(nil, "ARTWORK")
        btn.icon:SetSize(28, 28)
        btn.icon:SetPoint("LEFT", 6, -4)
        btn.name = Battlemon.Font(btn, 12, "", 0.94, 0.95, 0.98)
        btn.name:SetPoint("LEFT", 38, -6)
        btn.name:SetJustifyH("LEFT")
        btn.name:SetWidth(78)
        btn:SetScript("OnClick", function()
            assignDraftSlot(s)
        end)
        slots[s] = btn
    end

    local savedLabel = Battlemon.Font(right, 14, "", 1, 0.90, 0.40)
    savedLabel:SetPoint("TOPLEFT", 0, -210)
    savedLabel:SetText("Saved teams")

    local presetFrame = CreateFrame("Frame", nil, right)
    presetFrame:SetPoint("TOPLEFT", 0, -232)
    presetFrame:SetSize(390, PRESET_VISIBLE * PRESET_ROW + 6)
    local presetBg = presetFrame:CreateTexture(nil, "BACKGROUND")
    presetBg:SetAllPoints()
    Battlemon.Fill(presetBg, 0.03, 0.04, 0.06, 0.9)

    local presetEmpty = Battlemon.Font(presetFrame, 12, "", 0.7, 0.72, 0.78)
    presetEmpty:SetPoint("CENTER")
    presetEmpty:SetText("No saved teams yet.")

    local presetScroll = CreateFrame("ScrollFrame", "BattlemonTeamsPresetScroll", presetFrame, "FauxScrollFrameTemplate")
    presetScroll:SetPoint("TOPLEFT", 2, -3)
    presetScroll:SetPoint("BOTTOMRIGHT", -26, 3)
    presetScroll:SetScript("OnVerticalScroll", function(self, offset)
        FauxScrollFrame_OnVerticalScroll(self, offset, PRESET_ROW, Battlemon.RefreshTeams)
    end)

    local presetRows = {}
    for i = 1, PRESET_VISIBLE do
        local btn = CreateFrame("Button", nil, presetFrame)
        btn:SetSize(358, PRESET_ROW - 2)
        btn:SetPoint("TOPLEFT", 4, -((i - 1) * PRESET_ROW) - 4)
        btn.bg = btn:CreateTexture(nil, "BACKGROUND")
        btn.bg:SetAllPoints()
        btn.label = Battlemon.Font(btn, 13, "", 0.94, 0.95, 0.98)
        btn.label:SetPoint("LEFT", 10, 0)
        btn.label:SetJustifyH("LEFT")
        btn:SetScript("OnClick", function(self)
            if self.index then
                selectPreset(self.index)
            end
        end)
        presetRows[i] = btn
    end

    local newBtn = Battlemon.MakeTextButton(right, 100, 28, "NEW", function()
        Battlemon.ResetTeamDraft()
        nameBox:SetText("")
        presetScroll:SetVerticalScroll(0)
        Battlemon.RefreshTeams()
    end, 0.16, 0.17, 0.24)
    newBtn:SetPoint("BOTTOMLEFT", 0, 0)

    local delBtn = Battlemon.MakeTextButton(right, 100, 28, "DELETE", function()
        local idx = Battlemon.teamDraft.selectedIndex
        if idx <= 0 then
            Battlemon.Print("Select a saved team to delete.")
            return
        end
        local presets = Battlemon.GetTeamPresets()
        local preset = presets[idx]
        local name = preset and preset.name or "this team"
        StaticPopup_Show("BATTLEMON_DELETE_TEAM", name, nil, { index = idx })
    end, 0.16, 0.17, 0.24)
    delBtn:SetPoint("LEFT", newBtn, "RIGHT", 12, 0)

    f:SetScript("OnShow", function()
        Battlemon.Send("PARTY")
        Battlemon.RefreshTeams()
    end)

    ui = {
        frame = f, scroll = scroll, rows = rows, empty = empty, hint = hint,
        sortBtn = sortBtn, nameBox = nameBox, saveBtn = saveBtn, loadBtn = loadBtn,
        slots = slots, presetScroll = presetScroll, presetRows = presetRows,
        presetEmpty = presetEmpty, newBtn = newBtn, delBtn = delBtn,
    }
    return ui
end

function Battlemon.BuildTeams()
    return build().frame
end

function Battlemon.ShowTeams()
    Battlemon.EnsureData()
    Battlemon.OpenPanel("teams")
    Battlemon.RefreshTeams()
end
