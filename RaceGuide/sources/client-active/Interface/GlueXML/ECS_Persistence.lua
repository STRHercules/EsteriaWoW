--[[ ECS_Persistence.lua --------------------------------------------------------
    Esteria Character Select - restart-surviving storage (spec 11, 34).

    Glue has no SavedVariables: it runs before addons and cannot write files.
    The ONLY channel that survives a client restart is a STRING cvar the client
    never parses. That was established the hard way by the existing Freeborn
    badge code (CharacterCreate.lua:1858-1930), whose rules this module obeys:

      1. GetCVar/SetCVar RAISE on a name the client does not know. An uncaught
         error here can take the screen down and crash the client, so every
         access is wrapped in pcall.
      2. Only names the engine registers at the login screen are writable.
         Presence in Config.wtf proves nothing, so candidates are PROBED.
      3. Integer cvars get NORMALISED on load, so the store must be a string.
      4. Read-back verification is mandatory - a write may be silently refused.

    Design consequences:
      * the payload is SHARDED across every cvar that passes probing, so capacity
        is however many string cvars the client happens to expose;
      * a store that will not fit degrades (notes dropped, order kept) rather
        than failing;
      * corrupt/foreign/newer stores are IGNORED and the caller falls back to
        server order - a bad store must never block entry (spec 34).

    The backend is injectable, so all of this is unit-testable with no client.
    Lua 5.1 only.
------------------------------------------------------------------------------ ]]

ECS = ECS or {};
ECS.Persistence = ECS.Persistence or {};

local P = ECS.Persistence;
local C = ECS.Const;

P.MARKER = "ecs" .. tostring(C.SCHEMA_VERSION) .. ":";

-- Largest payload we will put in one cvar. Deliberately conservative: the real
-- bound is not discoverable offline, and being wrong the safe way costs only
-- extra shards.
P.MAX_CHUNK = 170;

-- Probe order. Sound_VoiceChatInputDriverName is intentionally NOT here: it is
-- exclusively owned by the Freeborn badge store. Sharing that CVar caused ECS
-- and Freeborn to wrap one another recursively until the fixed-size client CVar
-- buffer consumed the following Config.wtf setting (including accountName).
-- These remaining string-shaped cvars are probed before use because registration
-- differs by client build.
P.CANDIDATE_CVARS = {
    "Sound_VoiceChatOutputDriverName",
    "Sound_OutputDriverName",
    "lastCharacterDeleted",
    "agentUID",
    "portal",
};

-- ---------------------------------------------------------------- encoding
-- Percent-encoding keeps the payload to an alphabet that no cvar parser is
-- likely to mangle, and makes every delimiter safe without a bespoke escaper.
function P.Encode(text)
    if ( type(text) ~= "string" ) then
        return "";
    end
    return (string.gsub(text, "([^%w%-%._~])", function(character)
        return string.format("%%%02X", string.byte(character));
    end));
end

function P.Decode(text)
    if ( type(text) ~= "string" ) then
        return "";
    end
    return (string.gsub(text, "%%(%x%x)", function(hex)
        return string.char(tonumber(hex, 16));
    end));
end

-- ---------------------------------------------------------------- store codec
-- Store:
--   { version, account, realm, order = {key,...}, notes = {key = "text"} }
--
-- Notes are serialised as key*text pairs joined by !. Both key and text are
-- percent-encoded first, and P.Encode never emits literal '*' or '!', so these
-- printable delimiters are unambiguous without putting control bytes in a CVar.
local NOTE_PAIR = ";";
local NOTE_SEP  = ":";

-- ORDER KEYS ARE STORED WITHOUT THEIR REALM PREFIX.
--
-- A stable key is `lower(realm)..":"..lower(name)`, so every entry in a roster
-- repeats the same realm, and P.Encode escapes the ':' to '%3A'. Measured
-- against the real budget that is fatal: 100 characters cost 2219 payload chars
-- = 14 shards, while only a handful of candidate cvars exist. The custom order
-- for a full roster could therefore never be persisted at all.
--
-- The realm is already in the record's `r=` field, so writing it once instead of
-- once per character is lossless. It takes the same 100 characters down to ~850
-- chars (~5 shards), inside the budget. Names are plain ASCII letters, which
-- P.Encode leaves untouched, so a name costs only its own length.
--
-- Deserialise re-attaches the prefix, so ECS_Order and ECS_Data still see the
-- `realm:name` form everywhere and nothing else in the system changes.
local function OrderKeyPrefix(realm)
    if ( type(realm) ~= "string" or realm == "" ) then
        return nil;
    end
    return string.lower(realm) .. ":";
end

local function CompactOrderKey(key, prefix)
    if ( not prefix ) then
        return key;
    end
    if ( string.sub(key, 1, #prefix) == prefix ) then
        return string.sub(key, #prefix + 1);
    end
    return key;   -- a key from another realm is kept whole rather than mangled
end

function P.Serialise(store)
    if ( type(store) ~= "table" ) then
        return nil;
    end
    local prefix = OrderKeyPrefix(store.realm);
    local order = {};
    if ( type(store.order) == "table" ) then
        for index = 1, #store.order do
            local key = store.order[index];
            if ( type(key) == "string" and key ~= "" ) then
                order[#order + 1] = P.Encode(CompactOrderKey(key, prefix));
            end
        end
    end

    local notes = {};
    if ( type(store.notes) == "table" ) then
        local keys = {};
        for key in pairs(store.notes) do
            keys[#keys + 1] = key;
        end
        table.sort(keys);   -- deterministic output, so tests and diffs are stable
        for index = 1, #keys do
            local key = keys[index];
            local text = store.notes[key];
            if ( type(key) == "string" and type(text) == "string" and text ~= "" ) then
                notes[#notes + 1] = P.Encode(CompactOrderKey(key, prefix))
                    .. NOTE_SEP .. P.Encode(text);
            end
        end
    end

    return table.concat({
        "v=" .. tostring(store.version or C.SCHEMA_VERSION),
        "a=" .. P.Encode(store.account or ""),
        "r=" .. P.Encode(store.realm or ""),
        "o=" .. table.concat(order, ","),
        "n=" .. table.concat(notes, NOTE_PAIR),
    }, "|");
end

-- Splits "k=v|k=v" on the FIRST '=' of each segment.
local function ParsePairs(text)
    local out = {};
    for segment in string.gmatch(text, "([^|]+)") do
        local key, value = string.match(segment, "^(%w+)=(.*)$");
        if ( key ) then
            out[key] = value;
        end
    end
    return out;
end

function P.Deserialise(text)
    if ( type(text) ~= "string" or text == "" ) then
        return nil;
    end

    local pairs_ = ParsePairs(text);

    local version = tonumber(pairs_.v);
    if ( not version ) then
        return nil;
    end

    local store = {
        version = version,
        account = P.Decode(pairs_.a or ""),
        realm   = P.Decode(pairs_.r or ""),
        order   = {},
        notes   = {},
    };

    -- Re-attach the realm prefix that Serialise stripped (see OrderKeyPrefix).
    -- A token that already contains ':' is left alone, so a record written by an
    -- older or hand-edited build still decodes to a usable key.
    local prefix = OrderKeyPrefix(store.realm);
    local function ExpandKey(token)
        if ( not prefix ) then
            return token;
        end
        if ( string.find(token, ":", 1, true) ) then
            return token;
        end
        return prefix .. token;
    end

    if ( type(pairs_.o) == "string" ) then
        for chunk in string.gmatch(pairs_.o, "[^,]+") do
            local key = ExpandKey(P.Decode(chunk));
            if ( key ~= "" ) then
                store.order[#store.order + 1] = key;
            end
        end
    end

    if ( type(pairs_.n) == "string" and pairs_.n ~= "" ) then
        for chunk in string.gmatch(pairs_.n, "([^" .. NOTE_PAIR .. "]+)") do
            local key, value = string.match(chunk, "^(.-)" .. NOTE_SEP .. "(.*)$");
            if ( key and value ) then
                local decodedKey = ExpandKey(P.Decode(key));
                local decodedText = P.Decode(value);
                if ( decodedKey ~= "" ) then
                    store.notes[decodedKey] = decodedText;
                end
            end
        end
    end

    return store;
end

-- ---------------------------------------------------------------- sharding
-- "part/total;data" so chunks can be reassembled regardless of the order the
-- cvars come back in.
function P.Shard(payload, maxChunk)
    maxChunk = maxChunk or P.MAX_CHUNK;
    if ( type(payload) ~= "string" ) then
        return nil;
    end
    local total = math.max(1, math.ceil(#payload / maxChunk));
    local shards = {};
    for index = 1, total do
        local from = (index - 1) * maxChunk + 1;
        local to   = math.min(index * maxChunk, #payload);
        shards[index] = index .. "/" .. total .. ";" .. string.sub(payload, from, to);
    end
    return shards;
end

function P.JoinShards(chunks)
    if ( type(chunks) ~= "table" ) then
        return nil;
    end
    -- order by the explicit index, not by arrival order
    local ordered = {};
    local expectedTotal = nil;
    for index = 1, #chunks do
        local position, total, data = string.match(chunks[index], "^(%d+)/(%d+);(.*)$");
        if ( position ) then
            position = tonumber(position);
            total = tonumber(total);
            if ( expectedTotal == nil ) then
                expectedTotal = total;
            end
            if ( total ~= expectedTotal ) then
                return nil;   -- mixed generations: refuse rather than splice junk
            end
            ordered[position] = data;
        end
    end
    if ( not expectedTotal ) then
        return nil;
    end
    local parts = {};
    for index = 1, expectedTotal do
        if ( not ordered[index] ) then
            return nil;   -- incomplete store; caller falls back to server order
        end
        parts[#parts + 1] = ordered[index];
    end
    return table.concat(parts);
end

-- Full cvar value for one shard:
--   ecs1:<shardLength>|<shard><original value>
--
-- The shard payload itself contains '|' (our segment separator), so the shard
-- cannot be delimited by a pipe -- a non-greedy match would stop at the first
-- one and silently truncate the store. The length prefix makes the split
-- unambiguous no matter what the payload contains. The original value is kept
-- verbatim so we never destroy the real setting.
function P.WrapValue(shard, original)
    shard = shard or "";
    return P.MARKER .. tostring(#shard) .. "|" .. shard .. (original or "");
end

-- Parse an ECS envelope from ANY schema version. Current reads still require the
-- exact active marker, but probing uses this to peel old ecs1/ecs2 wrappers off
-- before it captures an "original" value. Without this migration step, every
-- startup could preserve the previous ECS envelope as the new original and grow
-- the CVar until the client truncated the following Config.wtf line.
local function UnwrapAnyECSValue(value)
    if ( type(value) ~= "string" ) then
        return nil, nil, nil;
    end

    local marker = string.match(value, "^(ecs%d+:)");
    if ( not marker ) then
        return nil, nil, nil;
    end

    local body = string.sub(value, #marker + 1);
    local lengthText, rest = string.match(body, "^(%d+)|(.*)$");
    if ( not lengthText ) then
        return nil, nil, marker;
    end

    local length = tonumber(lengthText);
    if ( not length or length < 0 or #rest < length ) then
        return nil, nil, marker;
    end

    return string.sub(rest, 1, length), string.sub(rest, length + 1), marker;
end

function P.UnwrapValue(value)
    local shard, original, marker = UnwrapAnyECSValue(value);
    if ( marker ~= P.MARKER ) then
        return nil, nil;
    end
    return shard, original;
end

-- Return the real client-owned value behind every old/current ECS wrapper. A
-- malformed ECS-looking value returns nil so callers can refuse that slot rather
-- than preserve or extend corruption. The depth guard is deliberately small:
-- legitimate data has one envelope; deeper nesting is legacy damage only.
function P.CleanOriginalValue(value)
    local current = type(value) == "string" and value or "";
    for _ = 1, 8 do
        local shard, original, marker = UnwrapAnyECSValue(current);
        if ( not marker ) then
            return current;
        end
        if ( shard == nil ) then
            return nil;
        end
        current = original or "";
    end

    if ( string.match(current, "^ecs%d+:") ) then
        return nil;
    end
    return current;
end

-- ---------------------------------------------------------------- backend
-- Default backend: real cvars, every access pcall-guarded (rule 1).
P.Backend = P.Backend or {
    get = function(name)
        local ok, value = pcall(GetCVar, name);
        if ( not ok ) then
            return nil;
        end
        return value;
    end,
    set = function(name, value)
        local ok = pcall(SetCVar, name, value);
        return ok and true or false;
    end,
};

function P.SetBackend(backend)
    P.Backend = backend;
end

-- ---------------------------------------------------------------- discovery
-- Write a marked probe, read it back, and keep only the cvars that stuck. This
-- is the only reliable way to know which names are writable (rule 2).
--
-- Accepts candidates as either a bare cvar name string, or a table
-- { name = "...", original = "..." }. When `original` is not supplied it is read
-- from the backend, so callers never have to pre-snapshot values.
function P.ProbeCandidates(candidates, backend)
    backend = backend or P.Backend;
    candidates = candidates or P.CANDIDATE_CVARS;

    local writable = {};
    for index = 1, #candidates do
        local entry = candidates[index];
        local name, declaredOriginal;
        if ( type(entry) == "table" ) then
            name = entry.name;
            declaredOriginal = entry.original;
        else
            name = entry;
        end

        if ( type(name) == "string" and name ~= "" ) then
            local original = declaredOriginal;
            if ( original == nil ) then
                original = backend.get(name);
            end
            original = P.CleanOriginalValue(original);

            -- A Freeborn envelope is owned by CharacterCreate/FreebornClaim. ECS
            -- must never wrap or probe through it. This also protects installs
            -- upgraded from the old shared-slot scheme if a badge record happens
            -- to be sitting in one of the remaining candidates.
            local foreignOwned = type(original) == "string"
                and string.sub(original, 1, 3) == "fb:";

            if ( original ~= nil and not foreignOwned ) then
                local shard = "probe" .. tostring(index) .. "/1;P";
                local probe = P.WrapValue(shard, original);
                local ok = backend.set(name, probe);
                local readBack = ok and backend.get(name) or nil;
                -- Restore even when the probe was truncated or otherwise failed
                -- read-back. Leaving a rejected probe behind is itself corruption.
                backend.set(name, original or "");
                if ( ok and readBack == probe ) then
                    writable[#writable + 1] = { name = name, original = original };
                end
            end
        end
    end
    return writable;
end

-- ---------------------------------------------------------------- capacity
-- How much a cvar will actually hold is NOT discoverable offline, and guessing it
-- wrong is not harmless: too small wastes slots, too large loses the write.
--
-- The measured consequence of guessing: at the conservative default of 170 chars
-- a full 100-character order needs 8 shards but only 6 cvars exist, so the order
-- could never be saved. The real limit has to come from the client, so measure it
-- - write a value of a known length, read it back, and binary-search the largest
-- length that survives intact. A client that silently truncates fails the
-- comparison, so truncation is DETECTED rather than trusted.
--
-- Every probe restores the value it found, exactly as ProbeCandidates does, so a
-- stored record can never be damaged by being measured.
P.PROBE_MAX_VALUE = 250;   -- nothing plausible exceeds a 255-char cvar buffer

-- Room reserved inside every value for the wrapper (`ecsN:<len>|`) and the shard
-- header (`12/34;`), so a payload chunk cannot overflow the measured limit. The
-- pre-existing value is appended after the payload, so its length is deducted too
-- - a long original would otherwise silently eat the room the shard needs.
P.PROBE_RESERVE = 24;

local function ValueFits(name, length, backend)
    local probe = string.rep("A", length);
    if ( not backend.set(name, probe) ) then
        return false;
    end
    return backend.get(name) == probe;
end

-- Measures each slot and records the payload room on the slot itself, so the
-- measurement is paid for once (at discovery) rather than on every save.
function P.ProbeCapacity(slots, backend)
    backend = backend or P.Backend;
    slots = slots or P.ProbeCandidates(nil, backend);

    local capacities = {};
    for index = 1, #slots do
        local slot = slots[index];
        local name, original = slot.name, slot.original;

        -- invariant: `low` is known to fit, `high` is untested or known too big
        local low = 0;
        if ( ValueFits(name, 1, backend) ) then
            low = 1;
            local high = P.PROBE_MAX_VALUE;
            while ( low < high ) do
                local mid = math.floor((low + high + 1) / 2);
                if ( ValueFits(name, mid, backend) ) then
                    low = mid;
                else
                    high = mid - 1;
                end
            end
        end

        -- restore whatever the search left behind, unconditionally
        backend.set(name, original or "");

        local room = low - P.PROBE_RESERVE - #(original or "");
        if ( room < 1 ) then
            room = nil;   -- cannot even hold a header: not usable for storage
        end
        capacities[index] = room;
        slot.capacity = room;
    end
    return capacities;
end

-- Payload room per slot: what was measured, or the conservative default when the
-- capacity has not been probed (which is also the path every offline test takes).
function P.SlotCapacities(slots)
    local capacities = {};
    for index = 1, #(slots or {}) do
        local slot = slots[index];
        capacities[index] = (slot and slot.capacity) or P.MAX_CHUNK;
    end
    return capacities;
end

-- Shards a payload using each slot's OWN room rather than assuming every cvar is
-- the same size. Returns nil when the payload does not fit the slots available.
function P.ShardToSlots(payload, capacities)
    if ( type(payload) ~= "string" or type(capacities) ~= "table" ) then
        return nil;
    end

    local pieces = {};
    local position = 1;
    local total = #payload;

    for index = 1, #capacities do
        if ( position > total ) then
            break;
        end
        local room = capacities[index];
        if ( room and room > 0 ) then
            pieces[#pieces + 1] = string.sub(payload, position, position + room - 1);
            position = position + room;
        end
    end

    if ( position <= total ) then
        return nil;   -- ran out of slots before the payload ran out
    end
    if ( #pieces == 0 ) then
        pieces[1] = "";   -- an empty payload still needs one shard
    end

    local shards = {};
    for index = 1, #pieces do
        shards[index] = index .. "/" .. #pieces .. ";" .. pieces[index];
    end
    return shards;
end

-- ---------------------------------------------------------------- load / save
-- `backend` defaults to the real cvar backend; passing one is what makes the
-- whole layer testable without a client.
--
-- Returns store, nil  on success, or nil, reason on any failure. Never raises.
-- The whole read path lives in ONE place so a full read and any other read can
-- never drift: shard reassembly, parsing and every identity check.
local function ReadStore(account, realm, slots, backend)
    slots = slots or P.ProbeCandidates(nil, backend);
    if ( #slots == 0 ) then
        return nil, "no writable storage slot";
    end

    local chunks = {};
    for index = 1, #slots do
        local raw = backend.get(slots[index].name);
        local shard = P.UnwrapValue(raw);
        if ( shard ) then
            chunks[#chunks + 1] = shard;
        end
    end
    if ( #chunks == 0 ) then
        return nil, "no stored record";
    end

    local payload = P.JoinShards(chunks);
    if ( not payload ) then
        return nil, "shards missing or mismatched";
    end

    local store = P.Deserialise(payload);
    if ( not store ) then
        return nil, "record did not parse";
    end
    if ( store.version ~= C.SCHEMA_VERSION ) then
        -- spec 34: a newer format is ignored rather than misread, and an
        -- older one is simply not applied. Stale metadata never blocks login.
        return nil, "schema version " .. tostring(store.version)
            .. " != " .. tostring(C.SCHEMA_VERSION);
    end
    if ( account and store.account ~= "" and store.account ~= account ) then
        return nil, "account mismatch";
    end
    if ( realm and store.realm ~= "" and store.realm ~= realm ) then
        return nil, "realm mismatch";
    end

    return store, nil;
end

function P.Load(account, realm, slots, backend)
    backend = backend or P.Backend;
    local ok, result, reason = pcall(ReadStore, account, realm, slots, backend);
    if ( not ok ) then
        return nil, "load error: " .. tostring(result);
    end
    return result, reason;
end

-- Writes the store, sharded across the writable slots. Read-back verified.
-- Returns true, nil on success, or false, reason.
function P.Save(store, slots, backend)
    backend = backend or P.Backend;
    local ok, saved, reason = pcall(function()
        slots = slots or P.ProbeCandidates(nil, backend);
        if ( #slots == 0 ) then
            return false, "no writable storage slot";
        end

        local payload = P.Serialise(store);
        if ( not payload ) then
            return false, "store did not serialise";
        end

        local shards = P.ShardToSlots(payload, P.SlotCapacities(slots));
        if ( not shards ) then
            return false, "payload does not fit " .. #slots .. " writable slots";
        end

        -- write every shard, then verify every shard
        for index = 1, #shards do
            local slot = slots[index];
            local value = P.WrapValue(shards[index], slot.original);
            local wrote = backend.set(slot.name, value);
            if ( not wrote ) then
                return false, "write refused on " .. slot.name;
            end
        end
        for index = 1, #shards do
            local slot = slots[index];
            local value = P.WrapValue(shards[index], slot.original);
            if ( backend.get(slot.name) ~= value ) then
                return false, "read-back mismatch on " .. slot.name;
            end
        end

        -- clear any slots we previously used but no longer need, so a shrinking
        -- store cannot leave stale shards behind to corrupt the next load
        for index = #shards + 1, #slots do
            local slot = slots[index];
            local existing = backend.get(slot.name);
            if ( P.UnwrapValue(existing) ) then
                backend.set(slot.name, slot.original or "");
            end
        end

        return true, nil;
    end);

    if ( not ok ) then
        return false, "save error: " .. tostring(saved);
    end
    return saved, reason;
end

-- Write-side graceful degradation (spec 11 / 33).
--
-- The real failure is CAPACITY, and it is measured, not hypothetical: notes are
-- by far the largest part of a record (100 characters with 20-char notes need 39
-- shards; the order alone needs a fraction of that) and there are only ever a
-- handful of writable cvars. Without this, a roster whose notes outgrew the
-- budget would fail to save AT ALL - so reordering characters would silently do
-- nothing, and the user would lose the order that is the point of the feature.
--
-- The ORDER is the primary feature and the notes are secondary, so on failure
-- this retries once with the notes dropped. Returns:
--   true,  nil,    false - saved in full
--   true,  reason, true  - saved, but the NOTES were sacrificed to keep the order
--   false, reason, false - nothing saved; the caller must surface this
function P.SaveDegraded(store, slots, backend)
    backend = backend or P.Backend;

    local saved, reason = P.Save(store, slots, backend);
    if ( saved ) then
        return true, nil, false;
    end
    if ( type(store) ~= "table" ) then
        return false, reason, false;
    end
    if ( type(store.notes) ~= "table" or next(store.notes) == nil ) then
        return false, reason, false;   -- there is nothing left to give up
    end

    local reduced = P.MakeStore(store.account, store.realm, store.order, {});
    local savedWithoutNotes, retryReason = P.Save(reduced, slots, backend);
    if ( savedWithoutNotes ) then
        return true, reason, true;
    end
    return false, retryReason, false;
end

-- ---------------------------------------------------------------- helpers
function P.MakeStore(account, realm, order, notes)
    return {
        version = C.SCHEMA_VERSION,
        account = account or "",
        realm   = realm or "",
        order   = order or {},
        notes   = notes or {},
    };
end
