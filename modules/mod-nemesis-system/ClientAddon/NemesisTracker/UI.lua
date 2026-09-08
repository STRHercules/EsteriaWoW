NemesisTracker = NemesisTracker or {}
local NT = NemesisTracker

NT.UI = NT.UI or {}
local UI = NT.UI

local DEFAULT_ROW_HEIGHT = 22
local COMPACT_ROW_HEIGHT = 18
local MAX_ROW_COUNT = 24
local FILTERS = {
    { key = "all", label = "All" },
    { key = "own", label = "Own" },
    { key = "party", label = "Party" },
    { key = "guild", label = "Guild" },
    { key = "public", label = "Public" },
}

local SCOPES = {
    { key = "all", label = "All Zones" },
    { key = "zone", label = "This Map" },
}

local function clamp(value, minValue, maxValue)
    if value < minValue then
        return minValue
    end
    if value > maxValue then
        return maxValue
    end
    return value
end

local function modulo(value, divisor)
    if math.fmod then
        return math.fmod(value, divisor)
    end

    return value - math.floor(value / divisor) * divisor
end

local function createBackdrop(frame)
    frame:SetBackdrop({
        bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
        edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
        tile = true,
        tileSize = 16,
        edgeSize = 12,
        insets = { left = 3, right = 3, top = 3, bottom = 3 },
    })
    frame:SetBackdropColor(0, 0, 0, 0.9)
end

local function relationColor(relation)
    if relation == "own" then
        return 1.0, 0.2, 0.2
    end
    if relation == "party" then
        return 0.3, 0.6, 1.0
    end
    if relation == "guild" then
        return 0.2, 0.9, 0.4
    end
    return 1.0, 0.82, 0.0
end

local function threatColor(threat)
    if threat == "extreme" then
        return 1.0, 0.1, 0.1
    end
    if threat == "high" then
        return 1.0, 0.45, 0.1
    end
    if threat == "medium" then
        return 1.0, 0.82, 0.0
    end
    return 0.4, 1.0, 0.4
end

local function getMarkerTexCoord(rank)
    local iconIndex = math.max(0, math.min(7, (rank or 1) - 1))
    local left = iconIndex * 0.125
    return left, left + 0.125, 0, 0.125
end

function UI:GetRowHeight()
    if NT.db and NT.db.compactList then
        return COMPACT_ROW_HEIGHT
    end

    return DEFAULT_ROW_HEIGHT
end

function UI:LayoutRows()
    if not self.rows or not self.list then
        return
    end

    local rowHeight = self:GetRowHeight()
    local visibleRows = NT:GetVisibleRows()
    self.list:SetHeight((rowHeight + 2) * visibleRows)

    for index, row in ipairs(self.rows) do
        row:ClearAllPoints()
        row:SetHeight(rowHeight)
        row:SetWidth(250)
        if index == 1 then
            row:SetPoint("TOPLEFT", self.list, "TOPLEFT", 0, 0)
        else
            row:SetPoint("TOPLEFT", self.rows[index - 1], "BOTTOMLEFT", 0, -2)
        end
    end
end

local function getDisplayedNemesis()
    local selected = NT:GetSelectedNemesis()
    if selected then
        return selected
    end

    return NT.data.ordered[1]
end

local function getDisplayedZoneInfo()
    local zoneId, zoneName = NT:EnsureDisplayedZone()
    if not zoneId and not zoneName then
        return nil, nil, nil
    end

    return zoneId, zoneName, NT.data.displayedZoneKey
end

local function isNemesisInZone(nemesis, zoneId, zoneName, zoneMapKey)
    if not nemesis then
        return false
    end

    if zoneMapKey and nemesis.zoneKey then
        return nemesis.zoneKey == zoneMapKey
    end

    if zoneId and zoneId ~= 0 then
        return nemesis.zoneId == zoneId
    end

    if zoneName and zoneName ~= "" then
        return nemesis.zoneName == zoneName
    end

    return false
end

local function getDisplayedZoneCount(zoneId, zoneName, zoneMapKey)
    local count = 0
    for _, nemesis in ipairs(NT.data.ordered) do
        if isNemesisInZone(nemesis, zoneId, zoneName, zoneMapKey) then
            count = count + 1
        end
    end

    return count
end

function UI:EnsureMapTiles()
    if self.mapTiles then
        return true
    end

    if not NT.MapData or not NT.MapData.tileCount then
        return false
    end

    self.mapTiles = {}
    for index = 1, NT.MapData.tileCount do
        local tile = self.canvas:CreateTexture(nil, "BACKGROUND")
        tile:SetTexture(nil)
        tile:Hide()
        self.mapTiles[index] = tile
    end

    return true
end

function UI:RefreshMapTiles(width, height, zoneId, zoneName)
    if not self:EnsureMapTiles() or not NT.MapData or not NT.MapData.tileColumns or
        not NT.MapData.tileRows or type(NT.MapData.GetTileTexture) ~= "function" then
        for _, tile in ipairs(self.mapTiles or {}) do
            tile:SetTexture(nil)
            tile:Hide()
        end

        if self.mapFallback then
            self.mapFallback:Show()
        end

        if self.mapZoneText then
            if zoneName and zoneName ~= "" then
                self.mapZoneText:SetText(zoneName)
            else
                self.mapZoneText:SetText("Map data unavailable")
            end
        end

        return
    end

    local tileWidth = width / NT.MapData.tileColumns
    local tileHeight = height / NT.MapData.tileRows
    local hasTexture = false

    for index, tile in ipairs(self.mapTiles) do
        local texturePath = NT.MapData:GetTileTexture(zoneId, zoneName, index)
        if texturePath then
            local column = modulo(index - 1, NT.MapData.tileColumns)
            local row = math.floor((index - 1) / NT.MapData.tileColumns)
            tile:ClearAllPoints()
            tile:SetPoint("TOPLEFT", self.canvas, "TOPLEFT", column * tileWidth, -(row * tileHeight))
            tile:SetWidth(tileWidth)
            tile:SetHeight(tileHeight)
            tile:SetTexture(texturePath)
            tile:SetTexCoord(0, 1, 0, 1)
            tile:Show()
            hasTexture = true
        else
            tile:SetTexture(nil)
            tile:Hide()
        end
    end

    if self.mapFallback then
        if hasTexture then
            self.mapFallback:Hide()
        else
            self.mapFallback:Show()
        end
    end

    if self.mapZoneText then
        if zoneName and zoneName ~= "" then
            self.mapZoneText:SetText(zoneName)
        else
            self.mapZoneText:SetText("No zone selected")
        end
    end
end

function UI:FormatLastSeen(lastSeenAt)
    if not lastSeenAt or lastSeenAt <= 0 then
        return "Unknown"
    end

    local age = math.max(0, time() - lastSeenAt)
    if age < 60 then
        return string.format("%ds ago", age)
    end
    if age < 3600 then
        return string.format("%dm ago", math.floor(age / 60))
    end
    return string.format("%dh ago", math.floor(age / 3600))
end

function UI:RefreshStatus()
    if not self.statusText then
        return
    end

    local total = NT.data.filteredCount or #NT.data.ordered
    local lastSync = NT.data.lastSyncAt > 0 and date("%H:%M:%S", NT.data.lastSyncAt) or "never"
    local state = NT.data.connectionState or "idle"
    local page = NT.data.page or 1
    local maxPage = NT:GetMaxPage()
    local filter = string.upper(NT.data.currentFilter or "all")
    local scope = (NT.data.currentScope or "all") == "zone" and "MAP" or "ALL"
    local zoneLabel = NT.data.displayedZoneName or "None"
    local search = NT.data.currentSearch or ""
    if search ~= "" then
        self.statusText:SetText(string.format("State: %s  Filter: %s  Scope: %s  Search: %s  Tracked: %d  Page: %d/%d  Zone: %s  Last Sync: %s", state, filter, scope, search, total, page, maxPage, zoneLabel, lastSync))
    else
        self.statusText:SetText(string.format("State: %s  Filter: %s  Scope: %s  Tracked: %d  Page: %d/%d  Zone: %s  Last Sync: %s", state, filter, scope, total, page, maxPage, zoneLabel, lastSync))
    end

    if self.pageText then
        self.pageText:SetText(string.format("Page %d/%d", page, maxPage))
    end

    if self.prevPageButton then
        if page > 1 then
            self.prevPageButton:Enable()
        else
            self.prevPageButton:Disable()
        end
    end

    if self.nextPageButton then
        if page < maxPage then
            self.nextPageButton:Enable()
        else
            self.nextPageButton:Disable()
        end
    end

    if self.filterButtons then
        for _, button in ipairs(self.filterButtons) do
            if button.key == (NT.data.currentFilter or "all") then
                button:Disable()
            else
                button:Enable()
            end
        end
    end

    if self.scopeButtons then
        for _, button in ipairs(self.scopeButtons) do
            if button.key == (NT.data.currentScope or "all") then
                button:Disable()
            else
                button:Enable()
            end
        end
    end

    if self.compactButton then
        if NT.db and NT.db.compactList then
            self.compactButton:SetText("Expanded")
        else
            self.compactButton:SetText("Compact")
        end
    end

    if self.searchBox and self.searchBox:GetText() ~= (NT.data.currentSearch or "") then
        self.searchBox:SetText(NT.data.currentSearch or "")
    end
end

function UI:RefreshList()
    self:LayoutRows()

    for index, row in ipairs(self.rows) do
        local nemesis = NT:GetPagedNemesis(index)
        if nemesis then
            row.spawnId = nemesis.spawnId
            row.nemesis = nemesis
            row:Show()
            local r, g, b = relationColor(nemesis.relation)
            row.name:SetTextColor(r, g, b)
            row.name:SetText(nemesis.name)
            row.rank:SetText(string.format("R%d", nemesis.rank or 1))
            row.zone:SetText(nemesis.zoneName or "Unknown")
            row.lastSeen:SetText(self:FormatLastSeen(nemesis.lastSeenAt))
            local alpha = NT:GetVisibilityAlpha(nemesis)
            row:SetAlpha(alpha)
            if NT.data.selectedSpawnId == nemesis.spawnId then
                row:SetBackdropColor(0.25, 0.25, 0.35, 0.85)
            else
                row:SetBackdropColor(0.08, 0.08, 0.08, 0.75)
            end
        else
            row.spawnId = nil
            row.nemesis = nil
            row:SetAlpha(1.0)
            row:Hide()
        end
    end
end

function UI:RefreshDetails()
    if not self.detailText then
        return
    end

    local nemesis = NT:GetSelectedNemesis()
    if not nemesis then
        self.detailHeader:SetTextColor(1, 1, 1)
        self.detailHeader:SetText("Nemesis Details")
        self.detailText:SetText("No nemesis selected")
        return
    end

    self.detailText:SetText(string.format(
        "Name: %s\nLevel: %d\nRank: %d - %s\nZone: %s (%d)\nRelation: %s\nReward: %s\nThreat: %s\nTarget: %s (%d)\nAffixes: %s\nLast Seen: %s\nStatus: %s\nSource: %s\nCoords: %.1f, %.1f, %.1f\nSpawn ID: %s",
        nemesis.name or "Unknown",
        nemesis.level or 0,
        nemesis.rank or 1,
        nemesis.rankTier or "Marked",
        nemesis.zoneName or "Unknown",
        nemesis.zoneId or 0,
        nemesis.relation or "public",
        nemesis.rewardClass or "none",
        nemesis.threatClass or "low",
        nemesis.targetName or "",
        nemesis.targetGuid or 0,
        nemesis.affixText or "None",
        self:FormatLastSeen(nemesis.lastSeenAt),
        NT:GetStalenessState(nemesis),
        nemesis.lastSeenSource or "unknown",
        nemesis.x or 0,
        nemesis.y or 0,
        nemesis.z or 0,
        tostring(nemesis.spawnId or 0)
    ))

    local r, g, b = threatColor(nemesis.threatClass)
    self.detailHeader:SetTextColor(r, g, b)
    self.detailHeader:SetText(nemesis.name or "Nemesis")
end

function UI:RefreshMap()
    if not self.canvas then
        return
    end

    local displayedZoneId, displayedZoneName, displayedZoneKey = getDisplayedZoneInfo()
    local zoneCount = getDisplayedZoneCount(displayedZoneId, displayedZoneName, displayedZoneKey)

    if self.zoomText then
        if zoneCount == 1 then
            self.zoomText:SetText("1 creature")
        else
            self.zoomText:SetText(string.format("%d creatures", zoneCount))
        end
    end

    if self.prevZoneButton then
        if #NT:GetAvailableZones() > 1 then
            self.prevZoneButton:Enable()
        else
            self.prevZoneButton:Disable()
        end
    end

    if self.nextZoneButton then
        if #NT:GetAvailableZones() > 1 then
            self.nextZoneButton:Enable()
        else
            self.nextZoneButton:Disable()
        end
    end

    for _, marker in ipairs(self.markers) do
        marker:Hide()
    end

    local width = self.canvas:GetWidth()
    local height = self.canvas:GetHeight()
    if width <= 0 or height <= 0 then
        return
    end

    self:RefreshMapTiles(width, height, displayedZoneId, displayedZoneName)

    for index, nemesis in ipairs(NT.data.ordered) do
        if isNemesisInZone(nemesis, displayedZoneId, displayedZoneName, displayedZoneKey) then
            local marker = self.markers[index]
            if not marker then
                marker = CreateFrame("Button", nil, self.canvas)
                marker:SetWidth(14)
                marker:SetHeight(14)
                marker.texture = marker:CreateTexture(nil, "ARTWORK")
                marker.texture:SetAllPoints(marker)
                marker:SetScript("OnClick", function(button)
                    NT:SelectNemesis(button.spawnId)
                end)
                marker:RegisterForClicks("LeftButtonUp", "RightButtonUp")
                marker:SetScript("OnEnter", function(button)
                    local target = NT.data.nemeses[button.spawnId]
                    if not target then
                        return
                    end
                    GameTooltip:SetOwner(button, "ANCHOR_RIGHT")
                    GameTooltip:SetText(target.name or "Nemesis")
                    GameTooltip:AddLine(string.format("Level %d  Rank %d - %s", target.level or 0, target.rank or 1, target.rankTier or "Marked"), 1, 1, 1)
                    GameTooltip:AddLine(target.zoneName or "Unknown", 0.8, 0.8, 0.8)
                    GameTooltip:AddLine("Last Seen: " .. UI:FormatLastSeen(target.lastSeenAt), 0.7, 0.9, 0.7)
                    GameTooltip:AddLine("Reward: " .. (target.rewardClass or "none"), 0.8, 0.8, 0.2)
                    GameTooltip:AddLine("Threat: " .. (target.threatClass or "low"), 1.0, 0.4, 0.2)
                    GameTooltip:Show()
                end)
                marker:SetScript("OnLeave", function()
                    GameTooltip:Hide()
                end)
                self.markers[index] = marker
            end

            marker.spawnId = nemesis.spawnId
            local x = clamp(nemesis.mapX or 0.5, 0.03, 0.97)
            local y = clamp(nemesis.mapY or 0.5, 0.03, 0.97)
            marker:ClearAllPoints()
            marker:SetPoint("CENTER", self.canvas, "TOPLEFT", width * x, -(height * y))
            marker:Show()
            marker:SetAlpha(NT:GetVisibilityAlpha(nemesis))

            local r, g, b = relationColor(nemesis.relation)
            marker.texture:SetTexture("Interface\\MINIMAP\\POIIcons")
            marker.texture:SetTexCoord(getMarkerTexCoord(nemesis.rank or 1))
            local tr, tg, tb = threatColor(nemesis.threatClass)
            marker.texture:SetVertexColor((r + tr) / 2, (g + tg) / 2, (b + tb) / 2)
            if NT.data.selectedSpawnId == nemesis.spawnId then
                marker:SetScale(1.1 + ((nemesis.rank or 1) * 0.08))
            else
                marker:SetScale(0.9 + ((nemesis.rank or 1) * 0.05))
            end
        end
    end
end

function UI:RefreshAll()
    self:RefreshStatus()
    self:RefreshList()
    self:RefreshDetails()
    self:RefreshMap()
end

function UI:CreateRow(parent, index)
    local row = CreateFrame("Button", nil, parent)
    row:SetHeight(self:GetRowHeight())
    row:SetWidth(250)
    createBackdrop(row)
    row:SetBackdropColor(0.08, 0.08, 0.08, 0.75)

    row.name = row:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    row.name:SetPoint("LEFT", row, "LEFT", 6, 0)
    row.name:SetWidth(92)
    row.name:SetJustifyH("LEFT")

    row.rank = row:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    row.rank:SetPoint("LEFT", row.name, "RIGHT", 4, 0)
    row.rank:SetWidth(28)

    row.zone = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    row.zone:SetPoint("LEFT", row.rank, "RIGHT", 4, 0)
    row.zone:SetWidth(64)
    row.zone:SetJustifyH("LEFT")

    row.lastSeen = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    row.lastSeen:SetPoint("RIGHT", row, "RIGHT", -6, 0)
    row.lastSeen:SetWidth(46)
    row.lastSeen:SetJustifyH("RIGHT")

    row:RegisterForClicks("LeftButtonUp", "RightButtonUp")
    row:SetScript("OnClick", function(button)
        if button.spawnId then
            NT:SelectNemesis(button.spawnId)
        end
    end)

    row:SetScript("OnDoubleClick", function(button)
        if not button.nemesis then
            return
        end

        DEFAULT_CHAT_FRAME:AddMessage(string.format("Nemesis waypoint: %s - %s (%.1f, %.1f, %.1f)", button.nemesis.name or "Nemesis", button.nemesis.zoneName or "Unknown", button.nemesis.x or 0, button.nemesis.y or 0, button.nemesis.z or 0))
    end)

    row:SetScript("OnEnter", function(button)
        if not button.nemesis then
            return
        end

        local nemesis = button.nemesis
        GameTooltip:SetOwner(button, "ANCHOR_RIGHT")
        GameTooltip:SetText(nemesis.name or "Nemesis")
        GameTooltip:AddLine(string.format("Level %d  Rank %d - %s", nemesis.level or 0, nemesis.rank or 1, nemesis.rankTier or "Marked"), 1, 1, 1)
        GameTooltip:AddLine(string.format("Relation: %s", nemesis.relation or "public"), 0.7, 0.9, 1)
        GameTooltip:AddLine(string.format("Reward: %s  Threat: %s", nemesis.rewardClass or "none", nemesis.threatClass or "low"), 1, 0.82, 0.2)
        GameTooltip:AddLine(string.format("Zone: %s", nemesis.zoneName or "Unknown"), 0.85, 0.85, 0.85)
        GameTooltip:AddLine("Last Seen: " .. self:FormatLastSeen(nemesis.lastSeenAt), 0.7, 0.9, 0.7)
        GameTooltip:AddLine(string.format("Status: %s  Source: %s", NT:GetStalenessState(nemesis), nemesis.lastSeenSource or "unknown"), 0.8, 0.8, 0.8)
        GameTooltip:Show()
    end)

    row:SetScript("OnLeave", function()
        GameTooltip:Hide()
    end)

    self.rows[index] = row
end

function UI:CreateFilterButton(parent, index, filterDef)
    local button = CreateFrame("Button", nil, parent, "UIPanelButtonTemplate")
    button:SetWidth(54)
    button:SetHeight(20)
    if index == 1 then
        button:SetPoint("TOPLEFT", parent, "TOPLEFT", 0, 0)
    else
        button:SetPoint("LEFT", self.filterButtons[index - 1], "RIGHT", 4, 0)
    end
    button:SetText(filterDef.label)
    button.key = filterDef.key
    button:SetScript("OnClick", function()
        NT:SetFilter(filterDef.key)
    end)
    self.filterButtons[index] = button
end

function UI:CreateScopeButton(parent, index, scopeDef)
    local button = CreateFrame("Button", nil, parent, "UIPanelButtonTemplate")
    button:SetWidth(78)
    button:SetHeight(20)
    if index == 1 then
        button:SetPoint("TOPLEFT", parent, "TOPLEFT", 0, -24)
    else
        button:SetPoint("LEFT", self.scopeButtons[index - 1], "RIGHT", 4, 0)
    end
    button:SetText(scopeDef.label)
    button.key = scopeDef.key
    button:SetScript("OnClick", function()
        NT:SetScope(scopeDef.key)
    end)
    self.scopeButtons[index] = button
end

function UI:ShowZoneMenu()
    if not self.zoneMenu then
        self.zoneMenu = CreateFrame("Frame", "NemesisTrackerZoneMenu", UIParent, "UIDropDownMenuTemplate")
    end

    local menu = {}
    local zones = NT:GetAvailableZones()
    if #zones == 0 then
        table.insert(menu, {
            text = "No zones available",
            isTitle = true,
            notCheckable = true,
        })
    else
        table.insert(menu, {
            text = "Select zone",
            isTitle = true,
            notCheckable = true,
        })

        for _, zone in ipairs(zones) do
            table.insert(menu, {
                text = zone.zoneName or "Unknown",
                checked = zone.zoneKey == NT.data.displayedZoneKey,
                func = function()
                    NT:SelectDisplayedZone(zone.zoneId, zone.zoneName, zone.zoneKey)
                end,
            })
        end
    end

    EasyMenu(menu, self.zoneMenu, self.zoneMenuButton, 0, 0, "MENU")
end

function UI:Create()
    if self.frame then
        return
    end

    local frame = CreateFrame("Frame", "NemesisTrackerFrame", UIParent)
    frame:SetClampedToScreen(true)
    frame:SetMovable(true)
    frame:EnableMouse(true)
    frame:RegisterForDrag("LeftButton")
    frame:SetResizable(true)
    frame:SetMinResize(860, 520)
    frame:SetMaxResize(1400, 1000)
    createBackdrop(frame)
    frame:SetWidth(NT.db.window.width or 980)
    frame:SetHeight(NT.db.window.height or 640)
    frame:SetPoint(NT.db.window.point or "CENTER", UIParent, NT.db.window.relativePoint or "CENTER", NT.db.window.x or 0, NT.db.window.y or 0)
    frame:SetScript("OnDragStart", function(self)
        self:StartMoving()
    end)
    frame:SetScript("OnDragStop", function(self)
        self:StopMovingOrSizing()
        local point, _, relativePoint, x, y = self:GetPoint(1)
        NT.db.window.point = point
        NT.db.window.relativePoint = relativePoint
        NT.db.window.x = x
        NT.db.window.y = y
    end)
    frame:Hide()
    self.frame = frame

    local title = frame:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    title:SetPoint("TOPLEFT", frame, "TOPLEFT", 14, -12)
    title:SetText("Nemesis Tracker")

    self.statusText = frame:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    self.statusText:SetPoint("TOPRIGHT", frame, "TOPRIGHT", -44, -16)

    local close = CreateFrame("Button", nil, frame, "UIPanelCloseButton")
    close:SetPoint("TOPRIGHT", frame, "TOPRIGHT", -4, -4)

    local sync = CreateFrame("Button", nil, frame, "UIPanelButtonTemplate")
    sync:SetWidth(90)
    sync:SetHeight(22)
    sync:SetPoint("TOPLEFT", frame, "TOPLEFT", 12, -40)
    sync:SetText("Refresh")
    sync:SetScript("OnClick", function()
        NT:RefreshFromSources()
    end)

    local waypoint = CreateFrame("Button", nil, frame, "UIPanelButtonTemplate")
    waypoint:SetWidth(110)
    waypoint:SetHeight(22)
    waypoint:SetPoint("LEFT", sync, "RIGHT", 8, 0)
    waypoint:SetText("Waypoint")
    waypoint:SetScript("OnClick", function()
        local nemesis = NT:GetSelectedNemesis()
        if not nemesis then
            return
        end
        DEFAULT_CHAT_FRAME:AddMessage(string.format("Nemesis waypoint: %s - %s (%.1f, %.1f, %.1f)", nemesis.name or "Nemesis", nemesis.zoneName or "Unknown", nemesis.x or 0, nemesis.y or 0, nemesis.z or 0))
    end)

    local filters = CreateFrame("Frame", nil, frame)
    filters:SetPoint("TOPLEFT", frame, "TOPLEFT", 12, -68)
    filters:SetWidth(320)
    filters:SetHeight(72)
    self.filterButtons = {}
    for index, filterDef in ipairs(FILTERS) do
        self:CreateFilterButton(filters, index, filterDef)
    end

    self.scopeButtons = {}
    for index, scopeDef in ipairs(SCOPES) do
        self:CreateScopeButton(filters, index, scopeDef)
    end

    self.compactButton = CreateFrame("Button", nil, filters, "UIPanelButtonTemplate")
    self.compactButton:SetWidth(92)
    self.compactButton:SetHeight(20)
    self.compactButton:SetPoint("LEFT", self.scopeButtons[#self.scopeButtons], "RIGHT", 4, 0)
    self.compactButton:SetText("Compact")
    self.compactButton:SetScript("OnClick", function()
        NT:ToggleCompactList()
    end)

    self.searchBox = CreateFrame("EditBox", nil, filters, "InputBoxTemplate")
    self.searchBox:SetAutoFocus(false)
    self.searchBox:SetWidth(244)
    self.searchBox:SetHeight(20)
    self.searchBox:SetPoint("TOPLEFT", filters, "TOPLEFT", 0, -48)
    self.searchBox:SetText(NT.data.currentSearch or "")
    self.searchBox:SetScript("OnEscapePressed", function(editBox)
        editBox:ClearFocus()
    end)
    self.searchBox:SetScript("OnEnterPressed", function(editBox)
        editBox:ClearFocus()
    end)
    self.searchBox:SetScript("OnTextChanged", function(editBox, userInput)
        if userInput then
            NT:SetSearch(editBox:GetText())
        end
    end)

    local list = CreateFrame("Frame", nil, frame)
    list:SetPoint("TOPLEFT", frame, "TOPLEFT", 12, -146)
    list:SetWidth(256)
    list:SetHeight((self:GetRowHeight() + 2) * NT:GetVisibleRows())
    self.list = list

    self.rows = {}
    for index = 1, MAX_ROW_COUNT do
        self:CreateRow(list, index)
    end
    self:LayoutRows()

    local mapPanel = CreateFrame("Frame", nil, frame)
    mapPanel:SetPoint("TOPLEFT", list, "TOPRIGHT", 12, 0)
    mapPanel:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", -12, 160)
    createBackdrop(mapPanel)
    self.mapPanel = mapPanel

    local canvas = CreateFrame("Frame", nil, mapPanel)
    canvas:SetAllPoints(mapPanel)
    canvas:EnableMouse(true)
    self.canvas = canvas

    self.zoomText = mapPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    self.zoomText:SetPoint("TOPRIGHT", mapPanel, "TOPRIGHT", -8, -8)

    self.prevZoneButton = CreateFrame("Button", nil, mapPanel, "UIPanelButtonTemplate")
    self.prevZoneButton:SetWidth(22)
    self.prevZoneButton:SetHeight(20)
    self.prevZoneButton:SetPoint("TOPLEFT", mapPanel, "TOPLEFT", 8, -6)
    self.prevZoneButton:SetText("<")
    self.prevZoneButton:SetScript("OnClick", function()
        NT:ChangeDisplayedZone(-1)
    end)

    self.nextZoneButton = CreateFrame("Button", nil, mapPanel, "UIPanelButtonTemplate")
    self.nextZoneButton:SetWidth(22)
    self.nextZoneButton:SetHeight(20)
    self.nextZoneButton:SetPoint("LEFT", self.prevZoneButton, "RIGHT", 196, 0)
    self.nextZoneButton:SetText(">")
    self.nextZoneButton:SetScript("OnClick", function()
        NT:ChangeDisplayedZone(1)
    end)

    self.zoneMenuButton = CreateFrame("Button", nil, mapPanel, "UIPanelButtonTemplate")
    self.zoneMenuButton:SetWidth(188)
    self.zoneMenuButton:SetHeight(20)
    self.zoneMenuButton:SetPoint("LEFT", self.prevZoneButton, "RIGHT", 8, 0)
    self.zoneMenuButton:SetText("Select Zone")
    self.zoneMenuButton:SetScript("OnClick", function()
        UI:ShowZoneMenu()
    end)
    self.mapZoneText = self.zoneMenuButton

    self.mapFallback = canvas:CreateTexture(nil, "BACKGROUND")
    self.mapFallback:SetAllPoints(canvas)
    self.mapFallback:SetTexture(0.12, 0.12, 0.16, 0.95)

    self.markers = {}

    self.detailHeader = frame:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    self.detailHeader:SetPoint("TOPLEFT", mapPanel, "BOTTOMLEFT", 4, -16)
    self.detailHeader:SetText("Nemesis Details")

    self.prevPageButton = CreateFrame("Button", nil, frame, "UIPanelButtonTemplate")
    self.prevPageButton:SetWidth(26)
    self.prevPageButton:SetHeight(20)
    self.prevPageButton:SetPoint("TOPLEFT", list, "BOTTOMLEFT", 0, -8)
    self.prevPageButton:SetText("<")
    self.prevPageButton:SetScript("OnClick", function()
        NT:ChangePage(-1)
    end)

    self.pageText = frame:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    self.pageText:SetPoint("LEFT", self.prevPageButton, "RIGHT", 8, 0)
    self.pageText:SetText("Page 1/1")

    self.nextPageButton = CreateFrame("Button", nil, frame, "UIPanelButtonTemplate")
    self.nextPageButton:SetWidth(26)
    self.nextPageButton:SetHeight(20)
    self.nextPageButton:SetPoint("LEFT", self.pageText, "RIGHT", 8, 0)
    self.nextPageButton:SetText(">")
    self.nextPageButton:SetScript("OnClick", function()
        NT:ChangePage(1)
    end)

    self.detailText = frame:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    self.detailText:SetPoint("TOPLEFT", self.detailHeader, "BOTTOMLEFT", 0, -8)
    self.detailText:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", -16, 14)
    self.detailText:SetJustifyH("LEFT")
    self.detailText:SetJustifyV("TOP")

    local resize = CreateFrame("Button", nil, frame)
    resize:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", -4, 4)
    resize:SetWidth(16)
    resize:SetHeight(16)
    resize:EnableMouse(true)
    resize:SetNormalTexture("Interface\\ChatFrame\\UI-ChatIM-SizeGrabber-Up")
    resize:SetHighlightTexture("Interface\\ChatFrame\\UI-ChatIM-SizeGrabber-Highlight")
    resize:SetPushedTexture("Interface\\ChatFrame\\UI-ChatIM-SizeGrabber-Down")
    resize:SetScript("OnMouseDown", function()
        frame:StartSizing("BOTTOMRIGHT")
    end)
    resize:SetScript("OnMouseUp", function()
        frame:StopMovingOrSizing()
        NT.db.window.width = frame:GetWidth()
        NT.db.window.height = frame:GetHeight()
        UI:RefreshMap()
    end)
end
