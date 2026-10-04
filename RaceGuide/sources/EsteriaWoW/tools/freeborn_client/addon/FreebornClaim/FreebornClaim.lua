-- ============================================================
-- Freeborn Claim
--
-- The character-creation screen cannot tell the server which team was
-- chosen: the only create field Lua can influence is the name, and a
-- Freeborn name has to follow the same rules as an Alliance or Horde
-- one. So the create screen records the choice and this addon claims it
-- once the character exists, over the addon-message channel.
--
-- This client's glue state rejects any CVar name it does not already
-- know ("Couldn't find CVar named ..."), and it also refuses values of
-- the wrong shape -- a "fb:"-prefixed marker string was silently
-- refused. So a record is a plain number:
--
--     1000000000 + (hash % 1000000000)
--
-- always exactly ten digits, always below INT_MAX, never confusable with
-- a cvar's own resting value ("1", "76", "0"), and the only shape proven
-- to survive being written.
--
--   checkAddonVersion   the create screen parks the chosen name's record
--                       here; this addon consumes it and puts the cvar
--                       back, because it is not ours.
--   readTOS / readEULA  where this addon parks the records of claimed
--                       characters so the select screen can draw their
--                       emblem. Both only ever get a truthiness test, so
--                       a number keeps them "accepted", and neither is
--                       restored: they are the badge's memory.
--
-- A record only claims a character whose name matches, so a name that
-- failed validation, or a creation the player abandoned, cannot claim a
-- later character.
--
-- `/freeborn` reports what this state can actually see, because a CVar
-- that was never written is indistinguishable from one written empty.
-- ============================================================

local PREFIX = "FREEBORN";
local CLAIM = "claim";
local STATUS = "status";

-- Written by older revisions of the create screen; still read so a leftover record is visible.
local CVAR = "freebornPending";

-- Must match CharacterFreeborn_CarrierCVars / _BadgeCVars / _RecordBase / _RecordMod in the glue.
-- The carrier only has to survive within one session; the emblem memory has to survive a client
-- restart, so it must be a STRING cvar the client never parses -- every integer cvar tried was
-- normalised on load (readTOS/readEULA to "1", gameTip by clipping the record to a tip index).
local CARRIERS = { "readTOS" };
-- Dedicated restart-persistent badge slot. ECS reserves the output-driver and
-- other string CVars for its own store; sharing a slot caused recursive wrapping
-- and eventually corrupted Config.wtf.
local BADGES = { "Sound_VoiceChatInputDriverName" };
local BADGE_MARKER = "fb:";
local RECORD_BASE = 1000000000;
local RECORD_MOD = 1000000000;

local CARRIER_RESTORE = {
    readTOS = "1",
};

local WORLD_TEST = "freebornWorldTest";

local function Send(body)
    SendAddonMessage(PREFIX, body, "WHISPER", UnitName("player"));
end

-- The automatic path must be SILENT: it runs on every login and the player never asked for it.
-- `/freeborn` switches this on for the duration of its own output.
local verbose = false;
local function Print(msg)
    if ( verbose ) then
        DEFAULT_CHAT_FRAME:AddMessage("|cff00ccff[Freeborn]|r " .. msg);
    end
end

-- CVar access is never bare: the glue state raises on unknown names, and this addon must not
-- throw inside an event handler either.
local function SafeGet(name)
    local ok, value = pcall(GetCVar, name);
    if ( not ok ) then
        return nil;
    end
    return value;
end

-- Returns whether the write was accepted, so callers can tell "refused" from "changed".
local function SafeSet(name, value)
    local ok = pcall(SetCVar, name, value);
    return ok and true or false;
end

-- Must stay identical to CharacterFreeborn_NameHash in the glue block.
local function NameHash(name)
    local hash = 0;
    local lowered = strlower(name or "");
    for i = 1, strlen(lowered) do
        hash = (hash * 31 + strbyte(lowered, i)) % 2147483647;
    end
    return hash;
end

-- The ten-digit record for a character. Must match CharacterFreeborn_RecordFor.
local function RecordFor(name)
    return RECORD_BASE + NameHash(name) % RECORD_MOD;
end

local function CarrierReport()
    local parts = {};
    for _, carrier in ipairs(CARRIERS) do
        parts[#parts+1] = carrier .. "=" .. tostring(SafeGet(carrier));
    end
    return table.concat(parts, ", ");
end

local function BadgeReport()
    local parts = {};
    for _, slot in ipairs(BADGES) do
        parts[#parts+1] = slot .. "=" .. tostring(SafeGet(slot));
    end
    return table.concat(parts, ", ");
end

-- Any carrier that is not holding its resting value means the create screen left something.
local function CarrierArmed()
    for _, carrier in ipairs(CARRIERS) do
        local value = SafeGet(carrier);
        if ( value ~= nil and value ~= "" and value ~= CARRIER_RESTORE[carrier] ) then
            return true;
        end
    end
    return false;
end

-- Remember this character so the select screen can draw its emblem. The record format is
-- "fb:<record>,<record>,...|<whatever the cvar held before>": one string holds every Freeborn
-- character, and the client's own value is kept behind the bar. Returns the cvar used, or nil plus
-- why each was rejected.
local function StoreBadge(record)
    local wanted = tostring(record - RECORD_BASE);
    local mark = #BADGE_MARKER;
    local why = {};

    for _, cvar in ipairs(BADGES) do
        local stored = SafeGet(cvar);
        if ( type(stored) ~= "string" ) then
            stored = "";
        end

        local original = stored;
        local body = "";
        if ( strsub(stored, 1, mark) == BADGE_MARKER ) then
            body = strsub(stored, mark + 1);
            local bar = strfind(body, "|", 1, true);
            if ( bar ) then
                original = strsub(body, bar + 1);
                body = strsub(body, 1, bar - 1);
            else
                original = "";
            end
        end

        local list = {};
        local present = false;
        for digits in string.gmatch(body, "%d+") do
            if ( digits == wanted ) then
                present = true;
            end
            list[#list + 1] = digits;
        end

        if ( not present ) then
            list[#list + 1] = wanted;
            SafeSet(cvar, BADGE_MARKER .. table.concat(list, ",") .. "|" .. original);
        end

        local check = SafeGet(cvar);
        if ( type(check) == "string" and strsub(check, 1, mark) == BADGE_MARKER
            and strfind(check, wanted, 1, true) ) then
            return cvar;
        end

        why[#why + 1] = cvar .. " refused the write";
    end

    return nil, table.concat(why, ", ");
end

-- Can an emblem record be written here at all? This writes the value it just read back, so it
-- proves writability without ever disturbing a record list that is already there.
local function SlotWritable(slot)
    local before = SafeGet(slot);
    if ( type(before) ~= "string" ) then
        before = "";
    end
    local ok = SafeSet(slot, before);
    if ( not ok ) then
        return "refused";
    end
    return (SafeGet(slot) == before) and "writable" or "changed";
end

local function SlotReport()
    local parts = {};
    for _, slot in ipairs(BADGES) do
        parts[#parts+1] = slot .. "=" .. tostring(SafeGet(slot)) .. "(" .. SlotWritable(slot) .. ")";
    end
    return table.concat(parts, ", ");
end

local function WorldWriteTest()
    local wrote = pcall(SetCVar, WORLD_TEST, "1");
    local seen = SafeGet(WORLD_TEST);
    SafeSet(WORLD_TEST, "");
    if ( not wrote ) then
        return "rejected";
    end
    return (seen == "1") and "OK" or ("NO(" .. tostring(seen) .. ")");
end

local function ClaimIfChosen(isInitialLogin, isReloadingUi)
    local name = UnitName("player");
    local record = RecordFor(name);
    local pending = SafeGet(CVAR);
    local armed = (pending and pending ~= "") or CarrierArmed();

    local matchedBy = nil;
    if ( pending and pending ~= "" and strlower(name) == strlower(pending) ) then
        matchedBy = "its name";
    else
        for _, carrier in ipairs(CARRIERS) do
            if ( tonumber(SafeGet(carrier)) == record ) then
                matchedBy = carrier .. "'s record";
                break;
            end
        end
    end

    if ( not matchedBy ) then
        if ( armed ) then
            Print("world entry with a record waiting (isInitialLogin=" .. tostring(isInitialLogin) ..
                ", isReloadingUi=" .. tostring(isReloadingUi) .. ", this character's record is " ..
                tostring(record) .. "); not claiming. Run /freeborn to see what is left.");
        end
        return;
    end

    -- Cleared before sending, so a reload or a second login cannot claim twice, and the borrowed
    -- carrier is handed back, because it is not ours.
    SafeSet(CVAR, "");
    for _, carrier in ipairs(CARRIERS) do
        SafeSet(carrier, CARRIER_RESTORE[carrier]);
    end

    local slot, why = StoreBadge(record);
    Send(CLAIM);
    Print("the create screen chose Freeborn for '" .. tostring(name) .. "' (matched by " ..
        matchedBy .. "); asked the server for it." ..
        (slot and (" Emblem remembered in " .. slot .. ".") or
            (" No emblem stored: " .. tostring(why) .. ".")));
end

-- `/freeborn claim` asks for this character explicitly, and remembers its emblem. That is the way
-- to badge a character that was claimed before this addon kept records, and it re-asks for one that
-- is already Freeborn (the server answers "already Freeborn" and changes nothing).
local function ForceClaim()
    local name = UnitName("player");
    local slot, why = StoreBadge(RecordFor(name));
    Send(CLAIM);
    Print("asked the server to make '" .. tostring(name) .. "' Freeborn" ..
        (slot and (", and remembered its emblem in " .. slot .. ".") or
            (", but stored no emblem: " .. tostring(why) .. ".")));
end

SLASH_FREEBORN1 = "/freeborn";
SlashCmdList["FREEBORN"] = function(msg)
    verbose = true;

    if ( msg and strlower(msg) == "claim" ) then
        ForceClaim();
        return;
    end

    Print("pending='" .. tostring(SafeGet(CVAR)) ..
        "' record=" .. tostring(RecordFor(UnitName("player"))) ..
        " worldWrite=" .. WorldWriteTest());
    Print("carriers: " .. CarrierReport() .. "  badges: " .. BadgeReport() ..
        "   (/freeborn claim makes this character Freeborn)");
    Print("slots: " .. SlotReport());
    Send(STATUS);
end;

-- The server answers on the ADDON channel, so its reply never reaches the chat frame. The body is
-- "team\t<teamId>", and TEAM_FREEBORN is 3.
local TEAM_FREEBORN_BODY = "team\t3";
local function ReadServerReply(prefix, body)
    if ( prefix ~= PREFIX or body ~= TEAM_FREEBORN_BODY ) then
        return;
    end

    local cvar, why = StoreBadge(RecordFor(UnitName("player")));
    if ( not cvar ) then
        Print("this character is Freeborn, but the emblem could not be recorded: " .. tostring(why) .. ".")
    end
end

local frame = CreateFrame("Frame");
frame:RegisterEvent("PLAYER_ENTERING_WORLD");
frame:RegisterEvent("CHAT_MSG_ADDON");

local askedThisSession = false;

frame:SetScript("OnEvent", function(self, event, arg1, arg2)
    if ( event == "CHAT_MSG_ADDON" ) then
        pcall(ReadServerReply, arg1, arg2);
        return;
    end

    -- Deliberately not gated on isInitialLogin: the record is cleared before the claim is sent, so
    -- a second world entry cannot claim twice, and a gate that never opens is how the first
    -- attempt silently did nothing.
    local ok, err = pcall(ClaimIfChosen, arg1, arg2);
    if ( not ok ) then
        Print("error while checking the create screen's choice: " .. tostring(err));
    end

    -- Ask the server what team this character is, once per login: the reply drives the emblem.
    if ( not askedThisSession ) then
        askedThisSession = true;
        Send(STATUS);
    end
end);
