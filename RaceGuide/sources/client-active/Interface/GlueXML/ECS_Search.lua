--[[ ECS_Search.lua -------------------------------------------------------------
    Esteria Character Select - the search field's behaviour (spec 8, 30).

    Matching itself lives in ECS_Order (it owns the searchable blob and drives the
    filtered visual order), so this module deliberately does NOT reimplement it.
    What lives here is the UI-facing half:
      * the raw text as typed, versus the normalised needle actually used
      * keyboard semantics (Escape clears, Enter defers to the caller)
      * a result summary for the empty/partial states
      * the match range inside the NAME, so the row can highlight it

    Pure Lua, no frames, fully testable.
    Lua 5.1 only.
------------------------------------------------------------------------------ ]]

ECS = ECS or {};
ECS.Search = ECS.Search or {};

local S = ECS.Search;
local C = ECS.Const;
local O = ECS.Order;

-- Keep the needle short: it is matched against 100 characters' blobs and it is
-- also what gets echoed in the summary line.
S.MAX_LENGTH = 40;

S.query = S.query or "";   -- raw text, exactly as typed (for the edit box)

-- Reuses ECS_Order's normalisation so the needle and the blob are always
-- produced by the same rules; a mismatch here would make search silently miss.
function S.Normalise(text)
    if ( type(text) ~= "string" ) then
        return "";
    end
    local value = string.gsub(text, "[%z\1-\31\127]", "");
    if ( #value > S.MAX_LENGTH ) then
        value = string.sub(value, 1, S.MAX_LENGTH);
    end
    return O.Normalise(value);
end

-- ---------------------------------------------------------------- state
-- Returns the number of visible matches.
function S.SetQuery(raw)
    S.query = (type(raw) == "string") and raw or "";
    O.SetFilter(S.Normalise(S.query));
    return O.VisibleCount();
end

function S.GetQuery()
    return S.query;
end

function S.GetNeedle()
    return O.GetFilter();
end

function S.IsActive()
    return O.GetFilter() ~= "";
end

function S.Clear()
    local wasActive = S.IsActive();
    S.query = "";
    O.SetFilter("");
    return wasActive;
end

-- spec 30: Escape in the search box clears and unfocuses. Returns true when the
-- key was consumed, so the caller knows not to also close the screen.
function S.HandleEscape()
    if ( S.IsActive() ) then
        S.Clear();
        return true;
    end
    if ( S.query ~= "" ) then
        S.query = "";
        return true;
    end
    return false;
end

-- Enter in the box should NOT enter the world; it should commit the search and
-- hand focus back. Returning false means "not consumed" so the caller decides.
function S.HandleEnter()
    return false;
end

-- ---------------------------------------------------------------- summary
-- Feedback for the empty-result and filtered states (spec 31 / 8).
function S.Summary()
    local total = #(O.characters or {});
    local visible = O.VisibleCount();

    if ( not S.IsActive() ) then
        if ( total == 0 ) then
            return "";
        end
        return tostring(total) .. ((total == 1) and " character" or " characters");
    end

    if ( visible == 0 ) then
        return "No matches";
    end
    return tostring(visible) .. " of " .. tostring(total);
end

function S.IsEmptyResult()
    return S.IsActive() and O.VisibleCount() == 0 and #(O.characters or {}) > 0;
end

-- True when the account genuinely has no characters (spec 31's empty state),
-- as opposed to everything being filtered out.
function S.IsRosterEmpty()
    return #(O.characters or {}) == 0;
end

-- ---------------------------------------------------------------- highlight
-- Locate the needle inside a specific string (usually the character name) so the
-- row can colour the matched run. Returns startIndex, endIndex (1-based,
-- inclusive) or nil. Only the name is searched: a hit on zone or class is a real
-- match for filtering but should not highlight a name that does not contain it.
function S.MatchRange(text)
    local needle = O.GetFilter();
    if ( needle == "" or type(text) ~= "string" or text == "" ) then
        return nil;
    end
    local lowered = string.lower(text);
    local startIndex, endIndex = string.find(lowered, needle, 1, true);
    if ( not startIndex ) then
        return nil;
    end
    return startIndex, endIndex;
end

-- Split a string into the three runs a highlighting FontString needs.
-- Returns before, match, after. When there is no match, before is the whole text.
function S.Split(text)
    text = (type(text) == "string") and text or "";
    local startIndex, endIndex = S.MatchRange(text);
    if ( not startIndex ) then
        return text, "", "";
    end
    return string.sub(text, 1, startIndex - 1),
           string.sub(text, startIndex, endIndex),
           string.sub(text, endIndex + 1);
end

-- Test/reset hook.
function S.Reset()
    S.query = "";
    O.SetFilter("");
end
