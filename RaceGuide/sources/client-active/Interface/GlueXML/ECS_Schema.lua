--[[ ECS_Schema.lua -------------------------------------------------------------
    Esteria Character Select - race / class / faction presentation (spec 14, 15, 27, 33).

    Design rule: DERIVE, NEVER HARDCODE.

    The client already maintains authoritative tables for its own custom races
    (RACE_DATA / Races_Informations in CharacterInfo.lua). We read those and add a
    presentation layer on top. An ID we have never seen must still render.

    There is deliberately no `if alliance then ... else horde` anywhere: factions
    are table lookups with a neutral fallback, so a third (Freeborn) or a future
    team id works without touching this file's logic.

    Lua 5.1 only.
------------------------------------------------------------------------------ ]]

ECS = ECS or {};
ECS.Schema = ECS.Schema or {};

local S = ECS.Schema;
local C = ECS.Const;

-- ---------------------------------------------------------------- factions
-- spec 14: keyed by faction id; every field optional. `accent` is used as an
-- ACCENT only (spec 27), never as a full row fill.
S.FactionStyle = {
    [0] = { name = "Neutral",  emblem = nil,                      accent = { 0.62, 0.62, 0.62 } },
    [1] = { name = "Alliance", emblem = C.TEX.allianceBadge,      accent = { 0.25, 0.50, 0.90 } },
    [2] = { name = "Horde",    emblem = C.TEX.hordeBadge,         accent = { 0.80, 0.22, 0.22 } },
    -- spec 14: Freeborn is a real third faction in Esteria. It is resolved via
    -- the client's existing name-hash badge mechanism (see CharacterCreate.lua),
    -- NOT via a TeamID, because the glue character list carries no team field.
    [3] = { name = "Freeborn", emblem = C.TEX.freebornBadge,      accent = { 0.62, 0.45, 0.85 } },
};

-- Neutral entry returned for any unknown id (spec 33).
S.NeutralFaction = { name = C.NEUTRAL_FACTION, emblem = nil, accent = { 0.62, 0.62, 0.62 } };

function S.GetFaction(factionID)
    local style = S.FactionStyle[factionID];
    if ( style ) then
        return style;
    end
    return S.NeutralFaction;
end

-- ---------------------------------------------------------------- races
--
-- ============================ CRITICAL HAZARD ==============================
-- The client's real race id space and the glue ORDINAL space are DIFFERENT
-- THINGS and must never be conflated.
--
--   * ChrRaces.dbc carries real race ids up to 44 (see
--     src/server/shared/SharedDefines.h:70-100 and
--     modules/mod-custom-server/data/races/race_registry.json).
--   * CharacterInfo.lua's RACE_DATA / ALLIANCE_RACES / HORDE_RACES are a
--     parallel 1..19 ORDINAL table, and CharacterCreate.lua:986 deliberately
--     passes `raceID = index` (an enumeration ordinal) into GetFactionForRace.
--     That is intentional, not a bug. DO NOT "fix" it to real ids.
--
-- Consequence: RACE_DATA[raceID] is only coincidentally correct for the stock
-- races 1..11, where ordinal happens to equal real id. For every custom race it
-- is WRONG -- which is exactly why the existing GetFactionForRaceName defaults
-- unknown races to "Horde".
--
-- Therefore this layer does NOT key off RACE_DATA by number. The authoritative
-- per-character race signal at runtime is the background MODEL FILE STRING from
-- GetSelectBackgroundModel(index) -- the same signal the existing custom faction
-- override at CharacterSelect.lua:586-594 already trusts (it string-matches
-- "HORDE" and "DARKFALLEN" out of it).
-- ==========================================================================
S.RaceOverride = {
    [54] = {name="Naga", faction=2, artKey="NagaHorde"},
    [55] = {name="Tuskarr", faction=1, artKey="Tuskarr"},
    [56] = {name="Vrykul", faction=1, artKey="Vrykul"},
    [57] = {name="Vrykul", faction=2, artKey="VrykulHorde"},
    [58] = {name="Forgotten", faction=1, artKey="ThinHuman"},
    [59] = {name="Forgotten", faction=2, artKey="ThinHumanHorde"},
    [50] = { name="Haranir", faction=1, artKey="Haranir" },
    [51] = { name="Haranir", faction=2, artKey="HaranirHorde" },
    [48] = { name="Earthen", faction=1, artKey="Earthen" },
    [49] = { name="Earthen", faction=2, artKey="EarthenHorde" },
    [46] = { name = "Highmountain Tauren", faction = 2, artKey = "HighmountainTauren" },
    [47] = { name = "Mechagnome", faction = 1, artKey = "Mechagnome" },
    [45] = { name = "Mag'har Orc", faction = 2, artKey = "Maghar" },
    [52] = { name = "Skyborn", faction = 1, artKey = "Skyborne" },
    [53] = { name = "Skyborn", faction = 2, artKey = "SkyborneHorde" },
    -- ChrRaces.dbc IDs from the deployed Dev client: 30 = Horde Illidari,
    -- 31 = Alliance Illidari. The client model folder may only say "Illidari",
    -- so race-ID resolution is the authoritative side signal for these plates.
    [30] = { name = "Illidari", faction = 2, artKey = "DemonHunterHorde" },
    [31] = { name = "Illidari", faction = 1, artKey = "DemonHunterAlliance" },
};

-- Model/file-string -> presentation. Matching is on an upper-cased, punctuation
-- -stripped form so "NIGHTELF", "NightElf" and "night_elf" all land together.
-- Order matters: the first key found inside the string wins, so put the more
-- specific names before the generic ones.
S.RaceByModelKey = {
    { "NAGAHORDE", { name = "Naga", faction = 2, artKey = "NagaHorde" } },
    { "TUSKARR", { name = "Tuskarr", faction = 1, artKey = "Tuskarr" } },
    { "VRYKULHORDE", { name = "Vrykul", faction = 2, artKey = "VrykulHorde" } },
    { "VRYKUL", { name = "Vrykul", faction = 1, artKey = "Vrykul" } },
    { "THINHUMANHORDE", { name = "Forgotten", faction = 2, artKey = "ThinHumanHorde" } },
    { "THINHUMAN", { name = "Forgotten", faction = 1, artKey = "ThinHuman" } },
    { "DARKFALLEN", { name = "Darkfallen", faction = 1, artKey = "Darkfallen" } },
    -- The Illidari portrait art is faction-specific and keyed by the create
    -- screen's ILLIDARI_ALLIANCE / ILLIDARI_HORDE model-folder tokens.
    { "ILLIDARIHORDE", { name = "Illidari", faction = 2, artKey = "DemonHunterHorde" } },
    { "ILLIDARIALLIANCE", { name = "Illidari", faction = 1, artKey = "DemonHunterAlliance" } },
    { "DEMONHUNTERHORDE", { name = "Illidari", faction = 2, artKey = "DemonHunterHorde" } },
    { "DEMONHUNTERALLIANCE", { name = "Illidari", faction = 1, artKey = "DemonHunterAlliance" } },
    -- GetCharacterInfo may return only the shared display race name. This
    -- last-resort token keeps it renderable; raceFilename/model tokens and IDs
    -- above preserve the faction-specific portrait when available.
    { "ILLIDARI", { name = "Illidari", faction = 2, artKey = "DemonHunterHorde" } },
    { "HIGHELF",    { name = "High Elf",   faction = 1, artKey = "HighElf" } },
    { "BLOODELF",   { name = "Blood Elf",  faction = 2, artKey = "BloodElf" } },
    { "NIGHTELF",   { name = "Night Elf",  faction = 1, artKey = "NightElf" } },
    { "VOIDELF",    { name = "Void Elf",   faction = 1, artKey = "VoidElf" } },
    { "NIGHTBORNE", { name = "Nightborne", faction = 2, artKey = "Nightborne" } },
    { "LIGHTFORGED",{ name = "Lightforged",faction = 1, artKey = "Lightforged" } },
    { "DARKIRON",   { name = "Dark Iron",  faction = 1, artKey = "DarkIron" } },
    { "KULTIRAN",   { name = "Kul Tiran",  faction = 1, artKey = "KulTiran" } },
    -- artKey is the CLIENT'S portrait file name, which is not always the model
    -- token: Zandalari trolls ship `UI-CharacterCreate-Zandalari<sex>.blp` (the
    -- create screen maps ZANDALARITROLL -> ...-ZandalariMale), so `ZandalariTroll`
    -- here asked for a file that does not exist and the row rendered no portrait.
    -- tools/check_artkeys.py cross-checks every key against the create screen's own
    -- mapping and against the plates actually in the client archives.
    { "ZANDALARI",  { name = "Zandalari",  faction = 2, artKey = "Zandalari" } },
    { "VULPERA",    { name = "Vulpera",    faction = 2, artKey = "Vulpera" } },
    { "SETHRAK",    { name = "Sethrak",    faction = 2, artKey = "Sethrak" } },
    { "DRACTHYR",   { name = "Dracthyr",   faction = 2, artKey = "Dracthyr" } },
    { "EREDAR",     { name = "Eredar",     faction = 2, artKey = "Eredar" } },
    { "WORGEN",     { name = "Worgen",     faction = 1, artKey = "Worgen" } },
    { "GOBLIN",     { name = "Goblin",     faction = 2, artKey = "Goblin" } },
    { "PANDAREN",   { name = "Pandaren",   faction = 1, artKey = "Pandaren" } },
    { "FORSAKEN",   { name = "Forsaken",   faction = 1, artKey = "Forsaken" } },
    { "SCOURGE",    { name = "Undead",     faction = 2, artKey = "Scourge" } },
    { "DRAENEI",    { name = "Draenei",    faction = 1, artKey = "Draenei" } },
    { "TAUREN",     { name = "Tauren",     faction = 2, artKey = "Tauren" } },
    { "GNOME",      { name = "Gnome",      faction = 1, artKey = "Gnome" } },
    { "DWARF",      { name = "Dwarf",      faction = 1, artKey = "Dwarf" } },
    { "TROLL",      { name = "Troll",      faction = 2, artKey = "Troll" } },
    { "ORC",        { name = "Orc",        faction = 2, artKey = "Orc" } },
    { "HUMAN",      { name = "Human",      faction = 1, artKey = "Human" } },
    { "BROKEN",     { name = "Broken",     faction = 2, artKey = "Broken" } },
};

-- Normalise a model path or race key into a comparable token.
function S.NormaliseModelKey(value)
    if ( type(value) ~= "string" ) then
        return nil;
    end
    local key = string.upper(value);
    key = string.gsub(key, "%.%a+$", "");      -- strip a trailing ".mdx"/".m2"
    key = string.gsub(key, "[^%w]", "");       -- strip \ / _ - and spaces
    return key;
end

-- Resolve presentation from a background model string (authoritative path).
function S.GetRaceByModel(model)
    local key = S.NormaliseModelKey(model);
    if ( not key ) then
        return nil;
    end
    for index = 1, #S.RaceByModelKey do
        local token = S.RaceByModelKey[index][1];
        local info  = S.RaceByModelKey[index][2];
        if ( string.find(key, token, 1, true) ) then
            return {
                name    = info.name,
                faction = info.faction,
                artKey  = info.artKey,
                known   = true,
                source  = "model",
            };
        end
    end
    return nil;
end

local function HasFactionQualifiedIllidari(info, token)
    if ( not info or type(token) ~= "string" ) then
        return false;
    end
    local key = S.NormaliseModelKey(token) or "";
    return (info.artKey == "DemonHunterHorde" and string.find(key, "HORDE", 1, true) ~= nil)
        or (info.artKey == "DemonHunterAlliance" and string.find(key, "ALLIANCE", 1, true) ~= nil);
end

-- Neutral race record (spec 15: unknown races stay selectable, spec 33).
function S.NeutralRace(raceID)
    return {
        id      = raceID,
        name    = C.FALLBACK_RACE_NAME,
        faction = 0,
        artKey  = nil,
        known   = false,
        source  = "neutral",
    };
end

-- Resolve a race. `raceID` is the value from GetCharacterInfo; `model` is the
-- optional GetSelectBackgroundModel string for the same character.
--
-- Precedence: explicit override (real id) -> model string -> neutral.
-- RACE_DATA is deliberately NOT consulted numerically (see HAZARD above); it is
-- only used for stock ids 1..11 where ordinal == real id by construction, and
-- that path is marked as low-confidence in the returned record.
function S.GetRace(raceID, model, raceHint, raceFileHint)
    if ( type(raceID) == "number" ) then
        local over = S.RaceOverride[raceID];
        if ( over ) then
            return {
                id = raceID, name = over.name or C.FALLBACK_RACE_NAME,
                faction = over.faction or 0, artKey = over.artKey,
                known = true, source = "override",
            };
        end
    end

    -- The stock tuple's raceFilename (field 6) may retain a faction-specific
    -- model token even when the display name and select-background model are shared.
    local byModel = S.GetRaceByModel(model);
    local byRaceFile = S.GetRaceByModel(raceFileHint);
    local byRaceHint = S.GetRaceByModel(raceHint);
    if ( HasFactionQualifiedIllidari(byModel, model) ) then
        return byModel;
    end
    if ( HasFactionQualifiedIllidari(byRaceFile, raceFileHint) ) then
        return byRaceFile;
    end
    if ( HasFactionQualifiedIllidari(byRaceHint, raceHint) ) then
        return byRaceHint;
    end
    -- Prefer the model getter over an unqualified filename/display-name fallback;
    -- both may contain only "Illidari" while the actual model token carries side.
    byModel = byModel or byRaceFile or byRaceHint;
    if ( byModel ) then
        byModel.id = raceID;
        return byModel;
    end

    -- Low-confidence ordinal fallback, kept ONLY so stock races 1..11 keep a
    -- sensible label on a client where the model API is unavailable.
    if ( type(raceID) == "number" and raceID >= 1 and raceID <= 11 and _G.RACE_DATA ) then
        local entry = _G.RACE_DATA[raceID];
        if ( entry and entry[1] ) then
            local name = entry[1];
            if ( _G[name] ) then name = _G[name]; end
            return {
                id = raceID, name = name, faction = entry[2] or 0,
                artKey = nil, known = true, source = "ordinal-fallback",
            };
        end
    end

    return S.NeutralRace(raceID);
end

-- spec 4: per-race portrait art ships as
--   ECS copy      Interface\Glues\CharacterSelect\ECS-Portrait-<artKey><Male|Female>.blp
--   fallback      Interface\Glues\CharacterCreate\UI-CharacterCreate-<artKey><Male|Female>.blp
-- sex is 0/1/nil; anything unexpected falls back to the male plate.
--
-- Art keys ECS has its own masked copy of, generated by
-- tools/make_ecs_portraits.py from the unmasked source portraits. Derived from that
-- generator's mapping and verified against the files on disk by
-- tools/check_artkeys.py, so the two cannot drift apart silently.
S.PortraitArtKeys = {
    ThinHuman=true, Tuskarr=true, Vrykul=true, VrykulHorde=true, NagaHorde=true, ThinHumanHorde=true,
    Haranir=true, HaranirHorde=true,
    Earthen=true, EarthenHorde=true,
    HighmountainTauren = true,
    Mechagnome = true,
    Maghar = true, Skyborne = true, SkyborneHorde = true,
    BloodElf = true, Broken = true, DarkIron = true, Darkfallen = true,
    DarkfallenHorde = true, DemonHunterAlliance = true, DemonHunterHorde = true,
    Dracthyr = true, Draenei = true, Dwarf = true, Eredar = true, Gnome = true,
    Goblin = true, HighElf = true, Human = true, KulTiran = true, Lightforged = true,
    Nightborne = true, NightElf = true, Orc = true, Pandaren = true, Scourge = true,
    Tauren = true, Troll = true, VoidElf = true, Vulpera = true, Worgen = true,
    Zandalari = true,
};

function S.GetPortrait(artKey, sex)
    if ( type(artKey) ~= "string" or artKey == "" ) then
        return nil;
    end
    local suffix = "Male";
    if ( sex == 1 ) then
        suffix = "Female";
    end
    -- ECS ships its own masked copies, generated from the unmasked 130x130 source
    -- art (tools/make_ecs_portraits.py). They are preferred because ECS controls the
    -- framing: the client's own plates leave ~4.4px of margin, so a face drawn from
    -- them sits noticeably inside the 50px ring drawn over it, while the ECS copies
    -- fill the frame. Anything ECS has no copy of falls back to the create screen's
    -- plate, which is what an incomplete install or a newly added race gets.
    if ( S.PortraitArtKeys[artKey] ) then
        return C.TEX.portraitNs .. artKey .. suffix;
    end
    return C.TEX.create .. "UI-CharacterCreate-" .. artKey .. suffix;
end

-- ---------------------------------------------------------------- classes
-- Neutral class record.
function S.NeutralClass(classID)
    return { id = classID, name = C.FALLBACK_CLASS_NAME, colour = { 1, 1, 1 }, known = false };
end

-- Class colour. Reads the existing CLASS_COLORS table if present; it is keyed by
-- upper-cased class NAME, and stores a colour-escape string ("|cffRRGGBB").
local function ParseColourEscape(escape)
    if ( type(escape) ~= "string" ) then
        return nil;
    end
    local hex = string.match(escape, "|cff(%x%x%x%x%x%x)");
    if ( not hex ) then
        return nil;
    end
    local r = tonumber(string.sub(hex, 1, 2), 16);
    local g = tonumber(string.sub(hex, 3, 4), 16);
    local b = tonumber(string.sub(hex, 5, 6), 16);
    if ( not r or not g or not b ) then
        return nil;
    end
    return { r / 255, g / 255, b / 255 };
end

S.ParseColourEscape = ParseColourEscape;

function S.GetClass(classID, className)
    local name = className;
    if ( not name and _G.GetClassInfo ) then
        local ok, resolved = pcall(_G.GetClassInfo, classID);
        if ( ok and resolved ) then
            name = resolved;
        end
    end
    if ( type(name) ~= "string" or name == "" ) then
        return S.NeutralClass(classID);
    end

    local colour = nil;
    if ( _G.CLASS_COLORS ) then
        colour = ParseColourEscape(_G.CLASS_COLORS[string.upper(name)]);
    end

    return {
        id     = classID,
        name   = name,
        colour = colour or { 1, 1, 1 },
        known  = true,
    };
end

-- ---------------------------------------------------------------- Freeborn
-- Freeborn is a persistent TEAM (TeamID 3), not a race, and the glue character
-- list carries no team field. The client's existing solution is a name-hash
-- record stored in inert string cvars, written by CharacterCreate.lua and applied
-- by CharacterFreeborn_ApplyBadges() -- which WRAPS UpdateCharacterList().
--
-- We must not duplicate or fight that. Instead we REUSE it: if the Freeborn
-- globals exist we ask them, and fall back to the neutral faction otherwise.
-- That keeps one source of truth for Freeborn membership.
local function MergeFreebornHashes(target, source)
    if ( type(source) ~= "table" ) then return end
    for record, present in pairs(source) do
        if ( present ) then target[tostring(record)] = true end
    end
end

local function UnwrapCVarValue(value)
    for depth = 1, 64 do
        if ( type(value) ~= "string" ) then return nil end
        local lengthText, rest = string.match(value, "^ecs%d+:(%d+)|(.*)$");
        if ( not lengthText ) then return value end
        local length = tonumber(lengthText);
        if ( not length or #rest < length ) then return nil end
        value = string.sub(rest, length + 1);
    end
    return nil;
end

-- ECS shares the proven string cvars with the Freeborn badge store. Each ECS shard
-- wraps and preserves its previous cvar value, which means the Freeborn marker may
-- be nested behind one or more `ecsN:<length>|<shard>` headers. The stock helper
-- only recognizes `fb:` at byte 1, so merge its result with the preserved records.
function S.FreebornHashes()
    local hashes = {};
    if ( type(_G.CharacterFreeborn_BadgeHashes) == "function" ) then
        local ok, existing = pcall(_G.CharacterFreeborn_BadgeHashes);
        if ( ok ) then MergeFreebornHashes(hashes, existing) end
    end

    local cvars = _G.CharacterFreeborn_BadgeCVars;
    local marker = _G.CharacterFreeborn_BadgeMarker or "fb:";
    if ( type(cvars) == "table" and type(_G.GetCVar) == "function" ) then
        for index = 1, #cvars do
            local ok, stored = pcall(_G.GetCVar, cvars[index]);
            if ( ok and type(stored) == "string" ) then
                stored = UnwrapCVarValue(stored);
                if ( type(stored) == "string" and string.sub(stored, 1, #marker) == marker ) then
                    local records = string.sub(stored, #marker + 1);
                    records = string.match(records, "^([^|]*)") or records;
                    for record in string.gmatch(records, "%d+") do
                        hashes[record] = true;
                    end
                end
            end
        end
    end

    return next(hashes) and hashes or nil;
end

-- Returns true when this character name is recorded as Freeborn.
-- Deliberately tolerant: any failure returns false, never an error (spec 33).
function S.IsFreeborn(name, hashes)
    if ( type(name) ~= "string" or name == "" ) then
        return false;
    end
    if ( type(_G.CharacterFreeborn_RecordFor) ~= "function"
        or type(_G.CharacterFreeborn_RecordBase) ~= "number" ) then
        return false;
    end

    hashes = hashes or S.FreebornHashes();
    if ( not hashes or not next(hashes) ) then
        return false;
    end

    local ok, record = pcall(_G.CharacterFreeborn_RecordFor, name);
    if ( not ok or type(record) ~= "number" ) then
        return false;
    end
    return hashes[tostring(record - _G.CharacterFreeborn_RecordBase)] == true;
end

-- Faction id for a character. Freeborn wins over the race-derived faction.
function S.ResolveFactionID(raceFaction, name, hashes)
    if ( S.IsFreeborn(name, hashes) ) then
        return 3;   -- ECS.Const / Schema.FactionStyle Freeborn
    end
    if ( type(raceFaction) == "number" and raceFaction > 0 ) then
        return raceFaction;
    end
    return 0;
end
