--[==[ test_anim.lua --------------------------------------------------------------
    Proves the tween controller is correct, cheap, and cannot be left spinning
    (spec 7, 32).

    Drives Update() by hand: in tests there is no CreateFrame, so the module stays
    headless. That is the whole point of separating the value math from the driver.
]==]

local A = ECS.Anim;
local C = ECS.Const;

-- Target stub: records the last value written for each key.
local function MakeTarget()
    return { values = {} };
end

local function SetterFor(key)
    return function(target, value)
        target.values[key] = value;
        target.calls = (target.calls or 0) + 1;
    end
end

A.Reset();

-- ---------------------------------------------------------------- 1. easings
ECS_CHECK(math.abs(A.Ease("linear", 0) - 0) < 1e-9, "1a: linear(0) is 0");
ECS_CHECK(math.abs(A.Ease("linear", 1) - 1) < 1e-9, "1b: linear(1) is 1");
for _, name in ipairs({ "linear", "quadIn", "quadOut", "quadInOut", "cubicOut", "backOut" }) do
    ECS_CHECK(math.abs(A.Ease(name, 0)) < 1e-9, "1c: " .. name .. " starts at 0");
    ECS_CHECK(math.abs(A.Ease(name, 1) - 1) < 1e-9, "1d: " .. name .. " ends at 1");
end
ECS_CHECK(A.Ease("nonsense", 0.5) ~= nil, "1e: an unknown easing falls back, not errors");
ECS_CHECK(A.Ease("linear", 0.5) == 0.5, "1f: linear midpoint");
-- backOut overshoots past 1 in the middle, which is what makes selection "pop"
ECS_CHECK(A.Ease("backOut", 0.8) > 1, "1g: backOut overshoots");

-- ---------------------------------------------------------------- 2. a single run
local target = MakeTarget();
local doneCount = 0;
A.Run(target, {
    key = "alpha", from = 0, to = 1, duration = 0.2, easing = "linear",
    setter = SetterFor("alpha"),
    onDone = function() doneCount = doneCount + 1; end,
});
ECS_EQ(A.ActiveCount(), 1, "2a: one tween active");
ECS_CHECK(A.IsRunning(target, "alpha"), "2b: IsRunning reports it");

A.Update(0.1);
ECS_CHECK(math.abs(target.values.alpha - 0.5) < 1e-6, "2c: half way at half the duration");
ECS_EQ(doneCount, 0, "2d: not finished early");

A.Update(0.1);
ECS_CHECK(math.abs(target.values.alpha - 1) < 1e-6, "2e: reaches the target value");
ECS_EQ(A.ActiveCount(), 0, "2f: tween removed when complete");
ECS_EQ(doneCount, 1, "2g: onDone fired exactly once");
ECS_CHECK(not A.IsRunning(target, "alpha"), "2h: no longer running");

-- 2i: extra updates after completion must not re-fire onDone
A.Update(0.5);
ECS_EQ(doneCount, 1, "2i: onDone does not repeat");

-- ---------------------------------------------------------------- 3. replace, do not stack
local t2 = MakeTarget();
local firstDone = 0;
local secondDone = 0;
A.Run(t2, { key = "alpha", from = 0, to = 1, duration = 0.5, setter = SetterFor("alpha"),
    onDone = function() firstDone = firstDone + 1; end });
A.Run(t2, { key = "alpha", from = 0, to = 0.25, duration = 0.1, setter = SetterFor("alpha"),
    onDone = function() secondDone = secondDone + 1; end });

ECS_EQ(A.ActiveCount(), 1, "3a: replacing does not stack a second tween on the same key");
ECS_EQ(firstDone, 0, "3b: the replaced tween's onDone does NOT fire");
A.Update(0.1);
ECS_EQ(secondDone, 1, "3c: the replacement completes");
ECS_CHECK(math.abs(t2.values.alpha - 0.25) < 1e-6, "3d: replacement target applied");

-- 3e: separate keys on the same target are independent.
-- easing is pinned to linear here so the arithmetic is checkable; A.Run's default
-- is quadOut, and Update clamps a single step to C.ANIM_MAX_DT.
local t3 = MakeTarget();
A.Run(t3, { key = "alpha", from = 0, to = 1, duration = 0.1, easing = "linear", setter = SetterFor("alpha") });
A.Run(t3, { key = "x", from = 0, to = 10, duration = 0.2, easing = "linear", setter = SetterFor("x") });
ECS_EQ(A.ActiveCount(), 2, "3e: different keys coexist");
A.Update(0.1);
ECS_CHECK(math.abs(t3.values.alpha - 1) < 1e-6, "3f: alpha finished");
ECS_CHECK(math.abs(t3.values.x - 5) < 1e-6, "3g: x is half way");
ECS_EQ(A.ActiveCount(), 1, "3h: only the unfinished tween remains");

-- ---------------------------------------------------------------- 4. cancel
A.Reset();   -- sections are independent: do not inherit earlier live tweens
local t4 = MakeTarget();
local cancelledDone = 0;
A.Run(t4, { key = "alpha", from = 0, to = 1, duration = 1, setter = SetterFor("alpha"),
    onDone = function() cancelledDone = cancelledDone + 1; end });
ECS_CHECK(A.Cancel(t4, "alpha") == true, "4a: cancel reports success");
ECS_EQ(A.ActiveCount(), 0, "4b: cancelled tween removed");
A.Update(1);
ECS_EQ(cancelledDone, 0, "4c: a cancelled tween must NOT fire onDone");
ECS_CHECK(A.Cancel(t4, "alpha") == false, "4d: cancelling again is a no-op");
ECS_CHECK(A.Cancel(t4, "never") == false, "4e: cancelling an unknown key is safe");
ECS_CHECK(A.Cancel(nil, "alpha") == false, "4f: nil target is safe");

-- 4g: CancelAll clears every key of one target but leaves others alone
local t5 = MakeTarget();
local t6 = MakeTarget();
A.Run(t5, { key = "a", from = 0, to = 1, duration = 1, setter = SetterFor("a") });
A.Run(t5, { key = "b", from = 0, to = 1, duration = 1, setter = SetterFor("b") });
A.Run(t6, { key = "a", from = 0, to = 1, duration = 1, setter = SetterFor("a") });
ECS_EQ(A.ActiveCount(), 3, "4g: three tweens active");
A.CancelAll(t5);
ECS_EQ(A.ActiveCount(), 1, "4h: CancelAll took only its own target's tweens");
ECS_CHECK(A.IsRunning(t6, "a"), "4i: the other target is untouched");

-- ---------------------------------------------------------------- 5. zero duration
A.Reset();
local t7 = MakeTarget();
local zeroDone = 0;
A.Run(t7, { key = "alpha", from = 0, to = 1, duration = 0, setter = SetterFor("alpha"),
    onDone = function() zeroDone = zeroDone + 1; end });
ECS_CHECK(math.abs(t7.values.alpha - 1) < 1e-6, "5a: zero duration settles immediately");
ECS_EQ(A.ActiveCount(), 0, "5b: zero-duration tween is not left active");
ECS_EQ(zeroDone, 1, "5c: onDone still fires for a zero-duration tween");

-- ---------------------------------------------------------------- 6. hostile input
A.Reset();
ECS_EQ(A.Run(nil, { setter = function() end }), nil, "6a: nil target rejected");
ECS_EQ(A.Run(MakeTarget(), nil), nil, "6b: nil spec rejected");
ECS_EQ(A.Run(MakeTarget(), { key = "x" }), nil, "6c: a spec with no setter is rejected");

local t8 = MakeTarget();
A.Run(t8, { key = "alpha", from = 0, to = 1, duration = 0.2, easing = "linear",
    setter = SetterFor("alpha") });
-- 6d: a long hitch is clamped so a tween cannot teleport
A.Update(1000);
ECS_CHECK(math.abs(t8.values.alpha - (C.ANIM_MAX_DT / 0.2)) < 1e-6,
    "6e: a huge delta is clamped to ANIM_MAX_DT");

-- 6f: garbage deltas do not raise
A.Update(nil);
A.Update("banana");
A.Update(0 / 0);
A.Update(-5);
ECS_CHECK(true, "6f: non-numeric and negative deltas are tolerated");

-- 6g: a throwing setter must not break the rest of the update loop
local bad = MakeTarget();
local good = MakeTarget();
A.Reset();
A.Run(bad, { key = "a", from = 0, to = 1, duration = 0.1, easing = "linear",
    setter = function() error("setter exploded"); end });
A.Run(good, { key = "a", from = 0, to = 1, duration = 0.1, easing = "linear",
    setter = SetterFor("a") });
A.Update(0.1);
ECS_CHECK(math.abs(good.values.a - 1) < 1e-6, "6g: a throwing setter does not stall others");
ECS_EQ(A.ActiveCount(), 0, "6h: the throwing tween still completes and is released");

-- ---------------------------------------------------------------- 7. pooling
A.Reset();
-- spec 32: completed tweens are returned to the pool, and a later batch REUSES
-- them rather than allocating. So the pool refills to the batch size and then
-- stays flat across batches.
local t9 = MakeTarget();
local batch = 20;
for i = 1, batch do
    A.Run(t9, { key = "k" .. i, from = 0, to = 1, duration = 0.05, setter = SetterFor("k" .. i) });
end
ECS_EQ(A.ActiveCount(), batch, "7a: 20 concurrent tweens");
A.Update(0.05);
ECS_EQ(A.ActiveCount(), 0, "7b: all completed");
local poolAfterFirst = #A.pool;
ECS_CHECK(poolAfterFirst >= batch,
    "7c: completed tween tables are returned to the pool (" .. poolAfterFirst .. ")");

for i = 1, batch do
    A.Run(t9, { key = "r" .. i, from = 0, to = 1, duration = 0.05, setter = SetterFor("r" .. i) });
end
ECS_EQ(A.ActiveCount(), batch, "7d: second batch starts full");
A.Update(0.05);
ECS_EQ(#A.pool, poolAfterFirst,
    "7e: a second batch REUSES pooled tables instead of growing the pool");

-- 7d: a reused tween must not carry stale state
local t10 = MakeTarget();
local reuseDone = 0;
A.Run(t10, { key = "alpha", from = 0, to = 1, duration = 0.1, setter = SetterFor("alpha"),
    onDone = function() reuseDone = reuseDone + 1; end });
A.Update(0.1);
ECS_EQ(reuseDone, 1, "7d: reused tween fires its own onDone exactly once");

-- ---------------------------------------------------------------- 8. reset
A.Reset();
local t11 = MakeTarget();
A.Run(t11, { key = "alpha", from = 0, to = 1, duration = 1, setter = SetterFor("alpha") });
ECS_EQ(A.ActiveCount(), 1, "8a: active before reset");
A.Reset();
ECS_EQ(A.ActiveCount(), 0, "8b: reset clears everything");
ECS_CHECK(not A.IsRunning(t11, "alpha"), "8c: nothing left running after reset");

-- ---------------------------------------------------------------- 9. convenience wrappers
-- These write through optional methods so they stay frame-agnostic.
local frameStub = { alpha = nil };
function frameStub.SetAlpha(_, value) frameStub.alpha = value; end
function frameStub.SetECSScale(_, value) frameStub.scale = value; end

A.Reset();
A.Fade(frameStub, 1, 0, 0.1);
A.Update(0.1);
ECS_CHECK(math.abs(frameStub.alpha - 1) < 1e-6, "9a: Fade writes through SetAlpha");

A.Scale(frameStub, 1.2, 1.0, 0.1);
A.Update(0.1);
ECS_CHECK(math.abs(frameStub.scale - 1.2) < 1e-6, "9b: Scale writes through SetECSScale");

-- 9c: a target that lacks the optional method is skipped, not fatal
local bare = {};
A.Reset();
A.Fade(bare, 1, 0, 0.1);
A.Update(0.1);
ECS_CHECK(true, "9c: a target without SetAlpha does not raise");
ECS_EQ(A.ActiveCount(), 0, "9d: the tween still completes and releases");
