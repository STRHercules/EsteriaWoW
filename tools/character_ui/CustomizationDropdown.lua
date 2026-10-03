-- Esteria customization dropdown: reuse the native selectors and Glue widgets.
local picker;

local function PickerState(id)
    if EA_ACTIVE() then
        return CycleCharCustomization("EA_GET", id);
    end
    return CycleCharCustomization("EA_STOCK_GET", id);
end

local function ChoiceText(id, value, label)
    if (CharacterCreate.selectedRaceID == 48 or CharacterCreate.selectedRaceID == 49) and label == "Belt" then
        return value == 0 and "None" or "Gem";
    end
    return label.." "..(value + 1);
end

local function PickerSignature()
    local parts = {CharacterCreate.selectedRaceID or 0, GetSelectedSex(), select(3, GetSelectedClass()) or 0};
    for i = 1, EA_ACTIVE() and 29 or 5 do
        local value = PickerState(i);
        parts[#parts + 1] = value or -1;
    end
    return table.concat(parts, ":");
end

function CharacterCustomization_CloseChoices()
    if picker then picker:Hide(); end
end

local function ApplyChoice(id, target)
    local value, count = PickerState(id);
    if not value or not count or value == target then return; end
    if EA_ACTIVE() then
        CycleCharCustomization("EA_SET", id, target);
    else
        -- Stock cycling may skip unavailable DBC rows; read the actual value after each step.
        for i = 1, count do
            local previous = value;
            CycleCharCustomization(id, 1);
            value = PickerState(id);
            if value == target or value == previous then break; end
        end
    end
    CharacterCreate_UpdateHairCustomization();
end

local function RestorePreview()
    if not picker or not picker.previewRow then return; end
    if PickerSignature() == picker.signature then
        CycleCharCustomization("EA_PREVIEW_RESTORE", 1);
        CharacterCreate_UpdateHairCustomization();
    end
    picker.previewRow = nil;
    picker.signature = PickerSignature();
end

local function PreviewChoice(self)
    if not picker:IsShown() or not picker.saved then return; end
    if PickerSignature() ~= picker.signature then picker:Hide(); return; end
    RestorePreview();
    ApplyChoice(picker.optionID, self.choice);
    picker.previewRow = self;
    picker.signature = PickerSignature();
end

local function SelectChoice(self)
    local id, target = picker.optionID, self.choice;
    picker:Hide();
    PlaySound("gsCharacterCreationLook");
    ApplyChoice(id, target);
end

local function ScrollChoices(_, delta)
    picker.scrollbar:SetValue(picker.offset - delta);
end

local function RefreshChoices()
    RestorePreview();
    local hovered;
    for i, row in ipairs(picker.rows) do
        local value = picker.choices[picker.offset + i];
        if value then
            row.choice = value;
            row:SetText(ChoiceText(picker.optionID, value, picker.label));
            if value == picker.selected then row:LockHighlight(); else row:UnlockHighlight(); end
            row:Show();
            if row.hovered then hovered = row; end
        else
            row:Hide();
        end
    end
    if hovered then PreviewChoice(hovered); end
end

function CharacterCustomization_OpenChoices(self)
    if picker and picker:IsShown() then
        local sameOwner = picker.owner == self;
        picker:Hide();
        if sameOwner then return; end
    end
    local id = self:GetParent():GetID();
    local value, count, label = PickerState(id);
    if not count or count < 2 then return; end
    label = label or _G[self:GetParent():GetName().."Text"]:GetText();
    label = label:gsub("%s+%d+/%d+$", ""):gsub("%s+None$", ""):gsub("%s+Gem$", "");
    local choices = {};
    local encoded = CycleCharCustomization(EA_ACTIVE() and "EA_CHOICES" or "EA_STOCK_CHOICES", id);
    for choice in string.gmatch(encoded or "", "%d+") do
        choices[#choices + 1] = tonumber(choice);
    end
    if #choices < 2 then return; end
    if not picker then
        picker = CreateFrame("Frame", "CharacterCustomizationChoiceMenu", CharacterCreateFrame);
        picker:SetFrameStrata("TOOLTIP");
        local dismiss = CreateFrame("Button", "CharacterCustomizationChoiceDismiss", CharacterCreateFrame);
        dismiss:SetAllPoints(CharacterCreateFrame);
        dismiss:SetFrameStrata("TOOLTIP");
        picker:SetFrameLevel(dismiss:GetFrameLevel() + 1);
        dismiss:SetScript("OnClick", CharacterCustomization_CloseChoices);
        picker:SetScript("OnShow", function()
            CycleCharCustomization("EA_WHEEL_BLOCK", 1);
            dismiss:Show();
        end);
        picker:SetScript("OnHide", function()
            RestorePreview();
            CycleCharCustomization("EA_PREVIEW_END", 1);
            CycleCharCustomization("EA_WHEEL_BLOCK", 0);
            picker.saved = nil;
            for _, row in ipairs(picker.rows or {}) do row.hovered = false; end
            dismiss:Hide();
        end);
        dismiss:Hide();
        picker:Hide();
        picker:SetClampedToScreen(true);
        picker:EnableMouse(true);
        picker:SetBackdrop({bgFile="Interface\\Glues\\Common\\Glue-Tooltip-Background",
            edgeFile="Interface\\Glues\\Common\\Glue-Tooltip-Border", tile=true, tileSize=16, edgeSize=16,
            insets={left=5, right=5, top=5, bottom=5}});
        picker.rows = {};
        for i = 1, 10 do
            local row = CreateFrame("Button", nil, picker);
            row:SetSize(260, 24);
            row:SetPoint("TOPLEFT", 10, -8 - (i - 1) * 24);
            row:SetNormalFontObject(GlueFontNormalSmall);
            row:SetHighlightFontObject(GlueFontHighlightSmall);
            row:SetHighlightTexture("Interface\\QuestFrame\\UI-QuestTitleHighlight");
            row:SetScript("OnClick", SelectChoice);
            row:SetScript("OnEnter", function(self) self.hovered = true; PreviewChoice(self); end);
            row:SetScript("OnLeave", function(self)
                self.hovered = false;
                if picker.previewRow == self then RestorePreview(); end
            end);
            row:EnableMouseWheel(true);
            row:SetScript("OnMouseWheel", ScrollChoices);
            picker.rows[i] = row;
        end
        picker.scrollbar = CreateFrame("Slider", "CharacterCustomizationChoiceMenuScrollBar",
            picker, "GlueScrollBarTemplate");
        picker.scrollbar:SetPoint("TOPRIGHT", -8, -24);
        picker.scrollbar:SetPoint("BOTTOMRIGHT", -8, 24);
        picker.scrollbar:SetValueStep(1);
        picker.scrollbar:EnableMouseWheel(true);
        picker.scrollbar:SetScript("OnMouseWheel", ScrollChoices);
        picker.scrollbar:SetScript("OnValueChanged", function(_, offset)
            picker.offset = math.floor(offset + .5);
            RefreshChoices();
        end);
        for _, direction in ipairs({"Up", "Down"}) do
            local button = _G["CharacterCustomizationChoiceMenuScrollBarScroll"..direction.."Button"];
            button:EnableMouseWheel(true);
            button:SetScript("OnMouseWheel", ScrollChoices);
            button:SetScript("OnClick",
                function() picker.scrollbar:SetValue(picker.offset + (direction == "Up" and -1 or 1)); end);
        end
        picker:EnableMouseWheel(true);
        picker:SetScript("OnMouseWheel", ScrollChoices);
        picker:SetScript("OnUpdate", function(self, elapsed)
            self.elapsed = (self.elapsed or 0) + elapsed;
            if self.elapsed > .15 then
                self.elapsed = 0;
                if not self.owner:IsVisible() or PickerSignature() ~= self.signature then self:Hide(); end
            end
        end);
    end
    picker.owner, picker.optionID, picker.label = self, id, label;
    picker.choices, picker.selected, picker.offset = choices, value, 0;
    picker.signature = PickerSignature();
    picker.saved = CycleCharCustomization("EA_PREVIEW_SAVE", 1) == 1;
    picker:ClearAllPoints();
    picker:SetPoint("TOPLEFT", self, "BOTTOMLEFT", -8, -2);
    picker:SetSize(300, 16 + math.min(10, #choices) * 24);
    picker.scrollbar:SetMinMaxValues(0, math.max(0, #choices - 10));
    local selectedRow = 1;
    for i, choice in ipairs(choices) do if choice == value then selectedRow = i; break; end end
    picker.offset = math.min(math.max(0, selectedRow - 5), math.max(0, #choices - 10));
    picker.scrollbar:SetValue(picker.offset);
    if #choices > 10 then picker.scrollbar:Show(); else picker.scrollbar:Hide(); end
    RefreshChoices();
    picker:Show();
end

local randomize = CharacterCreate_Randomize;
function CharacterCreate_Randomize()
    CharacterCustomization_CloseChoices();
    randomize();
    if EA_ACTIVE() and CharacterCreate.selectedRaceID ~= 46 and CharacterCreate.selectedRaceID ~= 48
        and CharacterCreate.selectedRaceID ~= 49 and CharacterCreate.selectedRaceID ~= 50
        and CharacterCreate.selectedRaceID ~= 51 then
        for i = 1, 29 do
            local _, count = PickerState(i);
            if count and count > 1 then CycleCharCustomization("EA_SET", i, math.random(0, count - 1)); end
        end
    end
    CharacterCreate_UpdateHairCustomization();
end

local keyDown = CharacterCreate_OnKeyDown;
function CharacterCreate_OnKeyDown(key)
    if key == "ESCAPE" and picker and picker:IsShown() then picker:Hide(); return; end
    if key == "ENTER" then CharacterCustomization_CloseChoices(); end
    keyDown(key);
end
