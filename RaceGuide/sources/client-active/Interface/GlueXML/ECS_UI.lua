--[[ ECS_UI.lua -----------------------------------------------------------------
    Esteria Character Select - the chrome ECS adds on top of the stock screen
    (spec 3, 6, 8, 12, 13, 16, 21, 29).

    Everything here is created ONCE and then only updated. No frame is built
    inside a refresh path, and no OnUpdate is added per row: a single driver steps
    the tooltip delay, and hover easing rides the existing ECS_Anim controller.

    All of it is additive. Nothing in the stock character-select frame is removed
    or re-parented, so AddOns / Options / Back / Enter World keep working exactly
    as before.

    Lua 5.1 only. No frame work at file scope.
------------------------------------------------------------------------------ ]]

ECS = ECS or {};
ECS.UI = ECS.UI or {};

local U = ECS.UI;
local C = ECS.Const;
local T = ECS.Tooltip;

U.built = false;

-- ---------------------------------------------------------------- helpers
local function SafeCall(fn, ...)
    if ( type(fn) ~= "function" ) then return nil end
    local ok, value = pcall(fn, ...)
    if ( not ok ) then return nil end
    return value
end

function U.ScreenWidth()
    return SafeCall(_G.GetScreenWidth) or 1024;
end

function U.ScreenHeight()
    return SafeCall(_G.GetScreenHeight) or 768;
end

-- The native textured Glue tooltip surface used by CharacterCreate.
local function ApplySurface(frame, alpha)
    if ( not frame or not frame.SetBackdrop ) then return end
    frame:SetBackdrop({
        bgFile   = C.TEX.createTooltipBackground,
        edgeFile = C.TEX.createTooltipBorder,
        tile     = true,
        tileSize = 16,
        edgeSize = 16,
        insets   = { left = 4, right = 4, top = 4, bottom = 4 },
    });
    frame:SetBackdropColor(0.09, 0.09, 0.19, alpha or 1);
    frame:SetBackdropBorderColor(1, 1, 1, 1);
end

U.ApplySurface = ApplySurface;

local BUTTON_UP_TEXCOORDS = { 0, 0.578125, 0, 0.75 };
local BUTTON_HIGHLIGHT_TEXCOORDS = { 0, 0.625, 0, 0.6875 };
local DELETE_ATLAS_TEXCOORDS = {
    NormalTexture = { 0.001953125, 0.126953125, 0, 0.248046875 },
    PushedTexture = { 0.128906250, 0.253906250, 0, 0.248046875 },
    HighlightTexture = { 0.253906250, 0.378906250, 0, 0.248046875 },
};

local function ApplyBlueGlueButton(button)
    if ( not button ) then return false end

    local states = {
        { setter = "SetNormalTexture", getter = "GetNormalTexture",
          texture = C.TEX.glueButtonUpBlue, coords = BUTTON_UP_TEXCOORDS },
        { setter = "SetPushedTexture", getter = "GetPushedTexture",
          texture = C.TEX.glueButtonDownBlue, coords = BUTTON_UP_TEXCOORDS },
        { setter = "SetHighlightTexture", getter = "GetHighlightTexture",
          texture = C.TEX.glueButtonHighlightBlue, coords = BUTTON_HIGHLIGHT_TEXCOORDS, blend = "ADD" },
    };
    for index = 1, #states do
        local state = states[index];
        local setTexture = button[state.setter];
        if ( type(setTexture) == "function" ) then
            local ok, region = pcall(setTexture, button, state.texture, state.blend);
            if ( ok and not region and type(button[state.getter]) == "function" ) then
                local got, value = pcall(button[state.getter], button);
                if ( got ) then region = value end
            end
            if ( ok and region ) then
                if ( region.SetTexCoord ) then region:SetTexCoord(unpack(state.coords)) end
                if ( region.SetAlpha ) then region:SetAlpha(1) end
            end
        end
    end
    return true;
end

local function ApplyBlueDeleteAtlas(button)
    if ( not button or not button.GetName ) then return false end
    local name = button:GetName();
    if ( not name ) then return false end

    if ( type(button.SetText) == "function" ) then button:SetText(""); end

    local states = {
        { suffix = "NormalTexture", getter = "GetNormalTexture" },
        { suffix = "PushedTexture", getter = "GetPushedTexture" },
        { suffix = "HighlightTexture", getter = "GetHighlightTexture" },
    };
    for index = 1, #states do
        local state = states[index];
        local suffix = state.suffix;
        local coords = DELETE_ATLAS_TEXCOORDS[suffix];
        local texture = _G[name .. suffix];
        if ( texture and texture.SetTexture ) then
            texture:SetTexture(C.TEX.deleteButtonBlueAtlas);
            if ( texture.SetTexCoord ) then texture:SetTexCoord(unpack(coords)) end
            if ( texture.SetAlpha ) then texture:SetAlpha(1) end
        end
        local getTexture = button[state.getter];
        if ( type(getTexture) == "function" ) then
            local ok, region = pcall(getTexture, button);
            if ( ok and region and region ~= texture and region.SetTexture ) then
                region:SetTexture(C.TEX.deleteButtonBlueAtlas);
                if ( region.SetTexCoord ) then region:SetTexCoord(unpack(coords)) end
                if ( region.SetAlpha ) then region:SetAlpha(1) end
            end
        end
    end

    -- The XML OnUpdate only swaps the old red/blue button skins for Death Knights.
    -- ECS installs a blue-tinted atlas for Delete in every case, so stop that swap.
    if ( button.SetScript ) then button:SetScript("OnUpdate", nil) end
    return true;
end

local function HideRealmChrome()
    local stockRealm = _G.CharSelectRealmName;
    if ( stockRealm ) then
        if ( stockRealm.SetAlpha ) then
            pcall(stockRealm.SetAlpha, stockRealm, 0);
        end
        if ( stockRealm.Hide ) then pcall(stockRealm.Hide, stockRealm) end
    end

    local changeRealm = _G.CharSelectChangeRealmButton;
    if ( changeRealm ) then
        if ( changeRealm.SetText ) then pcall(changeRealm.SetText, changeRealm, "") end
        if ( changeRealm.EnableMouse ) then pcall(changeRealm.EnableMouse, changeRealm, false) end
        if ( changeRealm.Hide ) then pcall(changeRealm.Hide, changeRealm) end
    end

    local listToggle = _G.DesenfoBoton2;
    if ( listToggle ) then
        if ( listToggle.EnableMouse ) then pcall(listToggle.EnableMouse, listToggle, false) end
        if ( listToggle.Hide ) then pcall(listToggle.Hide, listToggle) end
        local name = listToggle.GetName and listToggle:GetName();
        if ( name ) then
            local label = _G[name .. "Label"];
            if ( label and label.Hide ) then pcall(label.Hide, label) end
            local background = _G[name .. "TextBackground"];
            if ( background and background.Hide ) then pcall(background.Hide, background) end
        end
    end
end

local function ApplyCreateTooltipSurface(frame)
    ApplySurface(frame, 1);
end

local function MakeText(parent, size, justify)
    local font = parent:CreateFontString(nil, "OVERLAY");
    if ( justify ) then font:SetJustifyH(justify) end
    if ( ECS.Row and ECS.Row.ApplyFont ) then
        ECS.Row.ApplyFont(font, size);
    end
    return font;
end

-- ---------------------------------------------------------------- notes editor (spec 12)
-- A small dedicated panel rather than the generic modal, because it needs a text
-- field. Save/Cancel are explicit so Cancel can genuinely discard (ECS_Notes owns
-- the draft, so nothing is written until Save).
function U.BuildNotesEditor(parent)
    if ( U.notesEditor ) then
        return U.notesEditor
    end

    local editor = CreateFrame("Frame", "ECSNotesEditor", parent);
    editor:SetSize(C.MODAL_WIDTH, 132);
    editor:SetPoint("CENTER", parent, "CENTER", 0, 0);
    ApplySurface(editor, C.TOOLTIP_ALPHA);
    editor:Hide();

    editor.header = MakeText(editor, C.NAME_FONT_SIZE, "LEFT");
    editor.header:SetPoint("TOPLEFT", editor, "TOPLEFT", 12, -10);
    editor.header:SetWidth(C.MODAL_WIDTH - 24);

    local field = CreateFrame("Frame", "ECSNotesField", editor);
    field:SetSize(C.MODAL_WIDTH - 24, C.SEARCH_HEIGHT);
    field:SetPoint("TOPLEFT", editor, "TOPLEFT", 12, -32);
    ApplySurface(field, 0.85);

    local box = CreateFrame("EditBox", "ECSNotesEdit", field);
    box:SetPoint("TOPLEFT", field, "TOPLEFT", 6, -3);
    box:SetPoint("BOTTOMRIGHT", field, "BOTTOMRIGHT", -6, 3);
    box:SetAutoFocus(false);
    box:SetMaxLetters(ECS.Notes.MAX_LENGTH);
    box:SetTextInsets(0, 0, 0, 0);
    if ( ECS.Row and ECS.Row.ApplyFont ) then
        ECS.Row.ApplyFont(box, C.SUB_FONT_SIZE);
    end

    local function MakeButton(label, anchorTo, x)
        local button = CreateFrame("Button", nil, editor);
        button:SetSize(80, C.MODAL_BUTTON_H);
        button:SetPoint("BOTTOMRIGHT", anchorTo, "BOTTOMRIGHT", x, 12);
        ApplySurface(button, 0.85);
        button.label = MakeText(button, C.SUB_FONT_SIZE, "CENTER");
        button.label:SetPoint("CENTER", button, "CENTER", 0, 0);
        button.label:SetText(label);
        return button
    end

    editor.save   = MakeButton("Save", editor, -12);
    editor.cancel = MakeButton("Cancel", editor.save, -84);
    editor.clear  = MakeButton("Clear", editor.cancel, -84);

    editor.save:SetScript("OnClick", function()
        ECS.Notes.CommitEdit();
        U.HideNotesEditor();
        if ( ECS.Integrate ) then
            pcall(ECS.Integrate.ApplyNotesAndRefresh);
        end
    end);
    editor.cancel:SetScript("OnClick", function()
        ECS.Notes.CancelEdit();
        U.HideNotesEditor();
    end);
    editor.clear:SetScript("OnClick", function()
        ECS.Notes.ClearDraft();
        if ( box.SetText ) then box:SetText("") end
    end);
    box:SetScript("OnEscapePressed", function()
        ECS.Notes.CancelEdit();
        U.HideNotesEditor();
    end);
    -- Typing must reach the DRAFT. Without this the editor would look like it
    -- worked while Save silently persisted the original value, because the draft
    -- was only ever seeded from the stored note.
    box:SetScript("OnTextChanged", function(self, userInput)
        if ( not userInput ) then
            return;
        end
        ECS.Notes.SetDraft(self:GetText());
    end);
    box:SetScript("OnEnterPressed", function()
        ECS.Notes.CommitEdit();
        U.HideNotesEditor();
        if ( ECS.Integrate ) then
            pcall(ECS.Integrate.ApplyNotesAndRefresh);
        end
    end);

    editor.box = box;
    U.notesEditor = editor;
    return editor
end

function U.ShowNotesEditor(character)
    if ( not character or not character.stableKey ) then
        return false
    end
    if ( not U.BuildNotesEditor(U.parent) ) then
        return false
    end

    ECS.Notes.BeginEdit(character.stableKey);
    local editor = U.notesEditor;
    editor.header:SetText(character.name or "");
    if ( editor.box.SetText ) then
        editor.box:SetText(ECS.Notes.GetDraft() or "");
    end
    editor:Show();
    if ( editor.box.SetFocus ) then
        pcall(editor.box.SetFocus, editor.box);
    end
    return true
end

function U.HideNotesEditor()
    if ( U.notesEditor ) then
        U.notesEditor:Hide();
    end
    return true
end

function U.IsNotesEditorShown()
    return U.notesEditor ~= nil and U.notesEditor:IsShown() == true
end

-- ---------------------------------------------------------------- drag driver (spec 10)
-- A mouse-down only fires once. Without a driver polling while the button is
-- held, UpdatePress would never see the pointer move, the drop target would stay
-- where the drag started, and releasing would always be a no-op reorder.
--
-- Like the tooltip driver this hides itself the moment the drag ends, so idle
-- cost is zero.
function U.StartDragDriver()
    if ( type(CreateFrame) ~= "function" ) then
        return false
    end
    if ( not U.dragDriver ) then
        local driver = CreateFrame("Frame", "ECSDragDriver", U.parent or _G.UIParent);
        driver:Hide();
        driver:SetScript("OnUpdate", function(self)
            if ( not ECS.Roster.drag ) then
                self:Hide();
                return;
            end
            local x = 0;
            local ok, cursorX = pcall(_G.GetCursorPosition);
            if ( ok ) then x = cursorX or 0 end
            pcall(ECS.Roster.UpdatePress, x, ECS.Roster.CursorOffsetY() or 0);
        end);
        U.dragDriver = driver;
    end
    U.dragDriver:Show();
    return true
end

function U.StopDragDriver()
    if ( U.dragDriver ) then
        U.dragDriver:Hide();
    end
    return true
end

-- ---------------------------------------------------------------- build
-- CHROME MUST BE PARENTED TO THE SCREEN, NOT TO UIParent.
--
-- GlueParent.xml declares `<Frame name="GlueParent" setAllPoints="true">` with no
-- parent attribute, so GlueParent is a child of UIParent - and the glue screens are
-- children of GlueParent. SetGlueScreen() (GlueParent.lua:215) switches screens by
-- calling `frame:Hide()` on every frame in GlueScreenInfo and then Show() on the one
-- requested, where GlueScreenInfo["charselect"] = "CharacterSelect".
--
-- So anything parented to UIParent is a SIBLING of GlueParent and is never hidden:
-- it would stay on screen after Back, on the realm list, over the character-create
-- screen, the options panel, the credits and the intro movie. For ECS that meant a
-- visible search box and status line floating over character creation, with a live
-- EditBox that still ran the roster refresh when typed into.
--
-- CharacterSelect is a ModelFFX whose UI child is CharacterSelectUI; both are
-- setAllPoints, so anchoring to either covers the screen exactly as UIParent did and
-- the layout is unchanged - but the chrome now inherits the screen's show/hide.
function U.PreferredParent()
    if ( _G.CharacterSelectUI ) then
        return _G.CharacterSelectUI;
    end
    if ( _G.CharacterSelect ) then
        return _G.CharacterSelect;
    end
    return _G.UIParent;
end

function U.Build(parent)
    if ( U.built ) then
        return true;
    end
    if ( type(CreateFrame) ~= "function" ) then
        return false;
    end
    parent = parent or U.PreferredParent();
    if ( not parent ) then
        return false;
    end

    U.parent = parent;

    -- ------------------------------------------------ search field (spec 8)
    local search = CreateFrame("Frame", "ECSSearchFrame", parent);
    search:SetSize(C.ROSTER_WIDTH, C.SEARCH_HEIGHT);
    search:SetPoint("TOPRIGHT", parent, "TOPRIGHT", -C.ROSTER_RIGHT, -C.SEARCH_TOP);
    ApplySurface(search, 0.70);

    -- Magnifier, so the box reads as search at a glance (the reference layout puts
    -- one here). Typed text starts past it - test_ui asserts that geometry rather
    -- than trusting these two numbers to stay in step.
    local icon = search:CreateTexture("ECSSearchIcon", "ARTWORK");
    icon:SetTexture(C.TEX.searchIcon);
    icon:SetSize(C.SEARCH_ICON_SIZE, C.SEARCH_ICON_SIZE);
    icon:SetPoint("LEFT", search, "LEFT", C.SEARCH_ICON_INSET, 0);
    search.icon = icon;

    local box = CreateFrame("EditBox", "ECSSearchBox", search);
    box:SetPoint("TOPLEFT", search, "TOPLEFT", C.SEARCH_TEXT_INSET, -3);
    box:SetPoint("BOTTOMRIGHT", search, "BOTTOMRIGHT", -6, 3);
    box:SetAutoFocus(false);
    box:SetMaxLetters(ECS.Search.MAX_LENGTH);
    box:SetTextInsets(0, 0, 0, 0);
    if ( ECS.Row and ECS.Row.ApplyFont ) then
        ECS.Row.ApplyFont(box, C.SUB_FONT_SIZE);
    end
    local text = C.COLOUR.text;
    if ( box.SetTextColor ) then
        box:SetTextColor(text[1], text[2], text[3]);
    end

    local placeholder = MakeText(search, C.SUB_FONT_SIZE, "LEFT");
    placeholder:SetPoint("LEFT", box, "LEFT", 2, 0);
    local dim = C.COLOUR.textDim;
    if ( placeholder.SetTextColor ) then
        placeholder:SetTextColor(dim[1], dim[2], dim[3]);
    end
    placeholder:SetText(C.SEARCH_PLACEHOLDER);

    local function SyncPlaceholder()
        local current = "";
        if ( box.GetText ) then current = box:GetText() or "" end
        if ( current == "" ) then placeholder:Show() else placeholder:Hide() end
    end

    box:SetScript("OnTextChanged", function(self, userInput)
        if ( not userInput ) then return end
        ECS.Search.SetQuery(self:GetText());
        SyncPlaceholder();
        if ( ECS.Integrate and ECS.Integrate.Refresh ) then
            ECS.Integrate.Refresh();
        end
        U.RefreshStatus();
    end);
    box:SetScript("OnEscapePressed", function(self)
        -- spec 30: Escape clears; a second Escape releases focus so the key can
        -- reach the screen and close it.
        if ( ECS.Search.HandleEscape() ) then
            self:SetText("");
            SyncPlaceholder();
            if ( ECS.Integrate and ECS.Integrate.Refresh ) then
                ECS.Integrate.Refresh();
            end
            U.RefreshStatus();
        else
            self:ClearFocus();
        end
    end);
    box:SetScript("OnEnterPressed", function(self)
        -- Enter must never enter the world from inside a text box. HandleEnter is
        -- the seam that decides whether the key was consumed; it currently
        -- declines (returning false), so the box simply gives focus back and the
        -- screen behaves as before. It is consulted rather than assumed so the
        -- policy lives in one place instead of being implied by this comment.
        if ( not ECS.Search.HandleEnter() ) then
            self:ClearFocus();
        end
    end);
    box:SetScript("OnEditFocusGained", function() placeholder:Hide() end);
    box:SetScript("OnEditFocusLost", SyncPlaceholder);

    search.box = box;
    search.placeholder = placeholder;
    U.search = search;

    -- ------------------------------------------------ status / empty state (spec 8, 31)
    -- ECS_Search already computes "3 of 12" and "No matches"; without this line
    -- that feedback existed but was never shown, and an account with no
    -- characters looked like a broken roster rather than an empty one.
    local status = MakeText(parent, C.ZONE_FONT_SIZE, "RIGHT");
    status:SetPoint("TOPRIGHT", parent, "TOPRIGHT", -C.ROSTER_RIGHT, -C.STATUS_TOP);
    status:SetWidth(C.ROSTER_WIDTH);
    status:Hide();
    U.status = status;

    local empty = CreateFrame("Frame", "ECSEmptyState", parent);
    empty:SetSize(C.ROSTER_WIDTH, 60);
    empty:SetPoint("TOP", parent, "TOP", 0, -240);
    empty.title = MakeText(empty, C.NAME_FONT_SIZE, "CENTER");
    empty.title:SetPoint("TOP", empty, "TOP", 0, 0);
    empty.title:SetWidth(C.ROSTER_WIDTH);
    empty.title:SetText(C.EMPTY_TITLE);
    empty.body = MakeText(empty, C.SUB_FONT_SIZE, "CENTER");
    empty.body:SetPoint("TOP", empty, "TOP", 0, -18);
    empty.body:SetWidth(C.ROSTER_WIDTH);
    empty.body:SetText(C.EMPTY_BODY);
    empty:Hide();
    U.emptyState = empty;

    -- ------------------------------------------------ tooltip (spec 13)
    local tip = CreateFrame("Frame", "ECSTooltip", parent);
    tip:SetFrameStrata("TOOLTIP");
    tip:SetSize(T.MIN_WIDTH, 40);
    tip:SetPoint("TOPLEFT", parent, "TOPLEFT", 0, 0);
    ApplyCreateTooltipSurface(tip);
    tip.lines = {};
    tip:Hide();
    U.tooltip = tip;

    -- ------------------------------------------------ modal (spec 21)
    local overlay = CreateFrame("Frame", "ECSModalOverlay", parent);
    overlay:SetAllPoints(parent);
    overlay:Hide();

    local modal = CreateFrame("Frame", "ECSModal", overlay);
    modal:SetSize(C.MODAL_WIDTH, C.MODAL_MIN_HEIGHT);
    modal:SetPoint("CENTER", overlay, "CENTER", 0, 0);
    ApplySurface(modal, C.TOOLTIP_ALPHA);

    modal.title = MakeText(modal, C.NAME_FONT_SIZE, "LEFT");
    modal.title:SetPoint("TOPLEFT", modal, "TOPLEFT", 12, -10);
    modal.title:SetWidth(C.MODAL_WIDTH - 24);

    modal.body = MakeText(modal, C.SUB_FONT_SIZE, "LEFT");
    modal.body:SetPoint("TOPLEFT", modal, "TOPLEFT", 12, -32);
    modal.body:SetWidth(C.MODAL_WIDTH - 24);

    local accept = CreateFrame("Button", "ECSModalAccept", modal);
    accept:SetSize(C.MODAL_BUTTON_W, C.MODAL_BUTTON_H);
    accept:SetPoint("BOTTOMRIGHT", modal, "BOTTOMRIGHT", -12, 12);
    ApplySurface(accept, 0.85);
    accept.label = MakeText(accept, C.SUB_FONT_SIZE, "CENTER");
    accept.label:SetPoint("CENTER", accept, "CENTER", 0, 0);
    accept:SetScript("OnClick", function()
        ECS.Modal.Accept();
        U.RefreshModal();
    end);

    local cancel = CreateFrame("Button", "ECSModalCancel", modal);
    cancel:SetSize(C.MODAL_BUTTON_W, C.MODAL_BUTTON_H);
    cancel:SetPoint("BOTTOMRIGHT", accept, "BOTTOMLEFT", -8, 0);
    ApplySurface(cancel, 0.85);
    cancel.label = MakeText(cancel, C.SUB_FONT_SIZE, "CENTER");
    cancel.label:SetPoint("CENTER", cancel, "CENTER", 0, 0);
    cancel:SetScript("OnClick", function()
        ECS.Modal.Cancel();
        U.RefreshModal();
    end);

    modal.accept = accept;
    modal.cancel = cancel;
    overlay.modal = modal;
    U.overlay = overlay;

    -- ------------------------------------------------ one driver for the delay
    local driver = CreateFrame("Frame", "ECSUIDriver", parent);
    driver:Hide();
    driver:SetScript("OnUpdate", function(_, elapsed)
        if ( T.Update(elapsed) ) then
            U.RefreshTooltip();
        end
        if ( not T.IsVisible() and not T.pending ) then
            U.HideTooltip();
            driver:Hide();   -- no OnUpdate while the pointer is still
        end
    end);
    U.driver = driver;

    U.built = true;
    U.BuildNotesEditor(parent);
    U.Layout();
    return true;
end

-- ---------------------------------------------------------------- layout (spec 29)
function U.Layout()
    if ( not U.built ) then return end
    local screenWidth = U.ScreenWidth();
    -- keep the column on the right edge; if the screen is very narrow, widen the
    -- margin so the roster does not collide with the 3D character
    local margin = C.ROSTER_RIGHT;
    if ( screenWidth > 0 and screenWidth < 1100 ) then
        margin = 6;
    end
    local parent = U.parent;
    HideRealmChrome();

    -- The old standalone mode toggle sits beside Back at the lower left; the
    -- reference keeps the action stack clean and puts manager controls in the top bar.
    local oldModeToggle = _G.DesenfoBoton;
    if ( oldModeToggle and oldModeToggle.Hide ) then
        oldModeToggle:Hide();
    end

    local addons = _G.CharacterSelectAddonsButton;
    local options = _G.OptionsButton2;
    local back = _G.CharacterSelectBackButton;
    if ( back ) then
        back:SetSize(C.VANILLA_GLUE_BUTTON_WIDTH, C.VANILLA_GLUE_BUTTON_HEIGHT);
        back:ClearAllPoints();
        back:SetPoint("BOTTOMLEFT", parent, "BOTTOMLEFT", 5, 5);
        ApplyBlueGlueButton(back);
    end
    if ( addons ) then
        addons:SetSize(C.VANILLA_GLUE_BUTTON_WIDTH, C.VANILLA_GLUE_BUTTON_HEIGHT);
        addons:ClearAllPoints();
        addons:SetPoint("BOTTOMLEFT", parent, "BOTTOMLEFT", 5, 50);
        ApplyBlueGlueButton(addons);
    end
    if ( addons and options ) then
        options:SetSize(C.VANILLA_GLUE_BUTTON_WIDTH, C.VANILLA_GLUE_BUTTON_HEIGHT);
        options:ClearAllPoints();
        options:SetPoint("BOTTOMLEFT", addons, "TOPLEFT", 0, -5);
        ApplyBlueGlueButton(options);
    end

    local enterWorld = _G.CharSelectEnterWorldButton;
    if ( enterWorld ) then
        enterWorld:SetSize(C.VANILLA_ENTER_WORLD_WIDTH, C.VANILLA_ENTER_WORLD_HEIGHT);
        enterWorld:ClearAllPoints();
        enterWorld:SetPoint("BOTTOM", parent, "BOTTOM", 0, C.ENTER_WORLD_BOTTOM_OFFSET);
        ApplyBlueGlueButton(enterWorld);
    end

    local rotateLeft = _G.CharacterSelectRotateLeft;
    local rotateRight = _G.CharacterSelectRotateRight;
    if ( rotateLeft ) then
        rotateLeft:Hide();
        if ( rotateLeft.EnableMouse ) then rotateLeft:EnableMouse(false) end
    end
    if ( rotateRight ) then
        rotateRight:Hide();
        if ( rotateRight.EnableMouse ) then rotateRight:EnableMouse(false) end
    end

    local createCharacter = _G.CharSelectCreateCharacterButton;
    local deleteCharacter = _G.CharacterSelectDeleteButton;
    if ( createCharacter ) then
        createCharacter:SetSize(C.VANILLA_GLUE_BUTTON_WIDTH, C.VANILLA_GLUE_BUTTON_HEIGHT);
        createCharacter:ClearAllPoints();
        createCharacter:SetPoint("BOTTOMRIGHT", parent, "BOTTOMRIGHT",
            -(C.ACTION_BUTTON_MARGIN + C.VANILLA_DELETE_BUTTON_SIZE + C.ACTION_BUTTON_GAP),
            C.CREATE_BUTTON_BOTTOM_MARGIN);
        ApplyBlueGlueButton(createCharacter);
    end
    if ( deleteCharacter ) then
        deleteCharacter:SetSize(C.VANILLA_DELETE_BUTTON_SIZE, C.VANILLA_DELETE_BUTTON_SIZE);
        deleteCharacter:ClearAllPoints();
        if ( createCharacter ) then
            deleteCharacter:SetPoint("LEFT", createCharacter, "RIGHT", C.ACTION_BUTTON_GAP, 0);
        else
            deleteCharacter:SetPoint("BOTTOMRIGHT", parent, "BOTTOMRIGHT",
                -C.ACTION_BUTTON_MARGIN, C.CREATE_BUTTON_BOTTOM_MARGIN);
        end
        ApplyBlueDeleteAtlas(deleteCharacter);
    end

    local stockCharacterFrame = _G.CharacterSelectCharacterFrame;
    if ( stockCharacterFrame ) then
        if ( stockCharacterFrame.SetBackdropColor ) then
            pcall(stockCharacterFrame.SetBackdropColor, stockCharacterFrame, 0, 0, 0, 0);
        end
        if ( stockCharacterFrame.SetBackdropBorderColor ) then
            pcall(stockCharacterFrame.SetBackdropBorderColor, stockCharacterFrame, 0, 0, 0, 0);
        end
    end

    if ( U.search ) then
        U.search:ClearAllPoints();
        U.search:SetPoint("TOPRIGHT", parent, "TOPRIGHT", -margin, -C.SEARCH_TOP);
    end
end

function U.SetRealmName(name)
    if ( not U.built ) then return false end
    HideRealmChrome();
    return true;
end

-- ---------------------------------------------------------------- status (spec 8, 31)
-- A persistence failure is reported BEFORE the search summary, because it is the
-- more important news: the search summary describes what is on screen, while a
-- failed save means what is on screen is not what the user will get next login.
function U.PersistenceNotice()
    local integrate = ECS.Integrate;
    if ( not integrate ) then
        return nil;
    end
    if ( integrate.refreshError ) then
        return "Roster render error: " .. tostring(integrate.refreshError);
    end
    if ( integrate.buildError ) then
        return "Roster data error: " .. tostring(integrate.buildError);
    end
    if ( integrate.saveError ) then
        return C.NOTICE_SAVE_FAILED;
    end
    if ( integrate.notesDropped ) then
        return C.NOTICE_NOTES_DROPPED;
    end
    return nil;
end

-- Shows ECS_Search's summary ("12 characters" / "3 of 12" / "No matches"), and a
-- proper empty state when the account genuinely has no characters - which is a
-- different situation from "everything is filtered out" and needs different copy.
function U.RefreshStatus()
    if ( not U.built ) then return false end

    if ( U.emptyState ) then
        if ( ECS.Search.IsRosterEmpty() ) then
            U.emptyState:Show();
        else
            U.emptyState:Hide();
        end
    end

    if ( not U.status ) then return false end

    local notice = U.PersistenceNotice();
    if ( notice ) then
        U.status:SetText(notice);
        U.status:Show();
        if ( U.status.SetTextColor ) then
            local danger = C.COLOUR.danger;
            U.status:SetTextColor(danger[1], danger[2], danger[3]);
        end
        return true
    end

    if ( ECS.Search.IsRosterEmpty() ) then
        U.status:Hide();          -- the empty state says it better
        return true
    end

    -- The reference keeps the header compact: do not add a count line until the
    -- user is actively filtering the roster.
    if ( not ECS.Search.IsActive() ) then
        U.status:Hide();
        return true;
    end

    local summary = ECS.Search.Summary();
    if ( summary == "" ) then
        U.status:Hide();
    else
        U.status:SetText(summary);
        U.status:Show();
        if ( ECS.Search.IsEmptyResult() ) then
            local danger = C.COLOUR.textDim;
            if ( U.status.SetTextColor ) then
                U.status:SetTextColor(danger[1], danger[2], danger[3]);
            end
        else
            local text = C.COLOUR.textDim;
            if ( U.status.SetTextColor ) then
                U.status:SetTextColor(text[1], text[2], text[3]);
            end
        end
    end
    return true
end

-- ---------------------------------------------------------------- tooltip
function U.RefreshTooltip()
    if ( not U.built or not U.tooltip ) then return false end
    local character = T.GetCharacter();
    if ( not character ) then
        U.HideTooltip();
        return false;
    end

    local lines = T.BuildLines(character);
    local tip = U.tooltip;

    -- reuse the FontStrings; create only as many as this character needs
    for index = 1, #lines do
        local font = tip.lines[index];
        if ( not font ) then
            font = MakeText(tip, C.SUB_FONT_SIZE, "LEFT");
            tip.lines[index] = font;
        end
        font:SetText(lines[index].text or "");
        font:ClearAllPoints();
        font:SetPoint("TOPLEFT", tip, "TOPLEFT", 10, -8 - ((index - 1) * 14));
        if ( font.SetWidth ) then font:SetWidth(T.MAX_WIDTH - 20) end
        if ( font.Show ) then font:Show() end
    end
    for index = #lines + 1, #tip.lines do
        if ( tip.lines[index].Hide ) then tip.lines[index]:Hide() end
    end

    local width, height = T.EstimateSize(lines);
    tip:SetSize(width, height);

    local cursorX, cursorY = 0, 0;
    local ok, x, y = pcall(_G.GetCursorPosition);
    if ( ok ) then cursorX, cursorY = x or 0, y or 0 end
    local scale = U.parent.GetEffectiveScale and U.parent:GetEffectiveScale() or 1;
    if scale <= 0 then scale = 1; end
    cursorX, cursorY = cursorX / scale, cursorY / scale;

    -- GetCursorPosition is bottom-left origin; the anchor maths works top-left
    local screenHeight = U.parent:GetHeight();
    local topLeftY = screenHeight - cursorY;

    local px, py = T.ComputeAnchor(cursorX, topLeftY, width, height,
        U.parent:GetWidth(), screenHeight);
    tip:ClearAllPoints();
    tip:SetPoint("TOPLEFT", U.parent, "TOPLEFT", px, -py);
    tip:Show();
    return true;
end

function U.HideTooltip()
    if ( U.built and U.tooltip ) then
        U.tooltip:Hide();
    end
    return true;
end

-- ---------------------------------------------------------------- modal
function U.RefreshModal()
    if ( not U.built or not U.overlay ) then return false end
    local modal = ECS.Modal.Top();
    if ( not modal ) then
        U.overlay:Hide();
        return false;
    end

    local frame = U.overlay.modal;
    frame.title:SetText(modal.title or "");
    frame.body:SetText(modal.text or "");
    frame.accept.label:SetText(modal.accept or "OKAY");

    if ( modal.cancel ) then
        frame.cancel.label:SetText(modal.cancel);
        frame.cancel:Show();
    else
        frame.cancel:Hide();
    end

    U.overlay:Show();
    return true;
end

function U.HideModal()
    if ( U.built and U.overlay ) then
        U.overlay:Hide();
    end
    return true
end

-- ---------------------------------------------------------------- row polish
-- spec 6: hover eases rather than snapping. The hovered FLAG is set immediately
-- so behaviour is unchanged; only the visual amount is tweened.
function U.WireRow(button)
    if ( not button or button.__ecsUiWired ) then
        return false;
    end
    button.__ecsUiWired = true;

    button:HookScript("OnEnter", function(self)
        ECS.Row.SetHovered(self, true);
        -- SetHovered snaps the visual amount to its end state (so it is correct
        -- when used standalone), so reset it here and ease up from zero.
        ECS.Row.SetHoverAmount(self, 0);
        ECS.Anim.Run(self, {
            key = "hover",
            setter = function(target, value) ECS.Row.SetHoverAmount(target, value) end,
            from = 0, to = 1,
            duration = C.HOVER_DURATION,
            easing = "quadOut",
        });
        -- the slide DOES start from wherever it currently is, so a fast in/out
        -- cannot snap the row back to a stale starting value
        ECS.Anim.Run(self, {
            key = "slide",
            setter = function(target, value) ECS.Row.SetOffsetX(target, value) end,
            from = ECS.Row.GetOffsetX(self), to = C.HOVER_SLIDE,
            duration = C.HOVER_DURATION,
            easing = "quadOut",
        });
        if ( U.driver ) then U.driver:Show() end;
    end);

    button:HookScript("OnLeave", function(self)
        ECS.Row.SetHovered(self, false);
        ECS.Row.SetHoverAmount(self, 1);
        ECS.Anim.Run(self, {
            key = "hover",
            setter = function(target, value) ECS.Row.SetHoverAmount(target, value) end,
            from = 1, to = 0,
            duration = C.HOVER_DURATION,
            easing = "quadOut",
        });
        ECS.Anim.Run(self, {
            key = "slide",
            setter = function(target, value) ECS.Row.SetOffsetX(target, value) end,
            from = ECS.Row.GetOffsetX(self), to = 0,
            duration = C.HOVER_DURATION,
            easing = "quadOut",
        });
    end);

    return true;
end

function U.Reset()
    U.built = false;
    U.parent = nil;
    U.realm = nil;
    U.search = nil;
    U.tooltip = nil;
    U.overlay = nil;
    U.driver = nil;
    U.notesEditor = nil;
    U.dragDriver = nil;
    U.status = nil;
    U.emptyState = nil;
end
