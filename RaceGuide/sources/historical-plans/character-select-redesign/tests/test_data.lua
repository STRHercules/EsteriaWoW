--[==[ test_data.lua --------------------------------------------------------------
    Proves the normalized data layer is correct under BOTH possible
    GetCharacterInfo signatures, and that malformed rows degrade instead of
    raising (spec 23, 33).
]==]

local D = ECS.Data;
local C = ECS.Const;

local DEPS = { realm = "Esteria", model = "HIGHELF" };

-- ------------------------------------------------- 1. fork layout (field 6 = sex)
-- name, race, class, level, zone, sex, ghost, PCC, PRC, PFC
local fork = D.FromFields(1, { "Zach", 13, 2, 81, "Elwynn Forest", 0, false, 0, 0, 0 }, DEPS);
ECS_CHECK(fork ~= nil, "1a: fork-layout row parses");
ECS_EQ(fork.name, "Zach", "1b: name");
ECS_EQ(fork.level, 81, "1c: level");
ECS_EQ(fork.zone, "Elwynn Forest", "1d: zone");
ECS_EQ(fork.sex, 0, "1e: sex read from field 6 (fork)");
ECS_EQ(fork.raceName, "High Elf", "1f: race resolved from the model string");
ECS_EQ(fork.stableKey, "esteria:zach", "1g: stable key is lower-cased");
ECS_CHECK(fork.portrait ~= nil and string.find(fork.portrait, "HighElfMale", 1, true) ~= nil,
    "1h: portrait path");

-- The target Dev ChrRaces table uses 30/31 for Horde/Alliance Illidari. The
-- background model may be the shared "Illidari" token, so the real ID must pick
-- the faction-specific portrait rather than falling through to Unknown Race.
local illidariHorde = D.FromFields(7,
    { "Fel", 30, 4, 80, "Shadowmoon Valley", 0, false },
    { realm = "Esteria", model = "Illidari" });
local illidariAlliance = D.FromFields(8,
    { "Vengeance", 31, 4, 80, "Shadowmoon Valley", 1, false },
    { realm = "Esteria", model = "Illidari" });
ECS_EQ(illidariHorde.raceName, "Illidari", "1i: Horde Illidari race ID resolves despite the shared model token");
ECS_EQ(illidariAlliance.raceName, "Illidari", "1j: Alliance Illidari race ID resolves despite the shared model token");
ECS_EQ(illidariHorde.raceArtKey, "DemonHunterHorde", "1k: Horde Illidari chooses Horde portrait art");
ECS_EQ(illidariAlliance.raceArtKey, "DemonHunterAlliance", "1l: Alliance Illidari chooses Alliance portrait art");
ECS_EQ(illidariHorde.factionName, "Horde", "1m: Horde Illidari faction is retained");
ECS_EQ(illidariAlliance.factionName, "Alliance", "1n: Alliance Illidari faction is retained");
ECS_CHECK(string.find(illidariHorde.portrait, "DemonHunterHordeMale", 1, true) ~= nil,
    "1o: Horde Illidari portrait path exists");
ECS_CHECK(string.find(illidariAlliance.portrait, "DemonHunterAllianceFemale", 1, true) ~= nil,
    "1p: Alliance Illidari female portrait path exists");
local illidariFileHorde = D.FromFields(12,
    { "FelFile", "Illidari", 4, 80, "Shadowmoon Valley", "ILLIDARI_HORDE", "HERO", 0, false, 0 },
    { realm = "Esteria", model = "ILLIDARI" });
local illidariFileAlliance = D.FromFields(13,
    { "FelFileA", "Illidari", 4, 80, "Shadowmoon Valley", "ILLIDARI_ALLIANCE", "HERO", 1, false, 0 },
    { realm = "Esteria", model = "ILLIDARI" });
ECS_EQ(illidariFileHorde.raceArtKey, "DemonHunterHorde",
    "1p2: stock raceFilename overrides the shared model token for Horde");
ECS_EQ(illidariFileAlliance.raceArtKey, "DemonHunterAlliance",
    "1p3: stock raceFilename overrides the shared model token for Alliance");
ECS_CHECK(string.find(illidariFileHorde.portrait, "DemonHunterHordeMale", 1, true) ~= nil,
    "1p4: Horde raceFilename resolves the Horde portrait");
ECS_CHECK(string.find(illidariFileAlliance.portrait, "DemonHunterAllianceFemale", 1, true) ~= nil,
    "1p5: Alliance raceFilename resolves the Alliance portrait");
local illidariModelAlliance = D.FromFields(14,
    { "FelModelA", "Illidari", 4, 80, "Shadowmoon Valley", "ILLIDARI", "HERO", 1, false, 0 },
    { realm = "Esteria", model = "Character\\Illidari\\Illidari_Alliance.mdx" });
ECS_EQ(illidariModelAlliance.raceArtKey, "DemonHunterAlliance",
    "1p6: faction-qualified model wins over a generic raceFilename");
local illidariDisplayHorde = D.FromFields(9,
    { "FelName", "Illidari", 4, 80, "Shadowmoon Valley", 0, false },
    { realm = "Esteria", model = "Character\\Illidari\\Illidari_Horde.mdx" });
local illidariDisplayAlliance = D.FromFields(10,
    { "VengeanceName", "Illidari", 4, 80, "Shadowmoon Valley", 1, false },
    { realm = "Esteria", model = "Character\\Illidari\\Illidari_Alliance.mdx" });
ECS_EQ(illidariDisplayHorde.raceKnown, true, "1q: string race names resolve through model metadata");
ECS_EQ(illidariDisplayHorde.raceArtKey, "DemonHunterHorde", "1r: display-name Horde model keeps Horde art");
ECS_EQ(illidariDisplayAlliance.raceKnown, true, "1s: Alliance display-name race resolves");
ECS_EQ(illidariDisplayAlliance.raceArtKey, "DemonHunterAlliance", "1t: display-name Alliance model keeps Alliance art");
local illidariGeneric = D.FromFields(11,
    { "GenericFel", "Illidari", 4, 80, "Shadowmoon Valley", 0, false },
    { realm = "Esteria", model = "Character\\Illidari\\Illidari.mdx" });
ECS_EQ(illidariGeneric.raceName, "Illidari", "1u: shared Illidari model does not fall through to Unknown Race");
ECS_CHECK(illidariGeneric.portrait ~= nil, "1v: shared Illidari model still gets a portrait fallback");

-- ------------------------------------------------- 2. stock layout (field 6 = file string)
-- name, race, class, level, zone, raceFilename, classFilename, gender, ghost, PCC
local stock = D.FromFields(2, { "Nat", 4, 8, 80, "Dalaran", "NightElf", "MAGE", 1, false, 0 },
    { realm = "Esteria", model = "NIGHTELF" });
ECS_CHECK(stock ~= nil, "2a: stock-layout row parses");
ECS_EQ(stock.sex, 1, "2b: sex recovered from field 8 when field 6 is a filename");
ECS_EQ(stock.level, 80, "2c: level unaffected by the layout");
ECS_EQ(stock.zone, "Dalaran", "2d: zone unaffected");
ECS_CHECK(string.find(stock.portrait, "NightElfFemale", 1, true) ~= nil,
    "2e: female portrait chosen");

-- 2f: an ambiguous field 6 that is neither a valid sex nor a string is ignored
local amb = D.FromFields(3, { "Odd", 1, 1, 10, "X", 7, nil, 1, nil, nil }, DEPS);
ECS_EQ(amb.sex, 1, "2f: unusable field 6 falls through to field 8");

-- 2g: no usable sex at all -> nil, and the portrait still resolves (male plate)
local noSex = D.FromFields(4, { "Plain", 1, 1, 10, "X", "Human", "WARRIOR", 9, nil, nil }, DEPS);
ECS_EQ(noSex.sex, nil, "2g: no valid sex yields nil");
ECS_CHECK(noSex.portrait ~= nil, "2h: portrait still resolves without a sex");

-- 2i/2j/2k: the live fork returns SEX_MALE=2 / SEX_FEMALE=3 in field 6. Field 8
-- is PCC in that layout and may look like a 0/1 gender, so field 6 must take priority.
local forkMale = D.FromFields(5, { "Syl", 13, 2, 70, "X", 2, false, 1, nil, nil }, DEPS);
ECS_EQ(forkMale.sex, 0, "2i: SEX_MALE 2 normalizes to male even if PCC is 1");
ECS_CHECK(string.find(forkMale.portrait, "Male", 1, true) ~= nil,
    "2i2: fork male enum selects the male portrait");
local forkFemale = D.FromFields(6, { "Syl", 13, 2, 70, "X", 3, false, 0, nil, nil }, DEPS);
ECS_EQ(forkFemale.sex, 1, "2j: SEX_FEMALE 3 normalizes to female even if PCC is 0");
ECS_CHECK(string.find(forkFemale.portrait, "Female", 1, true) ~= nil,
    "2k: fork female enum selects the female portrait");

-- ------------------------------------------------- 3. degradation
ECS_EQ(D.FromFields(1, { nil, 1, 1, 10, "X" }, DEPS), nil, "3a: no name -> no record");
ECS_EQ(D.FromFields(1, { "   ", 1, 1, 10, "X" }, DEPS), nil, "3b: blank name -> no record");
ECS_EQ(D.FromFields(1, {}, DEPS), nil, "3c: empty tuple -> no record");
ECS_EQ(D.FromFields(1, nil, DEPS), nil, "3d: nil tuple -> no record");

local badLevel = D.FromFields(1, { "Low", 1, 1, 0, "X" }, DEPS);
ECS_EQ(badLevel.level, nil, "3e: level 0 rejected");
local hugeLevel = D.FromFields(1, { "High", 1, 1, 999, "X" }, DEPS);
ECS_EQ(hugeLevel.level, nil, "3f: absurd level rejected");
local nan = D.FromFields(1, { "Nan", 1, 1, 0 / 0, "X" }, DEPS);
ECS_EQ(nan.level, nil, "3g: NaN level rejected");

local noZone = D.FromFields(1, { "NoZone", 1, 1, 10, nil }, DEPS);
ECS_EQ(noZone.zone, C.FALLBACK_ZONE, "3h: nil zone becomes the fallback, not nil");

-- 3i: a string level (some clients return numbers as strings) is rejected, not coerced
local strLevel = D.FromFields(1, { "Str", 1, 1, "42", "X" }, DEPS);
ECS_EQ(strLevel.level, nil, "3i: string level is not silently coerced");

-- ------------------------------------------------- 4. unknown race stays renderable
local unknown = D.FromFields(9, { "Weird", 44, 2, 10, "Nowhere", 0 }, { realm = "Esteria" });
ECS_CHECK(unknown ~= nil, "4a: unknown race still produces a record");
ECS_EQ(unknown.raceKnown, false, "4b: flagged unknown");
ECS_EQ(unknown.raceName, C.FALLBACK_RACE_NAME, "4c: neutral race name");
ECS_CHECK(unknown.portrait == nil, "4d: no portrait for an unknown race (safe nil)");
ECS_CHECK(unknown.factionAccent ~= nil, "4e: a neutral faction accent is still available");

-- ------------------------------------------------- 5. stable key
ECS_EQ(D.StableKey("Esteria", "Zach"), "esteria:zach", "5a: canonical key");
ECS_EQ(D.StableKey("ESTERIA", "zach"), "esteria:zach", "5b: realm case-insensitive");
ECS_EQ(D.StableKey(nil, "Zach"), ":zach", "5c: missing realm still yields a key");
ECS_EQ(D.StableKey("Esteria", nil), nil, "5d: missing name yields no key");

-- ------------------------------------------------- 6. BuildList with injected deps
local function MakeDeps(count, rows, models)
    return {
        numCharacters  = function() return count; end,
        characterInfo  = function(i) return unpack(rows[i] or {}); end,
        backgroundModel= function(i) return (models or {})[i]; end,
        realmName      = function() return "Esteria"; end,
        freebornHashes = function() return nil; end,
        revision       = 1,
    };
end

local rows = {
    { "Alpha", 1, 1, 10, "Stormwind", 0 },
    { "Beta",  4, 8, 20, "Dalaran",   1 },
    { "Gamma", 13, 2, 30, "Elwynn",   0 },
}
local models = { "HUMAN", "NIGHTELF", "HIGHELF" };

local list, skipped = D.BuildList(MakeDeps(3, rows, models));
ECS_EQ(#list, 3, "6a: all three rows built");
ECS_EQ(skipped, 0, "6b: nothing skipped");
ECS_EQ(list[1].stableKey, "esteria:alpha", "6c: first record key");
ECS_EQ(list[3].raceName, "High Elf", "6d: model string drives race");
ECS_EQ(ECS.Order.VisibleCount(), 3, "6e: BuildList hands the list to the mapping layer");

-- 6f: a row that throws is skipped, and the rest survive
local throwing = MakeDeps(3, rows, models);
throwing.characterInfo = function(i)
    if ( i == 2 ) then error("client exploded"); end
    return unpack(rows[i]);
end;
local list2, skipped2 = D.BuildList(throwing);
ECS_EQ(#list2, 2, "6f: a throwing row is skipped, others survive");
ECS_EQ(skipped2, 1, "6g: skip counted");

-- 6h: an absurd reported count is clamped rather than trusted
local huge = MakeDeps(100000, rows, models);
local list3 = D.BuildList(huge);
ECS_EQ(#list3, 0, "6h: absurd numCharacters is clamped to zero");

-- 6i: a zero/garbage count yields an empty, safe list
local zero = MakeDeps(0, rows, models);
local list4 = D.BuildList(zero);
ECS_EQ(#list4, 0, "6i: zero characters is safe");
ECS_EQ(ECS.Order.VisibleCount(), 0, "6j: empty roster maps to zero visible");

-- 6k: missing dependency functions do not raise
local bare = { numCharacters = function() return 2; end };
local list5, skipped5 = D.BuildList(bare);
ECS_EQ(#list5, 0, "6k: missing characterInfo yields an empty list, not an error");
ECS_EQ(skipped5, 2, "6l: both rows counted as skipped");

-- ------------------------------------------------- 7. notes attachment
local noteList = {
    { stableKey = "esteria:alpha" },
    { stableKey = "esteria:beta" },
    { stableKey = nil },
}
D.ApplyNotes(noteList, { ["esteria:beta"] = "Bank alt" });
ECS_EQ(noteList[1].note, nil, "7a: character without a note stays nil");
ECS_EQ(noteList[2].note, "Bank alt", "7b: note attached by stable key");
ECS_CHECK(noteList[3] ~= nil and noteList[3].note == nil, "7c: keyless record is safe");
D.ApplyNotes(nil, {});
ECS_CHECK(true, "7d: nil list does not raise");
