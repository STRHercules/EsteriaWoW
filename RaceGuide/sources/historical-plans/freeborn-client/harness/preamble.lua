-- ---------------------------------------------------------------
-- WoW client stubs for running the DEPLOYED Freeborn glue block
-- offline. MODE selects which CVar environment the glue screen has:
--
--   custom-ok       the client accepts any cvar name (the bridge can work)
--   registered-only the client only accepts cvars it already knows
--   no-cvar         the glue state has no CVar API at all
-- ---------------------------------------------------------------

CVARS = {};
REGISTERED = {
    readTOS = "1", readEULA = "1", taintLog = "1", checkAddonVersion = "0",
    showGameTips = "0", screenshotQuality = "10", gameTip = "76",
    hwDetect = "0", lastCharacterIndex = "26",
    -- String cvars the client never parses: where the emblem records live.
    Sound_VoiceChatInputDriverName = "System Default",
    Sound_VoiceChatOutputDriverName = "System Default",
};
for name, value in pairs(REGISTERED) do
    CVARS[name] = value;
end

-- Cvars whose consumers only care about zero/non-zero: a client is free to store any write to them
-- as 0/1, which is exactly what would lose a record. registered-numeric models that.
local BOOL_CVARS = { readTOS = true, readEULA = true, taintLog = true, checkAddonVersion = true };

-- Cvars the client parses as numbers refuse a value of the wrong shape outright. This is what
-- silently killed a "fb:"-prefixed badge record in the field, so the harness models it.
local NUMERIC_CVARS = { readTOS = true, readEULA = true, checkAddonVersion = true, gameTip = true,
    showGameTips = true, screenshotQuality = true, hwDetect = true, lastCharacterIndex = true };

-- Some cvars are writable from the glue screen but protected from script writes in the world. That
-- is the observed case for readEULA: an in-world claim could not move it, while readTOS moved fine.
local WORLD_PROTECTED = { readEULA = true };

local function IsKnown(name)
    return REGISTERED[name] ~= nil or CVARS[name] ~= nil;
end

-- This client raises "Couldn't find CVar named '<x>'" for names it does not already know --
-- observed live on the character-create screen. world-lenient models the world state, where the
-- same read returned nil instead.
function GetCVar(name)
    if MODE == "world-lenient" then
        return CVARS[name];
    end
    if not IsKnown(name) then
        error("Couldn't find CVar named '" .. tostring(name) .. "'", 0);
    end
    return CVARS[name];
end

function SetCVar(name, value, scriptCvar)
    if MODE == "custom-ok" then
        CVARS[name] = tostring(value);
        return true;
    end
    -- three-arg-ok models a client where the optional scriptCvar argument registers a new name.
    if MODE == "three-arg-ok" and scriptCvar ~= nil then
        CVARS[name] = tostring(value);
        return true;
    end
    if not IsKnown(name) then
        error("Couldn't find CVar named '" .. tostring(name) .. "'", 0);
    end
    if ( MODE:sub(1, 5) == "world" and WORLD_PROTECTED[name] ) then
        error("CVar '" .. tostring(name) .. "' is not settable from script here", 0);
    end
    if MODE ~= "custom-ok" and NUMERIC_CVARS[name] then
        if ( not tostring(value):match("^%d+$") or tonumber(value) > 2147483647 ) then
            error("Invalid value for CVar '" .. tostring(name) .. "'", 0);
        end
    end
    if MODE == "registered-numeric" and BOOL_CVARS[name] then
        CVARS[name] = (tostring(value) ~= "0" and tostring(value) ~= "") and "1" or "0";
        return true;
    end
    CVARS[name] = tostring(value);
    return true;
end

-- absent bindings must really be absent, exactly like the glue state
if MODE == "no-cvar" then
    GetCVar = nil;
    SetCVar = nil;
end

SendAddonMessage = function() end;
-- SendChatMessage deliberately left undefined: the report has to show the difference.

strlower = string.lower;
strupper = string.upper;
strfind = string.find;
strsub = string.sub;
strlen = string.len;
strbyte = string.byte;
PlaySound = function() end;
PAID_SERVICE_TYPE = nil;

local function NewTexture()
    local texture = {};
    function texture:SetTexture(a) self.texture = a; end
    function texture:SetAllPoints() end
    function texture:ClearAllPoints() end
    function texture:SetSize() end
    function texture:SetPoint() end
    function texture:SetDrawLayer() end
    function texture:SetBlendMode() end
    function texture:SetAlpha() end
    function texture:Show() self.shown = true; end
    function texture:Hide() self.shown = false; end
    return texture;
end

local function NewFontString()
    local text = NewTexture();
    function text:SetText(value) self.text = value; end
    function text:GetText() return self.text; end
    function text:SetJustifyH() end
    function text:SetJustifyV() end
    function text:SetFont() end
    function text:SetTextColor(r, g, b) self.color = { r, g, b }; end
    function text:SetWordWrap(wrap) self.wordWrap = wrap; end
    function text:SetWidth(width) self.width = width; end
    -- One line per 45 characters at the tooltip's 260px body width.
    function text:GetHeight()
        local length = self.text and string.len(self.text) or 0;
        return 11 * (math.floor(length / 45) + 1);
    end
    return text;
end

function CreateFrame(kind, name, parent)
    local frame = { name = name, parent = parent };
    function frame:SetPoint(point, anchor, anchorPoint, x, y) self.point = { point, x, y }; end
    function frame:ClearAllPoints() end
    function frame:SetWidth(width) self.width = width; end
    function frame:SetHeight(height) self.height = height; end
    function frame:SetSize(width, height) self.width, self.height = width, height; end
    function frame:Show() self.shown = true; end
    function frame:Hide() self.shown = false; end
    function frame:GetName() return self.name; end
    function frame:SetChecked(value) self.checked = value; end
    function frame:SetID(id) self.id = id; end
    function frame:GetID() return self.id; end
    function frame:SetBackdrop(backdrop) self.backdrop = backdrop; end
    function frame:SetBackdropColor(r, g, b, a) self.backdropColor = { r, g, b, a }; end
    function frame:SetBackdropBorderColor(r, g, b) self.borderColor = { r, g, b }; end
    function frame:SetFrameStrata(strata) self.strata = strata; end
    function frame:SetScript(kind, fn) self.scripts = self.scripts or {}; self.scripts[kind] = fn; end
    function frame:RegisterEvent(event) self.events = self.events or {}; self.events[event] = true; end
    function frame:CreateTexture(textureName)
        local texture = NewTexture();
        if textureName then _G[textureName] = texture; end
        return texture;
    end
    function frame:CreateFontString(fontStringName)
        local text = NewFontString();
        if fontStringName then _G[fontStringName] = text; end
        return text;
    end
    if name then _G[name] = frame; end
    LAST_FRAME = frame;
    return frame;
end

-- character create screen
CharacterCreateFrame = CreateFrame("Frame", "CharacterCreateFrame");
CharacterCreate = CreateFrame("Frame", "CharacterCreate");
CharacterCreate.selectedFreeborn = false;
CharacterCreateFreebornButton = CreateFrame("Frame", "CharacterCreateFreebornButton");

CharacterCreateNameEdit = {};
function CharacterCreateNameEdit:GetText() return TYPED_NAME or ""; end

STOCK = {};
function CharacterCreate_CreateGenderButtonTextures() STOCK.genderTextures = (STOCK.genderTextures or 0) + 1; end
function CharacterCreate_PositionGenderButtons() STOCK.positionGender = (STOCK.positionGender or 0) + 1; end
function CharacterCreate_UpdateButtonCheckedStates() STOCK.updateChecked = (STOCK.updateChecked or 0) + 1; end
function CharacterCreate_OnShow() STOCK.onShow = (STOCK.onShow or 0) + 1; end
function CharacterCreate_Okay() STOCK.okay = (STOCK.okay or 0) + 1; end

-- character select screen
CharacterSelect = CreateFrame("Frame", "CharacterSelect");
CharacterSelect.selectedIndex = 1;
CharacterSelect.scrollOffset = 0;
MAX_CHARACTERS_DISPLAYED = 8;

INFO_COUNT = tonumber(INFO_COUNT or "10");
CHARACTERS = { "Dobb", "Someone", "Loo" };

function GetCharacterInfo(index)
    local name = CHARACTERS[index];
    if ( not name ) then
        return nil;
    end
    local base = { name, 1, 1, 80, "Elwynn Forest", 0, 0, 1, 1, 1 };
    local out = {};
    for i = 1, INFO_COUNT do
        out[i] = (i <= 10) and base[i] or 0;
    end
    return table.unpack(out);
end

function GetFactionForRace(race) return "Alliance"; end
function GetSelectBackgroundModel(index) return "HUMAN"; end
function GetNumCharacters() return #CHARACTERS; end

-- fiction: a couple of team/faction globals, so a scan would have something to report
function GetCharacterTeamProbe() end
function SetPlayerFactionProbe() end

-- Models what the stock UpdateCharacterList does: one button per character, tagged with the
-- character index, each owning a FactionIcon texture that starts on the race's own logo.
function UpdateCharacterList()
    STOCK.updateList = (STOCK.updateList or 0) + 1;

    for index = 1, #CHARACTERS do
        local name = "CharSelectCharacterButton" .. index;
        local button = _G[name];
        if ( not button ) then
            button = CreateFrame("Frame", name, CharacterSelect);
        end
        button:SetID(index);

        local iconName = name .. "FactionIcon";
        local icon = _G[iconName];
        if ( not icon ) then
            icon = button:CreateTexture(iconName, "OVERLAY");
        end
        icon:SetTexture("Interface\\Glues\\CharacterSelect\\AllianceLogo");
    end
end
