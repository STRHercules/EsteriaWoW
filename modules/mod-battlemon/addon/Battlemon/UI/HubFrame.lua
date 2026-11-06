Battlemon = Battlemon or {}

local hub

local function fmtWait(sec)
    sec = tonumber(sec) or 0
    if sec <= 0 then
        return "FIGHT"
    end
    return string.format("FIGHT  %d:%02d", math.floor(sec / 60), math.floor(sec % 60))
end

function Battlemon.RefreshHub()
    if not hub then
        return
    end
    if hub.split then
        hub.split.bmSync()
    end
    local st = Battlemon.state
    if st.ready then
        Battlemon.SetButtonEnabled(hub.fight, true)
        hub.fight.text:SetText("FIGHT")
        hub.status:SetText("A wild Battlemon is nearby.")
    else
        Battlemon.SetButtonEnabled(hub.fight, false)
        hub.fight.text:SetText(fmtWait(st.readyIn))
        hub.status:SetText("Searching the tall grass...")
    end
    hub.balls:SetText(string.format("Poké Balls |cffffffff%d|r        Points |cffffffff%d|r",
        (st.bag and st.bag.POKEBALL) or 0, st.points or 0))

    local lead
    for i = 1, 6 do
        local row = st.owned[st.partySlots[i] or 0]
        if row then
            lead = row
            break
        end
    end
    if lead then
        hub.lead:SetText(string.format("Lead: %s  ·  Lv.%d",
            Battlemon.ShinyName(Battlemon.FormName(lead.formId, lead.name), lead.shiny), lead.level))
        Battlemon.SetPokemonTexture(hub.leadIcon, "Front", Battlemon.FormSprite(lead.formId, lead.sprite), lead.shiny)
        hub.leadIcon:Show()
    else
        hub.lead:SetText("No Pokémon in your party yet.")
        hub.leadIcon:Hide()
    end
end

local function build()
    if hub then
        return hub
    end
    local f = Battlemon.MakeWindow("BattlemonHubFrame", 848, 552)

    local banner = f:CreateTexture(nil, "ARTWORK")
    banner:SetPoint("TOPLEFT", 4, -4)
    banner:SetPoint("TOPRIGHT", -4, -4)
    banner:SetHeight(170)
    banner:SetTexture(Battlemon.Media("bg_grass"))

    local shade = f:CreateTexture(nil, "ARTWORK")
    shade:SetPoint("TOPLEFT", banner, "TOPLEFT")
    shade:SetPoint("BOTTOMRIGHT", banner, "BOTTOMRIGHT")
    Battlemon.Fill(shade, 0, 0, 0, 0.35)

    local pika = f:CreateTexture(nil, "OVERLAY")
    pika:SetSize(156, 156)
    pika:SetPoint("TOPRIGHT", -24, -10)
    Battlemon.SetPokemonTexture(pika, "Front", "0025_Pikachu")

    local title = Battlemon.Font(f, 30, "", 1, 0.90, 0.35)
    title:SetPoint("TOPLEFT", 28, -26)
    title:SetJustifyH("LEFT")
    title:SetText("Battlemon")

    local status = Battlemon.Font(f, 15, "", 0.94, 0.96, 1)
    status:SetPoint("TOPLEFT", 28, -74)
    status:SetJustifyH("LEFT")
    status:SetWidth(520)

    local balls = Battlemon.Font(f, 15, "", 1, 0.88, 0.45)
    balls:SetPoint("TOPLEFT", 28, -104)
    balls:SetJustifyH("LEFT")

    local leadCard = CreateFrame("Frame", nil, f)
    leadCard:SetPoint("TOPLEFT", 28, -196)
    leadCard:SetSize(792, 68)
    local leadBg = leadCard:CreateTexture(nil, "BACKGROUND")
    leadBg:SetAllPoints()
    Battlemon.Fill(leadBg, 0.05, 0.06, 0.09, 0.9)

    local leadIcon = leadCard:CreateTexture(nil, "ARTWORK")
    leadIcon:SetSize(56, 56)
    leadIcon:SetPoint("LEFT", 8, 0)

    local lead = Battlemon.Font(f, 15, "", 0.90, 0.92, 0.96)
    lead:SetPoint("LEFT", leadIcon, "RIGHT", 12, 0)
    lead:SetJustifyH("LEFT")
    lead:SetWidth(690)

    local fight = Battlemon.MakeTextButton(f, 360, 78, "FIGHT", function()
        if Battlemon.state.ready then
            Battlemon.Send("WILD")
        end
    end, 0.42, 0.14, 0.16)
    fight:SetPoint("TOP", 0, -300)
    fight.text:SetFont("Fonts\\FRIZQT__.TTF", 26, "")

    -- Four across the bottom, so they are narrower than the old three.
    -- 4 x 168 with 24px gaps inside a 848 frame leaves 52 either side.
    local party = Battlemon.MakeTextButton(f, 168, 56, "PARTY", function()
        Battlemon.Send("PARTY")
        Battlemon.ShowParty()
    end, 0.13, 0.30, 0.26)
    party:SetPoint("BOTTOMLEFT", 52, 52)

    local bag = Battlemon.MakeTextButton(f, 168, 56, "BAG", function()
        Battlemon.Send("PARTY")
        Battlemon.ShowBag()
    end, 0.30, 0.18, 0.26)
    bag:SetPoint("LEFT", party, "RIGHT", 24, 0)

    local shop = Battlemon.MakeTextButton(f, 168, 56, "SHOP", function()
        Battlemon.ShowShop()
    end, 0.34, 0.26, 0.12)
    shop:SetPoint("LEFT", bag, "RIGHT", 24, 0)

    local dex = Battlemon.MakeTextButton(f, 168, 56, "POKéDEX", function()
        Battlemon.ShowDex()
    end, 0.16, 0.22, 0.40)
    dex:SetPoint("BOTTOMRIGHT", -52, 52)

    -- Home is the one page that exists in both presentations, so the mode switch
    -- lives here where it is reachable either way.
    local split = Battlemon.MakeCheckbox(f, "BattlemonSplitCheck", "Separate windows",
        function()
            return BattlemonDB and BattlemonDB.splitWindows
        end,
        function(on)
            Battlemon.SetSplitMode(on)
        end)
    split:SetPoint("BOTTOMLEFT", 24, 12)

    local splitHint = Battlemon.Font(f, 11, "", 0.62, 0.65, 0.72)
    splitHint:SetPoint("BOTTOMRIGHT", -24, 20)
    splitHint:SetJustifyH("RIGHT")
    splitHint:SetText("Unchecked keeps every page in this one window.")

    local elapsed = 0
    f:SetScript("OnUpdate", function(_, dt)
        elapsed = elapsed + dt
        if elapsed < 1 then
            return
        end
        elapsed = 0
        local st = Battlemon.state
        if not st.ready and st.readyIn and st.readyIn > 0 then
            st.readyIn = st.readyIn - 1
            if st.readyIn <= 0 then
                st.ready = true
                st.readyIn = 0
            end
            Battlemon.RefreshHub()
        end
    end)

    f:SetScript("OnShow", function()
        Battlemon.Send("STATUS")
        Battlemon.RefreshHub()
    end)

    hub = { frame = f, fight = fight, status = status, balls = balls, lead = lead,
            leadIcon = leadIcon, split = split }
    return hub
end

function Battlemon.BuildHub()
    return build().frame
end

function Battlemon.ShowHub()
    Battlemon.EnsureData()
    Battlemon.OpenPanel("home")
    Battlemon.RefreshHub()
end

function Battlemon.ToggleHub()
    if Battlemon.Unified() then
        if Battlemon.MainShown() then
            Battlemon.HideMain()
        else
            Battlemon.ShowHub()
        end
        return
    end
    if hub and hub.frame:IsShown() then
        hub.frame:Hide()
    else
        Battlemon.ShowHub()
    end
end

function Battlemon.CreateMinimapButton()
    if Battlemon.minimapButton then
        return Battlemon.minimapButton
    end
    if not Minimap then
        error("Minimap frame does not exist yet")
    end
    BattlemonDB = BattlemonDB or {}
    if BattlemonDB.minimapAngle == nil then
        BattlemonDB.minimapAngle = 220
    end

    local btn = CreateFrame("Button", "BattlemonMinimapButton", Minimap)
    btn:SetWidth(32)
    btn:SetHeight(32)
    btn:SetFrameStrata("MEDIUM")
    btn:SetFrameLevel((Minimap:GetFrameLevel() or 0) + 8)
    btn:SetHighlightTexture("Interface\\Minimap\\UI-Minimap-ZoomButton-Highlight")
    btn:RegisterForClicks("LeftButtonUp")
    btn:RegisterForDrag("LeftButton")
    btn:SetMovable(true)

    local icon = btn:CreateTexture(nil, "BACKGROUND")
    icon:SetWidth(20)
    icon:SetHeight(20)
    icon:SetPoint("TOPLEFT", 6, -6)
    if not Battlemon.SetPokemonTexture(icon, "Front", "0025_Pikachu") then
        icon:SetTexture("Interface\\Icons\\INV_Misc_Ball_01")
    end
    icon:SetTexCoord(0.12, 0.88, 0.08, 0.84)

    local border = btn:CreateTexture(nil, "OVERLAY")
    border:SetWidth(53)
    border:SetHeight(53)
    border:SetPoint("TOPLEFT")
    border:SetTexture("Interface\\Minimap\\MiniMap-TrackingBorder")

    local function place()
        local angle = math.rad(BattlemonDB.minimapAngle or 220)
        local r = (Minimap:GetWidth() / 2) + 5
        btn:ClearAllPoints()
        btn:SetPoint("CENTER", Minimap, "CENTER", math.cos(angle) * r, math.sin(angle) * r)
    end

    btn:SetScript("OnClick", function()
        pcall(PlaySound, "igMainMenuOptionCheckBoxOn")
        Battlemon.ToggleHub()
    end)
    btn:SetScript("OnDragStart", function(self)
        self:SetScript("OnUpdate", function()
            local mx, my = Minimap:GetCenter()
            local scale = Minimap:GetEffectiveScale()
            local px, py = GetCursorPosition()
            px, py = px / scale, py / scale
            BattlemonDB.minimapAngle = math.deg(math.atan2(py - my, px - mx))
            place()
        end)
    end)
    btn:SetScript("OnDragStop", function(self)
        self:SetScript("OnUpdate", nil)
    end)
    btn:SetScript("OnEnter", function(self)
        GameTooltip:SetOwner(self, "ANCHOR_LEFT")
        GameTooltip:SetText("Battlemon", 1, 0.82, 0)
        GameTooltip:AddLine("Left-click to open", 1, 1, 1)
        GameTooltip:AddLine("Drag to move", 0.7, 0.7, 0.7)
        GameTooltip:Show()
    end)
    btn:SetScript("OnLeave", function()
        GameTooltip:Hide()
    end)

    place()
    Battlemon.minimapButton = btn
    return btn
end
