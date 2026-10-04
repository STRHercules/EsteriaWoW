--[[ ECS_Row.lua ----------------------------------------------------------------
    Esteria Character Select - one roster row (spec 3, 4, 5, 6, 13, 25, 27, 33).

    DESIGN: DECORATE, DO NOT RECREATE.

    CharacterSelect.xml already defines the ten row buttons, and the live
    Freeborn wrapper (CharacterCreate.lua CharacterFreeborn_ApplyBadges) reaches
    into them by name. So ECS does not build new rows -- it decorates the existing
    ones and then only ever rebinds data. That satisfies the pooling requirement
    (spec 25) for free and keeps both existing contracts intact:

      * the button keeps its name                 CharSelectCharacterButton<N>
      * a child texture named ...FactionIcon      still exists
      * button:GetID()                            still returns the REAL index

    Every region ECS adds is created once, on first Build, and reused thereafter.
    Row:Reset is the single place that clears per-character state, so one
    character's data can never flash on another character's row when the pool
    recycles (spec 25).

    Lua 5.1 only. No frame work happens at file scope.
------------------------------------------------------------------------------ ]]

ECS = ECS or {};
ECS.Row = ECS.Row or {};

local R = ECS.Row;
local C = ECS.Const;
local S = ECS.Schema;

-- ---------------------------------------------------------------- state model
-- Visual state per row. Kept out of the frame table proper so it is easy to reset.
local function State(button)
    if ( not button.__ecs ) then
        button.__ecs = {
            built     = false,
            character = nil,
            selected  = false,
            hovered   = false,
            dragging  = false,
            offsetX   = 0,
            highlight = 0,
            hoverAmount = 0,   -- 0..1, animated by ECS_UI for a smooth hover
        };
    end
    return button.__ecs;
end

R.State = State;

-- ---------------------------------------------------------------- fonts
-- Glue FontStrings need an explicit font object or they may render nothing. We
-- try the glue-specific styles first (matching the surrounding screen) and fall
-- back to the frame styles, all pcall-guarded so a missing global is harmless.
local FONT_CANDIDATES = {
    "GlueFontHighlightSmall",
    "GlueFontNormalSmall",
    "GameFontNormalSmall",
    "GameFontHighlightSmall",
};

local function ApplyFont(fontString, size)
    if ( not fontString or not fontString.SetFontObject ) then
        return false;
    end
    for index = 1, #FONT_CANDIDATES do
        local name = FONT_CANDIDATES[index];
        if ( _G[name] ) then
            local ok = pcall(fontString.SetFontObject, fontString, _G[name]);
            if ( ok ) then
                if ( size and fontString.SetFont and _G[name].GetFont ) then
                    local path, _, flags = _G[name]:GetFont();
                    if ( path ) then
                        pcall(fontString.SetFont, fontString, path, size, flags or "");
                    end
                end
                return true;
            end
        end
    end
    return false;
end

R.ApplyFont = ApplyFont;

local function ApplyRowArtScale(texture)
    if ( not texture or not texture.SetTexCoord ) then return end
    local inset = (1 - 1 / C.ROW_ART_SCALE) / 2;
    texture:SetTexCoord(inset, 1 - inset, inset, 1 - inset);
end

-- ---------------------------------------------------------------- build
-- One-time decoration. Idempotent: calling it twice must not double up regions.
function R.Build(button)
    if ( not button ) then
        return nil;
    end
    local state = State(button);
    if ( state.built ) then
        return button;
    end
    state.built = true;

    -- The stock row art is a red slab; drop it entirely.
    if ( button.SetNormalTexture ) then
        local normal = button:GetNormalTexture();
        if ( normal and normal.SetAlpha ) then
            normal:SetAlpha(0);
        end
    end
    if ( button.SetHighlightTexture ) then
        local highlight = button:GetHighlightTexture();
        if ( highlight and highlight.SetAlpha ) then
            highlight:SetAlpha(0);
        end
    end

    -- Default and interaction art sit above the transparent surface and below row
    -- content. The upper plate is reserved for hover/selection over the idle grey.
    local tint = button:CreateTexture(nil, "BACKGROUND");
    tint:SetTexture(C.TEX.blank);
    tint:SetVertexColor(1, 1, 1, 0);
    state.tint = tint;
    if ( tint.SetAllPoints ) then tint:SetAllPoints(button) end

    local idleArt = button:CreateTexture(nil, "BACKGROUND", nil, 1);
    state.idleArt = idleArt;
    idleArt:SetTexture(C.TEX.idlePlate);
    if ( idleArt.SetAllPoints ) then idleArt:SetAllPoints(button) end
    ApplyRowArtScale(idleArt);

    local statusArt = button:CreateTexture(nil, "BACKGROUND", nil, 2);
    state.statusArt = statusArt;
    if ( statusArt.SetAllPoints ) then statusArt:SetAllPoints(button) end
    ApplyRowArtScale(statusArt);
    statusArt:Hide();

    -- portrait (spec 4)
    local portrait = button:CreateTexture(nil, "ARTWORK");
    state.portrait = portrait
    portrait:SetSize(C.PORTRAIT_SIZE, C.PORTRAIT_SIZE);
    portrait:SetPoint("LEFT", button, "LEFT", C.PORTRAIT_INSET, 0);

    -- Supplied portrait border replaces the old procedural white placeholder.
    local portraitBorder = button:CreateTexture(nil, "OVERLAY");
    state.portraitBorder = portraitBorder;
    portraitBorder:SetTexture(C.TEX.portraitBorder);
    portraitBorder:SetSize(C.PORTRAIT_BORDER_SIZE, C.PORTRAIT_BORDER_SIZE);
    portraitBorder:SetPoint("CENTER", portrait, "CENTER", 0, 0);

    -- Small class mark overlaps the portrait's upper-right edge, as in the
    -- reference roster. Reuse the character-create class atlas and its native
    -- CLASS_ICON_TCOORDS table; unknown/custom classes safely show no mark.
    local classIcon = button:CreateTexture(nil, "OVERLAY");
    state.classIcon = classIcon;
    classIcon:SetTexture(C.TEX.classIcon);
    classIcon:SetSize(C.CLASS_ICON_SIZE, C.CLASS_ICON_SIZE);
    classIcon:SetPoint("TOPRIGHT", portrait, "TOPRIGHT", 4, 4);
    classIcon:Hide();

    -- The level is framed by the supplied border at the portrait's lower-right.
    local levelBorder = button:CreateTexture(nil, "OVERLAY");
    state.levelBorder = levelBorder;
    levelBorder:SetTexture(C.TEX.levelBorder);
    levelBorder:SetSize(C.LEVEL_BORDER_SIZE, C.LEVEL_BORDER_SIZE);
    levelBorder:SetPoint("CENTER", portrait, "BOTTOMRIGHT", -1, 3);

    local badge = button:CreateFontString(nil, "OVERLAY");
    state.badge = badge;
    badge:SetSize(C.LEVEL_BADGE, C.LEVEL_BADGE);
    badge:SetPoint("CENTER", levelBorder, "CENTER", 0, 0);
    badge:SetJustifyH("CENTER");
    if ( badge.SetJustifyV ) then badge:SetJustifyV("MIDDLE") end
    ApplyFont(badge, C.SUB_FONT_SIZE);

    -- note indicator (spec 12)
    local dot = button:CreateTexture(nil, "OVERLAY");
    state.noteDot = dot
    dot:SetTexture(C.TEX.noteDot);
    dot:SetSize(C.NOTE_DOT_SIZE, C.NOTE_DOT_SIZE);
    dot:SetPoint("TOPRIGHT", button, "TOPRIGHT", -6, -6);

    -- name / zone / optional note, matching the compact reference roster
    local name = button:CreateFontString(nil, "OVERLAY");
    state.name = name
    name:SetPoint("TOPLEFT", button, "TOPLEFT", C.TEXT_LEFT, C.NAME_TOP);
    name:SetWidth(C.TEXT_RIGHT - C.TEXT_LEFT);
    name:SetJustifyH("LEFT");
    name:SetWordWrap(false);
    if name.SetNonSpaceWrap then name:SetNonSpaceWrap(false); end
    ApplyFont(name, C.NAME_FONT_SIZE);

    local zone = button:CreateFontString(nil, "OVERLAY");
    state.zone = zone
    zone:SetPoint("TOPLEFT", button, "TOPLEFT", C.TEXT_LEFT, C.ZONE_TOP);
    zone:SetWidth(C.TEXT_RIGHT - C.TEXT_LEFT);
    zone:SetJustifyH("LEFT");
    ApplyFont(zone, C.ZONE_FONT_SIZE);

    local noteText = button:CreateFontString(nil, "OVERLAY");
    state.noteText = noteText
    noteText:SetPoint("TOPLEFT", button, "TOPLEFT", C.TEXT_LEFT, C.NOTE_TOP);
    noteText:SetWidth(C.TEXT_RIGHT - C.TEXT_LEFT);
    noteText:SetJustifyH("LEFT");
    noteText:SetWordWrap(false);
    ApplyFont(noteText, C.SUB_FONT_SIZE);
    noteText:Hide();

    -- The faction emblem slot. Reuse the existing FactionIcon child when the XML
    -- provides one, because the Freeborn wrapper looks it up by name; otherwise
    -- create it under that exact name so the wrapper finds ours.
    local emblemName = button.GetName and button:GetName();
    local emblem = nil;
    if ( emblemName ) then
        emblem = _G[emblemName .. "FactionIcon"];
    end
    if ( not emblem ) then
        emblem = button:CreateTexture(emblemName and (emblemName .. "FactionIcon") or nil, "OVERLAY");
    end
    state.emblem = emblem
    emblem:SetSize(C.EMBLEM_SIZE, C.EMBLEM_SIZE);
    emblem:SetPoint("CENTER", button, "TOPLEFT", C.EMBLEM_X, C.EMBLEM_Y);
    emblem:Hide();

    return button;
end

-- The stock row regions ECS does not inherit and must therefore suppress.
--
-- The stock UpdateCharacterList writes a COMPLETE row presentation onto every
-- populated row, and ECS replaces all of it:
--
--   * `GeneralBackground` - a 243x62 plate cut from uicharacterselectglues2x, SHOWN
--     (CharacterSelect.lua:631) at BACKGROUND sublevel 1, which is above the backdrop
--     and above ECS's own tint at sublevel 0, so it drew stock art over the ElvUI
--     surface with the selected row's accent fill underneath it.
--   * `Background` - shown at OVERLAY sublevel 2, i.e. above ECS's portrait and text.
--     The stock code never gives it a texture, so it draws nothing today; hidden
--     anyway so ECS does not silently depend on that staying true.
--   * six FontStrings - Name at (0,-8) and Level/Separator/Class at (0..30,-25), all
--     at OVERLAY and anchored to the button's TOPLEFT. OVERLAY is ABOVE ECS's
--     portrait (ARTWORK) and level with ECS's own text, so each row rendered the
--     stock name/level/class ON TOP of ECS's portrait AND alongside ECS's own
--     name/zone/note. This was the largest of the misses: it affected every row,
--     always, and no offline test could see it because the shim has no stock regions.
--
-- This runs on EVERY refresh, not once in Build: the stock pass re-writes and
-- re-shows these each time it binds a row, while Build runs only once per button.
--
-- Two stock regions are deliberately NOT suppressed:
--   * `FactionIcon` - ECS adopts that exact texture, re-anchors and resizes it, which
--     is why it keeps the name the Freeborn wrapper looks up.
--   * `CharSelectCharacterCustomize/RaceChange/FactionChange` - real buttons for a
--     pending paid service. Hiding them would silently remove a feature the player
--     has already paid for. They are anchored `TOPRIGHT` to the row's `TOPLEFT` at
--     (-15, 6), i.e. OUTSIDE the row to its left, so they do not collide with ECS's
--     layout and need no repositioning either.
local STOCK_TEXT_SUFFIXES = {
    "ButtonTextName", "ButtonTextInfo", "ButtonTextLocation",
    "ButtonTextLevel", "ButtonTextSeparator", "ButtonTextClass",
    "ButtonTextZone", "ButtonTextStatus",
};

local function SuppressStockRegion(region)
    if ( not region ) then return end
    if ( region.SetAlpha ) then region:SetAlpha(0) end
    if ( region.Hide ) then region:Hide() end
end

local function IsECSRegion(state, region)
    return region == state.tint or region == state.idleArt or region == state.statusArt or region == state.portrait
        or region == state.portraitBorder or region == state.levelBorder
        or region == state.classIcon or region == state.badge or region == state.noteDot
        or region == state.name or region == state.zone or region == state.noteText
        or region == state.emblem;
end

local function SuppressStockRegions(button)
    local name = button.GetName and button:GetName();
    if ( name ) then
        SuppressStockRegion(_G[name .. "GeneralBackground"]);
        SuppressStockRegion(_G[name .. "Background"]);

        for index = 1, #STOCK_TEXT_SUFFIXES do
            SuppressStockRegion(_G[name .. STOCK_TEXT_SUFFIXES[index]]);
        end
    end

    -- The live client has extra unnamed/name-mismatched row regions beyond the
    -- historical ButtonText* children. Suppress every non-ECS FontString/Texture
    -- too, so a later Show() cannot leave stock text or plates on top of our row.
    local state = State(button);
    if ( button.GetRegions ) then
        local regions = { button:GetRegions() };
        for index = 1, #regions do
            local region = regions[index];
            if ( region and not IsECSRegion(state, region) and region.GetObjectType ) then
                local ok, objectType = pcall(region.GetObjectType, region);
                if ( ok and (objectType == "FontString" or objectType == "Texture") ) then
                    SuppressStockRegion(region);
                end
            end
        end
    end
end

R.SuppressStockRegions = SuppressStockRegions

-- ---------------------------------------------------------------- reset
-- spec 25: a recycled row must not leak any state from its previous character.
function R.Reset(button)
    if ( not button ) then
        return nil;
    end
    local state = State(button);
    state.character = nil;
    state.selected  = false;
    state.hovered   = false;
    state.dragging  = false;
    state.offsetX   = 0;
    state.highlight = 0;
    state.hoverAmount = 0;

    if ( state.portrait ) then state.portrait:SetTexture(nil) end
    if ( state.classIcon ) then state.classIcon:SetTexture(nil); state.classIcon:Hide() end
    if ( state.name )     then state.name:SetText("") end
    if ( state.zone )     then state.zone:SetText("") end
    if ( state.noteText ) then state.noteText:SetText(""); state.noteText:Hide() end
    if ( state.badge )    then state.badge:SetText("") end
    if ( state.noteDot )  then state.noteDot:Hide() end
    if ( state.idleArt )  then state.idleArt:SetAlpha(1) end
    if ( state.statusArt ) then state.statusArt:SetTexture(nil); state.statusArt:SetAlpha(0); state.statusArt:Hide() end
    if ( state.emblem )   then state.emblem:SetTexture(nil) state.emblem:Hide() end
    if ( state.tint )     then state.tint:SetVertexColor(1, 1, 1, 0) end

    -- Keep the last valid id while the pooled row is hidden. The WoW client
    -- rejects SetID(nil), and hidden rows cannot receive actions; the next bind
    -- always replaces this id before showing the button again.
    return button;
end

-- ---------------------------------------------------------------- appearance
local function ApplyTint(button, state)
    local tint = state.tint;
    if ( not tint ) then
        return;
    end
    local drag = C.COLOUR.dragTarget;
    tint:SetVertexColor(drag[1], drag[2], drag[3], state.dragging and drag[4] or 0);
end

R.ApplyTint = ApplyTint

local function ApplyStatusArt(button, state)
    local art = state.statusArt;
    if ( not art ) then return end

    local texture, alpha = nil, 0;
    if ( state.selected ) then
        texture, alpha = C.TEX.selectedPlate, 1;
    elseif ( state.hovered or (state.hoverAmount or 0) > 0 ) then
        local character = state.character;
        local factionID = character and character.factionID;
        if ( factionID == 1 ) then
            texture = C.TEX.allianceHoverPlate;
        elseif ( factionID == 2 ) then
            texture = C.TEX.hordeHoverPlate;
        elseif ( factionID == 3 ) then
            texture = C.TEX.freebornHoverPlate;
        end
        if ( texture ) then
            alpha = math.max(0, math.min(1, state.hoverAmount or 0));
        end
    end

    if ( texture ) then
        if ( state.idleArt ) then state.idleArt:SetAlpha(1 - alpha) end
        art:SetTexture(texture);
        art:SetAlpha(alpha);
        art:Show();
    else
        if ( state.idleArt ) then state.idleArt:SetAlpha(1) end
        art:SetAlpha(0);
        art:Hide();
    end
end

local function ApplyAccent(button, state)
    -- Faction colour is an ACCENT only (spec 27): it tints the rim, never the fill.
    local character = state.character;
    local accent = C.COLOUR.border;
    if ( character and character.factionAccent ) then
        accent = character.factionAccent;
    end

    local alpha = 1;
    if ( state.selected ) then
        alpha = 1;
    elseif ( state.hovered ) then
        alpha = 0.85;
    else
        alpha = 0.55;
    end

    if ( button.SetBackdropBorderColor ) then
        button:SetBackdropBorderColor(accent[1], accent[2], accent[3], alpha);
    end
end

R.ApplyAccent = ApplyAccent

local function NameColour(character)
    local colour = character.classColour;
    if ( type(colour) ~= "table" ) then
        colour = C.COLOUR.textBright;
    end

    local red = tonumber(colour[1]);
    local green = tonumber(colour[2]);
    local blue = tonumber(colour[3]);
    if ( not red or not green or not blue ) then
        colour = C.COLOUR.textBright;
        red, green, blue = colour[1], colour[2], colour[3];
    end

    red = math.max(0, math.min(1, red));
    green = math.max(0, math.min(1, green));
    blue = math.max(0, math.min(1, blue));
    return { red, green, blue }, string.format("|cff%02x%02x%02x",
        math.floor(red * 255 + 0.5), math.floor(green * 255 + 0.5), math.floor(blue * 255 + 0.5));
end

-- ---------------------------------------------------------------- update
-- Bind one character (or nil to blank the row) and the current interaction state.
-- Only ever called from the roster's refresh, never per frame (spec 22, 32).
function R.Update(button, character, state)
    if ( not button ) then
        return nil;
    end
    R.Build(button);

    -- after Build, and on every refresh: the stock pass re-writes and re-shows its own
    -- row art and text each time it binds a row, so suppressing them once is not enough
    SuppressStockRegions(button);

    local rowState = State(button);
    if ( state ) then
        rowState.selected = state.selected and true or false;
        rowState.hovered  = state.hovered and true or false;
        rowState.dragging = state.dragging and true or false;
    end

    if ( not character ) then
        R.Reset(button);
        rowState.character = nil;
        ApplyTint(button, rowState);
        ApplyStatusArt(button, rowState);
        ApplyAccent(button, rowState);
        button:Hide();
        return button;
    end

    rowState.character = character;
    button:SetID(character.realIndex);   -- the contract the Freeborn wrapper and
                                          -- the existing click handler both rely on
    button:Show();
    ApplyStatusArt(button, rowState);

    -- portrait (spec 4)
    if ( rowState.portrait ) then
        local portrait = character.portrait or S.GetPortrait(character.raceArtKey, character.sex);
        rowState.portrait:SetTexture(portrait);   -- nil is fine: renders empty, not an error
    end
    if ( rowState.classIcon ) then
        local classIcons = _G.CLASS_ICON_TCOORDS;
        local coords = nil;
        if ( type(classIcons) == "table" and type(character.className) == "string" ) then
            coords = classIcons[string.upper(character.className)];
        end
        if ( type(coords) == "table" ) then
            rowState.classIcon:SetTexture(C.TEX.classIcon);
            rowState.classIcon:SetTexCoord(unpack(coords));
            rowState.classIcon:Show();
        else
            rowState.classIcon:Hide();
        end
    end

    -- Name is class-coloured, with the active search match highlighted (spec 8).
    if ( rowState.name ) then
        ApplyFont(rowState.name, C.NAME_FONT_SIZE);
        rowState.name:SetWidth(0);
        local classColour, classEscape = NameColour(character);
        if ( rowState.name.SetTextColor ) then
            rowState.name:SetTextColor(classColour[1], classColour[2], classColour[3]);
        end
        if ( ECS.Search and ECS.Search.IsActive and ECS.Search.IsActive() ) then
            local before, match, after = ECS.Search.Split(character.name or "");
            if ( match ~= "" ) then
                rowState.name:SetText(classEscape .. before
                    .. "|r|cff" .. "fd7a2b" .. match .. "|r" .. classEscape .. after .. "|r");
            else
                rowState.name:SetText(character.name or "");
            end
        else
            rowState.name:SetText(character.name or "");
        end
        local available = C.TEXT_RIGHT - C.TEXT_LEFT;
        local natural = rowState.name:GetStringWidth();
        if natural > available then
            ApplyFont(rowState.name, math.max(9,C.NAME_FONT_SIZE * available / natural));
        end
        rowState.name:SetWidth(available);
    end

    if ( rowState.zone ) then
        rowState.zone:SetText(character.zone or C.FALLBACK_ZONE);
        local dim = C.COLOUR.textDim;
        if ( rowState.zone.SetTextColor ) then
            rowState.zone:SetTextColor(dim[1], dim[2], dim[3]);
        end
    end

    local note = character.note;
    if ( type(note) ~= "string" or note == "" ) then
        note = nil;
    end
    if ( rowState.noteText ) then
        rowState.noteText:SetText(note or "");
        if ( note ) then
            local dim = C.COLOUR.textDim;
            if ( rowState.noteText.SetTextColor ) then
                rowState.noteText:SetTextColor(dim[1], dim[2], dim[3]);
            end
            rowState.noteText:Show();
        else
            rowState.noteText:Hide();
        end
    end

    -- The level badge carries level without repeating it in the text rows.
    local levelText = C.LEVEL_UNKNOWN;
    if ( character.level ) then
        levelText = tostring(character.level);
    end
    if ( rowState.badge ) then
        rowState.badge:SetText(levelText);
    end

    -- note indicator (spec 12)
    if ( rowState.noteDot ) then
        if ( note ) then
            rowState.noteDot:Show();
        else
            rowState.noteDot:Hide();
        end
    end

    -- faction emblem; the Freeborn wrapper may override this afterwards (spec 14)
    if ( rowState.emblem ) then
        if ( character.factionEmblem ) then
            rowState.emblem:SetTexture(character.factionEmblem);
            rowState.emblem:Show();
        else
            rowState.emblem:Hide();
        end
    end

    ApplyTint(button, rowState);
    ApplyAccent(button, rowState);
    return button;
end

-- ---------------------------------------------------------------- interaction
function R.SetSelected(button, selected)
    if ( not button ) then return false end
    local rowState = State(button);
    if ( rowState.selected == (selected and true or false) ) then
        return false;
    end
    rowState.selected = selected and true or false;
    ApplyTint(button, rowState);
    ApplyStatusArt(button, rowState);
    ApplyAccent(button, rowState);
    return true;
end

function R.SetHovered(button, hovered)
    if ( not button ) then return false end
    local rowState = State(button);
    local target = hovered and true or false;
    if ( rowState.hovered == target and rowState.hoverAmount == (target and 1 or 0) ) then
        return false;
    end
    rowState.hovered = target;
    -- snapped by default; ECS_UI animates hoverAmount instead of calling this
    rowState.hoverAmount = target and 1 or 0;
    ApplyTint(button, rowState);
    ApplyStatusArt(button, rowState);
    ApplyAccent(button, rowState);
    return true;
end

-- Animated hover (spec 6): ECS_UI tweens this 0..1 so the surface eases in and
-- out. Kept separate from SetHovered so the hovered FLAG and the visual AMOUNT
-- cannot disagree - the flag decides, the amount only modulates.
function R.SetHoverAmount(button, amount)
    if ( not button ) then return false end
    local rowState = State(button);
    amount = tonumber(amount) or 0;
    if ( amount < 0 ) then amount = 0 end
    if ( amount > 1 ) then amount = 1 end
    if ( rowState.hoverAmount == amount ) then
        return false;
    end
    rowState.hoverAmount = amount;
    ApplyTint(button, rowState);
    ApplyStatusArt(button, rowState);
    return true;
end

function R.GetHoverAmount(button)
    if ( not button ) then return 0 end
    return State(button).hoverAmount or 0;
end

function R.IsSelected(button)
    return button and State(button).selected or false;
end

function R.IsHovered(button)
    return button and State(button).hovered or false;
end

function R.GetCharacter(button)
    if ( not button ) then return nil end
    return State(button).character;
end

-- Horizontal nudge used for the hover slide (spec 6). Applied through a single
-- stored offset so it cannot fight the roster's slot positioning, and pushed to
-- the roster so only this one row is re-anchored rather than the whole pool.
function R.SetOffsetX(button, offset)
    if ( not button ) then return false end
    offset = tonumber(offset) or 0;
    local rowState = State(button);
    if ( rowState.offsetX == offset ) then
        return false;
    end
    rowState.offsetX = offset;

    local roster = ECS.Roster;
    if ( roster and roster.ApplyRowOffset ) then
        pcall(roster.ApplyRowOffset, button);
    end
    return true;
end

function R.GetOffsetX(button)
    if ( not button ) then return 0 end
    return State(button).offsetX;
end
