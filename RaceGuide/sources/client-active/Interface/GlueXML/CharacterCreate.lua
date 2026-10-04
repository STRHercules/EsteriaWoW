-- ============================================================================
-- Autora: Noa
-- ============================================================================
CHARACTER_FACING_INCREMENT = 2;
MAX_RACES = 64;
MAX_CLASSES_PER_RACE = 10;
CHARACTER_CREATE_DEBUG_RACE_ENUMERATION = false;
NUM_CHAR_CUSTOMIZATIONS = 5;
MIN_CHAR_NAME_LENGTH = 2;
CHARACTER_CREATE_ROTATION_START_X = nil;
CHARACTER_ROTATION_INCREMENT = 90;
CHARACTER_CREATE_INITIAL_FACING = nil;

PAID_CHARACTER_CUSTOMIZATION = 1;
PAID_RACE_CHANGE = 2;
PAID_FACTION_CHANGE = 3;
PAID_SERVICE_CHARACTER_ID = nil;
PAID_SERVICE_TYPE = nil;

FACTION_BACKDROP_COLOR_TABLE = {
    ["Alliance"] = {0.5, 0.5, 0.5, 0.09, 0.09, 0.19},
    ["Horde"] = {0.5, 0.2, 0.2, 0.19, 0.05, 0.05},
};
FRAMES_TO_BACKDROP_COLOR = {
    "CharacterCreateCharacterRace",
    "CharacterCreateCharacterClass",
--	"CharacterCreateCharacterFaction",
    "CharacterCreateNameEdit",
    "CharacterCreateLastNameEdit",
};
RACE_ICON_TCOORDS = {
    ["HUMAN_MALE"] = {0, 0.125, 0, 0.25},
    ["DWARF_MALE"] = {0.125, 0.25, 0, 0.25},
    ["GNOME_MALE"] = {0.25, 0.375, 0, 0.25},
    ["NIGHTELF_MALE"] = {0.375, 0.5, 0, 0.25},
    ["DRAENEI_MALE"] = {0.5, 0.625, 0, 0.25},
    ["WORGEN_MALE"] = {0.625, 0.750, 0, 0.25},
    ["HIGHELF_MALE"] = {0.750, 0.875, 0, 0.25},
    ["BROKEN_MALE"] = {0.750, 0.875, 0.5, 0.625},
    ["TAUREN_MALE"] = {0, 0.125, 0.25, 0.5},
    ["SCOURGE_MALE"] = {0.125, 0.25, 0.25, 0.5},
    ["TROLL_MALE"] = {0.25, 0.375, 0.25, 0.5},
    ["ORC_MALE"] = {0.375, 0.5, 0.25, 0.5},
    ["BLOODELF_MALE"] = {0.5, 0.625, 0.25, 0.5},
    ["GOBLIN_MALE"] = {0.625, 0.750, 0.25, 0.5},
    ["MAGHAR_MALE"] = {0.750, 0.875, 0.25, 0.5},
    ["SETHRAK_MALE"] = {0.875, 1.0, 0.25, 0.5},
    ["HUMAN_FEMALE"] = {0, 0.125, 0.5, 0.75},
    ["DWARF_FEMALE"] = {0.125, 0.25, 0.5, 0.75},
    ["GNOME_FEMALE"] = {0.25, 0.375, 0.5, 0.75},
    ["NIGHTELF_FEMALE"] = {0.375, 0.5, 0.5, 0.75},
    ["DRAENEI_FEMALE"] = {0.5, 0.625, 0.5, 0.75},
    ["WORGEN_FEMALE"] = {0.625, 0.750, 0.5, 0.75},
    ["HIGHELF_FEMALE"] = {0.750, 0.875, 0.5, 0.75},
    ["BROKEN_FEMALE"] = {0.750, 0.875, 0.625, 0.75},
    ["TAUREN_FEMALE"] = {0, 0.125, 0.75, 1.0},
    ["SCOURGE_FEMALE"] = {0.125, 0.25, 0.75, 1.0},
    ["TROLL_FEMALE"] = {0.25, 0.375, 0.75, 1.0},
    ["ORC_FEMALE"] = {0.375, 0.5, 0.75, 1.0},
    ["BLOODELF_FEMALE"] = {0.5, 0.625, 0.75, 1.0},
    ["GOBLIN_FEMALE"] = {0.625, 0.750, 0.75, 1.0},
    ["MAGHAR_FEMALE"] = {0.750, 0.875, 0.75, 1.0},
    ["SETHRAK_FEMALE"] = {0.875, 1.0, 0.75, 1.0},
};
RACE_ICON_TEXTURES = {
    ["THINHUMANHORDE_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-ThinHumanHordeMale",
    ["VRYKULHORDE_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-VrykulHordeMale",
    ["VRYKUL_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-VrykulMale",
    ["TUSKARR_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-TuskarrMale",
    ["THINHUMAN_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-ThinHumanMale",
    ["NAGAHORDE_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-NagaHordeMale",
    ["NAGAHORDE_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-NagaHordeFemale",
    ["TUSKARR_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-TuskarrMale",
    ["VRYKUL_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-VrykulMale",
    ["VRYKULHORDE_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-VrykulHordeMale",
    ["THINHUMAN_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-ThinHumanMale",
    ["THINHUMANHORDE_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-ThinHumanHordeMale",
    ["HARANIR_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-HaranirMale",
    ["HARANIR_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-HaranirFemale",
    ["HARANIRHORDE_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-HaranirHordeMale",
    ["HARANIRHORDE_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-HaranirHordeFemale",
    ["EARTHEN_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-EarthenMale",
    ["EARTHEN_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-EarthenFemale",
    ["EARTHENHORDE_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-EarthenHordeMale",
    ["EARTHENHORDE_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-EarthenHordeFemale",
    ["HIGHMOUNTAINTAUREN_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-HighmountainTaurenMale",
    ["HIGHMOUNTAINTAUREN_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-HighmountainTaurenFemale",
    ["MECHAGNOME_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-MechagnomeMale",
    ["MECHAGNOME_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-MechagnomeFemale",
    ["MAGHAR_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-MagharFemale",
    ["MAGHAR_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-MagharMale",
    ["SKYBORNE_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-SkyborneMale",
    ["SKYBORNE_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-SkyborneFemale",
    ["SKYBORNEHORDE_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-SkyborneHordeMale",
    ["SKYBORNEHORDE_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-SkyborneHordeFemale",
	["EREDAR_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-EredarMale",
	["EREDAR_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-EredarFemale",
	["NIGHTBORNE_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-NightborneMale",
	["NIGHTBORNE_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-NightborneFemale",
	["VOIDELF_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-VoidElfMale",
	["VOIDELF_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-VoidElfFemale",
	["LIGHTFORGEDDRAENEI_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-LightforgedMale",
	["LIGHTFORGEDDRAENEI_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-LightforgedFemale",
	["ZANDALARITROLL_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-ZandalariMale",
	["ZANDALARITROLL_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-ZandalariFemale",
	["DARKIRONDWARF_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-DarkIronMale",
	["DARKIRONDWARF_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-DarkIronFemale",
	["DRACTHYR_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-DracthyrMale",
	["DRACTHYR_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-DracthyrFemale",
	["KULTIRAN_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-KulTiranMale",
	["KULTIRAN_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-KulTiranFemale",
	["ILLIDARI_ALLIANCE_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-DemonHunterAllianceMale",
	["ILLIDARI_ALLIANCE_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-DemonHunterAllianceFemale",
	["ILLIDARI_HORDE_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-DemonHunterHordeMale",
	["ILLIDARI_HORDE_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-DemonHunterHordeFemale",
    ["BLOODELF_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-BloodElfFemale",
    ["BLOODELF_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-BloodElfMale",
    ["DARKFALLENHORDE_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-DarkfallenHordeMale",
    ["DARKFALLENHORDE_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-DarkfallenHordeFemale",
    ["DARKFALLEN_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-DarkfallenMale",
    ["DARKFALLEN_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-DarkfallenFemale",
    ["BROKEN_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-BrokenFemale",
    ["BROKEN_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-BrokenMale",
    ["DRAENEI_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-DraeneiFemale",
    ["DRAENEI_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-DraeneiMale",
    ["DWARF_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-DwarfFemale",
    ["DWARF_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-DwarfMale",
    ["GNOME_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-GnomeFemale",
    ["GNOME_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-GnomeMale",
    ["GOBLIN_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-GoblinFemale",
    ["GOBLIN_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-GoblinMale",
    ["HIGHELF_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-HighElfFemale",
    ["HIGHELF_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-HighElfMale",
    ["HUMAN_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-HumanFemale",
    ["HUMAN_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-HumanMale",
    ["NIGHTELF_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-NightElfFemale",
    ["NIGHTELF_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-NightElfMale",
    ["ORC_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-OrcFemale",
    ["ORC_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-OrcMale",
    ["PANDAREN_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-PandarenFemale",
    ["PANDAREN_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-PandarenMale",
    ["SCOURGE_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-ScourgeFemale",
    ["SCOURGE_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-ScourgeMale",
    ["TAUREN_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-TaurenFemale",
    ["TAUREN_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-TaurenMale",
    ["TROLL_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-TrollFemale",
    ["TROLL_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-TrollMale",
    ["VULPERA_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-VulperaFemale",
    ["VULPERA_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-VulperaMale",
    ["WORGEN_FEMALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-WorgenFemale",
    ["WORGEN_MALE"] = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-WorgenMale",
};
local function GetRaceIconTextureKey(fileString, gender, faction)
    fileString = strupper(fileString or "");
    if fileString == "ILLIDARI" and faction then
        return fileString.."_"..strupper(faction).."_"..gender;
    end
    return fileString.."_"..gender;
end
CLASS_ICON_TCOORDS = {
    ["WARRIOR"]	    = {0.000000000, 0.063000000, 0.872000000, 1.000000000},
    ["MAGE"]	    = {0.127441406, 0.189941406, 0.872070313, 1.000000000},
    ["ROGUE"]	    = {0.191406250, 0.253906250, 0.872070313, 1.000000000},
    ["DRUID"]	    = {0.447753906, 0.510253906, 0.872070313, 1.000000000},
    ["HUNTER"]	    = {0.063476563, 0.126464844, 0.872070313, 1.000000000},
    ["SHAMAN"]	    = {0.512695313, 0.575195313, 0.872070313, 1.000000000},
    ["PRIEST"]	    = {0.255859375, 0.318359375, 0.872070313, 1.000000000},
    ["WARLOCK"]	    = {0.319824219, 0.382324219, 0.872070313, 1.000000000},
    ["PALADIN"]	    = {0.383300781, 0.445800781, 0.872070313, 1.000000000},
    ["DEATHKNIGHT"]	= {0.576660156, 0.639160156, 0.872070313, 1.000000000},
};

if not _G.ALLIANCE_RACES then
    _G.ALLIANCE_RACES = {1, 2, 3, 4, 5, 6, 7}
end

if not _G.HORDE_RACES then
    _G.HORDE_RACES = {8, 9, 10, 11, 12, 13, 14, 15}
end

local HideNameEditFrame = CreateFrame("Frame")
local hideScheduled = false

local AllianceTooltip
local HordeTooltip
local raceTooltips = {};
local classTooltips = {};
local detailedRaceTooltips = {};
local detailedClassTooltips = {};
local brokenRaceInfo = {
    Name = "Broken",
    Description = "Broken draenei survive through ingenuity, stealth, and an unbroken connection to the Naaru.",
    Spell_1 = {name = "Salvager", icon = "trade_engineering", description = "Engineering and Mining skill increased by 10, and repair costs reduced by 10%."},
    Spell_2 = {name = "Krokul Cunning", icon = "ability_hunter_misdirection", description = "Reduces the radius at which enemies detect you by 5 yards."},
    Spell_3 = {name = "Fel-Scarred", icon = "spell_shadow_antimagicshell", description = "Magic effects that would drain your mana are 10% less effective, and Shadow resistance increased by 10."},
    Spell_4 = {name = "Echo of the Naaru", icon = "spell_holy_holyprotection", description = "Restore 15% maximum health over 10 seconds. 3 minute cooldown."},
}

local function HideAllTooltips()
    for button, tooltip in pairs(raceTooltips) do
        if tooltip then
            tooltip:Hide()
        end
    end

    for button, tooltip in pairs(classTooltips) do
        if tooltip then
            tooltip:Hide()
        end
    end

    if AllianceTooltip then
        AllianceTooltip:Hide()
    end

    if HordeTooltip then
        HordeTooltip:Hide()
    end
end

local backdrop = {
    bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
    edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
    tile = true, tileSize = 16, edgeSize = 16,
    insets = { left = 4, right = 4, top = 4, bottom = 4 }
};

local Backdrop2 = {
    bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
    edgeFile = "Interface\\Tooltips\\ui-tooltip-border-maw",
    tile = true, tileSize = 16, edgeSize = 16,
    insets = { left = 4, right = 4, top = 4, bottom = 4 }
};

local function GetOrCreateRaceTooltip(button)
    if not raceTooltips[button] then
        local tooltip = CreateFrame("Frame", nil, CharacterCreateFrame)
        tooltip:SetBackdrop(Backdrop2)
        tooltip:SetSize(280, 150)
        tooltip:SetFrameStrata("TOOLTIP")
        tooltip:SetBackdropColor(0, 0, 0, 1)

        local raceID = button.raceID or button:GetID()
        local faction = _G.GetFactionForRaceID(raceID)

        if faction == "Alliance" then
            tooltip:SetPoint("LEFT", CharacterCreateFrame, "LEFT", 160, 50)
        elseif faction == "Horde" then
            tooltip:SetPoint("RIGHT", CharacterCreateFrame, "RIGHT", -160, 50)
        else
            tooltip:SetPoint("CENTER", CharacterCreateFrame, "CENTER", 0, 0)
        end

        tooltip.text = tooltip:CreateFontString(nil, "OVERLAY", "GlueFontNormalSmall")
        tooltip.text:SetFont("Fonts\\FRIZQT__.TTF", 10, "OUTLINE")
        tooltip.text:SetPoint("TOPLEFT", tooltip, "TOPLEFT", 10, -10)
        tooltip.text:SetTextColor(1, 0.82, 0)
        tooltip.text:SetJustifyH("LEFT")

        tooltip.detailsText = tooltip:CreateFontString(nil, "OVERLAY")
        tooltip.detailsText:SetFont("Fonts\\FRIZQT__.TTF", 10, "OUTLINE")
        tooltip.detailsText:SetPoint("TOPLEFT", tooltip.text, "BOTTOMLEFT", 0, -5)
        tooltip.detailsText:SetWidth(260)
        tooltip.detailsText:SetWordWrap(true)
        tooltip.detailsText:SetJustifyH("LEFT")

        tooltip.rightClickText = tooltip:CreateFontString(nil, "OVERLAY")
        tooltip.rightClickText:SetFont("Fonts\\FRIZQT__.TTF", 10, "OUTLINE")
        tooltip.rightClickText:SetPoint("TOP", tooltip.detailsText, "BOTTOM", 0, -10)
        tooltip.rightClickText:SetTextColor(0.8, 0.8, 0.8)
        tooltip.rightClickText:SetJustifyH("CENTER")

        raceTooltips[button] = tooltip
    end
    return raceTooltips[button]
end

local function UpdateRaceTooltip(button, toggleDetails)
    local tooltip = GetOrCreateRaceTooltip(button)
    local raceID = button:GetID()
    local info = button.raceInfo
    if button.name == "Broken" or button.raceFileString and strupper(button.raceFileString) == "BROKEN" or info and info.Name == "Broken" then
        info = brokenRaceInfo
    end
    if not info then return end

    for i = 1, 6 do
        if tooltip["spellContainer"..i] then
            tooltip["spellContainer"..i]:Hide()
        end
    end

    tooltip.text:SetText("|cFFFFFFFF"..info.Name)
    tooltip.detailsText:SetText("|cffffd100"..info.Description.."|r")

    tooltip.text:ClearAllPoints()
    tooltip.text:SetPoint("TOPLEFT", tooltip, "TOPLEFT", 10, -5)

    tooltip.detailsText:ClearAllPoints()
    tooltip.detailsText:SetPoint("TOPLEFT", tooltip.text, "BOTTOMLEFT", 0, -5)

    if toggleDetails == nil then
        toggleDetails = not detailedRaceTooltips[button]
    end

    tooltip.rightClickText:SetText(toggleDetails and RACIALS_HIDE_HINT or RACIALS_SHOW_HINT)

    local lastElement = tooltip.detailsText
    local heightToAdd = 0

    tooltip.rightClickText:ClearAllPoints()
    tooltip.rightClickText:SetPoint("TOP", tooltip.detailsText, "BOTTOM", 0, -10)
    lastElement = tooltip.rightClickText

    if toggleDetails then
        for i = 1, 6 do
            if info["Spell_"..i] and info["Spell_"..i].name ~= "" then
                if not tooltip["spellContainer"..i] then
                    tooltip["spellContainer"..i] = CreateFrame("Frame", nil, tooltip)
                    tooltip["spellContainer"..i]:SetSize(260, 60)

                    tooltip["spellIcon"..i] = tooltip["spellContainer"..i]:CreateTexture(nil, "OVERLAY")
                    tooltip["spellIcon"..i]:SetTexture("Interface\\Icons\\"..info["Spell_"..i].icon)
                    tooltip["spellIcon"..i]:SetSize(25, 25)
                    tooltip["spellIcon"..i]:SetPoint("TOPLEFT", -35, -20)

                    tooltip["spellName"..i] = tooltip["spellContainer"..i]:CreateFontString(nil, "OVERLAY")
                    tooltip["spellName"..i]:SetFont("Fonts\\FRIZQT__.TTF", 10, "OUTLINE")
                    tooltip["spellName"..i]:SetPoint("LEFT", tooltip["spellIcon"..i], "RIGHT", 5, 8)
                    tooltip["spellName"..i]:SetTextColor(1, 0.82, 0)
                    tooltip["spellName"..i]:SetJustifyH("LEFT")

                    tooltip["spellDesc"..i] = tooltip["spellContainer"..i]:CreateFontString(nil, "OVERLAY")
                    tooltip["spellDesc"..i]:SetFont("Fonts\\FRIZQT__.TTF", 9, "OUTLINE")
                    tooltip["spellDesc"..i]:SetWordWrap(true)
                    tooltip["spellDesc"..i]:SetJustifyH("LEFT")
                    tooltip["spellDesc"..i]:SetPoint("TOPLEFT", tooltip["spellName"..i], "BOTTOMLEFT", 0, -2)
                end

                tooltip["spellName"..i]:SetText(info["Spell_"..i].name)
                tooltip["spellDesc"..i]:SetText(info["Spell_"..i].description)

                tooltip["spellContainer"..i]:Show()
                tooltip["spellContainer"..i]:ClearAllPoints()
                tooltip["spellContainer"..i]:SetPoint("TOPLEFT", lastElement, "BOTTOMLEFT", 0, 3)

                local containerHeight = tooltip["spellIcon"..i]:GetHeight() + tooltip["spellDesc"..i]:GetHeight() + 3
                tooltip["spellContainer"..i]:SetHeight(containerHeight)

                lastElement = tooltip["spellContainer"..i]
            end
        end
    end

    local maxWidth = math.max(tooltip.text:GetWidth(), tooltip.detailsText:GetWidth())
    if toggleDetails then
        for i = 1, 6 do
            if tooltip["spellContainer"..i] and tooltip["spellContainer"..i]:IsShown() then
                local nameWidth = tooltip["spellName"..i]:GetStringWidth()
                maxWidth = math.max(maxWidth, nameWidth + 70)
            end
        end
    end
    maxWidth = math.max(280, math.min(maxWidth + 40, 600))
    tooltip:SetWidth(300)

    if toggleDetails then
        for i = 1, 6 do
            if tooltip["spellContainer"..i] and tooltip["spellContainer"..i]:IsShown() then
                tooltip["spellDesc"..i]:SetWidth(maxWidth - 60)
                local containerHeight = tooltip["spellIcon"..i]:GetHeight() + tooltip["spellDesc"..i]:GetHeight() + 3
                tooltip["spellContainer"..i]:SetHeight(containerHeight)
            end
        end
    end

    heightToAdd = 0
    if toggleDetails then
        for i = 1, 6 do
            if tooltip["spellContainer"..i] and tooltip["spellContainer"..i]:IsShown() then
                heightToAdd = heightToAdd + tooltip["spellContainer"..i]:GetHeight() + 3
            end
        end
    end

    local baseHeight = tooltip.text:GetHeight() +
                      tooltip.detailsText:GetHeight() +
                      tooltip.rightClickText:GetHeight() + 25

    tooltip:SetHeight(baseHeight + heightToAdd)
    detailedRaceTooltips[button] = toggleDetails
    tooltip:ClearAllPoints()

    local pos = _G.GetRaceTooltipPosition(raceID, button)
    tooltip:SetPoint(pos.point, button, pos.relPoint, pos.x, pos.y)
end

local function GetOrCreateClassTooltip(button)
    if not classTooltips[button] then
        local tooltip = CreateFrame("Frame", nil, CharacterCreateFrame)
        tooltip:SetBackdrop(Backdrop2)
        tooltip:SetSize(300, 200)
        tooltip:SetFrameStrata("TOOLTIP")
        tooltip:SetBackdropColor(0, 0, 0, 1)

        tooltip.text = tooltip:CreateFontString(nil, "OVERLAY", "GlueFontNormalSmall")
        tooltip.text:SetFont("Fonts\\FRIZQT__.TTF", 10, "OUTLINE")
        tooltip.text:SetPoint("TOPLEFT", tooltip, "TOPLEFT", 8, -8)
        tooltip.text:SetTextColor(1, 0.82, 0)
        tooltip.text:SetJustifyH("LEFT")

        tooltip.detailsText = tooltip:CreateFontString(nil, "OVERLAY")
        tooltip.detailsText:SetFont("Fonts\\FRIZQT__.TTF", 10, "OUTLINE")
        tooltip.detailsText:SetPoint("TOPLEFT", tooltip.text, "BOTTOMLEFT", 0, -5)
        tooltip.detailsText:SetWidth(284)
        tooltip.detailsText:SetWordWrap(true)
        tooltip.detailsText:SetJustifyH("LEFT")

        tooltip.Roles = tooltip:CreateFontString(nil, "OVERLAY", "GlueFontNormalSmall")
        tooltip.Roles:SetFont("Fonts\\FRIZQT__.TTF", 10, "OUTLINE")
        tooltip.Roles:SetWidth(284)
        tooltip.Roles:SetWordWrap(true)
        tooltip.Roles:SetJustifyH("LEFT")

        classTooltips[button] = tooltip
    end

    return classTooltips[button]
end

local function GetValidRacesForClass(classID)
    local allianceRaces = {}
    local hordeRaces = {}

    for _, raceID in ipairs(_G.ALLIANCE_RACES) do
        if IsRaceClassValid(raceID, classID) then
            local raceName = _G["RACE_" .. raceID] or RACE .. raceID
            table.insert(allianceRaces, raceName)
        end
    end

    for _, raceID in ipairs(_G.HORDE_RACES) do
        if IsRaceClassValid(raceID, classID) then
            local raceName = _G["RACE_" .. raceID] or RACE .. raceID
            table.insert(hordeRaces, raceName)
        end
    end

    return allianceRaces, hordeRaces
end
local function UpdateClassTooltip(button)
    local tooltip = GetOrCreateClassTooltip(button)
    local classID = button:GetID()
    local info = _G.Class_Informations[classID]

    if not info then return end

    local buttonX, buttonY = button:GetCenter()
    local parentX, parentY = CharacterCreateFrame:GetCenter()

    if buttonX > parentX then
        tooltip:SetPoint("BOTTOMRIGHT", button, "TOPRIGHT", 0, 10)
    else
        tooltip:SetPoint("BOTTOMLEFT", button, "TOPLEFT", 0, 10)
    end

    tooltip.text:SetText("|cFFFFFFFF"..info.Name)
    tooltip.detailsText:SetText("|cffffd100"..info.Description.."|r")

    tooltip.text:ClearAllPoints()
    tooltip.text:SetPoint("TOPLEFT", tooltip, "TOPLEFT", 8, -8)

    tooltip.detailsText:ClearAllPoints()
    tooltip.detailsText:SetPoint("TOPLEFT", tooltip.text, "BOTTOMLEFT", 0, -5)

    local currentRaceID = GetSelectedRace()
    local isAllowed = IsRaceClassValid(currentRaceID, classID)
    local showRestriction = not isAllowed

    tooltip.RestrictionText = tooltip.RestrictionText or tooltip:CreateFontString(nil, "OVERLAY")
    tooltip.RestrictionText:SetFont("Fonts\\FRIZQT__.TTF", 12, "OUTLINE")
    tooltip.RestrictionText:SetJustifyH("LEFT")

    tooltip.FactionText = tooltip.FactionText or tooltip:CreateFontString(nil, "OVERLAY")
    tooltip.FactionText:SetFont("Fonts\\FRIZQT__.TTF", 11)
    tooltip.FactionText:SetWordWrap(true)
    tooltip.FactionText:SetJustifyH("LEFT")

    local coloredRoles = info.Roles
    coloredRoles = string.gsub(coloredRoles, "Daño cuerpo a cuerpo", "|cffff2020Daño cuerpo a cuerpo|r")
    coloredRoles = string.gsub(coloredRoles, "Daño a distancia", "|cffff2020Daño a distancia|r")
    coloredRoles = string.gsub(coloredRoles, "Tanque", "|cff0070ddTanque|r")
    coloredRoles = string.gsub(coloredRoles, "Sanador", "|cff20c000Sanador|r")

    if not tooltip.Roles then
        tooltip.Roles = tooltip:CreateFontString(nil, "OVERLAY")
        tooltip.Roles:SetFont("Fonts\\FRIZQT__.TTF", 11)
    end

    tooltip.Roles:SetText("|cFFFFFFFF"..FUNTION_INF.."|r\n\n "..coloredRoles)

    if showRestriction then
        tooltip.Roles:ClearAllPoints()
        tooltip.Roles:SetPoint("TOPLEFT", tooltip.detailsText, "BOTTOMLEFT", 0, -20)
        tooltip.Roles:Show()

        tooltip.RestrictionText:SetPoint("TOPLEFT", tooltip.Roles, "BOTTOMLEFT", 0, -20)
        tooltip.RestrictionText:SetTextColor(1, 0, 0)
        tooltip.RestrictionText:SetText(WARNING_RACE)
        tooltip.RestrictionText:Show()

        local allianceRaces, hordeRaces = GetValidRacesForClass(classID)

        local factionText = ""

        if #allianceRaces > 0 then
            factionText = ALLIANCE_RACE .. " |cFFFFFFFF" .. table.concat(allianceRaces, ", ") .. "|r"
        end

        if #hordeRaces > 0 then
            if factionText ~= "" then
                factionText = factionText .. "\n\n"
            end
            factionText = factionText .. "\n" .. HORDE_RACE .. " |cFFFFFFFF" .. table.concat(hordeRaces, ", ") .. "|r"
        end

        tooltip.FactionText:SetPoint("TOPLEFT", tooltip.RestrictionText, "BOTTOMLEFT", 0, -15)
        tooltip.FactionText:SetTextColor(1, 0.82, 0)
        tooltip.FactionText:SetText(factionText)
        tooltip.FactionText:Show()

        local maxWidth = math.max(tooltip.text:GetWidth(), tooltip.detailsText:GetWidth())
        maxWidth = math.max(maxWidth, tooltip.Roles:GetWidth())
        maxWidth = math.max(maxWidth, tooltip.RestrictionText:GetWidth())
        maxWidth = math.max(maxWidth, tooltip.FactionText:GetWidth())
        maxWidth = math.max(280, math.min(maxWidth + 16, 400))

        tooltip:SetWidth(maxWidth)
        tooltip.FactionText:SetWidth(maxWidth - 16)

        local restrictionHeight = tooltip.text:GetHeight() +
                                tooltip.detailsText:GetHeight() +
                                tooltip.Roles:GetHeight() +
                                tooltip.RestrictionText:GetHeight() +
                                tooltip.FactionText:GetHeight() + 80

        tooltip:SetHeight(restrictionHeight)

    else
        tooltip.RestrictionText:Hide()
        tooltip.FactionText:Hide()

        tooltip.Roles:Show()
        tooltip.Roles:ClearAllPoints()
        tooltip.Roles:SetPoint("TOPLEFT", tooltip.detailsText, "BOTTOMLEFT", 0, -10)

        local maxWidth = math.max(tooltip.text:GetWidth(), tooltip.detailsText:GetWidth())
        maxWidth = math.max(maxWidth, tooltip.Roles:GetWidth())
        maxWidth = math.max(280, math.min(maxWidth + 16, 400))
        tooltip:SetWidth(maxWidth)

        local baseHeight = tooltip.text:GetHeight() +
                          tooltip.detailsText:GetHeight() +
                          tooltip.Roles:GetHeight() + 30

        tooltip:SetHeight(baseHeight)
    end
end

function CharacterCreate_MoveTexturesToBackground()
    for i = 1, MAX_RACES do
        local button = _G["CharacterCreateRaceButton"..i]
        if button then
            local normalTex = _G[button:GetName().."NormalTexture"]
            local pushedTex = _G[button:GetName().."PushedTexture"]

            if normalTex then
                normalTex:SetDrawLayer("BACKGROUND")
            end
            if pushedTex then
                pushedTex:SetDrawLayer("BACKGROUND")
            end
        end
    end

    for i = 1, MAX_CLASSES_PER_RACE do
        local button = _G["CharacterCreateClassButton"..i]
        if button then
            local normalTex = _G[button:GetName().."NormalTexture"]
            local pushedTex = _G[button:GetName().."PushedTexture"]

            if normalTex then
                normalTex:SetDrawLayer("BACKGROUND")
            end
            if pushedTex then
                pushedTex:SetDrawLayer("BACKGROUND")
            end
        end
    end

    local maleButton = CharacterCreateGenderButtonMale
    local femaleButton = CharacterCreateGenderButtonFemale

    if maleButton then
        _G[maleButton:GetName().."NormalTexture"]:SetDrawLayer("BACKGROUND")
        _G[maleButton:GetName().."PushedTexture"]:SetDrawLayer("BACKGROUND")
    end

    if femaleButton then
        _G[femaleButton:GetName().."NormalTexture"]:SetDrawLayer("BACKGROUND")
        _G[femaleButton:GetName().."PushedTexture"]:SetDrawLayer("BACKGROUND")
    end
end

local function CreateFactionTooltip(parent, factionName)
    local tooltip = CreateFrame("Frame", nil, parent)
    tooltip:SetBackdrop(backdrop)
    tooltip:SetFrameStrata("TOOLTIP")
    tooltip:SetBackdropColor(0, 0, 0, 0.9)
    tooltip:SetBackdropBorderColor(1, 1, 1, 1)
    tooltip:Hide()

    tooltip.title = tooltip:CreateFontString(nil, "OVERLAY")
    tooltip.title:SetFont("Fonts\\FRIZQT__.TTF", 12, "OUTLINE")
    tooltip.title:SetPoint("TOPLEFT", tooltip, "TOPLEFT", 10, -10)
    tooltip.title:SetTextColor(1, 0.82, 0)
    tooltip.title:SetJustifyH("LEFT")

    tooltip.description = tooltip:CreateFontString(nil, "OVERLAY")
    tooltip.description:SetFont("Fonts\\FRIZQT__.TTF", 12, "OUTLINE")
    tooltip.description:SetPoint("TOPLEFT", tooltip.title, "BOTTOMLEFT", 0, -8)
    tooltip.description:SetWidth(280)
    tooltip.description:SetWordWrap(true)
    tooltip.description:SetJustifyH("LEFT")
    tooltip.description:SetTextColor(0.9, 0.9, 0.9)

    return tooltip
end

local function UpdateTooltipSize(tooltip)
    local titleHeight = tooltip.title:GetHeight()
    local descHeight = tooltip.description:GetHeight()
    local totalHeight = titleHeight + descHeight + 30

    tooltip:SetHeight(totalHeight)
    tooltip:SetWidth(300)
end

function CharacterCreate_PositionRaceButtons()
    -- Esteria compact faction grid: preserve enumeration order and exact RaceIDs.
    local width = CharacterCreateFrame:GetWidth();
    if width <= 0 then return; end
    local columns = 7;
    local spacing = math.min(72, (width * 0.36 - 32) / columns);
    local size = math.max(24, spacing - 8);
    local gridWidth = (columns - 1) * spacing + size;
    local function positionFaction(indices, side)
        local left = side == "Alliance" and 24 or width - 24 - gridWidth;
        for slot,index in ipairs(indices or {}) do
            local button = _G["CharacterCreateRaceButton"..index];
            if button then
                local column = (slot - 1) % columns;
                local row = math.floor((slot - 1) / columns);
                button:ClearAllPoints();
                button:SetSize(size, size);
                button:SetPoint("CENTER", CharacterCreateFrame, "TOPLEFT",
                    left + size / 2 + column * spacing, -100 - row * spacing);
                button:GetNormalTexture():SetSize(size, size);
                button:GetPushedTexture():SetSize(size, size);
                for _,name in ipairs({"staticTexture","highlightTexture","checkedTexture"}) do
                    if button[name] then button[name]:SetSize(size * 112 / 50, size * 112 / 50); end
                end
            end
        end
        local logo = side == "Alliance" and CustomizationLogoAlliance or CustomizationLogoHorde;
        local label = side == "Alliance" and CustomizationTextAlliance or CustomizationTextHorde;
        local hitbox = side == "Alliance" and AllianceLogoFrame or HordeLogoFrame;
        if logo and label then
            local centre = left + gridWidth / 2;
            logo:ClearAllPoints();
            logo:SetSize(56,56);
            logo:SetPoint("CENTER",CharacterCreateFrame,"TOPLEFT",
                centre + (side == "Alliance" and -44 or 44),-46);
            label:ClearAllPoints();
            if side == "Alliance" then label:SetPoint("LEFT",logo,"RIGHT",-4,0);
            else label:SetPoint("RIGHT",logo,"LEFT",4,0); end
            if hitbox then
                hitbox:ClearAllPoints(); hitbox:SetSize(56,56); hitbox:SetPoint("CENTER",logo,"CENTER",0,0);
            end
        end
    end
    positionFaction(CharacterCreate.raceIndicesAlliance,"Alliance");
    positionFaction(CharacterCreate.raceIndicesHorde,"Horde");
    if not CharacterCreateFrame.esteriaRaceLayoutResize then
        CharacterCreateFrame:HookScript("OnSizeChanged",CharacterCreate_PositionRaceButtons);
        CharacterCreateFrame.esteriaRaceLayoutResize = true;
    end
end

function CharacterCreate_PositionClassButtons()
    local buttonSpacing = 80

    for i = 1, MAX_CLASSES_PER_RACE do
        local button = _G["CharacterCreateClassButton"..i]
        if button then
            button:ClearAllPoints()

            if i == 1 then
                button:SetPoint("CENTER", CharacterCreateFrame, "BOTTOM", -360, 80)
            else
                local prevButton = _G["CharacterCreateClassButton"..(i-1)]
                button:SetPoint("LEFT", prevButton, "RIGHT", buttonSpacing - 38, 0)
            end
        end
    end
end

function CharacterCreate_PositionGenderButtons()
    local genderSpacing = 310

    local maleButton = CharacterCreateGenderButtonMale
    local femaleButton = CharacterCreateGenderButtonFemale

    if maleButton then
        maleButton:ClearAllPoints()
        maleButton:SetPoint("CENTER", CharacterCreateFrame, "CENTER", -(genderSpacing/2), -250)
    end

    if femaleButton then
        femaleButton:ClearAllPoints()
        femaleButton:SetPoint("CENTER", CharacterCreateFrame, "CENTER", (genderSpacing/2), -250)
    end
end

function CharacterCreate_PositionAllButtons()
    CharacterCreate_PositionRaceButtons()
    CharacterCreate_PositionClassButtons()
    CharacterCreate_PositionGenderButtons()
end

function CharacterCreate_OnLoad(self)
    self:SetSequence(0)
    self:SetCamera(0)
    SetCharCustomizeFrame("CharacterCreate")

    CharacterCreate.numRaces = 0
    CharacterCreate.selectedRace = 0
    CharacterCreate.numClasses = 0
    CharacterCreate.selectedClass = 0
    CharacterCreate.selectedGender = 0
    CharacterCreate.raceIndicesAlliance = {}
    CharacterCreate.raceIndicesHorde = {}
    CharacterCreateRaceButtonsContainer:SetParent(CharacterCreateFrame)
    CharacterCreate.personalizationMode = false
    CharacterCreate_MoveTexturesToBackground()
    CharacterCreate_SetupCustomButtons()

    for i=1, NUM_CHAR_CUSTOMIZATIONS, 1 do
        _G["CharacterCustomizationButtonFrame"..i.."Text"]:SetText(_G["CHAR_CUSTOMIZATION"..i.."_DESC"])
    end

    local backdropColor = FACTION_BACKDROP_COLOR_TABLE["Alliance"]
    CharacterCreateNameEdit:SetBackdropBorderColor(backdropColor[1], backdropColor[2], backdropColor[3])
    CharacterCreateNameEdit:SetBackdropColor(backdropColor[4], backdropColor[5], backdropColor[6])
    CharacterCreateLastNameEdit:SetBackdropBorderColor(backdropColor[1], backdropColor[2], backdropColor[3])
    CharacterCreateLastNameEdit:SetBackdropColor(backdropColor[4], backdropColor[5], backdropColor[6])

    CustomizationBG2 = CharacterCreateFrame:CreateTexture("CustomizationBG2", "BACKGROUND")
    CustomizationBG2:SetSize(GlueParent:GetWidth() + 2, GlueParent:GetHeight() + 6)
    CustomizationBG2:SetTexture("Interface\\Glues\\CharacterCreate\\MainShadow")
    CustomizationBG2:SetPoint("CENTER")
    CustomizationBG2:SetAlpha(0.8)

    CustomizationLogoAlliance = CharacterCreateFrame:CreateTexture("CustomizationLogoAlliance", "ARTWORK")
    CustomizationLogoAlliance:SetSize(100, 100)
    CustomizationLogoAlliance:SetTexture("Interface\\Glues\\CharacterCreate\\AllianceLogo")
    CustomizationLogoAlliance:SetPoint("TOPLEFT", -16, 16)

    CustomizationTextAlliance = CharacterCreateFrame:CreateFontString("CustomizationTextAlliance", "OVERLAY")
    CustomizationTextAlliance:SetFontObject(GlueFontNormal)
    CustomizationTextAlliance:SetText(string.upper(ALLIANCE))
    CustomizationTextAlliance:SetPoint("LEFT", CustomizationLogoAlliance, "RIGHT", -24, 0)

    AllianceTooltip = CreateFactionTooltip(CharacterCreateFrame, "Alliance")

    AllianceLogoFrame = CreateFrame("Frame", "AllianceLogoFrame", CharacterCreateFrame)
    AllianceLogoFrame:SetSize(100, 100)
    AllianceLogoFrame:SetPoint("TOPLEFT", -16, 16)
    AllianceLogoFrame:EnableMouse(true)

    AllianceLogoFrame:SetScript("OnEnter", function(self)
        AllianceTooltip.title:SetText(ALLIANCE)
        AllianceTooltip.description:SetText(FACTION_ALLIANCE_DESCRIPTION)
        UpdateTooltipSize(AllianceTooltip)
        AllianceTooltip:ClearAllPoints()
        AllianceTooltip:SetPoint("TOPLEFT", self, "BOTTOMLEFT", 90, 60)
        AllianceTooltip:Show()
    end)

    AllianceLogoFrame:SetScript("OnLeave", function(self)
        AllianceTooltip:Hide()
    end)

    CustomizationLogoHorde = CharacterCreateFrame:CreateTexture("CustomizationLogoHorde", "ARTWORK")
    CustomizationLogoHorde:SetSize(100, 100)
    CustomizationLogoHorde:SetTexture("Interface\\Glues\\CharacterCreate\\HordeLogo")
    CustomizationLogoHorde:SetPoint("TOPRIGHT", 16, 16)

    CustomizationTextHorde = CharacterCreateFrame:CreateFontString("CustomizationTextHorde", "OVERLAY")
    CustomizationTextHorde:SetFontObject(GlueFontNormal)
    CustomizationTextHorde:SetText(string.upper(HORDE))
    CustomizationTextHorde:SetPoint("RIGHT", CustomizationLogoHorde, "LEFT", 24, 0)

    HordeTooltip = CreateFactionTooltip(CharacterCreateFrame, "Horde")

    HordeLogoFrame = CreateFrame("Frame", "HordeLogoFrame", CharacterCreateFrame)
    HordeLogoFrame:SetSize(100, 100)
    HordeLogoFrame:SetPoint("TOPRIGHT", 16, 16)
    HordeLogoFrame:EnableMouse(true)

    HordeLogoFrame:SetScript("OnEnter", function(self)
        HordeTooltip.title:SetText(HORDE)
        HordeTooltip.description:SetText(FACTION_HORDE_DESCRIPTION)
        UpdateTooltipSize(HordeTooltip)
        HordeTooltip:ClearAllPoints()
        HordeTooltip:SetPoint("TOPRIGHT", self, "BOTTOMRIGHT", -90, 60)
        HordeTooltip:Show()
    end)

    HordeLogoFrame:SetScript("OnLeave", function(self)
        HordeTooltip:Hide()
    end)

    CharacterCreate_CreateGenderButtonTextures()
   CharacterCreate_PositionAllButtons()
end

-- Esteria creator dice and smooth rotation: reuse the client atlas and native name generator.
function CharacterCreate_SetupCustomButtons()
    local buttons = {
        {button = CharCreateRandomizeButton, width = 36, height = 36},
        {button = CharacterCreateRandomName, width = 30, height = 30},
        {button = CharacterCreateRandomLastName, width = 30, height = 30}
    }

    local texturePath = "Interface\\Glues\\CharacterCreate\\charactercreate"

    for _, btnInfo in ipairs(buttons) do
        local button = btnInfo.button
        if button then
            button:SetNormalTexture(texturePath)
            button:GetNormalTexture():SetTexCoord(0.261230469, 0.292480469, 0.890625000, 0.920410156)

            button:SetPushedTexture(texturePath)
            button:GetPushedTexture():SetTexCoord(0.223144531, 0.253906250, 0.890625000, 0.920410156)

            button:SetHighlightTexture("Interface\\Buttons\\UI-Common-MouseHilight")
            button:GetHighlightTexture():SetTexCoord(0.1, 0.9, 0.1, 0.9)
            button:GetHighlightTexture():SetBlendMode("ADD")

            button:SetSize(btnInfo.width, btnInfo.height)

            if button:GetFontString() then
                button:GetFontString():Hide()
            else
                button:SetText("")
            end
        end
    end
end

function CharacterCreate_TogglePersonalization()
    if (CharacterCreate.personalizationMode == false) then
        CharacterCreate.personalizationMode = true;
        PlaySound("gsCharacterSelectionCreateNew");
        CharacterCreateRaceButtonsContainer:Hide();
        CharacterCreateClassButtonsContainer:Hide();
        CharacterCreateGenderButtonsContainer:Hide();
        CustomizationLogoAlliance:Hide();
        CustomizationTextAlliance:Hide();
        CustomizationLogoHorde:Hide();
        CustomizationTextHorde:Hide();
        CharacterCreateRotateLeft:Show();
        CharacterCreateRotateRight:Show();
        CharCreatePersonalizeButton:Hide();
        CharCreateOkayButton:Show();
        CharacterCreate_UpdateHairCustomization();
        CharCreateRandomizeButton:Show();
        CharacterCreateNameEdit:Show();
        CharacterCreateLastNameEdit:Show();
        CharacterCreateRandomName:Show();
        CharacterCreateRandomLastName:Show();

        for i=1, NUM_CHAR_CUSTOMIZATIONS do
            _G["CharacterCustomizationButtonFrame"..i]:Show();
        end
    else
        CharacterCreate.personalizationMode = false;
        PlaySound("gsCharacterCreationCancel");
        CharacterCreateRaceButtonsContainer:Show();
        CharacterCreateClassButtonsContainer:Show();
        CharacterCreateGenderButtonsContainer:Show();
        CustomizationLogoAlliance:Show();
        CustomizationTextAlliance:Show();
        CustomizationLogoHorde:Show();
        CustomizationTextHorde:Show();
        CharacterCreateRotateLeft:Hide();
        CharacterCreateRotateRight:Hide();
        CharCreateRandomizeButton:Hide();
        CharacterCreateNameEdit:Hide();
        CharacterCreateLastNameEdit:Hide();
        CharacterCreateRandomName:Hide();
        CharacterCreateRandomLastName:Hide();
        CharCreatePersonalizeButton:Show();
        CharCreateOkayButton:Hide();

        for i=1, NUM_CHAR_CUSTOMIZATIONS do
            _G["CharacterCustomizationButtonFrame"..i]:Hide();
        end
    end
end

HideNameEditFrame:SetScript("OnUpdate", function(self, elapsed)
    if hideScheduled then
        CharacterCreateNameEdit:Hide()
        CharacterCreateLastNameEdit:Hide();
        CharacterCreateRandomName:Hide()
        CharacterCreateRandomLastName:Hide();
        hideScheduled = false
        self:Hide()
    end
end)

function CharacterCreate_SetNameFields(fullName)
    local firstName = "";
    local lastName = "";
    if ( fullName and fullName ~= "" ) then
        local splitFirst, splitLast = string.match(fullName, "^([^ ]+)%s*(.*)$");
        firstName = splitFirst or fullName;
        lastName = splitLast or "";
    end
    CharacterCreateNameEdit:SetText(firstName);
    CharacterCreateLastNameEdit:SetText(lastName);
end

function CharacterCreate_GetFullName()
    local firstName = CharacterCreateNameEdit:GetText() or "";
    local lastName = CharacterCreateLastNameEdit:GetText() or "";
    if ( firstName == "" ) then
        return lastName;
    elseif ( lastName == "" ) then
        return firstName;
    end
    return firstName.." "..lastName;
end

function CharacterCreate_RandomizeName(editBox)
    local field = editBox or CharacterCreateNameEdit;
    field:SetText(GetRandomName());
end

function CharacterCreate_OnShow()
    CharacterCreate.personalizationMode = false;

    for i=1, MAX_CLASSES_PER_RACE, 1 do
        local button = _G["CharacterCreateClassButton"..i];
        button:Enable();
        SetButtonDesaturated(button, false)
    end
    for i=1, MAX_RACES, 1 do
        local button = _G["CharacterCreateRaceButton"..i];
        button:Enable();
        SetButtonDesaturated(button, false)
    end

    if ( PAID_SERVICE_TYPE ) then
        CustomizeExistingCharacter( PAID_SERVICE_CHARACTER_ID );
        CharacterCreate_SetNameFields(PaidChange_GetName());
    else
        ResetCharCustomize();
        CharacterCreate_SetNameFields("");
        CharCreateRandomizeButton:Hide();
    end

    CharacterCreate.personalizationMode = false;
    CharCreateOkayButton:Hide();

    for i=1, NUM_CHAR_CUSTOMIZATIONS do
        _G["CharacterCustomizationButtonFrame"..i]:Hide();
    end

    CharacterCreateEnumerateRaces(GetAvailableRaces());
    SetCharacterRace(GetSelectedRace());
    CharacterCreateEnumerateClasses(GetAvailableClasses());
    local_,_,index = GetSelectedClass();
    SetCharacterClass(index);
    SetCharacterGender(GetSelectedSex())
    CharacterCreate_UpdateHairCustomization();
    SetCharacterCreateFacing(-15);
    CharacterChangeFixup();
    CharacterCreate_CreateGenderButtonTextures();
    CharacterCreate_UpdateButtonCheckedStates();
    CharacterCreate_ResetState();

    hideScheduled = true
    HideNameEditFrame:Show()
   CharacterCreate_PositionAllButtons()
end

function CharacterCreate_OnHide()
    PAID_SERVICE_CHARACTER_ID = nil;
    PAID_SERVICE_TYPE = nil;
    CharacterCreate_ResetState();

    for button, tooltip in pairs(raceTooltips) do
        if tooltip then tooltip:Hide() end
    end
    for button, tooltip in pairs(classTooltips) do
        if tooltip then tooltip:Hide() end
    end
    if AllianceTooltip then AllianceTooltip:Hide() end
    if HordeTooltip then HordeTooltip:Hide() end
end

function CharacterCreateFrame_OnMouseDown(button)
    if ( button == "LeftButton" ) then
        CHARACTER_CREATE_ROTATION_START_X = GetCursorPosition();
        CHARACTER_CREATE_INITIAL_FACING = GetCharacterCreateFacing();
    end
end

function CharacterCreateFrame_OnMouseUp(button)
    if ( button == "LeftButton" ) then
        CHARACTER_CREATE_ROTATION_START_X = nil
    end
end

function CharacterCreateFrame_OnUpdate()
    if ( CHARACTER_CREATE_ROTATION_START_X ) then
        local x = GetCursorPosition();
        local diff = (x - CHARACTER_CREATE_ROTATION_START_X) * CHARACTER_ROTATION_CONSTANT;
        CHARACTER_CREATE_ROTATION_START_X = GetCursorPosition();
        SetCharacterCreateFacing(GetCharacterCreateFacing() + diff);
    end
end

function CharacterCreateEnumerateRaces(...)
    CharacterCreate.numRaces = select("#", ...)/3;
    CharacterCreate.raceIndicesAlliance = {};
    CharacterCreate.raceIndicesHorde = {};
    if ( CharacterCreate.numRaces > MAX_RACES ) then
        message("Too many races!  Update MAX_RACES");
        return;
    end
    local coords;
    local index = 1;
    local button;
    local gender;
    local hiddenSelection = false;
    local selectedSex = GetSelectedSex();
    local availableRaceIDs = nil;
    if ( type(GetAvailableRaceIDs) == "function" ) then
        availableRaceIDs = {GetAvailableRaceIDs()};
    end
    if ( selectedSex == SEX_MALE ) then
        gender = "MALE";
    elseif ( selectedSex == SEX_FEMALE ) then
        gender = "FEMALE";
    end
    for i=1, select("#", ...), 3 do
        local fileString = select(i+1, ...)
        local hiddenRace = strupper(fileString) == "SETHRAK" or strupper(fileString) == "VRYKULHORDE"
        local raceID = availableRaceIDs and availableRaceIDs[index] or index;
        if ( _G.GetExactRaceIDForFileString ) then
            local exactRaceID = _G.GetExactRaceIDForFileString(fileString);
            if ( exactRaceID ) then
                raceID = exactRaceID;
            end
        end
        local _, faction = GetFactionForRace(index);
        if ( _G.GetFactionForRaceID ) then
            faction = _G.GetFactionForRaceID(raceID);
        end
        local raceKey = GetRaceIconTextureKey(fileString, gender, faction);
        local targetTexture = RACE_ICON_TEXTURES[raceKey];
        local normalTexture = _G["CharacterCreateRaceButton"..index.."NormalTexture"];
        local pushedTexture = _G["CharacterCreateRaceButton"..index.."PushedTexture"];
        if targetTexture then
            normalTexture:SetTexture(targetTexture);
            pushedTexture:SetTexture(targetTexture);
            normalTexture:SetTexCoord(0, 1, 0, 1);
            pushedTexture:SetTexCoord(0, 1, 0, 1);
        else
            coords = RACE_ICON_TCOORDS[raceKey] or RACE_ICON_TCOORDS["HUMAN_"..(gender or "MALE")];
            normalTexture:SetTexture("Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Races");
            pushedTexture:SetTexture("Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Races");
            normalTexture:SetTexCoord(coords[1], coords[2], coords[3], coords[4]);
            pushedTexture:SetTexCoord(coords[1], coords[2], coords[3], coords[4]);
        end
        button = _G["CharacterCreateRaceButton"..index];
        button.uiSlot = index;
        button.raceID = raceID;
        button.raceFileString = fileString;
        button.raceInfo = _G.RaceInfoByFileString and _G.RaceInfoByFileString[strupper(fileString)] or nil;

        if not hiddenRace then
            if faction == "Alliance" then
                table.insert(CharacterCreate.raceIndicesAlliance, index)
            else
                table.insert(CharacterCreate.raceIndicesHorde, index)
            end
        end
        local borderColor

        if faction == "Alliance" then
            borderColor = {0.0, 0.4, 1.0}
        else
            borderColor = {1.0, 0.0, 0.0}
        end

        if not button.staticTexture then
            button.staticTexture = button:CreateTexture(button:GetName().."StaticTexture", "ARTWORK");
            button.staticTexture:SetTexture("Interface\\Glues\\CharacterCreate\\IconBorder_F");
            button.staticTexture:SetSize(112, 112);
            button.staticTexture:SetPoint("CENTER", 0, 0);
            button.staticTexture:SetVertexColor(borderColor[1], borderColor[2], borderColor[3]);
        else
            button.staticTexture:SetVertexColor(borderColor[1], borderColor[2], borderColor[3]);
        end
        button.staticTexture:Hide();

        if not button.highlightTexture then
            button.highlightTexture = button:CreateTexture(button:GetName().."HighlightTexture", "HIGHLIGHT");
            button.highlightTexture:SetTexture("Interface\\Glues\\CharacterCreate\\IconBorder_F");
            button.highlightTexture:SetAlpha(0.5);
            button.highlightTexture:SetBlendMode("ADD");
            button.highlightTexture:SetSize(112, 112);
            button.highlightTexture:SetPoint("CENTER", 0, 0);
            button.highlightTexture:SetVertexColor(borderColor[1], borderColor[2], borderColor[3]);
        else
            button.highlightTexture:SetVertexColor(borderColor[1], borderColor[2], borderColor[3]);
        end

        if not button.checkedTexture then
            button.checkedTexture = button:CreateTexture(button:GetName().."CheckedTexture", "OVERLAY");
            button.checkedTexture:SetDrawLayer("OVERLAY", 7);
            button.checkedTexture:SetTexture("Interface\\Glues\\CharacterCreate\\IconBorderRace_H");
            button.checkedTexture:SetBlendMode("ADD");
            button.checkedTexture:SetSize(112, 112);
            button.checkedTexture:SetPoint("CENTER", 0, 0);
            button.checkedTexture:Hide();
        end

        if not button.texturesMoved then
            button:SetScript("OnMouseDown", nil);
            button:SetScript("OnMouseUp", nil);

            button.texturesMoved = true;
        end

        if hiddenRace then
            hiddenSelection = hiddenSelection or GetSelectedRace() == index;
            button.enable = false
            button:SetChecked(nil)
            button:Disable()
            button:Hide()
        else
            button:Show();
        end
        if not hiddenRace and ( select(i+2, ...) == 1 ) then
            button.enable = true;
            SetButtonDesaturated(button);
            button.name = select(i, ...)
            button.tooltip = select(i, ...);

            button:SetScript("OnEnter", function(self)
                if self:IsEnabled() then
                    local tooltip = GetOrCreateRaceTooltip(self)
                    tooltip:Show()
                    UpdateRaceTooltip(self, false)
                end
            end)

            button:SetScript("OnLeave", function(self)
                if self:IsEnabled() then
                    local tooltip = GetOrCreateRaceTooltip(self)
                    tooltip:Hide()
                end
            end)

            button:SetScript("OnMouseDown", function(self, clickedButton)
                if self:IsEnabled() and clickedButton == "RightButton" then
                    local tooltip = GetOrCreateRaceTooltip(self)
                    local isDetailed = detailedRaceTooltips[self]
                    UpdateRaceTooltip(self, not isDetailed)
                end
            end)
		elseif not hiddenRace then
            button.enable = false;
            SetButtonDesaturated(button, 1);
            button.name = select(i, ...)
            button.tooltip = _G[strupper(select(i+1, ...).."_".."DISABLED")];
        end
        index = index + 1;
    end
    for i=CharacterCreate.numRaces + 1, MAX_RACES, 1 do
        _G["CharacterCreateRaceButton"..i]:Hide();
    end
    if hiddenSelection and CharacterCreate.raceIndicesAlliance[1] then
        SetSelectedRace(CharacterCreate.raceIndicesAlliance[1])
    end
    CharacterCreate_PositionRaceButtons()
end

function CharacterCreateEnumerateClasses(...)
    CharacterCreate.numClasses = select("#", ...)/3;
    if ( CharacterCreate.numClasses > MAX_CLASSES_PER_RACE ) then
        message("Too many classes!  Update MAX_CLASSES_PER_RACE");
        return;
    end
    local coords;
    local index = 1;
    local button;
    for i=1, select("#", ...), 3 do
        coords = CLASS_ICON_TCOORDS[strupper(select(i+1, ...))];
        _G["CharacterCreateClassButton"..index.."NormalTexture"]:SetTexCoord(coords[1], coords[2], coords[3], coords[4]);
        _G["CharacterCreateClassButton"..index.."PushedTexture"]:SetTexCoord(coords[1], coords[2], coords[3], coords[4]);
        button = _G["CharacterCreateClassButton"..index];

        if not button.staticTexture then
            button.staticTexture = button:CreateTexture(button:GetName().."StaticTexture", "ARTWORK");
            button.staticTexture:SetTexture("Interface\\Glues\\CharacterCreate\\IconBorder_F1");
            button.staticTexture:SetSize(112, 112);
            button.staticTexture:SetPoint("CENTER", 0, 0);
        end

        if not button.highlightTexture then
            button.highlightTexture = button:CreateTexture(button:GetName().."HighlightTexture", "HIGHLIGHT");
            button.highlightTexture:SetTexture("Interface\\Glues\\CharacterCreate\\IconBorder_F1");
            button.highlightTexture:SetAlpha(0.5);
            button.highlightTexture:SetBlendMode("ADD");
            button.highlightTexture:SetSize(112, 112);
            button.highlightTexture:SetPoint("CENTER", 0, 0);
        end

        if not button.checkedTexture then
            button.checkedTexture = button:CreateTexture(button:GetName().."CheckedTexture", "OVERLAY");
            button.checkedTexture:SetDrawLayer("OVERLAY", 7);
            button.checkedTexture:SetTexture("Interface\\Glues\\CharacterCreate\\IconBorderRace_H");
            button.checkedTexture:SetBlendMode("ADD");
            button.checkedTexture:SetSize(112, 112);
            button.checkedTexture:SetPoint("CENTER", 0, 0);
            button.checkedTexture:Hide();
        end

        if not button.nameFrame then
            button.nameFrame = CreateFrame("Frame", nil, button);
            button.nameFrame:SetSize(112, 40);
            button.nameFrame:SetPoint("TOP", button, "BOTTOM", 0, -5);

            button.nameFrame.text = button.nameFrame:CreateFontString(nil, "OVERLAY");
            button.nameFrame.text:SetFont("Fonts\\FRIZQT__.TTF", 10, "OUTLINE");
            button.nameFrame.text:SetPoint("CENTER", 0, 0);
            button.nameFrame.text:SetTextColor(1, 1, 1);
            button.nameFrame.text:SetJustifyH("CENTER");
            button.nameFrame.text:SetJustifyV("CENTER");
            button.nameFrame.text:SetWidth(112);
            button.nameFrame.text:SetWordWrap(true);
            button.nameFrame.text:SetHeight(40);
        end

        if not button.texturesMoved then
            button:SetScript("OnMouseDown", nil);
            button:SetScript("OnMouseUp", nil);

            button.texturesMoved = true;
        end

        button:Show();

        local className = select(i, ...);

        if className == "Caballero de la Muerte" then
            button.nameFrame.text:SetText("Caballero\nde la Muerte");
        elseif string.len(className) > 12 then
            local spacePos = string.find(className, " ", 6)
            if spacePos then
                local firstPart = string.sub(className, 1, spacePos - 1);
                local secondPart = string.sub(className, spacePos + 1);
                button.nameFrame.text:SetText(firstPart .. "\n" .. secondPart);
            else
                local midPoint = math.floor(string.len(className) / 2);
                local firstPart = string.sub(className, 1, midPoint);
                local secondPart = string.sub(className, midPoint + 1);
                button.nameFrame.text:SetText(firstPart .. "-\n" .. secondPart);
            end
        else
            button.nameFrame.text:SetText(className);
        end

        if ( (select(i+2, ...) == 1) and (IsRaceClassValid(CharacterCreate.selectedRace, index)) ) then
            button.enable = true;
            button:Enable();
            SetButtonDesaturated(button);
            button.name = select(i, ...)
            button.tooltip = select(i, ...);
            _G["CharacterCreateClassButton"..index.."DisableTexture"]:Hide();

            button.nameFrame.text:SetTextColor(1, 1, 1);

            button:SetScript("OnEnter", function(self)
                if self:IsEnabled() then
                    local tooltip = GetOrCreateClassTooltip(self)
                    tooltip:Show()
                    UpdateClassTooltip(self, false)
                end
            end)

            button:SetScript("OnLeave", function(self)
                if self:IsEnabled() then
                    local tooltip = GetOrCreateClassTooltip(self)
                    tooltip:Hide()
                end
            end)

            button:SetScript("OnMouseDown", function(self, clickedButton)
                if self:IsEnabled() and clickedButton == "RightButton" then
                    local tooltip = GetOrCreateClassTooltip(self)
                    local isDetailed = detailedClassTooltips[self]
                    UpdateClassTooltip(self, not isDetailed)
                end
            end)
        else
            button.enable = false;
            button:Disable();
            SetButtonDesaturated(button, 1);
            button.name = select(i, ...)
            button.tooltip = _G[strupper(select(i+1, ...).."_".."DISABLED")];
            _G["CharacterCreateClassButton"..index.."DisableTexture"]:Show();

            button.nameFrame.text:SetTextColor(0.5, 0.5, 0.5);

            button:SetScript("OnEnter", function(self)
                local tooltip = GetOrCreateClassTooltip(self)
                tooltip:Show()
                UpdateClassTooltip(self, false)
            end)

            button:SetScript("OnLeave", function(self)
                local tooltip = GetOrCreateClassTooltip(self)
                tooltip:Hide()
            end)
        end

        index = index + 1;
    end

    for i=CharacterCreate.numClasses + 1, MAX_CLASSES_PER_RACE, 1 do
        _G["CharacterCreateClassButton"..i]:Hide();
    end
end

function CharacterCreate_CreateGenderButtonTextures()
    local maleButton = CharacterCreateGenderButtonMale;
    if maleButton and not maleButton.highlightTexture then
        maleButton.staticTexture = maleButton:CreateTexture(maleButton:GetName().."StaticTexture", "ARTWORK");
        maleButton.staticTexture:SetTexture("Interface\\Glues\\CharacterCreate\\IconBorder_F1");
        maleButton.staticTexture:SetSize(86, 86);
        maleButton.staticTexture:SetPoint("CENTER", 0, 0);

        maleButton.highlightTexture = maleButton:CreateTexture(maleButton:GetName().."HighlightTexture", "HIGHLIGHT");
        maleButton.highlightTexture:SetTexture("Interface\\Glues\\CharacterCreate\\IconBorder_F1");
        maleButton.highlightTexture:SetAlpha(0.5);
        maleButton.highlightTexture:SetBlendMode("ADD");
        maleButton.highlightTexture:SetSize(86, 86);
        maleButton.highlightTexture:SetPoint("CENTER", 0, 0);

        maleButton.checkedTexture = maleButton:CreateTexture(maleButton:GetName().."CheckedTexture", "OVERLAY");
        maleButton.checkedTexture:SetDrawLayer("OVERLAY", 7);
        maleButton.checkedTexture:SetTexture("Interface\\Glues\\CharacterCreate\\IconBorderRace_H");
        maleButton.checkedTexture:SetBlendMode("ADD");
        maleButton.checkedTexture:SetSize(86, 86);
        maleButton.checkedTexture:SetPoint("CENTER", 0, 0);
        maleButton.checkedTexture:Hide();

        maleButton:SetScript("OnMouseDown", nil);
        maleButton:SetScript("OnMouseUp", nil);
    end

    local femaleButton = CharacterCreateGenderButtonFemale;
    if femaleButton and not femaleButton.highlightTexture then
        femaleButton.staticTexture = femaleButton:CreateTexture(femaleButton:GetName().."StaticTexture", "ARTWORK");
        femaleButton.staticTexture:SetTexture("Interface\\Glues\\CharacterCreate\\IconBorder_F1");
        femaleButton.staticTexture:SetSize(86, 86);
        femaleButton.staticTexture:SetPoint("CENTER", 0, 0);

        femaleButton.highlightTexture = femaleButton:CreateTexture(femaleButton:GetName().."HighlightTexture", "HIGHLIGHT");
        femaleButton.highlightTexture:SetTexture("Interface\\Glues\\CharacterCreate\\IconBorder_F1");
        femaleButton.highlightTexture:SetAlpha(0.5);
        femaleButton.highlightTexture:SetBlendMode("ADD");
        femaleButton.highlightTexture:SetSize(86, 86);
        femaleButton.highlightTexture:SetPoint("CENTER", 0, 0);

        femaleButton.checkedTexture = femaleButton:CreateTexture(femaleButton:GetName().."CheckedTexture", "OVERLAY");
        femaleButton.checkedTexture:SetDrawLayer("OVERLAY", 7);
        femaleButton.checkedTexture:SetTexture("Interface\\Glues\\CharacterCreate\\IconBorderRace_H");
        femaleButton.checkedTexture:SetBlendMode("ADD");
        femaleButton.checkedTexture:SetSize(86, 86);
        femaleButton.checkedTexture:SetPoint("CENTER", 0, 0);
        femaleButton.checkedTexture:Hide();

        femaleButton:SetScript("OnMouseDown", nil);
        femaleButton:SetScript("OnMouseUp", nil);
    end
end

function SetCharacterRace(id)
    CharacterCreate.selectedRace = id;
    local selectedButton;
    for i=1, CharacterCreate.numRaces, 1 do
        local button = _G["CharacterCreateRaceButton"..i];
        if ( i == id ) then
            if button.nameFrame and button.nameFrame.text then
                button.nameFrame.text:SetText(button.name);
            end
            button:SetChecked(1);
            selectedButton = button;
        else
            if button.nameFrame and button.nameFrame.text then
                button.nameFrame.text:SetText("");
            end
            button:SetChecked(0);
        end
    end

    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;
    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;
    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;
    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;
    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;
    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;
    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;
    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;
    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;
    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;
    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;
    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;
    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;
    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;
    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;
    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;
    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;
    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;
    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;
    CharacterCreate_UpdateButtonCheckedStates();

    local name, faction = GetFactionForRace(CharacterCreate.selectedRace);
    if ( _G.GetFactionForRaceID ) then
        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);
    end
    if ( _G.GetFactionForRaceID ) then
        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);
    end
    if ( _G.GetFactionForRaceID ) then
        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);
    end
    if ( _G.GetFactionForRaceID ) then
        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);
    end
    if ( _G.GetFactionForRaceID ) then
        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);
    end
    if ( _G.GetFactionForRaceID ) then
        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);
    end
    if ( _G.GetFactionForRaceID ) then
        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);
    end
    if ( _G.GetFactionForRaceID ) then
        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);
    end
    if ( _G.GetFactionForRaceID ) then
        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);
    end
    if ( _G.GetFactionForRaceID ) then
        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);
    end
    if ( _G.GetFactionForRaceID ) then
        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);
    end
    if ( _G.GetFactionForRaceID ) then
        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);
    end
    if ( _G.GetFactionForRaceID ) then
        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);
    end
    if ( _G.GetFactionForRaceID ) then
        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);
    end
    if ( _G.GetFactionForRaceID ) then
        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);
    end
    if ( _G.GetFactionForRaceID ) then
        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);
    end
    if ( _G.GetFactionForRaceID ) then
        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);
    end
    if ( _G.GetFactionForRaceID ) then
        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);
    end
    if ( _G.GetFactionForRaceID ) then
        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);
    end

    local race, fileString = GetNameForRace();

    CharacterCreateRaceLabel:SetText(race);
    fileString = strupper(fileString);
    if ( GetSelectedSex() == SEX_MALE ) then
        gender = "MALE";
    else
        gender = "FEMALE";
    end
    local raceKey = GetRaceIconTextureKey(fileString, gender, faction);
    local targetTexture = RACE_ICON_TEXTURES[raceKey];
    if targetTexture then
        CharacterCreateRaceIcon:SetTexture(targetTexture);
        CharacterCreateRaceIcon:SetTexCoord(0, 1, 0, 1);
    else
        local coords = RACE_ICON_TCOORDS[raceKey] or RACE_ICON_TCOORDS["HUMAN_"..(gender or "MALE")];
        CharacterCreateRaceIcon:SetTexture("Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-RacesRound");
        CharacterCreateRaceIcon:SetTexCoord(coords[1], coords[2], coords[3], coords[4]);
    end
    local raceText = _G["RACE_INFO_"..fileString];
    local abilityIndex = 1;
    local tempText = _G["ABILITY_INFO_"..fileString..abilityIndex];
    abilityText = "";
    while ( tempText ) do
        abilityText = abilityText..tempText.."\n\n";
        abilityIndex = abilityIndex + 1;
        tempText = _G["ABILITY_INFO_"..fileString..abilityIndex];
    end

    CharacterCreateRaceScrollFrameScrollBar:SetValue(0);
    CharacterCreateRaceText:SetText((GetFlavorText("RACE_INFO_"..strupper(fileString), GetSelectedSex()) or "").."|n|n");
    if ( abilityText and abilityText ~= "" ) then
        CharacterCreateRaceAbilityText:SetText(abilityText);
    else
        CharacterCreateRaceAbilityText:SetText("");
    end

    local backdropColor = FACTION_BACKDROP_COLOR_TABLE[faction] or FACTION_BACKDROP_COLOR_TABLE["Horde"] or FACTION_BACKDROP_COLOR_TABLE["Alliance"];
    local frame;
    for index, value in pairs(FRAMES_TO_BACKDROP_COLOR) do
        frame = _G[value];
        frame:SetBackdropColor(backdropColor[4], backdropColor[5], backdropColor[6]);
    end
    CharacterCreateConfigurationBackground:SetVertexColor(backdropColor[4], backdropColor[5], backdropColor[6]);

    local backgroundFilename = GetCreateBackgroundModel();
    local selectedRaceButton = _G["CharacterCreateRaceButton"..(CharacterCreate.selectedRace or 0)];
    local selectedRaceKey = selectedRaceButton and selectedRaceButton.raceFileString;
    local RACE_BACKGROUND_KEYS = {
        ["BROKEN"] = "ORC",
        ["BROKEN_ALLIANCE"] = "HUMAN",
        ["BROKEN_HORDE"] = "ORC",
        ["PANDAREN"] = "HUMAN",
        ["PANDAREN_ALLIANCE"] = "HUMAN",
        ["PANDAREN_HORDE"] = "ORC",
        ["VULPERA"] = "ORC",
        ["SETHRAK"] = "ORC",
        ["HIGHELF"] = "HUMAN",
        ["MAGHAR"] = "ORC",
        ["HARANIR"] = "NIGHTELF",
        ["HARANIRHORDE"] = "NIGHTELF",
        ["EARTHEN"] = "DWARF",
        ["EARTHENHORDE"] = "DWARF",
        ["HIGHMOUNTAINTAUREN"] = "TAUREN",
        ["MECHAGNOME"] = "GNOME",
        ["SKYBORNE"] = "HUMAN",
        ["SKYBORNEHORDE"] = "ORC",
        ["DARKFALLEN"] = "HUMAN",
        ["DARKFALLEN_ALLIANCE"] = "HUMAN",
        ["DARKFALLEN_HORDE"] = "ORC",
        ["DARKFALLENHORDE"] = "ORC",
        ["EREDAR"] = "ORC",
        ["NIGHTBORNE"] = "ORC",
        ["ZANDALARITROLL"] = "ORC",
        ["DRACTHYR"] = "ORC",
        ["ILLIDARI"] = "ORC",
        ["VOIDELF"] = "HUMAN",
        ["LIGHTFORGEDDRAENEI"] = "HUMAN",
        ["DARKIRONDWARF"] = "HUMAN",
        ["KULTIRAN"] = "HUMAN",
    };
    local mappedBackground = selectedRaceKey and RACE_BACKGROUND_KEYS[strupper(selectedRaceKey)];
    if ( mappedBackground ) then
        backgroundFilename = mappedBackground;
    end
    if ( not backgroundFilename or backgroundFilename == "" ) then
        if ( faction == "Alliance" ) then
            backgroundFilename = "HUMAN";
        else
            backgroundFilename = "ORC";
        end
    end
    SetBackgroundModel(CharacterCreate, backgroundFilename);
end

function SetCharacterClass(id)
    CharacterCreate.selectedClass = id;
    for i=1, CharacterCreate.numClasses, 1 do
        local button = _G["CharacterCreateClassButton"..i];
        if ( i == id ) then
            CharacterCreateClassName:SetText(button.name);
            button:SetChecked(1);
        else
            button:SetChecked(0);
        end
    end

    CharacterCreate_UpdateButtonCheckedStates();

    local className, classFileName, _, tank, healer, damage = GetSelectedClass();
    local abilityIndex = 0;
    local tempText = _G["CLASS_INFO_"..classFileName..abilityIndex];
    abilityText = "";
    while ( tempText ) do
        abilityText = abilityText..tempText.."\n\n";
        abilityIndex = abilityIndex + 1;
        tempText = _G["CLASS_INFO_"..classFileName..abilityIndex];
    end
    local coords = CLASS_ICON_TCOORDS[classFileName];
    CharacterCreateClassIcon:SetTexCoord(coords[1], coords[2], coords[3], coords[4]);
    CharacterCreateClassLabel:SetText(className);
    CharacterCreateClassRolesText:SetText(abilityText);
    CharacterCreateClassText:SetText(GetFlavorText("CLASS_"..strupper(classFileName), GetSelectedSex()).."|n|n");
    CharacterCreateClassScrollFrameScrollBar:SetValue(0);
end

function CharacterCreate_OnChar()
end

function CharacterCreate_UpdateButtonCheckedStates()
    for i=1, MAX_RACES, 1 do
        local button = _G["CharacterCreateRaceButton"..i];
        if button and button:IsShown() and button.checkedTexture then
            if button:GetChecked() then
                button.checkedTexture:Show();
            else
                button.checkedTexture:Hide();
            end
        end
    end

    for i=1, MAX_CLASSES_PER_RACE, 1 do
        local button = _G["CharacterCreateClassButton"..i];
        if button and button:IsShown() and button.checkedTexture then
            if button:GetChecked() then
                button.checkedTexture:Show();
            else
                button.checkedTexture:Hide();
            end
        end
    end

    local maleButton = CharacterCreateGenderButtonMale;
    local femaleButton = CharacterCreateGenderButtonFemale;

    if maleButton and maleButton.checkedTexture then
        if maleButton:GetChecked() then
            maleButton.checkedTexture:Show();
        else
            maleButton.checkedTexture:Hide();
        end
    end

    if femaleButton and femaleButton.checkedTexture then
        if femaleButton:GetChecked() then
            femaleButton.checkedTexture:Show();
        else
            femaleButton.checkedTexture:Hide();
        end
    end
end

function CharacterCreate_OnKeyDown(key)
    if ( key == "ESCAPE" ) then
        if (CharacterCreate.personalizationMode == true) then
            CharacterCreate_TogglePersonalization();
        else
            CharacterCreate_Back();
        end
    elseif ( key == "ENTER" ) then
        CharacterCreate_Okay();
    elseif ( key == "PRINTSCREEN" ) then
        Screenshot();
    end
end

function CharacterCreate_UpdateModel(self)
    UpdateCustomizationScene();
    self:AdvanceTime();
end

function CharacterCreate_Okay()
    if ( PAID_SERVICE_TYPE ) then
        GlueDialog_Show("CONFIRM_PAID_SERVICE");
    else
        CreateCharacter(CharacterCreate_GetFullName());
    end

    CharacterCreate.personalizationMode = false;
    PlaySound("gsCharacterCreationCreateChar");
end

function CharacterCreate_Back()
    if (CharacterCreate.personalizationMode == true) then
        CharacterCreate_TogglePersonalization();
        CharacterCreate.personalizationMode = false;
        return;
    end

    CharacterCreate.personalizationMode = false;
    PlaySound("gsCharacterCreationCancel");
    SetGlueScreen("charselect");
end

function CharacterClass_OnClick(id)
    PlaySound("gsCharacterCreationClass");
    local _,_,currClass = GetSelectedClass();
    if ( currClass ~= id and IsRaceClassValid(GetSelectedRace(), id) ) then
        SetSelectedClass(id);
        SetCharacterClass(id);
        SetCharacterRace(GetSelectedRace());
        CharacterChangeFixup();

        CharacterCreate_UpdateButtonCheckedStates();
    end
end

function CharacterRace_OnClick(self, id)
    PlaySound("gsCharacterCreationClass");
    if ( not self:GetChecked() ) then
        self:SetChecked(1);
        return;
    end
    if ( GetSelectedRace() ~= id ) then
        local target = _G["CharacterCreateRaceButton"..id];
        if target and target.raceID and target.raceID >= 55 and target.raceID <= 59 then
            SetSelectedSex(SEX_MALE);
        end
        SetSelectedRace(id);
        SetCharacterRace(id);
        SetSelectedSex(GetSelectedSex());
        SetCharacterCreateFacing(-15);
        CharacterCreateEnumerateClasses(GetAvailableClasses());
        local _,_,classIndex = GetSelectedClass();
        if ( PAID_SERVICE_TYPE ) then
            classIndex = PaidChange_GetCurrentClassIndex();
        end
        SetCharacterClass(classIndex);

        CharacterCreate_UpdateHairCustomization();

        CharacterChangeFixup();

        CharacterCreate_UpdateButtonCheckedStates();
    end
end

function SetCharacterGender(sex)
    if CharacterCreate.selectedRaceID and CharacterCreate.selectedRaceID >= 55 and CharacterCreate.selectedRaceID <= 59 then sex = SEX_MALE; end
    local gender;
    SetSelectedSex(sex);
    if ( sex == SEX_MALE ) then
        gender = "MALE";
        CharacterCreateGender:SetText(MALE);
        CharacterCreateGenderButtonMale:SetChecked(1);
        CharacterCreateGenderButtonFemale:SetChecked(nil);
    elseif ( sex == SEX_FEMALE ) then
        gender = "FEMALE";
        CharacterCreateGender:SetText(FEMALE);
        CharacterCreateGenderButtonMale:SetChecked(nil);
        CharacterCreateGenderButtonFemale:SetChecked(1);
    end

    CharacterCreateEnumerateRaces(GetAvailableRaces());
    CharacterCreateEnumerateClasses(GetAvailableClasses());
     SetCharacterRace(GetSelectedRace());

    local _,_,classIndex = GetSelectedClass();
    if ( PAID_SERVICE_TYPE ) then
        classIndex = PaidChange_GetCurrentClassIndex();
    end
    SetCharacterClass(classIndex);

    CharacterCreate_UpdateHairCustomization();

    local race, fileString = GetNameForRace();
    CharacterCreateRaceLabel:SetText(race);
    fileString = strupper(fileString);
    local _, faction = GetFactionForRace(CharacterCreate.selectedRace);
    local raceKey = GetRaceIconTextureKey(fileString, gender, faction);
    local targetTexture = RACE_ICON_TEXTURES[raceKey];
    if targetTexture then
        CharacterCreateRaceIcon:SetTexture(targetTexture);
        CharacterCreateRaceIcon:SetTexCoord(0, 1, 0, 1);
    else
        local coords = RACE_ICON_TCOORDS[raceKey] or RACE_ICON_TCOORDS["HUMAN_"..(gender or "MALE")];
        CharacterCreateRaceIcon:SetTexture("Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-RacesRound");
        CharacterCreateRaceIcon:SetTexCoord(coords[1], coords[2], coords[3], coords[4]);
    end

    CharacterChangeFixup();

    CharacterCreate_UpdateButtonCheckedStates();
end

function CharacterCreate_ResetState()
    CharacterCreate.personalizationMode = false;
    CharacterCreateRaceButtonsContainer:Show();
    CharacterCreateClassButtonsContainer:Show();
    CharacterCreateGenderButtonsContainer:Show();
    CustomizationLogoAlliance:Show();
    CustomizationTextAlliance:Show();
    CustomizationLogoHorde:Show();
    CustomizationTextHorde:Show();
    CharacterCreateRotateLeft:Hide();
    CharacterCreateRotateRight:Hide();
    CharCreateRandomizeButton:Hide();
    CharacterCreateNameEdit:Hide();
    CharacterCreateLastNameEdit:Hide();
    CharacterCreateRandomName:Hide();
    CharacterCreateRandomLastName:Hide();
    CharCreatePersonalizeButton:Show();
    CharCreateOkayButton:Hide();

    for i=1, NUM_CHAR_CUSTOMIZATIONS do
        _G["CharacterCustomizationButtonFrame"..i]:Hide();
    end
end

function CharacterCustomization_Left(id)
    PlaySound("gsCharacterCreationLook");
    CycleCharCustomization(id, -1);
end

function CharacterCustomization_Right(id)
    PlaySound("gsCharacterCreationLook");
    CycleCharCustomization(id, 1);
end

function CharacterCreate_Randomize()
    PlaySound("gsCharacterCreationLook");
    if CharacterCreate.selectedRaceID == 20 or CharacterCreate.selectedRaceID == 46 or CharacterCreate.selectedRaceID == 48 or CharacterCreate.selectedRaceID == 49 or CharacterCreate.selectedRaceID == 50 or CharacterCreate.selectedRaceID == 51 then CycleCharCustomization("EA_RANDOM",1);
    else RandomizeCharCustomization(); end
end

function CharacterCreateRotateRight_OnUpdate(self)
    if ( self:GetButtonState() == "PUSHED" ) then
        SetCharacterCreateFacing(GetCharacterCreateFacing() + CHARACTER_FACING_INCREMENT);
    end
end

function CharacterCreateRotateLeft_OnUpdate(self)
    if ( self:GetButtonState() == "PUSHED" ) then
        SetCharacterCreateFacing(GetCharacterCreateFacing() - CHARACTER_FACING_INCREMENT);
    end
end

function CharacterCreate_UpdateHairCustomization()
    CharacterCustomizationButtonFrame3Text:SetText(_G["HAIR_"..GetHairCustomization().."_STYLE"]);
    CharacterCustomizationButtonFrame4Text:SetText(_G["HAIR_"..GetHairCustomization().."_COLOR"]);
    CharacterCustomizationButtonFrame5Text:SetText(_G["FACIAL_HAIR_"..GetFacialHairCustomization()]);
    -- Skyborne legacy labels
    if CharacterCreate.selectedRaceID == 52 or CharacterCreate.selectedRaceID == 53 then
        CharacterCustomizationButtonFrame3Text:SetText("Hair Style");
        CharacterCustomizationButtonFrame4Text:SetText("Hair Color");
        CharacterCustomizationButtonFrame5Text:SetText("Features");
    end
end

function SetButtonDesaturated(button, desaturated, r, g, b)
    if ( not button ) then
        return;
    end
    local icon = button:GetNormalTexture();
    if ( not icon ) then
        return;
    end
    local shaderSupported = icon:SetDesaturated(desaturated);

    if ( not desaturated ) then
        r = 1.0;
        g = 1.0;
        b = 1.0;
    elseif ( not r or not shaderSupported ) then
        r = 0.5;
        g = 0.5;
        b = 0.5;
    end

    icon:SetVertexColor(r, g, b);
end

function GetFlavorText(tagname, sex)
    local primary, secondary;
    if ( sex == SEX_MALE ) then
        primary = "";
        secondary = "_FEMALE";
    else
        primary = "_FEMALE";
        secondary = "";
    end
    local text = _G[tagname..primary];
    if ( (text == nil) or (text == "") ) then
        text = _G[tagname..secondary];
    end
    return text;
end

function CharacterCreate_DeathKnightSwap(self)
    local _, classFilename = GetSelectedClass();
    if ( classFilename == "DEATHKNIGHT" ) then
        if (self.currentModel ~= "DEATHKNIGHT") then
            self.currentModel = "DEATHKNIGHT";
            self:SetNormalTexture("Interface\\Glues\\Common\\Glue-Panel-Button-Up-Blue");
            self:SetPushedTexture("Interface\\Glues\\Common\\Glue-Panel-Button-Down-Blue");
            self:SetHighlightTexture("Interface\\Glues\\Common\\Glue-Panel-Button-Highlight-Blue");
        end
    else
        if (self.currentModel == "DEATHKNIGHT") then
            self.currentModel = nil;
            self:SetNormalTexture("Interface\\Glues\\Common\\Glue-Panel-Button-Up");
            self:SetPushedTexture("Interface\\Glues\\Common\\Glue-Panel-Button-Down");
            self:SetHighlightTexture("Interface\\Glues\\Common\\Glue-Panel-Button-Highlight");
        end
    end
end

function CharacterChangeFixup()
    if ( PAID_SERVICE_TYPE ) then
        for i=1, MAX_CLASSES_PER_RACE, 1 do
            if (CharacterCreate.selectedClass ~= i) then
                local button = _G["CharacterCreateClassButton"..i];
                button:Disable();
                SetButtonDesaturated(button, true)
            end
        end

        for i=1, MAX_RACES, 1 do
            local allow = false;
            if ( PAID_SERVICE_TYPE == PAID_FACTION_CHANGE ) then
                local faction = GetFactionForRace(PaidChange_GetCurrentRaceIndex());
                if ( (i == PaidChange_GetCurrentRaceIndex()) or ((GetFactionForRace(i) ~= faction) and (IsRaceClassValid(i,CharacterCreate.selectedClass))) ) then
                    allow = true;
                end
            elseif ( PAID_SERVICE_TYPE == PAID_RACE_CHANGE ) then
                local faction = GetFactionForRace(PaidChange_GetCurrentRaceIndex());
                if ( (i == PaidChange_GetCurrentRaceIndex()) or ((GetFactionForRace(i) == faction) and (IsRaceClassValid(i,CharacterCreate.selectedClass))) ) then
                    allow = true
                end
            elseif ( PAID_SERVICE_TYPE == PAID_CHARACTER_CUSTOMIZATION ) then
                if ( i == CharacterCreate.selectedRace ) then
                    allow = true
                end
            end
            if (not allow) then
                local button = _G["CharacterCreateRaceButton"..i];
                button:Disable();
                SetButtonDesaturated(button, true)
            end
        end
    end
end

-- custom race names
if not _G["RACE_14"] then _G["RACE_14"] = "Broken" end
if not _G["RACE_15"] then _G["RACE_15"] = "Sethrak" end
if not _G["RACE_16"] then _G["RACE_16"] = "Eredar" end
if not _G["RACE_17"] then _G["RACE_17"] = "Nightborne" end
if not _G["RACE_18"] then _G["RACE_18"] = "Pandaren" end
if not _G["RACE_19"] then _G["RACE_19"] = "Void Elf" end
if not _G["RACE_20"] then _G["RACE_20"] = "Vulpera" end
if not _G["RACE_21"] then _G["RACE_21"] = "Lightforged Draenei" end
if not _G["RACE_22"] then _G["RACE_22"] = "Zandalari Troll" end
if not _G["RACE_23"] then _G["RACE_23"] = "Dark Iron Dwarf" end
if not _G["RACE_28"] then _G["RACE_28"] = "Dracthyr" end
if not _G["RACE_29"] then _G["RACE_29"] = "Kul Tiran" end
if not _G["RACE_30"] then _G["RACE_30"] = "Illidari" end
if not _G["RACE_31"] then _G["RACE_31"] = "Illidari" end


-- ============================================================
-- mod-classless-wildcard: single-class ("Hero") creation screen
-- Hides the leftover class-selection button. There is only one
-- class, so the picker is noise; the Hero name and description
-- stay. Selection state is untouched (SetCharacterClass still
-- runs via GetSelectedClass), so Accept works normally.
-- ============================================================
if not ClasslessWildcard_HideClass then
    ClasslessWildcard_HideClass = true;
    local _cw_orig_enumerate = CharacterCreateEnumerateClasses;
    function CharacterCreateEnumerateClasses(...)
        _cw_orig_enumerate(...);
        local maxc = MAX_CLASSES_PER_RACE or 10;
        for i = 1, maxc do
            local b = _G["CharacterCreateClassButton"..i];
            if b then b:Hide(); end
        end
    end
end

-- >>> freeborn-third-team (managed block, do not edit) >>>
-- ============================================================
-- Freeborn third player team: character-creation selection.
--
-- This block also paints the Freeborn emblem beside a Freeborn
-- character's name on the character-select screen.
--
-- The Freeborn choice is NOT carried by the create packet. The only
-- create field Lua can influence is the name, and a Freeborn name has
-- to follow exactly the same rules as an Alliance or Horde one, so the
-- name is sent untouched and the selection is recorded for the in-world
-- addon `Interface/AddOns/FreebornClaim`, which claims it once the
-- character exists. characters.teamId stays the only source of truth.
--
-- LOAD ORDER: the XML creates the CharacterCreate frame AFTER this
-- file has been executed, so nothing here may touch a frame at load
-- time. A top-level `CharacterCreate.selectedFreeborn = ...` is a nil
-- index, and because it aborts the whole chunk it also prevents every
-- function below from being defined -- leaving the button
-- unpositioned and untextured. Every frame access lives inside a
-- function; the selection state is created on first use.
--
-- GlueXML.toc loads CharacterSelect.xml before CharacterCreate.xml, so by
-- the time this block runs the select screen's globals already exist and
-- can be wrapped here without touching Interface/GlueXML/CharacterSelect.lua.
--
-- THREE RULES THIS SCREEN FORCES, all learned the hard way:
--
--   1. `GetCVar`/`SetCVar` raise "Couldn't find CVar named '<x>'" for any
--      name the client does not already know. Never call either outside
--      pcall -- an uncaught glue error here takes the create screen down
--      and can crash the client.
--   2. An argument is evaluated BEFORE pcall is entered, so
--      `pcall(f, builder())` does NOT protect the builder. Do the work
--      inside the pcall, or pcall the builder separately.
--   3. Only names the engine registers at the login screen are writable.
--      Being present in Config.wtf does not imply SetCVar accepts it, and
--      a cvar is free to store a value as 0/1 -- which is why the record
--      is judged live rather than assumed.
-- ============================================================
if not CharacterFreeborn_Init then
    CharacterFreeborn_Init = true;

    -- Cvar names this client accepts, used to carry the hash of the chosen name from here to the
    -- world. This only has to survive within one session -- the create screen and the login that
    -- claims it are the same client run -- so a cvar the client rewrites at startup is fine here.
    CharacterFreeborn_CarrierCVars = { "readTOS" };

    -- Where the emblem records live. This must survive a client restart, because the emblem is read
    -- on the character-select screen at the START of the next session, and every integer cvar tried
    -- was normalised when the client loaded it: readTOS and readEULA became "1", and gameTip had a
    -- record clipped to a valid tip index (the value was on disk, but not what the client loaded).
    -- So the store has to be a STRING cvar the client never parses. These two are voice-chat device
    -- names, and voice chat does not exist in 3.3.5, so arbitrary text there is inert. Because they
    -- are strings, one of them holds every Freeborn record at once.
    -- Dedicated restart-persistent badge slot. ECS deliberately does not use
    -- Sound_VoiceChatInputDriverName anymore; sharing it caused recursive
    -- fb:/ecsN: wrapping and eventual Config.wtf corruption.
    CharacterFreeborn_BadgeCVars = { "Sound_VoiceChatInputDriverName" };
    CharacterFreeborn_BadgeMarker = "fb:";

    -- The stock slot is 60x60. The Alliance/Horde crests sit inside their artwork, while the
    -- Freeborn plate fills its image edge to edge, so it reads larger at the same size. Draw it
    -- smaller inside the very same 60x60 box (centred on it) so the three match.
    CharacterFreeborn_BadgeSize = 44;

    -- A record is 1000000000 + (hash % 1000000000): always exactly ten digits, always below
    -- INT_MAX, and never confusable with a cvar's own resting value ("1", "76", "0"). This client
    -- rejects values of other shapes -- a "fb:"-prefixed string was silently refused -- so a plain
    -- number is the only shape proven to survive. Must match the addon's copy.
    CharacterFreeborn_RecordBase = 1000000000;
    CharacterFreeborn_RecordMod = 1000000000;

    CharacterFreeborn_BadgeTexture = "Interface\\Glues\\CharacterSelect\\FreebornLogo";

    function CharacterFreeborn_IsSelected()
        return CharacterCreate ~= nil and CharacterCreate.selectedFreeborn == true;
    end

    -- Every CVar access goes through these two. On this client an unknown name is a hard error.
    function CharacterFreeborn_SafeGet(name)
        local ok, value = pcall(GetCVar, name);
        if ( not ok ) then
            return nil;
        end
        return value;
    end

    function CharacterFreeborn_SafeSet(name, value)
        local ok = pcall(SetCVar, name, value);
        return ok and true or false;
    end

    -- Small non-cryptographic hash, so the choice can ride cvars the client parses as numbers.
    -- Must stay identical to the addon's copy.
    function CharacterFreeborn_NameHash(name)
        local hash = 0;
        local lowered = strlower(name or "");
        for i = 1, strlen(lowered) do
            hash = (hash * 31 + strbyte(lowered, i)) % 2147483647;
        end
        return hash;
    end

    function CharacterFreeborn_UpdateButton()
        local button = CharacterCreateFreebornButton;
        if ( not button ) then
            return;
        end

        if ( CharacterFreeborn_IsSelected() ) then
            button:SetChecked(1);
        else
            button:SetChecked(nil);
        end

        if ( button.checkedTexture ) then
            if ( CharacterFreeborn_IsSelected() ) then
                button.checkedTexture:Show();
            else
                button.checkedTexture:Hide();
            end
        end
    end

    function CharacterFreeborn_SetSelected(selected)
        if ( CharacterCreate == nil ) then
            return;
        end

        CharacterCreate.selectedFreeborn = selected and true or false;
        CharacterFreeborn_UpdateButton();
    end

    function CharacterFreeborn_OnClick(self)
        PlaySound("gsCharacterCreationClass");
        CharacterFreeborn_SetSelected(not CharacterFreeborn_IsSelected());
    end

    -- Hover tooltip for the Freeborn pick. It explains what the pick does, and it wears the same
    -- border as the race tooltips -- same background, same edge texture, same 16px tile and 4px
    -- insets -- so the two read as the same widget. The backdrop is spelled out here rather than
    -- borrowed from the stock `Backdrop2` local: this block is appended to the stock file, and an
    -- unresolved index on the create screen takes the whole screen down. The contract test pins
    -- these values against the stock race-tooltip backdrop so they cannot drift.
    function CharacterFreeborn_GetTooltip()
        local tooltip = CharacterFreebornTooltip;
        if ( tooltip ) then
            return tooltip;
        end

        tooltip = CreateFrame("Frame", "CharacterFreebornTooltip", CharacterCreateFrame);
        tooltip:SetFrameStrata("TOOLTIP");
        tooltip:SetBackdrop({
            bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
            edgeFile = "Interface\\Tooltips\\ui-tooltip-border-maw",
            tile = true, tileSize = 16, edgeSize = 16,
            insets = { left = 4, right = 4, top = 4, bottom = 4 } });
        tooltip:SetBackdropColor(0, 0, 0, 1);
        tooltip:SetWidth(300);

        tooltip.title = tooltip:CreateFontString(nil, "OVERLAY");
        tooltip.title:SetFont("Fonts\\FRIZQT__.TTF", 10, "OUTLINE");
        tooltip.title:SetPoint("TOPLEFT", tooltip, "TOPLEFT", 10, -10);
        tooltip.title:SetTextColor(1, 0.82, 0);
        tooltip.title:SetJustifyH("LEFT");
        tooltip.title:SetText("|cFFFFFFFFFreeborn|r");

        tooltip.body = tooltip:CreateFontString(nil, "OVERLAY");
        tooltip.body:SetFont("Fonts\\FRIZQT__.TTF", 10, "OUTLINE");
        tooltip.body:SetPoint("TOPLEFT", tooltip.title, "BOTTOMLEFT", 0, -6);
        tooltip.body:SetWidth(260);
        tooltip.body:SetWordWrap(true);
        tooltip.body:SetJustifyH("LEFT");
        tooltip.body:SetText("|cffffd100Freeborn are free of both the Alliance and the Horde. They swear no "
            .. "allegiance to either, though both have granted them access to their cities.\n\n"
            .. "They may take quests from either faction, and they can group and guild freely with "
            .. "other Freeborn. They can never group or guild with Alliance or Horde characters.\n\n"
            .. "Freeborn and the two factions are completely hostile to one another.|r");

        CharacterFreebornTooltip = tooltip;
        return tooltip;
    end

    -- The stock race tooltip sizes itself from its wrapped text, so this does the same: the body
    -- has to be laid out before its height means anything.
    function CharacterFreeborn_UpdateTooltipSize(tooltip)
        tooltip:SetHeight(tooltip.title:GetHeight() + tooltip.body:GetHeight() + 26);
    end

    function CharacterFreeborn_HideTooltip()
        if ( CharacterFreebornTooltip ) then
            CharacterFreebornTooltip:Hide();
        end
    end

    -- Sit the tooltip above the plate, clear of the button's own "Freeborn" label.
    function CharacterFreeborn_OnEnter(self)
        local tooltip = CharacterFreeborn_GetTooltip();
        CharacterFreeborn_UpdateTooltipSize(tooltip);
        tooltip:ClearAllPoints();
        tooltip:SetPoint("BOTTOM", self, "TOP", 0, 24);
        tooltip:Show();
    end

    function CharacterFreeborn_OnLeave(self)
        CharacterFreeborn_HideTooltip();
    end

    -- The Freeborn pick is a plain plate: no round border ring, unlike the gender picks. Only the
    -- checked ring is kept, and only while Freeborn is actually selected, as click feedback.
    local freeborn_originalGenderTextures = CharacterCreate_CreateGenderButtonTextures;
    function CharacterCreate_CreateGenderButtonTextures(...)
        freeborn_originalGenderTextures(...);

        local button = CharacterCreateFreebornButton;
        if ( button and not button.highlightTexture ) then
            button.staticTexture = button:CreateTexture(button:GetName().."StaticTexture", "ARTWORK");
            button.staticTexture:SetTexture("Interface\\Glues\\CharacterCreate\\IconBorder_F1");
            button.staticTexture:SetAlpha(0);
            button.staticTexture:SetSize(86, 86);
            button.staticTexture:SetPoint("CENTER", 0, 0);

            button.highlightTexture = button:CreateTexture(button:GetName().."HighlightTexture", "HIGHLIGHT");
            button.highlightTexture:SetTexture("Interface\\Glues\\CharacterCreate\\IconBorder_F1");
            button.highlightTexture:SetAlpha(0);
            button.highlightTexture:SetBlendMode("ADD");
            button.highlightTexture:SetSize(86, 86);
            button.highlightTexture:SetPoint("CENTER", 0, 0);

            button.checkedTexture = button:CreateTexture(button:GetName().."CheckedTexture", "OVERLAY");
            button.checkedTexture:SetDrawLayer("OVERLAY", 7);
            button.checkedTexture:SetTexture("Interface\\Glues\\CharacterCreate\\IconBorderRace_H");
            button.checkedTexture:SetBlendMode("ADD");
            button.checkedTexture:SetSize(86, 86);
            button.checkedTexture:SetPoint("CENTER", 0, 0);
            button.checkedTexture:Hide();

            button:SetScript("OnMouseDown", nil);
            button:SetScript("OnMouseUp", nil);
        end

        CharacterFreeborn_UpdateButton();
    end

    -- Sit the Freeborn pick between the two gender picks. It chooses a team,
    -- never a gender, so it never calls SetSelectedSex. The XML anchors it in the
    -- same place, so a wrapper that never ran would still leave it visible.
    local freeborn_originalPositionGenderButtons = CharacterCreate_PositionGenderButtons;
    function CharacterCreate_PositionGenderButtons(...)
        freeborn_originalPositionGenderButtons(...);

        local button = CharacterCreateFreebornButton;
        if ( button ) then
            button:ClearAllPoints();
            button:SetPoint("CENTER", CharacterCreateFrame, "CENTER", 0, -250);
            if ( PAID_SERVICE_TYPE ) then
                CharacterFreeborn_HideTooltip();
                button:Hide();
            else
                button:Show();
            end
        end
    end

    -- Race/gender clicks re-run this, so an explicit Freeborn selection is kept
    -- across race and gender changes until the player deselects it.
    local freeborn_originalUpdateButtonCheckedStates = CharacterCreate_UpdateButtonCheckedStates;
    function CharacterCreate_UpdateButtonCheckedStates(...)
        freeborn_originalUpdateButtonCheckedStates(...);
        CharacterFreeborn_UpdateButton();
    end

    -- A fresh visit to the create screen starts on the race's native team.
    local freeborn_originalOnShow = CharacterCreate_OnShow;
    function CharacterCreate_OnShow(...)
        CharacterFreeborn_SetSelected(false);
        CharacterFreeborn_HideTooltip();
        freeborn_originalOnShow(...);
        CharacterFreeborn_UpdateButton();
    end

    -- Record the choice for the addon, then run the stock accept path so the name reaches the
    -- server exactly as typed. Nothing here may raise. The record is written ONLY when Freeborn
    -- was chosen: an intervening native creation must not wipe an unclaimed choice, and a stale
    -- record cannot claim a later character because the addon also matches the name's hash.
    local freeborn_originalOkay = CharacterCreate_Okay;
    function CharacterCreate_Okay(...)
        local pending = "";
        if ( CharacterFreeborn_IsSelected() and not PAID_SERVICE_TYPE ) then
            if ( CharacterCreate_GetFullName ) then
                pending = CharacterCreate_GetFullName();
            else
                pending = CharacterCreateNameEdit:GetText();
            end
        end

        if ( pending ~= "" ) then
            local record = CharacterFreeborn_RecordFor(pending);
            for _, name in ipairs(CharacterFreeborn_CarrierCVars) do
                CharacterFreeborn_SafeSet(name, tostring(record));
            end
            -- Record the emblem here as well as from the addon on claiming. This screen can write
            -- cvars the world state refuses (readEULA is refused there), so the badge does not
            -- depend on that, and a record always claims a name, never a character that is not it.
            CharacterFreeborn_StoreBadge(record);
        end

        return freeborn_originalOkay(...);
    end

    -- The value the addon parks for a character, and the value this screen looks for.
    function CharacterFreeborn_RecordFor(name)
        return CharacterFreeborn_RecordBase + CharacterFreeborn_NameHash(name) % CharacterFreeborn_RecordMod;
    end

    -- The record format is "fb:<record>,<record>,...|<whatever the cvar held before>", so the
    -- client's own value is preserved behind the bar and all Freeborn records share one cvar.

    -- The hashes of every character the addon has claimed as Freeborn.
    function CharacterFreeborn_BadgeHashes()
        local hashes = {};
        local mark = strlen(CharacterFreeborn_BadgeMarker);

        for _, cvar in ipairs(CharacterFreeborn_BadgeCVars) do
            local stored = CharacterFreeborn_SafeGet(cvar);
            if ( type(stored) == "string" and strsub(stored, 1, mark) == CharacterFreeborn_BadgeMarker ) then
                local body = strsub(stored, mark + 1);
                local bar = strfind(body, "|", 1, true);
                if ( bar ) then
                    body = strsub(body, 1, bar - 1);
                end
                for digits in string.gmatch(body, "%d+") do
                    hashes[digits] = true;
                end
            end
        end

        return hashes;
    end

    -- Add this character's record to the first cvar that will take it, keeping whatever that cvar
    -- already held. Returns the cvar, or nil when no cvar would accept the write.
    function CharacterFreeborn_StoreBadge(record)
        local wanted = tostring(record - CharacterFreeborn_RecordBase);
        local mark = strlen(CharacterFreeborn_BadgeMarker);

        for _, cvar in ipairs(CharacterFreeborn_BadgeCVars) do
            local stored = CharacterFreeborn_SafeGet(cvar);
            if ( type(stored) ~= "string" ) then
                stored = "";
            end

            local original = stored;
            local body = "";
            if ( strsub(stored, 1, mark) == CharacterFreeborn_BadgeMarker ) then
                body = strsub(stored, mark + 1);
                local bar = strfind(body, "|", 1, true);
                if ( bar ) then
                    original = strsub(body, bar + 1);
                    body = strsub(body, 1, bar - 1);
                else
                    original = "";
                end
            end

            local list = {};
            for digits in string.gmatch(body, "%d+") do
                if ( digits == wanted ) then
                    return cvar;
                end
                list[#list + 1] = digits;
            end
            list[#list + 1] = wanted;

            CharacterFreeborn_SafeSet(cvar,
                CharacterFreeborn_BadgeMarker .. table.concat(list, ",") .. "|" .. original);

            local check = CharacterFreeborn_SafeGet(cvar);
            if ( type(check) == "string" and strsub(check, 1, mark) == CharacterFreeborn_BadgeMarker
                and strfind(check, wanted, 1, true) ) then
                return cvar;
            end
        end

        return nil;
    end

    -- Paint the Freeborn emblem over the Alliance/Horde logo for those characters. The stock list
    -- creates one FactionIcon texture per visible button and tags its button with the character's
    -- index, so the match is name-hash against the badge record.
    function CharacterFreeborn_ApplyBadges()
        if ( CharacterSelect == nil ) then
            return;
        end

        local hashes = CharacterFreeborn_BadgeHashes();
        if ( not next(hashes) ) then
            return;
        end

        for index = 1, ( MAX_CHARACTERS_DISPLAYED or 8 ) do
            local button = _G["CharSelectCharacterButton"..index];
            local icon = _G["CharSelectCharacterButton"..index.."FactionIcon"];
            if ( button and icon ) then
                local id = button:GetID() or 0;
                local name = nil;
                if ( id > 0 ) then
                    local ok, value = pcall(GetCharacterInfo, id);
                    if ( ok and type(value) == "string" ) then
                        name = value;
                    end
                end

                if ( name and hashes[tostring(CharacterFreeborn_RecordFor(name) - CharacterFreeborn_RecordBase)] ) then
                    -- The stock slot is anchored TOPLEFT (170,-5) at 60x60; keep the same centre.
                    icon:ClearAllPoints();
                    icon:SetPoint("CENTER", button, "TOPLEFT", 200, -35);
                    icon:SetSize(CharacterFreeborn_BadgeSize, CharacterFreeborn_BadgeSize);
                    icon:SetTexture(CharacterFreeborn_BadgeTexture);
                    icon:Show();
                end
            end
        end
    end

    local freeborn_originalUpdateCharacterList = UpdateCharacterList;
    function UpdateCharacterList(...)
        freeborn_originalUpdateCharacterList(...);
        pcall(CharacterFreeborn_ApplyBadges);
    end

    local freeborn_originalSelectOnEvent = CharacterSelect_OnEvent;
    function CharacterSelect_OnEvent(self, event, ...)
        freeborn_originalSelectOnEvent(self, event, ...);
        pcall(CharacterFreeborn_ApplyBadges);
    end
end
-- <<< freeborn-third-team (managed block) <<<

-- Esteria native appearance controls: logical options use the permanent executable callback.
local EA_LABELS = {"Skin Color", "Face", "Hair Style", "Hair Color", "Eye Color", "Eyebrow Style",
    "Feathers", "Feather Color", "Facial Hair", "Ears"};
local EA_MECH_LABELS = {"Skin Color","Face","Hair Style","Hair Color","Facial Hair","Arm Upgrade","Leg Upgrade","Modification","Eye Color","Paint","Eyesight","Eye Style"};
local EA_LEFT = CharacterCustomization_Left;
local EA_RIGHT = CharacterCustomization_Right;
local EA_UPDATE = CharacterCreate_UpdateHairCustomization;
local function EA_ACTIVE()
    return CharacterCreate.selectedRaceID == 20 or CharacterCreate.selectedRaceID == 50 or CharacterCreate.selectedRaceID == 51 or CharacterCreate.selectedRaceID == 48 or CharacterCreate.selectedRaceID == 49 or CharacterCreate.selectedRaceID == 46 or CharacterCreate.selectedRaceID == 47 or CharacterCreate.selectedRaceID == 52 or CharacterCreate.selectedRaceID == 53;
end
local function EA_REFRESH()
    if not CharacterCustomizationButtonFrame1 then return; end
    local parent = CharacterCustomizationButtonFrame1:GetParent();
    for i=6,29 do
        if not _G["CharacterCustomizationButtonFrame"..i] then
            local frame = CreateFrame("Frame", "CharacterCustomizationButtonFrame"..i,
                parent, "CharacterCustomizationFrameTemplate");
            frame:SetID(i);
        end
    end
    if EA_ACTIVE() then
        -- Esteria split customization columns: balance only selectable options.
        local optionCount=0;
        for i=1,29 do
            local _,count = CycleCharCustomization("EA_GET",i);
            if count and count>1 then optionCount=optionCount+1; end
        end
        local rowsPerColumn=math.max(1,math.ceil(optionCount/2));
        local rowSpacing=optionCount>22 and 28 or 36;
        local visibleRow=0;
        for i=1,29 do
            local frame = _G["CharacterCustomizationButtonFrame"..i];
            frame:ClearAllPoints();
            local value,count,label = CycleCharCustomization("EA_GET",i);
            local side=visibleRow>=rowsPerColumn and "TOPRIGHT" or "TOPLEFT";
            frame:SetPoint(side, CharacterCreateFrame, side, side=="TOPRIGHT" and -55 or 55,
                -110-(visibleRow%rowsPerColumn)*rowSpacing);
            local earthenChoiceText = nil;
            if (CharacterCreate.selectedRaceID == 48 or CharacterCreate.selectedRaceID == 49) and label == "Belt" then
                earthenChoiceText = value == 0 and "  None" or "  Gem";
            end
            _G["CharacterCustomizationButtonFrame"..i.."Text"]:SetText(
                ((CharacterCreate.selectedRaceID == 20 or CharacterCreate.selectedRaceID == 46 or CharacterCreate.selectedRaceID == 48 or CharacterCreate.selectedRaceID == 49 or CharacterCreate.selectedRaceID == 50 or CharacterCreate.selectedRaceID == 51) and (label or "") or CharacterCreate.selectedRaceID == 47 and EA_MECH_LABELS[i] or EA_LABELS[i] or "")..(earthenChoiceText or (count and "  "..(value+1).."/"..count or "")));
            if count and count>1 then
                visibleRow=visibleRow+1;
                if CharacterCustomizationButtonFrame1:IsShown() then frame:Show(); else frame:Hide(); end
            else frame:Hide(); end
        end
    else
        CharacterCustomizationButtonFrame1Text:SetText(CHAR_CUSTOMIZATION1_DESC);
        CharacterCustomizationButtonFrame2Text:SetText(CHAR_CUSTOMIZATION2_DESC);
        for i=6,29 do _G["CharacterCustomizationButtonFrame"..i]:Hide(); end
        for i=1,5 do
            local frame = _G["CharacterCustomizationButtonFrame"..i];
            frame:ClearAllPoints();
            frame:SetPoint("CENTER", parent, "CENTER", 900, 200-i*50);
        end
    end
end
function CharacterCustomization_Left(id)
    if EA_ACTIVE() then CycleCharCustomization("EA_CYCLE",id,-1); EA_REFRESH();
    else EA_LEFT(id); end
end
function CharacterCustomization_Right(id)
    if EA_ACTIVE() then CycleCharCustomization("EA_CYCLE",id,1); EA_REFRESH();
    else EA_RIGHT(id); end
end
function CharacterCreate_UpdateHairCustomization()
    EA_UPDATE(); EA_REFRESH();
end
local eaFrame = CreateFrame("Frame");
eaFrame:SetScript("OnUpdate",function(self,elapsed)
    self.elapsed=(self.elapsed or 0)+elapsed;
    if self.elapsed>.15 then self.elapsed=0; EA_REFRESH(); end
end);
-- Esteria customization dropdown: reuse the native selectors and Glue widgets.
local picker;

local function PickerState(id)
    if EA_ACTIVE() then
        return CycleCharCustomization("EA_GET", id);
    end
    return CycleCharCustomization("EA_STOCK_GET", id);
end

local VULPERA_CHOICE_NAMES = {
    [1] = {
        [1] = {"","","","","",""},
        [2] = {"","","","","","","",""},
        [3] = {""},
        [4] = {"Wanderer","Compact","Sharp","Rakish","Scruffy","Raised"},
        [5] = {"Long","Blunt","Flat","Short","Strong","Sharp"},
        [6] = {"","","","","","","","","","","","","","","Death Knight","","","","","","","","","","","","","","","Primalist - Earth","Primalist - Fire","Primalist - Air","Primalist - Water"},
        [7] = {"Unpierced","Pierced"},
        [8] = {"Desert","Forest","Plains"},
        [9] = {"Both","Right","Left","Neither"},
        [10] = {"Slit","Star","Glow"},
    },
    [2] = {
        [1] = {"","","","","",""},
        [2] = {"","","","","","","",""},
        [3] = {""},
        [4] = {"Desert","Sharp","Vigilant","Relaxed","Curled","Scruffy","Scarred","Calm"},
        [5] = {"Desert","Forest","Plains"},
        [6] = {"Long","Flat","Blunt","Round","Sharp","Short"},
        [7] = {"","","","","","","","","","","","","","","Death Knight","","","","","","","","","","","","","","","Primalist - Earth","Primalist - Fire","Primalist - Air","Primalist - Water"},
        [8] = {"Unpierced","Pierced"},
        [9] = {"Both","Right","Left","Neither"},
        [10] = {"Slit","Star","Glow"},
    },
};
local function ChoiceText(id, value, label)
    if CharacterCreate.selectedRaceID == 20 then
        local names = VULPERA_CHOICE_NAMES[GetSelectedSex()];
        local name = names and names[id] and names[id][value + 1];
        if name and name ~= "" then return name; end
    end
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

-- Only Naga has an authored second playable body type in this NPC port.
local creatureOriginalSetRace = SetCharacterRace;
function SetCharacterRace(id)
    creatureOriginalSetRace(id);
    local race = CharacterCreate.selectedRaceID;
    local maleOnly = race and race >= 55 and race <= 59;
    if maleOnly then
        CharacterCreateGenderButtonMale:Hide();
        CharacterCreateGenderButtonFemale:Hide();
        if GetSelectedSex() ~= SEX_MALE then SetCharacterGender(SEX_MALE); end
    else
        CharacterCreateGenderButtonMale:Show();
        CharacterCreateGenderButtonFemale:Show();
    end
end

-- Esteria Vrykul preview sizing.
local creaturePreviewUpdate = CharacterCreate_UpdateModel;
function CharacterCreate_UpdateModel(self)
    creaturePreviewUpdate(self);
    local index = 0;
    if index == 0 and type(CycleCharCustomization) == "function" then
        CycleCharCustomization("EA_PREVIEW_SCALE", index);
    end
end
