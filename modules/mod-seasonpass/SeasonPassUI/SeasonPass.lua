-- SeasonPassUI v4 — Season-Pass-Fenster im authentischen WoW-3.3.5-Stil.
-- Zweisprachig (DE/EN, folgt der Client-Sprache, per Knopf umschaltbar,
-- dauerhaft gespeichert). Sechs Tabs, Traumtausch-Würfel, Mutator- und
-- Sturm-Anzeige, Stufen-Fanfare. Kisten & Co. meldet der Server.

local BP = {
    points = 0, tier = 0, claimed = 0, claimedEpic = 0,
    perTier = BP_TIER_COST or 100, maxTier = BP_MAX_TIER or 100,
    weekend = 0, prestige = 0, streak = 0, pity = 0, welcomed = 1, page = 1,
    prestigeEnabled = 0,
    renown = 0, renownPoints = 0, renownPer = 100,
    supply = nil,
    weekly = {}, rerollFree = 0,
    runes = {}, runeSlots = 3,
    ach = {},
    events = nil,
}

local lastTier = nil
local lastPrestige = nil

local CELLS_PER_PAGE = 10
local NUM_PAGES = math.ceil(BP.maxTier / CELLS_PER_PAGE)

local ICON_GOLD    = "Interface\\Icons\\INV_Misc_Coin_02"
local ICON_TITLE   = "Interface\\Icons\\INV_Scroll_11"
local ICON_CHEST   = "Interface\\Icons\\INV_Box_02"
local ICON_UNKNOWN = "Interface\\Icons\\INV_Misc_QuestionMark"

local WEEKLY_ICONS = {
    [0]  = "Interface\\Icons\\Ability_DualWield",
    [1]  = "Interface\\Icons\\Ability_Warrior_Challange",
    [2]  = "Interface\\Icons\\INV_Misc_Head_Dragon_01",
    [3]  = "Interface\\Icons\\INV_Misc_Book_08",
    [4]  = "Interface\\Icons\\Spell_ChargePositive",
    [5]  = "Interface\\Icons\\INV_BannerPVP_02",
    [6]  = "Interface\\Icons\\Ability_Duelist",
    [7]  = "Interface\\Icons\\Ability_Hunter_SniperShot",
    [8]  = "Interface\\Icons\\INV_Misc_Coin_02",
    [9]  = "Interface\\Icons\\INV_Misc_Map_01",
    [10] = "Interface\\Icons\\Spell_Nature_WispSplode",
    [11] = "Interface\\Icons\\INV_Misc_Bone_HumanSkull_01",
    [12] = "Interface\\Icons\\INV_Misc_Head_Dragon_01",
}

-- Erfolgs-Icons nach Art (kind)
local ACH_ICONS = {
    [0]  = "Interface\\Icons\\INV_Misc_Head_Dragon_01",
    [1]  = "Interface\\Icons\\INV_Misc_Bone_HumanSkull_01",
    [2]  = "Interface\\Icons\\INV_Misc_Rune_01",
    [3]  = "Interface\\Icons\\INV_Misc_Note_02",
    [4]  = "Interface\\Icons\\Ability_Warrior_Challange",
    [5]  = "Interface\\Icons\\Ability_Hunter_SniperShot",
    [6]  = "Interface\\Icons\\INV_Misc_Key_03",
    [7]  = "Interface\\Icons\\Spell_ChargePositive",
    [8]  = "Interface\\Icons\\INV_Misc_Coin_17",
    [9]  = "Interface\\Icons\\INV_Misc_PocketWatch_01",
    [10] = "Interface\\Icons\\INV_Misc_Map_01",
    [12] = "Interface\\Icons\\INV_Crate_02",
    [13] = "Interface\\Icons\\INV_Box_02",
}

local function PlayerClassToken()
    local _, token = UnitClass("player")
    return token
end

local function EpicRewardFor(tier)
    local r = BP_REWARDS[tier]
    if not r or not r.epic then return nil end
    if r.epic.set then
        local set = BP_CLASS_SET[PlayerClassToken()]
        local piece = set and set[tier]
        if piece then
            return { type = 0, id = piece.id, count = 1, name = piece.name, en = piece.en, set = true }
        end
        return { type = 0, id = 0, count = 1, name = r.epic.name, en = r.epic.en, set = true }
    end
    return r.epic
end

-- ---------------------------------------------------------------------------
--  Stufen-Fanfare
-- ---------------------------------------------------------------------------
local banner = CreateFrame("Frame", nil, UIParent)
banner:SetWidth(500)
banner:SetHeight(60)
banner:SetPoint("TOP", 0, -200)
banner:SetFrameStrata("HIGH")
banner:Hide()
local bannerText = banner:CreateFontString(nil, "OVERLAY", "GameFontNormalHuge")
bannerText:SetPoint("CENTER", 0, 0)
local bannerTime = 0
banner:SetScript("OnUpdate", function(self, elapsed)
    bannerTime = bannerTime + elapsed
    if bannerTime > 3.5 then
        self:Hide()
    elseif bannerTime > 2.5 then
        self:SetAlpha(1 - (bannerTime - 2.5))
    end
end)

local function TierFanfare(newTier, isPrestige)
    PlaySoundFile("Sound\\Interface\\LevelUp.wav")
    if isPrestige then
        bannerText:SetText("|cffFF8800" .. string.format(BPL("fanfare_prestige"), newTier) .. "|r")
    else
        bannerText:SetText("|cffFFD700" .. string.format(BPL("fanfare"), newTier) .. "|r")
    end
    bannerTime = 0
    banner:SetAlpha(1)
    banner:Show()
end

-- ---------------------------------------------------------------------------
--  Hauptfenster
-- ---------------------------------------------------------------------------
local frame = CreateFrame("Frame", "SeasonPassFrame", UIParent)
frame:SetWidth(760)
frame:SetHeight(560)
frame:SetPoint("CENTER", 0, 10)
frame:SetBackdrop({
    edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
    tile = true, tileSize = 32, edgeSize = 32,
})
frame:SetMovable(true)
frame:EnableMouse(true)
frame:RegisterForDrag("LeftButton")
frame:SetScript("OnDragStart", function(self) self:StartMoving() end)
frame:SetScript("OnDragStop", function(self) self:StopMovingOrSizing() end)
frame:Hide()
tinsert(UISpecialFrames, "SeasonPassFrame")

local bg = frame:CreateTexture(nil, "BACKGROUND")
bg:SetTexture("Interface\\AchievementFrame\\UI-Achievement-Parchment-Horizontal")
bg:SetPoint("TOPLEFT", 11, -11)
bg:SetPoint("BOTTOMRIGHT", -11, 11)
bg:SetTexCoord(0, 1, 0, 1)

local header = frame:CreateTexture(nil, "ARTWORK")
header:SetTexture("Interface\\DialogFrame\\UI-DialogBox-Header")
header:SetWidth(400)
header:SetHeight(68)
header:SetPoint("TOP", 0, 14)

local title = frame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
title:SetPoint("TOP", header, "TOP", 0, -15)

local subtitle = frame:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
subtitle:SetPoint("TOP", header, "BOTTOM", 0, 16)

local closeBtn = CreateFrame("Button", nil, frame, "UIPanelCloseButton")
closeBtn:SetPoint("TOPRIGHT", -4, -4)

-- Sprachknopf DE/EN (persistent, meldet die Wahl auch dem Server)
local langBtn = CreateFrame("Button", nil, frame, "UIPanelButtonTemplate")
langBtn:SetWidth(52)
langBtn:SetHeight(20)
langBtn:SetPoint("TOPLEFT", 14, -14)
langBtn:SetScript("OnClick", function()
    local newLang = BP_Lang() == "de" and "en" or "de"
    if not SeasonPassDB then SeasonPassDB = {} end
    SeasonPassDB.lang = newLang
    SendChatMessage(".bp lang " .. newLang, "SAY")
    DEFAULT_CHAT_FRAME:AddMessage("|cffFFD700[Season Pass]|r " .. (BP_LOCALE[newLang].lang_note))
    ReloadUI()
end)

local bar = CreateFrame("StatusBar", nil, frame)
bar:SetWidth(360)
bar:SetHeight(18)
bar:SetPoint("TOP", 0, -66)
bar:SetStatusBarTexture("Interface\\TargetingFrame\\UI-StatusBar")
bar:SetStatusBarColor(1, 0.82, 0)
bar:SetMinMaxValues(0, BP.perTier)
bar:SetValue(0)

local barBG = bar:CreateTexture(nil, "BACKGROUND")
barBG:SetAllPoints()
barBG:SetTexture("Interface\\TargetingFrame\\UI-StatusBar")
barBG:SetVertexColor(0.15, 0.1, 0, 0.8)

local barBorder = bar:CreateTexture(nil, "OVERLAY")
barBorder:SetTexture("Interface\\CastingBar\\UI-CastingBar-Border")
barBorder:SetWidth(460)
barBorder:SetHeight(60)
barBorder:SetPoint("CENTER", bar, "CENTER", 0, 1)

local spark = bar:CreateTexture(nil, "OVERLAY")
spark:SetTexture("Interface\\CastingBar\\UI-CastingBar-Spark")
spark:SetBlendMode("ADD")
spark:SetWidth(24)
spark:SetHeight(40)

local barText = bar:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
barText:SetPoint("CENTER", 0, 0)

local infoText = frame:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
infoText:SetPoint("TOP", bar, "BOTTOM", 0, -12)

local contents = {}
for i = 1, 11 do
    local c = CreateFrame("Frame", nil, frame)
    c:SetPoint("TOPLEFT", 0, 0)
    c:SetPoint("BOTTOMRIGHT", 0, 0)
    if i > 1 then c:Hide() end
    contents[i] = c
end
local cRewards, cWeekly, cRunes, cSet, cEvents, cAch, cChar, cColl, cShop =
    contents[1], contents[2], contents[3], contents[4], contents[5],
    contents[6], contents[7], contents[8], contents[9]
local cChest = contents[10]
local cPara = contents[11]

-- ===========================================================================
--  TAB 1: Belohnungen
-- ===========================================================================
local cells = {}

local function RewardTooltip(self)
    if not self.tierNum or not self.reward then return end
    local r = self.reward
    GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
    if r.type == 0 and r.id > 0 then
        GameTooltip:SetHyperlink("item:" .. r.id)
        GameTooltip:AddLine(" ")
    else
        GameTooltip:AddLine(BPName(r), 1, 0.82, 0)
    end
    GameTooltip:AddLine(string.format(BPL("tier_label"), self.tierNum) ..
        (self.isEpic and "|cffA335EE" .. BPL("hero_tag") .. "|r" or ""), 0.6, 0.6, 1)
    if self.state == "claimed" then
        GameTooltip:AddLine(BPL("already"), 0, 1, 0)
    elseif self.state == "claimable" then
        GameTooltip:AddLine(BPL("claim_now"), 1, 0.82, 0)
    else
        local need = self.tierNum * BP.perTier - BP.points
        if need > 0 then
            GameTooltip:AddLine(string.format(BPL("need_points"), need), 0.9, 0.2, 0.2)
        end
    end
    GameTooltip:Show()
end

local function CellOnLeave() GameTooltip:Hide() end

-- Klick auf einen abholbaren Slot holt sofort alles Fällige ab
local function CellClaimClick(self)
    if self.state == "claimable" then
        PlaySound("LOOTWINDOWCOINSOUND")
        SendChatMessage(".bp claim", "SAY")
    end
end

for i = 1, CELLS_PER_PAGE do
    local col = (i - 1) % 5
    local row = math.floor((i - 1) / 5)
    local baseX = 62 + col * 136
    local baseY = -128 - row * 168

    local name = "BPCellF" .. i
    local cell = CreateFrame("Button", name, cRewards, "ItemButtonTemplate")
    cell:SetScale(1.3)
    cell:SetPoint("TOPLEFT", baseX / 1.3, baseY / 1.3)
    cell.iconTex = _G[name .. "IconTexture"]

    cell.shield = cell:CreateTexture(nil, "OVERLAY")
    cell.shield:SetTexture("Interface\\AchievementFrame\\UI-Achievement-Shields")
    cell.shield:SetTexCoord(0, 0.5, 0, 0.45)
    cell.shield:SetWidth(30)
    cell.shield:SetHeight(30)
    cell.shield:SetPoint("TOP", cell, "TOP", 0, 24)
    cell.shield:Hide()

    cell.tierText = cell:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    cell.tierText:SetPoint("TOP", cell, "TOP", 0, 16)

    cell.glow = cell:CreateTexture(nil, "OVERLAY")
    cell.glow:SetTexture("Interface\\Buttons\\UI-ActionButton-Border")
    cell.glow:SetBlendMode("ADD")
    cell.glow:SetWidth(66)
    cell.glow:SetHeight(66)
    cell.glow:SetPoint("CENTER", cell, "CENTER", 0, 0)
    cell.glow:Hide()

    cell.check = cell:CreateTexture(nil, "OVERLAY")
    cell.check:SetTexture("Interface\\RaidFrame\\ReadyCheck-Ready")
    cell.check:SetWidth(20)
    cell.check:SetHeight(20)
    cell.check:SetPoint("BOTTOMRIGHT", 6, -4)
    cell.check:Hide()

    cell.nameText = cell:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    cell.nameText:SetPoint("TOP", cell, "BOTTOM", 0, -3)
    cell.nameText:SetWidth(86)
    cell.nameText:SetHeight(24)

    cell:SetScript("OnEnter", RewardTooltip)
    cell:SetScript("OnLeave", CellOnLeave)
    cell:SetScript("OnClick", CellClaimClick)

    local ename = "BPCellE" .. i
    local ecell = CreateFrame("Button", ename, cRewards, "ItemButtonTemplate")
    ecell:SetScale(0.95)
    ecell:SetPoint("TOPLEFT", (baseX + 58) / 0.95, (baseY - 8) / 0.95)
    ecell.iconTex = _G[ename .. "IconTexture"]
    ecell.isEpic = true

    ecell.glow = ecell:CreateTexture(nil, "OVERLAY")
    ecell.glow:SetTexture("Interface\\Buttons\\UI-ActionButton-Border")
    ecell.glow:SetBlendMode("ADD")
    ecell.glow:SetWidth(60)
    ecell.glow:SetHeight(60)
    ecell.glow:SetPoint("CENTER", 0, 0)
    ecell.glow:Hide()

    ecell.check = ecell:CreateTexture(nil, "OVERLAY")
    ecell.check:SetTexture("Interface\\RaidFrame\\ReadyCheck-Ready")
    ecell.check:SetWidth(16)
    ecell.check:SetHeight(16)
    ecell.check:SetPoint("BOTTOMRIGHT", 4, -2)
    ecell.check:Hide()

    ecell:SetScript("OnEnter", RewardTooltip)
    ecell:SetScript("OnLeave", CellOnLeave)
    ecell:SetScript("OnClick", CellClaimClick)

    cells[i] = { free = cell, epic = ecell }
end

-- Stufe 0: Willkommenspaket als klickbarer Geschenk-Slot
local welcomeBtn = CreateFrame("Button", "BPWelcomeBtn", cRewards, "ItemButtonTemplate")
welcomeBtn:SetPoint("TOPLEFT", 30, -64)
welcomeBtn.iconTex = _G["BPWelcomeBtnIconTexture"]
welcomeBtn.iconTex:SetTexture("Interface\\Icons\\INV_Misc_Gift_01")

welcomeBtn.tierText = welcomeBtn:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
welcomeBtn.tierText:SetPoint("TOP", welcomeBtn, "TOP", 0, 14)
welcomeBtn.tierText:SetText("0")

welcomeBtn.glow = welcomeBtn:CreateTexture(nil, "OVERLAY")
welcomeBtn.glow:SetTexture("Interface\\Buttons\\UI-ActionButton-Border")
welcomeBtn.glow:SetBlendMode("ADD")
welcomeBtn.glow:SetWidth(62)
welcomeBtn.glow:SetHeight(62)
welcomeBtn.glow:SetPoint("CENTER", 0, 0)

welcomeBtn.check = welcomeBtn:CreateTexture(nil, "OVERLAY")
welcomeBtn.check:SetTexture("Interface\\RaidFrame\\ReadyCheck-Ready")
welcomeBtn.check:SetWidth(18)
welcomeBtn.check:SetHeight(18)
welcomeBtn.check:SetPoint("BOTTOMRIGHT", 5, -3)
welcomeBtn.check:Hide()

welcomeBtn:SetScript("OnClick", function()
    if BP.welcomed == 0 then
        PlaySound("LOOTWINDOWCOINSOUND")
        SendChatMessage(".bp welcome", "SAY")
    end
end)
welcomeBtn:SetScript("OnEnter", function(self)
    GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
    GameTooltip:AddLine(BPL("welcome_slot"), 1, 0.82, 0)
    for _, w in ipairs(BP_WELCOME or {}) do
        GameTooltip:AddLine("  " .. BPName(w), 1, 1, 1)
    end
    if BP.welcomed == 1 then
        GameTooltip:AddLine(BPL("welcome_claimed"), 0, 1, 0)
    else
        GameTooltip:AddLine(BPL("welcome_click"), 1, 0.82, 0)
    end
    GameTooltip:Show()
end)
welcomeBtn:SetScript("OnLeave", CellOnLeave)

local claimBtn = CreateFrame("Button", nil, cRewards, "UIPanelButtonTemplate")
claimBtn:SetWidth(220)
claimBtn:SetHeight(26)
claimBtn:SetPoint("BOTTOM", 0, 62)
claimBtn:SetScript("OnClick", function()
    PlaySound("LOOTWINDOWCOINSOUND")
    SendChatMessage(".bp claim", "SAY")
end)

local pageText = cRewards:CreateFontString(nil, "OVERLAY", "GameFontNormal")
pageText:SetPoint("BOTTOM", 0, 40)

local prevBtn = CreateFrame("Button", nil, cRewards)
prevBtn:SetWidth(32)
prevBtn:SetHeight(32)
prevBtn:SetPoint("BOTTOM", -140, 34)
prevBtn:SetNormalTexture("Interface\\Buttons\\UI-SpellbookIcon-PrevPage-Up")
prevBtn:SetPushedTexture("Interface\\Buttons\\UI-SpellbookIcon-PrevPage-Down")
prevBtn:SetDisabledTexture("Interface\\Buttons\\UI-SpellbookIcon-PrevPage-Disabled")
prevBtn:SetHighlightTexture("Interface\\Buttons\\UI-Common-MouseHilight", "ADD")

local nextBtn = CreateFrame("Button", nil, cRewards)
nextBtn:SetWidth(32)
nextBtn:SetHeight(32)
nextBtn:SetPoint("BOTTOM", 140, 34)
nextBtn:SetNormalTexture("Interface\\Buttons\\UI-SpellbookIcon-NextPage-Up")
nextBtn:SetPushedTexture("Interface\\Buttons\\UI-SpellbookIcon-NextPage-Down")
nextBtn:SetDisabledTexture("Interface\\Buttons\\UI-SpellbookIcon-NextPage-Disabled")
nextBtn:SetHighlightTexture("Interface\\Buttons\\UI-Common-MouseHilight", "ADD")

local function GetRewardIcon(r)
    if not r then return ICON_UNKNOWN end
    if r.type == 1 then return ICON_GOLD end
    if r.type == 2 then return ICON_TITLE end
    if r.type == 3 then return ICON_CHEST end
    local icon = GetItemIcon and r.id > 0 and GetItemIcon(r.id)
    return icon or ICON_UNKNOWN
end

local function SetCellState(cellObj, tierNum, claimedUpTo)
    if tierNum <= claimedUpTo then
        cellObj.state = "claimed"
        cellObj.iconTex:SetDesaturated(false)
        cellObj.iconTex:SetVertexColor(1, 1, 1)
        cellObj.glow:Hide()
        cellObj.check:Show()
        return "claimed"
    elseif tierNum <= BP.tier then
        cellObj.state = "claimable"
        cellObj.iconTex:SetDesaturated(false)
        cellObj.iconTex:SetVertexColor(1, 1, 1)
        cellObj.glow:Show()
        cellObj.check:Hide()
        return "claimable"
    else
        cellObj.state = "locked"
        cellObj.iconTex:SetDesaturated(true)
        cellObj.iconTex:SetVertexColor(0.6, 0.6, 0.6)
        cellObj.glow:Hide()
        cellObj.check:Hide()
        return "locked"
    end
end

local function RefreshRewards()
    if BP.welcomed == 1 then
        welcomeBtn.glow:Hide()
        welcomeBtn.check:Show()
        welcomeBtn.iconTex:SetDesaturated(false)
    else
        welcomeBtn.glow:Show()
        welcomeBtn.check:Hide()
        welcomeBtn.iconTex:SetDesaturated(false)
    end

    pageText:SetText(string.format(BPL("page"), BP.page, NUM_PAGES))
    if BP.page <= 1 then prevBtn:Disable() else prevBtn:Enable() end
    if BP.page >= NUM_PAGES then nextBtn:Disable() else nextBtn:Enable() end

    for i = 1, CELLS_PER_PAGE do
        local pair = cells[i]
        local cell, ecell = pair.free, pair.epic
        local tierNum = (BP.page - 1) * CELLS_PER_PAGE + i
        if tierNum > BP.maxTier then
            cell:Hide()
            ecell:Hide()
        else
            cell:Show()
            cell.tierNum = tierNum
            local rw = BP_REWARDS[tierNum]
            local r = rw and rw.free
            cell.reward = r
            local label = r and BPName(r) or ""
            if rw and rw.chest then
                label = label .. " |cff00CCFF+ " .. BPName(rw.chest) .. "|r"
            end
            cell.nameText:SetText(label)
            cell.iconTex:SetTexture(GetRewardIcon(r))

            if tierNum % 5 == 0 then
                cell.shield:Show()
                cell.tierText:SetPoint("TOP", cell, "TOP", 0, 21)
                cell.tierText:SetText("|cffFFFFFF" .. tierNum .. "|r")
            else
                cell.shield:Hide()
                cell.tierText:SetPoint("TOP", cell, "TOP", 0, 16)
                cell.tierText:SetText(tierNum)
            end

            local s = SetCellState(cell, tierNum, BP.claimed)
            if s == "claimed" then
                cell.nameText:SetTextColor(0.2, 0.9, 0.2)
            elseif s == "claimable" then
                cell.nameText:SetTextColor(1, 0.82, 0)
            else
                cell.nameText:SetTextColor(0.45, 0.42, 0.35)
            end

            local er = EpicRewardFor(tierNum)
            ecell.reward = er
            ecell.tierNum = tierNum
            if not er then
                ecell:Hide()
            else
                ecell:Show()
                ecell.iconTex:SetTexture(GetRewardIcon(er))
                SetCellState(ecell, tierNum, BP.claimedEpic)
            end
        end
    end

    local due = (BP.tier - BP.claimed) + (BP.tier - BP.claimedEpic)
    if due > 0 then
        claimBtn:Enable()
        claimBtn:SetText(string.format(BPL("claimN"), due))
    else
        claimBtn:Disable()
        claimBtn:SetText(BPL("claimed_all"))
    end
end

-- ===========================================================================
--  TAB 2: Wochenziele (mit Traumtausch-Würfel)
-- ===========================================================================
local weeklyHead = cWeekly:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
weeklyHead:SetPoint("TOP", 0, -118)

local weeklySub = cWeekly:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
weeklySub:SetPoint("TOP", weeklyHead, "BOTTOM", 0, -4)

local weeklyRows = {}
for i = 1, 3 do
    local row = CreateFrame("Frame", nil, cWeekly)
    row:SetWidth(560)
    row:SetHeight(64)
    row:SetPoint("TOP", 0, -158 - (i - 1) * 78)

    row.icon = row:CreateTexture(nil, "ARTWORK")
    row.icon:SetWidth(36)
    row.icon:SetHeight(36)
    row.icon:SetPoint("LEFT", 0, 6)

    row.name = row:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    row.name:SetPoint("TOPLEFT", 48, -2)
    row.name:SetJustifyH("LEFT")
    row.name:SetWidth(420)

    row.pts = row:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    row.pts:SetPoint("TOPRIGHT", 0, -2)

    row.barFrame = CreateFrame("Frame", nil, row)
    row.barFrame:SetWidth(390)
    row.barFrame:SetHeight(18)
    row.barFrame:SetPoint("TOPLEFT", 48, -24)
    row.barFrame:SetBackdrop({
        bgFile = "Interface\\ChatFrame\\ChatFrameBackground",
        edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
        tile = true, tileSize = 8, edgeSize = 12,
        insets = { left = 3, right = 3, top = 3, bottom = 3 },
    })
    row.barFrame:SetBackdropColor(0, 0, 0, 0.6)

    row.bar = CreateFrame("StatusBar", nil, row.barFrame)
    row.bar:SetPoint("TOPLEFT", 3, -3)
    row.bar:SetPoint("BOTTOMRIGHT", -3, 3)
    row.bar:SetStatusBarTexture("Interface\\TargetingFrame\\UI-StatusBar")
    row.bar:SetStatusBarColor(1, 0.82, 0)

    row.progText = row.bar:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    row.progText:SetPoint("CENTER", 0, 0)

    row.check = row:CreateTexture(nil, "OVERLAY")
    row.check:SetTexture("Interface\\RaidFrame\\ReadyCheck-Ready")
    row.check:SetWidth(24)
    row.check:SetHeight(24)
    row.check:SetPoint("LEFT", row.barFrame, "RIGHT", 8, 0)
    row.check:Hide()

    -- Traumtausch-Würfel (1x pro Woche ein Ziel neu würfeln)
    row.reroll = CreateFrame("Button", nil, row)
    row.reroll:SetWidth(26)
    row.reroll:SetHeight(26)
    row.reroll:SetPoint("LEFT", row.barFrame, "RIGHT", 8, 0)
    row.reroll:SetNormalTexture("Interface\\Buttons\\UI-RotationLeft-Button-Up")
    row.reroll:SetPushedTexture("Interface\\Buttons\\UI-RotationLeft-Button-Down")
    row.reroll:SetHighlightTexture("Interface\\Buttons\\UI-Common-MouseHilight", "ADD")
    row.reroll:Hide()
    local slotIdx = i
    row.reroll:SetScript("OnClick", function()
        PlaySound("igAbiliityPageTurn")
        SendChatMessage(".bp reroll " .. slotIdx, "SAY")
    end)
    row.reroll:SetScript("OnEnter", function(self)
        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        GameTooltip:AddLine(BPL("reroll_tip"), 1, 0.82, 0)
        GameTooltip:Show()
    end)
    row.reroll:SetScript("OnLeave", function() GameTooltip:Hide() end)

    weeklyRows[i] = row
end

-- Täglicher Versorgungsauftrag (SoD "Waylaid Supplies")
local supplyRow = CreateFrame("Frame", nil, cWeekly)
supplyRow:SetWidth(560)
supplyRow:SetHeight(48)
supplyRow:SetPoint("TOP", 0, -394)

supplyRow.icon = supplyRow:CreateTexture(nil, "ARTWORK")
supplyRow.icon:SetWidth(32)
supplyRow.icon:SetHeight(32)
supplyRow.icon:SetPoint("LEFT", 0, 4)

supplyRow.head = supplyRow:CreateFontString(nil, "OVERLAY", "GameFontNormal")
supplyRow.head:SetPoint("TOPLEFT", 44, -2)
supplyRow.head:SetJustifyH("LEFT")

supplyRow.text = supplyRow:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
supplyRow.text:SetPoint("TOPLEFT", 44, -20)
supplyRow.text:SetJustifyH("LEFT")
supplyRow.text:SetWidth(380)

supplyRow.btn = CreateFrame("Button", nil, supplyRow, "UIPanelButtonTemplate")
supplyRow.btn:SetWidth(110)
supplyRow.btn:SetHeight(24)
supplyRow.btn:SetPoint("RIGHT", 0, 0)
supplyRow.btn:SetScript("OnClick", function()
    PlaySound("LOOTWINDOWCOINSOUND")
    SendChatMessage(".bp deliver", "SAY")
end)

supplyRow.check = supplyRow:CreateTexture(nil, "OVERLAY")
supplyRow.check:SetTexture("Interface\\RaidFrame\\ReadyCheck-Ready")
supplyRow.check:SetWidth(24)
supplyRow.check:SetHeight(24)
supplyRow.check:SetPoint("RIGHT", supplyRow.btn, "LEFT", -8, 0)
supplyRow.check:Hide()

-- Täglicher Angelauftrag (Schlingendorntal-Extravaganza-Gefühl)
local fishRow = CreateFrame("Frame", nil, cWeekly)
fishRow:SetWidth(560)
fishRow:SetHeight(48)
fishRow:SetPoint("TOP", 0, -448)

fishRow.icon = fishRow:CreateTexture(nil, "ARTWORK")
fishRow.icon:SetWidth(32)
fishRow.icon:SetHeight(32)
fishRow.icon:SetPoint("LEFT", 0, 4)

fishRow.head = fishRow:CreateFontString(nil, "OVERLAY", "GameFontNormal")
fishRow.head:SetPoint("TOPLEFT", 44, -2)
fishRow.head:SetJustifyH("LEFT")

fishRow.text = fishRow:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
fishRow.text:SetPoint("TOPLEFT", 44, -20)
fishRow.text:SetJustifyH("LEFT")
fishRow.text:SetWidth(460)

fishRow.check = fishRow:CreateTexture(nil, "OVERLAY")
fishRow.check:SetTexture("Interface\\RaidFrame\\ReadyCheck-Ready")
fishRow.check:SetWidth(24)
fishRow.check:SetHeight(24)
fishRow.check:SetPoint("RIGHT", 0, 0)
fishRow.check:Hide()

local function RefreshFish()
    fishRow.head:SetText("|cffFFD700" .. BPL("fish_head") .. "|r")
    local fi = BP.fish
    if not fi then
        fishRow.icon:SetTexture(ICON_UNKNOWN)
        fishRow.text:SetText("|cff888888" .. BPL("wait_sync") .. "|r")
        fishRow.check:Hide()
        return
    end
    local iname = GetItemInfo(fi.id)
    fishRow.icon:SetTexture(GetItemIcon and GetItemIcon(fi.id) or ICON_UNKNOWN)
    fishRow.text:SetText(string.format(BPL("fish_text"), fi.need, iname or ("#" .. fi.id))
        .. "  (" .. fi.count .. "/" .. fi.need .. ")  —  "
        .. string.format(BPL("supply_reward"), fi.points, math.floor(fi.gold / 10000))
        .. " |cff00CCFF" .. BPL("fish_bonus") .. "|r")
    if fi.count >= fi.need then
        fishRow.check:Show()
    else
        fishRow.check:Hide()
    end
end

local function RefreshSupply()
    supplyRow.head:SetText("|cffFFD700" .. BPL("supply_head") .. "|r")
    supplyRow.btn:SetText(BPL("supply_deliver"))
    local s = BP.supply
    if not s then
        supplyRow.icon:SetTexture(ICON_UNKNOWN)
        supplyRow.text:SetText("|cff888888" .. BPL("wait_sync") .. "|r")
        supplyRow.btn:Disable()
        supplyRow.check:Hide()
        return
    end
    local iname = GetItemInfo(s.id)
    supplyRow.icon:SetTexture(GetItemIcon and GetItemIcon(s.id) or ICON_UNKNOWN)
    supplyRow.text:SetText(string.format(BPL("supply_text"), s.count, iname or ("#" .. s.id))
        .. "  —  " .. string.format(BPL("supply_reward"), s.points, math.floor(s.gold / 10000)))
    if s.done == 1 then
        supplyRow.btn:Disable()
        supplyRow.check:Show()
    else
        supplyRow.btn:Enable()
        supplyRow.check:Hide()
    end
end

local function RefreshWeekly()
    RefreshSupply()
    RefreshFish()
    for i = 1, 3 do
        local row = weeklyRows[i]
        local w = BP.weekly[i - 1]
        local def = w and BP_WEEKLY and BP_WEEKLY[w.id]
        if not w or not def then
            row.name:SetText("|cff888888" .. BPL("weekly_nodata") .. "|r")
            row.icon:SetTexture(ICON_UNKNOWN)
            row.bar:SetMinMaxValues(0, 1)
            row.bar:SetValue(0)
            row.progText:SetText("")
            row.pts:SetText("")
            row.check:Hide()
            row.reroll:Hide()
        else
            row.icon:SetTexture(WEEKLY_ICONS[def.type] or ICON_UNKNOWN)
            row.pts:SetText("|cffFFD700+" .. def.points .. "|r")
            row.bar:SetMinMaxValues(0, w.goal > 0 and w.goal or 1)
            row.bar:SetValue(w.prog)
            if w.done == 1 then
                row.name:SetText("|cff33FF33" .. BPName(def) .. "|r")
                row.bar:SetStatusBarColor(0.2, 0.8, 0.2)
                row.progText:SetText(BPL("done_excl"))
                row.check:Show()
                row.reroll:Hide()
            else
                row.name:SetText(BPName(def))
                row.bar:SetStatusBarColor(1, 0.82, 0)
                row.progText:SetText(w.prog .. " / " .. w.goal)
                row.check:Hide()
                if BP.rerollFree == 1 then row.reroll:Show() else row.reroll:Hide() end
            end
        end
    end
end

-- ===========================================================================
--  TAB 3: Runen
-- ===========================================================================
local runesHead = cRunes:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
runesHead:SetPoint("TOP", 0, -114)

local runesSub = cRunes:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
runesSub:SetPoint("TOP", runesHead, "BOTTOM", 0, -2)

-- Startfähigkeit: einmalige Gratis-Wahl einer Fähigkeit, die die Klasse nicht hat
StaticPopupDialogs["BP_STARTRUNE_CONFIRM"] = {
    text = "?",
    button1 = YES,
    button2 = NO,
    OnAccept = function()
        if BP._pickRune then
            SendChatMessage(".bp startrune " .. BP._pickRune, "SAY")
        end
    end,
    timeout = 0,
    whileDead = 1,
    hideOnEscape = 1,
}

local startLabel = cRunes:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
startLabel:SetPoint("TOP", runesSub, "BOTTOM", 0, -6)

local startBtns = {}
do
    local abilityIds = {}
    for id, def in pairs(BP_RUNES or {}) do
        if def.kind == 1 then table.insert(abilityIds, id) end
    end
    table.sort(abilityIds)
    for idx, id in ipairs(abilityIds) do
        local b = CreateFrame("Button", nil, cRunes)
        b:SetWidth(28)
        b:SetHeight(28)
        b:SetPoint("TOPLEFT", 178 + (idx - 1) * 34, -168)
        local tex = b:CreateTexture(nil, "BACKGROUND")
        tex:SetAllPoints()
        tex:SetTexture(BP_RUNES[id].icon)
        tex:SetTexCoord(0.07, 0.93, 0.07, 0.93)
        b:SetHighlightTexture("Interface\\Buttons\\ButtonHilight-Square", "ADD")
        b.runeId = id
        b:SetScript("OnClick", function(self)
            BP._pickRune = self.runeId
            StaticPopupDialogs["BP_STARTRUNE_CONFIRM"].text =
                string.format(BPL("start_confirm"), BPName(BP_RUNES[self.runeId]))
            StaticPopup_Show("BP_STARTRUNE_CONFIRM")
        end)
        b:SetScript("OnEnter", function(self)
            local def = BP_RUNES[self.runeId]
            GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
            GameTooltip:AddLine(BPName(def), 1, 0.82, 0)
            GameTooltip:AddLine((BP_Lang() == "en" and def.desc_en) or def.desc, 1, 1, 1, true)
            GameTooltip:Show()
        end)
        b:SetScript("OnLeave", function() GameTooltip:Hide() end)
        table.insert(startBtns, b)
    end
end

local runeRows = {}
local runeIds = {}
for id in pairs(BP_RUNES or {}) do table.insert(runeIds, id) end
table.sort(runeIds)

for idx, id in ipairs(runeIds) do
    local col = (idx - 1) % 2
    local row = math.floor((idx - 1) / 2)
    local r = CreateFrame("Button", nil, cRunes)
    r:SetWidth(330)
    r:SetHeight(26)
    r:SetPoint("TOPLEFT", 45 + col * 345, -204 - row * 27)
    r:SetHighlightTexture("Interface\\Buttons\\UI-Common-MouseHilight", "ADD")
    local runeId = id
    r:SetScript("OnClick", function()
        PlaySound("igMainMenuOptionCheckBoxOn")
        SendChatMessage(".bp rune " .. runeId, "SAY")
    end)
    r:SetScript("OnEnter", function(self)
        local def = BP_RUNES[runeId]
        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        GameTooltip:AddLine(BPName(def), 1, 0.82, 0)
        local d = (BP_Lang() == "en" and def.desc_en) or def.desc
        GameTooltip:AddLine(d, 1, 1, 1, true)
        GameTooltip:AddLine(math.floor(def.cost / 10000) .. " Gold", 0.8, 0.8, 0.8)
        GameTooltip:Show()
    end)
    r:SetScript("OnLeave", function() GameTooltip:Hide() end)

    r.icon = r:CreateTexture(nil, "ARTWORK")
    r.icon:SetWidth(22)
    r.icon:SetHeight(22)
    r.icon:SetPoint("LEFT", 0, 0)

    r.name = r:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    r.name:SetPoint("LEFT", 30, 0)
    r.name:SetJustifyH("LEFT")
    r.name:SetWidth(300)

    runeRows[idx] = { frame = r, runeId = id }
end

local runesFoot = cRunes:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
runesFoot:SetPoint("BOTTOM", 0, 38)

local function RefreshRunes()
    local active = {}
    for _, id in ipairs(BP.runes) do active[id] = true end
    runesSub:SetText(string.format(BPL("runes_sub"), #BP.runes, BP.runeSlots))

    if BP.startRune == nil then
        startLabel:SetText("")
        for _, b in ipairs(startBtns) do b:Hide() end
    elseif BP.startRune == 0 then
        startLabel:SetText("|cffA335EE" .. BPL("start_head") .. "|r")
        for _, b in ipairs(startBtns) do
            if IsSpellKnown and IsSpellKnown(BP_RUNES[b.runeId].spell) then
                b:Hide()
            else
                b:Show()
            end
        end
    else
        local sdef = BP_RUNES[BP.startRune]
        startLabel:SetText("|cffA335EE" .. string.format(BPL("start_done"), sdef and BPName(sdef) or "?") .. "|r")
        for _, b in ipairs(startBtns) do b:Hide() end
    end
    for _, entry in ipairs(runeRows) do
        local def = BP_RUNES[entry.runeId]
        local f = entry.frame
        f.icon:SetTexture(def.icon)
        local prefix = def.kind == 1 and "|cffA335EE[F]|r " or ""
        if active[entry.runeId] then
            f.name:SetText(prefix .. "|cff33FF33" .. BPName(def) .. " " .. BPL("active_tag") .. "|r")
            f.icon:SetDesaturated(false)
        else
            f.name:SetText(prefix .. BPName(def) .. " |cff888888(" .. math.floor(def.cost / 10000) .. " G)|r")
            f.icon:SetDesaturated(true)
        end
    end
end

-- ===========================================================================
--  TAB 4: Klassenset
-- ===========================================================================
local setHead = cSet:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
setHead:SetPoint("TOP", 0, -118)

local setSub = cSet:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
setSub:SetPoint("TOP", setHead, "BOTTOM", 0, -4)

local setRows = {}
for i = 1, 4 do
    local name = "BPSetCell" .. i
    local btn = CreateFrame("Button", name, cSet, "ItemButtonTemplate")
    btn:SetPoint("TOPLEFT", 200, -166 - (i - 1) * 72)
    btn.iconTex = _G[name .. "IconTexture"]

    btn.label = cSet:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    btn.label:SetPoint("TOPLEFT", btn, "TOPRIGHT", 14, -4)
    btn.label:SetJustifyH("LEFT")

    btn.status = cSet:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    btn.status:SetPoint("TOPLEFT", btn, "TOPRIGHT", 14, -22)
    btn.status:SetJustifyH("LEFT")

    btn:SetScript("OnEnter", function(self)
        if self.itemId and self.itemId > 0 then
            GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
            GameTooltip:SetHyperlink("item:" .. self.itemId)
            GameTooltip:Show()
        end
    end)
    btn:SetScript("OnLeave", CellOnLeave)
    setRows[i] = btn
end

local function RefreshSet()
    local className = UnitClass("player")
    setHead:SetText(string.format(BPL("set_head"), className or "?"))
    local set = BP_CLASS_SET[PlayerClassToken()]
    if not set then return end
    local tiers = {}
    for tier in pairs(set) do table.insert(tiers, tier) end
    table.sort(tiers)
    for i, tier in ipairs(tiers) do
        local piece = set[tier]
        local btn = setRows[i]
        if btn and piece then
            btn.itemId = piece.id
            btn.iconTex:SetTexture(GetItemIcon and GetItemIcon(piece.id) or ICON_UNKNOWN)
            btn.label:SetText("|cffA335EE" .. BPName(piece) .. "|r  |cff888888(" .. piece.slot .. ")|r")
            if tier <= BP.claimedEpic then
                btn.status:SetText("|cff33FF33" .. BPL("st_claimed") .. "|r — " .. tier)
                btn.iconTex:SetDesaturated(false)
            elseif tier <= BP.tier then
                btn.status:SetText("|cffFFD700" .. BPL("st_claimable") .. "|r — " .. tier)
                btn.iconTex:SetDesaturated(false)
            else
                btn.status:SetText("|cff888888" .. string.format(BPL("st_hero"), tier) .. "|r")
                btn.iconTex:SetDesaturated(true)
            end
        end
    end
end

-- ===========================================================================
--  TAB 5: Events
-- ===========================================================================
local evHead = cEvents:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
evHead:SetPoint("TOP", 0, -110)

local evRows = {}
local EV_DEFS = {
    { key = "zone",    icon = "Interface\\Icons\\Spell_Nature_WispSplode" },
    { key = "bounty",  icon = "Interface\\Icons\\INV_Misc_Bone_HumanSkull_01" },
    { key = "dungeon", icon = "Interface\\Icons\\INV_Misc_Key_03" },
    { key = "boss",    icon = "Interface\\Icons\\INV_Misc_Head_Dragon_01" },
    { key = "mutator", icon = "Interface\\Icons\\INV_Misc_Gear_01" },
    { key = "storm",   icon = "Interface\\Icons\\Spell_Nature_Cyclone" },
    { key = "chests",  icon = "Interface\\Icons\\INV_Box_02" },
}
for i, def in ipairs(EV_DEFS) do
    local row = CreateFrame("Frame", nil, cEvents)
    row:SetWidth(560)
    row:SetHeight(30)
    row:SetPoint("TOP", 0, -136 - (i - 1) * 32)

    row.icon = row:CreateTexture(nil, "ARTWORK")
    row.icon:SetTexture(def.icon)
    row.icon:SetWidth(26)
    row.icon:SetHeight(26)
    row.icon:SetPoint("LEFT", 0, 0)

    row.label = row:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    row.label:SetPoint("LEFT", 36, 6)
    row.label:SetJustifyH("LEFT")

    row.value = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    row.value:SetPoint("LEFT", 36, -8)
    row.value:SetJustifyH("LEFT")

    evRows[def.key] = row
end

local evInfo = cEvents:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
evInfo:SetPoint("TOPLEFT", 100, -366)
evInfo:SetWidth(560)
evInfo:SetJustifyH("LEFT")
evInfo:SetSpacing(3)

local function BuildEventInfo()
    local t = {}
    table.insert(t, "|cffFFD700" .. BPL("info_rotation") .. "|r")
    for _, b in ipairs(BP_BOSSES or {}) do
        local zone = BP_Lang() == "en" and (b.zone_en or b.zone) or b.zone
        table.insert(t, "   |cffFF8800" .. b.name .. "|r — " .. zone)
    end
    table.insert(t, " ")
    local w = {}
    for _, it in ipairs(BP_WELCOME or {}) do
        table.insert(w, BPName(it))
    end
    table.insert(t, "|cffFFD700" .. BPL("info_welcome") .. "|r " .. table.concat(w, ", "))
    table.insert(t, BPL("info_worldbuff"))
    table.insert(t, BPL("info_weekend"))
    evInfo:SetText(table.concat(t, "\n"))
end

local function RefreshEvents()
    local e = BP.events
    if not e then return end
    evRows.zone.value:SetText("|cff00CCFF" .. e.zone .. "|r")
    evRows.bounty.value:SetText("|cffFF8800" .. e.bounty .. "|r")
    evRows.dungeon.value:SetText("|cff00CCFF" .. e.dungeon .. "|r" ..
        (e.dungeonDone == 1 and "  |cff33FF33" .. BPL("dungeon_done") .. "|r"
                             or "  |cffFFA500" .. BPL("dungeon_hint") .. "|r"))
    if e.boss ~= "-" then
        evRows.boss.value:SetText("|cffFF4444" .. string.format(BPL("boss_active"), e.boss) .. "|r")
    else
        evRows.boss.value:SetText("|cff888888" .. BPL("boss_none") .. "|r")
    end
    evRows.mutator.value:SetText("|cffFFD700" .. (e.mutator or "-") .. "|r")
    if e.storm == 1 then
        evRows.storm.value:SetText("|cff00CCFF" .. BPL("storm_on") .. "|r")
    else
        evRows.storm.value:SetText("|cff888888" .. BPL("storm_off") .. "|r")
    end
    if BP.tier >= BP.maxTier then
        evRows.chests.value:SetText("|cff00FF00" .. string.format(BPL("chest_on"), BP.pity) .. "|r")
    else
        evRows.chests.value:SetText("|cff888888" .. string.format(BPL("chest_off"), BP.pity) .. "|r")
    end
end

-- ===========================================================================
--  TAB 6: Erfolge
-- ===========================================================================
local achHead = cAch:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
achHead:SetPoint("TOP", 0, -114)

local achSub = cAch:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
achSub:SetPoint("TOP", achHead, "BOTTOM", 0, -2)

local achRows = {}
local achIds = {}
for id in pairs(BP_ACH or {}) do table.insert(achIds, id) end
table.sort(achIds)

for idx, id in ipairs(achIds) do
    local col = (idx - 1) % 2
    local row = math.floor((idx - 1) / 2)
    local r = CreateFrame("Frame", nil, cAch)
    r:SetWidth(335)
    r:SetHeight(34)
    r:SetPoint("TOPLEFT", 42 + col * 352, -146 - row * 36)

    r.icon = r:CreateTexture(nil, "ARTWORK")
    r.icon:SetWidth(28)
    r.icon:SetHeight(28)
    r.icon:SetPoint("LEFT", 0, 0)

    r.check = r:CreateTexture(nil, "OVERLAY")
    r.check:SetTexture("Interface\\RaidFrame\\ReadyCheck-Ready")
    r.check:SetWidth(15)
    r.check:SetHeight(15)
    r.check:SetPoint("BOTTOMRIGHT", r.icon, "BOTTOMRIGHT", 3, -3)
    r.check:Hide()

    r.name = r:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    r.name:SetPoint("TOPLEFT", 36, -1)
    r.name:SetJustifyH("LEFT")
    r.name:SetWidth(300)

    -- Mini-Fortschrittsbalken im Tooltip-Goldrahmen
    r.barFrame = CreateFrame("Frame", nil, r)
    r.barFrame:SetWidth(150)
    r.barFrame:SetHeight(11)
    r.barFrame:SetPoint("TOPLEFT", 36, -17)
    r.barFrame:SetBackdrop({
        bgFile = "Interface\\ChatFrame\\ChatFrameBackground",
        edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
        tile = true, tileSize = 8, edgeSize = 8,
        insets = { left = 2, right = 2, top = 2, bottom = 2 },
    })
    r.barFrame:SetBackdropColor(0, 0, 0, 0.6)

    r.bar = CreateFrame("StatusBar", nil, r.barFrame)
    r.bar:SetPoint("TOPLEFT", 2, -2)
    r.bar:SetPoint("BOTTOMRIGHT", -2, 2)
    r.bar:SetStatusBarTexture("Interface\\TargetingFrame\\UI-StatusBar")
    r.bar:SetStatusBarColor(1, 0.82, 0)

    r.prog = r:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    r.prog:SetPoint("LEFT", r.barFrame, "RIGHT", 8, 0)
    r.prog:SetJustifyH("LEFT")

    achRows[idx] = { frame = r, achId = id }
end

local function RefreshAch()
    local doneCount = 0
    for _, entry in ipairs(achRows) do
        local def = BP_ACH[entry.achId]
        local f = entry.frame
        local prog = BP.ach[entry.achId] or 0
        local done = prog >= def.goal
        if done then doneCount = doneCount + 1 end
        f.icon:SetTexture(ACH_ICONS[def.kind] or ICON_UNKNOWN)
        f.bar:SetMinMaxValues(0, def.goal > 0 and def.goal or 1)
        f.bar:SetValue(prog)
        if done then
            f.icon:SetDesaturated(false)
            f.check:Show()
            f.bar:SetStatusBarColor(0.2, 0.8, 0.2)
            f.name:SetText("|cff33FF33" .. BPName(def) .. "|r")
            f.prog:SetText("|cff33FF33" .. string.format(BPL("ach_done"), def.points) .. "|r")
        else
            f.icon:SetDesaturated(true)
            f.check:Hide()
            f.bar:SetStatusBarColor(1, 0.82, 0)
            f.name:SetText(BPName(def))
            f.prog:SetText(prog .. " / " .. def.goal .. "  |cffFFD700" .. string.format(BPL("pts_suffix"), def.points) .. "|r")
        end
    end
    achSub:SetText(string.format(BPL("ach_sub"), doneCount, #achRows))
end

StaticPopupDialogs["BP_PRESTIGE_CONFIRM"] = {
    text = "?",
    button1 = YES,
    button2 = NO,
    OnAccept = function() SendChatMessage(".bp prestige ja", "SAY") end,
    timeout = 0,
    whileDead = 1,
    hideOnEscape = 1,
}

-- Prestige gehört ans Ende des Belohnungspfads (erscheint im Belohnungen-Tab)
local prestigeBtn = CreateFrame("Button", nil, cRewards, "UIPanelButtonTemplate")
prestigeBtn:SetWidth(170)
prestigeBtn:SetHeight(24)
prestigeBtn:SetPoint("BOTTOM", 255, 61)
prestigeBtn:SetScript("OnClick", function()
    StaticPopupDialogs["BP_PRESTIGE_CONFIRM"].text = BPL("prestige_confirm")
    StaticPopup_Show("BP_PRESTIGE_CONFIRM")
end)

-- ===========================================================================
--  TAB 7: Charakter — Werte & Saison-Statistiken
-- ===========================================================================
local charName = cChar:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
charName:SetPoint("TOP", 0, -118)

local function MakeStatLine(x, y)
    local label = cChar:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    label:SetPoint("TOPLEFT", x, y)
    label:SetJustifyH("LEFT")
    local value = cChar:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    value:SetPoint("TOPLEFT", x + 175, y)
    value:SetJustifyH("LEFT")
    return { l = label, v = value }
end

local charLeftHead = cChar:CreateFontString(nil, "OVERLAY", "GameFontNormal")
charLeftHead:SetPoint("TOPLEFT", 70, -152)
local charLines = {}
for i = 1, 10 do charLines[i] = MakeStatLine(70, -176 - (i - 1) * 23) end

local charRightHead = cChar:CreateFontString(nil, "OVERLAY", "GameFontNormal")
charRightHead:SetPoint("TOPLEFT", 410, -152)
local seasonLines = {}
for i = 1, 14 do seasonLines[i] = MakeStatLine(410, -176 - (i - 1) * 23) end

local playedTotal = nil

local function RequestPlayed()
    -- Standard-Chatausgabe von /played einmalig unterdrücken
    for i = 1, NUM_CHAT_WINDOWS do
        local f = _G["ChatFrame" .. i]
        if f then f:UnregisterEvent("TIME_PLAYED_MSG") end
    end
    RequestTimePlayed()
end

local function FmtPlayed(sec)
    local d = math.floor(sec / 86400)
    local h = math.floor((sec % 86400) / 3600)
    local m = math.floor((sec % 3600) / 60)
    if d > 0 then return d .. "d " .. h .. "h " .. m .. "m" end
    return h .. "h " .. m .. "m"
end

function BP_RefreshChar()
    local _, classToken = UnitClass("player")
    local color = RAID_CLASS_COLORS and RAID_CLASS_COLORS[classToken] or { r = 1, g = 0.82, b = 0 }
    charName:SetText(string.format("|cff%02x%02x%02x%s|r  —  Level %d",
        color.r * 255, color.g * 255, color.b * 255, UnitName("player") or "?", UnitLevel("player") or 1))
    charLeftHead:SetText("|cffFFD700" .. BPL("char_stats") .. "|r")
    charRightHead:SetText("|cffFFD700" .. BPL("char_season") .. "|r")

    local L = charLines
    L[1].l:SetText(BPL("char_played"))
    L[1].v:SetText(playedTotal and FmtPlayed(playedTotal) or "...")
    L[2].l:SetText(BPL("char_gold"))
    L[2].v:SetText(GetCoinTextureString and GetCoinTextureString(GetMoney() or 0) or tostring(GetMoney() or 0))
    for i = 1, 5 do
        local _, eff = UnitStat("player", i)
        L[2 + i].l:SetText(BPL("stat" .. i))
        L[2 + i].v:SetText(eff or 0)
    end
    local apBase, apPos, apNeg = UnitAttackPower("player")
    L[8].l:SetText(BPL("char_ap"))
    L[8].v:SetText((apBase or 0) + (apPos or 0) + (apNeg or 0))
    L[9].l:SetText(BPL("char_crit"))
    L[9].v:SetText(string.format("%.1f%%", GetCritChance() or 0))
    L[10].l:SetText(BPL("char_scrit"))
    L[10].v:SetText(string.format("%.1f%%", (GetSpellCritChance and GetSpellCritChance(2)) or 0))

    local S = seasonLines
    local function set(i, key, val)
        S[i].l:SetText(BPL(key))
        S[i].v:SetText(val)
    end
    local function ach(id) return BP.ach[id] or 0 end
    set(1, "cs_points", BP.points)
    set(2, "cs_tier", BP.tier .. " / " .. BP.maxTier)
    set(3, "cs_prestige", BP.prestige)
    set(4, "cs_streak", BP.streak)
    set(5, "cs_pity", "+" .. BP.pity .. "%")
    set(6, "cs_boss", ach(8))
    set(7, "cs_bounty", ach(10))
    set(8, "cs_rare", ach(16))
    set(9, "cs_duel", ach(15))
    set(10, "cs_weekly", ach(14))
    set(11, "cs_dungeon", ach(17))
    set(12, "cs_disc", ach(20) .. " / 18")
    set(13, "cs_supply", ach(22))
    set(14, "cs_rune", ach(12))
end

local playedFrame = CreateFrame("Frame")
playedFrame:RegisterEvent("TIME_PLAYED_MSG")
playedFrame:SetScript("OnEvent", function(_, _, total)
    playedTotal = total
    for i = 1, NUM_CHAT_WINDOWS do
        local f = _G["ChatFrame" .. i]
        if f then f:RegisterEvent("TIME_PLAYED_MSG") end
    end
    if frame:IsShown() then BP_RefreshChar() end
end)

-- ===========================================================================
--  TAB 8: Sammlung — das Saison-Journal (Pets, Cosmetics)
-- ===========================================================================
local collSub = cColl:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
collSub:SetPoint("TOP", 0, -122)

local collHeaders = {}
local collBtns = {}
do
    local cats = { {}, {} }
    for _, e in ipairs(BP_COLLECTION or {}) do
        table.insert(cats[e.cat] or cats[2], e)
    end
    local y = -148
    for c = 1, 2 do
        local h = cColl:CreateFontString(nil, "OVERLAY", "GameFontNormal")
        h:SetPoint("TOPLEFT", 70, y)
        collHeaders[c] = h
        y = y - 22
        for idx, e in ipairs(cats[c]) do
            local b = CreateFrame("Button", nil, cColl)
            b:SetWidth(34)
            b:SetHeight(34)
            b:SetPoint("TOPLEFT", 70 + (idx - 1) % 15 * 42, y - math.floor((idx - 1) / 15) * 42)
            local tex = b:CreateTexture(nil, "BACKGROUND")
            tex:SetAllPoints()
            tex:SetTexCoord(0.07, 0.93, 0.07, 0.93)
            b.icon = tex
            local check = b:CreateTexture(nil, "OVERLAY")
            check:SetTexture("Interface\\RaidFrame\\ReadyCheck-Ready")
            check:SetWidth(14)
            check:SetHeight(14)
            check:SetPoint("BOTTOMRIGHT", 2, -2)
            check:Hide()
            b.check = check
            b:SetHighlightTexture("Interface\\Buttons\\ButtonHilight-Square", "ADD")
            b.entry = e
            b:SetScript("OnEnter", function(self)
                GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
                GameTooltip:SetHyperlink("item:" .. self.entry.id)
                if GetItemCount(self.entry.id, true) > 0 then
                    GameTooltip:AddLine(BPL("coll_owned"), 0, 1, 0)
                else
                    GameTooltip:AddLine(BPL("coll_missing"), 0.7, 0.7, 0.7)
                end
                GameTooltip:Show()
            end)
            b:SetScript("OnLeave", CellOnLeave)
            table.insert(collBtns, b)
        end
        y = y - 42 * math.max(1, math.ceil(#cats[c] / 15)) - 26
    end
end

local function RefreshColl()
    collSub:SetText(BPL("coll_sub"))
    for c = 1, 2 do
        collHeaders[c]:SetText("|cffFFD700" .. BPL("coll_cat" .. c) .. "|r")
    end
    for _, b in ipairs(collBtns) do
        b.icon:SetTexture(GetItemIcon and GetItemIcon(b.entry.id) or ICON_UNKNOWN)
        if GetItemCount(b.entry.id, true) > 0 then
            b.icon:SetDesaturated(false)
            b.check:Show()
        else
            b.icon:SetDesaturated(true)
            b.check:Hide()
        end
    end
end

-- ===========================================================================
--  TAB 9: Shop der Saisonhändlerin — Traumkiste + Items, eine Seite je Kategorie
-- ===========================================================================
local SHOP_PER_PAGE = 40
local shopPage = 1
local shopCatSlots = {}
local SHOP_PAGES = 1
do
    for slot, e in pairs(BP_SHOP or {}) do
        local c = e.cat or 1
        shopCatSlots[c] = shopCatSlots[c] or {}
        table.insert(shopCatSlots[c], slot)
        if c > SHOP_PAGES then SHOP_PAGES = c end
    end
    for _, list in pairs(shopCatSlots) do table.sort(list) end
end

local BOX_ICONS = {
    [0] = "Interface\\Icons\\INV_Misc_Gift_05",
    [1] = "Interface\\Icons\\INV_Misc_Gift_01",
    [2] = "Interface\\Icons\\INV_Misc_Gift_03",
    [3] = "Interface\\Icons\\INV_Misc_Gift_05",
}

local shopLabel = cShop:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
shopLabel:SetPoint("TOP", 0, -118)

local shopPageText = cShop:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
shopPageText:SetPoint("TOP", 0, -144)

local shopPrev = CreateFrame("Button", nil, cShop)
shopPrev:SetWidth(26)
shopPrev:SetHeight(26)
shopPrev:SetPoint("TOP", -220, -136)
shopPrev:SetNormalTexture("Interface\\Buttons\\UI-SpellbookIcon-PrevPage-Up")
shopPrev:SetPushedTexture("Interface\\Buttons\\UI-SpellbookIcon-PrevPage-Down")
shopPrev:SetDisabledTexture("Interface\\Buttons\\UI-SpellbookIcon-PrevPage-Disabled")

local shopNext = CreateFrame("Button", nil, cShop)
shopNext:SetWidth(26)
shopNext:SetHeight(26)
shopNext:SetPoint("TOP", 220, -136)
shopNext:SetNormalTexture("Interface\\Buttons\\UI-SpellbookIcon-NextPage-Up")
shopNext:SetPushedTexture("Interface\\Buttons\\UI-SpellbookIcon-NextPage-Down")
shopNext:SetDisabledTexture("Interface\\Buttons\\UI-SpellbookIcon-NextPage-Disabled")

local function MoneyStr(c)
    local g = math.floor(c / 10000)
    local s = math.floor((c % 10000) / 100)
    local k = c % 100
    local parts = {}
    if g > 0 then table.insert(parts, g .. " |cffFFD700G|r") end
    if s > 0 then table.insert(parts, s .. " |cffC0C0C0S|r") end
    if k > 0 or #parts == 0 then table.insert(parts, k .. " |cffB87333K|r") end
    return table.concat(parts, " ")
end

local shopBtns = {}
for i = 1, SHOP_PER_PAGE do
    local col = (i - 1) % 10
    local row = math.floor((i - 1) / 10)
    local sname = "BPShopBtn" .. i
    local b = CreateFrame("Button", sname, cShop, "ItemButtonTemplate")
    b:SetPoint("TOPLEFT", 60 + col * 64, -174 - row * 56)
    b.iconTex = _G[sname .. "IconTexture"]
    b:SetScript("OnClick", function(self)
        if self.shopSlot then
            PlaySound("LOOTWINDOWCOINSOUND")
            SendChatMessage(".bp buy " .. self.shopSlot, "SAY")
        end
    end)
    b:SetScript("OnEnter", function(self)
        local e = self.shopSlot and BP_SHOP[self.shopSlot]
        if not e then return end
        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        if e.kind == 1 then
            GameTooltip:AddLine(BPName(BP_CHESTS[e.id] or {}), 0.64, 0.21, 0.93)
            GameTooltip:AddLine(BPL("box_desc"), 1, 1, 1, true)
            GameTooltip:AddLine(BPL("kt_see"), 0, 1, 0)
        else
            GameTooltip:SetHyperlink("item:" .. e.id)
            GameTooltip:AddLine(" ")
            GameTooltip:AddLine(string.format(BPL("shop_count"), e.count), 1, 1, 1)
        end
        GameTooltip:AddLine(string.format(BPL("shop_price"), MoneyStr(e.price)), 1, 0.82, 0)
        GameTooltip:Show()
    end)
    b:SetScript("OnLeave", CellOnLeave)
    shopBtns[i] = b
end

local function RefreshExtras()
    local cat = BP_SHOP_CATS and BP_SHOP_CATS[shopPage]
    shopPageText:SetText((cat and ("|cffFFD700" .. BPName(cat) .. "|r  —  ") or "")
        .. string.format(BPL("page"), shopPage, SHOP_PAGES))
    if shopPage <= 1 then shopPrev:Disable() else shopPrev:Enable() end
    if shopPage >= SHOP_PAGES then shopNext:Disable() else shopNext:Enable() end
    local list = shopCatSlots[shopPage] or {}
    for i = 1, SHOP_PER_PAGE do
        local b = shopBtns[i]
        local slot = list[i]
        local e = slot and BP_SHOP and BP_SHOP[slot]
        if e then
            b:Show()
            b.shopSlot = slot
            if e.kind == 1 then
                b.iconTex:SetTexture(BOX_ICONS[e.id] or ICON_CHEST)
            else
                b.iconTex:SetTexture(GetItemIcon and GetItemIcon(e.id) or ICON_UNKNOWN)
            end
        else
            b:Hide()
            b.shopSlot = nil
        end
    end
    if BP.prestigeEnabled == 1 and BP.tier >= BP.maxTier then prestigeBtn:Enable() else prestigeBtn:Disable() end
end

shopPrev:SetScript("OnClick", function()
    PlaySound("igAbiliityPageTurn")
    if shopPage > 1 then shopPage = shopPage - 1 end
    RefreshExtras()
end)
shopNext:SetScript("OnClick", function()
    PlaySound("igAbiliityPageTurn")
    if shopPage < SHOP_PAGES then shopPage = shopPage + 1 end
    RefreshExtras()
end)

-- ===========================================================================
--  TAB 10: Kisten — Beutevorschau mit Drop-Chancen
-- ===========================================================================
local RAR_HEX = { "ffffff", "0070dd", "a335ee", "ff8000" }
local RAR_RGB = { {1, 1, 1}, {0, 0.44, 0.87}, {0.64, 0.21, 0.93}, {1, 0.5, 0} }

local ktHead = cChest:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
ktHead:SetPoint("TOP", 0, -118)
local ktInfo = cChest:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
ktInfo:SetPoint("TOP", 0, -166)
local ktFever = cChest:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
ktFever:SetPoint("BOTTOM", 0, 48)

local ktSel = 1
local ktSelBtns = {}
local RefreshChestTab
for i = 1, 3 do
    local b = CreateFrame("Button", nil, cChest, "UIPanelButtonTemplate")
    b:SetWidth(190)
    b:SetHeight(22)
    b:SetPoint("TOP", (i - 2) * 200, -142)
    b:SetScript("OnClick", function()
        PlaySound("igAbiliityPageTurn")
        ktSel = i
        RefreshChestTab()
    end)
    ktSelBtns[i] = b
end

local ktHeaders = {}
local ktBtns = {}
local function KtButton(idx)
    if ktBtns[idx] then return ktBtns[idx] end
    local b = CreateFrame("Button", nil, cChest)
    b:SetWidth(22)
    b:SetHeight(22)
    local tex = b:CreateTexture(nil, "BACKGROUND")
    tex:SetAllPoints()
    tex:SetTexCoord(0.07, 0.93, 0.07, 0.93)
    b.icon = tex
    b:SetHighlightTexture("Interface\\Buttons\\ButtonHilight-Square", "ADD")
    b:SetScript("OnEnter", function(self)
        local e = self.entry
        if not e then return end
        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        if e.kind == 0 then
            GameTooltip:SetHyperlink("item:" .. e.id)
            if e.count > 1 then
                GameTooltip:AddLine(string.format(BPL("shop_count"), e.count), 1, 1, 1)
            end
        else
            local c = RAR_RGB[e.rar]
            GameTooltip:SetText(BPName(e), c[1], c[2], c[3])
            if e.kind == 2 then
                GameTooltip:AddLine(BPL("kt_rune_desc"), 1, 1, 1, 1)
            end
        end
        GameTooltip:AddLine(string.format(BPL("kt_chance"), self.pct), 0, 1, 0)
        GameTooltip:Show()
    end)
    b:SetScript("OnLeave", CellOnLeave)
    ktBtns[idx] = b
    return b
end
local function KtHeader(idx)
    if ktHeaders[idx] then return ktHeaders[idx] end
    local h = cChest:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    ktHeaders[idx] = h
    return h
end

RefreshChestTab = function()
    ktHead:SetText(BPL("kt_head"))
    ktFever:SetText("|cffFF6600" .. string.format(BPL("kt_fever"), BP.pity or 0) .. "|r")
    local up = BP_CHEST_RARITY and BP_CHEST_RARITY[0] or { 500, 350, 150 }
    ktInfo:SetText(string.format(BPL("kt_odds"), up[1] / 10, up[2] / 10, up[3] / 10))
    for i = 1, 3 do
        ktSelBtns[i]:SetText(BPName(BP_CHESTS[i]))
        if i == ktSel then ktSelBtns[i]:LockHighlight() else ktSelBtns[i]:UnlockHighlight() end
    end

    local rc = BP_CHEST_RARITY[ktSel] or { 0, 0, 0, 0 }
    local tot = { 0, 0, 0, 0 }
    for _, e in ipairs(BP_CHEST_LOOT or {}) do
        local w = e.w[ktSel]
        if w > 0 then tot[e.rar] = tot[e.rar] + w end
    end

    local used, usedH = 0, 0
    local y = -188
    for rar = 1, 4 do
        usedH = usedH + 1
        local h = KtHeader(usedH)
        h:ClearAllPoints()
        h:SetPoint("TOPLEFT", 80, y)
        h:SetText("|cff" .. RAR_HEX[rar] .. BPL("kt_rar" .. rar)
            .. string.format("  —  %.1f%%", rc[rar] / 10) .. "|r")
        h:Show()
        y = y - 17
        local col = 0
        for _, e in ipairs(BP_CHEST_LOOT or {}) do
            local w = e.w[ktSel]
            if e.rar == rar and w > 0 then
                if col == 24 then
                    col = 0
                    y = y - 25
                end
                used = used + 1
                local b = KtButton(used)
                b.entry = e
                b.pct = (rc[rar] / 10) * w / tot[rar]
                b.icon:SetTexture(e.kind == 1 and "Interface\\Icons\\INV_Misc_Coin_01"
                    or e.kind == 2 and "Interface\\Icons\\INV_Misc_Rune_01"
                    or (GetItemIcon and GetItemIcon(e.id)) or ICON_UNKNOWN)
                b:ClearAllPoints()
                b:SetPoint("TOPLEFT", 80 + col * 25, y)
                b:Show()
                col = col + 1
            end
        end
        y = y - 25 - 8
    end
    for i = used + 1, #ktBtns do ktBtns[i]:Hide() end
    for i = usedH + 1, #ktHeaders do ktHeaders[i]:Hide() end
end

-- ===========================================================================
--  Traumkisten-Aufwertung: Animation in der Bildschirmmitte (BPCHEST-Sync)
-- ===========================================================================
local chestFx = CreateFrame("Frame", nil, UIParent)
chestFx:SetWidth(240)
chestFx:SetHeight(130)
chestFx:SetPoint("CENTER", 0, 170)
chestFx:SetFrameStrata("HIGH")
chestFx:Hide()
chestFx.icon = chestFx:CreateTexture(nil, "ARTWORK")
chestFx.icon:SetWidth(64)
chestFx.icon:SetHeight(64)
chestFx.icon:SetPoint("TOP", 0, 0)
chestFx.icon:SetTexture("Interface\\Icons\\INV_Box_02")
chestFx.icon:SetTexCoord(0.07, 0.93, 0.07, 0.93)
chestFx.text = chestFx:CreateFontString(nil, "OVERLAY", "GameFontNormalHuge")
chestFx.text:SetPoint("TOP", chestFx.icon, "BOTTOM", 0, -10)
local CHEST_COLS = { { 0.2, 0.55, 1 }, { 0.64, 0.21, 0.93 }, { 1, 0.65, 0 } }
chestFx:SetScript("OnUpdate", function(self, elapsed)
    self.t = (self.t or 0) + elapsed
    if self.t < 1.5 then
        -- Spannung: Farben rotieren, Kiste pulsiert
        local c = CHEST_COLS[math.floor(self.t * 6) % 3 + 1]
        self.text:SetTextColor(c[1], c[2], c[3])
        self.text:SetText(BPL("chest_roll"))
        local s = 64 * (1 + 0.18 * math.sin(self.t * 14))
        self.icon:SetWidth(s)
        self.icon:SetHeight(s)
    elseif not self.done then
        self.done = true
        local c = CHEST_COLS[self.tier] or CHEST_COLS[1]
        self.text:SetTextColor(c[1], c[2], c[3])
        self.text:SetText(BPName(BP_CHESTS[self.tier] or {}) .. "!")
        self.icon:SetWidth(80)
        self.icon:SetHeight(80)
        PlaySound(self.tier == 3 and "LEVELUPSOUND" or "LOOTWINDOWCOINSOUND")
    elseif self.t > 4 then
        self:Hide()
    end
end)
function BP_ChestReveal(tier)
    chestFx.t = 0
    chestFx.done = nil
    chestFx.tier = tier
    chestFx:Show()
    PlaySound("igBackPackOpen")
end

-- ===========================================================================
--  TAB 11: Traumschmiede (Prestige-Pfad) — Punkte frei verteilen
-- ===========================================================================
local pgUI = { rows = {}, per = { 1, 1, 2, 2, 1, 1, 1, 1 },
    icons = { "Ability_Warrior_InnerRage", "Spell_Arcane_ArcaneTorrent", "Spell_Fire_SelfDestruct",
              "Ability_Creature_Poison_06", "Spell_Holy_BlessingOfStamina", "Spell_Holy_MagicalSentry",
              "Spell_Holy_FlashHeal", "INV_Misc_Book_07" } }

pgUI.head = cPara:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
pgUI.head:SetPoint("TOP", 0, -118)
pgUI.sub = cPara:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
pgUI.sub:SetPoint("TOP", 0, -140)
pgUI.info = cPara:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
pgUI.info:SetPoint("BOTTOM", 0, 52)
pgUI.info:SetWidth(620)

for i = 1, 8 do
    local col = (i - 1) % 2
    local rowN = math.floor((i - 1) / 2)
    local row = CreateFrame("Frame", nil, cPara)
    row:SetWidth(330)
    row:SetHeight(56)
    row:SetPoint("TOPLEFT", 55 + col * 350, -166 - rowN * 62)
    local icon = row:CreateTexture(nil, "ARTWORK")
    icon:SetWidth(30)
    icon:SetHeight(30)
    icon:SetPoint("TOPLEFT", 0, -6)
    icon:SetTexture("Interface\\Icons\\" .. pgUI.icons[i])
    icon:SetTexCoord(0.07, 0.93, 0.07, 0.93)
    row.name = row:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    row.name:SetPoint("TOPLEFT", 38, -2)
    row.desc = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    row.desc:SetPoint("TOPLEFT", 38, -18)
    row.pts = row:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    row.pts:SetPoint("TOPLEFT", 38, -34)
    local plus = CreateFrame("Button", nil, row, "UIPanelButtonTemplate")
    plus:SetWidth(26)
    plus:SetHeight(22)
    plus:SetPoint("TOPRIGHT", 0, -14)
    plus:SetText("+")
    plus:SetScript("OnClick", function()
        PlaySound("igMainMenuOptionCheckBoxOn")
        SendChatMessage(".bp paragon " .. i, "SAY")
    end)
    row.plus = plus
    pgUI.rows[i] = row
end

StaticPopupDialogs["BP_PARAGON_RESET"] = {
    text = "?", button1 = YES, button2 = NO,
    OnAccept = function() SendChatMessage(".bp paragon reset", "SAY") end,
    timeout = 0, whileDead = 1, hideOnEscape = 1,
}

pgUI.reset = CreateFrame("Button", nil, cPara, "UIPanelButtonTemplate")
pgUI.reset:SetWidth(180)
pgUI.reset:SetHeight(22)
pgUI.reset:SetPoint("BOTTOM", 0, 78)
pgUI.reset:SetScript("OnClick", function()
    StaticPopupDialogs["BP_PARAGON_RESET"].text = BPL("pg_reset_confirm")
    StaticPopup_Show("BP_PARAGON_RESET")
end)

local function RefreshParaTab()
    local pg = BP.pg or { prestige = BP.prestige or 0, max = 300, free = 0, cap = 50, mob = 1,
                          s = { 0, 0, 0, 0, 0, 0, 0, 0 } }
    if pg.max == 0 then
        pgUI.head:SetText(BPL("pg_disabled_head"))
        pgUI.sub:SetText(BPL("pg_disabled_sub"))
        pgUI.info:SetText("")
        pgUI.reset:Disable()
        for i = 1, 8 do
            pgUI.rows[i].plus:Disable()
        end
        return
    end
    pgUI.head:SetText(BPL("pg_head"))
    pgUI.sub:SetText(string.format(BPL("pg_sub"), pg.prestige, pg.max, pg.free))
    pgUI.info:SetText("|cff888888" .. string.format(BPL("pg_info"), pg.mob) .. "|r")
    pgUI.reset:Enable()
    pgUI.reset:SetText(BPL("pg_reset"))
    for i = 1, 8 do
        local row = pgUI.rows[i]
        local pts = pg.s[i] or 0
        row.name:SetText("|cffFFD700" .. BPL("pg_stat" .. i) .. "|r")
        row.desc:SetText(string.format(BPL("pg_desc" .. i), pgUI.per[i]))
        row.pts:SetText(string.format(BPL("pg_pts"), pts, pg.cap)
            .. "   " .. string.format(BPL("pg_eff"), pts * pgUI.per[i]))
        if pg.free > 0 and pts < pg.cap then row.plus:Enable() else row.plus:Disable() end
    end
end

-- ===========================================================================
--  Tabs + Texte
-- ===========================================================================
local tabs = {}
for i = 1, 11 do
    local tab = CreateFrame("Button", "SeasonPassFrameTab" .. i, frame, "CharacterFrameTabButtonTemplate")
    tab:SetID(i)
    if i == 1 then
        tab:SetPoint("TOPLEFT", frame, "BOTTOMLEFT", 14, 4)
    elseif i == 6 then
        tab:SetPoint("TOPLEFT", frame, "BOTTOMLEFT", 14, -23) -- zweite Tab-Reihe
    else
        tab:SetPoint("LEFT", tabs[i - 1], "RIGHT", -14, 0)
    end
    tabs[i] = tab
end

local RefreshAll

function SeasonPass_ApplyTexts()
    title:SetText(string.format(BPL("title"), BP_SEASON or 1))
    subtitle:SetText("|cffB48CFF" .. BPSeasonName() .. "|r")
    langBtn:SetText(BP_Lang() == "de" and "EN?" or "DE?")
    for i = 1, 11 do
        tabs[i]:SetText(BPL("tab" .. i))
        PanelTemplates_TabResize(tabs[i], 0)
    end
    prestigeBtn:SetText("|cffFF8800" .. BPL("prestige_btn") .. "|r")
    shopLabel:SetText(BPL("shop_head"))
    weeklyHead:SetText(BPL("weekly_head"))
    weeklySub:SetText(BPL("weekly_sub"))
    runesHead:SetText(BPL("runes_head"))
    runesFoot:SetText(BPL("runes_foot"))
    setSub:SetText(BPL("set_sub"))
    evHead:SetText(BPL("ev_head"))
    for _, def in ipairs(EV_DEFS) do
        evRows[def.key].label:SetText(BPL("ev_" .. def.key))
        evRows[def.key].value:SetText("|cff888888" .. BPL("wait_sync") .. "|r")
    end
    BuildEventInfo()
    achHead:SetText(BPL("ach_head"))
    RefreshAll()
end

local function SelectTab(idx)
    for i, tab in ipairs(tabs) do
        if i == idx then
            PanelTemplates_SelectTab(tab)
            contents[i]:Show()
        else
            PanelTemplates_DeselectTab(tab)
            contents[i]:Hide()
        end
    end
    PlaySound("igCharacterInfoTab")
    if idx == 7 then
        RequestPlayed() -- Spielzeit frisch abfragen (ohne Chat-Spam)
    end
    RefreshAll()
end

for i, tab in ipairs(tabs) do
    tab:SetScript("OnClick", function() SelectTab(i) end)
end
PanelTemplates_SelectTab(tabs[1])
for i = 2, 11 do PanelTemplates_DeselectTab(tabs[i]) end

-- ===========================================================================
--  Gesamt-Refresh
-- ===========================================================================
RefreshAll = function()
    local into
    if (BP.prestige or 0) > 0 then
        -- Prestige-Modus: jede volle Leiste = +1 Prestige
        into = math.min(BP.points, BP.perTier)
        bar:SetStatusBarColor(1, 0.53, 0)
        barText:SetText(string.format(BPL("bar_prestige"),
            BP.prestige, (BP.pg and BP.pg.max) or 300, into, BP.perTier))
    elseif BP.tier >= BP.maxTier then
        into = BP.perTier
        bar:SetStatusBarColor(1, 0.82, 0)
        local capKey = BP.prestigeEnabled == 1 and "bar_max" or "bar_max_no_prestige"
        barText:SetText(string.format(BPL(capKey), BP.maxTier))
    else
        into = BP.points - BP.tier * BP.perTier
        bar:SetStatusBarColor(1, 0.82, 0)
        barText:SetText(string.format(BPL("bar_prog"), BP.tier, into, BP.perTier))
    end
    bar:SetMinMaxValues(0, BP.perTier)
    bar:SetValue(into)
    local frac = into / BP.perTier
    if frac > 0 and frac < 1 then
        spark:SetPoint("CENTER", bar, "LEFT", frac * bar:GetWidth(), 0)
        spark:Show()
    else
        spark:Hide()
    end

    local bits = {}
    table.insert(bits, "|cffFFD700" .. string.format(BPL("info_points"), BP.points) .. "|r")
    if BP.prestige > 0 then
        table.insert(bits, "|cffFF8800" .. string.format(BPL("info_prestige"), BP.prestige) .. "|r")
    end
    if BP.renown > 0 or BP.renownPoints > 0 then
        table.insert(bits, "|cff88CCFF" .. string.format(BPL("info_renown"),
            BP.renown, BP.renownPoints, BP.renownPer) .. "|r")
    end
    if BP.streak > 1 then
        table.insert(bits, "|cff88FF88" .. string.format(BPL("info_streak"), BP.streak) .. "|r")
    end
    if BP.weekend == 1 then
        table.insert(bits, "|cff33FF33" .. BPL("info_weekend2") .. "|r")
    end
    infoText:SetText(table.concat(bits, "   "))

    RefreshRewards()
    RefreshWeekly()
    RefreshRunes()
    RefreshSet()
    RefreshEvents()
    RefreshAch()
    RefreshExtras()
    BP_RefreshChar()
    RefreshColl()
    RefreshChestTab()
    RefreshParaTab()

    if SeasonPassHUD_Update then
        SeasonPassHUD_Update(BP)
    end
end

prevBtn:SetScript("OnClick", function()
    PlaySound("igAbiliityPageTurn")
    if BP.page > 1 then BP.page = BP.page - 1 end
    RefreshAll()
end)
nextBtn:SetScript("OnClick", function()
    PlaySound("igAbiliityPageTurn")
    if BP.page < NUM_PAGES then BP.page = BP.page + 1 end
    RefreshAll()
end)

frame:SetScript("OnShow", function()
    PlaySound("igCharacterInfoOpen")
    SendChatMessage(".bp sync", "SAY")
    RefreshAll()
end)
frame:SetScript("OnHide", function()
    PlaySound("igCharacterInfoClose")
end)

-- ===========================================================================
--  Server-Sync
--  BPSYNC:points:tier:claimedA:claimedH:perTier:maxTier:weekend:prestige:streak
--  BPWK:slot:defId:progress:goal:done:rerollFrei   (3 Zeilen)
--  BPRN:<id,id,...>:<maxSlots>
--  BPEV:zone:kopfgeld:dungeon:dungeonErledigt:boss:mutator:sturm
--  BPACH:<id.progress,...>
-- ===========================================================================
local listener = CreateFrame("Frame")
listener:RegisterEvent("CHAT_MSG_SYSTEM")
listener:SetScript("OnEvent", function(_, _, msg)
    msg = msg or ""
    local p, t, cf, ce, per, mx, wk, pr, st, pity, wel = string.match(msg,
        "^BPSYNC:(%d+):(%d+):(%d+):(%d+):(%d+):(%d+):(%d+):(%d+):(%d+):(%d+):(%d+)")
    if p then
        local newTier = tonumber(t)
        local newPrestige = tonumber(pr)
        if lastPrestige and newPrestige > lastPrestige then
            TierFanfare(newPrestige, true)
        elseif lastTier and newTier > lastTier then
            TierFanfare(newTier)
        end
        lastTier = newTier
        lastPrestige = newPrestige
        BP.points      = tonumber(p)
        BP.tier        = newTier
        BP.claimed     = tonumber(cf)
        BP.claimedEpic = tonumber(ce)
        BP.perTier     = tonumber(per)
        BP.maxTier     = tonumber(mx)
        BP.weekend     = tonumber(wk)
        BP.prestige    = tonumber(pr)
        BP.streak      = tonumber(st)
        BP.pity        = tonumber(pity)
        BP.welcomed    = tonumber(wel)
        BP.page = math.max(1, math.min(NUM_PAGES, math.ceil(math.max(BP.tier, 1) / CELLS_PER_PAGE)))
        RefreshAll()
        return
    end

    local pe = string.match(msg, "^BPPRESTIGE:([01])$")
    if pe then
        BP.prestigeEnabled = tonumber(pe)
        RefreshAll()
        return
    end

    local rn, rp, rper = string.match(msg, "^BPRENOWN:(%d+):(%d+):(%d+)")
    if rn then
        BP.renown = tonumber(rn)
        BP.renownPoints = tonumber(rp)
        BP.renownPer = tonumber(rper)
        if frame:IsShown() then
            RefreshAll()
        elseif SeasonPassHUD_Update then
            SeasonPassHUD_Update(BP)
        end
        return
    end

    local slot, id, prog, goal, done, rr = string.match(msg, "^BPWK:(%d+):(%d+):(%d+):(%d+):(%d+):(%d+)")
    if slot then
        BP.weekly[tonumber(slot)] = {
            id = tonumber(id), prog = tonumber(prog),
            goal = tonumber(goal), done = tonumber(done),
        }
        BP.rerollFree = tonumber(rr)
        if frame:IsShown() then RefreshWeekly() end
        return
    end

    local list, slots, srune = string.match(msg, "^BPRN:([%d,]*):(%d+):(%d+)")
    if list then
        BP.runes = {}
        for rid in string.gmatch(list, "%d+") do
            table.insert(BP.runes, tonumber(rid))
        end
        BP.runeSlots = tonumber(slots)
        BP.startRune = tonumber(srune)
        if frame:IsShown() then RefreshRunes() end
        return
    end

    local zone, bounty, dungeon, ddone, boss, mutator, storm =
        string.match(msg, "^BPEV~([^~]*)~([^~]*)~([^~]*)~(%d+)~([^~]*)~([^~]*)~(%d+)")
    if zone then
        BP.events = { zone = zone, bounty = bounty, dungeon = dungeon,
                      dungeonDone = tonumber(ddone), boss = boss,
                      mutator = mutator, storm = tonumber(storm) }
        if frame:IsShown() then RefreshEvents() end
        if SeasonPassHUD_Update then SeasonPassHUD_Update(BP) end
        return
    end

    local sid, scount, sdone, spts, sgold = string.match(msg, "^BPSUP:(%d+):(%d+):(%d+):(%d+):(%d+)")
    if sid then
        BP.supply = { id = tonumber(sid), count = tonumber(scount), done = tonumber(sdone),
                      points = tonumber(spts), gold = tonumber(sgold) }
        if not GetItemInfo(BP.supply.id) and BPScanTip then
            BPScanTip:SetHyperlink("item:" .. BP.supply.id)
        end
        if frame:IsShown() then RefreshWeekly() end
        return
    end

    local fid, fneed, fcount, fpts, fgold = string.match(msg, "^BPFI:(%d+):(%d+):(%d+):(%d+):(%d+)")
    if fid then
        BP.fish = { id = tonumber(fid), need = tonumber(fneed), count = tonumber(fcount),
                    points = tonumber(fpts), gold = tonumber(fgold) }
        if not GetItemInfo(BP.fish.id) and BPScanTip then
            BPScanTip:SetHyperlink("item:" .. BP.fish.id)
        end
        if frame:IsShown() then RefreshWeekly() end
        return
    end

    local chestTier = string.match(msg, "^BPCHEST:(%d+)")
    if chestTier then
        BP_ChestReveal(tonumber(chestTier))
        return
    end

    local pgRest = string.match(msg, "^BPPG:(.*)")
    if pgRest then
        local v = {}
        for n in string.gmatch(pgRest, "%d+") do
            table.insert(v, tonumber(n))
        end
        if v[13] then
            BP.pg = { prestige = v[1], max = v[2], free = v[3], cap = v[4], mob = v[5], s = {} }
            for i = 1, 8 do BP.pg.s[i] = v[5 + i] end
            if frame:IsShown() then RefreshParaTab() end
        end
        return
    end

    local achList = string.match(msg, "^BPACH:(.*)")
    if achList then
        for aid, aprog in string.gmatch(achList, "(%d+)%.(%d+)") do
            BP.ach[tonumber(aid)] = tonumber(aprog)
        end
        if frame:IsShown() then RefreshAch() end
    end
end)

ChatFrame_AddMessageEventFilter("CHAT_MSG_SYSTEM", function(_, _, msg)
    msg = msg or ""
    if string.find(msg, "^BPSYNC:") or string.find(msg, "^BPWK:") or string.find(msg, "^BPRN:")
        or string.find(msg, "^BPEV~") or string.find(msg, "^BPACH:") or string.find(msg, "^BPSUP:")
        or string.find(msg, "^BPFI:") or string.find(msg, "^BPPG:")
        or string.find(msg, "^BPRENOWN:") or string.find(msg, "^BPPRESTIGE:")
        or string.find(msg, "^BPCHEST:") then
        return true
    end
    return false
end)

-- ===========================================================================
--  Umschalten + Slash
-- ===========================================================================
function SeasonPass_Toggle()
    if frame:IsShown() then
        frame:Hide()
    else
        frame:Show()
    end
end

SLASH_SEASONPASS1 = "/bp"
SlashCmdList["SEASONPASS"] = function(msg)
    msg = string.lower(msg or "")
    local cmd, arg = string.match(msg, "^hud%s*(%a*)%s*([%d%.]*)")
    if cmd then
        if cmd == "lock" then SeasonPassHUD_SetLocked(true)
        elseif cmd == "unlock" then SeasonPassHUD_SetLocked(false)
        elseif cmd == "left" then SeasonPassHUD_SetSide("left")
        elseif cmd == "right" then SeasonPassHUD_SetSide("right")
        elseif cmd == "hide" then SeasonPassHUD_SetHidden(true)
        elseif cmd == "show" then SeasonPassHUD_SetHidden(false)
        elseif cmd == "scale" and arg ~= "" then SeasonPassHUD_SetScale(arg)
        else
            DEFAULT_CHAT_FRAME:AddMessage("|cffFFD700[Season Pass]|r /bp hud lock|unlock|left|right|hide|show|scale <0.5-2>")
        end
        return
    end
    SeasonPass_Toggle()
end

-- ===========================================================================
--  Icon-Vorladen: Client fragt alle Belohnungs-Items beim Server ab,
--  damit keine "?"-Icons bleiben (3.3.5-Cache-Verhalten)
-- ===========================================================================
local scanTip = CreateFrame("GameTooltip", "BPScanTip", nil, "GameTooltipTemplate")
scanTip:SetOwner(UIParent, "ANCHOR_NONE")
local warmQueue = {}
do
    local seen = {}
    local function add(id)
        if id and id > 0 and not seen[id] then
            seen[id] = true
            table.insert(warmQueue, id)
        end
    end
    for _, rw in pairs(BP_REWARDS) do
        if rw.free and rw.free.type == 0 then add(rw.free.id) end
        if rw.epic and rw.epic.type == 0 then add(rw.epic.id) end
    end
    for _, set in pairs(BP_CLASS_SET or {}) do
        for _, piece in pairs(set) do add(piece.id) end
    end
    for _, e in pairs(BP_SHOP or {}) do add(e.id) end
    for _, w in ipairs(BP_WELCOME or {}) do
        if w.type == 0 then add(w.id) end
    end
    for _, e in ipairs(BP_CHEST_LOOT or {}) do
        if e.kind == 0 then add(e.id) end
    end
end

local warmFrame = CreateFrame("Frame")
local warmDelay = 2 -- kurz den Login abwarten, dann zügig abfragen
warmFrame:SetScript("OnUpdate", function(self, elapsed)
    warmDelay = warmDelay - elapsed
    if warmDelay > 0 then return end
    for i = 1, 5 do
        local id = table.remove(warmQueue)
        if not id then
            self:SetScript("OnUpdate", nil)
            RefreshAll() -- Icons jetzt aus dem Cache nachladen
            return
        end
        scanTip:SetHyperlink("item:" .. id)
    end
    warmDelay = 0.2
end)

SeasonPass_ApplyTexts()
DEFAULT_CHAT_FRAME:AddMessage("|cffFFD700[SeasonPassUI v4]|r " .. BPL("loaded"))
