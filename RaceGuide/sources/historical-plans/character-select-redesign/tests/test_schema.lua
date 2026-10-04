--[==[ test_schema.lua ------------------------------------------------------------
    Proves the race / class / faction resolution is data-driven and CANNOT throw
    on an unknown id (spec 14, 15, 27, 33).

    Background: RACE_DATA in CharacterInfo.lua is a 1..19 ORDINAL table, while the
    real race id space goes to 44. Conflating them is the single most likely way
    to make a custom race render wrong, so these tests pin the separation.
]==]

local S = ECS.Schema;
local C = ECS.Const;

-- ---------------------------------------------------------------- model keys
-- A background model string is the authoritative per-character race signal.
local function RaceFrom(model, label, expectedName, expectedFaction)
    local race = S.GetRaceByModel(model);
    if ( not race ) then
        ECS_CHECK(false, label .. ": expected a match for " .. tostring(model));
        return;
    end
    ECS_EQ(race.name, expectedName, label .. ": name");
    ECS_EQ(race.faction, expectedFaction, label .. ": faction");
end

RaceFrom("Interface\\Glues\\CharacterSelect\\HIGHELF\\HIGHELF.mdx", "1a", "High Elf", 1);
RaceFrom("HIGHELF", "1b", "High Elf", 1);
RaceFrom("high_elf", "1c", "High Elf", 1);
RaceFrom("Interface\\Glues\\Models\\DARKFALLEN\\Darkfallen.m2", "1d", "Darkfallen", 1);
RaceFrom("NIGHTELF", "1e", "Night Elf", 1);
RaceFrom("SETHRAK", "1f", "Sethrak", 2);
RaceFrom("VULPERA", "1g", "Vulpera", 2);
RaceFrom("HUMAN.mdx", "1h", "Human", 1);
RaceFrom("ORC", "1i", "Orc", 2);

-- order matters: DARKFALLEN must not be swallowed by a generic token
RaceFrom("DARKFALLENHORDE", "1j", "Darkfallen", 1);
RaceFrom("ILLIDARI_ALLIANCE", "1j2", "Illidari", 1);
RaceFrom("ILLIDARI_HORDE", "1j3", "Illidari", 2);
local illidariAlliance = S.GetRaceByModel("ILLIDARI_ALLIANCE");
local illidariHorde = S.GetRaceByModel("ILLIDARI_HORDE");
ECS_EQ(illidariAlliance.artKey, "DemonHunterAlliance", "1j4: Alliance Illidari uses its own art key");
ECS_EQ(illidariHorde.artKey, "DemonHunterHorde", "1j5: Horde Illidari uses its own art key");
ECS_CHECK(string.find(S.GetPortrait(illidariAlliance.artKey, 0), "DemonHunterAllianceMale", 1, true) ~= nil,
    "1j6: Alliance Illidari resolves to its generated portrait");
ECS_CHECK(string.find(S.GetPortrait(illidariHorde.artKey, 1), "DemonHunterHordeFemale", 1, true) ~= nil,
    "1j7: Horde Illidari resolves to its generated portrait");
local illidariHordeID = S.GetRace(30, "ILLIDARI");
local illidariAllianceID = S.GetRace(31, "ILLIDARI");
ECS_EQ(illidariHordeID.artKey, "DemonHunterHorde", "1j8: ChrRaces ID 30 overrides a generic model token");
ECS_EQ(illidariAllianceID.artKey, "DemonHunterAlliance", "1j9: ChrRaces ID 31 overrides a generic model token");
ECS_EQ(illidariHordeID.faction, 2, "1j10: ChrRaces ID 30 keeps Horde faction");
ECS_EQ(illidariAllianceID.faction, 1, "1j11: ChrRaces ID 31 keeps Alliance faction");

-- unknown / junk never matches, and never raises
ECS_EQ(S.GetRaceByModel("SOMETHING_WEIRD"), nil, "1k: unknown model returns nil");
ECS_EQ(S.GetRaceByModel(nil), nil, "1l: nil model returns nil");
ECS_EQ(S.GetRaceByModel(42), nil, "1m: non-string model returns nil");

-- ---------------------------------------------------------------- normalisation
ECS_EQ(S.NormaliseModelKey("Interface\\Glues\\A\\B.mdx"), "INTERFACEGLUESAB",
    "2a: path separators and extension stripped");
ECS_EQ(S.NormaliseModelKey("night_elf"), "NIGHTELF", "2b: underscores stripped");
ECS_EQ(S.NormaliseModelKey(nil), nil, "2c: nil is safe");

-- ---------------------------------------------------------------- GetRace
-- Override by REAL race id wins over everything.
S.RaceOverride[999] = { name = "Testling", faction = 3, artKey = "Testling" };
local over = S.GetRace(999, "HUMAN");
ECS_EQ(over.name, "Testling", "3a: explicit override wins over the model string");
ECS_EQ(over.faction, 3, "3b: override faction preserved");
ECS_EQ(over.source, "override", "3c: source recorded");

-- Model string resolves when there is no override (a real id like 13 = HighElf)
local byModel = S.GetRace(13, "HIGHELF");
ECS_EQ(byModel.name, "High Elf", "3d: real id 13 resolves via the model string");
ECS_EQ(byModel.source, "model", "3e: source is 'model'");

-- Unknown real id with no model -> neutral, still renderable, never nil
local unknown = S.GetRace(44, nil);
ECS_CHECK(unknown ~= nil, "3f: unknown race still returns a record");
ECS_EQ(unknown.known, false, "3g: flagged as unknown");
ECS_EQ(unknown.name, C.FALLBACK_RACE_NAME, "3h: uses the fallback name");
ECS_EQ(unknown.faction, 0, "3i: neutral faction");
ECS_CHECK(S.GetFaction(unknown.faction) ~= nil, "3j: neutral faction style exists");

-- nil / wrong-typed id must not raise
ECS_CHECK(S.GetRace(nil, nil) ~= nil, "3k: nil race id is safe");
ECS_CHECK(S.GetRace("bogus", nil) ~= nil, "3l: string race id is safe");

-- A REAL custom race id (44 = Darkfallen) with its model must resolve properly,
-- which the ordinal table could never do.
local custom = S.GetRace(44, "DARKFALLEN");
ECS_EQ(custom.name, "Darkfallen", "3m: real custom race id 44 resolves by model");
ECS_EQ(custom.source, "model", "3n: not via the ordinal table");

-- ---------------------------------------------------------------- ordinal fallback
-- Only stock ids 1..11 may use RACE_DATA numerically, and only when the model
-- API gave us nothing. Inject a fake ordinal table to pin that behaviour.
_G.RACE_DATA = {
    [1] = { "HUMAN", 1 },
    [13] = { "HIGHELF", 1 },     -- ordinal 13 does NOT mean real race 13
};
local stock = S.GetRace(1, nil);
ECS_EQ(stock.name, "HUMAN", "4a: stock id 1 falls back to the ordinal table");
ECS_EQ(stock.source, "ordinal-fallback", "4b: marked low-confidence");

local notStock = S.GetRace(13, nil);
ECS_EQ(notStock.known, false,
    "4c: HAZARD - real id 13 must NOT be read from ordinal slot 13");
_G.RACE_DATA = nil;

-- ---------------------------------------------------------------- factions
ECS_EQ(S.GetFaction(1).name, "Alliance", "5a: alliance");
ECS_EQ(S.GetFaction(2).name, "Horde", "5b: horde");
ECS_EQ(S.GetFaction(3).name, "Freeborn", "5c: freeborn is a first-class faction");
ECS_EQ(S.GetFaction(77).name, C.NEUTRAL_FACTION, "5d: unknown faction id is neutral");
ECS_EQ(S.GetFaction(nil).name, C.NEUTRAL_FACTION, "5e: nil faction id is neutral");
ECS_CHECK(S.GetFaction(3).emblem ~= nil, "5f: freeborn has an emblem");
ECS_CHECK(S.GetFaction(1).accent ~= nil, "5g: every faction has an accent");

-- ---------------------------------------------------------------- classes
local cls = S.GetClass(2, "Paladin");
ECS_EQ(cls.name, "Paladin", "6a: class name");
ECS_CHECK(cls.colour ~= nil, "6b: class colour present");
ECS_EQ(cls.known, true, "6c: known class flagged");

local noClass = S.GetClass(nil, nil);
ECS_CHECK(noClass ~= nil, "6d: nil class is safe");
ECS_EQ(C.FALLBACK_CLASS_NAME, "Hero", "6e0: requested fallback label is Hero");
ECS_EQ(noClass.name, "Hero", "6e: fallback class name");
ECS_EQ(noClass.known, false, "6f: unknown class flagged");

-- colour escape parsing (CLASS_COLORS stores "|cffRRGGBB")
local parsed = S.ParseColourEscape("|cffFF8000");
ECS_CHECK(parsed ~= nil, "6g: colour escape parses");
ECS_CHECK(math.abs(parsed[1] - 1.0) < 0.01, "6h: red channel");
ECS_CHECK(math.abs(parsed[2] - 0.5) < 0.02, "6i: green channel");
ECS_EQ(S.ParseColourEscape("nonsense"), nil, "6j: junk colour escape returns nil");
ECS_EQ(S.ParseColourEscape(nil), nil, "6k: nil colour escape returns nil");

-- ---------------------------------------------------------------- portraits
local male   = S.GetPortrait("HighElf", 0);
local female = S.GetPortrait("HighElf", 1);
ECS_CHECK(male ~= nil and string.find(male, "HighElfMale", 1, true) ~= nil,
    "7a: male portrait path");
ECS_CHECK(female ~= nil and string.find(female, "HighElfFemale", 1, true) ~= nil,
    "7b: female portrait path");
ECS_CHECK(S.GetPortrait("HighElf", nil) ~= nil, "7c: unknown sex falls back to male");
ECS_CHECK(S.GetPortrait("HighElf", 9) ~= nil, "7d: out-of-range sex falls back to male");
ECS_EQ(S.GetPortrait(nil, 0), nil, "7e: unknown race yields no portrait, not an error");
ECS_EQ(S.GetPortrait("", 0), nil, "7f: empty key yields no portrait");

-- 7g/7h: the ART KEY is the client's portrait FILE name, which is not always the
-- model token. Zandalari trolls ship `UI-CharacterCreate-Zandalari<sex>.blp` - the
-- create screen maps ZANDALARITROLL -> ...-ZandalariMale - so an artKey of
-- "ZandalariTroll" asked for a file that does not exist and the row silently
-- rendered no portrait at all. tools/check_artkeys.py found it by cross-checking
-- every key against the create screen's mapping and the plates in the client.
local zandalari = S.GetRaceByModel("Character\\ZandalariTroll\\ZandalariTroll.mdx");
ECS_CHECK(zandalari ~= nil, "7g: the Zandalari model resolves");
ECS_EQ(zandalari.artKey, "Zandalari", "7h: ... to the art key the client actually ships");
ECS_CHECK(string.find(S.GetPortrait(zandalari.artKey, 0), "ZandalariMale", 1, true) ~= nil,
    "7i: and its portrait path names a real plate");

-- 7j/7k: ECS ships its own masked copies (generated from the unmasked source art),
-- so the roster asks for those; the create screen's plate is the fallback for any
-- art key ECS has no copy of, which is what an incomplete install or a brand new
-- race gets.
local namedPortrait = S.GetPortrait("HighElf", 0);
ECS_CHECK(string.find(namedPortrait, "ECS-Portrait-HighElfMale", 1, true) ~= nil,
    "7j: a listed art key uses the ECS masked copy");
ECS_CHECK(string.find(namedPortrait, "Glues\\CharacterSelect", 1, true) ~= nil,
    "7k: ... from the CharacterSelect namespace");
local unlisted = S.GetPortrait("SomeNewRace", 0);
ECS_CHECK(string.find(unlisted, "UI-CharacterCreate-SomeNewRaceMale", 1, true) ~= nil,
    "7l: an unlisted art key falls back to the create screen's plate");
ECS_CHECK(string.find(unlisted, "Glues\\CharacterCreate", 1, true) ~= nil,
    "7m: ... from the CharacterCreate namespace");

-- ---------------------------------------------------------------- freeborn
-- With the Freeborn globals absent, detection must simply be false, never error.
ECS_CHECK(S.IsFreeborn("Zach") == false, "8a: no Freeborn globals -> not freeborn");
ECS_EQ(S.ResolveFactionID(1, "Zach"), 1, "8b: faction passes through unchanged");
ECS_EQ(S.ResolveFactionID(nil, "Zach"), 0, "8c: nil race faction becomes neutral");

-- With the globals present, a recorded name must flip the faction to Freeborn.
-- The stub must be name-dependent, otherwise every name hashes identically and
-- the negative case cannot fail.
_G.CharacterFreeborn_RecordBase = 1000000000;
local function RecordFreebornName(name)
    if ( name == "Zach" ) then
        return 1000000000 + 12345;
    end
    return 1000000000 + 99999;
end
_G.CharacterFreeborn_RecordFor = RecordFreebornName;
local hashes = { ["12345"] = true };
ECS_CHECK(S.IsFreeborn("Zach", hashes) == true, "8d: recorded name is Freeborn");
ECS_CHECK(S.IsFreeborn("Someone", hashes) == false, "8e: unrecorded name is not");
ECS_EQ(S.ResolveFactionID(1, "Zach", hashes), 3, "8f: Freeborn overrides race faction");
ECS_EQ(S.ResolveFactionID(1, "Someone", hashes), 1, "8g: others keep race faction");
_G.CharacterFreeborn_RecordFor = function() error("boom"); end;
ECS_CHECK(S.IsFreeborn("Zach", hashes) == false, "8h: a throwing RecordFor is swallowed");

-- ECS stores shards in these same persistent string cvars, preserving the previous
-- Freeborn marker behind one or more length-prefixed ECS wrappers.
local freebornCvarValues = {};
local previousGetCVar = _G.GetCVar;
local previousBadgeHashes = _G.CharacterFreeborn_BadgeHashes;
local previousBadgeCvars = _G.CharacterFreeborn_BadgeCVars;
local previousBadgeMarker = _G.CharacterFreeborn_BadgeMarker;
_G.GetCVar = function(name) return freebornCvarValues[name]; end;
_G.CharacterFreeborn_BadgeHashes = function() return {}; end;
_G.CharacterFreeborn_BadgeCVars = { "voiceInput", "voiceOutput" };
_G.CharacterFreeborn_BadgeMarker = "fb:";
local badgeRecord = "fb:12345,777|legacy-setting";
freebornCvarValues.voiceInput = ECS.Persistence.WrapValue("1/1;ecs", badgeRecord);
freebornCvarValues.voiceInput = ECS.Persistence.WrapValue("1/1;nested", freebornCvarValues.voiceInput);
_G.CharacterFreeborn_RecordFor = RecordFreebornName;
local recoveredHashes = S.FreebornHashes();
ECS_CHECK(recoveredHashes and recoveredHashes["12345"] and recoveredHashes["777"],
    "8i: hashes survive nested ECS cvar wrappers");
ECS_EQ(S.ResolveFactionID(1, "Zach", recoveredHashes), 3,
    "8j: wrapped Freeborn record overrides the race faction");
ECS_EQ(S.ResolveFactionID(2, "Someone", recoveredHashes), 2,
    "8k: unrelated characters keep their race faction");
local recoveredCharacter = ECS.Data.FromFields(9,
    { "Zach", 1, 2, 80, "Stormwind", 0 },
    { realm = "Esteria", model = "HUMAN", freebornHashes = recoveredHashes });
ECS_EQ(recoveredCharacter.factionID, 3, "8l: normalized Freeborn character keeps TeamID 3");
ECS_EQ(recoveredCharacter.factionEmblem, C.TEX.freebornBadge,
    "8m: normalized Freeborn character resolves the Freeborn logo");
_G.GetCVar = previousGetCVar;
_G.CharacterFreeborn_BadgeHashes = previousBadgeHashes;
_G.CharacterFreeborn_BadgeCVars = previousBadgeCvars;
_G.CharacterFreeborn_BadgeMarker = previousBadgeMarker;
_G.CharacterFreeborn_RecordFor = nil;
_G.CharacterFreeborn_RecordBase = nil;
