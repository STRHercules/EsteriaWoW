--[==[ test_row.lua ---------------------------------------------------------------
    Exercises ECS_Row against the frame shim, so row construction is verified
    offline rather than only by launching the client (spec 3, 4, 5, 25, 27).

    The shim records what the code DID (texture set, vertex colour, text, SetID),
    so these assertions check behaviour rather than merely "did not crash".
]==]

local R = ECS.Row;
local C = ECS.Const;
local S = ECS.Schema;
local savedClassIconCoords = _G.CLASS_ICON_TCOORDS;
_G.CLASS_ICON_TCOORDS = { MAGE = { 0.1, 0.2, 0.3, 0.4 } };

SHIM.Reset();

-- ---------------------------------------------------------------- fixtures
local function MakeRow(name)
    local button = CreateFrame("Button", name, UIParent);
    button:SetSize(C.ROSTER_WIDTH, C.ROW_HEIGHT);
    return button;
end

local function MakeCharacter(realIndex, overrides)
    local character = {
        realIndex = realIndex,
        stableKey = "esteria:char" .. realIndex,
        name = "Char" .. realIndex,
        level = 80,
        raceName = "High Elf",
        raceArtKey = "HighElf",
        className = "Mage",
        classColour = { 0.75, 0.25, 0.20 },
        zone = "Dalaran",
        factionID = 1,
        factionName = "Alliance",
        factionAccent = { 0.25, 0.50, 0.90 },
        factionEmblem = C.TEX.allianceBadge,
        sex = 0,
        portrait = C.TEX.create .. "UI-CharacterCreate-HighElfMale",
    };
    if ( overrides ) then
        for key, value in pairs(overrides) do character[key] = value end
    end
    return character;
end

-- ---------------------------------------------------------------- 1. build
local row = MakeRow("CharSelectCharacterButton1");
R.Build(row);

local state = R.State(row);
ECS_CHECK(state.built, "1a: marked built");
ECS_CHECK(state.portrait ~= nil, "1b: portrait region created");
ECS_CHECK(state.portraitBorder ~= nil, "1b2: supplied portrait border created");
ECS_CHECK(state.name ~= nil, "1c: name region created");
ECS_CHECK(state.classIcon ~= nil, "1c2: class badge region created");
ECS_CHECK(state.zone ~= nil, "1d: zone region created");
ECS_CHECK(state.noteText ~= nil, "1e: optional note line created");
ECS_CHECK(state.badge ~= nil, "1f: level badge created");
ECS_CHECK(state.levelBorder ~= nil, "1f2: supplied level border created");
ECS_CHECK(state.noteDot ~= nil, "1g: note indicator created");
ECS_CHECK(state.emblem ~= nil, "1h: faction emblem created");
ECS_CHECK(state.tint ~= nil, "1i: tint surface created");
ECS_CHECK(state.idleArt ~= nil, "1i1: default row art created");
ECS_CHECK(state.statusArt ~= nil, "1i2: hover/selection art region created");
ECS_EQ(state.idleArt.__drawLayer, "BACKGROUND", "1i2a: default art stays behind row content");
ECS_EQ(state.idleArt.__subLevel, 1, "1i2b: default art is the bottom row-art layer");
ECS_EQ(state.statusArt.__drawLayer, "BACKGROUND", "1i3: state art stays behind row content");
ECS_EQ(state.statusArt.__subLevel, 2, "1i4: hover/selection art overlays the idle art");
ECS_EQ(state.portraitBorder:GetTexture(), C.TEX.portraitBorder, "1i5: supplied portrait border texture");
ECS_EQ(state.portraitBorder.__width, C.PORTRAIT_BORDER_SIZE, "1i6: border covers the full portrait edge");
ECS_EQ(state.levelBorder:GetTexture(), C.TEX.levelBorder, "1i7: supplied level border texture");
ECS_EQ(state.levelBorder.__width, C.LEVEL_BORDER_SIZE, "1i8: level border uses the compact scale");
local levelBorderPoint, _, _, levelBorderX, levelBorderY = state.levelBorder:GetPoint();
ECS_EQ(levelBorderPoint, "CENTER", "1i9: level border centers on the portrait corner");
ECS_EQ(levelBorderX, -1, "1i10: level badge moved six pixels left");
ECS_EQ(levelBorderY, 3, "1i11: level badge moved six pixels up");

-- 1j: the row uses its supplied artwork, not a flat fill or one-pixel panel rim.
ECS_EQ(row:GetBackdrop(), nil, "1j: no flat row backdrop is applied");
ECS_EQ(state.idleArt:GetTexture(), C.TEX.idlePlate, "1k: supplied grey art backs the idle row");
local rowArtInset = (1 - 1 / C.ROW_ART_SCALE) / 2;
ECS_EQ(C.ROW_ART_SCALE, 1.10, "1k1: all supplied row backdrops use the 10% zoom");
ECS_EQ(state.idleArt.__texcoord[1], rowArtInset, "1k2: grey idle art zooms in from the left edge");
ECS_EQ(state.idleArt.__texcoord[2], 1 - rowArtInset, "1k3: grey idle art zooms in from the right edge");
ECS_EQ(state.statusArt.__texcoord[3], rowArtInset, "1k4: hover/selection art zooms in from the top edge");
ECS_EQ(state.statusArt.__texcoord[4], 1 - rowArtInset,
    "1k5: hover/selection art zooms in from the bottom edge");

-- 1o: the stock red slab is switched off
local normal = row:GetNormalTexture();
ECS_CHECK(normal ~= nil and normal:GetAlpha() == 0, "1o: stock normal texture disabled");
local highlight = row:GetHighlightTexture();
ECS_CHECK(highlight ~= nil and highlight:GetAlpha() == 0, "1p: stock highlight disabled");

-- 1q: the FactionIcon child must exist under the exact name the live Freeborn
-- wrapper looks up, or Freeborn badges silently disappear.
ECS_CHECK(_G["CharSelectCharacterButton1FactionIcon"] ~= nil,
    "1q: FactionIcon registered under the name the Freeborn wrapper uses");

-- 1r/1s: Build must be idempotent - a second call must not replace regions
local portraitBefore = state.portrait;
local nameBefore = state.name;
R.Build(row);
ECS_CHECK(R.State(row).portrait == portraitBefore, "1r: second Build reuses the portrait region");
ECS_CHECK(R.State(row).name == nameBefore, "1s: second Build reuses the name region");
ECS_CHECK(R.Build(nil) == nil, "1t: Build(nil) is safe");

-- ---------------------------------------------------------------- 2. update
local character = MakeCharacter(4);
R.Update(row, character);

ECS_EQ(row:GetID(), 4, "2a: SetID carries the REAL character index");
ECS_EQ(R.GetCharacter(row).name, "Char4", "2b: character bound");
ECS_EQ(state.name:GetText(), "Char4", "2c: name rendered");
ECS_EQ(state.zone:GetText(), "Dalaran", "2d: zone is the second text line");
local nameRed, nameGreen = state.name:GetTextColor();
ECS_EQ(nameRed, character.classColour[1], "2e: name uses its class colour");
ECS_EQ(nameGreen, character.classColour[2], "2f: class colour is applied to the whole name");
ECS_CHECK(not state.noteText:IsShown(), "2g: the optional note line stays hidden when empty");
ECS_EQ(state.badge:GetText(), "80", "2h: level badge rendered");
ECS_EQ(state.badge.__justifyV, "MIDDLE", "2h2: level text is vertically centered in its border");
local levelTextPoint, levelTextAnchor = state.badge:GetPoint();
ECS_EQ(levelTextPoint, "CENTER", "2h3: level text is centered on its border");
ECS_EQ(levelTextAnchor, state.levelBorder, "2h4: level text anchors to the supplied border");
ECS_EQ(state.portrait:GetTexture(), character.portrait, "2i: portrait texture set");
ECS_EQ(state.idleArt:GetTexture(), C.TEX.idlePlate, "2i1: idle rows use the grey backdrop");
ECS_CHECK(state.idleArt:IsShown(), "2i1a: grey backdrop remains visible under content");
ECS_EQ(state.idleArt:GetAlpha(), 1, "2i1aa: idle grey is fully visible without hover");
ECS_CHECK(not state.statusArt:IsShown(), "2i1b: faction art is absent until hover or selection");
ECS_CHECK(state.classIcon:IsShown(), "2i2: known classes show their portrait badge");
ECS_EQ(state.classIcon:GetTexture(), C.TEX.classIcon, "2i3: the class badge uses the client class atlas");
ECS_EQ(state.classIcon.__texcoord[1], 0.1, "2i4: the class badge uses the class-specific atlas crop");
ECS_CHECK(row:IsShown(), "2j: row shown");

-- 2k: the note indicator only appears when there IS a note
ECS_CHECK(not state.noteDot:IsShown(), "2k: no note dot without a note");
R.Update(row, MakeCharacter(4, { note = "Main tank" }));
ECS_CHECK(state.noteDot:IsShown(), "2l: note dot appears with a note");
ECS_EQ(state.noteText:GetText(), "Main tank", "2m: note appears on the third line");
ECS_CHECK(state.noteText:IsShown(), "2n: the note line is visible when populated");

-- ---------------------------------------------------------------- 3. degradation
-- A character with no portrait and an unknown race must still render (spec 33).
-- NOTE: assigning nil inside a table constructor does not create the key, so the
-- fields must be cleared individually for the override to actually take effect.
local bare = MakeCharacter(5);
bare.portrait = nil;
bare.raceArtKey = nil;
bare.raceName = C.FALLBACK_RACE_NAME;
bare.factionAccent = nil;
bare.factionEmblem = nil;
bare.className = "Hero";
bare.zone = nil;
bare.level = nil;

ECS_CHECK(R.Update(row, bare) ~= nil, "3a: a bare character still updates");
ECS_EQ(row:GetID(), 5, "3b: real index still set");
ECS_EQ(state.zone:GetText(), C.FALLBACK_ZONE, "3c: a missing zone renders the Unknown Zone fallback");
ECS_EQ(state.badge:GetText(), "??", "3d: the level badge shows ?? too");
ECS_CHECK(not state.classIcon:IsShown(), "3d2: unknown classes do not inherit a stale class badge");

-- 3e: an unknown race/class do not require a text line in the compact row
ECS_CHECK(not state.noteText:IsShown(), "3e: no note line appears without a note");
-- 3e: a nil faction falls back to the neutral border colour rather than erroring
ECS_CHECK(row.__borderColor ~= nil, "3f: a border colour is still applied");

-- ---------------------------------------------------------------- 4. selection and hover
R.Update(row, MakeCharacter(6));
local idleVertex = { state.tint.__vertex[1], state.tint.__vertex[2],
                     state.tint.__vertex[3], state.tint.__vertex[4] };
ECS_CHECK(idleVertex[4] == 0, "4a: idle tint is fully transparent");

ECS_CHECK(R.SetSelected(row, true) == true, "4b: selection reports a change");
ECS_CHECK(R.IsSelected(row), "4c: selected state recorded");
ECS_EQ(state.statusArt:GetTexture(), C.TEX.selectedPlate, "4d: selected row uses the gold plate");
ECS_CHECK(state.statusArt:IsShown() and state.statusArt:GetAlpha() == 1,
    "4d2: selected plate is visible at full strength");
ECS_EQ(state.idleArt:GetAlpha(), 0, "4d3: gold selection replaces the idle grey plate");
ECS_CHECK(R.SetSelected(row, true) == false, "4e: selecting again is a no-op");
R.SetSelected(row, false);
ECS_CHECK(state.tint.__vertex[4] == 0, "4f: deselecting clears the tint");
ECS_CHECK(not state.statusArt:IsShown(), "4f2: deselecting hides the selection plate");
ECS_EQ(state.idleArt:GetAlpha(), 1, "4f3: deselecting restores the idle grey plate");

ECS_CHECK(R.SetHovered(row, true) == true, "4g: hover reports a change");
ECS_CHECK(R.IsHovered(row), "4h: hovered state recorded");
ECS_EQ(state.statusArt:GetTexture(), C.TEX.allianceHoverPlate, "4i: Alliance hover uses the blue plate");
ECS_CHECK(state.statusArt:IsShown() and state.statusArt:GetAlpha() == 1,
    "4i2: direct hover shows the plate at full strength");
ECS_EQ(state.idleArt:GetAlpha(), 0, "4i3: full Alliance hover replaces the grey plate");

-- 4j: selection must out-rank hover
R.SetSelected(row, true);
local selectedPlate = state.statusArt:GetTexture();
R.SetHovered(row, false);
ECS_EQ(state.statusArt:GetTexture(), selectedPlate,
    "4j: hover changes cannot replace the selected plate");
ECS_EQ(state.statusArt:GetTexture(), C.TEX.selectedPlate,
    "4j2: selected gold art outranks faction hover art");
R.SetSelected(row, false);

-- 4k: the accent is the faction colour, used as an accent only (spec 27)
R.Update(row, MakeCharacter(7, { factionAccent = { 0.8, 0.2, 0.2 } }));
ECS_CHECK(math.abs(row.__borderColor[1] - 0.8) < 1e-6,
    "4k: border takes the faction accent");
R.SetSelected(row, true);
ECS_CHECK(math.abs(row.__borderColor[1] - 0.8) < 1e-6,
    "4l: selection does not replace the faction accent with a solid fill");
R.SetSelected(row, false);

-- 4m/4n/4o: selection is represented by the supplied gold art, not a flat tint.
R.Update(row, MakeCharacter(8));
R.SetSelected(row, true);
ECS_EQ(state.statusArt:GetTexture(), C.TEX.selectedPlate,
    "4m: the selected state uses the supplied gold art");
ECS_CHECK(state.statusArt:GetAlpha() > state.tint.__vertex[4],
    "4n: selection art is stronger than the transparent drag surface");
ECS_EQ(state.tint.__vertex[4], 0, "4o: selection does not add a competing flat tint");
R.SetSelected(row, false);

-- Faction-specific hover artwork; the selected gold plate remains the top state.
R.Update(row, MakeCharacter(9, { factionID = 2, factionName = "Horde" }));
R.SetHovered(row, true);
ECS_EQ(state.statusArt:GetTexture(), C.TEX.hordeHoverPlate, "4p: Horde hover uses the red plate");
R.SetSelected(row, true);
ECS_EQ(state.statusArt:GetTexture(), C.TEX.selectedPlate, "4q: Gold selection overrides Horde hover");
R.SetSelected(row, false);
R.SetHovered(row, false);

R.Update(row, MakeCharacter(10, {
    factionID = 3, factionName = "Freeborn", factionEmblem = C.TEX.freebornBadge,
}));
ECS_EQ(state.emblem:GetTexture(), C.TEX.freebornBadge,
    "4r1: Freeborn rows show the Freeborn logo");
R.SetHovered(row, true);
ECS_EQ(state.statusArt:GetTexture(), C.TEX.freebornHoverPlate,
    "4r: Freeborn hover uses the purple Large backdrop");
R.SetHovered(row, false);

R.Update(row, MakeCharacter(11, { factionID = 0, factionName = "Neutral" }));
R.SetHovered(row, true);
ECS_CHECK(not state.statusArt:IsShown(), "4s: unknown factions retain the grey backdrop on hover");
R.SetHovered(row, false);

-- ---------------------------------------------------------------- 5. reset (spec 25)
-- THE critical antialiasing test: a recycled row must not show anything from the
-- character it previously displayed.
R.Update(row, MakeCharacter(9, { note = "secret", zone = "Undercity" }));
R.SetHovered(row, true);
ECS_EQ(state.idleArt:GetAlpha(), 0, "5pre: hover crossfade temporarily clears idle grey");
R.Reset(row);

ECS_EQ(R.GetCharacter(row), nil, "5a: character reference cleared");
ECS_EQ(row:GetID(), 9, "5b: hidden rows retain their last valid numeric id");
ECS_CHECK(not R.IsSelected(row), "5c: selection cleared");
ECS_CHECK(not R.IsHovered(row), "5d: hover cleared");
ECS_EQ(state.name:GetText(), "", "5e: name text cleared");
ECS_EQ(state.zone:GetText(), "", "5f: zone cleared");
ECS_EQ(state.noteText:GetText(), "", "5g: note text cleared");
ECS_CHECK(not state.noteText:IsShown(), "5g2: note line hidden after reset");
ECS_EQ(state.badge:GetText(), "", "5h: badge cleared");
ECS_CHECK(not state.noteDot:IsShown(), "5i: note dot hidden");
ECS_EQ(state.portrait:GetTexture(), nil, "5j: portrait texture cleared");
ECS_EQ(state.classIcon:GetTexture(), nil, "5j2: class badge texture cleared");
ECS_CHECK(not state.classIcon:IsShown(), "5j3: class badge hidden after reset");
ECS_EQ(state.emblem:GetTexture(), nil, "5k: emblem texture cleared");
ECS_CHECK(state.tint.__vertex[4] == 0, "5l: tint cleared");
ECS_CHECK(not state.statusArt:IsShown() and state.statusArt:GetTexture() == nil,
    "5l2: recycled rows clear their previous hover/selection art");
ECS_CHECK(state.idleArt:IsShown() and state.idleArt:GetTexture() == C.TEX.idlePlate,
    "5l2a: recycled rows retain the grey idle art");
ECS_EQ(state.idleArt:GetAlpha(), 1, "5l2b: recycled rows restore full idle grey");
ECS_EQ(state.portraitBorder:GetTexture(), C.TEX.portraitBorder,
    "5l3: the reusable portrait border remains assigned");

-- 5m: updating with nil blanks the row rather than leaving stale data
R.Update(row, MakeCharacter(10));
R.Update(row, nil);
ECS_EQ(state.name:GetText(), "", "5m: Update(nil) blanks the row");
ECS_EQ(R.GetCharacter(row), nil, "5n: and clears the character");
ECS_CHECK(not row:IsShown(), "5o: and hides it");

-- 5p: the full recycle cycle - after reuse, ONLY the new character's data shows
R.Update(row, MakeCharacter(11, { zone = "Orgimmar", note = "old note" }));
R.Reset(row);
R.Update(row, MakeCharacter(12, { zone = "Ironforge", note = nil }));
ECS_EQ(row:GetID(), 12, "5p: recycled row carries the new real index");
ECS_EQ(state.name:GetText(), "Char12", "5q: recycled row shows the new name");
ECS_EQ(state.zone:GetText(), "Ironforge", "5r: recycled row shows the new zone");
ECS_CHECK(state.name:GetText() ~= "Char11", "5s: no bleed-through of the previous character");
ECS_CHECK(not state.noteDot:IsShown(),
    "5t: the previous character's note indicator did not survive recycling");
ECS_CHECK(not state.noteText:IsShown(),
    "5u: the previous character's note text did not survive recycling");

-- ---------------------------------------------------------------- 6. search highlight
-- Colour codes are inserted AROUND the matched run, so the name is no longer
-- contiguous in the raw string. The meaningful assertion is therefore that the
-- VISIBLE text is unchanged once colour codes are stripped.
local function StripColour(text)
    -- WoW colour codes are |c followed by EIGHT hex digits (AARRGGBB).
    local stripped = string.gsub(text or "", "|c%x%x%x%x%x%x%x%x", "")
    stripped = string.gsub(stripped, "|r", "")
    return stripped
end

ECS.Search.Reset();
ECS.Order.SetCharacters({ MakeCharacter(20, { name = "Nathanie" }) });
R.Update(row, MakeCharacter(20, { name = "Nathanie" }));
ECS_CHECK(string.find(state.name:GetText(), "|c", 1, true) == nil,
    "6a: no colour codes when the search is inactive");

ECS.Search.SetQuery("than");
R.Update(row, MakeCharacter(20, { name = "Nathanie" }));
local highlighted = state.name:GetText();
ECS_CHECK(string.find(highlighted, "|c", 1, true) ~= nil,
    "6b: match is colour-highlighted when the search is active");
ECS_EQ(StripColour(highlighted), "Nathanie",
    "6c: the visible name is unchanged by highlighting");
ECS_CHECK(string.find(highlighted, "than", 1, true) ~= nil,
    "6d: the matched run itself is present");

-- 6e: a name with no match is not highlighted
R.Update(row, MakeCharacter(20, { name = "Zach" }));
ECS_CHECK(string.find(state.name:GetText(), "|c", 1, true) == nil,
    "6e: an unmatched name is left plain");
ECS_EQ(state.name:GetText(), "Zach", "6f: and renders verbatim");
ECS.Search.Reset();

-- ---------------------------------------------------------------- 7. offsets
ECS_CHECK(R.SetOffsetX(row, 4) == true, "7a: offset reports a change");
ECS_EQ(R.GetOffsetX(row), 4, "7b: offset stored");
ECS_CHECK(R.SetOffsetX(row, 4) == false, "7c: same offset is a no-op");
R.Reset(row);
ECS_EQ(R.GetOffsetX(row), 0, "7d: reset clears the offset");

-- ---------------------------------------------------------------- 8. shim sanity
-- The shim must fail loudly on an unimplemented Set* call, so a typo in ECS_Row
-- surfaces as a test failure instead of silently doing nothing.
local ok = pcall(function() return row:SetSomethingNotImplemented(1) end);
ECS_CHECK(ok == false, "8a: the shim rejects unimplemented Set* methods");

-- ---------------------------------------------------------------- 9. stock row art
-- The stock UpdateCharacterList SHOWS a `GeneralBackground` plate on every populated
-- row - 243x62 from uicharacterselectglues2x - at BACKGROUND sublevel 1, which is
-- ABOVE the backdrop and above ECS's own tint at sublevel 0. ECS draws a flat tile,
-- so the plate has to be hidden, and hidden on EVERY refresh: the stock pass re-shows
-- it each time it binds a row, while ECS_Row.Build only ever runs once per button.
local stockRow = MakeRow("ECSStockPlateTest1");
local plate = stockRow:CreateTexture("ECSStockPlateTest1GeneralBackground", "BACKGROUND", nil, 1);
plate:Show();
ECS_CHECK(plate:IsShown(), "9a: the stock plate is shown, as the stock pass leaves it");

R.Update(stockRow, MakeCharacter(11));
ECS_CHECK(not plate:IsShown(), "9b: ECS hides the stock GeneralBackground plate");

-- 9c: and again after the stock pass has re-shown it, which is the case a Build-time
-- fix alone would miss
plate:Show();
R.Update(stockRow, MakeCharacter(11));
ECS_CHECK(not plate:IsShown(), "9c: ... and suppresses it again on the next refresh");

-- 9d: the adopted fabric icon must NOT be hidden - the Freeborn wrapper looks it up
-- by name, and ECS re-anchors it as the row's emblem
local emblem = _G["ECSStockPlateTest1FactionIcon"];
ECS_CHECK(emblem ~= nil, "9d: the stock FactionIcon child is adopted, not discarded");

-- 9e-9h: the stock TEXT has to go too. The populated loop writes a whole row
-- presentation into ButtonTextName/Level/Separator/Class/Zone/Status at OVERLAY
-- level, anchored to the button's TOPLEFT - which is ABOVE ECS's ARTWORK portrait and
-- level with ECS's own text. Left alone, every row drew the stock name/level/class
-- over ECS's portrait AND alongside ECS's own name/zone. The shim has no stock
-- regions, so only an explicit fixture can catch this.
local textSuffixes = {
    "ButtonTextName", "ButtonTextLevel", "ButtonTextSeparator",
    "ButtonTextClass", "ButtonTextZone", "ButtonTextStatus",
};
local stockText = {};
for index = 1, #textSuffixes do
    local region = stockRow:CreateFontString(
        "ECSStockPlateTest1" .. textSuffixes[index], "OVERLAY");
    region:SetText("STOCK");
    region:Show();
    stockText[index] = region;
end
local legacyStockText = stockRow:CreateFontString("ECSStockLegacyText", "OVERLAY");
legacyStockText:SetText("LEGACY STOCK TEXT");
local legacyStockPlate = stockRow:CreateTexture("ECSStockLegacyPlate", "BACKGROUND");
legacyStockPlate:SetTexture("stock-plate");
R.Update(stockRow, MakeCharacter(12));

local function CountShown(regions)
    local shown = 0;
    for index = 1, #regions do
        if ( regions[index]:IsShown() ) then
            shown = shown + 1;
        end
    end
    return shown;
end

ECS_EQ(CountShown(stockText), 0, "9e: every stock row FontString is suppressed");
ECS_CHECK(not legacyStockText:IsShown(), "9e2: unlisted stock FontStrings are swept too");
ECS_EQ(legacyStockPlate:GetAlpha(), 0, "9e3: unlisted stock textures are made transparent");

-- 9f: and again after the stock pass re-shows them, which a Build-time fix would miss
for index = 1, #stockText do
    stockText[index]:SetText("STOCK AGAIN");
    stockText[index]:Show();
end
legacyStockText:Show();
legacyStockPlate:Show();
R.Update(stockRow, MakeCharacter(12));
ECS_EQ(CountShown(stockText), 0, "9f: and suppressed again on the next refresh");
ECS_CHECK(not legacyStockText:IsShown(), "9f2: extra text cannot resurface after Show()");
ECS_EQ(legacyStockPlate:GetAlpha(), 0, "9f3: extra art remains transparent after Show()");

-- 9g/9h: ECS's OWN text must survive that sweep. It is created unnamed, so a
-- name-based sweep cannot touch it - this pins that, because "hide everything named
-- ButtonText*" would be a plausible and wrong over-correction.
local ownText = ECS.Row.State(stockRow).name;
ECS_CHECK(ownText ~= nil, "9g: the row still has its own name FontString");
ECS_CHECK(ownText:IsShown() ~= false, "9h: ECS's own text is not hidden by the sweep");

_G.CLASS_ICON_TCOORDS = savedClassIconCoords;
