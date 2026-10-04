--[==[ test_tooltip.lua -----------------------------------------------------------
    Proves the detail panel's content and placement: sane copy for custom and
    unknown characters, edge clamping at any resolution, and a hover delay that
    never strands a stale panel (spec 13, 33).
]==]

local T = ECS.Tooltip;
local C = ECS.Const;

T.Reset();

local function MakeCharacter(overrides)
    local character = {
        realIndex = 1, stableKey = "esteria:zach", name = "Zach",
        level = 81, raceName = "High Elf", raceKnown = true,
        className = "Hero", classColour = { 0.9, 0.8, 0.7 },
        zone = "Elwynn Forest",
        factionName = "Alliance", factionAccent = { 0.25, 0.5, 0.9 },
        note = nil,
    };
    if ( overrides ) then
        for key, value in pairs(overrides) do character[key] = value end
    end
    return character
end

local function Texts(lines)
    local out = {}
    for index = 1, #lines do out[index] = lines[index].text end
    return table.concat(out, "|")
end

-- ================================================================ 1. content
local lines = T.BuildLines(MakeCharacter());
ECS_CHECK(#lines >= 4, "1a: a full character produces the expected line count");
ECS_EQ(lines[1].text, "Zach", "1b: name leads");
ECS_EQ(lines[1].style, "title", "1c: name is the title style");
ECS_CHECK(string.find(lines[2].text, "81", 1, true) ~= nil, "1d: level on the detail line");
ECS_CHECK(string.find(lines[2].text, "High Elf", 1, true) ~= nil, "1e: race on the detail line");
ECS_CHECK(string.find(lines[2].text, "Hero", 1, true) ~= nil, "1f: class on the detail line");
ECS_CHECK(string.find(Texts(lines), "Elwynn Forest", 1, true) ~= nil, "1g: zone shown");
ECS_CHECK(string.find(Texts(lines), "Alliance", 1, true) ~= nil, "1h: faction shown");

-- 1i: class colour is carried as the secondary accent (spec 27)
ECS_CHECK(lines[2].colour ~= nil, "1i: class colour carried on the detail line");

-- 1j: a nil zone produces NO empty line rather than a blank row.
-- Cleared with an explicit assignment: `zone = nil` inside a table constructor
-- does not create the key, so the default would survive and the test would pass
-- for the wrong reason.
local zoneLess = MakeCharacter();
zoneLess.zone = nil;
local noZone = T.BuildLines(zoneLess);
ECS_CHECK(string.find(Texts(noZone), "||", 1, true) == nil, "1j: no blank line for a nil zone");
ECS_CHECK(#noZone < #lines, "1k: and the panel is shorter for it");

-- 1l: an unknown race is surfaced rather than silently mislabelled
local unknown = T.BuildLines(MakeCharacter({
    raceName = C.FALLBACK_RACE_NAME, raceKnown = false,
}));
ECS_CHECK(string.find(Texts(unknown), "Unrecognised", 1, true) ~= nil,
    "1l: an unknown race is called out");

-- 1m: a note adds a line, and its absence does not
local withNote = T.BuildLines(MakeCharacter({ note = "Main tank" }));
ECS_CHECK(string.find(Texts(withNote), "Main tank", 1, true) ~= nil, "1m: the note is shown");
ECS_CHECK(#withNote == #lines + 1, "1n: exactly one extra line for the note");

-- 1o: a bare record still produces something safe
local bare = T.BuildLines({ name = "Ghost" });
ECS_CHECK(#bare >= 2, "1o: a minimal character still yields a title and a detail line");
ECS_CHECK(string.find(Texts(bare), C.LEVEL_UNKNOWN, 1, true) ~= nil,
    "1p: a missing level shows the placeholder");

-- 1q: junk input is safe
ECS_EQ(#T.BuildLines(nil), 0, "1q: BuildLines(nil) returns nothing");
ECS_EQ(#T.BuildLines("nonsense"), 0, "1r: BuildLines(non-table) returns nothing");

-- ================================================================ 2. size estimate
local width, height = T.EstimateSize(lines);
ECS_CHECK(width >= T.MIN_WIDTH, "2a: width respects the minimum");
ECS_CHECK(width <= T.MAX_WIDTH, "2b: width respects the maximum");
ECS_CHECK(height > 0, "2c: height is positive");

local wideW = T.EstimateSize({ { text = string.rep("x", 500) } });
ECS_EQ(wideW, T.MAX_WIDTH, "2d: an absurdly long line is capped at the maximum width");

local tinyW = T.EstimateSize({ { text = "" } });
ECS_EQ(tinyW, T.MIN_WIDTH, "2e: a short line is padded up to the minimum width");

-- 2f: EstimateSize returns width AND height, so the height must be captured
-- explicitly - taking only the first return would compare two widths.
local _, tall = T.EstimateSize({ { text = "a" }, { text = "b" }, { text = "c" } });
local _, short = T.EstimateSize({ { text = "a" } });
ECS_CHECK(tall > short, "2f: more lines means a taller panel");

-- ================================================================ 3. anchoring (spec 13)
local SW, SH = 1920, 1080;

-- 3a: the common case - cursor mid-screen, panel fits either side
local x, y, flippedX, flippedY = T.ComputeAnchor(900, 500, 200, 100, SW, SH);
ECS_CHECK(x >= 0 and x + 200 <= SW, "3a: panel stays on screen horizontally");
ECS_CHECK(y >= 0 and y + 100 <= SH, "3b: panel stays on screen vertically");
ECS_CHECK(flippedX == false, "3c: no horizontal flip when there is room");
ECS_CHECK(flippedY == false, "3d: no vertical flip when there is room");

-- 3e: near the right edge it must flip to the LEFT of the cursor
local fx, _, fFlipX = T.ComputeAnchor(SW - 10, 500, 200, 100, SW, SH);
ECS_CHECK(fFlipX == true, "3e: flips horizontally near the right edge");
ECS_CHECK(fx + 200 <= SW, "3f: and stays on screen after flipping");

-- 3g: near the top it must flip BELOW the cursor
local _, fy, _, fFlipY = T.ComputeAnchor(900, 10, 200, 100, SW, SH);
ECS_CHECK(fFlipY == true, "3g: flips vertically near the top");
ECS_CHECK(fy >= 0, "3h: and stays on screen after flipping");

-- 3i: bottom-right corner - both flips at once
local cx, cy = T.ComputeAnchor(SW - 5, SH - 5, 200, 100, SW, SH);
ECS_CHECK(cx >= 0 and cx + 200 <= SW, "3i: bottom-right corner stays on screen (x)");
ECS_CHECK(cy >= 0 and cy + 100 <= SH, "3j: bottom-right corner stays on screen (y)");

-- 3k: a panel WIDER than the screen is pinned to the left margin, not pushed off
local ox, oy = T.ComputeAnchor(100, 100, SW + 400, SH + 400, SW, SH);
ECS_CHECK(ox >= 0, "3k: an over-wide panel is clamped, not pushed negative");
ECS_CHECK(oy >= 0, "3l: an over-tall panel is clamped, not pushed negative");

-- 3m: PROPERTY - for a grid of cursor positions, the panel is always in bounds
local violations = 0
for _, ax in ipairs({ 0, 1, 5, 100, 500, 960, 1300, 1919, 1920, 5000 }) do
    for _, ay in ipairs({ 0, 1, 5, 100, 500, 700, 1079, 1080, 5000 }) do
        local px, py = T.ComputeAnchor(ax, ay, 220, 120, SW, SH)
        if ( px < 0 or py < 0 or px + 220 > SW or py + 120 > SH ) then
            violations = violations + 1
        end
    end
end
ECS_EQ(violations, 0, "3m: the panel is in bounds for every probed cursor position");

-- 3n: works at a small resolution too (spec 29)
local sx, sy = T.ComputeAnchor(600, 400, 200, 100, 800, 600);
ECS_CHECK(sx >= 0 and sx + 200 <= 800, "3n: small screen stays in bounds (x)");
ECS_CHECK(sy >= 0 and sy + 100 <= 600, "3o: small screen stays in bounds (y)");

-- 3p: junk arguments do not raise
local jx, jy = T.ComputeAnchor(nil, nil, nil, nil, nil, nil);
ECS_CHECK(type(jx) == "number" and type(jy) == "number", "3p: nil arguments are tolerated");

-- ================================================================ 4. hover delay
T.Reset();
local character = MakeCharacter();
ECS_CHECK(not T.IsVisible(), "4a: hidden initially");

T.BeginHover(character);
ECS_CHECK(not T.IsVisible(), "4b: not visible the instant the pointer arrives");
T.Update(C.TOOLTIP_DELAY / 2);
ECS_CHECK(not T.IsVisible(), "4c: still hidden before the delay elapses");
ECS_CHECK(T.Update(C.TOOLTIP_DELAY / 2 + 0.01) == true, "4d: becomes visible after the delay");
ECS_CHECK(T.IsVisible(), "4e: visible state reported");
ECS_EQ(T.GetCharacter().name, "Zach", "4f: the right character is shown");

-- 4g: once visible, further updates do not re-trigger
ECS_CHECK(T.Update(1) == false, "4g: further updates do not re-show it");

-- 4h: moving off the row before the delay means it never appears
T.Reset();
T.BeginHover(character);
T.Update(C.TOOLTIP_DELAY / 2);
T.Cancel();
T.Update(C.TOOLTIP_DELAY * 5);
ECS_CHECK(not T.IsVisible(), "4h: cancelling before the delay prevents the panel entirely");

-- 4i: Hide reports whether anything was actually shown, so the caller can avoid
-- needless frame work
T.Reset();
T.BeginHover(character);
T.Update(C.TOOLTIP_DELAY + 0.1);
ECS_CHECK(T.Hide() == true, "4i: Hide reports it was visible");
ECS_CHECK(T.Hide() == false, "4j: Hide on a hidden panel reports nothing to do");
ECS_CHECK(T.GetCharacter() == nil, "4k: Hide clears the character");

-- 4l: hovering a different row replaces the pending character
T.Reset();
T.BeginHover(character);
T.BeginHover(MakeCharacter({ name = "Nat" }));
T.Update(C.TOOLTIP_DELAY + 0.1);
ECS_EQ(T.GetCharacter().name, "Nat", "4l: the latest hovered row wins");

-- 4m: hovering nothing cancels rather than showing the previous character
T.BeginHover(nil);
ECS_CHECK(not T.IsVisible(), "4m: hovering nil cancels any pending panel");

-- 4n: spec 13 - the panel updates when the data changes under it
T.Reset();
T.BeginHover(character);
T.Update(C.TOOLTIP_DELAY + 0.1);
ECS_CHECK(T.Refresh(MakeCharacter({ name = "Renamed" })) == true, "4n: Refresh updates a visible panel");
ECS_EQ(T.GetCharacter().name, "Renamed", "4o: and the new data is shown");
T.Hide();
ECS_CHECK(T.Refresh(character) == false, "4p: Refresh on a hidden panel does nothing");

-- 4q: Reset clears everything
T.BeginHover(character);
T.Reset();
ECS_CHECK(not T.IsVisible(), "4q: Reset hides the panel");
ECS_CHECK(T.GetCharacter() == nil, "4r: Reset clears the character");
