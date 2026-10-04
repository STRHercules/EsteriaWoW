--[==[ test_roster.lua ------------------------------------------------------------
    Exercises the roster against the frame shim: layout maths, virtual scrolling
    over the fixed row pool, selection resolution, drag-reorder and the deletion
    animation (spec 3, 5, 9, 10, 20, 25, 29, 30).

    The headline invariant, checked repeatedly below: the pool may show any slice,
    but every action resolves to the REAL character index.
]==]

local R = ECS.Roster;
local O = ECS.Order;
local I = ECS.Integrate;
local C = ECS.Const;

-- ---------------------------------------------------------------- fixtures
local function MakeCharacter(realIndex, name)
    return {
        realIndex = realIndex,
        stableKey = "esteria:" .. string.lower(name),
        name = name or ("Char" .. realIndex),
        level = 80, raceName = "Human", raceArtKey = "Human",
        className = "Hero", zone = "Stormwind",
        factionName = "Alliance", factionAccent = { 0.25, 0.5, 0.9 },
        sex = 0, portrait = C.TEX.create .. "UI-CharacterCreate-HumanMale",
    };
end

local function ServerList(count)
    local list = {}
    for index = 1, count do
        list[index] = MakeCharacter(index, string.format("Char%03d", index))
    end
    return list
end

local function ResetRoster(count, poolSize)
    ECS.Search.Reset();
    ECS.Anim.Reset();
    R.Reset();
    O.SetCustomOrder({});
    O.SetCharacters(ServerList(count or 0));

    SHIM.Reset();
    local parent = CreateFrame("Frame", "ECSRowParent", UIParent);
    -- create the named row buttons the XML would have provided
    for index = 1, (poolSize or 10) do
        local button = CreateFrame("Button", R.RowName(index), parent);
        button:SetSize(C.ROSTER_WIDTH, C.ROW_HEIGHT);
    end
    R.BuildPool(parent, poolSize or 10);
    R.SetScrollFrame(nil);
end

-- ================================================================ 1. layout (spec 29)
local layout = R.ComputeLayout(560, 70, 2);
ECS_EQ(layout.viewportHeight, 560, "1a: viewport recorded");
ECS_EQ(layout.rowHeight, 70, "1b: row height recorded");
ECS_EQ(layout.slots, 10, "1c: 560/70 = 8 visible rows + 2 buffer");

-- 1d: a SHORT viewport must not ask for a negative or zero pool
local tiny = R.ComputeLayout(140, 70, 2);
ECS_EQ(tiny.slots, 4, "1d: small viewport yields a small pool");

local zero = R.ComputeLayout(0, 70, 2);
ECS_CHECK(zero.slots >= 1, "1e: a zero-height viewport still yields at least one slot");

local broken = R.ComputeLayout(560, 0, 2);
ECS_CHECK(broken.rowHeight > 0, "1f: a zero row height falls back rather than dividing by zero");
ECS_CHECK(broken.slots >= 1, "1g: and still yields a usable pool");

-- 1h: taller resolutions ask for more rows, which is the resolution-independence
-- requirement in action
ECS_CHECK(R.ComputeLayout(1440, 70, 2).slots > R.ComputeLayout(720, 70, 2).slots,
    "1h: a taller viewport yields a larger pool");

-- 1i: defaults work with no arguments
local defaults = R.ComputeLayout();
ECS_CHECK(defaults.slots >= 1, "1i: ComputeLayout() has usable defaults");

-- ================================================================ 2. offsets
ECS_EQ(R.MaxOffset(100, layout), 92, "2a: 100 characters, 8 visible -> max offset 92");
ECS_EQ(R.MaxOffset(5, layout), 0, "2b: fewer than a page -> no scrolling");
ECS_EQ(R.MaxOffset(0, layout), 0, "2c: empty roster -> no scrolling");
ECS_EQ(R.ClampOffset(-5, 100, layout), 0, "2d: negative offset clamped to 0");
ECS_EQ(R.ClampOffset(999, 100, layout), 92, "2e: over-large offset clamped to max");
ECS_EQ(R.ClampOffset(7, 100, layout), 7, "2f: an in-range offset is untouched");
ECS_EQ(R.ClampOffset("rubbish", 100, layout), 0, "2g: a non-numeric offset is tolerated");

-- ================================================================ 3. hit testing (spec 10)
R.offset = 0;
ECS_EQ(R.SlotForY(0, layout, 100), 1, "3a: y=0 is the first slot");
ECS_EQ(R.SlotForY(69, layout, 100), 1, "3b: within the first row");
ECS_EQ(R.SlotForY(70, layout, 100), 2, "3c: second row starts at one row height");
ECS_EQ(R.SlotForY(700, layout, 100), 8, "3d: drag targets clamp to the eighth visible row");
ECS_EQ(R.SlotForY(-50, layout, 100), 1, "3e: above the top clamps to the first slot");

-- 3f: hit testing must be offset-aware - this is what makes drag work while scrolled
R.offset = 10;
ECS_EQ(R.SlotForY(0, layout, 100), 11, "3f: with an offset, y=0 is visual 11");
R.offset = 0;

-- 3g: never return a slot beyond the data
ECS_EQ(R.SlotForY(7000, layout, 12), 8, "3g: clamped to the last slot in the eight-row viewport");

-- ================================================================ 4. pool
ResetRoster(50, 10);
ECS_EQ(R.PoolSize(), 10, "4a: pool built from the named row buttons");
ECS_CHECK(R.pool[1] ~= nil, "4b: pool holds frames");
ECS_CHECK(R.pool[1].__ecs ~= nil and R.pool[1].__ecs.built, "4c: pooled rows are decorated");
ECS_CHECK(_G["CharSelectCharacterButton1FactionIcon"] ~= nil,
    "4d: the Freeborn wrapper's FactionIcon still exists");

-- 4e: a missing named button is skipped rather than crashing
SHIM.Reset();
local bare = CreateFrame("Frame", "BareParent", UIParent);
CreateFrame("Button", R.RowName(1), bare);
R.BuildPool(bare, 10);
ECS_EQ(R.PoolSize(), 1, "4e: only the buttons that exist join the pool");

-- ================================================================ 4f. eight visible rows
ResetRoster(12, 10);
local stockRowParent = R.rowFrame;
_G[R.RowName(9)]:SetID(9);
_G[R.RowName(10)]:SetID(10);
R.BuildPool(stockRowParent, C.POOL_SIZE);
local savedCharacterSelect = _G.CharacterSelect;
_G.CharacterSelect = { scrollMax = 0 };
local maxScrollFrame = CreateFrame("ScrollFrame", "ECSMaxScrollFrame", UIParent);
local maxScrollChild = CreateFrame("Frame", "ECSMaxScrollChild", maxScrollFrame);
maxScrollFrame:SetScrollChild(maxScrollChild);
R.SetScrollFrame(maxScrollFrame);
R.Refresh();
ECS_EQ(R.PoolSize(), 8, "4f: only eight buttons are in the visible pool");
ECS_CHECK(not _G[R.RowName(9)]:IsShown(), "4g: stock row 9 stays hidden");
ECS_CHECK(not _G[R.RowName(10)]:IsShown(), "4h: stock row 10 stays hidden");
ECS_EQ(_G[R.RowName(9)]:GetID(), 9, "4i: hidden stock rows keep valid integer IDs");
ECS_EQ(_G[R.RowName(10)]:GetID(), 10, "4i2: second hidden stock row keeps its ID");
ECS_EQ(_G.CharacterSelect.scrollMax, 4, "4i2: stock wheel clamp uses the eight-row page size");
R.SetOffset(4);
ECS_EQ(R.pool[1]:GetID(), 5, "4j: scrolling rebinds the first row after the initial page");
ECS_EQ(R.pool[8]:GetID(), 12, "4k: the eighth row reaches the end of the roster");
_G.CharacterSelect = savedCharacterSelect;

-- ================================================================ 5. refresh / virtual window
ResetRoster(6, 4);
R.Refresh();
ECS_EQ(O.VisibleCount(), 6, "5a: six characters visible");
ECS_EQ(R.pool[1]:GetID(), 1, "5b: first row carries real index 1");
ECS_EQ(R.pool[4]:GetID(), 4, "5c: fourth row carries real index 4");
ECS_CHECK(R.pool[1]:IsShown(), "5d: bound rows are shown");

-- 5e: shrinking the filtered roster blanks unused pooled rows without assigning
-- nil to SetID (the live client raises on that invalid id).
ECS.Search.SetQuery("char001");
R.Refresh();
ECS_CHECK(R.pool[1]:IsShown(), "5e: row 1 bound");
ECS_CHECK(not R.pool[3]:IsShown(), "5f: row 3 hidden when only one result matches");
ECS_EQ(R.pool[3]:GetID(), 3, "5g: hidden rows retain their last valid numeric id");
ECS_EQ(O.VisibleCount(), 1, "5g2: search reduces the visible order to one character");
ECS.Search.Reset();

-- 5h: scrolling re-windows the SAME frames over different characters
ResetRoster(50, 4);
R.Refresh();
ECS_EQ(R.pool[1]:GetID(), 1, "5h: starts at real index 1");
R.SetOffset(5);
ECS_EQ(R.pool[1]:GetID(), 6, "5i: after scrolling 5, the first row shows real index 6");
ECS_EQ(R.pool[4]:GetID(), 9, "5j: and the last row shows real index 9");
ECS_EQ(R.PoolSize(), 4, "5k: no new frames were created by scrolling");

-- 5l: scrolling past the end clamps instead of showing blanks
R.SetOffset(999);
ECS_EQ(R.pool[1]:GetID(), 43, "5l: clamped so the last page is fully populated");
ECS_CHECK(R.pool[4]:IsShown(), "5m: the final row of the last page is bound");

-- ================================================================ 6. custom order + filter
ResetRoster(6, 4);
O.SetCustomOrder({ "esteria:char004", "esteria:char001" });
R.SetOffset(0);
R.Refresh();
ECS_EQ(R.pool[1]:GetID(), 4, "6a: custom order puts real index 4 first");
ECS_EQ(R.pool[2]:GetID(), 1, "6b: then real index 1");
ECS_EQ(R.pool[3]:GetID(), 2, "6c: remaining characters follow in server order");

-- 6d: with a custom order AND a filter active, the rows must still carry REAL
-- indices. This is the case where visual position and real index genuinely differ,
-- so it is the one that would expose a translation mistake.
ECS.Search.SetQuery("char00");
R.SetOffset(0);
R.Refresh();
ECS_EQ(O.VisibleCount(), 6, "6d: the filter matches all six characters");
ECS_EQ(R.pool[1]:GetID(), 4, "6e: row 1 shows REAL index 4 (custom order survives the filter)");
ECS_EQ(R.pool[2]:GetID(), 1, "6f: row 2 shows REAL index 1");
ECS_CHECK(R.pool[1]:GetID() ~= 1,
    "6g: and it is emphatically NOT the visual position");
ECS.Search.Reset();

-- ================================================================ 7. selection
ResetRoster(6, 4);
R.Refresh();
ECS_CHECK(R.GetSelected() == nil, "7a: nothing selected initially");

ECS_CHECK(R.Select(3) == true, "7b: selecting a real index reports a change");
ECS_EQ(R.GetSelected(), 3, "7c: selection recorded");
ECS_CHECK(R.ClearSelection() == true, "7c2: clearing an existing selection reports a change");
ECS_EQ(R.GetSelected(), nil, "7c3: clear selection removes the stale real index");
ECS_CHECK(R.ClearSelection() == false, "7c4: clearing an empty selection is a no-op");
R.Select(3);
ECS_CHECK(R.Select(3) == false, "7d: selecting the same index is a no-op");
ECS_CHECK(R.IsSelectionVisible(), "7e: the selection is visible");

-- 7f: clicking a row selects whatever REAL character that row displays
ResetRoster(50, 4);
R.SetOffset(10);
R.Refresh();
local clicked = R.HandleRowClick(R.pool[2]);
ECS_EQ(clicked, 12, "7f: clicking row 2 while scrolled selects real index 12");
ECS_EQ(R.GetSelected(), 12, "7g: and that becomes the selection");
ECS_CHECK(R.HandleRowClick(nil) == nil, "7h: clicking nothing is safe");

-- 7i: spec 8 - a filtered-out selection is kept but not rendered
ResetRoster(6, 4);
R.Select(3);
ECS.Search.SetQuery("char005");
R.Refresh();
ECS_EQ(R.GetSelected(), 3, "7i: the real selection is RETAINED while filtered out");
ECS_CHECK(not R.IsSelectionVisible(), "7j: but the roster shows no selected row");
ECS.Search.Reset();
ECS_CHECK(R.IsSelectionVisible(), "7k: clearing the filter restores the selected row");

-- 7l: selection follows the CHARACTER through a reorder, not the slot
ResetRoster(6, 4);
R.Select(2);
ECS_EQ(O.RealIndexAt(1), 1, "7l: real index 1 is first before the reorder");
O.MoveCharacter(2, 1);
R.Refresh();
ECS_EQ(R.GetSelected(), 2, "7m: the selection still points at real index 2");
ECS_EQ(O.RealIndexAt(1), 2, "7n: which is now the first row");

-- 7o: the stock adjustment compares real indices with a visual scroll offset.
-- Selecting real index 1 at visual row 10 must keep the bottom page in place.
local previousViewportHeight = R.ViewportHeight;
local previousPoolBuilt = I.poolBuilt;
local previousCharacterSelect = _G.CharacterSelect;
ResetRoster(10, 4);
R.ViewportHeight = function() return 280 end;
local reverseOrder = {};
for index = 10, 1, -1 do
    reverseOrder[#reverseOrder + 1] = "esteria:char" .. string.format("%03d", index);
end
O.SetCustomOrder(reverseOrder);
R.SetOffset(6);
I.poolBuilt = true;
_G.CharacterSelect = { selectedIndex = 1, scrollOffset = 6 };
local handled, changed = I.AdjustOffsetForSelection();
ECS_CHECK(handled, "7o: ECS handles selection offset while its pool is active");
ECS_CHECK(not changed, "7p: selecting a visible row does not move the list");
ECS_EQ(R.GetOffset(), 6, "7q: a visible selection preserves the bottom-page offset");
_G.CharacterSelect.selectedIndex = 10;
handled, changed = I.AdjustOffsetForSelection();
ECS_CHECK(handled and changed, "7r: off-page selections still bring their visual row into view");
ECS_EQ(R.GetOffset(), 0, "7s: the window moves to the selected visual row, not its real index");
R.Refresh();
ECS_EQ(R.pool[1]:GetID(), 10, "7t: the selected character is visible after the visual scroll");
_G.CharacterSelect.selectedIndex = 1;  -- real 1 is visual 10 on the reverse order
R.SetOffset(0);                       -- emulate a stock real-index page jump
_G.CharacterSelect.scrollOffset = 0;
ECS_CHECK(I.PreserveVisibleSelectionOffset(6),
    "7u: a visible selection restores the page if stock moved it");
ECS_EQ(R.GetOffset(), 6, "7v: selection restores the prior visual page");
ECS_EQ(_G.CharacterSelect.scrollOffset, 6, "7w: stock offset is resynchronized");
R.ViewportHeight = previousViewportHeight;
I.poolBuilt = previousPoolBuilt;
_G.CharacterSelect = previousCharacterSelect;

-- ================================================================ 8. drag (spec 10)
ResetRoster(6, 4);
R.Refresh();

ECS_CHECK(R.BeginPress(R.pool[1], 0, 0) == true, "8a: press armed");
ECS_CHECK(not R.IsDragging(), "8b: a press is NOT yet a drag");

-- 8c: movement below the threshold must not start a drag
ECS_CHECK(R.UpdatePress(2, 2) == false, "8c: movement under the threshold does not drag");
ECS_CHECK(not R.IsDragging(), "8d: still not dragging");

-- 8e: crossing the threshold arms it
ECS_CHECK(R.UpdatePress(C.DRAG_THRESHOLD + 5, C.DRAG_THRESHOLD + 5) == true,
    "8e: crossing the threshold starts the drag");
ECS_CHECK(R.IsDragging(), "8f: dragging reported");

-- 8g: releasing without ever arming is a CLICK, so no reorder happens
ResetRoster(6, 4);
R.Refresh();
R.BeginPress(R.pool[2], 0, 0);
ECS_CHECK(R.EndPress() == false, "8g: a click (no drag) does not reorder");
ECS_EQ(O.RealIndexAt(1), 1, "8h: order unchanged by a click");

-- 8i: a real drag commits the reorder
ResetRoster(6, 4);
R.Refresh();
R.BeginPress(R.pool[1], 0, 0);
R.UpdatePress(C.DRAG_THRESHOLD + 10, 2 * C.ROW_HEIGHT + 5);
ECS_EQ(R.GetDragTarget(), 3, "8i: the drop target is slot 3");
local changed = R.EndPress();
ECS_CHECK(changed == true, "8j: dropping reports a reorder");
ECS_EQ(O.RealIndexAt(3), 1, "8k: the dragged character landed at visual 3");

-- 8l: the reorder callback fires so the caller can persist
ResetRoster(6, 4);
R.Refresh();
local fired = 0;
R.onReordered = function() fired = fired + 1 end;
R.BeginPress(R.pool[1], 0, 0);
R.UpdatePress(C.DRAG_THRESHOLD + 10, 2 * C.ROW_HEIGHT + 5);
R.EndPress();
ECS_EQ(fired, 1, "8l: onReordered fired so the new order can be saved");
R.onReordered = nil;

-- 8m: dragging onto itself changes nothing
ResetRoster(6, 4);
R.Refresh();
R.BeginPress(R.pool[1], 0, 0);
R.UpdatePress(C.DRAG_THRESHOLD + 10, 1);
ECS_CHECK(R.EndPress() == false, "8m: dropping on the same slot is not a reorder");

-- 8n: cancelling a drag leaves the order alone
ResetRoster(6, 4);
R.Refresh();
R.BeginPress(R.pool[1], 0, 0);
R.UpdatePress(C.DRAG_THRESHOLD + 10, 2 * C.ROW_HEIGHT + 5);
R.CancelPress();
ECS_CHECK(not R.IsDragging(), "8n: drag cancelled");
ECS_EQ(O.RealIndexAt(1), 1, "8o: order untouched by a cancel");

-- 8p: dragging an unbound row is refused
ResetRoster(2, 4);
R.Refresh();
ECS_CHECK(R.BeginPress(R.pool[4], 0, 0) == false, "8p: an unbound row cannot be dragged");
ECS_CHECK(R.BeginPress(nil, 0, 0) == false, "8q: a nil row cannot be dragged");

-- ================================================================ 8b. pointer mapping
-- The drag target is derived from the row parent's own top edge rather than from
-- raw screen coordinates, so it does not depend on where the roster sits at a
-- given resolution.
ResetRoster(20, 4);
R.Refresh();

local rowParent = R.pool[1]:GetParent();
rowParent:SetTop(900);
SHIM.cursorY = 900;
ECS_EQ(R.CursorOffsetY(), 0, "8r: cursor level with the roster top is offset 0");

SHIM.cursorY = 830;   -- 70px below the top = exactly one row down
ECS_EQ(R.CursorOffsetY(), 70, "8s: 70px below the top is offset 70");

SHIM.cursorY = 900 + 35;   -- above the roster top
ECS_EQ(R.CursorOffsetY(), -35, "8t: above the top is a negative offset");

-- 8u: a drag armed with a roster-relative Y picks the right slot. SlotForY maps
-- 140px to the 3rd row.
R.SetOffset(0);
R.BeginPress(R.pool[1], 0, 140);
ECS_CHECK(R.UpdatePress(C.DRAG_THRESHOLD + 10, 140) == true, "8u: drag armed");
ECS_EQ(R.GetDragTarget(), 3, "8v: 140px down is the third slot");
R.CancelPress();

-- 8v2: production rows are screen-anchored below the header/search instead of
-- starting at the stock CharacterSelectCharacterFrame top edge.
local screenParent = CreateFrame("Frame", "ECSScreenParent", UIParent);
screenParent:SetTop(1200);
R.SetLayoutParent(screenParent);
R.Refresh();
local _, visualParent, _, visualX, visualY = R.pool[1]:GetPoint(1);
ECS_EQ(visualParent, screenParent, "8v2: row anchor uses the screen frame");
ECS_EQ(visualX, -C.ROSTER_RIGHT - C.ROSTER_WIDTH, "8v3: roster is right-aligned with its margin");
ECS_EQ(visualY, -C.ROSTER_TOP, "8v4: first row starts below the raised search field");

SHIM.cursorY = 1200 - C.ROSTER_TOP;
ECS_EQ(R.CursorOffsetY(), 0, "8v5: screen-relative pointer starts at the roster top");
SHIM.cursorY = 1200 - C.ROSTER_TOP - 70;
ECS_EQ(R.CursorOffsetY(), 70, "8v6: screen-relative pointer tracks row distance");
R.SetLayoutParent(nil);
R.Refresh();

-- 8w: with no rows there is no geometry to read, so it reports nil rather than a
-- wrong coordinate
local savedPool = R.pool;
R.pool = {};
ECS_EQ(R.CursorOffsetY(), nil, "8w: no rows means no pointer mapping");
R.pool = savedPool;

-- 8x: ApplyRowOffset re-anchors a single row without a full refresh
R.Refresh();
R.pool[2].__ecsRowY = 70;
ECS.Row.SetOffsetX(R.pool[2], 5);
local p = R.pool[2]:GetPoint(1);
ECS_CHECK(p ~= nil, "8x: the row has an anchor");
local _, _, _, ax, ay = R.pool[2]:GetPoint(1);
ECS_EQ(ax, 5, "8y: the hover offset is applied to the anchor");
ECS_EQ(ay, -70, "8z: the slot position is preserved");

-- ================================================================ 9. scrolling
-- (this header used to swallow its own ResetRoster call, so the section ran
-- against whatever roster the previous section left behind)
ResetRoster(100, 4);
R.Refresh();

-- 9a-9f: THE OFFSET IS A WHOLE ROW, ALWAYS. This is the invariant
-- ECS.Order.RealIndexAt depends on (`O.visible[pos]` does not round), and breaking
-- it is not a cosmetic rounding difference: a fractional offset makes every pooled
-- row resolve to nil, so the roster goes blank, and the stock
-- UpdateCharacterSelection builds a name like "CharSelectCharacterButton1.55" from
-- `selectedIndex - scrollOffset`, so its nil lookup errors inside the glue screen.
--
-- The live bug was ECS hooking the wheel IN ADDITION to the stock handler and then
-- assigning its own 0.45-row offset straight into select.scrollOffset.
R.SetOffset(0);
ECS_EQ(R.GetOffset(), 0, "9a: a fresh offset is a whole row");
R.SetOffset(4);
ECS_EQ(R.GetOffset(), 4, "9b: an integer offset is kept exactly");

R.SetOffset(4.55);
ECS_EQ(R.GetOffset(), 4, "9c: a fractional offset is floored, not stored");
ECS_CHECK(R.GetOffset() == math.floor(R.GetOffset()),
    "9d: the offset is always an integer row");

-- 9e: the roster must still bind its pooled rows after a fractional INPUT, which
-- is exactly what the live bug destroyed - every row hidden, since visual 5.55 is
-- not a row.
R.SetOffset(9.9);
local boundAfterFraction = 0;
for index = 1, #R.pool do
    if ( ECS.Row.GetCharacter(R.pool[index]) ~= nil ) then
        boundAfterFraction = boundAfterFraction + 1;
    end
end
ECS_CHECK(boundAfterFraction > 0,
    "9e: rows still bind after a fractional offset (the blank-roster regression)");

-- 9f: every visual position handed to the order is a whole row
local firstVisual = R.GetOffset() + 1;
ECS_EQ(firstVisual, math.floor(firstVisual), "9f: visual positions stay whole rows");

-- 9g/9h: the scroll frame callback converts pixels to rows
R.SetOffset(0);
R.OnVerticalScroll(140);
ECS_EQ(R.GetOffset(), 2, "9g: 140px at 70px per row is offset 2");
R.OnVerticalScroll(0);
ECS_EQ(R.GetOffset(), 0, "9h: back to the top");

-- 9i/9j: the native scrollbar is kept in sync with the child height
local frame = CreateFrame("Frame", "FakeScrollFrame", UIParent);
local child = CreateFrame("Frame", "FakeScrollChild", frame);
frame:SetScrollChild(child);
R.SetScrollFrame(frame);
R.SetOffset(10);
ECS_CHECK(child:GetHeight() > 0, "9i: the scroll child grows so the scrollbar has range");
ECS_CHECK(frame:GetVerticalScroll() > 0, "9j: the native scrollbar mirrors our offset");

-- 9k/9l/9m: applying our offset must run under the STOCK's re-entrancy guard.
-- SetVerticalScroll fires OnVerticalScroll synchronously and the stock handler only
-- returns early on `CharacterSelect.scrollUpdating`. ECS used to set only its own
-- R.applyingScroll flag, which nothing read: so our own scroll re-entered the stock
-- path, which rebinds the rows from SERVER order, and ECS's I.applying guard then
-- suppressed the re-skin that would have repaired them. That happens whenever a
-- filter shrinks the visible count while the roster is scrolled down, because ECS
-- clamps to the filtered maximum and stock had clamped to the full-roster one.
local guardSeen = nil;
local realSetVerticalScroll = frame.SetVerticalScroll;
frame.SetVerticalScroll = function(self, value)
    guardSeen = _G.CharacterSelect and _G.CharacterSelect.scrollUpdating;
    return realSetVerticalScroll(self, value);
end;

local savedSelect = _G.CharacterSelect;
_G.CharacterSelect = { scrollUpdating = false };

R.SetOffset(3);
ECS_CHECK(guardSeen == true, "9k: the stock guard is set while ECS applies its offset");
ECS_EQ(_G.CharacterSelect.scrollUpdating, false, "9l: ... and restored afterwards");

_G.CharacterSelect.scrollUpdating = true;
R.SetOffset(4);
ECS_EQ(_G.CharacterSelect.scrollUpdating, true,
    "9m: a guard that was already set is restored, not cleared");

_G.CharacterSelect = savedSelect;
frame.SetVerticalScroll = realSetVerticalScroll;

-- ================================================================ 10. deletion animation (spec 20)
ResetRoster(3, 4);
R.Refresh();
local completed = 0;
ECS_CHECK(R.AnimateDelete(R.pool[1], function() completed = completed + 1 end) == true,
    "10a: deletion animation starts");
-- Anim.Update clamps a single step to C.ANIM_MAX_DT, so the animation must be
-- stepped the way the client's OnUpdate would step it, not in one huge jump.
for step = 1, 10 do
    ECS.Anim.Update(C.ANIM_MAX_DT);
end
ECS_EQ(completed, 1, "10b: the completion callback fired");
ECS_CHECK(R.pool[1]:GetAlpha() < 0.001, "10c: the row faded out");

-- 10d: a nil row still completes rather than stalling the caller
local ran = false;
R.AnimateDelete(nil, function() ran = true end);
ECS_CHECK(ran, "10d: deleting a nil row still completes");

-- ================================================================ 11. reset
R.Select(3);
R.SetOffset(4);
R.Reset();
ECS_EQ(R.GetOffset(), 0, "11a: reset clears the offset");
ECS_EQ(R.GetSelected(), nil, "11b: reset clears the selection");
ECS_CHECK(not R.IsDragging(), "11c: reset clears any drag");
ECS_EQ(R.PoolSize(), 0, "11d: reset clears the pool");
