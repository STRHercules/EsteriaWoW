--[[ ECS_Tooltip.lua ------------------------------------------------------------
    Esteria Character Select - the character detail display (spec 13, 33).

    Two responsibilities, both deliberately testable without a frame:

      * BuildLines   - turn a CharacterData into the rows of text to show, with
                       the same fallbacks the roster uses, so an unknown race or a
                       nil zone produces sensible copy instead of a blank panel.
      * ComputeAnchor- place the panel near the cursor WITHOUT letting it run off
                       the screen. Edge clamping is pure arithmetic, so every
                       corner case is verifiable rather than eyeballed at one
                       resolution.

    The hover delay is an accumulated timer stepped by the caller, not an OnUpdate
    of its own, so it costs nothing while the pointer is still.

    Lua 5.1 only. No frame work at file scope.
------------------------------------------------------------------------------ ]]

ECS = ECS or {};
ECS.Tooltip = ECS.Tooltip or {};

local T = ECS.Tooltip;
local C = ECS.Const;
local S = ECS.Schema;

T.PAD          = 10;   -- gap between cursor and panel
T.EDGE_MARGIN  = 6;    -- never touch the very edge of the screen
T.MIN_WIDTH    = 170;
T.MAX_WIDTH    = 300;

-- ---------------------------------------------------------------- content
-- spec 3 / 13: the same hierarchy the row uses, plus the faction and the note.
function T.BuildLines(character)
    if ( type(character) ~= "table" ) then
        return {};
    end

    local lines = {};

    lines[#lines + 1] = {
        text  = character.name or "",
        style = "title",
    };

    local level = character.level and tostring(character.level) or C.LEVEL_UNKNOWN;
    local race  = character.raceName or C.FALLBACK_RACE_NAME;
    local klass = character.className or C.FALLBACK_CLASS_NAME;

    lines[#lines + 1] = {
        text  = level .. "  " .. race .. "  " .. klass,
        style = "normal",
        -- class colour as a secondary accent (spec 27)
        colour = character.classColour,
    };

    -- zone: omitted entirely when there is nothing to say, rather than an empty row
    if ( type(character.zone) == "string" and character.zone ~= "" ) then
        lines[#lines + 1] = { text = character.zone, style = "dim" };
    end

    local faction = character.factionName or C.NEUTRAL_FACTION;
    lines[#lines + 1] = {
        text   = faction,
        style  = "dim",
        colour = character.factionAccent,
    };

    -- an unknown race is worth surfacing rather than silently mislabelling
    if ( character.raceKnown == false ) then
        lines[#lines + 1] = { text = "Unrecognised race", style = "dim" };
    end

    if ( type(character.note) == "string" and character.note ~= "" ) then
        lines[#lines + 1] = { text = character.note, style = "note" };
    end

    return lines;
end

-- ---------------------------------------------------------------- geometry
-- Place a panel of width x height near (anchorX, anchorY), keeping it fully
-- on screen. anchorX/anchorY are the cursor; the panel prefers to sit below and
-- to the right of it and flips when there is no room.
--
-- Returns x, y, flippedX, flippedY
function T.ComputeAnchor(anchorX, anchorY, width, height, screenWidth, screenHeight)
    anchorX = tonumber(anchorX) or 0;
    anchorY = tonumber(anchorY) or 0;
    width   = tonumber(width) or T.MIN_WIDTH;
    height  = tonumber(height) or 0;
    screenWidth  = tonumber(screenWidth)  or 1024;
    screenHeight = tonumber(screenHeight) or 768;

    local margin = T.EDGE_MARGIN;

    local x = anchorX + T.PAD;
    local flippedX = false;
    if ( x + width > screenWidth - margin ) then
        -- flip to the left of the cursor
        x = anchorX - width - T.PAD;
        flippedX = true;
    end

    local y = anchorY + T.PAD;
    local flippedY = false;
    if ( y + height > screenHeight - margin ) then
        -- Only move above the cursor when there is no room below it.
        y = anchorY - height - T.PAD;
        flippedY = true;
    end

    -- final clamp: on a very small screen a flip may still not fit, and running
    -- off the edge is worse than overlapping the cursor
    if ( x < margin ) then x = margin; end
    if ( y < margin ) then y = margin; end
    if ( x + width > screenWidth - margin ) then
        x = screenWidth - width - margin;
        if ( x < margin ) then x = margin; end
    end
    if ( y + height > screenHeight - margin ) then
        y = screenHeight - height - margin;
        if ( y < margin ) then y = margin; end
    end

    return x, y, flippedX, flippedY;
end

-- Estimate the panel size from the content, so the anchor maths has something to
-- work with before any frame is measured. Rough, and deliberately so: the caller
-- replaces it with the real size once the frame exists.
function T.EstimateSize(lines)
    local count = (type(lines) == "table") and #lines or 0;
    local widest = 0;
    for index = 1, count do
        local text = lines[index] and lines[index].text or "";
        if ( #text > widest ) then widest = #text; end
    end

    local width = widest * 6 + T.PAD * 2;
    if ( width < T.MIN_WIDTH ) then width = T.MIN_WIDTH; end
    if ( width > T.MAX_WIDTH ) then width = T.MAX_WIDTH; end

    local height = count * 14 + T.PAD * 2;
    return width, height;
end

-- ---------------------------------------------------------------- hover timer
-- A single accumulated timer rather than an OnUpdate per row. The caller steps it
-- from whatever driver is already running.
function T.BeginHover(character)
    if ( not character ) then
        -- No hovered row means no tooltip at all. Cancelling only the PENDING one
        -- would leave an already-visible panel stranded on screen after the
        -- pointer moved away, which is exactly the stale-panel bug.
        T.Hide();
        return false;
    end
    T.pending = character;
    T.elapsed = 0;
    return true;
end

-- Returns true on the step that makes the tooltip visible.
function T.Update(dt)
    if ( not T.pending ) then
        return false;
    end
    if ( T.visible ) then
        return false;
    end
    dt = tonumber(dt) or 0;
    if ( dt < 0 ) then dt = 0; end

    T.elapsed = (T.elapsed or 0) + dt;
    if ( T.elapsed >= C.TOOLTIP_DELAY ) then
        T.visible = true;
        T.character = T.pending;
        return true;
    end
    return false;
end

-- Pointer left a row without settling: drop the pending tooltip.
function T.Cancel()
    T.pending = nil;
    T.elapsed = 0;
    return true;
end

function T.Hide()
    local wasVisible = T.visible and true or false;
    T.pending = nil;
    T.elapsed = 0;
    T.visible = false;
    T.character = nil;
    return wasVisible;
end

function T.IsVisible()
    return T.visible and true or false;
end

function T.GetCharacter()
    return T.character;
end

-- spec 13: the panel must update when the selection or the hovered row changes,
-- rather than showing stale details.
function T.Refresh(character)
    if ( not T.visible ) then
        return false;
    end
    T.character = character;
    return true;
end

function T.Reset()
    T.pending = nil;
    T.elapsed = 0;
    T.visible = false;
    T.character = nil;
end
