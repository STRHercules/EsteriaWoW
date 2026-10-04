--[[ ECS_Modal.lua --------------------------------------------------------------
    Esteria Character Select - reusable modal / notification framework (spec 21).

    Used for the delete confirmation, account-limit warnings, invalid character
    state, server messages and the notes editor.

    Glue already ships a GlueDialog system, but it is stock-styled and single-shot;
    this gives a stack with safe replacement, so a warning arriving while a
    confirmation is open cannot silently replace it or pile up unboundedly.

    The state machine is pure: it never touches a frame, so every rule here is
    unit-testable. The frame layer renders whatever Top() returns and animates with
    ECS_Anim.

    Lua 5.1 only.
------------------------------------------------------------------------------ ]]

ECS = ECS or {};
ECS.Modal = ECS.Modal or {};

local M = ECS.Modal;

-- Never stack deeper than this. A runaway event loop opening modals must not
-- build an unbounded stack.
M.MAX_DEPTH = 3;

M.stack = M.stack or {};
M.nextId = M.nextId or 0;

-- ---------------------------------------------------------------- helpers
local function Detach(id)
    for index = #M.stack, 1, -1 do
        if ( M.stack[index].id == id ) then
            return table.remove(M.stack, index);
        end
    end
    return nil;
end

local function FindByKey(key)
    if ( key == nil ) then
        return nil;
    end
    for index = 1, #M.stack do
        if ( M.stack[index].key == key ) then
            return M.stack[index];
        end
    end
    return nil;
end

-- Fire a callback without letting it break the stack.
local function Invoke(fn, modal)
    if ( type(fn) == "function" ) then
        pcall(fn, modal);
    end
end

-- ---------------------------------------------------------------- open / close
-- spec: { key, title, text, accept, cancel, onAccept, onCancel,
--         escapeCloses, kind, dismissable }
--
-- A spec carrying a `key` that is already open REPLACES that modal in place
-- instead of stacking a duplicate -- this is the "safe replacement" rule.
--
-- Returns the modal record, or nil when the request was refused.
function M.Open(spec)
    if ( type(spec) ~= "table" ) then
        return nil;
    end

    if ( spec.key ~= nil ) then
        local existing = FindByKey(spec.key);
        if ( existing ) then
            existing.title  = spec.title or existing.title;
            existing.text   = spec.text or existing.text;
            existing.accept = spec.accept or existing.accept;
            existing.cancel = spec.cancel or existing.cancel;
            existing.onAccept = spec.onAccept or existing.onAccept;
            existing.onCancel = spec.onCancel or existing.onCancel;
            existing.kind   = spec.kind or existing.kind;
            existing.replaced = true;
            return existing;
        end
    end

    if ( #M.stack >= M.MAX_DEPTH ) then
        return nil;   -- refuse rather than grow without bound
    end

    M.nextId = M.nextId + 1;
    local modal = {
        id            = M.nextId,
        key           = spec.key,
        title         = spec.title or "",
        text          = spec.text or "",
        accept        = spec.accept or "OKAY",
        cancel        = spec.cancel,          -- nil = information-only modal
        onAccept      = spec.onAccept,
        onCancel      = spec.onCancel,
        escapeCloses  = (spec.escapeCloses ~= false),
        dismissable   = (spec.dismissable ~= false),
        kind          = spec.kind or "info",
        replaced      = false,
    };
    M.stack[#M.stack + 1] = modal;
    return modal;
end

function M.Count()
    return #M.stack;
end

function M.IsOpen()
    return #M.stack > 0;
end

function M.Top()
    return M.stack[#M.stack];
end

function M.ById(id)
    for index = 1, #M.stack do
        if ( M.stack[index].id == id ) then
            return M.stack[index];
        end
    end
    return nil;
end

function M.ByKey(key)
    return FindByKey(key);
end

-- Close without firing a callback. Returns the removed modal or nil.
function M.Close(id)
    if ( id == nil ) then
        return nil;
    end
    return Detach(id);
end

-- spec 21: Accept on the top modal. Fires onAccept after it is off the stack, so
-- the callback is free to open a follow-up modal.
function M.Accept()
    local modal = M.Top();
    if ( not modal ) then
        return false;
    end
    local callback = modal.onAccept;
    Detach(modal.id);
    Invoke(callback, modal);
    return true;
end

-- spec 20/21: Cancel on the top modal. Refused when the modal is not dismissable,
-- which is how the delete confirmation stays deliberately hard to escape.
function M.Cancel()
    local modal = M.Top();
    if ( not modal ) then
        return false;
    end
    if ( modal.dismissable == false ) then
        return false;
    end
    local callback = modal.onCancel;
    Detach(modal.id);
    Invoke(callback, modal);
    return true;
end

-- spec 30: Escape closes the top modal when allowed. Returns true when consumed,
-- so the caller does not also act on the key.
function M.HandleEscape()
    local modal = M.Top();
    if ( not modal ) then
        return false;
    end
    if ( not modal.escapeCloses ) then
        return true;   -- swallowed on purpose: the modal is deliberately sticky
    end
    if ( modal.dismissable == false ) then
        return true;
    end
    return M.Cancel();
end

-- Close everything without firing callbacks (screen teardown, reconnect).
function M.CloseAll()
    local count = #M.stack;
    for index = #M.stack, 1, -1 do
        M.stack[index] = nil;
    end
    M.stack = {};
    return count;
end

-- ---------------------------------------------------------------- conveniences
function M.Confirm(key, title, text, onAccept, onCancel)
    return M.Open({
        key = key, title = title, text = text,
        accept = "OKAY", cancel = "CANCEL",
        onAccept = onAccept, onCancel = onCancel,
        kind = "confirm",
    });
end

-- An alert is dismissable but has no Cancel affordance.
function M.Alert(key, title, text, onAccept)
    return M.Open({
        key = key, title = title, text = text,
        accept = "OKAY", cancel = nil,
        onAccept = onAccept,
        kind = "alert",
    });
end

-- ---------------------------------------------------------------- test hook
function M.Reset()
    M.stack = {};
    M.nextId = 0;
end
