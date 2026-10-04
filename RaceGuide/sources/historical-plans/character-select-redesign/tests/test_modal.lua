--[==[ test_modal.lua -------------------------------------------------------------
    Proves the modal stack: safe replacement, bounded depth, accept/cancel
    semantics, Escape rules, and that a misbehaving callback cannot corrupt the
    stack (spec 20, 21, 30).
]==]

local M = ECS.Modal;

M.Reset();

-- ---------------------------------------------------------------- 1. open / close
local first = M.Open({ title = "One", text = "body", key = "one" });
ECS_CHECK(first ~= nil, "1a: modal opens");
ECS_EQ(M.Count(), 1, "1b: one on the stack");
ECS_CHECK(M.IsOpen(), "1c: IsOpen");
ECS_EQ(M.Top().title, "One", "1d: Top returns it");
ECS_EQ(M.Top().id, first.id, "1e: id matches");

local second = M.Open({ title = "Two", key = "two" });
ECS_EQ(M.Count(), 2, "1f: second modal stacks");
ECS_EQ(M.Top().title, "Two", "1g: Top is the newest");

-- 1h: closing by id removes the right one, not just the top
M.Close(first.id);
ECS_EQ(M.Count(), 1, "1h: closing by id removes it");
ECS_EQ(M.Top().key, "two", "1i: the other modal survives");
ECS_EQ(M.Close(9999), nil, "1j: closing an unknown id is a safe no-op");
ECS_EQ(M.Close(nil), nil, "1k: closing nil is safe");
ECS_EQ(M.ById(first.id), nil, "1l: ById no longer finds the closed modal");
ECS_CHECK(M.ByKey("two") ~= nil, "1m: ByKey finds the open one");

-- ---------------------------------------------------------------- 2. safe replacement
M.Reset();
local a = M.Open({ key = "delete", title = "Delete?", accept = "YES" });
ECS_EQ(M.Count(), 1, "2a: opened");
local b = M.Open({ key = "delete", title = "Delete REALLY?", text = "sure?" });
ECS_EQ(M.Count(), 1, "2b: the same key REPLACES rather than stacking");
ECS_EQ(b.id, a.id, "2c: the replacement reuses the same modal id");
ECS_EQ(M.Top().title, "Delete REALLY?", "2d: title updated");
ECS_EQ(M.Top().text, "sure?", "2e: text updated");
ECS_CHECK(M.Top().replaced == true, "2f: replacement flagged");

-- 2g: modals without a key never replace each other
M.Reset();
M.Open({ title = "X" });
M.Open({ title = "X" });
ECS_EQ(M.Count(), 2, "2g: keyless modals stack independently");

-- ---------------------------------------------------------------- 3. bounded depth
M.Reset();
for i = 1, M.MAX_DEPTH do
    ECS_CHECK(M.Open({ key = "k" .. i }) ~= nil, "3a: modal " .. i .. " accepted");
end
ECS_EQ(M.Count(), M.MAX_DEPTH, "3b: stack is at the limit");
ECS_EQ(M.Open({ key = "overflow" }), nil, "3c: opening beyond the limit is REFUSED");
ECS_EQ(M.Count(), M.MAX_DEPTH, "3d: the refused modal did not join the stack");

-- 3e: but replacing an existing key still works at the limit
local replaced = M.Open({ key = "k1", title = "replaced" });
ECS_CHECK(replaced ~= nil, "3e: replacement is allowed at the depth limit");
ECS_EQ(M.Count(), M.MAX_DEPTH, "3f: replacement did not grow the stack");

-- ---------------------------------------------------------------- 4. accept
M.Reset();
local accepted, accepts = nil, 0;
local m = M.Open({
    key = "confirm", title = "Confirm", accept = "YES", cancel = "NO",
    onAccept = function(modal) accepts = accepts + 1; accepted = modal; end,
});
ECS_CHECK(M.Accept() == true, "4a: Accept succeeds");
ECS_EQ(accepts, 1, "4b: onAccept fired once");
ECS_EQ(accepted.id, m.id, "4c: callback received the modal");
ECS_EQ(M.Count(), 0, "4d: modal left the stack");
ECS_CHECK(M.Accept() == false, "4e: Accept with an empty stack is a safe no-op");
ECS_EQ(accepts, 1, "4f: no extra callback");

-- 4g: the callback runs AFTER the pop, so it may open a follow-up modal
M.Reset();
local followUpOpened = false;
M.Open({
    key = "first",
    onAccept = function()
        followUpOpened = (M.Open({ key = "second", title = "Next" }) ~= nil);
    end,
});
M.Accept();
ECS_CHECK(followUpOpened, "4g: a follow-up modal can be opened from onAccept");
ECS_EQ(M.Top().key, "second", "4h: the follow-up is on the stack, not swallowed");

-- ---------------------------------------------------------------- 5. cancel
M.Reset();
local cancels = 0;
M.Open({ key = "c", cancel = "NO", onCancel = function() cancels = cancels + 1; end });
ECS_CHECK(M.Cancel() == true, "5a: Cancel succeeds");
ECS_EQ(cancels, 1, "5b: onCancel fired");
ECS_EQ(M.Count(), 0, "5c: popped");
ECS_CHECK(M.Cancel() == false, "5d: Cancel with an empty stack is a no-op");

-- 5e: a non-dismissable modal REFUSES to cancel - this is how the destructive
-- delete confirmation stays hard to escape
M.Reset();
local stickyCancels = 0;
M.Open({ key = "sticky", dismissable = false, onCancel = function() stickyCancels = stickyCancels + 1; end });
ECS_CHECK(M.Cancel() == false, "5e: a non-dismissable modal refuses Cancel");
ECS_EQ(M.Count(), 1, "5f: it is still on the stack");
ECS_EQ(stickyCancels, 0, "5g: its onCancel did not fire");

-- ---------------------------------------------------------------- 6. escape
M.Reset();
M.Open({ key = "esc", cancel = "CANCEL" });
ECS_CHECK(M.HandleEscape() == true, "6a: Escape closes a normal modal");
ECS_EQ(M.Count(), 0, "6b: popped");

-- 6c: escapeCloses = false swallows the key WITHOUT closing
M.Reset();
M.Open({ key = "noesc", escapeCloses = false, cancel = "CANCEL" });
ECS_CHECK(M.HandleEscape() == true, "6c: Escape is CONSUMED when escapeCloses is false");
ECS_EQ(M.Count(), 1, "6d: but the modal stays open");

-- 6e: a non-dismissable modal also swallows Escape
M.Reset();
M.Open({ key = "sticky2", dismissable = false });
ECS_CHECK(M.HandleEscape() == true, "6e: Escape consumed by a non-dismissable modal");
ECS_EQ(M.Count(), 1, "6f: still open");

-- 6g: Escape with no modal is not consumed, so the caller can act
M.Reset();
ECS_CHECK(M.HandleEscape() == false, "6g: Escape with no modal is not consumed");

-- 6h: Escape only affects the TOP modal
M.Reset();
M.Open({ key = "bottom" });
M.Open({ key = "top" });
M.HandleEscape();
ECS_EQ(M.Count(), 1, "6h: Escape popped exactly one");
ECS_EQ(M.Top().key, "bottom", "6i: the lower modal is now on top");

-- ---------------------------------------------------------------- 7. hostile callbacks
M.Reset();
M.Open({ key = "boom", onAccept = function() error("callback exploded"); end });
ECS_CHECK(M.Accept() == true, "7a: a throwing onAccept does not fail the Accept call");
ECS_EQ(M.Count(), 0, "7b: and the modal was still removed");

M.Reset();
M.Open({ key = "boom2", cancel = "NO", onCancel = function() error("nope"); end });
M.Cancel();
ECS_EQ(M.Count(), 0, "7c: a throwing onCancel still pops");

-- ---------------------------------------------------------------- 8. close all
M.Reset();
M.Open({ key = "a" });
M.Open({ key = "b" });
ECS_EQ(M.Count(), 2, "8a: two open");
ECS_EQ(M.CloseAll(), 2, "8b: CloseAll reports how many it closed");
ECS_EQ(M.Count(), 0, "8c: stack empty");
ECS_CHECK(not M.IsOpen(), "8d: IsOpen false");
ECS_EQ(M.Top(), nil, "8e: Top is nil on an empty stack");
ECS_EQ(M.CloseAll(), 0, "8f: CloseAll on an empty stack is safe");

-- ---------------------------------------------------------------- 9. conveniences
M.Reset();
local confirm = M.Confirm("del", "Delete", "Really?", function() end, function() end);
ECS_CHECK(confirm ~= nil, "9a: Confirm opens");
ECS_EQ(confirm.kind, "confirm", "9b: kind is confirm");
ECS_EQ(confirm.cancel, "CANCEL", "9c: Confirm has a cancel affordance");

M.Reset();
local alert = M.Alert("limit", "Limit", "You have too many characters");
ECS_CHECK(alert ~= nil, "9d: Alert opens");
ECS_EQ(alert.kind, "alert", "9e: kind is alert");
ECS_EQ(alert.cancel, nil, "9f: Alert has no cancel affordance");

-- ---------------------------------------------------------------- 10. malformed input
M.Reset();
ECS_EQ(M.Open(nil), nil, "10a: a nil spec is refused");
ECS_EQ(M.Open("nonsense"), nil, "10b: a non-table spec is refused");
ECS_EQ(M.Count(), 0, "10c: nothing joined the stack");

-- 10d: a spec with no fields still opens, with safe defaults
local bare = M.Open({});
ECS_CHECK(bare ~= nil, "10d: an empty spec opens with defaults");
ECS_EQ(bare.title, "", "10e: default title");
ECS_EQ(bare.accept, "OKAY", "10f: default accept label");
ECS_EQ(bare.dismissable, true, "10g: dismissable by default");
ECS_EQ(bare.escapeCloses, true, "10h: Escape closes by default");
