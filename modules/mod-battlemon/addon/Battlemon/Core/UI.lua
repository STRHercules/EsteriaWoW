Battlemon = Battlemon or {}

local TYPE_RGB = {
    NORMAL   = { 0.78, 0.78, 0.68 },
    FIRE     = { 0.98, 0.56, 0.22 },
    WATER    = { 0.45, 0.65, 1.00 },
    ELECTRIC = { 1.00, 0.87, 0.22 },
    GRASS    = { 0.55, 0.88, 0.36 },
    ICE      = { 0.66, 0.93, 0.92 },
    FIGHTING = { 0.92, 0.32, 0.28 },
    POISON   = { 0.80, 0.42, 0.82 },
    GROUND   = { 0.94, 0.80, 0.45 },
    FLYING   = { 0.74, 0.66, 1.00 },
    PSYCHIC  = { 1.00, 0.44, 0.62 },
    BUG      = { 0.76, 0.85, 0.18 },
    ROCK     = { 0.82, 0.73, 0.30 },
    GHOST    = { 0.60, 0.48, 0.78 },
    DRAGON   = { 0.58, 0.40, 1.00 },
    DARK     = { 0.66, 0.53, 0.45 },
    STEEL    = { 0.80, 0.80, 0.90 },
    FAIRY    = { 1.00, 0.68, 0.76 },
}

function Battlemon.TypeRGB(typeName)
    local c = TYPE_RGB[typeName or ""] or { 0.88, 0.88, 0.88 }
    return c[1], c[2], c[3]
end

function Battlemon.Fill(tex, r, g, b, a)
    tex:SetTexture(Battlemon.Media("white"))
    tex:SetVertexColor(r or 1, g or 1, b or 1, a or 1)
end

-- One font helper for the whole addon. A soft drop shadow reads far better at
-- small sizes than the thick OUTLINE the frames used to use.
function Battlemon.Font(parent, size, style, r, g, b, font)
    local fs = parent:CreateFontString(nil, "OVERLAY")
    fs:SetFont(font or "Fonts\\FRIZQT__.TTF", size or 14, style or "")
    fs:SetShadowColor(0, 0, 0, 0.9)
    fs:SetShadowOffset(1, -1)
    fs:SetTextColor(r or 0.96, g or 0.96, b or 0.98)
    return fs
end

-- Skins the frame itself rather than parenting a panel to it: a child frame
-- would draw over the artwork the caller adds afterwards.
function Battlemon.SkinPanel(frame, alpha)
    frame.bmEdge = frame:CreateTexture(nil, "BACKGROUND")
    frame.bmEdge:SetPoint("TOPLEFT", -2, 2)
    frame.bmEdge:SetPoint("BOTTOMRIGHT", 2, -2)
    Battlemon.Fill(frame.bmEdge, 0.82, 0.68, 0.26, 0.85)
    frame.bmBg = frame:CreateTexture(nil, "BORDER")
    frame.bmBg:SetAllPoints()
    Battlemon.Fill(frame.bmBg, 0.06, 0.07, 0.10, alpha or 0.96)
    return frame
end

-- UISpecialFrames is a plain array of frame names that Escape closes. Which of
-- our frames belong in it flips with the split/unified setting, so entries have
-- to be removable and not just appended once at creation.
function Battlemon.EscClose(globalName, on)
    if not globalName then
        return
    end
    for i = #UISpecialFrames, 1, -1 do
        if UISpecialFrames[i] == globalName then
            table.remove(UISpecialFrames, i)
        end
    end
    if on then
        tinsert(UISpecialFrames, globalName)
    end
end

-- A draggable, closable, escape-dismissable window with the addon's chrome.
-- The chrome is kept on named fields so the main window can strip it when it
-- adopts the frame as a page.
function Battlemon.MakeWindow(globalName, w, h)
    local f = CreateFrame("Frame", globalName, UIParent)
    f.bmName = globalName
    f:SetSize(w, h)
    f:SetPoint("CENTER")
    f:SetFrameStrata("DIALOG")
    f:SetToplevel(true)
    f:EnableMouse(true)
    f:SetMovable(true)
    f:SetClampedToScreen(true)
    f:RegisterForDrag("LeftButton")
    f:SetScript("OnDragStart", function(self) self:StartMoving() end)
    f:SetScript("OnDragStop", function(self) self:StopMovingOrSizing() end)
    Battlemon.EscClose(globalName, true)
    Battlemon.SkinPanel(f)
    f.bmClose = CreateFrame("Button", nil, f, "UIPanelCloseButton")
    f.bmClose:SetPoint("TOPRIGHT", 4, 4)
    return f
end

-- UICheckButtonTemplate finds its label by global name, so the button needs one.
function Battlemon.MakeCheckbox(parent, globalName, label, get, set)
    local cb = CreateFrame("CheckButton", globalName, parent, "UICheckButtonTemplate")
    cb:SetWidth(24)
    cb:SetHeight(24)
    local fs = getglobal(globalName .. "Text")
    if fs then
        fs:SetFont("Fonts\\FRIZQT__.TTF", 13, "")
        fs:SetTextColor(0.90, 0.92, 0.96)
        fs:SetShadowColor(0, 0, 0, 0.9)
        fs:SetShadowOffset(1, -1)
        fs:SetText(label or "")
    end
    cb.bmSync = function()
        cb:SetChecked(get and get() and true or false)
    end
    cb.bmSync()
    cb:SetScript("OnClick", function(self)
        pcall(PlaySound, "igMainMenuOptionCheckBoxOn")
        if set then
            set(self:GetChecked() and true or false)
        end
    end)
    return cb
end

local function tint(btn, r, g, b)
    btn.baseColor = { r, g, b }
    Battlemon.Fill(btn.bg, r, g, b, 1)
end

function Battlemon.MakeTextButton(parent, w, h, label, onClick, r, g, b)
    local btn = CreateFrame("Button", nil, parent)
    btn:SetSize(w, h)
    btn.rim = btn:CreateTexture(nil, "BACKGROUND")
    btn.rim:SetPoint("TOPLEFT", -1, 1)
    btn.rim:SetPoint("BOTTOMRIGHT", 1, -1)
    Battlemon.Fill(btn.rim, 0.85, 0.72, 0.30, 0.9)
    btn.bg = btn:CreateTexture(nil, "BORDER")
    btn.bg:SetAllPoints()
    btn.SetTint = tint
    tint(btn, r or 0.18, g or 0.20, b or 0.27)
    btn.text = Battlemon.Font(btn, 15, "", 1, 0.96, 0.82)
    btn.text:SetPoint("CENTER")
    btn.text:SetText(label or "")
    btn:RegisterForClicks("LeftButtonUp", "RightButtonUp")
    btn:SetScript("OnEnter", function(self)
        local c = self.baseColor
        Battlemon.Fill(self.bg, c[1] + 0.14, c[2] + 0.13, c[3] + 0.10, 1)
    end)
    btn:SetScript("OnLeave", function(self)
        local c = self.baseColor
        Battlemon.Fill(self.bg, c[1], c[2], c[3], 1)
    end)
    btn:SetScript("OnClick", function(self, mouseButton)
        pcall(PlaySound, "igMainMenuOptionCheckBoxOn")
        if onClick then
            onClick(self, mouseButton)
        end
    end)
    return btn
end

-- Duplicates of the same form are allowed, so a shiny needs to read apart from
-- its normal twin everywhere a name is shown.
function Battlemon.ShinyName(name, shiny)
    name = name or "???"
    if not shiny then
        return name
    end
    return "|cffffd200*|r " .. name
end

function Battlemon.SetButtonEnabled(btn, enabled)
    if enabled then
        btn:Enable()
        btn:SetAlpha(1)
    else
        btn:Disable()
        btn:SetAlpha(0.42)
    end
end

local HABITAT_BG = {
    Grassland    = "bg_grass",
    Forest       = "bg_forest",
    Sea          = "bg_water",
    WatersEdge   = "bg_water",
    Cave         = "bg_cave",
    Mountain     = "bg_mountain",
    RoughTerrain = "bg_mountain",
    Urban        = "bg_city",
    Rare         = "bg_snow",
}

function Battlemon.HabitatBackground(habitat)
    return Battlemon.Media(HABITAT_BG[habitat or ""] or "bg_grass")
end
