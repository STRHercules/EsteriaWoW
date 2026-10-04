--[==[ test_persistence.lua -------------------------------------------------------
    Proves the cvar store survives a restart, degrades instead of failing, and
    refuses to be corrupted by stale or foreign metadata (spec 11, 33, 34).

    Uses a fake cvar backend so unwritable names, length limits, silent write
    refusal and integer-normalisation can all be simulated without a client.
]==]

local P = ECS.Persistence;
local C = ECS.Const;

-- ---------------------------------------------------------------- fake cvar table
-- opts.initial : preloaded cvar values
-- opts.reject  : set of names whose writes are silently refused
-- opts.maxLen  : per-value length limit (simulates a fixed cvar buffer)
local function FakeBackend(opts)
    opts = opts or {};
    local values = {};
    if ( opts.initial ) then
        for name, value in pairs(opts.initial) do
            values[name] = value;
        end
    end
    local writes = 0;
    return {
        values = values,
        get = function(name)
            return values[name];
        end,
        set = function(name, value)
            if ( opts.reject and opts.reject[name] ) then
                return false;
            end
            if ( opts.maxLen and type(value) == "string" and #value > opts.maxLen ) then
                return false;   -- a real cvar silently truncates or refuses
            end
            writes = writes + 1;
            values[name] = value;
            return true;
        end,
        writeCount = function() return writes; end,
    };
end

local SLOTS = {
    { name = "Sound_VoiceChatOutputDriverName", original = "1" },
    { name = "Sound_OutputDriverName",          original = "0" },
    { name = "lastCharacterDeleted",            original = "" },
};

-- ---------------------------------------------------------------- 1. codec
ECS_EQ(P.Decode(P.Encode("Main tank")), "Main tank", "1a: simple text round-trips");
local nasty = "a|b,c;d\30e\31f%g h\\i";
ECS_EQ(P.Decode(P.Encode(nasty)), nasty, "1b: delimiters and percent survive");
ECS_EQ(P.Decode(P.Encode("")), "", "1c: empty string");
ECS_EQ(P.Encode(nil), "", "1d: nil encodes to empty, not an error");
ECS_EQ(P.Decode(nil), "", "1e: nil decodes to empty, not an error");
ECS_EQ((string.find(P.Encode("a b"), " ", 1, true)), nil, "1f: encoding removes spaces");
local encodedStore = P.Serialise(P.MakeStore("A", "R", {}, { ["r:n"] = nasty }));
ECS_CHECK(string.find(encodedStore, "\30", 1, true) == nil and string.find(encodedStore, "\31", 1, true) == nil,
    "1g: serialized store contains no raw control separators");

-- ---------------------------------------------------------------- 2. store codec
local store = P.MakeStore("ZACHGM", "Esteria",
    { "esteria:nat", "esteria:zach" },
    { ["esteria:nat"] = "Main tank", ["esteria:zach"] = "Bank alt | ICC" });

local text = P.Serialise(store);
ECS_CHECK(type(text) == "string" and #text > 0, "2a: store serialises");

local back = P.Deserialise(text);
ECS_CHECK(back ~= nil, "2b: store deserialises");
ECS_EQ(back.version, C.SCHEMA_VERSION, "2c: version preserved");
ECS_EQ(back.account, "ZACHGM", "2d: account preserved");
ECS_EQ(back.realm, "Esteria", "2e: realm preserved");
ECS_EQ(table.concat(back.order, ","), "esteria:nat,esteria:zach", "2f: order preserved");
ECS_EQ(back.notes["esteria:nat"], "Main tank", "2g: note preserved");
ECS_EQ(back.notes["esteria:zach"], "Bank alt | ICC",
    "2h: note containing a delimiter preserved");

ECS_EQ(P.Deserialise(""), nil, "2i: empty text yields nil");
ECS_EQ(P.Deserialise("garbage"), nil, "2j: junk yields nil");
ECS_EQ(P.Deserialise("v=notanumber|o=a"), nil, "2k: bad version yields nil");
ECS_EQ(P.Deserialise(nil), nil, "2l: nil yields nil");

-- 2m: an empty store still round-trips
local emptyBack = P.Deserialise(P.Serialise(P.MakeStore("A", "R", {}, {})));
ECS_EQ(#emptyBack.order, 0, "2m: empty order round-trips");
ECS_CHECK(next(emptyBack.notes) == nil, "2n: empty notes round-trip");

-- 2o: COMPACT ORDER KEYS. Every key in a roster repeats the same realm, and
-- P.Encode escapes ':' to '%3A', so a v1 record spent 20 chars per character
-- re-encoding a realm that was already in the `r=` field. That is what made a
-- full 100-character roster unpersistable (14 shards against 6 available cvars).
-- No escaped colon may survive in the payload now.
ECS_CHECK(string.find(text, "%3A", 1, true) == nil,
    "2o: order keys omit the realm prefix instead of escaping it per key");
ECS_EQ(P.Decode(text:match("o=([^|]*)")), "nat,zach", "2p: the order field is name-only");
local expanded = P.Deserialise(text);
ECS_EQ(table.concat(expanded.order, ","), "esteria:nat,esteria:zach",
    "2q: the realm prefix is re-attached on read, so callers see the same keys");

-- 2r: a key that is NOT under this record's realm keeps its own realm rather
-- than being silently re-prefixed into a different character.
local foreignRealm = P.MakeStore("A", "esteria", { "other:name" }, {});
local foreignBack = P.Deserialise(P.Serialise(foreignRealm));
ECS_EQ(foreignBack.order[1], "other:name", "2r: a foreign-realm key is not re-prefixed");

-- ---------------------------------------------------------------- 3. sharding
local payload = string.rep("abcdefghij", 20);   -- 200 chars
local shards = P.Shard(payload, 60);
ECS_EQ(#shards, 4, "3a: 200 chars at 60 per shard is 4 shards");
ECS_EQ(P.JoinShards(shards), payload, "3b: shards rejoin exactly");

-- 3c: reassembly must not depend on arrival order
local reversed = { shards[4], shards[2], shards[1], shards[3] };
ECS_EQ(P.JoinShards(reversed), payload, "3c: out-of-order shards rejoin correctly");

-- 3d: a missing shard is refused rather than spliced into corrupt data
ECS_EQ(P.JoinShards({ shards[1], shards[2] }), nil, "3d: incomplete shard set refused");
-- 3e: mixed generations are refused
ECS_EQ(P.JoinShards({ "1/2;aa", "2/3;bb" }), nil, "3e: mismatched totals refused");
ECS_EQ(P.JoinShards({}), nil, "3f: no shards refused");
ECS_EQ(P.JoinShards(nil), nil, "3g: nil shards refused");
ECS_EQ(#P.Shard(""), 1, "3h: empty payload still shards once");

-- ---------------------------------------------------------------- 4. wrapping
local wrapped = P.WrapValue("1/1;hello", "ORIGINAL");
local shard, original = P.UnwrapValue(wrapped);
ECS_EQ(shard, "1/1;hello", "4a: shard unwrapped");
ECS_EQ(original, "ORIGINAL", "4b: original value preserved");
ECS_EQ(P.UnwrapValue("something else"), nil, "4c: unmarked value is not ours");
ECS_EQ(P.UnwrapValue(nil), nil, "4d: nil value is safe");

-- 4e: REGRESSION - a shard whose payload contains the segment separator '|' must
-- survive wrapping intact. A separator-based split silently truncated the store
-- here, which emptied the account field and defeated the account scoping check.
local pipey = "1/1;v=1|a=ZACHGM|r=Esteria|o=esteria%3Anat|n=";
local pipeShard, pipeOrig = P.UnwrapValue(P.WrapValue(pipey, "1"));
ECS_EQ(pipeShard, pipey, "4e: shard containing '|' round-trips without truncation");
ECS_EQ(pipeOrig, "1", "4f: original still recovered after a pipe-laden shard");

-- 4g: a malformed wrapper (no length prefix) is rejected, not misread
ECS_EQ(P.UnwrapValue(P.MARKER .. "no-length-here"), nil, "4g: wrapper without a length is rejected");
-- 4h: a length longer than the remaining data is rejected
ECS_EQ(P.UnwrapValue(P.MARKER .. "999|short"), nil, "4h: over-long length is rejected");
-- 4i: an empty shard is legal (used when clearing)
local emptyShard, emptyOrig = P.UnwrapValue(P.WrapValue("", "kept"));
ECS_EQ(emptyShard, "", "4i: empty shard unwraps to empty");
ECS_EQ(emptyOrig, "kept", "4j: original preserved with an empty shard");

-- 4k-4m: migration hygiene. Old/current ECS envelopes may be nested because an
-- earlier probe captured the prior envelope as the CVar's "original" value. The
-- cleaner must peel all of them and recover only the real client-owned tail.
local legacyNested = "ecs2:5|1/1;A" .. "ecs1:5|1/1;BSystem Default";
ECS_EQ(P.CleanOriginalValue(legacyNested), "System Default",
    "4k: nested legacy ECS wrappers collapse to the real original value");
ECS_EQ(P.CleanOriginalValue("plain"), "plain", "4l: unrelated values are untouched");
ECS_EQ(P.CleanOriginalValue("ecs2:999|short"), nil,
    "4m: malformed ECS-looking values are rejected instead of preserved");

-- ---------------------------------------------------------------- 5. probe
-- Declared originals win: when the caller supplies one, that is what is restored.
local backend = FakeBackend({ initial = { ["Sound_OutputDriverName"] = "keepme" } });
local writable = P.ProbeCandidates(SLOTS, backend);
ECS_EQ(#writable, 3, "5a: all three probe as writable");
ECS_EQ(backend.values["Sound_OutputDriverName"], "0",
    "5b: probing restores the DECLARED original when one is supplied");

-- With bare string candidates the backend value is read first, then restored.
local readBack = FakeBackend({ initial = { ["Sound_OutputDriverName"] = "keepme" } });
local readSlots = P.ProbeCandidates({ "Sound_OutputDriverName" }, readBack);
ECS_EQ(#readSlots, 1, "5b2: a bare string candidate probes as writable");
ECS_EQ(readSlots[1].original, "keepme", "5b3: original read from the backend");
ECS_EQ(readBack.values["Sound_OutputDriverName"], "keepme",
    "5b4: backend original restored after probing");

local migratedBackend = FakeBackend({ initial = {
    ["Sound_OutputDriverName"] = "ecs2:5|1/1;Aecs1:5|1/1;BSystem Default",
} });
local migratedSlots = P.ProbeCandidates({ "Sound_OutputDriverName" }, migratedBackend);
ECS_EQ(#migratedSlots, 1, "5b4a: a legacy nested ECS slot is recoverable");
ECS_EQ(migratedSlots[1].original, "System Default",
    "5b4b: probing captures the cleaned client-owned original, not another ECS envelope");
ECS_EQ(migratedBackend.values["Sound_OutputDriverName"], "System Default",
    "5b4c: probing repairs the legacy nested value in-place");

local freebornOwned = FakeBackend({ initial = {
    ["Sound_VoiceChatOutputDriverName"] = "fb:123|System Default",
} });
ECS_EQ(#P.ProbeCandidates({ "Sound_VoiceChatOutputDriverName" }, freebornOwned), 0,
    "5b4d: ECS refuses a slot currently owned by a Freeborn envelope");
ECS_EQ(freebornOwned.values["Sound_VoiceChatOutputDriverName"], "fb:123|System Default",
    "5b4e: refusing a Freeborn-owned slot leaves it byte-for-byte untouched");

-- ---------------------------------------------------------------- 5b. capacity probe
-- The real per-cvar length limit is not discoverable offline, and guessing it is
-- what made a full 100-character order unpersistable. These assert that the limit
-- is MEASURED from the backend, that the measurement is restored, and that the
-- measured room is what Save actually uses.
local limited = FakeBackend({ maxLen = 120, initial = { ["Sound_OutputDriverName"] = "keepme" } });
local limitedSlots = P.ProbeCandidates(SLOTS, limited);
ECS_EQ(#limitedSlots, 3, "5b5: slots probe as writable before the capacity probe");

local capacities = P.ProbeCapacity(limitedSlots, limited);
-- the declared original ("0") is appended to every stored value, so its length is
-- deducted from the room as well
ECS_EQ(capacities[1], 120 - P.PROBE_RESERVE - 1,
    "5b6: the probe finds the backend's real per-cvar limit");

-- 5b7: the probe writes large values into the cvar, so it MUST put back what it
-- found. This uses bare names so the original is the backend's real value
-- ("keepme") rather than the declared one - the capacity probe must not be the
-- thing that destroys a user's cvar (or our own stored record).
local keepBackend = FakeBackend({ maxLen = 120,
    initial = { ["Sound_OutputDriverName"] = "keepme" } });
local keepSlots = P.ProbeCandidates({ "Sound_OutputDriverName" }, keepBackend);
P.ProbeCapacity(keepSlots, keepBackend);
ECS_EQ(keepBackend.values["Sound_OutputDriverName"], "keepme",
    "5b7: the capacity probe restores the stored value it found");

-- A cvar that accepts nothing cannot hold even a shard header, so it must be
-- reported as unusable rather than silently contributing zero room.
local tinyLimit = FakeBackend({ maxLen = 10 });
local tinySlots2 = P.ProbeCandidates(SLOTS, tinyLimit);
local tinyCaps = P.ProbeCapacity(tinySlots2, tinyLimit);
ECS_EQ(tinyCaps[1], nil, "5b8: a cvar too small for a header is not usable storage");

-- Without a probe the conservative default is used, which is the offline path.
ECS_EQ(P.SlotCapacities(limitedSlots)[1], 120 - P.PROBE_RESERVE - 1,
    "5b9: a probed slot reports its measured room");
local unprobed = { { name = "x", original = "1" } };
ECS_EQ(P.SlotCapacities(unprobed)[1], P.MAX_CHUNK,
    "5b10: an unprobed slot falls back to the conservative default");

-- 5b11: capacity-aware sharding fills each slot to ITS OWN room.
-- where the first is small and the rest are large must not waste the large ones.
local mixed = P.ShardToSlots(string.rep("x", 30), { 10, 10, 10 });
ECS_EQ(#mixed, 3, "5b11: sharding fills each slot independently");
ECS_EQ(P.JoinShards(mixed), string.rep("x", 30), "5b12: mixed-capacity shards rejoin exactly");
ECS_EQ(P.ShardToSlots(string.rep("x", 31), { 10, 10, 10 }), nil,
    "5b13: a payload that overruns the slots is refused, not truncated");

local hostile = FakeBackend({ reject = { ["Sound_VoiceChatOutputDriverName"] = true } });
local partial = P.ProbeCandidates(SLOTS, hostile);
ECS_EQ(#partial, 2, "5c: an unwritable cvar is dropped from the pool");

local dead = FakeBackend({ reject = {
    ["Sound_VoiceChatOutputDriverName"] = true,
    ["Sound_OutputDriverName"] = true,
    ["lastCharacterDeleted"] = true,
} });
ECS_EQ(#P.ProbeCandidates(SLOTS, dead), 0, "5d: no writable cvar yields an empty pool");

-- ---------------------------------------------------------------- 6. save / load
local live = FakeBackend();
P.SetBackend(live);   -- Save/Load default to the active backend
local saveSlots = P.ProbeCandidates(SLOTS, live);
ECS_EQ(#saveSlots, 3, "6a: pool discovered");

-- 6a2: the discovered slot must carry the cvar NAME as a string. Passing a table
-- through to GetCVar/SetCVar would fail against the real client; this pins it.
ECS_EQ(type(saveSlots[1].name), "string", "6a2: slot name is a string");
ECS_EQ(saveSlots[1].name, "Sound_VoiceChatOutputDriverName", "6a3: slot name preserved");
ECS_EQ(saveSlots[1].original, "1", "6a4: declared original preserved");

local saved, saveErr = P.Save(store, saveSlots);
ECS_CHECK(saved == true, "6b: save succeeds (" .. tostring(saveErr) .. ")");

local loaded, loadErr = P.Load("ZACHGM", "Esteria", saveSlots);
if ( ECS_CHECK(loaded ~= nil, "6c: load succeeds (" .. tostring(loadErr) .. ")") ) then
    ECS_EQ(table.concat(loaded.order, ","), "esteria:nat,esteria:zach", "6d: order survived");
    ECS_EQ(loaded.notes["esteria:nat"], "Main tank", "6e: note survived");
end

-- 6e2: plain-string candidates must also work, reading the original from the
-- backend rather than requiring the caller to pre-snapshot it.
local plainBackend = FakeBackend({ initial = { ["Sound_OutputDriverName"] = "MYORIG" } });
local plainSlots = P.ProbeCandidates({ "Sound_OutputDriverName" }, plainBackend);
ECS_EQ(#plainSlots, 1, "6e2: string candidate probes as writable");
ECS_EQ(plainSlots[1].name, "Sound_OutputDriverName", "6e3: string candidate keeps its name");
ECS_EQ(plainSlots[1].original, "MYORIG", "6e4: original read from the backend");
ECS_CHECK(plainBackend.values["Sound_OutputDriverName"] == "MYORIG",
    "6e5: original restored after probing");

-- 6f: the original cvar values are still recoverable from the stored payload
local _, preserved = P.UnwrapValue(live.values[SLOTS[1].name]);
ECS_EQ(preserved, "1", "6f: original cvar value kept in the trailing field");

-- ---------------------------------------------------------------- 7. scoping
local mismatched, reason = P.Load("SOMEONE_ELSE", "Esteria", saveSlots);
ECS_EQ(mismatched, nil, "7a: another account's store is not applied");
ECS_CHECK(string.find(reason, "account", 1, true) ~= nil, "7b: reason mentions account");

local wrongRealm, reason2 = P.Load("ZACHGM", "OtherRealm", saveSlots);
ECS_EQ(wrongRealm, nil, "7c: another realm's store is not applied");
ECS_CHECK(string.find(reason2, "realm", 1, true) ~= nil, "7d: reason mentions realm");

-- 7e: a blank account/realm on the store matches anything (legacy tolerance)
local loose = P.MakeStore("", "", { "esteria:nat" }, {});
P.Save(loose, saveSlots);
ECS_CHECK(P.Load("ANYONE", "ANYWHERE", saveSlots) ~= nil,
    "7e: a store with no account/realm scope loads for anyone");

-- ---------------------------------------------------------------- 8. corrupt / stale
P.Save(store, saveSlots);
live.values[SLOTS[1].name] = P.WrapValue("1/3;TRUNCATED", "1");
ECS_EQ(P.Load("ZACHGM", "Esteria", saveSlots), nil, "8a: truncated shard set refused");
ECS_CHECK(P.Load("ZACHGM", "Esteria", saveSlots) == nil,
    "8b: corrupt store does not raise and does not apply");

live.values[SLOTS[1].name] = P.WrapValue("1/1;v=99|a=X|r=Y|o=|n=", "1");
ECS_EQ(P.Load("ZACHGM", "Esteria", saveSlots), nil,
    "8c: a newer schema version is ignored, not misread (spec 34)");

-- 8c2: a store that parses but is scoped to another account must NOT be applied.
-- This is the assertion that caught the pipe-truncation bug: truncation emptied
-- the account field, which silently disabled the scope check.
--
-- The version is taken from the constant rather than hardcoded, so that bumping
-- SCHEMA_VERSION cannot quietly turn this into a version-mismatch test instead -
-- the account check must be the reason this record is refused, and 8c3 proves it.
live.values[SLOTS[1].name] = P.WrapValue(
    "1/1;v=" .. tostring(C.SCHEMA_VERSION) .. "|a=SOMEONE|r=Esteria|o=x|n=", "1");
local foreign, foreignReason = P.Load("ZACHGM", "Esteria", saveSlots);
ECS_EQ(foreign, nil, "8c2: a foreign account's store is refused even when intact");
ECS_CHECK(string.find(tostring(foreignReason), "account", 1, true) ~= nil,
    "8c3: and the reason names the account as the cause");

live.values[SLOTS[1].name] = "utterly unrelated";
local none = P.Load("ZACHGM", "Esteria", saveSlots);
ECS_CHECK(none == nil, "8d: an unrelated cvar value is ignored");

-- ---------------------------------------------------------------- 9. degradation
-- A backend whose cvars are short and few: the store must refuse cleanly, and
-- the caller must be able to retry with less data rather than losing everything.
local tiny = FakeBackend({ maxLen = 60 });
P.SetBackend(tiny);
local tinySlots = P.ProbeCandidates(SLOTS, tiny);
local bigOrder = {};
for i = 1, 40 do bigOrder[i] = "esteria:character" .. i; end
local bigStore = P.MakeStore("A", "R", bigOrder, {});
local okBig, errBig = P.Save(bigStore, tinySlots);
ECS_CHECK(okBig == false, "9a: an oversized store is refused, not half-written");
ECS_CHECK(string.find(errBig, "slots", 1, true) ~= nil, "9b: reason explains capacity");

-- 9c: the order-only store fits where order+notes would not
local smallStore = P.MakeStore("A", "R", { "esteria:one", "esteria:two" }, {});
local okSmall = P.Save(smallStore, tinySlots);
ECS_CHECK(okSmall == true, "9c: a small store still fits");
local reloaded = P.Load("A", "R", tinySlots);
ECS_EQ(table.concat(reloaded.order, ","), "esteria:one,esteria:two",
    "9d: degraded-capacity store round-trips");

-- 9e-9h: WRITE-side degradation. Capacity is the failure that actually happens:
-- notes dominate the payload and there are only a handful of writable cvars, so
-- without this a roster whose notes outgrew the budget would fail to save at all
-- and a reorder would silently do nothing. The order is the primary feature, so
-- it must survive even when the notes have to be given up.
local noisy = P.MakeStore("A", "esteria", { "esteria:alpha", "esteria:beta" }, {});
noisy.notes["esteria:alpha"] = string.rep("n", 40);
noisy.notes["esteria:beta"] = string.rep("n", 40);
ECS_CHECK(P.Save(noisy, tinySlots) == false,
    "9e: the notes make the record too large for the slots");

local savedDegraded, _why, dropped = P.SaveDegraded(noisy, tinySlots);
ECS_CHECK(savedDegraded == true, "9f: SaveDegraded still saves the order");
ECS_CHECK(dropped == true, "9g: ... and reports that the notes were sacrificed");

local rescued = P.Load("A", "esteria", tinySlots);
ECS_EQ(table.concat(rescued.order, ","), "esteria:alpha,esteria:beta",
    "9h: the ORDER is what survived, in order");
ECS_CHECK(next(rescued.notes) == nil, "9i: the sacrificed notes were not persisted");

-- 9j: with nothing to give up, a failure is reported rather than retried forever.
local hopeless = P.MakeStore("A", "R", {}, {});
ECS_CHECK(P.SaveDegraded(hopeless, {}) == false, "9j: no slots still fails cleanly");

-- 9k: CAPACITY ENVELOPE, pinned. The custom order is the headline feature and it
-- has to be storable for a large roster, so the size relationship between a
-- roster and the available cvars is a correctness property, not a detail. A
-- realistic 25-character roster must fit the candidate budget with room to spare.
local roster25 = {};
for index = 1, 25 do roster25[index] = "esteria:character" .. tostring(index); end
local envelope = P.Shard(P.Serialise(P.MakeStore("A", "esteria", roster25, {})));
ECS_CHECK(#envelope <= #P.CANDIDATE_CVARS,
    "9k: a 25-character order fits the candidate cvar budget (" .. #envelope .. " shards)");

-- KNOWN LIMIT, asserted so it cannot be quietly forgotten: a FULL 100-character
-- roster with long names does NOT fit the candidate pool at MAX_CHUNK = 170. The
-- shard count is pinned here so that any future change which alters the envelope
-- (a higher measured cvar limit, more candidate cvars, a smaller encoding) has to
-- update this number deliberately instead of silently regressing.
local roster100 = {};
for index = 1, 100 do roster100[index] = "esteria:character" .. tostring(index); end
-- 9l/9m: the CONSERVATIVE DEFAULT is not enough for a full roster. Pinned so that
-- a change to the encoding or the default has to move this number deliberately
-- rather than silently regressing the envelope.
local fullEnvelope = #P.Shard(P.Serialise(P.MakeStore("A", "esteria", roster100, {})));
ECS_EQ(fullEnvelope, 8, "9l: a 100-character order needs 8 shards at the default chunk size");
ECS_CHECK(fullEnvelope > #P.CANDIDATE_CVARS,
    "9m: ... which exceeds the candidate cvars, hence the capacity probe below");

-- 9n-9s: THE PROBE IS WHAT CLOSES THAT GAP. Same roster, but now the per-cvar
-- limit is MEASURED from the client instead of assumed to be 170. This is the
-- end-to-end proof that measuring is what makes a full roster persistable.
local roomy = FakeBackend({ maxLen = 250 });
local roomySlots = P.ProbeCandidates(SLOTS, roomy);
P.ProbeCapacity(roomySlots, roomy);
ECS_EQ(#roomySlots, 3, "9n: three roomy cvars probe as writable");

-- Three 250-char cvars give ~3 x 226 = 678 payload chars, still short of the
-- ~1219 a 100-character order needs, so this must refuse rather than half-write.
local roomyStore = P.MakeStore("A", "esteria", roster100, {});
ECS_CHECK(P.Save(roomyStore, roomySlots, roomy) == false,
    "9o: a measured budget that is still too small refuses the save");

-- Give it enough cvars and the SAME payload now fits: each slot holds 226 chars
-- instead of the assumed 170, so the order survives where it previously could not.
local manyNames = {};
for index = 1, 8 do manyNames[index] = "cvar" .. tostring(index); end
local manyBackend = FakeBackend({ maxLen = 250 });
local manySlots = P.ProbeCandidates(manyNames, manyBackend);
P.ProbeCapacity(manySlots, manyBackend);
ECS_CHECK(P.Save(roomyStore, manySlots, manyBackend) == true,
    "9p: with measured room the 100-character order saves instead of being lost");
local reloadedFull = P.Load("A", "esteria", manySlots, manyBackend);
ECS_EQ(#reloadedFull.order, 100, "9q: and all 100 characters come back");
ECS_EQ(reloadedFull.order[1], "esteria:character1", "9r: the first entry is intact");
ECS_EQ(reloadedFull.order[100], "esteria:character100", "9s: the last entry is intact");

-- ---------------------------------------------------------------- 10. shrink hygiene
-- Saving a SHORTER store must clear shards the longer one left behind.
-- 8 notes is deliberately sized to need 2 shards but still fit the 3 slots, so
-- the shrink-hygiene check below has a stale shard to clear.
local longStore = P.MakeStore("A", "R", {}, {});
for i = 1, 8 do longStore.notes["esteria:char" .. i] = "note number " .. i; end
local roomy = FakeBackend();
P.SetBackend(roomy);
local roomySlots = P.ProbeCandidates(SLOTS, roomy);
P.Save(longStore, roomySlots);

local usedBefore = 0;
for i = 1, #roomySlots do
    if ( P.UnwrapValue(roomy.values[roomySlots[i].name]) ) then
        usedBefore = usedBefore + 1;
    end
end
ECS_CHECK(usedBefore > 1, "10a: the long store needed more than one shard");

P.Save(P.MakeStore("A", "R", { "esteria:one" }, {}), roomySlots);
local usedAfter = 0;
for i = 1, #roomySlots do
    if ( P.UnwrapValue(roomy.values[roomySlots[i].name]) ) then
        usedAfter = usedAfter + 1;
    end
end
ECS_EQ(usedAfter, 1, "10b: stale shards from the longer store were cleared");

local shrunk = P.Load("A", "R", roomySlots);
ECS_CHECK(shrunk ~= nil, "10c: the shrunk store still loads");
ECS_EQ(table.concat(shrunk.order, ","), "esteria:one", "10d: shrunk store has no residue");

-- ---------------------------------------------------------------- 11. no slots at all
P.SetBackend(live);
ECS_EQ(P.Save(store, {}), false, "11a: saving with no slots fails cleanly");
local noneLoaded, noneReason = P.Load("A", "R", {});
ECS_EQ(noneLoaded, nil, "11b: loading with no slots fails cleanly");
ECS_CHECK(type(noneReason) == "string", "11c: a reason string is returned");
