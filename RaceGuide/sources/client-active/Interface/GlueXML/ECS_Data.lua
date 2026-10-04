--[[ ECS_Data.lua ---------------------------------------------------------------
    Esteria Character Select - normalized character data (spec 23, 33).

    Turns the client's positional GetCharacterInfo tuple into a stable record, so
    no other module ever touches a positional return again.

    THE FIELD-ORDER PROBLEM
    -----------------------
    The stock WotLK API returns:
        name, race, class, level, zone, raceFilename, classFilename, gender, ghost, PCC
    The Esteria fork's CharacterSelect.lua reads:
        name, race, class, level, zone, sex,          ghost,         PCC,  PRC,  PFC

    Field 6 is the conflict: the stock API returns a race filename, while the fork
    returns a sex enum (SEX_MALE=2 / SEX_FEMALE=3). Normalize that enum when present;
    otherwise use the stock API's field-8 gender (0=male / 1=female). This prevents
    field 8's fork-only PCC value from being mistaken for gender and supports either
    signature without mislabeling race, class, level or zone.

    Checked against the client's own glue since (stock-locale/CharacterSelect.lua):
        local name, race, class, level, zone, raceFilename, classFilename,
              gender, ghost, PCC = GetCharacterInfo(i);
        if ( gender == 0 ) then gender = "MALE" else gender = "FEMALE" ...
    which confirms that stock field 6 is a filename and field 8 is a 0/1 gender. The
    fork's field-6 sex is instead the SEX_MALE/SEX_FEMALE enum; both are normalized to
    ECS's 0=male / 1=female representation before portrait selection. `test_data`
    covers both signatures, including the enum values that distinguish female rows.

    Pure Lua, dependency-injected, so it is unit-testable with no client.
    Lua 5.1 only.
------------------------------------------------------------------------------ ]]

ECS = ECS or {};
ECS.Data = ECS.Data or {};

local D = ECS.Data;
local C = ECS.Const;
local S = ECS.Schema;

-- ---------------------------------------------------------------- coercion
-- Every helper returns nil rather than raising, so a malformed row degrades.

function D.AsName(value)
    if ( type(value) ~= "string" ) then
        return nil;
    end
    local name = string.gsub(value, "^%s+", "");
    name = string.gsub(name, "%s+$", "");
    if ( name == "" ) then
        return nil;
    end
    return name;
end

function D.AsLevel(value)
    if ( type(value) ~= "number" ) then
        return nil;
    end
    if ( value ~= value ) then          -- NaN guard: NaN ~= NaN
        return nil;
    end
    value = math.floor(value);
    if ( value < 1 or value > 255 ) then
        return nil;
    end
    return value;
end

function D.AsZone(value)
    local zone = D.AsName(value);
    if ( not zone ) then
        return C.FALLBACK_ZONE;
    end
    return zone;
end

-- Normalize the stock 0/1 gender and the fork's SEX_MALE=2 / SEX_FEMALE=3 enum to
-- 0=male / 1=female. Race filenames, booleans and unrelated flags are rejected so
-- the caller can try the next candidate field.
function D.AsSex(value)
    if ( type(value) ~= "number" ) then
        return nil;
    end
    if ( value == 0 or value == 2 ) then return 0; end
    if ( value == 1 or value == 3 ) then return 1; end
    return nil;
end

-- Accepts 0/1 numbers, booleans, or the strings "true"/"nil" that some glue
-- returns; anything else is nil.
function D.AsFlag(value)
    if ( value == nil or value == false ) then
        return false;
    end
    if ( value == true ) then
        return true;
    end
    if ( type(value) == "number" ) then
        if ( value == 0 ) then return false; end
        if ( value == 1 ) then return true; end
        return nil;
    end
    if ( type(value) == "string" ) then
        if ( value == "true" or value == "1" ) then return true; end
        if ( value == "false" or value == "0" or value == "" ) then return false; end
    end
    return nil;
end

-- spec 11: stable identity for order/notes. No GUID is exposed to glue, so the
-- key is realm + name, both lower-cased because both are case-insensitive. This
-- is the canonical form ECS_Order and ECS_Persistence must agree on.
function D.StableKey(realm, name)
    local realmPart = D.AsName(realm) or "";
    local namePart  = D.AsName(name);
    if ( not namePart ) then
        return nil;
    end
    return string.lower(realmPart) .. ":" .. string.lower(namePart);
end

-- ---------------------------------------------------------------- one record
-- fields: the raw positional tuple, as a table (1-based).
-- deps:   { realm = "Esteria", model = "HIGHELF", freebornHashes = {...} }
function D.FromFields(realIndex, fields, deps)
    deps = deps or {};

    local name = D.AsName(fields and fields[1]);
    if ( not name ) then
        return nil;   -- a character with no name is not renderable
    end

    -- fields 2-5 mean the same thing in both layouts -> safe to trust
    local raceID  = fields[2];
    local raceHint = nil;
    local classID = fields[3];
    if ( type(raceID) == "string" ) then
        local numericRaceID = tonumber(raceID);
        if ( numericRaceID ) then
            raceID = numericRaceID;
        else
            raceHint = D.AsName(raceID);
            raceID = nil;
        end
    elseif ( type(raceID) ~= "number" ) then
        raceID = nil;
    end
    if ( type(classID) ~= "number" ) then classID = nil; end

    local level = D.AsLevel(fields[4]);
    local zone  = D.AsZone(fields[5]);

    -- Fork field 6 is its SEX_MALE/SEX_FEMALE enum; stock field 6 is a filename.
    -- Prefer field 6 when it normalizes, and otherwise read stock's field-8 gender.
    local sex = D.AsSex(fields[6]) or D.AsSex(fields[8]);
    -- Stock GetCharacterInfo stores raceFilename in field 6; the fork layout
    -- stores sex there. Keep the file token for race/art resolution as well.
    local raceFileHint = (type(fields[6]) == "string") and D.AsName(fields[6]) or nil;

    local ghost = D.AsFlag(fields[7]) or false;

    local model = deps.model;

    local race  = S.GetRace(raceID, model, raceHint, raceFileHint);
    local klass = S.GetClass(classID, nil);

    local hashes   = deps.freebornHashes;
    local factionID = S.ResolveFactionID(race.faction, name, hashes);
    local faction   = S.GetFaction(factionID);

    return {
        realIndex   = realIndex,
        stableKey   = D.StableKey(deps.realm, name),

        name        = name,
        level       = level,
        zone        = zone,

        raceID      = raceID,
        raceName    = race.name,
        raceArtKey  = race.artKey,
        raceKnown   = race.known,
        raceSource  = race.source,

        classID     = classID,
        className   = klass.name,
        classColour = klass.colour,
        classKnown  = klass.known,

        sex         = sex,
        ghost       = ghost,

        factionID   = factionID,
        factionName = faction.name,
        factionAccent = faction.accent,
        factionEmblem = faction.emblem,

        modelKey    = model,
        portrait    = S.GetPortrait(race.artKey, sex),

        note        = nil,
        customOrder = nil,
        searchBlob  = nil,   -- lazily filled by ECS_Order
        revision    = deps.revision or 1,
    };
end

-- ---------------------------------------------------------------- the roster
-- Iterates the server list and returns a dense array of CharacterData.
-- A row that cannot be read is skipped, never fatal (spec 33).
--
-- deps:
--   numCharacters()      -> number        (GetNumCharacters)
--   characterInfo(i)     -> 10 values     (GetCharacterInfo)
--   backgroundModel(i)   -> string|nil    (GetSelectBackgroundModel)
--   realmName()          -> string
--   freebornHashes()     -> table|nil
--   revision             -> number
--
-- Returns list, skippedCount
function D.BuildList(deps)
    deps = deps or {};

    local list = {};
    local skipped = 0;

    local total = 0;
    if ( type(deps.numCharacters) == "function" ) then
        local ok, value = pcall(deps.numCharacters);
        if ( ok and type(value) == "number" and value > 0 ) then
            total = math.floor(value);
        end
    end

    -- never trust the reported count blindly: clamp to something sane so a
    -- misbehaving client cannot make us build thousands of phantom rows.
    if ( not (total > 0) or total >= 2000 ) then
        total = 0;
    end

    local realm = nil;
    if ( type(deps.realmName) == "function" ) then
        local ok, value = pcall(deps.realmName);
        if ( ok ) then realm = value; end
    end

    local hashes = nil;
    if ( type(deps.freebornHashes) == "function" ) then
        local ok, value = pcall(deps.freebornHashes);
        if ( ok ) then hashes = value; end
    end

    for index = 1, total do
        local ok, fields = pcall(function()
            if ( type(deps.characterInfo) ~= "function" ) then
                return nil;
            end
            return { deps.characterInfo(index) };
        end)

        if ( not ok or type(fields) ~= "table" or #fields == 0 ) then
            skipped = skipped + 1;
        else
            local model = nil;
            if ( type(deps.backgroundModel) == "function" ) then
                local mok, value = pcall(deps.backgroundModel, index);
                if ( mok ) then model = value; end
            end

            local record = D.FromFields(index, fields, {
                realm          = realm,
                model          = model,
                freebornHashes = hashes,
                revision       = deps.revision or 1,
            });

            if ( record ) then
                list[#list + 1] = record;
            else
                skipped = skipped + 1;
            end
        end
    end

    -- Hand the dense list to the mapping layer. Real indices are re-derived from
    -- position there, which is correct because the server list is dense and
    -- ordered; a skipped row shifts nothing because we index by position.
    if ( ECS.Order ) then
        ECS.Order.SetCharacters(list);
    end

    return list, skipped;
end

-- spec 12: attach notes from the persistence layer onto the records.
function D.ApplyNotes(list, notes)
    if ( type(list) ~= "table" ) then
        return;
    end
    notes = notes or {};
    for index = 1, #list do
        local record = list[index];
        if ( record and record.stableKey ) then
            record.note = notes[record.stableKey];
        end
    end
end
