Battlemon = Battlemon or {}

local MAX_TEAM_PRESETS = 20
local SORT_MODES = { "Default", "Dex", "Level" }
local SORT_LABELS = { Default = "Default", Dex = "Dex #", Level = "Level" }

Battlemon.partySortMode = Battlemon.partySortMode or "Default"
Battlemon.teamDraft = Battlemon.teamDraft or {
    selectedIndex = 0,
    name = "",
    party = { 0, 0, 0, 0, 0, 0 },
}

function Battlemon.EnsureProfileDB()
    BattlemonDB = BattlemonDB or {}
    if type(BattlemonDB.favorites) ~= "table" then
        BattlemonDB.favorites = {}
    end
    if type(BattlemonDB.teamPresets) ~= "table" then
        BattlemonDB.teamPresets = {}
    end
    if type(BattlemonDB.battleMusicTheme) ~= "string" then
        BattlemonDB.battleMusicTheme = "random"
    end
end

function Battlemon.IsFavorite(ownedId)
    Battlemon.EnsureProfileDB()
    ownedId = tonumber(ownedId) or 0
    if ownedId <= 0 then
        return false
    end
    for i = 1, #BattlemonDB.favorites do
        if BattlemonDB.favorites[i] == ownedId then
            return true
        end
    end
    return false
end

local function sortFavoriteIds()
    table.sort(BattlemonDB.favorites, function(a, b) return a < b end)
end

function Battlemon.SetFavorite(ownedId, on)
    Battlemon.EnsureProfileDB()
    ownedId = tonumber(ownedId) or 0
    if ownedId <= 0 or not Battlemon.state.owned[ownedId] then
        return false
    end

    local found
    for i = #BattlemonDB.favorites, 1, -1 do
        if BattlemonDB.favorites[i] == ownedId then
            table.remove(BattlemonDB.favorites, i)
            found = true
        end
    end
    if on then
        table.insert(BattlemonDB.favorites, ownedId)
        sortFavoriteIds()
    end
    return true
end

function Battlemon.ToggleFavorite(ownedId)
    return Battlemon.SetFavorite(ownedId, not Battlemon.IsFavorite(ownedId))
end

function Battlemon.SortModeLabel(mode)
    mode = mode or Battlemon.partySortMode or "Default"
    return SORT_LABELS[mode] or "Default"
end

function Battlemon.CyclePartySort()
    local cur = Battlemon.partySortMode or "Default"
    local idx = 1
    for i = 1, #SORT_MODES do
        if SORT_MODES[i] == cur then
            idx = i
            break
        end
    end
    idx = (idx % #SORT_MODES) + 1
    Battlemon.partySortMode = SORT_MODES[idx]
    return Battlemon.partySortMode
end

function Battlemon.GetSortedOwnedRows(mode)
    mode = mode or Battlemon.partySortMode or "Default"
    local rows = {}
    for _, row in pairs(Battlemon.state.owned or {}) do
        table.insert(rows, row)
    end

    local names = {}
    for i = 1, #rows do
        names[rows[i]] = string.lower(Battlemon.FormName(rows[i].formId, rows[i].name) or "")
    end

    table.sort(rows, function(a, b)
        local af = Battlemon.IsFavorite(a.id) and 0 or 1
        local bf = Battlemon.IsFavorite(b.id) and 0 or 1
        if af ~= bf then
            return af < bf
        end
        if mode == "Dex" then
            if (a.formId or 0) ~= (b.formId or 0) then
                return (a.formId or 0) < (b.formId or 0)
            end
            return (a.id or 0) < (b.id or 0)
        end
        if mode == "Level" then
            if (a.level or 1) ~= (b.level or 1) then
                return (a.level or 1) > (b.level or 1)
            end
            if names[a] ~= names[b] then
                return names[a] < names[b]
            end
            return (a.id or 0) < (b.id or 0)
        end
        if names[a] ~= names[b] then
            return names[a] < names[b]
        end
        return (a.id or 0) < (b.id or 0)
    end)
    return rows
end

function Battlemon.ResolvePartyIds(party)
    local out = { 0, 0, 0, 0, 0, 0 }
    if type(party) ~= "table" then
        if type(party) == "string" and party ~= "" then
            local i = 1
            for part in string.gmatch(party, "[^,%s]+") do
                if i <= 6 then
                    out[i] = tonumber(part) or 0
                    i = i + 1
                end
            end
        end
        return out
    end
    for i = 1, 6 do
        out[i] = tonumber(party[i]) or 0
    end
    return out
end

function Battlemon.SanitizeParty(party)
    local src = Battlemon.ResolvePartyIds(party)
    local out = { 0, 0, 0, 0, 0, 0 }
    local seen = {}
    for i = 1, 6 do
        local id = src[i] or 0
        if id > 0 and Battlemon.state.owned[id] and not seen[id] then
            out[i] = id
            seen[id] = true
        end
    end
    return out
end

function Battlemon.GetTeamPresets()
    Battlemon.EnsureProfileDB()
    return BattlemonDB.teamPresets
end

function Battlemon.SaveTeamPreset(name, party, index)
    Battlemon.EnsureProfileDB()
    name = string.gsub(name or "", "^%s*(.-)%s*$", "%1")
    if name == "" then
        return false, "Enter a team name."
    end

    local clean = Battlemon.SanitizeParty(party)
    if clean[1] <= 0 then
        return false, "Slot 1 must be filled."
    end

    local presets = BattlemonDB.teamPresets
    index = tonumber(index) or 0
    local entry = { name = name, party = clean }

    if index >= 1 and index <= #presets then
        presets[index] = entry
    else
        if #presets >= MAX_TEAM_PRESETS then
            return false, string.format("You can save at most %d teams.", MAX_TEAM_PRESETS)
        end
        table.insert(presets, entry)
        index = #presets
    end
    return true, nil, index
end

function Battlemon.RemoveTeamPreset(index)
    Battlemon.EnsureProfileDB()
    index = tonumber(index) or 0
    if index < 1 or index > #BattlemonDB.teamPresets then
        return false
    end
    table.remove(BattlemonDB.teamPresets, index)
    return true
end

function Battlemon.ResetTeamDraft()
    Battlemon.teamDraft.selectedIndex = 0
    Battlemon.teamDraft.name = ""
    Battlemon.teamDraft.party = { 0, 0, 0, 0, 0, 0 }
end

function Battlemon.LoadTeamDraftFromPreset(index)
    local presets = Battlemon.GetTeamPresets()
    index = tonumber(index) or 0
    if index < 1 or index > #presets then
        return false
    end
    local preset = presets[index]
    Battlemon.teamDraft.selectedIndex = index
    Battlemon.teamDraft.name = preset.name or ""
    Battlemon.teamDraft.party = Battlemon.SanitizeParty(preset.party)
    return true
end

function Battlemon.ApplyDraftToParty()
    if Battlemon.InBattle and Battlemon.InBattle() then
        Battlemon.Print("You can't rearrange your party during a battle.")
        return false
    end
    local party = Battlemon.SanitizeParty(Battlemon.teamDraft.party)
    if party[1] <= 0 then
        Battlemon.Print("Slot 1 must be filled before loading a team.")
        return false
    end
    for i = 1, 6 do
        Battlemon.state.partySlots[i] = party[i]
    end
    local parts = {}
    for i = 1, 6 do
        parts[i] = tostring(party[i])
    end
    Battlemon.Send("SETPARTY", table.concat(parts, ","))
    Battlemon.Print("Current party updated.")
    if Battlemon.RefreshParty then
        Battlemon.RefreshParty()
    end
    return true
end

function Battlemon.OwnedFaintTag(row)
    if (row.hp or 0) > 0 then
        return ""
    end
    local secs = row.reviveIn or 0
    if secs <= 0 then
        return "   |cffd05050FAINTED|r"
    elseif secs < 60 then
        return "   |cffd05050FAINTED|r |cff8a8f99" .. secs .. "s|r"
    end
    return string.format("   |cffd05050FAINTED|r |cff8a8f99%dm|r", math.ceil(secs / 60))
end

function Battlemon.PaintOwnedRow(btn, row, selectedId, slotNum, slotStyle)
    btn.ownedId = row.id
    Battlemon.SetPokemonTexture(btn.icon, "Front", Battlemon.FormSprite(row.formId, row.sprite), row.shiny)
    btn.name:SetText(Battlemon.ShinyName(Battlemon.FormName(row.formId, row.name), row.shiny))

    local slotText = ""
    if slotNum then
        if slotStyle == "draft" then
            slotText = string.format("   |cffffd45aSLOT %d|r", slotNum)
        else
            slotText = string.format("   |cffffd45aslot %d|r", slotNum)
        end
    end
    btn.info:SetText(string.format("Lv.%d   |cff6f7480#%d|r%s%s",
        row.level or 1, row.id or 0, slotText, Battlemon.OwnedFaintTag(row)))

    local fav = Battlemon.IsFavorite(row.id)
    btn.star:SetText(fav and "|cffffd200*|r" or "|cff6f7480*|r")

    if row.id == selectedId then
        Battlemon.Fill(btn.bg, 0.34, 0.28, 0.10, 1)
        btn.name:SetTextColor(1, 0.92, 0.55)
    else
        Battlemon.Fill(btn.bg, 0.12, 0.13, 0.17, 1)
        btn.name:SetTextColor(0.94, 0.95, 0.98)
    end
end

function Battlemon.MakeOwnedRow(parent, rowH, onSelect, onStar)
    local btn = CreateFrame("Button", nil, parent)
    btn:SetHeight(rowH - 2)
    btn.bg = btn:CreateTexture(nil, "BACKGROUND")
    btn.bg:SetAllPoints()
    Battlemon.Fill(btn.bg, 0.12, 0.13, 0.17, 1)

    btn.star = CreateFrame("Button", nil, btn)
    btn.star:SetSize(18, rowH - 2)
    btn.star:SetPoint("LEFT", 0, 0)
    btn.star.text = Battlemon.Font(btn.star, 14, "", 1, 0.82, 0.30)
    btn.star.text:SetPoint("CENTER")
    btn.star:SetScript("OnClick", function()
        if onStar then
            onStar(btn.ownedId)
        end
    end)

    btn.icon = btn:CreateTexture(nil, "ARTWORK")
    btn.icon:SetSize(30, 30)
    btn.icon:SetPoint("LEFT", 20, 0)
    btn.name = Battlemon.Font(btn, 14, "", 0.94, 0.95, 0.98)
    btn.name:SetPoint("LEFT", 54, 0)
    btn.name:SetJustifyH("LEFT")
    btn.name:SetWidth(190)
    btn.info = Battlemon.Font(btn, 12, "", 0.78, 0.82, 0.88)
    btn.info:SetPoint("RIGHT", -8, 0)
    btn.info:SetJustifyH("RIGHT")
    btn:SetScript("OnClick", function(self)
        if self.ownedId and onSelect then
            onSelect(self.ownedId)
        end
    end)
    return btn
end

-- Only called after a complete authoritative ownership snapshot, never per chunk.
function Battlemon.PruneRemovedOwned()
    Battlemon.EnsureProfileDB()
    for _, preset in ipairs(BattlemonDB.teamPresets) do
        preset.party = Battlemon.SanitizeParty(preset.party)
    end
    Battlemon.teamDraft.party = Battlemon.SanitizeParty(Battlemon.teamDraft.party)
    for i = #BattlemonDB.favorites, 1, -1 do
        if not Battlemon.state.owned[BattlemonDB.favorites[i]] then
            table.remove(BattlemonDB.favorites, i)
        end
    end
end
