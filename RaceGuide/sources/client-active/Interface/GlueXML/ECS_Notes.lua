--[[ ECS_Notes.lua --------------------------------------------------------------
    Esteria Character Select - per-character private notes (spec 12, 33).

    Notes are LOCAL client metadata: they never leave the machine and are never
    sent to the server. They live in the same account/realm-scoped cvar store as
    the custom order (ECS_Persistence), keyed by the same stableKey.

    The editor's draft/commit/cancel state machine lives here rather than in the
    row or the modal, so "Cancel really discards" is unit-testable without a
    single frame existing.

    Lua 5.1 only.
------------------------------------------------------------------------------ ]]

ECS = ECS or {};
ECS.Notes = ECS.Notes or {};

local N = ECS.Notes;

-- Long enough to be useful ("Herbalism / Alchemy, needs ICC lockout"), short
-- enough that 100 notes still fit the sharded cvar store.
N.MAX_LENGTH = 120;

N.notes = N.notes or {};    -- stableKey -> text
N.draft = nil;              -- { key, text, original } while editing

-- ---------------------------------------------------------------- text hygiene
-- Trims, collapses runs of whitespace, and strips control characters so a note
-- can never smuggle a delimiter or a newline into the persisted payload.
function N.Normalise(text)
    if ( type(text) ~= "string" ) then
        return "";
    end
    local value = string.gsub(text, "[%z\1-\31\127]", " ");
    value = string.gsub(value, "%s+", " ");
    value = string.gsub(value, "^%s+", "");
    value = string.gsub(value, "%s+$", "");
    if ( #value > N.MAX_LENGTH ) then
        value = string.sub(value, 1, N.MAX_LENGTH);
        value = string.gsub(value, "%s+$", "");
    end
    return value;
end

function N.IsEmpty(text)
    return N.Normalise(text) == "";
end

-- ---------------------------------------------------------------- storage
function N.Get(key)
    if ( type(key) ~= "string" ) then
        return nil;
    end
    return N.notes[key];
end

function N.Has(key)
    local text = N.Get(key);
    return text ~= nil and text ~= "";
end

function N.Count()
    local total = 0;
    for _, text in pairs(N.notes) do
        if ( text ~= nil and text ~= "" ) then
            total = total + 1;
        end
    end
    return total;
end

-- Set (or clear, when the text is empty). Returns true when something changed.
function N.Set(key, text)
    if ( type(key) ~= "string" or key == "" ) then
        return false;
    end
    local value = N.Normalise(text);
    local previous = N.notes[key];

    if ( value == "" ) then
        if ( previous == nil ) then
            return false;
        end
        N.notes[key] = nil;
        return true;
    end

    if ( previous == value ) then
        return false;
    end
    N.notes[key] = value;
    return true;
end

function N.Clear(key)
    if ( type(key) ~= "string" ) then
        return false;
    end
    if ( N.notes[key] == nil ) then
        return false;
    end
    N.notes[key] = nil;
    return true;
end

-- Replace the whole map, e.g. after loading the persisted store.
-- Anything malformed is dropped rather than raising (spec 33).
function N.Replace(map)
    local clean = {};
    if ( type(map) == "table" ) then
        for key, text in pairs(map) do
            if ( type(key) == "string" and key ~= "" and type(text) == "string" ) then
                local value = N.Normalise(text);
                if ( value ~= "" ) then
                    clean[key] = value;
                end
            end
        end
    end
    N.notes = clean;
    return clean;
end

-- Snapshot for the persistence layer.
function N.Export()
    local out = {};
    for key, text in pairs(N.notes) do
        out[key] = text;
    end
    return out;
end

-- spec 11/12: when a character is deleted, its note must go with it.
function N.Forget(key)
    return N.Clear(key);
end

-- ---------------------------------------------------------------- editor state
-- Begin editing a character's note. The draft remembers the original so Cancel
-- can restore it and so Commit can report "no change".
function N.BeginEdit(key)
    if ( type(key) ~= "string" or key == "" ) then
        return false;
    end
    N.draft = {
        key      = key,
        text     = N.notes[key] or "",
        original = N.notes[key],
    };
    return true;
end

function N.IsEditing()
    return N.draft ~= nil;
end

function N.GetDraftKey()
    if ( not N.draft ) then
        return nil;
    end
    return N.draft.key;
end

function N.GetDraft()
    if ( not N.draft ) then
        return nil;
    end
    return N.draft.text;
end

function N.SetDraft(text)
    if ( not N.draft ) then
        return false;
    end
    N.draft.text = N.Normalise(text);
    return true;
end

-- Escaping the editor must leave the stored note completely untouched.
function N.CancelEdit()
    if ( not N.draft ) then
        return false;
    end
    N.draft = nil;
    return true;
end

-- Commit the draft. Returns changed, key.
function N.CommitEdit()
    if ( not N.draft ) then
        return false, nil;
    end
    local key = N.draft.key;
    local text = N.draft.text;
    N.draft = nil;
    return N.Set(key, text), key;
end

-- Clear the note being edited, immediately, without leaving the editor.
function N.ClearDraft()
    if ( not N.draft ) then
        return false;
    end
    N.draft.text = "";
    N.Set(N.draft.key, "");
    return true;
end

-- Test/reset hook.
function N.Reset()
    N.notes = {};
    N.draft = nil;
end
