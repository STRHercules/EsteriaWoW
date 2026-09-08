NemesisTracker = NemesisTracker or {}
local NT = NemesisTracker

local function zoneKey(zoneId, zoneName)
    if NT.MapData and type(NT.MapData.GetZoneKey) == "function" then
        local key = NT.MapData:GetZoneKey(zoneId, zoneName)
        if key then
            return key
        end
    end

    return string.format("%s:%s", tostring(zoneId or 0), zoneName or "")
end

local function shouldIncludeNemesis(nemesis)
    if not nemesis or NT:ShouldHideNemesis(nemesis) then
        return false
    end

    local filter = NT.data.currentFilter or "all"
    if filter ~= "all" and nemesis.relation ~= filter then
        return false
    end

    local search = string.lower(NT.data.currentSearch or "")
    if search ~= "" then
        local name = string.lower(nemesis.name or "")
        local zone = string.lower(nemesis.zoneName or "")
        local rankTier = string.lower(nemesis.rankTier or "")
        if not string.find(name, search, 1, true) and
            not string.find(zone, search, 1, true) and
            not string.find(rankTier, search, 1, true) then
            return false
        end
    end

    if (NT.data.currentScope or "all") == "zone" then
        return nemesis.zoneKey and nemesis.zoneKey == NT.data.displayedZoneKey
    end

    return true
end

function NT:GetZoneKey(zoneId, zoneName)
    return zoneKey(zoneId, zoneName)
end

function NT:GetNow()
    return time()
end

function NT:GetAge(lastSeenAt)
    if not lastSeenAt or lastSeenAt <= 0 then
        return math.huge
    end

    return math.max(0, self:GetNow() - lastSeenAt)
end

function NT:GetStalenessState(nemesis)
    if not nemesis then
        return "unknown"
    end

    local age = self:GetAge(nemesis.lastSeenAt)
    if age >= (self.db.hideAfterSeconds or 7200) then
        return "hidden"
    end
    if age >= (self.db.staleAfterSeconds or 1800) then
        return "stale"
    end
    if age >= (self.db.fadeAfterSeconds or 600) then
        return "fading"
    end

    return "fresh"
end

function NT:GetVisibilityAlpha(nemesis)
    local state = self:GetStalenessState(nemesis)
    if state == "hidden" then
        return 0.0
    end
    if state == "stale" then
        return 0.35
    end
    if state == "fading" then
        return 0.6
    end

    return 1.0
end

function NT:ShouldHideNemesis(nemesis)
    return self:GetStalenessState(nemesis) == "hidden"
end

function NT:ShouldIncludeNemesis(nemesis)
    return shouldIncludeNemesis(nemesis)
end

function NT:SortNemeses()
    wipe(self.data.ordered)
    for _, nemesis in pairs(self.data.nemeses) do
        if shouldIncludeNemesis(nemesis) then
            table.insert(self.data.ordered, nemesis)
        end
    end

    self.data.filteredCount = #self.data.ordered

    table.sort(self.data.ordered, function(a, b)
        if a.relation ~= b.relation then
            return (self.relationOrder[a.relation] or 99) < (self.relationOrder[b.relation] or 99)
        end

        if (a.rank or 1) ~= (b.rank or 1) then
            return (a.rank or 1) > (b.rank or 1)
        end

        if (a.lastSeenAt or 0) ~= (b.lastSeenAt or 0) then
            return (a.lastSeenAt or 0) > (b.lastSeenAt or 0)
        end

        return (a.name or "") < (b.name or "")
    end)

    local maxPage = self:GetMaxPage()
    if self.data.page > maxPage then
        self.data.page = maxPage
    end
end

function NT:GetSelectedNemesis()
    if not self.data.selectedSpawnId then
        return nil
    end

    local nemesis = self.data.nemeses[self.data.selectedSpawnId]
    if nemesis and not self:ShouldHideNemesis(nemesis) then
        return nemesis
    end

    return nil
end

function NT:GetVisibleRows()
    if self.db and self.db.compactList then
        return 24
    end

    return 18
end

function NT:GetMaxPage()
    local rows = self:GetVisibleRows()
    return math.max(1, math.ceil((#self.data.ordered) / rows))
end

function NT:GetPagedNemesis(index)
    local offset = ((self.data.page or 1) - 1) * self:GetVisibleRows()
    return self.data.ordered[offset + index]
end

function NT:GetAvailableZones()
    local zones = {}
    local seen = {}
    local filter = self.data.currentFilter or "all"

    for _, nemesis in pairs(self.data.nemeses) do
        if not self:ShouldHideNemesis(nemesis) and (filter == "all" or nemesis.relation == filter) then
            local key = zoneKey(nemesis.zoneId, nemesis.zoneName)
            if not seen[key] then
                seen[key] = true
                table.insert(zones, {
                    zoneId = nemesis.zoneId,
                    zoneName = nemesis.zoneName or "Unknown",
                    zoneKey = key,
                })
            end
        end
    end

    table.sort(zones, function(a, b)
        if (a.zoneName or "") ~= (b.zoneName or "") then
            return (a.zoneName or "") < (b.zoneName or "")
        end

        return (a.zoneId or 0) < (b.zoneId or 0)
    end)

    return zones
end

function NT:SetDisplayedZone(zoneId, zoneName, zoneMapKey)
    self.data.displayedZoneId = zoneId
    self.data.displayedZoneName = zoneName
    self.data.displayedZoneKey = zoneMapKey or zoneKey(zoneId, zoneName)
end

function NT:EnsureDisplayedZone()
    local zones = self:GetAvailableZones()
    if #zones == 0 then
        self:SetDisplayedZone(nil, nil)
        return nil, nil
    end

    local currentKey = zoneKey(self.data.displayedZoneId, self.data.displayedZoneName)
    for _, zone in ipairs(zones) do
        if zone.zoneKey == currentKey or zone.zoneKey == self.data.displayedZoneKey then
            self:SetDisplayedZone(zone.zoneId, zone.zoneName, zone.zoneKey)
            return zone.zoneId, zone.zoneName
        end
    end

    local selected = self:GetSelectedNemesis()
    if selected then
        local selectedKey = zoneKey(selected.zoneId, selected.zoneName)
        for _, zone in ipairs(zones) do
            if zone.zoneKey == selectedKey then
                self:SetDisplayedZone(zone.zoneId, zone.zoneName, zone.zoneKey)
                return zone.zoneId, zone.zoneName
            end
        end
    end

    self:SetDisplayedZone(zones[1].zoneId, zones[1].zoneName, zones[1].zoneKey)
    return zones[1].zoneId, zones[1].zoneName
end

function NT:ChangeDisplayedZone(delta)
    local zones = self:GetAvailableZones()
    if #zones == 0 then
        return
    end

    local currentKey = zoneKey(self.data.displayedZoneId, self.data.displayedZoneName)
    local currentIndex = 1
    for index, zone in ipairs(zones) do
        if zone.zoneKey == currentKey or zone.zoneKey == self.data.displayedZoneKey then
            currentIndex = index
            break
        end
    end

    local targetIndex = currentIndex + delta
    if targetIndex < 1 then
        targetIndex = #zones
    elseif targetIndex > #zones then
        targetIndex = 1
    end

    self:SelectDisplayedZone(zones[targetIndex].zoneId, zones[targetIndex].zoneName, zones[targetIndex].zoneKey)
end

function NT:SetFilter(filter)
    self.data.currentFilter = filter or "all"
    self.data.page = 1
    self:SortNemeses()
    if self.data.selectedSpawnId and not self.data.nemeses[self.data.selectedSpawnId] then
        self.data.selectedSpawnId = nil
    end
    if self.data.selectedSpawnId and not shouldIncludeNemesis(self.data.nemeses[self.data.selectedSpawnId]) then
        self.data.selectedSpawnId = nil
    end
    if not self.data.selectedSpawnId and self.data.ordered[1] then
        self.data.selectedSpawnId = self.data.ordered[1].spawnId
    end
    if self.UI then
        self.UI:RefreshAll()
    end
end

function NT:SetSearch(search)
    self.data.currentSearch = string.lower(search or "")
    self.data.page = 1
    self:SortNemeses()
    if self.data.selectedSpawnId and not self.data.nemeses[self.data.selectedSpawnId] then
        self.data.selectedSpawnId = nil
    end
    if self.data.selectedSpawnId and not shouldIncludeNemesis(self.data.nemeses[self.data.selectedSpawnId]) then
        self.data.selectedSpawnId = nil
    end
    if not self.data.selectedSpawnId and self.data.ordered[1] then
        self.data.selectedSpawnId = self.data.ordered[1].spawnId
    end
    if self.UI then
        self.UI:RefreshAll()
    end
end

function NT:SetScope(scope)
    if scope ~= "zone" then
        scope = "all"
    end

    self.data.currentScope = scope
    self.data.page = 1
    self:SortNemeses()
    if self.data.selectedSpawnId and not self.data.nemeses[self.data.selectedSpawnId] then
        self.data.selectedSpawnId = nil
    end
    if self.data.selectedSpawnId and not shouldIncludeNemesis(self.data.nemeses[self.data.selectedSpawnId]) then
        self.data.selectedSpawnId = nil
    end
    if not self.data.selectedSpawnId and self.data.ordered[1] then
        self.data.selectedSpawnId = self.data.ordered[1].spawnId
    end
    if self.UI then
        self.UI:RefreshAll()
    end
end

function NT:SelectDisplayedZone(zoneId, zoneName, zoneMapKey)
    self:SetDisplayedZone(zoneId, zoneName, zoneMapKey)
    if (self.data.currentScope or "all") == "zone" then
        self.data.page = 1
        self:SortNemeses()
        if self.data.selectedSpawnId and not self.data.nemeses[self.data.selectedSpawnId] then
            self.data.selectedSpawnId = nil
        end
        if self.data.selectedSpawnId and not shouldIncludeNemesis(self.data.nemeses[self.data.selectedSpawnId]) then
            self.data.selectedSpawnId = nil
        end
        if not self.data.selectedSpawnId and self.data.ordered[1] then
            self.data.selectedSpawnId = self.data.ordered[1].spawnId
        end
    end
    if self.UI then
        self.UI:RefreshAll()
    end
end

function NT:ChangePage(delta)
    local targetPage = math.min(self:GetMaxPage(), math.max(1, (self.data.page or 1) + delta))
    if targetPage == self.data.page then
        return
    end

    self.data.page = targetPage
    if self.UI then
        self.UI:RefreshList()
        self.UI:RefreshStatus()
    end
end

function NT:CenterOnNemesis(spawnId)
    local nemesis = spawnId and self.data.nemeses[spawnId] or nil
    if not nemesis then
        return
    end

    self:SetDisplayedZone(nemesis.zoneId, nemesis.zoneName)
end

function NT:SelectNemesis(spawnId)
    if spawnId and self.data.nemeses[spawnId] and not self:ShouldHideNemesis(self.data.nemeses[spawnId]) then
        self.data.selectedSpawnId = spawnId
    elseif not self.data.selectedSpawnId and self.data.ordered[1] then
        self.data.selectedSpawnId = self.data.ordered[1].spawnId
    end

    if self.data.selectedSpawnId then
        self:CenterOnNemesis(self.data.selectedSpawnId)
    end

    if self.UI then
        self.UI:RefreshAll()
    end
end

function NT:GetPeerSyncCandidates()
    local candidates = {}
    for _, nemesis in pairs(self.data.nemeses) do
        if not self:ShouldHideNemesis(nemesis) and (nemesis.lastSeenAt or 0) > 0 then
            table.insert(candidates, nemesis)
        end
    end

    table.sort(candidates, function(a, b)
        if (a.lastSeenAt or 0) ~= (b.lastSeenAt or 0) then
            return (a.lastSeenAt or 0) > (b.lastSeenAt or 0)
        end

        return (a.rank or 1) > (b.rank or 1)
    end)

    local maxEntries = self.db.peerSyncMaxEntries or 100
    while #candidates > maxEntries do
        table.remove(candidates)
    end

    return candidates
end
