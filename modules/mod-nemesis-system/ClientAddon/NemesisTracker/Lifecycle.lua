NemesisTracker = NemesisTracker or {}
local NT = NemesisTracker

local function parseSpawnIdFromGuid(guid)
    if not guid then
        return nil
    end

    local low = string.match(guid, "(%x+)$")
    if not low then
        return nil
    end

    if string.len(low) > 8 then
        low = string.sub(low, -8)
    end

    return tonumber(low, 16)
end

function NT:RequestSync()
    self:RefreshFromSources()
end

function NT:ToggleWindow()
    if not self.UI or not self.UI.frame then
        return
    end

    if self.UI.frame:IsShown() then
        self.UI.frame:Hide()
    else
        self.UI.frame:Show()
        self.UI:RefreshAll()
    end
end

function NT:InitializeDatabase()
    local defaults = {
        profile = {
            window = { point = "CENTER", relativePoint = "CENTER", x = 0, y = 0, width = 980, height = 640 },
            compactList = false,
            syncScope = "GUILD",
            publicChannelName = "NemesisTracker",
            fadeAfterSeconds = 600,
            staleAfterSeconds = 1800,
            hideAfterSeconds = 7200,
            autoBootstrap = true,
            autoPeerSync = true,
            reportSightingsToServer = true,
            peerSyncMaxEntries = 100,
            reportThrottleSeconds = 20,
            cache = { nemeses = {} },
        },
    }

    self.database = LibStub("AceDB-3.0"):New("NemesisTrackerDB", defaults, true)
    self.db = self.database.profile
    self.db.cache = self.db.cache or {}
    self.db.cache.nemeses = self.db.cache.nemeses or {}
    self.data.nemeses = self.db.cache.nemeses
end

function NT:ToggleCompactList()
    self.db.compactList = not self.db.compactList
    self.data.page = 1
    self:SortNemeses()
    if self.UI then
        self.UI:RefreshAll()
    end
end

function NT:SlashCommand(input)
    input = string.lower(input or "")
    if input == "sync" or input == "refresh" then
        self:RefreshFromSources()
        return
    end
    if input == "peer" then
        self:RequestPeerSync()
        return
    end

    self:ToggleWindow()
end

function NT:RefreshVisibleUI()
    if self.UI and self.UI.frame and self.UI.frame:IsShown() then
        self.UI:RefreshStatus()
        self.UI:RefreshList()
        self.UI:RefreshDetails()
        self.UI:RefreshMap()
    end
end

function NT:RefreshFromSources()
    self:RequestBootstrap()
    self:RequestPeerSync()
end

function NT:TrackKnownUnit(unit)
    if not UnitExists or not UnitExists(unit) then
        return
    end

    local spawnId = parseSpawnIdFromGuid(UnitGUID(unit))
    if spawnId and self.data.nemeses[spawnId] then
        self:ReportSighting(spawnId)
    end
end

function NT:OnInitialize()
    self:InitializeDatabase()
    self:SortNemeses()
    if self.data.ordered[1] then
        self.data.selectedSpawnId = self.data.ordered[1].spawnId
    end

    if self.UI then
        self.UI:Create()
        self.UI:RefreshAll()
    end

    self:RegisterChatCommand("nemesistracker", "SlashCommand")
    self:RegisterChatCommand("ntrack", "SlashCommand")

    if RegisterAddonMessagePrefix then
        RegisterAddonMessagePrefix(self.prefix)
        RegisterAddonMessagePrefix(self.peerPrefix)
    end

    self:RegisterComm(self.peerPrefix, "OnPeerCommReceived")
end

function NT:OnEnable()
    self:RegisterEvent("PLAYER_ENTERING_WORLD")
    self:RegisterEvent("PLAYER_TARGET_CHANGED")
    self:RegisterEvent("UPDATE_MOUSEOVER_UNIT")
    self:RegisterEvent("CHAT_MSG_SYSTEM")
    self:RegisterEvent("CHAT_MSG_ADDON")
    self.refreshTimer = self:ScheduleRepeatingTimer("RefreshVisibleUI", 1)
end

function NT:OnDisable()
    if self.refreshTimer then
        self:CancelTimer(self.refreshTimer)
        self.refreshTimer = nil
    end
end

function NT:PLAYER_ENTERING_WORLD()
    self:ScheduleTimer(function()
        if self.db.autoBootstrap then
            self:RequestBootstrap()
        end
        if self.db.autoPeerSync then
            self:RequestPeerSync()
        end
    end, 2)
end

function NT:PLAYER_TARGET_CHANGED()
    self:TrackKnownUnit("target")
end

function NT:UPDATE_MOUSEOVER_UNIT()
    self:TrackKnownUnit("mouseover")
end

function NT:CHAT_MSG_SYSTEM(_, message)
    self:HandleSystemMessage(message)
end

function NT:CHAT_MSG_ADDON(_, prefix, message)
    if prefix == self.prefix then
        self:ParseServerPayload(message)
    end
end
