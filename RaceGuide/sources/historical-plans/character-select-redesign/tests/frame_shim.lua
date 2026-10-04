--[==[ frame_shim.lua -------------------------------------------------------------
    A minimal WoW 3.3.5a frame API emulation for offline testing.

    This is NOT part of the shipped addon. It exists so ECS_Row / ECS_Roster can be
    exercised headlessly on real Lua 5.1, instead of only being verifiable by
    launching a 2008 client and eyeballing the result.

    It models the parts of the API the roster actually touches, and -- importantly
    -- it records calls so tests can assert on what the code DID (which texture,
    which point, which alpha) rather than only that it did not crash.

    Deliberately narrow: anything not needed by ECS is not implemented, and calling
    an unimplemented method raises rather than silently doing nothing, so a typo in
    the module surfaces as a test failure.

    Lua 5.1 only.
]==]

-- ---------------------------------------------------------------- registry
SHIM = {
    frames = {},          -- id -> frame table
    nextId = 0,
    created = 0,          -- how many frames have ever been created
    textures = 0,
    fonts = 0,
    globals = {},         -- names this shim registered into _G
};

local function NewRegion(kind, name, parent)
    SHIM.nextId = SHIM.nextId + 1;
    local region = {
        __kind = kind,
        __id = SHIM.nextId,
        __name = name,
        __parent = parent,
        __points = {},
        __shown = true,
        __alpha = 1,
        __texture = nil,
        __text = nil,
        __scripts = {},
        __width = 0,
        __height = 0,
        __events = {},
        __id_value = nil,
        __level = 0,
        __calls = {},
        __regions = {},
    };
    SHIM.frames[region.__id] = region;
    return region
end

local function Record(frame, method, ...)
    if ( not frame.__calls ) then frame.__calls = {} end
    local args = { ... }
    frame.__calls[#frame.__calls + 1] = { method = method, args = args, n = select("#", ...) }
end

-- ---------------------------------------------------------------- method table
-- Every method routes through here so behaviour is consistent and recorded.
local Methods = {};

-- Forward declaration: regions created by CreateTexture/CreateFontString need the
-- same metatable as frames, and those creators are defined before the metatable
-- itself further down this file.
local FrameMeta;

function Methods.GetName(self) return self.__name end
function Methods.GetParent(self) return self.__parent end
function Methods.SetParent(self, parent) self.__parent = parent; Record(self, "SetParent", parent); return self end

function Methods.SetPoint(self, point, relativeTo, relativePoint, x, y)
    -- support both SetPoint("CENTER") and the full form
    if ( type(relativeTo) == "number" ) then
        x, y, relativeTo, relativePoint = relativeTo, relativePoint, self.__parent, point
    end
    self.__points[#self.__points + 1] = {
        point = point, relativeTo = relativeTo,
        relativePoint = relativePoint, x = x or 0, y = y or 0,
    }
    Record(self, "SetPoint", point, relativePoint, x, y)
    return self
end
function Methods.ClearAllPoints(self) self.__points = {}; Record(self, "ClearAllPoints"); return self end
function Methods.GetPoint(self, index)
    local p = self.__points[index or 1]
    if ( not p ) then return nil end
    return p.point, p.relativeTo, p.relativePoint, p.x, p.y
end
function Methods.GetNumPoints(self) return #self.__points end
function Methods.SetAllPoints(self, target) Record(self, "SetAllPoints"); return self end

function Methods.SetSize(self, w, h) self.__width, self.__height = w or 0, h or 0; Record(self, "SetSize", w, h); return self end
function Methods.SetWidth(self, w) self.__width = w or 0; Record(self, "SetWidth", w); return self end
function Methods.SetHeight(self, h) self.__height = h or 0; Record(self, "SetHeight", h); return self end
function Methods.GetWidth(self) return self.__width end
function Methods.GetHeight(self) return self.__height end

function Methods.SetAlpha(self, a) self.__alpha = a; Record(self, "SetAlpha", a); return self end
function Methods.GetAlpha(self) return self.__alpha end

-- Geometry accessors. ECS_Roster derives the roster-relative pointer position
-- from GetTop() rather than from raw screen coordinates, so the shim must expose
-- edges for that path to be testable.
function Methods.GetTop(self) return self.__top or 0 end
function Methods.GetBottom(self) return self.__bottom or 0 end
function Methods.GetLeft(self) return self.__left or 0 end
function Methods.GetRight(self) return self.__right or 0 end
function Methods.SetTop(self, value) self.__top = value; return self end
function Methods.Show(self) self.__shown = true; Record(self, "Show"); return self end
function Methods.Hide(self) self.__shown = false; Record(self, "Hide"); return self end
function Methods.IsShown(self) return self.__shown end
function Methods.IsVisible(self) return self.__shown end
function Methods.SetShown(self, shown)
    if ( shown ) then return Methods.Show(self) end
    return Methods.Hide(self)
end
function Methods.SetFrameLevel(self, level) self.__level = level or 0; Record(self, "SetFrameLevel", level); return self end
function Methods.GetFrameLevel(self) return self.__level end
function Methods.SetFrameStrata(self, strata) self.__strata = strata; Record(self, "SetFrameStrata", strata); return self end

function Methods.SetScript(self, event, handler)
    self.__scripts[event] = handler
    Record(self, "SetScript", event, handler ~= nil)
    return self
end
function Methods.GetScript(self, event) return self.__scripts[event] end
function Methods.HookScript(self, event, handler)
    local previous = self.__scripts[event]
    self.__scripts[event] = function(...)
        if ( previous ) then previous(...) end
        return handler(...)
    end
    Record(self, "HookScript", event)
    return self
end
-- Test helper: fire a script the way the client would.
function Methods.__Fire(self, event, ...)
    local handler = self.__scripts[event]
    if ( handler ) then return handler(self, ...) end
    return nil
end

function Methods.RegisterEvent(self, event) self.__events[event] = true; Record(self, "RegisterEvent", event); return self end
function Methods.UnregisterEvent(self, event) self.__events[event] = nil; return self end
function Methods.RegisterForDrag(self, button) self.__dragButton = button; return self end
function Methods.SetMovable(self, movable) self.__movable = movable; return self end
function Methods.EnableMouse(self, enabled) self.__mouse = enabled; return self end
function Methods.EnableMouseWheel(self, enabled) self.__wheel = enabled; return self end
function Methods.SetHitRectInsets(self) return self end

-- ---------------------------------------------------------------- EditBox
function Methods.SetAutoFocus(self, value) self.__autoFocus = value; return self end
function Methods.SetMaxLetters(self, count) self.__maxLetters = count; return self end
function Methods.SetTextInsets(self, l, r, t, b) self.__textInsets = { l, r, t, b }; return self end
function Methods.SetNumeric(self, value) self.__numeric = value; return self end
function Methods.SetMultiLine(self, value) self.__multiLine = value; return self end
function Methods.SetAltArrowKeyMode(self, value) return self end
function Methods.Insert(self, text) self.__text = (self.__text or "") .. (text or ""); return self end
function Methods.HighlightText(self) return self end
function Methods.SetFocus(self) self.__focused = true; return self end
function Methods.ClearFocus(self) self.__focused = false; return self end
function Methods.HasFocus(self) return self.__focused == true end

function Methods.SetID(self, id)
    if ( type(id) ~= "number" ) then error("Usage: SetID(ID)") end
    self.__id_value = id;
    Record(self, "SetID", id);
    return self;
end
function Methods.GetID(self) return self.__id_value end

function Methods.CreateTexture(self, name, layer, template, subLevel)
    SHIM.textures = SHIM.textures + 1
    local region = NewRegion("Texture", name, self)
    region.__drawLayer = layer;
    region.__subLevel = subLevel or 0;
    setmetatable(region, FrameMeta)
    self.__textures = self.__textures or {}
    self.__textures[#self.__textures + 1] = region
    self.__regions[#self.__regions + 1] = region
    SHIM.Register(region, name)
    return region
end
function Methods.CreateFontString(self, name, layer, template)
    SHIM.fonts = SHIM.fonts + 1
    local region = NewRegion("FontString", name, self)
    setmetatable(region, FrameMeta)
    self.__fonts = self.__fonts or {}
    self.__fonts[#self.__fonts + 1] = region
    self.__regions[#self.__regions + 1] = region
    SHIM.Register(region, name)
    return region
end
function Methods.GetRegions(self) return unpack(self.__regions or {}) end

function Methods.SetTexture(self, texture) self.__texture = texture; Record(self, "SetTexture", texture); return self end
function Methods.GetTexture(self) return self.__texture end
function Methods.SetTexCoord(self, ...) self.__texcoord = { ... }; Record(self, "SetTexCoord", ...); return self end
function Methods.SetVertexColor(self, r, g, b, a)
    self.__vertex = { r, g, b, a }
    Record(self, "SetVertexColor", r, g, b, a)
    return self
end
function Methods.SetDesaturated(self, value) self.__desaturated = value; return self end
function Methods.SetBlendMode(self, mode) self.__blend = mode; return self end
function Methods.SetDrawLayer(self, layer) self.__layer = layer; return self end
function Methods.SetGradient(self) return self end

function Methods.SetText(self, text) self.__text = text; Record(self, "SetText", text); return self end
function Methods.GetText(self) return self.__text end
function Methods.SetFormattedText(self, fmt, ...) self.__text = string.format(fmt, ...); return self end
function Methods.SetTextColor(self, r, g, b, a) self.__textColor = { r, g, b, a }; return self end
function Methods.GetTextColor(self)
    local c = self.__textColor or { 1, 1, 1, 1 }
    return c[1], c[2], c[3], c[4]
end
function Methods.SetJustifyH(self, value) self.__justifyH = value; return self end
function Methods.SetJustifyV(self, value) self.__justifyV = value; return self end
function Methods.SetFont(self, path, size, flags) self.__font = { path, size, flags }; return self end
function Methods.SetShadowColor(self) return self end
function Methods.SetShadowOffset(self) return self end
function Methods.SetWordWrap(self, value) self.__wordWrap = value; return self end
function Methods.SetNonSpaceWrap(self) return self end
function Methods.GetStringWidth(self) return #(self.__text or "") * 6 end

function Methods.SetBackdrop(self, backdrop) self.__backdrop = backdrop; Record(self, "SetBackdrop", backdrop ~= nil); return self end
function Methods.SetBackdropColor(self, r, g, b, a) self.__backdropColor = { r, g, b, a }; return self end
function Methods.SetBackdropBorderColor(self, r, g, b, a) self.__borderColor = { r, g, b, a }; return self end
function Methods.GetBackdrop(self) return self.__backdrop end

function Methods.SetNormalTexture(self, texture)
    if ( type(texture) == "table" ) then self.__normalTexture = texture; return texture end
    if ( not self.__normalTexture or type(self.__normalTexture) == "string" ) then
        self.__normalTexture = Methods.CreateTexture(self)
    end
    self.__normalTexture:SetTexture(texture)
    Record(self, "SetNormalTexture", texture)
    return self.__normalTexture
end
function Methods.GetNormalTexture(self)
    if ( not self.__normalTexture ) then
        self.__normalTexture = Methods.CreateTexture(self)
    end
    return self.__normalTexture
end
function Methods.SetPushedTexture(self, texture)
    if ( type(texture) == "table" ) then self.__pushedTexture = texture; return texture end
    if ( not self.__pushedTexture or type(self.__pushedTexture) == "string" ) then
        self.__pushedTexture = Methods.CreateTexture(self)
    end
    self.__pushedTexture:SetTexture(texture)
    return self.__pushedTexture
end
function Methods.SetHighlightTexture(self, texture, mode)
    if ( type(texture) == "table" ) then self.__highlightTexture = texture; return texture end
    if ( not self.__highlightTexture or type(self.__highlightTexture) == "string" ) then
        self.__highlightTexture = Methods.CreateTexture(self)
    end
    self.__highlightTexture:SetTexture(texture)
    if ( mode ) then self.__highlightTexture:SetBlendMode(mode) end
    return self.__highlightTexture
end
function Methods.GetHighlightTexture(self)
    if ( not self.__highlightTexture ) then
        self.__highlightTexture = Methods.CreateTexture(self)
    end
    return self.__highlightTexture
end
function Methods.SetDisabledTexture(self, texture)
    if ( not self.__disabledTexture or type(self.__disabledTexture) == "string" ) then
        self.__disabledTexture = Methods.CreateTexture(self)
    end
    self.__disabledTexture:SetTexture(texture)
    return self.__disabledTexture
end

function Methods.LockHighlight(self) self.__highlighted = true; Record(self, "LockHighlight"); return self end
function Methods.UnlockHighlight(self) self.__highlighted = false; Record(self, "UnlockHighlight"); return self end
function Methods.SetChecked(self, value) self.__checked = value; return self end
function Methods.GetChecked(self) return self.__checked end
function Methods.Click(self) return self end

function Methods.SetVerticalScroll(self, value) self.__scroll = value; Record(self, "SetVerticalScroll", value); return self end
function Methods.GetVerticalScroll(self) return self.__scroll or 0 end
function Methods.SetHorizontalScroll(self, value) self.__scrollX = value; return self end
function Methods.GetVerticalScrollRange(self) return self.__scrollRange or 0 end
function Methods.SetScrollChild(self, child) self.__scrollChild = child; return self end
function Methods.GetScrollChild(self) return self.__scrollChild end
function Methods.UpdateScrollChildRect(self) Record(self, "UpdateScrollChildRect"); return self end
function Methods.SetMinMaxValues(self, min, max) self.__min, self.__max = min, max; return self end
function Methods.SetValue(self, value) self.__value = value; return self end
function Methods.GetValue(self) return self.__value or 0 end
function Methods.SetMinMaxValues(self, mn, mx) self.__min, self.__max = mn, mx; return self end

function Methods.SetScale(self, scale) self.__scale = scale; return self end
function Methods.GetScale(self) return self.__scale or 1 end

function Methods.IsObjectType(self, kind) return self.__kind == kind end
function Methods.GetObjectType(self) return self.__kind end

-- ---------------------------------------------------------------- metatable
FrameMeta = {}
FrameMeta.__index = function(self, key)
    local method = Methods[key]
    if ( method ) then return method end
    -- Unknown method: fail loudly so a typo in a module is caught by tests.
    if ( type(key) == "string" and string.sub(key, 1, 3) == "Set" ) then
        return function()
            error("frame shim: unimplemented method '" .. tostring(key)
                .. "' on " .. tostring(self.__kind), 2)
        end
    end
    return nil
end

function SHIM.CreateFrame(kind, name, parent, template)
    SHIM.created = SHIM.created + 1
    local frame = NewRegion(kind or "Frame", name, parent)
    setmetatable(frame, FrameMeta)
    SHIM.Register(frame, name)
    return frame
end

-- Install the globals the ECS modules expect.
function SHIM.Install()
    _G.CreateFrame = function(kind, name, parent, template)
        return SHIM.CreateFrame(kind, name, parent, template)
    end
    _G.UIParent = SHIM.CreateFrame("Frame", "UIParent")
    _G.GetTime = function() return 0 end
    -- Screen metrics are part of the real API and ECS_UI's layout depends on
    -- them, so the shim provides them rather than letting the module fall back to
    -- its default (which is a narrow screen and would mask a wide-screen bug).
    SHIM.screenWidth = SHIM.screenWidth or 1920
    SHIM.screenHeight = SHIM.screenHeight or 1080
    _G.GetScreenWidth = function() return SHIM.screenWidth end
    _G.GetScreenHeight = function() return SHIM.screenHeight end
    -- Cursor position in UI space (bottom-left origin), overridable per test.
    SHIM.cursorX = SHIM.cursorX or 0
    SHIM.cursorY = SHIM.cursorY or 0
    _G.GetCursorPosition = function() return SHIM.cursorX, SHIM.cursorY end
    -- WoW glue globals the modules may reference defensively.
    _G.strlower = string.lower
    _G.strupper = string.upper
    _G.strsub = string.sub
    _G.strlen = string.len
    _G.strfind = string.find
    _G.format = string.format
    _G.tinsert = table.insert
    _G.tremove = table.remove
    _G.unpack = unpack
end

function SHIM.Register(frame, name)
    if ( name ) then
        _G[name] = frame;
        SHIM.globals[#SHIM.globals + 1] = name;
    end
    return frame;
end

function SHIM.Reset()
    -- Also clear the globals this shim created, otherwise a Reset is not really a
    -- reset: stale named frames from a previous test would still be found by
    -- _G lookups, which is exactly how a pool-building test can pass or fail by
    -- accident.
    for index = 1, #SHIM.globals do
        _G[SHIM.globals[index]] = nil
    end
    SHIM.frames = {}
    SHIM.globals = {}
    SHIM.nextId = 0
    SHIM.created = 0
    SHIM.textures = 0
    SHIM.fonts = 0
end
