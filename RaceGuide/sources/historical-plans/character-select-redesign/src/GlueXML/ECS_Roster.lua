--[[ ECS_Roster.lua -------------------------------------------------------------
    Esteria Character Select - the scrolling roster (spec 3, 5, 6, 9, 10, 20, 25,
    29, 30).

    STRUCTURE, and why it looks like this:

      * The row buttons already exist in CharacterSelect.xml and are SIBLINGS of
        the scroll frame, not children of the scroll child. That is a re-windowing
        virtual list: SetVerticalScroll moves nothing visually; the fixed pool is
        re-pointed at a different slice of the data. ECS keeps that shape because
        it is what "100 characters with 8 frames" already means here.

      * The existing code offsets by raw server index. With a custom order and a
        search filter that stops being true, so this layer offsets by VISUAL
        position and resolves through ECS_Order.visible[]. button:SetID() still
        carries the real index, so every existing action keeps working.

      * All geometry maths is pure (ComputeLayout / SlotForY / ClampOffset) so it
        can be verified headlessly, including at resolutions and row counts that
        would be tedious to reproduce by hand in the client.

    Lua 5.1 only. No frame work at file scope.
------------------------------------------------------------------------------ ]]

ECS = ECS or {};
ECS.Roster = ECS.Roster or {};

local R = ECS.Roster;
local C = ECS.Const;
local O = ECS.Order;

-- ---------------------------------------------------------------- state
R.offset   = R.offset or 0;      -- 0-based visual index of the first visible row
R.selected = R.selected or nil;  -- REAL index of the selected character
R.drag     = R.drag or nil;      -- { button, fromVisual, toVisual, y0, armed }
R.pool     = R.pool or {};       -- array of row buttons, built once
R.rowFrame = R.rowFrame or nil;  -- the frame the pool lives in
R.layoutParent = R.layoutParent or nil; -- screen frame that owns the roster geometry
R.onReordered = R.onReordered;   -- callback(visualFrom, visualTo) for persistence
R.onSelected  = R.onSelected;    -- callback(realIndex)

-- ---------------------------------------------------------------- pure geometry
-- spec 29: derive everything from the ACTUAL viewport rather than assuming
-- 1920x1080. Returns a table so callers can inspect it in tests.
function R.ComputeLayout(viewportHeight, rowHeight, buffer)
    viewportHeight = tonumber(viewportHeight) or C.VIEWPORT_HEIGHT;
    rowHeight      = tonumber(rowHeight) or C.ROW_HEIGHT;
    buffer         = tonumber(buffer) or 2;

    if ( rowHeight <= 0 ) then
        rowHeight = C.ROW_HEIGHT;
    end
    if ( viewportHeight < 0 ) then
        viewportHeight = 0;
    end

    -- rows needed to fill the viewport, plus a small buffer so a row sliding in
    -- during a scroll or drag has somewhere to live
    local slots = math.ceil(viewportHeight / rowHeight) + buffer;
    if ( slots < 1 ) then
        slots = 1;
    end

    return {
        viewportHeight = viewportHeight,
        rowHeight      = rowHeight,
        buffer         = buffer,
        slots          = slots,
    };
end

-- Highest legal 0-based offset for a given number of visible rows.
function R.MaxOffset(visibleCount, layout)
    visibleCount = tonumber(visibleCount) or 0;
    layout = layout or R.ComputeLayout();
    local maxOffset = visibleCount - layout.viewportHeight / layout.rowHeight;
    maxOffset = math.ceil(maxOffset);
    if ( maxOffset < 0 ) then
        maxOffset = 0;
    end
    return maxOffset;
end

-- The offset is a whole row index, ALWAYS.
--
-- It doubles as the visual position ECS.Row binding uses (`visual = offset + slot`)
-- and as the argument to ECS.Order.RealIndexAt, which indexes `O.visible[pos]`
-- directly - so a fractional offset does not round, it yields nil and hides every
-- row. Flooring here makes that invariant hold for every caller rather than
-- relying on each of them to pass an integer.
function R.ClampOffset(offset, visibleCount, layout)
    offset = tonumber(offset) or 0;
    if ( offset < 0 ) then
        return 0;
    end
    local maximum = R.MaxOffset(visibleCount, layout);
    offset = math.floor(offset);
    if ( offset > maximum ) then
        return maximum;
    end
    return offset;
end

-- spec 10: which visual slot does a pointer at `y` (relative to the top of the
-- roster) land on? Returns the 1-based visual position, clamped into range.
function R.SlotForY(y, layout, visibleCount)
    layout = layout or R.ComputeLayout();
    y = tonumber(y) or 0;
    visibleCount = tonumber(visibleCount) or O.VisibleCount();

    local slot = math.floor(y / layout.rowHeight) + 1;
    if ( slot < 1 ) then
        slot = 1;
    end
    local visibleSlots = math.max(1, math.ceil(layout.viewportHeight / layout.rowHeight));
    if ( slot > visibleSlots ) then
        slot = visibleSlots;
    end

    local offset = R.offset or 0;
    local visual = offset + slot;

    if ( visibleCount > 0 and visual > visibleCount ) then
        visual = visibleCount;
    end
    if ( visual < 1 ) then
        visual = 1;
    end
    return visual;
end

-- NOTE: there is deliberately no wheel helper here. The scroll frame's
-- OnMouseWheel is owned by the stock glue (`CharacterSelect_ScrollBy`), which
-- already routes through UpdateCharacterList and therefore through ECS. A
-- fractional, ECS-side wheel delta is what used to blank the roster - see the
-- scrolling note in ECS_Integrate.lua.

-- ---------------------------------------------------------------- pool
-- The row buttons are created by CharacterSelect.xml and looked up by name,
-- because the live Freeborn wrapper depends on those exact names.
function R.RowName(index)
    return "CharSelectCharacterButton" .. tostring(index)
end

function R.BuildPool(parent, slots)
    R.pool = {};
    R.rowFrame = parent;

    for index = 1, slots do
        local button = _G[R.RowName(index)];
        if ( button ) then
            ECS.Row.Build(button);
            R.pool[#R.pool + 1] = button;
        end
    end
    return R.pool;
end

-- ---------------------------------------------------------------- pointer
-- Convert the raw cursor position into a Y offset measured DOWN from the top of
-- the roster.
--
-- Raw GetCursorPosition() is screen space. With the ECS layout parent, convert
-- from the screen top and subtract the same ROSTER_TOP used by row placement.
--
-- Returns nil when the geometry is unavailable, so the caller can fall back
-- rather than drag against a wrong coordinate.
function R.CursorOffsetY()
    local pool = R.pool or {};
    local anchor = pool[1];
    if ( not anchor or type(GetCursorPosition) ~= "function" ) then
        return nil;
    end
    local parent = R.layoutParent;
    local topInset = C.ROSTER_TOP;
    if ( not parent ) then
        parent = anchor:GetParent();
        topInset = 0;
    end
    if ( not parent or not parent.GetTop ) then
        return nil;
    end

    local okTop, top = pcall(parent.GetTop, parent);
    if ( not okTop or type(top) ~= "number" ) then
        return nil;
    end

    local okCursor, _, cursorY = pcall(GetCursorPosition);
    if ( not okCursor or type(cursorY) ~= "number" ) then
        return nil;
    end

    -- GetCursorPosition is bottom-left origin; convert from screen top to the
    -- roster top, including the configured gap below the chrome.
    return top - topInset - cursorY;
end

-- Re-anchor ONE row below the realm/search chrome, with its current hover offset.
-- The button remains a child of CharacterSelectCharacterFrame to preserve stock
-- visibility/click behavior, but its visual anchor is screen-relative.
function R.ApplyRowOffset(button)
    if ( not button or not button.SetPoint ) then
        return false;
    end
    local rowY = button.__ecsRowY or 0;
    local offset = 0;
    if ( ECS.Row and ECS.Row.GetOffsetX ) then
        offset = ECS.Row.GetOffsetX(button) or 0;
    end
    if ( button.ClearAllPoints ) then button:ClearAllPoints() end
    if ( R.layoutParent ) then
        button:SetPoint("TOPLEFT", R.layoutParent, "TOPRIGHT",
            -C.ROSTER_RIGHT - C.ROSTER_WIDTH + offset, -C.ROSTER_TOP - rowY);
    else
        button:SetPoint("TOPLEFT", offset, -rowY);
    end
    return true;
end

function R.SetLayoutParent(parent)
    R.layoutParent = parent;
    local pool = R.pool or {};
    for index = 1, #pool do
        R.ApplyRowOffset(pool[index]);
    end
    return parent ~= nil;
end

function R.PoolSize()
    return #(R.pool or {});
end

-- ---------------------------------------------------------------- refresh
-- Re-point every pooled row at the current slice of the visual order.
-- Only ever called on invalidation (spec 22, 32) - never per frame.
function R.Refresh()
    if ( not ECS.Row ) then
        return 0;
    end

    local pool = R.pool or {};
    local visibleCount = O.VisibleCount();
    local layout = R.ComputeLayout(R.ViewportHeight(), R.RowHeight());

    R.offset = R.ClampOffset(R.offset, visibleCount, layout);

    local bound = 0;
    for slot = 1, #pool do
        local button = pool[slot];
        local visual = R.offset + slot;
        local realIndex = O.RealIndexAt(visual);
        local character = realIndex and O.characters[realIndex] or nil;

        if ( character ) then
            -- position the row by slot, including any hover-slide offset
            button.__ecsRowY = (slot - 1) * layout.rowHeight;
            R.ApplyRowOffset(button);

            ECS.Row.Update(button, character, {
                selected = (R.selected ~= nil and realIndex == R.selected),
                hovered  = ECS.Row.IsHovered(button),
                dragging = (R.drag ~= nil and R.drag.button == button),
            });
            bound = bound + 1;
        else
            button.__ecsRowY = (slot - 1) * layout.rowHeight;
            R.ApplyRowOffset(button);
            ECS.Row.Reset(button);
            button:Hide();
        end
    end

    -- The XML owns ten stock buttons, but the manager viewport is eight rows.
    -- Keep the two overflow buttons hidden so the stock list cannot leak rows
    -- below the virtualized window; scrolling rebinds the eight pooled buttons.
    for slot = #pool + 1, (C.STOCK_ROW_COUNT or #pool) do
        local button = _G[R.RowName(slot)];
        if ( button ) then
            if ( ECS.Row.SuppressStockRegions ) then
                pcall(ECS.Row.SuppressStockRegions, button);
            end
            if ( button.Hide ) then button:Hide(); end
        end
    end

    R.SyncScrollbar(visibleCount, layout);
    return bound;
end

-- ---------------------------------------------------------------- viewport
-- Overridable so tests (and unusual resolutions) can inject sizes.
function R.ViewportHeight()
    local frame = R.scrollFrame;
    if ( frame and frame.GetHeight ) then
        local height = frame:GetHeight();
        if ( height and height > 0 ) then
            return height;
        end
    end
    return C.VIEWPORT_HEIGHT;
end

function R.RowHeight()
    return C.ROW_HEIGHT;
end

function R.SetScrollFrame(frame)
    R.scrollFrame = frame;
end

function R.GetOffset()
    return R.offset;
end

function R.SetOffset(offset)
    local visibleCount = O.VisibleCount();
    local layout = R.ComputeLayout(R.ViewportHeight(), R.RowHeight());
    local clamped = R.ClampOffset(offset, visibleCount, layout);
    if ( clamped == R.offset ) then
        R.Refresh();
        return false;
    end
    R.offset = clamped;
    R.Refresh();
    return true;
end

-- Scroll frame callback: `position` is in pixels from the top of the content.
function R.OnVerticalScroll(position)
    if ( R.syncingScroll ) then
        return false;
    end
    local layout = R.ComputeLayout(R.ViewportHeight(), R.RowHeight());
    local offset = math.floor((tonumber(position) or 0) / layout.rowHeight);
    return R.SetOffset(offset);
end

-- Mirror our offset onto the native scrollbar so the two cannot desync.
function R.SyncScrollbar(visibleCount, layout)
    local frame = R.scrollFrame;
    if ( not frame ) then
        return;
    end
    layout = layout or R.ComputeLayout(R.ViewportHeight(), R.RowHeight());
    visibleCount = visibleCount or O.VisibleCount();

    local maxOffset = R.MaxOffset(visibleCount, layout);
    local contentHeight = layout.viewportHeight + maxOffset * layout.rowHeight;
    local select = _G.CharacterSelect;
    if ( select ) then
        select.scrollMax = maxOffset;
    end

    local child = frame.GetScrollChild and frame:GetScrollChild();
    if ( child and child.SetHeight ) then
        child:SetHeight(contentHeight);
    end
    if ( frame.SetVerticalScroll ) then
        -- Apply the offset under the STOCK's re-entrancy guard.
        --
        -- SetVerticalScroll fires OnVerticalScroll synchronously, and
        -- CharacterSelect_OnVerticalScroll only returns early when
        -- `CharacterSelect.scrollUpdating` is set - the same flag the stock
        -- CharacterSelect_ApplyScrollOffset uses around its own call. ECS used to
        -- set only its own R.applyingScroll flag, which NOTHING read, so the guard
        -- guarded nothing and our own scroll re-entered the stock path:
        --
        --   SetVerticalScroll -> CharacterSelect_OnVerticalScroll ->
        --   CharacterSelect_SetScrollOffset -> (when the clamped value differs from
        --   the stock scrollOffset) CharacterSelect_RefreshVisibleList ->
        --   UpdateCharacterList, which rebinds the rows from SERVER order. ECS's
        --   own I.applying guard then suppressed the re-skin that would have fixed
        --   them, so the roster was left showing stock-bound characters.
        --
        -- The clamped value differs whenever a search filter shrinks the visible
        -- count while the roster is scrolled down: ECS clamps to the filtered
        -- maximum, stock had clamped to the full-roster one. Skipping the glue
        -- helper is safe - it only sets the scrollbar widget's value and toggles its
        -- arrow buttons, and SetVerticalScroll already updates the scrollbar; stock
        -- skips it in exactly the same way.
        local select = _G.CharacterSelect;
        local previousGuard = nil;
        local previousEcsGuard = R.syncingScroll;
        if ( select ) then
            previousGuard = select.scrollUpdating;
            select.scrollUpdating = true;
        end
        R.syncingScroll = true;
        local ok, reason = pcall(frame.SetVerticalScroll, frame, (R.offset or 0) * layout.rowHeight);
        R.syncingScroll = previousEcsGuard;
        if ( select ) then
            select.scrollUpdating = previousGuard;   -- restore, do not clear
        end
        if ( not ok ) then
            error(reason);
        end
    end
    if ( frame.UpdateScrollChildRect ) then
        frame:UpdateScrollChildRect();
    end
end

-- ---------------------------------------------------------------- selection
function R.GetSelected()
    return R.selected;
end

-- Select by REAL index (never by visual position) so the caller cannot pass the
-- wrong space by accident.
function R.Select(realIndex)
    if ( realIndex == nil ) then
        return false;
    end
    if ( R.selected == realIndex ) then
        return false;
    end
    R.selected = realIndex;
    R.Refresh();
    if ( R.onSelected ) then
        pcall(R.onSelected, realIndex);
    end
    return true;
end

function R.ClearSelection()
    if ( R.selected == nil ) then
        return false;
    end
    R.selected = nil;
    R.Refresh();
    return true;
end

-- Clicking a row selects the character that row currently displays.
function R.HandleRowClick(button)
    if ( not button ) then
        return nil;
    end
    local realIndex = button.GetID and button:GetID();
    if ( not realIndex ) then
        return nil;
    end
    R.Select(realIndex);
    return realIndex;
end

-- spec 5: the selection must never point at a character the roster cannot see.
-- When a filter hides it we KEEP the real selection (spec 8) and simply do not
-- render a selected row.
function R.IsSelectionVisible()
    if ( not R.selected ) then
        return false;
    end
    return O.VisualPosOf(R.selected) ~= nil;
end

-- ------------------------------------------------------------------ drag/drop
function R.IsDragging()
    return R.drag ~= nil and R.drag.armed == true;
end

-- spec 10 step 1-2: a press arms a potential drag; it only becomes a real drag
-- once the pointer travels past the threshold, so a plain click never reorders.
--
-- `pointerY` must be the ROSTER-RELATIVE distance from the top (see
-- CursorOffsetY). x is only used for the threshold; the drop target is vertical.
function R.BeginPress(button, x, pointerY)
    if ( not button ) then
        return false;
    end
    local realIndex = button.GetID and button:GetID();
    if ( not realIndex ) then
        return false;
    end
    R.drag = {
        button = button,
        realIndex = realIndex,
        fromVisual = O.VisualPosOf(realIndex),
        toVisual = O.VisualPosOf(realIndex),
        x0 = tonumber(x) or 0,
        y0 = tonumber(pointerY) or 0,
        armed = false,
    };
    return true;
end

-- Returns true once the press has become an actual drag.
function R.UpdatePress(x, pointerY)
    local drag = R.drag;
    if ( not drag ) then
        return false;
    end
    x = tonumber(x) or 0;
    pointerY = tonumber(pointerY) or drag.y0

    if ( not drag.armed ) then
        local dx, dy = x - drag.x0, pointerY - drag.y0;
        if ( (dx * dx + dy * dy) < (C.DRAG_THRESHOLD * C.DRAG_THRESHOLD) ) then
            return false;
        end
        drag.armed = true;
    end

    local layout = R.ComputeLayout(R.ViewportHeight(), R.RowHeight());
    drag.toVisual = R.SlotForY(pointerY, layout, O.VisibleCount());
    -- reflect the pending drop on the rows so the user sees the gap open
    R.Refresh();
    return true;
end

-- Commit the drop. Returns true when the order actually changed.
function R.EndPress()
    local drag = R.drag;
    R.drag = nil;
    if ( not drag ) then
        return false;
    end
    if ( not drag.armed ) then
        R.Refresh();
        return false;   -- it was a click, not a drag
    end

    local changed = false;
    if ( ECS.Order.MoveCharacter and drag.fromVisual and drag.toVisual
        and drag.fromVisual ~= drag.toVisual ) then
        changed = ECS.Order.MoveCharacter(drag.fromVisual, drag.toVisual) and true or false;
    end

    -- the selection follows the character, not the slot
    R.Refresh();
    if ( changed and R.onReordered ) then
        pcall(R.onReordered, drag.fromVisual, drag.toVisual);
    end
    return changed;
end

function R.CancelPress()
    local had = R.drag ~= nil;
    R.drag = nil;
    R.Refresh();
    return had;
end

function R.GetDragTarget()
    if ( not R.drag ) then
        return nil;
    end
    return R.drag.toVisual;
end

-- ---------------------------------------------------------------- deletion
-- spec 20: fade, shrink, then collapse and refresh. The character is only
-- removed from the VISUAL list here; the caller must confirm the server actually
-- deleted it before rebuilding the data.
function R.AnimateDelete(button, onComplete)
    if ( not button ) then
        if ( onComplete ) then pcall(onComplete) end
        return false;
    end
    local anim = ECS.Anim;
    if ( not anim or not anim.Fade ) then
        if ( onComplete ) then pcall(onComplete) end
        return false;
    end

    local startAlpha = button.GetAlpha and button:GetAlpha() or 1;
    anim.Fade(button, 0, startAlpha, C.DELETE_DURATION, function()
        if ( onComplete ) then pcall(onComplete) end
    end);
    return true;
end

-- ---------------------------------------------------------------- lifecycle
function R.Reset()
    R.offset = 0;
    R.selected = nil;
    R.drag = nil;
    R.pool = {};
    R.scrollFrame = nil;
    R.rowFrame = nil;
    R.layoutParent = nil;
end
