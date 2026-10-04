--[==[ test_search.lua ------------------------------------------------------------
    Proves the search field's semantics: what is typed versus what is matched,
    Escape behaviour, the summary/empty states, and match highlighting (spec 8,
    30, 31).
]==]

local S = ECS.Search;
local O = ECS.Order;
local C = ECS.Const;

-- ---------------------------------------------------------------- fixtures
local function MakeCharacter(realIndex, name, race, class, level, zone)
    return {
        realIndex = realIndex,
        stableKey = "esteria:" .. string.lower(name),
        name = name, raceName = race, className = class,
        level = level, zone = zone, factionName = "Alliance",
    };
end

local function SampleList()
    return {
        MakeCharacter(1, "Zach",       "High Elf", "Hero",  81, "Elwynn Forest"),
        MakeCharacter(2, "Auctioneer", "Human",    "Hero",   1, "Dun Morogh"),
        MakeCharacter(3, "Clunt",      "Orc",      "Hero",   3, "Undercity"),
        MakeCharacter(4, "Nat",        "High Elf", "Mage",  80, "Dalaran"),
        MakeCharacter(5, "Tubby",      "Gnome",    "Rogue", 70, "Stormwind"),
    };
end

local function Reset(list)
    S.Reset();
    O.SetCustomOrder({});
    O.SetCharacters(list or SampleList());
end

Reset();

-- ---------------------------------------------------------------- 1. normalisation
ECS_EQ(S.Normalise("  Nat  "), "nat", "1a: trimmed and lower-cased");
ECS_EQ(S.Normalise("HIGH ELF"), "high elf", "1b: case folded, inner space kept");
ECS_EQ(S.Normalise(nil), "", "1c: nil becomes empty");
ECS_EQ(S.Normalise(42), "", "1d: a number becomes empty");
ECS_EQ(S.Normalise("a\0b"), "ab", "1e: control characters stripped");

-- 1f: the needle must be capped: it is matched against 100 blobs and echoed in
-- the summary line.
ECS_EQ(#S.Normalise(string.rep("x", 500)), S.MAX_LENGTH, "1f: over-long queries are capped");

-- ---------------------------------------------------------------- 2. state
Reset();
ECS_EQ(S.GetQuery(), "", "2a: starts empty");
ECS_CHECK(not S.IsActive(), "2b: not active initially");

local matches = S.SetQuery("nat");
ECS_EQ(matches, 1, "2c: SetQuery returns the match count");
ECS_EQ(S.GetQuery(), "nat", "2d: raw query remembered for the edit box");
ECS_EQ(S.GetNeedle(), "nat", "2e: needle normalised");
ECS_CHECK(S.IsActive(), "2f: active once text is entered");

-- 2g: the raw text is preserved verbatim even though the needle is normalised
S.SetQuery("  Nat  ");
ECS_EQ(S.GetQuery(), "  Nat  ", "2g: raw text kept as typed");
ECS_EQ(S.GetNeedle(), "nat", "2h: needle is normalised");

-- 2i: an all-whitespace query is not an active filter
S.SetQuery("   ");
ECS_CHECK(not S.IsActive(), "2i: whitespace-only query does not filter");

-- ---------------------------------------------------------------- 3. filtering
Reset();
S.SetQuery("mage");
ECS_EQ(O.VisibleCount(), 1, "3a: class match");
ECS_EQ(O.CharacterAt(1).name, "Nat", "3b: correct character");

S.SetQuery("80");
ECS_EQ(O.VisibleCount(), 1, "3c: level match");

S.SetQuery("high elf");
ECS_EQ(O.VisibleCount(), 2, "3d: race match spans two characters");

S.SetQuery("stormwind");
ECS_EQ(O.VisibleCount(), 1, "3e: zone match");
ECS_EQ(O.RealIndexAt(1), 5, "3f: real index preserved through search");

S.SetQuery("zzz");
ECS_EQ(O.VisibleCount(), 0, "3g: no matches is safe");
ECS_EQ(O.RealIndexAt(1), nil, "3h: out-of-range access returns nil");

-- 3i: clearing restores everything
ECS_CHECK(S.Clear() == true, "3i: Clear reports it was active");
ECS_EQ(O.VisibleCount(), 5, "3j: full roster restored");
ECS_CHECK(not S.IsActive(), "3k: no longer active");

-- 3L/3M: the placeholder TELLS THE USER which fields are searched, so it must not
-- name one a query cannot use. It used to read "Search characters...", which left
-- the user guessing; it now names the fields the blob actually carries. These bind
-- the wording to the behaviour, so the copy cannot drift away from the search.
--
-- Placed AFTER the 3h-3k block on purpose: those assert against the still-active
-- "zzz" filter, so resetting the query before them (as a first draft of this did)
-- silently changes what they test.
Reset();
local claims = {
    { word = "name",  needle = "nat",      expected = 1 },
    { word = "class", needle = "mage",     expected = 1 },
    { word = "race",  needle = "high elf", expected = 2 },
    { word = "level", needle = "80",       expected = 1 },
};
for index = 1, #claims do
    local claim = claims[index];
    ECS_CHECK(string.find(C.SEARCH_PLACEHOLDER, claim.word, 1, true) ~= nil,
        "3L" .. index .. ": the placeholder names " .. claim.word);
    S.SetQuery(claim.needle);
    ECS_EQ(O.VisibleCount(), claim.expected,
        "3M" .. index .. ": ... and a query really matches " .. claim.word);
end
S.Reset();

-- ---------------------------------------------------------------- 4. summary
Reset();
ECS_EQ(S.Summary(), "5 characters", "4a: unfiltered summary");

O.SetCharacters({ MakeCharacter(1, "Solo", "Human", "Hero", 1, "X") });
ECS_EQ(S.Summary(), "1 character", "4b: singular form");

Reset();
S.SetQuery("high elf");
ECS_EQ(S.Summary(), "2 of 5", "4c: filtered summary");

S.SetQuery("zzz");
ECS_EQ(S.Summary(), "No matches", "4d: empty result summary");
ECS_CHECK(S.IsEmptyResult(), "4e: empty-result state reported");
ECS_CHECK(not S.IsRosterEmpty(), "4f: the account is not actually empty");

S.Clear();
ECS_CHECK(not S.IsEmptyResult(), "4g: no empty-result state when unfiltered");

-- 4h: a genuinely empty account is a different state (spec 31)
Reset({});
ECS_EQ(S.Summary(), "", "4h: empty account has no summary");
ECS_CHECK(S.IsRosterEmpty(), "4i: empty roster reported");
ECS_CHECK(not S.IsEmptyResult(), "4j: an empty account is not an empty RESULT");

-- ---------------------------------------------------------------- 5. escape
Reset();
S.SetQuery("nat");
ECS_CHECK(S.HandleEscape() == true, "5a: Escape clears an active search");
ECS_CHECK(not S.IsActive(), "5b: search cleared");
ECS_EQ(S.GetQuery(), "", "5c: raw query cleared too");

-- 5d: Escape with nothing to clear is NOT consumed, so the caller can close the screen
ECS_CHECK(S.HandleEscape() == false, "5d: Escape with an empty box is not consumed");

-- ---------------------------------------------------------------- 6. highlight
Reset();
S.SetQuery("nat");
local startIndex, endIndex = S.MatchRange("Nat");
ECS_CHECK(startIndex == 1 and endIndex == 3, "6a: match range found in the name");
ECS_EQ(S.MatchRange("Zach"), nil, "6b: no range when the name does not contain the match");
ECS_EQ(S.MatchRange(nil), nil, "6c: nil text is safe");

-- 6d: matching is case-insensitive
local s2, e2 = S.MatchRange("NATHANIEL");
ECS_CHECK(s2 == 1 and e2 == 3, "6d: range is case-insensitive");

-- 6e: an inactive search never highlights
S.Clear();
ECS_EQ(S.MatchRange("Nat"), nil, "6e: no highlight when the search is inactive");

-- 6f: Split yields the three runs a FontString needs
S.SetQuery("nat");
local before, match, after = S.Split("Nathanie");
ECS_EQ(before, "", "6g: leading run");
ECS_EQ(match, "Nat", "6h: matched run preserves original casing");
ECS_EQ(after, "hanie", "6i: trailing run");

local b2, m2, a2 = S.Split("Zach");
ECS_EQ(b2, "Zach", "6j: unmatched text is returned whole");
ECS_EQ(m2, "", "6k: no matched run");
ECS_EQ(a2, "", "6l: no trailing run");

-- 6m: a match in the middle splits correctly.
-- "Nathanie" (N-a-t-h-a-n-i-e) with the needle "than" matches at index 3..6.
S.SetQuery("than");
local b3, m3, a3 = S.Split("Nathanie");
ECS_EQ(b3, "Na", "6n: middle match leading run");
ECS_EQ(m3, "than", "6o: middle match run");
ECS_EQ(a3, "ie", "6p: middle match trailing run");

-- 6q: Split tolerates nil
local b4, m4 = S.Split(nil);
ECS_EQ(b4, "", "6q: Split(nil) is safe");
ECS_EQ(m4, "", "6r: Split(nil) has no match");

-- ---------------------------------------------------------------- 7. reset
S.SetQuery("nat");
S.Reset();
ECS_CHECK(not S.IsActive(), "7a: Reset clears the filter");
ECS_EQ(S.GetQuery(), "", "7b: Reset clears the raw query");
