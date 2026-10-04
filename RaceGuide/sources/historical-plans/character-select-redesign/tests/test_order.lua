--[==[ test_order.lua -------------------------------------------------------------
    Proves the visual-index / real-index invariant (spec 24, 41).

    The single most important property: for every visible position i,
    realToVisual[ visible[i] ] == i, and every visible entry resolves back to a
    real character index that the client's SelectCharacter/DeleteCharacter/
    EnterWorld calls will accept.

    NOTE: this file uses a levelled long bracket (--[==[ ) because the comment
    text itself contains a double closing bracket. Plain --[[ would be closed
    early by that sequence, which is a genuine Lua footgun.
]==]

local O = ECS.Order;

-- ---------------------------------------------------------------- fixtures
local REALM = "Esteria";

-- Canonical stable key: realm and name are both case-insensitive in WoW, so the
-- key is fully lower-cased. ECS_Data must produce exactly this form.
local function StableKey(name)
    return string.lower(REALM) .. ":" .. string.lower(name);
end

local function MakeCharacter(realIndex, name, level, race, class, zone)
    return {
        realIndex   = realIndex,
        stableKey   = StableKey(name),
        name        = name,
        level       = level,
        raceName    = race,
        className   = class,
        zone        = zone,
        factionName = "Alliance",
    };
end

-- 6 characters, deliberately NOT in alphabetical order.
local function SampleList()
    return {
        MakeCharacter(1, "Zach",      81, "High Elf", "Hero",   "Elwynn Forest"),
        MakeCharacter(2, "Auctioneer", 1, "Human",    "Hero",   "Dun Morogh"),
        MakeCharacter(3, "Clunt",      3, "Orc",      "Hero",   "Undercity"),
        MakeCharacter(4, "Nat",       80, "High Elf", "Mage",   "Dalaran"),
        MakeCharacter(5, "Tubby",     70, "Gnome",    "Rogue",  "Stormwind"),
        MakeCharacter(6, "Greg",       1, "Sethrak",  "Hunter", "Orgrimmar"),
    };
end

local function Reset(list)
    O.SetFilter("");
    O.SetCustomOrder({});
    O.SetCharacters(list or {});
end

local function NamesInVisualOrder()
    local names = {};
    for i = 1, O.VisibleCount() do
        local c = O.CharacterAt(i);
        names[#names + 1] = c and c.name or "?";
    end
    return table.concat(names, ",");
end

-- The invariant, checked on whatever state is current.
local function AssertInverseMapping(label)
    local visible = O.visible;
    local ok = true;
    for i = 1, #visible do
        local realIndex = visible[i];
        if ( O.realToVisual[realIndex] ~= i ) then
            ok = false;
            ECS_CHECK(false, label .. ": realToVisual[" .. tostring(realIndex)
                .. "] ~= " .. tostring(i));
        end
        if ( O.characters[realIndex] == nil ) then
            ok = false;
            ECS_CHECK(false, label .. ": visible[" .. tostring(i)
                .. "] does not resolve to a character");
        end
    end
    if ( ok ) then
        ECS_CHECK(true, label .. ": inverse mapping holds across " .. #visible .. " entries");
    end
end

-- ============================================================ 1. server order
Reset(SampleList());
ECS_EQ(O.VisibleCount(), 6, "1a: all characters visible with no filter/order");
ECS_EQ(O.RealIndexAt(1), 1, "1b: first visible is real index 1");
ECS_EQ(O.RealIndexAt(6), 6, "1c: last visible is real index 6");
AssertInverseMapping("1d");

-- ============================================================ 2. custom order
Reset(SampleList());
O.SetCustomOrder({ "esteria:nat", "esteria:zach", "esteria:greg" });
ECS_EQ(NamesInVisualOrder(), "Nat,Zach,Greg,Auctioneer,Clunt,Tubby",
    "2a: saved order first, unseen characters appended in server order");
ECS_EQ(O.VisibleCount(), 6, "2b: custom order does not drop characters");
AssertInverseMapping("2c");

-- 2d: the crucial case - visual position must NOT be assumed equal to real index
ECS_EQ(O.RealIndexAt(1), 4, "2d: visual 1 is real index 4 (Nat)");
ECS_EQ(O.VisualPosOf(4), 1, "2e: real 4 is at visual position 1");
ECS_EQ(O.VisualPosOf(1), 2, "2f: real 1 (Zach) moved to visual position 2");

-- ============================================================ 3. filtering
Reset(SampleList());
O.SetFilter("nat");
ECS_EQ(O.VisibleCount(), 1, "3a: name filter matches one character");
ECS_EQ(O.RealIndexAt(1), 4, "3b: filter preserves the REAL index");
AssertInverseMapping("3c");

O.SetFilter("high elf");
ECS_EQ(O.VisibleCount(), 2, "3d: race filter matches two characters");

O.SetFilter("mage");
ECS_EQ(O.VisibleCount(), 1, "3e: class filter");
ECS_EQ(O.RealIndexAt(1), 4, "3f: class filter resolves to Nat");

O.SetFilter("80");
ECS_EQ(O.VisibleCount(), 1, "3g: level filter");
ECS_EQ(O.RealIndexAt(1), 4, "3h: level filter resolves to Nat");

O.SetFilter("stormwind");
ECS_EQ(O.VisibleCount(), 1, "3i: zone filter");
ECS_EQ(O.RealIndexAt(1), 5, "3j: zone filter resolves to Tubby");

O.SetFilter("  MAGE  ");
ECS_EQ(O.VisibleCount(), 1, "3k: filter is trimmed and case-insensitive");

O.SetFilter("zzzznotfound");
ECS_EQ(O.VisibleCount(), 0, "3l: empty result is safe");
ECS_EQ(O.RealIndexAt(1), nil, "3m: out-of-range visual returns nil, not an error");
AssertInverseMapping("3n");

-- ============================================================ 4. filtered selection
Reset(SampleList());
O.SetFilter("mage");
ECS_CHECK(O.IsFilteredOut(1) == true, "4a: Zach is filtered out");
ECS_CHECK(O.IsFilteredOut(4) == false, "4b: Nat is visible");
ECS_CHECK(O.IsFilteredOut(0) == false, "4c: no selection is never 'filtered out'");
ECS_EQ(O.VisibleCount(), 1, "4d: only the match is shown");

-- spec 8: keep the real selection, show no selected row while filtered out.
-- The invariant that matters: filtering never changes which real index is 1st.
O.SetFilter("");
ECS_EQ(O.RealIndexAt(1), 1, "4e: clearing the filter restores server order");

-- ============================================================ 5. reordering
Reset(SampleList());
ECS_CHECK(O.MoveCharacter(1, 3) == true, "5a: move reports a change");
-- Dragging row 1 down to slot 3: the dragged character lands AT slot 3 and rows
-- 2..3 shift up. Zach(real 1) => slot 3, so order is 2,3,1,4,5,6.
ECS_EQ(NamesInVisualOrder(), "Auctioneer,Clunt,Zach,Nat,Tubby,Greg",
    "5b: dragging visual 1 to visual 3 shifts the rows between them up");
AssertInverseMapping("5c");

-- 5d: after a reorder the real indices must be untouched
local byName = {};
for i = 1, O.VisibleCount() do
    local c = O.CharacterAt(i);
    byName[c.name] = c.realIndex;
end
ECS_EQ(byName["Zach"], 1, "5d: Zach still has real index 1 after reorder");
ECS_EQ(byName["Nat"], 4, "5e: Nat still has real index 4 after reorder");

-- 5f: reordering while a filter is active must still produce a global order
Reset(SampleList());
O.SetFilter("e");
O.MoveCharacter(1, 2);
ECS_CHECK(O.GetCustomOrder() ~= nil, "5f: reorder with an active filter does not error");
AssertInverseMapping("5g");

-- ============================================================ 6. delete
Reset(SampleList());
O.SetCustomOrder({ "esteria:nat", "esteria:zach" });
local removed = O.RemoveFromOrder(4);   -- Nat
ECS_CHECK(removed == true, "6a: deleting a saved character removes its order entry");
ECS_EQ(table.concat(O.GetCustomOrder(), ","), "esteria:zach",
    "6b: only the deleted key is dropped");

-- 6c: a stale key for a character that no longer exists is pruned on rebuild
Reset(SampleList());
O.SetCustomOrder({ "esteria:nat", "esteria:ghost" });
ECS_EQ(O.VisibleCount(), 6, "6c: stale order key does not reduce the roster");
ECS_EQ(table.concat(O.GetCustomOrder(), ","), "esteria:nat",
    "6d: stale key pruned from the persisted order");

-- ============================================================ 7. new character
Reset(SampleList());
O.SetCustomOrder({ "esteria:nat", "esteria:zach" });
local grown = SampleList();
grown[7] = MakeCharacter(7, "Brandnew", 1, "Vulpera", "Hero", "Dalaran");
O.SetCharacters(grown);
ECS_EQ(O.VisibleCount(), 7, "7a: newly created character appears");
ECS_EQ(O.RealIndexAt(7), 7, "7b: new character lands at the tail");
ECS_EQ(O.RealIndexAt(1), 4, "7c: saved order still leads");

-- ============================================================ 8. tolerate junk
Reset(SampleList());
O.SetCustomOrder({ "", 17, "esteria:zach", {}, "esteria:zach" });
ECS_CHECK(true, "8a: malformed order entries do not raise");
ECS_EQ(O.VisibleCount(), 6, "8b: roster survives a malformed order");
ECS_EQ(O.RealIndexAt(1), 1, "8c: duplicated key does not scramble the list (first wins)");
AssertInverseMapping("8d");

-- 8e/8f: junk tolerance has to be tested at the STORE boundary, because the
-- table a loaded record produces is what actually reaches the order - the
-- persisted text itself is ECS_Persistence's job (see test_persistence). An
-- O.Deserialise used to be tested here instead; production never called it, so
-- the assertions covered a dead path while the live one went unexercised.
--
-- The keys must be REAL roster keys: SetCustomOrder prunes anything the roster
-- does not contain, so a made-up key would be dropped for that reason and the
-- assertion would pass for the wrong one.
O.SetCustomOrder(nil);
ECS_EQ(#O.GetCustomOrder(), 0, "8e: a store carrying no order leaves an empty order");
O.SetCustomOrder({ "", "esteria:nat", "", "esteria:zach" });
ECS_EQ(table.concat(O.GetCustomOrder(), ","), "esteria:nat,esteria:zach",
    "8f: empty segments dropped");

-- 8g: REGRESSION - a saved order loaded BEFORE the character list arrives must be
-- kept. Pruning against an empty roster used to discard the whole order, which is
-- exactly what the login screen would do.
Reset({});                                    -- no characters yet
O.SetCustomOrder({ "esteria:nat", "esteria:zach" });
ECS_EQ(#O.GetCustomOrder(), 2, "8g: order survives being set with an empty roster");
O.SetCharacters(SampleList());                -- the server list arrives later
ECS_EQ(#O.GetCustomOrder(), 2, "8h: order still intact once characters arrive");
ECS_EQ(NamesInVisualOrder(), "Nat,Zach,Auctioneer,Clunt,Tubby,Greg",
    "8i: the pre-loaded order is applied once characters exist");

-- 8j: but a key for a genuinely absent character IS pruned once we have a roster
Reset(SampleList());
O.SetCustomOrder({ "esteria:nat", "esteria:ghost" });
ECS_EQ(table.concat(O.GetCustomOrder(), ","), "esteria:nat",
    "8j: a stale key is pruned when a real roster is present");

-- ============================================================ 9. empty roster
Reset({});
ECS_EQ(O.VisibleCount(), 0, "9a: zero characters is safe");
ECS_EQ(O.RealIndexAt(1), nil, "9b: no rows resolve");
AssertInverseMapping("9c");

-- ============================================================ 10. 100 characters
-- spec 9 / 41: a 100-character roster must map correctly with no overlap.
local big = {};
local expectedNames = {};
for i = 1, 100 do
    local name = string.format("Char%03d", i);
    big[i] = MakeCharacter(i, name, (i % 80) + 1, "Human", "Hero", "Stormwind");
    expectedNames[i] = name;
end
Reset(big);
ECS_EQ(O.VisibleCount(), 100, "10a: all 100 characters visible");

-- no visual position may map to two different real indices, and every real
-- index must appear exactly once
local seen = {};
local duplicates = 0;
for i = 1, 100 do
    local realIndex = O.RealIndexAt(i);
    if ( seen[realIndex] ) then
        duplicates = duplicates + 1;
    end
    seen[realIndex] = true;
    if ( realIndex ~= i ) then
        ECS_CHECK(false, "10b: unfiltered 100-roster should preserve server order at " .. i);
        break;
    end
end
ECS_EQ(duplicates, 0, "10c: no real index appears twice");
AssertInverseMapping("10d");

-- 10e: a filter over a large roster still maps correctly
O.SetFilter("char01");
ECS_EQ(O.VisibleCount(), 10, "10e: prefix filter over 100 characters");
for i = 1, O.VisibleCount() do
    local c = O.CharacterAt(i);
    if ( not string.find(c.name, "Char01", 1, true) ) then
        ECS_CHECK(false, "10f: filter leaked a non-matching character: " .. c.name);
    end
end
AssertInverseMapping("10g");

-- 10h: reorder at scale keeps the mapping total
O.SetFilter("");
O.MoveCharacter(1, 100);
ECS_EQ(O.VisibleCount(), 100, "10h: reorder at scale keeps all characters");
ECS_EQ(O.RealIndexAt(100), 1, "10i: moved character is now last");
ECS_EQ(O.RealIndexAt(99), 100, "10j: former last character shifted up");
AssertInverseMapping("10k");
