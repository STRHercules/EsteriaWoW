NemesisTracker = NemesisTracker or {}
local NT = NemesisTracker

local function splitPreserveEmpty(message, delimiter)
    local result = {}
    if message == nil then
        return result
    end

    local startIndex = 1
    while true do
        local delimiterIndex = string.find(message, delimiter, startIndex, true)
        if not delimiterIndex then
            table.insert(result, string.sub(message, startIndex))
            break
        end

        table.insert(result, string.sub(message, startIndex, delimiterIndex - 1))
        startIndex = delimiterIndex + string.len(delimiter)

        if startIndex > string.len(message) + 1 then
            table.insert(result, "")
            break
        end
    end

    return result
end

local function joinFields(fields, startIndex, delimiter)
    if not fields or not startIndex or startIndex > #fields then
        return ""
    end

    return table.concat(fields, delimiter or ":", startIndex)
end

local function shortName(name)
    return string.match(name or "", "^[^-]+") or (name or "")
end

local function sanitizeField(value)
    value = tostring(value or "")
    value = string.gsub(value, ":", ";")
    value = string.gsub(value, "|", "/")
    value = string.gsub(value, "\t", " ")
    value = string.gsub(value, "\r", " ")
    value = string.gsub(value, "\n", " ")
    return value
end

local function normalizeRelation(value)
    if value == "own" or value == "party" or value == "guild" then
        return value
    end

    return "public"
end

function NT:BuildCommandChannel()
    if IsInGuild and IsInGuild() then
        return "GUILD"
    end
    if GetNumRaidMembers and GetNumRaidMembers() > 0 then
        return "RAID"
    end
    if GetNumPartyMembers and GetNumPartyMembers() > 0 then
        return "PARTY"
    end

    return "SAY"
end

function NT:SendServerCommand(commandText)
    SendChatMessage(commandText, self:BuildCommandChannel())
end

function NT:BeginBootstrap(count)
    self.data.bootstrapExpected = tonumber(count) or 0
    self.data.bootstrapActive = true
    self.data.connectionState = "bootstrap"
    self.data.lastSyncAt = self:GetNow()
    if self.UI then
        self.UI:RefreshStatus()
    end
end

function NT:FinalizeBootstrap()
    self.data.bootstrapActive = false
    self.data.connectionState = "live"
    self:SortNemeses()
    if (not self.data.selectedSpawnId or self:ShouldHideNemesis(self.data.nemeses[self.data.selectedSpawnId])) and self.data.ordered[1] then
        self.data.selectedSpawnId = self.data.ordered[1].spawnId
    end
    if self.UI then
        self.UI:RefreshAll()
    end
end

function NT:ShouldReplaceLocation(existing, incomingTime, incomingSource)
    if not existing then
        return true
    end

    local existingTime = existing.lastSeenAt or 0
    if incomingTime > existingTime then
        return true
    end
    if incomingTime < existingTime then
        return false
    end

    return (self.sourceOrder[incomingSource] or 0) >= (self.sourceOrder[existing.lastSeenSource] or 0)
end

function NT:UpsertNemesisFromFields(fields, startIndex, source)
    local spawnId = tonumber(fields[startIndex])
    if not spawnId then
        return nil
    end

    local existing = self.data.nemeses[spawnId]
    local incoming = {
        spawnId = spawnId,
        creatureEntry = tonumber(fields[startIndex + 1]) or 0,
        name = fields[startIndex + 2] or "Unknown",
        mapId = tonumber(fields[startIndex + 3]) or 0,
        zoneId = tonumber(fields[startIndex + 4]) or 0,
        zoneName = fields[startIndex + 5] or "Unknown",
        x = tonumber(fields[startIndex + 6]) or 0,
        y = tonumber(fields[startIndex + 7]) or 0,
        z = tonumber(fields[startIndex + 8]) or 0,
        mapX = tonumber(fields[startIndex + 9]) or 0.5,
        mapY = tonumber(fields[startIndex + 10]) or 0.5,
        level = tonumber(fields[startIndex + 11]) or 0,
        rank = tonumber(fields[startIndex + 12]) or 1,
        rankTier = fields[startIndex + 13] or "Marked",
        affixMask = tonumber(fields[startIndex + 14]) or 0,
        affixText = fields[startIndex + 15] or "None",
        targetGuid = tonumber(fields[startIndex + 16]) or 0,
        targetName = fields[startIndex + 17] or "",
        relation = normalizeRelation(fields[startIndex + 18]),
        rewardClass = fields[startIndex + 19] or "none",
        threatClass = fields[startIndex + 20] or "low",
        lastSeenAt = tonumber(fields[startIndex + 21]) or 0,
        lastSeenSource = source,
        isAlive = true,
        removeReason = nil,
    }
    incoming.zoneKey = self:GetZoneKey(incoming.zoneId, incoming.zoneName)

    if incoming.lastSeenAt <= 0 then
        incoming.lastSeenAt = existing and existing.lastSeenAt or self:GetNow()
    end

    if existing then
        if (existing.rank or 1) > incoming.rank then
            incoming.rank = existing.rank or incoming.rank
            incoming.rankTier = existing.rankTier or incoming.rankTier
        end

        if not self:ShouldReplaceLocation(existing, incoming.lastSeenAt, source) then
            incoming.mapId = existing.mapId or incoming.mapId
            incoming.zoneId = existing.zoneId or incoming.zoneId
            incoming.zoneName = existing.zoneName or incoming.zoneName
            incoming.zoneKey = existing.zoneKey or incoming.zoneKey
            incoming.x = existing.x or incoming.x
            incoming.y = existing.y or incoming.y
            incoming.z = existing.z or incoming.z
            incoming.mapX = existing.mapX or incoming.mapX
            incoming.mapY = existing.mapY or incoming.mapY
            incoming.lastSeenAt = existing.lastSeenAt or incoming.lastSeenAt
            incoming.lastSeenSource = existing.lastSeenSource or incoming.lastSeenSource
        end

        if source == "peer-sync" then
            incoming.relation = existing.relation or incoming.relation
            incoming.rewardClass = existing.rewardClass or incoming.rewardClass
            incoming.threatClass = existing.threatClass or incoming.threatClass
        end
    end

    self.data.nemeses[spawnId] = incoming

    if not self.data.selectedSpawnId then
        self.data.selectedSpawnId = spawnId
    end

    self:SortNemeses()
    if self.UI then
        self.UI:RefreshAll()
    end

    return incoming
end

function NT:RemoveNemesis(spawnId, reason)
    if not spawnId then
        return
    end

    local old = self.data.nemeses[spawnId]
    if old then
        old.removeReason = reason
    end

    self.data.nemeses[spawnId] = nil
    if self.data.selectedSpawnId == spawnId then
        self.data.selectedSpawnId = nil
    end
    self:SortNemeses()
    if not self.data.selectedSpawnId and self.data.ordered[1] then
        self.data.selectedSpawnId = self.data.ordered[1].spawnId
    end
    if self.UI then
        self.UI:RefreshAll()
    end
end

function NT:HandleChunk(message)
    local fields = splitPreserveEmpty(message, ":")
    if fields[1] ~= "V2" or fields[2] ~= "CHUNK" then
        return
    end

    local chunkId = fields[3]
    local part = tonumber(fields[4]) or 0
    local total = tonumber(fields[5]) or 0
    local payload = joinFields(fields, 6, ":")

    if not chunkId or chunkId == "" or part <= 0 or total <= 0 then
        return
    end

    if not self.data.chunks[chunkId] then
        self.data.chunks[chunkId] = { total = total, parts = {} }
    end

    local state = self.data.chunks[chunkId]
    if state.total ~= total then
        state.total = total
    end
    state.parts[part] = payload

    local count = 0
    for _ in pairs(state.parts) do
        count = count + 1
    end

    if count < state.total then
        return
    end

    local rebuilt = ""
    for index = 1, state.total do
        rebuilt = rebuilt .. (state.parts[index] or "")
    end

    self.data.chunks[chunkId] = nil
    self:ParseServerPayload(rebuilt)
end

function NT:GetPeerDistributionTarget()
    local scope = string.upper(self.db.syncScope or "GUILD")
    if scope == "PARTY" and GetNumPartyMembers and GetNumPartyMembers() > 0 then
        return "PARTY", nil
    end
    if scope == "RAID" and GetNumRaidMembers and GetNumRaidMembers() > 0 then
        return "RAID", nil
    end
    if scope == "PUBLIC" and GetChannelName then
        local channelId = GetChannelName(self.db.publicChannelName or "NemesisTracker")
        if channelId and channelId ~= 0 then
            return "CHANNEL", channelId
        end
    end
    if IsInGuild and IsInGuild() then
        return "GUILD", nil
    end
    if GetNumRaidMembers and GetNumRaidMembers() > 0 then
        return "RAID", nil
    end
    if GetNumPartyMembers and GetNumPartyMembers() > 0 then
        return "PARTY", nil
    end

    return nil, nil
end

function NT:ShareValidatedNemesis(nemesis)
    if not nemesis then
        return
    end

    local distribution, target = self:GetPeerDistributionTarget()
    if not distribution then
        return
    end

    local message = string.format(
        "ENT:%d:%d:%s:%d:%d:%s:%.1f:%.1f:%.1f:%.2f:%.2f:%d:%d:%s:%d:%s:%d:%s:%s:%s:%s:%d",
        nemesis.spawnId or 0,
        nemesis.creatureEntry or 0,
        sanitizeField(nemesis.name),
        nemesis.mapId or 0,
        nemesis.zoneId or 0,
        sanitizeField(nemesis.zoneName),
        nemesis.x or 0,
        nemesis.y or 0,
        nemesis.z or 0,
        nemesis.mapX or 0.5,
        nemesis.mapY or 0.5,
        nemesis.level or 0,
        nemesis.rank or 1,
        sanitizeField(nemesis.rankTier),
        nemesis.affixMask or 0,
        sanitizeField(nemesis.affixText),
        nemesis.targetGuid or 0,
        sanitizeField(nemesis.targetName),
        sanitizeField(nemesis.relation),
        sanitizeField(nemesis.rewardClass),
        sanitizeField(nemesis.threatClass),
        nemesis.lastSeenAt or 0)
    self:SendCommMessage(self.peerPrefix, message, distribution, target, "NORMAL")
end

function NT:ParseServerPayload(payload)
    if not payload or payload == "" then
        return
    end

    local fields = splitPreserveEmpty(payload, ":")
    if fields[1] ~= "V2" then
        return
    end

    local opcode = fields[2]
    if not opcode then
        return
    end

    if opcode == "CHUNK" then
        self:HandleChunk(payload)
        return
    end
    if opcode == "HELLO" then
        self.data.lastSyncAt = self:GetNow()
        self.data.connectionState = "connected"
        self.data.lastServerTime = tonumber(fields[5]) or 0
        if self.UI then
            self.UI:RefreshStatus()
        end
        return
    end
    if opcode == "BOOTSTRAP_BEGIN" then
        self:BeginBootstrap(fields[3])
        return
    end
    if opcode == "BOOTSTRAP_ENTRY" then
        self:UpsertNemesisFromFields(fields, 3, "server-bootstrap")
        return
    end
    if opcode == "BOOTSTRAP_END" then
        self:FinalizeBootstrap()
        return
    end
    if opcode == "RANK5_BROADCAST" then
        self:UpsertNemesisFromFields(fields, 3, "rank5-broadcast")
        return
    end
    if opcode == "UPSERT_VALIDATED" then
        local nemesis = self:UpsertNemesisFromFields(fields, 3, "server-validated")
        self:ShareValidatedNemesis(nemesis)
        return
    end
    if opcode == "REMOVE" then
        self:RemoveNemesis(tonumber(fields[3]), fields[4])
    end
end

function NT:HandleSystemMessage(message)
    if not message then
        return
    end

    local prefix = self.prefix .. "\t"
    if string.sub(message, 1, string.len(prefix)) ~= prefix then
        return
    end

    self:ParseServerPayload(string.sub(message, string.len(prefix) + 1))
end

function NT:RequestBootstrap()
    self.data.connectionState = "requesting"
    self.data.lastSyncAt = self:GetNow()
    if self.UI then
        self.UI:RefreshStatus()
    end
    self:SendServerCommand(".nemesis addon bootstrap")
end

function NT:RequestPeerSync()
    local distribution, target = self:GetPeerDistributionTarget()
    if not distribution then
        return
    end

    self.data.connectionState = "peer-sync"
    self:SendCommMessage(self.peerPrefix, string.format("REQ:%d", self:GetNow()), distribution, target, "BULK")
    if self.UI then
        self.UI:RefreshStatus()
    end
end

function NT:RespondToPeerSync(sender)
    if not sender or sender == "" then
        return
    end

    for _, nemesis in ipairs(self:GetPeerSyncCandidates()) do
        local message = string.format(
            "ENT:%d:%d:%s:%d:%d:%s:%.1f:%.1f:%.1f:%.2f:%.2f:%d:%d:%s:%d:%s:%d:%s:%s:%s:%s:%d",
            nemesis.spawnId or 0,
            nemesis.creatureEntry or 0,
            sanitizeField(nemesis.name),
            nemesis.mapId or 0,
            nemesis.zoneId or 0,
            sanitizeField(nemesis.zoneName),
            nemesis.x or 0,
            nemesis.y or 0,
            nemesis.z or 0,
            nemesis.mapX or 0.5,
            nemesis.mapY or 0.5,
            nemesis.level or 0,
            nemesis.rank or 1,
            sanitizeField(nemesis.rankTier),
            nemesis.affixMask or 0,
            sanitizeField(nemesis.affixText),
            nemesis.targetGuid or 0,
            sanitizeField(nemesis.targetName),
            sanitizeField(nemesis.relation),
            sanitizeField(nemesis.rewardClass),
            sanitizeField(nemesis.threatClass),
            nemesis.lastSeenAt or 0)
        self:SendCommMessage(self.peerPrefix, message, "WHISPER", sender, "BULK")
    end

    self:SendCommMessage(self.peerPrefix, string.format("DONE:%d", self:GetNow()), "WHISPER", sender, "NORMAL")
end

function NT:OnPeerCommReceived(prefix, message, distribution, sender)
    if prefix ~= self.peerPrefix or not message or shortName(sender) == shortName(UnitName("player")) then
        return
    end

    local fields = splitPreserveEmpty(message, ":")
    if fields[1] == "REQ" then
        self:RespondToPeerSync(sender)
        return
    end
    if fields[1] == "ENT" then
        self:UpsertNemesisFromFields(fields, 2, "peer-sync")
        self.data.lastSyncAt = self:GetNow()
        self.data.connectionState = "live"
        return
    end
    if fields[1] == "DONE" then
        self.data.lastSyncAt = self:GetNow()
        self.data.connectionState = "live"
        if self.UI then
            self.UI:RefreshStatus()
        end
        return
    end
    if fields[1] == "DEL" then
        self:RemoveNemesis(tonumber(fields[2]), fields[3])
    end
end

function NT:ReportSighting(spawnId)
    if not spawnId or not self.db.reportSightingsToServer then
        return
    end

    local now = self:GetNow()
    local throttle = self.db.reportThrottleSeconds or 20
    local lastReportAt = self.data.lastReportBySpawnId[spawnId] or 0
    if lastReportAt + throttle > now then
        return
    end

    self.data.lastReportBySpawnId[spawnId] = now
    self:SendServerCommand(string.format(".nemesis addon report %d", spawnId))
end
