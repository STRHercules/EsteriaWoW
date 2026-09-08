-- =====================================================================
-- Transmog Collection
--
-- A read-only "browse your collection" mode for the Transmog addon,
-- opened from the main bar via the (on this server, unused) Dungeon
-- Finder microbutton instead of talking to the transmogrifier NPC.
--
-- This is a separate, dependent addon - it never edits Transmog.lua.
-- Everything below works by hooking Transmog's own public frames and
-- widgets (TransmogFrame, TransmogFrameApplyButton, etc.), which are
-- global XML-named widgets and safe to hook from outside. That's also
-- why the base Transmog addon must load first (see RequiredDeps in the
-- .toc) - these globals need to already exist when this file runs.
-- =====================================================================

-- =====================================================================
-- HideUI / Undress / Reset buttons
--
-- These take over the space the (hidden, in browse mode) Apply button
-- and cost UI used to occupy. Same idea as Blizzard's own dressing-room
-- buttons (HideUI / Undress / Reset Position), adapted for a pure
-- preview - nothing here ever touches the server or actually applies
-- anything.
-- =====================================================================

-- Same sentinel the base addon (and mod-transmog-plus/src/Transmog.h on
-- the server) uses for "no item transmogged to this slot".
local HIDDEN_ITEM_ID = 999999

-- Deliberately excludes MainHandSlot/SecondaryHandSlot/RangedSlot - the
-- user asked for weapons to stay on.
local UNDRESS_SLOTS = {
    "HeadSlot", "ShoulderSlot", "BackSlot", "ChestSlot",
    "WristSlot", "HandsSlot", "WaistSlot", "LegsSlot", "FeetSlot",
}

function TransmogCollection_Undress()
    for _, slotName in ipairs(UNDRESS_SLOTS) do
        local slotId = GetInventorySlotInfo(slotName)
        if slotId and GetInventoryItemLink("player", slotId) then
            -- Mirrors what actually clicking the slot, then clicking the
            -- "hidden" item in its grid, would do - so the rest of the
            -- UI (borders, item-grid highlighting, etc.) stays correct
            -- if the user browses further afterward.
            selectTransmogSlot(slotId, slotName)
            Transmog_Try(HIDDEN_ITEM_ID, slotName, false)
        end
    end
end

function TransmogCollection_Reset()
    Transmog_revert() -- base addon's own "discard pending preview" function
end

local hiddenUIFrames = {}
local uiIsHidden = false

function TransmogCollection_ToggleUI()
    if uiIsHidden then
        for frame in pairs(hiddenUIFrames) do
            frame:Show()
        end
        wipe(hiddenUIFrames)
        uiIsHidden = false
    else
        local children = { UIParent:GetChildren() }
        for _, child in ipairs(children) do
            if child ~= TransmogFrame and child:IsShown() then
                child:Hide()
                hiddenUIFrames[child] = true
            end
        end
        uiIsHidden = true
    end
end

local function CreateCollectionButton(nameSuffix, label, onClick)
    local btn = CreateFrame("Button", "TransmogCollection" .. nameSuffix, TransmogFrame, "UIPanelButtonTemplate")
    btn:SetHeight(22)
    btn:SetText(label)
    -- Auto-size to the label instead of a fixed width, so the row stays
    -- compact and doesn't spill past the narrow left panel.
    btn:SetWidth(btn:GetFontString():GetStringWidth() + 16)
    btn:SetScript("OnClick", onClick)
    btn:Hide()
    return btn
end

local resetButton = CreateCollectionButton("ResetButton", "Reset Changes", TransmogCollection_Reset)
local undressButton = CreateCollectionButton("UndressButton", "Undress", TransmogCollection_Undress)
local hideUIButton = CreateCollectionButton("HideUIButton", "Hide UI", TransmogCollection_ToggleUI)

-- Row was falling short of the track's right edge by ~16px (see prior
-- conversation). First attempt added all 16px to just Reset Changes'
-- width - technically correct for the FINAL right edge position, but
-- since these three are LEFT-anchored in a chain (each one's RIGHT edge
-- is what the next one anchors to), only that one button's own gap grew
-- visibly, leaving Hide UI<->Undress and Undress<->Reset looking
-- mismatched. Spreading the same 16px evenly across all three instead -
-- each button contributes 16/3 to the total rightward shift, so every
-- gap grows by the same amount and stays visually consistent.
local EXTRA_WIDTH_PER_BUTTON = 16 / 3
for _, btn in ipairs({ hideUIButton, undressButton, resetButton }) do
    btn:SetWidth(btn:GetWidth() + EXTRA_WIDTH_PER_BUTTON)
end

-- Flush to the frame's own left edge (that yellow/gray area is just
-- static background art, not a real widget, so there's nothing to
-- anchor to there) - x=16 matches the left padding the base addon's own
-- CurrencyText uses elsewhere in this same panel. Tweak the 16/9 here if
-- it still needs nudging.
hideUIButton:SetPoint("BOTTOMLEFT", TransmogFrame, "BOTTOMLEFT", 16, 9)
undressButton:SetPoint("LEFT", hideUIButton, "RIGHT", -2, 0)
-- Measured directly off a screenshot: Hide UI<->Undress gap was ~12px,
-- Undress<->Reset was ~17px - pulled Reset 5px closer to Undress to match.
-- That ended up a little too tight. Loosening it back by 3px, but the
-- right-side ending position was already good, so shrink Reset's own
-- width by the same 3px to compensate - keeps its right edge fixed in
-- place while only the left edge (the gap to Undress) moves.
resetButton:SetWidth(resetButton:GetWidth() - 3)
resetButton:SetPoint("LEFT", undressButton, "RIGHT", -4, 0)

local collectionButtons = { hideUIButton, undressButton, resetButton }

-- =====================================================================
-- Opening / closing the browser
-- =====================================================================

local browseOnlyMode = false

local COLLECTION_BUTTON_ICON = "Interface\\AddOns\\TransmogCollection\\TransmogFrame\\collection_button"
local COLLECTION_PORTRAIT_ICON = "Interface\\AddOns\\TransmogCollection\\TransmogFrame\\collection_portrait"

function TransmogCollection_Toggle()
    if TransmogFrame:IsShown() then
        TransmogFrame:Hide()
        return
    end

    if GossipFrame then
        HideUIPanel(GossipFrame) -- harmless no-op if gossip isn't open
    end

    browseOnlyMode = true
    TransmogFrame:Show() -- Transmog's own OnShow handler loads the data for us
end

-- Apply button / cost UI: Transmog re-shows these itself every time the
-- previewed items change (cost recalculation), so a one-off Hide() right
-- after TransmogFrame:Show() isn't enough - it'd pop back up as soon as
-- you click an item. Hooking each widget's own Show() catches every one
-- of those calls, no matter where inside Transmog.lua they come from.
local function HideWhileBrowsing(widget)
    if browseOnlyMode then
        widget:Hide()
    end
end

hooksecurefunc(TransmogFrameApplyButton, "Show", function() HideWhileBrowsing(TransmogFrameApplyButton) end)
hooksecurefunc(TransmogFrameMoneyFrame, "Show", function() HideWhileBrowsing(TransmogFrameMoneyFrame) end)
hooksecurefunc(TransmogFrameCurrencyIcon, "Show", function() HideWhileBrowsing(TransmogFrameCurrencyIcon) end)
hooksecurefunc(TransmogFrameCurrencyText, "Show", function() HideWhileBrowsing(TransmogFrameCurrencyText) end)

TransmogFrame:HookScript("OnShow", function()
    if browseOnlyMode then
        TransmogFramePortrait:SetTexture(COLLECTION_PORTRAIT_ICON)
        TransmogFrameTitleText:SetText("Collection")
        TransmogFrameApplyButton:Hide()
        TransmogFrameMoneyFrame:Hide()
        TransmogFrameCurrencyIcon:Hide()
        TransmogFrameCurrencyText:Hide()
        for _, btn in ipairs(collectionButtons) do
            btn:Show()
        end
    else
        -- Base addon never sets TitleText dynamically either (grepped),
        -- same story as the Apply button below - restore it explicitly or
        -- it stays stuck on "Collection" forever after the first browse.
        TransmogFrameTitleText:SetText("Transmogrify")
        -- Base addon only ever Enable()/Disable()s this button, it never
        -- Show()s it again itself - so without this, once browse mode had
        -- hidden it a single time, it stayed hidden forever after, even
        -- back in normal (real transmogrifier NPC) use. Money/Currency
        -- widgets don't need the same treatment since Transmog:updateCost()
        -- already re-Shows those itself on the next cost recalculation.
        TransmogFrameApplyButton:Show()
        for _, btn in ipairs(collectionButtons) do
            btn:Hide()
        end
    end
end)

TransmogFrame:HookScript("OnHide", function()
    browseOnlyMode = false
    if uiIsHidden then
        TransmogCollection_ToggleUI() -- don't leave the player's UI hidden after closing
    end
    for _, btn in ipairs(collectionButtons) do
        btn:Hide()
    end
end)

-- =====================================================================
-- Main-bar button
-- =====================================================================

local function InstallCollectionButton()
    if not LFDMicroButton then
        return
    end

    -- Keep UpdateMicroButtons() (FrameXML) from disabling this by level.
    LFDMicroButton.minLevel = 0
    LFDMicroButton:Enable()

    LFDMicroButton:SetNormalTexture(COLLECTION_BUTTON_ICON)
    LFDMicroButton:SetPushedTexture(COLLECTION_BUTTON_ICON)
    LFDMicroButton:SetDisabledTexture(COLLECTION_BUTTON_ICON)
    LFDMicroButton:SetHighlightTexture("Interface\\Buttons\\UI-MicroButton-Hilight", "ADD")

    local textures = {
        LFDMicroButton:GetNormalTexture(),
        LFDMicroButton:GetPushedTexture(),
        LFDMicroButton:GetDisabledTexture(),
    }
    for _, tex in ipairs(textures) do
        if tex then
            tex:ClearAllPoints()
            tex:SetWidth(29)
            tex:SetHeight(37.5)
            tex:SetPoint("CENTER", LFDMicroButton, "CENTER", 0, -10.3)
            -- Source art is 32x41, padded to a 32x64 canvas since the
            -- WotLK client only loads power-of-two textures - crop back
            -- down to just the real art.
            tex:SetTexCoord(0, 1, 0, 0.640625)
        end
    end

    LFDMicroButton:SetScript("OnEnter", function(self)
        GameTooltip:SetOwner(self, "ANCHOR_LEFT")
        local key = GetBindingKey("CLICK LFDMicroButton:LeftButton")
        if key then
            GameTooltip:SetText("Collection |cffffd200(" .. key .. ")|r", 1, 1, 1)
        else
            GameTooltip:SetText("Collection", 1, 1, 1)
        end
        GameTooltip:Show()
    end)
    LFDMicroButton:SetScript("OnLeave", function()
        GameTooltip:Hide()
    end)

    LFDMicroButton:SetScript("OnClick", function()
        PlaySound("igMainMenuOptionCheckBoxOn")
        TransmogCollection_Toggle()
    end)
end

-- =====================================================================
-- Hotkey
--
-- Whatever key(s) were bound to the Dungeon Finder toggle now open the
-- collection browser instead. Only done once ever (tracked in a saved
-- variable) so it doesn't fight the player if they later rebind it
-- themselves via the normal Key Bindings UI.
-- =====================================================================

local function RebindDungeonFinderKey()
    TransmogCollectionDB = TransmogCollectionDB or {}
    if TransmogCollectionDB.rebindDone then
        return
    end

    SetBinding("I", "CLICK LFDMicroButton:LeftButton")
    SaveBindings(GetCurrentBindingSet())

    TransmogCollectionDB.rebindDone = true
end

local loader = CreateFrame("Frame")
loader:RegisterEvent("PLAYER_LOGIN")
loader:SetScript("OnEvent", function()
    InstallCollectionButton()
    RebindDungeonFinderKey()
end)
